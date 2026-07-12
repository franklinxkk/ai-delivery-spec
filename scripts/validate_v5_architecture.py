#!/usr/bin/env python3
"""Validate v5 runtime budgets, routing, schemas, and public claim sources."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "schemas/product-truth.schema.json",
    "schemas/discovery-contract.schema.json",
    "schemas/clarification-transcript.schema.json",
    "schemas/domain-pack.schema.json",
    "schemas/change-package.schema.json",
    "schemas/project-domain-capsule.schema.json",
    "schemas/spec-config.schema.json",
    "schemas/context-plan.schema.json",
    "schemas/execution-state.schema.json",
    "schemas/gate-result.schema.json",
    "schemas/assurance-evidence.schema.json",
    "schemas/eval-case.schema.json",
    "schemas/evaluation-run.schema.json",
    "references/discover.md",
    "references/specify.md",
    "references/composition.md",
    "references/handoff.md",
    "references/change.md",
    "references/verify.md",
    "references/operate.md",
    "references/context-planning.md",
    "references/execution-gates.md",
    "references/domain-coverage.yaml",
    "references/domain-sources.yaml",
    "references/capability-profiles.yaml",
    "evals/eval-catalog.yaml",
    "evals/domain-fixtures.yaml",
    "evals/github-cases.yaml",
    "evals/metric-definitions.yaml",
    "evals/evidence/github-source-verification-2026-07-11.yaml",
    "evals/evidence/github-validation-matrix.yaml",
    "evals/evidence/v5-hardening-regression-2026-07-11.yaml",
    "evals/evidence/release-status.yaml",
    "evals/triage-benchmark.yaml",
    "scripts/validate_prd_quality.py",
    "scripts/validate_ia_skeleton.py",
    "scripts/validate_coding_agent_contract.py",
    "scripts/render_mermaid_flow.py",
    "tests/test_v501_triage.py",
    "tests/test_v501_validators.py",
    "scripts/compile_clarification_transcript.py",
    "scripts/validate_capsule_composition.py",
    "tests/test_v5_agent_deadlock.py",
    "tests/test_v5_capsule_pollution.py",
    "tests/test_v5_change_drift.py",
    "tests/test_v5_schema_grill.py",
    "tests/test_v5_status.py",
    "spec.config.example.yaml",
    "references/templates/product-truth-template.yaml",
    "references/templates/discovery-contract-template.yaml",
)

STAGE_REFERENCE_BUDGET = 500
SKILL_LINE_BUDGET = 350


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def main() -> int:
    failures: list[str] = []
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if line_count(ROOT / "SKILL.md") > SKILL_LINE_BUDGET:
        failures.append(f"SKILL.md exceeds {SKILL_LINE_BUDGET} lines")
    for marker in (
        "ToB/ToG",
        "Product Truth",
        "project domain capsule",
        "references/domain-coverage.yaml",
        "schemas/change-package.schema.json",
        "schemas/project-domain-capsule.schema.json",
    ):
        if marker.lower() not in skill.lower():
            failures.append(f"SKILL.md missing v5 marker: {marker}")

    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing required file: {relative}")
            continue
        if path.suffix == ".md" and relative.startswith("references/") and line_count(path) > STAGE_REFERENCE_BUDGET:
            failures.append(f"stage reference exceeds {STAGE_REFERENCE_BUDGET} lines: {relative}")

    for relative in (
        "schemas/product-truth.schema.json",
        "schemas/discovery-contract.schema.json",
        "schemas/clarification-transcript.schema.json",
        "schemas/domain-pack.schema.json",
        "schemas/change-package.schema.json",
        "schemas/project-domain-capsule.schema.json",
        "schemas/spec-config.schema.json",
        "schemas/context-plan.schema.json",
        "schemas/execution-state.schema.json",
        "schemas/gate-result.schema.json",
        "schemas/assurance-evidence.schema.json",
        "schemas/eval-case.schema.json",
        "schemas/evaluation-run.schema.json",
    ):
        try:
            json.loads((ROOT / relative).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"invalid JSON schema {relative}: {exc}")

    try:
        yaml.safe_load((ROOT / "references/templates/product-truth-template.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "references/domain-sources.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "references/capability-profiles.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "evals/eval-catalog.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "evals/domain-fixtures.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "evals/github-cases.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "evals/metric-definitions.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "spec.config.example.yaml").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        failures.append(f"invalid YAML asset: {exc}")

    human = (ROOT / "references/templates/human-first-prd-template.md").read_text(encoding="utf-8")
    coding = (ROOT / "references/templates/ai-coding-prd-template.md").read_text(encoding="utf-8")
    if not re.search(r"not\s+an independent source of truth", human.lower()):
        failures.append("Human-First template does not declare projection semantics")
    if "do not copy the complete" not in coding.lower():
        failures.append("Coding-Agent template still permits Human-First duplication")
    for forbidden in ("Bug Management", "Sprint Task Breakdown / WBS", "Development Follow-Up"):
        if forbidden in human:
            failures.append(f"Human-First template contains project-tracking section: {forbidden}")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    print(
        "PASS: v5 runtime architecture is lean and contract-driven "
        f"(SKILL {line_count(ROOT / 'SKILL.md')} lines, stage refs <= {STAGE_REFERENCE_BUDGET})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
