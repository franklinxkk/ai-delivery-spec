# Minimal v5 — 5 分钟完成第一次可验证交付

这是中文用户的黄金入门示例：一个单角色、可逆、局部 UI 调整只生成一页需求卡，
不会加载领域包、Product Truth 或重型工程附录。

## 先把这句话交给 Agent

```text
使用 ai-delivery-spec 处理“制度列表增加仅看当前有效筛选”：先准入，再补齐范围、字段规则、
正常/空结果/无权异常和正反验收；保持一页需求卡，不生成 Product Truth。输出语言跟随中文。
```

Agent 应先确认这是需求卡，而不是要求用户选择 mode、tier、domain。仓库内已经提供一份
已闭合的示例输入和需求卡，安装依赖后可直接验证：

```powershell
py -3 scripts/ai_delivery_spec_cli.py triage --input examples/minimal-v5/intake.yaml
py -3 scripts/ai_delivery_spec_cli.py gate --profile prd --prd examples/minimal-v5/requirement-card.md --level auto
```

期望结果：分诊建议 `requirement_card`，门禁返回 `PASS`。这只证明该需求卡结构完整、
可测试；不等于真实客户已经验收。

## 这个示例教会三件事

1. 小改动只写完成工作所需的最小规格，不为了套模板升级成完整 PRD。
2. 一页需求卡仍要闭合角色、权限、正常路径、空结果、失败恢复和正反验收。
3. 用户用中文提问时，标题、正文、表头和验收默认使用中文；稳定 ID 保持不变。

下一步：跨角色、状态流、数据上报、指标、批量、审批、集成或高风险需求会自动升级为
统一 PRD。只有多投影、持续跨模块变更、数据血缘或强审计才按需启用 Product Truth。
