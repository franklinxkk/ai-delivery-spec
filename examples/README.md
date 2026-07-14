# Examples

v5 intentionally keeps a small number of evidence-shaped examples instead of
many shallow domain PRDs.

| Example | Purpose | Claim Status |
|---|---|---|
| [Publishing Authorization and Learning v5](publishing-learning-v5/README.md) | optional large-project Product Truth + one unified PRD for a multi-role ToB chain | schema/reference validated; behavior not run |
| [Generic Energy Capsule v5](generic-energy-capsule-v5/README.md) | unfamiliar-domain discovery without a dedicated pack | capsule schema validated; professional unknowns remain |
| [Traffic Regulatory Change v5](traffic-regulatory-change-v5/README.md) | regulated source update and impact/change semantics | change schema validated; behavior not run |
| [Newcomer SaaS Light v5](minimal-v5/README.md) | low-context first use without heavy modeling | review-complete-with-gaps example |

New public examples must add a distinct requirement-management stage, project
shape, consumer, or evaluation dimension. Do not add another short PRD merely
to list a domain.

Behavioral scenarios live in `evals/eval-catalog.yaml`; evidence must be stored
separately from expected behavior.

Real open-source requirement/design/handoff cases live in
`evals/github-cases.yaml`, pinned to repository commits. They are evaluation
inputs rather than examples to copy into customer products.
