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
- Domain Modules And Templates
- Coding Agent Compatibility
- Repository Cleanliness Rule

## Extension Loading Rule

Do not load this file for ordinary CRUD, static display, simple copy edits, or code-only syntax/debugging. Within this file, read only the section whose trigger applies.

Extension trigger matrix:

| Trigger | Section |
|---|---|
| product AI exists or AI claims/effects are in scope | AI Feature / AI Native / Prompt Ops |
| tenant, org tree, data scope, RBAC, license, seat, region isolation | SaaS, RBAC, And Multi-Tenancy |
| approval, escalation, countersign, dispatch, audit, return/reject | Approval And Audit Workflow |
| data source, ingestion, ETL, ELT, CDC, stream, lakehouse, warehouse, catalog, lineage, governance, ontology, semantic layer, data agent, ChatBI, NL2SQL, indicator, BI, dashboard, report template/task/fill, data mart, metric, 数据源, 数据采集, 清洗, 治理, 存储, 检索, 本体, 语义层, 数据智能体, 智能问数, 数据集市, 报表配置, 填报系统, 指标管理, 口径管理, 维度管理, 取数范围 | Reporting, Dashboard, And Data Product |
| visual workflow, low-code, connector, automation node, execution replay | Workflow Automation And Low-Code |
| app/H5/mini-program/PC+mobile, overseas, localization, app stores | Mobile, Multi-Surface, And Global Delivery |
| release, migration, rollout, on-call, rollback, retirement | System Readiness, Release, And Retirement |
| industry/domain switch, traffic safety, transport supervision, CRM, AI-native product, agentic system, higher-education informationization, medical/hospital IT, templates | Domain Modules And Templates |
| coding agent handoff, generate AGENTS.md/CLAUDE.md/.cursor/rules/.cursorrules, convert AC to test stubs, implement from PRD | Coding Agent Compatibility |

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
- use `ai_contract_lite` for L2 AI-supporting features by default; upgrade to
  full `ai_runtime_contract` only when AI writes consequential state, calls
  side-effect tools, needs runtime rollback/eval/on-call, or affects
  compliance, safety, money, legal, or customer acceptance.

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
- For coding-agent handoff, choose contract depth with the selection ladder in
  `coding-agent-compat.md`. L2 AI-supporting features should normally stay on
  `ai_contract_lite`; AI-core or high-risk features use full contract with
  `impl` and `eval`.

Prompt ops is now handled inside this section and `coding-agent-compat.md`.
Do not load separate prompt registry files; if a project needs prompt/version
operations, write a local project `prompt-registry.yaml` in the delivery package
rather than in this skill repository.

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

This section is the authoritative SaaS/RBAC contract. No extra SaaS reference
file is required.

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

This section is the authoritative approval/audit workflow contract. No extra
approval reference file is required.

## Reporting, Dashboard, And Data Product

Trigger when scope includes data source ingestion, ETL/ELT, CDC, stream, data
cleaning, data quality, governance, catalog, lineage, storage, retrieval,
lakehouse/warehouse/mart, semantic layer, ontology, indicator library, metric
platform, dashboard, BI, report template/task, Excel fill-in, data scope
filter, Data Agent, ChatBI, NL2SQL/NL2Metrics, insight generation, or AI data
report. For deep data-product work, also load `domain-data-mart.md`.

Minimum contracts:

AI+Data capability stack:

| Layer | Required Contract |
|---|---|
| Source and acquisition | source inventory, connector/API/file/stream/manual mode, credential owner, schema, sync cadence, backfill, idempotency, retry |
| Processing and cleaning | transform rules, standardization, dedupe/entity resolution, exception queue, raw preservation, quality gates |
| Governance and catalog | asset owner, classification, metadata, lineage, certification, access approval, audit, lifecycle |
| Storage and retrieval | lake/warehouse/mart/OLAP/search/vector/cache path, freshness, latency, retention, cost, permission, index/materialization |
| Semantic and ontology | business glossary, metrics, dimensions, object/link/action types, relations, examples, model version, rollback |
| Analytics and reporting | dashboard/report/fill/self-service analysis, filters, drill paths, exports, empty/error/permission states |
| Data Agent and ChatBI | allowed sources/tools, user-scope inheritance, citations, freshness handling, refusal rules, eval sets, human gate |
| Action loop and operations | insight-to-action owner, write scope, workflow task/ontology action, monitoring, rollback, incident, cost/adoption metrics |

Indicator:

```yaml
indicator:
  id: IND-001
  name:
  layer: atomic | derived | composite
  subject: enterprise | vehicle | person | org | time_period | custom
  business_definition:
  technical_expression: sql | mql | formula | rule
  source_tables_or_api:
  refresh_frequency:
  statistical_period:
  unit:
  dimension_refs:
  permissions:
  quality_rule:
  business_owner:
  technical_owner:
```

Indicator governance:

| Contract | Required |
|---|---|
| Layered indicators | atomic / derived / composite layer, dependency graph, recalculation rule |
| Caliber dual track | business definition plus SQL/MQL/formula, source, period, owner, version |
| Dimension dictionary | dimension ID, value source, hierarchy/drill path, related indicators |
| Exception rule table | related metric, effective condition, adjustment logic, business basis, expiry |
| Change propagation | affected templates/reports/dashboards/exports/AI answers, owner notification |
| Lineage | source system -> table/API -> indicator -> template -> report/dashboard/export |

Dashboard/report:

- metric caliber and lineage;
- filter dimensions, drill path, export behavior;
- empty/error/loading/permission states;
- source freshness and refresh time;
- row-level and column-level permission behavior before aggregation and export;
- generated report sections, prompt fragments, inserted indicators, knowledge references, and evidence citations.

Excel/report task:

