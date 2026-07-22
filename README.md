# AI Delivery Spec 5.3.2 — Requirements Humans Can Read, Coding Agents Can Execute

> 需求一来就写 PRD，低价值需求也进入重型设计？
>
> PRD 写了几十页，传统开发看不下去，AI Coding 仍在猜规则？
>
> 需求一变，页面、字段、接口、测试和验收漏改，最后无法审计？

**One Requirement Baseline. Human-Readable. AI-Coding-Ready. Traceable to Acceptance.**
**AI Delivery Spec 是面向 ToB/ToG、兼顾 ToC 的需求管理 Skill。**它不接管研发项目管理，而是把从
需求准入、澄清、定稿、变更、追溯到验收的事实，统一成业务可确认、产研可执行、Coding Agent 不必猜的契约。

默认交付不是两套 PRD，也不是先造一个巨型 YAML，而是**一份统一需求规格说明书**：
正文让客户、产品和传统开发顺序读懂，同文档工程附录让测试与 AI Coding 精确执行。
只有大项目、持续变更、多投影或强审计场景才启用分片 Product Truth。

[![Version](https://img.shields.io/badge/version-5.3.2-0052A4.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)

<!-- CLAIM: CLM-ADOPTION-20260719; as_of=2026-07-19; evidence=public-platform-links-below -->
**公开采用信号 / Public Adoption Signals（截至 2026-07-19）**：
[ClawHub 850 次下载](https://clawhub.ai/franklinxkk/skills/ai-delivery-spec) · [skills.sh 23 次安装](https://www.skills.sh/franklinxkk/ai-delivery-spec) ·
[SkillHub TRACE 4.6/5](https://skillhub.cn/skills/ai-delivery-spec)，双安全扫描均为安全、无风险。
这是第三方动态快照，不替代项目适用性判断；领域成熟度见 [release-status.yaml](maintainer/evals/evidence/release-status.yaml) 和 [domain-coverage.yaml](references/domain-coverage.yaml)。

### 30 秒术语速览 / 30-Second Glossary

- **Stable ID｜稳定 ID**：需求、动作、字段、规则和验收的长期编号，改文案也不丢追溯。
- **Product Truth｜结构化事实源**：仅复杂多投影/强审计项目按需启用；普通需求不生成。
- **Gate｜门禁**：零模型静态检查结构、锚点和追溯；L3 原型还需浏览器 `ARUN-*`，静态 PASS 不等于业务或客户验收通过。

## 它直接帮助谁 / Who It Helps

| 使用者 | 直接获得的帮助 |
|---|---|
| 客户、业务与项目负责人 | 在投入设计前确认价值、范围、优先级、责任和验收边界 |
| 初中高级产品与设计 | 分批澄清，形成一份可读 PRD，并把角色旅程、页面、字段、状态和异常闭环 |
| 前后端与架构师 | 获得可施工的页面合同、关系台账、指标口径、数据流、接口语义和禁止推断边界 |
| 测试、实施与验收人员 | 从 `AC-*` 生成正反用例、证据要求，并把缺陷反向追到原需求 |
| Codex、Trae、Cursor、Qoder 等 Coding Agent | 按稳定 ID 切片实现，不再猜角色、字段、业务规则或成功标准 |

## 60 秒上手 / Start in 60 Seconds

不必手工克隆仓库。任选与你的 Agent 环境匹配的安装方式：

```bash
# Codex / Claude Code / Cursor / Trae 等 Agent Skills 兼容工具
npx skills add franklinxkk/ai-delivery-spec

# OpenClaw
openclaw skills install @franklinxkk/ai-delivery-spec
```

运行本地校验需 Python 3.10+：先执行 `python -m pip install -r scripts/requirements.txt`；
Windows 的 `python` 若是商店占位符，请改用已安装解释器的完整路径或 `py -3`。

安装后复制下面一条指令；拿不准时从 **Standard L2** 开始，Skill 会先分诊，不会把
小需求强行升级成重交付。

### 一个可逆小改动 / ToC Idea（兼容名：Ultra-Light）

```text
使用 AI Delivery Spec Ultra-Light：先做需求准入，再把“列表新增一个可选字段”写成一页需求卡；包含目标、范围、字段规则、正反验收。不要生成独立 Product Truth。
```

### 常规需求 / 一份完整 PRD（兼容名：Standard L2）

```text
使用 AI Delivery Spec Standard L2：盘点我给的材料，批量澄清互不依赖的问题，然后交付一份人类可读且 AI Coding 可直接使用的统一 PRD。所有角色、流程、状态、权限、字段、异常和验收必须闭环，不要拆成两套 PRD。domain=generic
```

### 大型或高风险项目（兼容名：Full L3 smart-large-project）

```text
使用 AI Delivery Spec Full L3 smart-large-project：先完成需求准入和全量 REQ/角色/流程/页面/字段/验收索引，再按切片持续写入同一份统一 PRD；仅在多文档、持续变更或强审计需要时生成分片 Product Truth。domain=traffic
```

一句话 Idea 或竞品参考场景，可在上述指令后补充：

```text
先按依赖层分批澄清；第三批前给出2—3个有取舍的方案。竞品只作为带版本和边界的 SRC 证据，先确认定位 DEC，再写用户故事、页面、原型和 PRD。
```

首选修正：`delivery_shape=requirement_card|unified_prd|governed_truth assurance_profile=bounded|standard|high_risk|safety_critical domain=<pack>`；旧 `mode/tier` 仍兼容。`--level auto` 对 PRD 读取 frontmatter，对原型/handoff 默认 L2；需要逐动作交付时显式使用 L3。
黄金入门示例见 [examples/minimal-v5](examples/minimal-v5/README.md)。

## 第一次使用，你会拿到什么 / What You Get

- **Intake First｜先准入**：目标、价值、范围、责任和未知项不足时先批量澄清，不用长 PRD 掩盖决策空洞。
- **One Shared Baseline｜一份基线**：旅程、页面、字段、规则、状态、异常、接口和验收用稳定 ID 绑定。
- **Prototype When Needed｜按需原型**：存量先做 Stage 0；L3 复杂页有 `REG-*`，每个动作以浏览器 `ARUN-*` 闭环。
- **Lightweight Gate｜轻门禁**：区分已静态证明与仍需领域、浏览器或客户证明的内容。

## 常见的第一次疑问

**这个 Skill 重吗？** 不固定重：可逆小改动走 Ultra-Light，常规需求走 Standard L2，只有规模/审计阈值才加载分片真相。

**每次都要 Product Truth YAML 吗？** 不要。普通项目以一份统一 PRD 为基线，避免长上下文工具被巨型 YAML 拖慢。

**PRD 能交给开发/Coding Agent 吗？** 合同与门禁闭环后可作同一基线；未确认的法规、客户决定和领域规则仍必须标为未知。

**会替代产品、架构、测试或甲方吗？** 不会；范围、技术方案、专业判断和最终签署仍由相应责任人完成。

## 出错或中断：三分钟恢复
校验失败先解释第一个错误码，修复对应契约，再复制门禁输出的 RETRY 原命令：

    python scripts/ai_delivery_spec_cli.py explain-finding PRD-STRUCTURE
大项目或 Product Truth 中断时，恢复最后有效检查点，不要让 Agent 从头重写：

    python scripts/ai_delivery_spec_cli.py resume

命令自动选择最近快照，也可用 `--state` 指定；中断后只继续该阶段/ID 切片。
集中 FAQ、常见错误与反模式见[排障与恢复](references/troubleshooting.md)。
校验器仍然只定位问题，不替用户发明角色、规则、限值或验收结论。

## 只管六件事 / Six Requirement Capabilities

| 能力 | 解决的问题 | 核心产物 |
|---|---|---|
| Intake｜需求准入 | 过滤低价值、边界不清或错配等级的需求 | `REQ-*`、价值/复杂度/优先级、准入结论 |
| Clarification｜需求澄清 | 从模糊 Idea 到可判定业务规则 | 来源、问题批次、`REV-*`、关闭证据 |
| Specification｜规格交付 | 全角色共用口径且传统开发可读 | 一份统一 PRD + 同文档工程附录 |
| Change Control｜需求变更 | 防止口头变更和漏改 | `CHG-*`、影响分析、diff、审批、同步、回归 |
| Traceability｜双向追溯 | 从需求追到页面/字段/AC，也可从缺陷反查 | 正向/反向稳定 ID 账本、审计日志 |
| Acceptance｜需求验收 | 不止定义 AC，还记录执行结果 | `ARUN-*`、证据、缺陷、条件、签署结论 |

研发排期、Sprint/任务、代码、CI/CD、部署执行、监控和运营属于下游系统。
本项目只记录它们与需求/验收有关的外部引用，不接管流程。

## 5.3.2 — User-Language PRDs, Module-Complete Delivery

5.3.2 保留轻量内核，重点解决“中文需求产出英文文档”“读者需要跨章拼规格”和“数据上报被误判为轻量需求”。

因此本版不是增加一套模式，而是收敛成以下合同：

1. **Silent Dual-Axis Triage｜静默双轴分诊**：内部选择需求卡/统一 PRD/受治理真相和风险强度，用户不必先学模式名。
2. **Product Truth on Demand｜严格按需**：受控多投影、反复跨模块变更、血缘或强审计才启用；数量大不是充分条件。
3. **Brownfield Stage 0｜存量反向盘点**：现有 PRD/原型先逐项标记来源与 `confirmed/inferred/unknown/defect_candidate`，再允许覆盖式重写。
4. **Composable Page Contract｜复合页面合同**：按 `primary + layout + surfaces` 组合指标、列表、表单、预览、组装器，只校验适用表面。
5. **Stage-Aware P0 Blocking｜分阶段 P0 阻断**：只阻断已到达阶段和受影响切片，门禁返回独立退出码 3。
6. **Agent Handoff Projection｜Agent 交接投影**：可选生成根/模块 `AGENTS.md` 与 `MOD/XCT/EDGE/HANDOFF` 包，绑定基线 hash、责任人、AC 和 QA 投影。
7. **Governed Learning｜受治理知识回流**：默认关闭、本地、无网络、`project_only`；公共晋升必须独立审批。
8. **Zero-LLM Quality Gate｜轻量门禁内核**：零模型、单遍读取，默认只给第一个可修问题与摘要；传统校验入口只是薄适配。
9. **Honest Static PASS｜诚实通过边界**：门禁始终输出 `not_proven`；动态拼接 `data-'+'action`、运行时补挂动作锚点会阻断，不能再用不可枚举交互换取假 PASS。
10. **Reverse Mapping｜反推不再另造基线**：已有正向 PRD 时，原型观察使用 `INV-*` 映射 `REQ-*`；推断项进入有责任人的 `RBATCH-*` 后批量确认。
11. **Local Private Extensions｜本地私有扩展**：`custom/` 默认不提交，可叠加团队领域包、继承式 PRD 模板和声明式校验；绑定规则冲突必须 `DEC-CONFLICT-*`，禁止静默覆盖。
12. **Decision-Tree Clarification｜决策树澄清**：事实问题按依赖批量，审美/路线/冲突逐项确认；每问给推荐、证据和取舍，无人场不得静默默认。
13. **Evidence-Bound Prototype｜证据化原型**：L3 复杂页强制 `REG-*`；缺少覆盖 `data-ac` 的浏览器 `ARUN-*` 时返回缺口，不再把静态通过包装成完成。
14. **User-Language Contract｜用户语言契约**：标题、正文、表头、澄清和测试默认跟随当前请求语言；稳定 ID、代码与 API 名保持不变。
15. **Module-Complete Slices｜模块纵切闭环**：目标、旅程、页面/数据、规则/状态、指标、恢复和验收在模块内就近闭环，附录只做索引与精确投影。
16. **Risk-Aware Card Escalation｜需求卡自动升档**：数据上报/统计、批量、审批审计、集成和跨角色流程自动进入统一 PRD；未触发的规格不加载。

## 5 分钟接入自己的项目 / Team Setup in 5 Minutes

不用修改官方 Skill。在目标项目根目录把下面指令交给 Agent；它会创建默认不提交的 `custom/` 和项目需求工作区：

```text
使用 ai-delivery-spec 为当前项目执行五分钟团队接入：
1. 运行 init-custom，保留私有目录；2. 从现有制度、术语、历史 PRD 和已确认案例提炼 my-team 领域包；
3. 只把公司特有章节覆盖进继承式 PRD 模板；4. 增加声明式门禁，不执行私有 Python；
5. 用“官方行业包 + my-team”初始化 requirements，并列出仍需负责人确认的来源冲突和未知项。
```

- `custom/domains/my-team.md`：适用/排除场景、对象、状态、业务不变量、禁止项、来源日期和已知缺口。
- `custom/templates/my-team.md`：仅写公司目录、术语、评审/签认差异，继承官方统一 PRD 主体与工程附录。
- `custom/validators/my-team.yaml`：用 `must_match/must_not_match` 固化团队底线；不得放可执行代码。
- `requirements/`：项目的一份 PRD、登记、变更、验收和切片工作区，不再另造公司版/AI版两套基线。

```powershell
$ADS="<安装后的 ai-delivery-spec 目录>"
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" init-custom --output custom
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" init-requirements --output requirements --custom-root custom --template my-team
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" query-domain --domain traffic+my-team --custom-root custom --format yaml
# Agent 完成 PRD 后再运行门禁；骨架初建时出现内容缺口属于正常结果
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" gate --profile prd --prd requirements/PRD.md --level L2 --custom-root custom
```

没有合适官方包时，把 `traffic` 换成自己的行业 ID；先标来源、适用边界和未知项，不能把模型常识当公司规则。五分钟完成的是骨架和接入，不是五分钟证明领域正确；绑定规则冲突必须登记 `DEC-CONFLICT-*`，最终仍由责任人确认。

## 跨行业质量保障，而不是每项目多 Agent 税

v5.x 的发布保障组合覆盖制造、医疗、金融保险、能源、零售电商、数字政府、
建筑工程七类需求物理，以及既有交通、CRM、教育、数据产品和 AI Native 组合。
每个场景贯穿准入、澄清、规格、评审、基线、变更、验收，并由业务、产品、领域、
UX/原型、研发架构、测试验收、合规安全、客户验收八个镜头检查统一 PRD、工程原型
和机器验收。详见 [保障实验室](maintainer/README.md) 与
[行业组合](maintainer/evals/industry-assurance-portfolio.yaml)。

这套多 Agent 压测只在 Skill、模板、领域包或校验器变化时运行。模拟结果不等于行业
专家确认、客户签署或生产证据；普通项目只承担与自身等级匹配的轻门禁成本。

仅当规模/审计门槛触发时：

```bash
python scripts/ai_delivery_spec_cli.py init-requirements --output requirements --with-product-truth
python scripts/ai_delivery_spec_cli.py trace --truth requirements/truth/compiled/product-truth.yaml --output requirements/traceability.yaml --baseline-version 1.0
python scripts/ai_delivery_spec_cli.py impact --truth requirements/truth/compiled/product-truth.yaml --change requirements/changes/CHG-001.yaml
```

## 一份统一 PRD / One PRD, One Baseline

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
[生命周期与角色责任](references/lifecycle.md)，普通单角色小改动不加载。

## 领域实践与知识包保证分开

| 领域包 | 实践状态 | 可复用包成熟度 | 使用边界 |
|---|---|---|---|
| `traffic` | `production_practiced` | `contract_tested` | 方法已用于上线项目；法规和项目适用性仍需确认 |
| `crm` | `production_practiced` | `contract_tested` | 方法已用于上线项目；复杂商业规则按项目确认 |
| `education-it` | `production_practiced` | `contract_tested` | 方法已用于上线项目；教育形态按项目确认 |
| `data-product` | `production_practiced` | `contract_tested` | 方法已用于上线项目；登记、授权、会计、价格、数据集权利和行业规则按项目确认 |
| `ai-native` | `production_practiced` | `contract_tested` | 方法已用于上线项目；模型与安全治理必须项目评测 |
| `oa` | `knowledge_only` | `contract_tested` | 法规/标准/厂商材料已映射；仍需真实行为和 OA 专家复核 |
| `medical-hospital-it` | `knowledge_only` | `contract_tested` | 不得据此推导临床生产结论 |

`production_practiced` 说明相关方法有真实上线实践；`contract_tested` 只说明来源、
关键不变量和16个轻量契约场景通过确定性回归，不等于真实 Agent 行为、专家审查、
客户验收或生产正确性。成熟度继续按 `behavior_validated → expert_reviewed → audited`
逐领域升级。白皮书、案例、开放平台和 SDK 的证据边界详见
[领域保证规则](maintainer/README.md) 与
[references/domain-coverage.yaml](references/domain-coverage.yaml)。

## 与上下游工具的边界 / Ecosystem Boundary

| 位置 | 工具类型 | 责任 |
|---|---|---|
| 上游 | 产品发现、调研、工作坊 | 发现机会、证据和策略假设 |
| **需求管理内核** | **AI Delivery Spec 5.3.2** | 准入 → 澄清 → 基线 → 变更 → 追溯 → 验收 |
| 下游 | Spec Kit、项目/研发管理工具 | 技术方案、任务、排期和依赖执行 |
| 下游 | Codex、Trae、Cursor、Qoder 等 | 依据已基线需求编码、测试和修改 |
| 外部证据 | CI、测试、发布、监控平台 | 向需求验收回传可引用证据 |

这是职责互补关系，不是未经对照实验的质量排行榜。

## 仓库结构

```text
.github/      GitHub 社区文件与工作流
agents/       Skill UI 元数据，仅保留 openai.yaml
examples/     极简入门示例与运行配置
references/   按阶段加载的规则、领域包、适配和模板
schemas/      用户项目需要的需求、变更、追溯与验收契约
scripts/      用户 CLI、编译、分析和轻量门禁
maintainer/   发布保障实验室：tests/evals/evidence/tools/examples/schemas
```

普通需求运行不得加载 `maintainer/`。维护者资产集中在一个目录，整个 GitHub
仓库同时受 180 文件硬预算约束；第三方平台使用 allowlist 运行包，不携带维护实验室。

## 维护与验证

```bash
python scripts/ai_delivery_spec_cli.py check --keep-going
python maintainer/tools/validators/validate_v5_architecture.py
python maintainer/tests/test_v510_requirement_management.py
python maintainer/tests/test_v510_unified_prd.py
python maintainer/tests/test_v510_semantic_guards.py
python maintainer/tests/test_v510_lightweight_gate.py
python maintainer/tests/test_v510_industry_assurance.py
python maintainer/tests/test_v511_runtime_budget.py
python maintainer/tests/test_v511_domain_assurance.py
python maintainer/tests/test_v515_page_delivery_contract.py
python maintainer/tests/test_v516_ai_applicability.py
python maintainer/tests/test_v530_contracts.py
python maintainer/tools/validators/validate_domain_contracts.py
```

一键生成 Mermaid：

```bash
python scripts/render_mermaid_flow.py --truth product-truth.yaml --output flow.mmd
```

贡献、安全与许可证见 [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)、
[.github/SECURITY.md](.github/SECURITY.md) 和 [LICENSE](LICENSE)。
