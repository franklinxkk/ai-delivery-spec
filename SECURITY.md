# Security And Sensitive Artifact Policy

## Reporting A Vulnerability

Use GitHub private vulnerability reporting / Security Advisories when available.
Do not open a public issue containing an exploit, credential, private customer
artifact, personal data, or sensitive production path.

## Repository Safety Boundary

This repository must not contain:

- credentials, API keys, tokens, cookies, private URLs, or production secrets;
- customer-identifiable PRDs, screenshots, exports, logs, prompts, or datasets;
- personal or regulated data that is not demonstrably anonymized;
- paid/protected standards or research copied in full;
- executable evidence that writes to live customer/production systems by default.

Examples and eval fixtures use synthetic or safely anonymized data. Automated
prototype/browser checks use mock, shadow, or disposable environments.

## AI And Domain Claims

- Model memory is not an authority source.
- Mocked scenarios and simulated reviewers are not expert/production evidence.
- High-risk professional rules require official/accountable sources and named
  responsibility.
- Coding agents must not expand permissions or invent consequential business
  behavior when Product Truth is incomplete.

## Dependency And Release Checks

CI validates Python syntax, Product Truth Schema/reference closure, public claim
alignment, domain source freshness, migration behavior, and projection IDs.
Release owners should also review dependency advisories, generated artifacts,
and the staged diff before tagging a stable version.
