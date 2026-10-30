# Domain: Medical / Hospital IT

Source authority and freshness metadata: `references/domains/domain-sources.yaml`.
Coverage and maturity: `references/domain-coverage.yaml`.

Use this file for hospital information systems, clinical workflow, internet
hospital, medical quality and safety, medical data governance, research data,
and AI-assisted medical operations.

This is a replaceable domain module. Public protocol files must stay
domain-neutral.

This module is not medical, legal, or regulatory advice. Any medical safety
claim, retention period, device-classification decision, internet-diagnosis
rule, cross-border data rule, or local policy threshold must be verified against
the latest official source and the hospital's accountable governance owner
before PRD signoff.

## 中文导读

覆盖患者与就诊、医嘱、检验检查、病历、结算和医疗数据交换。重点是患者身份、临床责任、状态回执和敏感数据授权；软件流程不能替代医疗判断。

常用名称：医疗、医院、医疗信息化、院内系统、HIS、EMR。以下中文提示是现有章节的阅读入口，不新增项目规则；需要详细依据时阅读对应原文和来源。

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

- Business outcome: improve clinical, nursing, quality, infection-control,
  patient-service, research, and hospital-management workflows while preserving
  patient safety, medical accountability, and traceable evidence.
- Primary users: outpatient/inpatient doctor, nurse, pharmacist, technician,
  imaging doctor, lab doctor, medical-record coder, quality manager, infection
  control staff, department director, hospital administrator, researcher,
  patient, family member, and platform operator.
- Regulated or sensitive areas: diagnosis, prescription, order execution,
  medical record signing, critical-value handling, infection control, payment,
  medical insurance, patient identity, consent, privacy, research data, and AI
  decision support.
- AI may optimize: summarization, extraction, coding suggestion, triage draft,
  risk reminder, quality-rule detection, imaging/lab pre-analysis, patient
  education draft, research cohort screening, and operation dashboard insight.
- AI must not decide automatically: final diagnosis, prescription, treatment
  plan, surgery decision, discharge decision, medical-record signing, research
  data release, patient punishment, payment settlement, or any irreversible
  clinical/legal outcome.
- Out of scope unless explicitly requested: medical device hardware design,
  pharmaceutical manufacturing, insurance claim adjudication independent of
  hospital workflow, and public-health command systems outside hospital IT.

### Current Baseline and Change Watch (verified 2026-08-29)

| Evidence class | Current signal | Requirement effect |
|---|---|---|
| binding_baseline | `KS-MEDICAL-AI-PLUS-2025`, `KS-MEDICAL-MUTUAL-RECOGNITION-2024`, `KS-MEDICAL-TERTIARY-EVAL-2025` | declare clinical owner, applicable institution/scope, data quality, negative/exception list, human judgment, AI safety, trace and local implementation before deriving scope or acceptance |
| design_guidance | `KS-MEDICAL-THREE-IN-ONE-2025` and the published smart-service/clinical/management evaluation tracks | retain track-specific evidence and cross-system data lineage; do not collapse evaluation semantics without an official replacement |
| change_watch | market discussion reports a possible “digital-intelligent hospital” consolidated evaluation transition but cites no publicly accessible replacement standard | for 2026-2027 projects, preserve adaptable evidence mapping and re-check NHC sources; “four-in-one is mandatory” is prohibited until a primary source is verified |

### AI Transformation Horizon

| Axis | From -> toward | Non-negotiable product guard |
|---|---|---|
| clinical work | isolated model output -> longitudinal, multimodal clinical copilot embedded in encounter workflow | patient/encounter identity, source provenance, indication, uncertainty and clinician sign-off are explicit |
| patient service | generic Q&A -> navigation, preparation, follow-up and chronic-care support agents | emergency/escalation path, consent, accessibility and human service fallback remain visible |
| hospital operation | retrospective reports -> bounded quality, capacity, supply and mutual-recognition orchestration | AI cannot silently change orders, reports, charges or clinical responsibility; integration is reversible and audited |
| evidence loop | aggregate accuracy -> clinical utility, harmful-error slices, override, drift and patient outcome evidence | simulated/static PASS never proves clinical safety, device status or regulatory acceptance |

## First-Principles Domain Lens

Medical/hospital IT product judgment starts from patient safety, accountable
clinical workflow, and legally traceable evidence.

