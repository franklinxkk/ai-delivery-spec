#!/usr/bin/env python3
"""Online verification for pinned GitHub evaluation issues, refs, and paths."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
API = "https://api.github.com"


def request_json(path: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-delivery-spec-source-verifier",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    request = urllib.request.Request(
        API + path,
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def verify_case(case: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    repo = case["repository"]
    ref = case["pinned_ref"]
    branch = urllib.parse.quote(case["default_branch"], safe="")
    issue_number = case["source_issue"]["number"]
    row: dict[str, Any] = {"case_id": case["id"], "repository": repo, "pinned_ref": ref}
    try:
        tree = request_json(f"/repos/{repo}/git/trees/{ref}?recursive=1")
        paths = {item["path"] for item in tree.get("tree", [])}
        missing_paths = [path for path in case["source_paths"] if path not in paths]
        row["pinned_ref_reachable"] = not tree.get("truncated", False)
        row["source_paths_exist"] = not missing_paths
        row["missing_paths"] = missing_paths
        issue_url = case["source_issue"]["url"]
        issue_repo = "/".join(issue_url.split("/")[3:5])
        issue = request_json(f"/repos/{issue_repo}/issues/{issue_number}")
        row["issue_reachable"] = issue.get("number") == issue_number
        branch_ref = request_json(f"/repos/{repo}/git/ref/heads/{branch}")
        row["current_branch_head"] = branch_ref.get("object", {}).get("sha")
        row["head_changed_since_pin"] = row["current_branch_head"] != ref
        if missing_paths:
            failures.append(f"{case['id']} missing pinned paths: {', '.join(missing_paths)}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        row["error"] = str(exc)
        failures.append(f"{case['id']} GitHub verification failed: {exc}")
    return row, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=ROOT / "maintainer/evals/github-cases.yaml")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    catalog = yaml.safe_load(args.catalog.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    failures: list[str] = []

    with ThreadPoolExecutor(max_workers=min(8, len(catalog["cases"]))) as pool:
        futures = {pool.submit(verify_case, case): case["id"] for case in catalog["cases"]}
        for future in as_completed(futures):
            row, case_failures = future.result()
            results.append(row)
            failures.extend(case_failures)
    results.sort(key=lambda item: item["case_id"])

    document = {
        "schema_version": "5.0.0",
        "evidence_type": "online_github_source_verification",
        "verification_channel": "GitHub REST API; set GITHUB_TOKEN to avoid anonymous rate limits",
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "result": "failed" if failures else "passed",
        "cases": results,
        "claim_boundary": (
            "Proves that pinned refs, source paths, and issues were reachable at verification time; "
            "it does not prove requirement correctness, roadmap status, or implementation behavior."
        ),
    }
    rendered = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1
    print(f"PASS: verified {len(results)} pinned GitHub evaluation sources online")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
