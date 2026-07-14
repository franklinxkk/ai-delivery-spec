# Real-time Contract

Load this file when the product includes SSE (Server-Sent Events), WebSocket,
countdown timers, real-time alerts, push notifications, polling strategies, or
any mechanism where the server pushes updates to the client without a
user-initiated refresh.

## Contents

- When To Load
- SSE Event Type Definition
- SLA Countdown Strategy
- Alert Rule Engine
- Reconnection And Polling Strategy

## When To Load

Load this file in addition to `references/specify.md` when any trigger applies:

| Trigger | Action |
|---|---|
| Product has real-time data push (SSE, WebSocket, long-polling) | Load full file |
| Product has countdown timers or SLA display | Load SLA Countdown section |
| Product has alert/warning rules that generate tasks or notifications | Load Alert Rule Engine section |
| Prototype has `EventSource`, `WebSocket`, `setInterval` with server sync, or timer-based UI updates | Load full file |

Do not load this file for simple HTTP request-response CRUD without any
real-time or timer-driven behavior.

## SSE Event Type Definition

When the product uses SSE or WebSocket for real-time updates, every event type
must be declared with its payload schema, trigger condition, and consuming
pages.

### Event Type Registry

| event_type | payload_schema | trigger_condition | consumer_page | consumer_component | ui_update_strategy | retry_on_miss |
|---|---|---|---|---|---|---|
| task.created | `{ taskId, title, assigneeId, priority, createdAt }` | backend creates a new task and assignee is online | /workbench | TaskList | prepend to list + highlight 2s + badge++ | yes, GET /tasks?since={lastEventId} |
| task.updated | `{ taskId, field, oldValue, newValue, updatedBy, updatedAt }` | any task field changes for a task the user can see | /workbench, /task-detail | TaskList, TaskDetail | update row in-place + flash 1s | yes, GET /tasks/{id} |
| task.completed | `{ taskId, completedBy, completedAt }` | task marked as done | /workbench | TaskList | move to completed section + strike-through | yes, GET /tasks?status=completed&since={lastEventId} |
| alert.triggered | `{ alertId, ruleId, entity_type, entity_id, level, message, triggeredAt }` | alert rule engine matches a condition | /dashboard, /alerts | AlertBanner, AlertList | show toast + add to alert list + play sound (if enabled) | yes, GET /alerts?since={lastEventId} |
| sla.warning | `{ taskId, remainingSeconds, threshold }` | SLA countdown crosses warning threshold | /workbench, /task-detail | SlaTimer | change timer color to warning (amber) | no, timer is client-side |
| sla.expired | `{ taskId, expiredAt }` | SLA countdown reaches zero | /workbench, /task-detail | SlaTimer | change timer to expired (red) + escalate | no, timer is client-side |

### Payload Schema Rules

- Every event type must have a versioned schema. When the schema changes, bump
  the version and maintain backward compatibility for at least one release.
- `payload_schema` must list every field with its type and whether it is
  required or optional.
- `consumer_page` must list every page that listens to this event.
- `consumer_component` must list the specific UI component(s) that update.
- `ui_update_strategy` must describe exactly how the UI changes when the event
  is received (prepend, update in-place, flash, badge increment, toast, sound,
  etc.).
- `retry_on_miss` defines what happens if an event is missed (connection drop):
  whether the client should fetch a snapshot to catch up, and which API endpoint
  to call.

### Event Delivery Guarantees

| Guarantee Level | Description | Use When |
|---|---|---|
| at-most-once | event may be lost; no retry | non-critical notifications (e.g., "someone is typing") |
| at-least-once | event delivered at least once; may duplicate; consumer must be idempotent | task updates, alert triggers |
| business-effect-once | transport may duplicate or reorder; one business effect is enforced by command idempotency, state guards, a durable processing ledger and reconciliation | financial, compliance, safety or other consequential state changes |

Rules:

- Most real-time updates should use `at-least-once` with client-side
  deduplication via `event_type + entityId + updatedAt` composite key.
- Do not claim end-to-end `exactly-once` from an event ID or transport feature.
  When duplicates cause harm, define the authoritative state, idempotency key,
  allowed transition, durable receipt/result lookup, compensation and owner-led
  reconciliation.

