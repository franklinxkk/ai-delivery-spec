# Domain: Traffic Safety And Transport Supervision

Use this replaceable domain module for 运管、交通监管、道路运输、交通安全、数据集市和指标库产品. A replacement `domain-*.md` must preserve the same 14 section headings used here and in `domain-module-template.md`.

## Contents

- Domain Purpose
- Vocabulary
- Aggregates and Entities
- Domain Events
- State Machines
- Metric / Indicator Governance
- AI Context Sources
- Content / Knowledge Assets
- Core Workflows
- Role Path Patterns
- UI / Mobile Patterns
- Policy / Privacy Constraints
- Domain Test Scenarios
- Acceptance Checklist

## Domain Purpose

- Business outcome: make regulated enterprises, vehicles, personnel, risks, inspections, rectification, training, maintenance, and reports visible and closable.
- Primary users: province/city/district regulators, inspectors, enterprise safety managers, drivers/personnel, platform administrators.
- Sensitive areas: identity documents, qualifications, vehicle location/trajectory, enforcement evidence, enterprise operating data.
- AI may optimize: document extraction, anomaly detection, risk hints, inspection assistance, report drafting.
- AI must not autonomously decide: punishment, license restriction, final major-hazard classification, forced service suspension, or other binding enforcement actions.

## Vocabulary

| Term | Meaning | Source Of Truth |
|---|---|---|
| Regulated Enterprise | enterprise within an institution/department supervision scope | enterprise master + org scope |
| Two-Type Personnel | principal and safety manager requiring safety assessment qualification | personnel/certificate records |
| Safety Code | governed enterprise/vehicle/person risk score and color | risk/safety-code service |
| Alert | machine, external platform, or rule-detected risk signal | alert source/event store |
| Safety Inspection | regulator-created online/offline inspection with items and evidence | inspection aggregate |
| Hidden Danger | problem requiring rectification and, when applicable, acceptance | hidden-danger aggregate |
| Rectification | enterprise evidence and action submitted against an issue | rectification record |
| Indicator | versioned metric with caliber, source, dimensions, owner, and quality rules | indicator registry |
| Report Task | period-specific execution using frozen template/indicator versions | report service |

## Aggregates and Entities

| Aggregate | Owns | Notes |
|---|---|---|
| Enterprise | profile, industries, licenses, signer, district scope | authoritative master data; multi-industry license union |
| Vehicle | profile, certificates, maintenance, insurance, GPS identity | often joins enterprise; trajectory remains external/event data |
| Driver/Personnel | employment, post, qualification, training | personal data requires masking and retention rules |
| RiskAssessment | risk score/level, evidence, rule/model version | AI/rule writable with audit; not a punishment decision |
| Alert | source, object, severity, disposition state | high-volume operational flow |
| SafetyInspection | plan/list, items, evidence, signatures, result | human-owned inspection and classification |
| HiddenDanger | source, level, rectification rounds, acceptance | history is append-only across returned rounds |
| EnforcementTask | inspection/rectification/escalation task | binding action requires authorized human approval |
| Indicator | caliber, source, dimensions, owner, version, status | governed reusable metric |
| ReportTemplate | indicators, fill columns, formulas, dimensions | reusable definition |
| ReportTask | period, scope, template snapshot, progress/result | execution record distinct from template |

## Domain Events

```yaml
events:
  RiskAssessmentCompleted:
    payload: { enterprise_id, risk_level, confidence, evidence_refs, rule_version }
  AlertAssigned:
    payload: { alert_id, owner_id, assigned_at }
  InspectionCompleted:
    payload: { inspection_id, enterprise_id, result, evidence_refs, signer_refs }
  RectificationIssued:
    payload: { inspection_id, hidden_danger_ids, deadline, issuer_id }
  RectificationSubmitted:
    payload: { hidden_danger_id, round, evidence_refs, submitted_at }
  RectificationAccepted:
    payload: { hidden_danger_id, reviewer_id, accepted_at }
  ReportSnapshotFrozen:
    payload: { report_task_id, template_version, metric_versions, cutoff_time }
```

