# Prototype + Testability

Use this file when generating, reviewing, or repairing an HTML prototype.

## Contents

- Five-Layer Test Annotation
- Command and State Annotations
- Interaction Completeness Gate
- Assertion Modes
- Multi-Step Forms
- Batch Operations
- Scenario Test Template
- Verification Loop
- Test State Self-Healing / Shadow-Data Isolation
- Prototype Helper Contract
- Visual Design Rules
- Prototype Acceptance Checklist

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

## Visual Design Rules

- Build actual usable screens, not landing pages, unless requested.
- Operational ToG/ToB tools should be dense, quiet, and scannable.
- Do not hide the primary workflow inside decorative cards.
- Use stable layout dimensions for boards, tables, tabs, toolbars, and counters.
- Text must not overflow buttons/cards on desktop or mobile.
- Use familiar controls: icons for tools, segmented controls for modes, checkboxes for binary choices, tabs for views.
- Avoid one-hue palettes and decorative gradient blobs.

## Prototype Acceptance Checklist

- [ ] All interactive elements have `data-testid`.
- [ ] All commands have `data-action`.
- [ ] Backend-writing automated scenarios have shadow-data isolation or are explicitly disabled.
- [ ] All `data-action` commands have implemented handlers and visible outcomes.
- [ ] No placeholder attributes remain, such as `${action}`.
- [ ] All stateful containers have `data-state`.
- [ ] Async sections have `data-loads-after`.
- [ ] Modals, toasts, charts, tables, row items have stable testids.
- [ ] Multi-step and batch operations use the required naming.
- [ ] Iterative prototypes pass the interaction parity gate against the prior version.
- [ ] Mobile/responsive variants preserve testid system.
- [ ] `_test.scan()` finds the critical path elements.
- [ ] Browser/Playwright can complete the main scenario without brittle selectors.
