# AI Native Harness Engineering

Use this file after an AI-native scenario and target outcome are defined, before runtime implementation starts.

AI Native delivery fails when the scenario is attractive but the engineering harness cannot support stable execution. Every AI-native feature must prove that its context, agent workflow, tools, evaluation, observability, and release path can be simulated before development is accepted.

## Contents

- Core Principle
- When Required
- Required Inputs
- Harness Minimum
- Multi-Agent Feasibility Review
- Engineering Path Simulation
- Required Harness Artifacts
- Hard Fail Conditions
- Acceptance Checklist

## Core Principle

AI Native is not "add an LLM call to a workflow". It is a new operating loop:

```text
business trigger -> context assembly -> agent planning -> tool execution -> evidence generation
-> human gate or auto action -> domain write -> trace -> evaluation -> learning loop
```

The harness is the engineering scaffold that makes this loop testable and repeatable.

## When Required

This gate is mandatory when any of these are true:

- the feature changes an existing business workflow through AI;
- one AI result triggers another agent, workflow, notification, report, or write action;
- the AI output affects compliance, money, safety, customer commitment, or operational priority;
- the feature depends on RAG, long context, tool calls, data queries, memory, or multi-step planning;
- the PM claims measurable efficiency, quality, risk reduction, or automation value.

## Required Inputs

Before review, the PM and engineering owner must provide:

```yaml
ai_native_scenario:
  id: ANS-001
  business_goal: string
  target_user: string
  trigger: user_request | event | schedule | external_signal
  current_workflow: [step]
  ai_native_workflow: [step]
  expected_business_outcome: string
  success_metrics:
    - metric: saved_minutes_per_task
      target: number
    - metric: adoption_rate
      target: number
    - metric: human_override_rate
      max: number
  risk_level: low | medium | high | critical
  allowed_auto_actions: [string]
  human_gate_actions: [string]
  forbidden_actions: [string]
  required_context:
    business_data: [string]
    knowledge_sources: [string]
    user_profile: [string]
    historical_cases: [string]
  required_tools: [string]
  target_latency_ms: number
  target_cost_per_run: number
  realtime_or_multimodal:
    enabled: true | false
    modes: [text, voice, stt, tts, avatar, video, screen, image]
    fallback_modes: [text, audio_only, cached_content, human_handoff]
```

If the scenario cannot express the current workflow, AI-native workflow, business outcome, risk level, and required context, it is not ready for engineering review.

## Harness Minimum

Every AI-native scenario must define six harness layers.

| Layer | Required Definition | Fail If Missing |
|---|---|---|
| Context harness | data sources, knowledge refs, freshness, permission scope, retrieval rules, memory boundary | AI has no trustworthy context or can see data outside user scope |
| Tool/API harness | tool registry, sandbox/stub, fixture inputs, side-effect policy, idempotency | tools cannot be simulated without touching production |
| Workflow harness | agent graph, events, state machine, retries, timeouts, fallback, human gates | agent path is only a prompt narrative |
| Evaluation harness | golden cases, adversarial cases, schema checks, human rubric, business metric checks | no repeatable way to prove quality |
| Observability harness | trace schema, replay fields, cost/latency, confidence, hallucination, tool audit | failures cannot be replayed or explained |
| Release harness | dry-run, shadow, canary, rollback, kill switch, owner/SLA | no safe path from prototype to production |

For real-time or multimodal AI scenarios such as AI 数字人、语音助教、avatar tutor, voice customer service, or AI learning coach, add a media harness:

| Media Harness Area | Required Definition | Fail If Missing |
|---|---|---|
| STT/TTS harness | provider, latency target, timeout, transcript policy, retry/fallback | voice path cannot be replayed or falls back silently |
| Avatar/render harness | renderer/provider, bandwidth downgrade, audio/text fallback, accessibility fallback | avatar failure blocks the business task |
| Conversation turn harness | turn state, interrupt behavior, low-confidence fallback, memory boundary | long responses cannot be stopped or audited |
| Mobile permission harness | microphone/camera/speaker consent, denial fallback, retention | sensitive capture starts without explicit consent |
| Evidence/citation harness | knowledge refs, source cards, hallucination checks | tutor/digital human answers cannot be traced |

## Multi-Agent Feasibility Review

