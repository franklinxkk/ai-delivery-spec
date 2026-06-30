---
name: ai-delivery-spec
description: Create PRDs, prototypes, tests, AI runtime specs, and coding agent handoffs for product delivery. Excludes code debugging and copy rewriting.
---

# AI Delivery Spec - Production Elastic Delivery Standard (v4.9.10)

Author: Li Kang. Purpose: produce delivery artifacts that product, engineering,
algorithm, QA, operations, customers, and sponsors can read, build, verify, and
operate without losing lifecycle state, evidence, or handoff accountability.

## 0. Initialization And Triage

Before loading any reference, classify the request and state the result:

```text
[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false] | [INFO: complete|partial|missing]
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
- **INFO: missing/partial** when P0 users, outcome, data source, metric
  caliber, permission boundary, workflow state, or acceptance evidence is
  absent enough to change the PRD.

Fast-pass pruning:

- If `AI: false`, do not load AI Feature, AI Native, prompt, eval, or runtime
  material unless the user explicitly asks for AI governance.
- If `WORKFLOW: false`, do not load approval, low-code, workflow automation, or
  E2E lifecycle extension material.
- If `TIER: Light`, review only the requested artifact and minimum evidence.
  Do not expand into full PRD, DDD, readiness, or acceptance package.

Do not treat pruning as quality relaxation: any in-scope interaction, field,
state, rule, or acceptance claim must still be testable. If `INFO: missing`,
run the clarification protocol before generating; if the user says to proceed
anyway, mark assumptions and finish as `REVIEW_COMPLETE_WITH_GAPS`.

## 1. Runtime File Architecture

Default runtime has four entrypoints. Load only the required default entrypoint
plus any explicitly triggered add-on.

| Entrypoint | Use When | Contains |
|---|---|---|
| `SKILL.md` | always | 0D triage, mode/tier rules, top-level gates, routing |
| `references/delivery-core.md` | PRD, requirement, story, state, Stage 0, DDD/API/data handoff, E2E matrix | main delivery kernel; may load readability layer for L1+ PRD/handoff |
| `references/prototype-testability.md` | HTML prototype, executable demo, mobile/H5/mini-program/app interaction | state-driven prototype and testability kernel |
| `references/advanced-extensions.md` | only when triggered by 0D or explicit scope | AI, SaaS, approval, reporting, low-code, global/readiness/domain extensions |

Triggered add-on:

| Add-on | Use When | Contains |
|---|---|---|
| `references/coding-agent-compat.md` | only when output is consumed by coding agents | AC-YAML, machine-readable AI contract, AGENTS.md / CLAUDE.md / Cursor rules |
| `references/realtime-contract.md` | when the product includes SSE/WebSocket, countdown timers, real-time alerts, polling, or push notifications | real-time event types, SLA countdown, alert rule engine, reconnection and polling strategy |

Templates and domain modules are load-on-demand source assets. Do not load them
directly unless a default entrypoint or triggered add-on explicitly instructs it
for the current task.

## 2. Scope, Mode, And Tier

Keep these decisions separate:

- **Lifecycle stage**: discovery, specification, planning, task breakdown,
  build/verification, launch/readiness, operation/learning, or retirement.
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

### PRD Profile Selector

When the user asks for a PRD, requirement document, product specification, or
development handoff, choose exactly one profile:

| Profile | Trigger | Required Shape |
|---|---|---|
| Contract Summary | quick review, gap check, local change note, or L0/L1 alignment without implementation handoff | concise scope, gaps, decisions, and upgrade triggers |
| Human-First Full PRD | default for human PM/RD/QA/vendor delivery, customer review, bid/demo, or any development handoff unless the user explicitly requests all-AI coding | use `references/templates/human-first-prd-template.md`; readable product specification first: scenarios, page/region layout, field and interaction detail, rules, exceptions, permissions, NFR, acceptance, and handoff notes |
| AI-Coding Full PRD | user explicitly says coding agent, full AI coding, Cursor/Claude Code/Copilot/Codex implementation, or asks for machine-readable contracts/tests | use `references/templates/ai-coding-prd-template.md`; Human-First Full PRD plus `ac_structured`, machine-readable AI/runtime contracts when applicable, delivery package manifest, and coding-agent rules |

- AI-Coding Full PRD is an extension of Human-First Full PRD, not a replacement.
- Formal implementation handoff must never degrade to contract-only summaries.
- If the user's intent is ambiguous but the output may guide developers or QA,
  choose Human-First Full PRD and list what would trigger AI-Coding enrichment.

### Product Work Path Selector

Select Work Path first, then PRD Profile: Work Path controls lifecycle stages; PRD Profile controls document format and consumer. Select before loading detailed references.

| Work Path | Trigger | Required Route |
|---|---|---|
| Traditional Product Lifecycle | user wants a full lifecycle PRD similar to enterprise PM standards, vendor/human development, review/sign-off, launch, or acceptance | Human-First Full PRD + Stage 4-6 lifecycle annex + readiness/acceptance where needed |
| AI Native Product Discovery | user wants AI-native product brainstorming, competitor research, agent workflow, AI runtime, prototype, or AI product planning | delivery-core opportunity shaping + advanced AI/native/runtime/eval sections + prototype when requested |
| AI Coding Delivery | user wants to learn from competitor/prototype and have AI generate the system | AI-Coding Full PRD + locked prototype/source evidence + coding-agent compatibility + delivery package |

If multiple paths apply, keep one source PRD and add path-specific sections.
Do not create separate unsynchronized PRDs.

End every task with one completion state: `PASS`,
`REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`.

Lifecycle rule: external PM/discovery frameworks and spec-driven engineering
tools may provide upstream evidence or naming. Do not import their whole
process. Map them into this lightweight chain only when the request needs it:

```text
Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire
```

`Specify` records what/why/acceptance. `Plan` records engineering approach,
risks, and dependencies. `Tasks` records vertical slices traceable to functions
and acceptance. Skip stages that are not needed for the requested artifact.

Learn/Retire coverage is deliberately minimal: capture metric review,
post-launch learning, sunset evidence, and any external framework gap.

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
- formal PRDs must declare one PRD Profile: Contract Summary, Human-First Full
  PRD, or AI-Coding Full PRD;
- every release function has a complete Functional Requirement Record;
- engineering contract is embedded as an implementation/traceability layer, not
  a replacement for product specification;
- when a locked prototype exists, FRR pages/fields/actions must extract and
  normalize the business-relevant page layout, regions, visible states, fields,
  modal/drawer behavior, and action-to-domain flow. A bare "see prototype" is
  not a complete specification;
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
| PRD/requirement/story/path/state/DDD/API/data contract/full lifecycle walkthrough | `delivery-core.md`; choose Work Path, then PRD Profile; run Stage 3.5 IA Skeleton Gate before Stage 5 **when: >=2 modules OR >=2 primary roles OR any cross-module flow**; for multi-module delivery, run domain/multi-module post-generation gates before `PASS` |
| prototype/demo/HTML/mobile interaction | `prototype-testability.md`; require IA Skeleton as input; add `delivery-core.md` for story/state evidence |
| test/UAT/acceptance/readiness/post-launch/retirement | `delivery-core.md`; add advanced readiness section if real environment |
| AI, SaaS, approval, reporting, low-code, global, domain switch | load `advanced-extensions.md` only after 0D trigger |
| coding agent handoff, generate AGENTS.md/CLAUDE.md/Cursor rules, convert AC to test stubs | `delivery-core.md` + `coding-agent-compat.md`; use AI-Coding Full PRD and locked prototype as source evidence for pages/fields/actions |
| implementation task breakdown / issue slicing | `delivery-core.md`; generate tasks only from approved specification/plan evidence |

## 6. Non-Negotiable Rules

- Product specification and engineering contract must coexist in one source of
  truth. Do not split them into unsynchronized documents.
- Task breakdown is downstream of specification and plan. Do not create coding
  tasks from vague goals, screenshots, or incomplete FRRs.
- Machine-readable contracts are not enough for human teams. PRDs must restore
  business scenario, boundary, exception, metric, and test intent before
  engineering tables.
- When a PRD will be consumed by a coding agent, add machine-readable acceptance
  and runtime blocks as an implementation layer; do not remove human-readable
  FRR narrative.
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
python scripts/validate_coding_agent_contract.py --prd path/to/prd.md --prototype path/to/prototype.html
python scripts/validate_ia_skeleton.py --ia-skeleton path/to/ia-skeleton.yaml --prototype path/to/prototype.html --prd path/to/prd.md
python scripts/validate_skill_consistency.py
python scripts/validate_routing_scenarios.py
```

