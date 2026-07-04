# Multi-Domain Package Example

Use this example when one product crosses more than one domain module, such as
CRM customer operations plus OA unified todo plus data mart reporting.

## Example Prompt

```text
Use AI Delivery Spec.
Design a CRM response center that sends approved customer issues into OA
unified todo, then aggregates SLA and conversion indicators in a data mart.
Produce the Domain Composition Map, Cross-Module Flow Contract, E2E Canvas,
delivery manifest, and IA Skeleton.
```

## Domain Composition Map

| Domain | Value Object | Source Of Truth | Lifecycle State | High-Risk Boundary | Shared Owner |
|---|---|---|---|---|---|
| CRM | Lead / Ticket / Demand | CRM module | lead -> opportunity, ticket -> demand | customer data scope and follow-up SLA | sales/service owner |
| OA | Todo / Workflow Instance | OA workflow engine | pending -> processing -> closed | workflow_human_gate and audit opinion | process owner |
| Data Mart | Indicator / Report | metric catalog | draft -> published -> reviewed | metric caliber and row-level permission | data owner |

Conflict rule: if CRM says a ticket is closed but OA todo is still open, the
E2E canvas must mark the lifecycle as `CONFLICT` and stop at
`REVIEW_COMPLETE_WITH_GAPS` until the source-of-truth owner decides.

## Cross-Module Flow Contract

| Source State | Domain Event | Target Module | Target State | Field Mapping | Guard |
|---|---|---|---|---|---|
| Ticket.confirmed_need | `TicketConvertedToDemand` | CRM Demand | pending_review | ticket_id -> demand.ticket_id | customer permission scope |
| Demand.approved | `DemandTodoCreated` | OA Todo | pending | demand_id -> todo.source_id | workflow_human_gate |
| Todo.closed | `TodoClosedForDemand` | Data Mart | indicator_refresh_pending | todo.sla_result -> metric.sla_result | metric owner approval |

## E2E Cross-Module Canvas

| E2E Path | Start | Event Chain | End | Acceptance |
|---|---|---|---|---|
| service issue to product improvement | customer ticket confirmed | TicketConvertedToDemand -> DemandTodoCreated -> TodoClosedForDemand | demand SLA visible in data mart | QA can replay the full chain with shadow data |

## Files

- [delivery/manifest.json](delivery/manifest.json)
- [delivery/ia-skeleton.yaml](delivery/ia-skeleton.yaml)
