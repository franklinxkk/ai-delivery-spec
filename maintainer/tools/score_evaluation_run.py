#!/usr/bin/env python3
"""Score an evaluation run against a frozen GitHub case."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def ratio(numerator: float, denominator: float) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def load_case(case_id: str, stage: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    catalog = yaml.safe_load((ROOT / "maintainer/evals/github-cases.yaml").read_text(encoding="utf-8"))
    for case in catalog["cases"]:
        if case["id"] == case_id:
            return case, case["stages"][stage]
    raise ValueError(f"unknown case: {case_id}")


def score(run: dict[str, Any]) -> dict[str, Any]:
    case, obligations = load_case(run["case_id"], run["stage"])
    obligation_map = {item["id"]: item for item in obligations}
    observations = {item["obligation_id"]: item for item in run["observations"]}
    unknown = sorted(set(observations) - set(obligation_map))
    if unknown:
        raise ValueError("run contains unknown obligation IDs: " + ", ".join(unknown))

    total_weight = sum(item["weight"] for item in obligations)
    p0_weight = sum(item["weight"] for item in obligations if item["priority"] == "P0")
    executed_weight = 0.0
    satisfied_weight = 0.0
    p0_satisfied_weight = 0.0
    loss_weight = 0.0
    p0_missing = 0
    result_factor = {"satisfied": 1.0, "partial": 0.5, "missing": 0.0, "conflict": 0.0, "not_run": 0.0}

    for obligation in obligations:
        observation = observations.get(obligation["id"], {"result": "not_run"})
        result = observation["result"]
        if result != "not_run":
            executed_weight += obligation["weight"]
        factor = result_factor[result]
        satisfied_weight += obligation["weight"] * factor
        if obligation["priority"] == "P0":
            p0_satisfied_weight += obligation["weight"] * factor
            if result in {"missing", "conflict", "not_run"}:
                p0_missing += 1
        if result in {"missing", "conflict", "not_run"}:
            loss_weight += obligation["weight"]

    inventions = run["inventions"]
    delivery = run["delivery"]
    context = run["context"]
    metrics = {
        "execution_coverage": ratio(executed_weight, total_weight),
        "contract_adherence_rate": ratio(satisfied_weight, total_weight),
        "p0_contract_adherence_rate": ratio(p0_satisfied_weight, p0_weight),
        "unsupported_invention_rate": ratio(
            inventions["unsupported_business_behaviors"], inventions["delivered_business_behaviors"]
        ),
        "context_loss_rate": ratio(loss_weight, total_weight),
        "change_regression_rate": ratio(
            delivery["failed_impacted_acceptance"], delivery["impacted_acceptance"]
        ),
        "spec_rework_rate": ratio(delivery["reopened_for_spec_mismatch"], delivery["delivered_slices"]),
        "tokens_per_accepted_ac": (
            ratio(context["input_tokens"] + context["output_tokens"], delivery["accepted_acceptance"])
            if context["input_tokens"] is not None and context["output_tokens"] is not None
            else None
        ),
        "human_navigation_seconds": context.get("human_navigation_seconds"),
        "cross_artifact_switches": context["cross_artifact_switches"],
    }

    gates = {
        "completed": run["status"] == "completed",
        "minimum_repetitions": run["repetitions"] >= 3,
        "all_obligations_executed": metrics["execution_coverage"] == 1.0,
        "p0_complete": p0_missing == 0 and metrics["p0_contract_adherence_rate"] == 1.0,
        "overall_adherence": (metrics["contract_adherence_rate"] or 0) >= 0.95,
        "no_unsupported_invention": inventions["p0_unsupported"] == 0
        and (metrics["unsupported_invention_rate"] in {None, 0.0}),
        "context_loss": (metrics["context_loss_rate"] or 0) <= 0.05,
        "change_regression": metrics["change_regression_rate"] in {None, 0.0},
        "spec_rework": metrics["spec_rework_rate"] is None or metrics["spec_rework_rate"] <= 0.05,
        "coding_execution": run["stage"] != "coding_delivery"
        or (delivery["delivered_slices"] > 0 and delivery["accepted_acceptance"] > 0),
        "token_measurement": context["input_tokens"] is not None and context["output_tokens"] is not None,
    }
    release_pass = all(gates.values())
    return {
        "schema_version": "5.0.0",
        "run_id": run["run_id"],
        "case_id": case["id"],
        "stage": run["stage"],
        "skill_version": run["system"]["skill_version"],
        "metrics": metrics,
        "critical_counts": {
            "p0_missing": p0_missing,
            "p0_unsupported_inventions": inventions["p0_unsupported"],
        },
        "release_gates": gates,
        "release_pass": release_pass,
        "claim_boundary": (
            "A score covers only this pinned case, stage, input, model/settings, repetitions, and evidence."
        ),
    }


def validate_run(run: dict[str, Any]) -> list[str]:
    schema = json.loads((ROOT / "maintainer/schemas/evaluation-run.schema.json").read_text(encoding="utf-8"))
    failures = [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(run)
    ]
    if isinstance(run, dict) and len(run.get("trial_evidence_refs", [])) != run.get("repetitions"):
        failures.append("trial_evidence_refs count must equal repetitions")
    refs = list(run.get("trial_evidence_refs", [])) + list(run.get("evidence_refs", []))
    for observation in run.get("observations", []):
        refs.extend(observation.get("evidence_refs", []))
    for ref in set(refs):
        if not ref.startswith(("https://", "http://")) and not (ROOT / ref).exists():
            failures.append(f"missing evaluation evidence: {ref}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-release-pass", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    run = yaml.safe_load(args.run.read_text(encoding="utf-8"))
    failures = validate_run(run)
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    try:
        result = score(run)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    rendered = yaml.safe_dump(result, allow_unicode=True, sort_keys=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    elif not args.quiet:
        print(rendered, end="")
    if args.require_release_pass and not result["release_pass"]:
        print("FAIL: evaluation run does not satisfy release gates")
        return 1
    print(f"PASS: scored {run['run_id']} (release_pass={result['release_pass']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
