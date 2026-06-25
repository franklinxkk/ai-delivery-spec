#!/usr/bin/env python3
"""Validate IA Skeleton <-> Prototype <-> PRD cross-references.

Usage:
    python scripts/validate_ia_skeleton.py \
        --ia-skeleton path/to/ia-skeleton.yaml \
        --prototype path/to/prototype.html \
        --prd path/to/prd.md

Exit code 0 if no issues, 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def extract_data_testids(html: str) -> set[str]:
    return set(re.findall(r'data-testid="([^"]+)"', html))


def extract_data_actions(html: str) -> set[str]:
    return set(re.findall(r'data-action="([^"]+)"', html))


def extract_prd_references(prd: str) -> dict[str, set[str]]:
    """Extract IA Skeleton view references and data-action references from PRD."""
    return {
        "view_refs": set(re.findall(r"IA Skeleton `(M\d+-V\d+)`", prd)),
        "data_action_refs": set(re.findall(r"data-action=\"([^\"]+)\"", prd)),
        "data_testid_refs": set(re.findall(r"data-testid=\"([^\"]+)\"", prd)),
    }


def validate(ia_skeleton_path: Path, prototype_path: Path | None, prd_path: Path | None) -> list[str]:
    issues: list[str] = []

    skeleton = load_yaml(ia_skeleton_path)
    modules = skeleton.get("ia_skeleton", {}).get("modules", [])
    if not modules:
        issues.append("IA Skeleton has no modules")
        return issues

    all_view_ids: set[str] = set()
    all_region_ids: set[str] = set()
    module_view_map: dict[str, list[str]] = {}

    for mod in modules:
        mod_id = mod.get("module_id")
        mod_name = mod.get("module_name", mod_id)
        views = mod.get("views", [])
        primary_roles = mod.get("primary_roles", [])

        if not views:
            issues.append(f"{mod_id} ({mod_name}) has no views")
            continue

        module_view_map[mod_id] = []
        covered_roles: set[str] = set()

        for view in views:
            view_id = view.get("view_id")
            view_type = view.get("view_type", "page")
            regions = view.get("regions", [])
            visible_to = view.get("visible_to", primary_roles)

            if not view_id:
                issues.append(f"{mod_id} has a view without view_id")
                continue

            if not re.match(r"^M\d+-V\d+$", view_id):
                issues.append(f"{mod_id}: view_id '{view_id}' does not match MNN-VNN pattern")

            expected_prefix = f"{mod_id}-V"
            if not view_id.startswith(expected_prefix):
                issues.append(
                    f"{mod_id}: view_id '{view_id}' should start with '{expected_prefix}'"
                )

            all_view_ids.add(view_id)
            module_view_map[mod_id].append(view_id)
            covered_roles.update(visible_to)

            for region in regions:
                region_id = region.get("region_id")
                if region_id:
                    all_region_ids.add(region_id)

        # Every primary role should see at least one view in this module
        for role in primary_roles:
            if role not in covered_roles:
                issues.append(
                    f"{mod_id}: primary role '{role}' has no visible view"
                )

    # Cross-module flows
    flows = skeleton.get("ia_skeleton", {}).get("cross_module_flows", [])
    for flow in flows:
        source = flow.get("source_view")
        target = flow.get("target_view")
        if source and source not in all_view_ids:
            issues.append(f"Cross-module flow '{flow.get('flow')}' references missing source view '{source}'")
        if target and target not in all_view_ids:
            issues.append(f"Cross-module flow '{flow.get('flow')}' references missing target view '{target}'")

    # Prototype checks
    if prototype_path:
        html = load_text(prototype_path)
        testids = extract_data_testids(html)
        actions = extract_data_actions(html)

        for view_id in sorted(all_view_ids):
            expected_testids = {f"page-{view_id}", f"modal-{view_id}", f"drawer-{view_id}"}
            if not expected_testids & testids:
                issues.append(
                    f"Prototype missing data-testid for view '{view_id}' "
                    f"(expected one of {expected_testids})"
                )

        for region_id in sorted(all_region_ids):
            expected = f"region-{region_id}"
            if expected not in testids:
                issues.append(f"Prototype missing region data-testid '{expected}'")

        # --- primary_actions → data-action cross-validation ---
        for mod in modules:
            mod_id = mod.get("module_id", "?")
            for view in mod.get("views", []):
                view_id = view.get("view_id", "?")
                for action_entry in view.get("primary_actions", []):
                    action_desc = action_entry.get("action", "") if isinstance(action_entry, dict) else str(action_entry)
                    keywords = re.findall(r"[\w-]+", action_desc.lower())
                    matched = False
                    for kw in keywords:
                        if len(kw) < 3:
                            continue
                        for da in actions:
                            if kw in da.lower():
                                matched = True
                                break
                        if matched:
                            break
                    if not matched and keywords:
                        issues.append(
                            f"WARNING: primary_action '{action_desc[:50]}' in {view_id} "
                            f"has no matching data-action in prototype"
                        )

    # PRD checks
    if prd_path:
        prd = load_text(prd_path)
        refs = extract_prd_references(prd)

        for view_ref in sorted(refs["view_refs"]):
            if view_ref not in all_view_ids:
                issues.append(f"PRD references unknown IA Skeleton view '{view_ref}'")

        if prototype_path:
            for action_ref in sorted(refs["data_action_refs"]):
                if action_ref not in actions:
                    issues.append(f"PRD references data-action '{action_ref}' not found in prototype")

            for testid_ref in sorted(refs["data_testid_refs"]):
                if testid_ref not in testids:
                    issues.append(f"PRD references data-testid '{testid_ref}' not found in prototype")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate IA Skeleton <-> Prototype <-> PRD consistency"
    )
    parser.add_argument(
        "--ia-skeleton",
        type=Path,
        required=True,
        help="Path to ia-skeleton.yaml",
    )
    parser.add_argument(
        "--prototype",
        type=Path,
        default=None,
        help="Path to prototype.html (optional)",
    )
    parser.add_argument(
        "--prd",
        type=Path,
        default=None,
        help="Path to prd.md (optional)",
    )
    args = parser.parse_args()

    if not args.ia_skeleton.exists():
        print(f"ERROR: IA Skeleton not found: {args.ia_skeleton}", file=sys.stderr)
        return 1

    issues = validate(args.ia_skeleton, args.prototype, args.prd)

    if issues:
        print(f"Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("IA Skeleton validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
