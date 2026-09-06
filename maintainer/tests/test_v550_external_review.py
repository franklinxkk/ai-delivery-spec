"""Synthetic positive/negative pairs from external review failure mechanisms.

No private artifacts or external reviewers' scores are release evidence.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from requirement_contract import route, check_spec
from scan_requirement_ambiguity import inspect_content
from stage_contract import unknown_rows, validate_unknowns, Artifact
from change_package_contract import extract_seed_refs, ChangeContractError
from extract_interaction_ledger import extract_handler_actions, attr_values
from query_domain import select_sections
from triage_requirement import recommend


def content(text):
    return {item["kind"] for item in inspect_content(text)["findings"]}


@pytest.mark.parametrize("bad,good,kind", [
    ("审批通过后可发布。", "审批通过后可发布；由运营手动发布，不会自动发布。", "publication"),
    ("退回后重新提交。", "退回后编辑原单并重新提交，保留原编号。", "return-object"),
    ("字段可空。", "字段可空；空值表示未采集，不等于零。", "null-meaning"),
    ("展示本月活跃用户。", "展示本月活跃用户；按用户去重，统计人群为本月登录的用户。", "metric-population"),
    ("提交失败请重试。", "提交失败请重试；按原请求键幂等，确认已写入后直接返回原结果。", "retry-result"),
    ("隐藏删除按钮；深链仍可访问。", "隐藏删除按钮；深链由服务端校验对象归属，拒绝跨租户访问。", "deep-link"),
    ("置信度>0.8 自动给客户发信。", "AI 仅生成草稿，不会自动给客户发送，由用户编辑后确认。", "ai-write"),
    ("AI 自动修改账单并保存，无需人工确认。", "AI 自动修改账单并保存，仅限授权账单范围；允许人工停止并回退。", "ai-write"),
    ("相关性=授权。", "相关性不等于授权。", "relevance-authority"),
    ("C2PA 有效=为真。", "C2PA 有效不证明内容为真。", "provenance-truth"),
    ("置信度作为完成率。", "置信度与完成率分别统计。", "confidence-outcome"),
])
def test_decision_forks_have_local_questions_and_positive_controls(bad, good, kind):
    assert kind in content(bad)
    assert kind not in content(good)
    findings, _ = check_spec({}, "## 范围\n当前功能。\n## 行为\n" + bad + "\n## 验收\n按上述规则核对。")
    assert any(f["code"] == "SPEC-CONTENT-" + kind.upper() and f["severity"] == "GAP" for f in findings)


def test_absent_scope_is_not_execute_and_tags_cannot_hide_body_write():
    assert "irreversible_ai_write" not in route({"ai_behavior": True, "title": "只读 AI 问答"})["risk_facets"]
    assert "irreversible_ai_write" not in route({"ai_behavior": True, "ai_write_scope": "draft_only"})["risk_facets"]
    assert "irreversible_ai_write" in route({}, body="AI 自动修改用户账单并保存。") ["risk_facets"]
    assert "irreversible_ai_write" in route({"ai_write_scope": "consequential_write"})["risk_facets"]
    assert "ai-write" in content("AI 自动修改账单并保存，无回退入口。")
    assert "recovery" not in route({"risk_facets": ["state"]})["semantic_review_categories"]


def test_review_declaration_cannot_suppress_body_conflict():
    body = "## 行为\n退回后申请人编辑原单。\n退回后原单关闭，新建对象提交。"
    assert "return-conflict" in content(body)
    assert "return-conflict" in content(body.replace("退回后申请人", "### 修改\n退回后申请人").replace("退回后原单", "### 财务\n退回后原单"))
    doc = {"semantic_reviews": [{"category": "recovery", "result": "pass", "scope_refs": ["REQ-A"],
          "source_refs": ["SRC-A"], "reviewer": "reviewer", "baseline_version": "1", "evidence_ref": "evidence.md"}], "baseline_version": "1"}
    assert any(f["code"] == "SPEC-CONTENT-RETURN-CONFLICT" for f in check_spec(doc, body)[0])


def test_same_topic_decisions_need_explicit_replacement():
    table = "| DEC ID | 问题 | 决定 | 状态 |\n|---|---|---|---|\n| DEC-A | 审核后发布 | 自动发布 | confirmed |\n| DEC-B | 审核后发布 | 人工发布 | confirmed |"
    assert "decision-conflict" in content(table)
    assert "decision-conflict" not in content(table.replace("人工发布", "人工发布，取代 DEC-A"))


def test_examples_and_other_sections_cannot_create_or_resolve_live_risk():
    assert not content("```text\nAI 自动修改账单并保存。\n```\n<!-- 相关性=授权 -->")
    assert "publication" in content("## REQ-A\n审批通过后可发布。\n## REQ-B\n由运营手动发布。")
    assert not content("禁止 AI 自动修改账单并保存。")


TABLE = """| ID | 优先级 | 问题 | 责任人 | 阻断阶段（`blocks_stage`） | 回退路径 | 状态 | 关闭依据 |
|---|---|---|---|---|---|---|---|
| UNK-A | P0 | 发布时机 | 产品负责人 | 需求基线（`baseline`） | 保持待发布 | 待关闭（`open`） | - |
"""


def test_template_tokens_preserve_blocking_status_in_prd():
    assert unknown_rows(TABLE)[0]["status"] == "open"
    assert unknown_rows(TABLE)[0]["blocks_stage"] == "baseline"
    doc = {}
    before = deepcopy(doc)
    for _ in range(2):
        assert any(f["code"] == "SPEC-OPEN-DECISION" and f["severity"] == "BLOCK" for f in check_spec(doc, TABLE, stage="baseline")[0])
    assert doc == before
    assert not any(f["code"] == "SPEC-OPEN-DECISION" and f["severity"] == "BLOCK" for f in check_spec({}, TABLE, stage="explore")[0])
    assert not unknown_rows("| AC ID | 关联 |\n|---|---|\n| AC-A | UNK-A |")


def test_unknown_status_and_fake_closure_do_not_count_as_closed():
    for status in ("done-ish", "", "closed"):
        codes = {f["code"] for f in check_spec({}, TABLE.replace("待关闭（`open`）", status))[0]}
        assert ("SPEC-UNKNOWN-CLOSURE" if status == "closed" else "SPEC-UNKNOWN-STATUS") in codes
    good = TABLE.replace("待关闭（`open`）", "已关闭（`closed`）").replace("| - |", "| DEC-A |")
    assert not {f["code"] for f in check_spec({}, good)[0]} & {"SPEC-UNKNOWN-CLOSURE", "SPEC-OPEN-DECISION"}


def test_clarify_table_uses_real_stage_not_priority_or_decorated_status():
    artifact = Artifact(Path("brief.md"), TABLE, {}, "requirement-brief", "clarify")
    assert any(f["severity"] == "P0_UNKNOWN" for f in validate_unknowns(artifact, "baseline"))
    assert not any(f["severity"] in ("BLOCK", "P0_UNKNOWN") for f in validate_unknowns(artifact, "clarify"))
    artifact.text = TABLE.replace("P0", "P2")
    assert any(f["severity"] == "BLOCK" for f in validate_unknowns(artifact, "baseline"))
    artifact.text = TABLE.replace("待关闭（`open`）", "随便")
    assert any(f["code"] == "CLARIFY-UNKNOWN-STATUS" for f in validate_unknowns(artifact, "clarify"))


def test_plain_publication_conflict_and_numeric_null_are_visible():
    assert "publication-conflict" in content("## 发布\n文章审核通过后自动发布。\n## 复核\n文章审核通过后必须由管理员手动点击发布。")
    assert "null-meaning" in content("用户健康数据未采集时，按数值 0 计入统计结果。")
    assert "deep-link" in content("对象详情复制链接 /objects/{id}，收到链接的人可直接查看。")


def test_seed_alias_is_read_only_and_conflicts_are_not_silently_merged():
    source = {"seed_refs": [" REQ-A ", "REQ-A"]}
    old = deepcopy(source)
    assert extract_seed_refs(source) == ["REQ-A"] and source == old
    assert extract_seed_refs({"seed_refs": ["REQ-A"], "request": {"seed_refs": ["REQ-A"]}}) == ["REQ-A"]
    with pytest.raises(ChangeContractError):
        extract_seed_refs({"seed_refs": ["REQ-A"], "request": {"seed_refs": ["REQ-B"]}})


def test_dispatch_alias_and_candidate_anchor_separation():
    raw = '<button data-action="ACT-SAVE">保存</button><script type="application/json">{"target_selector":"[data-action=\'ACT-CANDIDATE\']"}</script>'
    assert attr_values(raw, "data-action") == ["ACT-SAVE"]
    source = "const act = t.dataset.action; if (act === 'ACT-SAVE') save();"
    assert extract_handler_actions(source) == ["ACT-SAVE"]
    assert extract_handler_actions(source.replace("act", "chosenAction")) == ["ACT-SAVE"]


def test_triage_reads_content_but_cannot_mutate_lifecycle():
    result = recommend({"title": "审批通过后可发布，退回后重新提交"})
    assert result["recommendation"] == "clarify"
    assert "state" in result["content_risk_candidates"]
    assert result["lifecycle_mutated"] is False
    assert recommend({"title": "审核与发布", "description": "审核通过产生已审核状态，不会自动发布。"})["recommendation"] == "accept"
    assert recommend({"title": "AI 只读", "description": "没有任何自动执行权限。"})["recommendation"] == "accept"
    unknown = "重复写入策略尚未决定，超时重试待确认。"
    assert recommend({"title": "同步", "description": unknown})["recommendation"] == "clarify"
    assert "open-decision" in content(unknown)
    assert "ai-write" in content("AI 分析来信，评分达到 0.9 时自动向第三方 CRM 创建客户档案。")


def cli(*args):
    return subprocess.run([sys.executable, "-B", str(ROOT / "scripts/ai_delivery_spec_cli.py"), *args], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)


def test_domain_search_alias_and_usage_boundary():
    result = cli("query-domain", "--search", "confidence", "--limit", "2")
    data = yaml.safe_load(result.stdout)
    assert result.returncode == 0 and len(data["hits"]) <= 2 and data["total_matches"] > 0
    assert all(hit["status"] == "candidate" for hit in data["hits"])
    result = cli("query-domain", "--domain", "ai-native", "--section", "指标")
    data = yaml.safe_load(result.stdout)
    assert result.returncode == 0 and data["source_usage_rule"] and data["practice_status"]
    assert data["selected_sections"]
    assert select_sections("## Metric / Indicator Governance\n内容", ["METRIC / INDICATOR GOVERNANCE"])[1] == []


def test_early_disposition_and_local_scope_cli(tmp_path):
    path = tmp_path / "analysis.md"
    path.write_text("---\nstatus: draft\ndisposition:\n  outcome: defer\n  status: proposed\n  reason: 先验证价值\n  scope_refs: [REQ-A]\n---\n## 范围\n当前问题。\n## 行为\n建议暂缓。\n## 验收\n授权人可据此决定。\n" + TABLE, encoding="utf-8")
    result = cli("gate", "--profile", "prd", "--prd", str(path), "--stage", "explore", "--format", "json")
    assert result.returncode == 1 and not any(f["severity"] == "BLOCK" for f in json.loads(result.stdout)["findings"])
    path.write_text("# REQ-A\n## 范围\n仅提示。\n## 行为\n保存成功提示完成。\n## 验收\n成功时显示完成。\n# REQ-B\nAI 自动修改账单并保存。", encoding="utf-8")
    scoped = json.loads(cli("gate", "--profile", "prd", "--prd", str(path), "--scope-ref", "REQ-A", "--format", "json").stdout)
    assert not any(f["code"] == "SPEC-CONTENT-AI-WRITE" for f in scoped["findings"])
