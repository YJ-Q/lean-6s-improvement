# Lean 6S Case Study Site and PDF Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished, privacy-safe static HTML case study, a 10-page PDF, and an offline package that present the Lean 6S AI Skill as an evidence-grounded AI product-management project.

**Architecture:** Use hand-authored semantic HTML with shared design tokens and small vanilla-JavaScript enhancements. Keep claims in a canonical JSON file and validate that both screen and print artifacts use the same values; export the dedicated print page with Playwright and package only an explicit public allowlist.

**Tech Stack:** HTML5, CSS custom properties/Grid/print CSS, vanilla JavaScript, Python 3.11+ standard library, Node.js 20+, `playwright-core` 1.61.1 using the installed Microsoft Edge executable, reportlab 4.4.9 for QR generation, pypdf 6.10.0 for page-count verification, Markdown, GitHub Pages, Git.

## Global Constraints

- Public content is Chinese-first with English section labels.
- Visual style is Claude-inspired editorial minimalism: warm ivory, charcoal, restrained terracotta, editorial grid, serif display and sans-serif body.
- Do not use Anthropic/Claude logos, copied official layouts, purple AI gradients, decorative emoji, or a grid of generic rounded cards.
- The screen site contains exactly nine narrative sections: Hero, Problem, Opportunity, Solution, Early Failure, Key Iterations, Evaluation, Results & Limitations, Reflection & Next Steps.
- The print artifact contains exactly 10 A4 pages and must stay within the approved 8–12 page range.
- First release uses reconstructed diagrams, redacted text excerpts, and project-output screenshots; it does not publish raw site photos or original DOCX reports.
- Core content must be present in HTML and readable when JavaScript is disabled.
- No backend, login, API key, package installation, or build command is required to view the final public artifacts.
- Treat 31/31 as existing-case regression consistency only.
- Label synthetic testing as “合成用户测试” and “不等同于真实用户研究”.
- Public output must not include `验收报告/`, `case-study/mastery/`, raw session transcripts, company names, people, locations, project numbers, or contact information.

---

## File Map

- Create `case-study/index.html`: complete screen experience and semantic source content.
- Create `case-study/print.html`: dedicated 10-page print composition.
- Create `case-study/styles/tokens.css`: color, typography, spacing, border, and motion tokens.
- Create `case-study/styles/screen.css`: responsive screen layout and component styles.
- Create `case-study/styles/print.css`: A4 pagination and print-only layout.
- Create `case-study/scripts/navigation.js`: active section and progress navigation.
- Create `case-study/scripts/interactions.js`: accessible case/iteration tabs and details controls.
- Create `case-study/scripts/charts.js`: progressive enhancement for data bars and labels.
- Create `case-study/content/claims.json`: canonical publishable metrics and disclaimers.
- Create `case-study/content/evidence-index.json`: claim-to-source traceability.
- Create `case-study/content/copy.md`: approved long-form copy and source notes.
- Create `case-study/content/review-log.md`: visual/content approval log.
- Create `case-study/assets/diagrams/*.html`: reusable HTML-native workflow and architecture diagrams.
- Create `case-study/assets/screenshots/*.png`: verified screenshots of real project output or site previews.
- Create `case-study/assets/asset-manifest.json`: origin, privacy status, and public-use decision for every asset.
- Create `case-study/assets/qr/site-url.svg`: QR code generated from the deployed public URL.
- Create `case-study/exports/lean-6s-case-study.pdf`: final PDF.
- Create `case-study/offline/`: public allowlist package.
- Create `scripts/validate_case_study.py`: content, privacy, link, and consistency validator.
- Create `scripts/export_case_study_pdf.mjs`: Playwright PDF export.
- Create `scripts/capture_case_study.mjs`: desktop/mobile screenshot capture.
- Create `scripts/generate_case_study_qr.py`: deterministic QR SVG generation after deployment.
- Create `scripts/package_case_study.py`: deterministic offline packaging.
- Create `tests/test_case_study_site.py`: automated validator tests.
- Create `package.json` and `pnpm-lock.yaml`: pinned development-only browser automation dependency.
- Create `.github/workflows/case-study-pages.yml`: deploy only `case-study/offline/` to GitHub Pages.

## Task 1: Establish Canonical Claims, Evidence, and Privacy Rules

**Files:**
- Create: `case-study/content/claims.json`
- Create: `case-study/content/evidence-index.json`
- Create: `case-study/assets/asset-manifest.json`
- Create: `scripts/validate_case_study.py`
- Create: `tests/test_case_study_site.py`

**Interfaces:**
- Consumes: current repository reports, cases, Git history, and `case-study/content/synthetic-test-summary.js`.
- Produces: `load_claims()`, `validate_evidence()`, `scan_forbidden_text()`, and canonical values used by screen/print artifacts.

- [ ] **Step 1: Write failing tests for claim traceability and privacy scanning**

