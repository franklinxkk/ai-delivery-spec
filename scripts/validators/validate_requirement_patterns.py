#!/usr/bin/env python3
"""Validate reusable requirement patterns as bounded assets, not prose snippets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/requirement-pattern-library.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    doc = yaml.safe_load(args.document.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    failures = [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(doc)
    ]
    ids = [item.get("id") for item in doc.get("patterns", [])] if isinstance(doc, dict) else []
    if len(ids) != len(set(ids)):
        failures.append("duplicate pattern IDs")
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: Requirement Pattern Library contains {len(ids)} reusable governed patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
