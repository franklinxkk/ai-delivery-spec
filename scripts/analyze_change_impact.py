#!/usr/bin/env python3
"""Bounded dependency candidates. Graph reachability is never change authorization."""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path
from typing import Any
import yaml
from change_package_contract import ChangeContractError, extract_seed_refs, load_yaml_mapping


def dependency_graph(document: dict[str, Any]) -> tuple[dict[str, set[str]], dict, list[dict]]:
    graph: dict[str, set[str]] = defaultdict(set)
    links: dict[tuple[str, str], list[str]] = defaultdict(list)
    nodes: list[tuple[dict, str]] = []
    visited: set[int] = set()

    def walk(value: Any, location: str):
        if isinstance(value, (dict, list)):
            if id(value) in visited:
                return
            visited.add(id(value))
            if len(visited) > 100_000:
                raise ChangeContractError("dependency input exceeds 100000 containers; query a smaller slice")
        if isinstance(value, dict):
            nodes.append((value, location))
            for key, child in value.items():
                walk(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{location}[{index}]")
    walk(document, "$")
    ids = {node["id"] for node, _ in nodes if isinstance(node.get("id"), str) and node["id"].strip()}
    edges = document.get("edges", [])
    if not isinstance(edges, list):
        raise ChangeContractError("edges must be an array")

    def connect(left: str, right: str, location: str):
        graph[left].add(right)
        graph[right].add(left)
        links[tuple(sorted((left, right)))].append(location)

    for i, edge in enumerate(edges):
        if not isinstance(edge, dict) or not all(isinstance(edge.get(k), str) and edge[k].strip() for k in ("from_id", "to_id")):
            raise ChangeContractError(f"edges[{i}] needs non-empty from_id/to_id")
        left, right = edge["from_id"], edge["to_id"]
        ids.update((left, right))
        connect(left, right, f"$.edges[{i}]")
    for name in ("forward_index", "reverse_index"):
        index = document.get(name, {})
        if not isinstance(index, dict):
            raise ChangeContractError(name + " must be an object")
        for owner, refs in index.items():
            if not isinstance(owner, str) or not isinstance(refs, list) or any(not isinstance(r, str) or not r.strip() for r in refs):
                raise ChangeContractError(name + " needs string IDs and string arrays")
            ids.add(owner)
            for ref in refs:
                ids.add(ref)
                connect(owner, ref, f"$.{name}.{owner}")
    for item_id in ids:
        graph.setdefault(item_id, set())
    unresolved = []
    for node, location in nodes:
        owner = node.get("id")
        if not isinstance(owner, str):
            continue
        for key, value in node.items():
            if not isinstance(key, str) or not key.endswith(("_ref", "_refs")) or value is None:
                continue
            refs = [value] if key.endswith("_ref") else value
            if not isinstance(refs, list) or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
                raise ChangeContractError(f"{location}.{key} must contain non-empty string references")
            for ref in refs:
                if ref in ids:
                    connect(owner, ref, f"{location}.{key}")
                else:
                    unresolved.append({"owner": owner, "ref": ref, "location": f"{location}.{key}"})
    return dict(graph), dict(links), unresolved


def graph_from_truth(document: dict[str, Any]) -> dict[str, set[str]]:
    """Compatibility API for callers that only need adjacency."""
    return dependency_graph(document)[0]


def analyze(truth: dict, change: dict, max_depth: int = 4) -> dict:
    if not 0 <= max_depth <= 100:
        raise ChangeContractError("max-depth must be between 0 and 100")
    seeds = extract_seed_refs(change)
    graph, links, unresolved = dependency_graph(truth)
    missing = sorted(set(seeds) - set(graph))
    parents: dict[str, str | None] = {seed: None for seed in seeds if seed in graph}
    distances = {seed: 0 for seed in parents}
    queue = deque(parents)
    while queue:
        current = queue.popleft()
        if distances[current] >= max_depth:
            continue
        for neighbor in sorted(graph[current]):
            if neighbor not in parents:
                parents[neighbor] = current
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
    boundary = sorted(ref for ref in parents if any(n not in parents for n in graph[ref]))
    affected = []
    for ref in sorted(parents, key=lambda r: (distances[r], r)):
        path, cursor = [ref], ref
        while parents[cursor] is not None:
            cursor = parents[cursor]
            path.append(cursor)
        path.reverse()
        affected.append({
            "ref": ref, "category": ref.split("-", 1)[0], "distance": distances[ref],
            "impact": "seed" if not distances[ref] else "direct" if distances[ref] == 1 else "transitive",
            "status": "candidate", "dependency_path": path,
            "edge_sources": [links[tuple(sorted(pair))] for pair in zip(path, path[1:])],
            "reason": "Reachable through declared references; verify actual consumption before including in approved scope",
        })
    relevant_unresolved = [item for item in unresolved if item["owner"] in parents]
    actual_version = truth.get("baseline_version")
    requested_version = change.get("baseline_version")
    version_match = None if actual_version is None or requested_version is None else str(actual_version) == str(requested_version)
    return {
        "schema_version": "5.5.0", "change_id": change.get("change_id"),
        "baseline_version": change.get("baseline_version"), "seed_refs": seeds,
        "input_baselines": {"truth": actual_version, "change": requested_version, "match": version_match},
        "missing_seed_refs": missing, "affected": affected,
        "coverage": {"max_depth": max_depth, "depth_truncated": bool(boundary),
                     "frontier_refs": boundary, "unresolved_refs": relevant_unresolved,
                     "unresolved_outside_slice_count": len(unresolved) - len(relevant_unresolved)},
        "authority": "candidate_only",
        "not_proven": ["complete consumer inventory", "semantic dependency", "change authorization", "implementation or acceptance"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--change", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-depth", type=int, default=4)
    args = parser.parse_args()
    try:
        result = analyze(load_yaml_mapping(args.truth, label="truth/trace ledger"),
                         load_yaml_mapping(args.change, label="change package"), args.max_depth)
        rendered = yaml.safe_dump(result, allow_unicode=True, sort_keys=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"WROTE: {len(result['affected'])} dependency candidates to {args.output}; not an approved impact list")
        else:
            print(rendered, end="")
    except (ChangeContractError, OSError, UnicodeError, RecursionError) as exc:
        print(f"FAIL: {exc}")
        return 2
    return 1 if result["missing_seed_refs"] or result["coverage"]["depth_truncated"] or result["coverage"]["unresolved_refs"] or result["input_baselines"]["match"] is False else 0


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
