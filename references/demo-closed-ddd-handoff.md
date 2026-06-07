# Demo-Closed Prototype + DDD PRD Handoff Reference

Use this reference whenever the user asks for a PRD, prototype HTML, product handoff, development handoff, customer demo prototype, or prototype iteration from an existing HTML.

## Non-Negotiable Delivery Standard

The prototype is an executable requirement. It must let a PM or pre-sales person demonstrate every core function to a customer without a backend.

The PRD is the domain contract. It must let development and testing implement the same behavior without guessing business rules.

## Required Artifact Package

Deliver at least:

1. `PROTOTYPE.html`: self-contained HTML/CSS/JS with mock data and complete user paths.
2. `PRD.md`: DDD-oriented product/development/test contract.
3. `demo-paths.json` or equivalent section in PRD: core user stories, steps, expected UI/domain result.
4. `verification-report`: browser/DOM audit result, list of passed demo paths, remaining exceptions if any.

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

For each bounded context or feature module, write:

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

Test cases:
- Happy path:
- Validation failure:
- Permission failure:
- State conflict:
- Batch action:
- Regression against previous prototype:

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

## Mandatory Diagrams

Use Mermaid for:

- Context map.
- Aggregate relationship or ER model.
- State machine for each lifecycle aggregate.
- Sequence diagram for each critical command.
- Flowchart for each multi-step user story.

## Review Questions

Before delivery, answer:

1. Can I demo every promised function without explaining “this button would later do X”?
2. Can dev infer the command/query and aggregate touched by every primary action?
3. Can QA turn every user story into step-by-step tests with concrete expected results?
4. Does the PRD describe what changes when state changes, who can trigger it, and what audit/event is written?
5. Did the new prototype preserve the old prototype’s critical workflows, or explicitly de-scope them?

If any answer is no, revise before final delivery.
