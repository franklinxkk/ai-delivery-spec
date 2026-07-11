# 融合出版与学习服务交付 — Human-First Projection

> Generated from `../truth/product-truth.yaml`, schema 5.0.0. This projection
> demonstrates navigation and traceability; Product Truth remains authoritative.

## 1. 交付目标

内容管理员将资源、知识点、题目发布为不可变课程版本；渠道在授权额度内
分配资源；学员通过合法学习码获得权益并形成可按课程版本、渠道、批次和
学员追溯的学习证据。

主链路：`FLOW-PUBLISH-001 → FLOW-AUTH-001 → FLOW-ACTIVATE-001 → FLOW-LEARN-001`。

## 2. 页面与操作闭环

| Feature | 页面 | 核心操作 | 点击后可见结果 | 领域结果 | 验收 |
|---|---|---|---|---|---|
| `FEAT-CONTENT-PUBLISH-001` | `VIEW-COURSE-EDITOR` | `ACT-COURSE-PUBLISH` | 发布状态、版本号、快照摘要 | 冻结课程版本并发布事件 | `AC-PUBLISH-001` |
| `FEAT-CHANNEL-AUTH-001` | `VIEW-AUTH-CONSOLE` | `ACT-AUTH-GRANT` | 新授权和剩余额度 | 原子创建授权、扣减额度 | `AC-AUTH-001` |
| `FEAT-CODE-ACTIVATE-001` | `VIEW-CODE-ACTIVATE` | `ACT-CODE-ACTIVATE` | 课程卡片和学习入口 | 绑定学习码并生成权益 | `AC-ACTIVATE-001` |
| `FEAT-LEARNING-EVIDENCE-001` | `VIEW-LEARNING-HOME` | `ACT-LEARNING-COMPLETE` | 任务状态、进度、结果 | 写入学习事件和验收证据 | `AC-LEARN-001` |

## 3. 关键业务约束

- `RULE-COURSE-COMPLETE-001`：不完整课程不能发布。
- `RULE-AUTH-SCOPE-001`：不可越级、超额或非原子授权。
- `RULE-CODE-VALID-001`：学习码必须有效、未使用且授权链有效。
- `RULE-ENTITLEMENT-ACTIVE-001`：无有效权益的事件不计入正式学习证据。

## 4. 关键异常

- 超额授权：`AC-AUTH-OVERLIMIT-001`，记录和余额均不变化。
- 重复激活：`AC-ACTIVATE-DUPLICATE-001`，原绑定不变化且不生成第二份权益。
- 组织主数据不可用：禁止新增授权，已有数据只读，恢复后对账。
- 学习事件重复或弱网重试：按学员、任务和完成版本幂等处理。

## 5. 当前验证状态

Product Truth 可进行 Schema 和引用闭合验证。浏览器、Coding Agent、QA、
客户验收和领域专家行为证据尚未运行，因此本样例不得宣称生产验证通过。
