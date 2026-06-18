# Delivery Core

Use this file for reverse engineering, PRD generation, state machines, guards, SIM review, and developer handoff.

## Contents

- Stage 0 Reverse Engineering
- Engineering Profile / Anti-Bloating
- Stage 1-5 Product Workflow
- Human-Readable PRD Layer
- Guard Protocol
- Complexity Budget Counting
- SIM Review
- Developer Prompt Skeleton
- Quality Gate Summary

## Stage 0 Reverse Engineering

Use Stage 0 when the input is an existing HTML prototype, legacy system, screenshot, Excel template, or competitor product.

### Annotation Pattern Detection

| Pattern | Signal | Strategy |
|---------|--------|----------|
| Semantic | `data-action`, `data-testid`, `data-state`, `data-api`, `gotoView` | Parse data-* and code together |
| Inline handler | many `onclick="..."`, few/no data-* | Extract onclick targets and function names |
| File route | multiple HTML files, no router | Treat file names as feature keys |
| External SPA | React/Vue bundles/minified JS | Visual walkthrough + DOM snapshot |

Fallback rule: if semantic pattern is absent, downgrade gracefully. Do not force data-* parsing onto incompatible prototypes.

### Stage 0 Steps

1. Scan external dependencies: scripts, stylesheets, adjacent data files.
2. Parse entities from JS constants, tables, forms, local state, schemas.
3. Parse views from nav items, routes, functions, containers, modals.
4. Parse features from buttons, onclick handlers, data-actions, submit flows.
5. Parse states from enum-like values, badge mappings, lifecycle functions.
6. Mark each output as CONFIRMED / INFERRED / UNKNOWN.
7. If iteration input exists, run regression detection and interaction parity detection.
8. Produce `stage0-output.json`.

### Source Evidence Inventory And Coverage

When the input includes Excel, Word/PDF, SQL, screenshots, rule catalogs, field dictionaries, metric caliber tables, prototypes, or legacy documents, Stage 0 must inventory the evidence before drafting the PRD.

Minimum register:

| Source ID | File / Artifact | Sheet / Page / Section / Path | Evidence Type | Atomic Item Count | Authority | Intended Module | Disposition | Assertion Status | PRD / Annex Reference | Conflict / Decision Owner |
|---|---|---|---|---:|---|---|---|---|---|---|
| SRC-001 | | | metric / rule / field / flow / screenshot / schema / policy | | authoritative / supporting / historical | | `EMBEDDED` / `AUTHORITATIVE_ANNEX` / `DEFERRED` / `CONFLICT` / `NOT_APPLICABLE` | `VERIFIED` / `INFERRED` / `PROPOSED` / `UNKNOWN` / `CONFLICT` | | |

Rules:

- Count the source at its atomic level: workbook sheets and rows, document sections/pages, prototype views/actions, SQL tables/columns/dictionaries, screenshots, policy clauses, and decision records.
- Preserve authoritative detail. A source containing 45 metrics, 45 judgment rules, or 95 configurable fields cannot be represented by three examples unless the remaining items are linked to a versioned authoritative annex.
- `EMBEDDED` means the complete atomic content appears in the product specification.
- `AUTHORITATIVE_ANNEX` means the source or normalized annex remains part of the frozen delivery package and the main PRD states its authority, version, owner, and module mapping.
- `DEFERRED` requires scope reason, owner, target release, and downstream impact.
- `CONFLICT` records both values/behaviors and the decision owner; do not silently choose.
- `NOT_APPLICABLE` requires a reason.
- Zero silent omission: every registered source item must have a disposition before Gate 3 can pass.
- Assertion status is separate from disposition. `VERIFIED` can be used as a requirement. `INFERRED` needs evidence and reviewer owner. `PROPOSED` is a recommendation until accepted by the accountable owner. `UNKNOWN` and `CONFLICT` block PASS when they affect core behavior.
- Prototype gaps use prototype evidence status, not source disposition. Use `VERIFIED`, `SPEC_ONLY`, `GAP`, `CONFLICT`, or `UNKNOWN` in the interaction ledger or verification report.

