# 页面、原型与可测试性合同 / Page, Prototype And Testability Contract

创建、反推、评审或修复交互原型时加载。原型是需求基线的可操作投影，不是独立的范围或业务权威。
用户指定单 HTML 时就用一个 HTML；大型工程原型可拆分本地 HTML/CSS/JavaScript，但所有依赖和锚点必须能从同一根目录枚举。存量小迭代默认把现有页面作为布局、密度、组件和视觉语言的权威，不因“改进设计”而擅自重画。
页面产品模式、可见评审标注、抽屉、流程图和交互反馈必须跟随任务语言；全英文原型不得出现中文模板
占位、表头或诊断，全中文原型不得出现裸英文状态/BDD 标签。`data-*`、稳定 ID、API/字段名和机器枚举
不翻译；HTML 同步声明 `lang="en"` 或 `lang="zh-CN"`，供门禁 `--language auto` 选择诊断语言。

## 1. 输入合同 / Input Contract

开始 UI 工作前取得或恢复：

- `MOD/FLOW/VIEW/REG/ACT/FLD/STATE/AC` 图；
- 角色和数据范围差异；
- 默认（`default`）、空数据（`empty`）、加载中（`loading`）、错误（`error`）、部分/陈旧（`partial/stale`）、成功（`success`），以及按权限分层后真实可达的权限状态；
- 每个主要动作的可见结果和领域结果；
- 代表性数据、字典、长文本和大列表行为；
- 弹窗/抽屉链，以及适用的响应式、打印、导出；
- 页面白名单和每页的指标、列、筛选、控件、限制、分页合同。

存量原型先执行交互盘点：

```powershell
py -3 scripts/extract_interaction_ledger.py --input app.html --output interaction-ledger.json
```

修改前登记视图、动作、处理器、字段、状态、弹窗、角色路径、数据集和缺口。

存量小迭代同时提供上一版，门禁只把本次新增回归作为阻断；基线中完全相同的问题降为显式 GAP，
不能因此声称旧债已修复：

```powershell
py -3 scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app-new.html --prototype-baseline app-old.html --level L2
```

## 2. 产品模式、评审模式与三类核心图 / Product, Review And Core Diagrams

- 探索、售前、客户演示、客户确认阶段默认使用可操作的产品模式，不在页面边缘预埋整份研发说明。
- 只有用户明确要求“评审版”“评审模式”“编号标注”“评审抽屉”等可见研发投影时才直接生成。显式
  “我要评审版”已经构成确认，不重复追问。
- 英文等价表述 `review version / review mode / numbered annotations / review drawer` 同样构成确认；
  `customer demo / sales demo / product prototype` 默认产品模式。确认问题始终使用当前任务语言。
- “交开发”“给前端/后端/测试看”“开需求评审会”只说明消费方，不等于同意生成评审模式；继续产品
  模式并只询问一次是否需要可见评审投影，未确认、拒绝或暂缓时不生成。两种模式共用同一页面、数据、
  动作和状态仓，切换模式不能改变业务行为。
- 一句话需求经澄清/规格/基线首次进入原型且评审偏好尚未表达时，只询问一次：“本轮默认先做产品
  模式；是否同时需要带编号和前后端/测试说明的评审版？”该问题不阻断产品模式生成；未回复时先交付
  产品模式。内部可记录 `review_projection=unset|confirmed|declined`，不向用户暴露参数。用户明确
  拒绝或延后后，同一需求基线内不再询问；范围或交付对象实质变化时才重新确认。
- 正式需求生命周期的 review 工作站是评审签署和缺口关闭，不等于原型的可见评审模式。“评审一下
  现有原型”默认只做分析并报告问题；除非用户另行确认，不修改页面、不增加编号或评审抽屉。
- 人类评审模式采用页面共识 + `1/2/3...` 编号标注 + 共识/前端/后端/测试角色说明。每点只写该位置
  必须知道的目标、输入输出、限制、守卫、失败恢复和验收证据，不复制整份 PRD，也不承载代码方案。
- Coding Agent 不以可见标注文案为唯一输入；单 HTML 可嵌入结构化 handoff，多文件项目可用独立
  JSON/YAML。handoff 只引用同一基线、稳定 ID、当前变化、禁止推断和开放项。

