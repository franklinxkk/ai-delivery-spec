# Skill Version Migration

Use this file when upgrading projects or the skill itself across major versions.

## Contents

- v3.9.x -> v4.0 Changes
- v4.0 -> v4.0.1 Defensive Hardening
- v4.0.1 -> v4.0.2 Practical Adoption
- v4.0.2 -> v4.0.3 Strategy Handoff
- v4.0.3 -> v4.0.4 Trigger and Lite Mode
- v4.0.4 -> v4.0.5 Scope And Consistency Hardening
- v4.0.5 -> v4.0.6 Execution Clarity
- v4.0.6 -> v4.0.7 Intent And Scenario Validation
- v4.0.7 -> v4.0.8 Global AI Readiness
- v4.0.8 -> v4.1.0 Lifecycle Review Baseline
- v4.1.0 -> v4.2.0 Product Specification Completeness
- v4.2.0 -> v4.2.1 Deterministic Functional Specification
- v4.2.1 -> v4.3.0 Reader-First Quality Layer
- v4.3.0 -> v4.4.0 Production Elastic Delivery Standard
- v4.4.0 -> v4.4.1 Human Readability Layer
- v4.4.1 -> v4.5.0 Lifecycle Benchmark Bridge
- v4.5.0 -> v4.5.1 PRD Runtime Consistency
- v4.5.1 -> v4.5.2 Higher-Education Domain Module
- v4.5.2 -> v4.6.0 Coding Agent Compatibility
- v4.6.0 -> v4.6.1 Coding Agent Hardening
- v4.6.1 -> v4.6.2 Medical Hospital IT Domain Module
- Gate Mapping
- Project Upgrade Path
- Migration Checklist

## v3.9.x -> v4.0 Changes

| Change | Impact |
|---|---|
| Tiered Delivery Model added | L0/L1 work can skip heavy gates with explicit tier |
| Gate names simplified | Gate A/B/C/D map to Gate 1/2/3/4 |
| Conditional plugins introduced | AI, mobile, approval, multitenancy, reporting, build governance load only when triggered |
| AI Feature Injection split from AI Native | lightweight AI in normal products no longer needs full harness |
| Multi-Surface Consistency added | PC/mobile/mini-program cross-surface contract is explicit |
| ToB/ToG patterns added | approval, RBAC, multitenancy become reusable public patterns |
| Reporting/Analytics pattern added | metric/report/dashboard products get a fitting DDD model |

## v4.0 -> v4.0.1 Defensive Hardening

| Change | Impact |
|---|---|
| Spec Tiering / Anti-Bloating added | Simple CRUD and deterministic workflows no longer inherit unnecessary prompt/DAG/multi-agent contracts |
| Shadow-Data Isolation added | Automated browser agents cannot pollute production/preprod business data, indicator libraries, or reports |
| Contract Version Semantics added | Prompt tests and baselines declare API/event/domain/schema dependency versions |
| Edge-Fallback Gateway added | Mobile/field/weak-network AI flows have local fallback and offline queue rules |
| Human Overrule contract added | Automated acceptance is a release signal with auditable human override, not an unchallengeable judge |

## v4.0.1 -> v4.0.2 Practical Adoption

| Change | Impact |
|---|---|
| Apache-2.0 license added | The protocol can be reused and adapted as an open-source project |
| Reusable templates added | Junior PMs can start from L1/L2/L3 PRD and readiness templates instead of blank documents |
| Golden case tiering added | Prompt Ops can start with low-cost P0 smoke cases and scale to P1/P2 by risk |
| Gate 2 surface branches added | PC Web, H5, mini-program, Native App, API/admin, and workflow canvas can pass Gate 2 with fitting evidence |
| System Readiness Gate added | PRD/prototype acceptance is separated from launch readiness and operational safety |

## v4.0.2 -> v4.0.3 Strategy Handoff

| Change | Impact |
|---|---|
| Strategic Discovery Handoff Gate added | New product/market, major investment, repositioning, and commercialization decisions carry evidence into delivery |
| TAM/SAM/SOM made conditional | Ordinary feature PRDs do not inherit unnecessary market-sizing work |
| Competitive analysis broadened | Status quo, indirect alternatives, switching barriers, and build/buy/partner options are considered |
| Differentiation evidence contract added | Positioning claims must describe provable outcomes or a validation plan |
| Strategy and delivery boundaries clarified | External discovery toolkits can feed Stage 1 without being copied into the delivery protocol |

