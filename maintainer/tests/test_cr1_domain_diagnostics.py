"""Relevant retrieval and actionable review gaps, not semantic proof."""
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from requirement_contract import check_spec
from quality_gate import Gate, localized_finding


def query(term, domain=None):
    args = [sys.executable, "-B", str(ROOT / "scripts/query_domain.py"), "--search", term, "--limit", "5"]
    if domain:
        args += ["--domain", domain]
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    return yaml.safe_load(result.stdout)


@pytest.mark.parametrize("term,concept,phrase", [
    ("安全例会", "安全例会", "会议"),
    ("安全会议", "安全例会", "会议"),
    ("安全会议签到", "安全会议签到", "签到"),
    ("专家检查", "专家检查", "专家"),
    ("线上检查", "线上检查", "检查"),
    ("企业预警", "企业预警", "预警"),
    ("safety meeting attendance", "安全会议签到", "attendance"),
    ("expert safety inspection", "专家检查", "inspection"),
    ("online inspection", "线上检查", "inspection"),
    ("enterprise alert", "企业预警", "alert"),
])
def test_domain_query_returns_actual_relevant_passage(term, concept, phrase):
    data = query(term)
    assert concept in data["matched_concepts"]
    relevant = [hit for hit in data["hits"] if hit["domain_id"] == "traffic" and concept in hit["matched_concepts"]]
    assert relevant
    hit = relevant[0]
    assert hit["section"] in {"Core Workflows", "State Machines"}
    line = (ROOT / hit["knowledge_file"]).read_text(encoding="utf-8").splitlines()[hit["line"] - 1]
    assert phrase.casefold() in line.casefold()
    assert hit["excerpt"] == line.strip()[:300]
    assert hit["status"] == "candidate"


@pytest.mark.parametrize("term", ["线上选课", "专家诊疗", "公司周年庆", "safety meetinghouse"])
def test_nearby_words_do_not_expand_transport_workflow(term):
    data = query(term, "traffic")
    assert not ({"安全例会", "安全会议签到", "专家检查", "线上检查", "企业预警"} & set(data["matched_concepts"]))


def gap(doc, body, category):
    findings, _ = check_spec(doc, body)
    return next(f for f in findings if f["code"] == "SPEC-SEMANTIC-NOT-PROVEN" and f["ref"].startswith(category + ":"))


def test_structured_gap_locates_unreviewed_scope_without_laundering_other_scope():
    body = "# 统计\n## 4.1 REQ-A 完成率\n分母按已确认的参与对象计算。\n## 4.2 REQ-B 缺数\n空值不当成零。"
    doc = {"risk_facets": ["metric"], "baseline_version": "1", "requirement_ids": ["REQ-A", "REQ-B"],
           "source_refs": ["SRC-OWNER"], "semantic_reviews": [{"category": "metric_definition", "result": "pass",
               "scope_refs": ["REQ-A"], "source_refs": ["SRC-OWNER"], "reviewer": "QA", "evidence_ref": "actual.md", "baseline_version": "1"}]}
    finding = gap(doc, body, "metric_definition")
    assert "REQ-B @line 4" in finding["ref"] and "4.2 REQ-B 缺数" in finding["message"]
    assert "REQ-A" not in finding["ref"]
    assert "SRC-OWNER" in finding["message"] and "分母" in finding["message"]
    assert "counterexample" in finding["message_en"] or "boundary case" in finding["message_en"]


def test_plain_module_location_is_explicitly_candidate_not_invented_rule():
    finding = gap({"risk_facets": ["integration"]}, "# 通知\n## 4.2 提交\n提交结果未知时按原编号查询。", "recovery")
    assert "@line 3" in finding["ref"] and "4.2 提交" in finding["message"]
    assert "候选" in finding["message"] and "归属待核对" in finding["message"]
    assert "REQ-" not in finding["ref"] and "RULE-" not in finding["ref"]
    assert "重试" in finding["message"] and "不能补写 pass" in finding["message"]


def test_no_location_is_reported_as_unknown_and_code_examples_are_ignored():
    finding = gap({"risk_facets": ["integration"], "requirement_ids": ["REQ-REAL"]},
                  "# 范围\n仅展示资料。\n```md\n## REQ-REAL 提交\n```", "recovery")
    assert "正文未定位" in finding["message"] and "@line" not in finding["ref"]
    assert "未定位本项原始来源" in finding["message"]


def test_gate_preserves_absolute_line_and_localized_action(tmp_path):
    path = tmp_path / "prd.md"
    path.write_text("---\nrisk_facets: [integration]\nrequirement_ids: [REQ-NOTIFY]\n---\n# 通知\n## REQ-NOTIFY 提交\n提交结果未知时按原编号查询。\n", encoding="utf-8")
    gate = Gate()
    gate.check_prd(path)
    item = next(f for f in gate.findings if f.code == "SPEC-SEMANTIC-NOT-PROVEN" and f.ref.startswith("recovery:"))
    assert "@line 6" in item.ref
    zh = localized_finding(item, "zh-CN")
    en = localized_finding(item, "en-US")
    assert "重复提交" in zh["how_to_fix"] and "retry" in en["how_to_fix"]
    assert "actual result" in en["repair_example"] and "not invent rule IDs" in en["repair_example"]


def test_signoff_never_silently_resolves_unknown():
    doc = {"status": "baselined", "unknowns": [{"id": "UNK-A", "status": "open", "blocks_stage": "review", "affected_refs": ["REQ-A"]}], "signoff": {"result": "approved"}}
    findings, _ = check_spec(doc, "# 范围\n仍需确定付款期数。", stage="baseline")
    assert any(f["code"] == "SPEC-OPEN-DECISION" and f["severity"] == "BLOCK" for f in findings)
