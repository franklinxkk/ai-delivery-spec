# 当前目标与工具

阶段是进入点和停止点，允许直接进入，不要求顺次通过。明确小改可在回复或已有产物中完成，不需要 YAML、登记册或 Gate 才能工作。

| 目标 | 当前交付与停止 |
|---|---|
| frame/explore | 现状证据、关键解释/假设、选择及能改变决定的最小验证；有理由的暂缓/不做也可以是结果 |
| intake/clarify | 有效决定、依赖当前决定的未知及处置；授权清楚就继续用户目标 |
| specify | 最小充分业务约定、继承边界、正反验收及未证明范围 |
| prototype | 在明确范围内可操作的产品表现；概念候选标明假设，不能冒充基线 |
| review/baseline | 指定范围获得必要来源、语义复核和授权，保留未覆盖部分 |
| change/acceptance | 有依据的变更消费者、受影响证据、实际验证与接收结果 |

## 工具只在有用时运行

`artifact_mode=direct|card|prd` 只选择阅读规模；`risk_facets` 触发业务检查。高风险小规则可以很短。显式治理请求独立保留，不被小规模覆盖。L0–L4 只作旧输入提示，不再作为补章节或风险证据的依据。

分诊输入用 YAML/JSON 记录已有事实，可只含 title；不发明 owner、迭代或价值。`triage` 的 accept 只建议进入规格整理，不证明需求已清楚，也不改变状态或优先级。

```bash
python scripts/ai_delivery_spec_cli.py triage --input intake.yaml --format json
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd requirement.md --stage specify
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html
python scripts/ai_delivery_spec_cli.py impact --truth product-truth.yaml --change change.yaml
```

正式工程交接确需机器 manifest 时，才使用现有 handoff/Truth Schema。full 是显式组合检查，要求以下已存在输入，不是每次任务的终点：

```bash
python scripts/ai_delivery_spec_cli.py gate --profile full --requirement requirement-register.yaml --prd PRD.md --prototype app.html --manifest handoff.yaml
```

`gate --profile prd` 接受自由标题 Markdown；`ADS:scope/behavior/acceptance` 可辅助定位，不要求固定章数、附录、表格比例或具体 API 路径。无法定位自由文本时返回待评阅范围，不推断业务内容缺失。frontmatter 如使用，必须是合法对象；5.5 声明见 [specify.md](specify.md)。

`--scope-ref` 只限制已明确归属的未知/审查范围。无归属的风险不能被过滤掉。静态 PASS 仅说明已检查声明未发现阻断；GAP 与未执行证据继续保留，不表示业务、浏览器或客户验收。

`gate --profile prd --stage frame|explore` 可检查自由文本的分析结论；省略阶段仍按 baseline。triage 从已给文本返回风险候选和待澄清问题，不能完整解析自然语言的所有排除范围；若候选已明确属于另一需求，应保留其归属并继续当前目标，不照单追问。

审批、表单、权限、指标等复用 [需求模式](patterns/common-requirement-patterns.yaml) 的相关条目；实时协作才读 [实时合同](patterns/realtime-contract.md)。模式提供问题与反例，不替项目决定。旧专业工具按需查 `--help` 和 Schema；子合同版本不必等于 Skill 版本。

JSON `metrics.unknown_summary` 按范围/阶段去重；旧 `summary.p0_unknowns` 仅计同名诊断。兼容 PRD 验证入口复用当前内核。无法定位归属的疑点保留 GAP，不算已核实阻断或已覆盖。

## 领域检索

行业问题先查内置切片和来源；中英文长句按已知业务短语检索，无法识别的仍按原文查。零命中可缩短业务词或选领域，不证明没有适用规则。例：

```bash
python scripts/ai_delivery_spec_cli.py query-domain --search "安全考核" --format yaml
python scripts/ai_delivery_spec_cli.py query-domain --domain medical-hospital-it --section "Policy / Privacy Constraints" --source-detail full --language en-US --format yaml
```

按问题读取命中领域的相关段落及 `references/domains/domain-sources.yaml` 中对应来源。无命中再检索外部来源；需要当前法规结论时，已有命中也须核对发布机关原文、修订替代关系、辖区及适用对象。外部检索的旧页面不能无说明地覆盖目录中的较新基线；目录本身也可能过时，无法核实就保留版本未知。

回答跟随用户语言，法规名称和引用可保留原文。区分法定义务、项目授权规则与设计建议；把义务转成行为验收时，不把上传证明、冻结整个账号等可替代实现升级为法规要求。限制权限要对应受约束的对象和动作，不随意扩大范围。
