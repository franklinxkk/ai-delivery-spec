"""Static checks, authorization and receipt handling at the public delivery boundaries."""
import hashlib
import json
from pathlib import Path
import sys

import pytest
import yaml

from test_evidence_scope_regressions import run_cli, save, write_run
from test_v555_reference_resolution import BODY, run as build_handoff_fixture

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from quality_gate import Gate, collect_acceptance_claims
from triage_requirement import recommend
from validators.validate_prd_semantics import check_pending_execution


def test_triage_questions_follow_evidence_and_leave_small_edit_direct():
    result = recommend({"title": "加一个自动审批，超时就通过"})
    assert result["recommendation"] == "clarify" and result["lifecycle_mutated"] is False
    assert any("超时" in q and "谁" in q for q in result["next_questions"])
    assert any("授权" in q for q in recommend({"title": "AI 自动发送退款通知"})["next_questions"])
    known = recommend({"title": "将保存按钮改名为提交"})
    assert (known["recommendation"], known["next_questions"]) == ("accept", [])


@pytest.mark.parametrize("text,blocked", [
    ("退款规则仍待确认。确认前系统必须先默认执行。", True),
    ("退款规则待确认。已批准的付款按原规则执行。", False),
    ("退款规则待确认。付款确认前系统应按默认执行。", False),
    ("退款规则待确认。确认前不得按默认执行。", False),
    ("退款规则待确认。已授权的临时方案规定确认前系统必须按默认执行。", False),
])
def test_adjacent_explicit_instruction(text, blocked):
    assert bool(check_pending_execution(text)) == blocked


