---
name: ai-delivery-spec
description: Manage requirements from intake through clarification, specification, baseline, change, traceability, and acceptance. Produce one human-readable, AI-coding-ready contract with stable IDs and executable acceptance for ToC/ToB/ToG PRDs, prototypes, brownfield change, and audit. Excludes delivery execution, CI/CD, operations, and unrelated code work.
---

# AI Delivery Spec 5.1.5 — Requirement Management Kernel

> First use: run requirement intake; use `mode=ultra_light` only for one reversible change.
>
> Default deliverable: one human-readable PRD shared by product, engineering, QA, and Coding Agents.
>
> Domain route: append `domain=traffic|crm|education-it|oa|medical-hospital-it|data-product|ai-native`.

Manage intake, clarification, specification, change, traceability, and
acceptance only. Planning, code, CI/CD, deployment, and operations are downstream.

## 1. Start with intake

Before formal design, report:

```text
Decision: accept|clarify|defer|reject
Priority: P0|P1|P2|P3
Value: high|medium|low + evidence
Complexity: S|M|L|XL + impacted dimensions
Uncertainty: low|medium|high + unresolved decisions
Mode/Tier: ultra_light|lite|standard|full + L0|L1|L2|L3|L4
Stage: intake|clarify|specify|review|baseline|change|acceptance|closed
Override: mode=<...>; tier=<...>; domain=generic|<pack>
```

- Do not invent cost or effort without engineering confirmation.
- Ultra-Light is only for one reversible change with one role and no cross-module
  state, sensitive data, regulation, acceptance, or migration.
- Multi-role, brownfield, regulated, complete-PRD, or acceptance work is L2+.
- Register iteration, dependencies, conflicts, and ordering for parallel needs.

Run `scripts/triage_requirement.py` or use `references/requirement-management.md`.
Do not finalize before intake and P0 clarification pass.

## 2. Load only the active slice

| Need | Read |
|---|---|
| intake, lifecycle, requirement pool | `references/requirement-management.md` |
| source/prototype/legacy inventory | `references/discover.md` |
| ambiguity and clarification | `references/runtime/schema-grill.md` |
| behavior and stable IDs | `references/specify.md` |
| unified PRD | `references/templates/unified-requirement-prd-template.md` |
| page contract + four-lens sign-off | `references/runtime/page-delivery-contract.md` + `references/runtime/four-lens-module-walkthrough.md` |
| machine annex | `references/runtime/ai-coding-completeness.md` |
| role/seniority handoff | `references/runtime/role-stage-playbook.md` |
| prototype | `references/runtime/prototype-testability.md` |
| change/acceptance | `references/runtime/change.md` / `references/runtime/verify.md` |
| large context | `references/runtime/context-planning.md` |
| domain work | `scripts/query_domain.py --domain <pack>`, then matching sections only |
| domain evidence or promotion | `references/runtime/domain-assurance.md` |
| common reusable pattern | matching entry in `references/patterns/common-requirement-patterns.yaml` |
| Skill/template/validator release | `references/runtime/assurance-lab.md` |

Load one stage reference, optionally one domain pack, and triggered governance.
Do not load the README, all examples/domains, or full repository at runtime.

## 3. Run the requirement loop

```text
Intake → Clarify → Specify → Review → Baseline → Change → Acceptance → Closed
```

1. **Intake** — create `REQ-*` against
   `schemas/requirement-register.schema.json`; record source, outcome, evidence,
   scope, owner, dependency, priority, complexity, version, and decision.
2. **Clarify** — close roles, trigger/result, flow, scope, state, rule,
   exception, integration, acceptance, and out-of-scope. Track open P0 as `REV-*`.
3. **Specify** — write one sequential PRD: readable business narrative first,
   field/state/API/event/trace/machine-AC annex second. Keep implementation choices
   out unless contractual. For implementation/prototypes, declare every view and
   give it a Page Delivery Contract; CRUD/import/export labels are insufficient.
