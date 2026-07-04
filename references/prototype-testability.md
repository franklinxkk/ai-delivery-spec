# Prototype + Testability

Use this file when generating, reviewing, or repairing an HTML prototype.

## Contents

- Prototype From IA Skeleton
- Five-Layer Test Annotation
- Command and State Annotations
- State-Driven UI Iron Law
- Interaction Completeness Gate
- Dynamic Surface Scan Gate
- Assertion Modes
- Multi-Step Forms
- Batch Operations
- Scenario Test Template
- Verification Loop
- Test State Self-Healing / Shadow-Data Isolation
- Prototype Helper Contract
- Prototype Design Process
- Visual Design Rules
- Presentation Mode Specification
- Prototype Acceptance Checklist

## Prototype From IA Skeleton

Before drawing any HTML, load the IA Skeleton produced in `delivery-core.md`
Stage 3.5. The prototype is a pixel-level realization of the locked skeleton,
not a new design exploration.

### Translation rules

| IA Skeleton element | Prototype output |
|---|---|
| `module_id` + `module_name` | One top-level navigation group or landing section |
| `views[].view_id` | One HTML page, drawer, or modal root with matching `data-testid="page-{view_id}"` |
| `views[].view_type` | `page` → full route; `modal` → modal container; `drawer` → side drawer |
| `views[].entry_path` | Route/URL shown in prototype address bar or navigation link |
| `regions[].region_id` | Container `div` with `data-testid="region-{region_id}"` |
| `regions[].components` | Placeholder components with realistic sample data and labels |
| `regions[].visible_to` | Conditional rendering attribute `data-visible-role="role"` |
| `primary_actions[]` | Buttons/links with `data-action="{action_id}"` and target view/modal |
| `related_views` | Navigation links, breadcrumbs, or cross-view action targets |

### Constraints

1. **No new views without IA Skeleton update**: if a missing view is discovered
   during prototyping, update the IA Skeleton and re-confirm before adding it to
   the HTML. Do not silently expand scope.
2. **No new primary roles**: role-specific regions must match the IA Skeleton
   `primary_roles`. Additional roles require skeleton revision.
3. **Modal chain from views**: every `view_type: modal` or `drawer` must be
   reachable from at least one `page` view via a `data-action` annotated
   element.
4. **Prototype lock statement**: when the prototype is complete, output
   ```
   [PROTOTYPE LOCK] view_count=N, modal_count=M, action_count=A, state_count=S
   Gaps against IA Skeleton: <list or NONE>
   ```
   Do not proceed to PRD detail until locked or gaps accepted.

### From prototype to PRD

After locking the prototype:

1. Run `scripts/extract_interaction_ledger.py` to produce
   `interaction-ledger.json`.
2. The PRD's FRR §4-§6 reference the prototype by `view_id`, `region_id`,
   `data-testid`, `data-action`, and modal/drawer IDs, then normalize the page
   layout, visible states, field behavior, and action-to-domain flow into a
   human-readable implementation specification. "See prototype" is not enough.
3. Any business rule, state transition, permission, or exception that is not
   visible in the prototype must still be fully specified in the PRD.

## Five-Layer Test Annotation

Every verifiable element should expose identity, expected value, rule, scenario, and assertion.

```html
<div
  data-testid="account-status-badge"
  data-expected="待复核"
  data-rule="关键字段缺失 -> 待复核"
  data-test-scenario="status-review"
  data-assert="{mode:'exact',value:'待复核'}"
>
  <span class="status-badge status-review">待复核</span>
</div>
```

Attributes:

| Attribute | Required | Purpose |
|-----------|:---:|---------|
| `data-testid` | yes | Stable automation locator |
| `data-expected` | yes for displayed business values | Expected text/value |
| `data-rule` | optional | Business rule behind state/value |
| `data-test-scenario` | optional | Scenario grouping |
| `data-assert` | optional | Assertion config |
| `data-depends-on` | optional | Dependent testid |
| `data-loads-after` | optional | Async completion marker |
| `data-variant` | optional | Multi-state variant |

Naming:

```text
{domain}-{component}-{variant}

item-list-row-{item_id}
customer-card-{customer_id}
status-badge-pending
task-status-pending
btn-approve-request-{request_id}
modal-confirm-reject
chart-monthly-trend
table-summary
```

## Command and State Annotations

Buttons:

