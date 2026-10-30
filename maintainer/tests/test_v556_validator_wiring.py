"""Static entry wiring must follow real edges without blessing name mentions."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/validators"))
from validate_validator_wiring import find_orphans


def put(root, path, text="pass\n"):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def test_transitive_gate_imports_and_local_relative_imports_are_connected(tmp_path):
    put(tmp_path, "scripts/quality_gate.py", "from gate_checks import Checks\n")
    put(tmp_path, "scripts/validators/gate_checks.py", "from validators.context import check\nclass Checks: pass\n")
    put(tmp_path, "scripts/validators/context.py", "from . import helper\ndef check(): pass\n")
    put(tmp_path, "scripts/validators/helper.py")
    assert find_orphans(tmp_path) == []


def test_documented_manual_entry_connects_its_helper_without_exemption_list(tmp_path):
    put(tmp_path, "scripts/validators/manual_check.py", "from structure import analyze\n")
    put(tmp_path, "scripts/validators/structure.py", "def analyze(): pass\n")
    put(tmp_path, "references/troubleshooting.md", "手动执行 `python scripts/validators/manual_check.py sample.md`。\n")
    assert find_orphans(tmp_path) == []


def test_real_orphans_stay_blocked_despite_comments_names_and_unreachable_imports(tmp_path):
    put(tmp_path, "scripts/quality_gate.py", '# validate_unused.py\nDOC = "validate_unused.py"\n')
    put(tmp_path, "scripts/unreachable.py", "import validate_unused\n")
    put(tmp_path, "scripts/validators/validate_unused.py")
    put(tmp_path, "references/troubleshooting.md", "已经移除 validate_unused.py。\n")
    assert find_orphans(tmp_path) == ["validate_unused.py"]


def test_similar_name_does_not_accidentally_connect_an_orphan(tmp_path):
    put(tmp_path, "scripts/quality_gate.py", "import validate_alpha_extra\n")
    put(tmp_path, "scripts/validators/validate_alpha_extra.py")
    put(tmp_path, "scripts/validators/validate_alpha.py")
    assert find_orphans(tmp_path) == ["validate_alpha.py"]


def test_subprocess_command_list_and_dispatch_helper_paths_are_connected(tmp_path):
    put(tmp_path, "scripts/ai_delivery_spec_cli.py", '''import subprocess
def run():
    commands = [["python", "scripts/validators/first.py"]]
    for command in commands:
        subprocess.run(command)
def other():
    run_script("validators/second.py", [])
''')
    put(tmp_path, "scripts/validators/first.py")
    put(tmp_path, "scripts/validators/second.py", "import common\n")
    put(tmp_path, "scripts/validators/common.py")
    assert find_orphans(tmp_path) == []


def test_same_named_unused_command_in_another_function_is_not_an_edge(tmp_path):
    put(tmp_path, "scripts/ai_delivery_spec_cli.py", '''import subprocess
def one():
    command = ["python", "scripts/validators/unused.py"]
def two():
    command = ["python", "scripts/validators/actual.py"]
    subprocess.run(command)
''')
    put(tmp_path, "scripts/validators/unused.py")
    put(tmp_path, "scripts/validators/actual.py")
    assert find_orphans(tmp_path) == ["unused.py"]


def test_release_tree_wiring_has_no_orphans():
    assert find_orphans(ROOT) == []
