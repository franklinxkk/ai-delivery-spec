#!/usr/bin/env python3
"""Validate review findings and block false completion with open P0/P1 items."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/review-record.schema.json"


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
    if doc.get("status") == "completed":
        open_material = [item.get("id") for item in doc.get("findings", []) if item.get("severity") in {"P0", "P1"} and item.get("status") == "open"]
        if open_material:
            failures.append("completed review has open P0/P1 findings: " + ", ".join(open_material))
        no_resolution = [item.get("id") for item in doc.get("findings", []) if item.get("severity") in {"P0", "P1"} and item.get("status") != "open" and not str(item.get("resolution", "")).strip()]
        if no_resolution:
            failures.append("closed P0/P1 findings have no resolution: " + ", ".join(no_resolution))
        no_evidence = [item.get("id") for item in doc.get("findings", []) if item.get("status") in {"resolved", "deferred", "rejected"} and not item.get("evidence_refs")]
        if no_evidence:
            failures.append("resolved findings have no evidence: " + ", ".join(no_evidence))
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: Review Record {doc.get('review_id')} has honest finding closure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
