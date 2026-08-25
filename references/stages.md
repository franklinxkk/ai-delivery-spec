# Stage Workstations｜需求阶段工作站（5.4）

本页只在用户要从特定阶段进入、停止、交接或续跑时加载。它不是另一条瀑布流程，也不是必须逐项执行的检查表：只运行目标所需的工作站，不补跑无关前序；路由过程默认静默，不把内部阶段术语交给用户。

## 0. 先走快速小改旁路

阶段工作站用于管理复杂度，不应制造复杂度。一个来源明确、范围局部、可逆且不改变跨模块状态、外部数据权威、权限范围、指标口径、迁移兼容、法规/安全责任或高影响 AI 写回的改动，默认走快速小改：只检查触达面，直接交付目标，用一个短屏说明差异、边界、正反验收和未证明事项，不创建阶段文件、不显示 L0/内部 ID、不逐站过门禁。

出现任一风险才升级到标准需求或治理交付，并只补该风险需要的工作站：

- 多角色/多页面之间存在状态守卫、回退、并发或责任交接；
- 引入外部集成、双向同步、数据权威变化、指标/金额计算或迁移；
- 权限、隐私、法规、安全、医疗、金融、执法或不可逆副作用改变；
- 需要跨会话/跨团队基线、Coding Agent 精确实施合同、正式验收或审计。

升级时用用户语言说明具体触发器；不得只因“ToB/ToG”“有 PRD”“要给开发”就默认跑完整治理链。

### 三种工作深度，不再用一个等级承载四种含义

先选人类可理解的工作深度，再独立声明风险与证据：

| 工作深度 | 默认主产物 | 典型出口 |
|---|---|---|
| `direct` | 直接修改/结论 + 差异、边界、正反验收 | 当前目标已交付，无阻断未知 |
| `standard` | 需求卡或统一 PRD；按需原型/交接 | 跨角色行为、状态、数据和 AC 可独立复现 |
| `governed` | 同一 PRD + 必要 Truth/评审/变更/证据侧车 | 权威、签署、血缘、变更和证据边界闭合 |

这三个轴必须正交：

```yaml
delivery_profile:
  artifact_mode: direct | card | prd
  risk_facets: [] # state、authority、integration、metric、permission、privacy、regulated、irreversible_ai_write 等
  evidence_level: static | browser | real_system | customer_acceptance
```

`artifact_mode` 决定写多少；`risk_facets` 决定必须补哪些合同；`evidence_level` 只表示实际取得的证据上限。高风险不自动等于长文档，长 PRD 也不证明高证据。现有 CLI、Schema 和历史产物继续接受 `L0-L4`，兼容映射为：L0≈direct，L1≈card，L2-L4≈prd；原等级只驱动旧门禁，不得再作为人类主要说明，也不得越级推断风险或验收状态。

## 1. 两层模型

- `frame`、`explore` 是准入前工作区，用于把问题和选项想明白；不创建正式 `REQ-*`，不把假设伪装成需求。
- `intake → clarify → specify → review → baseline → change/acceptance` 是受治理的正式需求生命周期；`REQ-*` 从 intake 开始。
- baseline 不是第二份文档，而是“统一 PRD/需求卡 + 评审结论 + 权威来源 + 版本/hash”的受控状态。
- change 与 acceptance 可以多次发生，但必须回链当前基线；研发任务、代码、部署和运营不属于本 Skill。验收结论交给外部交付/发布工具，线上反馈只作为新 `SRC-*` 回到 intake 或已基线 `CHG-*`，不在本 Skill 内追踪上线状态。

```text
问题定义(frame) → 方案探索(explore) → 准入(intake) → 澄清(clarify)
→ 规格(specify) → 评审(review) → 基线(baseline) ↔ 变更(change)
                                              └→ 验收(acceptance) → 外部发布/交付引用
                                                                  └→ 新 SRC → intake/CHG
```

## 2. 语义路由，不用关键词猜意图

按以下优先级确定 `entry_stage` 和 `target_stage`：

1. 用户明确指定的目标产物/停止点最高优先；“不要写 PRD，只做澄清”等否定约束高于“PRD”关键词。
2. 已有产物决定可续接位置，但不能强迫用户重跑已完成阶段；先核对版本、来源和 hash 漂移。
3. 未明确目标时，先用一轮“发散选项 → 推荐聚焦 → 深化关键链路”交付可用判断，再只询问会实质改变范围的决策；不要让用户先回答整套问卷。
4. 单次明确任务在目标阶段停止；用户明确要求端到端交付时持续到目标，不把中间模板或一次静态 PASS 当成完成。一句话请求已把 HTML/原型列为目标时，需求澄清和详细需求清单属于中间工作，不得提前停止，也不得无解释地不生成目标产物。
5. `route-stage` 只检查显式目标、已有产物和确定性前置条件，绝不解析自然语言关键词：

```bash
python scripts/ai_delivery_spec_cli.py route-stage --target clarify --artifact requirements/problem-brief.md
```

