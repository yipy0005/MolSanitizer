"""Pure Python handlers used by the MolSanitizer MCP server.

Handlers are deliberately bounded and do not execute arbitrary shell commands,
submit SLURM jobs, or write project files. The MCP layer is an adapter around
existing MolSanitizer APIs, not a second chemistry implementation.
"""

from __future__ import annotations

import importlib.util
import math
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


MAX_SMILES = 100
MAX_TEST_TIMEOUT = 900
MAX_TEST_OUTPUT = 12_000
MAX_INSPECT_BYTES = 20 * 1024 * 1024
_TEST_SUITES = {
    "readers": "test.test_input_readers",
    "config": "test.test_config",
    "msani": "test.test_msani",
    "validation": "test.test_validation_sets",
    "all": "test",
}


class MCPInputError(ValueError):
    """Raised when an MCP request violates a documented safety bound."""


def _require_list(value: Any, name: str, maximum: int = MAX_SMILES) -> list[Any]:
    if not isinstance(value, list):
        raise MCPInputError(f"{name} must be a JSON array")
    if not value:
        raise MCPInputError(f"{name} must not be empty")
    if len(value) > maximum:
        raise MCPInputError(f"{name} has {len(value)} entries; maximum is {maximum}")
    return value


def _project_root() -> Path:
    configured = os.environ.get("MSANI_MCP_ROOT")
    root = Path(configured).expanduser() if configured else Path.cwd()
    return root.resolve()


def _safe_file_path(path: str) -> tuple[Path, Path]:
    if not isinstance(path, str) or not path.strip():
        raise MCPInputError("path must be a non-empty string")
    root = _project_root()
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except FileNotFoundError as exc:
        raise MCPInputError(f"file does not exist under MCP root: {path}") from exc
    except ValueError as exc:
        raise MCPInputError("path must stay inside MSANI_MCP_ROOT") from exc
    if not resolved.is_file():
        raise MCPInputError(f"path is not a regular file: {path}")
    if resolved.stat().st_size > MAX_INSPECT_BYTES:
        raise MCPInputError(
            f"file is larger than the inspection limit ({MAX_INSPECT_BYTES} bytes)"
        )
    return root, resolved


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if hasattr(value, "item"):
        return _json_value(value.item())
    return str(value)


def _rows(frame: Any) -> list[dict[str, Any]]:
    columns = [column for column in frame.columns if column != "mol"]
    return [
        {str(column): _json_value(row[column]) for column in columns}
        for _, row in frame.iterrows()
    ]


def project_info() -> dict[str, Any]:
    """Return bounded package, runtime, and optional-capability information."""
    import msani

    optional = {
        name: importlib.util.find_spec(name) is not None
        for name in ("rdkit", "pandas", "numpy", "meeko", "openeye", "mcp")
    }
    rdkit_version = None
    try:
        from rdkit import rdBase

        rdkit_version = rdBase.rdkitVersion
    except Exception as exc:  # pragma: no cover - diagnostic fallback
        rdkit_version = f"unavailable: {type(exc).__name__}"

    return {
        "project": "MolSanitizer",
        "version": msani.__version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "rdkit": rdkit_version,
        "optional_modules": optional,
        "mcp_root": str(_project_root()),
        "limits": {
            "max_smiles_per_request": MAX_SMILES,
            "max_inspection_bytes": MAX_INSPECT_BYTES,
            "max_test_timeout_seconds": MAX_TEST_TIMEOUT,
        },
        "available_workflows": [
            "validate_smiles",
            "prepare_smiles",
            "inspect_input_file",
            "run_tests",
        ],
    }


def validate_smiles(smiles: list[str], ids: list[str] | None = None) -> dict[str, Any]:
    """Parse SMILES and return validity plus canonical SMILES without modifying files."""
    values = _require_list(smiles, "smiles")
    if any(not isinstance(value, str) for value in values):
        raise MCPInputError("every smiles entry must be a string")
    if ids is not None:
        ids = _require_list(ids, "ids")
        if len(ids) != len(values):
            raise MCPInputError("ids must have the same length as smiles")
        if any(not isinstance(value, str) for value in ids):
            raise MCPInputError("every ids entry must be a string")
    from rdkit import Chem

    records = []
    valid_count = 0
    for index, value in enumerate(values):
        identifier = ids[index] if ids is not None else str(index + 1)
        molecule = Chem.MolFromSmiles(value) if value.strip() else None
        if molecule is None:
            records.append(
                {"index": index, "id": identifier, "input_smiles": value, "valid": False, "error": "invalid SMILES"}
            )
            continue
        valid_count += 1
        records.append(
            {
                "index": index,
                "id": identifier,
                "input_smiles": value,
                "valid": True,
                "canonical_smiles": Chem.MolToSmiles(molecule),
                "heavy_atoms": molecule.GetNumHeavyAtoms(),
            }
        )
    return {"count": len(records), "valid": valid_count, "invalid": len(records) - valid_count, "records": records}


