#!/usr/bin/env python3
"""Build or check the deterministic GitHub case-by-stage validation matrix."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from score_evaluation_run import score, validate_run


ROOT = Path(__file__).resolve().parents[1]
STAGES = ("requirement", "design", "coding_delivery")


def build() -> dict[str, Any]:
    catalog = yaml.safe_load((ROOT / "evals/github-cases.yaml").read_text(encoding="utf-8"))
    run_map: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted((ROOT / "evals/runs").glob("*.yaml")):
        run = yaml.safe_load(path.read_text(encoding="utf-8"))
        if validate_run(run):
            continue
        key = (run["case_id"], run["stage"])
        run_map[key] = {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "run": run}

    rows: list[dict[str, Any]] = []
    counts = {"not_run": 0, "partial": 0, "passed": 0}
    for case in catalog["cases"]:
        for stage in STAGES:
            found = run_map.get((case["id"], stage))
            if not found:
                status = "not_run"
                row = {
                    "case_id": case["id"],
                    "domain": case["domain"],
                    "stage": stage,
                    "status": status,
                    "run": None,
                    "release_pass": False,
                }
            else:
                result = score(found["run"])
                status = "passed" if result["release_pass"] else "partial"
                row = {
                    "case_id": case["id"],
                    "domain": case["domain"],
                    "stage": stage,
                    "status": status,
                    "run": found["path"],
                    "release_pass": result["release_pass"],
                }
            counts[status] += 1
            rows.append(row)
    return {
        "schema_version": "5.0.0",
        "matrix_type": "github_requirement_design_coding_validation",
        "summary": {"cases": len(catalog["cases"]), "stage_cells": len(rows), **counts},
        "rows": rows,
        "claim_boundary": (
            "A partial cell has one exploratory run only. A not_run cell has obligations but no execution evidence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if bool(args.output) == bool(args.check):
        parser.error("provide exactly one of --output or --check")
    document = build()
    rendered = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
    target = args.output or args.check
    if args.check:
        if not args.check.exists() or args.check.read_text(encoding="utf-8") != rendered:
            print(f"FAIL: GitHub validation matrix is stale: {args.check}")
            return 1
        print(
            "PASS: GitHub validation matrix is current "
            f"({document['summary']['partial']} partial, {document['summary']['not_run']} not_run)"
        )
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"PASS: wrote GitHub validation matrix to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
