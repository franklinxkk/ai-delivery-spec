# Claude Code Agent Entry - ai-delivery-spec

Use this entry when the session runs inside Claude Code, Cursor, or a coding
agent environment that consumes repo-level instructions.

This file is a companion to `agents/openai.yaml`. It adds coding-agent-specific
verification steps while keeping the same product delivery protocol.

## Activation

Load this entry when any condition applies:

- The session is initiated from Claude Code or a similar coding-agent CLI.
- The user asks to generate `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, or
  `.cursorrules`.
- The user asks to convert PRD acceptance criteria into test stubs.
- The user asks to implement a feature from an existing PRD and prototype.

After activation, load:

1. `SKILL.md` for 0D triage and routing.
2. `references/delivery-core.md` for FRR structure and acceptance format.
3. `references/coding-agent-compat.md` for AC-YAML, agent entrypoints, and
   verification rules.

## Default Behavior In Coding Agent Sessions

### Step 1 - Locate Source Of Truth

Before writing code, use this priority:

```text
1. FRR in the PRD: business logic, states, permissions, acceptance.
2. Prototype data-* attributes: UI behavior and component binding.
3. ac_structured blocks in FRR section 16: expected outcomes for tests.
4. Engineering contract in FRR section 13: API/data/AI schemas and constraints.
```

Never invent behavior not present in these sources. If a gap exists, report:

```text
[GAP] {FunctionID} section {Section}: {description}
```

Then stop the affected implementation step.

### Step 2 - Pre-Implementation Checklist

For each function:

- [ ] Locate FRR by Function ID.
- [ ] Read section 8 business rules and section 9 state-button matrix.
- [ ] Read section 10 permission and data scope.
- [ ] Extract all `ac_structured` entries where `frr_ref` matches this function.
- [ ] Map each AC `data_testid` to a prototype element.
- [ ] Confirm `data-api` + `data-method` match the planned endpoint.
- [ ] Confirm `data-field` / `data-bind` match FRR section 5 field names.

### Step 3 - Test Generation Rules

Generate test stubs for all `ac_structured` entries with `priority: P0` or
`priority: P1`.

```python
def test_{ac_id}_{type}():
    # given: {given}
    # when: {when}
    # then.ui: {then.ui}
    # then.domain: {then.domain}
    pass
```

Tag mapping:

- `P0` -> smoke.
- `P1` -> regression.
- `P2` -> long-tail/adversarial; automate only when cost is justified.

### Step 4 - AI Feature Implementation Rules

If the function has `ai_runtime_contract` or `ai_contract_lite` in FRR section 13:

- Load and version-pin `impl.prompt_file`; do not inline prompt text into code.
- Gate AI behavior with `impl.feature_flag` or the declared feature flag.
- Implement fallback/manual path as the default path; AI path is an enhancement.
- Emit observability fields on every AI call.
- Never let AI write `business_state` unless `write_scope: business_state` is
  explicitly present and human-gate/rollback rules are defined.

### Step 5 - Generated Project Instructions

When asked to generate `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, or
`.cursorrules`, use `references/coding-agent-compat.md` and write the generated
file to the target project repo root, not inside `ai-delivery-spec`.

Prefer:

- `CLAUDE.md` for Claude Code.
- `.cursor/rules/*.mdc` for modern Cursor project rules.
- `.cursorrules` only for legacy Cursor projects.
- `AGENTS.md` for Codex, GitHub coding-agent-style repo context, and generic
  multi-agent coding tools.

When PRD and prototype artifacts are available, run:

```powershell
python scripts/validate_coding_agent_contract.py --prd path/to/prd.md --prototype path/to/prototype.html
```

## Compatibility

- Claude Code: use `CLAUDE.md` or project memory plus the PRD/prototype.
- Cursor: prefer `.cursor/rules/*.mdc`; `.cursorrules` is legacy-compatible.
- GitHub Copilot coding agent / Workspace: use repo-level markdown instructions
  plus PRD/prototype artifacts.
- OpenAI Codex: use `AGENTS.md` and this repo's `agents/openai.yaml`.
