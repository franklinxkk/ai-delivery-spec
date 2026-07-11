# Discover And Clarify

Use this reference when the input is ambiguous, idea-only, a customer request,
a meeting note, an old system, a prototype, or a domain without a dedicated
pack. Stop when the opportunity, delivery context, evidence, and P0 unknowns
are explicit enough for the selected artifact.

## Contents

- Evidence before questions
- Risk-adaptive clarification
- ToB / ToG context
- Project Domain Capsule
- Discovery completion

## Evidence Before Questions

Inventory supplied artifacts before asking what they already answer. Register
each source with `SRC-*`, authority, status, disposition, owner, and location.

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

Ask one focused question at a time in a guided conversation. A context dump or
best-guess mode may batch assumptions when the user explicitly prefers speed.
Question depth follows risk, not a fixed questionnaire.

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

```yaml
unknown:
  id: UNK-001
  question:
  impact: scope | role | state | data | compliance | acceptance | commercial | risk
  owner:
  due_date:
  status: open | answered | blocked | accepted_risk
```

P0 unknowns change scope, legality, safety, data authority, commercial promise,
or acceptance. Do not silently default them.

## ToB / ToG Context

For enterprise or public-sector delivery, identify the four lifecycles that
intersect the product:

```text
Product: discover -> validate -> define -> build -> pilot -> scale -> evolve -> retire
Customer: qualify -> discover -> solution -> pilot -> contract -> deliver -> accept -> adopt -> renew/exit
Engineering: specify -> plan -> tasks -> build -> verify -> release -> operate
Governance: propose -> review -> approve -> execute -> evidence -> close/supersede
```

For ToG or state-owned delivery, add project establishment, budget,
procurement/tender, contract, trial operation, formal acceptance, performance,
audit, and archive where applicable.

Minimum enterprise context:

- buyer, sponsor, end user, payer, acceptance owner, operations owner;
- organization, department, tenant, partner/agent/integrator hierarchy;
- contract scope, pilot success, delivery baseline, acceptance evidence;
- legacy system, data migration, rollout, training, SLA, renewal, and exit;
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

## Discovery Completion

Return one decision:

| Decision | Meaning |
|---|---|
| `READY_FOR_LIGHT_SPEC` | enough for opportunity/scope alignment |
| `READY_FOR_PRODUCT_TRUTH` | enough for development-oriented specification |
| `READY_FOR_CHANGE_PACKAGE` | an existing baseline and requested change are understood |
| `REVIEW_COMPLETE_WITH_GAPS` | useful output is possible but named unknowns remain |
| `BLOCKED_BY_P0_UNKNOWN` | proceeding would invent a material business or risk decision |

Discovery is complete only when the outcome, users, scope, evidence, risk,
next artifact, and decision owners are explicit.
