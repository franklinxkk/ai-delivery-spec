# Example: CRM Response Center

## Scenario

A SaaS company needs a CRM response center that prevents missed leads, delayed
customer issue handling, invisible product feedback, and overdue payments.

## Input Prompt

```text
Use AI Delivery Spec to turn this CRM prototype into a development-ready PRD.

The system must support boss, sales, customer service, product/R&D, finance,
and channel partner roles.

Core lifecycle:
lead -> opportunity -> customer -> contract/payment
customer issue -> ticket -> demand -> iteration -> release feedback
partner feedback -> sales follow-up -> closed response task

Output a readable PRD, role-path matrix, E2E lifecycle matrix, acceptance
criteria, and unresolved decisions.
```

## Expected 0D Triage

```text
[TIER: Heavy] | [AI: false] | [WORKFLOW: true]
```

## References To Load

- `SKILL.md`
- `references/delivery-core.md`
- `references/prototype-testability.md` if an executable prototype is provided
- `references/advanced-extensions.md` for SaaS/RBAC/workflow triggers
- `references/domain-crm.md`
- `references/readability-layer.md`
- `references/templates/human-first-prd-template.md`

## Required Artifacts

| Artifact | Purpose |
|---|---|
| PRD | Human-readable product specification |
| Role path matrix | Boss, sales, CS, R&D, finance, partner paths |
| E2E lifecycle matrix | Cross-module events and state transitions |
| Development handoff | Aggregates, states, commands, events, policies |
| QA acceptance matrix | Story, path, selector, state result, domain result |
| Gap list | Decisions needed before production development |

Sample output: [L1 PRD sample](l1-prd-sample.md).

## Gate Focus

- Gate 1: every role has a complete operating path.
- Gate 2: prototype actions are not toast-only.
- Gate 3: PRD includes development contract, not only feature names.
- Gate 4: unresolved P0 decisions are explicit.

## Common P0 Decisions

- What is the difference between supplier, partner, and channel agent?
- What are the RBAC and data-scope rules?
- How is lead assignment calculated when sales capacity is saturated?
- What is the contract/payment source of truth?
- When does a ticket become a product demand?
- How is release feedback sent back to customer service and sales?
