# Advanced Extensions

Use this file only after `SKILL.md` 0D triage or explicit user scope triggers an advanced capability.

## Contents

- Extension Loading Rule
- AI Feature / AI Native / Prompt Ops
- SaaS, RBAC, And Multi-Tenancy
- Approval And Audit Workflow
- Reporting, Dashboard, And Data Product
- Workflow Automation And Low-Code
- Mobile, Multi-Surface, And Global Delivery
- System Readiness, Release, And Retirement
- Domain Modules, Templates, And Legacy Assets

## Extension Loading Rule

Do not load this file for ordinary CRUD, static display, simple copy edits, or code-only syntax/debugging. Within this file, read only the section whose trigger applies.

Extension trigger matrix:

| Trigger | Section |
|---|---|
| product AI exists or AI claims/effects are in scope | AI Feature / AI Native / Prompt Ops |
| tenant, org tree, data scope, RBAC, license, seat, region isolation | SaaS, RBAC, And Multi-Tenancy |
| approval, escalation, countersign, dispatch, audit, return/reject | Approval And Audit Workflow |
| indicator, BI, dashboard, report template/task/fill, data mart | Reporting, Dashboard, And Data Product |
| visual workflow, low-code, connector, automation node, execution replay | Workflow Automation And Low-Code |
| app/H5/mini-program/PC+mobile, overseas, localization, app stores | Mobile, Multi-Surface, And Global Delivery |
| release, migration, rollout, on-call, rollback, retirement | System Readiness, Release, And Retirement |
| industry/domain switch, traffic safety, CRM, prompt registry, templates | Domain Modules, Templates, And Legacy Assets |

## AI Feature / AI Native / Prompt Ops

Classify per module:

| Class | Contract |
|---|---|
| AI-supporting | manual path remains valid; AI output is draft/extraction/classification/recommendation; qualified human confirms consequential outcomes |
| AI-core | user outcome depends on AI or AI routes/tools/writes state; requires runtime, evaluation, observability, rollback, and human gate |
| AI-incidental | AI only helps create artifacts; no product AI gate |

Minimum AI-supporting contract:

- user-visible AI role and confidence boundary;
- deterministic fallback/manual path;
- input source, output schema, human confirmation point;
- prohibited writes and refusal behavior;
- linked test cases and regression examples;
- effect claim evidence level.

AI-core production contract:

```yaml
ai_runtime_contract:
  agent_or_model: name/version
  write_scope: none | draft_only | workflow_task | business_state
  input_schema_version: v1
  output_schema_version: v1
  tool_scope: allowed tools and forbidden combinations
  human_gate: required_before_write | required_before_publish | not_applicable_with_reason
  fallback_state: local_fallback | manual_review | ai_failed
  observability: trace_id, prompt_version, model_version, latency, confidence, failure_reason
  rollback: owner, trigger, linked_test_cases
```

Evaluation contract:

- golden cases are tiered: P0 smoke, P1 regression, P2 long-tail/adversarial;
- each claim has evidence reference, baseline, threshold, reviewer, and sample size;
- product copy must not overclaim beyond evidence level;
- prompt/model parameters are `PROPOSED` until calibrated with evidence.

Runtime resilience:

- if network probe > 3000ms or cloud AI returns 5xx, enter `local_fallback` within 100ms;
- local fallback may display cached data, deterministic rule result, or manual workflow only;
- AI must not write business state during fallback unless a deterministic local policy explicitly allows it.

Prompt Ops source assets:

- `prompt-registry.yaml`
- `prompt-registry-integration.md`
- `ai-feature-injection.md`
- `ai-native-harness-engineering.md`
- `ai-runtime-ops.md`
- `ai-effect-evaluation.md`

Load them only when this section is insufficient for the requested artifact.

## SaaS, RBAC, And Multi-Tenancy

Trigger when scope includes tenant, enterprise, government unit, organization tree, data permission, license, seat, or region isolation.

Minimum contract:

| Area | Required |
|---|---|
| Tenant model | tenant root, sub-org, department, user, role, resource owner |
| Data scope | own, department, subordinate, assigned industry/type, assigned enterprise, cross-region prohibition |
| RBAC | role-menu-action-data matrix; disabled/locked/system roles |
| Delegation | who can grant, revoke, inherit, union/intersection rule |
| Isolation | tenant_id, org_id, region/home_region, audit boundary |
| License/seat | enabled features, quota, expiry, overage behavior |

Permission rule must state whether multiple scopes are union or intersection. If not specified, block development handoff.

Source asset: `saas-multitenancy.md`.

## Approval And Audit Workflow

Trigger when scope contains approval, escalation, countersign, return/reject, dispatch, deadline, audit, or record retention.

Minimum workflow canvas:

| Step | Actor | Input | Decision | State Change | Audit/Event | Timeout/Fallback |
|---|---|---|---|---|---|---|
| | | | approve/reject/return/escalate/cancel | | | |

Rules:

- state determines buttons;
- returned/rejected/resubmitted paths must be explicit;
- deadline, overdue, reminder, and manual override must be defined when business-critical;
- audit contains actor, role, org, before/after value, reason, attachment, time, source surface.

