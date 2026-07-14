"""Regression: final gate is deterministic, profile-based, and non-generative."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "quality_gate.py"
FIXTURES = ROOT / "tests" / "fixtures"
failures: list[str] = []


def run(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
    return subprocess.run(
        [sys.executable, str(GATE), *args], cwd=ROOT, text=True,
        encoding="utf-8", capture_output=True, env=env,
    )


valid_requirement = FIXTURES / "gate-requirement-valid.yaml"
invalid_requirement = FIXTURES / "gate-requirement-invalid.yaml"
valid_prd = FIXTURES / "coding-l2.md"
keyword_shell_prd = FIXTURES / "prd-l2-keyword-shell.md"
valid_prototype = FIXTURES / "gate-prototype-valid.html"
invalid_prototype = FIXTURES / "gate-prototype-invalid.html"
review_prototype = FIXTURES / "gate-prototype-review.html"

for profile, option, artifact in (
    ("requirement", "--requirement", valid_requirement),
    ("prd", "--prd", valid_prd),
    ("prototype", "--prototype", valid_prototype),
):
    result = run("--profile", profile, option, str(artifact), "--format", "json")
    if result.returncode != 0:
        failures.append(f"valid {profile} did not pass: {result.stdout}{result.stderr}")
        continue
    payload = json.loads(result.stdout)
    if payload["status"] != "PASS":
        failures.append(f"valid {profile} status was {payload['status']}")
    counts = payload["metrics"]["input_read_counts"]
    if any(count != 1 for count in counts.values()):
        failures.append(f"{profile} reread its input: {counts}")

full = run(
    "--profile", "full",
    "--requirement", str(valid_requirement),
    "--prd", str(valid_prd),
    "--prototype", str(valid_prototype),
    "--format", "json",
)
if full.returncode != 0:
    failures.append(f"valid full profile did not pass: {full.stdout}{full.stderr}")
else:
    payload = json.loads(full.stdout)
    if len(payload["metrics"]["input_read_counts"]) != 3 or any(
        count != 1 for count in payload["metrics"]["input_read_counts"].values()
    ):
        failures.append(f"full profile did not read each input exactly once: {payload['metrics']['input_read_counts']}")

bad_requirement = run("--profile", "requirement", "--requirement", str(invalid_requirement), "--format", "json")
if bad_requirement.returncode != 2 or json.loads(bad_requirement.stdout)["status"] != "BLOCKED":
    failures.append("broken requirement register was not blocked")

keyword_shell = run("--profile", "prd", "--prd", str(keyword_shell_prd), "--format", "json")
if keyword_shell.returncode != 2:
    failures.append(f"keyword-only PRD shell was not blocked: {keyword_shell.stdout}{keyword_shell.stderr}")
elif not any(item["code"] == "PRD-STRUCTURE" for item in json.loads(keyword_shell.stdout)["findings"]):
    failures.append("keyword-only PRD was blocked without the structural contract finding")

bad_prototype = run("--profile", "prototype", "--prototype", str(invalid_prototype), "--format", "json")
if bad_prototype.returncode != 2:
    failures.append("broken prototype was not blocked")
else:
    codes = {item["code"] for item in json.loads(bad_prototype.stdout)["findings"]}
    required_codes = {"PROTO-NO-PAGE-ANCHOR", "PROTO-UNHANDLED-ACTION", "PROTO-JS-SYNTAX"}
    if not required_codes.issubset(codes) or not any(code.startswith("PROTO-CSS-") for code in codes):
        failures.append(f"prototype blockers were not precise enough: {sorted(codes)}")

review = run("--profile", "prototype", "--prototype", str(review_prototype), "--format", "json")
if review.returncode != 1:
    failures.append(f"review-only prototype should exit 1: {review.stdout}{review.stderr}")
else:
    payload = json.loads(review.stdout)
    if payload["status"] != "REVIEW_COMPLETE_WITH_GAPS" or payload["summary"]["blockers"]:
        failures.append(f"review-only finding was classified incorrectly: {payload}")

missing = run("--profile", "full", "--prd", str(valid_prd), "--prototype", str(valid_prototype), "--format", "json")
if missing.returncode != 2 or not any(
    item["code"] == "GATE-MISSING-INPUT" for item in json.loads(missing.stdout)["findings"]
):
    failures.append("full profile did not block a missing requirement input")

source = GATE.read_text(encoding="utf-8")
for forbidden in ("openai", "anthropic", "generate_requirement", "auto_fix"):
    if forbidden in source.lower():
        failures.append(f"quality gate contains generative/fix coupling: {forbidden}")

if failures:
    raise SystemExit("\n".join(failures))
print("PASS: lightweight gate scans each input once, supports four profiles, and blocks precise contract gaps")
