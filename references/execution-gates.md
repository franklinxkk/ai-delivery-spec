# Execution State And Micro-Gate Protocol

Load this reference for long-running, multi-agent, resumed, regulated,
production, migration, or formal acceptance work. It operationalizes the
runtime self-check without assuming that conversation context survives.

## 1. Guarantee Boundary

- A repository file is mutable. Hash chains make changes detectable; only an
  enterprise signing service or immutable evidence store can provide stronger
  guarantees.
- Prompt text is not inherently immutable. Reload the checkpoint before every
  stage and reject anchor drift instead of relying on prompt memory.
- Coverage means every approved in-scope Feature has behavior and acceptance
  refs. Raw ambiguity, deferred scope, not-applicable scope, and accepted gaps
  remain explicit; do not relabel them to manufacture 100%.
- Automatic risk classification selects rigor. It never grants domain
  maturity, expert approval, audit status, or production eligibility.

## 2. Runtime Artifacts

| Artifact | Purpose |
|---|---|
| `execution-state.yaml` | version, environment, risk, domain assurance, access scope, immutable anchors, stage and prior-state hash |
| `gate-<id>.yaml` | checks and evidence bound to one state hash and lifecycle node |
| Product Truth `FEAT-*` | approved scope key from source evidence to behavior and acceptance |
| Context Plan | adaptive retrieval budget; not an authority or maturity override |

Use a Discovery Contract before Product Truth exists. Each checkpoint copies
the active contract/config into an immutable snapshot. Edit the working file,
then run `checkpoint`; never edit a snapshot in place.

Create and verify a checkpoint:

```powershell
py -3 scripts/manage_execution_state.py create --truth delivery/truth/product-truth.yaml --config delivery/spec.config.yaml --installed-skill C:/path/to/installed/ai-delivery-spec/SKILL.md --execution-id EXEC-PROJECT-001 --project-id PROJECT-001 --output delivery/evidence/execution/state-000.yaml
py -3 scripts/manage_execution_state.py create --discovery-contract discovery.yaml --config delivery/spec.config.yaml --installed-skill C:/path/to/installed/ai-delivery-spec/SKILL.md --execution-id EXEC-PROJECT-001 --output delivery/evidence/execution/state-000.yaml
py -3 scripts/manage_execution_state.py verify --state delivery/evidence/execution/state-000.yaml
```

Run every gate at the current node. A gate result is valid only for the exact
`state_hash` it names.

```powershell
py -3 scripts/manage_execution_state.py gate --state state-000.yaml --gate-id contract_traceability --projection delivery/projections/human-first-prd.md --projection delivery/projections/coding-agent-spec.md --output gate-contract.yaml
```

Advance exactly one node only after all required results pass:

```powershell
py -3 scripts/manage_execution_state.py advance --state state-000.yaml --to specify --gate-result gate-version.yaml --gate-result gate-assurance.yaml --gate-result gate-context.yaml --gate-result gate-contract.yaml --gate-result gate-audit.yaml --gate-result gate-fallback.yaml --output state-001.yaml
```

Record each material agent/human clarification or negotiation turn. Exceeding
`execution.max_turns_per_stage` raises `LifecycleConvergenceError` and keeps the
last stable state unchanged:

```powershell
py -3 scripts/manage_execution_state.py record-turn --state state-000.yaml --output state-turn-001.yaml
```

## 3. Six Active Gates, Seven Gate Types

1. `version_environment`: expected, repository, and installed skill versions;
   repository commit; dependencies; rollback revalidation.
2. `complexity_domain`: structured risk signals, project mode/tier, domain
   evidence and production boundary. Keywords may flag review but never award
   maturity.
3. `context_survival`: state hash, Product Truth/config/domain/evidence anchor
   hashes, checkpoint recovery and current-stage binding.
4. `discovery_readiness`: valid Discovery Contract, accountable sources,
   approved outcome/scope, no open P0 unknowns, and an explicit ready decision.
5. `contract_traceability`: unique `FEAT-*`, source refs, behavior refs,
   acceptance refs, and projection coverage with no invented ID.
6. `audit_access`: access allowlist/denylist, accountable Human Gate where
   required, evidence refs, and hash-chain or external signature mode.
7. `fallback_risk`: fail closed for high risk; low risk may continue only as
   explicit human review with recorded gaps; experimental behavior stays out of
   staging/production.

## 4. Stage Rule

At each `Discover (产品发现与策略) -> Specify (需求澄清、范围与统一规格)
-> Plan (工程方案与交接规划) -> Tasks (任务拆解与 Coding Agent 切片)
-> Build/Verify (构建、验收测试与追溯) -> Launch (上线与交付)
-> Learn/Retire (运营、学习与退役)` transition:

1. reload and verify state;
2. build a scoped Product Truth slice using `--execution-state`;
3. run all required micro-gates;
4. bind human approval evidence when the risk profile requires it;
5. advance one node and retain the previous checkpoint and gate results.
6. stop at the configured turn limit and return unresolved IDs to an accountable human.

`discover` uses `discovery_readiness` instead of `contract_traceability`.
After entering `specify`, bind the first Product Truth with `checkpoint
--truth`; later stages use contract traceability. Any legitimate contract or
config change creates a new revision, previous-state hash, snapshot set, and
fresh gate requirement.

After interruption, resume only from the latest checkpoint whose hash, anchor
files, gate results, access scope, version, and dependencies still verify.

## 5. Failure Policy

- High-risk, staging, or production validation failure: `BLOCKED`.
- A declared validator outage in low-risk development/test may advance only as
  `approved_with_gap` with accountable approval evidence; it is never a pass.
- Other low-risk failures remain `REVIEW_COMPLETE_WITH_GAPS` until corrected.
- Validator outage is a failure, not a pass. Record the outage and chosen
  policy.
- Detect bypass structurally: version/config/hash drift, stale gate results,
  missing Feature links, scope downgrade, or production use of weak assurance.
  Keyword substitution detection is only a heuristic and cannot prove intent.
