# AI + Data Product System Domain Module

Use this replaceable domain module for AI+Data platforms, data marts, data warehouses, lakehouse products, BI, ChatBI, Data Agent, semantic/ontology products, metric platforms, dashboards, reporting, fill-in systems, data governance, data catalog, lineage, retrieval/search, and data analysis products. A replacement `domain-*.md` must preserve the same 14 section headings used here and in `domain-module-template.md`.

This module is intentionally broader than a data mart checklist. It treats data products as an end-to-end system: source acquisition -> processing -> governance -> storage/retrieval -> semantic/ontology layer -> analytics/BI -> AI agents -> action/decision loop -> operations/evaluation.

## Contents

- Domain Purpose
- Vocabulary
- Aggregates and Entities
- Domain Events
- State Machines
- Metric / Indicator Governance
- AI Context Sources
- Content / Knowledge Assets
- Core Workflows
- Role Path Patterns
- UI / Mobile Patterns
- Policy / Privacy Constraints
- Domain Test Scenarios
- Acceptance Checklist

## Domain Purpose

AI+Data PRDs must specify how raw, distributed, and often untrusted data becomes governed, explainable, searchable, analyzable, and actionable. The product contract is not just a dataset, report, or agent conversation. It is the full operating chain:

```text
multi-source data -> ingest/sync -> clean/standardize -> govern/catalog/lineage
-> store/index/retrieve -> semantic model / ontology -> BI / analysis / report
-> Data Agent / ChatBI / insight -> workflow action / decision -> monitor/evaluate
```

Use this module when any of these capabilities are in scope:

- multi-source connectors, file upload, API sync, CDC, streaming, batch jobs, or manual fill-in;
- data cleaning, transformation, entity resolution, standardization, deduplication, quality checks, or exception handling;
- metadata, catalog, lineage, RBAC/ABAC, row/column permissions, privacy classification, approval, audit, or data asset lifecycle;
- data lake, warehouse, lakehouse, ODS/DWD/DWS/ADS, OLAP cube, search index, vector index, cache, or retrieval service;
- semantic model, metric layer, dimension dictionary, business glossary, ontology object/link/action types, or data product API;
- dashboard, self-service analysis, report template, filling task, export, embedded analytics, or operational cockpit;
- Data Agent, ChatBI, NL2SQL, NL2Metrics, insight generation, anomaly attribution, report writing, or action agent.

## Vocabulary

| Term | Meaning | PRD Requirement |
|---|---|---|
| 数据源 / Data source | database, file, API, stream, SaaS app, manual fill-in, external data | ownership, credential, schema, cadence, SLA, backfill, permission |
| 接入 / Ingestion | batch, CDC, stream, file import, API pull/push, manual upload | connector, schedule, idempotency, retry, failure quarantine |
| 清洗 / Cleaning | normalize, type cast, dedupe, map dictionary, repair, standardize | rule, exception queue, owner, audit, sample evidence |
| 治理 / Governance | catalog, metadata, lineage, quality, standard, security, lifecycle | owner, policy, approval, lineage, quality score, audit |
| 存储 / Storage | lake, warehouse, lakehouse, mart, OLAP, cache | model layer, partition, retention, cost, refresh |
| 检索 / Retrieval | SQL, OLAP, search, vector search, API, materialized view | latency, freshness, permission, ranking, citations |
| 语义层 / Semantic layer | business mapping over tables, fields, metrics, dimensions, synonyms | model version, field descriptions, relations, approved query scope |
| 本体 / Ontology | object types, properties, links, actions, rules, operational semantics | object/link/action contract, write guard, policy, audit |
| 指标 / Metric | stable measurable business concept | layer, formula, unit, period, source, owner, quality rule |
| 维度 / Dimension | grouping, filter, drill, hierarchy, permission scope | dictionary, value source, hierarchy, scope rule |
| ChatBI | conversational analytics over governed semantic data | semantic context, permission, answer citation, query trace, fallback |
| Data Agent | agent that reads, reasons, analyzes, or acts over governed data | tools, allowed sources, write scope, human gate, evaluation |
| sys column | system-extracted report/fill field | source, refresh, lock, quality rule |
| ext column | human-filled report/fill field | control, validation, submit/review state |

