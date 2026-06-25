# Coding Agent Compatibility

Load this file when the output will be consumed by a coding agent such as
Claude Code, Cursor, GitHub Copilot coding agent / Workspace, Devin, or a
similar implementation agent. Also load it when the user asks to generate
`AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, `.cursorrules`, test scaffolding, or
machine-readable acceptance criteria.

## Contents

- When To Load
- Structured Acceptance Criteria (AC-YAML)
- Machine-Readable AI Runtime Contract
- Prototype Data-Attribute Contract
- Delivery Package Layout
- Agent Entrypoint Generation
- Coding Agent Handoff Prompt

## When To Load

Load this file in addition to `delivery-core.md` when any trigger applies:

| Trigger | Action |
|---|---|
| User asks to generate `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, or `.cursorrules` | Load full file |
| User asks to convert PRD acceptance criteria into test cases or test stubs | Load AC-YAML section |
| User asks to generate `ai_runtime_contract` in YAML or JSON | Load Machine-Readable AI Runtime Contract section |
| PRD will be handed off to a coding agent for implementation | Load Coding Agent Handoff Prompt section |
| User asks to validate prototype `data-*` attribute coverage | Load Prototype Data-Attribute Contract section |

Do not load this file for human-only PRD review, Stage 0 triage, or L0
prototype exploration.

## Structured Acceptance Criteria (AC-YAML)

FRR section 16 in `delivery-core.md` remains human-readable prose first. For coding
agent handoff, add a machine-parseable `ac_structured` block immediately after
the prose acceptance table. This block is additive and does not replace the
human acceptance section.

```yaml
ac_structured:
  - id: AC-M04-F01-001
    frr_ref: M04-F01
    type: happy_path
    priority: P0
    status: active
    revision: 1
    given: "The user is logged in as a sales representative and at least one lead is in draft state."
    when: "The user clicks the Submit For Review button."
    then:
      ui: "The button becomes disabled and the page shows a submitted-for-review toast."
      domain: "The lead state changes from draft to pending_review and an audit_log entry is written."
      sla: "UI response <= 300ms; server write <= 1s."
    test_type: integration
    data_testid: "btn-submit-review"
    data_action: "lead.submitReview"
    skip_reason: null
```

ID convention:

```text
AC-{ModuleID}-{FunctionID}-{SequenceNumber}
AC-{ModuleID}-SHARED-{SequenceNumber}
```

Rules:

- Module and Function IDs must match FRR section 1 function inventory.
- Sequence numbers are stable after assignment; do not renumber old ACs.
- Do not add version suffixes to AC IDs. Use `revision`, `status`,
  `supersedes`, and `replaced_by` metadata when behavior changes.
- `priority: P0` is smoke; `P1` is regression; `P2` is long-tail/adversarial.
- `test_type` is one of `unit`, `integration`, `e2e`, `contract`, `manual`.
- If automation is intentionally skipped, set `skip_reason`; do not omit the AC.

### AC ID Evolution Rules

Use these rules when FRRs change after AC IDs have been assigned:

| Change | Rule |
|---|---|
| Add a new case to the same function | Append the next sequence number, for example `AC-M04-F01-004`. |
| Split one function into several functions | Keep unchanged ACs in place only if the original FRR remains valid. For behavior moved to a new function, create new AC IDs under the new Function ID and mark old ACs `status: moved` with `replaced_by`. |
| Merge several functions | Keep still-valid AC IDs active and update `frr_ref` only when the merged function becomes the authoritative FRR. Mark duplicate or obsolete ACs `status: deprecated` with `replaced_by`. |
| Clarify wording without changing expected UI/domain result | Keep the same AC ID and increment `revision`. |
| Change expected UI/domain result, permission, state transition, or SLA | Create a new AC ID, mark the old one `status: superseded`, and link it with `replaced_by` / `supersedes`. |
| Remove a function from release scope | Keep historical AC IDs in the PRD appendix or manifest as `status: deferred` / `deprecated`; do not recycle the numbers. |

Optional metadata:

```yaml
status: active        # active | moved | superseded | deprecated | deferred
revision: 1
supersedes: []
replaced_by: []
owner: "pm-or-qa-owner"
last_changed: "YYYY-MM-DD"
```

Type taxonomy:

| Type | Covers |
|---|---|
| `happy_path` | successful completion of the primary scenario |
| `validation` | field-level or business-rule rejection |
| `permission` | role, tenant, org, row, field, or action scope |
| `state` | lifecycle guard or invalid transition |
| `dependency` | upstream/downstream/API/message failure |
| `regression` | previously failed scenario that must not recur |
| `edge` | boundary, concurrency, partial failure, timeout, weak network |

## Machine-Readable AI Runtime Contract

The product-level `ai_runtime_contract` in `advanced-extensions.md` is
authoritative. For coding agent implementation, extend it with implementation
fields that can map to config, tests, observability, and feature flags.

