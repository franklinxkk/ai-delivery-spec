"""v5.3.x regression: authority, clarification, prototype evidence and handoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "quality_gate.py"
CLI = ROOT / "scripts" / "ai_delivery_spec_cli.py"
FIXTURE = ROOT / "maintainer" / "tests" / "fixtures" / "coding-l2.md"
failures: list[str] = []

for relative, markers in {
    "references/lifecycle.md": (
        "Decision-Tree Clarification", "self-check gate", "recommended answer",
        "Only P0/P1 branches", "is unavailable",
    ),
    "references/prototype.md": (
        "DEC-AESTHETIC-*", "explicit taboo", "--acceptance-run",
        "browser_evidence_status", "region-REG-*",
    ),
    "references/troubleshooting.md": (
        "Exact-ID And Dynamic-Anchor Migration", "${act}", "dataset.action",
        "PROTO-BROWSER-EVIDENCE-MISSING",
    ),
}.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            failures.append(f"{relative} misses v5.3.1 contract marker: {marker}")


def run_gate(*args: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(GATE), *args, "--format", "json"], cwd=ROOT,
        text=True, encoding="utf-8", capture_output=True,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(result.stdout + result.stderr) from exc
    return result.returncode, payload


def codes(payload: dict) -> set[str]:
    return {item["code"] for item in payload["findings"]}


with tempfile.TemporaryDirectory(prefix="ads-v530-") as temp_name:
    temp = Path(temp_name)
    base = FIXTURE.read_text(encoding="utf-8")

    # A fenced/prose mention of an appendix cannot satisfy heading order.
    heading_probe = temp / "heading-probe.md"
    heading_probe.write_text(
        base.replace("## 4. 角色旅程", "```markdown\n## 附录 A：假的提前附录\n```\n正文提到 ## 附录 A 不算标题。\n\n## 4. 角色旅程"),
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(heading_probe), "--level", "L2")
    if code != 0:
        failures.append(f"real Markdown heading parser rejected a valid baseline: {codes(payload)}")

    unknown_frontmatter = """---
open_p0_unknown_ids: [UNK-ITEM-001]
unknowns:
  - id: UNK-ITEM-001
    priority: P0
    status: open
    owner: product-owner
    blocks_stage: baseline
    affected_refs: [REQ-ITEM-001]
---
"""
    unknown_prd = temp / "unknown.md"
    unknown_prd.write_text(unknown_frontmatter + base, encoding="utf-8")
    code, payload = run_gate("--profile", "prd", "--prd", str(unknown_prd), "--level", "L2", "--stage", "clarify")
    if code != 1 or payload["status"] != "REVIEW_COMPLETE_WITH_GAPS":
        failures.append(f"future-stage P0 should be a scoped gap: {payload['status']} {codes(payload)}")
    code, payload = run_gate("--profile", "prd", "--prd", str(unknown_prd), "--level", "L2", "--stage", "baseline", "--scope-ref", "REQ-ITEM-001")
    if code != 3 or payload["status"] != "BLOCKED_BY_P0_UNKNOWN":
        failures.append(f"active P0 did not use exit 3: {payload['status']} {codes(payload)}")

    unstructured_prd = temp / "unstructured-unknown.md"
    unstructured_prd.write_text("---\nopen_p0_unknown_ids: [REV-ITEM-001]\n---\n" + base, encoding="utf-8")
    code, payload = run_gate("--profile", "prd", "--prd", str(unstructured_prd), "--level", "L2")
    if code != 2 or not {"PRD-P0-UNKNOWN-ID-NOT-UNK", "PRD-P0-UNKNOWN-NOT-STRUCTURED"}.issubset(codes(payload)):
        failures.append(f"manual REV/open-P0 bypass escaped: {codes(payload)}")

    dynamic_prototype = temp / "dynamic-anchor.html"
    dynamic_prototype.write_text(
        """<!doctype html><main data-testid="page-VIEW-DEMO"></main>
