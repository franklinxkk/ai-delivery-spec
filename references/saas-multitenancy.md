# SaaS Multitenancy / RBAC Pattern

Use this file for SaaS, ToB, ToG, group-company, agency, enterprise, school, tenant, organization tree, role/permission, license, seat, data isolation, or cross-tenant analytics.

## Tenant Contract

```yaml
tenant_contract:
  tenant_type: government_org | enterprise | school | partner | customer
  org_tree: province/city/district/enterprise | group/subsidiary/department | custom
  isolation_model: physical | logical | row_level | hybrid
  home_region: string
  allowed_processing_regions: [string]
  allowed_support_access_regions: [string]
  cross_tenant_access:
    allowed_roles: []
    allowed_data_scope: []
    audit_required: true
  license:
    plan: string
    seats: number
    feature_flags: []
```

## RBAC Matrix

| Role | Data Scope | View | Create | Edit | Approve | Export | Admin | Forbidden |
|---|---|---|---|---|---|---|---|---|
| tenant_admin | own tenant | yes | yes | yes | conditional | yes | yes | other tenant data |
| operator | assigned scope | yes | yes | assigned | no | limited | no | admin config |
| auditor | configured scope | yes | no | no | no | yes | no | mutation |

## Permission Rules

- UI hiding is not a permission boundary; backend guard must match.
- Every cross-tenant query needs explicit scope and audit.
- Export must record tenant, role, data scope, fields, and reason.
- Sensitive fields need masking rules by role.
- Feature flags/license must define disabled UI and API behavior.
- Seat/license limits need validation and upgrade path.
- Tenant home region is part of the authorization context, not only deployment configuration.
- Cross-region administration, support impersonation, exports, backups, analytics, search indexes, embeddings, and AI traces require explicit scope and audit.
- A tenant move between regions is a migration with consent/contract, export/import verification, rollback, and deletion of the old copy; do not change a region flag only.

## Regional Tenant Matrix

| Concern | Required Contract |
|---|---|
| tenant creation | choose/derive home region, legal entity, locale, timezone, currency, contract/privacy versions |
| data plane | storage, cache, search/vector index, queue, logs, backup, analytics, model endpoint regions |
| control plane | define which metadata is global and prohibit customer content in global control records unless approved |
| admin/support | regional access policy, just-in-time grant, reason, masking, session recording/audit, expiry |
| cross-region aggregate | allowed metrics, anonymization/aggregation threshold, export owner, prohibited dimensions |
| disaster recovery | approved secondary region, recovery point/time targets, transfer basis, tested failover |
| tenant exit | export format, encryption, deletion SLA, subprocessor deletion evidence |

## Prototype Requirements

- Role switch demonstrates at least one permission boundary.
- Tenant/org selector or current tenant context is visible where relevant.
- Forbidden actions are hidden or explain permission rule.
- Mock data includes at least two tenants when isolation matters.

## Test Cases

| Case | Expected Result |
|---|---|
| user from tenant A opens tenant B data | denied or masked |
| tenant admin exports data | audit record created |
| role lacks approval permission | approve action hidden/blocked |
| license limit reached | create user/action blocked with upgrade path |
| upper-level regulator views lower org | scope-limited aggregate/drilldown only |
| tenant A in region A fails over | traffic remains in an approved region or enters safe fallback; no silent cross-region movement |
| support engineer outside allowed region requests access | denied or time-bound approved access with full audit |