```html
<button
  data-testid="btn-submit-review"
  data-action="submit-review"
  data-behavior="提交复核材料并将状态置为submitted"
>
  提交
</button>
```

Stateful containers:

```html
<section
  data-testid="review-workflow"
  data-state="pending_review"
  data-allowed-actions="approve,reject"
>
</section>
```

State enum contract:

```javascript
window.STATE_ENUMS = {
  lead: ["pending_review", "approved", "rejected"],
  ticket: ["open", "processing", "resolved", "closed"]
};
```

Rules:

- Runtime attributes must not contain unresolved template placeholders such as
  `data-state="${state}"`. If a renderer uses templates, the rendered DOM must
  contain concrete values and the full enum space must be exported in
  `window.STATE_ENUMS`.
- `data-state` values use concrete business states, not CSS classes or display
  text. PRD FRR §9 must use the same enum values.
- When state is composite, use a stable namespace such as
  `objectType:stateName` or expose the object type in `data-state-owner`.

API-backed components:

```html
<table
  data-testid="request-table"
  data-api="/api/v1/requests"
  data-method="GET"
  data-loads-after="api:getRequests"
></table>
```

Role-specific views:

```html
<button data-visible-role="supervisor" data-action="approve-task">审批</button>
```

If role visibility is computed at runtime instead of rendered as static
`data-visible-role` attributes, export the role contract explicitly:

```javascript
window.PROTOTYPE_ROLE_CONTRACT = {
  "approve-task": ["supervisor", "admin"],
  "view-finance-region": ["finance", "boss"]
};
```

Modal / drawer identity:

```html
<section
  data-testid="modal-create-lead"
  data-modal-id="create-lead"
  data-modal-title="新建线索"
  data-modal-mode="create"
>
</section>
```

Rules:

- Every modal, drawer, popover workflow, or confirmation dialog that changes
  domain state must have a stable `data-testid="modal-{modal_id}"` or
  `data-testid="drawer-{drawer_id}"`.
- Helper APIs such as `showModal(title, body, ...)` must either render a stable
  modal testid from an explicit id or maintain a `window.MODAL_CONTRACT` map
  from triggering `data-action` to modal id, title, fields, and result action.
- A title-only modal is not enough for PRD or automated test traceability.

Write action API contract:

```javascript
window.ACTION_API_CONTRACT = {
  "save-lead": {
    method: "POST",
    api: "/api/leads",
    domain_result: "LeadCreated",
    rollback: "none"
  }
};
```

Rules:

- Write actions should expose `data-api` and `data-method` on the triggering
  element when practical.
- If the API is intentionally abstract in prototype mode, export
  `window.ACTION_API_CONTRACT` so the PRD/coding-agent handoff can still map
  actions to backend commands, state changes, events, and failure behavior.

## State-Driven UI Iron Law

Generated HTML prototypes must follow `UI = f(State)`. DOM attributes and
selectors are allowed for event routing, automation, and rendering verification,
but they must never be the source of truth for business lifecycle state.

Required architecture for workflow prototypes:

```javascript
window.GlobalState = {
  route: "dashboard",
  role: "admin",
  entities: {},
  ui: {},
  presentationMode: false
};

function transition(currentState, action) {
  // pure business transition: no DOM reads/writes here
  return nextState;
}

function render(state) {
  // one-way rendering from state to DOM
}
```

Rules:

- `data-action` is an event command, not business state.
- `data-testid`, `data-state`, `data-visible-role`, and `data-api` may be
  rendered from state and scanned by tests, but business logic must not infer
  lifecycle stage from siblings, CSS classes, element text, or DOM position.
- `querySelector` is permitted for event delegation, test helpers, focus
  management, and rendering target selection. It is forbidden as the decision
  source for guards such as “current step”, “approval state”, “selected tenant”,
  or “can submit”.
- All state-changing interactions route through one transition boundary:
  `transition(currentState, action) -> nextState`, then re-render.
- If a prototype is too small for a full renderer, it still needs a single
  state object and explicit action-to-state mapping table.

Anti-patterns:

```javascript
// FAIL: business state inferred from DOM text
if (document.querySelector(".badge").textContent === "待审核") approve();

// FAIL: next step inferred from sibling order
var next = button.parentElement.nextElementSibling;

// PASS: command payload comes from data-action, business state from GlobalState
dispatch({ type: event.target.dataset.action, id: event.target.dataset.id });
```

## Interaction Completeness Gate

