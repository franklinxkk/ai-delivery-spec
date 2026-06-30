# AI Delivery Spec（产品侧 SDD / AI Coding 交付规范）

**Search keywords**: product management | PRD | product requirements document |
requirements engineering | spec-driven development | SDD | AI coding |
coding-agent handoff | acceptance criteria | prototype testability | product ops |
enterprise software | SaaS | CRM | BI | ChatBI | Data Agent | AI Native |
agentic workflow | spec-kit | skills.sh

**中文关键词**：产品经理 | 产品需求文档 | 需求规格说明书 | PRD | 原型 |
验收标准 | AI 编程 | AI Coding | 编码智能体 | 产品侧 SDD | 产研协同 |
测试验收 | 自动化测试 | ToB | ToG | SaaS | CRM | 数据产品 | ChatBI |
Data Agent | AI 原生 | 智能体工作流 | spec-kit | skills.sh

> 面向产品经理、产研团队和 AI 编程团队的产品侧 SDD 规范：把想法、竞品、原型、PRD、验收、上线和 AI Coding 交接统一成可读、可测、可实现的一套交付标准。
>
> Product-side Spec-Driven Delivery for PMs and product teams who need PRDs,
> prototypes, acceptance criteria, and coding-agent handoff to stay consistent.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/version-4.9.10-green.svg)]()
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-purple.svg)](https://openclaw.ai)
![skills.sh](https://skills.sh/b/franklinxkk/ai-delivery-spec)

**AI Delivery Spec is not another PRD template.** It is a tool-agnostic
delivery framework for turning messy product input into human-readable product
specs and machine-readable implementation contracts.

It works with ChatGPT, Claude, Gemini, Codex, Cursor, GitHub Copilot Workspace,
OpenClaw, and any AI tool that can read Markdown.

Recommended GitHub topics:

```text
product-management, prd, requirements-engineering, spec-driven-development,
ai-coding, coding-agent, ai-agents, ai-native, agent-skills, skills-sh,
spec-kit, acceptance-criteria, prototype, software-delivery,
enterprise-software, saas, crm, business-intelligence, chatbi, data-agent
```

Use it when a team needs one shared source of truth for PMs, developers,
architects, QA, vendors, customers, and coding agents.

## 解决什么问题 / The Pain

AI coding is fast. Enterprise product delivery is still slow because the
handoff breaks:

| Common Failure | What AI Delivery Spec Forces |
|---|---|
| PRD is readable by AI but not by developers, QA, or stakeholders | scenario-first, human-readable PRD with role paths, page layout, fields, rules, exceptions, NFR, and acceptance |
| Prototype looks good but cannot be tested or implemented | `data-testid`, `data-action`, IA Skeleton, page/region layout, interaction ledger, and demo-closed checks |
| Coding agent gets vague requirements and invents behavior | AI-Coding PRD with `ac_structured`, API/data/event contracts, `AGENTS.md`, `CLAUDE.md`, Cursor rules, and manifest |
| Large PRD starts detailed but later modules become thin | Stage 3.5 cross-module flow contract, FRR completion gates, batch continuation, and post-generation checklist |
| AI features ship without runtime safety | write scope, human gate, fallback, eval, rollback, observability, prompt/version governance |
| PM, frontend, backend, algorithm, and QA read different truths | one source PRD with human-readable spec plus machine-readable contracts |

## 你能产出什么 / What You Can Produce

- **Light PRD**: turn a rough idea, meeting note, boss message, or customer pain
  into a structured requirement draft.
- **Human-First Full PRD**: Tencent-style readable lifecycle PRD for PM,
  frontend, backend, algorithm, QA, vendor, sponsor, and customer review.
- **AI-Coding Full PRD**: Human-First PRD plus AC-YAML, machine-readable
  contracts, API/event/data stubs, delivery manifest, and coding-agent rules.
- **Multi-Module PRD Pack**: master contract plus module PRDs, cross-module
  flow contract, field mapping, event/notification inventory, and E2E canvas.
- **Prototype Delivery Pack**: clickable prototype requirements with stable
  test IDs, actions, state rules, role paths, shadow-test isolation, and demo
  mode.
- **Review Report**: PRD/prototype gap review across product, engineering,
  QA, architecture, AI, and operations perspectives.
- **Domain-Aware Specs**: traffic safety, CRM, AI+Data / data mart / BI /
  reporting / fill-in, AI Native / agentic systems, higher-education IT, and
  medical/hospital IT domain modules.

## 安装 / Install

### Install With skills.sh / Skills CLI

```bash
npx skills add franklinxkk/ai-delivery-spec
```

Useful skills.sh commands:

```bash
# list skills discovered from this repo
npx skills add franklinxkk/ai-delivery-spec --list

# install to specific agents
npx skills add franklinxkk/ai-delivery-spec -a codex -a claude-code -a cursor

# use without installing
npx skills use franklinxkk/ai-delivery-spec --agent codex

# update installed copy
npx skills update ai-delivery-spec
```

This repository keeps `SKILL.md` at the root, so Skills CLI / skills.sh can
discover it directly. Root `SKILL.md` plus valid YAML frontmatter is the
cross-agent compatibility baseline.

### Clone

```bash
git clone https://github.com/franklinxkk/ai-delivery-spec.git
```

### Manual Install To Claude Code

```bash
cp -r ai-delivery-spec ~/.claude/skills/ai-delivery-spec
```

## 10 分钟快速上手 / Quick Start

### 产品经理 5 步上手 / PM Quickstart

1. 粗想法先用 Light PRD：说清目标用户、痛点、期望结果，让 AI Delivery Spec 先问最少必要问题。
2. 要给研发、测试、客户或外包团队看时，升级为 Human-First Full PRD。
3. 要交给 Cursor、Claude Code、Codex、Copilot 等自动实现时，再升级为 AI-Coding Full PRD。
4. 有原型、截图、Excel、旧系统或竞品时，先跑 Stage 0，把页面、字段、动作、状态、证据和缺口抽出来。
5. 最终交付前必须看 Completion State：只有 `PASS` 才代表当前范围已闭合。

### 按角色/痛点选择入口 / Role-Based Entry

| Role / Pain | Start With | Ask For |
|---|---|---|
| 初级产品经理 / new PM | Light PRD + clarification | turn rough input into goals, users, scenarios, open questions, and next checks |
| 中级产品经理 / feature owner | Human-First Full PRD | complete module specs, role paths, field dictionaries, rules, exceptions, and acceptance |
| 高级产品经理 / complex owner | Stage 0 + Stage 3.5 + gates | prototype reverse engineering, IA Skeleton, cross-module flow contract, E2E canvas, and launch readiness |
| 产品总监 / product lead | opportunity shaping + lifecycle review | outcome, priority, roadmap assumptions, resource tradeoffs, launch risks, and learn/retire signals |
| 开发/架构 / engineering lead | AI-Coding Full PRD | API/data/event contracts, source-of-truth order, manifest, AGENTS/CLAUDE/Cursor rules |
| 测试/RPA / QA automation | coding-agent contract checks | AC-YAML, data-testid/action/state/API mapping, positive/negative cases, regression paths |

### 1. From Rough Idea To PRD / 从想法到需求

```text
Use AI Delivery Spec.
I have a rough idea: [target user + pain + expected result].
First ask the minimum clarification questions, then produce a light PRD.
```

### 2. Review An Existing PRD / 审核已有需求文档

```text
Use AI Delivery Spec Gate 1 and Gate 3 to review this PRD.
Check user story, role path, page layout, fields, state transitions,
exceptions, permissions, testability, and whether developers/QA can implement it.
```

### 3. Upgrade To Human-First Full PRD / 升级为古法研发可读 PRD

```text
Use AI Delivery Spec.
Upgrade this requirement to L2 Standard.
Use Human-First Full PRD.
Include complete module/function specs, page layout, field dictionary,
interaction flow, business rules, exceptions, permissions, NFR,
frontend/backend/QA handoff notes, acceptance, WBS, risk, test, launch review.
```

### 4. Create AI-Coding PRD / 生成 AI Coding 需求规格说明书

```text
Use AI Delivery Spec coding-agent compatibility mode.
Use AI-Coding Full PRD.
Given this PRD/prototype, generate complete FRRs, ac_structured YAML,
API/event/data contracts, delivery/manifest.json, AGENTS.md, CLAUDE.md,
Cursor rules, and implementation validation checks.
```

### 5. Reverse Engineer A Prototype Or Competitor / 从原型或竞品反推需求

```text
Use AI Delivery Spec Stage 0.
Extract views, roles, data actions, states, fields, modals, entities,
business flows, gaps, and source evidence from this prototype/screenshot.
Then help me shape a differentiated PRD and prototype plan.
```

### 6. Brainstorm Product Direction / 产品脑暴

```text
Use AI Delivery Spec opportunity shaping.
I want to explore [problem / market / user group].
First help me separate outcome, customer problem, options, assumptions,
validation path, and next artifact. Do not jump directly to a full PRD.
```

If you already use a generic `brainstorming` skill, run it for divergent ideas
first, then feed the selected direction into AI Delivery Spec for PRD, prototype,
acceptance, and handoff.

### 7. Prototype Visual Style / 原型视觉风格

```text
Use AI Delivery Spec prototype path.
Create a clickable prototype for [domain].
Ask me to choose visual style only if it affects brand/demo/acceptance.
If unspecified, use a restrained enterprise UI and keep data-testid/data-action
coverage complete.
```

When a dedicated frontend-design/UIUX/design-system skill is available, use it
for visual language and component choices. AI Delivery Spec owns IA, state,
actions, business rules, and testability.

## 选择工作路径 / Work Paths

| Work Path | Use When | Main Output |
|---|---|---|
| Traditional / Enterprise Product Lifecycle | human PM/RD/QA review, vendor delivery, customer acceptance, launch, post-launch review | Human-First Full PRD, lifecycle annex, WBS, risk, test, readiness, post-launch review |
| AI Native Product Discovery | AI-native product brainstorming, agent workflow, model/tool/runtime design, AI governance | opportunity shaping, AI centrality, AI feature/native contract, prototype, runtime/eval/fallback |
| AI Coding Delivery | competitor/prototype/requirements must become a coding-agent-ready implementation spec | AI-Coding Full PRD, `ac_structured`, API/event/data contract, manifest, AGENTS/CLAUDE/Cursor rules |

## PRD 类型选择 / Profile Selector

| Intent | Profile | Output |
|---|---|---|
| quick review or gap list | Contract Summary | concise decisions, gaps, assumptions, and upgrade triggers |
| humans will review/develop/test/outsource | Human-First Full PRD | readable full PRD with scenarios, page layout, fields, interactions, rules, exceptions, acceptance, and handoff notes |
| coding agent will implement | AI-Coding Full PRD | Human-First PRD plus AC-YAML, machine-readable contracts, manifest, and agent rules |

Default rule: if frontend, backend, algorithm, QA, vendor, customer, or sponsor
will use the document, choose **Human-First Full PRD**. Upgrade to
**AI-Coding Full PRD** only when implementation by Cursor, Claude Code, Copilot,
Codex, Devin, or another coding agent is explicit.

## 适合谁 / Who Should Use This

| Persona | Start Here | Typical Outcome |
|---|---|---|
| Solo PM + AI assistant | L0/L1 + Light PRD | turn an idea or rough note into a usable PRD draft |
| 2-8 person product team | L1/L2 + PRD + prototype + acceptance | align PM, frontend, backend, algorithm, and QA before build |
| Enterprise / public-sector delivery team | L2/L3 + readiness + domain modules | support bids, customer demos, regulated launch, and acceptance |
| AI-native product team | L3 + AI runtime/eval/ops contracts | define human gates, fallback, evaluation, rollback, and observability |
| Coding-agent users | AI-Coding Full PRD | generate `AGENTS.md`, `CLAUDE.md`, Cursor rules, AC-YAML, and manifest |

Do not use this framework for pure code syntax questions, unrelated debugging,
copy rewriting, or casual brainstorming with no delivery intent.

## 核心差异 / What Makes It Different

| Capability | AI Delivery Spec | Common PM Skills | spec-kit |
|---|:---:|:---:|:---:|
| Product-side PRD + prototype governance | Yes | Partial | No |
| Idea/meeting note/prototype reverse engineering | Yes | Partial | No |
| L0-L3 delivery tiering | Yes | Partial | No |
| Human-readable PRD plus machine-readable contract | Yes | Partial | Yes, engineering-side |
| Prototype testability and `data-*` contracts | Yes | No | No |
| AI runtime/evaluation/fallback governance | Yes | Rare | No |
| Coding-agent handoff package | Yes | Partial | Yes, after spec approval |
| Replaceable domain modules | Yes | Rare | No |

Use **AI Delivery Spec** when the requirement, prototype, domain logic, role
path, or acceptance evidence is not yet stable.

Use **spec-kit** when the approved specification already exists and you need
engineering task decomposition. They are complementary: AI Delivery Spec
stabilizes product-side truth; spec-kit can consume the stabilized truth for
implementation planning.

### spec-kit 配合方式 / spec-kit Interop

Use this sequence when both tools are present:

```text
AI Delivery Spec: Discover -> Human-First / AI-Coding PRD -> prototype/IA/AC
spec-kit: /speckit.constitution -> /speckit.specify -> /speckit.plan -> /speckit.tasks -> /speckit.implement
```

Mapping:

| AI Delivery Spec | spec-kit |
|---|---|
| `delivery/prd/main.md` | feature `spec.md` input / source evidence |
| `delivery/ia-skeleton.yaml` | product IA annex, no direct replacement |
| `delivery/prototype/` | interactive evidence, no direct replacement |
| `delivery/acceptance/ac-structured.yaml` | success criteria and tests |
| `delivery/agents/AGENTS.md` | coding-agent operating rules |

Rule: spec-kit can decompose and implement after product truth is stable. It
must not replace the Human-First PRD, AI-Coding PRD, IA Skeleton, or prototype
evidence.

## 交付包约定 / Delivery Package Convention

When a PRD/prototype will be consumed by a coding agent or development team,
use this structure:

```text
delivery/
  prd/                        # PRD Markdown files
  prototype/                  # HTML prototype(s)
  ia-skeleton.yaml            # Stage 3.5 structural truth
  acceptance/                 # AC-YAML files, one per FRR or module
  agents/                     # AGENTS.md / CLAUDE.md / .cursor/rules
  evidence/                   # validation logs, screenshots, UAT notes
  manifest.json               # artifact list, versions, hashes, source status
```

Coding agents should locate artifacts in this order:

1. `delivery/manifest.json`
2. `delivery/ia-skeleton.yaml`
3. `delivery/prd/`
4. `delivery/prototype/`
5. `delivery/acceptance/`
6. `delivery/agents/`

## 运行架构 / Runtime Architecture

Default runtime has four entrypoints:

```text
SKILL.md                              triage, routing, gates
references/delivery-core.md           PRD, stories, state, DDD/API/data, lifecycle
references/prototype-testability.md   prototype, mobile, interaction testability
references/advanced-extensions.md     AI, SaaS, approval, reporting, global/domain extensions
```

Optional triggered references:

```text
references/coding-agent-compat.md     AC-YAML, AI runtime schema, AGENTS/CLAUDE/Cursor rules
references/realtime-contract.md       SSE/WebSocket/polling/push/countdown contracts
```

Templates and domain modules are load-on-demand source assets. They should not
be loaded unless an entrypoint instructs the agent to use them.

## 工具链集成 / Toolchain Integration

AI Delivery Spec does not require a specific tracker or coding agent. Use the
same source PRD and export only the slices each tool needs:

| Tool / Surface | Input Artifact | Output / Use | Put It Here |
|---|---|---|---|
| Cursor / Claude Code / Codex / Copilot Workspace | AI-Coding Full PRD, `ac_structured`, prototype | implementation rules and testable build plan | `delivery/agents/` |
| skills.sh / Skills CLI | root `SKILL.md` GitHub repo | install/use/update skill across Codex, Claude Code, Cursor, Copilot, Gemini CLI, and more | agent skill directories |
| spec-kit | approved PRD + AC + agent rules | engineering plan, tasks, and implementation convergence | `.specify/` and `specs/` |
| frontend-design / UIUX skills | IA Skeleton, prototype goal, brand/design system choice | visual language and component-system decisions | prototype/design artifacts |
| Jira / TAPD / Linear / GitHub Issues | vertical slice backlog, blocker table, bug records | tasks, risks, defects | project tracker |
| Figma / design review | IA Skeleton, Layout IDs, page regions, component states | design alignment and visual gaps | design file or design review note |
| Playwright / Browser Use | `data-testid`, `data-action`, demo paths, AC-YAML | automated verification | `delivery/evidence/` |
| Notion / Confluence / Feishu | Human-First Full PRD and lifecycle annex | stakeholder-readable source of truth | team knowledge base |

## 轻量 CLI / Helper CLI

The repository includes a small helper CLI for teams that want a repeatable
package layout without adopting another platform:

```powershell
# create delivery/ with prd, prototype, acceptance, agents, evidence, manifest
python scripts/ai_delivery_spec_cli.py init-delivery --output delivery

# run repository-level validators
python scripts/ai_delivery_spec_cli.py check

# run PRD/prototype checks when artifacts exist
python scripts/ai_delivery_spec_cli.py check --prd delivery/prd/main.md --prototype delivery/prototype/app.html --ia-skeleton delivery/ia-skeleton.yaml --target-language zh
```

On Windows, use `py -3` instead of `python` if the `python` launcher is not
registered in PATH.

This CLI is intentionally thin. It initializes the convention and calls the
same validators documented below; it is not a separate runtime or framework.

## 输出形态选择 / Output Selector

| Situation | Use | Expected Output |
|---|---|---|
| rough idea or pain | `Mode=Lite` + clarification | questions, assumptions, opportunity shape |
| internal alignment | `Tier=L1` | light PRD and gaps |
| development/QA handoff | `Tier=L2` + Human-First Full PRD | full PRD, FRR, IA Skeleton, page/field/action detail, acceptance |
| customer demo | Gate 2 prototype path | clickable prototype and verification |
| AI-core/high-risk automation | `Tier=L3` | runtime, eval, fallback, ops contracts |
| coding-agent implementation | AI-Coding Full PRD + coding-agent compatibility | Human-First PRD + AC-YAML, agent rules, validation checks |

## 多智能体生命周期验证 / Multi-Agent Lifecycle Validation

Before final publication, customer handoff, or GitHub release, validate the
selected domains across the full product lifecycle:

```text
Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire
```

Reviewer agents:

| Agent | Checks |
|---|---|
| PM Agent | outcome, scope, priority, stakeholder-readable PRD |
| Domain Expert Agent | standards, vocabulary, scenarios, policy constraints |
| Architecture / Data / AI Agent | state, data, integration, ontology, AI/runtime, security |
| QA Agent | acceptance, exception, permission, E2E, regression |
| Coding Agent | FRR completeness, AC-YAML, prototype data-* mapping, source-of-truth order |

Run:

```powershell
python scripts/validate_multi_agent_lifecycle_scenarios.py
```

The built-in simulation covers Traffic, CRM, AI+Data, AI Native / Agentic
Systems, Higher-Education IT, and Medical / Hospital IT across all lifecycle
stages and reviewer agents.

## 领域模块 / Domain Modules

| Domain | File |
|---|---|
| Traffic Safety / 交通安全 | `references/domain-traffic.md` |
| CRM / 客户经营 | `references/domain-crm.md` |
| AI Native / Agentic Systems / AI 原生与智能体系统 | `references/domain-ai-native.md` |
| AI+Data / Data Mart / BI / Reporting / 数据智能、数据集市、报表与填报 | `references/domain-data-mart.md` |
| Higher-Education IT / 高校教育信息化 | `references/domain-education-it.md` |
| Medical / Hospital IT / 医疗医院信息化 | `references/domain-medical-hospital-it.md` |

Adding a new industry: copy `references/domain-module-template.md`, keep the
section contract, and replace domain-specific vocabulary, workflows, state
machines, privacy rules, and test scenarios. Keep the First-Principles Domain Lens compact:
value object, role job, lifecycle state, source authority, high-risk boundary,
and test evidence.

## 示例 / Examples

- [CRM Response Center](examples/crm-response-center/README.md)
- [Traffic Safety SaaS](examples/traffic-safety-saas/README.md)
- [Higher-Education IT](examples/education-it/README.md)
- [Medical / Hospital IT](examples/medical-hospital-it/README.md)

See [examples/README.md](examples/README.md) for the full example index.

## Reference 文件策略 / File Policy

The repository intentionally keeps references compact:

- runtime entrypoints;
- current PRD templates;
- domain modules;
- coding-agent and realtime add-ons;
- validators and examples.

Historical split protocols have been consolidated into `advanced-extensions.md`
or `delivery-core.md`. Do not re-add one-off reference files unless they are
needed by at least three real projects, two domains, and one validator change.

## 校验 / Validation

```powershell
python scripts/validate_skill_consistency.py
python scripts/validate_routing_scenarios.py
python scripts/validate_release_readiness.py
python scripts/validate_ai_data_product_scenarios.py
python scripts/validate_multi_agent_lifecycle_scenarios.py
python scripts/ai_delivery_spec_cli.py check
python scripts/validate_ia_skeleton.py --ia-skeleton delivery/ia-skeleton.yaml --prototype delivery/prototype/app.html --prd delivery/prd/main.md
python scripts/validate_coding_agent_contract.py --prd delivery/prd/main.md --prototype delivery/prototype/app.html
```

## 许可证 / License

Apache-2.0. See [LICENSE](LICENSE).
