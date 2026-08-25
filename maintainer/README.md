# Maintainer Assurance Lab

本目录仅用于 Skill/模板/Schema/门禁变更的发版加固；日常项目不得加载，也不是客户项目的新阶段。历史探索留在 Git 历史，当前树只保留仍能约束发布结论的不变量、紧凑夹具与证据索引。

## 1. 两条循环必须隔离

```text
方法/发布变更 → 有界模拟/盲测 → 确定性回归 → 发布
客户项目       → 需求工作流 → 统一规格/原型 → 轻门禁 → 人/客户验收
```

维护实验室发现“方法是否漏掉一类需求”；运行门禁发现“当前工件是否违反已知合同”。不得用一组模拟 Reviewer 自我宣布客户项目完成。

## 2. 证据边界

可证明：代表场景覆盖已声明的阶段、角色、风险和产物合同；已知遗漏能被确定性负例捕获。

不能证明：司法辖区/领域正确、临床/金融/安全可靠、真实浏览器/生产行为、客户验收、领域包成熟度或“行业最好”。模拟 Reviewer 不是责任专家，静态 PASS 不能升级签署或验收证据。

`maintainer/evals/industry-assurance-portfolio.yaml` 中的来源只是发现锚点；真实项目仍要登记适用版本、辖区、权威、解释责任人和客户决定。

## 3. 何时运行

以下变化运行相称组合：SKILL 路由/完成语义、统一 PRD/原型/评审/handoff、共享 Schema、领域/能力包、门禁严重度，或生产逃逸暴露新的遗漏类。纯文字勘误只需静态检查。新增行业前先证明其“需求物理”未被已有场景覆盖，禁止一个行业一个文件。

## 4. 有界评审与盲测

只启用风险所需镜头：业务/产品、领域、UX、工程、QA、合规安全、客户验收。每个镜头只读一个稳定 ID 切片，返回受影响 ID、证据、一个可证伪缺口、责任人和关闭条件。按稳定 ID 聚合；多数票不得推翻权威、安全、隐私、金额或验收阻断。

正式比较必须预注册：同一输入、模型、权限、上下文上限、停止条件、隐藏金标和评分规则；隔离各实验臂，记录原始输出、墙钟时间、交互轮次、token、澄清与返工。至少跨三类真实项目、每臂每场景多次重复；单次自报只能算校准，结论最多是“在该有界基准中领先”。

## 5. 轻量运行门禁

运行门禁是守门员，不是作者：

- 零 LLM/子 Agent 调用，不自动重写 PRD/Truth/原型；
- 每个工件最多读取一次并复用索引，只选适用检查；
- 输出严重度、稳定 ID、证据与违反合同，默认按根因收敛；
- P0 fail-fast；完整诊断只供维护者显式请求；
- 只对范围内关键旅程要求浏览器证据；
- 统一状态沿用 `PASS`、`REVIEW_COMPLETE_WITH_GAPS`、`BLOCKED_BY_P0_UNKNOWN`、`BLOCKED`。

## 6. 文件与执行模型

- `maintainer/tests/`：可被 pytest 收集、夹具隔离、普通 assertion 失败；新增行为优先并入能力级不变量测试。
- `maintainer/checks/`：由 CLI 以子进程运行的独立发布检查；不得作为 import API。
- `evals/`：紧凑目录、指标、预注册协议和证据索引，不存一轮一个文件的叙事报告。
- `examples/`：脱敏非运行时参考工程；`tools/`/`schemas/`/`templates/` 只服务维护。

禁止把 import 即 `SystemExit` 的脚本放入 tests。过期夹具应重写或删除；版本号命名的检查只在仍表达独立兼容边界时保留，新测试按能力/不变量命名。优先向现有目录/账本追加记录，只有独立 Schema、不可变原始证据或可单独评审的工具才新建文件。

## 7. 领域包成熟度

方法实践和公共知识成熟度分开：

```text
knowledge_backed → contract_tested → behavior_validated → expert_reviewed → audited
```

| 目标 | 最低证据 |
|---|---|
| `contract_tested` | 来源/覆盖/Schema + 确定性夹具 |
| `behavior_validated` | 独立新会话/新 Agent 原始产物 |
| `expert_reviewed` | 责任专家、范围、发现和关闭证据 |
| `audited` | 受控审计与决策轨迹 |

厂商材料只证明其明确版本/行为；案例只种场景；开源/SDK 只证明被检查组件。禁止用一次场景批量晋级全部领域。

```bash
python maintainer/tools/validators/validate_domain_sources.py
python maintainer/tools/validators/validate_domain_contracts.py
python maintainer/tools/validators/validate_domain_coverage.py
```

## 8. 私有知识与安全

```text
project-local candidate → 跨项目使用证据 → assess → 独立人工评审 → 组织/公共候选 → 回归
```

`candidate assess` 只推荐，不移动、改范围、发布或联网。adopted 不足以晋级；modified/rejected/invalidated 同样保留。项目候选在责任人脱敏并移入 review 前不得进入共享私有包；明文凭据、Token、私密联系方式、客户记录和未授权附件不得进入测试、日志、提示词或公开包。

## 9. Reviewer 合同

评审 intake、统一 PRD、可选 Truth、原型、变更、追溯、handoff 与验收证据；每条发现绑定 `REV-*` 和受影响 ID，未授权不得直接重写：

- P0：目标、权威、安全/合规、数据隔离或验收阻断；
- P1：高概率返工、歧义、旅程断裂或关键证据缺失；
- P2/P3：可读性、维护性、上下文效率和未来风险。

开放 P0/P1 不能藏在备注。结论必须具名范围、ID、证据和未证明事项。

## 10. 预算与发布

实验室从属于运行时。`check_v511_runtime_budget.py` 守住不超过 56 个维护文件、450 KB、默认 fast check 12 条命令；不得为容纳历史产物提高预算。普通使用不加载本目录，候选发布才运行 `check --profile release`。
