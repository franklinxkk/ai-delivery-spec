#!/usr/bin/env python3
"""Validate that every scripts/validators/*.py is wired or explicitly documented as manual.

Follow local imports, direct calls, argparse handlers and Python commands
from gate/CLI and documented manual entries. Nonconstant branches represent
possible paths. Dynamic dispatch and arbitrary Python data flow are outside
this static check; execution and validation outcomes require separate tests.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC_FILES = lambda root: [root / "README.md", *sorted((root / "references").glob("*.md"))]
MANUAL_MARKERS = ("手动执行", "未纳入 gate", "未纳入gate", "manual execution", "run manually")


def _local_file(root: Path, base: Path, value: str) -> Path | None:
    """Only the launched script operand, resolved against the dispatcher's directory."""
    if not value.endswith(".py") or "\n" in value:
        return None
    relative = Path(value.replace("\\", "/"))
    candidate = (base / relative).resolve()
    if candidate.is_relative_to(root) and candidate.is_file():
        return candidate
    return None


def _module_files(root: Path, caller: Path, module: str, level: int = 0) -> set[Path]:
    parts = module.split(".") if module else []
    if level:
        base = caller.parent
        for _ in range(level - 1):
            base = base.parent
        bases = (base,)
    else:
        bases = (caller.parent, root / "scripts", root / "scripts/validators", root)
    for base in bases:
        target = base.joinpath(*parts)
        for candidate in (target / "__init__.py", target.with_suffix(".py")):
            candidate = candidate.resolve()
            if candidate.is_relative_to(root.resolve()) and candidate.is_file():
                return {candidate}
    return set()


DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
PROCESS_CALLS = {f"subprocess.{name}" for name in ("run", "call", "Popen", "check_call", "check_output")}


def _executed_nodes(node: ast.AST, entry: bool):
    """Yield statements in this scope without entering bodies of its declarations."""
    yield node
    if isinstance(node, DEFINITIONS):
        for decorator in node.decorator_list:
            yield from _executed_nodes(decorator, entry)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    yield from _executed_nodes(default, entry)
        return
    if isinstance(node, ast.Lambda):
        return
    if isinstance(node, ast.If):
        condition = node.test
        value = None
        if isinstance(condition, ast.Constant):
            value = bool(condition.value)
        elif isinstance(condition, ast.Compare) and len(condition.ops) == 1:
            left, right = condition.left, condition.comparators[0]
            if isinstance(right, ast.Name):
                left, right = right, left
            if isinstance(left, ast.Name) and left.id == "__name__" and isinstance(right, ast.Constant) and right.value == "__main__":
                if isinstance(condition.ops[0], (ast.Eq, ast.NotEq)):
                    value = entry == isinstance(condition.ops[0], ast.Eq)
        if value is not None:
            for statement in node.body if value else node.orelse:
                yield from _executed_nodes(statement, entry)
            return
    for child in ast.iter_child_nodes(node):
        yield from _executed_nodes(child, entry)


class Scope:
    """Lexical names from one module, class or function; build the index on demand."""

    def __init__(self, path, node, entry, parent=None):
        self.path, self.node, self.entry, self.parent = path, node, entry, parent
        self.nodes = []
        for statement in node.body:
            self.nodes.extend(_executed_nodes(statement, entry))
            if isinstance(statement, (ast.Return, ast.Raise)):
                break
        self.members = {item.name: item for item in self.nodes if isinstance(item, DEFINITIONS)}
        self.children = {}
        self.invocations = {}
        self.imports = {}
        self.values = {}
        self.iterations = {}
        self.types = {}
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
                self.types[arg.arg] = arg.annotation
        for item in self.nodes:
            if isinstance(item, ast.Import):
                for alias in item.names:
                    bound = alias.asname or alias.name.partition(".")[0]
                    self.imports[bound] = (alias.name if alias.asname else bound, "", 0)
            elif isinstance(item, ast.ImportFrom):
                for alias in item.names:
                    self.imports[alias.asname or alias.name] = (item.module or "", alias.name, item.level)
            elif isinstance(item, (ast.Assign, ast.AnnAssign)):
                targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                for target in targets:
                    if isinstance(target, ast.Name) and item.value is not None:
                        self.values.setdefault(target.id, []).append(item.value)
            elif isinstance(item, (ast.For, ast.AsyncFor)) and isinstance(item.target, ast.Name):
                self.iterations[item.target.id] = item.iter
        self.dispatches_handler = any(
            isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
            and call.func.attr == "func" and isinstance(call.func.value, ast.Name)
            and any(isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute)
                    and value.func.attr == "parse_args" for value in self.values.get(call.func.value.id, []))
            for call in self.nodes
        )

    def child(self, name):
        if name not in self.children:
            self.children[name] = Scope(self.path, self.members[name], self.entry, self)
        return self.children[name]

    def with_script_arguments(self, arguments):
        if not arguments:
            return self
        key = tuple(sorted(arguments.items()))
        if key not in self.invocations:
            called = Scope(self.path, self.node, self.entry, self.parent)
            for name, value in key:
                called.values[name] = [ast.Constant(value=value)]
            self.invocations[key] = called
        return self.invocations[key]

    def defining_scope(self, name):
        scope = self
        while scope:
            if any(name in table for table in (scope.members, scope.imports, scope.values, scope.types, scope.iterations)):
                return scope
            scope = scope.parent
        return None


