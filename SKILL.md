---
name: ai-delivery-spec
description: >-
  Use whenever Codex must create or review a product lifecycle delivery artifact for
  decision, development, verification, release, operation, or retirement: strategy handoff,
  PRD, executable prototype, role path, DDD/API contract, test/UAT evidence, readiness record,
  post-launch review, cross-border spec, or AI runtime/evaluation contract. Supports validation
  and handoff. Do not use for code-only syntax/debugging, copy rewriting, or idea exploration
  with no delivery intent.
---

# AI Delivery Spec — AI Native 软件交付协议 (v4.1.0 Lifecycle Review Baseline)

> 作者：李康（Li Kang） | 版本：v4.1.0 | 原则：全生命周期单产物评审、精准触发、意图证据、范围优先、明确停止、分级交付、确定性路由、场景回归、区域配置、条件 Gate、ToB/ToG 通用模式、AI Native 与 AI 嵌入分流、领域插件化、可审计可开发可验证。

## 1. Core Rule

Do not force every artifact through the full pipeline. Identify its lifecycle stage, then choose artifact scope, execution mode, and delivery tier where applicable. Review only the requested artifact and the evidence required to judge it.

Every accepted deliverable must answer:

```text
artifact purpose -> accountable consumer/decision -> evidence or contract
-> downstream acceptance -> unresolved risk and next action
```

For behavior-defining artifacts, also preserve:

```text
user/role -> operation path -> visible result -> domain result -> verification
```

## 2. Loading Strategy

Load only what is needed.

1. Always start with this `SKILL.md`.
2. Load `references/delivery-tier-model.md` when tier or scope is unclear.
3. Load `references/delivery-core.md` for Stage 0 reverse engineering, PRD, story/state, or standard delivery.
4. Load conditional references only when their trigger applies.
5. Do not preload all references at Stage 0.

### 2.1 Lifecycle Stage, Scope, Mode, And Tier

First identify the artifact stage: `discovery`, `definition`, `design`, `engineering`, `verification`, `release`, `operation/learning`, or `retirement`. Stage selects review criteria; it does not expand scope or determine rigor.

These remain independent decisions:
- **Artifact scope**: one requested artifact, a bounded module package, or a full delivery package.
- **Execution mode**: how broadly to work in this request.
- **Delivery tier**: how rigorous the in-scope artifact must be.

Do not create missing package artifacts unless the user requests a package or they are necessary to make the requested artifact valid. Report them as package gaps instead.

| Mode | Use When | Execution Rule | Stop Boundary |
|---|---|---|---|
| Lite | quick validation, one requested artifact, or bounded review | Work only on the named artifact/path and the minimum evidence needed to judge it. | requested artifact verified + gaps/upgrade triggers listed |
| Standard | normal product delivery, development/QA handoff, or a requested module package | Produce the requested artifacts and run applicable gates/plugins. | requested package verified + unresolved decisions listed |
| Full | user requests a complete package, formal acceptance, or launch readiness | Complete all artifacts required by the selected tier and triggered readiness gates. | full package manifest and readiness result completed |

Mode rules:
- Mode and tier are orthogonal. A Lite review may inspect one L2/L3 artifact without downgrading its rigor; a non-AI L2 production launch may use Full mode without becoming L3.
- Select mode from current destination evidence, not speculation about possible future use.
- Lite signals: “先看方向 / 快速验证 / 粗略 / 草稿 / one-page / 只看这一个产物”, with no higher-assurance destination signal.
- Standard signals: development team, QA/test cases, procurement, bid/tender, customer demo, implementation handoff, or a multi-role lifecycle.
- Full signals: formal acceptance, production launch, migration/cutover, release readiness, on-call/rollback, or an explicitly complete package.
- Higher assurance wins when signals conflict: `Full > Standard > Lite`. Example: “先快速做个原型，下周给客户演示” is Standard.
- Mode never expands artifact scope by itself. “只审这份 PRD，开发下周开工” is a Standard single-artifact review, not an automatic full package.
- When destination evidence is absent, choose Lite, state the assumption, and list concrete upgrade signals. Do not guess that an artifact may someday be used for development or bidding.
- Lite is not permission to leave dead interactions: its scoped demo path must still close.
- AI centrality changes tier/gates for the affected module; it does not automatically determine execution mode.
- Pre-delivery strategy, post-launch evidence, incident review, and retirement artifacts inherit the product's approved tier when known. If no tier exists, record `tier: N/A (lifecycle governance)` and use destination/risk to choose review rigor; do not force them into L0-L3.

