# AI Delivery Spec

AI Delivery Spec 是一套面向产品经理、AI 产品负责人、研发负责人和测试团队的 **AI Native 软件交付协议 / Codex Skill**。

它把 PRD、交互原型、用户故事、角色路径、DDD 研发交接、AI Native Harness 工程化验证、AI Agent 运行治理、Prompt/Tool 管理、可观测性和测试验收统一成一套可执行标准，帮助产研团队从“写需求文档”升级到“交付可开发、可测试、可演示、可治理、可稳定落地的产品规格”。

## 适合谁用

- 产品经理：输出更标准的 PRD、用户故事、角色操作路径、原型验收说明。
- AI 产品负责人：设计 AI 功能、智能体协同、Prompt/Tool/Agent 治理和评估体系。
- 研发负责人：拿到更清晰的 DDD 研发交接、状态机、API/命令查询契约和边界条件。
- 测试/QA：基于用户故事、角色路径、状态按钮矩阵和 data-testid 进行自动化验收。
- ToB/ToG 团队：把复杂业务、审批流、监管合规、数据报表、AI 辅助决策做成可落地交付物。

## 解决什么问题

传统产品交付常见问题：

- PRD 写了很多功能名，但没有完整用户故事和角色路径。
- 原型看起来完整，但按钮不可点、核心流程无法演示。
- AI 功能只写“接入大模型”，没有失败兜底、人工确认、可观测性和回滚机制。
- AI Native 场景目标看起来成立，但没有证明上下文、工具、工作流、评估、发布工程是否支撑稳定落地。
- 开发拿不到清晰的业务对象、状态机、输入输出、领域事件和测试用例。
- 测试只能凭感觉验收，无法从需求追溯到原型、状态、接口和用例。

AI Delivery Spec 强制把每个核心功能映射到：

- 用户故事
- 角色操作路径
- 原型演示路径
- 状态变化
- DDD 业务对象
- 测试用例
- AI 运行与治理契约
- AI Native Harness 工程化验证

## 核心能力

### 1. PRD 与研发交接

- Stage 0 反向解析已有 HTML/原型/旧系统。
- Stage 1-5 从机会、调研、方案、用户故事、状态机到 PRD/原型交付。
- DDD Handoff PRD：输出 bounded context、aggregate、entity/value object、domain event、command/query、invariant、state machine、sequence diagram、API contract、feature test cases。

### 2. 可演示原型验收

- Customer-demoable prototype gate。
- 每个核心故事必须能在无后端情况下通过 mock data 演示。
- 核心动作不能只 toast：创建、查看、编辑、提交、审核、启用、停用、导出、分析必须产生真实可见结果。
- 原型迭代必须保留上一版页面、动作、弹窗、状态、数据覆盖和关键路径，除非明确 de-scope。

### 3. 用户故事与角色路径

- User Story Inventory。
- Role Operation Path Matrix。
- Story -> Prototype `data-testid` / `data-action` -> Test Case 的可追溯链路。
- 每个角色至少有 happy path 和 exception/permission path。

### 4. AI Native Harness 工程化验证

- 场景和目标确定后，先验证工程化承载能力，再进入 runtime 开发。
- 多智能体可行性评审：Sponsor、Domain Workflow、AI Architect、Backend Integration、Data/RAG、QA/Eval、Ops/SRE。
- Harness 六层：context、tool/API、workflow、evaluation、observability、release。
- 模拟业务逻辑路径和工程路径：trigger -> context -> agent -> tool -> human gate -> write -> trace -> evaluation。
- 支持 fixture replay、dry-run、shadow、canary、failure injection。

### 5. AI Agent 治理

- Agent runtime contract。
- Prompt/Agent Registry。
- Tool Registry。
- Trace Log。
- Fallback、human gate、write_scope、precondition、rollback。
- AI 变更必须声明 impact_surface、linked_test_cases、rollback_owner、observability_signal。

### 6. 测试与验收

