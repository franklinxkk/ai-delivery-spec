"""Capability suite: lifecycle convergence, atomic checkpoints, isolation, and clarification."""
from __future__ import annotations
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[2]
MANAGER = ROOT / 'scripts/manage_execution_state.py'
COMPILER = ROOT / 'scripts/compile_clarification_transcript.py'
CAPSULE_VALIDATOR = ROOT / 'scripts/validators/validate_capsule_composition.py'
CLI = ROOT / 'scripts/ai_delivery_spec_cli.py'
TRUTH = ROOT / 'maintainer/examples/publishing-learning-v5/delivery/truth/product-truth.yaml'
CONFIG = ROOT / 'examples/spec.config.example.yaml'
sys.path.insert(0, str(ROOT / 'scripts'))
from plan_context import build_plan
from query_product_truth import make_slice
from ai_delivery_spec_cli import validate_runtime_manifest

def run(script: Path, *args: str, expected: int=0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([sys.executable, str(script), *args], cwd=ROOT, text=True, encoding='utf-8', errors='replace', capture_output=True)
    if result.returncode != expected:
        raise AssertionError(result.stdout + result.stderr)
    return result

def test_context_plan_scales_without_silent_loss() -> None:
    truth = yaml.safe_load(TRUTH.read_text(encoding='utf-8'))
    config = yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
    standard = build_plan(truth, config, ['MOD-CONTENT-001'])
    assert standard['profile'] != 'minimal'
    assert not standard['overflow']['silent_truncation_allowed']
    assert 'maturity' not in standard and 'domain_maturity' not in standard
    micro_truth = copy.deepcopy(truth)
    micro_truth['delivery_context'].update({'tier': 'L1', 'delivery_mode': 'lite', 'project_shape': 'greenfield', 'governance_profiles': [], 'domain_packs': []})
    for collection in ('roles', 'modules', 'flows', 'actions', 'integrations', 'unknowns', 'conflicts'):
        micro_truth[collection] = micro_truth.get(collection, [])[:1]
    micro_truth['fields'] = []
    micro_truth['sources'] = micro_truth['sources'][:1]
    micro = build_plan(micro_truth, config, [])
    assert micro['profile'] == 'minimal'
    assert len(micro['selection']['stage_references']) <= 1
    regulated_truth = copy.deepcopy(truth)
    regulated_truth['delivery_context'].update({'tier': 'L3', 'governance_profiles': ['regulated', 'multi-tenant']})
    regulated_truth['sources'].append({'id': 'SRC-REGULATION-TEST', 'kind': 'regulation', 'title': 'Test source', 'authority': 'primary', 'status': 'active', 'disposition': 'authoritative_annex'})
    downgrade = copy.deepcopy(config)
    downgrade['context'].update({'profile': 'minimal', 'max_stage_references': 0, 'max_domain_packs': 0})
    downgrade['assurance']['manual_profile'] = 'minimal'
    protected = build_plan(regulated_truth, downgrade, [])
    assert protected['profile'] == 'regulated' and protected['assurance_profile'] == 'regulated'
    assert 'human_accountability' in protected['required_gates']
    assert protected['overflow']['triggered'] and protected['selection']['deferred_stage_references']
    stress = copy.deepcopy(config)
    stress['context'].update({'model_context_tokens': 4096, 'system_overhead_tokens': 512, 'reserved_output_tokens': 512, 'warn_at_ratio': 0.8, 'overflow_strategy': 'summarize'})
    pressured = build_plan(truth, stress, [])
    assert pressured['overflow']['triggered']
    assert pressured['overflow']['required_action'] == 'write_compaction_manifest'
    assert 'P0' in pressured['overflow']['preserved_priorities']
    sliced = make_slice(truth, ['MOD-CONTENT-001'], include_reverse=False)
    slice_ids = {item['id'] for items in sliced['items'].values() for item in items if isinstance(item, dict) and item.get('id')}
    assert {'MOD-CONTENT-001', 'FLOW-PUBLISH-001'} <= slice_ids

def test_legacy_delivery_init_preserves_local_config() -> None:
    with tempfile.TemporaryDirectory(prefix='ads-init-', dir=ROOT) as temp:
        target = Path(temp) / 'delivery'
        run(CLI, 'init-delivery', '--output', str(target), '--truth-layout', 'progressive')
        required = ('spec.config.yaml', 'manifest.json', 'truth/index.yaml', 'truth/fragments/00-core.yaml', 'truth/fragments/MOD-EXAMPLE.yaml', 'evidence')
        assert all(((target / path).exists() for path in required))
        config_path = target / 'spec.config.yaml'
        local = yaml.safe_load(config_path.read_text(encoding='utf-8'))
        local['context']['profile'] = 'minimal'
        config_path.write_text(yaml.safe_dump(local, sort_keys=False), encoding='utf-8')
        run(CLI, 'init-delivery', '--output', str(target), '--truth-layout', 'progressive', '--force')
        assert yaml.safe_load(config_path.read_text(encoding='utf-8'))['context']['profile'] == 'minimal'

def test_runtime_manifest_requires_schema_and_closed_file_set() -> None:
    with tempfile.TemporaryDirectory(prefix='ads-manifest-', dir=ROOT) as temp:
        runtime = Path(temp)
        skill, data = (runtime / 'SKILL.md', b'x')
        skill.write_bytes(data)
        record = {'path': 'SKILL.md', 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        valid = {'schema_version': '5.3.0', 'skill_version': '5.4.7', 'source_commit': 'uncommitted-dirty', 'source_worktree_dirty': True, 'files': [record]}
        manifest = runtime / 'runtime-manifest.json'

        def check(value: object) -> str:
            manifest.write_text(json.dumps(value), encoding='utf-8')
            return '\n'.join(validate_runtime_manifest(runtime, '5.4.7'))
        assert not check(valid)
        cases = [({}, 'missing required fields'), ({**valid, 'files': []}, 'non-empty array'), ({**valid, 'extra': True}, 'unsupported fields'), ({**valid, 'source_commit': 'main-dirty'}, 'full Git SHA'), ({**valid, 'files': [{**record, 'extra': True}]}, 'exactly path, size and sha256'), ({**valid, 'files': [{**record, 'path': '../x'}]}, 'unsafe path'), ({**valid, 'files': [record, record]}, 'duplicate path'), ({**valid, 'source_worktree_dirty': False}, 'disagree')]
        assert all((expected in check(value) for value, expected in cases))
        extra = runtime / 'extra.txt'
        extra.write_text('x')
        assert 'does not cover' in check(valid)
        extra.unlink()
        skill.write_text('xx')
        assert 'manifest file drift' in check(valid)

def test_turn_budget_fails_closed() -> None:
    with tempfile.TemporaryDirectory(prefix='ads-deadlock-') as temp:
        work = Path(temp)
        contract = yaml.safe_load((ROOT / 'references/templates/discovery-contract-template.yaml').read_text(encoding='utf-8'))
        contract.update({'contract_id': 'DISC-DEADLOCK-001', 'project_id': 'deadlock-test'})
        contract['sources'][0].update({'id': 'SRC-DEADLOCK-001', 'path': 'test input'})
        contract['unknowns'][0].update({'id': 'UNK-DEADLOCK-001', 'owner': 'test owner'})
        contract_path = work / 'discovery.yaml'
        contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding='utf-8')
        config = yaml.safe_load(CONFIG.read_text(encoding='utf-8'))
        config['execution']['max_turns_per_stage'] = 2
        config_path = work / 'spec.config.yaml'
        config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        state0, state1, state2, overflow = [work / f'state-{item}.yaml' for item in (0, 1, 2, 3)]
        run(MANAGER, 'create', '--discovery-contract', str(contract_path), '--config', str(config_path), '--installed-skill', str(ROOT), '--execution-id', 'EXEC-DEADLOCK-001', '--output', str(state0))
        run(MANAGER, 'record-turn', '--state', str(state0), '--output', str(state1))
        run(MANAGER, 'record-turn', '--state', str(state1), '--output', str(state2))
        blocked = run(MANAGER, 'record-turn', '--state', str(state2), '--output', str(overflow), expected=1)
        assert 'LifecycleConvergenceError' in blocked.stdout
        assert not overflow.exists()
        run(MANAGER, 'verify', '--state', str(state2))

def test_capsule_write_slots_are_isolated() -> None:
    source = yaml.safe_load((ROOT / 'maintainer/examples/generic-energy-capsule-v5/project-domain-capsule.yaml').read_text(encoding='utf-8'))
    other = copy.deepcopy(source)
    other['capsule_id'] = 'CAP-FACILITY-MAINTENANCE-001'
    other['namespace'] = 'facility-maintenance'
    for index, policy in enumerate(other['policies'], start=1):
        policy['id'] = f'RULE-FACILITY-MAINTENANCE-{index:03d}'
    with tempfile.TemporaryDirectory(prefix='ads-capsule-') as temp:
        work = Path(temp)
        first, second = (work / 'energy.yaml', work / 'facility.yaml')
        first.write_text(yaml.safe_dump(source, allow_unicode=True, sort_keys=False), encoding='utf-8')
        second.write_text(yaml.safe_dump(other, allow_unicode=True, sort_keys=False), encoding='utf-8')
        conflict = run(CAPSULE_VALIDATOR, '--capsule', str(first), '--capsule', str(second), expected=1)
        assert 'shadow write conflict' in conflict.stdout
        for policy in other['policies']:
            policy['writes_to'] = ['facility.' + slot for slot in policy.get('writes_to', [])]
        other['context_dictionary'].extend(({'name': 'facility.' + item['name'], 'type': item['type'], 'description': item['description']} for item in list(other['context_dictionary']) if item['name'].startswith('work_order.')))
        second.write_text(yaml.safe_dump(other, allow_unicode=True, sort_keys=False), encoding='utf-8')
        run(CAPSULE_VALIDATOR, '--capsule', str(first), '--capsule', str(second))

def test_invalid_change_does_not_replace_stable_checkpoint() -> None:
    with tempfile.TemporaryDirectory(prefix='ads-change-drift-') as temp:
        work = Path(temp)
        state0 = work / 'state-000.yaml'
        run(MANAGER, 'create', '--truth', str(TRUTH), '--config', str(CONFIG), '--installed-skill', str(ROOT), '--execution-id', 'EXEC-CHANGE-DRIFT-001', '--output', str(state0))
        invalid = yaml.safe_load(TRUTH.read_text(encoding='utf-8'))
        invalid.pop('product')
        invalid_path = work / 'invalid-truth.yaml'
        invalid_path.write_text(yaml.safe_dump(invalid, sort_keys=False), encoding='utf-8')
        failed_state = work / 'state-failed.yaml'
        run(MANAGER, 'checkpoint', '--state', str(state0), '--truth', str(invalid_path), '--output', str(failed_state), expected=1)
        assert not failed_state.exists()
        run(MANAGER, 'verify', '--state', str(state0))

def test_structured_clarification_closes_only_named_unknowns() -> None:
    contract = yaml.safe_load((ROOT / 'references/templates/discovery-contract-template.yaml').read_text(encoding='utf-8'))
    contract.update({'contract_id': 'DISC-X', 'project_id': 'test'})
    contract['sources'][0].update({'id': 'SRC-X', 'path': 'input'})
    contract['unknowns'][0].update({'id': 'UNK-X', 'owner': 'owner'})
    transcript = {'schema_version': '5.3.3', 'transcript_id': 'TRN-X', 'project_id': 'test', 'turns': [{'turn_id': 'TURN-X', 'unknown_id': 'UNK-X', 'question': 'Which slice?', 'answer': 'Import and search.', 'decision_owner': 'owner', 'status': 'answered', 'question_kind': 'direction', 'recommendation': 'Use one slice.', 'recommendation_evidence_refs': ['meeting'], 'tradeoff': 'History deferred.', 'affected_refs': ['UNK-X'], 'blocks_stage': 'specify', 'reversal_path': 'Reopen by CHG.', 'evidence_refs': ['meeting']}]}
    with tempfile.TemporaryDirectory(prefix='ads-grill-') as temp:
        work = Path(temp)
        contract_path, transcript_path, output = (work / 'contract.yaml', work / 'transcript.yaml', work / 'next.yaml')
        contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding='utf-8')
        transcript_path.write_text(yaml.safe_dump(transcript, sort_keys=False), encoding='utf-8')
        run(COMPILER, '--contract', str(contract_path), '--transcript', str(transcript_path), '--decision', 'READY_FOR_PRODUCT_TRUTH', '--output', str(output))
        compiled = yaml.safe_load(output.read_text(encoding='utf-8'))
        assert compiled['unknowns'][0]['status'] == 'answered'
        bad_contract = yaml.safe_load(contract_path.read_text(encoding='utf-8'))
        bad_contract['unknowns'].append({'id': 'UNK-Y', 'question': 'Which authority?', 'impact': 'data', 'priority': 'P1', 'owner': 'owner', 'status': 'open', 'recommendation': 'Keep read-only.', 'recommendation_evidence_refs': ['meeting'], 'tradeoff': 'Submit blocked.'})
        bad_path = work / 'bad-contract.yaml'
        bad_path.write_text(yaml.safe_dump(bad_contract, sort_keys=False), encoding='utf-8')
        blocked = run(COMPILER, '--contract', str(bad_path), '--transcript', str(transcript_path), '--decision', 'READY_FOR_PRODUCT_TRUTH', '--output', str(work / 'bad-next.yaml'), expected=1)
        assert 'not owned/scoped' in blocked.stdout

def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith('test_')]
    for test in tests:
        test()
    print(f'PASS: {len(tests)} runtime-resilience capability regressions')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
