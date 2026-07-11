#!/usr/bin/env python3
"""Validate the dated, source-backed ecosystem comparison contract."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "evals/ecosystem-comparison.yaml"
README = ROOT / "README.md"
REPORT = ROOT / "docs/ecosystem-comparison.md"
RATINGS = {"primary", "supported", "adjacent", "not_evidenced"}
REQUIRED_DIMENSIONS = {
    "discovery_strategy",
    "clarification_scope",
    "business_model_truth",
    "engineering_handoff",
    "acceptance_traceability",
    "change_management",
    "launch_learn_retire",
    "ai_governance_runtime_risk",
    "skill_engineering_maintainability",
}
REQUIRED_TOOLS = {
    "ai-delivery-spec",
    "github-spec-kit",
    "mattpocock-requirements-chain",
    "phuryn-pm-skills",
    "product-on-purpose-pm-skills",
    "alirezarezvani-product-skills",
    "deanpeters-pm-skills",
    "max4c-requirements-flow",
    "github-awesome-copilot-prd",
    "digidai-product-manager-skills",
    "pratikshadake-pm-skills",
    "superpowers",
}
README_FEATURED_TOOLS = {
    "ai-delivery-spec",
    "github-spec-kit",
    "mattpocock-requirements-chain",
    "phuryn-pm-skills",
    "product-on-purpose-pm-skills",
    "digidai-product-manager-skills",
    "superpowers",
}


def main() -> int:
    failures: list[str] = []
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")

    try:
        snapshot = date.fromisoformat(str(data["snapshot_date"]))
    except (KeyError, ValueError):
        failures.append("snapshot_date must be ISO YYYY-MM-DD")
        snapshot = None
    if snapshot and snapshot > date.today():
        failures.append("snapshot_date cannot be in the future")

    environment = data.get("execution_environment", {})
    if environment.get("user_interface_label") != "GPT-5.6 SOL":
        failures.append("user-reported execution model label is missing")
    if environment.get("attestation") != "user_reported":
        failures.append("model label must remain explicitly user-reported")
    if environment.get("independently_verifiable_from_repository") is not False:
        failures.append("repository must not claim independent model-identity attestation")

    dimensions = set(data.get("dimensions", {}))
    if dimensions != REQUIRED_DIMENSIONS:
        failures.append(
            "comparison dimensions drifted: "
            f"missing={sorted(REQUIRED_DIMENSIONS - dimensions)}, "
            f"extra={sorted(dimensions - REQUIRED_DIMENSIONS)}"
        )

    tools = data.get("tools", [])
    ids = [tool.get("id") for tool in tools]
    if len(ids) != len(set(ids)):
        failures.append("tool IDs must be unique")
    if set(ids) != REQUIRED_TOOLS:
        failures.append(
            "comparison candidate set drifted: "
            f"missing={sorted(REQUIRED_TOOLS - set(ids))}, "
            f"extra={sorted(set(ids) - REQUIRED_TOOLS)}"
        )

    repositories: set[str] = set()
    for tool in tools:
        tool_id = tool.get("id", "<missing>")
        repository = tool.get("repository", "")
        parsed = urlparse(repository)
        if parsed.scheme != "https" or parsed.netloc != "github.com":
            failures.append(f"{tool_id}: repository must be an official GitHub URL")
        if repository in repositories:
            failures.append(f"{tool_id}: duplicate repository {repository}")
        repositories.add(repository)

        activity = tool.get("activity", {})
        for key in ("stars", "forks"):
            if not isinstance(activity.get(key), int) or activity[key] < 0:
                failures.append(f"{tool_id}: activity.{key} must be a non-negative integer")
        try:
            date.fromisoformat(str(activity.get("pushed")))
        except ValueError:
            failures.append(f"{tool_id}: activity.pushed must be ISO YYYY-MM-DD")

        evidence = tool.get("evidence", [])
        if not evidence:
            failures.append(f"{tool_id}: at least one evidence reference is required")
        for item in evidence:
            item = str(item)
            if item.startswith("https://"):
                if urlparse(item).netloc not in {"github.com", "github.github.com"}:
                    failures.append(f"{tool_id}: non-primary evidence host: {item}")
            elif not (ROOT / item).is_file():
                failures.append(f"{tool_id}: local evidence does not exist: {item}")

        ratings = tool.get("ratings", {})
        if set(ratings) != REQUIRED_DIMENSIONS:
            failures.append(f"{tool_id}: ratings must cover all nine dimensions exactly once")
        for dimension, rating in ratings.items():
            if rating not in RATINGS:
                failures.append(f"{tool_id}: invalid rating {rating!r} for {dimension}")

        name = tool.get("name", "")
        if tool_id in README_FEATURED_TOOLS and repository not in readme:
            failures.append(f"{tool_id}: README complementary table omits {repository}")
        if name not in report:
            failures.append(f"{tool_id}: detailed report omits tool name {name!r}")

    for text_name, text in (("README", readme), ("report", report)):
        lowered = text.lower()
        if "user-reported" not in lowered:
            failures.append(f"{text_name}: model-label attestation boundary is missing")
        if "not output quality" not in lowered and "not a benchmark" not in lowered:
            failures.append(f"{text_name}: documentary-coverage limitation is missing")
        if "stars" not in lowered or "never change" not in lowered:
            failures.append(f"{text_name}: popularity non-scoring rule is missing")

    if failures:
        for item in sorted(set(failures)):
            print(f"FAIL: {item}")
        return 1
    print(
        "PASS: ecosystem comparison has 12 source-backed candidates, nine complete "
        "dimensions, dated activity signals, and an explicit model-attestation boundary"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
