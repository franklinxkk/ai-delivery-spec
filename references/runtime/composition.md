# Capability, Governance, And Domain Composition

Use this reference after discovery identifies reusable cross-cutting needs,
governance overlays, or dedicated domain knowledge.

## Four Layers

```text
Requirement management kernel
  + Capability packs
  + Governance / project profiles
  + Domain pack or Project Domain Capsule
```

Do not treat all four as equivalent domains.

## Capability Packs

Capability packs are reusable across at least three projects and two domains.
Load only when triggered:

| Pack | Trigger |
|---|---|
| identity/tenant | organization, tenant, department, agent, partner, data scope |
| workflow/audit | approval, task, escalation, long-running process, audit |
| content/resource | resource, version, publishing, rights, knowledge, archive |
| data/integration | import, API, event, data product, lineage, reconciliation |
| AI governance | model/agent behavior, knowledge context, tool call, AI writeback |
| resilience/security | migration constraint, SLA, DR, high-risk security or auditable recovery requirement |

A capability pack adds reusable contracts; it never owns a business-domain
state unless the Product Truth assigns ownership.

## Governance And Project Profiles

Profiles overlay delivery constraints:

| Profile | Adds |
|---|---|
| ToB | buyer/user/payer/acceptor split, contract, delivery, adoption, renewal, exit |
| ToG / public sector | establishment, budget, procurement, tender, trial, acceptance, performance, audit/archive |
| regulated | authority source, human accountability, immutable evidence, incident and rollback |
| greenfield | target architecture assumptions, initial data, launch baseline |
| brownfield | current-state ledger, parity, migration, coexistence, rollback, retirement |

Profiles do not introduce industry vocabulary. A project can compose education
domain + ToB + regulated + brownfield.

## Domain Pack Selection

Read `references/domain-coverage.yaml` before loading a domain file. Load a
pack only when its business objects and lifecycle match the request. Generic
terms such as “approval”, “AI”, “customer”, or “report” do not automatically
select OA, AI Native, CRM, or data-product domains.

If no pack matches, use the Project Domain Capsule in `discover.md`.

Maturity behavior:

| Maturity | Runtime Behavior |
|---|---|
| experimental | use as questions and candidate patterns; warn on unsupported claims |
| validated | reuse evaluated paths; still confirm customer/jurisdiction applicability |
| audited | reuse within audited scope; record deviations and source versions |

`practice_status` is orthogonal: `production_practiced` means the method has
been used in a shipped product, not that every reusable rule has passed the
behavioral and accountable-review evidence required for `validated` maturity.

Never convert a mocked scenario or simulated reviewer into expert/production
evidence.

## Composition Contract

When two or more packs participate, record:

| Item | Required Decision |
|---|---|
| shared object | canonical ID, owner, aliases, mapping |
| lifecycle | state owner and allowed external commands |
| event | producer, consumers, version, ordering, replay |
| permission | intersection of domain and governance restrictions |
| rule conflict | assertions, applicability, decision owner, resolution |
| metric | caliber owner, source, dimensions, historical behavior |
| failure | retry, compensation, reconciliation, support owner |

Project Domain Capsules also declare a lowercase `namespace`, namespaced
`RULE-{NAMESPACE}-*` IDs, a context dictionary, and policy `listens_to` /
`writes_to` slots. Before flattening capsules, run
`scripts/validators/validate_capsule_composition.py`; two namespaces cannot react to the
same input and write the same output slot without redesigning ownership.

An AI or data pack can narrow access but cannot expand permissions granted by
the owning business domain.
