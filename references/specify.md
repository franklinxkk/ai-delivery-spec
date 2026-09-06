# 最小充分业务规格

目标是让实施者不必补猜关键业务选择；技术实现保留空间。用用户语言表达，一条事实只人工定义一次，其他页面、流程、机器交接引用或展开同一内容。不要把同一规则在页面表、模块表、STEP 和附录分别改写。

## 从当前改变纵向写清

说明来源和目标、改变与继承的范围、谁在什么前提下做什么、可见反馈与业务结果、拒绝/失败/恢复及验收。简单只读字段只需对应差异；多模块规格按一条完整用户链或模块纵切，有跨模块依赖才补最小有用的流程/状态/数据流图。

自然语言标题可自由选择，不要求固定章节数量、表格比例或工程附录。字段、规则和稳定 ID 就近放置；确需多投影或审计才使用 Product Truth。Markdown 是便于修改与检查的默认形式，分发件按实际用途选择，不能反向覆盖已指定权威。

可从 [需求卡](templates/prd-light-template.md) 或 [统一规格](templates/unified-requirement-prd-template.md) 开始；模板是编辑起点，不适用部分可删除。数据库、框架、端点或精确阈值只有构成已授权业务/集成约束才进入规格，不能为填空发明。

## 按风险补足，不按规模升级

| 触发内容 | 必要业务约定与反例 |
|---|---|
| 状态/审批 | 状态权威、动作、允许者、守卫、业务结果；通过是发布前提时不能擅自自动发布 |
| 指标/统计 | 对象、公式与分子分母、时间/时区、过滤/去重、权威源、空零与时效；用边界数据检查 AND/OR、分母和快照 |
| 拒绝/退回/失败 | 谁还能修改什么、从哪重提、旧对象保留什么；拒绝后有真实下一步而非只有提示 |
| 可空或陈旧数据 | 区分零、空、未采集、无权、失败和过期；已决显示可继承，不猜未知的业务含义 |
| 权限/隐私 | 主体、对象、动作和数据范围；UI隐藏不证明授权；按实际可达路径检查深链、撤权、批量 |
| 身份/已有规则变更 | 区分显示序号与稳定身份，查读写、计数、旧对象、别名和失效证据 |
| 外部系统/批量/异步 | 生产者与消费者、方向、匹配/版本、时效、重复/乱序/部分成功、幂等与对账恢复；精度取已决约束 |
| 高后果 AI 写入 | 数据与指令来源、可操作范围、确认/回退、拒绝及异常；工具执行不越过用户授权 |

标签只是辅助索引，内容出现风险但 risk_facets 缺失时仍需审查。高影响规则逐条查，其他取代表对象，并写明未覆盖范围。两个接收者一致也可能共同理解错，须核对来源和独立反例。

业务审批与需求评审是两个对象；审批理由不能塞入 baseline/context/point 的需求确认记录。接收方确认一条需求规则也不代表运行中的业务对象已批准。

## 可选机器声明

日常文本不强制 frontmatter。需执行 `gate --profile prd` 时，可用下面的声明帮助定位；缺失不得被自动补成已确认：

```yaml
artifact_mode: card
baseline_version: B2
requirement_ids: [REQ-RETRY]
risk_facets: [state]
decisions:
  - id: DEC-REJECT
    status: confirmed
    actor: 有权决定人
    source_refs: [SRC-APPROVAL]
unknowns:
  - id: UNK-RETRY
    status: open
    affected_refs: [REQ-RETRY]
    blocks_stage: baseline
semantic_reviews: []
```

声明经过结构检查不证明授权真实性。unknowns 的关闭绑定 resolution_ref/source_refs；风险接受另写其授权与当前执行边界，不能只改成 closed。需要审查记录时，在同一规格或现有 ARUN/EVD 中保留类别、对象范围、来源、版本、评阅者、结果、证据。支持类别为 state_authority、metric_definition、recovery、null_stale、permission_boundary、change_propagation；未执行用 not_run，不适用说明理由。

`semantic_reviews` 的 pass 需要 scope_refs、source_refs、reviewer、baseline_version 和 evidence_ref；not_applicable 需范围、理由、评阅者及当前版本。检查范围由 --scope-ref 或 requirement_ids/scope_refs 指定；一个对象的通过不能覆盖另一个对象。工具检查声明与版本，不替人核实自然语言和签署。外部实际结果使用 [验收合同](change-acceptance.md)。

## 交接的充分性

对复杂或正式交接，让无讨论历史的接收方复述主路径、拒绝/恢复、数据权威和未决事项，或完成一个小测试/实施任务。产品、前后端、QA 和 Agent 共享相同业务含义；正常技术选择不计为规格失败。

一次明确小改无须全角色报告。缺少工程基线时，业务规格仍可在对应目标下完成，工程交接保持缺口。声称可开发或验收完成时，必须有该范围所需的决定、来源和实际证据；不要把模板填满当完成。
