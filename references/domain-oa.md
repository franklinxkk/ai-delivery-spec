# Domain: OA / Collaborative Office

Use this file for OA, collaborative office, employee workspace, workflow
automation, official document, meeting, task, portal, knowledge, e-signature,
and enterprise intelligent office scenarios.

This is a replaceable domain module. Public protocol files must stay
domain-neutral.

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
- Multi-Module PRD Quality Gate
- Acceptance Checklist

## Domain Purpose

- Business outcome: make work items, approvals, documents, meetings, tasks,
  knowledge, service requests, and management decisions traceable, timely, and
  closable across organization boundaries.
- Primary users: employee, department manager, executive, secretary/office
  clerk, workflow administrator, document officer, meeting organizer, HR,
  finance, legal, IT/helpdesk, system administrator, auditor, and AI office
  assistant user.
- Regulated or sensitive areas: official documents, approval opinions,
  contracts, finance reimbursement, personnel and performance data, meeting
  minutes, seal/signature records, organization permissions, audit logs,
  exported files, watermarks, and AI conversation context.
- AI may optimize: task summarization, meeting minutes, document drafting,
  knowledge Q&A, smart search, workflow routing suggestion, deadline
  supervision, report insight, policy explanation, service triage, and office
  assistant actions that remain human-confirmed.
- AI must not decide automatically: final approval/rejection, official document
  issuance, contract signing, seal/e-signature application, payment approval,
  personnel decision, performance result, deletion/destruction of records, or
  cross-org data access.
- Capability scope may include IM/portal, unified todo, workflow approval,
  official document, meeting, calendar, task/supervision, knowledge, cloud docs,
  low-code forms, data/reporting, helpdesk, HR/expense/legal integrations,
  mobile office, e-signature, and AI office assistant.
- Stage 3.5 IA Skeleton should be used when the OA scope covers two or more
  modules, two or more primary roles, PC+mobile surfaces, or any cross-module
  lifecycle such as todo -> workflow -> document -> archive.
- FRR anti-bloat rule: do not repeat common page layout, org fields, user
  fields, workflow-node fields, and document metadata in every OA function.
  Lock module/view/region/action in the IA Skeleton, place common fields in
  the global field dictionary, and keep each FRR focused on scenario, state,
  rule, permission, exception, and acceptance differences.

## First-Principles Domain Lens

OA product judgment starts from accountable work closure, not from a catalog of
forms, portals, or chat features.

| Lens | OA Question | Acceptance Signal |
|---|---|---|
| Work object | Which work item, approval, document, meeting, task, service request, or knowledge artifact changes? | object owner, source module, state, and audit are explicit |
| Accountability | Who must respond, by when, with what evidence, and what closes the work? | todo SLA, handler, decision, opinion/evidence, and close guard are testable |
| Document authority | Which artifact is the source of truth for content, version, opinion, seal/signature, and archive? | document_authority order is stated before build |
| Workflow physics | Which state transition proves real handling rather than notification-only movement? | node action, state change, event, and audit are aligned |
| Permission scope | Which org, role, field, document level, or temporary delegation allows access? | org_permission_scope blocks horizontal and vertical overreach |
| Human gate | Which high-impact office actions must remain human-accountable? | workflow_human_gate protects approval, issue, seal, payment, HR, and archive decisions |
| AI boundary | Which AI output is draft, suggestion, retrieval, or action proposal? | ai_office_assistant_boundary states citation, confidence, forbidden write, and fallback |
| Test evidence | Which happy, rejection, timeout, weak-network, permission, duplicate, and dependency-failure paths prove closure? | QA can convert state and role paths into AC/test cases |

## Vocabulary

