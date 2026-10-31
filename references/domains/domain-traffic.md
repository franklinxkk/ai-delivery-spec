# Domain: Traffic Safety And Road Transport SaaS

Source authority and freshness metadata: `references/domains/domain-sources.yaml`.
Coverage and maturity: `references/domain-coverage.yaml`.

Use this replaceable domain module for 运管、交通监管、道路运输企业安全生产、交通安全 SaaS、两客一危、普货、站场、维修、驾培、租赁、数据集市和指标库产品. A replacement `domain-*.md` must preserve the core section headings used here and in `domain-module-template.md`.

## 中文导读

围绕运输企业、车辆、驾驶员与监管机构，说明资质、安全检查、风险预警、隐患整改和教育培训怎样形成可追溯的业务闭环。适合监管端与企业端协同；行业指标和地方执行规则仍须按项目核实。

常用名称：交通、道路运输、交通安全、运输监管、运管、交通运输、营运车辆。以下中文提示是现有章节的阅读入口，不新增项目规则；需要详细依据时阅读对应原文和来源。

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
- Evaluation Profile
- Acceptance Checklist

> Use only the slices relevant to the project. State arrows and YAML/field lists below are design sketches, not executable schemas or a complete workflow. Instantiate the normal, exception and recovery paths, guards, data owner, permissions and version effects before handoff. A pattern does not override an authorized project decision or create a legal obligation. Where confidence is useful, declare its measurement and limits; do not invent a calibrated score from model self-report.

## Domain Purpose

- Business outcome: make regulated enterprises, vehicles, personnel, qualifications, training, inspections, warnings, hidden dangers, rectification, maintenance, transport operations, and reports visible, assignable, closable, and auditable.
- Product outcome: support both regulator-facing supervision products and enterprise-facing road transport safety/compliance/operation SaaS. Do not collapse these two modes: regulator products emphasize jurisdiction, inspection, evidence, and enforcement boundary; enterprise products emphasize daily execution, low-friction evidence capture, safety responsibility, cost pressure, and adoption.
- Enterprise SaaS outcome: transform old menu-based systems into workflow-driven, industry-adapted, AI-assisted management. The durable product frame is `process transformation -> industry adaptation -> AI upgrade`.
- Chinese trigger aliases: 道路运输九大行业、两客一危、危货运输、驾驶员全生命周期、教学培训、入职流程、人车企资质、双重预防、车辆三检、出车安全告诫、隐患排查整改、流程化改造、行业化适配、AI化升级.
- Primary users: transport regulators, inspectors, enterprise owners/general managers, safety principals, safety managers, fleet/dispatch/maintenance staff, drivers, escorts, station staff, repair shop staff, driving school staff, platform administrators, sales/customer success.
- Illustrative industry segmentation: urban public bus, taxi/ride-hailing, road passenger transport, international road passenger/freight transport, road freight including dangerous goods and network freight, road transport station operation, motor vehicle maintenance, driver training, small passenger car rental. This is a reusable discovery list, not a universal statutory taxonomy or default complete project scope; preserve a project's authorized taxonomy in that project.
- Scenic/tourism transport is an optional scenario slice. Verify its vehicle, road and operating regime before treating it as road passenger transport; select passenger operation, station/source checks, maintenance, training, dispatch, ledgers and daily reports only where the project needs them.
- Sensitive areas: identity documents, employment records, certificates, vehicle location/trajectory, dangerous goods waybills, inspection evidence, training/exam records, enterprise operating data, and safety responsibility evidence.
- AI may optimize: document extraction, certificate recognition, checklist matching, rule verification, risk hints, task generation, evidence completeness checks, training/course matching, rectification summary, management briefing, and customer migration analysis.
- AI must not autonomously decide: punishment, license restriction, final major-hazard classification, final safety responsibility conclusion, forced service suspension, transport qualification revocation, or other binding regulated actions.

### Current Baseline and Change Watch (verified 2026-08-29)

| Evidence class | Current signal | Requirement effect |
|---|---|---|
| binding_baseline | `KS-TRAFFIC-SAFETY-MANAGERS-2024`, `KS-TRAFFIC-PASSENGER-SAFETY-2023`, `KS-TRAFFIC-DANGEROUS-SAFETY-2025`, `KS-TRAFFIC-GOODS-STATION-2026`, existing 2025 inspection and 2026 practitioner/operation rules | resolve enterprise industry, regulated object, jurisdiction, effective date and local implementation before deriving checks, staffing, certificates, warnings or acceptance; keep passenger, freight-station and dangerous-goods applicability/document numbers separate |
| product_pattern | `KS-TRAFFIC-SMART-PILOTS-2026` | learn regional coordination, infrastructure and scenario patterns; never infer that every transport product needs the same cockpit, data scope or integration |
| change_watch | ministry/local rules, inspection-code practices and pilot outputs continue to evolve | re-verify before each regulated baseline; local procurement/news evidence cannot override national rules or customer source systems |

### AI Transformation Horizon

| Axis | From -> toward | Non-negotiable product guard |
|---|---|---|
| work interface | menus/checklists -> role-specific daily safety missions and exception inboxes | every task still links to enterprise/person/vehicle/trip, source time, rule version and accountable owner |
| safety context | fragmented records -> governed person-vehicle-enterprise-operation risk graph | missing/stale/outage data is visible; no fabricated compliance conclusion |
| action | recognition/reminders -> bounded evidence collection, task routing, reconciliation and report drafting | AI may prepare/route; release-to-duty, major-hazard, enforcement and punishment remain authorized human decisions |
| learning loop | alert volume -> false-positive slices, closure quality, recurrence and front-line burden | optimize verified risk closure and adoption, not dashboard activity or notification count |

## First-Principles Domain Lens

Traffic and road transport safety products start from accountable risk closure and operational adoption, not from dashboards alone.

