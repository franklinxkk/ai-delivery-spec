---
name: ai-delivery-spec
description: >-
  AI-native product-engineering delivery protocol for PRD, prototype, reverse engineering,
  AI agent design, AI-native harness engineering, runtime governance, observability, prompt ops, tool policy, testability,
  user-story inventory, role operation path verification, customer-demoable self-contained
  HTML prototypes, DDD handoff PRD, and domain-specific product delivery. Use for AI系统设计,
  智能体协同, PRD, 原型, 用户故事, 角色路径, 客户演示原型, DDD领域建模, 业务建模,
  指标体系, 逆向工程, software delivery, product-engineering collaboration,
  executable specification work, and traffic safety / transport supervision products.
---

# AI Delivery Spec — AI Native 软件交付协议 (v3.8 Harness-Engineering Verified)

> 作者：李康（Li Kang） | 版本：v3.8 | 原则：公共协议去领域化，业务知识插件化，用户故事与角色路径先行，AI Native Harness 工程化验证，迭代原型交互保真，状态按钮矩阵强制化，原型客户演示自闭环，PRD按DDD可开发可测试

## Why This Version

v3.8 keeps the protocol layer domain-neutral and adds AI-native harness engineering gates on top of v3.7 delivery-acceptance verification:

1. **Story-Path Verification Gate**: every described function must map to at least one user story, role operation path, prototype demo path, state transition, and test case.
2. **Demo-Closed Prototype Gate**: the HTML prototype must be self-contained and customer-demoable without a backend. Every core user story must be walkable end-to-end with in-memory mock data, visible state changes, modals/pages, role switching, success/error/empty states, and no dead buttons.
3. **DDD Handoff PRD Gate**: the PRD must describe bounded contexts, aggregates, entities/value objects, domain events, commands/queries, invariants, state transitions, key sequence diagrams, inputs/outputs, processing logic, business transformation logic, API contracts, and feature-level test cases.
4. **State-Button Matrix Gate**: every list/detail object with lifecycle state must define state → visible actions → forbidden actions → guard conditions → visible outcome before the prototype/PRD is accepted.
5. **No Toast-Only Core Action Gate**: create/view/edit/configure/submit/review/enable/disable/export/analyze actions must produce a real visible page, modal, data mutation, table refresh, result view, or state transition. Toast may only be feedback, not the business outcome.
6. **AI Native Harness Engineering Gate**: once an AI-native scenario and target outcome are defined, multi-agent feasibility review must verify whether context, tools, workflow, evaluation, observability, and release harnesses can support stable landing. The logic path and engineering path must be simulated before runtime development is accepted.

When a new prototype is generated from an existing one, semantic annotations are not enough: the new version must preserve or explicitly de-scope the previous version's pages, actions, modals, handlers, data coverage, and critical workflows. A prototype that looks complete but cannot complete a user story is a failed delivery artifact.

## Module Map

| Need | Load |
|------|------|
| Reverse-engineer an existing HTML/prototype, write PRD, plan stages, state machine, SIM review | `references/delivery-core.md` |
| Generate/review an HTML prototype, data-testid, visual/test automation, AD5 patterns | `references/prototype-testability.md` |
| Produce customer-demoable prototype + DDD PRD handoff with hard gates | `references/demo-closed-ddd-handoff.md` |
| Apply final acceptance gates: interaction ledger, state-button matrix, no-toast rule, browser verification report | `references/delivery-acceptance-gates.md` |
| Validate user stories, role operation paths, demo paths, scenarios, and test coverage | `references/story-path-verification.md` |
| Design AI feature, agent runtime, tool calls, alerts, rollback, operations | `references/ai-runtime-ops.md` |
| Validate AI-native scenario feasibility, harness engineering, multi-agent review, and engineering path simulation | `references/ai-native-harness-engineering.md` |
| Company/industry domain context, metrics, entities, scenarios, UI patterns | current domain module, default `references/domain-traffic.md` |
| Validate traffic safety / transport supervision scenarios in depth | `references/domain-traffic-safety-scenarios.md` |
| Register/update LLM prompts and linked tests | `references/prompt-registry.yaml` |

Domain module contract: the current domain module may be replaced when the company or industry changes. A valid domain module should define domain entities, metrics, workflows, scenarios, UI patterns, policy constraints, and acceptance checklist. Public protocol files must stay domain-neutral.

