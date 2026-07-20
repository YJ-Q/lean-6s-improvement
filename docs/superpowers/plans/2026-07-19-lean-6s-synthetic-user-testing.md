# Lean 6S Synthetic-User Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run a reproducible 30-session formative evaluation comparing generic-AI and Skill-enabled responses across five synthetic user types and three Lean 6S task classes.

**Architecture:** Freeze personas, scenarios, response conditions, and a 0–2 scoring rubric before generating any session. Store each transcript as structured JSON, validate and aggregate it with a Python standard-library harness, and publish a report that clearly labels the work as synthetic testing rather than real-user research.

**Tech Stack:** JSON, Markdown, Python 3.11+ standard library (`argparse`, `json`, `pathlib`, `statistics`, `unittest`), existing `SKILL.md` and Lean 6S references.

## Global Constraints

- Create exactly 5 personas, 3 scenarios, 2 conditions, and 30 unique sessions.
- Conditions are `baseline` and `skill`; never reuse a generated answer between them.
- Baseline generation must occur in an independent context that is not given `SKILL.md` or `references/`.
- Skill generation must use the current `SKILL.md` and only the reference file required by the scenario.
- Freeze catalogs and rubric in Git before generating sessions.
- Score every rubric dimension from 0 to 2 and attach a concrete evidence note.
- Preserve failed and low-scoring sessions.
- Use the phrases “合成用户测试” and “不等同于真实用户研究” in every public summary.
- Do not report synthetic satisfaction, productivity, accident reduction, ROI, or statistical significance.
- Use only Python standard-library code for validation and aggregation.

---

## File Map

- Create `case-study/testing/README.md`: purpose, limitations, directory guide.
- Create `case-study/testing/protocol.md`: exact generation and scoring procedure.
- Create `case-study/testing/personas.json`: five frozen persona cards.
- Create `case-study/testing/scenarios.json`: three frozen tasks and hidden facts.
- Create `case-study/testing/rubric.json`: eight 0–2 dimensions.
- Create `case-study/testing/sessions/baseline/*.json`: 15 baseline transcripts.
- Create `case-study/testing/sessions/skill/*.json`: 15 Skill-enabled transcripts.
- Create `case-study/testing/results.json`: deterministic aggregate output.
- Create `case-study/testing/report.md`: findings, failures, and limitations.
- Create `case-study/content/synthetic-test-summary.js`: public-safe data projection.
- Create `scripts/synthetic_test_harness.py`: catalog/session validation and aggregation CLI.
- Create `tests/test_synthetic_test_harness.py`: unit tests for the harness.

## Task 1: Freeze the Test Catalogs and Protocol

**Files:**
- Create: `case-study/testing/README.md`
- Create: `case-study/testing/protocol.md`
- Create: `case-study/testing/personas.json`
- Create: `case-study/testing/scenarios.json`
- Create: `case-study/testing/rubric.json`
- Test: `tests/test_synthetic_test_harness.py`

**Interfaces:**
- Consumes: product intent in `docs/superpowers/specs/2026-07-19-lean-6s-case-study-design.md`.
- Produces: catalogs keyed by `persona_id`, `scenario_id`, and rubric `dimension_id` for all later session files.

- [ ] **Step 1: Write the failing catalog-shape test**

Create `tests/test_synthetic_test_harness.py` with:

```python
import importlib.util
import json
import tempfile
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
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_synthetic_test_harness.CatalogTests -v
```

Expected: FAIL because `scripts/synthetic_test_harness.py` and catalog files do not exist.

- [ ] **Step 3: Create the five exact persona cards**

Create `case-study/testing/personas.json` as a JSON array with these fixed records:

