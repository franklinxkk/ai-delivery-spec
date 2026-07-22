# Domain: AI Native Product And Agentic Systems

Source authority and freshness metadata: `references/domains/domain-sources.yaml`.
Coverage and maturity: `references/domain-coverage.yaml`.

Use this replaceable domain module for AI-native products, agent workflows,
LLM-powered applications, multi-agent systems, copilots, AI assistants, RAG
products, tool-using agents, evaluation platforms, prompt/model operations, and
human-in-the-loop automation. A replacement `domain-*.md` must preserve the
same 15 section headings used here and in `domain-module-template.md`.

## Contents

- Domain Purpose
- First-Principles Domain Lens
- Vocabulary
- Aggregates and Entities
- Domain Events
- State Machines
- Metric / Indicator Governance
- AI Context Sources
- Content / Knowledge Assets
- Core Workflows
- Role Path Patterns
- UI / Mobile Patterns
- Policy / Privacy Constraints
- Domain Test Scenarios
- Evaluation Profile
- Acceptance Checklist

## Domain Purpose

- Business outcome: deliver trustworthy AI-assisted or AI-core outcomes with
  clear user value, accountable human gates, measurable quality, and safe
  rollback.
- Primary users: end user, expert reviewer, operations owner, AI engineer,
  product manager, risk/compliance reviewer, admin.
- Sensitive areas: private context, prompts, retrieved documents, model output,
  tool credentials, writeback actions, evaluation data, and user feedback.
- AI may optimize: intent understanding, retrieval, summarization,
  recommendation, reasoning support, drafting, routing, and workflow assistance.
- AI must not autonomously decide: high-impact legal, financial, medical,
  safety, enforcement, account closure, payment, or irreversible business
  actions without explicit authorized human accountability.

## First-Principles Domain Lens

First-Principles Product Logic: AI-native product judgment must start from work physics, not tool hype. Claude,
Codex, Trae, OpenClaw/Lobster-class tools, WorkBuddy-class internal assistants,
and new agent platforms are delivery surfaces. They are not the product logic.

Use these first principles before selecting features:

| Principle | Product Question | Value Signal |
|---|---|---|
| Work outcome first | What role, decision, artifact, or state transition changes? | shorter cycle time, fewer defects, higher throughput, better decision evidence |
| Context before model | What context must be correct, fresh, permitted, and cited? | lower hallucination, fewer reviewer edits, reusable knowledge assets |
| Workflow before chat | Which repeated workflow can be compressed or redesigned? | fewer handoffs, less waiting, clearer owner/action closure |
| Reversibility determines autonomy | If AI is wrong, can the action be reversed cheaply and safely? | safe automation scope and human-gate placement |
| Evidence beats fluency | Can the output be traced to source, rule, eval, or reviewer decision? | acceptance confidence and auditability |
| Human accountability remains | Who signs off on consequential decisions? | deployable governance instead of demo-only automation |
| Eval is product telemetry | What golden cases, adversarial cases, and live metrics prove value? | launch readiness and regression control |
| Ontology turns data into action | What business objects, links, actions, and rules must AI understand? | agents can reason over operations, not just documents |

Durable AI-native trend map:

| Trend Layer | Stable Capability | Product Risk If Ignored |
|---|---|---|
| Coding agents | spec -> plan -> tasks -> code -> tests loop | fast code with wrong product behavior |
| Enterprise work agents | inbox/task/workflow orchestration across tools | fragmented assistants that do not close work |
| Knowledge engineering | curated corpus, metadata, lifecycle, retrieval, feedback | confident answers over stale or unauthorized knowledge |
| Ontology / semantic layer | object/link/action/rule model over business reality | agents cannot safely write back or explain decisions |
| Tool protocol layer | MCP/API/tool registry, auth, schema, side-effect control | unsafe tool calls and hidden integration drift |
| Evaluation and observability | golden cases, traces, feedback, rollout/rollback | demo success but production regression |
| Human-in-the-loop ops | review queues, escalation, override, incident response | no accountable owner for AI mistakes |

