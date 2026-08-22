# Coding Agent 与国产工具适配 / Tool Adapters — v5.4

只有明确指定 Coding Agent、国产模型或需求协作工具消费已固化需求时才加载本文件。统一 PRD 始终是唯一
评审基线；工具规则只能投影约束，不能新增业务行为。可见的研发评审模式服务产品、前端、后端和测试
快速阅读，不是 Coding Agent 的第二份 PRD；Agent 使用结构化 handoff 与稳定 ID 切片。

## 共用交接合同

以下是 Coding Agent 的有界读取顺序，不是业务权威优先级；业务语义仍以已批准 PRD/Truth 与 CHG 为准，
工具规则和 handoff 只能路由/投影约束。Stable ID（稳定 ID）在所有投影中保持不变：

```text
根/模块 AGENTS.md（路由/工程守卫） → handoff manifest/当前 packet
→ 同 hash 的统一 PRD或 Product Truth ID 切片 → 已批准 CHG-*
→ 锁定产品原型的 VIEW/REG/ACT → 工程基线/仓库约束 → 验收记录
```

- 一次只实现绑定 `REQ/MOD/FLOW/VIEW/REG/ACT/FLD/STM/STATE/METRIC/REL/API/AC` 的一个纵切。
- 冲突或缺失业务决策返回 `REV-*`/`CFL-*`；不得编造角色、字段、状态、权限、公式、默认值或事件。
- 状态、多租户、权限和高风险守卫以后端为准。
- 仓库路径、框架和技术架构属于下游工程事实，不能反向扩大产品范围。
- 测试和实现证据必须回链到 `AC-*` 与 `REQ-*`。
- 大任务只加载一个 PRD/Truth 切片并保存检查点，禁止让一个模型重写巨型事实源。
- 评审工作台只给人类走读；Agent 可用其稳定锚点核对页面落点，但不读取角色文案来补规则。manifest 缺失、
  baseline hash 不同或 STEP/AC 解析失败时返回 GAP/REV，不得降级为“看原型猜实现”。

- 人类可见标题、验收叙述和图节点跟随用户语言；机器状态、字段/API名和 Schema 关键字保持原值，
  通过“草稿（`draft`）”这类显式映射消除歧义，不把混合语言当作技术精确。
## 工具路由

| 工具/模型 | 适配规则 |
|---|---|
| OpenAI / Codex | 先读批准的需求切片再检查仓库；优先遵循用户语义与否定约束；在 UI 锚点和测试中保留稳定 ID，运行适用仓库检查并返回证据。 |
| Anthropic / Claude / Claude Code / Cursor | 在项目规则中固定来源顺序、`entry_stage/target_stage` 和禁止推断；按稳定 ID 检索可选 Product Truth，不加载整张图。 |
| Trae | 每个任务只编写或实现一个纵切；切换前保存已接受检查点。 |
| WorkBuddy | 工作区规则只放 `SKILL.md` 和当前 PRD/Truth 切片；每个事项验证一个检查点。 |
| Qoder | `.qoder/rules` 只保留文件匹配和工具权限；业务规则引用根/模块 `AGENTS.md` 与 PRD，避免工具规则优先级造成漂移。 |
| CodeBuddy | 使用共用交接合同，编码前返回歧义；不得把 UI 猜测升级为需求。 |
| Z.AI / GLM | 使用简洁中文和确定性输出结构；稳定 ID 原样保留，压缩上下文时不能丢角色、权限、状态、异常和 P0 AC。 |
| DeepSeek | 分离分析与最终工件；按合同章节起草，每个接受切片后运行确定性门禁。 |
| Alibaba / Qwen / Qwen Code | 长中文 ToB/ToG 输入先生成 Context Plan，再按模块/流程切片写入同一 PRD。 |
| Moonshot / Kimi | 先读 `SKILL.md`，再只加载目标阶段切片、对应模板/Schema/门禁；禁止读取 README、`maintainer/`、无关模板和全量领域包。除非当前阶段确需时效性证据，否则不做外部调研；目标门禁得出结论后立即停止。长上下文只用于用户明确要求的来源盘点，随后冻结 ID 索引、目标阶段和权威层级，再切换到小模块检查点。 |

> **版本证据规则**：Skill 只固化模型家族和交接行为，不把未经官方公开目录或当前运行时确认的版本名写成能力事实。跨模型测评必须记录 CLI/API 实际返回的 `provider`、`model_id`、客户端版本、上下文/温度设置与运行日期；社区俗称、共享 Token 或推测版本不能作为证据。

### 无人值守跨模型执行合同

CLI/API 批量测评或后台任务必须在用户需求后附加以下边界，避免把“模型愿意继续探索”误当成更高质量：

1. 先读 `SKILL.md`，禁止读取 README、`maintainer/`、无关示例和全量领域包；
2. 只读目标阶段在 `references/stages.md` 指定的最小切片，以及该阶段明确引用的模板、Schema 和门禁；
3. 只生成目标阶段合同要求的主产物与必要伴随工件，不补写后续阶段；
4. 不是 discover/explore 且没有时效性或外部证据缺口时，不进行网络检索；
5. 运行目标阶段门禁或返回阻断结论后立即停止，不输出长篇工作日志；
6. 记录实际 provider、model_id、客户端版本、耗时、产物数与门禁结果；行为 PASS 与成本结论分开。

## 需求协作工具交接

Jira、Linear、Azure DevOps、TAPD、禅道等外部工具只接收需求基线的索引，不成为第二事实源：

| Skill 字段 | 外部工具常见映射 | 同步规则 |
|---|---|---|
| `REQ-* / title / priority` | issue/work item 标识、标题、优先级 | 保留 Stable ID；外部改名不重写需求语义 |
| `iteration_ref / dependency_refs` | release/version、blocked-by/relates-to | 只同步归属和依赖，不在 Skill 内拆 Sprint/工时 |
| `baseline_version + hash` | 固定版本字段/附件链接 | 任何实现事项必须回链准确基线 |
| `stage` | 需求状态 | 开发/部署状态写入 `external_milestones`，不能反向伪造需求已验收 |
| `review_refs / change_refs / acceptance_refs` | 评审、变更、验收链接 | 只传引用与结论，原证据仍由受控工件保存 |

需求交付/技术负责人可先运行：

```bash
python scripts/validators/validate_requirement_register.py requirements/register.yaml --summary
```

它只聚合优先级、复杂度带、依赖和迭代归属，供人做容量与版本判断；不自动排期、不分配人员，也不调用模型。

## 直接编码入口

只有交接包同时具备以下内容才允许进入实现：

1. 已批准的基线版本和稳定 ID 切片；
2. 开放外部依赖和禁止推断清单；
3. 适用 API/业务语义、状态、错误与恢复；
4. 正向和反向验收及可观察证据；
5. 工程团队提供的仓库与架构约束。

先校验统一需求；只有可选 Product Truth 实际存在时才校验它。验证器 PASS 是就绪证据，
不是客户或领域负责人的接受结论。
