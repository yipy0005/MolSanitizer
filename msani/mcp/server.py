"""MCP stdio server for bounded MolSanitizer workflows.

Install the optional dependency with ``pixi install -e mcp`` and run this
module through the ``molsanitizer-mcp`` console script. MCP protocol traffic
uses stdout, so diagnostics must go to stderr.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from . import core


LOGGER = logging.getLogger("molsanitizer.mcp")


def create_server() -> Any:
    """Create a fresh MCP server and register only safe, bounded tools."""
    try:
        # MCP SDK 2.x renamed FastMCP to MCPServer. Keep the fallback so
        # older environments can still use the same repository adapter.
        try:
            from mcp.server.mcpserver import MCPServer
        except ImportError:
            from mcp.server.fastmcp import FastMCP as MCPServer
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "MCP support is optional. Install it with "
            "pixi install -e mcp"
        ) from exc

    server = MCPServer(
        "molsanitizer",
        instructions=(
            "Use these read-only, bounded tools for MolSanitizer chemistry and "
            "repository validation. Do not infer scientific validity from a "
            "single tool result; report the options and environment used. "
            "This server never submits SLURM jobs or executes arbitrary commands."
        ),
    )

    @server.tool()
    def project_info() -> dict[str, Any]:
        """Report MolSanitizer, Python, RDKit, optional-module, and request limits."""
        return core.project_info()

    @server.tool()
    def validate_smiles(smiles: list[str], ids: list[str] | None = None) -> dict[str, Any]:
        """Parse SMILES and return validity, canonical SMILES, and heavy-atom counts."""
        return core.validate_smiles(smiles, ids)

    @server.tool()
    def prepare_smiles(
        smiles: list[str],
        ids: list[str] | None = None,
        removesalts: bool = False,
        neutralize: bool = False,
        tautomers: bool = False,
        extended_tautomers: bool = False,
        protonation: bool = False,
        pH: int = 7,
        pH_range: int = 0,
        stereoisomers: bool = False,
        max_stereoisomers: int = 8,
        pains: bool = False,
        unwanted: list[str] | None = None,
        standardize: bool = False,
        metal: str = "strict",
    ) -> dict[str, Any]:
        """Prepare up to 100 in-memory SMILES using the public Msani API.

        This tool does not write outputs. For reproducible files, use the CLI
        or ask the agent to create a reviewed command instead.
        """
        return core.prepare_smiles(
            smiles,
            ids,
            removesalts=removesalts,
            neutralize=neutralize,
            tautomers=tautomers,
            extended_tautomers=extended_tautomers,
            protonation=protonation,
            pH=pH,
            pH_range=pH_range,
            stereoisomers=stereoisomers,
            max_stereoisomers=max_stereoisomers,
            pains=pains,
            unwanted=unwanted,
            standardize=standardize,
            metal=metal,
        )

    @server.tool()
    def inspect_input_file(
        path: str,
        extended: bool = False,
        synthon: bool = False,
    ) -> dict[str, Any]:
        """Inspect a repository-local SMILES file with MolSanitizer's reader."""
        return core.inspect_input_file(path, extended=extended, synthon=synthon)

    @server.tool()
    def run_tests(suite: str = "readers", timeout_seconds: int = 120) -> dict[str, Any]:
        """Run an allow-listed unittest suite without accepting arbitrary commands."""
        return core.run_tests(suite=suite, timeout_seconds=timeout_seconds)

    return server


def main() -> None:
    """Start the MCP stdio transport."""
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    try:
        server = create_server()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