### 2.1 评审投影的信息预算

评审模式必须同时满足“机器覆盖完整、人工投影克制”。全量字段、动作、状态、指标、权限和 AC
进入隐藏/独立的结构化 handoff 与覆盖账本；可见编号只投影会改变实现、验收或上线结论的内容：

- 阻断决策的未知项、冲突和回退策略；
- 跨页面、角色或系统的交接，以及写入、删除、提交、撤回等不可逆/受守卫状态变化；
- 无法从标签直接理解的指标口径、时间窗、去重、数据范围和权威源；
- 权限守卫、异常、重试、补偿、对账和恢复；
- 高价值输入输出、边界与验收证据。

常规字段释义、显然按钮、重复规则和完整测试步骤只进入机器覆盖账本，不逐项占用右侧抽屉。一个编号
可以覆盖一个区域或一段连续操作。每条可见说明使用“已确认/建议/未知/观察缺陷”之一，并提供精确
`source_ref`；没有来源的技术接口、数据库表或 API 路径不得补写为已确认合同。角色栏只显示有实施
责任的产品/前端/后端/测试内容，空栏不渲染。禁止用“每个字段必须一个可见标注”作为完整性门槛。

“克制”只减少重复，不减少核心实现语义。凡一个步骤会改变持久数据、业务状态、指标、责任方，或跨越
页面/模块/系统边界，必须建立 `STEP-*` 实施卡；连续且事务边界相同的纯界面动作可以合并。每张卡在
当前页面/图旁即可独立读懂，不要求接收方去其他章节拼接：

| 实施卡字段 | 必须回答的问题 |
|---|---|
| 入口与责任 | 从哪个可见入口触发；谁可见、谁可执行；入口权限不足时是菜单/路由隐藏还是局部禁用 |
| 输入与权威源 | 输入对象/版本/字段来自哪里；哪个系统或对象为权威；时效、数据范围和身份匹配键；确认差异后是否回写企业源、监管源或只写本次快照 |
| 处理与口径 | 校验、比较、合并、计算、去重、排序或覆盖如何执行；公式的分子/分母/时间窗/零值；企业/人员/车辆/证件等计数单位和日志一行代表什么 |
| 守卫与状态 | 前置条件、并发/版本/权限守卫；前状态→后状态；非法路径如何拒绝 |
| 双结果 | 用户立即看到什么；提交哪些选中项；持久数据、权威源、下游任务或领域对象实际发生什么；未选项是否保持不变 |
| 事件与责任交接 | 发布/消费什么事件、审计或日志；成功/失败/部分成功各按何种粒度记账；交给哪个角色/系统；下一入口如何可达 |
| 失败与恢复 | 校验失败、超时、重复、部分成功、陈旧写入如何恢复、补偿、重试、幂等和对账 |
| 追溯与验收 | `REQ/FLOW/ACT/RULE/STATE/API/EVT/AC/source_ref`；已确认/建议/未知/观察缺陷 |

同一 `STEP-*` 允许用“共识/前端/后端/测试”镜头过滤：共识显示业务目的和边界；前端显示入口、控件、
可见状态与反馈；后端显示权威源、守卫、状态、事件、幂等与恢复；测试显示正反路径、边界和证据。镜头
只能改变呈现密度，不能拥有不同事实。核心字段缺失时显示“待确认/GAP”，不得用空白或通用话术掩盖。

### 2.2 评审叠加实现合同

- 产品模式与评审模式共享同一份业务 DOM、状态仓和 `ACT-*`，评审开关、编号显隐、分组切换等纯
  界面动作使用 `UIACT-REVIEW-*`；禁止复制一份产品页面或用 `ACT-REVIEW-*` 混入业务动作。
- 交互账本是从原型提取的覆盖清单和回归证据，不是需求权威源；它不能为 PRD 中不存在的业务
  `ACT-*`、`AC-*` 或规则自证合法。纯界面 `UIACT-*` 可不进入业务动作清单，但仍须有处理器和可见结果。
