# Domain: Higher-Education Informationization / 高校教育信息化

Use this replaceable domain module for higher-education digital campus, vocational college digital transformation, academic affairs, student affairs, teaching quality, smart classroom, one-stop service, data governance, data middle platform, AI assistant, and education data/BI scenarios.

This module is distilled from multi-year higher-education informationization materials. Keep customer/project details out of the public protocol; preserve reusable domain rules only.

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

- Business outcome: make university teaching, learning, student growth, campus service, quality diagnosis, and data governance visible, serviceable, measurable, and continuously improvable.
- Primary users: school leaders, academic affairs office, student affairs office, teaching quality office, departments/colleges, program directors, teachers, counselors, students, data center/network office, IT administrators, external evaluators.
- Sensitive areas: student identity, grades, awards/punishments, financial aid, mental-health risk, employment data, attendance/location, classroom video/audio, teacher evaluation, personnel data, and cross-system master data.
- AI may optimize: policy Q&A, one-stop service guidance, learning/career suggestions, counselor work assistance, data Q&A, classroom quality analysis, teaching report drafting, form/process filling, and risk hints.
- AI must not decide automatically: student disciplinary action, scholarship/aid final result, psychological crisis classification, final grades, graduation eligibility, teacher performance conclusion, official evaluation result, or any legally/accountably binding school decision.

## Vocabulary

| Term | Meaning | Source of Truth |
|---|---|---|
| School / Campus | institution-level tenant and governance boundary | organization master |
| College / Department | teaching or administrative sub-organization | organization master |
| Program / Major | approved talent-training unit such as undergraduate/vocational major | academic affairs / program registry |
| Class Cohort | student administrative class or teaching class | student/academic master |
| Student | learner with identity, enrollment, study, service, and growth records | student master / academic affairs |
| Teacher | teaching staff with courses, workload, quality evaluation, and teaching resources | personnel + academic affairs |
| Course | curriculum unit with syllabus, offering, class schedule, resources, assessments | course registry |
| Teaching Class | concrete course offering for a term with teacher, students, time, room | teaching operation service |
| Training Plan | talent-cultivation plan including curriculum system, credits, outcomes | academic affairs / program committee |
| Academic Status | enrollment, registration, leave, transfer, warning, graduation status | academic status service |
| Student Affairs Case | counselor/student-service process such as leave, aid, award, sanction, dorm, safety | student affairs service |
| One-Stop Service | cross-department online process and service portal | process/workflow platform |
| Quality Diagnosis | goals, indicators, evidence, diagnosis, improvement, review | quality assurance/diagnosis platform |
| Smart Classroom Signal | classroom video/audio/interaction/attendance/device data | smart classroom platform |
| Education Indicator | governed metric with caliber, source, owner, dimension, version | indicator registry / data platform |

## Aggregates and Entities

| Aggregate | Owns | Key States | Notes |
|---|---|---|---|
| Organization | school, college, department, role scope | active / merged / disabled | tenant and data-scope root |
| PersonIdentity | student/teacher/staff identity, account, role binding | active / frozen / left / archived | shared identity; avoid duplicate person records |
| StudentProfile | enrollment, cohort, academic status, growth tags, risk markers | enrolled / suspended / transferred / graduated / withdrawn | student master data with privacy controls |
| TeacherProfile | teaching roles, course assignments, workload, evaluation history | active / inactive / archived | joins personnel and academic affairs |
| ProgramMajor | major profile, professional group, outcomes, enrollment plan | draft / active / suspended / archived | supports vocational professional-group governance |
| TrainingPlan | course system, credits, outcomes, version, approval | draft / reviewing / published / revised / archived | published plan is versioned and referenced by students |
| Course | syllabus, resources, knowledge points, assessment rules | draft / active / retired | course registry differs from term offering |
| TeachingClass | term offering, teacher, students, schedule, classroom | planned / scheduling / running / completed / closed | core academic operation aggregate |
| ExamAssessment | paper/question strategy, exam arrangement, score, appeal | draft / published / grading / released / archived | high-risk state requires audit |
| StudentAffairsCase | application, approval, evidence, result, notification | draft / submitted / processing / returned / approved / rejected / closed | many school workflows share this pattern |
| CounselingCase | counselor follow-up, interview, warning, referral, closure | open / following / referred / closed / archived | mental-health content has strict visibility |
| ClassroomEvaluation | classroom signal, rubric, evidence, result, appeal | pending / analyzing / reviewed / published / archived | AI analysis is suggestion/evidence, not final evaluation |
| ServiceProcess | form, workflow instance, task, deadline, audit | draft / submitted / processing / returned / completed / cancelled | one-stop service and low-code workflows |
| DataResource | standard, master data, source system, API, quality rule | draft / active / deprecated | owned by data responsibility department |
| IndicatorReport | indicator snapshot, report template, analysis, release | draft / generated / reviewed / published / archived | generated reports must cite indicator versions |

