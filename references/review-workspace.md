# 人类评审工作台合同 / Human Review Workspace Contract

仅在用户明确确认评审版后加载。先读取 `prototype.md`；本文件只定义人类评审投影，不改变 PRD、
Product Truth、结构化 handoff 或验收证据的权威边界。

5.5.2 继续读取 `5.4.9 / RC4` 评审合同；这是子合同版本，不是 Skill 版本漂移。正式 manifest 以 `schemas/review-workspace.schema.json` 为准。下面的 DOM 片段仅解释绑定方式，不是完整可直接过门禁的实现。

图的触发依据业务依赖：仅有弹窗、抽屉或 secondary_context 不自动等于跨页业务链，也不因此强制每个只读浮层补流程图和正反例。实际状态迁移、跨角色交接及显式复杂度仍需对应图与验收。

先选使用方式：R0 用于当前功能的就近说明；R1 用于正式团队评审，包含三页签、记录/分享/进度与冷读；R2 为旧项目保留值，当前检查与 R1 相同，不暗含额外文档。新项目选 R0 或 R1；业务复杂不自动升级。三者都保留业务覆盖、真实上下文、准确定位、角色说明和无业务副作用。L0–L4 是另一条旧锚点兼容轴。

## 可生成起点

```powershell
python scripts/build_review_workspace.py init --output review-project
python scripts/build_review_workspace.py build --project review-project
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype review-project/prototype.html --prd review-project/requirement.md --stage specify --require-review-workspace
```

`init` 从已验证样例拆出可编辑的 PRD、页面/说明、样式、运行脚本和 manifest，`EDITING.md` 给编辑位置。它仍是设备维修教学业务，须替换成项目事实；不是空白项目过检证明。`build` 只拼接本地片段、绑定真实 PRD 的规范文本 hash、清空旧验证结论，输出离线单 HTML；不生成业务政策、不代替 gate/浏览器。大文件分块编辑后构建，避免单次输出截断；不能先写巨型 manifest 再缩业务来迁就它。

生成顺序：先用一个完整任务写清“谁从哪进入 → 输入与条件 → 成功变化与下一入口 → 拒绝/恢复”，在 PRD 和产品上走通；再在对应动作旁展开同源说明和角色要点，最后映射上下文/评审点/语义项。先确认这一纵向切片能被接手，再扩其他模块。每个模块读完应知道如何做和如何判断对错，而不是只知道去哪里查 ID。

机器字段查 `schemas/review-workspace.schema.json` 对应段，不必通读校验器：`baseline` 绑定来源；`review_contexts` 定页面/浮层；`review_points` 定动作说明；`semantic_coverage` 防字段/指标/系统规则漏项；`acceptance_examples` 定可执行输入与页面/业务结果。稳定 ID 的后缀用大写字母、数字、连字符，不用下划线。语义项为 gap 时，关联点须是 gap/pending_decision，不能仍宣称 confirmed；图按实际跨页/跨角色、状态及数据依赖选择，不能只为弹窗补图。

> **Review Explains, Product Operates.** 左侧始终是完整可操作产品；右侧只解释真实产品动作产生的当前
> 上下文。Context 定位置，Declaration 定评审点分母，Semantic Coverage 定功能完整性分母，Candidate Diff 防漏，Fingerprint 定副作用边界，
> Layout + Detection 保证真实可运行，Target Resolution 防绑错，Review Record 防丢结论。

## 1. 人类任务与禁止结构

完成标准是未参与原讨论的产品、前端、后端、测试能沿产品自身入口独立操作，在当前页面或业务浮层旁
理解用途、上下游、结果、规则、边界和验收，并能报告 GAP、开始实现或编写测试。每个页面及由它打开的
业务弹窗、抽屉、气泡都必须覆盖影响实现/验收的功能语义；仍需作者补讲指标、流转、权限、数据写入、
异常或二级页面功能即为 GAP。

R1/R2 只有三个一级页签：

1. `overview`：总览；
2. `function_flow`：功能与流转；
3. `boundary_acceptance`：边界与验收。

