"""Small synthetic equipment example; no project authorization policy is embedded."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,json,sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from validators.contextual_review import check_contextual,digest
from validators.contextual_review import check_document_sections
from build_review_workspace import init_project,build_project
from quality_gate import Gate

def test_runtime_actions_do_not_leak_to_another_file(tmp_path):
 p=tmp_path/'second.html';p.write_text('<main data-testid="page-VIEW-EQUIPMENT"></main><script>const actions={"ACT-SAVE":function(){return 1}};</script>')
 g=Gate();g.runtime_verified_actions={'ACT-SAVE'};g.check_prototype(p,'L2')
 assert g.runtime_verified_actions==set()
 assert any(f.code=='PROTO-ORPHAN-HANDLER' and f.ref=='ACT-SAVE' for f in g.findings)

def test_contextual_initializer_changes_actual_layout(tmp_path):
 init_project(tmp_path,'R0',presentation_mode='contextual');build_project(tmp_path)
 raw=(tmp_path/'prototype.html').read_text(encoding='utf8')
 assert 'data-review-tab-target=' not in raw and 'contextual-diagram-viewer' in raw
 assert 'body class="ads-collapsed"' in raw
 assert json.loads((tmp_path/'review.json').read_text())['workspace']['presentation_mode']=='contextual'

def test_metadata_alone_cannot_convert_tabs(tmp_path):
 init_project(tmp_path);p=tmp_path/'review.json';d=json.loads(p.read_text());d['workspace']['presentation_mode']='contextual';p.write_text(json.dumps(d))
 with pytest.raises(ValueError,match='contextual'):build_project(tmp_path)

def fixture(tmp_path):
 p=tmp_path/'prototype.html';p.write_text('<aside data-review-renderer="contextual-v1"></aside>')
 doc={'workspace':{'review_level':'R0'},'review_contexts':[{'context_ref':'VIEW-EQUIPMENT','context_type':'VIEW','review_point_refs':['RVP-SAVE']}],
 'review_points':[{'ref':'RVP-SAVE','owner_context_ref':'VIEW-EQUIPMENT','summary':'保存设备名称','source_refs':['REQ-EQUIPMENT'],'marker_required':True,'target_selector':'#save','target_ref':'save','implementation_detail':{'required':True}}],
 'semantic_coverage_items':[{'coverage_id':'SC-SAVE','owner_context_ref':'VIEW-EQUIPMENT','review_point_refs':['RVP-SAVE']}],
 'acceptance_examples':[{'example_ref':'TEST-SAVE','owner_context_ref':'VIEW-EQUIPMENT','precondition':'设备名称为空','action':'点击保存','expected_visible_result':'提示必填','expected_domain_result':'不创建记录'}],
 'diagram_contract':{'diagrams':[{'diagram_ref':'DIAG-SAVE'}]},'presentation':{'contexts':[{'context_ref':'VIEW-EQUIPMENT','root_selector':'#equipment','task':'登记设备','point_views':[{'ref':'RVP-SAVE'}],'source_sections':['1'],'diagram_ref':'DIAG-SAVE'}],'sections':{'1':{}},'diagrams':{'DIAG-SAVE':{'src':'data:image/svg+xml,x','title':'设备登记流程'}}}}
 obs={'context_ref':'VIEW-EQUIPMENT','current_context':'VIEW-EQUIPMENT','detected_context':'VIEW-EQUIPMENT','capture_method':'browser_ui','trigger':'点击登记设备','panel_visible':True,'product_root_visible':True,'fingerprint_before':'abc','fingerprint_after':'abc','cards':[{'ref':'RVP-SAVE','visible':True,'text':'保存设备名称','implementation_visible':True,'target':{'count':1}}],'examples':[{'ref':'TEST-SAVE','visible':True,'text':'设备名称为空 点击保存 提示必填 不创建记录'}],'diagrams':[{'ref':'DIAG-SAVE','thumbnail_visible':True,'image_loaded':True,'viewer_opened':True}],'return_preserves_context':True,'visible_actions':['ACT-SAVE']}
 e={'schema_version':1,'prototype_sha256':digest(p),'manifest_sha256':hashlib.sha256(json.dumps(doc,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),'observations':[obs]}
 return p,doc,e

def run(p,d,e):
 findings=[];g=SimpleNamespace(metrics={},add=lambda *a,**k:findings.append(a))
 if e is not None:
  ep=p.with_suffix('.evidence.json');ep.write_text(json.dumps(e));g.review_runtime_evidence=ep
 check_contextual(g,p,p.read_text(),d);return findings,g

def test_valid_observation_and_dynamic_entry(tmp_path):
 p,d,e=fixture(tmp_path);f,g=run(p,d,e);assert not f;assert g.runtime_verified_actions=={'ACT-SAVE'}

def test_no_evidence_is_unverified_not_visible(tmp_path):
 p,d,e=fixture(tmp_path);f,g=run(p,d,None);assert any(x[0]=='GAP' and 'UNVERIFIED' in x[1] for x in f);assert not hasattr(g,'runtime_verified_actions')

@pytest.mark.parametrize('fault,code',[('example','EXAMPLE'),('diagram','DIAGRAM'),('target','TARGET'),('implementation','IMPLEMENTATION'),('side_effect','SIDE-EFFECT'),('stale','EVIDENCE-DRIFT'),('summary','POINT-CONTENT')])
def test_observed_defects_stay_blocked(tmp_path,fault,code):
 p,d,e=fixture(tmp_path);o=e['observations'][0]
 if fault=='example':o['examples']=[]
 elif fault=='diagram':o['diagrams'][0]['image_loaded']=False
 elif fault=='target':o['cards'][0]['target']['count']=2
 elif fault=='implementation':o['cards'][0]['implementation_visible']=False
 elif fault=='side_effect':o['fingerprint_after']='changed'
 elif fault=='stale':p.write_text('changed file')
 elif fault=='summary':o['cards'][0]['text']='unrelated explanation'
 f,g=run(p,d,e);assert any(x[0]=='BLOCK' and x[1].endswith(code) for x in f)
 if fault=='stale':assert not hasattr(g,'runtime_verified_actions')

@pytest.mark.parametrize('fault',[None,'changed_body','bad_source','ready','r1'])
def test_document_provenance_not_machine_handoff(tmp_path,fault):
 p,d,e=fixture(tmp_path);d['presentation']['sections']={'1':{'title':'1 设备登记','blocks':[{'text':'设备名称为必填。'}]}};d['review_points'][0]['source_refs']=['REQ-1'];d['presentation']['contexts'][0]['point_views'][0]['source']='1';d['semantic_coverage_items'][0]['source_refs']=['REQ-1']
 if fault=='changed_body':d['presentation']['sections']['1']['blocks'][0]['text']='名称可以不填。'
 if fault=='bad_source':d['review_points'][0]['source_refs']=['REQ-OTHER']
 if fault=='ready':d['machine_handoff']={'status':'ready'}
 if fault=='r1':d['workspace']['review_level']='R1'
 findings=[];g=SimpleNamespace(metrics={},add=lambda *a,**k:findings.append(a));check_document_sections(g,p,'## [REQ-1] 1 设备登记\n设备名称为必填。\n',d)
 assert bool([f for f in findings if f[0]=='BLOCK'])==bool(fault)
 if not fault:assert 'structured ID handoff not claimed' in g.metrics['handoff_scope']