## Domain Events

```yaml
events:
  StudentStatusChanged:
    payload: { student_id, old_status, new_status, reason, operator_id, effective_at }
  TeachingClassPublished:
    payload: { teaching_class_id, term_id, course_id, teacher_ids, student_count }
  CourseSelectionConfirmed:
    payload: { student_id, teaching_class_id, selection_batch, confirmed_at }
  ScoreReleased:
    payload: { exam_id, teaching_class_id, release_scope, released_by, released_at }
  StudentAffairsCaseSubmitted:
    payload: { case_id, case_type, student_id, submitter_id, submitted_at }
  StudentAffairsCaseReturned:
    payload: { case_id, node_id, return_reason, operator_id }
  CounselingRiskFlagged:
    payload: { student_id, risk_level, source_refs, reviewer_id, followup_required }
  ClassroomEvaluationReviewed:
    payload: { evaluation_id, teaching_class_id, reviewer_id, result, evidence_refs }
  TrainingPlanPublished:
    payload: { plan_id, program_id, version, effective_grade, approved_by }
  DataStandardActivated:
    payload: { standard_id, domain, owner_department, version, effective_at }
  IndicatorSnapshotFrozen:
    payload: { report_id, indicator_versions, cutoff_time, publisher_id }
```

## State Machines

```text
TrainingPlan: draft -> reviewing -> published -> revised -> archived
TeachingClass: planned -> scheduling -> running -> completed -> closed
CourseSelection: available -> selected -> confirmed | dropped | waitlisted
ExamAssessment: draft -> published -> grading -> released -> archived
ScoreAppeal: submitted -> reviewing -> adjusted | rejected -> closed
StudentAffairsCase: draft -> submitted -> processing -> approved | rejected | returned
StudentAffairsCase: returned -> resubmitted -> processing
CounselingCase: open -> following -> referred | closed -> archived
ClassroomEvaluation: pending -> analyzing -> reviewed -> published | returned -> archived
ServiceProcess: draft -> submitted -> processing -> returned | completed | cancelled
DataResource: draft -> pending_review -> active -> deprecated
IndicatorReport: draft -> generated -> reviewed -> published -> archived
```

State consistency:

| Business Concept | Source of Truth | Consumers | Consistency Need |
|---|---|---|---|
| student identity/status | student master / academic affairs | teaching, student affairs, finance, dorm, data BI | strong before official action |
| course offering and roster | teaching operation service | timetable, exam, classroom, learning platform | strong for selection/exam; eventual for analytics |
| grades and credits | exam/academic affairs | graduation audit, warning, scholarship, analytics | strong and auditable |
| student affairs result | workflow aggregate | student portal, counselor desk, BI, archives | human-confirmed |
| classroom evaluation result | teaching quality service | teacher improvement, quality report, leadership dashboard | reviewed before publishing |
| indicator/report result | indicator registry + frozen snapshot | dashboard, report, external evaluation | immutable snapshot |

## Metric / Indicator Governance

```yaml
indicator:
  id: EDU-IND-001
  name: string
  category: academic_affairs | student_affairs | teaching_quality | employment | service | data_quality | smart_classroom
  caliber: string
  source: system_or_table_or_api
  dimensions: [school, college, program, grade, class, teacher, course, term, time]
  compute_type: count | distinct | sum | avg | ratio | score | distribution | trend
  owner: responsible_department
  version: semver
  status: draft | pending_review | active | deprecated
  quality_checks: [source_exists, owner_confirmed, dimension_join_valid, null_rate_threshold, duplicate_rule]
```

Rules:

- no active education indicator without caliber, source, owner department, dimensions, refresh frequency, and privacy level;
- official reports freeze indicator versions, source cutoff time, organization scope, and template version;
- cross-department data must record responsibility department: "who produces, who owns, who maintains";
- AI-generated data interpretation is a draft unless reviewed by the responsible office;
- student-level sensitive indicators must support aggregation, masking, and minimum-sample thresholds before display/export.

Common categories:

| Category | Examples |
|---|---|
| Academic affairs | course offering count, selection success rate, timetable conflict count, grade pass rate, credit completion |
| Student affairs | leave approval time, aid application completion, counseling follow-up, dorm issue closure, safety warning count |
| Teaching quality | classroom evaluation score, attendance, interaction frequency, objective achievement, evaluation-improvement closure |
| Employment and growth | employment rate, major relevance, career guidance participation, certificate/competition achievements |
| One-stop service | service volume, completion rate, timeout rate, return rate, satisfaction |
| Data governance | data standard coverage, master-data duplicate rate, interface freshness, data-quality issue closure |

## AI Context Sources

