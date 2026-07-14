"""Contract regression for the v5.1.0 cross-industry assurance portfolio.

This test proves structural coverage only. It intentionally does not claim that
the scenario fixtures were executed by experts or accepted by customers.
"""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "evals/industry-assurance-portfolio.yaml"
REFERENCE_PATH = ROOT / "references/runtime/assurance-lab.md"

portfolio = yaml.safe_load(PORTFOLIO_PATH.read_text(encoding="utf-8"))
reference = REFERENCE_PATH.read_text(encoding="utf-8")
failures: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


expected_stages = {
    "intake", "clarify", "specify", "review", "baseline", "change", "acceptance"
}
expected_roles = {
    "ROLE-LENS-SPONSOR",
    "ROLE-LENS-PRODUCT",
    "ROLE-LENS-DOMAIN",
    "ROLE-LENS-UX",
    "ROLE-LENS-ENGINEERING",
    "ROLE-LENS-QA",
    "ROLE-LENS-COMPLIANCE",
    "ROLE-LENS-CUSTOMER",
}
expected_sectors = {
    "manufacturing-industrial",
    "medical-healthcare",
    "finance-insurance",
    "energy-utilities",
    "retail-ecommerce",
    "digital-government",
    "construction-property",
}
expected_bridges = {"traffic", "crm", "education-it", "data-product", "ai-native"}
expected_outputs = {"unified_prd", "interactive_prototype", "machine_acceptance"}
expected_consumer_probes = {
    "product_design_review", "prototype_build", "engineering_design",
    "coding_implementation", "test_derivation", "customer_acceptance",
}

require(portfolio.get("schema_version") == "5.1.0", "portfolio schema_version must be 5.1.0")
claim = portfolio.get("claim_boundary", {})
require(claim.get("execution_status") == "contract_fixture", "portfolio must remain an unexecuted contract fixture")
require(claim.get("simulated_review_is_expert_review") is False, "simulation must not claim expert review")
require(claim.get("production_claim") == "prohibited", "production claims must be prohibited")

execution = portfolio.get("execution_model", {})
require(execution.get("scope") == "offline_release_hardening", "multi-agent work must be release hardening")
require(execution.get("runtime_prerequisite") is False, "multi-agent lab must not become a runtime prerequisite")
finding_contract = execution.get("finding_contract", {})
require(
    set(finding_contract.get("required", []))
    == {"id", "stage", "role", "verdict", "affected_ids", "evidence_refs", "gap", "required_decision"},
    "role findings need the compact stable-ID contract",
)
require(1 <= finding_contract.get("max_findings_per_role_scenario", 0) <= 5, "role finding cap must stay small")
require(finding_contract.get("max_chars_per_gap", 0) <= 240, "finding text must remain bounded")
require(execution.get("aggregation", {}).get("majority_can_override_blocker") is False, "majority voting cannot override blockers")

goalkeeper = portfolio.get("runtime_goalkeeper", {})
require(goalkeeper.get("llm_calls") == 0, "runtime goalkeeper must use zero LLM calls")
require(goalkeeper.get("subagent_calls") == 0, "runtime goalkeeper must use zero sub-agent calls")
require(goalkeeper.get("generates_or_fixes_requirements") is False, "goalkeeper must not author or fix requirements")
require(goalkeeper.get("generates_product_truth") is False, "goalkeeper must not generate Product Truth")
require(goalkeeper.get("artifact_parse_passes") == 1, "goalkeeper should parse each artifact once")

consumer_probes = portfolio.get("downstream_consumer_probes", {})
require(set(consumer_probes) == expected_consumer_probes, "product/R&D downstream consumer probes are incomplete")
for probe_id, probe in consumer_probes.items():
    require(bool(probe.get("consumer")), f"{probe_id} needs an accountable consumer")
    require(bool(probe.get("ready_when")), f"{probe_id} needs a readiness contract")
    require(bool(probe.get("forbidden")), f"{probe_id} needs a forbidden-invention boundary")

roles = portfolio.get("role_lenses", {})
require(set(roles) == expected_roles, f"role lens coverage mismatch: {set(roles)}")
stages = portfolio.get("stages", [])
stage_ids = {stage.get("id") for stage in stages}
require(stage_ids == expected_stages, f"stage coverage mismatch: {stage_ids}")
require(len(stages) == len(stage_ids), "stage IDs must be unique")
for stage in stages:
    stage_id = stage.get("id", "<missing>")
    mandatory = set(stage.get("mandatory_roles", []))
    minimum = stage.get("minimum_output", {})
    require(mandatory == expected_roles, f"{stage_id} must require all role lenses")
    require(set(minimum) == expected_roles, f"{stage_id} minimum outputs miss role lenses")
    for role, outputs in minimum.items():
        require(isinstance(outputs, list) and len(outputs) >= 4, f"{stage_id}/{role} needs at least four bounded outputs")