| Lens | Transport Question | Acceptance Signal |
|---|---|---|
| Regulated object | Which enterprise, vehicle, person, license, operation, inspection, danger, or report is governed? | authoritative master, jurisdiction, industry, owner, and data scope are explicit |
| Daily execution | Which front-line behavior actually happens today: onboarding, training, pre-trip warning, trip check, dispatch, repair, inspection, rectification? | workflow state, assignee, deadline, evidence, exception, and retry path are visible |
| Safety closure | What risk or hidden danger moves from detected to rectified/accepted? | state, deadline, evidence, reviewer, audit, and returned-round history are traceable |
| Industry adaptation | Which verified operating category changes fields, checks, certificates, roles, or workflow? | common platform + selected industry template boundary is explicit |
| Scenic operation peak | How do passenger flow, weather, route risk, station checks, vehicle status, and driver readiness affect safe scenic transport today? | peak/holiday plan, low-disruption workflow, risk hint, dispatch relation, and printable ledger are traceable |
| Standards authority | Which national law/policy, GB/GB-T, JT/JT-T/JTG, GA, DBxx/T, group, or customer rule applies? | source register and applicability/conflict status are explicit |
| Human authority | Which enforcement, punishment, license, or safety responsibility decision needs accountable human approval? | AI/rules only suggest; final binding action is human-owned |
| Evidence quality | Can inspection, rectification, alert, training, and report conclusions be replayed? | frozen metrics, evidence refs, signatures, timestamps, and versioned rules exist |
| Adoption economy | Is this workflow simple enough for older drivers and overloaded safety managers? | mobile path, low typing, reminders, batch handling, and exception repair are designed |
| Migration value | How does the new version protect existing revenue while proving upgrade value? | old usage baseline, active customer tiers, urgent debt, pilot scope, and upgrade path are frozen |

## Vocabulary

**中文阅读提示**

**出车安全告诫**（出车告诫、pre-trip safety briefing、pre-departure safety briefing）：出车安全告诫关联驾驶员、车辆和出车任务，确认已阅读与是否具备出车条件分别判断。

**车辆三检**（三检、vehicle trip check、trip check）：区分出车前、行车中、收车后检查的任务与证据；检查时点和适用对象以项目确认的规则为准。

**资质证照**（证件、许可证、营运证、资质到期、qualification、certificate）：区分证照有效性、适用对象与业务许可；临期、过期和未知不可混为正常。

| Term | Meaning | Source Of Truth |
|---|---|---|
| Regulated Enterprise | enterprise within an institution/department supervision scope | enterprise master + org scope |
| Transport Enterprise | operating enterprise using SaaS for safety/compliance/operation management | tenant enterprise master |
| Industry Type | one or more of the road transport industry categories attached to an enterprise | license + business profile + customer confirmation |
| Two-Type Personnel | principal and safety manager requiring safety assessment qualification | personnel/certificate records |
| Driver Lifecycle | recruitment, qualification review, tests, interview, medical/psychological checks, training, internship/probation/substitute, onboarding, post management, resignation | workflow instance + personnel file |
| Escort / Supercargo | dangerous goods transport escort role where applicable | personnel/certificate records |
| Vehicle Trip Check | pre-trip/in-trip/post-trip or enterprise-defined vehicle inspection | check task + evidence |
| Pre-Trip Safety Briefing | safety warning/acknowledgement before dispatch or trip | briefing task + driver acknowledgement |
| Hidden Danger | safety problem requiring rectification and, when applicable, acceptance | hidden-danger aggregate |
| Dual Prevention | risk classification control + hidden-danger investigation/governance | risk rule + inspection/rectification workflows |
| Safety Code / Risk Level | governed enterprise/vehicle/person risk score and color | risk/safety-code service |
| Alert | machine, external platform, or rule-detected risk signal | alert source/event store |
| Safety Inspection | regulator or enterprise-created online/offline inspection with items and evidence | inspection aggregate |
| Rectification | enterprise evidence and action submitted against an issue | rectification record |
| e-Waybill | electronic transport waybill, especially relevant for dangerous goods | waybill/operation system |
| Scenic / Tourism Passenger Transport | passenger transport serving scenic areas, tourism lines, transfer stations, shuttle/sightseeing vehicles, or peak visitor flows | enterprise profile + operation confirmation |
| Shuttle / Sightseeing Vehicle | scenic transfer, shuttle, sightseeing, or tourism passenger vehicle under enterprise operation | vehicle master + dispatch/operation data |
| Source Station Check | station/source-side vehicle, driver, certificate, safety, or release check before operation | station/check system + human confirmation |
| Peak Operation / Holiday Dispatch | planned operating mode for holidays, peak seasons, passenger-flow spikes, weather, and route constraints | operation plan + dispatch records |
| Printable Safety Ledger | online record that can be exported/printed as an auditable management ledger | ledger/report snapshot |
| Qualification / Certificate | enterprise, vehicle, personnel, equipment, business, or industry-specific qualification | certificate registry |
| Indicator | versioned metric with caliber, source, dimensions, owner, and quality rules | indicator registry |
| Report Task | period-specific execution using frozen template/indicator versions | report service |

## Aggregates and Entities

**中文阅读提示**

**车辆**（车牌、车牌号、营运车、vehicle、plate）：车辆识别与企业归属分别描述；车辆转籍或换牌时检查历史证据和当前责任范围。

**运输企业**（道路运输企业、承运企业、车企、transport enterprise）：企业、车辆和驾驶员是不同对象；核对标识、归属和有效时间，不能凭名称合并。

