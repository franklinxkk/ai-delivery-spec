# AI-Coding Full PRD Template (v4.9.14 Profile)

Use this profile only when the user explicitly wants a coding agent, full AI
implementation, machine-readable contracts, test stubs, or an implementation
handoff package. AI-Coding Full PRD is an extension of Human-First Full PRD,
not a replacement.

## Contents

- Heading Hierarchy Lock
- 0D 分流与 PRD 类型 / 0D Triage And PRD Profile
- 原型交互清单提取 / Prototype Interaction Ledger Extraction
- 第一部分 人类可读基础层 / Part 1 Human-First Foundation Layer
- 第二部分 机器可读扩展层 / Part 2 Machine-Readable Extension Layer
- 第三部分 Coding Agent 交付包 / Part 3 Coding Agent Delivery Package
- 第四部分 验证与评审 / Part 4 Validation And Review
- 完成门禁声明 / Gate Completion Statement

## Heading Hierarchy Lock

- Use exactly one H1 (`#`) for the document title.
- Use H2 (`##`) for global lifecycle stages or top-level parts.
- Use H3 (`###`) for module subsections, machine-readable blocks, and package sections.
- Use H4 (`####`) for FRR numbered sections inside one function.
- Do not jump from H2 directly to H4.
- Do not use bold text, table rows, or numbered list items as fake headings.
- Final output language follows the user's spoken language. For Chinese PRDs,
  use Chinese headings only unless the user explicitly asks for bilingual
  headings. Do not copy English template headings into Chinese deliverables.
- If generated `AGENTS.md`, `CLAUDE.md`, or Cursor rules are included inline in
  the same Markdown file, put them under H2/H3 annex headings or fenced code
  blocks. Do not start them with a second H1 such as `# AGENTS.md`.

## 0D 分流与 PRD 类型 / 0D Triage And PRD Profile

```text
[TIER: Heavy|Light] | [AI: true|false] | [WORKFLOW: true|false] | [INFO: complete|partial|missing]
Mode: Standard | Full
PRD Profile: AI-Coding Full PRD
```

