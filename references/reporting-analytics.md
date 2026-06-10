# Reporting / Analytics Product Pattern

Use this file for data marts, BI dashboards, report builders, indicator libraries, data reports, large screens, self-service analytics, Excel imports, and AI-generated reports.

Reporting products are not only CRUD. Model them as metric definitions, datasets, transformations, templates, tasks, generated outputs, and evidence lineage.

## Domain Model

| Aggregate | Owns | Key States |
|---|---|---|
| MetricDefinition | caliber, formula, dimensions, owner, version | draft / active / deprecated |
| Dataset | source, schema, refresh policy, permission | draft / active / failed |
| Transformation | join, filter, aggregation, calculation | draft / validated / failed |
| ReportTemplate | layout, blocks, metrics, parameters | draft / published / archived |
| ReportTask | period, scope, template snapshot, status | created / running / completed / failed |
| ReportOutput | generated data, narrative, charts, export | pending / ready / reviewed / published |

## Required Contracts

| Contract | Required Fields |
|---|---|
| Metric | id, name, caliber, formula, dimensions, source, owner, version |
| Dataset | source table/API/file, refresh frequency, permission scope, quality checks |
| Transformation | input, processing logic, join keys, aggregation, null handling |
| Template | parameters, blocks, metric bindings, version lock |
| Output | data snapshot, generated time, evidence refs, export path |

## State Rules

- Active metrics used by published templates cannot be edited without versioning.
- Report outputs must lock metric/template versions.
- AI narrative must cite metric evidence and source period.
- Failed data refresh must show stale/failed state, not silently reuse old data.
- Manual fill and automatic extraction must show source difference.

## Prototype Requirements

- Metric detail shows formula/caliber/source/version.
- Template creation and report task creation are separate.
- Generated report output can be opened and inspected.
- Data lineage/evidence is visible for at least one chart/table/narrative.
- Empty, failed refresh, stale data, and permission-limited states are represented.

## Developer Fast-Lane Example

| Command/Query | Aggregate | Domain Result |
|---|---|---|
| `PublishMetricDefinition` | MetricDefinition | new active metric version |
| `CreateReportTask` | ReportTask | task created with template snapshot |
| `GenerateReportOutput` | ReportOutput | output ready with evidence refs |
| `ReviewAiNarrative` | ReportOutput | narrative approved/rejected |

## Acceptance Tests

| Case | Expected Domain Result |
|---|---|
| metric formula changes | new version, old report unchanged |
| dataset refresh fails | task/report shows failed or stale state |
| template creates task | task references template snapshot |
| AI report generates narrative | citations/evidence attached |
| permission-limited user opens report | hidden dimensions masked/denied |
