#!/usr/bin/env python3
"""Validate PRD quality signals that are safe to check deterministically.

This script is intentionally conservative. It does not claim to replace product,
engineering, AI, QA, or architecture review. It only enforces checks when the
source artifact or a machine-readable manifest makes them deterministic.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


WILDCARD_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+-(?:\*|[.][.][A-Z0-9*]+|\d+[.][.]\d+)\b")
UNSUPPORTED_NUMERIC_RE = re.compile(
    r"(?i)\b(?:\d+(?:\.\d+)?%|\d+\s*(?:cases|tokens|ms|s|seconds|minutes)|temperature\s*=\s*\d)"
)

# Language check: detect English-heavy lines (>= 80% ASCII alpha characters)
# Used to enforce the Output Language Rules from readability-layer.md
ASCII_ALPHA_RE = re.compile(r"[A-Za-z]")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
TECH_IDENTIFIER_RE = re.compile(
    r"(?i)\b("
    r"data-[a-z0-9_-]+|data-testid|data-action|data-field|"
    r"FRR|AC-YAML|ac_structured|Given|When|Then|API|REST|JSON|YAML|"
    r"AC-[A-Z0-9-]+|SRC-[A-Z0-9-]+|LAY-[A-Z0-9-]+|"
    r"M\d{2}(?:-F\d{2}|-V\d{2})?|BR-M\d{2}-F\d{2}-\d{2}"
    r")\b"
)
FENCE_RE = re.compile(r"^```")
TABLE_HEADER_RE = re.compile(r"^\s*\|")
HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
HEADING_DETAIL_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FRR_HEADING_RE = re.compile(r"^(#{3,4})\s+(M\d{2}-F\d{2})\b")
FRR_ID_RE = re.compile(r"\bM\d{2}-F\d{2}\b")
r"""
FRR_SECTION_RE = re.compile(r"^#{4,6}\s*(?:[§搂]\s*)?(\d{1,2})\b")
FRR_SECTION_RE = re.compile(r"^#{4,6}\s*(?:§\s*)?(\d{1,2})\b")
FRR_SECTION_RE = re.compile(r"^#{4,6}\s*(?:[§搂]\s*)?(\d{1,2})\b")
"""
FRR_SECTION_RE = re.compile(r"^#{4,6}\s*(?:(?:\u00a7|\u6402)\s*)?(\d{1,2})\b")
FRR_COVERAGE_TRIGGER_RE = re.compile(
    r"(Release Function Inventory|Function Inventory|Complete Functional Requirement|"
    r"Stage 3|阶段三|完整功能需求|ac_structured)",
    re.IGNORECASE,
)
FULL_PRD_TRIGGER_RE = re.compile(
    r"(Human-First Full PRD|AI-Coding Full PRD|PRD Profile|Stage 3 Complete Functional Requirement|"
    r"阶段三\s*完整功能需求|development handoff|研发|测试|交付)",
    re.IGNORECASE,
)
RELEASE_INVENTORY_RE = re.compile(r"(Release Function Inventory|Function Inventory|功能清单|发布功能清单)", re.IGNORECASE)
COMPLETION_LEDGER_RE = re.compile(r"(PRD Completion Ledger|Completion Ledger|完成度台账|完成台账)", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(
    r"(?i)^(?:todo|tbd|n/a|na|none|null|same as above|see prototype|existing logic|"
    r"\u5f85\u8865\u5145|\u5f85\u5b9a|\u540c\u4e0a|\u89c1\u539f\u578b|\u6309\u73b0\u6709\u903b\u8f91|[-_/\\.]*)$"
)
RFI_TABLE_HEADER_RE = re.compile(
    r"\|(?=[^\n]*(?:Function ID|功能 ID|功能ID))(?=[^\n]*(?:Release Scope|发布范围|Scope|范围))[^\n]*\|",
    re.IGNORECASE,
)
_DISABLED_LEDGER_TABLE_HEADER_RE = r"""
    r"\|(?=[^\n]*(?:Function ID|Module|模块|功能))(?=[^\n]*(?:Planned|Completed|Status|计划|完成|状态))[^\n]*\|",
    re.IGNORECASE,
)
PART1_RE = re.compile(r"^##\s+.*(?:Part 1|第一部分).*$", re.MULTILINE | re.IGNORECASE)
PART2_RE = re.compile(r"^##\s+.*(?:Part 2|第二部分).*$", re.MULTILINE | re.IGNORECASE)
"""
r"""
LEDGER_TABLE_HEADER_RE = re.compile(
    r"\|(?=[^\n]*(?:Function ID|Module|模块|功能))"
    r"(?=[^\n]*(?:Planned|Completed|Complete Sections|Status|计划|完成|状态))[^\n]*\|",
    re.IGNORECASE,
)
PART1_RE = re.compile(r"^##\s+.*(?:Part 1|第一部分).*$", re.MULTILINE | re.IGNORECASE)
PART2_RE = re.compile(r"^##\s+.*(?:Part 2|第二部分).*$", re.MULTILINE | re.IGNORECASE)
FULL_PRD_TRIGGER_RE = re.compile(
    r"(Human-First Full PRD|AI-Coding Full PRD|PRD Profile|"
    r"Stage 3 Complete Functional Requirement|Complete Functional Requirement Records|"
    r"Development Handoff|development handoff|PRD Completion Ledger|研发|测试|交付)",
    re.IGNORECASE,
)
RELEASE_INVENTORY_RE = re.compile(
    r"(Release Function Inventory|Function Inventory|功能清单|发布功能清单)",
    re.IGNORECASE,
)
COMPLETION_LEDGER_RE = re.compile(
    r"(PRD Completion Ledger|Completion Ledger|完成度台账|完成台账)",
    re.IGNORECASE,
)
CONTINUATION_REQUIRED_RE = re.compile(
    r"(CONTINUATION_REQUIRED|REVIEW_COMPLETE_WITH_GAPS|Completion State:\s*BLOCKED|Completion state:\s*BLOCKED)",
    re.IGNORECASE,
)
FINAL_PASS_RE = re.compile(r"(?im)^\s*Completion state\s*:\s*PASS\s*$")
RFI_TABLE_HEADER_RE = re.compile(
    r"\|(?=[^\n]*(?:Function ID|功能 ID|功能ID))(?=[^\n]*(?:Release Scope|Scope|发布范围|范围))[^\n]*\|",
    re.IGNORECASE,
)
"""
LEDGER_TABLE_HEADER_RE = re.compile(
    r"\|(?=[^\n]*(?:Function ID|Module|Function))"
    r"(?=[^\n]*(?:Planned|Completed|Complete Sections|Status))[^\n]*\|",
    re.IGNORECASE,
)
PART1_RE = re.compile(r"^##\s+.*(?:Part 1|Part One).*$", re.MULTILINE | re.IGNORECASE)
PART2_RE = re.compile(r"^##\s+.*(?:Part 2|Part Two).*$", re.MULTILINE | re.IGNORECASE)
FULL_PRD_TRIGGER_RE = re.compile(
    r"(Human-First Full PRD|AI-Coding Full PRD|PRD Profile|"
    r"Stage 3 Complete Functional Requirement|Complete Functional Requirement Records|"
    r"Development Handoff|development handoff|PRD Completion Ledger)",
    re.IGNORECASE,
)
RELEASE_INVENTORY_RE = re.compile(
    r"(Release Function Inventory|Function Inventory)",
    re.IGNORECASE,
)
COMPLETION_LEDGER_RE = re.compile(
    r"(PRD Completion Ledger|Completion Ledger)",
    re.IGNORECASE,
)
CONTINUATION_REQUIRED_RE = re.compile(
    r"(CONTINUATION_REQUIRED|REVIEW_COMPLETE_WITH_GAPS|Completion State:\s*BLOCKED|Completion state:\s*BLOCKED)",
    re.IGNORECASE,
)
FINAL_PASS_RE = re.compile(r"(?im)^\s*Completion state\s*:\s*PASS\s*$")
RFI_TABLE_HEADER_RE = re.compile(
    r"\|(?=[^\n]*(?:Function ID))(?=[^\n]*(?:Release Scope|Scope))[^\n]*\|",
    re.IGNORECASE,
)
FRR_INDEX_SUBSTITUTE_RE = re.compile(
    r"(FRR\s*Index|FRR\s*Map|索引表|索引地图|详见|参见|see\s+(?:the\s+)?(?:prd|template|appendix|annex|file))",
    re.IGNORECASE,
)
LAZY_REFERENCE_RE = re.compile(
    "("
    "\u89c1\u539f\u578b|\u53c2\u89c1\u539f\u578b|\u53c2\u8003\u539f\u578b|"
    "\u89c1\u9644\u4ef6|\u6309\u73b0\u6709\u903b\u8f91|\u540c\u4e0a|"
    "see prototype|same as above|existing logic|see attachment"
    ")",
    re.IGNORECASE,
)
REFERENCE_ANCHOR_RE = re.compile(
    r"(data-testid|data-action|FRR|AC-|SRC-|Source ID|view_id|region_id|"
    r"prototype lock|prototype path|\[(?:page|modal|drawer|region|btn|action|field)-)",
    re.IGNORECASE,
)
FRR_OPERATION_TABLE_RE = re.compile(
    r"\|(?=[^\n]*(?:\u64cd\u4f5c|Action))"
    r"(?=[^\n]*(?:\u5141\u8bb8\u89d2\u8272|Allowed Roles?|Allowed Role))"
    r"(?=[^\n]*(?:\u5141\u8bb8\u72b6\u6001|Allowed States?|Allowed State|"
    r"\u786e\u8ba4|\u5e42\u7b49|\u53ef\u89c1\u7ed3\u679c|\u9886\u57df\u7ed3\u679c|"
    r"Confirmation|Idempotent|Visible Result|Domain Result))[^\n]*\|",
    re.IGNORECASE,
)
LAYOUT_REGION_TABLE_RE = re.compile(
    r"\|(?=[^\n]*Layout ID)(?=[^\n]*(?:Region|\u533a\u57df))"
    r"(?=[^\n]*(?:\u4f4d\u7f6e|Position|\u4e3b\u8981\u7ec4\u4ef6|Component))[^\n]*\|",
    re.IGNORECASE,
)


def read_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".html", ".json", ".yaml", ".yml"}:
        return path.read_text(encoding="utf-8-sig", errors="ignore")
    if suffix == ".docx":
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        texts = [node.text or "" for node in root.findall(".//w:t", ns)]
        return "\n".join(texts)
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def add_failure(failures: list[str], message: str) -> None:
    failures.append(message)


def check_wildcard_ids(text: str, failures: list[str]) -> None:
    matches = sorted(set(WILDCARD_ID_RE.findall(text)))
    if matches:
        add_failure(failures, "wildcard ID references found: " + ", ".join(matches[:20]))


def check_duplicate_boilerplate(text: str, failures: list[str]) -> None:
    lines = [
        re.sub(r"\s+", " ", line.strip())
        for line in text.splitlines()
        if len(line.strip()) >= 90 and "|" not in line
    ]
    repeated = [(line, count) for line, count in Counter(lines).items() if count >= 3]
    if repeated:
        samples = "; ".join(f"{count}x {line[:80]}" for line, count in repeated[:10])
        add_failure(failures, "duplicate boilerplate detected: " + samples)


def check_unsupported_numeric_claims(text: str, failures: list[str]) -> None:
    """Flag likely unsupported numeric claims.

    This is a heuristic warning promoted to failure only when the local paragraph
    does not indicate evidence, source, calibration, baseline, proposed status,
    or owner decision.
    """

    paragraphs = re.split(r"\n\s*\n", text)
    suspicious = []
    safe_words = re.compile(r"(?i)(source|evidence|baseline|calibrat|owner|decision|proposed|example|sample|annex|verified|依据|来源|证据|基线|校准|建议|示例|附件|负责人)")
    for para in paragraphs:
        if UNSUPPORTED_NUMERIC_RE.search(para) and not safe_words.search(para):
            suspicious.append(re.sub(r"\s+", " ", para.strip())[:160])
    if suspicious:
        add_failure(failures, "unsupported numeric claim candidates: " + " | ".join(suspicious[:10]))


def check_manifest(manifest_path: Path, failures: list[str]) -> None:
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))

    artifacts = data.get("artifacts")
    if artifacts is None:
        add_failure(failures, "manifest missing artifacts[] package inventory")
    elif not isinstance(artifacts, list) or not artifacts:
        add_failure(failures, "manifest artifacts[] must be a non-empty list")
    else:
        allowed_status = {
            "EMBEDDED",
            "AUTHORITATIVE_ANNEX",
            "DEFERRED",
            "CONFLICT",
            "NOT_APPLICABLE",
        }
        manifest_base = manifest_path.parent
        repo_base = manifest_base.parent if manifest_base.name == "delivery" else manifest_base
        for index, item in enumerate(artifacts, start=1):
            if not isinstance(item, dict):
                add_failure(failures, f"manifest artifact #{index} must be an object")
                continue
            for key in ("path", "role", "version", "source_status", "sha256"):
                if not item.get(key):
                    add_failure(failures, f"manifest artifact #{index} missing {key}")
            status = str(item.get("source_status", "")).upper()
            if status and status not in allowed_status:
                add_failure(
                    failures,
                    f"manifest artifact #{index} has invalid source_status: {status}",
                )
            rel_path = str(item.get("path", ""))
            if rel_path and not (
                (repo_base / rel_path).exists() or (manifest_base / rel_path).exists()
            ):
                add_failure(
                    failures,
                    f"manifest artifact path does not exist: {rel_path}",
                )

    defined = set(data.get("defined_ids", []))
    referenced = set(data.get("referenced_ids", []))
    if defined or referenced:
        missing = sorted(referenced - defined)
        if missing:
            add_failure(failures, "broken ID references in machine-readable manifest: " + ", ".join(missing[:50]))

    actions = set(data.get("prototype_actions", []))
    mapped = set()
    for item in data.get("action_mappings", []):
        action = item.get("action") if isinstance(item, dict) else item
        if action:
            mapped.add(action)
    if actions:
        unmapped = sorted(actions - mapped)
        if unmapped:
            add_failure(failures, "action mapping gaps in machine-readable manifest: " + ", ".join(unmapped[:50]))

    for item in data.get("source_assertions", []):
        status = str(item.get("assertion_status", "")).upper()
        if status in {"UNKNOWN", "CONFLICT"} and item.get("core_behavior", False):
            source_id = item.get("source_id", "<unknown>")
            add_failure(failures, f"core source assertion blocks PASS: {source_id}={status}")


def check_language_ratio(
    text: str,
    failures: list[str],
    target_language: str,
    fail_ratio: float = 0.30,
) -> None:
    """Check language only when a target output language is declared.

    `zh` enforces that non-code narrative is not English-heavy. This supports
    Chinese delivery teams. English/global open-source examples should run with
    the default `none` and are not penalized for English content.
    """
    if target_language in {"none", "en"}:
        return

    lines = text.splitlines()
    total_weight = 0.0
    english_heavy_weight = 0.0
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Track code block state
        if FENCE_RE.match(line):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Skip empty lines
        if not stripped:
            continue

        # Skip table separator lines (|---|---|)
        if TABLE_HEADER_RE.match(line) and re.match(r"^[\s|\-:]+$", stripped):
            continue

        weight = 0.3 if TECH_IDENTIFIER_RE.search(stripped) else 1.0
        total_weight += weight

        # Count ASCII alpha characters
        ascii_chars = len(ASCII_ALPHA_RE.findall(stripped))
        alpha_total = sum(1 for ch in stripped if ch.isalpha())

        if alpha_total > 0 and ascii_chars / alpha_total >= 0.8:
            english_heavy_weight += weight

    if total_weight == 0:
        return

    ratio = english_heavy_weight / total_weight
    warn_ratio = min(0.20, max(0.01, fail_ratio * 0.67))
    if ratio > fail_ratio:
        add_failure(
            failures,
            f"LANGUAGE_GAP: English-heavy weighted lines "
            f"{english_heavy_weight:.1f}/{total_weight:.1f} "
            f"({ratio:.1%}) exceed {fail_ratio:.0%} threshold. Rewrite non-code content "
            f"in the user's spoken language per Output Language Rules."
        )
    elif ratio > warn_ratio:
        # Warning, not failure
        print(
            f"WARNING: English-heavy weighted lines "
            f"{english_heavy_weight:.1f}/{total_weight:.1f} "
            f"({ratio:.1%}) above {warn_ratio:.0%} recommendation"
        )


def check_heading_language(text: str, failures: list[str], target_language: str) -> None:
    """For Chinese delivery docs, require navigational headings to be Chinese."""
    if target_language != "zh":
        return

    bad: list[str] = []
    in_code_block = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        match = HEADING_DETAIL_RE.match(line)
        if not match:
            continue
        level = len(match.group(1))
        heading = match.group(2).strip()
        if level in {2, 3, 4} and len(CJK_RE.findall(heading)) < 2:
            bad.append(line.strip())

    if bad:
        add_failure(
            failures,
            "HEADING_LANGUAGE_GAP: H2/H3/H4 headings must be in Chinese when "
            "--target-language=zh. Offending headings: " + " | ".join(bad[:10]),
        )


def iter_markdown_lines_without_code(text: str) -> list[str]:
    lines: list[str] = []
    in_code_block = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        lines.append(line)
    return lines


def split_markdown_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|[\s|\-:]+\|\s*$", line))


def parse_tables(lines: list[str]) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in lines + [""]:
        row = split_markdown_table_row(line)
        if row:
            if not is_table_separator(line):
                current.append(row)
            continue
        if current:
            tables.append(current)
            current = []
    return tables


def col_index(headers: list[str], names: tuple[str, ...]) -> int | None:
    lowered = [header.lower() for header in headers]
    for idx, header in enumerate(lowered):
        if any(name.lower() in header for name in names):
            return idx
    return None


def extract_release_inventory_ids(text: str) -> set[str]:
    ids: set[str] = set()
    lines = iter_markdown_lines_without_code(text)
    for table in parse_tables(lines):
        if not table:
            continue
        headers = table[0]
        header_line = "|" + "|".join(headers) + "|"
        if not RFI_TABLE_HEADER_RE.search(header_line):
            continue
        id_col = col_index(headers, ("Function ID", "功能 ID", "功能ID"))
        scope_col = col_index(headers, ("Release Scope", "发布范围", "Scope", "范围"))
        if id_col is None:
            continue
        for row in table[1:]:
            if id_col >= len(row):
                continue
            frr_id_match = FRR_ID_RE.search(row[id_col])
            if not frr_id_match:
                continue
            scope = row[scope_col].lower() if scope_col is not None and scope_col < len(row) else "in"
            if any(term in scope for term in ("out", "defer", "later", "external", "not_applicable", "不做", "延期", "外部")):
                continue
            ids.add(frr_id_match.group(0))
    return ids


def section_content_too_thin(content: str) -> bool:
    stripped = re.sub(r"\s+", " ", content.strip())
    if not stripped:
        return True
    if PLACEHOLDER_RE.match(stripped):
        return True
    # Remove common table punctuation and technical IDs before measuring signal.
    signal = re.sub(r"[|:\-`#*_{}\[\]()/\\.,;，。；、\s]", "", stripped)
    if len(signal) < 18 and not REFERENCE_ANCHOR_RE.search(stripped):
        return True
    return False


def extract_frrs(text: str) -> list[dict[str, object]]:
    lines = iter_markdown_lines_without_code(text)
    frrs: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    section_no: int | None = None
    section_lines: list[str] = []

    def flush_section() -> None:
        nonlocal section_no, section_lines
        if current is not None and section_no is not None:
            sections = current.setdefault("sections", {})
            assert isinstance(sections, dict)
            sections[section_no] = "\n".join(section_lines).strip()
        section_no = None
        section_lines = []

    def flush_frr() -> None:
        nonlocal current
        if current is not None:
            flush_section()
            frrs.append(current)
        current = None

    for line in lines:
        heading_match = HEADING_DETAIL_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            frr_match = FRR_HEADING_RE.match(line)
            if frr_match:
                flush_frr()
                current = {"id": frr_match.group(2), "level": len(frr_match.group(1)), "sections": {}}
                continue
            if current is not None and level <= int(current["level"]):
                flush_frr()
                continue
            if current is not None:
                section_match = FRR_SECTION_RE.match(line)
                if section_match:
                    flush_section()
                    number = int(section_match.group(1))
                    if 1 <= number <= 16:
                        section_no = number
                        section_lines = []
                    continue
        if current is not None and section_no is not None:
            section_lines.append(line)

    flush_frr()
    return frrs


def check_frr_section_completeness(text: str, failures: list[str]) -> None:
    """Require every explicit FRR heading to contain sections 1-16."""
    frrs = extract_frrs(text)
    missing_messages = []
    required = set(range(1, 17))
    for frr in frrs:
        sections = frr["sections"]
        assert isinstance(sections, dict)
        missing = sorted(required - set(sections))
        if missing:
            missing_messages.append(f"{frr['id']} missing sections: {', '.join('§' + str(i) for i in missing)}")

    if missing_messages:
        add_failure(
            failures,
            "FRR_COMPLETENESS_GAP: every FRR must inline sections §1-§16. "
            + " | ".join(missing_messages[:20]),
        )


def check_frr_section_body_quality(text: str, failures: list[str]) -> None:
    """Reject FRRs whose required sections are present but placeholder-thin."""
    frrs = extract_frrs(text)
    bad: list[str] = []
    for frr in frrs:
        sections = frr["sections"]
        assert isinstance(sections, dict)
        for number in range(1, 17):
            content = str(sections.get(number, ""))
            if section_content_too_thin(content):
                bad.append(f"{frr['id']} §{number}")
    if bad:
        add_failure(
            failures,
            "FRR_SECTION_BODY_GAP: FRR sections must contain non-placeholder, "
            "implementation-useful content. Thin sections: " + ", ".join(bad[:50]),
        )


def check_frr_reference_coverage(text: str, failures: list[str]) -> None:
    """Require referenced release function IDs to exist as inline FRR headings."""
    if not FRR_COVERAGE_TRIGGER_RE.search(text):
        return

    lines = iter_markdown_lines_without_code(text)
    referenced_ids = set(FRR_ID_RE.findall("\n".join(lines)))
    if not referenced_ids:
        return

    heading_ids = {
        match.group(2)
        for match in (FRR_HEADING_RE.match(line) for line in lines)
        if match
    }
    missing = sorted(referenced_ids - heading_ids)
    if missing:
        add_failure(
            failures,
            "FRR_INVENTORY_COVERAGE_GAP: every referenced release function ID "
            "must have an inline FRR heading: " + ", ".join(missing[:30]),
        )


def requires_full_prd_contract(text: str) -> bool:
    """Return true when the artifact claims full PRD / full FRR delivery."""
    return bool(FRR_ID_RE.search(text) and FULL_PRD_TRIGGER_RE.search(text))


def extract_inline_frr_heading_ids(text: str) -> set[str]:
    lines = iter_markdown_lines_without_code(text)
    return {
        match.group(2)
        for match in (FRR_HEADING_RE.match(line) for line in lines)
        if match
    }


def parse_int_cell(value: str) -> int | None:
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def extract_completion_ledger_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = iter_markdown_lines_without_code(text)
    for table in parse_tables(lines):
        if not table:
            continue
        headers = table[0]
        header_line = "|" + "|".join(headers) + "|"
        if not LEDGER_TABLE_HEADER_RE.search(header_line):
            continue
        for raw_row in table[1:]:
            row: dict[str, str] = {}
            for index, header in enumerate(headers):
                row[header.strip()] = raw_row[index].strip() if index < len(raw_row) else ""
            rows.append(row)
    return rows


def check_rfi_and_ledger_presence(text: str, failures: list[str]) -> None:
    if not requires_full_prd_contract(text):
        return

    inventory_ids = extract_release_inventory_ids(text)
    ledger_rows = extract_completion_ledger_rows(text)
    missing: list[str] = []
    if not RELEASE_INVENTORY_RE.search(text) or not inventory_ids:
        missing.append("parseable Release Function Inventory table")
    if not COMPLETION_LEDGER_RE.search(text) or not ledger_rows:
        missing.append("parseable PRD Completion Ledger table")
    if missing:
        add_failure(
            failures,
            "RFI_LEDGER_GAP: full PRD delivery must include "
            + " and ".join(missing)
            + " before final handoff.",
        )


def check_rfi_denominator(text: str, failures: list[str]) -> None:
    inventory_ids = extract_release_inventory_ids(text)
    if not inventory_ids:
        return
    heading_ids = extract_inline_frr_heading_ids(text)
    missing = sorted(inventory_ids - heading_ids)
    if missing:
        add_failure(
            failures,
            "FRR_INVENTORY_COVERAGE_GAP: every in-scope Release Function "
            "Inventory item must have an inline FRR heading: "
            + ", ".join(missing[:30]),
        )


def ledger_row_identifier(row: dict[str, str]) -> str:
    for key, value in row.items():
        lowered = key.lower()
        if any(marker in lowered for marker in ("function id", "module", "function")) and value:
            return value
    return "<unknown>"


def row_value(row: dict[str, str], markers: tuple[str, ...]) -> str:
    for key, value in row.items():
        lowered = key.lower()
        if any(marker.lower() in lowered for marker in markers):
            return value
    return ""


def ledger_row_incomplete(row: dict[str, str]) -> bool:
    planned_text = row_value(row, ("Planned FRRs", "Planned"))
    completed_text = row_value(row, ("Completed FRRs", "Completed", "Complete Sections"))
    status_text = row_value(row, ("Status",))
    missing_text = row_value(row, ("Missing", "Blocking"))

    planned = parse_int_cell(planned_text)
    completed = parse_int_cell(completed_text)
    if planned is not None and completed is not None and planned > completed:
        return True

    combined = " ".join([completed_text, status_text, missing_text]).lower()
    if "§1-§16" in completed_text or "搂1-搂16" in completed_text:
        return False
    if status_text and not re.search(r"(?i)\b(complete|completed|pass|done)\b", status_text):
        return True
    if missing_text and not re.search(r"(?i)\b(none|n/a|na|0|-)\b", missing_text):
        return True
    if any(marker in combined for marker in ("missing", "blocked", "gap", "todo", "tbd")):
        return True
    return False


def check_completion_ledger_state(text: str, failures: list[str]) -> None:
    rows = extract_completion_ledger_rows(text)
    if not rows:
        return

    incomplete = [ledger_row_identifier(row) for row in rows if ledger_row_incomplete(row)]
    if not incomplete:
        return

    if FINAL_PASS_RE.search(text) or not CONTINUATION_REQUIRED_RE.search(text):
        add_failure(
            failures,
            "PRD_COMPLETION_LEDGER_GAP: ledger has incomplete planned work but "
            "the artifact does not stop with CONTINUATION_REQUIRED, BLOCKED, or "
            "REVIEW_COMPLETE_WITH_GAPS. Incomplete rows: "
            + ", ".join(incomplete[:30]),
        )


def check_ai_coding_part1_inline(text: str, failures: list[str]) -> None:
    """Fail AI-Coding PRDs whose Part 1 is only an index or external pointer."""
    part1_match = PART1_RE.search(text)
    part2_match = PART2_RE.search(text)
    if not part1_match or not part2_match or part2_match.start() <= part1_match.end():
        return

    part1 = text[part1_match.end():part2_match.start()]
    function_ids = set(FRR_ID_RE.findall(part1))
    frr_heading_ids = set(
        match.group(2)
        for match in (FRR_HEADING_RE.match(line) for line in iter_markdown_lines_without_code(part1))
        if match
    )

    if function_ids and len(frr_heading_ids) < len(function_ids):
        add_failure(
            failures,
            "FRR_INLINE_GAP: AI-Coding Part 1 references function IDs that are "
            "not present as inline FRR headings: "
            + ", ".join(sorted(function_ids - frr_heading_ids)[:20]),
        )
    if function_ids and FRR_INDEX_SUBSTITUTE_RE.search(part1) and len(frr_heading_ids) < len(function_ids):
        add_failure(
            failures,
            "FRR_INLINE_GAP: AI-Coding Part 1 appears to use an index/reference "
            "instead of inline FRR bodies.",
        )


def is_structured_repetition_table(paragraph: str) -> bool:
    """Return true for structured tables where repeated cells are intentional.

    Operation matrices often use "same as above" or "同上" inside table cells to
    avoid repeating role/status text. That is not a lazy implementation
    reference because the table header itself supplies the missing dimension.
    Layout region tables use the same shorthand for visible roles or data source.
    """

    for line in paragraph.splitlines()[:5]:
        if FRR_OPERATION_TABLE_RE.search(line) or LAYOUT_REGION_TABLE_RE.search(line):
            return True
    return False


def check_lazy_references(text: str, failures: list[str]) -> None:
    """Fail bare references that replace implementation detail.

    Phrases such as "see prototype" are allowed only when the same paragraph
    gives a traceable locator (FRR/source/testid/action/view/region). Otherwise
    human developers and coding agents cannot reconstruct page behavior.
    """

    paragraphs = re.split(r"\n\s*\n", text)
    bad: list[str] = []
    for para in paragraphs:
        if is_structured_repetition_table(para):
            continue
        if LAZY_REFERENCE_RE.search(para) and not REFERENCE_ANCHOR_RE.search(para):
            bad.append(re.sub(r"\s+", " ", para.strip())[:180])
    if bad:
        add_failure(
            failures,
            "lazy implementation references without locator/detail: "
            + " | ".join(bad[:10]),
        )


def check_heading_hierarchy(text: str, failures: list[str]) -> None:
    """Fail heading structures that break PRD/document navigation."""

    headings: list[tuple[int, str]] = []
    in_code_block = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        match = HEADING_RE.match(line)
        if match:
            headings.append((len(match.group(1)), line.strip()))

    if not headings:
        return

    h1_count = sum(1 for level, _ in headings if level == 1)
    if h1_count != 1:
        add_failure(failures, f"HEADING_GAP: expected exactly one H1, found {h1_count}")

    previous_level = headings[0][0]
    if previous_level != 1:
        add_failure(failures, f"HEADING_GAP: first heading must be H1, found {headings[0][1]}")

    for level, heading in headings[1:]:
        if level > previous_level + 1:
            add_failure(
                failures,
                f"HEADING_GAP: heading jumps from H{previous_level} to H{level}: {heading}",
            )
            break
        previous_level = level


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path, help="PRD/prototype/spec artifact to inspect")
    parser.add_argument("--manifest", type=Path, help="Optional machine-readable manifest for strict graph checks")
    parser.add_argument("--allow-wildcards", action="store_true", help="Allow wildcard IDs in templates/examples")
    parser.add_argument("--warn-numeric", action="store_true", help="Check unsupported numeric-claim candidates")
    parser.add_argument(
        "--target-language",
        choices=("none", "zh", "en"),
        default="none",
        help="Optional narrative language enforcement. Use zh for Chinese delivery docs.",
    )
    parser.add_argument(
        "--language-threshold",
        dest="legacy_language_threshold",
        help=(
            "Deprecated compatibility alias. Accepts zh/en/none as an alias for "
            "--target-language, or a numeric fail ratio such as 0.30."
        ),
    )
    parser.add_argument(
        "--language-fail-ratio",
        type=float,
        default=0.30,
        help="Fail threshold for English-heavy weighted lines when --target-language=zh.",
    )
    args = parser.parse_args()

    failures: list[str] = []
    text = read_text(args.artifact)
    target_language = args.target_language
    language_fail_ratio = args.language_fail_ratio

    if args.legacy_language_threshold:
        legacy = args.legacy_language_threshold.strip().lower()
        aliases = {
            "zh": "zh",
            "cn": "zh",
            "chinese": "zh",
            "en": "en",
            "english": "en",
            "none": "none",
            "off": "none",
            "false": "none",
        }
        if legacy in aliases:
            target_language = aliases[legacy]
        else:
            try:
                language_fail_ratio = float(legacy)
            except ValueError:
                parser.error("--language-threshold expects zh/en/none or a numeric ratio")
    if not 0 < language_fail_ratio <= 1:
        parser.error("--language-fail-ratio must be between 0 and 1")

    if not args.allow_wildcards:
        check_wildcard_ids(text, failures)
    check_duplicate_boilerplate(text, failures)
    check_heading_hierarchy(text, failures)
    check_lazy_references(text, failures)
    check_language_ratio(text, failures, target_language, language_fail_ratio)
    check_heading_language(text, failures, target_language)
    check_rfi_and_ledger_presence(text, failures)
    check_frr_reference_coverage(text, failures)
    check_rfi_denominator(text, failures)
    check_frr_section_completeness(text, failures)
    check_frr_section_body_quality(text, failures)
    check_completion_ledger_state(text, failures)
    check_ai_coding_part1_inline(text, failures)
    if args.warn_numeric:
        check_unsupported_numeric_claims(text, failures)
    if args.manifest:
        check_manifest(args.manifest, failures)

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: PRD quality deterministic checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