| Lens | Hospital Question | Acceptance Signal |
|---|---|---|
| Clinical object | Which patient, encounter, order, record, report, prescription, quality issue, or research dataset changes? | source system, encounter scope, and responsible role are explicit |
| Safety state | What transition proves care, review, execution, acknowledgement, or closure happened safely? | state guard, signer/reviewer, timestamp, and audit are traceable |
| Authority boundary | Which hospital policy, national/local regulation, clinical guideline, consent, insurance, or research rule applies? | accountable owner and verified source status are recorded |
| Human gate | Which diagnosis, prescription, discharge, signature, settlement, or data-release decision cannot be automated? | AI output remains draft/evidence until authorized human confirmation |
| Failure recovery | What happens on critical value, contraindication, identity mismatch, downtime, or AI disagreement? | escalation, fallback, rollback/amendment, and patient-safety evidence exist |

## Vocabulary

| Term | Meaning | Source of Truth |
|---|---|---|
| HIS | hospital information system for registration, charging, inpatient/outpatient operations | hospital HIS |
| EMR | electronic medical record used for clinical documentation and signing | EMR system |
| CDR | clinical data repository integrating longitudinal clinical data | data platform / CDR |
| MPI | master patient index for patient identity matching | master data platform |
| LIS | laboratory information system | LIS |
| PACS | picture archiving and communication system | PACS |
| RIS | radiology information system for imaging workflow | RIS |
| NIS | nursing information system | NIS |
| CIS / CDSS | clinical information / clinical decision support system | clinical platform |
| QMS | medical quality management system | quality office system |
| Infection Control | healthcare-associated infection monitoring and intervention workflow | infection-control system |
| Internet Hospital | online follow-up, consultation, prescription, and patient service surface | internet hospital platform |
| CA Signature | legally accountable electronic signature for clinical/legal documents | CA/signature service |
| Critical Value | lab/imaging result requiring urgent acknowledgement and handling | LIS/RIS/QMS |
| DRG / DIP | diagnosis-related / disease-based payment and management model | insurance/operation system |
| AI Recommendation | non-binding machine-generated suggestion, extraction, or classification | AI service trace |
| Human Gate | accountable clinician/manager confirmation before consequential write/publish | workflow/audit system |

## Aggregates and Entities

**中文阅读提示**

**患者身份**（病人、患者、就诊人、patient、patient identity）：区分自然人、就诊记录和住院记录，核对合并身份及重复登记后的数据归属。

| Aggregate | Owns | Key States | Notes |
|---|---|---|---|
| Patient | identity, MPI link, demographics, contact, consent | active / merged / archived / restricted | patient identity must be deduplicated and auditable |
| Encounter | outpatient visit, inpatient admission, department, attending team | registered / in_consultation / admitted / completed / archived | scope for most clinical records and orders |
| ClinicalOrder | medication, lab, imaging, treatment, nursing order | draft / submitted / verified / executed / stopped / cancelled | execution requires role and department authority |
| MedicalRecord | note, diagnosis, procedure, discharge summary, amendment | draft / submitted / signed / archived / amended | signed records need versioned amendment, not silent overwrite |
| LabReport | specimen, test item, result, critical value, reviewer | sample_collected / tested / reviewed / published / acknowledged | critical values require closed-loop acknowledgement |
| ImagingStudy | request, image, AI pre-analysis, report, signature | requested / acquired / ai_analyzed / radiologist_reviewed / signed / published | AI output is draft evidence, not final report |
| Prescription | drug items, dosage, review, dispensing | draft / doctor_signed / pharmacist_reviewed / dispensed / cancelled | pharmacist review and contraindication handling are explicit |
| QualityEvent | defect, rule, owner, rectification, evidence | detected / assigned / rectifying / verified / closed | includes medical quality, record quality, and safety issues |
| InfectionAlert | patient, pathogen/risk, department, isolation/reminder action | detected / notified / acknowledged / resolved | must not create clinical orders automatically unless policy allows |
| ResearchDataRequest | cohort condition, data scope, approval, export package | applied / ethics_approved / data_committee_approved / desensitized / delivered / closed | research data release must be approved and traceable |
| AIInferenceRecord | input reference, model, prompt/version, output, confidence, reviewer | generated / shown / accepted / modified / rejected / suppressed | required for medical AI audit and regression |

