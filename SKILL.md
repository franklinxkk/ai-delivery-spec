---
name: ai-delivery-spec
description: >-
  Use to create or review product delivery artifacts with handoff intent: PRD,
  prototype, role path, DDD/API/data contract, test/UAT evidence, readiness,
  post-launch review, retirement, AI runtime/evaluation, or cross-border spec.
  First run 0D triage to prune AI/workflow gates. Do not use for code-only
  syntax/debugging, copy rewriting, or idea exploration with no delivery intent.
---

# AI Delivery Spec — Production Elastic Delivery Standard (v4.4.1)

Author: Li Kang. Purpose: produce delivery artifacts that product, engineering,
algorithm, QA, operations, customers, and sponsors can read, build, verify, and
operate without losing lifecycle state, evidence, or handoff accountability.

## 0. Initialization And Triage

Before loading any reference, classify the request and state the result:

```text
[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false]
```

Classification rules:

- **TIER: Heavy** when the artifact will guide development, QA, customer demo,
  bid/procurement, production launch, migration, formal acceptance, or a
  multi-role lifecycle. Otherwise use **Light**.
- **AI: true** only when the product/module itself contains AI-core or
  AI-supporting behavior. AI used merely to write PRD/prototype/code is
  `AI: false`.
- **WORKFLOW: true** when the scope contains approval, escalation, cross-module
  state, low-code workflow, task routing, audit lifecycle, or long-running
  business process.

Fast-pass pruning:

- If `AI: false`, do not load AI Feature, AI Native, prompt, eval, or runtime
  material unless the user explicitly asks for AI governance.
- If `WORKFLOW: false`, do not load approval, low-code, workflow automation, or
  E2E lifecycle extension material.
- If `TIER: Light`, review only the requested artifact and minimum evidence.
  Do not expand into full PRD, DDD, readiness, or acceptance package.

Do not treat pruning as quality relaxation: any in-scope interaction, field,
state, rule, or acceptance claim must still be testable.

## 1. Runtime File Architecture

Load only these runtime entrypoints:

| Entrypoint | Use When | Contains |
|---|---|---|
| `SKILL.md` | always | 0D triage, mode/tier rules, top-level gates, routing |
| `references/delivery-core.md` | PRD, requirement, story, state, Stage 0, DDD/API/data handoff, E2E matrix | main delivery kernel; may load readability layer for L1+ PRD/handoff |
| `references/prototype-testability.md` | HTML prototype, executable demo, mobile/H5/mini-program/app interaction | state-driven prototype and testability kernel |
| `references/advanced-extensions.md` | only when triggered by 0D or explicit scope | AI, SaaS, approval, reporting, low-code, global/readiness/domain extensions |

Legacy reference files, templates, prompt registry, and domain modules are
source assets. Do not load them directly unless one of the four entrypoints
explicitly instructs it for the current task.

## 2. Scope, Mode, And Tier

Keep these decisions separate:

- **Artifact scope**: one artifact, one module package, or full delivery package.
- **Execution mode**: Lite, Standard, or Full.
- **Delivery tier**: L0-L3 rigor of the in-scope artifact/module.

| Mode | Use When | Stop Boundary |
|---|---|---|
| Lite | quick validation, one named artifact, draft, direction check | requested artifact verified + gaps/upgrade triggers listed |
| Standard | development/QA handoff, customer demo, bid, multi-role lifecycle | requested artifact/package verified + unresolved decisions listed |
| Full | formal acceptance, production launch, migration, on-call/rollback, complete package | full manifest + readiness result |

Higher assurance wins when signals conflict: `Full > Standard > Lite`. Mode
does not expand artifact scope by itself.

Tier guide:

| Tier | Use When | Skip By Default |
|---|---|---|
| L0 | exploration prototype/note, no development handoff | full PRD, DDD, AI harness |
| L1 | light product contract, simple feature alignment | full DDD unless lifecycle-heavy |
| L2 | ToB/ToG standard delivery, development handoff, bid/demo package | AI Native unless triggered |
| L3 | AI-core, high-risk automation, compliance/money/safety impact, multi-agent | none for affected module unless de-scoped |

End every task with one completion state: `PASS`,
`REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`.

## 3. AI Centrality

Classify per module:

- **AI-core**: primary outcome fails without AI, or AI routes/tools/writes
  consequential state. Use L3 gates for that module.
