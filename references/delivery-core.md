# Delivery Core

Use this file for reverse engineering, PRD generation, state machines, guards, SIM review, and developer handoff.

## Contents

- Stage 0 Reverse Engineering
- Engineering Profile / Anti-Bloating
- Stage 1-5 Product Workflow
- Guard Protocol
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

Prototype rules:
- Use design-system tokens and real app screen as first viewport.
- Every interactive element has `data-testid` and `data-action`.
- Every stateful container has `data-state`.
- Every backend-backed component has `data-api` + `data-method`.
- Every role-specific view has `data-visible-role`.
- If based on an older prototype, preserve the interaction baseline ledger or document approved de-scope.

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

## SIM Review

SIM 1 after Stage 3: review solution before prototype.

SIM 2 after Stage 5: review PRD + prototype together.

Required outputs:
- Sponsor: PASS/NEEDS_REVISION + business/control concerns.
- End user: task walkthrough + pain points.
- Peer PM: scope creep, state gaps, complexity budget PASS/FAIL.
- Dev Lead: feasibility, hidden complexity, undefined dependencies.

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
- User completes core task without hints.
- Confusion points are recorded, not explained away.
- No major "if only it could..." gaps remain.
- If this is an iteration, no unapproved loss appears in the interaction parity gate.

Gate 3 Dev Pre-review:
- Dev Lead can restate core logic.
- Risks have mitigation.
- Estimate is concrete.
- Spec tier is justified; simple CRUD/linear workflow is not over-modeled as multi-agent DAG.
