# AI + Data Product System Domain Module

Source authority and freshness metadata: `references/domains/domain-sources.yaml`.
Coverage and maturity: `references/domain-coverage.yaml`.

Use this replaceable domain module for data-resource inventory and registration, data products and services, public-data authorization operations, trusted data spaces, AI-ready and high-quality datasets, data labeling, training/evaluation/preference data, AI+Data platforms, warehouses/lakehouses, governance, catalog, lineage, semantic/ontology products, BI, ChatBI, Data Agents, reporting, retrieval, and operational data applications. A replacement domain module must preserve the same section headings used here and in the maintainer domain template.

This module is intentionally broader than a data mart checklist. It treats data products as an end-to-end system: source acquisition -> processing -> governance -> storage/retrieval -> semantic/ontology layer -> analytics/BI -> AI agents -> action/decision loop -> operations/evaluation.

## Contents

- Domain Purpose
- First-Principles Domain Lens
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
- Evaluation Profile
- Acceptance Checklist

## Domain Purpose

AI+Data PRDs must specify how raw, distributed, and often untrusted data becomes governed, explainable, searchable, analyzable, and actionable. The product contract is not just a dataset, report, or agent conversation. It is the full operating chain:

```text
scenario demand -> source/right/use proof -> acquire/ingest -> clean/label/standardize
-> govern/catalog/lineage -> register/certify -> productize and price
-> authorize/digital contract/trusted use -> settle/evaluate
-> BI/API/AI training or action -> application/model feedback -> iterate or retire
```

Use this module when any of these capabilities are in scope:

- multi-source connectors, file upload, API sync, CDC, streaming, batch jobs, or manual fill-in;
- data cleaning, transformation, entity resolution, standardization, deduplication, quality checks, or exception handling;
- metadata, catalog, lineage, RBAC/ABAC, row/column permissions, privacy classification, approval, audit, or data asset lifecycle;
- data lake, warehouse, lakehouse, ODS/DWD/DWS/ADS, OLAP cube, search index, vector index, cache, or retrieval service;
- semantic model, metric layer, dimension dictionary, business glossary, ontology object/link/action types, or data product API;
- dashboard, self-service analysis, report template, filling task, export, embedded analytics, or operational cockpit;
- Data Agent, ChatBI, NL2SQL, NL2Metrics, insight generation, anomaly attribution, report writing, or action agent;
- public-data resource registration, authorized operation, product/service disclosure, pricing, settlement, supervision, or exit;
- data-property registration, source/right evidence, transfer/change/renewal/cancellation, objection, credential, or cross-platform recognition;
- dataset collection, cleaning, deduplication, labeling, de-identification, train/validation/test split, SFT, preference/DPO/RLHF, model evaluation, contamination control, or application-feedback iteration.

### Evidence-Bounded 2026-2028 Planning Horizon

Treat these as planning directions supported by current policy and standards, not
as mandatory features for every project.

| Direction | Likely Product Shift | Requirement Guard |
|---|---|---|
| nationwide registration and interoperability | resource/property/product credentials become reusable trust evidence | registration type, applicant, source proof, review, objection, validity, change and cancellation remain distinct |
| trusted circulation infrastructure | one-off file exchange shifts toward governed use inside data spaces | participant identity, purpose, digital contract, usage control, audit, revocation and exit are explicit |
| public-data market operations | catalog publication shifts toward scenario-based authorized products/services | implementing/operating roles, authorization scope, cost/revenue, price, disclosure, supervision and no-raw-data-market rule are explicit |
| high-quality industry datasets | data governance extends from BI correctness to AI fitness | intended model/scenario, data rights, coverage, labeling, split, quality, bias, contamination and benchmark are versioned |
| model-data-scene flywheel | dataset delivery becomes continuous supply and evaluation | model/evaluation/app feedback creates traceable dataset changes without polluting held-out tests |
| asset and value management | registration, accounting, valuation and financing become connected but separate workflows | no credential or appraisal automatically becomes accounting recognition, ownership judgment, or guaranteed value |

## First-Principles Domain Lens

AI+Data product judgment starts from trusted decision flow, not from a report,
warehouse, or chatbot label.

