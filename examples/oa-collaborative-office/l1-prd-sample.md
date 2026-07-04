# L1 PRD Sample: OA Unified Todo And Workflow Approval

## 1. Outcome

Reduce missed approvals and untraceable office work by unifying workflow todos,
mobile approval, and overdue supervision into one accountable work center.

## 2. Users And Roles

| Role | Goal | Key Risk |
|---|---|---|
| Employee | submit requests and handle assigned todos | unclear state or lost draft |
| Department Manager | approve, return, or assign work on time | stale todo and duplicate approval |
| Workflow Admin | configure workflow versions and SLA | running instances affected by template changes |
| Auditor | inspect approval, export, and permission evidence | incomplete audit chain |

## 3. Scope

In scope:

- unified todo list for workflow items;
- workflow submit, approve, return, reject, and complete;
- mobile approval with weak-network draft;
- overdue reminder and escalation;
- AI summary of approval context as a draft only.

Out of scope for L1:

- official document issuing;
- e-signature/seal;
- low-code workflow designer;
- cross-company federation.

## 4. Core Flow

User from `page-portal` opens `table-unified-todo`, selects a pending approval,
reviews form data, history, attachments, and AI-generated context summary, then
clicks `btn-approve` or `btn-return`. The system validates current node state,
role permission, delegation, and stale-state guard before writing the decision
and closing or forwarding the todo.

## 5. State Machine

```text
WorkflowInstance: draft -> running -> completed
WorkflowInstance: running -> returned -> running
WorkflowInstance: running -> rejected | terminated
WorkflowNode: pending -> processed
WorkflowNode: pending -> timeout -> escalated -> processed
WorkItem: pending -> read -> processing -> closed
WorkItem: pending -> overdue -> escalated -> closed
```

## 6. Functional Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| OA-F01 | The todo center shall show pending, overdue, and processed work items by authorized scope. | A manager cannot see another department's confidential item without scope. |
| OA-F02 | The approval detail shall show applicant, current node, form fields, opinion history, attachments, SLA, and AI summary citation. | AI summary is hidden or marked unavailable when source permission fails. |
| OA-F03 | Approve/return/reject actions shall validate current node state before writing. | A stale todo action is blocked and refreshes state. |
| OA-F04 | Mobile approval shall preserve draft opinion during weak network but must not finalize until server validation. | No duplicate approval is created after retry. |
| OA-F05 | Overdue todos shall create reminder/escalation evidence with owner and close guard. | Supervision dashboard can drill into source workflow. |

## 7. AI Boundary

AI may summarize approval context and recommend next action with source
citations. AI must not approve, reject, return, sign, seal, archive, or change
workflow state without accountable human confirmation.

## 8. Test Scenarios

| Scenario | Expected Result |
|---|---|
| Manager approves a valid pending todo | node processed; next todo created or workflow completed |
| Manager acts on stale todo | action blocked; current state refreshed |
| User lacks document permission | sensitive fields and AI source summary are hidden |
| Mobile network fails before submit | draft opinion preserved; no business state written |
| SLA expires | overdue state and escalation record created |

## 9. Completion State

`REVIEW_COMPLETE_WITH_GAPS`: L1 scope is clear. Before L2 development handoff,
lock IA Skeleton, global field dictionary, permission matrix, API contract,
and AC-YAML.