Recommended `stage0-output.json` extension:

```json
{
  "sourceEvidenceRegister": [
    {
      "sourceId": "SRC-001",
      "artifact": "metrics.xlsx",
      "locator": "Dashboard!A2:D46",
      "evidenceType": "metric-caliber",
      "atomicItemCount": 45,
      "authority": "authoritative",
      "targetModule": "M01 Dashboard",
      "disposition": "AUTHORITATIVE_ANNEX",
      "assertionStatus": "VERIFIED",
      "traceTo": ["M01", "ANNEX-H", "TC-M01-*" ]
    }
  ]
}
```

### stage0-output.json Minimum Shape

```json
{
  "artifact": "path-or-url",
  "annotationPattern": {"detected": "semantic|inline|file-route|external-spa"},
  "externalDependencies": {"scripts": [], "stylesheets": [], "dataFiles": []},
  "domainModel": {"entities": []},
  "views": [],
  "features": [],
  "interactionLedger": {
    "navViews": [],
    "actions": [],
    "handlers": [],
    "modals": [],
    "roleFlows": [],
    "dataSets": [],
    "criticalWorkflows": []
  },
  "stateMachine": {},
  "roles": [],
  "qualityFindings": [],
  "confidenceSummary": {"confirmed": [], "inferred": [], "unknown": []}
}
```

### Regression Detection

When analyzing vN, compare against vN-1 change notes or bug list if available.

Check:
- duplicate function definitions;
- new handler missing from event delegation;
- state value missing from badge/color mapping;
- deleted navigation still referenced;
- build script overwriting manual fixes;
- old stubs overriding real implementations.

### Prototype Iteration Parity Gate

When generating vN from vN-1, the prior prototype is the regression oracle. First extract an interaction baseline ledger:

```json
{
  "views": ["view-id-or-title"],
  "actions": ["data-action-or-onclick-command"],
  "handlers": ["function-or-event-handler"],
  "modals": ["modal-purpose"],
  "roleFlows": ["role -> reachable views/actions"],
  "dataSets": [{"name": "indicators", "count": 39}],
  "criticalWorkflows": [
    {"name": "create from template", "steps": ["open", "select", "confirm", "view result"]}
  ]
}
```

Gate rule: a new prototype fails if it removes baseline views, actions, handlers, modals, role flows, data sets, or critical workflows without an explicit de-scope note.

De-scope note format:

```yaml
removed_item: action-or-view-name
reason: why it is no longer needed
owner: PM/Design/Dev
replacement: new path or "none"
approved_by: reviewer
```

Interaction parity checks:
- Count both semantic actions (`data-action`) and inline handlers (`onclick`).
- Compare named views, not only route counts.
- Compare action-to-handler binding; every primary command must produce a visible view, state, modal, or data change. Toast may be secondary feedback, not the sole result.
- Compare representative data volume for mock data arrays; do not shrink data sets so far that empty, long-tail, or permission states disappear.
- Preserve role-specific navigation and task flows unless explicitly removed.
- Semantic annotations improve testability, but they do not replace working prototype behavior.

## Engineering Profile / Anti-Bloating

Use the smallest contract that can safely deliver the feature. Do not introduce multi-agent topology, prompt graph, DAG router, or prompt registry complexity when ordinary product logic is cheaper and more reliable.

Do not call these profiles “tiers”; delivery tiers are L0-L3. Classify per module.

| Engineering Profile | Use When | Required Contract | Do Not Require |
|---|---|---|---|
| Profile S: Deterministic / AI-Supporting | list/detail, create/edit, approval, query/report, deterministic rules, or AI assistance with a valid manual path | role path, state-button matrix, prototype actions, tests, optional AI Feature Injection | dynamic DAG, multi-agent graph, prompt topology, autonomous tool planning |
| Profile A: AI-Core / Agentic | primary outcome depends on AI, AI chooses tools/routes, autonomous workflow write, or multi-agent collaboration | AI Native Harness, runtime contract, prompt/tool registry, eval, observability, rollback, human gate | direct production write without harness |

