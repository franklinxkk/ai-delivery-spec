# L1 PRD Sample: CRM Lead Response

## 0. Delivery Metadata

```yaml
artifact: light_prd_sample
domain: CRM / Customer Response
mode: Lite
tier: L1
ai: false
workflow: true
completion_state: REVIEW_COMPLETE_WITH_GAPS
```

## 1. Problem And Outcome

Sales leads arrive from phone, website, partners, customer service, and manual
entry. The boss wants to prevent missed opportunities and delayed follow-up.
The product outcome is: every high-value lead has an owner, first-response SLA,
follow-up state, and escalation path.

Success metric:

```text
High-value lead first response within 30 minutes: unknown baseline -> 90% in pilot region within 30 days.
```

## 2. Users And Core Scenario

| Role | Goal | Pain |
|---|---|---|
| Boss | see whether opportunities are being followed | cannot tell which sales owner is delaying |
| Sales | receive and follow up leads | lead context is scattered |
| Customer service | transfer business signals | service tickets and sales opportunities are disconnected |

Core flow:

```text
Lead created -> system assigns owner -> sales first responds -> lead becomes opportunity or invalid -> boss sees SLA result.
```

## 3. Function Inventory

| Function ID | Function Name | User Outcome | Release Scope |
|---|---|---|---|
| CRM-F01 | Create and assign lead | lead has owner and SLA | in |
| CRM-F02 | First response tracking | lead response is visible | in |
| CRM-F03 | Convert to opportunity | qualified lead enters sales pipeline | in |

## 4. Functional Requirement Record: CRM-F01 Create And Assign Lead

| Section | Content |
|---|---|
| Identity and value | CRM-F01; sales/customer-service creates lead and prevents missed owner assignment |
| Roles and scenario | customer service or sales creates lead from customer signal |
| Entry and preconditions | user has lead-create permission; customer name or contact method is required |
| Pages and visible states | create form, validation error, saved success, assigned lead list row |
| Fields and dictionaries | lead source, customer name, contact, industry, intent level, region, owner, next follow-up time |
| Numbered interaction flow | 1 open create form; 2 fill required fields; 3 submit; 4 system assigns owner; 5 list shows new lead |
| Actions and results | submit creates lead, owner, SLA timer, audit record |
| Business rules and calibers | high intent lead must have next follow-up time; duplicate contact warns before save |
| State-button behavior | new -> assigned; assigned shows contact, convert, invalid |
| Permission and data scope | sales sees own leads; boss sees all authorized leads |
| Exceptions and recovery | missing contact blocks; duplicate contact requires confirm/merge decision |
| Notifications, audit, and dependencies | assigned owner receives task; audit stores creator/source/time |
| Data / AI / algorithm contract | N/A: deterministic assignment unless future AI routing is introduced |
| Function-Level NFR | save response <= 2s for normal load; audit cannot be skipped |
| Frontend / Backend / QA handoff notes | frontend shows validation and new row; backend validates duplicate/contact/owner; QA tests duplicate and permission |
| Acceptance | Given authorized CS creates a valid lead, when submit succeeds, then list shows assigned lead and owner task exists |

```yaml
ac_structured:
  - id: AC-CRM-F01-001
    given: "authorized customer-service user has a valid lead signal"
    when: "the user submits required lead fields"
    then: "the lead appears in the list with owner, assigned state, SLA timer, and audit record"
    test_type: integration
```

## 5. Gaps Before L2

- Confirm assignment rule: round-robin, industry owner, region owner, or manual assignment.
- Confirm duplicate handling: block, merge, or warn-only.
- Confirm boss data scope across departments and partners.
