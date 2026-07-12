---
name: ai-delivery-spec
description: Turn rough product ideas, customer materials, prototypes, legacy systems, or approved changes into traceable Product Truth, Human-First requirements, complete AI Coding PRDs, testable prototypes, structured acceptance, and coding-agent handoffs. Use for ToC clarification/light PRDs, ToB/ToG delivery, multi-role workflows, product/domain modeling, AI/data products, brownfield change, customer acceptance, launch, or operations. Excludes unrelated code debugging and copy rewriting.
---

# AI Delivery Spec 5.0.2 — Product Delivery Kernel

> 首次使用推荐：先跑 Ultra-Light 轻量模式快速体验。
>
> 切换领域：指令末尾加 `domain=traffic` 即可启用交通垂类规则。
>
> 完整文档：见 `README.md`。

Maintain one evidence-backed product contract and project it for users,
product, engineering, QA, customers, coding agents, and operations.

## 1. Triage Before Loading

Declare:

```text
[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false] | [INFO: complete|partial|missing]
Lifecycle: discover|specify|plan|tasks|build_verify|launch|learn_retire
Shape: greenfield|brownfield|hybrid
Consumer: human|prototype|coding_agent|qa|customer|operations
Override: mode=ultra_light|lite|standard|full; tier=L0|L1|L2|L3|L4; domain=generic|<pack>
```

- Recommend `Ultra-Light` only for one reversible page/copy/field/rule change,
  one primary role, no cross-module state, sensitive decision, migration, or
  customer acceptance. Output one requirement card, assumptions, and positive/
  negative AC; do not create Product Truth unless risk escalates.
- `Heavy` includes development, QA, customer delivery, production, migration,
  regulated behavior, multi-role workflow, or a complete AI Coding PRD.
- Product behavior using a model/agent is `AI: true`; AI only writing artifacts
  or code is `false`.
- Approval, escalation, cross-module state, audit, or long-running work sets
  `WORKFLOW: true`.
- Mark information partial/missing only when an unknown can change outcome,
  scope, owner, role, state, data authority, compliance, commercial promise, or
  acceptance. Do not repeat discovery after the user has approved these.

Higher assurance wins. Mode controls artifact breadth; tier controls rigor.
Manual mode/tier/domain overrides are always accepted unless they would hide a
P0 safety or compliance risk.

## 2. Load Only The Triggered References

| Need | Read |
|---|---|
| source/prototype/legacy inventory or ambiguity | `references/discover.md` |
| active clarification | `references/runtime/schema-grill.md` |
| Product Truth and behavior specification | `references/specify.md` |
| complete AI Coding PRD | `references/runtime/ai-coding-completeness.md` + `references/templates/ai-coding-prd-template.md` |
| Human-First/Coding/QA/customer projection | `references/handoff.md` |
| executable prototype | `references/runtime/prototype-testability.md` + `references/handoff.md` |
| capability/domain composition | `references/runtime/composition.md` |
| change/migration/rollback | `references/runtime/change.md` |
| review/evidence/domain assurance | `references/runtime/verify.md` |
| launch/operate/retire | `references/runtime/operate.md` |
| realtime/push/countdown/SSE/WebSocket | `references/runtime/realtime-contract.md` |
| large project/context pressure | `references/runtime/context-planning.md` |
| long chain/formal checkpoint | `references/runtime/execution-gates.md` |
| GLM/Qwen/DeepSeek/Kimi/WorkBuddy/Trae/Qoder/Cursor | matched `agents/domestic/*.md` + `agents/domestic/china-tools.md` |

Load one or two stage references, zero or one matched domain pack, and only
triggered governance rules. Do not load README, history, examples, every domain,
or every reference during runtime.

## 3. Choose The Work Path

```text
Discover 产品发现 → Specify 统一需求契约 → Plan/Tasks 工程交接
→ Build/Verify 构建验收 → Launch 上线 → Learn/Retire 运营与退役
```

- For an idea, clarify outcome, opportunity/problem, hypothesis, assumptions,
  risks, metric, and next validation before a full PRD.
- For customer material or an existing prototype, perform Stage 0 inventory:
  views, roles, states, actions/handlers, entities/fields, metrics, sources,
  unresolved gaps, and preserved behavior.
- When scope is approved and the user requests a complete AI Coding PRD, use
  the Complete Contract Route in §5. Do not return a thin projection.
- For existing baselines, record `CHG-*`, impact, compatibility, migration,
  regression, rollout, and rollback in `schemas/change-package.schema.json`;
  regenerate only affected projections.

## 4. Canonical Product Truth Without Monolith Deadlocks

Product Truth owns stable facts and IDs:

```text
source/assertion/decision/unknown/conflict/feature
role/module/entity/field/flow/view/region/action
state/rule/event/integration/acceptance/evidence/change/projection
```

Use `schemas/product-truth.schema.json`. Core invariants:

- Evidence precedes assertions; mark verified/inferred/proposed/unknown/conflict.
- Every primary action has visible and domain results.
- Every state change has owner, guard, next state, event/audit, failure, and AC.
- Every field has meaning, source, type/dictionary, editability, sensitivity,
  and validation when applicable.
- Every cross-module flow has ownership, mapping, command/event, failure/
  compensation, reconciliation, and evidence.
- Every approved `FEAT-*` links source, behavior, and AC; deferred/out-of-scope/
  unknown behavior remains explicit.

### Progressive Truth is the large-project default

Never ask an agent, subagent, Trae, or WorkBuddy to generate/rewrite one large
`product-truth.yaml` in a single pass. Use:

```text
delivery/truth/index.yaml
delivery/truth/fragments/00-core.yaml
delivery/truth/fragments/MOD-*.yaml
delivery/truth/compiled/product-truth.yaml
```

