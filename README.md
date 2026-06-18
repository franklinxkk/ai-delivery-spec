# AI Delivery Spec / AI 产研交付规格

AI Delivery Spec is a tool-agnostic product-engineering delivery standard for
AI assistants and human teams. It can be used with ChatGPT, Claude, Gemini,
Copilot, Cursor, Codex, or any agent/workflow system that can read Markdown
instructions and reference files.

AI Delivery Spec 是一套面向真实产研协作的交付规范，不绑定任何单一 AI
工具。它的目标不是把文档写厚，而是让 PRD、原型、开发契约、验收证据和上线
准备变得可读、可开发、可测试、可运营。

## What It Is / 它解决什么

Use it when a product artifact will guide development, QA, customer demo,
procurement, release, migration, AI runtime governance, or acceptance.

适用场景：

- PRD / 产品规格书 / 需求评审
- 可交互 HTML 原型 / 小程序 / App / PC 多端原型
- 用户故事、角色路径、状态机、按钮矩阵
- DDD / API / 数据 / 字段字典 / 指标口径交接
- 测试用例、UAT、验收证据、上线 readiness
- AI Native、AI 功能注入、智能体运行时、评测、Prompt Ops
- SaaS 多租户、RBAC、审批流、低代码工作流、数据报表/报告
- 出海、多语言、区域合规、跨境数据场景

Do not use it for pure code syntax debugging, copy rewriting, or loose
brainstorming with no delivery intent.

## v4.5.2 Focus

v4.5.2 keeps the v4.5 lifecycle bridge, preserves the v4.5.1 PRD
runtime/template consistency fix, and adds a new replaceable domain module for
Higher-Education Informationization:

- the runtime FRR summary now has the same 16 sections as the standard PRD
  template;
- `Function-Level NFR` is separated from dependencies, while upstream/downstream
  dependencies stay in `Notifications, Audit, And Dependencies`;
- PRD readability explicitly covers Sponsor/PM, UX/UI, Frontend, Backend,
  Algorithm/AI, and QA readers from one source of truth;
- public PRD-writing references are treated as readability guidance, not copied
  wholesale into the runtime;
- `references/domain-education-it.md` supports digital campus, academic affairs,
  student affairs, teaching quality, smart classroom, one-stop service, data
  governance, and campus AI assistant scenarios.

v4.5.2 在保留 v4.5.1 PRD 运行时一致性修复的基础上，新增高校教育信息化领域模块。
PRD 仍然是单一权威文档，工程契约嵌入其中，用来让前端、后端、算法和测试都能直接找到
自己的实现与验收依据。

## Domain Modules / 可替换领域模块

Domain knowledge lives in replaceable modules. The public protocol stays
domain-neutral.

领域知识放在可替换的 domain 模块里，公共交付协议保持领域无关。

| Domain | File | Typical Scope |
|---|---|---|
| Traffic Safety / 交通安全与运管监管 | `references/domain-traffic.md` | regulated enterprise, vehicle, personnel, inspection, hidden danger, training, report |
| CRM / 客户经营响应 | `references/domain-crm.md` | lead, opportunity, customer 360, ticket, demand, contract/payment, partner response |
| Higher-Education Informationization / 高校教育信息化 | `references/domain-education-it.md` | academic affairs, student affairs, teaching quality, smart classroom, one-stop service, data governance, campus AI assistant |

When changing company or industry, replace or add a `domain-*.md` module first.
Only change the public protocol when the delivery behavior itself must change.

换公司或行业时，优先替换或新增 `domain-*.md`。只有交付行为本身需要变化时，才修改公共协议。

## Runtime Architecture / 运行架构

Default runtime has only four entrypoints:

| Entrypoint | When To Read |
|---|---|
| `SKILL.md` | triage, mode/tier, routing, gates |
| `references/delivery-core.md` | PRD, requirement, story, state, DDD/API/data, lifecycle/task bridge |
| `references/prototype-testability.md` | executable prototype, mobile/H5/mini-program/app interaction |
| `references/advanced-extensions.md` | AI, SaaS, approval, reporting, low-code, global, readiness, domain extensions |

默认只读这 4 个入口。其他 reference 是高级场景的明细库，按触发条件加载，避免
大模型一次性吞下过多上下文。

## Core Gates / 核心门闸

| Gate | Purpose |
|---|---|
| Gate 1 Story-Path | user story -> role path -> visible result -> domain result -> test |
| Gate 2 Demo-Closed Prototype | every primary action has visible/domain outcome |
| Gate 3 Product Specification + Development Contract | traditional PRD remains primary; engineering contract is embedded and traceable |
| Gate 4 Acceptance Package | deliver only in-scope artifacts with verification, gaps, and risks |

## PRD Readiness / 什么样的 PRD 可交付开发

For development handoff, every in-scope release function needs a complete
Functional Requirement Record:

- business scenario and role path;
- entry, preconditions, page regions, visible states;
- fields, dictionaries, validation, editability, masking;
- numbered user-system interaction flow;
- actions, visible result, domain result, idempotency;
- business rules, formulas, calibers, state guards;
- permission and tenant/data scope;
- exceptions, recovery, notification, audit;
- data/AI/algorithm contract when applicable;
- frontend/backend/QA notes and acceptance cases.

工程契约不是替代 PRD，而是嵌入 PRD 的可追溯层。DDD、API、事件、命令、指标、
测试和任务拆解都必须能回溯到功能记录和验收用例。

## Lifecycle Bridge / 生命周期桥接

Use only the stages needed by the requested artifact:

```text
Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire
```

- `Discover`: opportunity, customer/job, evidence, assumptions.
- `Specify`: product truth, complete FRRs, acceptance.
- `Plan`: implementation assumptions, dependencies, risk controls.
- `Tasks`: vertical slices tied to FRR + AC IDs.
- `Build/Verify`: prototype/test evidence and defect closure.
- `Launch`: readiness, rollout, rollback, notice.
- `Learn/Retire`: post-launch review, migration, deprecation, data closure.

## Using With Any AI Tool / 在任意 AI 工具中使用

Recommended prompt:

```text
Use AI Delivery Spec as the delivery standard.
First run 0D triage: [TIER] [AI] [WORKFLOW].
Load only the relevant entrypoint files.
Produce the requested artifact and end with gates, verification, gaps, and completion state.
```

If the tool supports uploaded files, upload `SKILL.md` plus only the relevant
entrypoint file. If it supports repositories, point it to this repo and ask it
to follow the runtime routing rules.

## Validation / 校验

Before publishing changes:

```powershell
py -3 scripts/validate_skill_consistency.py
py -3 scripts/validate_routing_scenarios.py
py -3 scripts/validate_prd_quality.py path\to\prd.docx --manifest path\to\manifest.json
```

## License

Apache-2.0.
