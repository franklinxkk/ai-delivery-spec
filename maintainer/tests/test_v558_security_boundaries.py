import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from cli_support import validation_environment
import manage_execution_state as execution


def test_validation_child_has_utf8_but_no_caller_secret(monkeypatch):
    monkeypatch.setenv("UNRELATED_PROJECT_SECRET", "test-marker")
    monkeypatch.setenv("NODE_OPTIONS", "test-marker")
    proc = subprocess.run(
        [sys.executable, "-c", "import os; print(os.environ['PYTHONIOENCODING'],"
         "'UNRELATED_PROJECT_SECRET' in os.environ, 'NODE_OPTIONS' in os.environ)"],
        env=validation_environment(), capture_output=True, text=True, check=True)
    assert proc.stdout.strip() == "utf-8 False False"


def test_ledger_output_preserves_source_and_accepts_dedicated_path(tmp_path):
    source = tmp_path / "demo.html"
    content = '<button data-action="save">保存</button>'
    source.write_text(content, encoding="utf-8")
    cmd = [sys.executable, str(ROOT / "scripts" / "extract_interaction_ledger.py"),
           "--input", str(source), "--output"]
    blocked = subprocess.run([*cmd, str(source)], capture_output=True)
    assert blocked.returncode == 2 and source.read_text("utf-8") == content
    destination = tmp_path / "ledger.json"
    subprocess.run([*cmd, str(destination)], capture_output=True, check=True)
    assert {"type": "data-action", "name": "save"} in json.loads(destination.read_text("utf-8"))["actions"]


def hardlink(alias, source):
    try:
        alias.hardlink_to(source)
    except (PermissionError, NotImplementedError):
        pytest.skip("Hard-link creation unavailable")


def test_ledger_refuses_source_hardlink(tmp_path):
    source = tmp_path / "demo.html"
    content = '<button data-action="save">保存</button>'
    source.write_text(content, encoding="utf-8")
    alias = tmp_path / "alias.html"
    hardlink(alias, source)
    blocked = subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_interaction_ledger.py"),
                              "--input", str(source), "--output", str(alias)], capture_output=True)
    assert blocked.returncode == 2
    assert alias.samefile(source) and source.read_text("utf-8") == content


def test_equal_revision_checkpoints_keep_their_own_anchors(tmp_path, monkeypatch):
    original = ROOT / "maintainer/examples/publishing-learning-v5/delivery/truth/product-truth.yaml"
    changed = tmp_path / "truth.yaml"
    value = yaml.safe_load(original.read_text("utf-8"))
    value["product"]["outcome"] += " (second checkpoint)"
    changed.write_text(yaml.safe_dump(value), encoding="utf-8")
    monkeypatch.setattr(execution, "repository_fingerprint", lambda: ("a" * 64, False))

    def run(*args):
        monkeypatch.setattr(sys, "argv", ["manage_execution_state.py", *map(str, args)])
        assert execution.main() == 0

    states = [tmp_path / name for name in ("first.yaml", "second.yaml", "retry.yaml")]
    for source, state in zip((original, changed, original), states):
        run("create", "--truth", source, "--config", ROOT / "examples/spec.config.example.yaml", "--output", state)
    for state in states:
        run("verify", "--state", state)
    anchors = [execution.load(state)["anchors"][0] for state in states]
    assert anchors[0] == anchors[2]
    assert anchors[0]["path"] != anchors[1]["path"]

    # Existing checkpoints reference their original absolute path and digest.
    legacy = Path(anchors[0]["path"]).with_name("000-product-truth.yaml")
    legacy.write_bytes(original.read_bytes())
    state = execution.load(states[0])
    state["anchors"][0]["path"] = str(legacy)
    state["state_hash"] = execution.object_hash(state, "state_hash")
    execution.dump(states[0], state)
    run("verify", "--state", states[0])


def test_snapshot_refuses_to_reuse_linked_target(tmp_path):
    source = tmp_path / "source.yaml"
    source.write_text("ok: true\n", encoding="utf-8")
    output = tmp_path / "checkpoint.yaml"
    target = execution.snapshot(source, output)
    target.unlink()
    hardlink(target, source)
    with pytest.raises(execution.SnapshotError, match="cannot be reused"):
        execution.snapshot(source, output)
    assert target.samefile(source) and source.read_text("utf-8") == "ok: true\n"


def test_snapshot_refuses_to_overwrite_changed_target(tmp_path):
    source = tmp_path / "source.yaml"
    source.write_text("ok: true\n", encoding="utf-8")
    output = tmp_path / "checkpoint.yaml"
    target = execution.snapshot(source, output)
    target.write_text("ok: false\n", encoding="utf-8")
    with pytest.raises(execution.SnapshotError, match="cannot be reused"):
        execution.snapshot(source, output)
    assert target.read_text("utf-8") == "ok: false\n"


def test_snapshot_refuses_linked_directory(tmp_path):
    source = tmp_path / "source.yaml"
    source.write_text("ok: true\n", encoding="utf-8")
    destination = tmp_path / "separate"
    destination.mkdir()
    link = tmp_path / "snapshots"
    if sys.platform == "win32":
        result = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(link), str(destination)], capture_output=True)
        if result.returncode:
            pytest.skip("Windows junction creation unavailable")
    else:
        link.symlink_to(destination, target_is_directory=True)
    with pytest.raises(execution.SnapshotError, match="must be a real directory"):
        execution.snapshot(source, tmp_path / "checkpoint.yaml")
    assert list(destination.iterdir()) == []