def bound_run(folder):
    path, doc = write_run(folder, conclusion="accepted", baseline="1.3")
    raw = (ROOT / "examples/medium-review-handoff/requirement.md").read_text("utf-8")
    baseline = folder / "baseline.md"
    baseline.write_bytes(raw.replace("\n", "\r\n").encode("utf-8"))
    doc["baseline_hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    save(path, doc)
    return path, doc, baseline


def test_acceptance_matches_content_and_version_at_both_entries(tmp_path):
    path, doc, baseline = bound_run(tmp_path)
    cli = "validators/validate_acceptance_run.py"
    assert run_cli(cli, path, "--baseline", baseline).returncode == 0
    assert collect_acceptance_claims(Gate(), [path], baseline)
    assert not collect_acceptance_claims(Gate(), [path])
    doc["baseline_version"] = "2.0"
    save(path, doc)
    assert "ACCEPTANCE-BASELINE-VERSION" in run_cli(cli, path, "--baseline", baseline).stdout
    doc["baseline_version"] = "1.3"
    save(path, doc)
    baseline.write_text(baseline.read_text("utf-8") + "\nA material revision.", "utf-8")
    assert "ACCEPTANCE-BASELINE-HASH" in run_cli(cli, path, "--baseline", baseline).stdout
    assert not collect_acceptance_claims(Gate(), [path], baseline)


def test_acceptance_legacy_and_undefined_criterion(tmp_path):
    path, doc, baseline = bound_run(tmp_path)
    cli = "validators/validate_acceptance_run.py"
    doc["items"][0]["acceptance_ref"] = "AC-OTHER-SCOPE"
    save(path, doc)
    assert "ACCEPTANCE-BASELINE-AC" in run_cli(cli, path, "--baseline", baseline).stdout
    del doc["baseline_hash"]
    save(path, doc)
    legacy = run_cli(cli, path)
    assert legacy.returncode == 0 and "未比对当前规格" in legacy.stdout
    assert "ACCEPTANCE-BASELINE-HASH" in run_cli(cli, path, "--baseline", baseline).stdout


@pytest.mark.parametrize("refs,ok", [
    (["https://example.invalid/run"], False), (["empty.txt"], False),
    (["one.yaml"], False), (["missing.txt"], False),
    (["https://example.invalid/run", "evidence.txt"], True),
])
def test_bound_run_requires_readable_local_receipt(tmp_path, refs, ok):
    path, doc, baseline = bound_run(tmp_path)
    (tmp_path / "empty.txt").touch()
    doc["items"][0]["evidence_refs"] = refs
    save(path, doc)
    assert bool(collect_acceptance_claims(Gate(), [path], baseline)) == ok


@pytest.mark.parametrize("refs,strict_ok", [
    (["https://example.invalid/review"], False), (["review.yaml"], False),
    (["signed-review.txt"], True),
])
def test_review_without_findings_still_checks_signoff_receipt_when_requested(tmp_path, refs, strict_ok):
    path = tmp_path / "review.yaml"
    (tmp_path / "signed-review.txt").write_text("Synthetic review fixture", "utf-8")
    doc = dict(schema_version="5.4.0", review_id="REVIEW-X", baseline_version="1", status="completed",
               requirement_refs=["REQ-X"], reviewed_artifact_refs=["baseline.md"], reviewed_at="2026-11-01T15:00:00+08:00",
               review_type="qa", required_review_types=["qa"], reviewers=["fixture"], findings=[],
               sign_offs=[dict(actor="fixture", review_type="qa", decision="approve",
                               at="2026-11-01T15:01:00+08:00", evidence_refs=refs)])
    save(path, doc)
    cli = "validators/validate_review_record.py"
    legacy = run_cli(cli, path)
    assert legacy.returncode == 0 and "declaration checks" in legacy.stdout
    strict = run_cli(cli, path, "--verify-evidence")
    assert (strict.returncode == 0) == strict_ok, strict.stdout


@pytest.mark.parametrize("status,actor,sources,scope,policy_ref,blocked", [
    ("confirmed", "owner", ["minutes #2"], ["REQ-REPORT"], "DEC-SLA", False),
    ("proposed", "owner", ["minutes #2"], ["REQ-REPORT"], "DEC-SLA", True),
    ("confirmed", "", ["minutes #2"], ["REQ-REPORT"], "DEC-SLA", True),
    ("confirmed", "owner", [], ["REQ-REPORT"], "DEC-SLA", True),
    ("confirmed", "owner", ["minutes #2"], ["REQ-BILLING"], "DEC-SLA", True),
    ("confirmed", "owner", ["minutes #2"], ["REQ-REPORT"], "DEC-MISSING", True),
    ("proposed", "", [], ["REQ-OTHER"], None, False),
])
def test_ready_packet_checks_only_referenced_policy(tmp_path, status, actor, sources, scope, policy_ref, blocked):
    decision = dict(id="DEC-SLA", status=status, actor=actor, source_refs=sources, affected_refs=scope)
    header = yaml.safe_dump({"decisions": [decision]})
    build_handoff_fixture(tmp_path, body="---\n" + header + "---\n" + BODY)
    path = tmp_path / "handoff.yaml"
    doc = yaml.safe_load(path.read_text("utf-8"))
    if policy_ref:
        doc["packets"][0]["decision_refs"] = [policy_ref]
    save(path, doc)
    gate = Gate()
    gate.check_agent_handoff(path)
    assert ("HANDOFF-DECISION-UNRESOLVED" in {f.code for f in gate.findings}) == blocked


def test_unrecognized_main_and_explicit_support_get_distinct_acceptance_routes(tmp_path):
    path, _ = write_run(tmp_path, conclusion="accepted")
    extra = tmp_path / "extra.yaml"
    args = ("route-stage", "--target", "acceptance", "--artifact", path, "--artifact", extra, "--format", "json")
    for role, blocked in [("main", True), ("supporting", False)]:
        save(extra, {"artifact": "unrecognized_specification", "artifact_role": role})
        result = run_cli("ai_delivery_spec_cli.py", *args)
        assert result.stdout, result.stderr
        report = json.loads(result.stdout)
        assert report["assessment"]["kind"] == "route_check" and "业务签收" in report["not_proven"]
        assert ("ROUTE-UNKNOWN-ACCEPTANCE-INPUT" in {f["code"] for f in report["findings"]}) == blocked


def test_url_only_signature_does_not_bind_acceptance_to_a_readable_receipt(tmp_path):
    path, doc, baseline = bound_run(tmp_path)
    doc["sign_offs"][0]["evidence_ref"] = "https://example.invalid/signature"
    save(path, doc)
    result = run_cli("validators/validate_acceptance_run.py", path, "--baseline", baseline)
    assert result.returncode == 1 and "签认回执" in result.stdout


def test_prd_only_handoff_reports_real_document_entry():
    prd = ROOT / "examples/medium-review-handoff/requirement.md"
    command = "ai_delivery_spec_cli.py"
    result = run_cli(command, "gate", "--profile", "handoff", "--prd", prd, "--format", "json", "--diagnostics", "full")
    assert result.returncode != 0
    assert "--profile prd" in result.stdout and "--profile agent_handoff" in result.stdout
    direct = run_cli(command, "gate", "--profile", "prd", "--prd", prd, "--format", "json")
    assert json.loads(direct.stdout)["status"] == "PASS"
