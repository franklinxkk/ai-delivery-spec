# Domain Assurance

Use this reference when adding, verifying, promoting, or making a public claim
about a domain pack. Do not load it for ordinary project delivery.

## Contents

- Two-axis status
- Evidence classes
- First-principles triangulation
- Promotion gates
- Lightweight release check

## Two-axis status

Keep delivery practice separate from reusable-pack assurance.

Practice status:

- `knowledge_only`: no accountable project-use evidence is registered.
- `project_practiced`: used in a bounded real project, not necessarily live.
- `production_practiced`: used in an owner-attested live delivery.
- `production_observed`: independently observed in production.

Reusable-pack maturity:

| Maturity | What it proves | What it does not prove |
|---|---|---|
| `knowledge_backed` | structured pack has attributable sources and declared gaps | behavior, applicability or project correctness |
| `contract_tested` | deterministic fixtures verify named invariants, boundaries and source linkage | fresh-agent behavior or expert correctness |
| `behavior_validated` | bounded fresh-agent runs pass positive/negative/domain cases with evidence | accountable expert/customer approval |
| `expert_reviewed` | named responsible expert reviewed the declared scope and gaps | independent audit or universal applicability |
| `audited` | independent audit passed for the declared version/scope | future versions or other jurisdictions |

Never use `experimental` as a blanket label for a sourced or practiced pack.
Never promote all domains because the core Skill version changed.

## Evidence classes

| Evidence | Valid use | Claim limit |
|---|---|---|
| law/regulation/standard | binding boundary in its jurisdiction/version/scope | applicability still needs project confirmation |
| official product/API docs | vendor terminology, object, action and integration behavior | does not prove legal correctness or other versions |
| vendor whitepaper | capability map and solution pattern | not precise enough for unqualified business rules |
| official case study | discover scenario, role, exception and outcome hypotheses | vendor testimony is not independent outcome proof |
| official source repository | exact component behavior at a commit/license | SDK/demo/open platform is not core-product open source |
| project material and owner decision | project-specific truth and source precedence | not automatically reusable across customers |
| fresh-agent behavioral run | whether the Skill applies the pack correctly to bounded cases | not expert review or customer acceptance |
| accountable expert review | domain correctness within declared scope | not independent audit |

For a vendor source, record `evidence_role` and `claim_limit`. Verify issuer,
official host/repository owner, version/date, license where applicable, and last
review date. Do not infer a proprietary core-product rule from an SDK or demo.

## First-principles triangulation

For each capability:

1. Define the stable work object, accountable actor, state authority, invariant,
   permission/data boundary, failure/recovery and acceptance evidence.
2. Map binding sources to regulated constraints.
3. Compare at least two vendor/product patterns when claiming a cross-vendor
   convention; mark unique behavior as vendor-specific.
4. Convert cases into scenario seeds, not confirmed project requirements.
5. Convert source code/API into exact integration assertions bounded by version.
6. Record conflicts as `verified`, `inferred`, or `unknown`; project/customer
   authority resolves applicability.

First principles test completeness and consistency. They cannot establish legal
applicability, vendor behavior, customer policy, or production effectiveness by
reasoning alone.

## Promotion gates

### knowledge_backed

- domain file and source register exist;
- key claims have attributable sources and freshness metadata;
- known gaps and prohibited claims are explicit.

### contract_tested

- `knowledge_backed` passes;
- at least two domain fixtures cover lifecycle plus a risk/permission/exception;
- deterministic contract assertions pass;
- a `contract_eval/passed` evidence record is registered.

### behavior_validated

- `contract_tested` passes;
- fresh-agent runs cover happy, negative, permission, lifecycle, no-guess and
  applicable integration/migration/AI paths;
- executor, input, model/tool version, timestamp, result and raw evidence exist;
- no simulated reviewer is called an expert.

### expert_reviewed / audited

- `expert_reviewed` additionally requires named accountable expert review,
  project-sampled scenarios and disposition of P0/P1 findings.
- `audited` additionally requires independent audit evidence for the declared
  pack version and scope.

Legacy project assurance value `validated` is read as `expert_reviewed` only
when it uses the signed accountable-review evidence schema; it is not accepted
as a synonym for deterministic contract PASS.

## Lightweight release check

Run deterministic checks on every domain/source/schema change:

```bash
python scripts/validators/validate_domain_sources.py
python scripts/validators/validate_domain_contracts.py
python scripts/validators/validate_domain_coverage.py
```

These checks use zero LLM/subagent calls. Run fresh-agent behavioral evaluation
only when the domain contract, source mapping, prompt route, or expected behavior
changes; it is release hardening, not a per-project runtime tax.