## 8. Final Response Rule

When delivering work, state: 0D triage result; lifecycle stage, artifact type,
downstream consumer/decision; artifact scope, mode, tier; triggered
gates/extensions; created or updated artifacts; verification performed; and
completion state (`PASS`, `REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`) with
unresolved risks.

## 9. Version Control And Release Rules

When the skill files are managed in a Git repository and published to GitHub or
other remotes, follow these rules to prevent data loss and history corruption.

### Commit Flow

1. **Pull first**: Always `git pull origin main` before making any changes.
   If conflicts arise, resolve them locally before proceeding.
2. **Stage selectively**: `git add` only the files that were actually modified.
   Never use `git add .` or `git add -A` blindly.
3. **Commit with context**: Write a commit message that lists what changed and
   why. Format: `vX.Y.Z: <short description>`.
4. **Push after verification**: Only push after local verification (syntax
   check, test run, or manual review) passes.

### Prohibited Operations

- `git push --force` to `main` branch.
- `git add .` followed by a commit without reviewing the staged diff.
- Overwriting remote files without pulling first (causes non-fast-forward
  rejection or remote history loss if forced).
- Deleting files that exist on remote but not locally without explicit
  de-scope reason in the commit message.

### Release Tagging

When publishing a new version:

1. Update `SKILL.md` version number.
2. Update `CHANGELOG.md` with the new version entry.
3. Commit with message `vX.Y.Z release`.
4. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
5. Push: `git push origin main --tags`.

