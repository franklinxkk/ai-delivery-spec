# Changelog


## 5.4.3 - 2026-07-30

- 更新公开采用信号快照：ClawHub 1,364 次下载（约 1.4k）、SkillHub 696 次下载与 AI 评分 4.8/5.0；同步记录 SkillHub 两条安全测评为“安全，无风险”和 ClawHub 当前审计为 Review，不把采用数据或平台评分表述为质量排名。


- 将真实项目复测后的触发、收敛、存量原型继承和根因诊断修复固化为 SkillHub 发布版本；不新增工作站或第二套交付流程。
- 小功能、明确需求、存量页面小迭代仍必须触发 Skill，但按目标直达最小可用产物，不机械补跑阶段、建文件或重复澄清。
- 模糊需求继续使用“发散 → 推荐聚焦 → 深化”首答闭环；存量 HTML、截图和批准页面继续作为视觉权威，跨页沿用视觉锁。
- 发布包改用 allowlist 生成，排除 `maintainer/`、缓存和内部验证资产，并写入文件哈希与版本清单后执行解压自检。
- 保持诚实验证边界：静态与跨平台回归通过不等同于领域正确、客户验收或跨模型用户评分。

## 5.4.2 - 2026-07-28

- 修复 P0 触发逃逸：Skill frontmatter 与平台入口均声明需求、PRD、原型、竞品和存量系统的新增/修改/评审/反推/验收必须先调用，不得以“功能简单”或“需求明确”跳过；调用后仍按目标选择轻量交付。
- 阶段明确降级为路由地图而非执行清单：明确需求直达目标，不补跑无关前序；实时脑暴与澄清不机械建文件或逐站跑门禁。
- 新增“发散 → 推荐聚焦 → 深化 → 继续”的首答收敛环；删除 L1/L2/L3 固定 3/6/8 批默认，改为明确任务 0 轮、普通模糊任务最多 2 个阻断决策轮、高风险任务最多 4 轮。
- 对话与治理投影分离：直播对话不展示内部 `SRC/ASM/UNK/DEC/YAML`；跨会话、多人协作、审计或工具编译时才结构化持久化。
- 原型视觉治理改为“视觉权威 + 视觉锁”：存量小迭代继承现有 HTML/截图，绿地内部工具允许克制可逆默认，只有品牌化或方向显著影响交付时才询问审美；跨页固定 tokens、typography、shell、components、density 与 taboos。
- L3/L4 handoff 接受 `visual_authority + design_lock_ref` 或既有 `DEC-AESTHETIC-*`，不再强制所有高保真原型先暂停等待美学决策。
- 门禁新增 `--diagnostics roots` 并设为公共默认：每个唯一 finding code 展示一次及重复数，JSON 保留完整明细；`first/summary/full` 继续兼容。
- 同一企业约谈 PRD 的 62 条 finding 被压成 15 个根因组，默认人类可读输出从约 99,687 字符降到 3,696 字符，唯一根因覆盖从 1/15 提升为 15/15；检测结果没有被删除。
- 新增触发召回、首答价值、首个可用结果耗时、澄清决策轮、无关阶段、过度解读、视觉锁一致性、根因覆盖、修复轮次和真实用户满意度指标；没有实际跨模型重复和用户评分时禁止宣称“评价最高”。
- 新增明确小需求、模糊早期想法、存量原型小迭代和真实 PRD 门禁四类体验探针，以及 v5.4.2 体验合同回归测试。
- 维护实验室从 84 个文件、694,739 字节收敛为 55 个文件、约 402 KB；9 个版本专属重复测试进一步合并为 2 个能力级回归套件。默认 `check` 从 45 项收敛为 10 项，完整回归仅在 `check --profile release` 运行。
- 候选新会话探针捕获到一次工作区上下文污染：领域未明确的“运智管家”被带入无关 CRM 客户/合同/回款语义；新增工作区隔离规则后同题复测改为条件分支与单一方向问题。四类 5.4.2 探针记为 `partial`，不冒充跨模型或真实用户反馈通过。

