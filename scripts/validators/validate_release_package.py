#!/usr/bin/env python3
"""Validate that hardcoded relative paths in CLI/scripts resolve inside the release package.

Scans scripts/ai_delivery_spec_cli.py and scripts/quality_gate.py for string
literals and ``ROOT / "..."`` join chains under known top-level prefixes
(maintainer/ scripts/ references/ schemas/ examples/ agents/) and checks each
against the package. maintainer/ references are maintainer-only optional
dependencies: the CLI degrades gracefully when the directory is absent, so
they are exempted and reported as INFO instead of FAIL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCAN_TARGETS = ("scripts/ai_delivery_spec_cli.py", "scripts/quality_gate.py")
PATH_PREFIXES = ("maintainer", "scripts", "references", "schemas", "examples", "agents")
# maintainer/ 为维护者专属可选依赖：运行包不含该目录，CLI 已做优雅降级，故豁免。
MAINTAINER_ONLY_TOPLEVEL = {"maintainer"}

LITERAL = re.compile(
    r"""["']((?:maintainer|scripts|references|schemas|examples|agents)/[^"'\s]+?)["']"""
)
JOIN_CHAIN = re.compile(r"""ROOT\s*(?:/\s*"([^"]+)")+""")


def _join_chain_literals(source: str) -> list[str]:
    paths = []
    for match in re.finditer(r"ROOT((?:\s*/\s*\"[^\"]+\")+)", source):
        segments = re.findall(r'"([^"]+)"', match.group(1))
        if segments and segments[0] in PATH_PREFIXES:
            paths.append("/".join(segments))
    return paths


def collect_paths(target: Path) -> list[tuple[str, str]]:
    """Return (literal_path, source_name) pairs found in one script."""
    source = target.read_text(encoding="utf-8")
    found = [(match.group(1), target.name) for match in LITERAL.finditer(source)]
    found += [(path, target.name) for path in _join_chain_literals(source)]
    return found


def validate(root: Path = ROOT) -> tuple[list[str], list[str]]:
    """Return (failures, maintainer_only_infos) for quality_gate integration."""
    failures: list[str] = []
    infos: list[str] = []
    seen: set[str] = set()
    for relative in SCAN_TARGETS:
        target = root / relative
        if not target.is_file():
            failures.append(f"scan target missing from package: {relative}")
            continue
        for path, source_name in collect_paths(target):
            if path in seen:
                continue
            seen.add(path)
            if path.split("/", 1)[0] in MAINTAINER_ONLY_TOPLEVEL:
                infos.append(f"{path} ({source_name}: maintainer-only 可选依赖，已豁免)")
                continue
            if not (root / path).exists():
                failures.append(f"{source_name} 引用的路径在发布包内不存在: {path}")
    return failures, infos


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT, help="发布包根目录，默认为本仓库根")
    args = parser.parse_args()
    root = args.root.resolve()
    failures, infos = validate(root)
    for item in infos:
        print(f"INFO: {item}")
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: release package paths resolve ({len(infos)} maintainer-only references exempted)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
