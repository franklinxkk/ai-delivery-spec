# Human-First Projection Template - v5.0.0

This is a readable projection of `delivery/truth/product-truth.yaml`. It is not
an independent source of truth. Preserve all stable IDs and link annotated
prototype views where available.

## 0. Projection Metadata

```yaml
projection: human_first
generated_from: delivery/truth/product-truth.yaml
truth_schema_version: 5.0.0
generated_at:
covered_modules: []
covered_flows: []
known_gaps: []
```

## 1. Executive Product Contract

### 1.1 Outcome And Why Now

State customer outcome, business outcome, evidence, current workaround, and
riskiest assumption. Keep solution detail out of this section.

### 1.2 Scope And Release Boundary

| In Scope | Out Of Scope | Priority | Source / Decision | Revisit Condition |
|---|---|---|---|---|

### 1.3 Success And Acceptance

| Metric ID | Metric / Caliber | Baseline | Target / Time | Source | Owner |
|---|---|---|---|---|---|

### 1.4 Roles And Responsibility

| Role ID | Role | Job | Data Scope | Final Decision | Forbidden Action |
|---|---|---|---|---|---|

## 2. End-To-End Journey

| Flow ID | Trigger | Actors | Modules | Main Steps | Success Exit | Exception / Compensation | Acceptance |
|---|---|---|---|---|---|---|---|

Describe the primary journey in plain language before module details. For ToB
or ToG, show where customer, delivery, acceptance, governance, and product
lifecycles meet.

## 3. Module Delivery Slices

Repeat this section for every in-scope `MOD-*`.

### MOD-XXX — {Module Name}

#### 3.x.1 Outcome And Role Task

| Outcome | Primary Roles | Entry | Success Exit | Next Module / Action |
|---|---|---|---|---|

#### 3.x.2 Business Flow

| Step | Actor | View | Action | Visible Result | Domain Result | Failure / Recovery |
|---:|---|---|---|---|---|---|

Use `FLOW/VIEW/ACT` IDs. Do not write “system processes it” without the state,
record, event, or downstream result.

#### 3.x.3 Page Map And Data Presentation

| View ID | Surface | Region ID | Layout / Components | Data Shown | Data Source | Visible States | Role Variant |
|---|---|---|---|---|---|---|---|

Cover default, empty, loading, error, no-permission, partial, and success states
when applicable. Link prototype screenshot/route by View ID.

#### 3.x.4 Fields And Dictionaries

| Field ID | Name | Type | Source | Required | Dictionary / Caliber | Editable By | Validation / Error | Sensitivity |
|---|---|---|---:|---|---|---|---|---|

Reference a global field dictionary when reused; do not duplicate conflicting
definitions.

#### 3.x.5 Actions And Click Effects

| Action ID | Trigger | Role / Allowed State | Confirmation / Guard | Frontend Effect | Command | Domain Result | Failure Effect | AC |
|---|---|---|---|---|---|---|---|---|

Every core action must create an observable result and a durable domain result.

#### 3.x.6 State, Button, And Lifecycle

| State Machine | Current State | Visible / Allowed Actions | Forbidden Actions | Guard | Next State | Event / Audit |
|---|---|---|---|---|---|---|

#### 3.x.7 Rules, Permissions, And Exceptions

| Rule / Scenario ID | Condition | Owner | Enforcement | User Feedback | Audit / Escalation | Recovery |
|---|---|---|---|---|---|---|

Include validation, permission, stale state, duplicate, timeout, dependency,
offline/concurrency, sensitive export, and high-risk human gate as applicable.

#### 3.x.8 Data, Integration, And Events

| ID | Source / Producer | Target / Consumer | Payload / Mapping | Freshness / Order | Failure | Retry / Reconciliation | Owner |
|---|---|---|---|---|---|---|---|

#### 3.x.9 Acceptance And Evidence

| AC ID | Priority / Type | Preconditions | Steps | Expected Visible | Expected Domain | Required Evidence |
|---|---|---|---|---|---|---|

## 4. Cross-Module Contracts

| Flow | Shared Object | State Owner | Source → Target Mapping | Event / Command | Permission Intersection | Failure / Compensation | AC |
|---|---|---|---|---|---|---|---|

## 5. NFR And Operational Boundary

Load only applicable NFR profiles. State measurable acceptance and owner for
availability, performance, security, privacy, accessibility, audit, backup,
observability, migration, support, and AI runtime.

## 6. Decisions, Unknowns, And Conflicts

| ID | Type | Question / Conflict | Impact | Temporary Behavior | Owner | Due | Status / Resolution |
|---|---|---|---|---|---|---|---|

P0 unknowns cannot be hidden in notes.

## 7. Traceability Summary

| Module | Flows | Views | Actions | State Machines | AC | Prototype | Completion |
|---|---|---|---|---|---|---|---|

Completion is `PASS`, `REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED` for the named
scope and links to evidence. Do not use project WBS, bug logs, or daily follow-up
tables inside this projection.
