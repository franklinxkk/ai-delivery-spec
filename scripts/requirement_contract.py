"""Shared task routing and bounded declaration checks. Never authorizes business decisions."""
from __future__ import annotations
import re
from typing import Any
import yaml
from scan_requirement_ambiguity import inspect_content, prose_lines
from stage_contract import unknown_rows, contract_token, OPEN_UNKNOWN, CLOSED_UNKNOWN, GOVERNED_INDEX, blocking_relation


def load_declarations(raw: str) -> dict:
    class UniqueLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError("Declaration keys must be unique strings")
            result[key] = loader.construct_object(value_node, deep=deep)
        return result
    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    value = yaml.load(raw, Loader=UniqueLoader)
    if not isinstance(value, dict):
        raise ValueError("Declaration root must be an object")
    return value

VERSION = "5.5.6"
MODES = {"direct", "card", "prd"}
RISK_SIGNALS = {
    "state": ("states", "cross_module_state", "approval", "workflow"),
    "authority": ("data_lineage",),
    "integration": ("integrations", "data_submission", "data_reporting"),
    "metric": ("metric_caliber", "metrics"),
    "permission": ("tenant_isolation", "permissions"),
    "privacy": ("sensitive_data",),
    "regulated": ("compliance", "clinical", "safety_critical"),
    "migration": ("migration",),
    "compatibility": ("version_compatibility",),
    "irreversible": ("irreversible_write", "money"),
    "irreversible_ai_write": ("consequential_ai_write",),
    "strong_audit": ("strong_audit", "audit_required"),
    "batch": ("batch_io",),
}
CATEGORIES = {
    "state_authority": {"state", "authority"},
    "metric_definition": {"metric"},
    "recovery": {"integration", "batch", "irreversible", "irreversible_ai_write"},
    "null_stale": {"metric", "integration"},
    "permission_boundary": {"permission", "privacy"},
    "change_propagation": {"migration", "compatibility"},
}
# These prompts explain a declared review gap. They neither infer a new policy
# nor certify that the named reviewer/source is authentic.
SEMANTIC_REVIEW_GUIDANCE = {
    "state_authority": ("状态与数据权威", "核对每条转换的前置条件、操作者、结果状态和写入方；用被拒绝的转换核验边界。", "State and data authority", "Check each transition's precondition, actor, resulting state and writer; use a refused transition to distinguish the boundary."),
    "metric_definition": ("指标口径", "核对统计对象、分母、去重和时间窗口；用一个已知数值例及边界反例复算结果。", "Metric definition", "Check population, denominator, deduplication and time window; recalculate a known numerical example and a distinguishing boundary case."),
    "recovery": ("失败与恢复", "核对失败、结果未知、重试与重复提交是否保留同一业务结果；沿提交及重新打开入口验证。", "Failure and recovery", "Check failure, unknown results, retry and duplicate submissions against the intended business result; exercise submission and reopening paths."),
    "null_stale": ("缺失与失效数据", "核对缺失、零、失效数据分别如何参与判定与展示；按原始约定核验反例，不自行补过期政策。", "Missing and invalid data", "Check how missing, zero and invalid data affect decisions and display; verify counterexamples against the source without inventing an expiry policy."),
    "permission_boundary": ("权限边界", "核对操作者、对象和数据范围；从直接入口及角色切换验证拒绝结果，不能只检查按钮隐藏。", "Permission boundary", "Check actor, object and data scope; exercise direct entry and role changes, rather than relying on hidden controls."),
    "change_propagation": ("变更影响", "核对定义变更的生效时点、历史对象及下游消费者；验证受影响路径和一个应保持不变的路径。", "Change propagation", "Check effective time, historical objects and downstream consumers; verify an affected path and one path that should remain unchanged."),
}


def semantic_review_guidance(category: str, language: str = "zh-CN") -> tuple[str, str]:
    item = SEMANTIC_REVIEW_GUIDANCE[category]
    return item[2:] if language.casefold().startswith("en") else item[:2]