Source asset: `approval-workflow.md`.

## Reporting, Dashboard, And Data Product

Trigger when scope includes indicator library, dashboard, BI, report template/task, Excel fill-in, data mart, data source, or AI data report.

Minimum contracts:

Indicator:

```yaml
indicator:
  id: IND-001
  name:
  subject: enterprise | vehicle | person | org | time_period
  formula:
  source_tables_or_api:
  refresh_frequency:
  permissions:
  quality_rule:
  owner:
```

Dashboard/report:

- metric caliber and lineage;
- filter dimensions, drill path, export behavior;
- empty/error/loading/permission states;
- source freshness and refresh time;
- generated report sections, prompt fragments, inserted indicators, knowledge references, and evidence citations.

Excel/report task:

- template snapshot at publish time;
- auto-fill fields vs enterprise fill-in fields;
- auto extraction rate and fill completion rate;
- submit, return, complete, lock, export, and audit states.

Source asset: `reporting-analytics.md`.

## Workflow Automation And Low-Code

Trigger when scope includes workflow canvas, node graph, connectors, low-code form, automation, orchestration, or human-in-the-loop node.

Minimum contract:

| Contract | Required |
|---|---|
| Graph | nodes, edges, trigger, stop condition, retry policy |
| Node | input schema, output schema, side effect, timeout, idempotency |
| Connector | credential owner, permission, rate limit, error mapping |
| Version | draft/published/deprecated, migration behavior |
| Replay | execution history, trace, resume/retry, compensation |

Low-code does not remove product responsibility: field dictionary, validation, permission, audit, and acceptance must still be specified.

Source asset: `workflow-automation-lowcode.md`.

Use `build-governance.md` only when a prototype or workflow is repeatedly
patched/generated by scripts and the build chain itself becomes a delivery
risk.

## Mobile, Multi-Surface, And Global Delivery

Trigger for H5, app, mini-program, field staff, weak network, PC+mobile consistency, overseas launch, cross-border data, multi-language, or regional model routing.

Mobile contract:

- role path per surface;
- offline/weak-network behavior;
- permission gates: camera, location, files, notifications;
- message/subscription/non-disturb rules;
- biometric/signature/location evidence where applicable;
- mobile testid map and gesture/accessibility coverage.

Multi-surface consistency:

| Shared Across Surfaces | May Differ |
|---|---|
| business state machine, data ownership, permission, audit, domain events, validation | layout, navigation density, gesture, device capability, offline cache |

Global/regional contract:

- target countries/regions/languages;
- data residency and cross-border basis;
- model/API region routing;
- per-locale evaluation and native reviewer;
- app store/payment/local policy differences;
- RTL and localization behavior when relevant.

Source assets:

- `mobile-product-delivery.md`
- `multi-surface-consistency.md`
- `system-readiness-checklist.md`

## System Readiness, Release, And Retirement

Trigger for production rollout, pilot, migration, release, on-call, rollback, incident review, retirement, or data deletion/export.

Readiness minimum:

| Area | Required |
|---|---|
| Environment | target tenant/region, dependency, feature flag, migration script |
| Data | import/export, reconciliation, backup, rollback, shadow/test isolation |
| Operation | owner, on-call, alert, runbook, escalation |
| Release | cutover plan, smoke test, rollback trigger, customer notice |
| Compliance | audit retention, privacy, deletion/export proof |

Retirement requires dependency inventory, customer migration, compatibility window, data export/deletion, support stop date, and closure evidence.

Source assets:

- `system-readiness-checklist.md`
- `artifact-packaging.md`
- `delivery-acceptance-gates.md`

## Domain Modules, Templates, And Legacy Assets

Domain modules remain load-on-demand assets:

- new industry/company domain: start from `domain-module-template.md`;
- traffic safety: `domain-traffic.md` plus `domain-traffic-safety-scenarios.md`;
- CRM: `domain-crm.md`.

Templates:

- light PRD: `templates/prd-light-template.md`;
- standard PRD: `templates/prd-standard-template.md`;
- AI Native PRD: `templates/ai-native-prd-template.md`;
- readiness checklist: `templates/system-readiness-checklist-template.md`.

External lifecycle and PM frameworks are upstream evidence, not runtime
dependencies. If a user brings Product-Manager-Skills, Spec Kit, to-prd style
PRDs, market sizing, opportunity trees, roadmaps, or issue lists, register them
as source artifacts and map them into `delivery-core.md` lifecycle stages. Do
not load or reproduce their complete process unless the user explicitly asks to
run that external framework.

Strategy/discovery source asset:

- `strategy-discovery-handoff.md`

Historical detail assets retained for compatibility and audits:

- `delivery-tier-model.md`
- `demo-closed-ddd-handoff.md`
- `story-path-verification.md`
- `skill-design-benchmark.md` (maintenance-only; use when upgrading or auditing the skill itself)

Legacy reference files are retained as source assets for detail recovery and historical compatibility. Do not load them by default. The runtime truth is the four-entry architecture: `SKILL.md`, `delivery-core.md`, `prototype-testability.md`, and `advanced-extensions.md`.
