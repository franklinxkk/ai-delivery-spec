"""5.4.5 cross-entry, authority-surface, domain and trust-boundary regressions."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from quality_gate import Gate  # noqa: E402
from validators.validate_prd_semantics import run_semantic_checks  # noqa: E402


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_change_consumers_share_controlled_nested_shape_boundary(tmp_path: Path) -> None:
    change = yaml.safe_load((ROOT / "references/templates/change-request-template.yaml").read_text(encoding="utf-8"))
    change["request"]["seed_refs"] = []
    truth, request = tmp_path / "truth.yaml", tmp_path / "change.yaml"
    dump(truth, {"requirements": [{"id": "REQ-CORE-001"}]})
    change["impacts"]["requirements"] = ["REQ-CORE-001"]
    dump(request, change)
    analyzer = run("scripts/analyze_change_impact.py", "--truth", str(truth), "--change", str(request))
    validator = run("scripts/validators/validate_change_package.py", str(request))
    assert analyzer.returncode == 2 and "impacts.requirements[0] must be an object" in analyzer.stdout
    assert validator.returncode == 1 and "is not of type 'object'" in validator.stdout
    assert "Traceback" not in analyzer.stdout + analyzer.stderr + validator.stdout + validator.stderr

    change["impacts"]["requirements"] = [{"ref": "REQ-CORE-001", "change_type": "modify", "reason": "scope changed"}]
    dump(request, change)
    analyzer = run("scripts/analyze_change_impact.py", "--truth", str(truth), "--change", str(request))
    assert analyzer.returncode == 0 and "REQ-CORE-001" in analyzer.stdout
    template = (ROOT / "references/templates/change-request-template.yaml").read_text(encoding="utf-8")
    assert "ref: REQ-CORE-001" in template and "change_type: modify" in template


def custom_gate(root: Path, *domains: str) -> dict:
    custom = root / "custom"
    dump(custom / "config.yaml", {"domains": [{"domain_id": "securities"}, {"domain_id": "electric-vehicle"}]})
    dump(custom / "validators/ev.yaml", {"rules": [{
        "id": "CUST-EV-DRIVER-SAFETY", "artifact": "prd", "assertion": "must_match",
        "domains": ["electric-vehicle"], "severity": "BLOCK", "pattern": "驾驶安全",
    }]})
    prd = root / "prd.md"
    prd.write_text("---\ndocument_language: zh-CN\ndelivery_level: L0\n---\n# 证券需求\n## 范围\n自选证券。\n## 验收\n保存后可见。\n", encoding="utf-8")
    command = ["scripts/ai_delivery_spec_cli.py", "gate", "--profile", "prd", "--prd", str(prd),
               "--level", "L0", "--custom-root", str(custom), "--format", "json", "--diagnostics", "full"]
    for domain in domains:
        command += ["--domain", domain]
    return json.loads(run(*command).stdout)


def test_custom_rules_require_and_honor_domain_context(tmp_path: Path) -> None:
    securities = custom_gate(tmp_path / "sec", "securities")
    assert "CUST-EV-DRIVER-SAFETY" not in {item["code"] for item in securities["findings"]}
    assert securities["metrics"]["custom_validator_rules_skipped_domain"] == 1
    ev = custom_gate(tmp_path / "ev", "electric-vehicle")
    assert "CUST-EV-DRIVER-SAFETY" in {item["code"] for item in ev["findings"]}
    assert ev["metrics"]["custom_validator_rules_applied"] == 1
    missing = custom_gate(tmp_path / "missing")
    codes = {item["code"] for item in missing["findings"]}
    assert "CUSTOM-DOMAIN-CONTEXT-MISSING" in codes and "CUST-EV-DRIVER-SAFETY" not in codes
    combined = custom_gate(tmp_path / "combined", "securities", "electric-vehicle")
    assert "CUST-EV-DRIVER-SAFETY" in {item["code"] for item in combined["findings"]}
    unknown = custom_gate(tmp_path / "unknown", "unregistered-domain")
    assert "CUSTOM-DOMAIN-UNKNOWN" in {item["code"] for item in unknown["findings"]}


def test_prd_checks_human_decisions_and_definitions_not_references() -> None:
    body = """# 审计需求
### 0.5 澄清、评审与关键决策
| UNK/REV/DEC ID | 原问题/冲突 | 证据 | 影响 | 责任人 | 结论/状态 |
|---|---|---|---|---|---|
| DEC-AUDIT-001 | 数量上限 | 已确认 | REQ-AUDIT-001 | 产品 | 已确认 |
| UNK-AUDIT-001 | 数量上限 | 尚无 | REQ-AUDIT-001 | 产品 | 未关闭 |
## 2. 本期范围
| REQ ID | 需求 | 结论 |
|---|---|---|
| REQ-AUDIT-001 | 支持添加 | 纳入 |
| REQ-AUDIT-001 | 支持删除 | 纳入 |
"""
    codes = {item.code for item in run_semantic_checks(body)}
    assert {"PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT", "PRD-DUPLICATE-STABLE-ID-DEFINITION"} <= codes
    clean = body.replace("| UNK-AUDIT-001 | 数量上限", "| UNK-AUDIT-001 | 数据来源").replace(
        "| REQ-AUDIT-001 | 支持删除 | 纳入 |", "REQ-AUDIT-001 在主流程和异常恢复中均被引用。"
    )
    clean_codes = {item.code for item in run_semantic_checks(clean)}
    assert "PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT" not in clean_codes
    assert "PRD-DUPLICATE-STABLE-ID-DEFINITION" not in clean_codes


def test_prd_checks_conflicts_and_duplicate_definitions_across_tables() -> None:
    body = """# Audit baseline
