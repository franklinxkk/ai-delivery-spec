#!/usr/bin/env python3
"""Capability suite: trigger, convergence, scope control, status, and semantic safety."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "validators"))

from analyze_change_impact import graph_from_truth  # noqa: E402
from quality_gate import Finding, Gate, diagnostic_roots as quality_roots  # noqa: E402
from scan_requirement_ambiguity import scan, scan_closure  # noqa: E402
from stage_contract import diagnostic_roots as stage_roots  # noqa: E402


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} missing: {needle}")


def run(*parts: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *parts],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


def test_trigger_and_minimum_change_contract() -> None:
    skill = read("SKILL.md")
    agent = read("agents/openai.yaml")
    discover = read("references/discover.md")
    prototype = read("references/prototype.md")
    for needle in (
        "写/改一个小功能",
        "加字段/列/页签/下拉",
        "直接改更快",
        "小迭代先最小改动",
        "示例子集",
        "反向同步不得进入正向上报队列",
    ):
        require(skill, needle, "trigger/minimum-change contract")
    require(agent, "policy:", "implicit invocation policy")
    require(agent, "allow_implicit_invocation: true", "implicit invocation enabled")
    require(agent, "$ai-delivery-spec；写/改小功能", "host-facing trigger examples")
    require(agent, "不能用示例子集冒充替换", "host-facing parity contract")
    require(discover, "最小改动模式", "minimum-change routing")
    require(discover, "不超过一个短屏", "human-first output budget")
    require(discover, "生产者/权威源 → 汇聚或转换方 → 消费方", "integration direction")
    require(prototype, "parity_status=pass|blocked", "brownfield parity status")
    require(prototype, "正向上报、反向同步和纠错申请必须使用不同命令/队列", "queue separation")
    if 'version: "5.4.3"' in agent:
        raise AssertionError("agents/openai.yaml contains unsupported interface.version")


def test_convergence_and_visual_lock_contract() -> None:
    discover = read("references/discover.md")
    stages = read("references/stages.md")
    prototype = read("references/prototype.md")
    for needle in (
        "发散：",
        "聚焦：",
        "深化：",
        "小而明确的需求默认0轮澄清",
        "普通模糊需求最多2个阻断决策轮",
        "自由对话不展示这些内部 ID",
        "不得把无关工作区的客户、合同、回款、角色或流程移植进方案",
    ):
        require(discover, needle, "convergence loop")
    require(stages, "不要在到达目标前逐站运行门禁", "single milestone gate")
    for needle in (
        "现有 HTML、截图和已批准页面是默认视觉权威",
        "不询问美学方向",
        "visual_authority=existing",
        "design_lock_ref",
    ):
        require(prototype, needle, "visual lock")
    if "L1三批、L2六批、L3/L4八批" in discover:
        raise AssertionError("legacy fixed clarification batches remain active")


def test_root_diagnostics_compact_repetition() -> None:
    findings = [
        Finding("BLOCK", "CODE-A", "a.md", "first"),
        Finding("BLOCK", "CODE-A", "b.md", "second"),
        Finding("GAP", "CODE-B", "c.md", "third"),
    ]
    roots, unique = quality_roots(findings, 20)
    assert unique == 2
    assert [(item.code, count) for item, count in roots] == [("CODE-A", 2), ("CODE-B", 1)]
    stage, stage_unique = stage_roots(
        [{"code": "CODE-A"}, {"code": "CODE-A"}, {"code": "CODE-B"}],
        20,
    )
    assert stage_unique == 2
    assert [(item["code"], count) for item, count in stage] == [("CODE-A", 2), ("CODE-B", 1)]
    require(
        read("scripts/ai_delivery_spec_cli.py"),
        'choices=["first", "roots", "summary", "full"], default="roots"',
        "public gate default",
    )


class MemoryGate(Gate):
    def __init__(self, documents: dict[str, str]):
        super().__init__()
        self.documents = {str(Path(name)): value for name, value in documents.items()}

    def read(self, path: Path) -> str:
        return self.documents[str(path)]


def test_brownfield_visual_lock_satisfies_handoff() -> None:
    prd = Path("prd.md")
    prototype = Path("prototype.html")
    gate = MemoryGate(
        {
            str(prd): "---\npage_contract_view_ids: [VIEW-DEMO-001]\n---\nREQ-DEMO-001 ACT-DEMO-001 AC-DEMO-001\n",
            str(prototype): (
                '<section data-testid="page-VIEW-DEMO-001">'
                "<!-- [PROTOTYPE LOCK] visual_authority=existing design_lock_ref=inline -->"
                "</section>"
            ),
        }
    )
    gate.check_handoff(prd, [prototype], "L3")
    assert "HANDOFF-AESTHETIC-UNDECIDED" not in {item.code for item in gate.findings}


def test_experience_metrics_cover_reported_regressions() -> None:
    metrics = yaml.safe_load(read("maintainer/evals/metric-definitions.yaml"))["metrics"]
    required = {
        "skill_trigger_recall",
        "time_to_first_usable_result_seconds",
        "clarification_decision_turns",
        "unnecessary_stage_rate",
        "overinterpretation_rate",
        "visual_lock_consistency_rate",
        "gate_root_cause_coverage_rate",
        "gate_repair_cycles",
        "task_satisfaction_rate",
    }
    assert not (required - set(metrics)), f"missing experience metrics: {sorted(required - set(metrics))}"


def test_generated_status_matches_release_summary() -> None:
    result = run(str(ROOT / "scripts/ai_delivery_spec_cli.py"), "status", "--format", "yaml")
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    generated = yaml.safe_load(result.stdout)
    committed = yaml.safe_load(read("maintainer/evals/evidence/release-status.yaml"))
    assert generated == committed, "committed release status is stale"


def test_ai_applicability() -> None:
    validator = ROOT / "scripts/validators/validate_coding_agent_contract.py"
    spec = importlib.util.spec_from_file_location("coding_contract", validator)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    excluded = "本期不建设独立 AI 模型/能力中心。第四部分：工程与 AI Coding 附录。Coding Agent 读取稳定 ID 后实现页面。"
    applicable = "本期提供 AI 组课：调用大模型生成课程结构，由内容审核员人工确认后发布。"
    mixed = "本期不建设 AI 模型中心；但 AI 组课调用大模型生成结构，并保留人工审核。"
    assert not module.ai_contract_applicable(excluded)
    assert module.ai_contract_applicable(applicable)
    assert module.ai_contract_applicable(mixed)


def test_coding_contract_and_semantic_guards() -> None:
    complete = ROOT / "maintainer/tests/fixtures/coding-l2.md"
    thin = ROOT / "maintainer/tests/fixtures/coding-l2-thin.md"
    keyword_shell = ROOT / "maintainer/tests/fixtures/prd-l2-keyword-shell.md"
    for level in ("L0", "L1", "L2", "L3", "L4"):
        for script, fixture in (
            ("validate_prd_quality.py", complete),
            ("validate_ia_skeleton.py", ROOT / "maintainer/tests/fixtures/ia-l2.yaml"),
            ("validate_coding_agent_contract.py", complete),
        ):
            result = run(str(ROOT / "scripts/validators" / script), str(fixture), "--level", level)
            if result.returncode:
                raise AssertionError(f"{script} rejected level {level}\n{result.stdout}{result.stderr}")
    for script, extra in (
        ("validate_prd_quality.py", ("--level", "L2")),
        ("validate_coding_agent_contract.py", ("--level", "L2", "--profile", "full_prd")),
    ):
        good = run(str(ROOT / "scripts/validators" / script), str(complete), *extra)
        bad = run(str(ROOT / "scripts/validators" / script), str(keyword_shell), *extra)
        assert good.returncode == 0, good.stdout + good.stderr
        assert bad.returncode != 0, f"{script} accepted keyword shell"
    rejected = run(
        str(ROOT / "scripts/validators/validate_coding_agent_contract.py"),
        str(thin),
        "--level",
        "L2",
    )
    assert rejected.returncode != 0, "thin handoff passed coding contract"

    for text in (
        "三甲医院做门诊退费与医保对账，多角色审批，原支付渠道退款，医保失败人工处理。",
        "制造企业做来料质量异常、隔离、评审、退货或让步接收和供应商整改闭环。",
        "连锁零售在存量系统增加跨门店调拨、在途、收货差异和库存回冲。",
    ):
        assert not scan(text), "lexical-only scan unexpectedly inferred contract"
        structural = {item["kind"] for item in scan_closure(text)}
        assert {"actor-authority", "state-authority", "acceptance-evidence"}.issubset(structural)

    ledger = {
        "schema_version": "5.1.0",
        "edges": [
            {"from_id": "REQ-DEMO-001", "to_id": "ACT-DEMO-001", "relation": "specifies", "source": "behavior_refs"},
            {"from_id": "ACT-DEMO-001", "to_id": "AC-DEMO-001", "relation": "verified_by", "source": "acceptance_refs"},
        ],
        "forward_index": {"REQ-DEMO-001": ["ACT-DEMO-001"]},
        "reverse_index": {"AC-DEMO-001": ["ACT-DEMO-001"]},
    }
    graph = graph_from_truth(ledger)
    assert graph.get("REQ-DEMO-001") == {"ACT-DEMO-001"}
    assert graph.get("AC-DEMO-001") == {"ACT-DEMO-001"}


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} product-experience capability regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
