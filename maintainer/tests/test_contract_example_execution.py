"""Example conformance must execute the declared contract, not count headings."""
import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "validators"))
from validate_projection_consistency import DIALECT, StrictFormatChecker, verify_examples


def put(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def fixture(tmp_path):
    schema = {"$schema": DIALECT, "$defs": {
        "Operation": {"enum": ["query", "create", "update", "delete"]},
        "Input": {"type": "object", "properties": {"operation": {"$ref": "#/$defs/Operation"}},
                  "required": ["operation"], "additionalProperties": False}}}
    put(tmp_path / "schema.json", schema)
    put(tmp_path / "good.json", {"operation": "query"})
    put(tmp_path / "bad.json", {"operation": "scan"})
    manifest = {"contracts": [{"id": "data-input", "schema": "schema.json#/$defs/Input", "cases": [
        {"id": "query", "instance": "good.json", "valid": True},
        {"id": "unknown-operation", "instance": "bad.json", "valid": False,
         "error": {"keyword": "enum", "instance_path": "/operation"}}]}]}
    path = tmp_path / "cases.yaml"
    path.write_text(yaml.safe_dump(manifest, allow_unicode=True), encoding="utf-8")
    return path, manifest, schema


def save_manifest(path, manifest):
    path.write_text(yaml.safe_dump(manifest, allow_unicode=True), encoding="utf-8")


def test_examples_execute_local_defs_and_bind_input_hashes(tmp_path):
    path, _, _ = fixture(tmp_path)
    report = verify_examples(path)
    assert report["status"] == "PASS", report
    assert (report["passed"], report["checked"]) == (2, 2)
    assert set(report["identities"]) == {"cases.yaml", "schema.json", "good.json", "bad.json"}
    assert "runtime behavior" in report["not_proven"]
    previous = report["identities"]["good.json"]
    put(tmp_path / "good.json", {"operation": "create"})
    updated = verify_examples(path)
    assert updated["status"] == "PASS"
    assert updated["identities"]["good.json"] != previous


def test_stale_enum_and_type_shorthand_are_detected_by_actual_examples(tmp_path):
    path, _, schema = fixture(tmp_path)
    schema["$defs"]["Operation"]["enum"].remove("query")
    put(tmp_path / "schema.json", schema)
    report = verify_examples(path)
    assert report["status"] == "FAIL" and report["results"][0]["actual_valid"] is False
    # JSON Schema permits unknown keywords; check_schema alone cannot reject
    # this apparently complete but non-constraining key/type shorthand.
    schema["$defs"]["Input"] = {"operation": {"type": "string"}}
    put(tmp_path / "schema.json", schema)
    report = verify_examples(path)
    assert report["status"] == "FAIL"
    assert report["results"][1]["actual_valid"] is True


def test_rejection_for_wrong_reason_is_not_a_passing_negative(tmp_path):
    path, _, _ = fixture(tmp_path)
    put(tmp_path / "bad.json", {})
    report = verify_examples(path)
    assert report["status"] == "FAIL"
    assert report["results"][1]["errors"] == [{"keyword": "required", "instance_path": ""}]


@pytest.mark.parametrize("value,error", [
    ({}, {"keyword": "required", "instance_path": ""}),
    ({"operation": 42}, {"keyword": "enum", "instance_path": "/operation"}),
    ({"operation": "query", "unlisted": 1}, {"keyword": "additionalProperties", "instance_path": ""}),
])
def test_missing_type_and_extra_field_negatives(tmp_path, value, error):
    path, manifest, _ = fixture(tmp_path)
    put(tmp_path / "bad.json", value)
    manifest["contracts"][0]["cases"][1]["error"] = error
    save_manifest(path, manifest)
    assert verify_examples(path)["status"] == "PASS"


@pytest.mark.parametrize("kind", ["positive-only", "duplicate-case", "duplicate-contract", "string-bool", "unknown-key", "missing-reason"])
def test_malformed_or_vacuous_cases_do_not_pass(tmp_path, kind):
    path, manifest, _ = fixture(tmp_path)
    cases = manifest["contracts"][0]["cases"]
    if kind == "positive-only":
        cases.pop()
    elif kind == "duplicate-case":
        cases[1]["id"] = cases[0]["id"]
    elif kind == "duplicate-contract":
        manifest["contracts"].append(copy.deepcopy(manifest["contracts"][0]))
    elif kind == "string-bool":
        cases[1]["valid"] = "false"
    elif kind == "unknown-key":
        cases[1]["vaild"] = False
    else:
        cases[1].pop("error")
    save_manifest(path, manifest)
    assert verify_examples(path)["status"] == "INVALID"


@pytest.mark.parametrize("kind", ["missing-file", "parent-path", "absolute-path", "bad-pointer", "remote-ref", "schema-type", "no-dialect", "nan", "duplicate-key"])
def test_input_or_resolution_failures_never_count_as_expected_rejection(tmp_path, kind):
    path, manifest, schema = fixture(tmp_path)
    case = manifest["contracts"][0]["cases"][1]
    if kind == "missing-file":
        case["instance"] = "absent.json"
    elif kind == "parent-path":
        case["instance"] = "../outside.json"
    elif kind == "absolute-path":
        case["instance"] = str(tmp_path / "bad.json")
    elif kind == "bad-pointer":
        manifest["contracts"][0]["schema"] = "schema.json#/$defs/Missing"
    elif kind == "remote-ref":
        schema["$defs"]["Operation"] = {"$ref": "https://invalid.example/schema.json"}
    elif kind == "schema-type":
        schema["$defs"]["Input"]["type"] = "date-range"
    elif kind == "no-dialect":
        schema.pop("$schema")
    elif kind == "nan":
        (tmp_path / "bad.json").write_text('{"operation": NaN}', encoding="utf-8")
    else:
        (tmp_path / "bad.json").write_text('{"operation":"scan","operation":"query"}', encoding="utf-8")
    save_manifest(path, manifest)
    put(tmp_path / "schema.json", schema)
    assert verify_examples(path)["status"] == "INVALID"


def test_cli_runs_real_manifest_and_preserves_failure_exit(tmp_path):
    path, _, schema = fixture(tmp_path)
    command = [sys.executable, str(ROOT / "scripts/ai_delivery_spec_cli.py"),
               "check-examples", "--input", str(path), "--format", "json"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["checked"] == 2
    schema["$defs"]["Operation"]["enum"].remove("query")
    put(tmp_path / "schema.json", schema)
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "FAIL"


def test_projection_mode_remains_compatible(tmp_path):
    (tmp_path / "truth.yaml").write_text('truth_id: TRUTH-X\nrequirements: [{id: REQ-X}]\n', encoding="utf-8")
    (tmp_path / "prd.md").write_text('Source: Product Truth\nREQ-X defines the example.\n', encoding="utf-8")
    command = [sys.executable, str(ROOT / "scripts/validators/validate_projection_consistency.py"),
               "--truth", str(tmp_path / "truth.yaml"), "--projection", str(tmp_path / "prd.md")]
    assert subprocess.run(command, capture_output=True).returncode == 0
    (tmp_path / "prd.md").write_text('Source: Product Truth\nREQ-MISSING\n', encoding="utf-8")
    assert subprocess.run(command, capture_output=True).returncode == 1


def test_duplicate_yaml_cannot_hide_a_missing_contract(tmp_path):
    path, _, _ = fixture(tmp_path)
    good = path.read_text(encoding="utf-8")
    path.write_text('contracts: [{id: lost, schema: missing.json, cases: []}]\n' + good,
                    encoding="utf-8")
    report = verify_examples(path)
    assert report["status"] == "INVALID" and report["checked"] == 0


def test_missing_format_checker_is_unverified_not_passed(tmp_path, monkeypatch):
    path, _, schema = fixture(tmp_path)
    schema["$defs"]["Input"]["properties"]["operation"] = {"type": "string", "format": "date"}
    put(tmp_path / "schema.json", schema)
    monkeypatch.delitem(StrictFormatChecker.checkers, "date", raising=False)
    report = verify_examples(path)
    assert report["status"] == "INVALID"
    assert any("format checker unavailable: date" in error for error in report["errors"])


def test_available_format_is_actually_checked(tmp_path):
    path, manifest, schema = fixture(tmp_path)
    schema["$defs"]["Input"]["properties"]["operation"] = {"type": "string", "format": "date"}
    put(tmp_path / "schema.json", schema)
    put(tmp_path / "good.json", {"operation": "2026-10-11"})
    put(tmp_path / "bad.json", {"operation": "2026-02-30"})
    manifest["contracts"][0]["cases"][1]["error"]["keyword"] = "format"
    save_manifest(path, manifest)
    assert verify_examples(path)["status"] == "PASS"


def test_percent_encoded_schema_pointer_resolves_same_target(tmp_path):
    path, manifest, schema = fixture(tmp_path)
    schema["$defs"]["Device Check"] = schema["$defs"].pop("Input")
    put(tmp_path / "schema.json", schema)
    manifest["contracts"][0]["schema"] = "schema.json#/$defs/Device%20Check"
    save_manifest(path, manifest)
    assert verify_examples(path)["status"] == "PASS"


def test_shared_sources_are_read_once_for_consistent_hashes(tmp_path, monkeypatch):
    path, manifest, _ = fixture(tmp_path)
    extra = copy.deepcopy(manifest["contracts"][0])
    extra["id"] = "same-source"
    manifest["contracts"].append(extra)
    save_manifest(path, manifest)
    calls = []
    original = Path.read_bytes

    def read(p):
        calls.append(p)
        return original(p)

    monkeypatch.setattr(Path, "read_bytes", read)
    report = verify_examples(path)
    assert report["status"] == "PASS" and report["checked"] == 4
    assert len(calls) == len(set(calls)) == 4
