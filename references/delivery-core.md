# Delivery Core

Use this file for reverse engineering, PRD generation, state machines, guards, SIM review, and developer handoff.

## Contents

- Stage 0 Reverse Engineering
- Prototype Interaction Ledger
- Engineering Profile / Anti-Bloating
- Lifecycle And Spec-Plan-Tasks Bridge
- Stage 1-5 Product Workflow
- Human-Readable PRD Layer
- Guard Protocol
- Field-Level Permission
- Complexity Budget Counting
- SIM Review
- Developer Prompt Skeleton
- Quality Gate Summary

## Stage 0 Reverse Engineering

Use Stage 0 when the input is an existing HTML prototype, legacy system, screenshot, Excel template, or competitor product.

### Unstructured Input Protocol

Use this branch when the input is a raw idea, pain statement, meeting note,
boss message, customer complaint, competitor feature list, or short feature
request rather than a structured PRD/prototype.

Do not jump directly to a full PRD. First normalize the input:

1. Classify the input type: `idea` / `pain` / `solution` / `feature_list` /
   `meeting_note` / `evidence_bundle`.
2. Extract signals into `KNOWN`, `INFERRED`, `MISSING`, and `CONFLICT`.
3. Identify the smallest clarification set needed before Stage 1.

Minimum output:

```yaml
unstructured_input_parse:
  input_type:
  known:
    users:
    pain_or_outcome:
    proposed_solution:
    constraints:
    evidence:
  inferred:
    assumptions:
    likely_domain:
    likely_workflow:
  missing:
    - question:
      why_it_matters:
      blocks: story | role_path | state | data | acceptance | feasibility
  conflicts:
    - issue:
      decision_owner:
  recommended_next_step: clarify | opportunity_shape | light_prd | prototype | standard_prd
```

Rules:

- Ask only the minimum questions needed for the requested output.
- If the user wants fast exploration, keep missing items as assumptions and end
  with upgrade triggers.
- If the artifact will guide development, QA, customer demo, bid, or coding
  agent implementation, unresolved P0 missing items block `PASS`.

### 0.5 Input Clarification Protocol

Run this before Stage 1 when the request is ambiguous, idea-only, or missing
enough context that the product direction could change.

Ask 3-5 targeted questions. Do not ask a questionnaire. Choose questions by
input type:

| Input Type | Ask First |
|---|---|
| raw idea | target user, painful moment, desired outcome, current workaround |
| pain / complaint | frequency, severity, affected role, current cost, unacceptable failure |
| proposed solution | underlying problem, success metric, alternative solutions, must-not-do |
| feature list | primary workflow, release goal, role priority, out-of-scope boundary |
| old PRD/prototype upgrade | what changed, what must be preserved, what can be removed, acceptance owner |
| competitor feature | customer job, switching barrier, differentiation hypothesis, proof needed |

Question format:

```yaml
clarification_question:
  id: CQ-001
  question:
  why_it_matters:
  answer_type: free_text | choose_one | choose_many | numeric | owner_decision
  if_unanswered_default:
  downstream_impact: scope | role | state | data | acceptance | risk
```

After answers, return a decision:

| Decision | Meaning | Next Step |
|---|---|---|
| `READY_FOR_LIGHT_PRD` | enough for L1 alignment | write light PRD and gaps |
| `READY_FOR_OPPORTUNITY_SHAPING` | problem/opportunity still needs shaping | run Opportunity Shaping Protocol |
| `READY_FOR_STANDARD_PRD` | enough for development-oriented PRD | enter Stage 1-5 |
| `BLOCKED_BY_P0_UNKNOWN` | missing item would change scope, owner, legality, data, or feasibility | ask owner or record blocked |

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

### Prototype Interaction Ledger

When the input includes an HTML prototype, before drafting any PRD content,
extract a complete interaction ledger. This ledger is the single source of
truth for cross-validating PRD coverage.

#### Extraction Procedure

1. **Page inventory**: Parse all distinct views/pages. Record as
   `{ page_id, page_title, route_or_file, role_visibility }`.