- 模式切换前后必须比较业务指纹：业务 `data-action/data-state/data-field/data-metric`、表单值、
  disabled/checked 与当前视图保持一致；评审模式只改变布局和说明可见性。
- 评审开关始终可点击且不可被抽屉覆盖；侧栏优先参与布局重排。固定页头、弹窗、抽屉、Toast 和
  遮罩必须避让评审侧栏。编号默认可关闭，优先标当前可见/可达目标，动态目标在渲染后绑定。
- 禁止用 `!important` 压制存量样式。浏览器证据至少包含：开关可达、产品→评审→产品往返业务
  指纹不变、无关键控件遮挡、动态视图标注可达、窄屏退化策略。

### 2.3 重型存量页面的评审容器

只有评审模式已经确认且存在三个以上重型 HTML/Axure 页面时才使用容器。容器必须分页/分组，默认
不创建产品 iframe，一次只在用户选择后懒加载一页，并提供同目录直接打开回退；不得把全部页面同时
嵌入 DOM。容器根、页签、加载、上一页/下一页使用稳定 `data-testid` 和 `UIACT-REVIEW-*`，不得使用
内联 `onclick`。动态写入表格或 class 前必须转义，表头与单元格顺序需做语义冒烟；业务未知项未关闭
时，不得把其下游测试写成已确认结论。未确认评审模式时，无论页面多重都继续产品模式，不自动生成容器。

模式路由看用户要完成的工作，不用单个关键词猜测：

| 独立用户表达示例 | 处理 |
|---|---|
| “下周给客户演示 CRM”“售前拿去讲线索到回款”“老板先看效果” | 只生成产品模式 |
| “我要评审版”“生成带编号和右侧评审抽屉的版本” | 评审模式已确认，直接生成 |
| “这个原型要交开发”“前后端和测试要看”“下周开需求评审会” | 继续产品模式，询问一次是否生成评审模式 |
| “给客户演示，也方便开发看” | 先交付产品模式，再询问是否追加评审模式 |
| “先别加标注，之后再评审” | 只生成产品模式，本轮不询问 |
| “评审一下现有原型，不要改页面” | 执行评审分析，不生成评审模式原型 |

| “帮我做一个企业约谈原型”，澄清后详细需求已确定 | 首次进入原型时询问一次；未回复先交付产品模式 |
| “只做干净的产品原型，不要评审标注” | 只生成产品模式，同一需求基线内不再询问 |
以下图按条件出现，是人类评审的主干而不是装饰：

| 图 | 必须出现的条件 | 最低信息 |
|---|---|---|
| 核心流程图 | 跨页面/模块/角色，或主链有三步以上依赖/交接 | 起点/终点、角色泳道或责任方、系统边界、关键动作、成功/失败分支、补偿和 `FLOW/ACT/AC` |
| 状态转换图 | 三个以上业务状态，或存在守卫、分支、撤销、回退、超时 | 人类状态标签 + 机器枚举、触发动作、允许角色、守卫、非法路径、事件/审计、终态和 `STM/STATE/RULE` |
| 数据流/血缘图 | 跨系统、汇聚/转换、AI处理、正反向同步、批量上报或对账 | 权威源、生产者/消费者、字段/对象、方向、触发、转换、时效、身份匹配/去重、失败/重试、纠错/对账责任和 `ENT/FLD/INT/API` |

图中节点默认使用用户语言，稳定 ID 与机器枚举作为映射保留。图后引用详细合同，不把字段字典、所有
异常和验收全文塞入图中。无上述条件的简单单页 CRUD 可不画图，并注明“不适用：单页无跨对象流转”。

产品页面、评审抽屉、图、提示、空态、错误和指标说明都属于人类可见区域。机器状态、字段、事件或队列
对研发有用时，首次出现写成本地语言含义加原值，例如“待处理（`pending`）→ 已解决（`resolved`）/
申诉中（`appealing`）”“同步游标（`lastCursor`）”“申诉队列（`appeal`）”“未知来源
（`unknown_source`）”；同一区域后续可只写本地语言。不得把原值裸露成正文标签。稳定 ID、代码块、
公式、`data-*` 锚点和隐藏 handoff 不翻译；品牌或行业通用缩写若可能造成理解歧义，首次出现也补本地
语言含义。

