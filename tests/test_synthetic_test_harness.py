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


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def valid_session(self, condition="skill", persona_id="P01", scenario_id="S01"):
        return {
            "session_id": f"{condition}-{persona_id}-{scenario_id}",
            "condition": condition,
            "persona_id": persona_id,
            "scenario_id": scenario_id,
            "transcript": [
                {"speaker": "user", "text": "现场有问题。"},
                {"speaker": "assistant", "text": "请确认具体位置。"},
            ],
            "ratings": [
                {"dimension_id": f"R{i:02d}", "score": 1, "evidence": "记录中的具体证据"}
                for i in range(1, 9)
            ],
            "review": {"strengths": ["追问位置"], "failures": ["措施不完整"], "notes": "形成性测试"},
        }

    def test_validate_session_accepts_complete_record(self):
        self.assertEqual(self.module.validate_session(self.valid_session()), [])

    def test_validate_session_rejects_missing_evidence(self):
        session = self.valid_session()
        session["ratings"][0]["evidence"] = ""
        self.assertIn("R01 requires evidence", self.module.validate_session(session))

    def test_aggregate_computes_condition_means(self):
        baseline = self.valid_session("baseline")
        skill = self.valid_session("skill")
        skill["ratings"][0]["score"] = 2
        result = self.module.aggregate_sessions([baseline, skill])
        self.assertEqual(result["session_count"], 2)
        self.assertEqual(result["conditions"]["baseline"]["mean_total"], 8.0)
        self.assertEqual(result["conditions"]["skill"]["mean_total"], 9.0)

    def test_repository_contains_complete_thirty_session_matrix(self):
        testing_root = ROOT / "case-study" / "testing"
        sessions, errors = self.module.validate_sessions(testing_root)
        self.assertEqual(errors, [])
        self.assertEqual(len(sessions), 30)


class PublicProjectionTests(unittest.TestCase):
    def test_public_projection_has_required_disclaimer(self):
        module = load_module()
        result = {
            "study_label": "合成用户测试",
            "disclaimer": "不等同于真实用户研究",
            "session_count": 30,
            "personas": 5,
            "scenarios": 3,
            "conditions": {"baseline": {"mean_total": 8.0}, "skill": {"mean_total": 12.0}},
        }
        projection = module.to_public_projection(result)
        self.assertEqual(projection["label"], "合成用户测试")
        self.assertEqual(projection["disclaimer"], "不等同于真实用户研究")
        self.assertNotIn("satisfaction", projection)


if __name__ == "__main__":
    unittest.main()