def prepare_smiles(
    smiles: list[str],
    ids: list[str] | None = None,
    *,
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
    """Run bounded in-memory preparation through :class:`msani.api.Msani`."""
    values = _require_list(smiles, "smiles")
    if any(not isinstance(value, str) for value in values):
        raise MCPInputError("every smiles entry must be a string")
    if ids is not None:
        ids = _require_list(ids, "ids")
        if len(ids) != len(values):
            raise MCPInputError("ids must have the same length as smiles")
        if any(not isinstance(value, str) for value in ids):
            raise MCPInputError("every ids entry must be a string")
    if metal not in {"strict", "soft", "off"}:
        raise MCPInputError("metal must be one of: strict, soft, off")
    if not isinstance(max_stereoisomers, int) or not 1 <= max_stereoisomers <= 128:
        raise MCPInputError("max_stereoisomers must be between 1 and 128")
    if not isinstance(pH, int) or not 0 <= pH <= 14:
        raise MCPInputError("pH must be between 0 and 14")
    if not isinstance(pH_range, int) or not 0 <= pH_range <= 14:
        raise MCPInputError("pH_range must be between 0 and 14")
    if unwanted is not None:
        unwanted = _require_list(unwanted, "unwanted", maximum=16)
        if any(value not in {"all", "regular", "special", "optional"} for value in unwanted):
            raise MCPInputError("unwanted entries must be all, regular, special, or optional")

    import pandas as pd
    from msani.api import Msani

    frame = pd.DataFrame({"smiles": values, "ids": ids or [str(index + 1) for index in range(len(values))]})
    options = {
        "removesalts": removesalts,
        "neutralize": neutralize,
        "tautomers": tautomers or extended_tautomers,
        "extended_tautomers": extended_tautomers,
        "protonation": protonation,
        "pH": pH,
        "pH_range": pH_range,
        "stereoisomers": stereoisomers,
        "max_stereoisomers": max_stereoisomers,
        "pains": pains,
        "unwanted": unwanted,
        "standardize": standardize,
        "metal": metal,
        "numcores": 1,
    }
    with Msani(**options) as processor:
        output = processor.run(frame)
    records = _rows(output)
    return {
        "input_count": len(values),
        "output_count": len(records),
        "options": {key: _json_value(value) for key, value in options.items()},
        "records": records,
    }


def inspect_input_file(path: str, extended: bool = False, synthon: bool = False) -> dict[str, Any]:
    """Inspect a bounded input file using MolSanitizer's real reader logic."""
    _, resolved = _safe_file_path(path)
    from msani.cli import read_input_file
    from msani.io.readers import detect_input_compression, detect_input_separator

    compression = detect_input_compression(resolved)
    separator = "\\t" if extended else detect_input_separator(resolved, compression)
    result: dict[str, Any] = {
        "path": str(resolved),
        "relative_path": str(resolved.relative_to(_project_root())),
        "bytes": resolved.stat().st_size,
        "compression": compression or "none",
        "separator": separator,
        "extended": extended,
        "synthon": synthon,
    }
    try:
        with read_input_file(resolved, extended, synthon) as chunks:
            first = next(chunks, None)
        result["sample_rows"] = [] if first is None else _rows(first.head(5))
        result["sample_count"] = 0 if first is None else len(first)
        result["status"] = "ok"
    except Exception as exc:
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def run_tests(suite: str = "readers", timeout_seconds: int = 120) -> dict[str, Any]:
    """Run one allow-listed unittest suite from the repository root."""
    if suite not in _TEST_SUITES:
        raise MCPInputError(f"suite must be one of: {', '.join(_TEST_SUITES)}")
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= MAX_TEST_TIMEOUT:
        raise MCPInputError(f"timeout_seconds must be between 1 and {MAX_TEST_TIMEOUT}")
    command = [sys.executable, "-m", "unittest", "discover", "-s", _TEST_SUITES[suite]] if suite == "all" else [sys.executable, "-m", "unittest", _TEST_SUITES[suite]]
    try:
        completed = subprocess.run(
            command,
            cwd=_project_root(),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        output = (completed.stdout + "\n" + completed.stderr).strip()
        return {
            "suite": suite,
            "command": command,
            "returncode": completed.returncode,
            "passed": completed.returncode == 0,
            "output": output[-MAX_TEST_OUTPUT:],
            "truncated": len(output) > MAX_TEST_OUTPUT,
        }
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or "") + "\n" + (exc.stderr or "")).strip()
        return {
            "suite": suite,
            "command": command,
            "returncode": None,
            "passed": False,
            "timed_out": True,
            "output": output[-MAX_TEST_OUTPUT:],
            "truncated": len(output) > MAX_TEST_OUTPUT,
        }
