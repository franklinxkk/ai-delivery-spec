# Human-First Full PRD Template (v4.9.1 Profile)

Use this profile when the PRD will be reviewed, developed, tested, outsourced,
accepted, or archived by human teams. The document must be readable before it
is machine-readable. Engineering contracts are allowed, but they support the
product specification; they do not replace it.

## Contents

- Heading Hierarchy Lock / 标题层级锁
- 0D Triage And Scope / 0D 分流与范围声明
- Stage 1 Requirement Planning / 阶段一 需求规划
- Stage 2 IA And Prototype Lock / 阶段二 信息架构与原型锁定
- Stage 3 Complete Functional Requirement Records / 阶段三 完整功能需求记录
- Stage 4 Review And Delivery Plan / 阶段四 评审与交付计划
- Stage 5 Test And Acceptance / 阶段五 测试验收
- Stage 6 Launch And Review / 阶段六 上线复盘
- Appendix / 附录
- Gate Completion Statement / Gate 完成声明

## Heading Hierarchy Lock / 标题层级锁

- Use exactly one H1 (`#`) for the document title.
- Use H2 (`##`) for global lifecycle stages or top-level modules.
- Use H3 (`###`) for module subsections and function records.
- Use H4 (`####`) for FRR numbered sections inside one function.
- Do not jump from H2 directly to H4.
- Do not use bold text, table rows, or numbered list items as fake headings.
- In Chinese PRDs, translate headings but keep the hierarchy unchanged.

## 0D Triage And Scope / 0D 分流与范围声明

```text
[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false]
Mode: Lite | Standard | Full
PRD Profile: Human-First Full PRD
Lifecycle Stage: Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire
```

### 源证据登记册 (Source Evidence Register)

| Source ID | Artifact | Locator | Type | Authority | Target Module | Disposition | Assertion Status |
|---|---|---|---|---|---|---|---|
| SRC-001 | {file/path} | {page/sheet/view} | screenshot/prototype/prd/excel/sql/policy/interview | authoritative/supporting/historical | Mxx | EMBEDDED/ANNEX/DEFERRED/CONFLICT | VERIFIED/INFERRED/PROPOSED/UNKNOWN |

Rules:

- Every important claim must trace to a source, an inference, or an explicit
  open question.
- Do not write "see prototype" without `view_id`, `region_id`, `data-testid`,
  `data-action`, screenshot page, or module/function ID.

## Stage 1 Requirement Planning / 阶段一 需求规划

### 1.1 项目背景与业务目标

Write 1-2 short paragraphs explaining the business scene, pain, and expected
outcome. Avoid abstract phrases such as "improve efficiency" unless the
behavior and measurement are stated.

| Goal ID | Goal | Measurement | Priority |
|---|---|---|---|
| BO-01 | {business outcome} | {metric or review signal} | P0/P1/P2 |

### 1.2 角色、职责与使用场景

| Role ID | Role | Responsibility | System Goal | Typical Scenario | Pain Point |
|---|---|---|---|---|---|
| ROLE-001 | {name} | {responsibility} | {goal} | {when/where} | {pain} |

### 1.3 核心用户旅程与业务场景

| Scenario ID | Role | When / Trigger | Goal | Main Action | Success Result | Exception To Watch |
|---|---|---|---|---|---|---|
| SC-M01-01 | {role} | {trigger} | {goal} | {action} | visible result + domain result | {exception} |

### 1.4 竞品/替代方案、价值评估与优先级

Use this section when the requirement is not yet fully shaped, when multiple
solutions compete, or when roadmap priority must be justified.

| Alternative | User Job Covered | Strength | Weakness / Gap | What To Learn | What Not To Copy |
|---|---|---|---|---|---|
| competitor / status quo / manual workaround | {job} | {strength} | {gap} | {learning} | {avoid} |

| Option | Target Role | User Value | Business Value | Feasibility | Risk | Evidence | Recommendation |
|---|---|---:|---:|---:|---|---|---|
| {option} | {role} | H/M/L | H/M/L | H/M/L | {risk} | {source} | do/defer/test/reject |

| Candidate | Method | Score / Level | Why Now | Dependency | Release Decision |
|---|---|---|---|---|---|
| {feature} | ICE/RICE/MoSCoW/owner decision | {score} | {reason} | {dependency} | in/out/later |

### 1.5 EARS 需求描述原则

For P0/P1 behavior, include at least one EARS-style statement before detailed
tables.

