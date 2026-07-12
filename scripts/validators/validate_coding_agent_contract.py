#!/usr/bin/env python3
"""Validate structural AI Coding contracts instead of accepting keyword soup."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


BASE_AREAS = {
    "source order and scope": ("source-of-truth", "事实源", "generated_from", "优先级"),
    "repository baseline": ("repository baseline", "仓库基线", "技术栈", "目录结构"),
    "roles, permission and data scope": ("data scope", "数据范围", "权限矩阵", "角色与权限"),
    "IA, page and region layout": ("信息架构", "页面契约", "view contract", "页面布局", "page layout"),
    "flows, states and recovery": ("状态机", "state transition", "state machine", "异常恢复", "failure / retry"),
    "field dictionary": ("字段字典", "field dictionary", "field id"),
    "API request and response schema": ("request/response", "request schema", "请求 schema", "统一响应"),
    "error, idempotency and conflict": ("错误码", "error code", "idempotency", "幂等"),
    "events, integrations and reconciliation": ("事件契约", "event payload", "集成契约", "reconciliation"),
    "security, privacy and NFR": ("非功能", "nfr", "安全、隐私", "security and privacy"),
    "vertical slices, files and dependencies": ("likely files", "切片依赖", "vertical delivery", "垂直开发切片"),
    "machine-readable acceptance": ("机器可读验收", "structured acceptance", "ac_structured", "evidence_required"),
    "forbidden invention and unresolved decisions": ("禁止发明", "forbidden invention", "unknown", "未决"),
    "deployment, migration, rollback and operations": ("部署、迁移", "migration", "rollback", "运维"),
    "metrics and calculation caliber": ("统计口径", "calculation caliber", "指标口径", "metrics", "计算方式"),
}

SLICE_AREAS = {
    key: BASE_AREAS[key]
    for key in (
        "source order and scope", "repository baseline", "roles, permission and data scope",
        "IA, page and region layout", "flows, states and recovery", "field dictionary",
        "API request and response schema", "vertical slices, files and dependencies",
        "machine-readable acceptance", "forbidden invention and unresolved decisions",
    )
}

L3_AREAS = {
    "AI runtime contract": ("ai runtime", "模型契约", "prompt version", "tool policy"),
    "AI evaluation and human accountability": ("evaluation contract", "评测契约", "human gate", "人工兜底"),
}

ID_RULES = {
    "ROLE IDs": r"\bROLE-[A-Z0-9-]+\b",
    "module IDs": r"\bMOD-[A-Z0-9-]+\b",
    "flow IDs": r"\bFLOW-[A-Z0-9-]+\b",
    "view/page IDs": r"\b(?:VIEW|PAGE)-[A-Z0-9-]+\b",
    "action IDs": r"\bACT-[A-Z0-9-]+\b",
    "field IDs": r"\bFLD-[A-Z0-9-]+\b",
    "state machine IDs": r"\b(?:SM|STATE)-[A-Z0-9-]+\b",
    "acceptance IDs": r"\bAC-[A-Z0-9-]+\b",
}

STRUCTURED_AC_FIELDS = (
    ("preconditions", "前置条件"),
    ("steps", "步骤"),
    ("expected_visible", "可见结果"),
    ("expected_domain", "业务结果"),
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
        required = {
            "source": ("source", "事实源"),
            "task": ("task", "任务"),
            "test": ("test", "验收", "ac-"),
        }
    else:
        required = dict(BASE_AREAS if args.profile == "full_prd" else SLICE_AREAS)
        if args.level in {"L3", "L4"}:
            required.update(L3_AREAS)

    for area, terms in required.items():
        if not has_any(text, terms):
            failures.append(f"missing contract area: {area}")

    if args.level in {"L2", "L3", "L4"}:
        heading_count = len(re.findall(r"(?m)^#{2,4}\s+\S", raw))
        table_count = len(re.findall(r"(?m)^\s*\|(?:[^\n|]+\|){2,}\s*$", raw))
        if args.profile == "full_prd" and heading_count < 12:
            failures.append(f"full PRD has only {heading_count} section headings; need at least 12")
        if table_count < 5:
            failures.append(f"contract has only {table_count} table rows; executable mappings are missing")
        for label, pattern in ID_RULES.items():
            if not re.search(pattern, raw, flags=re.IGNORECASE):
                failures.append(f"missing stable {label}")
        for terms in STRUCTURED_AC_FIELDS:
            if not has_any(text, terms):
                failures.append(f"structured acceptance misses {terms[0]}")
        if not re.search(r"/(?:api|openapi)/|\b(?:get|post|put|patch|delete)\s+[`/]", text):
            failures.append("API contract has no concrete method/path")
        if not re.search(r"(?:err|error|错误)[-_a-z0-9]{2,}|\b[45]\d\d\b", text):
            failures.append("error contract has no concrete error code/status")
        if not has_any(text, ("request fields", "请求字段", "request body")):
            failures.append("API contract misses request fields/body")
        if not has_any(text, ("response fields", "响应字段", "response body", "统一响应")):
            failures.append("API contract misses response fields/body")
        if not has_any(text, ("payload version", "payload 示例", "事件 payload", "event version")):
            failures.append("event contract misses versioned payload")
        if not has_any(text, ("failure", "失败", "异常")):
            failures.append("contract misses failure behavior")
        if not has_any(text, ("dependencies", "依赖")):
            failures.append("vertical slices miss dependencies")
        if not has_any(text, ("likely files", "可能文件", "涉及文件")):
            failures.append("vertical slices miss likely files/modules")

    if args.domain_rules:
        rules = yaml.safe_load(args.domain_rules.read_text(encoding="utf-8")) or {}
        for term in rules.get("validators", {}).get("coding_agent", {}).get("required_terms", []):
            if term.lower() not in text:
                failures.append(f"missing domain term: {term}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: AI Coding {args.profile} satisfies {args.level} v5.0.2 executable contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
