# OpenAI Codex Agent Entry - ai-delivery-spec

Use this entry when the session runs inside OpenAI Codex, ChatGPT coding
workflows, GitHub Copilot coding agent-style environments, or any coding agent
that consumes repo-level `AGENTS.md` instructions.

This file complements `agents/openai.yaml`. `openai.yaml` is UI/harness
metadata; this file is the execution guide for coding-agent handoff.

## Activation

Load this entry when any condition applies:

- The user asks to implement from an AI Delivery Spec PRD/prototype.
- The user asks to generate `AGENTS.md`, `.cursor/rules`, `.cursorrules`,
  `CLAUDE.md`, or test stubs.
- The PRD contains `ac_structured`, `ai_contract_lite`, or
  `ai_runtime_contract` blocks.

After activation, load:

1. `SKILL.md` for 0D triage and routing.
2. `references/delivery-core.md` for FRR and acceptance structure.
3. `references/coding-agent-compat.md` for machine-readable AC, AI contract,
   project instruction generation, and data-* mapping verification.

## Source-Of-Truth Order

Before coding, resolve behavior in this order:

```text
1. delivery/manifest.json: artifact paths, versions, hashes, source status.
2. delivery/ia-skeleton.yaml: module/view/region/action structure.
3. PRD FRR in delivery/prd/: business scenario, rules, states, permissions, acceptance.
4. Prototype data-* attributes in delivery/prototype/: UI action and component binding.
5. AC-YAML in delivery/acceptance/ or ac_structured blocks: test expectations.
6. ai_contract_lite / ai_runtime_contract: AI behavior, fallback, eval, flags.
7. Repository conventions: framework, file layout, style, existing tests.
```

If a required behavior is missing, do not invent it. Report:

```text
[GAP] {FunctionID} section {Section}: {missing decision}
```

## Implementation Rules

- Generate or update tests for P0/P1 `ac_structured` cases before or alongside
  implementation.
- Map every generated test to an AC ID; do not create anonymous acceptance
  tests for product behavior.
- Implement only states, role scopes, actions, fields, and API contracts found
  in the PRD/prototype.
- Preserve tenant, org, role, row, and field-level data isolation.
- For AI-supporting L2 features, prefer `ai_contract_lite`; do not implement
  the full runtime harness unless an upgrade trigger is present.
- For AI-core or high-risk features, implement fallback/manual path first and
  gate AI behavior behind the declared feature flag.

## Verification Commands

When artifacts are available, run:

```powershell
python scripts/validate_coding_agent_contract.py --prd delivery/prd/main.md --prototype delivery/prototype/app.html
python scripts/validate_ia_skeleton.py --ia-skeleton delivery/ia-skeleton.yaml --prototype delivery/prototype/app.html --prd delivery/prd/main.md
python scripts/validate_prd_quality.py delivery/prd/main.md --manifest delivery/manifest.json
```

Then run the repository's own tests. Report command, result, and unresolved
gaps in the final answer.

## Generated Repo Instructions

When asked to generate project-local instructions:

- Write `AGENTS.md` for Codex, ChatGPT coding workflows, GitHub coding agents,
  and generic multi-agent coding tools.
- Write `CLAUDE.md` only when Claude Code is used.
- Prefer `.cursor/rules/*.mdc` for modern Cursor; use `.cursorrules` only for
  legacy Cursor projects.
- Include PRD path, prototype path, test commands, gap format, source-of-truth
  order, delivery package layout, and AI contract selection rules.
