#!/usr/bin/env python3
"""Extract a first-pass interaction ledger from a local HTML prototype.

This helper is intentionally conservative. It reads static HTML/JS and reports
views, data-actions, handler registries, testids, fields, metrics, acceptance
anchors, modal-like nodes, and statically unreachable surfaces. Dynamic behavior
still requires browser verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
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
            if attr == "hidden":
                m = re.search(r"(?:^|\s)hidden(?:\s|=|$)", raw_attrs, re.I)
                if m:
                    row[attr] = True
                    matched = True
                continue
            m = re.search(rf"""{attr}\s*=\s*["']([^"']+)["']""", raw_attrs, re.I)
            if m:
                row[attr] = m.group(1)
                matched = True
        if matched:
            rows.append(row)
    return rows


def extract_handler_actions(source: str) -> list[str]:
    """Return stable action IDs declared by common static dispatch patterns."""
    patterns = (
        r"\bcase\s*[\"']((?:ACT|UIACT)-[A-Z0-9-]+)[\"']",
        r"\.set\s*\(\s*[\"']((?:ACT|UIACT)-[A-Z0-9-]+)[\"']",
        r"(?:action|actionId)\s*={2,3}\s*[\"']((?:ACT|UIACT)-[A-Z0-9-]+)[\"']",
        r"\[\s*[\"']((?:ACT|UIACT)-[A-Z0-9-]+)[\"']\s*\]\s*=",
    )
    found: set[str] = set()
    for pattern in patterns:
        found.update(item.upper() for item in re.findall(pattern, source, re.I))
    registry_blocks: list[str] = []
    registry_start = re.compile(
        r"^([ \t]*)(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*\{[ \t]*(?:\r?\n|$)",
        re.I | re.M,
    )
    for match in registry_start.finditer(source):
        if not re.search(r"action|handler|registry|dispatch", match.group(2), re.I):
            continue
        closing = re.search(rf"^{re.escape(match.group(1))}\}}\s*;", source[match.end():], re.M)
        if closing:
            registry_blocks.append(source[match.end():match.end() + closing.start()])
    if not registry_blocks:
        registry_blocks = re.findall(
            r"(?:action|handler|registry|dispatch)[\w$]*\s*=\s*\{(.*?)\}\s*;",
            source,
            re.I | re.S,
        )
    for block in registry_blocks:
        found.update(
            item.upper()
            for item in re.findall(r"[\"']((?:ACT|UIACT)-[A-Z0-9-]+)[\"']\s*:", block, re.I)
        )
    return sorted(found)


def extract_dynamic_anchor_actions(source: str) -> list[str]:
    """Return literal action IDs passed through a statically visible UI factory."""
    split_name = r"(?:data-action|data-\s*[\"']\s*\+\s*[\"']action|[\"']data-[\"']\s*\+\s*[\"']action)"
    act_factory = re.search(
        rf"(?:\bfunction\s+act\s*\([^)]*\)\s*\{{|\b(?:const|let|var)\s+act\s*=)[\s\S]{{0,800}}?{split_name}",
        source,
        re.I,
    )
    if not act_factory:
        return []
    found = {
        item.upper()
        for item in re.findall(r"\bact\s*\(\s*[\"']((?:ACT|UIACT)-[A-Z0-9-]+)[\"']", source, re.I)
    }
    if re.search(r"\bact\s*\(\s*options\.confirmAction", source, re.I):
        for fragment in re.findall(r"\bconfirmAction\s*:\s*([^,}\n]+)", source, re.I):
            found.update(item.upper() for item in re.findall(r"\b(?:ACT|UIACT)-[A-Z0-9-]+\b", fragment, re.I))
    add_factory = re.search(
        r"\b(?:const|let|var)\s+add\s*=\s*[\s\S]{0,600}?insertAdjacentHTML[\s\S]{0,300}?\bact\s*\(",
        source,
        re.I,
    )
    if add_factory:
        found.update(
            item.upper()
            for item in re.findall(
                r"\badd\s*\(\s*(?:'[^']*'|\"[^\"]*\")\s*,\s*[\"']((?:ACT|UIACT)-[A-Z0-9-]+)[\"']",
                source,
                re.I,
            )
        )
    return sorted(found)


def reachability_inventory(rows: list[dict], source: str) -> list[dict]:
    """Flag explicitly hidden page/modal/drawer roots with no static route target."""
    target_values = {
        value.casefold()
        for row in rows
        for key in ("data-view", "data-target")
        if (value := row.get(key))
    }
    for pattern in (
        r"(?:showPage|showView|navigate|openSurface|openModal|openDrawer)\s*\(\s*[\"']([^\"']+)[\"']",
        r"(?:targetView|viewId|pageId|modalId|drawerId)\s*[:=]\s*[\"']([^\"']+)[\"']",
    ):
        target_values.update(item.casefold() for item in re.findall(pattern, source, re.I))
    for variable, target in re.findall(
        r"\bconst\s+([A-Za-z_$][\w$]*)\s*=\s*\$\(\s*[\"']#([^\"']+)[\"']\s*\)"
        r"[\s\S]{0,600}?\b\1\.hidden\s*=\s*(?:false|!\s*\1\.hidden)",
        source,
        re.I,
    ):
        target_values.add(target.casefold())
    target_values.update(
        item.casefold()
        for item in re.findall(
            r"\$\(\s*[\"']#([^\"']+)[\"']\s*\)\.hidden\s*=\s*false",
            source,
            re.I,
        )
    )
    target_values.update(item.lstrip("#.") for item in list(target_values))

    surfaces: list[dict] = []
    for row in rows:
        testid = str(row.get("data-testid", ""))
        classes = str(row.get("class", ""))
        class_tokens = {item.casefold() for item in re.split(r"\s+", classes) if item}
        is_surface = (
            testid.casefold().startswith(("page-", "modal-", "drawer-"))
            or bool(class_tokens & {"page", "modal", "drawer", "dialog", "sheet"})
        )
        if not is_surface:
            continue
        keys = {
            str(row.get(key, "")).casefold()
            for key in ("id", "data-testid", "data-view")
            if row.get(key)
        }
        aliases = set(keys)
        for key in list(keys):
            aliases.update({
                re.sub(r"^(?:page|modal|drawer)-", "", key),
                key.replace("view-", ""),
                re.sub(r"^(?:(?:page|modal|drawer|view)-)+", "", key),
            })
        explicitly_hidden = bool(row.get("hidden")) or "hidden" in class_tokens
        initially_visible = bool(class_tokens & {"active", "open", "show", "visible", "is-visible"})
        referenced = bool(aliases & target_values)
        surfaces.append({
            "surface": testid or row.get("id") or row.get("data-view") or "<anonymous>",
            "explicitlyHidden": explicitly_hidden,
            "initiallyVisible": initially_visible,
            "staticallyReferenced": referenced,
            "unreachable": explicitly_hidden and not initially_visible and not referenced,
        })
    return surfaces


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="HTML file path")
    parser.add_argument("--output", required=True, help="JSON output path, or - for stdout")
    args = parser.parse_args()

    html_path = Path(args.input)
    if not html_path.is_file():
        print(f"FAIL: input HTML file not found: {html_path}", file=sys.stderr)
        return 2
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
            "data-target",
            "data-visible-role",
            "data-api",
            "data-method",
            "data-field",
            "data-bind",
            "data-metric",
            "data-ac",
            "hidden",
            "onclick",
        ],
    )

    onclicks = attr_values(html, "onclick")
    data_actions = [item for item in attr_values(html, "data-action") if not re.search(r"\$\{|\{\{|<%", item)]
    data_testids = attr_values(html, "data-testid")
    data_states = attr_values(html, "data-state")
    data_fields = attr_values(html, "data-field")
    data_binds = attr_values(html, "data-bind")
    data_metrics = attr_values(html, "data-metric")
    data_acceptance = attr_values(html, "data-ac")
    ids = attr_values(html, "id")

    functions = re.findall(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(", html)
    arrow_assignments = re.findall(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", html)
    handler_actions = extract_handler_actions(html)
    dynamic_anchor_actions = extract_dynamic_anchor_actions(html)
    dom_actions = {item.upper() for item in data_actions} | set(dynamic_anchor_actions)
    orphan_handler_actions = sorted(set(handler_actions) - dom_actions)
    reachability = reachability_inventory(data_rows, html)

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

    state_snapshot = {
        "dataStates": sorted(set(data_states)),
        "dataActions": sorted(set(data_actions)),
        "dataTestids": sorted(set(data_testids)),
    }
    state_snapshot["stateChecksum"] = hashlib.sha256(
        json.dumps(state_snapshot, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    ledger = {
        "artifact": str(html_path),
        "schemaVersion": "interaction-ledger/v2",
        "annotationPattern": {
            "hasDataActions": bool(data_actions),
            "hasDataTestids": bool(data_testids),
            "hasInlineOnclick": bool(onclicks),
        },
        "counts": {
            "dataActions": len(data_actions),
            "uniqueDataActions": len(set(data_actions)),
            "dataTestids": len(data_testids),
            "dataStates": len(data_states),
            "uniqueDataStates": len(set(data_states)),
            "dataFields": len(data_fields),
            "uniqueDataFields": len(set(data_fields)),
            "dataBinds": len(data_binds),
            "dataMetrics": len(data_metrics),
            "uniqueDataMetrics": len(set(data_metrics)),
            "acceptanceRefs": len(set(data_acceptance)),
            "handlerActions": len(handler_actions),
            "dynamicAnchorActions": len(dynamic_anchor_actions),
            "orphanHandlerActions": len(orphan_handler_actions),
            "unreachableSurfaces": sum(item["unreachable"] for item in reachability),
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
        "states": sorted(set(data_states)),
        "stateSnapshot": state_snapshot,
        "fields": sorted(set(data_fields)),
        "binds": sorted(set(data_binds)),
        "metrics": sorted(set(data_metrics)),
        "acceptanceRefs": sorted(set(data_acceptance)),
        "handlerActions": handler_actions,
        "dynamicAnchorActions": dynamic_anchor_actions,
        "orphanHandlerActions": orphan_handler_actions,
        "reachability": reachability,
        "modalsOrDrawers": unique(modal_candidates),
        "functions": sorted(set(functions + arrow_assignments)),
        "notes": [
            "Static ledger only; verify dynamic routes and handlers in browser.",
            "orphanHandlerActions are registry entries with no source-template data-action; remove, restore the control, or document an approved deletion.",
            "reachability only blocks explicitly hidden roots with no static target; dynamic routing still needs browser evidence.",
            "stateSnapshot.stateChecksum protects high-value state/action/testid boundaries from lossy summarization.",
            "Inline onclick prototypes should be upgraded with data-action/data-testid before L2 handoff.",
        ],
    }

    rendered = json.dumps(ledger, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(rendered)
    else:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
