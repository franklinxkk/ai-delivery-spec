"""Focused regressions for the context-driven v5.4.7 Final review workspace."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from quality_gate import Gate


ONE_LINE_ROUTING_CASES = [
    # prompt, p0_open, concept_explicit, generate_now, state
    ("帮我做一个企业约谈 HTML。", True, False, False, "blocked_by_p0_unknown"),
    ("先做概念 HTML 看效果，允许合理假设。", True, True, True, "concept_candidate"),
    ("不要问，先画一个 HTML，缺口写待确认。", True, True, True, "restricted_concept_candidate"),
    ("附件需求已确认，生成可开发 HTML，不要 PRD。", False, False, True, "implementation_candidate"),
    ("直接生成带标号的评审版 HTML 给开发测试。", True, False, False, "blocked_by_p0_unknown"),
    ("Show me a rough HTML prototype first and list the gaps.", True, True, True, "concept_candidate"),
]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )


def test_one_line_prototype_routing_has_no_unsafe_or_dead_end_combination() -> None:
    assert len(ONE_LINE_ROUTING_CASES) >= 6
    for _prompt, p0_open, concept_explicit, generate_now, state in ONE_LINE_ROUTING_CASES:
        if p0_open and not concept_explicit:
            assert generate_now is False and state == "blocked_by_p0_unknown"
        if p0_open and concept_explicit:
            assert generate_now is True and "concept_candidate" in state
        if not p0_open:
            assert generate_now is True and state == "implementation_candidate"

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    stages = (ROOT / "references/stages.md").read_text(encoding="utf-8")
    prototype = (ROOT / "references/prototype.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "一句话要求 HTML/原型" in skill
    assert "不能停在需求清单或无解释地不出 HTML" in skill
    assert "concept_candidate" in stages and "concept_candidate" in prototype
    assert "只要求 HTML 时不机械附送 PRD" in stages
    assert "帮我做一个企业约谈 HTML" in readme and "不会停在一张需求清单" in readme


def test_review_workspace_docs_require_left_marker_and_three_surface_selection() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    contract = (ROOT / "references/review-workspace.md").read_text(encoding="utf-8")
    schema = (ROOT / "schemas/review-workspace.schema.json").read_text(encoding="utf-8")
    assert "右侧不得出现没有左侧落点的“1/2/3”" in skill
    assert "target、marker、card" in contract
    assert '"selection_contract"' in schema and '"bidirectional_marker_card_target"' in schema


def review_point(ref: str, context: str, target: str, title: str, summary: str, ac: str) -> dict:
    return {
        "ref": ref,
        "subject_ref": target,
        "owner_context_ref": context,
        "marker_required": True,
        "target_ref": target,
        "target_selector": f"[data-review-anchor='{target}']",
        "target_mode": "selector_exactly_one",
        "title": title,
        "business_status": "confirmed",
        "verification_status": "not_run",
        "evidence_origin": "explicit_source",
        "evidence_refs": [],
        "summary": summary,
        "actor_refs": ["ROLE-OPERATOR"],
        "precondition_refs": ["RULE-READY"],
        "visible_result_refs": ["REG-RESULT"],
        "domain_result_refs": ["STATE-SAVED", "EVT-SAVED"],
        "boundary_refs": ["RULE-DUPLICATE"],
        "acceptance_refs": [ac],
        "source_refs": ["SRC-X", "REQ-X"],
    }


def manifest(baseline_hash: str, *, level: str = "R1") -> dict:
    points = [
        review_point(
            "RVP-VIEW-SUBMIT", "VIEW-X", "ACT-X-SUBMIT", "提交记录",
            "校验通过后提交当前记录，并在原页面显示持久化结果。", "AC-X-SUBMIT",
        ),
        review_point(
            "RVP-DRAWER-CONFIRM", "DRAWER-X", "ACT-X-CONFIRM", "确认变更",
            "确认后写入当前变更，并将处理结果返回所属业务页面。", "AC-X-CONFIRM",
        ),
    ]
    return {
        "schema_version": "5.4.7-final",
        "contract_revision": "RC2",
        "workspace_id": "REVIEW-X",
        "language": "zh-CN",
        "baseline": {"version": "1.0", "hash": baseline_hash, "requirement_ref": "prd.md"},
        "workspace": {"review_level": level, "default_tab": "overview", "initial_context_ref": "VIEW-X"},
        "tabs": ["overview", "function_flow", "boundary_acceptance"],
        "context_contract": {
            "resolution": "topmost_business_overlay_else_active_view",
            "allowed_types": ["VIEW", "MODAL", "DRAWER", "POPOVER"],
            "current_context_control": "read_only",
            "resolution_priority": ["product_context_event", "declared_detection_contract", "mutation_observer_reresolve_only"],
            "product_context_event": "product-context-change",
        },
        "product_location_contract": {
            "view_policy": "exactly_one_active_entry_or_declared_exempt",
            "overlay_policy": "inherit_parent_view_location",
            "synchronized_fields": [
                "active_view", "route", "active_menu_path", "expanded_menu_ancestors",
                "breadcrumb", "page_title", "current_context",
            ],
            "review_actions_preserve_location": True,
            "mismatch_result": "block",
        },
        "review_contexts": [
            {
                "context_ref": "VIEW-X", "context_type": "VIEW", "title": "记录列表",
                "detection": {"type": "product_state_equals", "target": "activeView", "expected": "VIEW-X", "overlay_priority": 0},
                "product_location": {
                    "navigation_mode": "menu_bound", "menu_path": ["业务管理", "记录列表"],
                    "active_entry_selector": "[data-view-target='VIEW-X']", "route_ref": "VIEW-X",
                    "breadcrumb": ["业务管理", "记录列表"], "page_title": "记录列表",
                    "parent_view_ref": None, "exemption_reason": None,
                },
                "review_point_refs": ["RVP-VIEW-SUBMIT"],
            },
            {
                "context_ref": "DRAWER-X", "context_type": "DRAWER", "title": "变更确认",
                "detection": {"type": "selector_visible", "target": "[data-review-context-root='DRAWER-X']", "expected": True, "overlay_priority": 10},
                "product_location": {
                    "navigation_mode": "inherit_parent", "menu_path": ["业务管理", "记录列表"],
                    "active_entry_selector": "[data-view-target='VIEW-X']", "route_ref": "VIEW-X#DRAWER-X",
                    "breadcrumb": ["业务管理", "记录列表", "变更确认"], "page_title": "变更确认",
                    "parent_view_ref": "VIEW-X", "exemption_reason": None,
                },
                "review_point_refs": ["RVP-DRAWER-CONFIRM"],
            },
        ],
        "review_points": points,
        "candidate_review_points": [],
        "candidate_diff_contract": {
            "enabled": True, "auto_promote_to_declared": False,
            "candidate_sources": ["product_truth", "page_contracts", "stable_anchors"],
            "high_risk_omission": "block",
        },
        "layout_contract": {
            "desktop_mode": "participate_in_layout", "overlay_product_ui": False,
            "resizable": True, "collapsible": True,
            "compact_mode": "product_review_fullscreen_switcher",
        },
        "product_effect_contract": {
            "review_actions_preserve_product_fingerprint": True,
            "product_fingerprint_fields": [
                "active_view", "route", "active_menu_path", "expanded_menu_ancestors", "breadcrumb", "page_title",
                "overlay_stack", "selected_business_object", "business_state",
                "form_values_hash", "checked_hash", "disabled_hash", "filter_hash", "pagination_hash", "selection_hash",
            ],
            "review_fingerprint_separate": True,
        },
        "target_resolution": {
            "scope": "current_context_root", "visible_only": True, "cardinality": "exactly_one",
            "zero_result": "unresolved", "multiple_result": "block_ambiguous",
        },
        "selection_contract": {
            "ui_grounded_points_require_marker": True,
            "interaction": "bidirectional_marker_card_target",
            "selected_surfaces": ["marker", "card", "target"],
            "target_selected_attribute": "data-review-target-selected",
            "target_focus_style": "visible_focus_ring",
        },
        "progress_contract": {
            "denominator": "declared_applicable_review_points",
            "resolved_states": ["confirmed", "accepted_with_gap"],
            "navigation_advances_progress": False,
        },
        "share_contract": {
            "locator_fields": ["baseline_ref", "context_ref", "review_point_ref", "active_tab"],
            "forbidden_locator_fields": ["journey", "step", "role"],
            "hydrate_on_load": True,
        },
        "review_record_contract": {
            "persistence_required": True,
            "key_fields": ["baseline_ref", "context_ref", "review_point_ref"],
            "dispositions": ["unreviewed", "confirmed", "accepted_with_gap", "blocked"],
            "static_fallback": ["localStorage", "json_export", "json_import"],
            "baseline_mismatch": "do_not_reuse",
        },
        "cold_read_contract": {
            "required_for": ["R1", "R2"],
            "participant_roles": ["product", "frontend", "backend", "qa"],
            "time_limit_seconds": 180,
            "declared_point_recall_min": 0.8,
            "critical_point_recall": 1,
            "status": "pending",
            "evidence_refs": [],
        },
        "machine_models": {
            "flow_refs": ["FLOW-X"], "step_refs": ["STEP-X"], "edge_refs": ["EDGE-X"],
            "state_machine_refs": ["STM-X"], "data_flow_refs": ["DFD-X"],
            "acceptance_refs": ["AC-X-SUBMIT", "AC-X-CONFIRM"], "test_refs": ["TEST-X"],
        },
        "unknown_refs": [],
        "machine_handoff": {"status": "not_requested", "manifest_ref": None, "packet_refs": [], "gap_refs": []},
        "not_proven": ["静态合同不证明浏览器行为、真实系统实现或客户验收。"],
    }


def review_html(document: dict, *, include_tabs: bool = True) -> str:
    point_by_ref = {item["ref"]: item for item in document["review_points"]}
    context_parts = []
    for context in document["review_contexts"]:
        context_ref = context["context_ref"]
        hidden = "" if context_ref == document["workspace"]["initial_context_ref"] else " hidden"
        testid = ' data-testid="page-VIEW-X"' if context_ref == "VIEW-X" else ""
        points = []
        for number, point_ref in enumerate(context["review_point_refs"], start=1):
            point = point_by_ref[point_ref]
            points.append(
                f'<button data-action="{point["target_ref"]}" data-ac="{point["acceptance_refs"][0]}">{point["title"]}</button>'
                f'<button data-action="UIACT-REVIEW-SELECT" data-review-ref="{point_ref}" '
                f'data-review-context="{context_ref}" data-review-number="{number}" aria-current="false">{number}</button>'
            )
        context_parts.append(
            f'<main{testid}{hidden} data-review-context-root="{context_ref}" '
            f'data-review-context-type="{context["context_type"]}">{"".join(points)}</main>'
        )

    cards = []
    for context in document["review_contexts"]:
        for number, point_ref in enumerate(context["review_point_refs"], start=1):
            point = point_by_ref[point_ref]
            cards.append(
                f'<article data-action="UIACT-REVIEW-SELECT" data-review-point="{point_ref}" data-review-context="{context["context_ref"]}" '
                f'data-review-number="{number}" data-review-business-status="{point["business_status"]}" '
                f'data-review-verification-status="{point["verification_status"]}" '
                f'data-review-evidence-origin="{point["evidence_origin"]}" aria-current="false">'
                f'<h3>{point["title"]}</h3><p>{point["summary"]}</p>'
                f'<p>业务：已确认 · 验证：未执行 · 来源：明确来源</p></article>'
            )

    tab_buttons = "".join(
        f'<button data-action="UIACT-REVIEW-TAB" data-review-tab-target="{tab}">{label}</button>'
        for tab, label in (
            ("overview", "总览"), ("function_flow", "功能与流转"),
            ("boundary_acceptance", "边界与验收"),
        )
    )
    tab_sections = f'''
      <nav>{tab_buttons}</nav>
      <section data-review-tab="overview">
        <div data-review-content="goals_success" data-review-owner-tab="overview">目标与成功信号</div>
        <div data-review-content="scope" data-review-owner-tab="overview">范围与非目标</div>
        <div data-review-content="main_chain" data-review-owner-tab="overview">业务主链</div>
      </section>
      <section data-review-tab="function_flow">
        <div data-review-content="current_context" data-review-owner-tab="function_flow">当前上下文</div>
        <div data-review-content="review_points" data-review-owner-tab="function_flow">{"".join(cards)}</div>
        <div data-review-content="visible_domain_results" data-review-owner-tab="function_flow">可见结果与领域结果</div>
      </section>
      <section data-review-tab="boundary_acceptance">
        <div data-review-content="rules" data-review-owner-tab="boundary_acceptance">规则与权限</div>
        <div data-review-content="acceptance_tests" data-review-owner-tab="boundary_acceptance">AC-X-SUBMIT / AC-X-CONFIRM</div>
        <div data-review-content="open_items" data-review-owner-tab="boundary_acceptance">开放项已核对：0 项</div>
      </section>''' if include_tabs else f'<section data-review-r0>{"".join(cards)}</section>'

    workspace = document["workspace"]
    review_controls = '''
      <button data-action="UIACT-REVIEW-TOGGLE" data-ads-act="collapse">收起说明</button>
      <button data-action="UIACT-REVIEW-TOGGLE" data-ads-act="expand">展开说明</button>
      <button data-action="UIACT-REVIEW-SHARE" data-review-share-locator>复制定位</button>
      <button data-action="UIACT-REVIEW-RECORD">提交评审结论</button>
      <button data-action="UIACT-REVIEW-EXPORT">导出记录</button>
      <button data-action="UIACT-REVIEW-IMPORT">导入记录</button>
      <button data-action="UIACT-REVIEW-COMPACT">切换全屏</button>
      <div data-review-progress data-review-progress-denominator="2" data-review-progress-resolved="0">0/2</div>
      <div data-review-records>评审记录</div>'''
    handlers = [
        "ACT-X-NAVIGATE", "ACT-X-SUBMIT", "ACT-X-CONFIRM", "UIACT-REVIEW-SELECT", "UIACT-REVIEW-TOGGLE",
        "UIACT-REVIEW-SHARE", "UIACT-REVIEW-RECORD", "UIACT-REVIEW-EXPORT",
        "UIACT-REVIEW-IMPORT", "UIACT-REVIEW-COMPACT",
    ] + (["UIACT-REVIEW-TAB"] if include_tabs else [])
    registry = ",".join(f'"{item}":()=>true' for item in handlers)
    script = f'''
      const productContextEvent="product-context-change";
      window.__ADS_REVIEW_GATE__={{status:"passed",violations:[]}};
      function resolveProductLocation(){{const observed={{active_menu_path:["业务管理","记录列表"],expanded_menu_ancestors:["业务管理"],breadcrumb:["业务管理","记录列表"],page_title:"记录列表"}},expected={{...observed}},diff={{}};return {{observed,expected,diff,...observed}}}}
      function syncProductLocation(){{return resolveProductLocation()}}
      function assertProductLocationSynchronized(){{const location=syncProductLocation();if(!location.active_menu_path.length)throw new Error("product location missing");return true}}
      function captureProductFingerprint(){{const productLocation=resolveProductLocation();return JSON.stringify({{active_view:"VIEW-X",route:window.location.hash,active_menu_path:productLocation.active_menu_path,expanded_menu_ancestors:productLocation.expanded_menu_ancestors,breadcrumb:productLocation.breadcrumb,page_title:productLocation.page_title,overlay_stack:[],selected_business_object:null,business_state:"ready",form_values_hash:"0",checked_hash:"0",disabled_hash:"0",filter_hash:"0",pagination_hash:"0",selection_hash:"0"}})}}
      function captureReviewFingerprint(){{return JSON.stringify({{tab:document.querySelector("[data-review-workspace]").dataset.reviewActiveTab}})}}
      function assertProductFingerprintInvariant(before,after){{if(before!==after){{window.__ADS_REVIEW_GATE__.status="failed";throw new Error("PROTO-REVIEW-PRODUCT-FINGERPRINT-INVARIANT")}}}}
      function runReviewAction(handler){{const before=captureProductFingerprint();handler();const after=captureProductFingerprint();assertProductFingerprintInvariant(before,after);captureReviewFingerprint()}}
      function resolveCurrentContext(){{assertProductLocationSynchronized();return document.querySelector("[data-review-current-context]").dataset.reviewCurrentContext}}
      const PROTO_REVIEW_OVERLAY_UNDECLARED="PROTO-REVIEW-OVERLAY-UNDECLARED";
      window.addEventListener(productContextEvent,resolveCurrentContext);
      new MutationObserver(()=>resolveCurrentContext()).observe(document.body,{{attributes:true,subtree:true}});
      function currentContextRoot(){{return document.querySelector(`[data-review-context-root="${{resolveCurrentContext()}}"]`)}}
      function isTargetVisible(node){{return !node.hidden}}
      function exactlyOne(nodes){{if(nodes.length!==1)throw new Error("target cardinality");return nodes[0]}}
      function resolveReviewTarget(selector){{const nodes=[...currentContextRoot().querySelectorAll(selector)].filter(isTargetVisible);if(nodes.length===0)throw new Error("PROTO-REVIEW-TARGET-UNRESOLVED");if(nodes.length>1)throw new Error("PROTO-REVIEW-TARGET-AMBIGUOUS");return nodes[0]}}
      function focusReviewTarget(pointRef,selector){{document.querySelectorAll("[data-review-target-selected]").forEach(node=>node.removeAttribute("data-review-target-selected"));document.querySelectorAll("[data-review-ref],[data-review-point]").forEach(node=>node.setAttribute("aria-current",String((node.dataset.reviewRef||node.dataset.reviewPoint)===pointRef)));resolveReviewTarget(selector).setAttribute("data-review-target-selected","true")}}
      const pointSelectors={{"RVP-VIEW-SUBMIT":"[data-action='ACT-X-SUBMIT']","RVP-DRAWER-CONFIRM":"[data-action='ACT-X-CONFIRM']"}};
      const shareLocator=new URLSearchParams({{baseline_ref:"1.0",context_ref:"VIEW-X",review_point_ref:"RVP-VIEW-SUBMIT",active_tab:"overview"}}); location.hash=shareLocator.toString();
      function hydrateLocator(){{return new URLSearchParams(location.hash.slice(1)).get("context_ref")}}
      function saveReviewRecords(value){{localStorage.setItem("review:1.0",JSON.stringify(value))}}
      function loadReviewRecords(){{return JSON.parse(localStorage.getItem("review:1.0")||"[]")}}
      const actionRegistry={{{registry}}};
      actionRegistry["UIACT-REVIEW-SELECT"]=(node)=>{{const pointRef=node.dataset.reviewRef||node.dataset.reviewPoint;focusReviewTarget(pointRef,pointSelectors[pointRef])}};
      document.addEventListener("click",event=>{{const node=event.target.closest("[data-action]");if(!node)return;const handler=actionRegistry[node.dataset.action];if(!handler)return;if(node.dataset.action==="UIACT-REVIEW-TOGGLE")document.body.classList.toggle("ads-collapsed",node.dataset.adsAct==="collapse");if(node.dataset.action.startsWith("UIACT-REVIEW-"))runReviewAction(()=>handler(node));else handler(node)}});
    '''
    return f'''<!doctype html><html lang="zh-CN"><head><style>body{{display:grid;grid-template-columns:minmax(0,1fr) minmax(320px,420px)}}[data-review-workspace]{{min-width:0}}[data-review-target-selected="true"]{{outline:3px solid #6d5dfc;outline-offset:3px}}</style></head><body>
      <nav><button class="active" data-action="ACT-X-NAVIGATE" data-view-target="VIEW-X">记录列表</button></nav>
      {"".join(context_parts)}
      <aside data-review-workspace="REVIEW-X" data-review-level="{workspace["review_level"]}"
        data-review-active-tab="{workspace["default_tab"]}" data-review-current-context="{workspace["initial_context_ref"]}"
        data-review-current-context-control="read-only" data-review-layout="participate-in-layout"
        data-review-overlay-product-ui="false" data-review-resizable="true" data-review-collapsible="true">
        <p data-review-product-location>系统位置：业务管理 / 记录列表</p>
        {tab_sections}{review_controls}
      </aside>
      <script type="application/json" id="review-workspace-manifest">{json.dumps(document, ensure_ascii=False)}</script>
      <script>{script}</script>
    </body></html>'''


def html_gate(path: Path, raw: str) -> Gate:
    path.write_text(raw, encoding="utf-8")
    gate = Gate()
    gate.check_prototype(path, "L2")
    return gate


def review_codes(path: Path, document: dict, *, include_tabs: bool = True) -> set[str]:
    return {item.code for item in html_gate(path, review_html(document, include_tabs=include_tabs)).findings}


def cli_codes(prototype: Path, *runs: Path) -> tuple[int, set[str]]:
    args = [
        str(ROOT / "scripts/ai_delivery_spec_cli.py"), "gate", "--profile", "prototype",
        "--prototype", str(prototype), "--level", "L2", "--format", "json",
    ]
    for path in runs:
        args.extend(("--acceptance-run", str(path)))
    result = run(*args)
    return result.returncode, {item["code"] for item in json.loads(result.stdout)["findings"]}


def test_complete_final_workspace_passes_static_review_contract(tmp_path: Path) -> None:
    codes = review_codes(tmp_path / "review.html", manifest("1" * 64))
    assert not {code for code in codes if code.startswith("PROTO-REVIEW-")}
    assert "PROTO-PRODUCT-LOCATION-MISMATCH" not in codes


def test_product_location_rejects_static_or_unsynchronized_navigation(tmp_path: Path) -> None:
    static_menu = review_html(manifest("1" * 64)).replace(
        '<button class="active" data-action="ACT-X-NAVIGATE" data-view-target="VIEW-X">',
        '<button class="active" disabled data-action="ACT-X-NAVIGATE" data-view-target="VIEW-X">',
        1,
    )
    codes = {item.code for item in html_gate(tmp_path / "disabled-menu.html", static_menu).findings}
    assert "PROTO-PRODUCT-LOCATION-MISMATCH" in codes

    missing_sync = review_html(manifest("1" * 64)).replace("syncProductLocation", "lostProductLocationSync")
    codes = {item.code for item in html_gate(tmp_path / "missing-location-sync.html", missing_sync).findings}
    assert "PROTO-PRODUCT-LOCATION-MISMATCH" in codes


def test_overlay_can_inherit_a_menu_exempt_parent_without_fake_menu_path(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    parent = document["review_contexts"][0]["product_location"]
    parent.update({
        "navigation_mode": "menu_exempt", "menu_path": [], "active_entry_selector": None,
        "exemption_reason": "独立 H5 页面通过扫码或外部链接进入",
    })
    child = document["review_contexts"][1]["product_location"]
    child.update({"menu_path": [], "active_entry_selector": None})
    codes = review_codes(tmp_path / "menu-exempt-parent.html", document)
    assert "PROTO-REVIEW-WORKSPACE-SCHEMA" not in codes
    assert "PROTO-PRODUCT-LOCATION-MISMATCH" not in codes

    child["menu_path"] = ["伪造菜单"]
    codes = review_codes(tmp_path / "menu-exempt-drift.html", document)
    assert "PROTO-PRODUCT-LOCATION-MISMATCH" in codes


def test_final_workspace_rejects_old_modes_and_role_navigation(tmp_path: Path) -> None:
    raw = review_html(manifest("1" * 64)).replace(
        '<nav><button data-action="UIACT-REVIEW-TAB"',
        '<nav data-review-mode="journey" data-review-active-role="product"><button data-action="UIACT-REVIEW-TAB"',
        1,
    )
    codes = {item.code for item in html_gate(tmp_path / "old-nav.html", raw).findings}
    assert "PROTO-REVIEW-LEVEL" in codes


def test_declaration_is_the_only_denominator_and_numbers_restart_per_context(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_contexts"][1]["review_point_refs"] = ["RVP-VIEW-SUBMIT", "RVP-DRAWER-CONFIRM"]
    assert "PROTO-REVIEW-DECLARED-DENOMINATOR" in review_codes(tmp_path / "duplicate-owner.html", document)

    raw = review_html(manifest("1" * 64)).replace(
        'data-review-context="DRAWER-X" data-review-number="1"',
        'data-review-context="DRAWER-X" data-review-number="2"',
    )
    codes = {item.code for item in html_gate(tmp_path / "bad-number.html", raw).findings}
    assert "PROTO-REVIEW-CONTEXT-NUMBERING" in codes


def test_target_resolution_is_scoped_and_exactly_one(tmp_path: Path) -> None:
    raw = review_html(manifest("1" * 64)).replace(
        '<button data-action="ACT-X-SUBMIT"',
        '<button data-action="ACT-X-SUBMIT" data-copy="1">副本</button><button data-action="ACT-X-SUBMIT"',
        1,
    )
    codes = {item.code for item in html_gate(tmp_path / "duplicate-target.html", raw).findings}
    assert "PROTO-REVIEW-TARGET-RESOLUTION" in codes


def test_ui_grounded_review_point_requires_left_marker_and_three_surface_focus(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_points"][0]["marker_required"] = False
    raw = review_html(document)
    codes = {item.code for item in html_gate(tmp_path / "card-only.html", raw).findings}
    assert "PROTO-REVIEW-MARKER-REQUIRED" in codes

    no_focus = review_html(manifest("1" * 64)).replace("focusReviewTarget", "missingTargetFocus")
    codes = {item.code for item in html_gate(tmp_path / "no-target-focus.html", no_focus).findings}
    assert "PROTO-REVIEW-SELECTION-NOT-SYNCED" in codes


def test_status_axes_and_candidate_diff_cannot_be_hidden(tmp_path: Path) -> None:
    raw = review_html(manifest("1" * 64)).replace('data-review-evidence-origin="explicit_source"', '', 1)
    assert "PROTO-REVIEW-STATUS-AXES" in {item.code for item in html_gate(tmp_path / "status.html", raw).findings}

    candidate = review_html(manifest("1" * 64)).replace(
        '</main>', '<button data-action="ACT-X-DELETE" data-ac="AC-X-DELETE">删除</button></main>', 1,
    ).replace('"ACT-X-SUBMIT":()=>true', '"ACT-X-SUBMIT":()=>true,"ACT-X-DELETE":()=>true')
    assert "PROTO-REVIEW-CANDIDATE-DIFF" in {item.code for item in html_gate(tmp_path / "candidate.html", candidate).findings}


def test_runtime_boundaries_layout_and_persistence_are_required(tmp_path: Path) -> None:
    raw = review_html(manifest("1" * 64)).replace("assertProductFingerprintInvariant", "lostInvariant")
    assert "PROTO-REVIEW-PRODUCT-FINGERPRINT-INVARIANT" in {item.code for item in html_gate(tmp_path / "fingerprint.html", raw).findings}

    fixed = review_html(manifest("1" * 64)).replace(
        '[data-review-workspace]{min-width:0}', '[data-review-workspace]{position:fixed;min-width:0}',
    )
    assert "PROTO-REVIEW-LAYOUT-NONOVERLAP" in {item.code for item in html_gate(tmp_path / "fixed.html", fixed).findings}

    no_store = review_html(manifest("1" * 64)).replace("localStorage.setItem", "memoryStore.setItem").replace("localStorage.getItem", "memoryStore.getItem")
    assert "PROTO-REVIEW-RECORD-PERSISTENCE" in {item.code for item in html_gate(tmp_path / "record.html", no_store).findings}


def test_r0_may_omit_visible_tabs_but_keeps_context_and_denominator(tmp_path: Path) -> None:
    document = manifest("1" * 64, level="R0")
    codes = review_codes(tmp_path / "r0.html", document, include_tabs=False)
    assert not {code for code in codes if code.startswith("PROTO-REVIEW-")}


def test_overlay_detection_rejects_ambiguous_topmost_candidates(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_contexts"].append({
        "context_ref": "MODAL-X", "context_type": "MODAL", "title": "冲突浮层",
        "detection": copy.deepcopy(document["review_contexts"][1]["detection"]),
        "product_location": copy.deepcopy(document["review_contexts"][1]["product_location"]),
        "review_point_refs": [],
    })
    assert "PROTO-REVIEW-OVERLAY-DETECTION" in review_codes(tmp_path / "ambiguous-overlay.html", document)


def test_passed_review_point_requires_resolved_acceptance_evidence(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    point = document["review_points"][0]
    point["verification_status"] = "passed"
    point["evidence_refs"] = ["ARUN-X"]
    prototype = tmp_path / "passed.html"
    prototype.write_text(review_html(document), encoding="utf-8")
    code, codes = cli_codes(prototype)
    assert code == 2 and "PROTO-REVIEW-VERIFICATION-ARUN-UNRESOLVED" in codes


def test_legacy_overlay_is_gap_for_visual_review_but_blocked_for_handoff(tmp_path: Path) -> None:
    old = tmp_path / "old.html"
    old.write_text('<body class="review-mode"><main data-testid="page-VIEW-OLD-001"><button data-action="UIACT-REVIEW-SELECT" data-review-id="R1">1</button><aside data-review-id="R1">说明</aside><script>const actions={"UIACT-REVIEW-SELECT":()=>true};</script></main></body>', encoding="utf-8")
    prd = tmp_path / "prd.md"
    prd.write_text("# 基线\n\nREQ-OLD-001 / VIEW-OLD-001 / AC-OLD-001\n", encoding="utf-8")
    gate = Gate()
    gate.check_prototype(old, "L2")
    assert any(item.code == "PROTO-REVIEW-WORKSPACE-LEGACY" and item.severity == "GAP" for item in gate.findings)
    gate.check_handoff(prd, [old], "L2")
    assert any(item.code == "PROTO-REVIEW-WORKSPACE-REQUIRED" and item.severity == "BLOCK" for item in gate.findings)


def test_review_workspace_hash_and_handoff_indicator_match_real_inputs(tmp_path: Path) -> None:
    prd = tmp_path / "prd.md"
    prd.write_text("# 基线\n\nREQ-X / VIEW-X / AC-X-SUBMIT\n", encoding="utf-8")
    document = manifest("2" * 64)
    html = tmp_path / "review.html"
    gate = html_gate(html, review_html(document))
    gate.check_handoff(prd, [html], "L2")
    assert any(item.code == "PROTO-REVIEW-BASELINE-DRIFT" for item in gate.findings)

    baseline_hash = hashlib.sha256(prd.read_text(encoding="utf-8").encode()).hexdigest()
    document["baseline"]["hash"] = baseline_hash
    handoff = tmp_path / "handoff.yaml"
    handoff.write_text(
        f"schema_version: 5.3.0\nstatus: ready_for_implementation\nbaseline:\n  version: '1.0'\n  hash: {baseline_hash}\n  requirement_ref: prd.md\npackets:\n  - id: MOD-X\n    kind: mod\n    owner: team\n    path: packets/core.md\n    baseline_hash: {baseline_hash}\n    scope_refs: [REQ-X]\n    acceptance_refs: [AC-X-SUBMIT]\nhandoffs: []\n",
        encoding="utf-8",
    )
    document["machine_handoff"] = {"status": "ready", "manifest_ref": "handoff.yaml", "packet_refs": ["MOD-X"], "gap_refs": []}
    gate = html_gate(html, review_html(document))
    gate.check_review_manifest_binding(handoff)
    assert not {item.code for item in gate.findings if item.code.startswith("PROTO-REVIEW-HANDOFF-")}


def test_repaired_cli_and_query_surfaces_are_truthful() -> None:
    candidate = run("scripts/ai_delivery_spec_cli.py", "candidate", "--help")
    assert candidate.returncode == 0 and "validate" in candidate.stdout and "校验本地候选" in candidate.stdout
    section = run("scripts/query_domain.py", "--domain", "crm", "--section", "Domain Events", "--format", "markdown")
    assert section.returncode == 0 and "Domain Events" in section.stdout and "Compact context" not in section.stdout


def test_prototype_cannot_label_one_value_confirmed_and_unknown(tmp_path: Path) -> None:
    path = tmp_path / "conflict.html"
    raw = '<main data-testid="page-VIEW-METRIC-001"><div data-metric="METRIC-RATE-001" data-metric-status="confirmed" data-unk="UNK-RATE-001" data-unk-priority="P1" data-unk-owner="产品负责人" data-unk-blocks-stage="baseline" data-unk-affected-refs="METRIC-RATE-001" data-unk-fallback="不展示该指标">完成率</div></main>'
    gate = html_gate(path, raw)
    assert any(item.code == "PROTO-UNKNOWN-CONFIRMED-CONFLICT" for item in gate.findings)


def test_stage0_and_l1_skeletons_cannot_pass_as_content(tmp_path: Path) -> None:
    gate = Gate()
    gate.check_stage0(ROOT / "references/templates/stage0-inventory-template.yaml")
    assert any(item.code == "STAGE0-PLACEHOLDER" and item.severity == "BLOCK" for item in gate.findings)
    prd = tmp_path / "l1.md"
    prd.write_text('---\ndocument_language: zh-CN\ndelivery_level: L1\nactivated_facets: ui\n---\n# 需求卡\n## 来源、问题与价值\n来源与价值已确认。\n## 目标、范围与非目标\n提交单条记录，不做批量。\n## 角色、用户故事与权限\n业务员提交，管理员查看。\n## 旅程、流程、异常与状态\n失败保留输入，成功可见。\n## 验收与测试\n校验成功和拒绝路径。\n## 未知项与升级判断\n无开放未知项。\n', encoding="utf-8")
    gate = Gate()
    gate.check_prd(prd, "L1")
    codes = {item.code for item in gate.findings}
    assert "PRD-L1-SECTION-MISSING" in codes and "PRD-BAD-ACTIVATED-FACETS" in codes


def test_baseline_status_cannot_contradict_draft_version_or_document_control(tmp_path: Path) -> None:
    prd = tmp_path / "draft-claimed-baseline.md"
    prd.write_text(
        """---