## Aggregates and Entities

| Layer | Aggregates / Entities | Key Invariants |
|---|---|---|
| Source and ingestion | DataSource, Connector, SyncJob, StreamTopic, FileImport, Credential, BackfillTask | every ingest path has owner, auth, schema, cadence, idempotency, retry, and failure quarantine |
| Processing and quality | Pipeline, TransformStep, CleanRule, QualityRule, ExceptionRecord, MasterDataMap | raw data is never silently overwritten; fixes are versioned and auditable |
| Governance and catalog | DataAsset, Metadata, BusinessTerm, LineageEdge, Policy, Approval, AuditLog | each trusted asset has owner, classification, lineage, access policy, and lifecycle state |
| Storage and retrieval | LakeTable, WarehouseTable, MartTable, OLAPCube, SearchIndex, VectorIndex, Cache | consumers know freshness, retention, query limits, and permission scope |
| Semantic and ontology | SemanticModel, Dataset, Metric, Dimension, ObjectType, LinkType, ActionType, Rule | business questions resolve through approved semantics before raw SQL or tool calls |
| Analytics and reporting | Dashboard, Chart, AnalysisSession, ReportTemplate, ReportTask, FillSubmission, ExportJob | visible numbers use declared metric, dimension, period, scope, and caliber version |
| AI agent runtime | Agent, Tool, Prompt, EvalSet, Trace, Conversation, Insight, Recommendation, WritebackAction | AI reads and acts only within governed tools, permissions, confidence, and human gates |
| Operations | SLA, FreshnessCheck, CostBudget, Incident, RollbackPlan, UsageMetric | production trust is monitored with freshness, quality, latency, cost, adoption, and failure metrics |

## Domain Events

| Event | Trigger | Consumers |
|---|---|---|
| DataSourceConnected | connector or credential is approved | catalog, pipeline, permission review |
| SchemaChanged | source table/API/file schema changes | lineage, semantic model, tests, affected dashboards/agents |
| IngestionFailed | sync job fails or exceeds retry policy | ops, data owner, downstream freshness warnings |
| QualityRuleFailed | quality check violates threshold | exception queue, dashboard warning, release gate |
| DataAssetPublished | curated data asset becomes trusted | semantic model, BI, ChatBI, APIs |
| LineageUpdated | transform/source dependency changes | governance, impact analysis, audit |
| MetricCaliberChanged | metric business or technical definition changes | templates, dashboards, exports, agents, history markers |
| OntologyActionSubmitted | user/agent writes object, link, or workflow state | audit, policy guard, downstream operational app |
| SemanticModelPublished | dataset/metric/dimension/relationship model changes | ChatBI, self-service analysis, report builder |
| ChatBIQuestionAnswered | natural-language answer is generated | trace, eval, feedback, usage analytics |
| AgentInsightGenerated | agent produces insight/recommendation | human review, dashboard, task/workflow |
| AgentWritebackBlocked | agent tries disallowed write or low-confidence action | safety audit, fallback, human review |
| ReportAggregationCompleted | report/fill data is merged and calculated | dashboard, export, quality checks |
| DataProductRetired | asset/model/report/agent is deprecated | consumers, migration plan, retention/deletion |

## State Machines

Data source:

```text
draft -> connected -> syncing -> active -> degraded -> suspended -> retired
syncing -> failed -> syncing
```

Pipeline:

```text
draft -> test_run -> scheduled -> running -> succeeded
running -> failed -> retrying -> running
scheduled -> paused -> scheduled
```

Data asset:

```text
raw -> profiled -> curated -> certified -> deprecated -> retired
curated -> blocked_by_quality -> curated
```

Semantic model / ontology:

```text
draft -> reviewed -> published -> versioned -> deprecated
published -> rollback_pending -> published
```

Report/fill task:

```text
draft -> created -> collecting -> aggregating -> completed -> archived
collecting -> cancelled
aggregating -> failed -> aggregating
```

Data agent:

```text
draft -> evaluated -> pilot -> production -> degraded -> disabled -> retired
pilot/production -> rollback_pending -> previous_version
```

