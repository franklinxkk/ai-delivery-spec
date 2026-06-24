# Global Field Dictionary Template

Use this template to define each entity's fields once, then reference them from
FRR §5 instead of repeating the full dictionary in every function.

## How to use

1. Create one file per domain aggregate, e.g. `field-dictionary-lead.md`,
   `field-dictionary-opportunity.md`.
2. List every field that appears in list, create, edit, detail, filter, export,
   or state-machine contexts.
3. In each FRR §5, state:
   - "Fields reference `field-dictionary-{entity}.md`."
   - Then list only the fields whose rule differs in this function.

## Entity: {EntityName}

| # | field_name | label | type | required | constraints | enum / dictionary | read_only | system_filled | validation_rule | masking_rule |
|---:|---|---|---|---|---|---|---|---|---|---|
| 1 | {entity}.name | 名称 | string(100) | yes | max 100 | N/A | no | no | non-empty, no special chars | — |
| 2 | {entity}.status | 状态 | enum | no | system-managed | [待分配, 已分配, 跟进中, 已转商机, 无效] | yes | yes | set by state machine | — |
| 3 | {entity}.ownerId | 负责人 | ref(user) | no | — | N/A | no | system(分配时) | valid user reference | — |
| 4 | {entity}.createdAt | 创建时间 | datetime | no | — | N/A | yes | yes | auto-set on create | — |
| 5 | {entity}.version | 版本号 | integer | no | optimistic lock | N/A | yes | yes | ≥0 | — |

## Field ownership by view type

| field_name | list | create | edit | detail | filter | export | notes |
|---|---|---|---|---|---|---|---|
| {entity}.name | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | primary display field |
| {entity}.status | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | system-managed |
| {entity}.ownerId | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | assigned by system or role with permission |

## Enum definitions

### {entity}.status

| Value | Label | Meaning | Enter condition | Leave condition |
|---|---|---|---|---|
| pending | 待分配 | 新创建，未分配 | created | assigned |
| assigned | 已分配 | 已指定负责人 | assignment event | first follow-up or close |
| following | 跟进中 | 已开始跟进 | first follow-up saved | convert or close |
| converted | 已转商机 | 已转为商机 | convert action | — |
| invalid | 无效 | 手动关闭 | close action | — |

## Cross-entity reference fields

Fields that link this entity to others. Keep them consistent across all FRRs.

| field_name | type | references | rule |
|---|---|---|---|
| {entity}.customerId | ref(customer) | Customer.id | 转化/关联时携带 |
| {entity}.leadId | ref(lead) | Lead.id | 溯源字段，由线索转化时生成 |

## Usage in FRR

Example FRR §5 for "新建线索":

```markdown
##### 5. Fields and Dictionaries

Reference global field dictionary: `field-dictionary-lead.md`.

Fields with special rules in this function:

| Field | Special rule |
|---|---|
| lead.source | 代理商录入时强制为"代理商"并锁定 partnerId |
| lead.intent | 新建时必填，影响后续分配优先级 |
```