2. **Action inventory**: Parse every interactive element with `data-action`,
   `onclick`, or equivalent handler. Record as
   `{ action_id, page_id, element_text, handler_function, action_type }`.
   Action types: `navigate | create | update | delete | submit | filter |
   sort | export | import | confirm | cancel | toggle | drag | select | custom`.
3. **Modal inventory**: Parse all `showModal`, `Modal.open`, `dialog`,
   `drawer`, `confirm`, and popup-like patterns. Record as
   `{ modal_id, trigger_action, page_id, fields[], required_fields[] }`.
4. **State enum inventory**: Parse badge mappings, status colors, lifecycle
   functions. Record as `{ enum_name, values[], source_function, page_id }`.
5. **Role inventory**: Parse `data-visible-role`, role-based conditionals,
   navigation restrictions. Record as `{ role_id, reachable_pages[],
   reachable_actions[] }`.
6. **Field inventory**: Parse form fields, table columns, data bindings.
   Record as `{ field_id, page_id, component_type, data_type, required,
   enum_source }`.
7. **Workflow inventory**: Parse multi-step sequences (wizard, stepper,
   approval flow). Record as `{ workflow_id, steps[], roles[] }`.

#### Output Format

Save as `prototype-interaction-ledger.json` alongside `stage0-output.json`:

```json
{
  "artifact": "path-or-url",
  "extractedAt": "ISO-8601",
  "pages": [],
  "actions": [],
  "modals": [],
  "stateEnums": [],
  "roles": [],
  "fields": [],
  "workflows": [],
  "summary": {
    "pageCount": 0,
    "actionCount": 0,
    "modalCount": 0,
    "stateEnumCount": 0,
    "roleCount": 0,
    "fieldCount": 0,
    "workflowCount": 0
  }
}
```

#### Coverage Verification

After generating the PRD, run a cross-coverage check against the ledger:

| Category | Coverage Rule | Block Gate 3 If Below |
|---|---|---|
| Pages | Every page in ledger appears in PRD §4 (Pages/Regions) | 100% |
| Actions | Every action in ledger appears in at least one FRR §6 interaction step | 95% |
| Modals | Every modal in ledger appears in at least one FRR §6 `modal_spec` | 90% |
| State Enums | Every enum value in ledger appears in PRD §9 state matrix | 95% |
| Roles | Every role in ledger appears in PRD §7 (Users/Roles/Permissions) | 100% |
| Fields | Every field in ledger appears in FRR §5 field dictionary or authoritative annex | 90% |
| Workflows | Every workflow in ledger appears in E2E Cross-Module Canvas | 100% |

Missing items below the threshold produce a `COVERAGE_GAP` flag listing each
missing item with its prototype location. Items above the threshold but below
100% must have an explicit de-scope reason.

#### Regression Detection

When analyzing vN against vN-1, use the ledger diff:
- Pages removed without de-scope note → `REGRESSION_BLOCK`
- Actions removed without de-scope note → `REGRESSION_BLOCK`
- Modals removed without de-scope note → `REGRESSION_BLOCK`
- State values removed without de-scope note → `REGRESSION_BLOCK`
- New items added → verify they appear in the PRD

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

Do not call these profiles "tiers"; delivery tiers are L0-L3. Classify per module.

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

## Lifecycle And Spec-Plan-Tasks Bridge

Use external product or SDD frameworks as upstream evidence, not as a second
pipeline. Map them into this lifecycle only when the requested artifact needs
that stage.

| Lifecycle Stage | Purpose | Minimum Artifact | Do Not Expand Into |
|---|---|---|---|
| Discover | decide whether the opportunity is worth shaping | outcome, customer/job, evidence, riskiest assumption, next validation | full PRD when user only needs direction |
| Specify | define what/why/acceptance | complete product specification, FRRs, source register, role paths | implementation plan or coding tasks |
| Plan | decide how the team will safely implement | architecture/dependency assumptions, data/API/DDD contracts, risk plan | framework choices inside business-only PRD sections |
| Tasks | split work for execution | vertical slice backlog tied to FRR/AC IDs | layer-by-layer tickets that cannot demo value |
| Build/Verify | implement and test | prototype/test evidence, acceptance results, defect/risk log | launch approval without readiness |
| Launch | release or migrate | readiness checklist, rollout, rollback, notice, owner | new feature scope |
| Learn/Retire | operate, improve, or sunset | metric review, incident/post-launch learning, retirement plan | unowned backlog dumping |