class Wiring:
    def __init__(self, root):
        self.root = root
        self.modules = {}
        self.pending = []
        self.visited = set()
        self.module_paths = {}

    def module(self, path, entry=False):
        key = path, entry
        if key not in self.modules:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            self.modules[key] = Scope(path, tree, entry)
        return self.modules[key]

    def local_module(self, scope, name, level=0):
        key = scope.path.parent, name, level
        if key not in self.module_paths:
            self.module_paths[key] = _module_files(self.root, scope.path, name, level)
        return self.module_paths[key]

    def member(self, scope, name, seen):
        if name in scope.members:
            return scope.child(name)
        if isinstance(scope.node, ast.ClassDef) and scope not in seen:
            for expr in scope.node.bases:
                base = self.resolve(scope.parent, expr, seen | {scope})
                if isinstance(base, Scope):
                    member = self.member(base, name, seen | {scope})
                    if member:
                        return member
        return None

    def resolve(self, scope, expr, seen=frozenset()):
        """Resolve explicit calls, imported symbols and statically typed method receivers."""
        if isinstance(expr, ast.Attribute):
            owner = self.resolve(scope, expr.value, seen)
            if isinstance(owner, Scope):
                return self.member(owner, expr.attr, seen)
            if isinstance(owner, str):
                return owner + "." + expr.attr
        if isinstance(expr, ast.Call):
            return self.resolve(scope, expr.func, seen)
        if not isinstance(expr, ast.Name):
            return None
        name = expr.id
        owner = scope.defining_scope(name)
        if not owner or (owner, name) in seen:
            return None
        seen = seen | {(owner, name)}
        if name in owner.members:
            return owner.child(name)
        if name in owner.imports:
            module, symbol, level = owner.imports[name]
            full = ".".join(filter(None, (module, symbol)))
            if symbol:
                for path in self.local_module(owner, module, level):
                    member = self.member(self.module(path), symbol, seen)
                    if member:
                        return member
            for path in self.local_module(owner, full, level):
                return self.module(path)
            return full if not level else None
        if name in owner.types:
            if name in {"self", "cls"} and owner.parent and isinstance(owner.parent.node, ast.ClassDef):
                return owner.parent
            return self.resolve(owner, owner.types[name], seen)
        for value in owner.values.get(name, []):
            result = self.resolve(owner, value, seen)
            if result:
                return result
        return None

    def command_values(self, scope, expr, iterating=False, seen=frozenset()):
        """Follow command lists, concatenation and the for-loop element consumed by subprocess."""
        if isinstance(expr, ast.Name):
            owner = scope.defining_scope(expr.id)
            if not owner or (owner, expr.id) in seen:
                return
            seen = seen | {(owner, expr.id)}
            for value in owner.values.get(expr.id, []):
                yield from self.command_values(owner, value, iterating, seen)
            if expr.id in owner.iterations:
                yield from self.command_values(owner, owner.iterations[expr.id], True, seen)
        elif isinstance(expr, ast.IfExp):
            for branch in (expr.body, expr.orelse):
                yield from self.command_values(scope, branch, iterating, seen)
        elif iterating and isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
            for side in (expr.left, expr.right):
                yield from self.command_values(scope, side, True, seen)
        elif iterating and isinstance(expr, (ast.List, ast.Tuple)):
            for element in expr.elts:
                yield from self.command_values(scope, element, False, seen)
        elif not iterating and isinstance(expr, (ast.List, ast.Tuple)):
            yield expr.elts

    def path_value(self, scope, expr, seen=frozenset()):
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            return expr.value
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id in {"Path", "str"} and len(expr.args) == 1:
            return self.path_value(scope, expr.args[0], seen)
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
            left = self.path_value(scope, expr.left, seen)
            right = self.path_value(scope, expr.right, seen)
            if left is not None and right is not None:
                return str(Path(left) / right)
        if isinstance(expr, ast.Name) and expr.id not in seen:
            owner = scope.defining_scope(expr.id)
            if owner and len(owner.values.get(expr.id, [])) == 1:
                return self.path_value(owner, owner.values[expr.id][0], seen | {expr.id})
            if expr.id == "__file__":
                return str(scope.path)
        if isinstance(expr, ast.Attribute) and expr.attr == "parent":
            path = self.path_value(scope, expr.value, seen)
            if path:
                return str(Path(path).parent)
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "resolve":
            path = self.path_value(scope, expr.func.value, seen)
            if path:
                return str((self.root / path).resolve())
        if isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Attribute) and expr.value.attr == "parents":
            path = self.path_value(scope, expr.value.value, seen)
            index = expr.slice
            if path and isinstance(index, ast.Constant) and type(index.value) is int and 0 <= index.value < len(Path(path).parents):
                return str(Path(path).parents[index.value])
        return None

    def launch(self, scope, expr, base):
        value = self.path_value(scope, expr)
        if value and (base or Path(value).is_absolute()):
            path = _local_file(self.root, base or self.root, value)
            if path:
                self.pending.append(self.module(path, entry=True))

    def call(self, scope, node):
        target = self.resolve(scope, node.func)
        if isinstance(target, Scope):
            if isinstance(target.node, ast.ClassDef):
                constructor = self.member(target, "__init__", set())
                if constructor:
                    self.pending.append(constructor)
            elif isinstance(target.node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Forward literal script operands into local dispatchers. A helper's
                # name alone says nothing about whether it actually launches a tool.
                parameters = [arg.arg for arg in (*target.node.args.posonlyargs, *target.node.args.args)]
                if parameters[:1] in (["self"], ["cls"]) and isinstance(node.func, ast.Attribute):
                    parameters = parameters[1:]
                arguments = dict(zip(parameters, node.args))
                arguments.update({k.arg: k.value for k in node.keywords if k.arg})
                paths = {name: arg.value for name, arg in arguments.items()
                         if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.endswith(".py")}
                target = target.with_script_arguments(paths)
            self.pending.append(target)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "set_defaults" and scope.dispatches_handler:
            for keyword in node.keywords:
                if keyword.arg == "func":
                    callback = self.resolve(scope, keyword.value)
                    if isinstance(callback, Scope):
                        self.pending.append(callback)
        if target in PROCESS_CALLS:
            arg = node.args[0] if node.args else next((k.value for k in node.keywords if k.arg == "args"), None)
            cwd = next((k.value for k in node.keywords if k.arg == "cwd"), None)
            directory = self.path_value(scope, cwd) if cwd is not None else "."
            base = self.root / directory if directory else None
            for command in self.command_values(scope, arg):
                if not command:
                    continue
                executable = self.path_value(scope, command[0]) or ""
                python = self.resolve(scope, command[0]) == "sys.executable" or re.fullmatch(r"python(?:w|[0-9.]+)?(?:\.exe)?", Path(executable).name, re.I)
                if python and len(command) > 1:
                    self.launch(scope, command[1], base)
                elif executable.endswith(".py"):
                    self.launch(scope, command[0], base)

    def walk(self, entries):
        self.pending.extend(self.module(path, entry=True) for path in entries)
        while self.pending:
            scope = self.pending.pop()
            if scope in self.visited:
                continue
            self.visited.add(scope)
            for node in scope.nodes:
                if isinstance(node, ast.Call):
                    self.call(scope, node)
                elif isinstance(node, ast.ClassDef):
                    self.pending.append(scope.child(node.name))
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in node.names:
                        if isinstance(node, ast.Import):
                            paths = self.local_module(scope, alias.name)
                        else:
                            module = node.module or ""
                            paths = self.local_module(scope, module, node.level)
                            full = ".".join(filter(None, (module, alias.name)))
                            paths = paths | self.local_module(scope, full, node.level)
                        self.pending.extend(self.module(path) for path in paths)
        return {scope.path for scope in self.visited}


def find_orphans(root: Path = ROOT) -> list[str]:
    """Return orphan validator names; exposed for quality_gate integration."""
    validator_dir = root / "scripts" / "validators"
    callers = (
        root / "scripts" / "quality_gate.py",
        root / "scripts" / "ai_delivery_spec_cli.py",
    )
    doc_lines = [
        line
        for doc in DOC_FILES(root)
        if doc.is_file()
        for line in doc.read_text(encoding="utf-8").splitlines()
    ]
    validators = [path.resolve() for path in sorted(validator_dir.glob("*.py")) if not path.name.startswith("__")]
    manual = {path for path in validators if any(
        re.search(r"(?<![\w-])" + re.escape(path.stem) + r"(?:\.py)?(?![\w-])", line)
        and any(marker in line.casefold() for marker in MANUAL_MARKERS) for line in doc_lines)}
    entries = [path.resolve() for path in callers if path.is_file()] + list(manual)
    reachable = Wiring(root.resolve()).walk(entries)
    return [path.name for path in validators if path not in reachable]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT, help="发布包根目录，默认为本仓库根")
    args = parser.parse_args()
    root = args.root.resolve()
    orphans = find_orphans(root)
    if orphans:
        for name in orphans:
            print(f"BLOCK: 孤儿校验器未被 gate/CLI 调用，也未在文档标注手动执行: {name}")
        return 1
    print("PASS: every validator is wired into gate/CLI or explicitly marked manual")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
