"""Regression tests for the v5.4.1 Human-First and brownfield gate fixes."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "validators"))

from quality_gate import Gate  # noqa: E402
from scan_prototype_css import scan  # noqa: E402
from prd_structure import _section_bodies  # noqa: E402


def codes(gate: Gate) -> set[str]:
    return {item.code for item in gate.findings}


class MemoryGate(Gate):
    def __init__(self, documents: dict[str, str]):
        super().__init__()
        self.documents = {str(Path(name)): value for name, value in documents.items()}

    def read(self, path: Path) -> str:
        return self.documents[str(path)]


def test_h2_uses_full_h3_subtree() -> None:
    raw = """## 4. 端到端角色旅程

### 4.1 企业旅程 FLOW-DEMO-001
ROLE-USER 进入页面，提交后得到可见成功结果；失败时保留输入并恢复。

## 5. 业务流程与状态
正文。
"""
    sections = dict(_section_bodies(raw))
    assert "ROLE-USER" in sections["4. 端到端角色旅程"]
    assert "FLOW-DEMO-001" in sections["4. 端到端角色旅程"]


def test_todo_inside_stable_id_is_not_unknown_marker() -> None:
    gate = Gate()
    raw = """---
open_p0_unknown_ids: []
---
## 模块
REG-RPT-TODO 是待办区域，不是 TODO 占位符。
"""
    gate._check_unknowns(Path("prd.md"), raw, gate._frontmatter(raw), stage="specify", scope_refs=set())
    assert "PRD-UNTRACKED-UNKNOWN" not in codes(gate)


def test_uiact_is_allowed_without_business_ac() -> None:
    path = Path("prototype.html")
    raw = """<!doctype html><html><head><style>
.btn{border:1px solid #1677ff;padding:8px 12px;background:#fff}.page{display:block}.hidden{display:none!important}
</style></head><body>
<section class="page" data-testid="page-VIEW-DEMO-001" data-state="default">
<div data-testid="region-REG-DEMO-001"><button class="btn" data-action="UIACT-TAB-NEXT">下一页签</button>
<button class="btn" data-action="ACT-DEMO-SAVE" data-ac="AC-DEMO-001">保存</button></div></section>
<script>document.addEventListener('click',e=>{const el=e.target.closest('[data-action]');if(!el)return;switch(el.dataset.action){case 'UIACT-TAB-NEXT':document.body.setAttribute('data-state','tab-next');break;case 'ACT-DEMO-SAVE':document.body.setAttribute('data-state','saved');break;}});</script>
</body></html>"""
    gate = MemoryGate({str(path): raw})
    gate.check_prototype(path, "L3")
    found = codes(gate)
    assert "PROTO-UNSTABLE-ACTION" not in found
    assert "PROTO-ACTION-NO-AC" not in found
    assert "PROTO-UNHANDLED-ACTION" not in found


def test_binding_terms_are_checked_across_handoff() -> None:
    prd = Path("PRD.md")
    prototype = Path("prototype.html")
    prd_raw = """---
page_contract_view_ids: [VIEW-DEMO-001]
binding_terms: [道路运输经营许可证]
---
REQ-DEMO-001 ACT-DEMO-001 AC-DEMO-001
- id: AC-DEMO-001
"""
    prototype_raw = '<section data-testid="page-VIEW-DEMO-001">行业经营许可</section>'
    gate = MemoryGate({str(prd): prd_raw, str(prototype): prototype_raw})
    gate.check_handoff(prd, [prototype], "L2")
    assert "HANDOFF-BINDING-TERM-MISSING" in codes(gate)


def test_demo_and_local_iframe_are_blocked() -> None:
    path = Path("prototype.html")
    raw = '<section data-testid="page-VIEW-DEMO-001">验收场景<iframe src="child.html"></iframe></section>'
    gate = MemoryGate({str(path): raw})
    gate.check_prototype(path, "L2")
    found = codes(gate)
    assert "PROTO-DEMO-SCAFFOLDING-VISIBLE" in found
    assert "PROTO-NESTED-PRODUCT-IFRAME" in found

def test_css_scans_unstyled_controls_and_tiny_primary_text() -> None:
    findings = scan("""<style>.primary-btn{color:#fff}button{font-size:9px}</style><button class="btn primary">保存</button>""")
    kinds = {item["kind"] for item in findings}
    assert "unstyled-control-class" in kinds
    assert "unreadable-type-scale" in kinds


def test_state_columns_reject_api_ids() -> None:
    gate = Gate()
    raw = """REQ-DEMO-001 AC-DEMO-001
| 当前状态 | 动作 | 下一状态 |
|---|---|---|
| 待处理 | 复检 | API-RISK-RECHECK 复检 |
"""
    gate._check_testability(Path("PRD.md"), raw, {}, "L2")
    assert "PRD-STATE-SEMANTIC-POLLUTION" in codes(gate)


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"PASS: {len(tests)} v5.4.1 Human-First gate regressions")
