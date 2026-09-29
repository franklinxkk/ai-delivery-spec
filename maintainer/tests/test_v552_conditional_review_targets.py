"""Static uncertainty must not masquerade as either runtime failure or PASS."""
from pathlib import Path
import re
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from quality_gate import Gate
from validators.validate_prd_semantics import collect_defined_ids
from test_review_workspace_contracts import manifest,review_html

def findings(tmp_path,raw):
    path=tmp_path/'conditional.html';path.write_text(raw,encoding='utf-8')
    gate=Gate();gate.check_prototype(path,'L2')
    return gate.findings

@pytest.mark.parametrize('remove_target,initial,expected',[(True,False,'GAP'),(False,False,'BLOCK'),(True,True,'BLOCK')])
def test_absent_inactive_control_requires_runtime_evidence(tmp_path,remove_target,initial,expected):
    doc=manifest('1'*64)
    point=doc['review_points'][0 if initial else 1]
    raw=review_html(doc)
    raw=re.sub(r'<button\b[^>]*data-review-ref="'+point['ref']+r'"[^>]*>.*?</button>','',raw)
    if remove_target:
        raw=re.sub(r'<button\b[^>]*data-action="'+point['target_ref']+r'"[^>]*>.*?</button>','',raw)
    result=[f for f in findings(tmp_path,raw) if f.code=='PROTO-REVIEW-POINT-COVERAGE' and f.ref==point['ref']]
    assert result and {f.severity for f in result}=={expected}

def test_duplicate_marker_is_still_a_binding_error(tmp_path):
    doc=manifest('1'*64);point=doc['review_points'][1];raw=review_html(doc)
    marker=re.search(r'<button\b[^>]*data-review-ref="'+point['ref']+r'"[^>]*>.*?</button>',raw).group()
    raw=raw.replace(marker,marker+marker)
    assert any(f.code=='PROTO-REVIEW-POINT-COVERAGE' and f.severity=='BLOCK' for f in findings(tmp_path,raw))

@pytest.mark.parametrize('action,severity',[
    ('ACT-X-OVERLAY-CLOSE','GAP'),
    ('ACT-X-CONTRACT-CLOSE','BLOCK'),
    ('ACT-X-SAVE-OVERLAY-CLOSE','BLOCK'),
])
def test_surface_dismissal_name_is_not_proof_of_business_write(tmp_path,action,severity):
    raw=review_html(manifest('1'*64))
    raw=raw.replace('</main>',f'<button data-action="{action}">关闭</button></main>',1)
    result=[f for f in findings(tmp_path,raw) if f.code=='PROTO-REVIEW-CANDIDATE-DIFF' and f.ref==action]
    assert result and {f.severity for f in result}=={severity}

@pytest.mark.parametrize('family',['DRAWER','MODAL','POPOVER'])
def test_review_context_identity_defined_in_prd_can_be_resolved(family):
    ref=family+'-PAYMENT'
    raw=f'| 业务引用 | 说明 |\n|---|---|\n| {ref} | 回款登记与校验 |\n'
    assert ref in collect_defined_ids(raw)


def test_declared_business_action_may_bind_to_its_containing_region(tmp_path):
    doc=manifest('1'*64)
    point=doc['review_points'][0]
    action=point['subject_ref']
    point.update(target_ref='REG-ACTIONS',target_selector="[data-review-anchor='REG-ACTIONS']")
    raw=review_html(doc).replace('</main>',
        f'<button data-action="{action}">提交</button>'
        '<button data-action="ACT-UNDECLARED-DELETE">删除</button></main>',1)
    candidates={f.ref:f.severity for f in findings(tmp_path,raw) if f.code=='PROTO-REVIEW-CANDIDATE-DIFF'}
    assert action not in candidates
    assert candidates['ACT-UNDECLARED-DELETE']=='BLOCK'
