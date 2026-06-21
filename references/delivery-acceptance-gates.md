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
| Assertion status | every business statement has `VERIFIED`, `INFERRED`, `PROPOSED`, `UNKNOWN`, or `CONFLICT`; core `UNKNOWN`/`CONFLICT` blocks PASS |
| Authority | annex/source version, owner, effective scope, and target module are declared |
| Traceability | source -> module/rule/field -> engineering contract -> acceptance/test is navigable |
| Silent omission | zero |

### Product Specification Completeness

Every in-scope implementation module must first declare a complete release function inventory. Every release function must then have a deterministic Functional Requirement Record (FRR). `FULL_SPEC` is calculated from that coverage, not assigned by the author.

Function-level pass checks:

| Check | Pass Rule |
|---|---|
| Function inventory | every user-visible command/query/configuration/review/import/export/batch/system action in release scope has a Function ID |
| Coverage denominator | release function count equals complete FRR count |
| Semantic split | role, permission, trigger, aggregate/data owner, state transition, business result, audit/NFR, or acceptance-path differences create separate functions |
| FRR structure | identity/value, role/scenario, entry/preconditions, pages/states, fields/dictionaries, numbered flow, actions/results, rules/calibers, state-buttons, permissions/scope, exceptions/recovery, notifications/audit/dependencies, conditional data/AI/algorithm contract, NFR, acceptance |
| Determinism | no unresolved “etc.”, “related operations”, “according to existing logic”, or unversioned “see attachment/prototype” shortcut |
| Field coverage | complete rows or a frozen authoritative annex with version/owner/range/count/usage; examples do not count |
| Acceptance | each function has positive and applicable validation/permission/state/dependency/regression cases with UI and domain results |

Shared module contracts must define:

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
- a module summary table, screenshot list, purpose/input/output contract, DDD overlay, Fast-Lane row, or appendix is counted as an FRR;
- a release module is labeled `FULL_SPEC` while one or more functions have no complete FRR;
- a function says “supports add/edit/delete/export” without separate actions, conditions, results, exceptions, permissions, and acceptance;
- a Reader-first index, shared contract, DDD overlay, or Fast-Lane row is used to reduce the release function denominator or skip FRR sections;
- a required FRR section is blank or replaced by “same as above”, “see prototype”, “see attachment”, or “existing logic” without an authoritative frozen mapping.

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

### 3.5 Adversarial PRD Review Protocol

Use this before sharing an L1+ PRD, prototype package, development handoff, or
customer-demo artifact with stakeholders. This is different from persona
walkthrough: the reviewer actively tries to falsify the PRD.

Run 10 attack checks and report findings by severity:

| Attack Dimension | How To Try To Break The PRD |
|---|---|
| Scope creep | Find a feature, role, state, or dependency implied by text but not in scope/out-of-scope |
| Missing role path | Pick each named role and ask: can this role start, complete, and recover from its main task? |
| Untestable acceptance | Locate any acceptance statement without Given/When/Then, visible result, and domain result |
| Boundary condition gap | Test zero data, duplicate data, max length, stale data, permission denial, timeout, and partial success |
| State-machine dead end | Find states with no allowed next action, no owner, or no closure condition |
| Data permission hole | Try horizontal/vertical overreach: another tenant, org, department, region, enterprise, patient, student, or customer |
| External dependency blind spot | Find source systems, APIs, imports, SMS, payment, AI model, or third-party pages without owner/failure behavior |
| AI overclaim | Check whether AI copy, output, or automation exceeds evidence level, write scope, or human-gate permission |
| Operational unreleasability | Look for missing migration, rollout, rollback, alert, support owner, or data reconciliation |
| Coding-agent ambiguity | Ask whether a coding agent can identify files/modules, states, APIs, AC IDs, and forbidden guesses |

Finding format:

```yaml
adversarial_prd_finding:
  id: ADV-001
  severity: P0 | P1 | P2 | P3
  attack_dimension:
  evidence:
  why_it_breaks_delivery:
  required_fix:
  owner:
  blocks: PASS | release | coding_agent | qa | customer_demo | none
```

Severity:

- `P0`: wrong/unsafe build, compliance/security/privacy/data breach, impossible
  acceptance, or core workflow cannot close.
- `P1`: development/QA/customer demo likely blocked or materially ambiguous.
- `P2`: important improvement, workaround possible.
- `P3`: wording, navigation, or maintainability issue.

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

Prototype evidence status:

| Status | Meaning |
|---|---|
| `VERIFIED` | rendered DOM/browser or deterministic audit proves the behavior and visible/domain result |
| `SPEC_ONLY` | required by PRD but not implemented in prototype/demo surface |
| `GAP` | prototype has partial or broken behavior |
| `CONFLICT` | prototype contradicts PRD/source evidence |
| `UNKNOWN` | behavior cannot be verified with available evidence |

Stage 0 role-path extraction may pass while Gate 2 or Gate 3 remains blocked. Do not relabel prototype conflicts, duplicate handlers, malformed `data-action`, missing evidence UI, or missing backend contracts as non-blocking full-PRD gaps.

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
