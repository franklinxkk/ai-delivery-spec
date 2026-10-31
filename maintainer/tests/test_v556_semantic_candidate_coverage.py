"""Candidate Diff consumes traceable grouped semantics, never arbitrary refs."""
from __future__ import annotations

import copy
import re
from pathlib import Path

import pytest

from test_review_workspace_contracts import html_gate, manifest, review_html


def grouped_document():
    doc = manifest('1' * 64)
    point = doc['review_points'][0]
    point.update(subject_ref='REG-X-PAGES', target_ref='REG-X-PAGES',
                 target_selector="[data-testid='region-REG-X-PAGES']", title='分页',
                 summary='上一页只在页码大于一时可用；下一页只在筛选结果还有下一页时可用。')
    parent = doc['semantic_coverage_items'][0]
    parent.update(subject_ref='REG-X-PAGES', target_ref='REG-X-PAGES', semantic_type='business_region',
                  human_summary=point['summary'])
    for name, summary in [('PREV', '上一页仅在页码大于一时回退一页，筛选条件保持不变。'),
                          ('NEXT', '下一页仅在筛选后仍有后续记录时前进一页，筛选条件保持不变。')]:
        item = copy.deepcopy(parent)
        item.update(coverage_id='SCOV-X-' + name, subject_ref='ACT-X-' + name,
                    semantic_type='action', source_refs=['REQ-X', 'ACT-X-' + name], human_summary=summary)
        doc['semantic_coverage_items'].append(item)
    return doc


def grouped_html(doc):
    raw = review_html(doc)
    raw = re.sub(r'<button data-action="REG-X-PAGES"[^>]*>.*?</button>',
                 '<section data-testid="region-REG-X-PAGES">'
                 '<button data-action="ACT-X-PREV">上一页</button>'
                 '<button data-action="ACT-X-NEXT">下一页</button></section>', raw, count=1)
    return raw.replace('const actionRegistry={', 'const actionRegistry={"ACT-X-PREV":()=>true,"ACT-X-NEXT":()=>true,', 1)


def candidate_refs(gate):
    return {ref for item in gate.findings if item.code == 'PROTO-REVIEW-CANDIDATE-DIFF' for ref in item.related_refs}


def test_two_real_actions_share_one_formal_point_without_duplicate_cards(tmp_path: Path):
    doc = grouped_document()
    gate = html_gate(tmp_path / 'group.html', grouped_html(doc))
    assert not {'ACT-X-PREV', 'ACT-X-NEXT'} & candidate_refs(gate)
    assert not [f for f in gate.findings if f.code.startswith('PROTO-REVIEW-')]
    assert len(doc['review_contexts'][0]['review_point_refs']) == 1
    assert len(doc['review_points']) == 2  # one list group and the existing drawer point


@pytest.mark.parametrize('mutation', ['missing_point', 'cross_context', 'gap', 'unconfirmed_point',
                                     'fake_target', 'fake_subject', 'not_applicable', 'missing_summary'])
def test_invalid_group_mapping_does_not_silence_candidate_diff(tmp_path: Path, mutation):
    doc = grouped_document()
    item = doc['semantic_coverage_items'][-2]  # Previous action
    if mutation == 'missing_point':
        item['review_point_refs'] = ['RVP-MISSING']
    elif mutation == 'cross_context':
        item['review_point_refs'] = ['RVP-DRAWER-CONFIRM']
    elif mutation == 'gap':
        item.update(coverage_status='gap', unknown_ref='UNK-X-PREV')
        doc['unknown_refs'] = ['UNK-X-PREV']
    elif mutation == 'unconfirmed_point':
        doc['review_points'][0]['business_status'] = 'gap'
    elif mutation == 'fake_target':
        item['target_ref'] = 'REG-NOT-REAL'
    elif mutation == 'fake_subject':
        item['subject_ref'] = 'ACT-NOT-REAL'
    elif mutation == 'not_applicable':
        item.update(coverage_status='not_applicable', ui_grounded=False, target_ref=None,
                    review_point_refs=[], human_summary=None, detail_owner='not_applicable',
                    not_applicable_reason='此语义不属于本页，不能代替实际按钮说明。')
    raw = grouped_html(doc)
    if mutation == 'missing_summary':
        # Remove the rendered sentence only; the manifest retains its declaration.
        raw = raw.replace(item['human_summary'], '说明未渲染', 1)
    gate = html_gate(tmp_path / 'invalid.html', raw)
    assert 'ACT-X-PREV' in candidate_refs(gate), [f.code for f in gate.findings]


def test_unlisted_formal_point_cannot_cover_group(tmp_path: Path):
    doc = grouped_document()
    raw = grouped_html(doc)
    # Keep the real HTML point/card and registry but remove it from the official context.
    import json
    doc['review_contexts'][0]['review_point_refs'] = []
    raw = re.sub(r'(<script type="application/json" id="review-workspace-manifest">).*?(</script>)',
                 lambda m: m[1] + json.dumps(doc, ensure_ascii=False) + m[2], raw, flags=re.S)
    gate = html_gate(tmp_path / 'orphan.html', raw)
    assert 'ACT-X-PREV' in candidate_refs(gate)
    assert any(f.code == 'PROTO-REVIEW-POINT-COVERAGE' for f in gate.findings)


def test_real_action_in_another_context_cannot_borrow_group_mapping(tmp_path: Path):
    raw = grouped_html(grouped_document())
    raw = raw.replace('data-review-context-type="DRAWER">',
                      'data-review-context-type="DRAWER"><button data-action="ACT-X-PREV">上一页</button>', 1)
    assert 'ACT-X-PREV' in candidate_refs(html_gate(tmp_path / 'cross-context.html', raw))


def test_schema_invalid_declaration_stays_blocked(tmp_path: Path):
    doc = grouped_document()
    doc['semantic_coverage_items'][-2]['review_point_refs'] = []
    gate = html_gate(tmp_path / 'invalid-schema.html', grouped_html(doc))
    assert any(f.code == 'PROTO-REVIEW-WORKSPACE-SCHEMA' and f.severity == 'BLOCK' for f in gate.findings)


def test_direct_point_in_another_context_is_not_a_global_exemption(tmp_path: Path):
    raw = review_html(manifest('1' * 64)).replace('data-review-context-type="DRAWER">',
        'data-review-context-type="DRAWER"><button data-action="ACT-X-SUBMIT">别处提交</button>', 1)
    assert 'ACT-X-SUBMIT' in candidate_refs(html_gate(tmp_path / 'direct-cross-context.html', raw))
