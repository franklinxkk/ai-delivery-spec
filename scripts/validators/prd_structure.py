#!/usr/bin/env python3
"""Small structural checks shared by PRD validators and the runtime gate.

The checks deliberately avoid pretending to understand the business.  They
reject empty templates and keyword shells by requiring concrete contract rows
or prose that binds stable IDs to actors, transitions, results and evidence.
"""

from __future__ import annotations

import re


HEADING = re.compile(r"(?m)^(#{2,4})\s+(.+?)\s*$")
TABLE_SEPARATOR = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*$")
PLACEHOLDER = re.compile(r"\b(?:placeholder|tbd|todo|lorem ipsum)\b|待补充|待完善|占位(?:内容|文本)", re.I)


def _nonempty_cells(line: str) -> list[str]:
    if not line.lstrip().startswith("|"):
        return []
    return [cell.strip() for cell in line.strip().strip("|").split("|") if cell.strip()]


def _section_bodies(raw: str) -> list[tuple[str, str]]:
    matches = list(HEADING.finditer(raw))
    bodies: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        bodies.append((match.group(2).strip(), raw[match.end():end].strip()))
    return bodies


def _has_row(raw: str, id_pattern: str, minimum_cells: int, required_terms: tuple[str, ...] = ()) -> bool:
    for line in raw.splitlines():
        if not re.search(id_pattern, line, re.I):
            continue
        cells = _nonempty_cells(line)
        lowered = line.lower()
        if len(cells) >= minimum_cells and all(term.lower() in lowered for term in required_terms):
            return True
    return False


def analyze(raw: str, *, full_prd: bool = True) -> list[str]:
    """Return bounded structural failures without generating replacement text."""
    failures: list[str] = []
    lowered = raw.lower()

    if PLACEHOLDER.search(raw):
        failures.append("contains placeholder/TBD text; a baseline needs decided content or an owned unknown")

    rows = []
    for line in raw.splitlines():
        if line.lstrip().startswith("|") and not TABLE_SEPARATOR.match(line):
            normalized = re.sub(r"\s+", " ", line.strip().lower())
            if normalized.count("|") >= 2:
                rows.append(normalized)
    if rows:
        duplicate_count = len(rows) - len(set(rows))
        if duplicate_count >= 3 and len(set(rows)) / len(rows) < 0.75:
            failures.append("repeated template/table rows dominate the contract; replace them with distinct behavior mappings")

    if full_prd:
        sparse = []
        for title, body in _section_bodies(raw):
            content = re.sub(r"[`#|:*_\-]", "", body).strip()
            if len(content) < 24:
                sparse.append(title)
        if len(sparse) >= 4:
            failures.append("multiple empty or keyword-only sections: " + ", ".join(sparse[:6]))

    journey_ok = False
    for title, body in _section_bodies(raw):
        if not re.search(r"角色旅程|用户旅程|role journey", title, re.I):
            continue
        segment = title + "\n" + body
        journey_ok = bool(
            re.search(r"\bROLE-[A-Z0-9-]+\b", segment, re.I)
            and re.search(r"\bFLOW-[A-Z0-9-]+\b", segment, re.I)
            and re.search(r"进入|打开|提交|审批|处理|查看|选择|创建|更新|失败|恢复|enter|open|submit|approve|create|update|fail|recover", segment, re.I)
            and re.search(r"结果|状态|完成|成功|交接|可见|result|state|success|handoff|visible", segment, re.I)
        )
        if journey_ok:
            break
    if not journey_ok:
        failures.append("role journey does not bind ROLE/FLOW to concrete user steps, handoff/result and recovery")

    transition_ok = bool(
        re.search(r"\b(?:STATE|STM|SM)-[A-Z0-9-]+\b", raw, re.I)
        and (
            re.search(r"[A-Za-z0-9_\u4e00-\u9fff]+\s*(?:→|->)\s*[A-Za-z0-9_\u4e00-\u9fff]+", raw)
            or (re.search(r"当前状态|current state", lowered) and re.search(r"下一状态|next state", lowered))
        )
        and re.search(r"守卫|允许角色|前置|guard|allowed role|precondition", lowered)
        and re.search(r"失败|拒绝|异常|failure|denied|error", lowered)
    )
    if not transition_ok:
        failures.append("state contract lacks a concrete transition with guard/allowed role and failure result")

    action_ok = _has_row(raw, r"\bACT-[A-Z0-9-]+\b", 6)
    if not action_ok:
        for paragraph in re.split(r"\n\s*\n", raw):
            if (
                re.search(r"\bACT-[A-Z0-9-]+\b", paragraph, re.I)
                and re.search(r"可见结果|visible result", paragraph, re.I)
                and re.search(r"领域结果|业务结果|domain result", paragraph, re.I)
                and re.search(r"失败|恢复|failure|recovery", paragraph, re.I)
                and re.search(r"\bAC-[A-Z0-9-]+\b", paragraph, re.I)
            ):
                action_ok = True
                break
    if not action_ok:
        failures.append("no concrete ACT contract binds actor/precondition, visible result, domain result, failure/recovery and AC")

    field_ok = _has_row(raw, r"\bFLD-[A-Z0-9-]+\b", 7)
    if not field_ok:
        failures.append("field dictionary has no substantive FLD row with meaning, source/edit authority and validation")

    acceptance_ok = _has_row(raw, r"\bAC-[A-Z0-9-]+\b", 7)
    if not acceptance_ok:
        yaml_ac = re.search(
            r"(?s)-\s+id:\s*AC-[A-Z0-9-]+.*?preconditions:\s*\[[^\]]+\].*?steps:\s*\[[^\]]+\].*?expected_visible:\s*[^\n\[\]\"'].*?expected_domain:\s*[^\n\[\]\"'].*?negative_cases:\s*\[[^\]]+\].*?evidence_required:\s*\[[^\]]+\]",
            raw,
            re.I,
        )
        acceptance_ok = bool(yaml_ac)
    if not acceptance_ok:
        failures.append("acceptance is not executable: AC needs preconditions, steps/input, visible/domain results, negative case and evidence")

    trace_ok = any(
        re.search(r"\bREQ-[A-Z0-9-]+\b", line, re.I)
        and re.search(r"\bAC-[A-Z0-9-]+\b", line, re.I)
        and len(_nonempty_cells(line)) >= 5
        for line in raw.splitlines()
    )
    if not trace_ok:
        failures.append("traceability has no substantive REQ-to-behavior-to-AC mapping row")

    return failures[:20]