### 2.2 Iteration Stop Conditions

End with one explicit completion state:
- **PASS**: all applicable gates pass.
- **REVIEW_COMPLETE_WITH_GAPS**: the requested review is complete, but the artifact/package is not accepted; failures and next decisions are listed.
- **BLOCKED**: a required input is missing and cannot be safely inferred; the exact missing evidence is listed.

Stop expanding the delivery when all are true:
1. the requested artifact exists and can be opened, rendered, or executed as applicable;
2. every applicable gate has a result; failures are not relabeled as passes;
3. every in-scope primary path has a visible result, domain result, and verification evidence appropriate to the tier;
4. required validation has completed and no necessary tool process is still running;
5. unresolved items are listed with impact, owner/decision role, and next decision, not silently filled by assumptions.

Do not continue into unrequested stages, optional plugins, extra documents, or speculative features after these conditions are met.

### 2.3 AI Centrality Test

Classify AI per scoped module, not once for the whole product:
- **AI-core**: the module's primary user outcome or critical path fails without AI, or AI chooses routes/tools and writes consequential state. Apply L3 AI Native gates to that module.
- **AI-supporting**: the deterministic/manual workflow remains valid and AI only classifies, extracts, summarizes, recommends, or drafts for human confirmation. Apply AI Feature Injection.
- **AI-incidental**: AI is only used to create the PRD, prototype, code, or test artifact. Do not trigger product AI gates.

For mixed products, keep the overall package at its normal tier and elevate only AI-core modules unless shared runtime risk requires a product-level L3 review. High-impact AI advice that remains non-binding and independently human-verified stays AI-supporting, but must add evaluation, evidence, and human-accountability checks.

## 3. Tiered Delivery Model

| Tier | Use When | Required Artifacts | Required Gates | Gates Skipped by Default |
|---|---|---|---|---|
| L0 Exploration Artifact | idea demo, quick HTML/flow/decision note, no dev handoff | requested exploration artifact, path/decision notes, known gaps | applicable Gate 2 Lite + Gate 4 Lite | DDD, AI harness, full PRD |
| L1 Light Product Contract | feature explanation, internal alignment, simple CRUD/workflow | requested artifact + light story/path and state notes | applicable Gate 1 Lite / Gate 2 / Gate 4 Lite | full DDD unless lifecycle-heavy |
| L2 Standard Product Delivery | ToB/ToG module, bid/demo package, dev handoff | full package when requested: PRD, prototype/demo evidence, story/state matrix, acceptance report | applicable Gate 1-4 | AI Native unless triggered |
| L3 AI Native / High-Risk Delivery | AI-core workflow, AI writes/acts, compliance/money/safety impact, multi-agent | L2 package when requested + AI runtime/harness/effect/ops contracts | applicable Gate 1-4 + conditional AI gates | none for the AI-core module unless explicitly de-scoped |

Rules:
- A lower-tier artifact is not a failure just because it skips a higher-tier gate.
- If a lower-tier artifact is later used for development, upgrade it to L1/L2 first.
- If AI output triggers business write, workflow task, customer commitment, compliance action, money, or safety impact, escalate to L3 or justify AI Feature Injection instead.
- Tier choice, inherited tier, or `N/A (lifecycle governance)` must be recorded in the final answer or handoff package.

Gate applicability by artifact scope:
- Strategic Discovery Handoff applies to strategy/discovery decision artifacts and new-market entry into delivery.
- Gate 1 applies to requirement, story, path, PRD, prototype, and test-traceability scope.
- Gate 2 applies only when a prototype, demo surface, executable workflow, or interaction claim is in scope.
- Gate 3 applies when a PRD, product-linked architecture/API/data contract, or development handoff is in scope.
- Gate 4 applies to every request, but packages only the artifacts actually requested; full L2/L3 packages must declare any missing artifact.
- System Readiness applies to release/pilot/operation/retirement artifacts or real-environment claims.

