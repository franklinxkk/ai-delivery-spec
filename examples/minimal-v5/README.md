# 最小需求示例

这个虚构示例说明如何为制度列表增加“仅看当前有效”筛选。现有权限、时间边界、正常/空/失败结果与验收仍需说清，但不需要完整生命周期。

```powershell
python scripts/ai_delivery_spec_cli.py triage --input examples/minimal-v5/intake.yaml --format json
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd examples/minimal-v5/requirement-card.md --stage specify
```

预期为 card 路由建议及静态 PASS。建议不改变需求状态；PASS 不能证明自然语言风险发现完整、浏览器交互、真实系统或客户验收。

示例保留一份可读取的旧式卡片，演示 5.4.x 内容兼容。新任务可用更短的模板或直接答复；状态、集成、指标等复杂点只补相关语义，不自动升级长 PRD。
