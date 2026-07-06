#!/usr/bin/env python3
"""Validate ai-delivery-spec runtime routing and compact reference structure."""

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

OPTIONAL_ENTRYPOINTS = (
    "references/coding-agent-compat.md",
    "references/realtime-contract.md",
)

RETAINED_REFERENCE_FILES = {
    "advanced-extensions.md",
    "coding-agent-compat.md",
    "delivery-core.md",
    "prototype-testability.md",
    "readability-layer.md",
    "realtime-contract.md",
    "domain-ai-native.md",
    "domain-crm.md",
    "domain-data-mart.md",
    "domain-education-it.md",
    "domain-medical-hospital-it.md",
    "domain-module-template.md",
    "domain-oa.md",
    "domain-traffic.md",
    "templates/ai-coding-prd-template.md",
    "templates/field-dictionary-template.md",
    "templates/human-first-prd-template.md",
    "templates/post-launch-review-template.md",
    "templates/prd-light-template.md",
    "templates/system-readiness-checklist-template.md",
}

REMOVED_REFERENCE_NAMES = {
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
    "domain-traffic-safety-scenarios.md",
    "mobile-product-delivery.md",
    "multi-surface-consistency.md",
    "prompt-registry-integration.md",
    "prompt-registry.yaml",
    "reporting-analytics.md",
    "saas-multitenancy.md",
    "skill-design-benchmark.md",
    "skill-version-migration.md",
    "story-path-verification.md",
    "strategy-discovery-handoff.md",
    "system-readiness-checklist.md",
    "workflow-automation-lowcode.md",
    "ai-native-prd-template.md",
    "prd-standard-template.md",
}

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
    "Multi-Agent Lifecycle Verification Matrix",
    "Acceptance Checklist",
]

MOJIBAKE_MARKERS = (
    "\ufffd",
    "\u9205",
    "\u8133",
    "\u9983",
    "\u95c8\u3220",
    "\u6d93\u8f70",
    "\u9358\u62bd",
    "\u702f\u5921",
    "\u93cd\uffe0",
)


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter_description(text: str) -> str | None:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    lines = match.group(1).splitlines()
    collecting = False
    parts: list[str] = []
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


def markdown_headings(path: Path, level: int = 2) -> list[str]:
    prefix = "#" * level + " "
    headings: list[str] = []
    in_fence = False
    for line in read(path).splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith(prefix):
            heading = line[len(prefix):].strip()
            if heading != "Contents":
                headings.append(heading)
    return headings


def contents_entries(text: str) -> list[str]:
    match = re.search(r"\n## Contents\n\n(.*?)(?=\n## )", text, re.DOTALL)
    if not match:
        return []
    return [line[2:].strip() for line in match.group(1).splitlines() if line.startswith("- ")]


