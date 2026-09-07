"""Regressions for bilingual retrieval, runtime decoding and bounded advisories."""
from argparse import Namespace
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import ai_delivery_spec_cli as cli
from query_domain import search_terms
from requirement_contract import check_spec
from scan_prototype_css import scan
from scan_requirement_ambiguity import inspect_content
from triage_requirement import recommend


@pytest.mark.parametrize("exit_code,raw_bytes", [(0, False), (1, False), (1, True)])
def test_runtime_check_preserves_result_with_legacy_child_encoding(tmp_path, monkeypatch, capsys, exit_code, raw_bytes):
    root = tmp_path / "中文安装路径"
    script = root / "scripts/validators/validate_spec_config.py"
    script.parent.mkdir(parents=True)
    # A normal Python child and a legacy byte-writing child both need safe capture.
    script.write_text("import os,sys\n" + (
        "os.write(1, bytes([0xd6,0xd0,0xce,0xc4]))\n" if raw_bytes else "print('中文配置路径')\n"
    ) + f"raise SystemExit({exit_code})\n", encoding="utf-8")
    monkeypatch.setattr(cli, "ROOT", root)
    monkeypatch.setattr(cli, "MAINTAINER_DIR", root / "maintainer")
    monkeypatch.setattr(cli, "validate_runtime_manifest", lambda _: [])
    monkeypatch.setenv("PYTHONIOENCODING", "gbk")
    result = cli.run_check(Namespace(profile="fast", product_truth=None))
    output = capsys.readouterr()
    assert result == (2 if exit_code else 0)
    assert "UnicodeDecodeError" not in output.err and "TypeError" not in output.err
    if exit_code:
        assert "spec config self-check failed" in output.out
        if not raw_bytes:
            assert "中文配置路径" in output.out


def test_navigation_items_are_not_counted_as_containers():
    nav = '<nav class="top-nav"><a class="nav-order">Orders</a><button class="nav-report" data-action="ACT-REPORT">Report</button><div class="nav-settings" data-action="ACT-SETTINGS">Settings</div></nav>'
    page = '<main data-testid="page-VIEW-X">' + nav + '</main>'
    assert "dual-navigation" not in {f["kind"] for f in scan(page)}
    assert "dual-navigation" in {f["kind"] for f in scan(page.replace('</main>', nav + '</main>'))}


def test_repeated_partial_unknown_is_open_once_and_conflict_survives():
    header = '| ID | 优先级 | 阻断阶段 | 状态 |\n|---|---|---|---|\n'
    row = '| UNK-POLICY | P0 | baseline | partial |\n'
    body = (header + row + '\n') * 9
    findings = check_spec({}, body, stage="baseline")[0]
    assert not any(f["code"] == "SPEC-UNKNOWN-STATUS" for f in findings)
    assert sum(f["code"] == "SPEC-OPEN-DECISION" for f in findings) == 1
    assert next(f for f in findings if f["code"] == "SPEC-OPEN-DECISION")["severity"] == "BLOCK"
    early = check_spec({}, body, stage="explore")[0]
    assert next(f for f in early if f["code"] == "SPEC-OPEN-DECISION")["severity"] == "GAP"
    changed = body + header + row.replace('partial', 'resolved')
    assert any(f["code"] == "PRD-UNKNOWN-METADATA-DRIFT" for f in check_spec({}, changed)[0])
    assert any(f["code"] == "SPEC-UNKNOWN-STATUS" for f in check_spec({}, header + row.replace('partial', 'mystery'))[0])


@pytest.mark.parametrize("selection,approved,undecided", [
    ("补考成绩取最新一次考试成绩。", "依据 SRC-EXAM 中经批准的取值政策，补考成绩取最新一次考试成绩。", "补考取值策略尚未决定。\n补考成绩取最新一次考试成绩。"),
    ("Retake scores use the latest attempt.", "According to approved policy SRC-EXAM, retake scores use the latest attempt.", "Retake policy is undecided.\nRetake scores use the latest attempt."),
])
def test_policy_basis_is_advisory_until_an_unresolved_choice_is_visible(selection, approved, undecided):
    base = '## Scope\nExam records.\n## Behavior\n'
    findings = check_spec({}, base + selection + '\n## Acceptance\nVerify the selected attempt.')[0]
    assert next(f for f in findings if f["code"] == "SPEC-CONTENT-POLICY-BASIS")["severity"] == "WARN"
    assert "policy-basis" not in {f["kind"] for f in inspect_content(approved)["findings"]}
    assert "undecided-policy" in {f["kind"] for f in inspect_content(undecided)["findings"]}
    assert recommend({"title": selection})["recommendation"] == "accept"


def test_policy_probe_does_not_turn_presentation_defaults_into_business_gaps():
    for text in ("列表默认按最新更新时间排序。", "默认每页显示 20 条。", "建议补考成绩取最新一次，等待批准。", "禁止补考成绩取最新一次。", "Sort scores by newest first."):
        assert not {f["kind"] for f in inspect_content(text)["findings"]} & {"policy-basis", "undecided-policy"}


@pytest.mark.parametrize("zh,en,domain", [
    ("完成率", "completion rate", "traffic"), ("商机", "opportunity", "crm"),
    ("合同", "contract", "crm"), ("支付", "payment", "crm"),
    ("电子病历", "EMR", "medical-hospital-it"), ("高校", "campus", "education-it"),
])
def test_chinese_terms_retrieve_source_passages(zh, en, domain):
    args = [sys.executable, "-B", str(ROOT / "scripts/ai_delivery_spec_cli.py"), "query-domain", "--search", zh, "--domain", domain, "--limit", "3"]
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    data = yaml.safe_load(result.stdout)
    assert result.returncode == 0 and data["total_matches"] > 0
    assert en in data["expanded_terms"] and len(data["hits"]) <= 3
    assert all(h["status"] == "candidate" and h["line"] > 0 and h["matched_terms"] for h in data["hits"])
    assert search_terms("unknown-term", {"合同": ["contract"]}) == ["unknown-term"]


def test_english_slice_keeps_chinese_jurisdiction_and_source_urls():
    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/ai_delivery_spec_cli.py"), "query-domain", "--domain", "medical-hospital-it", "--section", "Policy / Privacy Constraints", "--source-detail", "full", "--language", "en-US"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    data = yaml.safe_load(result.stdout)
    assert result.returncode == 0 and "China" in data["jurisdictions"]
    assert "language does not determine jurisdiction" in data["source_usage_rule"]
    assert any(s["jurisdiction"] == "China" and s["url"].startswith("https://") for s in data["source_refs"])
    assert data["selected_sections"]
