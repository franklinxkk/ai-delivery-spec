#!/usr/bin/env python3
"""Regression checks for v5 execution checkpoints and micro-gates."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import json
import yaml

from manage_execution_state import object_hash
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANAGER = ROOT / "scripts" / "manage_execution_state.py"
TRUTH = ROOT / "examples" / "publishing-learning-v5" / "delivery" / "truth" / "product-truth.yaml"
CONFIG = ROOT / "spec.config.example.yaml"
PROJECTIONS = [
    ROOT / "examples" / "publishing-learning-v5" / "delivery" / "projections" / "human-first-prd.md",
    ROOT / "examples" / "publishing-learning-v5" / "delivery" / "projections" / "coding-agent-spec.md",
]
GATES = ["version_environment", "complexity_domain", "context_survival", "contract_traceability", "audit_access", "fallback_risk"]
DISCOVERY_GATES = ["version_environment", "complexity_domain", "context_survival", "discovery_readiness", "audit_access", "fallback_risk"]


def run(*args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([sys.executable, str(MANAGER), *args], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != expected:
        raise AssertionError(
            f"expected {expected}, got {result.returncode}: {' '.join(args)}\n{result.stdout}\n{result.stderr}"
        )
    return result


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        temp = Path(raw)
        state = temp / "state-000.yaml"
        run(
            "create", "--truth", str(TRUTH), "--config", str(CONFIG),
            "--installed-skill", str(ROOT), "--execution-id", "EXEC-TEST-001",
            "--project-id", "publishing-test", "--output", str(state),
        )
        run("verify", "--state", str(state))

        gate_paths: list[Path] = []
        approval = temp / "human-approval.json"
        approval.write_text(
            json.dumps(
                {
                    "reviewer": "test accountable owner",
                    "qualification": "fixture reviewer",
                    "decision": "approve",
                    "approved_at": "2026-07-11T00:00:00Z",
                    "evidence_ref": "EVD-TEST-HUMAN-GATE",
                }
            ),
            encoding="utf-8",
        )
        for gate_id in GATES:
            output = temp / f"gate-{gate_id}.yaml"
            values = ["gate", "--state", str(state), "--gate-id", gate_id, "--output", str(output)]
            if gate_id == "contract_traceability":
                for projection in PROJECTIONS:
                    values.extend(["--projection", str(projection)])
            if gate_id == "audit_access":
                values.extend(["--human-approval", str(approval)])
            run(*values)
            gate_paths.append(output)

        advanced = temp / "state-001.yaml"
        values = ["advance", "--state", str(state), "--to", "plan", "--output", str(advanced)]
        for gate_path in gate_paths:
            values.extend(["--gate-result", str(gate_path)])
        run(*values)
        run("verify", "--state", str(advanced))

        changed_truth_value = yaml.safe_load(TRUTH.read_text(encoding="utf-8"))
        changed_truth_value["product"]["outcome"] += " (checkpoint revision)"
        changed_truth = temp / "changed-product-truth.yaml"
        changed_truth.write_text(yaml.safe_dump(changed_truth_value, allow_unicode=True, sort_keys=False), encoding="utf-8")
        revised = temp / "state-revised.yaml"
        run("checkpoint", "--state", str(advanced), "--truth", str(changed_truth), "--output", str(revised))
        run("verify", "--state", str(revised))
        run("verify", "--state", str(advanced))

        discovery = {
            "schema_version": "5.0.0",
            "contract_id": "DISC-TEST-001",
            "project_id": "discovery-test",
            "product": {"name": "Discovery Test", "outcome": "", "outcome_status": "unknown", "scope": [], "scope_status": "unknown"},
            "delivery_context": {
                "lifecycle_stage": "discover", "shape": "greenfield", "mode": "standard", "tier": "L2",
                "ai": False, "workflow": True, "info": "missing", "consumers": ["product", "engineering"],
                "governance_profiles": [], "domain_packs": [],
            },
            "sources": [{"id": "SRC-DISC-001", "path": "customer-note", "authority": "accountable", "status": "active", "disposition": "embedded"}],
            "unknowns": [{"id": "UNK-DISC-001", "question": "What is the approved scope?", "impact": "scope", "priority": "P0", "owner": "product owner", "status": "open"}],
            "discovery_decision": "BLOCKED_BY_P0_UNKNOWN",
        }
        discovery_path = temp / "discovery.yaml"
        discovery_path.write_text(yaml.safe_dump(discovery, sort_keys=False), encoding="utf-8")
        discovery_state = temp / "discovery-state-000.yaml"
        run(
            "create", "--discovery-contract", str(discovery_path), "--config", str(CONFIG),
            "--installed-skill", str(ROOT), "--execution-id", "EXEC-DISCOVERY-TEST",
            "--output", str(discovery_state),
        )
        run(
            "gate", "--state", str(discovery_state), "--gate-id", "discovery_readiness",
            "--output", str(temp / "discovery-blocked-gate.yaml"), expected=1,
        )
        discovery["product"].update({"outcome": "Approved bounded delivery", "outcome_status": "known", "scope": ["bounded delivery"], "scope_status": "approved"})
        discovery["delivery_context"]["info"] = "complete"
        discovery["unknowns"][0].update({"status": "answered", "answer": "bounded delivery"})
        discovery["discovery_decision"] = "READY_FOR_PRODUCT_TRUTH"
        discovery_path.write_text(yaml.safe_dump(discovery, sort_keys=False), encoding="utf-8")
        discovery_ready_state = temp / "discovery-state-001.yaml"
        run(
            "checkpoint", "--state", str(discovery_state), "--discovery-contract", str(discovery_path),
            "--output", str(discovery_ready_state),
        )
        discovery_gate_paths: list[Path] = []
        for gate_id in DISCOVERY_GATES:
            output = temp / f"discovery-gate-{gate_id}.yaml"
            run("gate", "--state", str(discovery_ready_state), "--gate-id", gate_id, "--output", str(output))
            discovery_gate_paths.append(output)
        discovery_specify = temp / "discovery-state-002.yaml"
        values = ["advance", "--state", str(discovery_ready_state), "--to", "specify", "--output", str(discovery_specify)]
        for gate_path in discovery_gate_paths:
            values.extend(["--gate-result", str(gate_path)])
        run(*values)
        discovery_truth_state = temp / "discovery-state-003.yaml"
        run(
            "checkpoint", "--state", str(discovery_specify), "--truth", str(TRUTH),
            "--output", str(discovery_truth_state),
        )
        run("verify", "--state", str(discovery_truth_state))

        scoped = temp / "scoped.yaml"
        query = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts" / "query_product_truth.py"),
                "--truth", str(TRUTH), "--id", "FEAT-CONTENT-PUBLISH-001",
                "--execution-state", str(state), "--output", str(scoped),
            ],
            cwd=ROOT, text=True, capture_output=True,
        )
        if query.returncode != 0 or "execution_state_hash" not in scoped.read_text(encoding="utf-8"):
            raise AssertionError("scoped Product Truth retrieval did not bind the checkpoint")

        denied_state = yaml.safe_load(state.read_text(encoding="utf-8"))
        denied_state["access_scope"]["allowed_ids"].remove("FEAT-CONTENT-PUBLISH-001")
        denied_state["access_scope"]["denied_ids"].append("FEAT-CONTENT-PUBLISH-001")
        denied_state["state_hash"] = object_hash(denied_state, "state_hash")
        denied_path = temp / "state-denied.yaml"
        denied_path.write_text(yaml.safe_dump(denied_state, sort_keys=False), encoding="utf-8")
        denied = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts" / "query_product_truth.py"),
                "--truth", str(TRUTH), "--id", "FEAT-CONTENT-PUBLISH-001",
                "--execution-state", str(denied_path), "--output", str(temp / "denied.yaml"),
            ],
            cwd=ROOT, text=True, capture_output=True,
        )
        if denied.returncode == 0 or "outside execution access scope" not in denied.stdout:
            raise AssertionError("out-of-scope Product Truth seed was not blocked")

        low_truth_value = yaml.safe_load(TRUTH.read_text(encoding="utf-8"))
        low_truth_value["delivery_context"]["project_shape"] = "greenfield"
        low_truth_value["delivery_context"]["governance_profiles"] = []
        low_truth_value["delivery_context"]["domain_packs"] = []
        low_truth = temp / "low-risk-truth.yaml"
        low_truth.write_text(yaml.safe_dump(low_truth_value, allow_unicode=True, sort_keys=False), encoding="utf-8")
        low_state = temp / "low-state.yaml"
        run(
            "create", "--truth", str(low_truth), "--config", str(CONFIG),
            "--installed-skill", str(ROOT / "SKILL.md"), "--execution-id", "EXEC-TEST-LOW",
            "--project-id", "low-risk", "--output", str(low_state),
        )
        outage = temp / "gate-outage.yaml"
        run(
            "gate", "--state", str(low_state), "--gate-id", "fallback_risk",
            "--service-outage", "--human-approval", str(approval), "--output", str(outage),
        )
        if "result: approved_with_gap" not in outage.read_text(encoding="utf-8"):
            raise AssertionError("approved low-risk validator outage was not recorded explicitly")

        old_skill = temp / "SKILL.md"
        old_skill.write_text(
            (ROOT / "SKILL.md").read_text(encoding="utf-8").replace("AI Delivery Spec 5.0.1", "AI Delivery Spec 4.9.14", 1),
            encoding="utf-8",
        )
        blocked = temp / "blocked.yaml"
        result = run(
            "create", "--truth", str(TRUTH), "--config", str(CONFIG),
            "--installed-skill", str(old_skill), "--execution-id", "EXEC-TEST-DRIFT",
            "--project-id", "version-drift", "--output", str(blocked), expected=1,
        )
        if "installed skill version does not match" not in result.stdout:
            raise AssertionError("version drift was not explained")

    print("PASS: discovery contract, versioned checkpoints, contract rebinding, six gates, scoped retrieval, stage advance, and version-drift blocking work")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
