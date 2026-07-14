# Requirement Checkpoint And Micro-Gate Protocol

Load this reference for long-running, resumed, regulated, audit-heavy or formal
acceptance work. It preserves requirement decisions when conversation context
does not survive. It is not a sprint, code, release or operations manager.

## Guarantee Boundary

- A repository file remains mutable. Hash chains detect local changes; only an
  accountable external signing/evidence service provides stronger guarantees.
- Reload the checkpoint before every requirement stage instead of relying on
  prompt memory.
- Coverage means each baselined `REQ-*` has source, behavior and acceptance
  links. Deferred, rejected and approved gaps stay explicit.
- Risk classification selects rigor; it does not grant domain maturity, expert
  approval or legal applicability.

## Runtime Artifacts

| Artifact | Purpose |
|---|---|
| `execution-state.yaml` | versions, risk, access scope, anchors, requirement stage and prior-state hash |
| `gate-<id>.yaml` | checks and evidence bound to one state hash |
| Product Truth `REQ-*` | optional large-project trace authority |
| unified PRD | one human baseline and engineering annex |
| Context Plan | retrieval budget, never a requirement authority |

Use a Discovery Contract before a specification exists. Each checkpoint copies
the active contract/config into a snapshot. Edit the working file, then run
`checkpoint`; never edit a snapshot.

```powershell
py -3 scripts/manage_execution_state.py create --truth product-truth.yaml --config spec.config.yaml --installed-skill C:/path/to/ai-delivery-spec/SKILL.md --execution-id EXEC-PROJECT-001 --output evidence/state-000.yaml
py -3 scripts/manage_execution_state.py verify --state evidence/state-000.yaml
py -3 scripts/manage_execution_state.py gate --state evidence/state-000.yaml --gate-id contract_traceability --projection requirements/PRD.md --output gate-contract.yaml
```

Advance exactly one requirement stage after all required gates pass. Record
material clarification/review turns with `record-turn`; exceeding
`execution.max_turns_per_stage` preserves the last stable checkpoint.

## Stages

```text
intake → clarify → specify → review → baseline → change → acceptance → closed
```

An implementation status may be attached as an external reference; it cannot
replace or advance this requirement state.

## Active Gates

1. `version_environment`: expected/repository/installed skill and dependencies.
2. `complexity_domain`: structured risk, tier and honest domain evidence.
3. `context_survival`: state, contract/config and evidence anchor hashes.
4. `discovery_readiness`: outcome, scope, owner and P0 unknown closure at intake.
5. `contract_traceability`: `REQ-*` source/behavior/AC links and unified PRD coverage.
6. `audit_access`: allow/deny scope, accountable approval and tamper evidence.
7. `fallback_risk`: fail closed for high risk; explicit human-reviewed gap only
   when policy permits.

At each transition: verify state, load the required ID slice, run gates, attach
human evidence when triggered, advance one node and retain the prior checkpoint.
After interruption, resume only from the latest state whose hashes and anchors
still verify.

## Failure Policy

- High-risk validation failure: `BLOCKED`.
- A declared validator outage may become `approved_with_gap` only under the
  configured low-risk human-review policy; it is never PASS.
- Missing links, stale gate results, scope downgrade or version drift block the
  affected requirement baseline.
