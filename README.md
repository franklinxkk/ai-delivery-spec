<a id="top"></a>

# AI Delivery Spec

**这个需求值得做吗？要做成什么样？怎样判断做对了？**

只有一句想法，不知道该问什么；PRD 写了几十页，开发仍在猜；需求改了一轮，文档、原型和 AI 实现又各说各话。

**让人和 AI，一起把产品做对。** AI Delivery Spec 帮助团队先判断什么值得做，再讲清要做成什么样，用实际结果检验原来的判断。面向产品、业务、设计、研发与测试，也为 Coding Agent 提供共同的需求依据。

[![ClawHub: 3,139 downloads](https://img.shields.io/badge/ClawHub-3%2C139_downloads-2563eb)](https://clawhub.ai/franklinxkk/skills/ai-delivery-spec)
[![SkillHub: 4.6/5 for v5.5.5](https://img.shields.io/badge/SkillHub-4.6%2F5_%C2%B7_v5.5.5-15803d)](https://skillhub.cn/skills/user_12c92261/ai-delivery-spec)
[![License: MIT](https://img.shields.io/badge/License-MIT-64748b)](LICENSE)

<sub>ClawHub 累计下载：2026-10-30 核实。SkillHub 对 5.5.5 的历史评测：4.6/5，评级「优秀」。</sub>

**[开始试用 →](#install) · [能帮我做什么](#capabilities) · [看交付示例](#examples) · [English](#en)**

<a id="install"></a>
<a id="zh"></a>

## 一分钟开始

**安装到支持 Agent Skills 的工具：**

```bash
npx skills add franklinxkk/ai-delivery-spec
```

按提示选择你的 Agent。已有 ZIP，也可使用宿主的技能导入功能；[查看其他安装方式](references/tool-adapters.md)。

**然后，把真实问题交给它：**

```text
使用 ai-delivery-spec：客户说审批太慢，想加一个自动审批功能。
结合现有流程，先帮我判断真正的问题和可选方案，再带我把需求做清楚。
```

已有 PRD、原型、团队模板或客户反馈，就一起提供。它会沿用已确认的信息，只追问会改变当前方案的关键问题；明确的小改直接完成。**日常使用不需要学模板、写 YAML 或运行 Python。**

<a id="shortcuts"></a>

## 从你正在做的事开始

| 你遇到的情况 | 直接这样说 | 可以得到什么 |
|---|---|---|
| 想法很多，方向没定 | `/dig 这个需求值得做吗？有哪些更好的解法？` | 问题依据、方案取舍、关键未知和验证建议 |
| 规则基本确认，准备开工 | `/prd 沿用我们的模板，把这个模块讲清楚` | 模块内集中的字段、权限、动作、异常和验收 |
| 文字难以确认交互 | `/proto 按已确认需求做一个可操作原型` | 能操作的页面与关键路径，需要时附就近评审说明 |
| 已有系统要改，又怕漏改 | `/ads 这次变更会影响哪里？同步修订相关产物` | 影响范围、原处修订、需要回归的路径 |
| AI 说完成了，心里没底 | `/ads 从开发和测试视角冷读，并实际验证关键反例` | 具体差异、修复建议、已验证结果与剩余问题 |

这四个简写表达任务意图。宿主不识别裸斜杠命令时，直接说“使用 ai-delivery-spec……”即可。

<a id="capabilities"></a>

## 让目标、需求与实际结果保持一致

![AI Delivery Spec 产品决策循环：判断价值、选择方案、明确需求、验证结果；变更与反馈回到受影响的环节](examples/requirements-workflow.png)

**判断有依据，协作有共识，结果可验证。** 人掌握目标、约束和关键决定；Skill 引导 AI 分析、澄清、表达和核验，让这些决定贯穿需求、原型及后续变更。

### 判断价值：什么问题值得解决？

“加个按钮”“做个自动审批”往往只是候选解法。先理解谁在什么场景遇到了什么问题，核对事实与影响；需要时建议先验证、缩小范围或暂缓。

### 选择方案：怎样做更合适？

结合现有系统和约束比较方案，讲清收益、代价与取舍。已经确认的决定继续沿用，真正影响方案的未知才继续澄清；不会把示例或模型的默认选择当成业务决定。

### 明确需求：要做成什么样？

把决定写成人和 AI 都能据此工作的需求：字段、计算、权限、动作、状态、异常和验收集中在各自模块。沿用团队模板和设计规范，用可操作原型呈现关键行为，按需在页面或弹窗旁查看评审说明。[了解评审方式](references/review-workspace.md)

例如，“提交成功”要有明确凭据；失败保留哪些输入；结果未知如何确认原请求。产品、研发、测试与 Coding Agent 共享这些约定。

### 验证结果：实际做对了吗？

从原始目标和已确认规则建立预期，实际核对关键操作、拒绝与恢复路径；文档、原型彼此一致，还要检查它们是否一起理解错了。收到变更或验证反馈，回到受影响的决定与模块，同步修订、复验。

**从当前任务进入，不必走完整套流程。** 一句话想法、既定需求、存量系统与持续迭代都适用；小改保持轻量，已确认的信息持续复用。

<a id="roles"></a>

人可以按模块顺序阅读；Coding Agent 可按需要取得可定位规则、任务边界与交接材料。Skill 负责需求工作及相关产物，工程编码、部署和生产验收由对应团队与工具承接。

<a id="examples"></a>

## 先看一份交付物

| 示例 | 看点 |
|---|---|
| [一项筛选改动](examples/minimal-v5/requirement-card.md) | 小需求如何简短写清规则和验收 |
| [工单模块 PRD](examples/medium-review-handoff/requirement.md) | 角色、动作、状态与异常如何连续阅读 |
| [可操作评审原型](examples/medium-review-handoff/review-prototype.html) | 下载后操作产品并查看就近说明；使用本地模拟数据 |
| [配置如何产生真实行为](examples/configuration-to-consumption.md) | 从配置保存追到实际执行、结果与反例 |

<a id="customization"></a>

## 用你们自己的模板和设计规范

提供团队现有 PRD 模板、组件规范或参考原型，说一句“本项目沿用这些资料”。Agent 读取原件并应用，不要求团队换模板。原件和项目绑定保存在 Skill 安装目录之外，升级时继续复用。[查看团队定制](references/team-customization.md)

内置交通、CRM、教育、OA、医疗、数据产品、AI 原生、媒体与知识管理资料，支持中文摘要、术语与别名检索；也可接入私有领域资料。[打开领域导览](references/domains/中文导览.md)

<a id="faq"></a>

<details>
<summary><strong>常见问题与进阶入口</strong></summary>

- **一句话需求能用吗？** 能。先判断问题与关键未知，不要求先写 PRD。
- **已有文档需要重写吗？** 保留骨架和有效细节，按本次目标修订。
- **每次都要做原型、跑检查吗？** 按任务选择交付和验证，小改保持轻量。
- **检查 PASS 就能直接上线吗？** PASS 对应具体检查范围，真实系统联调与业务验收仍要实际执行。
- **遇到安装或检查问题？** 看[避坑与排错](references/troubleshooting.md)。
- **需要自动化工具或机器交接？** 看[工具与阶段](references/stages.md)、[上下文与交接](references/context.md)。
- **想了解版本改动？** 看 [CHANGELOG](CHANGELOG.md)。

</details>

<a id="en"></a>

<details>
<summary><strong>English — get started</strong></summary>

**Is this worth building? What should it do? How will we know it is right?**

**Help people and AI build the right product together.** AI Delivery Spec connects product decisions with requirements and verification: assess what is worth solving, compare approaches, define the expected behavior, and check actual results against the original intent. People retain the goals, constraints and key decisions. Start with an idea, existing artifacts or a change request; revisit affected decisions when feedback arrives. Small changes stay small, and approved decisions carry forward.

Install with `npx skills add franklinxkk/ai-delivery-spec`, then try:

```text
Use ai-delivery-spec: customers say approvals are slow and want automatic approval.
Review the current workflow, compare solutions, and help me clarify the requirements.
```

For confirmed work, ask it to update your team's PRD and prototype, preserve unrelated behavior, and verify affected acceptance conditions. Your templates and design resources stay outside the skill and can be reused across upgrades.

Optional intent shortcuts: `/ads` for the current task, `/dig` for discovery, `/prd` for specification, `/proto` for prototypes. If the host does not recognize them, name the skill in plain language. Everyday use requires no YAML or Python.

Browse the [requirement card](examples/minimal-v5/requirement-card.md), [modular PRD](examples/medium-review-handoff/requirement.md), and [interactive prototype](examples/medium-review-handoff/review-prototype.html). Engineering implementation, deployment and production acceptance remain with the relevant workflows.

</details>

<a id="community"></a>

## 一起减少“开工后补需求”

欢迎带着脱敏案例、预期与实际差异来[反馈问题](https://github.com/franklinxkk/ai-delivery-spec/issues)或[参与贡献](https://github.com/franklinxkk/ai-delivery-spec/blob/main/.github/CONTRIBUTING.md)。如果它帮到了你，欢迎 [Star ⭐](https://github.com/franklinxkk/ai-delivery-spec)。

**5.5.6** · [MIT](LICENSE) · [返回顶部](#top)
