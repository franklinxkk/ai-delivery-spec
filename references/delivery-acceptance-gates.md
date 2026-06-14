# Delivery Acceptance Gates

Use this reference to review a single product-lifecycle artifact or a final PRD, prototype, test/UAT, customer-demo, development, release, post-launch, or retirement package.

## Contents

- 0. Lifecycle Artifact Review
- 1. Interaction Ledger
- 1.5 Source Coverage And Product Specification Completeness
- 2. State-Button Matrix
- 3. No Toast-Only Core Actions
- 4. Role Path Verification
- 5. Customer Demo Closure
- 5.5 Gate 2 Surface Branches
- 6. Browser/DOM Verification
- 7. Final Delivery Package
- 7.5 Post-Launch Evidence Review
- 8. Common Failure Patterns
- 8.5 Mobile Acceptance

## 0. Lifecycle Artifact Review

Any lifecycle artifact may enter the skill independently. Review its fitness for the declared stage and downstream decision; do not fail it merely because adjacent-stage artifacts are absent.

Minimum review record:

```yaml
lifecycle_artifact_review:
  artifact:
  lifecycle_stage: discovery | definition | design | engineering | verification | release | operation_learning | retirement
  artifact_type:
  scope: single_artifact | module_package | full_package
  mode: Lite | Standard | Full
  tier: L0 | L1 | L2 | L3 | inherited | N/A_lifecycle_governance
  accountable_owner:
  downstream_consumer_or_decision:
  upstream_inputs_used: []
  applicable_gates: []
  decision: PASS | REVIEW_COMPLETE_WITH_GAPS | BLOCKED
  evidence_checked: []
  contradictions: []
  missing_evidence: []
  next_required_decision_or_artifact:
```

Lifecycle coverage:

| Stage | Typical Artifact | Minimum Review Evidence | Fail When |
|---|---|---|---|
| discovery/decision | interview synthesis, opportunity brief, business case, competitor/market analysis, roadmap decision | sources, facts vs assumptions, target outcome, alternatives, decision threshold, owner | recommendation has no attributable evidence or decision rule |
| definition | scope, story inventory, role path, PRD, state model | user/business outcome, boundaries, paths, states/guards, domain result, acceptance | feature names exist without executable behavior or acceptance |
| design | IA, UX flow, design handoff, prototype | role entry/exit, interaction/state coverage, responsive/accessibility constraints, visible outcomes | primary path is ambiguous, dead, or contradicts the requirement |
| engineering | product-linked architecture, API/schema/data/migration contract, Developer Fast-Lane | trace to stories/states, inputs/outputs, versions, errors, idempotency, security/permission, rollback | implementation contract invents or omits business behavior |
| verification | test plan/cases, traceability matrix, UAT/acceptance report | requirement-to-test links, positive/negative/permission/state/regression coverage, evidence, defect disposition | pass/fail claims lack reproducible evidence or critical paths are untested |
| release | pilot/rollout plan, runbook, readiness record, support handoff | scope, environment, migration, observability, rollback, support/on-call, approval | P0 readiness has no owner, mitigation, or tested fallback |
| operation/learning | metric dashboard spec, experiment/effect report, incident or delivery retrospective | metric lineage, cohort/window, guardrails, evidence strength, root cause, action owner, decision | correlation is presented as causation or learning has no owned action |
| retirement | deprecation/sunset plan, tenant/provider migration, export/deletion evidence | dependency inventory, customer notice, migration/export, retention/deletion, support end, rollback window | customers/data/dependencies can be stranded or silently deleted |

Review rules:

- Judge internal consistency, traceability to available upstream evidence, and fitness for the named downstream consumer.
- Mark unavailable adjacent artifacts as package gaps only when a full package was requested.
- A polished document with no owner, evidence, decision, or downstream acceptance is not PASS.
- When two supplied artifacts conflict, list the exact fields/behaviors and identify the decision owner; do not silently choose one.
- Artifact PASS means the artifact is fit for its declared purpose. It does not mean the whole product or release is approved.

