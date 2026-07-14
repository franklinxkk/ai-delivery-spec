---
name: ai-delivery-spec
description: Manage product requirements from intake through clarification, specification, baseline, change, traceability, and acceptance. Turn rough ideas, customer materials, prototypes, or approved changes into one human-readable, AI-coding-ready requirement contract with stable IDs and executable acceptance. Use for ToC/ToB/ToG requirement intake, PRDs, multi-role workflow closure, brownfield change, prototype requirements, acceptance, or audit traceability. Excludes sprint/task management, implementation management, CI/CD, production operations, and unrelated code debugging or copy rewriting.
---

# AI Delivery Spec 5.1.0 — Requirement Management Kernel

> 首次使用：先执行需求准入；小需求可走 `mode=ultra_light`。
>
> 切换领域：在指令末尾加 `domain=traffic` 等领域参数。
>
> 默认交付：一份人类可读、开发/测试/AI Coding 共用的统一 PRD。

把需求从入口管到验收闭环。只管理六件事：准入、澄清、规格交付、
变更、追溯、验收。研发排期、任务、代码、部署和运营由下游工具负责；
本 Skill 只记录它们与需求有关的外部状态或证据，不接管其流程。

## 1. 先准入，再写规格

任何正式设计前先给出：

```text
Decision: accept|clarify|defer|reject
Priority: P0|P1|P2|P3
Value: high|medium|low + evidence
Complexity: S|M|L|XL + impact dimensions
Uncertainty: low|medium|high + unresolved questions
Mode/Tier: ultra_light|lite|standard|full + L0|L1|L2|L3|L4
Requirement stage: intake|clarify|specify|review|baseline|change|acceptance|closed
Override: mode=<...>; tier=<...>; domain=generic|<pack>
```

- 价值、复杂度和优先级必须说明证据；没有研发确认时不得伪造人天或成本。
- `Ultra-Light` 仅用于一个可逆页面/文案/字段/规则改动：单主角色、无跨模块
  状态、敏感数据、合规决策、客户验收或存量迁移。
- 多角色流程、存量改造、监管/审计、正式客户验收或完整 PRD 至少用 L2。
- 自动推荐可被手动覆盖；覆盖不得隐藏 P0 安全、合规或合同风险。
- 多需求并行时登记版本归属、依赖、冲突和排序，不直接展开全部重型规格。

运行 `scripts/triage_requirement.py`，或按 `references/requirement-management.md`
和 `schemas/requirement-register.schema.json` 完成准入。未通过准入的需求不得进入
完整规格设计。

## 2. 只加载当前阶段材料

| 当前工作 | 必读 |
|---|---|
| 准入、需求池、六阶段闭环 | `references/requirement-management.md` |
| 材料/原型/旧系统盘点 | `references/discover.md` |
| 主动澄清、歧义扫描、评审问题 | `references/runtime/schema-grill.md` |
| 行为规格与稳定 ID | `references/specify.md` |
| 一份统一 PRD | `references/templates/unified-requirement-prd-template.md` |
| 机器附录最低契约 | `references/runtime/ai-coding-completeness.md` |
| 投影与工程交接 | `references/handoff.md` |
| 变更、影响分析、版本 diff | `references/runtime/change.md` |
| 验收执行、证据与结论 | `references/runtime/verify.md` |
| 可执行原型 | `references/runtime/prototype-testability.md` |
| 最终 PRD/原型轻门禁 | `scripts/quality_gate.py`；只按需读取，不加载额外说明 |
| 大项目/上下文压力 | `references/runtime/context-planning.md` |
| 领域组合 | `references/runtime/composition.md` + 匹配领域包 |
| 复用审批/权限/集成/数量/金额/部分执行/跨聚合等通用模式 | `references/patterns/common-requirement-patterns.yaml` |
| 国产模型/工具 | 匹配的 `agents/domestic/*.md` |
| 修改 Skill/模板/领域包/校验器 | `references/runtime/assurance-lab.md`；仅发布保障，不进入客户项目必经链路 |

一次只加载当前阶段的一至两个引用、零或一个领域包，以及被触发的治理规则。
运行时不要加载 README、历史版本、所有示例或全部领域包。
使用领域包前先读 `references/domain-coverage.yaml`，再加载匹配领域文件；实践状态
不能替代可复用知识包的保证等级。

## 3. 六阶段需求闭环

```text
Intake 准入 → Clarify 澄清 → Specify/Review 规格与评审
→ Baseline 基线 → Change 变更 → Acceptance 验收 → Closed
```

