# Domain: Traffic Safety And Road Transport SaaS

Source authority and freshness metadata: `references/domain-sources.yaml`.
Coverage and maturity: `references/domain-coverage.yaml`.

Use this replaceable domain module for 运管、交通监管、道路运输企业安全生产、交通安全 SaaS、两客一危、普货、站场、维修、驾培、租赁、数据集市和指标库产品. A replacement `domain-*.md` must preserve the same 15 section headings used here and in `domain-module-template.md`.

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

## Domain Purpose

- Business outcome: make regulated enterprises, vehicles, personnel, qualifications, training, inspections, warnings, hidden dangers, rectification, maintenance, transport operations, and reports visible, assignable, closable, and auditable.
- Product outcome: support both regulator-facing supervision products and enterprise-facing road transport safety/compliance/operation SaaS. Do not collapse these two modes: regulator products emphasize jurisdiction, inspection, evidence, and enforcement boundary; enterprise products emphasize daily execution, low-friction evidence capture, safety responsibility, cost pressure, and adoption.
- Enterprise SaaS outcome: transform old menu-based systems into workflow-driven, industry-adapted, AI-assisted management. The durable product frame is `process transformation -> industry adaptation -> AI upgrade`.
- Chinese trigger aliases: 道路运输九大行业、两客一危、危货运输、驾驶员全生命周期、教学培训、入职流程、人车企资质、双重预防、车辆三检、出车安全告诫、隐患排查整改、流程化改造、行业化适配、AI化升级.
- Primary users: transport regulators, inspectors, enterprise owners/general managers, safety principals, safety managers, fleet/dispatch/maintenance staff, drivers, escorts, station staff, repair shop staff, driving school staff, platform administrators, sales/customer success.
- Road transport industry coverage: urban public bus, taxi/ride-hailing, road passenger transport, international road passenger/freight transport, road freight including dangerous goods and network freight, road transport station operation, motor vehicle maintenance, driver training, small passenger car rental.
- Scenic/tourism passenger transport is a road-passenger overlay, not a separate base domain: combine passenger operation, station/source checks, maintenance, driver/personnel training, dispatch/passenger-flow context, printable ledgers, and safety daily reports.
- Sensitive areas: identity documents, employment records, certificates, vehicle location/trajectory, dangerous goods waybills, inspection evidence, training/exam records, enterprise operating data, and safety responsibility evidence.
- AI may optimize: document extraction, certificate recognition, checklist matching, rule verification, risk hints, task generation, evidence completeness checks, training/course matching, rectification summary, management briefing, and customer migration analysis.
- AI must not autonomously decide: punishment, license restriction, final major-hazard classification, final safety responsibility conclusion, forced service suspension, transport qualification revocation, or other binding regulated actions.

## First-Principles Domain Lens

Traffic and road transport safety products start from accountable risk closure and operational adoption, not from dashboards alone.

| Lens | Transport Question | Acceptance Signal |
|---|---|---|
| Regulated object | Which enterprise, vehicle, person, license, operation, inspection, danger, or report is governed? | authoritative master, jurisdiction, industry, owner, and data scope are explicit |
| Daily execution | Which front-line behavior actually happens today: onboarding, training, pre-trip warning, trip check, dispatch, repair, inspection, rectification? | workflow state, assignee, deadline, evidence, exception, and retry path are visible |
| Safety closure | What risk or hidden danger moves from detected to rectified/accepted? | state, deadline, evidence, reviewer, audit, and returned-round history are traceable |
| Industry adaptation | Which of the nine road transport industries changes required fields, checks, certificates, roles, or workflow? | common platform + industry template boundary is explicit |
| Scenic operation peak | How do passenger flow, weather, route risk, station checks, vehicle status, and driver readiness affect safe scenic transport today? | peak/holiday plan, low-disruption workflow, risk hint, dispatch relation, and printable ledger are traceable |
| Standards authority | Which national law/policy, GB/GB-T, JT/JT-T/JTG, GA, DBxx/T, group, or customer rule applies? | source register and applicability/conflict status are explicit |
| Human authority | Which enforcement, punishment, license, or safety responsibility decision needs accountable human approval? | AI/rules only suggest; final binding action is human-owned |
| Evidence quality | Can inspection, rectification, alert, training, and report conclusions be replayed? | frozen metrics, evidence refs, signatures, timestamps, and versioned rules exist |
| Adoption economy | Is this workflow simple enough for older drivers and overloaded safety managers? | mobile path, low typing, reminders, batch handling, and exception repair are designed |
| Migration value | How does the new version protect existing revenue while proving upgrade value? | old usage baseline, active customer tiers, urgent debt, pilot scope, and upgrade path are frozen |