Create `tests/test_case_study_site.py`:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify they fail**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_case_study_site.EvidenceTests -v
```

Expected: FAIL because the validator and canonical content files do not exist.

- [ ] **Step 3: Create canonical public claims**

Create `case-study/content/claims.json` with:

```json
{
  "project_title": "Lean 6S Improvement",
  "project_subtitle": "把精益改善专家方法封装成现场管理者可用的 AI Skill",
  "role": "产品问题、工作流、规则体系、评测与迭代主导；代码由 AI 辅助生成",
  "existing_case_regression": {
    "total": 31,
    "virtual_cases": 14,
    "real_record_cases": 17,
    "dimensions": ["主分类", "副分类", "习惯性异常", "闭环判定"],
    "claim": "31 条现有案例的四项回归检查均通过",
    "limitation": "只证明现有规则与现有案例标注一致，不代表未知现场问题准确率为 100%"
  },
  "expert_review": {
    "reviewers": 1,
    "profile": "具有精益改善现场项目咨询经验的导师",
    "feedback": "方向可用，但需要更契合现场情况",
    "design_response": "增加追问决策关卡，要求补充会改变风险、分类、措施或闭环判断的现场信息"
  },
  "synthetic_testing": {
    "sessions": 30,
    "personas": 5,
    "scenarios": 3,
    "label": "合成用户测试",
    "disclaimer": "不等同于真实用户研究"
  },
  "non_claims": [
    "未验证真实用户满意度",
    "未验证整改效率提升",
    "未验证事故率下降",
    "未验证业务投资回报"
  ]
}
```

- [ ] **Step 4: Create the exact evidence index**

Create `case-study/content/evidence-index.json`:

```json
{
  "project_title": ["README.md", "SKILL.md"],
  "role": ["docs/superpowers/specs/2026-07-19-lean-6s-case-study-design.md"],
  "existing_case_regression": ["README.md", "docs/case-validation.md", "examples/cases.md", "examples/cases2.md", "scripts/lean_6s_mvp.py"],
  "expert_review": ["真实使用场景skill优化复测报告.md", "docs/superpowers/specs/2026-07-19-lean-6s-case-study-design.md"],
  "synthetic_testing": ["case-study/testing/results.json", "case-study/testing/report.md", "case-study/content/synthetic-test-summary.js"],
  "skill_effect": ["gpt模型有无skill效果分析报告.md", "deepseek模型有无skill对比报告.md", "跨模型skill效果总结报告.md"],
  "iteration_history": ["SKILL.md", "README.md", ".git"]
}
```

The `.git` entry is evidence available through Git history; `validate_evidence` must treat it as a directory that exists rather than a public asset.

- [ ] **Step 5: Create the initial asset manifest**

Create `case-study/assets/asset-manifest.json`:

```json
{
  "policy": "Only files listed with public_use=true may enter the site, PDF, or offline package.",
  "assets": [
    {"id": "workflow-diagram", "path": "diagrams/workflow.html", "origin": "reconstructed from SKILL.md", "contains_real_site_data": false, "privacy_review": "passed", "public_use": true},
    {"id": "architecture-diagram", "path": "diagrams/architecture.html", "origin": "reconstructed from repository structure", "contains_real_site_data": false, "privacy_review": "passed", "public_use": true}
  ]
}
```

Do not add any raw file from `验收报告/` to this manifest.

- [ ] **Step 6: Implement the minimal evidence and privacy validator**

Create `scripts/validate_case_study.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = ROOT / "case-study"
FORBIDDEN_PATTERNS = [
    r"盘锦",
    r"工业服务公司",
    r"项目编号",
    r"验收报告[\\/]",
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    r"1[3-9]\d{9}",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_evidence(root: Path, claims: dict[str, Any], evidence: dict[str, list[str]]) -> list[str]:
    errors: list[str] = []
    required = ["project_title", "role", "existing_case_regression", "expert_review", "synthetic_testing"]
    for claim_id in required:
        if claim_id not in claims:
            errors.append(f"missing claim: {claim_id}")
        sources = evidence.get(claim_id, [])
        if not sources:
            errors.append(f"missing evidence mapping: {claim_id}")
        for source in sources:
            if not (root / source).exists():
                errors.append(f"missing source for {claim_id}: {source}")
    return errors


def scan_forbidden_text(paths: Iterable[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        matches = [pattern for pattern in FORBIDDEN_PATTERNS if re.search(pattern, text, flags=re.IGNORECASE)]
        if matches:
            findings.append(f"{path}: forbidden patterns {matches}")
    return findings
```

- [ ] **Step 7: Run the tests and verify they pass**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_case_study_site.EvidenceTests -v
```

Expected: 2 tests PASS, provided the synthetic testing plan has already produced its three evidence files. If that workstream is not complete, `validate_evidence` must fail on those exact missing sources; do not weaken the requirement.

- [ ] **Step 8: Commit the evidence contract**

```powershell
git add case-study/content/claims.json case-study/content/evidence-index.json case-study/assets/asset-manifest.json scripts/validate_case_study.py tests/test_case_study_site.py
git commit -m "docs: establish case study evidence contract"
```

## Task 2: Build the Semantic Screen and Print Skeletons

**Files:**
- Create: `case-study/index.html`
- Create: `case-study/print.html`
- Create: `case-study/content/copy.md`
- Modify: `scripts/validate_case_study.py`
- Modify: `tests/test_case_study_site.py`

**Interfaces:**
- Consumes: `claims.json` and `evidence-index.json`.
- Produces: nine screen section IDs and ten print page IDs; static core copy for no-JavaScript reading.

- [ ] **Step 1: Write failing structure and shared-metric tests**

Append to `tests/test_case_study_site.py`:

```python
class HtmlStructureTests(unittest.TestCase):
    def setUp(self):
        self.module = load_validator()
        self.site = ROOT / "case-study"

    def test_screen_has_exact_narrative_sections(self):
        ids = self.module.section_ids(self.site / "index.html")
        self.assertEqual(ids, [
            "hero", "problem", "opportunity", "solution", "early-failure",
            "key-iterations", "evaluation", "results-limitations", "reflection"
        ])

    def test_print_has_ten_pages(self):
        pages = self.module.page_ids(self.site / "print.html")
        self.assertEqual(pages, [f"page-{index}" for index in range(1, 11)])

    def test_screen_and_print_contain_canonical_metrics(self):
        claims = json.loads((self.site / "content" / "claims.json").read_text(encoding="utf-8"))
        errors = self.module.validate_shared_claims(
            [self.site / "index.html", self.site / "print.html"], claims
        )
        self.assertEqual(errors, [])
```

- [ ] **Step 2: Run tests and verify they fail**

Expected: FAIL because HTML files and parsing functions do not exist.

- [ ] **Step 3: Implement section/page parsing and shared-claim checks**

Add to `scripts/validate_case_study.py`:

```python
class StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[str] = []
        self.pages: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "section" and values.get("id"):
            self.sections.append(values["id"])
        classes = set((values.get("class") or "").split())
        if tag == "section" and "page" in classes and values.get("id"):
            self.pages.append(values["id"])


def parse_structure(path: Path) -> StructureParser:
    parser = StructureParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def section_ids(path: Path) -> list[str]:
    return [item for item in parse_structure(path).sections if not item.startswith("page-")]


def page_ids(path: Path) -> list[str]:
    return parse_structure(path).pages


def validate_shared_claims(paths: list[Path], claims: dict[str, Any]) -> list[str]:
    expected = [
        str(claims["existing_case_regression"]["total"]),
        str(claims["existing_case_regression"]["virtual_cases"]),
        str(claims["existing_case_regression"]["real_record_cases"]),
        str(claims["synthetic_testing"]["sessions"]),
        claims["synthetic_testing"]["label"],
        claims["synthetic_testing"]["disclaimer"],
    ]
    errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for value in expected:
            if value not in text:
                errors.append(f"{path.name} missing canonical value: {value}")
    return errors
```

- [ ] **Step 4: Write the approved long-form copy source**

Create `case-study/content/copy.md` with the exact nine headings from the design spec. Under each heading, write final publishable copy using this argument order:

1. Hero: problem, solution, role, 31-case regression with limitation.
2. Problem: “能发现问题，但缺少系统改善方法”.
3. Opportunity: distribution and configuration advantage of a Skill versus a standalone app or a generic prompt.
4. Solution: input → question gate → classification/risk → task → acceptance → closure.
5. Early Failure: generic recommendations, weak questioning, unstable non-typical boundaries.
6. Key Iterations: safety boundary, primary/secondary category, habitual abnormality, question gate, ledger-first output, fake-closure review.
7. Evaluation: 14 virtual + 17 real-record cases, with/without Skill, cross-model work, and synthetic testing.
8. Results & Limitations: expert feedback, current regression, synthetic findings, hard-coding and missing real-user validation.
9. Reflection: real users, hybrid LLM + structured validation, input assistance, and honest AI-assisted authorship.

Every paragraph that states a project fact ends with a source note in the form `<!-- source: claim_id -->`. Do not paste raw report prose or company-identifying descriptions.

- [ ] **Step 5: Create semantic `index.html` with static core content**

Create an HTML5 document with:

- `<header>` containing project title, role, and a skip link;
- `<nav aria-label="Case study chapters">` linking to all nine IDs;
- `<main>` containing exactly nine `<section id="...">` elements in the tested order;
- visible strings `31`, `14`, `17`, `30`, `合成用户测试`, and `不等同于真实用户研究`;
- a `<noscript>` note saying all core content remains available and only tabs/progress enhancement is disabled;
- `<footer>` containing authorship disclosure and a link to `print.html` for the print preview; Task 5 replaces that target with the verified PDF path.

Use the final prose from `copy.md`; do not insert lorem ipsum, generic sample metrics, or empty graphic boxes.

- [ ] **Step 6: Create exact 10-page `print.html` composition**

Create `<section class="page" id="page-1">` through `page-10` with this mapping:

1. Cover and one-sentence value.
2. User problem and product opportunity.
3. Skill workflow and why Skill was chosen.
4. Early failure and mentor feedback.
5. Key iteration: question gate and现场适配.
6. Key iteration: ledger-first and closure evidence.
7. Evaluation design and 31-case regression limitation.
8. Synthetic-user testing results and limitations.
9. Role, AI-assisted coding disclosure, and technical architecture.
10. Reflection, next steps, website link, and QR-code area generated from the final URL.

Every page must contain final copy; page 8 values must come from the frozen synthetic-test result, not a guessed improvement percentage.

- [ ] **Step 7: Run structure tests and verify they pass**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_case_study_site.HtmlStructureTests -v
```

Expected: 3 tests PASS.

- [ ] **Step 8: Commit semantic content**

```powershell
git add case-study/index.html case-study/print.html case-study/content/copy.md scripts/validate_case_study.py tests/test_case_study_site.py
git commit -m "feat: add semantic case study content"
```

## Task 3: Create and Approve the HTML Visual Sample

**Files:**
- Create: `case-study/styles/tokens.css`
- Create: `case-study/styles/screen.css`
- Create: `case-study/assets/diagrams/workflow.html`
- Create: `case-study/assets/diagrams/architecture.html`
- Create: `scripts/capture_case_study.mjs`
- Create: `case-study/content/review-log.md`
- Modify: `case-study/index.html`

**Interfaces:**
- Consumes: semantic HTML from Task 2.
- Produces: approved hero, one Before/Insight/Decision/After iteration, and one evaluation module at desktop and mobile widths.

- [ ] **Step 1: Create design tokens with exact first-pass values**

Create `case-study/styles/tokens.css`:

```css
:root {
  color-scheme: light;
  --paper: #f4f0e8;
  --paper-strong: #ebe4d8;
  --ink: #1f1e1b;
  --muted: #6f6a61;
  --accent: #c45f3d;
  --accent-dark: #8e3f29;
  --line: #d6cec1;
  --success: #3f6b55;
  --warning: #9b5d2e;
  --display: "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif;
  --body: "Noto Sans SC", "Source Han Sans SC", "Microsoft YaHei", sans-serif;
  --mono: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  --step--1: clamp(0.82rem, 0.8rem + 0.1vw, 0.9rem);
  --step-0: clamp(1rem, 0.96rem + 0.2vw, 1.12rem);
  --step-1: clamp(1.25rem, 1.12rem + 0.6vw, 1.65rem);
  --step-2: clamp(1.75rem, 1.42rem + 1.4vw, 2.75rem);
  --step-3: clamp(2.6rem, 2rem + 2.6vw, 5.25rem);
  --space-1: 0.5rem;
  --space-2: 0.9rem;
  --space-3: 1.5rem;
  --space-4: 2.5rem;
  --space-5: 4rem;
  --space-6: 7rem;
  --radius: 0.75rem;
  --max-width: 76rem;
}
```

- [ ] **Step 2: Create the first-pass screen layout**

Create `case-study/styles/screen.css` with:

```css
* { box-sizing: border-box; }
html { scroll-behavior: smooth; background: var(--paper); }
body { margin: 0; color: var(--ink); background: var(--paper); font: 400 var(--step-0)/1.75 var(--body); }
a { color: inherit; text-underline-offset: 0.2em; }
img { display: block; max-width: 100%; }
.skip-link { position: fixed; left: 1rem; top: -5rem; z-index: 20; background: var(--ink); color: var(--paper); padding: 0.75rem 1rem; }
.skip-link:focus { top: 1rem; }
.site-shell { width: min(calc(100% - 2rem), var(--max-width)); margin-inline: auto; }
.chapter-nav { position: sticky; top: 0; z-index: 10; border-bottom: 1px solid var(--line); background: color-mix(in srgb, var(--paper) 92%, transparent); backdrop-filter: blur(14px); }
.chapter-nav ul { display: flex; gap: 1.25rem; margin: 0; padding: 0.85rem 0; list-style: none; overflow-x: auto; }
.chapter-nav a { color: var(--muted); font-size: var(--step--1); text-decoration: none; white-space: nowrap; }
.chapter-nav a[aria-current="true"] { color: var(--ink); }
section { padding-block: var(--space-6); border-bottom: 1px solid var(--line); }
.eyebrow { color: var(--accent-dark); font: 650 var(--step--1)/1.2 var(--body); letter-spacing: 0.12em; text-transform: uppercase; }
h1, h2, h3 { margin: 0; font-family: var(--display); font-weight: 500; line-height: 1.08; text-wrap: balance; }
h1 { max-width: 14ch; font-size: var(--step-3); }
h2 { max-width: 18ch; font-size: var(--step-2); }
.lede { max-width: 60ch; color: var(--muted); font-size: var(--step-1); }
.hero-grid, .split-grid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(18rem, 0.9fr); gap: var(--space-5); align-items: center; }
.evidence-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; border-block: 1px solid var(--line); background: var(--line); }
.evidence-strip article { min-height: 9rem; padding: var(--space-3); background: var(--paper); }
.evidence-strip strong { display: block; font: 500 var(--step-2)/1 var(--display); }
.iteration { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-block: 1px solid var(--line); }
.iteration article { padding: var(--space-3); border-right: 1px solid var(--line); }
.iteration article:last-child { border-right: 0; }
.workflow { display: grid; gap: var(--space-2); }
.workflow-step { display: grid; grid-template-columns: 3rem 1fr; gap: var(--space-2); padding-block: var(--space-2); border-bottom: 1px solid var(--line); }
.workflow-step b { color: var(--accent-dark); font-family: var(--mono); }
.callout { padding: var(--space-3); border: 1px solid var(--line); border-radius: var(--radius); background: var(--paper-strong); }
@media (max-width: 760px) {
  .site-shell { width: min(calc(100% - 1.25rem), var(--max-width)); }
  section { padding-block: var(--space-5); }
  .hero-grid, .split-grid { grid-template-columns: 1fr; gap: var(--space-3); }
  .evidence-strip, .iteration { grid-template-columns: 1fr; }
  .iteration article { border-right: 0; border-bottom: 1px solid var(--line); }
  .iteration article:last-child { border-bottom: 0; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```

- [ ] **Step 3: Build two HTML-native diagrams**

Create `workflow.html` as a fragment with six `.workflow-step` rows: 01 现场描述, 02 决策追问, 03 分类与风险, 04 可派工动作, 05 验收标准, 06 闭环证据.

Create `architecture.html` as a fragment showing four layers with exact labels: `SKILL.md / references / cases / Python MVP`. Use text, borders, and CSS Grid; do not draw decorative SVG illustrations.

Embed the workflow fragment into Hero/Solution and use the architecture fragment only in the solution or role section.

- [ ] **Step 4: Restrict the visual sample to three approved modules**

Apply full styling to:

- Hero with title, role disclosure, workflow, and evidence strip.
- The question-gate iteration using Before / Insight / Decision / After.
- Evaluation with 31-case regression and synthetic-test disclaimer.

Leave the remaining sections semantically complete and legible, but do not add special visual components until this sample is approved.

- [ ] **Step 5: Pin the browser-automation development dependency**

Create `package.json`:

```json
{
  "name": "lean-6s-case-study-tools",
  "private": true,
  "devDependencies": {
    "playwright-core": "1.61.1"
  }
}
```

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' install
```

Expected: creates `pnpm-lock.yaml` and a local `node_modules/playwright-core` without downloading a separate browser. Viewing the final site still requires no Node installation.

- [ ] **Step 6: Create deterministic screenshot capture**

Create `scripts/capture_case_study.mjs`:

```javascript
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright-core");

(async () => {
  fs.mkdirSync("case-study/assets/screenshots", { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  const target = pathToFileURL(path.resolve("case-study/index.html")).href;
  await page.goto(target, { waitUntil: "networkidle" });
  await page.screenshot({ path: "case-study/assets/screenshots/sample-desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: "networkidle" });
  await page.screenshot({ path: "case-study/assets/screenshots/sample-mobile.png", fullPage: true });
  await browser.close();
  if (errors.length) throw new Error(errors.join("\n"));
})();
```

Run with:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' scripts\capture_case_study.mjs
```

Expected: creates desktop and mobile PNGs with no script error.

- [ ] **Step 7: Stop for the visual approval gate**

Show both screenshots and the live local HTML. Ask specifically about color warmth, type contrast, information density, and the Before/Insight/Decision/After treatment. Do not style the remaining sections until approval.

- [ ] **Step 8: Record the decision**

Create `case-study/content/review-log.md` containing the review date, screenshots reviewed, user decision, and exact requested adjustments. Apply requested adjustments and recapture screenshots until approved.

- [ ] **Step 9: Commit the approved visual system**

```powershell
git add package.json pnpm-lock.yaml case-study/styles case-study/assets/diagrams case-study/assets/screenshots case-study/index.html case-study/content/review-log.md scripts/capture_case_study.mjs
git commit -m "feat: approve case study visual direction"
```

## Task 4: Complete Responsive Components and Accessible Interactions

**Files:**
- Modify: `case-study/index.html`
- Modify: `case-study/styles/screen.css`
- Create: `case-study/scripts/navigation.js`
- Create: `case-study/scripts/interactions.js`
- Create: `case-study/scripts/charts.js`
- Modify: `tests/test_case_study_site.py`

**Interfaces:**
- Consumes: approved visual tokens and sample components.
- Produces: progressive-enhancement navigation, accessible tabs/details, and data bars without hiding core HTML content.

- [ ] **Step 1: Write failing tests for accessibility hooks and local assets**

Append:

```python
class PublicAssetTests(unittest.TestCase):
    def setUp(self):
        self.module = load_validator()
        self.site = ROOT / "case-study"

    def test_local_links_and_assets_exist(self):
        self.assertEqual(self.module.validate_local_references(self.site / "index.html", self.site), [])
        self.assertEqual(self.module.validate_local_references(self.site / "print.html", self.site), [])

    def test_interactive_controls_have_accessible_state(self):
        text = (self.site / "index.html").read_text(encoding="utf-8")
        self.assertIn('role="tablist"', text)
        self.assertIn('aria-selected="true"', text)
        self.assertIn('aria-controls=', text)
        self.assertIn('<noscript>', text)
```

- [ ] **Step 2: Implement local reference validation**

Extend the HTML parser to collect `href` and `src`. Ignore `#fragment`, `mailto:`, `http://`, and `https://`; resolve every other reference relative to the HTML file and report missing files.

Add:

```python
class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for name in ("href", "src"):
            value = values.get(name)
            if value:
                self.references.append(value)


def validate_local_references(html_path: Path, public_root: Path) -> list[str]:
    parser = ReferenceParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for reference in parser.references:
        if reference.startswith(("#", "http://", "https://", "mailto:")):
            continue
        candidate = (html_path.parent / reference.split("#", 1)[0]).resolve()
        if public_root.resolve() not in candidate.parents and candidate != public_root.resolve():
            errors.append(f"reference escapes public root: {reference}")
        elif not candidate.exists():
            errors.append(f"missing local reference: {reference}")
    return errors
```

- [ ] **Step 3: Implement active-section navigation**

Create `case-study/scripts/navigation.js`:

```javascript
(() => {
  const links = [...document.querySelectorAll(".chapter-nav a[href^='#']")];
  const sections = links.map(link => document.querySelector(link.getAttribute("href"))).filter(Boolean);
  if (!("IntersectionObserver" in window)) return;
  const observer = new IntersectionObserver(entries => {
    const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    links.forEach(link => link.setAttribute("aria-current", String(link.getAttribute("href") === `#${visible.target.id}`)));
  }, { rootMargin: "-20% 0px -65%", threshold: [0.1, 0.4, 0.7] });
  sections.forEach(section => observer.observe(section));
})();
```

- [ ] **Step 4: Implement accessible tabs without removing static fallback content**

Create `case-study/scripts/interactions.js` that enhances elements marked `[data-tabs]`. On click or ArrowLeft/ArrowRight, update `aria-selected`, `tabindex`, and panel `hidden`. In raw HTML, all panels must be visible; add the `js` class to `<html>` at script start and apply hiding only under `.js [role="tabpanel"][hidden] { display: none; }`.

Use this complete handler:

```javascript
document.documentElement.classList.add("js");
document.querySelectorAll("[data-tabs]").forEach(group => {
  const tabs = [...group.querySelectorAll('[role="tab"]')];
  const activate = tab => {
    tabs.forEach(item => {
      const active = item === tab;
      item.setAttribute("aria-selected", String(active));
      item.tabIndex = active ? 0 : -1;
      const panel = document.getElementById(item.getAttribute("aria-controls"));
      if (panel) panel.hidden = !active;
    });
    tab.focus();
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => activate(tab));
    tab.addEventListener("keydown", event => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      event.preventDefault();
      const offset = event.key === 'ArrowRight' ? 1 : -1;
      activate(tabs[(index + offset + tabs.length) % tabs.length]);
    });
  });
});
```

- [ ] **Step 5: Implement data-bar enhancement**

Create `case-study/scripts/charts.js`:

```javascript
document.querySelectorAll("[data-bar-value]").forEach(bar => {
  const value = Number(bar.dataset.barValue);
  const max = Number(bar.dataset.barMax || 16);
  const percent = Math.max(0, Math.min(100, (value / max) * 100));
  bar.style.setProperty("--bar-percent", `${percent}%`);
  bar.setAttribute("aria-label", `${bar.dataset.barLabel}: ${value} / ${max}`);
});
```

Render actual baseline and Skill values from `synthetic-test-summary.js`; do not hard-code a performance improvement before results exist.

- [ ] **Step 6: Complete all nine responsive sections**

Extend the approved editorial system to remaining sections. Keep one dominant visual idea per section. Use tables only for exact mapping, the workflow for sequence, and a small architecture diagram for file roles. Avoid adding decorative icons to every heading.

- [ ] **Step 7: Run automated and visual checks**

Run unit tests, capture desktop/mobile screenshots, then inspect at 1440×1000, 1024×768, and 390×844. Expected: no horizontal overflow, overlapping sticky navigation, unreadable tab focus state, or hidden no-JavaScript content.

- [ ] **Step 8: Commit completed screen experience**

```powershell
git add case-study/index.html case-study/styles/screen.css case-study/scripts tests/test_case_study_site.py scripts/validate_case_study.py case-study/assets/screenshots
git commit -m "feat: complete responsive case study experience"
```

## Task 5: Build the 10-Page PDF and Verify Print Quality

**Files:**
- Create: `case-study/styles/print.css`
- Modify: `case-study/print.html`
- Create: `scripts/export_case_study_pdf.mjs`
- Create: `case-study/exports/lean-6s-case-study.pdf`
- Modify: `tests/test_case_study_site.py`

**Interfaces:**
- Consumes: final canonical claims and approved visual tokens.
- Produces: searchable 10-page A4 PDF with working links and no overflow.

- [ ] **Step 1: Create exact A4 print CSS**

Create `case-study/styles/print.css`:

```css
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #fff; color: var(--ink); }
body { font-family: var(--body); }
.page {
  width: 210mm;
  height: 297mm;
  padding: 18mm 18mm 16mm;
  overflow: hidden;
  break-after: page;
  page-break-after: always;
  background: var(--paper);
  position: relative;
}
.page:last-child { break-after: auto; page-break-after: auto; }
.page-number { position: absolute; right: 18mm; bottom: 10mm; color: var(--muted); font-size: 9pt; }
h1, h2, h3 { font-family: var(--display); font-weight: 500; line-height: 1.08; }
h1 { font-size: 34pt; }
h2 { font-size: 24pt; }
p, li { font-size: 10.5pt; line-height: 1.6; }
a { color: inherit; text-decoration-thickness: 0.5pt; }
.print-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10mm; }
.print-rule { border-top: 0.5pt solid var(--line); padding-top: 5mm; }
@media screen {
  body { display: grid; gap: 24px; padding: 24px; justify-content: center; background: #d8d4cc; }
  .page { box-shadow: 0 16px 50px rgb(0 0 0 / 0.15); }
}
```

- [ ] **Step 2: Add explicit overflow sentinels to every page**

Add `data-page-check="true"` to page sections. Ensure every page has a visible page number, a single primary conclusion, and no content positioned outside the page box.

- [ ] **Step 3: Create Playwright PDF export with overflow failure**

Create `scripts/export_case_study_pdf.mjs`:

```javascript
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright-core");

(async () => {
  const output = path.resolve("case-study/exports/lean-6s-case-study.pdf");
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
  });
  const page = await browser.newPage();
  await page.goto(pathToFileURL(path.resolve("case-study/print.html")).href, { waitUntil: "networkidle" });
  const overflow = await page.$$eval('[data-page-check="true"]', pages => pages.flatMap((item, index) => {
    const errors = [];
    if (item.scrollHeight > item.clientHeight + 1) errors.push(`page-${index + 1} vertical overflow`);
    if (item.scrollWidth > item.clientWidth + 1) errors.push(`page-${index + 1} horizontal overflow`);
    return errors;
  }));
  if (overflow.length) throw new Error(overflow.join("\n"));
  await page.pdf({ path: output, printBackground: true, preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await browser.close();
  console.log(output);
})();
```

- [ ] **Step 4: Export the PDF**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' scripts\export_case_study_pdf.mjs
```

Expected: creates the PDF and exits with no overflow error.

After export succeeds, update the public footer link in `index.html` from `print.html` to `exports/lean-6s-case-study.pdf`, then re-run local-reference validation.

- [ ] **Step 5: Add and run a PDF page-count test**

Append a test that imports `PdfReader` from `pypdf` and asserts exactly 10 pages. Run it with the bundled Python runtime that includes pypdf.

```python
def test_exported_pdf_has_ten_pages(self):
    from pypdf import PdfReader
    pdf = ROOT / "case-study" / "exports" / "lean-6s-case-study.pdf"
    self.assertEqual(len(PdfReader(str(pdf)).pages), 10)
```

- [ ] **Step 6: Render and visually inspect all pages**

Render the PDF to page PNGs using the available PDF workflow. Inspect page boundaries, title stranding, chart legibility, link labels, and QR code. Correct `print.html` or `print.css`, re-export, and repeat until all 10 pages pass.

- [ ] **Step 7: Commit the verified PDF**

```powershell
git add case-study/print.html case-study/styles/print.css case-study/exports/lean-6s-case-study.pdf scripts/export_case_study_pdf.mjs tests/test_case_study_site.py
git commit -m "feat: export verified Lean 6S case study PDF"
```

## Task 6: Package Public Files and Run the Release Audit

**Files:**
- Create: `scripts/package_case_study.py`
- Create: `scripts/generate_case_study_qr.py`
- Create: `.github/workflows/case-study-pages.yml`
- Create: `case-study/offline/`
- Modify: `scripts/validate_case_study.py`
- Modify: `tests/test_case_study_site.py`
- Modify: `case-study/assets/asset-manifest.json`

**Interfaces:**
- Consumes: final site, print page, styles, scripts, public assets, and PDF.
- Produces: an allowlist-only offline package and a zero-error validation report.

- [ ] **Step 1: Write failing package allowlist test**

Append:

```python
class PackageTests(unittest.TestCase):
    def test_offline_package_excludes_private_materials(self):
        offline = ROOT / "case-study" / "offline"
        relative = {path.relative_to(offline).as_posix() for path in offline.rglob("*") if path.is_file()}
        self.assertNotIn("testing/report.md", relative)
        self.assertFalse(any(path.startswith("mastery/") for path in relative))
        self.assertFalse(any("验收报告" in path for path in relative))
        self.assertIn("index.html", relative)
        self.assertIn("exports/lean-6s-case-study.pdf", relative)
        self.assertIn("content/synthetic-test-summary.js", relative)
```

- [ ] **Step 2: Create deterministic packaging script**

Create `scripts/package_case_study.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "case-study"
TARGET = SOURCE / "offline"
FILES = ["index.html", "content/synthetic-test-summary.js"]
DIRECTORIES = ["styles", "scripts", "exports"]


def main() -> None:
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True)
    for name in FILES:
        destination = TARGET / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / name, destination)
    for name in DIRECTORIES:
        source = SOURCE / name
        if source.exists():
            shutil.copytree(source, TARGET / name)
    manifest = json.loads((SOURCE / "assets" / "asset-manifest.json").read_text(encoding="utf-8"))
    for asset in manifest["assets"]:
        if not asset.get("public_use"):
            continue
        if asset.get("privacy_review") != "passed":
            raise RuntimeError(f"public asset has not passed privacy review: {asset['id']}")
        source = SOURCE / "assets" / asset["path"]
        destination = TARGET / "assets" / asset["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    print(f"Packaged public files to {TARGET}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Package and test offline files**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\package_case_study.py
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_case_study_site.PackageTests -v
```

Expected: package test PASS.

- [ ] **Step 4: Create the GitHub Pages workflow that uploads only the public package**

Create `.github/workflows/case-study-pages.yml` using the current action versions documented by GitHub:

```yaml
name: Deploy Lean 6S Case Study

on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - "case-study/offline/**"
      - ".github/workflows/case-study-pages.yml"

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: github-pages
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
      - name: Configure Pages
        uses: actions/configure-pages@v5
      - name: Upload public case study only
        uses: actions/upload-pages-artifact@v4
        with:
          path: case-study/offline
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

The workflow must never upload the repository root, `验收报告/`, `case-study/testing/`, or `case-study/mastery/`.

- [ ] **Step 5: Obtain explicit publication confirmation and deploy the candidate**

Before pushing the workflow or a commit that triggers it, show the final offline package and privacy report to the user and obtain confirmation that the sanitized case study may be publicly accessible. After confirmation, push the current branch, enable GitHub Pages with “GitHub Actions” as the source if the repository has not enabled it, and wait for the workflow to return its actual `page_url`.

Expected page URL for the current origin is `https://yj-q.github.io/lean-6s-improvement/`, but use the workflow output as the source of truth.

- [ ] **Step 6: Generate a QR code from the actual deployed URL**

Create `scripts/generate_case_study_qr.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.graphics import renderSVG
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing


def write_qr(url: str, output: Path, size: int = 180) -> None:
    widget = qr.QrCodeWidget(url)
    x1, y1, x2, y2 = widget.getBounds()
    width, height = x2 - x1, y2 - y1
    scale = min(size / width, size / height)
    drawing = Drawing(size, size, transform=[scale, 0, 0, scale, -x1 * scale, -y1 * scale])
    drawing.add(widget)
    output.parent.mkdir(parents=True, exist_ok=True)
    renderSVG.drawToFile(drawing, str(output))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the public case-study QR code")
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, default=Path("case-study/assets/qr/site-url.svg"))
    args = parser.parse_args()
    write_qr(args.url, args.output)
    print(f"Wrote {args.output} for {args.url}")


if __name__ == "__main__":
    main()
```

Run, substituting the exact workflow output URL:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\generate_case_study_qr.py --url 'https://yj-q.github.io/lean-6s-improvement/'
```

Add the actual URL as a visible clickable link and `assets/qr/site-url.svg` as an image on print page 10. Add the QR asset to `asset-manifest.json` with `origin: "generated from deployed GitHub Pages URL"`, `privacy_review: "passed"`, and `public_use: true`.

- [ ] **Step 7: Re-export and repackage the final linked artifacts**

Run PDF export, the 10-page pypdf test, and the offline packager again. Then push the updated PDF/QR/package and wait for the second Pages deployment. Verify that scanning the QR opens the same final page URL.

- [ ] **Step 8: Complete the final validator CLI**

Add a `main()` that loads claims/evidence, checks section/page structure, checks local references, scans all public text files, checks the asset manifest, and exits non-zero on any issue. Exclude `case-study/testing/` and `case-study/mastery/` from the public scan; scan `case-study/offline/` independently.

Required success output:

```text
Case study validation passed:
- evidence mappings: valid
- screen sections: 9
- print pages: 10
- local references: valid
- shared claims: consistent
- privacy findings: 0
- offline package: valid
```

- [ ] **Step 9: Run complete automated checks**

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_case_study_site -v
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_case_study.py
```

Expected: all tests PASS and validator reports zero privacy findings.

- [ ] **Step 10: Perform clean-browser and second-device checks**

Open `case-study/offline/index.html` with networking disabled. Verify core content, navigation anchors, images, PDF link, and mobile layout. Then open the deployed candidate URL in a clean profile and verify the same behavior.

- [ ] **Step 11: Finalize asset privacy decisions**

Update `asset-manifest.json` so every public file has `privacy_review: "passed"` and `public_use: true`. Remove any unreviewed file from the public directories rather than marking it passed without inspection.

- [ ] **Step 12: Commit the release package**

```powershell
git add .github/workflows/case-study-pages.yml scripts/package_case_study.py scripts/generate_case_study_qr.py scripts/validate_case_study.py tests/test_case_study_site.py case-study/offline case-study/assets/asset-manifest.json case-study/assets/qr case-study/print.html case-study/exports/lean-6s-case-study.pdf
git commit -m "chore: package privacy-safe case study release"
```
