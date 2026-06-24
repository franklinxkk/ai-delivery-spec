# Changelog

All notable changes to AI Delivery Spec are summarized here.

## v4.6.6 - 2026-06-24

- P0-1: Added `Output Language Rules` to `readability-layer.md`: core rule
  (use prompting user's spoken language), what must be translated, what stays
  in English (technical identifiers, code blocks, standard architectural
  terms), chapter header translation table (18 chapter headers + 11 FRR
  section headers), and language verification rule (English-heavy lines ≤ 20%).
  Added `Language check` item to Readability Acceptance Checklist.
- P0-2: Added `Modal Chain Coverage Rule` to `delivery-core.md`: mandatory
  ≥ 90% modal coverage when source includes HTML prototype, with extraction
  procedure (showModal/Modal.open/dialog/drawer/confirm patterns), coverage
  computation formula, and `MODAL_COVERAGE_GAP` flag for Gate 3 blocking.
- P0-3: Added `check_language_ratio()` function to `validate_prd_quality.py`:
  detects English-heavy lines (≥ 80% ASCII alpha), skips code blocks and table
  separators, fails at > 30% ratio (`LANGUAGE_GAP`), warns at > 20% ratio.
  Verified against v5.0 English PRD (75% → FAIL) and v5.1 Chinese PRD
  (22.5% → PASS with warning).
- P1-4: Added `Module Self-Contained Organization (Optional)` section to
  `readability-layer.md`: optional layout mode for PRDs with ≥5 modules where
  each module is a vertical slice (Overview + FRR + State + Rules + Acceptance +
  Handoff). Includes when-to-use/when-not-to-use rules, structure template,
  trade-off comparison table, and cross-module consistency checklist item.
- P1-5: Added `### Prototype Interaction Ledger` section to `delivery-core.md`
  Stage 0: mandatory extraction procedure (7 inventories: pages, actions,
  modals, state enums, roles, fields, workflows), JSON output format, coverage
  verification table with per-category thresholds (pages 100%, actions 95%,
  modals 90%, etc.), `COVERAGE_GAP` blocking flag, and regression detection
  via ledger diff.
- P1-6: Added `## 9. Version Control And Release Rules` to `SKILL.md`: commit
  flow (pull → selective stage → commit → push), prohibited operations (force
  push to main, blind add, overwrite without pull), release tagging procedure,
  branch strategy (main + feature branches).

## v4.6.5 - 2026-06-23

- P0-1: Added Page Layout + Component Constraint + Interaction Density to
  `readability-layer.md`: per-page layout region diagram, component four-tuple
  constraint (ui_component + component_props + data_source + format_rule),
  and interaction density floor (data-action count per page + mandatory
  columns in interaction result tables).
- P0-2: Added Modal Chain Spec to FRR §6: branch conditions, interception
  modal four elements (trigger / education / guide action / return path),
  and mandatory chain description when prototype has showModal → showModal.
- P0-3: Added `references/realtime-contract.md` for SSE event definitions,
  SLA countdown strategy, alert rule engine, reconnection/polling strategy.
- P0-4: Added Field-level Permission to `delivery-core.md`: three-layer
  permission (function/row/field), role × entity × permission_level matrix,
  mandatory rules when prototype has canViewXxx() / data-visible-role.
- P0-5: Expanded FRR §5 Field Dictionary + Page-Field Matrix: global entity
  field dictionary, per-sub-page independent field lists with Row/Col position,
  component type binding rules (enum→Select, ref→Select.Search, etc.).
- P0-6: Added Computed Metrics specification to `readability-layer.md`:
  compute expression + format rule + source_fields for frontend aggregations,
  visual ratio formulas with boundary values.
- P1-7: Added Drag-Drop Interaction Spec to FRR §6: five-event description
  (dragstart/dragover/dragleave/drop/dragend) + visual feedback + failure
  rollback.
- P1-8: Added Tree/Recursive Component Spec template: data structure
  (id/parentId/children/level) + render rules + cascade selection.
- P1-9: Added Dynamic Form Row + Form Cascade to FRR §5: add/remove triggers,
  row data structure, cascade trigger/target/clear rules.
- P1-10: Added Metric Status Color Mapping: state_value → css_class →
  color_token explicit mapping table.

## v4.6.3 - 2026-06-21

- Added guided requirement shaping for vague ideas, raw pain points, meeting
  notes, boss messages, feature lists, and competitor references.
- Added a 3-5 question Input Clarification Protocol and Opportunity Shaping
  Protocol before full PRD generation.
- Added Adversarial PRD Review Protocol for scope, role path, acceptance,
  boundary, state, permission, dependency, AI overclaim, operations, and
  coding-agent ambiguity attacks.
- Added README output selector and L1 PRD samples for CRM, Higher-Education IT,
  and Medical / Hospital IT examples.

## v4.6.2 - 2026-06-21

- Added the Medical / Hospital IT domain module for HIS/EMR/LIS/PACS/RIS,
  clinical workflow, medical quality, infection control, internet hospital,
  research data governance, and AI-assisted medical operations.
- Added routing and consistency checks for medical-domain loading.
- Added v4.6.1 hardening for coding-agent adoption: AI contract selection
  ladder, AC ID evolution rules, OpenAI/Codex coding-agent entrypoint, and a
  deterministic PRD/prototype `data-*` mapping validator.
- Added v4.6.0 coding-agent compatibility: structured `ac_structured`
  acceptance, machine-readable AI runtime extensions, and generated
  `AGENTS.md` / `CLAUDE.md` / Cursor rules.
- Added a 10-minute README walkthrough and adopter persona guide.
- Added a complete L1 PRD sample for traffic-safety hidden-danger remediation.
- Improved the L1 light PRD core-flow section with a fill-in sentence pattern.
- Added explicit Learn/Retire scope boundaries and a generic post-launch review template.
- Expanded the Higher-Education IT domain module with OBE/accreditation,
  professional construction, smart classroom, student community, and research
  management lifecycle patterns.

## v4.5.2 - 2026-06-18

- Added the Higher-Education IT domain module for academic affairs, student affairs,
  teaching systems, smart classrooms, and education data governance.
- Strengthened PRD readability for human product, engineering, algorithm, and QA
  collaboration.
- Kept product specs as the single source of truth while embedding engineering
  contracts for AI-assisted development.

## v4.5.0 - 2026-06-18

- Introduced the lifecycle bridge from discovery to retirement.
- Added a readability layer for large-company style PRDs.
- Improved routing between product narrative, engineering contract, and QA evidence.

## v4.4.1 - 2026-06-17

- Reworked the spec for human-readable PRD output.
- Added stronger scenario, exception, metrics, and handoff requirements.

## v4.4.0 - 2026-06-16

- Consolidated the protocol into four entrypoints:
  `SKILL.md`, `delivery-core.md`, `prototype-testability.md`, and
  `advanced-extensions.md`.
- Added state-driven prototype rules and presentation-mode expectations.

## v4.3.0 - 2026-06-15

- Strengthened full product specification output.
- Added stronger development and QA readability checks.

## v4.1.0 - 2026-06-13

- Established lifecycle artifact review as a baseline.
- Added precise routing for strategy, PRD, prototype, test, readiness,
  post-launch, and retirement artifacts.

## v4.0.0 - 2026-06-10

- Introduced the tiered delivery model.
- Added domain module support.
- Added SaaS, approval, reporting, AI Native, prompt operations, and readiness gates.
