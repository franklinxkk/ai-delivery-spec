#!/usr/bin/env python3
"""Focused 5.4.4 contracts for localized human review and implementation handoff."""

from __future__ import annotations

import json
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
failures: list[str] = []


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(relative: str, markers: tuple[str, ...]) -> None:
    text = read(relative)
    for marker in markers:
        if marker not in text:
            failures.append(f"{relative} misses {marker!r}")


skill = read("SKILL.md")
if "# AI Delivery Spec 5.4.4" not in skill:
    failures.append("SKILL.md does not declare 5.4.4")
require(
    "SKILL.md",
    (
        "中文交付不得把 Given/When/Then、draft、pending → resolved、lastCursor 等英文裸露为正文",
        "人类可见状态/字段/事件/队列先写该语言含义",
        "客户演示或客户确认阶段默认产品模式",
        "只有用户明确要求“评审版/评审模式/编号标注/评审抽屉”",
        "“交开发/给前后端测试看/开需求评审会”只说明消费方",
        "未确认时继续产品模式",
        "明确“我要评审版”即已确认",
        "一句话请求已明确要求原型时",
        "必须继续到可操作产品原型",
        "一句话需求首次进入原型",
        "不阻断产品模式",
        "同一需求基线内不重复追问",
        "review 工作站是多角色签署与缺口关闭，不等于原型评审模式",
        "YAML/JSON 侧车可保留键名与枚举",
        "客户全生命周期",
        "无页面入口权限时菜单/路由入口不可见",
        "核心流程图/状态转换图/数据流血缘图",
        "机器全量覆盖、人类克制投影",
        "一个编号可覆盖一个区域",
        "同时加载 `references/context.md` 与 `references/prototype.md`",
        "L2/L3 PRD须用统一模板过门禁",
        "评审投影不得替代",
        "结构不全不得称可开发",
    ),
)
for forbidden in ("用户已明确要交前后端/测试时直接生成", "Start with intake", "one human-readable"):
    if forbidden in skill:
        failures.append(f"SKILL.md still auto-generates review mode for consumer-only intent: {forbidden!r}")

frontmatter_match = re.match(r"\A---\s*\n(.*?)\n---", skill, re.S)
frontmatter = yaml.safe_load(frontmatter_match.group(1)) if frontmatter_match else {}
description = str((frontmatter or {}).get("description", ""))
for marker in ("requirements", "prototypes", "Always invoke", "需求", "原型", "必须调用"):
    if marker not in description:
        failures.append(f"bilingual trigger description misses {marker!r}")

agent = yaml.safe_load(read("agents/openai.yaml"))
interface = (agent or {}).get("interface", {})
if "AI Delivery Spec" not in str(interface.get("display_name", "")) or "需求" not in str(interface.get("display_name", "")):
    failures.append("host display_name is not bilingual")
short_description = str(interface.get("short_description", ""))
if not (25 <= len(short_description) <= 64) or "Requirements" not in short_description or "需求" not in short_description:
    failures.append(f"host short_description is not concise bilingual metadata: {short_description!r}")
default_prompt = str(interface.get("default_prompt", ""))
for marker in ("$ai-delivery-spec", "follow the user's language", "使用"):
    if marker not in default_prompt:
        failures.append(f"host default_prompt misses {marker!r}")
if len(default_prompt) > 500:
    failures.append("host default_prompt should stay compact")
if any(marker in read("agents/openai.yaml") for marker in ("闇€", "浠讳", "锛")):
    failures.append("agents/openai.yaml still contains mojibake")