## 3. 稳定运行时锚点 / Stable Runtime Annotations

| 需求对象 | 原型锚点 |
|---|---|
| `VIEW-*` | 页面/弹窗/抽屉根 `data-testid="page-{view_id}"` |
| `REG-*` | 区域 `data-testid="region-{region_id}"` |
| `ACT-*` | 控件 `data-action="{ACT-*}"` |
| `UIACT-*` | 纯界面控件 `data-action="{UIACT-*}"`；评审叠加使用 `UIACT-REVIEW-*` |
| `FLD-*` | 字段/值 `data-field` 或 `data-bind` |
| `METRIC-*` | 指标根 `data-metric="{METRIC-*}"` |
| 状态枚举 | `data-state="{concrete-state}"` |
| 角色范围 | 测试需要时使用 `data-visible-role` |
| 命令/API | 已知时才使用 `data-api`、`data-method` |
| `AC-*` | 控件或场景的 `data-ac` 验收锚点 |

每个重要交互/可测试元素都要有稳定锚点。每项展示指标必须用 `data-metric` 对应 PRD 中的页面
局部口径，标签和模拟数字本身不构成指标合同。渲染 DOM 不得残留 `${state}` 等模板字符串。

锚点应直接写在源模板中。运行时批量补 `ACT-UI-*`、通过 `data-'+'action` 隐藏名称，或用
`${act}` 使动作集合不可枚举，都不能建立追溯。动态控件仍需可静态检查的模板/注册表，并由浏览器
ARUN 证明实际交互。门禁可将字面量 `act('ACT-*')`、`add(...,'ACT-*')` 与
`confirmAction:'ACT-*'` 识别为动态入口证据，避免把对应处理器重复误报为孤儿；这不豁免锚点名称拼接、
运行时补挂或未执行 ARUN 的独立问题。

## 4. 状态驱动 UI / State-Driven UI

业务状态必须进入显式状态模型，不能只藏在 CSS类、按钮文案或 DOM 文本中：

```javascript
const GlobalState = {
  currentRole: "ROLE-USER",
  entities: {},
  permissions: {},
  network: "online"
};

function transition(ownerId, actionId, payload) {
  // 校验角色、权限、当前状态、守卫和幂等
  // 写入 mock/领域结果，记录事件/审计，渲染可见结果
}
```

轻量静态原型可以简化实现，但动作仍要到达需求声明的状态和结果。

## 5. 交互闭环 / Interaction Closure

每个 `data-action` 必须具备：事件处理器、允许角色/状态与守卫、执行反馈、持久可见结果、
原型领域/状态结果、失败恢复，以及 `ACT-*` 和 `AC-*` 追溯。核心状态命令只有 Toast 不算完成。
优先让所属列表、卡片、详情或状态直接体现变化。

不同实体不能共用一个不识别实体 schema 的通用“编辑/详情”弹窗。题目编辑打开资源详情，即使
按钮都有 handler，也属于阻断缺陷。

父级点击处理器必须忽略嵌套可编辑/交互目标：

```javascript
if (event.target.closest("button,input,textarea,select,a,[contenteditable]")) return;
```

优先用事件委托和 `data-*`，避免内联 `onclick` 引号链。L3交接禁止内联 handler 和通用 alert
兜底，应使用键为静态 `ACT-*` 的显式 Action Registry。

## 6. 必备 UI 状态与权限分层 / Required UI States And Permission Layers

| 状态 | 可见要求 |
|---|---|
| 默认（`default`） | 正常数据和主要任务 |
| 空数据（`empty`） | 原因、下一动作，不伪造数据 |
| 加载中（`loading`） | 加载范围并禁用重复提交 |
| 错误（`error`） | 原因、重试/人工路径，安全保留输入 |
| 部分/陈旧（`partial/stale`） | 时效警告并限制有后果动作 |
| 成功（`success`） | 持久结果和下一动作 |

代表性数据至少覆盖长名称、空值、多状态、分页/滚动、窄屏和受限记录（适用时）。

权限不能只用一个 `no_permission` 页面概括：

