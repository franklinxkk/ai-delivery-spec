# 融合出版与学习服务需求规格说明书

> 这是客户、产品、传统开发、测试与 Coding Agent 共用的一份 PRD。大型示例的
> 结构化权威层是 `../truth/product-truth.yaml`（Product Truth 5.1.0）；本文是唯一
> 人类阅读基线，不维护两套 PRD。

## 0. 文档控制与来源优先级

基线版本 `1.0`，状态 `baselined`。批准材料优先于方案和原型。任何修改必须建立
`CHG-*` 并完成影响、diff、审批、同步和回归。

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

ROLE-CONTENT-ADMIN 在 VIEW-COURSE-EDITOR 完成课程并执行 ACT-COURSE-PUBLISH；
随后在 VIEW-AUTH-CONSOLE 执行 ACT-AUTH-GRANT。ROLE-CHANNEL-ADMIN 取得额度后向
学员交付学习码。ROLE-LEARNER 在 VIEW-CODE-ACTIVATE 执行 ACT-CODE-ACTIVATE，
进入 VIEW-LEARNING-HOME 完成 ACT-LEARNING-COMPLETE。ROLE-QA-ACCEPTOR 最终按
所有 AC 核验证据，流程才闭环。

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

### 7.1 内容编排与发布

资源、知识点和题目组成课程；发布前检查完整性。发布成功显示版本和快照摘要，
形成 EVT-COURSE-PUBLISHED。失败时课程保持草稿并显示缺失项。

### 7.2 授权与学习码

授权校验组织、范围和剩余额度。超额时 AC-AUTH-OVERLIMIT-001 要求授权记录和余额
均不变化。成功产生 EVT-AUTH-GRANTED。

### 7.3 激活、学习与证据

码必须有效、未使用且授权链有效。重复激活保留首次绑定，不生成第二份权益。
弱网重试按学员、任务和完成版本幂等处理。

## 8. 数据与接口流转

INT-ORG-MASTER-001 是组织主数据权威来源；不可用时禁止新增授权，既有数据只读，
恢复后对账。具体接口方法/路径由下游技术方案确认，本需求固定组织映射、权限、
失败降级、幂等和对账结果。

## 9. 非功能、安全与合规

学习身份属于受限数据；渠道隔离、服务端授权守卫、状态审计和证据留存必须可验收。
容量与性能目标由试点规模确认，不凭模板虚构数字。

## 10. 验收方案

| AC | 角色/行为 | 可见结果 | 领域结果 | 证据 |
|---|---|---|---|---|
| AC-PUBLISH-001 | 发布课程 | 版本与快照可见 | 发布不可变版本 | 截图+审计 |
| AC-AUTH-001 | 额度内授权 | 新授权和余额可见 | 原子创建/扣减 | API+审计 |
| AC-ACTIVATE-001 | 首次激活 | 课程入口可见 | 唯一权益生成 | UI+领域记录 |
| AC-LEARN-001 | 完成学习 | 进度和结果可见 | 合法学习证据写入 | 事件+记录 |

> 第四部分：工程与 AI Coding 附录

## 附录 A：全局字段字典

FLD-COURSE-NAME、FLD-COURSE-VERSION、FLD-AUTH-QUOTA、FLD-AUTH-ORG、
FLD-CODE-VALUE、FLD-CODE-EXPIRES、FLD-ENTITLEMENT-LEARNER 和
FLD-LEARNING-PROGRESS 的含义、类型、来源、编辑权、校验和敏感级别以 Product Truth
为准，Coding Agent 不得新增同义字段。

## 附录 B：规则与状态机

RULE-COURSE-COMPLETE-001、RULE-AUTH-SCOPE-001、RULE-CODE-VALID-001、
RULE-ENTITLEMENT-ACTIVE-001 分别约束发布、授权、激活和学习。STM-COURSE-001、
STM-AUTH-001、STM-CODE-001、STM-ENTITLEMENT-001、STM-LEARNING-001 是状态权威。

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