| Pattern | Sentence Shape | Example Intent |
|---|---|---|
| Event-driven | When {event}, the system shall {response}. | trigger-based behavior |
| State-driven | While {state}, the system shall {response}. | state-dependent buttons/rules |
| Unwanted behavior | If {unwanted condition}, the system shall {mitigation}. | invalid input / overreach / abuse |
| Optional feature | Where {feature/config/permission}, the system shall {response}. | configuration or permission branch |
| Ubiquitous | The system shall {invariant}. | always-on rule |

### 1.6 范围、优先级与不做项

| Module ID | Module | In Scope | Out Of Scope | Priority | Release |
|---|---|---|---|---|---|
| M01 | {module} | {functions} | {exclusions} | P0/P1/P2 | v{version} |

## Stage 2 IA And Prototype Lock / 阶段二 信息架构与原型锁定

### 2.1 信息架构骨架 (IA Skeleton)

| Module ID | View ID | View Name | Platform | Primary Roles | Regions | Primary Actions |
|---|---|---|---|---|---|---|
| M01 | M01-V01 | {view} | web/mobile/miniapp | {roles} | {region_ids} | {action_ids} |

### 2.2 页面布局与区域说明

| Layout ID | View ID | Region ID | Region Name | Position | Main Components | Visible States | Notes |
|---|---|---|---|---|---|---|---|
| LAY-M01-V01-R01 | M01-V01 | region-filter | {name} | top/left/main/right/bottom/modal/drawer | {components} | empty/loading/error/success/disabled | {notes} |

Rules:

- `Layout ID` format: `LAY-{view_id}-{RNN|MNN|DNN|PNN}`.
- Keep `Layout ID`, `view_id`, `region_id`, and `data-testid` stable after
  assignment.
- If an IA Skeleton is locked, reference its `region_id` instead of rewriting
  the same region definitions in multiple places.

### 2.3 原型锁定记录

| Artifact | Path / URL | Lock Status | Evidence Scope | Owner |
|---|---|---|---|---|
| Prototype | {path} | locked / draft | views/actions/modals/states/mock data | {owner} |

## Stage 3 Complete Functional Requirement Records / 阶段三 完整功能需求记录

Repeat one complete FRR for every in-scope function. A module is not complete
until all its functions have complete records.

### Mxx-Fxx {功能名称}

Every in-scope function must contain all 16 FRR sections. If a section does not
apply, write `N/A + reason`; do not leave it blank or write only "see prototype",
"same as above", or "existing logic".

#### §1 Business Scenario / 业务场景

Use `who / when / why / what / result` to describe the concrete scene. State
the visible user result and the domain/business result.

#### §2 Roles And Scenario / 角色与场景

| Role | Responsibility In This Function | Start Condition | Success Exit | Next Action |
|---|---|---|---|---|
| {role} | {responsibility} | {trigger/state} | {visible + domain result} | {next step} |

#### §3 Entry And Preconditions / 入口与前置条件

| Item | Requirement |
|---|---|
| Entry | {menu/button/link/API/notification} |
| Preconditions | {role/data/state/config/time/dependency} |
| Blocked Entry Handling | {disabled/hidden/error/redirect/audit} |
| Upstream Dependency | {source module/event/data} |

#### §4 Pages, Regions, And Visible States / 页面布局与可见状态

Reference `Layout ID`, `view_id`, `region_id`, `data-testid`, table columns,
form fields, modal/drawer chain, responsive differences, and empty/loading/error
/success/disabled states. State how the page looks and behaves, not only which
data exists.

#### §5 Fields, Dictionaries, And Validation / 字段、字典与校验

| Field ID | Field Name | Type | Required | Dictionary / Enum | Validation | Default | Editable By |
|---|---|---|---|---|---|---|---|
| FLD-Mxx-Fxx-001 | {field} | string/date/number/enum/file | Y/N | {dict} | {rule} | {value} | {role} |

#### §6 Numbered Interaction Flow / 编号交互流程

| Step | Actor | Action / data-action | Frontend Feedback | Backend Rule | Domain Result | Failure Branch |
|---|---|---|---|---|---|---|
| 1 | {role} | {data-action} | toast/modal/loading/disabled | {validation/transaction} | {state/event/audit} | {error/retry} |

#### §7 Actions And Operation Rules / 操作矩阵

