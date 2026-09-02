# AI Delivery Spec 5.4.9 — Requirement Management for Human & AI｜人机共用需求管理

> AI 把 PRD 和页面生成得越来越快，但指标、状态、权限、异常和验收仍在开工后靠人补。  
> **AI Delivery Spec 把一句话需求、存量系统或变更，收敛为业务能确认、研发可实施、测试可复现、Coding Agent 可执行的同一份需求基线。**
>
> **English:** AI can generate documents and screens quickly, but teams still discover missing metrics, states, permissions, failures, and acceptance rules after implementation starts. AI Delivery Spec turns an idea, an existing system, or a change request into one shared requirement baseline that business stakeholders can confirm, engineers can implement, testers can reproduce, and Coding Agents can execute.

适用于 ToC 与 ToB/ToG 产品：小改直接交最小闭环，跨角色、跨系统或高风险需求才升级治理。  
**English:** Works for consumer, enterprise, and government products. Small changes stay lightweight; cross-role, cross-system, regulated, or high-risk work receives only the additional governance it needs.

[![Version](https://img.shields.io/badge/version-5.4.9-7C3AED.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)
[![Forks](https://img.shields.io/github/forks/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec/forks)

## 社区验证｜Community Validation

| 平台 / Platform | 当前数据 / Current signal | 详情 / Details |
|---|---:|---|
| ClawHub | **2,200+ 次下载/使用 / downloads & uses** | [版本、下载量与安全审计 / Versions, usage and security audit](https://clawhub.ai/franklinxkk/skills/ai-delivery-spec) |
| SkillHub | **4.7 / 5** | [评分与安全扫描报告 / Rating and security scan](https://skillhub.cn/skills/user_12c92261/ai-delivery-spec) |

> 社区数据核对于 2026-09-02，会随平台实时变化。如果它帮你少开一次“补规则”的会，欢迎到 [GitHub 点个 Star ⭐](https://github.com/franklinxkk/ai-delivery-spec)。
>
> **English:** Community figures were checked on 2026-09-02 and may change. If the Skill saves your team one rule-repair meeting, please consider giving the project a [GitHub Star ⭐](https://github.com/franklinxkk/ai-delivery-spec).

## 它先解决谁的什么关键问题｜Who It Helps and Why

| 角色 / Role | 最常见的交付损耗 / Typical loss | 使用后得到什么 / What you gain |
|---|---|---|
| 初级产品经理<br>Junior PM | 不知道该问什么，把页面描述当需求<br>Does not know what to clarify and mistakes screen descriptions for requirements | 有边界的澄清引导、最小需求卡、规则与异常底线<br>Bounded clarification, a minimum requirement card, and rule/failure coverage |
| 中高级产品 / 产品负责人<br>Senior PM / Product lead | 跨模块、状态、数据和团队输出难统一<br>Cannot keep modules, states, data, and team outputs aligned | 一份可追溯基线、分级交付、内审与变更影响<br>One traceable baseline, proportional delivery, review, and change impact |
| 业务 / 售前 / 实施 / 设计<br>Business / Presales / Delivery / Design | 客户语言转成产品方案时不断失真<br>Customer language loses meaning while becoming a product solution | 事实、假设、未知和可确认的产品态原型<br>Separated facts, assumptions, unknowns, and a confirmable product prototype |
| 前端开发<br>Frontend engineer | 入口、交互、权限和失败反馈靠评审会补<br>Entry, interaction, permissions, and failure feedback are filled in during meetings | 页面、动作、状态结果、二级上下文与可观察验收<br>Pages, actions, visible states, secondary contexts, and observable acceptance |
| 后端 / 架构师<br>Backend engineer / Architect | 指标口径、权威源、状态守卫和幂等晚补<br>Metric formulas, authorities, guards, and idempotency arrive late | 对象、规则、数据流、状态、事件和 NFR 边界<br>Objects, rules, data flows, states, events, and NFR boundaries |
| 测试工程师<br>QA engineer | 只有正向页面描述，无法独立复现<br>Only happy-path screen descriptions exist | 正反例、边界、异常、权限、证据和回归范围<br>Positive/negative cases, boundaries, failures, permissions, evidence, and regression scope |
| Coding Agent | 文档可读但不可执行，缺口被模型自动脑补<br>Documents are readable but gaps are silently invented | 稳定 ID、机器切片、GAP 纪律和结构化 handoff<br>Stable IDs, machine-oriented slices, explicit gaps, and structured handoff |

## 60 秒上手｜60-Second Quick Start

### 1. 安装｜Install

```bash
# Codex / Claude Code / Cursor / Trae and other Agent Skills-compatible tools
npx skills add franklinxkk/ai-delivery-spec

# OpenClaw
openclaw skills install @franklinxkk/ai-delivery-spec
```

### 2. 直接说目标，或选择一个快捷入口｜State the Goal or Pick a Shortcut

不需要先学习阶段名、模板或内部 ID。拿不准时只用 `/ads`：  
**English:** You do not need to learn stages, templates, or internal IDs. When unsure, start with `/ads`.

```text
/ads 我有一个“企业数据一键上报”的想法，请判断目前最需要澄清什么，并带我做到可交付。
/ads I have an idea for one-click enterprise data reporting. Identify the most important unknown and guide me to a deliverable result.
```

目标明确时直接选停止点。  
**English:** When the target is clear, choose the shortcut that matches your desired stopping point.

| 入口 / Shortcut | 复制后替换括号内容 / Copy and replace | 得到什么 / Result |
|---|---|---|
| `/ads` | `/ads 我现在有（想法/材料/旧系统），本次想做到（目标）`<br>`/ads I have an (idea/artifact/existing system) and want to reach (target).` | 自动判断从哪里进入、做到哪里停止<br>Routes to the lightest suitable path and stopping point |
| `/dig` | `/dig 深挖这个需求，一次只问我一个真正影响方向的问题`<br>`/dig Challenge this requirement. Ask one direction-changing question at a time.` | 用战略、系统、可观察行为和反方挑战关闭关键未知<br>Closes key unknowns through strategic, systemic, observable-behavior, and devil's-advocate lenses |
| `/prd` | `/prd 基于这些材料形成可评审、可实施、可验收的统一 PRD`<br>`/prd Turn these materials into one reviewable, implementable, and testable PRD.` | 资料够就直接出 PRD；P0 未知先澄清，再自动返回 PRD<br>Produces the PRD directly when ready; otherwise closes blocking P0 unknowns first |
| `/proto` | `/proto 基于已确认需求生成可操作 HTML；需要评审态时先问我`<br>`/proto Build an operable HTML prototype from confirmed requirements; ask before adding review mode.` | 默认产品态；概念原型和研发评审态按目标区分<br>Defaults to product mode and separates concept prototypes from engineering review mode |

四个入口是意图别名，不是四套新流程。部分宿主会在消息到达模型前拦截未知命令，因此不宣称跨宿主原生注册；此时改用 `/ai-delivery-spec /dig …`、`$ai-delivery-spec /dig …`，或直接说“使用 ai-delivery-spec 深度澄清这个需求”。  
**English:** These are intent aliases, not four separate workflows. Some hosts intercept unknown slash commands before the model sees them. In that case, use an explicit Skill form such as `/ai-delivery-spec /dig …` or `$ai-delivery-spec /dig …`, or simply say “Use ai-delivery-spec to clarify this requirement deeply.” Native registration is not claimed across all hosts.

> **第一次深入使用前 / Before deeper use:** 花 3 分钟扫一遍[避坑指南与 FAQ](references/troubleshooting.md)，先避开“简单需求跑重流程、P0 未关闭就冒充基线、默认生成评审态、静态 PASS 冒充真实验收”等高频错误；不需要通读全部参考文档。
>
> Spend three minutes on the [Pitfall Guide and FAQ](references/troubleshooting.md) before team handoff. It prevents the most common mistakes without requiring you to read every reference.

### 3. 它会自动控制轻重｜It Automatically Controls Delivery Weight

如果你只说一句“帮我做一个企业约谈 HTML”，Skill 会记住 HTML 是最终目标，先分批确认会改变范围、规则、权限、状态、指标或数据的关键决定；P0 关闭后继续生成可实施原型，**不会停在一张需求清单**。若只是想先看方向，请明确说“先做概念原型，允许合理假设”；假设和 GAP 会被显式标出，不冒充开发基线。  
**English:** If you ask for an HTML prototype in one sentence, the Skill keeps that as the target and first closes only the decisions that change scope, rules, permissions, states, metrics, or data. It continues to the prototype after P0 unknowns are closed. If you only want an early concept, say so explicitly; assumptions and gaps remain visible and never masquerade as a development baseline.

你不需要说 `Ultra-Light`、`L2` 或 `smart-large-project`：  
**English:** You do not need to choose an internal delivery level.

- “表头联系人改成企业联系人，其他逻辑不变。”——直接按快速小改处理。  
  **EN:** “Rename the contact column; keep all other behavior unchanged.” → direct small change.
- “新增审批状态，影响三个角色、通知和统计。”——只升级状态、权限、数据、异常和回归合同。  
  **EN:** “Add an approval state affecting three roles, notifications, and reporting.” → expand only the relevant contracts.
- “跨系统双向同步，要正式验收。”——才启用权威源、数据流、追溯与验收证据。  
  **EN:** “Add bidirectional cross-system sync with formal acceptance.” → add authority, data flow, traceability, and evidence.

一个 Idea 也能开始。先看[最小需求样例](examples/minimal-v5/README.md)；需要理解指标、泳道流转和二级抽屉如何进入评审态时，直接打开[中等需求交互样例](examples/medium-review-handoff/review-prototype.html)。该匿名样例用于首次理解与冷读训练，不冒充可复制的完整 Schema/发布夹具。  
**English:** An idea is enough to begin. Start with the [minimal requirement example](examples/minimal-v5/README.md). To see how metrics, lane transitions, and a secondary drawer enter review mode, open the [medium interactive example](examples/medium-review-handoff/review-prototype.html). It is an onboarding and cold-read example, not a complete release fixture.

## 一条主线，不是一条僵硬流水线｜One Product-Truth Line, Not a Rigid Pipeline

`frame → explore → intake → clarify → specify → review → baseline → change / acceptance`

从哪里来就从哪里进入，只做到当前目标。  
**English:** Enter at the stage supported by your current evidence and stop when the requested artifact is complete.

- 从零开始：定义问题、用户、证据、成功信号和最小验证。  
  **EN:** From zero: define the problem, users, evidence, success signal, and smallest validation.
- 已有材料或系统：先做 Stage 0 盘点，再识别遗漏、冲突和不可实施处。  
  **EN:** Existing artifact/system: inventory Stage 0 before identifying gaps, conflicts, and infeasible behavior.
- 要开发：形成一份统一 PRD，按需配工程原型与机器附录。  
  **EN:** Ready for development: create one unified PRD, plus an engineering prototype and machine appendix only when needed.
- 有变更：比较基线，穿透角色、页面、规则、数据、消费者和回归范围。  
  **EN:** Change request: compare the baseline across roles, pages, rules, data, consumers, and regression scope.
- 要验收：把 AC 变成执行记录，区分静态检查、真实实现、领域确认和客户签署。  
  **EN:** Acceptance: turn ACs into execution records and separate static checks, real implementation, domain confirmation, and customer sign-off.

普通项目默认**一份统一 PRD**：正文供业务、产品和传统开发顺序阅读，同文档工程附录供前后端、测试和 Agent 精确执行。只有持续变更、多投影或强审计场景才启用**分片真相**（Product Truth）。  
**English:** Ordinary work uses one unified PRD: a sequential human-readable body plus an engineering appendix in the same document. Product Truth is reserved for sustained change, multiple projections, or strong audit needs.

## 产品态、评审态、机器合同各司其职｜Product, Review, and Machine Surfaces

- **产品态 / Product mode**：客户演示和需求确认默认产物，保持完整、可操作，不被注释破坏。 / The default for demos and requirement confirmation; complete, operable, and not damaged by annotations.
- **评审态 / Review mode**：只有用户明确要求或确认后生成。左侧保留完整产品；右侧解释当前页面或业务浮层。 / Generated only after explicit request or confirmation; the product remains intact while the side panel explains the current context.
- **机器合同 / Machine contract**：稳定 ID、规则、状态、数据流、错误、副作用和验收证据；不把右侧说明当 Coding Agent 的唯一输入。 / Stable IDs, rules, states, data flows, failures, side effects, and evidence; the review panel is never the Coding Agent's only input.

5.4.9 延续 5.4.8 的评审态语义合同：以“所有影响实施与验收的语义项”为覆盖分母。  
**English:** Review-mode coverage is based on every semantic item that changes implementation or acceptance—not on the number of visible annotations.

- 当前菜单、面包屑、页面和业务弹窗都要有可定位上下文。  
  **EN:** Menus, breadcrumbs, pages, and business overlays must identify the current product location.
- 页面上的关键功能要在真实目标旁标号；点击左侧标号或右侧卡片，目标、标号和说明同时框选。  
  **EN:** Key functions receive markers beside real targets; selecting either side highlights the target, marker, and explanation together.
- 简单功能可用一句话说明；装饰元素不强行标注。  
  **EN:** Simple functions may use one sentence; decorative elements are not annotated mechanically.
- 说明先写人能连续读懂的业务语言；复杂点再按需展开前端、后端和测试细节。稳定 ID、字段名和机器枚举默认收进“技术追溯”。
  **EN:** Lead with continuous business language; expand frontend, backend, and QA detail only for complex points. Stable IDs, field names, and machine enums stay in a collapsed technical trace.
- 指标卡必须写清口径、时间窗、范围、来源、刷新、缺失/延迟和验收。  
  **EN:** Every metric card defines formula, time window, scope, authority, refresh, missing/delayed data, and acceptance.
- 泳道或状态页必须写清迁移条件、角色守卫、副作用、失败与恢复。  
  **EN:** Workflow and state pages define transitions, role guards, side effects, failures, and recovery.
- 点击卡片后的拆解、编辑、确认等二级弹窗/抽屉，是独立评审上下文，不能只标入口按钮。  
  **EN:** Secondary modals and drawers are independent review contexts, not unexplained consequences of an entry button.
- 评审栏可以收起再展开；窄屏可在产品态和评审态间切换，不覆盖关键操作。  
  **EN:** The panel can collapse and reopen; narrow screens switch between product and review surfaces without covering key operations.

跨页面、模块或角色主链才在总览画核心流程并高亮当前页面；受守卫的状态变化在边界页画状态图；跨系统或多权威源画数据流，并保留少量可执行正反例。简单 CRUD 不机械堆图。
**English:** Overview shows a current-context-highlighted core flow only for real cross-page/module/role chains; Boundary & Acceptance adds guarded state or cross-system data-flow diagrams plus a few executable positive/negative cases. Simple CRUD stays diagram-free.

## 与 Spec Kit / OpenSpec 的边界｜Boundary with Spec Kit and OpenSpec

[Spec Kit](https://github.com/github/spec-kit) 和 [OpenSpec](https://github.com/Fission-AI/OpenSpec) 更贴近代码仓库中的规格、技术计划、任务与实现协作。AI Delivery Spec 聚焦更上游、更跨角色的 **requirement-to-acceptance**：先定准业务价值、范围、责任、规则、评审基线和验收，再交给团队已有的下游开发流程。  
**English:** Spec Kit and OpenSpec focus more directly on repository-local specifications, technical planning, tasks, and implementation. AI Delivery Spec focuses on the cross-role requirement-to-acceptance contract before work enters the team's existing development workflow.

如果项目已经使用 Spec Kit、OpenSpec 或某个 Coding Agent，可以按稳定需求 ID 和验收证据进行交接；AI Delivery Spec 当前不要求安装这些工具，也不宣称内置导出、双向同步或一等公民集成。  
**English:** If a project already uses Spec Kit, OpenSpec, or a Coding Agent, hand off through stable requirement IDs and acceptance evidence. AI Delivery Spec does not require these tools and does not claim built-in export, bidirectional synchronization, or first-class integration.

## 门禁：发现缺口，不制造绿灯｜Gates Find Gaps; They Do Not Manufacture Green Status

只用 Agent 完成需求工作无需 Python。运行零模型本地门禁需要 Python 3.10+，以及 PyYAML、jsonschema **两个本地依赖**。以下统一使用 `python`；若系统只提供 `python3`，替换命令前缀即可。  
**English:** Python is not required to use the Skill conversationally. Deterministic local gates require Python 3.10+, PyYAML, and jsonschema. Replace `python` with `python3` when needed.

```bash
python -m pip install -r scripts/requirements.txt
python scripts/ai_delivery_spec_cli.py route-stage --target clarify --artifact problem-brief.md --format json
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd requirements/PRD.md --level L2 --language auto
```

持久化产物使用 `ADS:*` 语义锚点和 `resume_context` 续跑。门禁区分 `BLOCK / P0_UNKNOWN / GAP / PASS` 并记录 `not_proven`；静态 PASS 不证明真实实现、法规适用性或客户验收。  
**English:** Persistent artifacts use `ADS:*` anchors and `resume_context`. Gates distinguish `BLOCK / P0_UNKNOWN / GAP / PASS` and retain `not_proven`. A static PASS does not prove real implementation, legal applicability, or customer acceptance.

复杂项目才启用 Product Truth。`init-requirements` 只生成含占位符和空分片的脚手架；先填入已确认业务事实，再运行 `compile-truth`，否则门禁会受控阻断。  
**English:** Product Truth is for complex projects. `init-requirements` creates an incomplete scaffold; add confirmed business facts before compiling, or the gate will block by design.

```bash
python scripts/ai_delivery_spec_cli.py init-requirements --output requirements --with-product-truth
python scripts/ai_delivery_spec_cli.py compile-truth --index requirements/truth/index.yaml
python scripts/ai_delivery_spec_cli.py trace --truth requirements/truth/compiled/product-truth.yaml --output requirements/traceability.yaml --baseline-version 1.0
python scripts/ai_delivery_spec_cli.py impact --truth requirements/truth/compiled/product-truth.yaml --change requirements/changes/CHG-CORE-001.yaml
```

团队自己的术语和规则放在私有 `custom/`。内置领域包为 `traffic`、`crm`、`education-it`、`data-product`、`ai-native`、`media-knowledge`、`oa`、`medical-hospital-it`，当前成熟度均为 `contract_tested`；实践状态分别使用 `production_practiced` 或 `knowledge_only`。这些标签不等于当前项目已获专家确认或生产可用。  
**English:** Put organization-specific terms and rules in private `custom/` extensions. Built-in domain packs are contract-tested references with explicit practice status; they are not proof that a specific project has expert approval or is production-ready.

## 边界与验证｜Scope and Evidence Boundaries

AI Delivery Spec 不接管排期、Sprint、技术架构决策、代码生成、CI/CD、部署和运营。它不能替代产品负责人、架构师、领域专家、测试或客户签署。  
**English:** AI Delivery Spec does not own scheduling, Sprints, technical architecture decisions, code generation, CI/CD, deployment, or operations. It does not replace accountable product, architecture, domain, QA, or customer decisions.

```bash
python scripts/ai_delivery_spec_cli.py check
python scripts/ai_delivery_spec_cli.py check --profile release --keep-going
```

`SKILL.md` 是触发与路由；`references/` 是按需合同；`schemas/` 与 `scripts/` 是确定性门禁；`maintainer/` 只服务发版验证，不进入普通项目上下文。完整证据边界见[维护者说明](maintainer/README.md)，变化见 [CHANGELOG](CHANGELOG.md)。  
**English:** `SKILL.md` handles discovery and routing; `references/` contains on-demand contracts; `schemas/` and `scripts/` provide deterministic gates; `maintainer/` is release-only. See the [maintainer guide](maintainer/README.md) for evidence boundaries and the [changelog](CHANGELOG.md) for version history.

## 支持项目｜Support the Project

有 Bug 或建议请[提交 Issue](https://github.com/franklinxkk/ai-delivery-spec/issues)。如果项目帮你减少了误解与返工，欢迎 [Star ⭐](https://github.com/franklinxkk/ai-delivery-spec)；贡献说明见 [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)。  
**English:** [Open an Issue](https://github.com/franklinxkk/ai-delivery-spec/issues) for bugs or suggestions. If the project reduces misunderstanding or rework, please [Star it ⭐](https://github.com/franklinxkk/ai-delivery-spec). See [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) to contribute.