Every state transition must define role/tool permission, data guard, quality/freshness guard, audit event, notification, retry/idempotency, and rollback behavior.

## Metric / Indicator Governance

AI+Data PRDs must separate data correctness from business meaning. For every trusted metric, specify all layers below.

### Indicator Layering

| Layer | Definition | Required Fields |
|---|---|---|
| 原子指标 | base measurable fact from a trusted source | source table/API, field, aggregation, unit, owner |
| 派生指标 | atomic metric plus dimension/filter/period | base metric, dimension, filter, statistical period |
| 复合指标 | expression over multiple metrics | dependency graph, formula, recalculation rule |
| 目标/阈值 | planned target, warning line, assessment rule | owner, period, exception rule, effective time |

### Caliber Dual Track

| Field | Required Content |
|---|---|
| 指标编码 | stable ID such as `IND-001` |
| 业务定义 | plain-language meaning, inclusion/exclusion, boundary time |
| 技术计算逻辑 | SQL, MQL, DAX, formula, semantic expression, or rule |
| 统计周期 | day/week/month/quarter/custom/cumulative and time-zone/boundary |
| 数据来源 | source system, ODS/DWD/DWS/ADS/API/table/field |
| 维度范围 | dimensions, hierarchies, allowed drill paths |
| 权限范围 | tenant/org/region/enterprise/row/column/action |
| 质量规则 | null/range/duplicate/freshness/referential/anomaly |
| 负责人 | business owner, data owner, technical owner |
| 版本 | effective time, superseded version, migration note |

### Dimension Dictionary

| Dimension ID | Name | Value Source | Drill Path | Related Metrics | Scope Rule |
|---|---|---|---|---|---|
| DIM-AREA | 区域 | region master data | province -> city -> district | enterprise_count, risk_count | user.home_region subtree |

### Ontology And Semantic Contract

| Contract | Required Content |
|---|---|
| Object type | business entity/event, properties, owner, source mapping |
| Link type | object relationship, cardinality, join/source field, lifecycle |
| Action type | user/agent operation, parameters, guard, side effect, audit |
| Query type | approved read/query pattern, filters, row/column scope |
| Rule | quality, policy, state, permission, or writeback condition |
| Synonym/glossary | business terms, aliases, forbidden ambiguous terms |

### Caliber Change Propagation

| Change | Required Impact Handling |
|---|---|
| source schema changes | list affected pipelines, metrics, semantic models, dashboards, agents, exports |
| metric caliber changes | preview affected templates, reports, dashboards, AI answers, and historical data |
| dimension values change | refresh filters, drill paths, permission scopes, and cached queries |
| ontology action changes | verify downstream state transitions, audit, side effects, and agent write scope |
| history data recalculates | keep old/new version markers and user-facing explanation |

## AI Context Sources

Data agents and ChatBI must be grounded in governed context rather than raw table guessing.

| AI Scenario | Required Context | Guard |
|---|---|---|
| ChatBI / NL2SQL | semantic model, metric/dimension dictionary, synonyms, query examples, permission scope | generate constrained query plan and cite metric/source; no arbitrary cross-source join unless approved |
| NL2Metrics / NL2Semantics | approved metrics, dimensions, object types, business terms | resolve question to metric/dimension/object first, then query |
| Data engineering assistant | source schema, lineage, pipeline templates, quality rules | propose pipeline/SQL; human approves before production write |
| Data governance agent | catalog, classification, policy, lineage, access logs | recommend policy/owner; no silent permission grants |
| Data quality agent | profiles, anomaly baselines, exception history | raise issue/recommend fix; preserve raw data and audit |
| Insight / attribution agent | time series, dimension drill path, benchmark, quality/freshness state | label correlation vs cause; require evidence for causal claims |
| Report-writing agent | certified metrics, report structure, source citations, audience | generated narrative cites metric IDs and periods |
| Action / decision agent | ontology actions, workflow state, write scope, human gate | draft or route tasks unless explicit production write permission exists |

Minimum AI data runtime contract:

