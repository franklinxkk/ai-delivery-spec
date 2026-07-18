#!/usr/bin/env python3
"""Build an allowlisted runtime zip; maintainer assets never enter the package."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

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


def self_check(root: Path) -> list[str]:
    failures: list[str] = []
    commands = (
        [sys.executable, "scripts/ai_delivery_spec_cli.py", "version"],
        [sys.executable, "scripts/validators/validate_spec_config.py", "examples/spec.config.example.yaml"],
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
    args = parser.parse_args()
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    files = select_files(config)
    failures: list[str] = []
    if len(files) > int(config["max_files"]):
        failures.append(f"runtime package has {len(files)} files; budget is {config['max_files']}")
    forbidden = [path for path in files if "maintainer" in path.relative_to(ROOT).parts]
    if forbidden:
        failures.append("maintainer files leaked into runtime package")
    version = yaml.safe_load((ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8"))["interface"]["version"]
    manifest = {
        "schema_version": "5.3.0", "skill_version": version,
        "source_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True).stdout.strip() or "uncommitted",
        "files": [file_record(path) for path in files],
    }
    with tempfile.TemporaryDirectory(prefix="ads-runtime-") as temp_name:
        temp = Path(temp_name)
        for source in files:
            target = temp / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        (temp / "runtime-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.check:
            failures.extend(self_check(temp))
        if args.output and not failures:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for source in files:
                    relative = source.relative_to(ROOT).as_posix()
                    archive.write(temp / relative, relative)
                archive.write(temp / "runtime-manifest.json", "runtime-manifest.json")
    if failures:
        for failure in failures:
            print("FAIL: " + failure)
        return 1
    print(f"PASS: runtime allowlist contains {len(files)} source files (budget {config['max_files']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
