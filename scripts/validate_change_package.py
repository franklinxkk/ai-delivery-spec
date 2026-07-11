#!/usr/bin/env python3
"""Validate a v5 Change Package and its release/evidence semantics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
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
    if status in {"verified", "released"} and result != "passed":
        failures.append(f"{status} change requires passed verification, got {result}")
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
