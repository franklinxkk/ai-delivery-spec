"""Focused regressions for literal data-action anchors on created DOM controls."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_interaction_ledger import (  # noqa: E402
    extract_dynamic_anchor_actions,
    inspect_runtime_action_assignments,
)
from quality_gate import Gate  # noqa: E402
from scan_prototype_css import scan as scan_css  # noqa: E402


def _codes(source: str) -> tuple[set[str], set[str]]:
    path = ROOT / "maintainer" / "tests" / "fixtures" / "in-memory-dynamic-anchor.html"
    gate = Gate()
    gate._cache[path.resolve()] = source
    gate.check_prototype(path, "L2")
    codes = {item.code for item in gate.findings}
    orphans = {item.ref for item in gate.findings if item.code == "PROTO-ORPHAN-HANDLER"}
    return codes, orphans


def test_literal_actions_on_created_controls_are_static_inventory() -> None:
    source = """<!doctype html><main data-testid="page-VIEW-DEMO"></main><script>
function buildControls(){const a=document.createElement('button');a.setAttribute('data-action','ACT-LITERAL-SET');const b=document.createElement('button');b.dataset.action='UIACT-LITERAL-DATASET';document.querySelector('main').append(a,b)}
const actionHandlers={'ACT-LITERAL-SET':()=>1,'UIACT-LITERAL-DATASET':()=>1,'ACT-REAL-ORPHAN':()=>1};
document.addEventListener('click',e=>{const n=e.target.closest('[data-action]');if(n)actionHandlers[n.dataset.action]?.()});buildControls();
</script>"""
    safe, unsafe = inspect_runtime_action_assignments(source)
    assert safe == ["ACT-LITERAL-SET", "UIACT-LITERAL-DATASET"]
    assert unsafe == []
    assert extract_dynamic_anchor_actions(source) == safe

    codes, orphans = _codes(source)
    assert "PROTO-RUNTIME-ACTION-RETROFIT" not in codes
    assert "ACT-LITERAL-SET" not in orphans
    assert "UIACT-LITERAL-DATASET" not in orphans
    assert "ACT-REAL-ORPHAN" in orphans


def test_variable_concat_and_existing_node_assignments_remain_blocked() -> None:
    source = """<!doctype html><main data-testid="page-VIEW-DEMO"><button id="existing">已有控件</button></main><script>
const variableAction='ACT-VARIABLE',variableControl=document.createElement('button');variableControl.setAttribute('data-action',variableAction);
const suffix='CONCAT',concatControl=document.createElement('button');concatControl.dataset.action='ACT-'+suffix;
const existing=document.querySelector('#existing');existing.setAttribute('data-action','ACT-EXISTING-SET');const existingAgain=document.querySelector('#existing');existingAgain.dataset.action='ACT-EXISTING-DATASET';
const actionHandlers={'ACT-VARIABLE':()=>1,'ACT-CONCAT':()=>1,'ACT-EXISTING-SET':()=>1,'ACT-EXISTING-DATASET':()=>1};
</script>"""
    safe, unsafe = inspect_runtime_action_assignments(source)
    assert safe == []
    assert len(unsafe) == 4
    assert extract_dynamic_anchor_actions(source) == []

    codes, orphans = _codes(source)
    assert "PROTO-RUNTIME-ACTION-RETROFIT" in codes
    assert {
        "ACT-VARIABLE",
        "ACT-CONCAT",
        "ACT-EXISTING-SET",
        "ACT-EXISTING-DATASET",
    } <= orphans


def test_freshness_is_isolated_by_function_scope_and_latest_local_write() -> None:
    source = """<main data-testid="page-VIEW-X"><button id="x"></button></main><script>
