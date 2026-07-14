#!/usr/bin/env python3
"""Validate executable acceptance results, evidence and sign-off semantics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "acceptance-run.schema.json"


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
    items = doc.get("items", []) if isinstance(doc, dict) else []
    for item in items:
        if item.get("result") == "pass" and not item.get("evidence_refs"):
            failures.append(f"{item.get('id')} passes without evidence")
    conclusion = doc.get("conclusion") if isinstance(doc, dict) else None
    incomplete = [item.get("id") for item in items if item.get("mandatory") and item.get("result") != "pass"]
    if conclusion == "accepted" and incomplete:
        failures.append("accepted run has incomplete mandatory items: " + ", ".join(incomplete))
    if conclusion == "accepted_with_conditions" and not doc.get("conditions"):
        failures.append("accepted_with_conditions requires named conditions, owners and due criteria")
    if conclusion in {"accepted", "accepted_with_conditions"} and not doc.get("sign_offs"):
        failures.append(f"{conclusion} requires sign-offs")
    rejected_sign_offs = [item.get("actor") for item in doc.get("sign_offs", []) if item.get("decision") == "reject"]
    if conclusion in {"accepted", "accepted_with_conditions"} and rejected_sign_offs:
        failures.append("accepted conclusion conflicts with rejecting sign-offs: " + ", ".join(rejected_sign_offs))
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: Acceptance Run {doc.get('run_id')} is executable and evidence-consistent ({conclusion})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