Escalate from Profile S to Profile A only when at least one is true:

- AI selects tools, routes, or downstream workflow steps.
- AI output writes business state or creates workflow tasks.
- AI directly determines a consequential compliance, money, customer, safety, or legal outcome without independent qualified human verification.
- A single linear prompt cannot be tested and operated safely.
- Failure recovery needs shadow/canary/replay/rollback at runtime.

Downgrade from Profile A to Profile S when:

- a deterministic rule engine or normal backend code is simpler than prompt orchestration;
- prompt maintenance cost exceeds the feature's business value;
- the team cannot name the agent write scope, fallback, eval set, and owner;
- the feature is only UI display, CRUD, filtering, export, or manual review support.

Rule: prompt and agent architecture must reduce delivery risk. If it mainly increases vocabulary, documents, and maintenance load, use code, configuration, or a single linear AI feature contract.

## Stage 1-5 Product Workflow

Run only the stages needed by the selected artifact scope and execution mode. Skip stages whose inputs are already supplied and validated.

Stage 1 Brainstorm:
- When opportunity framing is in scope, frame the opportunity and write a testable outcome/JTBD.
- Use ICE or another prioritization method only when comparing options.

Stage 1.5 Research:
- Run only when evidence, policy, market, domain, or competitor uncertainty affects the decision.
- Output domain norms, gaps, policy notes, interview questions.

### 1.3 Business Readiness And Requirement Diagnosis Anchors

Before detailed feature design, run these defensive anchors when the artifact
will guide development, customer demo, QA, compliance, or workflow design. If a
core answer is missing, record `BLOCKED` or `REVIEW_COMPLETE_WITH_GAPS` instead
of inventing business rules.

| Anchor | Required Question | Output |
|---|---|---|
| Accountability / compliance | Who owns the final administrative or commercial judgment? Are there data overreach, legal, audit, privacy, safety, or industry compliance red lines? | accountable decision role, prohibited system behavior, human override rule |
| Adversarial semantics | If a user enters evasive, vague, hostile, or low-information data such as “收到”, “再看”, “不知道”, what should the system block, warn, escalate, or record? | invalid-generic-response list, guard, penalty/escalation, audit |
| Offline / concurrency | If multiple users operate the module under weak network/offline/stale data, what is the final conflict reconciliation strategy? | version lock, merge policy, queue/retry, highlight review, rollback/compensation |

Minimum anchor record:

```yaml
requirement_diagnosis_anchor:
  accountability_owner:
  compliance_red_lines:
  invalid_generic_inputs:
  guard_or_escalation:
  offline_behavior:
  concurrency_strategy:
  unresolved_decision_owner:
```

Do not over-ask for L0 exploration. For L0/Lite, capture only the anchors that
could change the prototype path or invalidate the idea.

Stage 2 Stakeholder Profile:

| Stakeholder | Required Dimensions |
|-------------|---------------------|
| Sponsor | role, success criteria, constraints, risk tolerance |
| End user | daily workflow, pain, workarounds, tech comfort |
| Dev lead | constraints, integrations, team capacity, historical risks |

Stage 3 Requirement Design:
- Write solution overview: what and why, not how and pixel.
- Metrics format: `[Metric]: [Current] -> [Target] in [Timeline]`.
- Epic hypothesis must be falsifiable.
- Out of Scope lists material exclusions and revisit conditions; do not pad it to an arbitrary count.