| Term | Meaning | Source of Truth |
|---|---|---|
| OA / Collaborative Office | enterprise collaboration suite for workflow, documents, meetings, tasks, portal, and knowledge | OA platform |
| Unified Todo | cross-module work queue for approvals, documents, tasks, service requests, and reminders | todo center |
| Workflow Instance | running approval/handling process created from a workflow definition | workflow engine |
| Workflow Node | step with handler, action set, timeout, condition, and audit | workflow engine |
| Official Document | formal received/issued/report document with number, template, opinion, seal, and archive rules | document module |
| Circulation / Notification | non-decision routing for reading, copying, or informing | workflow/document module |
| Countersign | parallel or sequential multi-person approval with configured pass rule | workflow engine |
| Supervision Task | management task that tracks deadline, progress, reminder, escalation, and closure | task/supervision module |
| Meeting Resolution | meeting decision item that must be assigned, tracked, and closed | meeting module |
| Knowledge Asset | policy, SOP, FAQ, wiki, document, or historical case used for search/Q&A | knowledge module |
| Cloud Document | collaborative document, sheet, base/table, or page with version and comments | document/collaboration module |
| E-Signature / Seal | certificate, seal, signing action, timestamp, and verification record | e-signature service |
| Helpdesk Ticket | internal IT/HR/admin/legal/finance service request | service desk module |
| Low-Code App | form, workflow, report, automation, and permission app built by configuration | low-code platform |
| AI Office Assistant | AI feature that summarizes, drafts, searches, routes, or proposes actions | AI assistant platform |

## Aggregates and Entities

| Aggregate | Owns | Key States | Notes |
|---|---|---|---|
| WorkItem | object ref, title, owner, priority, deadline, source | pending / read / processing / overdue / closed / cancelled | normalized todo/task abstraction |
| WorkflowDefinition | nodes, conditions, handlers, version, form binding | draft / published / deprecated | published version is immutable for running instances |
| WorkflowInstance | form data, current node, opinions, attachments, audit | draft / running / returned / rejected / completed / terminated | source of approval state |
| WorkflowNode | handler, action, timeout, delegation, pass rule | pending / processed / timeout / transferred / skipped | node state drives buttons |
| OfficialDocument | doc number, title,正文/body, template, level, seal, archive | draft / reviewing / issued / distributed / archived / withdrawn | document_authority required |
| Meeting | agenda, room/link, participants, minutes, resolutions | draft / scheduled / in_progress / minutes_pending / closed / cancelled | resolution tasks must be traceable |
| SupervisionTask | source object, target org/user, deadline, reminders, evidence | created / executing / overdue / escalated / completed / closed | management accountability |
| KnowledgeAsset | content, category, tags, version, permission, index | draft / published / updated / deprecated / archived | AI Q&A cites asset version |
| CloudDocument | content, collaborators, comments, versions, permission | draft / collaborating / published / archived | real-time collaboration surface |
| HelpdeskTicket | requester, category, SLA, assignee, solution | new / assigned / processing / pending_user / resolved / closed | internal service request |
| ESignatureRecord | certificate, seal, signer, file hash, timestamp | pending / signed / revoked / expired / failed | high-risk audit entity |
| OrganizationUnit | hierarchy, leader, scope, status | active / merged / disabled / archived | permission backbone |
| RolePermission | menu, action, data, field, delegation | active / suspended / deprecated | access must be auditable |
| AIConversation | prompt, source refs, output, confidence, user decision | generated / shown / accepted / modified / rejected / suppressed | no consequential write without gate |

## Domain Events

```yaml
events:
  TodoCreated:
    payload: { todo_id, object_type, object_id, handler_id, deadline, source_module }
  WorkflowSubmitted:
    payload: { instance_id, definition_id, submitter_id, submitted_at }
  WorkflowNodeCompleted:
    payload: { instance_id, node_id, handler_id, action, opinion, completed_at }
  WorkflowReturned:
    payload: { instance_id, node_id, handler_id, return_to_node, reason, returned_at }
  WorkflowCompleted:
    payload: { instance_id, final_state, duration, completed_at }
  OfficialDocumentIssued:
    payload: { doc_id, doc_number, issuer_id, issue_time, distribution_scope }
  OfficialDocumentArchived:
    payload: { doc_id, archive_id, archive_user_id, archived_at }
  MeetingMinutesPublished:
    payload: { meeting_id, minutes_id, publisher_id, resolution_count, published_at }
  SupervisionTaskEscalated:
    payload: { task_id, reason, escalated_to, escalated_at }
  HelpdeskTicketResolved:
    payload: { ticket_id, resolver_id, solution_ref, resolved_at }
  ESignatureApplied:
    payload: { signature_id, object_type, object_id, signer_id, file_hash, signed_at }
  KnowledgeAssetIndexed:
    payload: { asset_id, index_version, indexed_at }
  AIOfficeSuggestionReviewed:
    payload: { ai_record_id, reviewer_id, decision, reason, reviewed_at }
```

