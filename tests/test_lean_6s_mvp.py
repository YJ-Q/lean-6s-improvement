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


if __name__ == "__main__":
    unittest.main()
