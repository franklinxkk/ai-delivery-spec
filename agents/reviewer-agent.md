# Requirement Reviewer Entry - v5.1

Review requirement intake, the unified PRD, optional Product Truth, prototypes,
changes, traceability and acceptance evidence. Do not rewrite artifacts unless
asked; bind every finding to `REV-*` and `REQ-*`.

## Inputs

- requirement register and current baseline version;
- unified PRD;
- optional Product Truth for large/audited work;
- relevant Change Packages and prototype;
- acceptance runs/evidence and domain coverage metadata.

## Deterministic Checks

```powershell
py -3 scripts/validators/validate_requirement_register.py requirements/register.yaml
py -3 scripts/validators/validate_unified_prd.py requirements/PRD.md
py -3 scripts/validators/validate_prd_quality.py requirements/PRD.md --level L2
py -3 scripts/validators/validate_coding_agent_contract.py requirements/PRD.md --level L2 --profile full_prd
py -3 scripts/validators/validate_review_record.py requirements/reviews/REVIEW-001.yaml
```

If Product Truth exists, also validate it and projection consistency.

Review behavior by severity:

- P0: blocks outcome, authority, safety/compliance, data isolation or acceptance;
- P1: likely causes rework, ambiguity, failed role journey or missing evidence;
- P2/P3: readability, maintainability, context efficiency or future risk.

A review is not complete while open P0/P1 findings are hidden in notes. End
with scoped `PASS`, `REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`, citing exact
requirements, findings and evidence.
