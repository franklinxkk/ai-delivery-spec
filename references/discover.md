# 发现与澄清 / Discover And Clarify

输入是一句话想法、客户要求、会议纪要、旧系统、原型，或缺少专用领域包时加载。先完成准入；
当目标、范围、证据、权威和 P0 未知项足以决定交付形态时停止，不把发现阶段无限延长。

## 目录 / Contents

- 先取证再提问
- 风险自适应澄清
- 一句话与竞品路径
- 存量系统三角盘点
- ToB/ToG 上下文和项目领域胶囊
- 澄清完成与定向追问

## 先取证再提问 / Evidence Before Questions

先盘点用户已经提供的材料。每个来源登记为 `SRC-*`，并声明：binding、supporting、
contextual、historical 或 untrusted；同时记录状态、范围、解释责任人和位置。若同一范围有多个
canonical 候选，停止并创建 `DEC-CONFLICT-*`，不能按文件名、时间或详细程度擅自选择。

尽可能提取：

- 角色、组织、租户、合作方、客户和数据范围；
- 业务对象、字段、字典、状态、动作与事件；
- 页面、区域、弹窗、处理器、报表、导入导出和集成；
- 合同、政策、标准、验收、迁移和运行证据；
- 矛盾、过期主张、隐式遗漏和未裁决问题。

来源处置与断言状态相互独立，断言使用：

```text
verified | inferred | proposed | unknown | conflict
```

材料已经回答的问题不要再让用户重复回答。

## 风险自适应澄清 / Risk-Adaptive Clarification

有依赖的问题按顺序问；互不依赖的问题按目标、角色权限、流程状态、数据集成和验收成批问。
用户明确偏好速度时，可以接收 context dump 或 best guess，但所有假设仍要有边界和责任人。
追问深度由风险决定，不使用固定问卷。

| 信号 | 必须澄清 |
|---|---|
| 原始想法 | 目标角色、痛苦时刻、期望结果、当前替代方式 |
| 已提出功能 | 根问题、成功指标、更小方案、禁止行为 |
| 多角色/模块 | 责任归属、跨模块流程、状态/异常责任人 |
| 金钱/安全/医疗/合规 | 责任人、权威来源、禁止自动化、回退 |
| 存量原型/系统 | 保留、改变、移除、迁移和验收基线 |
| 外部数据/集成 | 权威源、时效、失败、对账、数据责任人 |
| AI读写 | 上下文权限、时效、写入范围、评测、回退、人工闸 |

关键未知项使用可追溯结构，而不是自由文本：

```yaml
unknown:
  id: UNK-001
  question:
  priority: P0 | P1 | P2
  impact: scope | role | state | data | compliance | acceptance | commercial | risk
  question_kind: fact | direction
  owner:
  affected_refs: []
  blocks_stage: clarify | specify | review | baseline | implementation | acceptance
  recommendation:
  recommendation_evidence_refs: []
  tradeoff:
  reversal_path:
  due_date:
  status: open | answered | blocked | accepted_risk
  evidence_refs: []
```

改变范围、合法性、安全、数据权威、商业承诺或验收的未知项属于 P0，禁止静默默认。

### 一句话需求路径 / One-Sentence Requirement Track

不要把口号直接扩成页面。按依赖层推进：

1. 证据、目标角色、痛苦时刻、现有替代和期望结果；
2. 候选方案、最小验证和明确禁止项；
3. 角色责任、主/拒绝/恢复旅程和跨角色交接；
4. 状态、数据权威、集成、迁移、合规和验收；
5. 产品决策稳定后才进入页面/字段/动作细节。

最迟第三批提供2—3个有实质差异的方案和取舍，不把方案设计全部推回给提出者。默认上限：
L1三批、L2六批、L3/L4八批；到达上限后返回剩余 `UNK-*`，不能制造闭合或无限追问。

每批答案必须回绑原 `UNK-*`，并更新受影响的 `DEC/REQ/RULE/AC`。每轮记录推荐、推荐证据、
取舍、受影响 ID 和答案证据。方向问题串行处理，后续轮通过 `branch_ref` 指向前一方向轮。
仅有“1、2、3”回答而没有问题到 ID 的绑定，不构成长期需求证据。

ToC行为改变型想法还要检查目标行为、触发时刻、失败恢复、安全隐私、反操纵边界、试点证据和
停止条件；没有对应风险时不要套入企业级重治理。

### 竞品证据与差异化路径 / Competitive Evidence And Differentiation Track

竞品材料是证据，不是待办清单：