| Lens | Data Product Question | Acceptance Signal |
|---|---|---|
| Data supply chain | Which source becomes trusted data, at what freshness and quality? | source, sync, quality, lineage, and owner are explicit |
| Semantic truth | Which metrics, dimensions, entities, and ontology actions users rely on? | semantic/ontology version and permission scope are governed |
| Decision loop | What analysis, fill-in, alert, or action changes after insight? | BI/ChatBI/Data Agent output links to workflow or accountable decision |
| Reversibility | Which data or ontology writes can be corrected safely? | human gate, audit, rollback, and recalculation scope are defined |
| Evidence | Can every answer, metric, dataset and generated report cite source/caliber? | citations, query trace, dataset card and quality status are visible |
| Rights and purpose | Who may process which data for which purpose and period? | source/right evidence, lawful basis, authorization scope, use controls and expiry are linked |
| Market operation | What product/service is delivered without releasing uncontrolled raw data? | product contract, service level, price/settlement, disclosure, supervision and exit are explicit |
| AI fitness | Does the dataset improve the intended model and scenario rather than merely look clean? | task coverage, label agreement, split isolation, benchmark result and model feedback are versioned |
| Value proof | What measurable public, operational or commercial outcome justifies continued supply? | beneficiary, baseline, outcome metric, cost/revenue and attribution limits are declared |

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
| 数据资源登记 / Resource registration | public-data resource/product/service inventory and disclosure record | registration object, provider, catalog, update, review, credential and change |
| 数据产权登记 / Property registration | standardized evidence for data-resource or data-product rights and changes | applicant, source/right proof, initial/transfer/change/renewal/cancellation, objection and validity |
| 授权运营 / Authorized operation | approved operation of scoped public-data resources through an implementing and operating arrangement | plan, decision, agreement, resource/product scope, term, disclosure, supervision and exit |
| 数据产品与服务 / Data product or service | controlled data result, API, model-ready dataset, verification or computing service delivered for a purpose | inputs, transformations, quality, consumer, usage rule, SLA, price and liability |
| 数字合约 / Digital contract | machine-enforceable purpose, permission, obligation and usage-control agreement | parties, data/product, purpose, actions, period, count, location, revocation and evidence |
| 高质量数据集 / High-quality dataset | scenario-oriented, governed dataset that can measurably support model development or evaluation | intended use, provenance, rights, coverage, labels, splits, quality, benchmark and version |
| 训练/验证/测试数据 | separated data partitions for fitting, tuning and unbiased evaluation | split rule, isolation, leakage/contamination check and release lineage |
| 偏好数据 / Preference data | ranked/comparison/critique data used for preference optimization or reward learning | task/source, annotator policy, agreement, safety taxonomy, model/version and bias review |
| 数据卡 / Dataset card | human- and machine-readable evidence for one dataset version | owner, license/rights, collection, processing, population, gaps, risks, metrics and changes |
| 数据资源会计 / Data-resource accounting | accounting treatment based on applicable standards and economic substance | purpose, cost basis, recognition decision, useful life, impairment and disclosure; separate from registration/valuation |
| sys column | system-extracted report/fill field | source, refresh, lock, quality rule |
| ext column | human-filled report/fill field | control, validation, submit/review state |

## Aggregates and Entities

| Layer | Aggregates / Entities | Key Invariants |
|---|---|---|
| Source and ingestion | DataSource, Connector, SyncJob, StreamTopic, FileImport, Credential, BackfillTask | every ingest path has owner, auth, schema, cadence, idempotency, retry, and failure quarantine |
| Processing and quality | Pipeline, TransformStep, CleanRule, QualityRule, ExceptionRecord, MasterDataMap | raw data is never silently overwritten; fixes are versioned and auditable |
| Governance and catalog | DataAsset, Metadata, BusinessTerm, LineageEdge, Policy, Approval, AuditLog | each trusted asset has owner, classification, lineage, access policy, and lifecycle state |
| Rights and registration | SourceEvidence, RightEvidence, RegistrationApplication, RegistrationReview, Objection, Credential, RegistrationChange | registration preserves applicant, object, evidence, reviewer, validity and every change without implying accounting recognition |
| Market and trusted circulation | AuthorizationPlan, OperatingAgreement, DataProduct, DataService, Participant, DigitalContract, UsagePolicy, Settlement, Disclosure, ExitRecord | every use is bounded by participant, product, purpose, action, term, usage evidence, revocation and liability |
| AI data supply | Dataset, DatasetVersion, Sample, LabelSchema, AnnotationTask, Annotator, Split, DatasetCard, Benchmark, ModelFeedback | every sample/version preserves provenance and right basis; held-out evaluation is isolated from training and feedback |
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
| RegistrationCredentialIssued | a registration application passes review and objection handling | catalog, credential registry, applicant, authorized consumers |
| RegistrationChangedOrCancelled | transfer/change/renewal/cancellation becomes effective | credentials, contracts, consumers, accounting/legal review |
| AuthorizationAgreementEffective | approved resource/product/service scope becomes usable | operating platform, usage control, disclosure, supervision |
| UsagePolicyViolated | a participant exceeds purpose, scope, action, quantity, location or term | block/revoke, incident, audit, notification, liability |
| DatasetVersionReleased | a governed training/evaluation/preference dataset passes release gates | model teams, registry, benchmark, lineage and consumers |
| DatasetContaminationDetected | held-out or prohibited data is found in training/feedback inputs | release block, affected models, re-split/retrain decision and audit |
| ModelFeedbackAccepted | evaluated application feedback is approved as a dataset change | sampling backlog, label review, new dataset version; never mutate the old version |

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

    draft -> evaluated -> pilot -> production -> degraded -> disabled -> retired
    pilot/production -> rollback_pending -> previous_version

