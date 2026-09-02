"""Static prototype and acceptance-run checks (mixin split out of quality_gate.py)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent.parent
for _candidate in (SCRIPT_DIR, SCRIPT_DIR / "validators"):
    if str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

from jsonschema import Draft202012Validator, FormatChecker

from scan_prototype_css import scan as scan_prototype_css
from extract_interaction_ledger import (
    extract_dynamic_anchor_actions,
    extract_handler_actions,
    inspect_runtime_action_assignments,
)
from validate_acceptance_run import validate_evidence_refs

REVIEW_WORKSPACE_SCHEMA = SCRIPT_DIR.parent / "schemas" / "review-workspace.schema.json"

# Visible-text markers of acceptance/demo scaffolding that must never ship in a
# customer-facing prototype. Extend this tuple when new scaffold phrases appear.
DEMO_SCAFFOLDING_TERMS: tuple[str, ...] = (
    "验收场景",
    "验收样本",
    "E2E CONSOLE",
    "体验身份",
    "INHERITANCE",
    "继承预览",
    "下游继承预览",
    "lorem",
    "占位",
    "示例数据",
    "测试数据",
    "敬请期待",
    "xxx",
)

SCAFFOLDING_TERMS_FILE = SCRIPT_DIR.parent / "references" / "scaffolding-terms.yaml"
_scaffolding_terms_cache: tuple[str, ...] | None = None


def scaffolding_terms() -> tuple[str, ...]:
    """Merge the built-in visible-demo terms with the optional project list."""
    global _scaffolding_terms_cache
    if _scaffolding_terms_cache is not None:
        return _scaffolding_terms_cache
    terms = list(DEMO_SCAFFOLDING_TERMS)
    if SCAFFOLDING_TERMS_FILE.is_file():
        try:
            data = yaml.safe_load(SCAFFOLDING_TERMS_FILE.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError):
            data = None
        extras = data.get("terms", []) if isinstance(data, dict) else []
        for item in extras if isinstance(extras, list) else []:
            text = str(item).strip()
            if text and text.casefold() not in {term.casefold() for term in terms}:
                terms.append(text)
    _scaffolding_terms_cache = tuple(terms)
    return _scaffolding_terms_cache


def _visible_text(raw: str) -> str:
    """Strip scripts, styles, comments and tags, leaving user-visible copy."""
    text = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    return re.sub(r"<[^>]+>", " ", text)


class _ReviewStatusParser(HTMLParser):
    """Collect status axes only when their element and ancestors are visible."""

    _VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    _LOCALIZED_LABELS = {
        "confirmed": ("confirmed", "已确认", "确认"),
        "proposed": ("proposed", "建议", "提议", "待确认"),
        "inferred": ("inferred", "推断"),
        "unknown": ("unknown", "未知"),
        "conflict": ("conflict", "冲突"),
        "not_run": ("not_run", "not run", "未执行", "未运行"),
        "static_checked": ("static_checked", "static checked", "静态检查", "静态已检查"),
        "browser_checked": ("browser_checked", "browser checked", "浏览器检查", "浏览器已检查"),
        "integration_checked": ("integration_checked", "integration checked", "集成检查", "集成已检查"),
        "accepted": ("accepted", "已验收", "验收通过"),
        "failed": ("failed", "失败", "未通过"),
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.active: list[dict[str, object]] = []
        self.found: dict[tuple[str, str], str] = {}
        self.duplicates: set[tuple[str, str]] = set()

    @staticmethod
    def _is_hidden(attributes: dict[str, str], parent_hidden: bool, tag: str) -> bool:
        styles = re.sub(r"\s+", "", attributes.get("style", "").casefold())
        classes = {item.casefold() for item in attributes.get("class", "").split()}
        return (
            parent_hidden
            or tag in {"script", "style", "template"}
            or "hidden" in attributes
            or attributes.get("aria-hidden", "").casefold() == "true"
            or bool(classes & {"hidden", "is-hidden", "visually-hidden", "sr-only"})
            or "display:none" in styles
            or "visibility:hidden" in styles
            or "opacity:0" in styles
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {str(key).casefold(): str(value or "") for key, value in attrs}
        hidden = self._is_hidden(attributes, self.stack[-1][1] if self.stack else False, tag.casefold())
        self.stack.append((tag.casefold(), hidden))
        step = attributes.get("data-review-status-step", "").upper()
        axis = attributes.get("data-review-status-axis", "").casefold()
        value = attributes.get("data-review-status-value", "").casefold()
        if (
            not hidden
            and re.fullmatch(r"STEP-[A-Z0-9-]+", step)
            and axis in {"business", "verification"}
            and value
        ):
            self.active.append({
                "depth": len(self.stack), "step": step, "axis": axis,
                "value": value, "text": [],
            })
        if tag.casefold() in self._VOID_TAGS:
            self.handle_endtag(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.casefold() not in self._VOID_TAGS:
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if self.stack and not self.stack[-1][1]:
            for record in self.active:
                record["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        closing = tag.casefold()
        index = next((item for item in range(len(self.stack) - 1, -1, -1) if self.stack[item][0] == closing), None)
        if index is None:
            return
        closing_depth = index + 1
        remaining: list[dict[str, object]] = []
        for record in self.active:
            if int(record["depth"]) < closing_depth:
                remaining.append(record)
                continue
            label = " ".join(str(item) for item in record["text"]).casefold()
            value = str(record["value"])
            aliases = self._LOCALIZED_LABELS.get(value, (value,))
            if any(alias.casefold() in label for alias in aliases):
                key = (str(record["step"]), str(record["axis"]))
                if key in self.found:
                    self.duplicates.add(key)
                self.found[key] = value
        self.active = remaining
        self.stack = self.stack[:index]


def _visible_review_statuses(raw: str) -> tuple[dict[tuple[str, str], str], set[tuple[str, str]]]:
    parser = _ReviewStatusParser()
    try:
        parser.feed(raw)
        parser.close()
    except (UnicodeError, ValueError):
        return {}, set()
    return parser.found, parser.duplicates


class _MetricBindingParser(HTMLParser):
    """Collect each metric ID with an explicit or visible semantic label."""

    _VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.active: list[dict[str, object]] = []
        self.bindings: list[tuple[str, str, bool]] = []

    def _start(self, tag: str, attrs: list[tuple[str, str | None]], *, closed: bool) -> None:
        tag = tag.casefold()
        attr_map = {str(key).casefold(): (value or "") for key, value in attrs}
        if not closed and tag not in self._VOID_TAGS:
            self.depth += 1
        metric_id = attr_map.get("data-metric", "").strip()
        if not metric_id:
            return
        explicit_label = next(
            (attr_map.get(key, "").strip() for key in ("data-metric-label", "aria-label", "title") if attr_map.get(key, "").strip()),
            "",
        )
        record: dict[str, object] = {
            "id": metric_id.upper(), "tag": tag, "depth": self.depth,
            "explicit": bool(explicit_label), "text": [explicit_label] if explicit_label else [],
        }
        if closed or tag in self._VOID_TAGS:
            self._finish(record)
        else:
            self.active.append(record)

    def _finish(self, record: dict[str, object]) -> None:
        text = " ".join(str(item) for item in record["text"] if str(item).strip())
        self.bindings.append((str(record["id"]), text, bool(record["explicit"])))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, closed=False)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, closed=True)

    def handle_data(self, data: str) -> None:
        if data.strip():
            for record in self.active:
                if not record["explicit"]:
                    record["text"].append(data)  # type: ignore[union-attr]

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        for index in range(len(self.active) - 1, -1, -1):
            record = self.active[index]
            if record["tag"] == tag and record["depth"] == self.depth:
                self._finish(record)
                self.active.pop(index)
                break
        if tag not in self._VOID_TAGS:
            self.depth = max(0, self.depth - 1)

    def close(self) -> None:
        super().close()
        for record in self.active:
            self._finish(record)
        self.active.clear()


def _metric_bindings(raw: str) -> list[tuple[str, str, bool]]:
    parser = _MetricBindingParser()
    try:
        parser.feed(raw)
        parser.close()
    except Exception:  # malformed HTML is handled by the prototype syntax checks
        return []
    return parser.bindings


def _normalize_metric_label(value: str) -> str:
    """Remove volatile values while retaining the business meaning of a KPI label."""
    text = unescape(_visible_text(value)).casefold()
    text = re.sub(r"(?:¥|￥|\$)?[-+]?\d[\d,]*(?:\.\d+)?(?:%|‰)?", " ", text)
    text = re.sub(r"[：:|/\\·•—–_()（）\[\]{}]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:160]


def _prototype_unknown_contracts(raw: str) -> tuple[set[str], set[str]]:
    """Return bound UNK IDs and those with an owned, stage-aware lifecycle contract.

    Prototypes may bind unknowns directly on a DOM element or through a flat JS
    registry object. A label such as ``待确认：UNK-*`` is deliberately not enough:
    without priority, owner, blocking stage, affected refs and fallback, a large
    batch of unknowns can look governed while no one knows what must be resolved.
    """
    bound: set[str] = set()
    complete: set[str] = set()
    required_inline = (
        "data-unk-priority", "data-unk-owner", "data-unk-blocks-stage",
        "data-unk-affected-refs", "data-unk-fallback",
    )
    for tag in re.findall(r"<[A-Za-z][^>]*\bdata-unk\s*=\s*['\"][^'\"]+['\"][^>]*>", raw, re.I | re.S):
        match = re.search(r"\bdata-unk\s*=\s*['\"](UNK-[A-Z0-9-]+)['\"]", tag, re.I)
        if not match:
            continue
        unknown_id = match.group(1).upper()
        bound.add(unknown_id)
        if all(re.search(rf"\b{re.escape(attribute)}\s*=\s*['\"][^'\"]+['\"]", tag, re.I) for attribute in required_inline):
            complete.add(unknown_id)

    object_pattern = re.compile(
        r"\{[^{}]{0,1800}\b(?:id|unk|unknown_id|unknownId)\s*:\s*['\"]"
        r"(UNK-[A-Z0-9-]+)['\"][^{}]{0,1800}\}",
        re.I | re.S,
    )
    for match in object_pattern.finditer(raw):
        unknown_id = match.group(1).upper()
        bound.add(unknown_id)
        body = match.group(0)
        required_properties = (
            r"\bpriority\s*:",
            r"\bowner\s*:",
            r"\b(?:blocks_stage|blocksStage)\s*:",
            r"\b(?:affected_refs|affectedRefs)\s*:",
            r"\b(?:fallback|fallback_path|fallbackPath)\s*:",
        )
        if all(re.search(pattern, body, re.I) for pattern in required_properties):
            complete.add(unknown_id)
    return bound, complete


def _review_workspace_document(raw: str) -> tuple[dict[str, object] | None, str | None]:
    """Read the single embedded review-workspace projection contract.

    The JSON block is a projection index bound to the requirement baseline; it
    is not a second source of business truth.  Keeping it embedded lets a
    portable single-HTML prototype remain independently reviewable.
    """
    matches = re.findall(
        r"<script\b(?=[^>]*\bid\s*=\s*['\"]review-workspace-manifest['\"])(?=[^>]*\btype\s*=\s*['\"]application/json['\"])[^>]*>([\s\S]*?)</script>",
        raw,
        re.I,
    )
    if not matches:
        return None, "missing"
    if len(matches) > 1:
        return None, "duplicate"
    try:
        document = json.loads(matches[0])
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: line {exc.lineno}, column {exc.colno}: {exc.msg}"
    if not isinstance(document, dict):
        return None, "top level must be an object"
    return document, None


def _review_placeholder_paths(value: object, prefix: str = "") -> list[str]:
    """Find obvious template filler without pretending to understand prose."""
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            failures.extend(_review_placeholder_paths(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            failures.extend(_review_placeholder_paths(child, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        text = value.strip()
        if re.search(r"\{[^{}]+\}|(?<![A-Za-z0-9-])(?:TBD|TODO)(?![A-Za-z0-9-])|待补充|待完善|占位", text, re.I):
            failures.append(prefix or "<root>")
        elif re.fullmatch(r"(?:无|暂无|待定|N/?A|none|not applicable)", text, re.I):
            failures.append(prefix or "<root>")
    return failures


class _ReviewLensParser(HTMLParser):
    """Collect role-specific slot coverage from visible review templates."""

    _VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.active_steps: list[dict[str, object]] = []
        self.active: list[dict[str, object]] = []
        self.slots: dict[str, set[str]] = {}
        self.text: dict[str, list[str]] = {}
        self.step_slots: dict[tuple[str, str], set[str]] = {}
        self.step_text: dict[tuple[str, str], list[str]] = {}
        self.step_applicability: dict[tuple[str, str], str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        attr_map = {str(key).casefold(): (value or "") for key, value in attrs}
        if tag not in self._VOID_TAGS:
            self.depth += 1
        step = attr_map.get("data-review-step", "").strip().upper()
        if step:
            self.active_steps.append({"step": step, "tag": tag, "depth": self.depth})
        role = attr_map.get("data-review-lens", "").strip().casefold()
        if role:
            active_step = str(self.active_steps[-1]["step"]) if self.active_steps else ""
            self.active.append({"role": role, "step": active_step, "tag": tag, "depth": self.depth})
            self.slots.setdefault(role, set())
            self.text.setdefault(role, [])
            if active_step:
                self.step_slots.setdefault((active_step, role), set())
                self.step_text.setdefault((active_step, role), [])
                self.step_applicability[(active_step, role)] = attr_map.get(
                    "data-review-applicability", ""
                ).strip().casefold()
        slot = attr_map.get("data-review-slot", "").strip().casefold()
        if slot:
            for record in self.active:
                record_role = str(record["role"])
                record_step = str(record.get("step", ""))
                self.slots.setdefault(record_role, set()).add(slot)
                if record_step:
                    self.step_slots.setdefault((record_step, record_role), set()).add(slot)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if data.strip():
            for record in self.active:
                record_role = str(record["role"])
                record_step = str(record.get("step", ""))
                self.text.setdefault(record_role, []).append(data.strip())
                if record_step:
                    self.step_text.setdefault((record_step, record_role), []).append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        for index in range(len(self.active) - 1, -1, -1):
            record = self.active[index]
            if record["tag"] == tag and record["depth"] == self.depth:
                self.active.pop(index)
                break
        for index in range(len(self.active_steps) - 1, -1, -1):
            record = self.active_steps[index]
            if record["tag"] == tag and record["depth"] == self.depth:
                self.active_steps.pop(index)
                break
        if tag not in self._VOID_TAGS:
            self.depth = max(0, self.depth - 1)


def _review_lens_coverage(raw: str) -> tuple[
    dict[str, set[str]], dict[str, str],
    dict[tuple[str, str], set[str]], dict[tuple[str, str], str],
    dict[tuple[str, str], str],
]:
    parser = _ReviewLensParser()
    try:
        parser.feed(raw)
        parser.close()
    except Exception:
        return {}, {}, {}, {}, {}
    return (
        parser.slots,
        {role: " ".join(parts).strip() for role, parts in parser.text.items()},
        parser.step_slots,
        {key: " ".join(parts).strip() for key, parts in parser.step_text.items()},
        parser.step_applicability,
    )


def _handler_actions(scripts: str) -> set[str]:
    """Extract action IDs from the shared interaction-ledger parser."""
    return set(extract_handler_actions(scripts))


def _unreachable_hidden_surfaces(tag_source: str, scripts: str) -> list[str]:
    """Return explicitly hidden page/modal/drawer roots with no static route."""
    targets = {
        item.casefold()
        for item in re.findall(r"\bdata-(?:view|target)\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)
    }
    for pattern in (
        r"(?:showPage|showView|navigate|openSurface|openModal|openDrawer)\s*\(\s*['\"]([^'\"]+)['\"]",
        r"(?:targetView|viewId|pageId|modalId|drawerId)\s*[:=]\s*['\"]([^'\"]+)['\"]",
    ):
        targets.update(item.casefold() for item in re.findall(pattern, scripts, re.I))
    for _variable, target in re.findall(
        r"\bconst\s+([A-Za-z_$][\w$]*)\s*=\s*\$\(\s*['\"]#([^'\"]+)['\"]\s*\)"
        r"[\s\S]{0,600}?\b\1\.hidden\s*=\s*(?:false|!\s*\1\.hidden)",
        scripts,
        re.I,
    ):
        targets.add(target.casefold())
    targets.update(
        item.casefold()
        for item in re.findall(
            r"\$\(\s*['\"]#([^'\"]+)['\"]\s*\)\.hidden\s*=\s*false",
            scripts,
            re.I,
        )
    )
    targets.update(item.lstrip("#.") for item in list(targets))

    unreachable: list[str] = []
    for tag in re.findall(r"<[A-Za-z][^>]*>", tag_source, re.S):
        testid_match = re.search(r"\bdata-testid\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
        id_match = re.search(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
        view_match = re.search(r"\bdata-view\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
        class_match = re.search(r"\bclass\s*=\s*['\"]([^'\"]*)['\"]", tag, re.I)
        testid = testid_match.group(1) if testid_match else ""
        classes = class_match.group(1) if class_match else ""
        class_tokens = {item.casefold() for item in re.split(r"\s+", classes) if item}
        is_surface = (
            testid.casefold().startswith(("page-", "modal-", "drawer-"))
            or bool(class_tokens & {"page", "modal", "drawer", "dialog", "sheet"})
        )
        if not is_surface:
            continue
        explicitly_hidden = bool(re.search(r"\shidden(?:\s|=|>)", tag, re.I)) or "hidden" in class_tokens
        initially_visible = bool(class_tokens & {"active", "open", "show", "visible", "is-visible"})
        if not explicitly_hidden or initially_visible:
            continue
        keys = {
            value.casefold()
            for value in (
                testid,
                id_match.group(1) if id_match else "",
                view_match.group(1) if view_match else "",
            )
            if value
        }
        aliases = set(keys)
        for key in list(keys):
            aliases.update({
                re.sub(r"^(?:page|modal|drawer)-", "", key),
                key.replace("view-", ""),
                re.sub(r"^(?:(?:page|modal|drawer|view)-)+", "", key),
            })
        if not aliases & targets:
            unreachable.append(testid or (id_match.group(1) if id_match else "<anonymous>"))
    return sorted(set(unreachable))


class _ReviewFinalParser(HTMLParser):
    """Collect the context-scoped 5.4.7-5.4.9 review projection."""

    _VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.context_stack: list[tuple[int, str]] = []
        self.active_cards: list[dict[str, object]] = []
        self.active_semantics: list[dict[str, object]] = []
        self.workspace_depths: list[int] = []
        self.trace_depths: list[int] = []
        self.tab_stack: list[tuple[int, str]] = []
        self.active_traces: list[dict[str, object]] = []
        self.role_detail_stack: list[tuple[int, str]] = []
        self.active_role_details: list[dict[str, object]] = []
        self.active_examples: list[dict[str, object]] = []
        self.context_roots: Counter[str] = Counter()
        self.markers: list[dict[str, str]] = []
        self.cards: list[dict[str, str]] = []
        self.card_text: dict[str, str] = {}
        self.semantic_surfaces: list[dict[str, str]] = []
        self.semantic_text: dict[str, str] = {}
        self.product_overlays: list[dict[str, str]] = []
        self.targets: dict[str, Counter[str]] = defaultdict(Counter)
        self.visible_targets: dict[str, Counter[str]] = defaultdict(Counter)
        self.unbound_metric_like: Counter[str] = Counter()
        self.content_owners: list[tuple[str, str]] = []
        self.workspace_roots: list[dict[str, str]] = []
        self.primary_review_text: list[str] = []
        self.technical_traces: list[dict[str, object]] = []
        self.role_details: list[dict[str, object]] = []
        self.role_detail_text: dict[tuple[str, str], str] = {}
        self.diagrams: list[dict[str, str]] = []
        self.flow_context_nodes: list[dict[str, str]] = []
        self.acceptance_examples: list[dict[str, str]] = []
        self.acceptance_example_text: dict[str, str] = {}

    @staticmethod
    def _hidden(attrs: dict[str, str], parent_hidden: bool, tag: str) -> bool:
        style = re.sub(r"\s+", "", attrs.get("style", "").casefold())
        classes = {item.casefold() for item in attrs.get("class", "").split()}
        return (
            parent_hidden
            or tag in {"script", "style", "template"}
            or "hidden" in attrs
            or attrs.get("aria-hidden", "").casefold() == "true"
            or bool(classes & {"hidden", "is-hidden"})
            or "display:none" in style
            or "visibility:hidden" in style
        )

    @staticmethod
    def _target_refs(attrs: dict[str, str]) -> set[str]:
        refs: set[str] = set()
        for key, prefixes in (
            ("data-action", ("ACT-",)),
            ("data-field", ("FLD-",)),
            ("data-bind", ("FLD-",)),
            ("data-metric", ("METRIC-",)),
            ("data-state", ("STATE-",)),
        ):
            value = attrs.get(key, "").upper()
            if value.startswith(prefixes):
                refs.add(value)
        testid = attrs.get("data-testid", "").upper()
        for prefix in ("PAGE-", "REGION-"):
            if testid.startswith(prefix):
                candidate = testid[len(prefix):]
                if re.fullmatch(r"(?:VIEW|REG)-[A-Z0-9-]+", candidate):
                    refs.add(candidate)
        return refs

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        attr_map = {str(key).casefold(): str(value or "") for key, value in attrs}
        hidden = self._hidden(attr_map, self.stack[-1][1] if self.stack else False, tag)
        self.stack.append((tag, hidden))
        depth = len(self.stack)

        context_ref = attr_map.get("data-review-context-root", "").upper()
        if context_ref:
            self.context_roots[context_ref] += 1
            self.context_stack.append((depth, context_ref))
        active_context = self.context_stack[-1][1] if self.context_stack else ""

        if "data-review-workspace" in attr_map:
            self.workspace_roots.append(attr_map)
            self.workspace_depths.append(depth)
        tab_name = attr_map.get("data-review-tab", "").casefold()
        if tab_name:
            self.tab_stack.append((depth, tab_name))

        if "data-review-trace" in attr_map:
            record: dict[str, object] = {
                "depth": depth,
                "open": "open" in attr_map,
                "text": [],
            }
            self.technical_traces.append(record)
            self.active_traces.append(record)
            self.trace_depths.append(depth)

        detail_for = attr_map.get("data-review-detail-for", "").upper()
        if "data-review-role-details" in attr_map:
            record = {
                "point": detail_for,
                "open": "open" in attr_map,
                "roles": set(),
            }
            self.role_details.append(record)
            self.role_detail_stack.append((depth, detail_for))
        role_detail = attr_map.get("data-review-role-detail", "").casefold()
        if role_detail:
            detail_point = self.role_detail_stack[-1][1] if self.role_detail_stack else ""
            if self.role_details:
                self.role_details[-1]["roles"].add(role_detail)  # type: ignore[union-attr]
            self.active_role_details.append({
                "depth": depth,
                "point": detail_point,
                "role": role_detail,
                "text": [],
            })

        diagram_ref = attr_map.get("data-review-diagram", "").upper()
        if diagram_ref:
            self.diagrams.append({
                "ref": diagram_ref,
                "type": attr_map.get("data-review-diagram-type", "").casefold(),
                "owner": attr_map.get("data-review-diagram-owner", "").casefold(),
                "tab": self.tab_stack[-1][1] if self.tab_stack else "",
                "context": attr_map.get("data-review-context", active_context).upper(),
                "visible": str(not hidden).lower(),
            })
        flow_context = attr_map.get("data-review-flow-context", "").upper()
        if flow_context:
            self.flow_context_nodes.append({
                "diagram": attr_map.get("data-review-diagram-ref", "").upper(),
                "context": flow_context,
                "current": attr_map.get("data-flow-current", "").casefold(),
                "visible": str(not hidden).lower(),
            })

        example_ref = attr_map.get("data-review-example", "").upper()
        if example_ref:
            record = {
                "depth": depth,
                "ref": example_ref,
                "kind": attr_map.get("data-review-example-kind", "").casefold(),
                "context": attr_map.get("data-review-context", active_context).upper(),
                "acceptance": attr_map.get("data-review-acceptance-ref", "").upper(),
                "tab": self.tab_stack[-1][1] if self.tab_stack else "",
                "visible": str(not hidden).lower(),
                "text": [],
            }
            self.acceptance_examples.append({key: str(value) for key, value in record.items() if key not in {"depth", "text"}})
            self.active_examples.append(record)

        testid = attr_map.get("data-testid", "")
        if (
            attr_map.get("role", "").casefold() == "dialog"
            or re.match(r"^(?:modal|drawer)-", testid, re.I)
        ):
            self.product_overlays.append({
                "testid": testid or "role=dialog",
                "declared_context": context_ref,
                "active_context": active_context,
                "visible": str(not hidden).lower(),
            })

        marker_ref = attr_map.get("data-review-ref", "").upper()
        if re.fullmatch(r"(?:RP|RVP)-[A-Z0-9-]+", marker_ref):
            self.markers.append({
                "ref": marker_ref,
                "context": attr_map.get("data-review-context", active_context).upper(),
                "number": attr_map.get("data-review-number", ""),
                "visible": str(not hidden).lower(),
            })

        point_ref = attr_map.get("data-review-point", "").upper()
        if re.fullmatch(r"(?:RP|RVP)-[A-Z0-9-]+", point_ref):
            record = {
                "ref": point_ref,
                "context": attr_map.get("data-review-context", "").upper(),
                "number": attr_map.get("data-review-number", ""),
                "business_status": attr_map.get("data-review-business-status", "").casefold(),
                "verification_status": attr_map.get("data-review-verification-status", "").casefold(),
                "evidence_origin": attr_map.get("data-review-evidence-origin", "").casefold(),
                "visible": str(not hidden).lower(),
            }
            self.cards.append(record)
            self.active_cards.append({"depth": depth, "ref": point_ref, "text": [], "hidden": hidden})

        semantic_ref = attr_map.get("data-review-semantic-ref", "").upper()
        if re.fullmatch(r"SCOV-[A-Z0-9-]+", semantic_ref):
            semantic_record = {
                "ref": semantic_ref,
                "owner": attr_map.get("data-review-semantic-owner", "").casefold(),
                "context": attr_map.get("data-review-context", active_context).upper(),
                "visible": str(not hidden).lower(),
            }
            self.semantic_surfaces.append(semantic_record)
            self.active_semantics.append({"depth": depth, "ref": semantic_ref, "text": [], "hidden": hidden})

        content = attr_map.get("data-review-content", "").casefold()
        owner = attr_map.get("data-review-owner-tab", "").casefold()
        if content:
            self.content_owners.append((content, owner))

        if active_context:
            for target_ref in self._target_refs(attr_map):
                self.targets[active_context][target_ref] += 1
                if not hidden:
                    self.visible_targets[active_context][target_ref] += 1
            class_tokens = {item.casefold() for item in attr_map.get("class", "").split()}
            if not hidden and class_tokens & {"metric", "metric-card", "stat-card", "kpi"} and not attr_map.get("data-metric"):
                self.unbound_metric_like[active_context] += 1

        if tag in self._VOID_TAGS:
            self.handle_endtag(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.casefold() not in self._VOID_TAGS:
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        text = data.strip()
        current_hidden = self.stack[-1][1] if self.stack else False
        if self.workspace_depths and not self.trace_depths and not current_hidden:
            self.primary_review_text.append(text)
        for record in self.active_traces:
            record["text"].append(text)  # type: ignore[union-attr]
        for record in self.active_role_details:
            record["text"].append(text)  # type: ignore[union-attr]
        for record in self.active_examples:
            record["text"].append(text)  # type: ignore[union-attr]
        for record in self.active_cards:
            if not bool(record["hidden"]):
                record["text"].append(text)  # type: ignore[union-attr]
        for record in self.active_semantics:
            if not bool(record["hidden"]):
                record["text"].append(text)  # type: ignore[union-attr]

    def handle_endtag(self, tag: str) -> None:
        closing = tag.casefold()
        index = next((item for item in range(len(self.stack) - 1, -1, -1) if self.stack[item][0] == closing), None)
        if index is None:
            return
        closing_depth = index + 1
        remaining_cards: list[dict[str, object]] = []
        for record in self.active_cards:
            if int(record["depth"]) < closing_depth:
                remaining_cards.append(record)
                continue
            ref = str(record["ref"])
            text = " ".join(str(item) for item in record["text"])
            self.card_text[ref] = f"{self.card_text.get(ref, '')} {text}".strip()
        self.active_cards = remaining_cards
        remaining_semantics: list[dict[str, object]] = []
        for record in self.active_semantics:
            if int(record["depth"]) < closing_depth:
                remaining_semantics.append(record)
                continue
            ref = str(record["ref"])
            text = " ".join(str(item) for item in record["text"])
            self.semantic_text[ref] = f"{self.semantic_text.get(ref, '')} {text}".strip()
        self.active_semantics = remaining_semantics
        remaining_role_details: list[dict[str, object]] = []
        for record in self.active_role_details:
            if int(record["depth"]) < closing_depth:
                remaining_role_details.append(record)
                continue
            key = (str(record["point"]), str(record["role"]))
            text = " ".join(str(item) for item in record["text"])
            self.role_detail_text[key] = f"{self.role_detail_text.get(key, '')} {text}".strip()
        self.active_role_details = remaining_role_details
        remaining_examples: list[dict[str, object]] = []
        for record in self.active_examples:
            if int(record["depth"]) < closing_depth:
                remaining_examples.append(record)
                continue
            ref = str(record["ref"])
            text = " ".join(str(item) for item in record["text"])
            self.acceptance_example_text[ref] = f"{self.acceptance_example_text.get(ref, '')} {text}".strip()
        self.active_examples = remaining_examples
        self.active_traces = [record for record in self.active_traces if int(record["depth"]) < closing_depth]
        self.trace_depths = [depth for depth in self.trace_depths if depth < closing_depth]
        self.role_detail_stack = [item for item in self.role_detail_stack if item[0] < closing_depth]
        self.tab_stack = [item for item in self.tab_stack if item[0] < closing_depth]
        self.workspace_depths = [depth for depth in self.workspace_depths if depth < closing_depth]
        self.context_stack = [item for item in self.context_stack if item[0] < closing_depth]
        self.stack = self.stack[:index]


def _review_final_projection(raw: str) -> _ReviewFinalParser:
    parser = _ReviewFinalParser()
    try:
        parser.feed(raw)
        parser.close()
    except Exception:
        pass
    return parser


class PrototypeChecks:
    def _prototype_dependency(self, prototype: Path, uri: str, kind: str) -> Path | None:
        """Resolve a local prototype dependency without leaving the prototype directory."""
        parsed = urlsplit(uri)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            self.add(
                "GAP", "PROTO-REMOTE-DEPENDENCY", prototype,
                f"远程 {kind} 依赖不在本地静态检查范围内", uri,
            )
            return None
        if parsed.scheme or parsed.netloc:
            self.add("BLOCK", "PROTO-DEPENDENCY-URI", prototype, f"不支持的 {kind} 依赖 URI", uri)
            return None
        relative = Path(unquote(parsed.path))
        if relative.is_absolute():
            self.add("BLOCK", "PROTO-DEPENDENCY-ABSOLUTE", prototype, f"{kind} 依赖必须使用原型目录内的相对路径", uri)
            return None
        root = prototype.parent.resolve()
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            self.add("BLOCK", "PROTO-DEPENDENCY-ESCAPE", prototype, f"{kind} 依赖越过原型根目录", uri)
            return None
        if not candidate.is_file():
            self.add("BLOCK", "PROTO-DEPENDENCY-MISSING", prototype, f"本地 {kind} 依赖文件不存在", uri)
            return None
        return candidate

    @staticmethod
    def _page_contracts(raw: str) -> dict[str, tuple[dict[str, str], str]]:
        markers = list(re.finditer(
            r"<!--\s*PAGE-CONTRACT:\s*(VIEW-[A-Z0-9-]+)\s*(.*?)-->", raw, re.I | re.S
        ))
        contracts: dict[str, tuple[dict[str, str], str]] = {}
        for index, marker in enumerate(markers):
            end = markers[index + 1].start() if index + 1 < len(markers) else len(raw)
            attrs: dict[str, str] = {}
            tail = marker.group(2).strip().lstrip(";").strip()
            for part in tail.split(";") if tail else []:
                if "=" not in part:
                    continue
                key, value = part.split("=", 1)
                attrs[key.strip().lower()] = value.strip()
            contracts[marker.group(1).upper()] = (attrs, raw[marker.end():end])
        return contracts

    def _check_review_workspace_final(
        self,
        path: Path,
        raw: str,
        tag_source: str,
        scripts: str,
        document: dict[str, object],
    ) -> set[str]:
        """Validate the context-driven 5.4.7-5.4.9 human review projection.

        Static checks prove declaration integrity and the presence of runtime
        mechanisms. Product-fingerprint invariance, overlay ordering, target
        visibility and non-overlap still require the browser ARUN contract.
        """
        preflight_workspace = document.get("workspace") or {}
        preflight_workspace = preflight_workspace if isinstance(preflight_workspace, dict) else {}
        preflight_level = str(preflight_workspace.get("review_level", ""))
        for point in document.get("review_points", []) or []:
            if not isinstance(point, dict):
                continue
            point_ref = str(point.get("ref", "missing"))
            subject_ref = str(point.get("subject_ref", "")).upper()
            target_mode = str(point.get("target_mode", ""))
            if target_mode == "context_root" and not subject_ref.startswith(("VIEW-", "REG-")):
                self.add(
                    "BLOCK", "PROTO-REVIEW-TARGET-MODE-INVALID", path,
                    "context_root 只允许页面或业务区域方向标号，动作、字段、指标和状态必须精确定位",
                    f"{point_ref}/{subject_ref or 'missing'}",
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
            elif subject_ref.startswith(("ACT-", "FLD-", "METRIC-", "STATE-")) and target_mode != "selector_exactly_one":
                self.add(
                    "BLOCK", "PROTO-REVIEW-TARGET-MODE-INVALID", path,
                    "动作、字段、指标和状态评审点必须使用 selector_exactly_one，禁止回退到整页",
                    f"{point_ref}/{subject_ref}",
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
        preflight_cold_read = document.get("cold_read_contract") or {}
        if (
            preflight_level in {"R1", "R2"}
            and isinstance(preflight_cold_read, dict)
            and str(preflight_cold_read.get("status", "")) == "not_applicable"
        ):
            self.add(
                "BLOCK", "PROTO-REVIEW-COLD-READ", path,
                "R1/R2 评审投影必须保留真实冷读结论，不能声明不适用",
                preflight_level,
                affected_consumers=("product", "frontend", "backend", "qa"),
            )
        preflight_share = document.get("share_contract") or {}
        if isinstance(preflight_share, dict) and preflight_share.get("hydrate_on_load") is not True:
            self.add(
                "BLOCK", "PROTO-REVIEW-SHARE-LOCATOR", path,
                "正式分享定位必须在打开时恢复 baseline、Context、ReviewPoint 和页签",
                "share_contract.hydrate_on_load",
                affected_consumers=("product", "frontend", "qa"),
            )
        schema_errors = []
        if REVIEW_WORKSPACE_SCHEMA.is_file():
            schema = json.loads(REVIEW_WORKSPACE_SCHEMA.read_text(encoding="utf-8"))
            schema_errors = sorted(
                Draft202012Validator(schema).iter_errors(document),
                key=lambda item: tuple(str(part) for part in item.path),
            )
            for error in schema_errors:
                location = ".".join(str(part) for part in error.path) or "<root>"
                self.add(
                    "BLOCK", "PROTO-REVIEW-WORKSPACE-SCHEMA", path,
                    error.message, location,
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
        if schema_errors:
            return set()

        self.review_workspace_contracts.append((path.resolve(), document))
        projection = _review_final_projection(raw)
        workspace_id = str(document.get("workspace_id", ""))
        workspace = document.get("workspace") or {}
        workspace = workspace if isinstance(workspace, dict) else {}
        review_level = str(workspace.get("review_level", ""))
        default_tab = str(workspace.get("default_tab", ""))
        initial_context = str(workspace.get("initial_context_ref", "")).upper()

        declared_language = str(document.get("language", "")).casefold()
        html_language_match = re.search(r"<html\b[^>]*\blang\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)
        html_language = html_language_match.group(1).casefold() if html_language_match else ""
        if declared_language != html_language:
            self.add(
                "BLOCK", "PROTO-REVIEW-LANGUAGE-MISMATCH", path,
                "评审 manifest 的人类语言与 HTML lang 不一致",
                f"{declared_language or 'missing'} != {html_language or 'missing'}",
                affected_consumers=("product", "frontend", "backend", "qa"),
            )

        if len(projection.workspace_roots) != 1:
            self.add(
                "BLOCK", "PROTO-REVIEW-CONTEXT-CONTRACT", path,
                "5.4.7 Final—5.4.9 评审合同必须且只能有一个 data-review-workspace 根",
                str(len(projection.workspace_roots)),
                affected_consumers=("frontend", "qa"),
            )
            root: dict[str, str] = {}
        else:
            root = projection.workspace_roots[0]
        expected_resizable = str(bool((document.get("layout_contract") or {}).get("resizable"))).lower()
        required_root = {
            "data-review-workspace": workspace_id,
            "data-review-level": review_level,
            "data-review-active-tab": default_tab,
            "data-review-current-context": initial_context,
            "data-review-current-context-control": "read-only",
            "data-review-layout": "participate-in-layout",
            "data-review-overlay-product-ui": "false",
            "data-review-resizable": expected_resizable,
            "data-review-collapsible": "true",
        }
        for name, expected in required_root.items():
            if root.get(name, "") != expected:
                self.add(
                    "BLOCK", "PROTO-REVIEW-CONTEXT-CONTRACT" if "context" in name else "PROTO-REVIEW-LAYOUT-NONOVERLAP",
                    path, "评审根属性与 Final manifest 不一致", f"{name}: {root.get(name, 'missing')} != {expected}",
                    affected_consumers=("product", "frontend", "qa"),
                )

        prohibited_attributes = (
            "data-review-mode", "data-review-mode-target", "data-review-active-role",
            "data-review-role", "data-review-lens", "data-review-journey", "data-review-step",
        )
        for attribute in prohibited_attributes:
            if re.search(rf"\b{re.escape(attribute)}\s*=", tag_source, re.I):
                self.add(
                    "BLOCK", "PROTO-REVIEW-LEVEL", path,
                    "Final 评审态不得恢复 Journey/STEP/Page/Role 驱动的人类一级导航", attribute,
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )

        baseline = document.get("baseline") or {}
        if isinstance(baseline, dict) and str(baseline.get("hash", "")) == "0" * 64:
            self.add(
                "BLOCK", "PROTO-REVIEW-BASELINE-PLACEHOLDER", path,
                "评审工作台仍使用全零基线 hash，无法证明与 PRD 同源", workspace_id,
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )
        placeholder_paths = _review_placeholder_paths(document)
        if placeholder_paths:
            self.add(
                "BLOCK", "PROTO-REVIEW-WORKSPACE-PLACEHOLDER", path,
                "评审工作台索引仍含模板占位或无理由的不适用值", ", ".join(placeholder_paths[:8]),
                affected_consumers=("product", "frontend", "backend", "qa"),
            )

        context_items = [item for item in document.get("review_contexts", []) or [] if isinstance(item, dict)]
        point_items = [item for item in document.get("review_points", []) or [] if isinstance(item, dict)]
        candidate_items = [item for item in document.get("candidate_review_points", []) or [] if isinstance(item, dict)]
        semantic_items = [item for item in document.get("semantic_coverage_items", []) or [] if isinstance(item, dict)]
        schema_version = str(document.get("schema_version", ""))
        context_ids = [str(item.get("context_ref", "")).upper() for item in context_items]
        point_ids = [str(item.get("ref", "")).upper() for item in point_items]
        contexts = {str(item.get("context_ref", "")).upper(): item for item in context_items}
        points = {str(item.get("ref", "")).upper(): item for item in point_items}
        candidate_ids = [str(item.get("candidate_id", "")).upper() for item in candidate_items]
        candidate_subjects = [str(item.get("subject_ref", "")).upper() for item in candidate_items]
        declared_subjects = [str(item.get("subject_ref", "")).upper() for item in point_items]
        semantic_ids = [str(item.get("coverage_id", "")).upper() for item in semantic_items]
        semantic_keys = [
            (
                str(item.get("owner_context_ref", "")).upper(),
                str(item.get("subject_ref", "")).upper(),
            )
            for item in semantic_items
        ]
        if schema_version == "5.4.9":
            human_contract = document.get("human_projection_contract") or {}
            human_contract = human_contract if isinstance(human_contract, dict) else {}
            primary_text = " ".join(projection.primary_review_text)
            leaked_ids = sorted(set(re.findall(
                r"\b(?:REQ|SRC|DEC|ROLE|FLOW|STEP|VIEW|REG|ACT|UIACT|ENT|FLD|METRIC|RULE|STM|STATE|API|EVT|INT|AC|TEST|EVD|UNK|MOD|XCT|EDGE|RVP|SCOV|DIAG)-[A-Z0-9-]+\b",
                primary_text,
                re.I,
            )))
            leaked_terms = []
            for term in human_contract.get("technical_terms", []) or []:
                raw_term = str(term)
                if raw_term and re.search(rf"(?<![\w-]){re.escape(raw_term)}(?![\w-])", primary_text):
                    leaked_terms.append(raw_term)
            if leaked_ids or leaked_terms:
                detail = ", ".join([*leaked_ids[:8], *leaked_terms[:8]])
                self.add(
                    "BLOCK", "PROTO-REVIEW-HUMAN-COPY-LEAK", path,
                    "人类主阅读区泄露稳定 ID、字段名或机器枚举；这些内容只能进入默认收起的技术追溯",
                    detail,
                    affected_consumers=("product", "frontend", "backend", "qa"),
                    related_refs=tuple(leaked_ids[:50]),
                )

            if len(projection.technical_traces) != 1:
                self.add(
                    "BLOCK", "PROTO-REVIEW-TECHNICAL-TRACE", path,
                    "5.4.9 评审态必须且只能有一个默认收起的技术追溯区",
                    f"count={len(projection.technical_traces)}",
                    affected_consumers=("frontend", "backend", "qa", "coding_agent"),
                )
                trace_text = ""
            else:
                trace = projection.technical_traces[0]
                if bool(trace.get("open")):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-TECHNICAL-TRACE", path,
                        "技术追溯必须默认收起，不能抢占人类主阅读面",
                        workspace_id,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                trace_text = " ".join(str(item) for item in trace.get("text", []) or [])
            trace_refs = sorted(set(re.findall(
                r"\b[A-Z][A-Z0-9]*-[A-Z0-9-]+\b",
                json.dumps(document, ensure_ascii=False),
            )))
            missing_trace_refs = [ref for ref in trace_refs if ref not in trace_text]
            missing_trace_terms = [
                str(term) for term in human_contract.get("technical_terms", []) or []
                if str(term) not in trace_text
            ]
            if missing_trace_refs or missing_trace_terms:
                self.add(
                    "BLOCK", "PROTO-REVIEW-TECHNICAL-TRACE", path,
                    "技术追溯没有覆盖 manifest 中的稳定 ID、字段名或机器枚举",
                    ", ".join([*missing_trace_refs[:8], *missing_trace_terms[:8]]),
                    affected_consumers=("frontend", "backend", "qa", "coding_agent"),
                    related_refs=tuple(missing_trace_refs[:50]),
                )

            details_by_point: dict[str, list[dict[str, object]]] = defaultdict(list)
            for detail in projection.role_details:
                details_by_point[str(detail.get("point", "")).upper()].append(detail)
            for point in point_items:
                point_ref = str(point.get("ref", "")).upper()
                detail_contract = point.get("implementation_detail") or {}
                detail_contract = detail_contract if isinstance(detail_contract, dict) else {}
                if detail_contract.get("required") is not True:
                    continue
                surfaces = details_by_point.get(point_ref, [])
                if len(surfaces) != 1:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-ROLE-DETAIL", path,
                        "需要实施展开的评审点必须且只能有一个默认收起的前端/后端/测试详情",
                        f"{point_ref}: count={len(surfaces)}",
                        affected_consumers=("frontend", "backend", "qa"), related_refs=(point_ref,),
                    )
                    continue
                detail = surfaces[0]
                if bool(detail.get("open")):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-ROLE-DETAIL", path,
                        "实施详情必须默认收起，由读者按需展开",
                        point_ref,
                        affected_consumers=("product", "frontend", "backend", "qa"), related_refs=(point_ref,),
                    )
                expected_roles = {"frontend", "backend", "qa"}
                actual_roles = {str(item) for item in detail.get("roles", set())}
                if actual_roles != expected_roles:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-ROLE-DETAIL", path,
                        "实施详情必须同时覆盖前端实现、后端处理和测试验收",
                        f"{point_ref}: {', '.join(sorted(actual_roles)) or 'missing'}",
                        affected_consumers=("frontend", "backend", "qa"), related_refs=(point_ref,),
                    )
                for role in sorted(expected_roles):
                    role_text = projection.role_detail_text.get((point_ref, role), "")
                    if len(role_text.strip()) < 12 or re.search(r"\{[^{}]+\}|\b(?:TBD|TODO)\b|待补充|待完善", role_text, re.I):
                        self.add(
                            "BLOCK", "PROTO-REVIEW-ROLE-DETAIL", path,
                            "前端/后端/测试展开项必须是可独立执行的自然语言说明，不能留空或占位",
                            f"{point_ref}/{role}",
                            affected_consumers=(role,), related_refs=(point_ref,),
                        )

            diagram_contract = document.get("diagram_contract") or {}
            diagram_contract = diagram_contract if isinstance(diagram_contract, dict) else {}
            decisions = [item for item in diagram_contract.get("decisions", []) or [] if isinstance(item, dict)]
            diagram_items = [item for item in diagram_contract.get("diagrams", []) or [] if isinstance(item, dict)]
            decision_contexts = [str(item.get("context_ref", "")).upper() for item in decisions]
            diagram_refs = [str(item.get("diagram_ref", "")).upper() for item in diagram_items]
            if len(decision_contexts) != len(set(decision_contexts)) or set(decision_contexts) != set(contexts):
                self.add(
                    "BLOCK", "PROTO-REVIEW-DIAGRAM-DECISION", path,
                    "每个 CurrentContext 必须且只能有一条画图/不画图决定",
                    f"declared={sorted(set(decision_contexts))}; contexts={sorted(contexts)}",
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
            if len(diagram_refs) != len(set(diagram_refs)):
                self.add(
                    "BLOCK", "PROTO-REVIEW-DIAGRAM-DECISION", path,
                    "diagram_contract 存在重复 DIAG-*",
                    workspace_id,
                    affected_consumers=("product", "frontend", "qa"),
                )
            diagram_by_ref = {str(item.get("diagram_ref", "")).upper(): item for item in diagram_items}
            expected_types_by_driver = {
                "cross_page": {"core_flow"},
                "cross_role": {"core_flow"},
                "cross_system": {"core_flow", "data_flow"},
                "three_plus_dependent_steps": {"core_flow"},
                "critical_state_transition": {"state"},
            }
            semantic_types_for_context: dict[str, set[str]] = defaultdict(set)
            for semantic in semantic_items:
                semantic_types_for_context[str(semantic.get("owner_context_ref", "")).upper()].add(
                    str(semantic.get("semantic_type", ""))
                )
            complex_contexts: set[str] = set()
            for decision in decisions:
                context_ref = str(decision.get("context_ref", "")).upper()
                drivers = {str(item) for item in decision.get("complexity_drivers", []) or []}
                context = contexts.get(context_ref, {})
                inferred_drivers: set[str] = set()
                if (
                    str(context.get("context_type", "")) != "VIEW"
                    or bool(context.get("secondary_context_refs", []) or [])
                ):
                    inferred_drivers.add("cross_page")
                surface_types = {str(item) for item in context.get("surface_types", []) or []}
                semantic_types_here = semantic_types_for_context.get(context_ref, set())
                if "workflow" in surface_types or "state_transition" in semantic_types_here:
                    inferred_drivers.add("critical_state_transition")
                if semantic_types_here & {"event_handoff", "role_path"}:
                    inferred_drivers.add("cross_role")
                if not inferred_drivers.issubset(drivers):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DIAGRAM-DECISION", path,
                        "页面合同和语义账本已经触发复杂图，不能在 diagram_contract 中降级为简单 CRUD",
                        f"{context_ref}: missing={sorted(inferred_drivers - drivers)}",
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                declared_types = {str(item) for item in decision.get("required_types", []) or []}
                expected_types: set[str] = set()
                for driver in drivers:
                    expected_types.update(expected_types_by_driver.get(driver, set()))
                if drivers == {"simple_crud"}:
                    expected_types = set()
                elif "simple_crud" in drivers:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DIAGRAM-DECISION", path,
                        "simple_crud 不能与复杂度触发条件同时声明",
                        context_ref,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                if expected_types:
                    complex_contexts.add(context_ref)
                if declared_types != expected_types:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DIAGRAM-DECISION", path,
                        "画图类型必须由复杂度触发条件精确推导，既不能漏图也不能给简单 CRUD 堆图",
                        f"{context_ref}: expected={sorted(expected_types)} actual={sorted(declared_types)}",
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                refs = [str(item).upper() for item in decision.get("diagram_refs", []) or []]
                actual_types = {
                    str(diagram_by_ref.get(ref, {}).get("diagram_type", ""))
                    for ref in refs if ref in diagram_by_ref
                }
                if set(refs) - set(diagram_by_ref) or actual_types != declared_types:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DIAGRAM-DECISION", path,
                        "Context 的 diagram_refs 必须完整解析到所需图类型",
                        context_ref,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )

            dom_diagrams = {item.get("ref", ""): item for item in projection.diagrams}
            if len(dom_diagrams) != len(projection.diagrams) or set(dom_diagrams) != set(diagram_by_ref):
                self.add(
                    "BLOCK", "PROTO-REVIEW-DIAGRAM-VISIBLE", path,
                    "每张声明的图必须在人类评审区恰好出现一次，且不得出现未声明图",
                    f"manifest={sorted(diagram_by_ref)} dom={sorted(dom_diagrams)}",
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
            for diagram_ref, item in diagram_by_ref.items():
                dom = dom_diagrams.get(diagram_ref, {})
                diagram_type = str(item.get("diagram_type", ""))
                owner_tab = str(item.get("owner_tab", ""))
                if dom and (dom.get("type") != diagram_type or dom.get("owner") != owner_tab or dom.get("tab") != owner_tab):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DIAGRAM-VISIBLE", path,
                        "图必须位于声明页签并显示正确类型",
                        f"{diagram_ref}/{diagram_type}/{owner_tab}",
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                if diagram_type != "core_flow":
                    continue
                nodes = [node for node in projection.flow_context_nodes if node.get("diagram") == diagram_ref]
                node_contexts = [str(node.get("context", "")) for node in nodes]
                expected_contexts = {str(ref).upper() for ref in item.get("context_refs", []) or []}
                current_nodes = [node for node in nodes if node.get("current") == "true"]
                if set(node_contexts) != expected_contexts or len(node_contexts) != len(set(node_contexts)):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DIAGRAM-CONTEXT", path,
                        "核心流程图必须逐一映射声明的页面/业务浮层 Context",
                        diagram_ref,
                        affected_consumers=("product", "frontend", "qa"),
                    )
                if len(current_nodes) != 1 or current_nodes[0].get("context") != initial_context:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DIAGRAM-CONTEXT", path,
                        "核心流程图必须唯一高亮当前页面，并与初始 CurrentContext 一致",
                        diagram_ref,
                        affected_consumers=("product", "frontend", "qa"),
                    )
            if any(str(item.get("diagram_type", "")) == "core_flow" for item in diagram_items):
                if "syncReviewDiagramContext" not in scripts or "data-flow-current" not in scripts:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DIAGRAM-CONTEXT", path,
                        "核心流程图缺少随 CurrentContext 更新当前节点高亮的运行时机制",
                        workspace_id,
                        affected_consumers=("product", "frontend", "qa"),
                    )

            example_items = [item for item in document.get("acceptance_examples", []) or [] if isinstance(item, dict)]
            example_refs = [str(item.get("example_ref", "")).upper() for item in example_items]
            dom_examples = {item.get("ref", ""): item for item in projection.acceptance_examples}
            if len(example_refs) != len(set(example_refs)) or len(dom_examples) != len(projection.acceptance_examples) or set(example_refs) != set(dom_examples):
                self.add(
                    "BLOCK", "PROTO-REVIEW-EXECUTABLE-EXAMPLE", path,
                    "声明的少量正反例必须在边界与验收中各出现一次，且不得出现孤儿样例",
                    f"manifest={sorted(set(example_refs))}; dom={sorted(dom_examples)}",
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
            examples_by_context: dict[str, list[dict[str, object]]] = defaultdict(list)
            for item in example_items:
                ref = str(item.get("example_ref", "")).upper()
                context_ref = str(item.get("owner_context_ref", "")).upper()
                examples_by_context[context_ref].append(item)
                dom = dom_examples.get(ref, {})
                if dom and (
                    dom.get("kind") != str(item.get("kind", ""))
                    or dom.get("context") != context_ref
                    or dom.get("acceptance") != str(item.get("acceptance_ref", "")).upper()
                    or dom.get("tab") != "boundary_acceptance"
                ):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-EXECUTABLE-EXAMPLE", path,
                        "正反例必须位于边界与验收，并与 Context、类型和 AC 一致",
                        ref,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                text = projection.acceptance_example_text.get(ref, "")
                for field in ("precondition", "action", "expected_visible_result", "expected_domain_result"):
                    value = str(item.get(field, "") or "")
                    if value and value not in text:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-EXECUTABLE-EXAMPLE", path,
                            "正反例必须把前提、动作、可见结果和业务结果投影为可执行自然语言",
                            f"{ref}/{field}",
                            affected_consumers=("product", "frontend", "backend", "qa"),
                        )
                        break
            for context_ref in sorted(complex_contexts):
                context_examples = examples_by_context.get(context_ref, [])
                kinds = {str(item.get("kind", "")) for item in context_examples}
                if not {"positive", "negative"}.issubset(kinds) or not (2 <= len(context_examples) <= 6):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-EXECUTABLE-EXAMPLE", path,
                        "每个复杂 Context 只保留 2—6 条可直接执行的样例，且至少一正一反",
                        f"{context_ref}: count={len(context_examples)} kinds={sorted(kinds)}",
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
        if str(document.get("contract_revision", "")).upper() in {"RC2", "RC3", "RC4"}:
            legacy_record_ids = sorted(point_id for point_id in point_ids if not point_id.startswith("RVP-"))
            if legacy_record_ids:
                self.add(
                    "BLOCK", "PROTO-REVIEW-TRUTH-ID", path,
                    "RC2—RC4 的评审记录 ID 必须使用 RVP-*，并通过 subject_ref 单独引用业务事实",
                    ", ".join(legacy_record_ids[:8]),
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
        if len(context_ids) != len(set(context_ids)) or len(point_ids) != len(set(point_ids)):
            self.add(
                "BLOCK", "PROTO-REVIEW-DECLARED-DENOMINATOR", path,
                "review_contexts 或 review_points 存在重复稳定 ID，官方分母不唯一", workspace_id,
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )
        if len(candidate_ids) != len(set(candidate_ids)):
            self.add(
                "BLOCK", "PROTO-REVIEW-CANDIDATE-DIFF", path,
                "candidate_review_points 存在重复 candidate_id，防漏结果不可审计", workspace_id,
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )
        if schema_version in {"5.4.8", "5.4.9"} and (
            len(semantic_ids) != len(set(semantic_ids))
            or len(semantic_keys) != len(set(semantic_keys))
        ):
            self.add(
                "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                "页面语义覆盖账本存在重复 coverage_id 或重复 Context/subject，覆盖分母不可审计",
                workspace_id,
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )
        if set(candidate_ids) & set(point_ids):
            self.add(
                "BLOCK", "PROTO-REVIEW-DECLARED-DENOMINATOR", path,
                "Candidate 被复用为正式 ReviewPoint；两者必须物理分离", ", ".join(sorted(set(candidate_ids) & set(point_ids))),
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )
        overlapping_subjects = sorted(set(candidate_subjects) & set(declared_subjects))
        if overlapping_subjects:
            self.add(
                "BLOCK", "PROTO-REVIEW-CANDIDATE-DECLARATION-OVERLAP", path,
                "同一业务事实不能同时保留在 Candidate 与正式 Declaration；确认后必须移出候选集",
                ", ".join(overlapping_subjects[:8]),
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                related_refs=tuple(overlapping_subjects[:50]),
            )
        for item in candidate_items:
            if not item.get("candidate_reason") or item.get("business_status") != "gap":
                self.add(
                    "BLOCK", "PROTO-REVIEW-CANDIDATE-DIFF", path,
                    "Candidate 必须说明高价值发现原因并保持 GAP，禁止静默提升", str(item.get("candidate_id", "missing")),
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
        for point in point_items:
            if point.get("business_status") == "confirmed" and point.get("evidence_origin") in {"prototype_inferred", "assumption"}:
                self.add(
                    "BLOCK", "PROTO-REVIEW-STATUS-AXES", path,
                    "原型反推或假设不能标为已确认，必须保持 GAP/待决并引导产品澄清", str(point.get("ref", "missing")),
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
        if initial_context not in contexts or str(contexts.get(initial_context, {}).get("context_type", "")) != "VIEW":
            self.add(
                "BLOCK", "PROTO-REVIEW-CONTEXT-CONTRACT", path,
                "初始 CurrentContext 必须引用已声明 VIEW", initial_context or "missing",
                affected_consumers=("product", "frontend", "qa"),
            )

        location_surface = re.search(
            r"<[A-Za-z][^>]*\bdata-review-product-location(?:\s*=|\s|>)[^>]*>",
            tag_source,
            re.I | re.S,
        )
        if location_surface is None:
            self.add(
                "BLOCK", "PROTO-PRODUCT-LOCATION-MISMATCH", path,
                "评审工作台缺少只读系统位置表面，冷读者无法判断当前功能从哪个产品入口进入",
                "data-review-product-location",
                affected_consumers=("product", "frontend", "backend", "qa"),
            )

        def static_selector_tags(selector: str) -> list[str]:
            selector = selector.strip()
            id_match = re.fullmatch(r"#([A-Za-z_][\w:.-]*)", selector)
            if id_match:
                value = re.escape(id_match.group(1))
                return [
                    tag for tag in re.findall(r"<[A-Za-z][^>]*>", tag_source, re.S)
                    if re.search(rf"\bid\s*=\s*['\"]{value}['\"]", tag, re.I)
                ]
            attr_match = re.fullmatch(
                r"\[([A-Za-z_:][-\w:.]*)\s*=\s*['\"]([^'\"]+)['\"]\]", selector
            )
            if attr_match:
                name, value = map(re.escape, attr_match.groups())
                return [
                    tag for tag in re.findall(r"<[A-Za-z][^>]*>", tag_source, re.S)
                    if re.search(rf"\b{name}\s*=\s*['\"]{value}['\"]", tag, re.I)
                ]
            return []

        for context_ref, context in contexts.items():
            location = context.get("product_location") or {}
            if not isinstance(location, dict):
                continue
            mode = str(location.get("navigation_mode", ""))
            parent_ref = str(location.get("parent_view_ref", "") or "").upper()
            if mode == "inherit_parent":
                parent = contexts.get(parent_ref)
                if parent is None or str(parent.get("context_type", "")) != "VIEW":
                    self.add(
                        "BLOCK", "PROTO-PRODUCT-LOCATION-MISMATCH", path,
                        "业务浮层必须继承一个已声明 VIEW 的产品位置", f"{context_ref}->{parent_ref or 'missing'}",
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                else:
                    parent_location = parent.get("product_location") or {}
                    if isinstance(parent_location, dict):
                        inherited_fields = ("menu_path", "active_entry_selector")
                        drift = [
                            field for field in inherited_fields
                            if location.get(field) != parent_location.get(field)
                        ]
                        if drift:
                            self.add(
                                "BLOCK", "PROTO-PRODUCT-LOCATION-MISMATCH", path,
                                "业务浮层必须继承父 VIEW 的菜单路径；无菜单父页面也必须继承其空路径与豁免位置",
                                f"{context_ref}->{parent_ref}: {', '.join(drift)}",
                                affected_consumers=("product", "frontend", "backend", "qa"),
                            )
            elif mode == "inherit_invoker":
                if str(context.get("context_type", "")) == "VIEW" or parent_ref:
                    self.add(
                        "BLOCK", "PROTO-PRODUCT-LOCATION-MISMATCH", path,
                        "inherit_invoker 只适用于可从多个 VIEW 打开的业务浮层，且不得伪造固定 parent_view_ref", context_ref,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
            if mode != "menu_bound":
                continue
            selector = str(location.get("active_entry_selector", "") or "")
            matches = static_selector_tags(selector)
            if len(matches) > 1:
                self.add(
                    "BLOCK", "PROTO-PRODUCT-LOCATION-MISMATCH", path,
                    "活动菜单入口选择器在产品 DOM 中不唯一", f"{context_ref}/{selector}: {len(matches)}",
                    affected_consumers=("product", "frontend", "qa"),
                )
            if context_ref != initial_context or len(matches) != 1:
                continue
            tag = matches[0]
            active = bool(
                re.search(r"\bclass\s*=\s*['\"][^'\"]*\bactive\b", tag, re.I)
                or re.search(r"\baria-current\s*=\s*['\"](?:page|true)['\"]", tag, re.I)
                or re.search(r"\bdata-active\s*=\s*['\"]true['\"]", tag, re.I)
            )
            if not active or re.search(r"\bdisabled(?:\s|=|>)", tag, re.I):
                self.add(
                    "BLOCK", "PROTO-PRODUCT-LOCATION-MISMATCH", path,
                    "初始 VIEW 的真实产品菜单未唯一高亮，或入口被错误禁用", f"{context_ref}/{selector}",
                    affected_consumers=("product", "frontend", "qa"),
                )

        declared_order: dict[str, tuple[str, int]] = {}
        for context_ref, context in contexts.items():
            refs = [str(item).upper() for item in context.get("review_point_refs", []) or []]
            for number, point_ref in enumerate(refs, start=1):
                if point_ref in declared_order:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DECLARED-DENOMINATOR", path,
                        "同一评审点被多个 Context 或同一 Context 重复声明", point_ref,
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
                declared_order[point_ref] = (context_ref, number)
                point = points.get(point_ref)
                if point is None or str(point.get("owner_context_ref", "")).upper() != context_ref:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-POINT-COVERAGE", path,
                        "Context 的有序评审点与 ReviewPoint.owner_context_ref 不一致", f"{context_ref}->{point_ref}",
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
        for orphan in sorted(set(points) - set(declared_order)):
            self.add(
                "BLOCK", "PROTO-REVIEW-POINT-COVERAGE", path,
                "ReviewPoint 没有进入任何 review_contexts 官方分母", orphan,
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )

        if schema_version in {"5.4.8", "5.4.9"}:
            page_contracts = self._page_contracts(raw)
            semantic_by_context: dict[str, list[dict[str, object]]] = defaultdict(list)
            for item in semantic_items:
                semantic_by_context[str(item.get("owner_context_ref", "")).upper()].append(item)

            candidate_semantic_overlap = sorted(set(candidate_subjects) & {item[1] for item in semantic_keys})
            if candidate_semantic_overlap:
                self.add(
                    "BLOCK", "PROTO-REVIEW-CANDIDATE-DECLARATION-OVERLAP", path,
                    "同一业务语义不能同时存在于 Candidate 与正式语义覆盖账本",
                    ", ".join(candidate_semantic_overlap[:8]),
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    related_refs=tuple(candidate_semantic_overlap[:50]),
                )

            for context_ref, context in contexts.items():
                context_type = str(context.get("context_type", ""))
                surface_types = {str(item) for item in context.get("surface_types", []) or []}
                secondary_refs = {str(item).upper() for item in context.get("secondary_context_refs", []) or []}
                context_semantics = semantic_by_context.get(context_ref, [])
                semantic_types = {str(item.get("semantic_type", "")) for item in context_semantics}

                for secondary_ref in sorted(secondary_refs):
                    secondary = contexts.get(secondary_ref)
                    if secondary is None or str(secondary.get("context_type", "")) == "VIEW":
                        self.add(
                            "BLOCK", "PROTO-REVIEW-OVERLAY-UNCOVERED", path,
                            "secondary_context_refs 必须引用已声明的业务弹窗、抽屉或气泡 Context",
                            f"{context_ref}->{secondary_ref}",
                            affected_consumers=("product", "frontend", "backend", "qa"),
                        )
                        continue
                    location = secondary.get("product_location") or {}
                    if (
                        isinstance(location, dict)
                        and str(location.get("navigation_mode", "")) == "inherit_parent"
                        and str(location.get("parent_view_ref", "")).upper() != context_ref
                    ):
                        self.add(
                            "BLOCK", "PROTO-REVIEW-OVERLAY-UNCOVERED", path,
                            "二级业务 Context 的父页面与声明入口不一致",
                            f"{context_ref}->{secondary_ref}",
                            affected_consumers=("product", "frontend", "backend", "qa"),
                        )

                if context_type != "VIEW":
                    continue
                page_contract = page_contracts.get(context_ref)
                if page_contract is None:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-PAGE-CONTRACT-MISSING", path,
                        "5.4.8 起的每个评审 VIEW 必须有 PAGE-CONTRACT，避免模型从页面外观缩减功能分母",
                        context_ref,
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
                else:
                    attrs, _ = page_contract
                    declared_surfaces = {
                        item.strip()
                        for item in re.split(r"[,|]", attrs.get("surfaces", ""))
                        if item.strip()
                    }
                    if declared_surfaces != surface_types:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-PAGE-CONTRACT-MISMATCH", path,
                            "评审 Context 的 surface_types 必须与 PAGE-CONTRACT 完全一致",
                            f"{context_ref}: page={sorted(declared_surfaces)} manifest={sorted(surface_types)}",
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        )
                if "metrics" in surface_types and "metric" not in semantic_types:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-METRIC-UNCOVERED", path,
                        "页面声明了指标表面，却没有任何逐项指标语义说明",
                        context_ref,
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
                if "metrics" in surface_types:
                    visible_metric_refs = {
                        ref for ref in projection.visible_targets.get(context_ref, {})
                        if ref.startswith("METRIC-")
                    }
                    semantic_metric_refs = {
                        str(item.get("subject_ref", "")).upper()
                        for item in context_semantics
                        if str(item.get("semantic_type", "")) == "metric"
                        and str(item.get("coverage_status", "")) != "not_applicable"
                    }
                    missing_metric_refs = sorted(visible_metric_refs - semantic_metric_refs)
                    ungrounded_metric_refs = sorted(
                        ref for ref in visible_metric_refs
                        if not any(
                            str(item.get("subject_ref", "")).upper() == ref
                            and bool(item.get("ui_grounded"))
                            and str(item.get("target_ref", "")).upper() == ref
                            for item in context_semantics
                        )
                    )
                    if missing_metric_refs or ungrounded_metric_refs or projection.unbound_metric_like[context_ref]:
                        detail = ", ".join(missing_metric_refs[:8]) or f"unbound_metric_cards={projection.unbound_metric_like[context_ref]}"
                        if not missing_metric_refs and ungrounded_metric_refs:
                            detail = "missing_metric_marker=" + ", ".join(ungrounded_metric_refs[:8])
                        self.add(
                            "BLOCK", "PROTO-REVIEW-METRIC-UNCOVERED", path,
                            "每个可见指标卡都必须有唯一 METRIC-* 并逐项进入语义覆盖账本",
                            f"{context_ref}: {detail}",
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                            related_refs=tuple(missing_metric_refs[:50]),
                        )
                if "workflow" in surface_types and "state_transition" not in semantic_types:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-STATE-PATH-UNCOVERED", path,
                        "工作流/看板页面必须说明允许状态流转、守卫和非法路径",
                        context_ref,
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
                if "drawer_form" in surface_types and not secondary_refs:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-OVERLAY-UNCOVERED", path,
                        "页面包含抽屉表单却没有声明二级业务 Context",
                        context_ref,
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )

            semantic_surface_counts = Counter(item["ref"] for item in projection.semantic_surfaces)
            semantic_surfaces = {item["ref"]: item for item in projection.semantic_surfaces}
            for item in semantic_items:
                coverage_id = str(item.get("coverage_id", "")).upper()
                subject_ref = str(item.get("subject_ref", "")).upper()
                context_ref = str(item.get("owner_context_ref", "")).upper()
                semantic_type = str(item.get("semantic_type", ""))
                status = str(item.get("coverage_status", ""))
                criticality = str(item.get("criticality", ""))
                mapped_points = [str(ref).upper() for ref in item.get("review_point_refs", []) or []]
                human_summary = str(item.get("human_summary", "") or "")
                target_ref = str(item.get("target_ref", "") or "").upper()

                if context_ref not in contexts:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                        "语义覆盖项引用了未声明 CurrentContext", f"{coverage_id}->{context_ref or 'missing'}",
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
                for point_ref in mapped_points:
                    point = points.get(point_ref)
                    if point is None or str(point.get("owner_context_ref", "")).upper() != context_ref:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                            "语义覆盖项必须映射到同一 Context 内的正式 ReviewPoint",
                            f"{coverage_id}->{point_ref}",
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        )
                    elif status == "gap" and str(point.get("business_status", "")) not in {"gap", "pending_decision"}:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                            "开放语义缺口不能映射到已确认 ReviewPoint",
                            f"{coverage_id}->{point_ref}",
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        )
                    elif status == "covered" and str(point.get("business_status", "")) != "confirmed":
                        self.add(
                            "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                            "已覆盖语义项必须映射到已确认 ReviewPoint；待决内容应保持 gap",
                            f"{coverage_id}->{point_ref}",
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        )
                if status in {"covered", "gap"}:
                    if semantic_surface_counts[coverage_id] != 1:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                            "每个适用语义项必须在右侧恰好出现一次最小说明",
                            f"{coverage_id}: {semantic_surface_counts[coverage_id]}",
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        )
                    else:
                        surface = semantic_surfaces[coverage_id]
                        if surface.get("context") != context_ref or surface.get("owner") != str(item.get("detail_owner", "")):
                            self.add(
                                "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                                "语义说明必须位于声明的 CurrentContext 和唯一责任页签",
                                coverage_id,
                                affected_consumers=("product", "frontend", "backend", "qa"),
                            )
                        if human_summary and human_summary not in projection.semantic_text.get(coverage_id, ""):
                            self.add(
                                "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                                "语义说明只存在于 manifest，未在人类可见右栏呈现",
                                coverage_id,
                                affected_consumers=("product", "frontend", "backend", "qa"),
                            )
                    if bool(item.get("ui_grounded")):
                        grounded = any(
                            str(points.get(point_ref, {}).get("target_ref", "")).upper() == target_ref
                            and bool(points.get(point_ref, {}).get("marker_required"))
                            for point_ref in mapped_points
                        )
                        if not grounded:
                            self.add(
                                "BLOCK", "PROTO-REVIEW-MARKER-REQUIRED", path,
                                "有 UI 落点的语义项必须映射到同目标 marker，不能只在右栏说明",
                                f"{coverage_id}/{target_ref or 'missing'}",
                                affected_consumers=("product", "frontend", "qa", "coding_agent"),
                            )
                elif semantic_surface_counts[coverage_id]:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                        "not_applicable 语义项不得占用人类评审面板",
                        coverage_id,
                        affected_consumers=("product", "frontend", "qa"),
                    )

                if semantic_type == "metric" and not subject_ref.startswith("METRIC-"):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-METRIC-UNCOVERED", path,
                        "指标语义项必须引用真实 METRIC-* 口径，不得用泛化区域代替",
                        f"{coverage_id}/{subject_ref}",
                        affected_consumers=("product", "backend", "qa", "coding_agent"),
                    )
                if status == "gap":
                    severity = "BLOCK" if criticality in {"P0", "P1"} else "GAP"
                    self.add(
                        severity, "PROTO-REVIEW-SEMANTIC-COVERAGE", path,
                        "关键实现/验收语义仍未关闭，不能以结构完整替代业务完整",
                        f"{coverage_id}/{criticality}",
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        related_refs=tuple(filter(None, (coverage_id, subject_ref, str(item.get("unknown_ref", "") or "")))),
                    )

            for overlay in projection.product_overlays:
                if not overlay.get("declared_context"):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-OVERLAY-UNCOVERED", path,
                        "发现业务弹窗/抽屉但没有独立 CurrentContext；二级功能无法被研发和测试冷读",
                        overlay.get("testid", "role=dialog"),
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )

        if projection.context_roots[initial_context] != 1:
            self.add(
                "BLOCK", "PROTO-REVIEW-CONTEXT-CONTRACT", path,
                "初始 CurrentContextRoot 必须在产品 DOM 中恰好存在一次", initial_context,
                affected_consumers=("frontend", "qa"),
            )
        for context_ref in sorted(set(contexts) - {initial_context}):
            if projection.context_roots[context_ref] > 1:
                self.add(
                    "BLOCK", "PROTO-REVIEW-CONTEXT-CONTRACT", path,
                    "业务浮层 ContextRoot 在静态 DOM 中重复，最上层解析可能歧义", context_ref,
                    affected_consumers=("frontend", "qa"),
                )
            elif projection.context_roots[context_ref] == 0:
                self.add(
                    "GAP", "PROTO-REVIEW-OVERLAY-DETECTION", path,
                    "动态业务浮层未在静态 DOM 中出现，必须由浏览器 ARUN 证明 Context Event、探测与回退", context_ref,
                    affected_consumers=("frontend", "qa"),
                )

        overlay_signatures: Counter[tuple[str, str, int]] = Counter()
        for context_ref, context in contexts.items():
            detection = context.get("detection") or {}
            if not isinstance(detection, dict):
                continue
            signature = (
                str(detection.get("type", "")), str(detection.get("target", "")),
                int(detection.get("overlay_priority", 0)),
            )
            if str(context.get("context_type", "")) != "VIEW":
                overlay_signatures[signature] += 1
        for signature, count in overlay_signatures.items():
            if count > 1:
                self.add(
                    "BLOCK", "PROTO-REVIEW-OVERLAY-DETECTION", path,
                    "多个业务浮层使用相同探测目标与优先级，无法确定 topmost Context", str(signature),
                    affected_consumers=("frontend", "qa"),
                )

        visible_tabs = [item.casefold() for item in re.findall(r"\bdata-review-tab\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)]
        tab_targets = {item.casefold() for item in re.findall(r"\bdata-review-tab-target\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)}
        required_tabs = {"overview", "function_flow", "boundary_acceptance"}
        if review_level in {"R1", "R2"}:
            if Counter(visible_tabs) != Counter({item: 1 for item in required_tabs}) or tab_targets != required_tabs:
                self.add(
                    "BLOCK", "PROTO-REVIEW-LEVEL", path,
                    "R1/R2 必须且只能呈现总览、功能与流转、边界与验收三个可达一级页签", ", ".join(visible_tabs),
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
        elif set(visible_tabs) - required_tabs or tab_targets - required_tabs:
            self.add(
                "BLOCK", "PROTO-REVIEW-LEVEL", path,
                "R0 即使呈现页签也不得增加 Journey/STEP/Page/Role 导航", ", ".join(visible_tabs),
                affected_consumers=("product", "frontend", "backend", "qa"),
            )

        ownership = {
            "overview": {"background_problem", "goals_success", "roles", "scope", "main_chain", "core_flow_diagram", "change_summary", "risk_summary"},
            "function_flow": {"current_context", "business_duty", "upstream_downstream", "review_points", "visible_domain_results", "data_event_summary"},
            "boundary_acceptance": {"rules", "permissions", "state_machines", "data_flow_diagram", "metric_calculations", "exceptions_recovery", "acceptance_tests", "acceptance_examples", "open_items"},
        }
        owner_counts = Counter(item[0] for item in projection.content_owners)
        for content, owner in projection.content_owners:
            if owner not in ownership or content not in ownership[owner]:
                self.add(
                    "BLOCK", "PROTO-REVIEW-TAB-OWNERSHIP", path,
                    "评审内容进入了错误页签或没有唯一 owner", f"{content}->{owner or 'missing'}",
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
        for duplicate, count in owner_counts.items():
            if count > 1:
                self.add(
                    "BLOCK", "PROTO-REVIEW-TAB-OWNERSHIP", path,
                    "同一完整内容域在多个位置重复，形成第二份可修改事实", duplicate,
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
        if review_level in {"R1", "R2"}:
            minimum_content = {
                "goals_success", "scope", "main_chain", "current_context",
                "review_points", "visible_domain_results", "rules", "acceptance_tests", "open_items",
            }
            if schema_version in {"5.4.8", "5.4.9"}:
                semantic_types = {str(item.get("semantic_type", "")) for item in semantic_items}
                if "metric" in semantic_types:
                    minimum_content.add("metric_calculations")
                if "state_transition" in semantic_types:
                    minimum_content.add("state_machines")
                if "permission_guard" in semantic_types:
                    minimum_content.add("permissions")
                if "error_recovery" in semantic_types:
                    minimum_content.add("exceptions_recovery")
            for missing in sorted(minimum_content - set(owner_counts)):
                self.add(
                    "BLOCK", "PROTO-REVIEW-TAB-OWNERSHIP", path,
                    "三页签缺少最小人类冷读内容域", missing,
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )

        marker_counts = Counter(item["ref"] for item in projection.markers)
        card_counts = Counter(item["ref"] for item in projection.cards)
        for extra in sorted((set(marker_counts) | set(card_counts)) - set(points)):
            self.add(
                "BLOCK", "PROTO-REVIEW-POINT-COVERAGE", path,
                "DOM 中出现未由 review_contexts 声明的官方 marker/card", extra,
                affected_consumers=("product", "frontend", "qa"),
            )
        for point_ref, point in points.items():
            context_ref, expected_number = declared_order.get(point_ref, ("", 0))
            marker_required = bool(point.get("marker_required"))
            target_selector = str(point.get("target_selector", "") or "")
            subject_ref = str(point.get("subject_ref", "") or "").upper()
            visible_subject_count = projection.visible_targets[context_ref][subject_ref]
            if not marker_required and (target_selector or visible_subject_count > 0):
                self.add(
                    "BLOCK", "PROTO-REVIEW-MARKER-REQUIRED", path,
                    "已有可见 UI 目标的正式评审点不得只在右栏编号，必须在产品目标旁显示同号 marker",
                    point_ref,
                    affected_consumers=("product", "frontend", "qa", "coding_agent"),
                    related_refs=(point_ref,),
                )
            expected_marker_count = 1 if marker_required else 0
            if marker_counts[point_ref] != expected_marker_count or card_counts[point_ref] != 1:
                self.add(
                    "BLOCK", "PROTO-REVIEW-POINT-COVERAGE", path,
                    "每个声明评审点必须有一张卡；需要 UI 落点时还必须恰好一个 marker", point_ref,
                    affected_consumers=("product", "frontend", "qa", "coding_agent"),
                )
            for item in [*([marker for marker in projection.markers if marker["ref"] == point_ref]), *([card for card in projection.cards if card["ref"] == point_ref])]:
                if item.get("context") != context_ref or item.get("number") != str(expected_number):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-CONTEXT-NUMBERING", path,
                        "marker/card 必须按当前 Context 的声明顺序从 1 编号", f"{point_ref}: {item.get('context')}/{item.get('number')}",
                        affected_consumers=("product", "frontend", "qa"),
                    )
            card = next((item for item in projection.cards if item["ref"] == point_ref), {})
            for key in ("business_status", "verification_status", "evidence_origin"):
                if card.get(key) != str(point.get(key, "")).casefold():
                    self.add(
                        "BLOCK", "PROTO-REVIEW-STATUS-AXES", path,
                        "ReviewPoint 卡片未同步显示业务状态、验证状态和证据来源", f"{point_ref}/{key}",
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
            card_text = projection.card_text.get(point_ref, "")
            for visible_value in (str(point.get("title", "")), str(point.get("summary", ""))):
                if visible_value and visible_value not in card_text:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-POINT-COVERAGE", path,
                        "ReviewPoint 的标题或连贯业务摘要只在 manifest 中存在，未在人类卡片可见", point_ref,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                    break
            target_ref = str(point.get("target_ref", "") or "").upper()
            if marker_required and target_ref:
                visible_count = projection.visible_targets[context_ref][target_ref]
                total_count = projection.targets[context_ref][target_ref]
                if context_ref == initial_context and visible_count != 1:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-TARGET-RESOLUTION", path,
                        "初始 CurrentContext 内 marker 目标必须当前可见且恰好一个", f"{context_ref}/{target_ref}: {visible_count}",
                        affected_consumers=("frontend", "qa"), related_refs=(point_ref, target_ref),
                    )
                elif total_count > 1:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-TARGET-RESOLUTION", path,
                        "同一 Context 内目标锚点不唯一，禁止取全局第一个节点", f"{context_ref}/{target_ref}: {total_count}",
                        affected_consumers=("frontend", "qa"), related_refs=(point_ref, target_ref),
                    )

        declared_targets = {
            str(point.get("target_ref", "")).upper()
            for point in point_items if point.get("target_ref")
        }
        candidate_gap_refs: set[str] = set()
        candidate_block_refs: set[str] = set()
        high_risk_action = re.compile(r"(?:SUBMIT|SAVE|DELETE|REMOVE|APPROVE|REJECT|PUBLISH|UPLOAD|IMPORT|SYNC|SEND|ASSIGN|CLOSE|CANCEL|REVOKE|PAY|REFUND)")
        for context_ref, target_counts in projection.targets.items():
            for target_ref in target_counts:
                if target_ref in declared_targets or target_ref in candidate_subjects or target_ref.startswith("VIEW-"):
                    continue
                if target_ref.startswith(("METRIC-", "STATE-")) or (target_ref.startswith("ACT-") and high_risk_action.search(target_ref)):
                    candidate_block_refs.add(target_ref)
                elif target_ref.startswith(("ACT-", "FLD-", "REG-")):
                    candidate_gap_refs.add(target_ref)
        for ref in sorted(candidate_block_refs):
            self.add(
                "BLOCK", "PROTO-REVIEW-CANDIDATE-DIFF", path,
                "高风险 Candidate 未进入声明评审点；门禁只报告，不自动改变官方分母", ref,
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"), related_refs=(ref,),
            )
        for ref in sorted(candidate_gap_refs - candidate_block_refs):
            self.add(
                "GAP", "PROTO-REVIEW-CANDIDATE-DIFF", path,
                "稳定业务锚点未进入声明评审点，请人工确认是遗漏还是有依据的不适用", ref,
                affected_consumers=("product", "frontend", "backend", "qa"), related_refs=(ref,),
            )

        event_name = str((document.get("context_contract") or {}).get("product_context_event", "")) if isinstance(document.get("context_contract"), dict) else ""
        runtime_contracts = {
            "PROTO-PRODUCT-LOCATION-MISMATCH": (
                "resolveProductLocation" in scripts
                and "syncProductLocation" in scripts
                and all(item in scripts for item in ("observed", "expected", "diff"))
                and "active_menu_path" in scripts
                and "expanded_menu_ancestors" in scripts
            ),
            "PROTO-REVIEW-PRODUCT-FINGERPRINT-INVARIANT": (
                scripts.count("captureProductFingerprint") >= 3
                and "captureReviewFingerprint" in scripts
                and "assertProductFingerprintInvariant" in scripts
                and "runReviewAction" in scripts
                and "__ADS_REVIEW_GATE__" in scripts
                and "PROTO-REVIEW-PRODUCT-FINGERPRINT-INVARIANT" in scripts
            ),
            "PROTO-REVIEW-OVERLAY-DETECTION": (
                bool(event_name and event_name in scripts and re.search(r"addEventListener", scripts))
                and "MutationObserver" in scripts and "resolveCurrentContext" in scripts
                and "PROTO-REVIEW-OVERLAY-UNDECLARED" in scripts
            ),
            "PROTO-REVIEW-TARGET-RESOLUTION": (
                ("targetFor" in scripts or "resolveReviewTarget" in scripts)
                and "currentContextRoot" in scripts and "querySelectorAll" in scripts
                and ("isTargetVisible" in scripts or "visible" in scripts)
                and "nodes.length===0" in scripts and "nodes.length>1" in scripts
                and "PROTO-REVIEW-TARGET-UNRESOLVED" in scripts
                and "PROTO-REVIEW-TARGET-AMBIGUOUS" in scripts
            ),
            "PROTO-REVIEW-SELECTION-NOT-SYNCED": (
                "data-review-target-selected" in scripts
                and "aria-current" in scripts
                and ("focusReviewTarget" in scripts or "highlightReviewTarget" in scripts)
                and bool(re.search(
                    r"\[\s*data-review-target-selected\s*=\s*['\"]?true['\"]?\s*\][^{]*\{[^}]*(?:outline|box-shadow)\s*:",
                    raw, re.I | re.S,
                ))
            ),
            "PROTO-REVIEW-SHARE-LOCATOR": (
                bool(re.search(r"URLSearchParams|location\.hash", scripts))
                and all(item in scripts for item in ("baseline_ref", "context_ref", "review_point_ref", "active_tab"))
                and "hydrateLocator" in scripts
            ),
            "PROTO-REVIEW-RECORD-PERSISTENCE": (
                "localStorage" in scripts and "JSON.stringify" in scripts and "JSON.parse" in scripts
            ),
        }
        for code, passed in runtime_contracts.items():
            if not passed:
                self.add(
                    "BLOCK", code, path,
                    "Final 评审运行时缺少可静态发现的必要机制；仍需浏览器 ARUN 证明真实行为", workspace_id,
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )

        review_actions = {
            item.upper() for item in re.findall(r"\bdata-action\s*=\s*['\"](UIACT-REVIEW-[A-Z0-9-]+)['\"]", tag_source, re.I)
        }
        required_actions = {
            "UIACT-REVIEW-SELECT", "UIACT-REVIEW-TOGGLE", "UIACT-REVIEW-SHARE",
            "UIACT-REVIEW-RECORD", "UIACT-REVIEW-EXPORT", "UIACT-REVIEW-IMPORT",
        }
        if review_level in {"R1", "R2"}:
            required_actions |= {"UIACT-REVIEW-TAB", "UIACT-REVIEW-COMPACT"}
        missing_actions = sorted(required_actions - review_actions)
        if missing_actions:
            self.add(
                "BLOCK", "PROTO-REVIEW-LEVEL", path,
                "评审工作台缺少必要的纯评审动作入口", ", ".join(missing_actions),
                affected_consumers=("product", "frontend", "qa"),
            )
        expand_button = re.search(
            r"<button[^>]*data-action\s*=\s*['\"]UIACT-REVIEW-TOGGLE['\"][^>]*data-ads-act\s*=\s*['\"]expand['\"][^>]*>",
            tag_source, re.I | re.S,
        ) or re.search(
            r"<button[^>]*data-ads-act\s*=\s*['\"]expand['\"][^>]*data-action\s*=\s*['\"]UIACT-REVIEW-TOGGLE['\"][^>]*>",
            tag_source, re.I | re.S,
        )
        if not expand_button or "ads-collapsed" not in scripts or "UIACT-REVIEW-TOGGLE" not in scripts:
            self.add(
                "BLOCK", "PROTO-REVIEW-COLLAPSE-ROUNDTRIP", path,
                "评审栏必须使用可操作按钮完成收起→展开往返，不能收起后失去入口", workspace_id,
                affected_consumers=("product", "frontend", "qa"),
            )

        progress_tag = next((tag for tag in re.findall(r"<[A-Za-z][^>]*>", tag_source, re.S) if re.search(r"\bdata-review-progress(?:\s*=|\s|>)", tag, re.I)), "")
        denominator_match = re.search(r"\bdata-review-progress-denominator\s*=\s*['\"](\d+)['\"]", progress_tag, re.I)
        if not denominator_match or int(denominator_match.group(1)) != len(points):
            self.add(
                "BLOCK", "PROTO-REVIEW-PROGRESS-DENOMINATOR", path,
                "可见评审进度分母必须等于全部适用的声明 ReviewPoint，浏览不改变分母", f"expected={len(points)}",
                affected_consumers=("product", "frontend", "qa"),
            )
        for attribute in ("data-review-share-locator", "data-review-records"):
            if not re.search(rf"\b{re.escape(attribute)}(?:\s*=|\s|>)", tag_source, re.I):
                self.add(
                    "BLOCK", "PROTO-REVIEW-SHARE-LOCATOR" if "share" in attribute else "PROTO-REVIEW-RECORD-PERSISTENCE",
                    path, "评审工作台缺少可见的分享定位或评审记录表面", attribute,
                    affected_consumers=("product", "frontend", "qa"),
                )

        if re.search(r"\[data-review-workspace\][^{]*\{[^}]*position\s*:\s*fixed", raw, re.I | re.S) or re.search(r"data-review-workspace[^>]*style\s*=\s*['\"][^'\"]*position\s*:\s*fixed", tag_source, re.I):
            self.add(
                "BLOCK", "PROTO-REVIEW-LAYOUT-NONOVERLAP", path,
                "桌面评审区使用 fixed 覆盖产品主区，违反 participate_in_layout", workspace_id,
                affected_consumers=("product", "frontend", "qa"),
            )

        cold_read = document.get("cold_read_contract") or {}
        if isinstance(cold_read, dict) and str(cold_read.get("status", "")) == "passed" and not cold_read.get("evidence_refs"):
            self.add(
                "BLOCK", "PROTO-REVIEW-COLD-READ", path,
                "冷读通过必须绑定未参与者证据，不能由生成者或模型自报", workspace_id,
                affected_consumers=("product", "frontend", "backend", "qa"),
            )

        declared_unknowns = {str(item).upper() for item in document.get("unknown_refs", []) or []}
        referenced_unknowns: set[str] = set()
        for item in semantic_items:
            unknown_ref = str(item.get("unknown_ref", "") or "").upper()
            if unknown_ref:
                referenced_unknowns.add(unknown_ref)
        for point in point_items:
            point_unknowns: set[str] = set()
            for key in ("precondition_refs", "boundary_refs", "source_refs"):
                point_unknowns.update(
                    str(item).upper() for item in point.get(key, []) or []
                    if str(item).upper().startswith("UNK-")
                )
            referenced_unknowns.update(point_unknowns)
            if str(point.get("business_status", "")) in {"pending_decision", "gap"} and not point_unknowns:
                self.add(
                    "BLOCK", "PROTO-REVIEW-POINT-COVERAGE", path,
                    "未决定或 GAP ReviewPoint 必须绑定可关闭 UNK-*", str(point.get("ref", "")),
                    affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                )
        handoff = document.get("machine_handoff") or {}
        if isinstance(handoff, dict):
            referenced_unknowns.update(str(item).upper() for item in handoff.get("gap_refs", []) or [])
        for missing in sorted(referenced_unknowns - declared_unknowns):
            self.add(
                "BLOCK", "PROTO-REVIEW-POINT-COVERAGE", path,
                "ReviewPoint 或 handoff 引用的 UNK-* 未进入工作台未知项索引", missing,
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )

        return {
            str(point.get("target_ref", "")).upper()
            for point in point_items
            if point.get("marker_required") and point.get("target_ref")
        }

    def check_prototype(self, path: Path, level: str) -> None:
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "PROTO-READ", path, f"prototype cannot be read: {exc}")
            return
        # Restrict attribute discovery to actual HTML-like opening tags. Raw
        # regex over the whole document also matches JavaScript selectors such
        # as `[data-testid="page-X"]` and falsely reports duplicate pages.
        tag_source = self._tag_source(raw)
        visible_source = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->", " ", raw, flags=re.I | re.S)
        malformed_comparisons = re.findall(r"<[A-Za-z][A-Za-z0-9_-]*(?=[≤≥，。；：<])[^>]*>", visible_source)
        for fragment in malformed_comparisons[:5]:
            self.add(
                "BLOCK", "PROTO-VISIBLE-COMPARISON-UNESCAPED", path,
                "可见规则中的比较符被浏览器解析为 HTML 标签，公式或字段约束会吞字",
                fragment[:160],
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
            )
        polluted_classes = []
        for class_value in re.findall(r"\bclass\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I):
            for token in re.split(r"\s+", class_value):
                if re.match(r"(?:sev|priority|status)-", token, re.I) and len(token) > 32:
                    polluted_classes.append(token)
        for token in polluted_classes[:10]:
            self.add(
                "BLOCK", "PROTO-DYNAMIC-CLASS-POLLUTION", path,
                "业务描述被插入语义 class，可能破坏 CSS、选择器和 DOM 安全边界",
                token[:160],
                affected_consumers=("frontend", "qa", "coding_agent"),
            )
        visible_lowered = _visible_text(raw).lower()
        for term in scaffolding_terms():
            if term.lower() in visible_lowered:
                self.add(
                    "BLOCK", "PROTO-DEMO-SCAFFOLDING-VISIBLE", path,
                    "可见文本残留验收演示脚手架，客户会误读为产品功能", term,
                    affected_consumers=("product", "ux", "qa", "customer_acceptor"),
                )
        for iframe in re.findall(r"<iframe\b[^>]*>", raw, re.I | re.S):
            src_match = re.search(r"\bsrc\s*=\s*['\"]([^'\"]+)['\"]", iframe, re.I)
            if not src_match:
                continue
            src = src_match.group(1)
            parsed = urlsplit(src)
            if parsed.scheme.casefold() in {"javascript", "data", "file"}:
                self.add(
                    "BLOCK", "PROTO-IFRAME-UNSAFE-SCHEME", path,
                    "iframe 使用不可审计或可执行的高风险 URL scheme", src,
                    affected_consumers=("security", "frontend", "qa", "coding_agent"),
                )
                continue
            is_remote = bool(parsed.netloc and parsed.scheme.casefold() in {"", "http", "https"})
            if is_remote:
                if parsed.scheme.casefold() in {"", "http"}:
                    self.add(
                        "BLOCK", "PROTO-INSECURE-REMOTE-IFRAME", path,
                        "远程 iframe 使用明文 HTTP，内容和凭据边界不可接受", src,
                        affected_consumers=("security", "frontend", "qa", "coding_agent"),
                    )
                    continue
                required_attributes = {
                    "data-integration-ref": r"\bdata-integration-ref\s*=\s*['\"]INT-[A-Z0-9-]+['\"]",
                    "data-fallback": r"\bdata-fallback\s*=\s*['\"][^'\"]+['\"]",
                    "title": r"\btitle\s*=\s*['\"][^'\"]+['\"]",
                    "sandbox": r"\bsandbox(?:\s*=\s*['\"][^'\"]*['\"])?",
                    "referrerpolicy": r"\breferrerpolicy\s*=\s*['\"][^'\"]+['\"]",
                }
                missing = [name for name, pattern in required_attributes.items() if not re.search(pattern, iframe, re.I)]
                if missing:
                    severity = "BLOCK" if level in {"L2", "L3", "L4"} else "GAP"
                    self.add(
                        severity, "PROTO-REMOTE-IFRAME-UNDECLARED", path,
                        "远程 iframe 未声明集成归属、降级路径和浏览器安全边界",
                        f"{src}; missing={','.join(missing)}",
                        affected_consumers=("product", "architect", "security", "frontend", "qa", "coding_agent"),
                    )
                else:
                    self.add(
                        "GAP", "PROTO-REMOTE-IFRAME-UNVERIFIED", path,
                        "远程 iframe 已声明静态合同，但内容、登录态、网络可达性和运行时交互仍需浏览器证据",
                        src,
                        affected_consumers=("product", "frontend", "qa", "customer_acceptor"),
                    )
                continue
            if parsed.path.lower().endswith(".html"):
                self.add(
                    "BLOCK", "PROTO-NESTED-PRODUCT-IFRAME", path,
                    "原型用本地 iframe 嵌套另一个产品页面，嵌套页交互合同不可静态证明", src,
                    affected_consumers=("frontend", "qa", "coding_agent"),
                )
        testids = re.findall(r"\bdata-testid\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)
        action_values = set(re.findall(r"\bdata-action\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I))
        unstable_action_values = sorted(item for item in action_values if re.search(r"\$\{|\{\{|<%", item))
        actions = sorted(action_values - set(unstable_action_values))
        states = sorted(set(re.findall(r"\bdata-state\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        fields = sorted(set(re.findall(r"\bdata-(?:field|bind)\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        metric_bindings = _metric_bindings(raw)
        metric_ids = [item[0] for item in metric_bindings]
        metrics = sorted(set(metric_ids or re.findall(r"\bdata-metric\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        acceptance_refs = sorted(set(re.findall(r"\bdata-ac\s*=\s*['\"](AC-[A-Z0-9-]+)['\"]", tag_source, re.I)))
        page_testids = [item for item in testids if item.lower().startswith("page-")]
        region_testids = [item for item in testids if item.lower().startswith("region-")]
        self.prototype_acceptance_refs.update(item.upper() for item in acceptance_refs)
        if not page_testids:
            self.add("BLOCK" if actions or level in {"L2", "L3", "L4"} else "GAP", "PROTO-NO-PAGE-ANCHOR", path, "no page-* data-testid root was found")
        for duplicate in sorted(item for item, count in Counter(testids).items() if count > 1 and item.lower().startswith("page-")):
            self.add("BLOCK", "PROTO-DUPLICATE-PAGE", path, "page data-testid must be unique", duplicate)
        for duplicate in sorted(item for item, count in Counter(testids).items() if count > 1 and item.lower().startswith("region-")):
            self.add("BLOCK", "PROTO-DUPLICATE-REGION", path, "region data-testid must be unique", duplicate)
        if level in {"L2", "L3", "L4"}:
            for action in actions:
                # UIACT-* marks pure interface actions (tab switches, expand/collapse);
                # they stay exempt from business AC binding but keep handler checks.
                if not re.fullmatch(r"(?:ACT|UIACT)-[A-Z0-9-]+", action, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-ACTION", path, "data-action must bind a stable ACT-* or UIACT-* ID", action)
                if action.upper().startswith("ACT-REVIEW-") and re.search(r"review-mode|region-REVIEW|评审抽屉|评审模式", raw, re.I):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-UIACTION-NAMESPACE", path,
                        "评审叠加的纯界面动作必须使用 UIACT-REVIEW-*，不能污染业务 ACT-*",
                        action,
                        affected_consumers=("product", "frontend", "qa", "coding_agent"),
                    )
            for metric in metrics:
                if not re.fullmatch(r"METRIC-[A-Z0-9-]+", metric, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-METRIC", path, "data-metric must bind a stable METRIC-* ID", metric)
            metric_counts = Counter(metric_ids)
            for metric_id, count in sorted(metric_counts.items()):
                if count < 2:
                    continue
                bindings = [item for item in metric_bindings if item[0] == metric_id]
                normalized_labels = [_normalize_metric_label(item[1]) for item in bindings]
                labels = {item for item in normalized_labels if item}
                if any(not item for item in normalized_labels):
                    self.add(
                        "BLOCK", "PROTO-METRIC-LABEL-MISSING", path,
                        "重复使用的 METRIC-* 没有可判定的业务标签，无法证明这些卡片是同一指标",
                        metric_id,
                        affected_consumers=("product", "backend", "qa", "coding_agent"),
                        related_refs=(metric_id,),
                    )
                elif len(labels) > 1:
                    self.add(
                        "BLOCK", "PROTO-METRIC-ID-SEMANTIC-COLLISION", path,
                        "同一个 METRIC-* 绑定了多个业务含义；指标追溯和计算口径会多对一",
                        f"{metric_id}: {', '.join(sorted(labels)[:4])}",
                        affected_consumers=("product", "backend", "qa", "coding_agent"),
                        related_refs=(metric_id,),
                    )
        if level in {"L3", "L4"}:
            for region in region_testids:
                if not re.fullmatch(r"region-REG-[A-Z0-9-]+", region, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-REGION", path, "region data-testid must bind a stable REG-* ID", region)
            page_contracts = self._page_contracts(raw)
            complex_contract = any(
                attrs.get("layout", "").lower() in {"composite", "builder", "portal"}
                or len({item.strip().lower() for item in attrs.get("surfaces", "").split(",") if item.strip()}) > 1
                for attrs, _block in page_contracts.values()
            )
            complex_markup = len(page_testids) > 1 or bool(re.search(r"<table\b", raw, re.I) and re.search(r"<(?:form|input|select|textarea)\b", raw, re.I))
            if page_testids and (complex_contract or complex_markup) and not region_testids:
                self.add(
                    "BLOCK", "PROTO-NO-REGION-ANCHOR", path,
                    "L3/L4 复合页、组装器、门户或多视图原型至少需要一个稳定 REG-* 区域锚点",
                    affected_consumers=("product", "ux", "frontend", "qa", "coding_agent"),
                )
        if not actions and not unstable_action_values:
            self.add("GAP", "PROTO-NO-ACTIONS", path, "no data-action controls were found; confirm this is intentionally static")

        script_blocks = []
        module_script = False
        local_dependencies: set[str] = set()
        for attrs, body in re.findall(r"<script\b([^>]*)>(.*?)</script>", raw, re.I | re.S):
            type_match = re.search(r"\btype\s*=\s*['\"]([^'\"]+)['\"]", attrs, re.I)
            script_type = type_match.group(1).lower() if type_match else "text/javascript"
            if script_type in {"text/javascript", "application/javascript", "module"}:
                src_match = re.search(r"\bsrc\s*=\s*['\"]([^'\"]+)['\"]", attrs, re.I)
                if src_match:
                    dependency = self._prototype_dependency(path, src_match.group(1), "JavaScript")
                    if dependency is not None:
                        try:
                            script_blocks.append(self.read(dependency))
                            local_dependencies.add(str(dependency.resolve()))
                        except (OSError, UnicodeError) as exc:
                            self.add("BLOCK", "PROTO-DEPENDENCY-READ", path, f"本地 JavaScript 依赖无法读取：{exc}", src_match.group(1))
                else:
                    script_blocks.append(body)
                module_script = module_script or script_type == "module"
        scripts = "\n".join(script_blocks)
        for factory in re.finditer(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)", scripts, re.I):
            if "metric" not in factory.group(1).casefold():
                continue
            params = [item.strip() for item in factory.group(2).split(",") if item.strip()]
            semantic_params = [item for item in params if re.fullmatch(r"(?:label|name|title|metricName)", item, re.I)]
            window = scripts[factory.start():factory.start() + 1200]
            next_function = re.search(r"\n\s*function\s+[A-Za-z_$]", window[factory.end() - factory.start():], re.I)
            if next_function:
                window = window[:factory.end() - factory.start() + next_function.start()]
            metric_match = re.search(r"data-metric\s*=\s*['\"](METRIC-[A-Z0-9-]+)['\"]", window, re.I)
            dynamic_label = any(re.search(rf"\$\{{\s*{re.escape(param)}\s*\}}", window) for param in semantic_params)
            call_count = len(re.findall(rf"\b{re.escape(factory.group(1))}\s*\(", scripts))
            if metric_match and dynamic_label and call_count > 2:
                self.add(
                    "BLOCK", "PROTO-DYNAMIC-METRIC-ID-REUSE", path,
                    "动态指标工厂用一个固定 METRIC-* 承载多个运行时标签，无法一一追溯口径",
                    metric_match.group(1).upper(),
                    affected_consumers=("product", "backend", "qa", "coding_agent"),
                    related_refs=(metric_match.group(1).upper(),),
                )
        review_surface = bool(
            re.search(r"\bdata-review-id\s*=|\bdata-review-role\s*=|\bclass\s*=\s*['\"][^'\"]*\breview-mode\b", tag_source, re.I)
            or re.search(r"\bdata-testid\s*=\s*['\"](?:region|drawer)-REVIEW-", tag_source, re.I)
            or re.search(r"\bdata-review-workspace\s*=", tag_source, re.I)
            or re.search(r"\bid\s*=\s*['\"]review-workspace-manifest['\"]", tag_source, re.I)
        )
        review_workspace, review_workspace_error = _review_workspace_document(raw)
        declared_review_markers: set[str] = set()
        explicit_workspace = bool(re.search(r"\bdata-review-workspace\s*=", tag_source, re.I))
        if review_surface and review_workspace is None:
            if explicit_workspace or review_workspace_error not in {None, "missing"}:
                self.add(
                    "BLOCK", "PROTO-REVIEW-WORKSPACE-MANIFEST-INVALID", path,
                    "评审工作台缺少唯一、可解析的内嵌 review-workspace-manifest",
                    review_workspace_error or "review-workspace-manifest",
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
            else:
                # v5.4.6 and earlier review overlays remain inspectable in the
                # prototype-only profile, but cannot be promoted through a
                # combined handoff without migration to the v5.4.7 workspace.
                self.review_workspace_legacy_paths.add(path.resolve())
                self.add(
                    "GAP", "PROTO-REVIEW-WORKSPACE-LEGACY", path,
                    "检测到旧式评审叠加：可继续视检，但未形成 CurrentContext、声明分母、三页签与产品指纹合同",
                    affected_consumers=("product", "frontend", "backend", "qa"),
                )
        elif review_workspace is not None and str(review_workspace.get("schema_version", "")) in {"5.4.7-final", "5.4.8", "5.4.9"}:
            declared_review_markers = self._check_review_workspace_final(
                path, raw, tag_source, scripts, review_workspace,
            )
        elif review_workspace is not None:
            schema_errors = []
            if REVIEW_WORKSPACE_SCHEMA.is_file():
                schema = json.loads(REVIEW_WORKSPACE_SCHEMA.read_text(encoding="utf-8"))
                schema_errors = sorted(
                    Draft202012Validator(schema).iter_errors(review_workspace),
                    key=lambda item: tuple(str(part) for part in item.path),
                )
                for schema_error in schema_errors:
                    location = ".".join(str(part) for part in schema_error.path) or "<root>"
                    self.add(
                        "BLOCK", "PROTO-REVIEW-WORKSPACE-SCHEMA", path,
                        schema_error.message, location,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
            if not schema_errors:
                self.review_workspace_contracts.append((path.resolve(), review_workspace))
                workspace_id = str(review_workspace.get("workspace_id", ""))
                declared_language = str(review_workspace.get("language", "")).casefold()
                html_language_match = re.search(
                    r"<html\b[^>]*\blang\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I,
                )
                html_language = html_language_match.group(1).casefold() if html_language_match else ""
                if declared_language and declared_language != html_language:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-LANGUAGE-MISMATCH", path,
                        "评审 manifest 的人类语言与 HTML lang 不一致，角色投影可能混入错误语言",
                        f"{declared_language or 'missing'} != {html_language or 'missing'}",
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                root_ids = set(re.findall(r"\bdata-review-workspace\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I))
                if workspace_id not in root_ids:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-WORKSPACE-ROOT-MISMATCH", path,
                        "内嵌评审合同没有绑定同名 data-review-workspace 根容器", workspace_id,
                        affected_consumers=("frontend", "qa"),
                    )
                root_tag = next((
                    tag for tag in re.findall(
                        r"<[A-Za-z][^>]*\bdata-review-workspace\s*=\s*['\"][^'\"]+['\"][^>]*>",
                        tag_source, re.I | re.S,
                    )
                ), "")
                desktop_surface = str((review_workspace.get("layout") or {}).get("desktop_surface", ""))
                if not re.search(
                    rf"\bdata-review-desktop-surface\s*=\s*['\"]{re.escape(desktop_surface)}['\"]",
                    root_tag, re.I,
                ):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-DESKTOP-SURFACE-DRIFT", path,
                        "评审根没有绑定 manifest 的桌面自适应表面策略",
                        desktop_surface or workspace_id,
                        affected_consumers=("product", "frontend", "qa"),
                    )

                page_presentations: dict[str, tuple[str, str, str]] = {}
                duplicate_presentations: set[str] = set()
                for item in review_workspace.get("page_presentations", []) or []:
                    if not isinstance(item, dict):
                        continue
                    view_ref = str(item.get("view_ref", "")).upper()
                    if view_ref in page_presentations:
                        duplicate_presentations.add(view_ref)
                    page_presentations[view_ref] = (
                        str(item.get("page_profile", "")).casefold(),
                        str(item.get("focus_surface", "")).casefold(),
                        str(item.get("collision_policy", "")).casefold(),
                    )
                for duplicate in sorted(duplicate_presentations):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-PAGE-PRESENTATION-DUPLICATE", path,
                        "同一个 VIEW-* 登记了多个聚焦呈现，运行时无法确定应使用哪一种布局", duplicate,
                        affected_consumers=("product", "frontend", "qa"), related_refs=(duplicate,),
                    )

                visible_presentations: dict[str, tuple[str, str, str]] = {}
                duplicate_visible_presentations: set[str] = set()
                for tag in re.findall(r"<[A-Za-z][^>]*>", tag_source, re.S):
                    view_match = re.search(
                        r"\bdata-review-page-ref\s*=\s*['\"](VIEW-[A-Z0-9-]+)['\"]", tag, re.I,
                    )
                    if not view_match:
                        continue
                    view_ref = view_match.group(1).upper()
                    profile_match = re.search(r"\bdata-review-page-profile\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
                    surface_match = re.search(r"\bdata-review-focus-surface\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
                    collision_match = re.search(r"\bdata-review-collision-policy\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
                    value = (
                        profile_match.group(1).casefold() if profile_match else "",
                        surface_match.group(1).casefold() if surface_match else "",
                        collision_match.group(1).casefold() if collision_match else "",
                    )
                    if view_ref in visible_presentations:
                        duplicate_visible_presentations.add(view_ref)
                    visible_presentations[view_ref] = value
                for duplicate in sorted(duplicate_visible_presentations):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-PAGE-PRESENTATION-DUPLICATE", path,
                        "同一个 VIEW-* 存在多个可见聚焦呈现容器", duplicate,
                        affected_consumers=("frontend", "qa"), related_refs=(duplicate,),
                    )

                expected_page_refs: set[str] = set()
                for step in review_workspace.get("steps", []) or []:
                    if isinstance(step, dict):
                        expected_page_refs.update(
                            str(item).upper() for item in step.get("target_refs", []) or []
                            if str(item).upper().startswith("VIEW-")
                        )
                for journey in review_workspace.get("journeys", []) or []:
                    if isinstance(journey, dict):
                        expected_page_refs.update(
                            str(item).upper() for item in journey.get("entry_refs", []) or []
                            if str(item).upper().startswith("VIEW-")
                        )
                for missing in sorted(expected_page_refs - set(page_presentations)):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-PAGE-PRESENTATION-MISSING", path,
                        "进入聚焦评审的页面没有声明页面画像、评审表面和冲突策略", missing,
                        affected_consumers=("product", "frontend", "qa"), related_refs=(missing,),
                    )
                product_page_refs = {
                    item[5:].upper() for item in page_testids if item.upper().startswith("PAGE-VIEW-")
                }
                for orphan in sorted(set(page_presentations) - product_page_refs):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-PAGE-PRESENTATION-ORPHAN", path,
                        "页面自适应呈现引用了原型中不存在的 VIEW-*", orphan,
                        affected_consumers=("product", "frontend", "qa"), related_refs=(orphan,),
                    )
                for view_ref, expected in sorted(page_presentations.items()):
                    actual = visible_presentations.get(view_ref)
                    if actual != expected:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-PAGE-PRESENTATION-DRIFT", path,
                            "人类可见的页面画像/聚焦表面/冲突策略与 manifest 不一致",
                            f"{view_ref}: {actual or 'missing'} != {expected}",
                            affected_consumers=("product", "frontend", "qa"), related_refs=(view_ref,),
                        )
                for orphan in sorted(set(visible_presentations) - set(page_presentations)):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-PAGE-PRESENTATION-ORPHAN", path,
                        "HTML 中存在未登记到 manifest 的页面评审表面", orphan,
                        affected_consumers=("frontend", "qa"), related_refs=(orphan,),
                    )

                baseline = review_workspace.get("baseline") or {}
                if isinstance(baseline, dict) and str(baseline.get("hash", "")) == "0" * 64:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-BASELINE-PLACEHOLDER", path,
                        "评审工作台仍使用全零基线 hash，无法证明与 PRD 同源", workspace_id,
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
                placeholder_paths = _review_placeholder_paths(review_workspace)
                if placeholder_paths:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-WORKSPACE-PLACEHOLDER", path,
                        "评审工作台索引仍含模板占位或无理由的不适用值",
                        ", ".join(placeholder_paths[:8]),
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )

                steps = {
                    str(item.get("step_id", "")).upper(): item
                    for item in review_workspace.get("steps", []) or []
                    if isinstance(item, dict) and item.get("step_id")
                }
                step_ids = list(
                    str(item.get("step_id", "")).upper()
                    for item in review_workspace.get("steps", []) or []
                    if isinstance(item, dict) and item.get("step_id")
                )
                if len(step_ids) != len(set(step_ids)):
                    self.add("BLOCK", "PROTO-REVIEW-STEP-DUPLICATE", path, "评审工作台存在重复 STEP-*", workspace_id)
                anchored_step_ids = [
                    item.upper() for item in re.findall(
                        r"\bdata-review-step\s*=\s*['\"](STEP-[A-Z0-9-]+)['\"]",
                        tag_source, re.I,
                    )
                ]
                if len(anchored_step_ids) != len(set(anchored_step_ids)):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-STEP-ANCHOR-DUPLICATE", path,
                        "同一个 STEP-* 存在多个评审工作包根，切换与定位不再唯一", workspace_id,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                for missing in sorted(set(steps) - set(anchored_step_ids)):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-STEP-ANCHOR-MISSING", path,
                        "manifest 中的 STEP-* 没有对应的人类工作包 DOM 锚点", missing,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                for extra in sorted(set(anchored_step_ids) - set(steps)):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-STEP-ANCHOR-ORPHAN", path,
                        "HTML 中的 STEP-* 工作包不在评审 manifest 中", extra,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                visible_statuses, duplicate_statuses = _visible_review_statuses(raw)
                for step_id, step in steps.items():
                    expected_anchor = str(step.get("dom_anchor", ""))
                    bound = any(
                        re.search(rf"\bdata-review-step\s*=\s*['\"]{re.escape(step_id)}['\"]", tag, re.I)
                        and re.search(rf"\bdata-testid\s*=\s*['\"]{re.escape(expected_anchor)}['\"]", tag, re.I)
                        for tag in re.findall(r"<[A-Za-z][^>]*>", tag_source, re.S)
                    )
                    if not bound:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-STEP-ANCHOR-MISMATCH", path,
                            "STEP-* 的 data-review-step 与 manifest.dom_anchor 未绑定在同一根容器", step_id,
                            affected_consumers=("frontend", "qa", "coding_agent"),
                        )
                    for axis, field in (
                        ("business", "business_status"),
                        ("verification", "verification_status"),
                    ):
                        expected_status = str(step.get(field, "")).casefold()
                        visible_status = visible_statuses.get((step_id, axis))
                        if (step_id, axis) in duplicate_statuses:
                            self.add(
                                "BLOCK", "PROTO-REVIEW-STATUS-AXIS-DUPLICATE", path,
                                "同一 STEP 状态轴被重复投影；人类会同时看到多个可能冲突的结论",
                                f"{step_id}/{axis}",
                                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                            )
                        if visible_status is None:
                            self.add(
                                "BLOCK", "PROTO-REVIEW-STATUS-AXIS-HIDDEN", path,
                                "业务语义状态与验证证据状态必须在人类 STEP 工作包中分别可见",
                                f"{step_id}/{axis}",
                                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                            )
                        elif visible_status != expected_status:
                            self.add(
                                "BLOCK", "PROTO-REVIEW-STATUS-AXIS-DRIFT", path,
                                "人类可见状态与 review manifest 的状态轴不一致",
                                f"{step_id}/{axis}: {visible_status} != {expected_status}",
                                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                            )
                    source_refs = {str(item).upper() for item in step.get("source_refs", []) or []}
                    if str(step.get("business_status", "")).casefold() == "confirmed" and not any(
                        item.startswith(("SRC-", "DEC-")) for item in source_refs
                    ):
                        self.add(
                            "BLOCK", "PROTO-REVIEW-CONFIRMED-NO-EVIDENCE", path,
                            "confirmed STEP-* 至少需要一个 SRC-* 或 DEC-*，不能由原型现状或模型建议自证确认",
                            step_id,
                            affected_consumers=("product", "backend", "qa", "coding_agent"),
                        )
                    verification_status = str(step.get("verification_status", "")).casefold()
                    evidence_refs = {
                        str(item).upper() for item in step.get("evidence_refs", []) or []
                    }
                    if verification_status != "not_run" and not any(
                        item.startswith(("EVD-", "ARUN-")) for item in evidence_refs
                    ):
                        self.add(
                            "BLOCK", "PROTO-REVIEW-VERIFICATION-NO-EVIDENCE", path,
                            "STEP-* 声明已检查、验收或失败，但没有 EVD-* / ARUN-* 运行证据",
                            step_id,
                            affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                        )
                    declared_review_markers.update(
                        str(item).upper() for item in step.get("marker_refs", []) or []
                    )
                journeys = review_workspace.get("journeys", []) or []
                journey_ids = [
                    str(item.get("journey_id", "")).upper()
                    for item in journeys if isinstance(item, dict) and item.get("journey_id")
                ]
                if len(journey_ids) != len(set(journey_ids)):
                    self.add("BLOCK", "PROTO-REVIEW-JOURNEY-DUPLICATE", path, "评审工作台存在重复 FLOW-* 旅程", workspace_id)
                journey_steps: set[str] = set()
                for journey in journeys:
                    if not isinstance(journey, dict):
                        continue
                    refs = {str(item).upper() for item in journey.get("step_refs", []) or []}
                    journey_steps.update(refs)
                    for missing in sorted(refs - set(steps)):
                        self.add(
                            "BLOCK", "PROTO-REVIEW-JOURNEY-ORPHAN-STEP", path,
                            "旅程引用了不存在的 STEP-*", f"{journey.get('journey_id')}->{missing}",
                            affected_consumers=("product", "frontend", "backend", "qa"),
                        )
                    model_refs = journey.get("model_refs") or {}
                    if isinstance(model_refs, dict):
                        journey_id = str(journey.get("journey_id", "")).upper()
                        flow_refs = {str(item).upper() for item in model_refs.get("flow_refs", []) or []}
                        state_refs = {str(item).upper() for item in model_refs.get("state_machine_refs", []) or []}
                        data_refs = {str(item).upper() for item in model_refs.get("data_flow_refs", []) or []}
                        not_applicable = {
                            str(item).casefold() for item in model_refs.get("not_applicable", []) or []
                        }
                        if journey_id and journey_id not in flow_refs:
                            self.add(
                                "BLOCK", "PROTO-REVIEW-FLOW-MODEL-MISMATCH", path,
                                "旅程没有把自身 FLOW-* 登记为责任交接模型", journey_id,
                                affected_consumers=("product", "backend", "qa"),
                            )
                        for dimension, values in (
                            ("state_machine", state_refs), ("data_flow", data_refs),
                        ):
                            if not values and dimension not in not_applicable:
                                self.add(
                                    "BLOCK", "PROTO-REVIEW-MODEL-COVERAGE-AMBIGUOUS", path,
                                    "状态机/数据流为空时必须显式说明不适用，不能把遗漏伪装成无需求",
                                    f"{journey_id}/{dimension}",
                                    affected_consumers=("product", "backend", "qa", "coding_agent"),
                                )
                            if values and dimension in not_applicable:
                                self.add(
                                    "BLOCK", "PROTO-REVIEW-MODEL-COVERAGE-CONFLICT", path,
                                    "同一旅程模型既有引用又声明不适用", f"{journey_id}/{dimension}",
                                    affected_consumers=("product", "backend", "qa", "coding_agent"),
                                )
                visible_models: set[tuple[str, str]] = set()
                visible_model_na: set[str] = set()
                for tag in re.findall(r"<[A-Za-z][^>]*>", tag_source, re.S):
                    kind_match = re.search(
                        r"\bdata-review-model\s*=\s*['\"](flow|state_machine|data_flow)['\"]", tag, re.I,
                    )
                    ref_match = re.search(r"\bdata-review-model-ref\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
                    if kind_match and ref_match:
                        visible_models.add((kind_match.group(1).casefold(), ref_match.group(1).upper()))
                    na_match = re.search(
                        r"\bdata-review-model-na\s*=\s*['\"](state_machine|data_flow)['\"]", tag, re.I,
                    )
                    if na_match:
                        visible_model_na.add(na_match.group(1).casefold())
                expected_models: set[tuple[str, str]] = set()
                expected_model_na: set[str] = set()
                for journey in journeys:
                    if not isinstance(journey, dict):
                        continue
                    model_refs = journey.get("model_refs") or {}
                    if not isinstance(model_refs, dict):
                        continue
                    expected_models.update(("flow", str(item).upper()) for item in model_refs.get("flow_refs", []) or [])
                    expected_models.update(("state_machine", str(item).upper()) for item in model_refs.get("state_machine_refs", []) or [])
                    expected_models.update(("data_flow", str(item).upper()) for item in model_refs.get("data_flow_refs", []) or [])
                    expected_model_na.update(str(item).casefold() for item in model_refs.get("not_applicable", []) or [])
                for missing in sorted(expected_models - visible_models):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-MODEL-NOT-VISIBLE", path,
                        "FLOW/状态机/数据流引用未进入人类可见评审工作台",
                        f"{missing[0]}:{missing[1]}",
                        affected_consumers=("product", "backend", "qa"), related_refs=(missing[1],),
                    )
                for missing in sorted(expected_model_na - visible_model_na):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-MODEL-NA-HIDDEN", path,
                        "声明不适用的状态机/数据流没有向人类显示原因",
                        missing, affected_consumers=("product", "backend", "qa"),
                    )

                for missing in sorted(set(steps) - journey_steps):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-STEP-NOT-IN-JOURNEY", path,
                        "STEP-* 未归入任何可走读旅程", missing,
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )

                incoming = Counter()
                outgoing = Counter()
                edge_ids: list[str] = []
                for edge in review_workspace.get("edges", []) or []:
                    if not isinstance(edge, dict):
                        continue
                    edge_id = str(edge.get("edge_id", "")).upper()
                    edge_ids.append(edge_id)
                    kind = str(edge.get("kind", "")).lower()
                    source = str(edge.get("from_step_ref", "")).upper() if edge.get("from_step_ref") else None
                    target = str(edge.get("to_step_ref", "")).upper() if edge.get("to_step_ref") else None
                    if source and source not in steps:
                        self.add("BLOCK", "PROTO-REVIEW-EDGE-ORPHAN", path, "交接边起点不存在", f"{edge_id}->{source}")
                    if target and target not in steps:
                        self.add("BLOCK", "PROTO-REVIEW-EDGE-ORPHAN", path, "交接边终点不存在", f"{edge_id}->{target}")
                    if kind == "start" and (source is not None or target is None):
                        self.add("BLOCK", "PROTO-REVIEW-EDGE-SHAPE", path, "start 边必须从旅程外进入一个 STEP-*", edge_id)
                    elif kind == "finish" and (source is None or target is not None):
                        self.add("BLOCK", "PROTO-REVIEW-EDGE-SHAPE", path, "finish 边必须从 STEP-* 结束到旅程外", edge_id)
                    elif kind not in {"start", "finish"} and (source is None or target is None):
                        self.add("BLOCK", "PROTO-REVIEW-EDGE-SHAPE", path, "分支/并行/退回/异常边必须声明两端 STEP-*", edge_id)
                    if kind in {"return", "error", "compensate"} and not (edge.get("recovery_refs") or []):
                        self.add(
                            "BLOCK", "PROTO-REVIEW-EDGE-NO-RECOVERY", path,
                            "退回/异常/补偿边必须引用恢复、重新进入或接管合同", edge_id,
                            affected_consumers=("product", "backend", "qa", "coding_agent"),
                        )
                    if source in steps:
                        outgoing[source] += 1
                    if target in steps:
                        incoming[target] += 1
                if len(edge_ids) != len(set(edge_ids)):
                    self.add("BLOCK", "PROTO-REVIEW-EDGE-DUPLICATE", path, "评审工作台存在重复 EDGE-*", workspace_id)
                for step_id in sorted(steps):
                    if not incoming[step_id] or not outgoing[step_id]:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-STEP-DISCONNECTED", path,
                            "STEP-* 缺少进入或离开交接边，无法说明上游/下游/退回", step_id,
                            affected_consumers=("product", "backend", "qa"),
                        )

                scenarios = {
                    str(item.get("scenario_id", "")).upper(): item
                    for item in review_workspace.get("scenarios", []) or []
                    if isinstance(item, dict) and item.get("scenario_id")
                }
                scenario_ids = [
                    str(item.get("scenario_id", "")).upper()
                    for item in review_workspace.get("scenarios", []) or []
                    if isinstance(item, dict) and item.get("scenario_id")
                ]
                if len(scenario_ids) != len(set(scenario_ids)):
                    self.add("BLOCK", "PROTO-REVIEW-SCENARIO-DUPLICATE", path, "评审工作台存在重复 TEST-* 场景", workspace_id)
                covered_steps: set[str] = set()
                scenario_coverage_by_step: dict[str, set[str]] = defaultdict(set)
                for scenario_id, scenario in scenarios.items():
                    refs = {str(item).upper() for item in scenario.get("covered_step_refs", []) or []}
                    covered_steps.update(refs)
                    coverage = {str(item).casefold() for item in scenario.get("coverage", []) or []}
                    for step_ref in refs:
                        scenario_coverage_by_step[step_ref].update(coverage)
                    for missing in sorted(refs - set(steps)):
                        self.add("BLOCK", "PROTO-REVIEW-SCENARIO-ORPHAN-STEP", path, "测试场景覆盖了不存在的 STEP-*", f"{scenario_id}->{missing}")
                visible_scenarios: dict[str, str] = {}
                for tag in re.findall(r"<[A-Za-z][^>]*>", tag_source, re.S):
                    scenario_match = re.search(
                        r"\bdata-review-scenario\s*=\s*['\"](TEST-[A-Z0-9-]+)['\"]", tag, re.I,
                    )
                    if not scenario_match:
                        continue
                    acceptance_match = re.search(
                        r"\bdata-review-acceptance-ref\s*=\s*['\"](AC-[A-Z0-9-]+)['\"]", tag, re.I,
                    )
                    visible_scenarios[scenario_match.group(1).upper()] = (
                        acceptance_match.group(1).upper() if acceptance_match else ""
                    )
                for scenario_id, scenario in scenarios.items():
                    expected_acceptance = str(scenario.get("acceptance_ref", "")).upper()
                    if visible_scenarios.get(scenario_id) != expected_acceptance:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-SCENARIO-NOT-VISIBLE", path,
                            "TEST-* 场景及其 AC-* 未形成可见、可定位的验收卡",
                            f"{scenario_id}->{expected_acceptance}",
                            affected_consumers=("product", "qa", "coding_agent"),
                            related_refs=(scenario_id, expected_acceptance),
                        )
                for missing in sorted(set(steps) - covered_steps):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-STEP-NO-SCENARIO", path,
                        "STEP-* 没有任何可定位的正反/边界验收场景", missing,
                        affected_consumers=("product", "qa"),
                    )
                for step_id, step in steps.items():
                    required_risks = {
                        str(item).casefold() for item in step.get("risk_dimensions", []) or []
                    }
                    missing_risks = sorted(required_risks - scenario_coverage_by_step.get(step_id, set()))
                    if missing_risks:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-RISK-NOT-TESTED", path,
                            "STEP-* 已声明风险维度，但关联 TEST/AC 未覆盖",
                            f"{step_id}: {', '.join(missing_risks)}",
                            affected_consumers=("product", "qa", "coding_agent"),
                            related_refs=(step_id,),
                        )
                declared_unknowns = {str(item).upper() for item in review_workspace.get("unknown_refs", []) or []}
                referenced_unknowns: set[str] = set()
                for step_id, step in steps.items():
                    step_unknowns: set[str] = set()
                    role_packets = step.get("role_packets") or {}
                    if isinstance(role_packets, dict):
                        qa_packet = role_packets.get("qa") or {}
                        if isinstance(qa_packet, dict):
                            qa_refs = {str(item).upper() for item in qa_packet.get("scenario_refs", []) or []}
                            for missing in sorted(qa_refs - set(scenarios)):
                                self.add("BLOCK", "PROTO-REVIEW-QA-ORPHAN-SCENARIO", path, "测试镜头引用了不存在的 TEST-*", f"{step_id}->{missing}")
                        for packet in role_packets.values():
                            if isinstance(packet, dict):
                                step_unknowns.update(str(item).upper() for item in packet.get("gap_refs", []) or [])
                    step_unknowns.update(
                        str(item).upper() for item in step.get("contract_refs", []) or []
                        if str(item).upper().startswith("UNK-")
                    )
                    referenced_unknowns.update(step_unknowns)
                    if str(step.get("business_status", "")) != "confirmed" and not step_unknowns:
                        self.add("BLOCK", "PROTO-REVIEW-UNKNOWN-STEP-NO-GAP", path, "未确认的 STEP-* 未绑定可关闭 UNK-*", step_id)
                for missing in sorted(referenced_unknowns - declared_unknowns):
                    self.add("BLOCK", "PROTO-REVIEW-UNKNOWN-NOT-DECLARED", path, "角色工作包引用的 UNK-* 未进入工作台未知项索引", missing)

                handoff = review_workspace.get("machine_handoff") or {}
                if isinstance(handoff, dict):
                    handoff_gap_refs = {str(item).upper() for item in handoff.get("gap_refs", []) or []}
                    referenced_unknowns.update(handoff_gap_refs)
                    for missing in sorted(handoff_gap_refs - declared_unknowns):
                        self.add("BLOCK", "PROTO-REVIEW-HANDOFF-UNACCOUNTED", path, "Coding Agent handoff 的阻断项未进入工作台未知项索引", missing)
                bound_unknowns, _complete_bound_unknowns = _prototype_unknown_contracts(raw)
                for missing in sorted(declared_unknowns - bound_unknowns):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-UNKNOWN-NOT-VISIBLE", path,
                        "评审 manifest 声明的 UNK-* 没有可见且可关闭的 data-unk/注册表合同", missing,
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
                for orphan in sorted(declared_unknowns - referenced_unknowns):
                    self.add("BLOCK", "PROTO-REVIEW-UNKNOWN-ORPHAN", path, "工作台未知项没有绑定 STEP 或 machine handoff", orphan)

                modes = {item.casefold() for item in re.findall(r"\bdata-review-mode\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)}
                required_modes = {"orientation", "focus", "page", "acceptance"}
                if len(steps) > 1:
                    required_modes.add("journey")
                missing_modes = sorted(required_modes - modes)
                if missing_modes:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-MODE-MISSING", path,
                        "评审工作台缺少独立的信息模式，仍会退化成长列表/单抽屉",
                        ", ".join(missing_modes),
                        affected_consumers=("product", "frontend", "backend", "qa"),
                    )
                mode_targets = {item.casefold() for item in re.findall(r"\bdata-review-mode-target\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)}
                if not required_modes.issubset(mode_targets):
                    self.add("BLOCK", "PROTO-REVIEW-MODE-NOT-NAVIGABLE", path, "评审模式没有为每个必需视图提供可达切换控件", ", ".join(sorted(required_modes - mode_targets)))
                for attribute in ("data-review-progress", "data-review-current-step", "data-review-scenario", "data-review-compact-view"):
                    if not re.search(rf"\b{re.escape(attribute)}(?:\s*=|\s|>)", tag_source, re.I):
                        self.add("BLOCK", "PROTO-REVIEW-WORKSPACE-SURFACE-MISSING", path, "评审工作台缺少必要的任务导航表面", attribute)
                if not re.search(r"\bdata-review-compact\s*=\s*['\"]fullscreen-switcher['\"]", root_tag, re.I):
                    self.add("BLOCK", "PROTO-REVIEW-COMPACT-OVERLAY", path, "窄屏必须在产品/评审之间全屏切换，不能用宽抽屉遮住产品", workspace_id)
                if not re.search(r"\bdata-review-marker-policy\s*=\s*['\"](?:selected-step-only|current-page-on-demand)['\"]", root_tag, re.I):
                    self.add("BLOCK", "PROTO-REVIEW-MARKER-NOISE", path, "编号必须只显示当前 STEP 或按需显示当前页，不能默认铺满全站", workspace_id)
                default_role = str((review_workspace.get("layout") or {}).get("default_role", ""))
                if not re.search(rf"\bdata-review-active-role\s*=\s*['\"]{re.escape(default_role)}['\"]", root_tag, re.I):
                    self.add("BLOCK", "PROTO-REVIEW-LENS-NOT-INTERACTIVE", path, "评审根没有绑定 manifest 默认角色镜头", default_role or workspace_id)
                reads_mode = bool(re.search(r"dataset\.reviewModeTarget|getAttribute\s*\(\s*['\"]data-review-mode-target", scripts, re.I))
                writes_mode = bool(re.search(r"dataset\.reviewActiveMode\s*=|setAttribute\s*\(\s*['\"]data-review-active-mode", scripts, re.I))
                if not (reads_mode and writes_mode):
                    self.add("BLOCK", "PROTO-REVIEW-MODE-NOT-INTERACTIVE", path, "评审模式切换缺少可静态发现的读取与状态写入", workspace_id)
                reads_role = bool(re.search(r"dataset\.reviewRole|getAttribute\s*\(\s*['\"]data-review-role", scripts, re.I))
                writes_role = bool(re.search(r"dataset\.reviewActiveRole\s*=|setAttribute\s*\(\s*['\"]data-review-active-role", scripts, re.I))
                if not (reads_role and writes_role):
                    self.add("BLOCK", "PROTO-REVIEW-LENS-NOT-INTERACTIVE", path, "角色镜头切换缺少可静态发现的读取与状态写入", workspace_id)

                (
                    _lens_slots, _lens_text, step_lens_slots, step_lens_text,
                    step_lens_applicability,
                ) = _review_lens_coverage(raw)
                expected_slots = {
                    "product": {"purpose", "scope_and_boundary", "decision_and_source", "business_result"},
                    "frontend": {"entry_and_visibility", "surface_and_fields", "interaction_and_ui_states", "visible_result"},
                    "backend": {"authority_and_identity", "input_output_and_validation", "guards_and_state_effects", "side_effects_and_audit", "failure_recovery"},
                    "qa": {"preconditions_and_fixture", "positive_and_negative", "boundary_and_permission", "visible_and_domain_result", "evidence"},
                }
                for step_id in sorted(steps):
                    manifest_packets = steps[step_id].get("role_packets") or {}
                    for role, required_slots in expected_slots.items():
                        key = (step_id, role)
                        packet = manifest_packets.get(role) if isinstance(manifest_packets, dict) else {}
                        packet = packet if isinstance(packet, dict) else {}
                        applicability = str(packet.get("applicability", "")).casefold()
                        dom_applicability = step_lens_applicability.get(key, "")
                        if applicability != dom_applicability:
                            self.add(
                                "BLOCK", "PROTO-REVIEW-ROLE-APPLICABILITY-MISMATCH", path,
                                "角色是否受影响的 manifest 与可见工作包不一致",
                                f"{step_id}/{role}: {applicability or 'missing'} != {dom_applicability or 'missing'}",
                                affected_consumers=(role,), related_refs=(step_id,),
                            )
                        if applicability == "not_affected":
                            if step_lens_slots.get(key, set()):
                                self.add(
                                    "BLOCK", "PROTO-REVIEW-NOT-AFFECTED-HAS-CONTRACT", path,
                                    "标为不受影响的角色仍填充实施槽位，会制造无关负担或第二真相",
                                    f"{step_id}/{role}", affected_consumers=(role,), related_refs=(step_id,),
                                )
                            role_text = step_lens_text.get(key, "")
                            reason = str(packet.get("not_affected_reason", "") or "")
                            if not role_text or reason not in role_text:
                                self.add(
                                    "BLOCK", "PROTO-REVIEW-NOT-AFFECTED-REASON-HIDDEN", path,
                                    "不受影响原因必须在人类工作包中可见，不能只藏在 manifest",
                                    f"{step_id}/{role}", affected_consumers=(role,), related_refs=(step_id,),
                                )
                            continue
                        missing_slots = sorted(required_slots - step_lens_slots.get(key, set()))
                        if missing_slots:
                            self.add(
                                "BLOCK", "PROTO-REVIEW-ROLE-PACKET-INCOMPLETE", path,
                                "每个 STEP-* 的角色镜头都必须形成可独立执行的工作包",
                                f"{step_id}/{role}: {', '.join(missing_slots)}",
                                affected_consumers=(role,),
                                related_refs=(step_id,),
                            )
                        manifest_slots = {
                            str(item).casefold() for item in packet.get("slot_coverage", []) or []
                        }
                        if manifest_slots != step_lens_slots.get(key, set()):
                            self.add(
                                "BLOCK", "PROTO-REVIEW-ROLE-SLOT-DRIFT", path,
                                "角色槽位清单与可见 DOM 投影不一致",
                                f"{step_id}/{role}", affected_consumers=(role,), related_refs=(step_id,),
                            )
                        role_text = step_lens_text.get(key, "")
                        visible_role_refs = {
                            item.upper() for item in re.findall(
                                r"\b(?:SRC|DEC|REQ|ROLE|FLOW|STEP|VIEW|REG|ACT|UIACT|ENT|FLD|METRIC|RULE|STM|STATE|API|EVT|INT|AC|TEST|EVD|UNK|MOD|XCT|EDGE)-[A-Z0-9-]+\b",
                                role_text, re.I,
                            )
                        }
                        packet_refs = {str(item).upper() for item in packet.get("contract_refs", []) or []}
                        hidden_refs = sorted(packet_refs - visible_role_refs)
                        if hidden_refs:
                            self.add(
                                "BLOCK", "PROTO-REVIEW-CONTRACT-REF-HIDDEN", path,
                                "角色工作包摘要没有显示其权威合同引用，接收者无法回到规则/AC",
                                f"{step_id}/{role}: {', '.join(hidden_refs[:8])}",
                                affected_consumers=(role,), related_refs=tuple(hidden_refs[:50]),
                            )
                        if not role_text or re.search(r"\{[^{}]+\}|\b(?:TBD|TODO)\b|待补充|待完善", role_text, re.I):
                            self.add(
                                "BLOCK", "PROTO-REVIEW-ROLE-PACKET-PLACEHOLDER", path,
                                "STEP-* 的角色工作包为空或仍含模板占位", f"{step_id}/{role}",
                                affected_consumers=(role,), related_refs=(step_id,),
                            )
        prototype_unknowns, complete_unknowns = _prototype_unknown_contracts(raw)
        incomplete_unknowns = sorted(prototype_unknowns - complete_unknowns)
        if incomplete_unknowns:
            severity = "BLOCK" if review_surface and level in {"L2", "L3", "L4"} else "GAP"
            self.add(
                severity, "PROTO-UNKNOWN-CONTRACT-INCOMPLETE", path,
                f"{len(incomplete_unknowns)} 个原型未知项只有编号/待确认标签，缺少优先级、责任人、阻断阶段、影响引用或回退路径",
                ", ".join(incomplete_unknowns[:8]),
                affected_consumers=("product", "backend", "qa", "coding_agent", "customer_acceptor"),
                related_refs=tuple(incomplete_unknowns[:50]),
            )
        conflicting_unknowns: set[str] = set()
        for tag in re.findall(r"<[A-Za-z][^>]*\bdata-unk\s*=\s*['\"][^'\"]+['\"][^>]*>", tag_source, re.I | re.S):
            unknown_match = re.search(r"\bdata-unk\s*=\s*['\"](UNK-[A-Z0-9-]+)['\"]", tag, re.I)
            if unknown_match and re.search(
                r"\bdata-(?:metric|review|contract|decision)-status\s*=\s*['\"](?:confirmed|closed|resolved|decided)['\"]",
                tag, re.I,
            ):
                conflicting_unknowns.add(unknown_match.group(1).upper())
        for unknown_id in sorted(conflicting_unknowns):
            self.add(
                "BLOCK", "PROTO-UNKNOWN-CONFIRMED-CONFLICT", path,
                "同一原型对象同时标为已确认和未知，评审者无法判断是否可实施", unknown_id,
                affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                related_refs=(unknown_id,),
            )
        if (
            review_surface
            and level in {"L2", "L3", "L4"}
            and not (
                isinstance(review_workspace, dict)
                and str(review_workspace.get("schema_version", "")) in {"5.4.7-final", "5.4.8", "5.4.9"}
            )
        ):
            review_ids = [
                item.upper() for item in re.findall(
                    r"\bdata-review-id\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I
                )
            ]
            target_ids = [
                item.upper() for item in re.findall(
                    r"\bdata-review-target\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I
                )
            ]
            if review_workspace is not None:
                actual_markers = set(review_ids) | set(target_ids)
                for marker in sorted(actual_markers - declared_review_markers):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-MARKER-NOT-DECLARED", path,
                        "页面编号/说明卡不在当前 STEP 的 marker_refs 中，会产生跨页噪声或漂移", marker,
                        affected_consumers=("product", "frontend", "qa", "coding_agent"),
                    )
                for marker in sorted(declared_review_markers):
                    if Counter(review_ids)[marker] != 1 or Counter(target_ids)[marker] != 1:
                        self.add(
                            "BLOCK", "PROTO-REVIEW-LINKAGE-MISSING", path,
                            "每个 marker_ref 必须恰好有一个产品落点和一个说明卡，支持双向定位",
                            marker,
                            affected_consumers=("product", "frontend", "qa", "coding_agent"),
                        )
            elif not review_ids:
                self.add(
                    "BLOCK", "PROTO-REVIEW-LINKAGE-MISSING", path,
                    "旧式评审态没有为左侧编号和右侧说明建立共享 data-review-id",
                    affected_consumers=("product", "frontend", "qa", "coding_agent"),
                )
            else:
                for review_id, count in sorted(Counter(review_ids).items()):
                    if count < 2 and review_id not in set(target_ids):
                        self.add(
                            "BLOCK", "PROTO-REVIEW-LINKAGE-MISSING", path,
                            "评审编号没有对应的右侧说明卡，或说明卡无法反向定位编号",
                            review_id,
                            affected_consumers=("product", "frontend", "qa", "coding_agent"),
                        )
            if review_ids and (review_workspace is None or declared_review_markers):
                reads_review_id = bool(re.search(r"dataset\.reviewId|getAttribute\s*\(\s*['\"]data-review-id|closest\s*\(\s*['\"]\[data-review-id", scripts, re.I))
                writes_selection = bool(re.search(r"aria-current|dataset\.reviewSelected|classList\.(?:add|remove|toggle)\s*\(\s*['\"](?:active|selected|is-active)", scripts, re.I))
                initial_selection = bool(re.search(r"\baria-current\s*=\s*['\"]true['\"]", tag_source, re.I))
                if not (reads_review_id and writes_selection and initial_selection):
                    self.add(
                        "BLOCK", "PROTO-REVIEW-SELECTION-NOT-SYNCED", path,
                        "评审态未证明点击编号后左右两侧同时形成可见选中态",
                        "data-review-id + aria-current",
                        affected_consumers=("product", "frontend", "qa", "coding_agent"),
                        related_refs=tuple(sorted(set(review_ids))[:20]),
                    )
            review_roles = set(re.findall(r"\bdata-review-role\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I))
            for tag in re.findall(r"<[A-Za-z][^>]*>", tag_source, re.S):
                if re.search(r"(?:data-action|data-uiact)\s*=\s*['\"]UIACT-REVIEW-LENS['\"]", tag, re.I):
                    lens_match = re.search(r"\bdata-lens\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
                    if lens_match:
                        review_roles.add(lens_match.group(1))
            if review_roles:
                review_lenses = set(re.findall(r"\bdata-review-lens\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I))
                missing_lenses = sorted(review_roles - review_lenses)
                if missing_lenses:
                    self.add(
                        "BLOCK", "PROTO-REVIEW-LENS-COSMETIC", path,
                        "角色镜头只有切换控件，没有对应的结构化内容投影",
                        ", ".join(missing_lenses),
                        affected_consumers=("product", "frontend", "backend", "qa", "coding_agent"),
                    )
        handler_actions = _handler_actions(scripts)
        dynamic_anchor_actions = set(extract_dynamic_anchor_actions(scripts))
        for placeholder in unstable_action_values:
            related = tuple(sorted(dynamic_anchor_actions or handler_actions)[:50])
            self.add(
                "BLOCK", "PROTO-UNSTABLE-ACTION", path,
                "data-action 模板值无法静态解析为唯一稳定动作",
                related[0] if related else "data-action template",
                related_refs=related,
            )
        orphan_handler_actions = sorted(handler_actions - {item.upper() for item in actions} - dynamic_anchor_actions)
        for action in orphan_handler_actions:
            self.add(
                "BLOCK", "PROTO-ORPHAN-HANDLER", path,
                "动作注册表存在处理器，但源模板没有对应 data-action；可能是入口丢失、死代码或未批准删减",
                action,
                affected_consumers=("product", "frontend", "qa", "coding_agent"),
            )
        unreachable_surfaces = _unreachable_hidden_surfaces(tag_source, scripts)
        for surface in unreachable_surfaces:
            self.add(
                "BLOCK", "PROTO-UNREACHABLE-VIEW", path,
                "页面/弹窗/抽屉被显式隐藏且没有可静态发现的入口或路由",
                surface,
                affected_consumers=("product", "frontend", "qa", "coding_agent"),
            )
        split_anchor_pattern = re.compile(
            r"(?:data-\s*['\"]\s*\+\s*['\"](?:action|testid|state|field|metric)|"
            r"['\"]data-['\"]\s*\+\s*['\"](?:action|testid|state|field|metric)['\"])",
            re.I,
        )
        split_anchors = split_anchor_pattern.findall(scripts)
        script_action_candidates = sorted(dynamic_anchor_actions - {item.upper() for item in actions})
        if split_anchors:
            severity = "BLOCK" if level in {"L2", "L3", "L4"} else "GAP"
            self.add(
                severity, "PROTO-DYNAMIC-ANCHOR-CONSTRUCTION", path,
                f"发现 {len(split_anchors)} 处 data-* 锚点名称由字符串拼接生成；静态门禁无法证明其完整性",
                re.sub(r"\s+", " ", split_anchors[0])[:120],
                affected_consumers=("frontend", "qa", "coding_agent"),
                related_refs=tuple(item.upper() for item in script_action_candidates[:50]),
            )
        _literal_runtime_actions, unsafe_runtime_assignments = inspect_runtime_action_assignments(scripts)
        if level in {"L2", "L3", "L4"} and unsafe_runtime_assignments:
            self.add(
                "BLOCK", "PROTO-RUNTIME-ACTION-RETROFIT", path,
                "data-action 必须在视图模板源码中可静态枚举，不能在运行时补挂",
                unsafe_runtime_assignments[0],
            )
        if level in {"L3", "L4"}:
            metric_like_tags = [
                tag for tag in re.findall(r"<[A-Za-z][^>]*>", raw, re.S)
                if re.search(r"\bclass\s*=\s*['\"][^'\"]*\b(?:metric|metric-card|stat-card|kpi)\b", tag, re.I)
                and not re.search(r"\bdata-metric\s*=", tag, re.I)
            ]
            if metric_like_tags:
                self.add("BLOCK", "PROTO-METRIC-NO-ID", path, f"{len(metric_like_tags)} displayed metric elements have no stable data-metric", re.sub(r"\s+", " ", metric_like_tags[0])[:120])
            inline_handlers = re.findall(r"\bon(?:click|change|input|submit|dragstart|drop)\s*=", raw, re.I)
            if inline_handlers:
                self.add("BLOCK", "PROTO-INLINE-HANDLER", path, f"L3 prototype contains {len(inline_handlers)} inline event handlers; use one explicit action registry")
            missing_action_controls = []
            missing_ac_controls = []
            for tag in re.findall(r"<(?:button|a)\b[^>]*>", raw, re.I | re.S):
                if re.search(r"\bdisabled\b", tag, re.I):
                    continue
                action_match = re.search(r"\bdata-action\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
                if not action_match:
                    missing_action_controls.append(re.sub(r"\s+", " ", tag)[:120])
                elif action_match.group(1).upper().startswith("UIACT-"):
                    continue  # pure interface actions are exempt from business data-ac
                elif not re.search(r"\bdata-ac\s*=\s*['\"]AC-[A-Z0-9-]+['\"]", tag, re.I):
                    missing_ac_controls.append(re.sub(r"\s+", " ", tag)[:120])
            if missing_action_controls:
                self.add("BLOCK", "PROTO-CONTROL-NO-ACTION", path, f"{len(missing_action_controls)} button/link controls have no stable data-action", missing_action_controls[0])
            if missing_ac_controls:
                self.add("BLOCK", "PROTO-ACTION-NO-AC", path, f"{len(missing_ac_controls)} action controls have no data-ac trace", missing_ac_controls[0])
            function_names = re.findall(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(", scripts)
            duplicates = sorted(name for name, count in Counter(function_names).items() if count > 1)
            for name in duplicates[:10]:
                self.add("BLOCK", "PROTO-DUPLICATE-FUNCTION", path, "duplicate function declaration indicates stacked prototype overrides", name)
        inline_action_tags = {
            action
            for tag in re.findall(r"<[^>]+\bdata-action\s*=\s*['\"][^'\"]+['\"][^>]*>", raw, re.I | re.S)
            for action in re.findall(r"\bdata-action\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
            if re.search(r"\bonclick\s*=", tag, re.I)
        }
        has_listener = bool(re.search(r"addEventListener\s*\(\s*['\"](?:click|change|submit|input)['\"]", scripts, re.I))
        reads_action = bool(re.search(r"dataset\.action|getAttribute\s*\(\s*['\"]data-action['\"]|closest\s*\(\s*['\"]\[data-action\]", scripts, re.I))
        for action in actions:
            dispatch_evidence = bool(re.search(
                rf"(?:case\s+['\"]{re.escape(action)}['\"]|(?:action|actionId)\s*===?\s*['\"]{re.escape(action)}['\"]|['\"]{re.escape(action)}['\"]\s*:|\.set\s*\(\s*['\"]{re.escape(action)}['\"]|\[\s*['\"]{re.escape(action)}['\"]\s*\]\s*=)",
                scripts,
                re.I,
            ))
            if action not in inline_action_tags and not (has_listener and reads_action and dispatch_evidence):
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

        external_css: list[str] = []
        for tag in re.findall(r"<link\b[^>]*>", raw, re.I | re.S):
            if not re.search(r"\brel\s*=\s*['\"][^'\"]*stylesheet[^'\"]*['\"]", tag, re.I):
                continue
            href = re.search(r"\bhref\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
            if not href:
                continue
            dependency = self._prototype_dependency(path, href.group(1), "CSS")
            if dependency is not None:
                try:
                    external_css.append(self.read(dependency))
                    local_dependencies.add(str(dependency.resolve()))
                except (OSError, UnicodeError) as exc:
                    self.add("BLOCK", "PROTO-DEPENDENCY-READ", path, f"本地 CSS 依赖无法读取：{exc}", href.group(1))
        css_scan_source = raw
        if external_css:
            css_scan_source += "\n<style>\n" + "\n".join(external_css) + "\n</style>"
        for css_finding in scan_prototype_css(css_scan_source):
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
        self.metrics.update({
            "prototype_pages": len(page_testids),
            "prototype_regions": len(region_testids),
            "prototype_actions": len(actions),
            "prototype_dynamic_action_candidates": len(script_action_candidates),
            "prototype_action_inventory_total": len({item.upper() for item in actions} | dynamic_anchor_actions),
            "prototype_states": len(states),
            "prototype_fields": len(fields),
            "prototype_metrics": len(metrics),
            "prototype_acceptance_refs": len(self.prototype_acceptance_refs),
            "prototype_local_dependencies": len(local_dependencies),
            "prototype_handler_actions": len(handler_actions),
            "prototype_dynamic_anchor_actions": len(dynamic_anchor_actions),
            "prototype_orphan_handler_actions": len(orphan_handler_actions),
            "prototype_unreachable_surfaces": len(unreachable_surfaces),
            "prototype_dynamic_class_pollution": len(polluted_classes),
            "prototype_unknowns": len(prototype_unknowns),
            "prototype_incomplete_unknown_contracts": len(incomplete_unknowns),
        })

    def check_acceptance_run(self, path: Path) -> tuple[set[str], bool, bool]:
        from quality_gate import ACCEPTANCE_SCHEMA  # deferred: avoids circular import
        """Validate one ARUN and return evidenced ACs, browser environment, conclusion."""
        try:
            raw = self.read(path)
        except (OSError, UnicodeError) as exc:
            self.add("BLOCK", "ACCEPTANCE-READ", path, f"验收记录无法读取：{exc}")
            return set(), False, False
        document, error = self._yaml_document(path, raw)
        if error or document is None:
            self.add("BLOCK", "ACCEPTANCE-PARSE", path, error or "验收记录无效")
            return set(), False, False
        schema = json.loads(ACCEPTANCE_SCHEMA.read_text(encoding="utf-8"))
        schema_errors = sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
            key=lambda item: tuple(str(part) for part in item.path),
        )
        for schema_error in schema_errors:
            location = ".".join(str(part) for part in schema_error.path) or "<root>"
            self.add("BLOCK", "ACCEPTANCE-SCHEMA", path, schema_error.message, location)

        evidence_failures = validate_evidence_refs(document, path)
        for failure in evidence_failures:
            self.add("BLOCK", "ACCEPTANCE-EVIDENCE-INVALID", path, failure)

        evidenced: set[str] = set()
        mandatory_incomplete: list[str] = []
        for item in document.get("items", []) or []:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "<unknown>"))
            if item.get("mandatory") and item.get("result") != "pass":
                mandatory_incomplete.append(item_id)
            if item.get("result") != "pass":
                continue
            if not str(item.get("actual_result", "")).strip() or not item.get("evidence_refs"):
                self.add("BLOCK", "ACCEPTANCE-PASS-NO-EVIDENCE", path, "pass 项必须填写实际结果和证据引用", item_id)
                continue
            acceptance_ref = str(item.get("acceptance_ref", "")).upper()
            if acceptance_ref and not evidence_failures:
                evidenced.add(acceptance_ref)

        conclusion = str(document.get("conclusion", "pending"))
        sign_offs = document.get("sign_offs", []) or []
        if conclusion == "accepted" and mandatory_incomplete:
            self.add("BLOCK", "ACCEPTANCE-INCOMPLETE-CONCLUSION", path, "accepted 仍包含未通过的 mandatory 项", ", ".join(mandatory_incomplete))
        if conclusion == "accepted_with_conditions" and not document.get("conditions"):
            self.add("BLOCK", "ACCEPTANCE-CONDITION-MISSING", path, "accepted_with_conditions 缺少条件、责任人和完成标准")
        if conclusion in {"accepted", "accepted_with_conditions"} and not sign_offs:
            self.add("BLOCK", "ACCEPTANCE-SIGNOFF-MISSING", path, "接受结论缺少签署记录")
        elif conclusion in {"accepted", "accepted_with_conditions"}:
            missing_signoff_evidence = [
                str(item.get("actor", "<unknown>"))
                for item in sign_offs
                if isinstance(item, dict) and not str(item.get("evidence_ref", "")).strip()
            ]
            if missing_signoff_evidence:
                self.add(
                    "BLOCK", "ACCEPTANCE-SIGNOFF-NO-EVIDENCE", path,
                    "接受结论的每条签署记录都必须绑定可解析证据",
                    ", ".join(missing_signoff_evidence),
                )
            rejecting_signers = [
                str(item.get("actor", "<unknown>"))
                for item in sign_offs
                if isinstance(item, dict) and item.get("decision") == "reject"
            ]
            if rejecting_signers:
                self.add(
                    "BLOCK", "ACCEPTANCE-SIGNOFF-CONFLICT", path,
                    "接受结论与拒绝签署相冲突",
                    ", ".join(rejecting_signers),
                )

        environment = str(document.get("environment", "")).lower()
        browser_markers = ("browser", "浏览器", "chrome", "edge", "firefox", "safari", "webkit", "playwright")
        browser_environment = any(marker in environment for marker in browser_markers)
        conclusive = (
            conclusion in {"accepted", "accepted_with_conditions"}
            and not mandatory_incomplete
            and bool(sign_offs)
            and not schema_errors
            and not evidence_failures
            and all(str(item.get("evidence_ref", "")).strip() for item in sign_offs if isinstance(item, dict))
            and not any(item.get("decision") == "reject" for item in sign_offs if isinstance(item, dict))
        )
        self.metrics.update({
            "acceptance_run_items": self.metrics.get("acceptance_run_items", 0) + len(document.get("items", []) or []),
            "acceptance_run_evidenced_acs": self.metrics.get("acceptance_run_evidenced_acs", 0) + len(evidenced),
        })
        return evidenced, browser_environment, conclusive


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
