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

