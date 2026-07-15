# Requirement Review, Change And Acceptance Control

Use for any modification to a baselined `REQ-*`, rule, field, page, interface,
acceptance criterion or source precedence.

## 1. Change Request

Create `CHG-*` with:

- requester, source/authority, reason and urgency;
- original baseline version and seed IDs;
- proposed before/after behavior;
- affected users/roles and requested target baseline;
- approval policy and required reviewers.

Reject an untraceable verbal change as `clarify`; do not silently edit the PRD.

## 2. Impact Traversal

Traverse both outgoing and incoming stable-ID references from every seed. At
minimum inspect:

```text
REQ, SRC, ROLE, FLOW, VIEW, REG, ACT, FLD, ENT, RULE, STATE,
API/EVT/INT, AC, TEST, DEFECT, ARUN, EVD, CHG, projection
```

Classify impacts as direct, transitive, regression-only or no-impact-with-reason.
Check permission/data scope, historical data, compatibility, migration,
reporting/caliber, reconciliation and customer contract separately.

Run:

```bash
python scripts/analyze_change_impact.py \
  --truth requirements/product-truth.yaml \
  --change requirements/changes/CHG-001.yaml \
  --output requirements/changes/CHG-001-impact.yaml
```

## 3. Diff And Version

Record field-level before/after values for machine contracts and a readable
behavior diff for reviewers. Retain the old baseline; never overwrite history.
Each accepted change increments the requirement baseline version and links the
superseded version.

## 4. Approval And Synchronization

Approval must match authority and impact. Typical reviewers are product owner,
business/customer owner, engineering, QA, data/security/compliance when
triggered. Record decision, time, conditions and evidence.

After approval, update every affected authority/export and record recipient,
artifact/version, status and timestamp. A broadcast message without artifact
version is not closed synchronization.

## 5. Regression And Closure

Update or add affected AC/tests, execute mandatory regression, link evidence and
open defects. Close only when:

- impact inventory has no unexplained orphan;
- required approvals are complete;
- all governed artifacts share the new baseline;
- mandatory regression is pass or an accountable exception is approved;
- changed consumers received the versioned update.

If any condition fails, keep `CHG-*` open and do not advertise the new baseline.

## 6. Review Closure

Bind every finding to `REV-*` and one or more `REQ-*`/behavior IDs. Record
severity, owner, disposition, resolution and evidence. P0/P1 findings must be
resolved, explicitly deferred by an authorized owner, or reported as a blocker
before baseline. Review outcome/source/scope, role and module handoffs,
permission/data/state/rules, field/integration/reconciliation, readability,
acceptance executability and traceability.

## 7. Acceptance Definition And Run

An executable `AC-*` names requirement/behavior references, preconditions,
actor/data scope, steps or input, expected visible and domain results,
negative/exception behavior and mandatory evidence.

Use `schemas/acceptance-run.schema.json`. Each `ARUN-*` records baseline,
environment, executor, item results, actual behavior, evidence, defects,
residual issues and sign-off. Item results are `pass`, `fail`, `blocked` or
`not_run`; conclusions are `accepted`, `accepted_with_conditions`, `rejected`
or `pending`. Conditional acceptance names each condition, accountable owner
and due criterion.

## 8. Reverse Trace And Evidence Honesty

For every failed item or defect, verify:

```text
ARUN item / DEFECT -> AC -> behavior ID -> REQ -> SRC / CHG
```

Classify a broken path as a missing requirement, orphan test, implementation
defect or undocumented change before disposition. Generated documents, mock
screenshots and embedded `PASS` strings are not execution proof. Record the
tool/person, time, environment, location and result; use
`REVIEW_COMPLETE_WITH_GAPS` while execution or external sign-off is pending.
