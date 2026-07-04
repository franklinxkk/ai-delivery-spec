#!/usr/bin/env python3
"""Validate domain routing, composition, and marker isolation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"


@dataclass(frozen=True)
class DomainRule:
    domain_id: str
    file: str
    trigger_terms: tuple[str, ...]
    unique_markers: tuple[str, ...]


@dataclass(frozen=True)
class Probe:
    name: str
    prompt: str
    expected_domains: tuple[str, ...]


DOMAIN_RULES = (
    DomainRule(
        "traffic",
        "domain-traffic.md",
        ("traffic safety", "transport supervision", "道路运输", "交通安全", "运管"),
        ("standards_corpus_register", "regulated_action_human_accountability", "shadow_test_data"),
    ),
    DomainRule(
        "oa",
        "domain-oa.md",
        ("oa", "collaborative office", "official document", "unified todo", "协同办公", "公文", "统一待办"),
        ("workflow_human_gate", "document_authority", "todo_sla_close_guard", "org_permission_scope", "ai_office_assistant_boundary"),
    ),
    DomainRule(
        "crm",
        "domain-crm.md",
        ("crm", "sales pipeline", "customer 360", "customer service", "客户经营", "商机", "客户360"),
        ("lead_to_cash_trace", "ticket_to_demand_trace", "customer360_masking", "sla_response_task"),
    ),
    DomainRule(
        "data_mart",
        "domain-data-mart.md",
        ("data mart", "chatbi", "indicator library", "report template", "数据集市", "指标库", "智能问数"),
        ("ai_data_discover_pm_happy_path", "ai_data_specify_coding_acceptance_test_path", "data_agent_contract"),
    ),
    DomainRule(
        "ai_native",
        "domain-ai-native.md",
        ("ai native", "agentic system", "multi-agent runtime", "ai 原生", "智能体系统"),
        ("Work outcome first", "Context before model", "ai_native_discover_domain_exception_path"),
    ),
    DomainRule(
        "education_it",
        "domain-education-it.md",
        ("higher-education", "academic affairs", "student affairs", "教务", "学工", "高校"),
        ("student_privacy_scope", "grade_human_approval", "obe_evidence_trace"),
    ),
    DomainRule(
        "medical_hospital_it",
        "domain-medical-hospital-it.md",
        ("hospital", "emr", "his", "clinical workflow", "医院", "电子病历", "临床"),
        ("clinical_human_gate", "critical_value_ack_sla", "signed_record_amendment"),
    ),
)


PROBES = (
    Probe(
        "traffic transport supervision",
        "Write a PRD for a transport supervision traffic safety SaaS with enterprise risk alerts.",
        ("traffic",),
    ),
    Probe(
        "OA workflow approval",
        "Write a PRD for an OA collaborative office system with unified todo, workflow approval, official document and meeting resolution tracking.",
        ("oa",),
    ),
    Probe(
        "CRM customer response",
        "Write a PRD for a CRM customer response center with lead, opportunity, customer 360 and service tickets.",
        ("crm",),
    ),
    Probe(
        "AI data mart",
        "Write a PRD for a data mart with indicator library, report templates, ChatBI and Data Agent.",
        ("data_mart",),
    ),
    Probe(
        "AI native agentic system",
        "Brainstorm an AI native agentic system with multi-agent runtime, human gate and fallback.",
        ("ai_native",),
    ),
    Probe(
        "higher education IT",
        "Write a PRD for higher-education academic affairs, student affairs and teaching quality.",
        ("education_it",),
    ),
    Probe(
        "medical hospital IT",
        "Write a PRD for hospital HIS, EMR and clinical workflow with medical record signature.",
        ("medical_hospital_it",),
    ),
    Probe(
        "CRM with approval should stay CRM",
        "Write a CRM PRD with customer 360, service tickets and internal approval workflow.",
        ("crm",),
    ),
    Probe(
        "OA with AI assistant should stay OA",
        "Write an OA PRD with AI office assistant, document summary, unified todo and workflow approval.",
        ("oa",),
    ),
    Probe(
        "CRM plus OA composition",
        "Write a PRD for CRM customer service integrated with OA unified todo and workflow approval.",
        ("oa", "crm"),
    ),
    Probe(
        "CRM plus data mart composition",
        "Write a PRD for CRM customer 360 with a data mart, indicator library and ChatBI dashboard.",
        ("crm", "data_mart"),
    ),
    Probe(
        "Traffic plus data mart composition",
        "Write a PRD for transport supervision traffic safety with a data mart and report templates.",
        ("traffic", "data_mart"),
    ),
    Probe(
        "AI native plus data mart composition",
        "Brainstorm an AI native Data Agent over a governed data mart with multi-agent runtime.",
        ("data_mart", "ai_native"),
    ),
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def detect_domains(prompt: str) -> tuple[str, ...]:
    value = prompt.lower()
    matches: list[str] = []
    for rule in DOMAIN_RULES:
        if any(term_matches(value, term.lower()) for term in rule.trigger_terms):
            matches.append(rule.domain_id)
    return tuple(matches)


def term_matches(value: str, term: str) -> bool:
    if term.isascii() and term.replace("-", "").replace("_", "").isalnum() and len(term) <= 4:
        return re.search(rf"\b{re.escape(term)}\b", value) is not None
    return term in value


def validate_prompt_routing(failures: list[str]) -> None:
    for probe in PROBES:
        actual = detect_domains(probe.prompt)
        if actual != probe.expected_domains:
            failures.append(
                f"{probe.name}: expected domains {probe.expected_domains}, got {actual}"
            )


def validate_marker_isolation(failures: list[str]) -> None:
    texts = {rule.domain_id: read(REFERENCES / rule.file) for rule in DOMAIN_RULES}
    for owner in DOMAIN_RULES:
        for other in DOMAIN_RULES:
            if owner.domain_id == other.domain_id:
                continue
            for marker in owner.unique_markers:
                if marker.lower() in texts[other.domain_id].lower():
                    failures.append(
                        f"marker bleed: {marker!r} from {owner.domain_id} appears in {other.file}"
                    )


def validate_runtime_neutrality(failures: list[str]) -> None:
    skill = read(ROOT / "SKILL.md").lower()
    for rule in DOMAIN_RULES:
        if rule.file.lower() in skill:
            failures.append(
                f"SKILL.md should not directly load domain module {rule.file}; route via advanced-extensions.md"
            )


def main() -> int:
    failures: list[str] = []
    validate_prompt_routing(failures)
    validate_marker_isolation(failures)
    validate_runtime_neutrality(failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    print(
        f"PASS: {len(PROBES)} domain-routing/composition probes and "
        f"{len(DOMAIN_RULES)} domain modules are isolated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