```json
[
  {
    "id": "P01",
    "name": "精益新手班组长",
    "role": "生产班组长",
    "lean_experience": "low",
    "digital_literacy": "medium",
    "communication_style": "口语化、先说现象、很少主动给数量和历史",
    "cooperation": "回答追问，但每轮只补一到两个事实",
    "goal": "在当班结束前拿到能派给班组的动作",
    "risk": "容易把提醒员工当作主要对策"
  },
  {
    "id": "P02",
    "name": "时间紧张的仓库主管",
    "role": "仓库主管",
    "lean_experience": "medium",
    "digital_literacy": "high",
    "communication_style": "短句、批量描述、希望直接复制到台账",
    "cooperation": "只有追问会改变派工时才愿意回答",
    "goal": "快速得到责任、期限、验收和证据字段",
    "risk": "对长篇分析失去耐心"
  },
  {
    "id": "P03",
    "name": "风险敏感的 EHS 人员",
    "role": "EHS 专员",
    "lean_experience": "medium",
    "digital_literacy": "medium",
    "communication_style": "关注消防、逃生、配电和人员路径",
    "cooperation": "会提供风险边界，但要求回答区分事实与推断",
    "goal": "确认风险先受控，再讨论长期措施",
    "risk": "对未经证实的高风险判断非常敏感"
  },
  {
    "id": "P04",
    "name": "有经验的精益顾问",
    "role": "精益改善顾问",
    "lean_experience": "high",
    "digital_literacy": "high",
    "communication_style": "会挑战主副分类、系统原因和闭环证据",
    "cooperation": "完整回答，但会追问判断依据",
    "goal": "检查 Skill 是否只是关键词匹配和泛化建议",
    "risk": "发现规则矛盾后会降低信任"
  },
  {
    "id": "P05",
    "name": "数字工具不熟练的现场管理者",
    "role": "区域负责人",
    "lean_experience": "low",
    "digital_literacy": "low",
    "communication_style": "一句话描述、容易误解专业术语",
    "cooperation": "追问超过三个或一次包含多个概念时会漏答",
    "goal": "知道今天先做什么以及怎样算完成",
    "risk": "复杂输出会增加使用负担"
  }
]
```

- [ ] **Step 4: Create the three exact scenario records**

Create `case-study/testing/scenarios.json` with:

```json
[
  {
    "id": "S01",
    "type": "complete_information",
    "title": "安全疏散通道反复堆放托盘",
    "initial_message": "包装区安全疏散通道黄线内又堆了6个空托盘，上周清走过一次，叉车下班前会来拉走。请告诉我怎么整改。",
    "hidden_facts": {
      "location": "包装区安全疏散通道",
      "object": "6个空托盘",
      "risk_boundary": "黄线内堆放，影响人员疏散路径",
      "recurrence": "上周清理后复发",
      "existing_controls": "有黄线，无临时托盘位，无复查记录"
    },
    "expected_primary": "安全",
    "expected_secondary": ["整顿"],
    "expected_closure": null,
    "required_behavior": ["立即恢复通道", "建立临时托盘位置或清运触发条件", "要求原位置证据和复查"]
  },
  {
    "id": "S02",
    "type": "missing_information",
    "title": "工具架太乱",
    "initial_message": "车间工具架太乱了，帮我给个改善方案。",
    "hidden_facts": {
      "location": "维修工位工具架",
      "object": "仍在使用的扳手、量具和两件待报废工具",
      "risk_boundary": "不影响消防或人员必经路径",
      "recurrence": "首次系统整理，无法证明复发",
      "existing_controls": "没有形迹板、标签、数量标准或报废隔离区"
    },
    "expected_primary": "整顿",
    "expected_secondary": ["整理"],
    "expected_closure": null,
    "required_behavior": ["先问位置和对象", "确认物品是否需要保留", "不直接判定素养或习惯性异常"]
  },
  {
    "id": "S03",
    "type": "claimed_rectified",
    "title": "只把消防器材前纸箱搬走",
    "initial_message": "灭火器前的纸箱已经搬到仓库角落，也通知大家以后注意，照片拍好了，可以闭环了吗？",
    "hidden_facts": {
      "location": "包装仓灭火器前",
      "object": "纸箱",
      "risk_boundary": "原位置已清空",
      "recurrence": "此前没有正式记录",
      "existing_controls": "无禁放标识、无责任角色、无巡检项，仓库角落去向未验证"
    },
    "expected_primary": "安全",
    "expected_secondary": ["整理"],
    "expected_closure": "未闭环",
    "required_behavior": ["识别风险转移", "不把通知等同于防复发", "要求目标位置和复查证据"]
  }
]
```

- [ ] **Step 5: Create the exact eight-dimension rubric**

Create `case-study/testing/rubric.json`:

