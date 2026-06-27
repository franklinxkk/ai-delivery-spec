# Changelog

All notable changes to AI Delivery Spec are summarized here.

## v4.9.6 - 2026-06-27

- Further simplified `SKILL.md` frontmatter `description` for agentskill.sh:
  single-line, short, no folded YAML, no colon-space sequence, and no slash-heavy
  parser edge cases.
- Updated README badge and release metadata to v4.9.6.

## v4.9.5 - 2026-06-27

- Changed `SKILL.md` frontmatter `description` from folded YAML block syntax
  to a standard single-line string for agentskill.sh parser compatibility.
- Preserved the trigger exclusions for code-only syntax/debugging, copy
  rewriting, and idea exploration with no delivery intent.

## v4.9.4 - 2026-06-27

- Reworked `README.md` for community discovery and first-screen conversion:
  clearer pain statement, production outputs, install path, quick-start prompts,
  work-path selector, PRD profile selector, and toolchain positioning.
- Kept the README tool-agnostic and bilingual so product managers, developers,
  QA, AI-native teams, and coding-agent users can quickly identify the workflow
  that fits their job.

## v4.9.3 - 2026-06-27

- Added the `skills.sh` badge and a dedicated `npx skills add
  franklinxkk/ai-delivery-spec` install path in `README.md`.
- Added backward-compatible `--language-threshold` handling in
  `validate_prd_quality.py`, mapping `zh/en/none` to `--target-language` and
  preserving numeric ratio support.
- Reduced lazy-reference false positives for FRR operation matrices that use
  repeated role/status cells such as "same as above" or "同上".
- Added bilingual/community health checks to `validate_skill_consistency.py`
  so README and routing scenarios keep valid Chinese content and avoid mojibake.
- Added automated domain-module sync checks across domain files,
  `domain-module-template.md`, `CONTRIBUTING.md`, `README.md`, and
  `advanced-extensions.md`.
- Added `validate_release_readiness.py` to simulate traditional PRD,
  AI-native, AI-coding, PRD review, competitor/prototype, lifecycle, mobile,
  and launch/retirement paths before release.
- Synchronized release metadata across `SKILL.md`, README badge, OpenAI
  metadata, templates, and community submission docs.

## v4.9.2 - 2026-06-27

- Tightened Human-First PRD field guidance: when a locked prototype exists,
  FRR section 5 must list only prototype-invisible field rules instead of
  repeating every visible field already shown in the prototype.
- Clarified that Work Path is selected before PRD Profile: work path controls
  lifecycle scope, while PRD profile controls document format and consumer.
- Relaxed AI-Coding batch guidance from fixed module/FRR limits to context-size
  batching and added web/chat mode handling.
- Added an explicit AI-Coding heading rule preventing generated `AGENTS.md` or
  `CLAUDE.md` content from becoming a second H1 in the same PRD.
- Added Stage 4 `TRK` development follow-up and `BUG` defect register outputs
  to `delivery-core.md`.
- Rebuilt routing validation with clean bilingual English/Chinese scenarios.
- Reduced Chinese PRD language-ratio false positives by down-weighting common
  technical identifiers such as `data-testid`, `FRR`, `AC-YAML`, and `Mxx-Fxx`.
- Rewrote `CONTRIBUTING.md` without encoding corruption and added domain-module
  14-section and `advanced-extensions.md` sync checklist items.

## v4.9.1 - 2026-06-27

- Cleaned the reference architecture for community distribution. Removed legacy
  split-protocol references that had already been consolidated into
  `delivery-core.md`, `advanced-extensions.md`, current PRD templates, or
  coding-agent compatibility.
- Reduced `references/` from 42 files to 17 focused files: runtime entrypoints,
  current templates, domain modules, coding-agent compatibility, realtime
  contract, and readability layer.
- Rewrote README with a clean bilingual structure and removed corrupted legacy
  Chinese text.
- Updated `advanced-extensions.md` so it is the authoritative compact extension
  pack instead of an index pointing to many old reference files.
- Rebuilt `validate_skill_consistency.py` to enforce the compact architecture
  and fail when deleted legacy references are reintroduced.

## v4.9.0 - 2026-06-27

- Added lifecycle-strengthening rules for traditional PM delivery: discovery
  evidence, competitor/alternative analysis, value assessment, prioritization,
  EARS requirement writing, development follow-up, issue flow, bug triage, and
  post-launch review.
- Restored Human-First Full PRD template FRR scaffolding to the authoritative
  16-section structure, including notifications/audit/dependencies, data/AI/
  algorithm contract, function-level NFR, frontend/backend/QA handoff notes,
  and acceptance/traceability.
- Hardened AI-Coding Full PRD: Part 1 must inline the complete Human-First
  specification and pass the FRR Completion Gate before AC-YAML, API stubs,
  runtime contracts, or agent handoff sections are written.
- Added large-prototype context safety: prototypes over 100KB should first be
  converted into an interaction ledger via `extract_interaction_ledger.py`.
- Added batch generation guidance for large PRDs, plus WBS, risk register, key
  dependencies, open questions, global state summary, domain event inventory,
  and API endpoint inventory templates.
- Aligned coding-agent delivery package and manifest rules across templates,
  core routing, and `coding-agent-compat.md`.
- Strengthened manifest validation in `validate_prd_quality.py` when a package
  manifest is supplied.
