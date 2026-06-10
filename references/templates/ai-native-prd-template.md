# L3 AI Native PRD Template

Use when AI writes business state, chooses tools/routes, affects customer commitment, compliance, money, safety, or coordinates multiple agents.

## 1. Version And Risk

| Field | Value |
|---|---|
| Feature / Agent System | |
| Version | v1.0 |
| Owner | |
| Delivery Tier | L3 AI Native / High-Risk Delivery |
| Risk Level | low / medium / high / critical |
| Human Accountability Owner | |

## 2. Business Outcome

Business problem:

Target users:

Expected outcome:

Evidence level target:

## 3. AI Scenario Card

```yaml
ai_scenario:
  trigger:
  user_goal:
  business_goal:
  input_context:
  output:
  write_scope:
  forbidden_write:
  human_gate:
  fallback:
```

## 4. Agent / Runtime Design

| Agent | Role | Trigger | Tools | Output | Write Scope | Human Gate | Fallback |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

Runtime path:

```text
trigger -> context -> agent -> tool -> human gate -> write -> trace -> eval
```

## 5. Context And Data Sources

| Source | Data | Permission | Freshness | Risk |
|---|---|---|---|---|
| | | | | |

## 6. Tool / API Contract

| Tool | Class | Side Effect | Allowed When | Approval | Audit | Idempotency |
|---|---|---|---|---|---|---|
| | query/write/workflow/external | | | | | |

## 7. Prompt Registry

| Prompt ID | Agent | Model | Output Schema | Golden Case Tier | Linked Tests | Rollback Owner |
|---|---|---|---|---|---|---|
| | | | | P0 / P1 / P2 | | |

## 8. Evaluation Contract

| Metric | Baseline | Target | Window | Guardrail |
|---|---|---|---|---|
| | | | | |

Golden cases:

| Tier | Purpose | Min Cases | Run Timing |
|---|---|---:|---|
| P0 Smoke | cheap must-pass cases | 3-10 | every prompt change |
| P1 Regression | common business variants | 20-50 | release / weekly |
| P2 Benchmark | adversarial/long-tail/high-risk | 100+ | major release / monthly |

## 9. State And Fallback

| AI State | Entry | Exit | UI Message | Allowed Actions |
|---|---|---|---|---|
| ai_analyzing | | | | |
| ai_suggestion_pending | | | | |
| ai_low_confidence | | | | |
| ai_failed | | | | |
| local_fallback | weak network / 5xx / offline | reconnect + recheck | Local safe mode active | draft / queue / manual |

## 10. Observability And Operations

| Signal | Threshold | Executor | Action | Owner |
|---|---|---|---|---|
| | | ai-platform / ops-system / manual | | |

Rollback:

```text
alert -> rollback request -> canary/shadow previous version -> linked tests -> switch or manual decision
```

## 11. Acceptance

- [ ] AI write scope and forbidden write are explicit.
- [ ] Human gate exists for high-impact actions.
- [ ] Prompt registry has schema, golden cases, rollback owner.
- [ ] Evaluation target and guardrails are defined.
- [ ] Observability and alert executor exist.
- [ ] Edge/local fallback exists where weak network matters.
- [ ] System readiness checklist passes before launch.
