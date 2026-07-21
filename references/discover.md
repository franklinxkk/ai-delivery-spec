# Discover And Clarify

Use this reference when the input is ambiguous, idea-only, a customer request,
a meeting note, an old system, a prototype, or a domain without a dedicated
pack. First complete requirement intake. Stop when outcome, scope, evidence,
authority and P0 unknowns are explicit enough for the selected requirement
artifact.

## Contents

- Evidence before questions
- Risk-adaptive clarification
- One-sentence and competitive discovery tracks
- Brownfield triangulation
- ToB / ToG context
- Project Domain Capsule
- Discovery completion

## Evidence Before Questions

Inventory supplied artifacts before asking what they already answer. Register
each source with `SRC-*`, binding type (`binding`, `supporting`, `contextual`,
`historical`, `untrusted`), status, scope, interpretation owner and location.
If more than one source claims canonical authority for the same scope, stop and
record `DEC-CONFLICT-*`; never select by filename, timestamp or apparent detail.

Extract when present:

- roles, organizations, tenants, partners, customers, and data scopes;
- business objects, fields, dictionaries, states, actions, and events;
- pages, regions, modals, handlers, reports, imports, exports, and integrations;
- contract, policy, standard, acceptance, migration, and operational evidence;
- contradictions, stale claims, silent omissions, and unresolved decisions.

Assertion status is independent of source disposition:

```text
verified | inferred | proposed | unknown | conflict
```

Do not ask the user to repeat facts already visible in a supplied source.

## Risk-Adaptive Clarification

Ask dependent questions in order. Batch independent questions by outcome,
role/permission, flow/state, data/integration and acceptance so the user does
not endure unnecessary one-by-one interrogation. A context dump or best-guess
mode may batch assumptions when the user explicitly prefers speed. Question
depth follows risk, not a fixed questionnaire.

| Signal | Mandatory Clarification |
|---|---|
| raw idea | target role, painful moment, desired outcome, current workaround |
| proposed feature | underlying problem, success measure, simpler alternative, must-not-do |
| multiple roles/modules | ownership, cross-module flow, state owner, exception owner |
| money/safety/medical/compliance | accountable human, authority source, prohibited automation, rollback |
| existing prototype/system | preserve, change, remove, migration, acceptance baseline |
| external data/integration | authoritative source, freshness, failure, reconciliation, data owner |
| AI write/read | context permission, freshness, write scope, eval, fallback, human gate |

Record material questions:

The current decision contract treats these fields as durable evidence, not optional prose:

```yaml
unknown:
  id: UNK-001
  question:
  priority: P0 | P1 | P2
  impact: scope | role | state | data | compliance | acceptance | commercial | risk
  question_kind: fact | direction
  owner:
  affected_refs: []
  blocks_stage: clarify | specify | review | baseline | implementation | acceptance
  recommendation:
  recommendation_evidence_refs: []
  tradeoff:
  reversal_path:
  due_date:
  status: open | answered | blocked | accepted_risk
  evidence_refs: []
```

P0 unknowns change scope, legality, safety, data authority, commercial promise,
or acceptance. Do not silently default them.

### One-Sentence Requirement Track

Do not expand a slogan directly into features. Progress one dependency layer at
a time, batching only questions whose answers do not depend on one another:

1. evidence, target role, painful moment, current workaround and desired outcome;
2. candidate solution options, smallest proof and explicit must-not-do;
3. role ownership, main/denied/recovery journeys and cross-role handoffs;
4. state, data authority, integration, migration, compliance and acceptance;
5. page/field/action detail only after the product decision is stable.

By the third batch, offer two or three materially different options with tradeoffs
instead of forcing the requester to invent the solution alone. Default clarification
caps are three batches for L1, six for L2 and eight for L3/L4. At the cap, return
the unresolved `UNK-*`; never manufacture closure or continue an unbounded loop.

After every answer batch, bind each answer to its original `UNK-*` and create or
update the affected `DEC/REQ/RULE/AC` entries. Every turn records the Agent
recommendation, recommendation evidence, trade-off, affected IDs and answer
evidence. Direction turns are serial: a later direction turn carries `branch_ref`
to the previous direction turn. Report confirmed facts, remaining unknowns and
the consequence of leaving them open. A numbered answer without question-to-ID
binding is not durable requirement evidence.

For a ToC behavior-change idea, explicitly test target behavior, trigger moment,
failure/recovery, safety/privacy, anti-manipulation boundary, pilot evidence and
stop condition. Do not import enterprise governance that the risk does not require.

### Competitive Evidence And Differentiation Track

Treat competitor material as evidence, not a backlog:

1. register the exact page, version/date and observed behavior as `SRC-*`;
2. separate fact, inference, reusable pattern, hypothesis and prohibited copying;
3. compare user outcome, workflow cost, switching constraint, trust/risk and
   business fit—not feature count alone;
4. produce two or three positioning/solution options and a smallest proof;
5. freeze the chosen positioning as an accountable `DEC-*` before user stories,
   information architecture, page contracts or prototypes;
6. trace every claimed differentiator to evidence, a deliberate decision and a
   measurable acceptance/experiment; remove ornamental differentiation.

Official whitepapers, cases, SDKs and open-platform samples can validate the
behavior they actually document. They do not prove a vendor's full implementation,
market result, legal applicability or that the core product is open source.

## Brownfield Triangulation

For an existing product, triangulate three evidence classes before declaring a
current baseline:

