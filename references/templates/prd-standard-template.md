# L2 Standard PRD Template

Use for development handoff, bid/demo package, ToB/ToG modules, SaaS features, report products, approval workflows, and multi-surface delivery.

This is a deterministic traditional PRD template for development handoff. Its primary body is the familiar product requirement specification: background, goals/scope, users/permissions, architecture and flows, functional details, rules/data, non-functional requirements, acceptance/planning/risks. Engineering traceability and authoritative evidence are additional layers. DDD/API/Fast-Lane supplements the functional specification; it never replaces it.

The template is not complete merely because all chapter titles exist. Completeness is calculated from the release function inventory: every in-scope function must have one complete Functional Requirement Record (FRR).

## Contents

- 1. Version Information
- 1.5 Executive Summary
- 2. Change Log
- 3. Document Notes
- 3.5 Reader Navigation
- 3.6 Source Evidence Register
- 3.7 Requirement Diagnosis Anchors
- 4. Background And Opportunity
- 5. Goals, Metrics, And Scope
- 6. Users, Roles, And Permissions
- 7. Information Architecture
- 8. User Story And Role Path Matrix
- 9. Complete Module Product Specifications
- 10. Business Processes
- 10.5 E2E Cross-Module Canvas
- 11. State Machine And Button Matrix
- 12. Prototype And Interaction Contract
- 13. Engineering Traceability Contract
- 13.5 Implementation Plan And Task Backlog
- 14. Data, Metrics, And Tracking
- 15. Non-Functional Requirements
- 16. Acceptance And Readiness
- 17. Risks, Decisions, And Open Questions
- 18. Appendix

## 1. Version Information

| Field | Value |
|---|---|
| Product / Module | |
| Version | v1.0 |
| Owner | |
| Created At | |
| Reviewers | Sponsor / PM / Dev Lead / QA / Ops |
| Delivery Tier | L2 Standard Product Delivery |
| Triggered Gates | Story-Path / Demo-Closed / Development Contract / Acceptance / optional gates |

## 1.5 Executive Summary

Keep this within one screen. Write it before detailed sections so reviewers can
understand the business problem, scope, and acceptance signal without reading
the whole document.

| Field | Content |
|---|---|
| Problem | concrete user/business pain; avoid vague “improve efficiency” wording |
| Primary roles | |
| Release scope | 2-4 most important functions in this iteration |
| Out of scope | 1-3 high-expectation exclusions |
| Hard constraints | compliance, data, dependency, rollout, or deadline limits |
| Acceptance signal | measurable success indicator or launch decision signal |

## 2. Change Log

| Date | Version | Author | Change |
|---|---|---|---|
| | | | |

## 3. Document Notes

### Terms

| Term | Meaning |
|---|---|
| | |

### Related Artifacts

| Artifact | Link / Path |
|---|---|
| Prototype | |
| Flowchart | |
| Research / competitor notes | |
| Data report | |
| Metric / rule / field workbook | |
| SQL / dictionary / data contract | |
| Policy / standard | |
| Strategic Discovery Handoff | required only for new product/market, major investment, repositioning, or commercialization |

## 3.5 Reader Navigation

This table is navigation only. It must not create separate PRDs or redefine business facts.

| Reader | Required Route Through This PRD |
|---|---|
| Product / sponsor | goals -> scope -> role paths -> module specifications -> acceptance -> risks |
| Frontend | IA -> pages -> prototype contract -> state/button matrix -> function records -> acceptance |
| Backend | module specifications -> fields/rules -> commands/queries/events -> engineering traceability -> NFR |
| Algorithm / AI | AI boundary -> input/output schema -> prompt/model/eval/fallback -> function records |
| QA | role paths -> state/exception/permission matrix -> acceptance cases -> evidence |
| Architect / ops | system boundary -> data ownership -> dependencies -> readiness -> risk/rollback |

## 3.6 Source Evidence Register

Register every supplied source before writing feature details. Do not silently omit sheets, pages, rules, fields, metrics, screenshots, or prototype paths.

| Source ID | Artifact | Locator | Type | Atomic Count | Authority | Target Module | Disposition | Assertion Status | PRD / Annex / Test Trace | Conflict / Owner |
|---|---|---|---|---:|---|---|---|---|---|---|
| SRC-001 | | sheet/page/section/view/range | metric/rule/field/flow/schema/policy | | authoritative/supporting/historical | | `EMBEDDED` / `AUTHORITATIVE_ANNEX` / `DEFERRED` / `CONFLICT` / `NOT_APPLICABLE` | `VERIFIED` / `INFERRED` / `PROPOSED` / `UNKNOWN` / `CONFLICT` | | |

Assertion status rules:

- `VERIFIED`: directly proven by source, rendered prototype, database/schema, policy, or owner decision record.
- `INFERRED`: strongly implied but not directly stated; requires evidence and reviewer owner.
- `PROPOSED`: recommended by PM/AI/domain pattern; cannot be treated as accepted until owner confirms.
- `UNKNOWN`: missing evidence; blocks PASS when core behavior is affected.
- `CONFLICT`: sources disagree; blocks PASS until resolved.

