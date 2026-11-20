# 当前目标与工具

按当前目标进入；小改用回复或已有产物，无须 YAML、登记册或 Gate。这里的 Gate 只检查给定产物的声明与结构；BLOCK/GAP 不证明用户未测试，也不授权产品拦截或自动部署。

| 当前任务 | 从哪里取依据 | 到这一步，接收者能做什么 |
|---|---|---|
| 判断机会或比较方案（frame/explore） | 真实任务、现有做法、操作者遇到的代价 | 决定保留现状、尝试改动或补哪一条证据。 |
| 收敛业务选择（先用 triage 分诊；如需 Gate，选 clarify） | 现有约定、冲突和有权人的回答 | 能区分已决定的行为与仍待回答的分支，其他部分可继续。 |
| 盘点存量（inventory） | 用户指定基线、实际路由、已有对象与有效规则 | 能定位本次要改的入口和下游，知道哪些既有行为要保留。 |
| 写规格（specify） | 有效决定、原有模块、实际角色及数据范围 | 开发能还原动作与结果，测试能独立造数。正式权限可在正文查到。 |
| 做原型（prototype） | 用户认可的界面、业务前提、既定演示方式 | 评审人能从正常入口完成约定任务，并在使用结果的位置辨认自己的改动。 |
| 冷读与定基线（review/baseline） | 同版交付物、原始依据、接收人的首次独立理解 | 可复述的规则、需改的原句、操作已证和未证范围分别可定位。业务批准取自有权人。 |
| 交给研发或测试（handoff） | 相同版本的规格、原型及尚未决定的业务问题 | 能实施已定分支、设计验收用例，区分研发可自选的实现和需业务决定的结果。 |
| 变更与验收（change/acceptance） | 当前决定、原对象、不同入口和消费者、原始观察记录 | 明确本版实际兑现的结果、仍失败或未执行的步骤，以及受影响的旧结论。 |

按需要进入任一行。接收者能做表中的事即可结束该阶段。小改可在同一句话交代输入和结果；列出的阶段不产生六套交付物。

## 工具只在有用时运行

`artifact_mode=direct|card|prd` 选择阅读规模，`risk_facets` 触发检查；短规则也可高风险。显式治理独立保留。

分诊可只含title，不发明owner、迭代或价值。`triage` accept只建议整理规格，不证明已澄清，不改变状态或优先级。

```bash
python scripts/ai_delivery_spec_cli.py triage --input intake.yaml --format json
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd requirement.md --stage specify
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html
python scripts/ai_delivery_spec_cli.py impact --truth product-truth.yaml --change change.yaml
```

交给开发按[交接边界](context.md#给研发测试与-coding-agent-的交接)定位原文；确需机器清单才用 handoff/Truth，ready 检查本范围实施阻塞项。`full` 只组合已有输入，不是每次任务终点；已有对应文件时可复制：

```bash
python scripts/ai_delivery_spec_cli.py gate --profile full --requirement requirement.yaml --prd requirement.md --prototype app.html --manifest handoff.yaml --stage specify
```

输入须为 UTF-8 文本；PRD gate 读取 Markdown，不直接读取 DOCX/PDF。正式文档保留原件，按需另存文本投影供检查，图表及排版仍按原件渲染核对。

多个原型共用同版验收编号时，工具无法按入口分配同一份运行记录。联合链路可按原始轨迹人工核实；需要单入口机器统计时，按实际入口分别传对应记录。

文件名替换为实际产物；不为运行此命令新建无关交付物。参数查 `gate --help`，词表与统计字段见[命令边界](troubleshooting.md#命令边界)。

PRD 标题自由，`ADS:scope/behavior/acceptance` 仅辅助定位；无法定位返回待评阅，不判缺失。不强制篇幅、附录、API路径或元数据；使用 frontmatter 时须为 YAML 对象。见[模板](templates/unified-requirement-prd-template.md)及[声明校验](../scripts/requirement_contract.py)。

`gate --profile prd --stage frame|explore` 检查分析结论，省略阶段按baseline。triage不能解析全部排除条件；候选已明确属于另一需求时保留归属、继续当前目标，不照单追问。

审批、表单、权限、指标等复用 [需求模式](patterns/common-requirement-patterns.yaml) 的相关条目；实时协作才读 [实时合同](patterns/realtime-contract.md)。模式提供问题与反例，不替项目决定。旧工具按需查 `--help`；子合同版本独立。

## 契约样例校验

已有机器契约联调才用 `check-examples`，不加入默认 PRD gate。命令、输入样例、退出码及证据边界见[按需说明](troubleshooting.md#契约样例校验)。

## 领域检索

行业问题先查内置切片及来源；长句按已知中英文业务短语检索，未知表达保留原文。零命中可缩词或选领域，不证明无规则。

`common_patterns` 单列身份/会话等共性决策提示，不计入行业来源命中；不自动成为政策，已有答案直接继承。

```bash
python scripts/ai_delivery_spec_cli.py query-domain --search "安全考核" --format yaml
python scripts/ai_delivery_spec_cli.py query-domain --domain medical-hospital-it --section "Policy / Privacy Constraints" --source-detail full --language en-US --format yaml
```

命中后读相关正文及 `references/domains/domain-sources.yaml` 来源，无命中再外查。法规即使命中也核验发布机关原文、替代关系、辖区及适用对象。目录和网页都可能过时，不无说明以旧替新，无法核实保留版本未知。

回答跟随用户语言，法规名称和引用可保留原文。区分法定义务、项目授权规则与设计建议；把义务转成行为验收时，不把上传证明、冻结整个账号等可替代实现升级为法规要求。限制权限要对应受约束的对象和动作，不随意扩大范围。
