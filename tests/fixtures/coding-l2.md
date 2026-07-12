# Generic Operations Console AI Coding PRD

## 0. Source-of-truth order and scope

Generated_from Product Truth. Approved scope has module MOD-CORE and one operator workflow. Unknown
and conflict items block only affected slices.

## 1. Outcome and metrics

Metric caliber: successful submissions / eligible submissions per calendar day.

## 2. Roles, permission and data scope

| ROLE ID | Journey | Permission | Data scope |
|---|---|---|---|
| ROLE-ADMIN | Open VIEW-HOME, submit ACT-SUBMIT, verify success | create | own tenant |

## 3. Information architecture and page layout

| View | Region | Fields | Actions | UI states |
|---|---|---|---|---|
| VIEW-HOME | REG-FORM | FLD-NAME | ACT-SUBMIT | loading/error/success |

## 4. Field dictionary and data flow

| Entity | Field ID | Meaning | Type | Validation | Sensitivity |
|---|---|---|---|---|---|
| ENT-ITEM | FLD-NAME | Display name | string | 1..100 chars | internal |

Input flows from VIEW-HOME to API, persisted state, EVT-ITEM-CREATED and metrics.

## 5. FLOW-ITEM-CREATE and state machine

| State Machine | From | Action | Guard | To | Failure / recovery |
|---|---|---|---|---|---|
| SM-ITEM | draft | ACT-SUBMIT | ROLE-ADMIN + version | active | retain input and retry |

## 6. Action contract

| ACT ID | Trigger | Request fields | Visible result | Domain result | Audit | AC |
|---|---|---|---|---|---|---|
| ACT-SUBMIT | click | FLD-NAME | success toast | item active | creation audit | AC-ITEM-001 |

## 7. API request/response and errors

### POST `/api/items`

Request fields / request body: `name`, `expectedVersion`, `clientRequestId`.
Response fields / response body: `code`, `message`, `data.id`, `data.version`.

| API | Idempotency | Error code | HTTP | Client behavior |
|---|---|---|---|---|
| POST /api/items | clientRequestId | ERR-CONFLICT | 409 | refresh and retry |

## 8. Events, async and integration contracts

Event Payload Version: `EVT-ITEM-CREATED v1` with eventId, aggregateId and name.
Retry three times, then dead letter; owner reconciles by aggregateId. Integration
is Not applicable because this bounded module has no external system; add when
an outbound consumer is approved.

## 9. Security, privacy and NFR

Server enforces permission and tenant scope. P95 API latency <= 500 ms. Audit
state changes and retain records for the approved period.

## 10. Repository baseline

| Area | Current reality | Contract | Change allowed |
|---|---|---|---|
| stack | web + API | existing runtime | no |
| tests/CI | unit + integration | required | yes |

## 11. Vertical delivery slices, likely files and dependencies

| Task | Result | Dependencies | Likely Files / Modules | Tests / Evidence |
|---|---|---|---|---|
| TASK-ITEM-001 | item created | auth module | views/items, api/items | AC-ITEM-001 trace |

## 12. Machine-readable acceptance

```yaml
- id: AC-ITEM-001
  preconditions: [ROLE-ADMIN authenticated]
  steps: [open VIEW-HOME, enter FLD-NAME, invoke ACT-SUBMIT]
  expected_visible: success toast
  expected_domain: item is active exactly once
  evidence_required: [automated_test, api_trace]
```

## 13. Statistics and calculation caliber

Metric uses successful unique request IDs, excludes validation failures, and
refreshes daily from item records.

## 14. Deployment, migration, rollback and operations

Migration is Not applicable for empty greenfield storage. Deploy with health
check; rollback application version on failure. Operations monitor error rate,
latency, dead letters, and audit write failures.

## 15. AI runtime and evaluation contract

AI runtime is Not applicable because no model behavior is in scope; add prompt
version and tool policy if AI behavior is approved. Evaluation contract is Not
applicable; human gate and accountable owner become mandatory on that trigger.

## 16. Forbidden invention and completion

Forbidden invention: do not add roles, fields, pages, states, APIs, or rules.
Tests bind AC-ITEM-001 and write evidence. Complete only when tests pass.