Decision tree:

```text
已有原型/HTML/竞品/旧系统 → delivery-core
要写 PRD 或开发交接 → delivery-core + prototype-testability
只有普通业务功能，无 AI → delivery-core + prototype-testability
单个 AI 调用 → delivery-core + ai-runtime-ops + prompt-registry
多个 Agent / 工具 / 回滚 / 监控 → delivery-core + ai-runtime-ops + prompt-registry
AI Native 业务流程重构 / Agentic workflow / 高风险自动化 → delivery-core + ai-native-harness-engineering + ai-runtime-ops + prompt-registry
行业/公司/业务域知识 → add current domain module (default: domain-traffic; replace when company changes)
```

## Collaboration Model

Every AI feature must align five contracts before development starts:

| Contract | Owner | Required Artifact | Gate |
|----------|-------|-------------------|------|
| Business invariant | PM + Sponsor | Problem, state machine, guards, success metrics | SIM 1 + Gate 1 |
| Runtime contract | Dev Lead + AI Platform | Agent registry, events, write_scope, fallback, human gates | Stage 3.5 |
| Harness contract | AI Product + AI Architect + QA + Ops | Scenario card, context map, tool sandbox, eval set, replay trace, release gate | Stage 3.2 |
| Evaluation contract | PM + QA | Scenario matrix, linked_test_cases, testid map, complexity count | SIM 1 + SIM 2 |
| Operations contract | AI Platform + Ops | Trace fields, alert executor, rollback path, on-call/retrain owner | Stage 5.5 |

Rules:
- PM owns what must be true; do not hand-wave AI failure states.
- Engineering owns how it safely runs; reject specs missing write_scope, idempotency, or precondition policy.
- AI Product owns AI-native scenario value and target metrics; do not start runtime work before harness feasibility is reviewed.
- AI Platform owns model/prompt/tool behavior; every LLM agent must have prompt registration and tests.
- QA owns executable scenarios, including AI ambiguity, rollback, batch operations, multi-step flows.
- Ops owns alert executors and escalation paths; no alert ships with only intention-style action.

AI change control: every prompt/model/tool/runtime/UI change must declare `impact_surface`, `linked_test_cases`, `rollback_owner`, and `observability_signal`.

Prototype iteration control: when an existing prototype or HTML file is used as input, Stage 0 must produce an interaction baseline ledger. Stage 5 must compare the new prototype against that ledger. Do not reduce interaction coverage unless the removed behavior is listed in a de-scope note with owner and reason. For lifecycle-heavy products, Stage 4 must also produce a state-button matrix before final UI or PRD generation.

## Hard Gates: Story-Path Verification + AI Native Harness + Demo-Closed Prototype + DDD PRD

These gates are mandatory when generating or reviewing a PRD, HTML prototype, product design prototype, customer demo artifact, or development handoff package.

### Gate A: User Story and Role Path Verification

Requirement completeness is judged by paths, not by feature names. Every described function must be backed by a user story and an executable role operation path.

Required:
- Build a user story inventory before writing the PRD or prototype: role, goal, trigger, preconditions, path steps, expected visible result, domain result, exception path, state transition, and test case id.
- Build a role operation path matrix for each role: start page, action sequence, data touched, state before/after, permissions, audit/event, and next step.
- Every feature mentioned in PRD scope must map to at least one user story id. Every user story id must map to prototype `data-testid`/`data-action` and at least one test case.
- Every role must have at least one complete happy path and one exception/permission path.
- Scenario validation must include domain-specific cases, not only generic CRUD paths.
- During review, use the path matrix to click through the prototype and mark each story PASS/FAIL/BLOCKED. BLOCKED stories must be fixed or explicitly de-scoped.

Story/path fail conditions:
- A function is described but has no user story.
- A user story exists but cannot be clicked through in the prototype.
- A user story has no expected domain result or state transition.
- A role appears in the PRD but has no operation path.
- A test case cannot be traced back to a story, or a story cannot be traced forward to a test.

### Gate A2: AI Native Harness Engineering

AI-native scenarios must prove engineering feasibility before runtime design starts. A scenario that cannot be simulated through context, tools, workflow, evaluation, observability, and release harness is not ready for development.

