# L1 Light Product Contract Template

Use for internal alignment, simple CRUD/workflow, or feature explanation before full development handoff.

## Contents

- 1. Version
- 2. Background
- 3. Goal And Non-Goal
- 4. Users And Roles
- 5. Scope
- 6. User Stories
- 7. Core Flow
- 8. State And Actions
- 9. Prototype / Screen Notes
- 10. Risks And Open Questions
- 11. Acceptance

## 1. Version

| Field | Value |
|---|---|
| Feature / Module | |
| Version | v0.1 |
| Owner | |
| Date | |
| Reviewers | PM / Dev / QA / Sponsor |

## 2. Background

Current situation:

User / business problem:

Why now:

## 3. Goal And Non-Goal

Goal:

Success signal:

Out of scope:

- 
- 
- 

## 4. Users And Roles

| Role | Scenario | Pain / Need | Permission Boundary |
|---|---|---|---|
| | | | |

## 5. Scope

In scope:

- 

Not included in this version:

- 

## 6. User Stories

| Story ID | Role | User Story | Acceptance Criteria | Test Case |
|---|---|---|---|---|
| US-001 | | As a ..., I want ..., so that ... | Given / When / Then + visible result + domain result | TC-001 |

## 7. Core Flow

```text
entry -> action -> visible result -> domain result -> next action
```

Fill-in sentence:

```text
The user enters from [入口/Entry], triggers [动作/Action], the system returns
[可见结果/Visible Result], and writes or updates [领域对象/Domain Object].
```

Example:

| Step | Flow Sentence | Notes |
|---|---|---|
| 1 | The regulator enters from the hidden-danger list, clicks `Issue Notice`, the system shows a confirmation modal, and creates a `HiddenDangerNotice` in `issued` state. | Every step must include both visible result and domain result. |

## 8. State And Actions

| Object | State | Visible Actions | Forbidden Actions | Domain Result |
|---|---|---|---|---|
| | | | | |

## 9. Prototype / Screen Notes

Prototype path:

Primary actions:

| Screen | data-testid | data-action | Expected Result |
|---|---|---|---|
| | | | |

## 10. Risks And Open Questions

| Item | Type | Owner | Decision Needed |
|---|---|---|---|
| | risk / question | | |

## 11. Acceptance

- [ ] Role path can be walked through.
- [ ] Every primary action has visible result.
- [ ] Every state-changing action has domain result.
- [ ] Known gaps are listed.
- [ ] If moving to development, upgrade to v5 Product Truth and the required projections.
