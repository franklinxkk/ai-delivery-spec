#!/usr/bin/env python3
"""Validate trigger precision and cross-file contracts for ai-delivery-spec."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
REFERENCES = ROOT / "references"

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
            "code-only syntax/debugging",
            "copy rewriting",
            "idea exploration with no delivery intent",
        ):
            if exclusion not in description:
                fail(f"description missing exclusion: {exclusion}", failures)
        if "generic HTML implementation" in description:
            fail("description retains the ambiguous generic HTML exclusion", failures)

    if len(text.splitlines()) > 500:
        fail("SKILL.md exceeds 500 lines", failures)

    required_markers = [
        "Artifact scope",
        "Mode and tier are orthogonal",
        "PASS",
        "REVIEW_COMPLETE_WITH_GAPS",
        "BLOCKED",
        "AI-core",
        "AI-supporting",
        "AI-incidental",
        "Primary Output Route",
        "Product Plugins",
        "Higher assurance wins",
        "Global/Regional Readiness Profile",
    ]
    for marker in required_markers:
        if marker not in text:
            fail(f"SKILL.md missing marker: {marker}", failures)

    for path in sorted(REFERENCES.rglob("*.md")):
        ref_text = path.read_text(encoding="utf-8")
        if len(ref_text.splitlines()) > 100 and "\n## Contents\n" not in ref_text:
            fail(f"long reference missing Contents: {path.relative_to(ROOT)}", failures)
        elif "\n## Contents\n" in ref_text:
            expected = level_two_headings(path)
            actual = contents_entries(ref_text)
            if actual != expected:
                fail(f"Contents is stale or incomplete: {path.relative_to(ROOT)}", failures)
        if path.name not in text:
            fail(f"reference not discoverable from SKILL.md: {path.relative_to(ROOT)}", failures)
        headings = level_two_headings(path)
        duplicates = sorted({heading for heading in headings if headings.count(heading) > 1})
        if duplicates:
            fail(
                f"duplicate level-two headings: {path.relative_to(ROOT)} -> {', '.join(duplicates)}",
                failures,
            )

    for filename in ("domain-traffic.md", "domain-crm.md"):
        headings = level_two_headings(REFERENCES / filename)
        positions = []
        for section in DOMAIN_SECTIONS:
            if section not in headings:
                fail(f"{filename} missing domain section: {section}", failures)
            else:
                positions.append(headings.index(section))
        if positions and positions != sorted(positions):
            fail(f"{filename} domain sections are out of contract order", failures)

    demo_text = (REFERENCES / "demo-closed-ddd-handoff.md").read_text(encoding="utf-8")
    acceptance_text = (REFERENCES / "delivery-acceptance-gates.md").read_text(encoding="utf-8")
    tier_text = (REFERENCES / "delivery-tier-model.md").read_text(encoding="utf-8")
    ai_feature_text = (REFERENCES / "ai-feature-injection.md").read_text(encoding="utf-8")
    delivery_core_text = (REFERENCES / "delivery-core.md").read_text(encoding="utf-8")
    runtime_text = (REFERENCES / "ai-runtime-ops.md").read_text(encoding="utf-8")
    readiness_text = (REFERENCES / "system-readiness-checklist.md").read_text(encoding="utf-8")
    saas_text = (REFERENCES / "saas-multitenancy.md").read_text(encoding="utf-8")
    mobile_text = (REFERENCES / "mobile-product-delivery.md").read_text(encoding="utf-8")
    effect_text = (REFERENCES / "ai-effect-evaluation.md").read_text(encoding="utf-8")

    if "PRD-only request" not in demo_text:
        fail("demo handoff reference does not protect PRD-only scope", failures)
    if "| Artifact | Required When |" not in acceptance_text:
        fail("acceptance package requirements are not scope-conditional", failures)
    if "single-artifact request" not in tier_text:
        fail("tier model does not distinguish single-artifact scope", failures)
    if "High-impact but non-binding advice" not in ai_feature_text:
        fail("AI Feature Injection lacks high-impact human-verified boundary", failures)
    for marker in (
        "Persona Walkthrough Script",
        "Invalid Generic Response",
        "Complexity Budget Counting",
        "Do not claim a PRD page count",
    ):
        if marker not in delivery_core_text and marker not in text:
            fail(f"delivery execution guidance missing marker: {marker}", failures)
    for marker in (
        "Dual State Coordination",
        "Regional Model Routing",
        "business_state",
        "business_version",
        "ai_state",
        "precondition_violated",
    ):
        if marker not in runtime_text:
            fail(f"AI/business state coordination missing marker: {marker}", failures)

    global_contracts = {
        "system readiness": (readiness_text, ("Global / Regional Readiness Profile", "data_boundary", "Cross-border basis")),
        "SaaS": (saas_text, ("Regional Tenant Matrix", "home_region", "allowed_support_access_regions")),
        "mobile": (mobile_text, ("Localization / RTL / Distribution", "privacy_or_data_safety", "RTL")),
        "effect evaluation": (effect_text, ("Locale / Regional Evaluation", "worst-locale", "native/domain reviewers")),
    }
    for contract, (contract_text, markers) in global_contracts.items():
        for marker in markers:
            if marker not in contract_text:
                fail(f"global readiness {contract} contract missing marker: {marker}", failures)

    for stale_heading in ("## 5. Conditional Gates", "## 6. Module Map", "## 7. Decision Tree"):
        if stale_heading in text:
            fail(f"stale duplicate routing section remains: {stale_heading}", failures)

    lifecycle_markers = (
        "Lifecycle Artifact Review",
        "operation/learning",
        "Post-Launch Evidence Review",
        "Retirement / Exit Readiness Profile",
        "N/A (lifecycle governance)",
    )
    lifecycle_text = text + acceptance_text + readiness_text + tier_text
    for marker in lifecycle_markers:
        if marker not in lifecycle_text:
            fail(f"lifecycle artifact coverage missing marker: {marker}", failures)

    agent_file = ROOT / "agents" / "openai.yaml"
    if not agent_file.exists():
        fail("agents/openai.yaml is missing", failures)
    elif "$ai-delivery-spec" not in agent_file.read_text(encoding="utf-8"):
        fail("agents/openai.yaml default_prompt must mention $ai-delivery-spec", failures)

    routing_validator = ROOT / "scripts" / "validate_routing_scenarios.py"
    if not routing_validator.exists():
        fail("routing scenario validator is missing", failures)
    else:
        routing_text = routing_validator.read_text(encoding="utf-8")
        for marker in (
            "real patterns",
            "cross-industry",
            "global/AI-native",
            "lifecycle stages",
            "trigger boundaries",
        ):
            if marker not in routing_text:
                fail(f"routing scenario validator missing coverage marker: {marker}", failures)

    benchmark_text = (REFERENCES / "skill-design-benchmark.md").read_text(encoding="utf-8")
    for marker in ("Evolution Governance", "three real projects", "two domains"):
        if marker not in benchmark_text:
            fail(f"skill evolution governance missing marker: {marker}", failures)

    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASS: ai-delivery-spec trigger, scope, references, and domain contracts are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
