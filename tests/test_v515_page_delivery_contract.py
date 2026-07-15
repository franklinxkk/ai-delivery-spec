"""Regression: L3 handoff blocks page shells and stacked legacy prototypes."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "quality_gate.py"
FIXTURES = ROOT / "tests" / "fixtures"
failures: list[str] = []


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), *args, "--format", "json"],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )


thin_prd = run(
    "--profile", "prd", "--prd", str(FIXTURES / "coding-l2.md"), "--level", "L3",
)
thin_codes = {item["code"] for item in json.loads(thin_prd.stdout)["findings"]}
if "PRD-NO-PAGE-CONTRACT-SCOPE" not in thin_codes:
    failures.append(f"L3 PRD without declared page contracts was not blocked: {sorted(thin_codes)}")

legacy_html = """<!doctype html><html><body>
<div data-testid="page-VIEW-X"><button onclick="edit()">Edit</button></div>
<script>
function edit() { alert('ok'); }
function edit() { alert('wrong entity'); }
document.querySelector('button').dataset.action = 'ACT-EDIT';
</script></body></html>"""
with tempfile.TemporaryDirectory() as tmp:
    artifact = Path(tmp) / "legacy.html"
    artifact.write_text(legacy_html, encoding="utf-8")
    legacy = run("--profile", "prototype", "--prototype", str(artifact), "--level", "L3")
legacy_codes = {item["code"] for item in json.loads(legacy.stdout)["findings"]}
expected = {
    "PROTO-INLINE-HANDLER", "PROTO-CONTROL-NO-ACTION",
    "PROTO-DUPLICATE-FUNCTION", "PROTO-RUNTIME-ACTION-RETROFIT",
}
if not expected.issubset(legacy_codes):
    failures.append(f"stacked legacy prototype gaps were not blocked: {sorted(legacy_codes)}")

selector_html = """<!doctype html><html><body>
<main data-testid="page-VIEW-X" data-state="ready">
  <input data-field="FLD-X-NAME"><button data-action="ACT-X-SAVE" data-ac="AC-X-001">Save</button>
</main>
<script>document.querySelector('[data-testid="page-VIEW-X"]');</script>
</body></html>"""
with tempfile.TemporaryDirectory() as tmp:
    artifact = Path(tmp) / "selector.html"
    artifact.write_text(selector_html, encoding="utf-8")
    selector_result = run("--profile", "prototype", "--prototype", str(artifact), "--level", "L3")
selector_codes = {item["code"] for item in json.loads(selector_result.stdout)["findings"]}
if "PROTO-DUPLICATE-PAGE" in selector_codes:
    failures.append("JavaScript data-testid selector was misread as a duplicate page")

thin_four_lens = """---
page_contract_view_ids: [VIEW-DEMO]
---
# Demo baseline
需求准入 背景 角色 角色旅程 业务流程 功能总览 分模块功能需求 验收方案
字段字典 规则与状态机 机器可读验收 双向追溯 反向 禁止推断 一份 PRD
REQ-DEMO-001 ROLE-DEMO FLOW-DEMO MOD-DEMO STATE-DEMO ACT-DEMO AC-DEMO
数据范围 权限 审计 集成 非功能 变更入口 CHG-DEMO evidence_required
## 角色旅程
ROLE-DEMO enters FLOW-DEMO and submits; visible result succeeds or failure recovery preserves state.
## 分模块功能需求
<!-- PAGE-CONTRACT: VIEW-DEMO -->
页面目标与入口 区域布局 筛选 列表列 字段与控件 动作与权限 分页 导入不适用 导出不适用 状态异常 原型绑定
METRIC-DEMO formula 公式 去重 source zero format
ACT-DEMO-OPEN AC-DEMO-001
## 第四部分：工程与 AI Coding 附录
API、事件与集成 请求字段 成功响应 错误码 幂等
preconditions steps expected_visible expected_domain negative_cases evidence_required
REQ-DEMO-001 | VIEW-DEMO | ACT-DEMO-OPEN | behavior | AC-DEMO-001
"""
with tempfile.TemporaryDirectory() as tmp:
    artifact = Path(tmp) / "thin-four-lens.md"
    artifact.write_text(thin_four_lens, encoding="utf-8")
    walked = run("--profile", "prd", "--prd", str(artifact), "--level", "L3")
walked_codes = {item["code"] for item in json.loads(walked.stdout)["findings"]}
four_lens_expected = {"PRD-PAGE-NO-FIELDS", "PRD-PAGE-NO-ACTIONS", "PRD-PAGE-NO-API-TRACE"}
if not four_lens_expected.issubset(walked_codes):
    failures.append(f"thin four-lens page was not blocked: {sorted(walked_codes)}")

managed_thin = thin_four_lens.replace(
    "page_contract_view_ids: [VIEW-DEMO]",
    "page_contract_view_ids: [VIEW-DEMO]\nmanaged_relation_view_ids: [VIEW-DEMO]",
)
with tempfile.TemporaryDirectory() as tmp:
    artifact = Path(tmp) / "managed-thin.md"
    artifact.write_text(managed_thin, encoding="utf-8")
    managed = run("--profile", "prd", "--prd", str(artifact), "--level", "L3")
managed_codes = {item["code"] for item in json.loads(managed.stdout)["findings"]}
managed_expected = {"PRD-NO-ROLE-WORK-SURFACE-MATRIX", "PRD-INCOMPLETE-MANAGED-RELATION"}
if not managed_expected.issubset(managed_codes):
    failures.append(f"thin managed relation was not blocked: {sorted(managed_codes)}")

managed_complete = managed_thin.replace(
    "## 角色旅程",
    "## 角色—工作面闭环矩阵\nROLE-DEMO | managed collection | VIEW-DEMO inventory 台账 | batch result/recovery\n## 角色旅程",
).replace(
    "页面目标与入口 区域布局",
    "页面目标与入口 REL-DEMO parent target version 来源 继承 批量 预检 部分失败 幂等 /api/demo AC-DEMO-001 台账 区域布局",
)
with tempfile.TemporaryDirectory() as tmp:
    artifact = Path(tmp) / "managed-complete.md"
    artifact.write_text(managed_complete, encoding="utf-8")
    managed_ok = run("--profile", "prd", "--prd", str(artifact), "--level", "L3")
managed_ok_codes = {item["code"] for item in json.loads(managed_ok.stdout)["findings"]}
if managed_ok_codes & managed_expected:
    failures.append(f"complete managed relation was rejected: {sorted(managed_ok_codes)}")

if failures:
    raise SystemExit("\n".join(failures))
print("PASS: L3 page contracts and clean prototype ownership are enforced")
