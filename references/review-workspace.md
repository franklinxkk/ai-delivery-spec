# 人类评审工作台合同 / Human Review Workspace Contract

仅在用户明确确认评审版后加载。先读取 `prototype.md`；本文件只定义人类评审投影，不改变 PRD、
Product Truth、结构化 handoff 或验收证据的权威边界。

> **Review Explains, Product Operates.** 左侧始终是完整可操作产品；右侧只解释真实产品动作产生的当前
> 上下文。Context 定位置，Declaration 定分母，Candidate Diff 防漏，Fingerprint 定副作用边界，
> Layout + Detection 保证真实可运行，Target Resolution 防绑错，Review Record 防丢结论。

## 1. 人类任务与禁止结构

完成标准是未参与原讨论的产品、前端、后端、测试能沿产品自身入口独立操作，在当前页面或业务浮层旁
理解用途、上下游、结果、规则、边界和验收，并能报告 GAP、开始实现或编写测试；仍需作者逐页串讲即为
GAP。

R1/R2 只有三个一级页签：

1. `overview`：总览；
2. `function_flow`：功能与流转；
3. `boundary_acceptance`：边界与验收。

不得新增 Journey、Step Focus、Page、Acceptance 或产品/前端/后端/测试角色一级模式。复杂度只增加
页签内信息深度，不增加导航维度。R0 快速评审可不渲染三个可见页签，但仍必须声明
`CurrentContext`、`review_contexts` 分母并保证纯评审动作不改变 Product Fingerprint。

## 2. CurrentContext：产品决定评审位置

`CurrentContext = 最上层活动业务浮层，否则为活动产品视图`。允许类型只有 `VIEW`、`MODAL`、
`DRAWER`、`POPOVER`。CurrentContext 是只读结果，不提供页面/弹窗下拉框让评审层替产品导航。

- 页面、弹窗、抽屉和气泡只能由真实产品 `ACT-*` 打开、关闭或切换；`UIACT-REVIEW-*` 不得 push/pop
  Context Stack。
- 解析优先级：产品显式 Context Event → manifest 声明的 detection contract → MutationObserver 仅触发
  重新解析。MutationObserver 不能自行猜业务上下文。
- detection type 只允许 `class_contains`、`attribute_equals`、`selector_visible`、
  `product_state_equals`。多个同层候选无法判定最上层时 BLOCK，不得任取第一个。
- 未声明上下文出现时产品继续运行；右侧显示“该上下文尚未声明评审说明”，记录 GAP。不得从 DOM
  文案自动生成评审点，也不得自动跳转到其他页面。
- Overlay 关闭后恢复父级 Context 及其编号、选中评审点和滚动位置。
- 存量原型已有旧说明栏、角色镜头或旧 `review-mode` 时，迁移后必须停用旧表面。同一页面只能有一个
  可见评审事实源；新旧评审层并存会造成解释冲突，直接 BLOCK。

### 2.1 ProductLocation：产品导航证明系统位置

`CurrentContext` 回答“正在解释哪个页面/浮层”，`ProductLocation` 回答“这个功能在系统哪里、从哪里
进入”。两者必须同源同步，不能只让右侧标题变化而让左侧菜单永远停在首页。

- 每个 `VIEW-*` 的 `product_location.navigation_mode` 必须为 `menu_bound` 或 `menu_exempt`；
- `menu_bound` 同时声明 `menu_path / active_entry_selector / route_ref / breadcrumb / page_title`；
- `menu_exempt` 只用于确无产品菜单的独立入口，并写明 `exemption_reason`；
- 每个业务浮层使用 `inherit_parent` 并引用唯一 `parent_view_ref`；父页面有菜单时保持其路径高亮，父页面
  为 `menu_exempt` 时继承空菜单路径与豁免位置，不得为浮层伪造菜单；
- 页面切换同步活动视图、路由、活动菜单路径、展开父级、面包屑、标题和 CurrentContext；
- 右侧只读显示系统位置，不提供页面选择器或替代导航。

现有产品已经有菜单与同步函数时直接继承。禁用的静态菜单、仅用于展示的侧栏、页面已切换但活动菜单/
标题/面包屑未变，以及无法从真实菜单到达页面，均为评审移交阻断缺陷，而不是视觉优化项。