def semantic_review_location(body: str, category: str, scope_refs: list[str]) -> tuple[str, str]:
    """Locate real definitions/candidate prose, not fabricated rule IDs.

    Declaration scopes remain scopes when the body has no matching definition.
    Without IDs, lexical candidate locations help the reviewer find the prose;
    they are explicitly not claims of ownership or semantic completeness.
    """
    rows, headings = [], []
    for number, line in enumerate(prose_lines(body), 1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            level = len(match[1])
            while headings and headings[-1][0] >= level:
                headings.pop()
            headings.append((level, match[2]))
        rows.append((number, line, " / ".join(title for _, title in headings)))
    if scope_refs:
        positions = []
        for ref in scope_refs:
            # Heading or table definition only: a prose "see REQ-*" is not a definition.
            row = next((r for r in rows if re.match(r"^\s*(?:#{1,6}\s|\|)", r[1]) and re.search(r"(?<![A-Z0-9_-])" + re.escape(ref) + r"(?![A-Z0-9_-])", r[1])), None)
            positions.append(f"{ref} @line {row[0]} [{row[2]}]" if row else ref)
        absent = [ref for ref, location in zip(scope_refs, positions) if "@line" not in location]
        note_zh = "；正文未定位：" + ", ".join(absent) if absent else ""
        note_en = "; not located in body: " + ", ".join(absent) if absent else ""
        return "; ".join(positions) + note_zh, "; ".join(positions) + note_en
    patterns = {
        "state_authority": r"状态|转换|写入方|权威源|\bstate|transition|source of truth",
        "metric_definition": r"指标|分母|去重|占比|统计|metric|denominator|deduplicat|population",
        "recovery": r"重试|恢复|结果未知|提交|失败|retry|recover|unknown result|submit|failure",
        "null_stale": r"缺失|空值|失效|过期|missing|null|stale|invalid data",
        "permission_boundary": r"权限|越权|角色|数据范围|permission|authoriz|role|data scope",
        "change_propagation": r"变更|历史|下游|生效|change|historical|downstream|effective",
    }
    candidates = [f"@line {n} [{heading}]" if heading else f"@line {n}" for n, line, heading in rows if re.search(patterns[category], line, re.I)]
    if candidates:
        shown = "; ".join(candidates[:6])
        return "候选正文位置（归属待核对）：" + shown, "Candidate prose locations (ownership needs review): " + shown
    return "声明中启用了该复核类别，但正文未定位；先确认它适用的模块或范围", "This category is declared, but its body location is unknown; first identify the applicable module or scope"
STAGES = GOVERNED_INDEX



def string_list(value: Any, *, nonempty: bool = False) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value) and (bool(value) or not nonempty)


INTAKE_TEXT_FIELDS = (
    "title", "description", "request", "behavior", "brief", "outcome",
    "value_evidence", "goal", "problem", "current_behavior", "expected_behavior",
)
NARRATIVE_KEYS = set(INTAKE_TEXT_FIELDS) | {
    "text", "summary", "content", "details", "rationale", "observation",
    "facts", "items", "proposal", "scope", "acceptance", "constraints",
}


def intake_text(doc: dict[str, Any], *, include_title: bool = True) -> str:
    """Read known narrative slots, not IDs, source references or metadata.

    Structured prose may be a list or use named text wrappers. Unknown mapping
    keys are not recursively scanned just because their values contain words.
    """
    parts: list[str] = []
    active: set[int] = set()

    def visit(value: Any):
        if isinstance(value, str):
            if value.strip() and not re.fullmatch(r"(?:SRC|REQ|DEC|EVD|ROLE|MOD|UNK)-[A-Z0-9-]+", value.strip(), re.I):
                parts.append(value.strip())
        elif isinstance(value, (list, dict)) and id(value) not in active:
            active.add(id(value))
            if isinstance(value, list):
                for child in value:
                    visit(child)
            else:
                for key, child in value.items():
                    if key in NARRATIVE_KEYS:
                        visit(child)
            active.remove(id(value))

    for key in INTAKE_TEXT_FIELDS:
        if include_title or key != "title":
            visit(doc.get(key))
    return "\n".join(dict.fromkeys(parts))