## Domain Events

```yaml
events:
  PatientMatched:
    payload: { patient_id, mpi_id, match_rule, operator_id, matched_at }
  EncounterCreated:
    payload: { encounter_id, patient_id, department_id, encounter_type, created_at }
  ClinicalOrderSubmitted:
    payload: { order_id, encounter_id, order_type, doctor_id, submitted_at }
  ClinicalOrderExecuted:
    payload: { order_id, executor_id, execution_time, evidence_ref }
  MedicalRecordSigned:
    payload: { record_id, encounter_id, signer_id, signature_evidence_id, signed_at }
  LabCriticalValuePublished:
    payload: { report_id, patient_id, item_code, value, published_at }
  CriticalValueAcknowledged:
    payload: { report_id, ack_user_id, action_taken, ack_at }
  ImagingReportSigned:
    payload: { study_id, report_id, radiologist_id, signature_evidence_id, signed_at }
  PrescriptionReviewed:
    payload: { prescription_id, pharmacist_id, result, issue_codes, reviewed_at }
  QualityIssueDetected:
    payload: { issue_id, rule_id, object_type, object_id, severity, detected_at }
  InfectionAlertRaised:
    payload: { alert_id, patient_id, department_id, risk_type, raised_at }
  ResearchDataApproved:
    payload: { request_id, approver_id, scope, approved_at }
  AIRecommendationReviewed:
    payload: { ai_record_id, reviewer_id, decision, reason, reviewed_at }
```

## State Machines

**中文阅读提示**

**医嘱执行**（医嘱、处方、开单、order、prescription）：下达、审核、执行、撤销与回执状态分别判断，执行过的动作不能仅删除界面记录。

```text
Encounter: registered -> in_consultation -> completed -> archived
Encounter: registered -> admitted -> completed -> archived

MedicalRecord: draft -> submitted -> signed -> archived
MedicalRecord: archived -> amended -> signed -> archived

ClinicalOrder: draft -> submitted -> verified -> executed
ClinicalOrder: submitted | verified -> stopped | cancelled

LabReport: sample_collected -> tested -> reviewed -> published
LabReport: published -> critical_value_acknowledged

ImagingStudy: requested -> acquired -> ai_analyzed -> radiologist_reviewed -> signed -> published
ImagingStudy: requested -> acquired -> radiologist_reviewed -> signed -> published

Prescription: draft -> doctor_signed -> pharmacist_reviewed -> dispensed
Prescription: doctor_signed | pharmacist_reviewed -> cancelled

QualityEvent: detected -> assigned -> rectifying -> verified -> closed
InfectionAlert: detected -> notified -> acknowledged -> resolved
ResearchDataRequest: applied -> applicability_reviewed -> ethics_cleared -> data_use_approved -> prepared -> delivered -> closed
Ethics clearance records approval or a documented applicable exemption; the institution defines the accountable review authority, not necessarily a body named data committee.
AIRecommendation: generated -> shown_to_clinician -> accepted | modified | rejected
AIRecommendation: generated -> suppressed_low_confidence | suppressed_policy_block
```

State rules:

- A signed clinical artifact cannot be silently edited. Amendments must retain
  old content, new content, reason, signer, time, and audit trail.
- AI output cannot skip a required human gate. If model confidence, source
  freshness, or permission scope is insufficient, suppress the recommendation
  or route to manual review.
- Critical value, infection alert, and quality issue flows must include owner,
  acknowledgement, deadline, escalation, and closure evidence.

## Metric / Indicator Governance

| Indicator | Subject | Source | Minimum Governance |
|---|---|---|---|
| outpatient waiting time | encounter / department | HIS / queue system | caliber, sampling window, abnormal exclusion |
| bed turnover and occupancy | ward / department | HIS / inpatient system | source freshness and department attribution |
| critical value acknowledgement SLA | report / department | LIS/RIS/QMS | time from publish to acknowledgement, overdue rule |
| medical record completion rate | record / department | EMR | signed/archived denominator, overdue definition |
| prescription review issue rate | prescription / doctor / department | pharmacy system | issue taxonomy and appeal path |
| infection alert closure rate | alert / department | infection-control system | closure evidence and recurrence tracking |
| AI recommendation adoption rate | AI record / scenario | AI trace + business system | acceptance/modification/rejection must be separated |
| AI false-positive / false-negative review | scenario / model version | golden set + human review | reviewer, sample size, threshold, severity |
| research data request cycle time | request | research data platform | approval, desensitization, delivery timestamps |

