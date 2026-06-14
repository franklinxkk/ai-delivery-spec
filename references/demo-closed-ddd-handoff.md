# Demo-Closed Prototype + DDD PRD Handoff Reference

Use this reference for a requested prototype, development handoff, customer demo, or full L2/L3 delivery package. For a PRD-only request, use the PRD module and Developer Fast-Lane sections without forcing creation of a prototype.

## Contents

- Non-Negotiable Delivery Standard
- Full Package Artifacts
- Prototype Definition Of Done
- PRD Module Template
- Developer Fast-Lane
- Demo Path Contract
- Diagram Requirements
- Review Questions

## Non-Negotiable Delivery Standard

The prototype is an executable requirement. It must let a PM or pre-sales person demonstrate every core function to a customer without a backend.

The PRD contains both the complete product specification and the domain/engineering contract. Development and testing must be able to implement the same behavior without guessing fields, rules, interactions, states, permissions, exceptions, or technical entry points.

The product specification in `templates/prd-standard-template.md` is upstream. The module template below overlays DDD and implementation traceability on that specification; it must not replace or summarize away the detailed module behavior.

## Full Package Artifacts

When the user requests a full L2/L3 package, deliver at least:

1. `PROTOTYPE.html`: self-contained HTML/CSS/JS with mock data and complete user paths.
2. `PRD.md`: DDD-oriented product/development/test contract.
3. `demo-paths.json` or equivalent section in PRD: core user stories, steps, expected UI/domain result.
4. `verification-report`: browser/DOM audit result, list of passed demo paths, remaining exceptions if any.

For single-artifact or Lite requests:
- produce only the requested artifact and its applicable verification evidence;
- report missing package artifacts as gaps;
- do not silently expand a PRD-only request into a prototype build, or a prototype-only request into a full PRD.

## Prototype Definition Of Done

Must pass all:

- Top-level navigation reflects business workspaces, not every action. Workflow actions stay inside the module where users expect them.
- Every list item with “detail/progress/data/preview” can open item-level mock business data.
- Every create flow visibly creates a new mock object.
- Every edit/configuration flow mutates visible mock state.
- Every submit/review/reject/freeze flow changes a visible lifecycle state and writes a visible audit/record.
- Every primary user story has a start point, steps, visible result, and next action.
- Role switching demonstrates permission boundaries and data isolation.
- Empty, loading/processing, validation error, low-confidence AI, rejected, in-progress, completed, frozen states are represented where relevant.
- No primary action is placeholder-only, console-only, or toast-only.
- All action ids are registered and implemented.

## PRD Module Template

For each bounded context or feature module, write this engineering overlay after the complete module product specification:

### Module Name

Business purpose:
- What job does this module complete?
- Which role owns the decision?

Inputs:
- User input:
- System context:
- Upstream data:
- AI/tool/file input:
- Permission/scope:

Outputs:
- UI output:
- Domain object changes:
- Domain events:
- Notifications/audit:
- Export/report/snapshot:

Processing logic:
- Validation:
- Matching/calculation/aggregation:
- Persistence intent:
- Idempotency:
- Error/exception handling:

Business transformation logic:
- Input -> command/query:
- Command/query -> aggregate/entity/value object:
- Aggregate behavior -> state transition/domain event:
- Domain event -> downstream task/notification/snapshot:

DDD model:
- Bounded context:
- Aggregate root:
- Entities:
- Value objects:
- Domain services:
- Repository/contracts:
- Commands:
- Queries:
- Domain events:
- Policies:
- Invariants:

State machine:
- States:
- Transitions:
- Trigger:
- Guard:
- Post-action:
- Rollback/reopen path:

Sequence diagrams:
- Happy path:
- Validation failure:
- Async/AI ambiguity path:
- Permission failure:

Prototype mapping:
- `data-testid`:
- `data-action`:
- `data-state`:
- Expected visible result:
- Expected domain result:

Test cases:
- Happy path:
- Validation failure:
- Permission failure:
- State conflict:
- Batch action:
- Regression against previous prototype:

## Developer Fast-Lane

Add this compact section before development starts. It is the fixed consumption entry for Dev Lead and QA; do not force developers to hunt across a long narrative PRD.

Every row must reference the detailed module specification and, when attachments were supplied, the source evidence register. Fast-Lane is an index into authoritative behavior, not a replacement for it.

| Module / Spec Ref | Source IDs | Command/Query | Aggregate/Entity | State Before -> After | Guard/Permission | Domain Event/Audit | API/Business Contract | Prototype Action/Testid | Test Case |
|---|---|---|---|---|---|---|---|---|---|
| Customer issue ticket / M04-E | SRC-012 | `escalateTicket` command | Ticket / ResponseTask | `待客户确认` -> `已升级` | customer not satisfied; role in service/sales/boss | `TicketEscalated`, response task created | idempotency key + SLA rule | `data-action=escalate-ticket` | TC-TICKET-ESC-001 |

Fast-lane fail conditions:
- A primary prototype action has no command/query row.
- A state transition has no guard and no domain event/audit row.
- A create/submit/escalate/review action has no idempotency or duplicate-submit rule.
- Dev Lead cannot identify the aggregate and expected domain result for a primary action in under 10 minutes.
- A Fast-Lane row exists but its fields/rules/states cannot be traced to a complete module specification or authoritative source evidence.

## Demo Path Contract

Each core path should be written as:

```json
{
  "id": "DEMO-001",
  "role": "regulator",
  "story": "Create a report task from a blank template",
  "start": "report-task-list",
  "steps": [
    {"action": "click", "target": "btn-create-report-task", "expect": "modal-create-mode-blank visible"},
    {"action": "click", "target": "modal-create-mode-blank", "expect": "template-builder visible"},
    {"action": "click", "target": "builder-apply-sheet1-preset", "expect": "columns configured"},
    {"action": "click", "target": "builder-publish", "expect": "new report-task-row visible"}
  ],
  "domain_result": "ReportTemplateVersion published; ReportTask created; FillRecord generated for enterprises"
}
```

## Diagram Requirements

For a full L2/L3 development package, use Mermaid where the diagram removes implementation ambiguity. Mark non-applicable diagrams N/A with a reason instead of generating decorative diagrams.

Candidates:

- Context map when multiple bounded contexts/services interact.
- Aggregate relationship or ER model when ownership/relations are non-obvious.
- State machine for each in-scope lifecycle aggregate.
- Sequence diagram for critical async, cross-system, AI, or failure-sensitive commands.
- Flowchart for complex multi-step user stories.

## Review Questions

Before delivery, answer:

1. Can I demo every promised function without explaining “this button would later do X”?
2. Can dev infer the command/query and aggregate touched by every primary action?
3. Can QA turn every user story into step-by-step tests with concrete expected results?
4. Does the PRD describe what changes when state changes, who can trigger it, and what audit/event is written?
5. Did the new prototype preserve the old prototype’s critical workflows, or explicitly de-scope them?

If any answer is no, revise before final delivery.
