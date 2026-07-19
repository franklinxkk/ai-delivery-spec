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
from validators.validate_coding_agent_contract import (
    BASE_AREAS,
    ID_RULES,
    STRUCTURED_AC_FIELDS,
    has_any,
)
from validators.validate_prd_quality import LEVELS, TERMS


ROOT = SCRIPT_DIR.parent
REGISTER_SCHEMA = ROOT / "schemas" / "requirement-register.schema.json"
HANDOFF_SCHEMA = ROOT / "schemas" / "agent-handoff.schema.json"
ACCEPTANCE_SCHEMA = ROOT / "schemas" / "acceptance-run.schema.json"
MAIN_MARKERS = ("背景", "需求准入", "角色", "角色旅程", "业务流程", "功能总览", "分模块功能需求", "验收方案")
ANNEX_MARKERS = ("字段字典", "规则与状态机", "api", "机器可读验收", "双向追溯", "禁止推断")
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
    "视觉与美学方向已经用户确认（DEC-AESTHETIC-* 或等效记录）",
    "代码实现、数据迁移、安全、性能、部署与运行稳定性",
    "验收用例已经实际执行并形成签认证据",
)


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
        "修复 YAML 缩进、引号或编码后重新校验。",
    ),
    "REQ-SCHEMA": (
        "需求登记文件不符合 JSON Schema。",
        "按 finding.ref 定位字段，并参考 requirement-register-template.yaml 修复结构。",
    ),
    "PRD-STRUCTURE": (
        "文档虽然包含标题或关键词，但没有可验证的统一 PRD 结构。",
        "按统一 PRD 模板补齐真实业务叙述或工程附录，不要复制空标题。",
    ),
    "PRD-TOO-THIN": (
        "当前交付等级所需的页面、规则或验收细节不足。",
        "补齐适用合同，不要用空标题或关键词填充。",
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


class Gate:
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
    def _page_contracts(raw: str) -> dict[str, tuple[dict[str, str], str]]:
        markers = list(re.finditer(
            r"<!--\s*PAGE-CONTRACT:\s*(VIEW-[A-Z0-9-]+)\s*(.*?)-->", raw, re.I | re.S
        ))
        contracts: dict[str, tuple[dict[str, str], str]] = {}
        for index, marker in enumerate(markers):
            end = markers[index + 1].start() if index + 1 < len(markers) else len(raw)
            attrs: dict[str, str] = {}
            tail = marker.group(2).strip().lstrip(";").strip()
            for part in tail.split(";") if tail else []:
                if "=" not in part:
                    continue
                key, value = part.split("=", 1)
                attrs[key.strip().lower()] = value.strip()
            contracts[marker.group(1).upper()] = (attrs, raw[marker.end():end])
        return contracts

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

    def _check_authority(self, path: Path, frontmatter: dict[str, Any]) -> None:
        governance = frontmatter.get("governance") or {}
        if not isinstance(governance, dict):
            self.add("BLOCK", "AUTH-BAD-GOVERNANCE", path, "governance 必须是对象", "governance")
            return
        canonical = governance.get("canonical_authoring_surface")
        legacy = frontmatter.get("authority_mode")
        if legacy and canonical and str(legacy) != str(canonical):
            self.add(
                "BLOCK", "AUTH-LEGACY-CONFLICT", path,
                "authority_mode 与 canonical_authoring_surface 冲突",
                "governance.canonical_authoring_surface",
                affected_consumers=("product", "architect", "coding_agent"),
            )
        binding_sources = governance.get("binding_sources") or []
        if not isinstance(binding_sources, list):
            self.add("BLOCK", "AUTH-BAD-BINDING-SOURCES", path, "binding_sources 必须是数组", "governance.binding_sources")
            binding_sources = []
        canonical_sources = list(frontmatter.get("canonical_candidates") or [])
        canonical_sources.extend(
            item for item in binding_sources
            if isinstance(item, dict) and item.get("canonical") is True
        )
        conflicts = governance.get("source_conflicts") or frontmatter.get("source_conflicts") or []
        unresolved = [
            item for item in conflicts
            if isinstance(item, dict) and str(item.get("status", "open")).lower() not in {"resolved", "closed", "superseded"}
        ]
        conflict_decisions = {
            str(item.get("decision_ref", ""))
            for item in conflicts if isinstance(item, dict) and item.get("decision_ref")
        }
        if len(canonical_sources) > 1 and not any(ref.startswith("DEC-CONFLICT-") for ref in conflict_decisions):
            refs = tuple(
                str(item.get("source_ref") if isinstance(item, dict) else item)
                for item in canonical_sources
            )
            self.add(
                "BLOCK", "AUTH-MULTIPLE-CANONICAL-SOURCES", path,
                "同一基线存在多个 canonical 候选，且没有 DEC-CONFLICT-* 裁决",
                ", ".join(refs),
                affected_consumers=("product", "architect", "qa", "coding_agent"),
                binding_source_refs=refs,
            )
        for item in unresolved:
            conflict_id = str(item.get("id", "DEC-CONFLICT-MISSING"))
            refs = tuple(str(ref) for ref in item.get("source_refs", []) or [])
            self.add(
                "BLOCK", "AUTH-UNRESOLVED-SOURCE-CONFLICT", path,
                "来源冲突尚未由解释责任人裁决",
                conflict_id,
                affected_consumers=("product", "architect", "compliance"),
                related_refs=tuple(str(ref) for ref in item.get("affected_refs", []) or []),
                binding_source_refs=refs,
            )
        if canonical == "product_truth":
            if not str(governance.get("decision_ref", "")).startswith("DEC-"):
                self.add("BLOCK", "AUTH-TRUTH-NO-DECISION", path, "Product Truth 写入面缺少 DEC-*", "governance.decision_ref")
            if not governance.get("projection_policy"):
                self.add("BLOCK", "AUTH-TRUTH-NO-PROJECTION-POLICY", path, "Product Truth 写入面缺少投影同步规则", "governance.projection_policy")

    @staticmethod
    def _scope_intersects(affected: list[str], active: tuple[str, ...]) -> bool:
        if not active or not affected:
            return True
        for left in affected:
            prefix = str(left).rstrip("*")
            for right in active:
                right_prefix = str(right).rstrip("*")
                if str(right).startswith(prefix) or str(left).startswith(right_prefix):
                    return True
        return False

    def _check_unknowns(
        self,
        path: Path,
        raw: str,
        frontmatter: dict[str, Any],
        *,
        stage: str,
        scope_refs: tuple[str, ...],
    ) -> None:
        open_ids_raw = frontmatter.get("open_p0_unknown_ids", [])
        if not isinstance(open_ids_raw, list):
            self.add(
                "BLOCK", "PRD-BAD-P0-DISPOSITION", path,
                "open_p0_unknown_ids 必须是数组；字符串或自由文本会导致 P0 状态不可判定",
                "frontmatter.open_p0_unknown_ids",
            )
            return
        open_ids = {str(item).upper() for item in open_ids_raw}
        invalid_open_ids = sorted(item for item in open_ids if not re.fullmatch(r"UNK-[A-Z0-9-]+", item, re.I))
        if invalid_open_ids:
            self.add(
                "BLOCK", "PRD-P0-UNKNOWN-ID-NOT-UNK", path,
                "open_p0_unknown_ids 只能登记结构化 UNK-*；REV/DEC/GAP 不能代替阻塞未知项",
                ", ".join(invalid_open_ids),
                affected_consumers=("product", "qa", "coding_agent"),
                related_refs=tuple(invalid_open_ids),
            )
        records: dict[str, dict[str, Any]] = {}
        for item in frontmatter.get("unknowns", []) or []:
            if isinstance(item, dict) and re.fullmatch(r"UNK-[A-Z0-9-]+", str(item.get("id", "")), re.I):
                records[str(item["id"]).upper()] = item
        # Support a compact Markdown unknown table without treating arbitrary prose as data.
        for line in raw.splitlines():
            if not line.lstrip().startswith("|") or not re.search(r"\bUNK-[A-Z0-9-]+\b", line, re.I):
                continue
            unknown_id = re.search(r"\bUNK-[A-Z0-9-]+\b", line, re.I).group(0).upper()
            if unknown_id in records:
                continue
            lowered = line.lower()
            priority = "P0" if re.search(r"\bP0\b", line, re.I) else "P1"
            status = "blocked" if any(term in lowered for term in ("blocked", "阻塞", "open", "未关闭")) else "closed"
            stage_match = next((name for name in STAGE_ORDER if name in lowered), None)
            affected_refs = re.findall(r"\b(?:REQ|FLOW|VIEW|STATE|RULE|API|AC)-[A-Z0-9-]+\b", line, re.I)
            records[unknown_id] = {
                "id": unknown_id, "priority": priority, "status": status,
                "blocks_stage": stage_match or "baseline", "affected_refs": affected_refs,
            }
        record_open = {
            unknown_id for unknown_id, item in records.items()
            if str(item.get("priority", "")).upper() == "P0"
            and str(item.get("status", "open")).lower() in {"open", "blocked", "阻塞中", "未关闭"}
        }
        missing_records = sorted(open_ids - set(records))
        if missing_records:
            self.add(
                "BLOCK", "PRD-P0-UNKNOWN-NOT-STRUCTURED", path,
                "open_p0_unknown_ids 中的条目缺少 unknowns 结构化记录，无法判断责任人、阻断阶段与影响范围",
                ", ".join(missing_records),
                affected_consumers=("product", "architect", "qa", "coding_agent"),
                related_refs=tuple(missing_records),
            )
        if record_open != open_ids:
            self.add(
                "BLOCK", "PRD-P0-UNKNOWN-INDEX-DRIFT", path,
                "frontmatter 与结构化未知项表的未关闭 P0 ID 不一致",
                f"frontmatter={sorted(open_ids)} records={sorted(record_open)}",
                affected_consumers=("product", "qa", "coding_agent"),
                related_refs=tuple(sorted(open_ids | record_open)),
            )
        current_rank = STAGE_ORDER.get(stage, STAGE_ORDER["baseline"])
        for unknown_id in sorted(open_ids):
            item = records.get(unknown_id, {})
            blocks_stage = item.get("blocks_stage", "baseline")
            if isinstance(blocks_stage, list):
                ranks = [STAGE_ORDER.get(str(value), STAGE_ORDER["baseline"]) for value in blocks_stage]
                block_rank = min(ranks) if ranks else STAGE_ORDER["baseline"]
            else:
                block_rank = STAGE_ORDER.get(str(blocks_stage), STAGE_ORDER["baseline"])
            affected = [str(ref) for ref in item.get("affected_refs", []) or []]
            if current_rank >= block_rank and self._scope_intersects(affected, scope_refs):
                self.add(
                    "P0_UNKNOWN", "PRD-OPEN-P0-UNKNOWN", path,
                    f"P0 未知项阻断当前 {stage} 阶段",
                    unknown_id,
                    affected_consumers=("product", "architect", "qa", "coding_agent"),
                    related_refs=(unknown_id, *affected),
                )
            else:
                self.add(
                    "GAP", "PRD-P0-UNKNOWN-NOT-YET-BLOCKING", path,
                    f"P0 未知项尚未阻断当前 {stage} 阶段，但必须在 {blocks_stage} 前关闭",
                    unknown_id,
                    affected_consumers=("product",),
                    related_refs=(unknown_id, *affected),
                )

        in_fence = False
        for line_no, line in enumerate(raw.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence or re.search(r"\bUNK-[A-Z0-9-]+\b", line, re.I) or "placeholder=" in line.lower():
                continue
            marker = re.search(r"\b(?:TBD|TODO|FIXME|STUB)\b|待补充|以后再说|暂未定义", line)
            if marker:
                severity = "BLOCK" if re.search(r"\bP0\b", line, re.I) else "GAP"
                self.add(
                    severity, "PRD-UNDECLARED-UNKNOWN", path,
                    f"发现未登记未知项标记：{marker.group(0)}",
                    f"line {line_no}",
                    affected_consumers=("product", "qa", "coding_agent"),
                )

    def _check_triggered_contracts(
        self, path: Path, raw: str, frontmatter: dict[str, Any], level: str
    ) -> None:
        lowered = raw.lower()
        assurance = str(frontmatter.get("assurance_profile", "standard")).lower()
        if assurance in {"high_risk", "safety_critical"}:
            critical = re.compile(
                r"资金|支付|结算|对账|退款|合规|监管|牌照|责任|赔偿|保险|担保|隐私|跨境|个人信息|AML|KYC|GDPR|PIPL",
                re.I,
            )
            for line_no, line in enumerate(raw.splitlines(), 1):
                rule_match = re.search(r"\bRULE-[A-Z0-9-]+\b", line, re.I)
                if not rule_match or not critical.search(line):
                    continue
                if not re.search(r"\b(?:SRC|DEC|ASSUMPTION)-[A-Z0-9-]+\b|明确假设", line, re.I):
                    rule_id = rule_match.group(0).upper()
                    self.add(
                        "BLOCK", "PRD-HIGH-RISK-RULE-NO-SOURCE", path,
                        "高风险规则必须绑定 SRC/DEC 或显式假设",
                        f"{rule_id}@line {line_no}",
                        affected_consumers=("product", "architect", "compliance", "qa", "coding_agent"),
                        related_refs=(rule_id,),
                    )
        ai_runtime = frontmatter.get("ai_runtime") is True or str(frontmatter.get("ai_runtime", "")).lower() == "yes"
        if ai_runtime:
            ai_terms = {
                "input/output schema": ("input schema", "output schema", "输入 schema", "输出 schema", "输入输出 schema"),
                "version": ("模型版本", "提示版本", "prompt version", "model version"),
                "tool permission": ("工具权限", "tool permission", "tool scope"),
                "human gate": ("人工门", "人工审核", "human gate", "human review"),
                "fallback": ("回退", "降级", "fallback"),
                "evaluation": ("评测", "eval"),
                "observability": ("观测", "observability", "trace"),
            }
            for label, terms in ai_terms.items():
                if not any(term in lowered for term in terms):
                    self.add(
                        "BLOCK", "AI-RUNTIME-MISSING-CONTRACT", path,
                        f"AI Runtime 合同缺少 {label}", label,
                        affected_consumers=("product", "architect", "qa", "coding_agent"),
                    )
        lineage = frontmatter.get("lineage") is True or str(frontmatter.get("lineage", "")).lower() == "yes"
        if lineage:
            for label, terms in {
                "source": ("来源", "source"),
                "transformation": ("转换", "transform"),
                "owner": ("责任人", "owner"),
                "impact": ("影响", "impact"),
            }.items():
                if not any(term in lowered for term in terms):
                    self.add("BLOCK", "PRD-LINEAGE-MISSING-CONTRACT", path, f"数据血缘合同缺少 {label}", label)

    def _check_testability(
        self, path: Path, raw: str, frontmatter: dict[str, Any], level: str
    ) -> None:
        if level not in {"L2", "L3", "L4"}:
            return
        req_ids = {item.upper() for item in re.findall(r"\bREQ-[A-Z0-9-]+\b", raw, re.I)}
        mapped: set[str] = set()
        for line in raw.splitlines():
            if re.search(r"\bAC-[A-Z0-9-]+\b", line, re.I):
                mapped.update(item.upper() for item in re.findall(r"\bREQ-[A-Z0-9-]+\b", line, re.I))
        for req_id in sorted(req_ids - mapped):
            self.add(
                "BLOCK", "PRD-REQ-NO-STRUCTURED-AC", path,
                "实现范围 REQ 没有绑定结构化 AC",
                req_id,
                affected_consumers=("product", "qa", "coding_agent"),
                related_refs=(req_id,),
            )
        headings = markdown_headings(raw)
        for index, (_level, title, start) in enumerate(headings):
            stm = re.search(r"\bSTM-[A-Z0-9-]+\b", title, re.I)
            if not stm:
                continue
            end = headings[index + 1][2] if index + 1 < len(headings) else len(raw)
            block = raw[start:end].lower()
            required = {
                "from/to": ("当前状态", "下一状态", "->", "→"),
                "action": ("动作", "action"),
                "guard/role": ("守卫", "允许角色", "guard", "role"),
                "failure": ("失败", "拒绝", "异常", "failure", "error"),
            }
            missing = []
            if not (("当前状态" in block and "下一状态" in block) or "->" in block or "→" in block):
                missing.append("from/to")
            for label in ("action", "guard/role", "failure"):
                if not any(term in block for term in required[label]):
                    missing.append(label)
            if missing:
                stm_id = stm.group(0).upper()
                self.add(
                    "BLOCK", "PRD-STATE-CONTRACT-INCOMPLETE", path,
                    "状态机缺少 " + ", ".join(missing), stm_id,
                    affected_consumers=("backend", "qa", "coding_agent"),
                    related_refs=(stm_id,),
                )
        page_contracts = self._page_contracts(raw)
        workflow = any(
            "workflow" in {item.strip().lower() for item in attrs.get("surfaces", "").split(",")}
            for attrs, _block in page_contracts.values()
        ) or frontmatter.get("workflow") is True
        if workflow:
            has_flow = bool(re.search(r"\bFLOW-[A-Z0-9-]+\b", raw, re.I))
            has_e2e = bool(re.search(r"端到端验收|e2e acceptance|E2E-[A-Z0-9-]+", raw, re.I))
            if not (has_flow and has_e2e):
                self.add(
                    "BLOCK", "PRD-WORKFLOW-NO-E2E", path,
                    "workflow 页面必须绑定端到端 FLOW 和 E2E 验收",
                    affected_consumers=("product", "qa", "coding_agent"),
                )

    def check_prd(
        self,
        path: Path,
        level: str,
        *,
        stage: str = "baseline",
        scope_refs: tuple[str, ...] = (),
    ) -> None:
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "PRD-READ", path, f"PRD cannot be read: {exc}")
            return
        lowered = raw.lower()
        frontmatter = self._frontmatter(raw)
        if level == "auto":
            declared_level = str(frontmatter.get("delivery_level", frontmatter.get("level", "L2"))).upper()
            level = declared_level if declared_level in LEVELS else "L2"
            self.metrics["resolved_level"] = level
            self.metrics["level_source"] = "frontmatter" if declared_level in LEVELS else "fallback_L2"

        # Human-first unified baseline contract (reuses validate_unified_prd rules).
        h1_count = len(re.findall(r"(?m)^#\s+[^#\n]", raw))
        if h1_count != 1:
            self.add("BLOCK", "PRD-ONE-H1", path, f"unified PRD needs exactly one H1 title; found {h1_count}")
        for marker in MAIN_MARKERS:
            if marker.lower() not in lowered:
                self.add("BLOCK", "PRD-HUMAN-PATH", path, f"human reading path misses {marker}", marker)
        for marker in ANNEX_MARKERS:
            if marker.lower() not in lowered:
                self.add("BLOCK", "PRD-ENGINEERING-ANNEX", path, f"engineering annex misses {marker}", marker)
        appendix_pos = _heading_position(
            raw,
            (r"^第四部分", r"^附录\s*A(?:\b|[：:])", r"工程与\s*AI\s*Coding\s*附录"),
        )
        journey_pos = _heading_position(raw, (r"角色旅程", r"用户旅程", r"role journey"))
        if appendix_pos < 0 or journey_pos < 0 or appendix_pos <= journey_pos:
            self.add("BLOCK", "PRD-READING-ORDER", path, "engineering annex must follow role journeys and module narrative")
        main = raw[:appendix_pos] if appendix_pos >= 0 else raw
        nonblank = [line for line in main.splitlines() if line.strip()]
        table_lines = [line for line in nonblank if line.lstrip().startswith("|")]
        if nonblank and len(table_lines) / len(nonblank) > 0.55:
            self.add("BLOCK", "PRD-TABLE-DOMINATED", path, "human main body is table-dominated; add readable journey/rule explanations")
        requirement_ids = set(re.findall(r"\bREQ-[A-Z0-9-]+\b", raw, re.I))
        trace_pos = _heading_position(raw, (r"双向追溯", r"bidirectional trace"), last=True)
        trace_text = raw[trace_pos:] if trace_pos >= 0 else ""
        traced = set(re.findall(r"\bREQ-[A-Z0-9-]+\b", trace_text, re.I))
        for req_id in sorted(requirement_ids - traced):
            self.add("BLOCK", "PRD-UNTRACED-REQ", path, "requirement is absent from the trace annex", req_id)
        if trace_text and (not re.search(r"\bAC-[A-Z0-9-]+\b", trace_text, re.I) or "反向" not in trace_text):
            self.add("BLOCK", "PRD-NO-REVERSE-TRACE", path, "trace annex must bind AC IDs and declare reverse lookup")
        if "两套 prd" not in lowered and "一份" not in lowered:
            self.add("BLOCK", "PRD-NO-ONE-BASELINE", path, "document does not declare one-baseline semantics")

        # Requirement quality contract (reuses validate_prd_quality vocabulary).
        for key in LEVELS[level]:
            if not any(term in lowered for term in TERMS[key]):
                self.add("BLOCK", "PRD-MISSING-CONTRACT", path, f"missing {key} requirement contract", key)
        if level in {"L2", "L3", "L4"}:
            for pattern, label in (
                (r"req-[a-z0-9-]+", "REQ"), (r"role-[a-z0-9-]+", "ROLE"),
                (r"flow-[a-z0-9-]+", "FLOW"), (r"(?:view|page)-[a-z0-9-]+", "VIEW/PAGE"),
                (r"act-[a-z0-9-]+", "ACT"), (r"ac-[a-z0-9-]+", "AC"),
            ):
                if not re.search(pattern, lowered):
                    self.add("BLOCK", "PRD-MISSING-ID", path, f"missing stable {label} IDs", label)

        # AI-coding annex contract (same areas/IDs/AC semantics, one in-memory scan).
        if level in {"L0", "L1"}:
            required_areas = {"goal": ("目标", "goal"), "scope": ("范围", "scope"), "acceptance": ("验收", "ac-")}
        else:
            required_areas = dict(BASE_AREAS)
        for area, terms in required_areas.items():
            if not has_any(lowered, terms):
                self.add("BLOCK", "PRD-CODING-AREA", path, "AI-coding contract area is absent", area)
        if level in {"L2", "L3", "L4"}:
            heading_count = len(re.findall(r"(?m)^#{2,4}\s+\S", raw))
            table_rows = len(re.findall(r"(?m)^\s*\|(?:[^\n|]+\|){2,}\s*$", raw))
            if heading_count < 14:
                self.add("BLOCK", "PRD-TOO-THIN", path, f"full unified PRD has {heading_count} section headings; need at least 14")
            if table_rows < 8:
                self.add("BLOCK", "PRD-NO-PRECISE-MAPPING", path, f"contract has {table_rows} table rows; need at least 8")
            for label, pattern in ID_RULES.items():
                if not re.search(pattern, raw, flags=re.I):
                    self.add("BLOCK", "PRD-MISSING-ID", path, f"missing stable {label}", label)
            for terms in STRUCTURED_AC_FIELDS:
                if not has_any(lowered, terms):
                    self.add("BLOCK", "PRD-AC-FIELD", path, f"structured acceptance misses {terms[0]}", terms[0])
            api_not_applicable = bool(re.search(r"(?:api|接口)[^\n]{0,80}(?:不适用|not applicable)", lowered))
            if not api_not_applicable:
                if not re.search(r"/(?:api|openapi)/|\b(?:get|post|put|patch|delete)\s+[`/]", lowered):
                    self.add("BLOCK", "PRD-API-ROUTE", path, "applicable API contract lacks method/path or explicit engineering-owned path decision")
                for label, terms in {
                    "request fields/body": ("request fields", "请求字段", "request body"),
                    "response fields/body": ("response fields", "成功响应", "response body", "统一响应"),
                    "error/idempotency": ("错误码", "业务错误", "error code", "幂等", "idempotency"),
                }.items():
                    if not has_any(lowered, terms):
                        self.add("BLOCK", "PRD-API-CONTRACT", path, f"API contract misses {label}", label)
            if not has_any(lowered, ("异常", "失败", "failure")):
                self.add("BLOCK", "PRD-NO-FAILURE", path, "contract misses failure behavior")
            for failure in analyze_prd_structure(raw, full_prd=True):
                self.add("BLOCK", "PRD-STRUCTURE", path, failure)
        self._check_authority(path, frontmatter)
        self._check_unknowns(path, raw, frontmatter, stage=stage, scope_refs=scope_refs)
        self._check_triggered_contracts(path, raw, frontmatter, level)
        self._check_testability(path, raw, frontmatter, level)

        if level in {"L3", "L4"}:
            if STAGE_ORDER.get(stage, STAGE_ORDER["baseline"]) >= STAGE_ORDER["baseline"]:
                acceptance_plan = frontmatter.get("acceptance_plan")
                if not isinstance(acceptance_plan, dict):
                    self.add(
                        "BLOCK", "PRD-NO-ACCEPTANCE-PLAN", path,
                        "L3/L4 基线必须声明验收计划，定义谁验、验什么、如何判定和留什么证据",
                        "frontmatter.acceptance_plan",
                        affected_consumers=("product", "qa", "delivery", "customer"),
                    )
                else:
                    required_plan_fields = {
                        "owner": bool(acceptance_plan.get("owner")),
                        "scope_refs/scope_rule": bool(acceptance_plan.get("scope_refs") or acceptance_plan.get("scope_rule")),
                        "pass_rule": bool(acceptance_plan.get("pass_rule")),
                        "evidence_types": isinstance(acceptance_plan.get("evidence_types"), list) and bool(acceptance_plan.get("evidence_types")),
                        "signoff_roles": isinstance(acceptance_plan.get("signoff_roles"), list) and bool(acceptance_plan.get("signoff_roles")),
                    }
                    for field, present in required_plan_fields.items():
                        if not present:
                            self.add(
                                "BLOCK", "PRD-INCOMPLETE-ACCEPTANCE-PLAN", path,
                                f"验收计划缺少 {field}", f"frontmatter.acceptance_plan.{field}",
                                affected_consumers=("product", "qa", "delivery", "customer"),
                            )
            source_refs = frontmatter.get("source_refs")
            if not isinstance(source_refs, list) or not source_refs:
                self.add("BLOCK", "PRD-NO-SOURCE-SCOPE", path, "L3/L4 handoff must declare non-empty source_refs in frontmatter")
                source_refs = []
            if not has_any(lowered, ("来源登记", "source register")):
                self.add("BLOCK", "PRD-NO-SOURCE-REGISTER", path, "L3/L4 handoff needs a source register with authority and disposition")
            for source_ref in [str(item).upper() for item in source_refs]:
                if len(re.findall(rf"\b{re.escape(source_ref)}\b", raw, re.I)) < 2:
                    self.add("BLOCK", "PRD-UNRESOLVED-SOURCE", path, "frontmatter source_ref is not resolved in the source register/body", source_ref)
            if "open_p0_unknown_ids" not in frontmatter:
                self.add("BLOCK", "PRD-NO-P0-DISPOSITION", path, "L3/L4 handoff must declare open_p0_unknown_ids, using [] when all are closed")

            ac_refs = {item.upper() for item in re.findall(r"\bAC-[A-Z0-9-]+\b", raw, re.I)}
            machine_ac_defs = {
                item.upper()
                for item in re.findall(r"(?m)^\s*(?:-\s+)?id:\s*['\"]?(AC-[A-Z0-9-]+)\b", raw, re.I)
            }
            for ac_id in sorted(ac_refs - machine_ac_defs):
                self.add("BLOCK", "PRD-AC-NO-MACHINE-DEFINITION", path, "referenced AC has no exact machine-readable definition", ac_id)
            in_fence = False
            for line_no, line in enumerate(raw.splitlines(), 1):
                stripped = line.lstrip()
                if stripped.startswith("```") or stripped.startswith("~~~"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                loose_ids = re.finditer(
                    r"\b(?:REQ|ROLE|FLOW|VIEW|REG|ACT|FLD|STM|STATE|RULE|API|EVT|INT|AC|TEST|EVD|CHG|REV|REL|METRIC)-[A-Z0-9-]+(?:\*|\.\.|…)[A-Z0-9-]*",
                    line,
                    re.I,
                )
                for loose in loose_ids:
                    self.add(
                        "BLOCK", "PRD-NONEXACT-ID", path,
                        "基线中的稳定 ID 必须逐项精确书写；正文、表格和机器附录均不得使用通配符或范围缩写",
                        f"line {line_no}: {loose.group(0)}",
                    )
            module_ids = {item.upper() for item in re.findall(r"\bMOD-[A-Z0-9-]+\b", raw, re.I)}
            if len(module_ids) > 1:
                if not has_any(lowered, ("跨模块逐边契约", "cross-module edge contract")):
                    self.add("BLOCK", "PRD-NO-CROSS-MODULE-EDGE-CONTRACT", path, "multi-module L3/L4 handoff must specify every cross-module edge")
                if not has_any(lowered, ("后继可达性", "successor reachability")):
                    self.add("BLOCK", "PRD-NO-SUCCESSOR-REACHABILITY", path, "created/converted objects need an authorized reachable next action")
            declared_views = frontmatter.get("page_contract_view_ids", [])
            if not isinstance(declared_views, list) or not declared_views:
                self.add("BLOCK", "PRD-NO-PAGE-CONTRACT-SCOPE", path, "L3 direct-implementation PRD must declare page_contract_view_ids in frontmatter")
                declared_views = []
            managed_views = frontmatter.get("managed_relation_view_ids", [])
            if not isinstance(managed_views, list):
                self.add("BLOCK", "PRD-MANAGED-RELATION-SCOPE", path, "managed_relation_view_ids must be a list when present")
                managed_views = []
            contracts = self._page_contracts(raw)
            blocks = {view: block for view, (_attrs, block) in contracts.items()}
            core_surfaces = {
                "purpose/entry": ("页面目标", "purpose", "入口"),
                "region layout": ("区域布局", "layout"),
                "actions/permissions": ("动作", "权限", "action"),
                "states/exceptions": ("状态", "异常", "exception"),
                "prototype binding": ("原型绑定", "prototype binding"),
            }
            surface_contracts = {
                "metrics": {"metric caliber": ("指标口径", "metric")},
                "list": {
                    "filters": ("筛选", "filter"),
                    "columns/tree/canvas": ("列表列", "列", "树", "画布", "column"),
                    "pagination/batch": ("分页", "pagination"),
                },
                "form": {"fields/controls": ("字段与控件", "控件", "field")},
                "drawer_form": {"fields/controls": ("字段与控件", "控件", "field")},
                "import": {"import": ("导入", "预检", "import")},
                "export": {"export": ("导出", "export")},
                "composer": {"composer": ("拖拽", "层级", "资源池", "排序", "composer")},
                "workflow": {"workflow": ("待办", "退回", "撤回", "审批", "workflow")},
                "preview": {"preview": ("预览", "preview")},
            }
            allowed_surfaces = set(surface_contracts) | {"detail", "resource_pool", "hierarchy", "assessment_insert"}
            for view in [str(item).upper() for item in declared_views]:
                attrs, block = contracts.get(view, ({}, ""))
                if not block:
                    self.add("BLOCK", "PRD-MISSING-PAGE-CONTRACT", path, "declared view has no PAGE-CONTRACT block", view)
                    continue
                lowered_block = block.lower()
                primary = attrs.get("primary", attrs.get("profile", "")).lower()
                layout = attrs.get("layout", "single").lower()
                surfaces = {
                    item.strip().lower() for item in attrs.get("surfaces", "").split(",") if item.strip()
                }
                if not attrs:  # v5.2 compatibility: infer only explicitly applicable legacy surfaces.
                    legacy = block.lower()
                    metric_na = bool(re.search(r"(?:指标口径|metrics?)\s*(?:[:：—-]\s*)?(?:不适用|not applicable)", legacy))
                    field_na = bool(re.search(r"(?:字段|字段与控件)\s*(?:[:：—-]\s*)?(?:不适用|不存在可编辑业务字段|not applicable)", legacy))
                    import_na = bool(re.search(r"(?:导入|import)\s*(?:[:：—-]\s*)?(?:不适用|not applicable)", legacy))
                    export_na = bool(re.search(r"(?:导出|export)\s*(?:[:：—-]\s*)?(?:不适用|not applicable)", legacy))
                    if not metric_na and ("指标口径" in legacy or re.search(r"\bMETRIC-[A-Z0-9-]+\b", block, re.I)):
                        surfaces.add("metrics")
                    if any(term in legacy for term in ("筛选", "列表", "树", "画布", "filter", "column")):
                        surfaces.add("list")
                    if not field_na and any(term in legacy for term in ("字段与控件", "表单", "field", "form")):
                        surfaces.add("form")
                    if not import_na and any(term in legacy for term in ("导入", "import")):
                        surfaces.add("import")
                    if not export_na and any(term in legacy for term in ("导出", "export")):
                        surfaces.add("export")
                    if any(term in legacy for term in ("拖拽", "资源池", "composer")):
                        surfaces.add("composer")
                    if any(term in legacy for term in ("审批", "待办", "workflow")):
                        surfaces.add("workflow")
                    if any(term in legacy for term in ("预览", "preview")):
                        surfaces.add("preview")
                if primary and primary in surface_contracts:
                    surfaces.add(primary)
                if primary and primary not in allowed_surfaces:
                    self.add("BLOCK", "PRD-PAGE-BAD-PRIMARY", path, "primary 不是支持的页面表面", view)
                unknown_surfaces = sorted(surfaces - allowed_surfaces)
                if unknown_surfaces:
                    self.add("BLOCK", "PRD-PAGE-BAD-SURFACE", path, "存在不支持的 surfaces: " + ", ".join(unknown_surfaces), view)
                if layout not in {"single", "composite", "builder", "portal"}:
                    self.add("BLOCK", "PRD-PAGE-BAD-LAYOUT", path, "layout 只能是 single/composite/builder/portal", view)
                if layout == "composite" and len(surfaces) < 2:
                    self.add("BLOCK", "PRD-PAGE-COMPOSITE-TOO-THIN", path, "composite 页面至少声明两个 surfaces", view)
                builder_required = {"composer", "resource_pool", "hierarchy"}
                if layout == "builder" and not builder_required.issubset(surfaces):
                    missing = sorted(builder_required - surfaces)
                    self.add("BLOCK", "PRD-PAGE-BUILDER-INCOMPLETE", path, "builder 页面缺少 " + ", ".join(missing), view)
                required_surfaces = dict(core_surfaces)
                for surface in surfaces:
                    required_surfaces.update(surface_contracts.get(surface, {}))
                for label, terms in required_surfaces.items():
                    if not any(term.lower() in lowered_block for term in terms):
                        self.add("BLOCK", "PRD-INCOMPLETE-PAGE-CONTRACT", path, f"page contract misses {label}", view)
                if "metrics" in surfaces and not (
                    re.search(r"\bMETRIC-[A-Z0-9-]+\b", block, re.I)
                    and has_any(lowered_block, ("公式", "分子", "分母", "去重", "时间窗口"))
                ):
                    self.add("BLOCK", "PRD-METRIC-NO-CALIBER", path, "已激活 metrics 的页面必须提供 METRIC ID 和明确口径", view)
                def concrete_ids(prefix: str) -> set[str]:
                    values: set[str] = set()
                    for found in re.finditer(rf"\b{prefix}-[A-Z0-9-]+", block, re.I):
                        value = found.group(0).upper()
                        if value.endswith("-") or (found.end() < len(block) and block[found.end()] == "*"):
                            continue
                        values.add(value)
                    return values

                field_not_applicable = "form" not in surfaces and "drawer_form" not in surfaces or bool(re.search(
                    r"(?:字段|字段与控件)\s*(?:[:：—-]\s*)?(?:不适用|不存在可编辑业务字段|not applicable)",
                    lowered_block,
                ))
                if not field_not_applicable and len(concrete_ids("FLD")) < 2:
                    self.add("BLOCK", "PRD-PAGE-NO-FIELDS", path, "four-lens handoff needs concrete stable FLD contracts for the view", view)
                read_only = attrs.get("read_only", "no").lower() in {"yes", "true", "1"}
                minimum_actions = 1 if read_only else 2
                if len(concrete_ids("ACT")) < minimum_actions:
                    self.add("BLOCK", "PRD-PAGE-NO-ACTIONS", path, "four-lens handoff needs at least two concrete ACT contracts or an explicit read-only decision", view)
                if not concrete_ids("AC"):
                    self.add("BLOCK", "PRD-PAGE-NO-AC", path, "QA lens needs a concrete AC linked inside the page contract", view)
                api_trace = any(
                    view.lower() in line.lower() and ("/api/" in line.lower() or re.search(r"\bAPI-[A-Z0-9-]+\b", line, re.I))
                    for line in raw.splitlines()
                )
                if not api_trace:
                    self.add("BLOCK", "PRD-PAGE-NO-API-TRACE", path, "backend/Coding Agent lens needs an explicit view-to-API or no-write mapping", view)
            for extra in sorted(set(blocks) - {str(item).upper() for item in declared_views}):
                self.add("GAP", "PRD-UNDECLARED-PAGE-CONTRACT", path, "PAGE-CONTRACT block is not declared in page_contract_view_ids", extra)
            declared_set = {str(item).upper() for item in declared_views}
            managed_set = {str(item).upper() for item in managed_views}
            for view in sorted(managed_set - declared_set):
                self.add("BLOCK", "PRD-MANAGED-RELATION-UNDECLARED-VIEW", path, "managed relation view must also be a declared page contract", view)
            if managed_set and not has_any(lowered, ("角色—工作面闭环矩阵", "角色-工作面闭环矩阵", "role-work-surface")):
                self.add("BLOCK", "PRD-NO-ROLE-WORK-SURFACE-MATRIX", path, "managed relations require a role-to-work-surface closure matrix")
            relation_terms = {
                "stable REL ID": ("REL-",),
                "inventory": ("台账", "inventory"),
                "source/inheritance": ("来源", "继承", "source", "inherit"),
                "batch behavior": ("批量", "batch"),
                "preflight": ("预检", "preflight"),
                "partial failure": ("部分失败", "partial failure"),
                "idempotency": ("幂等", "idempot"),
                "API": ("/api/", "API-"),
            }
            for view in sorted(managed_set & declared_set):
                block = blocks.get(view, "")
                lowered_block = block.lower()
                for label, terms in relation_terms.items():
                    if not any(term.lower() in lowered_block for term in terms):
                        self.add("BLOCK", "PRD-INCOMPLETE-MANAGED-RELATION", path, f"managed relation contract misses {label}", view)
            self.metrics["prd_page_contracts"] = len(blocks)
        self.metrics.update({"prd_headings": len(re.findall(r"(?m)^#{1,4}\s+\S", raw)), "prd_requirement_ids": len(requirement_ids)})

    def check_stage0(self, path: Path) -> None:
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "STAGE0-READ", path, f"Stage 0 台账无法读取：{exc}")
            return
        document, error = self._yaml_document(path, raw)
        if error or document is None:
            self.add("BLOCK", "STAGE0-PARSE", path, error or "Stage 0 台账无效")
            return
        items = document.get("items") or []
        if not isinstance(items, list) or not items:
            self.add("BLOCK", "STAGE0-NO-INVENTORY", path, "Stage 0 台账必须包含非空 items")
            return
        allowed = {"confirmed", "inferred", "unknown", "defect_candidate"}
        baseline_refs_raw = document.get("baseline_requirement_refs") or []
        baseline_refs = {str(item).upper() for item in baseline_refs_raw} if isinstance(baseline_refs_raw, list) else set()
        if baseline_refs_raw and (
            not isinstance(baseline_refs_raw, list)
            or any(not re.fullmatch(r"REQ-[A-Z0-9-]+", item, re.I) for item in baseline_refs)
        ):
            self.add(
                "BLOCK", "STAGE0-BAD-BASELINE-REFS", path,
                "baseline_requirement_refs 必须是精确 REQ-* 数组", "baseline_requirement_refs",
            )
        batches_raw = document.get("review_batches") or []
        batches = {
            str(item.get("id")): item
            for item in batches_raw
            if isinstance(item, dict) and item.get("id")
        } if isinstance(batches_raw, list) else {}
        if batches_raw and not isinstance(batches_raw, list):
            self.add("BLOCK", "STAGE0-BAD-REVIEW-BATCHES", path, "review_batches 必须是数组", "review_batches")
        for batch_id, batch in batches.items():
            if not re.fullmatch(r"RBATCH-[A-Z0-9-]+", batch_id, re.I) or not batch.get("owner"):
                self.add(
                    "BLOCK", "STAGE0-INCOMPLETE-REVIEW-BATCH", path,
                    "确认批次必须使用 RBATCH-* 并声明 owner", batch_id,
                )
        open_core_unknowns = 0
        inferred_pending = 0
        for index, item in enumerate(items):
            ref = str(item.get("id", f"items[{index}]")) if isinstance(item, dict) else f"items[{index}]"
            if not isinstance(item, dict):
                self.add("BLOCK", "STAGE0-BAD-ITEM", path, "台账记录必须是对象", ref)
                continue
            missing = [key for key in ("id", "type", "source_ref", "source_location", "classification") if not item.get(key)]
            if missing:
                self.add("BLOCK", "STAGE0-INCOMPLETE-ITEM", path, "台账记录缺少 " + ", ".join(missing), ref)
                continue
            classification = str(item.get("classification")).lower()
            if classification not in allowed:
                self.add("BLOCK", "STAGE0-BAD-CLASSIFICATION", path, "classification 不在允许集合", ref)
            if classification == "unknown" and item.get("core_behavior") is True:
                open_core_unknowns += 1
                unknown = item.get("unknown") or {}
                if not (
                    isinstance(unknown, dict)
                    and re.fullmatch(r"UNK-[A-Z0-9-]+", str(unknown.get("id", "")), re.I)
                    and str(unknown.get("priority", "")).upper() == "P0"
                    and unknown.get("blocks_stage")
                    and unknown.get("owner")
                ):
                    self.add(
                        "BLOCK", "STAGE0-CORE-UNKNOWN-NOT-OWNED", path,
                        "核心行为 UNKNOWN 必须登记 UNK-*、P0、blocks_stage 和 owner", ref,
                        affected_consumers=("product", "architect", "qa"),
                    )
            if baseline_refs and not re.fullmatch(r"INV-[A-Z0-9-]+", str(item.get("id", "")), re.I):
                self.add(
                    "BLOCK", "STAGE0-REVERSE-ID-COLLISION", path,
                    "已有需求基线时，反推观察项必须使用 INV-*，不得另造 REQ-* 与正向基线争夺语义",
                    ref,
                )
            if baseline_refs and classification in {"confirmed", "inferred"}:
                mapping_status = str(item.get("mapping_status", "")).lower()
                target_refs = {str(value).upper() for value in item.get("target_refs", []) or []}
                if mapping_status not in {"mapped", "unmapped", "not_applicable"}:
                    self.add(
                        "BLOCK", "STAGE0-MISSING-BASELINE-MAPPING", path,
                        "反推项必须声明 mapping_status=mapped/unmapped/not_applicable", ref,
                    )
                elif mapping_status == "mapped":
                    if not target_refs:
                        self.add("BLOCK", "STAGE0-MAPPED-WITHOUT-TARGET", path, "mapped 反推项缺少 target_refs", ref)
                    for target in sorted(target_refs - baseline_refs):
                        self.add("BLOCK", "STAGE0-ORPHAN-TARGET-REF", path, "target_refs 不在声明的正向需求基线中", f"{ref}->{target}")
                elif mapping_status == "unmapped" and item.get("core_behavior") is True:
                    unknown = item.get("unknown") or {}
                    if not (
                        isinstance(unknown, dict)
                        and re.fullmatch(r"UNK-[A-Z0-9-]+", str(unknown.get("id", "")), re.I)
                        and unknown.get("owner")
                    ):
                        self.add(
                            "BLOCK", "STAGE0-UNMAPPED-CORE-NOT-OWNED", path,
                            "未映射的核心行为必须登记有 owner 的 UNK-*，不得直接升级为新需求", ref,
                        )
            if classification == "inferred":
                inferred_pending += 1
                batch_ref = str(item.get("review_batch_ref", ""))
                if not batch_ref:
                    self.add(
                        "GAP", "STAGE0-INFERRED-NO-REVIEW-BATCH", path,
                        "推断项未进入责任人确认批次，无法批量确认或否决", ref,
                    )
                elif batch_ref not in batches:
                    self.add(
                        "BLOCK", "STAGE0-ORPHAN-REVIEW-BATCH", path,
                        "review_batch_ref 未解析到 review_batches", f"{ref}->{batch_ref}",
                    )
            if classification == "defect_candidate" and item.get("target_requirement_ref"):
                self.add(
                    "BLOCK", "STAGE0-DEFECT-PROMOTED", path,
                    "缺陷候选未经 DEC/CHG 不得直接升级为目标需求", ref,
                    related_refs=(str(item.get("target_requirement_ref")),),
                )
        candidates = document.get("canonical_candidates") or []
        conflict_ref = str(document.get("conflict_decision_ref", ""))
        if len(candidates) > 1 and not conflict_ref.startswith("DEC-CONFLICT-"):
            self.add(
                "BLOCK", "STAGE0-MULTIPLE-BASELINES", path,
                "多版本 PRD/原型必须通过 DEC-CONFLICT-* 选择基线或划分范围",
                ", ".join(map(str, candidates)),
            )
        if str(document.get("inventory_status", "")).lower() == "inventory_complete" and any(
            finding.artifact == str(path) and finding.severity == "BLOCK" for finding in self.findings
        ):
            self.add("BLOCK", "STAGE0-FALSE-COMPLETE", path, "存在未闭合台账问题却声明 inventory_complete")
        if str(document.get("target_status", "")).lower() == "baseline_ready" and inferred_pending:
            self.add(
                "BLOCK", "STAGE0-INFERRED-NOT-CONFIRMED", path,
                "仍有 inferred 项时不得声明 baseline_ready；应由对应 review batch 批量确认、否决或转为未知项",
                f"inferred={inferred_pending}",
            )
        self.metrics.update({
            "stage0_items": len(items),
            "stage0_core_unknowns": open_core_unknowns,
            "stage0_inferred_pending": inferred_pending,
            "stage0_review_batches": len(batches),
            "stage0_baseline_refs": len(baseline_refs),
        })

    def check_agent_handoff(self, path: Path) -> None:
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "HANDOFF-READ", path, f"Agent 交接清单无法读取：{exc}")
            return
        document, error = self._yaml_document(path, raw)
        if error or document is None:
            self.add("BLOCK", "HANDOFF-PARSE", path, error or "Agent 交接清单无效")
            return
        if HANDOFF_SCHEMA.is_file():
            schema = json.loads(HANDOFF_SCHEMA.read_text(encoding="utf-8"))
            for schema_error in sorted(
                Draft202012Validator(schema).iter_errors(document),
                key=lambda item: tuple(str(part) for part in item.path),
            ):
                location = ".".join(str(part) for part in schema_error.path) or "<root>"
                self.add("BLOCK", "HANDOFF-SCHEMA", path, schema_error.message, location)
        baseline = document.get("baseline") or {}
        baseline_hash = str(baseline.get("hash", "")) if isinstance(baseline, dict) else ""
        ready = str(document.get("status", "draft")) == "ready_for_implementation"
        requirement_ref = str(baseline.get("requirement_ref", "")) if isinstance(baseline, dict) else ""
        requirement_path = path.parent / requirement_ref
        if requirement_ref and requirement_path.is_file():
            requirement_raw = self.read(requirement_path)
            if baseline_hash != self._sha256(requirement_raw):
                self.add("BLOCK", "HANDOFF-REQUIREMENT-HASH-DRIFT", path, "需求基线文件与 baseline.hash 不一致", requirement_ref)
        elif ready:
            self.add("BLOCK", "HANDOFF-REQUIREMENT-NOT-LOCAL", path, "开发交接的需求基线文件不可访问", requirement_ref or "baseline.requirement_ref")
        elif requirement_ref:
            self.add("GAP", "HANDOFF-REQUIREMENT-NOT-LOCAL", path, "草稿清单的需求基线文件不在当前目录", requirement_ref)
        engineering_ref = str(document.get("engineering_baseline_ref", ""))
        if ready and not engineering_ref:
            self.add(
                "BLOCK", "HANDOFF-NO-ENGINEERING-BASELINE", path,
                "开发交接缺少 engineering_baseline_ref",
                affected_consumers=("architect", "frontend", "backend", "qa", "coding_agent"),
            )
        elif engineering_ref and not (path.parent / engineering_ref).is_file():
            self.add("GAP", "HANDOFF-ENGINEERING-BASELINE-NOT-LOCAL", path, "工程基线引用不在当前交接目录，接收方需确认可访问", engineering_ref)
        packet_ids: set[str] = set()
        for packet in document.get("packets", []) or []:
            if not isinstance(packet, dict):
                continue
            packet_id = str(packet.get("id", "<unknown>"))
            packet_ids.add(packet_id)
            if packet.get("baseline_hash") != baseline_hash:
                self.add("BLOCK", "HANDOFF-PACKET-BASELINE-DRIFT", path, "工作包 baseline_hash 与清单不一致", packet_id)
            packet_path = path.parent / str(packet.get("path", ""))
            if not packet_path.is_file():
                self.add("BLOCK", "HANDOFF-PACKET-NOT-FILE", path, "工作包文件不存在", str(packet_path))
                continue
            packet_raw = self.read(packet_path)
            expected_hash = packet.get("content_sha256")
            if expected_hash and expected_hash != self._sha256(packet_raw):
                self.add("BLOCK", "HANDOFF-PACKET-HASH-DRIFT", path, "工作包内容哈希已漂移", packet_id)
            if packet_id not in packet_raw:
                self.add("BLOCK", "HANDOFF-PACKET-ID-MISSING", path, "工作包正文未声明自身 ID", packet_id)
            if not any(str(ref) in packet_raw for ref in packet.get("scope_refs", []) or []):
                self.add("BLOCK", "HANDOFF-PACKET-SCOPE-MISSING", path, "工作包正文没有任何声明的 scope_refs", packet_id)
            if not any(str(ref) in packet_raw for ref in packet.get("acceptance_refs", []) or []):
                self.add("BLOCK", "HANDOFF-PACKET-AC-MISSING", path, "工作包正文没有任何 acceptance_refs", packet_id)
            kind = str(packet.get("kind", "")).lower()
            if kind == "mod" and "qa_projection" not in packet_raw.lower() and "qa 投影" not in packet_raw.lower():
                self.add("BLOCK", "HANDOFF-MOD-NO-QA-PROJECTION", path, "MOD 工作包缺少 qa_projection", packet_id)
            if kind == "edge":
                lowered_packet = packet_raw.lower()
                for label, terms in {
                    "producer/consumer": ("producer", "consumer", "生产者", "消费者"),
                    "payload/version": ("payload", "字段映射", "版本"),
                    "idempotency/failure": ("幂等", "idempot", "失败", "补偿"),
                    "permission/E2E": ("权限", "permission", "e2e", "ac-"),
                }.items():
                    if not any(term in lowered_packet for term in terms):
                        self.add("BLOCK", "HANDOFF-EDGE-INCOMPLETE", path, f"EDGE 工作包缺少 {label}", packet_id)
        for envelope in document.get("handoffs", []) or []:
            if not isinstance(envelope, dict):
                continue
            affected = set(map(str, envelope.get("affected_packets", []) or []))
            missing = sorted(affected - packet_ids)
            if missing:
                self.add("BLOCK", "HANDOFF-ENVELOPE-ORPHAN-PACKET", path, "HANDOFF 引用不存在的工作包", ", ".join(missing))
            if envelope.get("intent") in {"proposal", "request"} and envelope.get("ack_status") == "applied" and not envelope.get("decision_refs"):
                self.add("BLOCK", "HANDOFF-UNAPPROVED-PROPOSAL", path, "proposal/request 未绑定 DEC/CHG 不得标记 applied", str(envelope.get("handoff_id", "")))
        self.metrics.update({"handoff_packets": len(packet_ids), "handoff_envelopes": len(document.get("handoffs", []) or [])})

    def check_manifest_prd_binding(self, prd_path: Path, manifest_path: Path) -> None:
        """Ensure a combined handoff does not pair a manifest with another PRD."""
        document, error = self._yaml_document(manifest_path, self.read(manifest_path))
        if error or document is None:
            return
        baseline = document.get("baseline") or {}
        if not isinstance(baseline, dict):
            return
        expected_hash = self._sha256(self.read(prd_path))
        if str(baseline.get("hash", "")) != expected_hash:
            self.add(
                "BLOCK", "HANDOFF-PRD-HASH-DRIFT", manifest_path,
                "交接清单与本次提供的 PRD 不是同一内容基线",
                str(baseline.get("requirement_ref", "")),
                affected_consumers=("architect", "frontend", "backend", "qa", "coding_agent"),
            )

    def check_prototype(self, path: Path, level: str) -> None:
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "PROTO-READ", path, f"prototype cannot be read: {exc}")
            return
        # Restrict attribute discovery to actual HTML-like opening tags. Raw
        # regex over the whole document also matches JavaScript selectors such
        # as `[data-testid="page-X"]` and falsely reports duplicate pages.
        tag_source = self._tag_source(raw)
        testids = re.findall(r"\bdata-testid\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)
        actions = sorted(set(re.findall(r"\bdata-action\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        states = sorted(set(re.findall(r"\bdata-state\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        fields = sorted(set(re.findall(r"\bdata-(?:field|bind)\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        metrics = sorted(set(re.findall(r"\bdata-metric\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        acceptance_refs = sorted(set(re.findall(r"\bdata-ac\s*=\s*['\"](AC-[A-Z0-9-]+)['\"]", tag_source, re.I)))
        page_testids = [item for item in testids if item.lower().startswith("page-")]
        region_testids = [item for item in testids if item.lower().startswith("region-")]
        self.prototype_acceptance_refs.update(item.upper() for item in acceptance_refs)
        if not page_testids:
            self.add("BLOCK" if actions or level in {"L2", "L3", "L4"} else "GAP", "PROTO-NO-PAGE-ANCHOR", path, "no page-* data-testid root was found")
        for duplicate in sorted(item for item, count in Counter(testids).items() if count > 1 and item.lower().startswith("page-")):
            self.add("BLOCK", "PROTO-DUPLICATE-PAGE", path, "page data-testid must be unique", duplicate)
        for duplicate in sorted(item for item, count in Counter(testids).items() if count > 1 and item.lower().startswith("region-")):
            self.add("BLOCK", "PROTO-DUPLICATE-REGION", path, "region data-testid must be unique", duplicate)
        if level in {"L2", "L3", "L4"}:
            for action in actions:
                if not re.fullmatch(r"ACT-[A-Z0-9-]+", action, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-ACTION", path, "data-action must bind a stable ACT-* ID", action)
            for metric in metrics:
                if not re.fullmatch(r"METRIC-[A-Z0-9-]+", metric, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-METRIC", path, "data-metric must bind a stable METRIC-* ID", metric)
        if level in {"L3", "L4"}:
            for region in region_testids:
                if not re.fullmatch(r"region-REG-[A-Z0-9-]+", region, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-REGION", path, "region data-testid must bind a stable REG-* ID", region)
            page_contracts = self._page_contracts(raw)
            complex_contract = any(
                attrs.get("layout", "").lower() in {"composite", "builder", "portal"}
                or len({item.strip().lower() for item in attrs.get("surfaces", "").split(",") if item.strip()}) > 1
                for attrs, _block in page_contracts.values()
            )
            complex_markup = len(page_testids) > 1 or bool(re.search(r"<table\b", raw, re.I) and re.search(r"<(?:form|input|select|textarea)\b", raw, re.I))
            if page_testids and (complex_contract or complex_markup) and not region_testids:
                self.add(
                    "BLOCK", "PROTO-NO-REGION-ANCHOR", path,
                    "L3/L4 复合页、组装器、门户或多视图原型至少需要一个稳定 REG-* 区域锚点",
                    affected_consumers=("product", "ux", "frontend", "qa", "coding_agent"),
                )
        if not actions:
            self.add("GAP", "PROTO-NO-ACTIONS", path, "no data-action controls were found; confirm this is intentionally static")

        script_blocks = []
        module_script = False
        for attrs, body in re.findall(r"<script\b([^>]*)>(.*?)</script>", raw, re.I | re.S):
            type_match = re.search(r"\btype\s*=\s*['\"]([^'\"]+)['\"]", attrs, re.I)
            script_type = type_match.group(1).lower() if type_match else "text/javascript"
            if script_type in {"text/javascript", "application/javascript", "module"}:
                script_blocks.append(body)
                module_script = module_script or script_type == "module"
        scripts = "\n".join(script_blocks)
        split_anchor_pattern = re.compile(
            r"(?:data-\s*['\"]\s*\+\s*['\"](?:action|testid|state|field|metric)|"
            r"['\"]data-['\"]\s*\+\s*['\"](?:action|testid|state|field|metric)['\"])",
            re.I,
        )
        split_anchors = split_anchor_pattern.findall(scripts)
        script_action_candidates = sorted(set(re.findall(r"\bACT-[A-Z0-9-]+\b", scripts, re.I)) - set(actions))
        if split_anchors:
            severity = "BLOCK" if level in {"L2", "L3", "L4"} else "GAP"
            self.add(
                severity, "PROTO-DYNAMIC-ANCHOR-CONSTRUCTION", path,
                f"发现 {len(split_anchors)} 处 data-* 锚点名称由字符串拼接生成；静态门禁无法证明其完整性",
                re.sub(r"\s+", " ", split_anchors[0])[:120],
                affected_consumers=("frontend", "qa", "coding_agent"),
                related_refs=tuple(item.upper() for item in script_action_candidates[:50]),
            )
        if level in {"L2", "L3", "L4"} and re.search(
            r"(?:setAttribute\s*\(\s*['\"]data-action|dataset\.action\s*=)", scripts, re.I
        ):
            self.add(
                "BLOCK", "PROTO-RUNTIME-ACTION-RETROFIT", path,
                "data-action 必须在视图模板源码中可静态枚举，不能在运行时补挂",
            )
        if level in {"L3", "L4"}:
            metric_like_tags = [
                tag for tag in re.findall(r"<[A-Za-z][^>]*>", raw, re.S)
                if re.search(r"\bclass\s*=\s*['\"][^'\"]*\b(?:metric|metric-card|stat-card|kpi)\b", tag, re.I)
                and not re.search(r"\bdata-metric\s*=", tag, re.I)
            ]
            if metric_like_tags:
                self.add("BLOCK", "PROTO-METRIC-NO-ID", path, f"{len(metric_like_tags)} displayed metric elements have no stable data-metric", re.sub(r"\s+", " ", metric_like_tags[0])[:120])
            inline_handlers = re.findall(r"\bon(?:click|change|input|submit|dragstart|drop)\s*=", raw, re.I)
            if inline_handlers:
                self.add("BLOCK", "PROTO-INLINE-HANDLER", path, f"L3 prototype contains {len(inline_handlers)} inline event handlers; use one explicit action registry")
            missing_action_controls = []
            missing_ac_controls = []
            for tag in re.findall(r"<(?:button|a)\b[^>]*>", raw, re.I | re.S):
                if re.search(r"\bdisabled\b", tag, re.I):
                    continue
                if not re.search(r"\bdata-action\s*=", tag, re.I):
                    missing_action_controls.append(re.sub(r"\s+", " ", tag)[:120])
                elif not re.search(r"\bdata-ac\s*=\s*['\"]AC-[A-Z0-9-]+['\"]", tag, re.I):
                    missing_ac_controls.append(re.sub(r"\s+", " ", tag)[:120])
            if missing_action_controls:
                self.add("BLOCK", "PROTO-CONTROL-NO-ACTION", path, f"{len(missing_action_controls)} button/link controls have no stable data-action", missing_action_controls[0])
            if missing_ac_controls:
                self.add("BLOCK", "PROTO-ACTION-NO-AC", path, f"{len(missing_ac_controls)} action controls have no data-ac trace", missing_ac_controls[0])
            function_names = re.findall(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(", scripts)
            duplicates = sorted(name for name, count in Counter(function_names).items() if count > 1)
            for name in duplicates[:10]:
                self.add("BLOCK", "PROTO-DUPLICATE-FUNCTION", path, "duplicate function declaration indicates stacked prototype overrides", name)
        inline_action_tags = {
            action
            for tag in re.findall(r"<[^>]+\bdata-action\s*=\s*['\"][^'\"]+['\"][^>]*>", raw, re.I | re.S)
            for action in re.findall(r"\bdata-action\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
            if re.search(r"\bonclick\s*=", tag, re.I)
        }
        has_listener = bool(re.search(r"addEventListener\s*\(\s*['\"](?:click|change|submit|input)['\"]", scripts, re.I))
        reads_action = bool(re.search(r"dataset\.action|getAttribute\s*\(\s*['\"]data-action['\"]|closest\s*\(\s*['\"]\[data-action\]", scripts, re.I))
        for action in actions:
            dispatch_evidence = bool(re.search(
                rf"(?:case\s+['\"]{re.escape(action)}['\"]|(?:action|actionId)\s*===?\s*['\"]{re.escape(action)}['\"]|['\"]{re.escape(action)}['\"]\s*:|\.set\s*\(\s*['\"]{re.escape(action)}['\"]|\[\s*['\"]{re.escape(action)}['\"]\s*\]\s*=)",
                scripts,
                re.I,
            ))
            if action not in inline_action_tags and not (has_listener and reads_action and dispatch_evidence):
                self.add("BLOCK", "PROTO-UNHANDLED-ACTION", path, "no static event-handler evidence for data-action", action)

        durable_result = bool(re.search(
            r"\.(?:textContent|innerHTML|value)\s*=|insertAdjacentHTML|appendChild|replaceChildren|classList\.(?:add|remove|toggle)|setAttribute\s*\(|\b(?:render|navigate|showModal)\w*\s*\(|location\.(?:href|assign)|history\.pushState",
            scripts,
            re.I,
        ))
        transient_result = bool(re.search(r"\b(?:alert|toast|notify)\s*\(", scripts, re.I))
        if actions and not durable_result and not transient_result:
            self.add("BLOCK", "PROTO-NO-VISIBLE-RESULT", path, "actions have no static visible-result mechanism")
        elif actions and transient_result and not durable_result:
            self.add("GAP", "PROTO-TRANSIENT-ONLY", path, "only transient feedback is visible; core state changes need a durable result")
        state_result = bool(states) and bool(re.search(
            r"setAttribute\s*\(\s*['\"]data-state|dataset\.state\s*=|\b(?:globalState|state|entities)\b\s*[.\[]|\btransition\s*\(",
            scripts,
            re.I,
        ))
        if actions and level in {"L2", "L3", "L4"} and not state_result:
            self.add("GAP", "PROTO-NO-DOMAIN-STATE", path, "static scan found no explicit data-state/domain-state mutation; bind core actions to a durable domain result or prove them in browser evidence")

        for css_finding in scan_prototype_css(raw):
            self.add("BLOCK", "PROTO-CSS-" + css_finding["kind"].upper(), path, css_finding["detail"], css_finding["selector"])

        if scripts.strip():
            node = shutil.which("node")
            if node:
                command = [node, "--check"]
                if module_script:
                    command.insert(1, "--input-type=module")
                # Node consumes JavaScript as UTF-8.  Do not inherit the Windows
                # runner's narrow locale (for example cp1252), otherwise a valid
                # prototype containing Chinese text can fail before Node starts.
                checked = subprocess.run(
                    command,
                    input=scripts,
                    text=True,
                    encoding="utf-8",
                    capture_output=True,
                    timeout=15,
                )
                if checked.returncode:
                    detail = next((line.strip() for line in checked.stderr.splitlines() if "SyntaxError" in line), "JavaScript syntax check failed")
                    self.add("BLOCK", "PROTO-JS-SYNTAX", path, detail)
            elif not _balanced_javascript(scripts):
                self.add("BLOCK", "PROTO-JS-DELIMITERS", path, "JavaScript has unbalanced delimiters")
            else:
                self.add("GAP", "PROTO-JS-CHECK-LIMITED", path, "Node.js is unavailable; only delimiter syntax was checked")
        external_scripts = re.findall(r"<script\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)['\"]", raw, re.I)
        if external_scripts:
            self.add("GAP", "PROTO-EXTERNAL-JS", path, "external scripts are outside this single-file static scan", ", ".join(external_scripts[:3]))
        self.metrics.update({
            "prototype_pages": len(page_testids),
            "prototype_regions": len(region_testids),
            "prototype_actions": len(actions),
            "prototype_dynamic_action_candidates": len(script_action_candidates) if split_anchors else 0,
            "prototype_action_inventory_total": len(set(actions) | (set(script_action_candidates) if split_anchors else set())),
            "prototype_states": len(states),
            "prototype_fields": len(fields),
            "prototype_metrics": len(metrics),
            "prototype_acceptance_refs": len(self.prototype_acceptance_refs),
        })

    def check_acceptance_run(self, path: Path) -> tuple[set[str], bool, bool]:
        """Validate one ARUN and return evidenced ACs, browser environment, conclusion."""
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "ACCEPTANCE-READ", path, f"验收记录无法读取：{exc}")
            return set(), False, False
        document, error = self._yaml_document(path, raw)
        if error or document is None:
            self.add("BLOCK", "ACCEPTANCE-PARSE", path, error or "验收记录无效")
            return set(), False, False
        schema = json.loads(ACCEPTANCE_SCHEMA.read_text(encoding="utf-8"))
        schema_errors = sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
            key=lambda item: tuple(str(part) for part in item.path),
        )
        for schema_error in schema_errors:
            location = ".".join(str(part) for part in schema_error.path) or "<root>"
            self.add("BLOCK", "ACCEPTANCE-SCHEMA", path, schema_error.message, location)

        evidenced: set[str] = set()
        mandatory_incomplete: list[str] = []
        for item in document.get("items", []) or []:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "<unknown>"))
            if item.get("mandatory") and item.get("result") != "pass":
                mandatory_incomplete.append(item_id)
            if item.get("result") != "pass":
                continue
            if not str(item.get("actual_result", "")).strip() or not item.get("evidence_refs"):
                self.add("BLOCK", "ACCEPTANCE-PASS-NO-EVIDENCE", path, "pass 项必须填写实际结果和证据引用", item_id)
                continue
            acceptance_ref = str(item.get("acceptance_ref", "")).upper()
            if acceptance_ref:
                evidenced.add(acceptance_ref)

        conclusion = str(document.get("conclusion", "pending"))
        sign_offs = document.get("sign_offs", []) or []
        if conclusion == "accepted" and mandatory_incomplete:
            self.add("BLOCK", "ACCEPTANCE-INCOMPLETE-CONCLUSION", path, "accepted 仍包含未通过的 mandatory 项", ", ".join(mandatory_incomplete))
        if conclusion == "accepted_with_conditions" and not document.get("conditions"):
            self.add("BLOCK", "ACCEPTANCE-CONDITION-MISSING", path, "accepted_with_conditions 缺少条件、责任人和完成标准")
        if conclusion in {"accepted", "accepted_with_conditions"} and not sign_offs:
            self.add("BLOCK", "ACCEPTANCE-SIGNOFF-MISSING", path, "接受结论缺少签署记录")

        environment = str(document.get("environment", "")).lower()
        browser_markers = ("browser", "浏览器", "chrome", "edge", "firefox", "safari", "webkit", "playwright")
        browser_environment = any(marker in environment for marker in browser_markers)
        conclusive = conclusion in {"accepted", "accepted_with_conditions"} and not mandatory_incomplete and bool(sign_offs)
        self.metrics.update({
            "acceptance_run_items": self.metrics.get("acceptance_run_items", 0) + len(document.get("items", []) or []),
            "acceptance_run_evidenced_acs": self.metrics.get("acceptance_run_evidenced_acs", 0) + len(evidenced),
        })
        return evidenced, browser_environment, conclusive

    def check_handoff(self, prd_path: Path, prototype_paths: list[Path], level: str) -> None:
        """Cross-check the one PRD baseline against one or more prototype projections."""
        try:
            prd = self.read(prd_path)
            prototype_raw = [(path, self.read(path)) for path in prototype_paths]
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "HANDOFF-READ", prd_path, f"handoff artifact cannot be read: {exc}")
            return

        frontmatter = self._frontmatter(prd)
        declared_views = {str(item).upper() for item in frontmatter.get("page_contract_view_ids", []) if item}
        prd_actions = {item.upper() for item in re.findall(r"\bACT-[A-Z0-9-]+\b", prd, re.I)}
        prd_ac_refs = {item.upper() for item in re.findall(r"\bAC-[A-Z0-9-]+\b", prd, re.I)}
        prd_metric_refs = {item.upper() for item in re.findall(r"\bMETRIC-[A-Z0-9-]+\b", prd, re.I)}
        machine_ac_defs = {
            item.upper()
            for item in re.findall(r"(?m)^\s*(?:-\s+)?id:\s*['\"]?(AC-[A-Z0-9-]+)\b", prd, re.I)
        }
        prototype_views: set[str] = set()
        prototype_actions: set[str] = set()
        prototype_acs: set[str] = set()
        prototype_metrics: set[str] = set()
        for path, raw in prototype_raw:
            tags = self._tag_source(raw)
            prototype_views.update(item.upper() for item in re.findall(r"\bdata-view\s*=\s*['\"](VIEW-[A-Z0-9-]+)['\"]", tags, re.I))
            prototype_views.update(item.upper() for item in re.findall(r"\bdata-testid\s*=\s*['\"]page-(VIEW-[A-Z0-9-]+)['\"]", tags, re.I))
            prototype_actions.update(item.upper() for item in re.findall(r"\bdata-action\s*=\s*['\"](ACT-[A-Z0-9-]+)['\"]", tags, re.I))
            if re.search(
                r"(?:data-\s*['\"]\s*\+\s*['\"]action|['\"]data-['\"]\s*\+\s*['\"]action['\"])",
                raw,
                re.I,
            ):
                # Include literal candidates in the cross-artifact inventory, but
                # check_prototype still blocks because their rendered presence is unproven.
                prototype_actions.update(item.upper() for item in re.findall(r"\bACT-[A-Z0-9-]+\b", raw, re.I))
            prototype_acs.update(item.upper() for item in re.findall(r"\bdata-ac\s*=\s*['\"](AC-[A-Z0-9-]+)['\"]", tags, re.I))
            prototype_metrics.update(item.upper() for item in re.findall(r"\bdata-metric\s*=\s*['\"](METRIC-[A-Z0-9-]+)['\"]", tags, re.I))

        for action in sorted(prototype_actions - prd_actions):
            self.add("BLOCK", "HANDOFF-PROTOTYPE-ACTION-NOT-IN-PRD", prd_path, "prototype action is absent from the PRD baseline", action)
        for ac_id in sorted(prototype_acs - prd_ac_refs):
            self.add("BLOCK", "HANDOFF-PROTOTYPE-AC-NOT-IN-PRD", prd_path, "prototype AC is absent from the PRD baseline", ac_id)
        if level in {"L3", "L4"}:
            for ac_id in sorted(prototype_acs - machine_ac_defs):
                self.add("BLOCK", "HANDOFF-PROTOTYPE-AC-NOT-MACHINE-DEFINED", prd_path, "prototype AC has no machine-readable PRD definition", ac_id)
            for view in sorted(prototype_views - declared_views):
                self.add("BLOCK", "HANDOFF-UNDECLARED-PROTOTYPE-VIEW", prd_path, "prototype exposes a view outside the declared PRD scope", view)
            for view in sorted(declared_views - prototype_views):
                self.add("BLOCK", "HANDOFF-DECLARED-VIEW-NOT-PROTOTYPED", prd_path, "declared implementation view is absent from all supplied prototypes", view)
            for metric in sorted(prototype_metrics - prd_metric_refs):
                self.add("BLOCK", "HANDOFF-PROTOTYPE-METRIC-NOT-IN-PRD", prd_path, "prototype metric is absent from the PRD caliber contract", metric)
        self.metrics.update({
            "handoff_prototypes": len(prototype_paths),
            "handoff_views": len(prototype_views),
            "handoff_actions": len(prototype_actions),
            "handoff_acceptance_refs": len(prototype_acs),
            "handoff_metrics": len(prototype_metrics),
        })

    def check_custom_rules(self, custom_root: Path, artifacts: dict[str, list[Path]]) -> None:
        """Load local declarative regex rules; never execute project Python code."""
        rule_dir = custom_root / "validators"
        if not rule_dir.is_dir():
            return
        loaded_rules = 0
        for rule_file in sorted(rule_dir.glob("*.yaml")):
            try:
                document = yaml.safe_load(rule_file.read_text(encoding="utf-8")) or {}
            except (OSError, UnicodeError, yaml.YAMLError) as exc:
                self.add("BLOCK", "CUSTOM-RULE-PARSE", rule_file, f"本地校验规则不可读：{exc}")
                continue
            rules = document.get("rules", []) if isinstance(document, dict) else []
            if not isinstance(rules, list):
                self.add("BLOCK", "CUSTOM-RULE-SHAPE", rule_file, "本地校验文件的 rules 必须是数组")
                continue
            for index, rule in enumerate(rules):
                ref = f"{rule_file.name}:rules[{index}]"
                if not isinstance(rule, dict):
                    self.add("BLOCK", "CUSTOM-RULE-SHAPE", rule_file, "规则必须是对象", ref)
                    continue
                code = str(rule.get("id", ""))
                artifact_kind = str(rule.get("artifact", "")).lower()
                assertion = str(rule.get("assertion", "")).lower()
                severity = str(rule.get("severity", "GAP")).upper()
                pattern = rule.get("pattern")
                unsafe_pattern = isinstance(pattern, str) and bool(re.search(
                    r"\\[1-9]|\(\?<=[^)]|\(\?<!|\([^)]*[+*][^)]*\)\s*(?:[+*]|\{)", pattern
                ))
                if (
                    not re.fullmatch(r"CUST-[A-Z0-9-]+", code, re.I)
                    or artifact_kind not in {*artifacts, "all"}
                    or assertion not in {"must_match", "must_not_match"}
                    or severity not in {"BLOCK", "GAP"}
                    or not isinstance(pattern, str)
                    or len(pattern) > 500
                    or unsafe_pattern
                ):
                    self.add(
                        "BLOCK", "CUSTOM-RULE-CONTRACT", rule_file,
                        "规则需声明 CUST-*、有效 artifact、must_match/must_not_match、BLOCK/GAP 和不含反向引用/嵌套量词的短 pattern",
                        ref,
                    )
                    continue
                try:
                    compiled = re.compile(pattern, re.I | re.M)
                except re.error as exc:
                    self.add("BLOCK", "CUSTOM-RULE-REGEX", rule_file, f"正则无效：{exc}", ref)
                    continue
                target_kinds = list(artifacts) if artifact_kind == "all" else [artifact_kind]
                loaded_rules += 1
                for target_kind in target_kinds:
                    for target in artifacts.get(target_kind, []):
                        raw = self.read(target)
                        matched = bool(compiled.search(raw))
                        failed = assertion == "must_match" and not matched or assertion == "must_not_match" and matched
                        if failed:
                            self.add(
                                severity, code.upper(), target,
                                str(rule.get("message") or f"本地规则 {code} 未通过"),
                                str(rule.get("ref") or ref),
                                affected_consumers=tuple(str(item) for item in rule.get("affected_consumers", []) or []),
                            )
        self.metrics["custom_validator_rules"] = loaded_rules


def _balanced_javascript(source: str) -> bool:
    """Small fallback only; Node syntax checking is preferred when available."""
    stack: list[str] = []
    pairs = {")": "(", "]": "[", "}": "{"}
    quote = ""
    escaped = False
    for char in source:
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in "'\"`":
            quote = char
        elif char in "([{":
            stack.append(char)
        elif char in ")]}":
            if not stack or stack.pop() != pairs[char]:
                return False
    return not quote and not stack


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
    return {
        "status": STATUSES[code],
        "profile": profile,
        "summary": {"blockers": blocks, "p0_unknowns": p0_unknowns, "gaps": gaps, "findings": len(gate.findings)},
        "coverage": "确定性静态门禁；不调用浏览器、LLM 或子 Agent",
        "not_proven": list(NOT_PROVEN_BY_STATIC_GATE),
        "retry_command": retry_command,
        "metrics": {**gate.metrics, "input_read_counts": dict(gate.read_counts)},
        "findings": rendered_findings,
        "exit_code": code,
    }


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
    parser.add_argument("--diagnostics", choices=["first", "summary", "full"], default="full")
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
        if args.diagnostics == "first":
            limit = 1
        elif args.diagnostics == "summary":
            limit = min(max(args.max_findings, 0), 12)
        else:
            limit = max(args.max_findings, 0)
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
