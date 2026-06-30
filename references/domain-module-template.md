# Domain Module Template

Use this file when creating or replacing a domain module such as `domain-traffic.md`, `domain-education.md`, `domain-sales.md`, `domain-customer-service.md`, or any company-specific domain file.

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
multi-agent lifecycle verification matrix
acceptance checklist
```

If a new company or industry is used, replace only the domain module unless public protocol behavior truly changes.

## Domain Module Skeleton

```markdown
# Domain: {Domain Name}

Use this file for {industry/company/product scope}.

This is a replaceable domain module. Public protocol files must stay domain-neutral.

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

## Multi-Agent Lifecycle Verification Matrix

| domain_id | stage | reviewer_agent | path_type | scenario_ref | evidence_ref | blocking_question | expected_result | test_marker | verdict |
|---|---|---|---|---|---|---|---|---|---|
| {domain_id} | Discover | PM Agent | happy_path | primary value object | Domain Purpose | Is the business outcome explicit? | value object and user result are testable | {domain_id}_discover_pm_happy_path | PASS |
| {domain_id} | Specify | QA Agent | lifecycle_transition | primary lifecycle | State Machines | Can QA convert state changes into test cases? | allowed/blocked transitions are explicit | {domain_id}_specify_qa_lifecycle_transition | PASS |
| {domain_id} | Build/Verify | Coding Agent | acceptance_test_path | implementation handoff | Acceptance Checklist | Can a coding agent trace source truth to tests? | FRR, AC, data-testid/action/state/API, and manifest are traceable | ac_structured;data-testid;data-action | PASS |

## Acceptance Checklist

- [ ] Domain entities and source of truth are explicit.
- [ ] Domain events are defined for core state changes.
- [ ] Metrics have caliber, source, dimensions, owner, status.
- [ ] AI context sources have freshness and permission scope.
- [ ] High-risk actions have human gate.
- [ ] Domain workflows have role paths and test scenarios.
- [ ] UI/mobile patterns include required testids.
- [ ] Multi-agent lifecycle matrix covers PM, domain, architecture/data/AI, QA, and coding perspectives across the stages in scope.
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
