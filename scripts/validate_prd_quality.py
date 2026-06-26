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
FENCE_RE = re.compile(r"^```")
TABLE_HEADER_RE = re.compile(r"^\s*\|")
LAZY_REFERENCE_RE = re.compile(
    r"(见原型|见附件|按现有逻辑|同上|参考原型|see prototype|same as above|existing logic|see attachment)",
    re.IGNORECASE,
)
REFERENCE_ANCHOR_RE = re.compile(
    r"(data-testid|data-action|FRR|AC-|SRC-|Source ID|view_id|region_id|modal-|drawer-|prototype lock|prototype path)",
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
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

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


def check_language_ratio(text: str, failures: list[str], target_language: str) -> None:
    """Check language only when a target output language is declared.

    `zh` enforces that non-code narrative is not English-heavy. This supports
    Chinese delivery teams. English/global open-source examples should run with
    the default `none` and are not penalized for English content.
    """
    if target_language in {"none", "en"}:
        return

    lines = text.splitlines()
    total = 0
    english_heavy = 0
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

        total += 1

        # Count ASCII alpha characters
        ascii_chars = len(ASCII_ALPHA_RE.findall(stripped))
        alpha_total = sum(1 for ch in stripped if ch.isalpha())

        if alpha_total > 0 and ascii_chars / alpha_total >= 0.8:
            english_heavy += 1

    if total == 0:
        return

    ratio = english_heavy / total
    if ratio > 0.30:
        add_failure(
            failures,
            f"LANGUAGE_GAP: English-heavy lines {english_heavy}/{total} "
            f"({ratio:.1%}) exceed 30% threshold. Rewrite non-code content "
            f"in the user's spoken language per Output Language Rules."
        )
    elif ratio > 0.20:
        # Warning, not failure
        print(
            f"WARNING: English-heavy lines {english_heavy}/{total} "
            f"({ratio:.1%}) above 20% recommendation"
        )


def check_lazy_references(text: str, failures: list[str]) -> None:
    """Fail bare references that replace implementation detail.

    Phrases such as "see prototype" are allowed only when the same paragraph
    gives a traceable locator (FRR/source/testid/action/view/region). Otherwise
    human developers and coding agents cannot reconstruct page behavior.
    """

    paragraphs = re.split(r"\n\s*\n", text)
    bad: list[str] = []
    for para in paragraphs:
        if LAZY_REFERENCE_RE.search(para) and not REFERENCE_ANCHOR_RE.search(para):
            bad.append(re.sub(r"\s+", " ", para.strip())[:180])
    if bad:
        add_failure(
            failures,
            "lazy implementation references without locator/detail: "
            + " | ".join(bad[:10]),
        )


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
    args = parser.parse_args()

    failures: list[str] = []
    text = read_text(args.artifact)

    if not args.allow_wildcards:
        check_wildcard_ids(text, failures)
    check_duplicate_boilerplate(text, failures)
    check_lazy_references(text, failures)
    check_language_ratio(text, failures, args.target_language)
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
