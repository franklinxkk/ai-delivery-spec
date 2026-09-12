"""Sanitized regressions for decision diagnostics and bilingual candidate retrieval.

These exercise deterministic boundaries, not natural-language completeness or
the quality of generated PRDs. Behavioral forward tests are reported separately.
"""
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from quality_gate import Gate, diagnostic_roots, result_payload
from query_domain import search_terms, term_matches
from requirement_contract import check_spec
from scan_requirement_ambiguity import inspect_content
from triage_requirement import recommend, render_markdown

BODY = "## Scope\nContract lookup and payment plans.\n## Behavior\nLookup uses the approved contract.\n## Acceptance\nVerify the returned contract identity.\n"


def test_unknown_counts_distinguish_priority_scope_stage_and_parser_uncertainty(tmp_path):
    doc = {"unknowns": [
        {"id": "UNK-TERMS", "status": "open", "priority": "P0", "affected_refs": ["REQ-PLAN"], "blocks_stage": "baseline"},
        {"id": "UNK-SOURCE", "status": "pending", "affected_refs": ["REQ-PLAN"], "blocks_stage": "implementation"},
        {"id": "UNK-OTHER", "status": "open", "priority": "P0", "affected_refs": ["REQ-OTHER"]},
        {"id": "UNK-DONE", "status": "closed", "resolution_ref": "DEC-DONE"},
        {"id": "UNK-BAD", "status": "mystery"},
    ]}
    # The same unknown also appears in a human table. Count one decision, not two.
    body = BODY + "\n| ID | Priority | Status | Blocks stage |\n|---|---|---|---|\n| UNK-TERMS | P0 | open | baseline |\n"
    path = tmp_path / "计划需求.md"
    path.write_text("---\n" + yaml.safe_dump(doc) + "---\n" + body, encoding="utf-8")
    gate = Gate()
    gate.check_prd(path, stage="specify", scope_refs=("REQ-PLAN",))
    data = result_payload(gate, "prd")
    counts = data["metrics"]["unknown_summary"]["counts"]
    assert counts == {"open": 2, "declared_open_p0": 1, "open_priority_unspecified": 1,
                      "blocking_now": 0, "status_unresolved": 1, "invalid_blocking_stage": 0, "out_of_scope": 1}
    assert data["summary"]["p0_unknowns"] == 0  # Stable legacy severity contract.
    assert data["status"] == "BLOCKED"  # Invalid status is not silently treated as closed.
    baseline = check_spec(doc, body, stage="baseline", scope=("REQ-PLAN",))[1]["unknown_summary"]
    assert baseline["refs"]["blocking_now"] == ["UNK-TERMS"]
    implementation = check_spec(doc, body, stage="implementation", scope=("REQ-PLAN",))[1]["unknown_summary"]
    assert implementation["refs"]["blocking_now"] == ["UNK-SOURCE", "UNK-TERMS"]


def test_unknown_conflicts_and_unlocated_rows_remain_visible():
    body = "| ID | 类型 | 说明 |\n|---|---|---|\n| UNK-X | 业务政策 | 等待来源 |\n"
    findings, route = check_spec({}, BODY + body)
    assert route["unknown_summary"]["counts"]["status_unresolved"] == 1
    assert route["unknown_summary"]["counts"]["open"] == 0
    assert any(f["code"] == "SPEC-UNKNOWN-STATUS-UNLOCATED" for f in findings)
    conflict = {"unknowns": [{"id": "UNK-X", "status": "open", "priority": "P0"}]}
    findings, _ = check_spec(conflict, BODY + "| ID | Status |\n|---|---|\n| UNK-X | closed |\n")
    assert any(f["code"] == "PRD-UNKNOWN-METADATA-DRIFT" for f in findings)


def test_independent_unknowns_are_not_hidden_as_one_root():
    gate = Gate()
    for ref in ("UNK-A", "UNK-A", "UNK-B"):
        gate.add("GAP", "SPEC-OPEN-DECISION", Path("prd.md"), "open", ref)
    roots, total = diagnostic_roots(gate.findings, 5)
    assert total == 2 and [(f.ref, n) for f, n in roots] == [("UNK-A", 2), ("UNK-B", 1)]


