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
| [CRM Response Center](crm-response-center/README.md) | sales, customer service, product feedback loop | `domain-crm.md` |
| [Traffic Safety SaaS](traffic-safety-saas/README.md) + [L1 PRD sample](traffic-safety-saas/l1-prd-sample.md) | regulated ToB/ToG SaaS, mobile field work | `domain-traffic.md` |
| [Higher-Education IT](education-it/README.md) | academic affairs, student affairs, teaching systems | `domain-education-it.md` |
| [Medical / Hospital IT](medical-hospital-it/README.md) | clinical workflow, medical quality, AI-assisted review | `domain-medical-hospital-it.md` |

## How To Use

Copy one prompt into your AI tool and point it to this repository:

```text
Use AI Delivery Spec from this repository.
Run 0D triage first.
Load only the references needed by the scenario.
Produce the requested artifact and end with gate results, verification, gaps,
and completion state.
```