Semantic attributes are required, but they are not a substitute for working behavior. A prototype is acceptable only when the user can operate the main workflows and a developer can trace each command to an implemented outcome.

Rules:
- Every `data-action` value must have a click handler or event-delegation branch.
- No literal template placeholder may remain in runtime attributes, such as `data-action="${action}"`.
- Every command must produce a visible outcome: route/view change, modal, toast, state update, table update, chart update, or form value change.
- Every navigable view must have a render path and at least one meaningful interactive element unless it is explicitly read-only.
- Filters, tabs, pagination, step controls, batch actions, role switches, and modal buttons must be executable, not only labeled.
- If the prototype is a new version of an older prototype, compare against the Stage 0 interaction ledger and preserve previous coverage unless de-scoped.

Minimal action audit:

```javascript
window._testActions = function() {
  var actions = Array.from(document.querySelectorAll("[data-action]"))
    .map(function(el) { return el.dataset.action; })
    .filter(Boolean);
  return Array.from(new Set(actions)).sort();
};
```

Acceptance:
- `data-action` count and named action list are reviewed against the PRD and, for iterations, the previous prototype.
- Handler coverage is 100% for non-disabled commands.
- Main user journeys pass in browser walkthrough, not only DOM scan.

## Dynamic Surface Scan Gate

Static HTML scans are insufficient for role-based apps, tabbed pages, drawers,
modals, lazy-rendered lists, or stateful prototypes. Before marking a prototype
ready for PRD/coding-agent handoff, scan the rendered DOM after exercising the
state surface.

Required scan dimensions:

| Dimension | Minimum Coverage |
|---|---|
| Role | each primary role or role group that changes navigation, visibility, or permissions |
| View/tab | each navigable page and each tab/segment/filter that renders unique actions or fields |
| Modal/drawer | each create/edit/detail/confirm modal or drawer opened by its trigger action |
| State | at least one record for each meaningful lifecycle state and guard branch |
| Repeated content | empty, one-record, and multi-record rendering for tables, cards, timelines, and child rows |

Record the scan as a dynamic interaction ledger with rendered `data-testid`,
`data-action`, `data-field`, `data-state`, `data-api`, `data-method`, and
`data-visible-role` values per surface. If a value appears only after changing
tab/role/state, it still must be mapped in the PRD contract and acceptance
coverage.

Fail the gate when a primary action exists only in a hidden/dynamic surface and
has no PRD action definition, handler, modal spec, API mapping, or AC coverage.

## Assertion Modes

| Mode | Use |
|------|-----|
| exact | exact text match |
| contains | substring match |
| regex | pattern match |
| numeric | range assertion |
| exists | element exists |
| visible | element visible |
| count | row/card count |
| order | ordered labels/states |

## Multi-Step Forms

Required naming for wizard/steps:

| Element | Pattern |
|---------|---------|
| step container | `stepper-{flow}` |
| current step indicator | `step-indicator-{flow}` |
| step item | `step-item-{flow}-{stepKey}` |
| next button | `btn-next-step-{flow}` |
| previous button | `btn-prev-step-{flow}` |
| draft button | `btn-save-draft-{flow}` |
| submit button | `btn-submit-{flow}` |
| step error | `step-error-{flow}-{stepKey}` |

Rules:
- `step-indicator-*` must include `data-current-step` and `data-total-steps`.
- `step-item-*` must include `data-step-status="pending|active|done|error"`.
- Tests must not depend on DOM child index.

## Batch Operations

Required naming:

| Element | Pattern |
|---------|---------|
| select all | `chk-select-all-{scope}` |
| row checkbox | `chk-select-row-{scope}-{id}` |
| selected count | `badge-selected-count-{scope}` |
| batch toolbar | `toolbar-batch-action-{scope}` |
| batch button | `btn-batch-{action}-{scope}` |
| confirm modal | `modal-batch-confirm-{action}-{scope}` |
| result toast | `toast-batch-result-{scope}` |

Rules:
- Batch toolbar includes `data-selected-count`.
- Batch button includes `data-action="batch-{action}"` and `data-requires-confirm`.
- Tests must cover 0, 1, many, cross-page, and partial failure.

## Scenario Test Template

```yaml
test_scenario:
  id: TS-001
  name: 申请复核流程
  role: 业务审核员
  precondition: 申请A存在待复核字段
  steps:
    - action: 打开申请列表
      testid: request-list
      expected: 列表加载完成
    - action: 查看申请A详情
      testid: request-detail-A
      expected: 状态显示待复核
    - action: 点击辅助分析
      testid: btn-assisted-analysis
      expected: 弹窗显示分析过程和置信度
  postcondition: 申请A进入待确认状态
```