## Vocabulary

| Term | Meaning | Source Of Truth |
|---|---|---|
| AI Feature | AI-supporting capability with a valid manual/deterministic path | Product Truth + runtime contract |
| AI-Core Workflow | primary user outcome depends on model/tool orchestration | AI runtime contract |
| Agent | bounded AI actor with goal, tools, memory/context, eval, owner | agent registry |
| Tool | callable system/API/function with permission and side-effect scope | tool registry |
| Prompt | versioned instruction/context template | prompt registry |
| RAG Context | retrieved document, record, vector result, or knowledge snippet | retrieval/index service |
| Human Gate | required review/approval before publish, send, write, or close | workflow policy |
| Golden Case | versioned evaluation example with expected behavior | eval set |
| Anchor Case | stable calibration case used to detect model/prompt/tool drift before normal eval | eval set |
| Refusal | safe response when request is unsupported, unsafe, or unauthorized | policy/rule set |

## Aggregates and Entities

| Aggregate | Owns | Notes |
|---|---|---|
| AIUseCase | user job, scope, risk level, success metric | product-facing intent |
| AgentDefinition | role, goal, allowed tools, write scope, memory policy | versioned and reviewable |
| ToolDefinition | schema, auth owner, side effects, rate limits, rollback | blocks unsafe tool mixing |
| PromptVersion | template, variables, examples, owner, status | draft -> tested -> active |
| ContextAsset | document/table/API/vector index, freshness, classification | permission inherited by user |
| EvalSet | anchor cases, golden cases, adversarial cases, thresholds, reviewer | required for AI-core release |
| RunTrace | input hash, context refs, model, tools, output, feedback | observability and audit |
| HumanReview | reviewer, decision, reason, edited output, audit | closes accountability loop |

## Domain Events

```yaml
events:
  AgentRunStarted:
    payload: { run_id, agent_id, user_id, prompt_version, model_version }
  ContextRetrieved:
    payload: { run_id, context_refs, freshness, permission_scope }
  ToolCallRequested:
    payload: { run_id, tool_id, side_effect_scope, approval_required }
  HumanReviewRequested:
    payload: { run_id, reviewer_role, reason, risk_level }
  AIOutputPublished:
    payload: { run_id, output_id, reviewer_id, published_at }
  AIWritebackBlocked:
    payload: { run_id, target_object, reason, policy_version }
  EvalRegressionDetected:
    payload: { eval_set_id, agent_id, threshold, failed_cases }
```

## State Machines

```text
AIUseCase: idea -> shaped -> specified -> evaluated -> launched -> monitored -> retired
AgentDefinition: draft -> test_ready -> approved -> active -> deprecated | suspended
PromptVersion: draft -> candidate -> evaluated -> active -> rolled_back | archived
AgentRun: created -> retrieving_context -> reasoning -> tool_pending -> human_review -> completed
AgentRun: reasoning | tool_pending -> refused | failed | fallback
HumanReview: pending -> approved | edited_and_approved | rejected | escalated
```

State consistency:

| Concept | Source Of Truth | Consistency Need |
|---|---|---|
| write scope | AgentDefinition + policy | strong before tool execution |
| context permission | user scope + asset classification | strong before retrieval and answer |
| prompt/model version | RunTrace | immutable after run starts |
| review decision | HumanReview | auditable before publish/writeback |
| eval threshold | EvalSet | versioned before launch gate |

## Metric / Indicator Governance

