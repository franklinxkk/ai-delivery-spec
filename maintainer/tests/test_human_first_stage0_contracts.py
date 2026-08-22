"""Capability regressions for Human-First, brownfield and Stage 0 contracts."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts' / 'validators'))
from quality_gate import Gate
from scan_prototype_css import scan
from prd_structure import _section_bodies
STAGE0_SCHEMA = json.loads((ROOT / 'schemas/stage0-inventory.schema.json').read_text(encoding='utf-8'))

def codes(gate: Gate) -> set[str]:
    return {item.code for item in gate.findings}

class MemoryGate(Gate):

    def __init__(self, documents: dict[str, str]):
        super().__init__()
        self.documents = {str(Path(name)): value for name, value in documents.items()}

    def read(self, path: Path) -> str:
        return self.documents[str(path)]

def test_h2_uses_full_h3_subtree() -> None:
    raw = '## 4. 端到端角色旅程\n### 4.1 企业旅程 FLOW-DEMO-001\nROLE-USER 提交后成功；失败时恢复。\n## 5. 业务流程与状态\n正文。'
    sections = dict(_section_bodies(raw))
    assert 'ROLE-USER' in sections['4. 端到端角色旅程']
    assert 'FLOW-DEMO-001' in sections['4. 端到端角色旅程']

def test_todo_inside_stable_id_is_not_unknown_marker() -> None:
    gate = Gate()
    raw = '---\nopen_p0_unknown_ids: []\n---\n## 模块\nREG-RPT-TODO 是待办区域。'
    gate._check_unknowns(Path('prd.md'), raw, gate._frontmatter(raw), stage='specify', scope_refs=set())
    assert 'PRD-UNTRACKED-UNKNOWN' not in codes(gate)

def test_uiact_is_allowed_without_business_ac() -> None:
    path = Path('prototype.html')
    raw = '<style>.btn{border:1px solid;padding:8px}.hidden{display:none!important}</style>\n<main data-testid="page-VIEW-DEMO-001" data-state="default"><section data-testid="region-REG-DEMO-001"><button class="btn" data-action="UIACT-TAB-NEXT">下一页</button><button class="btn" data-action="ACT-DEMO-SAVE" data-ac="AC-DEMO-001">保存</button></section></main><script>document.addEventListener(\'click\',e=>{const n=e.target.closest(\'[data-action]\');if(!n)return;switch(n.dataset.action){case\'UIACT-TAB-NEXT\':document.body.dataset.state=\'next\';break;case\'ACT-DEMO-SAVE\':document.body.dataset.state=\'saved\'}})</script>'
    gate = MemoryGate({str(path): raw})
    gate.check_prototype(path, 'L3')
    found = codes(gate)
    assert 'PROTO-UNSTABLE-ACTION' not in found
    assert 'PROTO-ACTION-NO-AC' not in found
    assert 'PROTO-UNHANDLED-ACTION' not in found

def test_binding_terms_are_checked_across_handoff() -> None:
    prd = Path('PRD.md')
    prototype = Path('prototype.html')
    prd_raw = '---\npage_contract_view_ids: [VIEW-DEMO-001]\nbinding_terms: [道路运输经营许可证]\n---\nREQ-DEMO-001 ACT-DEMO-001 AC-DEMO-001\n- id: AC-DEMO-001'
    prototype_raw = '<section data-testid="page-VIEW-DEMO-001">行业经营许可</section>'
    gate = MemoryGate({str(prd): prd_raw, str(prototype): prototype_raw})
    gate.check_handoff(prd, [prototype], 'L2')
    assert 'HANDOFF-BINDING-TERM-MISSING' in codes(gate)

def test_demo_and_local_iframe_are_blocked() -> None:
    path = Path('prototype.html')
    raw = '<section data-testid="page-VIEW-DEMO-001">验收场景<iframe src="child.html"></iframe></section>'
    gate = MemoryGate({str(path): raw})
    gate.check_prototype(path, 'L2')
    found = codes(gate)
    assert 'PROTO-DEMO-SCAFFOLDING-VISIBLE' in found
    assert 'PROTO-NESTED-PRODUCT-IFRAME' in found

def test_css_scans_unstyled_controls_and_tiny_primary_text() -> None:
    findings = scan('<style>.primary-btn{color:#fff}button{font-size:9px}</style><button class="btn primary">保存</button>')
    kinds = {item['kind'] for item in findings}
    assert 'unstyled-control-class' in kinds
    assert 'unreadable-type-scale' in kinds

def test_state_columns_reject_api_ids() -> None:
    gate = Gate()
    raw = 'REQ-DEMO-001 AC-DEMO-001\n| 当前状态 | 动作 | 下一状态 |\n|---|---|---|\n| 待处理 | 复检 | API-RISK-RECHECK 复检 |\n'
    gate._check_testability(Path('PRD.md'), raw, {}, 'L2')
    assert 'PRD-STATE-SEMANTIC-POLLUTION' in codes(gate)

def stage0_chain_document() -> dict:
    document = yaml.safe_load((ROOT / 'references/templates/stage0-inventory-template.yaml').read_text(encoding='utf-8'))
    document.update({'inventory_id': 'INV-STAGE0-CHAIN-001', 'inventory_status': 'inventory_complete', 'target_status': 'draft', 'review_batches': [], 'reachability_breaks': []})
    document['items'] = document['items'][:7]
    for item in document['items']:
        item['classification'] = 'confirmed'
        item.pop('review_batch_ref', None)
        item.pop('unknown', None)
    chain = document['critical_chains'][0]
    link = chain['links'][0]
    link.update({'next_entry': {'status': 'observed', 'refs': ['INV-VIEW-ORDER-LIST']}, 'next_guard': {'status': 'observed', 'refs': ['INV-GUARD-ORDER-EXPORT']}, 'reachability': 'reachable', 'break_refs': []})
    chain['break_refs'] = []
    return document

def gate_stage0(document: dict) -> Gate:
    path = Path('stage0.yaml')
    gate = MemoryGate({str(path): yaml.safe_dump(document, allow_unicode=True, sort_keys=False)})
    gate.check_stage0(path)
    return gate

def test_stage0_declared_reachable_chain_can_pass_with_empty_break_register() -> None:
    document = stage0_chain_document()
    Draft202012Validator.check_schema(STAGE0_SCHEMA)
    assert not list(Draft202012Validator(STAGE0_SCHEMA).iter_errors(document))
    gate = gate_stage0(document)
    assert not [item for item in gate.findings if item.severity in {'BLOCK', 'GAP', 'P0_UNKNOWN'}]
    assert gate.metrics['stage0_critical_chains'] == 1
    assert gate.metrics['stage0_reachability_breaks'] == 0

def test_stage0_legacy_inventory_gets_gap_without_forced_chain() -> None:
    document = stage0_chain_document()
    document.pop('critical_chains')
    document.pop('reachability_breaks')
    gate = gate_stage0(document)
    found = {(item.severity, item.code) for item in gate.findings}
    assert ('GAP', 'STAGE0-REACHABILITY-NOT-DECLARED') in found
    assert not [item for item in gate.findings if item.severity == 'BLOCK']

def test_stage0_informational_inventory_is_not_forced_to_declare_chain() -> None:
    document = stage0_chain_document()
    document.pop('critical_chains')
    document.pop('reachability_breaks')
    for row in document['items']:
        row.pop('core_behavior', None)
    gate = gate_stage0(document)
    assert 'STAGE0-REACHABILITY-NOT-DECLARED' not in codes(gate)
    assert not [item for item in gate.findings if item.severity in {'BLOCK', 'GAP'}]

def test_stage0_broken_chain_cannot_hide_behind_empty_break_register() -> None:
    document = stage0_chain_document()
    link = document['critical_chains'][0]['links'][0]
    link['next_entry'] = {'status': 'missing', 'refs': [], 'note': '未观察到下一入口'}
    link['next_guard'] = {'status': 'unknown', 'refs': [], 'note': '下一守卫无法确认'}
    link['reachability'] = 'broken'
    gate = gate_stage0(document)
    found = codes(gate)
    assert 'STAGE0-CHAIN-UNRESOLVED-UNTRACKED' in found
    assert 'STAGE0-EMPTY-BREAK-REGISTER' in found

def test_stage0_owned_unknown_break_is_inventory_not_invented_rule() -> None:
    document = stage0_chain_document()
    chain = document['critical_chains'][0]
    link = chain['links'][0]
    link['next_entry'] = {'status': 'unknown', 'refs': [], 'note': '源中无法确认下一入口'}
    link['next_guard'] = {'status': 'unknown', 'refs': [], 'note': '源中无法确认下一守卫'}
    link['reachability'] = 'unknown'
    link['break_refs'] = ['INV-BREAK-NEXT-ENTRY']
    chain['break_refs'] = ['INV-BREAK-NEXT-ENTRY']
    document['reachability_breaks'] = [{'id': 'INV-BREAK-NEXT-ENTRY', 'chain_ref': chain['id'], 'link_ref': link['id'], 'path_kind': 'next_entry', 'classification': 'unknown', 'source_ref': link['source_ref'], 'source_location': link['source_location'], 'description': '输出对象无法到达已观察到的下一入口及守卫', 'unknown': {'id': 'UNK-NEXT-ENTRY', 'priority': 'P0', 'owner': '产品负责人', 'blocks_stage': 'baseline'}}]
    assert not list(Draft202012Validator(STAGE0_SCHEMA).iter_errors(document))
    gate = gate_stage0(document)
    assert not [item for item in gate.findings if item.severity in {'BLOCK', 'GAP'}]
    assert gate.metrics['stage0_reachability_unresolved'] == 1

def test_stage0_reachable_rejects_state_entry_and_object_guard() -> None:
    document = stage0_chain_document()
    link = document['critical_chains'][0]['links'][0]
    link['next_entry'] = {'status': 'observed', 'refs': ['INV-STATE-EXPORT-READY']}
    link['next_guard'] = {'status': 'observed', 'refs': ['INV-OBJ-EXPORT-FILE']}
    gate = gate_stage0(document)
    mismatches = [item for item in gate.findings if item.code == 'STAGE0-CHAIN-REF-TYPE-MISMATCH']
    assert len(mismatches) >= 2
    assert any(('next_entry.refs' in item.ref for item in mismatches))
    assert any(('next_guard.refs' in item.ref for item in mismatches))

def test_stage0_reachable_accepts_handoff_entry_and_rule_guard() -> None:
    document = stage0_chain_document()
    document['items'].extend([{'id': 'INV-HANDOFF-FINANCE', 'type': 'handoff', 'source_ref': 'SRC-LEGACY-001', 'source_location': 'legacy.html#finance-handoff', 'classification': 'confirmed'}, {'id': 'INV-RULE-PENDING-ONLY', 'type': 'rule', 'source_ref': 'SRC-LEGACY-001', 'source_location': 'legacy.html#pending-only', 'classification': 'confirmed'}])
    link = document['critical_chains'][0]['links'][0]
    link['next_entry'] = {'status': 'observed', 'refs': ['INV-HANDOFF-FINANCE']}
    link['next_guard'] = {'status': 'observed', 'refs': ['INV-RULE-PENDING-ONLY']}
    gate = gate_stage0(document)
    assert 'STAGE0-CHAIN-REF-TYPE-MISMATCH' not in codes(gate)
    assert not [item for item in gate.findings if item.severity in {'BLOCK', 'GAP'}]

def test_stage0_unknown_entry_type_cannot_prove_reachable() -> None:
    document = stage0_chain_document()
    document['items'].append({'id': 'INV-ENTRY-UNKNOWN-KIND', 'type': 'teleport', 'source_ref': 'SRC-LEGACY-001', 'source_location': 'legacy.html#unknown-entry', 'classification': 'confirmed'})
    document['critical_chains'][0]['links'][0]['next_entry'] = {'status': 'observed', 'refs': ['INV-ENTRY-UNKNOWN-KIND']}
    gate = gate_stage0(document)
    assert 'STAGE0-CHAIN-REF-TYPE-MISMATCH' in codes(gate)

def test_stage0_declared_chain_requires_all_recovery_dimensions() -> None:
    document = stage0_chain_document()
    del document['critical_chains'][0]['recovery_paths']['retry']
    gate = gate_stage0(document)
    assert 'STAGE0-RECOVERY-CONTRACT-INCOMPLETE' in codes(gate)
if __name__ == '__main__':
    tests = [value for name, value in sorted(globals().items()) if name.startswith('test_')]
    for test in tests:
        test()
    print(f'PASS: {len(tests)} Human-First and Stage 0 contract regressions')
