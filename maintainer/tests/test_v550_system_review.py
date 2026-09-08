"""Behavioral regressions from source inspection, without loading any Skill."""
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from extract_interaction_ledger import attribute_inventory, attr_values
from requirement_contract import check_spec
from scan_requirement_ambiguity import inspect_content
from scan_prototype_css import scan
from query_domain import search_terms, term_matches


def kinds(text):
    return {x['kind'] for x in inspect_content(text)['findings']}


@pytest.mark.parametrize('metric_value', ['METRIC-COUNT', 'Revenue'])
def test_js_metric_fragment_is_in_inventory_but_not_dom_proof(tmp_path, metric_value):
    html = '''<main data-testid="page-VIEW-X" data-state="ready"></main>
    <!-- <span data-metric="METRIC-COMMENT">ignored</span> -->
    <script type="application/json">{"sample":"data-metric=\\"METRIC-JSON\\""}</script>
    <script>
    // mcard('data-metric="METRIC-JS-COMMENT"');
    // <section data-metric="METRIC-COMMENT-TAG">Old example</section>
    function mcard(anchor) { return '<section '+anchor+'>Count</section>'; }
    document.querySelector('main').innerHTML = mcard('data-metric="METRIC-COUNT"');
    </script>'''
    html = html.replace('METRIC-COUNT', metric_value)
    data = attribute_inventory(html, 'data-metric')
    assert attr_values(html, 'data-metric') == [metric_value]
    assert data['dynamic_candidates'][0]['dom_verified'] is False
    path = tmp_path/'metrics.html';path.write_text(html, encoding='utf-8')
    r = subprocess.run([sys.executable, '-X', 'utf8', '-B', 'scripts/ai_delivery_spec_cli.py', 'gate', '--profile', 'prototype', '--prototype', str(path), '--format', 'json'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    d = json.loads(r.stdout)
    assert d['status'] != 'PASS'
    assert any(f['code'] == 'PROTO-DYNAMIC-DECLARATIONS' and metric_value in f['ref'] for f in d['findings'])
    assert not any(f['code'] == 'PROTO-UNSTABLE-METRIC' for f in d['findings'])


def test_render_helpers_keep_action_and_modal_candidates():
    html = '''<script>const h = `${act('ACT-OPEN','Open')}`;
    showDialog({testid:'modal-VIEW-X'}); // act('ACT-COMMENT','ignore')
    </script>'''
    assert attr_values(html, 'data-action') == ['ACT-OPEN']
    assert attr_values(html, 'data-testid') == ['modal-VIEW-X']
    assert not attribute_inventory(html, 'data-action')['template_values']


def test_lookalike_attributes_do_not_define_contract_ids():
    assert attr_values('<p other-data-metric="METRIC-WRONG">x</p>', 'data-metric') == []


def table(status='已解决', header='类型'):
    return f'| ID | {header} | 关闭条件/结论 |\n|---|---|---|\n| UNK-X | {status} | DEC-X 已确认 |\n'


@pytest.mark.parametrize('header', ['类型','结论/状态','状态·结论','UNK 状态','status'])
def test_supported_status_headers_reuse_existing_closure(header):
    findings = check_spec({}, table(header=header))[0]
    assert not any(f['code'].startswith('SPEC-UNKNOWN') for f in findings)


def test_unknown_parser_uncertainty_is_not_closed_or_invalid_authored_status():
    missing = check_spec({}, table('业务规则', '类型'))[0]
    assert any(f['code']=='SPEC-UNKNOWN-STATUS-UNLOCATED' and f['severity']=='GAP' for f in missing)
    invalid = check_spec({}, table('mystery', '状态'))[0]
    assert any(f['code']=='SPEC-UNKNOWN-STATUS' and f['severity']=='BLOCK' for f in invalid)
    assert any(f['code']=='SPEC-UNKNOWN-CLOSURE' for f in check_spec({}, table().replace('DEC-X 已确认','-'))[0])


def test_body_tables_merge_absent_fields_and_name_true_conflict_sources():
    second = '| UNK/REV ID | 类型 | 阻断阶段 | 结论/状态 |\n|---|---|---|---|\n| UNK-X | 已解决 | none | DEC-X 已确认 |\n'
    assert not any(f['code']=='PRD-UNKNOWN-METADATA-DRIFT' for f in check_spec({},table()+'\n'+second)[0])
    conflict = check_spec({}, table()+'\n'+second.replace('已解决','已搁置'))[0]
    drift = next(f for f in conflict if f['code']=='PRD-UNKNOWN-METADATA-DRIFT')
    assert 'body table row 3' in drift['message'] and 'body table row 7' in drift['message']
    assert 'frontmatter' not in drift['message'] and 'status' in drift['message']
    doc = {'unknowns':[{'id':'UNK-X','status':'open','blocks_stage':'baseline'}]}
    assert 'frontmatter' in next(f['message'] for f in check_spec(doc,table())[0] if f['code']=='PRD-UNKNOWN-METADATA-DRIFT')


def test_navigation_container_actions_and_nested_items_are_independent():
    main = '<main data-testid="page-VIEW-X">{}</main>'
    first = '<div class="nav"><button class="nav-order">Order</button></div>'
    second = '<div class="tabs" data-action="ACT-SWITCH"><button>Tab</button></div>'
    assert 'dual-navigation' in {f['kind'] for f in scan(main.format(first+second))}
    nested = '<div class="nav"><div class="tabs" data-action="ACT-SWITCH"><button class="nav-order">Order</button></div></div>'
    assert 'dual-navigation' not in {f['kind'] for f in scan(main.format(nested))}


def test_business_role_and_status_do_not_become_ai_or_open_policy():
    business = '''## 代理商
    | do-agent-add-lead | 后端自动注入 partnerId 后保存，owner=代理商 |
    合同确认后自动关闭“合同待确认”响应任务，权限守卫为财务。
    | 规则触发类型 | [SLA超时/逾期/待确认/超期] |
    AI coding 可直接翻译为组件树；审计保留修改前后值。
    '''
    assert not kinds(business) & {'ai-write','open-decision'}
    assert 'ai-write' in kinds(business+'\nAI Agent 自动修改客户账单并保存。')
    assert 'open-decision' in kinds(business+'\n补考取值规则尚未最终确定。')
    assert 'ai-write' in kinds('Agent 自动保存客户审批结果。')


def test_diagnostic_note_does_not_retrigger_but_following_business_does():
    note = '- 说明：18 条 gaps（SPEC-CONTENT-*）包含深链权限问题'
    assert not kinds(note)
    assert 'ai-write' in kinds(note+'。AI 自动修改账单并保存。')
    assert 'null-meaning' not in kinds('| 修改前 | oldValue；新增类型为空 |')
    assert 'null-meaning' in kinds('字段可空。')


def test_policy_natural_chinese_keeps_unresolved_state_visible():
    assert 'policy-basis' not in kinds('补考成绩取最新一次，该规则已由教务处确认。')
    assert 'undecided-policy' in kinds('补考成绩取最新一次，该规则尚未最终确定。')
    assert 'undecided-policy' in kinds('补考成绩取最新一次，该规则待确认；曾由教务处批准。')


def test_aliases_do_not_equate_active_with_inactive_or_mileage_with_milestone():
    aliases = yaml.safe_load((ROOT/'references/domain-coverage.yaml').read_text(encoding='utf-8'))['search_aliases']
    assert 'mileage' in search_terms('车辆里程', aliases)
    assert 'mileage' not in search_terms('项目里程碑', aliases)
    assert 'mileage' in search_terms('车辆里程和项目里程碑', aliases)
    assert 'active' not in search_terms('活跃', aliases)
    assert not term_matches('active','inactive')
    assert not term_matches('ledger','pledger')
    assert term_matches('active customer','active customers')
    for zh,en in [('里程','mileage'),('报销','reimbursement'),('台账','ledger')]:
        assert en in search_terms(zh,aliases)
