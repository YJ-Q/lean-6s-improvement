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


def assert_safe_target() -> None:
    source = SOURCE.resolve()
    target = TARGET.resolve()
    if target.parent != source or target.name != "offline":
        raise RuntimeError(f"refusing to replace unexpected package target: {target}")


def main() -> None:
    assert_safe_target()
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True)

    for name in FILES:
        source = SOURCE / name
        destination = TARGET / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    for name in DIRECTORIES:
        source = SOURCE / name
        if source.exists():
            shutil.copytree(source, TARGET / name)

    manifest = json.loads(
        (SOURCE / "assets" / "asset-manifest.json").read_text(encoding="utf-8")
    )
    for asset in manifest["assets"]:
        if not asset.get("public_use"):
            continue
        if asset.get("privacy_review") != "passed":
            raise RuntimeError(
                f"public asset has not passed privacy review: {asset['id']}"
            )
        source = SOURCE / "assets" / asset["path"]
        if not source.is_file():
            raise FileNotFoundError(f"manifest asset is missing: {source}")
        destination = TARGET / "assets" / asset["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    print(f"Packaged public files to {TARGET}")


if __name__ == "__main__":
    main()