Write one fragment per module/flow slice, validate it, update its checkpoint,
then compile deterministically. The index is the authoring source; the compiled
file is the read-only canonical projection for existing tools. Use monolith only
for bounded projects that fit comfortably in one context.

## 5. Complete AI Coding PRD Route

Use when consumer is `coding_agent` and the user asks for a complete/final/
directly generatable PRD.

1. Lock a complete contract index: sources, modules, roles, journeys, views,
   flows, entities, fields, states, integrations, metrics, and P0 AC IDs.
2. Write Product Truth and PRD by ID slice; checkpoint each accepted module.
3. Assemble `references/templates/ai-coding-prd-template.md` without dropping
   sections. Use `Not applicable + reason + future trigger`, never an empty
   heading.
4. Require repository baseline; role/permission/data scope; IA/page layout;
   fields/data flow; state/recovery; concrete API request/response/errors/
   idempotency; versioned event payloads; integration/reconciliation; NFR;
   metrics caliber; vertical files/dependencies; machine AC; deployment/
   migration/rollback/operations; and forbidden invention.
5. Run `validate_coding_agent_contract.py --level L2 --profile full_prd` (L3
   for AI/high-risk). Fix the contract; never lower the level to obtain PASS.
6. Cross-check every role journey and P0 flow against the IA/prototype and AC.

Do not end after an outline, one module, one role, one validator, or one
prototype page when the requested package is larger.

## 6. Smart Large-Project Mode

Trigger when any two are true: 8+ roles, 12+ modules/views, 40+ actions, 80+
fields, 5+ sources, 3+ integrations, or PRD + prototype + coding/QA handoff.

1. Inventory the complete ID graph once.
2. Generate a Context Plan and declare pressure `low|medium|high`.
3. At medium pressure, stop reloading sources and work from approved IDs.
4. At high pressure, checkpoint the current fragment/section and start the next
   slice. Never merge roles or omit P0 states, permissions, exceptions, API
   contracts, or AC to save tokens.
5. Assemble and run global closure only after all slices pass locally.

Lite/Ultra-Light may trim prose and optional projections, not approved P0
behavior. If a safe slice does not fit, split it again or report a named P0
blocker.

## 7. Domain Use And Honest Evidence

Read `references/domain-coverage.yaml` before a file in `references/domains/`.

- `practice_status` answers whether methods have been used in shipped projects.
- `maturity` answers whether this reusable pack revision has sourced knowledge,
  behavioral evaluation, accountable review, and audit evidence.
- `production_practiced + experimental` is valid: it prevents denying real
  delivery experience while forbidding unsupported universal claims.

No matched pack means build a project-scoped Domain Capsule with
`schemas/project-domain-capsule.schema.json`; it never prevents
delivery. Composition may narrow permissions but cannot expand the owning
business domain's authority.

## 8. Projection And Prototype Closure

Generate only the views needed by the consumer, but preserve the same IDs.
Interactive prototypes must be usable:

```text
data-testid <- VIEW/REG/AC
data-action <- ACT
data-field  <- FLD
data-state  <- state enum
data-api    <- command/API
```

Every `data-action` needs a handler and visible outcome. Preserve existing
interaction coverage unless explicitly de-scoped. Verify JavaScript syntax,
all important role journeys, state/failure paths, and representative data.

## 9. Gates And Completion

Apply triggered gates without weakening in-scope quality:

1. discovery: sources, outcome, scope, owner, risks, P0 unknowns;
2. truth: role/flow/page/action/state/data/exception/AC closure;
3. prototype: every primary action has observable durable behavior;
4. handoff: target consumer proceeds without inventing business behavior;
5. acceptance: AC IDs produce named evidence;
6. change/launch: compatibility, migration, regression, rollout, rollback,
   support, and observability;
7. domain: practice and reusable-pack assurance claims remain distinct.

Completion is scoped: `PASS`, `REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`.
Embedded PASS text is never execution evidence.

## 10. Deterministic Commands

```powershell
py -3 scripts/ai_delivery_spec_cli.py init-delivery --output delivery
py -3 scripts/ai_delivery_spec_cli.py compile-truth --index delivery/truth/index.yaml
py -3 scripts/plan_context.py --truth delivery/truth/compiled/product-truth.yaml --config delivery/spec.config.yaml
py -3 scripts/query_product_truth.py --truth delivery/truth/compiled/product-truth.yaml --id MOD-EXAMPLE --output working-slice.yaml
py -3 scripts/validators/validate_product_truth.py delivery/truth/compiled/product-truth.yaml
py -3 scripts/validators/validate_prd_quality.py delivery/projections/human-first-prd.md --level L2
py -3 scripts/validators/validate_ia_skeleton.py delivery/ia-skeleton.yaml --level L2
py -3 scripts/validators/validate_coding_agent_contract.py delivery/projections/ai-coding-prd.md --level L2 --profile full_prd
py -3 scripts/extract_interaction_ledger.py --input prototype.html --output interaction-ledger.json
py -3 scripts/render_mermaid_flow.py --truth delivery/truth/compiled/product-truth.yaml --output delivery/projections/flow.mmd
```

Use `python` outside Windows when available.

## 11. Final Self-Check

- triage, lifecycle, shape, consumer, mode, tier, and source precedence are clear;
- approved source material has no silent omission;
- all roles, journeys, flows, states, permissions, failures, and P0 AC close;
- complete AI Coding requests pass the full contract validator;
- large work used fragments/checkpoints instead of monolithic generation;
- projections and prototype preserve IDs and interaction coverage;
- evidence, practice, maturity, gaps, and completion state are honestly named.