| 权限层 | 正常用户路径 | 原型与测试合同 |
|---|---|---|
| 菜单/页面入口 | 无权角色看不到菜单、快捷入口和可发现路由 | 角色切换后入口消失；直接链接仍模拟 403/拒绝，API 守卫单独验收 |
| 数据范围 | 页面可见但范围内没有记录 | 使用空数据/范围内无数据（`empty/no_data_in_scope`），说明筛选或范围，不泄露范围外数量与记录 |
| 动作/组件 | 页面可见但不能执行某动作 | 按业务合同隐藏、禁用或只读；需要可发现性时说明原因，服务端仍拒绝绕过请求 |
| 字段 | 可见记录中的字段受限 | 隐藏、脱敏或只读，并声明导出/API一致性 |

只有直接深链、收藏的旧地址、进入页面后权限被撤销、嵌入区域单独受限等可达情况，才展示页面或局部
`no_permission`。普通无入口角色不需要先进入页面再看“您无权限”。

## 7. 复杂交互模式 / Complex Interaction Patterns

### 弹窗与抽屉链 / Modal And Drawer Chains

定义触发、内容、字段、确认、取消、关闭、加载、成功、失败，以及关闭后所属页面可见/领域结果。
每个弹窗/抽屉必须从声明的页面和动作可到达。

### 表单与级联 / Forms And Cascades

覆盖默认、必填、字典、依赖、异步校验、动态行、计算、附件、草稿、提交、重复和恢复；
后端业务规则仍是权威。

### 批量与拖拽 / Batch And Drag Operations

批量操作定义可选资格、混合状态、确认、部分失败、重试、撤销/补偿、顺序和审计。拖拽定义开始、
允许目标、悬停提示、释放结果、非法释放，以及需要时的键盘/移动端替代方案。

### 异步、实时与弱网 / Async, Realtime, And Weak Network

SSE/WebSocket/倒计时/推送按需加载 `references/patterns/realtime-contract.md`，呈现重连、陈旧、
重复、离线队列、冲突、重试和人工对账。

## 8. 原型迭代等价性 / Prototype Iteration Parity

修改存量原型前后比较：路由/视图、动作/处理器、字段/字典、状态/转换、弹窗/抽屉、角色路径/
数据范围、代表性数据量、关键流程和验收锚点。移除行为必须有已批 `CHG-*` 或明确缩减范围；
视觉更干净但行为丢失仍然失败。

用户要求“修改、升级、融合、替换”存量原型时，等价性是硬完成条件：未授权变化之外的
view/action/handler/field/state/role path 和代表性数据量不得减少。只实现代表性字段或样本只能标为
`demo_slice`，不能作为目标原型交付；用户未批准缩减时状态必须是 `BLOCKED`。至少记录修改前后计数、
丢失集合、批准的移除引用和 `parity_status=pass|blocked`。

范围声明本身也要做等价性检查。用户要求“完整系统”“客户全生命周期”或点名端到端主链时，不能把一
个看板、一个列表或一条代表路径命名为完整交付。至少逐模块核对页面、动作、状态、角色/数据范围、字段
映射、溯源 ID、事件/审计、成功路径、非法状态、权限、重复/并发和失败恢复。CRM 完整范围至少包括：

- 销售链：`Lead.id → Opportunity.leadId → Contract.opportunityId → Invoice/Payment.contractId`；
- 服务与产研链：`Customer.id → Ticket.customerId → Demand.ticketId → IterationTask.demandId`；
- 客户 360：上述合同、回款、工单、需求与迭代结果按权限聚合回显。缺少任一声明链时标为 `demo_slice`。

集成类页面先在原型状态仓中声明：

```text
authority_source -> aggregator/transformer -> consumer
read_direction=
write_target=
trigger=manual|scheduled|event
failure_owner=
correction_owner=
queue=
```

正向上报、反向同步和纠错申请必须使用不同命令/队列；共用一个入口时也要分别呈现授权、进度和结果。

出现重复函数、层叠覆盖、内联 handler 引号问题、运行时补动作 ID、实体动作路由到错误弹窗时，
停止继续打补丁。保留交互台账和样本数据，以一个状态仓、每页一个 renderer、一个动作注册表重建。
状态变化尽量只改需要的 class/attribute/content，避免重建 DOM 导致焦点、光标、滚动和引用丢失。

