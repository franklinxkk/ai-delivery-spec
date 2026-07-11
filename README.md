# AI Delivery Spec 5.0.0

> **The product-side lifecycle delivery skill.** Turn an idea or customer
> request into one traceable Product Truth, then carry it through PRD,
> prototype, coding handoff, acceptance, change, launch, and learning.
>
> **产品侧全生命周期交付 Skill。**从想法或客户需求出发，建立唯一可追溯的
> Product Truth，贯通 PRD、原型、编码交接、验收、变更、上线与运营学习。

```text
Discover 产品发现 → Specify 需求与业务规格 → Plan/Tasks 工程交接
→ Build/Verify 构建验收 → Launch 上线 → Learn/Retire 学习与退役
```

Use the lightweight path for ToC ideas and quick PRDs. Increase rigor only for
multi-role, workflow, regulated, customer-delivery, or brownfield work.
简单想法走轻量路径；复杂 ToB/ToG、合规、客户交付或存量改造再按风险升级，
不强制每个项目生成整套重型文档。

[![Version](https://img.shields.io/badge/version-5.0.0--development-orange.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)

**Evidence status / 证据状态：** schemas and deterministic checks pass. All
built-in domains are `experimental`; behavioral, expert, customer, and
production evidence remains separately declared.

## Install / 安装

```bash
npx skills add franklinxkk/ai-delivery-spec
```

The open skills CLI can install the same skill for Claude Code, Codex, Cursor,
GitHub Copilot, and other supported agents. To select agents or global scope:

```bash
npx skills add franklinxkk/ai-delivery-spec -g -a claude-code -a codex
```

## Start in 60 seconds / 60 秒开始

Choose one natural-language entry. No repository command is required for first use.

```text
# ToC idea, brainstorming, clarification, or PRD / ToC 想法、脑暴、澄清或 PRD
Use AI Delivery Spec in Light mode. Help me clarify this product idea one
material question at a time, then create the smallest useful PRD: [idea].

# Customer material or prototype / 客户材料或原型
Use AI Delivery Spec. Inventory this material before asking questions. Preserve
existing behavior, expose conflicts and P0 unknowns, then propose the next artifact.

# Approved requirement for coding / 已确认需求进入开发
Use AI Delivery Spec. Build one Product Truth and project Human-First,
coding-agent, and acceptance views without inventing business behavior.
```

See [examples/minimal-v5](examples/minimal-v5/README.md) for a bounded first run.

## Who it helps / 产品交付中的核心价值

| Product-side need / 产品侧需求 | What AI Delivery Spec provides / 它给你什么 |
|---|---|
| Idea, discovery, clarification / 想法、发现与澄清 | One-question-at-a-time convergence, explicit assumptions, scope, and P0 unknowns |
| PRD and product design / PRD 与产品设计 | Roles, flows, pages, actions, states, data, rules, exceptions, and acceptance in one truth |
| Human + coding-agent delivery / 人机协同交付 | Human-First, prototype, Coding Agent, QA, and customer views projected from the same stable IDs |
| Change, launch, and operations / 变更、上线与运营 | Impact, migration, regression, rollout, evidence, learning, and retirement without rewriting unrelated truth |

Use another tool for unrelated syntax debugging or ordinary copy rewriting.
与产品交付无关的语法修复、普通文案改写不属于本 skill。

## One truth, every delivery view / 一份事实，覆盖所有交付视图

```text
Evidence + decisions + unknowns
                 ↓
          Product Truth (stable IDs)
        ↙        ↓        ↓        ↘
Human-First   Prototype   Coding    QA/Customer/Ops
```

- One fact is maintained once / 同一事实只维护一次。
- Every page action has visible and domain results / 每次点击都有界面结果与业务结果。
- Every state change names guard, event, failure, audit, and acceptance / 每次状态变化都有前置、事件、失败、审计和验收。
- Changes update impacted IDs instead of regenerating unrelated documents / 变更只更新受影响 ID，不整篇重写掩盖差异。

## Community fit / 以产品交付为主线的社区互补

AI Delivery Spec owns the committed product-delivery backbone. Use focused
community skills before it for exploration or after it for engineering execution.

| Tool | Best at / 最适合 | How it composes / 与 AI Delivery Spec 的组合 |
|---|---|---|
| **AI Delivery Spec 5.0.0** | Full product-side lifecycle: clarification → Product Truth → PRD/prototype → coding handoff → acceptance/change/operations | **Primary backbone / 主交付内核** |
| [grill-me](https://github.com/mattpocock/skills) | Relentless ambiguity challenge / 对抗式追问 | Optional upstream pressure test before Product Truth |
| [to-prd](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-prd/SKILL.md) | Fast PRD synthesis from current conversation/codebase | Optional lightweight PRD entry; converge committed scope into Product Truth |
| [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | Discovery, strategy, launch, and growth methods | Select methods upstream; carry approved decisions into Product Truth |
| [product-on-purpose/pm-skills](https://github.com/product-on-purpose/pm-skills) | Workshops, templates, and broad PM lifecycle methods | Use for divergence and facilitation; AI Delivery Spec owns delivery convergence |
| [Digidai/product-manager-skills](https://github.com/Digidai/product-manager-skills) | PM pushback, SaaS metrics, roadmap and post-launch learning | Use for decision review and metrics; sync accepted decisions back to Product Truth |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | Spec-driven engineering planning | Downstream implementation planning after product truth is approved |
| [Superpowers](https://github.com/obra/superpowers) | TDD, implementation, review, and branch completion | Downstream engineering execution and verification |

The full 12-project, nine-dimension assessment remains in the
[source-linked report](docs/ecosystem-comparison.md) and
[machine-readable record](evals/ecosystem-comparison.yaml). It records the
user-side execution label **GPT-5.6 SOL** as user-reported; popularity and
platform reach never change capability ratings. The comparison measures
documented coverage, not output quality or a universal winner.

## Generic first, domain-aware when useful / 通用优先、领域按需

No dedicated pack is required. Generic discovery can model roles, objects,
states, workflows, data, risks, and acceptance, then create a project-scoped
Domain Capsule.

没有专属领域包仍可完成需求澄清和交付；系统会先建立项目级 Domain Capsule，
不会因为“行业未内置”而停摆。

| Built-in pack | Current maturity | Evaluation assets |
|---|---|---|
| `traffic` | `experimental` | pinned transport case + domain fixtures |
| `crm` | `experimental` | pinned CRM/customer-service cases + fixtures |
| `education-it` | `experimental` | pinned education case + fixtures |
| `oa` | `experimental` | pinned enterprise-office case + fixtures |
| `medical-hospital-it` | `experimental` | safety/data fixtures; accountable review missing |
| `data-product` | `experimental` | pinned data-product case + fixtures |
| `ai-native` | `experimental` | permission/convergence fixtures; behavioral runs missing |

Coverage truth lives in
[references/domain-coverage.yaml](references/domain-coverage.yaml). Fixture
presence is not behavioral validation. Promotion to `validated` or `audited`
requires the declared evidence and accountable review.

## Core artifacts / 核心产物

| Artifact | Purpose |
|---|---|
| Discovery Contract | Sources, outcome, scope, risks, owners, and P0 unknowns before specification |
| Product Truth | Canonical roles, flows, views, actions, states, data, events, rules, acceptance, and evidence |
| Human-First projection | Scenario-first readable requirements with page/action effects and exceptions |
| Coding Agent projection | Source order, contracts, vertical slices, tests, and forbidden invention |
| Project Domain Capsule | Project-scoped knowledge for an unfamiliar domain |
| Change Package | Impact, compatibility, data migration, regression, rollout, and rollback |
| Context Plan | Risk-adaptive reference loading and ID-based retrieval without silent P0 truncation |
| Execution State | Versioned contract snapshots, micro-gates, access scope, and hash-linked evidence |

## Repository validation commands / 仓库维护与正式交付命令

These commands run inside a cloned skill repository or a delivery workspace
that exposes the scripts; they are not required for the first natural-language use.

```bash
python scripts/ai_delivery_spec_cli.py status --format yaml
python scripts/validate_product_truth.py delivery/truth/product-truth.yaml
python scripts/plan_context.py --truth delivery/truth/product-truth.yaml --config delivery/spec.config.yaml
python scripts/manage_execution_state.py create --discovery-contract discovery.yaml --config delivery/spec.config.yaml --output state.yaml
python scripts/validate_projection_consistency.py --truth delivery/truth/product-truth.yaml --projection delivery/projections/human-first-prd.md
```

Use `py -3` instead of `python` on Windows when needed.

## Examples / 示例

- [Minimal v5](examples/minimal-v5/README.md): first-use bounded discovery.
- [Publishing authorization and learning](examples/publishing-learning-v5/README.md): generic multi-role Product Truth and projections.
- [Generic energy capsule](examples/generic-energy-capsule-v5/README.md): delivery without a dedicated domain pack.
- [Traffic regulatory change](examples/traffic-regulatory-change-v5/README.md): source applicability, impact, rollback, and honest gaps.

## Current evaluation boundary / 当前评测边界

The repository contains 15 pinned GitHub cases across requirement, design, and
coding-delivery cells. Most cells remain `partial` or `not_run`; current evidence
does not prove a general quality, token, rework, or implementation improvement.

Run `python scripts/ai_delivery_spec_cli.py status` for the generated summary.

## Contributing and security / 贡献与安全

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[LICENSE](LICENSE). Domain contributions must include source applicability,
fixtures, honest maturity, and evidence boundaries.