- Story-Path Verification Gate。
- State-Button Matrix Gate。
- Delivery Acceptance Gate。
- Complexity Budget：PRD、states、actions、APIs、tools、agents 均需计数。
- SIM Review：Sponsor、End User、Peer PM、Dev Lead 多视角评审。

## 文件结构

```text
ai-delivery-spec/
├── SKILL.md
└── references/
    ├── delivery-core.md
    ├── prototype-testability.md
    ├── demo-closed-ddd-handoff.md
    ├── delivery-acceptance-gates.md
    ├── story-path-verification.md
    ├── ai-native-harness-engineering.md
    ├── ai-runtime-ops.md
    ├── prompt-registry.yaml
    ├── domain-traffic.md
    └── domain-traffic-safety-scenarios.md
```

## 如何安装到 Codex

将仓库克隆到 Codex skills 目录：

```powershell
cd $env:USERPROFILE\.codex\skills
git clone https://github.com/franklinxkk/ai-delivery-spec.git ai-delivery-spec
```

安装后，在 Codex 中提出 PRD、原型、AI Agent、DDD 交付、用户故事、角色路径、测试验收等任务时，会触发该 skill。

## 推荐使用方式

### 反向分析已有 HTML 原型

```text
使用 ai-delivery-spec，先对这个 HTML 做 Stage 0：
提取页面、角色、状态、数据动作、handler、实体、指标字段、mock data 和未闭合问题。
然后输出 PRD、用户故事矩阵、角色路径矩阵和交互验收报告。
```

### 生成可开发 PRD

```text
使用 ai-delivery-spec，按 DDD Handoff PRD 标准输出：
业务目标、角色、用户故事、状态机、命令/查询、领域事件、输入输出、处理逻辑、异常路径、测试用例。
```

### 设计 AI 智能体功能

```text
使用 ai-delivery-spec，设计一个 AI Agent 功能：
必须包含 runtime contract、prompt registry、tool policy、trace log、fallback、human gate、evaluation cases 和 observability。
```

### 评审 AI Native 场景工程可行性

```text
使用 ai-delivery-spec，对这个 AI Native 场景做 harness engineering review：
先输出 AI Native scenario card，然后让 Sponsor、Domain Workflow、AI Architect、Backend Integration、Data/RAG、QA/Eval、Ops/SRE 多视角评审。
必须模拟业务逻辑路径和工程路径，判断 context、tool/API、workflow、evaluation、observability、release harness 是否支撑稳定落地。
```

### 审查原型交互完整度

```text
使用 ai-delivery-spec，对比旧版和新版 HTML 原型：
输出 interaction ledger、页面/动作/弹窗/handler/mock data 差异、缺失路径和修复建议。
```

## 领域模块说明

协议层尽量保持领域中立。

当前仓库默认带有交通安全 / 运输监管领域模块：

- `references/domain-traffic.md`
- `references/domain-traffic-safety-scenarios.md`

如果你换到其他行业，只需要替换领域模块，公共协议层可以继续复用。一个合格的 domain module 应包含：

- 领域实体
- 指标体系
- 核心工作流
- 业务场景
- UI 模式
- 政策/合规约束
- 验收清单

## 推荐 GitHub 仓库信息

Description：

```text
AI-native product delivery protocol for PRD, prototypes, user stories, DDD handoff, AI agent governance, prompt ops, observability, and testable product-engineering collaboration.
```

Website：

```text
https://github.com/franklinxkk/ai-delivery-spec
```

Topics：

```text
ai-product-management
prd
product-requirements
product-management
ai-agent
ai-native
prompt-engineering
ddd
software-delivery
prototype
testability
product-engineering
codex-skill
agent-governance
observability
```

## 版本

当前版本：`v3.8 Harness-Engineering Verified`

v3.8 重点增强：

- AI Native Harness Engineering Gate
- Multi-Agent Feasibility Review
- Engineering Path Simulation
- Story-Path Verification Gate
- Demo-Closed Prototype Gate
- DDD Handoff PRD Gate
- State-Button Matrix Gate
- No Toast-Only Core Action Gate
- Delivery Acceptance Gate

## 作者

李康（Li Kang）