document_language: zh-CN
delivery_level: L2
baseline_version: 0.1-draft
status: baseline
open_p0_unknown_ids: []
unknowns: []
activated_facets: []
---
# 示例需求

| 项目 | 内容 |
|---|---|
| 状态 | 草稿（待评审基线） |
""",
        encoding="utf-8",
    )
    gate = Gate()
    gate.check_prd(prd, "L2")
    assert "PRD-STATUS-CONTRADICTION" in {item.code for item in gate.findings}


def test_rc2_candidate_is_physically_separate_from_declaration(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["candidate_review_points"] = [{
        "candidate_id": "CAND-VIEW-X-SAVE-LEGACY",
        "owner_context_ref": "VIEW-X",
        "subject_ref": "PROTO-OBS-ACT-SAVE-LEGACY",
        "candidate_type": "动作",
        "label": "保存",
        "selector": "[data-action='save-legacy']",
        "cardinality_policy": "exactly_one",
        "candidate_reason": ["state_guard", "permission_guard"],
        "business_status": "gap",
        "evidence_origin": "prototype_inferred",
        "unknown_ref": "UNK-VIEW-X-SAVE-LEGACY",
    }]
    before = sum(len(item["review_point_refs"]) for item in document["review_contexts"])
    codes = review_codes(tmp_path / "candidate.html", document)
    after = sum(len(item["review_point_refs"]) for item in document["review_contexts"])
    assert before == after == 2
    assert "PROTO-REVIEW-DECLARED-DENOMINATOR" not in codes


def test_rc2_rejects_confirmed_prototype_inference(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_points"][0]["evidence_origin"] = "prototype_inferred"
    codes = review_codes(tmp_path / "inferred-confirmed.html", document)
    assert "PROTO-REVIEW-WORKSPACE-SCHEMA" in codes or "PROTO-REVIEW-STATUS-AXES" in codes


def test_rc2_requires_separate_rvp_record_identity(tmp_path: Path) -> None:
    document = manifest("1" * 64)
    document["review_points"][0]["ref"] = "RP-VIEW-SUBMIT"
    document["review_contexts"][0]["review_point_refs"] = ["RP-VIEW-SUBMIT"]
    codes = review_codes(tmp_path / "legacy-review-id.html", document)
    assert "PROTO-REVIEW-TRUTH-ID" in codes


def test_rc2_requires_expand_button_and_hydration(tmp_path: Path) -> None:
    raw = review_html(manifest("1" * 64)).replace('data-ads-act="expand"', 'data-ads-act="missing"', 1)
    codes = {item.code for item in html_gate(tmp_path / "no-expand.html", raw).findings}
    assert "PROTO-REVIEW-COLLAPSE-ROUNDTRIP" in codes
    raw = review_html(manifest("1" * 64)).replace("function hydrateLocator()", "function omittedHydration()", 1)
    codes = {item.code for item in html_gate(tmp_path / "no-hydrate.html", raw).findings}
    assert "PROTO-REVIEW-SHARE-LOCATOR" in codes
