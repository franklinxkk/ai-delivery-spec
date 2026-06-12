---
name: ai-delivery-spec
description: >-
  Use when a product delivery artifact must be ready for development, demonstration,
  acceptance, or governance: PRD, executable prototype, role path, DDD handoff,
  ToB/ToG workflow or RBAC contract, multi-surface or analytics spec, and AI
  feature/agent/runtime/evaluation contract. Supports quick validation and full handoff.
  Do not use for standalone coding, generic HTML implementation, casual brainstorming,
  or copy editing.
---

# AI Delivery Spec — AI Native 软件交付协议 (v4.0.5 Scope & Consistency Hardening)

> 作者：李康（Li Kang） | 版本：v4.0.5 | 原则：精准触发、范围优先、快速路径、明确停止、分级交付、条件 Gate、ToB/ToG 通用模式、AI Native 与 AI 嵌入分流、多端一致性、领域插件化、可演示可开发可测试。

## 1. Core Rule

Do not force every task through the full pipeline. Choose artifact scope, execution mode, and delivery tier, then apply only the relevant gates and conditional plugins.

Every accepted deliverable must answer:

```text
who uses it -> what path they walk -> what visible result appears
-> what domain result changes -> how dev/test can verify it
```

## 2. Loading Strategy

Load only what is needed.

1. Always start with this `SKILL.md`.
2. Load `references/delivery-tier-model.md` when tier or scope is unclear.
3. Load `references/delivery-core.md` for Stage 0 reverse engineering, PRD, story/state, or standard delivery.
4. Load conditional references only when their trigger applies.
5. Do not preload all references at Stage 0.

### 2.1 Scope, Mode, And Tier

These are independent decisions:
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
- Explicit requests such as “快速验证 / 粗略原型 / 先看方向 / one-page / 只审这份 PRD” select Lite unless the user requests a package.
- When ambiguous, choose the least costly mode that can satisfy the stated outcome and record the assumption.
- Lite is not permission to leave dead interactions: its scoped demo path must still close.
- Upgrade Lite to Standard when the artifact will guide development, QA, procurement, bidding, customer acceptance, or a multi-role lifecycle.
- Upgrade Standard to Full only when the user needs a complete package, formal acceptance, or launch readiness.
- AI centrality changes tier/gates for the affected module; it does not automatically determine execution mode.

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
- Tier choice must be recorded in the final answer or handoff package.

Gate applicability by artifact scope:
- Gate 1 applies to story/path/PRD/prototype scope.
- Gate 2 applies only when a prototype, demo surface, executable workflow, or interaction claim is in scope.
- Gate 3 applies when a PRD or development handoff is in scope.
- Gate 4 applies to every request, but packages only the artifacts actually requested; full L2/L3 packages must declare any missing artifact.

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

Final delivery includes the artifacts appropriate to the tier:
- prototype path;
- PRD/story/state files when required;
- verification report;
- unresolved risks and de-scope notes;
- test handoff checklist;
- packaging manifest when the output is a bid/customer/internal package.

Use: `references/delivery-acceptance-gates.md`, `references/artifact-packaging.md`.

## 5. Conditional Gates

| Trigger | Gate | Load |
|---|---|---|
| New product/market, major investment, repositioning, commercialization, board/fundraising decision | Strategic Discovery Handoff Gate | `strategy-discovery-handoff.md` |
| Existing HTML/prototype/legacy version | Interaction Baseline + Drift Detection | `delivery-core.md`, `build-governance.md` |
| AI-supporting module: deterministic/manual workflow remains valid | AI Feature Injection Gate | `ai-feature-injection.md`, `prompt-registry-integration.md` |
| AI-core module: primary outcome depends on AI, agentic automation, or high-risk AI write/action | AI Native Harness Gate | `ai-native-harness-engineering.md`, `ai-runtime-ops.md`, `ai-effect-evaluation.md` |
| Mobile/H5/app/mini-program/field user | Mobile Delivery Gate | `mobile-product-delivery.md` |
| PC + mobile + mini-program/app surfaces | Multi-Surface Consistency Gate | `multi-surface-consistency.md` |
| ToB/ToG approval, escalation, audit workflow | Approval Workflow Gate | `approval-workflow.md` |
| SaaS, org tree, multi-tenant, RBAC, license/seat | SaaS Multitenancy Gate | `saas-multitenancy.md` |
| Indicator, report, BI, data mart, dashboard, report builder | Reporting/Analytics Gate | `reporting-analytics.md` |
| Prompt/model/tool registry, rollback, prompt tests | Prompt Ops Gate | `prompt-registry-integration.md`, `prompt-registry.yaml` |
| Low-code app builder, node workflow, connector/integration automation | Workflow Automation / Low-Code Gate | `workflow-automation-lowcode.md` |
| Production launch, release, migration, rollback, on-call readiness | System Readiness Gate | `system-readiness-checklist.md` |
| Patch scripts, generated HTML, repeated transforms | Build Governance Gate | `build-governance.md` |
| New industry/company/domain module | Domain Switch Gate | `domain-module-template.md`, current domain module |
| Skill upgrade or old project re-evaluation | Skill Version Migration Gate | `skill-version-migration.md` |

## 6. Module Map

