"""Translation must preserve the strength of the original finding."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from quality_gate import Finding, localized_finding

@pytest.mark.parametrize('severity', ['INFO', 'GAP', 'WARN', 'BLOCK'])
def test_english_fallback_does_not_turn_a_note_into_failure(severity):
    item=Finding(severity=severity, code='CUSTOM-CHECK', artifact='prd.md', message='需要人工查看该范围', ref='4.2')
    translated=localized_finding(item,'en-US')
    assert ('contract failed' in translated['message']) == (severity == 'BLOCK')
    assert '4.2' in translated['message']
    assert translated['severity'] == severity

def test_english_trace_skip_names_actual_skipped_check():
    item=Finding(severity='INFO', code='TRACE-LEDGER-SKIP', artifact='prd.md', message='缺少追溯侧车，跳过检查')
    message=localized_finding(item,'en-US')['message']
    assert 'sidecar' in message and 'not checked' in message and 'failed' not in message
