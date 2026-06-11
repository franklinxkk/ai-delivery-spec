# Skill Version Migration

Use this file when upgrading projects or the skill itself across major versions.

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

- [ ] Select tier.
- [ ] Decide whether Strategic Discovery Handoff is triggered.
- [ ] Map old gates to new gates.
- [ ] Identify conditional plugins.
- [ ] Preserve old interaction ledger or document de-scope.
- [ ] Add missing Developer Fast-Lane if project enters development.
- [ ] Add package manifest if delivering externally.
- [ ] Record what remains intentionally below full L3.
