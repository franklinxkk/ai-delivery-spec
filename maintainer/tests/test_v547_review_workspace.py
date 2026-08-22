"""Focused regressions for the v5.4.7 review workspace and repaired gates."""
from __future__ import annotations
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from quality_gate import Gate
REFS = ['REQ-X', 'VIEW-X', 'ACT-X', 'AC-X']
ROLE_SLOTS = {'product': ['purpose', 'scope_and_boundary', 'decision_and_source', 'business_result'], 'frontend': ['entry_and_visibility', 'surface_and_fields', 'interaction_and_ui_states', 'visible_result'], 'backend': ['authority_and_identity', 'input_output_and_validation', 'guards_and_state_effects', 'side_effects_and_audit', 'failure_recovery'], 'qa': ['preconditions_and_fixture', 'positive_and_negative', 'boundary_and_permission', 'visible_and_domain_result', 'evidence']}

def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', check=False)

def manifest(baseline_hash: str) -> dict:
    packets = {role: {'applicability': 'active', 'not_affected_reason': None, 'slot_coverage': slots, 'contract_refs': REFS, 'gap_refs': []} for role, slots in ROLE_SLOTS.items()}
    packets['qa']['scenario_refs'] = ['TEST-X']
    return {'schema_version': '5.4.7', 'workspace_id': 'REVIEW-X', 'language': 'zh-CN', 'baseline': {'version': '1.0', 'hash': baseline_hash, 'requirement_ref': 'prd.md'}, 'layout': {'default_mode': 'orientation', 'default_role': 'product', 'desktop_surface': 'adaptive_canvas_focus', 'compact_surface': 'fullscreen_switcher', 'marker_policy': 'selected_step_only'}, 'roles': ['product', 'frontend', 'backend', 'qa'], 'journeys': [{'journey_id': 'FLOW-X', 'title': '提交闭环', 'goal': '提交一条有效记录并确认领域结果', 'entry_refs': ['VIEW-X'], 'completion_refs': ['AC-X'], 'step_refs': ['STEP-X'], 'model_refs': {'flow_refs': ['FLOW-X'], 'state_machine_refs': ['STM-X'], 'data_flow_refs': ['INT-X'], 'not_applicable': []}}], 'steps': [{'step_id': 'STEP-X', 'dom_anchor': 'review-step-STEP-X', 'title': '提交记录', 'task_kind': 'user_commit', 'accountable_ref': 'ROLE-OP', 'business_status': 'confirmed', 'verification_status': 'not_run', 'source_refs': ['SRC-X', 'REQ-X'], 'evidence_refs': [], 'target_refs': ['VIEW-X', 'ACT-X'], 'outcome_refs': ['STATE-SAVED', 'EVT-SAVED'], 'contract_refs': REFS, 'risk_dimensions': ['boundary', 'permission_or_role', 'failure_or_recovery', 'network_or_concurrency'], 'marker_refs': ['ACT-X'], 'role_packets': packets}], 'edges': [{'edge_id': 'EDGE-START', 'kind': 'start', 'from_step_ref': None, 'to_step_ref': 'STEP-X', 'producer_ref': 'ROLE-OP', 'consumer_ref': 'ENT-SYS', 'payload_refs': ['ENT-REC'], 'entry_refs': ['VIEW-X'], 'postcondition_refs': ['STATE-DRAFT'], 'recovery_refs': [], 'condition_ref': None}, {'edge_id': 'EDGE-FINISH', 'kind': 'finish', 'from_step_ref': 'STEP-X', 'to_step_ref': None, 'producer_ref': 'ENT-SYS', 'consumer_ref': 'ROLE-OP', 'payload_refs': ['EVT-SAVED'], 'entry_refs': ['VIEW-X'], 'postcondition_refs': ['STATE-SAVED'], 'recovery_refs': [], 'condition_ref': None}], 'scenarios': [{'scenario_id': 'TEST-X', 'acceptance_ref': 'AC-X', 'covered_step_refs': ['STEP-X'], 'title': '提交成功与失败恢复', 'source_refs': ['REQ-X'], 'coverage': ['positive', 'negative', 'boundary', 'permission_or_role', 'failure_or_recovery', 'network_or_concurrency', 'visible_and_domain_result', 'evidence']}], 'unknown_refs': [], 'machine_handoff': {'status': 'not_requested', 'manifest_ref': None, 'packet_refs': [], 'gap_refs': []}, 'not_proven': ['静态合同不证明浏览器行为或真实系统验收']}