## 9. 安全验证闭环 / Safe Verification Loop

1. 检查 HTML/JavaScript 语法；
2. 在真实浏览器加载；
3. 不依赖设计讲解，按主要角色逐动作执行；
4. 覆盖适用的默认、失败、权限和状态冲突；
5. 对照需求确认可见结果和领域结果；
6. 检查运行时锚点具体、唯一；
7. 按 AC 捕获截图、trace或审计证据；
8. 修复后重跑等价性。

研发评审完成前增加角色复述检查：前端仅凭交付物能按 `STEP-*` 列出入口/可见性、字段控件、交互状态
和反馈；后端能按同一 `STEP-*` 列出权威源、处理/公式、权限/状态守卫、幂等、接口/事件和失败恢复；
测试能形成角色 × 权限层 × 状态 × 异常矩阵及对应证据；Coding Agent 能输出不新增业务假设的入口图、
状态/事件表、失败矩阵和实现切片。任何角色仍需产品口头补充核心语义，或不同角色复述出相互冲突的
状态、口径、事件和责任边界时，记录 GAP 并回写基线，不能以“说明大致有了”通过。
L3必须遍历所有声明页面的可见动作，而不是每角色只走一条成功主路径（`happy path`）；确认动作打开
的是所属实体页面/弹窗、字段控件与页面合同一致、关闭后持久结果回到所属列表/详情。

将执行记录写为 `ARUN-*`：执行环境（`environment`）指明真实浏览器/设备，每个 `data-ac` 有执行项，
每个通过项（`pass`）有实际结果（`actual_result`）和截图/trace/审计证据。通过 `--acceptance-run` 传给门禁。没有浏览器能力时，创建待执行（`pending`）ARUN 和准确动作清单，返回 `REVIEW_COMPLETE_WITH_GAPS`，不得宣称交互原型完成。

工程原型可拆成本地多文件。相对 JS/CSS 会与 HTML 一起进入动作、状态、语法和 CSS 污染扫描；
缺失、绝对路径、越过原型目录会阻断，远程依赖保留为 GAP。不得为过门禁打包成不可维护巨型 HTML。

远程 iframe 不是普通本地依赖：`http://`、`data:`、`javascript:`、`file:` 一律阻断；HTTPS iframe 在 L2+ 必须声明 `data-integration-ref="INT-*"`、`data-fallback`、`title`、`sandbox` 和 `referrerpolicy`，L0/L1 缺失时保留 GAP。即使静态声明完整，也只能得到 `PROTO-REMOTE-IFRAME-UNVERIFIED`，必须在目标网络与角色登录态下用浏览器 `ARUN-*` 证明内容、权限、可达性、交互及失败降级。

自动写操作只能使用 mock、shadow 或可丢弃测试数据，未经明确授权和安全计划不得污染生产数据/指标。

| 步骤 | 可见线索 | 用户动作 | 可见结果 | 领域结果 | 阻断/假设 | AC |
|---|---|---|---|---|---|---|

用户无法从界面推断下一步时停止并记录阻断，测试过程中不要口头提示“设计意图”。

## 10. 视觉锁与可访问性基线 / Visual Lock And Accessibility Baseline

先判断视觉权威：

- 存量小迭代：现有 HTML、截图和已批准页面是默认视觉权威。继承页面骨架、信息密度、字号、颜色、间距、控件高度、圆角、表格、表单、弹窗和按钮用法；除非用户明确要求重设计，不询问美学方向，不换设计系统。
- 同一项目多页面：先从权威页面提取一份紧凑视觉锁，随后所有页面复用；不得逐页重新发挥。
- 绿地内部工具：用户未给视觉方向时，选择一个克制、可逆、以任务为中心的默认方案直接推进；不因缺少审美决策阻断原型。
- 品牌化、外部客户展示或多个方向会显著改变交付时：才确认 feeling、reference、explicit taboo，必要时登记 `DEC-AESTHETIC-*`，先做一个代表屏再扩展。

