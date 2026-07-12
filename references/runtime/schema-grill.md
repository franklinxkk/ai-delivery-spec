# Schema-Driven Grill / Schema 靶向追问

Use this optional mode when material unknowns remain after evidence inventory.
It is adversarial about missing contracts, not aggressive toward the user.

## Target selection

Choose the highest-impact open `UNK-*` from the Discovery Contract. Ask one
question that can close or split that unknown. Typical targets are outcome,
scope, role authority, state boundary, data authority, compliance, commercial
promise, and acceptance.

Do not ask a generic checklist. Cite the source or conflict that made the
question necessary. Offer a proposed default only when accepting it would not
silently create a P0 business or risk decision.

## Turn contract

After each answer, record a `schemas/clarification-transcript.schema.json` turn:

```yaml
turn_id: TURN-SCOPE-001
unknown_id: UNK-SCOPE-001
question: Which end-to-end slice is approved for the first release?
answer: Resource version through learner evidence; billing is excluded.
decision_owner: accountable product owner
status: answered
evidence_refs: [meeting-2026-07-11]
```

Compile only structured, owner-attributed answers. Free-form chat remains
evidence input and requires the agent to produce this reviewable structure;
the deterministic compiler does not pretend to understand arbitrary prose.

## Convergence

Stop when all P0 unknowns are answered or accepted by an accountable owner, or
when the configured stage-turn limit is reached. At the limit, return control
to a human with unresolved IDs; never continue a propose/reject loop.

Compile with:

```bash
python scripts/compile_clarification_transcript.py --contract discovery.yaml --transcript transcript.yaml --decision READY_FOR_PRODUCT_TRUTH --output discovery-next.yaml
```
