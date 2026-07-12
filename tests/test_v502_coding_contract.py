from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
validator = ROOT / "scripts/validators/validate_coding_agent_contract.py"
complete = ROOT / "tests/fixtures/coding-l2.md"
thin = ROOT / "tests/fixtures/coding-l2-thin.md"

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

print("PASS: v5.0.2 accepts complete contracts and rejects thin keyword summaries "
      f"({rejected.stdout.count('FAIL:')} missing-contract findings)")
