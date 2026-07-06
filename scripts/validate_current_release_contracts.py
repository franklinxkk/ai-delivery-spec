#!/usr/bin/env python3
"""Validate current-release domain, continuation, platform, and gate contracts."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import re
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


def current_version(skill_text: str) -> str:
    match = re.search(r"Production Elastic Delivery Standard \(v([0-9]+\.[0-9]+\.[0-9]+)\)", skill_text)
    return match.group(1) if match else "unknown"


def complete_frr(function_id: str, title: str = "Complete Function") -> str:
    sections = "\n\n".join(
        f"#### {idx} Section {idx}\n"
        f"{function_id} section {idx} defines role, state, permission, "
        f"exception, evidence, implementation handoff, and acceptance detail."
        for idx in range(1, 17)
    )
    return f"### {function_id} {title}\n\n{sections}"


def validate_markers(failures: list[str]) -> None:
    skill = read(ROOT / "SKILL.md")
    readme = read(ROOT / "README.md")
    delivery = read(REFERENCES / "delivery-core.md")
    prototype = read(REFERENCES / "prototype-testability.md")
    advanced = read(REFERENCES / "advanced-extensions.md")
    coding = read(REFERENCES / "coding-agent-compat.md")
    traffic = read(REFERENCES / "domain-traffic.md")
    crm = read(REFERENCES / "domain-crm.md")
    ai_native = read(REFERENCES / "domain-ai-native.md")
    human_template = read(REFERENCES / "templates" / "human-first-prd-template.md")
    ai_template = read(REFERENCES / "templates" / "ai-coding-prd-template.md")
    version = current_version(skill)

    require("SKILL.md", skill, [f"v{version}"], failures)
    require(
        "README.md",
        readme,
        [
            f"version-{version}",
            "PM Quickstart",
            "skills.sh",
            "npx skills use franklinxkk/ai-delivery-spec",
            "spec-kit Interop",
            "frontend-design",
            "Brainstorm Product Direction",
            "Prototype Visual Style",
            "Helper CLI",
            "ai_delivery_spec_cli.py",
            "Multi-Agent Lifecycle Validation",
            "validate_multi_agent_lifecycle_scenarios.py",
            "references/domain-ai-native.md",
            "references/domain-oa.md",
            "First-Principles Domain Lens",
        ],
        failures,
    )
    require(
        "delivery-core.md",
        delivery,
        [
            "Long-Form PRD Continuation Contract",
            "Cross-Module Flow Contract",
            "Post-Generation Multi-Module Checklist",
            "Domain Knowledge Quality Gate",
            "CONTINUATION_REQUIRED",
            "self-repair loop",
            "external `brainstorming` skill",
            "planned release functions = complete functional requirement records",
        ],
        failures,
    )
    require(
        "human-first-prd-template.md",
        human_template,
        [
            "Long-form PRD continuation contract",
            "Release Function Inventory",
            "PRD Completion Ledger",
            "CONTINUATION_REQUIRED",
        ],
        failures,
    )
    require(
        "ai-coding-prd-template.md",
        ai_template,
        [
            "Self-driven repair rule",
            "Release Function Inventory",
            "PRD Completion Ledger",
            "CONTINUATION_REQUIRED",
        ],
        failures,
    )
    require(
        "prototype-testability.md",
        prototype,
        [
            "Visual Style Clarification And External UI Skills",
            "Ant Design-style enterprise UI",
            "ArcoDesign / ByteDance-style enterprise UI",
            "frontend-design",
            "remains responsible for IA",
        ],
        failures,
    )
    require(
        "advanced-extensions.md",
        advanced,
        [
            "domain-ai-native.md",
            "Traffic/transport domain note",
            "GB/GB-T",
            "JT/JT-T and JTG",
            "Composition with external skills",
            "spec-kit",
            "frontend-design/UIUX/design-system",
        ],
        failures,
    )
    require(
        "coding-agent-compat.md",
        coding,
        [
            "Recommended sequence",
            "spec-kit skills mode",
            "AI Delivery Spec answers what/why/acceptance",
        ],
        failures,
    )
    require(
        "domain-traffic.md",
        traffic,
        [
            "standards corpus",
            "GB",
            "JT/T",
            "JTG",
            "DBxx/T",
            "T/...",
            "standards applicability conflict",
        ],
        failures,
    )
    require(
        "domain-crm.md",
        crm,
        [
            "Campaign",
            "Quote",
            "RenewalPlan",
            "DemandCreatedFromTicket",
            "Customer 360",
            "quote/CPQ",
            "renewal/customer success",
            "First-Principles CRM Product Logic",
            "Multi-Module PRD Quality Gate",
            "CRM-G1 Cross-module handoff",
        ],
        failures,
    )
    require(
        "domain-ai-native.md",
        ai_native,
        [
            "AI Native Product And Agentic Systems",
            "First-Principles Product Logic",
            "Work outcome first",
            "Context before model",
            "Workflow before chat",
            "Reversibility determines autonomy",
            "Ontology turns data into action",
            "AgentDefinition",
            "ToolDefinition",
            "PromptVersion",
            "ContextAsset",
            "EvalSet",
            "RunTrace",
            "HumanReview",
            "AIWritebackBlocked",
            "EvalRegressionDetected",
            "fallback",
        ],
        failures,
    )


def validate_tail_thin_prd_rejected(failures: list[str]) -> None:
    complete_sections = "\n\n".join(
        f"#### §{idx} Section {idx}\nComplete content for section {idx} with role, state, rule, action, exception, and acceptance detail."
        for idx in range(1, 17)
    )
    bad_prd = f"""# Tail-Thin PRD

