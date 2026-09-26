# 大任务、上下文与交接

材料多或跨会话时读取；摘要用于导航，不替代原始依据。

## 切片与恢复

登记来源、版本、授权和范围，按角色完整路径或业务切片读取，保留权限、状态、指标、恢复与验收。存量走查列明受影响页面、页签、弹层、角色及未访问范围；抽样须注明，不能以首页代替全系统。

长任务在现有检查点记录目标、来源/版本、产物、有效决定、未决依赖和下一步；小改不建。恢复先核实文件及版本，限定冲突范围再合并。压缩保留未完成范围，不把进展包装成完成。

确有机器消费者才使用多文件 Truth；按模块生成、校验引用并重验。大型 PRD 同样切片编写，事实只维护一处。

## 按需取领域与结构化资料

依据项目及有权来源确定领域；通用词不自动决定领域。知识包是候选参考，其成熟度不是验收证据。

```powershell
python scripts/query_domain.py --domain oa
python scripts/query_product_truth.py --help
python scripts/plan_context.py --help
```

复杂项目可用 context-plan Schema/plan_context 估算切片；预算是建议，不强制新增计划或全量审查。

## 给研发、测试与 Coding Agent 的交接

交接引用目标、规则、输入输出、数据权威、权限、失败恢复、验收和禁止推断项的原位置及版本。业务语义依赖的来源须可获得，或指出缺谁提供的什么信息；Mock 数据不能假装已接通来源。技术方案由研发负责。

各输出注明源版本及待同步范围，手工投影不覆盖基线；新决定使旧证据失效时标明范围。多人接力明确边界和依赖负责人，不虚构责任人。

需要长期机器执行时使用 [handoff 模板](templates/agent-handoff-manifest-template.yaml)；
需要强追溯快照时使用 execution-state 工具。这些是明确选择的高级合同，不能反向变成日常 PRD 的必填项。

```powershell
python scripts/manage_execution_state.py --help
python scripts/ai_delivery_spec_cli.py gate --profile handoff --prd PRD.md --prototype app.html --manifest handoff.yaml
```

执行边界使用环境、权限和凭据引用，不写凭据本身。需求批准不代替外部操作授权。接收方反馈区分规格缺失、来源不可用、已登记未知、投影漂移、实现偏差、技术选择和环境问题，回写对应层；不能把研发忽略已有规则也算成需求遗漏。
