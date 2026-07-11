# Specify Product Truth

Use this reference to turn approved discovery evidence into one canonical
Product Truth that can be projected for humans, prototypes, coding agents, QA,
customers, and operations.

## Source Model

`schemas/product-truth.schema.json` is the machine contract. Product Truth is
the shared factual layer; Markdown PRDs and coding specifications are views.

Required identity graph:

```text
SRC -> FEAT -> MOD -> FLOW -> VIEW -> ACT
                                  |       |
                                  FLD     RULE
                                           |
ENTITY -> STATE <- transition <- EVENT     AC -> EVD
```

Stable prefixes:

| Object | Prefix |
|---|---|
| source / assertion / decision / unknown / conflict | `SRC` / `AST` / `DEC` / `UNK` / `CFL` |
| feature / role / module / entity / field | `FEAT` / `ROLE` / `MOD` / `ENT` / `FLD` |
| flow / view / region / action | `FLOW` / `VIEW` / `REG` / `ACT` |
| state machine / rule / event / integration | `STM` / `RULE` / `EVT` / `INT` |
| acceptance / evidence / change | `AC` / `EVD` / `CHG` |

IDs are permanent. Rename without changing semantic identity. For split,
merge, deprecation, or removal, preserve history in a Change Package with
`deprecated_ids` and `replacement_map`.

Each approved `FEAT-*` is a scope index, not a second requirements document.
Bind it to source, module/flow/view/action behavior, acceptance, owner, priority,
scope status, and version. Every released behavior and AC belongs to a Feature;
deferred, unknown, not-applicable, and out-of-scope items remain explicit.

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

Avoid a second chapter-oriented truth. A Human-First projection may organize
the same IDs for readability, but it cannot invent behavior absent from Product
Truth.

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

## Completion Gate

Product Truth is not complete when:

- a primary role cannot finish its task;
- an action lacks visible or domain result;
- a state transition has no owner/guard/event;
- a cross-module handoff lacks failure and reconciliation;
- a field lacks source/meaning/editability;
- a P0 assertion is inferred without owner review;
- a released module, flow, view, action, or AC has no Feature binding;
- an acceptance path cannot produce the required evidence.
