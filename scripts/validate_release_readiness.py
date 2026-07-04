#!/usr/bin/env python3
"""Release-readiness checks for ai-delivery-spec.

This is a deterministic smoke harness for the skill itself. It does not replace
human product review. It verifies that the current runtime can support:

- traditional / human-first PRD lifecycle work;
- AI-native discovery and governance routing;
- AI-coding handoff with machine-readable contracts;
- PRD review and competitor/prototype reverse-engineering routes;
- reader roles needed by PM, UX, frontend, backend, algorithm, QA, and coding agents.
- AI+Data product lifecycle, ontology/semantic modeling, ChatBI, and Data Agent paths.
- AI-native product / agentic system domain contracts and long-form PRD continuation.
- Multi-agent lifecycle verification across built-in domains before final release.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(failures: list[str], message: str) -> None:
    failures.append(message)


def require(name: str, text: str, markers: list[str], failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            fail(failures, f"{name} missing marker: {marker}")


def run(cmd: list[str], failures: list[str], cwd: Path = ROOT) -> str:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        fail(failures, f"command failed: {' '.join(cmd)}\n{output}")
    return output


def normalize_cn(text: str) -> str:
    return re.sub(r"\s+", "", text)


def validate_static_contracts(failures: list[str]) -> None:
    skill = read(ROOT / "SKILL.md")
    delivery = read(REFERENCES / "delivery-core.md")
    readability = read(REFERENCES / "readability-layer.md")
    coding = read(REFERENCES / "coding-agent-compat.md")
    prototype = read(REFERENCES / "prototype-testability.md")
    human_template = read(REFERENCES / "templates" / "human-first-prd-template.md")
    ai_template = read(REFERENCES / "templates" / "ai-coding-prd-template.md")
    data_domain = read(REFERENCES / "domain-data-mart.md")
    ai_domain = read(REFERENCES / "domain-ai-native.md")

    require(
        "SKILL.md work/profile routing",
        skill,
        [
            "Product Work Path Selector",
            "Select Work Path first, then PRD Profile",
            "Traditional Product Lifecycle",
            "AI Native Product Discovery",
            "AI Coding Delivery",
            "Human-First Full PRD",
            "AI-Coding Full PRD",
            "Gate 1: Story-Path",
            "Gate 2: Demo-Closed Prototype",
            "Gate 3: Product Specification + Development Contract",
            "Gate 4: Acceptance Package",
        ],
        failures,
    )
    require(
        "delivery-core lifecycle",
        delivery,
        [
            "Unstructured Input Protocol",
            "0.5 Input Clarification Protocol",
            "Opportunity Shaping Protocol",
            "Discovery Evidence, Value, And Prioritization",
            "EARS requirement writing rule",
            "Engineering Plan",
            "Development Follow-Up, Issue Flow, And Bug Triage",
            "Post-Launch Review And Retirement Protocol",
            "Stage 3.5 IA Skeleton Gate",
            "Global Entity Field Dictionary",
            "Complete Module And Function Product Specification",
            "Long-Form PRD Continuation Contract",
            "Multi-Agent Lifecycle Verification",
            "FRR section order remains authoritative",
            "Frontend / Backend / QA handoff notes",
            "E2E Cross-Module Canvas",
            "SIM Review",
        ],
        failures,
    )
    for section in range(1, 17):
        if f"{section}." not in delivery and f"§{section}" not in delivery:
            fail(failures, f"delivery-core FRR summary may miss section {section}")

    require(
        "readability-layer human team support",
        readability,
        [
            "Role-Oriented PRD Completeness",
            "Sponsor / PM",
            "UX / UI",
            "Frontend",
            "Backend",
            "Algorithm / AI",
            "QA",
            "Scenario-First Module Writing",
            "EARS Requirement Statements",
            "Boundary And Exception Coverage",
            "Metrics And Event Tracking",
            "Frontend Backend QA Handoff Notes",
            "Page Layout And Component Constraint",
            "Output Language Rules",
            "Document Heading Hierarchy",
            "Module Self-Contained Organization",
        ],
        failures,
    )
    require(
        "prototype-testability",
        prototype,
        [
            "State-Driven UI Iron Law",
            "UI = f(State)",
            "data-testid",
            "data-action",
            "Presentation Mode Specification",
            "shadow data",
        ],
        failures,
    )
    require(
        "human-first template",
        human_template,
        [
            "Human-First Full PRD",
            "Stage 1 Requirement Planning",
            "Stage 2 IA And Prototype Lock",
            "Stage 3 Complete Functional Requirement Records",
            "Stage 4 Review And Delivery Plan",
            "Stage 5 Test And Acceptance",
            "Stage 6 Launch And Review",
            "Source Evidence Register",
            "Page Layout And Region Map",
            "Repeat one complete FRR for every in-scope function",
            "Long-form PRD continuation contract",
            "Frontend / Backend / QA Handoff Notes",
            "Acceptance And Traceability",
            "Sprint Task Breakdown",
            "Bug Management And Acceptance Defects",
            "Post-launch Review",
        ],
        failures,
    )
    require(
        "AI-coding template",
        ai_template,
        [
            "AI-Coding Full PRD",
            "AI-Coding Full PRD is an extension of Human-First Full PRD",
            "Part 1 Human-First Foundation Layer",
            "Part 2 Machine-Readable Extension Layer",
            "Part 3 Coding Agent Delivery Package",
            "Part 4 Validation And Review",
            "FRR Completion Gate",
            "Self-driven repair rule",
            "ac_structured",
            "API Endpoint Inventory",
            "manifest.json",
            "AGENTS.md",
            "CLAUDE.md",
            ".cursor/rules",
            "Review checklist",
        ],
        failures,
    )
    require(
        "AI Native domain",
        ai_domain,
        [
            "AI Native Product And Agentic Systems",
            "AgentDefinition",
            "ToolDefinition",
            "PromptVersion",
            "ContextAsset",
            "EvalSet",
            "RunTrace",
            "HumanReview",
            "AIWritebackBlocked",
            "EvalRegressionDetected",
            "Human Gate",
            "fallback",
            "Acceptance Checklist",
        ],
        failures,
    )
    require(
        "AI+Data domain",
        data_domain,
        [
            "multi-source data",
            "Source and ingestion",
            "Processing and quality",
            "Governance and catalog",
            "Storage and retrieval",
            "Semantic and ontology",
            "Data Agent",
            "ChatBI",
            "Ontology And Semantic Contract",
            "data_agent_contract",
            "insight-to-action loop",
            "Acceptance Checklist",
        ],
        failures,
    )
    require(
        "coding-agent compatibility",
        coding,
        [
            "Structured Acceptance Criteria (AC-YAML)",
            "AC ID Evolution Rules",
            "Machine-Readable AI Runtime Contract",
            "Contract Selection Ladder",
            "ai_contract_lite",
            "ai_runtime_contract",
            "JSON Schema skeleton",
            "Prototype Data-Attribute Contract",
            "Delivery Package Layout",
            "Agent Entrypoint Generation",
            "Coding Agent Handoff Prompt",
        ],
        failures,
    )


def validate_scenario_matrix(failures: list[str]) -> None:
    corpus = "\n".join(
        read(path)
        for path in [
            ROOT / "SKILL.md",
            REFERENCES / "delivery-core.md",
            REFERENCES / "advanced-extensions.md",
            REFERENCES / "prototype-testability.md",
            REFERENCES / "coding-agent-compat.md",
            REFERENCES / "readability-layer.md",
            REFERENCES / "domain-ai-native.md",
            REFERENCES / "domain-data-mart.md",
            REFERENCES / "templates" / "human-first-prd-template.md",
            REFERENCES / "templates" / "ai-coding-prd-template.md",
        ]
    )
    scenarios = {
        "UC1 simple CRM idea -> guided brainstorm -> PRD/prototype": [
            "Unstructured Input Protocol",
            "0.5 Input Clarification Protocol",
            "Opportunity Shaping Protocol",
            "READY_FOR_LIGHT_PRD",
            "Human-First Full PRD",
            "prototype-testability.md",
        ],
        "UC2 clear requirement -> AI coding delivery": [
            "AI Coding Delivery",
            "AI-Coding Full PRD",
            "ac_structured",
            "Delivery Package Layout",
            "AGENTS.md",
            "CLAUDE.md",
            ".cursor/rules",
        ],
        "UC3 uploaded PRD -> review and improvement": [
            "Gate 1: Story-Path",
            "Gate 3: Product Specification + Development Contract",
            "SIM Review",
            "REVIEW_COMPLETE_WITH_GAPS",
        ],
        "UC4 competitor screenshot/prototype -> reverse-engineer -> own plan": [
            "Stage 0 Reverse Engineering",
            "Annotation Pattern Detection",
            "Source Evidence Inventory And Coverage",
            "Opportunity Shaping Protocol",
            "Stage 3.5 IA Skeleton Gate",
        ],
        "UC5 AI-native agent product -> runtime/eval/fallback": [
            "AI Native Product Discovery",
            "AI Feature / AI Native / Prompt Ops",
            "ai_runtime_contract",
            "human_gate",
            "fallback",
        ],
        "UC6 traditional lifecycle -> Tencent-style readable delivery": [
            "Traditional Product Lifecycle",
            "Stage 1 Requirement Planning",
            "Stage 4 Review And Delivery Plan",
            "Stage 5 Test And Acceptance",
            "Stage 6 Launch And Review",
        ],
        "UC7 mobile/multi-surface prototype": [
            "mobile",
            "multi-surface",
            "data-testid",
            "data-action",
            "State-Driven UI Iron Law",
        ],
        "UC8 launch/post-launch/retire": [
            "Launch",
            "Learn/Retire",
            "Post-Launch Review And Retirement Protocol",
            "System Readiness",
        ],
        "UC9 AI+Data lifecycle -> source to agent": [
            "multi-source data",
            "Source and ingestion",
            "Processing and quality",
            "Governance and catalog",
            "Storage and retrieval",
            "Semantic and ontology",
            "Data Agent",
            "ChatBI",
            "data_agent_contract",
        ],
        "UC10 ontology and data system product": [
            "Ontology And Semantic Contract",
            "Object type",
            "Link type",
            "Action type",
            "AgentWritebackBlocked",
            "insight-to-action loop",
        ],
        "UC11 AI-native agent domain": [
            "AI Native Product And Agentic Systems",
            "AgentDefinition",
            "ToolDefinition",
            "EvalSet",
            "RunTrace",
            "HumanReview",
            "AIWritebackBlocked",
        ],
        "UC12 long-form PRD continuation": [
            "Long-Form PRD Continuation Contract",
            "PRD Completion Ledger",
            "CONTINUATION_REQUIRED",
            "Self-driven repair rule",
        ],
        "UC13 multi-agent lifecycle validation": [
            "Multi-Agent Lifecycle Verification",
            "PM Agent",
            "Domain Expert Agent",
            "Architecture / Data / AI Agent",
            "QA Agent",
            "Coding Agent",
        ],
    }
    for name, markers in scenarios.items():
        for marker in markers:
            if marker not in corpus:
                fail(failures, f"scenario {name} is not supported by marker: {marker}")


def validate_generated_minimal_samples(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="ads-release-") as tmp:
        base = Path(tmp)
        prototype = base / "prototype.html"
        prd = base / "ai-coding-prd.md"
        human = base / "human-first-prd.md"

        prototype.write_text(
            textwrap.dedent(
                """
                <!doctype html>
                <html><body>
                <main data-testid="page-lead-create" data-visible-role="sales">
                  <section data-testid="region-lead-form">
                    <button
                      data-testid="btn-submit-lead"
                      data-action="lead.submit"
                      data-state="draft"
                      data-api="/api/leads"
                      data-method="POST"
                      data-visible-role="sales">Submit</button>
                  </section>
                  <div data-testid="modal-lead-create"></div>
                </main>
                </body></html>
                """
            ).strip(),
            encoding="utf-8",
        )

        shared_prd = """
        # CRM Lead Creation PRD

        ## Stage 1 Requirement Planning

        Sales users need a traceable way to submit a new lead.

        ## Stage 2 Product Specification

        Role: sales. State: draft. API: POST /api/leads.

        ## Stage 3 Detailed Functional Requirements

        ### M01 Lead Management

        #### M01-F01 Submit Lead

        ##### §1 Function Inventory And Scenario
        Sales submits a lead from page-lead-create.

        ##### §2 User Story And Role Path
        sales opens page-lead-create and clicks btn-submit-lead.

        ##### §3 Business Entry And Preconditions
        User is authenticated as sales.

        ##### §4 Pages, Regions, And Visible States
        page-lead-create / region-lead-form / modal-lead-create / draft.

        ##### §5 Fields And Dictionaries
        Lead name is required.

        ##### §6 Numbered Interaction Flow
        1. sales clicks data-action lead.submit on data-testid btn-submit-lead.

        ##### §7 Actions And Commands
        lead.submit creates a submitted lead.

        ##### §8 Business Rules And Calibers
        The system shall reject empty lead name.

        ##### §9 State, Button, And Lifecycle Behavior
        draft -> pending_review after lead.submit.

        ##### §10 Permissions And Data Scope
        sales can create own leads only.

        ##### §11 Exceptions And Boundary Cases
        If duplicate submit occurs, the system shall keep one lead and show the existing ID.

        ##### §12 Notifications, Audit, And Dependencies
        Audit event LeadSubmitted is written.

        ##### §13 Data, AI, And Algorithm Contract
        No AI. POST /api/leads is idempotent by request_id.

        ##### §14 Function-Level NFR
        Server write latency, validation failure, duplicate submit handling, and audit logging are observable with proposed threshold <= 1s.

        ##### §15 Frontend / Backend / QA Handoff Notes
        Frontend uses btn-submit-lead disabled/loading states. Backend validates owner. QA tests duplicate submit.

        ##### §16 Acceptance And Traceability
        Given sales is on page-lead-create, when lead.submit is clicked, then draft changes to pending_review.
        """
        human.write_text(
            textwrap.dedent(
                shared_prd
                + """

                ## Stage 4 Review And Delivery Plan
                TRK-001 tracks M01-F01.

                ## Stage 5 Test And Acceptance
                AC-M01-F01-001 covers submit.

                ## Stage 6 Launch And Review
                Review submit success and duplicate rate.
                """
            ).strip(),
            encoding="utf-8",
        )
        prd.write_text(
            textwrap.dedent(
                shared_prd
                + """

                ```yaml
                ac_structured:
                  - id: AC-M01-F01-001
                    frr_ref: M01-F01
                    type: happy_path
                    priority: P0
                    status: active
                    revision: 1
                    given: "sales is authenticated and the lead form is in draft state"
                    when: "sales clicks submit lead"
                    then:
                      ui: "btn-submit-lead shows loading and then success"
                      domain: "lead state changes from draft to pending_review"
                      sla: "server write <= 1s"
                    test_type: integration
                    data_testid: "btn-submit-lead"
                    data_action: "lead.submit"
                    skip_reason: null
                  - id: AC-M01-F01-002
                    frr_ref: M01-F01
                    type: regression
                    priority: P1
                    status: active
                    revision: 1
                    given: "sales can access the lead create page"
                    when: "the page renders"
                    then:
                      ui: "page-lead-create and region-lead-form are visible"
                      domain: "no write occurs"
                    test_type: e2e
                    data_testid: "page-lead-create"
                    data_action: "lead.submit"
                    skip_reason: null
                  - id: AC-M01-F01-003
                    frr_ref: M01-F01
                    type: regression
                    priority: P1
                    status: active
                    revision: 1
                    given: "sales opens the lead create modal"
                    when: "the modal renders"
                    then:
                      ui: "modal-lead-create is visible"
                      domain: "no write occurs"
                    test_type: e2e
                    data_testid: "modal-lead-create"
                    data_action: "lead.submit"
                    skip_reason: null
                  - id: AC-M01-F01-004
                    frr_ref: M01-F01
                    type: regression
                    priority: P1
                    status: active
                    revision: 1
                    given: "sales can access the lead form region"
                    when: "the region renders"
                    then:
                      ui: "region-lead-form is visible"
                      domain: "no write occurs"
                    test_type: e2e
                    data_testid: "region-lead-form"
                    data_action: "lead.submit"
                    skip_reason: null
                ```

                ## Part 2 Machine-Readable Contracts

                | Method | Path | Source FRR | Auth | Idempotency | Notes |
                |---|---|---|---|---|---|
                | POST | /api/leads | M01-F01 | sales | request_id | submit lead |

                ## Part 3 Coding Agent Delivery Package

                AGENTS.md, CLAUDE.md, and .cursor/rules read this PRD first.

                ## Part 4 Validation And Review

                PM, Frontend, Backend, QA, and Coding Agent review M01-F01.
                """
            ).strip(),
            encoding="utf-8",
        )

        run([sys.executable, "scripts/validate_prd_quality.py", str(human)], failures)
        run([sys.executable, "scripts/validate_prd_quality.py", str(prd)], failures)
        run(
            [
                sys.executable,
                "scripts/validate_coding_agent_contract.py",
                "--prd",
                str(prd),
                "--prototype",
                str(prototype),
            ],
            failures,
        )


def validate_local_crm_samples(crm_dir: Path | None, failures: list[str], warnings: list[str]) -> None:
    if not crm_dir or not crm_dir.exists():
        # The built-in minimal Human-First and AI-Coding samples above are the
        # default release smoke pressure. Local CRM artifacts are optional
        # extended checks and should not create a warning for fresh clones.
        return

    human = next(crm_dir.glob("*HumanFirst*.md"), None)
    ai = next(crm_dir.glob("*AICoding*.md"), None)
    prototype = next(crm_dir.glob("*完整原型*.html"), None)
    pdf = next(crm_dir.glob("*腾讯*.pdf"), None)

    if human:
        out = run(
            [
                sys.executable,
                "scripts/validate_prd_quality.py",
                str(human),
                "--allow-wildcards",
                "--language-threshold",
                "zh",
            ],
            failures,
        )
        if "PASS" not in out:
            warnings.append(f"HumanFirst pressure sample did not report PASS: {human.name}")
    else:
        warnings.append("HumanFirst CRM pressure sample not found")

    if ai:
        out = run(
            [
                sys.executable,
                "scripts/validate_prd_quality.py",
                str(ai),
                "--allow-wildcards",
                "--language-threshold",
                "zh",
            ],
            failures,
        )
        if "PASS" not in out:
            warnings.append(f"AI-Coding pressure sample did not report PASS: {ai.name}")
    else:
        warnings.append("AI-Coding CRM pressure sample not found")

    if ai and prototype:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/validate_coding_agent_contract.py",
                "--prd",
                str(ai),
                "--prototype",
                str(prototype),
                "--allow-unmapped-testid",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            warnings.append(
                "CRM AI-Coding/prototype strict contract pressure sample still has artifact gaps; "
                "this is a real project follow-up, not a runtime release blocker. First line: "
                + (result.stdout + result.stderr).strip().splitlines()[0]
            )

    if pdf:
        try:
            import pypdf  # type: ignore

            reader = pypdf.PdfReader(str(pdf))
            text = "\n".join(page.extract_text() or "" for page in reader.pages[:6])
            compact = normalize_cn(text)
            for marker in [
                "阶段一",
                "需求规划",
                "阶段二",
                "PRD",
                "阶段三",
                "设计研发评审",
                "阶段四",
                "研发跟进",
                "阶段五",
                "测试验收",
                "阶段六",
                "上线复盘",
            ]:
                if marker not in compact:
                    fail(failures, f"Tencent-style lifecycle PDF benchmark missing marker in extracted text: {marker}")
        except Exception as exc:  # pragma: no cover - optional local dependency
            warnings.append(f"Could not inspect local Tencent-style PDF benchmark: {exc}")
    else:
        warnings.append("Tencent-style CRM PDF benchmark not found")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--crm-dir", type=Path, help="Optional local CRM sample directory for pressure checks")
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []

    validate_static_contracts(failures)
    validate_scenario_matrix(failures)
    validate_generated_minimal_samples(failures)
    validate_local_crm_samples(args.crm_dir, failures, warnings)

    for warning in warnings:
        print(f"WARN: {warning}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: release readiness simulation checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