## Stage 3 Complete Functional Requirement Records

### M01-F01 Complete Function

{complete_sections}

### M02-F01 Thin Tail Function

#### §1 Business Scenario
same as above
""".strip()
    with tempfile.TemporaryDirectory(prefix="ads-499-") as tmp:
        path = Path(tmp) / "tail-thin-prd.md"
        path.write_text(bad_prd, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "scripts/validate_prd_quality.py", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            fail(failures, "tail-thin PRD unexpectedly passed validate_prd_quality.py")
        if "FRR_COMPLETENESS_GAP" not in output:
            fail(failures, "tail-thin PRD failed without FRR_COMPLETENESS_GAP signal")


def validate_inventory_only_prd_rejected(failures: list[str]) -> None:
    bad_prd = textwrap.dedent(
        """
        # Inventory-Only PRD

        ## Stage 3 Complete Functional Requirement Records

        | Function ID | Function Name | Release Scope |
        |---|---|---|
        | M01-F01 | Create lead | in |
        | M02-F01 | Convert opportunity | in |

        ### M01-F01 Create Lead

        #### §1 Business Scenario
        Create lead.
        #### §2 Roles And Scenario
        Sales creates lead.
        #### §3 Entry And Preconditions
        Entry is lead page.
        #### §4 Pages And Visible States
        Page is visible.
        #### §5 Fields And Validation
        Name is required.
        #### §6 Numbered Interaction Flow
        Submit lead.
        #### §7 Actions And Operation Rules
        Create action.
        #### §8 Business Rules
        Validate duplicate.
        #### §9 State Behavior
        draft -> submitted.
        #### §10 Permissions
        sales self.
        #### §11 Exceptions
        duplicate blocked.
        #### §12 Notifications
        audit written.
        #### §13 Data Contract
        API exists.
        #### §14 NFR
        server write <= 1s with proposed threshold.
        #### §15 Handoff Notes
        FE/BE/QA notes.
        #### §16 Acceptance
        AC passes.
        """
    ).strip()
    with tempfile.TemporaryDirectory(prefix="ads-499-inventory-") as tmp:
        path = Path(tmp) / "inventory-only-prd.md"
        path.write_text(bad_prd, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "scripts/validate_prd_quality.py", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            fail(failures, "inventory-only PRD unexpectedly passed validate_prd_quality.py")
        if "FRR_INVENTORY_COVERAGE_GAP" not in output:
            fail(failures, "inventory-only PRD failed without FRR_INVENTORY_COVERAGE_GAP signal")


def validate_full_prd_missing_rfi_ledger_rejected(failures: list[str]) -> None:
    bad_prd = f"""# Missing RFI Ledger PRD

Profile: Human-First Full PRD

## Stage 3 Complete Functional Requirement Records

{complete_frr("M01-F01", "Create Lead")}

Completion state: PASS
""".strip()
    with tempfile.TemporaryDirectory(prefix="ads-499-rfi-ledger-") as tmp:
        path = Path(tmp) / "missing-rfi-ledger-prd.md"
        path.write_text(bad_prd, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "scripts/validate_prd_quality.py", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            fail(failures, "full PRD without RFI/Ledger unexpectedly passed validate_prd_quality.py")
        if "RFI_LEDGER_GAP" not in output:
            fail(failures, "full PRD without RFI/Ledger failed without RFI_LEDGER_GAP signal")


def validate_placeholder_sections_rejected(failures: list[str]) -> None:
    thin_sections = "\n\n".join(f"#### {idx} Section {idx}\nTODO" for idx in range(1, 17))
    bad_prd = f"""# Placeholder Sections PRD

Profile: AI-Coding Full PRD

## Release Function Inventory

| Function ID | Function Name | Release Scope |
|---|---|---|
| M01-F01 | Create lead | in |

## PRD Completion Ledger

| Function ID | Planned | Completed | Status |
|---|---:|---:|---|
| M01-F01 | 1 | 1 | complete |

