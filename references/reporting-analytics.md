# Reporting / Analytics Product Pattern

Use this file for data marts, BI dashboards, indicator libraries, report builders, Excel collection reports, AI-generated data reports, large screens, and self-service analytics.

Reporting products are not only CRUD. Model metric definitions, datasets, transformations, templates, tasks, fill records, generated outputs, and evidence lineage. Apply the complete module specification in `templates/prd-standard-template.md`; the contracts below add reporting-specific depth.

## Contents

- Domain Model
- Shared Required Contracts
- A. Dashboard Detailed Specification
- B. Indicator Library Detailed Specification
- C. Excel Report Template, Task, And Fill Detailed Specification
- D. AI Data Report Detailed Specification
- Prototype Requirements
- Developer Fast-Lane Example
- Acceptance Tests

## Domain Model

| Aggregate | Owns | Key States |
|---|---|---|
| MetricDefinition | caliber, formula, dimensions, owner, version | draft / active / deprecated |
| Dataset | source, schema, refresh policy, permission | draft / active / failed / stale |
| Transformation | join, filter, aggregation, calculation | draft / validated / failed |
| DashboardDefinition | cards, charts, filters, drill paths, refresh | draft / published / archived |
| ReportTemplate | layout, blocks/columns, metrics, parameters, prompts | draft / published / disabled / archived |
| ReportTask | period, scope, template snapshot, schedule, status | created / running / collecting / completed / failed / returned |
| FillRecord | enterprise/subject, fields, validation, return reason | pending / filling / submitted / returned / locked |
| ReportOutput | data snapshot, narrative, charts, export, evidence | pending / ready / failed / reviewed / published |

## Shared Required Contracts

| Contract | Required Fields |
|---|---|
| Metric | id, name, business meaning, caliber/formula, dimensions, source, refresh, owner, version, permissions, null/duplicate handling |
| Dataset | source table/API/file, subject grain, schema, refresh frequency, permission scope, quality checks, stale/failure behavior |
| Transformation | inputs, join keys, filter, aggregation, calculation, null handling, effective version |
| Template | type, parameters, blocks/columns, metric bindings, manual-fill fields, version lock, owner, status |
| Task | template snapshot, period, subject scope, deadline, schedule, progress formulas, completion/return policy |
| Output | data snapshot, generated time, template/metric versions, evidence refs, export path, access scope |

## A. Dashboard Detailed Specification

For every metric card/chart/ranking, preserve the authoritative metric definition rather than only its display name.

| Metric ID | Display Name | Business Meaning | Formula / Caliber | Time Window | Subject / Dimensions | Filter Interaction | Drill Target | Refresh / Stale Rule | Permission | Empty / Error | Source ID |
|---|---|---|---|---|---|---|---|---|---|---|---|

Also define:

- global and local filters, default values, cascading behavior, reset behavior, and snapshot consistency;
- whether cards, charts, rankings, exports, and drills use the same data snapshot;
- comparison baseline, denominator, rounding, unit, timezone, and late-arriving-data rules;
- loading, empty, partial, stale, permission-limited, and refresh-failed states;
- card/chart click outcome and the exact filtered detail page or record set.

Fail if a supplied metric workbook is reduced to a few representative metrics without embedding all rows or freezing it as an authoritative annex.

## B. Indicator Library Detailed Specification

| Area | Minimum Detail |
|---|---|
| List/search | filters, columns, status, owner, version, references, actions |
| Create/edit | all business fields, formula/caliber editor, dimension/source binding, validation, preview |
| Publish/disable | guards, impact analysis, effective time, audit, referenced-template behavior |
| Versioning | compatible vs breaking change, historical output preservation, migration decision |
| Permissions | who defines, reviews, publishes, uses, and views sensitive dimensions |

State rules:

- Active metrics referenced by published templates cannot be directly overwritten; create a new version or disable after impact analysis.
- Historical report outputs keep the metric/template versions used at generation time.
- Missing, duplicate, delayed, or abnormal source data must produce an explicit quality state.

## C. Excel Report Template, Task, And Fill Detailed Specification

Separate reusable template definition from period-specific execution.

### Template Import And Binding

