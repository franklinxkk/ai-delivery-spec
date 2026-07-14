# Unified Requirement Handoff

## Default Projection

Deliver one governed PRD by default. The document has two reading layers:

1. a Human-First main body that business, product, design, development and QA
   can read in order;
2. engineering and machine annexes in the same file for fields, states, APIs,
   traceability and executable acceptance.

Do not create independent “Human PRD” and “AI Coding PRD” documents unless a
consumer explicitly requires a separate export. Parallel PRDs drift, create
review fatigue and make it unclear which one development should implement.

Use `references/templates/unified-requirement-prd-template.md` as the default.

## Consumer Views

| Consumer | Primary reading path | Optional export |
|---|---|---|
| customer/business | goals, scope, role journeys, business flows, acceptance | customer contract summary |
| product/design | full main body and page interactions | prototype/IA index |
| traditional development | main body then fields/states/interfaces annex | field/API extracts |
| QA | role journeys, exceptions, AC and trace index | executable acceptance list |
| Coding Agent | complete document plus machine annex | YAML/JSON slice if tool requires it |

All exports preserve stable IDs and baseline version. An export is generated
from the baseline; it never becomes a second authority.

## Handoff Gate

The receiving role must be able to proceed without inventing:

- who may act and which data they may access;
- trigger, precondition, happy path, branch, failure and recovery;
- field meaning, validation, edit authority and sensitivity;
- state transition, rule precedence and concurrency/idempotency behavior;
- integration input/output/error/reconciliation behavior;
- acceptance result and required evidence.

Technical implementation choices remain with engineering unless the choice is
a customer-visible, interoperability, security, compliance or acceptance
contract.

## Prototype Handoff

Map stable IDs to `data-testid`, `data-action`, `data-field`, `data-state`, and
`data-api`. Every action needs a handler and visible outcome. Compare the role,
view, action, modal, handler and representative data coverage against the
approved baseline; a visually polished regression is still a failed handoff.

## Change Handoff

A changed baseline is not ready until the change package names affected IDs,
before/after behavior, approvals, synchronized consumers, updated artifacts and
regression evidence. Notify only the affected consumers, but retain the audit
record for all baseline changes.