Spec/Plan/Tasks separation:

- **Spec** is product truth: user story, functional behavior, fields, rules,
  states, permissions, exceptions, source evidence, and acceptance.
- **Plan** is implementation alignment: architecture constraints, seams,
  dependencies, data/API/DDD contracts, release strategy, and risk controls.
- **Tasks** are execution slices: small enough to assign, broad enough to
  produce a visible/domain result, and traceable to FRR + acceptance IDs.

Do not force this bridge onto L0 idea exploration. For L2/L3 development
handoff, however, missing plan/task traceability is a delivery risk.

### Vertical Slice Task Backlog

Generate this only when the user requests build planning, issue breakdown, or
developer handoff.

| Task ID | Slice / Outcome | Source FRR | Acceptance IDs | Owner Role | Depends On | Files / Modules Likely Touched | Test / Evidence | Done Signal |
|---|---|---|---|---|---|---|---|---|
| TASK-001 | | Mxx-Fnn | AC-... | frontend/backend/algorithm/QA | none / TASK-... | optional, keep stable if known | | demoable path or passing test |

Rules:

- Prefer tracer-bullet vertical slices that cut through UI, API, data, and test
  only as far as needed for one user-visible/domain result.
- Use domain vocabulary from the PRD. Do not invent issue titles from
  implementation layers only.
- Mark dependencies explicitly. A task is not ready if it needs an unresolved
  business rule, missing field dictionary, or unknown permission decision.
- Avoid stale implementation detail. File paths are useful when known from an
  existing codebase, but product tasks must remain understandable without them.

## Stage 1-5 Product Workflow

Run only the stages needed by the selected artifact scope and execution mode. Skip stages whose inputs are already supplied and validated.

Stage 1 Brainstorm:
- When opportunity framing is in scope, frame the opportunity and write a testable outcome/JTBD.
- Use ICE or another prioritization method only when comparing options.

### 1.1 Opportunity Shaping Protocol

Use this when the user has a vague idea, pain, customer signal, policy/business
pressure, or proposed solution but not yet a stable requirement.

Pick the matching path:

| Path | Use When | Questions |
|---|---|---|
| A. Idea -> opportunity | the input is "I want to build X" | Who has the painful moment? What job/outcome changes? What is the current workaround? What evidence says this matters now? |
| B. Pain/data -> options | the input names pain or metrics but no solution | What segment is most affected? What root causes are plausible? What solution options exist? Which assumption is riskiest? |
| C. Solution -> hypothesis | the input already proposes a feature | What problem would make this feature necessary? What metric proves value? What simpler/manual alternative exists? What must be true for this to work? |

Output:

```yaml
opportunity_shape:
  target_user:
  painful_moment:
  job_to_be_done:
  desired_outcome:
  current_workaround:
  evidence:
  solution_options:
    - option:
      benefit:
      risk:
      validation:
  riskiest_assumption:
  next_artifact: one_pager | light_prd | prototype | research_plan | no_go_note
```

Rules:

- Keep L0/Lite outputs short: one opportunity, 2-3 options, one riskiest
  assumption, one next artifact.
- Do not force TAM/SAM/SOM, competitor matrices, or full strategy unless the
  request is a new market, major investment, board decision, or positioning
  problem.
- If the user asks for implementation before the opportunity is shaped, produce
  `REVIEW_COMPLETE_WITH_GAPS` and list the assumptions that coding would lock in.

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
| Adversarial semantics | If a user enters evasive, vague, hostile, or low-information data such as "收到", "再看", "不知道", what should the system block, warn, escalate, or record? | invalid-generic-response list, guard, penalty/escalation, audit |
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
- Output the **information architecture skeleton (IA Skeleton)** before any pixel-level prototype or PRD section 4/5/9 detail is produced. See Stage 3.5 below.

Stage 3.5 IA Skeleton Gate (NEW):