Coverage summary:

| Status | Count | Pass Rule |
|---|---:|---|
| Registered atomic items | | equals the source inventory count |
| Embedded | | complete and traceable |
| Authoritative annex | | versioned, owned, and included in delivery package |
| Deferred | | reason, owner, release, and impact stated |
| Conflict | | decision owner and deadline stated |
| Silent omission | 0 | mandatory |

## 3.7 Requirement Diagnosis Anchors

Complete these anchors before detailed function records when the PRD guides
development, QA, customer demo, compliance, or workflow design.

| Anchor | Question | Decision / Rule | Owner | Status |
|---|---|---|---|---|
| Accountability / compliance | Who owns final administrative/commercial judgment? What legal, data, audit, privacy, safety, or industry red lines apply? | | | VERIFIED / PROPOSED / UNKNOWN |
| Adversarial semantics | What happens when the user enters vague, evasive, hostile, or low-information data such as “收到”, “再看”, “不知道”? | | | VERIFIED / PROPOSED / UNKNOWN |
| Offline / concurrency | What happens when multiple users operate under weak network/offline/stale data? What is the final conflict strategy? | | | VERIFIED / PROPOSED / UNKNOWN |

Anchor rule: unresolved anchors that affect core state, compliance, audit, or
write behavior block development handoff. L0 exploration may mark non-critical
anchors `N/A` with reason.

## 4. Background And Opportunity

### Strategic Discovery Handoff (Conditional)

Complete only when `strategy-discovery-handoff.md` is triggered.

| Field | Value |
|---|---|
| Decision | GO / GO_WITH_ASSUMPTIONS / VALIDATE_FIRST / NO_GO |
| Target Segment | |
| Market Size Required | Yes / No; link to TAM/SAM/SOM evidence if applicable |
| Competitive Alternatives | link / summary |
| Differentiated Outcome | |
| Riskiest Assumptions | |
| Validation Milestones | |

Do not add TAM/SAM/SOM or positioning sections to ordinary feature PRDs when the strategic gate is not triggered.

### Product / Data Current State

Current workflow:

Current data and system constraints:

### User Research / Evidence

| Source | Sample / Evidence | Key Finding |
|---|---|---|
| | | |

### Business Problem

Problem:

Impact:

Why now:

## 5. Goals, Metrics, And Scope

### Goals

| Goal | Current | Target | Window |
|---|---|---|---|
| | | | |

### Scope

In scope:

- 

Out of scope:

- 
- 
- 
- 
- 

### Complexity Budget

| Item | Count | Budget | Pass / Fail | Notes |
|---|---:|---:|---|---|
| States | | | | |
| Actions | | | | |
| APIs / Commands | | | | |
| AI Agents | | | | |

## 6. Users, Roles, And Permissions

| Role | User Goal | Main Path | Exception Path | Permission Boundary |
|---|---|---|---|---|
| | | | | |

## 7. Information Architecture

| Module | Page / View | Purpose | Main Data | Role Visibility |
|---|---|---|---|---|
| | | | | |

## 8. User Story And Role Path Matrix

| Story ID | Role | User Story | Start | Steps | Expected Visible Result | Expected Domain Result | Test Case |
|---|---|---|---|---|---|---|---|
| US-001 | | As a ..., I want ..., so that ... | | | | | TC-001 |

## 9. Complete Module Product Specifications

The summary index is not the specification itself. Complete Section 9 before writing the engineering overlay in Section 13.

| Module ID | Module | Depth | Release Scope | Detailed Section / Annex | Source IDs | Owner |
|---|---|---|---|---|---|---|
| M01 | | `FULL_SPEC` / `OVERVIEW_ONLY` | in / deferred / external | | | |

Use `FULL_SPEC` for every module planned for implementation in this release. `OVERVIEW_ONLY` is allowed only for deferred, out-of-scope, or external modules and must state owner and revisit condition.

### Mxx Business Scenario Canvas

Start each module with scenarios before field, API, DDD, or command tables.
Each scenario must let RD and QA understand `who / when / why / what / result`.

| Scenario ID | Role | When / Trigger | Goal | Main Action | Success Result | Exception To Watch | FRR IDs |
|---|---|---|---|---|---|---|---|
| SC-Mxx-01 | | | | | visible result + domain result | | Mxx-Fnn |

Scenario rules:

- Every release FRR traces to at least one business scenario, unless it is a
  system/internal function with an explicit reason.
- A scenario is not a substitute for FRR detail. It explains business context
  before the deterministic specification.

### Mxx-0 Function Inventory And Completeness Calculation

List the complete release function tree first. This table is the denominator of Gate 3A.

| Function ID | Function Name | User Outcome | Trigger / Entry | Surface / Page | Release Scope | FRR Ref | Source IDs | Test IDs |
|---|---|---|---|---|---|---|---|---|
| Mxx-F01 | | | | | in / deferred / external | Mxx-F01 | | |

