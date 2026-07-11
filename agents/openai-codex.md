# Codex Coding-Agent Entry - v5

Use after the user explicitly requests implementation from an AI Delivery Spec
package. Read `SKILL.md`, then `references/handoff.md` and the package Product
Truth. Load change/prototype/domain references only when triggered.
For large or regulated packages, read `delivery/evidence/context-plan.yaml` or
generate one and query a stable-ID working slice instead of loading all truth.

## Source Order

1. `delivery/truth/product-truth.yaml`;
2. approved `delivery/changes/CHG-*.yaml`;
3. locked prototype/IA for visible structure and behavior;
4. acceptance and evidence requirements;
5. repository reality for implementation constraints.

Repository reality cannot silently change product behavior. Report a `CFL-*`
or propose a `CHG-*` when sources disagree.

## Implementation Rules

- Implement vertical slices tied to `MOD/FLOW/VIEW/ACT/STATE/AC` IDs.
- Do not invent roles, pages, fields, states, permissions, rules, or events.
- Enforce state, tenant, permission, money, and high-risk guards on the backend.
- Preserve stable IDs in prototype attributes and tests.
- Generate tests/evidence for P0/P1 ACs before claiming a slice complete.
- Record repository paths and technical decisions as implementation facts, not
  additions to product scope.
- Write conflicts, test results, and evidence back to declared package paths.

Validate Product Truth first:

```powershell
py -3 scripts/validate_product_truth.py delivery/truth/product-truth.yaml
py -3 scripts/ai_delivery_spec_cli.py plan-context --truth delivery/truth/product-truth.yaml --config delivery/spec.config.yaml
py -3 scripts/ai_delivery_spec_cli.py query-truth --truth delivery/truth/product-truth.yaml --id MOD-SLICE --output working-slice.yaml
```

Then run repository syntax, unit, integration, E2E, migration, accessibility,
and security checks applicable to the slice. Report passed, failed, blocked,
and not-run separately.