- template snapshot at publish time;
- auto-fill fields vs enterprise fill-in fields, with explicit `sys` / `ext` column split;
- auto extraction rate and fill completion rate;
- submit, return, complete, lock, export, and audit states;
- deadline, reminder, overdue, return/rework, and idempotent batch operations.

Data scope and statistical period:

| Area | Required |
|---|---|
| Scope filter | subject, selectable dimensions, default value, row-scope permission, export behavior |
| Statistical period | day/week/month/quarter/custom/cumulative parameters and boundary time |
| Refresh | source freshness, schedule, manual refresh rule, stale-data handling |
| Quality | null/range/duplicate/freshness/referential rules and issue owner |
| Fill mode | system extract, manual fill, Excel upload, review, return/rework |

Semantic-layer and AI-data rules:

- Prefer approved metric/dimension semantics over free-form SQL generation.
- Prefer ontology object/link/action semantics when the product must connect
  data to operational decisions or writeback actions.
- AI data answers must cite indicator IDs, object/asset IDs, period, scope,
  source freshness, and caliber/model version.
- AI must not bypass permission, row/column masks, source freshness warnings,
  lineage gaps, sensitivity labels, or caliber/model version constraints.
- Data agents must declare tool scope, write scope, human gate, evaluation
  cases, trace fields, fallback, and rollback before production use.

This section is the authoritative reporting/data-product contract. No extra
reporting reference file is required, except the load-on-demand
`domain-data-mart.md` domain module for data mart, BI, reporting, and fill-in
products.

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

This section is the authoritative low-code/workflow automation contract. When a
prototype or workflow is repeatedly patched/generated by scripts, require an
artifact manifest and reproducible build command in the PRD delivery package.

## Mobile, Multi-Surface, And Global Delivery

Trigger for H5, app, mini-program, field staff, weak network, PC+mobile consistency, overseas launch, cross-border data, multi-language, or regional model routing.

IA Skeleton linkage:

When mobile is in scope, mobile views must appear in the IA Skeleton (Stage
3.5). Mobile view_id format: `Mxx-Vyy-mobile` (e.g., `M01-V02-mobile`). If a
mobile view reuses a desktop view's business logic but has different layout,
state `platform: mobile` in the view entry and describe only the differing
regions. Do not skip Stage 3.5 for mobile-only modules.

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

This section is the authoritative mobile, multi-surface, and global delivery
contract. No separate mobile reference file is required.

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

This section is the authoritative readiness, release, package, and retirement
contract. No separate readiness or acceptance-gate reference file is required.

## Domain Modules And Templates

Domain modules remain load-on-demand assets:

- new industry/company domain: start from `domain-module-template.md`;
- traffic safety: `domain-traffic.md`;
- CRM: `domain-crm.md`.
- AI-native product / agentic system: `domain-ai-native.md`.
- higher-education informationization: `domain-education-it.md`.
- medical / hospital IT: `domain-medical-hospital-it.md`.
- data mart / BI / reporting / fill-in: `domain-data-mart.md`.

Traffic/transport domain note: when traffic safety, transport supervision, or
government transportation data products are in scope, the domain module must
include a standards corpus register covering applicable national law/policy,
GB/GB-T national standards, JT/JT-T and JTG transport industry standards,
GA/public-safety interfaces where relevant, provincial/local DB or DBxx/T
standards, group standards (`T/...`), and customer/enterprise rules. Do not
hardcode a standard as active without issuer, region, effective date, version,
and applicability.

CRM domain note: when CRM scope spans marketing, sales, service, customer
success, partner/channel, contract/payment, or product-feedback loops, use the
CRM domain module to lock lifecycle states, SLA/response tasks, Customer 360,
permission layers, and AI suggestions as supporting behavior.

Templates:

- light PRD: `templates/prd-light-template.md`;
- Human-First Full PRD profile: `templates/human-first-prd-template.md`;
- AI-Coding Full PRD profile: `templates/ai-coding-prd-template.md`;
- global field dictionary: `templates/field-dictionary-template.md`;
- readiness checklist: `templates/system-readiness-checklist-template.md`;
- post-launch review: `templates/post-launch-review-template.md`.

External lifecycle and PM frameworks are upstream evidence, not runtime
dependencies. If a user brings Product-Manager-Skills, Spec Kit, to-prd style
PRDs, market sizing, opportunity trees, roadmaps, or issue lists, register them
as source artifacts and map them into `delivery-core.md` lifecycle stages. Do
not load or reproduce their complete process unless the user explicitly asks to
run that external framework.

Composition with external skills:

- Use AI Delivery Spec for product-side truth: PRD, IA, prototype testability,
  acceptance, lifecycle gates, and coding-agent handoff.
- Use external brainstorming skills only for divergent ideation before product
  shape exists; then convert the result into Opportunity Shaping evidence.
- Use external frontend-design/UIUX/design-system skills for visual language
  when prototype style, brand, or component-system quality is in scope.
- Use spec-kit after the product specification is stable, mainly for
  engineering plan/tasks/implementation convergence. Do not let spec-kit task
  files replace the Human-First or AI-Coding PRD.

Strategy/discovery guidance lives in `delivery-core.md`. This file only adds
advanced triggers and contracts.

## Coding Agent Compatibility

Trigger when the PRD/prototype will be consumed by a coding agent, or the user
asks to generate `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, `.cursorrules`, or
test stubs from acceptance criteria.

Source asset: `coding-agent-compat.md`.

## Repository Cleanliness Rule

This repository intentionally keeps only runtime entrypoints, current templates,
domain modules, coding-agent compatibility, realtime contract, scripts, and
examples. Historical split protocols were consolidated into this file or
`delivery-core.md`; do not re-add one-off reference files unless they pass the
evolution rule: at least three real projects, two domains, and one validator
change need the new file.
