# Maintainer Assurance Lab

This directory contains release-only tests, evaluations, evidence, fixtures,
schemas and tools. Runtime agents must not load it for ordinary customer work.

Use this reference when changing the Skill, a shared template, a domain pack,
or a validator. The lab is a **release-hardening activity**. It is not a new
mandatory stage for every customer project.

## 1. Two Deliberately Separate Loops

```text
Release / method change
  -> offline cross-industry multi-agent simulation
  -> deterministic regression
  -> publish the Skill

Customer project
  -> requirement workflow
  -> one unified PRD and/or executable prototype
  -> small deterministic final gate
  -> human/customer acceptance
```

The assurance lab explores whether the method misses a class of requirement.
The runtime gate checks whether the current artifact violates a known contract.
Do not run a panel of reviewer agents merely to declare a project complete.

## 2. What The Lab Can And Cannot Prove

The lab can prove that representative scenarios exercise all requirement
stages, role lenses, risk classes, and output contracts, and that known omissions
are caught by deterministic tests. It cannot prove jurisdictional correctness,
clinical or financial safety, customer acceptance, production behavior, or
domain-pack maturity. A simulated reviewer is not an accountable domain expert.

Official sources in `maintainer/evals/industry-assurance-portfolio.yaml` are discovery
anchors. A real project must register the applicable edition, jurisdiction,
authority, interpretation owner, and customer-confirmed decisions as `SRC-*`.

## 3. When To Run It

Run the portfolio when any of these changes:

- `SKILL.md` routing, completion, or stage behavior;
- the unified PRD or prototype contract;
- shared intake, review, change, traceability, or acceptance schemas;
- a domain/capability pack or reusable pattern;
- a validator or quality-gate severity rule;
- a production escape reveals a missing requirement class.

For a documentation-only typo with no contract effect, the normal static tests
are enough. For a new industry, add one scenario only after its requirement
physics is not already represented by an existing case.

## 4. Compact Multi-Agent Protocol

Use eight independent role lenses. Give each reviewer one scenario, its role
contract, the seven stage checkpoints, and only the stable-ID slice needed for
that review. Do not give every reviewer the full repository or all domain packs.

| Lens | Accountability in the simulation |
|---|---|
| business sponsor | outcome, value evidence, decision authority, scope trade-off |
| product | requirement closure, source precedence, stable IDs, baseline/change |
| domain | vocabulary, lifecycle, invariant, authority applicability, unknowns |
| UX/prototype | discoverable role path, states, actions, errors, visible results |
| engineering/architecture | non-inventive handoff, integration, concurrency, recovery |
| QA/acceptance | executable AC, negative path, evidence, regression and reverse trace |
| compliance/security | data scope, human accountability, audit, retention, prohibited action |
| customer acceptor | business outcome, operable handoff, acceptance evidence, residual condition |

Each role returns compact finding records only:

```yaml
- id: FIND-{scenario}-{role}-{nnn}
  stage: intake|clarify|specify|review|baseline|change|acceptance
  role: ROLE-LENS-*
  verdict: pass|finding|block|not_applicable
  affected_ids: [REQ-*]
  evidence_refs: [SRC-*]
  gap: one concrete, falsifiable sentence
  required_decision: owner plus a closure condition
```

One role reviews all seven stage checkpoints in one bounded pass. The portfolio
caps findings and evidence references; a reviewer must prioritize missing P0/P1
contracts instead of rewriting the PRD. Independent role outputs are aggregated
by stable ID. Majority voting never overrules a safety, authority, privacy,
financial, or customer-acceptance blocker.

## 5. Seven Stage Checkpoints

| Stage | Minimal cross-role closure |
|---|---|
| intake | outcome/value/source/owner, complexity and risk, decision, mode/tier and target baseline |
| clarify | actor/data scope, lifecycle, rule/exception, integration and acceptance unknowns closed or blocked |
| specify | readable journeys plus exact page/action/field/state/rule/integration/AC contracts |
| review | P0/P1 findings bound to IDs, owners, dispositions, decisions and evidence |
| baseline | approved version, included IDs, source precedence, frozen unknowns and consumer synchronization |
| change | authorized request, bidirectional impact, before/after, compatibility, regression and new baseline |
| acceptance | executed mandatory AC, visible/domain results, evidence, defect reverse trace and sign-off |

The detailed role-by-stage minimum outputs live in the portfolio so a test can
detect silent loss of a reviewer or stage.

## 6. PRD Standard Exercised By The Portfolio

A simulated PRD output passes only when it remains one shared reading path and:

1. explains outcome, scope, roles, end-to-end handoffs and business flows before
   engineering appendices;
2. specifies actions, visible/domain results, permissions, states, rules,
   exceptions, data semantics and applicable integration behavior;
3. prevents product, development, test, and Coding Agents from inventing a
   business decision while leaving implementation design to engineering;
4. binds `SRC -> REQ -> behavior -> AC -> test/run -> evidence` in both
   directions and carries approved changes through every affected projection;
