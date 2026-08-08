---
artifact: decision_record
stage: clarify
schema_version: 5.4.0
version: "0.1"
status: draft
document_language: zh-CN
project_id: PROJECT-EXAMPLE
resume_context:
  completed_stages: [intake]
  # 续跑对象示例（全新任务保持空数组）：
  # - path: prior/intake.yaml
  #   sha256: "0000000000000000000000000000000000000000000000000000000000000000"
  #   stage: intake
  prior_artifacts: []
  open_threads: []
  next_stage_options: [clarify, specify]
---

# 决策记录：{需求/决策主题}

<!-- ADS:decision_log -->
## 已固化决策

| ID | 决策 | 选项与取舍 | 依据/来源 | 决策人 | 日期 | 状态 |
|---|---|---|---|---|---|---|
| `DEC-001` | {决策} | {选中与未选原因} | `SRC-*` | {有权责任人} | {日期} | 已确认（`confirmed`） |

<!-- ADS:rejected_options -->
## 未采用选项与复议条件

| 选项 | 未采用原因 | 决策人 | 复议条件 |
|---|---|---|---|
| {选项} | {原因} | {责任人} | {新证据/新边界} |

<!-- ADS:unknowns -->
## 剩余未知项

| ID | 优先级 | 内容 | 责任人 | 阻断阶段（`blocks_stage`） | 回退路径 | 状态 |
|---|---|---|---|---|---|---|
| `UNK-001` | P1 | {未知} | {责任人} | 需求基线（`baseline`） | {退路} | 待关闭（`open`） |

<!-- ADS:accepted_risks -->
## 接受的风险

| 风险 | 接受人 | 边界/期限 | 理由与证据 |
|---|---|---|---|
| {风险} | {责任人} | {范围/到期日} | {依据} |

<!-- ADS:next_step -->
## 下一步

进入规格固化（`specify`）/继续澄清（`clarify`）/缩范围/暂停；需携带全部 `DEC-*` 与开放 `UNK-*`。
