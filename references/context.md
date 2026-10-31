# 大任务、上下文与交接

材料多或跨会话时读取；摘要用于导航，不替代原始依据。

## 切片与恢复

按角色路径读取来源/版本/授权及权限、状态、指标、恢复和验收，说明未访问范围。

长任务入口指向当前文档、原型和证据；恢复时实际回读版本、来源、未决范围，旧生成器先核覆盖性。小改不建检查点体系。

交接修订稿在现有文档开头保留需求身份、修订标记、取代关系和决定/未决的位置。例：“REQ-REPAIR／1.2 取代 1.1；仅改说明上限，原权限继续有效，离线提交待定。”回读模块原文，不凭摘要补政策。

机器消费者才用多文件Truth；模块切片重组核对内容，事实只维护一处。Word/PDF实际渲染检查标题、表格、分页，不能以文本抽取替代。

## 按需取领域与结构化资料

按项目及有权来源确定领域；知识包成熟度不是验收证据。

```powershell
python scripts/query_domain.py --domain oa
python scripts/query_product_truth.py --help
python scripts/plan_context.py --help
```

plan_context 估算切片，不强制新增计划。

## 给研发、测试与 Coding Agent 的交接

交接引用目标、规则、输入输出、权限、恢复、验收及待决项的权威位置/版本。缺来源说明提供者；Mock不代表接通，技术方案留研发。

引用定位真实定义，不造空ID；模块包摘取正文与共享规则，修改回源。哈希不证明语义或证据真实。注明待同步、重验及实际依赖负责人。

接收者无法访问原文时，附本范围的条件、结果、拒绝/恢复、验收和未决原文及来源版本。ID 清单不能替代正文；已有可读模块包就不重复快照。接收者须能复述“做什么、何时拒绝、怎么验收”。

长期机器执行用 [handoff 模板](templates/agent-handoff-manifest-template.yaml)，强追溯用 execution-state，日常不必填。

```powershell
python scripts/manage_execution_state.py --help
python scripts/ai_delivery_spec_cli.py gate --profile handoff --prd PRD.md --prototype app.html --manifest handoff.yaml
```

执行边界使用环境、权限和凭据引用，不写凭据本身。需求批准不代替外部操作授权。接收方反馈区分规格缺失、来源不可用、已登记未知、投影漂移、实现偏差、技术选择和环境问题，回写对应层；不能把研发忽略已有规则也算成需求遗漏。

反馈例：“REQ-REPAIR／1.2；重试又追加审计，见本次日志；实现偏差；修实现，不改规则。”保留版本、差异、证据、类别及是否请求改需求；反馈不授予变更权。
