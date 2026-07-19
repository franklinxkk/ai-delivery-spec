# Page, Prototype And Testability Contract

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
- the declared page whitelist and the complete Page Delivery Contract for each
  view, including metrics, columns, filters, controls, limits and pagination.

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
| `METRIC-*` | displayed KPI root `data-metric="{METRIC-*}"` |
| state enum | `data-state="{concrete-state}"` |
| role scope | `data-visible-role` where useful for tests |
| command/API | `data-api` and `data-method` only when known |
| `AC-*` | stable test anchor and scenario reference |

Every important interactive/testable element has a stable anchor. Every displayed
statistic/KPI has `data-metric` and resolves to the PRD's page-local caliber;
the label and sample number alone are not a metric contract. Do not expose
unresolved template strings such as `data-state="${state}"` in rendered DOM.
Write these anchors in the source markup/template itself. A runtime pass that
retrofits generic `ACT-UI-*` identifiers onto unrelated legacy commands does
not establish traceability. Never hide an anchor name with string concatenation
such as `data-'+'action`; a static PASS is allowed only when the gate can enumerate
the authored anchors. Generated controls must still expose a statically inspectable
template/registry and must be proven separately by browser acceptance evidence.

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

Do not use one generic “edit/detail” modal across different entities unless its
schema and handler are explicitly entity-aware. A question edit action opening
a resource detail surface is a blocker even when both controls technically have
handlers.

Parent click handlers must ignore nested interactive/editable targets:

```javascript
if (event.target.closest("button,input,textarea,select,a,[contenteditable]")) return;
```

Prefer event delegation with `data-*` values over inline `onclick` strings.
For L3 handoff, inline `onclick` and generic alert-only fallbacks are prohibited.
Use one explicit action registry whose keys are the static `ACT-*` values.

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

Use `references/patterns/realtime-contract.md` for SSE/WebSocket/countdown/push. Show
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

If the existing artifact contains duplicate function declarations, stacked
override layers, inline-handler quoting, runtime action-ID retrofits, or entity
actions routed to the wrong modal, stop patching. Preserve the interaction
ledger and representative data, then rebuild a clean projection with one state
store, one renderer per view and one action registry.

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

At L3, sweep every visible action on every declared page, not only one happy
path per role. Assert that the opened page/modal belongs to the action's entity,
that field controls match the Page Delivery Contract and that the durable result
appears in the owning list/detail after close.

Record the sweep as an `ARUN-*`: its environment names the real browser/device,
each prototype `data-ac` has an executed item, and every pass has actual result
plus screenshot/trace/audit evidence. Supply it to the gate with
`--acceptance-run`. If no browser capability is available, create a pending
ARUN and an exact action checklist, return `REVIEW_COMPLETE_WITH_GAPS`, and do
not describe the interactive prototype as complete.

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

Before a visual redesign, clarify three user-owned direction inputs: intended
feeling, reference product/artifact, and explicit taboo. Record the decision as
`DEC-AESTHETIC-*`; if unavailable, create a P1 `UNK-*` with
`blocks_stage: baseline` instead of silently choosing a style. For competing
directions, show no more than one screen or one direction card
(`style + feeling keywords + reference + taboo`) and confirm it before applying
the direction to every page.