| Aggregate | Owns | Notes |
|---|---|---|
| Enterprise | profile, industries, licenses, responsible persons, signer, district scope | authoritative master data; multi-industry license union |
| IndustryTemplate | required fields, certificates, workflows, checklists, reports, role paths | classify as common, configurable template, or independent module |
| Vehicle | profile, certificates, technical grade, insurance, maintenance, GPS identity, tank/trailer attributes where applicable | often joins enterprise; trajectory remains external/event data |
| Driver/Personnel | employment, post, qualification, training, exams, onboarding state | personal data requires masking and retention rules |
| OnboardingProcess | steps, owners, evidence, exam/test results, approval/return state | use workflow engine when customers need custom step sequences |
| TrainingTask | course, target role, duration, exam, evidence, completion | education is often the adoption entry point; do not confuse content platform with safety SaaS core |
| PreTripBriefing | dispatch relation, briefing content, acknowledgement, exception | mobile-first for drivers |
| VehicleTripCheck | check type, item results, photos/video, fault relation, exception | supports pre-trip/in-trip/post-trip and enterprise variants |
| RiskAssessment | risk score/level, evidence, rule/model version | AI/rule writable with audit; not a punishment decision |
| Rule | source, applicability, condition, action, confidence, effective version | human reviewed before activation |
| Alert | source, object, severity, disposition state | high-volume operational flow |
| SafetyInspection | plan/list, items, evidence, signatures, result | human-owned inspection and classification |
| HiddenDanger | source, level, rectification rounds, acceptance | history is append-only across returned rounds |
| MaintenanceOrder | fault, repair order, parts/service evidence, acceptance | important for repair enterprises and vehicle technical management |
| TransportOperation | dispatch/trip/order/waybill relation, vehicle, driver, route, cargo/passenger context | domain-specific depth varies by industry |
| StationOperation | vehicle entry/exit, ticketing/boarding linkage, station safety checks | road transport station often needs independent module behavior |
| ScenicRoute / ScenicLine | route, station/stop, road risk, weather/geofence context, operating mode | overlay on passenger operation; do not hardcode one scenic area |
| ScenicOperationLedger | online form snapshot, source/check evidence, print/export record, archive state | supports paper-to-online migration while preserving printable archives |
| ScenicPeakPlan | holiday/peak passenger-flow plan, dispatch constraints, staffing, emergency adjustment | used for low-disruption pilot and management briefing |
| DrivingSchoolTraining | trainee, coach, vehicle, class hours, exam link, safety training | driving school often needs independent module behavior |
| EnforcementTask | inspection/rectification/escalation task | binding action requires authorized human approval |
| Indicator | caliber, source, dimensions, owner, version, status | governed reusable metric |
| ReportTemplate | indicators, fill columns, formulas, dimensions | reusable definition |
| ReportTask | period, scope, template snapshot, progress/result | execution record distinct from template |
| MigrationBaseline | customer tier, old modules, usage, ARR/renewal risk, upgrade target | freezes commercial baseline before rebuild |

## Domain Events

```yaml
events:
  EnterpriseIndustryChanged:
    payload: { enterprise_id, industries, source, confirmed_by, changed_at }
  QualificationExpiring:
    payload: { object_type, object_id, certificate_type, expire_at, rule_version }
  DriverOnboardingStepCompleted:
    payload: { process_id, driver_id, step_id, result, evidence_refs, completed_by }
  TrainingCompleted:
    payload: { task_id, person_id, course_id, hours, exam_result, evidence_refs }
  PreTripBriefingAcknowledged:
    payload: { briefing_id, driver_id, vehicle_id, operation_id, acknowledged_at }
  VehicleTripCheckSubmitted:
    payload: { check_id, vehicle_id, driver_id, check_type, result, evidence_refs }
  SourceCheckCompleted:
    payload: { check_id, station_id, vehicle_id, driver_id, result, evidence_refs, completed_by }
  ScenicPeakPlanPublished:
    payload: { plan_id, scope, effective_from, effective_to, published_by }
  PrintableLedgerGenerated:
    payload: { ledger_id, object_type, object_id, snapshot_version, generated_by, generated_at }
  PreventiveMaintenanceReminderGenerated:
    payload: { reminder_id, vehicle_id, source_refs, rule_version, human_required }
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
  AIRecommendationGenerated:
    payload: { recommendation_id, object_type, object_id, rule_refs, confidence, human_required }
  ReportSnapshotFrozen:
    payload: { report_task_id, template_version, metric_versions, cutoff_time }
```

## State Machines

**企业预警**（企业风险预警、enterprise alert、company risk warning）：区分企业级聚合提示与单条预警事件，按对象标识关联并说明去重、统计范围及处置入口；列表汇总不代替单条事件的证据和状态。

Enterprise alert: distinguish an enterprise aggregate from an individual alert event. Relate stable object identifiers, deduplication, statistical scope and disposition entry; a summary does not replace event evidence or state.

**中文阅读提示**

**风险预警**（报警、告警、预警中心、risk alert、warning）：区分风险信号、预警事件与隐患记录；写明触发、重复观察、处置及关闭条件。

```text
OnboardingProcess: draft -> reviewing -> testing -> training -> internship_or_probation -> pending_approval -> active | rejected | archived
TrainingTask: draft -> published -> learning -> exam_pending -> completed | failed | overdue | cancelled
PreTripBriefing: created -> pushed -> acknowledged -> effective | expired | exception_reported
VehicleTripCheck: created -> submitted -> completed (no defect, required evidence valid)
VehicleTripCheck: submitted -> exception_pending -> disposition_recorded -> closed | returned
Fault: created -> assigned -> repairing -> pending_verification -> closed | returned
Fault closure links to the original check; it neither erases its defect evidence nor automatically authorizes release to duty.
ScenicLedger: draft -> in_progress -> submitted -> reviewed -> printable_archived | returned
ScenicPeakPlan: draft -> published -> active -> reviewed -> archived
Alert: created -> pending_review -> assigned -> processing -> closed | escalated
Inspection: draft -> inspecting -> qualified (no issue, authorized confirmation)
Inspection: inspecting -> pending_rectification -> pending_acceptance -> qualified
Inspection: pending_acceptance -> pending_rectification (returned)
HiddenDanger: reported -> rectifying -> pending_acceptance -> accepted
HiddenDanger: pending_acceptance -> rectifying (rejected)
ReportTask: draft -> published -> executing -> completed | failed | cancelled
e-Waybill: draft -> submitted -> reviewed -> in_transport -> completed | rejected | cancelled
CustomerMigration: baseline_frozen -> pilot_selected -> migrated -> adopted -> upgraded | retained_old | churn_risk
```

