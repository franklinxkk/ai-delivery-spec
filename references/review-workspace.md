# 人类评审工作台合同 / Human Review Workspace Contract

仅在用户明确确认评审版后加载本文件；客户演示和产品确认默认不加载。先读取 `prototype.md`，本文件只
扩展人类评审投影，不改变 PRD/受治理真相和机器 handoff 的权威边界。

## 1. 完成任务，而不是浏览说明

完成标准是未参与原讨论的接收者能独立：选择业务旅程 → 判断当前步骤与上下游 → 切到自己的角色工作包
→ 找到页面落点和规则/AC → 报告 GAP 或开始实施/测试。需要原作者逐页串讲仍为 GAP。

| 模式 | 接收者任务 | 最小呈现 |
|---|---|---|
| 导读 `orientation` | 选择旅程并判断本次范围 | 目标、角色/系统、起止结果、步骤数、阻断未知项 |
| 旅程 `journey` | 看懂先后、分支与交接 | `FLOW/STEP/EDGE` 图、当前步骤、完成进度、成功/异常/退回/并行边 |
| 聚焦 `focus` | 在产品上下文评完一个步骤 | 当前页面/区域、一张 STEP 卡、角色镜头、上下游入口、规则/场景/GAP |
| 页面 `page` | 核对局部字段、指标、权限和交互 | 只标当前页或当前 STEP 的关键编号，不默认铺满全站 |
| 验收 `acceptance` | 把合同转为可执行场景 | `TEST → AC → STEP`、夹具、正反边界、可见+领域结果、证据要求 |

复杂主链从导读/旅程进入，单页单步骤可从聚焦进入。切换时保留
`journey_id/current_step/role/mode`；页面、弹窗或 DOM 更新不能重置到第一卡。角色镜头默认聚焦本角色，
但必须能查看影响本角色的上游输入、下游结果和失败边。

## 2. 自适应布局

- 桌面端：导读、旅程、验收使用独立工作区；聚焦才使用产品画布 + 可折叠/可调宽说明面板，产品画布
  保持主要阅读面。禁止固定窄画布加固定宽长抽屉承载所有任务。
- 窄屏/H5：使用“产品 / 评审”全屏切换并保留当前 STEP 与返回目标；不得用侧抽屉只留下产品窄缝。
- 聚焦面板：顶部显示任务、状态、来源和进度；中部只显示当前角色分组工作包；底部放上下游、关联规则/
  场景和 GAP。稳定 ID 辅助定位，不替代人类标题。
- 编号策略：只允许 `selected_step_only` 或 `current_page_on_demand`；关闭评审不改变业务状态。
- 选中反馈：点画布区域/编号时，右侧切到对应 STEP 并显示清晰边框、标题和上下游；点 STEP
  或合同引用时，画布反向定位到真实 DOM 目标。空间坐标、截图圈选和自增顺序号只是交互辅助，
  不得取代稳定 ID 和业务合同。
- 分享定位：严格评审路径应保留 `mode/journey/step/role/page/region`（可使用 URL 查询或 hash），
  接收者打开即到待评步骤；只发一个页面首屏、再由作者口头带路，不算可独立移交。单文件
  `file://` 环境可用 hash 降级，但必须保持同一定位语义。

## 3. STEP 交接图与角色工作包

用 `EDGE-*` 表达 `start/next/branch/parallel/join/return/error/compensate/finish`。每条边绑定生产者、
消费者、交接对象、对方入口、后置结果、条件和恢复引用；每个 STEP 至少一条进入和离开边，起终点使用
start/finish。

一个 STEP 是一个可归责工作提交点：只有一个主责任角色/系统、一个可复述任务和一组原子业务结果。不要把
“编辑提交 + 审核发布”、或“生成批次 + 分配代理商”压成一张卡；责任人、守卫或状态提交点不同就应拆成
STEP 后用 EDGE 连接。普通同角色 CRUD 点击不机械升格为 STEP。

| 镜头 | 必须独立回答 | 不得擅自补写 |
|---|---|---|
| 产品 `product` | 为什么做、本期/非目标、决策与来源、业务完成结果、开放 GAP | 未确认指标、范围和责任 |
| 前端 `frontend` | 入口/可见性、区域字段控件、适用 UI 状态、即时反馈与下一入口 | 未确认技术选型和后端规则 |
| 后端 `backend` | 权威源/身份键、I/O/校验、守卫/领域变化、事件审计、幂等并发、失败恢复 | 未确认 URL、表名、错误码和架构 |
| 测试 `qa` | 场景/AC、前置夹具、正反边界权限、网络重复并发、双结果与证据 | 把设计写成已执行 PASS |