### 3.1 准入

- 建立 `REQ-*`，记录来源、目标结果、价值证据、复杂度带、优先级、版本归属、
  依赖、负责人和准入结论。
- 区分需求优先级与事故/安全等级；不能用“领导要求”代替价值和边界说明。

### 3.2 澄清

- 依次闭合用户/角色、触发场景、业务结果、主流程、权限/数据范围、状态、
  规则、异常、验收与范围外项。
- 识别“支持、灵活、适量、及时、等、默认、可配置”等歧义，并要求可判定阈值。
- 关联 `REV-*` 评审问题、责任人、截止条件和关闭证据；不得把待办伪装成已确认事实。
- 澄清门禁未关闭时，不加载最终 PRD 模板、不生成“最终 PRD/原型”，只交付已知事实、
  P0 未知、禁止推断和下一批决策问题。词面歧义为零不等于角色、状态权威、金额/数量、
  补偿、存量迁移或验收已经闭合。

### 3.3 统一规格交付

- 默认只交付一份统一 PRD：前半部分供业务、产品和传统开发顺序阅读；后半部分
  是字段、状态、接口、事件、追溯和机器 AC 附录，供开发、测试与 Coding Agent 使用。
- 正文先讲目标、范围、角色旅程、模块和业务流程，不让机器表格淹没阅读路径。
- 工程附录必须禁止 AI/研发发明业务规则，但不得把数据库、框架或部署实现写成产品需求，
  除非它们本身是客户/业务契约。
- 复用模式只提供问题、契约、异常和 AC 蓝图；复制后必须绑定项目 `REQ-*` 和证据，
  不得把通用模式当成已确认需求。

### 3.4 变更

- 每个变更按 `schemas/change-package.schema.json` 建立 `CHG-*`：原因、来源、
  原基线、新旧差异、影响、审批、同步和回归。
- 从变更种子双向遍历 `REQ/Page/Field/Rule/API/AC/Test/Defect/Evidence`，禁止只改 PRD 正文。
- 变更未完成影响分析、版本留存、审批和受影响方同步前，不得建立新基线。

### 3.5 双向追溯

- 需求必须能正向追到页面、字段、规则、动作、状态、接口、验收、测试和证据；
  验收失败或缺陷必须能反向定位到原需求和变更。
- 细粒度绑定采用稳定 ID；谁在何时修改了什么以及依据是什么，写入审计记录。
- Product Truth 仅在多文档、多模块长期变更、强审计或大项目时独立生成；普通单文件
  PRD 在附录内维护稳定 ID 索引即可，避免为 YAML 而 YAML。

### 3.6 验收

- `AC-*` 必须拆成可执行项：前置、角色、步骤/输入、可见结果、领域结果、反例、证据。
- `ARUN-*` 记录执行环境、执行人、时间、逐项结果、缺陷、遗留项、签署和结论。
- 只有证据绑定后才能 `accepted`。开发中/待上线等只记录为外部里程碑，
  不是本 Skill 管理的任务状态。

## 4. 统一事实与适用门槛

稳定事实对象：

```text
source/assertion/decision/unknown/conflict/requirement/review/change
role/module/entity/field/flow/view/region/action/state/rule/event/integration
acceptance/test/defect/evidence/projection
```

始终遵守：

- 证据先于结论，区分 verified/inferred/proposed/unknown/conflict。
- 每个主动作有可见结果和领域结果；每个状态变化有守卫、失败、审计与 AC。
- 每个字段有含义、来源、字典、编辑权、敏感性和校验；每条跨模块流有所有权、
  映射、失败/补偿和对账。
- 每个已基线 `REQ-*` 关联来源、行为和验收；延期、拒绝、范围外和未知不得静默丢失。

满足任一条件时使用独立 Product Truth：12+ 页面/模块、40+ 动作、80+ 字段、
5+ 来源、3+ 集成、多份受控投影、持续变更或强审计。否则用统一 PRD 内嵌索引。

大项目不得一次性生成巨型 YAML；按 `00-core + REQ/MOD/FLOW` 分片，逐片校验后
确定性编译。Product Truth 是可选的规模化机制，不是所有需求的前置税。

## 5. 既有原型/系统的 Stage 0

从已有 HTML、应用方案、会议纪要或旧系统生成 PRD 前，先提取：

```text
views, regions, roles, actions/handlers, states, entities/fields,
data actions, metrics, representative data, source conflicts, unresolved gaps
```

建立保留清单并比较新旧视图、动作、处理器、弹窗、角色路径和数据量。未经明确
缩减，不得让新原型的交互覆盖低于可信基线。

