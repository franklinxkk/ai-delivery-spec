#!/usr/bin/env python3
"""Validate honest domain coverage and maturity metadata."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
COVERAGE_PATH = ROOT / "references" / "domain-coverage.yaml"
SCHEMA_PATH = ROOT / "schemas" / "domain-pack.schema.json"
FIXTURE_PATH = ROOT / "evals" / "domain-fixtures.yaml"
GITHUB_CASES_PATH = ROOT / "evals" / "github-cases.yaml"
GITHUB_DOMAIN_ALIASES = {
    "traffic": {"transport"},
    "crm": {"crm-customer", "customer-service"},
    "education-it": {"education"},
    "oa": {"enterprise-office"},
    "medical-hospital-it": set(),
    "data-product": {"data-product"},
    "ai-native": set(),
}


def main() -> int:
    catalog = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures: list[str] = []
    fixture_catalog = yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))
    github_catalog = yaml.safe_load(GITHUB_CASES_PATH.read_text(encoding="utf-8"))
    fixtures = fixture_catalog.get("fixtures", [])
    github_cases = github_catalog.get("cases", [])
    fixture_ids: set[str] = set()
    for fixture in fixtures:
        fixture_id = fixture.get("id", "<missing>")
        if fixture_id in fixture_ids:
            failures.append(f"duplicate domain fixture: {fixture_id}")
        fixture_ids.add(fixture_id)
        if fixture.get("status") not in {"not_run", "partial", "passed", "failed"}:
            failures.append(f"{fixture_id} has invalid status: {fixture.get('status')}")
        source = fixture.get("source")
        if not source or not (ROOT / source).exists():
            failures.append(f"{fixture_id} source is missing: {source}")

    domains = catalog.get("domains", [])
    seen: set[str] = set()
    for item in domains:
        candidate = {"schema_version": catalog.get("schema_version"), **item}
        domain_id = item.get("domain_id", "<missing>")
        if domain_id in seen:
            failures.append(f"duplicate domain_id: {domain_id}")
        seen.add(domain_id)

        for error in validator.iter_errors(candidate):
            path = ".".join(str(part) for part in error.path) or "<root>"
            failures.append(f"{domain_id} schema {path}: {error.message}")

        knowledge_file = item.get("knowledge_file")
        if not knowledge_file or not (ROOT / knowledge_file).exists():
            failures.append(f"{domain_id} missing knowledge file: {knowledge_file}")

        coverage = item.get("coverage", {})
        maturity = item.get("maturity")
        practice_status = item.get("practice_status")
        for evidence in item.get("evidence", []):
            location = evidence.get("location", "")
            local = location.split("#", 1)[0]
            if not location.startswith(("https://", "http://")) and (not local or not (ROOT / local).exists()):
                failures.append(f"{domain_id} evidence location is missing: {location}")
        if maturity in {"knowledge_backed", "contract_tested"} and item.get("production_claim") == "allowed":
            failures.append(f"{domain_id} {maturity} pack cannot allow unqualified production claims")
        if practice_status in {"production_practiced", "production_observed"}:
            has_practice = any(
                evidence.get("kind") == "owner_attestation" and evidence.get("status") == "passed"
                for evidence in item.get("evidence", [])
            )
            if not has_practice:
                failures.append(f"{domain_id} {practice_status} lacks accountable practice evidence")
        if coverage.get("knowledge") == "sourced" and not any(
            evidence.get("kind") == "official_source" and evidence.get("status") == "current"
            for evidence in item.get("evidence", [])
        ):
            failures.append(f"{domain_id} claims sourced knowledge without current official evidence")
        if coverage.get("contract_eval") == "passed":
            has_contract = any(
                evidence.get("kind") == "contract_eval" and evidence.get("status") == "passed"
                for evidence in item.get("evidence", [])
            )
            if not has_contract:
                failures.append(f"{domain_id} claims contract PASS without passing evidence")
            domain_fixtures = [fixture for fixture in fixtures if fixture.get("domain") == domain_id]
            if not domain_fixtures or any(fixture.get("status") != "passed" for fixture in domain_fixtures):
                failures.append(f"{domain_id} contract PASS has missing or non-passing fixtures")
        if coverage.get("behavioral_eval") == "passed":
            has_eval = any(
                evidence.get("kind") == "behavioral_eval" and evidence.get("status") == "passed"
                for evidence in item.get("evidence", [])
            )
            if not has_eval:
                failures.append(f"{domain_id} claims behavioral PASS without passing evidence")
        if coverage.get("expert_review") == "reviewed":
            has_review = any(
                evidence.get("kind") == "expert_review" and evidence.get("status") == "passed"
                for evidence in item.get("evidence", [])
            )
            if not has_review:
                failures.append(f"{domain_id} claims expert review without accountable evidence")
        if maturity in {"contract_tested", "behavior_validated", "expert_reviewed", "audited"}:
            kinds = {(evidence.get("kind"), evidence.get("status")) for evidence in item.get("evidence", [])}
            required_kinds = {
                ("official_source", "current"),
                ("contract_eval", "passed"),
            }
            if maturity in {"behavior_validated", "expert_reviewed", "audited"}:
                required_kinds.add(("behavioral_eval", "passed"))
            if maturity in {"expert_reviewed", "audited"}:
                required_kinds.update({("project_sample", "passed"), ("expert_review", "passed")})
            missing_kinds = required_kinds - kinds
            if missing_kinds:
                failures.append(
                    f"{domain_id} {maturity} maturity lacks evidence: "
                    + ", ".join(f"{kind}/{status}" for kind, status in sorted(missing_kinds))
                )
        if maturity == "audited" and not any(
            evidence.get("kind") == "audit" and evidence.get("status") == "passed"
            for evidence in item.get("evidence", [])
        ):
            failures.append(f"{domain_id} audited maturity lacks passing independent audit evidence")

        fixture_count = sum(1 for fixture in fixtures if fixture.get("domain") == domain_id)
        aliases = GITHUB_DOMAIN_ALIASES.get(domain_id, set())
        github_count = sum(1 for case in github_cases if case.get("domain") in aliases)
        if fixture_count + github_count < 2:
            failures.append(
                f"{domain_id} has fewer than two eval assets: "
                f"fixtures={fixture_count}, github_cases={github_count}"
            )
        if fixture_count == 0:
            failures.append(f"{domain_id} has no domain-targeted fixture")

    fallback = catalog.get("fallback", {})
    required = {
        "vocabulary",
        "entities",
        "state_machines",
        "workflows",
        "policies",
        "source_register",
        "unknowns",
        "scenario_fixtures",
    }
    missing = required - set(fallback.get("required_outputs", []))
    if fallback.get("mode") != "project_domain_capsule" or missing:
        failures.append("generic fallback is incomplete: " + ", ".join(sorted(missing)))

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    maturity = {item["domain_id"]: item["maturity"] for item in domains}
    print(f"PASS: {len(domains)} domain packs have evidence-bounded maturity and >=2 eval assets: {maturity}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
