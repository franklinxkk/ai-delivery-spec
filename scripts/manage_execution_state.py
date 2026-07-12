#!/usr/bin/env python3
"""Create, verify, gate, and advance a tamper-evident v5 execution checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
STAGES = ["discover", "specify", "plan", "tasks", "build_verify", "launch", "learn_retire"]
DISCOVERY_GATES = [
    "version_environment",
    "complexity_domain",
    "context_survival",
    "discovery_readiness",
    "audit_access",
    "fallback_risk",
]
DELIVERY_GATES = [
    "version_environment",
    "complexity_domain",
    "context_survival",
    "contract_traceability",
    "audit_access",
    "fallback_risk",
]
ALL_GATES = sorted(set(DISCOVERY_GATES + DELIVERY_GATES))


class LifecycleConvergenceError(RuntimeError):
    """Raised when one lifecycle stage exceeds its configured interaction budget."""


def gates_for_stage(stage: str) -> list[str]:
    return DISCOVERY_GATES if stage == "discover" else DELIVERY_GATES


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    else:
        text = yaml.safe_dump(value, allow_unicode=True, sort_keys=False)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_hash(value: dict[str, Any], hash_field: str) -> str:
    payload = {key: item for key, item in value.items() if key != hash_field}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def skill_version(path: Path) -> str:
    manifest = path / "SKILL.md" if path.is_dir() else path
    match = re.search(r"\bv?(\d+\.\d+\.\d+)\b", manifest.read_text(encoding="utf-8"))
    return match.group(1) if match else "unknown"


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def repository_fingerprint() -> tuple[str, bool]:
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    diff = subprocess.run(
        ["git", "diff", "--binary", "HEAD"], cwd=ROOT, capture_output=True, check=False
    )
    if status.returncode != 0:
        entries: list[str] = []
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or any(part in {".git", ".github", "__pycache__"} for part in path.parts):
                continue
            if path.suffix.lower() == ".pyc":
                continue
            entries.append(f"{path.relative_to(ROOT).as_posix()}:{sha256_file(path)}")
        raw = "\n".join(entries).encode("utf-8")
        return hashlib.sha256(raw).hexdigest(), False
    status_text = status.stdout
    extra: list[str] = []
    for line in status_text.splitlines():
        if not line.startswith("?? "):
            continue
        path = ROOT / line[3:]
        if path.is_file():
            extra.append(f"{line[3:]}:{sha256_file(path)}")
    payload = status_text.encode("utf-8") + diff.stdout + "\n".join(extra).encode("utf-8")
    return hashlib.sha256(payload).hexdigest(), bool(status_text.strip())


def dependency_versions() -> dict[str, str]:
    result: dict[str, str] = {}
    for package in ("PyYAML", "jsonschema"):
        try:
            result[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result[package] = "missing"
    result["python"] = ".".join(str(part) for part in sys.version_info[:3])
    return result


def version_tuple(value: str) -> tuple[int, ...]:
    match = re.match(r"^(\d+(?:\.\d+)*)", value)
    return tuple(int(part) for part in match.group(1).split(".")) if match else ()


def dependency_failures(versions: dict[str, str]) -> list[str]:
    failures: list[str] = []
    constraints = {"PyYAML": ((6, 0), (7, 0)), "jsonschema": ((4, 23), (5, 0)), "python": ((3, 11), (4, 0))}
    for name, (minimum, maximum) in constraints.items():
        current = version_tuple(versions.get(name, "missing"))
        if not current or current < minimum or current >= maximum:
            failures.append(f"{name}={versions.get(name, 'missing')} does not satisfy >= {'.'.join(map(str, minimum))}, < {'.'.join(map(str, maximum))}")
    return failures


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def truth_ids(truth: dict[str, Any]) -> list[str]:
    values = {node["id"] for node in walk(truth) if isinstance(node.get("id"), str)}
    if truth.get("truth_id"):
        values.add(truth["truth_id"])
    return sorted(values)


def classify_risk(truth: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    context = truth.get("delivery_context", {})
    assurance = config.get("assurance", {})
    signals = set(context.get("governance_profiles", []))
    if context.get("tier") == "L3":
        signals.add("tier_l3")
    shape = context.get("project_shape", context.get("shape"))
    mode = context.get("delivery_mode", context.get("mode"))
    if shape in {"brownfield", "hybrid"}:
        signals.add("migration")
    if len(truth.get("modules", [])) >= 4:
        signals.add("multi_module")
    high_signals = set(assurance.get("human_gate_on", []))
    high_risk = context.get("tier") == "L3" or bool(signals & high_signals)
    manual = assurance.get("manual_profile", "auto")
    if manual != "auto":
        profile = manual
    elif high_risk:
        profile = "regulated"
    elif mode == "full" or "multi_module" in signals:
        profile = "complex"
    elif context.get("tier") in {"L0", "L1"}:
        profile = "minimal"
    else:
        profile = "standard"
    return {
        "profile": profile,
        "signals": sorted(signals),
        "high_risk": high_risk,
        "classification_basis": "structured_contract",
    }


def domain_snapshot(
    truth: dict[str, Any], coverage: dict[str, Any], project_evidence: dict[str, Any] | None
) -> list[dict[str, Any]]:
    built_in = {item["domain_id"]: item for item in coverage.get("domains", [])}
    supplied = {
        item["domain_id"]: item for item in (project_evidence or {}).get("domains", [])
        if isinstance(item, dict) and item.get("domain_id")
    }
    rows: list[dict[str, Any]] = []
    domain_ids = sorted(set(truth.get("delivery_context", {}).get("domain_packs", [])) | set(supplied))
    for domain_id in domain_ids:
        if domain_id in supplied:
            item = supplied[domain_id]
            rows.append(
                {
                    "domain_id": domain_id,
                    "maturity": item.get("maturity", "none"),
                    "source": "project_evidence",
                    "evidence_refs": item.get("evidence_refs", []),
                    "production_claim": item.get("production_claim", "prohibited"),
                }
            )
        elif domain_id in built_in:
            item = built_in[domain_id]
            rows.append(
                {
                    "domain_id": domain_id,
                    "maturity": item.get("maturity", "none"),
                    "source": "built_in",
                    "evidence_refs": [entry.get("location", "") for entry in item.get("evidence", [])],
                    "production_claim": item.get("production_claim", "prohibited"),
                }
            )
        else:
            rows.append(
                {
                    "domain_id": domain_id,
                    "maturity": "none",
                    "source": "missing",
                    "evidence_refs": [],
                    "production_claim": "prohibited",
                }
            )
    return rows


def schema_failures(value: Any, name: str) -> list[str]:
    schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.path),
    )
    return [
        f"schema {'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
        for error in errors
    ]


def anchor(kind: str, path: Path) -> dict[str, str]:
    return {"kind": kind, "path": str(path.resolve()), "sha256": sha256_file(path.resolve())}


def snapshot(path: Path, output: Path, revision: int, label: str) -> Path:
    directory = output.resolve().parent / "snapshots"
    directory.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower() if path.suffix else ".yaml"
    target = directory / f"{revision:03d}-{label}{suffix}"
    shutil.copyfile(path.resolve(), target)
    return target


def contract_input(args: argparse.Namespace) -> tuple[str, Path, str]:
    if getattr(args, "truth", None):
        return "product_truth", args.truth.resolve(), "product-truth.schema.json"
    return "discovery_contract", args.discovery_contract.resolve(), "discovery-contract.schema.json"


def normalized_stage(contract: dict[str, Any], kind: str) -> str:
    if kind == "discovery_contract":
        return "discover"
    return contract.get("delivery_context", {}).get("lifecycle_stage", "specify")


def initial_failures(state: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    versions = state["versions"]
    if state["environment"] != state["configured_environment"]:
        failures.append("runtime environment does not match spec config")
    if versions["expected_skill"] != versions["repository_skill"]:
        failures.append("repository skill version does not match expected version")
    if versions["expected_skill"] != versions["installed_skill"]:
        failures.append("installed skill version does not match expected version")
    failures.extend(dependency_failures(versions["dependencies"]))
    if state["stage"]["turns"] > state["policy"]["max_turns_per_stage"]:
        failures.append("LifecycleConvergenceError: stage turn limit exceeded")
    if state["environment"] in {"staging", "production"}:
        if versions["repository_dirty"]:
            failures.append("staging/production execution requires a clean repository tree")
        weak = [
            item["domain_id"] for item in state["domain_assurance"]
            if item["maturity"] not in {"validated", "audited"}
            or item["production_claim"] != "allowed"
        ]
        if weak:
            failures.append("non-production domain assurance: " + ", ".join(weak))
        if state["risk"]["high_risk"] and not any(
            item["maturity"] == "audited" and item["production_claim"] == "allowed"
            for item in state["domain_assurance"]
        ):
            failures.append("high-risk production execution has no audited project/domain assurance")
    return failures


def create_state(args: argparse.Namespace) -> int:
    kind, contract_path, contract_schema = contract_input(args)
    config_path = args.config.resolve()
    installed = args.installed_skill.resolve()
    coverage_path = (ROOT / "references" / "domain-coverage.yaml").resolve()
    contract = load(contract_path)
    config = load(config_path)
    coverage = load(coverage_path)
    input_failures = schema_failures(contract, contract_schema) + schema_failures(config, "spec-config.schema.json")
    if input_failures:
        for failure in input_failures:
            print(f"FAIL: input contract: {failure}")
        return 1
    project_evidence = load(args.assurance_evidence.resolve()) if args.assurance_evidence else None
    environment = args.environment or config["execution"]["environment"]
    timestamp = now()
    tree_hash, repository_dirty = repository_fingerprint()
    output = args.output.resolve()
    contract_snapshot = snapshot(contract_path, output, 0, kind.replace("_", "-"))
    config_snapshot = snapshot(config_path, output, 0, "spec-config")
    coverage_snapshot = snapshot(coverage_path, output, 0, "domain-coverage")
    anchors = [anchor(kind, contract_snapshot), anchor("spec_config", config_snapshot), anchor("domain_coverage", coverage_snapshot)]
    if args.assurance_evidence:
        evidence_failures = schema_failures(project_evidence, "assurance-evidence.schema.json")
        if evidence_failures:
            for failure in evidence_failures:
                print(f"FAIL: assurance evidence: {failure}")
            return 1
        assurance_snapshot = snapshot(args.assurance_evidence.resolve(), output, 0, "assurance-evidence")
        anchors.append(anchor("assurance_evidence", assurance_snapshot))
    stage = normalized_stage(contract, kind)
    domains = domain_snapshot(contract, coverage, project_evidence)
    state: dict[str, Any] = {
        "schema_version": "5.0.0",
        "execution_id": args.execution_id,
        "project_id": args.project_id or contract.get("project_id") or contract.get("truth_id", "local-project"),
        "contract_kind": kind,
        "revision": 0,
        "environment": environment,
        "configured_environment": config["execution"]["environment"],
        "status": "ready",
        "versions": {
            "expected_skill": config["execution"]["expected_skill_version"],
            "repository_skill": skill_version(ROOT / "SKILL.md"),
            "installed_skill": skill_version(installed),
            "installed_skill_path": str(installed),
            "repository_commit": git_commit(),
            "repository_tree_hash": tree_hash,
            "repository_dirty": repository_dirty,
            "dependencies": dependency_versions(),
        },
        "risk": classify_risk(contract, config),
        "domain_assurance": domains,
        "anchors": anchors,
        "access_scope": {
            "allowed_ids": truth_ids(contract),
            "allowed_domains": [item["domain_id"] for item in domains],
            "denied_ids": [],
        },
        "stage": {"current": stage, "sequence": STAGES.index(stage), "turns": 0, "completed": STAGES[: STAGES.index(stage)], "required_gates": gates_for_stage(stage)},
        "policy": {
            "high_risk_failure": config["execution"]["high_risk_failure"],
            "low_risk_failure": config["execution"]["low_risk_failure"],
            "audit_mode": config["execution"]["audit_mode"],
            "max_turns_per_stage": config["execution"]["max_turns_per_stage"],
        },
        "gate_result_refs": [],
        "approved_gaps": [],
        "failures": [],
        "previous_state_hash": None,
        "state_hash": "0" * 64,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    state["failures"] = initial_failures(state)
    state["status"] = "blocked" if state["failures"] else "ready"
    state["state_hash"] = object_hash(state, "state_hash")
    failures = schema_failures(state, "execution-state.schema.json")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    dump(output, state)
    print(f"{state['status'].upper()}: execution state created at {output}")
    for failure in state["failures"]:
        print(f"BLOCK: {failure}")
    return 1 if state["status"] == "blocked" else 0


def verify_state_value(state: dict[str, Any]) -> list[str]:
    failures = schema_failures(state, "execution-state.schema.json")
    expected_hash = object_hash(state, "state_hash")
    if state.get("state_hash") != expected_hash:
        failures.append("state hash mismatch")
    for item in state.get("anchors", []):
        path = Path(item["path"])
        if not path.exists():
            failures.append(f"anchor is missing: {path}")
        elif sha256_file(path) != item["sha256"]:
            failures.append(f"anchor drift detected: {path}")
    installed = Path(state.get("versions", {}).get("installed_skill_path", ""))
    if not installed.exists():
        failures.append("installed skill path is missing")
    elif skill_version(installed) != state["versions"]["installed_skill"]:
        failures.append("installed skill changed after checkpoint")
    if skill_version(ROOT / "SKILL.md") != state.get("versions", {}).get("repository_skill"):
        failures.append("repository skill version changed after checkpoint")
    if git_commit() != state.get("versions", {}).get("repository_commit"):
        failures.append("repository commit changed after checkpoint")
    current_tree_hash, _ = repository_fingerprint()
    if current_tree_hash != state.get("versions", {}).get("repository_tree_hash"):
        failures.append("repository tree changed after checkpoint")
    failures.extend(state.get("failures", []))
    return list(dict.fromkeys(failures))


def verify_state(args: argparse.Namespace) -> int:
    state = load(args.state.resolve())
    failures = verify_state_value(state)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: execution state {state['execution_id']} is intact at {state['stage']['current']}")
    return 0


def check(gate_id: str, state: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def add(item_id: str, passed: bool, message: str) -> None:
        checks.append({"id": item_id, "passed": passed, "message": message})

    integrity = verify_state_value(state)
    if gate_id == "version_environment":
        add("state_integrity", not integrity, "; ".join(integrity) or "state and anchors match")
        versions = state["versions"]
        add("environment", state["environment"] == state["configured_environment"], "runtime and configured environments must match")
        match = versions["expected_skill"] == versions["repository_skill"] == versions["installed_skill"]
        add("skill_version", match, "expected/repository/installed versions must match")
        dependency_issues = dependency_failures(versions["dependencies"])
        add("dependencies", not dependency_issues, "; ".join(dependency_issues) or "dependency versions satisfy v5 requirements")
    elif gate_id == "complexity_domain":
        add("structured_classification", state["risk"]["classification_basis"] == "structured_contract", "classification must use structured contract signals")
        weak = [item["domain_id"] for item in state["domain_assurance"] if item["maturity"] in {"none", "experimental"}]
        production_ok = state["environment"] not in {"staging", "production"} or not weak
        add("domain_production_boundary", production_ok, "weak domains: " + (", ".join(weak) or "none"))
        audited_ok = not (state["risk"]["high_risk"] and state["environment"] in {"staging", "production"}) or any(
            item["maturity"] == "audited" and item["production_claim"] == "allowed" for item in state["domain_assurance"]
        )
        add("high_risk_assurance", audited_ok, "high-risk staging/production requires audited accountable evidence")
    elif gate_id == "context_survival":
        add("state_integrity", not integrity, "; ".join(integrity) or "state hash and anchors match")
        kinds = {item["kind"] for item in state["anchors"]}
        contract_present = bool({"discovery_contract", "product_truth"} & kinds)
        add("core_anchors", contract_present and "spec_config" in kinds, "active contract and config hashes must be anchored")
    elif gate_id == "discovery_readiness":
        discovery_anchor = next((item for item in state["anchors"] if item["kind"] == "discovery_contract"), None)
        if not discovery_anchor:
            add("discovery_contract", False, "discovery stage requires an anchored Discovery Contract")
        else:
            discovery = load(Path(discovery_anchor["path"]))
            schema_issues = schema_failures(discovery, "discovery-contract.schema.json")
            add("discovery_contract", not schema_issues, "; ".join(schema_issues) or "Discovery Contract is schema-valid")
            open_p0 = [
                item["id"] for item in discovery.get("unknowns", [])
                if item.get("priority") == "P0" and item.get("status") in {"open", "blocked"}
            ]
            add("p0_unknowns", not open_p0, "open P0 unknowns: " + (", ".join(open_p0) or "none"))
            ready = discovery.get("discovery_decision") in {
                "READY_FOR_LIGHT_SPEC", "READY_FOR_PRODUCT_TRUTH", "READY_FOR_CHANGE_PACKAGE"
            }
            add("discovery_decision", ready, f"decision={discovery.get('discovery_decision')}")
    elif gate_id == "contract_traceability":
        truth_anchor = next((item for item in state["anchors"] if item["kind"] == "product_truth"), None)
        if not truth_anchor:
            add("product_truth", False, "specify and later stages require an anchored Product Truth checkpoint")
        else:
            command = [sys.executable, str(ROOT / "scripts" / "validators" / "validate_product_truth.py"), truth_anchor["path"]]
            result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            add("product_truth", result.returncode == 0, (result.stdout + result.stderr).strip())
            truth = load(Path(truth_anchor["path"]))
            required = {item["id"] for item in truth.get("features", []) if item.get("scope_status") == "in_scope"}
            for projection in args.projection:
                text = projection.read_text(encoding="utf-8")
                missing = sorted(required - set(re.findall(r"\bFEAT-[A-Z0-9-]+\b", text)))
                projection_result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "validators" / "validate_projection_consistency.py"), "--truth", truth_anchor["path"], "--projection", str(projection)],
                    cwd=ROOT, text=True, capture_output=True, check=False,
                )
                passed = not missing and projection_result.returncode == 0
                message = "missing in-scope features: " + (", ".join(missing) or "none")
                if projection_result.returncode != 0:
                    message += "; " + (projection_result.stdout + projection_result.stderr).strip()
                add(f"projection:{projection.name}", passed, message)
    elif gate_id == "audit_access":
        scope = state["access_scope"]
        overlap = set(scope["allowed_ids"]) & set(scope["denied_ids"])
        add("scope_isolation", not overlap, "allowed and denied IDs must not overlap")
        add("tamper_evidence", state["policy"]["audit_mode"] in {"hash_chain", "signed_external"}, "audit must be tamper-evident")
        approval = load(args.human_approval.resolve()) if args.human_approval else None
        approval_ok = not state["risk"]["high_risk"] or bool(
            approval
            and approval.get("decision") == "approve"
            and approval.get("reviewer")
            and approval.get("qualification")
            and approval.get("evidence_ref")
        )
        add("human_gate", approval_ok, "high-risk execution requires accountable human approval evidence")
    elif gate_id == "fallback_risk":
        add("high_risk_fail_closed", state["policy"]["high_risk_failure"] == "block", "high-risk validation failure must block")
        add("low_risk_explicit", state["policy"]["low_risk_failure"] in {"block", "human_review"}, "low-risk fallback must be explicit")
        isolation_ok = state["environment"] != "production" or state["status"] != "blocked"
        add("no_blocked_production", isolation_ok, "blocked/experimental execution cannot enter production")
    return checks


def gate_state(args: argparse.Namespace) -> int:
    state = load(args.state.resolve())
    checks = (
        [{"id": "validator_service", "passed": False, "message": "validator service outage declared; no silent pass"}]
        if args.service_outage
        else check(args.gate_id, state, args)
    )
    failed = [item for item in checks if not item["passed"]]
    approval = load(args.human_approval.resolve()) if args.human_approval else None
    approval_valid = bool(
        approval
        and approval.get("decision") == "approve"
        and approval.get("reviewer")
        and approval.get("qualification")
        and approval.get("evidence_ref")
    )
    if not failed:
        result = "passed"
    elif state["risk"]["high_risk"] or state["environment"] in {"staging", "production"}:
        result = "blocked"
    elif args.service_outage and state["policy"]["low_risk_failure"] == "human_review" and approval_valid:
        result = "approved_with_gap"
    elif state["policy"]["low_risk_failure"] == "human_review":
        result = "review_required"
    else:
        result = "failed"
    payload: dict[str, Any] = {
        "schema_version": "5.0.0",
        "gate_id": args.gate_id,
        "execution_id": state["execution_id"],
        "stage": state["stage"]["current"],
        "state_hash": state["state_hash"],
        "result": result,
        "checks": checks,
        "evidence_refs": [str(path.resolve()) for path in args.projection],
        "human_approval": approval,
        "executed_at": now(),
        "result_hash": "0" * 64,
    }
    payload["result_hash"] = object_hash(payload, "result_hash")
    failures = schema_failures(payload, "gate-result.schema.json")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    dump(args.output.resolve(), payload)
    print(f"{result.upper()}: {args.gate_id} -> {args.output.resolve()}")
    return 0 if result in {"passed", "approved_with_gap"} else 1


def checkpoint_state(args: argparse.Namespace) -> int:
    state = load(args.state.resolve())
    failures = verify_state_value(state)
    if failures:
        for failure in failures:
            print(f"BLOCK: {failure}")
        return 1
    kind, contract_path, contract_schema = contract_input(args)
    if state["stage"]["current"] == "discover" and kind != "discovery_contract":
        print("BLOCK: advance to specify before binding Product Truth")
        return 1
    if state["stage"]["current"] != "discover" and kind == "discovery_contract":
        print("BLOCK: discovery contract cannot replace Product Truth after discover")
        return 1
    contract = load(contract_path)
    input_failures = schema_failures(contract, contract_schema)
    if input_failures:
        for failure in input_failures:
            print(f"FAIL: input contract: {failure}")
        return 1

    config_anchor = next(item for item in state["anchors"] if item["kind"] == "spec_config")
    config_path = args.config.resolve() if args.config else Path(config_anchor["path"])
    config = load(config_path)
    config_failures = schema_failures(config, "spec-config.schema.json")
    if config_failures:
        for failure in config_failures:
            print(f"FAIL: config: {failure}")
        return 1

    coverage_path = ROOT / "references" / "domain-coverage.yaml"
    coverage = load(coverage_path)
    existing_assurance = next((item for item in state["anchors"] if item["kind"] == "assurance_evidence"), None)
    assurance_path = args.assurance_evidence.resolve() if args.assurance_evidence else (
        Path(existing_assurance["path"]) if existing_assurance else None
    )
    project_evidence = load(assurance_path) if assurance_path else None
    if project_evidence:
        evidence_failures = schema_failures(project_evidence, "assurance-evidence.schema.json")
        if evidence_failures:
            for failure in evidence_failures:
                print(f"FAIL: assurance evidence: {failure}")
            return 1

    revision = state["revision"] + 1
    output = args.output.resolve()
    contract_snapshot = snapshot(contract_path, output, revision, kind.replace("_", "-"))
    config_snapshot = snapshot(config_path, output, revision, "spec-config")
    coverage_snapshot = snapshot(coverage_path, output, revision, "domain-coverage")
    anchors = [anchor(kind, contract_snapshot), anchor("spec_config", config_snapshot), anchor("domain_coverage", coverage_snapshot)]
    if assurance_path:
        assurance_snapshot = snapshot(assurance_path, output, revision, "assurance-evidence")
        anchors.append(anchor("assurance_evidence", assurance_snapshot))

    previous = state["state_hash"]
    domains = domain_snapshot(contract, coverage, project_evidence)
    state["contract_kind"] = kind
    state["revision"] = revision
    state["risk"] = classify_risk(contract, config)
    state["domain_assurance"] = domains
    state["anchors"] = anchors
    state["access_scope"] = {
        "allowed_ids": truth_ids(contract),
        "allowed_domains": [item["domain_id"] for item in domains],
        "denied_ids": state.get("access_scope", {}).get("denied_ids", []),
    }
    state["stage"]["required_gates"] = gates_for_stage(state["stage"]["current"])
    state["policy"]["max_turns_per_stage"] = config["execution"]["max_turns_per_stage"]
    state["gate_result_refs"] = []
    state["approved_gaps"] = []
    state["failures"] = initial_failures(state)
    state["status"] = "blocked" if state["failures"] else "ready"
    state["previous_state_hash"] = previous
    state["updated_at"] = now()
    state["state_hash"] = object_hash(state, "state_hash")
    schema_issues = schema_failures(state, "execution-state.schema.json")
    if schema_issues:
        for failure in schema_issues:
            print(f"FAIL: {failure}")
        return 1
    dump(output, state)
    print(f"{state['status'].upper()}: checkpoint revision {revision} -> {output}")
    return 1 if state["status"] == "blocked" else 0


def record_turn(args: argparse.Namespace) -> int:
    state = load(args.state.resolve())
    failures = verify_state_value(state)
    next_turn = state["stage"]["turns"] + 1
    limit = state["policy"]["max_turns_per_stage"]
    if next_turn > limit:
        failures.append(
            f"LifecycleConvergenceError: stage={state['stage']['current']} turns={next_turn} limit={limit}"
        )
    if failures:
        for failure in failures:
            print(f"BLOCK: {failure}")
        return 1
    previous = state["state_hash"]
    state["previous_state_hash"] = previous
    state["stage"]["turns"] = next_turn
    state["status"] = "in_progress"
    state["updated_at"] = now()
    state["state_hash"] = object_hash(state, "state_hash")
    schema_issues = schema_failures(state, "execution-state.schema.json")
    if schema_issues:
        for failure in schema_issues:
            print(f"FAIL: {failure}")
        return 1
    dump(args.output.resolve(), state)
    print(f"PASS: recorded stage turn {next_turn}/{limit} -> {args.output.resolve()}")
    return 0


def advance_state(args: argparse.Namespace) -> int:
    state = load(args.state.resolve())
    failures = verify_state_value(state)
    target_index = STAGES.index(args.to_stage)
    current_index = STAGES.index(state["stage"]["current"])
    if target_index != current_index + 1:
        failures.append("stage transition must advance exactly one lifecycle node")
    results = [load(path.resolve()) for path in args.gate_result]
    by_id = {item.get("gate_id"): item for item in results}
    for gate_id in state["stage"]["required_gates"]:
        result = by_id.get(gate_id)
        if not result:
            failures.append(f"missing gate result: {gate_id}")
        elif result.get("state_hash") != state["state_hash"] or result.get("result") not in {"passed", "approved_with_gap"}:
            failures.append(f"gate is stale or not passed: {gate_id}")
        elif result.get("result") == "approved_with_gap" and (
            state["risk"]["high_risk"] or state["environment"] in {"staging", "production"}
        ):
            failures.append(f"approved gap is forbidden for high-risk/staging/production: {gate_id}")
        elif object_hash(result, "result_hash") != result.get("result_hash"):
            failures.append(f"gate result hash mismatch: {gate_id}")
    if failures:
        for failure in failures:
            print(f"BLOCK: {failure}")
        return 1
    previous = state["state_hash"]
    state["previous_state_hash"] = previous
    state["stage"]["completed"].append(state["stage"]["current"])
    state["stage"]["current"] = args.to_stage
    state["stage"]["sequence"] += 1
    state["stage"]["turns"] = 0
    state["stage"]["required_gates"] = gates_for_stage(args.to_stage)
    state["gate_result_refs"] = [str(path.resolve()) for path in args.gate_result]
    state["approved_gaps"] = list(dict.fromkeys(state.get("approved_gaps", []) + [
        f"approved validator outage at {item['gate_id']}: {item['human_approval']['evidence_ref']}"
        for item in results if item.get("result") == "approved_with_gap"
    ]))
    state["status"] = "completed" if args.to_stage == "learn_retire" else "in_progress"
    state["updated_at"] = now()
    state["state_hash"] = object_hash(state, "state_hash")
    failures = schema_failures(state, "execution-state.schema.json")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    dump(args.output.resolve(), state)
    print(f"PASS: advanced to {args.to_stage}; previous state {previous[:12]}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create_contract = create.add_mutually_exclusive_group(required=True)
    create_contract.add_argument("--truth", type=Path)
    create_contract.add_argument("--discovery-contract", type=Path)
    create.add_argument("--config", type=Path, required=True)
    create.add_argument(
        "--installed-skill", type=Path, default=ROOT,
        help="installed skill directory or its SKILL.md file",
    )
    create.add_argument("--assurance-evidence", type=Path)
    create.add_argument("--environment", choices=["development", "test", "staging", "production"])
    create.add_argument("--execution-id", default="EXEC-LOCAL-001")
    create.add_argument("--project-id")
    create.add_argument("--output", type=Path, required=True)
    create.set_defaults(func=create_state)

    verify = sub.add_parser("verify")
    verify.add_argument("--state", type=Path, required=True)
    verify.set_defaults(func=verify_state)

    gate = sub.add_parser("gate")
    gate.add_argument("--state", type=Path, required=True)
    gate.add_argument("--gate-id", choices=ALL_GATES, required=True)
    gate.add_argument("--projection", type=Path, action="append", default=[])
    gate.add_argument("--human-approval", type=Path)
    gate.add_argument("--service-outage", action="store_true", help="Record a real validator outage; never treat it as an implicit pass")
    gate.add_argument("--output", type=Path, required=True)
    gate.set_defaults(func=gate_state)

    checkpoint = sub.add_parser("checkpoint")
    checkpoint.add_argument("--state", type=Path, required=True)
    checkpoint_contract = checkpoint.add_mutually_exclusive_group(required=True)
    checkpoint_contract.add_argument("--truth", type=Path)
    checkpoint_contract.add_argument("--discovery-contract", type=Path)
    checkpoint.add_argument("--config", type=Path)
    checkpoint.add_argument("--assurance-evidence", type=Path)
    checkpoint.add_argument("--output", type=Path, required=True)
    checkpoint.set_defaults(func=checkpoint_state)

    turn = sub.add_parser("record-turn")
    turn.add_argument("--state", type=Path, required=True)
    turn.add_argument("--output", type=Path, required=True)
    turn.set_defaults(func=record_turn)

    advance = sub.add_parser("advance")
    advance.add_argument("--state", type=Path, required=True)
    advance.add_argument("--to", dest="to_stage", choices=STAGES[1:], required=True)
    advance.add_argument("--gate-result", type=Path, action="append", required=True)
    advance.add_argument("--output", type=Path, required=True)
    advance.set_defaults(func=advance_state)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
