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


def _mask_javascript_literals(source: str) -> str:
    """Mask strings/comments while preserving offsets and executable braces."""
    masked = list(source)
    index = 0
    while index < len(source):
        char = source[index]
        if char in {"'", '"', "`"}:
            quote = char
            masked[index] = " "
            index += 1
            while index < len(source):
                current = source[index]
                if current == "\\":
                    masked[index] = " "
                    if index + 1 < len(source):
                        masked[index + 1] = " "
                    index += 2
                    continue
                if current == quote:
                    masked[index] = " "
                    index += 1
                    break
                if current not in "\r\n":
                    masked[index] = " "
                index += 1
            continue
        if source.startswith("//", index):
            masked[index:index + 2] = [" ", " "]
            index += 2
            while index < len(source) and source[index] not in "\r\n":
                masked[index] = " "
                index += 1
            continue
        if source.startswith("/*", index):
            masked[index:index + 2] = [" ", " "]
            index += 2
            while index < len(source):
                if source.startswith("*/", index):
                    masked[index:index + 2] = [" ", " "]
                    index += 2
                    break
                if source[index] not in "\r\n":
                    masked[index] = " "
                index += 1
            continue
        index += 1
    return "".join(masked)


def _javascript_brace_pairs(masked: str) -> dict[int, int]:
    """Return balanced JavaScript brace pairs for conservative scope checks."""
    stack: list[int] = []
    brace_pairs: dict[int, int] = {}
    for index, char in enumerate(masked):
        if char == "{":
            stack.append(index)
        elif char == "}" and stack:
            brace_pairs[stack.pop()] = index
    return brace_pairs


def _javascript_function_scopes(source: str) -> list[tuple[int, int]]:
    """Return conservative function/method/brace-arrow body spans."""
    masked = _mask_javascript_literals(source)
    brace_pairs = _javascript_brace_pairs(masked)

    openings: set[int] = set()
    patterns = (
        re.compile(r"\bfunction\b(?:\s+[A-Za-z_$][\w$]*)?\s*\([^(){}]*\)\s*\{", re.I),
        re.compile(r"(?:\([^(){};]*\)|\b[A-Za-z_$][\w$]*)\s*=>\s*\{", re.I),
    )
    for pattern in patterns:
        for match in pattern.finditer(masked):
            opening = masked.rfind("{", match.start(), match.end())
            if opening >= 0:
                openings.add(opening)

    # Cover class/object shorthand methods without treating control blocks as
    # functions.  Duplicate openings from ordinary function declarations are
    # harmless because this collection is a set.
    method_pattern = re.compile(r"\b([A-Za-z_$][\w$]*)\s*\([^(){}]*\)\s*\{", re.I)
    control_words = {"if", "for", "while", "switch", "catch", "with", "function"}
    for match in method_pattern.finditer(masked):
        if match.group(1).casefold() in control_words:
            continue
        opening = masked.rfind("{", match.start(), match.end())
        if opening >= 0:
            openings.add(opening)

    return sorted(
        (opening + 1, brace_pairs[opening])
        for opening in openings
        if opening in brace_pairs
    )


def _enclosing_function_scope(
    scopes: list[tuple[int, int]], position: int, source_length: int,
) -> tuple[int, int]:
    matches = [scope for scope in scopes if scope[0] <= position < scope[1]]
    return max(matches, key=lambda scope: scope[0]) if matches else (0, source_length)


def _has_unbraced_arrow_parameter_shadow(
    source: str, target: str, start: int, offset: int,
) -> bool:
    """Conservatively catch expression-arrow parameters that shadow target."""
    masked = _mask_javascript_literals(source)
    arrow = re.compile(
        r"(?P<params>\([^(){};]*\)|\b[A-Za-z_$][\w$]*)\s*=>\s*(?!\{)",
        re.I,
    )
    for match in arrow.finditer(masked, start, offset):
        identifiers = re.findall(r"[A-Za-z_$][\w$]*", match.group("params"))
        if target not in identifiers:
            continue
        # Without a complete JS parser, only accept that the expression still
        # contains the action when no explicit statement terminator intervenes.
        # False uncertainty remains unsafe, which is the intended narrow policy.
        if ";" not in masked[match.end():offset]:
            return True
    return False


