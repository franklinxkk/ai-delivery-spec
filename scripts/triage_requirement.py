#!/usr/bin/env python3
"""Deterministically recommend requirement intake decision, priority, mode and tier."""

from __future__ import annotations

import argparse
import json
import re
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


def document_language(doc: dict[str, Any]) -> str:
    explicit = str(doc.get("document_language", "")).strip()
    if explicit:
        return explicit
    sample = " ".join(str(doc.get(key, "")) for key in ("title", "outcome"))
    return "zh-CN" if re.search(r"[\u4e00-\u9fff]", sample) else "en"


def recommend(doc: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    language = document_language(doc)
    zh = language.lower().startswith("zh")
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
    states = size(doc.get("states"))
    handoffs = size(doc.get("cross_role_handoffs"))
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
    for key in ("data_submission", "data_reporting", "metric_caliber", "batch_io", "approval", "audit_required", "irreversible_write", "version_compatibility"):
        if doc.get(key):
            dimensions.append(key)
    if states > 3:
        dimensions.append("material_state")
    if handoffs:
        dimensions.append("cross_role_handoff")

    if doc.get("out_of_product_boundary") or doc.get("duplicate_of"):
        decision = "reject"
        reasons.append("需求超出产品边界或已被现有需求覆盖" if zh else "The request is outside the product boundary or duplicates an existing requirement")
    elif doc.get("blocked_dependency") or (doc.get("value") == "low" and not doc.get("urgent")):
        decision = "defer"
        reasons.append("依赖未解除或当前价值不足以进入本期设计" if zh else "A dependency is blocked or current value does not justify this iteration")
    elif missing or doc.get("ambiguity") == "high":
        decision = "clarify"
        prefix = "缺少会改变范围或结果的准入信息: " if zh else "Missing intake facts that can change scope or outcome: "
        reasons.append(prefix + ", ".join(sorted(set(missing))))
    else:
        decision = "accept"
        reasons.append("目标、责任人与价值证据足以进入需求设计" if zh else "Outcome, owner and value evidence are sufficient to enter specification")

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
    unified_triggers = {
        "multi_role", "multi_module", "integration", "cross_module_state",
        "data_submission", "data_reporting", "metric_caliber", "batch_io",
        "approval", "audit_required", "irreversible_write", "version_compatibility",
        "material_state", "cross_role_handoff", "migration", "compliance", "sensitive_data",
    }
    if ultra:
        delivery_shape = "requirement_card"
    elif governed_trigger:
        delivery_shape = "governed_truth"
    elif unified_triggers.intersection(dimensions):
        delivery_shape = "unified_prd"
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

    facets = []
    if doc.get("ui", True):
        facets.append("ui")
    if states or doc.get("cross_module_state"):
        facets.append("stateful")
    if any(doc.get(key) for key in ("data_submission", "data_reporting", "metric_caliber")):
        facets.append("data_submission")
    if integrations:
        facets.append("integration")
    if doc.get("batch_io"):
        facets.append("batch_io")
    if assurance_profile in {"high_risk", "safety_critical"}:
        facets.append("high_risk")

    return {
        "schema_version": "5.3.0",
        "document_language": language,
        "decision": decision,
        "priority": priority,
        "complexity": {"band": band, "dimensions": sorted(set(dimensions))},
        "uncertainty": "high" if missing or doc.get("ambiguity") == "high" else doc.get("ambiguity", "low"),
        "recommended_mode": mode,
        "recommended_tier": tier,
        "delivery_shape": delivery_shape,
        "assurance_profile": assurance_profile,
        "routing_signals": coupling_signals,
        "activated_facets": facets,
        "missing_for_intake": sorted(set(missing)),
        "reasons": reasons,
        "estimate_boundary": (
            "当前只判断复杂度；工期/成本由有权工程负责人确认"
            if zh else "Complexity band only; effort and cost require accountable engineering confirmation"
        ),
    }


def render_markdown(result: dict[str, Any]) -> str:
    zh = str(result.get("document_language", "")).lower().startswith("zh")
    if zh:
        return (
            "# 需求准入与分诊建议\n\n"
            f"- 准入结论：`{result['decision']}`\n"
            f"- 优先级：`{result['priority']}`\n"
            f"- 复杂度：`{result['complexity']['band']}`（{', '.join(result['complexity']['dimensions']) or '边界内'}）\n"
            f"- 不确定性：`{result['uncertainty']}`\n"
            f"- 模式/等级：`{result['recommended_mode']} / {result['recommended_tier']}`\n"
            f"- 交付形态/保证强度：`{result['delivery_shape']} / {result['assurance_profile']}`\n"
            f"- 激活规格：`{', '.join(result['activated_facets']) or '无'} `\n"
            f"- 待补信息：`{', '.join(result['missing_for_intake']) or '无'}`\n\n"
            + "".join(f"- 判断依据：{item}\n" for item in result["reasons"])
            + "- 估算边界：当前只判断复杂度；工期/成本由有权工程负责人确认。\n"
        )
    return (
        "# Requirement Intake And Triage Recommendation\n\n"
        f"- Decision: `{result['decision']}`\n- Priority: `{result['priority']}`\n"
        f"- Complexity: `{result['complexity']['band']}` ({', '.join(result['complexity']['dimensions']) or 'bounded'})\n"
        f"- Uncertainty: `{result['uncertainty']}`\n"
        f"- Mode/Tier: `{result['recommended_mode']} / {result['recommended_tier']}`\n"
        f"- Delivery/Assurance: `{result['delivery_shape']} / {result['assurance_profile']}`\n"
        f"- Activated facets: `{', '.join(result['activated_facets']) or 'none'}`\n"
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
