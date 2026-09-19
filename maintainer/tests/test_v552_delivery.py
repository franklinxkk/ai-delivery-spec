"""Behavior regressions from normal installation and explicit review delivery."""
from pathlib import Path
import hashlib
import json
import py_compile
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from ai_delivery_spec_cli import validate_runtime_manifest
from triage_requirement import recommend
from quality_gate import Gate
from test_review_workspace_contracts import manifest, review_html, manifest_v549, review_html_v549


def lightweight_review(tmp_path):
    import re
    doc=manifest('1'*64,level='R0')
    for key in ('share_contract','review_record_contract','progress_contract'):
        doc.pop(key)
    raw=review_html(doc,include_tabs=False)
    raw=re.sub(r'<button[^>]*data-action="UIACT-REVIEW-(?:SHARE|RECORD|EXPORT|IMPORT)"[^>]*>.*?</button>', '', raw)
    raw=re.sub(r'<div data-review-(?:progress|records)\b[^>]*>.*?</div>', '', raw)
    # These functions are genuinely absent, not hidden behind renamed stubs.
    raw=re.sub(r'function (?:saveReviewRecords|loadReviewRecords|hydrateLocator)\([^\n]*', '', raw)
    path=tmp_path/'light.html'
    path.write_text(raw,encoding='utf-8')
    return path,raw,doc


def test_r0_annotations_do_not_force_tracking_or_sharing(tmp_path):
    path,raw,doc=lightweight_review(tmp_path)
    gate=Gate();gate.check_prototype(path,'L2')
    assert not [x for x in gate.findings if x.code.startswith('PROTO-REVIEW-')], gate.findings
    # The lightweight path still rejects a missing review target.
    path.write_text(raw.replace('data-action="ACT-X-SUBMIT"', 'data-action="ACT-X-LOST"', 1),encoding='utf-8')
    gate=Gate();gate.check_prototype(path,'L2')
    assert 'PROTO-REVIEW-TARGET-RESOLUTION' in {x.code for x in gate.findings}


def test_r0_cannot_claim_unimplemented_features_or_bypass_r1(tmp_path):
    path,raw,doc=lightweight_review(tmp_path)
    for button in ('SHARE','RECORD'):
        path.write_text(raw.replace('</aside>',f'<button data-action="UIACT-REVIEW-{button}">Feature</button></aside>'),encoding='utf-8')
        gate=Gate();gate.check_prototype(path,'L2')
        assert 'PROTO-REVIEW-WORKSPACE-SCHEMA' in {x.code for x in gate.findings}
    # Raising review_level restores the full contract, even with no controls.
    path.write_text(raw.replace('"review_level": "R0"','"review_level": "R1"'),encoding='utf-8')
    gate=Gate();gate.check_prototype(path,'L2')
    assert 'PROTO-REVIEW-WORKSPACE-SCHEMA' in {x.code for x in gate.findings}


def test_used_runtime_accepts_only_cache_of_declared_sources(tmp_path):
    source = tmp_path / 'scripts' / 'sample.py'
    source.parent.mkdir()
    source.write_text('VALUE = 7\n', encoding='utf-8')
    data = source.read_bytes()
    manifest = {'schema_version': '5.3.0', 'skill_version': '5.5.2',
                'source_commit': 'uncommitted-dirty', 'source_worktree_dirty': True,
                'files': [{'path': 'scripts/sample.py', 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}]}
    (tmp_path / 'runtime-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    assert validate_runtime_manifest(tmp_path) == []
    cache = Path(py_compile.compile(str(source), doraise=True))
    assert cache.exists()
    assert validate_runtime_manifest(tmp_path) == []
    rogue = cache.with_name('undeclared.cpython-312.pyc')
    rogue.write_bytes(b'not shipped')
    assert validate_runtime_manifest(tmp_path)
    rogue.unlink()
    source.write_text('VALUE = 8\n', encoding='utf-8')
    assert validate_runtime_manifest(tmp_path)


def test_feedback_without_goal_does_not_accept_but_explicit_change_survives():
    for title in ['这系统太烂了，不想说了', 'This tool is terrible']:
        value = recommend({'title': title})
        assert value['recommendation'] == 'clarify'
        assert value['next_questions'] and not value['lifecycle_mutated']
    for title in ['这系统难用，请增加按创建日期排序', 'Please add sorting by creation date']:
        assert recommend({'title': title})['recommendation'] == 'accept'


def test_explicit_review_flag_cannot_be_satisfied_by_plain_prototype(tmp_path):
    html = tmp_path / 'plain.html'
    html.write_text('<!doctype html><main data-testid="page-VIEW-X">普通页面</main>', encoding='utf-8')
    args = [sys.executable, str(ROOT/'scripts/ai_delivery_spec_cli.py'), 'gate',
            '--profile', 'prototype', '--prototype', str(html), '--format', 'json']
    ordinary = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    required = subprocess.run([*args, '--require-review-workspace'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    code = 'PROTO-REVIEW-WORKSPACE-MANIFEST-INVALID'
    assert code not in {x['code'] for x in json.loads(ordinary.stdout)['findings']}
    payload = json.loads(required.stdout)
    assert code in {x['code'] for x in payload['findings']}
    assert required.returncode == 2
    assert '--require-review-workspace' in payload['retry_command']

    # An explicitly requested review contract cannot inherit an exemption from
    # an old, equally incomplete review surface.
    html.write_text('<!doctype html><main data-testid="page-VIEW-X"></main><aside data-review-workspace="REVIEW-X"></aside>', encoding='utf-8')
    inherited = subprocess.run([*args, '--require-review-workspace', '--prototype-baseline', str(html)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    assert any(x['code'] == code and x['severity'] == 'BLOCK' for x in json.loads(inherited.stdout)['findings'])


def test_event_driven_review_does_not_require_mutation_observer(tmp_path):
    raw = review_html_v549(manifest_v549('1'*64))
    import re
    raw = re.sub(r'new MutationObserver\(.*?\.observe\(document.body,.*?\);', '', raw)
    assert 'MutationObserver' not in raw
    path = tmp_path/'event.html'
    path.write_text(raw, encoding='utf-8')
    gate = Gate()
    gate.check_prototype(path, 'L2')
    assert 'PROTO-REVIEW-OVERLAY-DETECTION' not in {x.code for x in gate.findings}
    path.write_text(raw.replace('window.addEventListener(productContextEvent,resolveCurrentContext);', ''), encoding='utf-8')
    gate = Gate()
    gate.check_prototype(path, 'L2')
    assert 'PROTO-REVIEW-OVERLAY-DETECTION' in {x.code for x in gate.findings}


def test_shipped_review_example_is_bound_and_has_no_blockers():
    args = [sys.executable, str(ROOT/'scripts/ai_delivery_spec_cli.py'), 'gate', '--profile', 'prototype',
            '--prototype', str(ROOT/'examples/medium-review-handoff/review-prototype.html'),
            '--prd', str(ROOT/'examples/medium-review-handoff/requirement.md'),
            '--stage', 'specify', '--require-review-workspace', '--format', 'json']
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    payload = json.loads(result.stdout)
    assert not [x for x in payload['findings'] if x['severity'] == 'BLOCK'], payload['findings']
    assert payload['metrics']['review_workspace_required']
