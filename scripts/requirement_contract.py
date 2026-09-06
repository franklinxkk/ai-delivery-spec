"""Shared task routing and bounded declaration checks. Never authorizes business decisions."""
from __future__ import annotations
import re
from typing import Any
import yaml


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

VERSION = "5.5.0"
MODES = {"direct", "card", "prd"}
RISK_SIGNALS = {
    "state": ("states", "cross_module_state", "approval", "workflow"),
    "authority": ("data_lineage",),
    "integration": ("integrations", "data_submission", "data_reporting"),
    "metric": ("metric_caliber", "metrics"),
    "permission": ("tenant_isolation", "permissions"),
    "privacy": ("sensitive_data",),
    "regulated": ("compliance", "clinical", "safety_critical"),
    "migration": ("migration", "version_compatibility"),
    "irreversible": ("irreversible_write", "money"),
    "irreversible_ai_write": ("consequential_ai_write",),
    "strong_audit": ("strong_audit", "audit_required"),
    "batch": ("batch_io",),
}
CATEGORIES = {
    "state_authority": {"state", "authority"},
    "metric_definition": {"metric"},
    "recovery": {"state", "integration", "batch", "irreversible", "irreversible_ai_write"},
    "null_stale": {"metric", "integration"},
    "permission_boundary": {"permission", "privacy"},
    "change_propagation": {"migration"},
}
STAGES = {s: n for n, s in enumerate(("frame", "explore", "intake", "clarify", "specify", "prototype", "review", "baseline", "implementation", "acceptance", "closed"))}
STAGES["inventory"] = -1


def string_list(value: Any, *, nonempty: bool = False) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value) and (bool(value) or not nonempty)


def route(doc: dict[str, Any], legacy_level: str = "auto") -> dict[str, Any]:
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
    if doc.get("ai_behavior") and doc.get("ai_write_scope") not in ("none", "read_only", "draft_only"):
        risks.add("irreversible_ai_write")
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
    governed = bool(doc.get("governed_truth_requested") is True or shape == "governed_truth" or doc.get("governed") is True)
    categories = {name for name, facets in CATEGORIES.items() if facets & risks}
    if doc.get("nullable_fields") or doc.get("stale_data"):
        categories.add("null_stale")
    if doc.get("change") or doc.get("seed_refs"):
        categories.add("change_propagation")
    return {
        "schema_version": VERSION, "artifact_mode": mode, "risk_facets": sorted(risks),
        "governed": governed, "semantic_review_categories": sorted(categories),
        "priority": doc.get("priority"), "notes": notes, "errors": errors,
        "evidence_policy": "per_claim_scope_version", "authority": "recommendation_only",
        "not_proven": ["natural-language risk completeness", "business authorization", "implementation", "customer acceptance"],
    }


