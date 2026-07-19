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
    r"(?<![\d.])1[3-9]\d{9}(?![\d.])",
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


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        for name in ("href", "src"):
            value = values.get(name)
            if value:
                self.references.append(value)


def validate_local_references(html_path: Path, public_root: Path) -> list[str]:
    parser = ReferenceParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    root = public_root.resolve()
    for reference in parser.references:
        if reference.startswith(("#", "http://", "https://", "mailto:")):
            continue
        candidate = (html_path.parent / reference.split("#", 1)[0]).resolve()
        if root not in candidate.parents and candidate != root:
            errors.append(f"reference escapes public root: {reference}")
        elif not candidate.exists():
            errors.append(f"missing local reference: {reference}")
    return errors


def validate_asset_manifest(public_root: Path) -> list[str]:
    manifest_path = public_root / "assets" / "asset-manifest.json"
    manifest = load_json(manifest_path)
    errors: list[str] = []
    for asset in manifest.get("assets", []):
        if not asset.get("public_use"):
            continue
        if asset.get("privacy_review") != "passed":
            errors.append(f"asset privacy review is not passed: {asset.get('id')}")
        if not (public_root / "assets" / asset["path"]).is_file():
            errors.append(f"manifest asset is missing: {asset['path']}")
    return errors


def public_text_files(root: Path, excluded: set[str] | None = None) -> list[Path]:
    excluded = excluded or set()
    allowed_suffixes = {".html", ".css", ".js", ".json", ".svg", ".txt", ".md"}
    return [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in allowed_suffixes
        and not any(part in excluded for part in path.relative_to(root).parts)
    ]


def validate_offline_package(offline: Path) -> list[str]:
    required = {
        "index.html",
        "exports/lean-6s-case-study.pdf",
        "content/synthetic-test-summary.js",
    }
    relative = {
        path.relative_to(offline).as_posix()
        for path in offline.rglob("*")
        if path.is_file()
    }
    errors = [f"offline package missing: {path}" for path in sorted(required - relative)]
    forbidden = [
        path
        for path in relative
        if path.startswith(("testing/", "mastery/")) or "验收报告" in path
    ]
    errors.extend(f"offline package contains private path: {path}" for path in forbidden)
    if (offline / "index.html").exists():
        errors.extend(validate_local_references(offline / "index.html", offline))
    return errors


def main() -> None:
    claims = load_json(PUBLIC_ROOT / "content" / "claims.json")
    evidence = load_json(PUBLIC_ROOT / "content" / "evidence-index.json")
    index = PUBLIC_ROOT / "index.html"
    print_page = PUBLIC_ROOT / "print.html"
    offline = PUBLIC_ROOT / "offline"

    checks: list[tuple[str, list[str]]] = [
        ("evidence mappings", validate_evidence(ROOT, claims, evidence)),
        (
            "screen sections",
            []
            if len(section_ids(index)) == 9
            else [f"expected 9 screen sections, found {len(section_ids(index))}"],
        ),
        (
            "print pages",
            []
            if page_ids(print_page) == [f"page-{index}" for index in range(1, 11)]
            else ["print page ids are not page-1 through page-10"],
        ),
        (
            "local references",
            validate_local_references(index, PUBLIC_ROOT)
            + validate_local_references(print_page, PUBLIC_ROOT),
        ),
        (
            "shared claims",
            validate_shared_claims([index, print_page], claims),
        ),
        (
            "privacy findings",
            scan_forbidden_text(
                public_text_files(
                    PUBLIC_ROOT,
                    excluded={"testing", "mastery", "offline"},
                )
            ),
        ),
        ("asset manifest", validate_asset_manifest(PUBLIC_ROOT)),
        (
            "offline package",
            validate_offline_package(offline)
            + scan_forbidden_text(public_text_files(offline)),
        ),
    ]
    errors = [error for _, findings in checks for error in findings]
    if errors:
        print("Case study validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Case study validation passed:")
    print("- evidence mappings: valid")
    print("- screen sections: 9")
    print("- print pages: 10")
    print("- local references: valid")
    print("- shared claims: consistent")
    print("- privacy findings: 0")
    print("- asset manifest: valid")
    print("- offline package: valid")


if __name__ == "__main__":
    main()
