# Publishing Authorization and Learning — Coding-Agent Projection

Source: `../truth/product-truth.yaml`. Do not invent behavior outside approved
IDs. This is a brownfield example; inspect the repository baseline before tasks.

## Vertical Slices

| Task | Feature | Result | Source IDs | Acceptance |
|---|---|---|---|---|
| TASK-001 | `FEAT-CONTENT-PUBLISH-001` | publish immutable course version | `MOD-CONTENT-001`, `FLOW-PUBLISH-001`, `ACT-COURSE-PUBLISH` | `AC-PUBLISH-001` |
| TASK-002 | `FEAT-CHANNEL-AUTH-001` | grant channel quota atomically | `MOD-AUTH-001`, `FLOW-AUTH-001`, `ACT-AUTH-GRANT` | `AC-AUTH-001`, `AC-AUTH-OVERLIMIT-001` |
| TASK-003 | `FEAT-CODE-ACTIVATE-001` | activate one code for one learner | `MOD-LEARNING-001`, `FLOW-ACTIVATE-001`, `ACT-CODE-ACTIVATE` | `AC-ACTIVATE-001`, `AC-ACTIVATE-DUPLICATE-001` |
| TASK-004 | `FEAT-LEARNING-EVIDENCE-001` | record learning evidence idempotently | `FLOW-LEARN-001`, `ACT-LEARNING-COMPLETE` | `AC-LEARN-001` |

## Non-Negotiable Contracts

- Enforce course completeness, authorization balance/scope, code validity, and
  entitlement validity on the backend.
- Preserve `VIEW/REG/ACT/FLD/AC` IDs in UI and tests.
- Authorization create + quota decrement is one transaction or compensated
  equivalent.
- Code activation is idempotent by code and learner; a different learner fails.
- Published course versions are immutable; changes create a new version.
- Emit and consume the four `EVT-*` contracts idempotently.
- Write automated, screenshot, and audit evidence to paths declared by AC.

Repository paths, framework choices, endpoint URLs, and database mappings are
intentionally unresolved until the real codebase baseline is inspected. Report
them as implementation decisions, not product inventions.
