#!/usr/bin/env python3
"""Block exact duplicated normative rules in runtime-loaded Markdown."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNTIME_FILES = [
    "SKILL.md",
    "references/requirement-management.md",
    "references/discover.md",
    "references/specify.md",
    "references/tool-adapters.md",
    "references/runtime/composition.md",
    "references/runtime/ai-coding-completeness.md",
    "references/runtime/change.md",
    "references/runtime/context-planning.md",
    "references/runtime/page-delivery-contract.md",
    "references/runtime/prototype-testability.md",
    "references/runtime/realtime-contract.md",
    "references/runtime/role-stage-playbook.md",
]
NORMATIVE = re.compile(r"\b(must|must not|never|do not|cannot|should not|required|禁止|必须|不得|不能)\b", re.I)


def normalize(line: str) -> str:
    line = re.sub(r"^[\s>*#-]+", "", line.strip())
    line = re.sub(r"`([^`]+)`", r"\1", line)
    line = re.sub(r"\s+", " ", line)
    return line.rstrip(".;。；").lower()


def main() -> int:
    occurrences: dict[str, list[str]] = defaultdict(list)
    for relative in RUNTIME_FILES:
        path = ROOT / relative
        in_fence = False
        for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if raw.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or raw.lstrip().startswith("|") or not NORMATIVE.search(raw):
                continue
            value = normalize(raw)
            if len(value) >= 55:
                occurrences[value].append(f"{relative}:{number}")

    duplicates = {text: paths for text, paths in occurrences.items() if len(paths) > 1}
    if duplicates:
        for text, paths in duplicates.items():
            print(f"FAIL: exact duplicated runtime rule at {', '.join(paths)}: {text}")
        return 1
    print(f"PASS: no exact duplicated normative rules across {len(RUNTIME_FILES)} runtime files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
