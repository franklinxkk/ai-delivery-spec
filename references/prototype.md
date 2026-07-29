# 页面、原型与可测试性合同 / Page, Prototype And Testability Contract

创建、反推、评审或修复交互原型时加载。原型是需求基线的可操作投影，不是独立的范围或业务权威。
用户指定单 HTML 时就用一个 HTML；大型工程原型可拆分本地 HTML/CSS/JavaScript，但所有依赖和锚点必须能从同一根目录枚举。存量小迭代默认把现有页面作为布局、密度、组件和视觉语言的权威，不因“改进设计”而擅自重画。

## 1. 输入合同 / Input Contract

开始 UI 工作前取得或恢复：

- `MOD/FLOW/VIEW/REG/ACT/FLD/STATE/AC` 图；
- 角色和数据范围差异；
- default、empty、loading、error、no_permission、partial、success 状态；
- 每个主要动作的可见结果和领域结果；
- 代表性数据、字典、长文本和大列表行为；
- 弹窗/抽屉链，以及适用的响应式、打印、导出；
- 页面白名单和每页的指标、列、筛选、控件、限制、分页合同。

存量原型先执行交互盘点：

```powershell
py -3 scripts/extract_interaction_ledger.py --input app.html --output interaction-ledger.json
```

修改前登记视图、动作、处理器、字段、状态、弹窗、角色路径、数据集和缺口。

## 2. 稳定运行时锚点 / Stable Runtime Annotations

| 需求对象 | 原型锚点 |
|---|---|
| `VIEW-*` | 页面/弹窗/抽屉根 `data-testid="page-{view_id}"` |
| `REG-*` | 区域 `data-testid="region-{region_id}"` |
| `ACT-*` | 控件 `data-action="{ACT-*}"` |
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
ARUN 证明实际交互。

## 3. 状态驱动 UI / State-Driven UI

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

## 4. 交互闭环 / Interaction Closure

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

## 5. 必备 UI 状态 / Required UI States

| 状态 | 可见要求 |
|---|---|
| default | 正常数据和主要任务 |
| empty | 原因、下一动作，不伪造数据 |
| loading | 加载范围并禁用重复提交 |
| error | 原因、重试/人工路径，安全保留输入 |
| no_permission | 清楚说明边界且不泄露隐藏数据 |
| partial/stale | 时效警告并限制有后果动作 |
| success | 持久结果和下一动作 |

代表性数据至少覆盖长名称、空值、多状态、分页/滚动、窄屏和受限记录（适用时）。

## 6. 复杂交互模式 / Complex Interaction Patterns

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

## 7. 原型迭代等价性 / Prototype Iteration Parity

修改存量原型前后比较：路由/视图、动作/处理器、字段/字典、状态/转换、弹窗/抽屉、角色路径/
数据范围、代表性数据量、关键流程和验收锚点。移除行为必须有已批 `CHG-*` 或明确缩减范围；
视觉更干净但行为丢失仍然失败。

用户要求“修改、升级、融合、替换”存量原型时，等价性是硬完成条件：未授权变化之外的
view/action/handler/field/state/role path 和代表性数据量不得减少。只实现代表性字段或样本只能标为
`demo_slice`，不能作为目标原型交付；用户未批准缩减时状态必须是 `BLOCKED`。至少记录修改前后计数、
丢失集合、批准的移除引用和 `parity_status=pass|blocked`。

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

## 8. 安全验证闭环 / Safe Verification Loop

1. 检查 HTML/JavaScript 语法；
2. 在真实浏览器加载；
3. 不依赖设计讲解，按主要角色逐动作执行；
4. 覆盖适用的默认、失败、权限和状态冲突；
5. 对照需求确认可见结果和领域结果；
6. 检查运行时锚点具体、唯一；
7. 按 AC 捕获截图、trace或审计证据；
8. 修复后重跑等价性。

L3必须遍历所有声明页面的可见动作，而不是每角色只走一条 happy path；确认动作打开的是所属实体
页面/弹窗、字段控件与页面合同一致、关闭后持久结果回到所属列表/详情。

将执行记录写为 `ARUN-*`：environment 指明真实浏览器/设备，每个 `data-ac` 有执行项，每个 pass
有 actual_result 和截图/trace/审计证据。通过 `--acceptance-run` 传给门禁。没有浏览器能力时，
创建 pending ARUN 和准确动作清单，返回 `REVIEW_COMPLETE_WITH_GAPS`，不得宣称交互原型完成。

工程原型可拆成本地多文件。相对 JS/CSS 会与 HTML 一起进入动作、状态、语法和 CSS 污染扫描；
缺失、绝对路径、越过原型目录会阻断，远程依赖保留为 GAP。不得为过门禁打包成不可维护巨型 HTML。

自动写操作只能使用 mock、shadow 或可丢弃测试数据，未经明确授权和安全计划不得污染生产数据/指标。

| 步骤 | 可见线索 | 用户动作 | 可见结果 | 领域结果 | 阻断/假设 | AC |
|---|---|---|---|---|---|---|

用户无法从界面推断下一步时停止并记录阻断，测试过程中不要口头提示“设计意图”。

## 9. 视觉锁与可访问性基线 / Visual Lock And Accessibility Baseline

先判断视觉权威：

- 存量小迭代：现有 HTML、截图和已批准页面是默认视觉权威。继承页面骨架、信息密度、字号、颜色、间距、控件高度、圆角、表格、表单、弹窗和按钮用法；除非用户明确要求重设计，不询问美学方向，不换设计系统。
- 同一项目多页面：先从权威页面提取一份紧凑视觉锁，随后所有页面复用；不得逐页重新发挥。
- 绿地内部工具：用户未给视觉方向时，选择一个克制、可逆、以任务为中心的默认方案直接推进；不因缺少审美决策阻断原型。
- 品牌化、外部客户展示或多个方向会显著改变交付时：才确认 feeling、reference、explicit taboo，必要时登记 `DEC-AESTHETIC-*`，先做一个代表屏再扩展。

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

## 10. 锁定与验收 / Lock And Acceptance

完成时记录：

```text
[PROTOTYPE LOCK]
truth_version=
view_count=
region_count=
action_count=
state_count=
role_paths=
baseline_ref=
parity_status=pass|blocked|not_applicable
preserved_counts=
approved_removals=
browser_evidence_status=pending|passed|blocked
visual_authority=existing|greenfield_default|DEC-AESTHETIC-*
design_lock_ref=inline|file|DEC-AESTHETIC-*
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
