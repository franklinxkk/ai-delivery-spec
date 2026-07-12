# Complete AI Coding PRD Route

Use this route when the user asks for a complete AI Coding PRD, direct system
generation, or a handoff usable by product, engineering, QA, and coding agents.
Do not substitute a thin Coding Agent summary.

## Why This Route Exists

A production-practiced publishing/learning project showed that a 12-section,
20 KB summary still forced engineering to invent contracts. The verified
revision grew only after adding repository baseline, concrete API request and
response schemas, error catalog, field dictionaries, machine-readable AC,
integration and event payloads, statistics/calculation rules, and slice file
dependencies. These are structural requirements, not optional prose.

## Fast, Complete Sequence

1. Inventory all sources and approved decisions once. Do not restart discovery
   after the user confirms scope.
2. Create a contract index listing all modules, roles, views, flows, entities,
   integrations, metrics, and P0 AC IDs before drafting prose.
3. For a large project, write one Product Truth fragment and one PRD section
   slice at a time. Checkpoint files; do not ask an agent or subagent to emit a
   monolithic YAML/PRD in one response.
4. Assemble the PRD using `references/templates/ai-coding-prd-template.md`.
5. Run the L2/L3 validator. Fix missing contracts; do not weaken the level to
   make an incomplete document pass.
6. Cross-check every approved role journey and P0 flow against IA/prototype,
   structured AC, likely files, dependencies, and observable failure behavior.

## Completeness Gate

For L2 and above, require:

- source precedence, scope, repository baseline, roles, permissions, and data
  scope;
- IA, page/region layout, stable anchors, actions, fields, states, and recovery;
- field dictionary and end-to-end data flow;
- concrete API request/response, errors, idempotency/concurrency;
- versioned event payloads, async retry/dead-letter/reconciliation, and
  integration mapping;
- NFR/security/privacy, metrics/calculation caliber, deployment/migration/
  rollback/operations;
- vertical slices with dependencies and likely files/modules;
- machine-readable AC with visible/domain results and evidence requirements;
- forbidden invention plus explicit `UNK/CFL` handling.

Use `Not applicable + reason + future trigger` for a genuinely irrelevant
contract surface. An empty heading or keyword is not coverage.

## Context Pressure

At medium pressure, stop loading sources and continue from the approved ID
inventory. At high pressure, checkpoint the current fragment/section and start
the next slice. Never shorten P0 behavior, merge distinct roles, or omit
exceptions merely to fit one context window.