## Verification Loop

```yaml
verify_loop:
  max_retries: 3
  mode: incremental
  checkpoint: true
  on_failure:
    capture: [screenshot, dom_snapshot, console_log]
    classify: [locator_missing, assertion_mismatch, async_timeout, permission_blocked, data_error]
```

Exit conditions:
- all steps pass -> PASS;
- max retries reached -> FAIL;
- same failure three times -> BLOCKED;
- timeout exceeded -> TIMEOUT;
- manual stop -> ABORTED.

## Test State Self-Healing / Shadow-Data Isolation

Automated browser agents must not pollute real business data, indicator libraries, reports, or production statistics.

Rules:

- Any automated scenario that may call a backend must carry `data-test-scenario` and a unique `data-test-run-id`.
- The deterministic test runner or gateway must inject `X-Agent-Test-Mode: true` on outbound requests for automated scenarios.
- Backend/API gateway must route test-mode writes to one of:
  - shadow table / shadow database;
  - tenant-scoped test workspace;
  - transaction rollback after assertion;
  - Saga compensation with verified cleanup.
- Test data must include `test_run_id`, `trace_id`, creator, timestamp, and expiry.
- Reporting, metric, BI, index library, and dashboard queries must exclude test-mode records by default.
- Production writes are forbidden for automated browser verification unless shadow isolation is active and verified.
- Cleanup must be idempotent. Re-running cleanup for the same `test_run_id` must be safe.

Minimum backend contract:

```yaml
test_mode_isolation:
  request_header: X-Agent-Test-Mode
  required_when: data-test-scenario present
  write_routing: shadow_db | shadow_table | rollback_transaction | saga_compensation
  cleanup:
    key: test_run_id
    idempotent: true
    max_ttl: 24h
  metrics_exclusion: test_mode == true
```

Fail if an automated acceptance run can create customer-visible data, affect KPI/statistics, trigger real notifications, or mutate master data without shadow isolation.

## Prototype Helper Contract

Include a minimal test helper when possible:

```javascript
window._test = {
  scan: function() {
    return Array.from(document.querySelectorAll('[data-testid]')).map(function(el) {
      return {
        testid: el.dataset.testid,
        text: el.textContent.trim(),
        expected: el.dataset.expected || null,
        state: el.dataset.state || null,
        visible: el.offsetParent !== null,
        variant: el.dataset.variant || null
      };
    });
  },
  assert: function(testid, assertion) {
    var el = document.querySelector('[data-testid="' + testid + '"]');
    if (!el) return { pass: false, error: 'element not found', testid: testid };
    var text = el.textContent.trim();
    var mode = assertion.mode || 'contains';
    var value = assertion.value;
    if (mode === 'exact') return { pass: text === value, expected: value, actual: text };
    if (mode === 'contains') return { pass: text.indexOf(value) >= 0, expected: value, actual: text };
    if (mode === 'exists') return { pass: !!el };
    if (mode === 'visible') return { pass: el.offsetParent !== null };
    return { pass: false, error: 'unknown mode' };
  }
};
```

## Prototype Design Process

Use a compact design process before writing HTML. Do not import external
`design.md` files wholesale; extract only reusable process rules.

1. **Scenario first**: identify the role, task, decision, and success result.
2. **Structure before style**: lock IA Skeleton views, regions, and navigation
   before selecting colors or component flavor.
3. **Content density**: decide whether the screen is operational, analytical,
   mobile task, customer-facing demo, or consumer experience.
4. **Component state**: define empty, loading, error, disabled, selected,
   hover/focus, permission-denied, and offline states for primary controls.
5. **Visual system**: choose a design-system style only when it affects brand,
   acceptance, customer demo, or implementation reuse.
6. **Responsive pass**: verify desktop and mobile layout constraints for tables,
   forms, cards, dialogs, and long text.
7. **Screenshot pass**: inspect at least one desktop and one mobile viewport
   before declaring the prototype visually acceptable.

This process can improve prototype quality, but it must not override IA,
state, role path, business rules, or testability contracts.

## Visual Design Rules

