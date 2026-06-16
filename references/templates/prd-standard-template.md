# L2 Standard PRD Template

Use for development handoff, bid/demo package, ToB/ToG modules, SaaS features, report products, approval workflows, and multi-surface delivery.

This is a deterministic traditional PRD template for development handoff. Its primary body is the familiar product requirement specification: background, goals/scope, users/permissions, architecture and flows, functional details, rules/data, non-functional requirements, acceptance/planning/risks. Engineering traceability and authoritative evidence are additional layers. DDD/API/Fast-Lane supplements the functional specification; it never replaces it.

The template is not complete merely because all chapter titles exist. Completeness is calculated from the release function inventory: every in-scope function must have one complete Functional Requirement Record (FRR).

## Contents

- 1. Version Information
- 2. Change Log
- 3. Document Notes
- 3.5 Reader Navigation
- 3.6 Source Evidence Register
- 4. Background And Opportunity
- 5. Goals, Metrics, And Scope
- 6. Users, Roles, And Permissions
- 7. Information Architecture
- 8. User Story And Role Path Matrix
- 9. Complete Module Product Specifications
- 10. Business Processes
- 11. State Machine And Button Matrix
- 12. Prototype And Interaction Contract
- 13. Engineering Traceability Contract
- 14. Data, Metrics, And Tracking
- 15. Non-Functional Requirements
- 16. Acceptance And Readiness
- 17. Risks, Decisions, And Open Questions
- 18. Appendix

## 1. Version Information

| Field | Value |
|---|---|
| Product / Module | |
| Version | v1.0 |
| Owner | |
| Created At | |
| Reviewers | Sponsor / PM / Dev Lead / QA / Ops |
| Delivery Tier | L2 Standard Product Delivery |
| Triggered Gates | Story-Path / Demo-Closed / Development Contract / Acceptance / optional gates |

## 2. Change Log

| Date | Version | Author | Change |
|---|---|---|---|
| | | | |

## 3. Document Notes

### Terms

| Term | Meaning |
|---|---|
| | |

### Related Artifacts

| Artifact | Link / Path |
|---|---|
| Prototype | |
| Flowchart | |
| Research / competitor notes | |
| Data report | |
| Metric / rule / field workbook | |
| SQL / dictionary / data contract | |
| Policy / standard | |
| Strategic Discovery Handoff | required only for new product/market, major investment, repositioning, or commercialization |

## 3.5 Reader Navigation

This table is navigation only. It must not create separate PRDs or redefine business facts.

| Reader | Required Route Through This PRD |
|---|---|
| Product / sponsor | goals -> scope -> role paths -> module specifications -> acceptance -> risks |
| Frontend | IA -> pages -> prototype contract -> state/button matrix -> function records -> acceptance |
| Backend | module specifications -> fields/rules -> commands/queries/events -> engineering traceability -> NFR |
| Algorithm / AI | AI boundary -> input/output schema -> prompt/model/eval/fallback -> function records |
| QA | role paths -> state/exception/permission matrix -> acceptance cases -> evidence |
| Architect / ops | system boundary -> data ownership -> dependencies -> readiness -> risk/rollback |

## 3.6 Source Evidence Register

Register every supplied source before writing feature details. Do not silently omit sheets, pages, rules, fields, metrics, screenshots, or prototype paths.

| Source ID | Artifact | Locator | Type | Atomic Count | Authority | Target Module | Disposition | Assertion Status | PRD / Annex / Test Trace | Conflict / Owner |
|---|---|---|---|---:|---|---|---|---|---|---|
| SRC-001 | | sheet/page/section/view/range | metric/rule/field/flow/schema/policy | | authoritative/supporting/historical | | `EMBEDDED` / `AUTHORITATIVE_ANNEX` / `DEFERRED` / `CONFLICT` / `NOT_APPLICABLE` | `VERIFIED` / `INFERRED` / `PROPOSED` / `UNKNOWN` / `CONFLICT` | | |

