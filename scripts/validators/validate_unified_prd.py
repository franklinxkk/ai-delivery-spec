#!/usr/bin/env python3
"""Check that one PRD remains readable to humans while retaining engineering annexes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MAIN_MARKERS = ("背景", "需求准入", "角色", "角色旅程", "业务流程", "功能总览", "分模块功能需求", "验收方案")
ANNEX_MARKERS = ("字段字典", "规则与状态机", "api", "机器可读验收", "双向追溯", "禁止推断")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    raw = args.document.read_text(encoding="utf-8")
    lowered = raw.lower()
    failures = []
    h1 = re.findall(r"(?m)^#\s+[^#\n]", raw)
    if len(h1) != 1:
        failures.append(f"unified PRD must have exactly one H1 title, got {len(h1)}")
    for marker in MAIN_MARKERS:
        if marker.lower() not in lowered:
            failures.append(f"human reading path misses {marker}")
    for marker in ANNEX_MARKERS:
        if marker.lower() not in lowered:
            failures.append(f"engineering annex misses {marker}")
    appendix_pos = min((lowered.find(term) for term in ("第四部分", "附录 a", "工程与 ai coding 附录") if lowered.find(term) >= 0), default=-1)
    journey_pos = lowered.find("角色旅程")
    if appendix_pos < 0 or journey_pos < 0 or appendix_pos <= journey_pos:
        failures.append("engineering annex must follow the human role-journey and module reading path")
    main = raw[:appendix_pos] if appendix_pos >= 0 else raw
    nonblank = [line for line in main.splitlines() if line.strip()]
    table_lines = [line for line in nonblank if line.lstrip().startswith("|")]
    if nonblank and len(table_lines) / len(nonblank) > 0.55:
        failures.append("human main body is table-dominated; add readable journey/rule explanations")
    if not re.search(r"\bREQ-[A-Z0-9-]+\b", raw, re.I):
        failures.append("unified baseline has no REQ stable ID")
    requirement_ids = set(re.findall(r"\bREQ-[A-Z0-9-]+\b", raw, re.I))
    trace_pos = lowered.rfind("双向追溯")
    trace_text = raw[trace_pos:] if trace_pos >= 0 else ""
    missing_trace = sorted(requirement_ids - set(re.findall(r"\bREQ-[A-Z0-9-]+\b", trace_text, re.I)))
    if missing_trace:
        failures.append("requirements missing from trace annex: " + ", ".join(missing_trace))
    if trace_text and (not re.search(r"\bAC-[A-Z0-9-]+\b", trace_text, re.I) or "反向" not in trace_text):
        failures.append("trace annex must bind acceptance IDs and declare reverse lookup")
    if "两套 prd" not in lowered and "一份" not in lowered:
        failures.append("document does not declare one-baseline semantics")
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print("PASS: unified PRD has one human-first reading path and precise engineering annexes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