## 3. 三个页签各自拥有事实

| 页签 | 唯一负责的完整内容 |
|---|---|
| 总览 | 背景/问题、目标与成功信号、角色表、范围/非目标、主链、变更摘要、P0/P1 摘要 |
| 功能与流转 | CurrentContext、当前业务职责、上下游、声明评审点、可见/领域结果、当前数据与事件摘要 |
| 边界与验收 | 详细规则、权限、状态机、指标计算、异常/恢复/幂等、AC/TEST、UNK/DEC/GAP 详情 |

其他页签只能摘要并引用，不得复制完整正文。一个内容域只能有一个 owner；同一规则、状态机、指标公式
或验收正文在多个页签重复出现时记录 `PROTO-REVIEW-TAB-OWNERSHIP`。流程图、状态图和数据流图只在
确实满足 `prototype.md` 的触发条件时出现：总览显示主链摘要，功能与流转显示当前上下游，边界与验收
持有详细状态/数据/规则合同。

## 4. Declaration 定分母，Candidate Diff 只防漏

`review_contexts` 是官方上下文和评审点的唯一声明源。每个 Context 用有序 `review_point_refs` 声明
本上下文评审点；每个 ReviewPoint 必须且只能归属一个 Context。官方分母、编号和评审进度都以这些
声明为准，DOM 数量、视觉显著性和模型判断不能增减分母。

构建时另生成 Candidate Set：

- `BusinessSideEffectAction`：产生持久化、状态、外部通知或不可逆结果的动作；
- `RulefulField`：有必填、条件、计算、权限或联动规则的字段；
- `DefinedMetric`：有业务口径的指标；
- `BehaviorAffectingState`：影响可用动作或结果的状态；
- `BusinessSemanticRegion`：承载独立业务职责的区域。

执行 `Candidate - Declared`。遗漏形成 `PROTO-REVIEW-CANDIDATE-DIFF` 或 `REV/GAP`，高风险遗漏可
BLOCK；门禁不得自动把候选晋级为官方评审点，也不得改变分母。无 UI 落点的系统规则可声明为
`marker_required=false`，仍通过上下文卡片与机器合同追溯。

Candidate 必须进入独立 `candidate_review_points[]`，并至少说明 `subject_ref`、`candidate_reason`、
selector、cardinality 和 `UNK-*`。存量小写动作只可规范化为 `PROTO-OBS-ACT-*` 候选身份，不能借
规范化创造 `ACT-*` Product Truth。动态页面在浏览器中枚举指标、高风险动作和规则字段；候选可见但
不计进度，产品明确确认并绑定来源后才从候选移入 Declaration。

## 5. ReviewPoint 最小完整合同

每个 ReviewPoint 至少包含：

```yaml
ref: RVP-VIEW-EXAMPLE-001-SUBMIT
subject_ref: ACT-EXAMPLE-SUBMIT
owner_context_ref: VIEW-EXAMPLE-001
marker_required: true
target_ref: ACT-EXAMPLE-SUBMIT
target_selector: "[data-action='ACT-EXAMPLE-SUBMIT']"
target_mode: selector_exactly_one
title: 提交当前记录
business_status: confirmed
verification_status: not_run
evidence_origin: explicit_source
summary: 校验通过后提交当前记录，并在原页显示持久结果。
actor_refs: [ROLE-OPERATOR]
precondition_refs: [RULE-EXAMPLE-READY]
visible_result_refs: [REG-EXAMPLE-RESULT]
domain_result_refs: [STATE-EXAMPLE-SUBMITTED, EVT-EXAMPLE-SUBMITTED]
boundary_refs: [RULE-EXAMPLE-DUPLICATE]
acceptance_refs: [AC-EXAMPLE-SUBMIT]
source_refs: [REQ-EXAMPLE-001]
```

三条轴必须分开：

- `business_status=confirmed|pending_decision|gap|not_applicable`：业务是否已决定；
- `verification_status=not_run|passed|failed|blocked|not_applicable`：是否已有执行证据；
- `evidence_origin=explicit_source|prototype_inferred|implementation_observed|legacy_behavior|assumption`：
  事实从哪里来。