require(
    "README.md",
    (
        "Requirements to Delivery｜需求到交付",
        "English works end to end",
        "Use $ai-delivery-spec",
        "--language auto|en-US|zh-CN",
    ),
)
require(
    "references/specify.md",
    ("全英文交付必须使用英文标题", "中英混合输入未指定输出语言时取主要交流语言", "--language auto|zh-CN|en-US"),
)
require(
    "references/prototype.md",
    ("全英文原型不得出现中文模板", "review version / review mode / numbered annotations / review drawer", "HTML 同步声明"),
)
stages = read("references/stages.md")
for marker in (
    "一句话请求已把原型列为目标时",
    "评审偏好尚未表达时",
    "未回复时继续",
    "同一需求基线内不重复询问",
    "review 工作站负责签署与缺口关闭，不等于可见的原型评审模式",
    "机器文件的工作站，在对用户交付时还必须附同语言的人类",
    "客户演示或客户确认时默认产品模式",
    "只有用户明确要求“评审版”“评审模式”“编号",
    "“交开发”“给前后端/测试看”“开需求评审会”只说明",
    "未确认时继续产品模式",
    "显式“我要评审版”已经构成确认",
):
    if marker not in stages:
        failures.append(f"stages contract misses {marker!r}")
if "要进入前后端/测试评审时直接生成" in stages:
    failures.append("stages still auto-generates review mode for consumer-only intent")


for relative in (
    "references/templates/prd-light-template.md",
    "examples/minimal-v5/requirement-card.md",
):
    text = read(relative)
    if any(marker in text for marker in ("Given 前置", "When 操作", "Then 可见结果", "And 领域结果")):
        failures.append(f"{relative} still exposes English BDD labels in Chinese human content")
require(
    "references/templates/prd-light-template.md",
    ("前提（角色与数据）", "入口/数据/动作/字段权限分层"),
)

prototype = read("references/prototype.md")
for marker in (
    "帮我做一个企业约谈原型",
    "首次进入原型时询问一次；未回复先交付产品模式",
    "只做干净的产品原型，不要评审标注",
    "review 工作站是评审签署和缺口关闭，不等于原型的可见评审模式",
    "review_projection=unset|confirmed|declined",
    "默认（`default`）",
    "空数据/范围内无数据（`empty/no_data_in_scope`）",
    "成功主路径（`happy path`）",
    "产品模式、评审模式与三类核心图",
    "页面共识 + `1/2/3...` 编号标注",
    "| 核心流程图 |",
    "下周给客户演示 CRM",
    "售前拿去讲线索到回款",
    "我要评审版",
    "生成带编号和右侧评审抽屉的版本",
    "这个原型要交开发",
    "前后端和测试要看",
    "下周开需求评审会",
    "给客户演示，也方便开发看",
    "先别加标注，之后再评审",
    "评审一下现有原型，不要改页面",
    "Lead.id → Opportunity.leadId → Contract.opportunityId → Invoice/Payment.contractId",
    "Customer.id → Ticket.customerId → Demand.ticketId → IterationTask.demandId",
    "| 状态转换图 |",
    "| 数据流/血缘图 |",
    "| 菜单/页面入口 |",
    "| 数据范围 |",
    "| 动作/组件 |",
    "| 字段 |",
    "普通无入口角色不需要先进入页面再看“您无权限”",
    "角色复述检查",
    "待处理（`pending`）→ 已解决（`resolved`）/",
    "同步游标（`lastCursor`）",
    "申诉队列（`appeal`）",
    "未知来源",
    "（`unknown_source`）",
    "评审投影的信息预算",
    "常规字段释义、显然按钮、重复规则和完整测试步骤只进入机器覆盖账本",
    "“克制”只减少重复，不减少核心实现语义",
    "STEP-*",
    "入口与责任",
    "输入与权威源",
    "确认差异后是否回写企业源、监管源或只写本次快照",
    "计数单位和日志一行代表什么",
    "失败与恢复",
    "共识/前端/后端/测试",
    "Coding Agent 能输出不新增业务假设的入口图",
    "design_read",
    "variance/motion/density=1..5",
    "触发→选择→理由→证据",
    "UIACT-REVIEW-*",
    "产品→评审→产品往返业务",
    "重型存量页面的评审容器",
    "一次只在用户选择后懒加载一页",
    "artifact_sha256=",
    "baseline_sha256=",
    "visible_review_note_count=",
    "gate_output_ref=",
):
    if marker not in prototype:
        failures.append(f"prototype contract misses {marker!r}")

