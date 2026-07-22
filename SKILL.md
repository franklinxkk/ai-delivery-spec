---
name: ai-delivery-spec
description: 将一句话想法、客户材料、存量系统以及 ToC/ToB/ToG 需求转化为一份可实施、可追溯、可验收的人类与 Coding Agent 共用基线；用于需求准入、澄清、统一 PRD、工程原型、变更影响、Agent 交接与验收证据。Turn ideas, customer materials and brownfield systems into an implementable requirement baseline. 不负责排期、编码、CI/CD、部署和运营。
---

# AI Delivery Spec 5.3.3 — Requirement Management Kernel｜需求管理内核

生成一份人类可读、AI Coding 可执行的需求基线，并双向追溯“来源 → 行为 → 验收”。
Product Truth（结构化事实源）只在复杂治理场景按需启用，不是每个项目的前置作业。

输出语言默认跟随用户当前请求。标题、正文、表格、问题和测试均使用该语言；
稳定 ID、代码、API/字段名及专有名词保持不变。双语输出必须由用户明确要求。

首次运行需要 Python 3.10+：`python -m pip install -r scripts/requirements.txt`。
Stable ID 是长期不变的需求编号；Gate 是结构门禁，不等于业务、浏览器或客户验收。

## 静默完成需求准入

内部判断两个轴，仅在有助于决策或用户主动指定时展示：

- `delivery_shape`：`requirement_card`、`unified_prd` 或 `governed_truth`；
- `assurance_profile`：`bounded`、`standard`、`high_risk` 或 `safety_critical`。

只有单角色、可逆、局部变更才使用需求卡。数据上报/统计、实质状态、批量导入导出、
审批审计、系统集成、迁移、高风险或跨角色/模块需求必须升级为一份统一 PRD。
只有受控多投影、反复跨模块耦合、数据血缘或强审计才启用 governed truth。
L0—L4 是门禁强度元数据，不要求用户先学习或手工选择。

先检查现有材料和对应领域章节。互不依赖的事实问题成批询问；方向、冲突和路线决策
逐项询问，并给出推荐、证据和取舍。暂时无法取得的事实登记为有责任人、有范围、
有回退路径和 `blocks_stage` 的 `UNK-*`。P0/P1 未明确处置前不得进入正式规格阶段。

## 每次只加载一个有效切片

| 当前任务 | 读取内容 |
|---|---|
| 准入、阶段、角色、基线 | `references/lifecycle.md` |
| 一句话想法、来源、竞品、存量盘点 | `references/discover.md` |
| PRD、字段、规则、接口、机器附录 | `references/specify.md` |
| 页面合同、Stage 0、原型、视觉路线 | `references/prototype.md` |
| 变更、追溯、验收结果 | `references/change-acceptance.md` |
| 大输入、组合、检查点、Agent 工作包 | `references/context.md` |
| Coding 工具投影 | `references/tool-adapters.md` |
| 故障恢复、FAQ、反模式 | `references/troubleshooting.md` |
| 领域证据 | `scripts/query_domain.py --domain <pack> --section "<heading>"` |
| 私有领域/模板/规则 | `init-custom --sharing local|team`；候选知识用 `candidate record-usage/assess`，只人工晋级 |

一次只加载一个阶段参考和一个精确领域章节。不要加载 README、`maintainer/`、全部
模板/示例/领域包或整个仓库；只有触发时才加载可选模式。

## 执行需求闭环

```text
准入 → 澄清 → 规格 → 评审 → 基线 → 变更 → 验收 → 关闭
```

1. 将每个 `REQ-*` 绑定来源、目标、范围、责任人和验收。
2. 闭合角色与范围、业务流、状态、规则、字段、异常、指标和禁止项。
3. 只交付一份 PRD：30 秒摘要、按任务阅读地图、模块纵切规格、横切合同和工程/AI索引。
4. 用业务、产品、领域、UX、前后端、架构、QA、合规和客户视角评审，保留显式 `REV/UNK`。
5. 固化版本、权威、稳定 ID 和审批；来源冲突必须由 `DEC-CONFLICT-*` 裁决。
6. `CHG-*` 双向遍历受影响对象，同步全部投影并执行回归。
7. 每个强制 `AC-*` 记录真实结果、可解析证据和有责任主体的签署。

