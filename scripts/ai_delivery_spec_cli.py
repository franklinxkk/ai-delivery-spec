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

import yaml


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


def current_version() -> str:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"AI Delivery Spec\s+(\d+\.\d+\.\d+)", text)
    return match.group(1) if match else "unknown"


def init_delivery(args: argparse.Namespace) -> int:
    target = args.output.resolve()
    target.mkdir(parents=True, exist_ok=True)
    for rel in DELIVERY_DIRS:
        (target / rel).mkdir(parents=True, exist_ok=True)

    config = target / "spec.config.yaml"
    if not config.exists():
        shutil.copyfile(ROOT / "spec.config.example.yaml", config)

    manifest = target / "manifest.json"
    if not manifest.exists() or args.force:
        payload = {
            "schema_version": "5.0.0",
            "generated_by": f"ai-delivery-spec v{current_version()}",
            "source_of_truth": "truth/product-truth.yaml",
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

    truth = target / "truth" / "product-truth.yaml"
    if not truth.exists() or args.force:
        shutil.copyfile(ROOT / "references" / "templates" / "product-truth-template.yaml", truth)

    print(f"initialized delivery package: {target}")
    return 0


def run_check(args: argparse.Namespace) -> int:
    commands: list[list[str]] = [
        [sys.executable, "scripts/validate_v5_architecture.py"],
        [sys.executable, "scripts/validate_spec_config.py", "spec.config.example.yaml"],
        [sys.executable, "scripts/validate_runtime_rule_uniqueness.py"],
        [sys.executable, "scripts/validate_domain_coverage.py"],
        [sys.executable, "scripts/validate_domain_sources.py"],
        [sys.executable, "scripts/validate_eval_catalog.py"],
        [sys.executable, "scripts/validate_github_eval_cases.py"],
        [sys.executable, "tests/test_v501_triage.py"],
        [sys.executable, "tests/test_v501_validators.py"],
        [
            sys.executable,
            "scripts/build_github_validation_matrix.py",
            "--check",
            "evals/evidence/github-validation-matrix.yaml",
        ],
        [sys.executable, "scripts/validate_release_claims.py"],
        [sys.executable, "scripts/test_context_planning.py"],
        [sys.executable, "scripts/test_evaluation_metrics.py"],
        [sys.executable, "scripts/test_execution_state.py"],
        [sys.executable, "scripts/test_cli_init.py"],
        [sys.executable, "tests/test_v5_agent_deadlock.py"],
        [sys.executable, "tests/test_v5_capsule_pollution.py"],
        [sys.executable, "tests/test_v5_change_drift.py"],
        [sys.executable, "tests/test_v5_schema_grill.py"],
        [sys.executable, "tests/test_v5_status.py"],
        [
            sys.executable,
            "scripts/validate_project_domain_capsule.py",
            "examples/generic-energy-capsule-v5/project-domain-capsule.yaml",
        ],
        [
            sys.executable,
            "scripts/validate_capsule_composition.py",
            "--capsule",
            "examples/generic-energy-capsule-v5/project-domain-capsule.yaml",
        ],
        [
            sys.executable,
            "scripts/validate_change_package.py",
            "examples/traffic-regulatory-change-v5/change-package.yaml",
        ],
        [
            sys.executable,
            "scripts/validate_product_truth.py",
            "examples/publishing-learning-v5/delivery/truth/product-truth.yaml",
        ],
        [
            sys.executable,
            "scripts/validate_projection_consistency.py",
            "--truth",
            "examples/publishing-learning-v5/delivery/truth/product-truth.yaml",
            "--projection",
            "examples/publishing-learning-v5/delivery/projections/human-first-prd.md",
        ],
        [
            sys.executable,
            "scripts/validate_projection_consistency.py",
            "--truth",
            "examples/publishing-learning-v5/delivery/truth/product-truth.yaml",
            "--projection",
            "examples/publishing-learning-v5/delivery/projections/coding-agent-spec.md",
        ],
        [sys.executable, "scripts/score_evaluation_run.py", "evals/runs/chatwoot-voice-requirement-v5.yaml", "--quiet"],
        [sys.executable, "scripts/score_evaluation_run.py", "evals/runs/saleor-channel-id-design-v5.yaml", "--quiet"],
        [sys.executable, "scripts/score_evaluation_run.py", "evals/runs/openedx-reindex-design-v5.yaml", "--quiet"],
        [sys.executable, "scripts/score_evaluation_run.py", "evals/runs/orangehrm-password-policy-handoff-v5.yaml", "--quiet"],
    ]
    if args.product_truth:
        commands.append(
            [sys.executable, "scripts/validate_product_truth.py", str(args.product_truth)]
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
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *values], cwd=ROOT, text=True).returncode


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