require(
    "references/specify.md",
    (
        "“继续”或",
        "“下一步”不重置语言",
        "机器侧车交付时另附同语言的人类可读摘要",
        "实施步骤卡、原型评审抽屉和专项评审说明都不能替代这份统一 PRD",
        "专项说明只能标为“补充件”",
    ),
)
require(
    "references/lifecycle.md",
    (
        "接受（`accept`）",
        "澄清（`clarify`）",
        "有条件接受（`accepted_with_conditions`）",
        "机器侧车",
        "同语言的人类可读摘要",
    ),
)
require(
    "references/change-acceptance.md",
    (
        "通过/失败/阻断/未执行（`pass/fail/blocked/not_run`）",
        "有条件接受/拒绝/待定（`accepted/accepted_with_conditions/rejected/pending`）",
    ),
)
require(
    "references/templates/problem-brief-template.md",
    ("方案探索（`explore`）/需求准入（`intake`）",),
)
require(
    "references/templates/solution-sketch-template.md",
    ("未验证（`untested`）",),
)
for relative in (
    "references/templates/requirement-brief-template.md",
    "references/templates/decision-record-template.md",
):
    require(
        relative,
        (
            "已确认（`confirmed`）",
            "阻断阶段（`blocks_stage`）",
            "需求基线（`baseline`）",
            "待关闭（`open`）",
        ),
    )
require(
    "references/templates/prd-light-template.md",
    (
        "接受/澄清/延后/拒绝（`accept/clarify/defer/reject`）",
        "界面（`ui`）",
        "状态流转（`stateful`）",
    ),
)
require(
    "references/templates/unified-requirement-prd-template.md",
    ("默认/空数据/加载中/错误（`default/empty/loading/error`）状态",),
)
if "响应式和 default/empty/loading/error/no-permission 状态" in read("references/templates/unified-requirement-prd-template.md"):
    failures.append("unified PRD template still exposes bare English UI states")

known_human_leaks = {
    "references/templates/problem-brief-template.md": ("| explore/intake |",),
    "references/templates/solution-sketch-template.md": ("| untested |",),
    "references/templates/requirement-brief-template.md": (
        "| confirmed |", "| baseline |", "| open |", "READY_FOR_LIGHT_SPEC /",
    ),
    "references/templates/decision-record-template.md": (
        "| confirmed |", "| baseline |", "| open |", "进入 specify /",
    ),
    "references/templates/prd-light-template.md": (
        "accept / clarify / defer / reject", "| 条件 Facet |", "| `ui` |",
    ),
}
for relative, forbidden_markers in known_human_leaks.items():
    text = read(relative)
    for marker in forbidden_markers:
        if marker in text:
            failures.append(f"{relative} still exposes bare machine/English human text: {marker!r}")

for forbidden in ("用户已经明确要给前端、后端或测试评审时直接生成",):
    if forbidden in prototype:
        failures.append(f"prototype still auto-generates review mode for consumer-only intent: {forbidden!r}")


if "| no_permission | 清楚说明边界且不泄露隐藏数据 |" in prototype:
    failures.append("prototype still treats no_permission as a universal visible page state")

require(
    "references/specify.md",
    (
        "草稿（`draft`）",
        "（`pending`）→ 已解决（`resolved`）/申诉中（`appealing`）",
        "同步游标（`lastCursor`）",
        "（`unknown_source`）",
        "菜单和路由入口不可见",
        "empty/no_data_in_scope",
        "人类评审原型只投影页面共识",
        "核心实施步骤合同",
        "处理/计算口径",
        "差异确认后明确回写哪个权威对象",
        "成功、失败、部分成功的数量如何归集",
        "事件响应",
        "规格不能声明开发就绪",
    ),
)
require(
    "references/templates/unified-requirement-prd-template.md",
    (
        "STEP-{模块}-{序号}",
        "日志及一行代表的粒度",
        "企业/人员/车辆/证件等计数单位",
        "下一角色和可达入口",
    ),
)
require(
    "references/tool-adapters.md",
    (
        "不是 Coding Agent 的第二份 PRD",
        "机器状态、字段/API名和 Schema 关键字保持原值",
    ),
)