State consistency:

| Business Concept | Source Of Truth | Consumers | Consistency Need |
|---|---|---|---|
| enterprise status | enterprise master | risk/inspection/report | strong before regulated action |
| industry type | enterprise license + tenant confirmation | templates/workflows/rules | strong before required-rule activation |
| employment and certificate status | personnel/certificate records | onboarding/training/risk/report | strong for release to duty |
| vehicle online state | GPS/monitoring | alert/risk/report | eventual for dashboard |
| license expiry | license facts | alert/report | governed freshness |
| training completion | learning/exam service | personnel/risk/report | strong when used as compliance evidence |
| trip check result | check workflow | dispatch/fault/risk/audit | human-confirmed |
| rectification result | hidden-danger workflow | inspection/risk/report/audit | human-confirmed |
| final report | report snapshot | dashboard/export/submission | immutable snapshot |

## Metric / Indicator Governance

**中文阅读提示**

**分心驾驶**（分心、distracted driving、distraction）：分心报警保留原始证据及复核结果；信号类型和有效性以接入来源确认，不由中文别名生成判定规则。

**超速驾驶**（超速、speeding、overspeed）：超速信号需要对应监测来源及判定条件；不从报警名称推导统一阈值或自动处罚。

**疲劳驾驶**（疲劳、fatigue driving、driver fatigue、fatigue）：疲劳报警是动态监测信号，核对来源、发生时间及主体；信号本身不等于已确认违法或已完成处置。

**安全培训**（学时、月均学时、人均学时、training hours、safety training）：培训时长、完成率和考核结果的主体、周期、单位及缺数口径需可判定。

```yaml
indicator:
  id: string
  name: string
  category: hidden_danger | monitoring | license | training | maintenance | operation | adoption | baseline
  caliber: string
  source: string
  dimensions: [enterprise, district, industry, vehicle_type, person_role, date]
  compute_type: count | distinct | sum | avg | ratio | score | mom | chain
  sql_or_rule: string
  owner: role_or_team
  version: semver
  status: draft | pending_review | active | deprecated
  quality_checks: [source_exists, dimension_join_valid, null_rate_threshold, stale_source_guard]
```

Rules:

- no active indicator without business caliber, owner, source, dimensions, and version;
- distinguish safety result indicators from usage/adoption indicators;
- AI-generated indicators start as draft and require human review;
- final reports freeze template, indicator versions, scope, and cutoff time;
- chart count is not indicator count; semantically identical metrics reuse one definition;
- old-system usage baselines should be frozen before rebuild/migration to avoid losing renewal and upgrade evidence.

Common categories:

| Category | Examples |
|---|---|
| Hidden danger | pending rectification, pending acceptance, first-pass rate, closure rate |
| Dynamic monitoring | speeding/fatigue alerts, unhandled alerts, offline vehicles |
| License | expired enterprise/personnel/vehicle certificates, upcoming expiry, missing qualification |
| Training | pre-job completion, monthly training rate, learning hours, exam pass rate |
| Onboarding | step completion, overdue step, approval cycle time, rejection reason |
| Pre-trip / trip check | briefing acknowledgement, check completion, exception rate, fault closure |
| Maintenance | no plan, overdue, mileage anomaly, provider anomaly |
| Operation | trips/orders/waybills, vehicle dispatch relation, station entry/exit where applicable |
| Scenic / tourism operation | source-check pass rate, printable-ledger completeness, peak dispatch risk hints, route/weather warning acknowledgement |
| Adoption | active enterprises, active modules, depth of module use, zero-use customers, pilot conversion |
| Baseline | enterprises, vehicles, drivers, escorts, safety managers, modules, ARR/renewal cohort |

## AI Context Sources

**中文阅读提示**

**主动安全报警**（主防、主防报警、主动安全预警、active safety alarm、ADAS alarm、active-defense）：定位主动安全或动态监测来源，保留报警主体、时间与来源状态；报警类型不直接赋予处罚或停运权限。

| Context | Source | Freshness | Permission / Reliability Rule |
|---|---|---|---|
| enterprise/industry/license | enterprise master and license records | real-time/daily | org/data scope; authoritative fields identified |
| personnel qualification | employment and certificate records | real-time | identity fields minimized/masked |
| onboarding evidence | workflow forms, exam/test evidence, approvals | real-time | customer-specific workflow version recorded |
| training and exams | learning platform/course/exam service | real-time/daily | distinguish completion, pass, and evidence validity |
| vehicle maintenance/insurance | vehicle and maintenance services | daily/real-time | distinguish missing from expired |
| trip check / pre-trip briefing | mobile mini-program, dispatch relation, check task | real-time | weak-network and late-submission state preserved |
| trajectory and warnings | 809/GPS/active-defense platform | streaming/eventual | retain source timestamp and outage state |
| waybill/operation data | dispatch, station, waybill, network freight, or third-party systems | real-time/eventual | record source ownership and integration gap |
| scenic source checks and ledgers | station/source-check, vehicle release, printable ledger, and archive systems | real-time/daily | human check result and print snapshot remain authoritative |
| passenger-flow and ticketing context | ticketing, reservation, visitor-flow, or dispatch planning systems | real-time/eventual | aggregate where possible; avoid unnecessary personal ticket data |
| OEM / vehicle telematics | vehicle health, energy, mileage, tire temperature, fault, and monitoring data | streaming/daily | advisory for maintenance and dispatch; do not replace human release decision |
| route/weather risk | weather, road condition, geofence, route risk map | real-time/eventual | source time and applicability to route/line are recorded |
| inspection/hidden danger | inspection and rectification records | real-time | signed evidence and human result are authoritative |
| regulations/checklists | approved knowledge base | versioned | cite effective version; no unsupported legal conclusion |
| usage/renewal baseline | product analytics, CRM, billing, customer success records | monthly/quarterly | do not mix usage signal with legal compliance conclusion |

