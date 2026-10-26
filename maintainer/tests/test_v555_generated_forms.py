"""Independent binding/definition examples; generated samples are not fixtures."""

import re
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from extract_interaction_ledger import _mask_javascript_literals
from quality_gate import Gate
from quality_gate import localized_finding
from scan_prototype_css import scan
from validators.gate_prototype_checks import _id_bound_actions
from validators.validate_prd_semantics import check_dangling_refs, collect_defined_ids


BUTTON = '<button id="commit" type="button" data-action="ACT-COMMIT">提交</button>'
ARROW_HELPER = "const $=id=>document.getElementById(id);"
FUNCTION_HELPER = "function byId(id){return document.getElementById(id);}"


@pytest.mark.parametrize("helper,receiver", [
    ("", 'document.getElementById("commit")'),
    (ARROW_HELPER, '$("commit")'),
    (FUNCTION_HELPER, 'byId("commit")'),
])
@pytest.mark.parametrize("binding", [
    '.addEventListener("click",()=>{document.body.textContent="保存";});',
    '.onclick=function(){document.body.textContent="保存";};',
    '.addEventListener("click",save);function save(){document.body.textContent="保存";}',
])
def test_real_id_bindings_are_recognized(helper, receiver, binding):
    assert _id_bound_actions(BUTTON, helper + receiver + binding) == {"ACT-COMMIT"}


@pytest.mark.parametrize("js", [
    "",  # no handler
    'document.getElementById("missing").onclick=()=>{save();};',
    'document.getElementById("commit").onclick=null;',
    'document.getElementById("commit").addEventListener("click",undefinedHandler);',
    'document.getElementById("commit").addEventListener("click",()=>{});',
    'const $=id=>({});$("commit").onclick=()=>{save();};',
    'const $=id=>document.getElementById(id)||other;$("commit").onclick=()=>{save();};',
    ARROW_HELPER + '$=other;$("commit").onclick=()=>{save();};',
    ARROW_HELPER + 'function f($){$("commit").onclick=()=>{save();};}',
    ARROW_HELPER + 'const f=($)=>$("commit").addEventListener("click",()=>{save();});',
    'function privateSetup(){' + ARROW_HELPER + '}$("commit").onclick=()=>{save();};',
    '// document.getElementById("commit").onclick=()=>{save();};',
    'const example=\'document.getElementById("commit").onclick=()=>{save();};\';',
])
def test_absent_unsafe_or_non_executable_bindings_stay_unproven(js):
    assert _id_bound_actions(BUTTON, js) == set()


def test_static_target_must_exist_uniquely_and_be_live_markup():
    js = 'document.getElementById("commit").onclick=()=>{save();};'
    for html in [BUTTON + BUTTON, "<template>" + BUTTON + "</template>", "<!--" + BUTTON + "-->"]:
        assert _id_bound_actions(html, js) == set()


def test_native_form_submit_covers_only_submit_controls_owned_by_that_form():
    html = '''<form id="edit">
      <button data-action="ACT-SAVE">保存</button>
      <button type="button" data-action="ACT-CANCEL">取消</button>
      <input type="submit" data-action="ACT-INPUT-SAVE">
      <button form="other" data-action="ACT-OTHER">别的表单</button>
    </form><form id="other"></form>
    <button form="edit" data-action="ACT-EXTERNAL-SAVE">保存</button>'''
    js = ARROW_HELPER + '$("edit").addEventListener("submit",e=>{e.preventDefault();save();});'
    assert _id_bound_actions(html, js) == {"ACT-SAVE", "ACT-INPUT-SAVE", "ACT-EXTERNAL-SAVE"}
    assert not _id_bound_actions(html, js.replace('$("edit")', '$("missing")'))


