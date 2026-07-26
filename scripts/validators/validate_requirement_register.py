#!/usr/bin/env python3
"""Validate requirement semantics and optionally print a delivery-lead portfolio view."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "requirement-register.schema.json"


def portfolio_summary(document: dict, requirements: list[dict]) -> dict:
    iterations = {
        str(item.get("id")): str(item.get("name"))
        for item in document.get("iterations", [])
        if item.get("id")
    }
    by_iteration = Counter()
    for item in requirements:
        iteration_ref = str(item.get("iteration_ref") or "UNASSIGNED")
        label = f"{iteration_ref}｜{iterations.get(iteration_ref, '未分配')}"
        by_iteration[label] += 1
    dependency_edges = document.get("dependency_edges", [])
    blocking_targets = sorted({
        str(edge.get("to_ref")) for edge in dependency_edges
        if edge.get("kind") in {"blocks", "depends_on"} and edge.get("to_ref")
    })
    return {
        "total": len(requirements),
        "by_stage": dict(sorted(Counter(str(item.get("stage")) for item in requirements).items())),
        "by_priority": dict(sorted(Counter(str(item.get("priority")) for item in requirements).items())),
        "by_complexity": dict(sorted(Counter(str(item.get("complexity", {}).get("band")) for item in requirements).items())),
        "by_iteration": dict(sorted(by_iteration.items())),
        "requirements_with_dependencies": sorted(
            str(item.get("id")) for item in requirements if item.get("dependency_refs")
        ),
        "dependency_targets": blocking_targets,
        "unassigned_iteration": sorted(
            str(item.get("id")) for item in requirements if not item.get("iteration_ref")
        ),
        "decision_boundary": (
            "本视图只汇总优先级、复杂度带、依赖和迭代归属；"
            "不估算人日、不分配 Sprint/人员，也不替代产品价值或工程容量决策。"
        ),
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--summary", action="store_true", help="输出需求池聚合视图，不接管排期或容量")
    args = parser.parse_args()
    doc = yaml.safe_load(args.document.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    failures = [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(doc)
    ]
    requirements = doc.get("requirements", []) if isinstance(doc, dict) else []
    ids = [item.get("id") for item in requirements]
    duplicates = sorted(item for item, count in Counter(ids).items() if item and count > 1)
    if duplicates:
        failures.append("duplicate requirement IDs: " + ", ".join(duplicates))
    known = set(ids)
    for item in requirements:
        stage = item.get("stage")
        if stage in {"baselined", "change_requested", "acceptance", "accepted", "closed"}:
            if not item.get("behavior_refs"):
                failures.append(f"{item.get('id')} at {stage} has no behavior_refs")
            if not item.get("acceptance_refs"):
                failures.append(f"{item.get('id')} at {stage} has no acceptance_refs")
        if stage in {"accepted", "closed"} and not item.get("external_milestones"):
            failures.append(f"{item.get('id')} at {stage} has no acceptance/evidence milestone reference")
        for ref in item.get("dependency_refs", []):
            if ref not in known:
                failures.append(f"{item.get('id')} references unknown requirement dependency {ref}")
    for edge in doc.get("dependency_edges", []) if isinstance(doc, dict) else []:
        if edge.get("from_ref") not in known or edge.get("to_ref") not in known:
            failures.append(f"dependency edge is not requirement-closed: {edge.get('from_ref')} -> {edge.get('to_ref')}")
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: Requirement Register is valid ({len(requirements)} requirements, intake/baseline semantics closed)")
    if args.summary:
        print(yaml.safe_dump(
            {"requirement_portfolio_summary": portfolio_summary(doc, requirements)},
            allow_unicode=True, sort_keys=False,
        ).rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())