def check_spec(doc: dict[str, Any], body: str, *, stage: str = "specify", scope: tuple[str, ...] = (), legacy_level: str = "auto") -> tuple[list[dict], dict]:
    findings: list[dict] = []
    resolved = route(doc, legacy_level)

    def add(severity: str, code: str, message: str, ref: str = ""):
        findings.append(dict(severity=severity, code=code, message=message, ref=ref))

    for error in resolved["errors"]:
        add("BLOCK", "SPEC-ROUTE-CONFLICT", error)
    for note in resolved["notes"]:
        add("INFO", "SPEC-ROUTE-NOTE", note)
    if stage not in STAGES:
        add("BLOCK", "SPEC-STAGE", "Unknown target stage", str(stage))
    if not body.strip():
        add("BLOCK", "SPEC-EMPTY", "Requirement body is empty")
    if doc.get("status") in ("baseline", "baselined", "approved") and re.search(r"\bdraft\b", str(doc.get("baseline_version", "")), re.I):
        add("BLOCK", "PRD-STATUS-CONTRADICTION", "Baseline status contradicts draft version")
    for slot, pattern in {
        "scope": r"范围|目标|差异|scope|goal|delta",
        "behavior": r"行为|规则|变更|结果|behavior|rule|change|result",
        "acceptance": r"验收|验证|acceptance|verification",
    }.items():
        found = re.search(r"<!--\s*ADS:" + slot + r"\s*-->", body, re.I) or re.search(r"(?im)^#{1,6}\s+[^\n]*(?:" + pattern + r")[^\n]*", body)
        if not found:
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
    unknowns = objects("unknowns")
    for unknown in unknowns:
        if not relevant(unknown):
            continue
        if unknown.get("status") in ("resolved", "closed", "superseded"):
            if not unknown.get("resolution_ref") and not unknown.get("source_refs"):
                add("BLOCK", "SPEC-UNKNOWN-CLOSURE", "Closed unknown needs a resolution/decision/source reference", str(unknown.get("id", "")))
            continue
        stop = unknown.get("blocks_stage", "baseline")
        stops = stop if isinstance(stop, list) else [stop]
        if any(not isinstance(s, str) or (s not in STAGES and s != "none") for s in stops):
            add("BLOCK", "SPEC-UNKNOWN-STAGE", "Unrecognized blocking stage", str(unknown.get("id", "")))
            continue
        reached = any(STAGES.get(stage, 0) >= STAGES[s] for s in stops if s in STAGES)
        add("BLOCK" if reached else "GAP", "SPEC-OPEN-DECISION", "Dependent decision remains open; fallback must not decide it", str(unknown.get("id", "")))
    # Legacy artifacts can repeat metadata; detect disagreement without requiring
    # duplicate authoring. New artifacts should maintain each fact only once.
    by_id = {u["id"]: u for u in unknowns if isinstance(u.get("id"), str) and relevant(u)}
    headers = []
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            headers = []
            continue
        cells = [c.strip().strip(chr(96)) for c in line.strip().strip("|").split("|")]
        if not headers:
            headers = cells
            continue
        ref = next((c for c in cells if c in by_id), None)
        for header, value in zip(headers, cells):
            if not scope and re.search(r"下一状态|next state", header, re.I) and re.search(r"API-[A-Z0-9-]+", value):
                add("BLOCK", "PRD-STATE-SEMANTIC-POLLUTION", "Transition destination contains an API identifier")
            if not ref:
                continue
            key = "priority" if re.search(r"优先级|priority", header, re.I) else "blocks_stage" if re.search(r"阻断|blocks.?stage", header, re.I) else "status" if re.search(r"状态|status", header, re.I) else None
            if key and key in by_id[ref] and value in {"P0", "P1", "P2", "P3", "open", "blocked", "resolved", "closed", *STAGES} and value != by_id[ref][key]:
                add("BLOCK", "PRD-UNKNOWN-METADATA-DRIFT", "Human and structured unknown declarations disagree: " + key, ref)
    for conflict in objects("source_conflicts"):
        if not relevant(conflict):
            continue
        if conflict.get("status", "open") in ("resolved", "superseded"):
            if not conflict.get("resolution_ref"):
                add("BLOCK", "SPEC-CONFLICT-CLOSURE", "Resolved conflict needs its decision reference", str(conflict.get("id", "")))
        else:
            add("BLOCK" if STAGES.get(stage, 0) >= STAGES["baseline"] else "GAP", "SPEC-SOURCE-CONFLICT", "Resolve this topic before baselining", str(conflict.get("id", "")))
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
            add("GAP", "SPEC-SEMANTIC-NOT-PROVEN", "Scoped semantic review is not evidenced: " + (", ".join(sorted(missing)) or "declare the evaluated scope"), category)
    resolved["semantic_coverage"] = {"required": resolved["semantic_review_categories"], "expected_scope": expected_scope, "declared_covered": {k: sorted(v) for k, v in covered.items()}, "proof": "declaration_checks_only; references and reviewer claims are not independently authenticated"}
    return findings, resolved