### Branch Strategy

- `main`: stable, always deployable.
- Feature branches: `feature/<topic>` for experimental work; merge via PR.
- No direct pushes to `main` for experimental or unreviewed changes.

## 10. Delivery Package Convention

When handing off to a coding agent (Claude Code, Cursor, Copilot, Codex) or a
human development team, organize the delivery package using this directory
structure so that automated tools can locate artifacts without ambiguity:

```
delivery/
  prd/                        # PRD Markdown files
  prototype/                   # HTML prototype(s)
  ia-skeleton.yaml             # IA Skeleton (Stage 3.5 output)
  acceptance/                  # AC-YAML files (one per FRR)
  agents/                      # AGENTS.md / CLAUDE.md / .cursor/rules
  evidence/                    # Verification evidence, test results
  manifest.json                # Package manifest (artifact list + hashes)
```

Rules:

- `delivery/manifest.json` lists every artifact with its relative path, version, and
  source status (`EMBEDDED` / `AUTHORITATIVE_ANNEX` / `DEFERRED`).
- Coding agent compatibility files (`AGENTS.md`, `CLAUDE.md`) must reference
  `delivery/prd/` and `delivery/prototype/` as the primary truth for pages,
  fields, and visible behavior.
- When the IA Skeleton is locked (Stage 3.5), `delivery/ia-skeleton.yaml` is
  the structural truth for role x module x view x region.
- Acceptance files in `delivery/acceptance/` use the naming convention
  `M{module}-F{function}-ac.yaml` (e.g., `M04-F01-ac.yaml`).
- Do not place non-delivery files (scripts, configs, scratch files) inside
  `delivery/`. Use a sibling `tools/` or `scratch/` directory instead.
