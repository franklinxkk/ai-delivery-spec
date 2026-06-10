# Prompt Registry Integration

Use this file when a feature includes LLM prompts, agents, RAG, tool calling, AI feature injection, or AI-native runtime.

`prompt-registry.yaml` is not a side file. It is part of Stage 3.5 runtime design and Stage 5 handoff.

## Minimum Prompt Trace

| PRD Feature | Story ID | Agent/AI Feature | Prompt ID | Output Schema | Linked Test Case | Rollback Owner |
|---|---|---|---|---|---|---|

Rules:
- Every LLM-producing feature needs a prompt id.
- Every prompt id needs linked tests.
- Every prompt change needs impact surface and rollback owner.
- Prompt output schema must map to UI result and domain result.

## Stage Integration

| Stage | Prompt Work |
|---|---|
| Stage 3 | decide AI task, risk, claimed effect, human gate |
| Stage 3.5 | register prompt id, model, output schema, fallback |
| Stage 5 | map prompt to prototype action and test case |
| Stage 5.5 | add trace fields and alert signal |
| Stage 5.7 | link effect claims to evaluation card |

## Lightweight Prompt Entry

```yaml
prompt:
  id: ticket_classification_v1
  owner: ai-platform
  feature_id: CRM-TICKET-AI
  task: classify customer issue into product/course/finance/service
  model: string
  temperature: 0.2
  input_contract:
    fields: [ticket_title, ticket_content, customer_product]
    permission_scope: current_tenant
  output_schema:
    category: product | course | finance | service | unknown
    confidence: number
    rationale: string
  fallback:
    low_confidence: manual_classification
  linked_test_cases:
    - TC-AI-TICKET-001
  rollback_owner: ai-platform
```

## Fail Conditions

- Prompt exists in prose but not registry.
- Prompt output schema is not testable.
- Prompt has no linked test case.
- Prompt can write business data without runtime write policy.
- Rollback path is undefined.
