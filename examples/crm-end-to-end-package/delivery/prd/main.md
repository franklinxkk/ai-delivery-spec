# CRM Lead Response End-To-End PRD

PRD Profile: Human-First Full PRD
Lifecycle Stage: Discover -> Specify -> Plan -> Tasks -> Build/Verify
Mode: Standard
Tier: L2
Completion state: PASS

## Source Evidence Register

| Source ID | Path | Type | Source Status | Assertion Status | Scope |
|---|---|---|---|---|---|
| SRC-CRM-001 | delivery/stage0-output.json | stage0 | EMBEDDED | VERIFIED | Lead intake and response task scope |
| SRC-CRM-002 | delivery/prototype/app.html | prototype | AUTHORITATIVE_ANNEX | VERIFIED | IA Skeleton `M01-V01`, `data-testid="page-M01-V01"`, and primary actions |

## Release Function Inventory

| Function ID | Function Name | User Outcome | Release Scope | Source IDs | Test IDs |
|---|---|---|---|---|---|
| M01-F01 | Create lead and response task | New customer signal has an owner and response task | in | SRC-CRM-001, SRC-CRM-002 | AC-CRM-F01-001 |
| M01-F02 | Convert qualified lead to opportunity | Qualified lead enters pipeline with traceability | in | SRC-CRM-001, SRC-CRM-002 | AC-CRM-F02-001 |

## PRD Completion Ledger

| Function ID | Planned | Completed | Status | Missing Sections | Blocking Gaps |
|---|---:|---:|---|---|---|
| M01-F01 | 16 | 16 | complete | none | none |
| M01-F02 | 16 | 16 | complete | none | none |

## Stage 2 IA And Prototype Lock

The IA Skeleton `M01-V01` is locked for this example. The prototype root is
`data-testid="page-M01-V01"` with state `ready` and role visibility for
`cs_agent` and `sales_manager`.

| Region | Prototype Anchor | Purpose |
|---|---|---|
| lead-intake | `data-testid="region-lead-intake"` | capture Lead fields and run `data-action="create-lead"` |
| response-task | `data-testid="region-response-task"` | show assigned response context and run `data-action="convert-opportunity"` |

ACTION_API_CONTRACT:

| data-action | Method | API | FRR |
|---|---|---|---|
| create-lead | POST | /api/crm/leads | M01-F01 |
| convert-opportunity | POST | /api/crm/opportunities | M01-F02 |

## Stage 3 Complete Functional Requirement Records

### M01-F01 Create Lead And Response Task

#### 1 Identity And Value
M01-F01 creates a Lead from a customer signal and immediately creates a ResponseTask so the signal is not lost. The business result is assigned ownership, state `assigned`, and an audit record.

#### 2 Roles And Scenario
The initiating role is `cs_agent`; `sales_manager` can review the created Lead. The scenario starts from a phone or website signal and ends when the Lead and ResponseTask are visible in the response workspace.

#### 3 Entry And Preconditions
The entry is IA Skeleton `M01-V01` at `/crm/response-center`. The user must have lead-create permission, and required fields `Lead.customerName` and `Lead.source` must be present before persistence.

#### 4 Pages And Visible States
The page anchor is `data-testid="page-M01-V01"`. The lead intake region is `data-testid="region-lead-intake"` and uses state `draft` before submit; the root page remains `ready` for authorized users.

#### 5 Fields And Dictionaries
`Lead.customerName` is captured by `data-testid="field-lead-customer-name"` and must be non-empty. `Lead.source` is captured by `data-testid="field-lead-source"` and accepts phone or website in this minimal example.

#### 6 Numbered Interaction Flow
1. `cs_agent` opens IA Skeleton `M01-V01` and sees `data-testid="region-lead-intake"`.
2. The user enters `Lead.customerName` and selects `Lead.source`.
3. The user clicks `data-testid="btn-create-lead"` with `data-action="create-lead"`.
4. The backend validates required fields, writes Lead, creates ResponseTask, and returns the assigned state.
5. The response workspace shows the assigned task in `data-testid="region-response-task"`.

