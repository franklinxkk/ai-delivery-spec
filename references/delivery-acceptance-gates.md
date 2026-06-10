# Delivery Acceptance Gates

Use this reference before final delivery of a PRD, HTML prototype, customer-demoable artifact, or development handoff package.

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

Final answer or handoff should include:

| Artifact | Required |
|---|---|
| Prototype path | Yes |
| PRD path | Yes for PRD/prototype delivery |
| Verification report | Yes |
| State-button matrix | Yes for lifecycle-heavy products |
| Interaction ledger/regression note | Yes when iterating old prototypes |
| Test handoff checklist | Yes |
| Unresolved risks | Yes, even when non-blocking |
| Human overrule log | Required if any automated check is overridden |
| System readiness record | Required before staging/pilot/production/customer demo with real data |

## 8. Common Failure Patterns

- A page has the right title but no complete user path.
- A primary button only opens a placeholder or toast.
- A list row cannot open the underlying filled/result data.
- A newly created object is not visible after creation.
- Enabled/disabled/completed states expose the wrong actions.
- AI/Excel import skips ambiguous-field confirmation.
- Enterprise and admin paths are mixed without role visibility or data isolation.
- PRD names a module but omits inputs, outputs, processing logic, and testable transitions.

## 8.5 Mobile Acceptance

When the product has mini-program, H5, app, mobile web, driver, field, learner, customer, or sales-on-phone workflows, apply `mobile-product-delivery.md` before final delivery.

Required:
- `mobile-role-path-matrix.md` follows the schema in `mobile-product-delivery.md`.
- `permission-gates.md` follows the schema in `mobile-product-delivery.md`.
- `weak-network-matrix.md` follows the schema in `mobile-product-delivery.md`.
- Mobile prototype paths demonstrate touch entry, sticky primary action, permission denial fallback, weak-network retry, and role-specific result state.
- Safety/non-interruption policy is present for driving, operating, medical, field, or safety-critical contexts.

Fail if the mobile flow can lose user input silently, requires desktop-only interaction patterns, or claims mobile delivery while only showing a shrunken desktop page.
