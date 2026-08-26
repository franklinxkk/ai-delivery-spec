---
name: ai-delivery-spec
description: Use for creating, changing, reviewing, reverse-engineering or accepting requirements, PRDs, prototypes, competitor material or existing systems, including any small UI/field/column/tab/dropdown/legacy-HTML change and direct PRD/prototype generation. Always invoke regardless of size or clarity. Deliver the smallest complete, reviewable, implementable, traceable and testable artifact at the target stage. Covers framing through acceptance; excludes scheduling, coding, CI/CD, deployment and operations. 中文：用于任何新增、修改、评审、反推或验收需求、PRD、原型、竞品或存量系统；写/改一个小功能、加字段/列/页签/下拉、旧 HTML 小改、直接生成 PRD/原型也必须调用。按目标阶段交付最小完整、可评审实施追溯验收的产物；不负责排期、编码、CI/CD、部署和运营。
---

# AI Delivery Spec 5.4.7 — Requirement Management Kernel｜人机共用需求管理内核

让业务、产品、设计、前后端、架构、测试、合规和 Coding Agent 从需求任一阶段进入，共用一条产品事实主线，取得当前所需的最小合格产物后离开；用户明确要求端到端时持续到目标完成。

锁定任务起始语言并贯穿对话、PRD、原型、图、测试和可见状态；只有用户明确要求才双语。人类可见内容先写用户语言，括号保留必要机器原值；稳定 ID、代码、API、字段、Schema、公式不翻译。YAML/JSON 可保留键名与枚举，但交付须附同语言摘要。Gate 只证明静态合同，不证明业务正确、浏览器行为、真实实现或客户验收。

## 1. 先选最轻工作深度

- `direct`：来源明确、局部、可逆，不改变跨模块状态、数据权威、权限/指标、迁移、法规安全或高影响 AI 写回。直接交付差异、边界、正反验收和未证明事项；无未知则零澄清，不建生命周期文件。
- `standard`：跨角色/页面/模块，或存在状态、数据、异常、集成和正式交接。使用需求卡或统一 PRD，按适用切面闭环。
- `governed`：强审计、多次变更/多投影、敏感/受监管、不可逆副作用或复杂跨系统权威。启用 Product Truth、正式评审/基线、变更和证据治理中真正需要的部分。

工作深度、风险切面和证据等级必须正交记录：`artifact_mode=direct|card|prd`；`risk_facets=[]`；`evidence_level=static|browser|real_system|customer_acceptance`。旧 `L0-L4` 仅为工具兼容映射，不再让一个数字同时冒充文档、风险、原型和验收等级。详见 `references/stages.md`。

## 2. 识别进入点与停止点

内部识别 `entry_stage` 与 `target_stage`。工作站为 `frame → explore → intake → clarify → specify → review → baseline`，基线可进入 `change` 或 `acceptance`；正式 `REQ-*` 从 intake 开始。阶段是路由地图，不是执行清单。

显式目标和否定约束最高优先；已有证据不重跑。目标模糊时先在一轮内完成“发散选项 → 推荐聚焦 → 深化关键链路”，再只问会改变范围、权威、风险或验收的决策。一句话要求 HTML/原型时，默认目标是**可实施产品原型**而不是立即猜完页面：先说明“目标已记住、当前还缺什么”，用决策树持续关闭会阻断原型的 P0；澄清和详细需求只是中间工作，不能停在需求清单或无解释地不出 HTML。只有用户明确说“先看效果/概念原型/低保真/允许合理假设/先画再聊”时，才可先交带假设与 GAP 的概念候选；它不得标为基线、可开发、已评审或已验收。P0 未知项必须有责任人、影响范围、阻断阶段和退路；到达阻断阶段前不得伪装闭合。

## 3. 每次只加载一个有效切片

