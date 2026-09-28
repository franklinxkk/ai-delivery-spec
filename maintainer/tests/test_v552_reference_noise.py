"""A single document cannot prove that an anchor is unused elsewhere."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from validators.validate_prd_semantics import check_dangling_refs


def test_definition_alone_is_informational_not_a_request_to_invent_consumers():
    findings = check_dangling_refs('# 合同审批\n\n## REQ-CONTRACT 合同审批\n审批通过后生效。\n')
    orphan = [x for x in findings if x.code == 'PRD-ORPHAN-DEF']
    assert orphan and all(x.severity == 'INFO' for x in orphan)


def test_real_navigation_to_missing_definition_still_blocks():
    findings = check_dangling_refs('# 合同审批\n\n失败恢复详见 REQ-RECOVERY。\n')
    assert any(x.code == 'PRD-DANGLING-REF' and x.severity == 'BLOCK' for x in findings)
