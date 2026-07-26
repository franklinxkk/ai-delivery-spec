#!/usr/bin/env python3
"""Build or check the deterministic GitHub case-by-stage validation matrix."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from score_evaluation_run import score, validate_run


ROOT = Path(__file__).resolve().parents[2]
STAGES = ("requirement", "design", "coding_delivery")


def build() -> dict[str, Any]:
    catalog = yaml.safe_load((ROOT / "maintainer/evals/github-cases.yaml").read_text(encoding="utf-8"))
    run_map: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted((ROOT / "maintainer/evals/runs").glob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        runs = document.get("runs", []) if isinstance(document, dict) and "runs" in document else [document]
        for run in runs:
            if validate_run(run):
                continue
            key = (run["case_id"], run["stage"])
            if key in run_map:
                raise ValueError(f"duplicate evaluation run for {key[0]}/{key[1]}")
            run_map[key] = {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "run": run}

    rows: list[dict[str, Any]] = []
    counts = {"not_run": 0, "partial": 0, "passed": 0}
    for case in catalog["cases"]:
        for stage in STAGES:
            found = run_map.get((case["id"], stage))
            if not found:
                status = "not_run"
                row = {
                    "case_id": case["id"],
                    "domain": case["domain"],
                    "stage": stage,
                    "status": status,
                    "run": None,
                    "release_pass": False,
                }
            else:
                result = score(found["run"])
                status = "passed" if result["release_pass"] else "partial"
                row = {
                    "case_id": case["id"],
                    "domain": case["domain"],
                    "stage": stage,
                    "status": status,
                    "run": found["path"],
                    "release_pass": result["release_pass"],
                }
            counts[status] += 1
            rows.append(row)
    return {
        "schema_version": "5.0.0",
        "matrix_type": "github_requirement_design_coding_validation",
        "summary": {"cases": len(catalog["cases"]), "stage_cells": len(rows), **counts},
        "rows": rows,
        "claim_boundary": (
            "A partial cell has one exploratory run only. A not_run cell has obligations but no execution evidence."
        ),
    }


def build_prompt_pack() -> dict[str, Any]:
    catalog = yaml.safe_load((ROOT / "maintainer/evals/github-cases.yaml").read_text(encoding="utf-8"))
    prompts: list[dict[str, Any]] = []
    for case in catalog["cases"]:
        probe = case["lifecycle_probe"]
        prompt = (
            "使用 AI Delivery Spec 5.4.0。你只有下面这一句话需求，不得假设还有其他已批准材料：\n"
            f"{case['captured_requirement']}\n\n"
            f"当前从 {probe['entry_stage']} 阶段进入，本次只到 {probe['target_stage']} 阶段。"
            "生成该阶段最小合格产物；如果该阶段必须依赖前序规格、批准基线、可执行系统或真实证据，"
            "请明确阻断并列出最小前置材料，不得伪造。输出语言为中文，Stable ID 与代码标识保持原样。\n"
            "执行边界：先读 SKILL.md；不要读取 README、maintainer/、无关示例或全量领域包；"
            "只加载目标阶段切片及其明确引用的模板、Schema 和门禁；只生成该阶段合同要求的产物。"
            "除非当前阶段确需时效性证据，否则不要外部调研；目标门禁得出结论后立即停止，"
            "不要输出长篇工作日志。"
        )
        prompts.append({
            "prompt_id": f"LCP-{case['id']}",
            "case_id": case["id"],
            "domain": case["domain"],
            "repository": case["repository"],
            "entry_stage": probe["entry_stage"],
            "target_stage": probe["target_stage"],
            "prompt": prompt,
            "expected_output": probe["expected_output"],
            "expected_behavior": probe["expected_behavior"],
            "must_not": probe["must_not"],
        })
    return {
        "schema_version": "5.4.0",
        "pack_type": "cross_model_one_line_lifecycle_probe",
        "prompt_count": len(prompts),
        "required_run_metadata": [
            "provider", "model_id", "client_name", "client_version",
            "context_window", "temperature", "run_at", "duration_seconds",
            "artifact_count", "gate_result", "output_ref",
        ],
        "execution_contract": {
            "load": "SKILL.md + target-stage slice + explicitly referenced template/schema/gate only",
            "exclude": ["README", "maintainer/", "unrelated examples", "full domain packs"],
            "research": "only when the target stage requires current or external evidence",
            "stop": "after the target gate result or explicit prerequisite block",
            "claim": "score behavioral correctness and execution cost separately",
        },
        "prompts": prompts,
        "claim_boundary": (
            "This pack is a portable behavioral input. A generated file is not a pass; "
            "score actual outputs, preserve gaps, and never use shared or leaked credentials."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--prompt-pack", type=Path)
    args = parser.parse_args()
    selected = sum(bool(item) for item in (args.output, args.check, args.prompt_pack))
    if selected != 1:
        parser.error("provide exactly one of --output, --check, or --prompt-pack")
    if args.prompt_pack:
        document = build_prompt_pack()
        rendered = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
        args.prompt_pack.parent.mkdir(parents=True, exist_ok=True)
        args.prompt_pack.write_text(rendered, encoding="utf-8", newline="\n")
        stages = {item["entry_stage"] for item in document["prompts"]}
        print(f"PASS: wrote {document['prompt_count']} cross-model prompts covering {len(stages)} lifecycle stages to {args.prompt_pack}")
        return 0
    document = build()
    rendered = yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
    target = args.output or args.check
    if args.check:
        if not args.check.exists() or args.check.read_text(encoding="utf-8") != rendered:
            print(f"FAIL: GitHub validation matrix is stale: {args.check}")
            return 1
        print(
            "PASS: GitHub validation matrix is current "
            f"({document['summary']['partial']} partial, {document['summary']['not_run']} not_run)"
        )
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"PASS: wrote GitHub validation matrix to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