| 当前任务 | 只读取 |
|---|---|
| 阶段、轻重、交接、断点 | `references/stages.md` |
| 来源、竞品、现状、澄清 | `references/discover.md` |
| 准入、评审、基线、责任 | `references/lifecycle.md` |
| PRD、字段、规则、指标、接口 | `references/specify.md` |
| Stage 0、页面合同、原型、视觉 | `references/prototype.md` |
| 可见评审投影（仅确认后） | `references/review-workspace.md` |
| 变更、追溯、验收 | `references/change-acceptance.md` |
| 大输入、切片、Agent 交接 | `references/context.md` |
| 工具适配或故障 | `references/tool-adapters.md` / `references/troubleshooting.md` |
| 领域证据 | `scripts/query_domain.py --domain <pack> --section "<heading>"` |

不要加载 README、`maintainer/`、全部模板/示例/领域包或整个仓库。材料规模、链路数量或上下文预算触发切片时读取 `references/context.md`，不要用固定文件大小机械升级。细反例只进脱敏维护回归，不注入日常上下文。

## 4. 一条事实主线，按需投影

实时对话先交付判断，不展示内部 YAML/ID。持久化只在跨会话、跨角色、审计、变更或工具校验时发生。默认最小主产物：frame/problem brief；explore/solution sketch；clarify/requirement brief；specify/需求卡或统一 PRD；review/baseline 复用同一规格并绑定签署、版本/hash；change/acceptance 回链当前基线。Product Truth 只在多投影、反复变更、血缘或强审计确有需要时启用。

客户演示/需求确认默认产品模式。只有用户明确要求评审版，或在首次交开发前确认后，才生成可见评审投影；拒绝后同一基线不重复询问。评审态遵守 `Review Explains, Product Operates`：左侧始终是完整可操作产品，右侧只解释真实产品动作产生的当前页面/业务浮层上下文。R1/R2 人类一级导航固定为“总览 / 功能与流转 / 边界与验收”，不得再增加旅程、步骤、页面或产品/前端/后端/测试角色模式；复杂度只增加信息深度。`review_contexts` 声明评审点并确定分母，Candidate Diff 只防漏、不自动入选；纯评审动作不得改变 Product Fingerprint。FLOW/STEP/EDGE/STATE/DATA/AC/TEST 保留在同 hash 的 PRD 与结构化 handoff 中，并按当前上下文投影，不从右栏文案猜规则。确认评审版时完整读取 `references/review-workspace.md`。

Candidate 与 Declaration 必须是物理分离且 `subject_ref` 不重叠的数据集合：扫描稳定锚点、存量小写 `data-action` 或运行时动态页面只能生成带 `candidate_reason` 的 `candidate_review_points`，不得 append 到正式评审点或改变进度。`review_point_id` 只标识评审记录，`subject_ref` 才引用真实 Product Truth；正式 ReviewPoint 的 subject/source/precondition/result/boundary/AC 必须在本次 PRD 基线可解析。只有原型观察时使用 `PROTO-OBS-* + business_status=gap + evidence_origin=prototype_inferred`，禁止自动伪造 `REQ/RULE/STATE/AC` 或标成已确认。指标候选必须列出可见指标，并要求产品在开发前冻结对象、公式/分子分母、时间字段与窗口、状态过滤、去重、数据权威、刷新时点、空值/失败、单位精度与下钻条件。

评审态不得把真实导航降级成静态装饰。每个 `VIEW-*` 必须绑定唯一可见菜单路径，或说明为什么是扫码页、H5 独立页等无菜单入口；页面切换同步活动菜单、父级展开、路由、面包屑、标题和 `CurrentContext`。业务浮层继承父页面位置，只改变浮层 `CurrentContext`。任何静态假菜单、位置漂移或评审动作改变产品位置都阻断交付。

同一产物只能有一个可见评审事实面：迁移存量评审版时停用旧说明栏/角色镜头，不能让新旧评审层并存。`UIACT-REVIEW-*` 必须与业务 `ACT-*` 事件隔离。每个有 UI 落点的正式评审点都必须在左侧目标旁显示同号 marker；右侧不得出现没有左侧落点的“1/2/3”。点击 marker 或右侧卡片时，当前 marker、卡片和真实目标必须同时形成可见选中/框选态并互相滚动定位。产品动态重绘后须恢复当前 Context 的正式标号，只显示当前 Context 标号，并在浏览器中证明标号不重叠、不越出视口。桌面业务浮层只能占产品区域，不能盖住评审栏；窄屏切换回产品时恢复业务浮层全屏。右栏卡片默认摘要、按需展开，不复制整份 PRD。

