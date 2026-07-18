# Coding-Agent And Domestic Tool Adapters — v5.3

Load this reference only when a named Coding Agent or domestic model will
consume a baselined requirement. The unified PRD remains the single review
baseline; tool instructions cannot add business behavior.

## Shared Handoff Contract

Source order (tool rules are projections, not a new authority):

```text
root/module AGENTS.md -> handoff manifest/current baseline -> unified PRD
-> optional Product Truth ID slice -> approved CHG-* -> locked prototype
-> acceptance -> engineering baseline/repository constraints
```

- Implement one bounded vertical slice tied to
  `REQ/MOD/FLOW/VIEW/REG/ACT/FLD/STM/STATE/METRIC/REL/API/AC` IDs.
- Report conflicts or missing business decisions as `REV-*`/`CFL-*`; never
  invent roles, fields, states, permissions, formulas, defaults or events.
- Enforce state, tenant, permission and high-risk guards on the backend.
- Treat repository paths, framework choices and technical architecture as
  downstream engineering facts, not additions to product scope.
- Link tests and implementation evidence back to `AC-*` and `REQ-*`.
- For large work, load one PRD/Truth slice and checkpoint it; never ask one
  model or subagent to regenerate a giant Product Truth monolith.

## Tool Routes

| Tool/model | Adapter rule |
|---|---|
| Codex | Read the repository after the approved requirement slice; preserve stable IDs in UI attributes and tests; run applicable repository checks and return evidence. |
| Claude Code / Cursor | Pin source order and forbidden invention in project rules; retrieve optional Product Truth by stable ID rather than loading the graph. |
| Trae | Author or implement one vertical slice per task; save the accepted checkpoint before changing slices. |
| WorkBuddy | Put only `SKILL.md` plus the active PRD/Truth slice in workspace rules; validate one checkpoint per task. |
| Qoder | Keep `.qoder/rules` limited to Qoder file matching/tool permissions; business rules reference root/module `AGENTS.md` and PRD because Qoder may prioritize its own rules on conflict. |
| CodeBuddy | Use the shared handoff contract and return ambiguity before code generation; do not convert UI guesses into requirements. |
| GLM 5.2 | Use concise Chinese instructions and deterministic output schemas; preserve IDs verbatim and prevent context compression from dropping roles, permissions, states, exceptions or P0 AC. |
| DeepSeek | Separate analysis from the final artifact; draft by required contract section and run deterministic gates after each accepted slice. |
| Qwen | Generate a Context Plan for long Chinese ToB/ToG input, then write one unified-PRD module/flow slice per turn. |
| Kimi | Use long context for source inventory, then freeze the ID index and continue with small module checkpoints. |

## Direct Coding Entry

Direct implementation starts only when the handoff contains:

1. approved baseline version and stable-ID slice;
2. open external dependencies and forbidden inventions;
3. applicable API/business semantics, states, errors and recovery;
4. positive and negative acceptance with observable evidence;
5. repository architecture constraints supplied by engineering.

Validate the unified requirement first. Validate Product Truth only when that
optional artifact exists. A validator PASS is readiness evidence, not customer
or domain-owner acceptance.
