#!/usr/bin/env python3
"""Compare baseline/candidate runs only when experimental conditions match."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from score_evaluation_run import score, validate_run


COMPARABLE_FIELDS = (
    ("case_id",),
    ("stage",),
    ("input_fingerprint",),
    ("repetitions",),
    ("system", "model"),
    ("system", "model_settings"),
    ("system", "repository_ref"),
)


def get(document: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = document
    for part in path:
        value = value[part]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    baseline = yaml.safe_load(args.baseline.read_text(encoding="utf-8"))
    candidate = yaml.safe_load(args.candidate.read_text(encoding="utf-8"))
    failures = [f"baseline {item}" for item in validate_run(baseline)]
    failures.extend(f"candidate {item}" for item in validate_run(candidate))
    for field in COMPARABLE_FIELDS:
        if get(baseline, field) != get(candidate, field):
            failures.append(
                f"non-comparable {'.'.join(field)}: {get(baseline, field)!r} != {get(candidate, field)!r}"
            )
    if baseline.get("system", {}).get("skill_version") == candidate.get("system", {}).get("skill_version"):
        failures.append("baseline and candidate must identify different skill versions")
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    base_score = score(baseline)
    candidate_score = score(candidate)
    deltas: dict[str, float | None] = {}
    for name, value in candidate_score["metrics"].items():
        old = base_score["metrics"].get(name)
        deltas[name] = round(value - old, 6) if isinstance(value, (int, float)) and isinstance(old, (int, float)) else None
    report = {
        "schema_version": "5.0.0",
        "baseline_run": baseline["run_id"],
        "candidate_run": candidate["run_id"],
        "comparable": True,
        "baseline_skill": baseline["system"]["skill_version"],
        "candidate_skill": candidate["system"]["skill_version"],
        "metric_delta_candidate_minus_baseline": deltas,
        "claim_boundary": "Deltas apply only to the matched case, model/settings, repository ref, input, and repetition count.",
    }
    rendered = yaml.safe_dump(report, allow_unicode=True, sort_keys=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    print("PASS: evaluation runs are comparable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