- Reduced PRD bloat in FRR section 5.2: when a locked prototype exists, sub-page
  field lists must not repeat all positional fields. They should list only
  prototype-invisible rules such as permission differences, state-conditional
  editability, enum values not visible in the prototype, and cross-field
  linkage.
- Hardened `validate_prd_quality.py` lazy-reference detection so legal prototype
  anchors such as `[page-xxx]`, `[modal-xxx]`, `[region-xxx]`, and `[btn-xxx]`
  do not fail only because the paragraph omits the literal word
  `data-testid`.

## v4.7.3 - 2026-06-27

- Added three explicit product work paths: Traditional Product Lifecycle,
  AI Native Product Discovery, and AI Coding Delivery.
- Added profile-specific templates:
  `references/templates/human-first-prd-template.md` and
  `references/templates/ai-coding-prd-template.md`.
- Added heading hierarchy lock rules to the PRD templates and deterministic
  heading validation in `scripts/validate_prd_quality.py` so generated PRDs
  cannot pass with multiple H1 headings or skipped heading levels.
- Added stable `Layout ID` rules for PRD page/region/modal/drawer/panel
  specifications so layout detail can be traced across PRD, prototype,
  screenshots, acceptance, and coding-agent handoff.
- Strengthened PRD layout tables with `LAY-{view_id}-{RNN|MNN|DNN|PNN}`
  identifiers.
- Updated README with Chinese search keywords and work-path guidance for
  community adoption.
- Expanded recommended GitHub topics and Chinese community tags for PM,
  AI coding, PRD, prototype, ToB/ToG, and domain discovery.

## v4.7.2 - 2026-06-26

- Added explicit PRD Profile selection: `Contract Summary`,
  `Human-First Full PRD`, and `AI-Coding Full PRD`.
- Made Human-First Full PRD the default for formal PM/RD/QA/vendor handoff:
  complete scenarios, page/region layout, field behavior, interaction flow,
  business rules, exceptions, permissions, NFR, acceptance, and handoff notes.
- Clarified that AI-Coding Full PRD is additive: it keeps human-readable
  product specifications and adds `ac_structured`, machine-readable contracts,
  package manifest, and coding-agent rules.
- Corrected prototype-to-PRD rules: locked prototypes are authoritative
  evidence, but FRR §4-§6 must normalize layout/field/action/modal behavior
  into implementable PRD text instead of saying only "see prototype".
- Strengthened prototype contracts with `STATE_ENUMS`, modal/drawer identity,
  runtime role contract, and action/API contract guidance.
- Hardened validation scripts:
  `validate_prd_quality.py` now flags lazy references such as "见原型" without
  traceable detail; `validate_coding_agent_contract.py` now checks unresolved
  AC placeholders, template states, modal identity, and action/API contracts.
- Updated migration guidance for v4.7.2 and aligned the standard PRD template
  with lifecycle-style human review plus AI-coding enrichment.

## v4.7.1 - 2026-06-25

- Release hardening: synchronized `SKILL.md`, `README.md`, `CHANGELOG.md`, and
  validation scripts around the current public version.
- Rewrote `README.md` as a concise bilingual public landing page with clear
  user personas, quick start, delivery package convention, runtime architecture,
  domain modules, examples, and validation commands.
- Made Stage 3.5 IA Skeleton trigger visibility explicit in `SKILL.md` routing:
  run when the scope has two or more modules, two or more primary roles, or any
  cross-module lifecycle.
- Strengthened coding-agent handoff with a standard `delivery/` package layout
  and source-of-truth lookup order.
- Clarified IA Skeleton deduplication rules for readable PRD layout sections:
  reference locked `region_id` values instead of rewriting page regions.
- Linked mobile/multi-surface delivery and CRM domain usage back to Stage 3.5
  IA Skeleton and FRR anti-bloat rules.
- Hardened IA validation so `primary_actions` can be checked against prototype
  `data-action` values.

## v4.7.0 - 2026-06-25

- Added Stage 3.5 IA Skeleton Gate to `delivery-core.md`: PM-facing structural
  contract (role × module × view × region × primary action) confirmed before
  Stage 4/5. Trigger: ≥2 modules OR ≥2 primary roles OR any cross-module flow.
  Gate failures block Stage 5. IA Skeleton YAML format with view completeness,
  region minimality, action minimality, cross-view flow, and confirmation lock
  rules.
- Added `scripts/validate_ia_skeleton.py`: validates IA Skeleton ↔ Prototype ↔
  PRD cross-references. Checks view_id format, region_id existence, role view
  coverage, cross-module flow source/target existence, prototype data-testid
  matching, PRD view/data-action/data-testid reference consistency.
- Added `references/templates/field-dictionary-template.md`: reusable global
  entity field dictionary template with per-entity table format, per-sub-page
  field list, and component binding rules.
- Added `references/prototype-testability.md`: state-driven prototype and
  testability kernel extracted from delivery-core. Covers GlobalState,
  transition() pattern, data-action/data-testid/data-state annotation rules,
  demo-closed prototype verification.
- Enhanced `delivery-core.md`: prototype interaction ledger, coverage
  verification table with per-category thresholds, regression detection via
  ledger diff, prototype iteration parity gate.
- Enhanced `readability-layer.md`: Per-Page Layout Region Diagram, Component
  Four-Tuple Constraint, Computed Metrics Specification, Visual Ratio
  Computation with boundary clamping.

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
