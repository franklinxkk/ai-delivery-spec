# Stage Workstations｜需求阶段工作站（5.4）

本页只在用户要从特定阶段进入、停止、交接或续跑时加载。它不是另一条瀑布流程：使用者可以从任何有证据的工作站进入，并在目标产物完成后离开。

## 1. 两层模型

- `frame`、`explore` 是准入前工作区，用于把问题和选项想明白；不创建正式 `REQ-*`，不把假设伪装成需求。
- `intake → clarify → specify → review → baseline → change/acceptance` 是受治理的正式需求生命周期；`REQ-*` 从 intake 开始。
- baseline 不是第二份文档，而是“统一 PRD/需求卡 + 评审结论 + 权威来源 + 版本/hash”的受控状态。
- change 与 acceptance 可以多次发生，但必须回链当前基线；研发任务、代码、部署和运营不属于本 Skill。验收结论交给外部交付/发布工具，线上反馈只作为新 `SRC-*` 回到 intake 或已基线 `CHG-*`，不在本 Skill 内追踪上线状态。

```text
问题定义(frame) → 方案探索(explore) → 准入(intake) → 澄清(clarify)
→ 规格(specify) → 评审(review) → 基线(baseline) ↔ 变更(change)
                                              └→ 验收(acceptance) → 外部发布/交付引用
                                                                  └→ 新 SRC → intake/CHG
```

## 2. 语义路由，不用关键词猜意图

按以下优先级确定 `entry_stage` 和 `target_stage`：

1. 用户明确指定的目标产物/停止点最高优先；“不要写 PRD，只做澄清”等否定约束高于“PRD”关键词。
2. 已有产物决定可续接位置，但不能强迫用户重跑已完成阶段；先核对版本、来源和 hash 漂移。
3. 未明确目标时，选择能解决当前问题的最小产物，并继续执行可逆工作；只有不同选择会实质改变交付范围时才询问。
4. 单次明确任务在目标阶段停止；用户明确要求端到端交付时持续到目标，不把中间模板或一次静态 PASS 当成完成。
5. `route-stage` 只检查显式目标、已有产物和确定性前置条件，绝不解析自然语言关键词：

```bash
python scripts/ai_delivery_spec_cli.py route-stage --target clarify --artifact requirements/problem-brief.md
```

## 3. 九个工作站与最小产物

| 工作站 | 适用问题 | 默认最小产物 | 出口条件 | 对应轻门禁 |
|---|---|---|---|---|
| frame | 到底是谁在何时遇到什么问题 | 一份 `problem-brief.md` | 用户/痛点时刻/成功信号/事实与假设可区分 | `gate --profile frame` |
| explore | 应该做什么，是否有更小方案 | 一份 `solution-sketch.md`，假设内嵌 | 至少两个方案+不做选项；有最小验证与停止条件 | `gate --profile explore` |
| intake | 是否值得进入正式设计、用多重规格 | `intake.yaml` + requirement register | `REQ-*`、价值、复杂度档位、依赖、优先级、迭代归属、交付形态 | intake schema + `triage` + requirement gate |
| clarify | 规则、边界、角色和异常是否已决 | 一份 `requirement-brief.md`；复杂审计可用 Discovery Contract | 决策有依据；P0/P1 未知项有责任人、阻断阶段和退路 | `gate --profile clarify` |
| specify | 人与 Agent 是否能实现同一口径 | 一份需求卡或统一 PRD | 适用模块纵切闭环；横切合同和机器附录就近可查 | `gate --profile prd` |
| review | 各责任角色是否签署或提出缺口 | `review-record.yaml` | P0/P1 发现关闭；`required_review_types` 均有结构化签署 | `validate_review_record.py` |
| baseline | 哪个版本是唯一权威 | 同一规格 + review/authority/version/hash 元数据 | 权威来源、开放未知项、版本和消费方同步清楚 | `gate --profile prd --stage baseline` |
| change | 改动影响了谁、什么字段/规则/AC | `change-package.yaml` | diff、双向影响、审批、同步、回归和版本闭合 | change validator / impact |
| acceptance | 需求结果是否真的被执行验证 | `ARUN-*.yaml` | 正反用例、证据、遗留问题、条件和签署回链 | acceptance validator / gate |