```json
{
  "scale": {"0": "未满足或造成误导", "1": "部分满足但存在关键缺口", "2": "满足且有具体证据"},
  "dimensions": [
    {"id": "R01", "name": "关键追问", "max_score": 2, "rule": "只问会改变风险、分类、措施或闭环的关键信息，最多3个"},
    {"id": "R02", "name": "事实边界", "max_score": 2, "rule": "区分已知事实、合理风险和待确认事项，不捏造"},
    {"id": "R03", "name": "分类逻辑", "max_score": 2, "rule": "主副分类与证据一致且会改变对策"},
    {"id": "R04", "name": "可派工性", "max_score": 2, "rule": "动作包含对象、动作、责任角色、期限、验收和证据"},
    {"id": "R05", "name": "验收可测量", "max_score": 2, "rule": "标准可观察、可测量、可拍照或可记录"},
    {"id": "R06", "name": "闭环严谨性", "max_score": 2, "rule": "识别风险转移、只通知、只清理和复发未升级"},
    {"id": "R07", "name": "角色适配", "max_score": 2, "rule": "内容长度、术语和格式匹配人物目标与数字熟练度"},
    {"id": "R08", "name": "对话负担", "max_score": 2, "rule": "用最少必要轮次完成判断，不重复追问已知信息"}
  ]
}
```

- [ ] **Step 6: Create the protocol and limitations text**

In `case-study/testing/protocol.md`, include the exact session order `P01-S01` through `P05-S03`, first for baseline and then for Skill, but randomize scenario order within each persona using the fixed order `S02, S01, S03` for odd persona IDs and `S03, S02, S01` for even persona IDs.

Define these condition prompts verbatim:

```text
Baseline condition:
你是一个通用 AI 助手。请帮助用户处理制造现场管理问题。不要读取、引用或模拟本项目的 SKILL.md、references 或案例标注。根据用户当前提供的信息自然回答。

Skill condition:
严格使用当前仓库 SKILL.md。分类时加载 references/classification.md；判断习惯性异常时加载 references/habitual-abnormality.md；出现“已整改/闭环”时加载 references/closure-check.md。不得使用案例期望答案直接生成结论。
```

Define the transcript-generation rule: the synthetic user may reveal only facts present in that scenario's `hidden_facts`; it must follow the persona's cooperation behavior; the assistant must not see `expected_*` fields.

Create `case-study/testing/README.md` with this statement near the top:

```markdown
本目录记录合成用户测试，用于在真人招募前发现输入、追问和规则问题。它不等同于真实用户研究，不能证明满意度、效率提升、业务收益或真实世界准确率。
```

- [ ] **Step 7: Create the minimal catalog validator**

Create `scripts/synthetic_test_harness.py` initially with:

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PERSONA_IDS = ["P01", "P02", "P03", "P04", "P05"]
SCENARIO_IDS = ["S01", "S02", "S03"]
CONDITIONS = ["baseline", "skill"]
RUBRIC_IDS = [f"R{index:02d}" for index in range(1, 9)]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalogs(root: Path) -> list[str]:
    errors: list[str] = []
    personas = load_json(root / "personas.json")
    scenarios = load_json(root / "scenarios.json")
    rubric = load_json(root / "rubric.json")

    if [item.get("id") for item in personas] != PERSONA_IDS:
        errors.append("personas must use P01-P05 in order")
    if [item.get("id") for item in scenarios] != SCENARIO_IDS:
        errors.append("scenarios must use S01-S03 in order")
    if [item.get("id") for item in rubric.get("dimensions", [])] != RUBRIC_IDS:
        errors.append("rubric must use R01-R08 in order")
    if any(item.get("max_score") != 2 for item in rubric.get("dimensions", [])):
        errors.append("every rubric dimension must have max_score=2")
    return errors
```

- [ ] **Step 8: Run the catalog tests and verify they pass**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_synthetic_test_harness.CatalogTests -v
```

Expected: 2 tests PASS.

- [ ] **Step 9: Commit the frozen test design**

```powershell
git add case-study/testing/README.md case-study/testing/protocol.md case-study/testing/personas.json case-study/testing/scenarios.json case-study/testing/rubric.json scripts/synthetic_test_harness.py tests/test_synthetic_test_harness.py
git commit -m "test: freeze synthetic user study design"
```

## Task 2: Add Session Validation and Aggregation