def route(doc: dict[str, Any], legacy_level: str = "auto", *, body: str = "") -> dict[str, Any]:
    errors: list[str] = []
    notes: list[str] = []
    if "priority" in doc and doc["priority"] not in (None, "P0", "P1", "P2", "P3"):
        errors.append("priority must be P0, P1, P2, P3 or null")
    if "title" in doc and (not isinstance(doc["title"], str) or not doc["title"].strip()):
        errors.append("title must be a non-empty string")
    raw = doc.get("risk_facets", [])
    if not string_list(raw):
        errors.append("risk_facets must be a list of strings")
        raw = []
    risks = set(raw)
    legacy_facets = doc.get("activated_facets", [])
    if not string_list(legacy_facets):
        errors.append("activated_facets must be a string array when supplied")
    else:
        aliases = {"stateful": "state", "data_submission": "integration", "batch_io": "batch", "high_risk": "regulated"}
        risks.update(aliases.get(f, f) for f in legacy_facets if f != "ui")
    for key in ("reversible", "governed_truth_requested", "governed", "ai_behavior"):
        if key in doc and not isinstance(doc[key], bool):
            errors.append(key + " must be a boolean")
    for facet, keys in RISK_SIGNALS.items():
        if any(doc.get(key) for key in keys):
            risks.add(facet)
    ai_scope = doc.get("ai_write_scope")
    if ai_scope is not None and ai_scope not in ("none", "read_only", "draft_only", "consequential_write", "execute", "write_back"):
        errors.append("ai_write_scope must be none, read_only, draft_only, consequential_write, execute or write_back")
    if ai_scope in ("consequential_write", "execute", "write_back"):
        risks.add("irreversible_ai_write")
    elif doc.get("ai_behavior") and ai_scope is None:
        notes.append("AI write scope is undeclared; this is not evidence of consequential execution")
    if doc.get("reversible") is False:
        risks.add("irreversible")
    extra = risks - RISK_SIGNALS.keys()
    if extra:
        notes.append("Additional facets require scoped review: " + ", ".join(sorted(extra)))
    shape = doc.get("delivery_shape")
    if shape is not None and not isinstance(shape, str):
        errors.append("delivery_shape must be a string")
        shape = None
    mapped = {"requirement_card": "card", "unified_prd": "prd", "governed_truth": "prd"}.get(shape)
    mode = doc.get("artifact_mode")
    if mode is not None and (not isinstance(mode, str) or mode not in MODES):
        errors.append("artifact_mode must be direct, card or prd")
        mode = None
    if mode and mapped and shape != "governed_truth" and mode != mapped:
        errors.append("artifact_mode conflicts with delivery_shape; resolve the explicit target")
    level = doc.get("delivery_level", doc.get("level", legacy_level))
    if level is not None and level != "auto":
        if not isinstance(level, str) or level not in {"L0", "L1", "L2", "L3", "L4"}:
            errors.append("unsupported legacy level")
            level = "auto"
        else:
            notes.append("Legacy level is only a presentation hint, never a risk or evidence decision")
    if not mode:
        mode = mapped or {"L0": "direct", "L1": "card", "L2": "prd", "L3": "prd", "L4": "prd"}.get(level) or "card"
    complexity = doc.get("complexity")
    complexity_band = complexity.get("band") if isinstance(complexity, dict) else None
    if complexity_band in ("S", "M", "L", "XL"):
        notes.append(f"Declared complexity band {complexity_band} informs planning; it does not determine artifact mode, priority or prove risk coverage")
    else:
        complexity_band = None
    governed = bool(doc.get("governed_truth_requested") is True or shape == "governed_truth" or doc.get("governed") is True)
    categories = {name for name, facets in CATEGORIES.items() if facets & risks}
    if doc.get("nullable_fields") or doc.get("stale_data"):
        categories.add("null_stale")
    if doc.get("change") or doc.get("seed_refs"):
        categories.add("change_propagation")
    declared_risks = sorted(risks)
    content = inspect_content(body or intake_text(doc), intake_questions=not bool(body))
    risks.update(content["risk_facets"])
    return {
        "schema_version": VERSION, "artifact_mode": mode, "risk_facets": sorted(risks),
        "governed": governed, "semantic_review_categories": sorted(categories),
        "priority": doc.get("priority"), "notes": notes, "errors": errors,
        "complexity_band": complexity_band,
        "declared_risk_facets": declared_risks, "content_risk_candidates": content["risk_facets"],
        "content_review": content,
        "evidence_policy": "per_claim_scope_version", "authority": "recommendation_only",
        "not_proven": ["natural-language risk completeness", "business authorization", "implementation", "customer acceptance"],
    }


