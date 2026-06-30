# Domain: CRM / Customer Response

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
- Multi-Agent Lifecycle Verification Matrix
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
- Stage 3.5 IA Skeleton should be used for CRM delivery when the scope covers
  two or more modules (lead/opportunity/customer/ticket/contract/payment), two
  or more primary roles, or any cross-module lifecycle.
- FRR anti-bloat rule: do not repeat page layout and field dictionaries in every
  CRM function. Lock module/view/region/action in the IA Skeleton, place common
  fields in the global field dictionary, and keep each FRR focused on scenario,
  state, rule, permission, exception, and acceptance differences.

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

## Multi-Agent Lifecycle Verification Matrix

| domain_id | stage | reviewer_agent | path_type | scenario_ref | evidence_ref | blocking_question | expected_result | test_marker | verdict |
|---|---|---|---|---|---|---|---|---|---|
| crm | Discover | PM Agent | happy_path | lead response | Domain Purpose / Core Workflows | Is the business outcome lead response or wider customer operating response? | outcome and release boundary are explicit | crm_discover_pm_happy_path | PASS |
| crm | Discover | Domain Expert Agent | exception_path | customer rejects ticket result | Domain Test Scenarios | Are sales/service/customer success exceptions discovered? | ticket rejection and escalation are in scope or de-scoped | crm_discover_domain_exception_path | PASS |
| crm | Discover | Architecture / Data / AI Agent | permission_privacy_path | Customer 360 | Policy / Privacy Constraints | Are contact/payment/complaint data scopes identified? | customer360_masking and role scope are required | customer360_masking | PASS |
| crm | Discover | QA Agent | lifecycle_transition | lead to opportunity | State Machines | Can QA see the first lifecycle chain? | Lead -> Opportunity path is testable | crm_discover_qa_lifecycle_transition | PASS |
| crm | Discover | Coding Agent | acceptance_test_path | coding package | UI / Mobile Patterns | Can implementation sources be found? | ac_structured, data-testid, data-action, data-state, data-api, data-method, manifest.json, source_of_truth_order required | ac_structured;data-testid;data-action;data-state;data-api;data-method;manifest.json;source_of_truth_order | PASS |
| crm | Specify | PM Agent | happy_path | opportunity conversion | Core Workflows | Does the PRD specify visible and revenue result? | lead_to_cash_trace starts from qualified lead | lead_to_cash_trace | PASS |
| crm | Specify | Domain Expert Agent | exception_path | quote approval boundary | Domain Test Scenarios | Are discount and approval boundaries explicit? | QuoteApproved or rejection audit is specified | crm_specify_domain_exception_path | PASS |
| crm | Specify | Architecture / Data / AI Agent | permission_privacy_path | contract/payment | AI Context Sources / Policy | Are finance fields masked and human-owned? | AI cannot confirm payment or approve contract | crm_specify_arch_permission_privacy_path | PASS |
| crm | Specify | QA Agent | lifecycle_transition | ResponseTask SLA | State Machines | Can SLA state and escalation be tested? | pending -> overdue -> escalated -> closed is explicit | sla_response_task | PASS |
| crm | Specify | Coding Agent | acceptance_test_path | FRR package | Acceptance Checklist | Can coding agent implement without guessing? | function, state, permission, and AC are traceable | crm_specify_coding_acceptance_test_path | PASS |
| crm | Plan | PM Agent | happy_path | campaign to sales handoff | Core Workflows | Are marketing and sales owners aligned? | campaign leads hand off with SLA | crm_plan_pm_happy_path | PASS |
| crm | Plan | Domain Expert Agent | exception_path | partner feedback delay | Metric / Indicator Governance | Are partner/channel SLA metrics planned? | partner_feedback_delay has owner and source | crm_plan_domain_exception_path | PASS |
| crm | Plan | Architecture / Data / AI Agent | permission_privacy_path | row/field scope | Policy / Privacy Constraints | Are tenant/customer/partner scopes planned? | cross-tenant and cross-partner access blocked | crm_plan_arch_permission_privacy_path | PASS |
| crm | Plan | QA Agent | lifecycle_transition | renewal plan | State Machines | Can QA plan customer success lifecycle tests? | RenewalPlan planned -> renewed/churned is explicit | crm_plan_qa_lifecycle_transition | PASS |
| crm | Plan | Coding Agent | acceptance_test_path | AGENTS handoff | UI / Mobile Patterns | Are delivery paths and source order defined? | delivery/manifest and source_of_truth_order are required | source_of_truth_order;manifest.json | PASS |
| crm | Tasks | PM Agent | happy_path | customer issue handling | Core Workflows | Are slices tied to customer closure? | ticket closed or demand created | ticket_to_demand_trace | PASS |
| crm | Tasks | Domain Expert Agent | exception_path | quote rejected | State Machines | Are rejected/expired quote tasks split? | Quote states are not hidden under management | crm_tasks_domain_exception_path | PASS |
| crm | Tasks | Architecture / Data / AI Agent | permission_privacy_path | Customer 360 masking | UI / Mobile Patterns / Policy | Do tasks preserve field-level masking? | customer360_masking is acceptance relevant | customer360_masking | PASS |
| crm | Tasks | QA Agent | lifecycle_transition | ticket escalation | Domain Test Scenarios | Are escalation and urgent response tasks planned? | TicketEscalated and ResponseTask created | sla_response_task | PASS |
| crm | Tasks | Coding Agent | acceptance_test_path | data-* mapping | UI / Mobile Patterns | Can coding tasks map views/actions? | data-testid/data-action/data-state/data-api/data-method are required | data-testid;data-action;data-state;data-api;data-method | PASS |
| crm | Build/Verify | PM Agent | happy_path | boss exception cockpit | Role Path Patterns | Does build close operating exceptions? | owner action and verification visible | crm_build_pm_happy_path | PASS |
| crm | Build/Verify | Domain Expert Agent | exception_path | ticket to demand loop | Domain Test Scenarios | Is product feedback traceable? | DemandCreatedFromTicket links service to roadmap | ticket_to_demand_trace | PASS |
| crm | Build/Verify | Architecture / Data / AI Agent | permission_privacy_path | AI suggestion | Policy / Privacy Constraints | Does AI remain supporting behavior? | no payment/contract/ticket closure without human approval | crm_build_arch_permission_privacy_path | PASS |
| crm | Build/Verify | QA Agent | lifecycle_transition | mobile weak network | Domain Test Scenarios | Are offline drafts and duplicate prevention tested? | draft preserved and no data loss | crm_build_qa_lifecycle_transition | PASS |
| crm | Build/Verify | Coding Agent | acceptance_test_path | AC validation | Acceptance Checklist | Can tests bind to FRR and prototype? | ac_structured and data-* coverage required | ac_structured;data-testid;data-action | PASS |
| crm | Launch | PM Agent | happy_path | lead-to-cash launch | Aggregates and Entities / Events | Are revenue-critical events ready? | lead_to_cash_trace covers LeadAssigned -> PaymentRegistered | lead_to_cash_trace | PASS |
| crm | Launch | Domain Expert Agent | exception_path | churn risk intervention | Domain Test Scenarios | Are renewal risk launch controls explicit? | RenewalPlan closes renewed/churned with evidence | crm_launch_domain_exception_path | PASS |
| crm | Launch | Architecture / Data / AI Agent | permission_privacy_path | export and finance | Policy / Privacy Constraints | Are export and sensitive fields audited? | export requires audit and role masking | crm_launch_arch_permission_privacy_path | PASS |
| crm | Launch | QA Agent | lifecycle_transition | contract/payment | Aggregates and Entities | Can smoke tests cover payment overdue path? | Contract partially_paid/paid/overdue is testable | crm_launch_qa_lifecycle_transition | PASS |
| crm | Launch | Coding Agent | acceptance_test_path | release package | Acceptance Checklist | Can coding agent identify launch blockers? | package paths and acceptance evidence are explicit | crm_launch_coding_acceptance_test_path | PASS |
| crm | Learn/Retire | PM Agent | happy_path | funnel learning | Metric / Indicator Governance | Can post-launch learning improve conversion/SLA? | metrics have owners and sources | crm_learn_pm_happy_path | PASS |
| crm | Learn/Retire | Domain Expert Agent | exception_path | deprecated playbook | Content / Knowledge Assets | Can outdated policies/playbooks retire safely? | playbook versions and governance exist | crm_learn_domain_exception_path | PASS |
| crm | Learn/Retire | Architecture / Data / AI Agent | permission_privacy_path | retained customer data | Policy / Privacy Constraints | Are retention/export/privacy risks visible? | customer sensitive data remains scoped/audited | crm_learn_arch_permission_privacy_path | PASS |
| crm | Learn/Retire | QA Agent | lifecycle_transition | response task regression | State Machines | Can regression preserve SLA lifecycle? | pending/overdue/escalated/closed remains covered | sla_response_task | PASS |
| crm | Learn/Retire | Coding Agent | acceptance_test_path | historical AC | Acceptance Checklist | Can old AC IDs remain stable after iteration? | acceptance_test_path and source_of_truth_order preserved | crm_learn_coding_acceptance_test_path | PASS |