def test_id_delegation_is_limited_to_target_derived_branch_and_actual_container():
    html = '<div id="inside">' + BUTTON + '</div><button id="outside" data-action="ACT-OUTSIDE">外部</button>'
    js = '''document.getElementById("inside").addEventListener("click",function(e){
      const b=e.target.closest("button");
      if(b.id==="commit"){save();}
      if(b.id==="outside"){save();}
      if(unrelated.id==="outside"){save();}
    });'''
    assert _id_bound_actions(html, js) == {"ACT-COMMIT"}
    assert _id_bound_actions(html, js.replace('document.getElementById("inside")', "document")) == {"ACT-COMMIT", "ACT-OUTSIDE"}
    assert not _id_bound_actions(html, js.replace('b.id==="commit"', 'b.id==="missing"'))


def test_delegation_cannot_be_supplied_by_comment_or_string():
    js = '''document.addEventListener("click",e=>{
      const b=e.target.closest("button");
      // if(b.id==="commit"){save();}
      const example='if(b.id==="commit"){save();}';
      log(example);
    });'''
    assert not _id_bound_actions(BUTTON, js)


def test_regex_quotes_comments_and_braces_do_not_swallow_later_handlers():
    prefix = r'''const escape=s=>s.replace(/[&<>"']/g,x=>x);const slash=/[/*{}]/g;'''
    js = ARROW_HELPER + prefix + '$("commit").onclick=()=>{save();};'
    assert _id_bound_actions(BUTTON, js) == {"ACT-COMMIT"}
    masked = _mask_javascript_literals(js)
    assert len(masked) == len(js)
    assert "[/*{}]" not in masked
    assert 'onclick=()=>{save();}' in masked


def test_division_remains_executable_code_and_newlines_keep_offsets():
    js = 'const ratio=total/count; const half="4"/2; const objectRatio={value:4}/2;\nconst r=/["{}]/g;\nrun(ratio/2);'
    masked = _mask_javascript_literals(js)
    assert "total/count" in masked
    assert "/2" in masked
    assert "run(ratio/2)" in masked
    assert "{value:4}/2" in masked
    assert len(masked) == len(js)
    assert [m.start() for m in re.finditer("\n", masked)] == [m.start() for m in re.finditer("\n", js)]


@pytest.mark.parametrize("js,handled", [
    (ARROW_HELPER + '$("commit").onclick=()=>{document.body.textContent="保存";};', True),
    ('document.getElementById("missing").onclick=()=>{document.body.textContent="保存";};', False),
    ('document.body.textContent="静态内容";', False),
])
def test_actual_gate_preserves_real_unhandled_action_block(tmp_path, js, handled):
    path = tmp_path / "prototype.html"
    path.write_text('<main data-testid="page-VIEW-X">' + BUTTON + '</main><script>' + js + '</script>', encoding="utf-8")
    gate = Gate()
    gate.check_prototype(path, "L2")
    failures = [f for f in gate.findings if f.code == "PROTO-UNHANDLED-ACTION" and f.ref == "ACT-COMMIT"]
    assert bool(failures) is not handled
    assert all(f.severity == "BLOCK" for f in failures)


@pytest.mark.parametrize("line", [
    "场景编号：AC-SAVE", "场景编号: `AC-SAVE`", "- 场景编号：**AC-SAVE**", "**场景编号**：AC-SAVE",
])
def test_labelled_scenario_defines_only_its_own_id(line):
    text = "### 保存草稿\n" + line + "\n前提：输入合法。\n预期：保存草稿。\n参见 AC-SAVE。"
    assert "AC-SAVE" in collect_defined_ids(text)
    assert not check_dangling_refs(text)


@pytest.mark.parametrize("line", [
    "参见 AC-SAVE。", "备注：场景编号：AC-SAVE", "场景编号：参见 AC-SAVE。", "```text\n场景编号：AC-SAVE\n```",
])
def test_mentions_and_navigation_are_not_scenario_definitions(line):
    text = line + "\n参见 AC-SAVE。"
    assert "AC-SAVE" not in collect_defined_ids(text)
    assert any(f.code == "PRD-DANGLING-REF" and f.severity == "BLOCK" for f in check_dangling_refs(text))