## 5.4.1 - 2026-07-27

- 修复首跑断裂：`gate --profile requirement` 按 `artifact: requirement_intake` 识别单需求准入卡并改用独立 intake schema 校验，不再把扁平 intake.yaml 误判为需求登记册；修复提示指向正确模板。
- UI 动作与业务动作分层：纯界面动作使用 `UIACT-*`，豁免业务验收锚点与 PRD 动作回链；`ACT-*` 业务动作合同不变，handoff 不再把导航/关闭/页签切换当作业务缺口。
- 原型门禁拦截演示脚手架与套壳：可见 UI 出现验收场景/体验身份/E2E 控制台/继承预览等演示元素报 `PROTO-DEMO-SCAFFOLDING-VISIBLE`；iframe 嵌入本地产品页报 `PROTO-NESTED-PRODUCT-IFRAME`。
- CSS 扫描升级：HTML 交互元素类无样式定义报 `unstyled-control-class`，主文本字号低于 11px 报 `unreadable-type-scale`，并识别按钮无主次层级与同页双导航。
- PRD 语义纯净检查：状态机状态列混入 API/字段/动作 ID 报 `PRD-STATE-SEMANTIC-POLLUTION`（"状态机 / API"等工程映射列不误判）；同一主题同时登记为已确认决策和开放未知项报 `PRD-CONFIRMED-OPEN-UNKNOWN-CONFLICT`；稳定 ID 内含 TODO 子串不再误判为未跟踪未知项。
- 跨端绑定词一致性：PRD frontmatter `binding_terms`（法定名词、领域术语）必须同时出现在 PRD 正文与原型可见文本，缺失报 `HANDOFF-BINDING-TERM-MISSING`。
- 美学方向前置：handoff/full 组合门禁要求高保真原型具备 `DEC-AESTHETIC-*` 美学决策记录（视觉方向、参考产品、禁止风格、字号层级、按钮体系、密度），未确认报 `HANDOFF-AESTHETIC-UNDECIDED`。
- 存量资产处置契约：Stage 0 盘点条目支持 `disposition`（adopt_page/inherit_layout/rebuild_interaction/reuse_component/discard），整页采用、局部继承、重构、废弃成为正式处置方式。
- Human-First 模板重构：统一 PRD 模板显式分层——正文面向业务/产品/开发/测试阅读（角色阅读入口、一事一处、密度控制），工程附录面向机器（稳定 ID、字段、API、机器验收）；ADS 锚点保持兼容。
- 出口条件明确：单产物 PASS 不等于交付闭环，宣称最终完成前必须 `gate --profile full`（或 handoff）组合门禁通过；`not_proven` 边界声明不变。
- quality_gate.py 按职责拆分为 PRD/原型/交接三个 mixin 模块，单文件回到行数预算内，`from quality_gate import Gate` 兼容不变。
- 新 finding code 全部配备具体修复原因与示例，`explain-finding` 不再要求读源码猜合同。
- H2 章节结构分析包含完整 H3/H4 子树，角色旅程等嵌套内容不再被截断。
- `examples/minimal-v5/intake.yaml` 补齐 intake 必填字段，入门示例自身通过 `gate --profile requirement`。

## 5.4.0 - 2026-07-25