Data registration:

    draft -> submitted -> accepted_for_review -> reviewing -> public_notice -> issued -> changed/renewed/transferred -> cancelled/expired
    submitted/reviewing/public_notice -> returned/rejected
    public_notice -> objection_pending -> reviewing

Authorization and trusted use:

    planned -> approved -> contracted -> active -> suspended -> revoked/expired -> exited
    active -> violation_pending -> active/revoked

AI dataset:

    planned -> collecting -> processing -> labeling -> quality_review -> released -> in_use -> superseded -> retired
    quality_review -> rejected -> processing/labeling
    released/in_use -> contamination_hold -> corrected_new_version

Every state transition must define role/tool permission, data/right/purpose guard, quality/freshness guard, audit event, notification, retry/idempotency, affected consumers, and rollback or correction behavior.

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

### AI Dataset Supply Contract

Do not collapse collection, annotation, training, evaluation and feedback into one
dataset status. For every released dataset version, specify:

| Contract Area | Required Content |
|---|---|
| purpose | target industry, task, model family, application scenario, excluded uses and accountable owner |
| provenance and rights | source, collection method/time, lawful/right basis, license/contract, personal/sensitive data treatment and downstream restrictions |
| population and coverage | unit of observation, time/region/device/language/domain coverage, rare/edge cases, known gaps and representativeness limits |
| processing | extraction, cleaning, deduplication, de-identification, synthesis/augmentation, filtering and human/automated steps |
| labeling | schema/version, instructions, annotator qualifications, agreement/adjudication, acceptance sampling and rejected work |
| splits | train/validation/test/preference/benchmark purpose, isolation key, leakage and contamination checks |
| quality and fitness | intrinsic quality plus model/scenario benchmark, threshold, failure slices, bias/safety tests and reviewer |
| release and lineage | immutable version, parent/derived datasets, sample hash, code/rule version, model consumers and retirement |
| feedback | application/evaluation signal, sampling criteria, human approval, label correction and target next version |
| value | public/operational/commercial outcome, baseline, cost, attributable benefit and renewal/exit decision |