## State Machines

```text
WorkItem: pending -> read -> processing -> closed
WorkItem: pending | processing -> overdue -> escalated -> closed

WorkflowInstance: draft -> running -> completed
WorkflowInstance: running -> returned -> running
WorkflowInstance: running -> rejected | terminated

WorkflowNode: pending -> processed
WorkflowNode: pending -> timeout -> processed | transferred | escalated

OfficialDocument: draft -> reviewing -> issued -> distributed -> archived
OfficialDocument: issued | distributed -> withdrawn

Meeting: draft -> scheduled -> in_progress -> minutes_pending -> closed
Meeting: scheduled -> cancelled

SupervisionTask: created -> executing -> completed -> closed
SupervisionTask: executing -> overdue -> escalated -> completed

HelpdeskTicket: new -> assigned -> processing -> resolved -> closed
HelpdeskTicket: processing -> pending_user -> processing

KnowledgeAsset: draft -> published -> updated -> deprecated -> archived
AIRecommendation: generated -> shown -> accepted | modified | rejected
AIRecommendation: generated -> suppressed_low_confidence | suppressed_policy_block
```

State rules:

- Published workflow definitions and official document templates are versioned;
  running instances keep the version snapshot used at submit time.
- Buttons are state-driven: action availability depends on current state, role,
  delegation, timeout, and document level.
- Sealed/signed/archived files cannot be silently edited. Correction requires
  new version, reason, operator, timestamp, and retained evidence.
- AI output cannot skip workflow_human_gate. It may draft, summarize, search, or
  propose, but accountable users confirm consequential state changes.

## Metric / Indicator Governance

| Metric | Caliber | Source | Owner |
|---|---|---|---|
| todo_on_time_close_rate | closed todos before deadline / due todos | todo + workflow | operations owner |
| workflow_average_duration | completed workflow duration by definition/version | workflow engine | process admin |
| node_timeout_count | workflow nodes exceeding configured SLA | workflow engine | process admin |
| return_reject_rate | returned/rejected instances / submitted instances | workflow engine | process owner |
| official_document_issue_cycle | time from draft submit to issue | document module | office/document owner |
| document_read_completion_rate | required readers completed reading / required readers | document distribution | document owner |
| meeting_resolution_close_rate | closed meeting resolution tasks / generated tasks | meeting + task | meeting owner |
| supervision_overdue_count | overdue supervision tasks by org/owner | supervision module | executive office |
| knowledge_answer_citation_rate | AI answers with valid cited sources / AI answers | knowledge + AI trace | knowledge owner |
| helpdesk_sla_breach_count | internal service tickets exceeding SLA | helpdesk | service owner |
| mobile_approval_success_rate | mobile approvals completed without retry/failure | mobile + workflow | product owner |
| e_signature_failure_rate | failed or revoked signing records / signing attempts | e-signature service | legal/IT owner |

Every metric must state subject, denominator, time window, org scope, data
freshness, owner, and whether exports use masked or raw values.

## AI Context Sources

| Context | Source | Freshness | Permission Scope | Risk |
|---|---|---|---|---|
| workflow/form history | workflow engine | real-time | handler, owner, authorized manager | approval opinion leakage |
| official documents | document module/archive | versioned | document level + distribution scope | confidential document exposure |
| knowledge/SOP/wiki | knowledge base | daily/versioned | asset permission | stale policy answer |
| org/user/role data | organization platform | real-time/daily | org_permission_scope | horizontal or vertical overreach |
| meeting transcripts/minutes | meeting service | real-time/versioned | participant/authorized roles | sensitive decision leakage |
| cloud documents | doc collaboration platform | real-time/versioned | document ACL | comment/version leakage |
| service tickets | helpdesk | real-time | requester/assignee/service owner | personal or HR data leakage |
| finance/expense/contract refs | finance/legal systems | real-time/versioned | role and field masks | money/legal decision risk |