def _has_catch_parameter_shadow(source: str, target: str, offset: int) -> bool:
    """Return true when ``target`` is a catch parameter at the action write."""
    masked = _mask_javascript_literals(source)
    brace_pairs = _javascript_brace_pairs(masked)
    catch_pattern = re.compile(r"\bcatch\s*\((?P<params>[^(){}]*)\)\s*\{", re.I)
    for match in catch_pattern.finditer(masked, 0, offset):
        opening = masked.rfind("{", match.start(), match.end())
        closing = brace_pairs.get(opening)
        if opening < offset < (closing if closing is not None else -1):
            if target in re.findall(r"[A-Za-z_$][\w$]*", match.group("params")):
                return True
    return False


def _lexical_scope_at(source: str, position: int) -> tuple[int, int]:
    """Return the innermost balanced brace scope containing ``position``."""
    masked = _mask_javascript_literals(source)
    scopes = [
        (opening + 1, closing)
        for opening, closing in _javascript_brace_pairs(masked).items()
        if opening < position < closing
    ]
    return max(scopes, key=lambda scope: scope[0]) if scopes else (0, len(source))


def _inside_for_header(source: str, position: int) -> bool:
    """Conservatively reject let/const bindings whose scope is a for header."""
    masked = _mask_javascript_literals(source)
    for match in re.finditer(r"\bfor\s*\(", masked[:position], re.I):
        opening = masked.find("(", match.start(), match.end())
        depth = 0
        for index in range(opening, len(masked)):
            if masked[index] == "(":
                depth += 1
            elif masked[index] == ")":
                depth -= 1
                if depth == 0:
                    if opening < position < index:
                        return True
                    break
    return False


def _is_fresh_dynamic_element(source: str, target: str, offset: int) -> bool:
    """Return whether the latest same-scope write creates ``target`` as a node.

    The exemption stays deliberately narrow: the creation and data-action
    assignment must share one statically visible function/top-level scope, and
    no later same-scope declaration or reassignment may replace the node.  This
    prevents a createElement in one function from proving a same-named parameter
    or local in another function safe.
    """
    scopes = _javascript_function_scopes(source)
    current_scope = _enclosing_function_scope(scopes, offset, len(source))
    window_start = max(current_scope[0], offset - 4000)
    if (
        _has_unbraced_arrow_parameter_shadow(source, target, window_start, offset)
        or _has_catch_parameter_shadow(source, target, offset)
    ):
        return False
    # Preserve offsets while blanking comments and literals. Regex-based write
    # discovery must never treat examples or prose as executable reassignment.
    prefix = _mask_javascript_literals(source)[window_start:offset]
    target_pattern = re.escape(target)
    events: list[tuple[int, str | None]] = []

    assignments = re.compile(
        rf"(?<![\w$.])(?:(?P<kind>const|let|var)\s+)?{target_pattern}\b\s*="
        rf"(?!=|>)\s*([^;\r\n]+)",
    )
    for match in assignments.finditer(prefix):
        absolute = window_start + match.start()
        if _enclosing_function_scope(scopes, absolute, len(source)) != current_scope:
            continue
        kind = (match.group("kind") or "").casefold()
        declaration_scope = _lexical_scope_at(source, absolute)
        # let/const are visible only while their declaring block contains the
        # action write. Plain assignments are kept equally narrow; var remains
        # function-scoped. This rejects borrowing a node from a finished block.
        if kind in {"const", "let"} and _inside_for_header(source, absolute):
            continue
        if kind != "var" and not (declaration_scope[0] <= offset < declaration_scope[1]):
            continue
        events.append((absolute, match.group(2).strip()))

    # A later declaration without an initializer shadows/replaces an earlier
    # provable creation.  Treat it as an unsafe write instead of borrowing the
    # previous createElement assignment.
    declarations = re.compile(
        rf"\b(?P<kind>const|let|var)\s+{target_pattern}\b(?!\s*=(?!=|>))",
    )
    for match in declarations.finditer(prefix):
        absolute = window_start + match.start()
        if _enclosing_function_scope(scopes, absolute, len(source)) != current_scope:
            continue
        kind = match.group("kind").casefold()
        declaration_scope = _lexical_scope_at(source, absolute)
        if kind != "var" and not (declaration_scope[0] <= offset < declaration_scope[1]):
            continue
        events.append((absolute, None))

    # Compound/logical writes and explicit destructuring can replace the node
    # without using a plain ``target =`` form. Any later same-function match is
    # conservatively invalidating; property writes such as target.title remain
    # allowed because the receiver itself is unchanged.
    replacing_writes = (
        re.compile(
            rf"(?<![\w$.])(?:{target_pattern}\s*(?:&&=|\|\|=|\?\?=|\*\*=|<<=|>>>=|>>=|[+\-*/%&|^]=|\+\+|--)|"
            rf"(?:\+\+|--)\s*{target_pattern}\b)",
        ),
        re.compile(rf"\[[^\]\r\n]*\b{target_pattern}\b[^\]\r\n]*\]\s*=(?!=|>)"),
        re.compile(rf"\{{[^{{}}\r\n]*\b{target_pattern}\b[^{{}}\r\n]*\}}\s*=(?!=|>)"),
        re.compile(rf"\bfor\s*\(\s*{target_pattern}\s+(?:of|in)\b", re.I),
    )
    for pattern in replacing_writes:
        for match in pattern.finditer(prefix):
            absolute = window_start + match.start()
            if _enclosing_function_scope(scopes, absolute, len(source)) == current_scope:
                events.append((absolute, None))

    if not events:
        return False
    _position, initializer = max(events, key=lambda item: item[0])
    return bool(
        initializer
        and re.match(r"document\s*\.\s*createElement(?:NS)?\s*\(", initializer, re.I)
    )


