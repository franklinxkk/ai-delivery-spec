#!/usr/bin/env python3
"""Keep public claims, pure-v5 scope, package hygiene, and agent entries aligned."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
VERSION = "5.1.2"
PUBLIC_FILES = (
    "README.md",
    ".github/docs/social-launch-kit.md",
    ".github/docs/awesome-submission-targets.md",
    "examples/README.md",
)
POSITIVE_ONLY_CLAIMS = (
    "production ready",
    "production-ready",
    "fully validated",
    "full lifecycle simulation",
    "生产就绪",
    "完整全生命周期模拟",
    "已全面验证",
)
NEGATION_MARKERS = (
    "not ", "do not", "cannot", "no ", "prohibited", "without", "unproven",
    "未", "不", "禁止", "不可", "不得", "没有",
)
LEGACY_RUNTIME_MARKERS = (
    "migrate-v4", "inventory-v4", "compare-v4-v5", "export-v4-view",
    "v4_input_mode", "v4 compatibility", "v4-to-v5", "v5-to-v4",
)


def text_files() -> list[Path]:
    suffixes = {".md", ".yaml", ".yml", ".json", ".py", ".txt", ".html"}
    return [
        path for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in suffixes
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and path.name != "CHANGELOG.md"
    ]


def main() -> int:
    failures: list[str] = []
    required_version_files = (
        ROOT / "SKILL.md",
        ROOT / "README.md",
        ROOT / "agents/openai.yaml",
    )
    for path in required_version_files:
        if VERSION not in path.read_text(encoding="utf-8"):
            failures.append(f"version {VERSION} missing from {path.relative_to(ROOT)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if len(readme.splitlines()) > 300:
        failures.append("README.md exceeds 300-line onboarding budget")
    for marker in ("ToC", "ToB/ToG", "Idea", "PRD"):
        if marker not in readme:
            failures.append(f"README onboarding omits audience/path marker: {marker}")
    quick_start = readme.find("## 60 秒上手")
    if quick_start < 0 or readme.find("npx skills add") < quick_start:
        failures.append("README must put install inside the first 60-second entry")
    for marker in ("Ultra-Light", "smart-large-project", "examples/minimal-v5", "分片真相", "一份统一"):
        if marker not in readme:
            failures.append(f"README misses v5.1.0 onboarding marker: {marker}")
    coverage = yaml.safe_load((ROOT / "references/domain-coverage.yaml").read_text(encoding="utf-8"))
    release_status = yaml.safe_load((ROOT / "evals/evidence/release-status.yaml").read_text(encoding="utf-8"))
    matrix = yaml.safe_load((ROOT / "evals/evidence/github-validation-matrix.yaml").read_text(encoding="utf-8"))
    if release_status.get("runtime") != "pure_v5":
        failures.append("release status does not declare pure_v5 runtime")
    if release_status.get("domain_packs", {}).get("count") != len(coverage.get("domains", [])):
        failures.append("release status domain count is stale")
    if release_status.get("evaluation_assets", {}).get("github_matrix") != matrix.get("summary"):
        failures.append("release status GitHub matrix is stale")
    for domain in coverage.get("domains", []):
        if domain["domain_id"] not in readme:
            failures.append(f"README omits domain pack: {domain['domain_id']}")
        if domain["maturity"] not in readme:
            failures.append(f"README omits maturity vocabulary: {domain['maturity']}")
        if domain["practice_status"] not in readme:
            failures.append(f"README omits practice status: {domain['practice_status']}")
        if domain["maturity"] in {"knowledge_backed", "contract_tested"} and domain.get("production_claim") == "allowed":
            failures.append(f"non-expert domain allows unqualified production claim: {domain['domain_id']}")

    for relative in PUBLIC_FILES:
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing public document: {relative}")
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            lowered = line.lower()
            for claim in POSITIVE_ONLY_CLAIMS:
                if claim.lower() in lowered and not any(marker in lowered for marker in NEGATION_MARKERS):
                    failures.append(f"unsupported public claim in {relative}:{number}: {claim}")

    for path in text_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        lowered = path.read_text(encoding="utf-8").lower()
        for marker in LEGACY_RUNTIME_MARKERS:
            if marker in lowered:
                failures.append(f"legacy runtime marker {marker!r} in {path.relative_to(ROOT)}")
        if ".github" not in path.parts and re.search(r"\bv4(?:\.\d+)?\b|\b4\.x\b", lowered):
            failures.append(f"release-specific legacy version marker in {path.relative_to(ROOT)}")

    git_files = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if git_files.returncode == 0:
        for relative in git_files.stdout.splitlines():
            normalized = relative.replace("\\", "/")
            if "__pycache__/" in normalized or normalized.endswith((".pyc", ".tmp", ".log")):
                failures.append(f"generated file is tracked: {normalized}")
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for marker in ("__pycache__/", "*.pyc", "*.tmp", "*.log", "*.bak", "*.backup"):
        if marker not in ignore:
            failures.append(f".gitignore misses generated-file rule: {marker}")

    allowed_examples = {
        "minimal-v5", "publishing-learning-v5", "generic-energy-capsule-v5",
        "traffic-regulatory-change-v5",
    }
    shipped_examples = {path.name for path in (ROOT / "examples").iterdir() if path.is_dir()}
    unexpected_examples = shipped_examples - allowed_examples
    if unexpected_examples:
        failures.append("unreviewed or project-specific example directories: " + ", ".join(sorted(unexpected_examples)))

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
    for relative in ("agents/claude-code.md", "agents/openai-codex.md"):
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        for marker in ("v5", "product truth", "stable id"):
            if marker not in text:
                failures.append(f"{relative} is not aligned with SKILL.md marker: {marker}")
        if "product truth" not in skill:
            failures.append("SKILL.md lost Product Truth source ordering")

    if failures:
        for item in sorted(set(failures)):
            print(f"FAIL: {item}")
        return 1
    print("PASS: public claims, pure-v5 scope, package hygiene, domains, and agent entries are aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
