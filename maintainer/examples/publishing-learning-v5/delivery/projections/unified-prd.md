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

基线版本 `1.0`，状态 `baselined`。批准材料优先于方案和原型。任何修改必须建立
`CHG-*` 并完成影响、diff、审批、同步和回归。

### 0.1 任务式阅读导航

客户先读摘要、范围、角色旅程与验收；前端、后端和测试按 `MOD-*` 读取模块纵向切片，
再通过附录定位字段、状态、API 和 AC；Coding Agent 只实现指定 ID，不跳过正文猜业务。

### 0.2 30 秒摘要

内容管理员发布不可变课程版本并授权渠道；渠道在额度内交付学习码；学员激活后获得
唯一权益并形成学习证据。发布、授权、激活和学习任一步失败都不得伪造下游成功状态，
最终由 ROLE-QA-ACCEPTOR 按 AC 和审计证据验收。本期不含支付结算和法定证书签发。

## 1. 背景、目标与成功指标

内容方将资源、知识点和题目形成不可变课程版本；渠道在授权额度内分发；学员凭
合法学习码获得权益并形成可追溯学习证据。有效学习码激活成功率按
`METRIC-ACTIVATION-001` 的口径验收。

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

ROLE-CONTENT-ADMIN 在 FLOW-PUBLISH-001 中进入 VIEW-COURSE-EDITOR 完成课程并执行
ACT-COURSE-PUBLISH；随后在 FLOW-AUTH-001 的 VIEW-AUTH-CONSOLE 执行 ACT-AUTH-GRANT。
ROLE-CHANNEL-ADMIN 取得额度后向
学员交付学习码。ROLE-LEARNER 在 VIEW-CODE-ACTIVATE 执行 ACT-CODE-ACTIVATE，
进入 VIEW-LEARNING-HOME 完成 ACT-LEARNING-COMPLETE。ROLE-QA-ACCEPTOR 最终按
所有 AC 核验证据，流程才闭环。
任一角色遇到越权、失效码或上游不可用时，页面显示原因并保持已确认数据；恢复条件
满足后从原台账重试，不允许绕过守卫制造下游成功结果。

## 5. 业务流程与状态

主链路为 `FLOW-PUBLISH-001 → FLOW-AUTH-001 → FLOW-ACTIVATE-001 → FLOW-LEARN-001`。
课程发布后不可原地修改；授权必须原子扣减额度；码只允许合法首次绑定；学习事件
只有在权益有效时才计入正式证据。任一步失败不得伪造下游成功状态。

## 6. 功能总览与信息架构

| 模块 | 页面 | 核心动作 | 领域结果 |
|---|---|---|---|
| MOD-CONTENT-001 | VIEW-COURSE-EDITOR | ACT-COURSE-PUBLISH | 课程快照发布 |
| MOD-AUTH-001 | VIEW-AUTH-CONSOLE | ACT-AUTH-GRANT | 授权创建且额度扣减 |
| MOD-LEARNING-001 | VIEW-CODE-ACTIVATE | ACT-CODE-ACTIVATE | 码绑定并创建权益 |
| MOD-LEARNING-001 | VIEW-LEARNING-HOME | ACT-LEARNING-COMPLETE | 学习事件和证据写入 |

## 7. 分模块功能需求

### 7.1 内容编排与发布 MOD-CONTENT-001

资源、知识点和题目组成课程；发布前检查完整性。发布成功显示版本和快照摘要，
形成 EVT-COURSE-PUBLISHED。失败时课程保持草稿并显示缺失项。
模块目标是发布不可变课程，边界是不负责授权和学习；ROLE-CONTENT-ADMIN 从
VIEW-COURSE-EDITOR 入口进入，前置为草稿完整，成功结果为版本快照。主路径执行
FLOW-PUBLISH-001 / ACT-COURSE-PUBLISH；异常时保留输入并恢复到草稿重试。
FLD-COURSE-NAME 数据来源为内容管理员，权限仅限草稿期；RULE-COURSE-COMPLETE-001
与 STM-COURSE-001 守卫发布并产生 EVT-COURSE-PUBLISHED。模块指标不适用，
数据质量以快照字段完整且版本唯一核对。AC-PUBLISH-001 验收；无未决项。

### 7.2 授权与学习码 MOD-AUTH-001

授权校验组织、范围和剩余额度。超额时 AC-AUTH-OVERLIMIT-001 要求授权记录和余额
均不变化。成功产生 EVT-AUTH-GRANTED。
模块目标是在额度内授权，边界是不负责线下分发；ROLE-CONTENT-ADMIN 从
VIEW-AUTH-CONSOLE 入口进入，前置为组织有效且额度充足，成功结果为授权和余额同步更新。
主路径执行 FLOW-AUTH-001 / ACT-AUTH-GRANT；异常时零写入并返回台账恢复重试。
FLD-AUTH-QUOTA 来源为授权台账，权限由服务端守卫；RULE-AUTH-SCOPE-001 与
STM-AUTH-001 产生 EVT-AUTH-GRANTED，并通过 INT-ORG-MASTER-001 对账。模块指标不适用，
数据质量以余额非负和授权事务一致核对。AC-AUTH-001 验收；无未决项。

### 7.3 激活、学习与证据 MOD-LEARNING-001

