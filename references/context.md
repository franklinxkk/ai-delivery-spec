# 上下文、组合与 Agent 交接 / Context, Composition And Agent Handoff

任务极小、多模块、强监管、存量改造或接近上下文上限时加载。上下文是注意力预算，不是资料仓库；
Agent 工作包只投影同一需求基线，不能形成新的业务权威。

## 两类不同预算 / Two Different Budgets

仓库预算保证 Skill 可维护，运行时预算决定某个任务加载什么。`SKILL.md` 130行和阶段参考500行
不是模型 Token 上限。加载大型领域包或 Product Truth 前，使用
`schemas/context-plan.schema.json` 和 `scripts/plan_context.py` 生成 Context Plan。

## 分类信号 / Classification Signals

优先使用结构化证据，而非关键词：需求阶段、交付形态、保证强度、项目形态；模块/角色/流程/
动作/状态/集成/P0 AC 数量；监管来源和治理档案；受限字段、多租户、金钱/安全/隐私后果；
AI写回、历史兼容、并存、补偿、恢复；开放 P0 未知项或冲突。

关键词只能提示需要发现的问题，不能自行证明监管属性、选择领域包或提高领域成熟度。

## 运行时档案 / Runtime Profiles

| 档案 | 默认行为 |
|---|---|
| minimal | 核心 Skill + 0或1个阶段参考；无必要不加载领域包 |
| standard | 1—2个阶段参考和1个匹配领域包 |
| regulated | 相关阶段、权威来源、具理由的领域包和 Human Gate |
| large_program | 按模块/流程/变更分片，检索切片而非整图加载 |

档案是运行建议，不代表可以扩大模型上下文。

## 超限规则 / Overflow Rules

1. 先预留系统和输出 Token；
2. 不得静默截断 P0规则、监管断言、权限、状态转换、失败行为、验收、兼容或恢复；
3. 用 `scripts/query_product_truth.py` 按稳定 ID/模块查询；
4. 参考/领域限制是批次限制，需要的包应记录并后续检索，不能从范围消失；
5. 安全完整切片仍放不下时，拆交付或因缺证据返回 BLOCKED；
6. 摘要只用于导航，不能代替权威来源或 Product Truth 对象；
7. 到 `warn_at_ratio`（建议70%）时明确选择：检索 ID切片、写 compaction manifest、拆交付或阻断；
8. 不生成巨型 Product Truth。每次写一个 `truth/fragments/MOD-*.yaml`，校验、保存检查点后再编译；
   完整 AI Coding PRD 同样按章节切片，合同索引闭合后再组装。

compaction manifest 必须列出保留优先级和延期 ID，不能借压缩静默丢行为。

## 澄清后的快速通道 / Fast Lane After Clarification

来源优先级、范围和 P0 决策已批准时，不重启发现或重写摘要。冻结合同索引，只加载当前模块/
流程 ID，写对应 Truth/PRD 切片，局部校验、保存检查点后继续。这是大型完整 PRD 的默认路径。
项目覆盖写入可选且版本化的 `spec.config.yaml`，并用 schema 校验。

## 复杂度不等于成熟度 / Complexity Is Not Maturity

上下文/保证档案描述当前项目，领域成熟度描述可复用领域包的证据。自动分类可以选择更强门禁，
但绝不能把 knowledge-backed/contract-tested 自动晋升为 behavioral、expert-reviewed 或 audited。

## 检查点与微门禁 / Checkpoint And Micro-Gate Protocol

长任务、恢复、监管、审计或正式验收使用检查点，防止会话上下文丢失已批准决定；检查点不管理
Sprint、代码、发布或运营。

- 每个需求阶段前载入最近已验证检查点；
- 尚无规格时使用 Discovery Contract；
- 编辑工作合同并生成新快照，快照本身不可修改；
- hash 链只能检测本地变化，不能替代要求更高的外部签署。

```powershell
py -3 scripts/manage_execution_state.py create --truth product-truth.yaml --config spec.config.yaml --installed-skill C:/path/to/ai-delivery-spec/SKILL.md --execution-id EXEC-PROJECT-001 --output evidence/state-000.yaml
py -3 scripts/manage_execution_state.py verify --state evidence/state-000.yaml
py -3 scripts/manage_execution_state.py gate --state evidence/state-000.yaml --gate-id contract_traceability --projection requirements/PRD.md --output gate-contract.yaml
```

有效门禁覆盖版本/环境、复杂度/领域证据、上下文存续、发现就绪、合同追溯、审计访问和回退风险。
必要门禁通过后每次只推进一个需求阶段，并保留上一检查点；中断后只从 hash/锚点仍有效的状态恢复。

高风险失败必须 BLOCKED。已声明的验证器中断只有在配置允许的低风险策略下，才能形成显式人工
评审缺口，永远不能静默 PASS。链接缺失、门禁过期、范围降级或版本漂移阻断受影响基线。

## 组合与横切责任 / Composition And Cross-Cutting Ownership

只组合真实触发的能力、治理和领域知识。“审批、AI、客户、报表”等通用词本身不能选择 OA、
AI-native、CRM 或 data-product。两个领域包共享对象、状态、事件、权限、规则、指标或失败路径时，
登记 canonical owner、映射、生产者/消费者、优先级、重试/补偿和对账。领域包可收紧权限，
不能扩张所属业务域的权威。

## 智能大项目分轮 / Smart Large-Project Rounds

超过8个输入、50万可解析字符，或盘点发现至少8模块、12页面、200稳定对象时自动分轮。
Round 0 建立来源/权威清单；后续按端到端角色纵切，通常每轮最多3个大型来源、2个模块、40个
主要 ID。每轮保存持久检查点，最后执行一次跨模块门禁。

禁止按前端/后端横切、单轮重建巨型 Product Truth，或把中间分轮包装成最终完成。

## Agent 交接投影 / Agent Handoff Projection

长时间 AI Coding 只按 `schemas/agent-handoff.schema.json` 生成已触发工作包：

- 根 `AGENTS.md`：权威、稳定全局守卫、路由、命令和变更协议；引用 PRD而不复制所有规则；
- `MOD-*`：一个可独立负责的模块纵切，含输入输出、直接依赖、AC和 `qa_projection`；
- `XCT-*`：影响至少两个模块的 RBAC、多租户、审计、血缘、AI运行时或其他横切规则；
- `EDGE-*`：生产者/消费者对象或状态交接、映射、重试、对账和AC；
- `HANDOFF-*`：发送/接收双方、已确认基线和返回问题/提案。

所有活动工作包绑定同一 baseline version/hash、责任人、范围和 AC。`ready_for_implementation`
还必须引用工程团队维护的 `engineering_baseline_ref`。模块 Agent 只加载根摘要、一个模块包、
直接 XCT/EDGE 和测试，不加载全项目；它可返回 `REV-*` 或变更提案，但不能直接修改业务基线。
Qoder/Claude/Cursor/Codex 规则只是控制面的投影，不能复制出不同业务 ID。

每个 `XCT-*` 正文至少声明：影响模块、全局不变量、执行点、例外与失败处理和对应 `AC-*`。
只有“权限/审计见全局规则”的空壳不能进入 ready_for_implementation，门禁返回
`HANDOFF-XCT-INCOMPLETE`。
