"""Small distinguishing cases for evidence scope and existing-template compatibility."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from quality_gate import Gate, collect_acceptance_claims, check_browser_coverage, repair_example_for
from requirement_contract import check_spec


def write_run(folder, name="one", *, ac="AC-X-SUBMIT", execution="browser", conclusion="pending"):
    doc = yaml.safe_load((ROOT / "references/templates/acceptance-run-template.yaml").read_text(encoding="utf-8"))
    doc.update(run_id="ARUN-" + name.upper(), baseline_version="1.1", execution_type=execution,
               environment="Chrome" if execution == "browser" else "Node simulation", executor="fixture",
               executed_at="2026-11-01T15:00:00+08:00", conclusion=conclusion)
    doc["items"][0].update(acceptance_ref=ac, result="pass", actual_result="Synthetic observation", evidence_refs=["evidence.txt"])
    if conclusion == "accepted":
        doc["sign_offs"] = [dict(role="fixture", actor="fixture", decision="approve", at="2026-11-01T15:01:00+08:00", evidence_ref="evidence.txt")]
    (folder / "evidence.txt").write_text("SYNTHETIC CHECKER FIXTURE; not customer evidence", encoding="utf-8")
    path = folder / (name + ".yaml")
    save(path, doc)
    return path, doc


def save(path, doc):
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")


def run_cli(script, *args):
    return subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8",
                          env=dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1"), timeout=30)


def scope_gate(folder, *, baseline="1.1"):
    gate = Gate()
    proto = (folder / "prototype.html").resolve()
    gate.prototype_acceptance_by_path[proto] = {"AC-X-SUBMIT", "AC-X-CONFIRM"}
    if baseline:
        gate.review_workspace_contracts.append((proto, {"baseline": {"version": baseline}}))
    return gate


def test_existing_tables_locate_content_but_empty_or_example_tables_do_not():
    for labels in ("模块|当前行为|调整后行为|验收", "Module|Before|After|Acceptance"):
        table = f"|{labels}|\n|---|---|---|---|\n|备注|100字|200字|201字拒绝并保留输入|\n"
        assert not check_spec({}, table)[0]
        empty = table.replace("201字拒绝并保留输入", "")
        assert any(item["code"] == "SPEC-EMPTY-SECTION" for item in check_spec({}, empty)[0])
        fenced = "```markdown\n" + table + "```"
        assert any(item["code"] == "SPEC-REVIEW-LOCATION" for item in check_spec({}, fenced)[0])
    assert "confirmed" not in repair_example_for("SPEC-REVIEW-LOCATION")


def test_accepted_record_requires_actual_execution_in_both_entries(tmp_path):
    path, doc = write_run(tmp_path, conclusion="accepted")
    assert run_cli("validators/validate_acceptance_run.py", path).returncode == 0
    assert Gate().check_acceptance_run(path)[2]
    doc["items"][0].update(mandatory=False, result="not_run", actual_result="", evidence_refs=[])
    save(path, doc)
    result = run_cli("validators/validate_acceptance_run.py", path)
    gate = Gate()
    assert not gate.check_acceptance_run(path)[2]
    assert result.returncode == 1 and "ACCEPTANCE-NO-EXECUTION" in result.stdout
    assert "ACCEPTANCE-NO-EXECUTION" in {item.code for item in gate.findings}
    doc.update(conclusion="pending", sign_offs=[], executed_at=None)
    save(path, doc)
    assert run_cli("validators/validate_acceptance_run.py", path).returncode == 0


def test_one_pass_cannot_mask_another_case_for_the_same_ac(tmp_path):
    path, doc = write_run(tmp_path)
    other = copy.deepcopy(doc["items"][0])
    other.update(id="ARITEM-X-002", result="fail", actual_result="Second case failed")
    doc["items"].append(other)
    save(path, doc)
    assert run_cli("validators/validate_acceptance_run.py", path).returncode == 0
    assert Gate().check_acceptance_run(path) == (set(), True, False)
    other.update(result="pass", actual_result="Second case now passes")
    save(path, doc)
    assert Gate().check_acceptance_run(path)[0] == {"AC-X-SUBMIT"}
    other.update(result="blocked", actual_result="")
    save(path, doc)
    assert "ACCEPTANCE-RESULT-MISSING" in run_cli("validators/validate_acceptance_run.py", path).stdout


def test_browser_coverage_keeps_environment_baseline_and_execution_together(tmp_path):
    first, _ = write_run(tmp_path)
    second, doc = write_run(tmp_path, "two", ac="AC-X-CONFIRM")
    def coverage():
        gate = scope_gate(tmp_path)
        claims = collect_acceptance_claims(gate, [first, second])
        return check_browser_coverage(gate, claims, "L3"), claims
    complete, claims = coverage()
    assert complete and not any(item["conclusive"] for item in claims.values())
    doc.update(execution_type="simulation", environment="Node simulation")
    save(second, doc)
    assert not coverage()[0]
    doc.update(execution_type="browser", environment="Chrome", baseline_version="0.9")
    save(second, doc)
    assert not coverage()[0]
    doc["baseline_version"] = "1.1"
    save(second, doc)
    assert coverage()[0]
    gate = scope_gate(tmp_path, baseline="")
    assert not check_browser_coverage(gate, collect_acceptance_claims(gate, [first, second]), "L2")
    assert not gate.findings  # Unknown applicability does not impose metadata on an ordinary small prototype.


def test_duplicate_records_are_order_independent_and_not_silently_overwritten(tmp_path):
    first, doc = write_run(tmp_path)
    second = tmp_path / "duplicate.yaml"
    save(second, doc)
    for order in ([first, second], [second, first]):
        gate = Gate()
        assert not collect_acceptance_claims(gate, order)
        assert "ACCEPTANCE-DUPLICATE-RUN" in {item.code for item in gate.findings}
    gate = Gate()
    assert len(collect_acceptance_claims(gate, [first, first])) == 1
    assert gate.metrics["acceptance_run_items"] == 1
    doc["executed_at"] = None  # An invalid conflicting record must not leave its twin usable.
    save(second, doc)
    assert not collect_acceptance_claims(Gate(), [first, second])


def test_legacy_completion_needs_records_but_unfinished_migration_is_valid_in_a_draft(tmp_path):
    doc = yaml.safe_load((ROOT / "references/templates/change-request-template.yaml").read_text(encoding="utf-8"))
    path = tmp_path / "change.yaml"
    doc["impacts"]["data_migration"]["required"] = True
    save(path, doc)
    assert run_cli("validators/validate_change_package.py", path).returncode == 0
    doc["status"] = "approved"
    doc["approvals"] = [dict(role="fixture", actor="fixture", decision="approved", decided_at="2026-11-01T15:00:00Z")]
    doc["diff"] = [dict(ref="REQ-X", path="scope", before="old", after="new", reason="authorized change")]
    save(path, doc)
    assert "migration requires real strategy" in run_cli("validators/validate_change_package.py", path).stdout
    doc["impacts"]["data_migration"].update(strategy="Copy affected records", rollback="Restore prior copy")
    for version in ("5.0.0", "5.1.0"):
        doc["schema_version"] = version
        save(path, doc)
        assert run_cli("validators/validate_change_package.py", path).returncode == 0
        omitted = copy.deepcopy(doc)
        omitted["approvals"] = []
        save(path, omitted)
        assert "requires approval records" in run_cli("validators/validate_change_package.py", path).stdout
        omitted["approvals"] = [dict(doc["approvals"][0], decision="pending")]
        save(path, omitted)
        assert "non-approved decisions" in run_cli("validators/validate_change_package.py", path).stdout


def test_real_gate_consumes_current_browser_records_without_inventing_signoff(tmp_path):
    paths = [write_run(tmp_path)[0], write_run(tmp_path, "two", ac="AC-X-CONFIRM")[0]]
    args = ["gate", "--profile", "prototype", "--level", "L3", "--prototype",
            ROOT / "examples/medium-review-handoff/review-prototype.html", "--format", "json"]
    for path in paths:
        args += ["--acceptance-run", path]
    result = run_cli("ai_delivery_spec_cli.py", *args)
    payload = json.loads(result.stdout)
    # This sample has unrelated L3 findings: inspect only the changed evidence claim.
    assert payload["metrics"]["prototype_browser_evidence"] is True
    assert payload["metrics"]["acceptance_run_conclusive"] is False
    assert not any(item["code"].startswith("PROTO-BROWSER-EVIDENCE") for item in payload["findings"])
