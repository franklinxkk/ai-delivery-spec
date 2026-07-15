"""Keep the always-loaded Skill body lean and domain retrieval selective."""

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
failures: list[str] = []

if len(skill.splitlines()) > 180:
    failures.append("SKILL.md exceeds 180 lines")
if len(skill) > 8500:
    failures.append("SKILL.md exceeds 8,500 characters")
if "Load one stage reference" not in skill:
    failures.append("SKILL lost progressive-disclosure instruction")
if "scripts/query_domain.py --domain <pack>" not in skill:
    failures.append("SKILL loads full domain coverage instead of one compact record")

probe = subprocess.run(
    [sys.executable, str(ROOT / "scripts/query_domain.py"), "--domain", "oa"],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
    capture_output=True,
    check=False,
    env={**os.environ, "PYTHONIOENCODING": "cp1252"},
)
if probe.returncode != 0:
    failures.append("OA compact-domain query failed: " + probe.stdout + probe.stderr)
elif len(probe.stdout) > 5000:
    failures.append("OA compact-domain query exceeds 5,000 characters")
for marker in (
    "domain_id: oa", "maturity: contract_tested", "production_claim: prohibited",
    "KS-OA-WEAVER-WHITEPAPER", "KS-OA-DINGTALK-OSS", "KS-OA-FEISHU-OSS",
):
    if marker not in probe.stdout:
        failures.append(f"OA compact-domain query misses {marker!r}")

if failures:
    raise SystemExit("\n".join(failures))
print(f"PASS: SKILL stays within {len(skill.splitlines())} lines/{len(skill)} chars and domain retrieval is selective")
