"""Read interactions need results, not invented persistence obligations."""
import json
from pathlib import Path
import re
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/validators")]
from quality_gate import Gate, guidance_for


def workspace():
    raw = (ROOT / "examples/medium-review-handoff/review-prototype.html").read_text(encoding="utf-8")
    return json.loads(re.search(r'<script\b[^>]*id=[\'"]review-workspace-manifest[\'"][^>]*>(.*?)</script>', raw, re.S)[1])


def prototype(path, script, *, manifest=None, extra="", label="Read policy"):
    metadata = ('<script type="application/json" id="review-workspace-manifest">' +
                json.dumps(manifest, ensure_ascii=False) + '</script>') if manifest is not None else ''
    path.write_text('<!doctype html><html lang="en"><body><main data-testid="page-VIEW-X">'
                    '<button data-action="ACT-X-CONFIRM" onclick="perform()">' + label + '</button>'
                    '<section id="result" data-testid="region-REG-RESULT"></section></main>' +
                    extra + metadata + '<script>' + script + '</script></body></html>', encoding="utf-8")
    return path


def inspect(path, level="L2", gate=None):
    gate = gate or Gate()
    gate.check_prototype(path, level)
    return gate


def codes(gate):
    return {f.code for f in gate.findings}


@pytest.mark.parametrize("level", ["L0", "L2", "L3", "L4"])
def test_read_list_detail_has_no_domain_write_obligation_even_without_readonly_keyword(tmp_path, level):
    path = prototype(tmp_path / "policy.html", "function perform(){document.getElementById('result').textContent='Authorized policy';}")
    gate = inspect(path, level)
    assert "PROTO-NO-DOMAIN-STATE" not in codes(gate)
    assert gate.metrics["prototype_domain_write_check"]["status"] == "no_supplied_write_obligation"


def test_validated_read_semantics_do_not_create_write_duties(tmp_path):
    manifest = workspace()
    for item in manifest["semantic_coverage_items"]:
        item["semantic_type"] = "action"
    gate = inspect(prototype(tmp_path / "read.html", "function perform(){document.getElementById('result').textContent='Policy details';}", manifest=manifest))
    assert gate.review_workspace_contracts  # An actual schema-checked declaration was consumed.
    assert "PROTO-NO-DOMAIN-STATE" not in codes(gate)


@pytest.mark.parametrize("kind", ["data_write", "state_transition"])
def test_explicit_write_obligation_with_toast_only_still_reports_at_its_source(tmp_path, kind):
    manifest = workspace()
    manifest["semantic_coverage_items"][1]["semantic_type"] = kind
    path = prototype(tmp_path / "write.html", "function perform(){alert('Saved');}", manifest=manifest,
                     label="Read-only banner cannot waive a declared write")
    gate = inspect(path, "L0")  # Duties come from scope, not the old level.
    assert {"PROTO-NO-DOMAIN-STATE", "PROTO-TRANSIENT-ONLY"} <= codes(gate)
    issue = next(f for f in gate.findings if f.code == "PROTO-NO-DOMAIN-STATE")
    assert issue.severity == "GAP" and "SCOV-DRAWER-CONFIRM" in issue.ref and issue.binding_source_refs


def test_plain_toast_only_keeps_outcome_review_without_inventing_a_write(tmp_path):
    gate = inspect(prototype(tmp_path / "plain.html", "function perform(){alert('Done');}"))
    assert "PROTO-TRANSIENT-ONLY" in codes(gate)
    assert "PROTO-NO-DOMAIN-STATE" not in codes(gate)
    issue = next(f for f in gate.findings if f.code == "PROTO-TRANSIENT-ONLY")
    assert "若结果本就仅为提示" in issue.message


def test_missing_action_is_not_excused_by_readonly_prose(tmp_path):
    path = tmp_path / "missing.html"
    path.write_text('<main data-testid="page-VIEW-X">Read-only list'
                    '<button data-action="ACT-DETAIL">Details</button></main>', encoding="utf-8")
    gate = inspect(path)
    assert any(f.code == "PROTO-UNHANDLED-ACTION" and f.severity == "BLOCK" for f in gate.findings)
    assert "PROTO-NO-VISIBLE-RESULT" in codes(gate)


def test_write_probe_needs_no_artificial_dom_state_field_and_does_not_claim_execution(tmp_path):
    path = prototype(tmp_path / "write.html",
                     "const state={};function perform(){state.status='saved';document.getElementById('result').textContent=state.status;}", manifest=workspace())
    gate = inspect(path)
    assert gate.metrics["prototype_states"] == 0
    assert "PROTO-NO-DOMAIN-STATE" not in codes(gate)
    assert gate.metrics["prototype_domain_write_check"]["status"] == "static_mechanism_observed_not_executed"


def test_domain_reads_and_external_calls_are_not_mutation_proof(tmp_path):
    path = prototype(tmp_path / "external.html",
                     "const state={};function perform(){fetch('/save');document.getElementById('result').textContent=state.status;}",
                     manifest=workspace(), extra='<script src="https://example.invalid/adapter.js"></script>')
    gate = inspect(path)
    assert {"PROTO-NO-DOMAIN-STATE", "PROTO-REMOTE-DEPENDENCY"} <= codes(gate)
    assert gate.metrics["prototype_domain_write_check"]["status"] == "declared_write_unproven"


def test_arbitrary_review_evidence_cannot_clear_business_write_gap(tmp_path):
    path = prototype(tmp_path / "write.html", "function perform(){alert('Saved');}", manifest=workspace())
    evidence = tmp_path / "evidence.json"
    evidence.write_text('{"status":"passed","observations":[]}', encoding="utf-8")
    gate = Gate()
    gate.review_runtime_evidence = evidence
    gate.runtime_verified_actions = {"ACT-X-CONFIRM"}
    inspect(path, gate=gate)
    assert "PROTO-NO-DOMAIN-STATE" in codes(gate)


def test_invalid_manifest_cannot_establish_duty_or_escape_schema_block(tmp_path):
    manifest = workspace()
    manifest["semantic_coverage_items"][1].pop("source_refs")
    gate = inspect(prototype(tmp_path / "invalid.html", "function perform(){alert('Saved');}", manifest=manifest))
    assert "PROTO-REVIEW-WORKSPACE-SCHEMA" in codes(gate)
    assert gate.metrics["prototype_domain_write_check"]["obligation_refs"] == []


def test_obligations_do_not_leak_to_next_file(tmp_path):
    gate = inspect(prototype(tmp_path / "write.html", "function perform(){alert('Saved');}", manifest=workspace()))
    path = prototype(tmp_path / "read.html", "function perform(){document.getElementById('result').textContent='Details';}")
    gate.findings.clear()
    inspect(path, gate=gate)
    assert "PROTO-NO-DOMAIN-STATE" not in codes(gate)


def test_diagnostic_does_not_tell_readonly_authors_to_add_technical_fields():
    cause, fix = guidance_for("PROTO-NO-DOMAIN-STATE")
    assert "只读" in fix and "不需加写功能或技术字段" in fix
