#!/usr/bin/env python3
"""Validate a v5 Change Package and its release/evidence semantics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from change_package_contract import ChangeContractError, iter_impact_objects, load_yaml_mapping


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "change-package.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    try:
        document = load_yaml_mapping(args.document, label="change package")
    except ChangeContractError as exc:
        print(f"FAIL: {exc}")
        return 1
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    failures = [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document)
    ]
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    status = document.get("status")
    result = document.get("verification", {}).get("result")
    if status in {"verified", "baselined", "released"} and result != "passed":
        failures.append(f"{status} change requires passed verification, got {result}")
    if document.get("schema_version") == "5.1.0":
        approvals = document.get("approvals", [])
        if status in {"approved", "synchronized", "verified", "baselined", "implemented", "released"} and not approvals:
            failures.append(f"{status} change requires approval records")
        invalid_approvals = [item.get("role") for item in approvals if item.get("decision") not in {"approved", "approved_with_conditions"}]
        if status in {"approved", "synchronized", "verified", "baselined", "implemented", "released"} and invalid_approvals:
            failures.append("change has non-approved decisions: " + ", ".join(invalid_approvals))
        if status in {"approved", "synchronized", "verified", "baselined", "implemented", "released"} and not document.get("diff"):
            failures.append(f"{status} change requires a before/after diff")
        if status in {"synchronized", "verified", "baselined", "implemented", "released"}:
            synchronization = document.get("synchronization", [])
            if not synchronization:
                failures.append(f"{status} change requires versioned consumer synchronization records")
            pending = [item.get("consumer") for item in synchronization if item.get("status") not in {"sent", "acknowledged"}]
            if pending:
                failures.append("change has unsynchronized consumers: " + ", ".join(pending))
        if status == "baselined" and document.get("baseline_version") == document.get("target_version"):
            failures.append("baselined change must advance target_version from baseline_version")
    migration = document.get("impacts", {}).get("data_migration", {})
    required = migration.get("required")
    decided = {"approved", "synchronized", "verified", "baselined", "implemented", "released"}
    meaningful = lambda value: isinstance(value, str) and value.strip().casefold() not in {"", "unknown", "not_applicable", "n/a", "待定", "待补", "无"}
    if required is True and not all(meaningful(migration.get(key)) for key in ("strategy", "rollback")):
        failures.append("data migration requires real strategy and rollback; not_applicable is not a migration plan")
    if required in (None, "unknown") and status in decided:
        failures.append("migration is unknown: retain the draft or record its decision/scope before advancing the dependent change")
    if required is False and status in decided and not meaningful(migration.get("decision_ref")):
        failures.append("no-migration decision needs its existing source/decision reference; a legacy false alone is not approval")
    if result == "passed" and not document.get("verification", {}).get("evidence_refs"):
        failures.append("passed verification needs evidence_refs; keep not_run until execution is evidenced")
    for approval in document.get("approvals", []):
        if approval.get("decision") == "approved_with_conditions" and not meaningful(approval.get("conditions")):
            failures.append("conditional approval needs its actual conditions")
    if status in decided and any(a.get("decision") in {"pending", "rejected"} for a in document.get("approvals", [])):
        failures.append("the current change conclusion conflicts with its pending/rejected approval")

    try:
        removed = [
            item["ref"]
            for _group, _index, item in iter_impact_objects(document)
            if item.get("change_type") == "remove"
        ]
    except ChangeContractError as exc:  # defensive for direct/legacy callers
        failures.append(str(exc))
        removed = []
    replacements = document.get("compatibility", {}).get("replacement_map", {})
    missing_replacement = [item for item in removed if item not in replacements]
    if missing_replacement:
        failures.append("removed IDs lack replacement map: " + ", ".join(missing_replacement))

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: Change Package {document.get('change_id')} has consistent declarations status={status}/{result}; execution and authorization authenticity are not certified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
