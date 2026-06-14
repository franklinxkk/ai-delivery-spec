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
- [ ] Add missing Developer Fast-Lane if project enters development.
- [ ] Add package manifest if delivering externally.
- [ ] Record what remains intentionally below full L3.
