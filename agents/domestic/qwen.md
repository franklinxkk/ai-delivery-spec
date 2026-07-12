# Qwen Adapter

Prefer explicit source order, output schema, and completion gates. For long
Chinese ToB/ToG inputs, generate a Context Plan first, then retrieve ID slices.
Write one Product Truth fragment or complete-PRD section per turn; never emit a
large monolith before checkpoints.
Validate every Human/Coding/QA projection against Product Truth.
