# Human-First Full PRD Template (v4.9.5 Profile)

Use this profile when the PRD will be reviewed, developed, tested, outsourced,
accepted, or archived by human teams. The document must be readable before it
is machine-readable. Engineering contracts support the product specification;
they do not replace it.

## Contents

- Heading Hierarchy Lock
- 0D Triage And Scope
- Stage 1 Requirement Planning
- Stage 2 IA And Prototype Lock
- Stage 3 Complete Functional Requirement Records
- Stage 4 Review And Delivery Plan
- Stage 5 Test And Acceptance
- Stage 6 Launch And Review
- Appendix
- Gate Completion Statement

## Heading Hierarchy Lock

- Use exactly one H1 (`#`) for the document title.
- Use H2 (`##`) for global lifecycle stages or top-level modules.
- Use H3 (`###`) for module subsections and function records.
- Use H4 (`####`) for FRR numbered sections inside one function.
- Do not jump from H2 directly to H4.
- Do not use bold text, table rows, or numbered list items as fake headings.
- In Chinese PRDs, translate headings but keep the hierarchy unchanged.

## 0D Triage And Scope

```text
[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false]
Mode: Lite | Standard | Full
PRD Profile: Human-First Full PRD
Lifecycle Stage: Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire
```

### Source Evidence Register

| Source ID | Artifact | Locator | Type | Authority | Target Module | Disposition | Assertion Status |
|---|---|---|---|---|---|---|---|
| SRC-001 | {file/path} | {page/sheet/view} | screenshot/prototype/prd/excel/sql/policy/interview | authoritative/supporting/historical | Mxx | EMBEDDED/ANNEX/DEFERRED/CONFLICT | VERIFIED/INFERRED/PROPOSED/UNKNOWN |

Rules:

- Every important claim must trace to a source, an inference, or an explicit
  open question.
- Do not write "see prototype" without `view_id`, `region_id`, `data-testid`,
  `data-action`, screenshot page, or module/function ID.

## Stage 1 Requirement Planning

### 1.1 Project Background And Business Goals

Write 1-2 short paragraphs explaining the business scene, pain, and expected
outcome. Avoid abstract phrases such as "improve efficiency" unless the
behavior and measurement are stated.

| Goal ID | Goal | Measurement | Priority |
|---|---|---|---|
| BO-01 | {business outcome} | {metric or review signal} | P0/P1/P2 |

### 1.2 Roles, Responsibilities, And Use Scenes

| Role ID | Role | Responsibility | System Goal | Typical Scenario | Pain Point |
|---|---|---|---|---|---|
| ROLE-001 | {name} | {responsibility} | {goal} | {when/where} | {pain} |

### 1.3 Core User Journey And Business Scenario

| Scenario ID | Role | When / Trigger | Goal | Main Action | Success Result | Exception To Watch |
|---|---|---|---|---|---|---|
| SC-M01-01 | {role} | {trigger} | {goal} | {action} | visible result + domain result | {exception} |

### 1.4 Competitor / Alternative Analysis, Value, And Priority

Use this section when the requirement is not fully shaped, when multiple
solutions compete, or when roadmap priority must be justified.

| Alternative | User Job Covered | Strength | Weakness / Gap | What To Learn | What Not To Copy |
|---|---|---|---|---|---|
| competitor / status quo / manual workaround | {job} | {strength} | {gap} | {learning} | {avoid} |

| Option | Target Role | User Value | Business Value | Feasibility | Risk | Evidence | Recommendation |
|---|---|---:|---:|---:|---|---|---|
| {option} | {role} | H/M/L | H/M/L | H/M/L | {risk} | {source} | do/defer/test/reject |

| Candidate | Method | Score / Level | Why Now | Dependency | Release Decision |
|---|---|---|---|---|---|
| {feature} | ICE/RICE/MoSCoW/owner decision | {score} | {reason} | {dependency} | in/out/later |

### 1.5 EARS Requirement Writing Rule

For P0/P1 behavior, include at least one EARS-style statement before detailed
tables.