`RVP-*` 只是评审记录身份，不替代 `subject_ref`。没有真实来源时不得自动生成 `REQ/RULE/STATE/AC`。
人类卡片用一条紧凑状态行显示业务状态、验证状态和必要的证据来源，不创建三套工作流。`confirmed`
仍需有效来源；`passed` 仍需本次可解析 `ARUN/EVD`。原型中可见、模型自评或静态 Gate PASS 均不能
冒充业务批准或运行验收。

## 6. 当前上下文内编号与双向定位

- 每个 Context 按其 `review_point_refs` 数组顺序从 1 重新编号；Overlay 打开后从 1 开始，关闭后恢复
  父级编号，不使用全局、Journey 或 STEP 顺序。
- 可见 UI 目标对应的正式 ReviewPoint 必须 `marker_required=true`；marker 固定在真实目标旁并与 card
  同时绑定同一 `context/ref/number`。右栏不得出现没有左侧 marker 的编号说明；只有确无 UI 落点的
  系统规则才可 `marker_required=false` 并在卡片上说明原因。
- 点击 marker：滚动并高亮对应 card，同时给真实目标加可见框选；点击 card/右侧编号：只在
  `CurrentContextRoot` 内解析目标，滚动到目标并同时高亮 target、marker、card。三者选中态必须同步，
  目标使用 `data-review-target-selected="true"` 或等价可测试状态，并通过 outline/box-shadow 等明显焦点环
  呈现；只滚动、只高亮右栏或用不可见 class 记状态均不合格。
- 目标必须当前可见且恰好一个：0 个为 unresolved（`marker_required=true` 时 BLOCK），多个为
  ambiguous BLOCK。不得使用全局 `querySelector` 后取第一个可见节点。
- 跨页下游事实只作说明，不创建评审跳转。需要改变 CurrentContext 时必须操作产品自身菜单、链接或
  按钮。

## 7. FLOW/STEP/EDGE 与角色事实如何保留

FLOW/STEP/EDGE/STATE/DATA/AC/TEST 继续完整存在于 PRD、Product Truth 和机器 handoff：

- FLOW 投影为总览主链或当前 Context 的业务链说明；
- STEP 投影为 ReviewPoint 的处理、守卫、双结果、异常恢复与实现语义；
- EDGE 投影为当前功能的上游、下游和交接；
- STATE/DATA/规则/指标/AC/TEST 的详细正文归“边界与验收”。

右侧先让人连续读懂“这里做什么 → 从哪里来 → 会变成什么 → 失败怎么办”，再按需展开详情。产品、
前端、后端、测试需要的事实不得丢失，但不再用角色切换隐藏；Coding Agent 始终读取同 baseline hash 的
结构化 handoff，不从人类摘要推断实现。

## 8. 布局不得破坏产品

- 桌面说明区参与页面布局：产品可用宽度 = viewport - review panel width；可折叠，只有真正实现并
  验证拖拽手柄时才声明 `resizable=true`，否则如实为 false；默认不以
  `position: fixed` 覆盖产品主操作区。
- 产品弹窗、抽屉、Toast、全局错误和提交反馈的层级高于评审区；桌面固定业务浮层的右边界止于产品
  区，窄屏产品态恢复到视口右边界。评审区不得截获其点击或焦点。
- 宽表、看板、画布等可在不丢产品状态时切换为底部或全屏评审表面，但三个信息页签和 CurrentContext
  语义不变；页面画像不能衍生为新的一级模式。
- 窄屏允许“产品全屏 / 评审全屏”切换，必须保留 CurrentContext、产品状态、滚动位置和已选评审点。
- `UIACT-REVIEW-*` 在进入产品业务 dispatcher 前必须停止传播，或由业务 dispatcher 显式排除；任何
  评审切页、展开、记录或导入导出都不能触发产品 Toast、提交、导航或状态变更。
- 产品用 `innerHTML` 等方式动态重建页面/浮层时，运行时必须重建正式 marker 与 anchor；只能显示
  CurrentContext 的标号，父页面和其他隐藏 Context 标号必须隐藏。
- marker 必须有可点击尺寸、避让彼此且完整落在当前视口内；超出、重叠或盖住关键输入/动作都属于
  浏览器验收失败。右栏卡片默认显示摘要，详细实现与验收内容按需展开，避免把 PRD 全文铺在页面上。

