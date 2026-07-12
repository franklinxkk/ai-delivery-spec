# AI Delivery Spec 5.0.2

> PRD 写了几十页，开发仍在猜业务规则？
>
> 原型能演示，角色、异常和数据却走不通？
>
> 客户、产品、研发、测试各拿一套口径，最后靠返工对齐？

**AI Delivery Spec 不是 PRD 模板，而是面向 ToB/ToG 的产研统一交付契约。**
它把需求、页面、动作、状态、数据、接口、验收和变更锁定在同一组稳定 ID 上，让人类团队和 AI Coding 工具基于同一事实工作。

交通、CRM、教育 IT、数据产品、AI Native 方法已由项目负责人确认用于开发上线项目；仓库同时保留独立的知识包验证等级，避免把“做过项目”夸大成“所有规则都已审计”。

[![Version](https://img.shields.io/badge/version-5.0.2-0052A4.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)

## 60 秒上手：无需克隆，Agent 直接调用

先安装一次：

```bash
npx skills add franklinxkk/ai-delivery-spec
```

然后复制与你场景匹配的一条指令：

### Ultra-Light — ToC/单页/小改动/快速 Idea/PRD

```text
使用 AI Delivery Spec Ultra-Light：把“列表新增一个可选字段”写成一页需求卡，包含范围、字段规则、正向和负向验收；不要生成整套 Product Truth。
```

### Standard L2 — 常规产品开发与客户交付

```text
使用 AI Delivery Spec Standard L2：先盘点我给的材料和已确认决策，再生成完整 Human-First PRD、可测试原型、完整 AI Coding PRD 和机器可读验收；所有角色、流程、状态和数据必须闭环。domain=generic
```

### Full L3 smart-large-project — 多角色/多模块/AI/监管项目

```text
使用 AI Delivery Spec Full L3 smart-large-project：先建立完整 ID 清单，再按模块写入分片 Product Truth 和 PRD 切片，持续检查点交付；不得因上下文压力省略 P0 角色、异常、权限、接口或验收。domain=traffic
```

手动修正：`mode=ultra_light|lite|standard|full tier=L0|L1|L2|L3|L4 domain=<pack>`。
黄金入门示例见 [examples/minimal-v5](examples/minimal-v5/README.md)。

## 四个核心能力

**分层弹性交付**：一个字段改动不背重框架，复杂 ToB/ToG 项目也不会被轻量模式偷偷裁掉关键行为。

**单源 Product Truth**：角色、流程、页面、动作、状态、字段、事件和验收只维护一次，再投影给产品、原型、研发、QA 和客户。

**AI 原生治理**：为 AI 功能对齐业务不变量、运行时、评测、权限、人工责任和运维契约。

**工程化校验**：L0–L4 校验器检查结构和可执行契约，不再用几个关键词把残缺 PRD 判成通过。

## 5.0.2 为什么更快、更完整

- **分片真相**：大项目默认生成 `truth/index.yaml + fragments/*.yaml`；Agent 每次只写一个模块，脚本确定性合并，Trae/WorkBuddy 不再承担巨型 YAML 的一次性生成。
- **完整契约直达**：需求已澄清且用户明确要 AI Coding PRD 时，直接按完整契约分节写作，不先生成一份薄投影再反复补洞。
- **断点续作**：先锁定全量 ID 清单，再按模块/流程检查点推进；上下文紧张时切片，不压缩 P0 行为。
- **结构验收**：L2 必检仓库基线、页面布局、字段字典、API 请求/响应、错误码、事件 Payload、集成、统计口径、切片依赖和机器 AC。

初始化分片交付包并编译：

```bash
python scripts/ai_delivery_spec_cli.py init-delivery --output delivery
python scripts/ai_delivery_spec_cli.py compile-truth --index delivery/truth/index.yaml
python scripts/validators/validate_coding_agent_contract.py delivery/projections/ai-coding-prd.md --level L2 --profile full_prd
```

小项目确需单文件时使用 `--truth-layout monolith`。

## 主力定位与生态链路

### ToB/ToG 交付工具定位榜（按交付生命周期覆盖）

| 定位 | 工具 | 最适合承担的环节 |
|---|---|---|
| **主力交付内核** | **AI Delivery Spec 5.0.2** | 澄清 → 统一事实 → PRD/原型 → AI Coding/QA → 验收/变更/运营 |
| 上游发现方法 | pm-skills / product discovery skills | 机会识别、发散、工作坊、战略与指标方法 |
| 上游压力测试 | grill-me / schema questioning | 对抗式追问、暴露歧义 |
| 下游工程规格 | GitHub Spec Kit | 已确认产品契约后的技术规划与任务化 |
| 下游工程执行 | Superpowers / Coding Agents | TDD、实现、审查、分支与发布 |

这是按生命周期职责划分的定位榜，不是未经对照实验的“质量排行榜”。

### 上下游互补链路

| 阶段 | 可组合工具 | AI Delivery Spec 的责任 |
|---|---|---|
| 探索 | PM 方法、调研、工作坊 | 接收已确认的 outcome、机会、假设和证据 |
| 澄清/收敛 | grill-me、访谈、材料盘点 | 建立来源优先级、决策、未知项和范围 |
| **主交付** | **AI Delivery Spec** | 统一角色/流程/页面/数据/接口/验收契约 |
| 规划/编码 | Spec Kit、Codex、Trae、Cursor、Qoder | 提供禁止发明的完整 AI Coding 契约和切片 |
| 验证/上线 | QA、CI、运维平台 | 绑定 AC、证据、变更、回滚与运营责任 |

## 领域实践状态不是知识包验证等级

| 领域包 | 交付实践状态 | 可复用知识包保证等级 | 当前使用边界 |
|---|---|---|---|
| `traffic` | `production_practiced` | `experimental` | 已有上线实践；通用包仍需项目证据和适用性确认 |
| `crm` | `production_practiced` | `experimental` | 已有上线实践；复杂 CPQ/伙伴冲突仍需项目验证 |
| `education-it` | `production_practiced` | `experimental` | 已有上线实践；细分教育形态仍需项目验证 |
| `data-product` | `production_practiced` | `experimental` | 已有上线实践；血缘/成本/删除传播按项目验证 |
| `ai-native` | `production_practiced` | `experimental` | 已有上线实践；模型、工具和安全治理按项目评测 |
| `oa` | `knowledge_only` | `experimental` | 作为问题和候选模式使用 |
| `medical-hospital-it` | `knowledge_only` | `experimental` | 不允许从模拟场景推导临床生产结论 |

`production_practiced` 证明相关方法在上线项目中使用过，不等于当前仓库版本已通过独立行为评测、专家审查或审计。证据与边界见 [references/domain-coverage.yaml](references/domain-coverage.yaml)。

## 适配工具

Codex、Claude Code、Cursor 以及 GLM 5.2、Qwen、DeepSeek、Kimi、WorkBuddy、Trae、Qoder 的入口说明位于 `agents/`；国产工具的短上下文、断点续作和分片规则位于 `agents/domestic/`。

## 仓库结构

```text
.github/      社区文件、工作流和发布材料
agents/       Agent 入口；国产适配在 domestic/
evals/        基准、运行记录和证据
examples/     极简、标准和领域示例
references/   3 个核心入口、领域索引、runtime/domains/templates
schemas/      Product Truth、分片、变更和验收 Schema
scripts/      CLI、编译器；校验器在 validators/
tests/        结构、行为和回归测试
```

根目录只保留 `README.md`、`SKILL.md`、`LICENSE`、`CHANGELOG.md`、`.gitignore`、`.gitattributes`。

## 维护与验证

```bash
python scripts/ai_delivery_spec_cli.py check --keep-going
python scripts/validators/validate_v5_architecture.py
python scripts/validators/validate_domain_coverage.py
python tests/test_v502_progressive_truth.py
python tests/test_v502_coding_contract.py
```

一键生成 Mermaid：

```bash
python scripts/render_mermaid_flow.py --truth delivery/truth/compiled/product-truth.yaml --output delivery/projections/flow.mmd
```

贡献、安全与许可证见 [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)、[.github/SECURITY.md](.github/SECURITY.md) 和 [LICENSE](LICENSE)。
