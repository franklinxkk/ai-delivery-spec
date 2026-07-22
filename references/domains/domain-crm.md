# Domain: CRM / Customer Response

Source authority and freshness metadata: `references/domains/domain-sources.yaml`.
Coverage and maturity: `references/domain-coverage.yaml`.

Use this file for CRM, sales pipeline, customer service, partner service, customer success, contract/payment follow-up, and product-feedback-loop scenarios.

This file validates that the domain module contract can migrate beyond traffic safety.

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
- Multi-Module PRD Quality Gate
- Acceptance Checklist

## Domain Purpose

- Business outcome: prevent missed opportunities, delayed customer responses, unresolved issues, and invisible product feedback.
- Primary users: boss/sponsor, sales, customer service, product/R&D, finance, partner/channel manager.
- Sensitive areas: customer contacts, contract amount, payment, customer complaints, partner relationship.
- AI may optimize: lead classification, ticket routing, customer summary, follow-up suggestion, churn/renewal hint.
- AI must not decide automatically: contract approval, payment confirmation, customer punishment, final sales commitment.
- Capability scope may include marketing lead acquisition, SFA pipeline,
  Customer 360, CPQ/quotation, contract/payment, service tickets, customer
  success/renewal, partner/channel operations, and product-feedback loops.
- Product Truth must lock module/view/region/action ownership when CRM spans
  lead, opportunity, customer, ticket, contract, payment, multiple roles, or a
  cross-module lifecycle.
- Keep shared CRM fields canonical as `FLD-*`; projections show only relevant
  scenario, state, rule, permission, exception, and acceptance differences.

## First-Principles Domain Lens

First-Principles CRM Product Logic: CRM product judgment starts from customer
operating response, not from a list of tables or fashionable AI features.

| Lens | CRM Question | Acceptance Signal |
|---|---|---|
| Revenue lifecycle | Which customer or opportunity state moves toward signed revenue, renewal, or explicit loss? | lead/opportunity/customer/contract state changes and owner are traceable |
| Response accountability | Who must respond, by when, and what closes the response? | SLA task, owner, close guard, and audit are explicit |
| Customer truth | Which module is the source of truth for customer, contact, contract, ticket, and follow-up facts? | Customer 360 can explain every aggregate with source links |
| Exception closure | Which stuck, overdue, rejected, lost, or escalated case must be visible to a manager? | alert/response task links to the business object and real closure action |
| Boundary of automation | Which sales, finance, service, or roadmap actions cannot be automatic? | payment, contract approval, final commitment, and ticket closure keep human gates |
| Domain breadth | Which CRM family is in scope: SFA, service, customer success, CPQ, campaign, channel, data/BI, AI assistant? | included/deferred modules and external systems are explicit |

## Vocabulary

| Term | Meaning | Source of Truth |
|---|---|---|
| Lead | potential customer/opportunity signal | CRM |
| Opportunity | qualified sales chance with stage/value | CRM |
| Customer 360 | customer profile, contacts, interactions, contracts, tickets | CRM |
| Ticket | customer issue or request requiring handling | service module |
| ResponseTask | SLA-driven reminder/escalation task | workflow module |
| Partner | channel/agent who introduces or serves customers | partner module |
| Campaign | marketing activity, channel, audience, and conversion source | marketing module |
| Quote / CPQ | product/package/discount proposal before contract | quotation module |
| Renewal / Churn Risk | customer success lifecycle signal | customer success module |
| Demand | product request created from service or sales feedback | product/R&D module |

## Aggregates and Entities

| Aggregate | Owns | Key States | Notes |
|---|---|---|---|
| Lead | source, owner, first response, qualification | new / assigned / contacted / converted / invalid |
| Opportunity | stage, value, owner, next action | qualified / proposal / poc / negotiation / won / lost |
| Customer | profile, contacts, tags, owner, lifecycle | prospect / active / at_risk / churned |
| Contract | amount, payment plan, invoices | draft / signed / partially_paid / paid / overdue |
| Ticket | type, owner, SLA, result | new / assigned / processing / pending_customer / escalated / closed |
| ResponseTask | object ref, SLA, owner, priority | pending / responded / overdue / escalated / closed |
| Campaign | audience, channel, cost, leads, conversion | draft / active / completed / archived |
| Quote | product package, price, discount, approval | draft / submitted / approved / rejected / expired |
| RenewalPlan | account, renewal date, risk, owner, actions | planned / at_risk / negotiating / renewed / churned |
| Demand | source ticket/customer, value, review, roadmap link | new / reviewed / scheduled / released / rejected |

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
  RenewalRiskDetected:
    payload: { customer_id, risk_level, evidence_refs, owner_id }
  DemandCreatedFromTicket:
    payload: { demand_id, ticket_id, customer_id, creator_id }
  QuoteApproved:
    payload: { quote_id, opportunity_id, approver_id, approved_at }
