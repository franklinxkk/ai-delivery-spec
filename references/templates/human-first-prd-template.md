# Human-First Full PRD Template (v4.9.14 Profile)

Use this profile when the PRD will be reviewed, developed, tested, outsourced,
accepted, or archived by human teams. The document must be readable before it
is machine-readable. Engineering contracts support the product specification;
they do not replace it.

## Contents

- Heading Hierarchy Lock
- 0D 分流与范围 / 0D Triage And Scope
- 阶段一 需求规划 / Stage 1 Requirement Planning
- 阶段二 IA 与原型锁定 / Stage 2 IA And Prototype Lock
- 阶段三 完整功能需求记录 / Stage 3 Complete Functional Requirement Records
- 阶段四 评审与交付计划 / Stage 4 Review And Delivery Plan
- 阶段五 测试与验收 / Stage 5 Test And Acceptance
- 阶段六 上线与复盘 / Stage 6 Launch And Review
- 附录 / Appendix
- 完成门禁声明 / Gate Completion Statement

## Heading Hierarchy Lock

- Use exactly one H1 (`#`) for the document title.
- Use H2 (`##`) for global lifecycle stages or top-level modules.
- Use H3 (`###`) for module subsections and function records.
- Use H4 (`####`) for FRR numbered sections inside one function.
- Do not jump from H2 directly to H4.
- Do not use bold text, table rows, or numbered list items as fake headings.
- Final output language follows the user's spoken language. For Chinese PRDs,
  use Chinese headings only unless the user explicitly asks for bilingual
  headings. Do not copy English template headings into Chinese deliverables.

## 0D 分流与范围 / 0D Triage And Scope

```text
[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false] | [INFO: complete|partial|missing]
Mode: Lite | Standard | Full
PRD Profile: Human-First Full PRD
Lifecycle Stage: Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire
```

### Source Evidence Register

| Source ID | Artifact | Locator | Type | Authority | Target Module | Disposition | Assertion Status |
|---|---|---|---|---|---|---|---|
| SRC-001 | {file/path} | {page/sheet/view} | screenshot/prototype/prd/excel/sql/policy/interview | authoritative/supporting/historical | Mxx | EMBEDDED/ANNEX/DEFERRED/CONFLICT | VERIFIED/INFERRED/PROPOSED/UNKNOWN |

Rules:

- Every important claim must trace to a source, an inference, or an explicit
  open question.
- Do not write "see prototype" without `view_id`, `region_id`, `data-testid`,
  `data-action`, screenshot page, or module/function ID.

## 阶段一 需求规划 / Stage 1 Requirement Planning

### 1.1 项目背景与业务目标 / Project Background And Business Goals

Write 1-2 short paragraphs explaining the business scene, pain, and expected
outcome. Avoid abstract phrases such as "improve efficiency" unless the
behavior and measurement are stated.

| Goal ID | Goal | Measurement | Priority |
|---|---|---|---|
| BO-01 | {business outcome} | {metric or review signal} | P0/P1/P2 |

### 1.2 角色、职责与使用场景 / Roles, Responsibilities, And Use Scenes

| Role ID | Role | Responsibility | System Goal | Typical Scenario | Pain Point |
|---|---|---|---|---|---|
| ROLE-001 | {name} | {responsibility} | {goal} | {when/where} | {pain} |

### 1.3 核心用户旅程与业务场景 / Core User Journey And Business Scenario

| Scenario ID | Role | When / Trigger | Goal | Main Action | Success Result | Exception To Watch |
|---|---|---|---|---|---|---|
| SC-M01-01 | {role} | {trigger} | {goal} | {action} | visible result + domain result | {exception} |

### 1.4 竞品/替代方案、价值与优先级 / Competitor / Alternative Analysis, Value, And Priority

Use this section when the requirement is not fully shaped, when multiple
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

### 1.5 EARS 需求表述规则 / EARS Requirement Writing Rule

For P0/P1 behavior, include at least one EARS-style statement before detailed
tables.