```yaml
ai_office_context_source:
  source_id:
  owner_system:
  permission_check:
  freshness_sla:
  sensitivity_level: public | internal | confidential | secret
  allowed_ai_use: search | summarize | draft | classify | propose_action
  prohibited_ai_use:
  citation_required: true
  human_gate_required: true
  audit_fields: [trace_id, user_id, role_id, object_id, source_version, used_at]
```

## Content / Knowledge Assets

| Asset | Use | Governance |
|---|---|---|
| workflow templates | request/approval lifecycle | owner, version, effective date, deprecation |
| official document templates | format, header, numbering, distribution | office authority, template version |
| policies and SOPs | knowledge Q&A, workflow rules, service answers | issuer, effective date, applicability |
| org/role dictionaries | routing and permissions | HR/admin owner, sync cadence |
| meeting minutes/resolutions | task generation and decision trace | publisher, participant scope, version |
| seal/signature rules | e-signature workflow | legal/IT owner, certificate status |
| helpdesk solution library | internal service triage | service owner, rating, update date |
| AI prompt/model registry | assistant behavior | golden cases, owner, rollback |

Vendor capability register should be treated as source evidence, not product
truth. Domestic OA and work platforms commonly contribute patterns such as
workflow/document/portal strength, IM and cloud docs, low-code app building,
customer contact, e-signature, knowledge management, AI assistant, and
Xinchuang/private deployment. Global collaboration platforms commonly
contribute patterns such as team workspace, shared docs, workflow automation,
employee service center, knowledge search, task/project tracking, and AI
summarization. A PRD must state which benchmark pattern is in scope and which
is deliberately deferred.

## Core Workflows

| Workflow | Actors | Trigger | State Change | Success Result |
|---|---|---|---|---|
| unified todo handling | employee/manager | todo created by workflow/document/task | pending -> processing -> closed | work item closed with evidence |
| workflow approval | submitter/approver/admin | form submitted | draft -> running -> completed/returned/rejected | decision, opinion, audit, notification |
| official document issue | drafter/document officer/leader | document draft submitted | draft -> reviewing -> issued -> archived | numbered, distributed, archived document |
| meeting to resolution | organizer/participant/resolution owner | meeting ends | minutes_pending -> closed; tasks created | resolutions assigned and traceable |
| supervision follow-up | executive office/target org | key task created or overdue | executing -> completed/closed | deadline, reminders, evidence, closure |
| knowledge Q&A | employee/AI assistant | question submitted | generated -> reviewed/used | cited answer or safe refusal |
| helpdesk service | employee/service owner | service request created | new -> resolved -> closed | requester confirms or timeout closes |
| e-signature | applicant/legal/signer | sign request approved | pending -> signed/failed | valid signature record and file hash |
| low-code app publish | business admin/platform admin | app configured | draft -> published -> updated/deprecated | governed form/workflow/report app |
| mobile approval | mobile employee/manager | todo opened on mobile | pending -> processed | server-validated action with fallback |

## Role Path Patterns

| Role | Entry | Core Actions | Forbidden Actions | Exit |
|---|---|---|---|---|
| Employee | portal/mobile todo | submit form, handle todo, read docs, ask knowledge | approve own restricted process unless rule allows | work submitted/handled |
| Department Manager | dashboard/todo | approve, return, assign, supervise, view dept metrics | view other departments without scope | accountable decision |
| Executive | cockpit/supervision | inspect exceptions, create supervision, sign/approve high-level items | edit raw workflow/document records silently | exception closure |
| Document Officer | document workspace | number, distribute, archive, withdraw by rule | change issued content without version | document lifecycle closed |
| Meeting Organizer | calendar/meeting module | schedule, collect agenda, publish minutes, create tasks | falsify participant confirmation | resolutions traceable |
| Process Admin | workflow designer | configure templates, nodes, SLA, permissions | modify running instance without audit | versioned workflow |
| HR/Finance/Legal | specialty workspace | handle personnel, expense, contract, seal processes | bypass human gate or field masking | compliant decision |
| IT/Helpdesk | service desk | assign, resolve, maintain solution library | access unrelated personnel/finance data | service closed |
| Auditor | audit center | inspect logs, exports, signatures, data access | alter business records | evidence exported |
| AI Assistant User | search/assistant panel | ask, draft, summarize, propose action | let AI publish/approve/sign directly | reviewed suggestion |

