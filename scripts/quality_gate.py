#!/usr/bin/env python3
"""Token-free final gate for requirement, PRD, and static prototype artifacts.

The gate is deliberately a goalkeeper, not an author: it reads each supplied
artifact once, reports precise contract gaps, and never generates or fixes
requirements. Browser walkthroughs remain explicit acceptance evidence rather
than a hidden default dependency of this static gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ModuleNotFoundError as exc:  # pragma: no cover - exercised in a clean environment
    missing = getattr(exc, "name", "PyYAML/jsonschema")
    english_startup = any(value == "en-US" for value in sys.argv)
    message = (
        f"Missing runtime dependency {missing}. Run: python -m pip install -r scripts/requirements.txt"
        if english_startup else
        f"缺少运行依赖 {missing}。请先执行：python -m pip install -r scripts/requirements.txt"
    )
    print(message, file=sys.stderr)
    raise SystemExit(4) from exc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR_DIR = SCRIPT_DIR / "validators"
if str(VALIDATOR_DIR) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_DIR))

from scan_prototype_css import scan as scan_prototype_css
from prd_structure import analyze as analyze_prd_structure
from validate_acceptance_run import validate_evidence_refs
from validators.validate_coding_agent_contract import (
    BASE_AREAS,
    ID_RULES,
    STRUCTURED_AC_FIELDS,
    has_any,
)
from validators.validate_prd_quality import LEVELS, TERMS
from validators.validate_prd_semantics import run_semantic_checks
from gate_handoff_checks import HandoffChecks
from gate_prd_checks import PRDChecks
from gate_prototype_checks import PrototypeChecks, _balanced_javascript


ROOT = SCRIPT_DIR.parent
REGISTER_SCHEMA = ROOT / "schemas" / "requirement-register.schema.json"
INTAKE_SCHEMA = ROOT / "schemas" / "requirement-intake.schema.json"
HANDOFF_SCHEMA = ROOT / "schemas" / "agent-handoff.schema.json"
ACCEPTANCE_SCHEMA = ROOT / "schemas" / "acceptance-run.schema.json"
MAIN_SECTION_ALIASES = (
    ("背景/目标", (r"背景", r"目标", r"background", r"problem.+goal", r"objective")),
    ("准入/范围", (r"需求准入", r"准入.*范围", r"intake.+scope", r"scope")),
    ("角色", (r"角色", r"roles?", r"actors?")),
    ("角色旅程", (r"角色旅程", r"用户旅程", r"role journey", r"user journey")),
    ("业务流程/状态", (r"业务流程", r"状态机", r"business flow", r"workflow.+state")),
    ("模块规格", (r"分模块功能需求", r"模块规格", r"module requirements?", r"module specification")),
    ("验收", (r"验收方案", r"验收", r"acceptance plan", r"acceptance")),
)
ANNEX_SECTION_ALIASES = (
    ("字段字典", (r"字段字典", r"field dictionary")),
    ("规则/状态", (r"规则与状态", r"rules?.+state")),
    ("API/事件", (r"api", r"接口", r"event.+integration")),
    ("机器验收", (r"机器可读验收", r"machine-readable acceptance", r"structured acceptance")),
    ("双向追溯", (r"双向追溯", r"bidirectional trace")),
    ("禁止推断", (r"禁止推断", r"forbidden invention", r"do not infer")),
)
STATUSES = {
    0: "PASS",
    1: "REVIEW_COMPLETE_WITH_GAPS",
    2: "BLOCKED",
    3: "BLOCKED_BY_P0_UNKNOWN",
}
STAGE_ORDER = {
    "inventory": 0,
    "clarify": 1,
    "specify": 2,
    "review": 3,
    "baseline": 4,
    "prototype": 4,
    "implementation": 5,
    "acceptance": 6,
    "closed": 7,
}

NOT_PROVEN_BY_STATIC_GATE = (
    "业务与领域规则已经客户或权威来源确认",
    "原型在真实浏览器中的交互、视觉、可访问性与多端适配",
    "视觉权威与视觉锁已经确认（存量基线、绿地默认或 DEC-AESTHETIC-*）",
    "代码实现、数据迁移、安全、性能、部署与运行稳定性",
    "验收用例已经实际执行并形成签认证据",
)
NOT_PROVEN_BY_STATIC_GATE_EN = (
    "customer or authoritative-source confirmation of business and domain rules",
    "prototype interaction, visual quality, accessibility and responsive behavior in a real browser",
    "confirmed visual authority and visual lock (existing baseline, greenfield default or DEC-AESTHETIC-*)",
    "implementation, data migration, security, performance, deployment and runtime stability",
    "executed acceptance cases with signed evidence",
)


def not_proven_for(gate: "Gate", language: str = "zh-CN") -> list[str]:
    """Keep static-gate boundaries honest while closing claims backed by valid ARUN evidence."""
    english = language.casefold().startswith("en")
    items = list(NOT_PROVEN_BY_STATIC_GATE_EN if english else NOT_PROVEN_BY_STATIC_GATE)
    if gate.metrics.get("prototype_browser_evidence"):
        items.remove(NOT_PROVEN_BY_STATIC_GATE_EN[1] if english else NOT_PROVEN_BY_STATIC_GATE[1])
        items.append(
            "The browser ARUN proves recorded interactions only; uncovered visual, accessibility and responsive behavior remains unproven"
            if english else
            "浏览器 ARUN 已证明其记录范围内的交互结果；未覆盖的视觉、可访问性与多端适配仍未证明"
        )
    if gate.metrics.get("acceptance_run_conclusive"):
        items.remove(NOT_PROVEN_BY_STATIC_GATE_EN[4] if english else NOT_PROVEN_BY_STATIC_GATE[4])
        items.append(
            "The supplied ARUN has executable signed evidence; acceptance scope outside that record remains unproven"
            if english else
            "已提供的 ARUN 已执行并形成可解析签认证据；未纳入该记录的验收范围仍未证明"
        )
    return items


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    artifact: str
    message: str
    ref: str = ""
    cause: str = ""
    how_to_fix: str = ""
    repair_example: str = ""
    affected_consumers: tuple[str, ...] = ()
    related_refs: tuple[str, ...] = ()
    binding_source_refs: tuple[str, ...] = ()


FINDING_GUIDANCE: dict[str, tuple[str, str]] = {
    "GATE-MISSING-INPUT": (
        "所选门禁缺少必需输入。",
        "按 finding 指示补充对应的 --requirement、--prd、--prototype、--inventory 或 --manifest 参数。",
    ),
    "GATE-NOT-FILE": (
        "输入路径不是可读文件。",
        "修正路径并确认文件存在，然后重跑同一命令。",
    ),
    "REQ-PARSE": (
        "需求登记文件不是可读的 UTF-8 YAML。",
        "该 profile 只接收 YAML 需求登记册：修复 YAML 缩进、引号或编码；"
        "若输入是 Markdown 需求卡/PRD，请改用 --profile prd --prd <文件>。",
    ),
    "REQ-SCHEMA": (
        "需求登记文件不符合 JSON Schema。",
        "按 finding.ref 定位字段，并参考 requirement-register-template.yaml 修复结构。",
    ),
    "INTAKE-SCHEMA": (
        "输入是单条需求 intake 卡，但不符合 intake 合同；登记册与 intake 卡是两种不同工件。",
        "按 finding.ref 定位字段，参考 requirement-intake-template.yaml 补齐 intake 字段；"
        "若要提交多条需求登记册，改用 requirement-register-template.yaml 并提供 requirements 列表。",
    ),
    "PROTO-DEMO-SCAFFOLDING-VISIBLE": (
        "原型可见文本残留验收演示脚手架，会被客户误读为产品功能。",
        "删除 finding.ref 指示的演示文案（验收场景/验收样本/E2E CONSOLE/体验身份/继承预览等），只保留真实业务内容。",
    ),
    "PROTO-NESTED-PRODUCT-IFRAME": (
        "原型用本地 iframe 嵌套另一个 HTML 页面，静态门禁无法证明嵌套页的交互合同。",
        "把嵌套页内容并入当前原型的 page-VIEW-* 结构，或作为独立原型文件一并提交门禁。",
    ),
    "PROTO-IFRAME-UNSAFE-SCHEME": (
        "iframe 使用 data/javascript/file 等不可审计或可执行的高风险地址。",
        "移除该 iframe；外部系统只允许 HTTPS，并按远程集成合同声明 INT-*、降级和浏览器安全属性。",
    ),
    "PROTO-INSECURE-REMOTE-IFRAME": (
        "远程 iframe 使用明文 HTTP，传输内容和凭据边界不可接受。",
        "改用 HTTPS；若对方不支持 HTTPS，移除嵌入并设计明确的外部跳转或降级路径。",
    ),
    "PROTO-REMOTE-IFRAME-UNDECLARED": (
        "远程 iframe 没有声明集成归属、失败降级和最小浏览器安全边界。",
        "补齐 data-integration-ref=INT-*、data-fallback、title、sandbox 和 referrerpolicy；L2+ 缺任一项均阻断。",
    ),
    "PROTO-REMOTE-IFRAME-UNVERIFIED": (
        "远程 iframe 的静态合同完整，但门禁无法证明外部内容、登录态、网络可达性和运行时交互。",
        "在目标网络和角色登录态下执行浏览器 ARUN-*，记录成功、失败降级和证据；静态 GAP 不得冒充已验收。",
    ),
    "PRD-STATE-SEMANTIC-POLLUTION": (
        "状态机表的当前状态/下一状态列写入了 API/FLD/ACT 等工程 ID，状态语义被污染。",
        "状态列只写业务状态名（如 draft、active）；工程 ID 移回动作/规则/接口列或附录。",
    ),
    "PRD-DUPLICATE-STABLE-ID-DEFINITION": (
        "同一个稳定 ID 在一个或多个权威定义表中被重复定义，开发与测试无法判断哪一行生效。",
        "只保留一处定义；其他位置改为引用，确属不同对象时分配新的稳定 ID。",
    ),
    "PRD-DANGLING-REF": (
        "正文引用了全文没有定义位的稳定 ID，按 ID 追溯会断链。",
        "在标题、表格首列、列表项或 ID（…）注解中补该 ID 的定义位；若为笔误则修正引用。",
    ),
    "PRD-ID-PREFIX-COLLISION": (
        "截断式 ID 生成规则作用到同文档 code 枚举后多对一，生成的关联号不再唯一。",
        "改用完整 code 或保证截断后唯一；按 finding 给出的碰撞组逐一核对。",
    ),
    "PRD-STATE-COUNT-MISMATCH": (
        "文中“N 态”措辞与对应 STM-* 状态机表覆盖的状态数不一致。",
        "同步措辞或状态机表，使二者一致。",
    ),
    "PRD-GUARD-CONTRADICTION": (
        "同一动作的许可状态集与守卫拒绝状态集显式互斥，其余状态可能得到相反结论。",
        "对齐规则与守卫的状态集合，明确允许、拒绝和非法转换结果。",
    ),
    "PRD-ENUM-NOT-DEFINED": (
        "基数表述与枚举数量不符，或枚举值在状态机/规则中没有语义定义。",
        "同步基数与枚举清单，并为每个业务枚举值补状态机或规则语义。",
    ),
    "PRD-NO-FRONTMATTER": (
        "输入不是带 YAML frontmatter 的 Markdown，机器可校验性已经丢失。",
        "先在 Markdown + frontmatter 形态完成基线，再导出 docx/PDF 分发副本。",
    ),
    "HANDOFF-BINDING-TERM-MISSING": (
        "PRD 声明的绑定词没有同时出现在 PRD 正文和原型可见文本中，跨端用词不一致。",
        "让 finding.ref 指示的绑定词原样出现在 PRD 正文和原型可见文案中，或在评审后收窄 binding_terms 声明。",
    ),
    "PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT": (
        "同一主题同时登记为已确认决策和未关闭未知项，基线语义自相矛盾。",
        "二选一：关闭对应 UNK-* 并同步 open_p0_unknown_ids，或撤回该决策条目并重新登记为开放未知项。",
    ),
    "PRD-UNKNOWN-METADATA-DRIFT": (
        "同一未知项在机器 frontmatter 与人类正文中的优先级、状态或阻断阶段不一致。",
        "以责任人最新确认结果为准，同步 unknowns、open_p0_unknown_ids 与正文未知项表后重跑门禁。",
    ),
    "HANDOFF-AESTHETIC-UNDECIDED": (
        "L3/L4 交接没有声明视觉权威与视觉锁，跨页面风格可能漂移。",
        "存量小迭代记录 visual_authority=existing；绿地记录 greenfield_default；品牌化方案可引用 DEC-AESTHETIC-*，并提供 design_lock_ref。",
    ),
    "HANDOFF-STEP-NOT-IN-PRD": (
        "implementation_step_refs 引用了 PRD 中不存在的 STEP-*，交接包无法回到权威基线。",
        "删除幽灵引用或在 PRD 中补齐经评审的 STEP-* 实施卡，再同步 manifest 与工作包。",
    ),
    "HANDOFF-PACKET-STEP-MISSING": (
        "manifest 声明了 STEP-*，但工作包正文没有该步骤，Coding Agent 无法取得实施语义。",
        "在对应 packet 正文显式引用 STEP-* 并保留其入口、处理、守卫、结果、恢复和验收语义。",
    ),
    "HANDOFF-STEP-INCOMPLETE": (
        "PRD 的实施步骤卡缺少可独立实现和验收的核心语义。",
        "按 finding.message 补缺失字段；确实无事件、无状态变化或无需恢复时也要显式写“无”及责任边界。",
    ),
    "HANDOFF-STEP-CONTRACT-MISSING": (
        "交接状态已声明开发就绪，但 packet 没有 implementation_step_refs。",
        "为每个开发就绪 packet 列出其实现的 STEP-*；若尚未形成完整实施卡，降回 review_ready。",
    ),
    "HANDOFF-PRD-STEP-NOT-PACKETED": (
        "PRD 已定义实施步骤，但开发就绪交接包没有覆盖全部步骤。",
        "把 finding.ref 对应 STEP-* 分配到一个明确 owner 的 packet，或经评审从本次范围移除并重建基线。",
    ),
    "STAGE0-DISPOSITION-MISSING": (
        "Stage 0 台账的页面类条目缺少 disposition，存量页面处置方式未定。",
        "为该条目补 disposition：adopt_page / inherit_layout / rebuild_interaction / reuse_component / discard。",
    ),
    "STAGE0-LEGACY-INVENTORY": (
        "Stage 0 台账仍是旧版按 roles/views/actions 等分栏保存的结构，缺少当前逐项审计合同。",
        "将旧分栏逐项迁入 items；每项补齐 type、source_ref、source_location、classification，推断项再绑定有 owner 的 RBATCH-*。",
    ),
    "STAGE0-PLACEHOLDER": (
        "Stage 0 文件仍是未填写模板，模板结构不能证明真实页面、动作、状态或来源已经盘点。",
        "把花括号、待指定和全零 hash 替换为真实来源事实，无法确认的内容登记有 owner 的 UNK-*。",
    ),
    "STAGE0-REACHABILITY-NOT-DECLARED": (
        "Stage 0 已发现核心动作或处理器，但还没有结构化盘点关键链可达性。",
        "旧台账可继续使用；只为本轮关键链补 critical_chains，按来源记录处理器、输出、下一入口/守卫与恢复路径，未知登记 UNK-*。",
    ),
    "STAGE0-CHAIN-CONTRACT-INVALID": (
        "关键链结构不完整，无法审计动作到下一入口的真实可达性。",
        "按 stage0 模板补齐当前链的 action、processing、四类输出、next entry/guard、reachability、来源和 break_refs，不得发明目标规则。",
    ),
    "STAGE0-CHAIN-REACHABILITY-CONTRADICTION": (
        "链路声明可达或终止，但处理器、输出、下一入口/守卫仍缺失或未知。",
        "以来源事实修正 reachability；不能确认时改为 unknown/broken，并登记有 owner 的断裂记录。",
    ),
    "STAGE0-CHAIN-REF-TYPE-MISMATCH": (
        "关键链引用存在但对象类型不匹配，无法证明 action、处理器或输出维度。",
        "让 action_ref 指向 action，processing_refs 指向 handler/system_process/process，并把对象、状态、版本、身份分别引用到对应盘点项。",
    ),
    "STAGE0-CHAIN-UNRESOLVED-UNTRACKED": (
        "关键链存在缺失或未知，却没有进入断裂清单。",
        "建立 INV-BREAK-* 并从 link/recovery 和 chain.break_refs 回链；unknown 断裂再绑定 P0 UNK-*、owner 与 blocks_stage。",
    ),
    "STAGE0-EMPTY-BREAK-REGISTER": (
        "关键链仍有未评估、缺失、未知或断裂，但断裂清单为空。",
        "补充来源化 INV-BREAK-*；只有所有声明链均已评估且各 link/recovery 有证据可达或明确不适用时才允许空清单。",
    ),
    "STAGE0-RECOVERY-CONTRACT-INCOMPLETE": (
        "关键链没有分别盘点失败、退回、重试和补偿路径。",
        "按来源把四类路径标为 observed/broken/unknown/not_applicable；未知不能写成无需求，不适用须说明理由。",
    ),
    "STAGE0-CRITICAL-BREAK-NOT-OWNED": (
        "关键链未知断裂没有责任人和阻断边界。",
        "为 unknown 断裂登记 UNK-*、P0、owner 和 blocks_stage；Stage 0 只记录未知，不替 owner 决定目标规则。",
    ),
    "PRD-STRUCTURE": (
        "文档虽然包含标题或关键词，但没有可验证的统一 PRD 结构。",
        "按统一 PRD 模板补齐真实业务叙述或工程附录，不要复制空标题。",
    ),
    "PRD-TOO-THIN": (
        "当前交付等级所需的页面、规则或验收细节不足。",
        "补齐适用合同，不要用空标题或关键词填充。",
    ),
    "PRD-LANGUAGE-DRIFT": (
        "文档结构语言与声明的用户语言不一致，会直接降低评审与开发可读性。",
        "按 frontmatter document_language 统一 H1/H2/H3、正文、表头与测试叙述；ID、代码、API/字段名和专名保持原样。",
    ),
    "PRD-MODULE-SLICE-INCOMPLETE": (
        "模块规格被拆散或缺少实现/测试所需的本地闭环。",
        "在对应 MOD-* 章节就近补齐目标、主/异常路径、页面动作、字段权限、规则状态、指标、恢复、验收和未知项。",
    ),
    "PROTO-NO-PAGE-ANCHOR": (
        "原型缺少可追溯、可测试的稳定页面标识。",
        "为每个页面根节点增加唯一 data-testid=\"page-VIEW-*\"。",
    ),
    "PROTO-NO-REGION-ANCHOR": (
        "复杂原型没有把页面布局拆成可追溯、可测试的业务区域。",
        "为复合页、组装器、门户或多视图原型的关键区域增加唯一 data-testid=\"region-REG-*\"。",
    ),
    "PROTO-BROWSER-EVIDENCE-MISSING": (
        "L3/L4 静态契约已检查，但缺少真实浏览器逐动作执行证据。",
        "按原型内 data-ac 生成 ARUN-*，在真实浏览器执行后用 --acceptance-run 重新校验；缺证据时不得声明原型完成。",
    ),
    "PROTO-BROWSER-EVIDENCE-INCOMPLETE": (
        "浏览器验收记录没有覆盖原型声明的全部 AC，或没有形成可接受结论。",
        "补跑缺失 AC，填写 actual_result、evidence_refs、浏览器环境和签署结论，再重跑门禁。",
    ),
    "PROTO-UNHANDLED-ACTION": (
        "原型动作没有可观察的分发路径。",
        "将 data-action 绑定到唯一处理器，并产生页面、弹窗、状态或数据结果。",
    ),
    "PROTO-ORPHAN-HANDLER": (
        "动作注册表保留了没有源模板入口的处理器，存量交互可能在迭代中丢失。",
        "恢复对应 data-action 控件、删除确认无用的死代码，或将批准移除记录到原型锁；不要只让处理器留在脚本中。",
    ),
    "PROTO-UNREACHABLE-VIEW": (
        "页面、弹窗或抽屉被显式隐藏，但没有静态可发现的入口或路由。",
        "为该表面增加稳定 data-action/data-view 路由并验证可达性，或经批准删除该死页面。",
    ),
    "PROTO-REVIEW-UIACTION-NAMESPACE": (
        "评审开关等纯界面动作错误占用了业务 ACT-* 命名空间。",
        "将其改为 UIACT-REVIEW-*，并保证切换前后业务动作、状态、字段、指标和表单值不变。",
    ),
    "PROTO-METRIC-ID-SEMANTIC-COLLISION": (
        "同一个 METRIC-* 被多个业务含义复用，公式、来源和验收无法一一追溯。",
        "不同业务含义分配不同 METRIC-*；同一指标重复展示时使用相同 data-metric-label 和同一口径定义。",
    ),
    "PROTO-METRIC-LABEL-MISSING": (
        "重复指标卡没有足够的语义标签，静态门禁无法证明它们是否为同一指标。",
        "为重复 data-metric 增加稳定 data-metric-label，或为不同含义分配不同 METRIC-*。",
    ),
    "PROTO-DYNAMIC-METRIC-ID-REUSE": (
        "动态指标工厂用一个固定 METRIC-* 承载多个运行时标签，运行后会把不同口径压成一个 ID。",
        "让工厂接收并输出每个指标自己的稳定 METRIC-*，或改为按已定义指标配置渲染。",
    ),
    "PROTO-UNKNOWN-CONTRACT-INCOMPLETE": (
        "原型只显示 UNK-* 或“待确认”，却没有把未知项绑定到可关闭的责任合同。",
        "为每个 data-unk/注册表项补 priority、owner、blocks_stage、affected_refs 和 fallback；评审前按依赖批量向责任人澄清。",
    ),
    "PROTO-UNKNOWN-CONFIRMED-CONFLICT": (
        "同一原型对象同时携带已确认状态和开放 UNK-*，属于证据状态冲突。",
        "依据 DEC/source 裁决：已确认则关闭并移除当前 data-unk；仍未知则撤销 confirmed，保留 owner、阻断阶段和回退。",
    ),
    "PROTO-REVIEW-LINKAGE-MISSING": (
        "评审编号与右侧说明卡没有稳定双向关联。",
        "两侧使用相同 data-review-id，或在目标卡上声明同值 data-review-target，并补浏览器双向定位证据。",
    ),
    "PROTO-REVIEW-SELECTION-NOT-SYNCED": (
        "评审编号点击后没有可验证的左右同步选中状态。",
        "处理器读取 data-review-id，同时更新两侧 aria-current/选中样式，并用 ARUN-* 证明点击、滚动和框选。",
    ),
    "PROTO-REVIEW-LENS-COSMETIC": (
        "共识/前端/后端/测试镜头只有按钮外观变化，没有角色所需内容差异。",
        "用 data-review-role 标记控件、data-review-lens 标记对应内容；镜头只改变密度，不得改变事实。",
    ),
    "PROTO-REVIEW-WORKSPACE-LEGACY": (
        "旧评审叠加仍围绕页面编号/卡片组织，无法证明接收者能按业务旅程和角色任务独立完成交接。",
        "迁移为导读、旅程、单步聚焦、页面核对和验收五种按需模式，并嵌入同基线的 review-workspace-manifest。",
    ),
    "PROTO-REVIEW-WORKSPACE-MANIFEST-INVALID": (
        "评审工作台没有唯一、可解析的同源投影索引。",
        "在同一 HTML 内嵌 application/json 的 review-workspace-manifest，并按 review-workspace schema 校验。",
    ),
    "PROTO-REVIEW-LANGUAGE-MISMATCH": (
        "评审 manifest 与 HTML 声明了不同的人类语言。",
        "让 manifest.language 与 html[lang] 跟随用户语言；稳定 ID 和机器枚举保持原值，不用关键词禁令代替人工语言复核。",
    ),
    "PROTO-REVIEW-ROLE-PACKET-INCOMPLETE": (
        "角色镜头只是内容过滤或摘要，没有覆盖该角色启动工作所需的完整槽位。",
        "按 product/frontend/backend/qa 的 data-review-slot 合同补齐工作包；未知语义绑定 UNK-*，不要编造技术决定。",
    ),
    "PROTO-REVIEW-ROLE-APPLICABILITY-MISMATCH": (
        "角色是否受影响的机器索引与人类可见工作包不一致。",
        "受影响角色使用 active 并补齐槽位；确实不受影响时使用 not_affected、清空合同槽位并显示具体原因。",
    ),
    "PROTO-REVIEW-CONFIRMED-NO-EVIDENCE": (
        "评审步骤被标为已确认，却没有 SRC-* 或 DEC-* 作为确认依据。",
        "补充可核对来源/决定；只有原型现状、模型建议或演示行为时降为 proposed/unknown 并绑定 UNK-*。",
    ),
    "PROTO-REVIEW-VERIFICATION-NO-EVIDENCE": (
        "评审步骤把实现写成已检查、验收或失败，却没有 EVD-* / ARUN-* 运行证据。",
        "保持 verification_status=not_run，或绑定真实运行证据后再按实际证据等级升级；不得用作者自述替代。",
    ),
    "PROTO-REVIEW-STATUS-AXIS-HIDDEN": (
        "业务确认状态或验证证据状态只藏在机器清单里，人类接收者看不到。",
        "在每个 STEP 工作包中分别显示 business 与 verification 状态轴、原值和本地语言含义。",
    ),
    "PROTO-REVIEW-STATUS-AXIS-DRIFT": (
        "人类可见状态与 review manifest 的状态值不一致。",
        "从同一 STEP 记录投影两条状态轴，禁止在 HTML 中手写另一套状态。",
    ),
    "PROTO-REVIEW-STATUS-AXIS-DUPLICATE": (
        "同一 STEP 状态轴在人类界面重复出现，可能同时展示相互冲突的结论。",
        "每个 STEP/axis 只投影一次；由 manifest 的同一记录生成标签并删除陈旧副本。",
    ),
    "PROTO-REVIEW-VERIFICATION-ARUN-UNRESOLVED": (
        "评审步骤声称浏览器、集成、验收或失败证据，但引用的 ARUN 未在本次门禁中提供。",
        "保持 not_run，或把对应 ARUN 文件随门禁一起提供；伪造 EVD/ARUN 标识不能升级证据等级。",
    ),
    "PROTO-REVIEW-VERIFICATION-LEVEL-UNPROVED": (
        "已提供的 ARUN 环境或结论不足以支持评审步骤声明的验证等级。",
        "按真实 ARUN 环境、失败记录和有证据签署结论降级或补测，不得越级宣传。",
    ),
    "PROTO-REVIEW-VERIFICATION-BASELINE-DRIFT": (
        "评审步骤引用了其他基线版本的验收记录，旧证据不能证明当前语义。",
        "提供 baseline_version 与当前 review baseline 完全一致的 ARUN，或把验证状态降回真实等级。",
    ),
    "PROTO-REVIEW-VERIFICATION-AC-UNPROVED": (
        "ARUN 存在但没有覆盖当前 STEP 对应的 TEST→AC，属于无关证据借用。",
        "让该 STEP 的 QA 场景绑定 TEST/AC，并随门禁提供覆盖对应 AC 的 ARUN；accepted 必须通过全部相关 AC。",
    ),
    "PROTO-REVIEW-MODEL-COVERAGE-AMBIGUOUS": (
        "旅程没有说明状态机或数据流是遗漏还是确实不适用。",
        "分别登记 FLOW/STM/INT|EVT|ENT 引用；确实无状态或数据流时在 not_applicable 显式声明。",
    ),
    "PROTO-REVIEW-MODEL-NOT-VISIBLE": (
        "旅程引用了流程、状态机或数据流，但人类工作台没有对应可见模型。",
        "分别投影 data-review-model 与 data-review-model-ref；不要用一张万能流程图或隐藏 JSON 冒充人类走读。",
    ),
    "PROTO-REVIEW-MODEL-NA-HIDDEN": (
        "状态机或数据流被声明为不适用，但人类看不到原因。",
        "使用 data-review-model-na 显示具体不适用理由；无法判断时改为 active 并登记 UNK-*。",
    ),
    "PROTO-REVIEW-SCENARIO-NOT-VISIBLE": (
        "验收场景只存在于 manifest，测试无法从工作台定位 TEST→AC。",
        "为每个场景显示 data-review-scenario=TEST-* 与 data-review-acceptance-ref=AC-*，并呈现覆盖 STEP 和证据要求。",
    ),
    "PROTO-REVIEW-CONTRACT-REF-HIDDEN": (
        "角色工作包没有显示其规则、状态或 AC 引用，摘要会退化成第二份孤立说明。",
        "把 manifest.contract_refs 作为可见引用或可展开来源清单呈现；业务正文继续以 PRD/Truth 为权威。",
    ),
    "PROTO-REVIEW-RISK-NOT-TESTED": (
        "步骤声明了边界、权限、恢复或网络并发风险，但验收场景未覆盖。",
        "从同一 TEST/AC 补充该风险维度、双结果与证据要求，不要在 HTML 另写一套测试。",
    ),
    "PROTO-REVIEW-MODE-MISSING": (
        "评审信息被塞进单一长列表或抽屉，不能按接收者当前任务渐进展开。",
        "按适用范围提供 orientation/journey/focus/page/acceptance，并让复杂主链从旅程进入、单次只聚焦一个 STEP-*。",
    ),
    "PROTO-REVIEW-COMPACT-OVERLAY": (
        "窄屏评审面板会遮住产品上下文，无法同时完成页面核对。",
        "使用 fullscreen-switcher 在产品与评审之间切换，保留当前 STEP 与返回目标，再用浏览器证据验证。",
    ),
    "PROTO-REVIEW-BASELINE-DRIFT": (
        "评审工作台与本次 PRD 不是同一内容基线，角色说明可能已经过期。",
        "从权威 PRD 重新生成投影索引并写入其 SHA-256；同一 CHG 内同步人类投影与 machine handoff。",
    ),
    "PRD-FACET-REQUIRES-L2": (
        "轻量需求卡启用了数据上报、系统集成、批量导入导出或高风险治理规格，L1 无法承载完整跨角色合同。",
        "升级到 L2 统一 PRD，并补齐适用的来源、映射、状态、异常、审计与验收；不要用关键词把高风险切片伪装成 L1。",
    ),
    "PROTO-DYNAMIC-CLASS-POLLUTION": (
        "业务描述被动态拼进 CSS class，可能造成样式失效、选择器污染或未转义内容进入 DOM。",
        "class 只保留固定语义 token；把说明写入转义后的 textContent/单元格，并核对表头与数据列顺序。",
    ),
    "PROTO-JS-SYNTAX": (
        "静态检查发现 JavaScript 语法错误。",
        "修复对应脚本块并检查文档尾部完整性。",
    ),
}

PREFIX_GUIDANCE: tuple[tuple[str, str, str], ...] = (
    ("CUSTOM-", "项目本地扩展规则无效或未满足。", "检查 custom/validators 下的声明式 YAML；只允许正则规则，不执行本地 Python。"),
    ("CUST-", "项目本地需求规范未满足。", "按本地规则的 message 与 ref 修复工件，必要时由团队规范负责人调整规则。"),
    ("AUTH-", "需求来源或写入面存在未裁决冲突。", "由解释责任人创建 DEC-CONFLICT-*，限定适用范围并重新投影受影响工件。"),
    ("HANDOFF-", "交接包与需求基线或其他投影不一致。", "对齐基线 hash、责任人、稳定 ID 和验收引用，不要在交接包中另造规则。"),
    ("AI-", "AI 产品能力缺少适用的运行时治理合同。", "补充输入输出、版本、权限、人工门、回退、评测和观测引用。"),
    ("ACCEPTANCE-", "验收执行记录无效或与其结论矛盾。", "按 acceptance-run schema 修复执行环境、实际结果、证据、缺陷和签署结论。"),
    ("PROTO-REVIEW-STEP-ANCHOR", "评审 STEP 与其人类工作包 DOM 锚点不唯一或未闭合。", "让每个 manifest STEP 恰好绑定一个同 ID 的 data-review-step 与 manifest.dom_anchor；移除幽灵或重复工作包。"),
    ("PROTO-REVIEW-LENS-", "角色镜头只有外观或内容标签，没有形成真实可达的角色投影。", "读取 data-review-role 并更新根容器 data-review-active-role；保留关联角色入口并用浏览器证据验证。"),
    ("PROTO-CSS-", "CSS 污染可能隐藏或破坏交互状态。", "移除全局 !important 污染，并将可见性规则限制在所属组件和 data-state。"),
    ("PROTO-", "原型缺少可测试交互或状态合同。", "使用稳定 data-testid/data-action/data-state/data-field 和可见结果修复对应元素。"),
    ("PRD-", "PRD 缺少当前交付阶段所需的需求合同。", "按引用位置补齐经确认的规则、稳定 ID、异常和验收，不得发明值。"),
    ("REQ-", "需求生命周期记录不完整或不一致。", "修复对应字段并保留稳定 ID、来源、决策和审计历史。"),
)

EN_FINDING_GUIDANCE: dict[str, tuple[str, str]] = {
    "GATE-MISSING-INPUT": ("The selected gate is missing a required input.", "Provide the input named by the finding and rerun the same command."),
    "GATE-NOT-FILE": ("An input path is not a readable file.", "Correct the path, confirm the file exists, and rerun the same command."),
    "REQ-PARSE": ("The requirement register is not readable UTF-8 YAML.", "Repair YAML syntax or use the PRD profile for a Markdown artifact."),
    "REQ-SCHEMA": ("The requirement register violates its JSON Schema.", "Use finding.ref to repair the field against the requirement-register template."),
    "INTAKE-SCHEMA": ("The requirement intake card violates its contract.", "Use finding.ref and the requirement-intake template to repair the missing or invalid field."),
    "PRD-DANGLING-REF": ("A stable ID is referenced but has no definition site in the PRD.", "Define the ID at an authoritative location or correct the reference."),
    "PRD-ID-PREFIX-COLLISION": ("A truncated ID rule maps multiple enum values to the same ID.", "Use the full code or another collision-free stable-ID rule."),
    "PRD-STATE-COUNT-MISMATCH": ("A stated state count differs from the referenced state machine.", "Align the claim and the state-machine rows."),
    "PRD-GUARD-CONTRADICTION": ("An action's allow set conflicts with its guard reject set.", "Align the allowed, rejected and illegal transition sets."),
    "PRD-ENUM-NOT-DEFINED": ("A cardinality or enum contract is incomplete or inconsistent.", "Align counts and define every business enum in a rule or state machine."),
    "PRD-DUPLICATE-STABLE-ID-DEFINITION": ("A stable ID is defined more than once across authoritative PRD tables.", "Keep one definition; turn other occurrences into references or assign a new stable ID."),
    "PRD-NO-FRONTMATTER": ("The input is not Markdown with YAML front matter.", "Baseline in Markdown + front matter before exporting distribution copies."),
    "PRD-UNKNOWN-METADATA-DRIFT": ("The same unknown conflicts across machine and human projections.", "Synchronize priority, status and blocking stage in front matter, the open P0 index and the human unknown table."),
    "HANDOFF-STEP-NOT-IN-PRD": ("A packet references a STEP-* that is absent from the PRD baseline.", "Remove the ghost reference or baseline the complete STEP-* card before handoff."),
    "HANDOFF-PACKET-STEP-MISSING": ("The manifest declares a STEP-* that is absent from the packet body.", "Reference the STEP-* in the packet and preserve its implementation semantics."),
    "HANDOFF-STEP-INCOMPLETE": ("A PRD implementation step lacks a required implementation facet.", "Complete the facet named in the finding; explicitly state none when it is genuinely not applicable."),
    "HANDOFF-STEP-CONTRACT-MISSING": ("A ready-for-implementation packet has no implementation_step_refs.", "List every implemented STEP-* or return the packet to review_ready."),
    "HANDOFF-PRD-STEP-NOT-PACKETED": ("A PRD STEP-* is not covered by any ready implementation packet.", "Assign it to an owned packet or remove it from scope through an approved baseline change."),
    "PRD-STRUCTURE": ("The document does not contain a verifiable unified-PRD structure.", "Add real business content using the unified PRD template; do not copy empty headings."),
    "STAGE0-PLACEHOLDER": ("The Stage 0 artifact is still an unfilled template and proves no inventory facts.", "Replace placeholders and zero hashes with sourced observations, or register owned UNK-* items."),
    "STAGE0-REACHABILITY-NOT-DECLARED": ("Stage 0 found a core action or handler but has no structured critical-chain reachability inventory.", "Keep the legacy inventory compatible, then add only the in-scope critical chains with sourced processing, outputs, next entry/guard and recovery paths."),
    "STAGE0-CHAIN-CONTRACT-INVALID": ("The critical-chain contract is incomplete and cannot prove reachability.", "Complete the sourced action, processing, four output facets, next entry/guard, reachability and break references without inventing target rules."),
    "STAGE0-CHAIN-REACHABILITY-CONTRADICTION": ("A chain claims reachable or terminal while required processing, outputs or successor evidence is missing.", "Correct the observed verdict; use unknown/broken plus an owned break record when the source cannot prove reachability."),
    "STAGE0-CHAIN-REF-TYPE-MISMATCH": ("A critical-chain reference resolves to the wrong inventory object type.", "Point action_ref to an action, processing_refs to handlers/processes, and each output facet to the matching object, state, version or identity item."),
    "STAGE0-CHAIN-UNRESOLVED-UNTRACKED": ("A critical-chain gap is not linked to the reachability-break register.", "Create an INV-BREAK-* record and link it from the link/recovery and chain; bind an owned P0 UNK-* when it is unknown."),
    "STAGE0-EMPTY-BREAK-REGISTER": ("A declared critical chain still has unassessed, missing, unknown or broken facets but its break register is empty.", "Record sourced breaks; an empty register is valid only when every declared link and recovery path is explicitly assessed."),
    "STAGE0-RECOVERY-CONTRACT-INCOMPLETE": ("Failure, return, retry and compensation are not separately inventoried.", "Mark each path observed, broken, unknown or not_applicable from source evidence; explain not_applicable and register unknowns."),
    "STAGE0-CRITICAL-BREAK-NOT-OWNED": ("An unknown critical-chain break has no owner or blocking boundary.", "Bind UNK-*, P0, owner and blocks_stage; inventory the unknown without deciding the target rule."),
    "PRD-TOO-THIN": ("The artifact lacks details required by its delivery level.", "Complete the applicable business, interaction, exception and acceptance contracts without inventing values."),
    "PRD-LANGUAGE-DRIFT": ("The document structure does not match its declared language.", "Align headings, body text, tables, questions, diagrams and tests with document_language; keep IDs and machine names unchanged."),
    "PRD-MODULE-SLICE-INCOMPLETE": ("A module slice is not locally complete for implementation and testing.", "Complete goals, flows, UI/data, rules, states, metrics, recovery, acceptance and unknowns in the same module section."),
    "PRD-FACET-REQUIRES-L2": ("A lightweight card activates data submission, integration, batch I/O or high-risk governance that L1 cannot carry safely.", "Upgrade to an L2 unified PRD and complete the applicable source, mapping, state, failure, audit and acceptance contracts; keyword padding must not bypass the upgrade."),
    "PROTO-NO-PAGE-ANCHOR": ("The prototype has no stable page anchor.", "Add a unique data-testid=\"page-VIEW-*\" to every page root."),
    "PROTO-NO-REGION-ANCHOR": ("A complex prototype has no stable region anchors.", "Add unique data-testid=\"region-REG-*\" anchors to its key business regions."),
    "PROTO-IFRAME-UNSAFE-SCHEME": ("The iframe uses an executable or unauditable URL scheme.", "Remove it; external integrations must use HTTPS and an explicit INT-* contract."),
    "PROTO-INSECURE-REMOTE-IFRAME": ("The remote iframe uses plaintext HTTP.", "Use HTTPS or replace the embed with an explicit external navigation/fallback path."),
    "PROTO-REMOTE-IFRAME-UNDECLARED": ("The remote iframe lacks ownership, fallback or browser-security attributes.", "Add data-integration-ref, data-fallback, title, sandbox and referrerpolicy."),
    "PROTO-REMOTE-IFRAME-UNVERIFIED": ("The remote iframe is declared but its runtime content and availability remain unverified.", "Execute a browser ARUN-* in the target network and role session, including fallback evidence."),
    "PROTO-UNHANDLED-ACTION": ("A prototype action has no observable dispatch path.", "Bind the data-action to one handler and produce a visible page, modal, state or data result."),
    "PROTO-ORPHAN-HANDLER": ("The action registry contains a handler with no source control.", "Restore its data-action control, remove confirmed dead code, or record the approved removal."),
    "PROTO-UNREACHABLE-VIEW": ("A hidden page, modal or drawer has no discoverable route.", "Add a stable data-action/data-view route or remove the approved dead surface."),
    "PROTO-REVIEW-UIACTION-NAMESPACE": ("A review-only UI action uses the business ACT-* namespace.", "Rename it to UIACT-REVIEW-* without changing business state or data."),
    "PROTO-METRIC-ID-SEMANTIC-COLLISION": ("One METRIC-* ID is reused for multiple business meanings.", "Assign unique IDs to distinct metrics; repeated displays of one metric must share one semantic label and caliber."),
    "PROTO-METRIC-LABEL-MISSING": ("A repeated metric ID has no stable semantic label.", "Add data-metric-label or split distinct meanings into separate METRIC-* IDs."),
    "PROTO-DYNAMIC-METRIC-ID-REUSE": ("A dynamic metric factory reuses one fixed METRIC-* for multiple runtime labels.", "Pass a stable metric ID per defined metric or render from a metric-definition map."),
    "PROTO-UNKNOWN-CONTRACT-INCOMPLETE": ("A prototype labels an UNK-* without an owned and closable lifecycle contract.", "Add priority, owner, blocks_stage, affected_refs and fallback to every data-unk or registry entry; clarify material unknowns before review."),
    "PROTO-UNKNOWN-CONFIRMED-CONFLICT": ("One prototype object is simultaneously marked confirmed and bound to an open UNK-*.", "Resolve it from a DEC/source: remove the current unknown contract when confirmed, or remove confirmed while keeping the owned gap contract."),
    "PROTO-REVIEW-LINKAGE-MISSING": ("Review markers and note cards have no stable bidirectional link.", "Share data-review-id on both sides or use a matching data-review-target, then execute a browser ARUN-* proof."),
    "PROTO-REVIEW-SELECTION-NOT-SYNCED": ("Review marker clicks do not expose a synchronized selection state.", "Read data-review-id, update aria-current on both sides, and prove click, scroll and highlight behavior in a browser."),
    "PROTO-REVIEW-LENS-COSMETIC": ("Role lenses change controls but have no role-specific content projection.", "Bind data-review-role controls to matching data-review-lens content without changing shared facts."),
    "PROTO-REVIEW-WORKSPACE-LEGACY": ("The legacy review overlay is page-note oriented and has no journey/task workspace contract.", "Migrate to orientation, journey, single-step focus, page and acceptance modes with an embedded baseline-bound manifest."),
    "PROTO-REVIEW-WORKSPACE-MANIFEST-INVALID": ("The review workspace has no unique parseable projection manifest.", "Embed one application/json review-workspace-manifest and validate it against the review-workspace schema."),
    "PROTO-REVIEW-LANGUAGE-MISMATCH": ("The review manifest and HTML declare different human languages.", "Align manifest.language with html[lang] and the user's language while preserving stable IDs and machine enums."),
    "PROTO-REVIEW-ROLE-PACKET-INCOMPLETE": ("A role lens is a summary/filter rather than a complete start-work packet.", "Complete the product/frontend/backend/qa slot contract and bind unknown semantics to UNK-* instead of inventing decisions."),
    "PROTO-REVIEW-ROLE-APPLICABILITY-MISMATCH": ("Role applicability differs between the manifest and the visible packet.", "Use active with complete slots, or not_affected with empty slots and one visible reason."),
    "PROTO-REVIEW-CONFIRMED-NO-EVIDENCE": ("A confirmed review step has no SRC-* or DEC-* evidence.", "Bind a reviewable source or decision, or downgrade the step and attach an owned UNK-* gap."),
    "PROTO-REVIEW-VERIFICATION-NO-EVIDENCE": ("A review step claims verification without EVD-* or ARUN-* evidence.", "Keep verification_status=not_run, or bind runtime evidence before upgrading the verification level."),
    "PROTO-REVIEW-STATUS-AXIS-HIDDEN": ("A business or verification status is hidden in the manifest instead of shown to human reviewers.", "Render separate human-readable business and verification status axes in every STEP packet."),
    "PROTO-REVIEW-STATUS-AXIS-DRIFT": ("The visible status axis differs from the review manifest.", "Project both status axes from the same STEP record instead of hand-writing HTML values."),
    "PROTO-REVIEW-STATUS-AXIS-DUPLICATE": ("One STEP status axis is rendered more than once and may show conflicting conclusions.", "Render each STEP/axis exactly once from the manifest record and remove stale copies."),
    "PROTO-REVIEW-VERIFICATION-ARUN-UNRESOLVED": ("A claimed browser, integration, accepted or failed status references no ARUN supplied to this gate.", "Keep not_run or provide the referenced ARUN; an invented identifier is not runtime evidence."),
    "PROTO-REVIEW-VERIFICATION-BASELINE-DRIFT": ("The cited ARUN belongs to another baseline version.", "Provide an ARUN whose baseline_version exactly matches the review baseline, or lower the verification claim."),
    "PROTO-REVIEW-VERIFICATION-AC-UNPROVED": ("The ARUN does not cover this STEP's TEST-to-AC contract.", "Bind the STEP to its QA scenarios and provide an ARUN covering the relevant ACs; accepted requires every relevant AC to pass."),
    "PROTO-REVIEW-VERIFICATION-LEVEL-UNPROVED": ("The supplied ARUN environment or conclusion does not support the claimed verification level.", "Downgrade the claim or execute and attach evidence at the required level."),
    "PROTO-REVIEW-MODEL-COVERAGE-AMBIGUOUS": ("The journey leaves state or data-flow coverage ambiguous.", "Reference separate flow/state/data models or explicitly mark the inapplicable dimensions."),
    "PROTO-REVIEW-MODEL-NOT-VISIBLE": ("A referenced flow, state machine, or data flow is absent from the human workspace.", "Render each model with data-review-model and data-review-model-ref instead of hiding it in JSON."),
    "PROTO-REVIEW-MODEL-NA-HIDDEN": ("An inapplicable state or data-flow dimension has no visible reason.", "Expose the reason with data-review-model-na, or keep it active and bind an owned UNK-* gap."),
    "PROTO-REVIEW-SCENARIO-NOT-VISIBLE": ("A TEST-* to AC-* scenario exists only in the manifest.", "Render a locatable acceptance card with data-review-scenario and data-review-acceptance-ref."),
    "PROTO-REVIEW-CONTRACT-REF-HIDDEN": ("A role work packet hides the contracts behind its summary.", "Show the packet contract_refs as visible or expandable source links while keeping the canonical PRD/Truth authoritative."),
    "PROTO-REVIEW-RISK-NOT-TESTED": ("A declared step risk is absent from its TEST/AC coverage.", "Add the matching risk dimension, dual result and evidence from the canonical acceptance contract."),
    "PROTO-REVIEW-MODE-MISSING": ("Review information is flattened into one list or drawer instead of matching the receiver's task.", "Provide the applicable orientation, journey, focus, page and acceptance modes and focus one STEP-* at a time."),
    "PROTO-REVIEW-COMPACT-OVERLAY": ("The compact review surface obscures the product context.", "Use a fullscreen product/review switcher that preserves the current STEP and return target, then verify it in a browser."),
    "PROTO-REVIEW-BASELINE-DRIFT": ("The review workspace and supplied PRD are not the same content baseline.", "Regenerate the projection from the authoritative PRD hash and update human and machine projections in the same CHG-*.") ,
    "PROTO-DYNAMIC-CLASS-POLLUTION": ("Business text is interpolated into a CSS class.", "Keep class names as fixed semantic tokens and write escaped descriptions through textContent."),
    "PROTO-JS-SYNTAX": ("The prototype contains invalid JavaScript.", "Repair the referenced script and verify closing script/body/html tags."),
}
EN_PREFIX_GUIDANCE: tuple[tuple[str, str, str], ...] = (
    ("CUSTOM-", "A project-local validation rule is invalid or unmet.", "Repair the declarative YAML rule; local Python validators are not executed."),
    ("CUST-", "A project-local requirement rule is unmet.", "Repair the referenced artifact contract or have the rule owner revise the local rule."),
    ("AUTH-", "Requirement authority or write ownership is unresolved.", "Create a scoped DEC-CONFLICT-* owned by the accountable decision maker."),
    ("HANDOFF-", "The handoff package is inconsistent with the requirement baseline.", "Align baseline hashes, owners, stable IDs and acceptance references without inventing rules."),
    ("AI-", "An AI capability lacks an applicable runtime governance contract.", "Add input/output, version, permissions, human gate, fallback, evaluation and observability references."),
    ("ACCEPTANCE-", "The acceptance record is invalid or contradicts its conclusion.", "Repair execution context, actual results, evidence, defects and sign-off against the schema."),
    ("PROTO-REVIEW-STEP-ANCHOR", "A review STEP is not uniquely bound to its human work-packet DOM root.", "Bind every manifest STEP to exactly one matching data-review-step and manifest.dom_anchor; remove orphan or duplicate packets."),
    ("PROTO-REVIEW-LENS-", "A role lens has labels or styling but no reachable role projection.", "Read data-review-role, update data-review-active-role on the workspace root, retain related-role navigation and verify it in a browser."),
    ("PROTO-CSS-", "CSS pollution may hide or break interactive state.", "Scope visibility styles to their component and data-state; remove global !important pollution."),
    ("PROTO-", "The prototype lacks a testable interaction or state contract.", "Repair the referenced element using stable data-testid/data-action/data-state/data-field and a visible result."),
    ("PRD-", "The PRD lacks a requirement contract needed at this stage.", "Complete confirmed rules, stable IDs, exceptions and acceptance at the referenced location; do not invent values."),
    ("REQ-", "The requirement lifecycle record is incomplete or inconsistent.", "Repair the referenced field while preserving stable IDs, sources, decisions and audit history."),
)


def finding_code_match(code: str) -> str:
    """Return exact/family/unknown without pretending an unknown code is known."""
    normalized = code.strip().upper()
    if normalized in FINDING_GUIDANCE or normalized in EN_FINDING_GUIDANCE:
        return "exact"
    if any(normalized.startswith(prefix) for prefix, _cause, _fix in PREFIX_GUIDANCE):
        return "family"
    return "unknown"


def guidance_for(code: str) -> tuple[str, str]:
    """Return bounded, deterministic repair guidance for one finding code."""
    if code in FINDING_GUIDANCE:
        return FINDING_GUIDANCE[code]
    for prefix, cause, fix in PREFIX_GUIDANCE:
        if code.startswith(prefix):
            return cause, fix
    return (
        "工件违反了确定性交付合同。",
        "使用 code、artifact 和 ref 修复限定问题，然后重跑同一门禁命令。",
    )


def english_guidance_for(code: str) -> tuple[str, str]:
    if code in EN_FINDING_GUIDANCE:
        return EN_FINDING_GUIDANCE[code]
    for prefix, cause, fix in EN_PREFIX_GUIDANCE:
        if code.startswith(prefix):
            return cause, fix
    return (
        "The artifact violates a deterministic delivery contract.",
        "Use code, artifact and ref to repair only the bounded issue, then rerun the same gate command.",
    )


REPAIR_EXAMPLES: tuple[tuple[str, str], ...] = (
    ("INTAKE-SCHEMA", "cp references/templates/requirement-intake-template.yaml intake.yaml，补齐 artifact: requirement_intake、stage: intake、source_refs: [SRC-*]、value_evidence 等必填字段。"),
    ("PROTO-DEMO-SCAFFOLDING-VISIBLE", "删除 <div>验收场景</div> 这类演示文案块，改为真实业务空态文案，如 <p>暂无待办事项</p>。"),
    ("PROTO-NESTED-PRODUCT-IFRAME", "移除 <iframe src=\"child.html\">，把 child.html 的页面迁移为当前文件内的 <section data-testid=\"page-VIEW-CHILD-001\">。"),
    ("PROTO-REMOTE-IFRAME-UNDECLARED", "<iframe src=\"https://partner.example/app\" data-integration-ref=\"INT-PARTNER-001\" data-fallback=\"外部系统不可用时显示重试与跳转\" title=\"合作方系统\" sandbox referrerpolicy=\"no-referrer\"></iframe>"),
    ("PRD-STATE-SEMANTIC-POLLUTION", "| 待处理 | 复检 | 复检中 | —— 下一状态列写业务状态名；API-RISK-RECHECK 移入“动作/接口”列。"),
    ("PRD-DUPLICATE-STABLE-ID-DEFINITION", "在权威定义表中只保留一行 VIEW-RISK-LIST-001；其他章节写“参见 VIEW-RISK-LIST-001”，不要再次填写一行定义。"),
    ("HANDOFF-BINDING-TERM-MISSING", "PRD 正文写“上传道路运输经营许可证后进入审核”，原型对应区域可见文案同样写“道路运输经营许可证”。"),
    ("PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT", "关闭冲突项：unknowns 中该 key 的 status 改为 closed 并从 open_p0_unknown_ids 移除；或删除 decisions 中同 key 条目改登 UNK-*。"),
    ("HANDOFF-AESTHETIC-UNDECIDED", "存量小迭代写 visual_authority: existing 与 design_lock_ref: prototype.html#design-lock；绿地可写 greenfield_default；品牌化方案再引用 DEC-AESTHETIC-*。"),
    ("HANDOFF-STEP-", "STEP-REPORT-07：入口与责任、输入与权威源、处理与口径、守卫与状态、双结果、事件与责任交接、失败与恢复、追溯与验收八项逐一写明；不适用项显式写“无”。"),
    ("HANDOFF-PRD-STEP-NOT-PACKETED", "在 packet implementation_step_refs 中加入 STEP-REPORT-07，并在 packet 正文引用它；或通过 CHG-* 从本次基线移除。"),
    ("STAGE0-DISPOSITION-MISSING", "为 type: view 的条目补 disposition: inherit_layout（或 adopt_page/rebuild_interaction/reuse_component/discard）。"),
    ("PRD-LANGUAGE", "document_language: zh-CN；将英文结构标题改为中文，保留 REQ/API/字段名原样。"),
    ("PRD-MODULE-SLICE", "### 7.1 授权管理 MOD-AUTH-001；就近写目标、路径、VIEW/FLD/ACT、RULE/STM、METRIC、恢复、AC 与 UNK。"),
    ("PRD-DATA-SUBMISSION", "activated_facets: [data_submission]；补来源映射、校验、提交状态、重试/幂等、审计、口径/时效和对账。"),
    ("PRD-P0-UNKNOWN", "unknowns: [{id: UNK-AUTH-001, priority: P0, status: open, blocks_stage: baseline, owner: 产品负责人, affected_refs: [REQ-AUTH-001]}]"),
    ("PRD-OPEN-P0", "先由 owner 关闭 UNK-*，同步 open_p0_unknown_ids，再重新申请基线门禁。"),
    ("PRD-NONEXACT-ID", "逐条写 AC-AUDIT-001、AC-AUDIT-002、AC-AUDIT-003；不要写 AC-AUDIT-001..003。"),
    ("PROTO-NO-REGION-ANCHOR", "<section data-testid=\"region-REG-COURSE-FILTERS\">...</section>"),
    ("PROTO-BROWSER-EVIDENCE", "python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html --level L3 --acceptance-run acceptance/ARUN-PROTOTYPE-001.yaml"),
    ("PROTO-DYNAMIC-ANCHOR", "在模板源码直接写 data-action=\"ACT-COURSE-SAVE\"，不要用 'data-' + 'action' 拼接。"),
    ("PROTO-UNHANDLED-ACTION", "actionRegistry['ACT-COURSE-SAVE'] = saveCourse，并让处理器更新 data-state 或页面数据。"),
    ("PROTO-ORPHAN-HANDLER", "actionRegistry['ACT-COURSE-SAVE'] 存在时，源模板也应有 data-action=\"ACT-COURSE-SAVE\"；若功能已批准删除，则同时删除处理器并记录 approved_removals。"),
    ("PROTO-UNREACHABLE-VIEW", "为隐藏抽屉增加 data-testid=\"drawer-VIEW-DETAIL\"，并由 data-action=\"ACT-DETAIL-OPEN\" 的处理器显式打开。"),
    ("PROTO-REVIEW-UIACTION-NAMESPACE", "把 data-action=\"ACT-REVIEW-TOGGLE\" 改为 data-action=\"UIACT-REVIEW-TOGGLE\"。"),
    ("PROTO-DYNAMIC-CLASS-POLLUTION", "使用 class=\"sev sev-high\"；通过 cell.textContent = description 写入已转义说明，不把 description 拼入 class。"),
    ("STAGE0-", "为反推项使用 INV-*，保留 source_ref/location；推断项绑定 review_batch_ref，由责任人批量确认。"),
    ("GATE-", "按 finding.ref 修正输入或配置，然后复制 RETRY 命令重跑。"),
)


def repair_example_for(code: str) -> str:
    for prefix, example in REPAIR_EXAMPLES:
        if code.startswith(prefix):
            return example
    return "按 finding.ref 只修复该项，保留稳定 ID 与来源证据，再重跑门禁。"


def english_repair_example_for(code: str) -> str:
    examples = (
        ("PRD-LANGUAGE", "Set document_language: en-US, translate human-facing headings and tables, and keep REQ/API/field names unchanged."),
        ("PRD-DUPLICATE-STABLE-ID-DEFINITION", "Keep one VIEW-RISK-LIST-001 definition row; elsewhere write 'See VIEW-RISK-LIST-001' instead of defining it again."),
        ("PRD-MODULE-SLICE", "Complete MOD-AUTH-001 with goal, paths, VIEW/FLD/ACT, RULE/STATE, METRIC, recovery, AC and UNK references."),
        ("PROTO-NO-REGION-ANCHOR", '<section data-testid="region-REG-COURSE-FILTERS">...</section>'),
        ("PROTO-UNHANDLED-ACTION", "Bind actionRegistry['ACT-COURSE-SAVE'] = saveCourse and update a visible data-state or page value."),
        ("PROTO-ORPHAN-HANDLER", 'If ACT-COURSE-SAVE remains registered, keep a source control with data-action="ACT-COURSE-SAVE" or record its approved removal.'),
        ("PROTO-UNREACHABLE-VIEW", 'Open data-testid="drawer-VIEW-DETAIL" from data-action="ACT-DETAIL-OPEN", or remove the approved dead drawer.'),
        ("PROTO-REVIEW-UIACTION-NAMESPACE", 'Rename data-action="ACT-REVIEW-TOGGLE" to data-action="UIACT-REVIEW-TOGGLE".'),
        ("PROTO-DYNAMIC-CLASS-POLLUTION", 'Use class="severity severity-high" and assign the description through cell.textContent.'),
        ("HANDOFF-STEP-", "Complete all eight STEP-* facets; explicitly state none when a facet is not applicable, then align the manifest and packet body."),
        ("HANDOFF-PRD-STEP-NOT-PACKETED", "Assign the STEP-* to one owned packet or remove it through an approved baseline change."),
        ("GATE-", "Repair the input or option named by finding.ref, then copy the RETRY command."),
    )
    for prefix, example in examples:
        if code.startswith(prefix):
            return example
    return "Repair only finding.ref, preserve stable IDs and source evidence, and rerun the gate."


def _contains_cjk(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def _english_message(item: Finding) -> str:
    if not _contains_cjk(item.message):
        return item.message
    if item.message.startswith("存量基线已存在"):
        return f"Inherited baseline issue {item.code}; this run did not introduce a new regression."
    location = item.ref or Path(item.artifact).name
    return f"{item.code} contract failed at {location}."


def localized_finding(item: Finding, language: str) -> dict[str, Any]:
    zh_message = item.message if _contains_cjk(item.message) else f"{item.cause} 技术明细：{item.message}"
    if item.severity == "INFO":
        en_cause = "This is a gate-coverage note, not a contract violation."
        en_fix = "No repair is required; provide the named sidecar or runtime only when stronger assurance is needed."
    else:
        en_cause, en_fix = english_guidance_for(item.code)
    en_message = _english_message(item)
    en_example = (
        "Keep the current result and add the skipped input only if that assurance is required."
        if item.severity == "INFO" else english_repair_example_for(item.code)
    )
    english = language.casefold().startswith("en")
    record = asdict(item)
    record.update({
        "message": en_message if english else zh_message,
        "cause": en_cause if english else item.cause,
        "how_to_fix": en_fix if english else item.how_to_fix,
        "repair_example": en_example if english else item.repair_example,
        "message_zh": zh_message,
        "cause_zh": item.cause,
        "fix_zh": item.how_to_fix,
        "repair_example_zh": item.repair_example,
        "message_en": en_message,
        "cause_en": en_cause,
        "fix_en": en_fix,
        "repair_example_en": en_example,
    })
    return record


def markdown_headings(raw: str) -> list[tuple[int, str, int]]:
    """Return real Markdown headings while ignoring fenced examples and prose mentions."""
    headings: list[tuple[int, str, int]] = []
    in_fence = False
    offset = 0
    for line in raw.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        elif not in_fence:
            match = re.match(r"^(#{1,6})[ \t]+(.+?)\s*$", line.rstrip("\r\n"))
            if match:
                title = re.sub(r"\s+#+\s*$", "", match.group(2)).strip()
                headings.append((len(match.group(1)), title, offset))
        offset += len(line)
    return headings


def _heading_position(raw: str, patterns: tuple[str, ...], *, last: bool = False) -> int:
    matches = [
        position
        for _level, title, position in markdown_headings(raw)
        if any(re.search(pattern, title, re.I) for pattern in patterns)
    ]
    if not matches:
        return -1
    return max(matches) if last else min(matches)


def _has_heading(raw: str, patterns: tuple[str, ...]) -> bool:
    return any(
        any(re.search(pattern, title, re.I) for pattern in patterns)
        for _level, title, _position in markdown_headings(raw)
    )


def _heading_language(title: str) -> str:
    cleaned = re.sub(r"`[^`]+`", " ", title)
    cleaned = re.sub(r"\b(?:GET|POST|PUT|PATCH|DELETE|API|SDK|AI|SQL|JSON|YAML)\b", " ", cleaned, flags=re.I)
    cleaned = re.sub(
        r"\b(?:REQ|ROLE|MOD|FLOW|VIEW|REG|ACT|FLD|STM|STATE|RULE|API|EVT|INT|AC|TEST|EVD|UNK)-[A-Z0-9-]+\b",
        " ", cleaned, flags=re.I,
    )
    cjk = len(re.findall(r"[\u4e00-\u9fff]", cleaned))
    latin_words = len(re.findall(r"\b[A-Za-z]{2,}\b", cleaned))
    if cjk >= 2 and latin_words >= 2:
        return "mixed"
    if cjk >= 2:
        return "zh"
    if latin_words >= 2:
        return "en"
    return "neutral"


def _module_slices(raw: str) -> dict[str, str]:
    headings = markdown_headings(raw)
    slices: dict[str, str] = {}
    for index, (level, title, start) in enumerate(headings):
        module_match = re.search(r"\bMOD-[A-Z0-9-]+\b", title, re.I)
        if not module_match:
            continue
        end = len(raw)
        for next_level, _next_title, next_start in headings[index + 1:]:
            if next_level <= level:
                end = next_start
                break
        slices[module_match.group(0).upper()] = raw[start:end]
    return slices


class Gate(PRDChecks, PrototypeChecks, HandoffChecks):
    def __init__(self) -> None:
        self._cache: dict[Path, str] = {}
        self.read_counts: Counter[str] = Counter()
        self.findings: list[Finding] = []
        self.metrics: dict[str, Any] = {}
        self.prototype_acceptance_refs: set[str] = set()
        self.prototype_baseline_signatures: Counter[tuple[str, str, str]] = Counter()
        self.prototype_inherited_findings = 0
        self.review_workspace_contracts: list[tuple[Path, dict[str, Any]]] = []
        self.review_workspace_legacy_paths: set[Path] = set()

    def read(self, path: Path) -> str:
        key = path.resolve()
        if key not in self._cache:
            self._cache[key] = key.read_text(encoding="utf-8")
            self.read_counts[str(key)] += 1
        return self._cache[key]

    def add(
        self,
        severity: str,
        code: str,
        path: Path,
        message: str,
        ref: str = "",
        *,
        affected_consumers: tuple[str, ...] = (),
        related_refs: tuple[str, ...] = (),
        binding_source_refs: tuple[str, ...] = (),
    ) -> None:
        signature = (code, ref, message)
        if severity == "BLOCK" and code.startswith("PROTO-") and self.prototype_baseline_signatures[signature] > 0:
            self.prototype_baseline_signatures[signature] -= 1
            severity = "GAP"
            message = f"存量基线已存在，本次未新增：{message}"
            self.prototype_inherited_findings += 1
            self.metrics["prototype_inherited_findings"] = self.prototype_inherited_findings
        if severity == "INFO":
            cause = "这是门禁覆盖范围说明，不代表工件违反交付合同。"
            how_to_fix = "无需修复；需要更强保证时，按该说明提供对应侧车或运行环境。"
            repair_example = "保留当前 PASS/GAP/BLOCK 结论，另行补充被跳过检查所需输入。"
        else:
            cause, how_to_fix = guidance_for(code)
            repair_example = repair_example_for(code)
        self.findings.append(Finding(
            severity=severity,
            code=code,
            artifact=str(path),
            message=message,
            ref=ref,
            cause=cause,
            how_to_fix=how_to_fix,
            repair_example=repair_example,
            affected_consumers=affected_consumers,
            related_refs=related_refs,
            binding_source_refs=binding_source_refs,
        ))

    @staticmethod
    def _frontmatter(raw: str) -> dict[str, Any]:
        match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", raw, re.S)
        if not match:
            return {}
        try:
            loaded = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}
        return loaded if isinstance(loaded, dict) else {}

    def _check_semantics(self, path: Path, raw: str) -> None:
        for item in run_semantic_checks(raw):
            self.add(item.severity, item.code, path, item.message, item.ref)

    @staticmethod
    def _tag_source(raw: str) -> str:
        return "\n".join(re.findall(r"<[A-Za-z][^>]*>", raw, re.S))

    @staticmethod
    def _yaml_document(path: Path, raw: str) -> tuple[dict[str, Any] | None, str | None]:
        try:
            value = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            return None, f"{path.name} 不是有效 YAML：{exc}"
        if not isinstance(value, dict):
            return None, f"{path.name} 顶层必须是对象"
        return value, None

    @staticmethod
    def _sha256(raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def check_requirement(self, path: Path) -> None:
        try:
            raw = self.read(path)
            document = yaml.safe_load(raw)
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            self.add("BLOCK", "REQ-PARSE", path, f"requirement register cannot be read as YAML: {exc}")
            return
        if not (isinstance(document, dict) and "requirements" in document):
            # Single-requirement intake cards route to the intake contract instead of
            # being rejected by the register schema's unrelated field list.
            schema = json.loads(INTAKE_SCHEMA.read_text(encoding="utf-8"))
            errors = sorted(
                Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
                key=lambda item: tuple(str(part) for part in item.path),
            )
            for error in errors:
                location = ".".join(str(part) for part in error.path) or "<root>"
                self.add("BLOCK", "INTAKE-SCHEMA", path, error.message, location)
            if not errors and isinstance(document, dict):
                self.metrics["requirements"] = 1
            return
        schema = json.loads(REGISTER_SCHEMA.read_text(encoding="utf-8"))
        errors = sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
            key=lambda item: tuple(str(part) for part in item.path),
        )
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            self.add("BLOCK", "REQ-SCHEMA", path, error.message, location)
        if not isinstance(document, dict):
            return
        requirements = document.get("requirements", [])
        if not isinstance(requirements, list):
            return
        ids = [item.get("id") for item in requirements if isinstance(item, dict)]
        known = set(ids)
        acceptance_evidence = {
            item.get("requirement_ref")
            for item in document.get("audit_log", []) or []
            if isinstance(item, dict)
            and item.get("action") in {"accepted", "closed", "acceptance_signed"}
            and item.get("evidence_refs")
        }
        for duplicate in sorted(item for item, count in Counter(ids).items() if item and count > 1):
            self.add("BLOCK", "REQ-DUPLICATE-ID", path, "requirement ID is duplicated", duplicate)
        for item in requirements:
            if not isinstance(item, dict):
                continue
            req_id = str(item.get("id", "<unknown>"))
            stage = item.get("stage")
            if stage in {"baselined", "change_requested", "acceptance", "accepted", "closed"}:
                for key, code in (("behavior_refs", "REQ-NO-BEHAVIOR"), ("acceptance_refs", "REQ-NO-AC")):
                    if not item.get(key):
                        self.add("BLOCK", code, path, f"{stage} requirement has no {key}", req_id)
            if stage in {"accepted", "closed"} and item.get("id") not in acceptance_evidence:
                self.add("BLOCK", "REQ-NO-EVIDENCE", path, f"{stage} requirement has no signed acceptance audit with evidence", req_id)
            for dependency in item.get("dependency_refs", []) or []:
                if dependency not in known:
                    self.add("BLOCK", "REQ-ORPHAN-DEPENDENCY", path, "dependency does not resolve in the register", f"{req_id}->{dependency}")
        for edge in document.get("dependency_edges", []) or []:
            if not isinstance(edge, dict):
                continue
            source, target = edge.get("from_ref"), edge.get("to_ref")
            if source not in known or target not in known:
                self.add("BLOCK", "REQ-OPEN-EDGE", path, "dependency edge is not requirement-closed", f"{source}->{target}")
        self.metrics["requirements"] = len(requirements)

    def check_register_sidecar(self, path: Path) -> None:
        """Validate only current-schema requirement registers; legacy drafts stay advisory."""
        try:
            document = yaml.safe_load(self.read(path))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            self.add("INFO", "REQ-REGISTER-SIDECAR-SKIP", path, f"侧车产物无法按 YAML 解析，跳过登记册语义校验：{exc}")
            return
        schema = json.loads(REGISTER_SCHEMA.read_text(encoding="utf-8"))
        errors = sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
            key=lambda item: tuple(str(part) for part in item.path),
        )
        if errors:
            first = errors[0]
            location = ".".join(str(part) for part in first.path) or "<root>"
            self.add(
                "INFO", "REQ-REGISTER-SIDECAR-SKIP", path,
                f"侧车产物不符合当前登记册 schema（可能为旧格式草稿），跳过登记册语义校验：{location}: {first.message}",
            )
            return
        run_sidecar_validator(self, "validate_requirement_register.py", path, "REQ-REGISTER-SIDECAR")


def resolve_output_language(gate: Gate, requested: str) -> str:
    if requested != "auto":
        return requested
    for path, raw in gate._cache.items():
        metadata = Gate._frontmatter(raw)
        if not metadata and path.suffix.casefold() in {".yaml", ".yml", ".json"}:
            try:
                loaded = json.loads(raw) if path.suffix.casefold() == ".json" else yaml.safe_load(raw)
                metadata = loaded if isinstance(loaded, dict) else {}
            except (json.JSONDecodeError, yaml.YAMLError):
                metadata = {}
        declared = str(metadata.get("document_language", "")).casefold()
        if declared.startswith("en"):
            return "en-US"
        if declared.startswith("zh"):
            return "zh-CN"
        html_lang = re.search(r"<html\b[^>]*\blang\s*=\s*['\"]([^'\"]+)", raw, re.I)
        if html_lang:
            return "en-US" if html_lang.group(1).casefold().startswith("en") else "zh-CN"
    combined = "\n".join(gate._cache.values())
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", combined))
    english_words = len(re.findall(r"\b[A-Za-z]{3,}\b", combined))
    return "en-US" if english_words >= 20 and cjk_count < 20 else "zh-CN"


def result_payload(gate: Gate, profile: str, retry_command: str = "", output_language: str = "zh-CN") -> dict[str, Any]:
    blocks = sum(item.severity == "BLOCK" for item in gate.findings)
    p0_unknowns = sum(item.severity == "P0_UNKNOWN" for item in gate.findings)
    gaps = sum(item.severity == "GAP" for item in gate.findings)
    code = 2 if blocks else 3 if p0_unknowns else 1 if gaps else 0
    rendered_findings = [localized_finding(item, output_language) for item in gate.findings]
    consumed_browser_evidence = bool(gate.metrics.get("prototype_browser_evidence"))
    english = output_language.casefold().startswith("en")
    coverage = (
        "Deterministic static gate; it does not invoke a browser, LLM or sub-agent"
        if english else "确定性静态门禁；不调用浏览器、LLM 或子 Agent"
    )
    if consumed_browser_evidence:
        coverage += (
            "; external real-browser ARUN structure, evidence and sign-off were validated"
            if english else "；已校验外部真实浏览器 ARUN 的结构、证据与签署"
        )
    return {
        "status": STATUSES[code],
        "profile": profile,
        "output_language": output_language,
        "summary": {"blockers": blocks, "p0_unknowns": p0_unknowns, "gaps": gaps, "findings": len(gate.findings)},
        "coverage": coverage,
        "not_proven": not_proven_for(gate, output_language),
        "retry_command": retry_command,
        "metrics": {**gate.metrics, "input_read_counts": dict(gate.read_counts)},
        "findings": rendered_findings,
        "exit_code": code,
    }


def diagnostic_roots(findings: list[Finding], limit: int) -> tuple[list[tuple[Finding, int]], int]:
    """Compact by code while preferring a concrete representative over a template ref."""
    first: dict[str, Finding] = {}
    counts: dict[str, int] = {}
    order: list[str] = []
    for item in findings:
        if item.code not in first:
            first[item.code] = item
            order.append(item.code)
        elif _representative_ref_score(item.ref) > _representative_ref_score(first[item.code].ref):
            first[item.code] = item
        counts[item.code] = counts.get(item.code, 0) + 1
    selected = order[:max(limit, 0)]
    return [(first[code], counts[code]) for code in selected], len(order)


def _representative_ref_score(ref: str) -> int:
    """Rank a real stable reference above blank, shell or interpolation examples."""
    value = str(ref or "").strip()
    if not value:
        return 0
    if re.search(r"\$\{[^}]+\}|<[^>]+>|\{[^{}]+\}", value):
        return 1
    return 2


def run_sidecar_validator(gate: Gate, script: str, path: Path, code: str, extra: list[str] | None = None) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_DIR / script), str(path), *(extra or [])],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if result.returncode == 0:
        return
    lines = [line.removeprefix("FAIL: ") for line in result.stdout.splitlines() if line.startswith("FAIL: ")]
    if not lines:
        lines = [line for line in (result.stdout.strip() or result.stderr.strip()).splitlines() if line]
    for line in lines[:10] or [f"{script} 校验失败"]:
        gate.add("BLOCK", code, path, line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lightweight, non-generative final quality gate")
    parser.add_argument("--profile", choices=["requirement", "prd", "prototype", "handoff", "full", "stage0", "agent_handoff"], required=True)
    parser.add_argument("--requirement", type=Path, help="requirement register YAML")
    parser.add_argument("--register", type=Path, action="append", help="profile=requirement 的侧车需求登记册；提供时执行登记册语义校验")
    parser.add_argument("--review-record", type=Path, help="profile=prd baseline 阶段可选评审记录 YAML；提供时执行签署闭合校验")
    parser.add_argument("--prd", type=Path, help="unified PRD Markdown")
    parser.add_argument("--prototype", type=Path, action="append", help="HTML prototype; repeat for admin/H5/multi-surface handoff")
    parser.add_argument("--prototype-baseline", type=Path, help="Optional previous HTML baseline; inherited prototype blockers become gaps, new regressions still block")
    parser.add_argument("--inventory", type=Path, help="Stage 0 brownfield inventory YAML")
    parser.add_argument("--manifest", type=Path, help="Agent handoff manifest YAML")
    parser.add_argument("--acceptance-run", type=Path, action="append", help="Executed ARUN-* YAML; repeat when prototype AC evidence is split")
    parser.add_argument("--level", choices=["auto", *LEVELS], default="L2")
    parser.add_argument("--stage", choices=list(STAGE_ORDER), default="baseline")
    parser.add_argument("--scope-ref", action="append", default=[], help="Limit stage/P0 evaluation to one stable-ID scope; repeat as needed")
    parser.add_argument("--domain", action="append", default=[], help="当前工件适用的领域 ID；用于隔离 custom 规则，可重复")
    parser.add_argument("--format", choices=["concise", "json"], default="concise")
    parser.add_argument("--language", choices=["auto", "zh-CN", "en-US"], default="auto", help="Human-readable gate diagnostics; auto reads document_language or HTML lang")
    parser.add_argument("--diagnostics", choices=["first", "roots", "summary", "full"], default="roots")
    parser.add_argument("--max-findings", type=int, default=20)
    parser.add_argument("--custom-root", type=Path, help="项目本地私有扩展目录；默认自动发现当前目录 custom/")
    args = parser.parse_args()
    required = {
        "requirement": ("requirement",),
        "prd": ("prd",),
        "prototype": ("prototype",),
        "handoff": ("prd", "prototype"),
        "full": ("requirement", "prd", "prototype"),
        "stage0": ("inventory",),
        "agent_handoff": ("manifest",),
    }[args.profile]
    gate = Gate()
    prototype_level = "L2" if args.level == "auto" else args.level
    if args.prototype_baseline:
        if not args.prototype_baseline.is_file():
            gate.add("BLOCK", "GATE-NOT-FILE", args.prototype_baseline, "prototype baseline does not exist or is not a file", "prototype-baseline")
        else:
            baseline_gate = Gate()
            baseline_gate.check_prototype(args.prototype_baseline, prototype_level)
            gate.prototype_baseline_signatures = Counter(
                (item.code, item.ref, item.message)
                for item in baseline_gate.findings
                if item.severity == "BLOCK" and item.code.startswith("PROTO-")
            )
            baseline_raw = baseline_gate.read(args.prototype_baseline)
            gate.metrics.update({
                "prototype_baseline": str(args.prototype_baseline),
                "prototype_baseline_sha256": gate._sha256(baseline_raw),
                "prototype_baseline_blockers": sum(gate.prototype_baseline_signatures.values()),
                "prototype_inherited_findings": 0,
            })
    for name in required:
        value = getattr(args, name)
        values = value if name == "prototype" and isinstance(value, list) else [value]
        if not value:
            gate.add("BLOCK", "GATE-MISSING-INPUT", Path("<input>"), f"--{name} is required for profile={args.profile}", name)
            continue
        for item in values:
            if not item.is_file():
                gate.add("BLOCK", "GATE-NOT-FILE", item, "input does not exist or is not a file", name)
            elif name == "requirement":
                gate.check_requirement(item)
            elif name == "prd":
                gate.check_prd(item, args.level, stage=args.stage, scope_refs=tuple(args.scope_ref))
            elif name == "inventory":
                gate.check_stage0(item)
            elif name == "manifest":
                gate.check_agent_handoff(item)
            else:
                gate.check_prototype(item, prototype_level)
    if args.manifest and "manifest" not in required:
        if not args.manifest.is_file():
            gate.add("BLOCK", "GATE-NOT-FILE", args.manifest, "input does not exist or is not a file", "manifest")
        else:
            gate.check_agent_handoff(args.manifest)
    if args.inventory and "inventory" not in required:
        if not args.inventory.is_file():
            gate.add("BLOCK", "GATE-NOT-FILE", args.inventory, "input does not exist or is not a file", "inventory")
        else:
            gate.check_stage0(args.inventory)
    valid_prd = args.prd if args.prd and args.prd.is_file() else None
    valid_prototypes = [path for path in (args.prototype or []) if path.is_file()]
    for register in args.register or []:
        if not register.is_file():
            gate.add("BLOCK", "GATE-NOT-FILE", register, "input does not exist or is not a file", "register")
        else:
            gate.check_register_sidecar(register)
    if args.review_record:
        if not args.review_record.is_file():
            gate.add("BLOCK", "GATE-NOT-FILE", args.review_record, "input does not exist or is not a file", "review-record")
        else:
            run_sidecar_validator(gate, "validate_review_record.py", args.review_record, "REVIEW-RECORD-SIDECAR")
    if args.profile in {"prd", "full"} and valid_prd:
        ledgers = sorted(valid_prd.parent.glob("*ledger*.y*ml"))
        if ledgers:
            run_sidecar_validator(gate, "validate_traceability_ledger.py", ledgers[0], "TRACE-LEDGER-SIDECAR")
        else:
            gate.add("INFO", "TRACE-LEDGER-SKIP", valid_prd, "未在 PRD 同目录发现追溯矩阵 ledger 侧车，跳过双向追溯闭合校验")
    if args.profile in {"prototype", "handoff", "full"}:
        for prototype_path in valid_prototypes:
            marker = re.search(r'data-ia-skeleton="([^"]+)"', gate.read(prototype_path))
            if not marker:
                gate.add("INFO", "PROTO-IA-SKELETON-SKIP", prototype_path, "原型未声明 IA skeleton 标记，跳过 IA 骨架校验")
                continue
            skeleton = prototype_path.parent / marker.group(1)
            if not skeleton.is_file():
                gate.add("BLOCK", "PROTO-IA-SKELETON-NOT-FILE", prototype_path, "IA skeleton 标记引用的文件不存在", marker.group(1))
            else:
                run_sidecar_validator(
                    gate, "validate_ia_skeleton.py", skeleton, "PROTO-IA-SKELETON",
                    extra=["--level", prototype_level],
                )
    if args.profile in {"handoff", "full"} and valid_prd and valid_prototypes:
        gate.check_handoff(valid_prd, valid_prototypes, prototype_level)
    if args.profile in {"handoff", "full"} and valid_prd and args.manifest and args.manifest.is_file():
        gate.check_manifest_prd_binding(valid_prd, args.manifest)
        gate.check_review_manifest_binding(args.manifest)
    valid_acceptance_runs: list[Path] = []
    acceptance_claims: dict[str, dict[str, Any]] = {}
    evidenced_acs: set[str] = set()
    browser_evidence = False
    conclusive_evidence = False
    for acceptance_run in args.acceptance_run or []:
        if not acceptance_run.is_file():
            gate.add("BLOCK", "GATE-NOT-FILE", acceptance_run, "input does not exist or is not a file", "acceptance-run")
            continue
        valid_acceptance_runs.append(acceptance_run)
        passed, is_browser, is_conclusive = gate.check_acceptance_run(acceptance_run)
        try:
            run_document = yaml.safe_load(gate.read(acceptance_run)) or {}
        except yaml.YAMLError:
            run_document = {}
        if isinstance(run_document, dict):
            run_id = str(run_document.get("run_id", "")).upper()
            if re.fullmatch(r"ARUN-[A-Z0-9-]+", run_id):
                run_items = [item for item in run_document.get("items", []) or [] if isinstance(item, dict)]
                environment = str(run_document.get("environment", "")).casefold()
                acceptance_claims[run_id] = {
                    "browser": is_browser,
                    "integration": bool(
                        re.search(r"\b(?:integration|sit|uat|staging)\b", environment)
                        or any(marker in environment for marker in ("集成", "联调", "预发布"))
                    ),
                    "conclusive": is_conclusive,
                    "baseline_version": str(run_document.get("baseline_version", "")),
                    "covered_acs": {
                        str(item.get("acceptance_ref", "")).upper()
                        for item in run_items if str(item.get("acceptance_ref", "")).upper().startswith("AC-")
                    },
                    "passed_acs": set(passed),
                    "failed_acs": {
                        str(item.get("acceptance_ref", "")).upper()
                        for item in run_items
                        if item.get("result") in {"fail", "blocked"}
                        and str(item.get("acceptance_ref", "")).upper().startswith("AC-")
                    },
                    "failed": str(run_document.get("conclusion", "")).casefold() == "rejected"
                    or any(
                        isinstance(item, dict) and item.get("result") in {"fail", "blocked"}
                        for item in run_document.get("items", []) or []
                    ),
                }
        evidenced_acs.update(passed)
        browser_evidence = browser_evidence or is_browser
        conclusive_evidence = conclusive_evidence or is_conclusive
    for review_path, review_document in gate.review_workspace_contracts:
        scenarios = [item for item in review_document.get("scenarios", []) or [] if isinstance(item, dict)]
        expected_baseline_version = str((review_document.get("baseline") or {}).get("version", ""))
        for step in review_document.get("steps", []) or []:
            if not isinstance(step, dict):
                continue
            status = str(step.get("verification_status", "not_run")).casefold()
            if status not in {"browser_checked", "integration_checked", "accepted", "failed"}:
                continue
            step_id = str(step.get("step_id", "STEP-UNKNOWN"))
            claimed_runs = {
                str(item).upper() for item in step.get("evidence_refs", []) or []
                if str(item).upper().startswith("ARUN-")
            }
            resolved = [acceptance_claims[item] for item in claimed_runs if item in acceptance_claims]
            if not claimed_runs or len(resolved) != len(claimed_runs):
                missing = sorted(claimed_runs - set(acceptance_claims)) or ["ARUN-* missing"]
                gate.add(
                    "BLOCK", "PROTO-REVIEW-VERIFICATION-ARUN-UNRESOLVED", review_path,
                    "验证状态引用的 ARUN 未随本次门禁提供，证据等级不可解析",
                    f"{step_id}: {', '.join(missing)}",
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
                continue
            drifted_runs = sorted(
                run_id for run_id in claimed_runs
                if acceptance_claims[run_id]["baseline_version"] != expected_baseline_version
            )
            if drifted_runs:
                gate.add(
                    "BLOCK", "PROTO-REVIEW-VERIFICATION-BASELINE-DRIFT", review_path,
                    "评审步骤引用的 ARUN 不属于当前 review baseline version",
                    f"{step_id}: {', '.join(drifted_runs)}",
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
                continue
            qa_packet = ((step.get("role_packets") or {}).get("qa") or {})
            scenario_refs = {str(item).upper() for item in qa_packet.get("scenario_refs", []) or []}
            required_acs = {
                str(item.get("acceptance_ref", "")).upper()
                for item in scenarios
                if (
                    str(item.get("scenario_id", "")).upper() in scenario_refs
                    or step_id in {str(ref).upper() for ref in item.get("covered_step_refs", []) or []}
                )
                and str(item.get("acceptance_ref", "")).upper().startswith("AC-")
            }
            covered_acs = set().union(*(item["covered_acs"] for item in resolved))
            if not required_acs or not required_acs <= covered_acs:
                missing = required_acs - covered_acs
                gate.add(
                    "BLOCK", "PROTO-REVIEW-VERIFICATION-AC-UNPROVED", review_path,
                    "ARUN 没有覆盖当前 STEP 对应的 TEST→AC，不能用无关验收记录升级验证状态",
                    f"{step_id}: {', '.join(sorted(missing or required_acs)) or 'AC-* missing'}",
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
                continue
            status_supported_acs = (
                set().union(*(item["covered_acs"] for item in resolved if item["browser"]))
                if status == "browser_checked" else
                set().union(*(item["covered_acs"] for item in resolved if item["integration"]))
                if status == "integration_checked" else
                set().union(*(item["passed_acs"] for item in resolved if item["conclusive"]))
                if status == "accepted" else
                set().union(*(item["failed_acs"] for item in resolved))
            )
            level_supported = (
                bool(required_acs & status_supported_acs) if status == "failed"
                else required_acs <= status_supported_acs
            )
            if not level_supported:
                gate.add(
                    "BLOCK", "PROTO-REVIEW-VERIFICATION-LEVEL-UNPROVED", review_path,
                    "已提供 ARUN 的环境或结论不足以支撑当前 verification_status",
                    f"{step_id}: {status}",
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
    if valid_prototypes and prototype_level in {"L3", "L4"}:
        if not valid_acceptance_runs:
            gate.add(
                "GAP", "PROTO-BROWSER-EVIDENCE-MISSING", valid_prototypes[0],
                "L3/L4 原型只完成静态检查；未提供 ARUN-* 浏览器逐动作证据",
                affected_consumers=("product", "ux", "frontend", "qa", "customer_acceptor"),
            )
        else:
            missing_acs = sorted(gate.prototype_acceptance_refs - evidenced_acs)
            if missing_acs:
                gate.add(
                    "GAP", "PROTO-BROWSER-EVIDENCE-INCOMPLETE", valid_acceptance_runs[0],
                    f"浏览器验收缺少 {len(missing_acs)} 个原型 AC",
                    ", ".join(missing_acs[:20]), related_refs=tuple(missing_acs[:100]),
                )
            if not browser_evidence:
                gate.add("GAP", "PROTO-BROWSER-EVIDENCE-INCOMPLETE", valid_acceptance_runs[0], "ARUN environment 未声明真实浏览器/浏览器自动化环境", "environment")
            if not conclusive_evidence:
                gate.add("GAP", "PROTO-BROWSER-EVIDENCE-INCOMPLETE", valid_acceptance_runs[0], "ARUN 尚未形成 accepted/accepted_with_conditions 且有签署的结论", "conclusion/sign_offs")
    gate.metrics["prototype_browser_evidence"] = bool(valid_acceptance_runs and browser_evidence and conclusive_evidence)
    gate.metrics["acceptance_run_conclusive"] = bool(valid_acceptance_runs and conclusive_evidence)
    custom_root = args.custom_root
    if custom_root is None and (Path.cwd() / "custom").is_dir():
        custom_root = Path.cwd() / "custom"
    if custom_root is not None:
        artifact_map = {
            "requirement": [args.requirement] if args.requirement and args.requirement.is_file() else [],
            "prd": [args.prd] if args.prd and args.prd.is_file() else [],
            "prototype": valid_prototypes,
            "stage0": [args.inventory] if args.inventory and args.inventory.is_file() else [],
            "handoff": [args.manifest] if args.manifest and args.manifest.is_file() else [],
        }
        gate.check_custom_rules(custom_root, artifact_map, active_domains=tuple(args.domain))
    retry_command = "python scripts/quality_gate.py " + subprocess.list2cmdline(sys.argv[1:])
    output_language = resolve_output_language(gate, args.language)
    payload = result_payload(gate, args.profile, retry_command, output_language)
    if args.format == "json":
        # ASCII escaping keeps JSON deterministic even when callers force a legacy
        # console encoding; message_zh remains lossless after JSON decoding.
        print(json.dumps({key: value for key, value in payload.items() if key != "exit_code"}, ensure_ascii=True, indent=2))
    else:
        summary = payload["summary"]
        print(
            f"{payload['status']} profile={args.profile} blockers={summary['blockers']} "
            f"p0_unknowns={summary['p0_unknowns']} gaps={summary['gaps']}"
        )
        english = output_language.casefold().startswith("en")
        print("NOT_PROVEN: " + ("; " if english else "；").join(payload["not_proven"]))
        labels = ("Cause", "Fix", "Example") if english else ("原因", "修复", "示例")
        actionable_findings = [item for item in gate.findings if item.severity != "INFO"]
        information_findings = [item for item in gate.findings if item.severity == "INFO"]
        if args.diagnostics == "roots":
            roots, unique_count = diagnostic_roots(actionable_findings, args.max_findings)
            for item, count in roots:
                ref = f" [{item.ref}]" if item.ref else ""
                localized = localized_finding(item, output_language)
                print(f"{item.severity} {item.code} x{count}{ref}: {localized['message']}")
                print(f"  {labels[0]}: {localized['cause']}")
                print(f"  {labels[1]}: {localized['how_to_fix']}")
                print(f"  {labels[2]}: {localized['repair_example']}")
            print(
                f"ROOT_GROUPS shown={len(roots)} unique={unique_count} "
                f"repeated_findings_compacted={len(actionable_findings) - len(roots)}"
            )
            hidden_groups = unique_count - len(roots)
            if hidden_groups > 0:
                print(f"... {hidden_groups} additional root groups; rerun with --format json")
        else:
            limit = 1 if args.diagnostics == "first" else min(max(args.max_findings, 0), 12) if args.diagnostics == "summary" else max(args.max_findings, 0)
            for item in actionable_findings[:limit]:
                ref = f" [{item.ref}]" if item.ref else ""
                localized = localized_finding(item, output_language)
                print(f"{item.severity} {item.code}{ref}: {localized['message']}")
                print(f"  {labels[0]}: {localized['cause']}")
                print(f"  {labels[1]}: {localized['how_to_fix']}")
                print(f"  {labels[2]}: {localized['repair_example']}")
            hidden = len(actionable_findings) - limit
            if hidden > 0:
                print(f"... {hidden} additional findings; rerun with --format json")
        for item in information_findings[: min(max(args.max_findings, 0), 5)]:
            localized = localized_finding(item, output_language)
            ref = f" [{item.ref}]" if item.ref else ""
            print(f"INFO {item.code}{ref}: {localized['message']}")
        if len(information_findings) > 5:
            print(f"... {len(information_findings) - 5} additional INFO records; rerun with --format json")
        if actionable_findings:
            print(f"RETRY: {payload['retry_command']}")
    return int(payload["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
