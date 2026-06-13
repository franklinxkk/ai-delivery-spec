# Artifact Packaging Standard

Use this file when delivering a bid package, customer demo package, internal dev handoff, review archive, or release package.

## Package Types

| Package | Purpose | Required Contents |
|---|---|---|
| Exploration Demo | stakeholder discussion | prototype, demo path notes, known gaps |
| Internal Development | implementation and testing | PRD, prototype, story matrix, state-button matrix, Developer Fast-Lane, acceptance tests |
| Customer Demo | sales/pre-sales/customer validation | self-contained prototype, demo script, sample data, de-scope notes |
| Bid / Proposal | external formal delivery | service plan, architecture, PRD, prototype, user stories, screenshots, assumptions |
| AI Runtime Package | AI production readiness | runtime contract, prompt registry, tool policy, eval set, observability, rollback |
| Verification / UAT | test and business acceptance | test plan/cases, traceability matrix, evidence, defect disposition, acceptance decision |
| Release / Pilot | controlled rollout and operations | release scope, readiness record, migration, observability, rollback, support/runbook |
| Retirement / Exit | safe deprecation or shutdown | dependency/customer inventory, migration/export, retention/deletion, notice, closure evidence |

## Manifest

```yaml
delivery_package:
  name: string
  type: exploration | dev | customer_demo | bid | ai_runtime | verification | release | retirement
  version: string
  tier: L0 | L1 | L2 | L3
  artifacts:
    - path: string
      purpose: string
      owner: string
  verified_paths: []
  known_gaps: []
  de_scopes: []
  next_actions: []
```

## Packaging Rules

- Customer-demo prototypes must be self-contained or state external dependencies.
- Bid packages need assumptions, exclusions, and implementation boundary.
- Internal dev packages need Developer Fast-Lane and test cases.
- AI runtime packages need rollback and on-call owner.
- Verification packages need reproducible evidence and unresolved-defect disposition.
- Release packages need readiness decision, rollout/rollback, monitoring, and support ownership.
- Retirement packages need migration/export, retention/deletion, customer communication, dependency closure, and shutdown evidence.
- Every package needs version, owner, and date.

## Final Answer Checklist

When handing over, include:
- package type and tier;
- artifact paths;
- verification performed;
- unresolved risks;
- next decision needed.
