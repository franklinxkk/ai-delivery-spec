#!/usr/bin/env python3
"""Validate a v5 Change Package and its release/evidence semantics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "change-package.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    document = yaml.safe_load(args.document.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    failures = [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document)
    ]

    status = document.get("status")
    result = document.get("verification", {}).get("result")
    if status in {"verified", "baselined", "released"} and result != "passed":
        failures.append(f"{status} change requires passed verification, got {result}")
    if document.get("schema_version") == "5.1.0":
        approvals = document.get("approvals", [])
        if status in {"approved", "synchronized", "verified", "baselined"} and not approvals:
            failures.append(f"{status} change requires approval records")
        invalid_approvals = [item.get("role") for item in approvals if item.get("decision") not in {"approved", "approved_with_conditions"}]
        if status in {"approved", "synchronized", "verified", "baselined"} and invalid_approvals:
            failures.append("change has non-approved decisions: " + ", ".join(invalid_approvals))
        if status in {"approved", "synchronized", "verified", "baselined"} and not document.get("diff"):
            failures.append(f"{status} change requires a before/after diff")
        if status in {"synchronized", "verified", "baselined"}:
            synchronization = document.get("synchronization", [])
            if not synchronization:
                failures.append(f"{status} change requires versioned consumer synchronization records")
            pending = [item.get("consumer") for item in synchronization if item.get("status") not in {"sent", "acknowledged"}]
            if pending:
                failures.append("change has unsynchronized consumers: " + ", ".join(pending))
        if status == "baselined" and document.get("baseline_version") == document.get("target_version"):
            failures.append("baselined change must advance target_version from baseline_version")
    if document.get("impacts", {}).get("data_migration", {}).get("required"):
        migration = document["impacts"]["data_migration"]
        if not migration.get("strategy") or not migration.get("rollback"):
            failures.append("data migration requires strategy and rollback")
    removed = [
        item["ref"]
        for group, items in document.get("impacts", {}).items()
        if isinstance(items, list)
        for item in items
        if item.get("change_type") == "remove"
    ]
    replacements = document.get("compatibility", {}).get("replacement_map", {})
    missing_replacement = [item for item in removed if item not in replacements]
    if missing_replacement:
        failures.append("removed IDs lack replacement map: " + ", ".join(missing_replacement))

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: Change Package {document.get('change_id')} is schema-valid with honest status={status}/{result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
