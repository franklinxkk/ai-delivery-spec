#!/usr/bin/env python3
"""Compile small, resumable Product Truth fragments into one canonical document."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
INDEX_SCHEMA = ROOT / "schemas" / "product-truth-index.schema.json"
FRAGMENT_SCHEMA = ROOT / "schemas" / "product-truth-fragment.schema.json"
TRUTH_SCHEMA = ROOT / "schemas" / "product-truth.schema.json"
LIST_KEYS = {
    "sources", "assertions", "unknowns", "decisions", "conflicts", "roles",
    "requirements", "features", "modules", "entities", "fields", "flows", "views", "actions",
    "states", "rules", "events", "integrations", "acceptance", "evidence",
    "projections",
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return value


def schema_failures(value: dict[str, Any], path: Path, schema_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures = []
    for error in validator.iter_errors(value):
        location = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"{path}: {location}: {error.message}")
    return failures


def compile_index(index_path: Path, validate_final: bool = True) -> tuple[dict[str, Any], list[str]]:
    index_path = index_path.resolve()
    index = load_yaml(index_path)
    failures = schema_failures(index, index_path, INDEX_SCHEMA)
    merged: dict[str, Any] = {"schema_version": index.get("target_schema_version", "5.0.0")}
    seen_ids: dict[str, str] = {}

    for entry in index.get("fragments", []):
        fragment_path = (index_path.parent / entry["path"]).resolve()
        if not fragment_path.exists():
            failures.append(f"missing fragment: {fragment_path}")
            continue
        fragment = load_yaml(fragment_path)
        failures.extend(schema_failures(fragment, fragment_path, FRAGMENT_SCHEMA))
        if fragment.get("fragment_id") != entry.get("id"):
            failures.append(f"{fragment_path}: fragment_id does not match index")
        if fragment.get("truth_id") != index.get("truth_id"):
            failures.append(f"{fragment_path}: truth_id does not match index")
        for key, value in fragment.get("content", {}).items():
            if key in LIST_KEYS:
                bucket = merged.setdefault(key, [])
                for item in value:
                    item_id = item.get("id") if isinstance(item, dict) else None
                    if item_id and item_id in seen_ids:
                        failures.append(
                            f"duplicate stable ID {item_id}: {seen_ids[item_id]} and {fragment_path}"
                        )
                    if item_id:
                        seen_ids[item_id] = str(fragment_path)
                    bucket.append(item)
            elif key in merged and merged[key] != value:
                failures.append(f"conflicting singleton key {key} in {fragment_path}")
            else:
                merged[key] = value

    if merged.get("truth_id") != index.get("truth_id"):
        failures.append("compiled truth_id does not match index truth_id")
    if validate_final and not failures:
        failures.extend(schema_failures(merged, index_path, TRUTH_SCHEMA))
    return merged, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    merged, failures = compile_index(args.index, validate_final=not args.allow_incomplete)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    output = args.output
    if output is None:
        index = load_yaml(args.index.resolve())
        output = args.index.resolve().parent / index["compiled_output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(merged, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    count = sum(len(merged.get(key, [])) for key in LIST_KEYS)
    print(f"PASS: compiled {len(load_yaml(args.index.resolve())['fragments'])} fragments and {count} records to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