```yaml
data_agent_contract:
  agent_id:
  use_case: chatbi | insight | data_quality | data_engineering | governance | report_writer | action_agent
  allowed_sources: [semantic_model, catalog, lineage, certified_dataset, ontology]
  forbidden_sources: [raw_sensitive_table, unapproved_export]
  tool_scope: [sql_query, semantic_query, vector_search, catalog_lookup, lineage_lookup, create_task]
  write_scope: none | draft_only | workflow_task | ontology_action
  permission_mode: inherit_user_scope | service_role_with_policy
  citation_required: true
  freshness_required: true
  confidence_threshold:
  human_gate: before_write | before_publish | exception_only | none_with_reason
  eval_sets: [golden_questions, permission_denial, stale_data, ambiguous_terms, adversarial_queries]
```

## Content / Knowledge Assets

| Asset | Required Metadata |
|---|---|
| Source catalog | source name, system, credential owner, schema, cadence, SLA, classification |
| Pipeline registry | source, transform steps, schedule, retry, backfill, failure owner |
| Data asset catalog | asset ID, layer, owner, certification, lineage, access policy |
| Quality rule library | rule ID, severity, threshold, exception path, owner |
| Business glossary | term, synonym, definition, domain, owner, ambiguity guard |
| Semantic model | dataset, logical tables, relationships, metric/dimension bindings, examples |
| Ontology model | object/link/action/query/rule types, write guards, side effects |
| Metric dictionary | ID, name, layer, formula, unit, source, period, version |
| Dimension dictionary | ID, values, hierarchy, value source, scope rule |
| Report/template library | purpose, columns, sys/ext split, filters, snapshot/version |
| Agent knowledge pack | instructions, examples, refusal rules, evaluation cases, citations |
| Runbook | freshness, incident, rollback, cost, access review, retirement |

## Core Workflows

| Workflow | Minimum Steps |
|---|---|
| multi-source onboarding | register source -> classify -> approve credential -> profile schema -> test sync -> publish source asset |
| data pipeline delivery | define transform -> run sample -> validate quality -> schedule -> monitor -> backfill/rollback |
| governance certification | assign owner -> classify sensitivity -> define policy -> verify lineage -> certify asset |
| semantic/ontology modeling | define objects/metrics/dimensions/actions -> map source -> review -> publish -> version |
| BI/dashboard delivery | choose certified data -> bind metric/dimension -> design drill/filter -> verify permission/freshness -> publish |
| report/fill-in delivery | create template -> mark sys/ext -> set scope/period -> collect fill -> aggregate -> export/audit |
| ChatBI enablement | prepare semantic model -> add glossary/examples -> evaluate golden questions -> authorize users -> monitor feedback |
| data agent launch | define tools/write scope -> evaluate -> pilot -> monitor traces -> rollback/iterate |
| insight-to-action loop | detect signal -> explain/cite -> human confirm -> create task/action -> track outcome |
| retirement | inventory consumers -> migrate -> freeze writes -> export/delete -> close audit |

## Role Path Patterns

| Role | Main Job | Critical Permissions |
|---|---|---|
| Sponsor / owner | approve business value, risk, budget, launch | release scope, risk acceptance |
| 数据产品经理 | shape scenarios, metric value, lifecycle, acceptance | PRD, priority, evaluation |
| 数据架构师 | design source-to-serving architecture | model/layer decisions |
| 数据工程师 | build ingestion, processing, storage, quality | pipelines, schema, backfill |
| 数据治理负责人 | own catalog, lineage, policy, quality | certification, access review |
| 业务负责人 | approve metric definitions and exception rules | caliber/target decisions |
| 分析师 | build dashboards, analysis paths, reports | semantic assets, dashboard publish |
| 运营/监管人员 | create report/fill tasks, monitor progress, act on insights | report scope, reminders, returns |
| 企业/一线填报人 | submit ext fields and correct returned data | own tasks and own history |
| AI/算法工程师 | define agent runtime, eval, fallback, observability | prompts, tools, eval, traces |
| 管理层/查看者 | ask questions, inspect dashboards, decide actions | authorized metrics and drill paths |

## UI / Mobile Patterns

