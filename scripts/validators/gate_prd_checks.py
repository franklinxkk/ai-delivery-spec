"""PRD contract checks for the quality gate (mixin split out of quality_gate.py)."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent.parent
for _candidate in (SCRIPT_DIR, SCRIPT_DIR / "validators"):
    if str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

from prd_structure import analyze as analyze_prd_structure
from validate_coding_agent_contract import (
    BASE_AREAS,
    ID_RULES,
    STRUCTURED_AC_FIELDS,
    has_any,
)
from validate_prd_quality import LEVELS, TERMS


class PRDChecks:
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
        from quality_gate import STAGE_ORDER  # deferred: avoids circular import
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
        # When the same UNK-* is projected in frontmatter and the human table, explicit
        # priority/status/stage values must agree; otherwise the two audiences see
        # different release decisions.
        reported_drift_ids: set[str] = set()
        for line in raw.splitlines():
            if not line.lstrip().startswith("|") or not re.search(r"\bUNK-[A-Z0-9-]+\b", line, re.I):
                continue
            unknown_id = re.search(r"\bUNK-[A-Z0-9-]+\b", line, re.I).group(0).upper()
            lowered = line.lower()
            priority_match = re.search(r"\b(P[01])\b", line, re.I)
            priority = priority_match.group(1).upper() if priority_match else "P1"
            open_status = bool(re.search(r"\|\s*(?:blocked|open|阻塞中?|未关闭)\s*\|", lowered, re.I))
            closed_status = bool(re.search(r"\|\s*(?:closed|resolved|已关闭|已解决)\s*\|", lowered, re.I))
            explicit_status = "blocked" if open_status else "closed" if closed_status else None
            status = explicit_status or "closed"
            stage_pattern = "|".join(re.escape(name) for name in STAGE_ORDER)
            stage_value = re.search(rf"(?:\|\s*|blocks_stage\s*[:=]\s*)({stage_pattern})(?=\s*\||\s|$)", lowered, re.I)
            stage_match = stage_value.group(1).lower() if stage_value else None
            affected_refs = re.findall(r"\b(?:REQ|FLOW|VIEW|STATE|RULE|API|AC)-[A-Z0-9-]+\b", line, re.I)
            if unknown_id in records:
                record = records[unknown_id]
                drifts: list[str] = []
                if priority_match and str(record.get("priority", "")).upper() != priority:
                    drifts.append(f"priority frontmatter={record.get('priority')} body={priority}")
                if explicit_status:
                    front_status = str(record.get("status", "open")).lower()
                    front_open = front_status in {"open", "blocked", "阻塞中", "未关闭"}
                    body_open = explicit_status == "blocked"
                    if front_open != body_open:
                        drifts.append(f"status frontmatter={front_status} body={explicit_status}")
                if stage_match:
                    front_stages = record.get("blocks_stage", "baseline")
                    values = [str(value) for value in front_stages] if isinstance(front_stages, list) else [str(front_stages)]
                    if stage_match not in values:
                        drifts.append(f"blocks_stage frontmatter={values} body={stage_match}")
                if drifts and unknown_id not in reported_drift_ids:
                    self.add(
                        "BLOCK", "PRD-UNKNOWN-METADATA-DRIFT", path,
                        "同一 UNK-* 在机器 frontmatter 与人类正文中的优先级、状态或阻断阶段不一致",
                        f"{unknown_id}: {'; '.join(drifts)}",
                        affected_consumers=("product", "architect", "qa", "coding_agent"),
                        related_refs=(unknown_id,),
                    )
                    reported_drift_ids.add(unknown_id)
                continue
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

        # Conservative contradiction guard: only structured decisions/unknowns lists
        # sharing one ref/topic/key string conflict; no prose semantic matching.
        decision_topics: set[str] = set()
        for item in frontmatter.get("decisions", []) or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("status", "confirmed")).lower() not in {"confirmed", "closed", "resolved", "decided"}:
                continue
            for key_field in ("ref", "topic", "key"):
                if item.get(key_field):
                    decision_topics.add(str(item[key_field]).strip())
        open_unknown_topics: set[str] = set()
        for item in frontmatter.get("unknowns", []) or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("status", "open")).lower() not in {"open", "blocked", "阻塞中", "未关闭"}:
                continue
            for key_field in ("ref", "topic", "key"):
                if item.get(key_field):
                    open_unknown_topics.add(str(item[key_field]).strip())
        for conflict in sorted(decision_topics & open_unknown_topics):
            self.add(
                "BLOCK", "PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT", path,
                "同一主题同时登记为已确认决策和未关闭未知项",
                conflict,
                affected_consumers=("product", "architect", "qa"),
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
        from quality_gate import markdown_headings  # deferred: avoids circular import
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
        # State-machine tables must keep state columns free of engineering IDs.
        engineering_id = re.compile(r"\b(?:API|FLD|ACT|UIACT)-[A-Z0-9-]+\b", re.I)
        lines = raw.splitlines()
        in_fence = False
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence or not stripped.startswith("|"):
                continue
            if index + 1 >= len(lines) or not re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[index + 1]):
                continue
            header_cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            state_columns = [
                column for column, cell in enumerate(header_cells)
                if "状态" in cell
                and not any(marker in cell for marker in ("动作", "触发", "API", "api", "事件", "状态机", "变化", "副作用"))
            ]
            if not state_columns:
                continue
            for row in lines[index + 2:]:
                if not row.strip().startswith("|"):
                    break
                cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
                for column in state_columns:
                    if column >= len(cells):
                        continue
                    for found in engineering_id.finditer(cells[column]):
                        self.add(
                            "BLOCK", "PRD-STATE-SEMANTIC-POLLUTION", path,
                            "状态机表的状态列写入工程 ID，状态语义被污染",
                            f"{header_cells[column]}: {found.group(0).upper()}",
                            affected_consumers=("product", "backend", "qa", "coding_agent"),
                        )
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

    def _check_module_slices_and_facets(
        self, path: Path, raw: str, frontmatter: dict[str, Any], level: str
    ) -> None:
        from quality_gate import _heading_position, _module_slices  # deferred: avoids circular import
        document_lowered = raw.lower()
        facets_raw = frontmatter.get("activated_facets", []) or []
        if not isinstance(facets_raw, list):
            self.add("BLOCK", "PRD-BAD-ACTIVATED-FACETS", path, "activated_facets 必须是数组", "frontmatter.activated_facets")
            return
        facets = {str(item).lower() for item in facets_raw}
        allowed = {"ui", "stateful", "data_submission", "integration", "batch_io", "high_risk"}
        unknown = sorted(facets - allowed)
        if unknown:
            self.add("BLOCK", "PRD-BAD-ACTIVATED-FACETS", path, "未知条件规格: " + ", ".join(unknown))
        governed_facets = facets & {"data_submission", "integration", "batch_io", "high_risk"}
        if level in {"L0", "L1"} and governed_facets:
            self.add(
                "BLOCK", "PRD-FACET-REQUIRES-L2", path,
                "当前条件规格涉及多角色、跨边界或治理合同，不能停留在轻量需求卡",
                ", ".join(sorted(governed_facets)),
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )
        if "data_submission" in facets and level in {"L2", "L3", "L4"}:
            required = {
                "来源与映射": ("来源映射", "字段映射", "source mapping", "mapping"),
                "校验": ("校验", "validation"),
                "提交状态": ("提交状态", "上报状态", "submission state", "reporting state"),
                "重试与幂等": ("重试", "retry"),
                "幂等": ("幂等", "idempotency"),
                "审计": ("审计", "audit"),
                "口径与时效": ("指标口径", "计算口径", "metric caliber", "formula"),
                "刷新/时效": ("刷新", "时效", "延迟", "freshness", "latency"),
                "对账/更正": ("对账", "更正", "reconciliation", "correction"),
            }
            missing = [label for label, terms in required.items() if not any(term in document_lowered for term in terms)]
            if missing:
                self.add(
                    "BLOCK", "PRD-DATA-SUBMISSION-CONTRACT-INCOMPLETE", path,
                    "数据上报/统计口径规格缺少 " + "、".join(missing), "activated_facets.data_submission",
                    affected_consumers=("product", "backend", "qa", "coding_agent"),
                )
        if level not in {"L2", "L3", "L4"}:
            return
        appendix_pos = _heading_position(
            raw, (r"^第四部分", r"^附录\s*A(?:\b|[：:])", r"engineering.+annex")
        )
        main = raw[:appendix_pos] if appendix_pos >= 0 else raw
        module_ids = {item.upper() for item in re.findall(r"\bMOD-[A-Z0-9-]+\b", main, re.I)}
        slices = _module_slices(main)
        self.metrics["module_ids"] = len(module_ids)
        self.metrics["module_slices"] = len(slices)
        for module_id in sorted(module_ids - set(slices)):
            self.add(
                "BLOCK", "PRD-MODULE-SLICE-MISSING", path,
                "模块 ID 没有独立纵向规格章节", module_id,
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                related_refs=(module_id,),
            )
        for module_id, block in slices.items():
            lowered = block.lower()
            groups = {
                "目标/边界/入口/结果": (
                    ("目标", "outcome", "goal"), ("边界", "不负责", "scope", "non-goal"),
                    ("入口", "前置", "entry", "precondition"), ("结果", "出口", "success result"),
                ),
                "主路径/异常/恢复": (
                    ("主路径", "用户故事", "journey", "main path"),
                    ("异常", "失败", "exception", "failure"), ("恢复", "重试", "recovery", "retry"),
                ),
                "页面/动作": (
                    ("view-", "页面", "screen", "ui 不适用", "ui not applicable"),
                    ("act-", "动作", "action"),
                ),
                "字段/数据/权限": (
                    ("fld-", "字段", "field"), ("数据", "来源", "data", "source"),
                    ("权限", "角色", "permission", "role"),
                ),
                "规则/状态/事件": (
                    ("rule-", "规则", "rule"),
                    ("stm-", "state-", "状态", "无状态", "stateless"),
                    ("evt-", "api-", "事件", "集成", "无外部集成", "event", "integration", "no external integration"),
                ),
                "指标/数据质量": (
                    ("metric-", "指标口径", "指标不适用", "metric", "no metric"),
                    ("公式", "去重", "刷新", "数据质量", "不展示指标", "formula", "dedup", "freshness", "data quality"),
                ),
                "验收/未决项": (
                    ("ac-", "验收", "acceptance"),
                    ("unk-", "rev-", "未决", "未知项", "无未决项", "unknown", "open issue", "no open issue"),
                ),
            }
            missing = [
                label for label, requirements in groups.items()
                if any(not any(term in lowered for term in alternatives) for alternatives in requirements)
            ]
            if missing:
                self.add(
                    "BLOCK", "PRD-MODULE-SLICE-INCOMPLETE", path,
                    "模块纵向切片缺少 " + "、".join(missing), module_id,
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    related_refs=(module_id,),
                )

    def check_prd(
        self,
        path: Path,
        level: str,
        *,
        stage: str = "baseline",
        scope_refs: tuple[str, ...] = (),
    ) -> None:
        from quality_gate import MAIN_SECTION_ALIASES, ANNEX_SECTION_ALIASES, STAGE_ORDER, markdown_headings, _heading_position, _has_heading, _heading_language  # deferred: avoids circular import
        if path.suffix.casefold() not in {".md", ".markdown"}:
            self.add(
                "BLOCK", "PRD-NO-FRONTMATTER", path,
                "输入不含 YAML frontmatter，无法执行门禁校验。本产物未经任何自动校验，"
                "导出为 docx/PDF 将永久失去机器可校验性。请在 markdown + frontmatter 形态下完成基线，再导出分发格式。",
                path.suffix or "<无后缀>",
            )
            return
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "PRD-READ", path, f"PRD cannot be read: {exc}")
            return
        lowered = raw.lower()
        frontmatter = self._frontmatter(raw)
        if not frontmatter:
            self.add(
                "BLOCK", "PRD-NO-FRONTMATTER", path,
                "输入不含 YAML frontmatter，无法执行门禁校验。本产物未经任何自动校验，"
                "导出为 docx/PDF 将永久失去机器可校验性。请在 markdown + frontmatter 形态下完成基线，再导出分发格式。",
                "frontmatter",
            )
            return
        if level == "auto":
            declared_level = str(frontmatter.get("delivery_level", frontmatter.get("level", "L2"))).upper()
            level = declared_level if declared_level in LEVELS else "L2"
            self.metrics["resolved_level"] = level
            self.metrics["level_source"] = "frontmatter" if declared_level in LEVELS else "fallback_L2"

        # Human-first language and reading contract.
        h1_count = len(re.findall(r"(?m)^#\s+[^#\n]", raw))
        if h1_count != 1:
            self.add("BLOCK", "PRD-ONE-H1", path, f"unified PRD needs exactly one H1 title; found {h1_count}")
        declared_language = str(frontmatter.get("document_language", "")).strip()
        if not declared_language:
            self.add(
                "BLOCK", "PRD-LANGUAGE-NOT-DECLARED", path,
                "frontmatter 必须声明 document_language，并与用户当前请求语言一致",
                "frontmatter.document_language",
                affected_consumers=("business", "product", "engineering", "qa", "coding_agent"),
            )
        elif frontmatter.get("bilingual") is not True:
            expected = "zh" if declared_language.lower().startswith("zh") else "en"
            structural = [(level, title) for level, title, _pos in markdown_headings(raw) if level <= 3]
            drifted = [title for _level, title in structural if _heading_language(title) not in {expected, "neutral", "mixed"}]
            h1_drift = bool(structural and structural[0][0] == 1 and structural[0][1] in drifted)
            self.metrics["document_language"] = declared_language
            self.metrics["heading_language_drift"] = len(drifted)
            if h1_drift or len(drifted) >= 2:
                self.add(
                    "BLOCK", "PRD-LANGUAGE-DRIFT", path,
                    f"声明 {declared_language}，但关键标题出现 {len(drifted)} 处语言漂移",
                    "; ".join(drifted[:4]),
                    affected_consumers=("business", "product", "engineering", "qa", "coding_agent"),
                )
            elif drifted:
                self.add(
                    "GAP", "PRD-LANGUAGE-DRIFT", path,
                    f"声明 {declared_language}，仍有 1 处标题语言漂移",
                    drifted[0],
                    affected_consumers=("business", "product"),
                )

        if level in {"L2", "L3", "L4"}:
            section_contract = MAIN_SECTION_ALIASES
        elif level == "L1":
            section_contract = (
                ("目标/范围", (r"目标", r"范围", r"goal", r"scope")),
                ("角色/用户故事", (r"角色", r"用户故事", r"role", r"user stor")),
                ("流程/异常", (r"流程", r"异常", r"flow", r"exception")),
                ("验收", (r"验收", r"acceptance")),
            )
        else:
            section_contract = (
                ("目标/范围", (r"目标", r"范围", r"goal", r"scope")),
                ("验收", (r"验收", r"acceptance")),
            )
        for label, aliases in section_contract:
            if not _has_heading(raw, aliases):
                self.add("BLOCK", "PRD-HUMAN-PATH", path, f"human reading path misses {label}", label)

        if level == "L1":
            h2 = [(title, start) for heading_level, title, start in markdown_headings(raw) if heading_level == 2]
            required_l1_sections = {
                "来源、问题与价值": (r"来源.*问题.*价值", r"source.*problem.*value"),
                "目标、范围与非目标": (r"目标.*范围", r"goal.*scope"),
                "角色、用户故事与权限": (r"角色.*用户故事.*权限", r"role.*user stor.*permission"),
                "旅程、流程、异常与状态": (r"(?:旅程|流程).*(?:异常|状态)", r"(?:journey|flow).*(?:exception|state)"),
                "规则、字段与条件规格": (r"规则.*字段.*条件", r"rule.*field.*facet"),
                "验收与测试": (r"验收.*测试", r"acceptance.*test"),
                "未知项与升级判断": (r"未知.*升级", r"unknown.*escalat"),
            }
            for label, aliases in required_l1_sections.items():
                match_index = next(
                    (index for index, (title, _start) in enumerate(h2) if any(re.search(alias, title, re.I) for alias in aliases)),
                    None,
                )
                if match_index is None:
                    self.add(
                        "BLOCK", "PRD-L1-SECTION-MISSING", path,
                        "L1 需求卡缺少完整语义章节，不能只靠零散 ID 追溯", label,
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
                    continue
                start = h2[match_index][1]
                end = h2[match_index + 1][1] if match_index + 1 < len(h2) else len(raw)
                body = raw[start:end]
                meaningful = re.sub(r"(?m)^#{1,6}.*$|^\s*\|?[\s:|-]+\|?\s*$|[`#|:*_\-]", "", body).strip()
                if len(meaningful) < 24:
                    self.add(
                        "BLOCK", "PRD-L1-SECTION-EMPTY", path,
                        "L1 需求卡章节只有标题/表头，没有可实施或可验收内容", label,
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )

        # L0/L1 cards stay compact; L2+ use one unified PRD with exact annexes.
        if level in {"L2", "L3", "L4"}:
            for label, aliases in ANNEX_SECTION_ALIASES:
                if not _has_heading(raw, aliases):
                    self.add("BLOCK", "PRD-ENGINEERING-ANNEX", path, f"engineering annex misses {label}", label)
        appendix_pos = _heading_position(
            raw,
            (r"^第四部分", r"^附录\s*A(?:\b|[：:])", r"工程与\s*AI\s*Coding\s*附录", r"engineering.+ai.+annex"),
        )
        journey_pos = _heading_position(raw, (r"角色旅程", r"用户旅程", r"role journey"))
        if level in {"L2", "L3", "L4"} and (appendix_pos < 0 or journey_pos < 0 or appendix_pos <= journey_pos):
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
        if level in {"L2", "L3", "L4"}:
            for req_id in sorted(requirement_ids - traced):
                self.add("BLOCK", "PRD-UNTRACED-REQ", path, "requirement is absent from the trace annex", req_id)
        if level in {"L2", "L3", "L4"} and trace_text and (
            not re.search(r"\bAC-[A-Z0-9-]+\b", trace_text, re.I)
            or not re.search(r"反向|reverse", trace_text, re.I)
        ):
            self.add("BLOCK", "PRD-NO-REVERSE-TRACE", path, "trace annex must bind AC IDs and declare reverse lookup")
        if level in {"L2", "L3", "L4"} and not has_any(lowered, ("两套 prd", "一份", "one prd", "one baseline")):
            self.add("BLOCK", "PRD-NO-ONE-BASELINE", path, "document does not declare one-baseline semantics")
        if level in {"L2", "L3", "L4"}:
            if not has_any(lowered, ("30 秒摘要", "30秒摘要", "30-second summary", "executive summary")):
                self.add("BLOCK", "PRD-NO-QUICK-SUMMARY", path, "统一 PRD 缺少 30 秒摘要")
            if not has_any(lowered, ("任务式阅读导航", "任务阅读导航", "reading map", "reader task map")):
                self.add("BLOCK", "PRD-NO-READING-MAP", path, "统一 PRD 缺少按角色/任务定位的阅读导航")

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
        self._check_module_slices_and_facets(path, raw, frontmatter, level)
        self._check_semantics(path, raw)

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
