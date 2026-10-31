"""Bounded regressions from real-project review; no private project fixtures."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from validators.validate_prd_semantics import collect_defined_ids, check_pending_execution


def test_leading_plain_definition_is_not_a_mid_sentence_reference():
    assert collect_defined_ids('RULE-SAVE-1：保存时复核权限，参见 RULE-SAVE-2') == {'RULE-SAVE-1'}
    assert not collect_defined_ids('参见 RULE-SAVE-1：保存说明')


def test_explicit_pending_execution_conflict_and_safe_controls():
    for text in ['待确认；在此之前实现须按默认值执行。',
                 'Pending approval. In the meantime the system must apply defaults.']:
        assert check_pending_execution(text), text
    for text in ['未确认前不得按默认值执行。',
                 '已授权按当前默认值执行，暂不开放其他分支。',
                 '反例：待确认；在此之前实现须按默认值执行。',
                 'Concept-only: pending approval. In the meantime the system must apply defaults.']:
        assert not check_pending_execution(text), text
