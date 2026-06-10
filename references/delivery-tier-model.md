# Delivery Tier Model

Use this file when deciding how much process a project needs. The goal is to prevent L0/L1 prototypes from being judged by L3 AI-native standards while still making upgrade paths explicit.

## Tier Selection

| Tier | Best For | Decision Question |
|---|---|---|
| L0 Exploration Prototype | idea demo, workshop mockup, early HTML | "Can stakeholders understand the idea by clicking it?" |
| L1 Prototype + Light PRD | internal alignment, simple feature spec | "Can PM/design/dev discuss the same behavior?" |
| L2 Standard Product Delivery | real development, bid package, customer demo | "Can dev and QA implement/test without guessing?" |
| L3 AI Native / High-Risk Delivery | agentic workflow, automation, AI writes/actions | "Can the AI workflow be safely simulated, observed, evaluated, and rolled back?" |

## Required Artifacts

| Artifact | L0 | L1 | L2 | L3 |
|---|:---:|:---:|:---:|:---:|
| Prototype | required | required | required | required |
| Demo path notes | required | required | required | required |
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
