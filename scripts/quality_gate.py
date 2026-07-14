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
        self.findings.append(Finding(severity, code, str(path), message, ref))

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
        self.metrics.update({"prd_headings": len(re.findall(r"(?m)^#{1,4}\s+\S", raw)), "prd_requirement_ids": len(requirement_ids)})

    def check_prototype(self, path: Path, level: str) -> None:
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "PROTO-READ", path, f"prototype cannot be read: {exc}")
            return
        testids = re.findall(r"\bdata-testid\s*=\s*['\"]([^'\"]+)['\"]", raw, re.I)
        actions = sorted(set(re.findall(r"\bdata-action\s*=\s*['\"]([^'\"]+)['\"]", raw, re.I)))
        states = sorted(set(re.findall(r"\bdata-state\s*=\s*['\"]([^'\"]+)['\"]", raw, re.I)))
        fields = sorted(set(re.findall(r"\bdata-(?:field|bind)\s*=\s*['\"]([^'\"]+)['\"]", raw, re.I)))
        page_testids = [item for item in testids if item.lower().startswith("page-")]
        if not page_testids:
            self.add("BLOCK" if actions or level in {"L2", "L3", "L4"} else "GAP", "PROTO-NO-PAGE-ANCHOR", path, "no page-* data-testid root was found")
        for duplicate in sorted(item for item, count in Counter(testids).items() if count > 1 and item.lower().startswith("page-")):
            self.add("BLOCK", "PROTO-DUPLICATE-PAGE", path, "page data-testid must be unique", duplicate)
        if level in {"L2", "L3", "L4"}:
            for action in actions:
                if not re.fullmatch(r"ACT-[A-Z0-9-]+", action, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-ACTION", path, "data-action must bind a stable ACT-* ID", action)
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
        inline_action_tags = {
            action
            for tag in re.findall(r"<[^>]+\bdata-action\s*=\s*['\"][^'\"]+['\"][^>]*>", raw, re.I | re.S)
            for action in re.findall(r"\bdata-action\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
            if re.search(r"\bonclick\s*=", tag, re.I)
        }
        has_listener = bool(re.search(r"addEventListener\s*\(\s*['\"](?:click|change|submit|input)['\"]", scripts, re.I))
        reads_action = bool(re.search(r"dataset\.action|getAttribute\s*\(\s*['\"]data-action['\"]|closest\s*\(\s*['\"]\[data-action\]", scripts, re.I))
        generic_dispatch = bool(re.search(r"(?:handlers?|actions?|actionHandlers?)\s*\[\s*action\s*\]|(?:dispatch|handle)Action\s*\(\s*action\b", scripts, re.I))
        for action in actions:
            exact_in_script = bool(re.search(rf"(?<![A-Z0-9-]){re.escape(action)}(?![A-Z0-9-])", scripts, re.I))
            if action not in inline_action_tags and not (has_listener and reads_action and (generic_dispatch or exact_in_script)):
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
        self.metrics.update({"prototype_pages": len(page_testids), "prototype_actions": len(actions), "prototype_states": len(states), "prototype_fields": len(fields)})


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


def result_payload(gate: Gate, profile: str) -> dict[str, Any]:
    blocks = sum(item.severity == "BLOCK" for item in gate.findings)
    gaps = sum(item.severity == "GAP" for item in gate.findings)
    code = 2 if blocks else 1 if gaps else 0
    return {
        "status": STATUSES[code],
        "profile": profile,
        "summary": {"blockers": blocks, "gaps": gaps, "findings": len(gate.findings)},
        "coverage": "deterministic static scan; no browser and no generative model",
        "metrics": {**gate.metrics, "input_read_counts": dict(gate.read_counts)},
        "findings": [asdict(item) for item in gate.findings],
        "exit_code": code,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Lightweight, non-generative final quality gate")
    parser.add_argument("--profile", choices=["requirement", "prd", "prototype", "full"], required=True)
    parser.add_argument("--requirement", type=Path, help="requirement register YAML")
    parser.add_argument("--prd", type=Path, help="unified PRD Markdown")
    parser.add_argument("--prototype", type=Path, help="single-file HTML prototype")
    parser.add_argument("--level", choices=list(LEVELS), default="L2")
    parser.add_argument("--format", choices=["concise", "json"], default="concise")
    parser.add_argument("--max-findings", type=int, default=20)
    args = parser.parse_args()
    required = {
        "requirement": ("requirement",),
        "prd": ("prd",),
        "prototype": ("prototype",),
        "full": ("requirement", "prd", "prototype"),
    }[args.profile]
    gate = Gate()
    for name in required:
        value = getattr(args, name)
        if value is None:
            gate.add("BLOCK", "GATE-MISSING-INPUT", Path("<input>"), f"--{name} is required for profile={args.profile}", name)
        elif not value.is_file():
            gate.add("BLOCK", "GATE-NOT-FILE", value, "input does not exist or is not a file", name)
        elif name == "requirement":
            gate.check_requirement(value)
        elif name == "prd":
            gate.check_prd(value, args.level)
        else:
            gate.check_prototype(value, args.level)
    payload = result_payload(gate, args.profile)
    if args.format == "json":
        print(json.dumps({key: value for key, value in payload.items() if key != "exit_code"}, ensure_ascii=True, indent=2))
    else:
        summary = payload["summary"]
        print(f"{payload['status']} profile={args.profile} blockers={summary['blockers']} gaps={summary['gaps']}")
        for item in gate.findings[: max(args.max_findings, 0)]:
            ref = f" [{item.ref}]" if item.ref else ""
            print(f"{item.severity} {item.code}{ref}: {item.message}")
        hidden = len(gate.findings) - max(args.max_findings, 0)
        if hidden > 0:
            print(f"... {hidden} additional findings; rerun with --format json")
    return int(payload["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