1. 将准确页面、版本/日期和观察行为登记为 `SRC-*`；
2. 分开事实、推断、可复用模式、假设和禁止照搬项；
3. 比较用户结果、工作流成本、切换约束、信任风险与业务适配，不按功能数量排名；
4. 形成2—3个定位/方案选项和最小验证；
5. 先由责任人把定位固化为 `DEC-*`，再写故事、IA、页面合同和原型；
6. 每项差异化都要追到证据、主动决策和可测验收/实验，删除装饰性差异。

白皮书、案例、SDK和开放平台示例只能证明其明确描述的行为，不能证明完整实现、市场效果、
法律适用性或核心产品开源。

## 存量系统三角盘点 / Brownfield Triangulation

声明当前基线前，交叉比对三类证据：已批准需求/变更、可观察原型/系统/数据、工程/QA/运营
实际使用的澄清。历史上能开发出来不等于符合当前合同；口头补充应转为 `SRC/DEC/REV`。

覆盖原工件前，Stage 0 对每个视图、动作/处理器、状态、角色、对象、字段/指标和外部交接建立
记录，至少含 `id`、`type`、`source_ref`、`source_location` 和 classification：
`confirmed`、`inferred`、`unknown` 或 `defect_candidate`。核心未知项绑定 P0 `UNK-*`、owner
和 `blocks_stage`；缺陷候选没有 `DEC/CHG` 不能进入目标范围。

已有正向 PRD 时，反推观察只使用 `INV-*`，不得另造第二组 `REQ-*`。声明
`baseline_requirement_refs`，为 confirmed/inferred 记录 `mapping_status` 和准确 `target_refs`。
未映射核心行为转为 `UNK-*`；推断项按责任人归入 `RBATCH-*`，在 `baseline_ready` 前批量确认、
否决或转未知。反推结果只能是可审计交互草稿和缺口账本。

`inventory_complete` 只证明所有观察项有来源和分类，不批准推断行为，也不证明目标设计：

```bash
python scripts/ai_delivery_spec_cli.py gate --profile stage0 --inventory stage0.yaml
```

## ToB / ToG 项目上下文

仅记录会约束范围、权威、验收或证据的商业、客户、工程和治理上下文，不接管这些外部流程。
政企/国企项目按需把立项、采购、合同、试运行、正式验收和审计登记为来源、约束或验收里程碑。

最低上下文包括：购买方、发起人、最终用户、付款方、验收/运营责任人；组织/部门/租户/
代理商/接入商层级；合同范围和试点成功；存量系统、迁移、培训/SLA及退出责任；辖区、监管、
安全、隐私、档案和审计边界。

## 项目领域胶囊 / Project Domain Capsule

没有专用领域包不阻断交付。用证据和责任人决策建立项目级胶囊：

```yaml
project_domain_capsule:
  vocabulary: []
  entities: []
  state_machines: []
  workflows: []
  policies: []
  source_register: []
  unknowns: []
  scenario_fixtures: []
```

无来源的专业判断标为 inferred 或 unknown。只有经过多项目复用、来源验证、行为评测和独立专家
审查，项目胶囊才可能晋升为公共领域包。

## 澄清完成条件 / Clarification Completion

| 决策 | 含义 |
|---|---|
| `READY_FOR_LIGHT_SPEC` | 有界需求已准入，可以写需求卡 |
| `READY_FOR_UNIFIED_PRD` | 信息足以形成统一 PRD 基线 |
| `READY_FOR_PRODUCT_TRUTH` | 兼容名；多投影/反复变更/血缘/强审计需要 governed truth |
| `READY_FOR_CHANGE_PACKAGE` | 已理解现有基线和变更 |
| `REVIEW_COMPLETE_WITH_GAPS` | 可形成有用结果，但仍有具名未知项 |
| `BLOCKED_BY_P0_UNKNOWN` | 继续会编造实质业务或风险决策 |

准入结论、目标用户、范围、证据、权威、风险、下一工件和决策人都明确后，澄清才完成。

## Schema 驱动的定向澄清 / Schema-Driven Targeted Clarification

取证后仍有未知项时，选择影响最大的开放 `UNK-*`，只问能关闭或拆分它的最小问题，并引用
导致提问的来源或冲突。每个回答写入 `schemas/clarification-transcript.schema.json`：包含
turn_id、unknown_id、问答、责任人、状态、问题类型、推荐及证据、取舍、受影响 ID 和证据；
方向轮还要用 `branch_ref` 指向前一轮。

只编译结构化且有责任人归属的答案；自由对话仍只是来源证据，确定性脚本不能假装理解它。
全部 P0/P1 得到回答/接受，或成为有责任人、范围、阻断阶段和回退路径的 `UNK-*` 后停止。
超过阶段轮次限制时返回未解决 ID，不能继续 propose/reject 死循环。

```bash
python scripts/compile_clarification_transcript.py --contract discovery.yaml --transcript transcript.yaml --decision READY_FOR_PRODUCT_TRUTH --output discovery-next.yaml
```