## v4.0.3 -> v4.0.4 Trigger and Lite Mode

| Change | Impact |
|---|---|
| Description reduced and narrowed | Improves trigger precision and explicitly excludes pure coding, casual brainstorming, and copy editing |
| Lite/Standard/Full execution modes added | Quick validation stops after the requested artifact and lite evidence instead of expanding into the full pipeline |
| Iteration stop conditions added | Agents have an explicit completion boundary and cannot keep generating optional artifacts |
| AI centrality replaces binary AI detection | Mixed products classify AI per module as AI-core, AI-supporting, or AI-incidental |
| Pipeline clarified as routing, not checklist | Supplied/validated stages are skipped; Stage 0 runs only for existing artifacts |

## v4.0.4 -> v4.0.5 Scope And Consistency Hardening

| Change | Impact |
|---|---|
| Artifact scope separated from mode and tier | A PRD-only or prototype-only request no longer expands into a full package |
| Lite/Standard/Full made tier-independent | Non-AI launch work can be Full L2; narrow L3 reviews can remain Lite scope |
| Completion states added | Gate failures remain failures under REVIEW_COMPLETE_WITH_GAPS instead of becoming implicit passes |
| AI high-impact advice clarified | Human-verified, non-binding advice can remain AI-supporting with stronger evaluation/evidence controls |
| Package requirements made conditional | Prototype, PRD, test handoff, and readiness records are required only when their scope triggers |
| Domain module and consistency validator restored | Traffic/CRM examples follow the 14-section contract and future changes get deterministic regression checks |
| Engineering profile renamed | Deterministic vs AI-core classification no longer overloads the L0-L3 “Tier” term |
| Arbitrary mandatory output removed | Research, ICE, out-of-scope counts, and diagrams are conditional on decision value |

## v4.0.5 -> v4.0.6 Execution Clarity

| Change | Impact |
|---|---|
| Conditional Gates, Module Map, and Decision Tree unified | Select one primary output route, then add input modifiers and all matching product plugins |
| Trigger wording tightened without keyword expansion | Create/review intent is explicit while standalone coding and general PM questions remain excluded |
| AI/business dual state contract added | AI confidence/runtime state no longer gets merged into business lifecycle enums; snapshot revalidation controls writes |
| SIM Review converted to persona walkthrough | Reviewers execute one visible step at a time and report evidence-shaped blockers instead of generic opinions |
| Complexity budget boundaries added | UI state, business state, cross-surface action, API, and agent counts have deterministic examples |

## v4.0.6 -> v4.0.7 Intent And Scenario Validation

| Change | Impact |
|---|---|
| Ambiguous HTML exclusion removed | Handoff-ready HTML prototypes trigger the skill; code-only syntax/debugging remains excluded |
| Mode intent signals added | Lite/Standard/Full selection uses current delivery destination evidence instead of predicted future use |
| Mode conflict precedence added | Full > Standard > Lite, while artifact scope remains independent |
| AI-core removed from primary output routes | AI centrality is consistently treated as a product plugin over PRD/prototype/acceptance outputs |
| Prompt Ops loading narrowed | Lightweight AI concepts do not load managed prompt lifecycle rules until L2+/production or explicit registry scope |
| Routing scenario regression added | Real workspace, cross-industry, and non-trigger cases are executable in CI/local validation |
| Evolution governance threshold added | A new public Gate now needs evidence from three real projects across two domains; isolated needs stay in domain modules |

## v4.0.7 -> v4.0.8 Global AI Readiness

| Change | Impact |
|---|---|
| Global/Regional Readiness Profile added | Overseas/multi-country work composes existing readiness, runtime, SaaS, mobile, and evaluation contracts instead of adding an isolated Gate |
| Regional model routing added | AI failover cannot silently move prompts/data to an unapproved provider or region |
| Tenant home-region contract added | Storage, search/vector, logs, backup, support access, analytics, and exit are region-aware |
| Mobile localization/distribution contract added | RTL, input methods, formats, subscriptions, privacy labels, and AI-content reporting become testable |
| Per-locale AI evaluation added | Global averages cannot hide a failing locale, dialect, provider route, or safety-critical translation |
| Global scenario regression added | EU, Middle East, Southeast Asia, US, Japan, cross-border commerce, global consumer AI, and multi-country BI are covered |