- **AI-supporting**: deterministic/manual path remains valid and AI extracts,
  classifies, summarizes, drafts, or recommends for human confirmation. Use AI
  Feature Injection from `advanced-extensions.md`.
- **AI-incidental**: AI only creates the PRD, prototype, code, or tests. Do not
  trigger product AI gates.

## 4. Core Gates

### Gate 1: Story-Path

Every scoped function maps to user story, role path, visible result, domain
result, state/event/audit result where applicable, and test case.

### Gate 2: Demo-Closed Prototype

Applies only when prototype/demo/interaction is in scope. Every primary action
must have a visible result and domain result. Toast-only core commands fail.
Workflow prototypes must use `GlobalState` and
`transition(currentState, action) -> nextState` rather than DOM-derived
business state. Use `references/prototype-testability.md`.

### Gate 3: Product Specification + Development Contract

Applies to PRD, product-linked architecture/API/data contract, or development
handoff. Required:

- traditional product specification remains the primary truth;
- L1+ PRD/handoff documents must apply human readability rules: executive
  summary, scenario-first module writing, explicit boundary/exception coverage,
  metrics/event tracking where operationally useful, and frontend/backend/QA
  handoff notes;
- every release function has a complete Functional Requirement Record;
- engineering contract is embedded as an implementation/traceability layer, not
  a replacement for product specification;
- source evidence register has zero silent omission;
- DDD/API/data handoff includes commands, queries, events, invariants, state,
  policy, permission, and tests where applicable;
- when workflow is in scope, include the E2E Cross-Module Canvas.

Use `references/delivery-core.md`.

### Gate 4: Acceptance Package

Package only artifacts required by selected scope, tier, and triggered gates:
artifact links, verification evidence, unresolved risks, de-scope notes, test
handoff checklist, and package manifest when applicable.

## 5. Routing

Choose one primary route, then add triggered extensions.

| Request | Primary Entrypoint |
|---|---|
| strategy/discovery/business case/roadmap | `delivery-core.md`; add advanced strategy/readiness section if needed |
| PRD/requirement/story/path/state/DDD/API/data contract | `delivery-core.md` |
| prototype/demo/HTML/mobile interaction | `prototype-testability.md`; add `delivery-core.md` for story/state evidence |
| test/UAT/acceptance/readiness/post-launch/retirement | `delivery-core.md`; add advanced readiness section if real environment |
| AI, SaaS, approval, reporting, low-code, global, domain switch | load `advanced-extensions.md` only after 0D trigger |

## 6. Non-Negotiable Rules

- Product specification and engineering contract must coexist in one source of
  truth. Do not split them into unsynchronized documents.
- Machine-readable contracts are not enough for human teams. PRDs must restore
  business scenario, boundary, exception, metric, and test intent before
  engineering tables.
- Reader-first navigation may reduce duplication, never reduce function
  coverage, source evidence mapping, acceptance coverage, or traceability.
- Every supplied source file, sheet, page, rule, screenshot, SQL/dictionary,
  metric, and prototype path is registered as `EMBEDDED`,
  `AUTHORITATIVE_ANNEX`, `DEFERRED`, `CONFLICT`, or `NOT_APPLICABLE`.
- Assertion status is separate: `VERIFIED`, `INFERRED`, `PROPOSED`, `UNKNOWN`,
  or `CONFLICT`.
- Prototype evidence status is separate again: `VERIFIED`, `SPEC_ONLY`, `GAP`,
  `CONFLICT`, or `UNKNOWN`.
- Function splitting follows semantics: split when role, permission, trigger,
  aggregate/data owner, state transition, business result, audit/NFR, or
  acceptance path differs.
- Automated browser verification must use shadow/test-mode isolation for any
  write path. It cannot pollute real business data or KPI/statistics.
- Human overrule may release with recorded risk only after safety, compliance,
  data isolation, and rollback checks remain satisfied.

## 7. Required Scripts

Use scripts when applicable instead of retyping repeatable logic:

```powershell
python scripts/extract_interaction_ledger.py --input path/to/prototype.html --output interaction-ledger.json
python scripts/validate_prd_quality.py path/to/prd.docx --manifest path/to/manifest.json
python scripts/validate_skill_consistency.py
python scripts/validate_routing_scenarios.py
```

## 8. Final Response Rule

When delivering work, state:

- 0D triage result;
- lifecycle stage, artifact type, downstream consumer/decision;
- artifact scope, mode, tier;
- triggered gates/extensions;
- created or updated artifacts;
- verification performed;
- completion state and unresolved risks.