## Multi-Module PRD Quality Gate

Apply this gate after generating all CRM module PRDs or after splitting a large
CRM PRD into a master contract plus module PRDs. Any failed required item means
`REVIEW_COMPLETE_WITH_GAPS`.

| Gate | Required Condition | Blocks |
|---|---|---|
| CRM-G1 Cross-module handoff | For every CRM handoff, the source module FRR states trigger action, target module, emitted event/audit, and failure path; the target module FRR states received data, initial state, duplicate rule, and owner; the master contract has field mapping and notification/event reference. | objects such as contracts, demands, or response tasks appearing without trace |
| CRM-G2 Alert rule back-reference | Each configured response/alert rule such as R01-R12 is explicitly cited in the producing source module business rules using the pattern `Rxx -> creates M02 ResponseTask; owner=...; close_guard=...`. | alerts generated by rules that the source module never states |
| CRM-G3 Entity/event/notification integrity | ER lines, field mappings, domain events, notification catalog, audit rule, and E2E row exist for lead-to-cash, ticket-to-demand, demand-to-iteration, contract/payment, partner/channel, and campaign handoff flows that are in scope. | master contract omissions that module PRDs cannot repair |
| CRM-G4 Prototype testability | When a locked prototype exists, module sections for layout, flow, modal/detail, and acceptance reference stable `data-testid` / `data-action` anchors for primary happy and negative paths. | human-readable paths that QA/RPA/AI tests cannot locate |