def review_html(document: dict) -> str:
    buttons = ''.join((f'<button data-action="UIACT-REVIEW-MODE" data-review-mode-target="{mode}">{mode}</button>' for mode in ('orientation', 'journey', 'focus', 'page', 'acceptance')))
    role_buttons = ''.join((f'<button data-action="UIACT-REVIEW-LENS" data-review-role="{role}">{role}</button>' for role in ('product', 'frontend', 'backend', 'qa')))
    packets = document['steps'][0]['role_packets']
    lens_parts = []
    for role, slots in ROLE_SLOTS.items():
        packet = packets[role]
        applicability = packet['applicability']
        if applicability == 'not_affected':
            body = f"<p>{packet['not_affected_reason']}</p>"
        else:
            body = ''.join((f'<section data-review-slot="{slot}">{slot}</section>' for slot in slots))
            body += '<footer>合同引用：' + ' '.join(packet['contract_refs']) + '</footer>'
        lens_parts.append(f'<article data-review-lens="{role}" data-review-applicability="{applicability}">{body}</article>')
    lenses = ''.join(lens_parts)
    marker_refs = document['steps'][0]['marker_refs']
    product_marker = f'<button data-action="UIACT-REVIEW-SELECT" data-review-id="{marker_refs[0]}" aria-current="true">1</button>' if marker_refs else ''
    review_target = f'<button data-action="UIACT-REVIEW-SELECT" data-review-target="{marker_refs[0]}" aria-current="true">1</button>' if marker_refs else '<p>无页面落点</p>'
    handlers = '"UIACT-REVIEW-MODE":()=>1,"UIACT-REVIEW-LENS":()=>1,"UIACT-REVIEW-SELECT":()=>1,"UIACT-REVIEW-COMPACT-VIEW":()=>1'
    models = document['journeys'][0]['model_refs']
    model_surfaces = ''.join((f'<figure data-review-model="{kind}" data-review-model-ref="{ref}">{ref}</figure>' for kind, refs in (('flow', models['flow_refs']), ('state_machine', models['state_machine_refs']), ('data_flow', models['data_flow_refs'])) for ref in refs)) + ''.join((f'<p data-review-model-na="{kind}">{kind} 不适用</p>' for kind in models['not_applicable']))
    scenario_surfaces = ''.join((f'''<article data-review-scenario="{scenario['scenario_id']}" data-review-acceptance-ref="{scenario['acceptance_ref']}">{scenario['scenario_id']}→{scenario['acceptance_ref']} {' '.join(scenario['covered_step_refs'])} {' '.join(scenario['coverage'])}</article>''' for scenario in document['scenarios']))
    step = document['steps'][0]
    status_surfaces = ''.join((f'''<span data-review-status-step="{step['step_id']}" data-review-status-axis="{axis}" data-review-status-value="{step[key]}">{label}：{step[key]}</span>''' for axis, key, label in (('business', 'business_status', '业务状态'), ('verification', 'verification_status', '验证状态'))))
    return f"""<!doctype html><html lang="zh-CN"><body><main data-testid="page-VIEW-X">{product_marker}</main>\n<section data-review-workspace="REVIEW-X" data-review-compact="fullscreen-switcher" data-review-marker-policy="selected-step-only" data-review-active-mode="orientation" data-review-active-role="product">\n<nav data-testid="region-REG-REVIEW-MODES">{buttons}{role_buttons}</nav>\n<section data-review-mode="orientation">导读</section>\n<section data-review-mode="journey" data-review-progress>1/1{model_surfaces}</section>\n<section data-review-mode="focus" data-review-current-step><section data-review-step="STEP-X" data-testid="review-step-STEP-X">{status_surfaces}{review_target}{lenses}</section></section>\n<section data-review-mode="page">页面</section>\n<section data-review-mode="acceptance">{scenario_surfaces}</section>\n<button data-action="UIACT-REVIEW-COMPACT-VIEW" data-review-compact-view="product">查看产品</button>\n</section>\n<script type="application/json" id="review-workspace-manifest">{json.dumps(document, ensure_ascii=False)}</script>\n<script>const reviewHandlers={{{handlers}}};document.addEventListener('click',e=>{{const n=e.target.closest('[data-action]');if(!n)return;const r=document.querySelector('[data-review-workspace]'),id=n.dataset.reviewId||n.dataset.reviewTarget;if(id)document.querySelectorAll('[data-review-id],[data-review-target]').forEach(x=>x.setAttribute('aria-current',(x.dataset.reviewId||x.dataset.reviewTarget)===id?'true':'false'));if(n.dataset.reviewModeTarget)r.setAttribute('data-review-active-mode',n.dataset.reviewModeTarget);if(n.dataset.reviewRole)r.setAttribute('data-review-active-role',n.dataset.reviewRole);reviewHandlers[n.dataset.action]?.()}});</script>\n</body></html>"""