Completeness calculation:

| Check | Count / Result | Pass Rule |
|---|---:|---|
| Release functions | | all functions with `Release Scope = in` |
| Complete FRRs | | equals release functions |
| Functions with complete field/annex coverage | | equals release functions requiring data |
| Functions with actions and numbered flows | | equals release functions |
| Functions with exception/recovery cases | | equals release functions |
| Functions with acceptance cases | | equals release functions |
| Silent omissions / summary-only functions | 0 | mandatory |

Do not combine independent functions under “management”, “supports X/Y/Z”, “related operations”, or “complete lifecycle”. Create separate Function IDs when the role, trigger, state change, business result, permission, aggregate/data owner, audit/NFR, or acceptance path differs. Navigation, open/close, filtering, pagination and confirmation helpers may map to an owning function only when they have no independent domain result; the action-to-function mapping must still be explicit.

### Mxx-Fnn Functional Requirement Record

Repeat this complete record for every in-scope function in the inventory.

#### 1. Identity, Purpose, And Boundary

| Field | Requirement |
|---|---|
| Function ID / Name | |
| Module / Priority / Release | |
| User and business value | |
| In scope | |
| Out of scope / deferred | |
| Authoritative source IDs | |

#### 2. Roles And Scenario

| Item | Requirement |
|---|---|
| Initiating role | |
| Collaborating / receiving role | |
| Trigger and start condition | |
| Successful exit and next action | |

#### 3. Entry And Preconditions

| Item | Requirement |
|---|---|
| Entry page / route / upstream action | |
| Role prerequisite | |
| Data and object-state prerequisite | |
| Time / organization / tenant prerequisite | |
| Feature flag / configuration / dependency prerequisite | |

#### 4. Pages, Regions, And Visible States

**New flow (when IA Skeleton and locked prototype exist):**

- State the IA Skeleton `view_id` and prototype `data-testid` this function uses.
- Describe only business-visible differences by role/state. Do not rewrite layout,
  pixel sizes, or component props.

| IA Skeleton view | Prototype data-testid | Business-visible state differences |
|---|---|---|
| Mxx-V01 | page-mxx-list | admin sees batch toolbar; normal user does not |
| Mxx-V02 | modal-mxx-create | disabled when user lacks `mxx:create` permission |

**Fallback (when no prototype exists):**

| Page / Region | Purpose | Entry | Main Content | Loading | Empty | Error / Disabled | Exit |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

#### 5. Fields, Dictionaries, And Validation

**New flow (when global field dictionary and locked prototype exist):**

- Reference the global entity field dictionary for common fields.
- In this FRR, list only fields whose meaning, validation, enum, masking, or
  editability is business-critical or differs by role/state in this function.

| Field | Business meaning | Special rule for this function |
|---|---|---|
| lead.source | 来源 | 代理商录入时强制为"代理商"并锁定 partnerId |
| lead.intent | 意向度 | 新建时必填，影响分配优先级 |

**Fallback (when no field dictionary exists):**

List every user-entered, displayed, exported, matched, calculated, signed, uploaded, filtered, or state-driving field. A complete authoritative annex may replace the rows only when its source ID, version, owner, range, count, and usage rule are declared here.

##### 5.1 Global Entity Field Dictionary

One table per entity, covering every field across all sub-pages (list, create, edit, detail, filter).

| # | field_name | label | type | required | constraints | enum / dictionary | read_only | system_filled | validation_rule |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | lead.name | 线索名称 | string(100) | yes | max 100 chars | N/A | no | no | non-empty, no special chars |
| 2 | lead.source | 线索来源 | enum | yes | single-select | [广告, 介绍, 主动咨询, 展会, 其他] | no | no | must be in enum |
| 3 | lead.status | 状态 | enum | no | system-managed | [draft, pending_review, approved, rejected] | yes | yes | set by state machine |
| 4 | lead.amount | 预计金额 | decimal(12,2) | no | ≥0 | N/A | no | no | numeric, 2 decimal places |

##### 5.2 Per-Sub-Page Field List

Each sub-page (list view, create modal, edit modal, detail drawer, filter bar)
has its own field list with positional information.

**List View Fields:**

| # | Row | Col | field_name | label | component_type | required | special_behavior |
|---:|---|---|---|---|---|---|---|
| 1 | 1 | 1 | lead.name | 线索名称 | Text(Link) | N/A | click → open detail drawer |
| 2 | 1 | 2 | lead.source | 来源 | Tag(badge) | N/A | color by source enum |
| 3 | 1 | 3 | lead.status | 状态 | Badge | N/A | color by status enum |
| 4 | 1 | 4 | lead.amount | 预计金额 | Text(currency) | N/A | format: ¥#,##0.00 |
| 5 | 1 | 5 | lead.assignee | 负责人 | Text | N/A | show avatar + name |
| 6 | 1 | 6 | actions | 操作 | Button.Group | N/A | edit / submit / delete by state |