## Content / Knowledge Assets

| Asset | Minimum Metadata | Governance |
|---|---|---|
| laws/regulations | title, issuing authority, effective date, region, version | legal/business review before activation |
| national / industry / local / group standards corpus | standard code, issuer, region, effective date, status, applicability, mapped product rule | versioned register; never assume active without owner review |
| inspection standards/templates | owner institution, applicable industry, version, item/evidence rules | district/customer configuration with audit |
| road transport industry templates | industry, required objects, certificates, workflows, reports, independent-module flag | versioned product owner review |
| scenic transport operation templates | source-check item set, peak operation plan, route risk, station ledger, printable archive | customer-adapted overlay on passenger/station/maintenance templates |
| certificate dictionaries | certificate type, applicable role/industry, validity rule | shared dictionary, versioned |
| training/course content | target role, risk topic, duration, assessment | content review and evidence level |
| scenic transport training content | driver, station, dispatcher, maintenance, and safety manager scenarios | jointly reviewed by domain/content owner; customer-specific materials are marked |
| onboarding workflow templates | steps, role owner, required evidence, pass/fail criteria | customer instance can override with audit |
| AI rule tables | source fields, rule logic, confidence, output action, human confirmation | activate only after domain owner review |
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

Effective-source registry rules, web-verified on 2026-07-06:

- Prefer official sources: National People's Congress / State Council / Ministry of Transport / Ministry of Emergency Management / State Administration for Market Regulation standard platforms / official local government releases.
- Treat legal portals, industry media, training slides, and vendor documents as discovery leads only. Do not activate product rules from them without official source confirmation.
- Record `source_url`, `issuer`, `document_no`, `publish_date`, `effective_date`, `status`, `scope`, `industry`, `rule_owner`, and `last_verified_at` for every law, regulation, standard, checklist, or customer rule.
- Distinguish `law/regulation`, `department rule`, `normative file`, `mandatory national standard`, `recommended standard`, `industry standard`, `local rule`, and `enterprise rule`.
- Before generating compliance conclusions, verify whether a standard is current, superseded, partially replaced, or only recommended. Deprecated vehicle or repair standards must not drive active hard-stop rules.
- When source documents conflict, choose the stricter/applicable rule only after recording the conflict, scope, and human decision owner.

Current regulatory baseline to check before product specification:

| Source Family | Key Current Sources | Product Mapping |
|---|---|---|
| Safety production baseline | `安全生产法`; road transport / urban passenger major accident hidden-danger criteria; transport safety risk and hidden-danger governance files | dual prevention, hidden danger, accountability, audit evidence, major-risk human approval |
| Administrative inspection baseline | `交通运输涉企行政检查标准` and local implementation checklists | inspection templates, item evidence, self-check, regulator/enterprise checklist alignment |
| Enterprise/person/vehicle baseline | `道路运输条例`; `道路运输从业人员管理规定` (2026 revision); `道路运输车辆技术管理规定`; `道路运输车辆动态监督管理办法`; two-type personnel safety assessment measures | enterprise files, two-type personnel, driver/escort qualification, vehicle technical files, dynamic monitoring |
| Passenger and station baseline | `道路旅客运输及客运站管理规定` (2023 revision); `汽车客运站安全生产规范` (2024); passenger/station safety inspection standards | passenger transport, charter/tourism passenger, source station check, station release, station ledger |
| Urban bus and taxi baseline | `城市公共交通条例`; `城市公共汽车和电车客运管理规定`; `巡游出租汽车经营服务管理规定`; `网络预约出租汽车经营服务管理暂行办法`; taxi driver qualification rules | city bus, cruise taxi, ride-hailing, driver scale, platform data gaps, dispatch and service safety |
| Freight and network freight baseline | `道路货物运输及站场管理规定` (2026 revision); network freight / network cargo platform operation rules and service guidance | ordinary freight, freight station, network freight carrier/platform data, waybill/operation relation |
| Dangerous goods baseline | `道路危险货物运输管理规定` (2026 revision); `危险货物道路运输安全管理办法`; `危险货物道路运输企业安全管理规范` (2025); dangerous-goods standard families | driver/escort/vehicle/tank/cargo/e-waybill/checklist/risk task and human release decision |
| Radioactive goods baseline | `放射性物品道路运输管理规定` (2026 revision) | radioactive transport qualification, package/vehicle/personnel evidence, stricter approval and audit |
| International road transport baseline | `国际道路运输管理规定` (2023 revision) | cross-border permits, routes, vehicle/personnel qualification, document validity |
| Maintenance baseline | `机动车维修管理规定` (2023 revision); repair business condition standards; vehicle electronic health archive policies | repair enterprise, maintenance order, technical file, parts/service evidence, vehicle safety closure |
| Driver training baseline | `机动车驾驶员培训管理规定` (2026 revision); `GB/T 30340-2025`; `GB/T 30341-2025` | driving school, trainee/coach/class-hour/exam/training-field lifecycle |
| Vehicle rental baseline | `小微型客车租赁经营服务管理办法`; auto-rental service standards where current | rental enterprise, rental contract, vehicle status, driver/customer relation |
| Scenic/tourism overlay | passenger transport + station/source check + vehicle technical + training + maintenance + peak/holiday operation + local scenic/customer safety rules | scenic shuttle/sightseeing/transfer transport, printable ledgers, safety daily reports, route/weather/passenger-flow risk |

Standard families to map into data fields and rule tables:

| Standard Family | Examples | Product Mapping |
|---|---|---|
| Safety inspection | `JT/T 1482-2023 道路运输安全监督检查规范`; official涉企检查标准 | inspection item library, evidence requirements, issue classification |
| Dangerous goods | `JT/T 617` series dangerous-goods road transport rules; dangerous goods names/classification/vehicle marking standards | cargo classification, package/vehicle/marking/waybill rule matching |
| Vehicle safety and inspection | `GB 7258`; `GB 38900`; vehicle technical management and dynamic monitoring standards | vehicle files, technical status, inspection/maintenance evidence, active-defense/GPS source state |
| Dynamic monitoring and interfaces | `JT/T 794`, `JT/T 796`, `JT/T 808`, `JT/T 809`, active-safety/video alarm standard families where current | GPS/809/active-defense integration, alert source, outage/staleness status |
| Maintenance and repair | current `GB/T 16739` repair business condition series and repair service/technical-file standards | repair enterprise qualification, repair order, service evidence, maintenance closure |
| Driving school | `GB/T 30340-2025`; `GB/T 30341-2025`; training record/exam rules | institution qualification, training field, coach/trainee/class-hour data |
| Passenger station and operation | passenger/station ministerial rules, station safety production norm, station classification/building standards where current | station entry/exit, source release, boarding/security evidence, station risk |
| Service and rental | taxi/ride-hailing/rental service standards where current | service qualification, order/contract evidence, passenger/driver complaint and safety linkage |

Nine-industry adaptation map:

| Industry | Common Platform Fit | Must Watch | Primary Regulatory Mapping |
|---|---|---|---|
| Urban public bus | enterprise/person/vehicle/training/check/risk common base | line/shift/dispatch and public-service operation depth | urban public transport regulation + city bus/electric bus rules + vehicle/dynamic-monitoring standards |
| Taxi / ride-hailing | enterprise/person/vehicle/license/training common base | platform settlement, driver scale, third-party platform data gap | cruise taxi, ride-hailing, taxi-driver qualification, platform data and service rules |
| Road passenger transport | common base + passenger operation template | bus line, charter/tourism, station linkage, driver duty checks | passenger/station rules, station safety norm, vehicle technical and driver qualification rules |
| International road passenger/freight | common base + certificate/waybill/route template | cross-border permits, route/cargo/passenger data quality | international road transport rules + passenger/freight baseline |
| Road freight including dangerous goods and network freight | common base + freight/dangerous-goods template | escort, tank/trailer, e-waybill, cargo attributes, dangerous-goods checklists | freight/station rules, network freight platform rules, dangerous-goods and radioactive goods rules where applicable |
| Road transport station | independent module plus shared enterprise/person/risk base | station flow, entry/exit, boarding/security evidence | passenger/station rules, station safety norm, inspection/checklist standards |
| Motor vehicle maintenance | independent module plus shared enterprise/person/risk base | repair order, parts/service evidence, technical management | maintenance rules, repair business condition standards, vehicle technical-file policies |
| Driver training | independent module plus shared enterprise/person/training base | trainee/coach/class-hour/exam lifecycle | driver training rules, training institution/field standards |
| Small passenger car rental | common base + rental/vehicle template | rental contract, vehicle status, customer/driver relation | small passenger car rental rules and current rental service standards |

Do not promise full nine-industry depth in one P1 release. Use P1 to validate three to four high-value scenarios, then scale templates after rule, workflow, and data contracts are stable.
Scenic/tourism passenger transport should normally stay inside this traffic domain as a cross-template overlay across road passenger transport, station operation, maintenance, training, and operation data. Split it into a separate domain file only if it becomes a standalone product line with its own lifecycle, acceptance package, and routing rules.

## Core Workflows

**安全例会**（安全会议、安全生产例会、safety meeting、regular safety meeting）：分别说明会议安排、参与记录、纪要和后续任务；开会、签到、完成培训与问题闭环是不同结果。会议频次及必到人员以项目依据为准。

Safety meeting: distinguish scheduling, attendance, minutes and follow-up work. Attendance, training completion and issue closure are separate outcomes; use project authority for cadence and required participants.

**安全会议签到**（例会签到、安全例会签到、safety meeting attendance、meeting check-in）：签到关联会议和人员标识，核对重复签到、补录与缺席口径；签到记录不能单独证明实际学习时长或考核通过。

Safety meeting attendance: relate the meeting and person by stable identifiers; define duplicate check-in, corrections and absence. Attendance alone does not establish training duration or an examination pass.

**专家检查**（专家安全检查、expert safety inspection、expert inspection）：区分专家提出的问题、企业整改和有权人员的复核结论；专业建议不自动成为处罚或重大隐患的最终认定。

Expert safety inspection: separate expert observations, enterprise rectification and an authorized review conclusion. An expert recommendation is not automatically a penalty or final major-hazard classification.

**线上检查**（线上安全检查、远程检查、online safety inspection、online inspection、remote inspection）：说明远程核查材料的来源与时点，区分证据不足、未检查与已发现问题；需要现场复核时保留交接和处理结果，不把未上传当合格。

Online inspection: retain the source and time of remote evidence; distinguish insufficient evidence, not inspected and a detected issue. Preserve any handoff for an on-site review; missing uploads do not prove compliance.

**中文阅读提示**

**隐患整改**（隐患、整改闭环、销号、hazard、rectification）：整改、复核和关闭是有责任人的业务动作；拒绝或超期后仍需明确下一步。