| Trigger | Result |
|---|---|
| User asks for Cursor / Claude Code / Copilot / Codex / Devin implementation | Use AI-Coding Full PRD |
| User asks for `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, AC-YAML, or test stubs | Use AI-Coding Full PRD |
| User only asks for human review, vendor development, or QA handoff | Use Human-First Full PRD first; list upgrade conditions |

## 原型交互清单提取 / Prototype Interaction Ledger Extraction

If the source prototype HTML is larger than 100KB, first run:

```bash
python scripts/extract_interaction_ledger.py --input {prototype.html} --output prototype-interaction-ledger.json
```

Use the lightweight ledger as the primary context for pages, actions, modals,
states, roles, fields, and workflows. Do not load a very large prototype into
the main context when the ledger can provide the required implementation
evidence. The full prototype remains an authoritative source file and should be
referenced through path, `view_id`, `data-testid`, and `data-action`.

## 第一部分 人类可读基础层 / Part 1 Human-First Foundation Layer

Before adding any machine-readable blocks, inline the full Human-First Full PRD
in this document. Do not write "see human-first-prd-template.md" as a substitute
for content. Part 1 must include all modules and every complete FRR.

Forbidden substitutes:

- FRR Index Map without the full FRR body;
- "see / refer to / 详见 / 参见" another file or appendix instead of writing the
  FRR content inline;
- placeholder sections that only contain `TBD`, `same as above`, `见原型`,
  `按现有逻辑`, or an external source link;
- AC-YAML, API stubs, or task lists that reference FRRs not already present in
  Part 1.

Required foundation, all inline:

- source evidence register;
- Release Function Inventory and PRD Completion Ledger;
- Stage 1: background, roles, user journeys, competitor/alternative learning,
  EARS statements, scope, priority, and out-of-scope;
- Stage 2: IA Skeleton, prototype lock, `Layout ID`, page layout, and region
  behavior;
- Stage 3: one complete 16-section FRR per in-scope function;
- Stage 4-6: review plan, WBS, risk, dependency, QA acceptance, launch, and
  post-launch review when the requested scope includes lifecycle delivery.

FRR Completion Gate before Part 2:

| Check | Pass Standard |
|---|---|
| FRR count | every `Mxx-Fxx` in the release function inventory has one FRR |
| FRR completeness | every FRR contains sections 1-16 |
| FRR inline body | every FRR section 1-16 is written directly in Part 1, not replaced by an index, appendix link, or external reference |
| Module coverage | every in-scope module has at least one FRR or a clear deferred reason |
| Key information | every FRR section 1 states who/when/why/what/result and contains no unresolved P0 `TBD` |
| State machine | every FRR section 9 has state/button/lifecycle behavior or `N/A + reason` |
| Permission | every FRR section 10 has role/data/action permission or `N/A + reason` |
| Acceptance | every FRR section 16 has prose acceptance before AC-YAML |

If any check fails, return to Part 1 and complete the missing FRR before writing
Part 2. Coding agents need scenario context to avoid implementing technically
valid but business-wrong behavior.

Self-driven repair rule:

- Do not emit Part 2/Part 3 as a workaround for incomplete Part 1.
- If `validate_prd_quality.py` or the FRR Completion Gate finds gaps, revise
  Part 1 first, then regenerate affected AC-YAML/API/event/task references.
- If the context window is near exhaustion, output only the Completion Ledger,
  next-batch function list, and `CONTINUATION_REQUIRED` continuation
  instruction. Do not summarize the remaining modules as "same as previous" or
  "see appendix".
- If the output token budget is insufficient for all remaining FRRs, stop at
  the last fully completed FRR. Emit `CONTINUATION_REQUIRED`, the exact next
  `Mxx-Fxx`, remaining function count, and source evidence still needed. Never
  compress unfinished FRRs into summary prose.

Batch generation strategy:

| Trigger | Required Behavior |
|---|---|
| context estimate for remaining FRRs exceeds 6000 tokens | generate Part 1 Stage 3 in batches |
| one batch | keep the batch under roughly 6000 output tokens; choose module/function boundaries that preserve coherence |
| file-system agent mode | write each batch to the target output file and verify FRR IDs before continuing |
| web/chat mode without file system | write batches as consecutive conversation sections; do not require file writes |
| after every batch | update the PRD Completion Ledger and list the exact next FRR |
| after all batches | run the FRR Completion Gate and repair any failed FRR before Part 2 |

## 第二部分 机器可读扩展层 / Part 2 Machine-Readable Extension Layer

Prerequisite: Part 1 FRR Completion Gate has passed. Every `frr_ref` in
AC-YAML, API stubs, runtime contracts, and agent tasks must point to an existing
FRR in Part 1.

### 2.1 原型数据属性契约 / Prototype Data-Attribute Contract

| View ID | Layout ID | data-testid | data-action | data-field | Expected Handler / Result |
|---|---|---|---|---|---|
| M01-V01 | LAY-M01-V01-R01 | page-M01-V01 / region-filter | create-record | customer_id | opens modal / updates list / emits event |

Rules:

- Every `primary_action` in IA Skeleton must map to a prototype `data-action`.
- Every critical page/region/modal/drawer must have stable `data-testid`.
- Every form field needed for implementation or testing must map to `data-field`.
- Every dynamic role/tab/modal/state surface must be scanned after rendering,
  not only from the initial HTML DOM.

### 2.1.1 原型标注 x PRD 契约交叉校验矩阵

| Prototype Annotation | PRD Contract Location | Coverage Status | Gap / Decision |
|---|---|---|---|
| `data-action` | FRR §6/§7/§9 | COVERED / GAP / SPEC_ONLY | {note} |
| `data-testid` | FRR §4/§16 + AC-YAML | COVERED / GAP / SPEC_ONLY | {note} |
| `data-field` / `data-bind` | FRR §5 / field dictionary | COVERED / GAP / SPEC_ONLY | {note} |
| `data-state` | FRR §9 state machine | COVERED / GAP / SPEC_ONLY | {note} |
| `data-api` + `data-method` | FRR §13 / action-to-API matrix | COVERED / GAP / SPEC_ONLY | {note} |
| `data-visible-role` | FRR §10 RBAC matrix | COVERED / GAP / SPEC_ONLY | {note} |

Block coding tasks for any `GAP` that affects implementation behavior.

### 2.2 结构化验收标准 / Structured Acceptance Criteria (AC-YAML)

When embedded in a PRD, use the `ac_structured` key. When exported as a
standalone file, `ac-structured.yaml` may keep the top-level `acceptance` key.

```yaml
ac_structured:
  - id: AC-M01-F01-001
    frr_ref: M01-F01
    given: "The user has create permission and all required fields are valid"
    when: "The user submits the create form"
    then: "The system creates the record, returns an ID, updates the list, and writes an audit log"
    test_type: integration
    priority: P0
    source_ids: ["SRC-001"]
    view_ids: ["M01-V01"]
    actions: ["create-record"]
    data_testid: "btn-create-record"
    data_action: "create-record"
    frozen_apis:
      - method: POST
        path: /api/{module}/{resource}
        request_schema: schemas/Mxx-Fxx.create.request.json
        response_schema: schemas/Mxx-Fxx.create.response.json
    immutability_rules:
      - "Do not rename request/response fields to satisfy generated tests."
      - "Do not change state enum values without updating FRR section 9."