## 4. Core Gates

### Gate 1: Story-Path Verification

Every scoped function maps to a user story, role path, prototype action, state/domain result, and test case.

Fail if:
- feature has no user story;
- role has no executable path;
- path has UI result but no domain result;
- state-changing action has no transition/test.

Use: `references/story-path-verification.md`.

### Gate 2: Demo-Closed Prototype

The prototype must be executable enough for the selected tier.

Minimum:
- every primary `data-action` has a visible outcome;
- core create/view/edit/submit/review/analyze actions are not toast-only;
- mock data covers relevant happy/error/permission/state variants;
- old prototype iterations preserve or explicitly de-scope critical interactions.

Use: `references/prototype-testability.md`, `references/demo-closed-ddd-handoff.md`.

### Gate 3: Development Contract

For L2/L3, the PRD must be a development contract, not only a product narrative.

Required:
- inputs, outputs, processing logic, business transformation logic;
- aggregate/entity/value object/state/event/command/query/policy/invariant where applicable;
- Developer Fast-Lane table for coding entry;
- concrete tests with UI result and domain result.

Use: `references/demo-closed-ddd-handoff.md`.

### Gate 4: Acceptance Package

Final delivery includes only the artifacts required by the selected scope, tier, and triggered gates:
- prototype/demo path when interaction or demo scope applies;
- PRD/story/state files when PRD or development scope applies;
- verification report;
- unresolved risks and de-scope notes;
- test handoff checklist;
- packaging manifest when the output is a bid/customer/internal package.

Use: `references/delivery-acceptance-gates.md`, `references/artifact-packaging.md`.

## 5. Ordered Routing

Route in three passes. Do not force conditional capabilities into one exclusive decision tree.

1. **Choose one primary output route** from the requested deliverable.
2. **Add input modifiers** such as reverse engineering, packaging, or migration.
3. **Union all product plugins whose conditions are true**. Load each reference once; no matching condition means no plugin.

### 5.1 Primary Output Route — Choose One

| Requested Artifact | Review Route | Load |
|---|---|---|
| strategy, research synthesis, business case, roadmap decision | pre-delivery/lifecycle review; propose downstream tier only after decision | `strategy-discovery-handoff.md`, `delivery-acceptance-gates.md` |
| requirement, story inventory, role path, PRD, scope decision | L1/L2/L3 as destination/risk requires + Gate 1/3/4 | `delivery-core.md`, `story-path-verification.md`, `demo-closed-ddd-handoff.md`; load `templates/prd-light-template.md`, `templates/prd-standard-template.md`, or the AI Native template to match scope |
| IA, UX flow, design handoff, executable prototype, customer demo | selected tier + Gate 1/2/4 | `prototype-testability.md`, `story-path-verification.md`, `delivery-acceptance-gates.md` |
| product-linked architecture, API/schema/data/migration contract | L2/L3 + Gate 3/4; add readiness for real rollout | `demo-closed-ddd-handoff.md`, `delivery-acceptance-gates.md`, `system-readiness-checklist.md` when applicable |
| test plan, test cases, traceability matrix, UAT/acceptance report | inherited/selected tier + Gate 4; apply Gate 1/2/3 to the evidence under test | `story-path-verification.md`, `delivery-acceptance-gates.md` |
| pilot, release, rollout, runbook, operational readiness | inherited/selected tier + Full when production-critical + Readiness | `system-readiness-checklist.md`, `templates/system-readiness-checklist-template.md` |
| post-launch metrics, experiment/effect report, incident or delivery retrospective | inherited tier or lifecycle governance + evidence review; add AI Effect when AI claims exist | `delivery-acceptance-gates.md`, `ai-effect-evaluation.md` when applicable |
| deprecation, sunset, tenant/provider migration, data export/deletion, product retirement | inherited tier or lifecycle governance + Retirement Profile | `system-readiness-checklist.md`, `artifact-packaging.md` |