**Create Modal Fields:**

| # | Row | Col | field_name | label | component_type | required | special_behavior |
|---:|---|---|---|---|---|---|---|
| 1 | 1 | 1 | lead.name | 线索名称 | Input | yes | max 100 chars |
| 2 | 1 | 2 | lead.source | 线索来源 | Select | yes | single-select from enum |
| 3 | 2 | 1 | lead.contactPhone | 联系电话 | Input | no | format: mobile or landline |
| 4 | 2 | 2 | lead.contactName | 联系人 | Input | no | max 20 chars |
| 5 | 3 | 1 | lead.amount | 预计金额 | InputNumber | no | min=0, precision=2 |
| 6 | 3 | 2 | lead.expectedDate | 预计成交日 | DatePicker | no | disable past dates |

**Edit Modal Fields:**

| # | Row | Col | field_name | label | component_type | required | special_behavior |
|---:|---|---|---|---|---|---|---|
| 1 | 1 | 1 | lead.name | 线索名称 | Input | yes | same as create |
| 2 | 1 | 2 | lead.source | 线索来源 | Select | yes | same as create |
| 3 | 2 | 1 | lead.amount | 预计金额 | InputNumber | no | same as create |
| 4 | — | — | lead.status | 状态 | Badge(display) | N/A | **disabled in edit** (system-managed) |
| 5 | — | — | lead.source | 线索来源 | Select | yes | **来源不可改** (read-only after creation) |

**Detail Drawer Fields:**

| # | Section | field_name | label | component_type | special_behavior |
|---:|---|---|---|---|---|
| 1 | 基础信息 | lead.name | 线索名称 | Text | N/A |
| 2 | 基础信息 | lead.source | 来源 | Tag | color by enum |
| 3 | 基础信息 | lead.status | 状态 | Badge | color by status enum |
| 4 | 联系信息 | lead.contactPhone | 联系电话 | Text | masked by permission (see §10) |
| 5 | 财务信息 | lead.amount | 预计金额 | Text(currency) | ¥#,##0.00 |

##### 5.3 Component Type Binding Rules

When a field's data type is known, the component type is determined by the
following binding rules. Deviations must be justified.

| Data Type | Component Type | Notes |
|---|---|---|
| enum (single-select) | Select | dropdown with all enum values |
| enum (multi-select) | Checkbox.Group | all enum values as checkboxes |
| ref (foreign key) | Select.Search | searchable dropdown, label = display field of referenced entity |
| date | DatePicker | calendar picker, format: YYYY-MM-DD |
| datetime | DatePicker.ShowTime | calendar + time picker, format: YYYY-MM-DD HH:mm |
| date range | DatePicker.RangePicker | two linked pickers |
| number (integer) | InputNumber | step=1, precision=0 |
| number (decimal) | InputNumber | precision=decimal places |
| money | InputNumber | prefix="¥", precision=2 |
| string (short) | Input | text input with max length |
| string (long) | Input.TextArea | textarea with max length and optional char count |
| boolean | Switch | toggle switch |
| computed | Text(display) | read-only display, see Computed Metrics section |
| file/image | Upload | file picker with type/size validation |
| tag/category | Tag.Select | tag selector with predefined categories |

##### 5.4 Tree / Recursive Component Specification

When a page contains a tree component (org chart, menu management, category
tree, permission tree), the FRR must specify the data structure and rendering
rules.

| Property | Required Content |
|---|---|
| Data structure | `{ id, parentId, name, level, children: [], sortOrder, enabled }` |
| Root identification | parentId = null or parentId = 0 (state which) |
| Node display | icon + name + optional badge (count, status) |
| Expand behavior | default expanded / collapsed; lazy load children or preload all |
| Selection mode | single-select (highlight) / multi-select (checkbox) / none (display only) |
| Cascade selection | parent checks → all children check; parent unchecks → all children uncheck; child unchecks → parent becomes indeterminate; **exclude self and descendants when selecting** |
| Drag reorder | allowed / not allowed; if allowed, see §6.2 Drag-Drop spec |
| Empty tree | "暂无数据" illustration + create button |
| Loading | skeleton tree or spinner |
| Max depth | unlimited or state limit; behavior when limit reached |

##### 5.5 Metric Status Color Mapping

When a page displays metrics with status-based coloring (normal, warning,
danger, success), the FRR must declare the explicit mapping.

| state_value | css_class | color_token | hex | display_label | condition |
|---|---|---|---|---|---|
| normal | .status-normal | var(--brand) | #e8f1ff | 正常 | value ≤ threshold_warn |
| warning | .status-warning | var(--warn) | #fff3df | 预警 | threshold_warn < value ≤ threshold_danger |
| danger | .status-danger | var(--danger) | #ffe9e6 | 危险 | value > threshold_danger |
| success | .status-success | var(--ok) | #e7f7ed | 达标 | value ≥ target |
| neutral | .status-neutral | var(--neutral) | #f5f5f5 | 未开始 | value is null or 0 |