## 6. 完整 PRD 的闭合标准

用户要求“完整/最终/直接开发/AI Coding PRD”时：

1. 锁定全量需求、角色、旅程、模块、页面、流程、实体、字段、状态、接口和 P0 AC 索引。
2. 按 `REQ-*` 或模块切片写入统一 PRD；每片完成正文和对应工程附录，禁止最后补契约。
3. 逐角色走通入口、权限、主路径、异常、退出/交接、数据变化和验收结果。
4. 接口必须给出业务级请求/响应、错误、幂等、权限和对账；不替研发指定无业务依据的实现。
5. 运行 L2 完整性、PRD 可读性、追溯、验收和适用领域校验；修复内容，不能降级求 PASS。
6. 交付一份主 PRD。只有下游工具明确需要时，再导出独立 YAML/JSON/测试清单。

不得在只完成目录、一个模块、一个角色、一页原型或一次校验后宣称完成。

## 7. 原型与验收可测试性

```text
data-testid <- VIEW/REG/AC
data-action <- ACT
data-field  <- FLD
data-state  <- state enum
data-api    <- command/API
```

每个 `data-action` 必须有处理器和可见结果。验证 JavaScript 语法、关键角色旅程、
权限、状态/失败路径、代表性数据以及 `.hidden`/`!important` 污染。原型是需求验证载体，
不是需求事实的替代品。

## 8. 门禁与完成状态

1. intake：价值、范围、复杂度、优先级、版本和依赖可判定；
2. clarification：P0 歧义、冲突和评审问题已关闭或明确阻断；
3. specification：角色/流程/页面/动作/状态/字段/异常/AC 闭合且正文可读；
4. baseline：版本、批准人和追溯基线已冻结；
5. change：影响、diff、审批、同步和回归闭合；
6. acceptance：可执行项、结果、缺陷、证据和签署闭合；
7. domain：实践状态与可复用知识包保证等级保持分离。

完成状态仅为 `PASS`、`REVIEW_COMPLETE_WITH_GAPS` 或 `BLOCKED`。文档内写了 PASS
不等于真实执行证据。

最终门禁是守门员，不是作者：零模型调用、零子 Agent、每个输入至多读取一次；只定位
稳定 ID 和违反的契约，不生成或自动修复需求。按产物选择 `requirement|prd|prototype|full`
profile，默认最多输出 20 个问题。静态门禁不能替代关键角色浏览器走查、领域责任人确认
或客户验收证据。

跨行业多 Agent 模拟只在 Skill、共用模板、领域包或校验器发生实质变化时运行。它用于
发现方法缺口，不提升领域成熟度，也不冒充专家评审或生产证明。

## 9. 确定性命令

```powershell
py -3 scripts/ai_delivery_spec_cli.py init-requirements --output requirements
py -3 scripts/ai_delivery_spec_cli.py triage --input requirements/intake.yaml --format markdown
py -3 scripts/scan_requirement_ambiguity.py requirements/PRD.md
py -3 scripts/analyze_change_impact.py --truth requirements/product-truth.yaml --change requirements/changes/CHG-001.yaml
py -3 scripts/build_traceability_ledger.py --truth requirements/product-truth.yaml --output requirements/traceability.yaml
py -3 scripts/validators/validate_requirement_register.py requirements/register.yaml
py -3 scripts/validators/validate_acceptance_run.py requirements/acceptance/ARUN-001.yaml
py -3 scripts/validators/validate_prd_quality.py requirements/PRD.md --level L2
py -3 scripts/validators/validate_coding_agent_contract.py requirements/PRD.md --level L2 --profile full_prd
py -3 scripts/ai_delivery_spec_cli.py gate --profile prd --prd requirements/PRD.md --level L2
py -3 scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype prototype.html --level L2
```

非 Windows 环境使用 `python`。

## 10. 最终自检

- 准入结论、价值证据、复杂度、优先级、版本和依赖清晰；
- 已确认材料无静默遗漏，冲突与假设可见；
- 所有角色的入口、权限、主/异常路径、交接和数据结果闭环；
- 统一 PRD 对人可顺序阅读，对研发/测试/AI Coding 不要求发明规则；
- 变更可 diff、可评估、可审批、可同步、可回归；
- 任何 AC/测试/缺陷均能反查 REQ，验收结论有证据；
- 大项目使用分片和检查点，小项目不被 Product Truth 过度治理；
- 未越界接管任务、代码、发布或运营管理。
