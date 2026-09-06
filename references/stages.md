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

分诊输入用 YAML/JSON 对象记录已有事实，最小可只含 title、artifact_mode；不要为调用工具发明 owner、迭代或价值。`triage` 只返回建议，不执行准入、拒绝、延期或优先级更新。

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

旧 frame/explore/clarify 的机器锚点检查与复杂 Truth/评审工具仍可显式调用；自由探索默认不被旧模板合同约束。用到对应工具时读取其 `--help` 和 Schema，不加载所有模板。

兼容入口 `scripts/validators/validate_prd_quality.py` 与 `scripts/validators/validate_unified_prd.py` 可手动执行，均复用当前 PRD 内核。
局部正文检查只按明确的 REQ 标题/表格归属排除范围外项；无法定位的疑点保留 GAP，不能把它当成本次已核实阻断，也不能声称已覆盖。
