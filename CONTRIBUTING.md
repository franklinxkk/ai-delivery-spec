# Contributing to AI Delivery Spec

Thanks for helping improve AI Delivery Spec.

## Ways To Contribute

### Report Issues

- Open an issue.
- Include expected behavior, actual behavior, reproduction steps, AI tool used,
  and the relevant artifact path if possible.

### Suggest Enhancements

- Open an issue with an `[Enhancement]` prefix.
- Describe the scenario, current limitation, proposed solution, alternatives,
  and why the change should live in the core spec instead of a project-local
  PRD/template.

### Add A Domain Module

Domain modules make AI Delivery Spec useful in new industries.

1. Copy `references/domain-module-template.md`.
2. Keep the 15-section domain contract exactly:
   `Domain Purpose`, `Vocabulary`, `Aggregates and Entities`,
   `Domain Events`, `State Machines`, `Metric / Indicator Governance`,
   `AI Context Sources`, `Content / Knowledge Assets`, `Core Workflows`,
   `Role Path Patterns`, `UI / Mobile Patterns`,
   `Policy / Privacy Constraints`, `Domain Test Scenarios`,
   `Multi-Agent Lifecycle Verification Matrix`, `Acceptance Checklist`.
3. Fill in domain entities, roles, workflows, policies, terminology, privacy
   rules, test scenarios, and a compact First-Principles Domain Lens.
4. Name it `references/domain-{your-domain}.md`.
5. Update `references/advanced-extensions.md` trigger matrix and domain list.
6. Add or update at least one example if the domain is meant for public use.

### Fix Bugs Or Improve Protocol

1. Fork the repo.
2. Create a branch: `fix/short-description` or `feat/short-description`.
3. Make a focused change.
4. Run validation:

   ```powershell
   py scripts/validate_skill_consistency.py
   py scripts/validate_routing_scenarios.py
   py scripts/validate_prd_quality.py references/templates/human-first-prd-template.md --allow-wildcards
   py scripts/validate_prd_quality.py references/templates/ai-coding-prd-template.md --allow-wildcards
   ```

5. Submit a PR with a clear description and test output.

## PR Checklist

- [ ] Changes are consistent with the 4-entrypoint architecture.
- [ ] The change is not a one-off reference file unless it is justified by at
      least three real projects, two domains, and one validator change.
- [ ] Domain-specific content stays in `references/domain-*.md`, not in core
      runtime files.
- [ ] New domain modules keep the 15-section domain contract.
- [ ] New domain modules include a First-Principles Domain Lens without turning
      the file into an industry encyclopedia.
- [ ] New domain modules update `advanced-extensions.md` trigger matrix and
      domain list.
- [ ] Validation scripts pass where applicable.
- [ ] README is updated if a public feature, install path, or domain changes.
- [ ] No secrets, credentials, private customer data, or personal data are
      included.

## Design Principles

1. Depth over breadth: one complete delivery protocol, not scattered skills.
2. Routing over loading: load only what each artifact needs.
3. Domain-neutral core: industry knowledge lives in replaceable modules.
4. Gates guard quality: every artifact passes defined gates.
5. Readable by humans and AI: Markdown that both can parse.
6. Compact references: keep runtime entrypoints, current templates, domains,
   coding-agent add-ons, validators, and examples; avoid legacy protocol sprawl.

## Style

- Markdown: clear headings, short sections, stable tables.
- Python: PEP 8 where practical.
- YAML: 2-space indentation.
- Avoid mojibake or mixed encodings. Use UTF-8.

## License

By contributing, you agree your contributions are licensed under Apache-2.0.