1. Enterprise initialization: transport-platform export or customer files -> AI/rule extraction -> validation -> human confirmation -> master-data import -> exception repair.
2. Industry fit: enterprise license/business profile -> industry template selection -> required objects/certificates/workflows/rules -> owner confirmation -> activated customer instance.
3. Driver lifecycle: candidate -> qualification review -> written/road/interview/medical/psychological checks where applicable -> onboarding/training -> internship/probation/substitute -> approval -> active duty -> transfer/resignation/archive.
4. Training and education: target population -> course/task assignment -> learning/exam -> evidence capture -> overdue handling -> compliance report. Treat training as an entry workflow, not the whole product.
5. Qualification management: enterprise/person/vehicle certificate registration -> OCR/import -> validity and missing-item rule check -> reminder/task -> renewal evidence -> audit.
6. Pre-trip safety briefing and vehicle trip check: trigger -> mobile acknowledgement/check -> normal completion or exception disposition -> linked fault/hidden-danger work where needed -> evidence archive; release-to-duty authority remains distinct.
7. Dual prevention: risk source -> risk classification/control measure -> hidden-danger investigation -> rectification task -> acceptance/return -> statistics and report.
8. Dangerous goods sample path: vehicle/driver/escort/cargo/tank/e-waybill/context -> AI/rule pre-check -> missing or conflict item -> human confirmation -> task/stop-risk suggestion -> evidence archive.
9. Safety inspection: create -> execute -> evidence/signatures -> no-issue conclusion or issue/rectification -> enterprise submission where needed -> accept/return -> archive.
10. Special campaign: publish scope/deadline -> enterprises self-check/report -> rectification -> regulator/enterprise progress review -> summary.
11. Report delivery: select/create template -> validate indicators -> create period task -> fill missing fields -> review/return -> freeze/export.
12. Old system migration: freeze usage/ARR/renewal/customer tier baseline -> classify keep/upgrade/retire modules -> pilot customers -> data migration -> adoption tracking -> commercial upgrade.
13. Optional scenic transport pilot: inspect current records -> select the required source/check/maintenance data -> validate the agreed operational flow -> produce the authorized ledger or report -> review exceptions and outcome evidence. Source priority, AI features and benchmark materials remain project choices.

## Role Path Patterns

**中文阅读提示**

**驾驶员**（司机、从业人员、driver）：区分企业安全员、驾驶员和监管人员的读写范围，沿各自入口检查处理结果。

| Level / Role | Data Scope | Allowed Actions | Forbidden Actions |
|---|---|---|---|
| province regulator | cross-city aggregate and authorized drilldown | publish policy, inspect summary, escalate | edit enterprise self-fill records |
| city regulator | city and districts | assign inspection, review progress | bypass district evidence rules without authority |
| district/county regulator | own scoped enterprises | issue notice/inspection/rectification, accept closure | view other districts without authorization |
| inspector | assigned enterprises/tasks | execute items, capture evidence, sign, submit result | alter final evidence after submission |
| enterprise owner / general manager | own enterprise or group | view risk/operation summary, assign responsibility, approve resources | self-certify regulated closure without required role |
| enterprise safety principal | own enterprise/group according to duty | review risk, approve key workflows, receive AI briefing | delegate legal accountability to AI |
| safety manager | own enterprise/department/fleet | maintain data, assign training/check/rectification, submit evidence | view other tenants or erase audit history |
| dispatcher/fleet manager | assigned vehicles/drivers/operations | create operation/check/briefing tasks, handle exceptions | override certificate/qualification hard stop without authority |
| scenic operation / station manager | assigned scenic routes, stations, vehicles, shifts, and ledgers | manage source checks, peak plans, printable ledgers, and exceptions | change safety release or archive evidence without required approval |
| maintenance staff | assigned vehicles/orders | submit fault/repair/evidence and acceptance inputs | close safety hidden danger without reviewer if required |
| station/repair/driving school staff | own industry module data | execute industry-specific tasks | access unrelated industry data by default |
| driver/personnel | own permitted tasks/data | training, exam, acknowledgement, trip check, evidence upload | access enterprise-wide sensitive data |
| platform admin | tenant/config scope | configure templates, dictionaries, roles, rules | inspect personal or trajectory data without authorized support process |
| sales/customer success | customer/adoption scope | view usage baseline, renewal risk, pilot progress | infer legal compliance status from usage alone |

## UI / Mobile Patterns

- enterprise managers need dense operational lists with filters, saved views, scope label, status-driven actions, and export/report paths;
- drivers and older front-line personnel need mobile/mini-program paths with large touch targets, minimal typing, voice/photo upload when useful, clear done/not-done state, and weak-network draft;
- safety managers need today/this-week task boards: expiring certificates, overdue training, unchecked vehicles, unhandled alerts, pending rectification, and report due dates;
- for a selected scenic transport scenario, test whether peak/holiday use, printable ledgers, route/station filters, source-check status or daily reports solve the actual user task before adding them;
- detail drawer/page must show evidence, source, timestamp, rule version, human owner, and audit timeline;
- AI suggestions must show why: matched rule, missing data, confidence, recommended task, and required human confirmation;
- map only when spatial context is central; show stale/offline source state;
- batch actions require selection count, permission guard, confirmation, per-item result, and retry;
- multi-step onboarding, e-waybill, inspection, and rectification flows use step indicators and stable next/back/submit test ids;
- every important prototype action has a visible result and domain result; toast-only safety actions fail;
- embedded third-party pages must not bypass tenant/data-scope and audit rules.

## Policy / Privacy Constraints

**中文阅读提示**

**监管范围**（区县、监管企业、有车企业、属地、regulator supervision）：明确机构及企业范围的来源，核对跨机构、委托和历史归属边界；不由页面筛选替代权限。

- Province/city/district/enterprise/tenant data isolation applies to list, detail, export, statistics, AI context, and embedded third-party pages.
- Identity, phone, certificate, trajectory, dangerous-goods waybill, training/exam, and enforcement evidence follow least access, masking, retention, and audit rules.
- AI recommendations show source, uncertainty, missing context, and rule/model version. A numeric confidence value needs a declared measurement basis and limits; do not invent one when unavailable.
- Punishment, service restriction, major-hazard classification, release-to-duty hard decisions, and closure acceptance require authorized human accountability.
- Test agents use shadow data or rollback-safe fixtures and must not pollute production statistics.
- Reports and enforcement evidence retain immutable snapshots according to approved retention policy.
- Scenic passenger-flow and ticketing context should be aggregated unless personal ticket or identity detail is explicitly required and authorized.
- Standards used by rules, AI answers, templates, inspections, and reports must cite issuer, region, effective date, version/status, and applicability.
- When national, industry, local, group, and enterprise rules conflict, record the conflict and decision owner instead of silently choosing one.
- Usage/adoption analytics may guide product and commercial decisions but must not be presented as legal compliance evidence without domain verification.
- AI may cite and summarize current regulatory sources, but every compliance conclusion, release-to-duty decision, stop-operation suggestion, penalty-facing conclusion, or major-hidden-danger classification must expose source, uncertainty, missing context, and human confirmation owner. Include numeric confidence only where its measurement and limits are defined.
- Industry templates must separate nationally common requirements from provincial/local implementation details and customer-specific safety systems.

