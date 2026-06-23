# L1 PRD Sample: Imaging AI-Assisted Review

## 0. Delivery Metadata

```yaml
artifact: light_prd_sample
domain: Medical / Hospital IT
mode: Lite
tier: L1
ai: true
workflow: true
completion_state: REVIEW_COMPLETE_WITH_GAPS
```

## 1. Problem And Outcome

Radiologists need to review imaging studies efficiently while preserving
clinical accountability. AI may provide a draft finding or risk hint, but the
final imaging report must be reviewed and signed by an accountable radiologist.

Success metric:

```text
Average time from image acquisition to signed report: unknown baseline -> reduce by 20% in pilot department, with no unresolved safety incident.
```

## 2. Users And Core Scenario

| Role | Goal | Pain |
|---|---|---|
| Radiologist | review study and sign final report | repetitive reading and missed-prior comparison risk |
| Technician | ensure study is acquired and available | unclear failed AI state |
| Quality manager | audit AI usage and report quality | AI outputs are not traceable |

Core flow:

```text
Study requested -> image acquired -> AI draft generated -> radiologist reviews/edits/rejects -> report signed -> EMR publishes result.
```

## 3. Function Inventory

| Function ID | Function Name | User Outcome | Release Scope |
|---|---|---|---|
| MED-F01 | Review AI imaging draft | radiologist sees draft and makes accountable decision | in |
| MED-F02 | Sign imaging report | final report is signed and published | in |

## 4. Functional Requirement Record: MED-F01 Review AI Imaging Draft

| Section | Content |
|---|---|
| Identity and value | MED-F01; AI assists review without replacing radiologist judgment |
| Roles and scenario | radiologist opens study after image acquisition and AI draft generation |
| Entry and preconditions | study belongs to authorized department; image is available; AI trace exists or failed state exists |
| Pages and visible states | imaging viewer, AI suggestion panel, low-confidence warning, reviewed badge |
| Fields and dictionaries | study id, patient identity, modality, AI finding, confidence, model version, reviewer decision |
| Numbered interaction flow | 1 open worklist; 2 open study; 3 view AI draft; 4 accept/modify/reject; 5 save review decision |
| Actions and results | review action creates AIRecommendationReviewed audit event |
| Business rules and calibers | low confidence must be marked; AI cannot publish report; reviewer reason required for rejection if configured |
| State-button behavior | ai_analyzed -> radiologist_reviewed; reviewed enables report editing/signing |
| Permission and data scope | radiologist sees authorized department/patient studies only |
| Exceptions and recovery | AI timeout shows manual review path; patient mismatch blocks report publishing |
| Notifications, audit, and dependencies | PACS/RIS provides images; AI trace stores model/prompt/version; EMR publishes only signed report |
| Data / AI / algorithm contract | AI-supporting; write_scope=draft_only; human_gate=required_before_publish; fallback=manual_review |
| Function-Level NFR | viewer load and AI panel must not block manual reporting path |
| Frontend / Backend / QA handoff notes | frontend separates draft from signed report; backend enforces human gate; QA tests timeout, low confidence, permission |
| Acceptance | Given AI draft exists, when radiologist modifies and saves review, then study state becomes radiologist_reviewed and audit contains AI trace plus reviewer decision |

```yaml
ac_structured:
  - id: AC-MED-F01-001
    given: "authorized radiologist opens an acquired study with an AI draft"
    when: "the radiologist modifies the AI draft and saves the review decision"
    then: "the study becomes radiologist_reviewed and the audit record links study id, model version, draft output, reviewer, decision, and time"
    test_type: integration
```

## 5. Gaps Before L2

- Confirm official policy/SOP for AI-assisted imaging in the target hospital.
- Confirm PACS/RIS/EMR integration contract and source-of-truth boundary.
- Confirm whether critical-value notification is in this release.
