#!/usr/bin/env python3
"""Validate a v5 Product Truth document structurally and semantically."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "product-truth.schema.json"


def load_document(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def collect_ids(document: Any) -> tuple[set[str], list[str]]:
    values = [node["id"] for node in walk(document) if "id" in node and isinstance(node["id"], str)]
    values += [document["truth_id"]] if isinstance(document, dict) and document.get("truth_id") else []
    duplicates = [item for item, count in Counter(values).items() if count > 1]
    return set(values), duplicates


def collect_references(document: Any) -> list[tuple[str, str]]:
    references: list[tuple[str, str]] = []
    for node in walk(document):
        for key, value in node.items():
            if key.endswith("_ref") and isinstance(value, str):
                references.append((key, value))
            elif key.endswith("_refs") and isinstance(value, list):
                references.extend((key, item) for item in value if isinstance(item, str))
    return references


def semantic_failures(document: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    identifiers, duplicates = collect_ids(document)
    if duplicates:
        failures.append("duplicate stable IDs: " + ", ".join(sorted(duplicates)))

    for key, reference in collect_references(document):
        if reference not in identifiers:
            failures.append(f"unresolved {key}: {reference}")

    actions = {item["id"]: item for item in document.get("actions", [])}
    events = {item["id"]: item for item in document.get("events", [])}
    acceptance = {item["id"]: item for item in document.get("acceptance", [])}

    in_scope_features = [
        item for item in document.get("features", []) if item.get("scope_status") == "in_scope"
    ]
    unresolved_features = [
        item for item in document.get("features", []) if item.get("scope_status") in {"unknown", "deferred"}
    ]
    if not in_scope_features and not unresolved_features:
        failures.append("no approved or explicitly unresolved Feature IDs")
    for feature in in_scope_features:
        if not feature.get("source_refs"):
            failures.append(f"{feature['id']} has no source evidence")
        if not feature.get("behavior_refs"):
            failures.append(f"{feature['id']} has no behavior coverage")
        if not feature.get("acceptance_refs"):
            failures.append(f"{feature['id']} has no acceptance coverage")

    feature_behavior_refs = {
        reference for feature in document.get("features", []) for reference in feature.get("behavior_refs", [])
    }
    release_behavior_ids = {
        item["id"]
        for collection in ("modules", "flows", "views", "actions")
        for item in document.get(collection, [])
    }
    orphan_behavior = sorted(release_behavior_ids - feature_behavior_refs)
    if orphan_behavior:
        failures.append("delivery behavior has no Feature binding: " + ", ".join(orphan_behavior))

    feature_acceptance_refs = {
        reference for feature in document.get("features", []) for reference in feature.get("acceptance_refs", [])
    }
    orphan_acceptance = sorted(set(acceptance) - feature_acceptance_refs)
    if orphan_acceptance:
        failures.append("acceptance has no Feature binding: " + ", ".join(orphan_acceptance))

    for action_id, action in actions.items():
        if not action.get("visible_result", "").strip():
            failures.append(f"{action_id} has no visible result")
        if not action.get("domain_result", "").strip():
            failures.append(f"{action_id} has no domain result")
        for ac_ref in action.get("acceptance_refs", []):
            if ac_ref not in acceptance:
                failures.append(f"{action_id} references missing acceptance {ac_ref}")

    for machine in document.get("states", []):
        known_states = set(machine.get("states", []))
        for transition in machine.get("transitions", []):
            if transition.get("from") not in known_states:
                failures.append(f"{machine['id']} transition has unknown from state {transition.get('from')}")
            if transition.get("to") not in known_states:
                failures.append(f"{machine['id']} transition has unknown to state {transition.get('to')}")
            if transition.get("action_ref") not in actions:
                failures.append(f"{machine['id']} transition has unknown action {transition.get('action_ref')}")
            if transition.get("event_ref") and transition["event_ref"] not in events:
                failures.append(f"{machine['id']} transition has unknown event {transition['event_ref']}")

    for ac_id, criterion in acceptance.items():
        if not criterion.get("evidence_required"):
            failures.append(f"{ac_id} has no required evidence")
        if not criterion.get("expected_visible", "").strip():
            failures.append(f"{ac_id} has no expected visible result")
        if not criterion.get("expected_domain", "").strip():
            failures.append(f"{ac_id} has no expected domain result")

    p0_open = [
        item["id"]
        for item in document.get("unknowns", [])
        if item.get("status") in {"open", "blocked"}
        and item.get("impact") in {"scope", "compliance", "commercial", "risk"}
    ]
    if p0_open:
        failures.append("material unknowns remain open: " + ", ".join(p0_open))

    return failures


def validate(path: Path) -> int:
    document = load_document(path)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    failures = [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in schema_errors
    ]
    if isinstance(document, dict):
        failures.extend(semantic_failures(document))
    else:
        failures.append("Product Truth root must be an object")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    identifiers, _ = collect_ids(document)
    print(
        "PASS: Product Truth is schema-valid and reference-closed "
        f"({len(identifiers)} stable IDs, {len(document.get('features', []))} features, "
        f"{len(document.get('acceptance', []))} acceptance paths)"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    if not args.document.exists():
        print(f"FAIL: file not found: {args.document}")
        return 1
    return validate(args.document.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
