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
