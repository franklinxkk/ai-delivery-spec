from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from validators.gate_prototype_checks import _review_final_projection


def fragment(payload):
    return '<aside data-review-workspace="REVIEW-X">'+payload+'</aside>'


def content():
    return '<article data-review-point="RVP-X">真实卡片<span hidden>藏起来的假摘要</span></article><p data-review-semantic-ref="SCOV-X">真实业务约定<script>假脚本</script></p>'


def test_inactive_tab_preserves_authored_text_but_not_nested_hidden_payload():
    p=_review_final_projection(fragment('<section data-review-tab="function_flow" hidden>'+content()+'</section>'))
    assert p.card_text['RVP-X']=='真实卡片'
    assert p.semantic_text['SCOV-X']=='真实业务约定'
    assert p.cards[0]['visible']=='false'  # Static text extraction is not a visible-runtime claim.


def test_arbitrary_hidden_container_cannot_masquerade_as_a_review_tab():
    for wrapper in ['<section hidden>{}</section>','<template>{}</template>','<section data-review-tab="fake" hidden>{}</section>']:
        p=_review_final_projection(fragment(wrapper.format(content())))
        assert not p.card_text.get('RVP-X')
        assert not p.semantic_text.get('SCOV-X')


def test_hidden_card_inside_a_real_tab_remains_unreadable():
    p=_review_final_projection(fragment('<section data-review-tab="function_flow" hidden><div hidden>'+content()+'</div></section>'))
    assert not p.card_text['RVP-X']


def test_tab_outside_workspace_is_not_exempt_from_hidden():
    p=_review_final_projection('<section data-review-tab="function_flow" hidden>'+content()+'</section>')
    assert not p.card_text['RVP-X']
