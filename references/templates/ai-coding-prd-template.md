# AI-Coding Full PRD Template (v4.9.3 Profile)

Use this profile only when the user explicitly wants a coding agent, full AI
implementation, machine-readable contracts, test stubs, or an implementation
handoff package. AI-Coding Full PRD is an extension of Human-First Full PRD,
not a replacement.

## Contents

- Heading Hierarchy Lock
- 0D Triage And PRD Profile
- Prototype Interaction Ledger Extraction
- Part 1 Human-First Foundation Layer
- Part 2 Machine-Readable Extension Layer
- Part 3 Coding Agent Delivery Package
- Part 4 Validation And Review
- Gate Completion Statement

## Heading Hierarchy Lock

- Use exactly one H1 (`#`) for the document title.
- Use H2 (`##`) for global lifecycle stages or top-level parts.
- Use H3 (`###`) for module subsections, machine-readable blocks, and package sections.
- Use H4 (`####`) for FRR numbered sections inside one function.
- Do not jump from H2 directly to H4.
- Do not use bold text, table rows, or numbered list items as fake headings.
- In Chinese PRDs, translate headings but keep the hierarchy unchanged.
- If generated `AGENTS.md`, `CLAUDE.md`, or Cursor rules are included inline in
  the same Markdown file, put them under H2/H3 annex headings or fenced code
  blocks. Do not start them with a second H1 such as `# AGENTS.md`.

## 0D Triage And PRD Profile

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

## Prototype Interaction Ledger Extraction

If the source prototype HTML is larger than 100KB, first run:

```bash
python scripts/extract_interaction_ledger.py --input {prototype.html} --output prototype-interaction-ledger.json
```

Use the lightweight ledger as the primary context for pages, actions, modals,
states, roles, fields, and workflows. Do not load a very large prototype into
the main context when the ledger can provide the required implementation
evidence. The full prototype remains an authoritative source file and should be
referenced through path, `view_id`, `data-testid`, and `data-action`.

## Part 1 Human-First Foundation Layer

Before adding any machine-readable blocks, inline the full Human-First Full PRD
in this document. Do not write "see human-first-prd-template.md" as a substitute
for content. Part 1 must include all modules and every complete FRR.

Required foundation, all inline:

- source evidence register;
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
| Module coverage | every in-scope module has at least one FRR or a clear deferred reason |
| State machine | every FRR section 9 has state/button/lifecycle behavior or `N/A + reason` |
| Permission | every FRR section 10 has role/data/action permission or `N/A + reason` |
| Acceptance | every FRR section 16 has prose acceptance before AC-YAML |

If any check fails, return to Part 1 and complete the missing FRR before writing
Part 2. Coding agents need scenario context to avoid implementing technically
valid but business-wrong behavior.

Batch generation strategy:

| Trigger | Required Behavior |
|---|---|
| context estimate for remaining FRRs exceeds 6000 tokens | generate Part 1 Stage 3 in batches |
| one batch | keep the batch under roughly 6000 output tokens; choose module/function boundaries that preserve coherence |
| file-system agent mode | write each batch to the target output file and verify FRR IDs before continuing |
| web/chat mode without file system | write batches as consecutive conversation sections; do not require file writes |
| after all batches | run the FRR Completion Gate |

## Part 2 Machine-Readable Extension Layer

Prerequisite: Part 1 FRR Completion Gate has passed. Every `frr_ref` in
AC-YAML, API stubs, runtime contracts, and agent tasks must point to an existing
FRR in Part 1.

### 2.1 Prototype Data-Attribute Contract

| View ID | Layout ID | data-testid | data-action | data-field | Expected Handler / Result |
|---|---|---|---|---|---|
| M01-V01 | LAY-M01-V01-R01 | page-M01-V01 / region-filter | create-record | customer_id | opens modal / updates list / emits event |

Rules:

- Every `primary_action` in IA Skeleton must map to a prototype `data-action`.
- Every critical page/region/modal/drawer must have stable `data-testid`.
- Every form field needed for implementation or testing must map to `data-field`.

### 2.2 Structured Acceptance Criteria (AC-YAML)

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
```

AC ID evolution rules:

- Do not renumber existing AC IDs after assignment.
- Split functions by adding suffixes or new function IDs; keep deprecated IDs
  with `status: deprecated`.
- When behavior changes materially, add `revision`, `supersedes`, or a new AC ID
  and map the old one to migration notes.

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

#### 2.4.1 API Endpoint Inventory

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

## Part 3 Coding Agent Delivery Package

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

## Part 4 Validation And Review

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

## Gate Completion Statement

```text
Scope: {artifact scope}
Mode / Tier / Profile: {mode} / {tier} / AI-Coding Full PRD
Triggered gates: {gates}
Artifacts updated: {files}
Verification: {scripts/reviews}
Completion state: PASS | REVIEW_COMPLETE_WITH_GAPS | BLOCKED
```
