"""Explicit handoff references resolve; this does not judge business truth."""
import hashlib
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from quality_gate import Gate

BODY = '''## REQ-REPORT 提交登记
发布员提交；审核员只读。正式登记号才算成功。
| ID | 验收 |
|---|---|
| AC-REPORT-ONE | 响应丢失查原请求，只有一份登记 |
| AC-REPORT-TWO | 审核员提交无外部调用 |
'''

def run(tmp_path, body=BODY, packet=None, refs=None):
    digest = hashlib.sha256(body.encode()).hexdigest()
    (tmp_path/'prd.md').write_text(body, 'utf-8')
    (tmp_path/'engineering.md').write_text('Local pure-function adapter; no production calls.', 'utf-8')
    packet = packet if packet is not None else '# MOD-REPORT\n' + body
    (tmp_path/'packet.md').write_text(packet, 'utf-8')
    doc = {'schema_version':'5.3.0','status':'ready_for_implementation',
           'engineering_baseline_ref':'engineering.md',
           'baseline':{'version':'1','hash':digest,'requirement_ref':'prd.md'},
           'packets':[{'id':'MOD-REPORT','kind':'mod','owner':'test','path':'packet.md',
                       'baseline_hash':digest,'content_sha256':hashlib.sha256(packet.encode()).hexdigest(),
                       'scope_refs':['REQ-REPORT'],'acceptance_refs':refs or ['AC-REPORT-ONE','AC-REPORT-TWO']}],
           'handoffs':[]}
    p=tmp_path/'handoff.yaml';p.write_text(yaml.safe_dump(doc), 'utf-8')
    gate=Gate();gate.check_agent_handoff(p)
    return {f.code for f in gate.findings}

def test_declared_references_exist_in_baseline_and_packet(tmp_path):
    codes=run(tmp_path)
    assert not {'HANDOFF-PACKET-AC-MISSING','HANDOFF-REF-NOT-IN-PRD'} & codes

def test_one_valid_ac_does_not_hide_another_missing_ac(tmp_path):
    codes=run(tmp_path,packet='# MOD-REPORT\nREQ-REPORT\nAC-REPORT-ONE')
    assert 'HANDOFF-PACKET-AC-MISSING' in codes

def test_refs_only_in_packet_are_not_authoritative_definitions(tmp_path):
    codes=run(tmp_path,body='## 目标\n提交登记。',packet='# MOD-REPORT\nREQ-REPORT\nAC-REPORT-ONE\nAC-REPORT-TWO')
    assert 'HANDOFF-REF-NOT-IN-PRD' in codes

def test_reference_prefix_is_not_a_reference_match(tmp_path):
    codes=run(tmp_path,packet='# MOD-REPORT\nREQ-REPORT\nAC-REPORT-ONE-EXTRA\nAC-REPORT-TWO')
    assert 'HANDOFF-PACKET-AC-MISSING' in codes

def test_matching_definitions_do_not_claim_semantic_validation(tmp_path):
    codes=run(tmp_path,body=BODY.replace('审核员只读','审核员可以提交').replace('审核员提交无外部调用','审核员提交成功'))
    assert 'HANDOFF-REF-NOT-IN-PRD' not in codes
