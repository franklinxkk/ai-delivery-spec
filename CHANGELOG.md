# Changelog

## 5.1.3 - 2026-07-14

- Rebuilt the README first-use path around pain, outcome, honest public adoption
  signals, two install routes, three copyable task routes, expected deliverables,
  and concise answers to the four questions new users ask before adoption.
- Completed the Windows encoding fix at the real boundary: JavaScript extracted
  from multilingual prototypes is now sent to Node explicitly as UTF-8 instead
  of inheriting a narrow runner locale. The existing `cp1252` regression covers
  both JSON output and the nested Node syntax-check path.

## 5.1.2 - 2026-07-14

- Made machine-readable quality-gate JSON ASCII-safe so Chinese findings cannot
  crash on Windows runners with a narrow default console encoding. The
  lightweight-gate regression now forces `cp1252` output to reproduce this
  cross-platform boundary on every OS.

## 5.1.1 - 2026-07-14

- Reduced the always-loaded Skill from about 3,590 to about 1,870 `o200k`
  tokens and added selective domain lookup so runtime agents do not load the
  full domain catalog or an entire domain pack by default.
- Added a seven-seniority, eight-role, seven-stage playbook that defines
  decision ownership, escalation, engineering/architecture review, no-guess
  handoffs and acceptance accountability without taking over sprint work.
- Replaced the blanket `experimental` label with evidence-bounded reusable-pack
  maturity: `knowledge_backed`, `contract_tested`, `behavior_validated`,
  `expert_reviewed`, and `audited`; delivery practice remains an independent axis.
- Added zero-model contract regression for all seven built-in domains and 14
  lifecycle/risk scenarios. All built-in packs are now `contract_tested`; none
  falsely claims fresh-agent behavior, expert review, customer acceptance, or
  production correctness.
- Added OA source triangulation for law/standards plus Weaver, Seeyon, Landray,
  DingTalk and Feishu official materials, with explicit boundaries separating
  whitepapers, vendor cases, open platforms and public SDK/demo repositories
  from binding rules or core-product open-source claims.

## 5.1.0 - 2026-07-14

- Narrowed the product from a full delivery-lifecycle kernel to a requirement-
  management kernel with six governed concerns: intake, clarification,
  specification, change, traceability and acceptance. Sprint/task management,
  code, CI/CD, deployment execution and operations are explicit downstream
  boundaries.
- Added a requirement register with evidence-backed value, complexity bands,
  priority, intake decision, iteration/dependency metadata, audit history and
  external milestone references. Exact effort/cost remains engineering-owned.
- Replaced separate Human-First and AI Coding PRDs with one unified PRD by
  default: a sequential human reading path plus field/state/API/traceability/
  machine-acceptance annexes in the same baseline.
- Made independent Product Truth conditional on scale, repeated change,
  multiple governed exports or audit. Bounded projects start from a focused
  requirement workspace; large projects retain progressive fragments.
- Added bidirectional traceability, deterministic change-impact traversal,
  structured change diff/approval/synchronization, acceptance-run evidence and
  reverse defect/test trace contracts.
- Added guided ambiguity scanning, requirement-intake recommendations and a
  focused `init-requirements` CLI route.
- Added unified-PRD readability/engineering validators and CSS `!important` /
  `.hidden` pollution scanning for interactive prototypes.
- Migrated the publishing-learning golden example to `REQ-*` governance and one
  unified PRD; added v5.1 regression coverage for the full requirement loop.
- Added a seven-sector, seven-stage, eight-role offline assurance portfolio for
  PRD/prototype/change regression without making multi-agent review a runtime tax.
- Added a zero-LLM, single-read `gate` for requirement registers, unified PRDs
  and static prototypes; it reports bounded findings and never authors fixes.
- Closed three forward-test escapes: keyword-only PRD shells now fail structural
  checks, change impact reads standard trace-ledger edges, and clarification scan
  exposes actor/state/money/quantity/brownfield gaps beyond lexical ambiguity.
- Added reusable quantity-lineage, money-settlement, accountable-decision,
  statutory-service, partial-execution and cross-aggregate fulfillment patterns;
  removed unsafe realtime exactly-once/offline-queue assumptions and turned
  timing/retry values into project-confirmed variables.