Required:
- Build an AI-native scenario card with business goal, trigger, current workflow, AI-native workflow, target metrics, risk level, required context, required tools, allowed auto actions, human gates, forbidden actions, latency, and cost targets.
- Run multi-agent feasibility review with Sponsor, Domain Workflow, AI Architect, Backend Integration, Data/RAG, QA/Eval, and Ops/SRE perspectives.
- Define context harness, tool/API harness, workflow harness, evaluation harness, observability harness, and release harness.
- Simulate the business logic path and engineering path before Stage 3.5 runtime contract is accepted.
- Produce fixture replay, dry-run, failure-injection, and release gate plan for high-risk AI-native workflows.

Harness fail conditions:
- AI-native scenario lacks measurable business outcome.
- Required context is unavailable, stale, unscoped, or not permission-safe.
- Tool execution cannot be stubbed, sandboxed, or replayed.
- High-risk action lacks human gate.
- Agent workflow cannot be expressed as events, states, tools, fallback, and trace.
- No golden evaluation cases, human rubric, trace replay, rollback, or kill switch exists.

### Gate B: Customer-Demoable Prototype

The prototype is the executable requirement. It must be usable for a complete customer demo even when no backend exists.

Required:
- Every core user story has a runnable start point, operation path, visible result, and reversible/next action.
- Every visible `data-action` has an implemented handler and a visible outcome: state mutation, page switch, modal, table update, form update, validation message, or toast plus state change.
- Core actions must not be toast-only. Create/view/edit/configure/submit/review/freeze/analyze actions must open a real page/modal or mutate mock state.
- Use in-memory mock data to cover happy path, empty state, validation failure, permission boundary, in-progress state, completed state, rejected state, and frozen snapshot state.
- Role-based workflows must be demoable by switching roles in the prototype, not only described in PRD.
- Workbench actions should live inside their business module. Do not promote workflow actions such as “new task” or “template builder” into top-level navigation unless that is truly how users work.
- The prototype must include enough sample rows and state variants for a customer to understand the end-to-end business story.
- Before delivery, run a browser verification over the highest-risk paths. If browser automation is unavailable, run a deterministic DOM/action audit and explicitly state the verification gap.

Prototype fail conditions:
- A primary button does nothing, only logs to console, or only shows a placeholder toast.
- A detail/preview button cannot show the underlying business data.
- A create flow cannot produce a visible new object in the prototype.
- A state transition is described but cannot be demonstrated with mock state.
- A role or permission boundary is only written in PRD and not represented in the UI.

### Gate C: DDD Handoff PRD

The PRD must be a development contract, not only a product narrative.

Required per bounded context/module:
- Business purpose and actors.
- Inputs: user input, system context, upstream data, AI/tool output, file imports, and permissions.
- Outputs: UI result, domain object changes, domain events, notifications, exports, reports, and audit logs.
- Processing logic: validation, matching, calculations, aggregation, persistence intent, idempotency, and error handling.
- Business transformation logic: how inputs become entities, value objects, state transitions, snapshots, or downstream tasks.
- DDD model: bounded context, aggregate root, entities, value objects, domain services, repositories/contracts, domain events, commands, queries, policies, and invariants.
- State machine: states, transitions, triggers, guards, post-actions, rollback/reopen path.
- Sequence diagram for each critical flow: user action, frontend, domain service/API, AI/tool if any, persistence, notification/audit, UI refresh.
- API/business contract: method/path or command/query name, request, response, guards, idempotency key, permission rule, audit rule.
- Test cases: happy path, validation failure, permission failure, state conflict, async/AI ambiguity, batch action, and regression against prior prototype.

PRD fail conditions:
- A module lacks inputs, outputs, processing logic, or business transformation logic.
- A state transition lacks trigger, guard, and post-action.
- A prototype action lacks a corresponding PRD command/query or test case.
- A test case says only “verify normal” without concrete steps and expected visible/domain result.
- DDD terms are listed but not tied to actual business objects and behaviors.

### Gate D: Delivery Acceptance

Before final delivery, run the acceptance gates in `references/delivery-acceptance-gates.md`.

Required:
- Existing-prototype iterations include an interaction ledger and regression comparison.
- Every lifecycle object includes a state-button matrix.
- Every primary action has a visible business outcome; core actions are not toast-only.
- Every role has at least one complete demo path and one exception/permission path.
- Browser or deterministic DOM verification covers the highest-risk user paths.
- Final delivery includes prototype path, PRD path, verification report, unresolved risks, and test handoff checklist.