Stage 4 Stories + State Machine:
- Story format: As a [persona], I want [action], so that [value].
- AC format: Given / When / Then + Expected UI Result + Expected Domain Result.
- Every story includes happy, error, and boundary paths.
- Every state transition includes Trigger + Guard + Action.
- A story is not Stage-4 complete if it only states a visible UI result. It must also state the domain object change, domain event, audit record, task creation, notification, or measurable state change.

Stage 5 PRD + Prototype:

PRD chapters:
1. Problem statement
2. Users and personas
3. Core business concepts
4. Information architecture
5. Feature modules
6. Business processes
7. State transitions
8. User interactions
9. Edge cases
10. Non-functional requirements

For L2/L3, Stage 5 has three coordinated layers, in this authority order:

1. **Traditional Product Requirement Specification**: background, goals, scope, users, information architecture, business processes, complete functional details, shared rules/data, NFR, acceptance, planning, and risks. This is the primary product truth consumed by PM, design, development, algorithm, and QA.
2. **Complete Module And Function Specifications**: one inventory per module and one deterministic functional requirement record per in-scope release function, using the detailed structure below.
3. **Engineering Traceability Contracts**: DDD module contract, Developer Fast-Lane, API/schema/test mappings layered on top of the product specification.

The engineering layer does not replace the product layer. A module is not development-ready when it only states purpose, inputs, outputs, aggregates, and commands while omitting page behavior, fields, dictionaries, actions, rules/calibers, states, permissions, exceptions, and acceptance.

### Complete Module And Function Product Specification

Start each module with a function inventory. The inventory defines the denominator for completeness.

| Function ID | Function Name | User Outcome | Surface / Page | Release Scope | Detailed Record | Source IDs | Test IDs |
|---|---|---|---|---|---|---|---|
| M04-F01 | Query enterprises | find enterprises in the authorized scope | PC list | in | M04-F01 | SRC-... | TC-... |

Inventory rules:

- Include every user-visible command, query, configuration, review, import/export, batch operation, scheduled/system action, and material exception path planned for the release.
- Do not hide multiple independent functions under labels such as “management”, “supports”, “etc.”, “related operations”, or “complete lifecycle”.
- Split functions when role, permission, trigger, aggregate/data owner, state transition, business result, audit/NFR, or acceptance path differs. Creating a ticket, accepting it, escalating it, closing it, confirming a contract, and registering payment are normally different release functions.
- Navigation, open/close modal, filter, pagination, tab switch, and confirmation helpers may map to an owning function only when they have no independent domain result. The mapping still must be explicit in the action ledger.
- `planned release functions = complete functional requirement records` is mandatory. Deferred/external functions remain in the inventory but do not enter the release denominator.
- A screenshot, prototype, workbook, SQL table, policy, or previous PRD is evidence. It does not become an implementable requirement until its behavior is mapped to a functional record or a frozen authoritative annex.

For each function in the release inventory, write a deterministic functional requirement record:

| Section | Required Content |
|---|---|
| Identity and value | function ID/name, module, priority, release, user value, source IDs |
| Roles and scenario | initiating/collaborating roles, trigger, start condition, successful exit, next action |
| Entry and preconditions | page/route/entry, role/data prerequisites, upstream state, feature/config flags |
| Pages and visible states | list/detail/create/edit/config/result, loading/empty/error/success/disabled behavior |
| Fields and dictionaries | every input/output field or authoritative annex range; meaning, type, required/default, enum, source, validation, editability, masking |
| Numbered interaction flow | user action and corresponding system response for each step; no one-line “supports create/edit/delete” shorthand |
| Actions and results | action, confirmation, visible result, domain result, next action, idempotency/duplicate behavior |
| Business rules and calibers | numbered rules, priority, formulas/thresholds, time boundary, conflict behavior, effective version |
| State-button behavior | object state, visible/forbidden actions, guards, transitions, audit/event |
| Permission and data scope | tenant/org/region/enterprise/row/field/action scope and override/approval policy |
| Exceptions and recovery | validation, empty, duplicate, stale/conflict, permission, timeout, dependency failure, partial success, retry/reopen/rollback |
| Notifications and audit | recipient, channel, trigger, template/contents, failure behavior, audit fields |
| Data / AI / algorithm contract | when applicable: input/output schema, deterministic vs model responsibility, confidence/threshold, human confirmation, prompt/model/rule version, fallback, evaluation and prohibited writes; otherwise `N/A + reason` |
| Dependencies and NFR | source of truth, upstream/downstream timing, performance, security/privacy, compatibility, operations |
| Acceptance | happy, validation, permission, state conflict, dependency failure, regression; expected UI and domain result |

