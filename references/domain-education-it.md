# Domain: Higher-Education Informationization / 高校教育信息化

Use this replaceable domain module for higher-education digital campus, vocational college digital transformation, academic affairs, student affairs, research administration, teaching quality, smart classroom, professional/program construction, one-stop service, data governance, data middle platform, AI assistant, and education data/BI scenarios.

This module is distilled from multi-year higher-education informationization materials. Keep customer/project details out of the public protocol; preserve reusable domain rules only.

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

- Business outcome: make university teaching, learning, student growth, research activity, campus service, quality diagnosis, professional construction, and data governance visible, serviceable, measurable, and continuously improvable.
- Primary users: school leaders, academic affairs office, student affairs office, research office, teaching quality office, departments/colleges, program directors, professional-group leaders, teachers, counselors, students, data center/network office, IT administrators, external evaluators.
- Sensitive areas: student identity, grades, awards/punishments, financial aid, mental-health risk, employment data, attendance/location, classroom video/audio, teacher evaluation, research projects, research funding, contracts/IP, personnel data, and cross-system master data.
- AI may optimize: policy Q&A, one-stop service guidance, learning/career suggestions, counselor work assistance, data Q&A, classroom quality analysis, teaching report drafting, form/process filling, and risk hints.
- AI must not decide automatically: student disciplinary action, scholarship/aid final result, psychological crisis classification, final grades, graduation eligibility, teacher performance conclusion, official evaluation result, or any legally/accountably binding school decision.
- Representative system families to abstract from: academic affairs suites such as training-plan, course, scheduling, selection, exam, score, graduation-audit, and textbook management; learning/teaching platforms with course resources, classroom interaction, homework, analytics, and AI classroom signals; student-affairs platforms covering one-stop community, counselor workbench, aid/award/sanction/dorm/safety/employment; research management platforms covering project, fund, contract, output, IP, ethics/integrity, and achievement transformation; university data platforms covering standards, master data, indicators, reports, and dashboards.

## First-Principles Domain Lens

Education IT product judgment starts from accountable learning, teaching,
student growth, service, research, and governance outcomes.

