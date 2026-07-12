#!/usr/bin/env python3
"""Validate pinned, multi-domain GitHub evaluation cases."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals/github-cases.yaml"
SOURCE_EVIDENCE = ROOT / "evals/evidence/github-source-verification-2026-07-11.yaml"


def main() -> int:
    catalog = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas/eval-case.schema.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in validator.iter_errors(catalog):
        path = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"schema {path}: {error.message}")

    case_ids: set[str] = set()
    obligation_ids: set[str] = set()
    domains: set[str] = set()
    shapes: set[str] = set()
    for case in catalog.get("cases", []):
        case_id = case.get("id")
        if case_id in case_ids:
            failures.append(f"duplicate case id: {case_id}")
        case_ids.add(case_id)
        domains.add(case.get("domain", ""))
        shapes.add(case.get("shape", ""))
        issue_url = case.get("source_issue", {}).get("url", "")
        if not issue_url.startswith("https://github.com/") or "/issues/" not in issue_url:
            failures.append(f"{case_id} source issue is not a GitHub issue URL")
        ref = case.get("pinned_ref", "")
        for path in case.get("source_paths", []):
            if path.startswith("http"):
                failures.append(f"{case_id} source_paths must be repository-relative: {path}")
            if not path.strip():
                failures.append(f"{case_id} contains an empty source path")
        for stage, obligations in case.get("stages", {}).items():
            priorities = {item.get("priority") for item in obligations}
            if "P0" not in priorities:
                failures.append(f"{case_id}/{stage} has no P0 obligation")
            for obligation in obligations:
                obligation_id = obligation.get("id")
                if obligation_id in obligation_ids:
                    failures.append(f"duplicate obligation id: {obligation_id}")
                obligation_ids.add(obligation_id)
        if len(ref) != 40:
            failures.append(f"{case_id} is not pinned to a full commit SHA")

    if len(domains) < 6:
        failures.append("GitHub cases must cover at least six distinct domains")
    if "brownfield" not in shapes:
        failures.append("GitHub cases must exercise brownfield delivery")

    if not SOURCE_EVIDENCE.exists():
        failures.append("missing online GitHub source verification evidence")
    else:
        evidence = yaml.safe_load(SOURCE_EVIDENCE.read_text(encoding="utf-8"))
        verified = {row.get("case_id"): row for row in evidence.get("cases", [])}
        if evidence.get("result") != "passed":
            failures.append("online GitHub source verification is not passed")
        for case_id in case_ids:
            row = verified.get(case_id, {})
            if not all(row.get(field) for field in ("pinned_ref_reachable", "source_paths_exist", "issue_reachable")):
                failures.append(f"{case_id} lacks complete pinned source verification")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(
        f"PASS: {len(case_ids)} pinned GitHub cases cover {len(domains)} domains "
        f"and {len(obligation_ids)} requirement/design/coding obligations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
