# Domain: Traffic Safety And Transport Supervision

Use this replaceable domain module for 运管、交通监管、道路运输、交通安全、数据集市和指标库产品. A replacement `domain-*.md` must preserve the same 14 section headings used here and in `domain-module-template.md`.

## Contents

- Domain Purpose
- First-Principles Domain Lens
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
- Multi-Agent Lifecycle Verification Matrix
- Acceptance Checklist

## Domain Purpose

- Business outcome: make regulated enterprises, vehicles, personnel, risks, inspections, rectification, training, maintenance, and reports visible and closable.
- Primary users: province/city/district regulators, inspectors, enterprise safety managers, drivers/personnel, platform administrators.
- Sensitive areas: identity documents, qualifications, vehicle location/trajectory, enforcement evidence, enterprise operating data.
- AI may optimize: document extraction, anomaly detection, risk hints, inspection assistance, report drafting.
- AI must not autonomously decide: punishment, license restriction, final major-hazard classification, forced service suspension, or other binding enforcement actions.

## First-Principles Domain Lens

Traffic and transport supervision product judgment starts from regulated risk
closure, not from dashboards alone.

| Lens | Transport Question | Acceptance Signal |
|---|---|---|
| Regulated object | Which enterprise, vehicle, person, license, inspection, danger, or report is governed? | authoritative master, jurisdiction, and data scope are explicit |
| Safety closure | What risk or hidden danger moves from detected to rectified/accepted? | state, deadline, evidence, reviewer, and audit are traceable |
| Standards authority | Which national law/policy, GB/GB-T, JT/JT-T/JTG, GA, DBxx/T, group, or customer rule applies? | source register and applicability/conflict status are explicit |
| Human authority | Which enforcement, punishment, license, or suspension decision needs accountable human approval? | AI/rules only suggest; final binding action is human-owned |
| Evidence quality | Can inspection, rectification, alert, and report conclusions be replayed? | frozen metrics, evidence refs, signatures, and versioned rules exist |

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
| national / industry / local / group standards corpus | standard code, issuer, region, effective date, status, applicability, mapped product rule | versioned register; never assume active without owner review |
| inspection standards/templates | owner institution, applicable industry, version, item/evidence rules | district configuration with audit |
| certificate dictionaries | certificate type, applicable role/industry, validity rule | shared dictionary, versioned |
| training/course content | target role, risk topic, duration, assessment | content review and evidence level |
| notification/report templates | issuing level, audience, required signature/reply | controlled publishing and history |
| map/geofence data | coordinate system, source, update time | accuracy and access boundary recorded |

Standards corpus layers:

| Layer | Examples Of Code Family | Product Contract |
|---|---|---|
| National law / policy | laws, administrative regulations, State Council/ministerial rules | cite issuer, effective date, region, and binding force |
| National standards | `GB`, `GB/T` | record mandatory/recommended status and affected fields/rules |
| Transport industry standards | `JT`, `JT/T`, `JTG` | map inspection item, certificate, vehicle, monitoring, report, or interface rule |
| Public-safety / cross-agency interfaces | `GA`, local joint-interface rules where relevant | identify data-sharing boundary and authority |
| Provincial / local standards | `DB`, `DBxx/T`, local notices and implementation rules | bind to province/city/district applicability |
| Group / association standards | `T/...` | mark as optional/customer-adopted unless contract says otherwise |
| Enterprise / customer rules | internal safety system, operation handbook, acceptance checklist | mark as customer-specific and not general regulation |

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
- Standards used by rules, AI answers, templates, inspections, and reports must
  cite issuer, region, effective date, version/status, and applicability. When
  national, industry, local, group, and enterprise rules conflict, record the
  conflict and decision owner instead of silently choosing one.

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
| standards applicability conflict | regulator/legal reviewer | GB/industry/local/group/customer rule conflict is recorded with owner decision before activation |

## Multi-Agent Lifecycle Verification Matrix

