import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "synthetic_test_harness.py"


def load_module():
    spec = importlib.util.spec_from_file_location("synthetic_test_harness", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.testing_root = ROOT / "case-study" / "testing"

    def test_catalogs_define_fixed_matrix(self):
        personas = json.loads((self.testing_root / "personas.json").read_text(encoding="utf-8"))
        scenarios = json.loads((self.testing_root / "scenarios.json").read_text(encoding="utf-8"))
        rubric = json.loads((self.testing_root / "rubric.json").read_text(encoding="utf-8"))

        self.assertEqual([item["id"] for item in personas], ["P01", "P02", "P03", "P04", "P05"])
        self.assertEqual([item["id"] for item in scenarios], ["S01", "S02", "S03"])
        self.assertEqual(len(rubric["dimensions"]), 8)
        self.assertEqual({item["max_score"] for item in rubric["dimensions"]}, {2})

    def test_catalog_validation_has_no_errors(self):
        errors = self.module.validate_catalogs(self.testing_root)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
