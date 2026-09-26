"""Paired regressions for local permission and returned-object probes.

These synthetic examples verify diagnostic scope, not complete semantic review.
"""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from requirement_contract import check_spec
from scan_requirement_ambiguity import inspect_content


def kinds(text):
    return {item["kind"] for item in inspect_content(text)["findings"]}


@pytest.mark.parametrize("text", [
    "真实身份、角色及访问范围由服务端读取；隐藏按钮不能代替授权。各模块实际请求与直接深链都须检查当前角色和对象范围。缺少权限时拒绝且不泄露对象详情。",
    "深链检查当前身份和数据范围。",
    "直接请求和深链必须校验当前权限及对象访问范围。",
])
def test_explicit_link_check_answers_permission_question(text):
    assert "deep-link" not in kinds(text)
    assert "permission" in inspect_content(text)["risk_facets"]


@pytest.mark.parametrize("text", [
    "隐藏按钮不能代替授权。真实身份和角色由服务端读取。直接深链可以查看对象详情。",
    "直接深链只检查当前角色，不检查对象范围。",
    "直接深链检查对象范围。",
    "深链无需检查当前角色和对象范围。",
    "深链尚未检查当前角色和对象范围。",
    "深链由服务端不校验权限即可访问。",
    "深链计划检查当前角色和对象范围。",
    "## REQ-A\n深链直接访问。\n## REQ-B\n深链检查当前角色和对象范围。",
])
def test_missing_negated_proposed_and_other_scope_checks_still_gap(text):
    assert "deep-link" in kinds(text)


@pytest.mark.parametrize("summary", [
    "任务显示必要的退回历史；这里读取对应轮次的提交内容，不能误用别的申请或轮次。",
    "| 审核轮次/任务 | 每次提交新增；待审核 → 通过或退回 | 关联申请及提交内容快照；旧轮次结果不可覆盖新轮次 |",
    "详情显示退回记录。再次提交的内容在审核页展示。",
])
def test_history_and_round_summaries_do_not_redefine_return_policy(summary):
    assert "return-object" not in kinds(summary)
    assert "return-object" in kinds(summary + "\n退回后重新提交。")


def test_identity_field_row_answers_retention_without_repeated_recovery_rules():
    row = "| 申请编号/申请身份 | 保存后系统分配的稳定身份；用户不可改 | 退回、重提、付款全过程沿用；编号不替代审核轮次/指令 ID |"
    assert "return-object" not in kinds(row)
    assert "return-object" in kinds(row.replace("全过程沿用", "后续如何使用待定"))
    assert "return-object" in kinds(row.replace("全过程沿用", "不能全过程沿用"))
    # A different field being retained does not determine record identity.
    assert "return-object" in kinds(row.replace("申请编号/申请身份", "事由"))


def test_new_request_and_returned_original_are_different_paths():
    paragraph = (
        "列表可查看当前状态和退回历史。列表新建申请进入空白表单，保存后分配新的申请身份。"
        "已有草稿/退回单据进入同一原单编辑，不能以复制新单实现退回恢复。"
    )
    assert "return-conflict" not in kinds(paragraph)
    assert "return-conflict" in kinds(paragraph + "退回后原单关闭，新建对象提交。")


@pytest.mark.parametrize("good,bad", [
    ("退回后编辑原单，重提时新建审核任务。", "退回后编辑原单，重提时新建对象提交。"),
    ("退回后编辑原单，不新建对象提交。", "退回后编辑原单，并新建对象提交。"),
    ("退回后不编辑原单，新建对象提交。", "退回后编辑原单，新建对象提交。"),
    ("报销单退回后编辑原单。采购单退回后关闭原单并新建对象提交。",
     "报销单退回后编辑原单。报销单退回后关闭原单并新建对象提交。"),
])
def test_return_policies_bind_to_affirmative_object_path(good, bad):
    assert "return-conflict" not in kinds(good)
    assert "return-conflict" in kinds(bad)


def test_real_conflict_remains_a_gate_gap_even_with_unrelated_branch_or_review_pass():
    body = "## 行为\n### 修改\n退回后申请人编辑原单。\n### 财务\n退回后原单关闭，新建对象提交。\n如果用户仅浏览则只读，否则分别校验。"
    doc = {"semantic_reviews": [{"category": "recovery", "result": "pass", "scope_refs": ["REQ-A"],
            "source_refs": ["SRC-A"], "reviewer": "reviewer", "baseline_version": "1", "evidence_ref": "review.md"}],
           "baseline_version": "1"}
    assert any(f["code"] == "SPEC-CONTENT-RETURN-CONFLICT" and f["severity"] == "GAP"
               for f in check_spec(doc, body)[0])
    # A generic object name and its qualified name are not proven independent.
    assert "return-conflict" in kinds("申请退回后编辑原单。报销申请退回后原单关闭，新建对象提交。")


