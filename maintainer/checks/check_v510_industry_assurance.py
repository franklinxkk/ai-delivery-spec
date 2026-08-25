#!/usr/bin/env python3
"""Validate compact, risk-adaptive cross-domain release assurance."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
portfolio = yaml.safe_load(
    (ROOT / "maintainer/evals/industry-assurance-portfolio.yaml").read_text(encoding="utf-8")
)
reference = (ROOT / "maintainer/README.md").read_text(encoding="utf-8")
failures: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


claim = portfolio.get("claim_boundary", {})
require(claim.get("execution_status") == "contract_fixture", "portfolio must remain a contract fixture")
require(claim.get("simulated_review_is_expert_review") is False, "simulation cannot claim expert review")
require(claim.get("production_claim") == "prohibited", "production claim must be prohibited")

execution = portfolio.get("execution_model", {})
require(execution.get("runtime_prerequisite") is False, "assurance lab cannot become a runtime prerequisite")
comparison = execution.get("comparison", {})
require(comparison.get("preregistered") is True, "comparison must be preregistered")
require(comparison.get("same_model_permissions_context") is True, "comparison must control model and permissions")
require(comparison.get("repeated_runs_per_arm_scenario", 0) >= 3, "comparison needs repeated runs")
require(comparison.get("minimum_real_project_families", 0) >= 3, "comparison needs three real project families")
require(comparison.get("blind_scoring_before_unblind") is True, "scoring must be blind before unblinding")
require(len(comparison.get("required_metrics", [])) == 7, "comparison must retain seven decision metrics")

goalkeeper = portfolio.get("runtime_goalkeeper", {})
require(goalkeeper.get("llm_calls") == 0, "runtime gate must use zero LLM calls")
require(goalkeeper.get("subagent_calls") == 0, "runtime gate must use zero sub-agent calls")
require(goalkeeper.get("generates_or_fixes_requirements") is False, "runtime gate is not an author")
require(goalkeeper.get("artifact_parse_passes") == 1, "runtime gate should parse each artifact once")

lenses = portfolio.get("risk_lenses", {})
expected_lenses = {"business_product", "domain", "ux", "frontend", "backend", "qa", "compliance_safety"}
require(set(lenses) == expected_lenses, "risk lens set is incomplete")
for lens_id, lens in lenses.items():
    require(bool(lens.get("trigger")), f"{lens_id} needs an activation trigger")
    require(len(lens.get("must_answer", [])) >= 4, f"{lens_id} needs a bounded responsibility contract")

probes = portfolio.get("downstream_consumer_probes", {})
require(set(probes) == {"product", "frontend", "backend", "qa", "coding_agent"}, "consumer probes incomplete")
for probe_id, probe in probes.items():
    require(bool(probe.get("ready_when")), f"{probe_id} needs a readiness condition")
    require(bool(probe.get("forbidden")), f"{probe_id} needs a forbidden-invention boundary")

scenarios = portfolio.get("scenarios", [])
require(len(scenarios) >= 7, "portfolio needs seven distinct requirement-physics scenarios")
require(len({item.get("id") for item in scenarios}) == len(scenarios), "scenario IDs must be unique")
physics: set[str] = set()
for scenario in scenarios:
    scenario_id = scenario.get("id", "<missing>")
    scenario_lenses = set(scenario.get("required_lenses", []))
    scenario_physics = set(scenario.get("requirement_physics", []))
    physics.update(scenario_physics)
    require(3 <= len(scenario_lenses) < len(lenses), f"{scenario_id} must select, not exhaust, risk lenses")
    require(scenario_lenses <= set(lenses), f"{scenario_id} references an unknown lens")
    require(len(scenario_physics) >= 5, f"{scenario_id} requirement physics is too thin")
    require(bool(scenario.get("p0_seed")), f"{scenario_id} needs a P0 negative seed")
    require(bool(scenario.get("mutation_probe")), f"{scenario_id} needs a material change probe")
require(len(physics) >= 20, "requirement-physics diversity is too low")

require(len(portfolio.get("release_acceptance", [])) >= 5, "release acceptance is incomplete")
require("维护实验室发现" in reference, "maintainer guide must separate method lab from runtime")
require("运行门禁是守门员，不是作者" in reference, "maintainer guide must define the goalkeeper")
require("零 LLM/子 Agent 调用" in reference, "maintainer guide must keep runtime token-free")

if failures:
    raise SystemExit("\n".join(failures))

print(
    "PASS: risk-adaptive assurance selects bounded lenses across "
    f"{len(scenarios)} scenarios and {len(physics)} requirement-physics signals"
)