Rules:

- Every status badge, tag, or colored indicator must have a row in this table.
- `css_class` must be the actual class name used in the prototype.
- `color_token` must reference the design-system token, not a raw hex value.
- `hex` is provided for reference and verification.
- The condition must use the actual field name and threshold values from §8
  Business Rules, not vague terms like "high" or "low".
- If a state value is computed, reference the Computed Metrics section for the
  formula.

#### 6. Numbered Interaction Flow

Write one observable user-system exchange per step. Do not use a one-line summary such as “supports add, edit, delete, export”.

| Step | Actor | Preconditions | User Action / System Trigger | System Validation And Processing | Visible Result | Domain Result | Next Action |
|---:|---|---|---|---|---|---|---|
| 1 | | | | | | | |

#### 6.1 Modal Chain Specification

When a single user action can trigger a chain of modals (showModal → showModal),
or when an action has conditional branches that open different modals, the FRR
must describe the complete modal chain.

Branch condition chain:

| Branch ID | Trigger Action | Branch Condition | Target Modal | Branch Type |
|---|---|---|---|---|
| BC-01 | click "提交" | form has unsaved required fields | ValidationModal ("请填写必填项") | interception |
| BC-02 | click "提交" | form valid + has conflicting data | ConflictResolveModal ("检测到重复记录") | interception |
| BC-03 | click "提交" | form valid + no conflict | ConfirmSubmitModal ("确认提交?") | confirmation |
| BC-04 | confirm in ConfirmSubmitModal | server returns success | SuccessModal ("提交成功") | result |
| BC-05 | confirm in ConfirmSubmitModal | server returns error | ErrorModal ("提交失败: " + reason) | error |

Interception modal four elements:

| Element | Required Content |
|---|---|
| Trigger condition | what data or state triggers this modal (e.g., "required field empty", "duplicate record detected", "permission denied") |
| Education content | what the modal tells the user (e.g., "您有3个必填项未填写", "检测到同名客户已存在") |
| Guide action | what button(s) the modal offers and what each does (e.g., "去填写" → scroll to first empty field; "查看重复" → open duplicate record drawer) |
| Return path | what happens after the modal closes (e.g., "返回表单保持当前输入", "跳转到重复记录详情页") |

Rules:

- When the prototype has `showModal()` called inside another `showModal()`
  callback, or when a modal's confirm button opens another modal, the FRR must
  describe the full chain.
- Interception modals (validation, conflict, permission) must state all four
  elements. Confirmation modals ("确认提交?") may omit education content.
- Branch conditions must be mutually exclusive and collectively exhaustive for
  the trigger action.
- If a branch leads to a dead-end (no next action), mark it as `BLOCKED` and
  state the recovery path.

#### 6.2 Drag-Drop Interaction Specification

When a page contains drag-and-drop interactions (kanban reordering, task
assignment, file upload, list reordering), the FRR must describe the complete
drag-drop lifecycle.

Five-event specification:

| Event | Trigger | Visual Feedback | Data Operation | Failure Rollback |
|---|---|---|---|---|
| dragstart | user picks up draggable item | item gains opacity:0.5 + drag shadow; drop zones highlight with dashed border | record dragItem = { id, sourceColumn, sourceIndex } | N/A |
| dragover | dragged item hovers over a drop zone | drop zone shows insertion indicator (line or placeholder) | preventDefault to allow drop | N/A |
| dragleave | dragged item leaves drop zone | drop zone removes highlight/insertion indicator | clear drop zone hover state | N/A |
| drop | user releases item on a drop zone | item animates into new position; source and target columns update | update item position: { sourceColumn, sourceIndex } → { targetColumn, targetIndex }; persist via API | if API fails: revert item to original position + toast "移动失败" |
| dragend | drag completes (after drop or cancel) | all drag styling removed; drag shadow destroyed | clear dragItem state | if drop failed and rollback occurred, ensure UI matches persisted state |

Rules:

- All five events must be described. If any event has no visual feedback or data
  operation, state `N/A` explicitly.
- Failure rollback must specify: what the user sees (toast, animation, revert),
  what data is restored (original position, order), and whether retry is
  automatic or manual.
- For cross-column drag (kanban), state whether the API call is optimistic
  (update UI first, rollback on failure) or pessimistic (wait for API success
  before updating UI).
- For file drag-upload, describe file type/size validation on drop and the
  upload progress indicator.

#### 6.3 Dynamic Form Row And Form Cascade

When a form contains dynamic add/remove rows or cascade select dependencies,
the FRR must describe the complete behavior.

Dynamic form row specification:

| Property | Required Content |
|---|---|
| Add trigger | what button or action adds a row (e.g., click "+ 添加明细") |
| Remove trigger | what removes a row (e.g., click trash icon on each row); whether removal is allowed when only 1 row remains |
| Row data structure | fields in each row with type, required, default, validation |
| Auto-calculation | any field in the row that is computed from other fields (e.g., row subtotal = qty × price) |
| Row validation | per-row validation rules and error display (inline or on submit) |
| Max rows | maximum row count if limited; behavior when limit reached (disable add button + toast) |
| Initial rows | how many rows exist when form opens (0 or 1) |

Form cascade specification:

| Cascade ID | Trigger Field | Trigger Condition | Affected Field | Cascade Action | Clear Rule |
|---|---|---|---|---|---|
| CAS-01 | 工单类型 (ticketType) | value changes | 处理人 (assignee) | reload assignee options filtered by ticketType | clear current assignee value |
| CAS-02 | 客户名称 (customerId) | value changes | 联系人 (contactId) | reload contacts filtered by customerId | clear current contact value |
| CAS-03 | 省份 (province) | value changes | 市 (city) | reload city options filtered by province | clear current city value |

Rules:

- Clear rule must specify whether the cascade clears the affected field value,
  clears all dependent fields (downstream cascade), or preserves the value
  with a warning.
- If the cascade API call fails, state whether the affected field is disabled,
  shows stale options, or shows an error.
- For multi-level cascade (A→B→C), describe each level separately with its own
  cascade ID.

#### 7. Actions And Operation Rules

| Action ID | Page / State | Role | Trigger | Confirmation / Guard | Visible Result | Domain Result | Idempotency / Duplicate Rule | Next Action |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

#### 8. Business Rules, Calculations, And Calibers

| Rule ID | Applies To | Deterministic Rule / Formula / Threshold | Priority | Time / Effective Version | Evidence Source | Conflict / Exception Behavior |
|---|---|---|---|---|---|---|
| | | | | | | |

#### 9. State, Button, And Lifecycle Behavior

| Object | State | Visible Actions | Forbidden Actions | Guard | Trigger -> Next State | Visible Result | Event / Audit |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

#### 10. Permissions And Data Scope

| Role | Tenant / Org / Region / Enterprise Scope | Row Scope | Field Scope | Action Scope | Override / Approval | Unauthorized Behavior |
|---|---|---|---|---|---|---|
| | | | | | | |

#### 11. Exceptions, Fallback, And Recovery

| Exception ID | Case | Detection | User Feedback | Data Preservation | Allowed Recovery / Retry | Domain / Audit Result | Owner |
|---|---|---|---|---|---|---|---|
| | validation / empty / duplicate / stale / conflict / permission / timeout / dependency / partial failure | | | | | | |

#### 12. Notifications, Audit, And Dependencies

| Type | Trigger | Recipient / Dependency | Channel / Interface | Contents / Contract | Failure Behavior | Audit / Owner |
|---|---|---|---|---|---|---|
| notification / audit / upstream / downstream | | | | | | |

#### 13. Data, AI, And Algorithm Contract

Complete when the function includes recognition, recommendation, generation, scoring, semantic retrieval, configurable rules, statistical transformation, or other algorithmic processing. Otherwise write `N/A - deterministic CRUD/query with no algorithmic decision`.

| Item | Requirement |
|---|---|
| Input schema and source | |
| Output schema and downstream consumer | |
| Deterministic code/rule responsibility | |
| Model/prompt/retrieval responsibility | |
| Confidence, threshold, and human confirmation | |
| Model/prompt/rule/schema version | |
| Timeout, failure, fallback, and prohibited writes | |
| Golden/evaluation cases and pass threshold | |

For coding-agent handoff, add one of the following machine-readable blocks when
AI or algorithmic behavior exists. Keep the table above for human reviewers.
Use `ai_contract_lite` by default for L2 AI-supporting features. Upgrade to
full `ai_runtime_contract` only when AI writes consequential state, calls
side-effect tools, requires runtime rollback/eval/on-call, or affects
compliance, safety, money, legal, or customer acceptance.

```yaml
ai_contract_lite:
  model: ""
  prompt_file: ""
  write_scope: none
  human_gate: required_before_publish
  fallback: ""
  feature_flag: ""
```

For AI-core modules, use full `ai_runtime_contract`; see
`references/coding-agent-compat.md`.

#### 14. Function-Level NFR

| Category | Requirement | Measurement / Acceptance |
|---|---|---|
| performance / security / privacy / accessibility / compatibility / operations | | |

#### 15. Frontend / Backend / QA Handoff Notes

| Role | Required Notes |
|---|---|
| Frontend | component states, disabled/hidden/highlight behavior, modal/toast/copy, loading/empty/error, responsive/interaction notes |
| Backend | source of truth, validation owner, permission/data-scope guard, state transition, idempotency, audit/event, dependency failure behavior |
| QA | priority happy path, boundary values, permission/overreach cases, state conflict, weak network, regression path |

This table points readers to the detailed FRR, state matrix, prototype contract,
and acceptance IDs. It does not create a second source of truth.

#### 16. Acceptance And Traceability

