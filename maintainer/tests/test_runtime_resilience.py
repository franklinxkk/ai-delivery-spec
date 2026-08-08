#!/usr/bin/env python3
"""Capability suite: lifecycle convergence, atomic checkpoints, isolation, and clarification."""

from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MANAGER = ROOT / "scripts/manage_execution_state.py"
COMPILER = ROOT / "scripts/compile_clarification_transcript.py"
CAPSULE_VALIDATOR = ROOT / "scripts/validators/validate_capsule_composition.py"
TRUTH = ROOT / "maintainer/examples/publishing-learning-v5/delivery/truth/product-truth.yaml"
CONFIG = ROOT / "examples/spec.config.example.yaml"
TEMP_ROOT = ROOT.parent / ".ads-test-tmp-v542"
TEMP_ROOT.mkdir(exist_ok=True)


def run(script: Path, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if result.returncode != expected:
        raise AssertionError(result.stdout + result.stderr)
    return result


def test_turn_budget_fails_closed() -> None:
    with tempfile.TemporaryDirectory(prefix="ads-deadlock-", dir=TEMP_ROOT) as temp:
        work = Path(temp)
        contract = yaml.safe_load(
            (ROOT / "references/templates/discovery-contract-template.yaml").read_text(encoding="utf-8")
        )
        contract.update({"contract_id": "DISC-DEADLOCK-001", "project_id": "deadlock-test"})
        contract["sources"][0].update({"id": "SRC-DEADLOCK-001", "path": "test input"})
        contract["unknowns"][0].update({"id": "UNK-DEADLOCK-001", "owner": "test owner"})
        contract_path = work / "discovery.yaml"
        contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
        config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
        config["execution"]["max_turns_per_stage"] = 2
        config_path = work / "spec.config.yaml"
        config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        state0, state1, state2, overflow = [work / f"state-{item}.yaml" for item in (0, 1, 2, 3)]
        run(
            MANAGER,
            "create",
            "--discovery-contract",
            str(contract_path),
            "--config",
            str(config_path),
            "--installed-skill",
            str(ROOT),
            "--execution-id",
            "EXEC-DEADLOCK-001",
            "--output",
            str(state0),
        )
        run(MANAGER, "record-turn", "--state", str(state0), "--output", str(state1))
        run(MANAGER, "record-turn", "--state", str(state1), "--output", str(state2))
        blocked = run(
            MANAGER,
            "record-turn",
            "--state",
            str(state2),
            "--output",
            str(overflow),
            expected=1,
        )
        assert "LifecycleConvergenceError" in blocked.stdout
        assert not overflow.exists()
        run(MANAGER, "verify", "--state", str(state2))


def test_capsule_write_slots_are_isolated() -> None:
    source = yaml.safe_load(
        (ROOT / "maintainer/examples/generic-energy-capsule-v5/project-domain-capsule.yaml").read_text(
            encoding="utf-8"
        )
    )
    other = copy.deepcopy(source)
    other["capsule_id"] = "CAP-FACILITY-MAINTENANCE-001"
    other["namespace"] = "facility-maintenance"
    for index, policy in enumerate(other["policies"], start=1):
        policy["id"] = f"RULE-FACILITY-MAINTENANCE-{index:03d}"
    with tempfile.TemporaryDirectory(prefix="ads-capsule-", dir=TEMP_ROOT) as temp:
        work = Path(temp)
        first, second = work / "energy.yaml", work / "facility.yaml"
        first.write_text(yaml.safe_dump(source, allow_unicode=True, sort_keys=False), encoding="utf-8")
        second.write_text(yaml.safe_dump(other, allow_unicode=True, sort_keys=False), encoding="utf-8")
        conflict = run(CAPSULE_VALIDATOR, "--capsule", str(first), "--capsule", str(second), expected=1)
        assert "shadow write conflict" in conflict.stdout
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
        run(CAPSULE_VALIDATOR, "--capsule", str(first), "--capsule", str(second))


def test_invalid_change_does_not_replace_stable_checkpoint() -> None:
    with tempfile.TemporaryDirectory(prefix="ads-change-drift-", dir=TEMP_ROOT) as temp:
        work = Path(temp)
        state0 = work / "state-000.yaml"
        run(
            MANAGER,
            "create",
            "--truth",
            str(TRUTH),
            "--config",
            str(CONFIG),
            "--installed-skill",
            str(ROOT),
            "--execution-id",
            "EXEC-CHANGE-DRIFT-001",
            "--output",
            str(state0),
        )
        invalid = yaml.safe_load(TRUTH.read_text(encoding="utf-8"))
        invalid.pop("product")
        invalid_path = work / "invalid-truth.yaml"
        invalid_path.write_text(yaml.safe_dump(invalid, sort_keys=False), encoding="utf-8")
        failed_state = work / "state-failed.yaml"
        run(
            MANAGER,
            "checkpoint",
            "--state",
            str(state0),
            "--truth",
            str(invalid_path),
            "--output",
            str(failed_state),
            expected=1,
        )
        assert not failed_state.exists()
        run(MANAGER, "verify", "--state", str(state0))


def test_structured_clarification_closes_only_named_unknowns() -> None:
    contract = yaml.safe_load(
        (ROOT / "references/templates/discovery-contract-template.yaml").read_text(encoding="utf-8")
    )
    contract.update({"contract_id": "DISC-GRILL-001", "project_id": "grill-test"})
    contract["sources"][0].update({"id": "SRC-GRILL-001", "path": "test input"})
    contract["unknowns"][0].update({"id": "UNK-SCOPE-001", "owner": "product owner"})
    transcript = {
        "schema_version": "5.3.3",
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
                "question_kind": "direction",
                "recommendation": "Limit the first slice.",
                "recommendation_evidence_refs": ["meeting-001"],
                "tradeoff": "Historical diff review is deferred.",
                "affected_refs": ["UNK-SCOPE-001"],
                "blocks_stage": "specify",
                "reversal_path": "Reopen through CHG.",
                "evidence_refs": ["meeting-001"],
            }
        ],
    }
    with tempfile.TemporaryDirectory(prefix="ads-grill-", dir=TEMP_ROOT) as temp:
        work = Path(temp)
        contract_path, transcript_path, output = (
            work / "contract.yaml",
            work / "transcript.yaml",
            work / "next.yaml",
        )
        contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
        transcript_path.write_text(yaml.safe_dump(transcript, sort_keys=False), encoding="utf-8")
        run(
            COMPILER,
            "--contract",
            str(contract_path),
            "--transcript",
            str(transcript_path),
            "--decision",
            "READY_FOR_PRODUCT_TRUTH",
            "--output",
            str(output),
        )
        compiled = yaml.safe_load(output.read_text(encoding="utf-8"))
        assert compiled["unknowns"][0]["status"] == "answered"
        bad_contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
        bad_contract["unknowns"].append(
            {
                "id": "UNK-RISK-001",
                "question": "Which data authority applies?",
                "impact": "data",
                "priority": "P1",
                "owner": "product owner",
                "status": "open",
                "recommendation": "Keep the current source read-only until authority is confirmed.",
                "recommendation_evidence_refs": ["meeting-001"],
                "tradeoff": "Submission remains blocked.",
            }
        )
        bad_path = work / "bad-contract.yaml"
        bad_path.write_text(yaml.safe_dump(bad_contract, sort_keys=False), encoding="utf-8")
        blocked = run(
            COMPILER,
            "--contract",
            str(bad_path),
            "--transcript",
            str(transcript_path),
            "--decision",
            "READY_FOR_PRODUCT_TRUTH",
            "--output",
            str(work / "bad-next.yaml"),
            expected=1,
        )
        assert "not owned/scoped" in blocked.stdout


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} runtime-resilience capability regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
