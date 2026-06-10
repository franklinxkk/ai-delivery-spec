# AI Delivery Spec

AI Delivery Spec 是一套面向产品经理、AI 产品负责人、研发负责人和测试团队的 **AI Native 软件交付协议 / Codex Skill**。

它的目标不是让 PRD 变厚，而是让产品交付物真正可开发、可演示、可测试、可治理。v4.0.1 采用分级交付模型和条件 Gate：先判断项目复杂度，再按需加载移动端、多端一致性、ToB/ToG 审批、多租户/RBAC、报表指标、低代码工作流、AI 嵌入、AI Native Harness、Prompt Ops、效果评估等协议，并补充生产落地所需的防御性契约。

## 适合谁

- 产品经理：输出标准 PRD、用户故事、角色路径、原型验收说明。
- AI 产品负责人：设计 AI 功能、智能体协同、Prompt/Tool/Agent 治理和效果评估。
- 研发负责人：拿到 DDD 开发交接、状态机、命令/查询、领域事件、边界条件。
- 测试/QA：基于 story path、state-button matrix、data-testid、验收 Gate 做自动化和人工验收。
- ToB/ToG 团队：把审批流、多租户、权限、监管、报表、AI 辅助决策做成可落地交付物。

## v4.0.1 核心变化

v4.0 解决了早期版本“全量协议过重”的问题。v4.0.1 在不改变主架构的前提下，补齐企业真实交付中的防御性边界。

| 能力 | 说明 |
|---|---|
| Tiered Delivery Model | L0 探索原型、L1 轻 PRD、L2 标准交付、L3 AI Native / 高风险交付 |
| Core Gate 1-4 | Story-Path、Demo-Closed Prototype、Development Contract、Acceptance Package |
| Conditional Gates | 按需加载移动端、多端、审批、多租户、报表、AI、低代码工作流等协议 |
| AI 分流 | 普通 AI 嵌入走 AI Feature Injection，高风险自主动作走 AI Native Harness |
| ToB/ToG 模式 | 审批流、RBAC、多租户、License、组织树、审计、工单升级 |
| Workflow / Low-Code | 覆盖 n8n、Dify、Flowise 类节点工作流、连接器、凭证、执行历史、回放 |
| Domain Module | 行业知识插件化，换行业优先换 domain module，不改公共协议层 |
| Defensive Hardening | 防止概念过载、测试脏数据、契约演进崩塌、弱网 AI 失效和自动验收误判 |

## v4.0.1 防御性契约

| 风险 | 补充契约 | 文件 |
|---|---|---|
| Prompt / Agent / DAG 过度工程化 | Spec Tiering / Anti-Bloating：普通 CRUD 和线性流程不强制多智能体 DAG | `references/delivery-core.md` |
| 自动验收污染真实数据 | Shadow-Data Isolation：测试 Header、影子库/影子表、事务回滚、指标排除 | `references/prototype-testability.md` |
| API/Schema 演进导致历史 Prompt 测试崩塌 | Contract Version Semantics：声明 API/event/domain/schema 版本依赖和弃用策略 | `references/prompt-registry-integration.md`, `references/prompt-registry.yaml` |
| 移动端/现场弱网导致 AI Runtime 不可用 | Edge-Fallback Gateway：3000ms/5xx 触发 `local_fallback`，100ms 内切本地安全模式 | `references/ai-runtime-ops.md` |
| Browser Agent 被误当最终上线裁判 | Human Overrule：自动验收是 release signal，可审计人工 override，但不能绕过安全/合规/隔离 | `references/delivery-acceptance-gates.md` |

## 解决什么问题

传统产品交付常见问题：

- PRD 有功能名，但没有完整用户故事和角色操作路径。
- 原型看起来完整，但按钮不可点、流程不可演示、状态不可验证。
- 开发拿不到清晰的输入、输出、处理逻辑、状态机和边界规则。
- 测试只能凭感觉验收，无法从需求追溯到原型、状态、接口和用例。
- AI 功能只写“接入大模型”，没有人工确认、失败兜底、回滚、评估和可观测。
- AI Native 场景没有证明上下文、工具、工作流、评估、发布工程是否支撑稳定落地。
- 移动端/小程序只是 PC 缩小版，没有弱网、授权、消息、非打扰和移动端 testid。
- 报表/数据集市只有图表清单，没有指标定义、口径、血缘、模板和验收。
- 低代码/工作流只有画布，没有节点契约、连接器凭证、执行历史和版本发布规则。

