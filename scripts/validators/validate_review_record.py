#!/usr/bin/env python3
"""Validate review findings, required-role sign-offs and honest completion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/review-record.schema.json"
APPROVING_DECISIONS = {"approve", "approve_with_conditions"}


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
    if not isinstance(doc, dict):
        failures.append("评审记录必须是 YAML/JSON 对象")
        doc = {}

    if doc.get("status") == "completed":
        findings = doc.get("findings", [])
        open_material = [
            item.get("id") for item in findings
            if item.get("severity") in {"P0", "P1"} and item.get("status") == "open"
        ]
        if open_material:
            failures.append("completed review has open P0/P1 findings: " + ", ".join(open_material))
        no_resolution = [
            item.get("id") for item in findings
            if item.get("severity") in {"P0", "P1"}
            and item.get("status") != "open"
            and not str(item.get("resolution", "")).strip()
        ]
        if no_resolution:
            failures.append("closed P0/P1 findings have no resolution: " + ", ".join(no_resolution))
        no_evidence = [
            item.get("id") for item in findings
            if item.get("status") in {"resolved", "deferred", "rejected"}
            and not item.get("evidence_refs")
        ]
        if no_evidence:
            failures.append("resolved findings have no evidence: " + ", ".join(no_evidence))

        required_types = set(doc.get("required_review_types") or [])
        sign_offs = doc.get("sign_offs") or []
        if not required_types:
            failures.append("completed review must declare required_review_types from the approved review plan")
        approving_types = {
            item.get("review_type") for item in sign_offs
            if item.get("decision") in APPROVING_DECISIONS
        }
        rejected_types = {
            item.get("review_type") for item in sign_offs
            if item.get("decision") == "reject"
        }
        missing_types = sorted(required_types - approving_types)
        if missing_types:
            failures.append("required review types lack approving sign-off: " + ", ".join(missing_types))
        blocking_rejections = sorted(required_types & rejected_types)
        if blocking_rejections:
            failures.append("required review types contain rejecting sign-off: " + ", ".join(blocking_rejections))

        reviewers = set(doc.get("reviewers") or [])
        unlisted_actors = sorted({
            str(item.get("actor")) for item in sign_offs
            if item.get("actor") and item.get("actor") not in reviewers
        })
        if unlisted_actors:
            failures.append("sign-off actor is absent from reviewers: " + ", ".join(unlisted_actors))
        conditional_without_terms = [
            str(item.get("review_type")) for item in sign_offs
            if item.get("decision") == "approve_with_conditions" and not item.get("conditions")
        ]
        if conditional_without_terms:
            failures.append("conditional sign-off has no conditions: " + ", ".join(conditional_without_terms))
        record_type = doc.get("review_type")
        if record_type not in {"cross_functional", None} and record_type not in required_types:
            failures.append(f"review_type {record_type} is absent from required_review_types")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(
        f"PASS: Review Record {doc.get('review_id')} has honest finding closure "
        "and required-role sign-offs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())