def html_gate(path: Path, raw: str) -> Gate:
    path.write_text(raw, encoding='utf-8')
    gate = Gate()
    gate.check_prototype(path, 'L2')
    return gate

def review_codes(path: Path, document: dict) -> set[str]:
    return {item.code for item in html_gate(path, review_html(document)).findings}

def cli_codes(prototype: Path, *runs: Path) -> tuple[int, set[str]]:
    args = [str(ROOT / 'scripts/ai_delivery_spec_cli.py'), 'gate', '--profile', 'prototype', '--prototype', str(prototype), '--level', 'L2', '--format', 'json']
    for path in runs:
        args.extend(('--acceptance-run', str(path)))
    result = run(*args)
    return (result.returncode, {item['code'] for item in json.loads(result.stdout)['findings']})

def test_complete_workspace_passes_its_deterministic_contract(tmp_path: Path) -> None:
    codes = review_codes(tmp_path / 'review.html', manifest('1' * 64))
    assert not {code for code in codes if code.startswith('PROTO-REVIEW-')}

def test_workspace_rejects_structural_and_presentation_shortcuts(tmp_path: Path) -> None:
    bad = manifest('0' * 64)
    raw = review_html(bad).replace('data-review-compact="fullscreen-switcher"', 'data-review-compact="overlay"').replace('data-review-slot="failure_recovery"', 'data-review-slot="lost"')
    codes = {item.code for item in html_gate(tmp_path / 'bad.html', raw).findings}
    assert {'PROTO-REVIEW-BASELINE-PLACEHOLDER', 'PROTO-REVIEW-COMPACT-OVERLAY', 'PROTO-REVIEW-ROLE-PACKET-INCOMPLETE'} <= codes
    invalid = manifest('1' * 64)
    invalid['scenarios'][0]['coverage'].remove('failure_or_recovery')
    assert 'PROTO-REVIEW-RISK-NOT-TESTED' in review_codes(tmp_path / 'missing-risk.html', invalid)
    detached = review_html(manifest('1' * 64))
    detached = detached.replace('data-review-model-ref="FLOW-X"', 'data-review-model-ref="FLOW-H"', 1)
    detached = detached.replace('data-review-scenario="TEST-X"', 'data-review-scenario="TEST-H"', 1)
    detached = detached.replace('<footer>合同引用：REQ-X VIEW-X ACT-X AC-X</footer>', '<footer>合同引用已隐藏。</footer>', 1)
    detached_codes = {item.code for item in html_gate(tmp_path / 'detached.html', detached).findings}
    assert {'PROTO-REVIEW-MODEL-NOT-VISIBLE', 'PROTO-REVIEW-SCENARIO-NOT-VISIBLE', 'PROTO-REVIEW-CONTRACT-REF-HIDDEN'} <= detached_codes
    status_span = '<span data-review-status-step="STEP-X" data-review-status-axis="verification" data-review-status-value="not_run">验证状态：not_run</span>'
    duplicate = status_span.replace('data-review-status-value="not_run">验证状态：not_run', 'data-review-status-value="accepted">验证状态：accepted') + status_span
    variants = [('', 'PROTO-REVIEW-STATUS-AXIS-HIDDEN'), (status_span.replace('<span ', '<span hidden '), 'PROTO-REVIEW-STATUS-AXIS-HIDDEN'), (status_span.replace('<span ', '<span aria-hidden="true" '), 'PROTO-REVIEW-STATUS-AXIS-HIDDEN'), (status_span.replace('<span ', '<span style="display:none" '), 'PROTO-REVIEW-STATUS-AXIS-HIDDEN'), (f'<div class="is-hidden">{status_span}</div>', 'PROTO-REVIEW-STATUS-AXIS-HIDDEN'), (duplicate, 'PROTO-REVIEW-STATUS-AXIS-DUPLICATE'), (status_span.replace('验证状态：not_run', '验证状态：请查看清单'), 'PROTO-REVIEW-STATUS-AXIS-HIDDEN')]
    base = review_html(manifest('1' * 64))
    for index, (replacement, expected) in enumerate(variants):
        gate = html_gate(tmp_path / f'status-{index}.html', base.replace(status_span, replacement))
        assert expected in {item.code for item in gate.findings}