## UI / Mobile Patterns

Stable test identifiers for OA prototypes:

| Pattern | Recommended `data-testid` / `data-action` |
|---|---|
| portal and unified todo | `page-portal`, `table-unified-todo`, `btn-handle-todo` |
| workflow approval | `page-workflow-center`, `form-workflow-submit`, `btn-approve`, `btn-return`, `modal-approval-opinion` |
| official document | `page-official-document`, `btn-issue-document`, `btn-distribute-document`, `btn-archive-document` |
| meeting and resolution | `page-meeting`, `btn-publish-minutes`, `table-resolution-tasks` |
| supervision | `page-supervision`, `btn-create-supervision`, `btn-escalate-supervision` |
| knowledge and AI assistant | `panel-ai-office-assistant`, `btn-review-ai-suggestion`, `badge-source-citation` |
| e-signature | `modal-signature-confirm`, `btn-apply-seal`, `badge-signed-file` |
| low-code workflow | `page-lowcode-app`, `canvas-workflow`, `btn-publish-workflow-version` |
| mobile approval | `page-mobile-todo`, `btn-mobile-approve`, `banner-offline-draft` |

IA Skeleton examples:

- `M01-V01`: portal and unified todo cockpit.
- `M02-V01`: workflow approval center.
- `M03-V01`: official document workspace.
- `M04-V01`: meeting and resolution workspace.
- `M05-V01`: supervision and task tracking.
- `M06-V01`: knowledge and AI office assistant.
- `M02-V01-mobile`: mobile approval when layout/offline behavior differs.

Mobile rules:

- Mobile approval must show object title, applicant, current node, opinion
  history, attachments, permission, and offline/failure state.
- Offline mode may save drafts, but approve/reject/sign/seal/archive must wait
  for server validation.
- PC+mobile consistency must preserve the same business state machine, audit,
  data permission, and domain events.

## Policy / Privacy Constraints

- Data minimization: every role path must justify access to org, person,
  document, approval opinion, finance, HR, legal, or meeting content.
- Permission isolation: org_permission_scope must cover menu, action, data,
  field, document level, export, mobile, API, and AI context retrieval.
- Approval accountability: workflow_human_gate is mandatory for approval,
  rejection, issue, seal/signature, payment, HR, performance, and archive.
- Document integrity: issued, sealed, signed, or archived documents use
  versioned correction/withdrawal, not silent overwrite.
- E-signature: certificate status, signer identity, file hash, timestamp,
  revocation, and verification evidence are required.
- Export and watermark: sensitive export needs permission, watermark, reason,
  audit, and retention/deletion rule.
- AI boundary: AI suggestions require citation, confidence/quality boundary,
  forbidden write scope, fallback, and review record.
- Test/shadow data: automated tests must not create real approval, seal,
  payment, personnel, or official-document side effects.
- Compliance/source freshness: PRDs must record applicable laws, company
  policies, government/SOE rules, privacy/security requirements, and deployment
  constraints such as private deployment, Xinchuang, or cross-border data.

## Domain Test Scenarios

| ID | Scenario | Expected Result |
|---|---|---|
| OA-001 | Employee submits expense workflow and manager returns it | instance returns to configured node with opinion, editable fields, audit, and todo |
| OA-002 | Approver opens a stale todo after another approver has processed it | system blocks duplicate action and refreshes current state |
| OA-003 | Official document is issued then needs correction | withdrawal/correction creates versioned evidence; original remains auditable |
| OA-004 | Meeting minutes publish three resolutions | resolution tasks are created with owner, deadline, reminders, and close evidence |
| OA-005 | Supervision task is overdue | reminder/escalation creates visible owner action and audit trail |
| OA-006 | Employee asks AI to summarize a confidential document outside scope | AI refuses or hides source; access is audited |
| OA-007 | Mobile manager approves during weak network | draft opinion is preserved; final approval waits for server validation |
| OA-008 | Workflow definition changes while old instances are running | old instances continue on snapshot version; new submits use new version |
| OA-009 | E-signature certificate is expired | signing is blocked and routed to certificate renewal/manual handling |
| OA-010 | Browser test submits a real approval path | request uses shadow/test mode; no production workflow/seal/payment side effect remains |

