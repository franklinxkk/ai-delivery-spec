# Codex Coding-Agent Entry - v5.1

Use only when the user requests implementation from a baselined AI Delivery
Spec package. Read `SKILL.md`, `references/handoff.md`, the unified PRD and the
repository. Load change, prototype, domain or Product Truth slices only when
triggered.

## Source Order

1. manifest and current unified PRD baseline;
2. optional Product Truth structured authority;
3. approved `CHG-*` packages;
4. locked prototype/IA for visible behavior;
5. acceptance requirements and repository constraints.

Repository reality cannot silently change requirement behavior. Report a
`CFL-*` or propose `CHG-*` when authorities disagree.

## Implementation Rules

- Implement downstream slices tied to `REQ/MOD/FLOW/VIEW/ACT/STATE/AC` IDs.
- Do not invent roles, pages, fields, states, permissions, rules or events.
- Enforce state, tenant, permission and high-risk guards on the backend.
- Preserve stable IDs in prototype attributes and tests.
- Run applicable repository tests and return evidence references to AC/REQ.
- Record repository paths and technical decisions as engineering facts, not
  additions to product scope.

Validate the single PRD first:

```powershell
py -3 scripts/validators/validate_unified_prd.py requirements/PRD.md
py -3 scripts/validators/validate_coding_agent_contract.py requirements/PRD.md --level L2 --profile full_prd
```

If Product Truth exists, validate and query it by ID. Report passed, failed,
blocked and not-run evidence separately.
