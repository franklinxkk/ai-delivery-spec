"""Read-only CLI exports preserve their inputs and update independent destinations."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def installed(tmp_path):
    # A failed regression must never modify the developer's real source files.
    target = tmp_path / "skill"
    for folder in ("scripts", "references", "schemas", "examples"):
        shutil.copytree(ROOT / folder, target / folder, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(ROOT / "SKILL.md", target / "SKILL.md")
    return target


def run(installed, script, *args):
    return subprocess.run([sys.executable, "-B", str(installed / "scripts" / script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf8")


def verify_export(installed, args, inputs, separate, expected_key):
    cli = "ai_delivery_spec_cli.py"
    for source in inputs:
        original = source.read_bytes()
        rejected = run(installed, cli, *args, "--output", source)
        assert rejected.returncode == 2 and source.read_bytes() == original
        assert "Traceback" not in rejected.stderr
        assert "output" in (rejected.stdout + rejected.stderr).lower()
    separate.write_text("previous result", encoding="utf8")
    accepted = run(installed, cli, *args, "--output", separate)
    assert accepted.returncode == 0, (accepted.stdout, accepted.stderr)
    assert expected_key in yaml.safe_load(separate.read_bytes())


def test_impact_inputs(installed, tmp_path):
    truth, change = tmp_path / "truth.yaml", tmp_path / "change.yaml"
    truth.write_text("requirements: [{id: REQ-A}]", encoding="utf8")
    change.write_text("seed_refs: [REQ-A]", encoding="utf8")
    args = ("impact", "--truth", truth, "--change", change)
    verify_export(installed, args, [truth, change], tmp_path / "impact.yaml", "affected")


def test_plan_inputs(installed, tmp_path):
    truth = tmp_path / "truth.yaml"
    truth.write_text("{}", encoding="utf8")
    config = installed / "examples/spec.config.example.yaml"
    args = ("plan-context", "--truth", truth, "--config", config)
    inputs = [truth, config, installed / "SKILL.md", installed / "references/discover.md",
              installed / "schemas/context-plan.schema.json", installed / "schemas/spec-config.schema.json"]
    verify_export(installed, args, inputs, tmp_path / "plan.yaml", "selection")


def test_query_inputs_and_verified_state_anchors(installed, tmp_path):
    truth = tmp_path / "truth.yaml"
    shutil.copyfile(ROOT / "maintainer/examples/publishing-learning-v5/delivery/truth/product-truth.yaml", truth)
    state = tmp_path / "state.yaml"
    create = run(installed, "manage_execution_state.py", "create", "--truth", truth, "--config",
                 installed / "examples/spec.config.example.yaml", "--output", state)
    assert create.returncode == 0, (create.stdout, create.stderr)
    anchors = yaml.safe_load(state.read_bytes())["anchors"]
    anchor = Path(next(item["path"] for item in anchors if item["kind"] == "product_truth"))
    args = ("query-truth", "--truth", truth, "--id", "REQ-CONTENT-PUBLISH-001", "--execution-state", state)
    verify_export(installed, args, [truth, state, anchor], tmp_path / "slice.yaml", "items")
