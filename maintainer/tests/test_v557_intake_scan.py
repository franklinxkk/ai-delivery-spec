"""Run with the standard Python unittest runner and the runtime dependencies."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scan_requirement_ambiguity import scan
from triage_requirement import recommend, render_markdown


class IntakeAndScan(unittest.TestCase):
    def test_numeric_and_enum_defaults(self):
        for text in ('画布默认 1920×1080。','刷新默认 0；可手动更新。','导出默认全量。','默认 5 分钟。','默认最多3次。','必填；默认左 | 左连接保留所有左表记录。'):
            with self.subTest(text=text):
                self.assertFalse(any(x['kind']=='undefined-default' for x in scan(text)))

    def test_undefined_defaults_are_still_candidates(self):
        for text in ('默认处理。','默认 3 到多少天待定。','自动处理。'):
            findings = [x for x in scan(text) if x['kind']=='undefined-default']
            self.assertTrue(findings, text)
            self.assertTrue(all(x['advisory'] for x in findings))

    def test_explicit_facets_leave_authority_and_deliverable_alone(self):
        sample = {'title':'编辑列表字段名称','risk_facets':['患者隐私','权限','合同另约'],'artifact_mode':'direct'}
        result = recommend(sample)
        self.assertIn('permission_boundary', result['semantic_review_categories'])
        self.assertIn('合同另约',result['declared_risk_facets'])
        self.assertIn('患者隐私',render_markdown(result))
        self.assertEqual(result['artifact_mode'],'direct')
        self.assertFalse(result['governed'])
        self.assertFalse(result['lifecycle_mutated'])
        self.assertIsNone(result['priority'])
        self.assertEqual(result['next_questions'],[])

    def test_explicit_policy_fork(self):
        result=recommend({'title':'审批通过后可以发布','description':'审批通过后可以发布。'})
        self.assertEqual(result['recommendation'],'clarify')
        self.assertTrue(result['next_questions'])

    def test_public_cli_json_and_version(self):
        cli=ROOT/'scripts/ai_delivery_spec_cli.py'
        with tempfile.TemporaryDirectory() as temp:
            src=Path(temp)/'sample.md'
            src.write_text('自动处理。','utf8')
            output=subprocess.check_output([sys.executable,'-B','-X','utf8',str(ROOT/'scripts/scan_requirement_ambiguity.py'),str(src),'--format','json'],text=True,encoding='utf8')
            self.assertTrue(json.loads(output)['findings'])
        self.assertIn('5.5.7',subprocess.check_output([sys.executable,'-B',str(cli),'version'],text=True))

if __name__=='__main__':
    unittest.main()
