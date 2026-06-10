# Domain + Traffic Context

Use this file for 运管/交通监管/道路运输/数据集市/指标库 products.

This is the replaceable domain module. If the company/industry changes, replace this file with a new `domain-*.md` that preserves the same section types: domain model, metric governance, workflows, scenarios, UI patterns, and checklist.

## Domain Modeling

Core aggregates:

| Aggregate | Owns | Notes |
|-----------|------|-------|
| Enterprise | enterprise profile, license state, district scope | master data is human/system authoritative |
| Vehicle | vehicle profile, license, maintenance, GPS/online status | often joins enterprise |
| Driver/Personnel | qualification, training, position | personal data needs desensitization |
| RiskAssessment | risk score, risk level, evidence, AI reasoning | AI writable with audit |
| Alert | alert type, source, handling state | high-volume operational flow |
| EnforcementTask | inspection/rectification/penalty task | human approval required |
| ReportTemplate | report columns, indicators, fill columns, dimensions | PM/business configurable |
| Indicator | metric name, caliber, SQL/source, dimensions, owner, status | must be governed |
| FillTask | enterprise submission task, deadline, fill status | cross-role workflow |

Event storming:

```yaml
event:
  name: RiskAssessmentCompleted
  actor: risk-analysis-agent
  trigger: RiskAssessmentRequested
  payload:
    enterprise_id: string
    risk_level: low | medium | high | critical
    confidence: float
    evidence_refs: [string]
  downstream:
    - EnforcementTaskCreated if risk_level >= high
    - NotificationSent if risk_level >= medium
```

State consistency must be explicit across systems:

| Business Concept | Source of Truth | Consumers | Consistency Need |
|------------------|-----------------|-----------|------------------|
| enterprise status | enterprise master | risk/enforcement/report | strong before enforcement |
| vehicle online state | GPS/monitoring | alert/risk/report | eventual ok for dashboard |
| license expiry | license facts | alert/report | daily freshness |
| fill submission | report/fill service | dashboard/export | strong for final report |
| enforcement result | enforcement workflow | risk/report/audit | human-confirmed |

## Indicator Governance

Indicator minimum:

```yaml
indicator:
  id: string
  name: string
  category: hidden_danger | monitoring | license | training | maintenance | baseline
  caliber: string
  source_table: string
  dimensions: [enterprise, district, vehicle_type, date]
  compute_type: count | distinct | sum | avg | ratio | score | mom | chain
  sql_or_rule: string
  owner: role_or_team
  status: draft | pending_review | active | deprecated
  updated_at: date
  quality_checks:
    - no_duplicate_name
    - source_exists
    - dimension_join_valid
    - null_rate_threshold
```

Quality rules:
- no active indicator without caliber;
- no template column may reference an indicator with different semantic meaning;
- duplicate names require disambiguating dimension/scope suffix;
- SQL-derived indicators must declare source tables and dimensions;
- AI-generated indicators start as draft and require human review;
- every indicator used by report template increments `refCount`.

## Transport Metric Categories

Common categories:

| Category | Examples | Source |
|----------|----------|--------|
| 隐患闭环 | 待整改数, 待验收数, 安全闭环指数, 年度办结率 | `dwd_hidden_danger` |
| 动态监控 | 三超一疲劳预警处理率, 待处理数, 长期未处理数, 未在线车辆数 | `dwd_vehicle_alarm` |
| 证照预警 | 企业/人员/车辆证件超期数, 老旧车辆数 | `dwd_license_expire` |
| 培训教育 | 岗前培训不达标, 安全培训达标率, 学时不达标 | `dwd_training_record` |
| 维修维护 | 无年度计划, 维护异常, 里程超期, 周期超期 | `dwd_maintenance_record` |
| 基础底数 | 企业数, 车辆数, 驾驶员数, 押运员数 | dimension tables |

Dimension examples:
- 企业, 区县, 区域;
- 日期, 月份, 季度;
- 车辆类型, 车辆类型详细;
- 人员岗位, 培训类型;
- 隐患等级.

## Regulatory Hierarchy / ToG Workflow

Traffic supervision products usually have hierarchical visibility and escalation:

```text
province -> city -> district/county -> enterprise
```

