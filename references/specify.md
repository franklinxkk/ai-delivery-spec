# Specify The Requirement Baseline

Use this reference to turn accepted and clarified requirements into one
baseline. The default authority is one unified PRD with an embedded stable-ID
index. Add independent Product Truth only for scale, repeated change, multiple
controlled exports or strong audit needs.

## Output Language And Reading Contract

The dominant language of the user's current request is the default document
language. An explicit language request overrides it. Headings, prose, table
headers, clarification questions and test narratives stay in that language;
stable IDs, code, API/field names and proper nouns remain unchanged. Source
titles may remain original, but their meaning is summarized in the document
language. Generate bilingual content only when explicitly requested. Declare
`document_language`, `language_source` and `bilingual` in frontmatter.

One PRD uses progressive disclosure: a 30-second summary and task reading map;
business context and journeys; self-contained vertical module slices; cross-cutting
contracts; then exact indexes/machine projections. Annexes point to the same IDs
instead of restating business meaning. A frontend engineer, backend engineer, QA
or Coding Agent should complete one module by reading its slice plus named indexes,
without assembling rules from unrelated chapters or asking for missing behavior.

## Requirement Card Escalation

A card is only for one reversible, role-local change. Keep common outcome, scope,
story, flow/recovery, rules/permissions, AC and unknowns, then activate only the
applicable facets: `ui`, `stateful`, `data_submission`, `integration`, `batch_io`,
or `high_risk`. Each activated facet must be fully specified or explicitly owned
as unknown; unused facets impose no token cost.

Escalate to one unified PRD for any cross-role handoff, cross-module/system edge,
material state machine, data reporting/submission or metric-caliber behavior,
batch import/export, approval/audit, external integration, money/privacy/regulation,
irreversible write, migration or version compatibility. A data-submission request
is L2 by default because source mapping, validation, submission state, retry,
idempotency, audit, freshness and reconciliation affect several roles. A trivial
local label/copy/display change can remain a card.

## Source Model

`REQ-*` is the scope and traceability authority. When Product Truth is used,
`schemas/product-truth.schema.json` is its machine contract; the unified PRD is
the human reading path and approved baseline projection.

Required identity graph:

```text
SRC -> REQ -> MOD/FLOW -> VIEW/REG -> ACT/FLD/RULE/STATE/API
          |                                      |
          +---------------------> AC -> TEST/ARUN -> EVD
          ^                                      |
          +---------------- CHG / DEFECT <--------+
```

Stable prefixes:

| Object | Prefix |
|---|---|
| source / assertion / decision / unknown / conflict | `SRC` / `AST` / `DEC` / `UNK` / `CFL` |
| requirement / feature / review | `REQ` / `FEAT` / `REV` |
| role / module / entity / field | `ROLE` / `MOD` / `ENT` / `FLD` |
| flow / view / region / action | `FLOW` / `VIEW` / `REG` / `ACT` |
| state machine / concrete state / rule / event / integration/API | `STM` / `STATE` / `RULE` / `EVT` / `INT` / `API` |
| acceptance / test / run / defect / evidence / change | `AC` / `TEST` / `ARUN` / `DEFECT` / `EVD` / `CHG` |

IDs are permanent. Rename without changing semantic identity. For split,
merge, deprecation, or removal, preserve history in a Change Package with
`deprecated_ids` and `replacement_map`.

Each baselined `REQ-*` binds source, outcome, behavior, acceptance, owner,
priority, stage and version. `FEAT-*` may remain as a compatibility or capability
grouping but cannot replace the requirement record. Deferred, rejected,
superseded, unknown, not-applicable and out-of-scope items remain explicit.

## Module Delivery Slice

Specify by a user/domain result, not by frontend/backend/database layers. Every
in-scope module needs:

1. outcome, roles, entry, and success exit;
2. core and exception flows;
3. pages/regions and data presentation;
4. fields, dictionaries, source, editability, and sensitivity;
5. actions, guards, visible effect, command/domain effect, failure effect;
6. state machine, rules, events, permissions, audit, and compensation;
7. integrations, freshness, idempotency, reconciliation, and dependency owner;
8. acceptance paths and required evidence.

