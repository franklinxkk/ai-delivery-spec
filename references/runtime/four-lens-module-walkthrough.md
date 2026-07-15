# Four-Lens Module Walkthrough

Use this review before baselining a multi-page L3/L4 PRD or prototype. Review
every declared `VIEW-*` independently; a green cross-module happy path cannot
hide a thin page.

## 1. Frontend lens

For each view, reconstruct the screen without guessing:

- entry, regions, placement, sticky/scroll/responsive behavior;
- metrics, filters, columns/tree/canvas, row actions and pagination;
- every create/edit/detail/review modal or drawer, including all `FLD-*`;
- required/default/control/type/length/dictionary/dependency/editability;
- upload types, size/count, preview, import/export and partial failure;
- every `ACT-*` has a visible durable outcome and the correct entity form;
- prototype anchors exist and CSS utilities/state classes cannot pollute other
  components (`.status.active`, not a global grouped `.active` selector).

Reject if a frontend developer must invent a component, field, validation,
empty/error state, modal chain or post-action display.

## 2. Backend lens

For each view, trace its queries and writes:

- list/detail/option-source API paths, request/response fields and types;
- permission/data-scope and state/dependency guards;
- domain entity/version/snapshot relationships and ownership;
- transaction boundary, idempotency, optimistic locking and async retry;
- domain result, event/audit, downstream visibility and rollback/recovery;
- every displayed metric maps to a server-side formula, source and refresh;
- every `ACT-*` resolves to an explicit endpoint or an explicit no-write result.

Reject if a backend developer must invent an entity relationship, endpoint,
status transition, data-scope filter, metric aggregation or failure behavior.

## 3. QA lens

For each view, derive executable positive and negative tests:

- each P0 action binds `AC-*` with preconditions, steps, visible/domain result,
  negative case and evidence;
- field boundaries cover empty/min/max/format/dictionary/dependency/concurrency;
- permission, data isolation, stale version, duplicate request and retry paths;
- list/filter/sort/page/export values reconcile with source facts and metrics;
- modal identity tests prevent cross-entity reuse;
- role handoff and downstream pool visibility are tested end to end;
- defects can reverse-trace to `REQ/VIEW/ACT/API/AC` and object version.

Reject if QA must translate prose into an undisclosed rule or cannot observe the
domain result independently of a toast.

## 4. Coding Agent lens

Give the agent only one page contract plus shared appendices. It must be able to
produce a deterministic implementation plan containing:

- exact components and `data-*` anchors;
- typed fields, DTOs, endpoints and state guards;
- metric queries and zero/error behavior;
- action handler to domain-service mapping;
- positive/negative automated tests and trace IDs;
- a list of explicit `GAP-*` items, which must be empty at baseline.

Reject if two agents can make materially different choices while both claiming
to follow the contract.

## 5. Compact sign-off record

Keep the record lightweight; do not generate a second PRD.

| VIEW | frontend | backend | QA | Coding Agent | gaps fixed | evidence |
|---|---|---|---|---|---|---|
| VIEW-* | pass/fail | pass/fail | pass/fail | pass/fail | CHG/GAP IDs | page/API/AC/browser refs |

The review is complete only when every declared view is pass in all four lenses,
all material gaps are synchronized into the one PRD and prototype, and the
deterministic gate plus representative browser journeys pass.
