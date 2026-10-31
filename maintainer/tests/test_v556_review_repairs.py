from pathlib import Path
import sys,json,re,hashlib
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from build_review_workspace import init_project,build_project
from extract_interaction_ledger import dynamic_attribute_fragments
from quality_gate import Gate
from jsonschema import Draft202012Validator
from validators.gate_prototype_checks import compact_schema_error

ROOT=Path(__file__).resolve().parents[2]
def manifest(p):return json.loads(re.search(r'id="review-workspace-manifest">(.*?)</script>',p.read_text(encoding='utf8'),re.S)[1])

def test_examples_scale_without_accepting_invalid_example(tmp_path):
    init_project(tmp_path);d=json.loads((tmp_path/'review.json').read_text(encoding='utf8'))
    row=d['acceptance_examples'][0]
    d['acceptance_examples']=[dict(row,example_ref=f'TEST-X-{i}') for i in range(42)]
    validator=Draft202012Validator(json.loads((ROOT/'schemas/review-workspace.schema.json').read_text(encoding='utf-8')))
    assert not list(validator.iter_errors(d))
    d['acceptance_examples'][30].pop('expected_domain_result')
    assert any(list(e.path)[:2]==['acceptance_examples',30] for e in validator.iter_errors(d))

def test_concatenation_is_unknown_but_static_bad_id_still_bad(tmp_path):
    dynamic="<script>host.innerHTML='<button data-action=\"ACT-'+suffix+'\">go</button>';</script>"
    assert dynamic_attribute_fragments(dynamic,'data-action')==['ACT-']
    assert dynamic_attribute_fragments('<button data-action="ACT-">go</button>'+dynamic,'data-action')==[]
    p=tmp_path/'p.html';p.write_text('<main data-testid="page-VIEW-X">'+dynamic+'</main>')
    g=Gate();g.check_prototype(p,'L2')
    assert any(f.code=='PROTO-DYNAMIC-ACTION-FRAGMENT' and f.severity=='GAP' for f in g.findings)
    assert not any(f.code=='PROTO-UNSTABLE-ACTION' for f in g.findings)
    p.write_text('<main data-testid="page-VIEW-X"><button data-action="BAD">go</button></main>')
    g=Gate();g.check_prototype(p,'L2');assert any(f.code=='PROTO-UNSTABLE-ACTION' for f in g.findings)

def test_source_and_projection_fingerprints_are_distinct_and_checked(tmp_path):
    init_project(tmp_path);src=tmp_path/'source.docx';src.write_bytes(b'binary source for fingerprint test')
    build_project(tmp_path,source_document=src);d=manifest(tmp_path/'prototype.html')
    assert d['baseline']['source_file_sha256']==hashlib.sha256(src.read_bytes()).hexdigest()
    assert d['baseline']['hash']!=d['baseline']['source_file_sha256']
    g=Gate();g.check_prototype(tmp_path/'prototype.html','L2');g.check_handoff(tmp_path/'requirement.md',[tmp_path/'prototype.html'],'L2')
    assert not any(f.code in {'PROTO-REVIEW-BASELINE-DRIFT','PROTO-REVIEW-SOURCE-FILE-DRIFT'} for f in g.findings)
    src.write_bytes(b'changed');g=Gate();g.check_prototype(tmp_path/'prototype.html','L2');g.check_handoff(tmp_path/'requirement.md',[tmp_path/'prototype.html'],'L2')
    assert any(f.code=='PROTO-REVIEW-SOURCE-FILE-DRIFT' for f in g.findings)

def test_r0_has_real_business_and_no_enabled_signoff_ui(tmp_path):
    init_project(tmp_path,'R0');build_project(tmp_path);d=manifest(tmp_path/'prototype.html');raw=(tmp_path/'prototype.html').read_text(encoding='utf8')
    assert d['workspace']['review_level']=='R0'
    assert not {'share_contract','review_record_contract','progress_contract'}&d.keys()
    for name in ['SHARE','RECORD','EXPORT','IMPORT']:
        assert f'data-action="UIACT-REVIEW-{name}"' not in raw
        assert f"'UIACT-REVIEW-{name}':" not in raw
    g=Gate();g.check_prototype(tmp_path/'prototype.html','L2')
    assert not [f for f in g.findings if f.severity in ('BLOCK','GAP')]

