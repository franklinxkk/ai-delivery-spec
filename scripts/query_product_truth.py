#!/usr/bin/env python3
"""Extract a reference-closed Product Truth working slice by stable ID."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

from manage_execution_state import load, sha256_file, verify_state_value


ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
COLLECTIONS = (
    "sources", "assertions", "unknowns", "decisions", "conflicts", "roles",
    "features", "modules", "entities", "fields", "flows", "views", "actions", "states",
    "rules", "events", "integrations", "acceptance", "evidence", "projections",
)


def collect_ids(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str) and ID_PATTERN.match(value):
        found.add(value)
    elif isinstance(value, list):
        for item in value:
            found.update(collect_ids(item))
    elif isinstance(value, dict):
        for item in value.values():
            found.update(collect_ids(item))
    return found


def make_slice(
    truth: dict[str, Any], seeds: list[str], include_reverse: bool, allowed_ids: set[str] | None = None
) -> dict[str, Any]:
    index: dict[str, tuple[str, dict[str, Any]]] = {}
    for collection in COLLECTIONS:
        for item in truth.get(collection, []):
            if isinstance(item, dict) and item.get("id"):
                index[item["id"]] = (collection, item)

    missing = sorted(set(seeds) - set(index))
    if missing:
        raise ValueError("unknown seed IDs: " + ", ".join(missing))
    denied_seeds = sorted(set(seeds) - allowed_ids) if allowed_ids is not None else []
    if denied_seeds:
        raise ValueError("seed IDs are outside execution access scope: " + ", ".join(denied_seeds))

    selected = set(seeds)
    changed = True
    while changed:
        changed = False
        for item_id in list(selected):
            refs = collect_ids(index[item_id][1]) & set(index)
            if allowed_ids is not None:
                refs &= allowed_ids
            before = len(selected)
            selected.update(refs)
            changed = changed or len(selected) != before
        if include_reverse:
            for item_id, (_, item) in index.items():
                if allowed_ids is not None and item_id not in allowed_ids:
                    continue
                if item_id not in selected and collect_ids(item) & selected:
                    selected.add(item_id)
                    changed = True

    grouped: dict[str, list[dict[str, Any]]] = {collection: [] for collection in COLLECTIONS}
    for item_id in selected:
        collection, item = index[item_id]
        grouped[collection].append(item)
    for collection in grouped:
        grouped[collection].sort(key=lambda item: item.get("id", ""))

    return {
        "schema_version": "5.0.0",
        "slice_type": "product_truth_working_slice",
        "source_truth_id": truth.get("truth_id", "UNKNOWN"),
        "seed_ids": seeds,
        "include_reverse": include_reverse,
        "product": truth.get("product", {}),
        "delivery_context": truth.get("delivery_context", {}),
        "items": {key: value for key, value in grouped.items() if value},
        "claim_boundary": "A working slice is not an independent source of truth and must retain source Product Truth IDs.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--id", dest="ids", action="append", required=True)
    parser.add_argument("--include-reverse", action="store_true")
    parser.add_argument("--execution-state", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    truth = yaml.safe_load(args.truth.read_text(encoding="utf-8"))
    allowed_ids: set[str] | None = None
    state_hash: str | None = None
    if args.execution_state:
        state = load(args.execution_state.resolve())
        failures = verify_state_value(state)
        if failures:
            for failure in failures:
                print(f"FAIL: execution state: {failure}")
            return 1
        truth_anchor = next((item for item in state["anchors"] if item["kind"] == "product_truth"), None)
        if not truth_anchor or sha256_file(args.truth.resolve()) != truth_anchor["sha256"]:
            print("FAIL: requested Product Truth content is not the execution state's anchored checkpoint")
            return 1
        allowed_ids = set(state["access_scope"]["allowed_ids"]) - set(state["access_scope"]["denied_ids"])
        state_hash = state["state_hash"]
    try:
        document = make_slice(truth, args.ids, args.include_reverse, allowed_ids)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    if state_hash:
        document["execution_state_hash"] = state_hash
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(document, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    count = sum(len(items) for items in document["items"].values())
    print(f"PASS: wrote reference-closed working slice with {count} items to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
