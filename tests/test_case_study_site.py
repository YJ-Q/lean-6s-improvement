import importlib.util
import json
import re
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

    def test_forbidden_text_scan_ignores_svg_geometry_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "qr.svg"
            path.write_text('<rect x="17.161098105979995"/>', encoding="utf-8")
            findings = self.module.scan_forbidden_text([path])
        self.assertEqual(findings, [])


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


class PrintExportTests(unittest.TestCase):
    def setUp(self):
        self.site = ROOT / "case-study"

    def test_print_document_has_page_sentinels_and_numbers(self):
        text = (self.site / "print.html").read_text(encoding="utf-8")
        self.assertIn('href="styles/print.css"', text)
        self.assertEqual(text.count('data-page-check="true"'), 10)
        self.assertEqual(text.count('class="page-number"'), 10)

    def test_exported_pdf_has_ten_pages(self):
        from pypdf import PdfReader

        pdf = self.site / "exports" / "lean-6s-case-study.pdf"
        reader = PdfReader(str(pdf))
        self.assertEqual(len(reader.pages), 10)

    def test_exported_pdf_contains_searchable_core_claims(self):
        from pypdf import PdfReader

        pdf = self.site / "exports" / "lean-6s-case-study.pdf"
        text = "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf)).pages)
        # Chromium's CJK font subset maps inconsistently in pypdf on Windows, so
        # use stable Latin text to prove that the PDF has a searchable text layer.
        compact = re.sub(r"\s+", "", text)
        self.assertIn("Lean6SSkill", compact)
        self.assertIn("SYNTHETICUSERTESTING", compact)
        self.assertIsNotNone(re.search(r"13\.73\s*/\s*16", text))


class PackageTests(unittest.TestCase):
    def test_offline_package_excludes_private_materials(self):
        offline = ROOT / "case-study" / "offline"
        relative = {
            path.relative_to(offline).as_posix()
            for path in offline.rglob("*")
            if path.is_file()
        }
        self.assertNotIn("testing/report.md", relative)
        self.assertFalse(any(path.startswith("mastery/") for path in relative))
        self.assertFalse(any("验收报告" in path for path in relative))
        self.assertIn("index.html", relative)
        self.assertIn("exports/lean-6s-case-study.pdf", relative)
        self.assertIn("content/synthetic-test-summary.js", relative)

    def test_pages_workflow_uploads_only_offline_package(self):
        workflow = (ROOT / ".github" / "workflows" / "case-study-pages.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("path: case-study/offline", workflow)
        self.assertNotIn("path: .", workflow)

    def test_every_packaged_asset_has_passed_privacy_review(self):
        manifest = json.loads(
            (ROOT / "case-study" / "assets" / "asset-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        public = [asset for asset in manifest["assets"] if asset["public_use"]]
        self.assertTrue(public)
        self.assertTrue(all(asset["privacy_review"] == "passed" for asset in public))
        self.assertTrue(any(asset["id"] == "site-url-qr" for asset in public))


if __name__ == "__main__":
    unittest.main()