| Pattern | Sentence Shape | Example Intent |
|---|---|---|
| Event-driven | When {event}, the system shall {response}. | trigger-based behavior |
| State-driven | While {state}, the system shall {response}. | state-dependent buttons/rules |
| Unwanted behavior | If {unwanted condition}, the system shall {mitigation}. | invalid input / overreach / abuse |
| Optional feature | Where {feature/config/permission}, the system shall {response}. | configuration or permission branch |
| Ubiquitous | The system shall {invariant}. | always-on rule |

### 1.6 Scope, Priority, And Out-Of-Scope

| Module ID | Module | In Scope | Out Of Scope | Priority | Release |
|---|---|---|---|---|---|
| M01 | {module} | {functions} | {exclusions} | P0/P1/P2 | v{version} |

## Stage 2 IA And Prototype Lock

### 2.1 IA Skeleton

| Module ID | View ID | View Name | Platform | Primary Roles | Regions | Primary Actions |
|---|---|---|---|---|---|---|
| M01 | M01-V01 | {view} | web/mobile/miniapp | {roles} | {region_ids} | {action_ids} |

### 2.2 Page Layout And Region Map

| Layout ID | View ID | Region ID | Region Name | Position | Main Components | Visible States | Notes |
|---|---|---|---|---|---|---|---|
| LAY-M01-V01-R01 | M01-V01 | region-filter | {name} | top/left/main/right/bottom/modal/drawer | {components} | empty/loading/error/success/disabled | {notes} |

Rules:

- `Layout ID` format: `LAY-{view_id}-{RNN|MNN|DNN|PNN}`.
- Keep `Layout ID`, `view_id`, `region_id`, and `data-testid` stable after
  assignment.
- If an IA Skeleton is locked, reference its `region_id` instead of rewriting
  the same region definitions in multiple places.

### 2.3 Prototype Lock Record

| Artifact | Path / URL | Lock Status | Evidence Scope | Owner |
|---|---|---|---|---|
| Prototype | {path} | locked / draft | views/actions/modals/states/mock data | {owner} |

## Stage 3 Complete Functional Requirement Records

Repeat one complete FRR for every in-scope function. A module is not complete
until all its functions have complete records.

### Mxx-Fxx {Function Name}

Every in-scope function must contain all 16 FRR sections. If a section does not
apply, write `N/A + reason`; do not leave it blank or write only "see prototype",
"same as above", or "existing logic".

#### §1 Business Scenario

Use `who / when / why / what / result` to describe the concrete scene. State
the visible user result and the domain/business result.

#### §2 Roles And Scenario

| Role | Responsibility In This Function | Start Condition | Success Exit | Next Action |
|---|---|---|---|---|
| {role} | {responsibility} | {trigger/state} | {visible + domain result} | {next step} |

#### §3 Entry And Preconditions

| Item | Requirement |
|---|---|
| Entry | {menu/button/link/API/notification} |
| Preconditions | {role/data/state/config/time/dependency} |
| Blocked Entry Handling | {disabled/hidden/error/redirect/audit} |
| Upstream Dependency | {source module/event/data} |

#### §4 Pages, Regions, And Visible States

Reference `Layout ID`, `view_id`, `region_id`, `data-testid`, table columns,
form fields, modal/drawer chain, responsive differences, and empty/loading/error
/success/disabled states. State how the page looks and behaves, not only which
data exists.

#### §5 Fields, Dictionaries, And Validation

When a locked prototype exists: list only prototype-invisible rules such as
permission differences, state-conditional editability, enum values not visible
in the prototype, masking, backend-only fields, and cross-field linkage.
Reference the global field dictionary for all other fields. Do not repeat every
visible field position that the locked prototype already shows.

| Field ID | Field Name | Type | Required | Dictionary / Enum | Validation | Default | Editable By |
|---|---|---|---|---|---|---|---|
| FLD-Mxx-Fxx-001 | {field} | string/date/number/enum/file | Y/N | {dict} | {rule} | {value} | {role} |

