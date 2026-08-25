#!/usr/bin/env python3
"""Validate runtime budgets and capability contracts without pinning prose."""

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
    "schemas/requirement-intake.schema.json",
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
    "schemas/review-workspace.schema.json",
    "schemas/domain-candidate.schema.json",
    "schemas/domain-usage-log.schema.json",
    "schemas/assumption-register.schema.json",
    "maintainer/schemas/assurance-evidence.schema.json",
    "references/discover.md",
    "references/lifecycle.md",
    "references/specify.md",
    "references/prototype.md",
    "references/review-workspace.md",
    "references/context.md",
    "references/change-acceptance.md",
    "references/troubleshooting.md",
    "references/tool-adapters.md",
    "references/stages.md",
    "maintainer/README.md",
    "maintainer/templates/domain-module-template.md",
    "references/domain-coverage.yaml",
    "references/domains/domain-sources.yaml",
    "maintainer/evals/eval-catalog.yaml",
    "maintainer/evals/domain-fixtures.yaml",
    "maintainer/evals/metric-definitions.yaml",
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
    "scripts/stage_contract.py",
    "maintainer/checks/check_v540_stage_contracts.py",
    "maintainer/checks/check_v540_readme_commands.py",
    "maintainer/checks/check_human_review_contracts.py",
    "maintainer/tests/test_human_first_stage0_contracts.py",
    "maintainer/tests/test_product_experience.py",
    "maintainer/tests/test_v546_contract_invariants.py",
    "maintainer/tests/test_v547_dynamic_literal_anchor.py",
    "maintainer/tests/test_v547_review_workspace.py",
    "maintainer/checks/check_v502_progressive_truth.py",
    "maintainer/checks/check_v510_requirement_management.py",
    "maintainer/checks/check_v510_unified_prd.py",
    "maintainer/checks/check_v511_runtime_budget.py",
    "maintainer/checks/check_v511_domain_assurance.py",
    "maintainer/tests/test_runtime_resilience.py",
    "scripts/compile_product_truth.py",
    "scripts/compile_clarification_transcript.py",
    "scripts/validators/validate_capsule_composition.py",
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
    "references/templates/problem-brief-template.md",
    "references/templates/solution-sketch-template.md",
    "references/templates/assumption-register-template.yaml",
    "references/templates/requirement-brief-template.md",
    "references/templates/decision-record-template.md",
    "references/templates/agent-handoff-manifest-template.yaml",
    "references/patterns/common-requirement-patterns.yaml",
)

STAGE_REFERENCE_BUDGET = 500
SKILL_LINE_BUDGET = 130
SKILL_CHAR_BUDGET = 6500
REPOSITORY_FILE_BUDGET = 199


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def is_ignored_root_dir(name: str) -> bool:
    """Ignore known generated local evidence, never arbitrary product dirs."""
    return name in {
        ".pytest_cache", ".mypy_cache", ".ruff_cache", "htmlcov", "dist", "build", "custom",
    } or name.startswith(("pytest-cache-files-", "ads-human-review-", "ads-init-", "ads-manifest-"))


def main() -> int:
    failures: list[str] = []
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if line_count(ROOT / "SKILL.md") > SKILL_LINE_BUDGET:
        failures.append(f"SKILL.md exceeds {SKILL_LINE_BUDGET} lines")
    if len(skill) > SKILL_CHAR_BUDGET:
        failures.append(f"SKILL.md exceeds {SKILL_CHAR_BUDGET} characters")
    # Stable capabilities belong here; release-era slogans and incidental file
    # names do not. Required runtime files are validated separately below.
    capability_groups = {
        "requirements kernel": ("Requirement Management Kernel", "需求管理内核"),
        "shared human/agent contract": ("人机共用", "human and agent"),
        "single product fact line": ("产品事实主线", "product fact line"),
        "bidirectional trace": ("双向追溯", "bidirectional trace"),
        "requirements intake": ("需求准入", "requirements intake"),
        "retrieved domain evidence": ("scripts/query_domain.py",),
        "structured implementation handoff": ("结构化 handoff", "structured handoff"),
    }
    for capability, aliases in capability_groups.items():
        if not any(marker.lower() in skill.lower() for marker in aliases):
            failures.append(f"SKILL.md missing capability contract: {capability}")

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
    "schemas/requirement-intake.schema.json",
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
        "schemas/review-workspace.schema.json",
        "schemas/domain-candidate.schema.json",
        "schemas/domain-usage-log.schema.json",
        "schemas/assumption-register.schema.json",
        "maintainer/schemas/assurance-evidence.schema.json",
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
    # Git worktrees expose `.git` as a pointer file instead of a directory.
    actual_root_files = {path.name for path in ROOT.iterdir() if path.is_file() and path.name != ".git"}
    actual_root_dirs = {
        path.name for path in ROOT.iterdir()
        if path.is_dir() and path.name != ".git" and not is_ignored_root_dir(path.name)
    }
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
        "context.md", "change-acceptance.md", "troubleshooting.md", "review-workspace.md",
        "tool-adapters.md", "stages.md", "domain-coverage.yaml", "scaffolding-terms.yaml",
    }
    if reference_files != expected_reference_files:
        failures.append(f"references root is not reduced to requirement runtime entries plus domain index: {sorted(reference_files)}")

    misplaced_maintainer_dirs = [name for name in ("tests", "evals") if (ROOT / name).exists()]
    if misplaced_maintainer_dirs:
        failures.append(f"maintainer-only directories leaked into runtime root: {misplaced_maintainer_dirs}")
    for required_dir in ("tests", "evals", "tools", "examples", "schemas", "templates"):
        if not (ROOT / "maintainer" / required_dir).is_dir():
            failures.append(f"maintainer lab misses directory: {required_dir}")

    package_files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix == ".pyc":
            continue
        relative_parts = path.relative_to(ROOT).parts
        if ".git" in relative_parts or "__pycache__" in relative_parts:
            continue
        if relative_parts and is_ignored_root_dir(relative_parts[0]):
            continue
        package_files.append(path)
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
