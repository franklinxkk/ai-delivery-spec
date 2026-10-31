---
name: ai-delivery-spec
license: MIT
description: Clarify, create, review or change product, service and office workflow requirements, PRDs and interactive prototypes. Use for vague goals, process improvements, spreadsheet/form rules, small UI edits and changes to existing systems, even without the word requirement. 中文：产品、服务及办公流程的需求判断、深挖澄清、PRD、原型、变更与验收；一句话想法、表单/表格规则和微小改动也适用。明确的纯翻译、排版、抄录或既定步骤执行由对应工具直接处理。
---

# AI Delivery Spec 5.5.6 — 需求判断与交付

让人和 AI 一起把产品做对，为研发与测试提供明确的业务依据。

## 从当前目标进入

继承已确认决定，不因模板重复批准。`/ads` 从任务进入，`/dig` 澄清，`/prd` 写规格，`/proto` 做原型；宿主命令支持见 [README](README.md#shortcuts)。

小改读取相关基线，完成差异及正反验收；无关键未知不提问、不建生命周期文件。

先解决业务分歧。按[团队约定](references/team-customization.md)沿用模板、设计和交互原件；不让用户挑模板或维护机器文件。

| 当前需要 | 按需读取 |
|---|---|
| 判断问题、比较方案、澄清 | [discover.md](references/discover.md) |
| 轻量规格、正式 PRD 与模块交接 | [specify.md](references/specify.md) |
| 存量盘点、生成或修改可操作原型 | [prototype.md](references/prototype.md) |
| 用户需要双态评审 | [review-workspace.md](references/review-workspace.md) |
| 准入、处置、责任与基线 | [lifecycle.md](references/lifecycle.md) |
| 变更、交接反馈或验收 | [change-acceptance.md](references/change-acceptance.md) |
| 多文件、大上下文或跨会话 | [context.md](references/context.md) |
| 机器路由、模板或检查命令 | [stages.md](references/stages.md) |

领域入口不清时用 `python scripts/query_domain.py --list` 看中文摘要与别名；按[领域检索指引](references/stages.md#领域检索)取相关正文并核验权威、版本与适用对象。语言不决定法域，未命中不代表规则不存在；项目决定不写成通用领域规则。

## 保持业务含义与决定权

- 分清事实、授权决定、观察、建议和未知。硬条件核对当前来源；示例只借写法，不移植权限、状态或协议。原型行为不自动成为规则。
- 最新有效决定覆盖同主题旧内容。文档待同步、旧评审待复验不使该决定重新变成待批准。真正超出授权或存在冲突时只处理相应范围。
- 建议暂缓、不做、缩范围写回现有产物；未获处置权不得改变需求状态。记录理由、依据和复议条件；已获授权不重复询问。
- 未定规则保持未定。退路可以限制执行，不能借“保守默认”选定补考、口径、权限或晚到数据政策。未知只阻断依赖它的交付。

## 最小充分规格

按用户任务组织进入、输入、提交、结果及再次读取。先提取已定条件、待决分支和必须保持的结果；排版可自行设计，权限、状态、时间和成功凭据不能从示例或组件默认值补出。

业务条件和正反预期从原始决定产生，写在所属模块；工作推导不新增用户必填表。先完成一个任务的规格、可操作路径及拒绝/恢复验证，再扩展相邻任务；不先铺全产品空页面。复杂交接读[成品示例](examples/configuration-to-consumption.md)。技术空间保留，说明规则不等于新增配置。

重要判断由入口、提交和结果写入共同消费：表单打开后对象关闭、权限撤回或编号已生成，再点原提交按钮，应拒绝且不增加写入；只禁用入口不算验证完成。用来源预期检查产物，不能倒用生成代码作为正确答案。结构通过不证明业务正确。

GAP回读来源核对；未命中不证明通过，不为变绿编造政策、来源或pass。

## 变更与完成

存量原型先盘点受影响页面、角色、入口、动作/处理器、状态、实体、数据源和 Mock 边界；保护未经取消的基线功能与视觉约定。产品态默认可操作；双态评审按用户需要启用。

修改前核对当前文件、进行中对象及消费者；改后复验变化和相邻不变项，不覆盖他人变化或重置旧数据。交接修订稿沿用需求身份，以版本、日期或指纹区分新旧并注明取代关系；不要求另建台账。

交付前从真实入口完成操作、截图阅读与结果核对，入口报错先修复，不绕过入口测内部函数。复杂权限、状态或跨模块交付由获授权的独立接收者读来源验产物，不给作者答案。结论对应本次动作及前后数据；未操作、阻塞、仅界面阻止分别记录。可验证就继续，修发现项后交用户判断；无工具限定证据。改后复验受影响路径，证据充分即停止。

本 Skill 管需求及其产物；工程方案、排期、编码、部署和运营由相应工作流负责，只接收必要反馈与证据。私人材料与凭据不进入公共示例；外部写入遵守用户实际授权。
