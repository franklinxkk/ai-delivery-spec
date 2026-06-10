# AI Runtime + Operations

Use this file for AI features, LLM agents, multi-agent workflows, tool calling, observability, rollback, and operations.

## AI State Model

AI-specific states:

| State | Meaning | Entry | Exit |
|-------|---------|-------|------|
| `ai_analyzing` | AI is analyzing | data event / user request | suggestion / ambiguous / failed |
| `ai_suggestion_pending` | AI suggestion awaits human confirmation | confidence >= threshold | accepted / rejected |
| `ai_low_confidence` | confidence below threshold | confidence < threshold | manual decision / retry |
| `ai_failed` | inference failed | timeout / model / data shortage | retry / manual fallback |
| `ai_reference_expired` | referenced policy/knowledge source stale | source version changed | retry |
| `local_fallback` | edge-side local safety mode | network timeout / 5xx / circuit breaker open | reconnect + precondition recheck |

Freeze rule:
- During `ai_analyzing`, write operations on the entity are blocked except read-only viewing.
- Batch operations are blocked to avoid overwriting AI work.
- Timeout releases freeze.
- After freeze release, runtime preconditions must be rechecked.
- If entity status, permission, policy/knowledge version, or key master data changed during analysis, discard the AI result and set `ai_failed` with reason `precondition_violated`.

Every AI transition records:

```yaml
ai_state_transition:
  from: ai_analyzing
  to: ai_suggestion_pending
  timestamp: datetime
  triggered_by: system | user_id
  ai_model: string
  ai_model_version: string
  prompt_id: string
  confidence_score: float
  hallucination_score: float
  reasoning_summary: string
  referenced_policies: [string]
  referenced_data_sources: [string]
  processing_time_ms: number
```

## Edge-Fallback Gateway

Mobile, field, vehicle, safety, inspection, medical, and operational scenarios must not depend on cloud AI availability for basic continuity.

```yaml
edge_fallback_gateway:
  network_probe_timeout_ms: 3000
  fallback_transition_budget_ms: 100
  trigger:
    - network_timeout
    - model_api_5xx
    - gateway_504
    - circuit_breaker_open
    - offline_detected
  fallback_state: local_fallback
  local_engine: expression_rules | cached_policy | offline_queue | static_decision_table
  allowed_actions:
    - read_cached_data
    - save_draft_locally
    - local_validation
    - queue_for_sync
    - show_emergency_contact_or_manual_path
  forbidden_actions:
    - cloud_agent_call
    - final_decision_write
    - external_send
    - permission_change
  ui_message: "Local safe mode active"
```

Rules:

- If network probing exceeds `3000ms` or returns 5xx/504, the runtime must enter `local_fallback` within `100ms`.
- In `local_fallback`, all cloud agent calls are blocked. The UI must hand control to local deterministic rules, cached policies, or manual path.
- Local writes are drafts or offline queue items only. They need idempotency keys and must recheck permission, entity state, policy version, and master data before sync.
- When connectivity recovers, runtime does not auto-commit old AI results. It re-enters normal flow through precondition check.
- Trace logs must record fallback trigger, local rule version, offline duration, queued writes, sync result, and user-visible message.

## AI Action Governance

| AI action | Auto | Human approval | Audit | Regulation refs | Confidence |
|-----------|:---:|:---:|:---:|:---:|:---:|
| classification / scoring | yes | no | yes | optional | >=0.7 |
| anomaly detection | yes | no | yes | optional | >=0.8 |
| SQL query generation | yes | no | yes | no | n/a |
| statistics report | yes | conditional | yes | no | n/a |
| high-impact recommendation | no | required | yes | required when applicable | >=0.85 |
| service/status restriction suggestion | no | required | yes | required when applicable | >=0.90 |
| workflow task creation | no | required | yes | required when applicable | >=0.85 |
| amount/score recommendation | no | required | yes | required when applicable | >=0.90 |
| send notification | yes | conditional | yes | optional | >=0.7 |
| delete data / bypass approval / change permissions | forbidden | n/a | n/a | n/a | n/a |

Refusal rules:
- refuse requests that bypass audit, approval, data scope, or legal basis;
- refuse destructive data operations;
- refuse unsupported confidence claims;
- refuse to hide AI involvement where audit requires disclosure.

## Agent Runtime Contract

Every agent must declare:

```yaml
agent:
  id: assessment-agent
  role: 业务评估
  prompt_id: assessment_v1
  trigger_event: AssessmentRequested
  output_event: AssessmentCompleted
  write_scope: [assessment_result, ai_reasoning_log]
  forbidden_write: [master_data, final_decision]
  preconditions:
    - target_entity.status in ['active', 'pending_review']
  timeout_ms: 15000
  max_retry: 3
  retry_backoff: exponential
  idempotent_key: target_entity_id + assessment_date
  idempotent_ttl: business_event_window + max_retry_total_time + clock_skew_buffer
  idempotent_ttl_example: 24h + 7s + 5m
  fallback: manual_review_queue
```

`test-agent` is an LLM-assisted verifier, not a business writer:

```yaml
agent:
  id: test-agent
  execution_mode: llm_assisted_verifier
  prompt_id: test_validation_v1
  deterministic_runner: browser_use | playwright
  write_scope: [test_result_log]
  forbidden_write: [ALL_BUSINESS_DATA]
```

The deterministic runner performs DOM location, assertions, and screenshots. The LLM only summarizes failure cause and remediation hint.

## Event Bus

```yaml
events:
  AssessmentRequested:
    schema_version: 1.0.0
    source: cron | human_trigger
    payload: { target_entity_id: string, assessment_date: date, scope: [profile, activity, history] }
    consumers: [assessment-agent]

  AssessmentCompleted:
    schema_version: 1.0.0
    source: assessment-agent
    payload:
      target_entity_id: string
      result_level: low | medium | high | critical
      ai_reasoning: string
      confidence: float
      hallucination_score: float
    consumers:
      - workflow-agent     # if result_level >= high
      - notification-agent # if result_level >= medium
      - report-agent

  WorkflowTaskCreated:
    schema_version: 1.0.0
    source: workflow-agent
    payload: { task_id: string, target_entity_id: string, task_type: string, deadline: datetime, approved_by: string }
    consumers: [notification-agent, test-agent]

  VerificationResult:
    schema_version: 1.0.0
    source: test-agent
    payload: { test_suite_id: string, passed: boolean, failed_assertions: [string], data_drift_detected: boolean }
```

Event schema versioning rules:
- Every runtime event must include `schema_version`.
- Additive optional fields are backward-compatible minor changes.
- Required field additions, field removals, type changes, semantic changes, and consumer-breaking enum changes require a major version.
- A major version requires a consumer impact table: consumer, current version, target version, migration owner, fallback behavior.
- Producers may emit parallel versions during migration; consumers must declare the versions they accept.

Idempotency TTL rule:
- `TTL = business_event_window + max_retry_total_time + clock_skew_buffer`.
- `max_retry_total_time` is the sum of all retry backoff intervals, e.g. exponential retries `1s + 2s + 4s = 7s`.
- Use a default `clock_skew_buffer` of `5m` unless the system has stricter time sync.
- Example: a daily assessment with 3 retries has `24h + 7s + 5m`, rounded up to `25h`.

## Runtime Conflict Policy

Precondition check points:
- before agent start;
- before output event publish;
- before write_scope commit.

Conflict layers:
- tool `forbidden_combinations` blocks at API/tool-call layer;
- runtime `conflict_resolution` blocks at Agent write layer.

Rules:
- Agent may only write `write_scope`; writing `forbidden_write` is rejected and alerted.
- Business master data is human-only unless explicitly approved.
- Concurrent writes use audit-first strategy; prefer explicit lock or optimistic concurrency for regulated workflows.
- Idempotency key is checked before write.
- Validation/auth/forbidden_write errors are not retried.

## Tool Contract

Tool classes:

| Class | Side effect | Risk | Approval | Audit |
|-------|-------------|------|----------|-------|
| query | no | low | none | sampled |
| compute | no business write | low | none | sampled |
| write | yes | high | required/conditional | full |
| workflow | starts process | high | required | full |
| external | third party/data transfer | critical | required | full + alert |

Tool registration minimum:

```yaml
tool:
  name: workflow_task_create
  class: write
  allowed_when:
    - intent == "workflow_action"
    - assessment_result.result_level >= high
  requires:
    human_approval: true
    approval_by: supervisor_role
  forbidden_empty: [target_entity, task_type, deadline]
  audit: full
```

Forbidden combinations examples:
- `sql_query` containing DELETE/INSERT/UPDATE/DROP/ALTER/TRUNCATE;
- `notification_send(channel=voice_call)` by AI;
- `external_data_sync` with any business write in the same transaction.

