# Prototype And Testability - v5

Use when creating, reverse-engineering, reviewing, or repairing an interactive
prototype. The prototype is a projection of Product Truth, not an independent
source of scope or business behavior.

## 1. Input Contract

Before UI work, obtain or recover:

- `MOD/FLOW/VIEW/REG/ACT/FLD/STATE/AC` graph;
- role and data-scope variants;
- default, empty, loading, error, no-permission, partial, and success states;
- visible and domain result of every primary action;
- representative data, dictionaries, long-data and large-list behavior;
- modal/drawer chains, responsive surfaces, print/export when in scope.

If the input is an existing prototype, first run:

```powershell
py -3 scripts/extract_interaction_ledger.py --input app.html --output interaction-ledger.json
```

Register views, actions, handlers, fields, states, modals, role paths, data
sets, and gaps before changing the prototype.

## 2. Stable Runtime Annotations

| Product Truth | Prototype Contract |
|---|---|
| `VIEW-*` | page/modal/drawer root `data-testid="page-{view_id}"` |
| `REG-*` | container `data-testid="region-{region_id}"` |
| `ACT-*` | interactive control `data-action="{ACT-*}"` |
| `FLD-*` | field/value `data-field="{FLD-*}"` or `data-bind` |
| state enum | `data-state="{concrete-state}"` |
| role scope | `data-visible-role` where useful for tests |
| command/API | `data-api` and `data-method` only when known |
| `AC-*` | stable test anchor and scenario reference |

Every important interactive/testable element has a stable anchor. Do not expose
unresolved template strings such as `data-state="${state}"` in rendered DOM.

## 3. State-Driven UI

Business state lives in an explicit state model, not in CSS classes, button
labels, or inferred DOM text.

```javascript
const GlobalState = {
  currentRole: "ROLE-USER",
  entities: {},
  permissions: {},
  network: "online"
};

function transition(ownerId, actionId, payload) {
  // validate role, permission, current state, guard, and idempotency
  // persist mock/domain result
  // emit event/audit evidence
  // render visible result
}
```

For lightweight static prototypes, the implementation may be smaller, but the
same action must still lead to the Product Truth state and result.

## 4. Interaction Closure

Every `data-action` needs:

1. event handler;
2. allowed role/state and guard;
3. visible feedback during execution;
4. visible completion result;
5. domain/state result in prototype state;
6. failure and recovery behavior;
7. trace to `ACT-*` and `AC-*`.

Toast-only completion fails for a core state-changing action. Prefer list/card/
detail/state changes that let users see what was created or changed.

Parent click handlers must ignore nested interactive/editable targets:

```javascript
if (event.target.closest("button,input,textarea,select,a,[contenteditable]")) return;
```

Prefer event delegation with `data-*` values over inline `onclick` strings.

## 5. Required UI States

For each view, implement applicable states:

| State | Visible Requirement |
|---|---|
| default | normal data and primary task |
| empty | reason, next action, no fake records |
| loading | scope of loading and disabled duplicate action |
| error | reason, retry/manual path, preserved input where safe |
| no_permission | clear boundary without leaking hidden data |
| partial/stale | freshness warning and restricted consequential action |
| success | durable result and next action |

Use representative data volume: long names, null fields, multiple statuses,
pagination/scroll, narrow screen, and restricted records when relevant.

## 6. Complex Interaction Patterns

### Modal And Drawer Chains

Define trigger, content, fields, confirmation, cancel, close behavior, loading,
success, failure, and the visible/domain result after closing. Every modal or
drawer must be reachable from a declared view/action.

### Forms And Cascades

Cover default, required, dictionary, dependency, async validation, dynamic row,
calculation, attachment, draft, submit, duplicate, and recovery behavior.
Backend rules remain authoritative even in a prototype contract.

### Batch And Drag Operations

Define selection eligibility, mixed-state behavior, confirmation, partial
failure, retry, undo/compensation, ordering, and audit. Drag behavior covers
start, allowed target, hover cue, drop result, invalid drop, and keyboard/mobile
alternative where required.

### Async, Realtime, And Weak Network

Use `references/runtime/realtime-contract.md` for SSE/WebSocket/countdown/push. Show
reconnect, stale state, duplicate, offline queue, conflict, retry, and manual
reconciliation behavior when applicable.

## 7. Prototype Iteration Parity

When revising an existing prototype, compare before/after:

- views/routes;
- actions and handlers;
- fields and dictionaries;
- states and transitions;
- modals/drawers;
- role paths and data scope;
- representative data volume;
- critical workflows and acceptance anchors.

Removal requires an approved `CHG-*` or explicit de-scope. A visually cleaner
prototype that loses behavior fails parity.

State changes should update only necessary classes/attributes/content when
possible; unnecessary DOM reconstruction can lose focus, cursor, scroll, and
element references.

## 8. Safe Verification Loop

1. Check HTML/JavaScript syntax.
2. Load in a real browser.
3. Verify each primary role/task one action at a time without design hints.
4. Exercise default and applicable failure/permission/state paths.
5. Confirm visible and domain result against Product Truth.
6. Confirm all runtime annotations are concrete and unique where required.
7. Capture screenshot/trace/audit evidence by AC ID.
8. Re-run parity after fixes.

Automated writes use mock, shadow, or disposable test data. Never pollute live
customer data or production metrics without explicit authorization and a safe
test plan.

Minimum walkthrough record:

| Step | Visible Cue | User Action | Visible Result | Domain Result | Blocker / Assumption | AC |
|---|---|---|---|---|---|---|

If the next step cannot be inferred from visible cues, stop and record the
blocker; do not explain the intended route during the test.

## 9. Visual And Accessibility Baseline

- Use a coherent design system: spacing, typography, color, components, icons.
- Preserve hierarchy and task focus; avoid dense dashboard decoration without
  product meaning.
- Do not use color alone for state.
- Provide keyboard/focus behavior, labels, contrast, error association, and
  reduced-motion behavior appropriate to scope.
- Define responsive priority: what reflows, collapses, becomes read-only, or
  moves to another surface.
- Print/export views preserve required fields, pagination, signatures, version,
  and archive metadata when they are acceptance evidence.

Visual fidelity does not excuse missing interaction or business behavior.

## 10. Lock And Acceptance

When complete, record:

```text
[PROTOTYPE LOCK]
truth_version=
view_count=
region_count=
action_count=
state_count=
role_paths=
gaps=
evidence_location=
```

Prototype completion requires:

- all in-scope views/actions trace to Product Truth;
- primary role journeys are demo-closed;
- applicable empty/error/permission/state-conflict paths work;
- no unapproved parity loss;
- browser evidence exists for required ACs;
- unresolved gaps have owner and completion state.
