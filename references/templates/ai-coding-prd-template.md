# Coding-Agent Projection Template - v5.0.0

Generate this only from approved Product Truth when an implementation agent or
development team will build/change the product. Do not copy the complete
Human-First projection. Reference stable IDs and add implementation contracts.

## 0. Projection Metadata

```yaml
projection: coding_agent
generated_from: delivery/truth/product-truth.yaml
truth_schema_version: 5.0.0
project_shape: greenfield | brownfield | hybrid
generated_at:
covered_modules: []
covered_acceptance: []
```

## 1. Source-Of-Truth Order

1. approved Product Truth;
2. approved Change Packages for the target release;
3. locked IA/prototype for visible structure and behavior;
4. API/event/data contracts;
5. acceptance and evidence requirements;
6. repository reality for implementation constraints, never for silently
   changing business behavior.

List exact paths and versions. If sources conflict, stop the affected slice and
create `CFL-*`; do not guess.

## 2. Repository Baseline

| Area | Current Reality | Constraint / Contract | Source | Change Allowed? |
|---|---|---|---|---|
| stack/runtime | | | | |
| modules/routes | | | | |
| auth/tenant/data scope | | | | |
| API/events/data | | | | |
| tests/CI | | | | |
| migration/deployment | | | | |

For brownfield work, include preserved behaviors, compatibility, migration,
coexistence, rollback, and retirement.

## 3. Implementation Inventory

| Module | Flow | Views | Actions | Entities / States | Integrations | AC | Unknowns |
|---|---|---|---|---|---|---|---|

No module is ready if a referenced ID is missing from Product Truth.

## 4. Vertical Delivery Slices

| Task ID | User / Domain Result | Source IDs | Dependencies | Likely Files / Modules | Tests / Evidence | Done Signal |
|---|---|---|---|---|---|---|

Tasks cut through UI, API, data, event, and test only as needed for one
demonstrable result. Do not split purely by technical layer.

## 5. Page And Action Routing

### 5.1 View Contract

| View / Region | Route / Surface | Query Source | Fields | Actions | UI States | Role / Scope | AC |
|---|---|---|---|---|---|---|---|

### 5.2 Action Contract

| Action ID | UI Trigger | Role / State Guard | Command / API | Request Fields | Visible Result | State / Event / Audit | Failure / Retry | AC |
|---|---|---|---|---|---|---|---|---|

Prototype anchors:

```text
data-testid -> VIEW/REG/AC
data-action -> ACT
data-field  -> FLD
data-state  -> state enum
data-api    -> command/API when known
```

## 6. State, Data, API, And Event Contracts

### 6.1 State Transitions

| State Machine | From | Action | Guard / Expected Version | To | Event | Audit | Invalid Behavior |
|---|---|---|---|---|---|---|---|

### 6.2 API / Command / Query

| ID | Method / Type | Path / Name | Auth / Scope | Request | Response | Idempotency | Errors | Source IDs |
|---|---|---|---|---|---|---|---|---|

### 6.3 Events And Async Behavior

| Event | Producer | Consumers | Payload Version | Ordering / Replay | Retry / Dead Letter | Reconciliation | AC |
|---|---|---|---|---|---|---|---|

### 6.4 Fields And Migration

| Field ID | Storage / API Mapping | Type / Enum | Source | Validation | Sensitivity | Migration / Backfill | Compatibility |
|---|---|---|---|---|---|---|---|

## 7. Structured Acceptance

Keep machine-readable acceptance in `delivery/acceptance/`. Every row includes
AC ID, preconditions, steps, expected visible/domain result, test anchors,
evidence type, and result location. Generate positive and applicable negative
paths; never treat the acceptance file itself as execution evidence.

## 8. Agent Operating Rules

- Implement only approved IDs and Change Packages.
- Do not invent pages, fields, states, roles, permissions, or business rules.
- Enforce state, money, permission, and tenant rules on the backend.
- Record audit for state-changing and sensitive operations.
- Preserve stable IDs in tests and prototype attributes.
- Report repository/truth conflicts instead of silently adapting behavior.
- Write test/evidence results back to the declared evidence paths.
- Do not mark a slice done until its AC evidence exists.

## 9. Validation And Completion

List syntax, schema, unit, integration, E2E, migration, accessibility, security,
and manual UAT commands applicable to the slice. Report passing, failing,
blocked, and not-run separately.

Completion is scoped `PASS`, `REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`; include
unresolved `UNK/CFL/CHG` IDs.
