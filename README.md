# AI Delivery Spec 5.4.8 — Requirement Management for Human & AI｜人机共用需求管理

> 一句话需求，AI 就直接画页面；真正开工时，指标口径、状态守卫、权限、异常和验收全靠人补？
>
> PRD、原型、开发实现和测试用例各说各话；需求一变，又要靠会议人工同步？

**Any Stage In. Right-Sized Artifact Out. One Traceable Requirement Baseline.**

AI Delivery Spec 是面向大模型时代、适用于 ToC 与 ToB/ToG 的需求管理 Skill。它可以从一个 Idea、客户问题、会议纪要、竞品、旧 PRD、原型、存量系统、变更或缺陷开始，把“业务为什么做”收敛为业务能确认、产品能决策、研发可实施、测试可独立验收、Coding Agent 可按契约执行的同一份需求事实。

它不是 PRD 改写器，也不强迫小需求走完大流程：**小改直接交最小闭环，复杂需求才升级治理。**

[![Version](https://img.shields.io/badge/version-5.4.8-7C3AED.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)
[![Forks](https://img.shields.io/github/forks/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec/forks)

[ClawHub 下载与安全审计](https://clawhub.ai/franklinxkk/skills/ai-delivery-spec) · [SkillHub 最新评分与安全报告](https://skillhub.cn/skills/user_12c92261/ai-delivery-spec) · 如果它帮你少开一次“补规则”的会，欢迎到 [GitHub 点个 Star ⭐](https://github.com/franklinxkk/ai-delivery-spec)。

## 60 秒上手

```bash
# Codex / Claude Code / Cursor / Trae 等 Agent Skills 兼容工具
npx skills add franklinxkk/ai-delivery-spec

# OpenClaw
openclaw skills install @franklinxkk/ai-delivery-spec
```

安装后直接说真实目标，不需要先学阶段名或模板：

```text
使用 $ai-delivery-spec。我是<角色>，现在有<想法、材料或系统>，
本次只要<目标产物或停止点>。复用已确认事实；不确定的不要猜；
只问会改变范围或结果的问题，交付最小但完整的结果。
```

也可以用四个轻量入口；它们是**意图别名，不是四套新流程**：

| 入口 | 适合什么时候 | 行为 |
|---|---|---|
| `/ads` | 不知道该走哪一步 | 识别当前阶段与风险，路由到最小下一产物 |
| `/dig` | 想把需求“深挖到底” | 每次只问一个真正改变决策的问题，从战略、系统、行为动机、反方挑战四个镜头收敛；仍写回 DEC/UNK/ASM 与既有需求产物 |
| `/prd` | 目标是可评审、可实施 PRD | 先关闭阻断开工的 P0 未知项，再直接形成一份统一 PRD |
| `/proto` | 目标是可操作原型 | 默认交产品态；若要给研发测试走读，先确认是否同时生成评审态 |

这些入口是否能作为裸斜杠命令使用，取决于宿主：有的工具会在消息到达模型前拦截未知命令。此时请用该宿主的显式 Skill 调用形式，例如 `/ai-delivery-spec /dig …`、`$ai-delivery-spec /dig …`，或直接说“用 ADS 深度澄清 / 直接出 PRD / 直接出原型”。四个入口保证语义等价，不宣称跨宿主原生注册。

如果你只说一句“帮我做一个企业约谈 HTML”，Skill 会记住 HTML 是最终目标，先分批确认会改变范围、规则、权限、状态、指标或数据的关键决定；P0 关闭后继续生成可实施原型，**不会停在一张需求清单**。若只是想先看方向，请明确说“先做概念原型，允许合理假设”；假设和 GAP 会被显式标出，不冒充开发基线。

你不需要说 `Ultra-Light`、`L2` 或 `smart-large-project`：

- “表头联系人改成企业联系人，其他逻辑不变。”——直接按快速小改处理。
- “新增审批状态，影响三个角色、通知和统计。”——只升级状态、权限、数据、异常和回归合同。
- “跨系统双向同步，要正式验收。”——才启用权威源、数据流、追溯与验收证据。

一个 Idea 也能开始。先看[最小需求样例](examples/minimal-v5/README.md)；需要理解指标、泳道流转和二级抽屉如何进入评审态时，直接打开[中等需求交互样例](examples/medium-review-handoff/review-prototype.html)。该匿名样例用于首次理解与冷读训练，不冒充可复制的完整 Schema/发布夹具。

**English works end to end.** Say: “Use `/ads` and follow my language. Ask only scope-changing questions, deliver the smallest complete artifact, and mark what remains unproven.” Stable IDs and machine keys remain unchanged.

## 它解决谁的什么问题

| 角色 | 最常见损耗 | 得到什么 |
|---|---|---|
| 初级产品经理 | 不知道该问什么，把页面描述当需求 | 有边界的问题引导、最小需求卡、规则与异常底线 |
| 中高级产品 / 产品负责人 | 跨模块、状态、数据和团队输出难统一 | 一份可追溯基线、分级交付、内审与变更影响 |
| 业务 / 售前 / 实施 / 设计 | 客户语言到界面方案失真 | 事实、假设、未知和可确认的产品态原型 |
| 前端开发 | 入口、交互、权限和失败反馈靠猜 | 页面、动作、状态结果、二级上下文与可观察验收 |
| 后端 / 架构师 | 指标口径、权威源、守卫和幂等晚补 | 对象、规则、数据流、状态、事件和 NFR 边界 |
| 测试工程师 | 只有正向描述，无法独立复现 | 正反、边界、异常、权限、证据和回归范围 |
| Coding Agent | 文档可读但不可执行，缺口被自动脑补 | 稳定 ID、机器切片、GAP 纪律和结构化 handoff |

## 一条主线，不是一条僵硬流水线

`frame → explore → intake → clarify → specify → review → baseline → change / acceptance`

从哪里来就从哪里进入，只做到当前目标：

- 从零开始：定义问题、用户、证据、成功信号和最小验证。
- 已有材料或系统：先做 Stage 0 盘点，再识别遗漏、冲突和不可实施处。
- 要开发：形成一份统一 PRD，按需配工程原型与机器附录。
- 有变更：比较基线，穿透角色、页面、规则、数据、消费者和回归范围。
- 要验收：把 AC 变成执行记录，区分静态检查、真实实现、领域确认和客户签署。

普通项目默认**一份统一** PRD：正文供业务、产品和传统开发顺序阅读，同文档工程附录供前后端、测试和 Agent 精确执行。只有持续变更、多投影或强审计场景才启用**分片真相**（Product Truth）。

## 产品态、评审态、机器合同各司其职

- **产品态**：客户演示和需求确认默认产物，保持完整、可操作，不被注释破坏。
- **评审态**：只有用户明确要求或确认后生成。左侧保留完整产品；右侧解释当前页面或业务浮层。
- **机器合同**：稳定 ID、规则、状态、数据流、错误、副作用和验收证据；不把右侧说明当 Coding Agent 的唯一输入。

5.4.8 的评审态以“所有影响实施与验收的语义项”为覆盖分母：

- 当前菜单、面包屑、页面和业务弹窗都要有可定位上下文。
- 页面上的关键功能要在真实目标旁标号；点击左侧标号或右侧卡片，目标、标号和说明同时框选。
- 简单功能可用一句话说明；装饰元素不强行标注。
- 指标卡必须写清口径、时间窗、范围、来源、刷新、缺失/延迟和验收。
- 泳道或状态页必须写清迁移条件、角色守卫、副作用、失败与恢复。
- 点击卡片后的拆解、编辑、确认等二级弹窗/抽屉，是独立评审上下文，不能只标入口按钮。
- 评审栏可以收起再展开；窄屏可在产品态和评审态间切换，不覆盖关键操作。

跨页面/模块/角色主链才画流程图；受守卫的状态变化画状态图；跨系统或多权威源画数据流。简单 CRUD 不机械堆图。

## 与 Spec Kit / OpenSpec 的边界

[Spec Kit](https://github.com/github/spec-kit) 和 [OpenSpec](https://github.com/Fission-AI/OpenSpec) 更贴近代码仓库里的规格、技术计划、任务与实现协作。AI Delivery Spec 的主场是更上游、更跨角色的 **requirement-to-acceptance**：先把业务价值、范围、责任、规则、评审基线和验收定准，再交给下游 Coding Agent。

最佳组合通常是：`AI Delivery Spec 定准需求基线 → Spec Kit / OpenSpec / Coding Agent 规划与编码 → 实现和测试证据回流验收`。

## 门禁：发现缺口，不制造绿灯

只用 Agent 完成需求工作无需 Python。运行零模型本地门禁需要 Python 3.10+，以及 PyYAML、jsonschema **两个本地依赖**：

```bash
python -m pip install -r scripts/requirements.txt
python scripts/ai_delivery_spec_cli.py route-stage --target clarify --artifact problem-brief.md --format json
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd requirements/PRD.md --level L2 --language auto
```

持久化产物使用 `ADS:*` 语义锚点和 `resume_context` 续跑。门禁区分 `BLOCK / P0_UNKNOWN / GAP / PASS` 并记录 `not_proven`；静态 PASS 不证明真实实现、法规适用性或客户验收。

复杂项目才启用 Product Truth，执行顺序不能颠倒：

```bash
python scripts/ai_delivery_spec_cli.py init-requirements --output requirements --with-product-truth
python scripts/ai_delivery_spec_cli.py compile-truth --index requirements/truth/index.yaml
python scripts/ai_delivery_spec_cli.py trace --truth requirements/truth/compiled/product-truth.yaml --output requirements/traceability.yaml --baseline-version 1.0
python scripts/ai_delivery_spec_cli.py impact --truth requirements/truth/compiled/product-truth.yaml --change requirements/changes/CHG-CORE-001.yaml
```

团队自己的术语和规则放在私有 `custom/`。内置领域包为 `traffic`、`crm`、`education-it`、`data-product`、`ai-native`、`oa`、`medical-hospital-it`，当前成熟度均为 `contract_tested`；实践状态分别使用 `production_practiced` 或 `knowledge_only`。这些标签不等于当前项目已获专家确认或生产可用。

## 边界与验证

AI Delivery Spec 不接管排期、Sprint、技术架构决策、代码生成、CI/CD、部署和运营。它不能替产品负责人、架构师、领域专家、测试或客户签署。

```bash
python scripts/ai_delivery_spec_cli.py check
python scripts/ai_delivery_spec_cli.py check --profile release --keep-going
```

`SKILL.md` 是触发与路由；`references/` 是按需合同；`schemas/` 与 `scripts/` 是确定性门禁；`maintainer/` 只服务发版验证，不进入普通项目上下文。完整证据边界见[维护者说明](maintainer/README.md)，变化见 [CHANGELOG](CHANGELOG.md)。

## 支持项目

有 Bug 或建议请[提交 Issue](https://github.com/franklinxkk/ai-delivery-spec/issues)。如果项目帮你减少了误解与返工，欢迎 [Star ⭐](https://github.com/franklinxkk/ai-delivery-spec)；贡献说明见 [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)。
