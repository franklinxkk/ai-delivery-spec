#!/usr/bin/env python3
"""Detect !important, utility and generic-state selector pollution in prototypes.

CSS-only kinds: hidden-without-display-none, hidden-selector-pollution,
generic-state-selector-pollution, important-pollution, duplicate-hidden-rules,
missing-hidden-rule, unreadable-type-scale.

HTML-aware kinds (skipped for pure CSS input): unstyled-control-class,
flat-button-hierarchy, dual-navigation.
"""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path


STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
FONT_SIZE = re.compile(r"font-size\s*:\s*([0-9]*\.?[0-9]+)\s*px", re.I)
MIN_FONT_PX = 11.0
CLASS_IN_SELECTOR = re.compile(r"\.([A-Za-z_-][\w-]*)")
EXACT_HIDDEN_SELECTOR = re.compile(r"(?<![\w-])\.hidden(?![\w-])")

INTERACTIVE_TAGS = {"a", "button", "input", "select", "textarea"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
NAV_CONTAINER_CLASS = re.compile(r"nav|tabs|tab-bar", re.I)
NAV_ITEM_CLASS = re.compile(r"-(item|link|btn|button)$", re.I)
NAV_TESTID = re.compile(r"(?:^|[-_])(?:nav|tab|tabs|tab-bar)(?:[-_]|$)", re.I)


class _PrototypeHTMLParser(HTMLParser):
    """Collect elements with their classes, data-action and enclosing page container."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[dict[str, object]] = []
        self._stack: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._record(tag, attrs)
        if tag not in VOID_TAGS:
            self._stack.append((tag, dict(attrs).get("data-testid") or ""))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._record(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._stack) - 1, -1, -1):
            if self._stack[index][0] == tag:
                del self._stack[index:]
                break

    def _record(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        page = next((testid for _, testid in reversed(self._stack) if testid.startswith("page-")), "")
        self.elements.append({
            "tag": tag,
            "classes": (data.get("class") or "").split(),
            "testid": data.get("data-testid") or "",
            "action": "data-action" in data,
            "page": page,
        })


def _element_id(element: dict[str, object]) -> str:
    classes = element["classes"]
    suffix = "." + ".".join(classes) if classes else ""
    return f"{element['tag']}{suffix}"


def _scan_html(text: str, css: str) -> list[dict[str, str]]:
    parser = _PrototypeHTMLParser()
    parser.feed(text)
    findings: list[dict[str, str]] = []

    covered_classes: set[str] = set()
    for selector_raw, _ in RULE.findall(css):
        covered_classes.update(CLASS_IN_SELECTOR.findall(selector_raw))

    reported: set[tuple[str, str]] = set()
    for element in parser.elements:
        classes = element["classes"]
        if not classes or (element["tag"] not in INTERACTIVE_TAGS and not element["action"]):
            continue
        for cls in classes:
            if cls not in covered_classes and (_element_id(element), cls) not in reported:
                reported.add((_element_id(element), cls))
                findings.append({
                    "kind": "unstyled-control-class",
                    "selector": _element_id(element),
                    "detail": f"interactive element class '{cls}' has no rule covering it in <style>",
                })

    actions = [element for element in parser.elements if element["action"]]
    if len(actions) >= 3 and len({tuple(sorted(element["classes"])) for element in actions}) == 1:
        findings.append({
            "kind": "flat-button-hierarchy",
            "selector": _element_id(actions[0]),
            "detail": f"{len(actions)} data-action elements share the identical class combination; distinguish primary and secondary actions",
        })

    nav_pages: dict[str, int] = {}
    for element in parser.elements:
        if not element["page"]:
            continue
        is_nav_container = any(
            NAV_CONTAINER_CLASS.search(token) and not NAV_ITEM_CLASS.search(token)
            for token in element["classes"]
        ) or bool(NAV_TESTID.search(element["testid"]))
        if is_nav_container:
            nav_pages[element["page"]] = nav_pages.get(element["page"], 0) + 1
    for page, count in nav_pages.items():
        if count >= 2:
            findings.append({
                "kind": "dual-navigation",
                "selector": f'[data-testid="{page}"]',
                "detail": f"{count} navigation containers inside one page container; keep a single navigation pattern per page",
            })
    return findings


def scan(text: str) -> list[dict[str, str]]:
    has_html = "<" in text
    css_parts = STYLE_BLOCK.findall(text) if has_html else [text]
    css = "\n".join(css_parts)
    findings: list[dict[str, str]] = []
    hidden_rules: list[tuple[str, str]] = []
    generic_state_classes = {"active", "open", "selected", "disabled", "loading", "error", "success", "failed"}
    for selector_raw, body_raw in RULE.findall(css):
        selector = " ".join(selector_raw.split())
        body = " ".join(body_raw.split())
        if EXACT_HIDDEN_SELECTOR.search(selector):
            hidden_rules.append((selector, body))
            if not re.search(r"\bdisplay\s*:\s*none\b", body, re.I):
                findings.append({"kind": "hidden-without-display-none", "selector": selector, "detail": body})
            if "," in selector or selector.strip() != ".hidden":
                findings.append({"kind": "hidden-selector-pollution", "selector": selector, "detail": "keep the utility isolated as .hidden"})
        simple_group = [item.strip() for item in selector.split(",")]
        simple_classes = [match.group(1).lower() for item in simple_group if (match := re.fullmatch(r"\.([A-Za-z_-][\w-]*)", item))]
        polluted = sorted(set(simple_classes) & generic_state_classes)
        if len(simple_group) > 1 and polluted:
            findings.append({
                "kind": "generic-state-selector-pollution",
                "selector": selector,
                "detail": "scope generic state classes to their component, for example .status.active instead of grouped .active",
            })
        for declaration in re.findall(r"[^;{}]+!important", body, re.I):
            allowed = selector.strip() == ".hidden" and re.search(r"display\s*:\s*none\s*!important", declaration, re.I)
            if not allowed:
                findings.append({"kind": "important-pollution", "selector": selector, "detail": declaration.strip()})
        for size in FONT_SIZE.findall(body):
            if float(size) < MIN_FONT_PX:
                findings.append({
                    "kind": "unreadable-type-scale",
                    "selector": selector,
                    "detail": f"font-size {size}px is below the {int(MIN_FONT_PX)}px minimum readable size",
                })
    if len(hidden_rules) > 1:
        findings.append({"kind": "duplicate-hidden-rules", "selector": ".hidden", "detail": f"{len(hidden_rules)} definitions found"})
    class_values = re.findall(r"\bclass\s*=\s*[\"']([^\"']*)[\"']", text, re.I)
    uses_exact_hidden_class = any("hidden" in value.split() for value in class_values)
    if uses_exact_hidden_class and not hidden_rules:
        findings.append({"kind": "missing-hidden-rule", "selector": ".hidden", "detail": "HTML uses hidden class but CSS does not define it"})
    if has_html:
        findings.extend(_scan_html(text, css))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    if not args.document.is_file():
        message = f"input document not found: {args.document}"
        if args.format == "json":
            print(json.dumps({"status": "BLOCKED", "error": message, "findings": []}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {message}")
        return 2
    findings = scan(args.document.read_text(encoding="utf-8"))
    if args.format == "json":
        print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"FAIL: {item['kind']} [{item['selector']}]: {item['detail']}")
    if findings:
        return 1
    print("PASS: prototype CSS utilities, state selectors, control styling, type scale and navigation are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
