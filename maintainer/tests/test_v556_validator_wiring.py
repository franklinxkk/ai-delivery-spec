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
def run_script(script, args):
    return subprocess.run(["python", script, *args], cwd="scripts")
def run():
    commands = [["python", "scripts/validators/first.py"]]
    for command in commands:
        subprocess.run(command)
def other():
    run_script("validators/second.py", [])
run()
other()
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
two()
''')
    put(tmp_path, "scripts/validators/unused.py")
    put(tmp_path, "scripts/validators/actual.py")
    assert find_orphans(tmp_path) == ["unused.py"]


def test_release_tree_wiring_has_no_orphans():
    assert find_orphans(ROOT) == []


def test_only_called_functions_and_reachable_local_imports_connect(tmp_path):
    put(tmp_path, "scripts/quality_gate.py", """from workflow import dispatch
if __name__ == "__main__":
    dispatch()
""")
    put(tmp_path, "scripts/workflow.py", """def dispatch():
    def execute():
        import live
    def abandoned():
        import dead_nested
    execute()
def obsolete():
    import dead_helper
if __name__ == "__main__":
    import dead_main
""")
    for name in ("live", "dead_helper", "dead_nested", "dead_main"):
        put(tmp_path, f"scripts/validators/{name}.py")
    assert find_orphans(tmp_path) == ["dead_helper.py", "dead_main.py", "dead_nested.py"]


def test_registered_cli_handler_connects_only_executed_tool_chain(tmp_path):
    put(tmp_path, "scripts/ai_delivery_spec_cli.py", """import argparse
import subprocess
import sys
def handler(args):
    subprocess.run([sys.executable, "scripts/tool.py", "scripts/validators/data.py"])
def retired(args):
    subprocess.run([sys.executable, "scripts/validators/unused.py"])
parser = argparse.ArgumentParser()
parser.set_defaults(func=handler)
args = parser.parse_args()
args.func(args)
""")
    put(tmp_path, "scripts/tool.py", """from subprocess import run as invoke
def check():
    invoke(["python", "scripts/validators/active.py"])
if __name__ == "__main__":
    check()
""")
    for name in ("active", "data", "unused"):
        put(tmp_path, f"scripts/validators/{name}.py")
    assert find_orphans(tmp_path) == ["data.py", "unused.py"]


def test_reachable_inherited_method_runs_only_real_script_operand(tmp_path):
    put(tmp_path, "scripts/quality_gate.py", """from checker import Checks
class Gate(Checks): pass
def apply(gate: Gate):
    gate.run()
apply(Gate())
""")
    put(tmp_path, "scripts/checker.py", """import subprocess
class Checks:
    def run(self):
        launch("active.py")
        run_script("unused.py", [])
    def obsolete(self):
        launch("retired.py")
def launch(name):
    subprocess.run(["python", name], cwd="scripts/validators")
def run_script(name, args): pass
""")
    for name in ("active", "unused", "retired"):
        put(tmp_path, f"scripts/validators/{name}.py")
    assert find_orphans(tmp_path) == ["retired.py", "unused.py"]


def test_registered_handler_requires_reachable_dispatch(tmp_path):
    put(tmp_path, "scripts/ai_delivery_spec_cli.py", """import argparse
def handler(args):
    import unused
parser = argparse.ArgumentParser()
parser.set_defaults(func=handler)
def never_called():
    args = parser.parse_args()
    args.func(args)
""")
    put(tmp_path, "scripts/validators/unused.py")
    assert find_orphans(tmp_path) == ["unused.py"]
