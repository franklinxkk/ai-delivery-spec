# Maintainer Assurance Lab

This directory contains release-only tests, evaluations, evidence, fixtures,
schemas and tools. Runtime agents must not load it for ordinary customer work.

Use this reference when changing the Skill, a shared template, a domain pack,
or a validator. The lab is a **release-hardening activity**. It is not a new
mandatory stage for every customer project.

历史探索记录保留在 Git 历史中；当前版本只维护仍能约束发布结论的设计记录、夹具与门禁，不再为每个补丁版本新增平铺材料。

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

## 4. Bounded Review Protocol

Use only the role lenses required by the risk: sponsor/product, domain, UX,
engineering, QA, compliance/security and customer acceptance. Give each lens one
stable-ID slice, cap findings, and return only affected IDs, evidence, one
falsifiable gap, owner and closure condition. Aggregate by stable ID; never use
majority voting to overrule authority, safety, privacy, financial or acceptance
blockers. The portfolio contains the detailed stage/role coverage. Runtime PRD
and prototype contracts remain authoritative; this lab tests them and must not
duplicate them as another handbook.

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

Maintenance verification has two explicit execution models:

- `maintainer/tests/` contains pytest-collectable tests with isolated fixtures and normal assertion failures.
- `maintainer/checks/` contains standalone release/regression checks invoked as subprocesses by `ai_delivery_spec_cli.py check`; importing them is not a supported API.

Do not place import-time `SystemExit` scripts under `maintainer/tests/`. New current-release behavior should prefer a compact invariant test; retain a historical standalone check only while its contract is still relevant.

`maintainer/evals/industry-assurance-portfolio.yaml` contains seven high-relevance sectors
selected for different requirement physics rather than a marketing ranking:
industrial batch genealogy, clinical accountability, regulated money,
safety/IoT/offline work, high-scale order/inventory consistency, cross-agency
public service, and project/contract settlement. It also bridges the existing
traffic, CRM, education, data-product, and AI-native packs.

Run the deterministic contract check with:

```powershell
py -3 maintainer/checks/check_v510_industry_assurance.py
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

## Private Knowledge Promotion Test

The runtime `custom/` loop is deliberately smaller than a learning platform:

```text
project-local candidate -> usage evidence across projects -> assess
-> independent human review -> organization/public review candidate -> regression
```

`candidate assess` may recommend review but never moves files, changes scope,
publishes data or calls a network service. `adopted` evidence alone is
insufficient: modified, rejected and invalidated uses remain first-class records.
Sensitive project-local candidates are excluded even from the shared private
package until an accountable owner redacts and moves them into the review area.


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
The assurance lab is subordinate to the runtime skill. Budgets are enforced by
`test_v511_runtime_budget.py`: at most 56 maintainer files, 450 KB, and 12 commands
in the default fast check. Historical exploratory matrices and one-file-per-run
evidence belong in Git history or an external evidence store, not the active tree.

`check` defaults to fast release-risk checks. Only release candidates run
`check --profile release`; ordinary Skill use never loads this directory.


- `evals/`: compact catalogs, current metrics and active evidence only.
- `tests/`: deterministic regression and fixtures.
- `examples/`: non-runtime reference projects used by regression.
- `tools/`: release/evaluation utilities; user-facing commands stay in `scripts/`.
- `schemas/`: contracts used only by the assurance lab.
- `templates/`: maintainer-only extension templates.

Prefer appending records to an existing catalog/ledger over creating one file
per run. Create a new file only when immutability, a distinct schema or an
independently reviewable raw artifact requires it.