| domain_id | stage | reviewer_agent | path_type | scenario_ref | evidence_ref | blocking_question | expected_result | test_marker | verdict |
|---|---|---|---|---|---|---|---|---|---|
| traffic | Discover | PM Agent | happy_path | high-risk alert disposition | Domain Purpose / Core Workflows | Is the transport safety outcome valuable and scoped? | outcome and owner are explicit | traffic_discover_pm_happy_path | PASS |
| traffic | Discover | Domain Expert Agent | exception_path | standards applicability conflict | Content / Knowledge Assets | Are national, industry, local, group, and customer standards registered? | standards_corpus_register exists with issuer/region/effective date | standards_corpus_register | PASS |
| traffic | Discover | Architecture / Data / AI Agent | permission_privacy_path | vehicle trajectory and warning data | AI Context Sources / Policy / Privacy Constraints | Can discovery avoid over-collecting sensitive trajectory data? | source freshness, scope, and masking are recorded | traffic_discover_arch_permission_privacy_path | PASS |
| traffic | Discover | QA Agent | lifecycle_transition | alert disposition | State Machines / Domain Test Scenarios | Can QA identify the first lifecycle path? | Alert created -> closed/escalated is testable | traffic_discover_qa_lifecycle_transition | PASS |
| traffic | Discover | Coding Agent | acceptance_test_path | delivery package handoff | Acceptance Checklist | Can a coding agent find source-of-truth order? | ac_structured, data-testid, data-action, data-state, data-api, data-method, manifest.json, source_of_truth_order required | ac_structured;data-testid;data-action;data-state;data-api;data-method;manifest.json;source_of_truth_order | PASS |
| traffic | Specify | PM Agent | happy_path | safety inspection | Core Workflows | Does the PRD specify visible and domain result? | inspection -> rectification -> acceptance is explicit | traffic_specify_pm_happy_path | PASS |
| traffic | Specify | Domain Expert Agent | exception_path | rejected rectification | Domain Test Scenarios | Are returned/rejected paths specified? | new rectification round keeps previous evidence immutable | traffic_specify_domain_exception_path | PASS |
| traffic | Specify | Architecture / Data / AI Agent | permission_privacy_path | regulated action | Policy / Privacy Constraints | Are binding actions guarded by authorized humans? | regulated_action_human_accountability is mandatory | regulated_action_human_accountability | PASS |
| traffic | Specify | QA Agent | lifecycle_transition | HiddenDanger lifecycle | State Machines | Can state transitions be converted to tests? | reported -> accepted and rejected return path are present | traffic_specify_qa_lifecycle_transition | PASS |
| traffic | Specify | Coding Agent | acceptance_test_path | prototype/coding contract | UI / Mobile Patterns | Are stable actions and role paths implementable? | data-* and shadow_test_data requirements are visible | shadow_test_data | PASS |
| traffic | Plan | PM Agent | happy_path | special campaign | Core Workflows | Is rollout ownership and campaign scope clear? | scope/deadline/progress/acceptance owners are explicit | traffic_plan_pm_happy_path | PASS |
| traffic | Plan | Domain Expert Agent | exception_path | multi-industry license check | Domain Test Scenarios | Are license union rules planned? | active industries determine required license set | traffic_plan_domain_exception_path | PASS |
| traffic | Plan | Architecture / Data / AI Agent | permission_privacy_path | report indicators | Metric / Indicator Governance | Are metric owners and lineage planned? | indicator owner/source/version/quality are required | traffic_plan_arch_permission_privacy_path | PASS |
| traffic | Plan | QA Agent | lifecycle_transition | ReportTask lifecycle | State Machines | Can QA plan report task state tests? | draft -> completed/failed/cancelled path exists | traffic_plan_qa_lifecycle_transition | PASS |
| traffic | Plan | Coding Agent | acceptance_test_path | delivery manifest | Acceptance Checklist | Can tasks trace to FRR and AC? | source_of_truth_order and manifest are required | source_of_truth_order;manifest.json | PASS |
| traffic | Tasks | PM Agent | happy_path | risk handling | Core Workflows | Are vertical slices tied to business closure? | alert/risk handling task closes with audit | traffic_tasks_pm_happy_path | PASS |
| traffic | Tasks | Domain Expert Agent | exception_path | e-Waybill lifecycle | State Machines | Are domain-specific states sliced correctly? | draft -> completed/rejected/cancelled is explicit | traffic_tasks_domain_exception_path | PASS |
| traffic | Tasks | Architecture / Data / AI Agent | permission_privacy_path | data isolation | Policy / Privacy Constraints | Do tasks preserve province/city/district/enterprise isolation? | isolation applies to UI/API/export/analytics/AI | traffic_tasks_arch_permission_privacy_path | PASS |
| traffic | Tasks | QA Agent | lifecycle_transition | field inspection weak network | Domain Test Scenarios | Are weak-network and idempotent sync tests planned? | local draft and no duplicate result are required | traffic_tasks_qa_lifecycle_transition | PASS |
| traffic | Tasks | Coding Agent | acceptance_test_path | batch operations | UI / Mobile Patterns | Can coding agent implement retry and per-item result? | data-action and acceptance_test_path are traceable | traffic_tasks_coding_acceptance_test_path | PASS |
| traffic | Build/Verify | PM Agent | happy_path | enterprise initialization | Core Workflows | Does build verify usable operational result? | import/exception repair reaches confirmed master data | traffic_build_pm_happy_path | PASS |
| traffic | Build/Verify | Domain Expert Agent | exception_path | standards conflict | Content / Knowledge Assets | Are conflicting standards blocked for owner decision? | conflict and decision owner recorded | standards_corpus_register | PASS |
| traffic | Build/Verify | Architecture / Data / AI Agent | permission_privacy_path | AI recommendation | Policy / Privacy Constraints | Does AI cite rule/model and avoid enforcement write? | AI source/confidence/version visible and non-binding | traffic_build_arch_permission_privacy_path | PASS |
| traffic | Build/Verify | QA Agent | lifecycle_transition | Rectification returned | Domain Test Scenarios | Does regression cover rejected acceptance? | previous evidence immutable and new round created | traffic_build_qa_lifecycle_transition | PASS |
| traffic | Build/Verify | Coding Agent | acceptance_test_path | browser verification | Policy / Privacy Constraints | Can automated tests avoid production pollution? | shadow_test_data and rollback-safe fixtures required | shadow_test_data | PASS |
| traffic | Launch | PM Agent | happy_path | report delivery | Core Workflows | Is launch acceptance evidence frozen? | template/indicator/scope/cutoff snapshot immutable | traffic_launch_pm_happy_path | PASS |
| traffic | Launch | Domain Expert Agent | exception_path | driver fatigue recommendation | Domain Test Scenarios | Are binding interventions human-owned? | AI evidence visible; human decision required | regulated_action_human_accountability | PASS |
| traffic | Launch | Architecture / Data / AI Agent | permission_privacy_path | embedded third-party data | Policy / Privacy Constraints | Are embedded systems subject to same data isolation? | isolation covers embedded pages and AI context | traffic_launch_arch_permission_privacy_path | PASS |
| traffic | Launch | QA Agent | lifecycle_transition | ReportTask launch | State Machines | Can smoke tests verify publish/executing/completed? | launch state path and export are testable | traffic_launch_qa_lifecycle_transition | PASS |
| traffic | Launch | Coding Agent | acceptance_test_path | delivery package | Acceptance Checklist | Can release artifacts guide implementation safely? | all lifecycle, permission, and test markers present | traffic_launch_coding_acceptance_test_path | PASS |
| traffic | Learn/Retire | PM Agent | happy_path | risk dashboard learning | Metric / Indicator Governance | Can post-launch learning improve risk closure? | metrics have owner/version and change history | traffic_learn_pm_happy_path | PASS |
| traffic | Learn/Retire | Domain Expert Agent | exception_path | deprecated standard | Content / Knowledge Assets | Can retired standards be replaced without silent rule drift? | retired/replaced standard version is traceable | standards_corpus_register | PASS |
| traffic | Learn/Retire | Architecture / Data / AI Agent | permission_privacy_path | evidence retention | Policy / Privacy Constraints | Are retention/deletion/export rules explicit? | reports and enforcement evidence retain immutable snapshots | traffic_learn_arch_permission_privacy_path | PASS |
| traffic | Learn/Retire | QA Agent | lifecycle_transition | DataProductRetired equivalent | Acceptance Checklist | Can QA verify no orphaned workflow remains? | lifecycle de-scope and migration evidence required | traffic_learn_qa_lifecycle_transition | PASS |
| traffic | Learn/Retire | Coding Agent | acceptance_test_path | regression suite | Domain Test Scenarios | Can coding agent keep historical AC IDs stable? | acceptance_test_path maps to regression scenarios | traffic_learn_coding_acceptance_test_path | PASS |

## Acceptance Checklist

- [ ] All 14 domain module sections are present.
- [ ] Regulator, inspector, enterprise, driver/personnel, and admin paths are explicit where relevant.
- [ ] Organization and enterprise data isolation is enforced across UI, API, export, analytics, AI, and embedded systems.
- [ ] Enterprise, vehicle, personnel, inspection, hidden-danger, alert, indicator, and report lifecycles are consistent.
- [ ] Regulations, templates, indicators, rules, and AI outputs are versioned and traceable.
- [ ] National, industry, provincial/local, group, and customer-specific
      standards are registered with issuer, region, effective date, status,
      applicability, and product-rule mapping when used.
- [ ] Every binding regulated action has human accountability and audit evidence.
- [ ] Batch, multi-step, mobile weak-network, and exception paths are testable.
