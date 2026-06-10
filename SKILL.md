---
name: ai-delivery-spec
description: >-
  Use when the task requires producing or reviewing a gate-verified product
  delivery artifact: exploratory HTML prototype, PRD, role/user-story path
  inventory, DDD developer handoff, ToB/ToG approval/RBAC/multitenancy contract,
  multi-surface PC/mobile/mini-program delivery, reporting/analytics product
  spec, AI feature injection, AI-native agent/runtime/harness spec, or AI effect
  evaluation. Use for AI系统设计, 智能体协同, 可开发PRD, 可演示原型, 角色路径,
  DDD领域建模, 移动端/小程序交付, ToB/ToG审批流, 多租户/RBAC, 指标报表,
  AI效果评估, low-code/workflow automation, and executable software delivery. Do not trigger for casual
  brainstorming, quick copy edits, or isolated drafts that do not require gates.
---

# AI Delivery Spec — AI Native 软件交付协议 (v4.0 Tiered ToB/ToG Delivery)

> 作者：李康（Li Kang） | 版本：v4.0 | 原则：分级交付、条件 Gate、ToB/ToG 通用模式、AI Native 与 AI 嵌入分流、多端一致性、领域插件化、构建与版本治理、可演示可开发可测试。

## 1. Core Rule

Do not force every task through the full pipeline. Start by choosing a delivery tier, then apply only the required core gates and conditional plugins.

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

## 3. Tiered Delivery Model

| Tier | Use When | Required Artifacts | Required Gates | Gates Skipped by Default |
|---|---|---|---|---|
| L0 Exploration Prototype | idea demo, quick HTML, workshop prototype, no dev handoff | `PROTOTYPE.html`, demo path notes, known gaps | Gate 2 Lite + Gate 4 Lite | DDD, AI harness, full PRD |
| L1 Prototype + Light PRD | feature explanation, internal alignment, simple CRUD/workflow | prototype, light PRD, story/path list, state notes | Gate 1 Lite + Gate 2 + Gate 4 Lite | full DDD unless lifecycle-heavy |
| L2 Standard Product Delivery | ToB/ToG module, bid/demo package, dev handoff | PRD, prototype, story matrix, state-button matrix, acceptance report | Gate 1-4 | AI Native unless triggered |
| L3 AI Native / High-Risk Delivery | agentic workflow, AI writes/acts, compliance/money/safety impact, multi-agent | L2 package + AI runtime/harness/effect/ops contracts | Gate 1-4 + conditional AI gates | none unless explicitly de-scoped |

Rules:
- A lower-tier artifact is not a failure just because it skips a higher-tier gate.
- If a lower-tier artifact is later used for development, upgrade it to L1/L2 first.
- If AI output triggers business write, workflow task, customer commitment, compliance action, money, or safety impact, escalate to L3 or justify AI Feature Injection instead.
- Tier choice must be recorded in the final answer or handoff package.

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
| Existing HTML/prototype/legacy version | Interaction Baseline + Drift Detection | `delivery-core.md`, `build-governance.md` |
| AI added to normal product but does not own workflow | AI Feature Injection Gate | `ai-feature-injection.md`, `prompt-registry-integration.md` |
| AI-native workflow, agentic automation, high-risk AI write/action | AI Native Harness Gate | `ai-native-harness-engineering.md`, `ai-runtime-ops.md`, `ai-effect-evaluation.md` |
| Mobile/H5/app/mini-program/field user | Mobile Delivery Gate | `mobile-product-delivery.md` |
| PC + mobile + mini-program/app surfaces | Multi-Surface Consistency Gate | `multi-surface-consistency.md` |
| ToB/ToG approval, escalation, audit workflow | Approval Workflow Gate | `approval-workflow.md` |
| SaaS, org tree, multi-tenant, RBAC, license/seat | SaaS Multitenancy Gate | `saas-multitenancy.md` |
| Indicator, report, BI, data mart, dashboard, report builder | Reporting/Analytics Gate | `reporting-analytics.md` |
| Prompt/model/tool registry, rollback, prompt tests | Prompt Ops Gate | `prompt-registry-integration.md`, `prompt-registry.yaml` |
| Low-code app builder, node workflow, connector/integration automation | Workflow Automation / Low-Code Gate | `workflow-automation-lowcode.md` |
| Patch scripts, generated HTML, repeated transforms | Build Governance Gate | `build-governance.md` |
| New industry/company/domain module | Domain Switch Gate | `domain-module-template.md`, current domain module |
| Skill upgrade or old project re-evaluation | Skill Version Migration Gate | `skill-version-migration.md` |

## 6. Module Map

| Need | Load |
|---|---|
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
| Build/patch governance | `references/build-governance.md` |
| Artifact package standards | `references/artifact-packaging.md` |
| Prompt registry integration | `references/prompt-registry-integration.md` |
| Domain replacement | `references/domain-module-template.md` |
| Traffic safety domain | `references/domain-traffic.md`, `references/domain-traffic-safety-scenarios.md` |
| CRM domain validation example | `references/domain-crm.md` |
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

AI 会影响业务决策、工作流、客户承诺、合规、金额、安全?
  -> L3 + AI Native Harness + Runtime + Effect

只是给已有产品加 AI 分类/摘要/审核/推荐?
  -> L1/L2 + AI Feature Injection

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
```

## 8. Pipeline

Core stages stay simple. Conditional plugins attach to the relevant stage.

```text
Stage 0  Existing artifact / reverse engineering
Stage 1  Opportunity and scope
Stage 2  Stakeholder and tier
Stage 3  Requirement design
Stage 4  Stories, role paths, states
Stage 5  PRD, prototype, acceptance package
```

Optional plugins:
- Stage 0: interaction ledger, patch-chain drift, build manifest.
- Stage 3: AI feature injection, AI-native scenario, approval/multitenancy/reporting/workflow domain model.
- Stage 4: mobile/multi-surface paths, RBAC matrix, approval state machine, indicator lineage, workflow graph and connector contracts.
- Stage 5: DDD handoff, Developer Fast-Lane, prompt registry, effect evaluation, workflow execution acceptance, packaging manifest.

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
| Sponsor | L1+ | outcome, cost, compliance, overclaim |
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

## 12. Required Scripts

When analyzing old prototypes, prefer the bundled ledger extractor:

```powershell
python references/../scripts/extract_interaction_ledger.py --input path/to/prototype.html --output interaction-ledger.json
```

If the script misses minified/external behavior, supplement with browser/DOM verification and mark UNKNOWN.

## 13. Final Response Rule

When delivering work, state:
- selected tier;
- triggered conditional gates;
- created/updated artifacts;
- verification performed;
- unresolved risks or approved de-scopes.
