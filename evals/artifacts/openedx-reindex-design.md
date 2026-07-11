# Open edX Reindex Workflow — Brownfield Design Evaluation

Case: `GH-OPENEDX-REINDEX`

Pinned repository: `openedx/openedx-platform@264ced21b08ac56906d233abf86a1db7d661b0c8`

The source issue describes the desired upgrade behavior. Repository inspection
shows that much of it already exists: `reindex_studio` queues an incremental
Celery task, records resumable progress, treats incremental mode as the only
mode, and accepts removed flags with warnings for old automation. Therefore a
new delivery must describe a delta, not regenerate the original feature.

## Verified current behavior

- `OBL-EDX-REQ-LARGE`: the command no longer performs a synchronous full build;
  it queues background work and returns a task ID when Celery is not eager.
- `OBL-EDX-REQ-RESUME`: the command documents resumable progress through
  `IncrementalIndexCompleted`; current tests cover enqueue, disabled search,
  old-flag warnings, incremental invocation, lock contention, and idempotent
  repeated task calls.
- `OBL-EDX-DES-STATE`: repository evidence supports prepared by migration,
  queued, incrementally populating, interrupted/resumable, and completed states.
  Failed, stale, and operator-cancelled behavior remains a product/operations
  gap until verified in the task and API implementation.
- `OBL-EDX-DES-OPS`: current output points operators to Celery logs and gives a
  manual progress-reset command. A user-facing progress query, SLA, alert,
  cancellation, and automatic rollback are not proven.

## Safe next change shape

Any new request must choose one named gap, preserve removed-flag compatibility,
and include current-state regression. Candidate slices include observability,
operator progress, safe reset authorization, or failure recovery. “Implement
async incremental reindexing” is rejected as stale because the pinned baseline
already contains it.

Completion: `REVIEW_COMPLETE_WITH_GAPS` — current-state and remaining design
gaps were separated; production scale, operator usability, and new code are not
validated.
