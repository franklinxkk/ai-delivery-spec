# Human-First Full PRD Template (v4.7.3 Profile)

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

### 1.4 范围、优先级与不做项

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

#### §1 Business Scenario / 业务场景

Use `who / when / why / what / result` to describe the concrete scene.

#### §2 Entry And Permission / 入口与权限

| Item | Requirement |
|---|---|
| Entry | {menu/button/link/API/notification} |
| Allowed Roles | {roles} |
| Data Scope | self/department/specified/all/custom |
| Overreach Handling | block/mask/escalate/audit |

#### §3 Page And Layout / 页面与布局

Reference `Layout ID`, `view_id`, `region_id`, table columns, form fields,
modal/drawer chain, and responsive differences. State how the page looks and
behaves, not only which data exists.

#### §4 Field, Validation, And Dictionary / 字段、校验与字典

| Field ID | Field Name | Type | Required | Dictionary / Enum | Validation | Default | Editable By |
|---|---|---|---|---|---|---|---|
| FLD-Mxx-Fxx-001 | {field} | string/date/number/enum/file | Y/N | {dict} | {rule} | {value} | {role} |

#### §5 Interaction And State / 交互与状态

| Current State | Action | Frontend Feedback | Backend Rule | Next State | Event / Audit |
|---|---|---|---|---|---|
| {state} | {data-action} | toast/modal/loading/disabled | {validation/transaction} | {state} | {event} |

#### §6 Business Rules And Data Flow / 业务规则与数据流

Describe source of truth, create/update/delete rules, synchronization,
calculation, conflict handling, audit logging, and upstream/downstream impact.

#### §7 Boundary And Exceptions / 边界与异常

| Category | Required Behavior |
|---|---|
| Empty / loading / error | {visible feedback + retry/preserve rule} |
| Input boundary | {required/format/length/duplicate/cross-field} |
| Permission | {vertical/horizontal overreach behavior} |
| State conflict | {repeat submit/stale data/deleted/locked} |
| Network / dependency | {timeout/offline/partial success/retry} |

#### §8 Metrics And Tracking / 指标与埋点

| Event ID | Trigger | Params | Purpose | Privacy |
|---|---|---|---|---|
| EVT-Mxx-Fxx-001 | {moment} | user_id, role, tenant_id, object_id, status | {metric} | mask/hash/omit |

#### §9 Frontend / Backend / QA Handoff Notes / 前后端与测试交接

| Reader | Must Know |
|---|---|
| Frontend | layout, component states, `data-testid`, `data-action`, client validation |
| Backend | permissions, state transition, transaction, idempotency, audit, dependency |
| QA | happy path, boundary, permission, state conflict, weak network, regression |

#### §10 Function-Level NFR / 功能级非功能要求

| Category | Requirement | Measurement |
|---|---|---|
| Performance | {latency / batch size / concurrency} | {threshold or proposed} |
| Security / Privacy | {masking / audit / permission} | {check method} |
| Compatibility | {browser/device/surface} | {scope} |

#### §11 Acceptance Criteria / 验收标准

| AC ID | Given | When | Then | Test Type | Priority |
|---|---|---|---|---|---|
| AC-Mxx-Fxx-001 | {precondition} | {action} | {observable result + domain result} | unit/integration/e2e/manual | P0/P1/P2 |

## Stage 4 Review And Delivery Plan / 阶段四 评审与交付计划

| Reviewer | Focus | Result | Blocking Gaps |
|---|---|---|---|
| PM | scope, scenario, priority | PASS/REVIEW_WITH_GAPS/BLOCKED | {gaps} |
| Frontend | page/layout/interaction | PASS/REVIEW_WITH_GAPS/BLOCKED | {gaps} |
| Backend | rule/data/state/API | PASS/REVIEW_WITH_GAPS/BLOCKED | {gaps} |
| QA | acceptance/testability | PASS/REVIEW_WITH_GAPS/BLOCKED | {gaps} |

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

## Appendix / 附录

Use appendices for source tables, dictionary details, policy excerpts, screenshots,
and long examples. Do not hide core requirements only in appendices.

## Gate Completion Statement / Gate 完成声明

```text
Scope: {artifact scope}
Mode / Tier / Profile: {mode} / {tier} / Human-First Full PRD
Triggered gates: {gates}
Artifacts updated: {files}
Verification: {scripts/reviews}
Completion state: PASS | REVIEW_COMPLETE_WITH_GAPS | BLOCKED
```
