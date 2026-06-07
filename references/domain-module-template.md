# Domain Module Template

Use this file when creating or replacing a domain module such as `domain-traffic.md`, `domain-education.md`, `domain-sales.md`, `domain-customer-service.md`, or any company-specific domain file.

The public protocol stays domain-neutral. Domain knowledge must live in a replaceable domain module.

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

## Acceptance Checklist

- [ ] Domain entities and source of truth are explicit.
- [ ] Domain events are defined for core state changes.
- [ ] Metrics have caliber, source, dimensions, owner, status.
- [ ] AI context sources have freshness and permission scope.
- [ ] High-risk actions have human gate.
- [ ] Domain workflows have role paths and test scenarios.
- [ ] UI/mobile patterns include required testids.
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

