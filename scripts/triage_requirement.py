#!/usr/bin/env python3
"""Deterministically recommend requirement intake decision, priority, mode and tier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("intake input must be a YAML/JSON object")
    return value


def size(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, int):
        return value
    return 0


def recommend(doc: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    missing = [key for key in ("title", "outcome", "owner") if not str(doc.get(key, "")).strip()]
    sources = doc.get("source_refs", [])
    value_evidence = doc.get("value_evidence", [])
    if not sources:
        missing.append("source_refs")
    if not value_evidence:
        missing.append("value_evidence")

    roles = size(doc.get("roles"))
    modules = size(doc.get("modules"))
    integrations = size(doc.get("integrations"))
    dimensions = []
    for key in ("cross_module_state", "sensitive_data", "compliance", "migration", "customer_acceptance", "ai_behavior"):
        if doc.get(key):
            dimensions.append(key)
    if roles > 1:
        dimensions.append("multi_role")
    if modules > 1:
        dimensions.append("multi_module")
    if integrations:
        dimensions.append("integration")

    if doc.get("out_of_product_boundary") or doc.get("duplicate_of"):
        decision = "reject"
        reasons.append("需求超出产品边界或已被现有需求覆盖")
    elif doc.get("blocked_dependency") or (doc.get("value") == "low" and not doc.get("urgent")):
        decision = "defer"
        reasons.append("依赖未解除或当前价值不足以进入本期设计")
    elif missing or doc.get("ambiguity") == "high":
        decision = "clarify"
        reasons.append("缺少会改变范围或结果的准入信息: " + ", ".join(sorted(set(missing))))
    else:
        decision = "accept"
        reasons.append("目标、责任人与价值证据足以进入需求设计")

    complexity_score = roles + modules * 2 + integrations * 2 + len(dimensions) * 2
    if complexity_score <= 3:
        band = "S"
    elif complexity_score <= 8:
        band = "M"
    elif complexity_score <= 16:
        band = "L"
    else:
        band = "XL"

    ultra = (
        doc.get("reversible") is True
        and roles <= 1
        and modules <= 1
        and not dimensions
        and not integrations
    )
    if ultra:
        mode, tier = "ultra_light", "L0"
    elif band == "S" and not doc.get("customer_acceptance"):
        mode, tier = "lite", "L1"
    elif doc.get("compliance") or doc.get("migration") or doc.get("ai_behavior"):
        mode, tier = "full", "L3"
    elif roles >= 8 or modules >= 12 or band == "XL":
        mode, tier = "full", "L3"
    else:
        mode, tier = "standard", "L2"

    if doc.get("safety_critical") or doc.get("clinical"):
        mode, tier = "full", "L4"

    if doc.get("safety_critical") or doc.get("contract_deadline") or doc.get("regulatory_deadline"):
        priority = "P0"
    elif doc.get("urgent") or doc.get("value") == "high":
        priority = "P1"
    elif doc.get("value") == "low":
        priority = "P3"
    else:
        priority = "P2"

    return {
        "schema_version": "5.1.0",
        "decision": decision,
        "priority": priority,
        "complexity": {"band": band, "dimensions": sorted(set(dimensions))},
        "uncertainty": "high" if missing or doc.get("ambiguity") == "high" else doc.get("ambiguity", "low"),
        "recommended_mode": mode,
        "recommended_tier": tier,
        "missing_for_intake": sorted(set(missing)),
        "reasons": reasons,
        "estimate_boundary": "complexity band only; engineering effort/cost requires accountable engineering confirmation",
    }


def render_markdown(result: dict[str, Any]) -> str:
    return (
        "# Requirement Intake Recommendation\n\n"
        f"- Decision: `{result['decision']}`\n"
        f"- Priority: `{result['priority']}`\n"
        f"- Complexity: `{result['complexity']['band']}` ({', '.join(result['complexity']['dimensions']) or 'bounded'})\n"
        f"- Uncertainty: `{result['uncertainty']}`\n"
        f"- Mode/Tier: `{result['recommended_mode']} / {result['recommended_tier']}`\n"
        f"- Missing: `{', '.join(result['missing_for_intake']) or 'none'}`\n\n"
        + "".join(f"- Rationale: {item}\n" for item in result["reasons"])
        + f"- Estimate boundary: {result['estimate_boundary']}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=["markdown", "yaml", "json"], default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = recommend(load(args.input))
    if args.format == "json":
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    elif args.format == "yaml":
        rendered = yaml.safe_dump(result, allow_unicode=True, sort_keys=False)
    else:
        rendered = render_markdown(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"PASS: wrote intake recommendation to {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
