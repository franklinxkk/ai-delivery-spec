# L2 Standard PRD Template

Use for development handoff, bid/demo package, ToB/ToG modules, SaaS features, report products, approval workflows, and multi-surface delivery.

This template keeps the familiar PRD structure and requires three coordinated layers: complete product specification, engineering traceability contract, and authoritative evidence coverage. The DDD/Fast-Lane layer supplements the product specification; it never replaces it.

## Contents

- 1. Version Information
- 2. Change Log
- 3. Document Notes
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

### Source Evidence Register

Register every supplied source before writing feature details. Do not silently omit sheets, pages, rules, fields, metrics, screenshots, or prototype paths.

| Source ID | Artifact | Locator | Type | Atomic Count | Authority | Target Module | Disposition | PRD / Annex / Test Trace | Conflict / Owner |
|---|---|---|---|---:|---|---|---|---|---|
| SRC-001 | | sheet/page/section/view/range | metric/rule/field/flow/schema/policy | | authoritative/supporting/historical | | `EMBEDDED` / `AUTHORITATIVE_ANNEX` / `DEFERRED` / `CONFLICT` / `NOT_APPLICABLE` | | |

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

The summary index is not the specification itself.

| Module ID | Module | Depth | Release Scope | Detailed Section / Annex | Source IDs | Owner |
|---|---|---|---|---|---|---|
| M01 | | `FULL_SPEC` / `OVERVIEW_ONLY` | in / deferred / external | | | |

Use `FULL_SPEC` for every module planned for implementation in this release. `OVERVIEW_ONLY` is allowed only for deferred, out-of-scope, or external modules and must state owner and revisit condition.

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
