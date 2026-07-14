# Qwen Adapter

Prefer explicit source order, output schema, and completion gates. For long
Chinese ToB/ToG inputs, generate a Context Plan first, then retrieve ID slices.
Write one unified-PRD requirement/module slice per turn. Generate Product Truth
fragments only when scale or audit triggers them; never emit a large monolith.
Validate the one PRD's human reading path and engineering annex together.