## v4.0.8 -> v4.1.0 Lifecycle Review Baseline

| Change | Impact |
|---|---|
| Lifecycle stage made explicit | Discovery, definition, design, engineering, verification, release, operation/learning, and retirement use stage-specific review criteria |
| Primary routes changed to artifact types | Strategy, PRD, design/prototype, engineering contract, test/UAT, readiness, post-launch evidence, and retirement no longer compete with Tier selection |
| Single-artifact lifecycle review added | A test plan, UAT report, incident review, or retirement plan can pass/fail independently without requiring the whole product package |
| Lifecycle tier inheritance added | Strategy, post-launch, incident, and retirement artifacts inherit the product tier; unknown tier is recorded as `N/A (lifecycle governance)` |
| Post-launch evidence review added | Metrics, baselines, comparison, guardrails, qualitative evidence, incident learning, and next action become reviewable contracts |
| Retirement/exit readiness added | Dependency shutdown, customer migration, data portability/deletion, deprecation, notice, support end, and closure evidence are explicit |
| Routing regression expanded | 45 scenarios now include 12 lifecycle-stage artifact cases in addition to real, cross-industry, global, and non-trigger coverage |

## v4.1.0 -> v4.2.0 Product Specification Completeness

| Change | Migration Action |
|---|---|
| Gate 3 split into Product Specification Completeness and Engineering Traceability Contract | Re-review L2/L3 PRDs used for development; an engineering summary or DDD/Fast-Lane table alone no longer passes |
| Source Evidence Register added | Inventory supplied Excel/PDF/SQL/prototypes/screenshots/rule catalogs and disposition every atomic source item |
| Standard PRD template changed from a flat feature table to full module specifications | Convert in-scope build modules to `FULL_SPEC`; keep overview only for deferred/external scope |
| Reporting/Analytics contract expanded | Re-map dashboard metrics, indicator definitions, Excel report tasks/fill, and AI report generation into detailed page/field/rule/state contracts |
| Complexity budget clarified | Keep the master narrative concise, but split module specs/authoritative annexes instead of deleting detail |

Compatibility:

- Existing v4.1.0 artifacts remain valid lifecycle records, but do not claim v4.2.0 Gate 3 PASS until source coverage and complete module specifications are checked.
- No new public reference file is required; v4.2.0 strengthens existing core/template/reporting/gate contracts to limit context growth.
- Prototype, runtime, prompt, mobile, SaaS, approval, global, and AI gates keep their existing behavior.

## v4.2.0 -> v4.2.1 Deterministic Functional Specification

v4.2.1 corrects a critical ambiguity found while dogfooding v4.2.0 on the 运智管家 reconstruction PRD: a module-level purpose/input/output/state table could still be mislabeled `FULL_SPEC` even when individual functions had no detailed behavior.

| Change | Migration Action |
|---|---|
| Traditional PRD explicitly restored as the primary product truth | Keep background, scope, users, IA, flows, detailed functions, rules/data, NFR, acceptance, planning, and risks in the main product specification |
| Function inventory becomes the completeness denominator | List all in-scope functions per module before claiming completeness |
| Functional Requirement Record (FRR) added | Write one 15-part deterministic record for every release function, including conditional data/AI/algorithm contract |
| `FULL_SPEC` becomes calculated | Require `release functions = complete FRRs`; module summaries and DDD rows no longer count |
| Attachment shortcut constrained | Annexes may hold atomic fields/rules/metrics, but cannot replace flows, permissions, exceptions, or acceptance |
| Gate 3A fail conditions hardened | “supports add/edit/delete”, “see prototype”, “existing logic”, blank sections, and summary-only modules fail |

Compatibility:

