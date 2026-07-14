# Minimal v5 — 10-minute first run / 十分钟上手

This example demonstrates the bounded requirement-intake path. A one-sentence
idea does not force Product Truth, domain packs or an engineering package.

本例演示最小需求澄清：一句想法不会被强行扩写成大而全 PRD。

## Input / 输入

```text
做一个企业内部知识库，让员工能找到最新制度。
```

## Run / 执行

```bash
python scripts/ai_delivery_spec_cli.py init-requirements --output requirements
python scripts/ai_delivery_spec_cli.py triage --input requirements/intake.yaml
```

Ask the agent to inventory evidence and batch independent material questions.
要求 Agent 先盘点证据，互不依赖的问题成批澄清，有前后依赖时再逐步确认。

## Minimum useful result / 最小有效结果

**Outcome / 结果：** employees can find the currently effective policy within
their permission scope and see its source, version, owner, and update time.

员工可在权限范围内找到当前有效制度，并看到来源、版本、负责人和更新时间。

**First slice / 第一切片：**

```text
Policy owner imports confirmed policies
→ employee searches within data scope
→ result shows title, source, version, owner, and effective time
→ expired policy is excluded and the owner receives a maintenance task
```

**Material questions / 关键问题：**

1. Which employee group and policy category enter the pilot first?
2. Who confirms effectiveness, and what happens to an obsolete version?
3. Is AI answer generation in scope; if yes, which sources, permissions, and citations are mandatory?

**Completion / 完成状态：** `REVIEW_COMPLETE_WITH_GAPS`. Source inventory,
accountable owner, and AI scope still require decisions. This is the intended
safe result, not a failure.