Any section that truly does not apply must say `N/A` and why. Blank, omitted, “同上”, “见原型”, or “按现有逻辑” does not count as complete.

### Module Shared Contracts

After the per-function records, consolidate only genuinely shared module contracts. Shared contracts are semantic de-duplication and navigation aids; they cannot replace the release function inventory or make an incomplete FRR complete.

| Section | Minimum Content |
|---|---|
| Purpose and boundary | user/business outcome, in-scope and explicitly deferred capabilities |
| Roles and scenarios | initiating role, collaborating roles, start/exit conditions, role path |
| Pages and views | list/detail/create/edit/configure/result views, entries, exits, empty/error/loading states |
| Fields and dictionaries | label, meaning, type, required/default, source, validation, dictionary values, editable roles, display/masking |
| Actions and interactions | trigger, precondition, confirmation, visible result, domain result, next action |
| Business rules and calibers | numbered rule, priority, formula/caliber, effective range, evidence source, conflict handling |
| State-button matrix | object state, visible/forbidden actions, guards, transition/event/audit |
| Permission and data scope | role, organization/tenant/region scope, row/field/action permissions, override policy |
| Exceptions and fallback | validation, duplicate, stale/conflict, permission, timeout, partial failure, retry/reopen/rollback |
| Cross-module and external contract | upstream/downstream dependency, source of truth, sync timing, failure ownership |
| Data, metrics, AI, audit, NFR | only the applicable contracts, with evidence and acceptance |
| Acceptance and traceability | story/test IDs, expected UI/domain results, prototype mapping, source evidence IDs |

Depth rule:

- `FULL_SPEC`: mandatory for every module planned for implementation in the selected release, and may be declared only when the inventory denominator equals the number of complete function records and shared contracts are complete.
- `OVERVIEW_ONLY`: allowed only for out-of-scope/deferred/external modules, with owner and revisit condition.
- Large atomic tables may live in an authoritative annex, but the module section must state the governing source/version, item count, usage rules, and traceability. An appendix is not a dumping ground for unowned requirements.
- Module summaries, purpose/input/output tables, engineering overlays, and Fast-Lane rows are indexes only. They never satisfy the functional-detail denominator.

Prototype rules:
- Use design-system tokens and real app screen as first viewport.
- Every interactive element has `data-testid` and `data-action`.
- Every stateful container has `data-state`.
- Every backend-backed component has `data-api` + `data-method`.
- Every role-specific view has `data-visible-role`.
- If based on an older prototype, preserve the interaction baseline ledger or document approved de-scope.

## Human-Readable PRD Layer

For L1+ PRD, product specification, or development handoff documents, load
`readability-layer.md` after the core structure is selected. This is a
presentation and comprehension layer, not a replacement for FRR completeness.

Mandatory readable PRD behaviors:

| Need | Required Treatment |
|---|---|
| fast orientation | executive summary within one screen |
| business context | module scenarios before field/API/DDD tables |
| RD/QA clarity | explicit boundary, exception, permission, state conflict, network/offline, and fallback paths |
| operating feedback | metrics and event tracking where post-launch operation or conversion/risk monitoring matters |
| multi-role handoff | frontend/backend/QA notes that point to FRR/state/prototype/acceptance IDs |
| rule clarity | concrete examples for thresholds, formulas, time windows, scores, and AI confidence rules |

