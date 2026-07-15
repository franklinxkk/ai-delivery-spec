#!/usr/bin/env python3
"""Validate evaluation catalog coverage and prevent unevidenced PASS claims."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "maintainer" / "evals" / "eval-catalog.yaml"


def main() -> int:
    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    failures: list[str] = []
    scenarios = catalog.get("scenarios", [])
    ids: set[str] = set()
    projects: set[str] = set()
    perspectives: set[str] = set()
    shapes: set[str] = set()
    metrics_path = catalog.get("claim_policy", {}).get("quantitative_metrics")
    if not metrics_path or not (ROOT / metrics_path).exists():
        failures.append("evaluation catalog must reference quantitative metric definitions")

    for scenario in scenarios:
        scenario_id = scenario.get("id")
        if not scenario_id or scenario_id in ids:
            failures.append(f"missing or duplicate evaluation ID: {scenario_id}")
        ids.add(scenario_id)
        projects.add(scenario.get("project", ""))
        perspectives.add(scenario.get("perspective", ""))
        shapes.add(scenario.get("shape", ""))
        if not scenario.get("expected"):
            failures.append(f"{scenario_id} has no expected behavior")
        if not scenario.get("dimensions"):
            failures.append(f"{scenario_id} has no scoring dimensions")
        if scenario.get("status") in {"partial", "passed"} and not scenario.get("evidence"):
            failures.append(f"{scenario_id} claims {scenario.get('status')} without evidence")
        for evidence in scenario.get("evidence", []):
            evidence_path = ROOT / evidence
            if not evidence_path.exists():
                failures.append(f"{scenario_id} references missing evidence: {evidence}")
                continue
            if evidence_path.suffix in {".yaml", ".yml"}:
                document = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
                if scenario.get("status") == "passed" and document.get("release_pass") is False:
                    failures.append(f"{scenario_id} claims passed with a non-release evaluation score")

    if len(projects) < 4:
        failures.append("evaluation catalog must cover at least four projects")
    if not {"greenfield", "brownfield"}.issubset(shapes):
        failures.append("evaluation catalog must cover greenfield and brownfield")
    required_perspectives = {"newcomer", "product_owner", "coding_agent", "qa", "accountable_domain_reviewer"}
    missing = required_perspectives - perspectives
    if missing:
        failures.append("missing evaluation perspectives: " + ", ".join(sorted(missing)))

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    counts: dict[str, int] = {}
    for scenario in scenarios:
        counts[scenario["status"]] = counts.get(scenario["status"], 0) + 1
    print(
        f"PASS: evaluation catalog is honest and diverse "
        f"({len(scenarios)} scenarios, {len(projects)} projects, status={counts})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
