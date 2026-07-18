---
name: ai-delivery-spec
description: Manage requirements from intake through one implementable PRD/prototype baseline, change, traceability, Agent handoff, and acceptance. Use for ideas, customer materials, brownfield systems, ToC/ToB/ToG requirements, AI-coding handoffs, or audits. Excludes sprint management, coding, CI/CD, deployment, and operations.
---

# AI Delivery Spec 5.3.0 — Requirement Management Kernel

Create one human-readable, AI-coding-ready baseline. Trace truth in both
directions: source → behavior → acceptance and evidence/change → decision.
Product Truth is optional governed authority, not a mandatory first output.

First run: Python 3.10+; `python -m pip install -r scripts/requirements.txt`.
Terms: Stable ID = durable name; Product Truth = optional structured authority;
gate = static structure/trace check, never business/browser proof.

## Start with intake, silently

Internally classify two axes; expose them only when useful or overridden:

- `delivery_shape`: `requirement_card`, `unified_prd`, or `governed_truth`;
- `assurance_profile`: `bounded`, `standard`, `high_risk`, or `safety_critical`.

Use a card for one reversible role-local change, one PRD for normal work, and
governed truth only for controlled multi-output, repeated cross-module change,
lineage or strong audit. Size or “AI” alone never forces it. L0—L4 remain gate
intensity metadata, not user homework.

Confirm outcome, users, scope, authority, owner, uncertainty, priority,
dependencies, acceptance and exclusions. Batch independent questions. Record
P0 unknowns as owned, scoped `UNK-*`; never invent engineering cost.

## Load one active slice

| Active need | Read |
|---|---|
| intake, stages, roles, baseline | `references/lifecycle.md` |
| one-line idea, sources, competitor, brownfield inventory | `references/discover.md` |
| PRD, fields, rules, interfaces, machine annex | `references/specify.md` |
| page contract, Stage 0, prototype, visual route | `references/prototype.md` |
| change, traceability, acceptance result | `references/change-acceptance.md` |
| large input, composition, checkpoints, Agent packets | `references/context.md` |
| Coding tool projection | `references/tool-adapters.md` |
| failure/FAQ/anti-pattern | `references/troubleshooting.md` |
| domain evidence | `scripts/query_domain.py --domain <pack> --section "<heading>"` |
| private domain/template/rules | `init-custom`; local declarations override presentation only |

Load one stage reference plus one exact domain section by default.
Do not load README, `maintainer/`, all templates, examples, domains, or the whole
repository during a project task. Load optional realtime/common patterns only
when their trigger is present.

## Run the requirement loop

```text
Intake → Clarify → Specify → Review → Baseline → Change → Acceptance → Closed
```

1. Bind `REQ-*` to source, outcome, scope, owner and acceptance.
2. Close roles/data scope, flows, states, rules, fields, exceptions, recovery,
   metrics and prohibited behavior.
3. Deliver one PRD: readable narrative, then exact engineering/AI annexes.
4. Review through product, domain, UX, engineering, QA, compliance and customer;
   keep unresolved `REV/UNK` explicit.
5. Baseline version, authority, IDs and approvals; conflicts need `DEC-CONFLICT-*`.
6. `CHG-*` traverses both directions, updates projections and regresses.
7. Each mandatory `AC-*` records actual evidence, result and accountable sign-off.

## Preserve the no-guess contract

- Stable IDs cover source/decision/unknown, behavior/data, interface and proof.
- Every role reaches success, authorized denial, recovery, or explicit handoff.
- Every action binds actor, precondition, authority, input, visible and domain
  result, state/event/audit, failure/recovery and AC.
- State transitions declare from/to, trigger, guard, owner, illegal path and
  evidence; workflow scope has an E2E AC.
- Every displayed metric defines population, formula, time/status/filter/dedup,
  source/freshness, zero/null and format beside its view.
- Views declare `primary`, `layout`, applicable `surfaces`, conditional
  fields/actions/API/AC and stable prototype anchors.
- L3 baselines declare acceptance owner, scope, pass rule, evidence and signers.
- High-risk rules bind `SRC/DEC/ASSUMPTION`; AI and lineage contracts appear only
  when those behaviors are actually in scope.
- A Coding Agent implements one baselined ID slice without inventing business
  decisions. Missing engineering baseline is a handoff GAP, not PRD failure.

For existing PRD/prototype work, complete Stage 0 before overwrite: locate and
classify every view/action/state/role/object/field/handoff as `confirmed`,
`inferred`, `unknown`, or `defect_candidate`. With a forward baseline, recovered
items use `INV-*`, map to exact `REQ-*`, and inferred items enter owned `RBATCH-*`.
Inventory is not target approval; reverse extraction cannot infer API/metric/
permission/compliance truth.

## Bound large work and learning

Auto-round at >8 inputs, >500k parseable characters, ≥8 modules, ≥12 pages, or
≥200 stable objects. Round 0 freezes sources/authority; later rounds use vertical
role slices and checkpoints; the last round runs cross-module closure. A stage
checkpoint is not final completion.

Learning is off/local/no-network. Candidates follow
`schemas/domain-candidate.schema.json`, default to `project_only`, and need
approval plus maintainer gates before promotion.

Long work may project root/module `AGENTS.md` from
`schemas/agent-handoff.schema.json`; packets bind one hash, owner, scope, AC and
QA view and cannot modify requirement truth.

## Finish with one light gate

```bash
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd PRD.md --level auto
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html --level auto
python scripts/ai_delivery_spec_cli.py gate --profile handoff --prd PRD.md --prototype admin.html --manifest handoff-manifest.yaml --level auto
```

The zero-LLM, zero-subagent, single-read gate only diagnoses. Repair its first
finding and rerun RETRY. Static PASS never replaces review, browser/QA execution
or customer acceptance. Return exactly one state: `PASS`,
`REVIEW_COMPLETE_WITH_GAPS`, `BLOCKED_BY_P0_UNKNOWN`, or `BLOCKED`.

For authorized long tasks, continue through every requested artifact and gate;
pause only for a material user decision, unavailable authority, or scoped P0
unknown that blocks the current stage.
