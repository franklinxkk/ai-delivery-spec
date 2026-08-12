---
name: ai-delivery-spec
description: Use for creating, changing, reviewing, reverse-engineering or accepting requirements, PRDs, prototypes, competitor material or existing systems, including any small UI/field/column/tab/dropdown/legacy-HTML change and direct PRD/prototype generation. Always invoke regardless of size or clarity. Deliver the smallest complete, reviewable, implementable, traceable and testable artifact at the target stage. Covers framing through acceptance; excludes scheduling, coding, CI/CD, deployment and operations. 中文：用于任何新增、修改、评审、反推或验收需求、PRD、原型、竞品或存量系统；写/改一个小功能、加字段/列/页签/下拉、旧 HTML 小改、直接生成 PRD/原型也必须调用。按目标阶段交付最小完整、可评审实施追溯验收的产物；不负责排期、编码、CI/CD、部署和运营。
---

# AI Delivery Spec 5.4.6 — Requirement Management Kernel｜人机共用需求管理内核

本 Skill 是适用于 ToC/ToB/ToG 的 Requirement Management Kernel：让业务、产品、设计、前后端、架构、需求交付/技术负责人、测试、合规和 Coding Agent 在需求任一阶段进入，得到当前需要的最小合格产物后离开；也可在用户明确要求时持续完成端到端闭环。

默认锁定用户指定语言；未指定时取任务起始主要语言并贯穿全生命周期，“继续”不重置。标题、正文、表格、问题、测试、图节点和可见状态同语；全英文不得泄露中文模板，中文交付不得把 Given/When/Then、draft、pending → resolved、lastCursor 等英文裸露为正文。人类可见状态/字段/事件/队列先写该语言含义，括号保留必要机器原值；稳定 ID、代码、API/字段名、Schema、公式不翻译。双语须明确要求。YAML/JSON 侧车可保留键名与枚举，但交付须附同语言摘要；门禁用 `--language auto|zh-CN|en-US`。
只使用 Agent 不要求 Python；零模型门禁需 Python 3.10+ 与 `scripts/requirements.txt`。Gate 只证明静态结构，不证明业务、浏览器、实现或客户验收。

## 默认选择最轻可行路径

Skill 始终命中但默认走最轻路径。明确、局部、可逆且不改变跨模块状态、外部数据权威、权限/指标、迁移、法规安全或高影响 AI 写回的单点变化，按**快速小改**处理。

快速小改默认行为：不新建生命周期文件、不展示 ID；只检查触达面并交付；短屏说明差异、约束、边界、正反验收和未证明事项，无未知则零澄清。交接/基线才持久化 ID 和门禁；升级只补风险合同。详见 `references/stages.md`。

## 先确定进入点和停止点

内部识别两个字段，不要求用户学习参数：

- `entry_stage`：从现有材料和当前工作位置进入。
- `target_stage`：本次要拿到的产物/停止点。

工作站为 `frame → explore → intake → clarify → specify → review → baseline`，基线可进入 `change` 或 `acceptance`，变更须重新基线。`frame/explore` 是准入前工作区；正式 `REQ-*` 生命周期从 intake 开始。用户可从任意有证据的阶段进入，不强迫补跑无关前序。

阶段是路由地图，不是执行清单。显式目标最高优先；“不要写 PRD，只做澄清”等否定约束高于关键词。目标清楚时直接进入目标阶段，不补做前序文件；目标模糊时先在一轮内完成“发散选项 → 推荐聚焦 → 深化关键链路”，再只问会改变范围的决策。一句话请求已明确要求原型时，澄清 P0/P1 范围决策并列出详细需求只是通往原型的必要工作，不是新的停止点；除非用户改变目标，必须继续到可操作产品原型。单次任务到目标即停，明确端到端任务则持续到目标且不得把中间模板或静态 PASS 当成完成。

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

细反例只进 `maintainer/` 脱敏回归，不注入运行上下文。仅按命中表面预检：指标口径/未知项、评审双向联动、分发投影、组合交接或 Stage 0；连续漏读时缩成单表面切片并过对应门禁，不降标准。

## 默认最小产物，不为阶段机械建文件

实时对话先交付可用判断，不展示内部 YAML、稳定 ID 或工作站术语；只有需要保存、跨会话、跨角色交接、审计或工具校验时才结构化落盘。

- frame：一份 `problem-brief.md`，说清用户、痛点时刻、成功信号、事实/假设和下一步。
- explore：一份 `solution-sketch.md`，至少两个选项和不做选项，包含可证伪 `ASM-*`、最小验证与停止条件。
- intake：复用准入分流结果与需求登记表；正式需求从需求准入开始。
- clarify：一份 `requirement-brief.md`，内嵌 `DEC-*`、规则、开放 `UNK-*` 和退路；多决策人/审计才拆侧车。
- specify：一份人类可读的需求卡或统一 PRD；Product Truth 只在受控多投影、反复跨模块变更、血缘或强审计时按需启用。
- review/baseline：复用同一规格；`required_review_types` 全部结构化签署后绑定权威来源、版本/hash 和消费方。
- change/acceptance：现有 `CHG-*` 与 `ARUN-*` 回链当前基线。