| Action | Allowed Role | Allowed State | Confirmation | Idempotency | Visible Result | Domain Result |
|---|---|---|---|---|---|---|
| {action} | {role} | {state} | none/modal/second-confirm | yes/no/key | {ui result} | {data/state/event} |

#### §8 Business Rules, Calculations, And Calibers / 业务规则与计算口径

Describe source of truth, create/update/delete rules, synchronization,
calculation, threshold/caliber, conflict handling, audit logging, and
upstream/downstream impact. Number every rule as `BR-Mxx-Fxx-NN`.

#### §9 State, Button, And Lifecycle Behavior / 状态、按钮与生命周期

| Current State | Visible Actions | Forbidden Actions | Guard | Next State | Event / Audit |
|---|---|---|---|---|---|
| {state} | {actions} | {actions} | {role/data/time/config} | {state} | {event/audit} |

#### §10 Permissions And Data Scope / 权限与数据范围

| Role | Function Permission | Data Scope | Field / Action Restriction | Overreach Handling |
|---|---|---|---|---|
| {role} | view/create/update/delete/approve/export | self/department/specified/all/custom | {restriction} | block/mask/escalate/audit |

#### §11 Exceptions, Fallback, And Recovery / 异常、降级与恢复

| Category | Required Behavior |
|---|---|
| Empty / loading / error | {visible feedback + retry/preserve rule} |
| Input boundary | {required/format/length/duplicate/cross-field} |
| Permission | {vertical/horizontal overreach behavior} |
| State conflict | {repeat submit/stale data/deleted/locked} |
| Network / dependency | {timeout/offline/partial success/retry} |

#### §12 Notifications, Audit, And Dependencies / 通知、审计与依赖

| Trigger | Recipient / Dependency | Channel / Interface | Payload / Content | Failure Handling | Audit Owner |
|---|---|---|---|---|---|
| {trigger} | {role/system} | in-app/SMS/API/event/file | {payload} | retry/fallback/manual | {owner} |

#### §13 Data, AI, And Algorithm Contract / 数据、AI 与算法契约

| Contract Type | Required Content |
|---|---|
| Data | source of truth, schema/dictionary, import/export, sync timing, consistency owner |
| AI / Algorithm | deterministic vs model responsibility, input/output schema, confidence, human gate, fallback, evaluation |
| Prohibited Write | fields/states/actions AI or automation must not modify |

#### §14 Function-Level NFR / 功能级非功能要求

| Category | Requirement | Measurement |
|---|---|---|
| Performance | {latency / batch size / concurrency} | {threshold or proposed} |
| Security / Privacy | {masking / audit / permission} | {check method} |
| Compatibility | {browser/device/surface} | {scope} |
| Operations | {monitoring/retry/rollback/support} | {evidence} |

#### §15 Frontend / Backend / QA Handoff Notes / 前后端与 QA 交接

| Reader | Must Know |
|---|---|
| Frontend | layout, component states, `data-testid`, `data-action`, client validation |
| Backend | permissions, state transition, transaction, idempotency, audit, dependency |
| Algorithm / AI | data source, schema, prompt/rule/model responsibility, eval/fallback |
| QA | happy path, boundary, permission, state conflict, weak network, regression |

#### §16 Acceptance And Traceability / 验收标准与追溯

| AC ID | Given | When | Then | Test Type | Priority | Source / Prototype |
|---|---|---|---|---|---|---|
| AC-Mxx-Fxx-001 | {precondition} | {action} | {observable result + domain result} | unit/integration/e2e/manual | P0/P1/P2 | SRC-... / data-action |

## Stage 4 Review And Delivery Plan / 阶段四 评审与交付计划

| Reviewer | Focus | Result | Blocking Gaps |
|---|---|---|---|
| PM | scope, scenario, priority | PASS/REVIEW_WITH_GAPS/BLOCKED | {gaps} |
| Frontend | page/layout/interaction | PASS/REVIEW_WITH_GAPS/BLOCKED | {gaps} |
| Backend | rule/data/state/API | PASS/REVIEW_WITH_GAPS/BLOCKED | {gaps} |
| QA | acceptance/testability | PASS/REVIEW_WITH_GAPS/BLOCKED | {gaps} |

### 4.1 任务拆解（WBS）/ Sprint Task Breakdown

| Task ID | Task Name | Module / FRR | AC IDs | Est. Hours | Owner | Depends On | Sprint |
|---|---|---|---|---:|---|---|---|
| S1-T01 | {task} | Mxx-Fxx | AC-... | {hours} | FE/BE/QA/Algorithm/PM | none / Sx-Txx | Sprint 1 |

