---
delivery_level: L2
delivery_shape: governed_truth
assurance_profile: standard
document_language: zh-CN
language_source: user_request
bilingual: false
activated_facets: [ui, stateful, integration, high_risk]
open_p0_unknown_ids: []
governance:
  canonical_authoring_surface: product_truth
  decision_ref: DEC-AUTHORITY-PUBLISHING-001
  projection_policy: update_in_same_change
---

# 融合出版与学习服务需求规格说明书

> 这是客户、产品、传统开发、测试与 Coding Agent 共用的一份 PRD。大型示例的
> 结构化权威层是 `../truth/product-truth.yaml`（Product Truth 5.1.0）；本文是唯一
> 人类阅读基线，不维护两套 PRD。

## 0. 文档控制与来源优先级

基线 `1.0/baselined`；SRC-PUBLISHING-REQ-001（binding）是客户一书一码及授权材料。批准材料优先；修改须建立 `CHG-*` 并完成影响、diff、审批、同步和回归。

### 0.1 任务式阅读导航

客户读摘要、范围、旅程与验收；产研按 `MOD-*` 和附录读取纵向切片；Coding Agent 只实现指定 ID。

### 0.2 30 秒摘要

内容管理员发布不可变课程版本并授权渠道；渠道在额度内交付学习码；学员激活后获得唯一权益并形成学习证据。任一步失败不得伪造下游成功，ROLE-QA-ACCEPTOR 按 AC 和审计证据验收。本期不含支付结算和法定证书签发。

## 1. 背景、目标与成功指标

目标：内容形成不可变课程版本，渠道额度内分发，学员凭合法码获得权益和学习证据。METRIC-ACTIVATION-001（生成权益的合法首次激活数 ÷ 合法首次请求数）按月对账，目标 98%；分母 0 或源失败显示“—”及原因。

## 2. 需求准入与范围

| REQ ID | 结果 | 优先级 | 状态 | 验收 |
|---|---|---|---|---|
| REQ-CONTENT-PUBLISH-001 | 发布不可变课程版本 | P0 | baselined | AC-PUBLISH-001 |
| REQ-CHANNEL-AUTH-001 | 额度内授权渠道 | P0 | baselined | AC-AUTH-001 / AC-AUTH-OVERLIMIT-001 |
| REQ-CODE-ACTIVATE-001 | 合法码生成唯一权益 | P0 | baselined | AC-ACTIVATE-001 / AC-ACTIVATE-DUPLICATE-001 |
| REQ-LEARNING-EVIDENCE-001 | 有权益学习形成证据 | P0 | baselined | AC-LEARN-001 |

本期不含第三方支付结算和法定职业资格证书签发。

## 3. 角色与数据边界

| 角色 | 责任 | 数据范围 | 禁止行为 |
|---|---|---|---|
| ROLE-CONTENT-ADMIN | 内容编排、发布与授权 | 出版方内容和授权 | 修改已发布快照 |
| ROLE-CHANNEL-ADMIN | 在额度内向属地使用资源 | 自组织授权和码 | 查看其他渠道数据 |
| ROLE-LEARNER | 激活和学习 | 本人权益与记录 | 访问他人记录 |
| ROLE-QA-ACCEPTOR | 按口径验收 | 试点和脱敏汇总 | 修改业务记录 |

## 4. 角色旅程与跨角色闭环

ROLE-CONTENT-ADMIN 在 FLOW-PUBLISH-001 打开 VIEW-COURSE-EDITOR 提交发布，再按 FLOW-AUTH-001 到 VIEW-AUTH-CONSOLE 授权；ROLE-CHANNEL-ADMIN 交付码；ROLE-LEARNER 按 FLOW-ACTIVATE-001 激活、按 FLOW-LEARN-001 学习；ROLE-QA-ACCEPTOR 按 AC 验收成功结果。失败时显示原因、保持数据并从原台账恢复。

## 5. 业务流程与状态