Post-generation CRM checklist:

1. Master contract states module IDs, source-of-truth order, role/data scope,
   entity relations, field mappings, event/notification catalog, and audit rule.
2. Each module PRD has release functions, role paths, state/button matrix,
   business rules, exceptions, and test/acceptance rows.
3. Lead -> opportunity -> customer -> contract -> payment is covered or
   explicitly de-scoped.
4. Ticket -> demand -> iteration/release is covered or explicitly de-scoped.
5. Campaign/partner/customer-success/CPQ/renewal flows are included or
   explicitly deferred with owner and revisit condition.
6. Every ResponseTask/alert has source rule, owner, SLA, close guard, and
   target business action.
7. Every money, contract approval, payment confirmation, roadmap commitment,
   and customer-service closure keeps human accountability.
8. Customer 360 aggregates cite their source modules and masking rules.
9. Tests cover happy, validation, permission, duplicate, stale-state, timeout,
   and dependency-failure paths for P0/P1 CRM flows.
10. If prototype evidence exists, action/testid coverage gaps are listed before
    any `PASS` claim.

## Acceptance Checklist

- [ ] Lead, opportunity, customer, ticket, contract/payment, response task states are defined.
- [ ] Marketing/campaign, quote/CPQ, renewal/customer success, partner/channel,
      and product-demand loops are included or explicitly out of scope.
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