- v4.2.0 PRDs remain historical records, but any development handoff must be rechecked using the function inventory and FRR denominator.
- Engineering contracts, DDD, API mappings, and Fast-Lane remain valid only after their referenced FRRs pass.
- No new public Gate is introduced; this is a correctness fix to Gate 3A.

## v4.2.1 -> v4.3.0 Reader-First Quality Layer

v4.3.0 is a targeted quality layer added after validating the Skill against a data-intelligent report module and a CRM operating-response prototype. It does not replace the v4.2.1 deterministic PRD template.

| Change | Migration Action |
|---|---|
| Reader navigation added | Add one in-document route table for Product, Frontend, Backend, Algorithm/AI, QA, and Architect/Ops readers; do not create separate role PRDs |
| Source assertion status added | Keep existing source disposition values, and add `VERIFIED / INFERRED / PROPOSED / UNKNOWN / CONFLICT` to describe whether each business statement is proven |
| Prototype evidence status added | Mark prototype/demo behavior as `VERIFIED / SPEC_ONLY / GAP / CONFLICT / UNKNOWN`; Stage 0 extraction can pass while Gate 2/3 remains blocked |
| Semantic function split hardened | Split functions when role, permission, trigger, aggregate/data owner, state transition, business result, audit/NFR, or acceptance path differs |
| Reader-first de-duplication bounded | Shared contracts can remove repeated prose, but cannot reduce the release-function denominator or skip FRR sections |
| Backend closure checklist added | State-changing commands must define owner, schema, concurrency, idempotency, transaction/Saga boundary, persisted result, event, audit, retry, and reconciliation |
| AI report contract hardened | AI-core/report generation requires versioned schemas, claim-level evidence, prompt/model/retrieval/runtime versions, evaluation dataset, fallback states, and prohibited writes |
| PRD quality validator added | When a machine-readable manifest exists, validate wildcard IDs, broken references, duplicate boilerplate, source assertion gaps, and action-mapping gaps |

Compatibility:

- Existing v4.2.1 PRDs remain valid historical records. Re-run v4.3.0 only when using them for development, QA, customer acceptance, release readiness, or major refactor.
- Do not replace existing `EMBEDDED / AUTHORITATIVE_ANNEX / DEFERRED / CONFLICT / NOT_APPLICABLE` disposition values.
- `PROPOSED` numeric thresholds, model parameters, eval sizes, and AI runtime settings are not accepted release facts until calibrated and approved.
- A prototype can be valid Stage 0 evidence while still failing Gate 2 or Gate 3.

## v4.3.0 -> v4.4.0 Production Elastic Delivery Standard

v4.4.0 restructures runtime loading after dogfooding v4.3.0 on CRM, data
reporting, 运智管家, and knowledge-base style systems. The goal is to reduce
model overload without weakening FRR completeness, evidence traceability, or
engineering handoff.

| Change | Migration Action |
|---|---|
| Four runtime entrypoints | Start from `SKILL.md`, then load only `delivery-core.md`, `prototype-testability.md`, or `advanced-extensions.md` as triggered. Legacy references remain source assets, not default route files. |
| 0D triage | Every run declares `[TIER: Heavy/Light] | [AI: true/false] | [WORKFLOW: true/false]` before reference loading. Non-AI and non-workflow gates are pruned early. |
| Requirement Diagnosis Anchors | Development-facing requirements add accountability/compliance, adversarial semantics, and offline/concurrency anchor records. L0 exploration may mark non-critical anchors `N/A`. |
| State-driven prototype law | Workflow prototypes use `GlobalState` and `transition(currentState, action) -> nextState`; DOM can route events and support tests, but cannot be business state source. |
| Presentation Mode | Customer/sponsor demos should include a mode that hides technical noise, guides the storyline, and safely simulates invalid input, weak network, permission, or dependency-failure flows. |
| E2E Cross-Module Canvas | Workflow-heavy PRDs include upstream state, domain event, downstream state, transaction/failure owner, and `AC-E2E-LONG-RUNNING` style acceptance rows. |

Compatibility:

- v4.3.0 PRDs remain valid if they already contain full FRR coverage,
  engineering traceability, and source evidence mapping.
- Upgrade to v4.4.0 when a team complains about skill loading overhead,
  prototypes relying on DOM-derived business state, customer-demo friction, or
  cross-module integration gaps.