#### 7 Actions And Operation Rules
`data-action="create-lead"` calls POST `/api/crm/leads`. The command is idempotent by client request ID, requires lead-create permission, and writes Lead, ResponseTask, and AuditLog in one transaction.

#### 8 Business Rules And Calibers
BR-M01-F01-01: a Lead cannot be persisted without `Lead.customerName`. BR-M01-F01-02: `Lead.source` is copied to the Lead and AuditLog so response quality can be traced by source channel.

#### 9 State-Button Behavior
In state `draft`, `create-lead` is visible and enabled for `cs_agent`. After success, Lead becomes `assigned`; duplicate submit with the same idempotency key returns the original Lead result without creating a second ResponseTask.

#### 10 Permission And Data Scope
`cs_agent` can create leads from authorized channels and see self-created leads. `sales_manager` can see department leads and the response task state. Other roles are outside this example and must be blocked or hidden.

#### 11 Exceptions And Recovery
Missing `Lead.customerName` blocks persistence and keeps state `draft`. Duplicate contact detection returns a warning and requires a future merge decision, which is explicitly out of scope for this minimal package.

#### 12 Notifications, Audit, And Dependencies
The system writes `LeadCreated` and `LeadAssigned` audit entries with creator, role, source, assigned owner, time, and trace ID. Notification delivery is a dependency of the ResponseTask service.

#### 13 Data / AI / Algorithm Contract
No AI is used in this function. Deterministic backend contract: POST `/api/crm/leads` with `Lead.customerName`, `Lead.source`, idempotency key, and current user context; response returns Lead ID and assigned state.

#### 14 Function-Level NFR
The command must reject unauthorized users before validation details are exposed. Audit write is mandatory. The endpoint must be safe for retry with the same idempotency key.

#### 15 Frontend / Backend / QA Handoff Notes
Frontend binds `data-field="Lead.customerName"` and `data-field="Lead.source"` to the create form. Backend owns validation and transaction boundaries. QA covers happy path, missing field, duplicate retry, and permission denial.

#### 16 Acceptance
Given authorized `cs_agent` submits required fields through `data-action="create-lead"`, when POST `/api/crm/leads` succeeds, then Lead is `assigned`, ResponseTask exists, and audit entries are recorded.

```yaml
ac_structured:
  - id: AC-CRM-F01-001
    frr_ref: M01-F01
    data_testid: page-M01-V01
    data_action: create-lead
    data_field: Lead.customerName
    given: authorized cs_agent is on the CRM response workspace
    when: the user submits a valid lead
    then: Lead is created in assigned state and ResponseTask is created
    test_type: integration
  - id: AC-CRM-F01-002
    frr_ref: M01-F01
    data_testid: region-lead-intake
    data_action: create-lead
    data_field: Lead.source
    given: required lead source is present
    when: create-lead is submitted
    then: audit log records creator, source, and assigned owner
    test_type: integration
  - id: AC-CRM-F01-003
    frr_ref: M01-F01
    data_testid: field-lead-customer-name
    data_action: create-lead
    data_field: Lead.customerName
    given: customer name is empty
    when: create-lead is attempted
    then: validation blocks persistence and keeps draft state
    test_type: negative
  - id: AC-CRM-F01-004
    frr_ref: M01-F01
    data_testid: field-lead-source
    data_action: create-lead
    data_field: Lead.source
    given: lead source is selected
    when: create-lead succeeds
    then: source is stored on Lead and visible to sales_manager
    test_type: integration
  - id: AC-CRM-F01-005
    frr_ref: M01-F01
    data_testid: btn-create-lead
    data_action: create-lead
    given: user has lead create permission
    when: the button is clicked
    then: POST /api/crm/leads is called with idempotency guard
    test_type: integration
```

### M01-F02 Convert Qualified Lead To Opportunity

#### 1 Identity And Value
M01-F02 converts an assigned Lead into an Opportunity after qualification. The business result is Lead state `converted`, Opportunity creation, and preserved source traceability.

#### 2 Roles And Scenario
The initiating role is `sales_manager` in this bounded example. The scenario starts with an assigned Lead in `data-testid="region-response-task"` and ends when the Opportunity is created.

#### 3 Entry And Preconditions
The entry is IA Skeleton `M01-V01`. Preconditions are Lead state `assigned`, an existing ResponseTask, conversion permission, and enough customer context to create the Opportunity.

#### 4 Pages And Visible States
The response region is `data-testid="region-response-task"` and starts in state `assigned`. The conversion command is exposed by `data-testid="btn-convert-opportunity"`.

#### 5 Fields And Dictionaries
The conversion reuses Lead fields `Lead.customerName` and `Lead.source` as source trace fields on Opportunity. Opportunity amount, expected close date, and pipeline stage are deferred from this minimal package.

#### 6 Numbered Interaction Flow
1. `sales_manager` reviews the assigned response task in `data-testid="region-response-task"`.
2. The user confirms the Lead is qualified.
3. The user clicks `data-testid="btn-convert-opportunity"` with `data-action="convert-opportunity"`.
4. The backend calls POST `/api/crm/opportunities`, creates Opportunity, and marks Lead as `converted`.
5. The system records `LeadConverted` and links the Opportunity to the original Lead.

#### 7 Actions And Operation Rules
`data-action="convert-opportunity"` calls POST `/api/crm/opportunities`. The command is allowed only once per Lead; repeat conversion returns the existing Opportunity link.

#### 8 Business Rules And Calibers
BR-M01-F02-01: only Lead state `assigned` can convert. BR-M01-F02-02: Opportunity must retain `leadId` and source channel for lead-to-cash traceability.

#### 9 State-Button Behavior
In state `assigned`, `convert-opportunity` is visible for `sales_manager`. After success, Lead becomes `converted`; the convert button is hidden or disabled and the Opportunity link is shown.

#### 10 Permission And Data Scope
`sales_manager` can convert leads in department scope. `cs_agent` can view the conversion result for self-created leads but cannot execute the conversion in this example.

#### 11 Exceptions And Recovery
If the Lead is already `converted`, the command returns the existing Opportunity reference. If Opportunity creation fails after Lead validation, no Lead state change is committed and the user can retry.

#### 12 Notifications, Audit, And Dependencies
The system records `LeadConverted` with lead ID, opportunity ID, actor, role, and trace ID. Opportunity creation depends on the CRM opportunity service and must not silently drop the lead trace.

#### 13 Data / AI / Algorithm Contract
No AI is used in this function. Deterministic backend contract: POST `/api/crm/opportunities` with Lead ID, user context, expected version, and idempotency key; response returns Opportunity ID.

#### 14 Function-Level NFR
The command must enforce state guard and permission before creating Opportunity. Traceability is mandatory: Opportunity must keep `leadId` and audit record.

#### 15 Frontend / Backend / QA Handoff Notes
Frontend keeps the convert button stable as `data-testid="btn-convert-opportunity"`. Backend owns state guard, idempotency, and transaction. QA covers happy path, permission denial, already converted, and dependency failure.

#### 16 Acceptance
Given an assigned Lead and authorized `sales_manager`, when `data-action="convert-opportunity"` calls POST `/api/crm/opportunities`, then Opportunity is created, Lead becomes `converted`, and `LeadConverted` audit evidence exists.

```yaml
ac_structured:
  - id: AC-CRM-F02-001
    frr_ref: M01-F02
    data_testid: region-response-task
    data_action: convert-opportunity
    given: Lead is assigned and response task exists
    when: sales_manager converts the qualified lead
    then: Opportunity is created and Lead state becomes converted
    test_type: integration
  - id: AC-CRM-F02-002
    frr_ref: M01-F02
    data_testid: btn-convert-opportunity
    data_action: convert-opportunity
    given: user has conversion permission
    when: convert-opportunity is clicked
    then: POST /api/crm/opportunities is called and LeadConverted event is recorded
    test_type: integration
```

## Stage 4 Review And Delivery Plan

Implementation can proceed as two vertical slices: M01-F01 first because it
creates the Lead and ResponseTask source truth, then M01-F02 because it depends
on assigned Lead state and preserves lead-to-opportunity traceability.

## Stage 5 Test And Acceptance

Run the package validators listed in `delivery/evidence/validation-log.txt`.
Acceptance is complete only when PRD quality, IA Skeleton cross-check, and
coding-agent PRD/prototype contract validation pass.
