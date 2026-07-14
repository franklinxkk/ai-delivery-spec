# Claude Code / Cursor Coding-Agent Entry - v5.1

Use for implementation only after one unified PRD is baselined. Read `SKILL.md`
and `references/handoff.md`; do not load unrelated domains or requirement stages.
When optional Product Truth exists, retrieve stable-ID slices instead of loading
the entire graph.

Treat every stable ID as a permanent requirement/test anchor across the unified
PRD, prototype, implementation and evidence.

## Source Order

```text
manifest/current baseline -> unified PRD -> optional Product Truth
-> approved Change Package -> locked prototype -> acceptance -> repository constraints
```

If governed artifacts conflict or behavior is absent, stop the affected slice
and report `REQ/CFL/CHG` IDs. Do not guess.

## Required Behavior

- Work in vertical user/domain-result slices from the downstream technical plan.
- Preserve `REQ/VIEW/REG/ACT/FLD/STATE/AC` IDs in UI and tests.
- Enforce business invariants and permission on the backend.
- Treat AI behavior as governed only when context, evaluation, write scope,
  human gate and fallback are specified.
- Do not generate or maintain a second PRD.
- Bind implementation tests and evidence back to AC and REQ.

Validate the unified requirement contract before implementation. Product Truth
validation is conditional on that artifact existing. Repository architecture,
files, tasks and deployment remain downstream engineering decisions.