## 1. Interaction Ledger

Required when iterating from an existing prototype or old PRD.

| Area | Required Fields |
|---|---|
| Views | view id/name, entry URL/file, role visibility, empty state |
| Actions | label, `data-action`, handler, visible outcome, state mutation |
| Modals/Drawers | trigger, displayed business data, submit/close actions |
| States | object, state values, transitions, guards, forbidden actions |
| Mock Data | objects, variants, happy/exception coverage |
| Critical Paths | role, start page, steps, expected visible result |
| Regression Diff | removed/changed behavior, preserve/replace/de-scope decision, owner/reason |

Fail if a critical old behavior disappears without a de-scope note.

## 1.5 Source Coverage And Product Specification Completeness

Required for an L2/L3 PRD or development handoff when detailed source material is supplied.

### Source Coverage

| Check | Pass Rule |
|---|---|
| Evidence inventory | every file and relevant sheet/page/section/view/schema/rule catalog is registered |
| Atomic counts | metrics, rules, fields, prototype actions, dictionary values, and policy clauses have explicit counts or ranges |
| Disposition | every source item is `EMBEDDED`, `AUTHORITATIVE_ANNEX`, `DEFERRED`, `CONFLICT`, or `NOT_APPLICABLE` |
| Authority | annex/source version, owner, effective scope, and target module are declared |
| Traceability | source -> module/rule/field -> engineering contract -> acceptance/test is navigable |
| Silent omission | zero |

### Product Specification Completeness

Every in-scope implementation module must be `FULL_SPEC` and define:

- roles/scenarios and complete operation paths;
- pages/views and loading/empty/error/result behavior;
- fields/dictionaries and validation/editability;
- actions/interactions and visible/domain results;
- business rules/calibers and priority/conflict behavior;
- states, buttons, guards, permissions, data scope, audit;
- exceptions/fallback, cross-module/external dependencies;
- module acceptance and source/test/prototype traceability.

Fail when:

- a detailed Excel/PDF/SQL/prototype/rule catalog is reduced to examples or a short summary without a frozen authoritative annex;
- an in-scope module has only purpose, inputs, outputs, aggregates, or commands but omits product behavior needed by PM/dev/QA;
- an appendix contains requirements but has no owner, authority, version, target module, or acceptance mapping;
- page-budget pressure causes atomic fields, rules, metrics, states, or acceptance criteria to disappear;
- a `DEFERRED` or `CONFLICT` item lacks owner and decision/release target.

## 2. State-Button Matrix

Every lifecycle object shown in a table/card/list must have this matrix before final UI/PRD handoff.

| Object | State | Visible Actions | Forbidden Actions | Guard | Visible Outcome | Domain Event/Test |
|---|---|---|---|---|---|---|
| Example: Template | Enabled | Detail, Disable | Edit, Delete | user has manage permission | detail modal or disabled state | TemplateDisabled / TC-TPL-02 |

Rules:
- Do not derive buttons from generic CRUD.
- Do not show disabled buttons unless the UX intentionally teaches the rule; otherwise hide forbidden actions.
- Backend guards must match UI rules. UI hiding is not a permission boundary.

## 3. No Toast-Only Core Actions

Core actions must produce a visible business outcome.

| Action Type | Minimum Acceptable Outcome |
|---|---|
| Create | New object appears in list/detail with correct state |
| View/Detail | Modal/page shows underlying business data, not only metadata |
| Edit/Configure | Saved value is visible after close/reopen |
| Submit/Review | Status and progress update visibly |
| Enable/Disable | State badge and operation buttons change |
| Export/Download | Result view or export confirmation references the object |
| Analyze/Generate | Generated/analysis content appears or a clear pending/error state appears |

Toast is allowed only as secondary feedback.

## 4. Role Path Verification

For each role, provide at least one happy path and one exception/permission path.

| Role | Story ID | Start | Steps | Data Touched | State Before/After | Expected Visible Result | Expected Domain Result | Test Case |
|---|---|---|---|---|---|---|---|---|