agent_schema = json.loads(read("schemas/agent-handoff.schema.json"))
if agent_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
    failures.append("JSON Schema Draft identifier was incorrectly localized")
if "draft" not in agent_schema["properties"]["status"]["enum"]:
    failures.append("machine enum draft was incorrectly localized")
packet_props = agent_schema["properties"]["packets"]["items"]["properties"]
if "implementation_step_refs" not in packet_props:
    failures.append("agent handoff schema does not expose implementation step refs")
require(
    "references/prototype.md",
    ("交互账本是从原型提取的覆盖清单和回归证据，不是需求权威源", "不能为 PRD 中不存在的业务"),
)
require(
    "references/specify.md",
    ("implementation_step_refs", "必须解析到 PRD 中完整的 `STEP-*` 卡", "开发就绪时不得漏包"),
)
for template in (
    "references/templates/problem-brief-template.md",
    "references/templates/solution-sketch-template.md",
    "references/templates/requirement-brief-template.md",
    "references/templates/decision-record-template.md",
    "references/templates/assumption-register-template.yaml",
):
    require(template, ("续跑对象示例", "sha256:", "stage:"))


def run_json(command: list[str]) -> tuple[int, dict]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        failures.append(
            f"command did not return JSON: {' '.join(command)}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
        return completed.returncode, {}
    return completed.returncode, payload


def selected_human_text(payload: dict) -> str:
    values = [str(payload.get("coverage", "")), *[str(item) for item in payload.get("not_proven", [])]]
    for item in payload.get("findings", []):
        values.extend(str(item.get(key, "")) for key in ("message", "cause", "how_to_fix", "repair_example"))
    return "\n".join(values)


with tempfile.TemporaryDirectory(prefix="ads-v544-step-") as temp_name:
    temp = Path(temp_name)
    prd = temp / "PRD.md"
    prd_text = """# Demo PRD
REQ-DEMO-001 ACT-DEMO-SAVE AC-DEMO-001
### STEP-DEMO-01 保存业务对象
- 入口与责任：详情页保存按钮；管理员可执行。
- 输入与权威源：表单版本和字段来自业务主对象。
- 处理与口径：服务端校验、去重并按版本覆盖。
- 守卫与状态：draft -> saved；非法状态拒绝。
- 双结果：页面显示已保存；领域对象持久化。
- 事件与责任交接：发布 EVT-DEMO-SAVED 并交给审核人。
- 失败与恢复：冲突时刷新重试；命令幂等并保留审计。
- 追溯与验收：REQ-DEMO-001 / ACT-DEMO-SAVE / AC-DEMO-001 / SRC-DEMO-001。
"""
    prd.write_text(prd_text, encoding="utf-8")
    packet = temp / "MOD-DEMO.md"
    packet_text = """# MOD-DEMO
REQ-DEMO-001
STEP-DEMO-01
AC-DEMO-001
## qa_projection
positive, negative, permission and recovery evidence
"""
    packet.write_text(packet_text, encoding="utf-8")
    digest = hashlib.sha256(prd_text.encode("utf-8")).hexdigest()
    packet_digest = hashlib.sha256(packet_text.encode("utf-8")).hexdigest()
    manifest_document = {
        "schema_version": "5.3.0",
        "status": "review_ready",
        "baseline": {"version": "1.0", "hash": digest, "requirement_ref": prd.name},
        "packets": [{
            "id": "MOD-DEMO", "kind": "mod", "owner": "demo-team", "path": packet.name,
            "baseline_hash": digest, "content_sha256": packet_digest,
            "scope_refs": ["REQ-DEMO-001"], "implementation_step_refs": ["STEP-DEMO-01"],
            "acceptance_refs": ["AC-DEMO-001"],
        }],
        "handoffs": [],
    }
    manifest = temp / "handoff.json"
    manifest.write_text(json.dumps(manifest_document, ensure_ascii=False, indent=2), encoding="utf-8")
    code, payload = run_json([
        sys.executable, "scripts/ai_delivery_spec_cli.py", "gate", "--profile", "agent_handoff",
        "--manifest", str(manifest), "--format", "json",
    ])
    if code != 0:
        failures.append(f"complete STEP handoff should pass: {payload.get('findings')}")
    manifest_document["packets"][0]["implementation_step_refs"] = ["STEP-GHOST-999"]
    manifest.write_text(json.dumps(manifest_document, ensure_ascii=False, indent=2), encoding="utf-8")
    code, payload = run_json([
        sys.executable, "scripts/ai_delivery_spec_cli.py", "gate", "--profile", "agent_handoff",
        "--manifest", str(manifest), "--format", "json",
    ])
    finding_codes = {item.get("code") for item in payload.get("findings", [])}
    if code != 2 or "HANDOFF-STEP-NOT-IN-PRD" not in finding_codes:
        failures.append(f"ghost STEP reference escaped the handoff gate: rc={code}, codes={finding_codes}")

missing_html = ROOT / "maintainer/tests/fixtures/definitely-missing-v544.html"
for command, label in (
    ([sys.executable, "scripts/extract_interaction_ledger.py", "--input", str(missing_html), "--output", "-"], "ledger"),
    ([sys.executable, "scripts/scan_prototype_css.py", str(missing_html), "--format", "json"], "css"),
    ([sys.executable, "scripts/ai_delivery_spec_cli.py", "triage", "--input", str(missing_html)], "triage"),
    ([sys.executable, "scripts/ai_delivery_spec_cli.py", "resume", "--state", str(missing_html)], "resume"),
    ([
        sys.executable, "scripts/ai_delivery_spec_cli.py", "compile-discovery",
        "--contract", str(missing_html), "--transcript", str(missing_html),
        "--decision", "REVIEW_COMPLETE_WITH_GAPS", "--output", str(missing_html.with_suffix('.yaml')),
    ], "compile-discovery"),
):
    completed = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30)
    if completed.returncode != 2 or "Traceback" in completed.stdout + completed.stderr:
        failures.append(f"missing-file {label} path is not controlled: rc={completed.returncode}, out={completed.stdout}{completed.stderr}")