开始视觉实现前写一行 `design_read`：这是一个怎样的任务界面、需要什么信息密度和情绪、视觉权威来自
哪里。再登记三个相对旋钮 `variance/motion/density=1..5`，数字表示相对当前权威页面的变化程度，不是
通用审美分数；政企后台、数据表和多步骤业务默认以存量权威与任务效率为准，通常低变化、低动效、高
密度。关键视觉取舍用 `触发→选择→理由→证据` 记录，例如“老系统小迭代→继承表格密度→减少客户认知
变化→SRC-截图-02”。这份记录用于约束发挥，不取代页面合同、可访问性或业务评审。

视觉锁至少固定：

| 项 | 必须固定的内容 |
|---|---|
| tokens | 主/辅/状态色、背景、边框、阴影、圆角、间距阶梯、控件高度 |
| typography | 字体、字号层级、字重、行高；主文本不得小于 11px |
| shell | 导航、页头、内容宽度、栅格、固定/滚动区和响应式优先级 |
| components | 主/次/幽灵/危险按钮、输入、选择、表格、标签、卡片、弹窗的唯一变体与使用边界 |
| density | 列表行高、表单间距、留白和信息密度 |
| taboos | 禁止的装饰、渐变、驾驶舱堆叠或与权威页面冲突的风格 |

单 HTML 用一个 CSS token 区和一套组件类；多文件用同一 token/组件入口。新增页面只能复用视觉锁或通过明确变更更新它。视觉复核至少检查 token 漂移、同名组件变体、页面骨架漂移、字号/控件高度漂移和信息密度突变。

同时满足：状态不能只靠颜色；保持信息层级和任务聚焦，不堆无业务意义的驾驶舱装饰；按范围提供键盘/焦点、标签、对比度、错误关联和减少动效；打印/导出保留字段、分页、签署、版本和归档元数据。桌面和适用窄屏分别截全页图复核。高保真不能补偿缺失交互。

确有需要时只引入一个专门设计 Skill，不能声称执行未安装 Skill，也不能让两个工具生成竞争设计系统。

## 11. 锁定与验收 / Lock And Acceptance

完成时记录：

```text
[PROTOTYPE LOCK]
truth_version=
artifact_sha256=
view_count=
region_count=
action_count=
state_count=
role_paths=
baseline_ref=
baseline_sha256=
parity_status=pass|blocked|not_applicable
preserved_counts=
approved_removals=
review_projection=unset|confirmed|declined
visible_review_note_count=
review_coverage_ref=
browser_evidence_status=pending|passed|blocked
visual_authority=existing|greenfield_default|DEC-AESTHETIC-*
design_lock_ref=inline|file|DEC-AESTHETIC-*
design_read=
design_dials=variance:N,motion:N,density:N
taste_tradeoffs_ref=
gate_status=PASS|REVIEW_COMPLETE_WITH_GAPS|BLOCKED_BY_P0_UNKNOWN|BLOCKED
gate_command=
gate_output_ref=
gaps=
evidence_location=
```

锁定前要求：全部范围内视图/动作可追到基线；主要角色旅程闭合；适用空值/错误/权限/冲突路径可用；
无未批准行为损失；强制 AC 有浏览器证据；L3复杂页有稳定 `REG-*`；遗留缺口有责任人和状态。

CSS扫描：

```bash
python scripts/scan_prototype_css.py prototype.html
```

使用 `.hidden` 时只能有一条隔离的 `.hidden { display: none ... }`；该工具外禁止 `!important`。
重复/组合 `.hidden` 会污染层叠。`.active/.open/.selected/.disabled/.loading/.error/.success/.failed`
必须限定到组件，如 `.status.active`、`.tab.active`、`.page.active`，不能全局组合业务状态色。

## 页面类型与条件表面 / Page Profiles And Conditional Surfaces

每个实施页面先声明：

```markdown
<!-- PAGE-CONTRACT: VIEW-RESOURCE; primary=list; layout=composite; surfaces=metrics,list,drawer_form,preview -->
```

`layout` 为 `single/composite/builder/portal`。`surfaces` 可由 metrics、list、form、drawer_form、
detail、workflow、composer、resource_pool、hierarchy、assessment_insert、import、export、preview
组合。不要创建行业专用页面 profile。composite 至少两个真实表面；builder 必须含 composer、
resource_pool、hierarchy。移动/H5 的 scan、camera、weak_network、offline_draft、push 单独声明。

