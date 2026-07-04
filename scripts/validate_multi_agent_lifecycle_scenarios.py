#!/usr/bin/env python3
"""Validate parseable multi-agent lifecycle matrices in built-in domains."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"

STAGES = [
    "Discover",
    "Specify",
    "Plan",
    "Tasks",
    "Build/Verify",
    "Launch",
    "Learn/Retire",
]

AGENTS = [
    "PM Agent",
    "Domain Expert Agent",
    "Architecture / Data / AI Agent",
    "QA Agent",
    "Coding Agent",
]

PATH_TYPES = [
    "happy_path",
    "exception_path",
    "permission_privacy_path",
    "lifecycle_transition",
    "acceptance_test_path",
]

REQUIRED_COLUMNS = [
    "domain_id",
    "stage",
    "reviewer_agent",
    "path_type",
    "scenario_ref",
    "evidence_ref",
    "blocking_question",
    "expected_result",
    "test_marker",
    "verdict",
]

SHARED_SECTIONS = [
    "Domain Purpose",
    "Vocabulary",
    "Aggregates and Entities",
    "Domain Events",
    "State Machines",
    "Metric / Indicator Governance",
    "AI Context Sources",
    "Content / Knowledge Assets",
    "Core Workflows",
    "Role Path Patterns",
    "UI / Mobile Patterns",
    "Policy / Privacy Constraints",
    "Domain Test Scenarios",
    "Multi-Agent Lifecycle Verification Matrix",
    "Acceptance Checklist",
]

CODING_MARKERS = [
    "ac_structured",
    "data-testid",
    "data-action",
    "data-state",
    "data-api",
    "data-method",
    "manifest.json",
    "source_of_truth_order",
]

DOMAINS = {
    "traffic": {
        "file": "domain-traffic.md",
        "markers": [
            "standards_corpus_register",
            "regulated_action_human_accountability",
            "shadow_test_data",
        ],
    },
    "crm": {
        "file": "domain-crm.md",
        "markers": [
            "lead_to_cash_trace",
            "ticket_to_demand_trace",
            "sla_response_task",
            "customer360_masking",
        ],
    },
    "oa": {
        "file": "domain-oa.md",
        "markers": [
            "workflow_human_gate",
            "document_authority",
            "todo_sla_close_guard",
            "org_permission_scope",
            "ai_office_assistant_boundary",
        ],
    },
    "ai_data": {
        "file": "domain-data-mart.md",
        "markers": [
            "context_freshness",
            "ontology_semantic_contract",
            "eval_fallback",
            "human_gate",
            "write_scope",
            "agent_writeback_blocked",
            "rollback",
        ],
    },
    "ai_native": {
        "file": "domain-ai-native.md",
        "markers": [
            "First-Principles Product Logic",
            "Work outcome first",
            "Context before model",
            "Workflow before chat",
            "context_freshness",
            "ontology_semantic_contract",
            "eval_fallback",
            "human_gate",
            "write_scope",
            "agent_writeback_blocked",
            "rollback",
        ],
    },
    "education_it": {
        "file": "domain-education-it.md",
        "markers": [
            "student_privacy_scope",
            "grade_human_approval",
            "obe_evidence_trace",
            "dashboard_privacy_threshold",
        ],
    },
    "medical_hospital_it": {
        "file": "domain-medical-hospital-it.md",
        "markers": [
            "clinical_human_gate",
            "critical_value_ack_sla",
            "consent_check",
            "signed_record_amendment",
            "regulatory_freshness_source",
        ],
    },
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(failures: list[str], message: str) -> None:
    failures.append(message)


def require_markers(name: str, text: str, markers: list[str], failures: list[str]) -> None:
    lower = text.lower()
    for marker in markers:
        if marker.lower() not in lower:
            fail(failures, f"{name} missing marker: {marker}")


def split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def is_separator(row: list[str]) -> bool:
    return bool(row) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in row)


def extract_matrix_section(text: str) -> str:
    match = re.search(r"^## Multi-Agent Lifecycle Verification Matrix\s*$", text, re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def parse_matrix(section: str) -> list[dict[str, str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        row = split_table_row(line)
        if not row or is_separator(row):
            continue
        rows.append(row)
    if not rows:
        return []

    headers = [cell.strip() for cell in rows[0]]
    parsed: list[dict[str, str]] = []
    for raw in rows[1:]:
        parsed.append(
            {
                header: raw[index].strip() if index < len(raw) else ""
                for index, header in enumerate(headers)
            }
        )
    return parsed


def validate_framework(failures: list[str]) -> None:
    skill = read(ROOT / "SKILL.md")
    delivery = read(REFERENCES / "delivery-core.md")
    readme = read(ROOT / "README.md")
    cli = read(ROOT / "scripts" / "ai_delivery_spec_cli.py")

    require_markers(
        "SKILL.md lifecycle",
        skill,
        ["Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire"],
        failures,
    )
    require_markers(
        "delivery-core multi-agent lifecycle",
        delivery,
        [
            "Multi-Agent Lifecycle Verification",
            "Before final release, publication, GitHub submission, or customer handoff",
            *STAGES,
            *AGENTS,
            "happy path",
            "exception path",
            "permission/privacy path",
            "lifecycle transition",
            "acceptance/test path",
        ],
        failures,
    )
    require_markers(
        "README validation",
        readme,
        ["validate_multi_agent_lifecycle_scenarios.py", "AI Native / Agentic Systems"],
        failures,
    )
    require_markers("helper CLI", cli, ["validate_multi_agent_lifecycle_scenarios.py"], failures)


def validate_matrix(domain: str, text: str, failures: list[str]) -> None:
    section = extract_matrix_section(text)
    if not section:
        fail(failures, f"{domain} missing Multi-Agent Lifecycle Verification Matrix section")
        return

    rows = parse_matrix(section)
    if not rows:
        fail(failures, f"{domain} matrix is empty or unparsable")
        return

    columns = set(rows[0])
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in columns]
    if missing_columns:
        fail(failures, f"{domain} matrix missing columns: {', '.join(missing_columns)}")
        return

    expected_count = len(STAGES) * len(AGENTS)
    if len(rows) != expected_count:
        fail(failures, f"{domain} matrix row count mismatch: expected {expected_count}, got {len(rows)}")

    combos = {(row["stage"], row["reviewer_agent"]) for row in rows}
    missing_combos = [
        f"{stage} / {agent}"
        for stage in STAGES
        for agent in AGENTS
        if (stage, agent) not in combos
    ]
    if missing_combos:
        fail(failures, f"{domain} matrix missing stage-agent combos: {', '.join(missing_combos[:20])}")

    path_types = {row["path_type"] for row in rows}
    missing_paths = [path_type for path_type in PATH_TYPES if path_type not in path_types]
    if missing_paths:
        fail(failures, f"{domain} matrix missing path types: {', '.join(missing_paths)}")

    for index, row in enumerate(rows, start=1):
        if row["domain_id"] != domain:
            fail(failures, f"{domain} row {index} has domain_id={row['domain_id']!r}")
        if row["stage"] not in STAGES:
            fail(failures, f"{domain} row {index} has invalid stage={row['stage']!r}")
        if row["reviewer_agent"] not in AGENTS:
            fail(failures, f"{domain} row {index} has invalid reviewer_agent={row['reviewer_agent']!r}")
        if row["path_type"] not in PATH_TYPES:
            fail(failures, f"{domain} row {index} has invalid path_type={row['path_type']!r}")
        if row["verdict"] != "PASS":
            fail(failures, f"{domain} row {index} has non-PASS verdict={row['verdict']!r}")
        blank = [column for column in REQUIRED_COLUMNS if not row.get(column, "").strip()]
        if blank:
            fail(failures, f"{domain} row {index} has blank cells: {', '.join(blank)}")

    require_markers(domain, section, CODING_MARKERS, failures)
    require_markers(domain, section, DOMAINS[domain]["markers"], failures)


def validate_domains(failures: list[str]) -> None:
    for domain, config in DOMAINS.items():
        path = REFERENCES / config["file"]
        if not path.exists():
            fail(failures, f"{domain} domain file missing: {config['file']}")
            continue
        text = read(path)
        require_markers(domain, text, SHARED_SECTIONS, failures)
        validate_matrix(domain, text, failures)


def main() -> int:
    failures: list[str] = []
    validate_framework(failures)
    validate_domains(failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    print(
        "PASS: parsed multi-agent lifecycle matrices for "
        f"{len(DOMAINS)} domains x {len(STAGES)} stages x {len(AGENTS)} agents"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
