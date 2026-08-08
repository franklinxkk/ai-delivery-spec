#!/usr/bin/env python3
"""Validate that every scripts/validators/*.py is wired or explicitly documented as manual.

Each validator must satisfy one of:
(a) referenced (by module stem or file name) from scripts/quality_gate.py or
    scripts/ai_delivery_spec_cli.py;
(b) explicitly marked "手动执行"/"未纳入 gate" on the same line in README.md or
    references/*.md.
Orphans are reported as BLOCK.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC_FILES = lambda root: [root / "README.md", *sorted((root / "references").glob("*.md"))]
MANUAL_MARKERS = ("手动执行", "未纳入 gate", "未纳入gate")


def find_orphans(root: Path = ROOT) -> list[str]:
    """Return orphan validator names; exposed for quality_gate integration."""
    validator_dir = root / "scripts" / "validators"
    callers = (
        root / "scripts" / "quality_gate.py",
        root / "scripts" / "ai_delivery_spec_cli.py",
    )
    caller_text = "\n".join(
        caller.read_text(encoding="utf-8") for caller in callers if caller.is_file()
    )
    doc_lines = [
        line
        for doc in DOC_FILES(root)
        if doc.is_file()
        for line in doc.read_text(encoding="utf-8").splitlines()
    ]
    orphans: list[str] = []
    for path in sorted(validator_dir.glob("*.py")):
        if path.name.startswith("__"):
            continue
        stem = path.stem
        if stem in caller_text or path.name in caller_text:
            continue
        if any(stem in line and any(marker in line for marker in MANUAL_MARKERS) for line in doc_lines):
            continue
        orphans.append(path.name)
    return orphans


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT, help="发布包根目录，默认为本仓库根")
    args = parser.parse_args()
    root = args.root.resolve()
    orphans = find_orphans(root)
    if orphans:
        for name in orphans:
            print(f"BLOCK: 孤儿校验器未被 gate/CLI 调用，也未在文档标注手动执行: {name}")
        return 1
    print("PASS: every validator is wired into gate/CLI or explicitly marked manual")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
