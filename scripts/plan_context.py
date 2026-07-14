#!/usr/bin/env python3
"""Create a deterministic context and assurance plan from Product Truth."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from validators.validate_spec_config import validate as validate_config


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "examples/spec.config.example.yaml"

STAGE_REFERENCES = {
    "intake": ["references/requirement-management.md"],
    "clarify": ["references/discover.md", "references/runtime/schema-grill.md"],
    "review": ["references/specify.md", "references/runtime/verify.md"],
    "baseline": ["references/handoff.md"],
    "change": ["references/runtime/change.md"],
    "acceptance": ["references/runtime/verify.md"],
    "closed": ["references/requirement-management.md"],
    "discover": ["references/discover.md"],
    "specify": ["references/specify.md"],
    "plan": ["references/handoff.md"],
    "tasks": ["references/handoff.md"],
    "build_verify": ["references/runtime/verify.md"],
    "launch": ["references/runtime/verify.md"],
    "learn_retire": ["references/requirement-management.md"],
}

DOMAIN_FILES = {
    "traffic": "references/domains/domain-traffic.md",
    "crm": "references/domains/domain-crm.md",
    "education-it": "references/domains/domain-education-it.md",
    "oa": "references/domains/domain-oa.md",
    "medical-hospital-it": "references/domains/domain-medical-hospital-it.md",
    "data-product": "references/domains/domain-data-mart.md",
    "ai-native": "references/domains/domain-ai-native.md",
}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def estimate_tokens(document: dict[str, Any]) -> int:
    text = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
    ascii_chars = sum(ord(char) < 128 for char in text)
    non_ascii = len(text) - ascii_chars
    return max(1, math.ceil(ascii_chars / 4 + non_ascii / 1.5))


def estimate_text_tokens(text: str) -> int:
    ascii_chars = sum(ord(char) < 128 for char in text)
    non_ascii = len(text) - ascii_chars
    return max(1, math.ceil(ascii_chars / 4 + non_ascii / 1.5))


def classify(truth: dict[str, Any]) -> tuple[int, list[str], str, list[str]]:
    context = truth.get("delivery_context", {})
    score = 0
    signals: list[str] = []

    counts = {
        "requirements": len(truth.get("requirements", [])),
        "modules": len(truth.get("modules", [])),
        "roles": len(truth.get("roles", [])),
        "flows": len(truth.get("flows", [])),
        "actions": len(truth.get("actions", [])),
        "integrations": len(truth.get("integrations", [])),
        "unknowns": len([item for item in truth.get("unknowns", []) if item.get("status") == "open"]),
        "conflicts": len([item for item in truth.get("conflicts", []) if item.get("status") == "open"]),
    }
    score += max(0, counts["requirements"] - 3)
    score += max(0, counts["modules"] - 1) * 2
    score += max(0, counts["roles"] - 2)
    score += max(0, counts["flows"] - 1) * 2
    score += max(0, counts["actions"] - 5) // 3
    score += counts["integrations"] * 2 + counts["unknowns"] + counts["conflicts"] * 2

    if context.get("project_shape") in {"brownfield", "hybrid"}:
        score += 4
        signals.append("migration")
    if context.get("delivery_mode") == "full":
        score += 3
    if context.get("tier") in {"L3", "L4"}:
        score += 8
        signals.append("high_consequence")

    profiles = {str(item).lower() for item in context.get("governance_profiles", [])}
    for profile in ("regulated", "tog", "multi-tenant", "tenant_isolation"):
        if profile in profiles:
            score += 6 if profile == "regulated" else 3
            signals.append("tenant_isolation" if "tenant" in profile else profile)

    source_kinds = {item.get("kind") for item in truth.get("sources", [])}
    if source_kinds & {"law", "regulation", "standard"}:
        score += 6
        signals.append("regulated")

    if any(item.get("sensitivity") == "restricted" for item in truth.get("fields", [])):
        score += 5
        signals.append("privacy")
    if "ai-native" in context.get("domain_packs", []):
        score += 4
        signals.append("ai_writeback")

    signals = list(dict.fromkeys(signals))
    regulated = bool({"regulated", "privacy", "high_consequence"} & set(signals))
    if regulated:
        assurance = "regulated"
    elif score >= 24:
        assurance = "complex"
    elif score >= 8:
        assurance = "standard"
    else:
        assurance = "minimal"

    gates = ["intake", "clarification", "specification", "traceability", "acceptance"]
    if context.get("consumers") and "coding_agent" in context.get("consumers", []):
        gates.append("unified_prd_handoff")
    if context.get("project_shape") in {"brownfield", "hybrid"}:
        gates.append("change_impact")
    if assurance == "regulated":
        gates.extend(["authority_applicability", "human_accountability", "rollback"])
    return score, signals, assurance, list(dict.fromkeys(gates))


def build_plan(truth: dict[str, Any], config: dict[str, Any], seed_ids: list[str]) -> dict[str, Any]:
    score, signals, assurance, gates = classify(truth)
    configured_profile = config["context"]["profile"]
    if assurance == "regulated":
        inferred_profile = "regulated"
    elif score >= 28:
        inferred_profile = "large_program"
    elif score >= 8:
        inferred_profile = "standard"
    else:
        inferred_profile = "minimal"
    profile_rank = {"minimal": 0, "standard": 1, "large_program": 2, "regulated": 3}
    if configured_profile == "auto":
        profile = inferred_profile
    else:
        profile = max((inferred_profile, configured_profile), key=profile_rank.get)

    manual_assurance = config["assurance"].get("manual_profile", "auto")
    if manual_assurance != "auto":
        assurance_rank = {"minimal": 0, "standard": 1, "complex": 2, "regulated": 3}
        assurance = max((assurance, manual_assurance), key=assurance_rank.get)

    configured_model_tokens = config["context"].get("model_context_tokens")
    model_tokens = configured_model_tokens or 32768
    overhead = config["context"].get("system_overhead_tokens", 4096)
    output = config["context"].get("reserved_output_tokens", 4096)
    working = max(0, model_tokens - overhead - output)
    truth_tokens = estimate_tokens(truth)

    lifecycle = truth.get("delivery_context", {}).get("lifecycle_stage", "discover")
    stage_refs_all = list(STAGE_REFERENCES.get(lifecycle, ["references/discover.md"]))
    if truth.get("delivery_context", {}).get("domain_packs") or truth.get("delivery_context", {}).get("governance_profiles"):
        stage_refs_all.append("references/runtime/composition.md")
    if assurance == "regulated" and "references/runtime/verify.md" not in stage_refs_all:
        stage_refs_all.append("references/runtime/verify.md")
    max_refs = config["context"].get("max_stage_references", 3)
    stage_refs_all = list(dict.fromkeys(stage_refs_all))
    stage_refs = stage_refs_all[:max_refs]
    deferred_stage_refs = stage_refs_all[max_refs:]

    domain_ids = truth.get("delivery_context", {}).get("domain_packs", [])
    domain_files_all = [DOMAIN_FILES[item] for item in domain_ids if item in DOMAIN_FILES]
    unresolved_domain_ids = [item for item in domain_ids if item not in DOMAIN_FILES]
    max_domains = config["context"].get("max_domain_packs", 2)
    domain_files = domain_files_all[:max_domains]
    deferred_domain_files = domain_files_all[max_domains:]

    selected_runtime_files = ["SKILL.md", *stage_refs, *domain_files]
    reference_tokens = sum(
        estimate_text_tokens((ROOT / relative).read_text(encoding="utf-8"))
        for relative in selected_runtime_files
        if (ROOT / relative).exists()
    )
    total_selected_tokens = truth_tokens + reference_tokens

    item_count = sum(len(truth.get(key, [])) for key in (
        "sources", "requirements", "roles", "modules", "entities", "fields", "flows", "views",
        "actions", "states", "rules", "events", "integrations", "acceptance",
    ))
    max_items = config["context"].get("max_truth_items", 160)
    hard_limit_exceeded = total_selected_tokens > working
    warn_ratio = config["context"].get("warn_at_ratio", 0.8)
    overflow = (
        total_selected_tokens > working * warn_ratio
        or item_count > max_items
        or bool(deferred_stage_refs)
        or bool(deferred_domain_files)
        or bool(unresolved_domain_ids)
    )
    if not overflow:
        truth_strategy = "full"
    elif seed_ids:
        truth_strategy = "id_slice"
    elif len(truth.get("modules", [])) > 1:
        truth_strategy = "module_slice"
    else:
        truth_strategy = "split_delivery"
    overflow_strategy = config["context"].get("overflow_strategy", "retrieve")
    required_action = "none"
    if overflow:
        required_action = {
            "retrieve": "retrieve_stable_id_slice",
            "summarize": "write_compaction_manifest",
            "split": "split_delivery",
            "block": "block",
        }[overflow_strategy]

    plan = {
        "schema_version": "5.0.0",
        "profile": profile,
        "assurance_profile": assurance,
        "complexity_score": score,
        "risk_signals": signals,
        "budget": {
            "model_context_tokens": model_tokens,
            "model_context_source": "project_config" if configured_model_tokens else "default_assumption",
            "system_overhead_tokens": overhead,
            "reserved_output_tokens": output,
            "working_tokens": working,
            "estimated_truth_tokens": truth_tokens,
            "estimated_reference_tokens": reference_tokens,
            "estimated_total_selected_tokens": total_selected_tokens,
        },
        "selection": {
            "stage_references": stage_refs,
            "deferred_stage_references": deferred_stage_refs,
            "domain_packs": domain_files,
            "deferred_domain_packs": deferred_domain_files,
            "unresolved_domain_packs": unresolved_domain_ids,
            "truth_strategy": truth_strategy,
            "seed_ids": seed_ids,
        },
        "overflow": {
            "triggered": overflow,
            "hard_limit_exceeded": hard_limit_exceeded,
            "strategy": overflow_strategy,
            "required_action": required_action,
            "compaction_manifest_required": overflow and overflow_strategy == "summarize",
            "preserved_priorities": config["context"]["never_truncate_priorities"],
            "silent_truncation_allowed": False,
            "reason": (
                f"selected estimate={total_selected_tokens} tokens/items={item_count}, working={working}, "
                f"warn_at={warn_ratio}/max_items={max_items}, "
                f"deferred_refs={len(deferred_stage_refs)}, deferred_domains={len(deferred_domain_files)}, "
                f"unresolved_domains={len(unresolved_domain_ids)}"
                if overflow else "Selected runtime references and Product Truth fit configured working budget"
            ),
        },
        "required_gates": gates,
        "claim_boundary": (
            "Project complexity selects retrieval and assurance gates only; it does not change domain-pack maturity."
        ),
    }
    return plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--seed-id", action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    truth = load_yaml(args.truth)
    config = load_yaml(args.config)
    config_failures = validate_config(config)
    if config_failures:
        for item in config_failures:
            print(f"FAIL: config {item}")
        return 1
    plan = build_plan(truth, config, args.seed_id)
    schema = json.loads((ROOT / "schemas/context-plan.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(plan))
    if errors:
        for error in errors:
            print(f"FAIL: {'.'.join(str(part) for part in error.path)}: {error.message}")
        return 1
    rendered = yaml.safe_dump(plan, allow_unicode=True, sort_keys=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"PASS: wrote context plan to {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