def language_drift(doc: dict[str, Any], body: str) -> tuple[str, str] | None:
    """Flag only obvious declared main-language mismatch, not language quality.

    Technical names, quoted examples and code are not prose-language evidence.
    A declared bilingual document intentionally has no single-language target.
    """
    declared = str(doc.get("document_language", "")).casefold()
    if doc.get("bilingual") is True or isinstance(doc.get("document_languages"), list) and len(doc["document_languages"]) > 1:
        return None
    if declared not in {"zh", "zh-cn", "zh-tw", "en", "en-us", "en-gb"}:
        return None
    samples: list[tuple[int, str]] = []
    for number, line in enumerate(prose_lines(body), 1):
        if line.lstrip().startswith(("#", ">")):
            continue
        line = re.sub(r"`[^`]*`|https?://\S+|\b[A-Z][A-Z0-9]+(?:[-_][A-Z0-9]+)+\b", "", line)
        line = re.sub(r"\[[^\]]*\]\([^)]*\)", lambda m: m[0].split("](")[0][1:], line)
        if line.strip():
            samples.append((number, line))
    prose = "\n".join(line for _, line in samples)
    chinese = len(re.findall(r"[\u4e00-\u9fff]", prose))
    words = re.findall(r"\b[a-zA-Z][a-zA-Z']+\b", prose)
    # Conservative mismatch evidence, not a target percentage or a scoring rule.
    mismatch = (declared.startswith("zh") and chinese < 12 and len(words) >= 24
                and len(re.findall(r"[.!?](?:\s|$)", prose)) >= 2)
    mismatch |= declared.startswith("en") and chinese >= 40 and len(words) < 12
    if not mismatch:
        return None
    return declared, "@line " + str(samples[0][0])


