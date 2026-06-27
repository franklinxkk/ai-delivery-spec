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
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".docx":
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        texts = [node.text or "" for node in root.findall(".//w:t", ns)]
        return "\n".join(texts)
    return path.read_text(encoding="utf-8", errors="ignore")


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