- Do not delete domain modules, templates, or prompt registry assets. They are
  load-on-demand assets behind `advanced-extensions.md`.

## v4.4.0 -> v4.4.1 Human Readability Layer

v4.4.1 addresses a practical gap found when comparing SDD-style artifacts with
human RD/QA collaboration needs: machine-readable contracts alone are not
enough. PRDs also need business scenarios, readable intent, boundary cases,
metrics, and role-specific handoff notes.

| Change | Migration Action |
|---|---|
| Readability layer added | Load `readability-layer.md` for L1+ PRD, product specification, or development handoff documents. Keep four-entry runtime architecture; this layer is reached through `delivery-core.md`. |
| Executive Summary required | Add one-screen summary after version table: problem, roles, release scope, out of scope, constraints, acceptance signal. |
| Scenario-first module writing | Add module business scenario canvas before function inventory and engineering tables. |
| Boundary and exception hardening | Ensure validation, empty/loading/error, permission, state conflict, network/offline, and fallback cases are visible to RD/QA. |
| Metrics and event tracking strengthened | Add metric ID, event ID, trigger moment, parameters, purpose, privacy/masking, and AI runtime fields when applicable. |
| Frontend/backend/QA handoff notes | Add compact reader notes inside FRR to clarify component behavior, service/state responsibilities, and test focus. |

Compatibility:

- v4.4.0 PRDs remain valid if they are already readable and complete.
- Upgrade to v4.4.1 when a PRD feels machine-oriented, hard for RD/QA to
  review, or starts with APIs/DDD before business scenarios.
- Do not remove FRR, DDD, evidence, or acceptance sections to make documents
  shorter. Improve readability through scenario/context and navigation, not by
  reducing requirement coverage.

## v4.4.1 -> v4.5.0 Lifecycle Benchmark Bridge

v4.5.0 benchmarks public PM and spec-driven engineering projects, then absorbs
only the transferable lifecycle discipline. It does not import external command
systems or full PM-methodology catalogs into the runtime path.

| Change | Migration Action |
|---|---|
| Lifecycle stage made explicit | Record discovery, specification, planning, task breakdown, build/verification, launch, operation/learning, or retirement in final delivery metadata. |
| Spec/Plan/Tasks bridge added | Keep product specification as the source of truth; add implementation plan assumptions and vertical slice tasks only when the artifact enters build planning. |
| Vertical Slice Task Backlog added | For implementation handoff, tasks must trace to Function IDs and Acceptance IDs and produce independently verifiable user/domain results. |
| External framework boundary clarified | Product-Manager-Skills, engineering skills, and Spec Kit style workflows may be upstream evidence or naming references; do not load or copy their whole process. |
| README made AI-tool-agnostic | Public explanation now describes the standard as usable with any AI tool that can read Markdown, not as one platform's private skill. |

Compatibility:

- Existing v4.4.1 PRDs remain valid when they already contain complete FRRs,
  readability layer, DDD/API/data traceability, and acceptance evidence.
- Upgrade to v4.5.0 when the team needs implementation task breakdown, issue
  slicing, AI coding handoff, or clearer public onboarding.
- Do not create task backlogs from incomplete requirements. A task without FRR
  and Acceptance IDs is either a named prefactoring/migration task or `BLOCKED`.

## v4.5.0 -> v4.5.1 PRD Runtime Consistency

v4.5.1 fixes a runtime/template split found during PRD quality review. The
standard template already required 16 FRR sections, but the `delivery-core.md`
runtime summary still described only 15 sections. Since most PRD generation
loads the core file before the template, the core summary is now authoritative
and aligned with the template.

| Change | Migration Action |
|---|---|
| FRR summary aligned to 16 sections | Recheck development-facing PRDs generated from v4.5.0 if they lack `Frontend / Backend / QA Handoff Notes`. |
| §14 renamed to `Function-Level NFR` | Keep performance/security/privacy/accessibility/compatibility/operations here with measurable acceptance. |
| Dependencies moved out of §14 | Put upstream/downstream timing, interfaces, failure behavior, and owners in §12 `Notifications, Audit, And Dependencies`. |
| Role-oriented completeness strengthened | A PRD must answer Sponsor/PM, UX/UI, Frontend, Backend, Algorithm/AI, and QA questions from one source of truth. |

