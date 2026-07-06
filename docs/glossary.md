# Glossary

This glossary keeps the public README shorter and gives new users a quick way
to decode AI Delivery Spec terms.

| Term | Meaning |
|---|---|
| 0D triage | Initial classification of tier, AI centrality, workflow presence, and information completeness before loading references. |
| Stage 0 | Reverse-engineering pass for existing prototypes, screenshots, legacy docs, spreadsheets, or competitor products before writing a PRD. |
| IA Skeleton | Stage 3.5 structure that locks module, view, region, role, and primary action relationships before detailed PRD or prototype work. |
| FRR | Functional Requirement Record; one complete function-level product specification with roles, pages, fields, actions, rules, states, permissions, exceptions, NFR, handoff notes, and acceptance. |
| AC-YAML / ac_structured | Machine-readable acceptance criteria linked to FRRs, prototype anchors, data actions, and test paths. |
| Human-First Full PRD | Default implementation handoff profile for human PM/RD/QA/vendor/customer teams; readable business specification comes before machine-readable contracts. |
| AI-Coding Full PRD | Human-First PRD plus AC-YAML, API/data/event contracts, manifest, and coding-agent rules for Cursor, Claude Code, Codex, Copilot, or similar agents. |
| Domain module | Replaceable `references/domain-*.md` file that adds industry vocabulary, states, policies, risks, UI patterns, and test scenarios without polluting the core protocol. |
| Completion state | Final status of an output: `PASS`, `REVIEW_COMPLETE_WITH_GAPS`, or `BLOCKED`. |
| Complexity budget | Rule for counting states, actions, APIs, agents, and document scope by business meaning so small work is not over-modeled. |