### Contract Selection Ladder

Do not use the full `ai_runtime_contract` for every L2 AI-supporting feature.
Choose the smallest contract that preserves implementation safety:

| Scenario | Contract |
|---|---|
| AI only summarizes, extracts, drafts, classifies, recommends, or ranks; deterministic/manual path remains valid; AI writes no business state | `ai_contract_lite` |
| AI output becomes a workflow task, changes object lifecycle, triggers external notification, calls tools with side effects, or affects money/safety/compliance/legal decisions | full `ai_runtime_contract` |
| AI-core, multi-agent, autonomous tool routing, model-selected action, production rollout with rollback/eval/on-call, or high-risk regulated use | full `ai_runtime_contract` plus AI Native / runtime gates |

Upgrade from lite to full when any condition becomes true:

- `write_scope` must exceed `none` or `draft_only`;
- the AI path can create, update, dispatch, approve, reject, close, pay, notify,
  delete, or otherwise alter consequential business state;
- a tool call has external side effects or non-idempotent writes;
- the feature needs P0/P1 golden eval thresholds, runtime observability,
  rollback ownership, prompt/model registry, or on-call support;
- failure could create compliance, privacy, safety, financial, or customer
  acceptance risk.

Lite-to-full mapping:

| `ai_contract_lite` field | Full contract destination |
|---|---|
| `model` | `agent_or_model` / `impl.model_env` |
| `prompt_file` | `impl.prompt_file` |
| `write_scope` | `write_scope` |
| `human_gate` | `human_gate` |
| `fallback` | `fallback_state` plus recovery notes |
| `feature_flag` | `impl.feature_flag` |

```yaml
ai_runtime_contract:
  agent_or_model: "model-or-agent-name"
  write_scope: draft_only          # none | draft_only | workflow_task | business_state
  input_schema_version: v1
  output_schema_version: v1
  tool_scope:
    allowed: ["read_file", "search_index"]
    forbidden: ["delete_record", "send_external_notification"]
  human_gate: required_before_publish
  fallback_state: manual_review    # local_fallback | manual_review | ai_failed
  observability:
    fields: [trace_id, prompt_version, model_version, latency_ms, confidence, failure_reason]
    sink: "structured_log"
  rollback:
    owner: "product-ops"
    trigger: "P1 alert or user complaint rate > threshold"
    linked_test_cases: ["AC-M07-F02-001"]
  impl:
    prompt_file: "prompts/feature-name-v1.md"
    prompt_version_env: "PROMPT_VERSION"
    model_env: "AI_MODEL_ID"
    timeout_ms: 8000
    retry_policy:
      max_attempts: 2
      backoff: exponential
      retryable_errors: ["429", "529", "timeout"]
    output_parser: json_strict
    output_validation_schema: "schemas/feature-output.schema.json"
    cache_ttl_s: 0
    feature_flag: "ff_ai_feature_name"
  eval:
    golden_case_file: "evals/feature-golden.jsonl"
    p0_threshold: 0.95
    p1_threshold: 0.90
    eval_runner: "pytest evals/ -m p0"
```

JSON Schema skeleton:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["agent_or_model", "write_scope", "human_gate", "fallback_state"],
  "properties": {
    "agent_or_model": { "type": "string" },
    "write_scope": {
      "enum": ["none", "draft_only", "workflow_task", "business_state"]
    },
    "human_gate": {
      "enum": ["required_before_write", "required_before_publish", "not_applicable_with_reason"]
    },
    "fallback_state": {
      "enum": ["local_fallback", "manual_review", "ai_failed"]
    },
    "impl": {
      "type": "object",
      "properties": {
        "prompt_file": { "type": "string" },
        "timeout_ms": { "type": "integer", "minimum": 100 },
        "feature_flag": { "type": "string" },
        "output_validation_schema": { "type": "string" }
      }
    }
  }
}
```

For AI-supporting features that do not require the full runtime contract, use
this minimum block inside FRR section 13:

```yaml
ai_contract_lite:
  model: "model-or-agent-name"
  prompt_file: "prompts/feature-name-v1.md"
  write_scope: none
  human_gate: required_before_publish
  fallback: "Hide the AI suggestion area and show the manual input entry."
  feature_flag: "ff_ai_feature_name"