## SLA Countdown Strategy

When the product displays SLA timers (response time, resolution time, deadline
countdown), the PRD must specify the timer strategy, color thresholds, and
server time calibration.

### Timer Strategy Table

The values below are examples of a contract shape, not defaults. Every duration,
threshold, pause rule and escalation needs a project source, owner and acceptance
boundary before it becomes a requirement.

| Timer ID | Display Name | Start Condition | Duration | Pauses On | Resumes On | Display Format | Color Thresholds |
|---|---|---|---|---|---|---|---|
| SLA-01 | 响应倒计时 | task assigned to agent | 2h | task paused, task completed | task resumed | HH:MM:SS | >50% green; 20-50% amber; <20% red; 0 expired |
| SLA-02 | 处理倒计时 | task accepted by agent | 24h | task paused, task completed | task resumed | DD天HH时 | >50% green; 20-50% amber; <20% red; 0 expired |
| SLA-03 | 超时预警 | alert triggered | 1h | alert acknowledged | N/A (one-shot) | MM:SS | >50% green; <50% amber; 0 red |

### Color Threshold Rules

| State | Condition | CSS Class | Color Token | Hex | Behavior |
|---|---|---|---|---|---|
| normal | remaining > 50% of total | .sla-normal | var(--brand) | #e8f1ff | normal display |
| warning | 20% < remaining ≤ 50% | .sla-warning | var(--warn) | #fff3df | amber display + pulse animation |
| danger | 0 < remaining ≤ 20% | .sla-danger | var(--danger) | #ffe9e6 | red display + pulse animation + supervisor notification |
| expired | remaining ≤ 0 | .sla-expired | var(--danger-dark) | #ff4d4f | red solid + escalate + auto-create overdue task |

### Server Time Calibration

Client-side timers drift from server time. The PRD must specify how timers are
calibrated:

| Property | Required Content |
|---|---|
| Time source | server time (from API response header `Date` or dedicated `/api/server-time` endpoint) |
| Sync frequency | project-confirmed trigger/frequency; for example page load, reconnect and relevant state event |
| Drift tolerance | project-confirmed adjustment and warning thresholds with clock/source evidence |
| Timer computation | `remaining = serverDeadline - serverNow; display = formatDuration(remaining)` |
| Client disconnect | on reconnect, fetch latest task state and recompute timer from server deadline |
| Timezone | project-confirmed storage, calculation and display zones; never copy UTC+8 without a source |

Rules:

- Never rely solely on `setInterval` with client time. Always compute remaining
  time from server deadline minus server time.
- When the client reconnects after a disconnect, the timer must re-sync from
  the server, not continue from where it left off.
- If the server deadline changes (task paused then resumed), the timer must
  recompute from the new deadline.

## Alert Rule Engine

When the product has an alert/warning system that monitors conditions and
triggers actions, the PRD must specify the rule definitions, trigger chain, and
escalation policy.

### Rule Definition Table

| Rule ID | Rule Name | Entity Type | Condition | Threshold | Severity | Trigger Action | Escalation |
|---|---|---|---|---|---|---|---|
| RULE-01 | 响应超时 | task | `task.assignedAt + sla.response < now()` | 2h | warning | create alert + notify assignee + notify supervisor | after 30min: escalate to department head |
| RULE-02 | 处理超时 | task | `task.acceptedAt + sla.processing < now()` | 24h | danger | create alert + notify assignee + reassign option | after 1h: auto-escalate + create overdue task |
| RULE-03 | 重复提交 | form | `same entity submitted within 5min by same user` | 5min | info | block submission + show "您刚提交过相同内容" | N/A |
| RULE-04 | 高危操作 | any | `action in [delete, purge, export-all] and target has > 100 records` | 100 records | warning | require secondary confirmation + supervisor approval | if rejected: log + notify |

### Trigger Chain

When a rule matches, the system must execute a defined chain of actions:

```text
rule matches → create alert record → push SSE event → update UI (toast + badge + list) → create notification (if configured) → escalate (if threshold met)
```

Chain specification:

