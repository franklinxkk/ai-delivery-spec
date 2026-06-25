# Domain: CRM / Customer Response

Use this file for CRM, sales pipeline, customer service, partner service, customer success, contract/payment follow-up, and product-feedback-loop scenarios.

This file validates that the domain module contract can migrate beyond traffic safety.

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

- Business outcome: prevent missed opportunities, delayed customer responses, unresolved issues, and invisible product feedback.
- Primary users: boss/sponsor, sales, customer service, product/R&D, finance, partner/channel manager.
- Sensitive areas: customer contacts, contract amount, payment, customer complaints, partner relationship.
- AI may optimize: lead classification, ticket routing, customer summary, follow-up suggestion, churn/renewal hint.
- AI must not decide automatically: contract approval, payment confirmation, customer punishment, final sales commitment.
- Stage 3.5 IA Skeleton should be used for CRM delivery when the scope covers
  two or more modules (lead/opportunity/customer/ticket/contract/payment), two
  or more primary roles, or any cross-module lifecycle.
- FRR anti-bloat rule: do not repeat page layout and field dictionaries in every
  CRM function. Lock module/view/region/action in the IA Skeleton, place common
  fields in the global field dictionary, and keep each FRR focused on scenario,
  state, rule, permission, exception, and acceptance differences.

## Vocabulary

| Term | Meaning | Source of Truth |
|---|---|---|
| Lead | potential customer/opportunity signal | CRM |
| Opportunity | qualified sales chance with stage/value | CRM |
| Customer 360 | customer profile, contacts, interactions, contracts, tickets | CRM |
| Ticket | customer issue or request requiring handling | service module |
| ResponseTask | SLA-driven reminder/escalation task | workflow module |
| Partner | channel/agent who introduces or serves customers | partner module |

## Aggregates and Entities

| Aggregate | Owns | Key States | Notes |
|---|---|---|---|
| Lead | source, owner, first response, qualification | new / assigned / contacted / converted / invalid |
| Opportunity | stage, value, owner, next action | qualified / proposal / poc / negotiation / won / lost |
| Customer | profile, contacts, tags, owner, lifecycle | prospect / active / at_risk / churned |
| Contract | amount, payment plan, invoices | draft / signed / partially_paid / paid / overdue |
| Ticket | type, owner, SLA, result | new / assigned / processing / pending_customer / escalated / closed |
| ResponseTask | object ref, SLA, owner, priority | pending / responded / overdue / escalated / closed |

## Domain Events

```yaml
events:
  LeadAssigned:
    payload: { lead_id, owner_id, assigned_by, assigned_at }
  LeadFirstResponded:
    payload: { lead_id, response_time, followup_id }
  OpportunityWon:
    payload: { opportunity_id, customer_id, contract_id, amount }
  TicketCreated:
    payload: { ticket_id, customer_id, type, creator_id }
  TicketEscalated:
    payload: { ticket_id, reason, owner_role, response_task_id }
  PaymentRegistered:
    payload: { contract_id, payment_id, amount, operator_id }
```

## State Machines

```text
Lead: new -> assigned -> contacted -> converted | invalid
Opportunity: qualified -> proposal -> poc -> negotiation -> won | lost
Ticket: new -> assigned -> processing -> pending_customer -> closed
Ticket: processing | pending_customer -> escalated -> processing
ResponseTask: pending -> responded -> closed
ResponseTask: pending -> overdue -> escalated -> closed
```

## Metric / Indicator Governance

| Metric | Caliber | Source | Owner |
|---|---|---|---|
| first_response_timeout_count | high-intent leads not responded within SLA | Lead + ResponseTask | sales ops |
| overdue_ticket_count | tickets beyond SLA | Ticket | service manager |
| stalled_opportunity_count | opportunities with no update beyond threshold | Opportunity | sales manager |
| partner_feedback_delay | partner leads without feedback | Partner + Lead | channel manager |

## AI Context Sources

| Context | Source | Freshness | Permission Scope |
|---|---|---|---|
| lead source and text | CRM lead records | real-time | assigned org/role |
| customer interactions | followup/ticket records | real-time | customer owner + authorized roles |
| contract/payment | finance module | real-time | masked by role |
| product issue history | ticket/demand module | daily/real-time | service/product roles |

