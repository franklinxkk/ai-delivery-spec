# AI Delivery Spec 5.5.5

**AI 写代码越来越快，需求里的空白也会越来越快地变成代码。**

PRD 写了几十页，开发仍在问“什么时候能点、失败后怎么办”；原型看起来完整，配置却没有在后续页面生效；换一个 Coding Agent，又把没讨论过的规则补了一遍。如果这些问题熟悉，你需要一份团队和 AI 都能接着工作的需求。

**AI Delivery Spec 帮产品、业务和研发把需求讲清楚、把原型走通、把变更同步回去。** 从一句想法、已有 PRD、原型或客户反馈开始，保留已确认的决定，只追问真正影响实现的问题。小改交付清楚的差异，复杂系统按模块交付连续可读的规格与可操作原型。

*Turn unclear requirements into work your team and coding agents can follow. Keep decisions, interactions, recovery and acceptance together, without forcing every task through a full process.*

[![ClawHub downloads: 3096](https://img.shields.io/badge/ClawHub-3%2C096_downloads-2563eb)](https://clawhub.ai/franklinxkk/skills/ai-delivery-spec)
[![License: MIT](https://img.shields.io/badge/License-MIT-64748b)](LICENSE)

<sub>[ClawHub 公开统计](https://clawhub.ai/api/v1/skills/ai-delivery-spec)：2026-10-26 核实累计下载 3,096 次。下载量不代表验收质量。本仓库版本为 5.5.5，其他渠道版本可能不同，请核对实际安装包。</sub>

**[适合谁](#roles) · [快速上手](#zh) · [快捷入口](#shortcuts) · [安装](#install) · [成品示例](#examples) · [English](#en)**

## 从这些具体问题开始

| 你正在遇到的问题 | 可以得到什么 |
|---|---|
| 一句话需求，不知道该问什么 | 目标、依据和会改变方案的关键未知，不为填模板追问已定事项 |
| 字段、流程和按钮规则散落各处 | 模块内连续的输入、权限、动作、结果、异常与验收，减少翻找 |
| 页面能展示，配置却没有生效 | 从入口到修改、保存、重开和消费的检查，用边界与反例找断点 |
| 需求改后文档、原型、AI 实现各说各话 | 继承有效基线，找到受影响的写入、读取和旧对象并回填规则 |
| AI 说全部通过，却只跑了语法检查 | 分清静态、模拟、浏览器、接口和业务验收，让结论有对应证据 |

例如，“通知提交成功”可能指页面接受请求、接口返回成功，或取得正式业务编号。这里会把允许者、成功凭据、失败保留、结果未知和原请求恢复写在同一模块，再用原型和反例核对。它不代替你决定业务政策，不把演示数据当作上线验证。

<a id="roles"></a>

## 给谁用 交付什么

| 使用者 | 可以拿走的结果 |
|---|---|
| 产品经理、产品负责人 | 关键问题与方案取舍，能连续阅读和评审的模块需求 |
| 业务、售前、实施、设计 | 可确认的业务行为、字段与数据映射、可操作原型 |
| 前端、后端、架构 | 入口、允许条件、状态与数据结果、依赖和恢复边界 |
| 测试、验收方 | 有独立预期的正反例及变更后的验证范围 |
| Coding Agent | 当前有效规则与可定位引用，明确的未知、边界和模块任务 |

已有文档和系统可继续作为权威来源，不必迁移成另一套台账。交付册数、原型和评审态遵从项目目标；编号、检查命令和机器契约按需使用。

**当前 PRD 写法：** 整体说明与通用约定在前；同一对象的字段用录入/展示场景表集中描述；页面动作就地写条件、权限、结果和恢复；截图、主流程与状态图靠近模块。机器规则和接口合同按需补充，不另写重复业务真值。参见[配置到消费示例](examples/configuration-to-consumption.md)与[PRD 骨架](references/templates/unified-requirement-prd-template.md)。

**日常只需选一种交付规模，不用挑遍模板目录。** / Choose one delivery size, not a stack of templates.

| 当前任务 | 交付方式 |
|---|---|
| 规则已清楚的局部修改 | 直接回填原文和原型，说明差异与验收；无需新模板 |
| 有边界的独立小需求 | [轻量需求卡](references/templates/prd-light-template.md)，可直接写在现有文档里 |
| 复杂模块或完整产品 | [正式 PRD](references/templates/unified-requirement-prd-template.md)：字段、元素、流程与场景在模块内集中 |
| 用户明确需要治理或机器联调 | 才选相应记录/合同模板，业务规则仍引用原模块，不重复抄写 |

目录内另外四份 Markdown 是问题、澄清、方案和决策的可选过程材料；十三份 YAML 用于特定工具合同，不是十三份必交文档。小改、需求卡、正式 PRD 共享同一套业务事实，格式升级不重设政策，也不要求重新维护三份。原型按现有界面迭代，产品态与评审态是否并存由任务决定。Markdown 骨架不自带 Word 版式；生成 Word 后仍须实际渲染核对。

Other Markdown files support optional analysis and decisions; YAML templates serve explicit tooling contracts. They are not an extra deliverable set. Expand the existing requirement when needed, preserving approved rules. Word layout still needs actual rendering.

**能力边界：** Skill 提供判断、写作和复核方法，不保证一次生成零缺陷。小样本对照不能证明稳定优于纯模型；真实研发接收和生产验收仍需实际证据。安装、文件、浏览器与工具执行能力由宿主提供。

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

<sub>公开发布包与校验值见 [Releases](https://github.com/franklinxkk/ai-delivery-spec/releases)。仓库候选与社区渠道可能处于不同版本，请核对实际安装版本。 / Find published packages and checksums in [Releases](https://github.com/franklinxkk/ai-delivery-spec/releases). Repository candidates and community channels may differ; check the installed version.</sub>

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
使用 ai-delivery-spec：给现有列表增加“仅看已启用”筛选，
沿用系统已有的启用状态，默认显示全部，保留现有权限。
把这次改动的规则和验收说明白。
```

你会得到这次修改的范围、筛选含义、正常与异常结果，以及可判断对错的验收条件。有已确认资料时直接沿用；存在关键未知时先指出需要谁决定。小改可以用一张需求卡或简短差异说明完成。

**已有材料就一起给它。** PRD、截图、HTML、客户反馈或变更说明都可以作为起点；不同材料的事实与权威需要核实。资料读取、原型生成和验证能力取决于宿主实际提供的工具。

**不必先读完文件夹或学习命令。** 日常只需说清任务并提供已有材料，Agent 按当前任务读取需要的指南。想先看成品就打开下方模块化 PRD 示例；只有要运行确定性检查时才需要脚本环境。中文夹英文术语可直接使用，语言不决定适用地区或业务规则。<br>
You do not need to read every file or learn commands first. Describe the task and provide existing material; the agent loads relevant guidance. Scripts are optional checks, and mixed-language wording does not determine jurisdiction or policy.

### 选一句最像你现在的任务

| 现在要做什么 | 可以直接这样说 |
|---|---|
| **想清楚值不值得做** | “使用 ai-delivery-spec：用户说流程太慢。先判断可能卡在哪里，给我能改变选择的最小验证。” |
| **写清楚需求 / PRD** | “使用 ai-delivery-spec：基于这些已确认材料写 PRD，把角色、规则、异常和验收说明白。” |
| **做可操作原型** | “使用 ai-delivery-spec：基于这份 PRD 做可操作的产品原型，覆盖主路径和关键失败结果。” |
| **改现有需求或系统** | “使用 ai-delivery-spec：审核和发布要拆开，梳理旧对象、相关页面、权限和验收受到的影响。” |
| **评审与交接** | “使用 ai-delivery-spec：站在研发和测试接收者角度审查这份规格，找出仍要靠猜的关键业务选择。” |
| **办公流程与表格规则** | “使用 ai-delivery-spec：报销登记表要自动标出超期项，先帮我明确起算日、例外和责任人，再交给表格工具实现。” |

<a id="shortcuts"></a>

### 四个快捷入口怎么用｜Four intent shortcuts

**它们是对话中的意图简写。** 将下面任一句发给已加载技能的 Agent，附上相关材料或路径。安装技能是否同时注册裸斜杠命令取决于宿主；如果 `/dig` 等被宿主拦截，直接使用表中的带技能名写法。它们不是终端命令，也不对应四套独立流程。<br>
**These are conversation shortcuts.** Send a prompt below to an agent with the skill loaded, together with relevant materials or paths. Native slash registration depends on the host; if a bare shortcut is intercepted, use the explicit skill-name prompt below. These are not shell commands or four separate workflows.

| 入口 / Intent | 复制使用 / Copy and adapt | 当前结果 / Expected result |
|---|---|---|
| **`/ads` · 通用 / General** | `使用 ai-delivery-spec，以 /ads 处理：给现有列表增加按创建日期排序，保留权限。`<br>`Use ai-delivery-spec with /ads: add sorting by creation date to the existing list, preserving permissions.` | 从当前任务进入，完成必要差异与验收。 / Start at the relevant stage; deliver the change and acceptance needed. |
| **`/dig` · 深挖 / Discover** | `使用 ai-delivery-spec，以 /dig 处理：客户说合同审批太慢，帮我找到真正的问题和最小验证。`<br>`Use ai-delivery-spec with /dig: customers say contract approval is slow. Help identify the problem and the smallest useful validation.` | 找关键决定，澄清会改变选择的问题；足够后回到用户目标。 / Clarify decisions that change the choice, then continue toward the requested outcome. |
| **`/prd` · 规格 / Specify** | `使用 ai-delivery-spec，以 /prd 处理：基于附件中的已确认规则编写 PRD，按业务模块写清正常、拒绝与恢复。`<br>`Use ai-delivery-spec with /prd: write a PRD from the attached confirmed rules, organizing success, rejection and recovery by business module.` | 可读业务约定、待决影响及验收；小改可用需求卡。 / Readable business rules, unresolved impacts and acceptance; small changes can use a card. |
| **`/proto` · 原型 / Prototype** | `使用 ai-delivery-spec，以 /proto 处理：基于这份 PRD 做可操作原型，并为研发测试提供当前页面的评审说明。`<br>`Use ai-delivery-spec with /proto: build an interactive prototype from this PRD, with contextual review notes for engineering and QA.` | 可操作产品态；明确需要时提供就近评审说明。 / A working product view, with contextual review notes when requested. |

不知道选哪个就用 `/ads` 或直接说任务。单独写 `/prd`、`/proto` 不会替你确定业务规则；已有决定直接继承，只澄清真正影响交付的缺口。<br>
If unsure, use `/ads` or describe the task. A shortcut does not decide business policy for you; existing decisions carry forward, and only material gaps need clarification.

不必说出“需求”才使用它。办公中的目标、规则、权限或流程改变也可以进入；明确的翻译、排版、抄录等任务由对应工具直接完成。隐式命中取决于宿主与模型，需要稳定调用时显式写出技能名。

<a id="examples"></a>

## 先看实际产物｜See the outputs

| 示例 / Example | 看什么 / What to look for |
|---|---|
| **[最小需求卡 / Minimal requirement card](examples/minimal-v5/requirement-card.md)** · [运行说明 / Run it](examples/minimal-v5/README.md) | 给列表增加筛选：范围、权限、时间含义、异常和验收如何写在一起。 / A list filter with scope, permissions, time semantics, failure behavior and acceptance. |
| **[模块化 PRD / Modular PRD](examples/medium-review-handoff/requirement.md)** | 两个业务模块各自写清入口、权限、状态、失败恢复和正反用例，附产品、前端、后端、测试的阅读入口。 / Two complete business slices with role entry points, guards, recovery and executable acceptance examples. |
| **[交互评审原型 / Interactive review prototype](examples/medium-review-handoff/review-prototype.html)** | 本地打开即可操作工单指派与完成，查看就近实现要点、评审定位和独立记录；绑定上述 PRD。虚构教学数据，仅模拟业务服务。 / Open locally to assign and complete work orders, inspect implementation notes and record reviews separately. Bound to the PRD above; fictional data and a local service simulator. |

需要从可运行起点改写评审原型，可用[示例构建器](references/review-workspace.md)拆分编辑后合成单 HTML，并自动绑定 PRD 摘要。它提供工作样例，不会自动生成你的业务或证明需求已验收。<br>
The [example builder](references/review-workspace.md) splits the working review example into editable files and rebuilds one HTML bound to its PRD. It is a starting point, not automatic business generation or acceptance evidence.

## 常见问题｜Quick FAQ

- **只有一句话，或只改一个字段，也能用吗？** 能。明确小改直接交付差异与验收；模糊想法先找关键决定，不要求全套 PRD、等级或流程。 / **Can I start with an idea or one field?** Yes. Clear edits need a bounded change and acceptance; vague ideas need the relevant decision first.
- **已有 PRD 或 HTML，要重做吗？** 读取相关基线，从当前阶段继续；继承有效决定并保护未取消的功能。 / **Must I rewrite existing work?** No. Continue from the relevant baseline, preserving valid decisions and existing scope.
- **原型和评审态是否必交？** 按目标提供；需要原型时默认可操作产品态，双态评审按需启用。 / **Are prototypes and review mode mandatory?** They follow the task. Requested prototypes are interactive; dual-mode review is optional.
- **检查 PASS 就能上线，领域资料能直接当政策吗？** 都不能。PASS 只覆盖已运行的检查；规则适用性、真实系统和验收各需证据。编码与上线交给相应工作流。 / **Does PASS authorize launch or adopting a domain policy?** No. Applicability, implementation and acceptance need their own evidence; coding and deployment use their respective workflows.
- **检查报错看不懂怎么办？** 把完整提示和被检查的文件交给 Agent，要求解释“哪里、为什么、下一步”，保留原错误码。`INVALID` 表示输入或读取有问题，不算业务负例通过；`GAP` 是待核实疑点，不能为消除提示编造规则。门禁代码可在技能目录运行 `python scripts/ai_delivery_spec_cli.py explain-finding 实际代码 --language zh-CN` 查看原因、修复方向和例子；把“实际代码”替换为输出中的完整代码。未知代码先核对版本，不能套用别的错误。 / **What if a diagnostic is unclear?** Ask the agent to explain location, cause and next action while retaining the code. Invalid input is not a passing negative test; a GAP needs review, not invented policy. The optional `explain-finding` command explains recognized gate codes.
- **评审说某功能没有，应该马上加吗？** 先查实际交付文件、最终生效入口与后加载处理器；文字抽取未呈现图片，不代表原件没有图片。确认仍缺失后再修，旧报告只作线索。 / **Should every reported omission become a feature?** Verify the delivered file and effective handler first. Missing content in a text projection is not proof of absence in the original.



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

### What 5.5 focuses on

1. **Find the decision that matters now.** Start with the outcome, affected people and facts. Compare options and the smallest useful validation. A supported recommendation to investigate, defer, reduce scope or decline can complete the analysis; changing requirement status still requires the relevant authority.
2. **Make the specification tangible and the review concrete.** The PRD explains business rules, the prototype demonstrates interactions and outcomes, and acceptance criteria define how to judge them. “May publish after approval” must distinguish permission from publication in the rule, button behavior and acceptance case. Optional dual-mode review places rules, boundaries and acceptance beside the current product context while you operate it. Resolve critical business choices while leaving legitimate engineering choices open.
3. **Keep meaning consistent through change.** Follow concrete dependencies across writers, readers, entry points, metrics and existing records. Separate candidate impact from verified impact, and keep the PRD, prototype and handoff tied to the same rule.

Clear local edits can be completed directly. Complex work loads only the relevant guidance. You do not need to select a delivery tier or fill every template. Existing materials let you enter at the current stage. Product prototypes are interactive by default; review markers and a dual-mode workspace are optional. [Explore the examples ↑](#examples)

### Quick start

**Start with the work you have.** After [installing the skill](#install), paste this into your agent or replace it with your own task:

```text
Use ai-delivery-spec: add an "Enabled only" filter to the existing list.
Reuse the existing enabled status, show all records by default, and preserve permissions.
Specify the rules and acceptance criteria for this change.
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

Use the [four bilingual shortcut prompts](#shortcuts) for `/ads` (general), `/dig` (discovery), `/prd` (specification) and `/proto` (prototyping). Native slash-command support depends on the host; the explicit skill-name prompts work as conversation requests without requiring separate shortcut registration.

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
<summary><strong>契约样例校验与升级｜Contract examples and upgrading</strong></summary>

### 契约样例校验 / Contract examples

5.5.3 对复杂交接增加模块冷读、合并稿原位修订和配置变值验证；小改仍保持轻量。已有机器契约要用于联调或 AI Coding 时，可选择校验其实际样例，不必为普通 PRD 新建机器清单。<br>
5.5.3 strengthens module handoff, in-place reconciliation of merged specifications, and configuration-to-behavior checks. Small changes remain lightweight. Example checking is optional for existing machine contracts; ordinary PRDs do not need a new manifest.

本地验证：完整release检查通过，399项测试通过；此前5项来源已通过权威替代全文交叉核对。8领域、6阶段的192项合成条目已独立审阅，原始分歧与复核边界见[领域复核记录](maintainer/evals/evidence/v553-domain-review.md)。不代表真实系统、专家或客户验收，也未发布或更新安装。<br>
Local validation: the full release gate and 399 tests pass; five previously inaccessible sources were cross-checked through authoritative full-text alternatives. Independent reviewers examined 192 synthetic items across eight domains and six stage routes; see [scope, disagreements and evidence](maintainer/evals/evidence/v553-domain-review.md). This is not system, expert or customer acceptance, publication or installation.

```bash
python scripts/ai_delivery_spec_cli.py check-examples --input cases.yaml --format json
```

`cases.yaml` 引用同目录及其子目录内已有 JSON 文件，不复制一套权威定义。Schema 根须声明 `https://json-schema.org/draft/2020-12/schema`。支持根Schema或 `#/$defs/Input` 等 JSON Pointer、文件内 `$ref` 与标准格式检查；不获取外部Schema。<br>
Reference existing local JSON schemas and instance files under the manifest directory. Schemas must declare Draft 2020-12. Root schemas, JSON Pointer fragments, internal references and standard format validation are supported; external schemas are not retrieved.

```yaml
contracts:
  - id: input
    schema: model.json#/$defs/Input
    cases:
      - {id: valid, instance: good.json, valid: true}
      - id: missing
        instance: missing.json
        valid: false
        error: {keyword: required, instance_path: ""}
```

每组至少一个正例和一个负例。负例既要被拒绝，也须匹配声明的关键字及实例路径；例如缺必填发生在根对象时路径为 `""`，字段类型错误可能在 `/period`。不支持的format、缺少格式校验依赖、重复键及读取/解析失败均返回INVALID，不算负例通过。<br>
Each contract needs a positive and a negative example. A negative must match both the validation keyword and instance JSON Pointer, not merely fail somehow. Root-level missing-required errors use `""`; a field type error may use `/period`. Unsupported formats, missing format dependencies, duplicate keys and input/resolution failures return INVALID, never an expected rejection.

退出码：`0`=列出样例符合预期；`1`=结果或拒绝原因不符；`2`=输入/Schema/解析错误。输出保留实际校验数、结果和输入文件 SHA-256，不输出样例值。它不证明未列出数据、正文语义、权限实现或运行行为；不自动并入 PRD gate。<br>
Exit codes: `0` for conforming declared examples, `1` for mismatched outcomes/reasons, `2` for invalid inputs, schemas or resolution. Reports include executed results and input hashes, not instance values. This does not prove unlisted cases, prose semantics, authorization implementation or runtime behavior, and is not automatically added to PRD gates.

### 从 5.4.x 升级 / Upgrading from 5.4.x

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
python maintainer/tools/build_runtime_package.py --release --check --output dist/ai-delivery-spec-5.5.5.zip
```

兼容验证入口 `scripts/validators/validate_prd_quality.py`、`scripts/validators/validate_unified_prd.py` 可手动执行，复用当前内核。 / These legacy validators remain available for manual execution.

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

5.5.3 按维护者决定改为 [MIT](LICENSE)，保留原版权署名；历史版本按各自发布时附带的许可证识别，第三方材料的独立声明不由此替换。许可证正文采用 [OSI MIT 标准文本](https://opensource.org/license/mit)。<br>
Version 5.5.3 uses [MIT](LICENSE) at the maintainer's direction, preserving the copyright attribution. Historical artifacts retain their accompanying license notices; third-party notices are not replaced. The license follows the [OSI MIT text](https://opensource.org/license/mit).

[MIT](LICENSE) · [返回顶部 / Back to top](#ai-delivery-spec-553)