def inspect_runtime_action_assignments(source: str) -> tuple[list[str], list[str]]:
    """Split script-side data-action assignments into safe literals and risks.

    A literal stable action ID attached to a freshly-created element is a
    statically enumerable dynamic anchor.  A variable, concatenated value, or
    assignment to an existing/unknown node remains an unsafe runtime retrofit.
    The second return value contains compact source snippets for gate evidence.
    """
    action_id = r"(?:ACT|UIACT)-[A-Z0-9-]+"
    literal = re.compile(rf"^\s*(['\"`])({action_id})\1\s*$", re.I)
    patterns = (
        re.compile(
            r"(?<![\w$.])(?P<target>[A-Za-z_$][\w$]*)\s*\.\s*setAttribute\s*\(\s*"
            r"['\"]data-action['\"]\s*,\s*(?P<value>[^)\r\n]+?)\s*\)",
            re.I,
        ),
        re.compile(
            r"(?<![\w$.])(?P<target>[A-Za-z_$][\w$]*)\s*\.\s*dataset\s*\.\s*action\s*="
            r"(?!=)\s*(?P<value>[^;\r\n}]+)",
            re.I,
        ),
    )
    safe: set[str] = set()
    unsafe: list[str] = []
    consumed: list[tuple[int, int]] = []
    for pattern in patterns:
        for match in pattern.finditer(source):
            consumed.append(match.span())
            value_match = literal.fullmatch(match.group("value"))
            if value_match and _is_fresh_dynamic_element(source, match.group("target"), match.start()):
                safe.add(value_match.group(2).upper())
            else:
                unsafe.append(re.sub(r"\s+", " ", match.group(0)).strip()[:160])

    # Preserve the old conservative behavior for complex receivers that the
    # simple-identifier parser cannot classify (for example query(...).dataset).
    generic = re.compile(
        r"(?:setAttribute\s*\(\s*['\"]data-action['\"]\s*,|"
        r"dataset\s*\.\s*action\s*=(?!=))",
        re.I,
    )
    for match in generic.finditer(source):
        if any(start <= match.start() < end for start, end in consumed):
            continue
        unsafe.append(re.sub(r"\s+", " ", source[match.start():match.start() + 160]).strip())
    return sorted(safe), unique(unsafe)


def extract_dynamic_anchor_actions(source: str) -> list[str]:
    """Return literal action IDs passed through statically visible UI factories."""
    split_name = r"(?:data-action|data-\s*[\"']\s*\+\s*[\"']action|[\"']data-[\"']\s*\+\s*[\"']action)"
    act_factory = re.search(
        rf"(?:\bfunction\s+act\s*\([^)]*\)\s*\{{|\b(?:const|let|var)\s+act\s*=)[\s\S]{{0,800}}?{split_name}",
        source,
        re.I,
    )
    literal_assignments, _unsafe_assignments = inspect_runtime_action_assignments(source)
    found = set(literal_assignments)
    if not act_factory:
        return sorted(found)
    found.update({
        item.upper()
        for item in re.findall(r"\bact\s*\(\s*[\"']((?:ACT|UIACT)-[A-Z0-9-]+)[\"']", source, re.I)
    })
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