Fail the PRD readability layer when a module starts with only API/schema/DDD
tables, uses phrases such as “supports related operations”, “see prototype”,
“existing logic”, “intelligent processing”, or lacks business examples for
non-obvious rules.

### 5.4 E2E Cross-Module Canvas

For workflow-heavy PRDs, development handoff must not stop at isolated module
state machines. Provide a long-running lifecycle matrix that connects upstream
state changes, domain events, downstream state changes, ownership, and tests.

Required when any is true:

- `WORKFLOW: true` in 0D triage;
- two or more modules exchange task, event, audit, status, report, payment,
  notification, import, or approval state;
- QA must write integration/E2E tests;
- backend services or bounded contexts need event or Saga coordination.

Canvas format:

| E2E ID | Upstream Module / Object | Source State -> Target State | Domain Event | Downstream Module / Object | Downstream State Flow | Owner / Transaction Boundary | Failure / Compensation | Acceptance |
|---|---|---|---|---|---|---|---|---|
| E2E-001 | Lead | 有意向 -> 已转商机 | `LeadConverted` | Opportunity / Customer | 新建商机[初步接触] + 客户[锁定中] | CRM service; event outbox | duplicate event ignored by idempotency key | AC-E2E-LONG-RUNNING-001 |

Rules:

- Do not invent integration events when the product is a single isolated CRUD
  surface. Use the canvas only when cross-module lifecycle value exists.
- Each row must have a testable source state, event, downstream state result,
  transaction/consistency owner, and failure behavior.
- QA must be able to convert each row into an E2E integration or regression
  scenario without rereading the whole PRD.
- Backend must be able to identify event payload version, idempotency key,
  ordering/replay rule, and dead-letter owner for async rows.

## Guard Protocol

Guard format:

```yaml
transition:
  from: current_state
  to: next_state
  trigger: user_or_system_action
  guard:
    role: allowed_role
    state: required_entity_state
    data: required_data_condition
    time: optional_time_window
    org: optional_org_scope
  action: side_effect
```

Guard types:
- role guard: who can act;
- state guard: what lifecycle state allows action;
- data guard: what fields/metrics must satisfy;
- time guard: deadlines, windows, timeout;
- hierarchy guard: supervisor approval and escalation;
- org guard: region/tenant/department isolation;
- cross-entity guard: entity A action depends on entity B state.

Common failure: state diagrams show transitions but do not define who may trigger them or what data condition blocks them.

## Complexity Budget Counting

Count business contracts, not visual decoration or implementation trivia.

| Item | Count One When | Do Not Count Separately When |
|---|---|---|
| state | it has an independent transition, guard, allowed/forbidden action, SLA, audit meaning, or domain result | it is only a loading skeleton, tab selection, hover, temporary animation, or display alias |
| action | business action + guard combination + domain result is unique | the same action appears on PC/mobile with the same guard and domain result |
| API | the consumer depends on a distinct command/query contract | multiple UI components call the same contract or one endpoint is merely paginated |
| AI agent | it has an independent prompt/runtime identity, goal, write scope, failure policy, and owner | it is a deterministic tool, API adapter, prompt helper, or display component |
| PRD page | the document is rendered with a declared page size and margins | the source is Markdown or an unrendered editor view; report page count as N/A |

Boundary examples:

| Case | Count | Result |
|---|---:|---|
| `submit` on PC and mobile uses the same permission, transition, and event | 1 action | PASS: surface duplication does not inflate scope |
| `submit` as draft save and `submit` as final approval use different guards/events | 2 actions | PASS only if both are counted |
| `pending_review` and `returned` expose different actions and audit meaning | 2 states | PASS only if both are counted |
| `loading`, `empty`, and `error` are UI states without domain transitions | 0 business states; still verify as UI states | do not hide them, but do not inflate domain state count |
| one orchestrator calls two deterministic APIs | 1 agent, 2 tool/API contracts | FAIL if adapters are reported as agents |
| offline submit creates `queued_for_sync` before server acceptance | separate state/action path | count separately because guard and domain result differ |