## Vocabulary

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

```text
OnboardingProcess: draft -> reviewing -> testing -> training -> internship_or_probation -> pending_approval -> active | rejected | archived
TrainingTask: draft -> published -> learning -> exam_pending -> completed | failed | overdue | cancelled
PreTripBriefing: created -> pushed -> acknowledged -> effective | expired | exception_reported
VehicleTripCheck: created -> submitted -> exception_pending -> fault_created -> closed | returned
ScenicLedger: draft -> in_progress -> submitted -> reviewed -> printable_archived | returned
ScenicPeakPlan: draft -> published -> active -> reviewed -> archived
Alert: created -> pending_review -> assigned -> processing -> closed | escalated
Inspection: draft -> inspecting -> pending_rectification -> pending_acceptance -> qualified
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

1. Enterprise initialization: transport-platform export or customer files -> AI/rule extraction -> validation -> human confirmation -> master-data import -> exception repair.
2. Industry fit: enterprise license/business profile -> industry template selection -> required objects/certificates/workflows/rules -> owner confirmation -> activated customer instance.
3. Driver lifecycle: candidate -> qualification review -> written/road/interview/medical/psychological checks where applicable -> onboarding/training -> internship/probation/substitute -> approval -> active duty -> transfer/resignation/archive.
4. Training and education: target population -> course/task assignment -> learning/exam -> evidence capture -> overdue handling -> compliance report. Treat training as an entry workflow, not the whole product.
5. Qualification management: enterprise/person/vehicle certificate registration -> OCR/import -> validity and missing-item rule check -> reminder/task -> renewal evidence -> audit.
6. Pre-trip safety briefing and vehicle trip check: dispatch or task trigger -> mobile acknowledgement/check -> exception capture -> fault/hidden-danger relation -> closure and evidence archive.
7. Dual prevention: risk source -> risk classification/control measure -> hidden-danger investigation -> rectification task -> acceptance/return -> statistics and report.
8. Dangerous goods sample path: vehicle/driver/escort/cargo/tank/e-waybill/context -> AI/rule pre-check -> missing or conflict item -> human confirmation -> task/stop-risk suggestion -> evidence archive.
9. Safety inspection: create -> field/online execution -> evidence/signatures -> classify issue -> issue rectification -> enterprise submission -> accept/return -> archive.
10. Special campaign: publish scope/deadline -> enterprises self-check/report -> rectification -> regulator/enterprise progress review -> summary.
11. Report delivery: select/create template -> validate indicators -> create period task -> fill missing fields -> review/return -> freeze/export.
12. Old system migration: freeze usage/ARR/renewal/customer tier baseline -> classify keep/upgrade/retire modules -> pilot customers -> data migration -> adoption tracking -> commercial upgrade.
13. Scenic transport safety pilot: paper ledger/system exports -> field/form standardization -> P0 source connection (active-defense/GPS, source check, maintenance) -> printable ledger -> safety daily report -> driver/training/maintenance recommendations -> human review -> benchmark material.

## Role Path Patterns

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
- scenic transport pilots need low-disruption peak/holiday mode, printable ledger export, route/station filters, source-check status, and management daily-report entry points;
- detail drawer/page must show evidence, source, timestamp, rule version, human owner, and audit timeline;
- AI suggestions must show why: matched rule, missing data, confidence, recommended task, and required human confirmation;
- map only when spatial context is central; show stale/offline source state;
- batch actions require selection count, permission guard, confirmation, per-item result, and retry;
- multi-step onboarding, e-waybill, inspection, and rectification flows use step indicators and stable next/back/submit test ids;
- every important prototype action has a visible result and domain result; toast-only safety actions fail;
- embedded third-party pages must not bypass tenant/data-scope and audit rules.

## Policy / Privacy Constraints

- Province/city/district/enterprise/tenant data isolation applies to list, detail, export, statistics, AI context, and embedded third-party pages.
- Identity, phone, certificate, trajectory, dangerous-goods waybill, training/exam, and enforcement evidence follow least access, masking, retention, and audit rules.
- AI recommendation shows source, confidence, missing context, and rule/model version.
- Punishment, service restriction, major-hazard classification, release-to-duty hard decisions, and closure acceptance require authorized human accountability.
- Test agents use shadow data or rollback-safe fixtures and must not pollute production statistics.
- Reports and enforcement evidence retain immutable snapshots according to approved retention policy.
- Scenic passenger-flow and ticketing context should be aggregated unless personal ticket or identity detail is explicitly required and authorized.
- Standards used by rules, AI answers, templates, inspections, and reports must cite issuer, region, effective date, version/status, and applicability.
- When national, industry, local, group, and enterprise rules conflict, record the conflict and decision owner instead of silently choosing one.
- Usage/adoption analytics may guide product and commercial decisions but must not be presented as legal compliance evidence without domain verification.
- AI may cite and summarize current regulatory sources, but every compliance conclusion, release-to-duty decision, stop-operation suggestion, penalty-facing conclusion, or major-hidden-danger classification must expose source, confidence, missing context, and human confirmation owner.
- Industry templates must separate nationally common requirements from provincial/local implementation details and customer-specific safety systems.

## Domain Test Scenarios

| Scenario | Role | Expected Result |
|---|---|---|
| high-risk alert disposition | regulator / safety manager | alert assigned, handled/escalated, evidence and audit visible |
| multi-industry enterprise license check | regulator / enterprise | required license set is the union of active industries |
| two-type personnel certificate expiry | regulator / enterprise | risk shown without deleting personnel; source certificate traceable |
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

- [ ] All 15 domain module sections are present.
- [ ] Regulator-facing and enterprise-facing product modes are separated where relevant.
- [ ] Road transport nine-industry scope is explicit, with common platform, configurable template, and independent module boundaries.
- [ ] Scenic/tourism transport overlays identify source checks, passenger-flow/dispatch context, route/weather risk, maintenance prevention, role training, printable ledgers, AI human-review boundaries, and benchmark output without hardcoding one customer.
- [ ] Enterprise, vehicle, personnel, qualification, training, onboarding, trip check, warning, inspection, hidden-danger, alert, indicator, and report lifecycles are consistent.
- [ ] Driver/personnel mobile paths are low-friction and testable for older/low-literacy users.
- [ ] Organization, jurisdiction, enterprise, tenant, and role data isolation is enforced across UI, API, export, analytics, AI, and embedded systems.
- [ ] Regulations, templates, indicators, rules, and AI outputs are versioned and traceable.
- [ ] Laws, regulations, standards, inspection items, and AI rule tables record official source URL, issuer, document number, effective date, status, scope, last verification date, and human owner.
- [ ] National, industry, provincial/local, group, and customer-specific standards are registered with issuer, region, effective date, status, applicability, and product-rule mapping when used.
- [ ] Nine-industry templates map to the current regulatory baseline before PRD, prototype, rule-engine, checklist, or AI answer generation.
- [ ] Every binding regulated or safety-responsibility action has human accountability and audit evidence.
- [ ] AI behavior is classified as extraction, rule matching, recommendation, drafting, or decision support; binding decisions remain human-owned.
- [ ] Batch, multi-step, mobile weak-network, custom workflow, and exception paths are testable.
- [ ] Old-system usage, renewal, customer tier, and migration baseline are frozen before major rebuild/migration plans.
