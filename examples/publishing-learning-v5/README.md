# Publishing Authorization and Learning — v5 Golden Example

This example demonstrates the v5.1 requirement-management model on a multi-role
ToB education/content chain:

```text
resource -> knowledge point -> question -> course version
-> book/batch/code -> partner authorization -> learner activation
-> learning/assessment -> evidence/report -> renewal/revoke/migrate
```

It is a project-shaped evaluation fixture, not a production claim or an
authoritative education-domain standard.

## Artifacts

- `delivery/truth/product-truth.yaml`: optional large-project structured authority.
- `delivery/projections/unified-prd.md`: one customer/product/development/QA/Coding Agent PRD.
- `delivery/evidence/context-plan.yaml`: adaptive risk/context selection.
- `delivery/evidence/content-module-slice.yaml`: reference-closed working slice.
- `delivery/manifest.json`: authority and requirement-baseline metadata.

## Validation

```powershell
py -3 scripts/validators/validate_product_truth.py examples/publishing-learning-v5/delivery/truth/product-truth.yaml
py -3 scripts/validators/validate_unified_prd.py examples/publishing-learning-v5/delivery/projections/unified-prd.md
```

Schema/reference PASS proves structural closure only. Browser, domain-expert,
coding-agent, QA, and customer walkthrough evidence must be recorded separately
before the example can claim behavioral validation.

The Context Plan classifies this fixture as regulated because it is brownfield
and contains restricted learner identity data. The content slice contains 17
linked items. Neither derived artifact changes the education pack's
contract-tested maturity; project-specific applicability still requires accountable confirmation.