Acceptance fail conditions:
- A workflow action is placed outside its business module without a stated product reason.
- A created object is not visible in the relevant list/detail after creation.
- A detail/progress/result button cannot show underlying mock business data.
- State-specific forbidden actions still appear in the UI.
- The PRD describes a behavior that cannot be demonstrated in the prototype and is not explicitly marked as future scope.

## Delivery Pipeline

```text
Stage 0: Reverse-engineer      → stage0-output.json + interaction-ledger.json
Stage 1: Brainstorm            → Opportunity brief
Stage 1.5: Research            → Research brief
Stage 2: Stakeholder profile   → Sponsor + User + Dev portraits
Stage 3: Requirement design    → Solution + scope + metrics
     ↓ SIM 1: solution review
Stage 3.2: AI Native harness   → scenario card + multi-agent feasibility review + engineering path simulation
Stage 3.5: Agent runtime       → Agent/event/write_scope/fallback policy
Stage 4: Stories + state       → user-story-inventory.md + role-path-matrix.md + guarded state machine
Stage 5: PRD + prototype       → REQUIREMENT.md + PROTOTYPE.html + demo-paths.json + story-path-coverage.md + state-button-matrix.md
Stage 5.5: Observability       → trace fields + alert rules + dashboards
Stage 5.6: Tool contract       → tool registry + call policy + audit
     ↓ SIM 2: prototype review + browser/demo-path verification + delivery acceptance gates
Delivery: PRD + customer-demoable prototype + interaction ledger + state-button matrix + demo verification report + developer prompt + review report
```

Stage selection:

| Trigger | Start |
|---------|-------|
| "已有原型 / 竞品 / 从 HTML 反推需求" | Stage 0 |
| "Brainstorm / idea / opportunity" | Stage 1 |
| "调研 / research / discovery" | Stage 1.5 |
| "方案 / feature spec" | Stage 3 |
| "用户故事 / 状态机" | Stage 4 |
| "PRD / 原型 / 开发交接" | Stage 5 |
| No stage specified | Full pipeline |

## Complexity Budget

Budget: PRD <= 15pp / states <= 20 / actions <= 50 / APIs <= 30 / tools <= 12 / agents <= 8.

Counting rules:
- PRD pages: rendered A4 pages, excluding appendices and review reports.
- states: unique business + AI states; nested substates count if they have independent transitions.
- actions: user-visible commands and system-triggered actions; CRUD variants count separately when guards differ.
- APIs: unique endpoint + method contracts referenced by PRD or prototype `data-api`.
- tools: unique AI tools in the tool contract.
- agents: unique runtime agents.
- Peer PM must count each item in SIM 1 and output PASS/FAIL. Over-budget requires exception reason, owner, and mitigation.

## SIM Review

Run SIM 1 after Stage 3 and SIM 2 after Stage 5.

| Agent | Persona | Output |
|-------|---------|--------|
| Sponsor | 业务发起方，关注合规、审计、成本、结果 | PASS/NEEDS_REVISION + Top concerns |
| End User | 一线用户，不理解设计意图，只按真实任务操作 | Walkthrough + pain points |
| Peer PM | ToG/ToB PM，抓范围蔓延和逻辑矛盾 | Cross-check + state audit + complexity PASS/FAIL |
| Dev Lead | 后端/架构视角，关注可实现性和工期 | Feasibility + hidden complexity |

Report format:

```markdown
# Review Report: SIM [1/2] - [Feature]
## Verdicts | Agent | Verdict | Top Concern |
## Required Actions
- [ ] Action: Owner by Date
## Next Step
[Proceed / Revise / Escalate]
```

## Mandatory Gates

Gate 1: Requirement review after Stage 3. Business side can restate problem, confirm metrics, accept Out of Scope, and add at least one missing scenario.

Gate 2: Prototype walkthrough after Stage 5. Give users tasks without hints; observe silently; record where they fail. The prototype fails Gate 2 if any primary user story cannot be completed inside the HTML with mock state and visible output.

Gate 3: Dev pre-review after Gate 2. Dev Lead can click through the prototype and infer each feature's command/query, state transition, domain object, validation rule, and expected result even before reading the PRD.

## Developer Handoff Rules

PRD is a business script, not a technical blueprint. It should not contain DB table names, framework choices, implementation code, or pseudo APIs unless those are business contracts.