## Confirmed decisions
| DEC ID | Topic | Status |
|---|---|---|
| DEC-AUDIT-101 | maximum upload size | confirmed |
## Open unknowns
| UNK ID | Question | Status |
|---|---|---|
| UNK-AUDIT-101 | maximum upload size | open |
## Module A definitions
| REQ ID | Requirement |
|---|---|
| REQ-AUDIT-101 | validate before submit |
## Module B definitions
| REQ ID | Requirement |
|---|---|
| REQ-AUDIT-101 | validate after submit |
## Trace mapping
| REQ ID | VIEW ID |
|---|---|
| REQ-AUDIT-101 | VIEW-AUDIT-101 |
| REQ-AUDIT-101 | VIEW-AUDIT-102 |
"""
    codes = {item.code for item in run_semantic_checks(body)}
    assert {"PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT", "PRD-DUPLICATE-STABLE-ID-DEFINITION"} <= codes

    clean = body.replace("| UNK-AUDIT-101 | maximum upload size | open |", "| UNK-AUDIT-101 | retention period | open |").replace(
        "| REQ-AUDIT-101 | validate after submit |", "| REQ-AUDIT-102 | validate after submit |",
    )
    clean_codes = {item.code for item in run_semantic_checks(clean)}
    assert "PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT" not in clean_codes
    assert "PRD-DUPLICATE-STABLE-ID-DEFINITION" not in clean_codes


def prototype_findings(path: Path, iframe: str, level: str) -> list:
    path.write_text(
        f'<main data-testid="page-VIEW-AUDIT-001"><section data-testid="region-REG-AUDIT-001">{iframe}</section></main>',
        encoding="utf-8",
    )
    gate = Gate()
    gate.check_prototype(path, level)
    return gate.findings


def test_remote_iframe_has_level_aware_trust_contract(tmp_path: Path) -> None:
    l2 = prototype_findings(tmp_path / "l2.html", '<iframe src="https://example.com"></iframe>', "L2")
    l0 = prototype_findings(tmp_path / "l0.html", '<iframe src="https://example.com"></iframe>', "L0")
    assert any(item.code == "PROTO-REMOTE-IFRAME-UNDECLARED" and item.severity == "BLOCK" for item in l2)
    assert any(item.code == "PROTO-REMOTE-IFRAME-UNDECLARED" and item.severity == "GAP" for item in l0)
    declared = prototype_findings(
        tmp_path / "declared.html",
        '<iframe src="https://example.com" data-integration-ref="INT-EXT-001" data-fallback="显示重试" '
        'title="外部系统" sandbox referrerpolicy="no-referrer"></iframe>', "L2",
    )
    assert any(item.code == "PROTO-REMOTE-IFRAME-UNVERIFIED" and item.severity == "GAP" for item in declared)
    insecure = prototype_findings(tmp_path / "http.html", '<iframe src="http://example.com"></iframe>', "L0")
    assert any(item.code == "PROTO-INSECURE-REMOTE-IFRAME" and item.severity == "BLOCK" for item in insecure)
    protocol_relative = prototype_findings(tmp_path / "relative-remote.html", '<iframe src="//example.com"></iframe>', "L0")
    assert any(item.code == "PROTO-INSECURE-REMOTE-IFRAME" and item.severity == "BLOCK" for item in protocol_relative)
    unsafe = prototype_findings(tmp_path / "unsafe.html", '<iframe src="javascript:alert(1)"></iframe>', "L0")
    assert any(item.code == "PROTO-IFRAME-UNSAFE-SCHEME" and item.severity == "BLOCK" for item in unsafe)
    nested = prototype_findings(tmp_path / "nested.html", '<iframe src="details.html"></iframe>', "L0")
    assert any(item.code == "PROTO-NESTED-PRODUCT-IFRAME" and item.severity == "BLOCK" for item in nested)


def test_explain_finding_distinguishes_exact_family_and_unknown() -> None:
    exact = run("scripts/ai_delivery_spec_cli.py", "explain-finding", "PRD-DUPLICATE-STABLE-ID-DEFINITION", "--format", "json")
    family = run("scripts/ai_delivery_spec_cli.py", "explain-finding", "CUST-TEAM-001", "--format", "json")
    unknown = run("scripts/ai_delivery_spec_cli.py", "explain-finding", "FAKE-CODE-999", "--format", "json")
    exact_payload = json.loads(exact.stdout)
    assert exact.returncode == 0 and exact_payload["match"] == "exact"
    assert "VIEW-RISK-LIST-001" in exact_payload["repair_example"]
    assert family.returncode == 0 and json.loads(family.stdout)["match"] == "family"
    payload = json.loads(unknown.stdout)
    assert unknown.returncode == 2 and payload["recognized"] is False and payload["match"] == "unknown"
    assert "未知" in payload["cause_zh"] and "unknown" in payload["cause_en"].lower()


def test_version_and_generated_custom_rule_contract(tmp_path: Path) -> None:
    config = json.loads((ROOT / "schemas/spec-config.schema.json").read_text(encoding="utf-8"))
    versions = config["properties"]["execution"]["properties"]["expected_skill_version"]["enum"]
    assert "5.4.5" in versions
    custom = tmp_path / "custom"
    assert run("scripts/ai_delivery_spec_cli.py", "init-custom", "--output", str(custom)).returncode == 0
    rule = yaml.safe_load((custom / "validators/my-team.yaml").read_text(encoding="utf-8"))["rules"][0]
    assert rule["domains"] == ["my-team"]
