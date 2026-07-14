#!/usr/bin/env python3
"""Validate the engineering annex inside one unified requirement PRD."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


BASE_AREAS = {
    "source precedence, intake and scope": ("来源优先", "source-of-truth", "准入结论", "intake decision"),
    "requirement baseline and change entry": ("req id", "req-*", "需求准入", "变更入口", "chg-"),
    "roles, permission and data scope": ("数据范围", "权限", "data scope", "角色"),
    "role journeys and flow closure": ("角色旅程", "端到端", "flow-", "跨角色"),
    "IA, page and region layout": ("信息架构", "页面与布局", "page layout", "view contract"),
    "fields and data flow": ("全局字段字典", "字段字典", "field dictionary", "数据流转"),
    "states, rules and recovery": ("状态机", "规则与状态机", "异常与边界", "failure / recovery"),
    "API/integration business contract": ("api、事件与集成", "请求字段", "request fields", "集成业务契约"),
    "security, privacy and NFR": ("非功能与合规", "nfr", "安全", "隐私"),
    "machine-readable acceptance": ("机器可读验收", "ac_structured", "evidence_required"),
    "bidirectional traceability": ("双向追溯", "反向索引", "traceability"),
    "forbidden invention": ("禁止推断", "禁止发明", "forbidden invention"),
}

SLICE_AREAS = {key: BASE_AREAS[key] for key in (
    "source precedence, intake and scope", "requirement baseline and change entry",
    "roles, permission and data scope", "role journeys and flow closure",
    "IA, page and region layout", "fields and data flow", "states, rules and recovery",
    "machine-readable acceptance", "bidirectional traceability", "forbidden invention",
)}

L3_AREAS = {
    "AI runtime contract": ("ai runtime", "模型契约", "prompt version", "tool policy"),
    "AI evaluation and human accountability": ("评测契约", "evaluation contract", "human gate", "人工兜底"),
}

ID_RULES = {
    "REQ IDs": r"\bREQ-[A-Z0-9-]+\b",
    "ROLE IDs": r"\bROLE-[A-Z0-9-]+\b",
    "module IDs": r"\bMOD-[A-Z0-9-]+\b",
    "flow IDs": r"\bFLOW-[A-Z0-9-]+\b",
    "view/page IDs": r"\b(?:VIEW|PAGE)-[A-Z0-9-]+\b",
    "action IDs": r"\bACT-[A-Z0-9-]+\b",
    "field IDs": r"\bFLD-[A-Z0-9-]+\b",
    "state machine IDs": r"\b(?:SM|STM|STATE)-[A-Z0-9-]+\b",
    "acceptance IDs": r"\bAC-[A-Z0-9-]+\b",
}

STRUCTURED_AC_FIELDS = (
    ("preconditions", "前置条件"), ("steps", "步骤"),
    ("expected_visible", "预期可见结果", "可见结果"),
    ("expected_domain", "预期领域结果", "业务结果"),
    ("evidence_required", "证据"),
)


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term.lower() in text for term in terms)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--level", choices=["L0", "L1", "L2", "L3", "L4"], default="L2")
    parser.add_argument("--profile", choices=["full_prd", "slice"], default="full_prd")
    parser.add_argument("--domain-rules", type=Path)
    args = parser.parse_args()
    raw = args.document.read_text(encoding="utf-8")
    text = raw.lower()
    failures: list[str] = []

    if args.level in {"L0", "L1"}:
        required = {"goal": ("目标", "goal"), "scope": ("范围", "scope"), "acceptance": ("验收", "ac-")}
    else:
        required = dict(BASE_AREAS if args.profile == "full_prd" else SLICE_AREAS)
        if args.level in {"L3", "L4"} and has_any(text, ("ai runtime", "模型", "智能体", "大模型")):
            required.update(L3_AREAS)
    for area, terms in required.items():
        if not has_any(text, terms):
            failures.append(f"missing contract area: {area}")

    if args.level in {"L2", "L3", "L4"}:
        heading_count = len(re.findall(r"(?m)^#{2,4}\s+\S", raw))
        table_rows = len(re.findall(r"(?m)^\s*\|(?:[^\n|]+\|){2,}\s*$", raw))
        if args.profile == "full_prd" and heading_count < 14:
            failures.append(f"full unified PRD has only {heading_count} section headings; need at least 14")
        if table_rows < 8:
            failures.append(f"contract has only {table_rows} table rows; precise mappings are missing")
        for label, pattern in ID_RULES.items():
            if not re.search(pattern, raw, flags=re.IGNORECASE):
                failures.append(f"missing stable {label}")
        for terms in STRUCTURED_AC_FIELDS:
            if not has_any(text, terms):
                failures.append(f"structured acceptance misses {terms[0]}")
        api_not_applicable = bool(re.search(r"(?:api|接口)[^\n]{0,80}(?:不适用|not applicable)", text))
        if not api_not_applicable:
            if not re.search(r"/(?:api|openapi)/|\b(?:get|post|put|patch|delete)\s+[`/]", text):
                failures.append("applicable API contract has no concrete method/path or explicit engineering-owned path decision")
            for label, terms in {
                "request fields/body": ("request fields", "请求字段", "request body"),
                "response fields/body": ("response fields", "成功响应", "response body", "统一响应"),
                "error/idempotency": ("错误码", "业务错误", "error code", "幂等", "idempotency"),
            }.items():
                if not has_any(text, terms):
                    failures.append(f"API contract misses {label}")
        if not has_any(text, ("异常", "失败", "failure")):
            failures.append("contract misses failure behavior")

    if args.domain_rules:
        rules = yaml.safe_load(args.domain_rules.read_text(encoding="utf-8")) or {}
        for term in rules.get("validators", {}).get("coding_agent", {}).get("required_terms", []):
            if term.lower() not in text:
                failures.append(f"missing domain term: {term}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: unified PRD engineering annex satisfies {args.level} v5.1.0 requirement contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
