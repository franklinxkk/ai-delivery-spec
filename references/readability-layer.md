# Readability Layer

Use this file when generating or reviewing a PRD, product specification, or
development handoff document for L1 or above. It sits on top of
`delivery-core.md` and the selected PRD template. It does not replace FRR,
source evidence, DDD/API/data contracts, or acceptance coverage.

## Contents

- Purpose
- Role-Oriented PRD Completeness
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

## Role-Oriented PRD Completeness

A development-ready PRD must support different readers from one source of
truth. Do not create separate unsynchronized PRDs for product, design,
frontend, backend, algorithm, and QA.

| Reader | The PRD Must Answer |
|---|---|
| Sponsor / PM | What problem is solved, which users and scenarios matter, what is in/out, how success is measured, and what risks remain |
| UX / UI | user journey, IA, page regions, page states, interaction copy, empty/error/disabled states, accessibility and responsive constraints |
| Frontend | component states, interaction triggers, client validation, loading/empty/error, multi-surface differences, `data-testid` / `data-action` mapping |
| Backend | source of truth, fields/dictionaries, validation owner, permission/data scope, state transition, idempotency, dependencies, audit/event |
| Algorithm / AI | input/output schema, model/rule/prompt responsibility, confidence threshold, human confirmation, evaluation cases, fallback and prohibited writes |
| QA | happy path, boundary values, permission overreach, state conflict, weak network, dependency failure, regression path, expected UI/domain result |

Rules:

- Each major module must contain or link to these reader answers.
- A reader-aid table can point to FRR/state/prototype/acceptance IDs, but it
  cannot replace the detailed FRR.
- If one reader cannot identify their implementation or test responsibility
  from the PRD without asking the PM, Gate 3 is not ready.

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

## Page Layout And Component Constraint

For every primary page in a delivery-ready PRD, output a structured layout
region diagram and component constraints so that frontend developers and
coding agents can reproduce the page without inspecting the prototype pixel
by pixel.

### Per-Page Layout Region Diagram

Each primary page must produce a region diagram table:

| Region ID | Region Name | Position | Approximate Size | Primary Component | Data Source | Empty State | Loading State | Error State |
|---|---|---|---|---|---|---|---|---|
| R1 | Header | top | full-width, 60px | PageHeader | N/A | N/A | skeleton | "页面加载失败" + retry button |
| R2 | Filter Bar | below header | full-width, auto | Form + Select + DatePicker | filter store | "请选择筛选条件" | skeleton row | inline error toast |
| R3 | Table | main | full-width, flex-1 | ProTable | `/api/entities` list | "暂无数据" illustration | skeleton rows | error illustration + retry |
| R4 | Pagination | bottom | full-width, 48px | Pagination | table store | hidden when 0 rows | disabled | disabled |

Rules:

- Every user-visible region must appear, including modals, drawers, and
  floating panels that belong to the page.
- Empty, loading, and error states are mandatory for data-driven regions.
  Static decoration regions may mark `N/A`.
- Position and size are approximate for layout understanding, not pixel-perfect
  specs. Use relative terms (full-width, flex-1, sidebar-width, auto).

### Component Four-Tuple Constraint

Every interactive or data-driven component on the page must declare a
four-tuple constraint:

| Component ID | ui_component | component_props | data_source | format_rule |
|---|---|---|---|---|
| C1 | ProTable | columns=[...], rowKey="id", pagination=true | `/api/leads?status=active` | status: enum→badge; amount: number→¥#,##0.00 |
| C2 | Select.Search | showSearch, filterOption=true, allowClear=true | `/api/users?role=agent` | label: `${name} (${dept})` |
| C3 | DatePicker.RangePicker | presets=[today, 7d, 30d], disabledDate=future | filter.dateRange | format: YYYY-MM-DD |
| C4 | Statistic | precision=2, prefix="¥" | dashboard.revenue | number→¥#,##0.00 |

Rules:

- `ui_component`: the design-system or library component type (ProTable,
  Select, DatePicker, Form, Modal, Drawer, Statistic, Progress, Tag, etc.).
- `component_props`: key props that affect behavior or rendering. Do not list
  every prop; list the ones that change user-visible behavior or data binding.
- `data_source`: where the data comes from (API endpoint, store key, parent
  prop, computed value). If computed, reference the Computed Metrics section.
