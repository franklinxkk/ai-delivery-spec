# Example: Traffic Safety SaaS

## Scenario

A transportation safety SaaS platform serves local regulators and transport
enterprises. It manages enterprises, vehicles, drivers, safety training,
inspection, notices, meetings, hidden danger remediation, and data reports.

## Input Prompt

```text
Use AI Delivery Spec to review this traffic safety SaaS PRD.

The product has PC regulator console, enterprise console, and mini-program
field workflows. It must support role-based data scope, notices requiring
reading/signature, offline inspection, hidden danger remediation, and
regulatory audit trails.

Output a development-ready PRD review, missing decisions, mobile acceptance
checklist, and E2E cross-module matrix.
```

## Expected 0D Triage

```text
[TIER: Heavy] | [AI: false] | [WORKFLOW: true]
```

If AI inspection, AI data extraction, or AI report generation is in scope,
classify the affected modules separately as AI-supporting or AI-core.

## References To Load

- `SKILL.md`
- `references/delivery-core.md`
- `references/prototype-testability.md`
- `references/advanced-extensions.md`
- `references/domain-traffic.md`
- `references/domain-traffic-safety-scenarios.md`
- `references/mobile-product-delivery.md`
- `references/multi-surface-consistency.md`

## Gate Focus

- PC/mini-program surface consistency.
- Data-scope rules across province, city, county, department, and enterprise.
- Hidden danger source and remediation lifecycle.
- Notice read/sign/receipt rules.
- Offline field inspection and audit evidence.
- Report metric lineage and indicator ownership.

## Common P0 Decisions

- Which regulator level can edit enterprise data?
- What happens when enterprise data conflicts with imported transport bureau data?
- Which hidden dangers require acceptance review?
- What evidence is required for major hidden dangers?
- Which notices require signature, receipt, or forced reading duration?
- Which SMS or WeChat notifications cost money and need regional switches?