Rules:

- Group tasks by sprint or milestone: core skeleton, business expansion,
  integration, acceptance hardening, launch.
- Every implementation task must reference FRR ID and AC ID unless it is an
  explicit technical enabling task.
- Mark critical-path dependencies and parallelizable work.

### 4.2 风险登记册 / Risk Register

| Risk ID | Description | Probability | Impact | Level | Mitigation | Owner |
|---|---|---|---|---|---|---|
| RISK-001 | {risk} | H/M/L | H/M/L | red/yellow/green | {mitigation} | {role} |

Level rule: H×H = red and blocks release; H×M or M×H = yellow and must be
resolved or explicitly accepted before launch; others may enter backlog.

### 4.3 关键依赖项 / Key Dependencies

| Dep ID | Dependency | Provider | Delivery Date | Blocks Module | Risk Level |
|---|---|---|---|---|---|
| DEP-001 | {dependency content} | {provider} | Sprint X Week Y | Mxx | H/M/L |

### 4.4 研发跟进、风险与阻塞

| Item ID | Type | Source FRR / AC | Owner | Status | Risk / Blocker | Next Action | Due / Reminder | Decision Owner |
|---|---|---|---|---|---|---|---|---|
| TRK-001 | task/risk/blocker/change/decision | Mxx-Fxx / AC-... | PM/RD/QA/Design/Ops | open/in_progress/blocked/done | {risk} | {action} | {date} | {owner} |

### 4.5 Bug 管理与验收缺陷

| Bug ID | Severity | Source AC / View | Reproduction | Expected | Actual | Owner | Fix Version | Regression Evidence |
|---|---|---|---|---|---|---|---|---|
| BUG-001 | S0/S1/S2/S3 | AC-... / Mxx-Vxx | {steps} | {expected} | {actual} | {owner} | {version} | {test/screenshot} |

Severity rule: S0 blocks release; S1 blocks core lifecycle launch unless a human
overrule records risk; S2 schedules before or immediately after launch; S3 can
enter backlog.

### 4.6 待确认问题清单 / Open Questions

| Q ID | Question | Impact Scope | Suggested Approach | Decision Owner | Due Date |
|---|---|---|---|---|---|
| Q-001 | {question} | Mxx-Fxx / AC-... | {recommendation} | {owner} | {date} |

## Stage 5 Test And Acceptance / 阶段五 测试验收

### §16 验收标准与追溯 (Acceptance And Traceability)

| Function ID | AC IDs | Source IDs | Prototype IDs | Test Evidence | Result |
|---|---|---|---|---|---|
| Mxx-Fxx | AC-Mxx-Fxx-001..00N | SRC-001 | data-testid / data-action | test/report/screenshot | PASS/FAIL |

## Stage 6 Launch And Review / 阶段六 上线复盘

| Item | Content |
|---|---|
| Rollout Scope | pilot / phased / full |
| Readiness Checks | data, permission, operations, rollback, support |
| Post-launch Metrics | adoption, conversion, failure, SLA, satisfaction |
| Review Decision | continue / iterate / rollback / retire |

### 6.1 上线复盘与功能退役判断

| Review Item | Required Content |
|---|---|
| Outcome review | original goal, actual metric, adoption, failure/incident signal |
| User feedback | target role, evidence, frequency, severity, representative quote |
| Operations review | support tickets, override/rollback, data quality, on-call events |
| Decision | continue / iterate / rollback / retire / observe |
| Owner / next review | accountable owner and next review date |

## Appendix / 附录

Use appendices for source tables, dictionary details, policy excerpts, screenshots,
and long examples. Do not hide core requirements only in appendices.

### Appendix A Glossary / 术语表

| Term | English | Definition |
|---|---|---|
| {术语} | {english} | {definition} |

### Appendix E Decision Records / 决策记录（ADR）

| Decision | Conclusion | Scope | Date |
|---|---|---|---|
| {decision} | {conclusion} | Mxx-Fxx | {date} |

## Gate Completion Statement / Gate 完成声明

```text
Scope: {artifact scope}
Mode / Tier / Profile: {mode} / {tier} / Human-First Full PRD
Triggered gates: {gates}
Artifacts updated: {files}
Verification: {scripts/reviews}
Completion state: PASS | REVIEW_COMPLETE_WITH_GAPS | BLOCKED
```
