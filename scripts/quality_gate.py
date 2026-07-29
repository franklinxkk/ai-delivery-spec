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
    print(
        f"缺少运行依赖 {missing}。请先执行：python -m pip install -r scripts/requirements.txt",
        file=sys.stderr,
    )
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


def not_proven_for(gate: "Gate") -> list[str]:
    """Keep static-gate boundaries honest while closing claims backed by valid ARUN evidence."""
    items = list(NOT_PROVEN_BY_STATIC_GATE)
    if gate.metrics.get("prototype_browser_evidence"):
        items.remove("原型在真实浏览器中的交互、视觉、可访问性与多端适配")
        items.append("浏览器 ARUN 已证明其记录范围内的交互结果；未覆盖的视觉、可访问性与多端适配仍未证明")
    if gate.metrics.get("acceptance_run_conclusive"):
        items.remove("验收用例已经实际执行并形成签认证据")
        items.append("已提供的 ARUN 已执行并形成可解析签认证据；未纳入该记录的验收范围仍未证明")
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
    "PRD-STATE-SEMANTIC-POLLUTION": (
        "状态机表的当前状态/下一状态列写入了 API/FLD/ACT 等工程 ID，状态语义被污染。",
        "状态列只写业务状态名（如 draft、active）；工程 ID 移回动作/规则/接口列或附录。",
    ),
    "HANDOFF-BINDING-TERM-MISSING": (
        "PRD 声明的绑定词没有同时出现在 PRD 正文和原型可见文本中，跨端用词不一致。",
        "让 finding.ref 指示的绑定词原样出现在 PRD 正文和原型可见文案中，或在评审后收窄 binding_terms 声明。",
    ),
    "PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT": (
        "同一主题同时登记为已确认决策和未关闭未知项，基线语义自相矛盾。",
        "二选一：关闭对应 UNK-* 并同步 open_p0_unknown_ids，或撤回该决策条目并重新登记为开放未知项。",
    ),
    "HANDOFF-AESTHETIC-UNDECIDED": (
        "L3/L4 交接没有声明视觉权威与视觉锁，跨页面风格可能漂移。",
        "存量小迭代记录 visual_authority=existing；绿地记录 greenfield_default；品牌化方案可引用 DEC-AESTHETIC-*，并提供 design_lock_ref。",
    ),
    "STAGE0-DISPOSITION-MISSING": (
        "Stage 0 台账的页面类条目缺少 disposition，存量页面处置方式未定。",
        "为该条目补 disposition：adopt_page / inherit_layout / rebuild_interaction / reuse_component / discard。",
    ),
    "STAGE0-LEGACY-INVENTORY": (
        "Stage 0 台账仍是旧版按 roles/views/actions 等分栏保存的结构，缺少当前逐项审计合同。",
        "将旧分栏逐项迁入 items；每项补齐 type、source_ref、source_location、classification，推断项再绑定有 owner 的 RBATCH-*。",
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
    ("PROTO-CSS-", "CSS 污染可能隐藏或破坏交互状态。", "移除全局 !important 污染，并将可见性规则限制在所属组件和 data-state。"),
    ("PROTO-", "原型缺少可测试交互或状态合同。", "使用稳定 data-testid/data-action/data-state/data-field 和可见结果修复对应元素。"),
    ("PRD-", "PRD 缺少当前交付阶段所需的需求合同。", "按引用位置补齐经确认的规则、稳定 ID、异常和验收，不得发明值。"),
    ("REQ-", "需求生命周期记录不完整或不一致。", "修复对应字段并保留稳定 ID、来源、决策和审计历史。"),
)


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