- Build actual usable screens, not landing pages, unless requested.
- Operational ToG/ToB tools should be dense, quiet, and scannable.
- Do not hide the primary workflow inside decorative cards.
- Use stable layout dimensions for boards, tables, tabs, toolbars, and counters.
- Text must not overflow buttons/cards on desktop or mobile.
- Use familiar controls: icons for tools, segmented controls for modes, checkboxes for binary choices, tabs for views.
- Avoid one-hue palettes and decorative gradient blobs.

### Visual Style Clarification And External UI Skills

Ask a short visual-style clarification when style affects acceptance, brand,
customer demo, procurement review, or design-system compatibility. Useful
choices include Ant Design-style enterprise UI, Apple glass-style consumer UI,
Google Material-style flat UI, ArcoDesign / ByteDance-style enterprise UI, or
an existing company design system.

If the user does not specify a style and the request is an operational ToB/ToG
prototype, default to a restrained enterprise style: dense information,
moderate contrast, predictable tables/forms, 4-8px radii, stable layout, and no
decorative hero sections.

If a dedicated `frontend-design`, `web-design-guidelines`, `uiux`, Figma, or
brand-system skill is installed and the task includes visual design quality,
use it for visual language and component-system decisions. AI Delivery Spec
remains responsible for IA, data-testid/data-action, state, role path, business
rules, and acceptance traceability.

## Presentation Mode Specification

Customer-facing or sponsor-facing prototypes should provide a global
`Presentation Mode` / `演示模式` switch when the prototype will be used for
customer demo, boss review, bid presentation, or requirements workshop.

Activation behavior:

| Capability | Required Behavior |
|---|---|
| Technical noise control | Hide debug consoles, internal test panels, raw mock-data controls, and developer-only annotations. Keep `data-testid` and `data-action` in DOM for automation; do not visually expose them unless a debug panel is active. |
| Storyline guidance | Show a side guide for the locked core user journey, including current step, next action, expected business value, and branch options. |
| One-click main path | Provide a safe “start main journey” action that moves the user to the first step without skipping required visible screens. |
| Adversarial rehearsal | Include safe simulation controls for invalid generic input, permission denial, stale version, weak network/offline, dependency failure, or guard rejection when those risks are in scope. |
| Evidence capture | Allow screenshot/demo-note capture or visible scenario summary when practical. |

State contract:

```javascript
window.GlobalState.presentationMode = true;
window.GlobalState.demoScenario = "main-journey";
```

Rules:

- Presentation Mode must not alter domain rules, permission guards, validation,
  or state transitions. It changes visibility and guidance only.
- Error-flow simulation buttons must use mock/shadow data and must not call real
  production writes.
- If the prototype is L0 or purely internal, Presentation Mode may be marked
  `N/A` with reason.

## Prototype Acceptance Checklist

- [ ] All interactive elements have `data-testid`.
- [ ] All commands have `data-action`.
- [ ] All implementation-relevant displayed/input/calculated fields have
      `data-field` or a documented field dictionary mapping.
- [ ] Backend-writing automated scenarios have shadow-data isolation or are explicitly disabled.
- [ ] All `data-action` commands have implemented handlers and visible outcomes.
- [ ] No placeholder attributes remain, such as `${action}`.
- [ ] All stateful containers have concrete `data-state`; renderer templates
      export `window.STATE_ENUMS` and no runtime `data-state="${...}"` remains.
- [ ] Runtime role visibility is either represented by `data-visible-role` or
      exported through `window.PROTOTYPE_ROLE_CONTRACT`.
- [ ] Domain-state modals/drawers have stable `modal-*` / `drawer-*` testids or
      are listed in `window.MODAL_CONTRACT`.
- [ ] Write actions expose `data-api`/`data-method` or are mapped in
      `window.ACTION_API_CONTRACT`.
- [ ] Async sections have `data-loads-after`.
- [ ] Modals, toasts, charts, tables, row items have stable testids.
- [ ] Multi-step and batch operations use the required naming.
- [ ] Iterative prototypes pass the interaction parity gate against the prior version.
- [ ] Mobile/responsive variants preserve testid system.
- [ ] `_test.scan()` finds the critical path elements.
- [ ] Browser/Playwright can complete the main scenario without brittle selectors.
- [ ] Dynamic role/tab/modal/state scan has been performed; hidden/dynamic
      actions and fields are included in the PRD/prototype cross-check.
- [ ] Workflow prototypes use `GlobalState` and transition-driven state changes.
- [ ] Customer/sponsor demos include Presentation Mode or an explicit `N/A` reason.
