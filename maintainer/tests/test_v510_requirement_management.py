"""Regression for intake, focused workspace, change, traceability and acceptance closure."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from ai_delivery_spec_cli import init_requirements  # noqa: E402
from triage_requirement import recommend, render_markdown  # noqa: E402


def run(*parts: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *parts], cwd=ROOT, text=True, encoding="utf-8", capture_output=True)


failures: list[str] = []

benchmark = yaml.safe_load((ROOT / "maintainer/evals/requirement-intake-benchmark.yaml").read_text(encoding="utf-8"))
for case in benchmark["cases"]:
    actual = recommend(case["input"])
    expected = case["expected"]
    observed = {
        "decision": actual["decision"], "priority": actual["priority"],
        "mode": actual["recommended_mode"], "tier": actual["recommended_tier"],
    }
    if observed != expected:
        failures.append(f"{case['id']} intake benchmark mismatch: {observed} != {expected}")

tiny = recommend({
    "title": "rename", "outcome": "label is clear", "owner": "pm",
    "source_refs": ["SRC-1"], "value_evidence": ["approved request"],
    "roles": ["ROLE-1"], "modules": ["MOD-1"], "reversible": True,
})
if (tiny["decision"], tiny["recommended_mode"], tiny["recommended_tier"]) != ("accept", "ultra_light", "L0"):
    failures.append(f"tiny triage mismatch: {tiny}")

regulated = recommend({
    "title": "regulated change", "outcome": "meet authority requirement", "owner": "pm",
    "source_refs": ["SRC-LAW"], "value_evidence": ["regulatory deadline"],
    "roles": ["ROLE-A", "ROLE-B"], "modules": ["MOD-A", "MOD-B"],
    "reversible": False, "compliance": True, "regulatory_deadline": True,
})
if (regulated["priority"], regulated["recommended_mode"], regulated["recommended_tier"]) != ("P0", "full", "L3"):
    failures.append(f"regulated triage mismatch: {regulated}")

ai_assist = recommend({
    "title": "AI summary", "outcome": "reviewer reads a concise draft", "owner": "pm",
    "source_refs": ["SRC-AI"], "value_evidence": ["approved experiment"],
    "roles": ["ROLE-REVIEWER"], "modules": ["MOD-DETAIL"], "reversible": True,
    "ai_behavior": True, "ai_centrality": "supporting", "ai_write_scope": "draft_only",
    "ai_reversible": True, "ai_human_gate": True,
})
if ai_assist["recommended_tier"] == "L3":
    failures.append(f"reversible human-gated AI assistance was over-routed to L3: {ai_assist}")

ai_write = recommend({
    "title": "AI financial write", "outcome": "approved adjustment is posted", "owner": "finance",
    "source_refs": ["SRC-AI-WRITE"], "value_evidence": ["approved control"],
    "roles": ["ROLE-FINANCE"], "modules": ["MOD-LEDGER"], "reversible": False,
    "ai_behavior": True, "ai_centrality": "core", "ai_write_scope": "consequential_write",
    "ai_reversible": False, "ai_human_gate": True,
})
if ai_write["recommended_tier"] != "L3":
    failures.append(f"consequential AI write was not routed to L3: {ai_write}")

unclear = recommend({"title": "idea", "roles": [], "modules": [], "reversible": False})
if unclear["decision"] != "clarify" or not unclear["missing_for_intake"]:
    failures.append("unclear intake must not enter specification")

large_by_count = recommend({
    "title": "large readable PRD", "outcome": "all roles share one baseline", "owner": "pm",
    "source_refs": ["SRC-LARGE"], "value_evidence": ["approved scope"],
    "roles": [f"ROLE-{i}" for i in range(8)], "modules": [f"MOD-{i}" for i in range(12)],
    "reversible": False,
})
if large_by_count["delivery_shape"] != "unified_prd":
    failures.append("counts alone incorrectly forced governed Product Truth")

governed = recommend({
    "title": "controlled projections", "outcome": "all projections share governed facts", "owner": "pm",
    "source_refs": ["SRC-GOV"], "value_evidence": ["audit decision"],
    "roles": ["ROLE-1"], "modules": ["MOD-1"], "reversible": False,
    "controlled_projections": ["PRD", "admin", "H5"], "strong_audit": True,
})
if governed["delivery_shape"] != "governed_truth":
    failures.append("controlled multi-projection work did not trigger governed truth")

data_submission = recommend({
    "title": "经营数据上报", "outcome": "主管部门收到可对账的数据", "owner": "产品负责人",
    "source_refs": ["SRC-REPORT"], "value_evidence": ["已确认上报要求"],
    "roles": ["ROLE-REPORTER"], "modules": ["MOD-REPORT"], "reversible": True,
    "data_submission": True, "states": ["draft", "validating", "submitted", "rejected"],
})
if data_submission["document_language"] != "zh-CN":
    failures.append("Chinese intake did not preserve the user's language")
if data_submission["delivery_shape"] != "unified_prd" or data_submission["recommended_tier"] != "L2":
    failures.append(f"data submission was under-routed: {data_submission}")
if "data_submission" not in data_submission["activated_facets"]:
    failures.append("data submission did not activate its conditional contract")
if not render_markdown(data_submission).startswith("# 需求准入与分诊建议"):
    failures.append("Chinese intake rendered an English recommendation")

with tempfile.TemporaryDirectory(prefix="ads-v510-") as temp:
    workspace = Path(temp) / "requirements"
    init_requirements(argparse.Namespace(output=workspace, force=False, with_product_truth=False))
    required = ["intake.yaml", "register.yaml", "PRD.md", "manifest.json", "reviews/REVIEW-CORE-001.yaml", "changes/CHG-CORE-001.yaml", "acceptance/ARUN-CORE-001.yaml"]
    for rel in required:
        if not (workspace / rel).exists():
            failures.append(f"focused workspace omitted {rel}")
    if (workspace / "truth").exists():
        failures.append("Product Truth must be opt-in for bounded requirement work")

    for validator, rel in (
        ("scripts/validators/validate_requirement_register.py", "register.yaml"),
        ("scripts/validators/validate_review_record.py", "reviews/REVIEW-CORE-001.yaml"),
        ("scripts/validators/validate_change_package.py", "changes/CHG-CORE-001.yaml"),
        ("scripts/validators/validate_acceptance_run.py", "acceptance/ARUN-CORE-001.yaml"),
    ):
        result = run(validator, str(workspace / rel))
        if result.returncode:
            failures.append(f"template validator failed {rel}: {result.stdout}{result.stderr}")

    bad_review_value = yaml.safe_load((workspace / "reviews/REVIEW-CORE-001.yaml").read_text(encoding="utf-8"))
    bad_review_value["status"] = "completed"
    bad_review = workspace / "reviews/bad.yaml"
    bad_review.write_text(yaml.safe_dump(bad_review_value, allow_unicode=True, sort_keys=False), encoding="utf-8")
    if run("scripts/validators/validate_review_record.py", str(bad_review)).returncode == 0:
        failures.append("completed review with open P1 finding must fail")

    bad_change_value = yaml.safe_load((workspace / "changes/CHG-CORE-001.yaml").read_text(encoding="utf-8"))
    bad_change_value["status"] = "approved"
    bad_change = workspace / "changes/bad.yaml"
    bad_change.write_text(yaml.safe_dump(bad_change_value, allow_unicode=True, sort_keys=False), encoding="utf-8")
    if run("scripts/validators/validate_change_package.py", str(bad_change)).returncode == 0:
        failures.append("approved change without approval record must fail")

    truth = {
        "sources": [{"id": "SRC-ONE"}],
        "requirements": [{"id": "REQ-ONE", "source_refs": ["SRC-ONE"], "behavior_refs": ["VIEW-ONE", "ACT-ONE"], "acceptance_refs": ["AC-ONE"]}],
        "views": [{"id": "VIEW-ONE", "action_refs": ["ACT-ONE"]}],
        "actions": [{"id": "ACT-ONE", "acceptance_refs": ["AC-ONE"]}],
        "acceptance": [{"id": "AC-ONE", "requirement_refs": ["REQ-ONE"]}],
    }
    truth_path = workspace / "truth.yaml"
    truth_path.write_text(yaml.safe_dump(truth, sort_keys=False), encoding="utf-8")
    ledger_path = workspace / "traceability.yaml"
    built = run("scripts/build_traceability_ledger.py", "--truth", str(truth_path), "--output", str(ledger_path), "--baseline-version", "1.0")
    if built.returncode:
        failures.append("trace ledger build failed: " + built.stdout + built.stderr)
    checked = run("scripts/validators/validate_traceability_ledger.py", str(ledger_path))
    if checked.returncode:
        failures.append("trace ledger is not bidirectionally closed: " + checked.stdout + checked.stderr)
    slice_path = workspace / "req-slice.yaml"
    sliced = run("scripts/query_product_truth.py", "--truth", str(truth_path), "--id", "REQ-ONE", "--include-reverse", "--output", str(slice_path))
    if sliced.returncode or "requirements:" not in slice_path.read_text(encoding="utf-8"):
        failures.append("REQ seed must be retrievable as a reference-closed working slice")

    change = yaml.safe_load((workspace / "changes/CHG-CORE-001.yaml").read_text(encoding="utf-8"))
    change["request"]["seed_refs"] = ["REQ-ONE"]
    change_path = workspace / "change-for-impact.yaml"
    change_path.write_text(yaml.safe_dump(change, allow_unicode=True, sort_keys=False), encoding="utf-8")
    impact_path = workspace / "impact.yaml"
    impact = run("scripts/analyze_change_impact.py", "--truth", str(truth_path), "--change", str(change_path), "--output", str(impact_path))
    if impact.returncode:
        failures.append("change impact analysis failed: " + impact.stdout + impact.stderr)
    else:
        affected = {item["ref"] for item in yaml.safe_load(impact_path.read_text(encoding="utf-8"))["affected"]}
        if not {"REQ-ONE", "SRC-ONE", "VIEW-ONE", "ACT-ONE", "AC-ONE"}.issubset(affected):
            failures.append(f"impact traversal missed transitive IDs: {affected}")

    accepted = yaml.safe_load((workspace / "acceptance/ARUN-CORE-001.yaml").read_text(encoding="utf-8"))
    accepted["conclusion"] = "accepted"
    bad_run = workspace / "acceptance/bad.yaml"
    bad_run.write_text(yaml.safe_dump(accepted, sort_keys=False), encoding="utf-8")
    bad = run("scripts/validators/validate_acceptance_run.py", str(bad_run))
    if bad.returncode == 0:
        failures.append("acceptance without executed mandatory evidence must fail")

if failures:
    raise SystemExit("\n".join(failures))
print("PASS: v5.1.0 10/10 intake, focused workspace, change, traceability and acceptance are closed")

# Role/seniority ownership is part of the lifecycle reference, not a second runtime file.
lifecycle = (ROOT / "references/lifecycle.md").read_text(encoding="utf-8")
skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
for marker in (
    "Junior product", "Mid/senior product", "Developers and Coding Agents", "Architects",
    "sponsor/business", "domain owner", "UX/prototype", "engineering/architecture",
    "QA/acceptance", "compliance/security", "baseline version/hash", "REV/CHG",
):
    if marker not in lifecycle:
        raise SystemExit(f"lifecycle ownership misses {marker}")
if "references/lifecycle.md" not in skill:
    raise SystemExit("SKILL does not selectively route lifecycle/role work")
print("PASS: role and seniority ownership is bounded inside the lifecycle route")
