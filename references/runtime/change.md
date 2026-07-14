# Requirement Change Control

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
