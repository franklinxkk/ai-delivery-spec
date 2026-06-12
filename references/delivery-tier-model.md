# Delivery Tier Model

Use this file when deciding how much process a project needs. The goal is to prevent L0/L1 prototypes from being judged by L3 AI-native standards while still making upgrade paths explicit.

The Strategic Discovery Handoff Gate is independent of L0-L3. For a new product/market, major investment, repositioning, or commercialization decision, complete the strategic handoff first, then select the delivery tier. It is not a reason to classify ordinary non-AI work as L3.

## Scope And Execution Mode Before Tier

First choose artifact scope: one requested artifact, a bounded module package, or a full delivery package. Missing package artifacts are reported, not auto-generated, unless the user requests the package.

| Mode | Choose When | Stop After |
|---|---|---|
| Lite | quick validation, one requested artifact, bounded review | requested artifact + applicable gate evidence + known gaps |
| Standard | normal delivery or requested module package | requested artifacts + applicable gates/plugins |
| Full | complete tier package, formal acceptance, launch readiness | full package manifest + readiness result |

Choose the least costly mode that can satisfy the stated outcome. A mode controls execution breadth; a tier controls artifact rigor. A Lite review can inspect one L2/L3 artifact without downgrading it. A non-AI L2 launch can use Full mode without becoming L3.

## Tier Selection

| Tier | Best For | Decision Question |
|---|---|---|
| L0 Exploration Artifact | idea demo, workshop mockup, early HTML/flow/note | "Can stakeholders understand the idea or scoped interaction?" |
| L1 Light Product Contract | internal alignment, simple feature spec | "Can PM/design/dev discuss the same behavior?" |
| L2 Standard Product Delivery | real development, bid package, customer demo | "Can dev and QA implement/test without guessing?" |
| L3 AI Native / High-Risk Delivery | agentic workflow, automation, AI writes/actions | "Can the AI workflow be safely simulated, observed, evaluated, and rolled back?" |

## Required Artifacts

The table below defines a **full package**. For a single-artifact request, only the requested row and its applicable gates are mandatory; other rows are package gaps, not automatic work.

| Artifact | L0 | L1 | L2 | L3 |
|---|:---:|:---:|:---:|:---:|
| Requested primary artifact | required | required | required | required |
| Prototype/demo surface | when interactive idea is in scope | when interaction alignment is in scope | required for demo package; otherwise conditional | required for user-facing AI/demo package; executable trace may substitute for backend AI |
| Demo/path notes | required when interaction/path is claimed | required | required for full package | required for full package |
| Known gaps/de-scope | required | required | required | required |
| Light PRD | optional | required | replaced by PRD | replaced by PRD |
| User story inventory | optional | required lite | required | required |
| Role path matrix | optional | required lite | required | required |
| State-button matrix | only lifecycle objects | lifecycle objects | required | required |
| DDD handoff | no | conditional | required | required |
| Developer Fast-Lane | no | optional | required | required |
| Acceptance report | lite | lite | required | required |
| AI runtime/harness/effect | no | conditional | conditional | required |

## Gate Downgrade Rules

L0 may skip Gate 3 if:
- no one will develop from it directly;
- core buttons show visible outcomes or are clearly marked future scope;
- known gaps are listed.

L1 may skip full DDD if:
- the feature has no complex lifecycle;
- no cross-role approval or data isolation risk exists;
- dev handoff is not yet requested.

L2 must not skip Developer Fast-Lane if development starts.

L3 must not skip AI runtime, harness, observability, rollback, or effect-intent checks.

## Stop Conditions

Finish as PASS, REVIEW_COMPLETE_WITH_GAPS, or BLOCKED. Stop when the requested artifact/review is complete, every applicable gate has an honest result, in-scope paths have verification evidence, validation is complete, and unresolved items have impact plus a next decision. Do not generate optional artifacts after this point.

## AI Centrality

- AI-core: the scoped module's primary outcome or critical path depends on AI. Apply L3 AI gates to that module.
- AI-supporting: AI assists a valid deterministic/manual workflow. Use AI Feature Injection.
- AI-incidental: AI only helps create the delivery artifact. Do not trigger product AI gates.

Classify mixed products per module. Do not automatically escalate an entire product because one bounded feature uses AI. High-impact but non-binding AI advice may remain AI-supporting only when a qualified human independently verifies it and no consequential write/action occurs automatically; add evaluation and evidence gates.

## Upgrade Path

| From | To | Required Work |
|---|---|---|
| L0 -> L1 | Add story inventory, role paths, state notes, testids |
| L1 -> L2 | Add full PRD, state-button matrix, Developer Fast-Lane, acceptance report |
| L2 -> L3 | Add AI scenario card, harness, runtime, prompt registry, observability, effect evaluation |

## Tier Mismatch Failures

- Applying L3 gates to L0 exploratory work and calling it failed.
- Using an L0 prototype as a dev contract without upgrade.
- Calling an AI feature "AI Native" when it is only classification/summarization inside an existing workflow.
- Treating a customer/bid package as L1 when it needs acceptance evidence.
