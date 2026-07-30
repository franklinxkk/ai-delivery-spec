"""Audit README commands against the public CLI without executing placeholder-only examples."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "ai_delivery_spec_cli.py"
README = (ROOT / "README.md").read_text(encoding="utf-8")
failures: list[str] = []


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], cwd=ROOT,
        text=True, encoding="utf-8", capture_output=True,
    )


help_result = run("--help")
if help_result.returncode != 0 or "Traceback" in help_result.stderr:
    failures.append("public CLI help failed: " + help_result.stdout + help_result.stderr)
commands = set(re.findall(r"ai_delivery_spec_cli\.py(?:\"|'|`)?\s+([a-z][a-z-]+)", README))
for command in sorted(commands):
    if command not in help_result.stdout:
        failures.append(f"README references unknown public command: {command}")

required_order = ("init-requirements", "compile-truth", "trace", "impact")
positions = [README.find(f"ai_delivery_spec_cli.py {item}") for item in required_order]
if any(item < 0 for item in positions) or positions != sorted(positions):
    failures.append("Product Truth quick path is missing or out of execution order")
if "requirements/changes/CHG-001.yaml" in README or "requirements/changes/CHG-CORE-001.yaml" not in README:
    failures.append("README change example does not match init-requirements output")
for marker in ("route-stage", "ADS:*", "resume_context", "两个本地依赖"):
    if marker not in README:
        failures.append(f"README misses progressive-disclosure marker: {marker}")

version = run("version")
if version.returncode != 0 or version.stdout.strip() != "5.4.3":
    failures.append("README public version path failed: " + version.stdout + version.stderr)

with tempfile.TemporaryDirectory(prefix="ads-readme-") as temp_name:
    temp = Path(temp_name)
    frame = temp / "problem-brief.md"
    frame.write_text("""---
artifact: problem_brief
stage: frame
schema_version: 5.4.0
document_language: zh-CN
---
<!-- ADS:problem_owner -->\n用户与负责人已确认。
<!-- ADS:pain_moment -->\n失败时刻已有证据。
<!-- ADS:success_signal -->\n成功结果可观察。
<!-- ADS:evidence_hypothesis -->\nSRC 与 ASM 已分开。
<!-- ADS:unknowns -->\n当前无开放未知项。
<!-- ADS:next_step -->\n进入 intake。
""", encoding="utf-8")
    for args in (
        ("route-stage", "--target", "clarify", "--artifact", str(frame), "--format", "json"),
        ("gate", "--profile", "frame", "--artifact", str(frame), "--format", "json"),
    ):
        result = run(*args)
        if result.returncode != 0 or "Traceback" in result.stderr:
            failures.append(f"README-stage command failed ({args[0]}): " + result.stdout + result.stderr)

    custom = temp / "custom"
    result = run("init-custom", "--output", str(custom), "--force")
    if result.returncode != 0:
        failures.append("README init-custom command failed: " + result.stdout + result.stderr)
    candidate = custom / "learning" / "candidates" / "project-local" / "CAND-EXAMPLE.yaml"
    result = run("candidate", "validate", "--input", str(candidate))
    if result.returncode != 0:
        failures.append("README fresh candidate validation failed: " + result.stdout + result.stderr)

    requirements = temp / "requirements"
    result = run("init-requirements", "--output", str(requirements), "--with-product-truth")
    if result.returncode != 0 or not (requirements / "changes" / "CHG-CORE-001.yaml").is_file():
        failures.append("README init-requirements output contract failed: " + result.stdout + result.stderr)
    if not (requirements / "truth" / "index.yaml").is_file():
        failures.append("README Product Truth index was not initialized")

if failures:
    for item in failures:
        print("FAIL: " + item)
    raise SystemExit(1)
print("PASS: README public commands resolve, first-run artifacts validate, and Product Truth steps are ordered")