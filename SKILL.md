---
name: ai-delivery-spec
description: Turn ideas, customer materials, brownfield systems, and ToC/ToB/ToG requirements into one implementable PRD/prototype baseline with change, traceability, Agent handoff, and acceptance. Excludes sprint management, coding, CI/CD, deployment, and operations.
---

# AI Delivery Spec 5.3.2 — Requirement Management Kernel

Create one human-readable, AI-coding-ready baseline and trace source → behavior
→ acceptance in both directions. Product Truth is optional governed authority.

Output language follows the user's current request unless explicitly overridden.
Headings, prose, tables and tests use it; IDs, code, API/field names and proper
nouns stay unchanged. Bilingual: opt-in.

First run: Python 3.10+; `python -m pip install -r scripts/requirements.txt`.
Stable ID is durable; Product Truth is optional; gate proves structure, not business.

## Start with intake, silently

Internally classify two axes; expose them only when useful or overridden:

- `delivery_shape`: `requirement_card`, `unified_prd`, or `governed_truth`;
- `assurance_profile`: `bounded`, `standard`, `high_risk`, or `safety_critical`.

Use a card only for one reversible, role-local change. Escalate data submission/
reporting, material state, batch I/O, approval/audit, integration, migration,
high-risk or cross-role/module work to one PRD. Governed truth is only for
controlled multi-output, repeated coupling, lineage or strong audit. L0—L4 are
gate intensity metadata, not user homework.

Inspect artifacts and the exact domain section first. Batch independent facts;
ask direction/conflict decisions serially with recommendation, evidence and
trade-off. Unavailable facts become owned, scoped `UNK-*` with reversal path and
`blocks_stage`. Enter Specify only when P0/P1 disposition is explicit.

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

Load one stage reference plus one exact domain section. Do not load README,
`maintainer/`, all templates/examples/domains, or the whole repository. Load
optional patterns only when triggered.

## Run the requirement loop

```text
Intake → Clarify → Specify → Review → Baseline → Change → Acceptance → Closed
```

1. Bind `REQ-*` to source, outcome, scope, owner and acceptance.
2. Close roles/scope, flows, states, rules, fields, exceptions, metrics and bans.
3. Deliver one PRD: 30-second summary, task reading map, journeys, self-contained
   module slices, cross-cutting contracts, then exact engineering/AI indexes.
4. Review with product, domain, UX, engineering, QA, compliance and customer;
   keep `REV/UNK` explicit.
5. Baseline version, authority, IDs and approvals; conflicts need `DEC-CONFLICT-*`.
6. `CHG-*` traverses both directions, updates projections and regresses.
7. Each mandatory `AC-*` records actual evidence, result and accountable sign-off.

## Preserve the no-guess contract

- Stable IDs cover source/decision/unknown, behavior/data, interface and proof.
- Every role reaches success, authorized denial, recovery, or explicit handoff.
- Each module slice co-locates outcome, journey, UI/data, rules/permissions,
  state/events, metrics, recovery, acceptance and owned unknowns; annexes index
  or project the same IDs and never rewrite business meaning.
- Every action binds actor, guard, input, visible/domain result, state/audit,
  failure/recovery and AC; states declare from/to, trigger, owner and illegal path.
- Each metric defines population, formula, time/filter/dedup, source/freshness,
  zero/null and format beside its view; workflow scope has an E2E AC.
- Views declare `primary`, `layout`, applicable `surfaces`, conditional
  fields/actions/API/AC and stable prototype anchors.
- L3 baselines declare acceptance owner, scope, pass rule, evidence and signers;
  complex prototypes need `REG-*` anchors and browser `ARUN-*` evidence.
- High-risk rules bind `SRC/DEC/ASSUMPTION`; AI and lineage contracts appear only
  when those behaviors are actually in scope.
- A Coding Agent implements one baselined ID slice without inventing business
  decisions. Missing engineering baseline is a handoff GAP, not PRD failure.

Before overwrite, Stage 0 classifies every observed contract as `confirmed`,
`inferred`, `unknown`, or `defect_candidate`. Map `INV-* → REQ-*`; owned
`RBATCH-*` contains inferences. Never infer API, metric, permission or law.

## Bound large work and learning

Auto-round at >8 inputs, >500k characters, ≥8 modules, ≥12 pages, or ≥200 IDs.
Freeze sources, use vertical checkpoints, then close cross-module edges. Learning
uses `schemas/domain-candidate.schema.json`; local candidates default `project_only`.

Long work may project `AGENTS.md` from
`schemas/agent-handoff.schema.json`; packets bind hash, owner, scope and AC but
cannot modify requirement truth.

## Finish with one light gate

```bash
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd PRD.md --level auto
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html --level auto
python scripts/ai_delivery_spec_cli.py gate --profile handoff --prd PRD.md --prototype admin.html --manifest handoff-manifest.yaml --level auto
```

The zero-LLM, single-read gate diagnoses only. Repair its first finding and RETRY.
Static PASS never replaces review, browser/QA or customer acceptance. `auto`
reads PRD frontmatter; prototype/handoff default L2. L3/L4 without browser
`ARUN-*` is a gap. Return exactly one state: `PASS`,
`REVIEW_COMPLETE_WITH_GAPS`, `BLOCKED_BY_P0_UNKNOWN`, or `BLOCKED`.

For authorized long tasks, continue through every requested artifact and gate;
pause only for a material user decision, unavailable authority, or scoped P0
unknown that blocks the current stage.
