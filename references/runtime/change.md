# Change And Brownfield Delivery

Use this reference for requirement updates, locked prototype revisions,
existing products, migrations, policy updates, and post-launch iteration.

## Change Package

Use `schemas/change-package.schema.json`. A `CHG-*` records reason, source,
baseline, target, owner, affected IDs, compatibility, data migration,
regression, evidence, rollout, and rollback.

Never regenerate the entire PRD to hide a local change. Update Product Truth,
then regenerate affected projections.

## Impact Analysis

Traverse both directions:

```text
source/policy -> rule -> field/action/state/flow -> view/module -> AC/test/evidence
repository/test failure -> AC/action -> flow/rule -> source/decision
```

At minimum assess module, flow, view, action, field, state, event, integration,
acceptance, documentation, data migration, operations, and customer promise.

## Stable Identity

- Rename: keep ID.
- Behavior changes: keep ID and version through `CHG-*` when identity remains.
- Split: preserve valid old behavior; create new IDs and replacement map.
- Merge: keep still-valid IDs or deprecate with explicit replacements.
- Remove: deprecate first unless safety or law requires immediate removal.
- Acceptance history: never reuse an old AC ID for a different behavior.

## Brownfield Baseline

Before target design, inventory:

- current modules, views, actions, handlers, states, integrations, reports;
- real usage, customers, ARR/contract dependence, workarounds, support burden;
- data volumes, quality, ownership, retention, migration constraints;
- compatibility promises and behavior that must remain;
- keep, improve, replace, retire decisions and owners.

Define coexistence, migration batches, reconciliation, rollback, training,
customer communication, support, and retirement evidence. A new prototype fails
if it silently removes baseline behavior.

## Change Completion

A change is not verified until affected Product Truth IDs, projections,
acceptance, regression, migration, and operational evidence agree. Failed or
missing evidence leaves the change `implemented` or `partial`, not `verified`.
