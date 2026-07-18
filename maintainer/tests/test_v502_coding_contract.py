from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
validator = ROOT / "scripts/validators/validate_coding_agent_contract.py"
complete = ROOT / "maintainer/tests/fixtures/coding-l2.md"
thin = ROOT / "maintainer/tests/fixtures/coding-l2-thin.md"

# Core validators must preserve the L0-L4 compatibility surface.
for level in ("L0", "L1", "L2", "L3", "L4"):
    for script, fixture in (
        ("validate_prd_quality.py", "coding-l2.md"),
        ("validate_ia_skeleton.py", "ia-l2.yaml"),
        ("validate_coding_agent_contract.py", "coding-l2.md"),
    ):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validators" / script),
             str(ROOT / "maintainer/tests/fixtures" / fixture), "--level", level],
            cwd=ROOT, text=True, capture_output=True,
        )
        if result.returncode:
            raise SystemExit(f"failed {script} {level}\n" + result.stdout + result.stderr)

passed = subprocess.run(
    [sys.executable, str(validator), str(complete), "--level", "L2"],
    cwd=ROOT, text=True, capture_output=True,
)
if passed.returncode:
    raise SystemExit("complete AI Coding PRD fixture must pass\n" + passed.stdout + passed.stderr)

rejected = subprocess.run(
    [sys.executable, str(validator), str(thin), "--level", "L2"],
    cwd=ROOT, text=True, capture_output=True,
)
if rejected.returncode == 0:
    raise SystemExit("thin keyword-only handoff must fail")

print("PASS: L0-L4 validators accept complete unified contracts and reject thin keyword summaries "
      f"({rejected.stdout.count('FAIL:')} missing-contract findings)")