- 新增九个可进入、可停止、可续接的需求工作站；`frame/explore` 明确为准入前工作区，正式 `REQ-*` 生命周期仍从 intake 开始。
- 路由改为语义目标优先：显式目标与否定约束高于关键词；确定性工具只检查已有产物、显式目标、前置条件与断点漂移，不解析用户自然语言。
- 新增问题简报、方案草图、需求澄清简报三份轻量模板；假设寄存器仅在跨会话、跨角色或治理需要时侧车化，禁止为九阶段机械生成九份文件。
- 增加语言无关 `ADS:*` 稳定锚点，使中文、英文和团队自定义标题可共用轻门禁；frame/explore/clarify 纳入正式 CLI 且复用现有四种全局门禁状态。
- 增加可移植 `resume_context`：前序产物绑定相对路径、阶段和 SHA-256，目录越界、文件缺失和静默漂移均阻断；与大项目 execution-state/ID Slice 互补。
- 新增 assumption register schema、显式阶段路由与早期产物门禁回归，覆盖 P0 未知项、旧 PRD 续接、直接阶段进入和无规格下游阻断。
- README 增加业务、产品、设计、开发和测试按当前阶段进入的复制指令；运行时保持按需加载，不增加每次必跑脚本或多 Agent 税。
- 发布文件预算保持严格少于 200；维护实验室不进入第三方运行包，静态 PASS 继续明确 `not_proven` 边界。
- 修复 `init-custom` 时间戳被 YAML 解析为 datetime 的首次运行断点，并让正式 `intake.yaml` 通过独立 schema 和阶段路由识别。
- P0 未知项改为按 `blocks_stage` 分阶段阻断；澄清阶段增加 `REQ-*`、上游 `ASM-*`、决策取舍和空范围的确定性追溯。
- 早期工作站门禁支持 UTF-8 BOM/CRLF、二进制、损坏结构和超大输入的有界诊断，并按 `document_language` 输出中英文修复提示。
- README 公共命令进入自动审计；Product Truth 示例补齐 compile 步骤并对齐实际 `CHG-CORE-001.yaml` 文件名。
- 评审完成态新增 required_review_types 与逐角色 sign_offs，独立区分 architecture、engineering 与 delivery；缺席、拒绝或无证据签署不得基线。
- 新增需求交付/技术负责人角色镜头与零模型需求池汇总，聚合优先级、复杂度带、依赖和迭代归属，但不接管 Sprint、人员、工期和容量。
- 增加 Jira/Linear/Azure DevOps/TAPD/禅道交接映射、紧急变更补审规则和验收后反馈回流；坚持不把上线、监控和运营扩成第十阶段。
- 为 15 个固定 GitHub 案例生成覆盖九阶段的一句话跨模型探针，记录 provider/model/client/设置/日期/耗时/产物数/门禁结果/输出引用；生成提示包本身不算模型通过证据。
- 新增无人值守跨模型执行合同：只加载目标阶段切片和明确依赖，禁止 README/维护者目录/无关领域包及非必要外部调研，目标门禁得出结论后停止；行为正确性与执行成本分别记账。

## 5.3.3 - 2026-07-22

- 修复公共 CLI 将 `--acceptance-run` 错误转发为下划线参数的问题，并用真实公共入口建立回归。
- ARUN 新增可解析 `evidence_catalog`：本地证据必须存在且不得越过验收目录，稳定 `EVD-*`、可选 SHA-256 和签署证据保持一致。
- 本地多文件 HTML/CSS/JavaScript 原型进入同一静态扫描；缺失、绝对路径、目录逃逸和远程依赖均给出明确结论。
- `not_proven` 根据有效 ARUN 收敛已证明范围，同时保留未覆盖视觉、可访问性、多端与业务权威边界。
- `XCT-*` 横切工作包强制影响模块、全局不变量、执行点、例外/失败处理和 AC，不再只有空壳 schema。
- `SKILL.md`、六份核心阶段规则、排障入口和工具适配完成中文优先改造，稳定 ID 与标准术语保持兼容。
- 合并 v5.3 维护设计稿，保留决策摘要与 Git 历史，降低 GitHub/SkillHub 文件预算压力。
- 分诊收到 Markdown 或损坏的 YAML/JSON 时返回中文可操作阻断，不再泄漏 Python 堆栈；明确 Markdown 需求说明与结构化 intake 的边界。
- Stage 0 检测到 v5.3.0 早期按 roles/views/actions 分栏的台账时给出专用迁移诊断，不再用“items 为空”掩盖版本差异，也不静默晋升旧事实。
- 增加五个真实项目衍生、共 10 个有界小功能的需求卡生命周期回归，覆盖直线关闭与变更重基线两条路径；验收证据强制标注为实验室模拟，避免把机制验证冒充真实开发验收。
- 私域知识接入区分个人本地与团队私有仓库；候选知识新增使用记录与人工晋级评估，项目敏感候选默认不提交，工具永不自动晋级或联网外发。
- 重写中文黄金入门示例并以正式分诊和门禁跑通第一次可验证交付，避免先让新用户理解模式、等级或 Product Truth。
- 校验 15 个固定提交的 45 个本地源码文件，并补跑原矩阵 41 个 `not_run` 单元；矩阵现为 `45 partial / 0 not_run / 0 passed`，明确单会话探索不能冒充 release pass。
- 从跨领域源码场景提炼长耗时任务、版本兼容、多平台差异归并和指标口径四个共性需求模式；只更新适用的现有领域包引用，不新增泛化领域包或自动提升成熟度。