| Pattern | Sentence Shape | Example Intent |
|---|---|---|
| Event-driven | When {event}, the system shall {response}. | trigger-based behavior |
| State-driven | While {state}, the system shall {response}. | state-dependent buttons/rules |
| Unwanted behavior | If {unwanted condition}, the system shall {mitigation}. | invalid input / overreach / abuse |
| Optional feature | Where {feature/config/permission}, the system shall {response}. | configuration or permission branch |
| Ubiquitous | The system shall {invariant}. | always-on rule |

### 1.6 范围、优先级与不做事项 / Scope, Priority, And Out-Of-Scope

| Module ID | Module | In Scope | Out Of Scope | Priority | Release |
|---|---|---|---|---|---|
| M01 | {module} | {functions} | {exclusions} | P0/P1/P2 | v{version} |

## 阶段二 IA 与原型锁定 / Stage 2 IA And Prototype Lock

### 2.1 IA 骨架 / IA Skeleton

| Module ID | View ID | View Name | Platform | Primary Roles | Regions | Primary Actions |
|---|---|---|---|---|---|---|
| M01 | M01-V01 | {view} | web/mobile/miniapp | {roles} | {region_ids} | {action_ids} |

### 2.2 页面布局与区域地图 / Page Layout And Region Map

| Layout ID | View ID | Region ID | Region Name | Position | Main Components | Visible States | Notes |
|---|---|---|---|---|---|---|---|
| LAY-M01-V01-R01 | M01-V01 | region-filter | {name} | top/left/main/right/bottom/modal/drawer | {components} | empty/loading/error/success/disabled | {notes} |

Rules:

- `Layout ID` format: `LAY-{view_id}-{RNN|MNN|DNN|PNN}`.
- Keep `Layout ID`, `view_id`, `region_id`, and `data-testid` stable after
  assignment.
- If an IA Skeleton is locked, reference its `region_id` instead of rewriting
  the same region definitions in multiple places.

### 2.3 原型锁定记录 / Prototype Lock Record

| Artifact | Path / URL | Lock Status | Evidence Scope | Owner |
|---|---|---|---|---|
| Prototype | {path} | locked / draft | views/actions/modals/states/mock data | {owner} |

### 2.4 AI+Data 产品系统契约 / AI + Data Product System Contract

Use this section for data source, data platform, data mart, BI, reporting,
dashboard, indicator library, semantic/ontology, Data Agent, ChatBI, or fill-in
products. For Chinese PRDs, write this section in Chinese.

| Layer | Required Content |
|---|---|
| 多源数据接入 | 数据源清单、连接方式、凭证负责人、schema、同步频率、补数、幂等、失败隔离 |
| 清洗处理 | 转换规则、标准化、去重/实体对齐、异常队列、原始值保留、质量门禁 |
| 治理目录 | 资产目录、元数据、血缘、数据分级、质量分、审批、审计、生命周期 |
| 存储检索 | lake/warehouse/mart/OLAP/search/vector/cache、刷新、延迟、留存、成本、权限 |
| 语义/本体 | 业务术语、指标、维度、对象类型、关系、动作类型、示例、版本与回滚 |
| 分析应用 | 看板、自助分析、报表、填报、筛选、下钻、导出、空/错/无权限状态 |
| Data Agent / ChatBI | 允许数据源与工具、继承用户权限、引用证据、刷新状态、拒答规则、评测集、人工门禁 |
| 洞察到行动 | 洞察解释、任务/流程/本体动作、写入范围、最终责任人、回滚与复盘指标 |

## 阶段三 完整功能需求记录 / Stage 3 Complete Functional Requirement Records

Repeat one complete FRR for every in-scope function. A module is not complete
until all its functions have complete records.

Long-form PRD continuation contract:

- Build a Release Function Inventory before writing FRRs. The inventory is the
  denominator for completion and must list `module_id`, `function_id`, role,
  state/permission difference, source evidence, and priority.
- Write FRRs by bounded module/function batches when the document is large. Do
  not make later modules thinner to fit one response.
- Keep a PRD Completion Ledger after every batch:

| Module | Planned FRRs | Completed FRRs | Missing Sections | Blocking Gaps | Next Batch |
|---|---:|---:|---|---|---|
| M01 | 3 | 2 | M01-F03 §8/§11 | metric owner unknown | continue M01-F03 |

- If the remaining inventory cannot fit in the current response, stop at a
  stable boundary and output `CONTINUATION_REQUIRED` with the next batch plan.
  Final completion state remains `BLOCKED` or `REVIEW_COMPLETE_WITH_GAPS`
  until every planned FRR is complete.
- Before handing over the PRD as final, run a self-repair loop: verify FRR
  count, 16-section completeness, source coverage, page/action/state coverage,
  permission, exception, acceptance, and unresolved P0 gaps; then revise the
  weak modules instead of merely reporting them.

Use plain text or bold text for module grouping. Do not add `### Mxx Module`
between the Stage 3 heading and FRR records, because that causes H3 -> H5
heading jumps in generated PRDs.

### Mxx-Fxx {Function Name}

Every in-scope function must contain all 16 FRR sections. If a section does not
apply, write `N/A + reason`; do not leave it blank or write only "see prototype",
"same as above", or "existing logic".

#### §1 业务场景 / Business Scenario

Use `who / when / why / what / result` to describe the concrete scene. State
the visible user result and the domain/business result.

#### §2 角色与场景 / Roles And Scenario

| Role | Responsibility In This Function | Start Condition | Success Exit | Next Action |
|---|---|---|---|---|
| {role} | {responsibility} | {trigger/state} | {visible + domain result} | {next step} |

#### §3 入口与前置条件 / Entry And Preconditions

| Item | Requirement |
|---|---|
| Entry | {menu/button/link/API/notification} |
| Preconditions | {role/data/state/config/time/dependency} |
| Blocked Entry Handling | {disabled/hidden/error/redirect/audit} |
| Upstream Dependency | {source module/event/data} |

#### §4 页面、区域与可见状态 / Pages, Regions, And Visible States

Reference `Layout ID`, `view_id`, `region_id`, `data-testid`, table columns,
form fields, modal/drawer chain, responsive differences, and empty/loading/error
/success/disabled states. State how the page looks and behaves, not only which
data exists.

For each page, card, timeline, table, modal, or drawer in this function, add a
page-level detailed-design table:

| Surface | Position / Region | Fields Shown | Repeated Record Rule | Empty / Loading / Error | Role / State Variant |
|---|---|---|---|---|---|
| {page/card/modal} | top/middle/bottom/left/right/modal | {labels + data-field} | sort/group/page size/many-record behavior | {states} | {role/state differences} |

#### §5 字段、字典与校验 / Fields, Dictionaries, And Validation

When a locked prototype exists: every implementation-relevant `data-field`,
display field, input field, calculated field, table column, card label, timeline
item, and filter must map to a field definition here or in the global field
dictionary. Do not rely on visual labels alone.

| Field ID | Field Name | Type | Required | Dictionary / Enum | Validation | Default | Editable By |
|---|---|---|---|---|---|---|---|
| FLD-Mxx-Fxx-001 | {field} | string/date/number/enum/file | Y/N | {dict} | {rule} | {value} | {role} |

For data mart, BI, reporting, dashboard, indicator library, or fill-in
products, add these optional columns when relevant:

| Field ID | Field Name | Type | Required | Dictionary / Enum | Validation | Default | Editable By | Dimension / Caliber | sys/ext | Statistical Period |
|---|---|---|---|---|---|---|---|---|---|---|
| FLD-Mxx-Fxx-001 | {field} | number/string/date/enum | Y/N | {dict} | {rule} | {value} | system/role | IND-001 / DIM-AREA | sys/ext | month/custom |

#### §6 编号交互流程 / Numbered Interaction Flow

| Step | Actor | Action / data-action | Frontend Feedback | Backend Rule | Domain Result | Failure Branch |
|---|---|---|---|---|---|---|
| 1 | {role} | {data-action} | toast/modal/loading/disabled | {validation/transaction} | {state/event/audit} | {error/retry} |