不得新增 Journey、Step Focus、Page、Acceptance 或产品/前端/后端/测试角色一级模式。复杂度只增加
页签内信息深度，不增加导航维度。R0 快速评审可不渲染三个可见页签，但仍必须声明
`CurrentContext`、`review_contexts` 分母并保证纯评审动作不改变 Product Fingerprint。

5.5.2 的 R0 在用户仅需就近说明时，可省略 `progress_contract`、`share_contract`、`review_record_contract` 及对应功能，不为过门禁增建签署工作台。R0 若声明或展示分享、记录或确认进度，仍须兑现相应合同；确认进度依赖真实记录，浏览不计确认。R1/R2 保留这三项要求。旧检查器对轻量 R0 仍可能要求全量合同，需使用 5.5.2 检查；既有完整合同继续兼容。此裁剪不取消范围/语义覆盖、上下文、精确目标、角色说明或无业务副作用。

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

构建起点见 [可运行工作台](../examples/medium-review-handoff/review-prototype.html) 与其 [业务规格](../examples/medium-review-handoff/requirement.md)。先按当前项目映射业务对象、规则和范围，再替换内容；不要从门禁代码逆向拼装工作台。

| 页签 | 唯一负责的完整内容 |
|---|---|
| 总览 | 背景/问题、目标与成功信号、角色表、范围/非目标、主链、变更摘要、P0/P1 摘要；复杂模块显示核心流程图并高亮 CurrentContext |
| 功能与流转 | CurrentContext、当前业务职责、上下游、带同号 marker 的自然语言说明、可见/领域结果；复杂评审点按需展开前端实现、后端处理、测试验收 |
| 边界与验收 | 详细规则、权限、指标、异常/恢复/幂等、少量正反例；按触发条件显示状态转换图或数据流图；最后提供默认收起的技术追溯 |

其他页签可摘要、定位或按需展开 owner 的同源内容，不另维护规则；当前动作旁应能读懂必要边界和验收。一个内容域只能有一个 owner；同一规则、状态机、指标公式
或验收正文在多个页签重复出现时记录 `PROTO-REVIEW-TAB-OWNERSHIP`。流程图、状态图和数据流图只在
确实满足 `prototype.md` 的触发条件时出现：总览显示核心流程和当前页面，功能与流转显示当前上下游，
边界与验收持有详细状态/数据/规则合同。简单单页 CRUD 的 `diagram_contract` 明确记录不画图理由，
不得为了“完整”添加装饰图。

### 3.1 人类主阅读面与技术追溯

5.4.9 起，右栏明确分成两个信息层，不再把稳定 ID、字段名和机器枚举混入功能说明：

- **主阅读面**使用操作者语言说明“谁在什么前提下做什么、页面看到什么、业务实际改变什么、失败如何
  恢复”。标题、状态和图节点都使用自然语言；不得显示 `VIEW-* / ACT-* / AC-*`、`leadId`、
  `pending_review` 等技术追溯文本。
- **按需实施详情**仅在一个评审点确实涉及写入、状态、权限、口径、跨边界或恢复时出现，使用默认收起
  的 `<details data-review-role-details data-review-detail-for="RVP-*">`，其中只保留三段：前端实现、
  后端处理、测试验收。简单查看、普通筛选和无独立规则的 CRUD 不机械展开。
- **技术追溯**全页只保留一个默认收起的 `<details data-review-trace>`；稳定 ID、字段原名、机器枚举和
  AC/来源映射全部放在这里。它帮助研发和 Agent 精确回链，但不承担业务解释，也不作为右栏第二真相。

`human_projection_contract.technical_terms[]` 声明本次必须隐藏到技术追溯的字段名和枚举。静态门禁检查
明显泄露、默认展开和追溯缺失；“是否说人话、是否足够理解”仍由未参与者冷读证明。

评审标注按所指对象解释已知规则：前端能据此实现入口、条件、反馈及恢复；后端能找到输入权威、允许状态/范围、写入或计算结果及重复处理；测试能拿到区分错误实现的输入与可观察预期。已有信息就近引用，不复制三份合同。“校验权限、保存数据、符合预期”不能代替该对象的具体约定；无关技术实现仍留给研发。

