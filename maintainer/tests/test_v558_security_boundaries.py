import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from cli_support import validation_environment


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
