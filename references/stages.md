# 当前目标与工具

按当前目标进入；小改用回复或已有产物，无须 YAML、登记册或 Gate。

| 目标 | 当前交付与停止 |
|---|---|
| frame/explore | 现状证据、关键解释/假设、选择及能改变决定的最小验证；有理由的暂缓/不做也可以是结果 |
| intake/clarify | 有效决定、依赖当前决定的未知及处置；授权清楚就继续用户目标 |
| specify | 最小充分业务约定、继承边界、正反验收及未证明范围 |
| prototype | 在明确范围内可操作的产品表现；概念候选标明假设，不能冒充基线 |
| review/baseline | 指定范围获得必要来源、语义复核和授权，保留未覆盖部分 |
| change/acceptance | 有依据的变更消费者、受影响证据、实际验证与接收结果 |

## 工具只在有用时运行

`artifact_mode=direct|card|prd` 选择阅读规模，`risk_facets` 触发检查；短规则也可高风险。显式治理独立保留。

分诊可只含title，不发明owner、迭代或价值。`triage` accept只建议整理规格，不证明已澄清，不改变状态或优先级。

```bash
python scripts/ai_delivery_spec_cli.py triage --input intake.yaml --format json
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd requirement.md --stage specify
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html
python scripts/ai_delivery_spec_cli.py impact --truth product-truth.yaml --change change.yaml
```

确需机器交接才用 handoff/Truth。`full` 只组合已有输入，不是每次任务终点；参数查 `gate --help`。

PRD 标题自由，`ADS:scope/behavior/acceptance` 仅辅助定位；无法定位返回待评阅，不判缺失。不强制篇幅、附录、API路径或元数据；使用 frontmatter 时须为 YAML 对象。见[模板](templates/unified-requirement-prd-template.md)及[声明校验](../scripts/requirement_contract.py)。

`--scope-ref` 仅限制已明确归属的未知/审查，不过滤无归属风险。静态 PASS 只说明指定声明未发现阻断；GAP与未执行证据保留，不代表业务/浏览器/客户验收。

`gate --profile prd --stage frame|explore` 检查分析结论，省略阶段按baseline。triage不能解析全部排除条件；候选已明确属于另一需求时保留归属、继续当前目标，不照单追问。

审批、表单、权限、指标等复用 [需求模式](patterns/common-requirement-patterns.yaml) 的相关条目；实时协作才读 [实时合同](patterns/realtime-contract.md)。模式提供问题与反例，不替项目决定。旧工具按需查 `--help`；子合同版本独立。

`metrics.unknown_summary` 按范围/阶段去重；旧 `summary.p0_unknowns` 只计同名诊断。兼容入口复用当前内核；无归属疑点仍为GAP，不是已核实阻断或覆盖。

## 契约样例校验

已有机器契约需联调时，按需执行 `python scripts/ai_delivery_spec_cli.py check-examples --input cases.yaml --format json`。复用权威Schema及正反样例，核对拒绝原因；不自动加入PRD gate。输入、边界及退出码见 [用法](../README.md#契约样例校验--contract-examples)。它不证明自然语言一致性或运行行为，工具失败不能当合法拒绝。

## 领域检索

行业问题先查内置切片和来源；中英文长句按已知业务短语检索，无法识别的仍按原文查。零命中可缩短业务词或选领域，不证明没有适用规则。例：

`common_patterns` 单列身份/会话等共性决策提示，不计入行业来源命中；不自动成为政策，已有答案直接继承。

```bash
python scripts/ai_delivery_spec_cli.py query-domain --search "安全考核" --format yaml
python scripts/ai_delivery_spec_cli.py query-domain --domain medical-hospital-it --section "Policy / Privacy Constraints" --source-detail full --language en-US --format yaml
```

按问题读取命中领域的相关段落及 `references/domains/domain-sources.yaml` 中对应来源。无命中再检索外部来源；需要当前法规结论时，已有命中也须核对发布机关原文、修订替代关系、辖区及适用对象。外部检索的旧页面不能无说明地覆盖目录中的较新基线；目录本身也可能过时，无法核实就保留版本未知。

回答跟随用户语言，法规名称和引用可保留原文。区分法定义务、项目授权规则与设计建议；把义务转成行为验收时，不把上传证明、冻结整个账号等可替代实现升级为法规要求。限制权限要对应受约束的对象和动作，不随意扩大范围。
