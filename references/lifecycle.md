# Requirement Lifecycle And Role Ownership

Use this reference to manage a requirement from intake to acceptance without
turning AI Delivery Spec into a project-management or software-lifecycle tool.

## 1. Boundary

In scope:

1. intake and prioritization;
2. clarification and review closure;
3. one governed specification baseline;
4. change request, impact, diff, approval and synchronization;
5. bidirectional traceability and audit history;
6. executable acceptance and result closure.

Out of scope: sprint planning, effort assignment, task tracking, source-code
management, CI/CD, deployment execution, monitoring, incident management and
product operations. Record an external reference or milestone only when it is
needed to prove a requirement or acceptance outcome.

## 2. Requirement Record

Create one `REQ-*` record before detailed design. Minimum fields:

| Field | Meaning |
|---|---|
| id / title / type | stable identity and requirement class |
| source_refs | request, contract, minutes, policy or evidence |
| outcome | observable customer/business result |
| value | high/medium/low with evidence and affected users |
| complexity | S/M/L/XL with impacted roles, modules, data, integration and compliance |
| uncertainty | low/medium/high with named unknowns |
| priority | P0-P3 with rationale; not a safety severity |
| stage | intake through closed requirement-management state |
| iteration / dependencies | target baseline and blocking/related requirements |
| behavior_refs / acceptance_refs | forward trace links after specification |
| audit_history | actor, time, action, reason and before/after version |

Never invent exact engineering time or money. Use a complexity band until an
accountable engineering owner supplies an estimate.

## 3. Intake Decision

Evaluate five dimensions:

- strategic/customer value and evidence;
- affected users and urgency;
- scope clarity and decision authority;
- complexity/impact dimensions;
- dependency, compliance and delivery risk.

Return one decision:

- `accept`: value and owner are clear; proceed at the recommended mode/tier;
- `clarify`: potentially valid but a material unknown changes scope or outcome;
- `defer`: valid but lower value, blocked dependency or later iteration;
- `reject`: no supported outcome, duplicate, out of product boundary or
  disproportionate risk without mitigation.

Multi-requirement intake also records iteration, dependencies and ordering. It
is a light requirement pool, not a backlog/sprint manager.

## 4. Guided Clarification

Close questions in batches that do not depend on one another:

1. outcome, users, trigger and success;
2. scope, source precedence and forbidden behavior;
3. roles, permissions and data scope;
4. happy path, state transitions and cross-role handoffs;
5. rules, fields, exceptions, failure/recovery and integrations;
6. acceptance thresholds, evidence, sign-off and out-of-scope items.

Use `REV-*` for review findings. Each item has severity, requirement reference,
question/finding, owner, disposition, resolution and evidence. A review meeting
is not closed while its P0/P1 items are merely copied into meeting notes.

Ambiguity indicators include vague quantities/times, undefined defaults,
unnamed actors, hidden approval, undefined failure handling, unrestricted data
scope, and words such as “支持”, “灵活”, “适量”, “及时”, “等”, or “可配置”
without a decision rule.

## 5. Specification And Baseline

Default to one unified PRD. Its main body is the shared reading path; its
engineering appendices are part of the same baseline. Do not maintain a
traditional PRD and an AI Coding PRD as independent sources of truth.

A baseline requires:

- all in-scope `REQ-*` and their source precedence;
- complete roles and end-to-end journeys;
- functional behavior, pages, fields, states, rules, permissions and errors;
- business-level API/event/integration contracts where applicable;
- acceptance criteria and traceability index;
- unresolved items explicitly deferred or blocking;
- version, approvers and baseline time.

Use Product Truth only when one embedded index is insufficient for scale,
multiple projections, repeated changes or audit. Product Truth is a structured
authority layer, not a mandatory pre-document ceremony.

## 6. Change Control

Every material baseline change creates `CHG-*` and follows:

```text
request → validate source/authority → identify seed IDs → bidirectional impact
→ before/after diff → compatibility/data/history review → approval
→ update affected artifacts → synchronize consumers → regression → new baseline
```

