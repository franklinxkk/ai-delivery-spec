"""Stage-0, handoff and custom-rule checks (mixin split out of quality_gate.py)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
for _candidate in (SCRIPT_DIR, SCRIPT_DIR / "validators"):
    if str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

import yaml
from jsonschema import Draft202012Validator
from validate_prd_semantics import collect_defined_ids



def _placeholder_paths(value: object, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            paths.extend(_placeholder_paths(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_placeholder_paths(child, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        text = value.strip()
        if (
            re.search(r"\{[^{}]+\}|(?<![A-Za-z0-9-])(?:TBD|TODO)(?![A-Za-z0-9-])|待指定|待补充|占位", text, re.I)
            or text == "0" * 64
        ):
            paths.append(prefix or "<root>")
    return paths


class HandoffChecks:
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
        placeholders = _placeholder_paths(document)
        if placeholders:
            self.add(
                "BLOCK", "STAGE0-PLACEHOLDER", path,
                "Stage 0 台账仍含模板占位，不能把骨架当作已盘点事实",
                ", ".join(placeholders[:12]),
                affected_consumers=("product", "frontend", "backend", "qa"),
            )
        # disposition is a 5.4.1 contract; older inventories stay exempt so that
        # pre-5.4.1 complete inventories keep passing unchanged.
        version_match = re.match(r"(\d+)\.(\d+)\.(\d+)", str(document.get("schema_version", "")))
        disposition_contract = version_match is not None and tuple(
            int(part) for part in version_match.groups()
        ) >= (5, 4, 1)
        items = document.get("items") or []
        if not isinstance(items, list) or not items:
            legacy_sections = [
                key for key in (
                    "roles", "views", "actions", "states", "objects", "fields",
                    "metrics", "handoffs", "defect_candidates", "unknowns",
                )
                if isinstance(document.get(key), list) and document.get(key)
            ]
            if legacy_sections:
                self.add(
                    "BLOCK", "STAGE0-LEGACY-INVENTORY", path,
                    "检测到旧版分栏台账；不能静默升级为当前事实。请迁移为逐项 items 后重跑",
                    ",".join(legacy_sections),
                )
            else:
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
            if disposition_contract and str(item.get("type", "")).lower() in {"view", "page", "页面"} and not item.get("disposition"):
                self.add(
                    "GAP", "STAGE0-DISPOSITION-MISSING", path,
                    "页面类条目缺少 disposition（adopt_page/inherit_layout/rebuild_interaction/reuse_component/discard）",
                    ref,
                    affected_consumers=("product", "ux", "frontend"),
                )
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
        reachability_metrics = self._check_stage0_reachability(path, document, items)
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
            **reachability_metrics,
        })

    def _check_stage0_reachability(
        self, path: Path, document: dict, items: list[object],
    ) -> dict[str, int]:
        """Validate only explicitly scoped critical brownfield chains.

        Older inventories remain readable. A legacy inventory with a core action or
        handler receives a GAP so it cannot claim a clean reachability PASS, but it
        is not forced to invent a chain. Once ``critical_chains`` is declared, the
        declared slice must be fully auditable.
        """
        item_by_id = {
            str(item.get("id")): item
            for item in items
            if isinstance(item, dict) and item.get("id")
        }
        interaction_types = {"action", "handler", "handoff", "system_process", "process"}
        core_interactions = [
            item_id for item_id, item in item_by_id.items()
            if item.get("core_behavior") is True
            and str(item.get("type", "")).casefold() in interaction_types
        ]
        base_metrics = {
            "stage0_critical_chains": 0,
            "stage0_chain_links": 0,
            "stage0_reachability_breaks": 0,
            "stage0_reachability_unresolved": 0,
        }
        if "critical_chains" not in document:
            if core_interactions:
                self.add(
                    "GAP", "STAGE0-REACHABILITY-NOT-DECLARED", path,
                    "核心动作/处理器尚未声明关键链可达性盘点；旧台账继续兼容，但不能据此宣称主链可达",
                    ", ".join(core_interactions[:8]),
                    affected_consumers=("product", "backend", "qa"),
                )
            return base_metrics

        chains_raw = document.get("critical_chains")
        if not isinstance(chains_raw, list):
            self.add(
                "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                "critical_chains 必须是数组；无法解析的声明不能证明关键链可达",
                "critical_chains",
            )
            return base_metrics
        if not chains_raw:
            severity = "BLOCK" if core_interactions else "GAP"
            self.add(
                severity, "STAGE0-EMPTY-CHAIN-REGISTER", path,
                "已声明 critical_chains 却为空；请删除无意义声明，或只为本轮关键链补来源化盘点",
                ", ".join(core_interactions[:8]) or "critical_chains",
            )
            return base_metrics

        breaks_raw = document.get("reachability_breaks")
        if not isinstance(breaks_raw, list):
            self.add(
                "BLOCK", "STAGE0-BREAK-REGISTER-MISSING", path,
                "声明关键链后必须提供 reachability_breaks 数组；空数组只允许用于已证据化的完整可达链",
                "reachability_breaks",
            )
            breaks_raw = []

        break_by_id: dict[str, dict] = {}
        for index, record in enumerate(breaks_raw):
            ref = f"reachability_breaks[{index}]"
            if not isinstance(record, dict):
                self.add("BLOCK", "STAGE0-BREAK-CONTRACT-INVALID", path, "断裂记录必须是对象", ref)
                continue
            break_id = str(record.get("id", ""))
            if not re.fullmatch(r"INV-BREAK-[A-Z0-9-]+", break_id, re.I):
                self.add("BLOCK", "STAGE0-BREAK-CONTRACT-INVALID", path, "断裂记录必须使用 INV-BREAK-*", ref)
                continue
            if break_id in break_by_id:
                self.add("BLOCK", "STAGE0-BREAK-CONTRACT-INVALID", path, "断裂记录 ID 重复", break_id)
                continue
            break_by_id[break_id] = record
            missing = [
                key for key in (
                    "chain_ref", "path_kind", "classification", "source_ref",
                    "source_location", "description",
                )
                if not record.get(key)
            ]
            if missing:
                self.add(
                    "BLOCK", "STAGE0-BREAK-CONTRACT-INVALID", path,
                    "断裂记录缺少 " + ", ".join(missing), break_id,
                )
            classification = str(record.get("classification", "")).casefold()
            if classification not in {"unknown", "defect_candidate"}:
                self.add(
                    "BLOCK", "STAGE0-BREAK-CONTRACT-INVALID", path,
                    "断裂 classification 只能是 unknown 或 defect_candidate", break_id,
                )
            if classification == "unknown":
                unknown = record.get("unknown") or {}
                if not (
                    isinstance(unknown, dict)
                    and re.fullmatch(r"UNK-[A-Z0-9-]+", str(unknown.get("id", "")), re.I)
                    and str(unknown.get("priority", "")).upper() == "P0"
                    and unknown.get("owner")
                    and unknown.get("blocks_stage")
                ):
                    self.add(
                        "BLOCK", "STAGE0-CRITICAL-BREAK-NOT-OWNED", path,
                        "关键链 UNKNOWN 断裂必须登记 UNK-*、P0、owner 和 blocks_stage",
                        break_id, affected_consumers=("product", "backend", "qa"),
                    )

        chain_ids: set[str] = set()
        chain_links: dict[str, set[str]] = {}
        referenced_breaks: set[str] = set()
        unresolved_count = 0
        link_count = 0
        allowed_reachability = {"reachable", "broken", "unknown", "terminal"}
        allowed_output = {"observed", "missing", "unknown", "not_applicable"}
        allowed_entry = {"observed", "missing", "unknown", "terminal"}
        allowed_guard = {"observed", "missing", "unknown", "not_applicable"}
        allowed_recovery = {"observed", "broken", "unknown", "not_applicable"}
        entry_item_types = {
            "view", "page", "screen", "route", "action", "handoff", "handler",
            "system_process", "process", "event", "queue", "task", "endpoint",
            "视图", "页面", "路由", "动作", "交接", "处理器", "系统处理", "事件", "队列", "任务", "端点",
        }
        guard_item_types = {
            "guard", "rule", "state", "condition", "handler", "system_process",
            "process", "policy", "permission",
            "守卫", "规则", "状态", "条件", "处理器", "系统处理", "策略", "权限",
        }

        def normalize_refs(
            value: object, owner_ref: str, field: str, *, validate_items: bool = True,
        ) -> list[str]:
            if not isinstance(value, list):
                self.add(
                    "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                    f"{field} 必须是引用数组", owner_ref,
                )
                return []
            refs = [str(item) for item in value if str(item)]
            if len(refs) != len(value) or len(refs) != len(set(refs)):
                self.add(
                    "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                    f"{field} 含空值或重复引用", owner_ref,
                )
            for item_ref in refs:
                if validate_items and item_ref not in item_by_id:
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-ORPHAN-ITEM", path,
                        "关键链引用未解析到 Stage 0 items", f"{owner_ref}.{field}->{item_ref}",
                    )
            return refs

        def validate_item_types(
            refs: list[str], allowed_types: set[str], owner_ref: str, field: str,
        ) -> None:
            for item_ref in refs:
                if item_ref not in item_by_id:
                    continue
                item_type = str(item_by_id[item_ref].get("type", "")).casefold()
                if item_type not in allowed_types:
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-REF-TYPE-MISMATCH", path,
                        f"{field} 引用 type={item_type or '<empty>'}，不能证明可进入点或守卫",
                        f"{owner_ref}.{field}->{item_ref}",
                        affected_consumers=("product", "backend", "qa"),
                    )

        for index, chain in enumerate(chains_raw):
            fallback_ref = f"critical_chains[{index}]"
            if not isinstance(chain, dict):
                self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "关键链必须是对象", fallback_ref)
                continue
            chain_id = str(chain.get("id", ""))
            if not re.fullmatch(r"INV-CHAIN-[A-Z0-9-]+", chain_id, re.I):
                self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "关键链必须使用 INV-CHAIN-*", fallback_ref)
                chain_id = fallback_ref
            elif chain_id in chain_ids:
                self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "关键链 ID 重复", chain_id)
            chain_ids.add(chain_id)
            missing_chain = [
                key for key in ("title", "source_ref", "source_location", "assessment_status")
                if not chain.get(key)
            ]
            if missing_chain:
                self.add(
                    "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                    "关键链缺少 " + ", ".join(missing_chain), chain_id,
                )
            assessment = str(chain.get("assessment_status", "")).casefold()
            if assessment not in {"in_progress", "assessed"}:
                self.add(
                    "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                    "assessment_status 只能是 in_progress 或 assessed", chain_id,
                )
            elif assessment == "in_progress":
                severity = "BLOCK" if str(document.get("inventory_status", "")).casefold() == "inventory_complete" else "GAP"
                self.add(
                    severity, "STAGE0-CHAIN-ASSESSMENT-IN-PROGRESS", path,
                    "关键链可达性仍在盘点中，不能宣称该链已经完整可达",
                    chain_id, affected_consumers=("product", "backend", "qa"),
                )

            chain_break_refs = normalize_refs(
                chain.get("break_refs"), chain_id, "break_refs", validate_items=False,
            )
            # Break IDs live in a separate register rather than items.
            for break_ref in chain_break_refs:
                if break_ref not in break_by_id:
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-ORPHAN-BREAK", path,
                        "关键链断裂引用未解析到 reachability_breaks", f"{chain_id}->{break_ref}",
                    )
            links = chain.get("links")
            if not isinstance(links, list) or not links:
                self.add(
                    "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                    "关键链必须至少包含一个 action→processing→output→next link", chain_id,
                )
                chain_links[chain_id] = set()
                continue
            local_link_ids: set[str] = set()
            chain_links[chain_id] = local_link_ids
            chain_has_unresolved = assessment == "in_progress"
            for link_index, link in enumerate(links):
                link_count += 1
                link_fallback = f"{chain_id}.links[{link_index}]"
                if not isinstance(link, dict):
                    self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "关键链 link 必须是对象", link_fallback)
                    chain_has_unresolved = True
                    continue
                link_id = str(link.get("id", ""))
                if not re.fullmatch(r"INV-LINK-[A-Z0-9-]+", link_id, re.I):
                    self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "link 必须使用 INV-LINK-*", link_fallback)
                    link_id = link_fallback
                elif link_id in local_link_ids:
                    self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "link ID 重复", link_id)
                local_link_ids.add(link_id)
                missing_link = [
                    key for key in ("action_ref", "source_ref", "source_location", "reachability")
                    if not link.get(key)
                ]
                if missing_link:
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                        "link 缺少 " + ", ".join(missing_link), link_id,
                    )
                action_ref = str(link.get("action_ref", ""))
                if action_ref not in item_by_id:
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-ORPHAN-ITEM", path,
                        "action_ref 未解析到 Stage 0 items", f"{link_id}->{action_ref or '<empty>'}",
                    )
                elif str(item_by_id[action_ref].get("type", "")).casefold() != "action":
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-REF-TYPE-MISMATCH", path,
                        "action_ref 必须指向 type=action 的盘点项", f"{link_id}->{action_ref}",
                    )
                processing_refs = normalize_refs(link.get("processing_refs"), link_id, "processing_refs")
                for processing_ref in processing_refs:
                    if processing_ref in item_by_id and str(item_by_id[processing_ref].get("type", "")).casefold() not in {
                        "handler", "system_process", "process",
                    }:
                        self.add(
                            "BLOCK", "STAGE0-CHAIN-REF-TYPE-MISMATCH", path,
                            "processing_refs 必须指向 handler/system_process/process 盘点项",
                            f"{link_id}->{processing_ref}",
                        )
                link_break_refs = normalize_refs(
                    link.get("break_refs"), link_id, "break_refs", validate_items=False,
                )
                for break_ref in link_break_refs:
                    if break_ref not in break_by_id:
                        self.add(
                            "BLOCK", "STAGE0-CHAIN-ORPHAN-BREAK", path,
                            "link 断裂引用未解析到 reachability_breaks", f"{link_id}->{break_ref}",
                        )
                referenced_breaks.update(link_break_refs)
                if not set(link_break_refs).issubset(set(chain_break_refs)):
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-BREAK-DRIFT", path,
                        "link.break_refs 必须汇总到所属 chain.break_refs", link_id,
                    )

                outputs = link.get("outputs")
                observed_outputs = 0
                link_unresolved = not processing_refs
                if not isinstance(outputs, dict):
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                        "outputs 必须显式盘点 objects/states/versions/identities", link_id,
                    )
                    link_unresolved = True
                else:
                    for dimension in ("objects", "states", "versions", "identities"):
                        facet = outputs.get(dimension)
                        if not isinstance(facet, dict):
                            self.add(
                                "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                                f"outputs.{dimension} 缺少结构化盘点", link_id,
                            )
                            link_unresolved = True
                            continue
                        status = str(facet.get("status", "")).casefold()
                        refs = normalize_refs(facet.get("refs"), link_id, f"outputs.{dimension}.refs")
                        expected_types = {
                            "objects": {"object", "entity"},
                            "states": {"state"},
                            "versions": {"version", "field"},
                            "identities": {"identity", "field", "key"},
                        }[dimension]
                        for output_ref in refs:
                            if output_ref in item_by_id and str(item_by_id[output_ref].get("type", "")).casefold() not in expected_types:
                                self.add(
                                    "BLOCK", "STAGE0-CHAIN-REF-TYPE-MISMATCH", path,
                                    f"outputs.{dimension} 引用类型不匹配",
                                    f"{link_id}->{output_ref}",
                                )
                        if status not in allowed_output:
                            self.add(
                                "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                                f"outputs.{dimension}.status 无效", link_id,
                            )
                            link_unresolved = True
                        elif status == "observed":
                            observed_outputs += 1
                            if not refs:
                                self.add(
                                    "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                                    f"outputs.{dimension}=observed 必须有 items 引用", link_id,
                                )
                        elif status in {"missing", "unknown"}:
                            link_unresolved = True
                        elif status == "not_applicable" and not facet.get("note"):
                            self.add(
                                "BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path,
                                f"outputs.{dimension}=not_applicable 必须显示来源化理由", link_id,
                            )

                next_entry = link.get("next_entry")
                entry_status = ""
                if not isinstance(next_entry, dict):
                    self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "next_entry 缺少结构化盘点", link_id)
                    link_unresolved = True
                else:
                    entry_status = str(next_entry.get("status", "")).casefold()
                    entry_refs = normalize_refs(next_entry.get("refs"), link_id, "next_entry.refs")
                    validate_item_types(entry_refs, entry_item_types, link_id, "next_entry.refs")
                    if entry_status not in allowed_entry:
                        self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "next_entry.status 无效", link_id)
                        link_unresolved = True
                    elif entry_status == "observed" and not entry_refs:
                        self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "next_entry=observed 必须有入口引用", link_id)
                    elif entry_status in {"missing", "unknown"}:
                        link_unresolved = True
                    elif entry_status == "terminal" and not next_entry.get("note"):
                        self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "terminal 必须说明为何链路在此结束", link_id)

                next_guard = link.get("next_guard")
                guard_status = ""
                if not isinstance(next_guard, dict):
                    self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "next_guard 缺少结构化盘点", link_id)
                    link_unresolved = True
                else:
                    guard_status = str(next_guard.get("status", "")).casefold()
                    guard_refs = normalize_refs(next_guard.get("refs"), link_id, "next_guard.refs")
                    validate_item_types(guard_refs, guard_item_types, link_id, "next_guard.refs")
                    if guard_status not in allowed_guard:
                        self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "next_guard.status 无效", link_id)
                        link_unresolved = True
                    elif guard_status == "observed" and not guard_refs:
                        self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "next_guard=observed 必须有守卫引用", link_id)
                    elif guard_status in {"missing", "unknown"}:
                        link_unresolved = True
                    elif guard_status == "not_applicable" and not next_guard.get("note"):
                        self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "next_guard=not_applicable 必须说明理由", link_id)

                reachability = str(link.get("reachability", "")).casefold()
                if reachability not in allowed_reachability:
                    self.add("BLOCK", "STAGE0-CHAIN-CONTRACT-INVALID", path, "reachability 无效", link_id)
                    link_unresolved = True
                elif reachability == "reachable" and (
                    not processing_refs or not observed_outputs
                    or entry_status != "observed"
                    or guard_status not in {"observed", "not_applicable"}
                    or link_unresolved
                ):
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-REACHABILITY-CONTRADICTION", path,
                        "声明 reachable，但处理器、输出、下一入口或守卫仍缺失/未知",
                        link_id, affected_consumers=("product", "backend", "qa"),
                    )
                elif reachability == "terminal" and (
                    not processing_refs or not observed_outputs or entry_status != "terminal" or link_unresolved
                ):
                    self.add(
                        "BLOCK", "STAGE0-CHAIN-REACHABILITY-CONTRADICTION", path,
                        "声明 terminal，但处理器/输出未观察到或 next_entry 未标为 terminal",
                        link_id,
                    )
                elif reachability in {"broken", "unknown"}:
                    link_unresolved = True
                if link_unresolved:
                    unresolved_count += 1
                    chain_has_unresolved = True
                    if not link_break_refs:
                        self.add(
                            "BLOCK", "STAGE0-CHAIN-UNRESOLVED-UNTRACKED", path,
                            "link 有 missing/unknown/broken，却没有指向断裂清单",
                            link_id, affected_consumers=("product", "backend", "qa"),
                        )

            recovery_paths = chain.get("recovery_paths")
            required_recovery = ("failure", "return", "retry", "compensation")
            if not isinstance(recovery_paths, dict):
                self.add(
                    "BLOCK", "STAGE0-RECOVERY-CONTRACT-INCOMPLETE", path,
                    "关键链必须分别盘点 failure/return/retry/compensation", chain_id,
                )
                chain_has_unresolved = True
            else:
                for kind in required_recovery:
                    recovery = recovery_paths.get(kind)
                    if not isinstance(recovery, dict):
                        self.add(
                            "BLOCK", "STAGE0-RECOVERY-CONTRACT-INCOMPLETE", path,
                            f"recovery_paths.{kind} 缺少结构化盘点", chain_id,
                        )
                        chain_has_unresolved = True
                        continue
                    status = str(recovery.get("status", "")).casefold()
                    entry_refs = normalize_refs(recovery.get("entry_refs"), chain_id, f"recovery_paths.{kind}.entry_refs")
                    validate_item_types(
                        entry_refs, entry_item_types, chain_id, f"recovery_paths.{kind}.entry_refs",
                    )
                    recovery_guard_refs = normalize_refs(
                        recovery.get("guard_refs"), chain_id, f"recovery_paths.{kind}.guard_refs",
                    )
                    validate_item_types(
                        recovery_guard_refs, guard_item_types, chain_id,
                        f"recovery_paths.{kind}.guard_refs",
                    )
                    outcome_refs = normalize_refs(recovery.get("outcome_refs"), chain_id, f"recovery_paths.{kind}.outcome_refs")
                    recovery_break_refs = normalize_refs(
                        recovery.get("break_refs"), chain_id,
                        f"recovery_paths.{kind}.break_refs", validate_items=False,
                    )
                    for break_ref in recovery_break_refs:
                        if break_ref not in break_by_id:
                            self.add(
                                "BLOCK", "STAGE0-CHAIN-ORPHAN-BREAK", path,
                                "恢复路径断裂引用未解析到 reachability_breaks", f"{chain_id}.{kind}->{break_ref}",
                            )
                    referenced_breaks.update(recovery_break_refs)
                    if not set(recovery_break_refs).issubset(set(chain_break_refs)):
                        self.add(
                            "BLOCK", "STAGE0-CHAIN-BREAK-DRIFT", path,
                            "恢复路径 break_refs 必须汇总到所属 chain.break_refs", f"{chain_id}.{kind}",
                        )
                    if status not in allowed_recovery:
                        self.add(
                            "BLOCK", "STAGE0-RECOVERY-CONTRACT-INCOMPLETE", path,
                            f"recovery_paths.{kind}.status 无效", chain_id,
                        )
                        chain_has_unresolved = True
                    elif status == "observed":
                        if not recovery.get("source_ref") or not recovery.get("source_location"):
                            self.add(
                                "BLOCK", "STAGE0-RECOVERY-CONTRACT-INCOMPLETE", path,
                                f"recovery_paths.{kind}=observed 缺少来源", chain_id,
                            )
                        if not entry_refs and not outcome_refs:
                            self.add(
                                "BLOCK", "STAGE0-RECOVERY-CONTRACT-INCOMPLETE", path,
                                f"recovery_paths.{kind}=observed 必须指向可返回入口或结果", chain_id,
                            )
                    elif status in {"broken", "unknown"}:
                        unresolved_count += 1
                        chain_has_unresolved = True
                        if not recovery.get("source_ref") or not recovery.get("source_location"):
                            self.add(
                                "BLOCK", "STAGE0-RECOVERY-CONTRACT-INCOMPLETE", path,
                                f"recovery_paths.{kind}={status} 缺少观察来源", chain_id,
                            )
                        if not recovery_break_refs:
                            self.add(
                                "BLOCK", "STAGE0-CHAIN-UNRESOLVED-UNTRACKED", path,
                                f"recovery_paths.{kind}={status} 却没有指向断裂清单", chain_id,
                            )
                    elif status == "not_applicable" and not recovery.get("note"):
                        self.add(
                            "BLOCK", "STAGE0-RECOVERY-CONTRACT-INCOMPLETE", path,
                            f"recovery_paths.{kind}=not_applicable 必须说明来源化理由", chain_id,
                        )

            if chain_has_unresolved and not chain_break_refs:
                self.add(
                    "BLOCK", "STAGE0-EMPTY-BREAK-REGISTER", path,
                    "关键链仍有未评估、missing、unknown 或 broken，但 chain.break_refs/断裂清单为空",
                    chain_id, affected_consumers=("product", "backend", "qa"),
                )

        for break_id, record in break_by_id.items():
            chain_ref = str(record.get("chain_ref", ""))
            if chain_ref not in chain_ids:
                self.add(
                    "BLOCK", "STAGE0-BREAK-ORPHAN-CHAIN", path,
                    "断裂记录 chain_ref 未解析到 critical_chains", f"{break_id}->{chain_ref or '<empty>'}",
                )
                continue
            link_ref = str(record.get("link_ref", ""))
            if link_ref and link_ref not in chain_links.get(chain_ref, set()):
                self.add(
                    "BLOCK", "STAGE0-BREAK-ORPHAN-LINK", path,
                    "断裂记录 link_ref 未解析到所属关键链", f"{break_id}->{link_ref}",
                )
            if break_id not in referenced_breaks:
                self.add(
                    "BLOCK", "STAGE0-BREAK-NOT-REFERENCED", path,
                    "reachability_breaks 中的记录没有被所属 chain/link/recovery 引用",
                    break_id,
                )

        return {
            "stage0_critical_chains": len(chains_raw),
            "stage0_chain_links": link_count,
            "stage0_reachability_breaks": len(break_by_id),
            "stage0_reachability_unresolved": unresolved_count,
        }

    def check_agent_handoff(self, path: Path) -> None:
        from quality_gate import HANDOFF_SCHEMA  # deferred: avoids circular import
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
        requirement_raw = ""
        requirement_steps: set[str] = set()
        requirement_step_sections: dict[str, str] = {}
        if requirement_ref and requirement_path.is_file():
            requirement_raw = self.read(requirement_path)
            if baseline_hash != self._sha256(requirement_raw):
                self.add("BLOCK", "HANDOFF-REQUIREMENT-HASH-DRIFT", path, "需求基线文件与 baseline.hash 不一致", requirement_ref)
            step_matches = list(re.finditer(
                r"(?m)^#{2,6}\s+(STEP-[A-Z0-9-]+)\b[^\n]*$",
                requirement_raw,
                re.I,
            ))
            for index, match in enumerate(step_matches):
                end = step_matches[index + 1].start() if index + 1 < len(step_matches) else len(requirement_raw)
                step_id = match.group(1).upper()
                requirement_steps.add(step_id)
                requirement_step_sections[step_id] = requirement_raw[match.start():end]
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
        referenced_steps: set[str] = set()
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
            packet_steps = {
                str(ref).upper()
                for ref in packet.get("implementation_step_refs", []) or []
                if str(ref).strip()
            }
            referenced_steps.update(packet_steps)
            for step_id in sorted(packet_steps - requirement_steps):
                self.add(
                    "BLOCK", "HANDOFF-STEP-NOT-IN-PRD", path,
                    "implementation_step_refs 引用了 PRD 中不存在的实施步骤",
                    step_id,
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
            for step_id in sorted(packet_steps):
                if step_id not in packet_raw:
                    self.add(
                        "BLOCK", "HANDOFF-PACKET-STEP-MISSING", path,
                        "工作包正文未包含声明的实施步骤引用",
                        f"{packet_id}->{step_id}",
                        affected_consumers=("frontend", "backend", "qa", "coding_agent"),
                    )
            kind = str(packet.get("kind", "")).lower()
            expected_prefix = {"mod": "MOD-", "xct": "XCT-", "edge": "EDGE-"}.get(kind)
            if expected_prefix and not packet_id.startswith(expected_prefix):
                self.add("BLOCK", "HANDOFF-PACKET-KIND-MISMATCH", path, "工作包 ID 前缀与 kind 不一致", packet_id)
            if kind == "mod" and "qa_projection" not in packet_raw.lower() and "qa 投影" not in packet_raw.lower():
                self.add("BLOCK", "HANDOFF-MOD-NO-QA-PROJECTION", path, "MOD 工作包缺少 qa_projection", packet_id)
            if kind == "xct":
                lowered_packet = packet_raw.lower()
                affected_modules = set(re.findall(r"\bMOD-[A-Z0-9-]+\b", packet_raw, re.I))
                if len(affected_modules) < 2:
                    self.add("BLOCK", "HANDOFF-XCT-INCOMPLETE", path, "XCT 工作包必须明确影响至少两个 MOD-* 模块", packet_id)
                for label, terms in {
                    "影响模块": ("影响模块", "affected modules", "module scope"),
                    "全局不变量": ("全局不变量", "invariant"),
                    "执行点": ("执行点", "生效点", "enforcement point"),
                    "例外与失败处理": ("例外", "异常", "失败", "exception", "failure"),
                }.items():
                    if not any(term in lowered_packet for term in terms):
                        self.add("BLOCK", "HANDOFF-XCT-INCOMPLETE", path, f"XCT 工作包缺少 {label}", packet_id)
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
        step_facets = {
            "入口与责任": (r"入口与责任", r"entry.{0,40}(?:responsib|role|owner)"),
            "输入与权威源": (r"输入与权威源", r"input.{0,60}(?:authorit|source of truth)"),
            "处理与口径": (r"处理与口径", r"process.{0,50}(?:caliber|logic|rule|formula)"),
            "守卫与状态": (r"守卫与状态", r"guard.{0,40}state"),
            "双结果": (r"双结果", r"visible result.{0,80}(?:domain|persistent) result"),
            "事件与责任交接": (r"事件与(?:责任)?交接", r"event.{0,50}handoff"),
            "失败与恢复": (r"失败(?:与)?恢复", r"failure.{0,50}(?:recovery|retry|compensation)"),
            "追溯与验收": (r"追溯(?:与验收)?", r"traceab.{0,40}(?:accept|evidence)"),
        }
        for step_id in sorted(referenced_steps & requirement_steps):
            section = requirement_step_sections.get(step_id, "")
            missing_facets = [
                label
                for label, patterns in step_facets.items()
                if not any(re.search(pattern, section, re.I | re.S) for pattern in patterns)
            ]
            if missing_facets:
                self.add(
                    "BLOCK", "HANDOFF-STEP-INCOMPLETE", requirement_path,
                    "实施步骤卡缺少可独立实现和验收的必要字段：" + "、".join(missing_facets),
                    step_id,
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
        if ready and requirement_steps:
            for packet in document.get("packets", []) or []:
                if isinstance(packet, dict) and not packet.get("implementation_step_refs"):
                    self.add(
                        "BLOCK", "HANDOFF-STEP-CONTRACT-MISSING", path,
                        "ready_for_implementation 工作包必须声明 implementation_step_refs",
                        str(packet.get("id", "<unknown>")),
                        affected_consumers=("frontend", "backend", "qa", "coding_agent"),
                    )
            for step_id in sorted(requirement_steps - referenced_steps):
                self.add(
                    "BLOCK", "HANDOFF-PRD-STEP-NOT-PACKETED", path,
                    "PRD 实施步骤未被任何工作包接收",
                    step_id,
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
        for envelope in document.get("handoffs", []) or []:
            if not isinstance(envelope, dict):
                continue
            affected = set(map(str, envelope.get("affected_packets", []) or []))
            missing = sorted(affected - packet_ids)
            if missing:
                self.add("BLOCK", "HANDOFF-ENVELOPE-ORPHAN-PACKET", path, "HANDOFF 引用不存在的工作包", ", ".join(missing))
            if envelope.get("intent") in {"proposal", "request"} and envelope.get("ack_status") == "applied" and not envelope.get("decision_refs"):
                self.add("BLOCK", "HANDOFF-UNAPPROVED-PROPOSAL", path, "proposal/request 未绑定 DEC/CHG 不得标记 applied", str(envelope.get("handoff_id", "")))
        self.metrics.update({
            "handoff_packets": len(packet_ids),
            "handoff_envelopes": len(document.get("handoffs", []) or []),
            "handoff_prd_steps": len(requirement_steps),
            "handoff_referenced_steps": len(referenced_steps),
        })

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

    def check_review_manifest_binding(self, manifest_path: Path) -> None:
        """Align the human workspace handoff indicator with the supplied agent manifest."""
        document, error = self._yaml_document(manifest_path, self.read(manifest_path))
        if error or document is None:
            return
        manifest_status = str(document.get("status", "")).casefold()
        baseline = document.get("baseline") or {}
        manifest_hash = str(baseline.get("hash", "")) if isinstance(baseline, dict) else ""
        packet_ids = {
            str(item.get("id", "")).upper()
            for item in document.get("packets", []) or []
            if isinstance(item, dict) and item.get("id")
        }
        for review_path, review_document in self.review_workspace_contracts:
            handoff = review_document.get("machine_handoff") or {}
            if not isinstance(handoff, dict):
                continue
            declared_status = str(handoff.get("status", "")).casefold()
            if declared_status != "ready":
                self.add(
                    "BLOCK", "PROTO-REVIEW-HANDOFF-STATUS-DRIFT", review_path,
                    "本次已提供 Coding Agent handoff，但人类评审工作台仍显示未请求或被阻断",
                    declared_status or "machine_handoff.status",
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
                continue
            if manifest_status != "ready_for_implementation":
                self.add(
                    "BLOCK", "PROTO-REVIEW-HANDOFF-NOT-READY", review_path,
                    "评审工作台声称机器交接 ready，但实际 manifest 尚未 ready_for_implementation",
                    manifest_status or "manifest.status",
                    affected_consumers=("product", "coding_agent"),
                )
            review_baseline = review_document.get("baseline") or {}
            review_hash = str(review_baseline.get("hash", "")) if isinstance(review_baseline, dict) else ""
            if review_hash != manifest_hash:
                self.add(
                    "BLOCK", "PROTO-REVIEW-HANDOFF-BASELINE-DRIFT", review_path,
                    "评审工作台与 Coding Agent manifest 不是同一需求基线",
                    str(handoff.get("manifest_ref", "")),
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
            declared_packets = {str(item).upper() for item in handoff.get("packet_refs", []) or []}
            missing_packets = sorted(declared_packets - packet_ids)
            if missing_packets:
                self.add(
                    "BLOCK", "PROTO-REVIEW-HANDOFF-PACKET-DRIFT", review_path,
                    "工作台显示可用的机器工作包在实际 manifest 中不存在",
                    ", ".join(missing_packets[:8]),
                    affected_consumers=("product", "coding_agent"),
                    related_refs=tuple(missing_packets[:50]),
                )
            manifest_ref = str(handoff.get("manifest_ref", ""))
            if manifest_ref and Path(manifest_ref).name.casefold() != manifest_path.name.casefold():
                self.add(
                    "BLOCK", "PROTO-REVIEW-HANDOFF-MANIFEST-DRIFT", review_path,
                    "工作台引用的 handoff 文件与本次提供的 manifest 不一致", manifest_ref,
                    affected_consumers=("product", "coding_agent"),
                )

    def check_handoff(self, prd_path: Path, prototype_paths: list[Path], level: str) -> None:
        """Cross-check the one PRD baseline against one or more prototype projections."""
        try:
            prd = self.read(prd_path)
            prototype_raw = [(path, self.read(path)) for path in prototype_paths]
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "HANDOFF-READ", prd_path, f"handoff artifact cannot be read: {exc}")
            return

        prototype_resolved = {path.resolve() for path in prototype_paths}
        for legacy_path in sorted(self.review_workspace_legacy_paths & prototype_resolved, key=str):
            self.add(
                "BLOCK", "PROTO-REVIEW-WORKSPACE-REQUIRED", legacy_path,
                "旧式评审叠加可以单独视检，但不能作为研发测试交接；请迁移为 v5.4.9/RC4 上下文、语义覆盖与人类投影驱动的评审工作台",
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )
        expected_prd_hash = self._sha256(prd)
        prd_baseline_ids = collect_defined_ids(prd)
        for review_path, review_document in self.review_workspace_contracts:
            if review_path not in prototype_resolved:
                continue
            baseline = review_document.get("baseline") or {}
            baseline_hash = str(baseline.get("hash", "")) if isinstance(baseline, dict) else ""
            if baseline_hash != expected_prd_hash:
                self.add(
                    "BLOCK", "PROTO-REVIEW-BASELINE-DRIFT", review_path,
                    "评审工作台绑定的 baseline.hash 与本次 PRD 内容不一致",
                    str(baseline.get("requirement_ref", "")) if isinstance(baseline, dict) else "baseline",
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
            for point in review_document.get("review_points", []) or []:
                if not isinstance(point, dict):
                    continue
                point_ref = str(point.get("ref", "RVP-UNKNOWN"))
                subject_ref = str(point.get("subject_ref", "")).upper()
                if subject_ref and not subject_ref.startswith("PROTO-OBS-") and subject_ref not in prd_baseline_ids:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-SUBJECT-UNRESOLVED", review_path,
                        "ReviewPoint.subject_ref 未解析到本次提供的权威 PRD 基线",
                        f"{point_ref}->{subject_ref}",
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        related_refs=(point_ref, subject_ref),
                    )
                for source_ref in {
                    str(item).upper() for item in point.get("source_refs", []) or [] if str(item).strip()
                }:
                    if source_ref not in prd_baseline_ids:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-SOURCE-UNRESOLVED", review_path,
                            "ReviewPoint.source_refs 未解析到本次提供的权威 PRD 基线",
                            f"{point_ref}->{source_ref}",
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                            related_refs=(point_ref, source_ref),
                        )
                for acceptance_ref in {
                    str(item).upper() for item in point.get("acceptance_refs", []) or [] if str(item).strip()
                }:
                    if acceptance_ref not in prd_baseline_ids:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-AC-UNRESOLVED", review_path,
                            "ReviewPoint.acceptance_refs 未解析到本次提供的权威 PRD 基线",
                            f"{point_ref}->{acceptance_ref}",
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                            related_refs=(point_ref, acceptance_ref),
                        )
                other_refs: dict[str, set[str]] = {}
                for field in (
                    "actor_refs", "precondition_refs", "visible_result_refs",
                    "domain_result_refs", "boundary_refs", "target_ref",
                ):
                    value = point.get(field)
                    values = value if isinstance(value, list) else [value]
                    refs = {
                        str(item).upper() for item in values
                        if item and str(item).strip() and str(item).upper() != subject_ref
                    }
                    if refs:
                        other_refs[field] = refs
                for field, refs in other_refs.items():
                    for unresolved_ref in sorted(refs - prd_baseline_ids):
                        self.add(
                            "BLOCK", "PROTO-REVIEW-REF-UNRESOLVED", review_path,
                            f"ReviewPoint.{field} 未解析到本次提供的权威 PRD 基线",
                            f"{point_ref}->{unresolved_ref}",
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                            related_refs=(point_ref, unresolved_ref),
                        )
            point_ids = {
                str(item.get("ref", "")).upper()
                for item in review_document.get("review_points", []) or []
                if isinstance(item, dict)
            }
            for item in review_document.get("semantic_coverage_items", []) or []:
                if not isinstance(item, dict):
                    continue
                coverage_id = str(item.get("coverage_id", "SCOV-UNKNOWN")).upper()
                subject_ref = str(item.get("subject_ref", "")).upper()
                source_refs = {
                    str(ref).upper() for ref in item.get("source_refs", []) or [] if str(ref).strip()
                }
                target_ref = str(item.get("target_ref", "") or "").upper()
                unknown_ref = str(item.get("unknown_ref", "") or "").upper()
                mapped_points = {
                    str(ref).upper() for ref in item.get("review_point_refs", []) or [] if str(ref).strip()
                }
                unresolved = {
                    ref for ref in ({subject_ref, target_ref, unknown_ref} | source_refs)
                    if ref and ref not in prd_baseline_ids
                }
                for ref in sorted(unresolved):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-SEMANTIC-REF-UNRESOLVED", review_path,
                        "语义覆盖项未解析到本次提供的权威 PRD 基线",
                        f"{coverage_id}->{ref}",
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        related_refs=(coverage_id, ref),
                    )
                for point_ref in sorted(mapped_points - point_ids):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", review_path,
                        "语义覆盖项引用了不存在的 ReviewPoint",
                        f"{coverage_id}->{point_ref}",
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        related_refs=(coverage_id, point_ref),
                    )

        frontmatter = self._frontmatter(prd)
        declared_views = {str(item).upper() for item in frontmatter.get("page_contract_view_ids", []) if item}
        prd_actions = {item.upper() for item in re.findall(r"\bACT-[A-Z0-9-]+\b", prd, re.I)}
        prd_ac_refs = {item.upper() for item in re.findall(r"\bAC-[A-Z0-9-]+\b", prd, re.I)}
        prd_field_refs = {item.upper() for item in re.findall(r"\bFLD-[A-Z0-9-]+\b", prd, re.I)}
        prd_metric_refs = {item.upper() for item in re.findall(r"\bMETRIC-[A-Z0-9-]+\b", prd, re.I)}
        machine_ac_defs = {
            item.upper()
            for item in re.findall(r"(?m)^\s*(?:-\s+)?id:\s*['\"]?(AC-[A-Z0-9-]+)\b", prd, re.I)
        }
        prototype_views: set[str] = set()
        prototype_actions: set[str] = set()
        prototype_acs: set[str] = set()
        prototype_fields: set[str] = set()
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
            prototype_fields.update(item.upper() for item in re.findall(r"\bdata-field\s*=\s*['\"](FLD-[A-Z0-9-]+)['\"]", tags, re.I))
            prototype_metrics.update(item.upper() for item in re.findall(r"\bdata-metric\s*=\s*['\"](METRIC-[A-Z0-9-]+)['\"]", tags, re.I))

        for action in sorted(prototype_actions - prd_actions):
            self.add("BLOCK", "HANDOFF-PROTOTYPE-ACTION-NOT-IN-PRD", prd_path, "prototype action is absent from the PRD baseline", action)
        for ac_id in sorted(prototype_acs - prd_ac_refs):
            self.add("BLOCK", "HANDOFF-PROTOTYPE-AC-NOT-IN-PRD", prd_path, "prototype AC is absent from the PRD baseline", ac_id)
        if level in {"L2", "L3", "L4"}:
            for field in sorted(prototype_fields - prd_field_refs):
                self.add("BLOCK", "HANDOFF-PROTOTYPE-FIELD-NOT-IN-PRD", prd_path, "prototype field is absent from the PRD field contract", field)
            for metric in sorted(prototype_metrics - prd_metric_refs):
                self.add("BLOCK", "HANDOFF-PROTOTYPE-METRIC-NOT-IN-PRD", prd_path, "prototype metric is absent from the PRD caliber contract", metric)
        if level in {"L3", "L4"}:
            for ac_id in sorted(prototype_acs - machine_ac_defs):
                self.add("BLOCK", "HANDOFF-PROTOTYPE-AC-NOT-MACHINE-DEFINED", prd_path, "prototype AC has no machine-readable PRD definition", ac_id)
            for view in sorted(prototype_views - declared_views):
                self.add("BLOCK", "HANDOFF-UNDECLARED-PROTOTYPE-VIEW", prd_path, "prototype exposes a view outside the declared PRD scope", view)
            for view in sorted(declared_views - prototype_views):
                self.add("BLOCK", "HANDOFF-DECLARED-VIEW-NOT-PROTOTYPED", prd_path, "declared implementation view is absent from all supplied prototypes", view)
        binding_terms = [
            str(term).strip() for term in frontmatter.get("binding_terms", []) or []
            if str(term).strip()
        ]
        if binding_terms:
            from gate_prototype_checks import _visible_text  # deferred: sibling mixin helper
            prd_body = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", prd, flags=re.S)
            prototype_visible = "\n".join(_visible_text(raw) for _path, raw in prototype_raw)
            for term in binding_terms:
                if term not in prd_body or term not in prototype_visible:
                    self.add(
                        "BLOCK", "HANDOFF-BINDING-TERM-MISSING", prd_path,
                        "绑定词未同时出现在 PRD 正文与原型可见文本中，跨端用词不一致",
                        term,
                        affected_consumers=("product", "ux", "frontend", "qa"),
                    )
        if level in {"L3", "L4"}:
            aesthetic_refs = frontmatter.get("aesthetic_decision_refs") or []
            visual_authority = str(frontmatter.get("visual_authority", "")).strip()
            design_lock_ref = str(frontmatter.get("design_lock_ref", "")).strip()
            persisted_visual_lock = bool(visual_authority and design_lock_ref)
            prototype_visual_lock = any(
                re.search(
                    r"visual_authority\s*=\s*(?:existing|greenfield_default|DEC-AESTHETIC-[A-Z0-9-]+)",
                    raw,
                    re.I,
                )
                and re.search(r"design_lock_ref\s*=\s*\S+", raw, re.I)
                for _path, raw in prototype_raw
            )
            if not aesthetic_refs and not persisted_visual_lock and not prototype_visual_lock and not re.search(r"\bDEC-AESTHETIC-[A-Z0-9-]+", prd, re.I):
                self.add(
                    "GAP", "HANDOFF-AESTHETIC-UNDECIDED", prd_path,
                    "L3/L4 交接未声明视觉权威与视觉锁，无法证明跨页面样式一致",
                    affected_consumers=("product", "ux", "frontend"),
                )
        self.metrics.update({
            "handoff_prototypes": len(prototype_paths),
            "handoff_views": len(prototype_views),
            "handoff_actions": len(prototype_actions),
            "handoff_acceptance_refs": len(prototype_acs),
            "handoff_fields": len(prototype_fields),
            "handoff_metrics": len(prototype_metrics),
        })

    def check_custom_rules(
        self,
        custom_root: Path,
        artifacts: dict[str, list[Path]],
        *,
        active_domains: tuple[str, ...] = (),
    ) -> None:
        """Load local declarative regex rules; never execute project Python code."""
        rule_dir = custom_root / "validators"
        if not rule_dir.is_dir():
            return
        normalized_active = {item.strip().casefold() for item in active_domains if item.strip()}
        known_domains: set[str] = set()
        config_path = custom_root / "config.yaml"
        if config_path.is_file():
            try:
                config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
                if not isinstance(config, dict):
                    self.add("BLOCK", "CUSTOM-CONFIG-SHAPE", config_path, "本地扩展配置顶层必须是对象")
                    config = {}
                configured = config.get("domains", [])
                if not isinstance(configured, list):
                    self.add("BLOCK", "CUSTOM-CONFIG-SHAPE", config_path, "config.domains 必须是数组")
                    configured = []
                if isinstance(configured, list):
                    for item in configured:
                        domain_id = item.get("domain_id") if isinstance(item, dict) else item
                        if isinstance(domain_id, str) and domain_id.strip():
                            known_domains.add(domain_id.strip().casefold())
            except (OSError, UnicodeError, yaml.YAMLError) as exc:
                self.add("BLOCK", "CUSTOM-CONFIG-PARSE", config_path, f"本地扩展配置不可读：{exc}")
        unknown_active = sorted(normalized_active - known_domains) if known_domains else []
        if unknown_active:
            self.add(
                "BLOCK", "CUSTOM-DOMAIN-UNKNOWN", config_path,
                "--domain 包含未在 custom/config.yaml 注册的领域",
                ", ".join(unknown_active),
            )
        loaded_rules = 0
        applied_rules = 0
        skipped_domain_rules = 0
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
                singular_domain = rule.get("domain")
                plural_domains = rule.get("domains")
                domain_contract_valid = not (singular_domain is not None and plural_domains is not None)
                if singular_domain is not None:
                    scoped_domains = [singular_domain] if isinstance(singular_domain, str) else []
                    domain_contract_valid = domain_contract_valid and isinstance(singular_domain, str) and bool(singular_domain.strip())
                elif plural_domains is not None:
                    scoped_domains = plural_domains if isinstance(plural_domains, list) else []
                    domain_contract_valid = domain_contract_valid and isinstance(plural_domains, list) and bool(plural_domains)
                else:
                    scoped_domains = []
                domain_contract_valid = domain_contract_valid and all(
                    isinstance(item, str) and bool(item.strip()) for item in scoped_domains
                )
                normalized_rule_domains = {item.strip().casefold() for item in scoped_domains if isinstance(item, str)}
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
                    or not domain_contract_valid
                ):
                    self.add(
                        "BLOCK", "CUSTOM-RULE-CONTRACT", rule_file,
                        "规则需声明 CUST-*、有效 artifact、must_match/must_not_match、BLOCK/GAP 和安全短 pattern；domain/domains 如声明必须非空且只能选一个字段",
                        ref,
                    )
                    continue
                try:
                    compiled = re.compile(pattern, re.I | re.M)
                except re.error as exc:
                    self.add("BLOCK", "CUSTOM-RULE-REGEX", rule_file, f"正则无效：{exc}", ref)
                    continue
                loaded_rules += 1
                if normalized_rule_domains and not normalized_active:
                    self.add(
                        "BLOCK", "CUSTOM-DOMAIN-CONTEXT-MISSING", rule_file,
                        "领域限定规则需要通过 --domain 声明当前工件适用领域",
                        f"{ref}: {', '.join(sorted(normalized_rule_domains))}",
                    )
                    skipped_domain_rules += 1
                    continue
                if normalized_rule_domains and normalized_rule_domains.isdisjoint(normalized_active):
                    skipped_domain_rules += 1
                    continue
                target_kinds = list(artifacts) if artifact_kind == "all" else [artifact_kind]
                applied_rules += 1
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
        self.metrics["custom_validator_rules_applied"] = applied_rules
        self.metrics["custom_validator_rules_skipped_domain"] = skipped_domain_rules