def score_eval(args: argparse.Namespace) -> int:
    values = [str(args.run)]
    if args.output:
        values.extend(["--output", str(args.output)])
    if args.require_release_pass:
        values.append("--require-release-pass")
    if args.quiet:
        values.append("--quiet")
    return run_script("score_evaluation_run.py", values)


def compare_evals(args: argparse.Namespace) -> int:
    values = ["--baseline", str(args.baseline), "--candidate", str(args.candidate)]
    if args.output:
        values.extend(["--output", str(args.output)])
    return run_script("compare_evaluation_runs.py", values)


def status_report(args: argparse.Namespace) -> int:
    coverage = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
    fixtures = yaml.safe_load((ROOT / "evals/domain-fixtures.yaml").read_text(encoding="utf-8"))
    github_cases = yaml.safe_load((ROOT / "evals/github-cases.yaml").read_text(encoding="utf-8"))
    matrix = yaml.safe_load((ROOT / "evals/evidence/github-validation-matrix.yaml").read_text(encoding="utf-8"))
    catalog = yaml.safe_load((ROOT / "evals/eval-catalog.yaml").read_text(encoding="utf-8"))
    maturity: dict[str, int] = {}
    for domain in coverage.get("domains", []):
        maturity[domain["maturity"]] = maturity.get(domain["maturity"], 0) + 1
    eval_status: dict[str, int] = {}
    for scenario in catalog.get("scenarios", []):
        eval_status[scenario["status"]] = eval_status.get(scenario["status"], 0) + 1
    report = {
        "schema_version": "5.0.0",
        "skill_version": current_version(),
        "runtime": "pure_v5",
        "domain_packs": {
            "count": len(coverage.get("domains", [])),
            "maturity": maturity,
            "production_claims_allowed": sum(
                domain.get("production_claim") == "allowed" for domain in coverage.get("domains", [])
            ),
        },
        "evaluation_assets": {
            "domain_fixtures": len(fixtures.get("fixtures", [])),
            "github_cases": len(github_cases.get("cases", [])),
            "catalog_status": eval_status,
            "github_matrix": matrix.get("summary", {}),
        },
        "known_limitations": [
            "built-in domain packs are experimental",
            "GitHub runs are exploratory and have zero release-passed cells",
            "domain expert, customer, production, legal, safety, and financial correctness are not proven",
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


def main() -> int:
    parser = argparse.ArgumentParser(prog="ai_delivery_spec_cli.py")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init-delivery", help="Create the standard delivery/ package layout")
    init.add_argument("--output", type=Path, default=Path("delivery"))
    init.add_argument("--force", action="store_true", help="Overwrite manifest.json skeleton if it exists")
    init.set_defaults(func=init_delivery)

    check = sub.add_parser("check", help="Run v5 architecture and optional artifact validators")
    check.add_argument("--product-truth", type=Path)
    check.add_argument("--keep-going", action="store_true")
    check.set_defaults(func=run_check)

    context = sub.add_parser("plan-context", help="Create an adaptive context and assurance plan")
    context.add_argument("--truth", type=Path, required=True)
    context.add_argument("--config", type=Path, default=ROOT / "spec.config.example.yaml")
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

    score = sub.add_parser("score-eval", help="Score one requirement/design/coding evaluation run")
    score.add_argument("run", type=Path)
    score.add_argument("--output", type=Path)
    score.add_argument("--require-release-pass", action="store_true")
    score.add_argument("--quiet", action="store_true")
    score.set_defaults(func=score_eval)

    compare = sub.add_parser("compare-evals", help="Compare matched baseline and candidate evaluation runs")
    compare.add_argument("--baseline", type=Path, required=True)
    compare.add_argument("--candidate", type=Path, required=True)
    compare.add_argument("--output", type=Path)
    compare.set_defaults(func=compare_evals)

    status = sub.add_parser("status", help="Show evidence-backed domain and evaluation status")
    status.add_argument("--format", choices=["markdown", "yaml"], default="markdown")
    status.add_argument("--output", type=Path)
    status.set_defaults(func=status_report)

    compile_cmd = sub.add_parser("compile-discovery", help="Compile structured clarification turns into Discovery Contract")
    compile_cmd.add_argument("--contract", type=Path, required=True)
    compile_cmd.add_argument("--transcript", type=Path, required=True)
    compile_cmd.add_argument(
        "--decision",
        choices=["READY_FOR_LIGHT_SPEC", "READY_FOR_PRODUCT_TRUTH", "READY_FOR_CHANGE_PACKAGE", "REVIEW_COMPLETE_WITH_GAPS", "BLOCKED_BY_P0_UNKNOWN"],
        required=True,
    )
    compile_cmd.add_argument("--output", type=Path, required=True)
    compile_cmd.set_defaults(func=compile_discovery)

    version = sub.add_parser("version", help="Print AI Delivery Spec version")
    version.set_defaults(func=lambda _args: print(current_version()) or 0)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
