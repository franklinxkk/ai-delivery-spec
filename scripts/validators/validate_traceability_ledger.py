#!/usr/bin/env python3
"""Validate bidirectional trace indexes and reject unexplained error orphans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "traceability-ledger.schema.json"
sys.path.insert(0, str(ROOT / "scripts"))
from truth_references import EXTERNAL_ID_PATTERNS


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
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    forward = doc.get("forward_index", {}) if isinstance(doc, dict) else {}
    reverse = doc.get("reverse_index", {}) if isinstance(doc, dict) else {}
    pairs = {(edge["from_id"], edge["to_id"]) for edge in doc["edges"]}
    for edge in doc.get("edges", []) if isinstance(doc, dict) else []:
        source, target = edge.get("from_id"), edge.get("to_id")
        if edge["source"] in EXTERNAL_ID_PATTERNS:
            failures.append(f"external locator in resolved edges: {source} {edge['source']}")
        if target not in forward.get(source, []):
            failures.append(f"forward index missing {source} -> {target}")
        if source not in reverse.get(target, []):
            failures.append(f"reverse index missing {target} <- {source}")
    for source, targets in forward.items():
        for target in targets:
            if (source, target) not in pairs:
                failures.append(f"forward index has no edge {source} -> {target}")
    for target, sources in reverse.items():
        for source in sources:
            if (source, target) not in pairs:
                failures.append(f"reverse index has no edge {target} <- {source}")
    for ref in doc.get("unresolved_refs", []):
        failures.append(f"unresolved reference {ref['from_id']} {ref['path']} -> {ref['to_id']}")
    for ref in doc.get("unverified_external_refs", []):
        pattern = EXTERNAL_ID_PATTERNS.get(ref["source"])
        if pattern is None or not pattern.fullmatch(ref["to_id"]):
            failures.append(f"invalid external locator at {ref['path']}")
    errors = [item.get("id") for item in doc.get("orphans", []) if item.get("classification") == "error"]
    if errors:
        failures.append("unresolved traceability orphans: " + ", ".join(errors))
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: bidirectional indexes match {len(doc['edges'])} recorded edges")
    if "unresolved_refs" not in doc:
        print("INFO: legacy ledger; rebuild from Product Truth to check for unresolved references")
    if doc.get("unverified_external_refs"):
        print(f"INFO: {len(doc['unverified_external_refs'])} external locators remain unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
