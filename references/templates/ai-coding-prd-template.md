# AI Coding PRD Template — v5.0.2 Complete Contract

Use this template when the user asks for a complete PRD that product,
engineering, QA, or a coding agent can execute. It is not a thin summary. Write
large projects section-by-section, keep stable IDs, then assemble and validate
the complete document. A section may be `Not applicable` only with its business
reason and future trigger.

## 0. Contract Metadata And Source Order

```yaml
projection: ai_coding_prd
generated_from: delivery/truth/index.yaml
compiled_truth: delivery/truth/compiled/product-truth.yaml
truth_schema_version: 5.0.0
skill_version: 5.0.2
delivery_level: L2
project_shape: greenfield | brownfield | hybrid
covered_modules: []
covered_acceptance: []
unresolved_ids: []
```

List exact source paths, versions, authority order, conflicts, decisions, and
the behavior when two sources disagree. Repository reality constrains
implementation but never silently changes approved business behavior.

## 1. Outcome, Scope, Release And Success Metrics

Define business/customer outcome, in/out/deferred scope, release boundary,
dependencies, assumptions, owners, and metrics with formula, population,
period, exclusions, data source, target, and accountable owner.

## 2. Roles, Journeys, Permissions And Data Scope

| ROLE ID | Goal / Entry | Complete Journey | Allowed Actions | Data Scope | Forbidden / Isolation | Exit / Evidence |
|---|---|---|---|---|---|---|

Every in-scope role needs at least one end-to-end journey or an explicit
reason it has no interactive path. Include internal roles, customer/channel
roles, operations, product, engineering, QA, and support when in scope.

## 3. Information Architecture And Page Layout Contracts

| VIEW / Region | Route / Surface | Role | Layout / Components | Query Source | Fields | Actions | UI States | Empty/Error/No-Permission | AC |
|---|---|---|---|---|---|---|---|---|---|

Describe navigation entry, list/filter/form/detail/drawer/modal layout,
responsive behavior, representative data, and stable anchors:

```text
data-testid -> VIEW / REG / AC
data-action -> ACT
data-field  -> FLD
data-state  -> state enum
data-api    -> command or API
```

## 4. Domain Objects, Data Flow And Field Dictionary

Explain ownership and the end-to-end data path from input/import/API through
validation, state change, event, downstream projection, statistics, export,
retention, and deletion.

| Entity | FLD ID | Name / Meaning | Type / Enum | Source | Required / Default | Editable By | Validation | Sensitivity | API / Storage Mapping |
|---|---|---|---|---|---|---|---|---|---|

Specify identifiers, uniqueness, references, tenant/data-scope keys, audit
fields, optimistic version, timestamps, derived fields, and compatibility.

## 5. End-To-End Flows, State Machines And Recovery

For each `FLOW-*`, list actor, entry, ordered `VIEW/ACT` steps, visible result,
domain result, next actor, exit, and linked AC. Cover happy, validation,
permission, duplicate, concurrent update, timeout, integration failure,
retry/compensation, reconciliation, cancellation, and recovery paths.

| State Machine | From | ACT | Guard / Expected Version | To | Event | Audit | Invalid / Recovery Behavior |
|---|---|---|---|---|---|---|---|

## 6. Action And Service Contracts

| ACT ID | UI Trigger | Role / State Guard | Request Fields | Command / API | Visible Result | Domain Result | Event / Audit | Failure / Retry | AC |
|---|---|---|---|---|---|---|---|---|---|

Every action needs a handler and observable result. Server-side rules own
permission, state, money, uniqueness, idempotency, and sensitive-data checks.

## 7. API Request/Response Schema And Error Catalog

Define the uniform envelope and concrete contracts. Do not write only an
endpoint list.

### POST `/api/{module}/{resource}`

Request fields / request body:

```json
{"exampleField": "value", "expectedVersion": 1}
```

Response fields / response body:

```json
{"code": 0, "message": "success", "data": {"id": "...", "version": 2}}
```

