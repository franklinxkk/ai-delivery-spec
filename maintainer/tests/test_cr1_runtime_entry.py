"""Bounded entry diagnosis; browser behavior is checked separately, not inferred."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts' / 'validators'))
from gate_prototype_checks import inline_handler_collisions


@pytest.mark.parametrize('tag,event', [('button', 'onclick'), ('input', 'onchange'), ('select', 'onchange')])
def test_native_property_risk_is_located(tag, event):
    raw = f'<main>\n<{tag} id="save" {event}="return form(1)">Save</{tag}></main>'
    result, = inline_handler_collisions(raw)
    assert (result.line, result.column, result.tag, result.identifier, result.event, result.callee, result.origin) == (2, 1, tag, 'save', event, 'form', 'DOM')


@pytest.mark.parametrize('raw', [
    '<button onclick="window.form()">Save</button>',
    '<button onclick="app.form()">Save</button>',
    '<button onclick="const form=()=>1; form()">Save</button>',
    '<button onclick="form(); function form(){return 1}">Save</button>',
    '<div onclick="form()">Save</div>',
    '<!-- <button onclick="form()">Save</button> -->',
    '<script>const text = \'<button onclick="form()">Save</button>\';</script>',
    '<button onclick="save()" title="form()">Save</button>',
    '<button onclick="window.close()">Close</button>',
    '<button onclick="app.close()">Close</button>',
    '<button onclick="const close=()=>1; close()">Close</button>',
    '<button onclick="close(); function close(){return 1}">Close</button>',
    '<button onclick="close(); var close=()=>1">Close</button>',
    '<script>button.addEventListener("click",close); function close(){}</script>',
    '<script>const unused = \'<button onclick="close()">Close</button>\';</script>',
    '<!-- <button onclick="close()">Close</button> -->',
    '<script>// drawer.innerHTML=\'<button onclick="close()">Close</button>\';\n</script>',
    '<script>/* drawer.innerHTML=\'<button onclick="close()">Close</button>\'; */</script>',
    '<script>const unused = `drawer.innerHTML=\'<button onclick="close()">Close</button>\'`;</script>',
    '<script type="application/json">{"innerHTML":"<button onclick=\\"close()\\">Close</button>"}</script>',
    '<script>drawer.innerHTML=\'<button onclick="app.close()">Close</button>\';</script>',
    '<script>drawer.innerHTML=\'<button onclick="close(); function close(){}">Close</button>\';</script>',
])
def test_distinct_scopes_and_nonhandlers_are_not_this_finding(raw):
    assert inline_handler_collisions(raw) == []


def test_prerelease_identity_does_not_collapse_to_stable(tmp_path):
    sys.path.insert(0, str(ROOT / 'scripts'))
    from manage_execution_state import skill_version
    (tmp_path / 'SKILL.md').write_text('# AI Delivery Spec 5.5.6-cr1 内测版', encoding='utf-8')
    assert skill_version(tmp_path) == '5.5.6-cr1'


def test_collision_guidance_is_actionable_in_both_languages(tmp_path):
    sys.path.insert(0, str(ROOT / 'scripts'))
    from quality_gate import Gate, localized_finding
    page = tmp_path / 'app.html'
    page.write_text('<main><button id="create" onclick="form()">New</button></main><script>function form(){}</script>', encoding='utf-8')
    gate = Gate()
    gate.check_prototype(page, 'L1')
    finding = next(x for x in gate.findings if x.code == 'PROTO-INLINE-NATIVE-COLLISION')
    zh = localized_finding(finding, 'zh-CN')
    en = localized_finding(finding, 'en-US')
    assert finding.severity == 'GAP' and 'create' in finding.ref
    assert '实际点击' in zh['how_to_fix'] and 'form()' in en['message']
    assert 'Click' in en['how_to_fix'] and 'app.closeDrawer' in en['repair_example']


@pytest.mark.parametrize('tag', ['button', 'div', 'a'])
def test_document_close_risk_is_not_limited_to_form_controls(tag):
    result, = inline_handler_collisions(f'<main>\n  <{tag} id="dismiss" onclick="return close()">Close</{tag}></main>')
    assert (result.line, result.column, result.callee, result.identifier, result.origin) == (2, 3, 'close', 'dismiss', 'DOM')


@pytest.mark.parametrize('member', ['innerHTML', 'outerHTML'])
def test_direct_html_write_literal_has_actual_source_position(member):
    raw = '<script>\nfunction show(html){\n  drawer.' + member + '=\'<button id="dismiss" onclick="close()">关闭</button>\'+html;\n}\n</script>'
    result, = inline_handler_collisions(raw)
    assert result.line == 3 and result.column == raw.splitlines()[2].index('<button') + 1
    assert (result.callee, result.identifier, result.origin) == ('close', 'dismiss', member + ' literal')


def test_dynamic_escaped_quotes_and_newline_keep_physical_source_location():
    raw = r'''<script>drawer.innerHTML = "\n<button id=\"dismiss\" onclick=\"close()\">关闭</button>";</script>'''
    result, = inline_handler_collisions(raw)
    assert result.line == 1 and result.column == raw.index('<button') + 1
    assert result.identifier == 'dismiss'


def test_template_static_prefix_and_comments_are_bounded():
    raw = '''<script>
drawer.innerHTML /* direct write */ = /* prefix */ `<button onclick="close()">关闭</button>${html}`;
</script>'''
    result, = inline_handler_collisions(raw)
    assert result.line == 2 and result.callee == 'close'
    # No invented constant folding/dataflow across unknown interpolation or a
    # preceding variable. These dynamic paths still require a browser review.
    assert inline_handler_collisions('<script>drawer.innerHTML = `${html}<button onclick="close()">关闭</button>`;</script>') == []
    assert inline_handler_collisions('<script>drawer.innerHTML = html + \'<button onclick="close()">关闭</button>\';</script>') == []


def test_comment_does_not_invent_a_local_handler_binding():
    result, = inline_handler_collisions('<button onclick="/* note */ close(); /* function close(){} */">Close</button>')
    assert result.callee == 'close'


def test_nested_template_before_real_sink_does_not_hide_later_function():
    raw = '''<script>
function render(){view.innerHTML=role==='M1'?`<section>${name}</section>`:`<section>${listed?`<p>${name}</p>`:'<p>暂无课程</p>'}</section>`}
function show(html){drawer.innerHTML='<button onclick="close()">关闭</button>'+html}
</script>'''
    result, = inline_handler_collisions(raw)
    assert (result.line, result.callee, result.origin) == (3, 'close', 'innerHTML literal')
    assert result.column == raw.splitlines()[2].index('<button') + 1


@pytest.mark.parametrize('prefix', [
    r'''const unused = `outer ${flag ? `<button onclick="close()">Close</button>` : 'x'}`;''',
    r'''const unused = "` drawer.innerHTML='<button onclick=\\\"close()\\\">Close</button>'";''',
    r'''// ` drawer.innerHTML='<button onclick="close()">Close</button>'
''',
    r'''const pattern = /[`'"{}]/g;''',
    r'''const nested = `outer ${flag ? `inner ${ {key: '}', rx: /[}`]/}.key }` : 'x'}`;''',
])
def test_template_boundaries_do_not_promote_unused_markup_to_a_sink(prefix):
    raw = '<script>' + prefix + '\ndrawer.innerHTML=\'<button onclick="app.close()">Close</button>\';</script>'
    assert inline_handler_collisions(raw) == []
    # The same lexical prefix must not hide the actual, directly written risk.
    raw = raw.replace('onclick="app.close()"', 'onclick="close()"')
    result, = inline_handler_collisions(raw)
    assert result.origin == 'innerHTML literal'


def test_close_guidance_names_actual_handler_and_source_in_both_languages(tmp_path):
    sys.path.insert(0, str(ROOT / 'scripts'))
    from quality_gate import Gate, localized_finding
    page = tmp_path / 'app.html'
    page.write_text('<script>\ndrawer.innerHTML=\'<button id="dismiss" onclick="close()">关闭</button>\';\n</script>', encoding='utf-8')
    gate = Gate()
    gate.check_prototype(page, 'L1')
    finding, = [x for x in gate.findings if x.code == 'PROTO-INLINE-NATIVE-COLLISION']
    assert finding.severity == 'GAP'
    assert all(part in finding.ref for part in ('line 2', 'column', 'dismiss', 'onclick=close()', 'innerHTML literal'))
    zh, en = localized_finding(finding, 'zh-CN'), localized_finding(finding, 'en-US')
    assert 'close()' in zh['message'] and 'document.close' in zh['message'] and '实际点击' in zh['how_to_fix']
    assert 'close()' in en['message'] and 'document.close' in en['message'] and 'Click' in en['how_to_fix']
