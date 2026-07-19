import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_case_study.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_case_study", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.module = load_validator()
        self.content = ROOT / "case-study" / "content"

    def test_every_public_claim_has_a_repository_source(self):
        claims = json.loads((self.content / "claims.json").read_text(encoding="utf-8"))
        evidence = json.loads((self.content / "evidence-index.json").read_text(encoding="utf-8"))
        self.assertEqual(self.module.validate_evidence(ROOT, claims, evidence), [])

    def test_forbidden_text_scan_reports_sensitive_terms(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "public.html"
            path.write_text("盘锦分公司 项目编号 ABC-001", encoding="utf-8")
            findings = self.module.scan_forbidden_text([path])
        self.assertEqual(len(findings), 1)
        self.assertIn("盘锦", findings[0])


class HtmlStructureTests(unittest.TestCase):
    def setUp(self):
        self.module = load_validator()
        self.site = ROOT / "case-study"

    def test_screen_has_exact_narrative_sections(self):
        ids = self.module.section_ids(self.site / "index.html")
        self.assertEqual(
            ids,
            [
                "hero",
                "problem",
                "opportunity",
                "solution",
                "early-failure",
                "key-iterations",
                "evaluation",
                "results-limitations",
                "reflection",
            ],
        )

    def test_print_has_ten_pages(self):
        pages = self.module.page_ids(self.site / "print.html")
        self.assertEqual(pages, [f"page-{index}" for index in range(1, 11)])

    def test_screen_and_print_contain_canonical_metrics(self):
        claims = json.loads(
            (self.site / "content" / "claims.json").read_text(encoding="utf-8")
        )
        errors = self.module.validate_shared_claims(
            [self.site / "index.html", self.site / "print.html"], claims
        )
        self.assertEqual(errors, [])


class PublicAssetTests(unittest.TestCase):
    def setUp(self):
        self.module = load_validator()
        self.site = ROOT / "case-study"

    def test_local_links_and_assets_exist(self):
        self.assertEqual(
            self.module.validate_local_references(self.site / "index.html", self.site),
            [],
        )
        self.assertEqual(
            self.module.validate_local_references(self.site / "print.html", self.site),
            [],
        )

    def test_interactive_controls_have_accessible_state(self):
        text = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertIn('role="tablist"', text)
        self.assertIn('aria-selected="true"', text)
        self.assertIn("aria-controls=", text)
        self.assertIn("<noscript>", text)


if __name__ == "__main__":
    unittest.main()
