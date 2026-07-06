# CRM End-to-End Delivery Package

This example is the smallest complete delivery package for a CRM response
center feature. It shows the path from Stage 0 evidence to IA Skeleton,
prototype, Human-First PRD, AC-YAML, manifest, and validation evidence.

## Example Prompt

```text
Use AI Delivery Spec.
Turn a rough CRM response-center idea into a small development-ready delivery
package. Scope only lead intake, first response task creation, and conversion to
opportunity. Produce Stage 0 evidence, IA Skeleton, HTML prototype, PRD,
AC-YAML, manifest, and validation commands.
```

## Package Contents

| Artifact | Path | Purpose |
|---|---|---|
| Stage 0 evidence | `delivery/stage0-output.json` | source inventory, roles, entities, gaps |
| IA Skeleton | `delivery/ia-skeleton.yaml` | module/view/region/action structure |
| Prototype | `delivery/prototype/app.html` | testable HTML with data-* anchors |
| PRD | `delivery/prd/main.md` | Human-First PRD with inline FRRs |
| Acceptance | `delivery/acceptance/ac-structured.yaml` | machine-readable acceptance |
| Manifest | `delivery/manifest.json` | authoritative artifact inventory |
| Evidence | `delivery/evidence/validation-log.txt` | commands expected to pass |

## Validation

```powershell
py -3 scripts/validate_prd_quality.py examples/crm-end-to-end-package/delivery/prd/main.md --manifest examples/crm-end-to-end-package/delivery/manifest.json
py -3 scripts/validate_ia_skeleton.py --ia-skeleton examples/crm-end-to-end-package/delivery/ia-skeleton.yaml --prototype examples/crm-end-to-end-package/delivery/prototype/app.html --prd examples/crm-end-to-end-package/delivery/prd/main.md
py -3 scripts/validate_coding_agent_contract.py --prd examples/crm-end-to-end-package/delivery/prd/main.md --prototype examples/crm-end-to-end-package/delivery/prototype/app.html
```

Completion state: PASS for the bounded example scope.
