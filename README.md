# AI Delivery Spec 5.5.0

帮助产品、业务、设计、研发与测试围绕同一业务含义协作：识别当前决定，交付最小完整规格，并管理变更后的有效性。

AI 能快速生成 PRD 和页面，但团队仍可能在开工后才发现：审批并不等于发布，统计对象并不一致，失败重试会重复写入。**本 Skill 把一句话、现有材料或变更，推进为业务能决定、设计能表达、研发能实施、测试能复现、Coding Agent 能接续的共同业务约定。** 一个有依据的“先验证、暂缓或不做”也可以完成当前分析目标。

## 谁在什么时刻使用

| 核心用户 | 当前需要 | 拿走什么 |
|---|---|---|
| 业务负责人、客户、产品经理 | 判断值不值得做、收敛范围 | 问题证据、选择、最小验证和待授权决定 |
| 产品、设计 | 把规则变为可理解、可操作的体验 | 同源规格与产品态原型，含真实状态和失败路径 |
| 前后端研发、Coding Agent | 实施或接续已有工作 | 已定规则、数据权威、守卫、副作用、边界与稳定引用；工程细节按项目需要补 |
| QA、评审人、验收方 | 找分歧、验证改变 | 关键反例、变更消费者、实际证据及尚未证明的范围 |

这些是同一条用户链的不同读法，不要求每个角色各写一套文档。团队已有资料可直接进入当前阶段；不必先选择等级，也不必从零补齐生命周期。

本工作区为 5.5.0 候选。公开仓库或已安装版本以实际版本为准；本地构建不代表已发布。

## 使用

把安装包解压到宿主识别的 `ai-delivery-spec` 技能目录，使 `SKILL.md` 位于目录根部；保留需要的旧版本备份。无需 Python 即可使用核心指引。运行检查工具时使用 Python 3.10+：

```powershell
python -m pip install -r scripts/requirements.txt
python scripts/ai_delivery_spec_cli.py version
python scripts/ai_delivery_spec_cli.py check
```

在支持技能的宿主中直接提出任务，或明确调用 `$ai-delivery-spec`：

- “给现有列表增加一个筛选，保留现有权限，直接交付。”
- “这个问题是否值得做？给我能改变选择的最小验证。”
- “把审核与发布拆开，说明旧对象、消费者和验收受到什么影响。”
- “基于现有 HTML 做可操作原型；需要双态时再增加评审投影。”

`/ads`、`/dig`、`/prd`、`/proto` 是意图别名；不保证宿主注册了裸命令。只要消息能到达模型，即可用自然语言表达同一目标。

## 5.5.0 的取舍

| 保留的价值 | 减少的义务 |
|---|---|
| 事实、观察、建议、授权决定和未知分开 | 已有用户决定不反复确认 |
| 当前范围的关键业务语义与正反验收 | 不按 L0–L4、角色数或风险自动加长文档 |
| 按主张、范围和版本记录证据 | 不用全局证据等级代替具体证明 |
| 变更依赖路径与旧对象处理 | 图遍历结果只列候选，不自动扩大已批范围 |
| 同一事实多输出、按需交接 | 不默认全流程、全模板、双态或 full/handoff |
| 六类语义抽查与真实接收验证 | 不用固定标题、章节数或模型多数票证明完整 |

六类抽查覆盖状态权威、指标口径、恢复路径、空值/陈旧、权限边界和变更传播。脚本对声明及部分常见正文分歧作有界检查；正文疑点返回带位置和问题的 GAP，填写评阅 pass 不能覆盖它。未命中不证明语义完整，来源名称也不证明授权真实。

## 从小改开始

```powershell
python scripts/ai_delivery_spec_cli.py triage --input examples/minimal-v5/intake.yaml --format json
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd examples/minimal-v5/requirement-card.md --stage specify
```