主链路：`FLOW-PUBLISH-001 → FLOW-AUTH-001 → FLOW-ACTIVATE-001 → FLOW-LEARN-001`。发布不可原地修改；授权原子扣减；码仅首次合法绑定；仅有效权益计入证据。

| FLOW ID | 起点与主动作 | 成功结果 | 失败/补偿 |
|---|---|---|---|
| FLOW-PUBLISH-001 | 草稿完整；发布 | 不可变版本 | 缺项留草稿；改版新建版本 |
| FLOW-AUTH-001 | 版本已发布；授权 | 授权且原子扣额 | 超额/越级零写入；未用额可审计回收 |
| FLOW-ACTIVATE-001 | 合法未用码；激活 | 唯一码权益 | 过期/已用/越权拒绝；误绑人工审核 |
| FLOW-LEARN-001 | 有效权益；学习 | 事件和证据 | 无效拒绝、重复幂等、异常复核 |

## 6. 功能总览与信息架构

| 页面 | 模块 | 核心动作 | 领域结果 |
|---|---|---|---|
| VIEW-COURSE-EDITOR | MOD-CONTENT-001 | ACT-COURSE-PUBLISH | 课程快照发布 |
| VIEW-AUTH-CONSOLE | MOD-AUTH-001 | ACT-AUTH-GRANT | 授权创建且额度扣减 |
| VIEW-CODE-ACTIVATE | MOD-LEARNING-001 | ACT-CODE-ACTIVATE | 码绑定并创建权益 |
| VIEW-LEARNING-HOME | MOD-LEARNING-001 | ACT-LEARNING-COMPLETE | 学习事件和证据写入 |

## 7. 分模块功能需求

### 7.1 内容编排与发布 MOD-CONTENT-001

目标为发布不可变课程，边界是不负责授权；入口 VIEW-COURSE-EDITOR，前置草稿完整，结果为版本快照。主路径 FLOW-PUBLISH-001 / ACT-COURSE-PUBLISH；异常显示缺项，恢复为保留草稿重试。字段 FLD-COURSE-NAME 来源为管理员，权限仅草稿期。RULE-COURSE-COMPLETE-001、STM-COURSE-001、EVT-COURSE-PUBLISHED。指标不适用；数据质量为快照完整且版本唯一。AC-PUBLISH-001；无未决项。

### 7.2 授权与学习码 MOD-AUTH-001

目标为额度内授权，边界是不负责分发；入口 VIEW-AUTH-CONSOLE，前置组织有效且额度充足，结果为授权和余额同步。主路径 FLOW-AUTH-001 / ACT-AUTH-GRANT；异常零写入，恢复为台账重试。字段 FLD-AUTH-QUOTA 来源授权台账，权限由服务端守卫。RULE-AUTH-SCOPE-001、STM-AUTH-001、EVT-AUTH-GRANTED、INT-ORG-MASTER-001。指标不适用；数据质量为余额非负和事务一致。AC-AUTH-001 / AC-AUTH-OVERLIMIT-001；无未决项。

### 7.3 激活、学习与证据 MOD-LEARNING-001

目标为激活和学习，边界是不签发法定证书；入口 VIEW-CODE-ACTIVATE / VIEW-LEARNING-HOME，前置码和权益有效，结果为唯一权益与证据。主路径 FLOW-ACTIVATE-001 / FLOW-LEARN-001、ACT-CODE-ACTIVATE / ACT-LEARNING-COMPLETE；异常返回原因，恢复按幂等键重试。字段 FLD-CODE-VALUE / FLD-LEARNING-PROGRESS 来源码服务/事件，权限仅本人。RULE-CODE-VALID-001、STM-CODE-001、STM-LEARNING-001、EVT-CODE-ACTIVATED、EVT-LEARNING-UPDATED。METRIC-ACTIVATION-001 去重日更；数据质量靠权益/事件对账。AC-ACTIVATE-001 / AC-ACTIVATE-DUPLICATE-001 / AC-LEARN-001；无未决项。

