import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("report", ROOT / "reporting/generate_report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)

class ContractTests(unittest.TestCase):
    def read(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.json"
            path.write_text(json.dumps(rows), encoding="utf-8")
            return report.read_results(path)

    def test_healthy_example(self):
        rows = report.read_results(ROOT / "examples/healthy.json")
        self.assertTrue(all(r["assertion_status"] == "PASS" for r in rows))

    def test_mutation_has_expected_failure(self):
        rows = report.read_results(ROOT / "examples/MUT-01.json")
        self.assertEqual([r["test_id"] for r in rows if r["assertion_status"] == "FAIL"], ["SEC-002"])

    def test_empty_results_rejected(self):
        with self.assertRaises(ValueError):
            self.read([])

    def test_false_pass_rejected(self):
        rows = json.loads((ROOT / "examples/MUT-01.json").read_text(encoding="utf-8"))
        rows[1]["assertion_status"] = "PASS"
        with self.assertRaises(ValueError):
            self.read(rows)

    def test_missing_field_rejected(self):
        rows = json.loads((ROOT / "examples/healthy.json").read_text(encoding="utf-8"))
        del rows[0]["model_version"]
        with self.assertRaises(ValueError):
            self.read(rows)

if __name__ == "__main__":
    unittest.main()