def test_contextual_layout_does_not_require_three_tabs(tmp_path):
    init_project(tmp_path);p=tmp_path/'review.json';d=json.loads(p.read_text(encoding='utf8'));d['workspace']['presentation_mode']='contextual';d['cold_read_contract'].update(time_limit_seconds=600,declared_point_recall_min=.7,critical_point_recall=.9);p.write_text(json.dumps(d),encoding='utf8')
    q=tmp_path/'layout.html';s=q.read_text(encoding='utf8');s=re.sub(r'<nav\b[^>]*>.*?</nav>','',s,flags=re.S);s=re.sub(r' data-review-tab="[^"]+"','',s);q.write_text(s,encoding='utf8')
    build_project(tmp_path);g=Gate();g.check_prototype(tmp_path/'prototype.html','L2')
    assert not [f for f in g.findings if f.code in {'PROTO-REVIEW-LEVEL','PROTO-REVIEW-WORKSPACE-SCHEMA'}]

def test_schema_error_does_not_dump_customer_examples():
    data=['private '+str(i) for i in range(100)]
    e=next(Draft202012Validator({'type':'array','maxItems':2}).iter_errors(data))
    msg=compact_schema_error(e);assert len(msg)<100 and '100' in msg and 'private' not in msg


def test_contextual_point_view_schema_accepts_real_bindings_and_rejects_invalid_items(tmp_path):
    init_project(tmp_path, 'R0')
    document=json.loads((tmp_path/'review.json').read_text(encoding='utf8'))
    document['presentation']={'renderer':'contextual-v1','contexts':[{'context_ref':'VIEW-X','root_selector':'#x','task':'查看','point_views':[{'ref':'RVP-X'},{'ref':'RVP-Y','source':'4.2'}],'source_sections':['4.2']}], 'sections':{},'diagrams':{}}
    validator=Draft202012Validator(json.loads((ROOT/'schemas/review-workspace.schema.json').read_text(encoding='utf8')))
    Draft202012Validator.check_schema(validator.schema)
    assert not list(validator.iter_errors(document))
    for invalid in (42, {}, {'ref': 1}, {'ref':'RVP-X','source': 7}, {'ref':''}):
        bad=deepcopy(document);bad['presentation']['contexts'][0]['point_views']=[invalid]
        assert any(list(e.path)[:4]==['presentation','contexts',0,'point_views'] for e in validator.iter_errors(bad))


def test_cold_read_optional_targets_and_evidence(tmp_path):
    validator=Draft202012Validator(json.loads((ROOT/'schemas/review-workspace.schema.json').read_text(encoding='utf8')))
    names=('time_limit_seconds','declared_point_recall_min','critical_point_recall')
    for level in ('R0','R1'):
        for mode in ('tabs','contextual'):
            dest=tmp_path/(level+'-'+mode);init_project(dest,level,presentation_mode=mode)
            doc=json.loads((dest/'review.json').read_text(encoding='utf8'));cold=doc['cold_read_contract']
            assert not any(k in cold for k in names)
            assert cold['status']=='pending' and cold['evidence_refs']==[] and cold['participant_roles']
            assert not list(validator.iter_errors(doc))
            old=deepcopy(doc);old['cold_read_contract'].update(time_limit_seconds=180,declared_point_recall_min=.8,critical_point_recall=1)
            assert not list(validator.iter_errors(old))
            for key,value in [('time_limit_seconds',0),('time_limit_seconds',1.5),('declared_point_recall_min',-0.1),('declared_point_recall_min',1.1),('critical_point_recall',-0.1),('critical_point_recall',1.1)]:
                bad=deepcopy(doc);bad['cold_read_contract'][key]=value
                assert any(list(e.path)[:2]==['cold_read_contract',key] for e in validator.iter_errors(bad))
            bad=deepcopy(doc);bad['cold_read_contract'].update(status='passed',evidence_refs=[])
            assert list(validator.iter_errors(bad))
            bad['cold_read_contract']['evidence_refs']=['EVD-COLD']
            assert not list(validator.iter_errors(bad))