def table_content_locations(body: str) -> dict[str, bool]:
    """Locate existing Markdown columns, without judging their business correctness."""
    aliases = {
        "scope": r"模块|功能(?:模块)?|页面|范围|目标|scope|module|feature|page",
        "behavior": r"(?:调整后|修改后|变更后|目标)?行为|规则|需求(?:描述|说明)|功能(?:描述|说明)|调整后|after|(?:new |proposed )?behavior|rules?",
        "acceptance": r"验收(?:标准|条件)?|验证(?:标准|结果)?|预期结果|acceptance(?: criteria)?|verification|expected (?:result|outcome)",
    }
    def cells(line):
        return [re.sub(r"[*`]", "", c).strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
    lines = prose_lines(body)
    locations: dict[str, bool] = {}
    for index in range(len(lines) - 1):
        headers, separator = cells(lines[index]), cells(lines[index + 1])
        if len(headers) < 2 or len(separator) != len(headers) or not all(re.fullmatch(r":?-{3,}:?", c) for c in separator):
            continue
        rows = []
        for line in lines[index + 2:]:
            row = cells(line)
            if "|" not in line or len(row) != len(headers):
                break
            rows.append(row)
        for slot, pattern in aliases.items():
            columns = [i for i, label in enumerate(headers) if re.fullmatch(pattern, label, re.I)]
            if not columns:
                continue
            populated = any(row[i] and not re.fullmatch(r"[-—–…\s]+|TBD|TODO|待补(?:充)?|待填写", row[i], re.I) for row in rows for i in columns)
            locations[slot] = locations.get(slot, False) or populated
    return locations


def check_spec(doc: dict[str, Any], body: str, *, stage: str = "specify", scope: tuple[str, ...] = (), legacy_level: str = "auto") -> tuple[list[dict], dict]:
    findings: list[dict] = []
    resolved = route(doc, legacy_level, body=body)

    def add(severity: str, code: str, message: str, ref: str = "", message_en: str = ""):
        finding = dict(severity=severity, code=code, message=message, ref=ref)
        if message_en:
            finding["message_en"] = message_en
        if finding not in findings:
            findings.append(finding)

    for error in resolved["errors"]:
        add("BLOCK", "SPEC-ROUTE-CONFLICT", error)
    for note in resolved["notes"]:
        add("INFO", "SPEC-ROUTE-NOTE", note)
    for item in resolved["content_review"]["findings"]:
        add(item.get("severity", "GAP"), "SPEC-CONTENT-" + item["kind"].upper(), item["action"] + " 正文：" + item["text"], "@line " + str(item["line"]), item["action_en"] + " Text: " + item["text"])
    if stage not in STAGES:
        add("BLOCK", "SPEC-STAGE", "Unknown target stage", str(stage))
    if not body.strip():
        add("BLOCK", "SPEC-EMPTY", "Requirement body is empty")
    else:
        visible = re.sub(r"<!--.*?-->", "", body, flags=re.S)
        visible = re.sub(r"(?m)^\s*#{1,6}\s+[^\n]*$|^\s*[-=*_]{3,}\s*$", "", visible)
        if not visible.strip():
            add("BLOCK", "SPEC-EMPTY", "正文只有标题或空壳标记，没有可供实现和验收的需求。请补本次实际行为和可观察结果；不要求固定章节。", "body",
                "The body contains only headings or empty markup. Add the actual behavior and observable result; fixed sections are not required.")
    drift = language_drift(doc, body)
    if drift:
        add("GAP", "PRD-LANGUAGE-DRIFT", f"声明主语言为 {drift[0]}，可读取正文却明显使用另一语言。请核对正文或语言声明；刻意双语可声明 bilingual: true。代码、ID 和专名无需翻译。", drift[1],
            f"Declared main language is {drift[0]}, but readable prose clearly uses another language. Review the prose or declaration; intentional bilingual documents may declare bilingual: true. Keep code, IDs and proper names unchanged.")
    if doc.get("status") in ("baseline", "baselined", "approved") and re.search(r"\bdraft\b", str(doc.get("baseline_version", "")), re.I):
        add("BLOCK", "PRD-STATUS-CONTRADICTION", "Baseline status contradicts draft version")
    table_locations = table_content_locations(body)
    for slot, pattern in {
        "scope": r"范围|目标|差异|scope|goal|delta",
        "behavior": r"行为|规则|变更|结果|behavior|rule|change|result",
        "acceptance": r"验收|验证|acceptance|verification",
    }.items():
        found = re.search(r"<!--\s*ADS:" + slot + r"\s*-->", body, re.I) or re.search(r"(?im)^#{1,6}\s+[^\n]*(?:" + pattern + r")[^\n]*", body)
        if not found:
            if slot in table_locations:
                if not table_locations[slot]:
                    add("GAP", "SPEC-EMPTY-SECTION", "Located table column has no content", slot)
            else:
                add("GAP", "SPEC-REVIEW-LOCATION", "Locate or manually review " + slot + "; free-form prose is not proved incomplete", slot)
        else:
            tail = body[found.end():]
            heading = re.match(r"^\s*(#{1,6})[^\n]*\n", tail) if found.group().startswith("<!--") else re.match(r"(#{1,6})", found.group())
            level = len(heading[1]) if heading else 6
            if found.group().startswith("<!--") and heading:
                tail = tail[heading.end():]
            section = re.split(r"(?m)^#{1," + str(level) + r"}\s|<!--\s*ADS:", tail, maxsplit=1)[0]
            section = re.sub(r"(?m)^#{1,6}[^\n]*$", "", section)
            if not re.sub(r"<!--.*?-->|\s", "", section, flags=re.S):
                add("GAP", "SPEC-EMPTY-SECTION", "Located section has no content", slot)

    def objects(key: str) -> list[dict]:
        value = doc.get(key, [])
        if not isinstance(value, list) or any(not isinstance(v, dict) for v in value):
            add("BLOCK", "SPEC-DECLARATION-TYPE", key + " must be a list of objects", key)
            return []
        seen = set()
        for item in value:
            identity = item.get("id")
            if isinstance(identity, str):
                if identity in seen:
                    add("BLOCK", "PRD-DUPLICATE-UNKNOWN-DEFINITION" if key == "unknowns" else "SPEC-DUPLICATE-DEFINITION", "Duplicate definition in " + key, identity)
                seen.add(identity)
        return value

    def relevant(item: dict) -> bool:
        refs = item.get("affected_refs", item.get("scope_refs", []))
        if not string_list(refs):
            add("BLOCK", "SPEC-SCOPE-TYPE", "scope/affected refs must be a string array", str(item.get("id", "")))
            return True
        return not scope or not refs or bool(set(refs) & set(scope))

    def authority(item: dict) -> bool:
        return isinstance(item.get("actor"), str) and bool(item["actor"].strip()) and string_list(item.get("source_refs"), nonempty=True)

    for decision in objects("decisions"):
        if not relevant(decision):
            continue
        if decision.get("status") not in ("proposed", "confirmed", "approved", "superseded", "rejected"):
            add("BLOCK", "SPEC-DECISION-STATUS", "Unknown decision status", str(decision.get("id", "")))
        if decision.get("status") in ("confirmed", "approved") and not authority(decision):
            add("BLOCK", "SPEC-DECISION-AUTHORITY", "Confirmed decision requires actor and authorization source", str(decision.get("id", "")))
    disposition = doc.get("disposition")
    if disposition is not None:
        if not isinstance(disposition, dict):
            add("BLOCK", "SPEC-DISPOSITION-TYPE", "disposition must be an object")
        elif disposition.get("status") not in ("proposed", "confirmed"):
            add("BLOCK", "SPEC-DISPOSITION-STATUS", "Use proposed or confirmed; gate status is separate")
        elif disposition.get("status") == "confirmed" and not authority(disposition):
            add("BLOCK", "SPEC-DISPOSITION-AUTHORITY", "Confirmed disposition requires actor and authorization source")
        elif disposition.get("status") == "proposed" and doc.get("status") in ("deferred", "rejected", "cancelled"):
            add("BLOCK", "SPEC-DISPOSITION-NOT-AUTHORIZED", "A proposal cannot change the requirement lifecycle")
        if isinstance(disposition, dict) and (not all(isinstance(disposition.get(k), str) and disposition[k].strip() for k in ("outcome", "reason")) or not string_list(disposition.get("scope_refs"), nonempty=True)):
            add("BLOCK", "SPEC-DISPOSITION-CONTENT", "Disposition needs outcome, reason and applicable scope")
    unknowns = [dict(item, _origin="frontmatter unknowns", _fields=list(item)) for item in objects("unknowns")]
    for item in unknowns:
        item["_field_origins"] = {key: item["_origin"] for key in item["_fields"]}
    # Read the human table as an alternative to metadata, not as an obligation
    # to maintain a second copy. A decorated template token has the same meaning.
    known = {u.get("id"): u for u in unknowns if isinstance(u.get("id"), str)}
    for row in unknown_rows("\n".join(prose_lines(body))):
        row.setdefault("_origin", "body legacy row")
        row.setdefault("_fields", [key for key in row if not key.startswith("_")])
        row["_field_origins"] = {key: row["_origin"] for key in row.get("_fields", [])}
        if row["id"] in known:
            existing = known[row["id"]]
            if relevant(existing):
                for key in ("status", "priority", "blocks_stage"):
                    if key in existing.get("_fields", existing) and key in row.get("_fields", row) and row.get(key) and existing.get(key):
                        def comparable(value):
                            values = value if isinstance(value, list) else [value]
                            return sorted({"closed" if contract_token(v) in CLOSED_UNKNOWN else contract_token(v) for v in values})
                        if comparable(row[key]) != comparable(existing[key]):
                            add("BLOCK", "PRD-UNKNOWN-METADATA-DRIFT",
                                f"{existing.get('_field_origins', {}).get(key, existing.get('_origin'))} vs {row.get('_origin')}: {key} differs ({existing[key]!r} vs {row[key]!r})", row["id"])
                for key in row.get("_fields", []):
                    if key not in existing.get("_fields", []) or not existing.get(key):
                        existing[key] = row.get(key)
                        existing["_fields"] = list(set(existing.get("_fields", [])) | {key})
                        existing.setdefault("_field_origins", {})[key] = row["_origin"]
                if existing.get("status"):
                    existing["_status_unlocated"] = False
            continue
        unknowns.append(row)
        known[row["id"]] = row
    buckets = {key: set() for key in ("open", "declared_open_p0", "open_priority_unspecified", "blocking_now", "status_unresolved", "invalid_blocking_stage", "out_of_scope")}
    for index, unknown in enumerate(unknowns):
        identity = str(unknown.get("id") or f"<unknown-row-{index + 1}>")
        if not relevant(unknown):
            buckets["out_of_scope"].add(identity)
            continue
        status = contract_token(unknown.get("status"))
        if unknown.get("_status_unlocated"):
            buckets["status_unresolved"].add(identity)
            add("GAP", "SPEC-UNKNOWN-STATUS-UNLOCATED", "Cannot locate status in " + str(unknown.get("_origin")) + "; verify the existing declaration, do not assume closed", str(unknown.get("id", "")))
            continue
        if status not in OPEN_UNKNOWN | CLOSED_UNKNOWN:
            buckets["status_unresolved"].add(identity)
            add("BLOCK", "SPEC-UNKNOWN-STATUS", "Use an explicit open/pending/blocked or closed/resolved/superseded status", str(unknown.get("id", "")))
            continue
        if status in CLOSED_UNKNOWN:
            closure = unknown.get("resolution_ref")
            if (not isinstance(closure, str) or not closure.strip() or closure.strip() in ("-", "无", "待补", "N/A")) and not string_list(unknown.get("source_refs"), nonempty=True):
                add("BLOCK", "SPEC-UNKNOWN-CLOSURE", "Closed unknown needs a resolution/decision/source reference", str(unknown.get("id", "")))
            continue
        buckets["open"].add(identity)
        priority = contract_token(unknown.get("priority"))
        if priority == "p0":
            buckets["declared_open_p0"].add(identity)
        elif priority not in ("p1", "p2", "p3"):
            buckets["open_priority_unspecified"].add(identity)
        stop = unknown.get("blocks_stage", "baseline")
        stops = stop if isinstance(stop, list) else [stop]
        stops = [contract_token(s) for s in stops]
        if not stops or any(not isinstance(s, str) or (s not in STAGES and s != "none") for s in stops):
            buckets["invalid_blocking_stage"].add(identity)
            add("BLOCK", "SPEC-UNKNOWN-STAGE", "Unrecognized blocking stage", str(unknown.get("id", "")))
            continue
        relations = [blocking_relation(stage, s) for s in stops]
        reached = any(value is True for value in relations)
        if not reached and None in relations:
            add("GAP", "SPEC-UNKNOWN-ACTIVITY-SCOPE", "Prototype/change activities are not a linear stage order; retain the unknown and identify this delivery's actual dependencies", identity)
        if reached:
            buckets["blocking_now"].add(identity)
        refs = unknown.get("affected_refs", unknown.get("scope_refs", []))
        affected = ", ".join(refs) if string_list(refs, nonempty=True) else "scope not declared"
        add("BLOCK" if reached else "GAP", "SPEC-OPEN-DECISION",
            f"{identity} 仍为 {status}；影响：{affected}；阻断起点：{', '.join(stops)}；当前阶段：{stage}。整体签认或验收记录不能代替该项决定。若实际已解决，补真实决定/来源引用并关闭此项；否则保留 open，明确本轮不受影响的范围或有授权的有限例外，不能自动放行依赖行为。", identity,
            f"Open decision {identity} is still {status}; affected: {affected}; blocks from: {', '.join(stops)}; current stage: {stage}. A global signoff or acceptance record cannot resolve this item. If actually resolved, record its real decision/source and close it; otherwise retain it and identify unaffected scope or an authorized bounded exception. Do not automatically release dependent behavior.")
    resolved["unknown_summary"] = {
        "schema_version": 1, "stage": stage, "scope_refs": list(scope or []),
        "counts": {key: len(ids) for key, ids in buckets.items()},
        "refs": {key: sorted(ids) for key, ids in buckets.items()},
        "counting_rule": "unique declared unknown IDs after merging metadata/body; buckets overlap; no inferred priority; declaration conflicts remain findings; source authenticity not proven",
    }
    # Legacy artifacts can repeat metadata; detect disagreement without requiring
    # duplicate authoring. New artifacts should maintain each fact only once.
    headers = []
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            headers = []
            continue
        cells = [c.strip().strip(chr(96)) for c in line.strip().strip("|").split("|")]
        if not headers:
            headers = cells
            continue
        for header, value in zip(headers, cells):
            if not scope and re.search(r"下一状态|next state", header, re.I) and re.search(r"API-[A-Z0-9-]+", value):
                add("BLOCK", "PRD-STATE-SEMANTIC-POLLUTION", "Transition destination contains an API identifier")
    for conflict in objects("source_conflicts"):
        if not relevant(conflict):
            continue
        if conflict.get("status", "open") in ("resolved", "superseded"):
            if not conflict.get("resolution_ref"):
                add("BLOCK", "SPEC-CONFLICT-CLOSURE", "Resolved conflict needs its decision reference", str(conflict.get("id", "")))
        else:
            add("BLOCK" if blocking_relation(stage, "baseline") is True else "GAP", "SPEC-SOURCE-CONFLICT", "Resolve this topic before baselining", str(conflict.get("id", "")))
    covered: dict[str, set[str]] = {}
    expected_scope = list(scope) or doc.get("requirement_ids", doc.get("scope_refs", []))
    if not string_list(expected_scope):
        add("BLOCK", "SPEC-SCOPE-TYPE", "requirement_ids/scope_refs must be a string array")
        expected_scope = []
    for review in objects("semantic_reviews"):
        if not relevant(review):
            continue
        category = review.get("category")
        if not isinstance(category, str) or category not in CATEGORIES:
            add("BLOCK", "SPEC-REVIEW-CATEGORY", "Unknown review category", str(category))
            continue
        result = review.get("result")
        if result not in ("pass", "fail", "not_run", "blocked", "not_applicable"):
            add("BLOCK", "SPEC-REVIEW-RESULT", "Invalid review result", category)
        elif result == "pass":
            if not string_list(review.get("scope_refs"), nonempty=True) or not string_list(review.get("source_refs"), nonempty=True) or not all(isinstance(review.get(k), str) and review[k].strip() for k in ("reviewer", "evidence_ref", "baseline_version")):
                add("BLOCK", "SPEC-REVIEW-EVIDENCE", "Pass needs scope, source, reviewer, baseline and evidence reference", category)
            elif str(review["baseline_version"]) != str(doc.get("baseline_version", "")):
                add("BLOCK", "SPEC-REVIEW-BASELINE", "Review belongs to another baseline", category)
            else:
                covered.setdefault(category, set()).update(review["scope_refs"])
        elif result == "fail":
            add("BLOCK", "SPEC-SEMANTIC-FAILURE", str(review.get("finding", "Unresolved semantic finding")), category)
        elif result == "not_applicable":
            if not review.get("reason") or not review.get("reviewer") or not string_list(review.get("scope_refs"), nonempty=True) or review.get("baseline_version") != doc.get("baseline_version"):
                add("BLOCK", "SPEC-REVIEW-EXCLUSION", "Exclusion needs scope, reason, reviewer and current baseline", category)
            else:
                covered.setdefault(category, set()).update(review["scope_refs"])
    for category in resolved["semantic_review_categories"]:
        missing = set(expected_scope) - covered.get(category, set())
        if not expected_scope or missing:
            location_zh, location_en = semantic_review_location(body, category, sorted(missing))
            title_zh, action_zh = semantic_review_guidance(category)
            title_en, action_en = semantic_review_guidance(category, "en-US")
            sources = doc.get("source_refs", [])
            source_zh = "文档声明的来源（须核对本项适用性）：" + ", ".join(sources) if string_list(sources, nonempty=True) else "尚未定位本项原始来源，请回查已有约定"
            source_en = "Document-declared sources (check applicability to this item): " + ", ".join(sources) if string_list(sources, nonempty=True) else "No source is located for this item; consult the existing agreement"
            add("GAP", "SPEC-SEMANTIC-NOT-PROVEN",
                f"{title_zh}尚无当前范围的复核证据。{location_zh}。{source_zh}。下一步：{action_zh}在已有模块或评阅记录中注明真实结论、所核对的来源及当前基线；未复核保持缺口，不能补写 pass。",
                category + ": " + location_zh,
                f"{title_en} lacks review evidence for the current scope. {location_en}. {source_en}. Next: {action_en} Record the actual result, checked source and current baseline in the existing module or review record; keep an unreviewed gap rather than fabricating a pass.")
    resolved["semantic_coverage"] = {"required": resolved["semantic_review_categories"], "expected_scope": expected_scope, "declared_covered": {k: sorted(v) for k, v in covered.items()}, "proof": "declaration_checks_only; references and reviewer claims are not independently authenticated"}
    return findings, resolved
