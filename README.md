# AI Delivery Spec 5.4.3 — Trigger Reliably, Converge Fast, Deliver a Usable Artifact

> 需求一来就写 PRD，低价值需求也进入重型设计？
>
> PRD 写了几十页，传统开发看不下去，AI Coding 仍在猜规则？
>
> 需求一变，页面、字段、接口、测试和验收漏改，最后无法审计？

**Any Stage In. Right-Sized Artifact Out. One Traceable Requirement Baseline.**
**AI Delivery Spec 是面向 ToB/ToG、兼顾 ToC 的需求管理 Skill。**它不接管研发项目管理，而是把从
需求准入、澄清、定稿、变更、追溯到验收的事实，统一成业务可确认、产研可执行、Coding Agent 不必猜的契约。

默认交付不是两套 PRD，也不是先造一个巨型 YAML，而是**一份统一需求规格说明书**：
正文让客户、产品和传统开发顺序读懂，同文档工程附录让测试与 AI Coding 精确执行。
只有大项目、持续变更、多投影或强审计场景才启用分片 Product Truth。

[![Version](https://img.shields.io/badge/version-5.4.3-0052A4.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/franklinxkk/ai-delivery-spec?style=social)](https://github.com/franklinxkk/ai-delivery-spec)

<!-- CLAIM: CLM-ADOPTION-20260730; as_of=2026-07-30; evidence=public-platform-pages-checked -->
**公开采用信号 / Public Adoption Signals（截至 2026-07-30）**：
[ClawHub 约 1.4k 次下载](https://clawhub.ai/franklinxkk/skills/ai-delivery-spec) · [skills.sh 安装页](https://www.skills.sh/franklinxkk/ai-delivery-spec) ·
[SkillHub 696 次下载、AI 评分 4.8/5.0](https://skillhub.cn/skills/user_12c92261/ai-delivery-spec)。SkillHub 两条安全测评均显示“安全，无风险”；ClawHub 当前安全审计为 `Review`，请结合各平台报告人工复核。
动态数字和评分是作者提供/核对的公开快照，不代表质量排名或项目适用性判断；领域证据边界见 [release-status.yaml](maintainer/evals/evidence/release-status.yaml)。

## 你现在在哪，就从哪里开始 / Start Where You Are

不必先学阶段名、模式或 L0—L4。告诉 Agent **你的角色、已有材料、本次想拿到什么**，Skill 选择最小必要路径：

| 你现在的工作 | 常见角色 | 本次直接得到 |
|---|---|---|
| 只有一句想法、访谈或客户痛点 | 业务、客户、产品 | 问题简报：用户、痛点时刻、证据、成功信号和未知项 |
| 正在比较竞品、方案或交互方向 | 产品、设计、架构师 | 方案草图：至少两个方案、不做选项、取舍和最小验证 |
| 要判断需求是否值得做、放哪个版本 | 产品负责人、需求交付/技术负责人 | 准入结论与需求池聚合：价值、优先级、复杂度档位、依赖和交付形态 |
| 需求还模糊，需要把规则问清楚 | 业务、产品、领域专家 | 澄清简报：范围、决策、业务规则、异常、责任人与待确认项 |
| 要交付开发可实现的需求 | 产品、设计、前后端、架构师、测试 | 一份传统开发可读、Coding Agent 可执行的统一 PRD；按需配工程原型 |
| 已有 PRD/原型，要确认能否开工 | 设计、前后端、架构师、需求交付负责人、测试、合规 | 评审记录：必需评审类型逐项签署，页面、字段、状态、数据流、指标、接口、异常和 AC 缺口闭合 |
| 评审已完成，要锁定唯一开工版本 | 产品负责人、客户、研发、测试、Coding Agent | 需求基线：统一 PRD/需求卡、权威来源、版本与 Hash、开放项和交接范围 |
| 需求已经变化 | 产品、研发、测试、客户 | 变更包：差异、影响范围、审批、同步、回归和新基线 |
| 准备测试或客户验收 | 测试、实施、业务、客户 | 验收记录：正反用例、证据、缺陷、遗留条件和签署结论；发布状态交给外部工具，线上反馈回流新需求/变更 |

**核心承诺：Any Stage In, Right-Sized Artifact Out。**只做当前需要的产物；只有用户明确要求端到端交付时，才继续跑完整闭环。

## 60 秒上手 / Start in 60 Seconds

不必手工克隆仓库。任选与你的 Agent 环境匹配的安装方式：

```bash
# Codex / Claude Code / Cursor / Trae 等 Agent Skills 兼容工具
npx skills add franklinxkk/ai-delivery-spec

# OpenClaw
openclaw skills install @franklinxkk/ai-delivery-spec
```

只用 Agent 完成需求工作，无需先安装 Python。需要运行零模型本地门禁时，再准备 Python 3.10+、PyYAML 与 jsonschema 两个本地依赖：执行 `python -m pip install -r scripts/requirements.txt`；Windows 的 `python` 若是商店占位符，请改用已安装解释器的完整路径或 `py -3`。

安装后不必填写参数，直接用自然语言说明当前位置：

```text
使用 AI Delivery Spec。我是<角色>，已有<材料/系统/原型>，本次只要<目标产物或停止点>。
先复用已确认事实，批量询问互不依赖的关键缺口；未经确认不得猜，完成目标产物并自检后停止。

例：我是后端，已有 PRD，本次只做研发评审；不要重写产品背景。
例：我是产品，只有客户一句话需求，先澄清并交付需求卡；不要直接扩成大型 PRD。
例：我是测试，已有 PRD 和原型，只生成可执行验收项、反例、证据要求和缺口清单。
```

明确说“不要写 PRD，只做澄清”就会停在澄清；显式目标和否定约束高于关键词。需要检查旧产物能否续接时，再运行 `python scripts/ai_delivery_spec_cli.py route-stage --target <阶段> --artifact <产物>`。

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

黄金入门示例见 [examples/minimal-v5](examples/minimal-v5/README.md)。

## 第一次使用，你会拿到什么 / What You Get

- **Intake First｜先准入**：目标、价值、范围、责任和未知项不足时先批量澄清，不用长 PRD 掩盖决策空洞。
- **One Shared Baseline｜一份基线**：旅程、页面、字段、规则、状态、异常、接口和验收用稳定 ID 绑定。
- **Prototype When Needed｜按需原型**：存量先做 Stage 0；L3 复杂页有 `REG-*`，每个动作以浏览器 `ARUN-*` 闭环。
- **Lightweight Gate｜轻门禁**：区分已静态证明与仍需领域、浏览器或客户证明的内容。

第一次只需知道三个词：**Stable ID** 是跨文档不变的需求编号；**Product Truth** 是复杂项目按需启用的事实账本；**Gate** 是零模型静态检查，不等于业务、实现或客户验收通过。

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

## 5.4.3 — Reliable Trigger + Fast Convergence + Visual Lock｜稳定触发、快速收敛与视觉锁

5.4.3 保留 5.4.1 的 Human-First 门禁与九工作站能力，并固化真实项目验证后的四类体验修复：小功能也必须先触发 Skill；明确需求直达结果，模糊需求在首答完成发散、推荐聚焦和关键链深化；存量原型把既有页面作为视觉权威并冻结跨页视觉锁；门禁默认按根因分组，一次显示全部唯一问题码，JSON 仍保留完整明细。阶段是路由地图而非待办清单，实时对话不展示内部 YAML/ID，门禁只在目标里程碑运行；持久化阶段产物仍用 `artifact/stage`、`ADS:*` 和跨会话 `resume_context` 保持兼容。

你会感受到五个变化：

1. **Start Anywhere｜随时进入**：有一句话、会议纪要、原型、旧 PRD 或变更单，都从现状开始，不补跑无关流程。
2. **Stop with a Usable Artifact｜拿到即走**：只交付当前角色需要的问题简报、方案草图、需求卡、统一 PRD、评审、变更或验收记录。
3. **One Shared Baseline｜一份共同基线**：人类正文与机器契约在同一 PRD 中，Product Truth 只在持续变更、多投影或强审计时启用。
4. **Resume without Rework｜安全续接**：跨会话用版本、相对路径和 SHA-256 检查漂移，不让 Agent 从头重写；普通小需求不承担该成本。
5. **Verify without Pretending｜诚实验证**：轻门禁发现结构、追溯和输入问题，同时明确哪些仍需领域专家、浏览器、实现和客户证明。

## 5 分钟接入自己的项目 / Team Setup in 5 Minutes

不用修改官方 Skill。在目标项目根目录把下面指令交给 Agent；个人使用创建整目录不提交的
`custom/`，团队使用则进入受控私有仓库并继续排除敏感证据。

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
# 个人本机：custom/ 整目录默认不提交
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" init-custom --output custom --sharing local
# 团队协作：改用 --sharing team，仅提交到受控私有仓库
# py -3 "$ADS\scripts\ai_delivery_spec_cli.py" init-custom --output custom --sharing team
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" init-requirements --output requirements --custom-root custom --template my-team
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" query-domain --domain traffic+my-team --custom-root custom --format yaml
# Agent 完成 PRD 后再运行门禁；骨架初建时出现内容缺口属于正常结果
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" gate --profile prd --prd requirements/PRD.md --level L2 --custom-root custom
```

没有合适官方包时，把 `traffic` 换成自己的行业 ID；先标来源、适用边界和未知项，不能把模型常识当公司规则。五分钟完成的是骨架和接入，不是五分钟证明领域正确；绑定规则冲突必须登记 `DEC-CONFLICT-*`，最终仍由责任人确认。

团队知识不会因为 Agent 在一个项目里“看起来有效”就自动进入领域包。先在默认不提交的
`custom/learning/candidates/project-local/` 建候选，再对每次真实使用记录结果和证据；至少两个独立项目形成
支持性证据后，工具也只会建议进入组织级人工评审：

```powershell
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" candidate record-usage --candidate custom/learning/candidates/project-local/CAND-EXAMPLE.yaml --usage-id USAGE-MY-TEAM-001 --project project-a --outcome adopted --evidence EVD-ACCEPTANCE-001 --recorded-by domain-owner --output custom/learning/usage/USAGE-MY-TEAM-001.yaml
py -3 "$ADS\scripts\ai_delivery_spec_cli.py" candidate assess --candidate custom/learning/candidates/project-local/CAND-EXAMPLE.yaml --usage custom/learning/usage --format markdown
```

`modified/rejected/invalidated` 同样必须记录，避免只学习成功案例。敏感候选只能留在项目内；
组织/公共范围需要独立审批者、适用/排除边界和受影响领域回归；脱敏确认后才移入
`learning/candidates/review/`。CLI 永不自动移动、晋级或联网外发。

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
python scripts/ai_delivery_spec_cli.py compile-truth --index requirements/truth/index.yaml
python scripts/ai_delivery_spec_cli.py trace --truth requirements/truth/compiled/product-truth.yaml --output requirements/traceability.yaml --baseline-version 1.0
python scripts/ai_delivery_spec_cli.py impact --truth requirements/truth/compiled/product-truth.yaml --change requirements/changes/CHG-CORE-001.yaml
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

## 各级产品、研发与需求交付负责人如何协同

| 使用者 | 独立完成 | 必须升级/交接 |
|---|---|---|
| 初级产品 | 盘点、REQ/REV、旅程/规则/AC 草案 | 范围价值、权威冲突、敏感/监管规则和 P0 未知 |
| 中高级产品 | 准入、澄清、统一 PRD、基线、变更和追溯 | 超出授权的客户、法律、安全和合同决策 |
| 初中级开发/Coding Agent | 实现已基线的稳定 ID 切片并回报歧义 | 缺失角色、状态、权限、规则或接口语义，不得自行发明 |
| 高级开发/架构师 | 可实现性、跨系统状态、接口事件、迁移、恢复和 NFR 设计 | 产品范围、客户验收和领域权威仍由责任人决定 |
| 需求交付/技术负责人 | 汇总优先级、复杂度带、依赖、迭代归属、工程就绪和评审签署 | Skill 不替代 Sprint、人员、工期与容量决策；仅向外部工具交接 |
| 测试/领域/客户 | 反例、领域结果、执行证据和签署 | 静态 PASS 或开发自测不能替代其责任 |

多角色或正式交接时才读取
[生命周期与角色责任](references/lifecycle.md)，普通单角色小改动不加载。需求交付负责人可用
`python scripts/validators/validate_requirement_register.py requirements/register.yaml --summary`
得到零模型需求池视图；它不做自动排期。

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
| **需求管理内核** | **AI Delivery Spec 5.4.3** | 问题/方案 → 准入 → 澄清 → 基线 → 变更 → 验收 |
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

普通需求运行不得加载 `maintainer/`。维护实验室同时受 ≤56 文件、≤450 KB 和默认快速检查 ≤12 条命令约束；
完整发布检查只在候选版本运行。第三方平台使用 allowlist 运行包，不携带维护实验室。

## 维护与验证

```bash
python scripts/ai_delivery_spec_cli.py check
python scripts/ai_delivery_spec_cli.py check --profile release --keep-going
python scripts/render_mermaid_flow.py --truth product-truth.yaml --output flow.mmd
```

完整发布测试、领域检查与证据边界见[保障实验室](maintainer/README.md)。

贡献、安全与许可证见 [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)、
[.github/SECURITY.md](.github/SECURITY.md) 和 [LICENSE](LICENSE)。