SFT, preference optimization, DPO, reward learning and reinforcement-learning
datasets require separate schemas and quality evidence. Production conversations
or user feedback never enter training automatically; collection purpose,
authorization, filtering, approval and versioned lineage must be explicit.

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
| Registration dossier | applicant/object, source and right evidence, review/public notice/objection, credential, validity and lifecycle history |
| Authorization portfolio | approved plan, agreement, resource/product/service list, participant, purpose, usage policy, disclosure, evaluation and exit |
| Digital-contract registry | parties, product, permitted/prohibited use, count/time/location, enforcement, revocation and evidence |
| Dataset registry/card | version, intended use, provenance/right basis, population, processing, labels, splits, quality/benchmark, risks and consumers |
| Labeling specification | task/schema/version, instructions, examples, annotator qualification, agreement, adjudication and acceptance sampling |
| Model-data feedback ledger | model/application/eval version, failure slice, accepted feedback, dataset change, retraining decision and result |
| Accounting/value evidence | economic purpose, costs, recognition judgment, disclosures, valuation assumptions and restrictions kept distinct from registration |
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
| public-data resource registration | inventory object -> prove provider/catalog/update/quality -> submit -> review/correct -> issue -> change/cancel |
| data-property registration | choose type -> prove source/right boundary -> submit -> accept/review -> public notice/objection -> issue -> transfer/change/renew/cancel |
| authorized operation | justify scenario/value -> approve plan -> select operator -> sign agreement -> register resource/product/service -> controlled delivery -> disclose/supervise/evaluate -> renew/exit |
| trusted data use | onboard participant -> verify identity/qualification -> negotiate digital contract -> authorize purpose/action -> execute in controlled environment -> meter/audit -> settle/revoke |
| high-quality dataset delivery | define model/scenario -> inventory rights/data gaps -> collect/process -> label/adjudicate -> split/isolate -> benchmark -> release card/version -> monitor |
| model-data-scene iteration | detect model/application failure slice -> approve feedback sample -> relabel/augment -> release new dataset -> retrain/evaluate -> compare outcome |
| data-resource accounting support | identify economic purpose/cost -> preserve evidence -> authorized accounting judgment -> disclosure/impairment review; never infer recognition from registration |
| insight-to-action loop | detect signal -> explain/cite -> human confirm -> create task/action -> track outcome |
| retirement | inventory consumers/contracts/models -> revoke/migrate -> freeze writes/use -> retain/export/delete -> close registration/accounting/audit |

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
| 数据提供方/持有方 | prove source, quality, update and permitted use | register, authorize, correct and revoke owned/controlled scope |
| 数据登记申请人/代理人 | submit truthful dossier and manage lifecycle | initial/transfer/change/renewal/cancellation within authority |
| 登记机构审查人员 | accept, review, publicize, handle objections and issue credentials | independent review, reasoned return/reject, audit |
| 实施机构/主管部门 | approve public-data operation plan and supervise | scope, operator selection, disclosure, evaluation and exit |
| 运营机构 | develop and operate approved products/services without exceeding scope | controlled processing, product/service delivery, cost/revenue and audit |
| 数据空间运营方 | onboard participants and enforce shared rules/digital contracts | identity, contract, usage control, metering, incident and exit |
| 标注项目经理/领域标注员/质检员 | turn domain judgment into versioned labels | task allocation, qualification, annotation, agreement, adjudication and acceptance |
| 模型/应用负责人 | define data fitness and feed evaluated failures back | benchmark, failure slices, retraining decision and outcome evidence |
| 财务/法务/安全合规 | make separate accounting, contract, rights and security judgments | no cross-discipline automatic conclusion |
| 管理层/查看者 | ask questions, inspect dashboards, decide actions | authorized metrics, data-product outcome and drill paths |

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
| registration workbench | application list, object/evidence form, review timeline, correction, notice/objection and credential | draft/submitted/returned/reviewing/notice/issued/rejected/changed/cancelled |
| authorization operation | plan/agreement, resource-product-service relation, participant, disclosure, evaluation and exit | planned/approved/contracted/active/suspended/expired/exited |
| trusted data-space console | participants, products, digital contracts, usage meter, violations, settlement and revocation | onboarding/active/denied/violation/suspended/exited |
| dataset factory | demand, collection, processing, label schema, task/worker, sampling, split, benchmark, card and release diff | collecting/labeling/review/rejected/released/contamination_hold |
| model-data feedback | model/application version, failure slices, sample review, dataset change and before/after evaluation | proposed/accepted/rejected/in_next_version/verified |
| value cockpit | product/service usage, outcome, cost/revenue, settlement and renewal evidence | current/stale/disputed/under_review/closed |
| fill-in mobile | task card, sys locked values, ext editable cells, save/submit | filling/submitted/returned/overdue/offline |

## Policy / Privacy Constraints

