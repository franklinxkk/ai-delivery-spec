"""Complete server checks suppress advisory noise; backend hints cannot."""
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scan_requirement_ambiguity import inspect_content


def deep_link_findings(text):
    return [f for f in inspect_content(text)['findings'] if f['kind'] == 'deep-link']


@pytest.mark.parametrize('text', [
    '真实实现由服务端检查当前身份、对象与数据范围；直接调用、深链、撤权后的旧页面同样要检查，无权不给详情。',
    '隐藏按钮只是交互便利。服务端校验当前角色及对象访问范围，深链适用相同检查。',
    '深链与直接调用必须验证当前身份及数据范围。',
    '所有读写由服务端重新验证身份和数据范围；深链适用。',
])
def test_complete_server_identity_and_scope_check(text):
    assert not deep_link_findings(text)


@pytest.mark.parametrize('text', [
    '隐藏去处理按钮（前端），或 toast 任务已关闭（后端）。',
    '深链返回 FORBIDDEN 的提示文案；权限检查尚未实现。',
    '深链由服务端检查当前身份，但不检查数据范围。',
    '深链由服务端检查数据范围。',
    '深链由服务端无需检查当前身份和数据范围。',
    '深链由服务端尚未检查当前身份和数据范围。',
    '建议由服务端检查当前身份和数据范围；深链适用。',
    '是否由服务端检查当前身份和数据范围？深链策略未定。',
    '深链由服务端是否检查当前身份和数据范围？',
    '## 合同\n深链打开合同。\n## 回款\n由服务端检查身份和数据范围。',
])
def test_backend_wording_negation_proposal_and_other_scope_do_not_authorize(text):
    assert deep_link_findings(text)
