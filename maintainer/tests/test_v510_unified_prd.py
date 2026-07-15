"""Regression: one PRD must be readable to humans and executable as a requirement contract."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
complete = ROOT / "maintainer/tests/fixtures/coding-l2.md"
thin = ROOT / "maintainer/tests/fixtures/coding-l2-thin.md"
failures = []


def run(script: str, document: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(ROOT / script), str(document), *args], cwd=ROOT, text=True, capture_output=True)


for script, args in (
    ("scripts/validators/validate_unified_prd.py", ()),
    ("scripts/validators/validate_prd_quality.py", ("--level", "L2")),
    ("scripts/validators/validate_coding_agent_contract.py", ("--level", "L2", "--profile", "full_prd")),
):
    passed = run(script, complete, *args)
    if passed.returncode:
        failures.append(f"complete unified PRD failed {script}: {passed.stdout}{passed.stderr}")
    rejected = run(script, thin, *args)
    if rejected.returncode == 0:
        failures.append(f"thin keyword summary incorrectly passed {script}")

with tempfile.TemporaryDirectory(prefix="ads-css-") as temp:
    good = Path(temp) / "good.html"
    bad = Path(temp) / "bad.html"
    scoped_status = Path(temp) / "scoped-status.html"
    polluted_status = Path(temp) / "polluted-status.html"
    good.write_text('<style>.hidden { display:none !important; } .modal { display:block; }</style><div class="hidden"></div>', encoding="utf-8")
    bad.write_text('<style>.hidden,.modal { display:none !important; } .button { color:red !important; }</style><div class="hidden"></div>', encoding="utf-8")
    scoped_status.write_text('<style>.page.active { display:block; } .status.active,.status.passed { color:green; }</style>', encoding="utf-8")
    polluted_status.write_text('<style>.page.active { display:block; } .published,.active,.passed { color:green; }</style>', encoding="utf-8")
    if run("scripts/scan_prototype_css.py", good).returncode:
        failures.append("isolated hidden utility should pass CSS pollution scan")
    if run("scripts/scan_prototype_css.py", bad).returncode == 0:
        failures.append("combined hidden selector and unrelated !important must fail CSS pollution scan")
    if run("scripts/scan_prototype_css.py", scoped_status).returncode:
        failures.append("component-scoped status selectors should pass CSS pollution scan")
    if run("scripts/scan_prototype_css.py", polluted_status).returncode == 0:
        failures.append("grouped global active status selector must fail CSS pollution scan")

if failures:
    raise SystemExit("\n".join(failures))
print("PASS: v5.1.0 unified PRD is human-readable, AI-coding complete, and prototype CSS-safe")
