# L1 PRD Sample: Course Selection Conflict Check

## 0. Delivery Metadata

```yaml
artifact: light_prd_sample
domain: Higher-Education IT
mode: Lite
tier: L1
ai: false
workflow: true
completion_state: REVIEW_COMPLETE_WITH_GAPS
```

## 1. Problem And Outcome

Students often select courses with time, credit, prerequisite, or capacity
conflicts. Academic affairs staff need a deterministic check before the final
selection result is confirmed.

Success metric:

```text
Invalid course-selection submissions: unknown baseline -> reduce by 80% in one term pilot.
```

## 2. Users And Core Scenario

| Role | Goal | Pain |
|---|---|---|
| Student | select valid courses quickly | conflict reason is unclear |
| Academic affairs staff | reduce manual correction | late conflict handling creates workload |
| Teacher | see final class roster | roster changes after confirmation |

Core flow:

```text
Student opens selection -> system checks eligibility/conflict -> student submits -> selection becomes pending/confirmed.
```

## 3. Function Inventory

| Function ID | Function Name | User Outcome | Release Scope |
|---|---|---|---|
| EDU-F01 | Check course selection conflict | student sees exact blocking reason | in |
| EDU-F02 | Submit course selection | valid selection enters pending/confirmed state | in |

## 4. Functional Requirement Record: EDU-F01 Check Course Selection Conflict

| Section | Content |
|---|---|
| Identity and value | EDU-F01; prevent invalid course selection before submission |
| Roles and scenario | student selects one course and system checks conflicts |
| Entry and preconditions | student is active; term selection window is open; course is published |
| Pages and visible states | course list, conflict warning, selectable/disabled status |
| Fields and dictionaries | course code, course name, credit, time slot, capacity, prerequisite, selection state |
| Numbered interaction flow | 1 student views course; 2 clicks select; 3 system checks conflicts; 4 result shown |
| Actions and results | select action either adds draft selection or shows blocking reason |
| Business rules and calibers | time conflict, capacity full, prerequisite missing, max credits exceeded |
| State-button behavior | selectable shows Select; blocked shows reason; selected shows Remove |
| Permission and data scope | student sees own status and public course data only |
| Exceptions and recovery | stale capacity requires refresh; window closed blocks submit |
| Notifications, audit, and dependencies | audit stores conflict rule result for dispute handling |
| Data / AI / algorithm contract | N/A: deterministic rule engine |
| Function-Level NFR | conflict check <= 1s for normal selection load |
| Frontend / Backend / QA handoff notes | frontend must show one primary reason; backend returns rule code; QA tests every conflict type |
| Acceptance | Given a student selects a course with time conflict, when checking selection, then system blocks selection and shows conflict course/time |

```yaml
ac_structured:
  - id: AC-EDU-F01-001
    given: "student has already selected a course in the same time slot"
    when: "the student selects another course with overlapping time"
    then: "the system blocks the draft selection and shows the conflicting course and time slot"
    test_type: integration
```

## 5. Gaps Before L2

- Confirm whether waitlist is in scope.
- Confirm priority rules for major-required vs elective courses.
- Confirm grade/prerequisite source of truth.