Compatibility:

- v4.5.0 documents remain usable if they already contain complete 16-section
  FRRs or equivalent handoff notes.
- For active development, upgrade the FRR denominator before sprint kickoff:
  missing §15 is a Gate 3 readiness gap, not a stylistic issue.
- Do not split role-specific PRDs. Add reader navigation and handoff notes inside
  the same product specification.

## v4.5.1 -> v4.5.2 Higher-Education Domain Module

v4.5.2 adds a replaceable higher-education informationization domain module
based on reusable patterns from multi-year digital campus, academic affairs,
student affairs, teaching quality, data governance, one-stop service, and AI
assistant materials. It does not change the public runtime protocol.

| Change | Migration Action |
|---|---|
| `domain-education-it.md` added | Load only when the scenario is higher-education informationization, digital campus, academic affairs, student affairs, teaching quality, smart classroom, one-stop service, education data governance, or campus AI assistant. |
| Domain index updated | `advanced-extensions.md` now lists traffic, CRM, and higher-education as load-on-demand domain examples. |
| README bilingual wording refreshed | Public README remains AI-tool-agnostic and now names the supported replaceable domain modules. |

Compatibility:

- Existing traffic-safety and CRM projects are unaffected.
- Higher-education scenarios must still use the same 14-section domain module
  contract and the same Gate 1-4 rules.
- Do not copy school-specific customer data, quotations, or project names into
  public PRDs unless the user explicitly provides them as source evidence for
  that project.

## v4.5.2 -> v4.6.0 Coding Agent Compatibility

v4.6.0 adds first-class support for coding-agent handoff. It keeps the
human-readable PRD and FRR as the source of truth, then adds optional
machine-readable blocks that Cursor, Claude Code, GitHub Copilot Workspace,
Codex, and similar implementation agents can parse.

| Change | Migration Action |
|---|---|
| `coding-agent-compat.md` added | Load only when the PRD/prototype will be consumed by a coding agent, or when the user asks for `AGENTS.md`, `CLAUDE.md`, Cursor rules, test stubs, or machine-readable acceptance. |
| FRR section 16 extended | Keep prose acceptance required. Add an optional `ac_structured` YAML block immediately after the prose table for L2/L3 coding-agent handoff. |
| FRR section 13 extended | Add optional `ai_contract_lite` or full machine-readable `ai_runtime_contract` when AI behavior must be implemented, tested, or monitored. |
| Agent entrypoints added | Use `agents/claude-code.md` as a starter for `CLAUDE.md`, repo-level `AGENTS.md`, `.cursor/rules/*.mdc`, or legacy `.cursorrules`. |

Compatibility:

- L0/L1 human-only PRDs are unchanged unless the user explicitly asks for a
  coding-agent handoff.
- Natural-language acceptance remains mandatory. `ac_structured` is additive,
  not a replacement.
- Existing prototype `data-testid` and `data-action` conventions remain valid;
  v4.6.0 formalizes how they connect to tests and implementation tasks.
- If an old PRD has prose ACs only, migrate P0/P1 cases first and mark any
  intentionally manual case with `skip_reason`.

## v4.6.0 -> v4.6.1 Coding Agent Hardening

v4.6.1 tightens the first coding-agent layer without changing the default
four-entry runtime. It addresses adoption friction found in L2 AI-supporting
features and implementation handoff.

| Change | Migration Action |
|---|---|
| AI contract selection ladder added | Use `ai_contract_lite` by default for L2 AI-supporting features. Upgrade to full `ai_runtime_contract` only for consequential writes, side-effect tools, runtime eval/rollback/on-call, or compliance/safety/money/legal/customer-acceptance risk. |
| AC ID evolution rules added | Do not version AC IDs with suffixes. Use `revision`, `status`, `supersedes`, and `replaced_by` metadata when functions split, merge, or change expected behavior. |
| `agents/openai-codex.md` added | Keep `agents/openai.yaml` as UI/harness metadata; use `openai-codex.md` for OpenAI Codex / ChatGPT / GitHub coding-agent execution rules. |
| `validate_coding_agent_contract.py` added | Run it when both PRD and prototype are available to verify `data-*`, `ac_structured`, role, state, and API mappings before coding-agent implementation. |

