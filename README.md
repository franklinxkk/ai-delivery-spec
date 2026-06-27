# AI Delivery Spec

> Product-side Spec-Driven Delivery for teams that need PRDs, prototypes,
> acceptance criteria, and coding-agent handoff to stay consistent.
>
> 面向产品、研发、算法、测试和交付团队的产品侧 SDD 规范：让需求、原型、验收和 AI 编程交接保持一致。

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/version-4.9.2-green.svg)]()
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-purple.svg)](https://openclaw.ai)

AI Delivery Spec is tool-agnostic. It works with ChatGPT, Claude, Gemini,
Codex, Cursor, GitHub Copilot Workspace, OpenClaw, and any AI tool that can
read Markdown.

AI Delivery Spec is not just a PRD template and not a code generator. It is a
delivery standard that aligns product truth before build: scenarios, roles,
state, fields, prototype behavior, acceptance, engineering contract, and AI /
coding-agent handoff.

中文关键词：产品经理、PRD、需求文档、原型、竞品分析、AI Coding、AI Native、产研协同、测试验收、ToB、ToG、SaaS、CRM、交通安全、高校信息化、医疗信息化。

## Why It Exists / 为什么需要

AI coding agents can produce code quickly, but enterprise and public-sector
delivery still fails when:

- requirements are readable by AI but not by humans;
- prototypes are beautiful but not testable;
- PRDs list features but miss role paths, states, fields, exceptions, and
  acceptance criteria;
- AI features lack runtime, evaluation, fallback, and human-gate contracts;
- developers and QA cannot locate the locked PRD, prototype, IA skeleton, or
  acceptance files.

AI Delivery Spec makes product artifacts both human-readable and
machine-actionable.

Lifecycle bridge:

```text
Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire
```

## Who Should Use This / 适合谁

| Persona | Start Here | Typical Outcome |
|---|---|---|
| Solo PM + AI assistant | L0/L1 + light PRD | turn an idea or rough note into a usable PRD draft |
| 2-8 person product team | L1/L2 + PRD + prototype + acceptance | align PM, frontend, backend, algorithm, and QA before build |
| Enterprise/public-sector delivery team | L2/L3 + readiness + domain modules | support bids, customer demos, regulated launch, and acceptance |
| AI-native product team | L3 + AI runtime/eval/ops contracts | define human gates, fallback, evaluation, rollback, and observability |
| Coding-agent users | coding-agent compatibility mode | generate `AGENTS.md`, `CLAUDE.md`, Cursor rules, AC-YAML, and manifest |

Do not use this framework for pure code syntax questions, unrelated debugging,
copy rewriting, or casual brainstorming with no delivery intent.

## What Makes It Different / 核心差异

| Capability | AI Delivery Spec | Common PM Skills | spec-kit |
|---|:---:|:---:|:---:|
| Product-side PRD + prototype governance | Yes | Partial | No |
| L0-L3 delivery tiering | Yes | Partial | No |
| 0D triage to prune unnecessary gates | Yes | No | No |
| Human-readable FRR + machine-readable contracts | Yes | Partial | Yes, engineering-side |
| Prototype testability and `data-*` contracts | Yes | No | No |
| Replaceable domain modules | Yes | Rare | No |
| AI runtime/evaluation/fallback governance | Yes | Rare | No |
| Coding-agent handoff package | Yes | Partial | Yes, after spec is approved |

Use **AI Delivery Spec** when the requirement, prototype, domain logic, role
path, or acceptance evidence is not yet stable.

Use **spec-kit** when the approved specification already exists and you need
engineering task decomposition. They are complementary: AI Delivery Spec
stabilizes product-side truth; spec-kit can consume the stabilized truth for
implementation planning.

## 10-Minute Quick Start / 10 分钟开始

### 1. Choose a PRD Profile / 选择 PRD 类型

| Intent | Profile | Output |
|---|---|---|
| quick review or gap list | Contract Summary | concise decisions, gaps, and upgrade triggers |
| humans will review/develop/test/outsource | Human-First Full PRD | readable full PRD with page layout, fields, interactions, rules, exceptions, acceptance, and handoff notes |
| coding agent will implement | AI-Coding Full PRD | Human-First PRD plus AC-YAML, machine-readable contracts, manifest, and agent rules |

Default rule: if frontend, backend, algorithm, QA, vendor, customer, or sponsor
will use the document, choose **Human-First Full PRD**. Upgrade to
**AI-Coding Full PRD** only when implementation by Cursor, Claude Code, Copilot,
Codex, or another coding agent is explicit.

### 2. Generate a Light PRD / 生成轻量 PRD

```text
Use AI Delivery Spec.
Mode=Lite, Tier=L1.
Write a light PRD for: [feature + target user + business goal].
Use prd-light-template and list missing decisions at the end.
```

### 3. Review a PRD / 审核需求文档

```text
Use AI Delivery Spec Gate 1 and Gate 3 to review this PRD.
Check user story, role path, visible result, domain result, state transitions,
exceptions, data permission, and whether developers/QA can implement and test it.
```

### 4. Upgrade to Development Handoff / 升级到开发交付

```text
Upgrade this PRD to L2 Standard.
Use Human-First Full PRD unless I explicitly ask for all-AI coding.
Add complete FRRs, IA Skeleton, page/region layout, field dictionary,
state/action matrix, frontend/backend/QA handoff notes, acceptance, and traceability.
```

### 5. Coding Agent Handoff / 交给 AI 编程智能体

```text
Use AI Delivery Spec coding-agent compatibility mode.
Use AI-Coding Full PRD.
Given this PRD and prototype, generate AGENTS.md / CLAUDE.md / Cursor rules,
convert FRR section 16 acceptance into ac_structured YAML, and identify P0/P1 tests.
```

## Install / 安装

```bash
# Clone
git clone https://github.com/franklinxkk/ai-delivery-spec.git

# Skills CLI
npx skills add franklinxkk/ai-delivery-spec

# Manual install to Claude Code
cp -r ai-delivery-spec ~/.claude/skills/ai-delivery-spec
```

| Tool / Surface | Install / Use |
|---|---|
| Claude Code Skills CLI | `npx skills add franklinxkk/ai-delivery-spec` |
| Claude Code manual | copy repo folder to `~/.claude/skills/ai-delivery-spec` |
| Codex / ChatGPT / Gemini | clone the repo, attach or reference `SKILL.md`, and use `agents/openai-codex.md` when implementation is required |
| OpenAI / skill UI metadata | `agents/openai.yaml` provides display metadata; it is not the full execution protocol |
| Cursor | place generated `.cursor/rules` from `delivery/agents/` in the implementation repo |
| Copilot Workspace / other coding agents | give it `delivery/manifest.json`, PRD, prototype, AC-YAML, and agent rules |

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

## Three Main Work Paths / 三类主路径

| Work Path | Use This When | Main Artifacts |
|---|---|---|
| Traditional / Enterprise Product Lifecycle | human PM/RD/QA review, vendor development, launch, acceptance | Human-First Full PRD, lifecycle annex, review/sign-off, rollout/readiness, post-launch review |
| AI Native Product Discovery | AI-native product brainstorming, competitor research, agent workflow, runtime/eval/fallback | opportunity shaping, AI centrality, AI feature/native contract, prototype, AI PRD |
| AI Coding Delivery | competitor screenshots, prototypes, or requirements must become a detailed AI-friendly implementation spec | AI-Coding Full PRD, locked prototype, `ac_structured`, manifest, AGENTS/CLAUDE/Cursor rules |

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

## Examples / 示例

- [CRM Response Center](examples/crm-response-center/README.md)
- [Traffic Safety SaaS](examples/traffic-safety-saas/README.md)
- [Higher-Education IT](examples/education-it/README.md)
- [Medical / Hospital IT](examples/medical-hospital-it/README.md)

See [examples/README.md](examples/README.md) for the full example index.

## Validation / 校验

```powershell
python scripts/validate_skill_consistency.py
python scripts/validate_routing_scenarios.py
python scripts/validate_ia_skeleton.py --ia-skeleton delivery/ia-skeleton.yaml --prototype delivery/prototype/app.html --prd delivery/prd/main.md
python scripts/validate_coding_agent_contract.py --prd delivery/prd/main.md --prototype delivery/prototype/app.html
```

## License / 许可证

Apache-2.0. See [LICENSE](LICENSE).
