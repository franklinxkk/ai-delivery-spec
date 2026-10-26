"""Read-only input diagnostics and output-language regressions for triage."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from triage_requirement import recommend, render_markdown

SECRET = "DUMMY_SECRET_FOR_DIAGNOSTIC_TEST"


def run(path, *args, direct=False):
    entry = ["scripts/triage_requirement.py", str(path)] if direct else ["scripts/ai_delivery_spec_cli.py", "triage", "--input", str(path)]
    return subprocess.run([sys.executable, "-B", *entry, *args], cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8")


@pytest.mark.parametrize("kind,content", [
    ("missing", None), ("empty", b""), ("list", ("- " + SECRET).encode()),
    ("yaml", ("title: [" + SECRET).encode()), ("encoding", b"\xff\xfe\xfa"),
    ("keys", (SECRET + ": 1\n" + SECRET + ": 2\n").encode()),
])
@pytest.mark.parametrize("language", ["zh-CN", "en-US"])
def test_bad_inputs_have_localized_safe_diagnostics(tmp_path, kind, content, language):
    path = tmp_path / (kind + ".yaml")
    if content is not None:
        path.write_bytes(content)
    output = tmp_path / "result.json"
    result = run(path, "--format", "json", "--language", language, "--output", str(output))
    assert result.returncode == 2 and result.stdout == ""
    assert "TRIAGE-INPUT" in result.stderr and str(path) in result.stderr
    assert SECRET not in result.stderr and "Traceback" not in result.stderr
    assert '<unicode string>' not in result.stderr and not output.exists()
    assert ("下一步" in result.stderr) if language == "zh-CN" else ("Next:" in result.stderr)
    assert ("未形成业务处置建议" in result.stderr) if language == "zh-CN" else ("No routing recommendation" in result.stderr)
    if content is not None:
        assert path.read_bytes() == content
    if kind == "yaml":
        assert ("第 1 行" in result.stderr) if language == "zh-CN" else ("line 1" in result.stderr)


def test_auto_error_language_uses_declaration_or_cli_default(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("title: [" + SECRET, encoding="utf-8")
    assert "下一步" in run(path).stderr
    path.write_text("document_language: en-US\ntitle: [" + SECRET, encoding="utf-8")
    assert "Next:" in run(path).stderr
    assert "下一步" in run(path, "--language", "zh-CN").stderr


def test_direct_script_and_wrapper_share_diagnostic_language(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("title: [" + SECRET, encoding="utf-8")
    direct = run(path, "--language", "en-US", direct=True)
    wrapper = run(path, "--language", "en-US")
    assert direct.returncode == wrapper.returncode == 2
    assert direct.stderr == wrapper.stderr


@pytest.mark.parametrize("title,expected_language,heading", [
    ("现有列表增加按创建日期升序排序，默认仍降序，权限不变", "zh-CN", "需求处理建议"),
    ("Add ascending creation-date sorting; preserve permissions", "en", "Requirement routing"),
])
def test_valid_small_change_keeps_auto_recommendation_and_input(tmp_path, title, expected_language, heading):
    path = tmp_path / "valid.json"
    content = json.dumps({"title": title}, ensure_ascii=False).encode()
    path.write_bytes(content)
    result = run(path, "--format", "json")
    data = json.loads(result.stdout)
    assert result.returncode == 0 and result.stderr == ""
    # Title-only fixtures were accept/card in the saved pre-change CLI output.
    assert data["recommendation"] == "accept" and data["artifact_mode"] == "card"
    assert data["document_language"] == expected_language and data["lifecycle_mutated"] is False
    assert heading in render_markdown(data)
    assert path.read_bytes() == content


def test_explicit_output_language_preserves_business_result_and_declared_language(tmp_path):
    doc = {"title": "这个系统太难用了", "document_language": "zh-CN"}
    original = copy.deepcopy(doc)
    default = recommend(doc)
    english = recommend(doc, output_language="en-US")
    assert doc == original
    for key in ("recommendation", "artifact_mode", "risk_facets", "decision_status", "lifecycle_mutated"):
        assert default[key] == english[key]
    assert english["document_language"] == "zh-CN" and english["output_language"] == "en-US"
    assert "Who is trying" in english["next_questions"][0]
    assert "Requirement routing" in render_markdown(english)
    path = tmp_path / "valid.json"
    path.write_text(json.dumps(original, ensure_ascii=False), encoding="utf-8")
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    result = run(path, "--format", "json", "--language", "en-US")
    assert result.returncode == 0 and json.loads(result.stdout)["output_language"] == "en-US"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