5. gives traditional teams a readable document, not only YAML tables.

The same scenario is then probed as a downstream consumer handoff: product/
business review, prototype build, engineering design, coding implementation,
test derivation and customer acceptance. These probes check readiness and
forbidden invention; they do not manage sprints, code, CI/CD or deployment.

## 7. Prototype Standard Exercised By The Portfolio

A simulated prototype output passes only when:

- each important view, region, action, field and state has the stable runtime
  annotation defined in `prototype-testability.md`;
- every `data-action` has a handler, visible result, domain-state result, failure
  behavior and an acceptance reference;
- all primary role journeys include entry, permission, handoff, success, exit,
  applicable empty/error/no-permission/conflict states, and representative data;
- brownfield changes preserve the trusted view/action/handler/role-path baseline;
- JavaScript syntax, interaction ledger closure, CSS `.hidden` isolation, and
  applicable browser walkthroughs pass.

The lab inspects requirement and interaction completeness. It does not replace
visual design review or executed customer acceptance.

## 8. Lightweight Runtime Goalkeeper

The final project gate is a goalkeeper, not an author:

- zero LLM/sub-agent calls;
- no automatic PRD/Product Truth/prototype regeneration;
- load each artifact at most once and reuse parsed indexes;
- select only applicable checks from artifact type, tier, risk and change state;
- emit concise findings with severity, stable IDs, evidence and the violated
  contract; do not produce long tutorial prose;
- default to fail-fast on P0 and summarize P1/P2; use full diagnostics only when
  a maintainer explicitly requests it;
- do not require Product Truth below its existing scale/audit trigger;
- require browser evidence only for in-scope critical journeys, not every
  decorative control.

Runtime completion remains `PASS`, `REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`.
A syntactic PASS cannot upgrade missing accountable approval or acceptance
evidence.

## 9. Portfolio Maintenance

`maintainer/evals/industry-assurance-portfolio.yaml` contains seven high-relevance sectors
selected for different requirement physics rather than a marketing ranking:
industrial batch genealogy, clinical accountability, regulated money,
safety/IoT/offline work, high-scale order/inventory consistency, cross-agency
public service, and project/contract settlement. It also bridges the existing
traffic, CRM, education, data-product, and AI-native packs.

Run the deterministic contract check with:

```powershell
py -3 maintainer/tests/test_v510_industry_assurance.py
```

The test verifies portfolio structure and coverage. Actual agent transcripts,
expert reviews, customer sign-off, and browser evidence must be recorded as
separate dated evidence; do not rewrite scenario declarations to look executed.

## Domain-Pack Assurance

Keep method practice and reusable-pack maturity separate:

```text
knowledge_backed -> contract_tested -> behavior_validated
-> expert_reviewed -> audited
```

`production_practiced` records that the method was used in a shipped product;
it does not promote every reusable rule. Domain claims require applicable
sources, declared gaps and dated evidence. Vendor materials prove only the
documented product/version; cases seed scenarios; open source or SDK code proves
only the inspected component. Simulations and static PASS never count as expert
review or production correctness.

Promotion requires the matching evidence class:

| Target | Minimum evidence |
|---|---|
| `contract_tested` | source/coverage/schema checks and deterministic fixtures |
| `behavior_validated` | independent fresh-agent runs with raw task-local artifacts |
| `expert_reviewed` | accountable domain reviewer, scope, findings and closure |
| `audited` | controlled audit evidence and retained decision trail |

Run domain checks from the repository root:

```bash
python maintainer/tools/validators/validate_domain_sources.py
python maintainer/tools/validators/validate_domain_contracts.py
python maintainer/tools/validators/validate_domain_coverage.py
```

Never batch-promote all domains from one scenario. Promote one pack and one
evidence boundary at a time.

## Reviewer Contract

Review requirement intake, the unified PRD, optional Product Truth, prototypes,
changes, traceability and acceptance evidence. Bind each finding to `REV-*` and
affected `REQ-*`/behavior IDs; do not rewrite artifacts unless requested.

- P0 blocks outcome, authority, safety/compliance, data isolation or acceptance.
- P1 creates likely rework, ambiguity, failed journeys or missing evidence.
- P2/P3 cover readability, maintainability, context efficiency and future risk.

Open P0/P1 cannot be hidden in notes. Finish with scoped `PASS`,
`REVIEW_COMPLETE_WITH_GAPS` or `BLOCKED`, citing exact IDs and evidence.

## Directory Policy

- `evals/`: catalogs, runs and immutable evidence ledgers.
- `tests/`: deterministic regression and fixtures.
- `examples/`: non-runtime reference projects used by regression.
- `tools/`: release/evaluation utilities; user-facing commands stay in `scripts/`.
- `schemas/`: contracts used only by the assurance lab.
- `templates/`: maintainer-only extension templates.

Prefer appending records to an existing catalog/ledger over creating one file
per run. Create a new file only when immutability, a distinct schema or an
independently reviewable raw artifact requires it.
