#!/usr/bin/env python3
"""Regression: structured clarification closes only the unknowns it names."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "scripts/compile_clarification_transcript.py"


def main() -> int:
    contract = yaml.safe_load((ROOT / "references/templates/discovery-contract-template.yaml").read_text(encoding="utf-8"))
    contract.update({"contract_id": "DISC-GRILL-001", "project_id": "grill-test"})
    contract["sources"][0].update({"id": "SRC-GRILL-001", "path": "test input"})
    contract["unknowns"][0].update({"id": "UNK-SCOPE-001", "owner": "product owner"})
    transcript = {
        "schema_version": "5.0.0",
        "transcript_id": "TRN-GRILL-001",
        "project_id": "grill-test",
        "turns": [
            {
                "turn_id": "TURN-SCOPE-001",
                "unknown_id": "UNK-SCOPE-001",
                "question": "Which first slice is approved?",
                "answer": "Import, search, and current-version evidence only.",
                "decision_owner": "product owner",
                "status": "answered",
                "evidence_refs": ["meeting-001"],
            }
        ],
    }
    with tempfile.TemporaryDirectory(prefix="ai-delivery-grill-") as temp:
        work = Path(temp)
        contract_path, transcript_path, output = work / "contract.yaml", work / "transcript.yaml", work / "next.yaml"
        contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
        transcript_path.write_text(yaml.safe_dump(transcript, sort_keys=False), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(COMPILER), "--contract", str(contract_path), "--transcript", str(transcript_path), "--decision", "READY_FOR_PRODUCT_TRUTH", "--output", str(output)],
            cwd=ROOT, text=True, capture_output=True,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        compiled = yaml.safe_load(output.read_text(encoding="utf-8"))
        if compiled["unknowns"][0]["status"] != "answered" or compiled["discovery_decision"] != "READY_FOR_PRODUCT_TRUTH":
            raise AssertionError("structured clarification did not produce a checkpoint-ready contract")
    print("PASS: schema-driven grill compiles owner-attributed answers without free-form invention")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
