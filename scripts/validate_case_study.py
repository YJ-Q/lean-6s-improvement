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


def validate_evidence(
    root: Path,
    claims: dict[str, Any],
    evidence: dict[str, list[str]],
) -> list[str]:
    errors: list[str] = []
    required = [
        "project_title",
        "role",
        "existing_case_regression",
        "expert_review",
        "synthetic_testing",
    ]
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
        matches = [
            pattern
            for pattern in FORBIDDEN_PATTERNS
            if re.search(pattern, text, flags=re.IGNORECASE)
        ]
        if matches:
            findings.append(f"{path}: forbidden patterns {matches}")
    return findings


class StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[str] = []
        self.pages: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
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
