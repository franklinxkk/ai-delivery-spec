---
name: ai-delivery-spec
description: 用于任何新增、修改、评审、反推或验收需求、PRD、原型、竞品材料与存量系统，包括写/改一个小功能、加字段/列/页签/下拉、在旧 HTML 或系统上小改、直接生成 PRD 或原型。无论规模和清晰度，命中这些需求工作时都必须先调用，不得以“功能简单”“需求明确”或“直接改更快”跳过；调用后按目标阶段交付最小但完整、可评审、可实施、可追溯、可验收的人类与 Coding Agent 共用产物。支持问题定义、方案探索、需求准入、澄清、统一 PRD、工程原型、评审基线、变更影响和验收证据；不负责排期、编码、CI/CD、部署和运营。
---

# AI Delivery Spec 5.4.3 — Fast Convergence Workstations｜精准收敛的需求工作站

本 Skill 是适用于 ToC/ToB/ToG 的 Requirement Management Kernel：让业务、产品、设计、前后端、架构、需求交付/技术负责人、测试、合规和 Coding Agent 在需求任一阶段进入，得到当前需要的最小合格产物后离开；也可在用户明确要求时持续完成端到端闭环。

默认跟随用户当前语言生成标题、正文、表格、问题与测试；稳定 ID、代码、API/字段名和专有名词保持原样。双语必须由用户明确要求。
只使用 Agent 完成需求工作不要求安装 Python；运行本地零模型门禁时需要 Python 3.10+：`python -m pip install -r scripts/requirements.txt`。Stable ID 是长期不变的需求编号；Gate 是静态结构门禁，不等于业务、浏览器、实现或客户验收。

## 先确定进入点和停止点

内部识别两个字段，不要求用户学习参数：

- `entry_stage`：从现有材料和当前工作位置进入。
- `target_stage`：本次要拿到的产物/停止点。

工作站为 `frame → explore → intake → clarify → specify → review → baseline`，基线可进入 `change` 或 `acceptance`，变更须重新基线。`frame/explore` 是准入前工作区；正式 `REQ-*` 生命周期从 intake 开始。用户可从任意有证据的阶段进入，不强迫补跑无关前序。

阶段是路由地图，不是执行清单。显式目标最高优先；“不要写 PRD，只做澄清”等否定约束高于关键词。目标清楚时直接进入目标阶段，不补做前序文件；目标模糊时先在一轮内完成“发散选项 → 推荐聚焦 → 深化关键链路”，再只问会改变范围的决策。单次任务到目标即停，明确端到端任务则持续到目标且不得把中间模板或静态 PASS 当成完成。

需要跨会话或检查旧产物时才运行确定性路由；它不解析自然语言：

`python scripts/ai_delivery_spec_cli.py route-stage --target <stage> --artifact <path>`

## 每次只加载一个有效切片

| 当前任务 | 只读取 |
|---|---|
| 任意阶段进入/停止、角色交接、断点 | `references/stages.md` |
| 来源盘点、问题发现、竞品/现状研究 | `references/discover.md` |
| 正式生命周期、准入、评审、基线 | `references/lifecycle.md` |
| PRD、字段、规则、指标、接口、机器附录 | `references/specify.md` |
| 页面合同、Stage 0、原型、视觉路线 | `references/prototype.md` |
| 变更、双向追溯、验收结果 | `references/change-acceptance.md` |
| 大输入、ID 切片、检查点、Agent 工作区 | `references/context.md` |
| Coding/需求协作工具投影 | `references/tool-adapters.md` |
| 故障恢复、FAQ、反模式 | `references/troubleshooting.md` |
| 领域证据 | `scripts/query_domain.py --domain <pack> --section "<heading>"` |
| 私有领域/模板/规则 | `init-custom --sharing local|team`；候选知识用 `candidate record-usage/assess`，只人工晋级 |

一次只加载当前阶段参考、一个精确领域章节和当前 ID 切片。不要加载 README、`maintainer/`、全模板/示例/领域包或整个仓库。frame/explore 仅在法规、安全或行业物理约束会改变选项时加载领域知识。

## 默认最小产物，不为阶段机械建文件

实时对话先交付可用判断，不展示内部 YAML、稳定 ID 或工作站术语；只有需要保存、跨会话、跨角色交接、审计或工具校验时才结构化落盘。

