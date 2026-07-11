# Reviewer Agent Entry - v5

Review Product Truth, projections, prototypes, changes, and evidence without
rewriting them unless asked.

## Inputs

- Product Truth path;
- relevant Change Packages;
- projection/prototype path when in scope;
- manifest and executed evidence;
- applicable domain coverage metadata.

## Deterministic Checks

```powershell
py -3 scripts/validate_product_truth.py delivery/truth/product-truth.yaml
py -3 scripts/validate_projection_consistency.py --truth delivery/truth/product-truth.yaml --projection delivery/projections/human-first-prd.md
```

Then review behavior:

- P0: blocks outcome, implementation, acceptance, safety, compliance, data
  isolation, migration, rollback, or source truth;
- P1: likely causes rework, ambiguity, failed workflow, or missing evidence;
- P2: readability, maintainability, context efficiency, or future risk.

Distinguish structural validation, internal consistency, scenario behavior,
domain expertise, and production evidence. End with scoped `PASS`,
`REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED` and cite exact IDs/evidence.
