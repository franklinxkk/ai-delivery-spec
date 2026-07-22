# 变更、追溯与验收 / Change, Traceability And Acceptance

已基线 `REQ-*`、规则、字段、页面、接口、AC或来源优先级发生变化时加载。变更必须双向遍历；
验收只有实际执行、证据可解析且责任人签署后才闭合。

## 1. 变更申请 / Change Request

建立 `CHG-*` 并记录：提出人、来源/权威、原因/紧迫性、原基线版本、种子 ID、前后行为、
受影响用户/角色、目标基线、审批规则和必要评审人。无法追溯的口头变化返回 clarify，不能直接改 PRD。

## 2. 影响遍历 / Impact Traversal

从每个种子 ID 同时遍历入边和出边，至少检查：

```text
REQ, SRC, ROLE, FLOW, VIEW, REG, ACT, FLD, ENT, RULE, STATE,
API/EVT/INT, AC, TEST, DEFECT, ARUN, EVD, CHG, projection
```

将影响标为 direct、transitive、regression-only 或 no-impact-with-reason。权限/数据范围、历史数据、
兼容、迁移、报表/口径、对账和客户合同分别判断。

```bash
python scripts/analyze_change_impact.py \
  --truth requirements/product-truth.yaml \
  --change requirements/changes/CHG-001.yaml \
  --output requirements/changes/CHG-001-impact.yaml
```

## 3. 差异与版本 / Diff And Version

机器合同记录字段级 before/after，评审者同时获得可读行为差异。旧基线永久保留；已接受变更增加
需求基线版本并链接被替代版本，禁止覆盖历史。

## 4. 审批与同步 / Approval And Synchronization

审批人与权威和影响相匹配：通常包括产品、业务/客户、工程、QA，并在触发时加入数据、安全或合规。
记录结论、时间、条件和证据。批准后更新全部受影响权威/导出，并记录接收者、工件版本、状态和时间；
没有工件版本的群消息不算同步关闭。

## 5. 回归与关闭 / Regression And Closure

更新受影响 AC/测试，执行强制回归，绑定证据和开放缺陷。只有同时满足以下条件才能关闭 `CHG-*`：

- 影响清单没有无法解释的孤立项；
- 必要审批完成；
- 受控工件使用同一新基线；
- 强制回归通过，或责任人批准明确例外；
- 受影响使用方收到带版本更新。

任一条件不满足时保持开放，不能宣传新基线已经生效。

## 6. 评审关闭 / Review Closure

每个 finding 绑定 `REV-*` 和至少一个 `REQ-*`/行为 ID，记录严重度、责任人、处置、结果和证据。
P0/P1必须解决、由有权责任人明确延期，或在基线前报告为 blocker。评审至少覆盖目标/来源/范围、
角色和模块交接、权限/数据/状态/规则、字段/集成/对账、可读性、验收可执行性和追溯。

## 7. 验收定义与执行 / Acceptance Definition And Run

可执行 `AC-*` 声明需求/行为引用、前置条件、角色/数据范围、步骤/输入、预期可见/领域结果、
反向/异常行为和强制证据。

L3/L4基线前，frontmatter 的 `acceptance_plan` 声明责任人、准确范围/规则、通过规则、证据类型和
签署角色。它只是计划，不能冒充已执行。静态 Gate PASS 必须列出未证明项，只有 `ARUN-*` 加真实
证据才能证明执行。

`schemas/acceptance-run.schema.json` 中每个 ARUN 记录基线、环境、执行人、实际结果、证据、缺陷、
残余问题和签署。item 结果为 pass/fail/blocked/not_run；结论为 accepted、
accepted_with_conditions、rejected 或 pending；有条件接受要写条件、责任人和完成标准。

证据引用不能只是任意字符串：

- 本地文件使用 ARUN 所在目录内的相对路径，必须存在且不能目录逃逸；
- 稳定 `EVD-*` 在同一文件的 `evidence_catalog` 中绑定相对路径或 http(s) URL；
- 可选 SHA-256 用于检测证据漂移；
- pass 项和接受结论的每条签署都必须有可解析证据；
- 路径越界、缺文件、哈希漂移、未登记 EVD 或拒绝签署与接受结论冲突都会阻断。

## 8. 反向追溯与证据诚实性 / Reverse Trace And Evidence Honesty

每个失败项或缺陷都验证：

```text
ARUN item / DEFECT → AC → behavior ID → REQ → SRC / CHG
```

断链必须分类为需求缺失、孤立测试、实现缺陷或未登记变更，再决定处置。生成文档、模拟截图、
内嵌 PASS 文本不能证明执行。记录工具/人员、时间、环境、位置和结果；执行或外部签署未完成时
保持 `REVIEW_COMPLETE_WITH_GAPS`。