REPAIR_EXAMPLES: tuple[tuple[str, str], ...] = (
    ("INTAKE-SCHEMA", "cp references/templates/requirement-intake-template.yaml intake.yaml，补齐 artifact: requirement_intake、stage: intake、source_refs: [SRC-*]、value_evidence 等必填字段。"),
    ("PROTO-DEMO-SCAFFOLDING-VISIBLE", "删除 <div>验收场景</div> 这类演示文案块，改为真实业务空态文案，如 <p>暂无待办事项</p>。"),
    ("PROTO-NESTED-PRODUCT-IFRAME", "移除 <iframe src=\"child.html\">，把 child.html 的页面迁移为当前文件内的 <section data-testid=\"page-VIEW-CHILD-001\">。"),
    ("PRD-STATE-SEMANTIC-POLLUTION", "| 待处理 | 复检 | 复检中 | —— 下一状态列写业务状态名；API-RISK-RECHECK 移入“动作/接口”列。"),
    ("HANDOFF-BINDING-TERM-MISSING", "PRD 正文写“上传道路运输经营许可证后进入审核”，原型对应区域可见文案同样写“道路运输经营许可证”。"),
    ("PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT", "关闭冲突项：unknowns 中该 key 的 status 改为 closed 并从 open_p0_unknown_ids 移除；或删除 decisions 中同 key 条目改登 UNK-*。"),
    ("HANDOFF-AESTHETIC-UNDECIDED", "存量小迭代写 visual_authority: existing 与 design_lock_ref: prototype.html#design-lock；绿地可写 greenfield_default；品牌化方案再引用 DEC-AESTHETIC-*。"),
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
    ("STAGE0-", "为反推项使用 INV-*，保留 source_ref/location；推断项绑定 review_batch_ref，由责任人批量确认。"),
    ("GATE-", "按 finding.ref 修正输入或配置，然后复制 RETRY 命令重跑。"),
)


