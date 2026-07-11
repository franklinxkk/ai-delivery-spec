#!/usr/bin/env python3
"""Detect namespace, prompt-variable, and shared-slot conflicts across capsules."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


def inspect(document: dict[str, Any], source: Path) -> list[str]:
    failures: list[str] = []
    namespace = document.get("namespace", "")
    variables = {item.get("name") for item in document.get("context_dictionary", [])}
    prefix = "RULE-" + namespace.upper() + "-"
    for policy in document.get("policies", []):
        if not policy.get("id", "").startswith(prefix):
            failures.append(f"{source}: rule {policy.get('id')} does not use namespace {prefix}")
        used = set(policy.get("listens_to", [])) | set(policy.get("writes_to", []))
        used |= set(re.findall(r"{{\s*([A-Za-z][A-Za-z0-9_.-]*)\s*}}", policy.get("prompt", "")))
        missing = used - variables
        if missing:
            failures.append(f"{source}: undefined context variables: {', '.join(sorted(missing))}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capsule", type=Path, action="append", required=True)
    args = parser.parse_args()
    failures: list[str] = []
    documents: list[tuple[Path, dict[str, Any]]] = []
    namespaces: dict[str, Path] = {}
    slots: dict[tuple[str, str], list[str]] = defaultdict(list)
    for path in args.capsule:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        documents.append((path, document))
        namespace = document.get("namespace", "")
        if namespace in namespaces:
            failures.append(f"duplicate capsule namespace {namespace}: {namespaces[namespace]} and {path}")
        namespaces[namespace] = path
        failures.extend(inspect(document, path))
        for policy in document.get("policies", []):
            listeners = policy.get("listens_to", []) or ["*"]
            for listener in listeners:
                for output in policy.get("writes_to", []):
                    slots[(listener, output)].append(f"{namespace}/{policy.get('id')}")
    for (listener, output), owners in slots.items():
        namespaces_involved = {owner.split("/", 1)[0] for owner in owners}
        if len(namespaces_involved) > 1:
            failures.append(
                f"shadow write conflict input={listener} output={output}: {', '.join(owners)}"
            )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: {len(documents)} capsules have isolated namespaces, variables, and write slots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