假设寄存器仅在跨会话、跨角色复用或治理时单独导出。YAML/JSON 是工具投影，不是另一份 PRD。

客户演示或客户确认阶段默认产品模式。只有用户明确要求“评审版/评审模式/编号标注/评审抽屉”才直接生成可见研发投影；“交开发/给前后端测试看/开需求评审会”只说明消费方，必须询问一次，未确认时继续产品模式。一句话需求首次进入原型且偏好未表达时也只问一次是否追加评审版；不阻断产品模式，明确“我要评审版”即已确认，拒绝后同一需求基线内不重复追问。review 工作站是多角色签署与缺口关闭，不等于原型评审模式。评审模式坚持“机器全量覆盖、人类克制投影”：全量合同进入 handoff；改变数据、状态、指标、责任方或系统边界的步骤形成 `STEP-*`，人类编号只保留关键共识、未知、口径和边界，一个编号可覆盖一个区域。角色镜头、来源、实施卡、核心流程图/状态转换图/数据流血缘图的完整合同见 `references/prototype.md`；Coding Agent 不把评审文案当机器合同。

L2/L3 PRD须用统一模板过门禁；评审投影不得替代。P0未知应阻断，结构不全不得称可开发。

来源超过 100KB、涉及三个以上重型 HTML/Axure 页面或横跨多视图时，同时加载 `references/context.md` 与 `references/prototype.md`，先建来源/页面/动作清单再按稳定 ID 切片。评审模式已确认且有三个以上重型页面时才使用单页懒加载评审容器；材料重不自动加评审壳。

## 小迭代先最小改动，再补必要合同

- 用户只要求分析/评审时，给结论、最小范围、阻断未知和核心验收，不擅自产出整套 PRD、治理台账或新平台能力。
- 用户要求修改存量产物时，先完成可比较的目标产物；Stage 0、ID 和检查账本默认留在工作过程，最终只报告影响决策的差异。
- 快速小改禁止为了“完整”新增无关产物类型、角色、流程图、状态机或整套字段字典；一项风险最多引入一类必要合同。用户已要求直接改且信息充分时，先完成修改，再用自然语言报告假设与验收。
- 未经证据或用户授权，不新增角色、页面、实体、审批、审计、版本、并发、指标或状态机。必要的安全/合规约束单列为阻断，不混入本期范围。
- 用户要求“完整系统”“客户全生命周期”或点名端到端主链时，先按声明范围逐模块核对页面、动作、状态、角色、溯源字段、事件和正反验收；单个页面或代表链路必须标为 `demo_slice`，不得包装成完整系统。CRM 至少分别核对线索→商机→合同→开票/回款与客户→工单→需求→迭代两条链，以及客户 360 的聚合回显。
- “示例子集”不能替代“修改/替换存量原型”。除非用户明确批准缩减范围，必须保留未变更的视图、字段、动作、状态、角色路径和代表性数据量；不能完整保留时返回 `BLOCKED`，不得包装成完成。
- 外部数据集成先写清 `权威源 → 汇聚/转换方 → 消费方`、读写方向、触发、失败与纠错责任，再设计按钮、队列和自动化；反向同步不得进入正向上报队列。
- 权限先分层：无页面入口权限时菜单/路由入口不可见，直接链接与 API 仍由服务端拒绝；有页面权限但数据范围为空使用空态；有页面但无动作/字段权限才按合同隐藏、禁用、只读或脱敏。不得把这三类都画成页面内“无权限”提醒。

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

正式规格沿用 `gate --profile requirement|prd|prototype|handoff|full`。静态门禁只在目标里程碑运行一次；修复后重跑，不在每个经过的工作站重复执行。默认按根因分组输出诊断，JSON 保留全部明细。门禁必须输出 `not_proven`；静态、浏览器、业务确认、真实实现、客户验收五级证据不可越级，开放 P0/关键 P1 未知项不得称完整验收。单产物 PASS 不等于交付闭环；宣称最终完成前必须 `gate --profile full`（或 handoff）组合门禁通过。

5.4 模板用语言无关的 `<!-- ADS:* -->` 锚点，标题可按团队语言/模板改变。`resume_context` 记录相对路径、阶段和 SHA-256；漂移、缺失和路径越界必须阻断。大项目仍用执行检查点和 ID Slice，产物断点不能替代执行状态。

## 边界与扩展

`schemas/agent-handoff.schema.json` 只把已基线需求投影给 Coding Agent；`schemas/domain-candidate.schema.json` 只登记本地候选知识。私有扩展优先于官方默认，但绑定规则冲突必须形成 `DEC-CONFLICT-*`，禁止静默覆盖或联网外发。

研发排期、Sprint/任务、代码生成、CI/CD、部署、监控和运营属于下游系统。本 Skill 管到需求验收；外部状态只记引用，线上反馈以新来源回流 intake/CHG，并保留人类问责。