### 7.4 关键动作合同

| ACT | 角色/前置 | 可见结果 | 领域结果 | 失败/恢复 | 审计/事件 | AC |
|---|---|---|---|---|---|---|
| ACT-COURSE-PUBLISH | ROLE-CONTENT-ADMIN/草稿完整 | 版本快照 | 新不可变版本 | 缺项且留草稿 | EVT-COURSE-PUBLISHED | AC-PUBLISH-001 |
| ACT-AUTH-GRANT | ROLE-CONTENT-ADMIN/额度足 | 授权/余额 | 原子授权扣额 | 超额零写入 | EVT-AUTH-GRANTED | AC-AUTH-001 |
| ACT-CODE-ACTIVATE | ROLE-LEARNER/码有效 | 学习入口 | 唯一权益 | 首次结果或拒绝 | EVT-CODE-ACTIVATED | AC-ACTIVATE-001 |
| ACT-LEARNING-COMPLETE | ROLE-LEARNER/权益有效 | 完成进度 | 一份证据 | 幂等重试 | EVT-LEARNING-UPDATED | AC-LEARN-001 |

## 8. 数据与接口流转

INT-ORG-MASTER-001（入站组织主数据权威）不可用时禁止新增、既有只读，恢复后重试对账；技术方案定接口路径，本需求固定映射、权限、降级、幂等和对账结果。

## 9. 非功能、安全与合规

学习身份为受限数据；渠道隔离、服务端守卫、审计和证据留存必须可验收。性能目标待试点规模确认。

## 10. 验收方案

| AC | 角色/前置 | 步骤/输入 | 可见结果 | 领域结果 | 反例 | 证据 |
|---|---|---|---|---|---|---|
| AC-PUBLISH-001 | ROLE-CONTENT-ADMIN/草稿完整 | 提交课程发布 | 版本与快照可见 | 发布不可变版本 | 缺资源/重复请求 | 截图+审计 |
| AC-AUTH-001 | ROLE-CONTENT-ADMIN/额度充足 | 选择组织、范围和数量 | 新授权和余额可见 | 原子创建/扣减 | 超额/越权 | API+审计 |
| AC-AUTH-OVERLIMIT-001 | ROLE-CONTENT-ADMIN/余10 | 授权20 | 提示不足、保留输入 | 零写入 | 重复/并发 | 自动化+审计 |
| AC-ACTIVATE-001 | ROLE-LEARNER/码有效 | 提交码与身份 | 课程入口可见 | 唯一权益生成 | 失效/重复/越权 | UI+领域记录 |
| AC-ACTIVATE-DUPLICATE-001 | ROLE-LEARNER/码已绑定A | B提交同码 | 提示已用及客服入口 | 原绑定不变、无第二权益 | 重复/越权 | 自动化+审计 |
| AC-LEARN-001 | ROLE-LEARNER/权益有效 | 完成有效学习单元 | 进度和结果可见 | 合法学习证据写入 | 无权益/重复事件 | 事件+记录 |

> 第四部分：工程与 AI Coding 附录

## 附录 A：全局字段字典

| FLD | 含义 | 类型 | 来源 | 编辑权 | 校验 | 敏感/展示 |
|---|---|---|---|---|---|---|
| FLD-COURSE-NAME | 课程名称 | string | 内容管理员 | 草稿期 ROLE-CONTENT-ADMIN | 去空格后 1..100 | internal/原文 |
| FLD-COURSE-VERSION | 不可变课程版本 | string | 发布服务 | 系统只写 | 同课程单调递增且唯一 | internal/原文 |
| FLD-AUTH-QUOTA | 可授权剩余额度 | integer | 授权台账 | 授权事务扣减 | 非负且不得超额 | restricted/整数 |
| FLD-CODE-VALUE | 学习码标识 | string | 码服务 | 生成后不可改 | 唯一、有效期内、未核销 | secret/默认掩码 |
| FLD-LEARNING-PROGRESS | 学习进度 | decimal | 学习事件汇总 | 系统只写 | 0..100，按事件幂等 | personal/百分比 |

