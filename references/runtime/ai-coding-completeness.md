# Unified PRD Engineering Completeness

Use when development, QA or a Coding Agent must implement an accepted
requirement without inventing business behavior. This is an annex route inside
the unified PRD, not a separate AI Coding PRD.

## Why This Route Exists

A production-practiced publishing/learning project passed structural checks
but its machine-first PRD was unreadable to traditional development. Maintaining
a second Human-First PRD then created competing baselines. The correction is one
document: readable behavior first, precise engineering contract second.

## Sequence

1. Complete intake and clarification; do not restart discovery after scope is approved.
2. Lock the full `REQ/ROLE/FLOW/MOD/VIEW/ACT/FLD/STATE/API/AC` index.
3. Write each main-body module and its matching annex slice together.
4. Assemble `references/templates/unified-requirement-prd-template.md`.
5. Validate readability, PRD quality, Coding Agent completeness and traceability.
6. Walk every role and P0 flow through success, permission, exception, recovery,
   data result and AC.

## L2 Completeness

Require:

- source precedence, intake decision, scope, dependencies and baseline version;
- role journeys, permissions and data scope;
- IA, page/region layout, stable anchors, actions and visible results;
- fields, state transitions, rules, failure/recovery and end-to-end data flow;
- business-level API/integration request, response, error, idempotency,
  authorization and reconciliation when applicable;
- measurable NFR/security/privacy and calculation caliber when applicable;
- executable positive/negative AC with evidence requirements;
- bidirectional `REQ → behavior → AC/test/evidence` traceability;
- change entry and forbidden-invention list.

Technical architecture, database schema, likely files, framework choice,
deployment implementation and sprint breakdown belong to downstream technical
planning unless they are explicit customer-visible or interoperability contracts.

Use `Not applicable + reason + future trigger` for a genuinely irrelevant
contract surface. An empty heading or keyword is not coverage.

## Context Pressure

At medium pressure, stop reloading raw sources and continue from approved IDs.
At high pressure, checkpoint the current requirement/module slice and continue
in the same document. Never merge roles or omit P0 behavior merely to fit one
context window.
