# 需求生命周期与角色责任 / Requirement Lifecycle And Role Ownership

仅在管理需求阶段、责任或基线时加载。本文件只覆盖需求从准入到验收关闭，不扩张为项目管理
或软件研发全生命周期工具。

## 1. 能力边界 / Boundary

范围内只有六件事：需求准入与优先级、澄清与评审关闭、一份受控规格基线、变更影响与同步、
双向追溯和审计、可执行验收及结果关闭。

范围外包括 Sprint、工期分配、任务跟踪、源码管理、CI/CD、部署、监控、事件响应和产品运营。
只有在证明需求或验收结果需要时，才记录这些外部系统的引用或里程碑。

## 2. 需求记录 / Requirement Record

进入详细设计前先建立一个 `REQ-*`：

| 字段 | 含义 |
|---|---|
| id / title / type | 稳定身份和需求类别 |
| source_refs | 请求、合同、纪要、政策或证据 |
| outcome / value | 可观察结果、价值等级、证据和受影响用户 |
| complexity / uncertainty | S/M/L/XL 影响面及明确未知项 |
| priority | P0-P3及理由；不是安全事故等级 |
| stage / iteration | 当前需求状态和目标基线 |
| dependencies | 阻塞或关联需求 |
| behavior_refs / acceptance_refs | 规格完成后的行为与验收追溯 |
| audit_history | 操作者、时间、原因、动作和前后版本 |

工程负责人未估算前只能记录复杂度区间，不得编造精确工期或成本。

## 3. 准入决策 / Intake Decision

检查价值证据、用户与紧迫性、范围与决策权、复杂度影响、依赖/合规/交付风险，输出一种结果：

- `accept`：价值和责任人明确，按推荐形态继续；
- `clarify`：需求可能成立，但关键未知项会改变范围或结果；
- `defer`：需求有效，但价值较低、依赖未满足或归属后续迭代；
- `reject`：无受支持结果、重复、越界，或风险与收益明显不匹配且无缓解方案。

多需求只记录迭代归属、依赖与顺序，形成轻量需求池，不接管 backlog/Sprint。

单角色、可逆、局部变化可用需求卡。跨角色/模块/系统、实质状态、数据上报或统计口径、
批量 I/O、审批审计、集成、高风险、不可逆写入、迁移或版本兼容必须使用统一 PRD。
这是合同复杂度判断，不是文档长短偏好。

## 4. 决策树澄清 / Decision-Tree Clarification

提问前先执行自查闸（self-check gate）：检查用户材料、仓库和精确领域章节。可从证据回答的
事实先登记为 `inferred` 并给确认建议，只把用户偏好、禁止项、权威和冲突留给用户决策。

按依赖层批量处理互不依赖的事实：

1. 目标、用户、触发和成功；
2. 范围、来源优先级和禁止行为；
3. 角色、权限和数据范围；
4. 主流程、状态转换和跨角色交接；
5. 规则、字段、异常、恢复和集成；
6. 验收阈值、证据、签署和范围外事项。

审美、技术路线、来源冲突等方向节点逐项询问；后续问题必须引用上一答案并沿分支继续。
每个问题包含推荐答案（recommended answer）、证据、取舍和受影响 ID。用户同意后才把
有界推断升级为 `confirmed`；不同意则更新 `REV/UNK/DEC`，不能静默改范围。

只有 P0/P1 分支允许持续追问（Only P0/P1 branches）。P2及以下使用明确推荐默认或有责任人的
`UNK-*`。用户暂不可用（is unavailable）时，记录假设、责任人、`blocks_stage` 和回退路径，
不得静默替用户选择。

澄清仅在所有 P0/P1 已确认，或已转成有责任人、有范围、有阻断阶段和回退路径的 `UNK-*`
时退出。会议结束不代表问题关闭。重点扫描：模糊数量/时间、未定义默认值、匿名角色、隐式审批、
缺失失败处理、无限数据范围，以及没有判断规则的“支持、灵活、适量、及时、等、可配置”。

## 5. 规格与基线 / Specification And Baseline

默认只建立一份统一 PRD；传统 PRD 和 AI Coding PRD 不得成为两个独立事实源。文档语言跟随
用户当前请求，结构依次为30秒摘要、任务阅读地图、业务旅程、模块完整纵切、横切合同和工程/AI索引。

基线至少包含：

