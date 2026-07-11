## Outcome

What reusable behavior becomes better, and for whom?

## Type

- [ ] Runtime/routing
- [ ] Product Truth / Schema
- [ ] Projection/template
- [ ] Domain/capability/profile
- [ ] Validator/evaluation
- [ ] Migration/compatibility
- [ ] Example/documentation

## Truth And Compatibility Impact

- Affected stable IDs / schemas:
- Migration or replacement behavior:
- Context Plan / Truth slicing impact:
- Removed superseded material:

## Evidence And Claims

- Structural checks:
- Behavioral evidence:
- Quantitative run and matched baseline, or why not yet run:
- Expert/project evidence:
- Claims intentionally still marked `not_run` / `experimental`:

## Checklist

- [ ] Default runtime remains within context/line budgets.
- [ ] P0/compliance behavior cannot be silently truncated by config or retrieval.
- [ ] No duplicate independent truth or template copy was introduced.
- [ ] Project complexity and domain maturity remain separate.
- [ ] Domain maturity is supported by evidence.
- [ ] Customer/private/protected data is absent.
- [ ] Golden examples/eval catalog are updated where relevant.
- [ ] README, agent metadata, version, and CHANGELOG agree.
- [ ] `py -3 scripts/ai_delivery_spec_cli.py check` passes.
- [ ] The protected branch requires the `required-gate` status before merge.
