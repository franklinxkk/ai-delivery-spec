"""Audit public README commands."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "ai_delivery_spec_cli.py"
README = (ROOT / "README.md").read_text(encoding="utf-8")
MINIMAL = ROOT / "examples" / "minimal-v5"
MINIMAL_README = (MINIMAL / "README.md").read_text(encoding="utf-8")
MINIMAL_CARD = MINIMAL / "requirement-card.md"
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

badge_match = re.search(r"version-([0-9]+\.[0-9]+\.[0-9]+)-", README)
expected_version = badge_match.group(1) if badge_match else None
version = run("version")
if not expected_version or version.returncode != 0 or version.stdout.strip() != expected_version:
    failures.append("README public version path failed: " + version.stdout + version.stderr)

public_minimal_commands = (
    "python scripts/ai_delivery_spec_cli.py triage --input examples/minimal-v5/intake.yaml",
    "python scripts/ai_delivery_spec_cli.py gate --profile prd --prd examples/minimal-v5/requirement-card.md --level auto",
)
for command in public_minimal_commands:
    if command not in MINIMAL_README:
        failures.append("minimal README misses executable command: " + command)
triage = run("triage", "--input", str(MINIMAL / "intake.yaml"))
if triage.returncode or not all(marker in triage.stdout for marker in ("ultra_light / L0", "requirement_card / bounded")):
    failures.append("minimal triage disagrees with documented route: " + triage.stdout + triage.stderr)
minimal_gate = run("gate", "--profile", "prd", "--prd", str(MINIMAL_CARD), "--level", "auto")
if minimal_gate.returncode or "PASS profile=prd" not in minimal_gate.stdout:
    failures.append("minimal public auto-level gate failed: " + minimal_gate.stdout + minimal_gate.stderr)

with tempfile.TemporaryDirectory(prefix="ads-readme-") as temp_name:
    temp = Path(temp_name)
    card_text = MINIMAL_CARD.read_text(encoding="utf-8")

    frame = temp / "problem-brief.md"
    frame.write_text("""---
artifact: problem_brief
stage: frame
document_language: zh-CN
---
<!-- ADS:problem_owner -->\n负责人已确认。
<!-- ADS:pain_moment -->\n失败时刻已有证据。
<!-- ADS:success_signal -->\n成功结果可观察。
<!-- ADS:evidence_hypothesis -->\n来源与假设已分开。
<!-- ADS:unknowns -->\n当前无开放未知项。
<!-- ADS:next_step -->\n进入澄清。
""", encoding="utf-8")
    routed = run("route-stage", "--target", "clarify", "--artifact", str(frame), "--format", "json")
    if routed.returncode or "Traceback" in routed.stderr:
        failures.append("README route-stage command failed clean execution")
    framed = run("gate", "--profile", "frame", "--artifact", str(frame), "--format", "json")
    if framed.returncode or '"status": "PASS"' not in framed.stdout:
        failures.append("README frame gate failed: " + framed.stdout + framed.stderr)

    def reject(name: str, text: str, code: str) -> None:
        candidate = temp / f"{name}.md"
        candidate.write_text(text, encoding="utf-8")
        result = run("gate", "--profile", "prd", "--prd", str(candidate), "--level", "auto")
        if result.returncode == 0 or code not in result.stdout + result.stderr:
            failures.append(f"minimal badcase did not fail closed ({name}/{code}): " + result.stdout + result.stderr)

    reject("level-drift", card_text.replace("delivery_level: L0", "delivery_level: L1", 1), "PRD-L1-SECTION-MISSING")
    reject("open-p0", card_text.replace("open_p0_unknown_ids: []", "open_p0_unknown_ids: [UNK-MINIMAL-OPEN-001]", 1), "PRD-P0-UNKNOWN-NOT-STRUCTURED")
    reject("placeholder", card_text.replace("无未决项。", "待补充。", 1), "PRD-UNDECLARED-UNKNOWN")
    reject("no-frontmatter", card_text.replace("---\n", "", 1), "PRD-NO-FRONTMATTER")
    missing = run("gate", "--profile", "prd", "--prd", str(temp / "missing.md"), "--level", "auto")
    if missing.returncode == 0:
        failures.append("minimal missing-file badcase did not fail closed")

    requirements = temp / "requirements"
    initialized = run("init-requirements", "--output", str(requirements), "--with-product-truth")
    truth_index = requirements / "truth" / "index.yaml"
    if initialized.returncode or not truth_index.is_file():
        failures.append("Product Truth scaffold initialization failed")
    compiled = run("compile-truth", "--index", str(truth_index))
    if compiled.returncode == 0 or "Traceback" in compiled.stdout + compiled.stderr:
        failures.append("placeholder Product Truth did not fail cleanly before compilation")
    for name, content in (("missing", None), ("invalid-yaml", "items: ["), ("non-object", "- item\n")):
        truth = temp / f"{name}.yaml"
        if content is not None:
            truth.write_text(content, encoding="utf-8")
        traced = run("trace", "--truth", str(truth), "--output", str(temp / f"{name}-trace.yaml"))
        output = traced.stdout + traced.stderr
        if traced.returncode != 2 or "BLOCKED:" not in output or "Traceback" in output:
            failures.append(f"trace input did not fail cleanly ({name}): " + output)

if failures:
    for item in failures:
        print("FAIL: " + item)
    raise SystemExit(1)
print("PASS: public quickstarts execute; minimal and Product Truth badcases fail cleanly")
