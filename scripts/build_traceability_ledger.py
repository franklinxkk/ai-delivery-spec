#!/usr/bin/env python3
"""Build deterministic forward/reverse stable-ID traceability from Product Truth."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from truth_references import iter_references


def load_truth(path: Path) -> dict[str, Any] | None:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        print(f"BLOCKED: Product Truth is missing, unreadable or invalid YAML: {path}; run compile-truth first or fix --truth")
        return None
    if not isinstance(document, dict):
        print(f"BLOCKED: Product Truth root must be an object: {path}; fix the source or rerun compile-truth")
        return None
    return document


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def relation(key: str) -> str:
    return {
        "source_refs": "derived_from", "behavior_refs": "specifies",
        "acceptance_refs": "verified_by", "evidence_refs": "evidenced_by",
        "change_refs": "changed_by", "dependency_refs": "depends_on",
        "supersedes": "supersedes",
    }.get(key, "relates_to")


def build(document: dict[str, Any], baseline: str) -> dict[str, Any]:
    ids = {node["id"] for node in walk(document) if isinstance(node.get("id"), str)}
    targets = set(ids)
    if isinstance(document.get("truth_id"), str):
        targets.add(document["truth_id"])
    edges: dict[tuple[str, str, str], dict[str, str]] = {}
    unresolved = []
    external = []
    for ref in iter_references(document, document.get("truth_id")):
        if ref.external:
            if ref.valid_locator:
                external.append(ref.record())
            else:
                unresolved.append(ref.record())
            continue
        if ref.target not in targets or ref.owner is None:
            unresolved.append(ref.record())
            continue
        edges[(ref.owner, ref.target, ref.field)] = {
            "from_id": ref.owner, "to_id": ref.target,
            "relation": relation(ref.field), "source": ref.field,
        }
    forward: dict[str, list[str]] = defaultdict(list)
    reverse: dict[str, list[str]] = defaultdict(list)
    for edge in edges.values():
        forward[edge["from_id"]].append(edge["to_id"])
        reverse[edge["to_id"]].append(edge["from_id"])
    linked = set(forward) | set(reverse)
    orphans = [
        {"id": item, "classification": "error", "reason": "stable ID has no incoming or outgoing trace edge"}
        for item in sorted(ids - linked)
    ]
    return {
        "schema_version": "5.1.0",
        "ledger_id": "LEDGER-TRACEABILITY-001",
        "baseline_version": baseline,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "edges": sorted(edges.values(), key=lambda item: (item["from_id"], item["to_id"], item["relation"])),
        "forward_index": {key: sorted(set(values)) for key, values in sorted(forward.items())},
        "reverse_index": {key: sorted(set(values)) for key, values in sorted(reverse.items())},
        "orphans": orphans,
        "unresolved_refs": unresolved,
        "unverified_external_refs": external,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline-version", default="unversioned")
    args = parser.parse_args()
    document = load_truth(args.truth)
    if document is None:
        return 2
    if document.get("layout") == "progressive_shards":
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from compile_product_truth import compile_index
        document, failures = compile_index(args.truth, validate_final=False)
        if failures:
            raise SystemExit("\n".join(f"FAIL: {item}" for item in failures))
    result = build(document, args.baseline_version)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(result, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    print(f"Wrote {len(result['edges'])} trace edges, {len(result['orphans'])} orphans, "
          f"{len(result['unverified_external_refs'])} unverified external locators to {args.output}")
    for ref in result["unresolved_refs"]:
        print(f"FAIL: {ref['from_id']} {ref['path']} -> {ref['to_id']} (unresolved reference)")
    if result["unresolved_refs"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