| Lens | Education Question | Acceptance Signal |
|---|---|---|
| Educational object | Which student, teacher, course, class, program, service case, research project, or indicator changes? | source system, owner, term/version, and role scope are explicit |
| Accountability | Which office, teacher, counselor, reviewer, or student owns the next action? | workflow task, deadline, evidence, and appeal/review path exist |
| Outcome evidence | What proves learning, teaching quality, service completion, research progress, or improvement? | assessment, portfolio, diagnosis, output, or service result is traceable |
| Policy boundary | Which school, provincial, national, accreditation, privacy, or customer rule applies? | rule source, version, applicability, and conflict handling are registered |
| AI boundary | Which recommendations stay non-binding and require human confirmation? | final grades, graduation, aid, discipline, mental-health, and evaluations keep human gates |

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
| Program Group / Professional Group | vocational/professional cluster aligned to industry chain, job groups, courses, resources, and training base | program construction office |
| Graduation Requirement | outcome statement decomposed into indicators and supported by courses/assessments | OBE / accreditation evidence |
| Course Objective Achievement | calculated evidence that course objectives support graduation requirements and continuous improvement | achievement analysis system |
| Academic Status | enrollment, registration, leave, transfer, warning, graduation status | academic status service |
| Student Affairs Case | counselor/student-service process such as leave, aid, award, sanction, dorm, safety | student affairs service |
| One-Stop Student Community | physical/digital student service and education community integrating counselor, service, activity, network ideology, and growth support | student affairs office |
| Student Development Portfolio | longitudinal evidence for ideology, study, activity, practice, mental health, career, employment, and growth | student development platform |
| One-Stop Service | cross-department online process and service portal | process/workflow platform |
| Quality Diagnosis | goals, indicators, evidence, diagnosis, improvement, review | quality assurance/diagnosis platform |
| Teaching Quality Loop | teaching inspection, classroom observation, student evaluation, peer review, diagnosis, improvement, and re-evaluation | quality office |
| Smart Classroom Signal | classroom video/audio/interaction/attendance/device data | smart classroom platform |
| Research Project | proposal, approval, contract/task, budget, execution, inspection, acceptance, output, archive | research management platform |
| Research Output | paper, patent, software copyright, monograph, award, standard, project deliverable, achievement transformation | research output registry |
| Research Fund | budget, arrival, allocation, reimbursement, expenditure, adjustment, settlement | research/finance integration |
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
| ProgramConstructionPlan | program/group goals, standards, tasks, evidence, diagnosis, improvement | draft / executing / diagnosing / improved / archived | supports 双高, professional certification, audit evaluation, and annual construction |
| CurriculumStandard | syllabus, course objectives, content modules, assessment design, support matrix | draft / reviewing / published / revised / archived | connects course design, implementation, evaluation, and improvement |
| Course | syllabus, resources, knowledge points, assessment rules | draft / active / retired | course registry differs from term offering |
| TeachingClass | term offering, teacher, students, schedule, classroom | planned / scheduling / running / completed / closed | core academic operation aggregate |
| ExamAssessment | paper/question strategy, exam arrangement, score, appeal | draft / published / grading / released / archived | high-risk state requires audit |
| CourseObjectiveAchievement | course objective, graduation requirement support, assessment mapping, threshold, result, improvement | draft / mapped / calculated / reviewed / improved / archived | OBE evidence must be traceable to source score and assessment item |
| StudentAffairsCase | application, approval, evidence, result, notification | draft / submitted / processing / returned / approved / rejected / closed | many school workflows share this pattern |
| CounselingCase | counselor follow-up, interview, warning, referral, closure | open / following / referred / closed / archived | mental-health content has strict visibility |
| StudentCommunityActivity | one-stop community activity, participant, check-in, credit/points, evidence, feedback | planned / published / running / completed / archived | includes network ideology, growth, service, and activity operations |
| StudentDevelopmentPortfolio | student growth record, tags, warnings, services, activities, career evidence | active / frozen / archived | high sensitivity; student-visible and counselor-visible scopes differ |
| ClassroomEvaluation | classroom signal, rubric, evidence, result, appeal | pending / analyzing / reviewed / published / archived | AI analysis is suggestion/evidence, not final evaluation |
| TeachingQualityImprovement | issue, diagnosis, owner, action, deadline, evidence, review | created / assigned / improving / reviewed / closed / overdue | quality monitoring must close the improvement loop |
| SmartClassroomSpace | room/device/IoT/media/schedule/control/events | active / maintenance / disabled | device operation differs from teaching evidence ownership |
| ResearchProject | proposal, approval, task, budget, execution, inspection, acceptance, archive | draft / submitted / approved / executing / accepted / closed / terminated | project rules vary by fund source and level |
| ResearchFund | budget, arrival, allocation, reimbursement, expenditure, settlement | planned / arrived / allocated / spending / settled / frozen | requires finance integration and audit trail |
| ResearchOutput | paper/patent/award/standard/software/monograph/deliverable | draft / submitted / verified / published / transformed / archived | output attribution, duplicate check, and proof attachments are mandatory |
| ResearchIntegrityReview | ethics/integrity/conflict/IP review | pending / reviewing / passed / rejected / rectifying / archived | high-risk research compliance workflow |
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
  CurriculumStandardPublished:
    payload: { standard_id, course_id, version, outcome_matrix_version, effective_term }
  CourseObjectiveAchievementCalculated:
    payload: { achievement_id, course_id, teaching_class_id, assessment_refs, threshold, result, calculated_at }
  TeachingQualityIssueCreated:
    payload: { issue_id, source, course_id, teacher_id, evidence_refs, owner_id, deadline }
  TeachingQualityImprovementClosed:
    payload: { issue_id, reviewer_id, result, evidence_refs, closed_at }
  StudentCommunityActivityPublished:
    payload: { activity_id, organizer_id, target_scope, signup_rule, published_at }
  StudentDevelopmentRiskFlagged:
    payload: { student_id, risk_type, source_refs, visibility_scope, reviewer_id }
  ResearchProjectApproved:
    payload: { project_id, source_type, sponsor, pi_id, budget, start_at, end_at }
  ResearchFundArrived:
    payload: { fund_id, project_id, amount, source, arrival_at, finance_ref }
  ResearchOutputVerified:
    payload: { output_id, project_id, output_type, owner_ids, proof_refs, verified_by }
  ResearchIntegrityReviewCompleted:
    payload: { review_id, project_or_output_id, result, reviewer_id, evidence_refs }
  DataStandardActivated:
    payload: { standard_id, domain, owner_department, version, effective_at }
  IndicatorSnapshotFrozen:
    payload: { report_id, indicator_versions, cutoff_time, publisher_id }
