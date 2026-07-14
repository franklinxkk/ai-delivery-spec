#!/usr/bin/env python3
"""Validate requirement-management completeness of a PRD by assurance level."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


LEVELS = {
    "L0": ["goal", "scope", "acceptance"],
    "L1": ["goal", "intake", "scope", "role", "journey", "acceptance"],
    "L2": ["goal", "intake", "scope", "role", "journey", "flow", "view", "action", "state", "rule", "data", "exception", "permission", "acceptance", "trace", "change"],
    "L3": ["goal", "intake", "scope", "role", "journey", "flow", "view", "action", "state", "rule", "data", "exception", "permission", "audit", "integration", "acceptance", "trace", "change", "nfr"],
    "L4": ["goal", "intake", "scope", "role", "journey", "flow", "view", "action", "state", "rule", "data", "exception", "permission", "audit", "authority", "integration", "acceptance", "trace", "change", "nfr", "evidence", "human_accountability"],
}
TERMS = {
    "goal": ["目标", "goal"], "intake": ["准入", "intake", "req id"],
    "scope": ["范围", "scope"], "role": ["角色", "role"],
    "journey": ["角色旅程", "用户旅程", "journey"], "flow": ["流程", "flow", "路径"],
    "view": ["页面", "view"], "action": ["动作", "action", "操作", "act-"],
    "state": ["状态", "state"], "rule": ["规则", "rule-"],
    "data": ["数据", "字段", "field"], "exception": ["异常", "exception", "失败"],
    "permission": ["权限", "permission", "数据范围"], "audit": ["审计", "audit"],
    "authority": ["依据", "authority", "来源优先"], "integration": ["接口", "integration", "api"],
    "acceptance": ["验收", "acceptance", "ac-"], "trace": ["双向追溯", "traceability", "反向索引"],
    "change": ["变更入口", "变更记录", "chg-"], "nfr": ["非功能", "nfr", "性能"],
    "evidence": ["证据", "evidence"], "human_accountability": ["人工确认", "责任人", "human gate"],
}


def plugin_terms(path: Path | None) -> list[str]:
    if not path:
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("validators", {}).get("prd", {}).get("required_terms", [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--level", choices=LEVELS, default="L2")
    parser.add_argument("--domain-rules", type=Path)
    args = parser.parse_args()
    text = args.document.read_text(encoding="utf-8").lower()
    failures = []
    for key in LEVELS[args.level]:
        if not any(term in text for term in TERMS[key]):
            failures.append(f"missing {key} requirement contract")
    for term in plugin_terms(args.domain_rules):
        if term.lower() not in text:
            failures.append(f"missing domain term: {term}")
    if args.level in {"L2", "L3", "L4"}:
        for pattern, label in [
            (r"req-[a-z0-9-]+", "stable REQ IDs"), (r"role-[a-z0-9-]+", "stable ROLE IDs"),
            (r"flow-[a-z0-9-]+", "stable FLOW IDs"), (r"(?:view|page)-[a-z0-9-]+", "stable VIEW/PAGE IDs"),
            (r"act-[a-z0-9-]+", "stable ACT IDs"), (r"ac-[a-z0-9-]+", "stable AC IDs"),
        ]:
            if not re.search(pattern, text):
                failures.append(f"missing {label}")
    if failures:
        print("FAIL: " + "; ".join(failures))
        return 1
    print(f"PASS: PRD satisfies {args.level} v5.1.0 requirement-quality contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
