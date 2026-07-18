# Context, Composition And Agent Handoff

Use this reference when a task is unusually small, multi-module, regulated,
brownfield, or close to the model context limit.

## Two Different Budgets

Repository budgets keep the skill maintainable. Runtime budgets decide what a
specific task loads. Do not treat the 130-line SKILL ceiling or 500-line stage
reference ceiling as model token limits.

Generate a Context Plan before loading large domain packs or Product Truth.
Use `schemas/context-plan.schema.json` and `scripts/plan_context.py`.

## Classification Signals

Prefer structured evidence over keywords:

- requirement stage, mode, tier, and project shape;
- number of modules, roles, flows, actions, transitions, integrations, and P0 ACs;
- regulated sources and governance profiles;
- restricted fields, tenant isolation, money/safety/privacy consequences;
- AI writeback, historical compatibility, coexistence, compensation, and recovery;
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
   state transitions, failure behavior, acceptance, compatibility, or recovery.
3. Query Product Truth by stable ID or module with
   `scripts/query_product_truth.py`.
4. Treat reference/domain limits as batch limits. Record required deferred or
   unresolved packs and retrieve/split them; never drop them from scope.
5. If a complete safe slice still does not fit, split the delivery or return
   `BLOCKED` with the missing evidence.
6. Summaries are navigation aids. They do not replace authoritative source
   records or Product Truth objects.
7. At `warn_at_ratio` (recommended 70%), select an explicit action: retrieve an ID
   slice, write a compaction manifest, split the delivery, or block. A
   compaction manifest names preserved priorities and deferred IDs; it cannot
   silently discard behavior.
8. Do not generate a large Product Truth monolith. Write one
   `truth/fragments/MOD-*.yaml` file, checkpoint it, and compile only after the
   fragment passes. For complete AI Coding PRDs, apply the same section-slice
   pattern and assemble only after the contract index is closed.

## Fast Lane After Clarification

When source precedence, scope, and P0 decisions are already approved, do not
restart discovery or regenerate summaries. Freeze the contract index, load only
the current module/flow IDs, write its truth and PRD slices, validate locally,
checkpoint, and continue. This is the default route for large complete PRDs.

Project overrides belong in `spec.config.yaml`, validated against
`schemas/spec-config.schema.json`. Keep the config optional and versioned.

## Complexity Is Not Maturity

Context/assurance profiles describe this project. Domain maturity describes
the evidence behind a reusable domain pack. Automated classification may
select stronger gates; it must never promote a pack from knowledge-backed or
contract-tested to behavioral, expert-reviewed, or audited maturity.

## Checkpoint And Micro-Gate Protocol

Use checkpoints for long-running, resumed, regulated, audit-heavy or formal
acceptance work. They preserve requirement decisions when conversation context
does not survive; they do not manage sprints, code, releases or operations.

- Reload the latest verified checkpoint before each requirement stage.
- Use a Discovery Contract before specification exists.
- Edit the working contract and create a new snapshot; never edit a snapshot.
- Hash chains detect local change but do not replace accountable external
  signing when stronger evidence is required.

```powershell
py -3 scripts/manage_execution_state.py create --truth product-truth.yaml --config spec.config.yaml --installed-skill C:/path/to/ai-delivery-spec/SKILL.md --execution-id EXEC-PROJECT-001 --output evidence/state-000.yaml
py -3 scripts/manage_execution_state.py verify --state evidence/state-000.yaml
py -3 scripts/manage_execution_state.py gate --state evidence/state-000.yaml --gate-id contract_traceability --projection requirements/PRD.md --output gate-contract.yaml
```

Active gates cover version/environment, complexity/domain evidence,
context survival, discovery readiness, contract traceability, audit/access and
fallback risk. Advance exactly one requirement stage after required gates pass;
retain the prior checkpoint. After interruption, resume only from the latest
state whose hashes and anchors still verify.

High-risk failure is `BLOCKED`. A declared validator outage may become an
explicit human-reviewed gap only under configured low-risk policy; it is never
silent PASS. Missing links, stale gates, scope downgrade or version drift block
the affected baseline.

## Composition And Cross-Cutting Ownership

Compose the requirement kernel with only triggered capability/governance/domain
knowledge. Generic words such as “approval”, “AI”, “customer”, or “report” do
not select OA, AI-native, CRM, or data-product packs. When two packs share an
object, lifecycle, event, permission, rule, metric or failure path, record the
canonical owner, mapping, producer/consumer, precedence, retry/compensation and
reconciliation. A pack may narrow permissions but cannot expand the owning
business domain's authority.

## Smart Large-Project Rounds

Auto-round when inputs exceed 8 files or 500k parseable characters, or the
inventory finds at least 8 modules, 12 pages, or 200 stable objects. Round 0
creates the source/authority inventory; later rounds use end-to-end role slices,
normally at most 3 large sources, 2 modules and 40 major IDs. Preserve a durable
checkpoint after each round and finish with one cross-module gate. Do not split
by frontend/backend, regenerate a giant Product Truth in one pass, or present a
round checkpoint as final completion.

## Agent Handoff Projection

For long AI-coding work, generate only triggered packets against
`schemas/agent-handoff.schema.json`:

- root `AGENTS.md`: authority, stable global guards, routes, commands and change
  protocol; it references the PRD and never copies all business rules;
- `MOD-*`: one independently owned module slice with inputs/outputs, direct
  dependencies, AC and an embedded `qa_projection`;
- `XCT-*`: RBAC, tenancy, audit, lineage, AI runtime or another cross-cutting
  rule affecting at least two modules;
- `EDGE-*`: producer/consumer object or state handoff, mapping, retry,
  reconciliation and AC;
- `HANDOFF-*`: sender/receiver envelope recording acknowledged baseline and
  returned questions/proposals.

Every active packet binds the same requirement baseline version/hash, owner,
scope and AC. `ready_for_implementation` also requires an
`engineering_baseline_ref` maintained by engineering. A module Agent loads the
root summary, one module packet, direct XCT/EDGE dependencies and tests—not the
entire project. It may return `REV-*` or a change proposal but cannot mutate the
business baseline directly. Tool-specific Qoder/Claude/Cursor/Codex rules are
projections of this control plane and cannot duplicate divergent business IDs.