<script>
const act=(id)=>'<button data-'+'action="'+id+'">run</button>';
document.querySelector('main').innerHTML=act('ACT-DEMO-RUN');
</script>""",
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prototype", "--prototype", str(dynamic_prototype), "--level", "L2")
    if code != 2 or "PROTO-DYNAMIC-ANCHOR-CONSTRUCTION" not in codes(payload):
        failures.append(f"dynamic data-action construction escaped L2: {codes(payload)}")
    if payload.get("metrics", {}).get("prototype_dynamic_action_candidates") != 1:
        failures.append("dynamic ACT candidate was not included in prototype inventory metrics")

    placeholder_prototype = temp / "placeholder-anchor.html"
    placeholder_prototype.write_text(
        '''<!doctype html><main data-testid="page-VIEW-DEMO"></main>
<script>const template=(act)=>`<button data-action="${act}">运行</button>`;</script>''',
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prototype", "--prototype", str(placeholder_prototype), "--level", "L2")
    if code != 2 or "PROTO-UNSTABLE-ACTION" not in codes(payload):
        failures.append(f"template placeholder action escaped stable-ID gate: {codes(payload)}")

    prototype_source = """<!doctype html>
<!-- PAGE-CONTRACT: VIEW-DEMO; primary=form; layout=composite; surfaces=form,list -->
<main data-testid="page-VIEW-DEMO">
__REGION_OPEN__<button data-action="ACT-DEMO-SAVE" data-ac="AC-DEMO-SAVE">保存</button>
<span data-state="idle">待保存</span>__REGION_CLOSE__</main>
<script>
const GlobalState={status:"idle"};
const ActionRegistry={"ACT-DEMO-SAVE":function(){GlobalState.status="saved";document.querySelector("[data-state]").textContent="已保存";}};
document.addEventListener("click",function(event){const target=event.target.closest("[data-action]");if(!target)return;ActionRegistry[target.dataset.action]();});
</script>"""
    regionless = temp / "regionless.html"
    regionless.write_text(prototype_source.replace("__REGION_OPEN__", "").replace("__REGION_CLOSE__", ""), encoding="utf-8")
    code, payload = run_gate("--profile", "prototype", "--prototype", str(regionless), "--level", "L3")
    if code != 2 or "PROTO-NO-REGION-ANCHOR" not in codes(payload):
        failures.append(f"complex L3 prototype without REG-* escaped: {payload['status']} {codes(payload)}")
    if "PROTO-BROWSER-EVIDENCE-MISSING" not in codes(payload):
        failures.append("L3 prototype without ARUN did not expose the browser evidence gap")

    evidenced_prototype = temp / "evidenced.html"
    evidenced_prototype.write_text(
        prototype_source.replace(
            "__REGION_OPEN__", '<section data-testid="region-REG-DEMO-FORM">'
        ).replace("__REGION_CLOSE__", "</section>"),
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prototype", "--prototype", str(evidenced_prototype), "--level", "L3")
    if code != 1 or payload["status"] != "REVIEW_COMPLETE_WITH_GAPS" or "PROTO-BROWSER-EVIDENCE-MISSING" not in codes(payload):
        failures.append(f"static-only L3 prototype was presented as complete: {payload['status']} {codes(payload)}")

    acceptance_run = temp / "ARUN-PROTOTYPE-001.yaml"
    acceptance_run.write_text(yaml.safe_dump({
        "schema_version": "5.1.0",
        "run_id": "ARUN-PROTOTYPE-001",
        "baseline_version": "1.0",
        "environment": "Chrome 127 / Windows 11 / Playwright",
        "executor": "qa-owner",
        "executed_at": "2026-07-19T10:00:00+08:00",
        "items": [{
            "id": "ARITEM-PROTOTYPE-001", "acceptance_ref": "AC-DEMO-SAVE",
            "requirement_refs": ["REQ-DEMO-SAVE"], "mandatory": True,
            "result": "pass", "actual_result": "点击保存后状态区显示已保存",
            "evidence_refs": ["EVD-PROTOTYPE-SAVE-001"], "defect_refs": [],
        }],
        "residual_issues": [], "conclusion": "accepted", "conditions": [],
        "sign_offs": [{
            "role": "qa", "actor": "qa-owner", "decision": "approve",
            "at": "2026-07-19T10:05:00+08:00", "evidence_ref": "EVD-PROTOTYPE-SAVE-001",
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate(
        "--profile", "prototype", "--prototype", str(evidenced_prototype),
        "--level", "L3", "--acceptance-run", str(acceptance_run),
    )
    if code != 0 or payload["status"] != "PASS":
        failures.append(f"evidence-bound L3 prototype failed: {payload['status']} {codes(payload)}")
    if payload.get("metrics", {}).get("prototype_browser_evidence") is not True:
        failures.append("accepted browser ARUN was not reflected in gate metrics")
    if not any("DEC-AESTHETIC" in item for item in payload.get("not_proven", [])):
        failures.append("gate did not disclose the unproven aesthetic direction")

    conflict_prd = temp / "conflict.md"
    conflict_prd.write_text(
        """---