四个角色槽位都存在，但只展开真正受影响的角色。`applicability=not_affected` 时显示一条可核对的原因，
槽位、合同引用和场景保持为空；不得为了过门禁填“无”“同上”或伪造后端/API/测试内容。角色是否受影响
尚不明确时不能标不受影响，应保持 active 并绑定 `UNK-*`。

一个 STEP 可有多个场景，一个端到端场景也可覆盖多个 STEP；每个 STEP 至少由一个 `TEST/AC` 定位。
Coding Agent 不作为第五个可见镜头：工作台只显示 handoff 是否可用及 GAP，机器读取
`schemas/agent-handoff.schema.json`，不从右栏文案猜实现。

`machine_handoff.status` 区分 `not_requested/blocked/ready`：本阶段未要求 Coding Agent 时显式
`not_requested`，不生成空壳；被业务未知项阻断时用 `blocked + UNK-*`；只有同基线 manifest 与 packet
均存在且无阻断 GAP 时才能写 `ready`。handoff/full 门禁会把该状态、实际 manifest 状态、baseline hash、
文件名和 packet ID 交叉核对；可见绿灯不能由评审 HTML 自己声明。

## 4. 薄 manifest 与 DOM 合同

HTML 内嵌唯一 `<script type="application/json" id="review-workspace-manifest">`，按
`schemas/review-workspace.schema.json` 只登记 baseline hash、FLOW/STEP/EDGE、角色槽位覆盖、DOM/合同
引用、TEST/AC、UNK 索引和 handoff 状态；禁止复制业务规则正文。

根容器必须声明 `data-review-workspace`、`data-review-compact="fullscreen-switcher"`、允许的
`data-review-marker-policy`、`data-review-active-mode` 和 `data-review-active-role`。五种模式分别用 `data-review-mode`；模式入口用
`data-review-mode-target`；进度、当前步骤、验收场景和窄屏切换分别用 `data-review-progress`、
`data-review-current-step`、`data-review-scenario`、`data-review-compact-view`。

manifest 中每个 STEP 必须声明唯一 `dom_anchor: review-step-STEP-*`，HTML 中恰好一个同根元素同时绑定
`data-review-step="STEP-*"` 与该 `data-testid`。四个角色镜头和槽位必须位于这个 STEP 根内；一个全局
通用镜头不能冒充所有步骤的工作包。大型流程应提升 STEP 粒度，不把每个普通按钮都建成 STEP。

每个 STEP 同时声明 `task_kind/accountable_ref/outcome_refs/risk_dimensions/marker_refs`。业务决定与验证证据
必须分成两条轴：`business_status=confirmed` 需要仍有效的 `SRC/DEC`，`verification_status` 只有在绑定
`EVD/ARUN` 后才能从 `not_run` 升为静态检查、浏览器检查、集成检查、已验收或失败。原型里已经出现，
不等于业务获批；业务获批，也不等于实现已经运行通过。

两条轴不能只藏在 manifest：每个 STEP 工作包分别显示
`data-review-status-step="STEP-*" + data-review-status-axis="business|verification" + data-review-status-value`，
元素正文使用工件语言解释当前值。`browser_checked/integration_checked/accepted/failed` 必须引用本次门禁
实际提供的 `ARUN-*`；`browser_checked` 还需浏览器环境，`accepted` 还需有证据的签署结论，`failed`
还需失败/拒绝记录。只写一个看似真实的 ID 或 `EVD-FAKE-*` 不能升级验证状态。

`marker_refs` 只列
当前步骤需要人眼核对的关键 `VIEW/REG/ACT/FLD/METRIC/STATE`。页面级规则、系统处理、系统外交接和数据
权威等没有产品元素的事实留在角色工作包中，允许 `marker_refs=[]`；不得为了凑编号把它们钉到无关按钮。
流畅文案、原型现状和模型建议不能独自把未知升级为 confirmed；作者自测或模型角色扮演也不能把
`verification_status` 升为真人冷读、真实集成或客户验收。