Impact must cover requirement, role, flow, page/region/action, field/entity,
rule/state, API/event/integration, acceptance/test/defect/evidence, history,
permission, data scope and migration when applicable.

## 7. Bidirectional Traceability

Store edges as `from_id`, `to_id`, `relation`, and `source`. Build both indexes:

- forward: requirement to behavior and proof;
- reverse: behavior, test, defect or evidence back to requirement/change.

Minimum release trace for an approved requirement:

```text
SRC → REQ → FLOW/VIEW/ACT/FLD/RULE/STATE/API → AC → TEST/ARUN → EVD
                        ↑                         ↓
                        └──────── CHG / DEFECT ──┘
```

Unlinked items are either fixed or explicitly classified as draft, reusable
reference, out of scope or legacy evidence. Do not silently ignore orphans.

## 8. Acceptance Closure

Convert each `AC-*` into one or more executable items. An acceptance run records:

- baseline version and environment;
- executor, time and customer/owner when applicable;
- status of each item: pass/fail/blocked/not_run;
- actual result and evidence locations;
- linked defects and residual risks;
- sign-off decision: accepted/accepted_with_conditions/rejected;
- conditions, owner and due criterion.

Acceptance closes a requirement only when all mandatory items have evidence and
the sign-off decision permits closure. Text saying “verified” is not evidence.

## 9. State Model

Allowed requirement stages:

```text
submitted → triaging → clarifying → specified → reviewing → baselined
baselined → acceptance → accepted → closed
any non-closed stage → deferred|rejected|cancelled|superseded
baselined → change_requested → baselined (new version)
```

Implementation states such as development/test/deployed are optional external
milestones with a source URL/ID. They do not drive the requirement state machine.

## 10. Completion Gate

Before returning `PASS`, verify intake evidence, closed P0 questions, readable
specification, stable baseline, trace closure, change consistency and executed
acceptance evidence. Otherwise return `REVIEW_COMPLETE_WITH_GAPS` or
`BLOCKED_BY_P0_UNKNOWN`
with named IDs and owners.

## 11. Reusable Patterns

Use `references/patterns/common-requirement-patterns.yaml` for approval, list,
form, permission, import/export and integration scenarios. A pattern contributes
questions, behavior/exception contracts and AC blueprints only. It must be
adapted to project evidence and bound to `REQ-*`; it never authorizes inferred
roles, fields or rules.

## 12. Role And Seniority Ownership

Seniority changes autonomy, not decision authority. Junior product may inventory
facts, register `REQ/REV`, and draft journeys/rules/AC; scope, value, source
conflicts, regulated rules and unresolved P0 must be escalated. Mid/senior product
owns intake, clarification, the unified PRD, baseline, change and traceability
within delegated authority. Developers and Coding Agents implement a bounded,
baselined slice and return missing business decisions as `REV-*`; they never
invent role, permission, state, field, rule or acceptance semantics. Architects
own the downstream engineering baseline and challenge irreversible/cross-system
gaps, but do not redefine product scope or customer acceptance.

| Lens | Owns in the requirement lifecycle | Cannot self-approve |
|---|---|---|
| sponsor/business | outcome, value, scope trade-off | legal/safety/customer authority outside delegation |
| product | REQ/REV/CHG, journeys, one PRD, baseline and trace | unresolved source conflicts or P0 assumptions |
| domain owner | vocabulary, invariants, source applicability | another authority's jurisdiction or contract |
| UX/prototype | discoverable paths, visible states, parity and recovery | business policy absent from baseline |
| engineering/architecture | feasibility, API/state/event semantics, recovery | product outcome and customer sign-off |
| QA/acceptance | positive/negative AC, evidence and defect reverse trace | customer/domain acceptance on their behalf |
| compliance/security | purpose, minimization, human gate, audit/retention | business acceptance outside its mandate |

A formal handoff contains baseline version/hash, stable-ID scope, forbidden
inventions, open external dependencies, owner and expected evidence. Chat or
meeting clarification does not change the baseline until a `REV/CHG` is recorded.
