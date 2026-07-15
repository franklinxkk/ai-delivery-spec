# GitHub Scenario Evaluation Artifacts

These bounded artifacts record requirement/design/coding observations against
pinned repositories. They do not authorize roadmap changes or prove production
behavior.

## GH-CHATWOOT-VOICE — Requirement Clarification

Pinned repository: `chatwoot/chatwoot@98154bbeab2f5ea888dcb61bfd3a35a109ebb9a0`.
The issue describes a useful outcome but the repository already contains voice,
recording and model behavior, so current-state parity must precede a new PRD.

- Outbound must define permitted identity/endpoint, connecting through terminal
  states, concurrency, provider rejection and retry-safe timeout.
- Inbound must define account/inbox ownership, eligible agents, single accept
  ownership, reject/missed/timeout, duplicate webhook and disconnect behavior.
- Routing, working hours, consent, retention, AI/transcript use, emergency and
  geography, pricing, number provisioning, transfer/hold and audit remain named
  decisions.

Completion: `REVIEW_COMPLETE_WITH_GAPS`; production behavior and policy answers
remain unverified.

## GH-SALEOR-CHANNEL-ID — Product Design

Pinned repository: `saleor/saleor@697b9ec6ffb93199f62f783e7bf6c550cd3bcf7e`.
The issue is user evidence, not roadmap approval. The pinned baseline exposes a
channel slug, so an ID selector must preserve availability, permission,
pagination and filtering semantics.

- Accept exactly one of immutable `channelId`, explicit `channelSlug` and the
  legacy `channel`; multiple selectors return a stable argument error.
- Preserve the legacy selector for a declared compatibility window and do not
  silently reinterpret it.
- ID lookup changes identity resolution only and must not broaden visibility,
  permissions or database routing.
- Tests cover each selector, conflicts, defaults, permissions, renamed slugs,
  pagination/filter parity and generated schema.

Completion: `REVIEW_COMPLETE_WITH_GAPS`; maintainer decision and code execution
are not proven.

## GH-OPENEDX-REINDEX — Brownfield Design

Pinned repository: `openedx/openedx-platform@264ced21b08ac56906d233abf86a1db7d661b0c8`.
Repository inspection shows async incremental and resumable behavior already
exists, so a new delivery must describe a delta rather than regenerate it.

- Preserve queued incremental work, task ID behavior, resumable progress,
  removed-flag compatibility and existing lock/idempotency tests.
- Failed, stale and operator-cancelled behavior, user-facing progress, SLA,
  alerting and rollback remain gaps until verified.
- Candidate slices are observability, operator progress, safe reset authority
  or failure recovery, each with current-state regression.

Completion: `REVIEW_COMPLETE_WITH_GAPS`; scale, operator usability and new code
are not validated.

## GH-ORANGEHRM-PASSWORD-POLICY — Coding Handoff

Pinned repository: `orangehrm/orangehrm@56e23b3b09e7af29317a0943523b825843fff527`.
Frontend already calls server password validation and the backend contains
policy/validation/configuration surfaces that must be probed before edits.

Required slices cover authorized policy read, versioned/audited update,
server-side enforcement parity across every password write path, and declared
transition/rollback for existing accounts, invitations, resets and sessions.
Tests cover permission denial, invalid policy, every write path, message parity,
effective time, audit, rollback and concurrent update conflict.

Forbidden: client-only enforcement, plaintext logging, unanalysed endpoint
breakage or treating an old issue as current roadmap approval.

Completion: `REVIEW_COMPLETE_WITH_GAPS`; backend path inspection,
implementation and executed tests remain required.
