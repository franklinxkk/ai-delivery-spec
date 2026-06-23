# System Readiness Checklist

Use this reference before a feature moves from PRD/prototype/dev handoff into staging, pilot, production, or customer demo with real data.

This gate catches failures that a perfect PRD cannot prevent: environment gaps, missing rollback, data migration risk, observability gaps, permissions, test data pollution, AI fallback gaps, and owner/SLA ambiguity.

## Contents

- 1. Trigger
- 2. Readiness Domains
- 3. Minimum Checklist
- 4. Global / Regional Readiness Profile
- 5. Retirement / Exit Readiness Profile
- 6. Go / No-Go Rules
- 7. Readiness Record
- 8. Relationship To Other Gates

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
| Global/Regional | target market, locale, data/model region, transfer boundary, local support, platform/payment constraints |

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

## 4. Global / Regional Readiness Profile

Apply this profile when launching overseas, serving users in multiple countries/regions/languages, routing data or model calls across regions, or publishing through a regional app/payment platform.

Do not treat “English UI” as global readiness. Each target market needs an approved configuration and current evidence.

```yaml
regional_readiness:
  market_id: eu-en
  countries_or_regions: [string]
  locales: [en-GB, de-DE]
  legal_review:
    owner: legal_or_privacy_owner
    reviewed_at: date
    official_sources: [url]
    applicable_regimes: [string]
  user_contract:
    terms_version: string
    privacy_notice_version: string
    ai_disclosure_required: true
    age_or_minor_policy: string
    complaint_and_appeal_path: string
  data_boundary:
    tenant_home_region: eu
    storage_regions: [eu]
    processing_regions: [eu]
    model_endpoint_regions: [eu]
    subprocessors: [string]
    transfer_mechanism: none | approved_contract | adequacy | other_reviewed_basis
    retention_and_deletion_sla: string
  ai_boundary:
    allowed_models: [provider/model/version]
    disallowed_fallback_regions: [string]
    locale_eval_set: string
    safety_policy_version: string
    human_escalation_locale_coverage: [string]
  product_localization:
    timezone: string
    currency: string
    number_date_address_formats: [string]
    rtl_required: false
    local_content_policy: string
  distribution:
    channels: [web, app_store, google_play, enterprise_distribution]
    privacy_labels_or_data_safety_reviewed: true
    payment_tax_refund_owner: string
  operations:
    support_hours_and_timezone: string
    incident_notification_owner: string
    regional_status_page: string
    exit_or_provider_switch_plan: string
```

Required checks:

| Check | Pass Rule | Default Severity |
|---|---|---|
| Target market register | every market has owner, launch state, locales, legal review date, and official evidence links | P0 |
| Data and model flow map | collection, storage, retrieval, model inference, logs, analytics, support access, and deletion regions are explicit | P0 |
| Cross-border basis | every transfer has an approved basis and subprocessor inventory; “cloud provider supports it” is not evidence | P0 |
| Regional failover | failover cannot silently move customer data or model prompts to an unapproved region/provider | P0 |
| AI transparency and appeal | required AI disclosure, user reporting, human review, complaint, and appeal paths exist for the market | P0/P1 by risk |
| Locale evaluation | task quality, safety, refusal, citation, tool selection, and hallucination are evaluated per supported locale | P0 for AI-core |
| Localization behavior | text expansion, pluralization, timezone, currency, number/date/address, search/tokenization, and RTL are tested | P1 |
| Platform declaration | store privacy/data-safety declarations match actual SDK, model, analytics, ad, payment, and support data flows | P0 |
| Commercial operations | tax, invoicing, refund, payment failure, subscription cancellation, and local customer support owners are defined | P1 |
| Provider exit | model, vector store, messaging, payment, and identity providers have export/switch/rollback paths | P1 |

Compliance evidence rules:

