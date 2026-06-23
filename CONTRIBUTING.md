# Contributing to AI Delivery Spec

Thanks for your interest in improving AI Delivery Spec! 🎉

## Ways to Contribute

### 🐛 Report Issues
- Open an [Issue](https://github.com/franklinxkk/ai-delivery-spec/issues)
- Include: expected behavior, actual behavior, steps to reproduce, AI tool used

### 💡 Suggest Enhancements
- Open an Issue with `[Enhancement]` prefix
- Describe: the scenario, current limitation, proposed solution, alternatives considered

### 🌍 Add a Domain Module
Domain modules make AI Delivery Spec useful in new industries.

1. Copy `references/domain-module-template.md`
2. Fill in: domain entities, roles, common workflows, regulatory requirements, terminology
3. Name it `references/domain-{your-domain}.md`
4. Submit a PR

### 🔧 Fix Bugs or Improve Protocol
1. Fork the repo
2. Create a branch: `fix/short-description` or `feat/short-description`
3. Make your changes
4. Run validation:
   ```powershell
   py scripts/validate_skill_consistency.py
   py scripts/validate_routing_scenarios.py
   ```
5. Submit a PR with a clear description

### 📝 Improve Documentation
- Fix typos, clarify ambiguous wording, add examples
- Documentation PRs don't need validation scripts to pass

## PR Checklist

- [ ] Changes are consistent with the 4-entrypoint architecture
- [ ] Domain-specific content goes in `references/domain-*.md`, not in core files
- [ ] Validation scripts pass (if applicable)
- [ ] README updated if new feature/module added
- [ ] No secrets, credentials, or personal data

## Design Principles

1. **Depth over breadth** — One complete delivery protocol, not 50 scattered skills
2. **Routing over loading** — Load only what each artifact needs (0D triage)
3. **Domain-neutral core** — Industry knowledge in replaceable modules
4. **Gates guard quality** — Every artifact passes through defined gates
5. **Readable by humans and AI** — Markdown that both can parse

## Code Style

- Markdown files: 80-char line width where possible
- Python scripts: follow PEP 8
- YAML files: 2-space indent

## Questions?

Open an Issue with `[Question]` prefix. We're friendly! 😊

## License

By contributing, you agree your contributions are licensed under Apache-2.0.