Purpose: lock the structural decisions that currently leak into PRD FRR sections
4-6 (pages, regions, fields, flow). The IA Skeleton is a PM-facing contract:
role × module × view × region × primary action. It must be confirmed before
prototype or PRD detail work begins.

When to run:
- L1+ PRD or handoff where the scope has ≥2 modules, ≥2 primary roles, or any
  cross-module flow.
- When the user input is "I need a system to do X" without a confirmed page map.
- When the prior PRD grew because "we kept adding views/fields/rules later".

IA Skeleton output format (one module per block):

```yaml
ia_skeleton:
  version: 1.0
  modules:
    - module_id: M01
      module_name: 驾驶舱
      primary_roles: [老板, 销售负责人, 产研, 财务, 客服, 运营]
      views:
        - view_id: M01-V01
          view_name: 老板驾驶舱
          view_type: dashboard          # dashboard | list | detail | form | config | modal
          entry_path: /dashboard?role=boss
          regions:
            - region_id: R01
              region_name: 顶部指标卡片区
              components: [StatCard×8]
              data_owner: backend_aggregate
              visible_to: [老板]
            - region_id: R02
              region_name: 销售漏斗
              components: [FunnelChart]
              data_owner: opportunity_pipeline
          primary_actions:
            - action: 点击卡片→跳转对应模块
              target: 模块详情页
          modal_or_page: page
          related_views: [M02-V01, M04-V01]
```

Rules:

1. **View completeness**: every primary role must have at least one view where
   they accomplish their core job. A view is a page, drawer, or modal that a
   role deliberately navigates to.
2. **Region minimality**: regions are coarse-grained (header, sidebar, main
   content, footer, drawer body, modal body). Do not specify pixel sizes,
   colors, or component props.
3. **Action minimality**: list only the role's primary actions that cross views
   or change domain state. Do not enumerate every button.
4. **Cross-view flow**: for every object that moves across modules (lead →
   opportunity, ticket → requirement, opportunity → contract), document the
   source view ID and target view ID.
5. **Confirmation lock**: after presenting the IA Skeleton, ask the PM/Sponsor
   to confirm or revise. Output:
   ```
   [CONFIRM LOCK] IA Skeleton v1.0 — 0 unresolved structural gaps
   ```
   Do not proceed to Stage 4 or Stage 5 until the lock is granted, or every gap
   is explicitly accepted as a `PROPOSED` decision with an owner.

### Global Entity Field Dictionary (Stage 3.5 Output)

The Global Entity Field Dictionary is an附属产出 of Stage 3.5, produced after
the IA Skeleton lock and before Stage 4. It serves as the input for FRR §5
field dictionaries.

- **Owner**: PM (with input from engineering for system-filled fields).
- **Consumer**: FRR generation in Stage 5; coding agent handoff.
- **Format**: One table per entity, covering every field across all sub-pages
  (list, create, edit, detail, filter). Use
  `references/templates/field-dictionary-template.md`.
- **Gate rule**: FRR §5 must reference the global dictionary by field name. Do
  not re-declare common fields in each FRR; only list fields whose meaning,
  validation, or enum is business-critical or differs by role/state.
- **Verification**: `validate_ia_skeleton.py` checks that every field in the
  prototype interaction ledger appears in the global dictionary or in an FRR
  §5 with coverage ≥ 90%.

Stage 3.5 Gate failures that must block Stage 5:
- A module has no view for a primary role that needs it.
- A cross-module flow has a source view but no target view.
- A view is described as "same as PC" without stating mobile-specific region
  differences when mobile is in scope.
- A rule-heavy module (alerts, SLAs, allocation, saturation) has no config view.

Stage 4 Stories + State Machine:
- Story format: As a [persona], I want [action], so that [value].
- AC format: Given / When / Then + Expected UI Result + Expected Domain Result.
- Every story includes happy, error, and boundary paths.
- Every state transition includes Trigger + Guard + Action.
- A story is not Stage-4 complete if it only states a visible UI result. It must also state the domain object change, domain event, audit record, task creation, notification, or measurable state change.

Stage 5 Prototype + PRD:

Authority order for L2/L3:

1. **IA Skeleton** (Stage 3.5): confirmed role × module × view × region × primary action.
2. **Prototype / Demo-Closed Artifact** (Stage 5a): pixel-level layout, component
   annotations (`data-testid`, `data-action`, `data-state`), modal chain, and
   interaction flow. The prototype is the primary truth for pages, fields, and
   visible behavior.
3. **PRD** (Stage 5b): business scenario, rules, state machines, permissions,
   exceptions, acceptance, and traceability. The PRD references the prototype
   and IA Skeleton; it does not re-invent layout or field lists.
4. **Engineering Traceability Contracts** (Stage 5c, optional): DDD/API/data
   contract, coding-agent AC-YAML, layered on top of the product specification.

Stage 5a Prototype First:

- Generate or review the HTML prototype **after** the IA Skeleton is locked.
- Use `references/prototype-testability.md` for annotation rules and state-driven
  behavior.
- Extract the interaction ledger with `scripts/extract_interaction_ledger.py`.
- Lock the prototype with a `[PROTOTYPE LOCK]` statement: list every page,
  modal, action, state enum, role flow, and any gap against the IA Skeleton.
- Do not start Stage 5b PRD detail until the prototype is locked or gaps are
  explicitly accepted.

Stage 5b PRD from Locked Prototype:

PRD chapters:
1. Problem statement
2. Users and personas
3. Core business concepts
4. Information architecture (derived from IA Skeleton; do not expand)
5. Feature modules
6. Business processes
7. State transitions
8. User interactions
9. Edge cases
10. Non-functional requirements

PRD writing rules to prevent bloat:

- **§4 Information Architecture** must be a thin mapping from the IA Skeleton:
  module → views → regions → entry paths. Do not add new views or regions here.
- **FRR §4 Pages/Visible States** must reference the locked prototype page/region
  IDs (`data-testid`) and modal chain. Describe only the business-visible
  differences (e.g., role-dependent region visibility), not the full layout.
- **FRR §5 Fields/Dictionaries** must reference the global field dictionary and
  the per-page field matrix from the prototype/annex. In the FRR, list only
  fields whose meaning, validation, or enum is business-critical or differs by
  role/state. Common fields are documented once in the global dictionary and
  referenced by name.
- **FRR §6 Numbered Interaction Flow** must trace actions through the prototype
  `data-action` IDs. Each step is: user action (`data-action=...`) → system
  response → domain state change. Do not rewrite component behavior that is
  already annotated in the prototype.
- **FRR §8 Business Rules / §9 State / §10 Permission / §11 Exception / §16
  Acceptance** remain fully specified in the PRD. These are the primary product
  decisions that the prototype cannot express.

The engineering layer does not replace the product layer. A module is not
development-ready when it only states purpose, inputs, outputs, aggregates, and
commands while omitting business rules, state transitions, permission rules,
exceptions, and acceptance. However, page layout and field inventory are owned
by the locked prototype and IA Skeleton, not by the FRR.

When the artifact will guide implementation, add a compact plan/task bridge
after the product specification is complete: implementation assumptions,
dependencies, vertical slice backlog, and readiness risks. This borrows the
useful discipline of spec-driven workflows without creating separate unsynced
documents. Tasks must point back to Function IDs and Acceptance IDs.

### Complete Module And Function Product Specification

Start each module with a function inventory. The inventory defines the denominator for completeness.

| Function ID | Function Name | User Outcome | Surface / Page | Release Scope | Detailed Record | Source IDs | Test IDs |
|---|---|---|---|---|---|---|---|
| M04-F01 | Query enterprises | find enterprises in the authorized scope | PC list | in | M04-F01 | SRC-... | TC-... |

Inventory rules:

- Include every user-visible command, query, configuration, review, import/export, batch operation, scheduled/system action, and material exception path planned for the release.
- Do not hide multiple independent functions under labels such as "management", "supports", "etc.", "related operations", or "complete lifecycle".
- Split functions when role, permission, trigger, aggregate/data owner, state transition, business result, audit/NFR, or acceptance path differs. Creating a ticket, accepting it, escalating it, closing it, confirming a contract, and registering payment are normally different release functions.
- Navigation, open/close modal, filter, pagination, tab switch, and confirmation helpers may map to an owning function only when they have no independent domain result. The mapping still must be explicit in the action ledger.
- `planned release functions = complete functional requirement records` is mandatory. Deferred/external functions remain in the inventory but do not enter the release denominator.
- A screenshot, prototype, workbook, SQL table, policy, or previous PRD is evidence. It does not become an implementable requirement until its behavior is mapped to a functional record or a frozen authoritative annex.

