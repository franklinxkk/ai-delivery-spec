#!/usr/bin/env python3
"""Build an allowlisted runtime zip; maintainer assets never enter the package."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import shutil
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "maintainer" / "runtime-package.yaml"


def matched(relative: str, patterns: list[str]) -> bool:
    normalized = relative.replace("\\", "/")
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def select_files(config: dict) -> list[Path]:
    include = list(config["include"])
    exclude = list(config.get("exclude", []))
    selected = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if matched(relative, include) and not matched(relative, exclude):
            selected.append(path)
    return sorted(selected, key=lambda item: item.relative_to(ROOT).as_posix())


def file_record(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def source_revision() -> tuple[str, bool]:
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True,
        )
        if revision.returncode or not revision.stdout.strip():
            return "uncommitted-dirty", True
        commit = revision.stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True,
        )
    except OSError:
        return "uncommitted-dirty", True
    dirty = status.returncode != 0 or bool(status.stdout.strip())
    return (f"{commit}-dirty" if dirty else commit), dirty


def release_source_failures(source_commit: str, source_worktree_dirty: bool) -> list[str]:
    """Reject release artifacts that cannot be traced to one clean Git commit."""
    failures: list[str] = []
    if source_worktree_dirty:
        failures.append(
            "release package requires a clean Git worktree; commit the intended files and rebuild"
        )
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", source_commit):
        failures.append("release package source_commit must be one full clean Git SHA")
    return failures


def runtime_link_failures(root: Path) -> list[str]:
    """Check local Markdown destinations in the staged package, not the source tree.

    Maintenance-only evidence can exist in the checkout while being unavailable to
    installed users. Code examples and external URLs are not distribution links.
    This checks file presence; it does not claim to verify remote URLs or headings.
    """
    failures: list[str] = []
    root = root.resolve()
    for source in sorted(root.rglob("*.md")):
        raw = source.read_text(encoding="utf-8")
        raw = re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", raw)
        raw = re.sub(r"`[^`\n]+`", "", raw)
        links = re.findall(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", raw)
        links += re.findall(r"(?m)^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", raw)
        for link in links:
            destination = link[1:-1] if link.startswith("<") else link
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (source.parent / unquote(parsed.path)).resolve()
            if not target.is_relative_to(root) or not target.exists():
                failures.append(f"{source.relative_to(root).as_posix()}: runtime link target missing from package: {destination}")
    return failures


def self_check(root: Path) -> list[str]:
    failures: list[str] = []
    commands = (
        [sys.executable, "scripts/ai_delivery_spec_cli.py", "version"],
        [sys.executable, "scripts/validators/validate_spec_config.py", "examples/spec.config.example.yaml"],
        [sys.executable, "scripts/ai_delivery_spec_cli.py", "gate", "--profile", "prd", "--prd", "examples/minimal-v5/requirement-card.md", "--level", "auto"],
    )
    clean_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    for command in commands:
        result = subprocess.run(command, cwd=root, text=True, encoding="utf-8", capture_output=True, env=clean_env)
        if result.returncode:
            failures.append(" ".join(command[1:]) + ": " + result.stdout + result.stderr)
    prototype = root / "package-self-check.html"
    prototype.write_text(
        """<!doctype html><main data-testid=\"page-VIEW-CHECK\" data-state=\"ready\"><button data-action=\"ACT-CHECK\">check</button></main><script>const actionHandlers={'ACT-CHECK':()=>document.querySelector('main').setAttribute('data-state','done')};document.addEventListener('click',e=>{const action=e.target.closest('[data-action]')?.dataset.action;if(action)actionHandlers[action]?.();});</script>""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "scripts/quality_gate.py", "--profile", "prototype", "--prototype", prototype.name, "--level", "L2", "--format", "json"],
        cwd=root, text=True, encoding="utf-8", capture_output=True,
        env=clean_env,
    )
    prototype.unlink(missing_ok=True)
    if result.returncode not in {0, 1}:  # explicit-state GAP is acceptable for this minimal package smoke test
        failures.append("runtime gate smoke test: " + result.stdout + result.stderr)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="target zip; omitted for check-only")
    parser.add_argument("--check", action="store_true", help="validate selection and extracted runtime")
    parser.add_argument(
        "--release", action="store_true",
        help="enforce clean-source release provenance and run extracted-package checks",
    )
    args = parser.parse_args()
    if args.release:
        args.check = True
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    files = select_files(config)
    failures: list[str] = []
    if len(files) > int(config["max_files"]):
        failures.append(f"runtime package has {len(files)} files; budget is {config['max_files']}")
    forbidden = [path for path in files if "maintainer" in path.relative_to(ROOT).parts]
    if forbidden:
        failures.append("maintainer files leaked into runtime package")
    unsafe = [path for path in files if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve())]
    if unsafe:
        failures.append("runtime selection contains symlinks or sources outside the package root")
    if failures:
        for failure in failures:
            print("FAIL: " + failure)
        return 1
    skill_heading = next(
        (line for line in (ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines() if line.startswith("# AI Delivery Spec ")),
        "",
    )
    version = skill_heading.removeprefix("# AI Delivery Spec ").split(" ", 1)[0]
    if not version:
        failures.append("SKILL.md does not declare a release version in its H1 heading")
    source_commit, source_worktree_dirty = source_revision()
    if args.release:
        failures.extend(release_source_failures(source_commit, source_worktree_dirty))
    manifest = {
        "schema_version": "5.3.0", "skill_version": version,
        "source_commit": source_commit,
        "source_worktree_dirty": source_worktree_dirty,
        "files": [file_record(path) for path in files],
    }
    temp = (ROOT / "build" / f"runtime-package-{os.getpid()}").resolve()
    if temp.parent != (ROOT / "build").resolve():
        raise ValueError("runtime package staging path escaped build directory")
    shutil.rmtree(temp, ignore_errors=True)
    temp.mkdir(parents=True, exist_ok=True)
    try:
        for source in files:
            target = temp / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        (temp / "runtime-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # Always check shipped links, even when callers skip executable smoke tests.
        failures.extend(runtime_link_failures(temp))
        if args.check:
            failures.extend(self_check(temp))
        if args.output and not failures:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for source in files:
                    relative = source.relative_to(ROOT).as_posix()
                    archive.write(temp / relative, relative)
                archive.write(temp / "runtime-manifest.json", "runtime-manifest.json")
    finally:
        shutil.rmtree(temp, ignore_errors=True)
        try:
            temp.parent.rmdir()
        except OSError:
            pass
    if failures:
        for failure in failures:
            print("FAIL: " + failure)
        return 1
    print(f"PASS: runtime allowlist contains {len(files)} source files (budget {config['max_files']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
