# Domain Module Template

Use this file when creating or replacing a reusable domain pack. Customer-only
knowledge should remain in a Project Domain Capsule.

The public protocol stays domain-neutral. Domain knowledge must live in a replaceable domain module.

## Contents

- Replacement Rule
- Domain Module Skeleton
- Mapping From Old Domain to New Domain
- Domain Quality Gate
- First-Principles Domain Lens
- Domain Switch Verification Checklist
- Example: Knowledge Learning Domain Outline

## Replacement Rule

A valid domain module must preserve these section types:

```text
domain purpose
domain vocabulary
aggregates/entities
domain events
state machines
metric/indicator governance
AI context sources
content/knowledge assets
core workflows
role paths
UI/mobile patterns
policy/privacy constraints
test scenarios
evaluation profile
acceptance checklist
```

Also add metadata to `references/domain-coverage.yaml`, source records to
`references/domains/domain-sources.yaml`, and scenarios to `maintainer/evals/eval-catalog.yaml`.
New packs start as `knowledge_backed` only after source and gap checks pass;
otherwise keep them outside the built-in domain index.

## Domain Module Skeleton

```markdown
# Domain: {Domain Name}

Use this file for {industry/company/product scope}.

This is a replaceable domain module. Public protocol files must stay domain-neutral.

Source authority and freshness metadata: `references/domains/domain-sources.yaml`.
Coverage and maturity: `references/domain-coverage.yaml`.

Applies when:

- {domain object/lifecycle trigger}

Does not apply when:

- {generic or adjacent scenario that should use another pack/capsule}

## Domain Purpose

- Business outcome:
- Primary users:
- Regulated or sensitive areas:
- What AI may optimize:
- What AI must not decide automatically:

## First-Principles Domain Lens

| Lens | Required Answer |
|---|---|
| Value object | What domain object, decision, artifact, or state becomes better? |
| Role job | Which role's repeated job or accountability is changed? |
| State physics | What lifecycle state transition proves work really happened? |
| Source authority | Which public/global, China/national, regional/local, industry, group, or customer-specific rules apply? |
| High-risk boundary | Which actions need human gate, audit, fallback, or rollback? |
| Test evidence | Which scenarios prove the domain logic is usable, not just plausible? |

## Vocabulary

| Term | Meaning | Source of Truth |
|---|---|---|

## Aggregates and Entities

| Aggregate | Owns | Key States | Notes |
|---|---|---|---|

## Domain Events

```yaml
event:
  name: DomainEventName
  trigger: string
  actor: user | system | agent
  payload: {}
  consumers: []
  audit_required: true
```

## State Machines

```text
object: draft -> active -> suspended -> archived
```

## Metric / Indicator Governance

```yaml
metric:
  id: string
  name: string
  category: string
  caliber: string
  source: string
  dimensions: []
  owner: role_or_team
  status: draft | active | deprecated
```

## AI Context Sources

| Context | Source | Freshness | Permission Scope | Risk |
|---|---|---|---|---|

## Content / Knowledge Assets

| Asset Type | Examples | Tags | Quality Rule |
|---|---|---|---|

## Core Workflows

| Workflow | Actors | Trigger | State Change | Success Result |
|---|---|---|---|---|

## Role Path Patterns

| Role | Entry | Core Actions | Forbidden Actions | Exit |
|---|---|---|---|---|

## UI / Mobile Patterns

- desktop patterns:
- mobile patterns:
- required testids:
- role switch requirements:

## Policy / Privacy Constraints

- consent requirements:
- data minimization:
- human approval:
- forbidden AI actions:
- audit requirements:

## Domain Test Scenarios

| Scenario | Role | Preconditions | Steps | Expected Domain Result |
|---|---|---|---|---|

## Evaluation Profile

Register coverage, reusable-pack `maturity`, and delivery `practice_status` in
`references/domain-coverage.yaml`. Keep
behavioral scenarios and execution evidence outside this knowledge file.

Minimum independent evaluation:

- primary happy path;
- validation/exception path;
- permission/privacy path;
- lifecycle transition;
- coding-agent no-guess handoff;
- applicable migration, integration failure, AI, and high-risk human gate.

Record executor, input, environment, timestamp, result, and evidence location.
Do not prefill `PASS`. Mocked scenarios and simulated reviewers do not count as
expert review, project validation, or audit.

- `knowledge_backed`: sourced structure and explicit gaps; no behavior claim.
- `contract_tested`: deterministic lifecycle/risk fixtures pass; no fresh-agent claim.
- `behavior_validated`: fresh-agent positive/negative/domain runs pass with evidence.
- `expert_reviewed`: project samples and accountable expert review pass in scope.
- `audited`: expert-reviewed evidence plus passed independent audit in scope.

Practice status is independent:

- `knowledge_only`: no accountable production-use evidence is recorded;
- `project_practiced`: used in a bounded accountable project;
- `production_practiced`: an accountable owner confirms use in a shipped product;
- `production_observed`: operation evidence is retained and reviewable.

Production practice does not by itself validate every reusable rule in the pack.

Automation may verify that these evidence records exist, are current, and match
scope. Project keywords or complexity must never assign maturity.

## Acceptance Checklist

- [ ] Domain entities and source of truth are explicit.
- [ ] Domain events are defined for core state changes.
- [ ] Metrics have caliber, source, dimensions, owner, status.
- [ ] AI context sources have freshness and permission scope.
- [ ] High-risk actions have human gate.
- [ ] Domain workflows have role paths and test scenarios.
- [ ] UI/mobile patterns include required testids.
- [ ] Independent evaluation covers PM, domain, architecture/data/AI, QA, and coding perspectives required by the scoped stages.
```

