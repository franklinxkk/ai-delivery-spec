"""Compiled truth and trace reports must preserve the source package selected by the user."""

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "references/templates"


@pytest.fixture
def truth_index(tmp_path):
    directory = tmp_path / "truth"
    fragments = directory / "fragments"
    fragments.mkdir(parents=True)
    for name, target in (
        ("index", directory / "index.yaml"),
        ("core-fragment", fragments / "00-core.yaml"),
        ("module-fragment", fragments / "MOD-EXAMPLE.yaml"),
    ):
        shutil.copyfile(TEMPLATES / f"product-truth-{name}-template.yaml", target)
    return directory / "index.yaml"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/ai_delivery_spec_cli.py"), *map(str, args)],
        capture_output=True, encoding="utf-8",
    )


def update_yaml(path, update):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    update(data)
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_template_compiles_refreshes_and_exports_to_user_chosen_location(truth_index, tmp_path):
    update_yaml(truth_index, lambda doc: doc["fragments"][0].update(path="fragments/../fragments/00-core.yaml"))
    default = truth_index.parent / "compiled/product-truth.yaml"
    for product_name in ("First draft", "Confirmed product"):
        core = truth_index.parent / "fragments/00-core.yaml"
        update_yaml(core, lambda doc: doc["content"]["product"].update(name=product_name))
        result = run_cli("compile-truth", "--index", truth_index, "--allow-incomplete")
        assert result.returncode == 0, result.stdout + result.stderr
        assert yaml.safe_load(default.read_text(encoding="utf-8"))["product"]["name"] == product_name
    explicit = tmp_path / "handoff/truth.yaml"
    result = run_cli("compile-truth", "--index", truth_index, "--allow-incomplete", "--output", explicit)
    assert result.returncode == 0 and explicit.read_bytes() == default.read_bytes()
    ledger = tmp_path / "handoff/trace.yaml"
    result = run_cli("trace", "--truth", truth_index, "--output", ledger)
    assert result.returncode == 0, result.stdout + result.stderr
    assert yaml.safe_load(ledger.read_text(encoding="utf-8"))["ledger_id"]


@pytest.mark.parametrize("source", ("index.yaml", "fragments/00-core.yaml"))
@pytest.mark.parametrize("mode", ("compile", "default", "trace"))
def test_outputs_preserve_index_and_fragments(truth_index, source, mode):
    target = truth_index.parent / source
    if mode == "default":
        update_yaml(truth_index, lambda doc: doc.update(compiled_output=source))
    args = ["compile-truth", "--index", truth_index, "--allow-incomplete"]
    if mode == "compile":
        args += ["--output", target]
    if mode == "trace":
        args = ["trace", "--truth", truth_index, "--output", target]
    before = target.read_bytes()
    result = run_cli(*args)
    assert result.returncode and "output must differ" in result.stdout + result.stderr
    assert target.read_bytes() == before


@pytest.mark.parametrize("field", ("compiled_output", "fragment"))
def test_index_paths_stay_in_truth_workspace(truth_index, tmp_path, field):
    if field == "fragment":
        update_yaml(truth_index, lambda doc: doc["fragments"][0].update(path="../outside.yaml"))
    else:
        update_yaml(truth_index, lambda doc: doc.update(compiled_output="../outside.yaml"))
    result = run_cli("compile-truth", "--index", truth_index, "--allow-incomplete")
    assert result.returncode and "within the Product Truth index directory" in result.stdout + result.stderr
    assert not (tmp_path / "outside.yaml").exists()


def test_index_cannot_designate_an_existing_unrelated_file(truth_index):
    notes = truth_index.parent / "notes.md"
    notes.write_bytes(b"Project notes.")
    update_yaml(truth_index, lambda doc: doc.update(compiled_output="notes.md"))
    result = run_cli("compile-truth", "--index", truth_index, "--allow-incomplete")
    assert result.returncode and "existing index-declared output" in result.stdout
    assert notes.read_bytes() == b"Project notes."


def test_trace_preserves_source_file_identity(tmp_path):
    truth = tmp_path / "product-truth.yaml"
    truth.write_bytes(b"truth_id: TRUTH-EXAMPLE\n")
    alias = tmp_path / "ledger.yaml"
    try:
        os.link(truth, alias)
    except (PermissionError, NotImplementedError):
        pytest.skip("this filesystem cannot create a hard link")
    result = run_cli("trace", "--truth", truth, "--output", alias)
    assert result.returncode and "output must differ" in result.stdout
    assert truth.read_bytes() == b"truth_id: TRUTH-EXAMPLE\n"