- written requirements and accepted change records;
- observable prototype/system behavior and data;
- live clarification used by engineers, QA or operators.

Historical buildability is useful evidence but is not current-contract conformity.
Convert verbal clarifications into `SRC/DEC/REV`, preserve a mapping from legacy
actions/states/terms to stable IDs, and record contradictions instead of picking the
most convenient artifact. A feature implemented only because an engineer asked the
requester in person is a missing requirement contract, not proof that no contract is
needed. Conversely, a legacy artifact that lacks new IDs must not be dismissed when
its behavior is richer than a newly generated projection.

Before any overwrite, create a Stage 0 inventory with one record for every view,
action/handler, state, role, object, field/metric and external handoff. Each record
must include `id`, `type`, `source_ref`, `source_location` and `classification`:
`confirmed`, `inferred`, `unknown` or `defect_candidate`. A core unknown includes
owned P0 `UNK-*` and `blocks_stage`; a defect candidate cannot become target scope
without `DEC/CHG`. Multiple candidate baselines require `DEC-CONFLICT-*`.

When a forward PRD baseline already exists, reverse-engineered observations use
`INV-*`, never a second set of `REQ-*`. Declare `baseline_requirement_refs`; each
confirmed/inferred observation records `mapping_status` and exact `target_refs`.
An unmapped core behavior becomes an owned `UNK-*`, not an invented requirement.
Group inferred observations into `RBATCH-*` with `owner`; batch-confirm, reject or
convert them before `target_status: baseline_ready`. This makes reverse output an
auditable interaction draft and gap ledger, not a competing baseline.

`inventory_complete` means every observed item has a source and classification;
it does not approve inferred behavior or prove the target design. Validate it with:

```bash
python scripts/ai_delivery_spec_cli.py gate --profile stage0 --inventory stage0.yaml
```

## ToB / ToG Context

For enterprise or public-sector requirements, record the external business,
customer, engineering and governance context only where it constrains scope,
authority, acceptance or evidence. Do not manage those lifecycles here.

For ToG or state-owned delivery, capture project establishment, procurement,
contract, trial operation, formal acceptance and audit as sources, constraints,
approvals or acceptance milestones when applicable.

Minimum enterprise context:

- buyer, sponsor, end user, payer, acceptance owner, operations owner;
- organization, department, tenant, partner/agent/integrator hierarchy;
- contract scope, pilot success, requirement baseline, acceptance evidence;
- legacy system, data migration, training/SLA constraints and exit obligations;
- jurisdiction, regulation, security, privacy, records, and audit boundary.

## Project Domain Capsule

Missing a dedicated domain pack never blocks delivery. Build a project-scoped
capsule from evidence and accountable decisions:

```yaml
project_domain_capsule:
  vocabulary: []
  entities: []
  state_machines: []
  workflows: []
  policies: []
  source_register: []
  unknowns: []
  scenario_fixtures: []
```

Use generic questions to discover object, owner, lifecycle, workflow, data,
high-risk behavior, and acceptance. Mark unsupported professional conclusions
`inferred` or `unknown`. A project capsule becomes a public domain pack only
after multi-project reuse, sourced knowledge, behavioral evaluation, and
accountable expert review.

## Clarification Completion

Return one decision:

| Decision | Meaning |
|---|---|
| `READY_FOR_LIGHT_SPEC` | accepted bounded requirement; enough for a requirement card |
| `READY_FOR_PRODUCT_TRUTH` | compatibility name for `governed_truth`: controlled projections, repeated cross-module change, lineage or strong audit justify independent truth |
| `READY_FOR_UNIFIED_PRD` | accepted requirement; enough for the unified PRD baseline |
| `READY_FOR_CHANGE_PACKAGE` | an existing baseline and requested change are understood |
| `REVIEW_COMPLETE_WITH_GAPS` | useful output is possible but named unknowns remain |
| `BLOCKED_BY_P0_UNKNOWN` | proceeding would invent a material business or risk decision |

Clarification is complete only when the intake decision, outcome, users, scope,
evidence, authority, risk, next artifact and decision owners are explicit.

## Schema-Driven Targeted Clarification

When material unknowns remain after evidence inventory, choose the
highest-impact open `UNK-*` and ask the smallest question that can close or
split it. Typical targets are outcome, scope, role authority, state boundary,
data authority, compliance, commercial promise and acceptance. Cite the source
or conflict that made the question necessary; do not send a generic checklist.

After each answer, record a
`schemas/clarification-transcript.schema.json` turn with `turn_id`,
`unknown_id`, question, answer, decision owner, status, question kind,
recommendation, recommendation evidence, trade-off, affected IDs and evidence
references. Direction turns also cite the previous direction turn with
`branch_ref`. Compile only structured, owner-attributed answers. Free-form chat
remains source evidence; a deterministic compiler does not pretend to understand
it.

Stop when every P0/P1 item is answered/accepted by an accountable owner, or is
an owned, scoped `UNK-*` with `blocks_stage` and a reversal path. An open P0/P1
that blocks `clarify` or `specify` cannot produce a ready decision; a later-stage
unknown may be returned as `REVIEW_COMPLETE_WITH_GAPS`. At the configured
stage-turn limit, return the unresolved IDs instead of continuing a propose/reject loop.

```bash
python scripts/compile_clarification_transcript.py --contract discovery.yaml --transcript transcript.yaml --decision READY_FOR_PRODUCT_TRUTH --output discovery-next.yaml
```
