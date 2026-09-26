"""A form change handler does not make the field a primary command button."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from scan_prototype_css import _scan_html


def test_peer_fields_are_not_button_hierarchy_failures():
    html = '<main>' + ''.join(f'<select data-action="ACT-SELECT-{i}"><option>A</option></select>' for i in range(3)) + '</main>'
    assert 'flat-button-hierarchy' not in {x['kind'] for x in _scan_html(html, '')}
    html = '<input data-action="ACT-FILTER"><textarea data-action="ACT-NOTE"></textarea><select data-action="ACT-OWNER"></select>'
    assert 'flat-button-hierarchy' not in {x['kind'] for x in _scan_html(html, '')}


def test_command_control_hierarchy_remains_checked():
    html = '<button data-action="ACT-SAVE">保存</button><a data-action="ACT-CANCEL">取消</a><input type="submit" data-action="ACT-DELETE">'
    assert 'flat-button-hierarchy' in {x['kind'] for x in _scan_html(html, '')}
    html = html.replace('<button ', '<button class="primary" ')
    assert 'flat-button-hierarchy' not in {x['kind'] for x in _scan_html(html, '.primary{color:blue}')}
