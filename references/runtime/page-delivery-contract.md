# Page Delivery Contract

Use this reference when a PRD or prototype will be handed to human engineers,
QA, architects, or Coding Agents for direct implementation. It closes the gap
between a module-level feature description and an implementable page.

## 1. Declare The Page Scope

List every in-scope page in the PRD frontmatter:

```yaml
page_contract_view_ids:
  - VIEW-RESOURCE-LIST
  - VIEW-RESOURCE-EDIT
```

Only declared views are implementation scope. Record removed, merged, or
renamed views in `CHG-*`; a prototype must not expose undeclared navigation.

## 2. Write One Contract Per View

Start each contract with this exact marker so the deterministic gate can check
coverage:

```markdown
<!-- PAGE-CONTRACT: VIEW-RESOURCE-LIST -->
```

Each block must state all of the following. Use `Not applicable + reason` when
a surface genuinely does not apply; silence is not a decision.

1. **Page purpose and entry** — actor, entry, precondition, completion result.
2. **Region layout** — region order, width/placement, sticky/scroll behavior,
   responsive priority, empty/loading/error/no-permission states.
3. **Metric caliber** — `METRIC-*`, definition, formula, numerator/denominator,
   time window, timezone, filters, status inclusion, deduplication, freshness,
   source, zero denominator and display format.
4. **Filters and search** — field, control, operator, options/source, default,
   cascade, reset and query behavior.
5. **List/tree/canvas columns** — column, bound field, format, width, null,
   sort, visibility, row selection, default order and fixed columns.
6. **Fields and controls** — `FLD-*`, control, required/default, type, length,
   validation, dictionary, dependency, editability by state/role, help/error.
7. **Actions and permissions** — `ACT-*`, trigger, role/data scope, state guard,
   confirm surface, visible result, domain result, failure/recovery and `AC-*`.
8. **Modal/drawer chains** — title, size, sections, fields, buttons, cancel,
   dirty-close, loading, success, failure and durable result after close.
9. **Import/export** — formats, template version, limits, validation/preflight,
   partial failure, retry, selected scope/columns, file naming, async job,
   security and audit.
10. **Pagination and bulk behavior** — default/allowed page sizes, total,
    default sort, selection across pages, maximum batch and mixed-state rules.
11. **State and exceptions** — default, empty, loading, error, partial, stale,
    no-permission, conflict, duplicate, external failure and recovery.
12. **Prototype binding** — `VIEW/REG/ACT/FLD/STATE/AC` anchors and sample data.

## 3. Required Tables

### Metric contract

| METRIC | Name | Definition/formula | Window/filter/status/dedup | Source/freshness | Zero/null | Format |
|---|---|---|---|---|---|---|

Never use labels such as “完成率” or “成功率” without defining the population,
event, time window and zero denominator. Put the metric beside the page that
displays it; the global metric appendix is an index, not its only definition.

### Filter and column contract

| ID | UI label | Bound field | Control/format | Default/operator | Options/null | Sort/width |
|---|---|---|---|---|---|---|

### Field contract

| FLD | Label | Control | Required/default | Type/length | Validation/dictionary | Editable role/state |
|---|---|---|---|---|---|---|

“Supports CRUD” is not a requirement. Specify create, view, edit, delete/
disable, guard, consequence and recovery separately.

### Action contract

| ACT | Trigger | Role/state guard | Confirm/input | Visible result | Domain result | Failure/recovery | AC |
|---|---|---|---|---|---|---|---|

## 4. File And Preview Contract

For uploads, specify accepted extensions/MIME types, per-file size, batch
count/total, duplicate rule, virus/hash validation, upload cancellation,
processing/transcoding, metadata completion and submission guard.

For previews, specify behavior by file type: video controls and renditions,
document/page conversion, slide navigation, image zoom/rotate, unsupported/
failed conversion and authorization/watermark behavior.

For exports, specify scope, filters, selected rows, fields/order, format,
encoding, file name, maximum synchronous volume, async threshold, expiry,
masking and audit.

## 5. Composer And Drag Contract

For course/workflow/layout composers, define hierarchy, selection owner,
allowed source and target, insertion index, same-level/cross-level rules,
hover cue, invalid drop, ordering persistence, undo or recovery, concurrent
editing and a keyboard/button alternative. Every aggregate metric must refresh
from the persisted draft model, not inferred DOM text.

## 6. No-Guess Handoff Check

Before baseline, run every declared view through the four lenses in
`four-lens-module-walkthrough.md`. Ask frontend, backend, QA and a Coding Agent
to reconstruct their implementation or test plan using only that page block and
shared appendices. The contract fails if any lens must invent a displayed
column, field rule, endpoint, entity relationship, metric formula, action guard,
modal content, pagination limit, import/export rule, negative test or
post-action state.

## 7. Managed Relation Contract

When a role manages a parent object's complete child/target collection—such as
an organization's members, a partner's authorizations, a course's resources,
or an order's lines—declare the view in `managed_relation_view_ids` and add a
`REL-*` contract inside that page block. A parent-row count and a one-off create
button are not a maintenance surface.

The relation contract must name the parent, child/target and immutable version;
inventory entry, filters and columns; direct versus inherited/source relations;
single and bulk add/adjust/revoke; preflight and conflict policy; partial failure,
idempotency and concurrency; downstream impact and recovery; API, event/audit and
`AC-*`. If no such collection exists, state `Not applicable + reason`; never add
an external-role portal merely to satisfy this check.
