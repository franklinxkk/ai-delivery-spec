#!/usr/bin/env python3
"""Validate an optional AI Delivery Spec project configuration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]


def validate(document: dict) -> list[str]:
    schema = json.loads((ROOT / "schemas/spec-config.schema.json").read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
        key=lambda error: list(error.path),
    )
    failures = [
        f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]
    context = document.get("context", {}) if isinstance(document, dict) else {}
    model_tokens = context.get("model_context_tokens")
    if model_tokens and (
        context.get("reserved_output_tokens", 4096) + context.get("system_overhead_tokens", 4096)
    ) >= model_tokens:
        failures.append(
            "context: reserved_output_tokens + system_overhead_tokens must be below model_context_tokens"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()

    document = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    failures = validate(document)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: spec config is valid ({args.config})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