标注中的问题保留原 UNK 和影响，不能把待定口径改写成确定说明。抽查时把卡片、展开详情、边界样例和同版本 PRD 放在一起，用同一输入核对结果，再反查来源；尤其检查临界值、失败后副作用和下一入口。完整性从 PRD/产品实际功能向标注反查，不能只数已经画出的 marker。隐藏文本、脚本字符串或 JSON 声明不能代替读者展开后可读的说明。

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
不计进度，产品明确确认并绑定来源后才从候选移入 Declaration；晋级后必须从 Candidate Set 删除，
`candidate_review_points[].subject_ref` 与 `review_points[].subject_ref` 的交集必须为空。

### 4.1 Semantic Coverage：先定功能分母，再做克制投影

5.4.8 起的“克制”只压缩文字和重复，不允许缩减功能。先从同一基线的 PRD 页面合同、Stage 0、稳定锚点、
运行时语义扫描和冷读结果建立 `semantic_coverage_items[]`，再决定哪些项可按规则等价合并到一个
ReviewPoint。每个适用项必须在人类右栏恰好出现一次最小说明；有 UI 落点时还必须映射到同目标 marker。

必须进入语义分母的类型：

- `action`：会产生业务结果或改变下一动作的操作；
- `field_rule`：必填、条件、联动、计算、权限或校验字段；
- `metric`：每个可见指标及其独立口径；
- `state_transition`：允许流转、守卫、非法路径、撤回/回退；
- `permission_guard`：菜单、数据范围、动作和字段权限；
- `data_write`：持久化、覆盖、追加、同步、删除和审计；
- `event_handoff`：跨角色、页面、模块或系统的事件与下一入口；
- `error_recovery`：失败、超时、重复、部分成功、冲突、补偿和重试；
- `business_region`：承载独立任务的区域；
- `overlay`：业务弹窗、抽屉、气泡及其自身功能；
- `role_path`：核心角色从入口到结果的操作路径。

每项状态只能是 `covered`、`gap` 或 `not_applicable`：`covered` 必须映射同 Context 的正式 RVP 并显示
一句最小充分说明；`gap` 还必须绑定 `UNK-*`，P0/关键 P1 阻断完整交接；`not_applicable` 必须有来源和
理由且不能占用右栏。一个 ReviewPoint 只在语义项对象、规则、结果和验收等价时才可合并多项；不能用
“页面入口”“核心操作”“处理结果”三个泛化点代替页面功能。

`coverage_id` 与 `(owner_context_ref, subject_ref)` 各自唯一；同一对象的多个语义维度在该记录内说明。`gap` 语义项只能映射业务状态同为 `gap` 的评审点，不能借 confirmed 的卡片覆盖未定规则。

每个 `VIEW-*` 必须用 `PAGE-CONTRACT` 的 `surfaces` 与 Context 的 `surface_types` 双向对齐。声明
`metrics` 就必须逐项存在 `METRIC-*` 语义；声明 `workflow` 就必须有状态流转；声明 `drawer_form` 就
必须通过 `secondary_context_refs` 指向可到达的独立业务 Context。发现 `role=dialog` 或
`data-testid=modal-/drawer-` 却没有 CurrentContext 时直接 BLOCK。

右栏使用 `data-review-semantic-ref="SCOV-*"` 和 `data-review-semantic-owner` 呈现最小说明。简单筛选、
显然按钮或完全等价规则可以一句话/区域合并；指标、状态、权限、数据写入、交接、异常和二级页面详情归
“边界与验收”，不能只留一句泛化摘要。详细公式和测试仍以同 hash PRD/handoff 为权威。

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
implementation_detail:
  required: true
  reason: 提交会写入业务对象并触发后续事件
  roles: [frontend, backend, qa]
