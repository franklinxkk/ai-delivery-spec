# Workflow Automation / Low-Code Delivery

Use this reference when the product contains a visual workflow builder, low-code app builder, connector marketplace, integration automation, or node-based AI/non-AI orchestration.

This gate is inspired by products such as n8n, Dify, Flowise, Activepieces, NocoBase, Appsmith, ToolJet, and Budibase. It applies before AI Native Harness when the workflow itself is the product contract.

## 1. Trigger

Load this file when any of these are true:

- users create workflows through nodes, steps, cards, forms, or visual canvas;
- the product connects third-party systems, internal APIs, databases, files, models, or message channels;
- users configure triggers, routers, conditions, loops, approvals, retries, or schedules;
- workflows can be published, versioned, tested, replayed, rolled back, or shared as templates;
- the main risk is connector behavior, credential safety, execution reliability, or workflow drift.

## 2. Core Objects

| Object | Meaning | Required Contract |
|---|---|---|
| Workflow | Executable graph or ordered automation | owner, tenant, version, status, trigger, nodes, edges, permissions |
| Node | Atomic step | type, input schema, output schema, side effect, timeout, retry, idempotency |
| Edge | Flow relation | source, target, condition, error route |
| Trigger | Workflow start | manual, schedule, webhook, event, message, form submit, AI intent |
| Connector | External/internal capability | auth type, scopes, rate limit, sandbox mode, data sensitivity |
| Credential | Secret or token | owner, tenant, rotation, masking, access guard |
| Execution | One workflow run | version snapshot, node traces, status, logs, error, replay eligibility |
| Template | Reusable workflow/app | variables, required credentials, import guard, test fixture |
| Environment | dev/test/prod boundary | config, credentials, publish permission, audit |

## 3. Workflow State Machines

Workflow definition:

```text
draft -> testing -> published -> paused -> archived
draft -> discarded
published -> draft_revision
published -> disabled_by_policy
```

Execution run:

```text
queued -> running -> succeeded
queued -> cancelled
running -> waiting_for_human
running -> retrying -> running
running -> failed
waiting_for_human -> running
waiting_for_human -> expired
failed -> replayed
```

Rules:

- A running execution must use a version snapshot. Editing the workflow cannot mutate in-flight execution semantics.
- A published workflow must have at least one successful test run or an approved exception.
- A failed node must expose error, input summary, output summary, retry eligibility, and next action.
- Human approval nodes must define timeout, assignee, escalation, and audit event.

## 4. Node Contract

Each node type must define:

```yaml
node_type: string
category: trigger | action | condition | router | loop | approval | ai | tool | data_transform
input_schema: object
output_schema: object
side_effect: none | read | write | external_send | money | compliance | safety
credential_required: true | false
credential_scope: string
timeout_seconds: number
retry_policy:
  max_attempts: number
  backoff: fixed | exponential
idempotency_key: required | optional | not_applicable
test_fixture: sample input/output and expected visible result
error_routes: default failure path and optional custom branches
```

Acceptance:

- every node shown in prototype has config panel, validation state, test action, and visible result;
- every side-effect node has permission guard and audit event;
- every connector node declares credential and data sensitivity;
- every AI node also references AI Feature Injection or AI Native Harness according to risk.

## 5. Connector And Credential Safety

Minimum connector registry fields:

```yaml
connector_id:
display_name:
auth_type: none | api_key | oauth2 | basic | service_account | internal_token
scopes:
rate_limit:
sandbox_supported: true | false
data_sensitivity: public | internal | confidential | regulated
operations:
  - operation_id:
    input_schema:
    output_schema:
    side_effect:
    test_mode_behavior:
```

Rules:

- Secrets must never appear in prototype mock data, logs, traces, exported templates, or generated PRD examples.
- Execution logs should show redacted summaries by default and require elevated permission for raw payload inspection.
- Production credentials cannot be used in test mode unless explicitly approved.

## 6. PRD Additions

When this gate triggers, add these sections to PRD or module handoff:

1. Workflow inventory: workflows, owners, triggers, business outcomes.
2. Node catalog: trigger/action/condition/approval/AI/tool/data nodes.
3. Connector registry: auth, scopes, operations, rate limits, sandbox support.
4. Execution reliability: retry, idempotency, timeout, replay, dead-letter handling.
5. Versioning and release: draft/test/publish/rollback rules.
6. Permission and tenancy: who can build, publish, execute, inspect logs, manage credentials.
7. Trace and audit: execution history, node traces, redaction, export.
8. Template packaging: variables, import checklist, required credentials, sample data.

## 7. Prototype Requirements

For L1:

- workflow list;
- canvas or ordered step editor;
- node config panel;
- manual test run;
- execution result page or modal.

For L2/L3:

- version status badge;
- publish and rollback behavior;
- at least one success path, one failed-node path, one retry/replay path;
- credential missing/expired state;
- execution history and node-level trace;
- permission boundary for builder vs operator vs auditor.

Required testids:

```text
workflow-list
btn-create-workflow
workflow-canvas
node-{node_type}-{index}
node-config-panel
btn-test-node
btn-test-workflow
btn-publish-workflow
execution-history
execution-trace
credential-status
```

## 8. Acceptance Checklist

| Check | Pass Rule |
|---|---|
| Workflow graph closed | Every node has input/output and every edge has condition or default route |
| Test run exists | Published workflow has successful test run or approved exception |
| Version snapshot | Execution references immutable workflow version |
| Credential safe | No secret leaks in logs/templates/prototype |
| Retry/idempotency | Side-effect nodes define retry and idempotency behavior |
| Traceable failure | Failed execution shows failed node, reason, and next action |
| Permission closed | Builder/operator/auditor/admin boundaries are explicit |
| AI risk routed | AI node triggers AI Feature Injection or AI Native Harness as needed |

## 9. Relationship To Other Gates

- Use `ai-feature-injection.md` when a workflow node performs bounded AI classification, extraction, summary, recommendation, or review.
- Use `ai-native-harness-engineering.md` when AI chooses tools, changes workflow path, writes business state, or acts autonomously.
- Use `saas-multitenancy.md` when workflows are tenant-scoped or shared across organizations.
- Use `approval-workflow.md` for human approval nodes and escalation.
- Use `build-governance.md` when workflows are generated or patched through scripts.