```

## Prototype Data-Attribute Contract

Coding agents must link implementation and tests to prototype attributes:

| Attribute | Format | Example |
|---|---|---|
| `data-testid` | `{component}-{action-or-context}` | `btn-submit-review` |
| `data-action` | `{domain}.{verb}` | `lead.submitReview` |
| `data-state` | `{objectType}:{stateName}` | `lead:pending_review` |
| `data-api` | `/{resource}/{subresource}` | `/leads/submit` |
| `data-method` | uppercase HTTP verb | `POST` |
| `data-visible-role` | comma-separated role IDs | `sales_rep,sales_manager` |
| `data-field` | `{domain}.{fieldName}` | `lead.contactPhone` |
| `data-bind` | `{storeKey}.{path}` | `leadStore.detail.status` |

Verification checklist:

- [ ] Every `data-testid` maps to at least one `ac_structured.data_testid`.
- [ ] Every `data-action` appears in FRR section 6 numbered flow or FRR section 7 actions.
- [ ] Every `data-state` appears in FRR section 9 state/button/lifecycle matrix.
- [ ] Every `data-api` + `data-method` is declared in FRR section 13 or API contract.
- [ ] Every `data-visible-role` is defined in FRR section 10.
- [ ] No interactive element lacks `data-testid`.

If any check fails, the coding agent must report the gap and stop the affected
implementation step instead of inventing behavior.

Run the deterministic checker when both PRD and prototype are available:

```powershell
python scripts/validate_coding_agent_contract.py --prd path/to/prd.md --prototype path/to/prototype.html
```

## Delivery Package Layout

When a coding agent receives a delivery package, use this relative layout unless
the user explicitly provides another manifest:

```text
delivery/
  prd/                        # PRD Markdown files
  prototype/                  # HTML prototype(s)
  ia-skeleton.yaml            # Stage 3.5 structural truth
  acceptance/                 # AC-YAML files
  agents/                     # generated AGENTS.md / CLAUDE.md / Cursor rules
  evidence/                   # validation logs, screenshots, UAT notes
  manifest.json               # artifact list, versions, hashes, source status
```

Coding-agent lookup order:

1. Read `delivery/manifest.json` when present.
2. Read `delivery/ia-skeleton.yaml` for module/view/region/action structure.
3. Read PRDs from `delivery/prd/`.
4. Read prototypes from `delivery/prototype/`.
5. Read AC-YAML from `delivery/acceptance/`.
6. Read generated coding-agent instructions from `delivery/agents/`.

If the package does not follow this layout, first produce a source map and ask
for or infer missing paths before implementation. Do not start coding from
scattered files when the PRD/prototype/acceptance source of truth is ambiguous.

## Agent Entrypoint Generation

Generate project-local instruction files from the PRD, not inside this repo.

### `AGENTS.md`

Use for OpenAI Codex, GitHub Copilot coding agent-style repository context, and
general multi-agent coding tools that read repo-level instructions.

```markdown
# AGENTS.md

## Source Of Truth
- Manifest: `delivery/manifest.json` when present.
- IA Skeleton: `delivery/ia-skeleton.yaml`.
- PRD: `delivery/prd/` or `{prd_path}`.
- Prototype: `delivery/prototype/` or `{prototype_path}`.
- Acceptance: `delivery/acceptance/` or PRD FRR section 16 `ac_structured` blocks.

## Implementation Rules
1. Read manifest and IA Skeleton before coding when present.
2. Business logic follows PRD FRR section 8 and section 9.
3. UI behavior follows prototype `data-*` annotations.
4. Do not invent states, permissions, API contracts, or role paths.
5. Report missing requirements as `[GAP] {FunctionID} section {Section}: {description}`.
6. Preserve tenant/org/role/data isolation from FRR section 10.

## Verification
- P0 smoke: `{test_command_p0}`.
- P1 regression: `{test_command_p1}`.
- AI eval when applicable: `{eval_command}`.
```

### `CLAUDE.md`

Use for Claude Code. It may mirror `AGENTS.md`, but keep Claude-specific
commands, repo conventions, and gap-reporting rules in `CLAUDE.md` when the
project already uses one.

### Cursor Rules

Prefer modern Cursor project rules under `.cursor/rules/*.mdc` when the project
supports them. Generate `.cursorrules` only for legacy projects or when the user
explicitly asks for that file.

```markdown
---
description: Product spec implementation rules
globs: ["**/*"]
alwaysApply: true
---

Implement from `{prd_path}` and `{prototype_path}`.
Do not invent behavior missing from FRR.
Map tests to `ac_structured` IDs.
Report gaps with `[GAP]`.
```

## Coding Agent Handoff Prompt

```text
Use ai-delivery-spec coding-agent compatibility mode.

Inputs:
- PRD: {prd_path}
- Prototype: {prototype_path}
- Target repo: {repo_path}

Before coding:
1. Extract FRR function inventory.
2. Extract all `ac_structured` blocks.
3. Map prototype `data-testid`, `data-action`, `data-state`, `data-api`,
   `data-method`, `data-visible-role`, and `data-field`.
4. Report any gap before implementation.

Implementation:
- Generate tests from P0/P1 AC entries first.
- Implement only behavior covered by FRR/prototype/AC.
- For AI features, implement fallback as default and AI path behind feature flag.
- End with changed files, test results, and unresolved gaps.
```
