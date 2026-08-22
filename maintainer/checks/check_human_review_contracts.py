#!/usr/bin/env python3
"""Small current-contract smoke suite for human review and handoff behavior.

This intentionally checks user-visible decisions and executable boundaries instead
of pinning hundreds of historical phrases across the repository.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/ai_delivery_spec_cli.py"
failures: list[str] = []


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(relative: str, markers: tuple[str, ...]) -> None:
    text = read(relative)
    for marker in markers:
        if marker not in text:
            failures.append(f"{relative} misses {marker!r}")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )


def run_json(*args: str) -> tuple[int, dict]:
    result = run(*args)
    try:
        return result.returncode, json.loads(result.stdout)
    except json.JSONDecodeError:
        failures.append(f"command did not return JSON: {' '.join(args)}\n{result.stdout}{result.stderr}")
        return result.returncode, {}


def visible_text(payload: dict) -> str:
    values = [str(payload.get("coverage", "")), *map(str, payload.get("not_proven", []))]
    for item in payload.get("findings", []):
        values.extend(str(item.get(key, "")) for key in ("message", "cause", "how_to_fix", "repair_example"))
    return "\n".join(values)


# Preserve the product decisions that must survive refactors. Exact templates and
# exhaustive wording belong to focused tests, not this release smoke check.
require(
    "SKILL.md",
    (
        "用户明确要求“评审版/评审模式/编号标注/评审抽屉”",
        "未确认时继续产品模式",
        "默认锁定用户指定语言",
        "无页面入口权限时菜单/路由入口不可见",
        "静态、浏览器、业务确认、真实实现、客户验收五级证据不可越级",
    ),
)
require(
    "references/prototype.md",
    (
        "交开发”“给前端/后端/测试看”“开需求评审会”只说明消费方",
        "核心流程图",
        "状态转换图",
        "数据流/血缘图",
        "普通无入口角色不需要先进入页面再看“您无权限”",
    ),
)
require(
    "references/review-workspace.md",
    (
        "未参与原讨论的接收者能独立",
        "一个 STEP 是一个可归责工作提交点",
        "applicability=not_affected",
        "machine_handoff.status",
        "冷读通过仍不证明实现正确",
    ),
)

schema = json.loads(read("schemas/agent-handoff.schema.json"))
if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
    failures.append("machine JSON Schema draft identifier was localized")
if "draft" not in schema["properties"]["status"]["enum"]:
    failures.append("machine status enum was localized")


# Auto-language affects selected human text while JSON retains both diagnostic
# projections for tools and bilingual teams.
code, english = run_json(
    str(CLI), "gate", "--profile", "prototype",
    "--prototype", "schemas/gate-result.schema.json", "--level", "L2",
    "--language", "auto", "--format", "json",
)
if code != 2 or english.get("output_language") != "en-US":
    failures.append(f"English auto-language gate failed: rc={code}")
if re.search(r"[\u4e00-\u9fff]", visible_text(english)):
    failures.append("English gate leaked Chinese into selected human diagnostics")
if not all(item.get("message_zh") and item.get("message_en") for item in english.get("findings", [])):
    failures.append("JSON findings lost bilingual diagnostic projections")


# Existing prototype debt remains visible as GAP when the same baseline is
# supplied; it must not be silently called clean or reclassified as new BLOCK.
broken = ROOT / "maintainer/tests/fixtures/gate-prototype-invalid.html"
code, inherited = run_json(
    str(CLI), "gate", "--profile", "prototype", "--prototype", str(broken),
    "--prototype-baseline", str(broken), "--level", "L2", "--format", "json",
)
if code != 1 or inherited.get("summary", {}).get("blockers") != 0:
    failures.append(f"inherited prototype debt is not an explicit GAP: rc={code}")
if inherited.get("metrics", {}).get("prototype_inherited_findings", 0) < 1:
    failures.append("prototype baseline comparison did not record inherited findings")


# A handoff STEP is implementable only when it resolves to the bound PRD.
with tempfile.TemporaryDirectory(prefix="ads-human-review-", dir=ROOT) as raw:
    work = Path(raw)
    prd = work / "prd.md"
    prd_text = "# PRD\n\nREQ-DEMO-001 / ACT-DEMO-001 / AC-DEMO-001\n"
    prd.write_text(prd_text, encoding="utf-8")
    packet = work / "packet.md"
    packet_text = "# Packet\n\nREQ-DEMO-001 / STEP-GHOST-999 / AC-DEMO-001\n"
    packet.write_text(packet_text, encoding="utf-8")
    baseline_hash = hashlib.sha256(prd_text.encode()).hexdigest()
    manifest = work / "handoff.json"
    manifest.write_text(json.dumps({
        "schema_version": "5.3.0", "status": "review_ready",
        "baseline": {"version": "1.0", "hash": baseline_hash, "requirement_ref": prd.name},
        "packets": [{
            "id": "MOD-DEMO", "kind": "mod", "owner": "team", "path": packet.name,
            "baseline_hash": baseline_hash,
            "content_sha256": hashlib.sha256(packet_text.encode()).hexdigest(),
            "scope_refs": ["REQ-DEMO-001"], "implementation_step_refs": ["STEP-GHOST-999"],
            "acceptance_refs": ["AC-DEMO-001"],
        }],
        "handoffs": [],
    }), encoding="utf-8")
    code, handoff = run_json(str(CLI), "gate", "--profile", "agent_handoff", "--manifest", str(manifest), "--format", "json")
    if code != 2 or "HANDOFF-STEP-NOT-IN-PRD" not in {item.get("code") for item in handoff.get("findings", [])}:
        failures.append("ghost implementation STEP escaped the handoff gate")


if failures:
    raise SystemExit("\n".join(failures))
print("PASS: review opt-in, language projection, inherited debt, role workspace and STEP handoff boundaries hold")
