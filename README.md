# AI Delivery Spec

> Product-side Spec-Driven Delivery for teams that need PRDs, prototypes,
> acceptance criteria, and coding-agent handoff to stay consistent.
>
> 面向产品、研发、算法、测试与交付团队的产研交付规格：把需求、原型、验收、工程契约和 AI 编程交接放到同一套可追溯流程里。

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/version-4.7.3-green.svg)]()
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-purple.svg)](https://openclaw.ai)

AI Delivery Spec is tool-agnostic. It works with ChatGPT, Claude, Gemini,
Codex, Cursor, GitHub Copilot Workspace, OpenClaw, and any AI tool that can
read Markdown.

AI Delivery Spec 不是单纯的 PRD 模板，也不是代码生成框架。它是产品侧交付协议：在进入开发前，把业务场景、角色路径、状态流转、字段、原型交互、验收标准和 AI/coding-agent 契约对齐。

中文关键词：产品经理、需求文档、PRD、原型设计、竞品分析、AI 编程、AI Coding、AI Native、产研协同、测试验收、ToB、ToG、SaaS、CRM、交通安全、高校信息化、医疗信息化。

## Why It Exists / 为什么需要它

AI coding agents can produce code quickly, but ToB/ToG delivery still fails
when:

- requirements are readable by AI but not by humans;
- prototypes are beautiful but not testable;
- PRDs have functions but no role path, state, field, exception, or acceptance;
- AI features lack runtime, evaluation, fallback, and human-gate contracts;
- developers and QA cannot locate the locked PRD, prototype, IA skeleton, or
  acceptance files.

AI Delivery Spec solves this by making product artifacts both human-readable
and machine-actionable.

AI 编程能提升速度，但如果需求、原型、验收和工程交接不一致，速度只会放大返工。这个项目的目标是让产品文档既能给人评审，也能给 coding agent 解析。

Lifecycle bridge: `Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire`.

## Who Should Use This / 适合谁

| Persona | Start Here | Typical Outcome |
|---|---|---|
| Solo PM + AI assistant | L0/L1 + `prd-light-template` | turn an idea or rough note into a usable PRD draft |
| 2-8 person ToB product team | L1/L2 + PRD + prototype + acceptance | align PM, frontend, backend, algorithm, and QA before build |
| Enterprise delivery team | L2/L3 + readiness + domain modules | support bids, customer demos, regulated launch, and acceptance |
| AI-native product team | L3 + AI runtime/eval/ops contracts | define human gates, fallback, evaluation, rollback, and observability |
| Coding-agent users | coding-agent compatibility mode | generate `AGENTS.md`, `CLAUDE.md`, Cursor rules, and AC-YAML |

Do not use this framework for pure code syntax questions, unrelated debugging,
copy rewriting, or casual brainstorming with no delivery intent.

不适用于：纯代码语法问题、无关调试、单纯改文案、没有交付意图的随便聊天。

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

## 10-Minute Quick Start / 10 分钟快速开始

### Step 0. Choose the PRD profile / 先选 PRD Profile

| Your intent | Profile | What the AI should output |
|---|---|---|
| I only need a quick review or gap list | Contract Summary | concise decisions, gaps, and upgrade triggers |
| Humans will review, develop, test, or outsource this feature | Human-First Full PRD | use `references/templates/human-first-prd-template.md`; readable full PRD with page layout, fields, interactions, rules, exceptions, acceptance, and handoff notes |
| A coding agent will implement from the PRD/prototype | AI-Coding Full PRD | use `references/templates/ai-coding-prd-template.md`; Human-First Full PRD plus AC-YAML, machine-readable contracts, manifest, and agent rules |

默认原则：只要文档会给前端、后端、算法、测试、外包或客户评审使用，就用
**Human-First Full PRD**。只有明确要 Cursor / Claude Code / Copilot /
Codex 等 coding agent 直接实现时，才升级为 **AI-Coding Full PRD**。

### 1. Generate a light PRD / 生成轻量 PRD

```text
Use AI Delivery Spec.
Mode=Lite, Tier=L1.
Write a light PRD for: [feature + target user + business goal].
Use prd-light-template and list missing decisions at the end.
```

### 2. Review a PRD / 审核需求文档

```text
Use AI Delivery Spec Gate 1 and Gate 3 to review this PRD.
Check user story, role path, visible result, domain result, state transitions,
exceptions, data permission, and whether developers/QA can implement and test it.
```

### 3. Upgrade to development handoff / 升级到开发交付

```text
Upgrade this PRD to L2 Standard.
Use Human-First Full PRD unless I explicitly ask for all-AI coding.
Add complete FRRs, IA Skeleton, page/region layout, field dictionary,
state/action matrix, frontend/backend/QA handoff notes, acceptance, and
traceability.
```

### 4. Coding Agent Handoff / 交给 AI 编程智能体

```text
Use AI Delivery Spec coding-agent compatibility mode.
Use AI-Coding Full PRD.
Given this PRD and prototype, generate AGENTS.md / CLAUDE.md / Cursor rules,
convert FRR section 16 acceptance into ac_structured YAML, and identify P0/P1 tests.
```

### 5. Review before handoff / 交付前自查

```powershell
python scripts/validate_skill_consistency.py
python scripts/validate_prd_quality.py delivery/prd/main.md
python scripts/validate_coding_agent_contract.py --prd delivery/prd/main.md --prototype delivery/prototype/app.html
```

If the PRD contains phrases like “see prototype / 见原型 / 按现有逻辑”, it must
also provide traceable `view_id`, `region_id`, `data-testid`, `data-action`,
field behavior, and expected domain result.

## Install / 安装

```bash
# Clone
git clone https://github.com/franklinxkk/ai-delivery-spec.git

# Skills CLI
npx skills add franklinxkk/ai-delivery-spec

# Manual install to Claude Code
cp -r ai-delivery-spec ~/.claude/skills/ai-delivery-spec
```

In any AI tool:

```text
Use AI Delivery Spec as the delivery standard.
First run 0D triage: [TIER] [AI] [WORKFLOW].
Load only the relevant entrypoint files.
Produce the requested artifact and end with gates, verification, gaps, and completion state.
```

## Delivery Package Convention / 交付包目录约定

When a PRD/prototype will be consumed by a coding agent or development team,
use this directory structure:

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

Optional triggered reference:

```text
references/coding-agent-compat.md     AC-YAML, AI runtime schema, AGENTS/CLAUDE/Cursor rules
```

Other reference files are load-on-demand source assets. They should not be
loaded unless an entrypoint instructs the agent to use them.

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
| Traditional Product Lifecycle / 古法产品全生命周期 | You need a Tencent-style or enterprise-standard product lifecycle document for human PM/RD/QA review, vendor development, launch, and acceptance | Human-First Full PRD, lifecycle annex, review/sign-off, rollout/readiness, post-launch review |
| AI Native Product Discovery / AI Native 产品探索 | You need to brainstorm an AI-native product, learn from competitors, define agent workflow, prototype, PRD, runtime/eval/fallback | opportunity shaping, AI centrality, AI feature/native contract, prototype, AI PRD |
| AI Coding Delivery / AI 编程交付 | You want to turn competitor screenshots, prototypes, or requirements into a detailed AI-friendly specification so a coding agent can generate the system | AI-Coding Full PRD, locked prototype, `ac_structured`, delivery manifest, AGENTS/CLAUDE/Cursor rules |

Template relationship:

```text
AI-Coding Full PRD
└─ includes Human-First Full PRD
   └─ adds AC-YAML, machine-readable contracts, delivery package, and agent handoff prompts
```

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

## Validation / 校验

```powershell
python scripts/validate_skill_consistency.py
python scripts/validate_routing_scenarios.py
python scripts/validate_ia_skeleton.py --ia-skeleton delivery/ia-skeleton.yaml --prototype delivery/prototype/app.html --prd delivery/prd/main.md
python scripts/validate_coding_agent_contract.py --prd delivery/prd/main.md --prototype delivery/prototype/app.html
```

## License / 许可证

Apache-2.0. See [LICENSE](LICENSE).
