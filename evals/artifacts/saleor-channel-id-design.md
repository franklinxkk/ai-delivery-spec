# Saleor Channel Identifier — Product Design Evaluation

Case: `GH-SALEOR-CHANNEL-ID`

Pinned repository: `saleor/saleor@697b9ec6ffb93199f62f783e7bf6c550cd3bcf7e`

This is an evaluation artifact, not a Saleor roadmap proposal. The GitHub issue
is user evidence; maintainer acceptance and current roadmap status remain
unknown. The pinned `ProductQueries` baseline still exposes `channel` as a slug
for product and collection queries, so implementation must begin with a fresh
maintainer decision rather than assuming the issue is approved.

## Contract

- `OBL-SAL-REQ-ID`: introduce an immutable channel-ID selector without changing
  channel availability, unpublished-product permission, app, pagination, or
  filtering semantics.
- `OBL-SAL-REQ-COMPAT`: retain the legacy `channel` slug input for a declared
  compatibility window. If deprecation is approved, expose it in GraphQL schema
  metadata and migration notes; do not silently reinterpret it as an ID.
- `OBL-SAL-DES-PRECEDENCE`: accept exactly one selector among `channelId`,
  `channelSlug`, and legacy `channel`. Zero selectors follows the existing
  default-channel behavior. Multiple selectors return a stable argument error;
  they are not resolved by undocumented precedence.
- `OBL-SAL-DES-SCOPE`: ID lookup changes identity resolution only. It must not
  broaden product visibility, channel listing, permission, or database-routing
  behavior.

## Required states and failures

| Condition | Visible/API result | Domain result |
|---|---|---|
| valid ID | existing query shape | resolve the same Channel object as its slug |
| valid explicit slug | existing query shape | current slug resolution remains valid |
| legacy argument | existing query shape plus deprecation metadata when approved | current behavior preserved |
| ID and slug supplied | typed argument error | no resolver/query execution |
| unknown or unauthorized channel | existing not-found/permission policy | no information leakage |
| slug renamed | ID-based client remains stable | old slug behavior follows declared compatibility policy |

## Coding handoff boundary

Probe `saleor/graphql/product/schema.py`, channel loaders/utilities, product
resolvers, schema snapshots, and permission tests. Do not name a new loader or
database change until repository evidence shows it is required. Required tests
cover each selector, selector conflicts, default-channel behavior, permissions,
renamed slugs, pagination/filter parity, and generated GraphQL schema.

Completion: `REVIEW_COMPLETE_WITH_GAPS` — design obligations are closed for the
evaluation input; maintainer decision, full affected-query inventory, and code
execution are not proven.