For each function in the release inventory, write a deterministic functional requirement record (FRR). The FRR is a **business-behavior contract**, not a layout or component specification. Layout and field inventory are owned by the locked IA Skeleton and prototype.

| Section | Required Content | Owner / Source |
|---|---|---|
| 1. Identity and value | function ID/name, module, priority, release, user value, source IDs | PRD |
| 2. Roles and scenario | initiating/collaborating roles, trigger, start condition, successful exit, next action | PRD |
| 3. Entry and preconditions | page/route/entry, role/data prerequisites, upstream state, feature/config flags | PRD; route references IA Skeleton view_id |
| 4. Pages and visible states | list/detail/create/edit/config/result, loading/empty/error/success/disabled behavior | **Prototype primary, PRD references**. In PRD: state the role-dependent visibility and any business-visible layout rule; point to prototype `data-testid` and modal chain. Do not rewrite component layout. |
| 5. Fields and dictionaries | every input/output field or authoritative annex range; meaning, type, required/default, enum, source, validation, editability, masking | **Global field dictionary + prototype primary, PRD references**. In PRD: list only fields whose meaning, validation, enum, or masking is business-critical or differs by role/state. Common fields are documented once in the global dictionary. |
| 6. Numbered interaction flow | user action and corresponding system response for each step | PRD, but each user action references prototype `data-action` ID. System response states domain result. Do not rewrite component behavior already in the prototype. |
| 7. Actions and results | action, confirmation, visible result, domain result, next action, idempotency/duplicate behavior | PRD |
| 8. Business rules and calibers | numbered rules, priority, formulas/thresholds, time boundary, conflict behavior, effective version | PRD (primary owner) |
| 9. State-button behavior | object state, visible/forbidden actions, guards, transitions, audit/event | PRD (primary owner) |
| 10. Permission and data scope | tenant/org/region/enterprise/row/field/action scope and override/approval policy. Include three-layer permission model when prototype has conditional rendering | PRD; map to prototype `data-visible-role` / `canViewXxx()` |
| 11. Exceptions and recovery | validation, empty, duplicate, stale/conflict, permission, timeout, dependency failure, partial success, retry/reopen/rollback | PRD |
| 12. Notifications, audit, and dependencies | recipient/dependency, channel/interface, trigger, contract, failure behavior, audit/owner | PRD |
| 13. Data / AI / algorithm contract | when applicable: input/output schema, deterministic vs model responsibility, confidence/threshold, human confirmation, prompt/model/rule version, fallback, evaluation and prohibited writes; otherwise `N/A + reason` | PRD / engineering annex |
| 14. Function-Level NFR | performance, security/privacy, accessibility, compatibility, operations; each with measurement/acceptance | PRD |
| 15. Frontend / Backend / QA handoff notes | frontend component behavior, backend validation/state/data ownership, QA focus and regression paths; point to FRR/state/prototype/acceptance IDs | PRD; references prototype annotations |
| 16. Acceptance | happy, validation, permission, state conflict, dependency failure, regression; expected UI and domain result. For coding-agent handoff (L2+), add an `ac_structured` YAML block immediately after prose acceptance; see `coding-agent-compat.md`. | PRD |

FRR section order remains authoritative:
1 Identity, 2 Roles/Scenario, 3 Entry/Preconditions, 4 Pages/Visible States,
5 Fields/Dictionaries/Validation, 6 Numbered Flow, 7 Actions/Rules,
8 Business Rules/Calibers, 9 State/Button/Lifecycle, 10 Permissions/Data Scope,
11 Exceptions/Recovery, 12 Notifications/Audit/Dependencies,
13 Data/AI/Algorithm, 14 Function-Level NFR,
15 Frontend/Backend/QA Handoff Notes, 16 Acceptance/Traceability.