```

## State Machines

```text
TrainingPlan: draft -> reviewing -> published -> revised -> archived
ProgramConstructionPlan: draft -> executing -> diagnosing -> improved -> archived
CurriculumStandard: draft -> reviewing -> published -> revised -> archived
TeachingClass: planned -> scheduling -> running -> completed -> closed
CourseSelection: available -> selected -> confirmed | dropped | waitlisted
ExamAssessment: draft -> published -> grading -> released -> archived
ScoreAppeal: submitted -> reviewing -> adjusted | rejected -> closed
CourseObjectiveAchievement: draft -> mapped -> calculated -> reviewed -> improved -> archived
StudentAffairsCase: draft -> submitted -> processing -> approved | rejected | returned
StudentAffairsCase: returned -> resubmitted -> processing
CounselingCase: open -> following -> referred | closed -> archived
StudentCommunityActivity: planned -> published -> running -> completed -> archived
StudentDevelopmentPortfolio: active -> frozen -> archived
ClassroomEvaluation: pending -> analyzing -> reviewed -> published | returned -> archived
TeachingQualityImprovement: created -> assigned -> improving -> reviewed -> closed | overdue
SmartClassroomSpace: active -> maintenance | disabled
ResearchProject: draft -> submitted -> approved -> executing -> accepted -> closed | terminated
ResearchFund: planned -> arrived -> allocated -> spending -> settled | frozen
ResearchOutput: draft -> submitted -> verified -> published | transformed -> archived
ResearchIntegrityReview: pending -> reviewing -> passed | rejected | rectifying -> archived
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
| course objective achievement | OBE/achievement analysis service | certification, audit evaluation, program improvement, course improvement | traceable to source assessment and reviewed before official use |
| professional construction evidence | program construction platform | 双高/专业认证/audit evaluation/leadership dashboard | versioned evidence and owner-confirmed caliber |
| research project/fund/output | research management + finance + output registry | researcher desk, finance, audit, dashboard, external reporting | strong for fund/output verification; immutable after archive |
| indicator/report result | indicator registry + frozen snapshot | dashboard, report, external evaluation | immutable snapshot |

## Metric / Indicator Governance

