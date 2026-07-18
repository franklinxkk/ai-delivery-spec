# Troubleshooting, Recovery And Anti-Patterns

Load this reference only when a command fails, a large run is interrupted, or a
user asks why an artifact was blocked. Do not load it during a successful
Ultra-Light or Standard flow.

## Three-Minute Recovery

1. Keep the failing artifact and command unchanged.
2. Read the first finding code and its ref; do not repair all findings at once.
3. Run:

    python scripts/ai_delivery_spec_cli.py explain-finding <CODE>

4. Repair only the bounded contract named by that finding. A gate never authorizes
   invented business values.
5. Rerun the exact RETRY command printed by the gate.
6. For an interrupted large-project run, verify the checkpoint first:

    python scripts/ai_delivery_spec_cli.py resume

Continue only the reported stage and stable-ID slice. If the checkpoint reports
version, anchor, or repository drift, create an approved new checkpoint instead
of silently continuing.

## Common Symptoms

| Symptom | Likely Cause | Repair |
|---|---|---|
| ModuleNotFoundError | 首次运行未安装 PyYAML/jsonschema | `python -m pip install -r scripts/requirements.txt`；Windows 可用 `py -3 -m pip ...` |
| GATE-MISSING-INPUT | gate profile and supplied artifacts differ | add the named PRD/register/prototype path or choose the narrower profile |
| REQ-PARSE / REQ-SCHEMA | malformed YAML or missing lifecycle field | repair the exact schema path using the requirement-register template |
| PRD-STRUCTURE / PRD-TOO-THIN | headings exist without implementable local contracts | complete the relevant narrative and engineering annex; do not add empty headings |
| PROTO-NO-PAGE-ANCHOR | page cannot be traced to VIEW-* | add one unique data-testid="page-VIEW-*" root |
| PROTO-UNHANDLED-ACTION | button has no dispatch or visible outcome | bind one data-action handler and expose success/failure/state result |
| PROTO-DYNAMIC-ANCHOR-CONSTRUCTION | data-* 名称由字符串拼接，静态门禁无法枚举真实动作 | 在模板源码直接写稳定锚点；再用浏览器证据证明动态控件 |
| PRD-P0-UNKNOWN-NOT-STRUCTURED | open ID 只有 REV/自由文本，没有 owner/阶段/影响范围 | 使用 `UNK-*` 结构化登记并同步 open_p0_unknown_ids |
| PROTO-CSS-* | global or !important rules corrupt visibility/state | scope CSS to the owning component and explicit data-state |
| HANDOFF-* | PRD and one or more prototypes drift | repair the single PRD baseline and every affected surface using the same stable ID |
| Product Truth compile stops | monolith or unresolved cross-fragment reference | keep fragments, validate the current fragment, compile, repair unresolved IDs, resume |
| run interrupted or context lost | no visible checkpoint/recovery entry | run resume; continue the last valid stage/ID slice only |

JSON output includes Chinese cause/fix/repair example, retry command and
`not_proven`, so IDE/Coding Agent need not parse prose or误读静态 PASS。

## Product Truth Without Long-Run Deadlock

Product Truth remains conditional. Use it for controlled projections, repeated
cross-module change, lineage, strong audit, or an explicit authority decision.
Page/module/input counts alone are not a sufficient trigger.

When triggered:

1. write 00-core.yaml and one MOD-* fragment at a time;
2. validate the current fragment before adding another;
3. compile fragments and repair unresolved references;
4. checkpoint the compiled hash and active ID slice;
5. resume from the checkpoint, never regenerate the monolith through a subagent.

A failed compile is not permission to delete unknown IDs, fabricate targets, or
weaken schemas. Preserve UNK/REV items until the responsible person decides.

## Concentrated FAQ

**Does PASS mean the requirement is correct?** No. It proves bounded static
contracts only. Domain owners, browser journeys, QA execution, and customer
acceptance remain accountable evidence.

**Should I fix every warning automatically?** No. Gates locate gaps and never
make business decisions. Mechanical formatting may be automated; roles, rules,
limits, permissions, states, and acceptance values require evidence or an owner.

**Why did a small request trigger many artifacts?** Inspect the silent route.
One reversible, role-local, non-regulated change should be a requirement card;
override `delivery_shape` only when the impact evidence supports it.

**Why did the gate reject a long PRD?** Length is not completeness. Every
implemented view needs its local fields, actions, states, metrics, exceptions,
data flow, and acceptance links.

**Can I continue after a validator outage?** Only through the explicit
service-outage and human-approval path already defined by execution state.
Never convert an unavailable validator into an implicit pass.

**How do we keep private rules out of the public repository?** Run
`init-custom`. The generated directory is ignored by default. Only declarative
regex validators are loaded; binding-rule conflicts require `DEC-CONFLICT-*`.

## Anti-Patterns

- Generate a giant Product Truth before requirement intake or P0 clarification.
- Ask a subagent to regenerate the entire truth after one unresolved reference.
- Add headings, keywords, buttons, or data-testid values solely to satisfy a gate.
- Treat a static PASS as domain expertise, legal advice, customer sign-off, or
  production evidence.
- Maintain separate human and AI PRD baselines with different rules.
- Repair prototype drift by stacking duplicate handlers or global CSS overrides.
- Resume from a changed repository, skill version, or source set without a new
  approved checkpoint.