## Content / Knowledge Assets

| Asset | Minimum Metadata | Governance |
|---|---|---|
| sales playbook | stage, target customer, owner, version | approved by sales leadership |
| response/SLA policy | object type, priority, deadline, escalation | versioned and auditable |
| product FAQ/solution | product/version, audience, effective date | product review before publishing |
| contract/payment policy | contract type, approval role, financial boundary | finance/legal authority |
| service templates | ticket type, response text, attachment requirements | service owner and revision history |

## Core Workflows

| Workflow | Trigger | End State |
|---|---|---|
| lead response | lead imported/created | contacted or invalid |
| opportunity conversion | lead qualified | opportunity won/lost |
| customer issue handling | customer feedback | ticket closed or demand created |
| product feedback loop | repeated tickets | demand evaluated/scheduled |
| partner service | partner introduces lead | feedback sent to partner |

## Role Path Patterns

| Role | Entry | Core Actions | Forbidden Actions | Exit |
|---|---|---|---|---|
| boss | dashboard | inspect exception, assign owner, view closure | edit raw financial records | exception reduced |
| sales | my leads/customers | respond, follow up, convert, create ticket | view other sales sensitive data | next action recorded |
| customer service | service queue | create ticket, assign, follow, close | confirm payment | ticket closure |
| product/R&D | ticket/demand queue | accept, resolve, adopt demand | change contract/payment | demand roadmap |
| finance | contract/payment | register payment, view overdue | edit customer issue | payment updated |

## UI / Mobile Patterns

- dashboard: exception metrics with drilldown;
- response center: SLA task queue;
- customer 360: contacts, followups, opportunities, contracts, tickets;
- mobile sales: customer lookup, followup, ticket submission, weak-network draft;
- boss path: exception -> object detail -> owner action -> status verification.
- IA Skeleton examples:
  - `M01-V01`: boss operating cockpit / exception dashboard;
  - `M02-V01`: lead pool and lead response queue;
  - `M03-V01`: opportunity pipeline;
  - `M04-V01`: customer 360;
  - `M05-V01`: ticket and demand loop;
  - `M06-V01`: contract/payment follow-up;
  - `M02-V01-mobile`: sales mobile lead/customer follow-up when the mobile path
    has distinct navigation, permission, or offline behavior.
- Coding-agent handoff should use the standard `delivery/` layout:
  `delivery/ia-skeleton.yaml`, `delivery/prd/`, `delivery/prototype/`,
  `delivery/acceptance/`, `delivery/agents/`, and `delivery/manifest.json`.

## Policy / Privacy Constraints

- customer contacts and contract amounts are masked by role;
- export requires audit;
- cross-tenant/customer access requires explicit authorization;
- AI suggestions must show source and confidence;
- AI cannot confirm payment, approve contract, or close customer issue without human confirmation.

## Domain Test Scenarios

| Scenario | Role | Preconditions | Steps | Expected Domain Result |
|---|---|---|---|---|
| high-intent lead not responded | boss/sales | lead overdue | assign -> first respond | LeadFirstResponded, ResponseTask closed |
| customer rejects ticket result | customer service | ticket pending_customer | escalate | TicketEscalated, urgent ResponseTask created |
| sales mobile weak network followup | sales | customer visible | write followup offline | draft preserved, no data loss |
| partner lead feedback | channel manager | partner lead converted | send feedback | PartnerFeedbackRecorded |

## Acceptance Checklist

- [ ] Lead, opportunity, customer, ticket, contract/payment, response task states are defined.
- [ ] Every SLA exception has owner, action, and closure rule.
- [ ] Customer 360 shows business data, not only metadata.
- [ ] Role/data isolation is explicit.
- [ ] AI suggestions remain suggestions unless explicitly human-approved.
- [ ] If the CRM scope spans multiple modules or roles, IA Skeleton is locked
      before full FRR generation.
- [ ] Common CRM fields are maintained in a global field dictionary and FRRs do
      not duplicate unchanged field definitions.
- [ ] Coding-agent delivery package paths are explicit when implementation by
      Claude Code, Cursor, Codex, or Copilot is expected.
