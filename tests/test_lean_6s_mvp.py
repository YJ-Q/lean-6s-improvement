import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "lean_6s_mvp.py"


def load_mvp():
    spec = importlib.util.spec_from_file_location("lean_6s_mvp", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ObjectInferenceTests(unittest.TestCase):
    def test_infer_object_recognizes_cleaning_agent(self):
        module = load_mvp()

        result = module.infer_object("配电柜前放了两桶清洁剂")

        self.assertEqual(result, "清洁剂")


class ClassificationBoundaryTests(unittest.TestCase):
    def test_cleaning_agent_near_electrical_cabinet_is_not_a_cleaning_standard_gap(self):
        module = load_mvp()

        primary, secondary = module.classify("配电柜前放了两桶清洁剂")

        self.assertEqual(primary, "Safety / 安全")
        self.assertNotIn("Seiketsu / 清洁", secondary)

    def test_spray_booth_cleaning_method_gap_remains_standardize(self):
        module = load_mvp()

        primary, secondary = module.classify(
            "喷涂班组每天清洁喷房，但不同班组的方法不一样，也没有统一标准或SOP。"
        )

        self.assertEqual(primary, "Seiketsu / 清洁")
        self.assertEqual(secondary, [])


if __name__ == "__main__":
    unittest.main()
