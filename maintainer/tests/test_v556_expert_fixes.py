"""Focused intake, review-boundary and decision-aid regression cases."""
from pathlib import Path
import copy
import json
import re
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'scripts/validators')]
from triage_requirement import recommend
from quality_gate import Gate
from query_domain import common_pattern_candidates
from build_review_workspace import init_project, build_project, text_hash


@pytest.mark.parametrize('body', [
    '登录失败锁定阈值是多少；异地登录是否 MFA；历史系统无标准客户端如何接入；单点登出通知失败是否重试；同人是否允许多端在线。',
    'How many failed logins trigger a lockout?; Should new devices require MFA?; How should legacy clients connect?; Should failed single logout retry?; Can one user keep concurrent sessions?',
])
def test_direct_questions_remain_unresolved_without_pending_labels(body):
    doc = {'title': 'CAS SSO', 'brief': body}
    before = copy.deepcopy(doc)
    result = recommend(doc)
    assert result['recommendation'] == 'clarify'
    assert len([c for c in result['clarification_candidates'] if c['kind']=='explicit-question']) == 5
    assert len(result['next_questions']) >= 5
    assert doc == before and not result['lifecycle_mutated']
    assert result['decision_status'] == 'proposed'


@pytest.mark.parametrize('text', [
    '登录失败 5 次锁定 10 分钟；异地登录不要求 MFA；同人允许多端在线。',
    '检查是否启用并显示结果。',
    '将按钮文案改为“是否继续？”。',
    '是否允许多端在线？答：不允许。',
    '是否允许多端在线？\n答：不允许。',
    '离线登录如何接入不在本次范围。',
    '是否启用由管理员配置。',
    'Check whether the current user has access.',
    'Should concurrent sessions be allowed? Answer: yes.',
    'Rename the label to "Should we continue?".',
])
def test_known_answers_and_ui_copy_do_not_reopen_policy(text):
    result = recommend({'title':'登录页小改', 'brief': text})
    assert not [c for c in result['clarification_candidates'] if c.get('kind')=='explicit-question']
    assert result['recommendation'] == 'accept'


def test_one_answer_does_not_silence_another_question():
    result = recommend({'title':'退款处理', 'brief':'是否允许退款？答：允许；部分退款失败如何恢复？'})
    assert result['recommendation'] == 'clarify'
    direct = [c for c in result['clarification_candidates'] if c.get('kind')=='explicit-question']
    assert len(direct)==1 and '部分退款' in direct[0]['context']


def test_quoted_business_question_is_not_mistaken_for_ui_copy():
    result = recommend({'title':'认证规则', 'brief':'请确认“异地登录是否要求 MFA？”'})
    assert result['recommendation']=='clarify'
    assert any('MFA' in c['context'] for c in result['clarification_candidates'])


@pytest.mark.parametrize('question', ['异地登录需要二次认证吗？', '退回是修改原单还是新建？', '待决定：是否允许多端在线？'])
def test_other_direct_question_forms_also_need_a_decision(question):
    result = recommend({'title':'业务规则', 'brief':question})
    assert result['recommendation']=='clarify'
    assert any(c.get('kind')=='explicit-question' for c in result['clarification_candidates'])


@pytest.mark.parametrize('ref,label,severity', [
    ('ACT-ADMIN-FORCE-LOGOUT','强制登出所选会话','BLOCK'),
    ('ACT-KEY-ROTATE','轮换密钥','BLOCK'),
    ('ACT-EXPORT-CUSTOMERS','导出客户信息','BLOCK'),
    ('ACT-ACCOUNT-DISABLE','停用账号','BLOCK'),
    ('ACT-DO-ONE','<span>管理员强制退出所选会话</span>','BLOCK'),
    ('ACT-DO-TWO','Rotate credentials','BLOCK'),
    ('ACT-DO-THREE','冻结账号','BLOCK'),
    ('ACT-USER-LOGOUT','退出我的会话','GAP'),
    ('ACT-ADMIN-LOGOUT','管理员退出自己的账号','GAP'),
    ('ACT-ROTATE','旋转图片','GAP'),
    ('ACT-ENABLE-PREVIEW','启用预览','GAP'),
    ('ACT-EXPORT','导出当前筛选结果','GAP'),
    ('ACT-HELP','查看强制退出说明','GAP'),
    ('ACT-DISCLOSE','查看说明','GAP'),
    ('ACT-PAYMENT-DETAILS','查看付款详情','GAP'),
])
def test_real_review_gate_uses_action_object_and_effect(tmp_path,ref,label,severity):
    source=(ROOT/'examples/medium-review-handoff/review-prototype.html').read_text(encoding='utf8')
    source=source.replace('<section class="order-card">', f'<button data-action="{ref}">{label}</button><section class="order-card">',1)
    path=tmp_path/'review.html';path.write_text(source,encoding='utf8')
    gate=Gate();gate.check_prototype(path,'L2')
    issues=[i for i in gate.findings if i.code=='PROTO-REVIEW-CANDIDATE-DIFF' and i.ref==ref]
    assert len(issues)==1 and issues[0].severity==severity


@pytest.mark.parametrize('query',['统一身份认证 CAS SSO 登录会话','SSO','企业单点登录','MFA'])
def test_identity_search_returns_prompts_without_authorizing_policy(query):
    hits=common_pattern_candidates(query)
    assert len(hits)==1
    assert hits[0]['pattern_ref']=='PAT-IDENTITY-SESSION-001'
    assert hits[0]['authority']=='decision_prompts_not_project_policy'
    assert len(hits[0]['questions'])==5


def test_unrelated_terms_do_not_inject_identity_policy():
    assert common_pattern_candidates('库存盘点')==[]
    assert common_pattern_candidates('cassette')==[]


@pytest.mark.parametrize('level,mode',[('R0','tabs'),('R1','tabs'),('R1','contextual')])
def test_generated_starters_separate_business_and_review_tool(tmp_path,level,mode):
    directory=tmp_path/'starter';init_project(directory,level,mode)
    prd=(directory/'requirement.md').read_text(encoding='utf8')
    canonical=(ROOT/'examples/medium-review-handoff/requirement.md').read_text(encoding='utf8')
    assert prd==canonical.replace('(review-prototype.html)','(prototype.html)')
    assert '评审面板提供总览' not in prd and '可导入导出' not in prd
    assert '仅当调用者为调度员' in prd and '最长 100 个 Unicode 码点' in prd
    built=build_project(directory)
    html=Path(built['output']).read_text(encoding='utf8')
    assert '样例与评审工具说明' in html and 'requirement.md' in html
    assert built['baseline_text_sha256']==text_hash(prd)
    if level=='R0':
        assert 'R0 仅提供就近阅读' in html
        assert 'data-action="UIACT-REVIEW-IMPORT"' not in html
    else:
        assert 'data-action="UIACT-REVIEW-IMPORT"' in html
