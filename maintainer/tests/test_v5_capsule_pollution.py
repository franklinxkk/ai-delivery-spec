#!/usr/bin/env python3
"""Regression: composed capsules cannot collide on namespace or write slots."""

from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts/validators/validate_capsule_composition.py"


def main() -> int:
    source = yaml.safe_load((ROOT / "maintainer/examples/generic-energy-capsule-v5/project-domain-capsule.yaml").read_text(encoding="utf-8"))
    other = copy.deepcopy(source)
    other["capsule_id"] = "CAP-FACILITY-MAINTENANCE-001"
    other["namespace"] = "facility-maintenance"
    for index, policy in enumerate(other["policies"], start=1):
        policy["id"] = f"RULE-FACILITY-MAINTENANCE-{index:03d}"
    with tempfile.TemporaryDirectory(prefix="ai-delivery-capsule-") as temp:
        work = Path(temp)
        first, second = work / "energy.yaml", work / "facility.yaml"
        first.write_text(yaml.safe_dump(source, allow_unicode=True, sort_keys=False), encoding="utf-8")
        second.write_text(yaml.safe_dump(other, allow_unicode=True, sort_keys=False), encoding="utf-8")
        command = [sys.executable, str(VALIDATOR), "--capsule", str(first), "--capsule", str(second)]
        conflict = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if conflict.returncode == 0 or "shadow write conflict" not in conflict.stdout:
            raise AssertionError("cross-capsule shared-slot pollution was not blocked")
        for policy in other["policies"]:
            policy["writes_to"] = ["facility." + slot for slot in policy.get("writes_to", [])]
        other["context_dictionary"].extend(
            {
                "name": "facility." + item["name"],
                "type": item["type"],
                "description": item["description"],
            }
            for item in list(other["context_dictionary"])
            if item["name"].startswith("work_order.")
        )
        second.write_text(yaml.safe_dump(other, allow_unicode=True, sort_keys=False), encoding="utf-8")
        isolated = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if isolated.returncode != 0:
            raise AssertionError(isolated.stdout + isolated.stderr)
    print("PASS: capsule namespaces, variables, and write slots remain isolated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
