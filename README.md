# AI Delivery Spec

> The world's first **product-side Spec-Driven Development** framework for AI-native teams.
> 从需求到上线，一套可读、可开发、可测试、可运营的产研交付规格。

**AI Delivery Spec / AI 产研交付规格** is a tool-agnostic delivery standard
for product managers, AI product leads, engineering teams, and QA teams.
It works with ChatGPT, Claude, Gemini, Codex, Cursor, Copilot, OpenClaw,
and any AI tool that can read Markdown.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/version-4.5.2-green.svg)]()
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-purple.svg)](https://openclaw.ai)

---

## Why This Exists / 为什么存在

AI coding agents write code fast, but **product delivery is still chaos**:
PRD missing acceptance criteria, prototypes not testable, dev handoff ambiguous,
AI features without runtime governance.

AI 编程智能体写代码很快，但**产品交付仍然是混乱的**：
PRD 缺验收标准、原型不可测试、交接模糊、AI 功能无运行时治理。

**AI Delivery Spec** gives your team a shared delivery protocol — not templates,
but a routing-driven runtime that loads only what each artifact needs.

## What Makes It Different / 核心差异

| Feature | ai-delivery-spec | Other PM Skills | spec-kit |
|---------|:---:|:---:|:---:|
| L0-L3 delivery tiers (scale-adaptive) | ✅ | ❌ | ❌ |
| Replaceable domain modules | ✅ | ❌ | ❌ |
| Prototype testability rules | ✅ | ❌ | ❌ |
| 0D triage routing (TIER×AI×WORKFLOW) | ✅ | ❌ | ❌ |
| FRR 16-section delivery record | ✅ | ❌ | ❌ |
| Product-side spec (PRD + prototype) | ✅ | Partial | ❌ |
| Dev-side spec (code generation) | ❌ | ❌ | ✅ |

> 💡 **Complementary with [github/spec-kit](https://github.com/github/spec-kit)**:
> spec-kit handles spec→code, ai-delivery-spec handles requirement→spec+prototype.

## v4.5.2 Focus

- Human-readable PRDs for product, frontend, backend, algorithm, and QA teams.
- Embedded engineering contracts for AI-assisted development.
- Replaceable domain modules for CRM, traffic safety, and education IT.
- A single lifecycle bridge:
  `Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire`.

## Quick Start / 快速开始

### Install

```bash
# Option 1: Clone
git clone https://github.com/franklinxkk/ai-delivery-spec.git

# Option 2: Use with OpenClaw / Claude Code
# Point your agent to this repo and ask it to follow SKILL.md routing rules
```

### Use in Any AI Tool

```
Use AI Delivery Spec as the delivery standard.
First run 0D triage: [TIER] [AI] [WORKFLOW].
Load only the relevant entrypoint files.
Produce the requested artifact and end with gates, verification, gaps, and completion state.
```

## Examples / 示例

Start with a real-world scenario:

- [CRM Response Center](examples/crm-response-center/README.md) — lead,
  opportunity, customer service, product feedback, contract/payment.
- [Traffic Safety SaaS](examples/traffic-safety-saas/README.md) — regulated
  ToB/ToG workflows, mobile inspection, notices, hidden-danger remediation.
- [Higher-Education IT](examples/education-it/README.md) — academic affairs,
  student affairs, teaching systems, smart classrooms, AI learning assistants.

See [examples/README.md](examples/README.md) for the full example index.

### Try It Now / 立即试用

```
# Lightweight PRD
Use AI Delivery Spec, TIER=L0, WORKFLOW=prd.
Write a PRD for [your feature].

# Full delivery with prototype
Use AI Delivery Spec, TIER=L2, WORKFLOW=prototype.
Build an interactive HTML prototype for [your product].

# AI Native feature with runtime governance
Use AI Delivery Spec, TIER=L1, AI=native.
Spec an AI feature with runtime governance for [your scenario].
```

## Delivery Tiers / 交付层级

| Tier | Scope | Typical Artifacts | When to Use |
|------|-------|-------------------|-------------|
| **L0 Lite** | POC / validation | Simplified PRD + wireframe | Quick concept validation |
| **L1 Standard** | Standard project | Full PRD + interactive prototype + FRR | Regular feature delivery |
| **L2 Full** | Complex project | Full PRD + hi-fi prototype + complete FRR + acceptance matrix | Multi-stakeholder delivery |
| **L3 Enterprise** | Enterprise grade | Full suite + governance + multi-domain modules | Procurement / regulatory |

## Domain Modules / 可替换领域模块

| Domain | File | Scope |
|--------|------|-------|
| Traffic Safety / 交通安全 | `references/domain-traffic.md` | Regulated enterprise, vehicle, personnel, training |
| CRM / 客户经营 | `references/domain-crm.md` | Lead, opportunity, customer 360, ticket, contract |
| Higher-Education Informationization / 高校教育信息化 | `references/domain-education-it.md` | Academic affairs, student affairs, smart classroom |

> Adding a new industry? Copy `references/domain-module-template.md` and customize.

## Architecture / 运行架构

Only 4 entrypoints, loaded on demand:

Default runtime has only four entrypoints.

```
SKILL.md ─────────────────────── triage, routing, gates
references/delivery-core.md ───── PRD, stories, DDD/API/data, lifecycle
references/prototype-testability.md ── prototype, mobile, interaction
references/advanced-extensions.md ── AI, SaaS, approval, reporting, global
```

Other reference files are detail libraries, loaded by trigger conditions only.
This keeps context size small — your AI tool reads only what it needs.

其他 reference 文件是高级场景的明细库，按触发条件加载，避免大模型一次性吞下过多上下文。

## Core Gates / 核心门闸

| Gate | Purpose |
|------|---------|
| Gate 1: Story-Path | user story → role path → visible result → domain result → test |
| Gate 2: Demo-Closed Prototype | every primary action has visible/domain outcome |
| Gate 3: PRD + Dev Contract | PRD is primary; engineering contract embedded & traceable |
| Gate 4: Acceptance Package | deliver only in-scope artifacts with verification |

## Lifecycle Bridge / 生命周期桥接

Use only the stages needed by the requested artifact:

```
Discover → Specify → Plan → Tasks → Build/Verify → Launch → Learn/Retire
```

## Validation / 校验

```powershell
py scripts/validate_skill_consistency.py
py scripts/validate_routing_scenarios.py
py scripts/validate_prd_quality.py path\to\prd.docx --manifest path\to\manifest.json
```

## Compatibility / 兼容性

Works with: **Claude Code** • **Claude Desktop** • **ChatGPT** • **Gemini** • **Codex** • **Cursor** • **Copilot** • **OpenClaw** • Any AI tool that can read Markdown

## What It Is Not / 不适用场景

- Pure code syntax debugging
- Copy rewriting
- Loose brainstorming with no delivery intent

## License

[Apache-2.0](LICENSE) — use freely in commercial projects.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome! 🎉

## Launch / Community

- [Changelog](CHANGELOG.md)
- [Social launch kit](docs/social-launch-kit.md)
- [Awesome submission targets](docs/awesome-submission-targets.md)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=franklinxkk/ai-delivery-spec&type=Date)](https://star-history.com/#franklinxkk/ai-delivery-spec&Date)
