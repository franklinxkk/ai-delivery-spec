# Readability Layer

Use this file when generating or reviewing a PRD, product specification, or
development handoff document for L1 or above. It sits on top of
`delivery-core.md` and the selected PRD template. It does not replace FRR,
source evidence, DDD/API/data contracts, or acceptance coverage.

## Contents

- Purpose
- Executive Summary
- Scenario-First Module Writing
- Boundary And Exception Coverage
- Metrics And Event Tracking
- Frontend Backend QA Handoff Notes
- Business Examples
- Visual Hierarchy And Language Rules
- Readability Acceptance Checklist

## Purpose

Machine-readable contracts make AI coding and automated verification easier.
Human-readable PRD structure makes product review, RD implementation, frontend
interaction, backend service design, and QA test authoring possible without
guessing. A development-ready PRD must do both.

Rule: narrative explains why and when; tables define what and how to verify.
Do not produce a document that is only tables, schemas, and IDs.

## Executive Summary

Every PRD or standalone module specification must start with a short executive
summary after the version table. Keep it within one screen.

Required fields:

```markdown
## Executive Summary

**Problem**: 1-2 sentences naming the concrete user/business pain.
**Primary Roles**: roles that operate or approve the capability.
**Release Scope**: 2-4 highest-value functions in this iteration.
**Out Of Scope**: 1-3 high-expectation items explicitly excluded.
**Hard Constraints**: compliance, dependency, data, deadline, or rollout limits.
**Acceptance Signal**: 1-2 measurable success indicators.
```

Reject vague phrases such as “improve experience”, “make it intelligent”, or
“support related operations” unless followed by measurable behavior.

## Scenario-First Module Writing

Before listing function records, every module must include core business
scenarios. Each scenario answers `who / when / why / what / result`.

Scenario table:

| Scenario ID | Role | When / Trigger | Goal | Main Action | Success Result | Exception To Watch |
|---|---|---|---|---|---|---|
| SC-M01-01 | | | | | visible result + domain result | |

Rules:

- Do not start a module with API, SQL, DDD, or field tables. Start with the
  business scene so RD and QA understand why the module exists.
- One scenario may map to multiple FRRs. Each FRR must trace back to at least
  one scenario or state why it is system/internal.
- If a module has no scenario, it is likely a technical appendix, not a product
  module.

## Boundary And Exception Coverage

Every release function must explicitly cover business boundary and exception
paths, not only technical failures.

Minimum checklist:

| Category | Required Coverage |
|---|---|
| Input validation | required, format, enum, length, special characters, duplicate, cross-field dependency |
| Empty / loading / error | empty state, first load, long load, API failure, timeout, retry, partial success |
| Permission | vertical overreach, horizontal overreach, field-level masking/editing, expired/disabled account |
| State conflict | stale data, repeated submit, already processed, withdrawn/deleted/locked object |
| Network / offline | weak network, offline queue, retry, local draft, sync conflict |
| Business fallback | manual handling, escalation, return/reject, rollback/compensation, audit trail |

Do not write only “network error handled”. State the visible feedback, data
preservation rule, retry path, and domain/audit result.

## Metrics And Event Tracking

Every major module or release function must define business metrics and event
tracking when the product will be operated after launch.

Business metric table:

| Metric ID | Metric | Formula / Caliber | Dimension | Baseline | Target | Owner |
|---|---|---|---|---|---|---|
| MET-M01-01 | | | role/org/time/status | | | |

Event tracking table:

| Event ID | Event Name | Trigger Moment | Required Params | Purpose | Privacy / Masking |
|---|---|---|---|---|---|
| EVT-M01-01 | | button clicked / state changed / task completed | user_id, role, tenant_id, object_id, status | | |

Rules:

- Tracking should serve operation, conversion, risk monitoring, compliance, or
  product improvement. Do not add decorative events.
- Sensitive identifiers must be masked, hashed, or omitted according to privacy
  requirements.
- For AI features, track prompt/model/rule version, confidence bucket, fallback
  reason, human confirmation, and final outcome where applicable.

## Frontend Backend QA Handoff Notes

Each FRR or module shared contract should include a compact handoff note when
the section will be used by multiple roles.

| Role | What They Need |
|---|---|
| Frontend | component states, disabled/hidden/highlight behavior, modal/toast/copy, loading/empty/error, responsive/interaction notes |
| Backend | source of truth, validation owner, permission/data-scope guard, state transition, idempotency, audit/event, dependency failure behavior |
| QA | priority happy path, boundary values, permission/overreach cases, state conflict, weak network, regression path |

This is not a second specification. It is a reader aid that points to FRR,
state matrix, prototype contract, and acceptance IDs.

## Business Examples

Any threshold, formula, time window, scoring rule, AI confidence rule, or
non-obvious state guard must include at least one concrete example.

Format:

```markdown
Rule-03: When unread notice count > 0 and required_read_seconds is enabled,
the sign button remains disabled until countdown reaches 0.

Example: Notice A requires 30 seconds. The enterprise signer opens it at
10:00:00. The sign button is disabled from 10:00:00 to 10:00:29 and becomes
enabled at 10:00:30 if the page remains active.
```

Pure enum values and self-explanatory fields do not need examples.

## Visual Hierarchy And Language Rules

Use structure consistently:

| Content | Preferred Format |
|---|---|
| cause, context, tradeoff | prose paragraph |
| sequential operation | numbered list |
| fields, states, actions, rules, events | table |
| schema / API / config | fenced code block |
| unresolved risk | callout block with owner and deadline |

Language rewrite rules:

| Avoid | Replace With |
|---|---|
| supports X | list exact actions and results |
| improve efficiency | measurable before/after signal |
| intelligent processing | input -> AI/rule -> output -> human confirmation |
| related fields | complete field list or authoritative annex |
| see prototype / same as above / existing logic | exact FRR ID and section, or full expansion |
| TBD | open question with owner, deadline, and impact |

Keep requirement sentences short. Split multi-condition statements into numbered
rules.

## Readability Acceptance Checklist

Before marking a PRD ready for handoff:

- [ ] Executive Summary exists and is concrete.
- [ ] Every module starts with business scenarios before field/API/DDD tables.
- [ ] Every FRR traces to scenario, source evidence, state/domain result, and acceptance.
- [ ] Boundary and exception coverage includes validation, empty/loading/error,
      permission, state conflict, network/offline, and business fallback.
- [ ] Major modules define metrics and event tracking when operation data is needed.
- [ ] Thresholds, formulas, time windows, AI confidence rules, and non-obvious
      guards have examples.
- [ ] Frontend/backend/QA handoff notes exist for multi-role sections.
- [ ] No vague language remains without measurable behavior or owner.