Every dashboard/report must state subject, source system, refresh frequency,
permission scope, empty/error state, denominator, exclusion rule, and owner.

## AI Context Sources

| Source | Typical Use | Permission / Safety Rule |
|---|---|---|
| EMR / medical record | summary, quality detection, clinical context retrieval | encounter/department scope; signed content is source evidence |
| HIS encounter/order/payment data | workflow context and operation indicators | role and department data scope required |
| LIS reports | lab interpretation aid and critical-value detection | critical value must be confirmed by accountable staff |
| PACS/RIS images and reports | imaging pre-analysis, report draft, comparison | final report requires radiologist review/signature |
| NIS nursing records | nursing risk reminder and care-plan context | nurse role scope and shift handoff audit |
| QMS / infection-control rules | quality and infection alerts | rule owner and latest approved rule version required |
| Guidelines / pathway knowledge base | non-binding suggestion and patient education draft | version/date/source must be visible; outdated source cannot be used silently |
| Legal basis, patient consent and authorization | purpose-specific privacy and service boundary | verify the lawful basis; check consent where legally required and the permitted purpose/fields in every case |
| Research cohort/data mart | research screening and extraction | applicable ethics clearance, institutional data-use approval, required privacy treatment and export audit |

Context-source contract:

```yaml
medical_ai_context_source:
  source_id:
  owner_system:
  data_scope:
  freshness_sla:
  permission_check:
  patient_consent_required: true | false
  clinical_signoff_required: true | false
  prohibited_use:
  audit_fields: [trace_id, user_id, role_id, patient_id_or_hash, source_version, used_at]
```

## Content / Knowledge Assets

**中文阅读提示**

**电子病历**（病历、病案、EMR、electronic medical record）：病历草稿、签署、归档及更正的责任和读取范围不同，不能把保存当签署。

| Asset | Use | Governance |
|---|---|---|
| clinical guidelines and pathways | CDSS, patient education, record review | approved version, effective date, owner department |
| hospital rules and SOPs | quality, nursing, infection-control workflow | hospital owner and change history |
| medical terminology / code set | ICD, procedure, diagnosis, drug, lab item mapping | versioned dictionary and mapping owner |
| patient education content | internet hospital and discharge follow-up | clinical review, target population, disclaimer |
| AI prompt / model registry | extraction, summary, coding, risk suggestion | golden cases, model/prompt version, rollback owner |
| de-identification rules | research and data export | privacy owner, irreversible/reversible rule, audit proof |

## Core Workflows

**中文阅读提示**

**检验检查**（化验、检查报告、检验报告、laboratory、diagnostic）：申请、采样、执行、结果审核与发布须保持对象一致，迟到或更正结果保留来源。

**医疗结算**（医保、费用结算、退费、billing、settlement）：收费、支付、退费与结算回执分别说明，失败及未知结果避免重复扣费。

| Workflow | Happy Path | Required Exceptions |
|---|---|---|
| Outpatient visit | register -> consult -> order/prescription -> payment/execution -> record sign -> complete | patient mismatch, duplicate encounter, permission denial, unfinished record, payment dependency |
| Inpatient care | admission -> orders/nursing -> results -> daily record -> discharge -> archive | order conflict, critical value, transfer, operation, overdue record, discharge summary incomplete |
| Imaging AI assistance | order -> image acquisition -> AI pre-analysis -> radiologist review -> report sign -> publish | AI timeout, low confidence, conflicting prior report, radiologist rejection, delayed signature |
| Critical value loop | report publish -> notify owner -> acknowledge -> action/evidence -> close | unreachable owner, overdue acknowledgement, false alert, escalation |
| Internet follow-up | patient request -> identity/consent -> doctor review -> prescription/education -> payment/delivery | first-visit prohibition where applicable, unsupported disease, missing consent, refund/cancellation |
| Quality issue management | rule detection/manual issue -> assign -> rectify -> verify -> close | disputed issue, overdue rectification, repeated defect, department transfer |
| Infection alert handling | risk detected -> notify -> acknowledge -> isolate/intervene -> resolve | policy block, false positive, cross-department patient transfer |
| Research data request | apply -> ethics applicability/clearance -> data-use approval -> required privacy treatment -> deliver -> audit close | unsupported exemption, missing required approval, excessive scope, re-identification risk, export failure |