@pytest.mark.parametrize("kind,rough,clear", [
    ("publication", "审批通过后可发布。", "审批通过后可发布，由运营手动发布。"),
    ("publication", "Approved courses can be published.", "Approved courses can be published; operators publish manually."),
    ("publication", "Courses may be published after approval.", "Courses may be published after approval; publication is scheduled automatically."),
    ("return-object", "退回后重新提交。", "退回后修改原单重新提交，编号和历史保留。"),
    ("return-object", "Returned requests can be resubmitted.", "Returned requests can be resubmitted by editing the same record; retain the ID and history."),
    ("return-object", "Resubmit after return.", "Resubmit the original request after return."),
    ("retry-result", "支付失败后重试。", "支付失败后重试，先查询现有结果，按业务幂等键去重。"),
    ("retry-result", "Retry failed payments.", "Retry failed payments with the same idempotency key and query the existing result."),
])
def test_bilingual_decision_forks_with_explicit_answer_controls(kind, rough, clear):
    kinds = lambda text: {f["kind"] for f in inspect_content(text)["findings"]}
    assert kind in kinds(rough)
    assert kind not in kinds(clear)
    assert recommend({"title": rough})["recommendation"] == "clarify"


@pytest.mark.parametrize("text", ["置信度大于 0.8 自动给客户发信。", "When confidence exceeds 0.8, automatically email customers."])
def test_automatic_ai_writes_remain_visible_without_metadata(text):
    result = inspect_content(text)
    assert "irreversible_ai_write" in result["risk_facets"]
    assert any(f["kind"] == "ai-write" for f in result["findings"])


@pytest.mark.parametrize("text", ["AI 仅生成草稿，不自动给客户发信。", "AI only produces drafts and does not automatically email customers.", "AI never directly sends messages.", "AI answers questions using read-only data."])
def test_read_only_and_explicitly_excluded_writes_are_not_escalated(text):
    assert "irreversible_ai_write" not in inspect_content(text)["risk_facets"]


@pytest.mark.parametrize("kind,text,negative", [
    ("relevance-authority", "Relevance equals authorization.", "Relevance is not authorization."),
    ("provenance-truth", "Valid C2PA proves the content is true.", "Valid C2PA does not prove the content is true."),
    ("confidence-outcome", "Confidence is the task completion rate.", "Confidence is not the task completion rate."),
])
def test_english_domain_misconceptions_are_candidates(kind, text, negative):
    assert kind in {f["kind"] for f in inspect_content(text)["findings"]}
    assert kind not in {f["kind"] for f in inspect_content(negative)["findings"]}


@pytest.mark.parametrize("title", ["做个系统", "Build a system"])
def test_generic_intake_gives_an_answerable_first_question(title):
    result = recommend({"title": title})
    assert result["recommendation"] == "clarify" and result["next_questions"]
    assert result["lifecycle_mutated"] is False
    assert result["next_questions"][0] in render_markdown(result)


def test_english_gate_keeps_the_actual_business_question(tmp_path):
    path = tmp_path / "review.md"
    path.write_text(BODY.replace("Lookup uses the approved contract.", "Approved courses can be published."), encoding="utf-8")
    gate = Gate()
    gate.check_prd(path)
    data = result_payload(gate, "prd", output_language="en-US")
    item = next(f for f in data["findings"] if f["code"] == "SPEC-CONTENT-PUBLICATION")
    assert "Who publishes" in item["message"] and "Approved courses" in item["message"]
    assert "contract failed at" not in item["message"]


def test_long_queries_match_curated_phrases_without_substring_collisions():
    aliases = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))["search_aliases"]
    for query, expected in [("How are active customers counted in a contract report?", "活跃客户"),
                            ("合同报表里的活跃客户怎么计算？", "active customer"),
                            ("Where is the expense claim workflow?", "报销"),
                            ("How do project milestones work?", "里程碑")]:
        assert expected in search_terms(query, aliases)
    assert "mileage" not in search_terms("How do project milestones work?", aliases)
    assert "里程" not in search_terms("项目里程碑如何填写？", aliases)
    assert "active enterprise" not in search_terms("How are active customers counted?", aliases)
    assert "活跃客户" not in search_terms("Show inactive customers", aliases)
    assert not term_matches("ledger", "pledger")


@pytest.mark.parametrize("query", ["合同支付审核有哪些规则？", "What approval rules apply to contract payments?"])
def test_query_cli_ranks_joint_concepts_and_preserves_literal(query):
    result = subprocess.run([sys.executable, "-B", "scripts/query_domain.py", "--domain", "crm", "--search", query, "--limit", "8"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    data = yaml.safe_load(result.stdout)
    assert result.returncode == 0 and data["total_matches"] > 0
    assert data["expanded_terms"][0] == query and len(data["matched_concepts"]) >= 3
    counts = [len(hit["matched_concepts"]) for hit in data["hits"]]
    assert counts == sorted(counts, reverse=True)
    assert all(hit["status"] == "candidate" for hit in data["hits"])


def test_query_zero_hit_has_an_actionable_fallback():
    result = subprocess.run([sys.executable, "-B", "scripts/query_domain.py", "--search", "unmatchedxyz551"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    data = yaml.safe_load(result.stdout)
    assert result.returncode == 0 and data["total_matches"] == 0 and data["hits"] == []
    assert "--domain" in data["next_action"]
