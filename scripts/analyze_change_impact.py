#!/usr/bin/env python3
"""Traverse a Product Truth or trace ledger from change seed IDs."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import yaml


def graph_from_truth(document: dict[str, Any]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    def walk(value: Any):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)
    ids = {node["id"] for node in walk(document) if isinstance(node.get("id"), str)}
    for node in walk(document):
        owner = node.get("id")
        if not isinstance(owner, str):
            continue
        for key, value in node.items():
            refs = [value] if key.endswith("_ref") and isinstance(value, str) else value if key.endswith("_refs") and isinstance(value, list) else []
            for ref in refs:
                if ref in ids:
                    graph[owner].add(ref); graph[ref].add(owner)
    return graph


def category(item_id: str) -> str:
    return item_id.split("-", 1)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--change", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-depth", type=int, default=4)
    args = parser.parse_args()
    truth = yaml.safe_load(args.truth.read_text(encoding="utf-8"))
    change = yaml.safe_load(args.change.read_text(encoding="utf-8"))
    seeds = change.get("request", {}).get("seed_refs", [])
    if not seeds:
        seeds = [item.get("ref") for values in change.get("impacts", {}).values() if isinstance(values, list) for item in values if item.get("ref")]
    if not seeds:
        raise SystemExit("FAIL: change contains no request.seed_refs or impact refs")
    graph = graph_from_truth(truth)
    missing = sorted(set(seeds) - set(graph))
    queue = deque((seed, 0) for seed in seeds if seed in graph)
    seen: dict[str, int] = {}
    while queue:
        current, distance = queue.popleft()
        if current in seen and seen[current] <= distance:
            continue
        seen[current] = distance
        if distance < args.max_depth:
            queue.extend((neighbor, distance + 1) for neighbor in sorted(graph[current]))
    result = {
        "schema_version": "5.1.0",
        "change_id": change.get("change_id"),
        "baseline_version": change.get("baseline_version"),
        "seed_refs": seeds,
        "missing_seed_refs": missing,
        "affected": [
            {"ref": ref, "category": category(ref), "distance": distance, "impact": "direct" if distance <= 1 else "transitive"}
            for ref, distance in sorted(seen.items(), key=lambda item: (item[1], item[0]))
        ],
        "review_dimensions": ["permission_data_scope", "history", "compatibility", "migration", "metrics", "reconciliation", "acceptance_regression"],
    }
    rendered = yaml.safe_dump(result, allow_unicode=True, sort_keys=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"PASS: wrote impact analysis with {len(seen)} affected IDs to {args.output}")
    else:
        print(rendered, end="")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
