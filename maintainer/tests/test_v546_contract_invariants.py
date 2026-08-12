"""5.4.6 cross-entry, fragile-surface, domain and trust-boundary regressions."""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
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
    assert "5.4.6" in versions
    custom = tmp_path / "custom"
    assert run("scripts/ai_delivery_spec_cli.py", "init-custom", "--output", str(custom)).returncode == 0
    rule = yaml.safe_load((custom / "validators/my-team.yaml").read_text(encoding="utf-8"))["rules"][0]
    assert rule["domains"] == ["my-team"]


def _prototype_codes(path: Path, raw: str) -> set[str]:
    path.write_text(raw, encoding="utf-8")
    gate = Gate()
    gate.check_prototype(path, "L2")
    return {item.code for item in gate.findings}


def test_metric_ids_cannot_collapse_distinct_business_meanings(tmp_path: Path) -> None:
    bad = _prototype_codes(tmp_path / "bad-metric.html",
        '<main data-testid="page-VIEW-METRIC-001"><div data-metric="METRIC-DYNAMIC-CARD">Pending enterprises 8</div>'
        '<div data-metric="METRIC-DYNAMIC-CARD">Abnormal vehicles 12</div></main>')
    assert "PROTO-METRIC-ID-SEMANTIC-COLLISION" in bad
    dynamic = _prototype_codes(tmp_path / "dynamic-metric.html", '<main data-testid="page-VIEW-METRIC-003"></main><script>function metric(label,value){return `<div data-metric="METRIC-DYNAMIC-CARD">${label}:${value}</div>`}metric("A",1);metric("B",2)</script>')
    assert "PROTO-DYNAMIC-METRIC-ID-REUSE" in dynamic
    good = _prototype_codes(tmp_path / "good-metric.html",
        '<main data-testid="page-VIEW-METRIC-002">'
        '<div data-metric="METRIC-ENTERPRISE-PENDING" data-metric-label="Pending enterprises">Pending enterprises 8</div>'
        '<div data-metric="METRIC-ENTERPRISE-PENDING" data-metric-label="Pending enterprises">Pending enterprises 12</div></main>')
    assert not {"PROTO-METRIC-ID-SEMANTIC-COLLISION", "PROTO-METRIC-LABEL-MISSING"} & good


def test_review_projection_requires_bidirectional_link_and_real_role_lenses(tmp_path: Path) -> None:
    broken = _prototype_codes(tmp_path / "review-broken.html",
        '<body class="review-mode"><main data-testid="page-VIEW-REVIEW-001">'
        '<button data-action="UIACT-REVIEW-SELECT" data-review-id="REV-1" aria-current="true">1</button>'
        '<button data-action="UIACT-REVIEW-LENS" data-review-role="frontend">Frontend</button></main></body>')
    assert {"PROTO-REVIEW-LINKAGE-MISSING", "PROTO-REVIEW-SELECTION-NOT-SYNCED", "PROTO-REVIEW-LENS-COSMETIC"} <= broken

    valid = _prototype_codes(tmp_path / "review-linked.html", '''<body class="review-mode"><main data-testid="page-VIEW-REVIEW-002">
<button data-action="UIACT-REVIEW-SELECT" data-review-id="REV-1" aria-current="true">1</button><aside data-review-id="REV-1" aria-current="true">Entry</aside>
<button data-action="UIACT-REVIEW-LENS-FRONTEND" data-review-role="frontend">Frontend</button><section data-review-lens="frontend">Entry, state, feedback</section>
<script>document.addEventListener('click',e=>{const action=e.target.dataset.action,reviewId=e.target.dataset.reviewId;if(action==='UIACT-REVIEW-SELECT')document.querySelectorAll('[data-review-id]').forEach(n=>n.setAttribute('aria-current',n.dataset.reviewId===reviewId?'true':'false'));if(action==='UIACT-REVIEW-LENS-FRONTEND')document.body.setAttribute('data-state','frontend')});</script></main></body>''')
    assert not {"PROTO-REVIEW-LINKAGE-MISSING", "PROTO-REVIEW-SELECTION-NOT-SYNCED", "PROTO-REVIEW-LENS-COSMETIC"} & valid


def test_unknown_priority_cannot_drift_between_frontmatter_and_human_table(tmp_path: Path) -> None:
    prd = tmp_path / "unknown-drift.md"
    prd.write_text(
        """---
document_language: zh-CN
delivery_level: L0
open_p0_unknown_ids:
  - UNK-METRIC-001
unknowns:
  - id: UNK-METRIC-001
    priority: P0
    status: blocked
    blocks_stage: review
    affected_refs: [REQ-METRIC-001]
---
# Metric requirement
| UNK ID | Question | Priority | Status | Blocks stage |
|---|---|---|---|---|
| UNK-METRIC-001 | Dedup key | P1 | open | baseline |
""",
        encoding="utf-8",
    )
    gate = Gate()
    gate.check_prd(prd, "L0", stage="review")
    assert "PRD-UNKNOWN-METADATA-DRIFT" in {item.code for item in gate.findings}


