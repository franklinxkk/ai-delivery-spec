# System Readiness Checklist

Use this reference before a feature moves from PRD/prototype/dev handoff into staging, pilot, production, or customer demo with real data.

This gate catches failures that a perfect PRD cannot prevent: environment gaps, missing rollback, data migration risk, observability gaps, permissions, test data pollution, AI fallback gaps, and owner/SLA ambiguity.

## 1. Trigger

Load this file when any of these are true:

- the feature will be released to staging, pilot, production, or an external customer demo;
- backend writes, scheduled jobs, workflow automation, AI agents, reports, or notifications are involved;
- the feature touches permissions, tenant data, finance, compliance, safety, policy, learning result, or customer commitment;
- a release needs migration, rollback, on-call, monitoring, or data cleanup.

## 2. Readiness Domains

| Domain | Required Checks |
|---|---|
| Scope | release scope, out-of-scope, owner, decision log |
| Environment | dev/staging/prod config, env vars, third-party keys, feature flags |
| Data | migration, seed data, test data isolation, retention, backup, cleanup |
| Permission | RBAC, tenant isolation, admin/agent/tool scopes, audit trail |
| API/Contract | API version, schema compatibility, error codes, idempotency |
| Frontend/Surface | PC/mobile/mini-program/native app branch acceptance, offline/weak network |
| Workflow/Job | queue, retry, timeout, dead-letter, replay, compensation |
| AI | prompt registry, golden case tier, eval threshold, fallback, kill switch |
| Observability | logs, metrics, traces, alert owner, dashboard, sampling |
| Release | rollout plan, canary/pilot, rollback, human overrule, approval |
| Operations | on-call, runbook, SLA, escalation, customer support handoff |
| Security/Compliance | privacy, desensitization, license, legal basis, data export control |

## 3. Minimum Checklist

| Check | Pass Rule | Owner |
|---|---|---|
| Release scope frozen | release includes scope, excluded items, and known risks | PM |
| Feature flag exists | risky feature can be disabled without redeploy | Dev Lead |
| Rollback plan exists | rollback path tested or explicitly manual with owner | Dev Lead |
| Data migration reversible | migration has backup, dry-run, and validation query | Backend |
| Test data isolated | automated tests cannot pollute metrics or customer data | QA/Backend |
| Permission matrix verified | role/tenant/org isolation tested on at least one negative case | QA |
| API/schema versions declared | breaking changes have migration or compatibility plan | Backend |
| Observability live | logs, metrics, traces, alerts, executor, owner/SLA defined | Ops/SRE |
| AI fallback ready | AI failure/timeout/low confidence has manual/local fallback | AI Owner |
| Golden cases pass | required golden case tier passes for prompt risk level | QA/Eval |
| Multi-surface acceptance done | PC/App/H5/mini-program/native branch accepted as applicable | QA/PM |
| Support handoff ready | FAQ/runbook/escalation path exists for customer-facing change | Ops/CS |

## 4. Go / No-Go Rules

Default decision:

```text
P0 failed -> NO-GO
P1 failed -> GO only with owner-approved risk acceptance and rollback plan
P2 failed -> GO allowed with backlog item
```

P0 examples:

- no rollback or disable path for business-critical release;
- automated acceptance can write real production/preprod business data without isolation;
- permission or tenant isolation is unverified;
- AI high-risk write path has no human gate, fallback, or kill switch;
- migration can corrupt data and has no backup;
- no owner for critical alerts.

## 5. Readiness Record

```yaml
system_readiness:
  feature_id:
  release_type: internal | staging | pilot | production | customer_demo
  release_owner:
  decision: GO | NO_GO | GO_WITH_RISK
  failed_checks:
    - id:
      severity: P0 | P1 | P2
      owner:
      mitigation:
      expiry:
  approvals:
    pm:
    dev_lead:
    qa:
    ops:
    sponsor:
```

## 6. Relationship To Other Gates

- Use `delivery-acceptance-gates.md` for PRD/prototype acceptance.
- Use this file after acceptance when the question becomes "can this safely run in a real environment?"
- Use `prototype-testability.md` for shadow-data isolation.
- Use `ai-runtime-ops.md` for AI fallback, observability, rollback, and kill switch.
- Use `prompt-registry.yaml` for golden case tier requirements.