## Multi-Agent Lifecycle Verification Matrix

| domain_id | stage | reviewer_agent | path_type | scenario_ref | evidence_ref | blocking_question | expected_result | test_marker | verdict |
|---|---|---|---|---|---|---|---|---|---|
| oa | Discover | PM Agent | happy_path | unified todo and workflow closure | Domain Purpose / Core Workflows | Is the product outcome accountable work closure rather than feature list? | work object, owner, SLA, and close evidence are explicit | todo_sla_close_guard | PASS |
| oa | Discover | Domain Expert Agent | exception_path | official document correction | Domain Test Scenarios | Are issued/sealed/archived document changes handled by versioned correction? | document_authority and correction path are mandatory | document_authority | PASS |
| oa | Discover | Architecture / Data / AI Agent | permission_privacy_path | org and document permission | Policy / Privacy Constraints | Are org, document-level, field, export, API, and AI scopes identified? | org_permission_scope is required before PRD handoff | org_permission_scope | PASS |
| oa | Discover | QA Agent | lifecycle_transition | workflow instance lifecycle | State Machines | Can QA see submit, approve, return, reject, terminate, and complete paths? | workflow state machine is testable | oa_discover_qa_lifecycle_transition | PASS |
| oa | Discover | Coding Agent | acceptance_test_path | coding package | UI / Mobile Patterns | Can implementation trace views/actions/states and package files? | ac_structured, data-testid, data-action, data-state, data-api, data-method, manifest.json, source_of_truth_order required | ac_structured;data-testid;data-action;data-state;data-api;data-method;manifest.json;source_of_truth_order | PASS |
| oa | Specify | PM Agent | happy_path | approval handling | Core Workflows | Does each approval path state visible result and accountable decision? | workflow_human_gate and audit are explicit | workflow_human_gate | PASS |
| oa | Specify | Domain Expert Agent | exception_path | stale todo duplicate action | Domain Test Scenarios | Are stale-state and duplicate-processing guards specified? | duplicate action is blocked and state refreshes | oa_specify_domain_exception_path | PASS |
| oa | Specify | Architecture / Data / AI Agent | permission_privacy_path | AI document summary | AI Context Sources / Policy | Does AI cite permitted sources and refuse out-of-scope documents? | ai_office_assistant_boundary is testable | ai_office_assistant_boundary | PASS |
| oa | Specify | QA Agent | lifecycle_transition | official document lifecycle | State Machines | Can QA test draft, review, issue, distribute, archive, and withdraw? | document lifecycle is explicit | document_authority | PASS |
| oa | Specify | Coding Agent | acceptance_test_path | FRR/AC contract | Acceptance Checklist | Can coding agent implement without inventing workflow buttons? | buttons derive from state, role, node, and permission | oa_specify_coding_acceptance_test_path | PASS |
| oa | Plan | PM Agent | happy_path | meeting resolutions | Core Workflows | Are minutes and resolution tasks linked to accountable owners? | meeting resolutions create traceable tasks | oa_plan_pm_happy_path | PASS |
| oa | Plan | Domain Expert Agent | exception_path | workflow template version change | State Machines | Are running instances protected from definition drift? | snapshot version behavior is explicit | oa_plan_domain_exception_path | PASS |
| oa | Plan | Architecture / Data / AI Agent | permission_privacy_path | export and watermark | Policy / Privacy Constraints | Are export reason, watermark, retention, and audit planned? | sensitive export is governed | org_permission_scope | PASS |
| oa | Plan | QA Agent | lifecycle_transition | helpdesk ticket lifecycle | State Machines | Can QA plan service request open, assign, resolve, close, and pending-user paths? | helpdesk lifecycle is testable | oa_plan_qa_lifecycle_transition | PASS |
| oa | Plan | Coding Agent | acceptance_test_path | AGENTS handoff | UI / Mobile Patterns | Are delivery paths and source order defined? | delivery/manifest and source_of_truth_order are required | source_of_truth_order;manifest.json | PASS |
| oa | Tasks | PM Agent | happy_path | mobile approval | UI / Mobile Patterns | Are tasks sliced by user-visible approval completion? | mobile path preserves state, evidence, and fallback | oa_tasks_pm_happy_path | PASS |
| oa | Tasks | Domain Expert Agent | exception_path | expired e-signature certificate | Domain Test Scenarios | Is signature blocked with renewal/manual path? | e-signature failure is not silent | oa_tasks_domain_exception_path | PASS |
| oa | Tasks | Architecture / Data / AI Agent | permission_privacy_path | HR/finance/legal fields | Policy / Privacy Constraints | Do implementation tasks preserve field-level masks? | sensitive fields remain scoped and audited | org_permission_scope | PASS |
| oa | Tasks | QA Agent | lifecycle_transition | supervision overdue path | State Machines | Are overdue, escalation, completion, and closure testable? | todo_sla_close_guard has tests | todo_sla_close_guard | PASS |
| oa | Tasks | Coding Agent | acceptance_test_path | data-* mapping | UI / Mobile Patterns | Can tasks map primary controls to actions and APIs? | data-testid/data-action/data-state/data-api/data-method are required | data-testid;data-action;data-state;data-api;data-method | PASS |
| oa | Build/Verify | PM Agent | happy_path | portal exception cockpit | Role Path Patterns | Does build show owner action and closure evidence for exceptions? | manager can verify reduced overdue work | oa_build_pm_happy_path | PASS |
| oa | Build/Verify | Domain Expert Agent | exception_path | document withdrawal | Domain Test Scenarios | Does withdrawal preserve original issued evidence? | version/audit trail remains intact | document_authority | PASS |
| oa | Build/Verify | Architecture / Data / AI Agent | permission_privacy_path | unauthorized cross-org todo | Policy / Privacy Constraints | Can one org see or process another org's work item? | access is refused without leakage | org_permission_scope | PASS |
| oa | Build/Verify | QA Agent | lifecycle_transition | weak-network mobile approval | Domain Test Scenarios | Does weak network avoid duplicate approval and data loss? | server validation and draft preservation are testable | oa_build_qa_lifecycle_transition | PASS |
| oa | Build/Verify | Coding Agent | acceptance_test_path | automated test isolation | Domain Test Scenarios | Can tests run without real approval/seal/payment effects? | shadow/test mode is required | ac_structured;data-testid;data-action | PASS |
| oa | Launch | PM Agent | happy_path | workflow go-live | Metric / Indicator Governance | Are adoption, SLA, return/reject, and timeout metrics launch-ready? | launch dashboard has calibrated metrics | oa_launch_pm_happy_path | PASS |
| oa | Launch | Domain Expert Agent | exception_path | document/seal compliance | Policy / Privacy Constraints | Are seal, archive, retention, and correction policies verified? | document_authority and human gate are launch blockers | document_authority;workflow_human_gate | PASS |
| oa | Launch | Architecture / Data / AI Agent | permission_privacy_path | production AI assistant | AI Context Sources | Are source permission, citation, fallback, and forbidden writes enforced? | ai_office_assistant_boundary is production-ready | ai_office_assistant_boundary | PASS |
| oa | Launch | QA Agent | lifecycle_transition | smoke tests | State Machines | Can smoke tests cover submit, approve, return, reject, and complete? | workflow state smoke tests pass | oa_launch_qa_lifecycle_transition | PASS |
| oa | Launch | Coding Agent | acceptance_test_path | release package | Acceptance Checklist | Can coding agent identify release blockers? | package paths and acceptance evidence are explicit | oa_launch_coding_acceptance_test_path | PASS |
| oa | Learn/Retire | PM Agent | happy_path | process efficiency review | Metric / Indicator Governance | Can post-launch data decide optimize, expand, or retire workflow? | metrics have owner, source, and decision rule | oa_learn_pm_happy_path | PASS |
| oa | Learn/Retire | Domain Expert Agent | exception_path | stale policy knowledge | Content / Knowledge Assets | Can deprecated SOP stop affecting AI answers and workflows? | stale knowledge is deprecated and reindexed | ai_office_assistant_boundary | PASS |
| oa | Learn/Retire | Architecture / Data / AI Agent | permission_privacy_path | retained audit/export data | Policy / Privacy Constraints | Are retention, deletion/export proof, and audit immutability preserved? | retention scope remains enforceable | org_permission_scope | PASS |
| oa | Learn/Retire | QA Agent | lifecycle_transition | workflow retirement | State Machines | Can old workflow stop new submits while old instances finish? | deprecated workflow migration is testable | oa_learn_qa_lifecycle_transition | PASS |
| oa | Learn/Retire | Coding Agent | acceptance_test_path | historical AC continuity | Acceptance Checklist | Do old AC IDs and source truth remain stable after iteration? | source_of_truth_order and ac_structured remain traceable | source_of_truth_order;ac_structured | PASS |

