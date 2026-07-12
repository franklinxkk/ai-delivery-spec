# Verify Behavior And Evidence

Use this reference for artifact review, release validation, domain evaluation,
customer acceptance, and skill forward-testing.

## Evidence Semantics

Separate four claims:

1. schema/structure is valid;
2. artifacts are internally consistent;
3. a scenario behavior passed;
4. domain knowledge is validated or audited.

Never report one as another. `PASS` must name scope, executor, input, time,
environment, result, and evidence location.

## Artifact Gates

| Gate | Blocking Question |
|---|---|
| discovery | Are outcome, evidence, scope, owners, and P0 unknowns explicit? |
| product truth | Can roles finish tasks without missing pages/actions/states/rules? |
| prototype | Does every primary action have visible and domain results? |
| coding handoff | Can implementation proceed without inventing business behavior? |
| QA | Can tests run from AC IDs and produce required evidence? |
| launch | Are migration, rollback, security, operations, and acceptance ready? |
| domain | Are professional claims sourced, applicable, evaluated, and honestly matured? |

## Behavioral Evaluation

Use clean inputs and independent runs. Do not leak the intended answer or known
defect into the evaluation prompt.

Score:

| Dimension | Evidence |
|---|---|
| trigger accuracy | positive and negative prompts |
| clarification quality | material unknowns found without questionnaire bloat |
| requirement completeness | role/flow/page/action/state/data/exception/AC closure |
| no-guess handoff | implementation questions and inventions |
| cross-artifact consistency | ID graph and semantic comparison |
| domain accuracy | source/applicability/expert findings |
| change safety | affected IDs and regression coverage |
| human usability | task walkthrough by intended reader |
| context efficiency | files/tokens loaded for the task |

Use `evals/metric-definitions.yaml` and `schemas/evaluation-run.schema.json`
for quantitative runs. Record raw obligation outcomes, unsupported inventions,
impacted ACs, specification rework, accepted ACs, token usage, navigation time,
and evidence before calculating rates. A P0 omission or unsupported P0 business
behavior blocks release even when the aggregate score is high.

Compare baseline and candidate only when case/input fingerprint, pinned repository ref,
model, settings, and repetition count match. Report tokens per accepted AC, not
raw document size. Do not publish a percentage improvement from a single run.

## Required Perspectives

For a release candidate, test at least:

- newcomer with a one-sentence request;
- product owner with a multi-module ToB workflow;
- coding agent with only the delivery package;
- QA with Product Truth and acceptance;
- domain/accountability reviewer for regulated assertions.

Use multiple product stages and project shapes. A single CRM sample cannot prove
generic or full-lifecycle capability.

`evals/github-cases.yaml` provides pinned public-project inputs for requirement,
design, and coding-delivery evaluation. An issue is user evidence, not automatic
maintainer approval or current roadmap truth; inspect the pinned repository
before producing a brownfield design or handoff.

## Domain Maturity Gate

Read `references/domain-coverage.yaml` and validate it against
`schemas/domain-pack.schema.json`.

- `experimental`: knowledge may guide questions and candidate design.
- `validated`: requires sourced knowledge, project-sampled scenarios, passed
  behavioral evaluation, and accountable review.
- `audited`: requires validated scope plus independent audit evidence.

Mocked scenarios, generated tables, and simulated reviewers cannot satisfy
expert review or audit fields.

## Completion State

Return exactly one:

- `PASS`: every required gate in the named scope has evidence;
- `REVIEW_COMPLETE_WITH_GAPS`: useful result with named gaps/owners;
- `BLOCKED`: a P0 decision or external condition prevents safe progress.

The state must include scope and must never be inferred from the word `PASS`
inside a template or domain reference.
