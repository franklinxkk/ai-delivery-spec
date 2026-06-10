# Multi-Surface Consistency

Use this file when a product has multiple surfaces: PC, H5, mini-program, app, mobile web, large screen, embedded device, AI chat surface, or browser extension.

Mobile design can differ from desktop. Business state, permissions, domain results, and action semantics must stay consistent unless explicitly declared otherwise.

## Surface Matrix

| Feature / Story | PC | Mobile/H5 | Mini-Program/App | Large Screen/Other | Shared Domain Result | Allowed Differences |
|---|---|---|---|---|---|---|
| Create ticket | full form | simplified sticky action | photo/voice optional | no | TicketCreated | fields, layout, input mode |

## Consistency Contract

Must be shared:
- core domain model;
- state machine;
- permission guard;
- audit/event;
- command/query semantics;
- idempotency for write actions;
- required test case.

May differ:
- navigation depth;
- layout;
- density;
- input mode;
- offline behavior;
- notification entry;
- testid prefix.

## Cross-Surface Action Mapping

| Business Action | PC `data-action` | Mobile `data-action` | App/Mini `data-action` | Guard | Domain Result |
|---|---|---|---|---|---|
| submit ticket | `save-ticket` | `save-ticket` | `save-ticket` | user can create ticket for customer | TicketCreated |

Rules:
- Same business action should reuse action name where possible.
- If action name differs, provide a mapping row.
- Same action with different guard/domain result counts as separate action.

## Fail Conditions

- Mobile creates a different state than PC for the same business action.
- PC allows action that mobile forbids without reason.
- Mini-program has weaker permission guard than PC.
- One surface shows stale or incompatible status names.
- QA cannot trace the same story across surfaces.

## Acceptance

Before delivery:
- run one complete role path per surface;
- run one cross-surface continuation path, e.g. PC creates, mobile handles, PC verifies;
- run one permission/isolation test per surface;
- list intentionally missing surface capabilities.
