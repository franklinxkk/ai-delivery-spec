# Domain: Medical / Hospital IT

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
    payload: { record_id, encounter_id, signer_id, ca_signature_id, signed_at }
  LabCriticalValuePublished:
    payload: { report_id, patient_id, item_code, value, published_at }
  CriticalValueAcknowledged:
    payload: { report_id, ack_user_id, action_taken, ack_at }
  ImagingReportSigned:
    payload: { study_id, report_id, radiologist_id, ca_signature_id, signed_at }
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
ResearchDataRequest: applied -> ethics_approved -> data_committee_approved -> desensitized -> delivered -> closed
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
| Patient consent and authorization | privacy and online service boundary | consent state must be checked before sensitive data use |
| Research cohort/data mart | research screening and extraction | ethics/data approval, de-identification, and export audit required |

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

| Asset | Use | Governance |
|---|---|---|
| clinical guidelines and pathways | CDSS, patient education, record review | approved version, effective date, owner department |
| hospital rules and SOPs | quality, nursing, infection-control workflow | hospital owner and change history |
| medical terminology / code set | ICD, procedure, diagnosis, drug, lab item mapping | versioned dictionary and mapping owner |
| patient education content | internet hospital and discharge follow-up | clinical review, target population, disclaimer |
| AI prompt / model registry | extraction, summary, coding, risk suggestion | golden cases, model/prompt version, rollback owner |
| de-identification rules | research and data export | privacy owner, irreversible/reversible rule, audit proof |

## Core Workflows

| Workflow | Happy Path | Required Exceptions |
|---|---|---|
| Outpatient visit | register -> consult -> order/prescription -> payment/execution -> record sign -> complete | patient mismatch, duplicate encounter, permission denial, unfinished record, payment dependency |
| Inpatient care | admission -> orders/nursing -> results -> daily record -> discharge -> archive | order conflict, critical value, transfer, operation, overdue record, discharge summary incomplete |
| Imaging AI assistance | order -> image acquisition -> AI pre-analysis -> radiologist review -> report sign -> publish | AI timeout, low confidence, conflicting prior report, radiologist rejection, delayed signature |
| Critical value loop | report publish -> notify owner -> acknowledge -> action/evidence -> close | unreachable owner, overdue acknowledgement, false alert, escalation |
| Internet follow-up | patient request -> identity/consent -> doctor review -> prescription/education -> payment/delivery | first-visit prohibition where applicable, unsupported disease, missing consent, refund/cancellation |
| Quality issue management | rule detection/manual issue -> assign -> rectify -> verify -> close | disputed issue, overdue rectification, repeated defect, department transfer |
| Infection alert handling | risk detected -> notify -> acknowledge -> isolate/intervene -> resolve | policy block, false positive, cross-department patient transfer |
| Research data request | apply -> ethics approval -> data approval -> de-identify -> deliver -> audit close | missing approval, excessive scope, re-identification risk, export failure |

## Role Path Patterns

| Role | Typical Path | Must Be Explicit |
|---|---|---|
| Doctor | patient list -> encounter detail -> record/order/prescription -> sign -> follow-up | department scope, patient identity, unsigned draft, AI suggestion review |
| Nurse | ward list -> patient detail -> nursing task -> execution evidence -> handoff | shift, executor, time, evidence, exception escalation |
| Pharmacist | prescription queue -> review -> pass/return/intervene -> audit | rule reason, communication record, final responsibility |
| Imaging doctor | worklist -> image/report -> AI draft comparison -> edit -> sign/publish | AI draft boundary, prior image access, CA signature |
| Lab doctor/technician | sample/result -> review -> critical value publish -> acknowledgement tracking | critical threshold, reviewer, notification chain |
| Quality manager | rule dashboard -> issue detail -> assignment -> verification -> department ranking | rule version, appeal, evidence, overdue |
| Infection-control staff | alert dashboard -> patient/department context -> intervention -> closure | cross-department notification and traceability |
| Researcher | cohort request -> approval status -> de-identified dataset -> usage record | ethics approval, data minimization, export audit |
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
- Consent and authorization: patient-facing and research flows must check
  consent/authorization before sensitive data use.
- Research and export: ethics/data approval, de-identification, export purpose,
  recipient, retention, and deletion/return evidence must be recorded.
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

## Multi-Agent Lifecycle Verification Matrix