是否真正不遮挡、不压缩关键列、不破坏浮层，必须用桌面与适用窄屏浏览器 ARUN 证明；静态 DOM/CSS
检查只能证明声明存在。

## 9. Product Fingerprint 与纯评审动作

Product Fingerprint 至少覆盖：活动视图、路由、活动菜单路径、展开菜单父级、面包屑、页面标题、
Overlay Stack、选中业务对象、业务状态，以及表单值、
checked/disabled、筛选、分页、选择集合的稳定 hash。Review Fingerprint 单独记录活动页签、当前评审点、
面板宽度/折叠、评审记录等评审状态。

每个 `UIACT-REVIEW-*` 执行前后必须满足 `ProductFingerprint(before) == ProductFingerprint(after)`；
只有真实 `ACT-*` 可以改变产品指纹，随后评审层重新解析 CurrentContext。静态扫描到点击/路由代码只能
提示风险，不能代替浏览器前后指纹证据。Fingerprint 必须只采集实际 DOM/产品状态的 observed 值；
Expected ProductLocation 另行逐字段 diff。违规必须进入 `window.__ADS_REVIEW_GATE__` 或等价可失败
浏览器 Gate 并让 ARUN 非通过，`console.error` 只能作为调试信息。

## 10. 分享、进度与评审记录

- 分享定位只包含 `baseline_ref + context_ref + optional review_point_ref + active_tab`，不包含
  Journey/Step/Role。首次 hydration 可先由产品路由落到目标 Context，再建立初始产品指纹；之后所有
  纯评审动作仍满足不变量。
- 收起后必须保留真正可操作的“展开评审”按钮，并验证收起→展开后 CurrentContext、产品指纹、活动
  页签和记录均不丢失；只有“收起”入口而没有反向处理器属于结构性 BLOCK。
- 进度分母是全部适用的已声明 ReviewPoint。浏览、切页签和点击编号不增加进度；只有
  `confirmed` 或 `accepted_with_gap` 的评审处置计入完成。
- R1/R2 评审记录必须持久化，稳定键为 `baseline + context + point`，处置为
  `unreviewed|confirmed|accepted_with_gap|blocked`，并保存评论、评审人、更新时间和 GAP。
- 单 HTML 至少支持 localStorage 与 JSON 导出/导入。baseline 不同不得复用旧记录。记录可经需求内核
  转化为 REV/GAP/DEC/CHG，但不能直接覆盖 Product Truth。

## 11. Manifest 与 DOM 最小合同

HTML 内嵌唯一 `<script type="application/json" id="review-workspace-manifest">`，按
`schemas/review-workspace.schema.json` 登记合同，不复制 PRD 正文。

```html
<main data-review-context-root="VIEW-EXAMPLE-001" data-review-context-type="VIEW">…</main>
<button data-review-ref="RVP-EXAMPLE-001" data-review-context="VIEW-EXAMPLE-001"
        data-review-number="1" aria-current="false">1</button>

<aside data-review-workspace="REVIEW-EXAMPLE-001" data-review-level="R1"
       data-review-active-tab="overview" data-review-current-context="VIEW-EXAMPLE-001"
       data-review-layout="participate-in-layout" data-review-resizable="false"
       data-review-collapsible="true" data-review-overlay-product-ui="false"
       data-review-current-context-control="read-only">
  <section data-review-tab="overview">…</section>
  <section data-review-tab="function_flow">
    <article data-review-point="RVP-EXAMPLE-001" data-review-context="VIEW-EXAMPLE-001"
             data-review-number="1" data-review-business-status="confirmed"
             data-review-verification-status="not_run"
             data-review-evidence-origin="explicit_source">…</article>
  </section>
  <section data-review-tab="boundary_acceptance">…</section>
</aside>
```

选中时，marker 与 card 同步 `aria-current="true"`，真实目标同步
`data-review-target-selected="true"` 并显示焦点环。根容器还须提供页签切换、窄屏切换、分享、进度和记录入口。所有纯评审动作使用
`UIACT-REVIEW-*`；产品动作继续使用 `ACT-*`。marker、card、manifest 三方的 context/ref/number 必须
一致。可移交的稳定动作至少包括 `UIACT-REVIEW-SELECT/TOGGLE/SHARE/RECORD/EXPORT/IMPORT`；
R1/R2 另有 `UIACT-REVIEW-TAB/COMPACT`。实现可复用统一 dispatcher，但每项仍须有可见结果。

