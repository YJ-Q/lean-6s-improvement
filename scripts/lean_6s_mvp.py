#!/usr/bin/env python3
"""Rule-based MVP helper for Lean 6S issue triage and closure checks."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from typing import Iterable


CATEGORY_RULES = {
    "Safety / 安全": [
        "blocked extinguisher",
        "fire",
        "emergency",
        "exit",
        "guard",
        "slip",
        "trip",
        "forklift",
        "electric",
        "chemical",
        "ppe",
        "safety",
        "消防",
        "安全",
        "通道",
        "逃生",
        "灭火器",
        "配电",
        "护罩",
        "叉车",
        "滑倒",
    ],
    "Seiton / 整顿": [
        "no fixed location",
        "unlabeled",
        "label",
        "random",
        "search",
        "mixed location",
        "tool",
        "shelf",
        "shadow board",
        "定位",
        "标识",
        "标签",
        "乱放",
        "找不到",
        "工具",
        "货架",
        "混放",
    ],
    "Seiso / 清扫": [
        "oil",
        "leak",
        "dust",
        "chips",
        "trash",
        "waste",
        "dirty",
        "clean",
        "油",
        "漏",
        "灰尘",
        "铁屑",
        "垃圾",
        "脏",
        "清扫",
        "积水",
    ],
    "Seiri / 整理": [
        "obsolete",
        "unused",
        "expired",
        "scrap",
        "excess",
        "unneeded",
        "red tag",
        "呆滞",
        "不用",
        "过期",
        "报废",
        "多余",
        "废料",
        "红牌",
    ],
    "Seiketsu / 清洁": [
        "standard",
        "checklist",
        "different shift",
        "audit route",
        "标准",
        "点检",
        "检查表",
        "班组不一致",
        "清洁",
    ],
    "Shitsuke / 素养": [
        "everyone",
        "again",
        "habit",
        "ignored",
        "only before audit",
        "not follow",
        "大家",
        "又",
        "习惯",
        "没人管",
        "不执行",
        "检查前",
        "素养",
    ],
}

HABITUAL_PATTERNS = [
    "always",
    "often",
    "again",
    "every shift",
    "long-term",
    "everyone",
    "used to",
    "only before audit",
    "一直",
    "经常",
    "总是",
    "每班",
    "又",
    "反复",
    "习惯",
    "大家都",
    "检查前",
]

LOCATION_PATTERNS = [
    r"(warehouse|line\s*\d+|station\s*\w+|machine\s*\w+|aisle\s*\w+|rack\s*\w+)",
    r"(仓库|库区|产线|生产线|工位|设备区|通道|货架|机台|配电柜|消防栓|灭火器)(?:[A-Za-z0-9#_-]{0,12})?",
]


@dataclass
class Triage:
    location: str
    abnormality: str
    affected_object: str
    risk: str
    primary_category: str
    secondary_categories: list[str]
    habitual_judgment: str
    clarifying_questions: list[str]
    corrective_actions: list[dict[str, str]]
    acceptance_criteria: list[str]
    closure_judgment: dict[str, str] | None = None


def score_category(text: str, terms: Iterable[str]) -> int:
    lowered = text.lower()
    return sum(1 for term in terms if term.lower() in lowered)


def detect_location(text: str) -> str:
    for pattern in LOCATION_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return "Unknown"


def classify(text: str) -> tuple[str, list[str]]:
    scored = [
        (category, score_category(text, terms))
        for category, terms in CATEGORY_RULES.items()
    ]
    safety_score = next(score for category, score in scored if category == "Safety / 安全")
    if safety_score > 0 and re.search(
        r"(block|blocked|pile|stack|access|exit|堆|堵|占|挡|通道|消防|逃生|灭火器)",
        text,
        flags=re.IGNORECASE,
    ):
        scored = [
            (category, score + 10 if category == "Safety / 安全" else score)
            for category, score in scored
        ]
    scored.sort(key=lambda item: item[1], reverse=True)
    if scored[0][1] == 0:
        return "Unknown", []
    primary = scored[0][0]
    secondary = [category for category, score in scored[1:] if score > 0][:2]
    return primary, secondary


def habitual(text: str) -> str:
    hits = score_category(text, HABITUAL_PATTERNS)
    if hits >= 2:
        return "Habitual abnormality likely"
    if hits == 1:
        return "Habitual abnormality suspected"
    return "Not enough evidence"


def infer_object(text: str) -> str:
    candidates = [
        "tool",
        "material",
        "carton",
        "pallet",
        "oil",
        "waste",
        "fixture",
        "工具",
        "物料",
        "纸箱",
        "托盘",
        "油",
        "垃圾",
        "夹具",
    ]
    lowered = text.lower()
    for item in candidates:
        if item.lower() in lowered:
            return item
    return "Unknown"


def infer_risk(primary: str, text: str) -> str:
    if "Safety" in primary:
        return "Safety risk requiring immediate containment"
    if "Seiso" in primary:
        return "Contamination, slip, equipment, or quality risk"
    if "Seiton" in primary:
        return "Search time, mix-up, access, or placement discipline risk"
    if "Seiri" in primary:
        return "Space occupation, mix-up, hidden defect, or inventory risk"
    if "Shitsuke" in primary:
        return "Recurring noncompliance and weak management control risk"
    if "Seiketsu" in primary:
        return "Unstable standard and recurrence risk"
    return "Unknown risk; confirm impact and severity"


def missing_questions(location: str, affected_object: str, text: str) -> list[str]:
    questions: list[str] = []
    if location == "Unknown":
        questions.append("Which exact area, line, station, machine, aisle, or rack is affected?")
    if affected_object == "Unknown":
        questions.append("What exact object/material/equipment is abnormal, and roughly how much?")
    if not any(term in text.lower() for term in HABITUAL_PATTERNS):
        questions.append("Is this one-time, repeated, or something that tends to reappear after audits?")
    if len(text) < 30:
        questions.append("What visible evidence or risk has already appeared?")
    return questions[:3]


def build_actions(primary: str, habitual_judgment: str) -> list[dict[str, str]]:
    actions = [
        {
            "step": "Immediate containment",
            "action": "Remove or isolate the visible abnormality before the end of the shift.",
            "owner": "Area supervisor",
            "evidence": "After photo of the original location and affected object.",
        }
    ]
    if "Safety" in primary:
        actions.append(
            {
                "step": "Safety control",
                "action": "Restore required clearance/guarding and add a physical or visual control that prevents re-blocking or bypass.",
                "owner": "EHS owner plus area supervisor",
                "evidence": "Photo showing access clearance, control point, and supervisor verification.",
            }
        )
    elif "Seiton" in primary:
        actions.append(
            {
                "step": "Set in order",
                "action": "Define fixed location, label, max/min quantity, and return rule for the affected item.",
                "owner": "Line leader or warehouse owner",
                "evidence": "Location label or shadow board photo with item and quantity standard visible.",
            }
        )
    elif "Seiso" in primary:
        actions.append(
            {
                "step": "Clean and source control",
                "action": "Clean the area, identify the contamination source, and repair or capture the source.",
                "owner": "Maintenance owner plus area supervisor",
                "evidence": "Before/after photo and source-control record.",
            }
        )
    elif "Seiri" in primary:
        actions.append(
            {
                "step": "Sort",
                "action": "Red-tag unnecessary or unclear items and decide keep, move, scrap, or return by deadline.",
                "owner": "Area owner",
                "evidence": "Red-tag list with disposition result.",
            }
        )
    else:
        actions.append(
            {
                "step": "Standardize",
                "action": "Update the visible standard and inspection checklist for this abnormality.",
                "owner": "Area supervisor",
                "evidence": "Standard photo/checklist revision and shift briefing record.",
            }
        )
    if "likely" in habitual_judgment.lower() or "suspected" in habitual_judgment.lower():
        actions.append(
            {
                "step": "Recurrence prevention",
                "action": "Add a 3-check recurrence review and confirm whether the current standard is realistic during normal production.",
                "owner": "Area supervisor and process owner",
                "evidence": "Three consecutive check records with no recurrence or documented standard change.",
            }
        )
    return actions


def acceptance(primary: str) -> list[str]:
    base = [
        "Original location has no visible abnormal item or hazard.",
        "Owner, location, and expected state are visible or recorded.",
        "After photo covers the original location and affected object.",
    ]
    if "Safety" in primary:
        base.append("Safety access/control meets site requirement, with zero blockage or bypass.")
    if "Seiso" in primary:
        base.append("Contamination source is removed, repaired, or captured; area passes the next cleaning check.")
    if "Seiton" in primary:
        base.append("All affected items are in fixed locations with labels and quantity limits.")
    base.append("No recurrence in the next 3 daily checks or next scheduled layered audit.")
    return base


def closure_check(rectified_text: str | None) -> dict[str, str] | None:
    if not rectified_text:
        return None
    lowered = rectified_text.lower()
    evidence_hits = sum(
        term in lowered
        for term in [
            "photo",
            "label",
            "checklist",
            "owner",
            "audit",
            "3",
            "three",
            "照片",
            "标识",
            "点检",
            "责任人",
            "三次",
            "复查",
        ]
    )
    if evidence_hits >= 3:
        judgment = "Conditionally closed"
        gap = "Verify recurrence record and original-location evidence before full closure."
    elif evidence_hits >= 1:
        judgment = "Conditionally closed"
        gap = "Visible correction exists, but standard or recurrence evidence is incomplete."
    else:
        judgment = "Not closed"
        gap = "Claim lacks evidence against the acceptance criteria."
    return {
        "judgment": judgment,
        "evidence_considered": rectified_text,
        "gap": gap,
        "required_next_action": "Provide after photo, standard/control evidence, and recurrence check result.",
    }


def triage(problem: str, rectified_text: str | None = None) -> Triage:
    primary, secondary = classify(problem)
    location = detect_location(problem)
    affected_object = infer_object(problem)
    habitual_judgment = habitual(problem)
    questions = missing_questions(location, affected_object, problem)
    needs_clarification = primary == "Unknown" and len(questions) >= 2
    return Triage(
        location=location,
        abnormality=problem,
        affected_object=affected_object,
        risk=infer_risk(primary, problem),
        primary_category=primary,
        secondary_categories=secondary,
        habitual_judgment=habitual_judgment,
        clarifying_questions=questions,
        corrective_actions=[] if needs_clarification else build_actions(primary, habitual_judgment),
        acceptance_criteria=[] if needs_clarification else acceptance(primary),
        closure_judgment=closure_check(rectified_text),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Lean 6S MVP triage helper")
    parser.add_argument("--problem", required=True, help="Vague site issue description")
    parser.add_argument("--rectified-text", help="User's closure/evidence statement")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()
    result = asdict(triage(args.problem, args.rectified_text))
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
