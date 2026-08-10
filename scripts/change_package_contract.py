#!/usr/bin/env python3
"""Shared, defensive readers for Change Package consumers.

The JSON Schema remains the complete artifact contract. These helpers keep
standalone consumers from reimplementing nested-shape assumptions or leaking
tracebacks when they receive an invalid package directly.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml


class ChangeContractError(ValueError):
    """A bounded, user-actionable Change Package input failure."""


def load_yaml_mapping(path: Path, *, label: str) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ChangeContractError(f"{label} is not readable UTF-8 YAML: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ChangeContractError(f"{label} root must be an object")
    return loaded


def iter_impact_objects(document: dict[str, Any]) -> Iterator[tuple[str, int, dict[str, Any]]]:
    impacts = document.get("impacts", {})
    if not isinstance(impacts, dict):
        raise ChangeContractError("impacts must be an object")
    for group, values in impacts.items():
        if group == "data_migration":
            continue
        if not isinstance(values, list):
            raise ChangeContractError(f"impacts.{group} must be an array")
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                raise ChangeContractError(
                    f"impacts.{group}[{index}] must be an object with ref, change_type and reason"
                )
            yield str(group), index, item


def extract_seed_refs(document: dict[str, Any]) -> list[str]:
    """Read explicit seeds, or safely fall back to structured impact refs."""
    request = document.get("request", {})
    if not isinstance(request, dict):
        raise ChangeContractError("request must be an object")
    seeds = request.get("seed_refs", [])
    if seeds is None:
        seeds = []
    if not isinstance(seeds, list) or any(not isinstance(item, str) or not item.strip() for item in seeds):
        raise ChangeContractError("request.seed_refs must be an array of non-empty stable IDs")
    if not seeds:
        for group, index, item in iter_impact_objects(document):
            ref = item.get("ref")
            if ref is None:
                continue
            if not isinstance(ref, str) or not ref.strip():
                raise ChangeContractError(f"impacts.{group}[{index}].ref must be a non-empty stable ID")
            seeds.append(ref.strip())
    if not seeds:
        raise ChangeContractError("change contains no request.seed_refs or structured impact refs")
    return list(dict.fromkeys(item.strip() for item in seeds))