CurrentContext 必须由 manifest 的 detection 合同统一解析最上层业务浮层，不为单个原型硬编码特例。标号解析只允许 `CurrentContextRoot` 内当前可见且恰好一个目标；零个显示 unresolved，多个 BLOCK ambiguous，禁止取第一个或回退到 Context Root。`target_mode=context_root` 只允许 `VIEW/REG` 页面方向标号；`ACT/FLD/METRIC/STATE` 必须 `selector_exactly_one`。收起与展开、产品/评审切换、页签、记录、导入导出和分享都要跑双向浏览器验收；Fingerprint 违规必须进入可失败 Gate，不能只 `console.error`。分享链接必须在打开时校验 baseline 并恢复产品上下文/页签/评审点；R1/R2 冷读不得写不适用，未执行保持 pending/blocked。无法自动重开业务浮层时明确 GAP。

存量系统先做 Stage 0：页面、角色、入口、动作/处理器、状态、实体、字段/指标、数据源、代表数据和关键链可达性。未经批准不得丢失基线功能，也不得新增角色、页面、实体、审批、指标、状态或技术伪精确。权限、外部数据方向、指标口径、复杂流程/状态/数据流的详细合同按对应参考执行。

## 5. 来源、未知与安全

来源先分权威与用途：业务机会、产品决定、工程约束、评测任务、合同/法规、存量观察和推断不能互相替代。读取材料时先扫描凭据、令牌、私钥、个人/客户敏感信息；发现后停止复制和公开处理，只保留脱敏副本、内容 hash 与 `SECRET-*` 引用，原值进入受控密钥系统或隔离区。来源冲突形成具名决定，不能按文件更新或详细程度擅选权威。

规格按模块纵切：目标 → 角色旅程 → 页面/数据 → 规则/状态 → 指标 → 异常恢复 → 验收；横切权限、接口/事件、审计、兼容和 NFR 只在适用时加入。每个 `REQ-*` 绑定来源、行为、规则、AC、测试和证据并支持双向追溯；缺语义时人和 Agent 返回 GAP，禁止发明。

已基线需求投影给 Coding Agent 时，可在现有 handoff 中附 `execution_constraints`：受保护表面、允许/禁止动作、环境/密钥引用、必需证据和回滚责任人。它约束实现，不新增研发阶段，也不把部署、运维或项目管理纳入本 Skill。

## 6. 门禁与完成

静态门禁只在目标里程碑运行，修复后重跑；默认按根因输出。开放 P0/关键 P1 未知不得称开发就绪或完整验收；单产物 PASS 不等于交付闭环。正式最终交接运行 `gate --profile full` 或 handoff 组合门禁，并明确 `not_proven`。

```bash
python scripts/ai_delivery_spec_cli.py gate --profile clarify --artifact requirement-brief.md
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd PRD.md
python scripts/ai_delivery_spec_cli.py gate --profile full --prd PRD.md --prototype app.html --manifest handoff.yaml
```

统一状态保持 `PASS`、`REVIEW_COMPLETE_WITH_GAPS`、`BLOCKED_BY_P0_UNKNOWN`、`BLOCKED`。模板使用语言无关 `<!-- ADS:* -->` 锚点；断点保存相对路径、阶段和 SHA-256，漂移、缺失或路径越界必须阻断。

## 7. 边界

本 Skill 管问题定义、方案探索、需求准入、澄清、统一规格、原型、评审基线、变更影响、追溯与需求验收。Sprint、估时/排期、编码、源码管理、CI/CD、部署、监控和运营属于下游；这里只记录必要引用。私有扩展不得静默覆盖绑定规则或联网外发。任何“最好/生产可用/客户已验收”主张都必须有独立、可复现且边界清楚的对照证据。