def repair_example_for(code: str) -> str:
    for prefix, example in REPAIR_EXAMPLES:
        if code.startswith(prefix):
            return example
    return "按 finding.ref 只修复该项，保留稳定 ID 与来源证据，再重跑门禁。"


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
        cause, how_to_fix = guidance_for(code)
        self.findings.append(Finding(
            severity=severity,
            code=code,
            artifact=str(path),
            message=message,
            ref=ref,
            cause=cause,
            how_to_fix=how_to_fix,
            repair_example=repair_example_for(code),
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


def result_payload(gate: Gate, profile: str, retry_command: str = "") -> dict[str, Any]:
    blocks = sum(item.severity == "BLOCK" for item in gate.findings)
    p0_unknowns = sum(item.severity == "P0_UNKNOWN" for item in gate.findings)
    gaps = sum(item.severity == "GAP" for item in gate.findings)
    code = 2 if blocks else 3 if p0_unknowns else 1 if gaps else 0
    rendered_findings = []
    for item in gate.findings:
        record = asdict(item)
        localized_message = item.message if re.search(r"[\u4e00-\u9fff]", item.message) else f"{item.cause} 技术明细：{item.message}"
        record.update({
            "message_zh": localized_message,
            "cause_zh": item.cause,
            "fix_zh": item.how_to_fix,
            "repair_example_zh": item.repair_example,
        })
        rendered_findings.append(record)
    consumed_browser_evidence = bool(gate.metrics.get("prototype_browser_evidence"))
    coverage = "确定性静态门禁；不调用浏览器、LLM 或子 Agent"
    if consumed_browser_evidence:
        coverage += "；已校验外部真实浏览器 ARUN 的结构、证据与签署"
    return {
        "status": STATUSES[code],
        "profile": profile,
        "summary": {"blockers": blocks, "p0_unknowns": p0_unknowns, "gaps": gaps, "findings": len(gate.findings)},
        "coverage": coverage,
        "not_proven": not_proven_for(gate),
        "retry_command": retry_command,
        "metrics": {**gate.metrics, "input_read_counts": dict(gate.read_counts)},
        "findings": rendered_findings,
        "exit_code": code,
    }


def diagnostic_roots(findings: list[Finding], limit: int) -> tuple[list[tuple[Finding, int]], int]:
    """Compact repeated findings by stable root-cause code, preserving first-seen order."""
    first: dict[str, Finding] = {}
    counts: dict[str, int] = {}
    order: list[str] = []
    for item in findings:
        if item.code not in first:
            first[item.code] = item
            order.append(item.code)
        counts[item.code] = counts.get(item.code, 0) + 1
    selected = order[:max(limit, 0)]
    return [(first[code], counts[code]) for code in selected], len(order)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lightweight, non-generative final quality gate")
    parser.add_argument("--profile", choices=["requirement", "prd", "prototype", "handoff", "full", "stage0", "agent_handoff"], required=True)
    parser.add_argument("--requirement", type=Path, help="requirement register YAML")
    parser.add_argument("--prd", type=Path, help="unified PRD Markdown")
    parser.add_argument("--prototype", type=Path, action="append", help="HTML prototype; repeat for admin/H5/multi-surface handoff")
    parser.add_argument("--inventory", type=Path, help="Stage 0 brownfield inventory YAML")
    parser.add_argument("--manifest", type=Path, help="Agent handoff manifest YAML")
    parser.add_argument("--acceptance-run", type=Path, action="append", help="Executed ARUN-* YAML; repeat when prototype AC evidence is split")
    parser.add_argument("--level", choices=["auto", *LEVELS], default="L2")
    parser.add_argument("--stage", choices=list(STAGE_ORDER), default="baseline")
    parser.add_argument("--scope-ref", action="append", default=[], help="Limit stage/P0 evaluation to one stable-ID scope; repeat as needed")
    parser.add_argument("--format", choices=["concise", "json"], default="concise")
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
    if args.profile in {"handoff", "full"} and valid_prd and valid_prototypes:
        gate.check_handoff(valid_prd, valid_prototypes, prototype_level)
    if args.profile in {"handoff", "full"} and valid_prd and args.manifest and args.manifest.is_file():
        gate.check_manifest_prd_binding(valid_prd, args.manifest)
    valid_acceptance_runs: list[Path] = []
    evidenced_acs: set[str] = set()
    browser_evidence = False
    conclusive_evidence = False
    for acceptance_run in args.acceptance_run or []:
        if not acceptance_run.is_file():
            gate.add("BLOCK", "GATE-NOT-FILE", acceptance_run, "input does not exist or is not a file", "acceptance-run")
            continue
        valid_acceptance_runs.append(acceptance_run)
        passed, is_browser, is_conclusive = gate.check_acceptance_run(acceptance_run)
        evidenced_acs.update(passed)
        browser_evidence = browser_evidence or is_browser
        conclusive_evidence = conclusive_evidence or is_conclusive
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
        gate.check_custom_rules(custom_root, artifact_map)
    retry_command = "python scripts/quality_gate.py " + subprocess.list2cmdline(sys.argv[1:])
    payload = result_payload(gate, args.profile, retry_command)
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
        print("NOT_PROVEN: " + "；".join(payload["not_proven"]))
        if args.diagnostics == "roots":
            roots, unique_count = diagnostic_roots(gate.findings, args.max_findings)
            for item, count in roots:
                ref = f" [{item.ref}]" if item.ref else ""
                localized = item.message if re.search(r"[\u4e00-\u9fff]", item.message) else f"{item.cause} 技术明细：{item.message}"
                print(f"{item.severity} {item.code} x{count}{ref}: {localized}")
                print(f"  原因: {item.cause}")
                print(f"  修复: {item.how_to_fix}")
                print(f"  示例: {item.repair_example}")
            print(
                f"ROOT_GROUPS shown={len(roots)} unique={unique_count} "
                f"repeated_findings_compacted={len(gate.findings) - len(roots)}"
            )
            hidden_groups = unique_count - len(roots)
            if hidden_groups > 0:
                print(f"... {hidden_groups} additional root groups; rerun with --format json")
        else:
            limit = 1 if args.diagnostics == "first" else min(max(args.max_findings, 0), 12) if args.diagnostics == "summary" else max(args.max_findings, 0)
            for item in gate.findings[:limit]:
                ref = f" [{item.ref}]" if item.ref else ""
                localized = item.message if re.search(r"[\u4e00-\u9fff]", item.message) else f"{item.cause} 技术明细：{item.message}"
                print(f"{item.severity} {item.code}{ref}: {localized}")
                print(f"  原因: {item.cause}")
                print(f"  修复: {item.how_to_fix}")
                print(f"  示例: {item.repair_example}")
            hidden = len(gate.findings) - limit
            if hidden > 0:
                print(f"... {hidden} additional findings; rerun with --format json")
        if gate.findings:
            print(f"RETRY: {payload['retry_command']}")
    return int(payload["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