### 5.2 Input And Governance Modifiers — Add When True

| Condition | Add | Load |
|---|---|---|
| existing HTML/prototype/legacy version/screenshot | interaction baseline and drift review | `delivery-core.md`, `build-governance.md` |
| new product/market, major investment, repositioning, commercialization | strategic handoff before Stage 1 | `strategy-discovery-handoff.md` |
| bid, customer, internal archive, acceptance, release, or retirement package | packaging manifest and package-specific evidence | `artifact-packaging.md` |
| prompt/model/tool registry, rollback, prompt tests | Prompt Ops Gate | `prompt-registry-integration.md`, `prompt-registry.yaml` |
| patch scripts, generated HTML, repeated transforms | Build Governance Gate | `build-governance.md` |
| new industry/company/domain module | Domain Switch Gate | `domain-module-template.md` plus the selected domain module |
| traffic safety domain | traffic domain contract and scenarios | `domain-traffic.md`, `domain-traffic-safety-scenarios.md` |
| CRM domain | CRM domain contract | `domain-crm.md` |
| skill upgrade or old project re-evaluation | migration review | `skill-version-migration.md`, `skill-design-benchmark.md` |

### 5.3 Product Plugins — Add All Matching Rows

| Condition | Add | Load |
|---|---|---|
| AI-supporting: manual/deterministic path remains valid | AI Feature Injection Gate | `ai-feature-injection.md`; add `prompt-registry-integration.md` for L2+/managed prompt lifecycle |
| AI-core: primary outcome depends on AI or AI writes/routes/acts | AI Native Harness Gate and L3 rigor for that module | `ai-native-harness-engineering.md`, `ai-runtime-ops.md`, `ai-effect-evaluation.md`; add `templates/ai-native-prd-template.md` for PRD scope and Prompt Ops for L2+/production |
| mobile/H5/app/mini-program/field user | Mobile Delivery Gate | `mobile-product-delivery.md` |
| PC plus mobile/mini-program/app | Multi-Surface Consistency Gate | `multi-surface-consistency.md` |
| approval, escalation, countersign, audit workflow | Approval Workflow Gate | `approval-workflow.md` |
| SaaS, org tree, tenant, RBAC, license/seat | SaaS Multitenancy Gate | `saas-multitenancy.md` |
| indicator, report, BI, data mart, dashboard | Reporting/Analytics Gate | `reporting-analytics.md` |
| low-code builder, node workflow, connector automation | Workflow Automation / Low-Code Gate | `workflow-automation-lowcode.md` |
| overseas launch, multiple countries/regions/languages, cross-border users/data, regional deployment | Global/Regional Readiness Profile | `system-readiness-checklist.md`; add `saas-multitenancy.md`, `ai-runtime-ops.md`, `mobile-product-delivery.md`, `ai-effect-evaluation.md` as applicable |
| production launch, migration, rollback, on-call readiness | System Readiness Gate | `system-readiness-checklist.md`, `templates/system-readiness-checklist-template.md` |

## 6. Lifecycle And Delivery Pipeline

The product lifecycle is broader than the build pipeline:

```text
Discover/Decide -> Define/Design -> Build -> Verify -> Release
-> Operate/Learn -> Iterate or Retire
```

Review the artifact at its current stage. Do not require adjacent-stage artifacts unless they are necessary evidence or the user requests a package.

Inside definition/build work, core stages stay simple. Conditional plugins attach to the relevant stage.

The pipeline is a routing model, not a mandatory checklist. Skip any stage whose input is already supplied and validated. Stage 0 runs only when an existing artifact is being analyzed or iterated.

```text
Stage 0  Existing artifact / reverse engineering
Stage 1  Opportunity and scope
Stage 2  Stakeholder and tier
Stage 3  Requirement design
Stage 4  Stories, role paths, states
Stage 5  PRD, prototype, acceptance package
```