def test_later_reference_on_scenario_line_is_not_promoted_to_definition():
    text = "场景编号：AC-SAVE；参见 AC-MISSING。"
    assert collect_defined_ids(text) == {"AC-SAVE"}
    assert any(f.code == "PRD-DANGLING-REF" and f.severity == "BLOCK" and f.ref.startswith("AC-MISSING@") for f in check_dangling_refs(text))


def css_prototype(tmp_path, css, js=None):
    if js is None:
        js = 'document.getElementById("commit").addEventListener("click",()=>{document.getElementById("commit").textContent="Saved";document.body.dataset.state="saved";});'
    path = tmp_path / "css-prototype.html"
    path.write_text('<style>' + css + '</style><main data-testid="page-VIEW-X" data-state="ready">'
                    '<section data-testid="region-REG-X"><label class="field"><input aria-invalid="true"></label>'
                    + BUTTON + '</section></main><script>' + js + '</script>', encoding="utf-8")
    gate = Gate()
    gate.check_prototype(path, "L2")
    return path, gate.findings


def test_important_override_requires_review_without_claiming_function_failure(tmp_path):
    css = '.field input{border:1px solid gray}[aria-invalid="true"]{border-color:red!important}'
    _path, findings = css_prototype(tmp_path, css)
    finding = next(f for f in findings if f.code == "PROTO-CSS-IMPORTANT-POLLUTION")
    assert finding.severity == "GAP"
    assert finding.ref == '[aria-invalid="true"]'
    assert 'border-color:red!important' in finding.message
    for language in ["zh-CN", "en-US"]:
        data = localized_finding(finding, language)
        assert ('人工' in data['message'] or 'Review' in data['message'])
        assert 'focus' in data['fix_en'] and '焦点' in data['fix_zh']
        assert 'remove global' not in data['how_to_fix']
    assert not any(f.severity == "BLOCK" for f in findings)


def test_css_scanner_standalone_shape_and_exit_are_unchanged(tmp_path):
    css = '[aria-invalid="true"]{border-color:red!important}'
    assert scan(css) == [{'kind': 'important-pollution', 'selector': '[aria-invalid="true"]', 'detail': 'border-color:red!important'}]
    path = tmp_path / 'standalone.css'
    path.write_text(css, encoding='utf-8')
    script = Path(__file__).resolve().parents[2] / 'scripts/scan_prototype_css.py'
    run = subprocess.run([sys.executable, str(script), str(path), '--format', 'json'],
                         env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, capture_output=True, text=True, encoding='utf-8', timeout=15)
    assert run.returncode == 1
    assert json.loads(run.stdout) == {'findings': scan(css)}


@pytest.mark.parametrize('css,js,expected', [
    ('[aria-invalid="true"]{border-color:red!important}', 'document.body.dataset.state="ready";', 'PROTO-UNHANDLED-ACTION'),
    ('[aria-invalid="true"]{border-color:red!important}', 'document.getElementById("commit").onclick=()=>{document.body.dataset.state="saved";};const broken=;', 'PROTO-JS-SYNTAX'),
    ('.hidden{opacity:0}', None, 'PROTO-CSS-HIDDEN-WITHOUT-DISPLAY-NONE'),
    ('input{font-size:8px!important}', None, 'PROTO-CSS-UNREADABLE-TYPE-SCALE'),
])
def test_css_review_gap_does_not_downgrade_other_failures(tmp_path, css, js, expected):
    _path, findings = css_prototype(tmp_path, css, js)
    assert any(f.code == expected and f.severity == 'BLOCK' for f in findings)
    assert all(f.severity == 'GAP' for f in findings if f.code == 'PROTO-CSS-IMPORTANT-POLLUTION')
