#!/usr/bin/env python3
"""Version and evidence boundaries; never certify model or customer outcomes."""
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[3]


def main():
    failures = []
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    version = re.search(r"^# AI Delivery Spec (\d+\.\d+\.\d+)", skill, re.M).group(1)
    status = yaml.safe_load((ROOT / "maintainer/evals/evidence/release-status.yaml").read_text(encoding="utf-8"))
    config = yaml.safe_load((ROOT / "examples/spec.config.example.yaml").read_text(encoding="utf-8"))
    if status.get("skill_version") != version or config["execution"]["expected_skill_version"] != version:
        failures.append("current version and status/config disagree")
    evidence = status.get("release_evidence", {})
    if not evidence.get("scope") or not evidence.get("results"):
        failures.append("release evidence lacks scope or recorded results")
    if version not in (ROOT / "README.md").read_text(encoding="utf-8"):
        failures.append("README does not identify the current candidate")
    coverage = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
    for domain in coverage.get("domains", []):
        if domain.get("maturity") in {"knowledge_backed", "contract_tested"} and domain.get("production_claim") == "allowed":
            failures.append("deterministic domain evidence cannot authorize production claims")
    for issue in failures:
        print("FAIL: " + issue)
    if not failures:
        print("PASS: version and declared evidence boundaries consistent; outcome claims require their own evidence")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
