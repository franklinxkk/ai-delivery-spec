#!/usr/bin/env python3
"""Regression: a lifecycle stage must fail closed after its turn budget."""

from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MANAGER = ROOT / "scripts/manage_execution_state.py"


def run(*args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([sys.executable, str(MANAGER), *args], cwd=ROOT, text=True, encoding="utf-8", capture_output=True)
    if result.returncode != expected:
        raise AssertionError(result.stdout + result.stderr)
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ai-delivery-deadlock-") as temp:
        work = Path(temp)
        contract = yaml.safe_load((ROOT / "references/templates/discovery-contract-template.yaml").read_text(encoding="utf-8"))
        contract.update({"contract_id": "DISC-DEADLOCK-001", "project_id": "deadlock-test"})
        contract["sources"][0].update({"id": "SRC-DEADLOCK-001", "path": "test input"})
        contract["unknowns"][0].update({"id": "UNK-DEADLOCK-001", "owner": "test owner"})
        contract_path = work / "discovery.yaml"
        contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
        config = yaml.safe_load((ROOT / "examples/spec.config.example.yaml").read_text(encoding="utf-8"))
        config["execution"]["max_turns_per_stage"] = 2
        config_path = work / "spec.config.yaml"
        config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        state0, state1, state2, overflow = [work / f"state-{item}.yaml" for item in (0, 1, 2, 3)]
        run("create", "--discovery-contract", str(contract_path), "--config", str(config_path), "--installed-skill", str(ROOT), "--execution-id", "EXEC-DEADLOCK-001", "--output", str(state0))
        run("record-turn", "--state", str(state0), "--output", str(state1))
        run("record-turn", "--state", str(state1), "--output", str(state2))
        blocked = run("record-turn", "--state", str(state2), "--output", str(overflow), expected=1)
        if "LifecycleConvergenceError" not in blocked.stdout or overflow.exists():
            raise AssertionError("turn overflow did not fail atomically with LifecycleConvergenceError")
        run("verify", "--state", str(state2))
    print("PASS: lifecycle turn budget blocks propose/reject deadlock without corrupting the last state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