Optional plugins:
- Before Stage 1: strategic discovery handoff for new product/market, major investment, repositioning, or commercialization.
- Stage 0: interaction ledger, patch-chain drift, build manifest.
- Stage 3: AI feature injection, AI-native scenario, approval/multitenancy/reporting/workflow domain model.
- Stage 4: mobile/multi-surface paths, RBAC matrix, approval state machine, indicator lineage, workflow graph, connector contracts, locale/region behavior.
- Stage 5: DDD handoff, Developer Fast-Lane, prompt registry, effect evaluation, regional readiness, workflow execution acceptance, system readiness, packaging manifest.
- After Stage 5: UAT/acceptance, release readiness, post-launch evidence, incident learning, deprecation/retirement as independently reviewable artifacts.

Lite fast path:

```text
confirm requested artifact, outcome, and rigor tier
-> build/review the single requested artifact
-> verify the scoped demo/story path
-> list known gaps and upgrade triggers
-> stop
```

## 7. Complexity Budget

Budget is tier-aware.

| Tier | PRD | States | Actions | APIs | AI Agents | Expected Fit |
|---|---:|---:|---:|---:|---:|---|
| L0 | optional | <= 8 | <= 20 | optional | 0 | demo only |
| L1 | <= 6pp | <= 12 | <= 30 | <= 10 | <= 1 | internal alignment |
| L2 | <= 15pp | <= 25 | <= 60 | <= 30 | <= 3 | standard dev |
| L3 | modular | per bounded context | per module | per service | <= 8 | AI-native/high-risk |

Counting:
- action = business action name + guard combination + domain result;
- same action across surfaces counts once if guard/domain result match;
- reporting metric actions count by query/calculation/write behavior, not by chart count;
- over-budget is allowed only with owner, reason, de-scope or split plan.

Use `references/delivery-core.md` for state/action/API/agent counting boundaries and PASS/FAIL examples. Do not claim a PRD page count until it is rendered to a defined page size.

## 8. Review Model

Run only the reviewers needed by tier and triggers.

| Reviewer | Required When | Checks |
|---|---|---|
| Sponsor | L2+ or strategic/cost/compliance commitment | outcome, cost, compliance, overclaim |
| End User | L0+ | path usability, missing steps |
| Peer PM | L1+ | scope, state, story completeness, tier fit |
| Dev Lead | L2+ | implementation contract, hidden complexity |
| QA/Eval | L2+ or AI | testability, regression, eval design |
| AI Architect | AI Feature Injection / L3 | context, prompt/tool/runtime feasibility |
| Ops/SRE | L3 or production automation | observability, rollback, kill switch |

## 9. Cross-File Consistency Rules

- Every PRD feature maps to a story id.
- Every story id maps to role path, prototype action, state/domain result, and test case.
- Every lifecycle object has a state-button matrix.
- Every primary prototype action maps to command/query or is explicitly prototype-only.
- Every domain write has audit/event and permission guard.
- Every AI prompt/model/tool change declares impact surface, linked tests, rollback owner, and observability signal.
- Every multi-surface feature declares what is shared and what differs by surface.
- Every global/multi-region feature declares target markets, locale behavior, data/model region, transfer boundary, and per-locale evaluation evidence.
- Strategic market, competitor, and differentiation claims are required only when the Strategic Discovery Handoff Gate triggers; every claim must identify evidence, assumptions, confidence, and validation plan.

## 10. Required Scripts

When analyzing old prototypes, prefer the bundled ledger extractor:

```powershell
python references/../scripts/extract_interaction_ledger.py --input path/to/prototype.html --output interaction-ledger.json
```

If the script misses minified/external behavior, supplement with browser/DOM verification and mark UNKNOWN.

When modifying this skill, run:

```powershell
python scripts/validate_skill_consistency.py
python scripts/validate_routing_scenarios.py
```

## 11. Final Response Rule

When delivering work, state:
- lifecycle stage, artifact type, downstream consumer/decision;
- selected artifact scope, execution mode, and destination evidence;
- selected tier, inherited tier, or `N/A (lifecycle governance)`;
- triggered conditional gates;
- created/updated artifacts;
- verification performed;
- completion state: PASS / REVIEW_COMPLETE_WITH_GAPS / BLOCKED;
- unresolved risks or approved de-scopes.
