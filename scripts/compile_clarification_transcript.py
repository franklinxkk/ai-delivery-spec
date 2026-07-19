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
MATERIAL_PRIORITIES = {"P0", "P1"}
STAGE_ORDER = {"clarify": 0, "specify": 1, "review": 2, "baseline": 3, "implementation": 4, "acceptance": 5}
TURN_DECISION_FIELDS = ("recommendation", "recommendation_evidence_refs", "tradeoff", "affected_refs", "evidence_refs")


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
    previous_direction_turn: str | None = None
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
        missing_turn_fields = [name for name in TURN_DECISION_FIELDS if not turn.get(name)]
        if missing_turn_fields:
            failures.append(f"clarification turn {turn.get('turn_id')} misses decision evidence: {', '.join(missing_turn_fields)}")
        question_kind = turn.get("question_kind", unknown.get("question_kind", "fact"))
        if unknown.get("question_kind") and unknown.get("question_kind") != question_kind:
            failures.append(f"clarification turn {turn.get('turn_id')} question_kind conflicts with {unknown_id}")
        if question_kind == "direction":
            if previous_direction_turn and turn.get("branch_ref") != previous_direction_turn:
                failures.append(
                    f"direction turn {turn.get('turn_id')} must branch from previous direction turn {previous_direction_turn}"
                )
            previous_direction_turn = turn.get("turn_id")
        unknown["status"] = turn["status"]
        unknown["answer"] = turn["answer"]
        unknown["owner"] = turn["decision_owner"]
        for name in (
            "question_kind", "recommendation", "recommendation_evidence_refs", "tradeoff",
            "affected_refs", "blocks_stage", "reversal_path", "branch_ref", "evidence_refs",
        ):
            if turn.get(name) is not None:
                unknown[name] = turn[name]

    if args.decision in READY:
        for item in contract.get("unknowns", []):
            if item.get("priority") not in MATERIAL_PRIORITIES:
                continue
            item_id = item.get("id", "<unknown>")
            for name in ("recommendation", "recommendation_evidence_refs", "tradeoff", "affected_refs"):
                if not item.get(name):
                    failures.append(f"material unknown {item_id} misses {name}")
            if item.get("status") in {"answered", "accepted_risk"}:
                if not str(item.get("answer", "")).strip() or not item.get("evidence_refs"):
                    failures.append(f"closed material unknown {item_id} needs answer and evidence_refs")
                continue
            missing_ownership = [name for name in ("owner", "affected_refs", "blocks_stage", "reversal_path") if not item.get(name)]
            if missing_ownership:
                failures.append(f"open material unknown {item_id} is not owned/scoped: {', '.join(missing_ownership)}")
                continue
            if STAGE_ORDER.get(str(item.get("blocks_stage")), 0) <= STAGE_ORDER["specify"]:
                failures.append(
                    f"ready decision is forbidden because {item_id} blocks {item.get('blocks_stage')}"
                )
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
