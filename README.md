# AI Delivery Spec 5.1.4

> 需求一来就写 PRD，低价值需求也进入重型设计？
>
> PRD 写了几十页，传统开发看不下去，AI Coding 仍在猜规则？
>
> 需求一变，页面、字段、接口、测试和验收漏改，最后无法审计？

**AI Delivery Spec 是面向 ToB/ToG、兼顾 ToC 的需求管理 Skill。**
它不接管研发项目管理，只把需求从准入、澄清、定稿、变更、追溯到验收，变成
业务能确认、产品能维护、开发和测试能执行、Coding Agent 不必猜的同一份交付契约。

默认交付不是两套 PRD，也不是先造一个巨型 YAML，而是**一份统一需求规格说明书**：
正文让客户、产品和传统开发顺序读懂，同文档工程附录让测试与 AI Coding 精确执行。
只有大项目、持续变更、多投影或强审计场景才启用分片 Product Truth。

[![Version](https://img.shields.io/badge/version-5.1.4-0052A4.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)

**公开采用信号（截至 2026-07-14）**：
[ClawHub 606 次下载](https://clawhub.ai/franklinxkk/skills/ai-delivery-spec) ·
[skills.sh 16 次安装](https://www.skills.sh/franklinxkk/ai-delivery-spec) ·
[SkillHub TRACE 4.7/5](https://skillhub.cn/dashboard/evaluation/ai-delivery-spec)，双安全扫描无 P0/P1 风险。
这些是第三方平台的动态公开快照，用于说明已有真实关注与安装，不替代项目适用性判断。

## 60 秒上手：选一个任务，复制即用

不必手工克隆仓库。任选与你的 Agent 环境匹配的安装方式：

```bash
# Codex / Claude Code / Cursor / Trae 等 Agent Skills 兼容工具
npx skills add franklinxkk/ai-delivery-spec

# OpenClaw
openclaw skills install @franklinxkk/ai-delivery-spec
```

安装后复制下面一条指令；拿不准时从 **Standard L2** 开始，Skill 会先分诊，不会把
小需求强行升级成重交付。

### Ultra-Light — 一个可逆小改动 / ToC Idea

```text
使用 AI Delivery Spec Ultra-Light：先做需求准入，再把“列表新增一个可选字段”写成一页需求卡；包含目标、范围、字段规则、正反验收。不要生成独立 Product Truth。
```

### Standard L2 — 常规需求 / 一份完整 PRD

```text
使用 AI Delivery Spec Standard L2：盘点我给的材料，批量澄清互不依赖的问题，然后交付一份人类可读且 AI Coding 可直接使用的统一 PRD。所有角色、流程、状态、权限、字段、异常和验收必须闭环，不要拆成两套 PRD。domain=generic
```

### Full L3 smart-large-project — 多角色 / 存量改造 / 监管项目

```text
使用 AI Delivery Spec Full L3 smart-large-project：先完成需求准入和全量 REQ/角色/流程/页面/字段/验收索引，再按切片持续写入同一份统一 PRD；仅在多文档、持续变更或强审计需要时生成分片 Product Truth。domain=traffic
```

手动修正：`mode=ultra_light|lite|standard|full tier=L0|L1|L2|L3|L4 domain=<pack>`。
黄金入门示例见 [examples/minimal-v5](examples/minimal-v5/README.md)。

## 第一次使用，你会拿到什么

- **先有准入结论**：目标、价值、范围、责任人和未知项不足时，先列出需要确认的批次，
  不用一份看似完整的 PRD 掩盖决策空洞。
- **再有一份可读的基线**：角色旅程、页面、字段、规则、权限、状态、异常、接口和验收
  使用稳定 ID 互相绑定；传统开发读正文，Coding Agent 同时读取工程附录。
- **需要原型时才交付原型契约**：已有原型先做 Stage 0 反向盘点，保留视图、动作、状态
  和角色路径覆盖；新原型要求每个动作有处理器和可见结果。
- **最后有轻量门禁结论**：`PASS`、`REVIEW_COMPLETE_WITH_GAPS` 或 `BLOCKED`，明确哪些
  已被静态证明、哪些仍需领域负责人、浏览器旅程或客户验收。

## 常见的第一次疑问

**这个 Skill 重吗？** 不是固定重。单字段、单角色、可逆改动走 Ultra-Light；常规需求
走 Standard L2；只有规模或审计阈值触发才加载分片真相、领域包和完整门禁。

**每次都要生成 Product Truth YAML 吗？** 不要。它是复杂项目的内部单源事实，不是
默认交付物。普通项目以一份统一 PRD 为基线，避免 Trae、WorkBuddy 等工具被巨型 YAML
拖慢或中断。

**PRD 能直接交给开发和 Coding Agent 吗？** Standard L2 以上在角色、流程、状态、权限、
字段、接口、异常和机器验收通过对应门禁后，可以作为同一开发基线；未确认的法规、客户
决策和领域规则仍必须显式标为未知，Agent 不得自行发明。

**它会替代产品、架构、测试或甲方吗？** 不会。它统一交付口径、暴露缺口并保留证据，
但范围决策、技术方案、专业领域判断和最终签署仍由相应责任人完成。

## 只管六件事

| 能力 | 解决的问题 | 核心产物 |
|---|---|---|
| 需求准入 | 过滤低价值、边界不清或错配等级的需求 | `REQ-*`、价值/复杂度/优先级、准入结论 |
| 需求澄清 | 从模糊 Idea 到可判定业务规则 | 来源、问题批次、`REV-*`、关闭证据 |
| 规格交付 | 全角色共用口径且传统开发可读 | 一份统一 PRD + 同文档工程附录 |
| 需求变更 | 防止口头变更和漏改 | `CHG-*`、影响分析、diff、审批、同步、回归 |
| 双向追溯 | 从需求追到页面/字段/AC，也可从缺陷反查 | 正向/反向稳定 ID 账本、审计日志 |
| 需求验收 | 不止定义 AC，还记录执行结果 | `ARUN-*`、证据、缺陷、条件、签署结论 |

研发排期、Sprint/任务、代码、CI/CD、部署执行、监控和运营属于下游系统。
本项目只记录它们与需求/验收有关的外部引用，不接管流程。

## 5.1.x 如何解决真实项目中的失败

一次交通出版平台实战中，旧版结构校验可以 PASS，但仍出现三个典型问题：

- 机器契约直接成为主文档，90KB PRD 对传统开发不可读；
- Human-First 与 AI Coding PRD 分开维护，团队无法确认哪份才是基线；
- 普通需求也先生成大型 Product Truth，长上下文工具反复中断，增加交付成本。

5.1.x 因此改变默认路径：

1. **先准入**：没有价值证据、责任人或范围边界，先澄清，不直接上重型规格。
2. **一份 PRD**：业务正文和工程附录在同一文件、同一版本、同一评审链路中。
3. **Product Truth 按需**：12+ 页面/模块、持续变更、多投影或强审计才独立生成；
   大项目仍采用分片真相，避免一次性巨型 YAML。
4. **变更可计算**：从变更种子双向遍历关联 ID，生成影响清单和回归范围。
5. **验收有结果**：AC、执行项、实际结果、证据、缺陷和签署形成闭环。
6. **模式可复用**：审批、权限、集成、数量谱系、金额结算、部分执行和跨聚合等
   场景提供问题/异常/AC 蓝图，但必须绑定项目证据，不能把模板当已确认需求。
7. **双层质量保障**：发布前用跨行业多 Agent 组合找方法缺口；每个项目末端只运行
   零模型、单遍解析的轻量门禁，不把验证器做成第二个生成器。

仓库内的 10 个结构化准入基准覆盖小改动、信息缺失、监管、安全、跨角色、依赖阻塞、
低价值、重复、大项目和存量迁移，当前推荐结果为 10/10。

## 快速命令

```bash
python scripts/ai_delivery_spec_cli.py init-requirements --output requirements
python scripts/ai_delivery_spec_cli.py triage --input requirements/intake.yaml --format markdown
python scripts/scan_requirement_ambiguity.py requirements/PRD.md
python scripts/validators/validate_requirement_register.py requirements/register.yaml
python scripts/validators/validate_prd_quality.py requirements/PRD.md --level L2
python scripts/validators/validate_coding_agent_contract.py requirements/PRD.md --level L2 --profile full_prd
python scripts/validators/validate_acceptance_run.py requirements/acceptance/ARUN-CORE-001.yaml
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd requirements/PRD.md --level L2
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype prototype.html --level L2
python scripts/query_domain.py --domain oa --format markdown
```

`gate` 只判定和定位，不生成、不自动修复；支持 `requirement`、`prd`、`prototype`、
`full` 四个按需 Profile，默认最多报告 20 个问题。静态通过不替代领域负责人、浏览器
关键旅程或客户验收。

## 跨行业质量保障，而不是每项目多 Agent 税

v5.1.x 的发布保障组合覆盖制造、医疗、金融保险、能源、零售电商、数字政府、
建筑工程七类需求物理，以及既有交通、CRM、教育、数据产品和 AI Native 组合。
每个场景贯穿准入、澄清、规格、评审、基线、变更、验收，并由业务、产品、领域、
UX/原型、研发架构、测试验收、合规安全、客户验收八个镜头检查统一 PRD、工程原型
和机器验收。详见 [保障实验室](references/runtime/assurance-lab.md) 与
[行业组合](evals/industry-assurance-portfolio.yaml)。

这套多 Agent 压测只在 Skill、模板、领域包或校验器变化时运行。模拟结果不等于行业
专家确认、客户签署或生产证据；普通项目只承担与自身等级匹配的轻门禁成本。

仅当规模/审计门槛触发时：

```bash
python scripts/ai_delivery_spec_cli.py init-requirements --output requirements --with-product-truth
python scripts/ai_delivery_spec_cli.py trace --truth requirements/truth/compiled/product-truth.yaml --output requirements/traceability.yaml --baseline-version 1.0
python scripts/ai_delivery_spec_cli.py impact --truth requirements/truth/compiled/product-truth.yaml --change requirements/changes/CHG-001.yaml
```

## 一份统一 PRD 的阅读层次

| 阅读者 | 先读 | 需要的精确内容 |
|---|---|---|
| 客户/业务 | 背景、范围、角色旅程、业务流程、验收 | 目标、边界、责任和结果 |
| 产品/设计 | 正文全部 | 页面、交互、状态、规则和异常 |
| 传统开发 | 正文后读工程附录 | 字段、状态机、API、事件、兼容 |
| 测试 | 流程/异常/验收和追溯附录 | 正反用例、证据和缺陷回链 |
| Coding Agent | 全文 | 禁止推断清单、稳定 ID、机器 AC |

独立 YAML/JSON 是按工具需要导出的视图，不是第二份权威 PRD。

## 各级产品、开发和架构师如何协同

| 使用者 | 独立完成 | 必须升级/交接 |
|---|---|---|
| 初级产品 | 盘点、REQ/REV、旅程/规则/AC 草案 | 范围价值、权威冲突、敏感/监管规则和 P0 未知 |
| 中高级产品 | 准入、澄清、统一 PRD、基线、变更和追溯 | 超出授权的客户、法律、安全和合同决策 |
| 初中级开发/Coding Agent | 实现已基线的稳定 ID 切片并回报歧义 | 缺失角色、状态、权限、规则或接口语义，不得自行发明 |
| 高级开发/架构师 | 可实现性、跨系统状态、接口事件、迁移、恢复和 NFR 设计 | 产品范围、客户验收和领域权威仍由责任人决定 |
| 测试/领域/客户 | 反例、领域结果、执行证据和签署 | 静态 PASS 或开发自测不能替代其责任 |

多角色或正式交接时才读取
[角色阶段手册](references/runtime/role-stage-playbook.md)，普通单角色小改动不加载。

## 领域实践与知识包保证分开

| 领域包 | 实践状态 | 可复用包成熟度 | 使用边界 |
|---|---|---|---|
| `traffic` | `production_practiced` | `contract_tested` | 方法已用于上线项目；法规和项目适用性仍需确认 |
| `crm` | `production_practiced` | `contract_tested` | 方法已用于上线项目；复杂商业规则按项目确认 |
| `education-it` | `production_practiced` | `contract_tested` | 方法已用于上线项目；教育形态按项目确认 |
| `data-product` | `production_practiced` | `contract_tested` | 方法已用于上线项目；血缘/口径/删除传播按项目确认 |
| `ai-native` | `production_practiced` | `contract_tested` | 方法已用于上线项目；模型与安全治理必须项目评测 |
| `oa` | `knowledge_only` | `contract_tested` | 法规/标准/厂商材料已映射；仍需真实行为和 OA 专家复核 |
| `medical-hospital-it` | `knowledge_only` | `contract_tested` | 不得据此推导临床生产结论 |

`production_practiced` 说明相关方法有真实上线实践；`contract_tested` 只说明来源、
关键不变量和14个轻量契约场景通过确定性回归，不等于真实 Agent 行为、专家审查、
客户验收或生产正确性。成熟度继续按 `behavior_validated → expert_reviewed → audited`
逐领域升级。白皮书、案例、开放平台和 SDK 的证据边界详见
[领域保证规则](references/runtime/domain-assurance.md) 与
[references/domain-coverage.yaml](references/domain-coverage.yaml)。

## 与上下游工具的边界

| 位置 | 工具类型 | 责任 |
|---|---|---|
| 上游 | 产品发现、调研、工作坊 | 发现机会、证据和策略假设 |
| **需求管理内核** | **AI Delivery Spec 5.1.4** | 准入 → 澄清 → 基线 → 变更 → 追溯 → 验收 |
| 下游 | Spec Kit、项目/研发管理工具 | 技术方案、任务、排期和依赖执行 |
| 下游 | Codex、Trae、Cursor、Qoder 等 | 依据已基线需求编码、测试和修改 |
| 外部证据 | CI、测试、发布、监控平台 | 向需求验收回传可引用证据 |

这是职责互补关系，不是未经对照实验的质量排行榜。

## 仓库结构

```text
.github/      社区文件、工作流和发布材料
agents/       Agent 入口与国产工具适配
evals/        基准、运行记录和证据
examples/     极简、标准和领域示例
references/   需求管理规则、领域包和模板
schemas/      需求登记、Product Truth、变更、追溯和验收契约
scripts/      CLI、编译/分析脚本和 validators/
tests/        结构、行为和回归测试
```

## 维护与验证

```bash
python scripts/ai_delivery_spec_cli.py check --keep-going
python scripts/validators/validate_v5_architecture.py
python tests/test_v510_requirement_management.py
python tests/test_v510_unified_prd.py
python tests/test_v510_semantic_guards.py
python tests/test_v510_lightweight_gate.py
python tests/test_v510_industry_assurance.py
python tests/test_v511_runtime_budget.py
python tests/test_v511_role_stage.py
python tests/test_v511_domain_assurance.py
python scripts/validators/validate_domain_contracts.py
```

一键生成 Mermaid：

```bash
python scripts/render_mermaid_flow.py --truth product-truth.yaml --output flow.mmd
```

贡献、安全与许可证见 [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)、
[.github/SECURITY.md](.github/SECURITY.md) 和 [LICENSE](LICENSE)。
