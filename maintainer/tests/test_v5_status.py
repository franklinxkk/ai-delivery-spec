#!/usr/bin/env python3
"""Regression: generated status must match the committed release summary."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ai-delivery-status-") as temp:
        output = Path(temp) / "status.yaml"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/ai_delivery_spec_cli.py"), "status", "--format", "yaml", "--output", str(output)],
            cwd=ROOT, text=True, capture_output=True,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        generated = yaml.safe_load(output.read_text(encoding="utf-8"))
        committed = yaml.safe_load((ROOT / "maintainer/evals/evidence/release-status.yaml").read_text(encoding="utf-8"))
        if generated != committed:
            raise AssertionError("committed release status is stale")
    print("PASS: generated and committed release status agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
