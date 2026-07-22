---
artifact: requirement_card
baseline_version: 1.0
delivery_level: L1
delivery_shape: requirement_card
document_language: zh-CN
language_source: user_request
bilingual: false
activated_facets: [ui]
open_p0_unknown_ids: []
unknowns: []
status: baseline
governance:
  canonical_authoring_surface: unified_prd
  binding_sources:
    - source_ref: SRC-MINIMAL-001
      canonical: true
---

# 制度列表“仅看当前有效”需求卡

## 0. 文档控制与准入结论

`REQ-POLICY-ACTIVE-001`，基线版本 1.0。负责人和确认人均为产品负责人；准入结论为
`accept / requirement_card`。这是单角色、局部、可逆的列表筛选，不涉及状态写入、审批、
外部集成或敏感数据。

## 1. 目标与范围

- 目标：员工可一键只看查询时刻处于有效期内、且在本人数据权限范围内的制度。
- 本期范围：制度列表新增 `FLD-POLICY-ACTIVE-ONLY` 筛选开关，默认关闭。
- 明确不做：不修改制度状态，不改变搜索排序，不新增 AI 问答，不保存个人筛选偏好。
- 成功信号：正常、空结果与无权场景均按 `AC-POLICY-ACTIVE-001`—`003` 可判定。

## 2. 角色与用户故事

`ROLE-EMPLOYEE` 已登录且具有制度列表访问权限。作为员工，我希望在制度列表开启“仅看当前有效”，
从而避免查看已失效或尚未生效的制度。筛选始终叠加现有组织和制度分类数据权限，不能扩大可见范围。

## 3. 用户旅程、主流程与异常

`FLOW-POLICY-ACTIVE-001`：员工进入制度列表 → 开启 `ACT-POLICY-ACTIVE-ON` → 列表回到第 1 页
并显示已启用标签 → 只展示 `effective_from <= 当前时间` 且
`effective_to 为空或 effective_to > 当前时间` 的有权记录。

- 关闭开关：`ACT-POLICY-ACTIVE-OFF` 恢复原列表条件并回到第 1 页。
- 无匹配数据：显示“暂无当前有效制度”和清除筛选入口，不显示错误态。
- 无列表权限：沿用既有无权页，不展示该筛选，不能通过请求参数绕过权限。
- 查询失败：保留开关值，显示可重试提示；重试前不展示旧查询结果为最新结果。

## 4. 字段、规则与界面规格

| ID | 规格 |
|---|---|
| FLD-POLICY-ACTIVE-ONLY | 布尔开关；标签“仅看当前有效”；默认 `false`；不持久化；位于现有筛选区末尾 |
| RULE-POLICY-ACTIVE-001 | `effective_from <= server_now AND (effective_to IS NULL OR effective_to > server_now)`；边界时刻使用服务端时间 |
| RULE-POLICY-ACTIVE-002 | 新条件与关键词、分类、组织权限取交集；切换后页码重置为 1，分页大小保持原值 |
| RULE-POLICY-ACTIVE-003 | 仅改变查询条件，不产生制度状态、审计或外部事件；无外部集成 |

## 5. 验收与测试

| AC/TEST | Given 前置与数据 | When 操作 | Then 可见结果 | And 领域结果/反例证据 |
|---|---|---|---|---|
| AC-POLICY-ACTIVE-001 / TEST-POLICY-ACTIVE-001 | 有权数据包含有效、失效、未生效制度 | 开启开关 | 标签显示已启用，页码为 1，仅显示有效制度 | 返回记录全部满足 RULE-POLICY-ACTIVE-001，截图与响应记录可复核 |
| AC-POLICY-ACTIVE-002 / TEST-POLICY-ACTIVE-002 | 权限范围内没有有效制度 | 开启开关 | 显示空状态和清除筛选入口 | 不出现越权记录，也不把空结果显示为系统错误 |
| AC-POLICY-ACTIVE-003 / TEST-POLICY-ACTIVE-003 | 用户无制度列表权限 | 直接访问页面或构造筛选请求 | 显示既有无权结果且无开关 | 服务端拒绝请求，不能因筛选参数扩大数据范围 |

## 6. 未知项与升级判断

无未决项。若后续要求保存个人偏好、跨端同步、统计使用率或修改制度有效状态，应以同一
`REQ-POLICY-ACTIVE-001` 发起变更并重新分诊，不在本卡中自行扩展。
