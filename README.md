# AI Delivery Spec 5.5.0

**帮你管清需求，让产研和 AI 少猜、少漏、少返工。**<br>
**Manage requirements with less guesswork, fewer omissions and less rework—for your team and AI.**

面向**产研团队与 AI Agent**的需求管理内核，以 Skill 形式使用。从一句话、现有材料或变更进入，帮你定清该做什么、交代清楚业务规则、找出改动影响。按当前任务生成或维护需求卡、PRD、可操作原型与验收条件，让接手者知道依据什么做、哪些还没定。

A requirements management core for **product teams and AI agents**, delivered as a skill. Start with an idea, existing material or a change. Decide what needs doing, make business rules clear and identify change impacts. Create or update only the requirement cards, PRDs, interactive prototypes and acceptance criteria the task needs, so whoever takes over knows what to work from and what remains undecided.

[![ClawHub downloads: 2.4k](https://img.shields.io/badge/ClawHub-2.4k_downloads-2563eb)](https://clawhub.ai/franklinxkk/skills/ai-delivery-spec)
[![SkillHub AI score: 4.7/5](https://img.shields.io/badge/SkillHub_AI-4.7%2F5-f59e0b)](https://skillhub.cn/skills/user_12c92261/ai-delivery-spec)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-64748b)](LICENSE)

<sub>2026-09-08 社区快照：ClawHub 2,431 次下载；SkillHub 4.7/5 为 v5.4.8 历史 AI 评分，非 5.5.0 新评测。 / Community snapshot: 2,431 ClawHub downloads; SkillHub's 4.7/5 is a historical AI rating of v5.4.8, not a new evaluation of 5.5.0.</sub>

**[角色价值 / Role value](#roles) · [中文上手](#zh) · [English guide](#en) · [安装 / Install](#install) · [示例 / Examples](#examples) · [指南 / Guides](#resources) · [中英社区 / Community](#community)**

<a id="roles"></a>

## 各产研角色能得到什么

| 核心用户 | 经常遇到的问题 | 这次能拿走什么 |
|---|---|---|
| **初级产品经理** | 收到一句需求，不知道该问什么、写到多细 | 关键问题、范围与边界、能开始评审的需求卡或 PRD |
| **中高级产品 / 产品负责人** | 需求都合理，但优先做什么、跨模块如何一致还没定 | 问题证据、方案取舍、最小验证、当前决定与变更影响 |
| **业务 / 售前 / 实施 / 设计** | 客户说法、业务规则和页面体验之间有断层 | 可确认的业务行为、可操作的产品原型、待决定事项 |
| **前端研发** | 页面有了，入口、状态、权限和失败反馈仍不明确 | 与规格一致的交互路径、状态结果与验收条件 |
| **后端 / 架构** | 同一句话会推导出不同口径、状态或写入方式 | 数据权威、允许的状态变化、副作用、恢复与集成边界 |
| **QA / 验收方** | “显示正确”无法变成可重复的验收 | 正反例、权限与边界场景、变更回归范围和证据缺口 |
| **Coding Agent** | 换个会话就丢背景，或自行补出业务政策 | 当前有效规则、来源与稳定引用、未知及可接续的任务范围 |

适用于 ToC 产品、ToB/ToG 业务系统及 AI Native 场景。这些角色共用同一份业务约定，各自按需要读取；已有 PRD、需求系统和批准基线可以继续作为权威位置。

## 从决定到交付，重点做好三件事

**1. 更快找到当前要决定什么。** 从目标、受影响的人和事实出发，比较方案与最小验证。有依据的“先验证、暂缓、缩范围或不做”也可以完成分析；改变需求状态仍取决于实际授权。

**2. 让规格可以体验，让评审有具体落点。** PRD 说明业务规则，原型呈现操作与结果，验收条件判断是否符合约定。“审批通过后可发布”要在规则、按钮行为与验收中区分发布资格和发布动作。需要双态评审时，可以边操作产品，边在当前页面旁查看规则、边界与验收依据。只补影响关键业务选择的内容，保留合理的工程实现空间。

**3. 变更之后，相关产物仍然说同一件事。** 沿写入者、读取者、入口、指标和旧对象找具体依赖；区分候选影响与已核实影响，让 PRD、原型和交接引用同一规则。

清晰小改直接完成；复杂需求按问题深入。工作量跟随当前目标，不要求先选 L0–L4、跑完整生命周期或填完全部模板。产品态原型默认可操作；需要面向产研的双态评审时，再开启评审标记与工作区。

<a id="install"></a>

## 安装到你的 Agent｜Install in your agent

适用于能够加载 Agent Skills / `SKILL.md` 的**开发与办公 Agent**。安装、隐式调用、文件访问和浏览器能力由宿主提供，具体支持范围见[宿主适配](references/tool-adapters.md)。<br>
Use it with **development and office agents** that load Agent Skills / `SKILL.md`. Installation, implicit invocation, file access and browser capabilities depend on the host; see [host adapters](references/tool-adapters.md).

[Skills CLI](https://github.com/vercel-labs/skills) 支持的宿主可使用以下命令，按提示选择你的 Agent：<br>
For hosts supported by the Skills CLI, run this command and select your agent:

```bash
npx skills add franklinxkk/ai-delivery-spec
```

安装后直接到 [中文上手](#zh) 或 [English guide](#en) 复制你的第一条任务。**日常使用不需要 Python。**<br>
Then copy your first task from the Chinese or English guide. **Python is optional.**

<sub>5.5.0 当前为本地候选；以上命令安装远端版本。候选 ZIP 不会随本地修订自动更新，试用时核对包的修订说明。 / 5.5.0 is a local candidate; the command installs the remote version. Candidate ZIPs do not update with local revisions; check the package's revision notes before trying it.</sub>

<details>
<summary>ZIP 与宿主导入｜ZIP and host-native import</summary>

已有 ZIP 安装包？解压到宿主识别的 `ai-delivery-spec` 技能目录，让 `SKILL.md` 位于目录根部，再按宿主要求重新加载技能。<br>
Have a ZIP package? Extract it into your host's `ai-delivery-spec` skill directory, with `SKILL.md` at its root, then reload skills as required by the host.

宿主提供技能导入界面时，也可按其说明导入目录或 ZIP。仓库与社区各自更新版本，安装后请核对包内版本。<br>
If your host provides a skill-import interface, follow its instructions to import the directory or ZIP. Repository and community channels update separately; check the installed package's version.

</details>

<a id="zh"></a>

## 第一次用？复制一句话就能开始

安装后，在 Agent 对话中输入这句话；也可以直接换成你的真实需求。

```text
使用 ai-delivery-spec：给现有列表增加“仅看当前有效”筛选，
保留现有权限，把这次改动的规则和验收说明白。
```

你会得到这次修改的范围、筛选含义、正常与异常结果，以及可判断对错的验收条件。有已确认资料时直接沿用；存在关键未知时先指出需要谁决定。小改可以用一张需求卡或简短差异说明完成。

**已有材料就一起给它。** PRD、截图、HTML、客户反馈或变更说明都可以作为起点；不同材料的事实与权威需要核实。资料读取、原型生成和验证能力取决于宿主实际提供的工具。

### 选一句最像你现在的任务

| 现在要做什么 | 可以直接这样说 |
|---|---|
| **想清楚值不值得做** | “使用 ai-delivery-spec：用户说流程太慢。先判断可能卡在哪里，给我能改变选择的最小验证。” |
| **写清楚需求 / PRD** | “使用 ai-delivery-spec：基于这些已确认材料写 PRD，把角色、规则、异常和验收说明白。” |
| **做可操作原型** | “使用 ai-delivery-spec：基于这份 PRD 做可操作的产品原型，覆盖主路径和关键失败结果。” |
| **改现有需求或系统** | “使用 ai-delivery-spec：审核和发布要拆开，梳理旧对象、相关页面、权限和验收受到的影响。” |
| **评审与交接** | “使用 ai-delivery-spec：站在研发和测试接收者角度审查这份规格，找出仍要靠猜的关键业务选择。” |
| **办公流程与表格规则** | “使用 ai-delivery-spec：报销登记表要自动标出超期项，先帮我明确起算日、例外和责任人，再交给表格工具实现。” |

熟悉后可用 `/ads`（通用）、`/dig`（澄清）、`/prd`（规格）、`/proto`（原型）表达意图。它们是否可作为裸命令由宿主决定；自然语言入口始终可以表达相同任务。

不必说出“需求”才使用它。办公中的目标、规则、权限或流程改变也可以进入；明确的翻译、排版、抄录等任务由对应工具直接完成。隐式命中取决于宿主与模型，需要稳定调用时显式写出技能名。

<a id="examples"></a>

## 先看两个实际产物｜See the outputs

| 示例 / Example | 看什么 / What to look for |
|---|---|
| **[最小需求卡 / Minimal requirement card](examples/minimal-v5/requirement-card.md)** · [运行说明 / Run it](examples/minimal-v5/README.md) | 给列表增加筛选：范围、权限、时间含义、异常和验收如何写在一起。 / A list filter with scope, permissions, time semantics, failure behavior and acceptance. |
| **[交互评审原型 / Interactive review prototype](examples/medium-review-handoff/review-prototype.html)** | 下载或从安装包中用浏览器打开，体验产品界面与评审定位。适合需要双态协作的场景；是上手示例，未覆盖完整发布验收。 / Open the HTML locally to explore the product and review views. An onboarding example for dual-mode collaboration, with limited release-validation coverage. |

<details>
<summary><strong>常见问题：小改、存量材料、原型与验收｜Quick FAQ</strong></summary>

- **只有一句话，或只改一个字段，也能用吗？** 能。明确小改直接交付差异与验收；模糊想法先找关键决定，不要求全套 PRD、等级或流程。 / **Can I start with an idea or one field?** Yes. Clear edits need a bounded change and acceptance; vague ideas need the relevant decision first.
- **已有 PRD 或 HTML，要重做吗？** 读取相关基线，从当前阶段继续；继承有效决定并保护未取消的功能。 / **Must I rewrite existing work?** No. Continue from the relevant baseline, preserving valid decisions and existing scope.
- **原型和评审态是否必交？** 按目标提供；需要原型时默认可操作产品态，双态评审按需启用。 / **Are prototypes and review mode mandatory?** They follow the task. Requested prototypes are interactive; dual-mode review is optional.
- **检查 PASS 就能上线，领域资料能直接当政策吗？** 都不能。PASS 只覆盖已运行的检查；规则适用性、真实系统和验收各需证据。编码与上线交给相应工作流。 / **Does PASS authorize launch or adopting a domain policy?** No. Applicability, implementation and acceptance need their own evidence; coding and deployment use their respective workflows.

</details>

<a id="en"></a>

## English guide

### Value for your role

| Role | What you can take into the next conversation |
|---|---|
| **Junior PM** | The questions that matter, bounded scope and a reviewable card or PRD. |
| **Senior PM / product lead** | Problem evidence, options, a minimal validation, current decisions and change impact. |
| **Business / presales / delivery / design** | Business behavior to confirm, an interactive product prototype and explicit open decisions. |
| **Frontend engineer** | Interaction paths, permissions, visible states and success/failure outcomes. |
| **Backend engineer / architect** | Data authority, allowed transitions, side effects, recovery and integration boundaries. |
| **QA / acceptance reviewer** | Positive and negative cases, boundary scenarios, regression scope and missing evidence. |
| **Coding agent** | Current rules, source references, unresolved decisions and a scope it can resume. |

For consumer products, business and government systems, and AI-native workflows. These roles share one business agreement. Existing approved PRDs or requirement systems can remain the authoritative location.

### What 5.5.0 focuses on

1. **Find the decision that matters now.** Start with the outcome, affected people and facts. Compare options and the smallest useful validation. A supported recommendation to investigate, defer, reduce scope or decline can complete the analysis; changing requirement status still requires the relevant authority.
2. **Make the specification tangible and the review concrete.** The PRD explains business rules, the prototype demonstrates interactions and outcomes, and acceptance criteria define how to judge them. “May publish after approval” must distinguish permission from publication in the rule, button behavior and acceptance case. Optional dual-mode review places rules, boundaries and acceptance beside the current product context while you operate it. Resolve critical business choices while leaving legitimate engineering choices open.
3. **Keep meaning consistent through change.** Follow concrete dependencies across writers, readers, entry points, metrics and existing records. Separate candidate impact from verified impact, and keep the PRD, prototype and handoff tied to the same rule.

Clear local edits can be completed directly. Complex work loads only the relevant guidance. You do not need to select a delivery tier or fill every template. Existing materials let you enter at the current stage. Product prototypes are interactive by default; review markers and a dual-mode workspace are optional. [Explore the examples ↑](#examples)

### Quick start

**Start with the work you have.** After [installing the skill](#install), paste this into your agent or replace it with your own task:

```text
Use ai-delivery-spec: add an "Active only" filter to the existing list.
Preserve its permissions, and specify the rules and acceptance criteria for this change.
```

Expect the change scope, filter meaning, success and failure behavior, and testable acceptance criteria. Confirmed material carries forward. Missing business decisions stay explicit. A small change may need only a requirement card or a short change note.

Attach an existing PRD, screenshot, HTML prototype, customer feedback or change request if you have one. The skill checks how each source relates to the decision. File access, prototype creation and validation depend on your host's available tools.

### Choose your starting point

| Your task | A prompt to copy |
|---|---|
| **Decide whether to build** | “Use ai-delivery-spec: users say this workflow is slow. Identify plausible causes and the smallest validation that would change our choice.” |
| **Write requirements / a PRD** | “Use ai-delivery-spec: turn these confirmed materials into a PRD with roles, rules, exceptions and acceptance criteria.” |
| **Create an interactive prototype** | “Use ai-delivery-spec: build a working product prototype from this PRD, including the main path and key failure outcomes.” |
| **Change an existing system** | “Use ai-delivery-spec: separate approval from publishing. Identify affected existing records, screens, permissions and acceptance criteria.” |
| **Review or hand off** | “Use ai-delivery-spec: review this specification as an engineering and QA receiver. Find critical business choices that still require guessing.” |
| **Office workflows and spreadsheet rules** | “Use ai-delivery-spec: flag overdue reimbursements in this tracker. Clarify the start date, exceptions and responsible person before the spreadsheet tool implements it.” |

`/ads`, `/dig`, `/prd` and `/proto` are intent shortcuts for general work, clarification, specification and prototyping. Native slash-command support depends on the host; the natural-language prompts above express the same tasks.

You do not need to say “requirement.” Changes to office goals, rules, permissions or workflows also apply. Straightforward translation, formatting and transcription can go directly to their tools. Implicit selection depends on the host and model; name the skill explicitly when you need a reliable invocation.

<a id="resources"></a>

## 按需深入｜Go deeper when needed

| 当前需要 / Need | 入口 / Guide |
|---|---|
| 判断问题、澄清、比较方案 / Problem framing and options | [澄清与探索 / Discovery](references/discover.md) |
| 写规则、做需求处置、维护基线 / Specification and decisions | [可实施规格 / Specification](references/specify.md) · [需求处置 / Lifecycle](references/lifecycle.md) |
| 存量盘点、交互原型、双态评审 / Prototypes and reviews | [原型 / Prototyping](references/prototype.md) · [评审工作区 / Review workspace](references/review-workspace.md) |
| 变更、验收、跨会话接续 / Changes, acceptance and continuity | [变更与验收 / Change and acceptance](references/change-acceptance.md) · [上下文 / Context](references/context.md) |
| 交通、CRM、OA、数仓、教育、医疗、媒资知识、AI Native / Domain knowledge | [领域覆盖与证据 / Domain coverage](references/domain-coverage.yaml) |
| 命令、宿主适配与排错 / Tools and troubleshooting | [阶段与工具 / Stages](references/stages.md) · [宿主适配 / Adapters](references/tool-adapters.md) · [排错 / Troubleshooting](references/troubleshooting.md) |

领域资料按需读取，其经验与成熟度见覆盖表；项目规则仍须核实来源和适用性。<br>
Domain references load on demand. The coverage file records their evidence and maturity; project rules still need applicable, authoritative sources.

中英文关键词通过小型术语表检索同一份领域原文。回答跟随用户语言，法规名称与来源保留原文；中国法规、其他法域和国际标准分别核实，不能按提问语言选择适用法律。<br>
Chinese and English terms search the same source text through a curated glossary. Responses follow your language while preserving original source titles. Verify Chinese law, other jurisdictions and international standards separately; language does not select the applicable law.

<details>
<summary><strong>可选检查工具与命令｜Optional checks and commands</strong></summary>

在技能目录内运行，使用 Python 3.10+。这些是交付检查工具；日常澄清与小改可直接在对话中完成。<br>
Run from the skill directory with Python 3.10+. Use these tools at relevant delivery checkpoints; everyday clarification and small edits can stay in the conversation.

```bash
python -m pip install -r scripts/requirements.txt
python scripts/ai_delivery_spec_cli.py version
python scripts/ai_delivery_spec_cli.py check
python scripts/ai_delivery_spec_cli.py triage --input examples/minimal-v5/intake.yaml --format json
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd examples/minimal-v5/requirement-card.md --stage specify
```

按任务需要使用以下命令；`analysis.md`、`app.html`、`old-app.html` 换为你的文件：<br>
Use these as needed; replace `analysis.md`, `app.html` and `old-app.html` with your files:

```bash
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd analysis.md --stage explore
python scripts/ai_delivery_spec_cli.py query-domain --search confidence --limit 8
python scripts/ai_delivery_spec_cli.py query-domain --search 完成率 --limit 8
python scripts/ai_delivery_spec_cli.py query-domain --domain ai-native --section "Metric / Indicator Governance"
python scripts/ai_delivery_spec_cli.py query-domain --domain medical-hospital-it --section "Policy / Privacy Constraints" --source-detail full --language en-US
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html --prototype-baseline old-app.html
```

- **阶段 / Stage**：分析建议用 `explore` 检查；不传 `--stage` 仍默认 `baseline`。建议暂缓不会自动降低检查阶段或改变需求状态。 / Use `explore` for analysis. Omitting `--stage` retains the `baseline` default; a deferral recommendation does not change the stage or lifecycle.
- **风险 / Risk**：`triage` 读取声明和部分正文线索，只给建议；未声明 `ai_write_scope` 表示未知，正文自动写回风险仍会独立提示。 / Triage returns advice using declarations and bounded text cues. Missing `ai_write_scope` means unknown; write-back cues are checked separately.
- **变更 / Impact**：`impact` 接受顶层 `seed_refs: [REQ-A]` 或 `request.seed_refs`，同时给出时必须一致。图上的相关对象先作为候选核实。 / Impact accepts either seed location; both must agree if supplied. Related graph objects remain candidates until their dependencies are verified.
- **领域 / Domains**：也可用 `--section 指标`。搜索命中是候选线索，不能直接变成项目已批准规则。 / Chinese section aliases are supported. Search hits are leads, not approved project rules.

搜索结果给出扩展词、原文位置及 literal/alias 命中方式；它是有界关键词检索，未命中也可能只是术语表未覆盖。`--source-detail full` 可查看来源 URL、法域及适用范围，原文章节不会由脚本自动翻译。<br>
Results show expanded terms, source locations and literal/alias matches. This is bounded keyword retrieval; zero hits may mean a vocabulary gap. `--source-detail full` exposes source URLs, jurisdictions and applicability. The script preserves source passages without automatically translating them.

常用中文词可检索已有台账、报销和里程知识；“活跃”按客户/企业/用户相关短语召回，不等同于所有 `active` 状态。账本也保留 JS 动态声明候选及来源；候选进入盘点不代表已经渲染，门禁保留相应 GAP。UNK 表头未被识别时提示定位问题；显式无效状态、无依据关闭与真实冲突仍分别检查。<br>
Chinese ledger, reimbursement and mileage queries retrieve existing domain passages. Activity terms target relevant customer, enterprise or user phrases. Interaction ledgers retain JS declaration candidates with their origins; unresolved rendering remains a GAP. Unlocated unknown-status columns are distinguished from explicitly invalid statuses, unsupported closure and conflicting declarations.

</details>

<details>
<summary><strong>从 5.4.x 升级｜Upgrading from 5.4.x</strong></summary>

5.4.x 产物可继续读取，稳定 ID 和已批准事实保留。`artifact_mode` 使用 `direct/card/prd`；旧 L0–L4 在 PRD 中只作呈现提示，不能覆盖显式模式或自动提高风险、证据要求。专业原型、评审、Truth、handoff 与执行状态工具保留其版本化 Schema，不自动迁移旧产物，也不成为日常任务的默认依赖。

5.4.x artifacts remain readable with stable IDs and approved facts preserved. `artifact_mode` uses `direct/card/prd`; legacy tiers are presentation hints in PRDs. Specialized prototype, review, Truth, handoff and execution-state tools retain their versioned schemas and remain optional. Old artifacts are not automatically migrated.

旧未知项状态 `partial`、`in_progress` 及“部分关闭/部分解决”按 `open` 理解：只要仍有未决部分，就按其依赖范围与阻断阶段处理。同一未知项的相同诊断合并，冲突声明仍保留。其他未识别状态必须明确迁移，不能被当作关闭。<br>
Legacy `partial`, `in_progress` and equivalent Chinese partial-resolution labels are treated as `open`. Remaining decisions retain their scope and blocking stage. Repeated identical findings are merged; conflicting declarations remain visible. Other unknown status values require explicit migration and never count as closed.

接入脚本需注意：5.5 triage 使用 `recommendation / artifact_mode / risk_facets / governed`，移除旧 tier/mode 推导结果键；旧 Markdown PRD 入口复用新内核，退出码可能改变；旧 `validate_prd_quality.py --domain-rules` 已退役，领域约束通过显式 custom gate 或领域工具处理。

Script consumers: update to the triage keys above. Old derived tier/mode output keys are removed; legacy Markdown PRD entry points share the new engine, so exit codes may differ. The old `--domain-rules` keyword check is retired; use explicit custom gates or domain tools. See the [changelog](CHANGELOG.md) for version history.

</details>

<details>
<summary><strong>检查能证明什么；如何维护｜Evidence and maintenance</strong></summary>

正文检查对状态权威、指标口径、恢复路径、空值/陈旧、权限边界与变更传播做有界抽查，返回带位置的待核实 GAP。填写评阅 pass 不能覆盖正文疑点。`PASS` 只表示实际执行的确定性检查未发现对应阻断或缺口；业务语义、来源授权、浏览器交互、真实实现和客户验收仍需各自的证据。

Text checks sample known ambiguity patterns in state authority, metrics, recovery, null/stale values, permissions and change propagation. Findings are located GAPs for review; a declared review pass cannot suppress them. A deterministic `PASS` covers only the checks executed. Business meaning, source authority, browser behavior, implementation and customer acceptance require their own evidence.

对“补考成绩取最新”等取值政策，依据未显式出现时只给 WARN 提示；附近同时存在未决声明才给 GAP。提示不能鉴定授权真伪，也不要求为每个界面默认值补决策表。<br>
For selected policies such as using the latest retake score, an absent explicit basis produces a WARN advisory; a nearby unresolved decision produces a GAP. This does not authenticate authority or require decision tables for ordinary UI defaults.

本 Skill 管需求与其产物，连接工程反馈；排期、编码、部署与运营由相应工作流负责。公共反馈与示例请使用脱敏材料。<br>
The skill manages requirements and their artifacts, incorporating engineering feedback. Scheduling, coding, deployment and operations belong to the relevant workflows. Use sanitized material in public examples and feedback.

维护者可在**完整源码仓库**运行以下命令；构建发布包要求干净 Git 来源。运行包不包含 `maintainer/`，其中 `check` 只检查实际携带的文件与契约。<br>
Maintainers can run these commands in the **full source repository**. Release packaging requires a clean Git source. Runtime packages exclude `maintainer/`; their `check` covers the files and contracts actually shipped.

```bash
python -m pip install "pytest>=8,<9"
python scripts/ai_delivery_spec_cli.py check --profile release
python maintainer/tools/build_runtime_package.py --release --check --output dist/ai-delivery-spec-5.5.0.zip
```

</details>

<a id="community"></a>

## 一起把需求做得更清楚｜Join the community

欢迎**中文或英文**提问、反馈真实使用问题、分享脱敏案例、完善翻译或贡献领域知识。复现材料、预期与实际差异，会帮助我们判断该修模型指引、工具还是示例。

**Chinese and English** questions, bug reports, sanitized examples, translations and domain contributions are welcome. Reproduction steps and expected-versus-observed behavior help identify what needs to change.

- **[GitHub Issues：反馈与交流 / Feedback and questions](https://github.com/franklinxkk/ai-delivery-spec/issues)**
- **[ClawHub：社区安装入口 / Community listing](https://clawhub.ai/franklinxkk/skills/ai-delivery-spec)** · **[SkillHub：中文社区入口 / Chinese community listing](https://skillhub.cn/skills/user_12c92261/ai-delivery-spec)**
- **[参与贡献 / Contributing](https://github.com/franklinxkk/ai-delivery-spec/blob/main/.github/CONTRIBUTING.md)** · **[版本记录 / Changelog](CHANGELOG.md)**

如果它帮助你澄清了一条需求、发现一次关键分歧，欢迎给项目一个 **[Star ⭐](https://github.com/franklinxkk/ai-delivery-spec)**，让更多产研同伴找到它。<br>
If it helped clarify a requirement or expose a critical ambiguity, a **[Star ⭐](https://github.com/franklinxkk/ai-delivery-spec)** helps more product teams discover it.

[Apache 2.0](LICENSE) · [返回顶部 / Back to top](#ai-delivery-spec-550)