## Multi-Module PRD Quality Gate

Apply this gate after generating all OA module PRDs or after splitting a large
OA PRD into a master contract plus module PRDs. Any failed required item means
`REVIEW_COMPLETE_WITH_GAPS`.

| Gate | Required Condition | Blocks |
|---|---|---|
| OA-G1 Work object traceability | Every todo/task/workflow/document item has source module, owner, state, event, audit, and close guard. | orphan todos or notifications without business closure |
| OA-G2 State/button matrix | Primary buttons are derived from state, role, node, document level, delegation, timeout, and permission. | UI actions that backend cannot validate |
| OA-G3 Cross-module handoff | Workflow -> todo -> document -> archive and meeting -> resolution -> supervision paths include source event, target state, duplicate rule, and failure path. | cross-module gaps during integration |
| OA-G4 Permission and export | Org, role, field, document level, export, API, mobile, and AI context scopes are explicit. | data leakage and AI overreach |
| OA-G5 AI assistant boundary | Every AI feature states source citation, confidence/quality boundary, human gate, forbidden write, fallback, and eval cases. | AI output becoming unaccountable action |
| OA-G6 Document/e-sign integrity | Issued, archived, sealed, or signed documents have version, hash/signature, correction/withdrawal, and audit rule. | legally or operationally invalid documents |
| OA-G7 Mobile and weak network | PC/mobile state consistency, offline draft, duplicate prevention, and server validation are specified. | mobile approval divergence |