```

AC ID evolution rules:

- Do not renumber existing AC IDs after assignment.
- Split functions by adding suffixes or new function IDs; keep deprecated IDs
  with `status: deprecated`.
- When behavior changes materially, add `revision`, `supersedes`, or a new AC ID
  and map the old one to migration notes.
- Use `frozen_apis` and `immutability_rules` for AC entries that coding agents
  will turn into tests. These fields prevent agents from changing interfaces,
  enums, permission guards, or lifecycle states merely to make tests pass.

### 2.3 机器可读运行时 / AI 契约 / Machine-Readable Runtime / AI Contract

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
`rollback`, `prompt_file`, `golden_case_file`, and `anchor_case_file` for
model/prompt drift calibration.

### 2.4 API / 事件 / 数据契约桩 / API / Event / Data Contract Stub

#### 2.4.1 API 端点清单 / API Endpoint Inventory

| Method | Path | Auth Required | Description | Idempotency | Source FRR |
|---|---|---|---|---|---|
| GET | /api/{module}/{resource} | yes | list/query | yes | Mxx-Fxx |
| POST | /api/{module}/{resource} | yes | create | required | Mxx-Fxx |
| PUT | /api/{module}/{resource}/{id} | yes | update | yes | Mxx-Fxx |
| DELETE | /api/{module}/{resource}/{id} | yes | delete/logical delete | yes | Mxx-Fxx |

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

#### 2.4.2 Action-to-API Routing Matrix

| data-action | Method | Path | Command / Query | Request Source Fields | Permission | State Guard | Source FRR |
|---|---|---|---|---|---|---|---|
| {action-id} | POST | /api/{resource} | CMD-Mxx-Fxx | {data-field list} | {permission} | {state guard} | Mxx-Fxx |

## 第三部分 Coding Agent 交付包 / Part 3 Coding Agent Delivery Package

Use this directory convention when handing work to a coding agent:

```text
delivery/
  manifest.json
  ia-skeleton.yaml
  prd/
    main.md
    contracts/
      field-dictionary.md
      api-contract.yaml
      events.yaml
  prototype/
    app.html
  acceptance/
    ac-structured.yaml
  agents/
    AGENTS.md
    CLAUDE.md
    .cursor/rules/
  evidence/
```

`delivery/manifest.json` must list every authoritative file with relative path,
role, version, source status, and hash:

```json
{
  "version": "1.0.0",
  "artifacts": [
    {
      "path": "delivery/prd/main.md",
      "role": "prd",
      "version": "1.0.0",
      "source_status": "EMBEDDED",
      "sha256": "{hash}"
    },
    {
      "path": "delivery/prototype/app.html",
      "role": "prototype",
      "version": "locked",
      "source_status": "AUTHORITATIVE_ANNEX",
      "sha256": "{hash}"
    }
  ]
}
```

## 第四部分 验证与评审 / Part 4 Validation And Review

Run deterministic checks before declaring PASS:

```bash
python scripts/validate_prd_quality.py delivery/prd/main.md --target-language zh
python scripts/validate_coding_agent_contract.py --prd delivery/prd/main.md --prototype delivery/prototype/app.html
python scripts/validate_ia_skeleton.py --ia-skeleton delivery/ia-skeleton.yaml --prototype delivery/prototype/app.html --prd delivery/prd/main.md
```

Review checklist:

| Reviewer | Check |
|---|---|
| PM | Human-First layer is readable and business-complete |
| Frontend | `Layout ID`, `data-testid`, `data-action`, and component states are implementable |
| Backend | API, state, permission, idempotency, audit, and event contracts are clear |
| QA | AC-YAML can become automated or manual test cases |
| Coding Agent | package paths, schemas, and source-of-truth order are unambiguous |

## 完成门禁声明 / Gate Completion Statement

```text
Scope: {artifact scope}
Mode / Tier / Profile: {mode} / {tier} / AI-Coding Full PRD
Triggered gates: {gates}
Artifacts updated: {files}
Verification: {scripts/reviews}
Completion state: PASS | REVIEW_COMPLETE_WITH_GAPS | BLOCKED
```