## 5.3.2 - 2026-07-22

- 输出语言默认跟随用户当前请求，统一 PRD/需求卡声明 `document_language`；中英文标题结构均可校验，混杂漂移会被门禁拦截。
- 统一 PRD 改为 30 秒摘要、任务阅读导航、业务旅程、模块纵向切片、跨切面合同和工程索引的渐进结构。
- 每个 `MOD-*` 就近闭环目标、路径、页面/数据、权限、规则/状态、事件、指标、恢复、AC 和未知项，附录不再复制改写业务语义。
- 需求卡采用条件规格；数据上报/统计口径、批量 I/O、审批审计、集成、高风险、迁移和跨角色/模块工作自动升级为统一 PRD。
- 数据上报门禁新增来源映射、校验、提交状态、重试、幂等、审计、口径、时效和对账检查，保持零 LLM、单遍读取。

## 5.3.1 - 2026-07-19

- Replaced flat clarification with a dependency-aware decision tree: inspect
  available evidence first, batch independent facts, traverse aesthetic/route/
  conflict decisions serially, and attach a recommendation, evidence and
  trade-off to every user-owned question.
- Added explicit clarification exit conditions, P0/P1 follow-up bounds and an
  unattended fallback that records owned assumptions, reversal paths and
  `blocks_stage` instead of silently choosing defaults.
- Added an aesthetic intent contract (`feeling + reference + taboo`) and a
  one-screen direction confirmation loop using `DEC-AESTHETIC-*`/`UNK-*`.
- Added L3/L4 region-anchor checks for complex, builder, portal and multi-view
  prototypes, aligning the deterministic gate with the existing `REG-*` page
  contract.
- Reused existing `ARUN-*` acceptance records as the optional browser-evidence
  input. L3/L4 prototypes without executed, evidenced `data-ac` coverage now
  return `REVIEW_COMPLETE_WITH_GAPS` instead of appearing interaction-complete.
- Documented exact-ID expansion, known dynamic-anchor heuristics and `--level
  auto` semantics without adding model calls, subagents or a browser runtime to
  the final gate.
- Consolidated maintainer community copy into the lab README to preserve the
  180-file repository budget and keep the runtime package below 100 files.

## 5.3.0 - 2026-07-18

- Replaced the public mode maze with a silent two-axis route: delivery shape
  (`requirement_card`, `unified_prd`, `governed_truth`) and assurance profile;
  L0—L4 remain compatible gate metadata instead of mandatory user vocabulary.
- Added source-authority bootstrap and `DEC-CONFLICT-*` blocking for competing
  canonical materials; Product Truth remains optional and requires an explicit
  writing-surface and projection decision.
- Added deterministic Stage 0 inventory checks for brownfield PRDs/prototypes,
  including source locations, confirmed/inferred/unknown/defect classification,
  owned P0 unknowns, and protection against silently promoting legacy defects.