def require_markers(name: str, text: str, markers: tuple[str, ...], failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            fail(f"{name} missing marker: {marker}", failures)


def cjk_count(text: str) -> int:
    return sum("\u4e00" <= ch <= "\u9fff" for ch in text)


def require_clean_chinese_support(name: str, text: str, min_cjk: int, failures: list[str]) -> None:
    if cjk_count(text) < min_cjk:
        fail(f"{name} has insufficient Chinese coverage for bilingual/community use", failures)
    for marker in MOJIBAKE_MARKERS:
        if marker in text:
            fail(f"{name} contains likely mojibake marker: {marker!r}", failures)


def validate_contents(path: Path, failures: list[str]) -> None:
    ref_text = read(path)
    if len(ref_text.splitlines()) > 100 and "\n## Contents\n" not in ref_text:
        fail(f"long reference missing Contents: {path.relative_to(ROOT)}", failures)
    elif "\n## Contents\n" in ref_text:
        expected = markdown_headings(path, level=2)
        actual = contents_entries(ref_text)
        if actual != expected:
            fail(f"Contents is stale or incomplete: {path.relative_to(ROOT)}", failures)
    headings = markdown_headings(path, level=2)
    duplicates = sorted({heading for heading in headings if headings.count(heading) > 1})
    if duplicates:
        fail(f"duplicate level-two headings: {path.relative_to(ROOT)} -> {', '.join(duplicates)}", failures)


def main() -> int:
    failures: list[str] = []
    text = read(SKILL)
    description = frontmatter_description(text)

    if description is None:
        fail("SKILL.md frontmatter is missing or invalid", failures)
    else:
        word_count = len(description.split())
        if word_count > 60:
            fail(f"description has {word_count} words; maximum is 60", failures)
        description_lower = description.lower()
        if "code" not in description_lower or "debug" not in description_lower:
            fail("description missing code/debug exclusion", failures)
        if "copy rewriting" not in description_lower:
            fail("description missing copy rewriting exclusion", failures)

    version_match = re.search(
        r"Production Elastic Delivery Standard \(v([0-9]+\.[0-9]+\.[0-9]+)\)",
        text,
    )
    current_version = version_match.group(1) if version_match else None
    if current_version is None:
        fail("SKILL.md version heading is missing", failures)

    if len(text.splitlines()) > 380:
        fail("SKILL.md exceeds runtime-entry budget of 380 lines", failures)

    readme = read(ROOT / "README.md")
    changelog = read(ROOT / "CHANGELOG.md")
    require_clean_chinese_support("README.md", readme, 80, failures)
    require_clean_chinese_support(
        "scripts/validate_routing_scenarios.py",
        read(ROOT / "scripts" / "validate_routing_scenarios.py"),
        80,
        failures,
    )
    if current_version:
        if f"version-{current_version}" not in readme:
            fail(f"README.md badge is not synchronized to v{current_version}", failures)
        if f"## v{current_version} " not in changelog:
            fail(f"CHANGELOG.md missing current version entry v{current_version}", failures)

    require_markers(
        "SKILL.md",
        text,
        (
            "[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false]",
            "Fast-pass pruning",
            "Runtime File Architecture",
            "PRD Profile Selector",
            "Product Work Path Selector",
            "Human-First Full PRD",
            "AI-Coding Full PRD",
            "Default runtime has four entrypoints",
            "coding-agent-compat.md",
            "realtime-contract.md",
            "Final Self-Check",
            "Delivery Package Convention",
            "PASS",
            "REVIEW_COMPLETE_WITH_GAPS",
            "BLOCKED",
        ),
        failures,
    )

    for entrypoint in CORE_ENTRYPOINTS + OPTIONAL_ENTRYPOINTS:
        if entrypoint not in text:
            fail(f"SKILL.md missing entrypoint: {entrypoint}", failures)
        if not (ROOT / entrypoint).exists():
            fail(f"entrypoint file missing: {entrypoint}", failures)

    actual_refs = {
        str(path.relative_to(REFERENCES)).replace("\\", "/")
        for path in REFERENCES.rglob("*")
        if path.is_file()
    }
    missing_retained = sorted(RETAINED_REFERENCE_FILES - actual_refs)
    if missing_retained:
        fail("retained reference missing: " + ", ".join(missing_retained), failures)
    unexpected_refs = sorted(actual_refs - RETAINED_REFERENCE_FILES)
    if unexpected_refs:
        fail("unexpected reference file in compact architecture: " + ", ".join(unexpected_refs), failures)
    for removed in REMOVED_REFERENCE_NAMES:
        if removed in actual_refs or f"templates/{removed}" in actual_refs:
            fail(f"removed legacy reference still exists: {removed}", failures)

    for path in sorted(REFERENCES.rglob("*.md")):
        validate_contents(path, failures)

    delivery_core = read(REFERENCES / "delivery-core.md")
    prototype = read(REFERENCES / "prototype-testability.md")
    advanced = read(REFERENCES / "advanced-extensions.md")
    readability = read(REFERENCES / "readability-layer.md")
    coding_agent = read(REFERENCES / "coding-agent-compat.md")
    human_first_template = read(REFERENCES / "templates" / "human-first-prd-template.md")
    ai_coding_template = read(REFERENCES / "templates" / "ai-coding-prd-template.md")
    realtime = read(REFERENCES / "realtime-contract.md")
    interaction_ledger_script = read(ROOT / "scripts" / "extract_interaction_ledger.py")

    require_markers(
        "delivery-core.md",
        delivery_core,
        (
            "Input Clarification Protocol",
            "Opportunity Shaping Protocol",
            "Discovery Evidence, Value, And Prioritization",
            "EARS requirement writing rule",
            "Vertical Slice Task Backlog",
            "Engineering Plan",
            "Development Follow-Up, Issue Flow, And Bug Triage",
            "Post-Launch Review And Retirement Protocol",
            "E2E Cross-Module Canvas",
            "Cross-Module Flow Contract",
            "Post-Generation Multi-Module Checklist",
            "Domain Knowledge Quality Gate",
            "Human-Readable PRD Layer",
            "Complete Module And Function Product Specification",
            "Multi-Agent Lifecycle Verification",
            "Global State Machine Summary",
            "Domain Event Inventory",
            "Frontend / Backend / QA handoff notes",
            "ac_structured",
            "coding-agent-compat.md",
            "human-first-prd-template.md",
            "ai-coding-prd-template.md",
        ),
        failures,
    )
    if "prd-standard-template.md" in delivery_core:
        fail("delivery-core.md still references deleted prd-standard-template.md", failures)

    require_markers(
        "prototype-testability.md",
        prototype,
        (
            "State-Driven UI Iron Law",
            "UI = f(State)",
            "window.GlobalState",
            "transition(currentState, action)",
            "Presentation Mode Specification",
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
            "anchor cases",
            "SaaS, RBAC, And Multi-Tenancy",
            "Reporting, Dashboard, And Data Product",
            "Workflow Automation And Low-Code",
            "Mobile, Multi-Surface, And Global Delivery",
            "System Readiness, Release, And Retirement",
            "Domain Modules And Templates",
            "Multi-domain composition rule",
            "Repository Cleanliness Rule",
            "coding-agent-compat.md",
            "domain-education-it.md",
            "domain-medical-hospital-it.md",
            "domain-oa.md",
            "domain-ai-native.md",
            "domain-data-mart.md",
        ),
        failures,
    )
    for removed in REMOVED_REFERENCE_NAMES:
        if removed in advanced and removed not in {"prompt-registry.yaml"}:
            fail(f"advanced-extensions.md still references deleted file: {removed}", failures)

    require_markers(
        "readability-layer.md",
        readability,
        (
            "Executive Summary",
            "Scenario-First Module Writing",
            "EARS Requirement Statements",
            "Boundary And Exception Coverage",
            "Metrics And Event Tracking",
            "Frontend Backend QA Handoff Notes",
            "Document Heading Hierarchy",
            "Layout ID",
        ),
        failures,
    )

    require_markers(
        "human-first-prd-template.md",
        human_first_template,
        (
            "Human-First Full PRD",
            "Source Evidence Register",
            "FRR",
            "Notifications, Audit, And Dependencies",
            "Data, AI, And Algorithm Contract",
            "Function-Level NFR",
            "Frontend / Backend / QA Handoff Notes",
            "Acceptance And Traceability",
            "Sprint Task Breakdown",
            "Risk Register",
            "Open Questions",
            "Gate Completion Statement",
        ),
        failures,
    )

    require_markers(
        "ai-coding-prd-template.md",
        ai_coding_template,
        (
            "AI-Coding Full PRD",
            "Human-First Full PRD",
            "Prototype Interaction Ledger Extraction",
            "Structured Acceptance Criteria",
            "frozen_apis",
            "immutability_rules",
            "FRR Completion Gate",
            "Batch generation strategy",
            "API Endpoint Inventory",
            "Delivery Package",
            "source_status",
            "sha256",
            "AGENTS.md",
            "CLAUDE.md",
            ".cursor/rules",
        ),
        failures,
    )

    require_markers(
        "coding-agent-compat.md",
        coding_agent,
        (
            "Structured Acceptance Criteria (AC-YAML)",
            "frozen_apis",
            "immutability_rules",
            "Machine-Readable AI Runtime Contract",
            "Contract Selection Ladder",
            "anchor_case_file",
            "Agent Entrypoint Generation",
            "Delivery Package Layout",
            "Manifest minimum schema",
            "spec-kit Interoperability",
            "AGENTS.md",
            "CLAUDE.md",
            ".cursor/rules",
        ),
        failures,
    )

    require_markers(
        "realtime-contract.md",
        realtime,
        (
            "SSE",
            "WebSocket",
            "polling",
            "reconnect",
        ),
        failures,
    )
    require_markers(
        "extract_interaction_ledger.py",
        interaction_ledger_script,
        (
            "stateSnapshot",
            "stateChecksum",
            "schemaVersion",
        ),
        failures,
    )

    require_markers(
        "README.md",
        readme,
        (
            "Product-side Spec-Driven Delivery",
            "tool-agnostic",
            "skills.sh",
            "npx skills add franklinxkk/ai-delivery-spec",
            "PM Quickstart",
            "Recommended GitHub topics",
            "Role-Based Entry",
            "Multi-Module PRD Pack",
            "spec-kit Interop",
            "frontend-design",
            "Helper CLI",
            "ai_delivery_spec_cli.py",
            "Multi-Agent Lifecycle Validation",
            "validate_multi_agent_lifecycle_scenarios.py",
            "validate_domain_isolation.py",
            "validate_current_release_contracts.py",
            "Who Should Use This",
            "coding-agent compatibility",
            "Delivery Package Convention",
            "Default runtime has four entrypoints",
            "Output Selector",
            "Higher-Education IT",
            "Medical / Hospital IT",
            "OA / Collaborative Office",
            "Data Mart",
        ),
        failures,
    )
    if "Codex skill" in readme:
        fail("README.md still positions the project as a Codex-specific skill", failures)

    domain_template = read(REFERENCES / "domain-module-template.md")
    contributing = read(ROOT / "CONTRIBUTING.md")
    require_markers(
        "CONTRIBUTING.md",
        contributing,
        (
            "15-section domain contract",
            "references/domain-module-template.md",
            "references/advanced-extensions.md",
        ),
        failures,
    )
    for section in DOMAIN_SECTIONS:
        if section not in domain_template:
            fail(f"domain-module-template.md missing section contract item: {section}", failures)
        if section not in contributing:
            fail(f"CONTRIBUTING.md missing domain section checklist item: {section}", failures)
    if "First-Principles Domain Lens" not in domain_template:
        fail("domain-module-template.md missing First-Principles Domain Lens", failures)
    for stale_marker in ("same 14 section", "All 14 domain module sections"):
        if stale_marker in "\n".join(read(path) for path in REFERENCES.glob("domain-*.md")):
            fail(f"domain modules contain stale 14-section contract wording: {stale_marker}", failures)

    domain_files = sorted(
        path.name
        for path in REFERENCES.glob("domain-*.md")
        if path.name != "domain-module-template.md"
    )
    for filename in domain_files:
        if filename not in advanced:
            fail(f"advanced-extensions.md missing domain module: {filename}", failures)
        if f"references/{filename}" not in readme:
            fail(f"README.md missing domain module: references/{filename}", failures)
        headings = markdown_headings(REFERENCES / filename, level=2)
        if "First-Principles Domain Lens" not in headings:
            fail(f"{filename} missing First-Principles Domain Lens", failures)
        positions = []
        for section in DOMAIN_SECTIONS:
            if section not in headings:
                fail(f"{filename} missing domain section: {section}", failures)
            else:
                positions.append(headings.index(section))
        if positions and positions != sorted(positions):
            fail(f"{filename} domain sections are out of contract order", failures)

    for agent_path, markers in {
        ROOT / "agents" / "openai.yaml": ("$ai-delivery-spec",),
        ROOT / "agents" / "claude-code.md": ("Claude Code Agent Entry", "ac_structured", "AGENTS.md"),
        ROOT / "agents" / "openai-codex.md": ("OpenAI Codex Agent Entry", "Source-Of-Truth Order", "AGENTS.md"),
    }.items():
        if not agent_path.exists():
            fail(f"{agent_path.relative_to(ROOT)} is missing", failures)
        else:
            agent_text = read(agent_path)
            require_markers(str(agent_path.relative_to(ROOT)), agent_text, markers, failures)
            if current_version and agent_path.suffix in {".yaml", ".yml"}:
                version_match = re.search(r'^\s*version:\s*["\']?([^"\'\n]+)', agent_text, re.MULTILINE)
                if version_match and version_match.group(1).strip() != current_version:
                    fail(
                        f"{agent_path.relative_to(ROOT)} version {version_match.group(1).strip()} "
                        f"is not synchronized to v{current_version}",
                        failures,
                    )

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    print("PASS: ai-delivery-spec compact runtime, templates, domains, and validators are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
