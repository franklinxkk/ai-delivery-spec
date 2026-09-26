import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from validators.validate_prd_semantics import check_dangling_refs
from validators.validate_prd_semantics import check_enum_cardinality
from requirement_contract import check_spec
import pytest


def test_yaml_appendix_reference_is_not_orphan_but_missing_target_stays_visible():
    text='''## 3. 检查计划（REQ-CHECK）
规则已有说明。
```yaml
- id: AC-CHECK
  requirement_refs:
    - REQ-CHECK
    - REQ-MISSING
```
'''
    findings=check_dangling_refs(text)
    assert not any(x.code=='PRD-ORPHAN-DEF' and 'REQ-CHECK@' in x.ref for x in findings)
    assert any(x.code=='PRD-DANGLING-REF' and 'REQ-MISSING@' in x.ref for x in findings)


def test_json_links_count_but_arbitrary_code_literal_does_not_resolve_orphan():
    text='''## REQ-REAL
```json
{"id":"AC-REAL", "requirement_refs":["REQ-REAL"]}
```
## REQ-UNUSED
```python
print("REQ-UNUSED")
```
'''
    findings=check_dangling_refs(text)
    assert not any(x.code=='PRD-ORPHAN-DEF' and 'REQ-REAL@' in x.ref for x in findings)
    assert any(x.code=='PRD-ORPHAN-DEF' and 'REQ-UNUSED@' in x.ref for x in findings)


def test_formatted_navigation_does_not_hide_a_missing_definition():
    findings=check_dangling_refs('''参见 `STM-MISSING`。
路径是 `external/REQ-OTHER.yaml`。
''')
    assert any(x.code=='PRD-DANGLING-REF' and x.severity=='BLOCK' and 'STM-MISSING@' in x.ref for x in findings)
    assert not any('REQ-OTHER@' in x.ref for x in findings)


def test_id_embedded_in_heading_resolves_table_navigation():
    text='''## 附录 B. 审核状态机（STM-CHECK）
定义正文。
| 动作 | 依据 |
| --- | --- |
| 提交 | 参见 `STM-CHECK` |
'''
    assert not check_dangling_refs(text)


@pytest.mark.parametrize('wrapper',['{}','**{}**','__{}__','`{}`'])
@pytest.mark.parametrize('header',['resolution_ref','决议 / 来源'])
def test_unknown_closure_is_not_changed_by_markdown(wrapper,header):
    body='| ID | 状态 | '+wrapper.format(header)+' |\n|---|---|---|\n| '+wrapper.format('UNK-X')+' | '+wrapper.format('closed')+' | DEC-X |'
    assert not any(f['code']=='SPEC-UNKNOWN-CLOSURE' for f in check_spec({},body)[0])
    missing=body.replace('DEC-X','-')
    assert any(f['code']=='SPEC-UNKNOWN-CLOSURE' for f in check_spec({},missing)[0])


def test_bold_id_definition_is_not_a_wildcard_but_real_wildcard_is():
    body='| ID | 决定 |\n|---|---|\n| **DEC-39** | 保留原单 |\n\n详见 DEC-39。\nACT-TEST-* 用作家族模式。'
    assert not check_dangling_refs(body)


def test_appendix_index_is_not_a_cardinality_but_real_count_still_checks():
    rows='\n- 甲\n- 乙\n'
    assert not check_enum_cardinality('## 附录 3 类目覆盖度'+rows)
    assert check_enum_cardinality('## 共 3 类'+rows)
