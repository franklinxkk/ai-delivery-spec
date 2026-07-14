# Requirement Review And Acceptance

## Review Closure

Bind every review finding to `REV-*` and one or more `REQ-*`/behavior IDs.
Record severity, owner, disposition, resolution and evidence. `P0/P1` findings
must be resolved, explicitly deferred by an authorized owner, or reported as a
blocker before baseline.

Review dimensions:

- outcome, source precedence, scope and dependencies;
- role journey and cross-role/cross-module handoff closure;
- permission, data scope, state, rule, exception and recovery;
- field/data/integration semantics and reconciliation;
- readable main document and non-inventive engineering annex;
- acceptance executability and traceability.

## Acceptance Definition

An `AC-*` is executable only when it names:

- requirement/behavior references;
- preconditions and actor/data scope;
- steps or input;
- expected visible and domain results;
- negative/exception behavior when applicable;
- mandatory evidence type.

## Acceptance Run

Use `schemas/acceptance-run.schema.json`. Each `ARUN-*` records baseline,
environment, executor, item results, actual behavior, evidence, defects,
residual issues and sign-off.

Allowed item results: `pass`, `fail`, `blocked`, `not_run`. Allowed conclusions:
`accepted`, `accepted_with_conditions`, `rejected`, `pending`.

`accepted_with_conditions` must name each condition, accountable owner and due
criterion. A requirement reaches `accepted` only when mandatory AC has executed
evidence and the sign-off allows it.

## Reverse Trace

For every failed item or defect, verify:

```text
ARUN item / DEFECT → AC → behavior ID → REQ → SRC / CHG
```

If the reverse path is missing, classify the finding as a missing requirement,
orphan test, implementation defect or undocumented change before disposition.

## Evidence Honesty

Generated documents, mock screenshots and embedded `PASS` strings are not proof
of execution. Name the tool/person, time, environment, location and result.
Use `REVIEW_COMPLETE_WITH_GAPS` when the structure is sound but execution or
external sign-off is still pending.
