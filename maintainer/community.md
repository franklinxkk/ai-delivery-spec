# Community And Release Communication

This file contains reusable community copy, terminology and release checks. It
does not prove submission, acceptance, maturity or production behavior. Verify
each community's current rules and run the maintainer status/release checks
before publishing.

## Core Glossary

| Term | Meaning |
|---|---|
| Intake | Evidence-backed value, complexity, priority, owner, dependency and accept/clarify/defer/reject decision. |
| Requirement stage | `intake -> clarify -> specify -> review -> baseline -> change -> acceptance -> closed`; not a sprint state. |
| Unified PRD | One human reading baseline with engineering, machine acceptance and traceability annexes. |
| Product Truth | Optional structured authority for large, repeatedly changed, multi-export or audited requirements. |
| Stable ID | Permanent `REQ/FLOW/VIEW/ACT/FLD/RULE/API/AC` identity changed through `CHG-*`. |
| Review / Change / Acceptance | `REV-*` findings, `CHG-*` controlled diffs and `ARUN-*` executed evidence. |
| Domain Pack | Optional accelerator with explicit applicability, practice status, maturity and gaps. |
| Completion | Scoped `PASS`, `REVIEW_COMPLETE_WITH_GAPS` or `BLOCKED`. |

## Positioning

AI Delivery Spec is an open-source requirement-management kernel: lightweight
for ToC idea-to-PRD work and deep for governed ToB/ToG requirements. It manages
intake, clarification, one unified PRD, change, traceability and acceptance.

AI Delivery Spec 是需求管理内核：ToC 想法到 PRD 可以轻量使用，ToB/ToG 复杂
需求可以深度展开；默认只有一份人类可读、AI Coding 可执行的统一 PRD。

```md
- [AI Delivery Spec](https://github.com/franklinxkk/ai-delivery-spec) -
  Requirement-management kernel for intake, clarification, one unified PRD,
  prototype requirements, change, traceability, and acceptance.
```

## Evidence-Safe Proof Points

- requirement intake and adaptive mode/tier recommendation;
- guided clarification with P0-unknown blocking;
- one Human-First PRD with engineering/Coding Agent annexes;
- optional progressive Product Truth for scale/audit triggers;
- change impact, bidirectional traceability and evidence-bound acceptance;
- maturity-declared domain packs and deterministic project gates.

Never convert `contract_tested`, `partial` or `not_run` into behavioral,
expert, customer or production claims. Do not claim legal, clinical, financial,
safety or regulatory correctness without matching accountable evidence.

## Publication Checklist

- README first screen states problem, audience, install path and evidence boundary.
- Commands exist and status agrees with public maturity claims.
- No customer-specific project name or compatibility patch is shipped.
- Fixture presence is not described as behavioral validation.
- License, security policy, contribution guide and release tag are present.
- SkillHub package stays within the repository file-budget gate.

Suggested topics:

```text
product-management, requirements-engineering, spec-driven-development,
enterprise-software, tob, tog, prd, traceability, ai-coding, coding-agent,
acceptance-criteria, prototype, brownfield, agent-skills
```
