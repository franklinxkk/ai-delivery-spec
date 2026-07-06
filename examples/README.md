# Examples

These examples show how AI Delivery Spec can be used by product managers,
engineering leads, QA teams, and AI coding agents.

Each example includes:

- a realistic input prompt;
- the expected routing decision;
- the artifacts to produce;
- the gates that should be triggered;
- the review focus for product, engineering, and QA.

## Available Examples

| Example | Best For | Domain Module |
|---|---|---|
| [CRM End-to-End Delivery Package](crm-end-to-end-package/README.md) | full path from Stage 0 to IA, prototype, PRD, AC-YAML, manifest, and validation | `domain-crm.md` |
| [CRM Response Center](crm-response-center/README.md) + [L1 PRD sample](crm-response-center/l1-prd-sample.md) | sales, customer service, product feedback loop | `domain-crm.md` |
| [OA Collaborative Office](oa-collaborative-office/README.md) + [L1 PRD sample](oa-collaborative-office/l1-prd-sample.md) | workflow approval, official document, meeting, todo, AI office assistant | `domain-oa.md` |
| [Multi-Domain Package](multi-domain-package/README.md) | CRM x OA x Data Mart composition, cross-module flow, E2E canvas | `domain-crm.md` + `domain-oa.md` + `domain-data-mart.md` |
| [Traffic Safety SaaS](traffic-safety-saas/README.md) + [L1 PRD sample](traffic-safety-saas/l1-prd-sample.md) | regulated ToB/ToG SaaS, mobile field work | `domain-traffic.md` |
| [Higher-Education IT](education-it/README.md) + [L1 PRD sample](education-it/l1-prd-sample.md) | academic affairs, student affairs, teaching systems | `domain-education-it.md` |
| [Medical / Hospital IT](medical-hospital-it/README.md) + [L1 PRD sample](medical-hospital-it/l1-prd-sample.md) | clinical workflow, medical quality, AI-assisted review | `domain-medical-hospital-it.md` |

## How To Use

Copy one prompt into your AI tool and point it to this repository:

```text
Use AI Delivery Spec from this repository.
Run 0D triage first.
Load only the references needed by the scenario.
Produce the requested artifact and end with gate results, verification, gaps,
and completion state.
```
