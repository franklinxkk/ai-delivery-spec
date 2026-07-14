# 通用事项登记需求规格说明书

> 这是业务、产品、传统开发、测试和 Coding Agent 共用的一份 PRD，不维护两套 PRD。

## 0. 文档控制与来源优先级

基线版本 `1.0`。来源优先级为已批准决策、会议纪要、方案、原型。所有基线变更走
`CHG-ITEM-001` 变更入口，不允许口头覆盖。

## 1. 背景、目标与成功指标

目标：管理员可登记事项并立即看到已生效结果。成功指标按自然日计算成功唯一请求数 /
合法提交数，排除校验失败和重复请求。

## 2. 需求准入与范围

| REQ ID | 需求 | 价值证据 | 复杂度 | 优先级 | 结论 | 依赖 |
|---|---|---|---|---|---|---|
| REQ-ITEM-001 | 登记事项 | 已批准客户请求 SRC-ITEM-001 | S | P1 | accept | 无 |

范围包含单租户事项创建；批量导入和外部同步不在本期。

## 3. 角色与数据范围

| ROLE ID | 目标 | 权限 | 数据范围 | 禁止操作 |
|---|---|---|---|---|
| ROLE-ADMIN | 创建事项 | create | 当前租户 | 访问其他租户 |

## 4. 角色旅程 FLOW-ITEM-CREATE

ROLE-ADMIN 从 VIEW-HOME 进入，填写 FLD-NAME，触发 ACT-SUBMIT。系统校验权限、
租户、字段和版本，成功后展示事项编号及“已生效”；失败时保留输入并给出可恢复原因。
创建结果可在列表查到，AC-ITEM-001 证明可见结果和领域结果。

## 5. 业务流程与状态机 STATE-ITEM

| 步骤 | 角色 | 前置 | 操作 | 规则 | 状态变化 | 失败与恢复 |
|---|---|---|---|---|---|---|
| 1 | ROLE-ADMIN | 已登录 | 打开 VIEW-HOME | 当前租户 | 无 | 无权时终止 |
| 2 | ROLE-ADMIN | draft | ACT-SUBMIT | RULE-NAME-001 | draft→active | 保留输入后重试 |

并发使用 `expectedVersion`，重复使用 `clientRequestId` 返回首次结果，不重复创建。

## 6. 功能总览与信息架构

| MOD ID | 页面 | 区域 | 动作 | 结果 |
|---|---|---|---|---|
| MOD-ITEM | VIEW-HOME | REG-FORM | ACT-SUBMIT | 事项 active |

## 7. 分模块功能需求

### 7.1 页面与布局 VIEW-HOME

页面顶部显示标题，中部 REG-FORM 含名称字段和提交按钮，下部显示最近创建结果。
加载、空、错误、无权限和成功状态均必须有明确文字，不用颜色单独表达。

### 7.2 关键操作 ACT-SUBMIT

| ACT ID | 前置 | 可见结果 | 领域结果 | 失败/恢复 | AC |
|---|---|---|---|---|---|
| ACT-SUBMIT | ROLE-ADMIN + draft | 编号和已生效 | 事项仅创建一次并 active | 保留字段、提示错误 | AC-ITEM-001 |

### 7.3 异常与边界

名称为空返回校验错误；版本冲突提示刷新后重试；无权返回 403 且不泄露数据；外部集成
本期不适用，未来批准出站消费者时补充对账规则。

## 8. 数据与字段流转

FLD-NAME 从 REG-FORM 进入创建命令，服务端校验后写入 ENT-ITEM，并产生
EVT-ITEM-CREATED；列表按当前租户读取 active 事项。

## 9. 非功能、安全与隐私

服务端强制租户权限；P95 创建接口不高于 500ms；状态变更写审计，敏感日志不记录名称原文。

## 10. 指标与统计口径

按 `clientRequestId` 去重，成功指 ENT-ITEM 达到 active，同一自然日、当前租户汇总。

## 11. 验收方案