contracts = portfolio.get("output_contracts", {})
require(set(contracts) == expected_outputs, f"artifact output contracts mismatch: {set(contracts)}")
require(len(contracts["unified_prd"].get("required", [])) >= 7, "unified PRD quality contract is too thin")
require(len(contracts["interactive_prototype"].get("required", [])) >= 7, "prototype quality contract is too thin")
require(len(contracts["machine_acceptance"].get("required", [])) >= 3, "machine acceptance contract is too thin")

sources = portfolio.get("official_source_register", [])
source_ids = {source.get("id") for source in sources}
require(len(sources) >= 7 and len(source_ids) == len(sources), "official source register must cover unique sector anchors")
for source in sources:
    require(str(source.get("url", "")).startswith("https://"), f"{source.get('id')} must have an HTTPS source")
    require(bool(source.get("use")), f"{source.get('id')} must bound how the source is used")

scenarios = portfolio.get("scenarios", [])
scenario_ids = {scenario.get("id") for scenario in scenarios}
sectors = {scenario.get("sector") for scenario in scenarios}
require(len(scenarios) >= 6, "portfolio needs at least six new-sector scenarios")
require(len(scenario_ids) == len(scenarios), "scenario IDs must be unique")
require(expected_sectors.issubset(sectors), f"new-sector coverage mismatch: {sectors}")

physics_union: set[str] = set()
for scenario in scenarios:
    scenario_id = scenario.get("id", "<missing>")
    scenario_physics = set(scenario.get("requirement_physics", []))
    physics_union.update(scenario_physics)
    require(len(scenario_physics) >= 6, f"{scenario_id} requirement physics is too thin")
    require(set(scenario.get("deliverables", [])) == expected_outputs, f"{scenario_id} must exercise PRD, prototype and AC")
    require(set(scenario.get("stage_checks", {})) == expected_stages, f"{scenario_id} must exercise all seven stages")
    require(len(scenario.get("actors", [])) >= 6, f"{scenario_id} lacks cross-role workflow pressure")
    require(len(scenario.get("unknown_seeds", [])) >= 5, f"{scenario_id} lacks clarification pressure")
    require(len(scenario.get("prd_focus", [])) >= 6, f"{scenario_id} PRD focus is too thin")
    require(len(scenario.get("prototype_focus", [])) >= 5, f"{scenario_id} prototype focus is too thin")
    require(bool(scenario.get("change_probe")), f"{scenario_id} needs a material change probe")
    require(bool(scenario.get("acceptance_probe")), f"{scenario_id} needs an acceptance proof probe")
    for source_ref in scenario.get("source_refs", []):
        require(source_ref in source_ids, f"{scenario_id} references unknown official source {source_ref}")

require(len(physics_union) >= 30, f"portfolio requirement-physics diversity is too low: {len(physics_union)}")
bridges = portfolio.get("existing_domain_bridges", {})
require(set(bridges) == expected_bridges, f"existing domain bridge coverage mismatch: {set(bridges)}")
for bridge_id, bridge in bridges.items():
    linked = set(bridge.get("scenarios", []))
    require(linked and linked.issubset(scenario_ids), f"{bridge_id} bridge has invalid scenarios: {linked}")
    require(bool(bridge.get("bridge_question")), f"{bridge_id} needs a composition review question")

release_acceptance = portfolio.get("release_acceptance", {}).get("required", [])
require(len(release_acceptance) >= 6, "release acceptance must encode portfolio completion")
require("release-hardening activity" in reference, "reference must separate the offline lab from runtime")
require("zero LLM/sub-agent calls" in reference, "reference must keep the runtime gate token-free")
require("goalkeeper, not an author" in reference, "reference must define the validator as goalkeeper")

if failures:
    raise SystemExit("\n".join(failures))

print(
    "PASS: v5.1.0 industry assurance covers "
    f"{len(scenarios)} sectors, {len(stages)} stages, {len(roles)} role lenses, "
    f"{len(physics_union)} requirement-physics signals, and a zero-agent runtime goalkeeper"
)
