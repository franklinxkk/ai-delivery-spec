# System Readiness Checklist Template

Use before staging, pilot, production, or external customer demo with real data.

## 1. Release Record

| Field | Value |
|---|---|
| Feature / Module | |
| Release Type | internal / staging / pilot / production / customer_demo |
| Release Owner | |
| Date | |
| Decision | GO / NO_GO / GO_WITH_RISK |

## 2. Checklist

| # | Domain | Check | Severity | Owner | Result | Evidence / Notes |
|---|---|---|---|---|---|---|
| 1 | Scope | Release scope, out-of-scope, and known risks are frozen | P1 | PM | PASS / FAIL | |
| 2 | Environment | Dev/staging/prod config and keys are ready | P1 | Dev Lead | PASS / FAIL | |
| 3 | Data | Migration has backup, dry-run, and validation query | P0 | Backend | PASS / FAIL / N/A | |
| 4 | Test Data | Automated tests cannot pollute business data or metrics | P0 | QA/Backend | PASS / FAIL | |
| 5 | Permission | RBAC and tenant isolation have positive and negative tests | P0 | QA | PASS / FAIL | |
| 6 | API Contract | API/schema versions and breaking changes are declared | P1 | Backend | PASS / FAIL | |
| 7 | Surface | PC/App/H5/mini-program/native acceptance branch completed | P1 | QA/PM | PASS / FAIL / N/A | |
| 8 | Workflow | Queue/retry/timeout/dead-letter/replay behavior defined | P1 | Backend/Ops | PASS / FAIL / N/A | |
| 9 | AI | Prompt registry, golden case tier, fallback, kill switch ready | P0 | AI Owner | PASS / FAIL / N/A | |
| 10 | Observability | Logs, metrics, traces, alert owner, and SLA are live | P0 | Ops/SRE | PASS / FAIL | |
| 11 | Rollback | Rollback or disable path is tested | P0 | Dev Lead | PASS / FAIL | |
| 12 | Support | Support FAQ/runbook/escalation path is ready | P1 | Ops/CS | PASS / FAIL / N/A | |
| 13 | Compliance | Privacy, desensitization, license, data export controls checked | P0 | Sponsor/Legal | PASS / FAIL / N/A | |
| 14 | Global/Regional | Target-market register and current official compliance evidence reviewed | P0 | Legal/Privacy | PASS / FAIL / N/A | |
| 15 | Global/Regional | Data, model, log, analytics, backup, and support-access regions mapped | P0 | Architect/Privacy | PASS / FAIL / N/A | |
| 16 | Global/Regional | Cross-border basis, subprocessors, and regional failover approved | P0 | Legal/Privacy/Ops | PASS / FAIL / N/A | |
| 17 | Global/Regional | Locale/RTL/formats/platform declarations and support paths tested | P1 | PM/QA/Ops | PASS / FAIL / N/A | |
| 18 | Global/Regional AI | Per-locale golden/eval sets pass, including worst-locale safety result | P0 | AI Owner/QA | PASS / FAIL / N/A | |
| 19 | Retirement/Exit | Dependencies, customers, migration, export/retention/deletion, access, and shutdown sequence reviewed | P0 | PM/Dev/Ops/Legal | PASS / FAIL / N/A | |

### 2.1 Regional Profile

Complete once per launch market or materially different regional configuration.

| Field | Value |
|---|---|
| Market ID / Countries | |
| Locales / RTL | |
| Tenant Home Region | |
| Storage / Processing / Model Regions | |
| Approved Transfer Basis / Subprocessors | |
| Terms / Privacy / AI Disclosure Versions | |
| App/Payment Distribution | |
| Support Timezone / Escalation | |
| Legal/Privacy Review Date and Official Sources | |

### 2.2 Retirement / Exit Profile

Complete for feature/API/model/provider/product/tenant/region deprecation or shutdown.

| Field | Value |
|---|---|
| Object / Owner / Reason | |
| Freeze / End-of-Sale / End-of-Support / Shutdown Dates | |
| Affected Customers and Dependencies | |
| Replacement / Compatibility / Migration Path | |
| Notice Channels and Deadline | |
| Export / Retention / Deletion Plan | |
| Financial / Contract / License Closure | |
| Credential / Job / Traffic / Vendor Shutdown Sequence | |
| Rollback or Reopen Window | |
| Closure Verification Evidence | |

## 3. Failed Checks

| Check ID | Severity | Owner | Mitigation | Expiry | Approval |
|---|---|---|---|---|---|
| | P0 / P1 / P2 | | | | |

## 4. Go / No-Go Decision

Decision:

Reason:

Rollback plan:

Approvals:

| Role | Name | Decision |
|---|---|---|
| PM | | |
| Dev Lead | | |
| QA | | |
| Ops | | |
| Sponsor | | |
