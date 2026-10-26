# 大任务、上下文与交接

材料多或跨会话时读取；摘要用于导航，不替代原始依据。

## 切片与恢复

按角色路径读取来源/版本/授权及权限、状态、指标、恢复和验收，说明未访问范围。

长任务复用入口指向当前文档、原型及证据，历史结果标时点。恢复和交付时实际打开文件核对内容、生成来源与未决范围；旧生成器先核覆盖性。小改不建检查点体系。

确有机器消费者才用多文件 Truth；按模块生成并校验。大型 PRD 切片编写、事实只维护一处，重组核对内容去向。Word/PDF 须渲染检查标题、单元格、跨页及孤段，文本存在不证明排版正确。

## 按需取领域与结构化资料

按项目及有权来源确定领域；知识包成熟度不是验收证据。

```powershell
python scripts/query_domain.py --domain oa
python scripts/query_product_truth.py --help
python scripts/plan_context.py --help
```

plan_context 估算切片，不强制新增计划。

## 给研发、测试与 Coding Agent 的交接

交接引用目标、规则、输入输出、权威、权限、恢复、验收及禁止推断项的原位置/版本。依赖来源须可获得，否则说明缺什么、谁提供；Mock不代表接通，技术方案由研发负责。

交接引用必须定位到正文真实定义及验收，不为凑manifest另造空ID；模块包由正文摘取并携带必要共享规则，修改回源后再生成。哈希只证明内容未变，不证明语义正确或证据真实。交接注明待同步、待重验和依赖负责人，不虚构责任人。

长期机器执行用 [handoff 模板](templates/agent-handoff-manifest-template.yaml)，强追溯用 execution-state，日常不必填。

```powershell
python scripts/manage_execution_state.py --help
python scripts/ai_delivery_spec_cli.py gate --profile handoff --prd PRD.md --prototype app.html --manifest handoff.yaml
```

执行边界使用环境、权限和凭据引用，不写凭据本身。需求批准不代替外部操作授权。接收方反馈区分规格缺失、来源不可用、已登记未知、投影漂移、实现偏差、技术选择和环境问题，回写对应层；不能把研发忽略已有规则也算成需求遗漏。
