#!/usr/bin/env python3
"""Regression test for safe v5 delivery initialization."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import yaml

from ai_delivery_spec_cli import init_delivery


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ai-delivery-v5-init-") as temp:
        target = Path(temp) / "delivery"
        if init_delivery(argparse.Namespace(output=target, force=False)) != 0:
            failures.append("init-delivery returned failure")
        required = [
            target / "spec.config.yaml",
            target / "manifest.json",
            target / "truth/product-truth.yaml",
            target / "evidence",
        ]
        for path in required:
            if not path.exists():
                failures.append(f"init-delivery omitted {path.name}")
        manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("source_of_truth") != "truth/product-truth.yaml":
            failures.append("manifest does not name Product Truth")
        config_path = target / "spec.config.yaml"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        config["context"]["profile"] = "minimal"
        config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        init_delivery(argparse.Namespace(output=target, force=True))
        preserved = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if preserved["context"]["profile"] != "minimal":
            failures.append("--force must not overwrite enterprise project config")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print("PASS: init-delivery creates v5 config/truth layout and preserves project overrides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