Fail if a role only appears in PRD text but cannot be walked through in the prototype.

Mobile role path sub-checks:
- Mobile roles have separate paths or an explicit "same as desktop after mobile validation" note.
- Mobile paths include entry, exit, permission gate, weak-network behavior, and mobile `data-testid`.

## 5. Customer Demo Closure

A customer-demoable prototype must be able to demonstrate:

- List → create → visible new row.
- List → detail → business data.
- List/detail → state transition → changed buttons/status.
- Template/configuration → task/report instance.
- Task/report instance → progress/result/download.
- User-facing exception: validation failure, rejected/returned item, permission boundary, or ambiguous AI field confirmation.

Workflow actions should live inside their business module. For example, "new task" belongs in the task list context unless there is a clear product reason for top-level navigation.

## 5.5 Gate 2 Surface Branches

Gate 2 checks demo closure by surface. Do not fail a native app, mini-program, or backend-admin module only because it is not an HTML prototype.

| Surface | Acceptable Demo Artifact | Required Test Identity | Minimum Pass Rule |
|---|---|---|---|
| PC Web / H5 | interactive HTML, local app, or deployed URL | `data-testid`, `data-action`, route/view id | primary paths clickable with visible result |
| Mini-program | devtools build, screen flow, or interactive H5 approximation | stable component id / `data-testid` mapping / route path | role path, permission, weak-network, submit result covered |
| Native App | dev build, TestFlight/APK, clickable prototype, or recorded walkthrough plus screen map | accessibility id / test tag / screen id | native-only flows such as permission, offline, push, camera, file upload covered |
| Backend/Admin API | API console, Swagger/Postman collection, admin screen, or CLI dry run | endpoint id, command id, test case id | command/query result and domain event visible in logs/report |
| Workflow/Low-Code Canvas | workflow editor, exported graph, or interactive mock | workflow id, node id, edge id, execution id | test run and execution trace visible |

Rules:

- Surface branch must be declared before Gate 2 review.
- If a surface cannot be made interactive, provide a screen map, operation path, recorded walkthrough, and test case evidence.
- Native App and mini-program must reference `mobile-product-delivery.md` for permission, weak-network, offline, push/message, and safe-area behavior.
- Multi-surface products must also reference `multi-surface-consistency.md`.
- The same business state machine must remain consistent across surfaces unless an explicit surface difference is approved.

## 6. Browser/DOM Verification

Before final delivery, run browser verification for highest-risk paths. If a real browser is unavailable, run deterministic DOM/action audit and state the gap.

Minimum report:

| Check | Result | Evidence |
|---|---|---|
| Script/runtime errors | PASS/FAIL | console/runtime output |
| Primary actions | PASS/FAIL | clicked actions and visible result |
| State-button matrix | PASS/FAIL | sampled states and actions |
| Role paths | PASS/FAIL | paths walked |
| Entry files | PASS/FAIL | synced files and syntax/tail checks |

For large HTML prototypes also verify:
- JavaScript syntax.
- Duplicate or overridden critical functions.
- All split entry pages are synced from the validated main file.
- Tail integrity: `</script>`, `</body>`, `</html>`.

### Automated Verification Authority

Browser/DOM automation is a release signal, not the sole release judge.

Rules:

- Automated failures default to blocking until triaged.
- A human overrule is allowed only with Sponsor or accountable owner approval, Dev/QA acknowledgement, risk reason, affected test ids, rollback plan, and expiry date.
- Human overrule cannot bypass security, privacy, permission, destructive-operation, legal/compliance, or test-data isolation guards.
- If overruled, the failed checks must remain visible in the final delivery package as accepted risk, not be deleted from the report.
- Automated browser agents must run with shadow-data isolation when backend writes are possible. See `prototype-testability.md`.

Overrule log:

```yaml
human_overrule:
  allowed: true
  approver: sponsor_or_owner
  acknowledged_by: [dev_lead, qa]
  affected_checks: [AC-001, TC-LOGIN-003]
  reason: string
  rollback_plan: string
  expires_at: date
  forbidden_to_overrule:
    - security
    - privacy
    - permission_boundary
    - destructive_operation
    - legal_compliance
    - test_data_isolation
```

## 7. Final Delivery Package

Package only the current artifact scope. A single-artifact review must not create the rest of a full package automatically.

| Artifact | Required When |
|---|---|
| Prototype/demo path | prototype, demo surface, or interaction claim is in scope |
| PRD path | PRD or development contract is in scope |
| Verification report | always, scaled to Lite/Standard/Full mode |
| State-button matrix | lifecycle-heavy object is in scope |
| Interaction ledger/regression note | iterating an old prototype/PRD |
| Source evidence register + coverage matrix | detailed attachment/evidence informed an L2/L3 PRD or development handoff |
| Complete module specification index | one or more modules are in the implementation scope |
| Test handoff checklist | development or QA handoff is in scope |
| Package gap list | the request is narrower than a full L2/L3 package |
| Unresolved risks | always, even when non-blocking |
| Human overrule log | any automated check is overridden |
| System readiness record | staging/pilot/production/customer demo with real data |

## 7.5 Post-Launch Evidence Review

Apply when reviewing a metric report, experiment/pilot result, operational review, incident postmortem, customer-feedback synthesis, or claimed product effect.

| Area | Required Evidence |
|---|---|
| Decision | continue, scale, rollback, iterate, pause, or retire; owner and deadline |
| Metric integrity | definition, source, lineage, freshness, denominator, cohort/segment, timezone/window |
| Comparison | baseline, target, comparison group or prior period, material confounders |
| Guardrails | quality, complaint, safety, compliance, support load, cost/latency where relevant |
| Qualitative evidence | customer/user feedback source, sampling boundary, severity/frequency |
| Incident learning | timeline, impact, contributing conditions, containment, root cause, corrective/preventive actions |
| Follow-through | each action has owner, due date, verification method, and closure state |

Rules:

- Separate observed output, adoption, correlation, controlled evidence, and causal claims.
- Do not accept vanity metrics without a decision they inform.
- Do not average away a failing tenant, role, locale, market, or high-risk cohort.
- For AI effects, also apply `ai-effect-evaluation.md` and its evidence levels.
- For production incidents, corrective actions must update the relevant requirement, test, runtime, readiness, or runbook contract; a narrative postmortem alone is incomplete.

## 8. Common Failure Patterns

- A page has the right title but no complete user path.
- A primary button only opens a placeholder or toast.
- A list row cannot open the underlying filled/result data.
- A newly created object is not visible after creation.
- Enabled/disabled/completed states expose the wrong actions.
- AI/Excel import skips ambiguous-field confirmation.
- Enterprise and admin paths are mixed without role visibility or data isolation.
- PRD names a module but omits inputs, outputs, processing logic, and testable transitions.
- Test/UAT report declares PASS without traceable evidence or unresolved-defect disposition.
- Post-launch report lists metrics but no baseline, guardrail, decision, or owner.
- Retirement plan omits customer migration, data export/deletion, dependency, or support-end handling.

## 8.5 Mobile Acceptance

When the product has mini-program, H5, app, mobile web, driver, field, learner, customer, or sales-on-phone workflows, apply `mobile-product-delivery.md` before final delivery.

Required:
- `mobile-role-path-matrix.md` follows the schema in `mobile-product-delivery.md`.
- `permission-gates.md` follows the schema in `mobile-product-delivery.md`.
- `weak-network-matrix.md` follows the schema in `mobile-product-delivery.md`.
- Mobile prototype paths demonstrate touch entry, sticky primary action, permission denial fallback, weak-network retry, and role-specific result state.
- Safety/non-interruption policy is present for driving, operating, medical, field, or safety-critical contexts.

Fail if the mobile flow can lose user input silently, requires desktop-only interaction patterns, or claims mobile delivery while only showing a shrunken desktop page.