function seed(){const a=document.createElement('button');return a}function use(a){a.setAttribute('data-action','ACT-CROSS')}
function seed2(){const b=document.createElement('button');return b}const use2=b=>{b.dataset.action='ACT-ARROW'};
const c=document.createElement('button');[c].map(c=>c.setAttribute('data-action','ACT-EXPR'));
const d=document.createElement('button');this.d.setAttribute('data-action','ACT-MEMBER');const E=document.createElement('button');e.dataset.action='ACT-CASE';
{const f=document.createElement('button')}f.dataset.action='ACT-BLOCK';
const g=document.createElement('button');try{throw 1}catch(g){g.dataset.action='ACT-CATCH'}
for(let h=document.createElement('button');false;){}h.dataset.action='ACT-FOR';
let i=document.createElement('button');i&&=document.querySelector('#x');i.dataset.action='ACT-LOGICAL';
let j=document.createElement('button');[j]=[document.querySelector('#x')];j.dataset.action='ACT-DESTRUCT';
let k=document.createElement('button');for(k of [document.querySelector('#x')]){k.dataset.action='ACT-FOROF'}
function re(){let l=document.createElement('button');l=document.querySelector('#x');l.dataset.action='ACT-REASSIGN'}
function ok(){const m=document.createElement('button');m.setAttribute('data-action','ACT-FRESH')}
function okv(){if(1){var n=document.createElement('button')}n.dataset.action='ACT-VAR'}
function okc(){const o=document.createElement('button');// o&&=document.querySelector('#x')
o.dataset.action='ACT-COMMENT'}function oks(){const p=document.createElement('button');const note='for(p of nodes)';p.dataset.action='ACT-STRING'}
function okb(){const q=document.createElement('button');/* q=document.querySelector('#x') */q.dataset.action='ACT-BLOCK-COMMENT'}function okp(){const r=document.createElement('button');r.title='x';r.dataset.action='ACT-PROPERTY'}
const actionHandlers={'ACT-CROSS':()=>1,'ACT-ARROW':()=>1,'ACT-EXPR':()=>1,'ACT-MEMBER':()=>1,'ACT-CASE':()=>1,'ACT-BLOCK':()=>1,'ACT-CATCH':()=>1,'ACT-FOR':()=>1,'ACT-LOGICAL':()=>1,'ACT-DESTRUCT':()=>1,'ACT-FOROF':()=>1,'ACT-REASSIGN':()=>1,'ACT-FRESH':()=>1,'ACT-VAR':()=>1,'ACT-COMMENT':()=>1,'ACT-STRING':()=>1,'ACT-BLOCK-COMMENT':()=>1,'ACT-PROPERTY':()=>1};
</script>"""
    safe, unsafe = inspect_runtime_action_assignments(source)
    assert set(safe) == {"ACT-FRESH", "ACT-VAR", "ACT-COMMENT", "ACT-STRING", "ACT-BLOCK-COMMENT", "ACT-PROPERTY"}
    assert len(unsafe) == 12
    assert extract_dynamic_anchor_actions(source) == safe

    codes, orphans = _codes(source)
    assert "PROTO-RUNTIME-ACTION-RETROFIT" in codes
    assert {
        "ACT-CROSS", "ACT-ARROW", "ACT-EXPR", "ACT-MEMBER", "ACT-CASE", "ACT-BLOCK",
        "ACT-CATCH", "ACT-FOR", "ACT-LOGICAL", "ACT-DESTRUCT", "ACT-FOROF", "ACT-REASSIGN",
    } <= orphans
    assert not {"ACT-FRESH", "ACT-VAR", "ACT-COMMENT", "ACT-STRING", "ACT-BLOCK-COMMENT", "ACT-PROPERTY"} & orphans


def test_existing_t09_factory_exemption_stays_narrow() -> None:
    source = """<!doctype html><main data-testid="page-VIEW-DEMO"></main><script>
const actionHandlers={'ACT-FACTORY-RUN':()=>1,'ACT-FACTORY-DEAD':()=>1};
const act=(id)=>'<button data-'+'action="'+id+'">run</button>';
document.querySelector('main').innerHTML=act('ACT-FACTORY-RUN');
</script>"""
    assert extract_dynamic_anchor_actions(source) == ["ACT-FACTORY-RUN"]
    codes, orphans = _codes(source)
    assert "PROTO-DYNAMIC-ANCHOR-CONSTRUCTION" in codes
    assert "ACT-FACTORY-RUN" not in orphans
    assert "ACT-FACTORY-DEAD" in orphans


def test_hidden_utility_checks_use_exact_class_tokens() -> None:
    kinds = lambda html: {item["kind"] for item in scan_css(html)}
    prefixed = '<style>.is-hidden{display:none}</style><div class="is-hidden">内容</div>'
    assert not kinds(prefixed) & {
        "missing-hidden-rule", "hidden-without-display-none", "hidden-selector-pollution",
    }
    exact = '<style>.is-hidden{display:none}</style><div class="hidden">内容</div>'
    assert "missing-hidden-rule" in kinds(exact)
