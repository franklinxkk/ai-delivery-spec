#!/usr/bin/env python3
"""Validate v5 runtime budgets, routing, schemas, and public claim sources."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]

REQUIRED_FILES = (
    "schemas/product-truth.schema.json",
    "schemas/product-truth-index.schema.json",
    "schemas/product-truth-fragment.schema.json",
    "schemas/discovery-contract.schema.json",
    "schemas/clarification-transcript.schema.json",
    "maintainer/schemas/domain-pack.schema.json",
    "schemas/change-package.schema.json",
    "schemas/requirement-register.schema.json",
    "schemas/traceability-ledger.schema.json",
    "schemas/acceptance-run.schema.json",
    "schemas/review-record.schema.json",
    "schemas/requirement-pattern-library.schema.json",
    "schemas/project-domain-capsule.schema.json",
    "schemas/spec-config.schema.json",
    "schemas/context-plan.schema.json",
    "schemas/execution-state.schema.json",
    "schemas/gate-result.schema.json",
    "schemas/agent-handoff.schema.json",
    "schemas/domain-candidate.schema.json",
    "schemas/domain-usage-log.schema.json",
    "maintainer/schemas/assurance-evidence.schema.json",
    "maintainer/schemas/eval-case.schema.json",
    "maintainer/schemas/evaluation-run.schema.json",
    "references/discover.md",
    "references/lifecycle.md",
    "references/specify.md",
    "references/prototype.md",
    "references/context.md",
    "references/change-acceptance.md",
    "references/troubleshooting.md",
    "references/tool-adapters.md",
    "maintainer/README.md",
    "maintainer/templates/domain-module-template.md",
    "references/domain-coverage.yaml",
    "references/domains/domain-sources.yaml",
    "maintainer/evals/eval-catalog.yaml",
    "maintainer/evals/domain-fixtures.yaml",
    "maintainer/evals/github-cases.yaml",
    "maintainer/evals/metric-definitions.yaml",
    "maintainer/evals/evidence/github-source-verification-2026-07-11.yaml",
    "maintainer/evals/evidence/github-validation-matrix.yaml",
    "maintainer/evals/evidence/static-regression-2026-07-11.yaml",
    "maintainer/evals/evidence/production-practice-attestation-2026-07-12.yaml",
    "maintainer/evals/evidence/release-status.yaml",
    "maintainer/evals/requirement-intake-benchmark.yaml",
    "scripts/validators/validate_prd_quality.py",
    "scripts/validators/validate_ia_skeleton.py",
    "scripts/validators/validate_coding_agent_contract.py",
    "scripts/validators/validate_unified_prd.py",
    "scripts/validators/validate_requirement_register.py",
    "scripts/validators/validate_traceability_ledger.py",
    "scripts/validators/validate_acceptance_run.py",
    "scripts/validators/validate_review_record.py",
    "maintainer/tools/validators/validate_domain_contracts.py",
    "scripts/validators/validate_requirement_patterns.py",
    "scripts/triage_requirement.py",
    "scripts/analyze_change_impact.py",
    "scripts/build_traceability_ledger.py",
    "scripts/query_domain.py",
    "scripts/scan_requirement_ambiguity.py",
    "scripts/scan_prototype_css.py",
    "scripts/render_mermaid_flow.py",
    "maintainer/tests/test_v502_coding_contract.py",
    "maintainer/tests/test_v502_progressive_truth.py",
    "maintainer/tests/test_v510_requirement_management.py",
    "maintainer/tests/test_v510_unified_prd.py",
    "maintainer/tests/test_v511_runtime_budget.py",
    "maintainer/tests/test_v511_domain_assurance.py",
    "scripts/compile_product_truth.py",
    "scripts/compile_clarification_transcript.py",
    "scripts/validators/validate_capsule_composition.py",
    "maintainer/tests/test_v5_agent_deadlock.py",
    "maintainer/tests/test_v5_capsule_pollution.py",
    "maintainer/tests/test_v5_change_drift.py",
    "maintainer/tests/test_v5_schema_grill.py",
    "maintainer/tests/test_v5_status.py",
    "examples/spec.config.example.yaml",
    "references/templates/product-truth-template.yaml",
    "references/templates/product-truth-index-template.yaml",
    "references/templates/product-truth-core-fragment-template.yaml",
    "references/templates/product-truth-module-fragment-template.yaml",
    "references/templates/discovery-contract-template.yaml",
    "references/templates/unified-requirement-prd-template.md",
    "references/templates/requirement-register-template.yaml",
    "references/templates/change-request-template.yaml",
    "references/templates/acceptance-run-template.yaml",
    "references/templates/review-record-template.yaml",
    "references/templates/agent-handoff-manifest-template.yaml",
    "references/patterns/common-requirement-patterns.yaml",
)

STAGE_REFERENCE_BUDGET = 500
SKILL_LINE_BUDGET = 130
SKILL_CHAR_BUDGET = 6500
REPOSITORY_FILE_BUDGET = 180


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def main() -> int:
    failures: list[str] = []
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if line_count(ROOT / "SKILL.md") > SKILL_LINE_BUDGET:
        failures.append(f"SKILL.md exceeds {SKILL_LINE_BUDGET} lines")
    if len(skill) > SKILL_CHAR_BUDGET:
        failures.append(f"SKILL.md exceeds {SKILL_CHAR_BUDGET} characters")
    marker_groups = (
        ("ToB/ToG",),
        ("Requirement Management Kernel", "需求管理内核"),
        ("Product Truth", "结构化事实源"),
        ("one human-readable", "一份人类可读"),
        ("both directions", "双向追溯"),
        ("Start with intake", "需求准入"),
        ("scripts/query_domain.py",),
        ("schemas/agent-handoff.schema.json",),
        ("schemas/domain-candidate.schema.json",),
    )
    for aliases in marker_groups:
        if not any(marker.lower() in skill.lower() for marker in aliases):
            failures.append(f"SKILL.md missing v5 marker: {' / '.join(aliases)}")

    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing required file: {relative}")
            continue
        if path.suffix == ".md" and relative.startswith("references/") and line_count(path) > STAGE_REFERENCE_BUDGET:
            failures.append(f"stage reference exceeds {STAGE_REFERENCE_BUDGET} lines: {relative}")

    for relative in (
        "schemas/product-truth.schema.json",
        "schemas/product-truth-index.schema.json",
        "schemas/product-truth-fragment.schema.json",
        "schemas/discovery-contract.schema.json",
        "schemas/clarification-transcript.schema.json",
        "maintainer/schemas/domain-pack.schema.json",
        "schemas/change-package.schema.json",
        "schemas/requirement-register.schema.json",
        "schemas/traceability-ledger.schema.json",
        "schemas/acceptance-run.schema.json",
        "schemas/review-record.schema.json",
        "schemas/requirement-pattern-library.schema.json",
        "schemas/project-domain-capsule.schema.json",
        "schemas/spec-config.schema.json",
        "schemas/context-plan.schema.json",
        "schemas/execution-state.schema.json",
        "schemas/gate-result.schema.json",
        "schemas/agent-handoff.schema.json",
        "schemas/domain-candidate.schema.json",
        "schemas/domain-usage-log.schema.json",
        "maintainer/schemas/assurance-evidence.schema.json",
        "maintainer/schemas/eval-case.schema.json",
        "maintainer/schemas/evaluation-run.schema.json",
    ):
        try:
            json.loads((ROOT / relative).read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"invalid JSON schema {relative}: {exc}")

    try:
        yaml.safe_load((ROOT / "references/templates/product-truth-template.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "references/domains/domain-sources.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "maintainer/evals/eval-catalog.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "maintainer/evals/domain-fixtures.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "maintainer/evals/github-cases.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "maintainer/evals/metric-definitions.yaml").read_text(encoding="utf-8"))
        yaml.safe_load((ROOT / "examples/spec.config.example.yaml").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        failures.append(f"invalid YAML asset: {exc}")

    unified = (ROOT / "references/templates/unified-requirement-prd-template.md").read_text(encoding="utf-8")
    for marker in ("角色旅程", "页面与布局", "全局字段字典", "api、事件与集成业务契约", "机器可读验收", "双向追溯矩阵", "禁止推断清单"):
        if marker not in unified.lower():
            failures.append(f"Unified PRD template misses contract marker: {marker}")
    for forbidden in ("Bug Management", "Sprint Task Breakdown / WBS", "Development Follow-Up"):
        if forbidden in unified:
            failures.append(f"Unified PRD template contains project-tracking section: {forbidden}")

    allowed_root_files = {
        ".gitattributes", ".gitignore", "CHANGELOG.md", "LICENSE", "README.md", "SKILL.md"
    }
    allowed_root_dirs = {".github", "agents", "examples", "maintainer", "references", "schemas", "scripts"}
    actual_root_files = {path.name for path in ROOT.iterdir() if path.is_file()}
    actual_root_dirs = {path.name for path in ROOT.iterdir() if path.is_dir() and path.name != ".git"}
    if actual_root_files != allowed_root_files:
        failures.append(f"root files are not minimal: {sorted(actual_root_files)}")
    if actual_root_dirs != allowed_root_dirs:
        failures.append(f"root directories do not preserve runtime/maintainer separation: {sorted(actual_root_dirs)}")
    if any((ROOT / "scripts").glob("validate_*.py")):
        failures.append("validator scripts must live under scripts/validators")
    agent_files = {
        path.relative_to(ROOT / "agents").as_posix()
        for path in (ROOT / "agents").rglob("*") if path.is_file()
    }
    if agent_files != {"openai.yaml"}:
        failures.append(f"agents/ must contain UI metadata only: {sorted(agent_files)}")
    reference_files = {path.name for path in (ROOT / "references").iterdir() if path.is_file()}
    expected_reference_files = {
        "discover.md", "lifecycle.md", "specify.md", "prototype.md",
        "context.md", "change-acceptance.md", "troubleshooting.md",
        "tool-adapters.md", "domain-coverage.yaml",
    }
    if reference_files != expected_reference_files:
        failures.append(f"references root is not reduced to requirement runtime entries plus domain index: {sorted(reference_files)}")

    misplaced_maintainer_dirs = [name for name in ("tests", "evals") if (ROOT / name).exists()]
    if misplaced_maintainer_dirs:
        failures.append(f"maintainer-only directories leaked into runtime root: {misplaced_maintainer_dirs}")
    for required_dir in ("tests", "evals", "tools", "examples", "schemas", "templates"):
        if not (ROOT / "maintainer" / required_dir).is_dir():
            failures.append(f"maintainer lab misses directory: {required_dir}")

    package_files = [
        path for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    ]
    if len(package_files) > REPOSITORY_FILE_BUDGET:
        failures.append(
            f"repository has {len(package_files)} publishable files; budget is {REPOSITORY_FILE_BUDGET}"
        )

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    print(
        "PASS: v5 runtime architecture is lean and contract-driven "
        f"(SKILL {line_count(ROOT / 'SKILL.md')} lines, {len(package_files)} files, "
        f"stage refs <= {STAGE_REFERENCE_BUDGET})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