**Files:**
- Modify: `scripts/synthetic_test_harness.py`
- Modify: `tests/test_synthetic_test_harness.py`
- Create: `case-study/testing/sessions/baseline/.gitkeep`
- Create: `case-study/testing/sessions/skill/.gitkeep`

**Interfaces:**
- Consumes: frozen catalogs from Task 1.
- Produces: `validate_sessions(root) -> tuple[list[dict], list[str]]`, `aggregate_sessions(sessions) -> dict`, and CLI commands `validate` and `aggregate`.

- [ ] **Step 1: Write failing tests for a valid session and exact matrix**

Append to `tests/test_synthetic_test_harness.py`:

```python
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
                {"speaker": "assistant", "text": "请确认具体位置。"}
            ],
            "ratings": [
                {"dimension_id": f"R{i:02d}", "score": 1, "evidence": "记录中的具体证据"}
                for i in range(1, 9)
            ],
            "review": {"strengths": ["追问位置"], "failures": ["措施不完整"], "notes": "形成性测试"}
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
```

- [ ] **Step 2: Run the new tests and verify they fail**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_synthetic_test_harness.SessionTests -v
```

Expected: FAIL because `validate_session` and `aggregate_sessions` are undefined.

- [ ] **Step 3: Implement validation, aggregation, and CLI**

Extend `scripts/synthetic_test_harness.py` with:

```python
import argparse
from collections import defaultdict
from statistics import mean