每条旅程把三种模型分开索引：`flow_refs` 说明责任交接，`state_machine_refs` 说明对象合法转换，
`data_flow_refs` 说明权威源、方向与回写。确实不适用状态机或数据流时在 `not_applicable` 显式声明；留空
不等于不适用，也不能用一张“万能流程图”同时冒充三种合同。人类工作台必须把引用到的模型分别投影为
`data-review-model="flow|state_machine|data_flow" + data-review-model-ref`；不适用维度用
`data-review-model-na` 显示原因。标签存在但没有可读图、转换/方向说明或来源，仍不能通过真人冷读。

每个 `data-review-lens` 必须有以下非空槽位：

- product：`purpose`、`scope_and_boundary`、`decision_and_source`、`business_result`；
- frontend：`entry_and_visibility`、`surface_and_fields`、`interaction_and_ui_states`、`visible_result`；
- backend：`authority_and_identity`、`input_output_and_validation`、`guards_and_state_effects`、
  `side_effects_and_audit`、`failure_recovery`；
- qa：`preconditions_and_fixture`、`positive_and_negative`、`boundary_and_permission`、
  `visible_and_domain_result`、`evidence`。

上表只约束 active 角色。每个场景始终覆盖正向、反向、可见+领域结果和证据；STEP 声明了 boundary、
permission、failure/recovery 或 network/concurrency 风险时，关联场景必须追加对应维度。测试投影从同一
`TEST/AC` 生成，HTML 只负责导航与展示，禁止在原型脚本中手写另一套 API、错误码或测试 YAML。
每个镜头根以 `data-review-applicability="active|not_affected"` 与 manifest 对齐；不受影响原因必须作为
人类可见正文呈现，不能只藏在 JSON 属性里。active 镜头必须把 manifest 的 `contract_refs` 作为可见引用
或可展开来源清单展示，方便接收者从摘要回到权威规则；摘要不是第二份可独立修改的业务事实。

验收模式中每个场景使用 `data-review-scenario="TEST-*"` 与 `data-review-acceptance-ref="AC-*"`，并显示
其覆盖 STEP、前置夹具、正反/风险维度、可见+领域结果和证据要求。仅显示“已覆盖 8 条用例”不算可交接。

## 5. 产品等价与浏览器证据

- 产品与评审共享同一业务 DOM、状态仓和 `ACT-*`；纯评审动作使用 `UIACT-REVIEW-*`。
- 模式切换前后比较业务 `data-action/data-state/data-field/data-metric`、值和 disabled/checked 指纹。
- 开关不可被面板覆盖；固定页头、业务弹窗/抽屉、Toast、遮罩和动态目标必须协调。
- 不用 `!important` 压制存量样式；编号/卡片共享 `data-review-id` 或对应 `data-review-target`，两侧均有
  `aria-current="true"` 等可访问选中态，点击任一侧会定位、滚动并框选另一侧。
- 局部修改后不只显示文件 Diff；评审工作台还要能回到受影响的 `REQ/STEP/RULE/STATE/DFD/AC/TEST`
  引用。“只改了这几行 HTML”不能独自证明业务变更无回归。
- 只对 manifest 声明的 `marker_refs` 建立双向编号；`marker_refs=[]` 的系统/外部步骤显示“无页面落点”，
  不触发缺编号门禁。
- 浏览器 `ARUN-*` 至少证明：开关可达、产品→评审→产品指纹不变、无关键遮挡、动态视图可达、编号双向
  联动、四角色切换后工作包确实变化，以及窄屏全屏切换保留当前任务。

## 6. 冷读门禁

交接前让未参与者在限定时间内选一条主链，按自己的角色复述一个 STEP 的输入、处理、双结果、异常和
下一交接，并定位规则/AC/GAP。四类角色分别通过才可称“人类评审就绪”；冷读通过仍不证明实现正确、
真实系统运行或客户验收。

记录每个角色的找到入口时间、正确复述率、首次澄清、误猜规则、阻断 GAP、返工和完成证据；生成者自评、
字段填满或“零 GAP”不能替代未参与者冷读。界面中的“前置/操作/预期”等流程词跟随工件语言，中文工件
不残留 Given/When/Draft 等非稳定英文；稳定 ID、官方名称与代码标识保持原文。