- Added composite page contracts (`primary + layout + surfaces`) so metrics,
  lists, forms, preview, workflow and builder rules are required only when
  applicable while preserving page-level implementation detail.
- Added stage- and scope-aware P0 unknown handling with the distinct
  `BLOCKED_BY_P0_UNKNOWN` status/exit code 3; structural blockers retain higher
  precedence and all findings carry Chinese cause/fix plus consumer/source refs.
- Added governed Coding-Agent handoff manifests with baseline hashes,
  engineering-baseline references, `MOD/XCT/EDGE/HANDOFF` packets and embedded
  QA projections; packet drift and unapproved proposals now block handoff.
- Added opt-in, project-local domain candidate and usage-log schemas. Learning is
  disabled/no-network by default and never auto-promotes project material.
- Consolidated overlapping runtime references into lifecycle, specification,
  page/prototype, context/handoff, change/acceptance and troubleshooting routes.
- Added smart large-input rounds, source-expiry warnings, Windows-safe UTF-8 CLI
  output, one canonical gate implementation and v5.3 deterministic regressions.
- Introduced a maintainable full-repository budget and a runtime allowlist
  packaging path for third-party platforms that should not ship the lab.
- Refined README onboarding with concise English value anchors and refreshed
  dated public adoption signals from ClawHub, skills.sh and SkillHub TRACE.
- Closed the static-prototype blind spot for concatenated/runtime `data-action`
  anchors at L2+, and exposed dynamic action candidates without pretending the
  rendered controls were proven.
- Required structured `UNK-*` records for every open P0 item, exact stable IDs
  in all non-code baseline prose, and an owned L3/L4 acceptance plan.
- Added honest `not_proven` gate output, Chinese cause/fix/repair examples and
  regressions that keep official examples on the same user-facing gate kernel.
- Added reverse-inventory `INV-* -> REQ-*` mapping plus owned confirmation
  batches so reverse extraction cannot become a competing requirements baseline.
- Added private-by-default `custom/` domains, inherited PRD overlays and
  declarative validators; executable local validators and silent high-risk rule
  overrides remain prohibited.
- Added friendly dependency diagnostics and automatic discovery of the latest
  conventional execution checkpoint for interrupted large-project work.
- Made runtime archives allowlist-only and bytecode-free even after their
  extracted self-check, with a regression that rejects `__pycache__`/`*.pyc`.
- Replaced the command dump with a five-minute team onboarding path for local
  project domains, company PRD overlays, declarative gates and first workspace.
- Fixed project-facing CLI path resolution so relative `custom/`, `requirements/`
  and artifact paths resolve from the user's project instead of the Skill folder.

## 5.2.0 - 2026-07-16

- Expanded the data-product pack from analytics/semantic governance to the full
  data-value and AI-data supply chain: source/right evidence, public-data and
  property registration, authorized operation, trusted data spaces, digital
  contracts, data products/services, accounting separation, high-quality
  datasets, labeling, train/validation/test/preference data, contamination,
  model feedback and measurable value.
- Added evidence-bounded 2026-2028 planning directions and current primary
  sources from the National Data Administration, Ministry of Finance, Sichuan,
  the EU and OECD without promoting domain maturity or turning policy direction
  into universal product requirements.
- Added section-level domain retrieval so large packs can be loaded by exact
  heading instead of consuming the whole knowledge file.
- Made final-gate findings actionable with deterministic cause, repair direction
  and retry command fields; added the lightweight explain-finding command.
- Exposed the existing tamper-evident checkpoint verification through one resume
  command, preventing interrupted large projects from restarting or silently
  continuing after source/version drift.
- Centralized troubleshooting, recovery, Product Truth interruption guidance,
  FAQ and anti-patterns in one runtime reference to improve first-use recovery
  without expanding the default context.
## 5.1.7 - 2026-07-15

