#!/usr/bin/env python3
"""Validate review findings, required-role sign-offs and honest completion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from cli_support import input_error_detail
from validators.validate_acceptance_run import local_evidence_path, readable_receipt

SCHEMA = ROOT / "schemas/review-record.schema.json"
APPROVING_DECISIONS = {"approve", "approve_with_conditions"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--verify-evidence", action="store_true", help="check local receipts for completed review findings and sign-offs")
    args = parser.parse_args()
    try:
        doc = yaml.safe_load(args.document.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        print(f"FAIL: REVIEW-INPUT {args.document}: {input_error_detail(exc)}")
        return 1
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    failures = [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(doc)
    ]
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
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
        if args.verify_evidence:
            closed = [item for item in findings if item.get("status") in {"resolved", "deferred", "rejected"}]
            for item in closed + sign_offs:
                owner = item.get("id") or item.get("actor")
                readable = False
                for ref in item.get("evidence_refs", []):
                    local, error = local_evidence_path(args.document, ref)
                    if error:
                        failures.append(f"{owner}: {error}")
                    if local and readable_receipt(args.document, local):
                        readable = True
                if not readable:
                    failures.append(f"{owner}: no readable local review receipt")
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
    check_scope = " Checked local receipt references for this completed review." if args.verify_evidence and doc.get("status") == "completed" else ""
    print(
        f"PASS: Review Record {doc.get('review_id')} passed declaration checks. "
        f"Reviewer independence, actual review and sign-off authenticity were not verified.{check_scope}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