| Surface | Pattern | Required States |
|---|---|---|
| source connection | connector list, credential drawer, schema preview, sync history | draft/connected/syncing/failed/degraded |
| pipeline builder | DAG/step list, sample output, quality panel, run log | draft/test_run/scheduled/running/failed |
| catalog/governance | asset card, owner, classification, lineage graph, access panel | raw/curated/certified/deprecated |
| semantic/ontology manager | object/metric/dimension/action model, examples, publish diff | draft/reviewed/published/versioned |
| BI/dashboard | metric cards, filters, drill path, freshness marker, export | loading/empty/no_permission/stale/error |
| analysis workspace | drag/drop dimensions, charts, pivot, attribution, annotations | editing/saved/shared/locked |
| ChatBI | question box, semantic match, generated query, answer, citations, feedback | thinking/answered/ambiguous/denied/stale |
| Data Agent console | task/instruction, tool trace, confidence, human review, rollback | draft/evaluated/pilot/production/degraded |
| fill-in mobile | task card, sys locked values, ext editable cells, save/submit | filling/submitted/returned/overdue/offline |

## Policy / Privacy Constraints

- Apply row-level, column-level, action-level, and agent-tool-level permissions before query generation, aggregation, export, or writeback.
- Do not let agents bypass semantic model, source freshness, lineage, sensitivity labels, or user data scope.
- Record who changed source schemas, pipelines, metrics, dimensions, ontology actions, permissions, prompts, eval sets, and report scopes.
- Keep test/shadow records out of KPI, dashboard, BI, ChatBI, agent eval, and exported reports by default.
- For sensitive or regulated data, define masking, desensitization, retention, deletion/export approval, access review, and audit retention.
- For ontology/action agents, define human accountability for consequential state changes.
- For public-sector delivery, specify private deployment, network boundaries, domestic database/OS constraints, and external model/data-exit restrictions when applicable.

## Domain Test Scenarios

| Scenario | Must Verify |
|---|---|
| source schema change | impacted pipelines, semantic models, metrics, dashboards, agents, and exports are listed |
| ingestion retry/backfill | duplicate records are not created and failed batches can replay |
| cleaning/dedup | raw value is preserved; corrected value is versioned and auditable |
| quality failure | downstream dashboards/agents show stale/quality warning or block strict use |
| lineage trace | metric -> semantic model -> pipeline -> source field can be traced |
| permission denial | unauthorized user/agent cannot query, export, or infer restricted rows/columns |
| ChatBI ambiguous question | asks clarification or uses approved synonym; does not invent metric |
| ChatBI stale data | answer cites freshness or refuses when strict freshness is required |
| data agent writeback | low-confidence or disallowed ontology action is blocked and audited |
| report/fill sys/ext split | sys fields are locked/refreshed; ext fields validate, submit, return, audit |
| dashboard drill | filter/drill respects dimension hierarchy and row-scope permissions |
| retirement | consumers are notified, migration/retention is completed, old asset is blocked |

## Acceptance Checklist

- [ ] Every data source has owner, credential, schema, sync mode, cadence, SLA, backfill, retry, and classification.
- [ ] Every pipeline has transform rules, quality gates, idempotency, sample evidence, lineage, and failure owner.
- [ ] Every curated asset has catalog metadata, certification state, sensitivity label, access policy, and consumer list.
- [ ] Every storage/retrieval path declares freshness, latency, retention, cost, permission, and index/materialization strategy.
- [ ] Every semantic/ontology model defines objects/metrics/dimensions/actions/relations, examples, versioning, and rollback.
- [ ] Every metric has ID, owner, layer, business definition, technical expression, source, period, unit, and quality rule.
- [ ] Every dashboard/report shows source freshness, caliber version, permission state, empty/error state, and export rule.
- [ ] Every report/fill workflow declares sys/ext fields, validation, submit/review/return state, deadline, and audit.
- [ ] Every Data Agent/ChatBI feature has allowed sources/tools, permission inheritance, citations, freshness handling, refusal rules, eval sets, and human gate.
- [ ] Every insight-to-action flow identifies who is accountable for final business decision and what the agent may not write.
- [ ] Acceptance tests cover ingestion, cleaning, governance, semantic/ontology, BI, ChatBI, agent, permission, freshness, export, and retirement paths.