| AC ID | 前置与角色 | 步骤 | 预期可见结果 | 预期领域结果 | 反例 | 证据 |
|---|---|---|---|---|---|---|
| AC-ITEM-001 | ROLE-ADMIN 已登录 | 输入合法名称并提交 | 显示编号和已生效 | active 事项恰好一条 | 重复请求不新增 | UI 截图+API trace |

## 12. 验收结论规则

AC-ITEM-001 为必过项；失败或无证据时结论为 rejected。条件通过必须记录负责人和关闭条件。

> 第四部分：工程与 AI Coding 附录

## 附录 A：页面—区域—动作索引

| VIEW | REG | ACT | ROLE | STATE | API | AC |
|---|---|---|---|---|---|---|
| VIEW-HOME | REG-FORM | ACT-SUBMIT | ROLE-ADMIN | STATE-ITEM | API-ITEM-CREATE | AC-ITEM-001 |

## 附录 B：全局字段字典

| FLD ID | 实体.字段 | 含义 | 类型 | 必填 | 来源 | 编辑权 | 校验 | 敏感 |
|---|---|---|---|---|---|---|---|---|
| FLD-NAME | ENT-ITEM.name | 事项名称 | string | 是 | 用户输入 | ROLE-ADMIN/当前租户 | 1..100 字符 | internal |

## 附录 C：规则与状态机

RULE-NAME-001：去除首尾空格后长度 1..100；失败不改变状态。STATE-ITEM 只允许
draft 经 ACT-SUBMIT 到 active，服务端校验角色、租户和 expectedVersion。

## 附录 D：API、事件与集成业务契约

### POST `/api/items`

请求字段 / Request fields：`name`, `expectedVersion`, `clientRequestId`。
成功响应 / Response body：`code`, `message`, `data.id`, `data.state`, `data.version`。

| API | 权限/幂等 | 业务错误 | HTTP | 状态/事件副作用 | 对账/补偿 |
|---|---|---|---|---|---|
| API-ITEM-CREATE | ROLE-ADMIN / clientRequestId | ERR-NAME-INVALID, ERR-VERSION-CONFLICT | 400/409 | active + EVT-ITEM-CREATED v1 | 按请求 ID 查首次结果 |

事件 payload version v1 包含 eventId、aggregateId、tenantId、state 和 occurredAt。

## 附录 E：机器可读验收

```yaml
acceptance:
  - id: AC-ITEM-001
    requirement_refs: [REQ-ITEM-001]
    behavior_refs: [FLOW-ITEM-CREATE, VIEW-HOME, ACT-SUBMIT, RULE-NAME-001]
    preconditions: [ROLE-ADMIN authenticated in current tenant]
    steps: [open VIEW-HOME, enter FLD-NAME, invoke ACT-SUBMIT]
    expected_visible: item id and active state are visible
    expected_domain: one ENT-ITEM is active for clientRequestId
    negative_cases: [empty name, version conflict, duplicate request, forbidden tenant]
    evidence_required: [ui_screenshot, api_trace, audit_record]
```

## 附录 F：双向追溯矩阵

| REQ | 来源 | 流程/页面/动作/字段/规则 | API/事件 | AC | 测试/证据/变更 |
|---|---|---|---|---|---|
| REQ-ITEM-001 | SRC-ITEM-001 | FLOW-ITEM-CREATE / VIEW-HOME / ACT-SUBMIT / FLD-NAME / RULE-NAME-001 | API-ITEM-CREATE / EVT-ITEM-CREATED | AC-ITEM-001 | TEST-ITEM-001 / EVD-ITEM-001 / CHG-ITEM-001 |

反向索引：AC-ITEM-001、TEST-ITEM-001、EVD-ITEM-001 和 DEFECT-ITEM-001 均反查
REQ-ITEM-001；任何新增孤儿项阻断基线。

## 附录 G：禁止推断清单

禁止推断新增角色、字段、状态、默认值、审批、跨租户访问和外部消息。技术架构、数据库、
框架、涉及文件、部署和任务拆分由下游技术方案决定，不得改写上述业务契约。