- Store the official source URL, review date, accountable legal/privacy owner, applicability decision, and affected product controls. Do not hard-code a legal conclusion into the product spec without current review.
- Re-review when entering a new market, changing model/provider/subprocessor, changing data purpose, adding minors, adding biometric/health/financial data, or making AI decisions more consequential.
- Examples of official evidence sources include the [European Commission AI regulatory framework](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai), [EU Standard Contractual Clauses](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/standard-contractual-clauses-scc_en), [UK ICO AI guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/), Singapore PDPC AI governance guidance, [Apple App Privacy Details](https://developer.apple.com/app-store/app-privacy-details/), and [Google Play User Data policy](https://support.google.com/googleplay/android-developer/answer/10144311). These are inputs to qualified review, not substitutes for it.

## 5. Retirement / Exit Readiness Profile

Apply when deprecating a feature/API/model/prompt, closing a product, migrating tenants or providers, ending a regional service, or deleting customer data after contract termination.

```yaml
retirement_readiness:
  object: product | feature | api | model | prompt | provider | tenant | region
  owner:
  reason:
  freeze_date:
  end_of_sale_date:
  end_of_support_date:
  shutdown_date:
  affected_customers_or_consumers: []
  dependency_inventory: []
  replacement_or_migration_path:
  compatibility_window:
  customer_notice_channels: []
  export_format_and_deadline:
  retention_and_deletion_plan:
  rollback_or_reopen_window:
  support_and_escalation_end:
  closure_evidence: []
```

Required checks:

| Check | Pass Rule | Severity |
|---|---|---|
| Dependency inventory | UI, API, jobs, reports, prompts, tools, integrations, contracts, customers, and downstream data uses are known | P0 |
| Customer/consumer migration | replacement, compatibility, notice, migration owner, deadline, and failure path exist | P0 |
| Data portability and deletion | export scope/format, retention basis, deletion SLA, backup/log/vector/analytics copies, and evidence are defined | P0 |
| Version deprecation | old API/schema/event/prompt/model versions have consumer tracking and an explicit compatibility window | P0/P1 |
| Financial/legal closure | subscription, invoice/refund, contract, license, regulatory retention, and dispute owner are defined | P0/P1 |
| Operational shutdown | feature flags, traffic drain, queue/job stop, credential/key revocation, monitoring, DNS/store/listing, and vendor termination are sequenced | P0 |
| Rollback/reopen | cutoff and recovery window are explicit; irreversible deletion occurs only after approval and expiry | P0 |
| Closure verification | no active consumer, stranded task, orphaned data, unresolved support case, or unrevoked access remains | P0 |

Retirement is not complete when code is disabled. It is complete only when consumers, data, money/contracts, access, operations, and evidence are closed.

## 6. Go / No-Go Rules

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
- cross-border data/model routing has no approved boundary or transfer basis;
- a supported locale has no AI quality/safety evaluation for an AI-core path;
- regional failover can silently use an unapproved provider or region.
- retirement can strand customers/dependencies or delete data without export, retention, approval, and closure evidence.

## 7. Readiness Record

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
  regional_profiles:
    - market_id:
      decision: GO | NO_GO | GO_WITH_RISK
      legal_privacy_owner:
      evidence_reviewed_at:
  retirement_profile:
    object:
    decision: GO | NO_GO | GO_WITH_RISK
    end_of_support_date:
    shutdown_date:
    closure_owner:
```

## 8. Relationship To Other Gates

- Use `delivery-acceptance-gates.md` for PRD/prototype acceptance.
- Use this file after acceptance when the question becomes "can this safely run in a real environment?"
- Use `prototype-testability.md` for shadow-data isolation.
- Use `ai-runtime-ops.md` for AI fallback, observability, rollback, and kill switch.
- Use `prompt-registry.yaml` for golden case tier requirements.
- Use `saas-multitenancy.md` for tenant home region and cross-region administration.
- Use `mobile-product-delivery.md` for locale/RTL/input/platform behavior.
- Use `ai-effect-evaluation.md` for per-locale quality and effect evidence.