文档语言在任务起始时按用户明确要求或主要交流语言锁定，并由后续工作站继承；“继续”“下一步”不重置
语言，只有用户明确切换时才更新。标题、正文、提问、表格、图、页面文案、评审说明和验收摘要均使用
该语言；双语必须显式要求。机器 YAML/JSON、代码、稳定 ID、API/字段和枚举保持原值，但 intake、
review、change、acceptance 等默认最小产物为机器文件的工作站，在对用户交付时还必须附同语言的人类
可读摘要，不能只返回机器键值。全英文任务的标题、问题、表头、图节点、测试、评审说明和门禁诊断均
不得泄露中文模板；全中文任务不得泄露裸英文工作站/BDD 标签。混合输入未指定时取主要交流语言。
## 3. 九个工作站与最小产物

| 工作站 | 适用问题 | 默认最小产物 | 出口条件 | 对应轻门禁 |
|---|---|---|---|---|
| frame | 到底是谁在何时遇到什么问题 | 一份 `problem-brief.md` | 用户/痛点时刻/成功信号/事实与假设可区分 | `gate --profile frame` |
| explore | 应该做什么，是否有更小方案 | 一份 `solution-sketch.md`，假设内嵌 | 至少两个方案+不做选项；有最小验证与停止条件 | `gate --profile explore` |
| intake | 是否值得进入正式设计、用多重规格 | `intake.yaml` + requirement register | `REQ-*`、价值、复杂度档位、依赖、优先级、迭代归属、交付形态 | intake schema + `triage` + requirement gate |
| clarify | 规则、边界、角色和异常是否已决 | 一份 `requirement-brief.md`；复杂审计可用 Discovery Contract | 决策有依据；P0/P1 未知项有责任人、阻断阶段和退路 | `gate --profile clarify` |
| specify | 人与 Agent 是否能实现同一口径 | 一份需求卡或统一 PRD | 适用模块纵切闭环；横切合同和机器附录就近可查 | `gate --profile prd` |
| review | 各责任角色是否签署或提出缺口 | `review-record.yaml` | P0/P1 发现关闭；`required_review_types` 均有结构化签署 | `validate_review_record.py` |
| baseline | 哪个版本是唯一权威 | 同一规格 + review/authority/version/hash 元数据 | 权威来源、开放未知项、版本和消费方同步清楚 | `gate --profile prd --stage baseline` |
| change | 改动影响了谁、什么字段/规则/AC | `change-package.yaml` | diff、双向影响、审批、同步、回归和版本闭合 | change validator / impact |
| acceptance | 需求结果是否真的被执行验证 | `ARUN-*.yaml` | 正反用例、证据、遗留问题、条件和签署回链 | acceptance validator / gate |

实时脑暴、比较和澄清不是必须持久化的产物。只有跨会话、跨角色复用或需要治理时才拆 `assumption-register.yaml`；多决策人、审计或跨需求复用时才拆决策侧车。不要为“九阶段”机械生成九个文件，也不要在到达目标前逐站运行门禁。

### 一句话要 HTML：先区分交付成熟度，不把“要原型”误解为“允许猜需求”

| 用户表达的真实意图 | 立即动作 | 允许的原型状态 | 禁止声明 |
|---|---|---|---|
| “做一个 XX HTML/原型”，未说明先看效果 | 记住原型目标；说明当前阻断项；按依赖批次反问会改变范围/规则/权限/状态/指标/数据的 P0，关闭后直接生成 | 可实施产品原型 | P0 未闭合时假装可开发，或只给需求清单后停止 |
| “先看效果/概念原型/低保真/允许合理假设/先画再聊” | 可立即生成最小可操作概念候选，同时列出假设、GAP、P0 和下一轮验证 | `concept_candidate` / `demo_slice` | 基线、可开发、完整 PRD、已评审、已验收 |
| “不要问，先画一个”但未授权业务假设 | 只可假设可逆视觉与布局；业务规则缺口显示待确认、隐藏受影响能力或提供安全回退 | 视觉骨架或受限概念候选 | 发明权限、指标口径、数据权威、状态流转、法规结论或不可逆 AI 写回 |
| “附件需求已冻结，生成可开发 HTML” | 先核对来源、版本和 P0；闭合则直出，存在阻断则指出精确缺口并继续收敛 | 可实施产品原型 | 因“已冻结”三个字跳过证据核对 |

第一次回复至少让用户知道：目标产物仍是 HTML、当前为何还不能安全生成、正在确认第几组关键决策、确认后会继续到哪里。反问按依赖分批，不一次抛整套问卷；同一答案不重复问。用户只要求 HTML 时不机械附送 PRD；用户要求端到端、正式交接或 PRD 时，才把同一已确认事实投影为对应文档。

原型用于探索、售前、客户演示或客户确认时默认产品模式。只有用户明确要求“评审版”“评审模式”“编号
标注”或“评审抽屉”等可见研发投影时才直接生成；“交开发”“给前后端/测试看”“开需求评审会”只说明
消费方，必须先询问一次是否生成评审模式，未确认时继续产品模式。一句话需求经澄清/规格/基线首次
进入原型且评审偏好尚未表达时，也询问一次是否同时生成评审版；问题不阻断产品模式，未回复时继续
产品模式。显式“我要评审版”已经构成确认；明确拒绝或延后后，同一需求基线内不重复询问。正式生命周期
的 review 工作站负责签署与缺口关闭，不等于可见的原型评审模式；“评审现有原型”本身不授权修改页面
或生成评审模式。评审模式是同一原型的精简人类投影，Coding Agent 使用结构化 handoff；跨模块流程、受守卫状态机和跨系统数据流按 `references/prototype.md` 条件化配图。