## 坚守“不猜业务”合同

- 稳定 ID 覆盖来源/决策/未知项、行为/数据、接口和证据。
- 每个角色必须走到成功、授权拒绝、可恢复失败或明确交接。
- 每个模块纵切就近放置目标、旅程、UI/数据、规则/权限、状态/事件、指标、恢复、
  验收和未知项；附录只索引同一组 ID，不改写业务含义。
- 每个动作声明角色、前置条件、输入、可见结果、领域结果、状态/审计、失败恢复和 AC；
  状态声明起点、终点、触发器、责任人和非法路径。
- 每个指标在对应页面旁声明统计对象、公式、时间/过滤/去重、来源/时效、零值/空值和格式；
  每条跨模块流程至少有一个 E2E AC。
- 每个页面声明 `primary`、`layout`、适用 `surfaces`、条件字段/动作/API/AC 和稳定原型锚点。
- L3 基线声明验收责任人、范围、通过规则、证据和签署角色；复杂原型必须有 `REG-*`
  区域锚点和真实浏览器 `ARUN-*`。
- 本地多文件原型允许相对 HTML/CSS/JS 依赖，门禁会一并扫描；远程或越界依赖不得伪装成已证明。
- ARUN 的本地证据必须真实存在；`EVD-*` 必须在同一记录的 `evidence_catalog` 中解析。
- 高风险规则绑定 `SRC/DEC/ASSUMPTION`；只有真实存在 AI 或血缘行为时才加载对应合同。
- Coding Agent 只能实现已固化的 ID 切片。缺少工程基线是交接 GAP，不是让 PRD 编造技术方案。

覆盖旧原型或 PRD 前，Stage 0 必须把观察到的合同标为 `confirmed`、`inferred`、
`unknown` 或 `defect_candidate`，并完成 `INV-* → REQ-*` 映射；推断项进入有责任人的
`RBATCH-*` 批次确认。不得从原型猜测 API、指标、权限或法律结论。

## 控制大项目上下文与知识回流

输入超过 8 个文件、50 万可解析字符，或盘点发现 ≥8 模块、≥12 页面、≥200 稳定对象时
自动分轮。先冻结来源，再按角色端到端纵切建立检查点，最后闭合跨模块边。
知识候选使用 `schemas/domain-candidate.schema.json`，默认仅限 `project_only`。每次采用、修改、
拒绝或失效都以 `candidate record-usage` 留证；`candidate assess` 只给人工评审建议，永不自动晋级。

长任务可依据 `schemas/agent-handoff.schema.json` 投影 `AGENTS.md`。工作包绑定基线 hash、
责任人、范围和 AC，不能修改需求真相。`XCT-*` 还必须声明影响模块、全局不变量、
执行点、例外与失败处理。

## 最后只跑一次轻量门禁

```bash
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd PRD.md --level auto
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html --level auto
python scripts/ai_delivery_spec_cli.py gate --profile handoff --prd PRD.md --prototype admin.html --manifest handoff-manifest.yaml --level auto
```

零 LLM、单遍读取的门禁只负责诊断。先修第一个 Finding，再执行 RETRY；它不会自动改写需求。
静态 PASS 永远不能替代领域评审、浏览器/QA 或客户验收。`auto` 对 PRD 读取 frontmatter，
对原型和 handoff 默认 L2；L3/L4 缺少可解析的浏览器 ARUN 时必须返回缺口。
最终状态只能是 `PASS`、`REVIEW_COMPLETE_WITH_GAPS`、`BLOCKED_BY_P0_UNKNOWN` 或 `BLOCKED`。

对用户已授权的长任务，持续完成全部约定交付物和门禁；仅在需要改变范围的用户决策、
权威来源不可获得或当前阶段被 P0 未知项阻断时暂停。
