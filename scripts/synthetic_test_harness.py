#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
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
            key: value.get("dimension_means", {})
            for key, value in result["conditions"].items()
        },
        "interpretation": "用于发现输入、追问与规则问题，不证明真实用户满意度或业务效果。",
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
    projection_path = args.root.parent / "content" / "synthetic-test-summary.js"
    projection_path.parent.mkdir(parents=True, exist_ok=True)
    projection_path.write_text(
        "window.SYNTHETIC_TEST_SUMMARY = "
        + json.dumps(to_public_projection(result), ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