At minimum include happy, validation, permission, state-conflict, dependency-failure, and regression cases when applicable.

| Acceptance ID | Case | Preconditions / Data | Steps | Expected UI Result | Expected Domain Result | Prototype / Test | Source IDs |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

For coding-agent handoff, add this optional block immediately after the table.
It is additive and does not replace human-readable acceptance.

```yaml
ac_structured:
  - id: AC-Mxx-Fxx-001
    frr_ref: Mxx-Fxx
    type: happy_path
    priority: P0
    status: active
    revision: 1
    given: ""
    when: ""
    then:
      ui: ""
      domain: ""
      sla: ""
    test_type: integration
    data_testid: ""
    data_action: ""
    skip_reason: null
```

FRR completion rules:

- Every numbered section 1-16 must contain concrete content or `N/A + reason`.
- “见原型”, “见附件”, “按现有逻辑”, “同上”, “支持相关操作”, and a screenshot without behavior mapping are incomplete.
- Enum/dictionary values must be fully listed or mapped to a frozen authoritative annex range.
- A source annex may carry atomic fields/rules/metrics, but interaction flow, permissions, exception behavior, and acceptance stay in the FRR.
- `FULL_SPEC` is allowed only after the completeness calculation passes.

### Mxx Shared Module Contracts

Use the following A-L structure only for contracts genuinely shared by several FRRs. Do not use it to replace FRRs.

### Mxx Module Name

#### A. Purpose And Boundary

- User/business outcome:
- In scope:
- Explicitly deferred / external:
- Entry and exit conditions:
- Authoritative source IDs:

#### B. Roles, Scenarios, And Paths

| Scenario ID | Role | Start | Steps | Exit / Next Action | Visible Result | Domain Result |
|---|---|---|---|---|---|---|
| | | | | | | |

#### C. Pages And Views

| Page / View | Entry | Purpose | Main Regions | Empty / Loading / Error | Exit |
|---|---|---|---|---|---|
| | | | | | |

#### D. Fields And Dictionaries

| Field ID | Page / Object | Label / Meaning | Type | Required / Default | Source | Validation / Dictionary | Editable By | Display / Masking |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

If a source workbook/SQL dictionary contains a large complete field set, keep it as a versioned authoritative annex and map its item count and range here. Do not replace it with examples.

#### E. Actions And Interactions

| Action ID | Page / State | Role | Trigger | Preconditions / Confirmation | Visible Result | Domain Result | Next Action |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

#### F. Business Rules, Calculations, And Calibers

| Rule ID | Applies To | Rule / Formula / Caliber | Priority | Effective Range | Evidence Source | Conflict / Exception |
|---|---|---|---|---|---|---|
| | | | | | | |

#### G. State-Button Matrix

| Object | State | Visible Actions | Forbidden Actions | Guard | Transition / Event / Audit |
|---|---|---|---|---|---|
| | | | | | |

#### H. Permissions And Data Scope

| Role | Org / Tenant / Region Scope | Row Scope | Field Scope | Action Scope | Override / Approval |
|---|---|---|---|---|---|
| | | | | | |

#### I. Exceptions And Fallback

| Case | Detection | User Feedback | Allowed Recovery | Domain / Audit Result | Owner |
|---|---|---|---|---|---|
| validation / duplicate / conflict / stale / permission / timeout / partial failure | | | | | |

#### J. Cross-Module And External Contracts

| Dependency | Direction | Source Of Truth | Sync / Trigger | Failure Behavior | Owner |
|---|---|---|---|---|---|
| | | | | | |

#### K. Data, Metrics, AI, Audit, And NFR

Include only applicable contracts, but make each one specific and testable.

#### L. Acceptance And Traceability

| Acceptance ID | Story / Rule | Preconditions | Steps | Expected UI Result | Expected Domain Result | Prototype / Test | Source IDs |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

Product-spec rules:

- describe what, why, and complete observable business behavior;
- include enough fields, rules, states, interactions, exceptions, permissions, and acceptance for development and QA to proceed without guessing;
- avoid framework choices and physical database design unless they are explicit business contracts;
- when detail exceeds the master document budget, split by bounded module or authoritative annex. Never summarize away atomic requirements.

## 10. Business Processes

```text
trigger -> validation -> processing -> state change -> notification/report/audit -> next action
```

| Process | Trigger | Guard | Action | Result | Audit / Event |
|---|---|---|---|---|---|
| | | | | | |

## 10.5 E2E Cross-Module Canvas

Required when workflow state crosses modules, services, tenants, reports,
notifications, approvals, imports, payments, or audits. Mark `N/A` only for
isolated modules without cross-module lifecycle.

| E2E ID | Upstream Module / Object | Source State -> Target State | Domain Event | Downstream Module / Object | Downstream State Flow | Owner / Transaction Boundary | Failure / Compensation | Acceptance |
|---|---|---|---|---|---|---|---|---|
| E2E-001 | | | | | | | | AC-E2E-LONG-RUNNING-001 |

