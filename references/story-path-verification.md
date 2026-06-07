# User Story and Role Path Verification

Use this reference before PRD/prototype generation and during review. The goal is to prove that every described function is complete enough to build, test, and demo.

## Core Rule

Feature names are not requirements. A requirement is complete only when it has:

`feature -> user story -> role path -> prototype actions -> state transition -> command/query/API -> test case`

## User Story Inventory Template

| Story ID | Role | Goal | Trigger | Preconditions | Operation Path | Expected UI Result | Expected Domain Result | Exception Path | State Transition | Test ID |
|---|---|---|---|---|---|---|---|---|---|---|
| US-001 | regulator | Create a report task from blank template | Needs a new statistics task | Indicator library exists | report list -> create -> blank -> builder -> publish | New task row appears | ReportTask created; FillRecord generated | Missing template name | Draft -> Filling | TC-001 |

Rules:
- Every scoped feature needs at least one story.
- Every role needs at least one happy path and one exception/permission path.
- Every story needs a visible UI result and a domain result.
- Stories without state transitions are allowed only for read-only queries; mark them as Query.

## Role Operation Path Matrix

| Role | Path ID | Start | Steps | Data Touched | Before State | After State | Permission Rule | Audit/Event | Next Action |
|---|---|---|---|---|---|---|---|---|---|
| enterprise | RP-ENT-001 | My Fill Tasks | open task -> edit ext fields -> submit | FillRecord.editableData | 待填写 | 已提交 | own enterprise only | FillSubmitted | View submit history |

Rules:
- Paths must use prototype-visible labels or `data-testid`.
- If the role is mentioned in PRD, it must have paths.
- A role path that cannot be executed in the prototype is a product gap.

## Coverage Matrix

| Feature | Story ID | Role Path | Prototype `data-action` | `data-testid` | State Transition | Command/Query/API | Test Case | Status |
|---|---|---|---|---|---|---|---|---|
| Create task | US-001 | RP-REG-001 | open-create-modal, open-blank-builder, builder-publish | btn-create-report-task, template-builder | 草稿 -> 填报中 | PublishTemplateCommand | TC-001 | PASS |

Statuses:
- PASS: PRD, prototype, state, and test all align.
- FAIL: Path exists but cannot be executed or expected result missing.
- BLOCKED: Missing domain data, policy, or external dependency.
- DESCOPED: Explicitly removed with owner/reason.

## Domain Scenario Validation

For domain-heavy products, validate requirements against real scenarios:

| Scenario | Stress Point |
|---|---|
| Routine reporting | Repeatable period task, historical reuse, no duplicate collection |
| Emergency reporting | Fast creation, partial submission, urgent reminders |
| Regulatory inspection | Evidence, attachments, audit logs, snapshot |
| Enterprise self-report | Data isolation, minimal fields, mobile/share entry |
| AI template parsing | Ambiguous headers, low confidence, manual confirmation |
| Metric governance | changing definitions, version locking, retrospective traceability |
| Analysis/reporting | indicator evidence chain, narrative report, review before publish |

## Review Protocol

1. Extract all features from the PRD and prototype navigation/actions.
2. Build or verify user story inventory.
3. Build or verify role operation path matrix.
4. Trace each story to prototype actions and expected state changes.
5. Trace each story to DDD command/query/API and test case.
6. Run browser or DOM verification for high-risk demo paths.
7. Mark each row PASS/FAIL/BLOCKED/DESCOPED.
8. Fix FAIL rows before delivery.

## Automatic Failure Conditions

- Any scoped feature has no story.
- Any story has no role path.
- Any role path has no prototype action.
- Any primary prototype action is toast-only.
- Any state-changing story lacks a state transition.
- Any state-changing story lacks a test case.
- Any role lacks a permission/isolation test.