- frame：一份 `problem-brief.md`，说清用户、痛点时刻、成功信号、事实/假设和下一步。
- explore：一份 `solution-sketch.md`，至少两个选项和不做选项，包含可证伪 `ASM-*`、最小验证与停止条件。
- intake：复用 triage 结果与 requirement register；Start with intake for formal governed requirements。
- clarify：一份 `requirement-brief.md`，内嵌 `DEC-*`、规则、开放 `UNK-*` 和退路；多决策人/审计才拆侧车。
- specify：一份需求卡或 one human-readable 统一 PRD；Product Truth 只在受控多投影、反复跨模块变更、血缘或强审计时按需启用。
- review/baseline：复用同一规格；`required_review_types` 全部结构化签署后绑定权威来源、版本/hash 和消费方。
- change/acceptance：现有 `CHG-*` 与 `ARUN-*` 回链当前基线。

假设寄存器仅在跨会话、跨角色复用或治理时单独导出。YAML/JSON 是工具投影，不是另一份 PRD。

## 小迭代先最小改动，再补必要合同

- 用户只要求分析/评审时，给结论、最小范围、阻断未知和核心验收，不擅自产出整套 PRD、治理台账或新平台能力。
- 用户要求修改存量产物时，先完成可比较的目标产物；Stage 0、ID 和检查账本默认留在工作过程，最终只报告影响决策的差异。
- 未经证据或用户授权，不新增角色、页面、实体、审批、审计、版本、并发、指标或状态机。必要的安全/合规约束单列为阻断，不混入本期范围。
- “示例子集”不能替代“修改/替换存量原型”。除非用户明确批准缩减范围，必须保留未变更的视图、字段、动作、状态、角色路径和代表性数据量；不能完整保留时返回 `BLOCKED`，不得包装成完成。
- 外部数据集成先写清 `权威源 → 汇聚/转换方 → 消费方`、读写方向、触发、失败与纠错责任，再设计按钮、队列和自动化；反向同步不得进入正向上报队列。

## 需求闭环与禁止推断

1. 先检查用户材料、现有产物、权威层级和适用领域；存量 HTML/系统重写前先执行 Stage 0。
2. 事实问题按依赖成批澄清；方向、冲突和路线逐项给出推荐、依据与取舍。无法取得的事实登记 `UNK-*`，包含责任人、范围、`blocks_stage` 和回退路径。
3. `ASM-*` 是待验证解释；`UNK-*` 是缺失事实/决策。两者不得互换。P0 未知项只阻断受影响且已到达的阶段。
4. 规格按模块纵切闭环：目标 → 角色旅程 → 页面/数据 → 规则/状态 → 指标口径 → 异常恢复 → 验收；横切权限、接口、事件、审计、兼容和 NFR 作为同一基线合同。
5. 每个 `REQ-*` 绑定来源、行为、字段/规则、AC、测试与证据，并支持 both directions 追溯；缺少语义时开发与 Agent 必须回报 GAP，不能发明。
6. 评审后才基线；变更必须登记 diff、影响、审批、同步、回归和版本；验收记录执行结果、证据、缺陷、条件和签署。

## 门禁只做轻量守门员

统一状态只有 `PASS`、`REVIEW_COMPLETE_WITH_GAPS`、`BLOCKED_BY_P0_UNKNOWN`、`BLOCKED`。早期阶段：

```bash
python scripts/ai_delivery_spec_cli.py gate --profile frame --artifact problem-brief.md
python scripts/ai_delivery_spec_cli.py gate --profile explore --artifact solution-sketch.md
python scripts/ai_delivery_spec_cli.py gate --profile clarify --artifact requirement-brief.md
```

正式规格沿用 `gate --profile requirement|prd|prototype|handoff|full`。静态门禁只在目标里程碑运行一次；修复后重跑，不在每个经过的工作站重复执行。默认按根因分组输出诊断，JSON 保留全部明细。门禁必须输出 `not_proven`，不能把结构通过宣传为领域正确、真实运行或客户签收。单产物 PASS 不等于交付闭环；宣称最终完成前必须 `gate --profile full`（或 handoff）组合门禁通过。

5.4 模板用语言无关的 `<!-- ADS:* -->` 锚点，标题可按团队语言/模板改变。`resume_context` 记录相对路径、阶段和 SHA-256；漂移、缺失和路径越界必须阻断。大项目仍用执行检查点和 ID Slice，产物断点不能替代执行状态。

## 边界与扩展

`schemas/agent-handoff.schema.json` 只把已基线需求投影给 Coding Agent；`schemas/domain-candidate.schema.json` 只登记本地候选知识。私有扩展优先于官方默认，但绑定规则冲突必须形成 `DEC-CONFLICT-*`，禁止静默覆盖或联网外发。

研发排期、Sprint/任务、代码生成、CI/CD、部署、监控和运营属于下游系统。本 Skill 管到需求验收；外部状态只记引用，线上反馈以新来源回流 intake/CHG，并保留人类问责。