其余字段见同一 Product Truth；Coding Agent 不得新增同义字段。

## 附录 B：规则与状态机

下表规则与 STM 是发布、授权、激活、权益和学习的状态权威。

| RULE ID | 服务端守卫 | 失败行为 |
|---|---|---|
| RULE-COURSE-COMPLETE-001 | 名称/资源/知识点/考核/版本完整 | 阻断并定位缺项 |
| RULE-AUTH-SCOPE-001 | 组织可管、额度足、授权扣减原子 | 阻断、余额不变并审计 |
| RULE-CODE-VALID-001 | 未过期/激活/撤销且授权有效 | 不生成权益并说明原因 |
| RULE-ENTITLEMENT-ACTIVE-001 | 仅有效权益计入证据 | 无效事件阻断或复核 |

| STM | 当前状态 | 动作/允许角色与守卫 | 下一状态 | 事件/审计 | 非法转换结果 |
|---|---|---|---|---|---|
| STM-COURSE-001 | draft | ACT-COURSE-PUBLISH / ROLE-CONTENT-ADMIN / 完整性通过 | published | EVT-COURSE-PUBLISHED | 拒绝并保留 draft |
| STM-AUTH-001 | pending | ACT-AUTH-GRANT / ROLE-CONTENT-ADMIN / 额度充足 | active | EVT-AUTH-GRANTED | 拒绝且余额不变 |
| STM-CODE-001 | unused | ACT-CODE-ACTIVATE / ROLE-LEARNER / 码与授权有效 | activated | EVT-CODE-ACTIVATED | 返回首次结果或拒绝 |
| STM-ENTITLEMENT-001 | active | 到期/撤销/迁移；权益守卫 | expired/revoked/migrated | 权益审计 | 原状态并复核 |
| STM-LEARNING-001 | in_progress | ACT-LEARNING-COMPLETE；有效权益 | completed | EVT-LEARNING-UPDATED | 拒绝或幂等返回 |

## 附录 C：API、事件与集成业务契约

API 不适用：路径由技术设计。业务契约保留身份、版本、幂等键、对象状态、错误，以及 EVT-COURSE-PUBLISHED、EVT-AUTH-GRANTED、EVT-CODE-ACTIVATED、EVT-LEARNING-UPDATED 的载荷和对账语义。

## 附录 D：机器可读验收

每条 AC 的 `preconditions`、`steps`、`expected_visible`、`expected_domain`、`negative_cases`、`evidence_required` 由 Product Truth acceptance 导出；摘要不替代步骤。

## 附录 E：双向追溯矩阵

| REQ | 行为 | AC | 反向追溯 |
|---|---|---|---|
| REQ-CONTENT-PUBLISH-001 | FLOW-PUBLISH-001 / ACT-COURSE-PUBLISH | AC-PUBLISH-001 | AC → REQ → SRC-PUBLISHING-REQ-001 |
| REQ-CHANNEL-AUTH-001 | FLOW-AUTH-001 / ACT-AUTH-GRANT | AC-AUTH-001 | AC → REQ → SRC-PUBLISHING-REQ-001 |
| REQ-CODE-ACTIVATE-001 | FLOW-ACTIVATE-001 / ACT-CODE-ACTIVATE | AC-ACTIVATE-001 | AC → REQ → SRC-PUBLISHING-REQ-001 |
| REQ-LEARNING-EVIDENCE-001 | FLOW-LEARN-001 / ACT-LEARNING-COMPLETE | AC-LEARN-001 | AC → REQ → SRC-PUBLISHING-REQ-001 |

## 附录 F：禁止推断清单

禁止推断新角色、越级授权、同码多学员、已发布版本原地修改、无权益计入正式学时、
第三方支付和法定证书签发。技术框架、数据库、文件和任务由下游技术方案决定。
