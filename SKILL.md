---
name: ai-delivery-spec
description: Manage product requirements from intake through clarification, specification, baseline, change, traceability, and acceptance. Turn rough ideas, customer materials, prototypes, legacy systems, or approved changes into one human-readable, AI-coding-ready requirement contract with stable IDs and executable acceptance. Use for ToC/ToB/ToG requirement intake, PRDs, role workflow closure, brownfield change, prototypes, acceptance, or audit traceability. Excludes sprint/task management, implementation management, CI/CD, production operations, and unrelated code debugging or copy rewriting.
---

# AI Delivery Spec 5.1.1 — Requirement Management Kernel

> First use: run requirement intake; use `mode=ultra_light` only for one reversible change.
>
> Default deliverable: one human-readable PRD shared by product, engineering, QA, and Coding Agents.
>
> Domain route: append `domain=traffic|crm|education-it|oa|medical-hospital-it|data-product|ai-native`.

Manage six concerns only: intake, clarification, specification, change,
traceability, and acceptance. Treat planning, tasks, code, CI/CD, deployment,
and operations as downstream systems; retain only requirement-related links or
evidence.

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
- Use Ultra-Light only for one reversible page/copy/field/rule change with one
  primary role and no cross-module state, sensitive data, regulated decision,
  customer acceptance, or migration.
- Multi-role flows, brownfield change, regulation/audit, complete PRDs, and
  customer acceptance require at least L2.
- Register iteration, dependencies, conflicts, and ordering for parallel needs.

Run `scripts/triage_requirement.py` or use
`references/requirement-management.md` and
`schemas/requirement-register.schema.json`. Do not write a final PRD before
intake and P0 clarification gates pass.

## 2. Load only the active slice

| Need | Read |
|---|---|
| intake, lifecycle, requirement pool | `references/requirement-management.md` |
| source/prototype/legacy inventory | `references/discover.md` |
| ambiguity and clarification | `references/runtime/schema-grill.md` |
| behavior and stable IDs | `references/specify.md` |
| unified PRD | `references/templates/unified-requirement-prd-template.md` |
| machine annex | `references/runtime/ai-coding-completeness.md` |
| multi-role or seniority handoff | `references/runtime/role-stage-playbook.md` |
| prototype | `references/runtime/prototype-testability.md` |
| change / acceptance | `references/runtime/change.md` / `references/runtime/verify.md` |
| large context | `references/runtime/context-planning.md` |
| domain work | run `scripts/query_domain.py --domain <pack>`, then read only matching domain sections |
| domain evidence or promotion | `references/runtime/domain-assurance.md` |
| common reusable pattern | matching entry in `references/patterns/common-requirement-patterns.yaml` |
| Skill/template/validator release | `references/runtime/assurance-lab.md` |

Load one stage reference, optionally one domain pack, and only triggered
governance. Do not load README, all examples, all domains, or the full repository
at runtime. For long domain files, search the contents/table first and read only
the relevant section plus Evaluation Profile.

## 3. Run the requirement loop

```text
Intake → Clarify → Specify → Review → Baseline → Change → Acceptance → Closed
```

1. **Intake** — create `REQ-*`; record source, outcome, evidence, scope, owner,
   dependency, priority, complexity, target version, and decision.
2. **Clarify** — close roles, trigger, result, flow, permission/data scope,
   state authority, rule, exception, migration/integration, acceptance, and
   out-of-scope. Batch independent questions. Record unresolved material issues
   as `REV-*` with owner and closure evidence.
3. **Specify** — write one sequential PRD. The main body explains why/what,
   roles, journeys, modules, flows, pages, rules, exceptions, and acceptance.
   Append field/state/API/event/trace/machine-AC contracts for engineering and
   Coding Agents. Do not turn database/framework/deployment choices into product
   requirements unless they are business contracts.
4. **Review** — product, domain, UX, engineering/architecture, QA, compliance,
   and customer lenses independently check their required outputs. Read
   `references/runtime/role-stage-playbook.md` for multi-role work.
5. **Baseline** — freeze version, included IDs, source precedence, approvals,
   unresolved dispositions, prototype binding, and consumer synchronization.
6. **Change** — create `CHG-*` under
   `schemas/change-package.schema.json`; traverse requirement, role, flow,
   view/action/field, state/rule, API/event, acceptance/test/evidence, and
   history in both directions; approve, synchronize, regress, and re-baseline.
7. **Acceptance** — turn every `AC-*` into executed items with actual result,
   evidence, defect/change reverse links, conditions, and accountable sign-off.

Use `Product Truth` only when 12+ modules/views, repeated material change,
multiple governed projections, long-lived audit, or explicit user choice makes
an independent truth model valuable. Otherwise keep the requirement register,
one PRD, change package, trace ledger, and acceptance run as the baseline. For
large truth, use progressive fragments and ID slices; never generate one giant
YAML in a single pass.

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
- A Coding Agent must be able to implement one `REQ-*` slice without inventing
  roles, fields, states, business rules, errors, or success criteria.

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