## Mapping From Old Domain to New Domain

When migrating a scenario to another domain, create a mapping table:

| Existing Domain Concept | New Domain Concept | Notes |
|---|---|---|
| Driver | Learner | if learning domain |
| Active Safety Alert | Behavior Signal / Mistake Signal | risk signal becomes learning signal |
| RiskAssessment | MasteryAssessment | profile/scoring aggregate |
| Safety Video | Learning Content Asset | tagged content |
| Exam | Quiz / Assessment | result state |
| Behavior Delta | Mastery Delta / Application Evidence | effect evidence |

## Domain Quality Gate

Fail the domain module if:

- it only lists industry terms but lacks workflows and states;
- it lacks source-of-truth rules;
- it lacks AI context sources and permission scope;
- it lacks domain-specific test scenarios;
- it leaks domain-specific rules into public protocol files;
- it does not define what AI is forbidden to do.

## First-Principles Domain Lens

When a domain is created or updated, keep the domain file compact but make the
product logic defensible:

- Start from the value object, role job, lifecycle state, and measurable result.
- Register public/global, China/national, regional/local, industry, group, and
  customer-specific rules when they materially affect scope or acceptance.
- Prefer source registers and applicability notes over copying long standards.
- Mark unverified or time-sensitive rules as assumptions until checked against
  official or accountable sources.
- Define high-risk boundaries: irreversible actions, regulated decisions, money,
  safety, privacy, and AI writeback.

## Domain Switch Verification Checklist

When replacing a domain module, run this checklist before using the protocol in the new company or industry.

| Layer | Check | Pass Rule |
|---|---|---|
| Vocabulary | Old domain terms removed or intentionally mapped | No unmapped old-domain entity appears in new PRD/prototype/testids |
| State machines | New aggregates have explicit states and transitions | No old regulatory/workflow state is reused without mapping |
| Policy/privacy | Retention, desensitization, consent, approval, audit rules fit the new domain | Policy source and owner are named |
| AI context | Context sources, freshness, permission scope, and forbidden AI actions are domain-specific | No AI precondition relies on old-domain data |
| Metrics | Metric caliber/source/dimensions/owner are replaced | No old indicator is copied without a new source of truth |
| UI/testids | Domain-specific testid prefixes and role paths are updated | Automated tests can identify new-domain paths |
| Acceptance scenarios | At least 5 domain-specific happy/error/edge scenarios exist | Scenarios use new-domain entities and risks |

Fail migration if the new domain file passes structurally but still contains old-domain preconditions, regulation triggers, privacy rules, state names, or testid naming assumptions.

## Example: Knowledge Learning Domain Outline

```markdown
# Domain: Knowledge Learning

## Aggregates and Entities

| Aggregate | Owns | Key States |
|---|---|---|
| Learner | profile, goals, consent, learning history | active / inactive |
| ContentAsset | video/article/course metadata, tags, version | draft / published / deprecated |
| KnowledgePoint | concept, prerequisite, difficulty | active / deprecated |
| Quiz | questions, pass threshold, attempts | draft / active / archived |
| MasteryAssessment | mastery score, evidence, weak points | pending / ready / stale |
| LearningTask | assigned content, deadline, status | not_started / in_progress / completed / overdue |

## AI Context Sources

| Context | Source | Freshness | Permission Scope |
|---|---|---|---|
| learning history | learning service | real-time | own learner/org |
| mistake records | quiz service | real-time | own learner/org |
| content catalog | CMS | daily/versioned | public/published |
| knowledge graph | knowledge base | versioned | product |
```
