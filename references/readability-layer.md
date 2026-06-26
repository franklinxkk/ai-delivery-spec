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
- Page Layout And Component Constraint
- Computed Metrics Specification
- Visual Hierarchy And Language Rules
- Output Language Rules
- Module Self-Contained Organization (Optional)
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

When the IA Skeleton is locked (Stage 3.5), reference `region_id` from the
skeleton and do not create parallel region IDs. Still add the layout,
component, data-source, empty/loading/error, and conditional-visibility
constraints needed by frontend and QA. Only create new region rows when the
locked skeleton lacks a modal-only region, conditional panel, or post-lock
accepted addition.

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

## Output Language Rules

### Core Rule

Use the prompting user's spoken language for all document content, regardless
of the AI assistant's default or training language. Technical terminology that
has no established translation or is universally recognized in its English form
may remain in English.

### What Must Be In The User's Language

- Chapter and section headers
- Business scenario descriptions
- Field names, field descriptions, and field validation rules
- Interaction flow narratives (what happens when a user clicks X)
- Business rules, calculations, and caliber descriptions
- Acceptance criteria narrative text
- Error messages, empty states, loading states, confirmation dialogs
- Permission descriptions
- Non-functional requirement descriptions

### What Stays In English

- Technical keywords that serve as identifiers or tooling hooks:
  `data-action`, `data-testid`, `FRR`, `AC`, `API`, `RBAC`, `E2E`, `SSE`,
  `SLA`, `SSO`, `LDAP`, `JSON`, `YAML`, `CSS`, `HTML`
- Standard architectural terms when no well-known local equivalent exists:
  `Layout Region Diagram`, `Component Four-Tuple`, `Interaction Density
  Floor`, `Modal Chain Spec`, `Computed Metrics`, `State Machine`,
  `idempotency key`
- Code or command references, identifiers, API paths, field IDs, status codes
- Tables where column headers are standard technical terms (e.g. `FRR ID`,
  `data-action`, `component_props`, `compute_expression`)
- Fenced code blocks (schema, API contract, YAML, SQL, AGENTS.md stubs)

### Chapter Header Translation Table

When generating a PRD from the L2 Standard template, translate these chapter
headers to the user's language. Below is the Chinese mapping; for other
languages, apply the equivalent translation.

| English (Template) | Chinese |
|---|---|
| Version Information | 版本信息 |
| Executive Summary | 执行摘要 |
| Change Log | 变更记录 |
| Background And Opportunity | 背景与机会 |
| Goals, Metrics, And Scope | 目标、指标与范围 |
| Users, Roles, And Permissions | 用户、角色与权限 |
| Information Architecture | 信息架构 |
| Complete Module Product Specifications | 完整模块产品规格 |
| Business Processes | 业务流程 |
| E2E Cross-Module Canvas | E2E跨模块链路画布 |
| State Machine And Button Matrix | 状态机与按钮矩阵 |
| Prototype And Interaction Contract | 原型与交互契约 |
| Engineering Traceability Contract | 工程追溯契约 |
| Data, Metrics, And Tracking | 数据、指标与追踪 |
| Non-Functional Requirements | 非功能需求 |
| Acceptance And Readiness | 验收与就绪 |
| Risks, Decisions, And Open Questions | 风险、决策与待解问题 |
| Appendix | 附录 |

FRR section headers within a module also translate:

| English (FRR section) | Chinese |
|---|---|
| Identity, Purpose, And Boundary | 身份、目的与边界 |
| Entry And Preconditions | 入口与前置条件 |
| Pages, Regions, And Visible States | 页面、区域与可见状态 |
| Fields, Dictionaries, And Validation | 字段、字典与校验 |
| Numbered Interaction Flow | 编号交互流程 |
| Actions And Operation Rules | 操作与规则 |
| Business Rules, Calculations, And Calibers | 业务规则、计算与口径 |
| State, Button, And Lifecycle Behavior | 状态、按钮与生命周期行为 |
| Permissions And Data Scope | 权限与数据范围 |
| Business Scenario Canvas | 业务场景画布 |
| Three-Layer Permission Model | 三层权限模型 |

### Verification

Before marking a PRD as `PASS`, run a language check:

- Count total content lines and lines that are >80% English characters.
- Accept if the English-heavy ratio is below 20% (explainable by code blocks,
  table headers, and technical terms).
- If >30% English-heavy ratio, flag as `LANGUAGE_GAP` and rewrite.

## Module Self-Contained Organization (Optional)

When the PRD has many modules (>=5) and readers complain about jumping between
sections, use the Module Self-Contained mode. This is an optional layout that
reorganizes the standard template so each module is a complete vertical slice.

### When To Use

- PRD has >=5 modules with independent development teams
- Readers (PM, frontend, backend, QA) each focus on specific modules
- The standard template's cross-cutting H2 sections cause navigation friction
- User or sponsor explicitly requests module-first organization

### When NOT To Use

- PRD has <=3 modules (overhead exceeds benefit)
- Modules share heavy cross-cutting contracts (shared state machines,
  cross-module workflows, shared field dictionaries)
- The PRD is a bid/demo document where reviewers read linearly

### Structure

Replace the standard cross-cutting H2 layout with this module-first structure:

```markdown
# PRD Title

## Version Information
## Executive Summary
## Background And Opportunity
## Goals, Metrics, And Scope
## Users, Roles, And Permissions
## Information Architecture (global only)

## Module M01: [Module Name]
### Module Overview
  (scenario table, in/out scope, module-level metrics)
### Function Records
  (FRR §1-§16 per function, self-contained)
### Module State Machine
  (state-button matrix for this module only)
### Module Business Rules
  (numbered rules, calibers, formulas)
### Module Acceptance
  (happy path, boundary, permission, state conflict, regression)
### Frontend/Backend/QA Handoff
  (component notes, API ownership, test priorities)

## Module M02: [Module Name]
  (same structure)

## Cross-Module Canvas
  (E2E workflows that span modules)
## Engineering Traceability Contract
  (global RBAC, shared API contracts, shared data schemas)
## Non-Functional Requirements
## Risks, Decisions, And Open Questions
## Appendix
```

### Rules

- Each module section must contain ALL FRR records for that module.
  Do not split a module's functions across different H2 sections.
- Cross-cutting contracts (global RBAC, shared data schemas, E2E workflows)
  remain in dedicated sections after all modules.
- The Information Architecture section covers global navigation and IA only;
  per-module page layout lives inside the module section.
- Global metrics (cross-module KPIs) stay in the Goals section; per-module
  metrics stay in the module's Module Overview.
- The Executive Summary and Background sections remain global.
- When using this mode, add `Organization: Module-Self-Contained` to the
  version information table so reviewers know the layout convention.

### Trade-offs

| Standard Layout | Module Self-Contained |
|---|---|
| Cross-cutting sections group all state machines, all rules, all acceptance | Each module is a vertical slice; reader stays in one section |
| Easier to compare same-type artifacts across modules | Easier to hand a module to a team |
| Risk: reader jumps between H2 sections | Risk: cross-cutting patterns duplicated or inconsistent |
| Good for: bid docs, review boards, linear reading | Good for: multi-team delivery, coding agent handoff |

When using Module Self-Contained mode, add a cross-module consistency check to
the Readability Acceptance Checklist to catch duplicated or inconsistent
contracts.

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
- [ ] Language check: English-heavy lines ≤ 20% of total content lines.
- [ ] If Module Self-Contained mode is used, cross-module consistency check
      passed (no duplicated contracts, consistent state definitions, shared
      fields traced to a single source).