- Added dependency-layered one-sentence clarification with bounded answer batches,
  durable `UNK/DEC/REQ` answer binding, option tradeoffs and a lightweight ToC
  behavior-change route.
- Added competitor-evidence discipline: versioned facts, claim limits, reusable
  patterns, prohibited copying, positioning decisions and measurable differentiation.
- Added brownfield triangulation across written requirements, observed behavior and
  live engineering clarification; historical buildability no longer masquerades as
  current contract conformance.
- Added cross-module edge and successor-reachability contracts plus a reusable
  object-conversion pattern, closing orphan drafts and missing intermediate hops.
- Added the zero-model `handoff` gate for one PRD and multiple prototypes. It checks
  view/action/AC/metric drift, exact machine AC coverage, source/P0 disposition,
  stable `data-metric` anchors and explicit action-dispatch evidence.
- Refined AI triage so reversible, human-gated read/draft assistance is not promoted
  to L3 solely because AI is present, while consequential AI writes remain L3+.
- Unified requirement lifecycle vocabulary with the register schema and clarified
  `STM-*` (state machine) versus `STATE-*` (concrete state).

## 5.1.6 - 2026-07-15

- Added a role-to-work-surface closure matrix so a role task cannot terminate at
  a summary count or unexplained handoff.
- Added `managed_relation_view_ids` and `REL-*` contracts for parent-child or
  many-to-many inventories, including source/inheritance, preflight, batch
  adjust/revoke, partial failure, idempotency, downstream impact, API and AC.
- Added a deterministic L3/L4 gate regression for managed relation contracts.
- Scoped prototype attribute discovery to real HTML-like tags so JavaScript
  selectors no longer create false duplicate-page findings.
- Limited L3/L4 AI-runtime checks to positively applicable AI product behavior;
  an explicit out-of-scope statement or the phrase "AI Coding" no longer creates
  a false requirement for model, prompt, tool-policy and evaluation contracts.
- Reworked the README around user roles, direct outcomes and copyable first-use
  routes, without relying on any named customer-project claim.

## 5.1.5 - 2026-07-15

### Page-level engineering closure

- Added `page-delivery-contract.md`: every implementation view must define local metric caliber, filters, columns, controls, validation, action guards, modal chains, pagination, import/export and UI states.
- Added L3 `page_contract_view_ids` plus deterministic `PAGE-CONTRACT` coverage checks, so one global field/API appendix can no longer hide thin pages.
- Tightened prototype L3 checks: block inline handlers, buttons without stable actions/AC trace, duplicate function overrides and runtime action-ID retrofits.
- Added clean-rebuild guidance for legacy prototypes with stacked overrides or cross-entity modal routing, and a visual-design route combining a design skill with an enterprise component system.
- Added a per-view four-lens walkthrough for frontend, backend, QA and Coding
  Agents. L3/L4 gates now require concrete fields, actions, AC linkage and an
  explicit view-to-API/no-write mapping for every declared page.
- Extended CSS pollution checks beyond `.hidden` and `!important`: grouped
  global state selectors such as `.published,.active` now fail because they can
  silently recolor active pages, navigation and tabs.

## 5.1.4 - 2026-07-14

- Made selective domain lookup emit UTF-8 explicitly, so multilingual source
  titles and known gaps work on Windows hosts with legacy console encodings.
  The runtime-budget regression now forces `cp1252` and decodes UTF-8 on every
  OS, preventing this CLI boundary from escaping local validation again.

## 5.1.3 - 2026-07-14

- Rebuilt the README first-use path around pain, outcome, honest public adoption
  signals, two install routes, three copyable task routes, expected deliverables,
  and concise answers to the four questions new users ask before adoption.
- Completed the Windows encoding fix at the real boundary: JavaScript extracted
  from multilingual prototypes is now sent to Node explicitly as UTF-8 instead
  of inheriting a narrow runner locale. The existing `cp1252` regression covers
  both JSON output and the nested Node syntax-check path.

## 5.1.2 - 2026-07-14