def test_review_unknowns_require_owned_stage_aware_contracts(tmp_path: Path) -> None:
    incomplete = _prototype_codes(
        tmp_path / "unknown-incomplete.html",
        '<body class="review-mode"><main data-testid="page-VIEW-UNK-001">'
        '<div data-metric="METRIC-UNK-001" data-unk="UNK-METRIC-001">待确认</div>'
        '<button data-review-id="REV-UNK-001" aria-current="true">1</button>'
        '<aside data-review-id="REV-UNK-001" aria-current="true">指标说明</aside></main></body>',
    )
    assert "PROTO-UNKNOWN-CONTRACT-INCOMPLETE" in incomplete

    complete = _prototype_codes(
        tmp_path / "unknown-complete.html",
        '<body class="review-mode"><main data-testid="page-VIEW-UNK-002">'
        '<div data-metric="METRIC-UNK-002" data-unk="UNK-METRIC-002" data-unk-priority="P1" '
        'data-unk-owner="产品负责人" data-unk-blocks-stage="baseline" '
        'data-unk-affected-refs="METRIC-UNK-002,AC-UNK-002" data-unk-fallback="显示—且不参与验收">待确认</div>'
        '<button data-review-id="REV-UNK-002" aria-current="true">1</button>'
        '<aside data-review-id="REV-UNK-002" aria-current="true">指标说明</aside></main></body>',
    )
    assert "PROTO-UNKNOWN-CONTRACT-INCOMPLETE" not in complete

    registry = _prototype_codes(
        tmp_path / "unknown-registry.html",
        '<main data-testid="page-VIEW-UNK-003"></main><script>const unknowns=['
        "{unk:'UNK-METRIC-003',priority:'P0',owner:'业务负责人',blocks_stage:'review',"
        "affected_refs:['METRIC-UNK-003'],fallback:'隐藏指标'}];</script>",
    )
    assert "PROTO-UNKNOWN-CONTRACT-INCOMPLETE" not in registry


def test_trace_release_proxy_is_complete_and_honest() -> None:
    definitions = yaml.safe_load((ROOT / "maintainer/evals/metric-definitions.yaml").read_text(encoding="utf-8"))
    proxy = definitions["trace_release_proxy"]
    assert set(proxy["dimensions"]) == {"trust", "reliability", "adaptability", "convention", "effectiveness"}
    assert "not the platform algorithm" in proxy["purpose"]
    assert all(item["local_evidence"] for item in proxy["dimensions"].values())
    status = yaml.safe_load((ROOT / "maintainer/evals/evidence/release-status.yaml").read_text(encoding="utf-8"))
    assert status["trace_release_proxy"]["dimensions"]["effectiveness"] == "partial"
    assert "not a SkillHub score" in status["trace_release_proxy"]["boundary"]


def _write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    body = "".join(f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>" for text in paragraphs)
    xml = '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">' + f"<w:body>{body}</w:body></w:document>"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)


def test_human_projection_and_distribution_gate_prevent_word_metadata_leak(tmp_path: Path) -> None:
    canonical = tmp_path / "PRD.md"
    human = tmp_path / "PRD.human.md"
    canonical.write_text(
        "---\ndocument_language: en-US\ndelivery_level: L2\n---\n<!-- ADS:SECTION:SUMMARY -->\n# Product requirement\n\nBody.\n",
        encoding="utf-8",
    )
    projected = run("scripts/ai_delivery_spec_cli.py", "project-human", "--input", str(canonical), "--output", str(human))
    assert projected.returncode == 0
    rendered = human.read_text(encoding="utf-8")
    assert rendered.startswith("# Product requirement") and "document_language:" not in rendered and "ADS:" not in rendered

    bad_docx = tmp_path / "bad.docx"
    _write_minimal_docx(bad_docx, ["---", "document_language: en-US", "# Product requirement", "**Body**"])
    bad = run("scripts/ai_delivery_spec_cli.py", "check-distribution", "--document", str(bad_docx), "--format", "json")
    assert bad.returncode == 2 and json.loads(bad.stdout)["status"] == "BLOCKED"

    clean_docx = tmp_path / "clean.docx"
    _write_minimal_docx(clean_docx, ["Product requirement", "Body content"])
    clean = run("scripts/ai_delivery_spec_cli.py", "check-distribution", "--document", str(clean_docx), "--format", "json")
    assert clean.returncode == 0 and json.loads(clean.stdout)["status"] == "PASS"
