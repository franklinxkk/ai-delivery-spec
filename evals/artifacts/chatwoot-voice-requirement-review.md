# Chatwoot Voice Channel — Requirement Clarification Evaluation

Case: `GH-CHATWOOT-VOICE`

Pinned repository: `chatwoot/chatwoot@98154bbeab2f5ea888dcb61bfd3a35a109ebb9a0`

The issue provides a useful v1 outcome but is not sufficient for delivery. The
pinned repository already contains Twilio voice services, recording attachment
logic, migration, and model specs, so the issue may describe behavior that is
partly implemented. Current-state parity must precede any new PRD.

## Requirement closure

- `OBL-CW-REQ-OUTBOUND`: agent selects a permitted account phone identity and
  contact endpoint, initiates a call, sees connecting/ringing/connected/ended or
  failed state, and cannot create a second active call unless concurrency policy
  permits it. Provider rejection and timeout have visible, retry-safe results.
- `OBL-CW-REQ-INBOUND`: an inbound provider event creates or associates a call
  with the owning account/inbox, presents ringing to eligible agents, grants one
  agent ownership on accept, and produces explicit reject, missed, timeout,
  duplicate-webhook, and provider-disconnect results.
- `OBL-CW-REQ-UNKNOWN`: routing strategy, working hours, recording consent,
  media retention, transcript/AI use, emergency calling, geographic support,
  pricing, number provisioning, transfer/hold, and audit/export remain named
  decisions. They are not silently included in “basic voice support.”

## Material questions only

1. Which account/inbox owns a number, credentials, call record, and recording?
2. Which roles may initiate, receive, listen to, download, or delete call media?
3. What is the authoritative provider event order and duplicate/retry policy?
4. What must happen when the browser disconnects but the provider call remains?
5. Is recording enabled, and who supplies jurisdiction-specific consent and
   retention policy?

Completion: `REVIEW_COMPLETE_WITH_GAPS` — the issue was converted into bounded
behavior and material unknowns; current production behavior and policy answers
remain unverified.
