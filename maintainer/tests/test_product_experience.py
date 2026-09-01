"""Product experience regression"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/validators')]
from analyze_change_impact import graph_from_truth
from quality_gate import Finding, Gate, diagnostic_roots as quality_roots
from scan_requirement_ambiguity import scan, scan_closure
from stage_contract import diagnostic_roots as stage_roots
from validate_coding_agent_contract import ai_contract_applicable

def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding='utf-8')

def require(relative: str, *needles: str) -> str:
    text = read(relative)
    missing = [item for item in needles if item not in text]
    assert not missing, f'{relative} missing {missing}'
    return text

def run(*parts: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *parts], cwd=ROOT, text=True, encoding='utf-8', errors='replace', capture_output=True)

def test_trigger_and_minimum_change_contract() -> None:
    skill = require('SKILL.md', '写/改一个小功能', '加字段/列/页签/下拉', 'Always invoke regardless of size or clarity', '也必须调用', '`direct`', '最小主产物', '存量系统先做 Stage 0', '声称 `PASS` 前运行', '语法检查不得替代门禁')
    agent = require('agents/openai.yaml', 'policy:', 'allow_implicit_invocation: true', 'Use $ai-delivery-spec', '使用', "user's language")
    require('references/discover.md', '最小改动模式', '不超过一个短屏', '生产者/权威源 → 汇聚或转换方 → 消费方', '隔离粒度、批次/记录状态、幂等键', '可重报范围与聚合回执是同一组 P0')
    require('references/prototype.md', 'parity_status=pass|blocked', '正向上报、反向同步和纠错申请必须使用不同命令/队列')
    assert 'version: "5.4.2"' not in agent and skill

def test_convergence_and_visual_lock_contract() -> None:
    discover = require('references/discover.md', '发散：', '聚焦：', '深化：', '小而明确的需求默认0轮澄清', '普通模糊需求默认最多2个阻断决策轮', '自由对话不展示这些内部 ID', '不得把无关工作区的客户、合同、回款、角色或流程移植进方案')
    require('references/stages.md', '不要在到达目标前逐站运行门禁')
    require('references/prototype.md', '现有 HTML、截图和已批准页面是默认视觉权威', '不询问美学方向', 'visual_authority=existing', 'design_lock_ref')
    assert 'L1三批、L2六批、L3/L4八批' not in discover

def test_v548_shortcuts_are_thin_routes_and_medium_example_is_shipped() -> None:
    skill = require('SKILL.md', '`/ads`', '`/dig`', '`/prd`', '`/proto`', '不创建四套流程或四类新产物', '不得宣称四个裸别名已在所有宿主原生注册', '未读到基线时列为非阻断 GAP')
    discover = require(
        'references/discover.md',
        '战略（strategic）', '系统（systemic）', '行为心理（psychological）', '反方挑战（devil\'s advocate）',
        '不得另造一份与基线竞争的拷问报告', '一次只问一个',
    )
    stages = require('references/stages.md', '四个快捷入口只覆盖本次目标', '它们是意图别名', '`/ads`', '`/dig`', '`/prd`', '`/proto`', '没有读到基线时必须记为非阻断 GAP', '不得把四个裸别名描述成跨宿主原生注册')
    readme = require('README.md', '意图别名，不是四套新流程', 'examples/medium-review-handoff/review-prototype.html', '消息到达模型前拦截未知命令', '不宣称跨宿主原生注册', '社区验证｜Community Validation', '60 秒上手｜60-Second Quick Start', '**English:**')
    assert '| GitHub | Apache 2.0 开源 |' not in readme
    agent = yaml.safe_load(read('agents/openai.yaml'))
    assert set(agent['inputs']['intent_shortcut']['enum']) == {'auto', 'ads', 'dig', 'prd', 'proto'}
    assert '/clarify' not in skill + discover + stages + readme + read('agents/openai.yaml')
    assert 'grill report' not in (skill + discover + stages + readme).lower()
    example = require(
        'examples/medium-review-handoff/review-prototype.html',
        '.app.review-collapsed ~ .review-launch{display:block}',
        '.review-launch{position:fixed;right:18px;top:18px;z-index:45;',
        '.review-list:not([hidden]){display:grid;gap:8px}',
        '.review-list[hidden]{display:none}',
        'left:208px;right:var(--review)',
        'data-ads-act="collapse"', 'data-ads-act="expand"',
        'data-review-anchor="METRIC-SLA-001"', 'data-review-point="RVP-METRIC-SLA"',
        'data-review-context-root="DRAWER-TASK-001"',
    )
    assert 'data-action="UIACT-REVIEW-TOGGLE"' in example
    assert 'data-state="board_ready"' in example and "app.dataset.state='task_saved'" in example

def test_root_diagnostics_compact_repetition() -> None:
    findings = [Finding('BLOCK', 'CODE-A', 'a', 'one'), Finding('BLOCK', 'CODE-A', 'b', 'two'), Finding('GAP', 'CODE-B', 'c', 'three')]
    roots, unique = quality_roots(findings, 20)
    assert unique == 2 and [(item.code, count) for item, count in roots] == [('CODE-A', 2), ('CODE-B', 1)]
    roots, _ = quality_roots([Finding('BLOCK', 'CODE-C', 'x', 'shell', '${act}'), Finding('BLOCK', 'CODE-C', 'x', 'real', 'ACT-SAVE')], 20)
    assert roots[0][0].ref == 'ACT-SAVE'
    roots, unique = stage_roots([{'code': 'CODE-A'}, {'code': 'CODE-A'}, {'code': 'CODE-B'}], 20)
    assert unique == 2 and [(item['code'], count) for item, count in roots] == [('CODE-A', 2), ('CODE-B', 1)]
    require('scripts/ai_delivery_spec_cli.py', 'choices=["first", "roots", "summary", "full"], default="roots"')

class MemoryGate(Gate):

    def __init__(self, documents: dict[str, str]):
        super().__init__()
        self.documents = {str(Path(name)): value for name, value in documents.items()}

    def read(self, path: Path) -> str:
        return self.documents[str(path)]

def test_visible_comparison_copy_cannot_be_swallowed_as_html_tag() -> None:
    broken = Path('broken-comparison.html')
    safe = Path('safe-comparison.html')
    documents = {
        str(broken): '<section data-testid="page-VIEW-X" data-state="ready"><p>比例0<rate≤100，金额>0。</p></section>',
        str(safe): '<section data-testid="page-VIEW-X" data-state="ready"><p>比例0 &lt; rate ≤ 100，金额 &gt; 0。</p></section>',
    }
    gate = MemoryGate(documents)
    gate.check_prototype(broken, 'L0')
    assert 'PROTO-VISIBLE-COMPARISON-UNESCAPED' in {item.code for item in gate.findings}
    gate = MemoryGate(documents)
    gate.check_prototype(safe, 'L0')
    assert 'PROTO-VISIBLE-COMPARISON-UNESCAPED' not in {item.code for item in gate.findings}

def test_brownfield_visual_lock_satisfies_handoff() -> None:
    prd, prototype = (Path('prd.md'), Path('prototype.html'))
    gate = MemoryGate({str(prd): '---\npage_contract_view_ids: [VIEW-X]\n---\nREQ-X ACT-X AC-X', str(prototype): '<section data-testid="page-VIEW-X"><!-- [PROTOTYPE LOCK] visual_authority=existing design_lock_ref=inline --></section>'})
    gate.check_handoff(prd, [prototype], 'L3')
    assert 'HANDOFF-AESTHETIC-UNDECIDED' not in {item.code for item in gate.findings}

def test_experience_metrics_cover_reported_regressions() -> None:
    metrics = yaml.safe_load(read('maintainer/evals/metric-definitions.yaml'))['metrics']
    required = {'skill_trigger_recall', 'time_to_first_usable_result_seconds', 'clarification_decision_turns', 'unnecessary_stage_rate', 'overinterpretation_rate', 'visual_lock_consistency_rate', 'gate_root_cause_coverage_rate', 'gate_repair_cycles', 'task_satisfaction_rate'}
    assert required <= set(metrics)

def test_generated_status_matches_release_summary() -> None:
    result = run('scripts/ai_delivery_spec_cli.py', 'status', '--format', 'yaml')
    assert result.returncode == 0
    generated = yaml.safe_load(result.stdout)
    evidence = yaml.safe_load(read('maintainer/evals/evidence/release-status.yaml'))
    for key in ('schema_version', 'skill_version', 'runtime', 'domain_packs', 'evaluation_assets'):
        assert generated[key] == evidence[key]
    assert generated['domain_packs']['production_claims_allowed'] == 0
    assert generated['trace_release_proxy']['dimensions']['effectiveness'] == 'partial'
    assert evidence['trace_release_proxy']['dimensions']['effectiveness'] == 'partial'
    combined = yaml.safe_dump(generated, allow_unicode=True).lower()
    assert 'customer acceptance' in combined and 'not proven' in combined

def test_ai_applicability() -> None:
    assert not ai_contract_applicable('本期不建设独立 AI 模型。Coding Agent 读取稳定 ID 后实现页面。')
    assert ai_contract_applicable('AI 组课调用大模型生成课程结构，由内容审核员确认后发布。')
    assert ai_contract_applicable('不建设 AI 模型中心；但 AI 组课调用大模型并保留人工审核。')

def test_semantic_guards_and_trace_graph() -> None:
    for text in ('三甲医院做门诊退费、医保对账和失败人工处理。', '制造企业做质量异常、隔离、评审和供应商整改闭环。', '连锁零售增加跨门店调拨、收货差异和库存回冲。'):
        assert not scan(text)
        assert {'actor-authority', 'state-authority', 'acceptance-evidence'} <= {item['kind'] for item in scan_closure(text)}
    graph = graph_from_truth({'edges': [{'from_id': 'REQ-X', 'to_id': 'ACT-X'}, {'from_id': 'ACT-X', 'to_id': 'AC-X'}]})
    assert graph['REQ-X'] == {'ACT-X'} and graph['AC-X'] == {'ACT-X'}

def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith('test_')]
    for test in tests:
        test()
    print(f'PASS: {len(tests)} product-experience capability regressions')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