- Made machine-readable quality-gate JSON ASCII-safe so Chinese findings cannot
  crash on Windows runners with a narrow default console encoding. The
  lightweight-gate regression now forces `cp1252` output to reproduce this
  cross-platform boundary on every OS.

## 5.1.1 - 2026-07-14

- Reduced the always-loaded Skill from about 3,590 to about 1,870 `o200k`
  tokens and added selective domain lookup so runtime agents do not load the
  full domain catalog or an entire domain pack by default.
- Added a seven-seniority, eight-role, seven-stage playbook that defines
  decision ownership, escalation, engineering/architecture review, no-guess
  handoffs and acceptance accountability without taking over sprint work.
- Replaced the blanket `experimental` label with evidence-bounded reusable-pack
  maturity: `knowledge_backed`, `contract_tested`, `behavior_validated`,
  `expert_reviewed`, and `audited`; delivery practice remains an independent axis.
- Added zero-model contract regression for all seven built-in domains and 14
  lifecycle/risk scenarios. All built-in packs are now `contract_tested`; none
  falsely claims fresh-agent behavior, expert review, customer acceptance, or
  production correctness.
- Added OA source triangulation for law/standards plus Weaver, Seeyon, Landray,
  DingTalk and Feishu official materials, with explicit boundaries separating
  whitepapers, vendor cases, open platforms and public SDK/demo repositories
  from binding rules or core-product open-source claims.

## 5.1.0 - 2026-07-14

- Narrowed the product from a full delivery-lifecycle kernel to a requirement-
  management kernel with six governed concerns: intake, clarification,
  specification, change, traceability and acceptance. Sprint/task management,
  code, CI/CD, deployment execution and operations are explicit downstream
  boundaries.
- Added a requirement register with evidence-backed value, complexity bands,
  priority, intake decision, iteration/dependency metadata, audit history and
  external milestone references. Exact effort/cost remains engineering-owned.
- Replaced separate Human-First and AI Coding PRDs with one unified PRD by
  default: a sequential human reading path plus field/state/API/traceability/
  machine-acceptance annexes in the same baseline.
- Made independent Product Truth conditional on scale, repeated change,
  multiple governed exports or audit. Bounded projects start from a focused
  requirement workspace; large projects retain progressive fragments.
- Added bidirectional traceability, deterministic change-impact traversal,
  structured change diff/approval/synchronization, acceptance-run evidence and
  reverse defect/test trace contracts.
- Added guided ambiguity scanning, requirement-intake recommendations and a
  focused `init-requirements` CLI route.
- Added unified-PRD readability/engineering validators and CSS `!important` /
  `.hidden` pollution scanning for interactive prototypes.
- Migrated the publishing-learning golden example to `REQ-*` governance and one
  unified PRD; added v5.1 regression coverage for the full requirement loop.
- Added a seven-sector, seven-stage, eight-role offline assurance portfolio for
  PRD/prototype/change regression without making multi-agent review a runtime tax.
- Added a zero-LLM, single-read `gate` for requirement registers, unified PRDs
  and static prototypes; it reports bounded findings and never authors fixes.
- Closed three forward-test escapes: keyword-only PRD shells now fail structural
  checks, change impact reads standard trace-ledger edges, and clarification scan
  exposes actor/state/money/quantity/brownfield gaps beyond lexical ambiguity.
- Added reusable quantity-lineage, money-settlement, accountable-decision,
  statutory-service, partial-execution and cross-aggregate fulfillment patterns;
  removed unsafe realtime exactly-once/offline-queue assumptions and turned
  timing/retry values into project-confirmed variables.

## 5.0.2 - 2026-07-12

- Added Progressive Product Truth: checkpointable core/module fragments, index
  schemas, deterministic compilation, CLI defaults, and lossless regression
  coverage for Trae/WorkBuddy and other interruption-prone large-project flows.