假设只有在跨会话、跨角色复用或需要治理时才拆为 `assumption-register.yaml`；普通探索写在方案草图中。澄清决策默认写入需求简报，只有多决策人、审计或跨需求复用时才拆侧车记录。不要为“九阶段”机械生成九个文件。

## 4. Skill 使用者角色在各工作站如何进入和离开

| 角色 | 常见进入点 | 读取/贡献 | 可独立决定 | 必须交接 |
|---|---|---|---|---|
| 业务/客户 | frame、clarify、review、acceptance | 痛点、业务事实、权威口径、签署结果 | 自身业务目标与授权范围内的规则 | 合同、法规、跨组织冲突给对应责任人 |
| 产品 | 任意工作站 | 问题、选项、准入、统一规格、变更影响 | 可逆产品取舍和文档组织 | 超授权业务/法律/技术约束 |
| UX/设计 | explore、clarify、specify、review | 用户路径、信息架构、页面状态、可用性证据 | 交互方案选项 | 业务规则和品牌方向签署 |
| 前端 | clarify、specify、review | 页面/区域/控件/字段/动作/状态/异常/锚点 | 可实现性建议 | 不得发明业务规则、权限或验收口径 |
| 后端 | clarify、specify、review | 数据流、状态流、规则、幂等、接口/事件和恢复 | 可实现性与技术约束 | 不得改变业务语义与客户边界 |
| 架构师 | explore、specify、review、change | 跨系统边界、NFR、兼容、迁移、失败语义 | 架构约束与风险意见 | 需求范围和验收由业务/产品负责 |
| 需求交付/技术负责人 | intake、review、baseline、change | 复杂度带、跨团队依赖、工程就绪、评审角色和外部交付引用 | 工程可行性、容量约束证据与交接建议 | 不替代业务优先级，不在 Skill 内分配人员/Sprint/工期 |
| QA/测试 | clarify、specify、review、acceptance | 正反例、边界、可观测证据、缺陷回链 | 测试设计与结果 | 条件验收需产品/客户签署 |
| 合规/安全 | frame、clarify、review、change | 适用法规、数据权限、审计和禁止项 | 专业责任范围内结论 | 法源适用性不由 Agent 代签 |
| Coding Agent | baseline 后消费 | 稳定 ID、纵切规格、横切合同、禁止推断、AC | 只在既定合同内实现 | 缺失语义必须回报 GAP，不得猜测 |

这里的“Skill 使用者角色”指参与需求工作的业务、产品、设计、研发和测试人员；PRD 内的 `ROLE-*` 指系统中的业务角色，两者不能混用。每次交接只传：当前主产物、变更/评审侧车、开放 `UNK/ASM`、权威来源、目标阶段和可验证的 SHA-256；不要把整个仓库或全部领域包塞入上下文。

## 5. 阶段门禁语义

所有门禁只使用一套状态：

- `PASS`：被检查的静态合同无已知缺口；仍不证明业务、运行时或客户验收。
- `REVIEW_COMPLETE_WITH_GAPS`：可继续探索/评审，但必须保留发现；不能伪装成已基线。
- `BLOCKED_BY_P0_UNKNOWN`：当前目标阶段被 P0 未知项阻断；可返回、缩范围或由责任人关闭。
- `BLOCKED`：结构、依赖、漂移或必需输入无效。

frame/explore 的未证实假设通常是 GAP，不是 P0 阻断；澄清必须通过 `assumption_refs/assumption_resolutions` 将上游 `ASM-*` 承接、转为 `UNK-*` 或关闭。开放 P0 只有在当前阶段到达其 `blocks_stage` 时才阻断，提前阶段保持可见 GAP。静态门禁是守门员，不是领域专家、浏览器、测试执行器或客户签字。

## 6. 断点与按需加载

5.4 模板的 `resume_context.prior_artifacts` 每项使用相对路径、阶段和 SHA-256。`stage_contract.py` 会拒绝目录越界、缺失文件和 hash 漂移。大项目仍使用 `manage_execution_state.py` 保存 ID 切片、读取预算和检查点；产物级 resume 与执行级 checkpoint 互补，不能互相替代。

- frame/explore：通常不加载领域包；只有法规、安全或行业物理约束会改变选项时加载一个精确章节。
- intake 以后：只加载当前阶段参考 + 一个精确领域章节 + 当前 ID 切片。
- 普通单角色任务：不加载本页之外的 maintainer、全模板、全示例或全部领域资产。
