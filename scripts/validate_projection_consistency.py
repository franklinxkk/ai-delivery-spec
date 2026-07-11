#!/usr/bin/env python3
"""Check that a v5 Markdown projection does not invent Product Truth IDs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


ID_PATTERN = re.compile(
    r"\b(?:SRC|AST|DEC|UNK|CFL|ROLE|FEAT|MOD|ENT|FLD|FLOW|VIEW|REG|ACT|STM|RULE|EVT|INT|AC|EVD|CHG|METRIC|TRUTH)-[A-Z0-9-]+\b"
)


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def truth_ids(document: dict[str, Any]) -> set[str]:
    ids = {node["id"] for node in walk(document) if isinstance(node.get("id"), str)}
    if document.get("truth_id"):
        ids.add(document["truth_id"])
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--projection", type=Path, required=True)
    args = parser.parse_args()

    truth = yaml.safe_load(args.truth.read_text(encoding="utf-8"))
    text = args.projection.read_text(encoding="utf-8")
    known = truth_ids(truth)
    referenced = set(ID_PATTERN.findall(text))
    invented = sorted(referenced - known)
    failures: list[str] = []
    if invented:
        failures.append("projection invents IDs: " + ", ".join(invented))
    if "product-truth" not in text.lower() and "product truth" not in text.lower():
        failures.append("projection does not name Product Truth as its source")
    if not referenced:
        failures.append("projection contains no stable Product Truth IDs")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(
        f"PASS: projection references {len(referenced)} known Product Truth IDs "
        f"and invents none ({args.projection.name})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