#### §6 Numbered Interaction Flow

| Step | Actor | Action / data-action | Frontend Feedback | Backend Rule | Domain Result | Failure Branch |
|---|---|---|---|---|---|---|
| 1 | {role} | {data-action} | toast/modal/loading/disabled | {validation/transaction} | {state/event/audit} | {error/retry} |

#### §7 Actions And Operation Rules

| Action | Allowed Role | Allowed State | Confirmation | Idempotency | Visible Result | Domain Result |
|---|---|---|---|---|---|---|
| {action} | {role} | {state} | none/modal/second-confirm | yes/no/key | {ui result} | {data/state/event} |

#### §8 Business Rules, Calculations, And Calibers

Describe source of truth, create/update/delete rules, synchronization,
calculation, threshold/caliber, conflict handling, audit logging, and
upstream/downstream impact. Number every rule as `BR-Mxx-Fxx-NN`.

#### §9 State, Button, And Lifecycle Behavior

| Current State | Visible Actions | Forbidden Actions | Guard | Next State | Event / Audit |
|---|---|---|---|---|---|
| {state} | {actions} | {actions} | {role/data/time/config} | {state} | {event/audit} |

#### §10 Permissions And Data Scope

| Role | Function Permission | Data Scope | Field / Action Restriction | Overreach Handling |
|---|---|---|---|---|
| {role} | view/create/update/delete/approve/export | self/department/specified/all/custom | {restriction} | block/mask/escalate/audit |

#### §11 Exceptions, Fallback, And Recovery

| Category | Required Behavior |
|---|---|
| Empty / loading / error | {visible feedback + retry/preserve rule} |
| Input boundary | {required/format/length/duplicate/cross-field} |
| Permission | {vertical/horizontal overreach behavior} |
| State conflict | {repeat submit/stale data/deleted/locked} |
| Network / dependency | {timeout/offline/partial success/retry} |

#### §12 Notifications, Audit, And Dependencies

| Trigger | Recipient / Dependency | Channel / Interface | Payload / Content | Failure Handling | Audit Owner |
|---|---|---|---|---|---|
| {trigger} | {role/system} | in-app/SMS/API/event/file | {payload} | retry/fallback/manual | {owner} |

#### §13 Data, AI, And Algorithm Contract

| Contract Type | Required Content |
|---|---|
| Data | source of truth, schema/dictionary, import/export, sync timing, consistency owner |
| AI / Algorithm | deterministic vs model responsibility, input/output schema, confidence, human gate, fallback, evaluation |
| Prohibited Write | fields/states/actions AI or automation must not modify |

#### §14 Function-Level NFR

| Category | Requirement | Measurement |
|---|---|---|
| Performance | {latency / batch size / concurrency} | {threshold or proposed} |
| Security / Privacy | {masking / audit / permission} | {check method} |
| Compatibility | {browser/device/surface} | {scope} |
| Operations | {monitoring/retry/rollback/support} | {evidence} |

#### §15 Frontend / Backend / QA Handoff Notes

| Reader | Must Know |
|---|---|
| Frontend | layout, component states, `data-testid`, `data-action`, client validation |
| Backend | permissions, state transition, transaction, idempotency, audit, dependency |
| Algorithm / AI | data source, schema, prompt/rule/model responsibility, eval/fallback |
| QA | happy path, boundary, permission, state conflict, weak network, regression |

#### §16 Acceptance And Traceability

| AC ID | Given | When | Then | Test Type | Priority | Source / Prototype |
|---|---|---|---|---|---|---|
| AC-Mxx-Fxx-001 | {precondition} | {action} | {observable result + domain result} | unit/integration/e2e/manual | P0/P1/P2 | SRC-... / data-action |

## Stage 4 Review And Delivery Plan

### 4.1 Sprint Task Breakdown / WBS

| Task ID | Slice | Source FRR | Owner Role | Dependency | Done Criteria |
|---|---|---|---|---|---|
| TASK-Mxx-001 | {vertical slice} | Mxx-Fxx | FE/BE/QA/AI | {dependency} | {test/evidence} |