```

## State Machines

```text
Lead: new -> assigned -> contacted -> converted | invalid
Opportunity: qualified -> proposal -> poc -> negotiation -> won | lost
Ticket: new -> assigned -> processing -> pending_customer -> closed
Ticket: processing | pending_customer -> escalated -> processing
ResponseTask: pending -> responded -> closed
ResponseTask: pending -> overdue -> escalated -> closed
Quote: draft -> submitted -> approved | rejected | expired
RenewalPlan: planned -> at_risk -> negotiating -> renewed | churned
Demand: new -> reviewed -> scheduled -> released | rejected
```

## Metric / Indicator Governance

| Metric | Caliber | Source | Owner |
|---|---|---|---|
| first_response_timeout_count | high-intent leads not responded within SLA | Lead + ResponseTask | sales ops |
| overdue_ticket_count | tickets beyond SLA | Ticket | service manager |
| stalled_opportunity_count | opportunities with no update beyond threshold | Opportunity | sales manager |
| partner_feedback_delay | partner leads without feedback | Partner + Lead | channel manager |
| campaign_conversion_rate | qualified leads / campaign leads by channel and period | Campaign + Lead | marketing ops |
| win_rate_by_stage | won opportunities / stage-entered opportunities | Opportunity | sales ops |
| payment_overdue_amount | unpaid amount past payment-plan date | Contract + Payment | finance |
| renewal_risk_count | active customers with renewal risk above threshold | Customer + RenewalPlan | customer success |
| ticket_to_demand_rate | product-related tickets converted to demands | Ticket + Demand | product ops |

## AI Context Sources

| Context | Source | Freshness | Permission Scope |
|---|---|---|---|
| lead source and text | CRM lead records | real-time | assigned org/role |
| customer interactions | followup/ticket records | real-time | customer owner + authorized roles |
| contract/payment | finance module | real-time | masked by role |
| product issue history | ticket/demand module | daily/real-time | service/product roles |
| marketing and channel source | campaign/partner platform | daily/real-time | marketing/channel roles |
| quote/discount history | quotation/contract module | real-time | sales manager/finance/legal scope |
| renewal and usage signals | customer success/product telemetry | daily | customer owner + CS role |

## Content / Knowledge Assets

| Asset | Minimum Metadata | Governance |
|---|---|---|
| sales playbook | stage, target customer, owner, version | approved by sales leadership |
| response/SLA policy | object type, priority, deadline, escalation | versioned and auditable |
| product FAQ/solution | product/version, audience, effective date | product review before publishing |
| contract/payment policy | contract type, approval role, financial boundary | finance/legal authority |
| service templates | ticket type, response text, attachment requirements | service owner and revision history |
| sales stage playbook | stage, exit criteria, required evidence, next action | sales leadership review |
| quote/discount policy | product package, discount boundary, approval role | finance/legal authority |
| renewal/churn playbook | risk signal, intervention action, owner, cadence | customer success owner |

## Core Workflows

| Workflow | Trigger | End State |
|---|---|---|
| lead response | lead imported/created | contacted or invalid |
| opportunity conversion | lead qualified | opportunity won/lost |
| customer issue handling | customer feedback | ticket closed or demand created |
| product feedback loop | repeated tickets | demand evaluated/scheduled |
| partner service | partner introduces lead | feedback sent to partner |
| marketing-to-sales handoff | campaign lead qualified | lead assigned and SLA tracked |
| quote-to-contract | opportunity price proposal approved | contract draft or signed |
| renewal/churn intervention | renewal risk signal appears | renewal plan closed as renewed/churned |

## Role Path Patterns

| Role | Entry | Core Actions | Forbidden Actions | Exit |
|---|---|---|---|---|
| boss | dashboard | inspect exception, assign owner, view closure | edit raw financial records | exception reduced |
| sales | my leads/customers | respond, follow up, convert, create ticket | view other sales sensitive data | next action recorded |
| customer service | service queue | create ticket, assign, follow, close | confirm payment | ticket closure |
| product/R&D | ticket/demand queue | accept, resolve, adopt demand | change contract/payment | demand roadmap |
| finance | contract/payment | register payment, view overdue | edit customer issue | payment updated |
| marketing ops | campaign dashboard | import leads, inspect conversion | change opportunity stage | leads handed off |
| customer success | customer success workspace | inspect health, plan renewal, create task | approve discount/payment | renewal outcome |
| channel manager | partner workspace | manage partner leads, feedback, settlement evidence | see unrelated partner data | partner SLA closed |

## UI / Mobile Patterns

- dashboard: exception metrics with drilldown;
- response center: SLA task queue;
- customer 360: contacts, followups, opportunities, contracts, tickets;
- customer success workspace: health, usage, renewal, churn risk, intervention tasks;
- campaign and channel views: lead source, conversion funnel, attribution, partner feedback;
- quote/contract/payment flow: quote approval, contract state, payment plan, overdue follow-up;
- mobile sales: customer lookup, followup, ticket submission, weak-network draft;
- boss path: exception -> object detail -> owner action -> status verification.
- Product Truth view examples:
  - `M01-V01`: boss operating cockpit / exception dashboard;
  - `M02-V01`: lead pool and lead response queue;
  - `M03-V01`: opportunity pipeline;
  - `M04-V01`: customer 360;
  - `M05-V01`: ticket and demand loop;
  - `M06-V01`: contract/payment follow-up;
  - `M02-V01-mobile`: sales mobile lead/customer follow-up when the mobile path
    has distinct navigation, permission, or offline behavior.
- Coding-agent handoff uses `delivery/truth/product-truth.yaml`, approved
  changes, projections, prototype, acceptance, agents, evidence, and manifest.

## Policy / Privacy Constraints

- customer contacts and contract amounts are masked by role;
- export requires audit;
- cross-tenant/customer access requires explicit authorization;
- AI suggestions must show source and confidence;
- AI cannot confirm payment, approve contract, or close customer issue without human confirmation.
- AI cannot approve quote discounts, decide churn status, modify payment amount,
  or publish product roadmap commitments without accountable human approval.

## Domain Test Scenarios

| Scenario | Role | Preconditions | Steps | Expected Domain Result |
|---|---|---|---|---|
| high-intent lead not responded | boss/sales | lead overdue | assign -> first respond | LeadFirstResponded, ResponseTask closed |
| customer rejects ticket result | customer service | ticket pending_customer | escalate | TicketEscalated, urgent ResponseTask created |
| sales mobile weak network followup | sales | customer visible | write followup offline | draft preserved, no data loss |
| partner lead feedback | channel manager | partner lead converted | send feedback | PartnerFeedbackRecorded |
| quote approval boundary | sales manager/finance | quote exceeds discount threshold | submit -> review -> approve/reject | QuoteApproved or rejection audit |
| renewal risk intervention | customer success | customer is at_risk | create plan -> follow up -> close | RenewalPlan ends renewed/churned |
| ticket to demand loop | service/product | repeated product issue | convert ticket to demand | DemandCreatedFromTicket traceable |
| lead to collected revenue | sales/finance | qualified lead exists | convert -> win opportunity -> sign contract -> invoice -> register payment | lead, opportunity, customer, contract, invoice, and payment retain source IDs, state owners, permissions, and audit |

## Cross-Domain Requirement Patterns

- `PAT-CROSS-MODULE-CONVERSION-001`: ticket→demand, lead→opportunity/customer and opportunity→contract preserve stable source/target references and a reachable next owner action.
- `PAT-PERMISSION-001`: navigation visibility, object permission, row scope and field masking are separate contracts; a visible menu never expands data access.
- `PAT-VERSION-COMPATIBILITY-001`: sales stages, SLA, quote policy and approval configuration preserve in-flight and historical interpretation.
- `PAT-METRIC-CALIBER-001`: funnel, win rate, response SLA, revenue and collection metrics share one state, time and dedup caliber across cockpit/export/API.

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

- [ ] Lead, opportunity, customer, ticket, contract/payment, response task states are defined.
- [ ] Marketing/campaign, quote/CPQ, renewal/customer success, partner/channel,
      and product-demand loops are included or explicitly out of scope.
- [ ] Every SLA exception has owner, action, and closure rule.
- [ ] Customer 360 shows business data, not only metadata.
- [ ] Role/data isolation is explicit.
- [ ] AI suggestions remain suggestions unless explicitly human-approved.
- [ ] If CRM spans multiple modules or roles, Product Truth locks shared
      objects, state owners, views, actions, events, permissions, and flows.
- [ ] Common CRM fields use canonical `FLD-*` definitions; projections do not
      duplicate or redefine them.
- [ ] Coding-agent delivery package paths are explicit when implementation by
      Claude Code, Cursor, Codex, or Copilot is expected.
