import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from msani.mcp import core
except ModuleNotFoundError as exc:  # pragma: no cover - environment-dependent
    core = None
    MISSING_DEPENDENCY = exc.name
else:
    MISSING_DEPENDENCY = None


@unittest.skipIf(core is None, f"MolSanitizer runtime dependency is unavailable: {MISSING_DEPENDENCY}")
class TestMcpCore(unittest.TestCase):
    def test_validate_smiles_reports_validity_and_canonical_form(self):
        result = core.validate_smiles(["OCC", "not-a-smiles"], ["alcohol", "bad"])
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["invalid"], 1)
        self.assertEqual(result["records"][0]["canonical_smiles"], "CCO")

    def test_validate_smiles_rejects_oversized_requests(self):
        with self.assertRaises(core.MCPInputError):
            core.validate_smiles(["CCO"] * (core.MAX_SMILES + 1))

    def test_file_inspection_stays_inside_configured_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_file = root / "input.smi"
            input_file.write_text("CCO ethanol\n", encoding="utf-8")
            with patch.dict(os.environ, {"MSANI_MCP_ROOT": str(root)}):
                result = core.inspect_input_file("input.smi")
                self.assertEqual(result["status"], "ok")
                self.assertEqual(result["sample_rows"][0]["ids"], "ethanol")
                with self.assertRaises(core.MCPInputError):
                    core.inspect_input_file("../outside.smi")

    def test_test_runner_has_no_arbitrary_suite(self):
        with self.assertRaises(core.MCPInputError):
            core.run_tests("python -c malicious")


if __name__ == "__main__":
    unittest.main()
