# Reviewer Agent Entry

Use this entry when an AI tool is asked to review a generated PRD, prototype,
or delivery package against AI Delivery Spec.

## Inputs

- PRD path, when available.
- Prototype path, when available.
- IA Skeleton path or PRD-embedded `ia_skeleton` YAML, when available.
- Manifest path, when available.

## Review Steps

1. Identify the intended PRD profile: Contract Summary, Human-First Full PRD,
   or AI-Coding Full PRD.
2. Run deterministic validators before subjective comments:

```bash
python scripts/validate_prd_quality.py {prd_path}
python scripts/validate_ia_skeleton.py --ia-skeleton {ia_path} --prototype {prototype_path} --prd {prd_path}
python scripts/validate_ia_skeleton.py --extract-from-prd --prd {prd_path} --prototype {prototype_path}
python scripts/validate_coding_agent_contract.py --prd {prd_path} --prototype {prototype_path}
```

3. Report findings by severity:
   - P0: blocks implementation, acceptance, safety, compliance, or source truth.
   - P1: likely causes rework or QA ambiguity.
   - P2: readability, maintainability, or future-proofing issue.
4. End with `PASS`, `REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`.

Do not rewrite the PRD unless asked. First produce a gate report with evidence.