## State Machines

```text
Alert: created -> pending_review -> assigned -> processing -> closed | escalated
Inspection: draft -> inspecting -> pending_rectification -> pending_acceptance -> qualified
Inspection: pending_acceptance -> pending_rectification (returned)
HiddenDanger: reported -> rectifying -> pending_acceptance -> accepted
HiddenDanger: pending_acceptance -> rectifying (rejected)
ReportTask: draft -> published -> executing -> completed | failed | cancelled
e-Waybill: draft -> submitted -> reviewed -> in_transport -> completed | rejected | cancelled
```

State consistency:

| Business Concept | Source Of Truth | Consumers | Consistency Need |
|---|---|---|---|
| enterprise status | enterprise master | risk/inspection/report | strong before regulated action |
| vehicle online state | GPS/monitoring | alert/risk/report | eventual for dashboard |
| license expiry | license facts | alert/report | governed freshness |
| rectification result | hidden-danger workflow | inspection/risk/report/audit | human-confirmed |
| final report | report snapshot | dashboard/export/submission | immutable snapshot |

## Metric / Indicator Governance

```yaml
indicator:
  id: string
  name: string
  category: hidden_danger | monitoring | license | training | maintenance | baseline
  caliber: string
  source: string
  dimensions: [enterprise, district, vehicle_type, date]
  compute_type: count | distinct | sum | avg | ratio | score | mom | chain
  sql_or_rule: string
  owner: role_or_team
  version: semver
  status: draft | pending_review | active | deprecated
  quality_checks: [source_exists, dimension_join_valid, null_rate_threshold]
```

Rules:
- no active indicator without business caliber, owner, source, dimensions, and version;
- AI-generated indicators start as draft and require human review;
- final reports freeze template, indicator versions, scope, and cutoff time;
- chart count is not indicator count; semantically identical metrics reuse one definition.

Common categories:

| Category | Examples |
|---|---|
| Hidden danger | pending rectification, pending acceptance, first-pass rate, closure rate |
| Dynamic monitoring | speeding/fatigue alerts, unhandled alerts, offline vehicles |
| License | expired enterprise/personnel/vehicle certificates |
| Training | pre-job completion, monthly training rate, learning hours |
| Maintenance | no plan, overdue, mileage anomaly, provider anomaly |
| Baseline | enterprises, vehicles, drivers, escorts, safety managers |

## AI Context Sources

| Context | Source | Freshness | Permission / Reliability Rule |
|---|---|---|---|
| enterprise/industry/license | enterprise master and license records | real-time/daily | org/data scope; authoritative fields identified |
| personnel qualification | employment and certificate records | real-time | identity fields minimized/masked |
| vehicle maintenance/insurance | vehicle and maintenance services | daily/real-time | distinguish missing from expired |
| trajectory and warnings | 809/GPS/active-defense platform | streaming/eventual | retain source timestamp and outage state |
| inspection/hidden danger | inspection and rectification records | real-time | signed evidence and human result are authoritative |
| regulations/checklists | approved knowledge base | versioned | cite effective version; no unsupported legal conclusion |

## Content / Knowledge Assets

| Asset | Minimum Metadata | Governance |
|---|---|---|
| laws/regulations | title, issuing authority, effective date, region, version | legal/business review before activation |
| inspection standards/templates | owner institution, applicable industry, version, item/evidence rules | district configuration with audit |
| certificate dictionaries | certificate type, applicable role/industry, validity rule | shared dictionary, versioned |
| training/course content | target role, risk topic, duration, assessment | content review and evidence level |
| notification/report templates | issuing level, audience, required signature/reply | controlled publishing and history |
| map/geofence data | coordinate system, source, update time | accuracy and access boundary recorded |

## Core Workflows