#### §7 操作与规则 / Actions And Operation Rules

| Action | Allowed Role | Allowed State | Confirmation | Idempotency | Visible Result | Domain Result |
|---|---|---|---|---|---|---|
| {action} | {role} | {state} | none/modal/second-confirm | yes/no/key | {ui result} | {data/state/event} |

For each lifecycle entity touched by the function, declare CRUD/delete semantics:

| Entity | Create | Edit | Delete / Close / Void / Archive | Allowed States | Forbidden States | Audit / Event |
|---|---|---|---|---|---|---|
| {entity} | {action/API} | {action/API} | physical delete / soft delete / close / void / archive / not supported | {states} | {states} | {audit/event} |

#### §8 业务规则、计算与口径 / Business Rules, Calculations, And Calibers

Describe source of truth, create/update/delete rules, synchronization,
calculation, threshold/caliber, conflict handling, audit logging, and
upstream/downstream impact. Number every rule as `BR-Mxx-Fxx-NN`.

For complex forms or calculated values, add a calculation contract:

| Field / Row | Trigger | Formula / Rule | Manual Override | Backend Validation | Error / Empty Behavior |
|---|---|---|---|---|---|
| {field} | on change / submit / recalc | {formula} | allowed/forbidden + flag | {server rule} | {message/state} |

#### §9 状态、按钮与生命周期行为 / State, Button, And Lifecycle Behavior

| Current State | Visible Actions | Forbidden Actions | Guard | Next State | Event / Audit |
|---|---|---|---|---|---|
| {state} | {actions} | {actions} | {role/data/time/config} | {state} | {event/audit} |

Example:

| Current State | Visible Actions | Forbidden Actions | Guard | Next State | Event / Audit |
|---|---|---|---|---|---|
| draft | submit, save | approve, export | owner role + required fields valid | submitted | SubmissionSubmitted / audit |

#### §10 权限与数据范围 / Permissions And Data Scope

| Role | Function Permission | Data Scope | Field / Action Restriction | Overreach Handling |
|---|---|---|---|---|
| {role} | view/create/update/delete/approve/export | self/department/specified/all/custom | {restriction} | block/mask/escalate/audit |

#### §11 异常、降级与恢复 / Exceptions, Fallback, And Recovery

| Category | Required Behavior |
|---|---|
| Empty / loading / error | {visible feedback + retry/preserve rule} |
| Input boundary | {required/format/length/duplicate/cross-field} |
| Permission | {vertical/horizontal overreach behavior} |
| State conflict | {repeat submit/stale data/deleted/locked} |
| Network / dependency | {timeout/offline/partial success/retry} |

#### §12 通知、审计与依赖 / Notifications, Audit, And Dependencies

| Trigger | Recipient / Dependency | Channel / Interface | Payload / Content | Failure Handling | Audit Owner |
|---|---|---|---|---|---|
| {trigger} | {role/system} | in-app/SMS/API/event/file | {payload} | retry/fallback/manual | {owner} |

#### §13 数据、AI 与算法契约 / Data, AI, And Algorithm Contract

Choose the applicable sub-template by product type.

Data product:

| Contract Type | Required Content |
|---|---|
| Source and ingestion | source inventory, connector/API/file/stream/manual mode, auth, schema, cadence, backfill, retry, idempotency |
| Processing and quality | transform/clean rules, dedupe, entity resolution, quality gates, exception handling, raw-data preservation |
| Governance and catalog | owner, classification, metadata, lineage, certification, access policy, audit, lifecycle |
| Storage and retrieval | lake/warehouse/mart/OLAP/search/vector/cache, freshness, latency, retention, cost, permissions |
| Semantic and ontology | glossary, metric/dimension model, object/link/action types, relation rules, examples, model version |
| Analytics/reporting/fill-in | dashboard/report/fill workflow, filters, drill, export, sys/ext split, submit/review state |
| Data Agent / ChatBI | allowed sources/tools, inherited permission, citations, freshness, refusal rules, eval sets, human gate |
| Action loop | insight-to-task/action, write scope, final accountable owner, rollback, monitoring |