## Role Path Patterns

| Role | Typical Path | Must Be Explicit |
|---|---|---|
| Doctor | patient list -> encounter detail -> record/order/prescription -> sign -> follow-up | department scope, patient identity, unsigned draft, AI suggestion review |
| Nurse | ward list -> patient detail -> nursing task -> execution evidence -> handoff | shift, executor, time, evidence, exception escalation |
| Pharmacist | prescription queue -> review -> pass/return/intervene -> audit | rule reason, communication record, final responsibility |
| Imaging doctor | worklist -> image/report -> AI draft comparison -> edit -> sign/publish | AI draft boundary, prior image access, adopted signature method and verification |
| Lab doctor/technician | sample/result -> review -> critical value publish -> acknowledgement tracking | critical threshold, reviewer, notification chain |
| Quality manager | rule dashboard -> issue detail -> assignment -> verification -> department ranking | rule version, appeal, evidence, overdue |
| Infection-control staff | alert dashboard -> patient/department context -> intervention -> closure | cross-department notification and traceability |
| Researcher | cohort request -> clearance status -> permitted dataset -> usage record | applicable ethics clearance, data minimization, export audit |
| Patient/family | app/internet hospital -> appointment/follow-up/report/education -> payment/feedback | consent, identity, accessibility, message timing |
| Hospital administrator | dashboard -> drill-down -> department action -> review | indicator caliber, source freshness, permission scope |

## UI / Mobile Patterns

Stable test identifiers for medical/hospital prototypes:

| Pattern | Recommended `data-testid` / `data-action` |
|---|---|
| AI suggestion panel | `panel-ai-suggestion`, `btn-ai-review-result`, `badge-human-reviewed` |
| Consent and privacy confirmation | `modal-consent-confirm`, `btn-confirm-consent`, `banner-data-scope` |
| Clinical signature | `btn-ca-sign`, `modal-signature-confirm`, `badge-signed-record` |
| Critical value loop | `table-critical-values`, `btn-ack-critical-value`, `modal-critical-value-action` |
| Imaging workflow | `viewer-imaging-study`, `panel-ai-imaging-draft`, `btn-sign-imaging-report` |
| Prescription review | `table-prescription-review`, `btn-return-prescription`, `modal-intervention-record` |
| Quality/infection alerts | `table-quality-issues`, `card-infection-alert`, `btn-assign-rectification` |
| Research request | `form-research-data-request`, `btn-export-desensitized-data`, `badge-ethics-approved` |

Mobile/field rules:

- Patient-facing mobile flows must show identity, consent, service scope,
  payment/refund state, message/notification timing, and manual-service path.
- Clinician mobile flows must prevent accidental consequential writes through
  confirmation, biometric/CA where applicable, and visible patient identity.
- Offline/weak-network mode may cache draft notes/tasks, but clinical publish,
  signature, prescription, and research export must wait for server validation.

## Policy / Privacy Constraints

**中文阅读提示**

**医疗互认**（结果互认、检查互认、mutual recognition）：区分可交换、可读取与可用于医疗决策；适用范围和来源有效性需要核实。

**医疗隐私**（健康数据、医疗数据、患者隐私、health data）：读取、导出、共享和代理访问须继承患者数据权限及用途边界。

- Minimum necessary data: every role path must state why the user can access
  the patient, encounter, department, or dataset.
- Horizontal and vertical access control: one department, doctor, tenant,
  researcher, or patient must not access another scope without explicit rule,
  authorization, or temporary delegation.
- Clinical accountability: AI may produce draft suggestions only. Final
  diagnosis, prescription, report, discharge, and record signature remain human
  responsibilities.
- Medical record integrity: signed/archived content uses versioned amendment
  with reason and audit trail.
