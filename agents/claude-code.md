# Claude Code / Cursor Coding-Agent Entry - v5

Use for implementation only after Product Truth or an approved Change Package
exists. Read `SKILL.md` and `references/handoff.md`; do not load unrelated
domains or lifecycle stages.
Use the Context Plan and stable-ID Truth slices for large or regulated work;
never silently truncate P0 or compliance behavior to fit context.

## Source Order

```text
Product Truth -> approved Change Package -> locked prototype -> acceptance
-> repository constraints
```

If a required behavior is absent or conflicts with the repository, stop the
affected slice and report the stable IDs. Do not guess.

## Required Behavior

- Work in vertical user/domain-result slices.
- Preserve `VIEW/REG/ACT/FLD/STATE/AC` IDs in UI and tests.
- Enforce business invariants and permission on the backend.
- Treat AI behavior as governed only when Product Truth defines context,
  evaluation, write scope, human gate, fallback, observability, and rollback.
- Generate `CLAUDE.md`, `.cursor/rules/*.mdc`, or project instructions from the
  Product Truth source order; do not copy a second PRD.
- Bind every product test to AC and evidence IDs.

Validate before implementation:

```powershell
python scripts/validate_product_truth.py delivery/truth/product-truth.yaml
```

After implementation, run repository tests and write evidence to the package.
Passing text in a template is not execution evidence.
