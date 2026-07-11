---
name: Domain Pack Proposal
about: Propose professional knowledge that may deserve a reusable domain pack
title: "[Domain] "
labels: ["domain-pack", "needs-evidence"]
assignees: []
---

## Domain And Product Boundary

What business objects and lifecycle make this a domain rather than a generic
capability? When should the pack not trigger?

## Reuse Evidence

Which projects/scenarios show that the knowledge is reusable beyond one customer?

## Core Model

- Roles and accountable decisions:
- Entities and state owners:
- Core and exception workflows:
- Permissions/privacy/high-risk boundaries:
- Metrics and acceptance evidence:

## Sources

List authoritative/accountable sources, jurisdiction/applicability, version,
status, verification date, and owner. Do not paste protected full text.

## Proposed Coverage

```yaml
knowledge: absent | partial | structured | sourced
scenarios: absent | mocked | project_sampled | multi_project
behavioral_eval: not_run | failed | partial | passed
expert_review: not_reviewed | reviewed_with_gaps | reviewed
maturity: experimental | validated | audited
```

## Known Gaps And Forbidden Claims

What must users still verify? What production claim must not be made?

## Privacy And Rights

Confirm that proposed examples contain no private customer data, secrets,
personal data, or protected standards/research copied in full.
