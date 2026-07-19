# Lean 6S Case Study Delivery Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a public Lean 6S AI Skill case study as an online static site, an 8–12 page PDF, an offline HTML package, a synthetic-user evaluation, and a private project-mastery handbook.

**Architecture:** Split delivery into three independently reviewable workstreams: synthetic-user testing, the public case-study site/PDF, and the private mastery handbook. Execute them in that order so the site reports frozen evidence and the handbook explains the final, published claims and implementation accurately.

**Tech Stack:** Python 3.11+ standard library, semantic HTML5, CSS, vanilla JavaScript, Node.js 20+, Playwright from the bundled Codex runtime, Markdown, Git.

## Global Constraints

- Public narrative is Chinese-first with English project and section labels.
- Visual direction is Claude-inspired editorial minimalism; do not copy Anthropic pages or use Anthropic/Claude logos.
- Public artifacts must not contain original acceptance reports, identifiable company names, people, locations, project numbers, contact details, logos, badges, or document headers.
- Treat “31/31” only as consistency on the existing case set, never as real-world accuracy.
- Label expert feedback, synthetic-user testing, and case-library regression separately.
- The public site must remain readable without JavaScript and require no login, build step, or backend.
- The PDF must contain 8–12 pages and use the same frozen claims and evidence values as the site.
- Do not claim user satisfaction, productivity improvement, accident reduction, or business ROI without real evidence.
- Preserve unrelated working-tree changes and use focused commits after each independently testable task.

---

## Plan Set and Dependency Order

1. [`2026-07-19-lean-6s-synthetic-user-testing.md`](./2026-07-19-lean-6s-synthetic-user-testing.md)
   - Produces frozen persona/scenario definitions, 30 session records, scored results, limitations, and publishable chart data.
2. [`2026-07-19-lean-6s-case-study-site.md`](./2026-07-19-lean-6s-case-study-site.md)
   - Consumes the synthetic-test results and existing project evidence; produces the online/offline site and PDF.
3. [`2026-07-19-lean-6s-project-mastery.md`](./2026-07-19-lean-6s-project-mastery.md)
   - Consumes the frozen public narrative and current code; produces private learning and interview materials.

## Task 1: Complete Synthetic-User Testing

**Files:**
- Follow: `docs/superpowers/plans/2026-07-19-lean-6s-synthetic-user-testing.md`
- Produce: `case-study/testing/results.json`
- Produce: `case-study/testing/report.md`
- Produce: `case-study/content/synthetic-test-summary.js`

**Interfaces:**
- Consumes: `SKILL.md`, `references/*.md`, `examples/cases*.md`.
- Produces: frozen result metrics and qualitative findings that the public site may quote.

- [ ] **Step 1: Execute every checkbox in the synthetic-user testing plan**

Run the plan from Task 1 through its final validation task. Do not begin site copy that cites synthetic results before `results.json` and `report.md` are frozen.

- [ ] **Step 2: Verify the workstream acceptance gate**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_synthetic_test_harness.py' -v
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\synthetic_test_harness.py validate --root case-study\testing
```

Expected: all unit tests pass and validation returns `{"ok": true, "sessions": 30, "schema_errors": 0}`; complete R01–R08 rating evidence is guaranteed by the session schema validator.

- [ ] **Step 3: Review claims before committing the workstream gate**

Confirm that the report contains the exact labels “合成用户测试” and “不等同于真实用户研究”, includes failed sessions, and contains no “用户满意度” claim.

- [ ] **Step 4: Commit the completed workstream**

```powershell
git add case-study/testing case-study/content/synthetic-test-summary.js scripts/synthetic_test_harness.py tests/test_synthetic_test_harness.py
git commit -m "test: add synthetic Lean 6S user evaluation"
```

## Task 2: Complete the Public Site and PDF

**Files:**
- Follow: `docs/superpowers/plans/2026-07-19-lean-6s-case-study-site.md`
- Produce: `case-study/index.html`
- Produce: `case-study/print.html`
- Produce: `case-study/exports/lean-6s-case-study.pdf`

**Interfaces:**
- Consumes: `case-study/content/synthetic-test-summary.js` and the evidence index created by the site plan.
- Produces: public online/offline HTML and the 8–12 page PDF.

- [ ] **Step 1: Execute every checkbox in the site/PDF plan through the visual-sample gate**

Stop after the sample contains the hero, one Before/Insight/Decision/After iteration, and one evaluation block.

- [ ] **Step 2: Obtain visual-direction approval**

Open `case-study/index.html` and show desktop/mobile screenshots. Record the approval or requested changes in `case-study/content/review-log.md` before completing the remaining site tasks.

- [ ] **Step 3: Execute the remaining site/PDF tasks**

Complete responsive layout, interactions, print composition, PDF export, privacy scan, offline packaging, and accessibility checks.

- [ ] **Step 4: Verify the workstream acceptance gate**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_case_study_site.py' -v
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_case_study.py
```