- 全部范围内 `REQ-*` 及来源优先级；
- 完整角色和端到端旅程；
- 页面、字段、动作、状态、规则、权限、错误与恢复；
- 适用的业务 API/事件/集成合同；
- 验收标准和追溯索引；
- 明确延期或阻断的未知项；
- 版本、审批人和基线时间。

只有单文档索引不足以支撑规模、多投影、反复变更或强审计时才启用 Product Truth。

## 6. 变更控制 / Change Control

任何实质基线变化都创建 `CHG-*`：

```text
申请 → 校验来源/权威 → 确定种子 ID → 双向影响分析 → 前后差异
→ 兼容/数据/历史审查 → 审批 → 同步全部工件和使用方 → 回归 → 新基线
```

影响面按需覆盖需求、角色、流程、页面/区域/动作、字段/实体、规则/状态、API/事件/集成、
验收/测试/缺陷/证据、历史、权限、数据范围和迁移。

## 7. 双向追溯 / Bidirectional Traceability

每条边记录 `from_id`、`to_id`、`relation` 和 `source`，同时建立正向与反向索引：

```text
SRC → REQ → FLOW/VIEW/ACT/FLD/RULE/STATE/API → AC → TEST/ARUN → EVD
                        ↑                         ↓
                        └──────── CHG / DEFECT ──┘
```

孤立项必须修复，或明确标为草稿、复用参考、范围外或历史证据，不能静默忽略。

## 8. 验收关闭 / Acceptance Closure

将每个 `AC-*` 转为可执行验收项，记录基线版本、环境、执行人/时间、每项结果、实际表现、
证据、缺陷、残余风险和签署结论。结论为 accepted、accepted_with_conditions 或 rejected；
有条件接受还要写责任人和完成标准。只有所有强制项有证据且签署允许，需求才能关闭。

## 9. 状态模型 / State Model

```text
submitted → triaging → clarifying → specified → reviewing → baselined
baselined → acceptance → accepted → closed
任一未关闭状态 → deferred | rejected | cancelled | superseded
baselined → change_requested → baselined（新版本）
```

development/test/deployed 等实现状态只是可选外部里程碑，不能驱动需求状态机。

## 10. 完成门禁 / Completion Gate

返回 PASS 前检查准入证据、P0关闭、规格可读、基线稳定、追溯闭合、变更一致和真实验收证据；
否则返回 `REVIEW_COMPLETE_WITH_GAPS` 或 `BLOCKED_BY_P0_UNKNOWN`，并列出 ID 与责任人。

## 11. 可复用模式 / Reusable Patterns

审批、列表、表单、权限、导入导出和集成可引用
`references/patterns/common-requirement-patterns.yaml`。模式只提供问题、异常合同和 AC 蓝图，
必须结合项目证据绑定 `REQ-*`，不能授权推断角色、字段或规则。

## 12. 角色与职级责任 / Role And Seniority Ownership

职级只改变自主程度，不改变决策权：

- Junior product：盘点事实、登记 `REQ/REV`、起草旅程/规则/AC；范围、价值、来源冲突、
  监管规则和未关闭 P0 必须升级；
- Mid/senior product：在授权内负责准入、澄清、统一 PRD、基线、变更与追溯；
- Developers and Coding Agents：实现一个已固化切片，缺失业务决定返回 `REV-*`，不得编造；
- Architects：维护下游工程基线并挑战不可逆/跨系统缺口，不重新定义产品范围或客户验收。

| Lens | 负责内容 | 不能自行批准 |
|---|---|---|
| sponsor/business | 目标、价值、范围取舍 | 授权外的法律/安全/客户权威 |
| product | REQ/REV/CHG、旅程、PRD、基线、追溯 | 来源冲突或 P0 假设 |
| domain owner | 术语、不变量、来源适用性 | 其他权威的辖区或合同 |
| UX/prototype | 可发现路径、可见状态、等价性和恢复 | 基线缺失的业务政策 |
| engineering/architecture | 可行性、API/状态/事件语义、恢复 | 产品目标和客户签署 |
| QA/acceptance | 正反 AC、证据、缺陷反向追溯 | 代替客户/领域负责人接受 |
| compliance/security | 目的、最小化、人工闸、审计/留存 | 职责外的业务接受 |

正式交接必须包含 baseline version/hash、稳定 ID 范围、禁止推断、外部依赖、责任人和证据要求。
口头澄清只有登记为 `REV/CHG` 后才能改变基线。