Also record module-local metric caliber and data-quality behavior, plus owned
unknowns/review items. The slice must bind outcome, story, main/exception path,
UI/data, rules/permission, state/event/integration, metric, recovery and acceptance
in one reading neighborhood. Cross-cutting chapters define only truly shared
contracts; appendices are exact indexes, not a second narrative.

The unified PRD main body may organize the same IDs for readability. Its
engineering annexes and optional Product Truth cannot contradict or invent
behavior absent from the approved requirement baseline.

## Page Contract

Every implementation-relevant view defines:

- `VIEW-*`, owning module, surfaces, and visible roles;
- `REG-*` regions, repeated-record rules, fields, actions, and query source;
- default, empty, loading, error, no-permission, partial, and success states;
- modal/drawer chain, long-data behavior, responsive/print behavior when in scope;
- links to flows, actions, states, and acceptance.

A bare “see prototype” fails. A bare component inventory also fails.

## Action Contract

Every material `ACT-*` records:

- trigger and allowed role/state;
- guard/confirmation;
- frontend feedback and durable visible result;
- command/API when the implementation boundary is in scope;
- domain result, next state, event, audit, and idempotency;
- validation, permission, dependency, duplicate, timeout, and stale-write failure;
- acceptance references.

Toast-only completion fails for a state-changing core command.

## Flow Contract

Every `FLOW-*` identifies actors, modules, start condition, ordered steps,
visible and domain result per step, exception branch, compensation, final
evidence, and acceptance. Cross-module flows must name source/target object,
field mapping, state owner, producer/consumer, retry, and reconciliation.

## State, Permission, And Data

- The owning aggregate or system is the state authority.
- Backend guards business state; UI visibility is not authorization.
- Data scope is explicit by tenant, organization, department, owner, partner,
  record, field, purpose, and time where relevant.
- Money, safety, regulated decisions, sensitive export, and consequential AI
  writeback require accountable human ownership and audit.
- Data sources record ownership, freshness, quality, permission, retention,
  deletion/export, and failure behavior.

## NFR Profiles

Load only applicable profiles. Do not force arbitrary numbers.

| Profile | Minimum Concerns |
|---|---|
| standard enterprise | availability, performance, audit, backup, support |
| multi-tenant SaaS | isolation, quotas, export, tenant lifecycle, noisy neighbor |
| realtime | latency, ordering, reconnect, duplicate, clock, degraded mode |
| data product | freshness, lineage, quality, cost, backfill, semantic consistency |
| AI core | eval, safety, context, tool scope, fallback, rollback, observability |
| regulated/high risk | authority, human gate, immutable evidence, recovery, incident owner |

## Baseline Gate

The requirement baseline is not complete when:

- a primary role cannot finish its task;
- an action lacks visible or domain result;
- a state transition has no owner/guard/event;
- a cross-module handoff lacks failure and reconciliation;
- a field lacks source/meaning/editability;
- a P0 assertion is inferred without owner review;
- a released module, flow, view, action, field, rule, API or AC has no REQ binding;
- an acceptance path cannot produce the required evidence.

## AI-Coding Handoff Without A Second PRD

The unified PRD is both the human review path and the business implementation
contract. Machine-oriented tables and YAML are annexes/projections of the same
baseline, not independent authority. At L2+ the receiver must be able to derive:

- exact roles/data scope, flow branches and recovery;
- page regions, fields/controls/validation and visible states;
- action guards, domain result, state transition, event/audit and idempotency;
- business API/event inputs, outputs, errors, compatibility and reconciliation;
- positive/negative AC, fixtures/evidence and reverse trace;
- explicit forbidden-invention and open-decision lists.

Technical framework, database DDL, repository layout and deployment topology
remain engineering decisions unless interoperability, compliance or acceptance
makes them a business contract. A module can be implementation-ready while the
project lacks an engineering baseline only if the result is reported as a
handoff GAP, never as full development-readiness PASS.

High-risk `RULE-*` lines bind an authoritative `SRC-*`, approved `DEC-*`, or
explicit `ASSUMPTION-*` owner. AI behavior additionally declares input/output,
model/prompt/tool versions, human gate, fallback, evaluation and observability.
Data lineage behavior declares source, transformation, owner and change impact.