| Metric | Caliber | Owner |
|---|---|---|
| task_success_rate | reviewed runs that complete user goal without material correction | product + QA |
| human_edit_rate | approved outputs requiring user/reviewer edits | product ops |
| refusal_correctness | unsafe/unsupported/unauthorized requests correctly refused | risk owner |
| tool_call_error_rate | failed or blocked tool calls / total tool calls | engineering |
| grounded_answer_rate | answers with valid context citations / answer runs | AI engineer |
| eval_p0_pass_rate | P0 golden cases passed / P0 cases | release owner |
| anchor_case_pass_rate | anchor cases passed before normal eval / anchor cases | AI engineer + QA |
| rollback_time | time from regression alert to safe fallback | operations |

Rules:

- Every launch claim needs an eval set, baseline, threshold, sample size, and
  owner.
- Any model, prompt, retrieval, tool, or schema change must run Anchor-Cases
  before normal golden/adversarial evaluation. Anchor failure means the eval
  baseline is not comparable and must stop release as `REVIEW_COMPLETE_WITH_GAPS`.
- AI-core modules require P0 smoke, P1 regression, and adversarial cases.
- Production monitoring must connect run traces to user feedback and incidents.
- Metrics must segment by model/prompt/tool/context version.

## AI Context Sources

| Context | Source | Freshness | Permission / Reliability Rule |
|---|---|---|---|
| user profile and task state | product database | real-time | inherit user/tenant/data scope |
| knowledge documents | approved knowledge base | versioned | cite document/version; do not use expired policy |
| structured business data | API/data warehouse/semantic layer | real-time/batch | row/column permissions before aggregation |
| conversation memory | session or durable memory store | session/versioned | user-controlled retention and delete/export |
| tool outputs | tool/API result | per call | include tool version and error handling |
| eval cases | evaluation repository | versioned | do not train or leak private cases without approval |

## Content / Knowledge Assets

| Asset | Minimum Metadata | Governance |
|---|---|---|
| prompt library | owner, variables, examples, version, risk class | review before active |
| tool registry | schema, auth owner, write scope, rollback, rate limit | security review |
| knowledge base | owner, source, effective date, classification, freshness | lifecycle review |
| eval set | anchor/golden/adversarial case type, expected behavior, threshold, reviewer, version | release gate |
| refusal policy | forbidden request class, response boundary, escalation | risk/compliance owner |
| fallback playbook | trigger, user message, manual path, owner, recovery | operations owner |

## Core Workflows

1. Opportunity shaping: user pain -> AI centrality -> manual fallback ->
   success metric -> risk class -> PRD profile.
2. Agent specification: goal -> allowed context -> allowed tools -> write scope
   -> human gate -> eval set -> trace fields.
3. Runtime answer: user request -> permission check -> context retrieval ->
   model/tool execution -> citation/refusal -> human gate when needed -> output.
4. Tool writeback: proposed action -> policy check -> reviewer approval ->
   idempotent tool call -> audit/event -> rollback path.
5. Evaluation loop: anchor calibration -> golden/adversarial run -> threshold
   check -> regression triage -> prompt/model/tool update -> release decision.
6. Operations loop: trace/feedback/incident -> classify failure -> fallback or
   rollback -> fix -> post-launch review.

## Role Path Patterns

| Role | Entry | Core Actions | Forbidden Actions | Exit |
|---|---|---|---|---|
| end user | chat/copilot/task UI | ask, refine, accept, reject, give feedback | bypass permission or hidden data | completed task or fallback |
| expert reviewer | review queue | inspect evidence, edit, approve/reject | approve without evidence for high-risk output | accountable decision |
| AI engineer | eval/runtime console | tune prompt/model/tool, run evals | change active prompt without release evidence | versioned candidate |
| product manager | PRD/eval dashboard | define outcome, scope, gate, metrics | claim quality without eval evidence | launch decision |
| operations owner | incident console | monitor, rollback, suspend agent | silently ignore regressions | restored service |
| admin/risk | policy/tool registry | approve tools, scopes, retention | grant broad write scopes without audit | safe active policy |

## UI / Mobile Patterns

- Show AI role, confidence/evidence boundary, citations, and freshness when it
  affects user trust.