AI Delivery Spec 要求每个核心功能至少能映射到：

```text
用户故事 -> 角色路径 -> 原型动作 -> 状态/领域结果 -> 测试用例
```

## 文件结构

```text
ai-delivery-spec/
├── SKILL.md
├── scripts/
│   └── extract_interaction_ledger.py
└── references/
    ├── delivery-tier-model.md
    ├── delivery-core.md
    ├── story-path-verification.md
    ├── prototype-testability.md
    ├── demo-closed-ddd-handoff.md
    ├── delivery-acceptance-gates.md
    ├── mobile-product-delivery.md
    ├── multi-surface-consistency.md
    ├── approval-workflow.md
    ├── saas-multitenancy.md
    ├── reporting-analytics.md
    ├── workflow-automation-lowcode.md
    ├── ai-feature-injection.md
    ├── ai-native-harness-engineering.md
    ├── ai-runtime-ops.md
    ├── ai-effect-evaluation.md
    ├── prompt-registry-integration.md
    ├── prompt-registry.yaml
    ├── build-governance.md
    ├── artifact-packaging.md
    ├── domain-module-template.md
    ├── domain-traffic.md
    ├── domain-traffic-safety-scenarios.md
    ├── domain-crm.md
    ├── skill-version-migration.md
    └── skill-design-benchmark.md
```

## 如何安装到 Codex

```powershell
cd $env:USERPROFILE\.codex\skills
git clone https://github.com/franklinxkk/ai-delivery-spec.git ai-delivery-spec
```

如果本地已经安装过旧版：

```powershell
cd $env:USERPROFILE\.codex\skills\ai-delivery-spec
git pull
```

## 推荐使用方式

### 反向分析已有 HTML 原型

```text
使用 ai-delivery-spec，先对这个 HTML 做 Stage 0：
提取页面、角色、状态、data-action、handler、实体、指标字段、mock data 和未闭合问题。
然后输出 PRD、用户故事矩阵、角色路径矩阵和交互验收报告。
```

### 生成可开发 PRD

```text
使用 ai-delivery-spec，按 L2 标准交付输出：
业务目标、角色、用户故事、状态机、命令/查询、领域事件、输入输出、处理逻辑、异常路径和测试用例。
```

### 设计 AI 功能

```text
使用 ai-delivery-spec，判断这是 AI Feature Injection 还是 AI Native。
如果只是分类/摘要/推荐/审核，输出轻量 AI 契约。
如果 AI 会写业务状态、选择工具、影响客户承诺/合规/金额/安全，升级到 L3 + AI Native Harness。
```

### 设计小程序 / 移动端功能

```text
使用 ai-delivery-spec，加载 mobile-product-delivery 和 multi-surface-consistency：
输出移动端角色路径、授权门禁、弱网策略、订阅消息、非打扰规则、移动端 testid 和验收用例。
```

### 设计低代码 / 工作流 / AI 中台

```text
使用 ai-delivery-spec，加载 workflow-automation-lowcode：
定义 Workflow、Node、Edge、Trigger、Connector、Credential、Execution、Template、Environment，
并补充节点输入输出、凭证安全、执行历史、重试、回放、版本发布和权限边界。
```

## 领域模块

公共协议层尽量保持领域中立。

当前仓库包含两个示例领域模块：

- `references/domain-traffic.md`：交通安全 / 运输监管领域。
- `references/domain-crm.md`：CRM / 客服 / 销售 SaaS 领域验证样例。

如果换行业，优先按 `references/domain-module-template.md` 创建新的 domain module。公共协议层不要混入行业专有知识。

## GitHub 仓库建议

Description:

```text
AI-native product delivery protocol for PRD, prototypes, user stories, DDD handoff, mobile delivery, ToB/ToG workflows, low-code automation, AI agent governance, prompt ops, observability, and testable product-engineering collaboration.
```

Topics:

```text
ai-product, product-management, prd, prototype, ddd, ai-agent, ai-native, low-code, workflow-automation, tob, tog, rbac, codex-skill
```

## License

目前未声明开源许可证。对外公开使用前建议补充 LICENSE。