1. Enterprise initialization: transport-platform export -> AI/rule extraction -> validation -> human confirmation -> master-data import -> exception repair.
2. Risk handling: source event -> alert/risk calculation -> evidence review -> assign/handle/escalate -> close with audit.
3. Safety inspection: create -> field/online execution -> evidence/signatures -> classify issue -> issue rectification -> enterprise submission -> accept/return -> archive.
4. Special campaign: publish scope/deadline -> enterprises self-check/report -> rectification -> regulator progress/acceptance -> summary.
5. Report delivery: select/create template -> validate indicators -> create period task -> fill missing fields -> review/return -> freeze/export.

## Role Path Patterns

| Level / Role | Data Scope | Allowed Actions | Forbidden Actions |
|---|---|---|---|
| province regulator | cross-city aggregate and authorized drilldown | publish policy, inspect summary, escalate | edit enterprise self-fill records |
| city regulator | city and districts | assign inspection, review progress | bypass district evidence rules without authority |
| district/county regulator | own scoped enterprises | issue notice/inspection/rectification, accept closure | view other districts without authorization |
| inspector | assigned enterprises/tasks | execute items, capture evidence, sign, submit result | alter final evidence after submission |
| enterprise safety manager | own enterprise | maintain data, sign/submit evidence, rectify | view other enterprises or self-approve regulated closure |
| driver/personnel | own permitted tasks/data | training, exam, acknowledgement | access enterprise-wide sensitive data |

## UI / Mobile Patterns

- dense operational list with filters, saved views, scope label, and status-driven actions;
- detail drawer/page with evidence, source, timestamp, and audit timeline;
- mobile field inspection with stable test ids, camera/location permission fallback, weak-network draft, and idempotent sync;
- map only when spatial context is central; show stale/offline source state;
- batch actions require selection count, permission guard, confirmation, per-item result, and retry;
- multi-step e-Waybill or inspection flows use step indicators and stable next/back/submit test ids.

## Policy / Privacy Constraints

- Province/city/district/enterprise data isolation applies to list, detail, export, statistics, AI context, and embedded third-party pages.
- Identity, phone, certificate, trajectory, and enforcement evidence follow least access, masking, retention, and audit rules.
- AI recommendation shows source, confidence, missing context, and rule/model version.
- Punishment, service restriction, major-hazard classification, and closure acceptance require authorized human accountability.
- Test agents use shadow data or rollback-safe fixtures and must not pollute production statistics.
- Reports and enforcement evidence retain immutable snapshots according to approved retention policy.

## Domain Test Scenarios

| Scenario | Role | Expected Result |
|---|---|---|
| high-risk alert disposition | regulator | alert assigned, handled/escalated, evidence and audit visible |
| multi-industry enterprise license check | regulator/enterprise | required license set is the union of active industries |
| two-type personnel certificate expiry | regulator | risk shown without deleting personnel; source certificate traceable |
| field inspection under weak network | inspector | local draft preserved; idempotent sync; no duplicate inspection result |
| rejected rectification | enterprise/regulator | new rectification round created; previous evidence immutable |
| report task with mixed auto/fill data | regulator/enterprise | progress, fill assignments, frozen result, and export are traceable |
| driver fatigue recommendation | regulator | AI evidence visible; binding intervention requires human decision |
| e-Waybill lifecycle | enterprise/regulator | multi-step path and state guards match across PC/mobile |

## Acceptance Checklist

- [ ] All 14 domain module sections are present.
- [ ] Regulator, inspector, enterprise, driver/personnel, and admin paths are explicit where relevant.
- [ ] Organization and enterprise data isolation is enforced across UI, API, export, analytics, AI, and embedded systems.
- [ ] Enterprise, vehicle, personnel, inspection, hidden-danger, alert, indicator, and report lifecycles are consistent.
- [ ] Regulations, templates, indicators, rules, and AI outputs are versioned and traceable.
- [ ] Every binding regulated action has human accountability and audit evidence.
- [ ] Batch, multi-step, mobile weak-network, and exception paths are testable.