coverage = yaml.safe_load(read("references/domain-coverage.yaml"))
domain_id = coverage["domains"][0]["domain_id"]
completed = subprocess.run(
    [sys.executable, "scripts/query_domain.py", "--domain", domain_id, "--section", "__MISSING_V544__"],
    cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30,
)
if completed.returncode != 1 or "available headings:" not in completed.stdout:
    failures.append(f"section-level domain failure does not list available headings: {completed.stdout}{completed.stderr}")


# 正式候选补接回归：结构化校验器不得泄漏 traceback，PRD 语义校验必须真正进入公共 gate，
# Markdown/frontmatter 权威边界、脚手架词表、模板和发布自检均需有负例或可执行证据。
with tempfile.TemporaryDirectory(prefix="ads-v544-formal-") as temp_name:
    temp = Path(temp_name)
    invalid_yaml = temp / "invalid.yaml"
    invalid_yaml.write_text("- schema-invalid-root\n", encoding="utf-8")
    structured_validators = (
        "validate_acceptance_run.py",
        "validate_change_package.py",
        "validate_product_truth.py",
        "validate_project_domain_capsule.py",
        "validate_requirement_patterns.py",
        "validate_requirement_register.py",
        "validate_review_record.py",
        "validate_spec_config.py",
        "validate_traceability_ledger.py",
    )
    for validator in structured_validators:
        completed = subprocess.run(
            [sys.executable, f"scripts/validators/{validator}", str(invalid_yaml)],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30,
        )
        output = completed.stdout + completed.stderr
        if completed.returncode != 1 or "FAIL:" not in output or "Traceback" in output:
            failures.append(f"{validator} does not fail structurally on an invalid root: rc={completed.returncode}, out={output}")

    no_frontmatter = temp / "no-frontmatter.md"
    no_frontmatter.write_text("# 无 frontmatter 的需求产物\n\n正文。\n", encoding="utf-8")
    distribution = temp / "distribution.docx"
    distribution.write_bytes(b"PK\\x03\\x04 fake distribution copy")
    for profile, option, path, code in (
        ("prd", "--prd", no_frontmatter, "PRD-NO-FRONTMATTER"),
        ("prd", "--prd", distribution, "PRD-NO-FRONTMATTER"),
        ("frame", "--artifact", no_frontmatter, "STAGE-NO-FRONTMATTER"),
        ("frame", "--artifact", distribution, "STAGE-NO-FRONTMATTER"),
    ):
        completed = subprocess.run(
            [sys.executable, "scripts/ai_delivery_spec_cli.py", "gate", "--profile", profile, option, str(path)],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30,
        )
        output = completed.stdout + completed.stderr
        if completed.returncode != 2 or code not in output or "Traceback" in output:
            failures.append(f"{profile} authority guard failed for {path.suffix}: rc={completed.returncode}, out={output}")

    semantic_cases = {
        "dangling": (
            "---\ndocument_language: zh-CN\n---\n# 语义负例\n请详见 FLOW-GHOST-001。\n",
            "PRD-DANGLING-REF",
        ),
        "prefix": (
            "---\ndocument_language: zh-CN\n---\n# 语义负例\n关联号 COR-{code 前3位}。\n枚举：organization/organic/vehicle/venue\n",
            "PRD-ID-PREFIX-COLLISION",
        ),
        "states": (
            "---\ndocument_language: zh-CN\n---\n# 语义负例\n该流程为三态，详见 STM-DEMO-001。\n"
            "## STM-DEMO-001\n| 当前状态 | 下一状态 |\n|---|---|\n| pending | resolved |\n| resolved | pending |\n",
            "PRD-STATE-COUNT-MISMATCH",
        ),
    }
    for name, (raw, expected) in semantic_cases.items():
        document = temp / f"semantic-{name}.md"
        document.write_text(raw, encoding="utf-8")
        standalone = subprocess.run(
            [sys.executable, "scripts/validators/validate_prd_semantics.py", str(document)],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30,
        )
        gate_run = subprocess.run(
            [sys.executable, "scripts/ai_delivery_spec_cli.py", "gate", "--profile", "prd", "--prd", str(document), "--diagnostics", "full", "--max-findings", "200"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30,
        )
        if standalone.returncode != 1 or expected not in standalone.stdout:
            failures.append(f"standalone semantic case {name} did not detect {expected}: {standalone.stdout}{standalone.stderr}")
        if gate_run.returncode != 2 or expected not in gate_run.stdout:
            failures.append(f"public PRD gate did not wire {expected}: {gate_run.stdout}{gate_run.stderr}")

    semantic_warn_cases = {
        "guard": (
            "---\ndocument_language: zh-CN\n---\n# 弱信号负例\n"
            "RULE-SELECT-001 仅 due/ready 可勾选。\n"
            "RULE-SELECT-001 守卫 state ∉ {succeeded/not_due/running}，不可勾选。\n",
            "PRD-GUARD-CONTRADICTION",
        ),
        "enum": (
            "---\ndocument_language: zh-CN\n---\n# 弱信号负例\n系统包含四组：\n- 企业\n- 人员\n- 车辆\n",
            "PRD-ENUM-NOT-DEFINED",
        ),
    }
    for name, (raw, expected) in semantic_warn_cases.items():
        document = temp / f"semantic-warn-{name}.md"
        document.write_text(raw, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, "scripts/validators/validate_prd_semantics.py", str(document)],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30,
        )
        if completed.returncode != 0 or f"WARN: {expected}" not in completed.stdout:
            failures.append(f"semantic weak-signal case {name} did not detect {expected}: {completed.stdout}{completed.stderr}")

    placeholder_probe = subprocess.run(
        [
            sys.executable, "-c",
            "import sys; sys.path.insert(0, 'scripts'); "
            "from stage_contract import has_placeholder; "
            "from validators.prd_structure import PLACEHOLDER; "
            "assert not has_placeholder('资料待补充'); "
            "assert not has_placeholder('数据待补充，提交前补齐'); "
            "assert not has_placeholder('信息待补充完整'); "
            "assert PLACEHOLDER.search('VIEW-TODO-PANEL') is None; "
            "assert has_placeholder('TODO')",
        ],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30,
    )
    if placeholder_probe.returncode != 0:
        failures.append(f"placeholder false-positive regression failed: {placeholder_probe.stdout}{placeholder_probe.stderr}")

    scaffold = temp / "scaffold.html"
    scaffold.write_text(
        '<!doctype html><html lang="zh-CN"><body><main data-testid="page-VIEW-HOME-001">新功能敬请期待</main></body></html>',
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, "scripts/ai_delivery_spec_cli.py", "gate", "--profile", "prototype", "--prototype", str(scaffold)],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30,
    )
    if completed.returncode != 2 or "PROTO-DEMO-SCAFFOLDING-VISIBLE" not in completed.stdout:
        failures.append(f"prototype scaffolding term did not block: {completed.stdout}{completed.stderr}")

