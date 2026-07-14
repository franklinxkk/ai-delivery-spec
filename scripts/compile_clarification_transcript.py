#!/usr/bin/env python3
"""Compile owner-attributed clarification turns into a revised Discovery Contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
READY = {"READY_FOR_LIGHT_SPEC", "READY_FOR_UNIFIED_PRD", "READY_FOR_PRODUCT_TRUTH", "READY_FOR_CHANGE_PACKAGE"}


def errors(document: dict, schema_name: str) -> list[str]:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    return [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(document)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--decision", choices=[*sorted(READY), "REVIEW_COMPLETE_WITH_GAPS", "BLOCKED_BY_P0_UNKNOWN"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract = yaml.safe_load(args.contract.read_text(encoding="utf-8"))
    transcript = yaml.safe_load(args.transcript.read_text(encoding="utf-8"))
    failures = errors(contract, "discovery-contract.schema.json")
    failures += errors(transcript, "clarification-transcript.schema.json")
    if transcript.get("project_id") != contract.get("project_id"):
        failures.append("transcript project_id does not match Discovery Contract")
    by_id = {item["id"]: item for item in contract.get("unknowns", [])}
    seen: set[str] = set()
    for turn in transcript.get("turns", []):
        unknown_id = turn.get("unknown_id")
        if unknown_id in seen:
            failures.append(f"duplicate answer for unknown in one transcript: {unknown_id}")
            continue
        seen.add(unknown_id)
        unknown = by_id.get(unknown_id)
        if not unknown:
            failures.append(f"transcript references unknown ID not in contract: {unknown_id}")
            continue
        unknown["status"] = turn["status"]
        unknown["answer"] = turn["answer"]
        unknown["owner"] = turn["decision_owner"]
    open_p0 = [
        item["id"] for item in contract.get("unknowns", [])
        if item.get("priority") == "P0" and item.get("status") in {"open", "blocked"}
    ]
    if args.decision in READY and open_p0:
        failures.append("ready decision is forbidden with open P0 unknowns: " + ", ".join(open_p0))
    contract["discovery_decision"] = args.decision
    failures += errors(contract, "discovery-contract.schema.json")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(contract, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    print(f"PASS: compiled {len(transcript.get('turns', []))} turns into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