If a tier budget is exceeded, do not relabel items to make the count pass. Record the owner and reason, then split a bounded context/module, de-scope, or approve the exception.

## SIM Review

SIM 1 after Stage 3: review solution before prototype.

SIM 2 after Stage 5: review PRD + prototype together.

### Persona Walkthrough Script

For each required reviewer, execute the review instead of generating a generic opinion:

1. Give the persona one concrete task, start state, role/data scope, and only the cues visible in the artifact.
2. Walk one action at a time. Do not reveal the intended design, hidden route, or expected answer.
3. Record `step`, `visible cue`, `chosen action`, `visible result`, `domain result`, and `blocker/assumption`.
4. If the next step cannot be inferred from the artifact, stop that path and mark the exact blockage. Do not invent a button or explain the design to the persona.
5. After the walkthrough, produce the reviewer verdict and findings with artifact evidence.

Minimum walkthrough record:

| Step | Visible Cue | Persona Action | Visible Result | Domain Result | Blocker/Assumption |
|---|---|---|---|---|---|

Reviewer outputs and anti-patterns:

| Reviewer | Required Output | Invalid Generic Response | Valid Evidence-Shaped Response |
|---|---|---|---|
| Sponsor | PASS/NEEDS_REVISION + outcome, cost, control concerns | “The design looks comprehensive.” | “No owner or SLA exists for overdue high-intent leads; business closure fails.” |
| End User | task walkthrough + concrete pain points | “The DDD model is reasonable.” | “I clicked Submit, saw only a toast, and could not find the created record.” |
| Peer PM | scope/state gaps + complexity PASS/FAIL | “The requirements are complete.” | “Returned state has no resubmit path; 2 actions are missing from the count.” |
| Dev Lead | feasibility + undefined contracts/dependencies | “This should be feasible.” | “The approve command lacks idempotency, expected version, and rejection event.” |

Do not let personas share hidden conclusions before their own walkthrough. Merge findings only after each required perspective produces evidence.

### Backend Closure Rules

For each state-changing command, define:

- aggregate or data owner;
- command input and output schema;
- expected version or concurrency strategy;
- idempotency key and scope;
- transaction/Saga boundary and rollback/compensation rule;
- persisted result and domain event;
- audit fields;
- retry, duplicate, stale write, dependency failure and reconciliation behavior.

For async or cross-module flows, also define event id, producer, payload version, ordering/replay behavior, dead-letter handling, alert owner and recovery path.

## Developer Prompt Skeleton

Use this when handing off to an implementation agent:

```markdown
You are implementing from REQUIREMENT.md and PROTOTYPE.html.

Rules:
- Business logic follows PRD state machines and guards.
- UI behavior follows prototype data-* annotations.
- Do not invent hidden states or API contracts.
- Report gaps instead of guessing.
- Keep role/org/data isolation explicit.

Must verify:
- PRD states match `data-state`.
- ACTION IDs match `data-action`.
- API contracts match `data-api` + `data-method`.
- Fields match `data-field` / `data-bind`.
- Role matrix matches `data-visible-role`.
```

## Quality Gate Summary

Gate 1 Requirement Review:
- Business can restate problem.
- Metrics and Out of Scope accepted.
- At least one missing scenario added.

Gate 2 Prototype Walkthrough:
- Run the Persona Walkthrough Script against each scoped primary task without design hints.
- Record the exact step and visible cue where the persona blocks; do not explain the route during execution.
- No major "if only it could..." gaps remain.
- If this is an iteration, no unapproved loss appears in the interaction parity gate.

Gate 3 Dev Pre-review:
- Dev Lead can restate core logic.
- Risks have mitigation.
- Estimate is concrete.
- Spec tier is justified; simple CRUD/linear workflow is not over-modeled as multi-agent DAG.
