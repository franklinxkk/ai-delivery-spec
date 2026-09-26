from pathlib import Path
import hashlib
import json
import re
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from build_review_workspace import init_project, build_project
from quality_gate import Gate


def manifest(path):
    return json.loads(re.search(r'id="review-workspace-manifest">(.*?)</script>', path.read_text(encoding='utf-8'), re.S)[1])


def test_worked_starter_builds_real_contract_without_claiming_validation(tmp_path):
    project = tmp_path / '中文评审'
    init_project(project)
    result = build_project(project)
    assert result['status'] == 'built_not_validated'
    gate = Gate(); gate.check_prototype(project / 'prototype.html', 'L2')
    assert not [f for f in gate.findings if f.severity in ('BLOCK', 'GAP')]
    assert 'function request(' in (project / 'prototype.html').read_text(encoding='utf-8')


def test_build_binds_normalized_prd_and_invalidates_old_verification(tmp_path):
    init_project(tmp_path)
    prd = tmp_path / 'requirement.md'
    prd.write_bytes('新业务约定\r\n第二行\r第三行\n'.encode('utf-8'))
    source = tmp_path / 'review.json'
    doc = json.loads(source.read_text(encoding='utf-8'))
    doc['review_points'][0].update(verification_status='verified', evidence_refs=['EVD-OLD'])
    doc['cold_read_contract'].update(status='passed', evidence_refs=['EVD-OLD'])
    source.write_text(json.dumps(doc), encoding='utf-8')
    build_project(tmp_path)
    out = manifest(tmp_path / 'prototype.html')
    assert out['baseline']['hash'] == hashlib.sha256('新业务约定\n第二行\n第三行\n'.encode('utf-8')).hexdigest()
    assert out['review_points'][0]['verification_status'] == 'not_run'
    assert out['review_points'][0]['evidence_refs'] == []
    assert out['cold_read_contract']['status'] == 'pending'
    assert json.loads(source.read_text(encoding='utf-8')) == doc  # source evidence not overwritten


def test_init_does_not_overwrite_existing_work(tmp_path):
    (tmp_path / 'mine.txt').write_text('preserve', encoding='utf-8')
    with pytest.raises(ValueError, match='empty'):
        init_project(tmp_path)
    assert (tmp_path / 'mine.txt').read_text() == 'preserve'


def test_json_script_escape_and_resource_boundary(tmp_path):
    init_project(tmp_path)
    path = tmp_path / 'review.json'; doc = json.loads(path.read_text(encoding='utf-8'))
    doc['not_proven'] = ['</script><script>throw Error("wrong")</script>']
    path.write_text(json.dumps(doc), encoding='utf-8')
    build_project(tmp_path)
    assert manifest(tmp_path / 'prototype.html')['not_proven'] == doc['not_proven']
    with (tmp_path / 'runtime.js').open('a', encoding='utf-8') as f:
        f.write('\nconst bad="</script>";')
    with pytest.raises(ValueError, match='unsafe inline'):
        build_project(tmp_path)


def test_missing_fragment_or_overwrite_fails_before_output(tmp_path):
    init_project(tmp_path)
    with pytest.raises(ValueError, match='input'):
        build_project(tmp_path, tmp_path / 'layout.html')
    (tmp_path / 'style.css').rename(tmp_path / 'saved.css')
    with pytest.raises(ValueError, match='missing fragments'):
        build_project(tmp_path)
    assert not (tmp_path / 'prototype.html').exists()


def test_builder_does_not_silently_rebind_ready_handoff(tmp_path):
    init_project(tmp_path)
    path = tmp_path / 'review.json'; doc = json.loads(path.read_text(encoding='utf-8'))
    doc['machine_handoff']['status'] = 'ready'
    path.write_text(json.dumps(doc), encoding='utf-8')
    with pytest.raises(ValueError, match='signed handoff'):
        build_project(tmp_path)
