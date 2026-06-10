# AI Feature Injection

Use this file when AI is embedded into a normal product but does not redesign or own the whole business workflow. Examples: AI classification, extraction, summarization, draft generation, risk hint, document review, ticket routing, report narrative.

Do not use the full AI Native Harness unless AI output triggers autonomous workflow writes/actions, high-risk recommendations, compliance/safety/money impact, or multi-agent orchestration.

## Lightweight Contract

```yaml
ai_feature_injection:
  feature_id: string
  host_workflow: string
  ai_task: classify | extract | summarize | recommend | draft | review | rank | generate
  input_context:
    user_input: []
    business_records: []
    knowledge_sources: []
  output:
    schema: {}
    confidence_required: number
    citations_required: true | false
  human_gate:
    required: true | false
    reviewer_role: string
  write_policy:
    ai_can_write: none | draft_only | suggestion_only | auto_write_low_risk
    forbidden_write: []
  fallback:
    low_confidence: string
    timeout: string
    source_missing: string
  linked_tests: []
  prompt_id: string
```

## Minimum Gates

| Area | Required |
|---|---|
| Context | source, freshness, permission scope |
| Output | schema, confidence, citation/evidence when needed |
| UI | distinguish AI suggestion from confirmed business data |
| Human review | required for high-impact changes |
| Fallback | low confidence, timeout, empty context |
| Prompt ops | prompt id, linked tests, rollback owner |
| Acceptance | golden cases + adversarial/edge cases |

## Escalate to AI Native When

- AI output creates or changes workflow tasks automatically.
- AI writes final business state.
- AI chains multiple tools/agents.
- AI affects compliance, money, safety, customer commitment, punishment, or service restriction.
- The PM claims measurable business effect beyond output quality.

## Prototype Requirements

- AI output must have visible confidence/evidence or "needs review" state.
- Low-confidence and failure states must be demoable.
- Accept/reject/edit actions must mutate mock state.
- The user must be able to see what AI used and what it did not know.

## Test Cases

| Case | Expected Result |
|---|---|
| normal input | valid AI output, confidence shown |
| ambiguous input | low-confidence state + review |
| missing source | explain missing context, no fabricated result |
| permission-limited user | AI cannot use hidden data |
| prompt regression | linked test catches schema/quality drift |
