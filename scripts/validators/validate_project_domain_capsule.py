#!/usr/bin/env python3
"""Validate a project-scoped generic-domain capsule."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "project-domain-capsule.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()

    document = yaml.safe_load(args.document.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    failures = [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(document)
    ]

    source_ids = {item["id"] for item in document.get("sources", [])}
    entity_ids = {item["id"] for item in document.get("entities", [])}
    state_ids = {item["id"] for item in document.get("state_machines", [])}
    context_names = {item["name"] for item in document.get("context_dictionary", [])}
    namespace = document.get("namespace", "")
    rule_prefix = "RULE-" + namespace.upper() + "-"
    for item in document.get("vocabulary", []):
        if item.get("source_ref") not in source_ids:
            failures.append(f"vocabulary source missing: {item.get('source_ref')}")
    for item in document.get("policies", []):
        if not item.get("id", "").startswith(rule_prefix):
            failures.append(f"policy ID must use capsule namespace {rule_prefix}: {item.get('id')}")
        if item.get("source_ref") not in source_ids:
            failures.append(f"policy source missing: {item.get('source_ref')}")
        if item.get("assertion_status") in {"inferred", "unknown"} and item.get("enforcement") == "backend_guard":
            failures.append(f"unverified policy cannot become backend guard: {item.get('id')}")
        referenced = set(item.get("listens_to", [])) | set(item.get("writes_to", []))
        missing_context = referenced - context_names
        if missing_context:
            failures.append(
                f"policy {item.get('id')} uses undefined context variables: {', '.join(sorted(missing_context))}"
            )
        placeholders = set(re.findall(r"{{\s*([A-Za-z][A-Za-z0-9_.-]*)\s*}}", item.get("prompt", "")))
        missing_placeholders = placeholders - context_names
        if missing_placeholders:
            failures.append(
                f"policy {item.get('id')} has undefined prompt placeholders: "
                + ", ".join(sorted(missing_placeholders))
            )
    for item in document.get("entities", []):
        if item.get("state_machine_ref") not in state_ids:
            failures.append(f"entity state machine missing: {item.get('id')}")
    for item in document.get("state_machines", []):
        if item.get("owner_ref") not in entity_ids:
            failures.append(f"state owner missing: {item.get('id')}")
    if document.get("promotion", {}).get("eligible") and any(
        item.get("assertion_status") in {"inferred", "unknown", "conflict"}
        for section in ("vocabulary", "entities", "policies")
        for item in document.get(section, [])
    ):
        failures.append("capsule cannot be promotion-eligible with unresolved professional assertions")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(
        "PASS: Project Domain Capsule is structured, project-scoped, and honest "
        f"({len(entity_ids)} entities, {len(document.get('scenario_fixtures', []))} scenarios)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
