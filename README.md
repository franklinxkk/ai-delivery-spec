# AI Delivery Spec

AI Delivery Spec 是一套面向产品经理、AI 产品负责人、研发负责人和测试团队的 **AI Native 软件交付协议 / Codex Skill**。

它的目标不是让 PRD 变厚，而是让产品全生命周期的单一交付物或完整交付包都能被准确触发、独立评审、正确路由并在明确边界停止。v4.1.0 将覆盖范围从“需求到上线”扩展到“发现、定义、设计、工程、验证、发布、运营学习和退役”。

## 适合谁

- 产品经理：输出标准 PRD、用户故事、角色路径、原型验收说明。
- AI 产品负责人：设计 AI 功能、智能体协同、Prompt/Tool/Agent 治理和效果评估。
- 研发负责人：拿到 DDD 开发交接、状态机、命令/查询、领域事件、边界条件。
- 测试/QA：基于 story path、state-button matrix、data-testid、验收 Gate 做自动化和人工验收。
- ToB/ToG 团队：把审批流、多租户、权限、监管、报表、AI 辅助决策做成可落地交付物。

## v4.1.0 核心变化

v4.0-v4.0.8 依次解决分级交付、防御性边界、模板、战略交接、精准触发、范围一致性、场景回归和全球化准备。v4.1.0 不新增公共 Gate，而是统一产品生命周期入口，使每个阶段的交付物可以单独进入评审，且不会因为缺少相邻阶段材料被误判失败。

| 能力 | 说明 |
|---|---|
| Lifecycle Artifact Review | 调研、PRD、设计、技术契约、测试/UAT、发布、上线后复盘和退役材料均可独立进入评审 |
| Artifact-Type Routing | 主路由由交付物类型决定；Mode、Tier、AI centrality 和条件插件保持正交 |
| Lifecycle Tier Rule | 战略、上线后和退役材料继承产品 Tier；未知时使用 `N/A (lifecycle governance)`，不强塞入 L0-L3 |
| Post-Launch Evidence | 评审指标口径、基线、对照、护栏、事故学习和后续决策，不把上线等同于成功 |
| Retirement Readiness | 覆盖依赖盘点、客户迁移、数据导出删除、兼容窗口、通知、支持终止和关闭证据 |
| Artifact Scope | 单一产物、模块包、完整交付包分开，缺失包件只报告不自动生成 |
| Ordered Routing | 先选一个主输出路由，再叠加输入修饰和全部匹配插件，消除三套路由重复 |
| Intent Evidence | 用开发、测试、投标、客户演示、正式验收、上线等当前可见信号选择 Mode，不猜测未来用途 |
| Conflict Precedence | Mode 信号冲突时按 Full > Standard > Lite；Mode 不自动扩大产物范围 |
| Trigger Boundary | HTML 原型交付会触发；纯语法、无交付意图的代码实现不会触发 |
| Scenario Regression | 45 个场景覆盖 8 类真实项目、9 个跨行业组合、8 个全球化场景、12 个生命周期产物和 8 个触发边界 |
| Evolution Governance | 新公共 Gate 需至少 3 个真实项目、2 个领域共同证明，避免被碎片建议持续膨胀 |
| Global/Regional Profile | 目标市场、跨境数据、区域模型路由、多语言评测、RTL、应用商店、支付和区域运营 |
| Global Scenario Regression | 新增欧盟、中东、东南亚、美国、日本和多国家 SaaS/AI Native 场景 |
| Execution Modes | Lite 单一产物/快速验证、Standard 常规交付、Full 完整包/正式验收/上线准备 |
| Stop Conditions | 使用 PASS / REVIEW_COMPLETE_WITH_GAPS / BLOCKED 明确终止，不把失败包装成通过 |
| Tiered Delivery Model | L0 探索原型、L1 轻 PRD、L2 标准交付、L3 AI Native / 高风险交付 |
| Core Gate 1-4 | Story-Path、Demo-Closed Prototype、Development Contract、Acceptance Package |
| Conditional Gates | 按需加载移动端、多端、审批、多租户、报表、AI、低代码工作流等协议 |
| AI 分流 | 按模块判断 AI-core、AI-supporting、AI-incidental，混合产品不再整体误升 L3 |
| Dual State Coordination | AI 状态与业务状态分开建模，通过版本快照和命令 Guard 协调 |
| Executable SIM Review | Persona 按可见线索逐步操作，卡点必须落到具体步骤和证据 |
| Complexity Counting | 明确业务状态、UI 状态、跨端动作、API 与 Agent 的计数边界 |
| ToB/ToG 模式 | 审批流、RBAC、多租户、License、组织树、审计、工单升级 |
| Workflow / Low-Code | 覆盖 n8n、Dify、Flowise 类节点工作流、连接器、凭证、执行历史、回放 |
| Domain Module | 行业知识插件化，换行业优先换 domain module，不改公共协议层 |
| Defensive Hardening | 防止概念过载、测试脏数据、契约演进崩塌、弱网 AI 失效和自动验收误判 |
| Practical Adoption | Apache-2.0、模板目录、golden cases 分级、Gate 2 多形态验收、System Readiness |
| Strategy Handoff | 条件式接收 TAM/SAM/SOM、竞品、定位和验证结论，不吞并完整产品战略方法论 |

## v4.0.3 战略发现交接

`Strategic Discovery Handoff Gate` 只在以下情况触发：

- 新产品、新业务线、新行业、新区域或新客户群；
- 重大投资、年度规划、董事会、融资或商业化决策；
- 产品重新定位、改变主要买方或品类；
- 战略级 build / buy / partner 决策。

交接内容包括机会证据、目标客群、按需的 TAM/SAM/SOM、竞品与替代方案、差异化定位、战略选择、验证计划和建议交付 Tier。

普通 CRUD、字段、报表、权限、bug 和流程优化默认不触发，不要求重复填写市场规模和定位。

详见 `references/strategy-discovery-handoff.md`。

## v4.0.2 采用增强

| 增强 | 目的 | 文件 |
|---|---|---|
| Apache-2.0 License | 允许社区和团队复用、修改、分发 | `LICENSE` |
| PRD Templates | 初级 PM 不从空白文档开始写 | `references/templates/` |
| Golden Case Tiering | Prompt Ops 可以先跑低成本 P0 smoke，再按风险升级 P1/P2 | `references/prompt-registry.yaml` |
| Gate 2 Surface Branches | PC/H5/小程序/Native App/API/工作流画布按各自形态验收 | `references/delivery-acceptance-gates.md` |
| System Readiness Gate | 区分 PRD/原型验收和真实上线就绪 | `references/system-readiness-checklist.md` |

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
    ├── strategy-discovery-handoff.md
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
    ├── system-readiness-checklist.md
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
    ├── skill-design-benchmark.md
    └── templates/
        ├── prd-light-template.md
        ├── prd-standard-template.md
        ├── ai-native-prd-template.md
        └── system-readiness-checklist-template.md
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

### 新产品 / 新市场进入交付前

```text
使用 ai-delivery-spec 的 Strategic Discovery Handoff Gate，
整理机会证据、目标客群、按需的 TAM/SAM/SOM、竞品替代方案、差异化定位、
关键假设和验证计划，并给出 GO / GO_WITH_ASSUMPTIONS / VALIDATE_FIRST / NO_GO 结论。
结论通过后再进入 Stage 1 和 L1/L2/L3 交付。
```

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

Apache License 2.0. See [LICENSE](LICENSE).
