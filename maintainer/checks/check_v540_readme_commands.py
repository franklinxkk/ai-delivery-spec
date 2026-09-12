"""Execute the public quickstart and controlled bad-input paths."""
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[2]


def run(*args):
    return subprocess.run([sys.executable, "scripts/ai_delivery_spec_cli.py", *args], cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def main():
    failures = []
    version = run("version")
    expected = re.search(r"^# AI Delivery Spec (\d+\.\d+\.\d+)", (ROOT / "SKILL.md").read_text(encoding="utf-8"), re.M).group(1)
    if version.returncode or version.stdout.strip() != expected:
        failures.append("public version command failed")
    result = run("triage", "--input", "examples/minimal-v5/intake.yaml", "--format", "json")
    if result.returncode or json.loads(result.stdout).get("lifecycle_mutated") is not False:
        failures.append("public triage command failed or mutated lifecycle")
    result = run("gate", "--profile", "prd", "--prd", "examples/minimal-v5/requirement-card.md", "--stage", "specify", "--format", "json")
    if result.returncode or json.loads(result.stdout)["status"] != "PASS":
        failures.append("public PRD quickstart failed: " + result.stdout + result.stderr)
    with tempfile.TemporaryDirectory(prefix="ads-readme-") as temp:
        path = Path(temp) / "bad.yaml"
        for raw in ("items: [", "- list", "artifact_mode: [prd]\ntitle: sample"):
            path.write_text(raw, encoding="utf-8")
            result = run("triage", "--input", str(path), "--format", "json")
            if result.returncode != 2 or "Traceback" in result.stdout + result.stderr:
                failures.append("triage bad input was not rejected cleanly")
        result = run("gate", "--profile", "prd", "--prd", str(Path(temp) / "missing.md"), "--format", "json")
        if result.returncode != 2:
            failures.append("missing PRD was not rejected")
    for failure in failures:
        print("FAIL: " + failure)
    if not failures:
        print("PASS: public version/triage/PRD commands execute; invalid input is rejected cleanly")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