- Separate "draft/recommendation" from "published/written" states visually.
- High-impact actions require review drawer, diff, reason, and explicit approve
  button.
- Provide a deterministic/manual path for AI-supporting features.
- Show source gaps, permission denials, stale context, and refusal reasons
  without exposing sensitive hidden data.
- For mobile, keep review/approve actions short, auditable, and reversible
  where business policy allows.

## Policy / Privacy Constraints

- AI context retrieval inherits user, tenant, organization, row, column, and
  field-level permissions.
- Tool calls must declare read/write scope, idempotency, side effects, timeout,
  rollback, and audit owner.
- Model output cannot be treated as authoritative when source evidence is
  missing, stale, unauthorized, or contradicted.
- Prompt, context, trace, and feedback retention must follow privacy and data
  deletion/export policy.
- Autonomous writeback is forbidden for high-impact actions unless the PRD
  explicitly defines policy, human gate, eval, rollback, and on-call ownership.
- Test agents must use shadow data or mocked tools for write paths.

## Domain Test Scenarios

| Scenario | Role | Expected Result |
|---|---|---|
| grounded answer with citations | end user | answer cites permitted context refs and freshness |
| unauthorized data request | end user | refusal without leaking hidden fields |
| tool write requires approval | expert reviewer | writeback waits for approval and logs decision |
| stale knowledge base | end user | answer warns stale source or routes to manual path |
| eval regression before launch | AI engineer | release blocked and failed cases listed |
| anchor case drift after model upgrade | AI engineer | normal eval is paused until baseline is recalibrated |
| fallback on model outage | operations owner | deterministic/manual fallback within SLA |
| prompt rollback | operations owner | active prompt returns to last passing version |
| adversarial prompt injection | risk reviewer | tool call blocked and event logged |
| delegated tool denial | risk reviewer | a denied tool/action remains denied through agent delegation, memory and prompt content; denial is audited |
| repeated propose-reject loop | accountable user | loop stops at configured limit and hands control to a human/manual path |

## Cross-Domain Requirement Patterns

- `PAT-VERSION-COMPATIBILITY-001`: model, prompt, tool schema, retrieval corpus and policy versions bind every consequential run and remain replayable.
- `PAT-LONG-RUNNING-JOB-001`: indexing, evaluation, batch inference and multi-agent jobs expose bounded progress, retry, cancellation and human takeover.
- `PAT-METRIC-CALIBER-001`: quality, safety, cost and latency metrics declare datasets, thresholds, aggregation windows, versions and accountable interpretation.

## Evaluation Profile

Domain knowledge is not execution evidence. Register coverage and maturity in
`references/domain-coverage.yaml`; keep behavioral scenarios and run evidence
outside this knowledge file.

Before raising maturity, independently evaluate:

- one primary happy path;
- one validation or exception path;
- one permission/privacy path;
- one lifecycle transition;
- one coding-agent no-guess handoff path;
- applicable migration, integration-failure, AI, and high-risk human-gate paths.

Record executor, input, environment, timestamp, result, and evidence location.
Mocked matrices and simulated reviewers cannot satisfy expert review or audit.

## Acceptance Checklist

- [ ] All 15 domain module sections are present.
- [ ] AI centrality is classified per module: AI-incidental, AI-supporting, or AI-core.
- [ ] Agent/tool/write scopes and human gates are explicit.
- [ ] Context sources have freshness, permission, citation, and reliability rules.
- [ ] Eval sets, thresholds, baselines, and owners exist before AI-core launch.
- [ ] Anchor-Cases run before golden/adversarial eval after model, prompt,
      retrieval, tool, schema, or context changes.
- [ ] Refusal, fallback, rollback, incident, and post-launch review paths are defined.
- [ ] High-impact decisions keep authorized human accountability.
- [ ] Coding-agent handoff includes `ai_contract_lite` or `ai_runtime_contract`
      only at the necessary depth.
