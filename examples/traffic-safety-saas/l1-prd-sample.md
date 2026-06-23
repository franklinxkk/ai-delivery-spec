# L1 PRD Sample: Hidden Danger Rectification Notice

This is a beginner-friendly L1 sample. It is complete enough for internal
alignment, but it should be upgraded to L2 before formal development handoff.

## 1. Version

| Field | Value |
|---|---|
| Feature / Module | Hidden Danger Rectification Notice |
| Version | v0.1 |
| Owner | Product Manager |
| Date | 2026-06-19 |
| Reviewers | PM / Dev / QA / Regulator Sponsor |

## 2. Background

Current situation:

Local transportation regulators inspect enterprises and find safety problems.
Some findings are recorded offline or spread across messages, making follow-up
and audit evidence weak.

User / business problem:

Regulators need a simple way to issue a rectification notice, track enterprise
response, and prove that daily supervision work was performed.

Why now:

Hidden danger remediation is a high-frequency regulated workflow. A minimal
closed loop can reduce missed follow-up and make later mobile inspection,
notices, and statistics easier to connect.

## 3. Goal And Non-Goal

Goal:

Regulators can create, issue, track, return, and accept a hidden-danger
rectification record. Enterprises can receive the notice, upload rectification
evidence, and see the result.

Success signal:

For a pilot county, more than 90% of issued hidden dangers have a visible
status, deadline, responsible enterprise, evidence, and audit record.

Out of scope:

- Administrative punishment, license revocation, or external enforcement.
- AI automatic classification of major hidden dangers.
- Cross-city/province command dispatch.

## 4. Users And Roles

| Role | Scenario | Pain / Need | Permission Boundary |
|---|---|---|---|
| County regulator | Issues and tracks hidden dangers | Needs audit trail and overdue visibility | Can manage enterprises within authorized scope only |
| Enterprise safety manager | Receives and rectifies hidden dangers | Needs clear deadline and evidence requirements | Can view and submit records for own enterprise only |
| Regulator supervisor | Reviews overdue and acceptance statistics | Needs ranking and accountability view | Can view subordinate departments based on data scope |

## 5. Scope

In scope:

- Hidden danger list with status, enterprise, source, level, deadline, and overdue flag.
- Create and issue hidden danger to one enterprise.
- Enterprise evidence submission.
- Regulator acceptance pass or return.
- Audit records for create, issue, submit, accept, return, delete.

Not included in this version:

- Batch import from external government documents.
- Mobile offline inspection.
- SMS cost switch and WeChat sharing.

## 6. User Stories

| Story ID | Role | User Story | Acceptance Criteria | Test Case |
|---|---|---|---|---|
| US-001 | County regulator | As a regulator, I want to issue a hidden danger notice so that the enterprise must rectify it before a deadline. | Given required fields are valid, when I click Issue, then the record becomes `issued`, appears in the enterprise pending list, and writes an audit log. | TC-001 |
| US-002 | Enterprise safety manager | As an enterprise manager, I want to upload evidence so that the regulator can review my rectification. | Given the record is `issued` or `returned`, when I submit evidence, then the status becomes `submitted_for_acceptance` and the regulator receives a pending review item. | TC-002 |
| US-003 | County regulator | As a regulator, I want to return insufficient evidence so that the enterprise can correct it. | Given the record is `submitted_for_acceptance`, when I click Return and enter a reason, then the status becomes `returned` and the enterprise can resubmit. | TC-003 |
| US-004 | Regulator supervisor | As a supervisor, I want to see overdue records so that I can follow up with responsible departments. | Given the deadline has passed and the record is not accepted, then the list marks it as overdue and includes it in overdue statistics. | TC-004 |

## 7. Core Flow

```text
entry -> action -> visible result -> domain result -> next action
```

| Step | Flow Sentence |
|---|---|
| 1 | The regulator enters from the hidden-danger list, clicks `New Hidden Danger`, the system opens a creation form, and prepares a `HiddenDanger` draft. |
| 2 | The regulator fills enterprise, source, level, problem description, deadline, and evidence requirement, then clicks `Issue`; the system shows a success toast and writes `HiddenDanger.status = issued`. |
| 3 | The enterprise enters from its pending rectification list, clicks `Submit Evidence`, the system opens an evidence form, and updates the record to `submitted_for_acceptance`. |
| 4 | The regulator enters from pending acceptance, clicks `Accept`, the system shows the accepted state and writes `HiddenDanger.status = accepted`. |
| 5 | If evidence is insufficient, the regulator clicks `Return`, the system requires a return reason and writes `HiddenDanger.status = returned`. |

## 8. State And Actions

| Object | State | Visible Actions | Forbidden Actions | Domain Result |
|---|---|---|---|---|
| HiddenDanger | draft | save, issue, delete | submit evidence, accept | record not visible to enterprise |
| HiddenDanger | issued | view, urge, enterprise submit evidence | edit core fields, delete physically | enterprise pending task exists |
| HiddenDanger | submitted_for_acceptance | accept, return, view evidence | enterprise edit evidence | acceptance task exists |
| HiddenDanger | returned | enterprise resubmit, view return reason | regulator accept before resubmission | return reason recorded |
| HiddenDanger | accepted | view, export, logical delete | edit, submit, return | closure timestamp and reviewer recorded |
| HiddenDanger | overdue | urge, call record, view | auto-close | overdue flag included in statistics |

## 9. Prototype / Screen Notes

Prototype path:

Not included in this L1 sample. If a prototype is created, use stable
`data-testid` and `data-action` for list, create, issue, submit, accept, return,
and export operations.

Primary actions:

| Screen | data-testid | data-action | Expected Result |
|---|---|---|---|
| Hidden danger list | `table-hidden-danger` | `filter-hidden-danger` | Table refreshes and count updates |
| New form | `btn-issue-hidden-danger` | `issue-hidden-danger` | Status becomes `issued`; enterprise task appears |
| Enterprise evidence form | `btn-submit-evidence` | `submit-evidence` | Status becomes `submitted_for_acceptance` |
| Acceptance detail | `btn-accept-hidden-danger` | `accept-hidden-danger` | Status becomes `accepted` |
| Acceptance detail | `btn-return-hidden-danger` | `return-hidden-danger` | Return reason required; status becomes `returned` |

## 10. Risks And Open Questions

| Item | Type | Owner | Decision Needed |
|---|---|---|---|
| Hidden danger level | question | Sponsor | Which levels require mandatory acceptance review? |
| Evidence standard | risk | PM + QA | What minimum photo/file/text evidence is required? |
| Data scope | risk | Dev | How to prevent a regulator from viewing enterprises outside authorized scope? |
| Notification cost | question | Sponsor | Is SMS enabled for this region or only in-system notification? |

## 11. Acceptance

- [x] Role path can be walked through.
- [x] Every primary action has visible result.
- [x] Every state-changing action has domain result.
- [x] Known gaps are listed.
- [ ] If moving to development, upgrade to L2 Standard PRD with full FRR,
  permission rules, field validation, notification rules, and traceability.