Any section that truly does not apply must say `N/A` and why. Blank, omitted,
"同上", "见原型", or "按现有逻辑" does not count as complete.

**FRR bloat prevention rule**: if a fact is already in the IA Skeleton, the
locked prototype, or the global field dictionary, the FRR must reference it
rather than repeat it. Repetition is allowed only when the fact is modified by
role, state, or business rule in this specific function.

### Modal Chain Coverage Rule

When the source includes an HTML prototype or interactive mockup, the PRD must
achieve ≥ 90% modal coverage before marking Gate 3 as PASS.

Procedure:
1. Extract the complete modal inventory from the prototype: search for all
   `showModal`, `Modal.open`, `dialog`, `drawer`, `confirm`, and popup-like
   patterns. Record each as `{ modal_id, trigger_action, page_context }`.
2. In the PRD FRR §6 (Numbered Interaction Flow), every modal in the inventory
   must appear in at least one interaction step with its `modal_spec`
   (title, width/size, field list with required markers).
3. Compute coverage: `covered_modals / total_modals_in_prototype`.
4. If coverage < 90%, flag as `MODAL_COVERAGE_GAP` and list missing modals
   with their prototype location. Do not mark Gate 3 PASS until coverage
   reaches 90% or each missing modal has an explicit de-scope reason.

Entry-alias modals (same modal triggered from different navigation paths) may
be counted once if the alias relationships are documented.

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
tables, uses phrases such as "supports related operations", "see prototype",
"existing logic", "intelligent processing", or lacks business examples for
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

## Field-Level Permission

Permission in a delivery-ready PRD must cover three layers, not just
function-level (menu/button) visibility. When the prototype contains
`canViewXxx()`, `data-visible-role`, `isAgent` filters, or any field-level
conditional rendering, the PRD must describe the complete permission rule.

### Three-Layer Permission Model

| Layer | Scope | What It Controls | Example |
|---|---|---|---|
| Function-level | menu / button / page entry | whether a role can see or click | sales_rep cannot see "系统设置" menu; only admin can click "删除" |
| Row-level | data range: self / specified / department / all | which records a role can query or operate on | sales_rep sees only own leads; sales_manager sees department's leads; admin sees all |
| Field-level | field visibility: full / masked / hidden | what field values a role can view or edit | sales_rep cannot see customer phone (masked: 138****1234); only sales_manager can see full phone |

### Role × Entity × Permission_Level Matrix

| Role | Entity | Function-Level | Row-Level | Field-Level (Masked) | Field-Level (Hidden) | Override / Approval |
|---|---|---|---|---|---|---|
| sales_rep | Lead | create, read, submit, edit(draft) | self | customer.phone (masked: 138****5678) | lead.assignee (system-filled) | N/A |
| sales_manager | Lead | above + approve, reject, reassign | department | none masked | none hidden | can override row-level to self |
| admin | Lead | above + delete, export | all | none masked | none hidden | N/A |

Rules:

- When the prototype has `canViewXxx()` or `data-visible-role` on any element,
  the PRD must list every such function and its permission rule.
- When the prototype masks a field (e.g., phone shows `138****5678`), the PRD
  must state which roles see masked vs. full values.
- Row-level scope must use explicit enum values: `self`, `specified_person`,
  `department`, `department_and_below`, `all`. Do not use vague terms like
  "related data".
- Field-level permission must list every restricted field and its visibility
  rule per role: `full`, `masked` (with mask pattern), or `hidden`.
- If a role can override its default scope with approval, state the approval
  chain and audit requirement.

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
| Sponsor | PASS/NEEDS_REVISION + outcome, cost, control concerns | "The design looks comprehensive." | "No owner or SLA exists for overdue high-intent leads; business closure fails." |
| End User | task walkthrough + concrete pain points | "The DDD model is reasonable." | "I clicked Submit, saw only a toast, and could not find the created record." |
| Peer PM | scope/state gaps + complexity PASS/FAIL | "The requirements are complete." | "Returned state has no resubmit path; 2 actions are missing from the count." |
| Dev Lead | feasibility + undefined contracts/dependencies | "This should be feasible." | "The approve command lacks idempotency, expected version, and rejection event." |

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