码必须有效、未使用且授权链有效。重复激活保留首次绑定，不生成第二份权益。
弱网重试按学员、任务和完成版本幂等处理。
模块目标是让 ROLE-LEARNER 从 VIEW-CODE-ACTIVATE 入口激活并在 VIEW-LEARNING-HOME
完成学习；边界是不签发法定证书，前置为码与授权有效，成功结果为唯一权益和学习证据。
主路径执行 FLOW-ACTIVATE-001 / FLOW-LEARN-001、ACT-CODE-ACTIVATE 与
ACT-LEARNING-COMPLETE；失效、重复或弱网异常返回明确原因并按幂等键恢复。
FLD-CODE-VALUE 和 FLD-LEARNING-PROGRESS 分别来自码服务和事件汇总，权限仅限本人；
RULE-CODE-VALID-001、STM-CODE-001 和 STM-LEARNING-001 产生 EVT-CODE-ACTIVATED、
EVT-LEARNING-UPDATED。METRIC-ACTIVATION-001 按唯一激活请求去重并每日刷新，数据质量
通过权益与事件对账。AC-ACTIVATE-001、AC-LEARN-001 验收；无未决项。

### 7.4 关键动作合同

| ACT | 角色/前置 | 可见结果 | 领域结果 | 失败/恢复 | 审计/事件 | AC |
|---|---|---|---|---|---|---|
| ACT-COURSE-PUBLISH | ROLE-CONTENT-ADMIN/草稿完整 | 版本与快照摘要 | 新不可变课程版本 | 显示缺失项并保留草稿 | EVT-COURSE-PUBLISHED | AC-PUBLISH-001 |
| ACT-AUTH-GRANT | ROLE-CONTENT-ADMIN/额度充足 | 授权与余额刷新 | 原子创建授权并扣减 | 超额时零写入并返回台账 | EVT-AUTH-GRANTED | AC-AUTH-001 |
| ACT-CODE-ACTIVATE | ROLE-LEARNER/码与授权有效 | 学习入口可见 | 生成唯一权益 | 失效/重复时显示首次结果或拒绝 | EVT-CODE-ACTIVATED | AC-ACTIVATE-001 |
| ACT-LEARNING-COMPLETE | ROLE-LEARNER/权益有效 | 进度完成可见 | 写入一份学习证据 | 弱网按幂等键重试 | EVT-LEARNING-UPDATED | AC-LEARN-001 |

## 8. 数据与接口流转

INT-ORG-MASTER-001 是组织主数据权威来源；不可用时禁止新增授权，既有数据只读，
恢复后对账。具体接口方法/路径由下游技术方案确认，本需求固定组织映射、权限、
失败降级、幂等和对账结果。

## 9. 非功能、安全与合规

学习身份属于受限数据；渠道隔离、服务端授权守卫、状态审计和证据留存必须可验收。
容量与性能目标由试点规模确认，不凭模板虚构数字。

## 10. 验收方案

| AC | 角色/前置 | 步骤/输入 | 可见结果 | 领域结果 | 反例 | 证据 |
|---|---|---|---|---|---|---|
| AC-PUBLISH-001 | ROLE-CONTENT-ADMIN/草稿完整 | 提交课程发布 | 版本与快照可见 | 发布不可变版本 | 缺资源/重复请求 | 截图+审计 |
| AC-AUTH-001 | ROLE-CONTENT-ADMIN/额度充足 | 选择组织、范围和数量 | 新授权和余额可见 | 原子创建/扣减 | 超额/越权 | API+审计 |
| AC-ACTIVATE-001 | ROLE-LEARNER/码有效 | 提交码与身份 | 课程入口可见 | 唯一权益生成 | 失效/重复/越权 | UI+领域记录 |
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

其余字段的完整定义在同一 Product Truth 基线中；Coding Agent 不得新增同义字段。

## 附录 B：规则与状态机

RULE-COURSE-COMPLETE-001、RULE-AUTH-SCOPE-001、RULE-CODE-VALID-001、
RULE-ENTITLEMENT-ACTIVE-001 分别约束发布、授权、激活和学习。STM-COURSE-001、
STM-AUTH-001、STM-CODE-001、STM-ENTITLEMENT-001、STM-LEARNING-001 是状态权威。

| STM | 当前状态 | 动作/允许角色与守卫 | 下一状态 | 事件/审计 | 非法转换结果 |
|---|---|---|---|---|---|
| STM-COURSE-001 | draft | ACT-COURSE-PUBLISH / ROLE-CONTENT-ADMIN / 完整性通过 | published | EVT-COURSE-PUBLISHED | 拒绝并保留 draft |
| STM-AUTH-001 | pending | ACT-AUTH-GRANT / ROLE-CONTENT-ADMIN / 额度充足 | active | EVT-AUTH-GRANTED | 拒绝且余额不变 |
| STM-CODE-001 | unused | ACT-CODE-ACTIVATE / ROLE-LEARNER / 码与授权有效 | activated | EVT-CODE-ACTIVATED | 返回首次结果或拒绝 |

## 附录 C：API、事件与集成业务契约

API 路径本例不适用：仓库基线未提供，路径由下游技术设计。业务契约必须保留请求
身份/版本/幂等键、成功响应的对象与状态、权限/额度/冲突错误，以及
EVT-COURSE-PUBLISHED、EVT-AUTH-GRANTED、EVT-CODE-ACTIVATED、
EVT-LEARNING-UPDATED 的版本化载荷和对账语义。

## 附录 D：机器可读验收

每条 AC 均包含 `preconditions`、`steps`、`expected_visible`、`expected_domain`、
`negative_cases` 和 `evidence_required`。详表由 Product Truth 的 acceptance 节导出；
不得用本文中的摘要替代具体步骤。

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