def test_workspace_allows_explicit_not_affected_roles_and_markerless_system_steps(tmp_path: Path) -> None:
    document = manifest('1' * 64)
    backend = document['steps'][0]['role_packets']['backend']
    backend.update({'applicability': 'not_affected', 'not_affected_reason': '本次仅调整前端静态提示，不改变任何服务端合同。', 'slot_coverage': [], 'contract_refs': [], 'gap_refs': []})
    document['steps'][0]['marker_refs'] = []
    codes = review_codes(tmp_path / 'conditional.html', document)
    assert not {'PROTO-REVIEW-ROLE-PACKET-INCOMPLETE', 'PROTO-REVIEW-NOT-AFFECTED-HAS-CONTRACT', 'PROTO-REVIEW-NOT-AFFECTED-REASON-HIDDEN', 'PROTO-REVIEW-LINKAGE-MISSING'} & codes

def test_workspace_blocks_unproved_confirmation_and_ambiguous_model_coverage(tmp_path: Path) -> None:
    document = manifest('1' * 64)
    document['steps'][0]['source_refs'] = ['REQ-X']
    document['journeys'][0]['model_refs']['state_machine_refs'] = []
    codes = review_codes(tmp_path / 'unproved.html', document)
    assert {'PROTO-REVIEW-CONFIRMED-NO-EVIDENCE', 'PROTO-REVIEW-MODEL-COVERAGE-AMBIGUOUS'} <= codes

def test_workspace_blocks_verification_claim_without_runtime_evidence(tmp_path: Path) -> None:
    document = manifest('1' * 64)
    document['steps'][0]['verification_status'] = 'browser_checked'
    codes = review_codes(tmp_path / 'verification-without-evidence.html', document)
    assert 'PROTO-REVIEW-WORKSPACE-SCHEMA' in codes

def test_workspace_cannot_self_certify_acceptance_with_fake_evidence_id(tmp_path: Path) -> None:
    document = manifest('1' * 64)
    document['steps'][0]['verification_status'] = 'accepted'
    document['steps'][0]['evidence_refs'] = ['EVD-F']
    prototype = tmp_path / 'fake-accepted.html'
    prototype.write_text(review_html(document), encoding='utf-8')
    code, findings = cli_codes(prototype)
    assert code == 2 and 'PROTO-REVIEW-VERIFICATION-ARUN-UNRESOLVED' in findings
    evidence = tmp_path / 'evidence.txt'
    evidence.write_text('browser evidence', encoding='utf-8')
    run_document = {'schema_version': '5.1.0', 'run_id': 'ARUN-U', 'baseline_version': '1.0', 'environment': 'Chrome browser', 'executor': 'QA', 'executed_at': '2026-08-20T00:00:00Z', 'evidence_catalog': [{'id': 'EVD-U', 'uri': evidence.name}], 'items': [{'id': 'ARITEM-U', 'acceptance_ref': 'AC-O', 'requirement_refs': ['REQ-O'], 'mandatory': True, 'result': 'pass', 'actual_result': 'unrelated flow passed', 'evidence_refs': ['EVD-U'], 'defect_refs': []}], 'conclusion': 'accepted', 'sign_offs': [{'role': '验收人', 'actor': 'QA', 'decision': 'approve', 'at': '2026-08-20T00:00:00Z', 'evidence_ref': 'EVD-U'}]}
    acceptance_run = tmp_path / 'unrelated-arun.yaml'
    acceptance_run.write_text(json.dumps(run_document, ensure_ascii=False), encoding='utf-8')
    document['steps'][0]['evidence_refs'] = ['ARUN-U']
    prototype.write_text(review_html(document), encoding='utf-8')
    code, findings = cli_codes(prototype, acceptance_run)
    assert code == 2 and 'PROTO-REVIEW-VERIFICATION-AC-UNPROVED' in findings
    pending_run = copy.deepcopy(run_document)
    pending_run.update({'run_id': 'ARUN-P', 'conclusion': 'pending', 'sign_offs': []})
    pending_run['items'][0].update({'id': 'ARITEM-P', 'acceptance_ref': 'AC-X', 'requirement_refs': ['REQ-X'], 'actual_result': 'browser-only core flow passed'})
    pending_path = tmp_path / 'pending-core-arun.yaml'
    pending_path.write_text(json.dumps(pending_run, ensure_ascii=False), encoding='utf-8')
    document['steps'][0].update({'verification_status': 'integration_checked', 'evidence_refs': ['ARUN-P']})
    prototype.write_text(review_html(document), encoding='utf-8')
    assert 'PROTO-REVIEW-VERIFICATION-LEVEL-UNPROVED' in cli_codes(prototype, pending_path)[1]
    document['steps'][0].update({'verification_status': 'accepted', 'evidence_refs': ['ARUN-U', 'ARUN-P']})
    prototype.write_text(review_html(document), encoding='utf-8')
    assert 'PROTO-REVIEW-VERIFICATION-LEVEL-UNPROVED' in cli_codes(prototype, acceptance_run, pending_path)[1]