## 12. 浏览器 ARUN 必测清单

R1/R2 至少执行并留证：

1. 初始 VIEW CurrentContext 正确；
2. 三页签可达且只改变 Review Fingerprint；
3. marker → card/target 和 card → target/marker 双向联动；两向都同时框选 marker、card、真实目标；
4. 打开 MODAL/DRAWER/POPOVER 后 Context 入栈并从 1 编号；
5. 关闭 Overlay 后恢复父 Context、编号、选择与滚动；
6. 跨页说明不导航，真实产品导航能改变 Context；
7. 未声明 Context 显示 GAP 且产品仍可操作；
8. 分享链接 hydration 到正确 Context/Point/Tab；
9. 浏览不推进进度，提交评审处置才推进；
10. Candidate Diff 不自动进入分母；
11. 桌面不遮挡产品主区，业务 Overlay/Toast 高于评审区；
12. 两个 Overlay 候选时按声明判定最上层，歧义被阻断；
13. 隐藏目标、零目标和同 Context 多目标均按合同拒绝；
14. 刷新后评审记录恢复，JSON 导出/导入可用；
15. baseline 变化后旧记录不被复用；
16. 适用时窄屏全屏切换保留产品状态；
17. R0 仍满足 Context、声明分母和指纹不变量。
18. 每个 VIEW 有且只有一个活动菜单叶子，或有可解释的 `menu_exempt`；
19. 菜单跳转、正文跨页入口、刷新/深链均同步路由、父级展开、面包屑、标题和 CurrentContext；
20. Overlay 继承父页面菜单位置，关闭后位置与父 Context 一并恢复；
21. 角色无权时菜单/快捷入口消失，直接深链拒绝且不泄露范围外数据。
22. 旧说明栏/角色镜头不可见，页面只有一个可见评审事实面；
23. 每个 `UIACT-REVIEW-*` 都不会落入业务动作 dispatcher 或产生产品 Toast/状态变化；
24. 动态重绘页面或浮层后，当前 Context marker 自动恢复且 marker/card/ref 仍一致；
25. 只显示 CurrentContext marker，全部可见 marker 不重叠、不越出视口且不遮挡关键产品动作；
26. 桌面业务固定浮层止于产品区，窄屏产品态恢复全屏，关闭后评审与产品位置均回到父 Context。

浏览器未执行时只能声明静态合同已通过并保留 ARUN GAP，不能称“可完美复现”“已验收”或“真实运行
无副作用”。

## 13. 冷读门禁

R1/R2 由未参与原讨论的产品、前端、后端、测试分别冷读。目标是在 3 分钟内沿产品入口找到当前功能，
复述输入、处理、可见结果、领域结果、主要异常和下一交接；声明评审点回忆率至少 80%，P0/P1 为
100%。记录找到入口时间、误猜规则、首次澄清、阻断 GAP 和证据。失败应修复信息投影、上下文或文字
层级，不得增加 Journey/Step/Role 导航。

## 14. 迁移与完成条件

旧五模式评审态迁移时：删除 Journey/Focus/Page/Acceptance 与角色一级切换；保留完整产品 DOM、动作
和状态仓；将 STEP/角色包内容合并回三个页签；按真实 VIEW/Overlay 建 `review_contexts`；重新生成
当前上下文编号；补 Candidate Diff、Fingerprint、分享、进度和持久化记录；最后执行浏览器 ARUN 与冷读。

完成必须同时满足：需求内核无回归；CurrentContext 可确定；ProductLocation 与菜单/路由/标题同步；声明评审点唯一且分母稳定；R1/R2 只有三
页签；纯评审动作产品指纹不变；Candidate Diff 不自动晋级；布局不遮挡；Overlay 可探测；目标在当前
上下文唯一；评审记录可持久化且不跨 baseline 污染；页面只有一个评审事实面；评审事件与业务事件隔离；
动态重绘后标号恢复且只显示当前 Context；标号可见、避碰、不越界；业务浮层不覆盖评审区。任何一项缺失
都不得包装为 5.4.7 Final。
