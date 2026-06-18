#!/usr/bin/env python3
"""Validate ai-delivery-spec v4.5.x runtime routing and core contracts."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
REFERENCES = ROOT / "references"

CORE_ENTRYPOINTS = (
    "references/delivery-core.md",
    "references/prototype-testability.md",
    "references/advanced-extensions.md",
)

LEGACY_ASSETS = (
    "ai-effect-evaluation.md",
    "ai-feature-injection.md",
    "ai-native-harness-engineering.md",
    "ai-runtime-ops.md",
    "approval-workflow.md",
    "artifact-packaging.md",
    "build-governance.md",
    "delivery-acceptance-gates.md",
    "delivery-tier-model.md",
    "demo-closed-ddd-handoff.md",
    "mobile-product-delivery.md",
    "multi-surface-consistency.md",
    "prompt-registry-integration.md",
    "reporting-analytics.md",
    "saas-multitenancy.md",
    "story-path-verification.md",
    "strategy-discovery-handoff.md",
    "system-readiness-checklist.md",
    "workflow-automation-lowcode.md",
)

MAINTENANCE_ASSETS = (
    "skill-design-benchmark.md",
    "skill-version-migration.md",
)

DOMAIN_SECTIONS = [
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
    "Acceptance Checklist",
]


def fail(message, failures):
    failures.append(message)


def frontmatter_description(text):
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    lines = match.group(1).splitlines()
    collecting = False
    parts = []
    for line in lines:
        if line.startswith("description:"):
            collecting = True
            value = line.split(":", 1)[1].strip()
            if value not in {">-", ">", "|-", "|"}:
                parts.append(value)
            continue
        if collecting:
            if line and not line.startswith((" ", "\t")):
                break
            parts.append(line.strip())
    return " ".join(part for part in parts if part)


def markdown_headings(path, level=2):
    prefix = "#" * level + " "
    headings = []
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith(prefix):
            heading = line[len(prefix):].strip()
            if heading != "Contents":
                headings.append(heading)
    return headings


def level_two_headings(path):
    return markdown_headings(path, level=2)


def contents_entries(text):
    match = re.search(r"\n## Contents\n\n(.*?)(?=\n## )", text, re.DOTALL)
    if not match:
        return []
    return [
        line[2:].strip()
        for line in match.group(1).splitlines()
        if line.startswith("- ")
    ]


def require_markers(name, text, markers, failures):
    for marker in markers:
        if marker not in text:
            fail(f"{name} missing marker: {marker}", failures)


def main():
    failures = []
    text = SKILL.read_text(encoding="utf-8")
    description = frontmatter_description(text)

    if description is None:
        fail("SKILL.md frontmatter is missing or invalid", failures)
    else:
        word_count = len(description.split())
        if word_count > 60:
            fail(f"description has {word_count} words; maximum is 60", failures)
        for exclusion in (
            "code-only",
            "syntax/debugging",
            "copy rewriting",
            "idea exploration with no delivery intent",
        ):
            if exclusion not in description:
                fail(f"description missing exclusion: {exclusion}", failures)
        if "generic HTML implementation" in description:
            fail("description retains ambiguous generic HTML exclusion", failures)

    if len(text.splitlines()) > 260:
        fail("SKILL.md exceeds v4.5 runtime-entry budget of 260 lines", failures)

    require_markers(
        "SKILL.md",
        text,
        (
            "v4.5.2",
            "[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false]",
            "Fast-pass pruning",
            "Runtime File Architecture",
            "advanced-extensions.md",
            "Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire",
            "E2E Cross-Module Canvas",
            "GlobalState",
            "transition(currentState, action) -> nextState",
            "Product specification and engineering contract",
            "human readability rules",
            "PASS",
            "REVIEW_COMPLETE_WITH_GAPS",
            "BLOCKED",
        ),
        failures,
    )

    for entrypoint in CORE_ENTRYPOINTS:
        if entrypoint not in text:
            fail(f"SKILL.md missing runtime entrypoint: {entrypoint}", failures)
        if not (ROOT / entrypoint).exists():
            fail(f"runtime entrypoint file missing: {entrypoint}", failures)

    # The default route must not list every legacy reference as a direct primary load path.
    direct_legacy_mentions = [name for name in LEGACY_ASSETS if name in text]
    if direct_legacy_mentions:
        fail(
            "SKILL.md directly mentions legacy assets outside four-entry routing: "
            + ", ".join(direct_legacy_mentions),
            failures,
        )

    for path in sorted(REFERENCES.rglob("*.md")):
        ref_text = path.read_text(encoding="utf-8")
        if len(ref_text.splitlines()) > 100 and "\n## Contents\n" not in ref_text:
            fail(f"long reference missing Contents: {path.relative_to(ROOT)}", failures)
        elif "\n## Contents\n" in ref_text:
            expected = level_two_headings(path)
            actual = contents_entries(ref_text)
            if actual != expected:
                fail(f"Contents is stale or incomplete: {path.relative_to(ROOT)}", failures)
        headings = level_two_headings(path)
        duplicates = sorted({heading for heading in headings if headings.count(heading) > 1})
        if duplicates:
            fail(
                f"duplicate level-two headings: {path.relative_to(ROOT)} -> {', '.join(duplicates)}",
                failures,
            )

    delivery_core = (REFERENCES / "delivery-core.md").read_text(encoding="utf-8")
    prototype = (REFERENCES / "prototype-testability.md").read_text(encoding="utf-8")
    advanced = (REFERENCES / "advanced-extensions.md").read_text(encoding="utf-8")
    readability = (REFERENCES / "readability-layer.md").read_text(encoding="utf-8")
    migration = (REFERENCES / "skill-version-migration.md").read_text(encoding="utf-8")
    benchmark = (REFERENCES / "skill-design-benchmark.md").read_text(encoding="utf-8")
    prd_template = (REFERENCES / "templates" / "prd-standard-template.md").read_text(encoding="utf-8")
    source_asset_index = "\n".join(
        (
            advanced,
            prd_template,
            (REFERENCES / "system-readiness-checklist.md").read_text(encoding="utf-8"),
            (REFERENCES / "workflow-automation-lowcode.md").read_text(encoding="utf-8"),
        )
    )

    for asset in LEGACY_ASSETS:
        if not (REFERENCES / asset).exists():
            fail(f"retained source asset is missing: {asset}", failures)
        if asset not in source_asset_index:
            fail(f"retained source asset is not reachable from runtime source index: {asset}", failures)

    for asset in MAINTENANCE_ASSETS:
        if not (REFERENCES / asset).exists():
            fail(f"maintenance asset is missing: {asset}", failures)
        if asset not in advanced and asset != "skill-version-migration.md":
            fail(f"maintenance asset is not declared in advanced extensions: {asset}", failures)

    require_markers(
        "delivery-core.md",
        delivery_core,
        (
            "Business Readiness And Requirement Diagnosis Anchors",
            "Lifecycle And Spec-Plan-Tasks Bridge",
            "Vertical Slice Task Backlog",
            "Accountability / compliance",
            "Adversarial semantics",
            "Offline / concurrency",
            "E2E Cross-Module Canvas",
            "AC-E2E-LONG-RUNNING",
            "Human-Readable PRD Layer",
            "readability-layer.md",
            "executive summary",
            "Complete Module And Function Product Specification",
            "Backend Closure Rules",
            "Function-Level NFR",
            "Frontend / Backend / QA handoff notes",
        ),
        failures,
    )
    if "| Dependencies and NFR |" in delivery_core:
        fail("delivery-core.md still has the obsolete FRR row: Dependencies and NFR", failures)

    require_markers(
        "prototype-testability.md",
        prototype,
        (
            "State-Driven UI Iron Law",
            "UI = f(State)",
            "window.GlobalState",
            "transition(currentState, action)",
            "Presentation Mode Specification",
            "Adversarial rehearsal",
            "shadow data",
        ),
        failures,
    )

    require_markers(
        "advanced-extensions.md",
        advanced,
        (
            "Extension Loading Rule",
            "AI Feature / AI Native / Prompt Ops",
            "SaaS, RBAC, And Multi-Tenancy",
            "Reporting, Dashboard, And Data Product",
            "Workflow Automation And Low-Code",
            "Domain Modules, Templates, And Legacy Assets",
            "load-on-demand assets",
            "domain-education-it.md",
            "External lifecycle and PM frameworks are upstream evidence",
        ),
        failures,
    )

    require_markers(
        "readability-layer.md",
        readability,
        (
            "Executive Summary",
            "Role-Oriented PRD Completeness",
            "Scenario-First Module Writing",
            "Boundary And Exception Coverage",
            "Metrics And Event Tracking",
            "Frontend Backend QA Handoff Notes",
            "Business Examples",
            "Readability Acceptance Checklist",
        ),
        failures,
    )

    require_markers(
        "prd-standard-template.md",
        prd_template,
        (
            "1.5 Executive Summary",
            "Mxx Business Scenario Canvas",
            "Frontend / Backend / QA Handoff Notes",
            "13.5 Implementation Plan And Task Backlog",
            "Vertical Slice Backlog",
            "Event ID",
            "Privacy / Masking",
        ),
        failures,
    )

    require_markers(
        "skill-version-migration.md",
        migration,
        (
            "v4.3.0 -> v4.4.0 Production Elastic Delivery Standard",
            "v4.4.0 -> v4.4.1 Human Readability Layer",
            "v4.4.1 -> v4.5.0 Lifecycle Benchmark Bridge",
            "v4.5.0 -> v4.5.1 PRD Runtime Consistency",
            "v4.5.1 -> v4.5.2 Higher-Education Domain Module",
            "Four runtime entrypoints",
            "0D triage",
            "State-driven prototype law",
            "E2E Cross-Module Canvas",
            "Spec/Plan/Tasks bridge added",
            "FRR summary aligned to 16 sections",
        ),
        failures,
    )

    require_markers(
        "skill-design-benchmark.md",
        benchmark,
        (
            "deanpeters/Product-Manager-Skills",
            "mattpocock/to-prd",
            "github/spec-kit",
            "Woshipm 6063060 / 5264380",
            "Atlassian PRD guidance",
            "Microsoft Well-Architected business-requirement guidance",
            "Do not turn every review comment into a new public protocol",
        ),
        failures,
    )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require_markers(
        "README.md",
        readme,
        (
            "AI Delivery Spec / AI 产研交付规格",
            "tool-agnostic",
            "ChatGPT, Claude, Gemini",
            "v4.5.2 Focus",
            "Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire",
            "Default runtime has only four entrypoints",
            "Higher-Education Informationization",
        ),
        failures,
    )
    if "Codex skill" in readme:
        fail("README.md still positions the project as a Codex-specific skill", failures)

    for filename in ("domain-traffic.md", "domain-crm.md", "domain-education-it.md"):
        headings = level_two_headings(REFERENCES / filename)
        positions = []
        for section in DOMAIN_SECTIONS:
            if section not in headings:
                fail(f"{filename} missing domain section: {section}", failures)
            else:
                positions.append(headings.index(section))
        if positions and positions != sorted(positions):
            fail(f"{filename} domain sections are out of contract order", failures)

    agent_file = ROOT / "agents" / "openai.yaml"
    if not agent_file.exists():
        fail("agents/openai.yaml is missing", failures)
    elif "$ai-delivery-spec" not in agent_file.read_text(encoding="utf-8"):
        fail("agents/openai.yaml default_prompt must mention $ai-delivery-spec", failures)

    for script in ("validate_routing_scenarios.py", "validate_prd_quality.py"):
        if not (ROOT / "scripts" / script).exists():
            fail(f"{script} is missing", failures)

    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASS: ai-delivery-spec v4.5.x runtime routing, readability, and core contracts are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