```

三条轴必须分开：

- `business_status=confirmed|pending_decision|gap|not_applicable`：业务是否已决定；
- `verification_status=not_run|passed|failed|blocked|not_applicable`：是否已有执行证据；
- `evidence_origin=explicit_source|prototype_inferred|implementation_observed|legacy_behavior|assumption`：
  事实从哪里来。

`RVP-*` 只是评审记录身份，不替代 `subject_ref`。没有真实来源时不得自动生成 `REQ/RULE/STATE/AC`。
正式交接时，`subject_ref/source_refs/precondition_refs/visible_result_refs/domain_result_refs/boundary_refs/
acceptance_refs/target_ref` 必须逐项解析到本次提供的权威 PRD 稳定 ID 索引；Product Truth 为主源时也
必须把这些 ID 投影进同 hash PRD。`PROTO-OBS-*` 仅作为 `gap + prototype_inferred` 例外，不能替代
基线事实。
人类卡片用一条紧凑状态行显示业务状态、验证状态和必要的证据来源，不创建三套工作流。`confirmed`
仍需有效来源；`passed` 仍需本次可解析 `ARUN/EVD`。原型中可见、模型自评或静态 Gate PASS 均不能
冒充业务批准或运行验收。

## 6. 当前上下文内编号与双向定位

- 每个 Context 按其 `review_point_refs` 数组顺序从 1 重新编号；Overlay 打开后从 1 开始，关闭后恢复
  父级编号，不使用全局、Journey 或 STEP 顺序。
- 评审意见导致修改、删除或新增时，先按 `change-acceptance.md` 建立 `CHG-*` 和新基线。修改项可在业务
  身份不变时保留 `RVP-*`；删除项退出新 Declaration；新增项取得新的 `RVP-*`。随后按新 Declaration
  重算可见序号，禁止把显示数字当永久身份或把旧记录静默套到新点上。
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

右侧先让人连续读懂“这里做什么 → 从哪里来 → 会变成什么 → 失败怎么办”，再按需展开前端实现、后端
处理和测试验收。稳定 ID、字段原名、枚举和机器索引统一进入默认收起的技术追溯。产品、前端、后端、
测试需要的事实不得丢失，但不再用角色切换隐藏；Coding Agent 始终读取同 baseline hash 的结构化
handoff，不从人类摘要推断实现。

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

`selection_hash` 仅是业务对象选择集合，绝不是被点中的评审编号。marker 用独立定位层或目标内部不占位的锚点，不能作为 Grid/Flex 的业务兄弟项挤走卡片。正文、浮层、不同窗口尺寸下分别看实际呈现，数据指纹相等不证明布局未受影响。

每个 `UIACT-REVIEW-*` 执行前后必须满足 `ProductFingerprint(before) == ProductFingerprint(after)`；
只有真实 `ACT-*` 可以改变产品指纹，随后评审层重新解析 CurrentContext。静态扫描到点击/路由代码只能
提示风险，不能代替浏览器前后指纹证据。Fingerprint 必须只采集实际 DOM/产品状态的 observed 值；
Expected ProductLocation 另行逐字段 diff。违规必须进入 `window.__ADS_REVIEW_GATE__` 或等价可失败
浏览器 Gate 并让 ARUN 非通过，`console.error` 只能作为调试信息。

## 10. 分享、进度与评审记录

本节功能对 R1/R2 必需；R0 仅在启用对应功能时适用。未启用时不生成按钮、空记录或假进度。

- 分享定位只包含 `baseline_ref + context_ref + optional review_point_ref + active_tab`，不包含
  Journey/Step/Role；`hydrate_on_load` 固定为 true。首次 hydration 先由产品路由落到目标 Context，再建立初始产品指纹；之后所有
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

`baseline.hash` 对 UTF-8 文本读取后的内容计算 SHA-256，通用换行会归一化为 LF，再编码 UTF-8；它不是原文件字节哈希。包完整性哈希另按原始字节计算，二者不能混用。页签之外还需实际提供 `data-review-progress`、`data-review-progress-denominator`、`data-review-share-locator`、`data-review-records`，并按 Schema/诊断核对 PAGE-CONTRACT、内容 owner 与语义分母；不要靠补无关 DOM 锚点修复 JSON 字段错误。

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
    <p data-review-semantic-ref="SCOV-EXAMPLE-001" data-review-semantic-owner="function_flow"
       data-review-context="VIEW-EXAMPLE-001">校验通过后提交，并在原页显示持久结果。</p>
  </section>
  <section data-review-tab="boundary_acceptance">…</section>
</aside>
```

