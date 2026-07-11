# Product Truth Field Dictionary Projection

Fields are canonical `FLD-*` objects in Product Truth. Use this readable table
when customers, product, engineering, or QA need a field-focused projection.
Do not create a second conflicting dictionary.

## Entity

| Entity ID | Entity | Owner | State Machine | Source IDs |
|---|---|---|---|---|

## Fields

| Field ID | Name | Type | Required | Source | Dictionary / Caliber | Default | Editable By | Validation / Error | Sensitivity | Retention / Export |
|---|---|---|---|---|---|---|---|---|---|---|

Every list, create, edit, detail, filter, import, export, API, event, report,
and migration use must reference the same Field ID.

## View Usage

| Field ID | View / Region | Display | Create | Edit | Filter | Export | Role / State Variant |
|---|---|---:|---:|---:|---:|---:|---|

## Dictionary / Enum

| Field ID | Value | Label | Meaning | Enter Condition | Leave Condition | Effective Version |
|---|---|---|---|---|---|---|

## Cross-Entity Mapping

| Field ID | References | Cardinality | Source Owner | Mapping / Conflict Rule | Migration |
|---|---|---|---|---|---|

## Change Rules

- Rename a label without changing semantics: keep Field ID.
- Change type, meaning, source, sensitivity, or lifecycle: use `CHG-*` and
  assess every view/action/API/event/AC consumer.
- Split/merge/deprecate: record replacement map and historical compatibility.
- Never reuse a deprecated Field ID for a different meaning.
