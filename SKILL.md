---
name: ai-delivery-spec
description: Turn rough product ideas, consumer or enterprise requests, customer materials, prototypes, legacy systems, or approved changes into traceable product truth, Human-First requirements, PRDs, testable prototypes, acceptance evidence, and coding-agent handoffs. Use for ToC idea clarification and lightweight PRDs, ToB/ToG delivery, product/domain modeling, AI/data/workflow products, brownfield change, customer acceptance, launch/operations, or multi-role lifecycle work. Excludes unrelated code debugging and copy rewriting.
---

# AI Delivery Spec 5.0.0 - Product Delivery Kernel, ToB/ToG Deep

Create one canonical Product Truth and project it for product, engineering, QA,
customers, coding agents, and operations. Dedicated domain packs accelerate
professional work; they are never required for generic delivery.

## 1. Triage Before Loading

Declare:

```text
[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false] | [INFO: complete|partial|missing]
Lifecycle: discover|specify|plan|tasks|build_verify|launch|learn_retire
Shape: greenfield|brownfield|hybrid
Consumer: human|prototype|coding_agent|qa|customer|operations
```

Rules:

- `Heavy`: development, QA, customer demo, bid/procurement, migration,
  production, acceptance, regulated decision, or multi-role lifecycle.
- `AI: true`: the product behavior uses models/agents. AI only writing the
  artifact or code is `false`.
- `WORKFLOW: true`: approval, task, escalation, cross-module state, audit, or
  long-running process exists.
- `INFO: partial/missing`: an unknown could change outcome, scope, ownership,
  state, data authority, compliance, commercial promise, or acceptance.

Mode and tier are independent:

| Mode | Stop Boundary |
|---|---|
| Lite | requested artifact plus explicit gaps |
| Standard | implementation/QA/customer handoff plus unresolved decisions |
| Full | complete truth, projections, manifest, readiness, and evidence |

| Tier | Typical Use |
|---|---|
| L0 | exploration and proof of life |
| L1 | bounded feature/product alignment |
| L2 | standard product development and customer delivery |
| L3 | AI core, regulated, money/safety/privacy impact, complex multi-agent |

Higher assurance wins when signals conflict. Mode never expands artifact scope
by itself.

## 2. Load Only What The Task Needs

Read no more than the matching stage references and triggered add-ons.

| Need | Read |
|---|---|
| ambiguous input, customer material, prototype/legacy inventory, unknown domain | `references/discover.md` |
| material unknowns need active, one-question-at-a-time convergence | `references/schema-grill.md` |
| Product Truth, module/flow/page/action/state/data specification | `references/specify.md` |
| capabilities, ToB/ToG/regulated/greenfield/brownfield, domain selection | `references/composition.md` |
| executable/clickable prototype | `references/prototype-testability.md` + `references/handoff.md` |
| Human-First, Coding Agent, QA, customer projection | `references/handoff.md` |
| change, version evolution, impact, migration | `references/change.md` |
| review, acceptance, evidence, domain maturity, release evaluation | `references/verify.md` |
| launch, operation, adoption, renewal, retirement | `references/operate.md` |
| realtime/SSE/WebSocket/countdown/push | `references/realtime-contract.md` |
| micro-change, regulated scope, large truth, or context pressure | `references/context-planning.md` |
| long chain, resume, multi-agent, staging/production, or formal audit | `references/execution-gates.md` |

Do not load every domain or reference "for safety". Default task budget:

- one or two stage references;
- zero or one dedicated domain pack;
- only triggered capability/governance rules;
- no historical docs, README, examples, or CHANGELOG at runtime.

For unusually small, regulated, or large work, generate an adaptive Context
Plan from `spec.config.yaml` or the versioned example. Context planning may
strengthen gates and retrieve Product Truth slices; it cannot change domain
maturity or silently truncate P0 behavior.

For long-running discovery, start with
`schemas/discovery-contract.schema.json`; do not fabricate a complete Product
Truth merely to create an execution checkpoint.

## 3. Canonical Product Truth

Use `schemas/product-truth.schema.json`. Product Truth contains stable facts:

```text
source/assertion/decision/unknown/conflict/feature
role/module/entity/field
flow/view/region/action
state/rule/event/integration
acceptance/evidence/change/projection
```

Human-First PRD, prototype, Coding Agent spec, QA acceptance, and customer
contract are projections from the same IDs. Never maintain separate truths.

Core rules:

- Evidence precedes assertion. Mark `verified`, `inferred`, `proposed`,
  `unknown`, or `conflict`.
- Every primary action has visible and domain results.
- Every lifecycle change has owner, guard, next state, event/audit, failure,
  and acceptance.
- Every field has meaning, source, type/dictionary, editability, sensitivity,
  and validation when applicable.
- Every cross-module flow has object ownership, mapping, event/command,
  failure/compensation, reconciliation, and evidence.
- Stable IDs are not reused for different behavior.
- Every approved in-scope `FEAT-*` links source evidence to behavior and
  acceptance; deferred, unknown, and not-applicable scope remains explicit.

## 4. Domain-Agnostic By Default

Read `references/domain-coverage.yaml` before using a dedicated domain file.

Three modes:

| Mode | Behavior |
|---|---|
| generic | discover roles, objects, lifecycle, workflow, data, risk, and acceptance from project evidence |
| project domain capsule | create scoped vocabulary/entities/states/workflows/policies/sources/unknowns/scenarios |
| dedicated domain pack | reuse matched, maturity-aware professional knowledge and tests |

No domain pack means more discovery and owner confirmation, not inability to
deliver. Do not claim production validation from a domain file, mocked scenario,
or simulated reviewer.

Use `schemas/project-domain-capsule.schema.json` when the capsule becomes a
reusable project artifact.