Tool audit log:

```yaml
tool_audit_log:
  required_fields:
    - tool_name
    - called_by
    - timestamp
    - intent
    - params_hash
    - result_status
    - trace_id
  additional_for_write:
    - affected_entity_ids
    - before_snapshot_hash
    - after_snapshot_hash
    - approval_id
```

## Observability

Trace minimum:

```yaml
trace:
  trace_id: string
  session_id: string
  user_id: string
  target_entity_id: string
  timestamp: datetime
  agent_chain:
    - agent_id: string
      started_at: datetime
      completed_at: datetime
      status: success | failed | timeout | blocked
      input_event: string
      output_event: string
  tools_used:
    - tool: string
      called_at: datetime
      duration_ms: number
      result_status: string
  rag_refs: [string]
  sql_refs: [string]
  model_refs: [string]
  latency: { total_ms: number, llm_inference_ms: number, tool_execution_ms: number }
  token_usage: { input_tokens: number, output_tokens: number, total_tokens: number, estimated_cost_cny: number }
  confidence: float
  hallucination_score: float
```

Alert rules must include `executor`.

```yaml
alerts:
  - id: hallucination_spike
    condition: hallucination_rate > 0.15
    severity: critical
    executor: ai-platform
    action: trigger_prompt_rollback + notify_ai_team
    handoff: "emit RollbackRequested(prompt_id, reason, trace_id); prompt-registry owns rollback tests"

  - id: data_drift
    condition: input_distribution_shift > 0.20
    severity: warning
    executor: ai-platform
    action: retrain_trigger + notify_ds_team

  - id: circuit_breaker_open
    condition: circuit_breaker == open
    severity: critical
    executor: ops-system
    action: page_oncall + manual_reset_required
```

Executors:
- `ops-system`: on-call, scaling, circuit breaker, manual reset;
- `ai-platform`: prompt/model rollback, regression tests, retrain, RAG supplement;
- `manual`: PM/business/data science handling with owner and SLA.

Monitoring triggers events. Rollback procedure lives in `prompt-registry.yaml`.

## Circuit Breaker

```yaml
circuit_breaker:
  open_when: consecutive_failures >= 5
  cooldown: 300s
  half_open_probe_count: 3
  half_open_success_threshold: 3
  half_open_fail_action: reset_cooldown
  close_when: half_open_success_count >= half_open_success_threshold
```

Rules:
- In `open`, block new non-critical calls and use fallback.
- After cooldown, enter `half_open` and allow only `half_open_probe_count` controlled probe requests.
- If all probe requests succeed, close the breaker.
- If any probe fails, return to `open` and restart cooldown.
- Probe requests must be tagged in trace logs.

## Prompt Ops

Every LLM agent must have a prompt registry entry:

```yaml
prompt:
  prompt_id: assessment_v1
  agent: assessment-agent
  model: deepseek-v4
  owner: ai_team
  status: active
  previous_version: assessment_v0
  rollback_supported: true
  linked_test_cases: [TC-001, TC-002]
  input_schema: {}
  output_schema: {}
  constraints: { temperature: 0.1, max_tokens: 2000 }
```

Rollback is trigger -> gated execution:
1. Observability emits `RollbackRequested`.
2. Registry marks current version `rollback_pending`.
3. Previous version loads in canary/shadow.
4. Run previous version linked tests.
5. Only if all pass, switch previous version to active.
6. Any test failure keeps current active and escalates to manual decision.

Prompt coupling detection:
- read dependency graph;
- for each downstream prompt, run 100 fixed golden cases on baseline and candidate;
- compare schema-valid rate, enum distribution KL, confidence delta, label agreement;
- alert if more than 3 downstream prompts are impacted.

## AI Acceptance Checklist

- [ ] AI states and freeze rules defined.
- [ ] Edge fallback and local safe mode defined for mobile/field/weak-network scenarios.
- [ ] Human approval thresholds defined.
- [ ] Evidence chain includes model, prompt, data source, policy/knowledge refs.
- [ ] Agents declare trigger/output/write_scope/forbidden_write/fallback.
- [ ] Preconditions are rechecked before commit.
- [ ] Tool classes and audit rules defined.
- [ ] Alerts include executor and owner.
- [ ] Prompts registered with linked tests.
- [ ] Rollback is gated by tests, not direct activation.
- [ ] Test-agent is read-only against business data.
