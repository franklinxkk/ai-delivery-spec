# Contributing To AI Delivery Spec 5

Contributions must improve reusable delivery behavior without inflating the
default runtime or overstating validation.

## Before Opening A Change

Classify the proposal:

| Type | Belongs In |
|---|---|
| core routing or invariant used on nearly every task | `SKILL.md` |
| requirement-stage procedure | one focused top-level `references/*.md` file |
| machine contract | `schemas/` plus validation |
| reusable cross-domain concern | capability/profile catalog |
| professional industry knowledge | one matched `references/domains/domain-*.md` plus coverage metadata |
| customer-specific behavior | project Product Truth / Project Domain Capsule, not this repo |
| deterministic repeatable work | `scripts/` |
| behavioral validation | `maintainer/evals/` with evidence |

Do not add a public file for a one-off project rule.

## Runtime Budget

- Keep `SKILL.md` at or below 350 lines.
- Keep stage references at or below 500 lines.
- Do not duplicate a rule across SKILL, reference, template, and README.
- Load domain/profile/capability material only on explicit triggers.
- Prefer Schema and deterministic validation over long format instructions.
- Remove superseded runtime material in the same PR; Git history is the archive.

## Domain Pack Contribution

1. Start from `maintainer/templates/domain-module-template.md`.
2. Add an entry to `references/domain-coverage.yaml`.
3. State `applies_when` and `does_not_apply_when`.
4. Define vocabulary, entities, state owners, events, metrics, context sources,
   workflows, roles, UI patterns, permissions, risks, and scenarios.
5. Register sources with authority, status, jurisdiction/applicability, version,
   verification date, and owner where relevant.
6. Keep customer rules separate from public/industry rules.
7. Add evaluation scenarios to `maintainer/evals/eval-catalog.yaml`.
8. Declare actual reusable-pack maturity and delivery `practice_status`
   separately. New packs default to `experimental` + `knowledge_only`.

The following do not count as expert or production validation:

- the existence of a domain file;
- a generated checklist;
- a prefilled PASS matrix;
- a simulated reviewer;
- a single undocumented customer anecdote.

`production_practiced` may be recorded from accountable owner evidence, but it
does not promote pack maturity. `validated` requires sourced knowledge, project-sampled scenarios, passing
behavioral evidence, and accountable review. `audited` additionally requires
independent audit evidence.

## Privacy, Copyright, And Evidence

- Never submit secrets, credentials, personal data, private customer documents,
  or insufficiently anonymized screenshots/data.
- Do not copy protected standards or paid research in full. Store citation,
  applicability, version, and the minimal product implication.
- Generated or inferred professional claims must be marked as such.
- Evaluation evidence records executor, input, environment, time, result, and
  location. A document containing the word PASS is not execution evidence.

## Change And Compatibility

Breaking changes require:

- affected Schema/runtime version;
- stable ID and migration behavior;
- previous-version or brownfield migration test where applicable;
- updated golden example;
- README/agent metadata/CHANGELOG alignment;
- explicit removal of superseded runtime files.

## Validation

Run:

```powershell
py -3 scripts/ai_delivery_spec_cli.py check
```

For Product Truth changes:

```powershell
py -3 scripts/validators/validate_product_truth.py path/to/product-truth.yaml
```

For prototype extraction or compatibility work, run the applicable artifact
validator and record the command/result in the PR.

Repository maintainers should configure the protected default branch to
require the GitHub Actions status `required-gate`. The workflow aggregates the
Windows/Linux and Python matrix, blocks schema, context-plan, exact runtime-rule
duplication, maturity-evidence, migration, GitHub-case, and evaluation failures,
and verifies that validators do not modify tracked files. The workflow file
does not enforce merge protection until the repository ruleset marks this
status as required.

## PR Checklist

- [ ] Change has one clear reusable purpose.
- [ ] Runtime budget and progressive loading remain intact.
- [ ] Product Truth / Schema / projection semantics remain consistent.
- [ ] Stable IDs and migration impact are addressed.
- [ ] Domain maturity and evidence claims are honest.
- [ ] No private data, secrets, or protected full-text sources are included.
- [ ] Relevant golden examples and eval scenarios are updated.
- [ ] `ai_delivery_spec_cli.py check` passes.
- [ ] README, agents metadata, version, and CHANGELOG agree when public behavior changes.

By contributing, you agree that your contribution is licensed under Apache-2.0.
