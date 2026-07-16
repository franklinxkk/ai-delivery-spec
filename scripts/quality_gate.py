#!/usr/bin/env python3
"""Token-free final gate for requirement, PRD, and static prototype artifacts.

The gate is deliberately a goalkeeper, not an author: it reads each supplied
artifact once, reports precise contract gaps, and never generates or fixes
requirements. Browser walkthroughs remain explicit acceptance evidence rather
than a hidden default dependency of this static gate.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

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
from validators.validate_unified_prd import ANNEX_MARKERS, MAIN_MARKERS


ROOT = SCRIPT_DIR.parent
REGISTER_SCHEMA = ROOT / "schemas" / "requirement-register.schema.json"
STATUSES = {0: "PASS", 1: "REVIEW_COMPLETE_WITH_GAPS", 2: "BLOCKED"}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    artifact: str
    message: str
    ref: str = ""
    cause: str = ""
    how_to_fix: str = ""


FINDING_GUIDANCE: dict[str, tuple[str, str]] = {
    "GATE-MISSING-INPUT": (
        "The selected gate profile requires an artifact that was not supplied.",
        "Add the missing --requirement, --prd, or --prototype argument shown in the finding.",
    ),
    "GATE-NOT-FILE": (
        "The supplied path does not resolve to a readable file.",
        "Correct the path and confirm the artifact exists before rerunning the same command.",
    ),
    "REQ-PARSE": (
        "The requirement register is not readable UTF-8 YAML.",
        "Fix YAML indentation/quoting or file encoding, then validate the register again.",
    ),
    "REQ-SCHEMA": (
        "The requirement register does not satisfy the declared JSON Schema contract.",
        "Use the finding ref as the field path and copy the expected shape from references/templates/requirement-register-template.yaml.",
    ),
    "PRD-STRUCTURE": (
        "The document has headings or keywords but no verifiable unified-PRD structure.",
        "Add the missing business narrative or engineering annex section using references/templates/unified-requirement-prd-template.md.",
    ),
    "PRD-TOO-THIN": (
        "The requested delivery level needs more page/rule/acceptance detail than the document contains.",
        "Complete the required unified-PRD sections; do not pad the document with empty headings.",
    ),
    "PROTO-NO-PAGE-ANCHOR": (
        "The prototype has no stable page identity for traceability and automated tests.",
        "Add a unique data-testid=\"page-VIEW-*\" anchor to each declared page root.",
    ),
    "PROTO-UNHANDLED-ACTION": (
        "A declared prototype action has no observable dispatch path.",
        "Bind the data-action to one handler and produce a visible state, view, modal, toast, or data result.",
    ),
    "PROTO-JS-SYNTAX": (
        "Static inspection found unbalanced JavaScript delimiters or quotes.",
        "Run a JavaScript syntax check, repair the referenced script block, and verify the document tail.",
    ),
}

PREFIX_GUIDANCE: tuple[tuple[str, str, str], ...] = (
    ("HANDOFF-", "The PRD and prototype disagree on a stable implementation contract.", "Align the referenced VIEW/ACT/AC/METRIC in the single PRD baseline and every affected prototype."),
    ("PROTO-CSS-", "CSS changes or overrides a state contract in a way that can hide or corrupt behavior.", "Remove global/!important pollution and scope visibility rules to the owning component and explicit data-state."),
    ("PROTO-", "The prototype is missing a testable interaction or state contract.", "Repair the referenced element using stable data-testid/data-action/data-state/data-field anchors and a visible outcome."),
    ("PRD-", "The PRD is missing a contract required by the selected delivery level.", "Complete the referenced section with project-confirmed rules, stable IDs, exceptions, and acceptance; do not invent values."),
    ("REQ-", "The requirement lifecycle record is incomplete or internally inconsistent.", "Repair the referenced requirement field and preserve its stable ID, source, decision, and audit history."),
)


def guidance_for(code: str) -> tuple[str, str]:
    """Return bounded, deterministic repair guidance for one finding code."""
    if code in FINDING_GUIDANCE:
        return FINDING_GUIDANCE[code]
    for prefix, cause, fix in PREFIX_GUIDANCE:
        if code.startswith(prefix):
            return cause, fix
    return (
        "The artifact violates a deterministic delivery contract.",
        "Use the code, artifact and ref to repair the bounded contract, then rerun the same gate command.",
    )


class Gate:
    def __init__(self) -> None:
        self._cache: dict[Path, str] = {}
        self.read_counts: Counter[str] = Counter()
        self.findings: list[Finding] = []
        self.metrics: dict[str, Any] = {}

    def read(self, path: Path) -> str:
        key = path.resolve()
        if key not in self._cache:
            self._cache[key] = key.read_text(encoding="utf-8")
            self.read_counts[str(key)] += 1
        return self._cache[key]

    def add(self, severity: str, code: str, path: Path, message: str, ref: str = "") -> None:
        cause, how_to_fix = guidance_for(code)
        self.findings.append(Finding(severity, code, str(path), message, ref, cause, how_to_fix))

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

    def check_prd(self, path: Path, level: str) -> None:
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "PRD-READ", path, f"PRD cannot be read: {exc}")
            return
        lowered = raw.lower()

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
        appendix_pos = min(
            (lowered.find(term) for term in ("第四部分", "附录 a", "工程与 ai coding 附录") if lowered.find(term) >= 0),
            default=-1,
        )
        journey_pos = lowered.find("角色旅程")
        if appendix_pos < 0 or journey_pos < 0 or appendix_pos <= journey_pos:
            self.add("BLOCK", "PRD-READING-ORDER", path, "engineering annex must follow role journeys and module narrative")
        main = raw[:appendix_pos] if appendix_pos >= 0 else raw
        nonblank = [line for line in main.splitlines() if line.strip()]
        table_lines = [line for line in nonblank if line.lstrip().startswith("|")]
        if nonblank and len(table_lines) / len(nonblank) > 0.55:
            self.add("BLOCK", "PRD-TABLE-DOMINATED", path, "human main body is table-dominated; add readable journey/rule explanations")
        requirement_ids = set(re.findall(r"\bREQ-[A-Z0-9-]+\b", raw, re.I))
        trace_pos = lowered.rfind("双向追溯")
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
        if level in {"L3", "L4"}:
            frontmatter = self._frontmatter(raw)
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
            elif not isinstance(frontmatter.get("open_p0_unknown_ids"), list):
                self.add("BLOCK", "PRD-BAD-P0-DISPOSITION", path, "open_p0_unknown_ids must be a list")
            elif frontmatter.get("open_p0_unknown_ids"):
                self.add("BLOCK", "PRD-OPEN-P0-UNKNOWN", path, "direct implementation cannot baseline with unresolved P0 unknowns", ", ".join(map(str, frontmatter["open_p0_unknown_ids"])))

            ac_refs = {item.upper() for item in re.findall(r"\bAC-[A-Z0-9-]+\b", raw, re.I)}
            machine_ac_defs = {
                item.upper()
                for item in re.findall(r"(?m)^\s*(?:-\s+)?id:\s*['\"]?(AC-[A-Z0-9-]+)\b", raw, re.I)
            }
            for ac_id in sorted(ac_refs - machine_ac_defs):
                self.add("BLOCK", "PRD-AC-NO-MACHINE-DEFINITION", path, "referenced AC has no exact machine-readable definition", ac_id)
            for line_no, line in enumerate(raw.splitlines(), 1):
                if not re.match(r"\s*(?:\||-\s+id:)", line):
                    continue
                loose = re.search(
                    r"\b(?:REQ|ROLE|FLOW|VIEW|REG|ACT|FLD|STM|STATE|RULE|API|EVT|INT|AC|TEST|EVD|CHG|REV|REL|METRIC)-[A-Z0-9-]*(?:\*|\.\.|…)",
                    line,
                    re.I,
                )
                if loose:
                    self.add("BLOCK", "PRD-NONEXACT-ID", path, "baseline contract rows cannot use wildcard/range stable IDs", f"line {line_no}: {loose.group(0)}")
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
            markers = list(re.finditer(r"<!--\s*PAGE-CONTRACT:\s*(VIEW-[A-Z0-9-]+)\s*-->", raw, re.I))
            blocks: dict[str, str] = {}
            for index, marker in enumerate(markers):
                end = markers[index + 1].start() if index + 1 < len(markers) else len(raw)
                blocks[marker.group(1).upper()] = raw[marker.end():end]
            required_surfaces = {
                "purpose/entry": ("页面目标", "purpose", "入口"),
                "region layout": ("区域布局", "layout"),
                "metric caliber": ("指标口径", "metric"),
                "filters": ("筛选", "filter"),
                "columns/tree/canvas": ("列表列", "列", "树", "画布", "column"),
                "fields/controls": ("字段与控件", "控件", "field"),
                "actions/permissions": ("动作", "权限", "action"),
                "pagination/batch": ("分页", "pagination"),
                "import": ("导入", "不适用", "not applicable"),
                "export": ("导出", "不适用", "not applicable"),
                "states/exceptions": ("状态", "异常", "exception"),
                "prototype binding": ("原型绑定", "prototype binding"),
            }
            for view in [str(item).upper() for item in declared_views]:
                block = blocks.get(view, "")
                if not block:
                    self.add("BLOCK", "PRD-MISSING-PAGE-CONTRACT", path, "declared view has no PAGE-CONTRACT block", view)
                    continue
                lowered_block = block.lower()
                for label, terms in required_surfaces.items():
                    if not any(term.lower() in lowered_block for term in terms):
                        self.add("BLOCK", "PRD-INCOMPLETE-PAGE-CONTRACT", path, f"page contract misses {label}", view)
                metric_not_applicable = bool(re.search(r"指标[^\n]{0,40}(?:不适用|not applicable)", lowered_block))
                if not metric_not_applicable and not (
                    re.search(r"\bMETRIC-[A-Z0-9-]+\b", block, re.I)
                    and has_any(lowered_block, ("公式", "分子", "分母", "去重", "时间窗口"))
                ):
                    self.add("BLOCK", "PRD-METRIC-NO-CALIBER", path, "displayed metrics need METRIC IDs and explicit formula/caliber or Not applicable", view)
                def concrete_ids(prefix: str) -> set[str]:
                    values: set[str] = set()
                    for found in re.finditer(rf"\b{prefix}-[A-Z0-9-]+", block, re.I):
                        value = found.group(0).upper()
                        if value.endswith("-") or (found.end() < len(block) and block[found.end()] == "*"):
                            continue
                        values.add(value)
                    return values

                field_not_applicable = bool(re.search(
                    r"(?:字段|字段与控件)\s*(?:[:：—-]\s*)?(?:不适用|不存在可编辑业务字段|not applicable)",
                    lowered_block,
                ))
                if not field_not_applicable and len(concrete_ids("FLD")) < 2:
                    self.add("BLOCK", "PRD-PAGE-NO-FIELDS", path, "four-lens handoff needs concrete stable FLD contracts for the view", view)
                if len(concrete_ids("ACT")) < 2:
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
        page_testids = [item for item in testids if item.lower().startswith("page-")]
        if not page_testids:
            self.add("BLOCK" if actions or level in {"L2", "L3", "L4"} else "GAP", "PROTO-NO-PAGE-ANCHOR", path, "no page-* data-testid root was found")
        for duplicate in sorted(item for item, count in Counter(testids).items() if count > 1 and item.lower().startswith("page-")):
            self.add("BLOCK", "PROTO-DUPLICATE-PAGE", path, "page data-testid must be unique", duplicate)
        if level in {"L2", "L3", "L4"}:
            for action in actions:
                if not re.fullmatch(r"ACT-[A-Z0-9-]+", action, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-ACTION", path, "data-action must bind a stable ACT-* ID", action)
            for metric in metrics:
                if not re.fullmatch(r"METRIC-[A-Z0-9-]+", metric, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-METRIC", path, "data-metric must bind a stable METRIC-* ID", metric)
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
            if re.search(r"(?:setAttribute\s*\(\s*['\"]data-action|dataset\.action\s*=)", scripts, re.I):
                self.add("BLOCK", "PROTO-RUNTIME-ACTION-RETROFIT", path, "data-action IDs must be authored in view templates, not retrofitted at runtime")
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
        self.metrics.update({"prototype_pages": len(page_testids), "prototype_actions": len(actions), "prototype_states": len(states), "prototype_fields": len(fields), "prototype_metrics": len(metrics)})

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
    gaps = sum(item.severity == "GAP" for item in gate.findings)
    code = 2 if blocks else 1 if gaps else 0
    return {
        "status": STATUSES[code],
        "profile": profile,
        "summary": {"blockers": blocks, "gaps": gaps, "findings": len(gate.findings)},
        "coverage": "deterministic static scan; no browser and no generative model",
        "retry_command": retry_command,
        "metrics": {**gate.metrics, "input_read_counts": dict(gate.read_counts)},
        "findings": [asdict(item) for item in gate.findings],
        "exit_code": code,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Lightweight, non-generative final quality gate")
    parser.add_argument("--profile", choices=["requirement", "prd", "prototype", "handoff", "full"], required=True)
    parser.add_argument("--requirement", type=Path, help="requirement register YAML")
    parser.add_argument("--prd", type=Path, help="unified PRD Markdown")
    parser.add_argument("--prototype", type=Path, action="append", help="HTML prototype; repeat for admin/H5/multi-surface handoff")
    parser.add_argument("--level", choices=list(LEVELS), default="L2")
    parser.add_argument("--format", choices=["concise", "json"], default="concise")
    parser.add_argument("--max-findings", type=int, default=20)
    args = parser.parse_args()
    required = {
        "requirement": ("requirement",),
        "prd": ("prd",),
        "prototype": ("prototype",),
        "handoff": ("prd", "prototype"),
        "full": ("requirement", "prd", "prototype"),
    }[args.profile]
    gate = Gate()
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
                gate.check_prd(item, args.level)
            else:
                gate.check_prototype(item, args.level)
    valid_prd = args.prd if args.prd and args.prd.is_file() else None
    valid_prototypes = [path for path in (args.prototype or []) if path.is_file()]
    if args.profile in {"handoff", "full"} and valid_prd and valid_prototypes:
        gate.check_handoff(valid_prd, valid_prototypes, args.level)
    retry_command = "python scripts/quality_gate.py " + subprocess.list2cmdline(sys.argv[1:])
    payload = result_payload(gate, args.profile, retry_command)
    if args.format == "json":
        print(json.dumps({key: value for key, value in payload.items() if key != "exit_code"}, ensure_ascii=True, indent=2))
    else:
        summary = payload["summary"]
        print(f"{payload['status']} profile={args.profile} blockers={summary['blockers']} gaps={summary['gaps']}")
        for item in gate.findings[: max(args.max_findings, 0)]:
            ref = f" [{item.ref}]" if item.ref else ""
            print(f"{item.severity} {item.code}{ref}: {item.message}")
            print(f"  FIX: {item.how_to_fix}")
        hidden = len(gate.findings) - max(args.max_findings, 0)
        if hidden > 0:
            print(f"... {hidden} additional findings; rerun with --format json")
        if gate.findings:
            print(f"RETRY: {payload['retry_command']}")
    return int(payload["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