canonical_candidates: [SRC-PRD-A, SRC-PROTOTYPE-B]
governance:
  canonical_authoring_surface: unified_prd
  binding_sources:
    - {source_ref: SRC-PRD-A, canonical: true}
    - {source_ref: SRC-PROTOTYPE-B, canonical: true}
---
""" + base,
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(conflict_prd), "--level", "L2")
    if code != 2 or "AUTH-MULTIPLE-CANONICAL-SOURCES" not in codes(payload):
        failures.append("multiple canonical candidates escaped DEC-CONFLICT gate")

    page_prd = temp / "page-profiles.md"
    page_prd.write_text(
        """---
source_refs: [SRC-ITEM-001]
open_p0_unknown_ids: []
page_contract_view_ids: [VIEW-COMPOSITE, VIEW-BUILDER]
---
""" + base + """

<!-- PAGE-CONTRACT: VIEW-COMPOSITE; primary=list; layout=composite; surfaces=list -->
页面目标与入口；区域布局；动作与权限；状态与异常；原型绑定；筛选；列表列；分页。
ACT-COMPOSITE-OPEN / ACT-COMPOSITE-EXPORT / AC-COMPOSITE-001；VIEW-COMPOSITE → API-COMPOSITE-LIST /api/composite。

<!-- PAGE-CONTRACT: VIEW-BUILDER; primary=composer; layout=builder; surfaces=composer -->
页面目标与入口；区域布局；动作与权限；状态与异常；原型绑定；拖拽、层级、资源池和排序。
ACT-BUILDER-ADD / ACT-BUILDER-SAVE / AC-BUILDER-001；VIEW-BUILDER → API-BUILDER-SAVE /api/builder。
""",
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(page_prd), "--level", "L3")
    page_codes = codes(payload)
    if "PRD-PAGE-COMPOSITE-TOO-THIN" not in page_codes:
        failures.append("composite page with one surface escaped")
    if "PRD-PAGE-BUILDER-INCOMPLETE" not in page_codes:
        failures.append("builder without composer/resource_pool/hierarchy set escaped")
    if "PRD-NO-ACCEPTANCE-PLAN" not in page_codes:
        failures.append("L3 baseline without an owned acceptance plan escaped")

    range_prd = temp / "range-id.md"
    range_prd.write_text(
        "---\nsource_refs: [SRC-ITEM-001]\nopen_p0_unknown_ids: []\npage_contract_view_ids: [VIEW-ITEM]\n---\n"
        + base + "\n正文错误缩写：AC-AUDIT-001..003。\n",
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(range_prd), "--level", "L3")
    if "PRD-NONEXACT-ID" not in codes(payload):
        failures.append("range stable ID in prose escaped exact-ID gate")

    # A v5.2 page contract may explicitly declare a surface not applicable.  It
    # must not be upgraded into a v5.3 mandatory surface merely because the
    # explanatory text contains the surface label.
    legacy_na_prd = temp / "legacy-na-page.md"
    legacy_na_prd.write_text(
        """---
source_refs: [SRC-ITEM-001]
open_p0_unknown_ids: []
page_contract_view_ids: [VIEW-LEGACY-NA]
---
""" + base + """

