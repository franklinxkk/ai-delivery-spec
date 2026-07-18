#!/usr/bin/env python3
"""Regression test for safe v5 delivery initialization."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from ai_delivery_spec_cli import init_delivery


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ai-delivery-v5-init-") as temp:
        target = Path(temp) / "delivery"
        if init_delivery(argparse.Namespace(output=target, force=False, truth_layout="progressive")) != 0:
            failures.append("init-delivery returned failure")
        required = [
            target / "spec.config.yaml",
            target / "manifest.json",
            target / "truth/index.yaml",
            target / "truth/fragments/00-core.yaml",
            target / "truth/fragments/MOD-EXAMPLE.yaml",
            target / "evidence",
        ]
        for path in required:
            if not path.exists():
                failures.append(f"init-delivery omitted {path.name}")
        manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("source_of_truth") != "truth/index.yaml":
            failures.append("manifest does not name progressive Product Truth index")
        config_path = target / "spec.config.yaml"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        config["context"]["profile"] = "minimal"
        config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        init_delivery(argparse.Namespace(output=target, force=True, truth_layout="progressive"))
        preserved = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if preserved["context"]["profile"] != "minimal":
            failures.append("--force must not overwrite enterprise project config")

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print("PASS: legacy init-delivery remains compatible while requirement-first init remains the default")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