`triage` 只给建议，不修改优先级或生命周期。明确小改本身不要求先运行脚本。
它读取 title/description/behavior 等已有文本，区分声明风险和正文候选；仍不能完整理解任意自然语言。`ai_write_scope` 未声明表示未知，不默认升级为执行；正文出现自动写回仍会独立提示。
`PASS` 只表示所执行的确定性检查未发现阻断/缺口，不能证明全部业务、交互、实现或客户验收。
风险标签遗漏也不能证明内容无风险。

## 按需深入

- [当前目标与工具](references/stages.md)：路由、停止点、局部 gate。
- [澄清与方案判断](references/discover.md)、[可实施规格](references/specify.md)、[需求处置与基线](references/lifecycle.md)。
- [可操作原型](references/prototype.md)、[可选双态评审合同](references/review-workspace.md)。
- [变更与验收](references/change-acceptance.md)、[上下文与交接](references/context.md)。
- [排错与专业工具](references/troubleshooting.md)、[宿主适配](references/tool-adapters.md)。
- [中型交互评审示例](examples/medium-review-handoff/review-prototype.html)用于明确需要评审态时；它的复杂度不是小改最低门槛，也不是完整发布夹具。

### 常用的进一步操作

```powershell
# 分析建议已形成、实施决定仍未知：按分析阶段检查，不冒充可开发基线
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd analysis.md --stage explore
# 查找领域线索，再读具体章节；英文领域正文可使用 confidence 等原文关键词
python scripts/ai_delivery_spec_cli.py query-domain --search confidence --limit 8
python scripts/ai_delivery_spec_cli.py query-domain --domain ai-native --section 指标
# 修改存量原型时比较旧文件，区分旧问题与本次回归
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype app.html --prototype-baseline old-app.html
```

不传 `--stage` 时 gate 保留 `baseline` 默认值；建议暂缓不会自动降低检查阶段。分析可完成并保留实施 GAP，只有获权才能改变需求生命周期。领域搜索命中是候选，章节中的行业经验不是项目已批准规则。

`impact` 的最小输入可用顶层 `seed_refs: [REQ-A]`，也兼容正式包中的 `request.seed_refs`；二者同时给出时必须一致。图上的相关对象仍是候选，需要核实具体依赖后才进入正式变更范围。

## 兼容边界

5.4.x 原始产物可以继续读取，稳定 ID 和已批准事实保留。新的 `artifact_mode` 选择 direct/card/prd；旧 L0–L4 在 PRD 中只作呈现提示，不能覆盖显式模式或提高风险/证据等级。矛盾的显式模式仍报错。

专业原型、评审工作区、Truth、handoff、执行状态等工具保留其版本化 Schema 和既有严格合同；不自动迁移旧产物。它们不是日常需求的默认依赖。旧 Markdown PRD 兼容入口使用同一个 5.5 检查内核，退出码与原有章节型门禁可能不同。

5.5 triage 输出采用 `recommendation / artifact_mode / risk_facets / governed`；移除旧的 tier/mode 推导结果键。消费旧输出的脚本需要调整。旧 `validate_prd_quality.py --domain-rules` 关键词检查已退役，领域约束使用显式 custom gate/领域工具。

## 验证与维护

```powershell
python -m pip install "pytest>=8,<9"
python scripts/ai_delivery_spec_cli.py check --profile release
python maintainer/tools/build_runtime_package.py --release --check --output dist/ai-delivery-spec-5.5.0.zip
```

最后一条要求干净 Git 来源。维护实验、私有样本及凭据不进入运行包。
源码中的 `maintainer/README.md` 记录验证范围和规则删减；运行包不包含维护实验目录，`check` 在运行包中只验证其实际携带的文件和契约。

**English:** A lean requirements skill for current product decisions, precise business behavior, scoped evidence and change impact. Simple changes stay simple; specialized tools are explicit. Deterministic checks do not prove business correctness, implementation or customer acceptance.

许可证：[Apache 2.0](LICENSE)。