Assertion status rules:

- `VERIFIED`: directly proven by source, rendered prototype, database/schema, policy, or owner decision record.
- `INFERRED`: strongly implied but not directly stated; requires evidence and reviewer owner.
- `PROPOSED`: recommended by PM/AI/domain pattern; cannot be treated as accepted until owner confirms.
- `UNKNOWN`: missing evidence; blocks PASS when core behavior is affected.
- `CONFLICT`: sources disagree; blocks PASS until resolved.

Coverage summary:

| Status | Count | Pass Rule |
|---|---:|---|
| Registered atomic items | | equals the source inventory count |
| Embedded | | complete and traceable |
| Authoritative annex | | versioned, owned, and included in delivery package |
| Deferred | | reason, owner, release, and impact stated |
| Conflict | | decision owner and deadline stated |
| Silent omission | 0 | mandatory |

## 4. Background And Opportunity

### Strategic Discovery Handoff (Conditional)

Complete only when `strategy-discovery-handoff.md` is triggered.

| Field | Value |
|---|---|
| Decision | GO / GO_WITH_ASSUMPTIONS / VALIDATE_FIRST / NO_GO |
| Target Segment | |
| Market Size Required | Yes / No; link to TAM/SAM/SOM evidence if applicable |
| Competitive Alternatives | link / summary |
| Differentiated Outcome | |
| Riskiest Assumptions | |
| Validation Milestones | |

Do not add TAM/SAM/SOM or positioning sections to ordinary feature PRDs when the strategic gate is not triggered.

### Product / Data Current State

Current workflow:

Current data and system constraints:

### User Research / Evidence

| Source | Sample / Evidence | Key Finding |
|---|---|---|
| | | |

### Business Problem

Problem:

Impact:

Why now:

## 5. Goals, Metrics, And Scope

### Goals

| Goal | Current | Target | Window |
|---|---|---|---|
| | | | |

### Scope

In scope:

- 

Out of scope:

- 
- 
- 
- 
- 

### Complexity Budget

| Item | Count | Budget | Pass / Fail | Notes |
|---|---:|---:|---|---|
| States | | | | |
| Actions | | | | |
| APIs / Commands | | | | |
| AI Agents | | | | |

## 6. Users, Roles, And Permissions

| Role | User Goal | Main Path | Exception Path | Permission Boundary |
|---|---|---|---|---|
| | | | | |

## 7. Information Architecture

| Module | Page / View | Purpose | Main Data | Role Visibility |
|---|---|---|---|---|
| | | | | |

## 8. User Story And Role Path Matrix

| Story ID | Role | User Story | Start | Steps | Expected Visible Result | Expected Domain Result | Test Case |
|---|---|---|---|---|---|---|---|
| US-001 | | As a ..., I want ..., so that ... | | | | | TC-001 |

## 9. Complete Module Product Specifications

The summary index is not the specification itself. Complete Section 9 before writing the engineering overlay in Section 13.

| Module ID | Module | Depth | Release Scope | Detailed Section / Annex | Source IDs | Owner |
|---|---|---|---|---|---|---|
| M01 | | `FULL_SPEC` / `OVERVIEW_ONLY` | in / deferred / external | | | |

Use `FULL_SPEC` for every module planned for implementation in this release. `OVERVIEW_ONLY` is allowed only for deferred, out-of-scope, or external modules and must state owner and revisit condition.

### Mxx-0 Function Inventory And Completeness Calculation

List the complete release function tree first. This table is the denominator of Gate 3A.

| Function ID | Function Name | User Outcome | Trigger / Entry | Surface / Page | Release Scope | FRR Ref | Source IDs | Test IDs |
|---|---|---|---|---|---|---|---|---|
| Mxx-F01 | | | | | in / deferred / external | Mxx-F01 | | |

Completeness calculation:

| Check | Count / Result | Pass Rule |
|---|---:|---|
| Release functions | | all functions with `Release Scope = in` |
| Complete FRRs | | equals release functions |
| Functions with complete field/annex coverage | | equals release functions requiring data |
| Functions with actions and numbered flows | | equals release functions |
| Functions with exception/recovery cases | | equals release functions |
| Functions with acceptance cases | | equals release functions |
| Silent omissions / summary-only functions | 0 | mandatory |

Do not combine independent functions under “management”, “supports X/Y/Z”, “related operations”, or “complete lifecycle”. Create separate Function IDs when the role, trigger, state change, business result, permission, aggregate/data owner, audit/NFR, or acceptance path differs. Navigation, open/close, filtering, pagination and confirmation helpers may map to an owning function only when they have no independent domain result; the action-to-function mapping must still be explicit.

### Mxx-Fnn Functional Requirement Record

Repeat this complete record for every in-scope function in the inventory.

#### 1. Identity, Purpose, And Boundary

| Field | Requirement |
|---|---|
| Function ID / Name | |
| Module / Priority / Release | |
| User and business value | |
| In scope | |
| Out of scope / deferred | |
| Authoritative source IDs | |

#### 2. Roles And Scenario

| Item | Requirement |
|---|---|
| Initiating role | |
| Collaborating / receiving role | |
| Trigger and start condition | |
| Successful exit and next action | |

#### 3. Entry And Preconditions

| Item | Requirement |
|---|---|
| Entry page / route / upstream action | |
| Role prerequisite | |
| Data and object-state prerequisite | |
| Time / organization / tenant prerequisite | |
| Feature flag / configuration / dependency prerequisite | |

#### 4. Pages, Regions, And Visible States

| Page / Region | Purpose | Entry | Main Content | Loading | Empty | Error / Disabled | Exit |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

#### 5. Fields, Dictionaries, And Validation

List every user-entered, displayed, exported, matched, calculated, signed, uploaded, filtered, or state-driving field. A complete authoritative annex may replace the rows only when its source ID, version, owner, range, count, and usage rule are declared here.

| Field ID | Page / Object | Label / Meaning | Input / Display / Derived | Type / Format | Required / Default | Dictionary / Value Range | Validation And Error Copy | Source / Calculation | Editable By / State | Masking / Export |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |

#### 6. Numbered Interaction Flow

Write one observable user-system exchange per step. Do not use a one-line summary such as “supports add, edit, delete, export”.

| Step | Actor | Preconditions | User Action / System Trigger | System Validation And Processing | Visible Result | Domain Result | Next Action |
|---:|---|---|---|---|---|---|---|
| 1 | | | | | | | |

#### 7. Actions And Operation Rules

| Action ID | Page / State | Role | Trigger | Confirmation / Guard | Visible Result | Domain Result | Idempotency / Duplicate Rule | Next Action |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

#### 8. Business Rules, Calculations, And Calibers

| Rule ID | Applies To | Deterministic Rule / Formula / Threshold | Priority | Time / Effective Version | Evidence Source | Conflict / Exception Behavior |
|---|---|---|---|---|---|---|
| | | | | | | |

#### 9. State, Button, And Lifecycle Behavior

| Object | State | Visible Actions | Forbidden Actions | Guard | Trigger -> Next State | Visible Result | Event / Audit |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

#### 10. Permissions And Data Scope

| Role | Tenant / Org / Region / Enterprise Scope | Row Scope | Field Scope | Action Scope | Override / Approval | Unauthorized Behavior |
|---|---|---|---|---|---|---|
| | | | | | | |

#### 11. Exceptions, Fallback, And Recovery

| Exception ID | Case | Detection | User Feedback | Data Preservation | Allowed Recovery / Retry | Domain / Audit Result | Owner |
|---|---|---|---|---|---|---|---|
| | validation / empty / duplicate / stale / conflict / permission / timeout / dependency / partial failure | | | | | | |

#### 12. Notifications, Audit, And Dependencies

| Type | Trigger | Recipient / Dependency | Channel / Interface | Contents / Contract | Failure Behavior | Audit / Owner |
|---|---|---|---|---|---|---|
| notification / audit / upstream / downstream | | | | | | |

#### 13. Data, AI, And Algorithm Contract

Complete when the function includes recognition, recommendation, generation, scoring, semantic retrieval, configurable rules, statistical transformation, or other algorithmic processing. Otherwise write `N/A - deterministic CRUD/query with no algorithmic decision`.

| Item | Requirement |
|---|---|
| Input schema and source | |
| Output schema and downstream consumer | |
| Deterministic code/rule responsibility | |
| Model/prompt/retrieval responsibility | |
| Confidence, threshold, and human confirmation | |
| Model/prompt/rule/schema version | |
| Timeout, failure, fallback, and prohibited writes | |
| Golden/evaluation cases and pass threshold | |

#### 14. Function-Level NFR

| Category | Requirement | Measurement / Acceptance |
|---|---|---|
| performance / security / privacy / accessibility / compatibility / operations | | |

#### 15. Acceptance And Traceability

At minimum include happy, validation, permission, state-conflict, dependency-failure, and regression cases when applicable.

| Acceptance ID | Case | Preconditions / Data | Steps | Expected UI Result | Expected Domain Result | Prototype / Test | Source IDs |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

FRR completion rules:

- Every numbered section 1-15 must contain concrete content or `N/A + reason`.
- “见原型”, “见附件”, “按现有逻辑”, “同上”, “支持相关操作”, and a screenshot without behavior mapping are incomplete.
- Enum/dictionary values must be fully listed or mapped to a frozen authoritative annex range.
- A source annex may carry atomic fields/rules/metrics, but interaction flow, permissions, exception behavior, and acceptance stay in the FRR.
- `FULL_SPEC` is allowed only after the completeness calculation passes.

### Mxx Shared Module Contracts

Use the following A-L structure only for contracts genuinely shared by several FRRs. Do not use it to replace FRRs.

### Mxx Module Name

#### A. Purpose And Boundary

- User/business outcome:
- In scope:
- Explicitly deferred / external:
- Entry and exit conditions:
- Authoritative source IDs:

#### B. Roles, Scenarios, And Paths

| Scenario ID | Role | Start | Steps | Exit / Next Action | Visible Result | Domain Result |
|---|---|---|---|---|---|---|
| | | | | | | |

#### C. Pages And Views

| Page / View | Entry | Purpose | Main Regions | Empty / Loading / Error | Exit |
|---|---|---|---|---|---|
| | | | | | |

#### D. Fields And Dictionaries

| Field ID | Page / Object | Label / Meaning | Type | Required / Default | Source | Validation / Dictionary | Editable By | Display / Masking |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

If a source workbook/SQL dictionary contains a large complete field set, keep it as a versioned authoritative annex and map its item count and range here. Do not replace it with examples.

#### E. Actions And Interactions

| Action ID | Page / State | Role | Trigger | Preconditions / Confirmation | Visible Result | Domain Result | Next Action |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

#### F. Business Rules, Calculations, And Calibers

| Rule ID | Applies To | Rule / Formula / Caliber | Priority | Effective Range | Evidence Source | Conflict / Exception |
|---|---|---|---|---|---|---|
| | | | | | | |

#### G. State-Button Matrix

| Object | State | Visible Actions | Forbidden Actions | Guard | Transition / Event / Audit |
|---|---|---|---|---|---|
| | | | | | |

#### H. Permissions And Data Scope

| Role | Org / Tenant / Region Scope | Row Scope | Field Scope | Action Scope | Override / Approval |
|---|---|---|---|---|---|
| | | | | | |

#### I. Exceptions And Fallback

| Case | Detection | User Feedback | Allowed Recovery | Domain / Audit Result | Owner |
|---|---|---|---|---|---|
| validation / duplicate / conflict / stale / permission / timeout / partial failure | | | | | |

#### J. Cross-Module And External Contracts

| Dependency | Direction | Source Of Truth | Sync / Trigger | Failure Behavior | Owner |
|---|---|---|---|---|---|
| | | | | | |

#### K. Data, Metrics, AI, Audit, And NFR

Include only applicable contracts, but make each one specific and testable.

#### L. Acceptance And Traceability

| Acceptance ID | Story / Rule | Preconditions | Steps | Expected UI Result | Expected Domain Result | Prototype / Test | Source IDs |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

Product-spec rules:

- describe what, why, and complete observable business behavior;
- include enough fields, rules, states, interactions, exceptions, permissions, and acceptance for development and QA to proceed without guessing;
- avoid framework choices and physical database design unless they are explicit business contracts;
- when detail exceeds the master document budget, split by bounded module or authoritative annex. Never summarize away atomic requirements.

## 10. Business Processes

```text
trigger -> validation -> processing -> state change -> notification/report/audit -> next action
```

| Process | Trigger | Guard | Action | Result | Audit / Event |
|---|---|---|---|---|---|
| | | | | | |

## 11. State Machine And Button Matrix

| Object | State | Visible Actions | Forbidden Actions | Guard | Result Event |
|---|---|---|---|---|---|
| | | | | | |

State transition:

```yaml
transition:
  from:
  to:
  trigger:
  guard:
  action:
  event:
```

## 12. Prototype And Interaction Contract

Prototype path:

| Screen | data-testid | data-action | data-state / data-api | Expected Result |
|---|---|---|---|---|
| | | | | |

Demo paths:

| Path | Role | Steps | Pass Rule |
|---|---|---|---|
| Happy path | | | |
| Permission path | | | |
| Error / empty path | | | |

## 13. Engineering Traceability Contract

Complete this after Section 9. It maps product behavior into implementation entry points; it is not a substitute for the module specification.

| Module | Inputs | Outputs | Processing | Domain Object | Commands / Queries | Test Cases |
|---|---|---|---|---|---|---|
| | | | | | | |

Invariants:

- 

Domain events:

- 

Backend closure checklist for each write command:

| Function ID | Aggregate / Owner | Command Input / Output | Expected Version / Concurrency | Idempotency Key | Transaction / Saga Boundary | Persisted Result | Domain Event | Audit Fields | Retry / Reconciliation |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## 14. Data, Metrics, And Tracking

### Business Data

| Field / Object | Meaning | Source | Owner | Validation |
|---|---|---|---|---|
| | | | | |

### Metrics / Reports

| Metric | Formula / Caliber | Dimension | Refresh | Usage |
|---|---|---|---|---|
| | | | | |

### Event Tracking

| Event | Trigger | Params | Purpose |
|---|---|---|---|
| | | | |

## 15. Non-Functional Requirements

| Category | Requirement | Acceptance |
|---|---|---|
| Performance | | |
| Security / Privacy | | |
| Audit | | |
| Compatibility | | |
| Accessibility | | |
| Operations | | |

## 16. Acceptance And Readiness

| Gate | Result | Evidence |
|---|---|---|
| Gate 1 Story-Path | PASS / FAIL | |
| Gate 2 Demo-Closed Prototype | PASS / FAIL | |
| Gate 3A Product Specification Completeness | PASS / FAIL | source coverage + full module specs |
| Gate 3B Engineering Traceability Contract | PASS / FAIL | DDD/Fast-Lane/API/test trace |
| Gate 4 Acceptance Package | PASS / FAIL | |
| System Readiness | PASS / FAIL / N/A | |

## 17. Risks, Decisions, And Open Questions

| Type | Item | Owner | Deadline | Decision / Mitigation |
|---|---|---|---|---|
| Risk | | | | |
| Decision | | | | |
| Question | | | | |

## 18. Appendix

- Research report:
- Competitor analysis:
- Data analysis:
- Design files:
- Test report:
