#!/usr/bin/env python3
"""Validate coding-agent handoff mappings between PRD and prototype.

The check is intentionally conservative and regex-based. It does not try to
fully parse Markdown, YAML, or HTML. It verifies the deterministic links that
coding agents need before turning a PRD/prototype into implementation tasks:

- prototype data-testid -> ac_structured.data_testid
- prototype data-action -> FRR prose or ac_structured.data_action
- prototype data-state -> PRD state matrix/prose
- prototype data-api + data-method -> PRD API/contract prose
- prototype data-visible-role -> PRD role/permission prose
- interactive prototype controls have data-testid
- runtime data-state values are concrete, not template placeholders
- domain-state modals/drawers have stable identifiers or a modal contract
- ac_structured does not leave data_testid/data_action as MISSING placeholders
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ATTR_RE = re.compile(r"\b(data-[a-zA-Z0-9_-]+)\s*=\s*(['\"])(.*?)\2", re.DOTALL)
INTERACTIVE_RE = re.compile(
    r"<(?P<tag>button|a|input|select|textarea)\b(?P<attrs>[^>]*)>",
    re.IGNORECASE | re.DOTALL,
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


def yaml_values(text: str, key: str) -> set[str]:
    pattern = re.compile(rf"^\s*{re.escape(key)}:\s*['\"]?([^'\"\n#]+)", re.MULTILINE)
    return {match.group(1).strip() for match in pattern.finditer(text) if match.group(1).strip()}


def collect_attrs(html: str) -> dict[str, set[str]]:
    values: dict[str, set[str]] = {}
    for name, _quote, value in ATTR_RE.findall(html):
        values.setdefault(name, set()).add(value.strip())
    return values


def has_window_contract(html: str, name: str) -> bool:
    return bool(re.search(rf"\bwindow\.{re.escape(name)}\b|\b{re.escape(name)}\s*=", html))


def interactive_missing_testid(html: str) -> list[str]:
    missing: list[str] = []
    for match in INTERACTIVE_RE.finditer(html):
        tag = match.group("tag").lower()
        attrs = match.group("attrs") or ""
        if "data-testid" not in attrs:
            label = re.sub(r"\s+", " ", attrs.strip())[:120]
            missing.append(f"<{tag} {label}>")
    return missing


def data_action_missing_testid(html: str) -> list[str]:
    missing: list[str] = []
    for match in re.finditer(r"<(?P<tag>[a-zA-Z0-9-]+)\b(?P<attrs>[^>]*)>", html, re.DOTALL):
        attrs = match.group("attrs") or ""
        if "data-action" in attrs and "data-testid" not in attrs:
            action = ""
            action_match = re.search(r"data-action\s*=\s*(['\"])(.*?)\1", attrs, re.DOTALL)
            if action_match:
                action = action_match.group(2)
            missing.append(f"<{match.group('tag')}> data-action={action}")
    return missing


def contains_loose(text: str, value: str) -> bool:
    if not value:
        return True
    if value in text:
        return True
    if ":" in value and value.split(":", 1)[1] in text:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prd", type=Path, required=True, help="PRD/spec file containing FRR and ac_structured")
    parser.add_argument("--prototype", type=Path, required=True, help="HTML prototype to inspect")
    parser.add_argument(
        "--allow-unmapped-testid",
        action="store_true",
        help="Warn instead of fail when non-AC data-testid values exist in the prototype",
    )
    args = parser.parse_args()

    prd_text = read_text(args.prd)
    html = read_text(args.prototype)
    attrs = collect_attrs(html)

    failures: list[str] = []
    warnings: list[str] = []

    ac_testids = yaml_values(prd_text, "data_testid")
    ac_actions = yaml_values(prd_text, "data_action")

    missing_ac_placeholders = sorted(
        value for value in (ac_testids | ac_actions)
        if value.upper() in {"MISSING", "TBD", "TODO", "UNKNOWN", "N/A"}
    )
    if missing_ac_placeholders:
        failures.append(
            "ac_structured contains unresolved data_testid/data_action placeholders: "
            + ", ".join(missing_ac_placeholders)
        )

    prototype_testids = attrs.get("data-testid", set())
    unmapped_testids = sorted(t for t in prototype_testids if t not in ac_testids)
    if unmapped_testids:
        message = "data-testid values not mapped by ac_structured.data_testid: " + ", ".join(unmapped_testids[:50])
        if args.allow_unmapped_testid:
            warnings.append(message)
        else:
            failures.append(message)

    actions = attrs.get("data-action", set())
    missing_actions = sorted(a for a in actions if a not in prd_text and a not in ac_actions)
    if missing_actions:
        failures.append("data-action values missing from PRD FRR flow/actions or AC: " + ", ".join(missing_actions[:50]))

    states = attrs.get("data-state", set())
    templated_states = sorted(s for s in states if "${" in s or "{{" in s or "}}" in s)
    if templated_states:
        if has_window_contract(html, "STATE_ENUMS"):
            warnings.append(
                "template-like data-state values detected; verify rendered DOM replaces them: "
                + ", ".join(templated_states[:20])
            )
        else:
            failures.append(
                "TEMPLATE_STATE_DETECTED: data-state values contain template placeholders "
                "and window.STATE_ENUMS is missing: "
                + ", ".join(templated_states[:20])
            )
    missing_states = sorted(s for s in states if not contains_loose(prd_text, s))
    if missing_states:
        failures.append("data-state values missing from PRD state matrix/prose: " + ", ".join(missing_states[:50]))

    apis = attrs.get("data-api", set())
    methods = attrs.get("data-method", set())
    missing_api = sorted(api for api in apis if api not in prd_text)
    missing_method = sorted(method for method in methods if method not in prd_text)
    if missing_api or missing_method:
        failures.append(
            "data-api/data-method values missing from PRD contract: "
            + ", ".join((missing_api + missing_method)[:50])
        )

    role_values = attrs.get("data-visible-role", set())
    roles = sorted({role.strip() for value in role_values for role in value.split(",") if role.strip()})
    missing_roles = sorted(role for role in roles if role not in prd_text)
    if missing_roles:
        failures.append("data-visible-role values missing from PRD permissions: " + ", ".join(missing_roles[:50]))

    if not role_values and re.search(r"\bcanView[A-Z]|\bcan[A-Z][A-Za-z0-9_]*\(", html):
        if not has_window_contract(html, "PROTOTYPE_ROLE_CONTRACT"):
            warnings.append(
                "runtime role/permission helpers detected but no data-visible-role or "
                "window.PROTOTYPE_ROLE_CONTRACT was found"
            )

    has_modal_testid = bool(
        re.search(r"""data-testid=["'](?:modal|drawer)-[^"']+["']""", html)
    )
    has_modal_helper = bool(re.search(r"\b(showModal|openModal|showDrawer|openDrawer)\s*\(", html))
    if has_modal_helper and not has_modal_testid and not has_window_contract(html, "MODAL_CONTRACT"):
        failures.append(
            "MODAL_TESTID_GAP: modal/drawer helper detected but no stable modal-* / "
            "drawer-* data-testid or window.MODAL_CONTRACT was found"
        )

    write_action_re = re.compile(
        r"^(save|create|update|delete|remove|submit|approve|reject|assign|convert|"
        r"close|resolve|escalate|confirm|register|adjust|recover|publish|send|"
        r"import|export|do)-",
        re.IGNORECASE,
    )
    write_actions = sorted(a for a in actions if write_action_re.search(a))
    if write_actions and not apis and not has_window_contract(html, "ACTION_API_CONTRACT"):
        warnings.append(
            "write-like data-action values found without data-api/data-method or "
            "window.ACTION_API_CONTRACT: " + ", ".join(write_actions[:30])
        )

    missing_controls = interactive_missing_testid(html)
    if missing_controls:
        failures.append("interactive elements missing data-testid: " + "; ".join(missing_controls[:30]))

    missing_action_testids = data_action_missing_testid(html)
    if missing_action_testids:
        failures.append("data-action elements missing data-testid: " + "; ".join(missing_action_testids[:30]))

    if warnings:
        print("WARN")
        for warning in warnings:
            print(f"- {warning}")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: coding-agent PRD/prototype contract mappings are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