def test_workspace_blocks_declared_language_drift_without_keyword_policing(tmp_path: Path) -> None:
    document = manifest('1' * 64)
    document['language'] = 'en-US'
    codes = review_codes(tmp_path / 'language-drift.html', document)
    assert 'PROTO-REVIEW-LANGUAGE-MISMATCH' in codes

def test_legacy_overlay_is_gap_for_visual_review_but_blocked_for_handoff(tmp_path: Path) -> None:
    old = tmp_path / 'old.html'
    old.write_text('<body class="review-mode"><main data-testid="page-VIEW-OLD-001"><button data-action="UIACT-REVIEW-SELECT" data-review-id="R1" aria-current="true">1</button><aside data-review-id="R1" aria-current="true">说明</aside><script>const reviewHandlers={"UIACT-REVIEW-SELECT":()=>true};document.addEventListener("click",e=>{const reviewId=e.target.dataset.reviewId;if(reviewId)document.querySelectorAll("[data-review-id]").forEach(n=>n.setAttribute("aria-current","true"));});</script></main></body>', encoding='utf-8')
    prd = tmp_path / 'prd.md'
    prd.write_text('# 基线\n\nREQ-OLD-001 / VIEW-OLD-001 / AC-OLD-001\n', encoding='utf-8')
    gate = Gate()
    gate.check_prototype(old, 'L2')
    assert any((item.code == 'PROTO-REVIEW-WORKSPACE-LEGACY' and item.severity == 'GAP' for item in gate.findings))
    gate.check_handoff(prd, [old], 'L2')
    assert any((item.code == 'PROTO-REVIEW-WORKSPACE-REQUIRED' and item.severity == 'BLOCK' for item in gate.findings))

def test_review_workspace_hash_must_match_supplied_prd(tmp_path: Path) -> None:
    prd = tmp_path / 'prd.md'
    prd.write_text('# 基线\n\nREQ-X / VIEW-X / AC-X\n', encoding='utf-8')
    html = tmp_path / 'review.html'
    document = manifest('2' * 64)
    gate = html_gate(html, review_html(document))
    gate.check_handoff(prd, [html], 'L2')
    assert any((item.code == 'PROTO-REVIEW-BASELINE-DRIFT' for item in gate.findings))
    document['baseline']['hash'] = hashlib.sha256(prd.read_text(encoding='utf-8').encode()).hexdigest()
    gate = html_gate(html, review_html(document))
    gate.check_handoff(prd, [html], 'L2')
    assert not any((item.code == 'PROTO-REVIEW-BASELINE-DRIFT' for item in gate.findings))