只要求实际启用的表面。每页共同声明用途/入口、区域布局、角色/数据范围、七类 UI状态、弹窗链、
分页/批量、原型锚点和 API/AC，再按条件补充：

- metrics：统计对象、分子分母、窗口/时区、状态/过滤、去重、来源/时效、零值/空值、格式；
- list/tree：筛选、列、格式/宽度/空值/排序、选择、页大小；
- form/upload：控件、必填/默认、类型/长度、字典、校验、可编辑性、扩展名/MIME、数量/大小、
  预检、转码和恢复；
- action/workflow：守卫、确认、可见/领域结果、状态/事件/审计、权限、幂等、失败/补偿和AC；
- import/export：模板/版本、范围、部分失败、异步阈值、文件过期、脱敏和审计；
- preview：按文件类型的控件、转码失败、授权/水印；
- composer：层级、允许源/目标、插入顺序、非法拖放、持久化、撤销/恢复、并发和替代操作。

L3/L4 的 composite、builder、portal、多视图或表格+表单页面必须有稳定 `region-REG-*` 根；
复杂页 `region_count=0` 不能完成，单表面有界页面可不设区域。

要求高保真、品牌化或生产级原型时，先冻结 UI 需求合同。复杂后台优先设计系统型 UI/UX Skill，
品牌/H5差异化优先前端艺术指导型 Skill；不能让两个工具生成竞争设计系统。

## 存量原型 Stage 0 / Stage 0 For Existing Prototypes

重写前对每个视图、动作、处理器、状态、角色、对象、字段/指标和外部交接登记来源位置和
classification：confirmed、inferred、unknown、defect_candidate。核心未知绑定 `UNK-*`、优先级、
责任人和 `blocks_stage`；缺陷不能静默变目标需求；多个候选基线由 `DEC-CONFLICT-*` 裁决。

已有 PRD 时，恢复观察使用 `INV-*`，并通过 `baseline_requirement_refs`、`mapping_status`、准确
`target_refs` 映射。所有推断项进入有责任人的 `RBATCH-*`；未确认、否决或转未知前不得声明
`baseline_ready`。反推能恢复交互证据，不能推断 API语义、指标口径、权限权威、合规或 AC 真相。

## 存量资产处置 / Legacy Asset Disposition

Stage 0 盘点恢复"有什么"，处置决定"怎么对待"。5.4.1 起，每个 view 类盘点条目建议用
`disposition` 字段登记处置方式（见 `schemas/stage0-inventory.schema.json` 与
`references/templates/stage0-inventory-template.yaml`），五选一：

| 处置 | 定义 | 何时选择 |
|---|---|---|
| `adopt_page` | 整页直接采用，行为与视觉均不重做 | 页面已满足目标合同，仅需补锚点和状态 |
| `inherit_layout` | 保留布局与信息架构，重做视觉层 | 结构合理但视觉不达标，已确认 `DEC-AESTHETIC-*` |
| `rebuild_interaction` | 保留业务流程，重做交互与状态模型 | 流程正确但交互断裂、状态隐式或锚点不可枚举 |
| `reuse_component` | 仅复用局部组件，页面其余部分重画 | 只有个别表格、表单等组件达到复用标准 |
| `discard` | 废弃重画，不作为新页面基础 | 行为或结构与目标合同冲突，或属重复/死页面 |

规则：

- `disposition` 不替代 classification 和 `mapping_status`；条目仍需先完成来源、分类和基线映射。
- 未登记 `disposition` 的条目按未定处置对待，不得默认整页采用。
- `discard` 或任何移除存量行为的处置，仍需已批 `CHG-*` 或明确缩减范围；缺陷候选未经
  `DEC/CHG` 不得借处置名义升级为目标需求。
- `inherit_layout` 与涉及视觉重做的处置，先完成美学方向确认；`rebuild_interaction` 重画部分
  按本文件全部交互合同执行。
- 处置结论是原型迭代等价性比较（第 7 节）的基线：声明保留的布局、流程或组件必须出现在
  等价性核对范围内。