for validator, template in (
    ("validate_review_record.py", "references/templates/review-record-template.yaml"),
    ("validate_acceptance_run.py", "references/templates/acceptance-run-template.yaml"),
):
    completed = subprocess.run(
        [sys.executable, f"scripts/validators/{validator}", template],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30,
    )
    if completed.returncode != 0:
        failures.append(f"template is not executable through {validator}: {completed.stdout}{completed.stderr}")

for command, label in (
    ([sys.executable, "scripts/validators/validate_release_package.py"], "release package paths"),
    ([sys.executable, "scripts/validators/validate_validator_wiring.py"], "validator wiring"),
):
    completed = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30)
    if completed.returncode != 0 or "PASS:" not in completed.stdout:
        failures.append(f"{label} self-check failed: {completed.stdout}{completed.stderr}")


broken = ROOT / "maintainer/tests/fixtures/gate-prototype-invalid.html"
english_probe = ROOT / "schemas/gate-result.schema.json"
return_code, english_payload = run_json([
    sys.executable, "scripts/ai_delivery_spec_cli.py", "gate",
    "--profile", "prototype", "--prototype", str(english_probe),
    "--level", "L2", "--language", "auto", "--format", "json",
])
if return_code != 2 or english_payload.get("output_language") != "en-US":
    failures.append(f"English prototype auto-language gate failed: rc={return_code}, payload={english_payload}")