| Context | Source | Freshness | Permission Scope | Risk |
|---|---|---|---|---|
| student basic/profile | student master / academic affairs | real-time/daily | own student, counselor scope, authorized office | identity/privacy leakage |
| course/teaching data | academic affairs, LMS, timetable, exam | real-time/term | teacher/class/college scope | wrong source affects grade/credit decisions |
| student affairs cases | workflow/student affairs systems | real-time | student owner, counselor, responsible office | sensitive award/aid/discipline exposure |
| counseling/mental-health notes | counseling system / counselor records | real-time/restricted | minimum necessary authorized staff | high sensitivity; AI cannot diagnose |
| classroom media/signals | smart classroom platform | streaming/eventual | course teacher, evaluator, quality office | biometric/video/audio privacy |
| policies and service guides | approved knowledge base /制度文件 | versioned | public or role-limited | outdated answer causes wrong procedure |
| data standards/indicators | data governance platform | versioned | data center + responsible office | misleading BI if caliber/source stale |
| employment and career data | employment system / third-party platform | daily/term | student/career office/college scope | consent and external data reliability |

## Content / Knowledge Assets

| Asset Type | Examples | Tags | Quality Rule |
|---|---|---|---|
| policy/regulation | student handbook, teaching rules, academic status rules, aid policy | role, department, effective date | owner office review; versioned |
| service guide | one-stop service procedures, required materials, deadline, responsible office | service_type, audience, channel | must map to live process/form |
| training plan/course asset | talent-cultivation plan, syllabus, knowledge points, resources | program, grade, course, version | published version immutable |
| rubric/template | classroom evaluation rubric, teaching inspection checklist, diagnosis report template | scenario, evaluator, version | activation requires business owner |
| FAQ/AI knowledge | admissions FAQ, student affairs FAQ, academic affairs FAQ, IT support Q&A | source, audience, validity | cite source and freshness |
| indicator/report template | quality report, data-governance report, employment analysis | indicator_ids, scope, cutoff | frozen snapshot and traceable owner |
| workflow/form template | leave, award, aid, repair, certificate, approval forms | process_key, version, fields | field dictionary and approval path required |

## Core Workflows

| Workflow | Actors | Trigger | State Change | Success Result |
|---|---|---|---|---|
| academic term setup | academic affairs, college, teacher | new term preparation | teaching class planned -> published | course offerings, roster, timetable, exam basis established |
| course selection and adjustment | student, academic affairs, college | selection window opens | selected/waitlisted -> confirmed/dropped | student timetable and roster consistent |
| score release and appeal | teacher, academic affairs, student | grading completed | grading -> released; appeal -> closed | grades auditable; changes traceable |
| student affairs service | student/counselor/office | application submitted | submitted -> approved/rejected/returned | service result notified and archived |
| counseling/risk follow-up | counselor, student affairs, professional staff | risk signal or manual case | open -> following/referred/closed | follow-up evidence and privacy boundary recorded |
| classroom quality evaluation | teacher, evaluator, quality office | class observed or AI signal generated | analyzing -> reviewed -> published | reviewed result and improvement task produced |
| training-plan revision | program leader, college, academic affairs | curriculum update | draft -> reviewing -> published | versioned plan applied to target grade |
| one-stop service process | applicant, handler, approver | form/process submitted | submitted -> processing -> completed/returned | cross-department task closed with audit |
| data governance | data center, responsible office | standard/source integration | draft -> active/deprecated | master data, API, indicator, quality rules traceable |
| AI assistant answer/action | teacher/student/staff, AI assistant, responsible office | user asks / requests operation | draft answer/task -> human confirmed where consequential | answer cites source; action remains within permission |

## Role Path Patterns

| Role | Entry | Core Actions | Forbidden Actions | Exit |
|---|---|---|---|---|
| school leader | dashboard / data brain | inspect indicators, drill to college/program, assign follow-up | view unnecessary student-sensitive details | decision or follow-up task recorded |
| academic affairs office | academic affairs console | manage term, course, selection, exam, grade release, training plans | alter teacher/student data outside authority without audit | academic operation closed |
| student affairs office | student affairs console | manage aid/award/sanction/dorm/safety policies and cases | bypass counselor/professional review for sensitive cases | case result and archive |
| counselor | counselor workbench/mobile | view own students, follow up warnings, submit/handle cases, record interviews | view other classes without authorization; AI-only crisis decision | follow-up completed or referred |
| teacher | teaching workbench | manage class resources, attendance, grading, feedback, improvement | view unrelated student affairs/mental data | teaching task completed |
| student | portal/mobile/mini-program | apply services, check timetable/grades, learn, submit feedback, appeal | view other students or hidden evaluation data | service completed or progress visible |
| college/program leader | college dashboard | monitor program, teaching, students, quality tasks | change school-level standard without approval | improvement action closed |
| teaching quality office / evaluator | evaluation console/mobile | create/review evaluation, publish result, assign improvement | publish AI result without human review | quality evidence archived |
| data center/network office | data governance platform | manage standards, APIs, quality rules, identity, permissions | decide business caliber without owner office | data service active and monitored |
| IT administrator | system admin | configure tenant, org, roles, integrations, logs | access business content without audit/authorization | secure operation |