## Stage 3 Complete Functional Requirement Records

### M01-F01 Create Lead

{thin_sections}

Completion state: PASS
""".strip()
    with tempfile.TemporaryDirectory(prefix="ads-499-placeholder-") as tmp:
        path = Path(tmp) / "placeholder-prd.md"
        path.write_text(bad_prd, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "scripts/validate_prd_quality.py", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            fail(failures, "placeholder FRR sections unexpectedly passed validate_prd_quality.py")
        if "FRR_SECTION_BODY_GAP" not in output:
            fail(failures, "placeholder FRR sections failed without FRR_SECTION_BODY_GAP signal")


def validate_incomplete_ledger_pass_rejected(failures: list[str]) -> None:
    bad_prd = f"""# Incomplete Ledger PASS PRD

Profile: Human-First Full PRD

## Release Function Inventory

| Function ID | Function Name | Release Scope |
|---|---|---|
| M01-F01 | Create lead | in |
| M02-F01 | Convert opportunity | in |

## PRD Completion Ledger

| Module | Planned FRRs | Completed FRRs | Missing Sections | Blocking Gaps | Next Batch |
|---|---:|---:|---|---|---|
| M01-M02 | 2 | 1 | M02-F01 all sections | context window ended | continue M02-F01 |

## Stage 3 Complete Functional Requirement Records

{complete_frr("M01-F01", "Create Lead")}

{complete_frr("M02-F01", "Convert Opportunity")}

Completion state: PASS
""".strip()
    with tempfile.TemporaryDirectory(prefix="ads-499-ledger-pass-") as tmp:
        path = Path(tmp) / "incomplete-ledger-pass-prd.md"
        path.write_text(bad_prd, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "scripts/validate_prd_quality.py", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            fail(failures, "incomplete ledger with PASS unexpectedly passed validate_prd_quality.py")
        if "PRD_COMPLETION_LEDGER_GAP" not in output:
            fail(failures, "incomplete ledger with PASS failed without PRD_COMPLETION_LEDGER_GAP signal")


def validate_over_specified_simple_scope_rejected(failures: list[str]) -> None:
    bad_prd = textwrap.dedent(
        """
        # Over-Specified Simple Scope

        ## Stage 1 Requirement Planning

        The release is a simple CRUD list/detail feature for manual review, but
        the implementation plan sets Tier: L3 and requires a multi-agent DAG,
        prompt graph, prompt registry, and autonomous tool planning.
        """
    ).strip()
    with tempfile.TemporaryDirectory(prefix="ads-499-antibloat-") as tmp:
        path = Path(tmp) / "over-specified-simple-scope.md"
        path.write_text(bad_prd, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "scripts/validate_prd_quality.py", str(path), "--stage", "draft"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            fail(failures, "over-specified simple scope unexpectedly passed validate_prd_quality.py")
        if "ANTI_BLOATING_GAP" not in output:
            fail(failures, "over-specified simple scope failed without ANTI_BLOATING_GAP signal")


def validate_crm_end_to_end_example(failures: list[str]) -> None:
    base = ROOT / "examples" / "crm-end-to-end-package" / "delivery"
    prd = base / "prd" / "main.md"
    manifest = base / "manifest.json"
    ia = base / "ia-skeleton.yaml"
    prototype = base / "prototype" / "app.html"
    required = [prd, manifest, ia, prototype, base / "acceptance" / "ac-structured.yaml"]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        fail(failures, "CRM end-to-end example missing files: " + ", ".join(missing))
        return

    commands = [
        [
            sys.executable,
            "scripts/validate_prd_quality.py",
            str(prd),
            "--manifest",
            str(manifest),
        ],
        [
            sys.executable,
            "scripts/validate_ia_skeleton.py",
            "--ia-skeleton",
            str(ia),
            "--prototype",
            str(prototype),
            "--prd",
            str(prd),
        ],
        [
            sys.executable,
            "scripts/validate_coding_agent_contract.py",
            "--prd",
            str(prd),
            "--prototype",
            str(prototype),
        ],
    ]
    for cmd in commands:
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            first_line = output.splitlines()[0] if output else "<no output>"
            fail(
                failures,
                "CRM end-to-end example validation failed: "
                + " ".join(cmd)
                + "\n"
                + first_line,
            )


def main() -> int:
    failures: list[str] = []
    validate_markers(failures)
    validate_tail_thin_prd_rejected(failures)
    validate_inventory_only_prd_rejected(failures)
    validate_full_prd_missing_rfi_ledger_rejected(failures)
    validate_placeholder_sections_rejected(failures)
    validate_incomplete_ledger_pass_rejected(failures)
    validate_over_specified_simple_scope_rejected(failures)
    validate_crm_end_to_end_example(failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    print("PASS: current release domain, continuation, platform, and gate contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
