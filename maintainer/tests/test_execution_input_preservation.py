import json
from pathlib import Path
import shutil
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import manage_execution_state as execution


@pytest.fixture
def project(tmp_path, monkeypatch):
    contract = tmp_path / "discovery.yaml"
    config = tmp_path / "config.yaml"
    shutil.copyfile(ROOT / "maintainer/examples/discovery-contract-example.yaml", contract)
    shutil.copyfile(ROOT / "examples/spec.config.example.yaml", config)
    monkeypatch.setattr(execution, "repository_fingerprint", lambda: ("a" * 64, False))

    def run(*args):
        monkeypatch.setattr(sys, "argv", ["manage_execution_state.py", *map(str, args)])
        return execution.main()

    return run, contract, config


def test_create_rejects_collisions_before_writing_snapshots(project, tmp_path):
    run, contract, config = project
    source_bytes = contract.read_bytes(), config.read_bytes()
    args = ["create", "--discovery-contract", contract, "--config", config]
    for output in (contract, config):
        assert run(*args, "--output", output) == 1
    assert (contract.read_bytes(), config.read_bytes()) == source_bytes
    assert not (tmp_path / "snapshots").exists()


def test_create_preserves_hardlinked_input(project, tmp_path):
    run, contract, config = project
    original = contract.read_bytes()
    alias = tmp_path / "second-name.yaml"
    try:
        alias.hardlink_to(contract)
    except (PermissionError, NotImplementedError):
        pytest.skip("this filesystem cannot create a hard link")
    assert run("create", "--discovery-contract", contract, "--config", config, "--output", alias) == 1
    assert alias.samefile(contract)
    assert alias.read_bytes() == original
    assert not (tmp_path / "snapshots").exists()


def test_state_updates_keep_inputs_and_allow_existing_state_output(project, tmp_path):
    run, contract, config = project
    state = tmp_path / "state.json"
    state.write_text("previous explicit output", encoding="utf-8")
    create = ["create", "--discovery-contract", contract, "--config", config]
    assert run(*create, "--output", state) == 0
    before = state.read_bytes()
    anchors = {Path(a["path"]): Path(a["path"]).read_bytes() for a in json.loads(before)["anchors"]}
    old_snapshot = next(iter(anchors))
    assert run(*create, "--output", old_snapshot) == 1
    assert not (old_snapshot.parent / "snapshots").exists()
    assert run("gate", "--state", state, "--gate-id", "version_environment", "--output", state) == 1
    assert run("gate", "--state", state, "--gate-id", "version_environment", "--projection", contract,
               "--output", contract) == 1
    receipt = tmp_path / "gate.json"
    assert run("gate", "--state", state, "--gate-id", "version_environment", "--output", receipt) == 0
    original_receipt = receipt.read_bytes()
    assert run("advance", "--state", state, "--to", "clarify", "--gate-result", receipt, "--output", receipt) == 1
    assert receipt.read_bytes() == original_receipt
    assert run("record-turn", "--state", state, "--output", old_snapshot) == 1
    checkpoint = ["checkpoint", "--state", state, "--discovery-contract", contract]
    assert run(*checkpoint, "--output", contract) == 1
    assert state.read_bytes() == before
    assert all(path.read_bytes() == original for path, original in anchors.items())
    assert run(*checkpoint, "--output", state) == 0
    assert run("record-turn", "--state", state, "--output", state) == 0
    assert run("verify", "--state", state) == 0