英文意图等价：`show me a concept first / rough prototype / low-fidelity / make reasonable assumptions` 允许概念候选；普通 `build an HTML prototype` 仍先关闭原型阶段 P0。`review version / review mode / numbered annotations / review drawer` 可直接确认评审投影；
`hand this to engineering / frontend, backend and QA will use it / requirement review meeting` 只说明消费方，
仍需确认一次。`customer demo / sales demo / product prototype` 默认产品模式。确认问题必须使用当前任务语言。

## 4. Skill 使用者角色在各工作站如何进入和离开

| 角色 | 常见进入点 | 读取/贡献 | 可独立决定 | 必须交接 |
|---|---|---|---|---|
| 业务/客户 | frame、clarify、review、acceptance | 痛点、业务事实、权威口径、签署结果 | 自身业务目标与授权范围内的规则 | 合同、法规、跨组织冲突给对应责任人 |
| 产品 | 任意工作站 | 问题、选项、准入、统一规格、变更影响 | 可逆产品取舍和文档组织 | 超授权业务/法律/技术约束 |
| UX/设计 | explore、clarify、specify、review | 用户路径、信息架构、页面状态、可用性证据 | 交互方案选项 | 业务规则和品牌方向签署 |
| 前端 | clarify、specify、review | 页面/区域/控件/字段/动作/状态/异常/锚点 | 可实现性建议 | 不得发明业务规则、权限或验收口径 |
| 后端 | clarify、specify、review | 数据流、状态流、规则、幂等、接口/事件和恢复 | 可实现性与技术约束 | 不得改变业务语义与客户边界 |
| 架构师 | explore、specify、review、change | 跨系统边界、NFR、兼容、迁移、失败语义 | 架构约束与风险意见 | 需求范围和验收由业务/产品负责 |
| 需求交付/技术负责人 | intake、review、baseline、change | 复杂度带、跨团队依赖、工程就绪、评审角色和外部交付引用 | 工程可行性、容量约束证据与交接建议 | 不替代业务优先级，不在 Skill 内分配人员/Sprint/工期 |
| QA/测试 | clarify、specify、review、acceptance | 正反例、边界、可观测证据、缺陷回链 | 测试设计与结果 | 条件验收需产品/客户签署 |
| 合规/安全 | frame、clarify、review、change | 适用法规、数据权限、审计和禁止项 | 专业责任范围内结论 | 法源适用性不由 Agent 代签 |
| Coding Agent | baseline 后消费 | 稳定 ID、纵切规格、横切合同、禁止推断、AC | 只在既定合同内实现 | 缺失语义必须回报 GAP，不得猜测 |

这里的“Skill 使用者角色”指参与需求工作的业务、产品、设计、研发和测试人员；PRD 内的 `ROLE-*` 指系统中的业务角色，两者不能混用。每次交接只传：当前主产物、变更/评审侧车、开放 `UNK/ASM`、权威来源、目标阶段和可验证的 SHA-256；不要把整个仓库或全部领域包塞入上下文。

## 5. 阶段门禁语义

所有门禁只使用一套状态：

- `PASS`：被检查的静态合同无已知缺口；仍不证明业务、运行时或客户验收。
- `REVIEW_COMPLETE_WITH_GAPS`：可继续探索/评审，但必须保留发现；不能伪装成已基线。
- `BLOCKED_BY_P0_UNKNOWN`：当前目标阶段被 P0 未知项阻断；可返回、缩范围或由责任人关闭。
- `BLOCKED`：结构、依赖、漂移或必需输入无效。

frame/explore 的未证实假设通常是 GAP，不是 P0 阻断；澄清必须通过 `assumption_refs/assumption_resolutions` 将上游 `ASM-*` 承接、转为 `UNK-*` 或关闭。开放 P0 只有在当前阶段到达其 `blocks_stage` 时才阻断，提前阶段保持可见 GAP。静态门禁是守门员，不是领域专家、浏览器、测试执行器或客户签字。

## 6. 断点与按需加载

5.4 模板的 `resume_context.prior_artifacts` 每项使用相对路径、阶段和 SHA-256。相对路径以声明它的产物文件所在目录为根解析，且解析结果不得越出该目录；`stage_contract.py` 会拒绝目录越界、缺失文件和 hash 漂移。大项目仍使用 `manage_execution_state.py` 保存 ID 切片、读取预算和检查点；产物级 resume 与执行级 checkpoint 互补，不能互相替代。

- frame/explore：通常不加载领域包；只有法规、安全或行业物理约束会改变选项时加载一个精确章节。
- intake 以后：只加载当前阶段参考 + 一个精确领域章节 + 当前 ID 切片。
- 普通单角色任务：不加载本页之外的 maintainer、全模板、全示例或全部领域资产。
