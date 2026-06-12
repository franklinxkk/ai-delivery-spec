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


def level_two_headings(path):
    return [
        line[3:].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("## ") and line.strip() != "## Contents"
    ]


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
        for exclusion in ("standalone coding", "generic HTML implementation", "copy editing"):
            if exclusion not in description:
                fail(f"description missing exclusion: {exclusion}", failures)

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

    if "PRD-only request" not in demo_text:
        fail("demo handoff reference does not protect PRD-only scope", failures)
    if "| Artifact | Required When |" not in acceptance_text:
        fail("acceptance package requirements are not scope-conditional", failures)
    if "single-artifact request" not in tier_text:
        fail("tier model does not distinguish single-artifact scope", failures)
    if "High-impact but non-binding advice" not in ai_feature_text:
        fail("AI Feature Injection lacks high-impact human-verified boundary", failures)

    agent_file = ROOT / "agents" / "openai.yaml"
    if not agent_file.exists():
        fail("agents/openai.yaml is missing", failures)
    elif "$ai-delivery-spec" not in agent_file.read_text(encoding="utf-8"):
        fail("agents/openai.yaml default_prompt must mention $ai-delivery-spec", failures)

    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    print("PASS: ai-delivery-spec trigger, scope, references, and domain contracts are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
