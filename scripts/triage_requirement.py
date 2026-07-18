#!/usr/bin/env python3
"""Deterministically recommend requirement intake decision, priority, mode and tier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


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
    ai_behavior = bool(doc.get("ai_behavior"))
    ai_centrality = str(doc.get("ai_centrality", "unknown")).lower()
    ai_write_scope = str(doc.get("ai_write_scope", "unknown")).lower()
    ai_high_risk = ai_behavior and not (
        ai_centrality in {"incidental", "supporting"}
        and ai_write_scope in {"none", "read_only", "draft_only"}
        and doc.get("ai_reversible") is True
        and doc.get("ai_human_gate") is True
    )
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
    elif doc.get("compliance") or doc.get("migration") or ai_high_risk:
        mode, tier = "full", "L3"
    elif roles >= 8 or modules >= 12 or band == "XL":
        mode, tier = "full", "L3"
    else:
        mode, tier = "standard", "L2"

    if doc.get("safety_critical") or doc.get("clinical"):
        mode, tier = "full", "L4"

    if doc.get("safety_critical") or doc.get("clinical"):
        assurance_profile = "safety_critical"
    elif any(doc.get(key) for key in ("compliance", "money", "sensitive_data", "tenant_isolation", "migration")) or ai_high_risk:
        assurance_profile = "high_risk"
    elif ultra:
        assurance_profile = "bounded"
    else:
        assurance_profile = "standard"

    cross_edges = size(doc.get("cross_module_edges"))
    crosscut = size(doc.get("cross_cutting_policies"))
    controlled_projections = size(doc.get("controlled_projections"))
    coupling_signals = {
        "cross_module_edges": cross_edges,
        "cross_cutting_policies": crosscut,
        "controlled_projections": controlled_projections,
        "data_lineage": bool(doc.get("data_lineage")),
        "frequent_change": str(doc.get("change_frequency", "")).lower() in {"high", "frequent"},
        "strong_audit": bool(doc.get("strong_audit") or doc.get("audit_required")),
    }
    governed_trigger = (
        controlled_projections >= 3
        or (cross_edges >= 3 and (crosscut >= 1 or coupling_signals["frequent_change"]))
        or bool(coupling_signals["data_lineage"] and coupling_signals["strong_audit"])
        or bool(doc.get("governed_truth_requested"))
    )
    if ultra:
        delivery_shape = "requirement_card"
    elif governed_trigger:
        delivery_shape = "governed_truth"
    else:
        delivery_shape = "unified_prd"

    override_shape = str(doc.get("delivery_shape", "")).lower()
    if override_shape in {"requirement_card", "unified_prd", "governed_truth"}:
        delivery_shape = override_shape

    if doc.get("safety_critical") or doc.get("contract_deadline") or doc.get("regulatory_deadline"):
        priority = "P0"
    elif doc.get("urgent") or doc.get("value") == "high":
        priority = "P1"
    elif doc.get("value") == "low":
        priority = "P3"
    else:
        priority = "P2"

    return {
        "schema_version": "5.3.0",
        "decision": decision,
        "priority": priority,
        "complexity": {"band": band, "dimensions": sorted(set(dimensions))},
        "uncertainty": "high" if missing or doc.get("ambiguity") == "high" else doc.get("ambiguity", "low"),
        "recommended_mode": mode,
        "recommended_tier": tier,
        "delivery_shape": delivery_shape,
        "assurance_profile": assurance_profile,
        "routing_signals": coupling_signals,
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
        f"- Delivery/Assurance: `{result['delivery_shape']} / {result['assurance_profile']}`\n"
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