Rules:

- Each row must be convertible into an integration or E2E regression case.
- Event payload version, idempotency key, ordering/replay behavior, and
  dead-letter owner must be defined for async rows.
- Do not use this canvas to invent artificial workflow complexity for a simple
  single-module CRUD feature.

## 11. State Machine And Button Matrix

| Object | State | Visible Actions | Forbidden Actions | Guard | Result Event |
|---|---|---|---|---|---|
| | | | | | |

State transition:

```yaml
transition:
  from:
  to:
  trigger:
  guard:
  action:
  event:
```

## 12. Prototype And Interaction Contract

Prototype path:

| Screen | data-testid | data-action | data-state / data-api | Expected Result |
|---|---|---|---|---|
| | | | | |

Demo paths:

| Path | Role | Steps | Pass Rule |
|---|---|---|---|
| Happy path | | | |
| Permission path | | | |
| Error / empty path | | | |

## 13. Engineering Traceability Contract

Complete this after Section 9. It maps product behavior into implementation entry points; it is not a substitute for the module specification.

| Module | Inputs | Outputs | Processing | Domain Object | Commands / Queries | Test Cases |
|---|---|---|---|---|---|---|
| | | | | | | |

Invariants:

- 

Domain events:

- 

Backend closure checklist for each write command:

| Function ID | Aggregate / Owner | Command Input / Output | Expected Version / Concurrency | Idempotency Key | Transaction / Saga Boundary | Persisted Result | Domain Event | Audit Fields | Retry / Reconciliation |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## 13.5 Implementation Plan And Task Backlog

Complete this only when the PRD will enter development planning, AI coding, or
issue assignment. It is a downstream execution map, not a second source of
requirements.

### Implementation Assumptions

| Area | Assumption / Decision | Evidence / Owner | Risk If Wrong |
|---|---|---|---|
| architecture / dependency / data / migration / release | | | |

### Vertical Slice Backlog

Each task must deliver a verifiable user-visible or domain result. Avoid pure
horizontal tickets such as "build database layer" unless they are explicit
prefactoring tasks and unblock a vertical slice.

| Task ID | Slice / Outcome | Source FRR | Acceptance IDs | Owner Role | Depends On | Files / Modules Likely Touched | Test / Evidence | Done Signal |
|---|---|---|---|---|---|---|---|---|
| TASK-001 | | Mxx-Fnn | AC-... | frontend/backend/algorithm/QA | none / TASK-... | optional if known | | demoable path / passing test |

Task rules:

- No task without `Source FRR` and `Acceptance IDs`, unless it is a named
  prefactoring, migration, or environment task with a clear blocker reason.
- Split by independently testable workflow/result, not by organization chart.
- If a task depends on an unresolved business rule, field dictionary, permission
  decision, source system, or external integration, mark it `BLOCKED`.

## 14. Data, Metrics, And Tracking

### Business Data

| Field / Object | Meaning | Source | Owner | Validation |
|---|---|---|---|---|
| | | | | |

### Metrics / Reports

| Metric ID | Metric | Formula / Caliber | Dimension | Baseline | Target | Refresh | Usage / Owner |
|---|---|---|---|---|---|---|---|
| MET-001 | | | | | | | |

### Event Tracking

| Event ID | Event Name | Trigger Moment | Required Params | Purpose | Privacy / Masking |
|---|---|---|---|---|---|
| EVT-001 | | button clicked / state changed / task completed | user_id, role, tenant_id, object_id, status | | |

Tracking rules:

- Add events only when they support operation, conversion, risk monitoring,
  compliance, or product improvement.
- For AI features, include prompt/model/rule version, confidence bucket,
  fallback reason, human confirmation, and final outcome when applicable.
- Sensitive identifiers must be masked, hashed, or omitted according to privacy
  requirements.

## 15. Non-Functional Requirements

| Category | Requirement | Acceptance |
|---|---|---|
| Performance | | |
| Security / Privacy | | |
| Audit | | |
| Compatibility | | |
| Accessibility | | |
| Operations | | |

## 16. Acceptance And Readiness

| Gate | Result | Evidence |
|---|---|---|
| Gate 1 Story-Path | PASS / FAIL | |
| Gate 2 Demo-Closed Prototype | PASS / FAIL | |
| Gate 3A Product Specification Completeness | PASS / FAIL | source coverage + full module specs |
| Gate 3B Engineering Traceability Contract | PASS / FAIL | DDD/Fast-Lane/API/test trace |
| Gate 4 Acceptance Package | PASS / FAIL | |
| System Readiness | PASS / FAIL / N/A | |

## 17. Risks, Decisions, And Open Questions

| Type | Item | Owner | Deadline | Decision / Mitigation |
|---|---|---|---|---|
| Risk | | | | |
| Decision | | | | |
| Question | | | | |

## 18. Appendix

- Research report:
- Competitor analysis:
- Data analysis:
- Design files:
- Test report:
