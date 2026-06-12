# L2 Standard PRD Template

Use for development handoff, bid/demo package, ToB/ToG modules, SaaS features, report products, approval workflows, and multi-surface delivery.

This template keeps the familiar PRD structure but adds the missing engineering contracts: story path, state machine, prototype acceptance, DDD module handoff, testability, and readiness.

## Contents

- 1. Version Information
- 2. Change Log
- 3. Document Notes
- 4. Background And Opportunity
- 5. Goals, Metrics, And Scope
- 6. Users, Roles, And Permissions
- 7. Information Architecture
- 8. User Story And Role Path Matrix
- 9. Feature Details
- 10. Business Processes
- 11. State Machine And Button Matrix
- 12. Prototype And Interaction Contract
- 13. Development Contract
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
| Strategic Discovery Handoff | required only for new product/market, major investment, repositioning, or commercialization |

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

## 9. Feature Details

| Feature ID | Module | Feature | Input | Processing Logic | Output / Visible Result | Domain Result | Edge Cases |
|---|---|---|---|---|---|---|---|
| F-001 | | | | | | | |

Rules:

- describe what and why;
- include enough business logic for development and QA;
- avoid framework choices and database schema unless they are business contracts.

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

## 13. Development Contract

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
| Gate 3 Development Contract | PASS / FAIL | |
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
