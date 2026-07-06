#!/usr/bin/env python3
"""Small helper CLI for AI Delivery Spec delivery packages."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


DELIVERY_DIRS = (
    "prd",
    "prd/contracts",
    "prototype",
    "acceptance",
    "agents",
    "evidence",
)


def current_version() -> str:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    marker = "Production Elastic Delivery Standard (v"
    start = text.find(marker)
    if start == -1:
        return "unknown"
    start += len(marker)
    end = text.find(")", start)
    return text[start:end] if end != -1 else "unknown"


def init_delivery(args: argparse.Namespace) -> int:
    target = args.output.resolve()
    target.mkdir(parents=True, exist_ok=True)
    for rel in DELIVERY_DIRS:
        (target / rel).mkdir(parents=True, exist_ok=True)

    manifest = target / "manifest.json"
    if not manifest.exists() or args.force:
        payload = {
            "version": "1.0.0",
            "generated_by": f"ai-delivery-spec v{current_version()}",
            "artifacts": [],
        }
        manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"initialized delivery package: {target}")
    return 0


def run_check(args: argparse.Namespace) -> int:
    commands: list[list[str]] = [
        [sys.executable, "scripts/validate_skill_consistency.py"],
        [sys.executable, "scripts/validate_routing_scenarios.py"],
        [sys.executable, "scripts/validate_release_readiness.py"],
        [sys.executable, "scripts/validate_ai_data_product_scenarios.py"],
        [sys.executable, "scripts/validate_current_release_contracts.py"],
        [sys.executable, "scripts/validate_multi_agent_lifecycle_scenarios.py"],
        [sys.executable, "scripts/validate_domain_isolation.py"],
    ]
    if args.prd:
        cmd = [sys.executable, "scripts/validate_prd_quality.py", str(args.prd)]
        if args.target_language:
            cmd += ["--target-language", args.target_language]
        commands.append(cmd)
    if args.ia_skeleton and args.prototype and args.prd:
        commands.append(
            [
                sys.executable,
                "scripts/validate_ia_skeleton.py",
                "--ia-skeleton",
                str(args.ia_skeleton),
                "--prototype",
                str(args.prototype),
                "--prd",
                str(args.prd),
            ]
        )
    if args.prototype and args.prd:
        commands.append(
            [
                sys.executable,
                "scripts/validate_coding_agent_contract.py",
                "--prd",
                str(args.prd),
                "--prototype",
                str(args.prototype),
            ]
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


def main() -> int:
    parser = argparse.ArgumentParser(prog="ai_delivery_spec_cli.py")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init-delivery", help="Create the standard delivery/ package layout")
    init.add_argument("--output", type=Path, default=Path("delivery"))
    init.add_argument("--force", action="store_true", help="Overwrite manifest.json skeleton if it exists")
    init.set_defaults(func=init_delivery)

    check = sub.add_parser("check", help="Run skill and optional PRD/prototype validators")
    check.add_argument("--prd", type=Path)
    check.add_argument("--prototype", type=Path)
    check.add_argument("--ia-skeleton", type=Path)
    check.add_argument("--target-language", choices=("zh", "en", "none"))
    check.add_argument("--keep-going", action="store_true")
    check.set_defaults(func=run_check)

    version = sub.add_parser("version", help="Print AI Delivery Spec version")
    version.set_defaults(func=lambda _args: print(current_version()) or 0)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