Then record one design-system baseline (for example Ant Design 5 tokens and
components) and, when useful, apply one specialized design skill. Do not claim
that an uninstalled skill was executed; call a public-rule imitation a method
reference. Capture full-page screenshots at desktop and one narrow width and
perform a visual critique before completion.

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
browser_evidence_status=pending|passed|blocked
aesthetic_decision_ref=DEC-AESTHETIC-*|UNK-*
gaps=
evidence_location=
```

Prototype completion requires:

- all in-scope views/actions trace to Product Truth;
- primary role journeys are demo-closed;
- applicable empty/error/permission/state-conflict paths work;
- no unapproved parity loss;
- browser evidence exists for required ACs;
- complex L3 views expose stable `REG-*` region anchors;
- unresolved gaps have owner and completion state.
Before accepting an HTML prototype, run:

```bash
python scripts/scan_prototype_css.py prototype.html
```

The scanner requires a single isolated `.hidden { display: none ... }` utility
when the class is used and rejects `!important` outside that utility. Duplicate
or combined `.hidden` selectors are treated as cascade pollution because they
commonly make modal/view state impossible to reason about.

Generic behavior/state classes must also be component-scoped. Do not group a
global `.active`, `.open`, `.selected`, `.disabled`, `.loading`, `.error`,
`.success` or `.failed` selector with business status colors: it can recolor or
hide the active page, navigation or tab. Use separate selectors such as
`.status.active`, `.tab.active` and `.page.active`.

## Page Profiles And Conditional Surfaces

Each implementation view starts with a machine-readable marker:

```markdown
<!-- PAGE-CONTRACT: VIEW-RESOURCE; primary=list; layout=composite; surfaces=metrics,list,drawer_form,preview -->
```

`layout` is `single`, `composite`, `builder`, or `portal`. `surfaces` are composed
from `metrics`, `list`, `form`, `drawer_form`, `detail`, `workflow`, `composer`,
`resource_pool`, `hierarchy`, `assessment_insert`, `import`, `export`, and
`preview`. Do not create industry-specific page profiles. A composite view has
at least two real surfaces; a builder declares composer, resource pool and
hierarchy. Mobile/H5 capabilities are separate (`scan`, `camera`,
`weak_network`, `offline_draft`, `push`) and are never inferred.

Only activated surfaces are mandatory. For each view specify purpose/entry,
regions/layout, role and data scope, default/empty/loading/error/no-permission/
stale/success states, modal/drawer chains, pagination/bulk behavior, prototype
anchors and applicable API/AC trace. Then add conditional contracts:

- metrics: population, numerator/denominator, window/timezone, status/filter,
  deduplication, source/freshness, zero/null and format;
- list/tree: filters, columns, format/width/null/sort, selection and page size;
- form/upload: control, required/default, type/length, dictionary, validation,
  editability, extension/MIME, count/size, preflight, conversion and recovery;
- action/workflow: guard, confirmation, visible/domain result, state/event/audit,
  permission, idempotency, failure/compensation and AC;
- import/export: template/version, scope, partial failure, async threshold,
  file expiry, masking and audit;
- preview: per-file controls, conversion failure and authorization/watermark;
- composer: hierarchy, allowed source/target, insertion/order, invalid drop,
  persistence, undo/recovery, concurrency and keyboard/mobile alternative.

At L3/L4, a composite, builder, portal, multi-view artifact, or a page combining
table and form controls must expose stable `region-REG-*` roots for its meaningful
layout regions. A complex prototype with `region_count=0` is not a complete
page contract; a bounded single-surface page may remain regionless.

When the user requests high-fidelity, branding, visual redesign, or a
production-grade prototype, freeze the UI requirement contract first. Prefer a
design-system-oriented UI/UX skill for complex enterprise back offices and a
frontend art-direction skill for brand/H5 differentiation; never let two tools
create competing design systems. Visual quality does not replace interaction
closure or business truth.

## Stage 0 For Existing Prototypes

Before rewriting an existing artifact, inventory every view, action, handler,
state, role, object, field/metric and external handoff with `source_ref`, source
location and classification: `confirmed`, `inferred`, `unknown`, or
`defect_candidate`. Core unknowns become `UNK-*` with priority, owner and
`blocks_stage`; defects cannot silently become target requirements. Multiple
candidate baselines require a scoped `DEC-CONFLICT-*`. Only a fully classified,
source-located inventory may declare `inventory_complete`; that proves inventory
coverage, not business approval.

If a PRD baseline exists, use `INV-*` for recovered prototype observations and
map them to declared `baseline_requirement_refs` with `mapping_status` plus exact
`target_refs`. Put every inferred item into an owned `RBATCH-*`; do not declare
`baseline_ready` until those batches are confirmed, rejected or converted to
owned unknowns. Reverse extraction can recover interaction evidence, but cannot
infer API semantics, metric caliber, permission authority, compliance or AC truth.
