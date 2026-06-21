# Medical / Hospital IT Example

Use this example when a product team needs to specify hospital information
systems, clinical workflow, medical quality, patient service, research data, or
AI-assisted medical operations.

## Example Prompt

```text
Use AI Delivery Spec.
Write a Standard L2 PRD for a hospital imaging AI-assisted review feature.
The feature integrates PACS/RIS, shows an AI draft to the radiologist, requires
human review before EMR report publishing, tracks critical-value notification,
and prepares developer/QA handoff.
```

## Expected 0D Triage

```text
[TIER: Heavy] | [AI: true] | [WORKFLOW: true]
```

## Expected Routing

| Decision | Value |
|---|---|
| Primary entrypoint | `references/delivery-core.md` |
| Triggered extensions | `references/advanced-extensions.md` |
| Domain module | `references/domain-medical-hospital-it.md` |
| AI class | AI-supporting, not AI-core by default |
| Delivery tier | L2 unless AI writes consequential clinical state |

## Required Output Focus

Sample output: [L1 PRD sample](l1-prd-sample.md).

- Business scenario: radiologist reviews AI draft before final report signing.
- Source evidence: PACS/RIS image/report, EMR encounter, patient identity, AI
  model trace, hospital SOP, and current regulatory/policy references.
- Human gate: AI output cannot publish diagnosis, report, prescription, or
  clinical order without accountable clinician review/signature.
- State machine: imaging requested -> acquired -> ai_analyzed ->
  radiologist_reviewed -> signed -> published.
- Exceptions: AI timeout, low confidence, conflicting prior report, permission
  denial, patient mismatch, signature failure, stale source data.
- Acceptance: prose AC plus optional `ac_structured` YAML for coding-agent
  implementation.

## Review Checks

- Clinical accountability is explicit.
- Privacy, consent, data minimization, and access scope are explicit.
- Test/shadow data cannot create real clinical, billing, patient-message, or
  research-export side effects.
- Regulatory claims are marked as source evidence to verify, not assumed as
  permanent truth.