if re.search(r"[\u4e00-\u9fff]", selected_human_text(english_payload)):
    failures.append("English gate selected fields still leak Chinese diagnostics")
if not all(item.get("message_zh") and item.get("message_en") for item in english_payload.get("findings", [])):
    failures.append("gate JSON does not preserve bilingual diagnostic projections")

_return_code, early_payload = run_json([
    sys.executable, "scripts/ai_delivery_spec_cli.py", "gate",
    "--profile", "frame", "--language", "en-US", "--format", "json",
])
if early_payload.get("output_language") != "en-US" or re.search(r"[\u4e00-\u9fff]", selected_human_text(early_payload)):
    failures.append(f"English early-stage gate is not end-to-end localized: {early_payload}")

for command in (
    [sys.executable, "scripts/ai_delivery_spec_cli.py", "gate", "--language", "en-US", "--help"],
    [sys.executable, "scripts/ai_delivery_spec_cli.py", "explain-finding", "PRD-STRUCTURE", "--language", "en-US"],
    [
        sys.executable, "scripts/ai_delivery_spec_cli.py", "gate", "--profile", "requirement",
        "--requirement", str(ROOT / "examples/minimal-v5/requirement-card.md"), "--language", "en-US",
    ],
):
    completed = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=30)
    if re.search(r"[\u4e00-\u9fff]", completed.stdout + completed.stderr):
        failures.append(f"English CLI path leaks Chinese: {' '.join(command)}\n{completed.stdout}{completed.stderr}")