- `format_rule`: how raw data is formatted for display (enum→badge mapping,
  number→currency, date→format string, computed→formula reference).

### Interaction Density Floor

Every primary page must meet a minimum interaction density:

| Metric | Minimum | Counting Rule |
|---|---|---|
| data-action count per page | ≥ 3 | unique data-action values on the page; navigation-only pages may be exempt with reason |
| Interaction result table rows | ≥ 1 per data-action | each row must include: trigger, actor, precondition, ui_response, modal_spec, domain_result, next_action |

Interaction result table (per page):

| trigger | actor | precondition | ui_response | modal_spec | domain_result | next_action |
|---|---|---|---|---|---|---|
| click "新增线索" | sales_rep | page loaded, has create permission | open CreateLead modal | { title: "新增线索", width: 480, fields: [name*, phone*, source*, ...] } | create lead record (status=draft) | modal closes, table refreshes |
| click "提交审核" | sales_rep | selected lead is in draft state | button disabled → show confirm dialog | { title: "确认提交审核?", type: "confirm" } | lead status: draft→pending_review | dialog closes, table refreshes, badge updates |

Rules:

- `modal_spec` must include: modal title, width (or size), and field list with
  required markers. If no modal is triggered, write `N/A`.
- `ui_response` must describe the immediate visual change before the domain
  result (button disable, spinner, highlight, toast, etc.).
- `domain_result` must describe the business state change or data operation.
- `next_action` must describe what happens after the interaction completes
  (table refresh, navigation, modal close, etc.).

## Computed Metrics Specification

Any metric or value that is computed on the frontend (aggregation, ratio,
visual proportion, derived display) must declare its compute logic explicitly.

### Compute Declaration Table

| Metric ID | Display Name | compute_expression | format_rule | source_fields | Boundary / Edge Case |
|---|---|---|---|---|---|
| MET-C01 | 漏斗金额 | `filter(deals, stage==='won').reduce((s,d)=>s+d.amount, 0)` | ¥#,##0.00 | deals[].stage, deals[].amount | empty deals → ¥0.00 |
| MET-C02 | 转化率 | `round(count(currentStage) / count(prevStage) * 100, 1)` | 0.0% | count(currentStage), count(prevStage) | prevCount=0 → display "—" |
| MET-C03 | 柱状图宽度 | `min(100, max(14, count * 22))` | CSS width: {value}% | count | count=0 → 14% (min visible); count>5 → 100% |
| MET-C04 | 进度百分比 | `round(completed / total * 100)` | {value}% | completed, total | total=0 → 0% |

Rules:

- `compute_expression`: the actual formula in pseudocode or JS expression.
  Must be unambiguous and implementable directly from the expression.
- `format_rule`: how the computed value is formatted for display (currency,
  percentage, CSS value, etc.).
- `source_fields`: the list of fields the computation depends on. Must trace
  back to FRR §5 field dictionary or API response schema.
- `Boundary / Edge Case`: what happens at extremes (zero, null, negative,
  overflow, division by zero). Must produce a defined display value, not
  `NaN` or `Infinity`.

### Visual Ratio Computation

When a metric drives a visual element (bar width, chart proportion, progress
fill, gauge), the formula must include boundary clamping:

| Visual Element | Formula | Min | Max | Unit |
|---|---|---|---|---|
| Funnel bar width | `min(100, max(14, count * 22))` | 14% | 100% | CSS % |
| Progress fill | `clamp(round(completed/total*100), 0, 100)` | 0% | 100% | CSS % |
| Gauge needle | `clamp(value, min_range, max_range)` | min_range | max_range | degrees |

Rule: a computed visual that produces `NaN`, `Infinity`, negative width, or
overflow is a P0 bug. Every visual ratio formula must state its boundary
behavior.

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
- [ ] Every primary page has a Layout Region Diagram with empty/loading/error states.
- [ ] Every interactive component has a four-tuple constraint
      (ui_component + component_props + data_source + format_rule).
- [ ] Every primary page meets interaction density floor (≥3 data-actions,
      full interaction result table rows).
- [ ] Every frontend-computed metric has a compute declaration with expression,
      format rule, source fields, and boundary behavior.
- [ ] No vague language remains without measurable behavior or owner.
