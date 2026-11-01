"""Small standard-library CLI helpers; no business decisions or dependencies."""
from __future__ import annotations
import os
from pathlib import Path
import shlex
import sys


def shell_command(parts) -> str:
    values = [str(value) for value in parts]
    if os.name == "nt":
        return "& " + " ".join("'" + value.replace("'", "''") + "'" for value in values)
    return shlex.join(values)


def dependency_message(missing: str, english: bool = False) -> str:
    command = shell_command([sys.executable, "-m", "pip", "install", "-r", Path(__file__).resolve().parent / "requirements.txt"])
    return (f"Missing runtime dependency {missing}. Run: " if english else f"缺少运行依赖 {missing}。请在当前解释器安装：") + command


def input_error_detail(exc, line_offset: int = 0) -> str:
    mark = getattr(exc, "problem_mark", None)
    if mark:
        return f"YAML syntax: line {mark.line + 1 + line_offset}, column {mark.column + 1}"
    return str(exc)


def run_cli(main) -> int:
    try:
        return main()
    except Exception as exc:
        # Do not hide implementation defects behind an input diagnosis.
        if not isinstance(exc, (OSError, UnicodeError, ValueError)) and not type(exc).__module__.startswith("yaml"):
            raise
        inputs = " ".join(sys.argv[1:])
        english = "en-US" in sys.argv
        label = "Input could not be read/validated" if english else "输入无法读取或校验"
        next_step = "Check the named path, UTF-8 encoding and syntax, then rerun; no output was accepted." if english else "检查所示路径、UTF-8 编码及语法后重跑；本次未形成有效产物。"
        detail = input_error_detail(exc)
        print(f"BLOCKED INPUT-ERROR: {label}: {inputs}\n{detail}\n{next_step}", file=sys.stderr)
        return 2