| Need | Load |
|---|---|
| Strategy/discovery evidence entering delivery | `references/strategy-discovery-handoff.md` |
| Tier selection and gate downgrade/upgrade | `references/delivery-tier-model.md` |
| Reverse-engineer existing artifacts | `references/delivery-core.md` |
| Prototype semantic annotations and testids | `references/prototype-testability.md` |
| Story, role path, coverage matrix | `references/story-path-verification.md` |
| Customer-demoable prototype + DDD handoff | `references/demo-closed-ddd-handoff.md` |
| Delivery acceptance report | `references/delivery-acceptance-gates.md` |
| AI Feature Injection lightweight contract | `references/ai-feature-injection.md` |
| AI Native harness | `references/ai-native-harness-engineering.md` |
| AI runtime/ops | `references/ai-runtime-ops.md` |
| AI effect evaluation | `references/ai-effect-evaluation.md` |
| Mobile product delivery | `references/mobile-product-delivery.md` |
| Multi-surface consistency | `references/multi-surface-consistency.md` |
| ToB/ToG approval workflow | `references/approval-workflow.md` |
| SaaS multitenancy/RBAC/license | `references/saas-multitenancy.md` |
| Reporting/data mart/dashboard | `references/reporting-analytics.md` |
| Low-code/workflow automation/app builder | `references/workflow-automation-lowcode.md` |
| System readiness before launch | `references/system-readiness-checklist.md` |
| Build/patch governance | `references/build-governance.md` |
| Artifact package standards | `references/artifact-packaging.md` |
| Prompt registry integration | `references/prompt-registry-integration.md` |
| Domain replacement | `references/domain-module-template.md` |
| Traffic safety domain | `references/domain-traffic.md`, `references/domain-traffic-safety-scenarios.md` |
| CRM domain validation example | `references/domain-crm.md` |
| Reusable PRD/checklist templates | `references/templates/prd-light-template.md`, `references/templates/prd-standard-template.md`, `references/templates/ai-native-prd-template.md`, `references/templates/system-readiness-checklist-template.md` |
| Skill upgrade path | `references/skill-version-migration.md` |
| Skill structure benchmark | `references/skill-design-benchmark.md` |

## 7. Decision Tree

```text
只是快速想法/演示 HTML?
  -> L0 + Gate 2 Lite + Gate 4 Lite

需要产品说明但不进入开发?
  -> L1 + Gate 1 Lite + Gate 2 + Gate 4 Lite

要交给开发/测试/投标/客户演示?
  -> L2 + Gate 1-4

AI 是否是本次交付模块的核心，即没有 AI 就无法完成主要用户结果或关键路径?
  -> 是: 该模块使用 L3 AI Native Harness + Runtime + Effect

AI 只是辅助分类/提取/摘要/推荐/草拟，且人工或确定性流程仍可完成?
  -> 是: 保持原 Tier + AI Feature Injection

AI 只是被用来编写 PRD/原型/代码，而不是产品功能?
  -> 不触发产品 AI Gate

有 PC + 移动/小程序/App?
  -> add Mobile + Multi-Surface Consistency

有审批/多级监管/会签/转审/撤回/超时?
  -> add Approval Workflow

有组织、租户、角色、数据隔离、席位/license?
  -> add SaaS Multitenancy

有指标、报表、数据集市、大屏、报告生成?
  -> add Reporting/Analytics

Has low-code app builder, node workflow, connector, or automation orchestration?
  -> add Workflow Automation / Low-Code

Is this a new product/market, major investment, repositioning, or commercialization decision?
  -> add Strategic Discovery Handoff before Stage 1
```

## 8. Pipeline

Core stages stay simple. Conditional plugins attach to the relevant stage.

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
- Stage 4: mobile/multi-surface paths, RBAC matrix, approval state machine, indicator lineage, workflow graph and connector contracts.
- Stage 5: DDD handoff, Developer Fast-Lane, prompt registry, effect evaluation, workflow execution acceptance, system readiness, packaging manifest.

Lite fast path:

```text
confirm requested artifact, outcome, and rigor tier
-> build/review the single requested artifact
-> verify the scoped demo/story path
-> list known gaps and upgrade triggers
-> stop
```

## 9. Complexity Budget

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

## 10. Review Model

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

## 11. Cross-File Consistency Rules

- Every PRD feature maps to a story id.
- Every story id maps to role path, prototype action, state/domain result, and test case.
- Every lifecycle object has a state-button matrix.
- Every primary prototype action maps to command/query or is explicitly prototype-only.
- Every domain write has audit/event and permission guard.
- Every AI prompt/model/tool change declares impact surface, linked tests, rollback owner, and observability signal.
- Every multi-surface feature declares what is shared and what differs by surface.
- Strategic market, competitor, and differentiation claims are required only when the Strategic Discovery Handoff Gate triggers; every claim must identify evidence, assumptions, confidence, and validation plan.

## 12. Required Scripts

When analyzing old prototypes, prefer the bundled ledger extractor:

```powershell
python references/../scripts/extract_interaction_ledger.py --input path/to/prototype.html --output interaction-ledger.json
```

If the script misses minified/external behavior, supplement with browser/DOM verification and mark UNKNOWN.

When modifying this skill, run:

```powershell
python scripts/validate_skill_consistency.py
```

## 13. Final Response Rule

When delivering work, state:
- selected artifact scope and execution mode;
- selected tier;
- triggered conditional gates;
- created/updated artifacts;
- verification performed;
- completion state: PASS / REVIEW_COMPLETE_WITH_GAPS / BLOCKED;
- unresolved risks or approved de-scopes.
