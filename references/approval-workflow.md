# Approval Workflow Pattern

Use this file for ToB/ToG approval, review, audit, escalation, acceptance, rectification, demand review, contract approval, ticket escalation, or multi-level regulatory workflows.

## Approval Model

```yaml
approval_workflow:
  object: string
  requester_roles: []
  approver_roles: []
  modes: sequential | parallel_all | parallel_any | countersign | conditional
  states:
    - draft
    - submitted
    - under_review
    - returned
    - approved
    - rejected
    - withdrawn
    - expired
  actions:
    submit: {}
    approve: {}
    reject: {}
    return: {}
    transfer: {}
    withdraw: {}
    timeout_action: {}
```

## Required State-Button Matrix

| State | Visible Actions | Forbidden Actions | Guard | Domain Event |
|---|---|---|---|---|
| draft | submit, edit, delete | approve, reject | owner | DraftSubmitted |
| submitted | withdraw, view | edit, delete | requester | ApprovalWithdrawn |
| under_review | approve, reject, return, transfer | delete | current approver | ApprovalDecided |
| returned | edit, resubmit | approve | owner | ApprovalResubmitted |
| approved | view, archive | edit, delete | permission | ApprovalCompleted |

## Approval Rules

- Every approval step needs owner role, SLA, timeout behavior, and audit log.
- Transfer/reassign must preserve original approver and reason.
- Withdraw is allowed only before final approval unless policy says otherwise.
- Return/reject must capture reason and next allowed state.
- Timeout behavior must be explicit: remind, escalate, auto approve, auto reject, or manual queue.
- Approval history is immutable.

## ToG Multi-Level Pattern

For regulatory hierarchy:

```text
province -> city -> district/county -> enterprise
```

Define:
- data visibility by level;
- who can assign/return/accept;
- whether upper level can override;
- evidence snapshot required at each state.

## Test Cases

| Case | Expected Domain Result |
|---|---|
| sequential approval happy path | all steps approved; object final approved |
| return and resubmit | returned reason recorded; new version submitted |
| withdraw | workflow closed; approver cannot approve old request |
| transfer | new approver active; audit keeps old approver |
| timeout | configured timeout action triggered |