When domains compose, use `references/composition.md` to resolve object/state/
event/permission/metric/failure ownership. AI/data packs may narrow permission
but cannot expand the owning business domain's authority.

## 5. Work Paths

Choose only the stages required by the request:

```text
Discover (产品发现与策略)
-> Specify (需求澄清、范围与统一规格)
-> Plan (工程方案与交接规划)
-> Tasks (任务拆解与 Coding Agent 切片)
-> Build/Verify (构建、验收测试与追溯)
-> Launch (上线与交付)
-> Learn/Retire (运营、学习与退役)
```

- Specify: what, why, behavior, boundary, acceptance.
- Plan: implementation seams, dependencies, risk, migration, rollout.
- Tasks: vertical slices tied to visible/domain result and AC IDs.
- Build/Verify: implementation and evidence, never automatic launch approval.

For ToB/ToG, also model customer and governance lifecycle when in scope. PRD is
not a project tracker: keep WBS, bugs, daily follow-up, and support tickets in
their own artifacts linked by stable IDs.

## 6. Projections

Select the smallest view that satisfies the consumer:

| View | Required Output |
|---|---|
| Contract Summary | outcome, scope, decisions, gaps, upgrade triggers |
| Human-First | scenario-first module slices, page/action effects, rules, exceptions, flow/data, acceptance |
| Prototype | stable test/action/field/state anchors and demo-closed behavior |
| Coding Agent | source order, repository baseline, contracts, vertical tasks, tests, forbidden invention |
| QA | AC paths, evidence requirements, regression and failure cases |
| Customer | scope, responsibility, deliverables, exclusions, acceptance, change control |

Use templates only as projection aids:

- `references/templates/prd-light-template.md`
- `references/templates/human-first-prd-template.md`
- `references/templates/ai-coding-prd-template.md`
- `references/templates/product-truth-template.yaml`

## 7. Change Instead Of Regeneration

For an existing baseline, use `schemas/change-package.schema.json` and
`references/change.md`. Record `CHG-*`, impacted IDs, compatibility, migration,
regression, evidence, rollout, and rollback. Update Product Truth, then
regenerate only affected projections.

Brownfield work starts with current-state and interaction parity evidence. Do
not silently remove existing views, actions, states, integrations, data, or
contract behavior.

## 8. Gates

Apply only gates triggered by scope, but never weaken in-scope quality.

1. Discovery: outcome, sources, scope, owners, risk, P0 unknowns.
2. Product Truth: role/flow/page/action/state/data/exception/AC closure.
3. Prototype: every primary action has observable and durable behavior.
4. Handoff: target consumer can proceed without inventing business behavior.
5. Acceptance: AC IDs can produce named evidence.
6. Change: impact, compatibility, migration, regression, rollback.
7. Launch/Operate: readiness, support, observability, adoption, retirement.
8. Domain: source/applicability, behavioral evaluation, expert evidence,
   honest maturity.

For long-running or governed work, create an execution checkpoint and rerun
the six micro-gates before each stage transition. A classifier may strengthen
rigor but cannot award domain maturity or human approval. Use
`references/execution-gates.md`.

Completion is scoped:

- `PASS`: required gates have evidence;
- `REVIEW_COMPLETE_WITH_GAPS`: useful result with named gaps and owners;
- `BLOCKED`: a P0 decision or external condition prevents safe progress.

Never infer completion from `PASS` text embedded in a template/reference.

## 9. Deterministic Tools

Use scripts instead of retyping repeatable logic:

```powershell
py -3 scripts/ai_delivery_spec_cli.py init-delivery --output delivery
py -3 scripts/ai_delivery_spec_cli.py check
py -3 scripts/validate_product_truth.py delivery/truth/product-truth.yaml
py -3 scripts/plan_context.py --truth delivery/truth/product-truth.yaml --config delivery/spec.config.yaml
py -3 scripts/query_product_truth.py --truth delivery/truth/product-truth.yaml --id MOD-EXAMPLE --output working-slice.yaml
py -3 scripts/manage_execution_state.py create --truth delivery/truth/product-truth.yaml --config delivery/spec.config.yaml --installed-skill path/to/SKILL.md --output delivery/evidence/execution/state.yaml
py -3 scripts/manage_execution_state.py create --discovery-contract discovery.yaml --config delivery/spec.config.yaml --installed-skill path/to/SKILL.md --output delivery/evidence/execution/state.yaml
py -3 scripts/manage_execution_state.py checkpoint --state state.yaml --truth delivery/truth/product-truth.yaml --output next-state.yaml
py -3 scripts/manage_execution_state.py record-turn --state state.yaml --output next-turn-state.yaml
py -3 scripts/compile_clarification_transcript.py --contract discovery.yaml --transcript transcript.yaml --decision READY_FOR_PRODUCT_TRUTH --output discovery-next.yaml
py -3 scripts/extract_interaction_ledger.py --input prototype.html --output interaction-ledger.json
py -3 scripts/validate_projection_consistency.py --truth delivery/truth/product-truth.yaml --projection delivery/projections/human-first-prd.md
```

Use `python` when available outside Windows.

## 10. Final Self-Check

Before handoff:

- triage, lifecycle, shape, consumer, mode, and tier are explicit;
- only relevant references/packs were loaded;
- adaptive Context Plan/slicing was used when size or risk required it;
- Product Truth or an explicitly lighter artifact is the named source;
- supplied evidence has no silent omission;
- P0 unknowns/conflicts have owners;
- projections preserve stable IDs and do not contradict truth;
- acceptance names required evidence;
- domain maturity and validation claims are honest;
- final state names verification performed and unresolved risks.

Final response states created/updated artifacts, verification, scope, and one
completion state.
