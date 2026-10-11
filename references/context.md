# 大任务、上下文与交接

材料多或跨会话时读取；摘要用于导航，不替代原始依据。

## 切片与恢复

按角色路径或业务切片读取，登记来源/版本/授权，保留权限、状态、指标、恢复及验收。存量列明页面、页签、弹层、角色与未访问范围；抽样不代表全系统。

长任务复用检查点记录目标、基线、产物、有效决定、未决依赖和下一步；小改不建。恢复先核实文件及版本再合并，保留未完成范围。

确有机器消费者才使用多文件 Truth；按模块生成、校验引用并重验。大型 PRD 同样切片编写，事实只维护一处。

## 按需取领域与结构化资料

按项目及有权来源确定领域；通用词不决定领域，知识包成熟度不是验收证据。

```powershell
python scripts/query_domain.py --domain oa
python scripts/query_product_truth.py --help
python scripts/plan_context.py --help
```

复杂项目可用 plan_context 估算切片；预算不强制新增计划或全量审查。

## 给研发、测试与 Coding Agent 的交接

交接引用目标、规则、输入输出、权威、权限、恢复、验收及禁止推断项的原位置/版本。依赖来源须可获得，否则说明缺什么、谁提供；Mock不代表接通，技术方案由研发负责。

输出标明源版本、待同步及证据失效范围；手工投影不覆盖基线。接力写清边界和依赖负责人，不虚构责任人。

长期机器执行才用 [handoff 模板](templates/agent-handoff-manifest-template.yaml)，强追溯才用 execution-state；不作为日常PRD必填项。

```powershell
python scripts/manage_execution_state.py --help
python scripts/ai_delivery_spec_cli.py gate --profile handoff --prd PRD.md --prototype app.html --manifest handoff.yaml
```

执行边界使用环境、权限和凭据引用，不写凭据本身。需求批准不代替外部操作授权。接收方反馈区分规格缺失、来源不可用、已登记未知、投影漂移、实现偏差、技术选择和环境问题，回写对应层；不能把研发忽略已有规则也算成需求遗漏。
