#!/usr/bin/env python3
"""Regression: a failed contract checkpoint cannot contaminate the last stable state."""

from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANAGER = ROOT / "scripts/manage_execution_state.py"
TRUTH = ROOT / "examples/publishing-learning-v5/delivery/truth/product-truth.yaml"
CONFIG = ROOT / "spec.config.example.yaml"


def run(*args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([sys.executable, str(MANAGER), *args], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != expected:
        raise AssertionError(result.stdout + result.stderr)
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ai-delivery-change-drift-") as temp:
        work = Path(temp)
        state0 = work / "state-000.yaml"
        run("create", "--truth", str(TRUTH), "--config", str(CONFIG), "--installed-skill", str(ROOT), "--execution-id", "EXEC-CHANGE-DRIFT-001", "--output", str(state0))
        invalid = yaml.safe_load(TRUTH.read_text(encoding="utf-8"))
        invalid.pop("product")
        invalid_path = work / "invalid-truth.yaml"
        invalid_path.write_text(yaml.safe_dump(invalid, sort_keys=False), encoding="utf-8")
        failed_state = work / "state-failed.yaml"
        run("checkpoint", "--state", str(state0), "--truth", str(invalid_path), "--output", str(failed_state), expected=1)
        if failed_state.exists():
            raise AssertionError("failed checkpoint wrote a new active state")
        run("verify", "--state", str(state0))
    print("PASS: invalid change is atomic and the last stable contract remains verifiable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
