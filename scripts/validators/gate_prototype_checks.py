"""Static prototype and acceptance-run checks (mixin split out of quality_gate.py)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

SCRIPT_DIR = Path(__file__).resolve().parent.parent
for _candidate in (SCRIPT_DIR, SCRIPT_DIR / "validators"):
    if str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

from jsonschema import Draft202012Validator, FormatChecker

from scan_prototype_css import scan as scan_prototype_css
from validate_acceptance_run import validate_evidence_refs

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
)


def _visible_text(raw: str) -> str:
    """Strip scripts, styles, comments and tags, leaving user-visible copy."""
    text = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    return re.sub(r"<[^>]+>", " ", text)


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
        visible_lowered = _visible_text(raw).lower()
        for term in DEMO_SCAFFOLDING_TERMS:
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
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                continue
            if parsed.path.lower().endswith(".html"):
                self.add(
                    "BLOCK", "PROTO-NESTED-PRODUCT-IFRAME", path,
                    "原型用本地 iframe 嵌套另一个产品页面，嵌套页交互合同不可静态证明", src,
                    affected_consumers=("frontend", "qa", "coding_agent"),
                )
        testids = re.findall(r"\bdata-testid\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)
        actions = sorted(set(re.findall(r"\bdata-action\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        states = sorted(set(re.findall(r"\bdata-state\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        fields = sorted(set(re.findall(r"\bdata-(?:field|bind)\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
        metrics = sorted(set(re.findall(r"\bdata-metric\s*=\s*['\"]([^'\"]+)['\"]", tag_source, re.I)))
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
            for metric in metrics:
                if not re.fullmatch(r"METRIC-[A-Z0-9-]+", metric, re.I):
                    self.add("BLOCK", "PROTO-UNSTABLE-METRIC", path, "data-metric must bind a stable METRIC-* ID", metric)
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
        if not actions:
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
        split_anchor_pattern = re.compile(
            r"(?:data-\s*['\"]\s*\+\s*['\"](?:action|testid|state|field|metric)|"
            r"['\"]data-['\"]\s*\+\s*['\"](?:action|testid|state|field|metric)['\"])",
            re.I,
        )
        split_anchors = split_anchor_pattern.findall(scripts)
        script_action_candidates = sorted(set(re.findall(r"\bACT-[A-Z0-9-]+\b", scripts, re.I)) - set(actions))
        if split_anchors:
            severity = "BLOCK" if level in {"L2", "L3", "L4"} else "GAP"
            self.add(
                severity, "PROTO-DYNAMIC-ANCHOR-CONSTRUCTION", path,
                f"发现 {len(split_anchors)} 处 data-* 锚点名称由字符串拼接生成；静态门禁无法证明其完整性",
                re.sub(r"\s+", " ", split_anchors[0])[:120],
                affected_consumers=("frontend", "qa", "coding_agent"),
                related_refs=tuple(item.upper() for item in script_action_candidates[:50]),
            )
        if level in {"L2", "L3", "L4"} and re.search(
            r"(?:setAttribute\s*\(\s*['\"]data-action|dataset\.action\s*=)", scripts, re.I
        ):
            self.add(
                "BLOCK", "PROTO-RUNTIME-ACTION-RETROFIT", path,
                "data-action 必须在视图模板源码中可静态枚举，不能在运行时补挂",
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
            "prototype_dynamic_action_candidates": len(script_action_candidates) if split_anchors else 0,
            "prototype_action_inventory_total": len(set(actions) | (set(script_action_candidates) if split_anchors else set())),
            "prototype_states": len(states),
            "prototype_fields": len(fields),
            "prototype_metrics": len(metrics),
            "prototype_acceptance_refs": len(self.prototype_acceptance_refs),
            "prototype_local_dependencies": len(local_dependencies),
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

