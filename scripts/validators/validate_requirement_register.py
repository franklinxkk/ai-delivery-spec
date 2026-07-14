#!/usr/bin/env python3
"""Validate requirement intake, stage, dependency and baseline semantics."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "requirement-register.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
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
            # Acceptance evidence lives in an external run/artifact reference.
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
