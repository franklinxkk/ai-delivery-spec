# SaaS Multitenancy / RBAC Pattern

Use this file for SaaS, ToB, ToG, group-company, agency, enterprise, school, tenant, organization tree, role/permission, license, seat, data isolation, or cross-tenant analytics.

## Tenant Contract

```yaml
tenant_contract:
  tenant_type: government_org | enterprise | school | partner | customer
  org_tree: province/city/district/enterprise | group/subsidiary/department | custom
  isolation_model: physical | logical | row_level | hybrid
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