| Step | Action | Actor | Failure Behavior | Audit |
|---|---|---|---|---|
| 1 | Rule engine evaluates condition | system (cron or event-triggered) | log error + retry 3x | rule_id, entity_id, matched_at |
| 2 | Create alert record in database | system | if DB fails: retry with backoff; if still fails: dead-letter queue + ops alert | alert_id, rule_id, entity_id, severity |
| 3 | Push SSE event to online users | SSE server | if SSE fails: fall back to polling; client will catch up on reconnect | event_id, alert_id, delivered_to[] |
| 4 | Update UI: toast + badge increment + list prepend | client (SSE handler) | if UI update fails: next polling cycle will refresh | N/A (client-side) |
| 5 | Create notification record (in-app / SMS / email) | notification service | if notification fails: retry 3x; if still fails: log + mark for retry | notification_id, channel, status |
| 6 | Escalate (if threshold met) | escalation job | if escalation fails: retry + ops alert | escalation_id, escalated_to, escalated_at |

### Rule Evaluation Frequency

| Rule Type | Evaluation Trigger | Frequency |
|---|---|---|
| Time-based (SLA, deadline) | cron job | every 1 minute |
| Event-based (form submit, state change) | event listener | real-time |
| Data-based (threshold, count) | scheduled query | every 5 minutes |
| Composite (time + data) | cron + event | time check every 1min; event check real-time |

## Reconnection And Polling Strategy

When the product uses SSE or WebSocket, the PRD must specify what happens when
the connection drops and how the client recovers.

### Reconnection Strategy

The values in this table illustrate required decisions. They are not shared
defaults; derive them from business freshness, load, device/network conditions
and failure tolerance.

| Property | Required Content |
|---|---|
| Heartbeat interval | project-confirmed interval or protocol-managed heartbeat |
| Heartbeat timeout | project-confirmed stale/dead threshold and evidence source |
| Max retry attempts | bounded project-confirmed attempts or duration |
| Retry backoff | project-confirmed capped backoff with jitter where applicable |
| Max retry duration | project-confirmed degradation trigger |
| On reconnect | re-fetch missed events via `GET /events?since={lastEventId}` |
| Connection states | connecting → connected → disconnected → reconnecting → polling (degraded) |
| UI indicator | green dot (connected), yellow dot (reconnecting), red dot (disconnected/polling) |
| User message | "实时连接已断开，正在尝试重连..." / "已切换到轮询模式，数据可能有延迟" |

### Polling Strategy (Degraded Mode)

When SSE/WebSocket cannot be restored, the client falls back to polling:

| Data Type | Polling Endpoint | Frequency | Conflict Handling | Data Scope |
|---|---|---|---|---|
| Task list | project endpoint | project-confirmed | compare authoritative version/cursor; preserve safe local draft | current authorized scope |
| Alert list | project endpoint | project-confirmed | deduplicate by stable event/alert ID and refresh authoritative snapshot | current authorized scope |
| Dashboard metrics | project endpoint | project-confirmed | replace or merge according to metric version/freshness contract | authorized widgets |
| SLA timers | authoritative deadline endpoint/event | display tick plus project-confirmed resync | recompute from authoritative deadline | current authorized object |

### Polling Conflict Handling

| Scenario | Resolution Rule |
|---|---|
| Polling returns newer data than client has | server wins; client replaces local state |
| User modified data locally that hasn't been saved | preserve local draft; show "有未保存的更改" warning |
| Polling returns 401 (session expired) | stop polling; redirect to login |
| Polling returns 5xx | retry 3 times with 2s interval; if still failing: show "数据加载失败" + manual retry button |
| SSE reconnects while polling is active | stop polling; switch to SSE; fetch missed events via `since={lastEventId}` |

### Degradation Rules

- Polling is a degraded mode, not a replacement. The UI must indicate that
  real-time updates are unavailable.
- Polling frequency must be conservative and project-confirmed from freshness,
  capacity and failure tolerance; this reference defines no universal default.
- If polling also fails (network down), show offline indicator and queue
  only actions explicitly approved as queueable. Classify actions as read-only,
  local draft/evidence capture, reversible command, or consequential command.
  Safety, money, clinical, permission, final-approval and other irreversible
  commands are blocked offline by default; never queue them merely because the
  UI can store a request.
- When SSE reconnects, the client must fetch all missed events using the last
  received event ID. Do not assume the SSE stream replays missed events.