## UI / Mobile Patterns

- desktop patterns: dense lists with term/college/program/class filters, source labels, status-driven actions, evidence timeline, and drilldown from dashboard to object detail;
- mobile patterns: student/counselor/teacher task cards, service progress, timetable, approval, attendance, classroom evidence upload, weak-network drafts;
- one-stop service: service catalog -> form -> material check -> submit -> progress -> result/archive;
- dashboard/data brain: indicator caliber tooltip, source/freshness label, minimum-sample privacy guard, drill path, export audit;
- smart classroom: media/evidence preview, rubric scoring, AI suggestion side panel, human review button, appeal/history timeline;
- required testids: `nav-academic-affairs`, `nav-student-affairs`, `nav-teaching-quality`, `nav-data-governance`, `tbl-course-selection`, `btn-submit-service`, `btn-return-case`, `btn-release-score`, `btn-review-classroom-eval`, `badge-data-freshness`;
- role switch requirements: school leader, academic affairs, student affairs, counselor, teacher, student, quality office, data center/admin paths must be independently demoable when in scope.

## Policy / Privacy Constraints

- Student personal, academic, financial-aid, counseling, health, dorm, employment, and disciplinary data follow least privilege, masking, retention, and audit rules.
- Mental-health and counseling AI can provide triage hints or conversation assistance only; diagnosis, crisis level, and intervention decision require authorized human/professional accountability.
- Grades, credits, graduation eligibility, awards/aid/sanctions, and teacher evaluation conclusions require human approval and audit evidence.
- Classroom audio/video/image use requires clear purpose, role access, retention period, and display/export control.
- Cross-system data integration must identify authoritative source, owner department, update frequency, conflict resolution, and rollback/reconciliation path.
- Data export, API opening, dashboard drilldown, and AI context retrieval must respect organization, role, student cohort/class, course, and department data scope.
- Test agents must use synthetic/shadow data and must not pollute student records, grades, service statistics, or official reports.
- Generated reports and official evaluation evidence must freeze source, indicator versions, template version, and cutoff time.

## Domain Test Scenarios

| Scenario | Role | Preconditions | Steps | Expected Domain Result |
|---|---|---|---|---|
| course selection conflict | student/academic affairs | selection window open; timetable conflict exists | select conflicting class -> confirm | conflict blocked or waitlisted; no inconsistent roster |
| score release with appeal | teacher/student/academic affairs | grades submitted | release -> student appeals -> review -> adjust/reject | score change audited; appeal closed |
| student leave process | student/counselor/office | student submits leave | submit -> counselor review -> office approve/return | service state visible; notifications and audit recorded |
| scholarship/aid review | student affairs/counselor | application submitted | review materials -> approve/reject/return | final result human-approved; sensitive fields masked |
| counseling risk follow-up | counselor | risk signal exists | create case -> follow-up -> refer/close | AI hint not final diagnosis; evidence and visibility restricted |
| classroom AI quality evaluation | evaluator/quality office | classroom signal analyzed | view AI evidence -> human review -> publish/return | reviewed result published; teacher can view scope-allowed evidence |
| training-plan version change | program leader/academic affairs | published plan exists | create revision -> approve -> publish | old students keep old version; target grade uses new version |
| data standard activation | data center/owner office | new data standard drafted | owner review -> activate -> monitor quality | source owner and quality rules traceable |
| AI policy Q&A stale source | teacher/student | policy knowledge has old and new versions | ask question -> answer cites source | answer uses effective version or refuses with update warning |
| dashboard privacy threshold | school leader | small sample group exists | drill into sensitive student indicator | aggregate shown; student-level detail hidden without authority |

## Acceptance Checklist

- [ ] All 14 domain module sections are present.
- [ ] Academic affairs, student affairs, teaching quality, one-stop service, data governance, and AI assistant boundaries are explicit when relevant.
- [ ] Student, teacher, course, teaching class, score, service case, classroom evaluation, data resource, and indicator lifecycles are defined.
- [ ] Authoritative source, owner department, freshness, and conflict-resolution rule are named for cross-system data.
- [ ] Sensitive student and classroom data are masked, scoped, retained, and audited.
- [ ] AI outputs show source/freshness/confidence and cannot finalize high-stakes educational decisions.
- [ ] Mobile/student/teacher/counselor paths include weak-network, notification, and permission behavior where in scope.
- [ ] Every dashboard/report metric has caliber, source, dimension, owner, version, and acceptance evidence.