```yaml
indicator:
  id: EDU-IND-001
  name: string
  category: academic_affairs | student_affairs | teaching_quality | professional_construction | obe_achievement | employment | research | service | data_quality | smart_classroom
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
| Professional construction | professional-group task progress, talent-training plan revision, industry alignment, course-resource standard coverage, evidence completeness |
| OBE / accreditation | graduation requirement support coverage, course-objective mapping completeness, achievement pass rate, improvement closure |
| Employment and growth | employment rate, major relevance, career guidance participation, certificate/competition achievements |
| Research | project approval rate, fund arrival/expenditure progress, output verification count, IP/achievement transformation, integrity review closure |
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
| OBE/accreditation evidence | training plan, curriculum standard, assessment mapping, achievement analysis | term/versioned | program leader, academic affairs, quality office | wrong mapping affects certification/audit evidence |
| professional construction evidence | program/group tasks, 双高 evidence, industry cooperation, resource assets | monthly/term | college/program/school leadership scope | overclaiming construction results |
| research project/fund/output | research management, finance, output/IP systems | real-time/monthly | PI, research office, finance/audit, authorized leader | fund/IP/confidential project leakage |
| data standards/indicators | data governance platform | versioned | data center + responsible office | misleading BI if caliber/source stale |
| employment and career data | employment system / third-party platform | daily/term | student/career office/college scope | consent and external data reliability |

## Content / Knowledge Assets

| Asset Type | Examples | Tags | Quality Rule |
|---|---|---|---|
| policy/regulation | student handbook, teaching rules, academic status rules, aid policy | role, department, effective date | owner office review; versioned |
| service guide | one-stop service procedures, required materials, deadline, responsible office | service_type, audience, channel | must map to live process/form |
| training plan/course asset | talent-cultivation plan, syllabus, knowledge points, resources | program, grade, course, version | published version immutable |
| OBE/accreditation asset | graduation requirements, indicator points, support matrix, course objective mapping, achievement report | program, grade, course, term, version | mapping and calculation evidence traceable to assessment source |
| professional construction asset | 双高/professional-group task book, annual plan, evidence catalog, industry-research report, course-resource standard | program_group, task, owner, year | evidence must map to target, task, metric, owner, and review result |
| rubric/template | classroom evaluation rubric, teaching inspection checklist, diagnosis report template | scenario, evaluator, version | activation requires business owner |
| research asset | project guide, proposal, contract/task book, budget, ethics/integrity review, output proof, IP/transfer agreement | project_type, fund_source, PI, confidentiality | access by PI/research office/finance/audit scope; versioned |
| FAQ/AI knowledge | admissions FAQ, student affairs FAQ, academic affairs FAQ, IT support Q&A | source, audience, validity | cite source and freshness |
| indicator/report template | quality report, data-governance report, employment analysis | indicator_ids, scope, cutoff | frozen snapshot and traceable owner |
| workflow/form template | leave, award, aid, repair, certificate, approval forms | process_key, version, fields | field dictionary and approval path required |

## Core Workflows

| Workflow | Actors | Trigger | State Change | Success Result |
|---|---|---|---|---|
| academic term setup | academic affairs, college, teacher | new term preparation | teaching class planned -> published | course offerings, roster, timetable, exam basis established |
| course selection and adjustment | student, academic affairs, college | selection window opens | selected/waitlisted -> confirmed/dropped | student timetable and roster consistent |
| score release and appeal | teacher, academic affairs, student | grading completed | grading -> released; appeal -> closed | grades auditable; changes traceable |
| OBE achievement analysis | teacher, program leader, academic affairs, quality office | course/exam/assessment data available | mapped -> calculated -> reviewed -> improved | course objective and graduation requirement evidence traceable |
| professional-group construction | college, program leader, school leader, enterprise mentor | annual construction/task plan | executing -> diagnosing -> improved | 双高/professional/accreditation evidence and improvement closed |
| student affairs service | student/counselor/office | application submitted | submitted -> approved/rejected/returned | service result notified and archived |
| one-stop student community activity | student affairs, counselor, student organization | activity/service published | published -> running -> completed | participation, feedback, growth evidence, and network-ideology record archived |
| counseling/risk follow-up | counselor, student affairs, professional staff | risk signal or manual case | open -> following/referred/closed | follow-up evidence and privacy boundary recorded |
| classroom quality evaluation | teacher, evaluator, quality office | class observed or AI signal generated | analyzing -> reviewed -> published | reviewed result and improvement task produced |
| smart classroom operation | teacher, classroom admin, quality office | timetable or manual start | active/recording -> evidence generated -> archived | device, media, interaction, attendance, and classroom evidence traceable |
| training-plan revision | program leader, college, academic affairs | curriculum update | draft -> reviewing -> published | versioned plan applied to target grade |
| research project lifecycle | researcher/PI, research office, finance, ethics/integrity reviewer | call or project proposal | submitted -> approved -> executing -> accepted/closed | project, fund, output, compliance, and archive traceable |
| research output/IP transformation | researcher, research office, IP/technology-transfer office | output submitted or transfer opportunity | submitted -> verified -> published/transformed | attribution, proof, IP/contract, and reward basis recorded |
| one-stop service process | applicant, handler, approver | form/process submitted | submitted -> processing -> completed/returned | cross-department task closed with audit |
| data governance | data center, responsible office | standard/source integration | draft -> active/deprecated | master data, API, indicator, quality rules traceable |
| AI assistant answer/action | teacher/student/staff, AI assistant, responsible office | user asks / requests operation | draft answer/task -> human confirmed where consequential | answer cites source; action remains within permission |

## Role Path Patterns

| Role | Entry | Core Actions | Forbidden Actions | Exit |
|---|---|---|---|---|
| school leader | dashboard / data brain | inspect indicators, drill to college/program, assign follow-up | view unnecessary student-sensitive details | decision or follow-up task recorded |
| academic affairs office | academic affairs console | manage term, course, selection, exam, grade release, training plans | alter teacher/student data outside authority without audit | academic operation closed |
| student affairs office | student affairs console | manage aid/award/sanction/dorm/safety policies and cases | bypass counselor/professional review for sensitive cases | case result and archive |
| research office | research management console | manage project calls, approval, process checks, output verification, statistics | change PI/fund/output records without source proof and audit | research record archived or dashboard updated |
| finance/audit office | finance/research integration | review fund arrival, expenditure, reimbursement, settlement, audit evidence | decide academic output attribution or project acceptance | fund/audit status synchronized |
| counselor | counselor workbench/mobile | view own students, follow up warnings, submit/handle cases, record interviews | view other classes without authorization; AI-only crisis decision | follow-up completed or referred |
| teacher | teaching workbench | manage class resources, attendance, grading, feedback, improvement | view unrelated student affairs/mental data | teaching task completed |
| researcher / PI | research desk | submit project/output, track fund, upload evidence, request changes | view other PI confidential project/fund details | project/output/fund process advanced |
| student | portal/mobile/mini-program | apply services, check timetable/grades, learn, submit feedback, appeal | view other students or hidden evaluation data | service completed or progress visible |
| college/program leader | college dashboard | monitor program, teaching, students, quality tasks | change school-level standard without approval | improvement action closed |
| professional-group leader | program construction cockpit | manage professional-group tasks, curriculum/resource evidence, industry alignment | publish construction results without owner evidence | construction progress and diagnosis evidence updated |
| teaching quality office / evaluator | evaluation console/mobile | create/review evaluation, publish result, assign improvement | publish AI result without human review | quality evidence archived |
| data center/network office | data governance platform | manage standards, APIs, quality rules, identity, permissions | decide business caliber without owner office | data service active and monitored |
| IT administrator | system admin | configure tenant, org, roles, integrations, logs | access business content without audit/authorization | secure operation |

## UI / Mobile Patterns

- desktop patterns: dense lists with term/college/program/class filters, source labels, status-driven actions, evidence timeline, and drilldown from dashboard to object detail;
- mobile patterns: student/counselor/teacher task cards, service progress, timetable, approval, attendance, classroom evidence upload, weak-network drafts;
- one-stop service: service catalog -> form -> material check -> submit -> progress -> result/archive;
- dashboard/data brain: indicator caliber tooltip, source/freshness label, minimum-sample privacy guard, drill path, export audit;
- professional/OBE cockpit: goal tree -> task/evidence -> support matrix -> achievement result -> improvement item -> review closure;
- smart classroom: media/evidence preview, rubric scoring, AI suggestion side panel, human review button, appeal/history timeline;
- research management: call/project list, PI desk, fund ledger, output registry, integrity review, transformation/award evidence, dashboard drilldown;
- required testids: `nav-academic-affairs`, `nav-student-affairs`, `nav-research-management`, `nav-teaching-quality`, `nav-program-construction`, `nav-data-governance`, `tbl-course-selection`, `btn-submit-service`, `btn-return-case`, `btn-release-score`, `btn-calculate-achievement`, `btn-review-classroom-eval`, `btn-submit-research-project`, `badge-data-freshness`;
- role switch requirements: school leader, academic affairs, student affairs, research office, counselor, teacher, researcher/PI, student, quality office, data center/admin paths must be independently demoable when in scope.

## Policy / Privacy Constraints

- Student personal, academic, financial-aid, counseling, health, dorm, employment, and disciplinary data follow least privilege, masking, retention, and audit rules.
- Mental-health and counseling AI can provide triage hints or conversation assistance only; diagnosis, crisis level, and intervention decision require authorized human/professional accountability.
- Grades, credits, graduation eligibility, awards/aid/sanctions, and teacher evaluation conclusions require human approval and audit evidence.
- Classroom audio/video/image use requires clear purpose, role access, retention period, and display/export control.
- Research project, fund, contract, IP, ethics/integrity, and transformation data require confidentiality level, owner, proof attachment, finance/audit boundary, and export approval.
- OBE/accreditation, 双高, and audit-evaluation evidence must distinguish draft analysis from official school evidence; published evidence is versioned and cannot be silently overwritten.
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
| OBE achievement recalculation | teacher/program leader | score source changed after achievement calculated | recalculate -> compare old/new -> review -> publish improvement | source version, threshold, result, and improvement item traceable |
| professional-group evidence review | program leader/school leader | annual 双高/professional construction evidence uploaded | submit evidence -> owner review -> diagnose gap -> close improvement | evidence maps to target/task/indicator/owner |
| training-plan version change | program leader/academic affairs | published plan exists | create revision -> approve -> publish | old students keep old version; target grade uses new version |
| research project fund lifecycle | PI/research office/finance | project approved; fund arrives | register arrival -> allocate -> reimburse -> settle | fund state consistent with project and finance audit |
| research output duplicate/confidential check | researcher/research office | output submitted | verify proof -> check duplicate/confidentiality -> publish/archive | output attribution and visibility controlled |
| data standard activation | data center/owner office | new data standard drafted | owner review -> activate -> monitor quality | source owner and quality rules traceable |
| AI policy Q&A stale source | teacher/student | policy knowledge has old and new versions | ask question -> answer cites source | answer uses effective version or refuses with update warning |
| dashboard privacy threshold | school leader | small sample group exists | drill into sensitive student indicator | aggregate shown; student-level detail hidden without authority |

## Multi-Agent Lifecycle Verification Matrix

| domain_id | stage | reviewer_agent | path_type | scenario_ref | evidence_ref | blocking_question | expected_result | test_marker | verdict |
|---|---|---|---|---|---|---|---|---|---|
| education_it | Discover | PM Agent | happy_path | one-stop service / academic affairs | Domain Purpose | Is the education outcome measurable and scoped? | student/teacher/office value is explicit | education_discover_pm_happy_path | PASS |
| education_it | Discover | Domain Expert Agent | exception_path | policy Q&A stale source | Domain Test Scenarios | Are school policy versions and owners discovered? | stale source is refused or warned | education_discover_domain_exception_path | PASS |
| education_it | Discover | Architecture / Data / AI Agent | permission_privacy_path | student profile | AI Context Sources / Policy | Are student-sensitive sources scoped before use? | student_privacy_scope is required | student_privacy_scope | PASS |
| education_it | Discover | QA Agent | lifecycle_transition | TrainingPlan lifecycle | State Machines | Can QA identify published/revised/archived states? | plan lifecycle is testable | education_discover_qa_lifecycle_transition | PASS |
| education_it | Discover | Coding Agent | acceptance_test_path | delivery handoff | UI / Mobile Patterns | Can implementation trace source truth? | ac_structured, data-testid, data-action, data-state, data-api, data-method, manifest.json, source_of_truth_order required | ac_structured;data-testid;data-action;data-state;data-api;data-method;manifest.json;source_of_truth_order | PASS |
| education_it | Specify | PM Agent | happy_path | OBE achievement analysis | Core Workflows | Does PRD connect course evidence to improvement? | obe_evidence_trace maps source -> result -> improvement | obe_evidence_trace | PASS |
| education_it | Specify | Domain Expert Agent | exception_path | score release with appeal | Domain Test Scenarios | Are appeal and score adjustment rules explicit? | grade changes are human-approved and audited | grade_human_approval | PASS |
| education_it | Specify | Architecture / Data / AI Agent | permission_privacy_path | dashboard drilldown | UI / Mobile Patterns / Policy | Are small-sample privacy guards specified? | dashboard_privacy_threshold blocks student-level leakage | dashboard_privacy_threshold | PASS |
| education_it | Specify | QA Agent | lifecycle_transition | StudentAffairsCase returned | State Machines | Can returned/resubmitted paths be tested? | returned -> resubmitted -> processing exists | education_specify_qa_lifecycle_transition | PASS |
| education_it | Specify | Coding Agent | acceptance_test_path | FRR/AC contract | Acceptance Checklist | Can coding agent implement without guessing school policy? | FRR, AC, field, permission, state are traceable | education_specify_coding_acceptance_test_path | PASS |
| education_it | Plan | PM Agent | happy_path | professional construction | Core Workflows | Are annual construction owners and metrics planned? | target/task/indicator/owner/evidence chain exists | obe_evidence_trace | PASS |
| education_it | Plan | Domain Expert Agent | exception_path | scholarship/aid review | Domain Test Scenarios | Are high-stakes student decisions human-owned? | final aid/award result requires human approval | grade_human_approval | PASS |
| education_it | Plan | Architecture / Data / AI Agent | permission_privacy_path | research/fund data | Policy / Privacy Constraints | Are confidentiality and finance/audit scopes planned? | research data access is scoped/versioned/audited | education_plan_arch_permission_privacy_path | PASS |
| education_it | Plan | QA Agent | lifecycle_transition | CourseObjectiveAchievement | State Machines | Can QA plan achievement recalculation tests? | mapped -> calculated -> reviewed -> improved path exists | obe_evidence_trace | PASS |
| education_it | Plan | Coding Agent | acceptance_test_path | delivery package | UI / Mobile Patterns | Are view/action/testid paths discoverable? | source_of_truth_order and manifest are required | source_of_truth_order;manifest.json | PASS |
| education_it | Tasks | PM Agent | happy_path | student affairs service | Core Workflows | Are tasks sliced by service closure? | submitted -> result/archive can be delivered vertically | education_tasks_pm_happy_path | PASS |
| education_it | Tasks | Domain Expert Agent | exception_path | counseling risk follow-up | Domain Test Scenarios | Are sensitive mental-health paths separated? | AI cannot diagnose; referral/closure evidence exists | student_privacy_scope | PASS |
| education_it | Tasks | Architecture / Data / AI Agent | permission_privacy_path | cross-system master data | Policy / Privacy Constraints | Do tasks preserve authoritative source and conflict rules? | source owner/freshness/conflict resolution recorded | education_tasks_arch_permission_privacy_path | PASS |
| education_it | Tasks | QA Agent | lifecycle_transition | SmartClassroomSpace | State Machines | Are classroom device/evidence states planned? | active/maintenance/disabled paths are testable | education_tasks_qa_lifecycle_transition | PASS |
| education_it | Tasks | Coding Agent | acceptance_test_path | mobile weak network | UI / Mobile Patterns | Can coding tasks cover student/teacher/counselor mobile paths? | data-* and offline behavior are testable | data-testid;data-action;data-state | PASS |
| education_it | Build/Verify | PM Agent | happy_path | classroom AI evaluation | Domain Test Scenarios | Does build prove AI is evidence, not final evaluation? | human review publishes result | education_build_pm_happy_path | PASS |
| education_it | Build/Verify | Domain Expert Agent | exception_path | training-plan version change | Domain Test Scenarios | Are old/new student cohorts protected? | old students keep old plan; target grade uses new version | education_build_domain_exception_path | PASS |
| education_it | Build/Verify | Architecture / Data / AI Agent | permission_privacy_path | AI assistant answer | AI Context Sources | Does AI cite effective policy and preserve scope? | answer cites source/freshness or refuses | education_build_arch_permission_privacy_path | PASS |
| education_it | Build/Verify | QA Agent | lifecycle_transition | research project fund lifecycle | Domain Test Scenarios | Can integration tests cover project/fund states? | arrival/allocation/reimbursement/settlement traceable | education_build_qa_lifecycle_transition | PASS |
| education_it | Build/Verify | Coding Agent | acceptance_test_path | AC/prototype check | Acceptance Checklist | Can coding agent bind tests to AC and data-*? | ac_structured and data-* coverage exist | ac_structured;data-testid;data-action | PASS |
| education_it | Launch | PM Agent | happy_path | indicator dashboard | Metric / Indicator Governance | Are school dashboards launch-ready with caliber/source? | indicator owner/source/version/privacy level visible | dashboard_privacy_threshold | PASS |
| education_it | Launch | Domain Expert Agent | exception_path | grade/final decision | Policy / Privacy Constraints | Are official educational decisions human-approved? | final grades/graduation/aid/sanction need accountable human | grade_human_approval | PASS |
| education_it | Launch | Architecture / Data / AI Agent | permission_privacy_path | export/API opening | Policy / Privacy Constraints | Are data export and API scope protected? | org/role/cohort/course scopes enforced | student_privacy_scope | PASS |
| education_it | Launch | QA Agent | lifecycle_transition | ServiceProcess launch | State Machines | Can smoke tests verify submitted -> completed/returned/cancelled? | service process path is testable | education_launch_qa_lifecycle_transition | PASS |
| education_it | Launch | Coding Agent | acceptance_test_path | release package | Acceptance Checklist | Can coding agent identify launch blockers? | lifecycle, permission, AI boundary, and acceptance evidence present | education_launch_coding_acceptance_test_path | PASS |
| education_it | Learn/Retire | PM Agent | happy_path | continuous improvement | Core Workflows | Can learning close teaching quality improvement? | issue -> action -> review -> closure metrics exist | education_learn_pm_happy_path | PASS |
| education_it | Learn/Retire | Domain Expert Agent | exception_path | deprecated policy/course plan | Content / Knowledge Assets | Can retired rules stop affecting new students? | versioned policy/plan lifecycle is explicit | education_learn_domain_exception_path | PASS |
| education_it | Learn/Retire | Architecture / Data / AI Agent | permission_privacy_path | student record retention | Policy / Privacy Constraints | Are sensitive student/classroom records retained/deleted correctly? | retention, masking, audit, export controls apply | student_privacy_scope | PASS |
| education_it | Learn/Retire | QA Agent | lifecycle_transition | DataResource deprecated | State Machines | Can QA verify data standard retirement? | active -> deprecated is testable | education_learn_qa_lifecycle_transition | PASS |
| education_it | Learn/Retire | Coding Agent | acceptance_test_path | regression continuity | Acceptance Checklist | Can implementation preserve AC and evidence history? | source_of_truth_order and historical IDs remain traceable | source_of_truth_order | PASS |

## Acceptance Checklist

- [ ] All 14 domain module sections are present.
- [ ] Academic affairs, student affairs, research management, teaching quality, professional construction, one-stop service, data governance, and AI assistant boundaries are explicit when relevant.
- [ ] Student, teacher, course, teaching class, score, service case, classroom evaluation, OBE achievement, research project/fund/output, data resource, and indicator lifecycles are defined.
- [ ] Authoritative source, owner department, freshness, and conflict-resolution rule are named for cross-system data.
- [ ] Sensitive student and classroom data are masked, scoped, retained, and audited.
- [ ] Research fund, contract, IP, ethics/integrity, and confidential output data are scoped, versioned, retained, and audited.
- [ ] Professional construction, accreditation, and audit-evaluation evidence maps target -> task -> indicator -> owner -> evidence -> improvement.
- [ ] AI outputs show source/freshness/confidence and cannot finalize high-stakes educational decisions.
- [ ] Mobile/student/teacher/counselor paths include weak-network, notification, and permission behavior where in scope.
- [ ] Every dashboard/report metric has caliber, source, dimension, owner, version, and acceptance evidence.
