# AI-Coding Full PRD Template (v4.7.3 Profile)

Use this profile only when the user explicitly wants a coding agent, full AI
implementation, machine-readable contracts, test stubs, or an implementation
handoff package. AI-Coding Full PRD is an extension of Human-First Full PRD,
not a replacement.

## Contents

- Heading Hierarchy Lock / 标题层级锁
- 0D Triage And PRD Profile / 0D 分流与 PRD Profile
- Part 1 Human-First Foundation Layer / 第一部分 人类可读基础层
- Part 2 Machine-Readable Extension Layer / 第二部分 机器可读扩展层
- Part 3 Coding Agent Delivery Package / 第三部分 编程智能体交付包
- Part 4 Validation And Review / 第四部分 验证与评审
- Gate Completion Statement / Gate 完成声明

## Heading Hierarchy Lock / 标题层级锁

- Use exactly one H1 (`#`) for the document title.
- Use H2 (`##`) for global lifecycle stages or top-level modules.
- Use H3 (`###`) for module subsections and function records.
- Use H4 (`####`) for FRR numbered sections inside one function.
- Do not jump from H2 directly to H4.
- Do not use bold text, table rows, or numbered list items as fake headings.
- In Chinese PRDs, translate headings but keep the hierarchy unchanged.

## 0D Triage And PRD Profile / 0D 分流与 PRD Profile

```text
[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false]
Mode: Standard | Full
PRD Profile: AI-Coding Full PRD
```

| Trigger | Result |
|---|---|
| User asks for Cursor / Claude Code / Copilot / Codex / Devin implementation | Use AI-Coding Full PRD |
| User asks for `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, AC-YAML, or test stubs | Use AI-Coding Full PRD |
| User only asks for human review, vendor development, or QA handoff | Use Human-First Full PRD first; list upgrade conditions |

## Part 1 Human-First Foundation Layer / 第一部分 人类可读基础层

Before adding any machine-readable blocks, write the full business-readable
specification using `references/templates/human-first-prd-template.md`.

Required foundation:

- source evidence register;
- roles, scope, user journeys, and business scenarios;
- IA Skeleton, prototype lock, `Layout ID`, page layout, and region behavior;
- one complete FRR per function;
- field validation, dictionaries, interaction/state flow, business rules,
  exceptions, permission, metrics, NFR, and acceptance;
- frontend / backend / QA handoff notes.

Do not compress this layer into schemas. Coding agents need scenario context to
avoid implementing technically valid but business-wrong behavior.

## Part 2 Machine-Readable Extension Layer / 第二部分 机器可读扩展层

### 2.1 Prototype Data-Attribute Contract / 原型数据属性契约

| View ID | Layout ID | data-testid | data-action | data-field | Expected Handler / Result |
|---|---|---|---|---|---|
| M01-V01 | LAY-M01-V01-R01 | page-M01-V01 / region-filter | create-record | customer_id | opens modal / updates list / emits event |

Rules:

- Every `primary_action` in IA Skeleton must map to a prototype `data-action`.
- Every critical page/region/modal/drawer must have stable `data-testid`.
- Every form field needed for implementation or testing must map to
  `data-field`.

### 2.2 Structured Acceptance Criteria (AC-YAML)

When embedded in a PRD, use the `ac_structured` key. When exported as a
standalone file, `ac-structured.yaml` may keep the top-level `acceptance` key.

```yaml
ac_structured:
  source_file: delivery/ac-structured.yaml
acceptance:
  - id: AC-M01-F01-001
    given: "用户具备新增权限且必填字段合法"
    when: "提交新增表单"
    then: "系统创建记录、返回编号、列表展示新记录并写入审计日志"
    test_type: integration
    priority: P0
    source_ids: ["SRC-001"]
    view_ids: ["M01-V01"]
    actions: ["create-record"]
```

AC ID evolution rules:

- Do not renumber existing AC IDs after assignment.
- Split functions by adding suffixes or new function IDs; keep deprecated IDs
  with `status: deprecated`.
- When behavior changes materially, add `version: v2` or a new AC ID and map the
  old one to migration notes.

### 2.3 Machine-Readable Runtime / AI Contract

Use `ai_contract_lite` for AI-supporting features. Use full
`ai_runtime_contract` only for AI-core or production AI actions with tool use,
write scope, human gate, observability, rollback, or prompt/eval lifecycle.

```yaml
ai_contract_lite:
  feature_id: Mxx-Fxx
  ai_role: classify | summarize | recommend | extract | answer | generate
  input_schema_ref: schemas/Mxx-Fxx.input.json
  output_schema_ref: schemas/Mxx-Fxx.output.json
  confidence_threshold: 0.80
  human_gate: before_write | before_send | exception_only | none
  fallback: rule_based | template | manual | disable_ai
```

For full AI runtime, reference `references/coding-agent-compat.md` and include
`write_scope`, `tool_scope`, `human_gate`, `fallback`, `observability`,
`rollback`, `prompt_file`, and `golden_case_file`.

### 2.4 API / Event / Data Contract Stub

```yaml
commands:
  - id: CMD-M01-F01-create
    method: POST
    path: /api/m01/records
    request_schema: schemas/M01-F01.create.request.json
    response_schema: schemas/M01-F01.create.response.json
    permission: M01_RECORD_CREATE
    idempotency: required
events:
  - id: EVT-M01-F01-created
    topic: m01.record.created
    payload_schema: schemas/M01-F01.created.event.json
```

## Part 3 Coding Agent Delivery Package / 第三部分 编程智能体交付包

Use this directory convention when handing work to a coding agent:

```text
delivery/
  manifest.json
  prd.md
  prototype.html
  ia-skeleton.yaml
  ac-structured.yaml
  field-dictionary.md
  api-contract.yaml
  events.yaml
  AGENTS.md
  CLAUDE.md
  .cursor/rules
```

`delivery/manifest.json` must list every authoritative file and its role:

```json
{
  "prd": "delivery/prd.md",
  "prototype": "delivery/prototype.html",
  "ia_skeleton": "delivery/ia-skeleton.yaml",
  "acceptance": "delivery/ac-structured.yaml",
  "agent_rules": ["delivery/AGENTS.md", "delivery/CLAUDE.md", "delivery/.cursor/rules"]
}
```

## Part 4 Validation And Review / 第四部分 验证与评审

Run deterministic checks before declaring PASS:

```bash
python scripts/validate_prd_quality.py delivery/prd.md --target-language zh
python scripts/validate_coding_agent_contract.py delivery
python scripts/validate_ia_skeleton.py delivery/ia-skeleton.yaml --prototype delivery/prototype.html --prd delivery/prd.md
```

Review checklist:

| Reviewer | Check |
|---|---|
| PM | Human-First layer is readable and business-complete |
| Frontend | `Layout ID`, `data-testid`, `data-action`, and component states are implementable |
| Backend | API, state, permission, idempotency, audit, and event contracts are clear |
| QA | AC-YAML can become automated or manual test cases |
| Coding Agent | package paths, schemas, and source-of-truth order are unambiguous |

## Gate Completion Statement / Gate 完成声明

```text
Scope: {artifact scope}
Mode / Tier / Profile: {mode} / {tier} / AI-Coding Full PRD
Triggered gates: {gates}
Artifacts updated: {files}
Verification: {scripts/reviews}
Completion state: PASS | REVIEW_COMPLETE_WITH_GAPS | BLOCKED
```
