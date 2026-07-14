# Role and Seniority Stage Playbook

Use this reference only for multi-role requirements, formal handoffs, team
onboarding, or a request aimed at a named role/seniority. It defines who owns a
decision, who challenges it, and what evidence crosses the stage gate. It does
not assign sprint tasks or replace team accountability.

## Contents

- Seniority lanes
- Role ownership
- Stage matrix
- Handoff rules
- No-guess checks

## Seniority lanes

| Lane | May do independently | Must escalate |
|---|---|---|
| Junior product | inventory facts, register REQ/REV, draft journeys/rules/AC, run checklists | scope/value priority, conflicting authority, sensitive/regulated rule, unresolved P0 |
| Mid-level product | lead intake/clarification/spec/review, maintain baseline/change/trace, coordinate acceptance | cross-product strategy, contractual exception, high-impact risk acceptance |
| Senior product / product owner | decide outcome, scope, priority, source precedence, risk disposition and customer baseline | customer/legal/safety decisions outside delegated authority |
| Junior developer | implement a baselined bounded slice, report ambiguity, link tests/evidence | missing state/rule/permission/API semantics; never invent a business decision |
| Mid-level developer | review feasibility, interface/state semantics, compatibility, idempotency and recovery | architecture/security/capacity decisions beyond delegated boundary |
| Senior developer / tech lead | own engineering review, cross-module consistency, migration and integration risk | enterprise architecture or business-policy decisions |
| Architect | define technical architecture from the approved business contract; challenge irreversible, cross-system and NFR gaps | product scope, customer acceptance and domain authority |

Seniority changes autonomy, not truth. A senior participant cannot approve a
decision owned by the customer, legal/safety authority, or accountable domain
owner.

## Role ownership

| Role lens | Owns | Required challenge |
|---|---|---|
| Sponsor / business owner | observable outcome, value, scope trade-off, authority | reject feature lists with no outcome/evidence |
| Product | REQ/REV/CHG, journeys, rules, one PRD, baseline and trace | prevent unresolved decisions from becoming facts |
| Domain owner | vocabulary, invariants, lifecycle, source applicability | identify vendor/project variation and regulated boundaries |
| UX / prototype | discoverable role paths, full UI states, recovery and parity | expose invisible handoffs and action/result gaps |
| Engineering / architecture | feasibility, state/API/event semantics, idempotency, integration, migration | issue `REV-*` when implementation would require business invention |
| QA / acceptance | positive/negative AC, data, observable evidence, defect reverse trace | reject keyword-only or non-executable acceptance |
| Compliance / security | authority, data minimization, human gate, retention and audit | block unauthorized or unaccountable consequential behavior |
| Customer acceptance | real operating path, organization boundary, acceptance result and sign-off | reject simulated/static evidence as business acceptance |

## Stage matrix

### Intake

- Sponsor: outcome, evidence, decision authority, target iteration.
- Product: `REQ-*`, source order, scope, dependency, tier and decision.
- Domain: core object, lifecycle risk, applicable authority and unknowns.
- UX: primary task, entry and visible success; decide whether prototype is needed.
- Engineering/architecture: impact dimensions, integrations, legacy signals,
  complexity band and irreversibility; no invented person-days.
- QA/compliance/customer: acceptance observability, critical counterexample,
  sensitive/regulated boundary and acceptance owner.
- Gate: value, owner, boundary and material unknowns are explicit.

### Clarify

- Product batches independent questions and closes role/data scope, main and
  exception flows, state authority, rules and acceptance.
- Domain resolves terminology/invariant/source conflicts or names the owner.
- UX closes entry, discoverability, feedback, recovery and handoff states.
- Engineering/architecture closes interface semantics, concurrency/idempotency,
  migration, compatibility, compensation and reconciliation unknowns.
- QA/compliance/customer close negative cases, test data/evidence, legal
  authority, on-site path and conditional-acceptance rules.
- Gate: no unresolved P0 is disguised as a confirmed rule.

### Specify

- Product owns one readable PRD and stable-ID trace.
- Domain owns entity/lifecycle/invariant accuracy and source applicability.
- UX owns view/region/action/state mapping and testable role journeys.
- Engineering/architecture owns the review of business API/event semantics,
  failure/recovery and forbidden inference; it does not put database/framework
  choices into the PRD unless they are business contracts.
- QA owns executable AC and evidence anchors; compliance owns human gates and
  audit events; customer confirms readable operating results.
- Gate: one `REQ-*` slice can be designed, implemented and tested without a new
  business decision.

### Review

Each lens independently records `REV-*`, affected IDs, severity, decision owner,
disposition and closure evidence. Majority opinion cannot override safety,
authority, privacy, money, or customer-acceptance blockers.

### Baseline

- Sponsor/customer/domain owner approve only within their authority.
- Product freezes baseline ID/version, included REQs, source order, approved
  gaps, prototype binding and synchronization recipients.
- Engineering/architecture confirms the no-guess handoff and external
  dependencies; QA freezes AC and mandatory regression scope.
- Gate: every consumer can reproduce the same approved facts.

### Change

- Product opens `CHG-*` with before/after and bidirectional impact.
- Domain checks historical meaning and new exceptions.
- UX checks page/action/path parity.
- Engineering/architecture checks API/event/data, migration, idempotency,
  rollback, compensation and reconciliation.
- QA/compliance/customer update regression, evidence validity, authority and
  acceptance version.
- Gate: impacted artifacts are synchronized before re-baseline.

### Acceptance

- QA executes each mandatory AC and records actual/evidence/defects.
- Product links defects and changes back to `REQ-*` and proposes requirement
  closure only when conditions hold.
- Domain, compliance and customer sign their respective business, authority and
  operating results; development supplies technical evidence but cannot sign on
  their behalf.
- Gate: accepted, conditionally accepted, or rejected is explicit and traceable.

## Handoff rules

1. A handoff contains baseline version, stable-ID slice, prohibited inventions,
   open external dependencies and expected evidence.
2. A receiver returns ambiguity as `REV-*`; chat clarification alone does not
   alter the baseline.
3. A developer or Coding Agent may choose implementation details only inside the
   approved business contract.
4. Architecture review is required for cross-system state ownership,
   irreversible migration, regulated data, high concurrency, money or safety.
5. Static validator PASS is readiness evidence only; QA/customer acceptance
   requires execution and accountable sign-off.

## No-guess checks

- Can a junior product user identify exactly what decision must be escalated?
- Can a traditional developer read the main flow before machine annexes?
- Can a Coding Agent implement one slice without inventing role/state/rule/error?
- Can an architect distinguish business invariants from technical design space?
- Can QA derive positive, negative, permission, concurrency/external-failure and
  brownfield regression cases?
- Can a defect or acceptance result trace back to the original requirement and
  the approved baseline?
