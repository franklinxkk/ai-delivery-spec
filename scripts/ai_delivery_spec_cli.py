#!/usr/bin/env python3
"""Small helper CLI for AI Delivery Spec delivery packages."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ModuleNotFoundError as exc:  # pragma: no cover - clean-machine path
    missing = getattr(exc, "name", "PyYAML/jsonschema")
    print(
        f"缺少运行依赖 {missing}。请先执行：python -m pip install -r scripts/requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(4) from exc


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parents[1]


DELIVERY_DIRS = (
    "truth",
    "projections",
    "prototype",
    "acceptance",
    "changes",
    "agents",
    "evidence",
)

REQUIREMENT_DIRS = (
    "reviews",
    "changes",
    "acceptance",
    "exports",
    "slices",
    "crosscut",
    "integration",
)


def current_version() -> str:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"AI Delivery Spec\s+(\d+\.\d+\.\d+)", text)
    return match.group(1) if match else "unknown"


def merge_markdown_template(base: str, overlay: str) -> str:
    """Replace exact H2 sections from a small local overlay; keep all other official sections."""
    directive = re.match(r"\s*<!--\s*extends:\s*unified-requirement-prd-template(?:\.md)?\s*-->\s*", overlay, re.I)
    if not directive:
        return overlay
    overlay = overlay[directive.end():]

    def sections(text: str) -> list[tuple[str, int, int]]:
        matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", text))
        return [
            (match.group(1).strip(), match.start(), matches[index + 1].start() if index + 1 < len(matches) else len(text))
            for index, match in enumerate(matches)
        ]

    result = base
    for title, start, end in sections(overlay):
        replacement = overlay[start:end].rstrip() + "\n\n"
        target = next((item for item in sections(result) if item[0].casefold() == title.casefold()), None)
        if target:
            result = result[:target[1]] + replacement + result[target[2]:]
        else:
            result = result.rstrip() + "\n\n" + replacement
    return result.rstrip() + "\n"


def init_custom(args: argparse.Namespace) -> int:
    """Create a private-by-default, declarative local extension workspace."""
    target = args.output.resolve()
    for rel in ("domains", "templates", "validators"):
        (target / rel).mkdir(parents=True, exist_ok=True)
    files = {
        target / ".gitignore": "*\n!.gitignore\n",
        target / "config.yaml": (
            "schema_version: 5.3.0\nprivacy: local_only\n"
            "conflict_policy: binding_conflicts_require_DEC-CONFLICT\n"
            "domains:\n  - domain_id: my-team\n    knowledge_file: domains/my-team.md\n"
            "    maturity: local\n    owner: 待指定\n"
        ),
        target / "domains" / "my-team.md": "# my-team 私有领域包\n\n## 适用范围\n\n待补充。\n\n## 绑定规则\n\n待补充；与官方规则冲突时登记 DEC-CONFLICT-*。\n",
        target / "templates" / "my-team.md": "<!-- extends: unified-requirement-prd-template.md -->\n\n## 项目私有补充\n\n待补充团队特有的评审或审计要求。\n",
        target / "validators" / "my-team.yaml": (
            "rules:\n  - id: CUST-EXAMPLE-001\n    artifact: prd\n    assertion: must_match\n"
            "    severity: GAP\n    pattern: '项目私有补充'\n    message: PRD 缺少团队私有补充章节\n"
        ),
    }
    for path, content in files.items():
        if not path.exists() or args.force:
            path.write_text(content, encoding="utf-8", newline="\n")
    print(f"PASS: 已创建本地私有扩展目录 {target}；默认被 custom/.gitignore 阻止提交")
    return 0


def init_delivery(args: argparse.Namespace) -> int:
    target = args.output.resolve()
    target.mkdir(parents=True, exist_ok=True)
    for rel in DELIVERY_DIRS:
        (target / rel).mkdir(parents=True, exist_ok=True)

    config = target / "spec.config.yaml"
    if not config.exists():
        shutil.copyfile(ROOT / "examples/spec.config.example.yaml", config)

    progressive = args.truth_layout == "progressive"
    manifest = target / "manifest.json"
    if not manifest.exists() or args.force:
        payload = {
            "schema_version": "5.3.0",
            "generated_by": f"ai-delivery-spec v{current_version()}",
            "source_of_truth": "truth/index.yaml" if progressive else "truth/product-truth.yaml",
            "artifacts": [
                {
                    "path": "spec.config.yaml",
                    "kind": "project_config",
                    "authority": "project_override",
                    "status": "active",
                }
            ],
            "claims": {
                "schema_validated": False,
                "behaviorally_evaluated": False,
                "expert_reviewed": False,
                "production_validated": False,
            },
        }
        manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if progressive:
        (target / "truth" / "fragments").mkdir(parents=True, exist_ok=True)
        (target / "truth" / "compiled").mkdir(parents=True, exist_ok=True)
        template_pairs = (
            ("product-truth-index-template.yaml", target / "truth" / "index.yaml"),
            ("product-truth-core-fragment-template.yaml", target / "truth" / "fragments" / "00-core.yaml"),
            ("product-truth-module-fragment-template.yaml", target / "truth" / "fragments" / "MOD-EXAMPLE.yaml"),
        )
        for template, destination in template_pairs:
            if not destination.exists() or args.force:
                shutil.copyfile(ROOT / "references" / "templates" / template, destination)
    else:
        truth = target / "truth" / "product-truth.yaml"
        if not truth.exists() or args.force:
            shutil.copyfile(ROOT / "references" / "templates" / "product-truth-template.yaml", truth)

    print(f"initialized delivery package: {target}")
    return 0


def init_requirements(args: argparse.Namespace) -> int:
    """Create the focused requirement-management workspace used by v5.1+."""
    target = args.output.resolve()
    target.mkdir(parents=True, exist_ok=True)
    for rel in REQUIREMENT_DIRS:
        (target / rel).mkdir(parents=True, exist_ok=True)
    templates = (
        ("requirement-intake-template.yaml", target / "intake.yaml"),
        ("requirement-register-template.yaml", target / "register.yaml"),
        ("review-record-template.yaml", target / "reviews" / "REVIEW-CORE-001.yaml"),
        ("change-request-template.yaml", target / "changes" / "CHG-CORE-001.yaml"),
        ("acceptance-run-template.yaml", target / "acceptance" / "ARUN-CORE-001.yaml"),
        ("agent-handoff-manifest-template.yaml", target / "handoff-manifest.yaml"),
    )
    for template, destination in templates:
        if not destination.exists() or args.force:
            shutil.copyfile(ROOT / "references" / "templates" / template, destination)
    prd_destination = target / "PRD.md"
    if not prd_destination.exists() or args.force:
        official = (ROOT / "references" / "templates" / "unified-requirement-prd-template.md").read_text(encoding="utf-8")
        rendered = official
        template_name = getattr(args, "template", None)
        if template_name:
            if not re.fullmatch(r"[A-Za-z0-9_-]+", template_name):
                print("BLOCKED: template 只能包含字母、数字、下划线和连字符")
                return 2
            custom_root = getattr(args, "custom_root", Path("custom")).resolve()
            custom_template = custom_root / "templates" / f"{template_name}.md"
            if not custom_template.is_file():
                print(f"BLOCKED: 本地模板不存在：{custom_template}")
                return 2
            rendered = merge_markdown_template(official, custom_template.read_text(encoding="utf-8"))
        prd_destination.write_text(rendered, encoding="utf-8", newline="\n")
    if args.with_product_truth:
        truth_dir = target / "truth"
        (truth_dir / "fragments").mkdir(parents=True, exist_ok=True)
        (truth_dir / "compiled").mkdir(parents=True, exist_ok=True)
        for template, destination in (
            ("product-truth-index-template.yaml", truth_dir / "index.yaml"),
            ("product-truth-core-fragment-template.yaml", truth_dir / "fragments" / "00-core.yaml"),
            ("product-truth-module-fragment-template.yaml", truth_dir / "fragments" / "MOD-EXAMPLE.yaml"),
        ):
            if not destination.exists() or args.force:
                shutil.copyfile(ROOT / "references" / "templates" / template, destination)
    manifest = {
        "schema_version": "5.3.0",
        "generated_by": f"ai-delivery-spec v{current_version()}",
        "human_baseline": "PRD.md",
        "requirement_register": "register.yaml",
        "independent_product_truth": bool(args.with_product_truth),
        "structured_authority": "truth/index.yaml" if args.with_product_truth else None,
        "authority_rule": "one PRD is the review baseline; optional structured truth must preserve the same stable IDs and cannot become a second PRD",
        "boundary": "requirements_intake_to_acceptance",
        "template": getattr(args, "template", None) or "official:unified-requirement-prd-template",
        "governance": {
            "canonical_authoring_surface": "unified_prd",
            "projection_policy": "update_in_same_change",
        },
    }
    manifest_path = target / "manifest.json"
    if not manifest_path.exists() or args.force:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"initialized requirement workspace: {target}")
    return 0


def run_check(args: argparse.Namespace) -> int:
    commands: list[list[str]] = [
        [sys.executable, "maintainer/tools/validators/validate_v5_architecture.py"],
        [sys.executable, "scripts/validators/validate_spec_config.py", "examples/spec.config.example.yaml"],
        [sys.executable, "maintainer/tools/validators/validate_runtime_rule_uniqueness.py"],
        [sys.executable, "maintainer/tools/validators/validate_domain_coverage.py"],
        [sys.executable, "maintainer/tools/validators/validate_domain_sources.py"],
        [sys.executable, "maintainer/tools/validators/validate_domain_contracts.py"],
        [sys.executable, "maintainer/tools/validators/validate_eval_catalog.py"],
        [sys.executable, "maintainer/tools/validators/validate_github_eval_cases.py"],
        [sys.executable, "maintainer/tests/test_v502_coding_contract.py"],
        [sys.executable, "maintainer/tests/test_v502_progressive_truth.py"],
        [sys.executable, "maintainer/tests/test_v510_requirement_management.py"],
        [sys.executable, "maintainer/tests/test_v510_unified_prd.py"],
        [sys.executable, "maintainer/tests/test_v510_semantic_guards.py"],
        [sys.executable, "maintainer/tests/test_v510_lightweight_gate.py"],
        [sys.executable, "maintainer/tests/test_v510_industry_assurance.py"],
        [sys.executable, "maintainer/tests/test_v511_runtime_budget.py"],
        [sys.executable, "maintainer/tests/test_v511_domain_assurance.py"],
        [sys.executable, "maintainer/tests/test_v515_page_delivery_contract.py"],
        [sys.executable, "maintainer/tests/test_v516_ai_applicability.py"],
        [sys.executable, "maintainer/tests/test_v530_contracts.py"],
        [sys.executable, "scripts/validators/validate_requirement_patterns.py", "references/patterns/common-requirement-patterns.yaml"],
        [
            sys.executable,
            "maintainer/tools/build_github_validation_matrix.py",
            "--check",
            "maintainer/evals/evidence/github-validation-matrix.yaml",
        ],
        [sys.executable, "maintainer/tools/validators/validate_release_claims.py"],
        [sys.executable, "maintainer/tools/build_runtime_package.py", "--check"],
        [sys.executable, "maintainer/tests/test_context_planning.py"],
        [sys.executable, "maintainer/tests/test_evaluation_metrics.py"],
        [sys.executable, "maintainer/tests/test_execution_state.py"],
        [sys.executable, "maintainer/tests/test_cli_init.py"],
        [sys.executable, "maintainer/tests/test_v5_agent_deadlock.py"],
        [sys.executable, "maintainer/tests/test_v5_capsule_pollution.py"],
        [sys.executable, "maintainer/tests/test_v5_change_drift.py"],
        [sys.executable, "maintainer/tests/test_v5_schema_grill.py"],
        [sys.executable, "maintainer/tests/test_v5_status.py"],
        [
            sys.executable,
            "scripts/validators/validate_project_domain_capsule.py",
            "maintainer/examples/generic-energy-capsule-v5/project-domain-capsule.yaml",
        ],
        [
            sys.executable,
            "scripts/validators/validate_capsule_composition.py",
            "--capsule",
            "maintainer/examples/generic-energy-capsule-v5/project-domain-capsule.yaml",
        ],
        [
            sys.executable,
            "scripts/validators/validate_change_package.py",
            "maintainer/examples/traffic-regulatory-change-v5/change-package.yaml",
        ],
        [
            sys.executable,
            "scripts/validators/validate_product_truth.py",
            "maintainer/examples/publishing-learning-v5/delivery/truth/product-truth.yaml",
        ],
        [
            sys.executable,
            "scripts/validators/validate_projection_consistency.py",
            "--truth",
            "maintainer/examples/publishing-learning-v5/delivery/truth/product-truth.yaml",
            "--projection",
            "maintainer/examples/publishing-learning-v5/delivery/projections/unified-prd.md",
        ],
        [sys.executable, "scripts/validators/validate_unified_prd.py", "maintainer/examples/publishing-learning-v5/delivery/projections/unified-prd.md"],
        [sys.executable, "maintainer/tools/score_evaluation_run.py", "maintainer/evals/runs/chatwoot-voice-requirement-v5.yaml", "--quiet"],
        [sys.executable, "maintainer/tools/score_evaluation_run.py", "maintainer/evals/runs/saleor-channel-id-design-v5.yaml", "--quiet"],
        [sys.executable, "maintainer/tools/score_evaluation_run.py", "maintainer/evals/runs/openedx-reindex-design-v5.yaml", "--quiet"],
        [sys.executable, "maintainer/tools/score_evaluation_run.py", "maintainer/evals/runs/orangehrm-password-policy-handoff-v5.yaml", "--quiet"],
    ]
    if args.product_truth:
        commands.append(
            [sys.executable, "scripts/validators/validate_product_truth.py", str(args.product_truth)]
        )

    failed = 0
    for cmd in commands:
        print("+ " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=ROOT, text=True)
        if result.returncode != 0:
            failed = result.returncode
            if not args.keep_going:
                return failed
    return failed

def run_script(script: str, values: list[str]) -> int:
    # Resolve project-facing arguments from the caller's workspace, not from
    # the installed Skill directory. Bundled resources are located via __file__.
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *values],
        cwd=Path.cwd(), text=True,
    ).returncode


def run_repo_tool(relative: str, values: list[str]) -> int:
    """Run an explicitly located repository tool without mixing it into runtime scripts."""
    return subprocess.run([sys.executable, str(ROOT / relative), *values], cwd=ROOT, text=True).returncode


def plan_context(args: argparse.Namespace) -> int:
    values = ["--truth", str(args.truth), "--config", str(args.config)]
    for seed in args.seed_id:
        values.extend(["--seed-id", seed])
    if args.output:
        values.extend(["--output", str(args.output)])
    return run_script("plan_context.py", values)


def query_truth(args: argparse.Namespace) -> int:
    values = ["--truth", str(args.truth), "--output", str(args.output)]
    for item_id in args.ids:
        values.extend(["--id", item_id])
    if args.include_reverse:
        values.append("--include-reverse")
    if args.execution_state:
        values.extend(["--execution-state", str(args.execution_state)])
    return run_script("query_product_truth.py", values)


def triage_requirement(args: argparse.Namespace) -> int:
    values = [str(args.input), "--format", args.format]
    if args.output:
        values.extend(["--output", str(args.output)])
    return run_script("triage_requirement.py", values)


def analyze_change(args: argparse.Namespace) -> int:
    values = ["--truth", str(args.truth), "--change", str(args.change), "--max-depth", str(args.max_depth)]
    if args.output:
        values.extend(["--output", str(args.output)])
    return run_script("analyze_change_impact.py", values)


def build_trace(args: argparse.Namespace) -> int:
    return run_script("build_traceability_ledger.py", ["--truth", str(args.truth), "--output", str(args.output), "--baseline-version", args.baseline_version])


def score_eval(args: argparse.Namespace) -> int:
    values = [str(args.run)]
    if args.output:
        values.extend(["--output", str(args.output)])
    if args.require_release_pass:
        values.append("--require-release-pass")
    if args.quiet:
        values.append("--quiet")
    return run_repo_tool("maintainer/tools/score_evaluation_run.py", values)


def compare_evals(args: argparse.Namespace) -> int:
    values = ["--baseline", str(args.baseline), "--candidate", str(args.candidate)]
    if args.output:
        values.extend(["--output", str(args.output)])
    return run_repo_tool("maintainer/tools/compare_evaluation_runs.py", values)


def status_report(args: argparse.Namespace) -> int:
    coverage = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
    fixtures = yaml.safe_load((ROOT / "maintainer/evals/domain-fixtures.yaml").read_text(encoding="utf-8"))
    github_cases = yaml.safe_load((ROOT / "maintainer/evals/github-cases.yaml").read_text(encoding="utf-8"))
    matrix = yaml.safe_load((ROOT / "maintainer/evals/evidence/github-validation-matrix.yaml").read_text(encoding="utf-8"))
    catalog = yaml.safe_load((ROOT / "maintainer/evals/eval-catalog.yaml").read_text(encoding="utf-8"))
    lifecycle_forward = yaml.safe_load((ROOT / "maintainer/evals/evidence/v517-lifecycle-forward-test-2026-07-15.yaml").read_text(encoding="utf-8"))
    maturity: dict[str, int] = {}
    practice: dict[str, int] = {}
    for domain in coverage.get("domains", []):
        maturity[domain["maturity"]] = maturity.get(domain["maturity"], 0) + 1
        practice[domain["practice_status"]] = practice.get(domain["practice_status"], 0) + 1
    eval_status: dict[str, int] = {}
    for scenario in catalog.get("scenarios", []):
        eval_status[scenario["status"]] = eval_status.get(scenario["status"], 0) + 1
    report = {
        "schema_version": "5.3.0",
        "skill_version": current_version(),
        "runtime": "pure_v5",
        "domain_packs": {
            "count": len(coverage.get("domains", [])),
            "maturity": maturity,
            "practice_status": practice,
            "production_claims_allowed": sum(
                domain.get("production_claim") == "allowed" for domain in coverage.get("domains", [])
            ),
        },
        "evaluation_assets": {
            "domain_fixtures": len(fixtures.get("fixtures", [])),
            "contract_fixtures_passed": sum(
                fixture.get("status") == "passed" for fixture in fixtures.get("fixtures", [])
            ),
            "github_cases": len(github_cases.get("cases", [])),
            "lifecycle_forward_test_cases": len(lifecycle_forward.get("cases", [])),
            "catalog_status": eval_status,
            "github_matrix": matrix.get("summary", {}),
        },
        "known_limitations": [
            "five domain methods have owner-attested production practice; all built-in packs pass deterministic contract checks but fresh-agent/expert maturity remains separate",
            "GitHub runs are exploratory and have zero release-passed cells",
            "domain expert, customer, production, legal, safety, and financial correctness are not proven",
            "lifecycle simulations and private brownfield calibration expose method gaps but do not prove implementation or customer acceptance",
        ],
    }
    if args.format == "yaml":
        rendered = yaml.safe_dump(report, allow_unicode=True, sort_keys=False)
    else:
        matrix_summary = report["evaluation_assets"]["github_matrix"]
        rendered = (
            "# AI Delivery Spec Status\n\n"
            f"- Version: `{report['skill_version']}` (`pure_v5`)\n"
            f"- Domain packs: {report['domain_packs']['count']}; maturity: `{maturity}`\n"
            f"- Delivery practice: `{practice}`\n"
            f"- Production claims allowed by built-in packs: {report['domain_packs']['production_claims_allowed']}\n"
            f"- Domain fixtures: {report['evaluation_assets']['domain_fixtures']}\n"
            f"- Pinned GitHub cases: {report['evaluation_assets']['github_cases']}\n"
            f"- GitHub stage cells: passed={matrix_summary.get('passed', 0)}, "
            f"partial={matrix_summary.get('partial', 0)}, not_run={matrix_summary.get('not_run', 0)}\n\n"
            "## Known limitations\n\n"
            + "".join(f"- {item}\n" for item in report["known_limitations"])
        )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"PASS: wrote status report to {args.output}")
    else:
        print(rendered, end="")
    return 0


def compile_discovery(args: argparse.Namespace) -> int:
    return run_script(
        "compile_clarification_transcript.py",
        [
            "--contract", str(args.contract), "--transcript", str(args.transcript),
            "--decision", args.decision, "--output", str(args.output),
        ],
    )


def compile_truth(args: argparse.Namespace) -> int:
    values = ["--index", str(args.index)]
    if args.output:
        values.extend(["--output", str(args.output)])
    if args.allow_incomplete:
        values.append("--allow-incomplete")
    return run_script("compile_product_truth.py", values)


def quality_gate(args: argparse.Namespace) -> int:
    values = [
        "--profile", args.profile, "--level", args.level, "--stage", args.stage,
        "--format", args.format, "--diagnostics", args.diagnostics,
        "--max-findings", str(args.max_findings),
    ]
    for scope_ref in args.scope_ref:
        values.extend(["--scope-ref", scope_ref])
    if args.custom_root:
        values.extend(["--custom-root", str(args.custom_root)])
    for name in ("requirement", "prd", "prototype", "inventory", "manifest", "acceptance_run"):
        value = getattr(args, name)
        if isinstance(value, list):
            for item in value:
                values.extend([f"--{name}", str(item)])
        elif value:
            values.extend([f"--{name}", str(value)])
    return run_script("quality_gate.py", values)


def query_domain(args: argparse.Namespace) -> int:
    values = ["--domain", args.domain, "--format", args.format]
    if args.custom_root:
        values.extend(["--custom-root", str(args.custom_root)])
    for section in args.section:
        values.extend(["--section", section])
    return run_script("query_domain.py", values)


def validate_candidate(args: argparse.Namespace) -> int:
    try:
        document = yaml.safe_load(args.input.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        print(f"BLOCKED: 候选知识无法读取：{exc}")
        return 2
    schema = json.loads((ROOT / "schemas/domain-candidate.schema.json").read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
        key=lambda error: tuple(str(part) for part in error.path),
    )
    failures = [f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors]
    if isinstance(document, dict):
        scope = document.get("reuse_scope")
        if document.get("sensitive_data") is True and scope != "project_only":
            failures.append("敏感数据候选只能使用 reuse_scope=project_only")
        if scope in {"organization", "public_candidate"}:
            approver = document.get("reuse_approver")
            if not approver:
                failures.append("组织/公共候选必须声明 reuse_approver")
            if approver in {document.get("submitted_by"), document.get("decision_owner")}:
                failures.append("reuse_approver 必须与 submitted_by/decision_owner 职责分离")
        if document.get("status") in {"confirmed", "corroborated"} and not document.get("reuse_approver"):
            failures.append("corroborated/confirmed 候选缺少独立 reuse_approver")
    if failures:
        for failure in failures:
            print(f"BLOCK: CANDIDATE-INVALID: {failure}")
        return 2
    print(f"PASS: 候选知识结构有效，范围={document.get('reuse_scope')}，未执行自动晋升")
    return 0


def explain_finding(args: argparse.Namespace) -> int:
    from quality_gate import guidance_for, repair_example_for

    cause, how_to_fix = guidance_for(args.code)
    example = repair_example_for(args.code)
    payload = {"code": args.code, "cause": cause, "how_to_fix": how_to_fix, "repair_example": example}
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{args.code}\n原因: {cause}\n修复: {how_to_fix}\n示例: {example}")
    return 0


def resume_execution(args: argparse.Namespace) -> int:
    state = args.state
    if state is None:
        candidates = []
        for pattern in (
            "delivery/evidence/execution-state.yaml",
            "requirements/evidence/execution-state.yaml",
            "*/evidence/execution-state.yaml",
            ".ai-delivery-spec/checkpoints/*.yaml",
        ):
            candidates.extend(path for path in Path.cwd().glob(pattern) if path.is_file())
        if not candidates:
            print("BLOCKED: 未自动发现执行快照；请用 --state 指定 execution-state.yaml")
            return 2
        state = max(set(candidates), key=lambda path: path.stat().st_mtime)
        print(f"INFO: 自动选择最近快照 {state}")
    return run_script("manage_execution_state.py", ["resume", "--state", str(state)])


def main() -> int:
    parser = argparse.ArgumentParser(prog="ai_delivery_spec_cli.py")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init-delivery", help="Create a resumable delivery/ package layout")
    init.add_argument("--output", type=Path, default=Path("delivery"))
    init.add_argument("--force", action="store_true", help="Overwrite manifest.json skeleton if it exists")
    init.add_argument(
        "--truth-layout", choices=["progressive", "monolith"], default="progressive",
        help="Use small checkpointable fragments by default; monolith is for bounded projects only",
    )
    init.set_defaults(func=init_delivery)

    req_init = sub.add_parser("init-requirements", help="Create a focused intake-to-acceptance requirement workspace")
    req_init.add_argument("--output", type=Path, default=Path("requirements"))
    req_init.add_argument("--force", action="store_true")
    req_init.add_argument("--with-product-truth", action="store_true", help="Add progressive Product Truth only for scale/audit needs")
    req_init.add_argument("--template", help="项目本地模板名（custom/templates/<name>.md）")
    req_init.add_argument("--custom-root", type=Path, default=Path("custom"))
    req_init.set_defaults(func=init_requirements)

    custom = sub.add_parser("init-custom", help="创建默认不提交的本地领域包、模板和声明式校验规则")
    custom.add_argument("--output", type=Path, default=Path("custom"))
    custom.add_argument("--force", action="store_true")
    custom.set_defaults(func=init_custom)

    check = sub.add_parser("check", help="Run the maintainer assurance suite and optional artifact validators")
    check.add_argument("--product-truth", type=Path)
    check.add_argument("--keep-going", action="store_true")
    check.set_defaults(func=run_check)

    gate = sub.add_parser("gate", help="Run the token-free final requirement/PRD/prototype goalkeeper")
    gate.add_argument("--profile", choices=["requirement", "prd", "prototype", "handoff", "full", "stage0", "agent_handoff"], required=True)
    gate.add_argument("--requirement", type=Path)
    gate.add_argument("--prd", type=Path)
    gate.add_argument("--prototype", type=Path, action="append", help="Repeat for admin/H5/multi-surface prototypes")
    gate.add_argument("--inventory", type=Path, help="Stage 0 brownfield inventory YAML")
    gate.add_argument("--manifest", type=Path, help="Agent handoff manifest YAML")
    gate.add_argument("--acceptance-run", type=Path, action="append", help="已执行的 ARUN-*；L3/L4 原型据此闭合浏览器证据")
    gate.add_argument("--level", choices=["auto", "L0", "L1", "L2", "L3", "L4"], default="auto")
    gate.add_argument("--stage", choices=["inventory", "clarify", "specify", "review", "baseline", "prototype", "implementation", "acceptance", "closed"], default="baseline")
    gate.add_argument("--scope-ref", action="append", default=[])
    gate.add_argument("--format", choices=["concise", "json"], default="concise")
    gate.add_argument("--diagnostics", choices=["first", "summary", "full"], default="first")
    gate.add_argument("--max-findings", type=int, default=20)
    gate.add_argument("--custom-root", type=Path, help="本地私有扩展目录；省略时门禁自动发现当前目录 custom/")
    gate.set_defaults(func=quality_gate)

    explain = sub.add_parser("explain-finding", help="Explain one gate code and show a bounded repair direction")
    explain.add_argument("code")
    explain.add_argument("--format", choices=["concise", "json"], default="concise")
    explain.set_defaults(func=explain_finding)

    resume = sub.add_parser("resume", help="Verify and resume from the last valid large-project checkpoint")
    resume.add_argument("--state", type=Path, help="省略时自动选择约定目录中最近的快照")
    resume.set_defaults(func=resume_execution)

    context = sub.add_parser("plan-context", help="Create an adaptive context and assurance plan")
    context.add_argument("--truth", type=Path, required=True)
    context.add_argument("--config", type=Path, default=ROOT / "examples/spec.config.example.yaml")
    context.add_argument("--seed-id", action="append", default=[])
    context.add_argument("--output", type=Path)
    context.set_defaults(func=plan_context)

    query = sub.add_parser("query-truth", help="Extract a Product Truth working slice by stable ID")
    query.add_argument("--truth", type=Path, required=True)
    query.add_argument("--id", dest="ids", action="append", required=True)
    query.add_argument("--include-reverse", action="store_true")
    query.add_argument("--execution-state", type=Path)
    query.add_argument("--output", type=Path, required=True)
    query.set_defaults(func=query_truth)

    domain = sub.add_parser("query-domain", help="Load one compact domain record or exact section")
    domain.add_argument("--domain", required=True)
    domain.add_argument("--format", choices=["yaml", "markdown"], default="yaml")
    domain.add_argument("--section", action="append", default=[])
    domain.add_argument("--custom-root", type=Path, default=Path("custom"))
    domain.set_defaults(func=query_domain)

    candidate = sub.add_parser("candidate", help="Validate a project-local knowledge candidate; never auto-promote")
    candidate_sub = candidate.add_subparsers(dest="candidate_command", required=True)
    candidate_validate = candidate_sub.add_parser("validate")
    candidate_validate.add_argument("--input", type=Path, required=True)
    candidate_validate.set_defaults(func=validate_candidate)

    triage = sub.add_parser("triage", help="Recommend requirement intake decision, priority, mode and tier")
    triage.add_argument("--input", type=Path, required=True)
    triage.add_argument("--format", choices=["markdown", "yaml", "json"], default="markdown")
    triage.add_argument("--output", type=Path)
    triage.set_defaults(func=triage_requirement)

    impact = sub.add_parser("impact", help="Analyze bidirectional change impact from seed IDs")
    impact.add_argument("--truth", type=Path, required=True)
    impact.add_argument("--change", type=Path, required=True)
    impact.add_argument("--output", type=Path)
    impact.add_argument("--max-depth", type=int, default=4)
    impact.set_defaults(func=analyze_change)

    trace = sub.add_parser("trace", help="Build a bidirectional traceability ledger")
    trace.add_argument("--truth", type=Path, required=True)
    trace.add_argument("--output", type=Path, required=True)
    trace.add_argument("--baseline-version", default="unversioned")
    trace.set_defaults(func=build_trace)

    score = sub.add_parser("score-eval", help="Maintainer: score one requirement/design/coding evaluation run")
    score.add_argument("run", type=Path)
    score.add_argument("--output", type=Path)
    score.add_argument("--require-release-pass", action="store_true")
    score.add_argument("--quiet", action="store_true")
    score.set_defaults(func=score_eval)

    compare = sub.add_parser("compare-evals", help="Maintainer: compare matched baseline and candidate evaluation runs")
    compare.add_argument("--baseline", type=Path, required=True)
    compare.add_argument("--candidate", type=Path, required=True)
    compare.add_argument("--output", type=Path)
    compare.set_defaults(func=compare_evals)

    status = sub.add_parser("status", help="Maintainer: show evidence-backed domain and evaluation status")
    status.add_argument("--format", choices=["markdown", "yaml"], default="markdown")
    status.add_argument("--output", type=Path)
    status.set_defaults(func=status_report)

    compile_cmd = sub.add_parser("compile-discovery", help="Compile structured clarification turns into Discovery Contract")
    compile_cmd.add_argument("--contract", type=Path, required=True)
    compile_cmd.add_argument("--transcript", type=Path, required=True)
    compile_cmd.add_argument(
        "--decision",
        choices=["READY_FOR_LIGHT_SPEC", "READY_FOR_UNIFIED_PRD", "READY_FOR_PRODUCT_TRUTH", "READY_FOR_CHANGE_PACKAGE", "REVIEW_COMPLETE_WITH_GAPS", "BLOCKED_BY_P0_UNKNOWN"],
        required=True,
    )
    compile_cmd.add_argument("--output", type=Path, required=True)
    compile_cmd.set_defaults(func=compile_discovery)

    truth_cmd = sub.add_parser("compile-truth", help="Compile and validate progressive Product Truth fragments")
    truth_cmd.add_argument("--index", type=Path, required=True)
    truth_cmd.add_argument("--output", type=Path)
    truth_cmd.add_argument("--allow-incomplete", action="store_true")
    truth_cmd.set_defaults(func=compile_truth)

    version = sub.add_parser("version", help="Print AI Delivery Spec version")
    version.set_defaults(func=lambda _args: print(current_version()) or 0)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