选中时，marker 与 card 同步 `aria-current="true"`，真实目标同步
`data-review-target-selected="true"` 并显示焦点环。根容器按实际启用功能提供页签、窄屏、分享、进度和记录入口。所有纯评审动作使用
`UIACT-REVIEW-*`；产品动作继续使用 `ACT-*`。marker、card、manifest 三方的 context/ref/number 必须
一致。基本动作是 `UIACT-REVIEW-SELECT/TOGGLE`；启用分享增加 `SHARE`，启用记录增加 `RECORD/EXPORT/IMPORT`（均沿用 `UIACT-REVIEW-` 前缀）。R1/R2 包含上述全部功能及 `TAB/COMPACT`。实现可复用统一 dispatcher，但每项仍须有可见结果。

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
27. 每个 VIEW 的 PAGE-CONTRACT 与 `surface_types` 一致；全部适用 `SCOV-*` 在右栏恰好出现一次；
28. 指标页面逐个核对 `METRIC-*` 口径，工作流页面核对流转守卫，业务弹窗/抽屉进入独立 Context；
29. 简单项合并后仍能逐项回溯语义分母，P0/P1 GAP 会阻断完整交接。
30. 浏览器可见规则文本与 PRD 逐字核对；正文中的 `<`、`>` 等比较符必须使用 HTML 实体或安全文本写入，不能被浏览器误解析为标签而吞字。

浏览器未执行时只能声明静态合同已通过并保留 ARUN GAP，不能称“可完美复现”“已验收”或“真实运行
无副作用”。

## 13. 冷读门禁

R1/R2 由未参与原讨论的产品、前端、后端、测试分别冷读。目标是在 3 分钟内沿产品入口找到当前功能，
复述输入、处理、可见结果、领域结果、指标口径、允许状态流转、主要异常、二级页面和下一交接；声明
评审点回忆率至少 80%，P0/P1 及核心角色路径为 100%。记录找到入口时间、误猜规则、首次澄清、阻断
GAP 和证据。失败应修复信息投影、上下文或文字
层级，不得增加 Journey/Step/Role 导航。R1/R2 的状态只能是 pending/passed/failed/blocked，不能用
`not_applicable` 逃避；只有 R0 可声明不适用。

## 14. 迁移与完成条件

旧五模式评审态迁移时：删除 Journey/Focus/Page/Acceptance 与角色一级切换；保留完整产品 DOM、动作
和状态仓；将 STEP/角色包内容合并回三个页签；按真实 VIEW/Overlay 建 `review_contexts`；重新生成
当前上下文编号；补 Candidate Diff、Fingerprint 及当前等级/实际启用的分享、进度和持久化记录；最后执行适用的浏览器 ARUN 与冷读。

大规模存量分批顺序：先保留并回归产品路径 → 映射真实页面/浮层上下文 → 每条核心链补规则与角色说明 → 再补候选/语义映射和运行验证。批次写明已覆盖、待覆盖与源分母；不能把已完成子集说成全量。当前 manifest 的评审级别是工作区级，不支持同一工作区随意混用 R0/R1；可分独立范围交工作区并保留原产品全范围，不未经授权删页。ARUN 可复用已有浏览器测试产生的真实证据，不要求手写第二套点击日志；未执行项保留未执行。

完成必须同时满足：需求内核无回归；CurrentContext 可确定；ProductLocation 与菜单/路由/标题同步；声明评审点唯一且分母稳定；R1/R2 只有三
页签；纯评审动作产品指纹不变；Candidate Diff 不自动晋级；布局不遮挡；Overlay 可探测；目标在当前
上下文唯一；启用的评审记录可持久化且不跨 baseline 污染；页面只有一个评审事实面；评审事件与业务事件隔离；
动态重绘后标号恢复且只显示当前 Context；标号可见、避碰、不越界；业务浮层不覆盖评审区；
PAGE-CONTRACT、语义分母、右栏最小说明和 marker 映射闭合；指标、工作流、二级 Context 与核心角色
路径无静默遗漏。任何一项缺失都不得包装为 5.4.9 完整评审交接。