Prototype must make behavior inspectable:
- `data-testid` on every interactive/verifiable element.
- `data-action` on commands.
- `data-state` on stateful containers.
- `data-api` + `data-method` where backend contract is implied.
- `data-visible-role` where role visibility differs.
- If iterating from an older prototype, preserve baseline interaction coverage unless explicitly de-scoped.
- Business workbench/detail views must show the real mock business data behind each list item, not only metadata summaries.
- Create flows must visibly create mock records; edit flows must visibly mutate mock records; submit/review/freeze flows must visibly change state.
- Customer demo data must cover at least one complete journey per role and one state variant per critical lifecycle state.
- The prototype must expose a test helper such as `window._test.scan()` and `window._test.missingHandlers()` or an equivalent deterministic DOM/action audit.

Cross-file consistency checks:
- Every PRD feature maps to a user story id.
- Every user story id maps to role path steps, prototype actions, state transitions, and test cases.
- PRD state machine states match prototype `data-state`.
- ACTION IDs match prototype `data-action`.
- ACTION IDs have implemented handlers and visible outcomes.
- API contract matches `data-api` + `data-method`.
- Field definitions match `data-field` / `data-bind`.
- Role matrix matches `data-visible-role`.
- PRD commands/queries/events match prototype actions and visible domain state changes.
- PRD test cases cover every primary demo path in `demo-paths.json` or equivalent browser verification script.

## Quality Checklist

Stage 0:
- [ ] Input pattern detected: semantic / inline / file-route / external SPA.
- [ ] External dependencies scanned.
- [ ] Entities, views, features, states, roles extracted.
- [ ] If iterating, interaction baseline ledger extracted from the prior prototype.
- [ ] Regression diff lists removed views/actions/handlers/data sets and de-scope reasons.
- [ ] Confidence labels: CONFIRMED / INFERRED / UNKNOWN.
- [ ] `stage0-output.json` produced.

Stage 1-3:
- [ ] Problem has 3+ evidence sources.
- [ ] Epic hypothesis is falsifiable.
- [ ] Out of Scope has 5+ items with revisit conditions.
- [ ] Success metrics have baseline, target, timeline.

Stage 4:
- [ ] User story inventory exists and every story has role, trigger, precondition, path, expected UI result, expected domain result, exception path, state transition, and test id.
- [ ] Role operation path matrix exists for every role.
- [ ] Every scoped feature maps to at least one user story.
- [ ] Stories follow INVEST.
- [ ] Every AC has happy, error, boundary paths.
- [ ] Every state transition has Trigger + Guard + Action.
- [ ] Cross-entity guards are explicit.

Stage 5:
- [ ] PRD has all 10 chapters.
- [ ] Story-path coverage table maps feature -> story -> role path -> prototype action -> state transition -> API/command -> test case.
- [ ] PRD is DDD-complete for each bounded context: aggregates, entities, value objects, commands, queries, events, policies, invariants.
- [ ] Each module has inputs, outputs, processing logic, business transformation logic, exceptions/guards, API/business contract, sequence diagram, state diagram, and concrete tests.
- [ ] Prototype has complete semantic annotations.
- [ ] Prototype preserves prior interaction coverage or documents approved de-scope.
- [ ] Every `data-action` has a handler and visible state/view/modal/toast effect.
- [ ] Every core create/view/edit/configure/submit/review/freeze/analyze flow is demoable end-to-end using in-memory mock data.
- [ ] No primary action is toast-only; each primary action opens a real view/modal or mutates mock state.
- [ ] Workbench/detail views show item-level business data and not just summaries.
- [ ] Browser/demo-path verification passes; failures are fixed before delivery or documented as approved exceptions.
- [ ] Test scenarios cover core, error, permission, async, concurrent, batch, and mobile.

AI protocol checks:
- [ ] AI states, confidence, ambiguity, and evidence chain defined.
- [ ] Agents have trigger_event, output_event, write_scope, forbidden_write, timeout, retry, fallback.
- [ ] Tool calls have class, allowed_when, forbidden_when, audit, approval gates.
- [ ] Alerts have executor and owner.
- [ ] Prompts are registered in `prompt-registry.yaml` with linked tests.

ToG/ToB mandatory:
- [ ] Data retention, desensitization, audit trail, org isolation, SLA defined.
- [ ] Approval workflows and escalation paths identified.
- [ ] Requirement gaps documented with owners and deadlines.
