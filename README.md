# AI Delivery Spec

AI Delivery Spec is a Codex skill for production-grade product delivery artifacts:
PRD, executable prototype, role path, DDD/API/data contract, test/UAT evidence,
release readiness, post-launch review, retirement plan, AI runtime/evaluation
contract, and cross-border delivery spec.

The goal is not to make documents thicker. The goal is to make product
requirements readable, buildable, testable, and operable for product,
frontend, backend, algorithm, QA, operations, customers, and sponsors.

## v4.4.1 Focus

v4.4.1 adds a **Human Readability Layer** for PRD and development handoff
documents. It keeps the v4.4.0 four-entry runtime architecture, but makes
L1+ PRDs more useful for human RD and QA collaboration:

- executive summary within one screen;
- scenario-first module writing before API/DDD/data tables;
- explicit business boundary and exception coverage;
- metrics and event tracking tables with purpose and privacy notes;
- frontend/backend/QA handoff notes inside FRRs;
- concrete examples for thresholds, formulas, time windows, AI confidence
  rules, and non-obvious state guards.

## v4.4.0 Focus

v4.4.0 introduces the **Production Elastic Delivery Standard**:

- **0D triage first**: every run declares `[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false]` before loading references.
- **Four runtime entrypoints**: `SKILL.md`, `delivery-core.md`, `prototype-testability.md`, and `advanced-extensions.md`.
- **Fast-pass pruning**: non-AI work does not load AI runtime/eval/prompt material; non-workflow work does not load approval/low-code/E2E workflow extensions.
- **Requirement Diagnosis Anchors**: development-facing requirements must answer accountability/compliance, adversarial semantics, and offline/concurrency boundaries.
- **State-driven prototype law**: workflow prototypes use `GlobalState` and `transition(currentState, action) -> nextState`; DOM is not a business state source.
- **Presentation Mode**: customer/sponsor demos can hide technical noise, show storyline guidance, and simulate safe error/weak-network/adversarial flows.
- **E2E Cross-Module Canvas**: workflow-heavy PRDs include upstream state, domain event, downstream state, failure/compensation, and E2E acceptance rows.

## Runtime File Structure

```text
ai-delivery-spec/
├── SKILL.md
├── LICENSE
├── scripts/
│   ├── extract_interaction_ledger.py
│   ├── validate_prd_quality.py
│   ├── validate_routing_scenarios.py
│   └── validate_skill_consistency.py
└── references/
    ├── delivery-core.md
    ├── prototype-testability.md
    ├── advanced-extensions.md
    ├── readability-layer.md
    ├── templates/
    ├── prompt-registry.yaml
    ├── domain-module-template.md
    ├── domain-traffic.md
    └── domain-crm.md
```

Other reference files are retained as source assets and historical detail. The
runtime path should start from the four entrypoints above.

## Core Gates

| Gate | Purpose |
|---|---|
| Gate 1 Story-Path | user story -> role path -> visible result -> domain result -> test |
| Gate 2 Demo-Closed Prototype | every primary `data-action` has visible/domain outcome |
| Gate 3 Product Specification + Development Contract | traditional PRD remains primary; engineering contract is embedded and traceable |
| Gate 4 Acceptance Package | package only requested/in-scope artifacts with verification and risks |

## What Makes A PRD Development-Ready

For L2/L3 development handoff, a module is not ready when it only has a summary,
screenshot, DDD table, or input/output list. Each release function needs a
complete Functional Requirement Record:

- role and scenario;
- entry, preconditions, pages, and visible states;
- fields, dictionaries, validation, and editability;
- numbered user-system interaction flow;
- actions, visible result, domain result, idempotency;
- business rules/calibers;
- state-button behavior and guards;
- permission and data scope;
- exceptions, recovery, notifications, and audit;
- data/AI/algorithm contract when applicable;
- dependencies, NFR, and acceptance cases.

Engineering contracts such as DDD, API, command/query, domain event, and
Developer Fast-Lane are embedded inside the same artifact. They guide coding and
testing, but do not replace the product specification.

## Prototype Standard

Workflow prototypes should be executable requirement contracts:

- stable `data-testid` and `data-action`;
- `GlobalState` as single source of truth;
- pure `transition(currentState, action) -> nextState`;
- render from state to DOM;
- shadow/test-mode isolation for automated write-path verification;
- Presentation Mode for customer/sponsor demo when applicable.

## Validation

Run before publishing changes:

```powershell
py -3 scripts/validate_skill_consistency.py
py -3 scripts/validate_routing_scenarios.py
py -3 scripts/validate_prd_quality.py path\to\prd.docx --manifest path\to\manifest.json
```

## License

Apache-2.0.
