#!/usr/bin/env python3
"""Validate bidirectional trace indexes and reject unexplained error orphans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "traceability-ledger.schema.json"


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
    forward = doc.get("forward_index", {}) if isinstance(doc, dict) else {}
    reverse = doc.get("reverse_index", {}) if isinstance(doc, dict) else {}
    for edge in doc.get("edges", []) if isinstance(doc, dict) else []:
        source, target = edge.get("from_id"), edge.get("to_id")
        if target not in forward.get(source, []):
            failures.append(f"forward index missing {source} -> {target}")
        if source not in reverse.get(target, []):
            failures.append(f"reverse index missing {target} <- {source}")
    errors = [item.get("id") for item in doc.get("orphans", []) if item.get("classification") == "error"]
    if errors:
        failures.append("unresolved traceability orphans: " + ", ".join(errors))
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: Traceability Ledger is bidirectionally closed ({len(doc.get('edges', []))} edges)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
