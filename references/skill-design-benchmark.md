# Skill Design Benchmark

Use this file only when upgrading or auditing the skill itself. Do not load it for ordinary PRD/prototype work.

## 1. External Benchmarks

| Benchmark | Observed Pattern | What This Skill Absorbs |
|---|---|---|
| `anthropics/skills` | Skill is a self-contained folder with `SKILL.md`, optional `skills/`, `spec/`, `template/`, and clear frontmatter. | Keep `SKILL.md` as the router and move detailed protocols into references. |
| `mattpocock/skills` | Skills are small, composable, practical, and easy to adapt. | Keep delivery gates modular and tier-aware instead of forcing every task through a heavyweight process. |
| Large community skill libraries | Broad category organization, authoring standards, scripts, and validation conventions. | Add structure only when it maps to a real trigger, real artifact, and real validation surface. |

## 2. Design Rules For This Skill

- `SKILL.md` should remain a routing and decision document, not a full methodology book.
- Every reference file must be reachable from `SKILL.md` through Conditional Gates or Module Map.
- Every new gate must declare: trigger, required artifacts, acceptance checklist, and relationship to other gates.
- Prefer one-level references under `references/`; avoid deep reference chains.
- Put deterministic repeatable logic in `scripts/`.
- Keep validation reports outside the installed skill directory unless they are examples intentionally loaded by a trigger.
- Archive old versions outside the active skill path or mark them clearly as backups.

## 3. Anti-Patterns

- A universal full pipeline with no downgrade path.
- A reference file that is not connected to any trigger.
- Domain knowledge mixed into core delivery rules.
- Multiple PRD structures with no layering rule.
- AI terms added as labels without runtime, evaluation, or operations contracts.
- Long examples inside `SKILL.md` that should be test cases or reference files.

## 4. Upgrade Checklist

Before publishing a new version:

| Check | Pass Rule |
|---|---|
| Trigger clarity | Frontmatter and Conditional Gates describe when the skill should load |
| Progressive disclosure | Core file routes; detailed content lives in references |
| Artifact closure | Each gate has concrete artifacts and acceptance checks |
| Cross-reference integrity | Every reference is listed in Module Map or intentionally script-only |
| Domain replaceability | Core files contain no unnecessary industry-specific residue |
| Real-world validation | At least one local project and one external benchmark scenario are tested |