AI product:

| Contract Type | Required Content |
|---|---|
| AI / Algorithm | deterministic vs model responsibility, input/output schema, confidence, human gate, fallback, evaluation |
| Prohibited Write | fields/states/actions AI or automation must not modify |

CRUD / business product:

| Contract Type | Required Content |
|---|---|
| Data | source of truth, schema/dictionary, import/export, sync timing, consistency owner |
| API / event | endpoint, request/response, state guard, event payload, idempotency |

#### §14 功能级非功能需求 / Function-Level NFR

| Category | Requirement | Measurement |
|---|---|---|
| Performance | {latency / batch size / concurrency} | {threshold or proposed} |
| Security / Privacy | {masking / audit / permission} | {check method} |
| Compatibility | {browser/device/surface} | {scope} |
| Operations | {monitoring/retry/rollback/support} | {evidence} |

#### §15 前端 / 后端 / QA 交接说明 / Frontend / Backend / QA Handoff Notes

| Reader | Must Know |
|---|---|
| Frontend | layout, component states, `data-testid`, `data-action`, client validation |
| Backend | permissions, state transition, transaction, idempotency, audit, dependency |
| Algorithm / AI | data source, schema, prompt/rule/model responsibility, eval/fallback |
| QA | happy path, boundary, permission, state conflict, weak network, regression |

#### §16 验收与追溯 / Acceptance And Traceability

| AC ID | Given | When | Then | Test Type | Priority | Source / Prototype |
|---|---|---|---|---|---|---|
| AC-Mxx-Fxx-001 | {precondition} | {action} | {observable result + domain result} | unit/integration/e2e/manual | P0/P1/P2 | SRC-... / data-action |

After all FRRs, add these shared summaries when lifecycle, workflow, or
cross-module delivery is in scope: Global State Machine Summary, Domain Event
Inventory, and E2E Cross-Module Canvas.

## 阶段四 评审与交付计划 / Stage 4 Review And Delivery Plan

### 4.1 Sprint 任务拆解 / Sprint Task Breakdown / WBS

| Task ID | Slice | Source FRR | Owner Role | Dependency | Done Criteria |
|---|---|---|---|---|---|
| TASK-Mxx-001 | {vertical slice} | Mxx-Fxx | FE/BE/QA/AI | {dependency} | {test/evidence} |
| TASK-M01-001 | complete create-report happy path | M01-F01 | FE+BE+QA | indicator dictionary ready | AC-M01-F01-001 pass |

### 4.2 风险登记册 / Risk Register

| Risk ID | Risk | Impact | Probability | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| RISK-001 | {risk} | H/M/L | H/M/L | {mitigation} | {owner} | {trigger} |
| RISK-002 | metric source table not delivered | H | M | freeze mock source and mark report as draft | data owner | DWD delivery delayed |

### 4.3 关键依赖项 / Key Dependencies

| Dependency ID | Upstream / Owner | Needed By | Required Date | Fallback | Status |
|---|---|---|---|---|---|
| DEP-001 | {system/person} | {module/function} | {date} | {fallback} | open/confirmed/blocked |
| DEP-002 | DWD source table / data owner | M01-F01, M03-F01 | Sprint 1 Week 2 | use verified CSV annex | open |

### 4.4 研发跟进、风险与阻塞 / Development Follow-Up, Risk, And Blockers

Use this when build/verify is in scope.

| TRK ID | Date | Module / FRR | Owner | Progress | Blocker / Risk | Decision Needed | Next Check |
|---|---|---|---|---|---|---|---|
| TRK-001 | {date} | Mxx-Fxx | {owner} | not-started/in-progress/done | {blocker} | {decision} | {date} |

### 4.5 Bug 管理与验收缺陷 / Bug Management And Acceptance Defects

| BUG ID | Source AC | Severity | Steps To Reproduce | Expected | Actual | Owner | Status |
|---|---|---|---|---|---|---|---|
| BUG-001 | AC-Mxx-Fxx-001 | P0/P1/P2 | {steps} | {expected} | {actual} | {owner} | open/fixed/verified |

