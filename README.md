# AI Delivery Spec

> Product-side Spec-Driven Delivery for PMs and product teams who need PRDs,
> prototypes, acceptance criteria, and coding-agent handoff to stay consistent.
>
> 面向产品经理、产研团队和 AI 编程团队的产品侧 SDD 规范：把想法、竞品、原型、PRD、验收、上线和 AI Coding 交接统一成可读、可测、可实现的一套交付标准。

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/version-4.9.7-green.svg)]()
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-purple.svg)](https://openclaw.ai)
![skills.sh](https://skills.sh/b/franklinxkk/ai-delivery-spec)

**AI Delivery Spec is not another PRD template.** It is a tool-agnostic
delivery framework for turning messy product input into human-readable product
specs and machine-readable implementation contracts.

It works with ChatGPT, Claude, Gemini, Codex, Cursor, GitHub Copilot Workspace,
OpenClaw, and any AI tool that can read Markdown.

中文关键词：产品经理、PRD、需求文档、产品需求文档、需求规格说明书、原型、竞品分析、AI Coding、AI Native、Spec-Driven Development、SDD、产研协同、测试验收、ToB、ToG、SaaS、CRM、交通安全、高校信息化、医疗信息化。

## The Pain / 解决什么问题

AI coding is fast. Enterprise product delivery is still slow because the
handoff breaks:

| Common Failure | What AI Delivery Spec Forces |
|---|---|
| PRD is readable by AI but not by developers, QA, or stakeholders | scenario-first, human-readable PRD with role paths, page layout, fields, rules, exceptions, NFR, and acceptance |
| Prototype looks good but cannot be tested or implemented | `data-testid`, `data-action`, IA Skeleton, page/region layout, interaction ledger, and demo-closed checks |
| Coding agent gets vague requirements and invents behavior | AI-Coding PRD with `ac_structured`, API/data/event contracts, `AGENTS.md`, `CLAUDE.md`, Cursor rules, and manifest |
| AI features ship without runtime safety | write scope, human gate, fallback, eval, rollback, observability, prompt/version governance |
| PM, frontend, backend, algorithm, and QA read different truths | one source PRD with human-readable spec plus machine-readable contracts |

## What You Can Produce / 你能产出什么

- **Light PRD**: turn a rough idea, meeting note, boss message, or customer pain
  into a structured requirement draft.
- **Human-First Full PRD**: Tencent-style readable lifecycle PRD for PM,
  frontend, backend, algorithm, QA, vendor, sponsor, and customer review.
- **AI-Coding Full PRD**: Human-First PRD plus AC-YAML, machine-readable
  contracts, API/event/data stubs, delivery manifest, and coding-agent rules.
- **Prototype Delivery Pack**: clickable prototype requirements with stable
  test IDs, actions, state rules, role paths, shadow-test isolation, and demo
  mode.
- **Review Report**: PRD/prototype gap review across product, engineering,
  QA, architecture, AI, and operations perspectives.
- **Domain-Aware Specs**: traffic safety, CRM, higher-education IT, and
  medical/hospital IT domain modules.

## Install / 安装

### Install With skills.sh / Skills CLI

```bash
npx skills add franklinxkk/ai-delivery-spec
```

### Clone

```bash
git clone https://github.com/franklinxkk/ai-delivery-spec.git
```

### Manual Install To Claude Code

```bash
cp -r ai-delivery-spec ~/.claude/skills/ai-delivery-spec
```

## 10-Minute Quick Start / 10 分钟开始

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

## Choose Your Work Path / 选择工作路径

| Work Path | Use When | Main Output |
|---|---|---|
| Traditional / Enterprise Product Lifecycle | human PM/RD/QA review, vendor delivery, customer acceptance, launch, post-launch review | Human-First Full PRD, lifecycle annex, WBS, risk, test, readiness, post-launch review |
| AI Native Product Discovery | AI-native product brainstorming, agent workflow, model/tool/runtime design, AI governance | opportunity shaping, AI centrality, AI feature/native contract, prototype, runtime/eval/fallback |
| AI Coding Delivery | competitor/prototype/requirements must become a coding-agent-ready implementation spec | AI-Coding Full PRD, `ac_structured`, API/event/data contract, manifest, AGENTS/CLAUDE/Cursor rules |

## PRD Profile Selector / PRD 类型选择

| Intent | Profile | Output |
|---|---|---|
| quick review or gap list | Contract Summary | concise decisions, gaps, assumptions, and upgrade triggers |
| humans will review/develop/test/outsource | Human-First Full PRD | readable full PRD with scenarios, page layout, fields, interactions, rules, exceptions, acceptance, and handoff notes |
| coding agent will implement | AI-Coding Full PRD | Human-First PRD plus AC-YAML, machine-readable contracts, manifest, and agent rules |

Default rule: if frontend, backend, algorithm, QA, vendor, customer, or sponsor
will use the document, choose **Human-First Full PRD**. Upgrade to
**AI-Coding Full PRD** only when implementation by Cursor, Claude Code, Copilot,
Codex, Devin, or another coding agent is explicit.

## Who Should Use This / 适合谁

| Persona | Start Here | Typical Outcome |
|---|---|---|
| Solo PM + AI assistant | L0/L1 + Light PRD | turn an idea or rough note into a usable PRD draft |
| 2-8 person product team | L1/L2 + PRD + prototype + acceptance | align PM, frontend, backend, algorithm, and QA before build |
| Enterprise / public-sector delivery team | L2/L3 + readiness + domain modules | support bids, customer demos, regulated launch, and acceptance |
| AI-native product team | L3 + AI runtime/eval/ops contracts | define human gates, fallback, evaluation, rollback, and observability |
| Coding-agent users | AI-Coding Full PRD | generate `AGENTS.md`, `CLAUDE.md`, Cursor rules, AC-YAML, and manifest |

Do not use this framework for pure code syntax questions, unrelated debugging,
copy rewriting, or casual brainstorming with no delivery intent.

## What Makes It Different / 核心差异

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

## Delivery Package Convention / 交付包约定

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

## Runtime Architecture / 运行架构

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

## Toolchain Integration / 工具链集成

AI Delivery Spec does not require a specific tracker or coding agent. Use the
same source PRD and export only the slices each tool needs:

| Tool / Surface | Input Artifact | Output / Use | Put It Here |
|---|---|---|---|
| Cursor / Claude Code / Codex / Copilot Workspace | AI-Coding Full PRD, `ac_structured`, prototype | implementation rules and testable build plan | `delivery/agents/` |
| Jira / TAPD / Linear / GitHub Issues | vertical slice backlog, blocker table, bug records | tasks, risks, defects | project tracker |
| Figma / design review | IA Skeleton, Layout IDs, page regions, component states | design alignment and visual gaps | design file or design review note |
| Playwright / Browser Use | `data-testid`, `data-action`, demo paths, AC-YAML | automated verification | `delivery/evidence/` |
| Notion / Confluence / Feishu | Human-First Full PRD and lifecycle annex | stakeholder-readable source of truth | team knowledge base |

## Output Selector / 输出形态选择

| Situation | Use | Expected Output |
|---|---|---|
| rough idea or pain | `Mode=Lite` + clarification | questions, assumptions, opportunity shape |
| internal alignment | `Tier=L1` | light PRD and gaps |
| development/QA handoff | `Tier=L2` + Human-First Full PRD | full PRD, FRR, IA Skeleton, page/field/action detail, acceptance |
| customer demo | Gate 2 prototype path | clickable prototype and verification |
| AI-core/high-risk automation | `Tier=L3` | runtime, eval, fallback, ops contracts |
| coding-agent implementation | AI-Coding Full PRD + coding-agent compatibility | Human-First PRD + AC-YAML, agent rules, validation checks |

## Domain Modules / 领域模块

| Domain | File |
|---|---|
| Traffic Safety / 交通安全 | `references/domain-traffic.md` |
| CRM / 客户经营 | `references/domain-crm.md` |
| Higher-Education IT / 高校教育信息化 | `references/domain-education-it.md` |
| Medical / Hospital IT / 医疗医院信息化 | `references/domain-medical-hospital-it.md` |

Adding a new industry: copy `references/domain-module-template.md`, keep the
section contract, and replace domain-specific vocabulary, workflows, state
machines, privacy rules, and test scenarios.

## Examples / 示例

- [CRM Response Center](examples/crm-response-center/README.md)
- [Traffic Safety SaaS](examples/traffic-safety-saas/README.md)
- [Higher-Education IT](examples/education-it/README.md)
- [Medical / Hospital IT](examples/medical-hospital-it/README.md)

See [examples/README.md](examples/README.md) for the full example index.

## Reference File Policy / reference 文件策略

The repository intentionally keeps references compact:

- runtime entrypoints;
- current PRD templates;
- domain modules;
- coding-agent and realtime add-ons;
- validators and examples.

Historical split protocols have been consolidated into `advanced-extensions.md`
or `delivery-core.md`. Do not re-add one-off reference files unless they are
needed by at least three real projects, two domains, and one validator change.

## Validation / 校验

```powershell
python scripts/validate_skill_consistency.py
python scripts/validate_routing_scenarios.py
python scripts/validate_release_readiness.py
python scripts/validate_ia_skeleton.py --ia-skeleton delivery/ia-skeleton.yaml --prototype delivery/prototype/app.html --prd delivery/prd/main.md
python scripts/validate_coding_agent_contract.py --prd delivery/prd/main.md --prototype delivery/prototype/app.html
```

## License / 许可证

Apache-2.0. See [LICENSE](LICENSE).