def test_review_workspace_handoff_indicator_matches_the_real_manifest(tmp_path: Path) -> None:
    baseline_hash = '3' * 64
    handoff = tmp_path / 'handoff.yaml'
    handoff.write_text(f"schema_version: 5.3.0\nstatus: ready_for_implementation\nbaseline:\n  version: '1.0'\n  hash: {baseline_hash}\n  requirement_ref: prd.md\npackets:\n  - id: MOD-X\n    kind: mod\n    owner: team\n    path: packets/core.md\n    baseline_hash: {baseline_hash}\n    scope_refs: [REQ-X]\n    acceptance_refs: [AC-X]\nhandoffs: []\n", encoding='utf-8')
    document = manifest(baseline_hash)
    document['machine_handoff'] = {'status': 'ready', 'manifest_ref': 'handoff.yaml', 'packet_refs': ['MOD-X'], 'gap_refs': []}
    html = tmp_path / 'review.html'
    gate = html_gate(html, review_html(document))
    gate.check_review_manifest_binding(handoff)
    assert not {item.code for item in gate.findings if item.code.startswith('PROTO-REVIEW-HANDOFF-')}
    document['machine_handoff'] = {'status': 'not_requested', 'manifest_ref': None, 'packet_refs': [], 'gap_refs': []}
    gate = html_gate(html, review_html(document))
    gate.check_review_manifest_binding(handoff)
    assert any((item.code == 'PROTO-REVIEW-HANDOFF-STATUS-DRIFT' for item in gate.findings))

def test_repaired_cli_and_query_surfaces_are_truthful() -> None:
    candidate = run('scripts/ai_delivery_spec_cli.py', 'candidate', '--help')
    assert candidate.returncode == 0 and 'validate' in candidate.stdout and ('校验本地候选' in candidate.stdout)
    section = run('scripts/query_domain.py', '--domain', 'crm', '--section', 'Domain Events', '--format', 'markdown')
    assert section.returncode == 0 and 'Domain Events' in section.stdout and ('Compact context' not in section.stdout)

def test_prototype_cannot_label_one_value_confirmed_and_unknown(tmp_path: Path) -> None:
    path = tmp_path / 'conflict.html'
    path.write_text('<main data-testid="page-VIEW-METRIC-001"><div data-metric="METRIC-RATE-001" data-metric-status="confirmed" data-unk="UNK-RATE-001" data-unk-priority="P1" data-unk-owner="产品负责人" data-unk-blocks-stage="baseline" data-unk-affected-refs="METRIC-RATE-001" data-unk-fallback="不展示该指标">完成率</div></main>', encoding='utf-8')
    gate = html_gate(path, path.read_text(encoding='utf-8'))
    assert any((item.code == 'PROTO-UNKNOWN-CONFIRMED-CONFLICT' for item in gate.findings))

def test_stage0_and_l1_skeletons_cannot_pass_as_content(tmp_path: Path) -> None:
    stage0 = ROOT / 'references/templates/stage0-inventory-template.yaml'
    gate = Gate()
    gate.check_stage0(stage0)
    assert any((item.code == 'STAGE0-PLACEHOLDER' and item.severity == 'BLOCK' for item in gate.findings))
    prd = tmp_path / 'l1.md'
    prd.write_text('---\ndocument_language: zh-CN\ndelivery_level: L1\nactivated_facets: ui\n---\n# 需求卡\n## 来源、问题与价值\n来源与价值已确认。\n## 目标、范围与非目标\n提交单条记录，不做批量。\n## 角色、用户故事与权限\n业务员提交，管理员查看。\n## 旅程、流程、异常与状态\n失败保留输入，成功可见。\n## 验收与测试\n校验成功和拒绝路径。\n## 未知项与升级判断\n无开放未知项。\n', encoding='utf-8')
    gate = Gate()
    gate.check_prd(prd, 'L1')
    codes = {item.code for item in gate.findings}
    assert 'PRD-L1-SECTION-MISSING' in codes and 'PRD-BAD-ACTIVATED-FACETS' in codes
    governed = tmp_path / 'l1-data-submission.md'
    governed.write_text(prd.read_text(encoding='utf-8').replace('activated_facets: ui', 'activated_facets: [data_submission]').replace('## 验收与测试', '## 规则、字段与条件规格\n映射、校验、状态、审计、计算、对账与更正。\n## 验收与测试'), encoding='utf-8')
    gate = Gate()
    gate.check_prd(governed, 'L1')
    assert 'PRD-FACET-REQUIRES-L2' in {item.code for item in gate.findings}