## Domain Test Scenarios

| Scenario | Role | Expected Result |
|---|---|---|
| high-risk alert disposition | regulator / safety manager | alert assigned, handled/escalated, evidence and audit visible |
| multi-industry enterprise license check | regulator / enterprise | required license set is the union of active industries |
| two-type personnel certificate expiry | regulator / enterprise | risk shown without deleting personnel; source certificate traceable |
| road passenger safety staffing | regulator / enterprise | required safety-manager count is derived from the current passenger-enterprise rule and verified active vehicle count; threshold/minimum boundaries, source version and local overlay are visible |
| driver onboarding with customer-specific steps | safety manager | workflow instance supports configured steps, evidence, return, and approval |
| training task overdue | safety manager / driver | reminder, overdue state, reassignment, and report impact are visible |
| pre-trip briefing acknowledgement | driver / dispatcher | acknowledgement captured; expired/missing acknowledgement creates exception |
| vehicle trip check under weak network | driver | local draft preserved; idempotent sync; no duplicate check result |
| dangerous goods AI pre-check | safety manager | AI flags missing driver/escort/vehicle/waybill evidence; human confirms action |
| rejected rectification | enterprise / regulator | new rectification round created; previous evidence immutable |
| report task with mixed auto/fill data | regulator / enterprise | progress, fill assignments, frozen result, and export are traceable |
| driver fatigue recommendation | regulator / enterprise | AI evidence visible; binding intervention requires human decision |
| e-Waybill lifecycle | enterprise / regulator | multi-step path and state guards match across PC/mobile |
| road transport station module | station manager | station-specific flow does not get forced into generic vehicle template |
| scenic transport paper ledger to printable archive | scenic station / safety manager | source checks, exceptions, review, print/export snapshot, and archive are traceable |
| scenic peak operation low-disruption pilot | scenic operation manager | peak plan and risk hints run beside existing dispatch flow without breaking production operation |
| maintenance enterprise module | repair shop manager | repair order/evidence path connects to vehicle technical management without leaking other tenant data |
| old customer migration baseline | product / customer success | old usage, module depth, ARR/renewal risk, and upgrade target are frozen before rollout |
| standards applicability conflict | regulator / legal reviewer | GB/industry/local/group/customer rule conflict is recorded with owner decision before activation |

## Cross-Domain Requirement Patterns

- `PAT-PERMISSION-001`: jurisdiction, enterprise, fleet, personnel and shared-link access remain server-authoritative across UI/API/export.
- `PAT-VERSION-COMPATIBILITY-001`: regulation, checklist, training, token and workflow versions preserve historical and in-progress interpretation.
- `PAT-FEDERATED-RECONCILIATION-001`: regulator and enterprise platforms compare overlapping person/vehicle/enterprise records by field or credential, never by silent whole-object overwrite.
- `PAT-METRIC-CALIBER-001`: supervision, learning-time, risk and closure indicators expose source, cutoff, state filter and reproducible formula.

## Evaluation Profile

Domain knowledge is not execution evidence. Register coverage and maturity in
`references/domain-coverage.yaml`; keep behavioral scenarios and run evidence
outside this knowledge file.

Before raising maturity, independently evaluate:

- one primary happy path;
- one validation or exception path;
- one permission/privacy path;
- one lifecycle transition;
- one coding-agent no-guess handoff path;
- applicable migration, integration-failure, AI, and high-risk human-gate paths.

Record executor, input, environment, timestamp, result, and evidence location.
Mocked matrices and simulated reviewers cannot satisfy expert review or audit.

## Acceptance Checklist

- [ ] Relevant domain slices and their applicability are explicit; the pack structure is not a mandatory PRD outline.
- [ ] Regulator-facing and enterprise-facing product modes are separated where relevant.
- [ ] Selected operating categories and their authoritative basis are explicit, with common platform, configurable template and independent module boundaries.
- [ ] If scenic/tourism transport is in scope, its applicable operating regime and selected workflow are verified; excluded modules and optional benchmark output do not become acceptance requirements.
- [ ] Enterprise, vehicle, personnel, qualification, training, onboarding, trip check, warning, inspection, hidden-danger, alert, indicator, and report lifecycles are consistent.
- [ ] Driver/personnel mobile paths are low-friction and testable for older/low-literacy users.
- [ ] Organization, jurisdiction, enterprise, tenant, and role data isolation is enforced across UI, API, export, analytics, AI, and embedded systems.
- [ ] Regulations, templates, indicators, rules, and AI outputs are versioned and traceable.
- [ ] Laws, regulations, standards, inspection items, and AI rule tables record official source URL, issuer, document number, effective date, status, scope, last verification date, and human owner.
- [ ] National, industry, provincial/local, group, and customer-specific standards are registered with issuer, region, effective date, status, applicability, and product-rule mapping when used.
- [ ] In-scope industry templates map to the applicable regulatory baseline before generating regulated rules, checklists or AI compliance conclusions.
- [ ] Road passenger and dangerous-goods safety-management rules keep their applicability, document numbers and staffing/check logic separate.
- [ ] Every binding regulated or safety-responsibility action has human accountability and audit evidence.
- [ ] AI behavior is classified as extraction, rule matching, recommendation, drafting, or decision support; binding decisions remain human-owned.
- [ ] Batch, multi-step, mobile weak-network, custom workflow, and exception paths are testable.
- [ ] Old-system usage, renewal, customer tier, and migration baseline are frozen before major rebuild/migration plans.