- Lawful basis and authorization: verify the purpose-specific legal basis and permitted scope for diagnosis/treatment, research and patient services. Where consent is legally required, check the applicable consent; do not make consent the sole legal basis or treat one consent as unlimited permission.
- Research and export: record ethics-review applicability, the responsible institutional data-use authority, required privacy treatment, export purpose, recipient, retention and deletion/return evidence. KS-MEDICAL-ETHICS-2023 article 32 provides limited exemption conditions, not a blanket waiver for de-identified data. An accountable applicability decision is required; AI cannot self-exempt a study. An exemption does not remove other lawful-basis and data-use obligations.
- Signature evidence follows the adopted valid method; PKI/CA-specific checks apply when that method is used.
- Integration safety: do not design direct uncontrolled writes to HIS/EMR/LIS/
  PACS databases. Use approved integration gateway/API/message bus with idempotency,
  retry, audit, and rollback/compensation rules.
- Test/shadow data: automated test agents must not create real clinical,
  billing, research, or patient-message side effects.
- Regulatory freshness: PRDs must record which official policies, hospital SOPs,
  and data standards were used, with date/source and unresolved verification gaps.

## Domain Test Scenarios

| ID | Scenario | Expected Result |
|---|---|---|
| MED-001 | Imaging AI returns a suspected lesion with low confidence | recommendation is suppressed or marked draft; radiologist can review, edit, reject, and sign final report |
| MED-002 | LIS publishes a critical potassium value | owner receives notification; acknowledgement SLA starts; action/evidence is recorded; overdue escalates |
| MED-003 | Patient attempts internet follow-up without valid consent or unsupported scope | system blocks consequential service and routes to offline/manual guidance |
| MED-004 | Doctor edits an archived discharge summary | system creates amendment version with reason, signer, time, before/after evidence |
| MED-005 | Pharmacist rejects a prescription due contraindication | prescription returns to doctor with reason; audit and intervention record are visible |
| MED-006 | Infection alert detects cross-department transfer risk | alert follows patient and notifies both responsible departments without auto-creating clinical orders |
| MED-007 | Researcher requests identifiable patient data beyond approval scope | export is blocked; request must be revised or re-approved |
| MED-008 | AI service times out during outpatient record summary | manual path remains available; AI state becomes failed/fallback; no clinical state is written |
| MED-009 | Department director opens dashboard with stale source data | page shows freshness warning and prevents misleading real-time claims |
| MED-010 | Automated browser acceptance test submits a clinical workflow | request is tagged as test/shadow mode; no real clinical/billing side effect remains |
| MED-011 | Two patient identities are confirmed as the same person | merge requires accountable approval; surviving identity, source provenance, access history, correction and rollback evidence remain traceable |
| MED-012 | Clinician cancels a submitted or verified clinical order | role and state guard are checked; downstream execution or billing impact is reconciled; reason and immutable audit remain visible |

## Cross-Domain Requirement Patterns

- `PAT-VERSION-COMPATIBILITY-001`: order sets, forms, clinical policies, consent and AI configurations preserve signed/historical and in-flight versions.
- `PAT-LONG-RUNNING-JOB-001`: imaging processing, research export, record indexing and batch quality checks expose progress, cancellation, retry and accountable failure handling.
- `PAT-METRIC-CALIBER-001`: quality, critical-value, infection, operations and research metrics declare denominator, cutoff, freshness and privacy threshold.
- `PAT-FEDERATED-RECONCILIATION-001`: patient identity and cross-system clinical metadata conflicts require source-aware, accountable reconciliation rather than silent overwrite.

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

- The PRD identifies whether the scenario is clinical, nursing, quality,
  infection-control, patient-service, research, operation, or mixed.
- Each consequential action has accountable human role, permission scope,
  confirmation/signature rule, audit record, and rollback/compensation path.
- AI output has input source, confidence/quality boundary, human gate,
  prohibited write scope, fallback state, and linked golden cases.
- Patient identity, consent, privacy, and data minimization are explicit.
- Integration contracts use approved APIs/messages, not direct uncontrolled DB
  writes to core clinical systems.
- Critical value, infection alert, quality issue, and research export scenarios
  have owner, deadline, escalation, and closure evidence.
- Dashboards/reports state source system, freshness, denominator, permission,
  and unavailable/error states.
- Automated test data is isolated from real clinical, billing, patient-message,
  and research-export effects.
- Regulatory and hospital-policy references are recorded as source evidence,
  with unresolved verification gaps surfaced before handoff.
