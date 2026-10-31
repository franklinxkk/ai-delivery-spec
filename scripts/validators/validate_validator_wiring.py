#!/usr/bin/env python3
"""Validate that every scripts/validators/*.py is wired or explicitly documented as manual.

Follow local imports and script invocations transitively from gate/CLI and
documented manual entries. Comments and uncalled helpers are not connections.
This is static wiring evidence, not proof that any branch has executed.
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


def _local_file(root: Path, caller: Path, value: str) -> Path | None:
    """Resolve only repository-local Python paths using actual file locations."""
    if not value.endswith(".py") or "\n" in value:
        return None
    relative = Path(value.replace("\\", "/"))
    for base in (caller.parent, root, root / "scripts", root / "scripts/validators"):
        candidate = (base / relative).resolve()
        if candidate.is_relative_to(root.resolve()) and candidate.is_file():
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
    result = set()
    for base in bases:
        target = base.joinpath(*parts)
        for candidate in (target.with_suffix(".py"), target / "__init__.py"):
            candidate = candidate.resolve()
            if candidate.is_relative_to(root.resolve()) and candidate.is_file():
                result.add(candidate)
    return result


def _scope_nodes(node: ast.AST):
    """Do not confuse same-named local command variables across functions."""
    yield node
    for child in ast.iter_child_nodes(node):
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            yield from _scope_nodes(child)


def dependencies(root: Path, caller: Path) -> set[Path]:
    tree = ast.parse(caller.read_text(encoding="utf-8-sig"), filename=str(caller))
    result: set[Path] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.update(_module_files(root, caller, alias.name))
        elif isinstance(node, ast.ImportFrom):
            result.update(_module_files(root, caller, node.module or "", node.level))
            for alias in node.names:
                if alias.name != "*":
                    module = ".".join(part for part in (node.module, alias.name) if part)
                    result.update(_module_files(root, caller, module, node.level))

    # Script launch helpers and subprocess calls may consume an inline path,
    # a local command list, or the iteration variable for a list of commands.
    scopes = [tree, *(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))]
    for scope in scopes:
        nodes = list(_scope_nodes(scope))
        bindings: dict[str, list[ast.AST]] = {}
        for node in nodes:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and node.value is not None:
                        bindings.setdefault(target.id, []).append(node.value)
            elif isinstance(node, (ast.For, ast.AsyncFor)) and isinstance(node.target, ast.Name):
                bindings.setdefault(node.target.id, []).append(node.iter)

        def strings(node: ast.AST, seen: frozenset[str] = frozenset()):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                yield node.value
            elif isinstance(node, ast.Name):
                if node.id not in seen:
                    for value in bindings.get(node.id, []):
                        yield from strings(value, seen | {node.id})
            else:
                for child in ast.iter_child_nodes(node):
                    yield from strings(child, seen)

        for node in nodes:
            if not isinstance(node, ast.Call):
                continue
            function = ast.unparse(node.func)
            if function not in {"run_script", "run_sidecar_validator", "subprocess.run", "subprocess.call", "subprocess.Popen", "subprocess.check_call", "subprocess.check_output"}:
                continue
            for argument in [*node.args, *(keyword.value for keyword in node.keywords)]:
                for value in strings(argument):
                    target = _local_file(root, caller, value)
                    if target:
                        result.add(target)
    return result


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
    pending = [path.resolve() for path in callers if path.is_file()] + list(manual)
    reachable: set[Path] = set()
    while pending:
        path = pending.pop()
        if path in reachable:
            continue
        reachable.add(path)
        pending.extend(dependencies(root, path) - reachable)
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