Run this review after Stage 3 scenario design and before Stage 3.5 runtime design.

| Reviewer | Question | Output |
|---|---|---|
| Sponsor Agent | Does this solve a material business outcome? | outcome value + scope risk |
| Domain Workflow Agent | Does the AI-native workflow preserve business invariants? | invariant gaps + manual gate needs |
| AI Architect Agent | Can the agent/context/tool design support the outcome? | agent graph + context design risk |
| Backend Integration Agent | Can current systems/data/APIs support stable execution? | integration path + missing APIs/data |
| Data/RAG Agent | Are sources reliable, fresh, scoped, and retrievable? | data readiness + RAG risk |
| QA/Eval Agent | Can quality be measured before release? | golden set + eval plan |
| Ops/SRE Agent | Can the system be observed, throttled, rolled back, and supported? | operations gate + failure modes |

Verdict format:

```markdown
## AI Native Harness Review

Scenario: ANS-001
Verdict: PASS | CONDITIONAL_PASS | NO_GO

### Reviewer Verdicts
| Reviewer | Verdict | Blocking Issue | Required Fix |
|---|---|---|---|

### Engineering Path
- Context path:
- Agent path:
- Tool/API path:
- Data/RAG path:
- Human gate path:
- Write/audit path:
- Release path:

### Simulation Result
- fixture replay:
- dry-run:
- failure injection:
- expected metric confidence:

### Decision
- proceed to Stage 3.5:
- reduce scope:
- reject:
```

## Engineering Path Simulation

The review must simulate both business logic and engineering execution.

Business path:

```text
trigger -> user intent -> required context -> agent plan -> evidence -> recommendation
-> human confirmation or auto action -> domain state change -> user-visible result
```

Engineering path:

```text
frontend/API -> auth/scope -> context assembler -> retrieval/query -> agent runtime
-> tool sandbox -> event bus -> write service -> audit log -> trace store -> dashboard/alert
```

Simulation modes:

| Mode | Purpose | Required Before |
|---|---|---|
| fixture replay | run fixed business cases with mocked tools/data | PRD accepted |
| dry-run | execute full path without business writes | internal demo |
| shadow run | run beside real workflow without affecting users | pilot |
| canary | limited real users / entities / time window | production rollout |
| failure injection | timeout, stale knowledge, permission denied, tool failure, low confidence | pilot |

## Required Harness Artifacts

```text
ai-native-scenario-card.yaml
context-map.md
agent-graph.yaml
tool-sandbox-contract.yaml
golden-eval-set.yaml
failure-injection-matrix.md
trace-replay-schema.yaml
release-gate-plan.md
harness-review-report.md
media-harness-contract.yaml (when voice, avatar, video, or streaming is used)
```

## Hard Fail Conditions

- AI-native scenario lacks measurable business outcome.
- Required context is unknown, stale, unscoped, or unavailable.
- Tool execution cannot be stubbed, sandboxed, or replayed.
- High-risk action lacks human gate.
- Agent path cannot be expressed as events, states, tools, and fallback.
- No golden cases or human evaluation rubric exists.
- No trace/replay path exists.
- Production release has no dry-run, shadow/canary, rollback, or kill switch.
- Voice/avatar/streaming scenarios have no STT/TTS/avatar fallback, transcript/replay, or interrupt behavior.

## Acceptance Checklist

- [ ] Scenario card defines goal, trigger, current workflow, AI-native workflow, risk, metrics.
- [ ] Context harness defines data, RAG, permissions, freshness, memory boundary.
- [ ] Tool/API harness defines sandbox, fixtures, side-effect policy, idempotency.
- [ ] Agent graph defines events, states, retries, fallback, human gates.
- [ ] Evaluation harness includes golden, adversarial, regression, and human rubric cases.
- [ ] Engineering path simulation covers happy, low-confidence, stale context, tool failure, permission failure.
- [ ] Trace/replay schema can reproduce a run from input to output.
- [ ] Release plan includes dry-run, shadow/canary, rollback, kill switch, owner, SLA.
- [ ] Media harness defines STT/TTS/avatar latency, permission, fallback, transcript, interruption, and replay when real-time/multimodal AI is used.
- [ ] Multi-agent feasibility review returns PASS or CONDITIONAL_PASS with fixes assigned.
