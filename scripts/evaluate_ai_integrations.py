#!/usr/bin/env python3
"""Evaluate repository-local Kiro skills and the MolSanitizer MCP adapter."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SKILLS = ROOT / ".kiro" / "skills"
AGENTS = ROOT / ".kiro" / "agents"
MCP_CONFIG = ROOT / ".kiro" / "settings" / "mcp.json"
MCP_CONFIG_EXAMPLE = ROOT / ".kiro" / "mcp.json.example"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def check_skills(failures: list[str]) -> int:
    checked = 0
    if not SKILLS.is_dir():
        fail(".kiro/skills directory is missing", failures)
        return checked
    for directory in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        checked += 1
        skill = directory / "SKILL.md"
        if not skill.is_file():
            fail(f"{directory.name}: SKILL.md is missing", failures)
            continue
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            fail(f"{directory.name}: frontmatter is missing", failures)
            continue
        end = text.find("\n---\n", 4)
        if end < 0:
            fail(f"{directory.name}: frontmatter is not closed", failures)
            continue
        frontmatter = text[4:end].splitlines()
        fields = {}
        for line in frontmatter:
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
        name = fields.get("name", "")
        description = fields.get("description", "")
        if name != directory.name or not NAME_RE.fullmatch(name) or len(name) > 64:
            fail(f"{directory.name}: invalid or mismatched name", failures)
        if not description or len(description) > 1024:
            fail(f"{directory.name}: description missing or too long", failures)
        for reference in re.findall(r"`(references/[^`]+)`", text):
            if not (directory / reference).is_file():
                fail(f"{directory.name}: missing reference {reference}", failures)
        if "TODO" in text:
            fail(f"{directory.name}: unresolved TODO", failures)
    return checked


def check_agents(failures: list[str]) -> int:
    checked = 0
    if not AGENTS.is_dir():
        fail(".kiro/agents directory is missing", failures)
        return checked
    for agent_file in sorted(AGENTS.glob("*.json")):
        checked += 1
        try:
            agent = json.loads(agent_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{agent_file.name}: invalid JSON: {exc}", failures)
            continue
        expected_name = agent_file.stem
        if agent.get("name") != expected_name or not NAME_RE.fullmatch(expected_name):
            fail(f"{agent_file.name}: name must match its lowercase kebab-case filename", failures)
        if not agent.get("description") or not agent.get("prompt"):
            fail(f"{agent_file.name}: description and prompt are required", failures)
        resources = agent.get("resources", [])
        if "skill://.kiro/skills/*/SKILL.md" not in resources:
            fail(f"{agent_file.name}: explicit workspace skill resource is missing", failures)
        if "@molsanitizer" not in agent.get("tools", []):
            fail(f"{agent_file.name}: MolSanitizer MCP tool selector is missing", failures)
        server = agent.get("mcpServers", {}).get("molsanitizer")
        if not isinstance(server, dict) or server.get("command") != "pixi":
            fail(f"{agent_file.name}: MCP server must launch through Pixi", failures)
        args = server.get("args", [])
        if not all(value in args for value in ("run", "-e", "mcp", "msani.mcp.server")):
            fail(f"{agent_file.name}: MCP args must select Pixi mcp environment", failures)
        if "hooks" in agent:
            fail(f"{agent_file.name}: IDE agents must not define CLI-only hooks", failures)
        prompt = agent.get("prompt", "")
        for required_term in ("Pixi", "SLURM", "explicit user authorization"):
            if required_term not in prompt:
                fail(f"{agent_file.name}: prompt is missing {required_term}", failures)
    return checked


def check_mcp_config(failures: list[str]) -> None:
    config_path = MCP_CONFIG if MCP_CONFIG.is_file() else MCP_CONFIG_EXAMPLE
    if not config_path.is_file():
        fail("MCP config and .kiro/mcp.json.example are missing", failures)
        return
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"MCP config is invalid JSON: {exc}", failures)
        return
    server = config.get("mcpServers", {}).get("molsanitizer")
    if not isinstance(server, dict):
        fail("molsanitizer MCP server entry is missing", failures)
        return
    for key in ("command", "args", "disabled", "autoApprove"):
        if key not in server:
            fail(f"MCP server is missing {key}", failures)
    if server.get("autoApprove") != []:
        fail("MCP autoApprove must remain empty by default", failures)
    if "-m" not in server.get("args", []) or "msani.mcp.server" not in server.get("args", []):
        fail("MCP config does not launch msani.mcp.server", failures)


def check_core(failures: list[str], require_sdk: bool) -> None:
    try:
        from msani.mcp import core

        result = core.validate_smiles(["CCO", "not-a-smiles"], ["ethanol", "bad"])
        if result["valid"] != 1 or result["invalid"] != 1:
            fail("validate_smiles smoke check returned unexpected counts", failures)
        info = core.project_info()
        if info.get("project") != "MolSanitizer":
            fail("project_info smoke check returned the wrong project", failures)
    except ModuleNotFoundError as exc:
        print(f"WARN: MCP core smoke check skipped; missing runtime dependency: {exc.name}")
    except Exception as exc:
        fail(f"MCP core smoke check failed: {type(exc).__name__}: {exc}", failures)

    sdk_available = importlib.util.find_spec("mcp") is not None
    if sdk_available:
        try:
            from msani.mcp.server import create_server

            create_server()
        except Exception as exc:
            fail(f"MCP server registration failed: {type(exc).__name__}: {exc}", failures)
    elif require_sdk:
        fail("MCP SDK is not installed; install the [mcp] extra", failures)
    else:
        print("WARN: MCP SDK not installed; server registration skipped")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-mcp-sdk",
        action="store_true",
        help="fail unless the optional MCP SDK is installed and the server registers",
    )
    args = parser.parse_args()
    failures: list[str] = []
    skill_count = check_skills(failures)
    agent_count = check_agents(failures)
    check_mcp_config(failures)
    check_core(failures, args.require_mcp_sdk)
    if failures:
        print(f"{len(failures)} integration check(s) failed")
        return 1
    print(f"PASS: {skill_count} Kiro skills, {agent_count} Kiro agents, MCP config, and core smoke checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