- Added a complete AI Coding PRD route based on a verified delivery failure:
  repository baseline, page/field/state/data contracts, concrete API schemas and
  errors, versioned event/integration contracts, metrics caliber, vertical file
  dependencies, structured AC, migration/rollback, and operations are now L2
  contract surfaces.
- Replaced the keyword-only Coding Agent validator with structural L0-L4 checks
  and a regression that rejects the former thin-summary pattern.
- Separated `practice_status` from reusable domain-pack `maturity`; traffic,
  CRM, education IT, data product, and AI Native now record accountable
  production-practice attestation without claiming unearned validation/audit.
- Rebuilt README around pain-first positioning, copyable 60-second routes, four
  capabilities, ecosystem responsibility mapping, and evidence-bounded claims.
- Reduced the root to six files/eight directories and grouped runtime/domain
  references, validators, domestic adapters, community documents, config, and
  requirements by responsibility.

## 5.0.1 - 2026-07-12

- Added Ultra-Light routing, smart recommendations/manual overrides, and smart
  large-project Context Plan + ID Slice guidance.
- Added 60-second onboarding, Mermaid generation, China-model/tool adapters,
  ten-case triage benchmark, and v5-native L0-L4 validators.
- Removed obsolete comparison artifacts and strengthened repository hygiene.

## 5.0.0 - 2026-07-11

### Architecture

- Rebuilt the skill around one schema-governed Product Truth with Human-First,
  prototype, coding-agent, QA, customer, and operations projections.
- Added an honest Discovery Contract so incomplete requirements can enter the
  lifecycle without fabricated Product Truth.
- Added project-scoped Domain Capsules as the generic fallback when no dedicated
  domain pack matches.
- Added adaptive Context Plans, ID-based retrieval, versioned checkpoints,
  stage gates, change impact, rollback, and evidence-bound completion states.
- Removed release-specific legacy conversion and compatibility adapters. The
  package is a pure v5 runtime; brownfield product/data migration remains a core
  lifecycle capability.
- Replaced customer-specific examples with reusable generic fixtures.
- Broadened discovery and PRD triggering to lightweight ToC work while keeping
  ToB/ToG as the deep-governance specialization.

### Validation

- Added schema/reference closure, projection consistency, domain maturity,
  source freshness, GitHub-case, evaluation, public-claim, runtime duplication,
  package cleanliness, and agent-entry checks.
- Added versioned Discovery/Product Truth checkpoint tests and installed-package
  fingerprint verification.
- Added stage-turn convergence limits, 80% context-pressure actions, atomic
  failed-checkpoint tests, Capsule namespace/slot/placeholder isolation, and a
  structured clarification transcript compiler.
- Added domain-to-evaluation cross-checks, an evidence-backed `status` command,
  public-claim scanning, agent-entry alignment, and tracked-package hygiene.
- Moved installation and natural-language first use above role detail, and
  added a source-linked ecosystem-composition comparison without self-scored
  quality or popularity claims.
- Added baseline/candidate evaluation comparison with strict input, model,
  settings, repository, and repetition comparability.
- Added a dated, machine-readable ecosystem comparison across 12 product and
  engineering skill projects, nine delivery dimensions, platform boundaries,
  non-scoring activity signals, and an explicit user-reported model-label
  attestation boundary.
- Added Chinese lifecycle annotations to the public workflow, runtime entry,
  and stage-gate contract; re-audited public paths and text for customer- or
  project-specific naming before release.

### Known Limitations

- All seven built-in domain packs remain `experimental`; none authorizes a
  production claim.
- GitHub evaluations are pinned exploratory evidence. Most cells remain
  `partial` or `not_run`, and no general performance improvement is proven.
- Behavioral release claims require at least three comparable repetitions and
  executed coding/acceptance evidence; current fixtures do not meet that bar.
- Domain expert review, customer acceptance, legal applicability, safety,
  financial correctness, and production behavior require accountable external
  evidence.
- Hash chaining detects local drift but is not an external signature service or
  immutable audit store.
