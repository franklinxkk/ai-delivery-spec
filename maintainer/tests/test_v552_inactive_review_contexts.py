import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from validators.gate_prototype_checks import _review_final_projection


def sample(owner='VIEW-B',wrapper='',workspace='REVIEW-X'):
    doc={'workspace_id':'REVIEW-X','workspace':{'initial_context_ref':'VIEW-A'},
         'review_contexts':[{'context_ref':'VIEW-A'},{'context_ref':'VIEW-B'}],
         'review_points':[{'ref':'RVP-B','owner_context_ref':'VIEW-B'}],
         'semantic_coverage_items':[{'coverage_id':'SCOV-B','owner_context_ref':'VIEW-B'}],
         'acceptance_examples':[{'example_ref':'TEST-B','owner_context_ref':'VIEW-B'}]}
    content=f'<article data-review-point="RVP-B" data-review-context="{owner}" hidden>可读业务<span hidden>隐藏假摘要</span><script>假脚本</script></article>'
    content+=f'<p data-review-semantic-ref="SCOV-B" data-review-context="{owner}" hidden>合法语义</p>'
    content+=f'<article data-review-example="TEST-B" data-review-context="{owner}" hidden>可执行样例<span hidden>隐藏预期</span></article>'
    if wrapper:content=wrapper.format(content)
    return f'<aside data-review-workspace="{workspace}"><section data-review-tab="function_flow" hidden>{content}</section></aside><script id="review-workspace-manifest" type="application/json">{json.dumps(doc)}</script>'


def test_bound_inactive_context_has_authored_text_not_visible_runtime_evidence():
    p=_review_final_projection(sample())
    assert p.card_text['RVP-B']=='可读业务'
    assert p.semantic_text['SCOV-B']=='合法语义'
    assert p.acceptance_example_text['TEST-B']=='可执行样例'
    assert p.cards[0]['visible']=='false'


@pytest.mark.parametrize('owner',['VIEW-A','VIEW-C',''])
def test_initial_unknown_and_mismatched_contexts_do_not_hide_required_text(owner):
    p=_review_final_projection(sample(owner))
    assert not p.card_text.get('RVP-B')
    assert not p.semantic_text.get('SCOV-B')


@pytest.mark.parametrize('wrapper',['<div hidden>{}</div>','<template>{}</template>','<div style="display:none">{}</div>'])
def test_arbitrary_hidden_ancestor_is_not_exempt(wrapper):
    p=_review_final_projection(sample(wrapper=wrapper))
    assert not p.card_text.get('RVP-B')


def test_other_workspace_cannot_reuse_manifest_exemption():
    assert not _review_final_projection(sample(workspace='REVIEW-OTHER')).card_text.get('RVP-B')


def test_invalid_manifest_owner_is_left_for_schema_diagnostics_not_a_parser_crash():
    raw = sample().replace('"owner_context_ref": "VIEW-B"', '"owner_context_ref": {}')
    assert not _review_final_projection(raw).card_text.get('RVP-B')


def test_explicit_css_and_aria_hiding_are_not_context_visibility_flags():
    for attr in ['style="display:none"','aria-hidden="true"','class="hidden"']:
        raw=sample().replace('data-review-point="RVP-B"',f'data-review-point="RVP-B" {attr}')
        assert not _review_final_projection(raw).card_text.get('RVP-B')
