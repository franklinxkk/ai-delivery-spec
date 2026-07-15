#!/usr/bin/env python3
"""Regression tests for adaptive context planning and maturity separation."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from plan_context import build_plan
from query_product_truth import make_slice

TRUTH_PATH = ROOT / "maintainer/examples/publishing-learning-v5/delivery/truth/product-truth.yaml"
CONFIG_PATH = ROOT / "examples/spec.config.example.yaml"


def main() -> int:
    truth = yaml.safe_load(TRUTH_PATH.read_text(encoding="utf-8"))
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    standard = build_plan(truth, config, ["MOD-CONTENT-001"])
    if standard["profile"] == "minimal":
        failures.append("multi-module Publishing truth must not classify as minimal")
    if standard["overflow"]["silent_truncation_allowed"]:
        failures.append("context planning must never allow silent truncation")
    if "maturity" in standard or "domain_maturity" in standard:
        failures.append("context plan must not assign domain maturity fields")

    micro_truth = copy.deepcopy(truth)
    micro_truth["delivery_context"].update(
        {"tier": "L1", "delivery_mode": "lite", "project_shape": "greenfield", "governance_profiles": [], "domain_packs": []}
    )
    for collection in ("roles", "modules", "flows", "actions", "integrations", "unknowns", "conflicts"):
        micro_truth[collection] = micro_truth.get(collection, [])[:1]
    micro_truth["fields"] = []
    micro_truth["sources"] = micro_truth["sources"][:1]
    micro = build_plan(micro_truth, config, [])
    if micro["profile"] != "minimal" or len(micro["selection"]["stage_references"]) > 1:
        failures.append("bounded greenfield change should select the minimal context profile")

    regulated_truth = copy.deepcopy(truth)
    regulated_truth["delivery_context"]["tier"] = "L3"
    regulated_truth["delivery_context"]["governance_profiles"] = ["regulated", "multi-tenant"]
    regulated_truth["sources"].append(
        {
            "id": "SRC-REGULATION-TEST",
            "kind": "regulation",
            "title": "Test-only regulated source",
            "authority": "primary",
            "status": "active",
            "disposition": "authoritative_annex",
        }
    )
    regulated = build_plan(regulated_truth, config, [])
    if regulated["profile"] != "regulated" or regulated["assurance_profile"] != "regulated":
        failures.append("regulated structural signals must select regulated assurance")
    if "human_accountability" not in regulated["required_gates"]:
        failures.append("regulated assurance must require accountable human gate")
    downgrade_config = copy.deepcopy(config)
    downgrade_config["context"]["profile"] = "minimal"
    downgrade_config["assurance"]["manual_profile"] = "minimal"
    protected = build_plan(regulated_truth, downgrade_config, [])
    if protected["profile"] != "regulated" or protected["assurance_profile"] != "regulated":
        failures.append("project config must not downgrade structurally required regulated assurance")
    constrained_config = copy.deepcopy(config)
    constrained_config["context"]["max_stage_references"] = 0
    constrained_config["context"]["max_domain_packs"] = 0
    deferred = build_plan(regulated_truth, constrained_config, [])
    if not deferred["overflow"]["triggered"] or not deferred["selection"]["deferred_stage_references"]:
        failures.append("configured batch limits must defer and split required references, never drop them silently")

    stress_config = copy.deepcopy(config)
    stress_config["context"].update(
        {
            "model_context_tokens": 4096,
            "system_overhead_tokens": 512,
            "reserved_output_tokens": 512,
            "warn_at_ratio": 0.8,
            "overflow_strategy": "summarize",
        }
    )
    stress = build_plan(truth, stress_config, [])
    if not stress["overflow"]["triggered"]:
        failures.append("80% context pressure must trigger controlled compaction")
    if stress["overflow"]["required_action"] != "write_compaction_manifest":
        failures.append("summarize strategy must require a compaction manifest")
    if not stress["overflow"]["compaction_manifest_required"] or "P0" not in stress["overflow"]["preserved_priorities"]:
        failures.append("context compaction must preserve configured priorities and emit a manifest")

    working_slice = make_slice(truth, ["MOD-CONTENT-001"], include_reverse=False)
    slice_ids = {
        item["id"]
        for items in working_slice["items"].values()
        for item in items
        if isinstance(item, dict) and item.get("id")
    }
    if "MOD-CONTENT-001" not in slice_ids or "FLOW-PUBLISH-001" not in slice_ids:
        failures.append("module slice must include its forward flow closure")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(
        "PASS: context planning adapts to project structure, never silently truncates, "
        "and does not modify domain maturity"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
