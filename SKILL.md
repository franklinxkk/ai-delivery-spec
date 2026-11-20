---
name: ai-delivery-spec
license: MIT
description: Clarify, create, review or change product, service and office workflow requirements, PRDs and interactive prototypes. Use for vague goals, process improvements, spreadsheet/form rules, small UI edits and changes to existing systems, even without the word requirement. 中文：产品、服务及办公流程的需求判断、深挖澄清、PRD、原型、变更与验收；一句话想法、表单/表格规则和微小改动也适用。明确的纯翻译、排版、抄录或既定步骤执行由对应工具直接处理。
---

# AI Delivery Spec 5.5.7 — 需求判断与交付

帮助团队做值得做的产品，让人和 AI 少猜、少返工。按当前目标选择方法与工具；本 Skill 保留业务事实、决定权和交付依据，不规定思考步骤、固定角色队列或整套产物。

## 保留这些约束

- **范围与决定权**：继承当前授权、项目约定及仍有效的决定。建议、示例、原型默认值和领域经验不自动成为业务政策；最新决定覆盖同主题旧说法，待同步不等于待批准。未决事项只限制依赖它的判断和交付；产品是否禁止某个操作，另按已授权规则判断。
- **来源与版本**：区分事实、观察、推断、建议和未知；冲突回到对象、适用范围与来源，不凭新旧、模型一致或文字流畅裁决。当前法规、标准及易变信息核实版本和适用性；原文访问失败可用权威佐证，说明实际核实范围。
- **业务行为与复杂度**：说清谁在什么条件下操作哪个对象、成功改变什么、失败保留什么以及如何继续。先判断去掉新增机制会破坏哪项已知业务结果，再比较现有能力或系统自动处理能否承担。把决定交给确实需要作判断的人。增加设置前，说明谁会在什么场景改变它，以及使用结果有何差异。已有样式、默认值和系统可推导的信息直接沿用。首版只写接收者为本次结果必须知道的事。未经授权的建议即使容易实现，也不混入交付条件。
- **存量保真**：定位实际入口、对象、消费者和旧数据，保护未取消的路径、合法操作、字段含义及视觉约定。同一规则在受影响原处同步；新默认不自动改写旧对象，演示数据重置和文案修改不能掩盖执行问题。
- **覆盖与完成**：长任务、跨模块多轮变更或明确逐一核验时，沿用计划或检查点记录来源、范围、完成条件、版本和证据；反查原始要求，不能只核对生成的计划。小改只处理受影响项，不新建过程文件。验证操作时，从约定入口按实际分工走到结果使用处。结论引用同一对象的操作与可复查结果；为绕过阻断而切身份、改道或代造状态，另记诊断结果。未到终点按实际进度报告。详见[覆盖记录](references/context.md#覆盖与执行)。

## 按具体缺口取参考

按下一位使用者需要的结果选入口。跨阶段沿用有效决定与对象，带上实际证据及缺口；清晰小改直接回填。下表可按问题跳读。

| 当前需要 | 可选资源 |
|---|---|
| 判断机会、比较方案、澄清关键未知 | [discover](references/discover.md) |
| 写业务规则、正式角色权限、办公流程或验收规格 | [specify](references/specify.md) |
| 选演示权限、修改页面或检查配置能否实际使用 | [prototype](references/prototype.md)；[机制取舍与消费示例](examples/configuration-to-consumption.md) |
| 找受影响入口、复核测试记录或判断能否宣称闭环 | [change-acceptance](references/change-acceptance.md) |
| 恢复大材料、交接或接着按规格开发 | [context](references/context.md) |
| 团队资料、评审工作台或显式生命周期 | [team-customization](references/team-customization.md)、[review-workspace](references/review-workspace.md)、[lifecycle](references/lifecycle.md) |
| 长任务反复漏项、适配接收工具或比较模型 | [tool-adapters](references/tool-adapters.md) |
| 核对阶段输入输出、领域知识或已有契约 | [stages](references/stages.md)；`python scripts/query_domain.py --list`，不需通读目录 |

## 按接收者下一步交付

沿用指定形式、项目模板和设计原件，只交当前必要内容，小改回填原处。未指定形式时选择能支持下一步的最小产物，不默认同时制作 PRD、原型、台账或工程工作包。有角色差异的规格在正文交代谁能对哪些对象做什么。演示权限沿用项目选择；浏览器实操、模拟依赖、生产授权各按所见交付。

跨文件冲突、复杂角色链或明显接收歧义可用独立冷读；要求逐模块审查时覆盖全部约定模块，代表任务不能代替。其余按风险取样，不强制小改全角色、全页面复核。局部结论不扩大到全项目；缺少某项检查证据不等于用户未做测试，也不自动新增产品发布门槛。

`/ads`、`/dig`、`/prd`、`/proto`见[README](README.md#shortcuts)。用户接着要求开发时，以原规格为准，转工程流程实现已定部分。发布、文档渲染及运营沿用相应流程，各按实证交付。