| Step | Required Behavior |
|---|---|
| Upload | file type/size/sheet selection, duplicate upload, parse progress, failure reason |
| Parse | preserve sheet/header hierarchy, identify subject columns, data columns, formulas, merged cells, unknown fields |
| Confirm | show recognized/unrecognized columns, allow correction, bind each column to metric or manual-fill field |
| Validate | subject grain, required columns, duplicate bindings, incompatible dimensions, dictionary/type checks |
| Publish | freeze template version and binding snapshot; create no execution task unless explicitly requested |

### Task And Fill Contract

| Item | Required Detail |
|---|---|
| Task creation | template version, period, subjects/enterprises, deadline, schedule, notification policy |
| Auto extraction | metric-bound columns, snapshot time, automatic extraction rate formula, failure/retry |
| Manual fill | assignee entry, field validation, save draft, submit, return reason, resubmit |
| Industry review | progress view, return selected records, mark task complete, forced-complete confirmation |
| Locking | after industry marks complete, enterprise records are read-only and export uses frozen snapshot |
| Progress | total records/fields, auto-filled count, submitted count, returned count, completion rate/caliber |

Required paths: fully automatic task, mixed auto/manual task, parse failure, unknown column correction, enterprise draft/submit, industry return/resubmit, completed snapshot/detail/export.

## D. AI Data Report Detailed Specification

An AI report is a governed template-to-output workflow, not a free-form prompt box.

| Area | Required Detail |
|---|---|
| Template metadata | name, purpose, service department/role, owner, status, schedule, scope |
| Full prompt | purpose, audience, tone/format, global constraints, variable limits, maximum length |
| Chapter structure | chapter order, chapter title, chapter prompt, inserted metrics, inserted knowledge, optional tables/charts |
| Variables | system/business variables, metric bindings, knowledge references, period/scope placeholders |
| Generation | manual/scheduled trigger, input snapshot, prompt/template/model version, timeout/retry |
| Output | report title/period, chapter content, evidence links, preview, download/export, failure reason |
| Governance | edit/publish/disable/delete guards, historical output preservation, audit, permissions |

Evidence rules:

- Every generated numeric claim traces to metric id/version, subject scope, period, and data snapshot.
- Knowledge-derived statements trace to the knowledge item/version.
- Generated output records prompt/template/model version and failure/retry history.
- If internal use permits direct generation without approval, state that explicitly; do not invent an approval workflow.
- High-confidence structured data does not remove the need for generation failure, empty-data, contradictory-evidence, and permission fallbacks.

## Prototype Requirements

- Metric detail shows complete caliber/source/version and one drillable result.
- Template creation and task creation are visibly separate.
- Excel parsing shows recognized and unidentified fields, human correction, and final save result.
- Created tasks appear in the task list immediately with progress and result/fill detail.
- Enterprise users enter through their own fill-task list and only see their assigned records.
- Generated report output can be opened, inspected, and downloaded.
- At least one chart/table/narrative exposes data lineage/evidence.
- Empty, failed refresh/generation, stale data, returned fill, completed lock, and permission-limited states are represented.

## Developer Fast-Lane Example

| Command/Query | Aggregate | Domain Result |
|---|---|---|
| `PublishMetricDefinition` | MetricDefinition | new active metric version |
| `ImportReportTemplate` | ReportTemplate | parsed draft with recognized/unrecognized bindings |
| `CreateReportTask` | ReportTask | task created with template snapshot and fill records |
| `SubmitFillRecord` | FillRecord | record submitted and progress recalculated |
| `ReturnFillRecord` | FillRecord | record returned with reason and editable again |
| `CompleteReportTask` | ReportTask | records/output frozen and task completed |
| `GenerateReportOutput` | ReportOutput | output ready with evidence refs |

## Acceptance Tests

| Case | Expected Domain Result |
|---|---|
| metric formula changes | new version; old report/output unchanged |
| dataset refresh fails | task/report explicitly shows failed or stale state |
| dashboard filter changes | all linked components use the same new snapshot and scope |
| Excel contains unknown column | column is flagged; user can correct or download errors before publish |
| template creates task | task references template snapshot and generates correct fill records |
| enterprise submission is returned | record becomes editable with visible reason and can be resubmitted |
| industry marks task complete | remaining data follows declared force-complete rule; all records lock |
| AI report generates narrative | numeric and knowledge claims include evidence references |
| permission-limited user opens report | restricted dimensions are masked or denied and audited |
