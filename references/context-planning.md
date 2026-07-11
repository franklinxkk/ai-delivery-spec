# Adaptive Context Planning

Use this reference when a task is unusually small, multi-module, regulated,
brownfield, or close to the model context limit.

## Two Different Budgets

Repository budgets keep the skill maintainable. Runtime budgets decide what a
specific task loads. Do not treat the 350-line SKILL ceiling or 500-line stage
reference ceiling as model token limits.

Generate a Context Plan before loading large domain packs or Product Truth.
Use `schemas/context-plan.schema.json` and `scripts/plan_context.py`.

## Classification Signals

Prefer structured evidence over keywords:

- lifecycle, mode, tier, and project shape;
- number of modules, roles, flows, actions, transitions, integrations, and P0 ACs;
- regulated sources and governance profiles;
- restricted fields, tenant isolation, money/safety/privacy consequences;
- AI writeback, migration, coexistence, compensation, and rollback;
- open P0 unknowns or conflicts.

Keywords may suggest discovery questions. They cannot prove regulation,
select a domain pack by themselves, or change domain-pack maturity.

## Runtime Profiles

| Profile | Default behavior |
|---|---|
| minimal | core skill plus zero or one stage reference; no domain pack unless necessary |
| standard | one or two stage references and one matched pack |
| regulated | relevant stages, authority sources, one or more justified packs, Human Gate |
| large_program | split by module/flow/change package; retrieve slices instead of loading all truth |

The profile is an operating recommendation, not a license to expand the
model's context window.

## Overflow Rules

1. Reserve system and output tokens first.
2. Never silently truncate P0 rules, regulated assertions, permissions,
   state transitions, failure behavior, acceptance, migration, or rollback.
3. Query Product Truth by stable ID or module with
   `scripts/query_product_truth.py`.
4. Treat reference/domain limits as batch limits. Record required deferred or
   unresolved packs and retrieve/split them; never drop them from scope.
5. If a complete safe slice still does not fit, split the delivery or return
   `BLOCKED` with the missing evidence.
6. Summaries are navigation aids. They do not replace authoritative source
   records or Product Truth objects.
7. At `warn_at_ratio` (default 80%), select an explicit action: retrieve an ID
   slice, write a compaction manifest, split the delivery, or block. A
   compaction manifest names preserved priorities and deferred IDs; it cannot
   silently discard behavior.

Project overrides belong in `spec.config.yaml`, validated against
`schemas/spec-config.schema.json`. Keep the config optional and versioned.

## Complexity Is Not Maturity

Context/assurance profiles describe this project. Domain maturity describes
the evidence behind a reusable domain pack. Automated classification may
select stronger gates; it must never promote a pack from experimental to
validated or audited.