### 4.6 待确认问题 / Open Questions

| Question ID | Module / FRR | Question | Owner | Blocks Delivery? | Due Date | Decision |
|---|---|---|---|---|---|---|
| Q-001 | Mxx-Fxx | {question} | {owner} | Y/N | {date} | open/decided |

## 阶段五 测试与验收 / Stage 5 Test And Acceptance

| Test ID | Source AC | Test Type | Preconditions | Steps | Expected Result | Evidence |
|---|---|---|---|---|---|---|
| TC-001 | AC-Mxx-Fxx-001 | unit/integration/e2e/manual | {precondition} | {steps} | {result} | screenshot/log/report |

Acceptance package:

- source evidence register;
- IA Skeleton and prototype lock record;
- FRR coverage table;
- acceptance/test coverage table;
- unresolved risks and de-scoped items;
- sign-off owner and date.

## 阶段六 上线与复盘 / Stage 6 Launch And Review

### 6.1 上线检查清单 / Launch Checklist

| Area | Check | Owner | Evidence | Result |
|---|---|---|---|---|
| data | migration/import/reconciliation ready | {owner} | {evidence} | pass/fail |
| operation | on-call, rollback, support ready | {owner} | {evidence} | pass/fail |
| security | permission, masking, audit, test-data isolation verified | {owner} | {evidence} | pass/fail |
| rollback | feature flag, data backup, and rollback owner ready | {owner} | {evidence} | pass/fail |

### 6.2 数据观察清单 / Post-Launch Metrics Watch

| Metric / Signal | Baseline | Target | Actual | Watch Window | Alert Threshold |
|---|---|---|---|---|---|
| {metric} | {baseline} | {target} | {actual} | T+1/T+7/T+30 | {threshold} |

### 6.3 复盘报告 / Post-launch Review

| Metric / Signal | Baseline | Target | Actual | Decision | Follow-Up |
|---|---|---|---|---|---|
| {metric} | {baseline} | {target} | {actual} | continue/iterate/rollback/retire | {action} |

### 6.4 5 Whys 根因分析 / 5 Whys

| Problem | Why 1 | Why 2 | Why 3 | Why 4 | Why 5 | Root Cause | Action |
|---|---|---|---|---|---|---|---|
| {problem} | | | | | | {root cause} | {owner/date} |

### 6.5 后续行动项 / Action Items

| Iteration | Topic | Action | Priority | Owner | Due Date |
|---|---|---|---|---|---|
| vNext | {topic} | {action} | P0/P1/P2 | {owner} | {date} |

## 附录 / Appendix

### 附录 A 术语表 / Appendix A Glossary

| Term | Definition | Notes |
|---|---|---|
| {term} | {definition} | {notes} |

### 附录 B 角色权限矩阵 / Appendix B Role Permission Matrix

| Role | Menu | Action | Data Scope | Field Scope |
|---|---|---|---|---|
| {role} | {menu} | {action} | {scope} | {fields} |

### 附录 C API 端点清单 / Appendix C API Endpoint Inventory

| Method | Path | Source FRR | Auth | Idempotency | Notes |
|---|---|---|---|---|---|
| GET | /api/{module}/{resource} | Mxx-Fxx | yes | yes | {notes} |

### 附录 D E2E 跨模块链路画布 / Appendix D E2E Cross-Module Canvas

| Upstream State Change | Domain Event | Downstream State Change | Test Case |
|---|---|---|---|
| {source state} | {event} | {target state} | AC-E2E-001 |

### 附录 E 决策记录 / Appendix E Decision Records

| Decision ID | Date | Decision | Options Considered | Owner | Impact |
|---|---|---|---|---|---|
| ADR-001 | {date} | {decision} | {options} | {owner} | {impact} |

## 完成门禁声明 / Gate Completion Statement

```text
Completion State: PASS | REVIEW_COMPLETE_WITH_GAPS | BLOCKED
Profile: Human-First Full PRD
Scope:
Triggered Gates:
Verification:
Open Risks:
Next Step:
```