| Level | Typical Role | Data Scope | Allowed Actions | Forbidden Actions |
|---|---|---|---|---|
| province | provincial regulator | cross-city aggregate + drilldown by policy | publish policy, inspect summary, escalate | edit enterprise self-fill records |
| city | city regulator | city + districts | assign inspection, review district progress | approve enterprise evidence without district rule |
| district/county | local regulator | own district enterprises | issue rectification, review evidence, accept closure | view other districts unless authorized |
| enterprise | enterprise safety/admin | own enterprise only | submit evidence, fill reports, view own alerts | view other enterprise data |

Common approval/rectification state:

```text
draft -> issued -> enterprise_processing -> submitted_for_review
-> returned | accepted | escalated | closed
```

Rules:
- Every rectification/inspection task must record issuing level, responsible enterprise, deadline, evidence requirement, and acceptance role.
- Upper-level override or escalation must create audit evidence and reason.
- Enterprise-submitted evidence is not final until regulator acceptance.
- Cross-level dashboard data may aggregate broadly, but item-level evidence follows org-scope permission.
- Use `approval-workflow.md` for review/return/acceptance behavior and `saas-multitenancy.md` for org-scope isolation.

## Data Mart / Report Template Pattern

Use this pattern for 运管数据集市:

```yaml
report_template:
  id: string
  name: string
  type: 上级常用报表 | 专项报表 | 基础台账 | 本单位自建模板
  main_dimension: 企业 | 区县 | 车辆类型 | 人员岗位 | 隐患等级
  columns:
    - kind: sys
      indicator_id: string
      label: string
    - kind: ext
      label: string
      fill_required: true
    - kind: formula
      label: string
      expression: string
      dependencies: [column_label]
  filters:
    dimensions: []
    indicator_filters: []
  lifecycle: draft | active | deprecated
```

Workflow:
1. PM/运管员 selects or creates template.
2. System validates indicator references and dimensions.
3. User adds fill columns if source data is incomplete.
4. Report task is created for period and enterprise scope.
5. Enterprises fill missing columns.
6. Regulator reviews/returns/exports.
7. Final report freezes data snapshot and audit log.

## Traffic Scenarios

### 1. Alert Disposition Center

Goal: detect and handle vehicle/enterprise risk alerts.

Core flow:
`alert_created -> pending_review -> assigned -> processing -> closed | escalated`

Required views:
- alert list with severity, source, enterprise, time;
- detail evidence chain;
- handling action;
- batch reminder/assignment;
- audit timeline.

### 2. Enterprise Compliance Dashboard

Goal: one-page compliance health for enterprise and regulator.

Content:
- risk score and trend;
- hidden danger closure;
- license/training/maintenance status;
- alert handling rate;
- drilldown by vehicle/personnel.

### 3. Driver Fatigue Intervention

Goal: identify fatigue driving and trigger intervention.

AI constraints:
- AI may recommend risk level;
- enforcement or suspension requires human approval;
- evidence must include vehicle track, time window, regulation refs.

### 4. e-Waybill

Goal: manage electronic waybill lifecycle.

State:
`draft -> submitted -> reviewed -> in_transport -> completed | rejected | cancelled`

Prototype must use multi-step testid naming for waybill create/edit flows.

### 5. Real-Time Tracking + Geofence

Goal: map-based supervision.

Core:
- vehicle marker;
- track replay;
- geofence alert;
- offline state;
- drilldown to enterprise/vehicle.

## UI Patterns for Traffic Products

Recommended operational screens:
- dense table with filters and saved views;
- metric cards for operational totals;
- drilldown drawer/modal for evidence;
- timeline for audit and state changes;
- map only when spatial context is central;
- role switcher for regulator/enterprise preview;
- data scope label for district/org isolation.

Required annotations:

```html
<section data-testid="data-scope-banner" data-org-scope="district:东坡区"></section>
<table data-testid="enterprise-risk-table" data-api="/api/v1/enterprises/risk" data-method="GET"></table>
<button data-testid="btn-batch-remind-fill" data-action="batch-remind-fill"></button>
```

## Transport Product Checklist

- [ ] Roles include regulator, supervisor, enterprise user, admin.
- [ ] District/org data isolation is explicit.
- [ ] Every regulated action has audit trail.
- [ ] Report/export freezes source snapshot.
- [ ] Indicator caliber, source, dimension, owner, status are present.
- [ ] AI recommendations show confidence, evidence, and human gate.
- [ ] Batch actions and multi-step forms have stable testids.
- [ ] Mobile/field use is considered for enterprise filling and inspection.