4. **Review** — product, domain, UX, engineering, QA, compliance, and customer
   lenses check outputs. For L3/L4 multi-page work, run every view through the
   four-lens walkthrough and fix the one PRD/prototype, not a parallel spec.
5. **Baseline** — freeze version, IDs, source precedence, approvals, open-item
   dispositions, prototype binding, and consumer synchronization.
6. **Change** — create `CHG-*` under
   `schemas/change-package.schema.json`; traverse requirement, role, flow,
   view/action/field, state/rule, API/event, acceptance/test/evidence, and
   history in both directions; approve, synchronize, regress, and re-baseline.
7. **Acceptance** — record actual result, evidence, defect/change reverse links,
   conditions, and sign-off for every `AC-*`.

Use `Product Truth` only for 12+ views/modules, repeated material change,
governed projections, long audit, or explicit choice. Otherwise keep the
register, one PRD, change/trace, and acceptance. Large truth uses fragments/ID
slices, never one giant YAML pass.

## 4. Preserve one implementation contract

- Stable IDs cover `REQ/ROLE/FLOW/VIEW/REG/ACT/FLD/STATE/RULE/API/EVT/INT/AC/TEST/DEF/EV/CHG/REV`.
- Every important role reaches an authorized exit, denial, recovery, or explicit
  handoff; no journey ends at an unexplained button or notification.
- Every action has precondition, authority, input, state/result, failure,
  audit/event, and acceptance linkage.
- Every P0 requirement has positive and negative acceptance, observable result,
  test data/evidence, and reverse trace.
- A prototype must preserve declared views/actions/states and use stable
  `data-testid`, `data-action`, `data-state`, and `data-field`; every action has a
  visible outcome and no unexplained handler.
- Every displayed metric defines population, formula, time/status/filter/dedup
  caliber, source, freshness, zero denominator and format beside its view.
- Every list/form/composer declares columns, filters, controls, validation,
  editability, pagination, import/export and modal chains or explicitly states
  why a surface does not apply.
- Every declared L3/L4 view has stable `FLD/ACT/AC`, an explicit API/data-flow
  mapping, and a four-lens sign-off. A cross-module happy path cannot compensate
  for a thin page.
- Do not patch a duplicate-handler legacy prototype into apparent compliance.
  Rebuild from a trusted interaction ledger when overrides, inline handlers or
  cross-entity modal reuse make action ownership ambiguous.
- A Coding Agent must be able to implement one `REQ-*` slice without inventing
  roles, fields, metrics, controls, limits, states, business rules, errors, or
  success criteria.

## 5. Use domain evidence honestly

Run `scripts/query_domain.py --domain <pack>` before a domain pack. Separate:

- practice status: whether the method was used in a real delivery;
- reusable-pack maturity: `knowledge_backed → contract_tested →
  behavior_validated → expert_reviewed → audited`.

Use first principles to derive domain invariants, authoritative sources for
binding rules, vendor documents for product behavior/patterns, cases for scenario
seeds, and source code/SDKs only for their exact component/version. Open platform
is not proof that a core product is open source. Never promote maturity from
keywords, project complexity, simulation, or static PASS alone.

## 6. Finish with the light gate

```bash
python scripts/ai_delivery_spec_cli.py gate --profile prd --prd requirements/PRD.md --level L2
python scripts/ai_delivery_spec_cli.py gate --profile prototype --prototype prototype.html --level L2
```

The final gate is a zero-LLM, zero-subagent, single-read goalkeeper. It locates
bounded violations but does not author or fix requirements. Static PASS never
replaces domain-owner review, browser journeys, QA execution, or customer
acceptance.

Return one completion state:

```text
PASS
REVIEW_COMPLETE_WITH_GAPS
BLOCKED_BY_P0_UNKNOWN
```

Do not call work complete when only files, headings, buttons, or schemas exist.
For an authorized long task, continue through all requested artifacts and gates;
pause only for a material user decision, external authority, or unsatisfied P0
blocker.
