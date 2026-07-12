# Project Product Truth Into Delivery Views

Use this reference after Product Truth is complete enough for the selected
consumer. Generate views; do not author independent specifications.

## Projection Rules

Every projection records `generated_from: product_truth`, generation time, and
the in-scope `FEAT-*` plus stable behavior/acceptance IDs it covers. A projection may improve navigation and explanation,
but cannot change scope, rules, states, permissions, or acceptance.

| Projection | Consumer | Emphasis |
|---|---|---|
| Human-First | PM, customer, sponsor, frontend/backend/QA/vendor | scenarios, module slices, page/action effects, rules, exceptions, acceptance |
| Prototype | user, PM, customer, QA | visible states, interactions, representative data, role paths |
| Coding Agent | Codex, Claude Code, Cursor, Copilot, implementation team | source order, repository baseline, contracts, tasks, tests, forbidden inventions |
| QA / Acceptance | QA, UAT, customer acceptor | preconditions, steps, visible/domain result, evidence |
| Customer Contract | sales, delivery, customer | scope, responsibilities, deliverables, exclusions, acceptance, change control |

## Human-First Projection

Organize by module and end-to-end flow. For each module show:

1. outcome and role journey;
2. page map with fields and visible states;
3. numbered interaction flow;
4. action/result matrix;
5. rules, lifecycle, permissions, exceptions;
6. cross-module/data flow;
7. acceptance and open decisions.

Embed or link annotated prototype views by `VIEW/REG/ACT` IDs so readers do not
switch blindly between prose and prototype. Keep WBS, bug logs, and daily
tracking outside the PRD projection.

## Prototype Projection

Use `references/runtime/prototype-testability.md`. The prototype must preserve IDs:

```text
data-testid <- VIEW/REG/AC
data-action <- ACT
data-field  <- FLD
data-state  <- STATE
data-api    <- Action command/API when known
```

Every primary action produces a visible and domain result. Browser tests use
isolated mock/shadow data unless the user explicitly authorizes a safe test
environment.

## Coding-Agent Projection

Generate only when implementation is requested. If the user asks for a
complete/final AI Coding PRD or direct system generation, first read
`references/runtime/ai-coding-completeness.md` and use the complete template;
the shorter projection below is not an acceptable substitute. Include:

- source-of-truth order and manifest;
- greenfield or brownfield repository baseline;
- module/flow/view/action/state/event/field/AC maps;
- API/event/data contracts only at known implementation boundaries;
- vertical slices tied to visible/domain results and AC IDs;
- explicit unknowns and forbidden invention;
- validation commands and evidence writeback path.

The coding agent must report conflicts between Product Truth and repository
reality as `CFL-*` or `CHG-*`; it must not silently rewrite business behavior.

## QA Projection

Generate happy, validation, permission, state-conflict, duplicate, timeout,
integration-failure, migration, accessibility, and security paths as applicable.
Bind every test to `AC-*` and evidence type. A document assertion is not test
evidence.

## Delivery Package

```text
delivery/
  truth/index.yaml
  truth/fragments/*.yaml
  truth/compiled/product-truth.yaml
  projections/human-first-prd.md
  projections/coding-agent-spec.md
  prototype/
  acceptance/
  changes/
  agents/
  evidence/
  manifest.json
```

Small bounded projects may retain `truth/product-truth.yaml`. Large-project
authoring uses the index/fragments as the resumable source and treats the
compiled document as read-only output.

Only include directories required by scope. Manifest entries record path,
version, hash when available, authority, and lifecycle status.