## 5.0.2 - 2026-07-12

- Added Progressive Product Truth: checkpointable core/module fragments, index
  schemas, deterministic compilation, CLI defaults, and lossless regression
  coverage for Trae/WorkBuddy and other interruption-prone large-project flows.
- Added a complete AI Coding PRD route based on a verified delivery failure:
  repository baseline, page/field/state/data contracts, concrete API schemas and
  errors, versioned event/integration contracts, metrics caliber, vertical file
  dependencies, structured AC, migration/rollback, and operations are now L2
  contract surfaces.
- Replaced the keyword-only Coding Agent validator with structural L0-L4 checks
  and a regression that rejects the former thin-summary pattern.
- Separated `practice_status` from reusable domain-pack `maturity`; traffic,
  CRM, education IT, data product, and AI Native now record accountable
  production-practice attestation without claiming unearned validation/audit.
- Rebuilt README around pain-first positioning, copyable 60-second routes, four
  capabilities, ecosystem responsibility mapping, and evidence-bounded claims.
- Reduced the root to six files/eight directories and grouped runtime/domain
  references, validators, domestic adapters, community documents, config, and
  requirements by responsibility.

## 5.0.1 - 2026-07-12

- Added Ultra-Light routing, smart recommendations/manual overrides, and smart
  large-project Context Plan + ID Slice guidance.
- Added 60-second onboarding, Mermaid generation, China-model/tool adapters,
  ten-case triage benchmark, and v5-native L0-L4 validators.
- Removed obsolete comparison artifacts and strengthened repository hygiene.

## 5.0.0 - 2026-07-11

### Architecture

- Rebuilt the skill around one schema-governed Product Truth with Human-First,
  prototype, coding-agent, QA, customer, and operations projections.
- Added an honest Discovery Contract so incomplete requirements can enter the
  lifecycle without fabricated Product Truth.
- Added project-scoped Domain Capsules as the generic fallback when no dedicated
  domain pack matches.
- Added adaptive Context Plans, ID-based retrieval, versioned checkpoints,
  stage gates, change impact, rollback, and evidence-bound completion states.
- Removed release-specific legacy conversion and compatibility adapters. The
  package is a pure v5 runtime; brownfield product/data migration remains a core
  lifecycle capability.
- Replaced customer-specific examples with reusable generic fixtures.
- Broadened discovery and PRD triggering to lightweight ToC work while keeping
  ToB/ToG as the deep-governance specialization.

### Validation

- Added schema/reference closure, projection consistency, domain maturity,
  source freshness, GitHub-case, evaluation, public-claim, runtime duplication,
  package cleanliness, and agent-entry checks.
- Added versioned Discovery/Product Truth checkpoint tests and installed-package
  fingerprint verification.
- Added stage-turn convergence limits, 80% context-pressure actions, atomic
  failed-checkpoint tests, Capsule namespace/slot/placeholder isolation, and a
  structured clarification transcript compiler.
- Added domain-to-evaluation cross-checks, an evidence-backed `status` command,
  public-claim scanning, agent-entry alignment, and tracked-package hygiene.
- Moved installation and natural-language first use above role detail, and
  added a source-linked ecosystem-composition comparison without self-scored
  quality or popularity claims.
- Added baseline/candidate evaluation comparison with strict input, model,
  settings, repository, and repetition comparability.
- Added a dated, machine-readable ecosystem comparison across 12 product and
  engineering skill projects, nine delivery dimensions, platform boundaries,
  non-scoring activity signals, and an explicit user-reported model-label
  attestation boundary.
- Added Chinese lifecycle annotations to the public workflow, runtime entry,
  and stage-gate contract; re-audited public paths and text for customer- or
  project-specific naming before release.

### Known Limitations

- All seven built-in domain packs remain `experimental`; none authorizes a
  production claim.
- GitHub evaluations are pinned exploratory evidence. Most cells remain
  `partial` or `not_run`, and no general performance improvement is proven.
- Behavioral release claims require at least three comparable repetitions and
  executed coding/acceptance evidence; current fixtures do not meet that bar.
- Domain expert review, customer acceptance, legal applicability, safety,
  financial correctness, and production behavior require accountable external
  evidence.
- Hash chaining detects local drift but is not an external signature service or
  immutable audit store.