def validate_session(session: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    condition = session.get("condition")
    persona_id = session.get("persona_id")
    scenario_id = session.get("scenario_id")
    expected_id = f"{condition}-{persona_id}-{scenario_id}"
    if condition not in CONDITIONS:
        errors.append("condition must be baseline or skill")
    if persona_id not in PERSONA_IDS:
        errors.append("unknown persona_id")
    if scenario_id not in SCENARIO_IDS:
        errors.append("unknown scenario_id")
    if session.get("session_id") != expected_id:
        errors.append(f"session_id must be {expected_id}")
    transcript = session.get("transcript", [])
    if len(transcript) < 2 or transcript[0].get("speaker") != "user":
        errors.append("transcript must start with a user turn and include an assistant response")
    ratings = session.get("ratings", [])
    if [item.get("dimension_id") for item in ratings] != RUBRIC_IDS:
        errors.append("ratings must contain R01-R08 in order")
    for rating in ratings:
        dimension_id = rating.get("dimension_id", "unknown")
        if rating.get("score") not in (0, 1, 2):
            errors.append(f"{dimension_id} score must be 0, 1, or 2")
        if not str(rating.get("evidence", "")).strip():
            errors.append(f"{dimension_id} requires evidence")
    review = session.get("review", {})
    if not isinstance(review.get("strengths"), list) or not isinstance(review.get("failures"), list):
        errors.append("review strengths and failures must be lists")
    return errors


def validate_sessions(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    sessions: list[dict[str, Any]] = []
    errors = validate_catalogs(root)
    seen: set[str] = set()
    for condition in CONDITIONS:
        folder = root / "sessions" / condition
        for path in sorted(folder.glob("*.json")):
            session = load_json(path)
            sessions.append(session)
            session_errors = validate_session(session)
            errors.extend(f"{path.name}: {error}" for error in session_errors)
            session_id = session.get("session_id", "")
            if session_id in seen:
                errors.append(f"duplicate session_id: {session_id}")
            seen.add(session_id)
    if len(sessions) not in (0, 30):
        errors.append(f"expected 0 or 30 sessions during validation, found {len(sessions)}")
    if len(sessions) == 30:
        expected = {
            f"{condition}-{persona_id}-{scenario_id}"
            for condition in CONDITIONS
            for persona_id in PERSONA_IDS
            for scenario_id in SCENARIO_IDS
        }
        missing = sorted(expected - seen)
        if missing:
            errors.append("missing sessions: " + ", ".join(missing))
    return sessions, errors


def aggregate_sessions(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for session in sessions:
        grouped[session["condition"]].append(session)
    conditions: dict[str, Any] = {}
    for condition, records in grouped.items():
        totals = [sum(item["score"] for item in record["ratings"]) for record in records]
        by_dimension = {
            dimension_id: mean(
                next(item["score"] for item in record["ratings"] if item["dimension_id"] == dimension_id)
                for record in records
            )
            for dimension_id in RUBRIC_IDS
        }
        conditions[condition] = {
            "session_count": len(records),
            "mean_total": round(mean(totals), 2),
            "max_total": 16,
            "dimension_means": {key: round(value, 2) for key, value in by_dimension.items()},
            "sessions_with_failures": sum(bool(record["review"]["failures"]) for record in records),
        }
    return {
        "study_label": "合成用户测试",
        "disclaimer": "不等同于真实用户研究",
        "session_count": len(sessions),
        "personas": len(PERSONA_IDS),
        "scenarios": len(SCENARIO_IDS),
        "conditions": conditions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and aggregate synthetic Lean 6S sessions")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "aggregate"):
        command = subparsers.add_parser(name)
        command.add_argument("--root", type=Path, default=Path("case-study/testing"))
    args = parser.parse_args()
    sessions, errors = validate_sessions(args.root)
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    if args.command == "validate":
        print(json.dumps({"ok": True, "sessions": len(sessions), "schema_errors": 0}, ensure_ascii=False))
        return
    result = aggregate_sessions(sessions)
    output = args.root / "results.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the session tests and verify they pass**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_synthetic_test_harness.SessionTests -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Create empty tracked session directories**

Create empty `.gitkeep` files in `case-study/testing/sessions/baseline/` and `case-study/testing/sessions/skill/`, then run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\synthetic_test_harness.py validate --root case-study\testing
```

Expected: `{"ok": true, "sessions": 0, "schema_errors": 0}`.

- [ ] **Step 6: Commit the harness**

```powershell
git add scripts/synthetic_test_harness.py tests/test_synthetic_test_harness.py case-study/testing/sessions
git commit -m "test: add synthetic session validation harness"
```

## Task 3: Generate and Record the 30 Sessions

**Files:**
- Create: `case-study/testing/sessions/baseline/baseline-P01-S01.json` through `baseline-P05-S03.json`
- Create: `case-study/testing/sessions/skill/skill-P01-S01.json` through `skill-P05-S03.json`

**Interfaces:**
- Consumes: frozen persona, scenario, protocol, and rubric files.
- Produces: 30 transcripts with empty-independent scoring completed in the next pass.

- [ ] **Step 1: Create the exact session JSON template**

For each condition/persona/scenario combination, use this structure. The record below is a schema fixture only; actual study files must contain the verbatim transcript and evidence from their own session rather than copying this fixture's scores:

```json
{
  "session_id": "skill-P01-S01",
  "condition": "skill",
  "persona_id": "P01",
  "scenario_id": "S01",
  "transcript": [
    {"speaker": "user", "text": "包装区安全疏散通道黄线内又堆了6个空托盘，上周清走过一次，叉车下班前会来拉走。请告诉我怎么整改。"},
    {"speaker": "assistant", "text": "先恢复疏散通道，当班由包装区班组长将6个托盘移至明确的临时托盘位；完成标准是黄线内0托盘，并保留原位置整改前后照片。由于上周清理后复发，还需确认现有临时存放位置和清运触发条件。"}
  ],
  "ratings": [
    {"dimension_id": "R01", "score": 2, "evidence": "只追问会影响防复发的临时存放位置和清运触发条件"},
    {"dimension_id": "R02", "score": 2, "evidence": "沿用用户已提供的6个托盘、黄线内和复发事实，没有补造距离"},
    {"dimension_id": "R03", "score": 1, "evidence": "回答体现安全优先，但没有明确写出整顿副分类"},
    {"dimension_id": "R04", "score": 2, "evidence": "包含对象、动作、班组长、当班期限、黄线内0托盘和照片证据"},
    {"dimension_id": "R05", "score": 2, "evidence": "黄线内0托盘可观察、可拍照"},
    {"dimension_id": "R06", "score": 1, "evidence": "提出防复发信息需求，但尚未要求连续复查记录"},
    {"dimension_id": "R07", "score": 2, "evidence": "输出短且先给当班动作，符合班组长目标"},
    {"dimension_id": "R08", "score": 2, "evidence": "一次回答内给临时控制并只保留一个后续确认主题"}
  ],
  "review": {"strengths": ["当班动作和验收标准明确"], "failures": ["复查周期不足"], "notes": "结构示例，不计入正式30个会话"}
}
```

- [ ] **Step 2: Generate the 15 baseline sessions in isolated contexts**

For each baseline session:

1. Start a fresh generation context with the baseline condition prompt only.
2. Provide the persona behavior without revealing `expected_*` or `required_behavior`.
3. Send `initial_message`.
4. If the assistant asks questions, answer only according to `hidden_facts` and persona cooperation behavior.
5. Stop when the assistant presents a final action/closure response or after four assistant turns.
6. Save every turn verbatim.

Do not consult `SKILL.md`, reference rules, or the Skill transcript for the matching task while generating baseline responses.

Generate and save one session per checkbox in the fixed persona order and the scenario order defined in `protocol.md`:

- [ ] `baseline-P01-S02.json`
- [ ] `baseline-P01-S01.json`
- [ ] `baseline-P01-S03.json`
- [ ] `baseline-P02-S03.json`
- [ ] `baseline-P02-S02.json`
- [ ] `baseline-P02-S01.json`
- [ ] `baseline-P03-S02.json`
- [ ] `baseline-P03-S01.json`
- [ ] `baseline-P03-S03.json`
- [ ] `baseline-P04-S03.json`
- [ ] `baseline-P04-S02.json`
- [ ] `baseline-P04-S01.json`
- [ ] `baseline-P05-S02.json`
- [ ] `baseline-P05-S01.json`
- [ ] `baseline-P05-S03.json`

- [ ] **Step 3: Generate the 15 Skill sessions in fresh isolated contexts**

Repeat the same procedure using the Skill condition prompt. Load the current `SKILL.md`; load `classification.md` and `habitual-abnormality.md` when needed; load `closure-check.md` for S03. Do not show the assistant `expected_*` or `required_behavior`.

- [ ] `skill-P01-S02.json`
- [ ] `skill-P01-S01.json`
- [ ] `skill-P01-S03.json`
- [ ] `skill-P02-S03.json`
- [ ] `skill-P02-S02.json`
- [ ] `skill-P02-S01.json`
- [ ] `skill-P03-S02.json`
- [ ] `skill-P03-S01.json`
- [ ] `skill-P03-S03.json`
- [ ] `skill-P04-S03.json`
- [ ] `skill-P04-S02.json`
- [ ] `skill-P04-S01.json`
- [ ] `skill-P05-S02.json`
- [ ] `skill-P05-S01.json`
- [ ] `skill-P05-S03.json`

- [ ] **Step 4: Score every session in a separate review pass**

Review sessions in filename order without editing transcript text. For each R01–R08:

- assign 0, 1, or 2 using `rubric.json`;
- quote or paraphrase the exact transcript evidence;
- add at least one strength or failure, allowing an empty strength list only when all eight scores are 0;
- write session-specific evidence and notes rather than copying the schema fixture.

For S03, read `references/closure-check.md` during scoring. For S01/S02, read the relevant classification and habitual-abnormality rules.

Score one pair per checkbox so the reviewer compares the same persona/scenario across conditions without editing either transcript:

- [ ] P01-S01 baseline/Skill pair
- [ ] P01-S02 baseline/Skill pair
- [ ] P01-S03 baseline/Skill pair
- [ ] P02-S01 baseline/Skill pair
- [ ] P02-S02 baseline/Skill pair
- [ ] P02-S03 baseline/Skill pair
- [ ] P03-S01 baseline/Skill pair
- [ ] P03-S02 baseline/Skill pair
- [ ] P03-S03 baseline/Skill pair
- [ ] P04-S01 baseline/Skill pair
- [ ] P04-S02 baseline/Skill pair
- [ ] P04-S03 baseline/Skill pair
- [ ] P05-S01 baseline/Skill pair
- [ ] P05-S02 baseline/Skill pair
- [ ] P05-S03 baseline/Skill pair

- [ ] **Step 5: Validate the full session matrix**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\synthetic_test_harness.py validate --root case-study\testing
```

Expected: validation reports 30 sessions and zero errors. If a session is missing or evidence is empty, fix the record without changing the transcript.

- [ ] **Step 6: Commit immutable transcripts and ratings**

```powershell
git add case-study/testing/sessions
git commit -m "test: record synthetic Lean 6S sessions"
```

## Task 4: Aggregate Results and Write the Evidence Report

**Files:**
- Create: `case-study/testing/results.json`
- Create: `case-study/testing/report.md`
- Create: `case-study/content/synthetic-test-summary.js`
- Modify: `tests/test_synthetic_test_harness.py`

**Interfaces:**
- Consumes: 30 validated session records.
- Produces: deterministic metrics and a public-safe JavaScript projection for the site.

- [ ] **Step 1: Write a failing test for the public projection**

Append:

```python
class PublicProjectionTests(unittest.TestCase):
    def test_public_projection_has_required_disclaimer(self):
        module = load_module()
        result = {
            "study_label": "合成用户测试",
            "disclaimer": "不等同于真实用户研究",
            "session_count": 30,
            "personas": 5,
            "scenarios": 3,
            "conditions": {"baseline": {"mean_total": 8.0}, "skill": {"mean_total": 12.0}}
        }
        projection = module.to_public_projection(result)
        self.assertEqual(projection["label"], "合成用户测试")
        self.assertEqual(projection["disclaimer"], "不等同于真实用户研究")
        self.assertNotIn("satisfaction", projection)
```

- [ ] **Step 2: Run the test and verify it fails**

Expected: FAIL because `to_public_projection` is undefined.

- [ ] **Step 3: Implement public projection output**

Add to `scripts/synthetic_test_harness.py`:

```python
def to_public_projection(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": result["study_label"],
        "disclaimer": result["disclaimer"],
        "sessions": result["session_count"],
        "personas": result["personas"],
        "scenarios": result["scenarios"],
        "condition_scores": {
            key: value["mean_total"]
            for key, value in result["conditions"].items()
        },
        "dimension_scores": {
            key: value["dimension_means"]
            for key, value in result["conditions"].items()
        },
        "interpretation": "用于发现输入、追问与规则问题，不证明真实用户满意度或业务效果。"
    }
```

In the `aggregate` CLI branch, after writing `results.json`, write `case-study/content/synthetic-test-summary.js` as:

```python
projection_path = Path("case-study/content/synthetic-test-summary.js")
projection_path.parent.mkdir(parents=True, exist_ok=True)
projection_path.write_text(
    "window.SYNTHETIC_TEST_SUMMARY = "
    + json.dumps(to_public_projection(result), ensure_ascii=False, indent=2)
    + ";\n",
    encoding="utf-8",
)
```

- [ ] **Step 4: Run all harness tests**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_synthetic_test_harness -v
```

Expected: all tests PASS.

- [ ] **Step 5: Generate deterministic results**

Run:

```powershell
& 'C:\Users\邓志谦\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\synthetic_test_harness.py aggregate --root case-study\testing
```

Expected: creates `results.json` and `synthetic-test-summary.js` from the frozen sessions without manual metric entry.

- [ ] **Step 6: Write the report from actual results**

Create `case-study/testing/report.md` with these exact sections:

```markdown
# Lean 6S Skill 合成用户测试报告

## 结论摘要
## 测试目的与非目标
## 人物与任务矩阵
## 普通 AI 与 Skill 结果
## 分角色发现
## 分场景发现
## 典型成功会话
## 典型失败会话
## 产品改进清单
## 方法限制
```

Populate every number from `results.json`. Cite session IDs beside qualitative findings. In “方法限制”, explicitly state that personas, messages, and scoring were AI-mediated; the same project team designed the rubric; the study has no statistical or market-validity claim; and real-user testing remains necessary.

- [ ] **Step 7: Verify public wording and failure retention**

Run:

```powershell
Select-String -Path case-study\testing\report.md,case-study\content\synthetic-test-summary.js -Pattern '合成用户测试|不等同于真实用户研究'
Select-String -Path case-study\testing\report.md -Pattern '失败|限制|真实用户'
```

Expected: required labels appear in both public outputs; the report contains failure, limitation, and real-user caveats.

- [ ] **Step 8: Commit the results and report**

```powershell
git add scripts/synthetic_test_harness.py tests/test_synthetic_test_harness.py case-study/testing/results.json case-study/testing/report.md case-study/content/synthetic-test-summary.js
git commit -m "test: report synthetic Lean 6S evaluation"
```
