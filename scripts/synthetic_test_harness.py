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
