#!/usr/bin/env python3
"""Extract a first-pass interaction ledger from a local HTML prototype.

This helper is intentionally conservative. It reads static HTML/JS and reports
views, data-actions, onclick handlers, testids, data-fields, modal-like nodes,
and function names. Dynamic behavior still requires browser verification.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def unique(items):
    seen = set()
    out = []
    for item in items:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, dict) else item
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def attr_values(html: str, attr: str):
    pattern = re.compile(rf"""{attr}\s*=\s*["']([^"']+)["']""", re.I)
    return pattern.findall(html)


def extract_attrs(html: str, attrs):
    tag_pattern = re.compile(r"<([a-zA-Z][\w:-]*)([^>]*)>", re.S)
    rows = []
    for tag, raw_attrs in tag_pattern.findall(html):
        row = {"tag": tag.lower()}
        matched = False
        for attr in attrs:
            m = re.search(rf"""{attr}\s*=\s*["']([^"']+)["']""", raw_attrs, re.I)
            if m:
                row[attr] = m.group(1)
                matched = True
        if matched:
            rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="HTML file path")
    parser.add_argument("--output", required=True, help="JSON output path")
    args = parser.parse_args()

    html_path = Path(args.input)
    html = html_path.read_text(encoding="utf-8", errors="replace")

    data_rows = extract_attrs(
        html,
        [
            "id",
            "class",
            "data-testid",
            "data-action",
            "data-state",
            "data-view",
            "data-visible-role",
            "data-api",
            "data-method",
            "data-field",
            "data-bind",
            "onclick",
        ],
    )

    onclicks = attr_values(html, "onclick")
    data_actions = attr_values(html, "data-action")
    data_testids = attr_values(html, "data-testid")
    data_fields = attr_values(html, "data-field")
    data_binds = attr_values(html, "data-bind")
    ids = attr_values(html, "id")

    functions = re.findall(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(", html)
    arrow_assignments = re.findall(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", html)

    view_candidates = []
    for row in data_rows:
        classes = row.get("class", "")
        if row.get("data-view") or row.get("data-testid", "").startswith("page-") or "section" in classes:
            view_candidates.append(row)

    modal_candidates = []
    for row in data_rows:
        text = " ".join(str(v) for v in row.values()).lower()
        if "modal" in text or "drawer" in text or "dialog" in text or "sheet" in text:
            modal_candidates.append(row)

    ledger = {
        "artifact": str(html_path),
        "annotationPattern": {
            "hasDataActions": bool(data_actions),
            "hasDataTestids": bool(data_testids),
            "hasInlineOnclick": bool(onclicks),
        },
        "counts": {
            "dataActions": len(data_actions),
            "uniqueDataActions": len(set(data_actions)),
            "dataTestids": len(data_testids),
            "dataFields": len(data_fields),
            "uniqueDataFields": len(set(data_fields)),
            "dataBinds": len(data_binds),
            "onclicks": len(onclicks),
            "ids": len(ids),
            "functions": len(set(functions + arrow_assignments)),
        },
        "views": unique(view_candidates),
        "actions": unique(
            [{"type": "data-action", "name": a} for a in data_actions]
            + [{"type": "onclick", "name": o} for o in onclicks]
        ),
        "testids": sorted(set(data_testids)),
        "fields": sorted(set(data_fields)),
        "binds": sorted(set(data_binds)),
        "modalsOrDrawers": unique(modal_candidates),
        "functions": sorted(set(functions + arrow_assignments)),
        "notes": [
            "Static ledger only; verify dynamic routes and handlers in browser.",
            "Inline onclick prototypes should be upgraded with data-action/data-testid before L2 handoff.",
        ],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
