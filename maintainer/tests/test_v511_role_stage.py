"""Regression for role/seniority requirement-stage collaboration."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAYBOOK = (ROOT / "references/runtime/role-stage-playbook.md").read_text(encoding="utf-8")
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
failures: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


for lane in (
    "Junior product", "Mid-level product", "Senior product",
    "Junior developer", "Mid-level developer", "Senior developer", "Architect",
):
    require(lane in PLAYBOOK, f"missing seniority lane: {lane}")

for role in (
    "Sponsor / business owner", "Product", "Domain owner", "UX / prototype",
    "Engineering / architecture", "QA / acceptance", "Compliance / security",
    "Customer acceptance",
):
    require(role in PLAYBOOK, f"missing role lens: {role}")

for stage in ("Intake", "Clarify", "Specify", "Review", "Baseline", "Change", "Acceptance"):
    require(f"### {stage}" in PLAYBOOK, f"missing stage contract: {stage}")

for marker in ("without inventing", "No-guess", "Static validator PASS", "Coding Agent"):
    require(marker in PLAYBOOK, f"playbook missing handoff boundary: {marker}")

require("role-stage-playbook.md" in SKILL, "SKILL does not route multi-role work to playbook")

if failures:
    raise SystemExit("\n".join(failures))
print("PASS: seven seniority lanes, eight role lenses, and seven requirement stages have bounded handoffs")