- Apply row-level, column-level, action-level, and agent-tool-level permissions before query generation, aggregation, export, or writeback.
- Do not let agents bypass semantic model, source freshness, lineage, sensitivity labels, or user data scope.
- Record who changed source schemas, pipelines, metrics, dimensions, ontology actions, permissions, prompts, eval sets, and report scopes.
- Keep test/shadow records out of KPI, dashboard, BI, ChatBI, agent eval, and exported reports by default.
- For sensitive or regulated data, define masking, desensitization, retention, deletion/export approval, access review, and audit retention.
- For ontology/action agents, define human accountability for consequential state changes.
- For public-sector delivery, specify private deployment, network boundaries, domestic database/OS constraints, and external model/data-exit restrictions when applicable.
- Keep public-data resource registration, data-property registration, accounting recognition, appraisal/valuation, authorization, transaction and financing as linked but separately accountable decisions.
- Do not directly or indirectly release uncontrolled non-public raw public data into the market; deliver approved products/services through the confirmed environment and scope.
- Bind every participant and use to purpose, product, action, quantity, time, location, onward-transfer, retention, revocation and audit rules; a download permission alone is not a usage contract.
- Training, validation, testing, preference and application-feedback data require provenance, rights, purpose, isolation and version lineage. Production feedback is opt-in/authorized and human-gated before dataset inclusion.
- Protect held-out evaluation from training contamination, including retrieval corpora, synthetic derivatives, cached prompts, agent memory and human feedback.
- Copyright/license, personal information, trade secrets, state/public interest, export/cross-border and sector rules are project-specific P0 questions; a dataset card does not cure an unlawful source.
- Model performance gain does not by itself prove data-product value. Tie renewal, price or public benefit claims to an agreed baseline, measurement window and attribution boundary.

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
| metric definition version change | owner approval, old/new caliber, lineage impact, historical recalculation decision, consumer notification and rollback are linked |
| data-agent permission denial | denied query/write cannot be bypassed by prompt, tool delegation or cached context; denial is audited |
| registration lifecycle | initial/transfer/change/renewal/cancellation keep source/right evidence, review, notice/objection, credential validity and history linked |
| registration-accounting separation | issued credential does not automatically mark the resource as accounting-recognized, valued, financeable or dispute-free |
| authorized-operation scope | operator cannot use an unapproved resource/product/purpose or bypass disclosure, supervision and exit |
| digital-contract enforcement | expired, revoked, over-count, wrong-purpose, wrong-region or onward-transfer use is blocked and evidenced |
| dataset provenance/right withdrawal | affected samples, derived versions, models and applications are identified; freeze/retrain/delete/retain decisions are accountable |
| labeling disagreement | qualification, agreement threshold, adjudication and rejected work remain visible by schema/version |
| split leakage/contamination | entity/time/source/near-duplicate leakage and test-to-train feedback are detected before release |
| preference-data quality | ranking/critique schema, annotator policy, safety taxonomy, agreement and model/version bias are testable |
| model feedback flywheel | accepted failure slices create a new dataset version; old data and held-out benchmark are not silently mutated |
| value verification | product usage, public/operational outcome, cost/revenue and attribution limits support renew/stop decisions |

## Cross-Domain Requirement Patterns

- `PAT-METRIC-CALIBER-001`: dashboards, reports, semantic metrics and value verification must share one reproducible caliber and version.
- `PAT-LONG-RUNNING-JOB-001`: ingestion, backfill, index rebuild, export and dataset build need observable, idempotent and resumable task semantics.
- `PAT-VERSION-COMPATIBILITY-001`: schema, metric, semantic model, label policy and dataset releases must preserve historical/in-flight interpretation.
- `PAT-FEDERATED-RECONCILIATION-001`: use when registered, operated and source platforms retain overlapping authoritative attributes.

## Evaluation Profile

Domain knowledge is not execution evidence. Register coverage and maturity in
`references/domain-coverage.yaml`; keep behavioral scenarios and run evidence
outside this knowledge file.

Before raising maturity, independently evaluate:

- one primary happy path;
- one validation or exception path;
- one permission/privacy path;
- one lifecycle transition;
- one coding-agent no-guess handoff path;
- applicable migration, integration-failure, AI, and high-risk human-gate paths.

Record executor, input, environment, timestamp, result, and evidence location.
Mocked matrices and simulated reviewers cannot satisfy expert review or audit.

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
- [ ] Every registration flow declares object/type, applicant/agent, source/right evidence, review/return/reject, notice/objection, credential validity, change/renewal/transfer/cancellation and audit.
- [ ] Every authorization operation declares approving/implementing/operating roles, resource-product-service scope, agreement/term, controlled environment, price/settlement, disclosure/supervision, evaluation and exit.
- [ ] Every trusted use declares participant identity, product/purpose/action, digital contract, usage controls, metering/evidence, revocation and incident/liability path.
- [ ] Every AI dataset version has intended use, provenance/right basis, population/coverage, processing, labeling, split isolation, quality/benchmark, risks/gaps, lineage, consumers and retirement.
- [ ] SFT, validation, test, preference/DPO/RLHF and application-feedback data remain separately identifiable and cannot contaminate the held-out evaluation baseline.
- [ ] Registration credential, accounting recognition, appraisal/valuation, transaction and financing decisions have separate owners, evidence and states.
- [ ] Data-product value defines beneficiary, baseline, measurement window, cost/revenue or public outcome, attribution limit and renew/stop decision.
- [ ] Acceptance tests cover registration, authorization, digital-contract denial, AI-data provenance/label/split/benchmark/feedback, accounting separation, ingestion, governance, BI/agent, permission, freshness, export and retirement.