def test_unknown_index_cannot_infer_closed_and_normalized_open_remains_unresolved():
    index = "| 稳定标识 | 权威定义位置与页面落点 |\n|---|---|\n| UNK-PAY-01 | 模块三银行拒绝后的后续指令政策 |"
    body = "**UNK-PAY-01（产品未决定）：银行拒绝后是否可创建新付款指令。**\n" + index
    findings, routed = check_spec({}, body, stage="implementation")
    assert "SPEC-UNKNOWN-STATUS-UNLOCATED" in {f["code"] for f in findings}
    assert routed["unknown_summary"]["refs"]["status_unresolved"] == ["UNK-PAY-01"]
    unknown = {"id": "UNK-PAY-01", "status": "open", "affected_refs": ["REQ-PAY-RETRY"], "blocks_stage": "implementation"}
    doc = {"unknowns": [unknown]}
    findings, routed = check_spec(doc, body, stage="implementation", scope=("REQ-PAY-RETRY",))
    assert routed["unknown_summary"]["refs"]["blocking_now"] == ["UNK-PAY-01"]
    assert any(f["code"] == "SPEC-OPEN-DECISION" and f["severity"] == "BLOCK" for f in findings)
    assert not check_spec(doc, body, stage="implementation", scope=("REQ-PAY-FIRST",))[1]["unknown_summary"]["refs"]["blocking_now"]
    unknown["status"] = "closed"
    assert "SPEC-UNKNOWN-CLOSURE" in {f["code"] for f in check_spec(doc, body)[0]}


def test_unknown_status_conflict_cannot_be_silently_normalized():
    body = "| ID | 状态 |\n|---|---|\n| UNK-A | closed |"
    doc = {"unknowns": [{"id": "UNK-A", "status": "open"}]}
    assert "PRD-UNKNOWN-METADATA-DRIFT" in {f["code"] for f in check_spec(doc, body)[0]}


def test_body_unknown_explicit_scope_is_preserved_without_metadata_copy():
    body = "| ID | status | affected_refs | blocks_stage |\n|---|---|---|---|\n| UNK-RETRY | open | RULE-RETRY, RULE-APPROVER | implementation |"
    _, selected = check_spec({}, body, stage="implementation", scope=("RULE-RETRY",))
    assert selected["unknown_summary"]["refs"]["blocking_now"] == ["UNK-RETRY"]
    _, unrelated = check_spec({}, body, stage="implementation", scope=("RULE-FIRST-PAYMENT",))
    assert unrelated["unknown_summary"]["refs"]["out_of_scope"] == ["UNK-RETRY"]
    assert not unrelated["unknown_summary"]["refs"]["blocking_now"]
    # Without a declared reference there is no authority to assume separation.
    _, missing = check_spec({}, body.replace("RULE-RETRY, RULE-APPROVER", ""), stage="implementation", scope=("RULE-FIRST-PAYMENT",))
    assert missing["unknown_summary"]["refs"]["blocking_now"] == ["UNK-RETRY"]
@pytest.mark.parametrize('text', [
    '非管理员看不到入口，直接深链访问会话管理 API 返回拒绝，不返回会话列表。',
    '| 无权操作 | 审计员尝试新增 | 无按钮/深链拒绝 | 不产生变更 |',
])
def test_explicit_denied_deep_link_is_not_missing_authorization(text):
    from scan_requirement_ambiguity import inspect_content
    assert not any(x['kind'] == 'deep-link' for x in inspect_content(text)['findings'])


@pytest.mark.parametrize('text', ['深链未拒绝越权访问。', '深链不拒绝访问。', '建议深链拒绝访问。', '深链仅隐藏按钮。'])
def test_deep_link_denial_must_be_actual_policy(text):
    from scan_requirement_ambiguity import inspect_content
    assert any(x['kind'] == 'deep-link' for x in inspect_content(text)['findings'])
def test_explicit_identity_and_server_verification_synonyms():
    from scan_requirement_ambiguity import inspect_content
    good='''## 合同
退回重提仍用原 ID 与号，历史保留；合同 ID/号不变。
每次读写由服务端重新验证当前身份、对象范围、状态和版本。深链适用相同检查。
'''
    kinds={f['kind'] for f in inspect_content(good)['findings']}
    assert not kinds & {'return-object','deep-link'}
    bad=good.replace('仍用原 ID 与号，历史保留；合同 ID/号不变','是否新建待确认').replace('重新验证','未验证')
    kinds={f['kind'] for f in inspect_content(bad)['findings']}
    assert {'return-object','deep-link'} <= kinds
