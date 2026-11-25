"""An explicitly selected report may be replaced, but its sources must survive."""
import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
CLI = "ai_delivery_spec_cli.py"


def run(script, *args, expected=0):
    result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert result.returncode == expected, result.stdout + result.stderr
    return result


@pytest.mark.parametrize(("script", "args", "content"), [
    ("scan_requirement_ambiguity.py", [], "The original user request."),
    ("render_mermaid_flow.py", ["--truth"], "flows: []"),
])
def test_report_and_source_are_separate(tmp_path, script, args, content):
    source, report = tmp_path / "source.txt", tmp_path / "report.txt"
    source.write_text(content, encoding="utf-8")
    report.write_text("previous export", encoding="utf-8")
    run(script, *args, source, "--output", report)
    assert report.read_text(encoding="utf-8") != "previous export"
    run(script, *args, source, "--output", source, expected=2)
    assert source.read_text(encoding="utf-8") == content


def test_candidate_reports_preserve_original_and_usage_inputs(tmp_path):
    candidate = tmp_path / "candidate.yaml"
    usages = tmp_path / "usages"
    usages.mkdir()
    usage = usages / "usage.yaml"
    candidate.write_text(json.dumps({
        "schema_version": "5.3.0", "candidate_id": "CAND-TEST", "domain": "office",
        "statement": "A source document must remain readable.", "candidate_type": "pattern",
        "status": "proposed", "reuse_scope": "project_only", "submitted_by": "author",
        "decision_owner": "owner", "source_refs": ["brief"], "evidence_refs": ["example"],
        "sensitive_data": False, "created_at": "2026-01-01T00:00:00Z",
    }), encoding="utf-8")
    original = candidate.read_bytes()
    record = ["candidate", "record-usage", "--candidate", candidate, "--usage-id", "USAGE-TEST",
              "--project", "sample", "--outcome", "adopted", "--evidence", "sample",
              "--recorded-by", "reviewer", "--output"]
    run(CLI, *record, usage)
    run(CLI, *record, usage, "--force")
    run(CLI, *record, candidate, "--force", expected=2)
    assert candidate.read_bytes() == original
    previous_usage = usage.read_bytes()
    assess = ["candidate", "assess", "--candidate", candidate, "--usage", usages, "--output"]
    report = tmp_path / "assessment.md"
    run(CLI, *assess, report)
    assert report.stat().st_size > 0
    for protected in (candidate, usage):
        run(CLI, *assess, protected, expected=2)
    assert candidate.read_bytes() == original
    assert usage.read_bytes() == previous_usage