| API ID | Auth / Data Scope | Request Validation | Response Schema | Idempotency / Concurrency | Errors | Rate / Timeout | Source IDs |
|---|---|---|---|---|---|---|---|

| Error Code / HTTP | Condition | User Message | Retryable | Client Behavior | Audit / Alert |
|---|---|---|---|---|---|
| ERR-CONFLICT / 409 | expectedVersion stale | Data changed | yes | refresh and retry | conflict audit |

## 8. Events, Async Jobs And Integration Contracts

| Event / Version | Producer | Consumers | Payload Fields | Ordering / Replay | Retry / Dead Letter | Reconciliation | AC |
|---|---|---|---|---|---|---|---|

Event payload example / 事件 Payload 示例:

```json
{"eventId":"...","eventType":"EVT-EXAMPLE","eventVersion":"v1","occurredAt":"...","aggregateId":"..."}
```

| INT ID | External System | Direction | Auth | Request/Response Mapping | SLA / Timeout | Failure / Degrade | Reconciliation | Owner |
|---|---|---|---|---|---|---|---|---|

## 9. Security, Privacy And Non-Functional Requirements

Define authentication, authorization, tenant/data isolation, PII handling,
export controls, encryption, audit, retention/deletion, accessibility,
browser/device support, performance/concurrency, availability, backup/RPO/RTO,
observability, rate limits, and explicit phase assumptions.

## 10. Repository Baseline And Engineering Boundaries

| Area | Current Reality | Required Contract | Source | Change Allowed? |
|---|---|---|---|---|
| stack/runtime | | | | |
| directory/modules/routes | | | | |
| auth/tenant/data scope | | | | |
| API/events/data | | | | |
| test/CI | | | | |
| deployment/migration | | | | |

For greenfield work, state the approved baseline or mark the decision owner;
do not let a coding agent choose business-impacting architecture silently.

## 11. Vertical Delivery Slices, Likely Files And Dependencies

| Task ID | User / Domain Result | Source IDs | Dependencies | Likely Files / Modules | API / Data / Event | Tests / Evidence | Done Signal |
|---|---|---|---|---|---|---|---|

Add a dependency graph. Each slice crosses UI, API, data, event, and tests only
as needed for one demonstrable result; do not split only by technical layer.

## 12. Machine-Readable Acceptance

Keep the authoritative copy in `delivery/acceptance/ac-structured.yaml` and
embed or link each P0/P1 AC. Every P0 feature needs happy and applicable
negative paths.

```yaml
- id: AC-EXAMPLE-001
  priority: P0
  preconditions: []
  steps: []
  expected_visible: ""
  expected_domain: ""
  test_anchors: [VIEW-EXAMPLE, ACT-EXAMPLE]
  evidence_required: [automated_test, api_trace]
```

## 13. Statistics, Metrics And Calculation Caliber

| Metric ID | Meaning | Formula | Population / Time Window | Exclusions | Data Source / Refresh | Permission | Reconciliation | AC |
|---|---|---|---|---|---|---|---|---|

If no statistics are in scope, write `Not applicable` plus the business reason
and trigger for adding this contract.

## 14. Deployment, Migration, Rollback And Operations

Define environment/config dependencies, seed/import, compatibility,
coexistence, migration/backfill, verification, rollout, rollback, scheduled-job
idempotency, monitoring/alerts, support owner, and incident recovery. Greenfield
projects still require deployment and rollback boundaries.

## 15. Forbidden Invention, Unknowns And Completion

- Do not invent pages, roles, fields, states, permissions, APIs, integrations,
  statistics, or business rules.
- Record missing decisions as `UNK-*` and conflicts as `CFL-*`; block only the
  affected slice.
- Preserve all approved P0 roles, paths, exceptions, and ACs under context
  pressure; write/checkpoint more slices instead of shortening the contract.
- Report passing, failing, blocked, and not-run validation separately.

Completion is `PASS`, `REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`, with exact
validator commands and evidence locations.