<!-- PAGE-CONTRACT: VIEW-LEGACY-NA -->
页面目标与入口；区域布局；动作与权限；状态与异常；原型绑定。
指标口径：不适用。字段与控件：不存在可编辑业务字段。导入：不适用。导出：不适用。
ACT-LEGACY-OPEN / AC-LEGACY-001；VIEW-LEGACY-NA → API-LEGACY-GET /api/legacy。
""",
        encoding="utf-8",
    )
    code, payload = run_gate("--profile", "prd", "--prd", str(legacy_na_prd), "--level", "L3")
    legacy_codes = codes(payload)
    forbidden_legacy_na = {
        "PRD-METRIC-NO-CALIBER", "PRD-FIELD-DICTIONARY-INCOMPLETE",
        "PRD-IMPORT-CONTRACT-INCOMPLETE", "PRD-EXPORT-CONTRACT-INCOMPLETE",
    }
    if forbidden_legacy_na & legacy_codes:
        failures.append(f"legacy N/A surfaces were falsely required: {forbidden_legacy_na & legacy_codes}")

    good_inventory = temp / "stage0-good.yaml"
    good_inventory.write_text(yaml.safe_dump({
        "inventory_status": "inventory_complete",
        "canonical_candidates": ["SRC-PRD-A"],
        "items": [{
            "id": "VIEW-ITEM", "type": "view", "source_ref": "SRC-PRD-A",
            "source_location": "PRD.md#VIEW-ITEM", "classification": "confirmed",
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate("--profile", "stage0", "--inventory", str(good_inventory))
    if code != 0:
        failures.append(f"complete Stage 0 inventory failed: {codes(payload)}")

    reverse_inventory = temp / "stage0-reverse-bad.yaml"
    reverse_inventory.write_text(yaml.safe_dump({
        "inventory_status": "inventory_complete",
        "target_status": "baseline_ready",
        "baseline_requirement_refs": ["REQ-ITEM-001"],
        "canonical_candidates": ["SRC-PRD-A"],
        "items": [{
            "id": "REQ-REVERSE-001", "type": "action", "source_ref": "SRC-PROTOTYPE-A",
            "source_location": "app.html#run", "classification": "inferred", "core_behavior": True,
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate("--profile", "stage0", "--inventory", str(reverse_inventory))
    expected_reverse = {"STAGE0-REVERSE-ID-COLLISION", "STAGE0-MISSING-BASELINE-MAPPING", "STAGE0-INFERRED-NOT-CONFIRMED"}
    if code != 2 or not expected_reverse.issubset(codes(payload)):
        failures.append(f"reverse ID/mapping/batch contract escaped: {codes(payload)}")

    bad_inventory = temp / "stage0-bad.yaml"
    bad_inventory.write_text(yaml.safe_dump({
        "inventory_status": "inventory_complete",
        "canonical_candidates": ["SRC-PRD-A", "SRC-PROTOTYPE-B"],
        "items": [{
            "id": "ACT-UNKNOWN", "type": "action", "source_ref": "SRC-PROTOTYPE-B",
            "source_location": "app.html#button", "classification": "unknown",
            "core_behavior": True,
        }],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate("--profile", "stage0", "--inventory", str(bad_inventory))
    if code != 2 or not {"STAGE0-CORE-UNKNOWN-NOT-OWNED", "STAGE0-MULTIPLE-BASELINES", "STAGE0-FALSE-COMPLETE"}.issubset(codes(payload)):
        failures.append(f"Stage 0 false completeness escaped: {codes(payload)}")

    engineering = temp / "engineering-baseline.md"
    engineering.write_text("# Engineering baseline v1\nowner: architect\n", encoding="utf-8")
    baseline_prd = temp / "PRD.md"
    baseline_prd.write_text(base, encoding="utf-8")
    packet = temp / "MOD-ITEM.md"
    packet_text = "# MOD-ITEM\nREQ-ITEM-001\nAC-ITEM-001\n## qa_projection\npositive, negative, permission, recovery evidence\n"
    packet.write_text(packet_text, encoding="utf-8")
    baseline_hash = hashlib.sha256(base.encode("utf-8")).hexdigest()
    manifest = temp / "handoff.yaml"
    manifest.write_text(yaml.safe_dump({
        "schema_version": "5.3.0",
        "status": "ready_for_implementation",
        "engineering_baseline_ref": engineering.name,
        "baseline": {"version": "1.0", "hash": baseline_hash, "requirement_ref": baseline_prd.name},
        "packets": [{
            "id": "MOD-ITEM", "kind": "mod", "owner": "team-item", "path": packet.name,
            "baseline_hash": baseline_hash,
            "content_sha256": hashlib.sha256(packet_text.encode("utf-8")).hexdigest(),
            "scope_refs": ["REQ-ITEM-001"], "input_refs": [], "output_refs": [],
            "acceptance_refs": ["AC-ITEM-001"],
        }],
        "handoffs": [],
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    code, payload = run_gate("--profile", "agent_handoff", "--manifest", str(manifest))
    if code != 0:
        failures.append(f"valid Agent handoff failed: {codes(payload)}")
    code, payload = run_gate(
        "--profile", "handoff", "--prd", str(baseline_prd),
        "--prototype", str(ROOT / "maintainer/tests/fixtures/gate-prototype-valid.html"),
        "--manifest", str(manifest), "--level", "L2",
    )
    if code != 0:
        failures.append(f"combined PRD/prototype/Agent handoff failed: {codes(payload)}")

    candidate = temp / "candidate.yaml"
    candidate.write_text(yaml.safe_dump({
        "schema_version": "5.3.0", "candidate_id": "CAND-CRM-001", "domain": "crm",
        "statement": "A won opportunity must retain its source lead reference.",
        "candidate_type": "invariant", "status": "proposed", "reuse_scope": "project_only",
        "submitted_by": "product-agent", "decision_owner": "product-owner",
        "reuse_approver": None, "source_refs": ["SRC-CRM-001"], "evidence_refs": ["EVD-CRM-001"],
        "applicability": ["project-demo"], "exclusions": [], "jurisdiction": None,
        "regulatory_version": None, "sensitive_data": False, "created_at": "2026-07-18T12:00:00+08:00",
        "expires_at": None,
    }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(CLI), "candidate", "validate", "--input", str(candidate)],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0:
        failures.append("project-only candidate validation failed: " + result.stdout + result.stderr)

    custom_root = temp / "custom"
    result = subprocess.run(
        [sys.executable, str(CLI), "init-custom", "--output", str(custom_root)],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0 or not (custom_root / "validators" / "my-team.yaml").is_file():
        failures.append("init-custom did not create the private declarative extension skeleton")
    custom_requirements = temp / "custom-requirements"
    result = subprocess.run(
        [
            sys.executable, str(CLI), "init-requirements", "--output", str(custom_requirements),
            "--custom-root", str(custom_root), "--template", "my-team",
        ],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0 or "## 项目私有补充" not in (custom_requirements / "PRD.md").read_text(encoding="utf-8"):
        failures.append("local inherited PRD template did not overlay the official template")
    result = subprocess.run(
        [
            sys.executable, str(CLI), "query-domain", "--domain", "traffic+my-team",
            "--custom-root", str(custom_root), "--format", "yaml",
        ],
        cwd=ROOT, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0 or "local_private" not in result.stdout or "DEC-CONFLICT" not in result.stdout:
        failures.append("official + local private domain composition did not preserve conflict semantics")

    caller_project = temp / "caller-project"
    caller_project.mkdir()
    for command in (
        [sys.executable, str(CLI), "init-custom", "--output", "custom"],
        [
            sys.executable, str(CLI), "init-requirements", "--output", "requirements",
            "--custom-root", "custom", "--template", "my-team",
        ],
    ):
        result = subprocess.run(
            command, cwd=caller_project, text=True, encoding="utf-8", capture_output=True,
        )
        if result.returncode != 0:
            failures.append("five-minute project setup failed outside the Skill repository: " + result.stdout + result.stderr)
    result = subprocess.run(
        [
            sys.executable, str(CLI), "query-domain", "--domain", "traffic+my-team",
            "--custom-root", "custom", "--format", "yaml",
        ],
        cwd=caller_project, text=True, encoding="utf-8", capture_output=True,
    )
    if result.returncode != 0 or "local_private" not in result.stdout:
        failures.append("relative custom domain did not resolve from the caller project")
    result = subprocess.run(
        [
            sys.executable, str(CLI), "gate", "--profile", "prd", "--prd", "requirements/PRD.md",
            "--level", "L2", "--custom-root", "custom", "--format", "json",
        ],
        cwd=caller_project, text=True, encoding="utf-8", capture_output=True,
    )
    try:
        caller_gate = json.loads(result.stdout)
    except json.JSONDecodeError:
        failures.append("relative caller-project gate did not return JSON: " + result.stdout + result.stderr)
    else:
        if "GATE-NOT-FILE" in codes(caller_gate):
            failures.append("relative PRD path was still resolved from the installed Skill directory")

    # New gate output remains schema-valid and exposes consumer/source diagnostics.
    gate_schema = json.loads((ROOT / "schemas" / "gate-result.schema.json").read_text(encoding="utf-8"))
    schema_errors = list(Draft202012Validator(gate_schema).iter_errors(payload))
    if schema_errors:
        failures.append("gate-result schema rejected v5.3 payload: " + schema_errors[0].message)
    if not payload.get("not_proven"):
        failures.append("static gate payload did not disclose its not-proven boundary")


if failures:
    raise SystemExit("\n".join(failures))
print("PASS: v5.3.x authority, clarification, prototype evidence, Stage 0 and Agent handoff are deterministic")