if not broken.is_file():
    failures.append("missing review overlay gate fixture")
else:
    return_code, payload = run_json([
        sys.executable,
        "scripts/quality_gate.py",
        "--profile",
        "prototype",
        "--prototype",
        str(broken),
        "--level",
        "L2",
        "--format",
        "json",
    ])
    codes = {item.get("code") for item in payload.get("findings", [])}
    if payload.get("output_language") != "zh-CN":
        failures.append(f"Chinese HTML lang was not auto-detected: {payload.get('output_language')}")
    if not re.search(r"[\u4e00-\u9fff]", selected_human_text(payload)):
        failures.append("Chinese gate did not return Chinese human-readable diagnostics")
    for expected in (
        "PROTO-DYNAMIC-CLASS-POLLUTION",
        "PROTO-REVIEW-UIACTION-NAMESPACE",
        "PROTO-ORPHAN-HANDLER",
        "PROTO-UNREACHABLE-VIEW",
    ):
        if expected not in codes:
            failures.append(f"prototype gate did not detect {expected}: {sorted(codes)}")
    if return_code != 2:
        failures.append(f"broken review prototype should block, got {return_code}")

    ledger_run = subprocess.run(
        [
            sys.executable,
            "scripts/extract_interaction_ledger.py",
            "--input",
            str(broken),
            "--output",
            "-",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
    )
    if ledger_run.returncode:
        failures.append(f"interaction ledger failed: {ledger_run.stderr}")
    else:
        ledger = json.loads(ledger_run.stdout)
        if "ACT-ORPHAN-SAVE" not in ledger.get("orphanHandlerActions", []):
            failures.append("interaction ledger misses orphan handler action")
        if not any(item.get("unreachable") for item in ledger.get("reachability", [])):
            failures.append("interaction ledger misses explicitly hidden unreachable surface")

    return_code, payload = run_json([
        sys.executable,
        "scripts/ai_delivery_spec_cli.py",
        "gate",
        "--profile",
        "prototype",
        "--prototype",
        str(broken),
        "--prototype-baseline",
        str(broken),
        "--level",
        "L2",
        "--format",
        "json",
    ])
    if payload.get("summary", {}).get("blockers") != 0:
        failures.append(f"inherited baseline finding should not block: {payload.get('summary')}")
    if payload.get("metrics", {}).get("prototype_inherited_findings", 0) < 4:
        failures.append("prototype baseline comparison did not record inherited finding")
    if return_code != 1:
        failures.append(f"inherited prototype debt should remain an explicit GAP, got {return_code}")

spec_schema = json.loads(read("schemas/spec-config.schema.json"))
versions = spec_schema["properties"]["execution"]["properties"]["expected_skill_version"]["enum"]
if "5.4.4" not in versions:
    failures.append("spec config does not accept 5.4.4")

if failures:
    raise SystemExit("\n".join(failures))
print("PASS: v5.4.4 preserves lifecycle language, reaches the requested prototype target, asks once before optional review projection, localizes human labels, separates review stage from review mode, protects full-lifecycle scope, separates permission layers, and requires conditional human-first diagrams")