### 4.2 Risk Register

| Risk ID | Risk | Impact | Probability | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|---|
| RISK-001 | {risk} | H/M/L | H/M/L | {mitigation} | {owner} | {trigger} |

### 4.3 Key Dependencies

| Dependency ID | Upstream / Owner | Needed By | Required Date | Fallback | Status |
|---|---|---|---|---|---|
| DEP-001 | {system/person} | {module/function} | {date} | {fallback} | open/confirmed/blocked |

### 4.4 Development Follow-Up, Risk, And Blockers

Use this when build/verify is in scope.

| TRK ID | Date | Module / FRR | Owner | Progress | Blocker / Risk | Decision Needed | Next Check |
|---|---|---|---|---|---|---|---|
| TRK-001 | {date} | Mxx-Fxx | {owner} | not-started/in-progress/done | {blocker} | {decision} | {date} |

### 4.5 Bug Management And Acceptance Defects

| BUG ID | Source AC | Severity | Steps To Reproduce | Expected | Actual | Owner | Status |
|---|---|---|---|---|---|---|---|
| BUG-001 | AC-Mxx-Fxx-001 | P0/P1/P2 | {steps} | {expected} | {actual} | {owner} | open/fixed/verified |

### 4.6 Open Questions

| Question ID | Module / FRR | Question | Owner | Blocks Delivery? | Due Date | Decision |
|---|---|---|---|---|---|---|
| Q-001 | Mxx-Fxx | {question} | {owner} | Y/N | {date} | open/decided |

## Stage 5 Test And Acceptance

| Test ID | Source AC | Test Type | Preconditions | Steps | Expected Result | Evidence |
|---|---|---|---|---|---|---|
| TC-001 | AC-Mxx-Fxx-001 | unit/integration/e2e/manual | {precondition} | {steps} | {result} | screenshot/log/report |

Acceptance package:

- source evidence register;
- IA Skeleton and prototype lock record;
- FRR coverage table;
- acceptance/test coverage table;
- unresolved risks and de-scoped items;
- sign-off owner and date.

## Stage 6 Launch And Review

### 6.1 Launch Checklist

| Area | Check | Owner | Evidence | Result |
|---|---|---|---|---|
| data | migration/import/reconciliation ready | {owner} | {evidence} | pass/fail |
| operation | on-call, rollback, support ready | {owner} | {evidence} | pass/fail |

### 6.2 Post-launch Review

| Metric / Signal | Baseline | Target | Actual | Decision | Follow-Up |
|---|---|---|---|---|---|
| {metric} | {baseline} | {target} | {actual} | continue/iterate/rollback/retire | {action} |

## Appendix

### Appendix A Glossary

| Term | Definition | Notes |
|---|---|---|
| {term} | {definition} | {notes} |

### Appendix B Role Permission Matrix

| Role | Menu | Action | Data Scope | Field Scope |
|---|---|---|---|---|
| {role} | {menu} | {action} | {scope} | {fields} |

### Appendix C API Endpoint Inventory

| Method | Path | Source FRR | Auth | Idempotency | Notes |
|---|---|---|---|---|---|
| GET | /api/{module}/{resource} | Mxx-Fxx | yes | yes | {notes} |

### Appendix D E2E Cross-Module Canvas

| Upstream State Change | Domain Event | Downstream State Change | Test Case |
|---|---|---|---|
| {source state} | {event} | {target state} | AC-E2E-001 |

### Appendix E Decision Records

| Decision ID | Date | Decision | Options Considered | Owner | Impact |
|---|---|---|---|---|---|
| ADR-001 | {date} | {decision} | {options} | {owner} | {impact} |

## Gate Completion Statement

```text
Completion State: PASS | REVIEW_COMPLETE_WITH_GAPS | BLOCKED
Profile: Human-First Full PRD
Scope:
Triggered Gates:
Verification:
Open Risks:
Next Step:
```
