---
artifact: requirement_brief
stage: clarify
schema_version: 5.4.0
version: "0.1"
status: draft
document_language: zh-CN
project_id: PROJECT-EXAMPLE
requirement_refs: [REQ-CORE-001]
assumption_refs: []
assumption_resolutions: []
resume_context:
  completed_stages: [intake]
  # 续跑对象示例（全新任务保持空数组）：
  # - path: prior/intake.yaml
  #   sha256: "0000000000000000000000000000000000000000000000000000000000000000"
  #   stage: intake
  prior_artifacts: []
  open_threads: []
  next_stage_options: [specify, intake]
---

# 需求澄清简报：{需求名称}

<!-- ADS:summary -->
## 30 秒摘要

为{用户}在{场景}解决{问题}，本次只交付{范围}；成功以{信号}判定。

<!-- ADS:outcome -->
## 目标、成功指标与约束

| 项目 | 内容 |
|---|---|
| 用户结果 | {可观察结果} |
| 业务结果 | {可判定结果} |
| 指标口径 | {对象、公式、周期、去重、数据源、空值/异常处理} |
| 强约束 | {权限、合规、兼容、时间等} |
| 准入继承 | `REQ-*`、优先级、复杂度档位、目标迭代和依赖；不得在此虚构估时 |

<!-- ADS:users -->
## 角色与核心场景

| 角色 | 入口/前置 | 目标任务 | 结果/交接方 |
|---|---|---|---|
| `ROLE-*` | {入口} | {任务} | {可见结果及接收角色} |

<!-- ADS:scope_in -->
## 本期范围

- {明确纳入的能力、数据和表面}

<!-- ADS:scope_out -->
## 非目标与后续口子

- {明确不做；是否预留以及预留到什么边界}

<!-- ADS:decisions -->
## 已确认决策

| ID | 决策 | 选项与取舍 | 依据/来源 | 决策人 | 状态 |
|---|---|---|---|---|---|
| `DEC-001` | {决策} | {选择及未选原因} | `SRC-*` | {责任人} | 已确认（`confirmed`） |

<!-- ADS:rules -->
## 业务规则、流程与异常

| ID | 触发/前置 | 系统行为与数据变化 | 可见结果 | 失败/恢复 | 验收方向 |
|---|---|---|---|---|---|
| `BR-001` | {触发条件：当/期间/如果} | {必须；写明覆盖/追加/幂等/权限} | {结果} | {错误、重试、回退} | `AC-*` |

<!-- ADS:unknowns -->
## 未知项、风险与禁止推断

| ID | 优先级 | 内容 | 责任人 | 阻断阶段（`blocks_stage`） | 回退/缩范围路径 | 状态 |
|---|---|---|---|---|---|---|
| `UNK-001` | P1 | {尚未确认内容} | {责任人} | 需求基线（`baseline`） | {安全退路} | 待关闭（`open`） |

<!-- ADS:next_step -->
## 出口判断与下一步

- 结论：
  - 可进入轻量规格（`READY_FOR_LIGHT_SPEC`）/可进入统一 PRD（`READY_FOR_UNIFIED_PRD`）；
  - 可进入受治理需求真相（`READY_FOR_PRODUCT_TRUTH`）；
  - 被 P0 未知项阻断（`BLOCKED_BY_P0_UNKNOWN`）。
- 下一交付：{需求卡/统一PRD/受治理真相/返回准入}
- 必须携带：`DEC-*`、开放`UNK-*`、适用来源、禁止推断项和责任人。
