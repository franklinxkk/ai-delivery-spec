# Skill Design Benchmark

Use this file only when upgrading or auditing the skill itself. Do not load it for ordinary PRD/prototype work.

## 1. External Benchmarks

| Benchmark | Observed Pattern | What This Skill Absorbs |
|---|---|---|
| `anthropics/skills` | Skill is a self-contained folder with `SKILL.md`, optional `skills/`, `spec/`, `template/`, and clear frontmatter. | Keep `SKILL.md` as the router and move detailed protocols into references. |
| `deanpeters/Product-Manager-Skills` | Broad PM lifecycle library: discovery, strategy, validation, PRD, roadmap, prioritization, coaching, and packaging for multiple AI tools. Strength: PM education and coverage. Risk: too broad for one delivery run. | Treat discovery/strategy outputs as upstream evidence. Keep lifecycle naming, but do not import the full PM catalog into runtime. |
| `mattpocock/skills` | Skills are small, composable, practical, and easy to adapt. | Keep delivery gates modular and tier-aware instead of forcing every task through a heavyweight process. |
| `mattpocock/to-prd` and `to-issues` | PRD synthesis favors existing context, domain vocabulary, testing seams, and issue breakdown by independently verifiable vertical slices. Strength: pragmatic execution. Risk: PRD template is intentionally lightweight for complex ToB/ToG. | Add a Spec/Plan/Tasks bridge and vertical slice backlog, while retaining complete FRR product specification for enterprise delivery. |
| `github/spec-kit` | Spec-driven workflow separates constitution, specify, clarify/analyze, plan, tasks, and implement. Strength: strong engineering traceability. Risk: command/tool pipeline can be heavier than PM teams need. | Absorb only the lightweight `Discover -> Specify -> Plan -> Tasks -> Build/Verify -> Launch -> Learn/Retire` mapping and traceability rule. |
| Large community skill libraries | Broad category organization, authoring standards, scripts, and validation conventions. | Add structure only when it maps to a real trigger, real artifact, and real validation surface. |

## 2. Design Rules For This Skill

- `SKILL.md` should remain a routing and decision document, not a full methodology book.
- Every reference file must be reachable from `SKILL.md` through Ordered Routing or an explicit maintenance script.
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

## 4. Evolution Governance

Do not turn every review comment into a new public protocol.

- Add a public Gate only when the same unresolved delivery risk appears in at least three real projects across at least two domains or product types.
- If one existing Gate can absorb the rule without changing its ownership or acceptance meaning, strengthen that Gate instead of adding another.
- Put industry vocabulary, entities, policies, and scenarios in a domain module; do not change the public protocol for one industry.
- Put deterministic regression logic in `scripts/`; every trigger, routing, mode, or tier change must add or update representative routing scenarios.
- Treat a single expert opinion as a hypothesis. Accept it only after checking the current version, real artifacts, overlap with existing rules, execution cost, and regression risk.
- Prefer deleting duplication or narrowing a trigger over adding explanatory prose.
- Freeze the architecture when real scenarios pass. Start a new iteration only for observed false triggers, missed gates, contradictory contracts, or repeated delivery failure.

## 5. Upgrade Checklist

Before publishing a new version:

| Check | Pass Rule |
|---|---|
| Trigger clarity | Frontmatter and Ordered Routing describe when the skill should load |
| Progressive disclosure | Core file routes; detailed content lives in references |
| Artifact closure | Each gate has concrete artifacts and acceptance checks |
| Cross-reference integrity | Every reference is listed in Ordered Routing or intentionally script-only |
| Domain replaceability | Core files contain no unnecessary industry-specific residue |
| Real-world validation | Representative local projects, cross-industry combinations, and non-trigger boundaries are tested |
| Change evidence | New public Gates satisfy the multi-project, multi-domain evidence threshold |
