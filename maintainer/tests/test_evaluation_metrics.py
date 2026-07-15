#!/usr/bin/env python3
"""Regression test for evaluation scoring and strict baseline comparability."""

from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "maintainer" / "tools"))
from score_evaluation_run import score, validate_run

RUN = ROOT / "maintainer/evals/runs/saleor-channel-id-design-v5.yaml"


def main() -> int:
    candidate = yaml.safe_load(RUN.read_text(encoding="utf-8"))
    candidate["inventions"].update(
        {"unsupported_business_behaviors": 0, "delivered_business_behaviors": 1, "p0_unsupported": 0}
    )
    failures: list[str] = []
    if validate_run(candidate):
        failures.append("candidate fixture is not schema-valid")
    result = score(candidate)
    if result["release_pass"]:
        failures.append("single exploratory run must not satisfy release repetition gate")

    baseline = copy.deepcopy(candidate)
    baseline["run_id"] = "RUN-SALEOR-DESIGN-BASELINE-TEST"
    baseline["system"]["skill_version"] = "5.0.0-baseline-fixture"
    baseline["observations"][0]["result"] = "missing"
    baseline["inventions"].update(
        {"unsupported_business_behaviors": 1, "delivered_business_behaviors": 1, "p0_unsupported": 1}
    )
    with tempfile.TemporaryDirectory(prefix="ai-delivery-eval-compare-") as temp:
        temp_path = Path(temp)
        base_path = temp_path / "baseline.yaml"
        candidate_path = temp_path / "candidate.yaml"
        report_path = temp_path / "report.yaml"
        base_path.write_text(yaml.safe_dump(baseline, sort_keys=False), encoding="utf-8")
        candidate_path.write_text(yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8")
        command = [
            sys.executable,
            str(ROOT / "maintainer/tools/compare_evaluation_runs.py"),
            "--baseline",
            str(base_path),
            "--candidate",
            str(candidate_path),
            "--output",
            str(report_path),
        ]
        comparable = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if comparable.returncode != 0 or not report_path.exists():
            failures.append("matched baseline/candidate fixture was not accepted as comparable")
        else:
            report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
            if report["metric_delta_candidate_minus_baseline"]["contract_adherence_rate"] <= 0:
                failures.append("comparison did not preserve candidate adherence improvement")
            if report["metric_delta_candidate_minus_baseline"]["unsupported_invention_rate"] >= 0:
                failures.append("comparison did not detect unsupported-invention drift")

        mismatched = copy.deepcopy(candidate)
        mismatched["input_fingerprint"] = "different-input"
        candidate_path.write_text(yaml.safe_dump(mismatched, sort_keys=False), encoding="utf-8")
        rejected = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if rejected.returncode == 0:
            failures.append("comparison accepted mismatched input fingerprints")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print("PASS: evaluation scorer enforces release repetition and strict baseline comparability")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