Expected: all tests pass; no broken local asset links, forbidden sensitive terms, unsupported claims, or content-value mismatches.

- [ ] **Step 5: Commit the completed workstream**

```powershell
git add case-study/index.html case-study/print.html case-study/styles case-study/scripts case-study/content case-study/assets case-study/exports case-study/offline scripts/validate_case_study.py scripts/export_case_study_pdf.mjs tests/test_case_study_site.py
git commit -m "feat: publish Lean 6S case study site and PDF"
```

## Task 3: Complete the Project-Mastery Handbook

**Files:**
- Follow: `docs/superpowers/plans/2026-07-19-lean-6s-project-mastery.md`
- Produce: `case-study/mastery/README.md`
- Produce: `case-study/mastery/interview-q-and-a.md`

**Interfaces:**
- Consumes: current `SKILL.md`, `references/*.md`, `scripts/lean_6s_mvp.py`, case libraries, and the frozen public narrative.
- Produces: private learning modules, exercises, and interview scripts.

- [ ] **Step 1: Execute every checkbox in the mastery plan**

Do not publish `case-study/mastery/` with the public site or offline public package.

- [ ] **Step 2: Verify the workstream acceptance gate**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_mastery_materials.py' -v
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_mastery_materials.py
```

Expected: all tests pass; every referenced function exists, every demonstration command runs, and no interview answer overstates authorship or evidence.

- [ ] **Step 3: Complete the spoken-answer gate with the user**

Ask the user to deliver the 3-minute summary and explain one `triage()` walkthrough without reading the handbook. Record only learning gaps, not a fabricated pass result, in `case-study/mastery/progress.md`.

- [ ] **Step 4: Commit the completed workstream**

```powershell
git add case-study/mastery scripts/validate_mastery_materials.py tests/test_mastery_materials.py
git commit -m "docs: add Lean 6S project mastery handbook"
```

## Task 4: Final Cross-Artifact Release Audit

**Files:**
- Verify: `case-study/index.html`
- Verify: `case-study/print.html`
- Verify: `case-study/exports/lean-6s-case-study.pdf`
- Verify: `case-study/offline/`
- Verify: `case-study/testing/report.md`
- Verify: `case-study/mastery/README.md`
- Create: `case-study/RELEASE-CHECKLIST.md`

**Interfaces:**
- Consumes: all three completed workstreams.
- Produces: one signed-off checklist for public release and private interview preparation.

- [ ] **Step 1: Create the release checklist with exact gates**

Create `case-study/RELEASE-CHECKLIST.md` with unchecked items for:

```markdown
# Release Checklist

- [ ] Site opens from a public URL without login.
- [ ] Offline `index.html` opens with images and core content intact.
- [ ] PDF contains 8–12 pages and all links/QR codes work.
- [ ] Site, PDF, and report use identical frozen metrics.
- [ ] Synthetic testing is never labeled as real user research.
- [ ] “31/31” is accompanied by its generalization limitation.
- [ ] No original acceptance-report file is included in public artifacts.
- [ ] Privacy scan reports zero forbidden terms and zero unreviewed images.
- [ ] Desktop, tablet, and mobile screenshots have been visually reviewed.
- [ ] The user can deliver the 3-minute project explanation.
```

- [ ] **Step 2: Run the complete automated suite**

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: all project, synthetic-test, site, and mastery validation tests pass.

- [ ] **Step 3: Re-run the existing Lean 6S regression suites**

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\lean_6s_mvp.py --case-file examples\cases.md --test-cases --pretty
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\lean_6s_mvp.py --case-file examples\cases2.md --test-cases --pretty
```

Expected: both suites retain full pass results for primary, secondary, habitual, and closure fields.

- [ ] **Step 4: Complete manual release checks**

Open the online candidate, offline package, and PDF on a second device or a clean browser profile. Check every item in `RELEASE-CHECKLIST.md` only after direct verification.

- [ ] **Step 5: Commit the release audit**

```powershell
git add case-study/RELEASE-CHECKLIST.md
git commit -m "chore: complete case study release audit"
```