| domain_id | stage | reviewer_agent | path_type | scenario_ref | evidence_ref | blocking_question | expected_result | test_marker | verdict |
|---|---|---|---|---|---|---|---|---|---|
| medical_hospital_it | Discover | PM Agent | happy_path | outpatient/inpatient clinical workflow | Domain Purpose | Is the product outcome clinical, nursing, quality, research, operation, or mixed? | scope and accountable user value are explicit | medical_discover_pm_happy_path | PASS |
| medical_hospital_it | Discover | Domain Expert Agent | exception_path | AI-assisted diagnosis request | Domain Purpose / Policy | Is AI prevented from deciding final diagnosis, prescription, discharge, or signature? | clinical_human_gate is mandatory | clinical_human_gate | PASS |
| medical_hospital_it | Discover | Architecture / Data / AI Agent | permission_privacy_path | patient longitudinal context | AI Context Sources / Policy | Are patient identity, encounter scope, and consent discovered before data use? | consent_check and minimum-necessary scope are required | consent_check | PASS |
| medical_hospital_it | Discover | QA Agent | lifecycle_transition | PatientEncounter lifecycle | State Machines | Can QA see open -> discharged/closed paths and corrections? | encounter lifecycle is testable | medical_discover_qa_lifecycle_transition | PASS |
| medical_hospital_it | Discover | Coding Agent | acceptance_test_path | clinical delivery handoff | UI / Mobile Patterns | Can implementation trace source truth and UI controls? | ac_structured, data-testid, data-action, data-state, data-api, data-method, manifest.json, source_of_truth_order required | ac_structured;data-testid;data-action;data-state;data-api;data-method;manifest.json;source_of_truth_order | PASS |
| medical_hospital_it | Specify | PM Agent | happy_path | critical value closed loop | Core Workflows | Does PRD define owner, notification, acknowledgement, action, escalation, and closure? | critical_value_ack_sla is visible and testable | critical_value_ack_sla | PASS |
| medical_hospital_it | Specify | Domain Expert Agent | exception_path | archived medical record edit | Policy / Privacy Constraints | Can signed/archived records be changed only through amendment? | signed_record_amendment requires reason, signer, before/after evidence | signed_record_amendment | PASS |
| medical_hospital_it | Specify | Architecture / Data / AI Agent | permission_privacy_path | internet hospital follow-up | Domain Test Scenarios | Are consent, service scope, identity, and manual path specified? | consent_check blocks unsupported consequential service | consent_check | PASS |
| medical_hospital_it | Specify | QA Agent | lifecycle_transition | PrescriptionReview lifecycle | State Machines | Can review pass/return/intervene paths be tested? | pharmacist intervention and doctor correction are traceable | medical_specify_qa_lifecycle_transition | PASS |
| medical_hospital_it | Specify | Coding Agent | acceptance_test_path | clinical FRR/AC contract | Acceptance Checklist | Can coding agent implement without inventing clinical rules? | FRR, AC, permission, state, audit, and fallback are explicit | medical_specify_coding_acceptance_test_path | PASS |
| medical_hospital_it | Plan | PM Agent | happy_path | imaging AI report workflow | Core Workflows | Are AI draft, radiologist review, signature, and fallback planned? | clinical_human_gate owns final report | clinical_human_gate | PASS |
| medical_hospital_it | Plan | Domain Expert Agent | exception_path | infection alert overreach | Domain Test Scenarios | Does alert avoid auto-creating clinical orders? | human review and department responsibility are explicit | medical_plan_domain_exception_path | PASS |
| medical_hospital_it | Plan | Architecture / Data / AI Agent | permission_privacy_path | research data export | Policy / Privacy Constraints | Are ethics approval, de-identification, purpose, recipient, retention, and deletion planned? | consent_check and approval scope block excess export | consent_check | PASS |
| medical_hospital_it | Plan | QA Agent | lifecycle_transition | MedicalRecord lifecycle | State Machines | Can QA plan draft -> signed -> archived -> amended tests? | signed_record_amendment path exists | signed_record_amendment | PASS |
| medical_hospital_it | Plan | Coding Agent | acceptance_test_path | delivery package | UI / Mobile Patterns | Are medical data-* controls, APIs, and source order planned? | source_of_truth_order and manifest are required | source_of_truth_order;manifest.json | PASS |
| medical_hospital_it | Tasks | PM Agent | happy_path | patient service workflow | Role Path Patterns | Are tasks sliced by patient-visible closure, not only backend integration? | patient path has identity, consent, result, notification, manual service | medical_tasks_pm_happy_path | PASS |
| medical_hospital_it | Tasks | Domain Expert Agent | exception_path | low-confidence AI suggestion | Domain Test Scenarios | Are suppress/reject/edit/sign paths taskable? | AI suggestion cannot become final clinical state | clinical_human_gate | PASS |
| medical_hospital_it | Tasks | Architecture / Data / AI Agent | permission_privacy_path | approved integration gateway | Policy / Privacy Constraints | Do tasks avoid uncontrolled writes to HIS/EMR/LIS/PACS? | approved API/message bus with audit and rollback is required | medical_tasks_arch_permission_privacy_path | PASS |
| medical_hospital_it | Tasks | QA Agent | lifecycle_transition | CriticalValueAlert lifecycle | State Machines | Are ack/action/escalation/closed cases assigned? | critical_value_ack_sla has tests and overdue escalation | critical_value_ack_sla | PASS |
| medical_hospital_it | Tasks | Coding Agent | acceptance_test_path | browser automation isolation | Domain Test Scenarios | Can automated tests avoid real clinical/billing side effects? | shadow/test mode and data-* hooks are required | data-testid;data-action;data-state | PASS |
| medical_hospital_it | Build/Verify | PM Agent | happy_path | quality issue rectification | Domain Test Scenarios | Does build prove owner, deadline, evidence, and closure? | quality workflow closes with accountable evidence | medical_build_pm_happy_path | PASS |
| medical_hospital_it | Build/Verify | Domain Expert Agent | exception_path | contraindication prescription return | Domain Test Scenarios | Does pharmacist intervention preserve clinical accountability? | doctor correction and audit are visible | clinical_human_gate | PASS |
| medical_hospital_it | Build/Verify | Architecture / Data / AI Agent | permission_privacy_path | unauthorized patient data access | Policy / Privacy Constraints | Can unauthorized role see another patient/department/dataset? | access is refused without leakage | medical_build_arch_permission_privacy_path | PASS |
| medical_hospital_it | Build/Verify | QA Agent | lifecycle_transition | medical AI timeout | Domain Test Scenarios | Does timeout avoid clinical write and keep manual path? | fallback state is testable | medical_build_qa_lifecycle_transition | PASS |
| medical_hospital_it | Build/Verify | Coding Agent | acceptance_test_path | implementation validation | Acceptance Checklist | Can tests bind UI, API, AC, audit, and medical state? | ac_structured and data-* coverage exist | ac_structured;data-testid;data-action | PASS |
| medical_hospital_it | Launch | PM Agent | happy_path | department dashboard launch | Metric / Indicator Governance | Are source, freshness, denominator, permission, and error states launch-ready? | stale data warning prevents misleading claims | regulatory_freshness_source | PASS |
| medical_hospital_it | Launch | Domain Expert Agent | exception_path | policy-sensitive release | Policy / Privacy Constraints | Were latest official policies and hospital SOPs verified before signoff? | regulatory_freshness_source records date/source/gaps | regulatory_freshness_source | PASS |
| medical_hospital_it | Launch | Architecture / Data / AI Agent | permission_privacy_path | production clinical write | Policy / Privacy Constraints | Are high-impact writes guarded, audited, and compensatable? | integration gateway, human gate, audit, rollback/compensation exist | clinical_human_gate | PASS |
| medical_hospital_it | Launch | QA Agent | lifecycle_transition | internet hospital launch | State Machines | Can smoke tests verify service open/blocked/manual/closed paths? | consent and unsupported scope paths are testable | consent_check | PASS |
| medical_hospital_it | Launch | Coding Agent | acceptance_test_path | release package | Acceptance Checklist | Can coding agent identify launch blockers? | lifecycle, permission, AI boundary, audit, and acceptance evidence present | medical_launch_coding_acceptance_test_path | PASS |
| medical_hospital_it | Learn/Retire | PM Agent | happy_path | post-launch medical quality review | Metric / Indicator Governance | Can metrics decide iterate, rollback, retire, or expand? | safety, SLA, fallback, and adoption signals feed decision | medical_learn_pm_happy_path | PASS |
| medical_hospital_it | Learn/Retire | Domain Expert Agent | exception_path | obsolete clinical policy | Content / Knowledge Assets | Can stale policy or SOP stop affecting decisions? | regulatory_freshness_source triggers review/retirement | regulatory_freshness_source | PASS |
| medical_hospital_it | Learn/Retire | Architecture / Data / AI Agent | permission_privacy_path | retained clinical/research records | Policy / Privacy Constraints | Are retention, masking, export/delete, and audit rules respected? | consent and approval scopes remain enforceable | consent_check | PASS |
| medical_hospital_it | Learn/Retire | QA Agent | lifecycle_transition | AI model/prompt retired | State Machines | Can QA verify degraded/disabled/retired states? | no clinical write occurs after retirement | medical_learn_qa_lifecycle_transition | PASS |
| medical_hospital_it | Learn/Retire | Coding Agent | acceptance_test_path | regression continuity | Acceptance Checklist | Can implementation preserve historical AC and signed evidence? | source_of_truth_order and signed_record_amendment remain traceable | source_of_truth_order;signed_record_amendment | PASS |

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