Compatibility:

- Existing v4.6.0 PRDs remain valid.
- Full `ai_runtime_contract` remains valid for AI-core/high-risk modules.
- L2 AI-supporting modules may be simplified to `ai_contract_lite` unless an
  upgrade trigger is present.
- Existing AC IDs must not be renumbered during migration.

## v4.6.1 -> v4.6.2 Medical Hospital IT Domain Module

v4.6.2 adds a replaceable medical / hospital informationization domain module
without changing the default four-entry runtime. It is intended for hospital
HIS/EMR/LIS/PACS/RIS integration, clinical workflow, medical quality, infection
control, internet hospital, research data governance, and AI-assisted medical
operations.

| Change | Migration Action |
|---|---|
| `domain-medical-hospital-it.md` added | Load only when the scenario is medical, hospital IT, clinical workflow, EMR/HIS/LIS/PACS/RIS, internet hospital, medical quality, infection control, research data, or medical AI. |
| Domain index updated | `advanced-extensions.md` and README now list traffic, CRM, higher-education, and medical/hospital IT as load-on-demand domain modules. |
| Routing scenario added | The routing harness includes an AI-assisted hospital imaging PRD to verify L2 AI-supporting classification with medical-domain loading. |

Compatibility:

- Existing traffic-safety, CRM, and higher-education projects are unaffected.
- Medical/hospital projects must still use the same 14-section domain module
  contract and the same Gate 1-4 rules.
- Regulatory statements in this module are domain constraints to verify, not
  substitute medical/legal advice. PRDs must cite the latest official policy,
  hospital SOP, data standard, and accountable owner before formal handoff.
- AI-assisted medical outputs remain non-binding drafts unless an accountable
  clinician or approved governance role completes the required human gate.

## Gate Mapping

| v3.9 Gate | v4.0 Equivalent |
|---|---|
| Gate A Story-Path | Gate 1 Story-Path |
| Gate B Demo-Closed | Gate 2 Demo-Closed Prototype |
| Gate C DDD Handoff | Gate 3 Development Contract |
| Gate D Acceptance | Gate 4 Acceptance Package |
| Gate A2 AI Native Harness | Conditional AI Native Harness Gate |
| Mobile Product Delivery Gate | Conditional Mobile + Multi-Surface Gates |
| AI Effect Evaluation Gate | Conditional Effect Evaluation Gate |

## Project Upgrade Path

| Old Project Type | Recommended v4.0 Treatment |
|---|---|
| quick HTML prototype | classify L0, add demo path and known gaps only |
| prototype + light PRD | classify L1, add story/path lite and state notes |
| standard dev PRD/prototype | classify L2, add Developer Fast-Lane and acceptance report |
| AI agent / AI-native workflow | classify L3, add runtime/harness/effect/ops |
| data dashboard/report builder | add Reporting/Analytics Gate |
| ToB/ToG SaaS | add Approval + SaaS Multitenancy |
| PC + mobile/mini-program | add Multi-Surface Consistency |
| new product/market, major investment, repositioning, commercialization | add Strategic Discovery Handoff before Stage 1 |

## Migration Checklist

- [ ] Select Lite, Standard, or Full execution mode.
- [ ] Identify lifecycle stage and requested artifact type.
- [ ] Select artifact scope: single artifact, module package, or full package.
- [ ] Select, inherit, or mark the tier as `N/A (lifecycle governance)`.
- [ ] Classify AI per module as core, supporting, or incidental.
- [ ] Decide whether Strategic Discovery Handoff is triggered.
- [ ] Map old gates to new gates.
- [ ] Identify conditional plugins.
- [ ] Preserve old interaction ledger or document de-scope.
- [ ] Inventory every in-scope module function and calculate `release functions = complete FRRs`.
- [ ] Reject module summaries, screenshots, or engineering rows being counted as complete product specifications.
- [ ] Add missing Developer Fast-Lane if project enters development.
- [ ] Add package manifest if delivering externally.
- [ ] Record what remains intentionally below full L3.
