# Example: Higher-Education IT

## Scenario

A university needs to modernize academic affairs, student affairs, teaching
systems, smart classrooms, data dashboards, and AI learning assistants.

## Input Prompt

```text
Use AI Delivery Spec to create a standard PRD for a higher-education IT module.

The system involves academic administrators, teachers, students, counselors,
department leaders, and platform operators.

The module must be readable by product, frontend, backend, algorithm, and QA
teams, with clear state transitions, data contracts, and acceptance criteria.
```

## Expected 0D Triage

For deterministic education workflows:

```text
[TIER: Heavy] | [AI: false] | [WORKFLOW: true]
```

For AI learning assistant, AI course generation, AI Q&A, or adaptive learning:

```text
[TIER: Heavy] | [AI: true] | [WORKFLOW: true]
```

## References To Load

- `SKILL.md`
- `references/delivery-core.md`
- `references/prototype-testability.md` if UI/prototype is in scope
- `references/advanced-extensions.md` for SaaS, mobile, reporting, or AI triggers
- `references/domain-education-it.md`
- `references/readability-layer.md`

## Gate Focus

- Academic calendar and term boundaries.
- Role and organization hierarchy: university, college, major, class, student.
- Course, timetable, exam, grade, attendance, and credit state machines.
- Student affairs workflows: leave, scholarship, warning, dormitory, counseling.
- Data privacy and student record audit.
- AI learning assistant evidence, hallucination controls, and human override.

## Common P0 Decisions

- Which office is the source of truth for student status?
- Can teachers modify grades after submission?
- What approval is required for grade changes?
- How are course conflicts detected?
- What data can AI use for personalized learning recommendations?
- What must be logged for education compliance and dispute handling?
