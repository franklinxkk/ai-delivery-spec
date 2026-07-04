# OA Collaborative Office Example

Use this example when a team wants to design or review an OA / collaborative
office product with workflow approval, unified todo, official document,
meeting resolution, supervision, mobile approval, knowledge, e-signature, or AI
office assistant scenarios.

## Example Prompt

```text
Use AI Delivery Spec.
We want to build an OA collaborative office system for a mid-size enterprise.
It should cover unified todo, workflow approval, official document issuing,
meeting minutes and resolution tracking, mobile approval, and an AI assistant
that can summarize documents and recommend next actions.
Guide me from rough idea to a readable Human-First PRD, and list what would be
needed if the project later becomes AI-Coding delivery.
```

## Expected Routing

```text
[TIER: Heavy] | [AI: true] | [WORKFLOW: true] | [INFO: partial]
```

- Primary entrypoint: `references/delivery-core.md`
- Advanced extension: `references/advanced-extensions.md`
- Domain module: `references/domain-oa.md`
- PRD profile: Human-First Full PRD by default
- AI contract: AI-supporting contract for summary/search/recommendation unless
  the assistant writes consequential workflow state

## Required Gates

- Stage 0.5 input clarification for rough idea.
- Stage 1 opportunity shaping.
- Stage 3.5 IA Skeleton because the scope spans multiple modules and roles.
- Gate 3 product specification and development contract.
- OA multi-module PRD quality gate.

## Review Focus

- Work item source, owner, SLA, state, and close evidence.
- Workflow node state and button matrix.
- Official document authority, version, issue, withdrawal, and archive rules.
- Org, role, field, document-level, export, mobile, API, and AI context
  permission scope.
- AI office assistant boundary: source citation, confidence, human gate,
  forbidden write, fallback, and eval cases.