Post-generation OA checklist:

1. Master contract states module IDs, source-of-truth order, org/data scope,
   entity relations, event/notification catalog, field mapping, and audit rule.
2. Each module PRD has release functions, role paths, state/button matrix,
   business rules, exceptions, and test/acceptance rows.
3. Unified todo, workflow approval, official document, meeting/resolution,
   supervision, knowledge/AI, helpdesk, e-signature, and mobile approval are
   included or explicitly de-scoped.
4. Every high-impact action keeps human accountability and audit evidence.
5. Every alert/reminder/supervision item has source rule, owner, SLA, close
   guard, and target business action.
6. If prototype evidence exists, action/testid coverage gaps are listed before
   any `PASS` claim.

## Acceptance Checklist

- [ ] OA scope is classified: collaboration suite, classic OA, employee
      workspace, government/SOE office, service desk, low-code workflow, AI
      assistant, or mixed.
- [ ] WorkItem, WorkflowInstance, OfficialDocument, Meeting, SupervisionTask,
      KnowledgeAsset, HelpdeskTicket, ESignatureRecord, OrgUnit, and AI
      conversation boundaries are explicit where relevant.
- [ ] Workflow states, node actions, return/reject/terminate/timeout paths, and
      duplicate/stale-state guards are specified.
- [ ] Org, role, data, field, document-level, export, API, mobile, and AI
      permission scopes are explicit.
- [ ] Official document, seal/e-signature, archive, correction, and withdrawal
      rules are versioned and auditable.
- [ ] AI features have source citation, confidence/quality boundary, human
      gate, forbidden write scope, fallback, and linked tests.
- [ ] PC+mobile state consistency and weak-network behavior are defined when
      mobile is in scope.
- [ ] Common OA fields are maintained in a global field dictionary and FRRs do
      not duplicate unchanged field definitions.
- [ ] Stage 3.5 IA Skeleton is locked before full FRR generation when the scope
      spans multiple modules, roles, or surfaces.
- [ ] Coding-agent delivery package paths are explicit when implementation by
      Claude Code, Cursor, Codex, or Copilot is expected.
