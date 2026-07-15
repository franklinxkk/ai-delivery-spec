#!/usr/bin/env python3
"""Detect !important, utility and generic-state selector pollution in prototypes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)


def scan(text: str) -> list[dict[str, str]]:
    css_parts = STYLE_BLOCK.findall(text) if "<" in text else [text]
    css = "\n".join(css_parts)
    findings: list[dict[str, str]] = []
    hidden_rules: list[tuple[str, str]] = []
    generic_state_classes = {"active", "open", "selected", "disabled", "loading", "error", "success", "failed"}
    for selector_raw, body_raw in RULE.findall(css):
        selector = " ".join(selector_raw.split())
        body = " ".join(body_raw.split())
        if ".hidden" in selector:
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
    if len(hidden_rules) > 1:
        findings.append({"kind": "duplicate-hidden-rules", "selector": ".hidden", "detail": f"{len(hidden_rules)} definitions found"})
    if re.search(r"class=[\"'][^\"']*\bhidden\b", text, re.I) and not hidden_rules:
        findings.append({"kind": "missing-hidden-rule", "selector": ".hidden", "detail": "HTML uses hidden class but CSS does not define it"})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()
    findings = scan(args.document.read_text(encoding="utf-8"))
    if args.format == "json":
        print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"FAIL: {item['kind']} [{item['selector']}]: {item['detail']}")
    if findings:
        return 1
    print("PASS: prototype CSS utilities and generic state selectors are scoped without !important pollution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
