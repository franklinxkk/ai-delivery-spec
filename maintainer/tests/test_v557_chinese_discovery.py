from pathlib import Path
import json,subprocess,sys
import yaml
ROOT=Path(__file__).resolve().parents[2]
def query(*args):
 r=subprocess.run([sys.executable,str(ROOT/'scripts/query_domain.py'),*args,'--format','yaml'],capture_output=True,text=True,encoding='utf8');assert r.returncode==0,r.stdout+r.stderr;return yaml.safe_load(r.stdout)
def test_catalog_has_chinese_summary_and_real_files():
 d=json.loads((ROOT/'references/domains/domain-discovery.json').read_text(encoding='utf8'))
 assert len(d['domains'])==8
 for row in d['domains']:
  assert row['summary_zh'] and row['aliases'] and row['terms']
  assert (ROOT/row['knowledge_file']).is_file()
 assert query('--list')
def test_chinese_domain_section_and_alias_expansion():
 d=query('--domain','数据底座','--section','指标口径');assert d['domain_id']=='data-product' and d['selected_sections']
 d=query('--search','补考后重修怎么保留成绩','--limit','5');assert any(h['domain_id']=='education-it' for h in d['hits'])
 assert d['domain_expansions'] and d['expanded_terms']
def test_unknown_expression_does_not_invent_knowledge():
 d=query('--search','ZXQNONEXISTENT887');assert not d['hits'] and d['next_action'] and d['fallback']
def test_project_permission_is_not_domain_default():
 guides=json.loads((ROOT/'references/domains/domain-discovery.json').read_text(encoding='utf8'))['domains'];t=(ROOT/next(d['knowledge_file'] for d in guides if d['domain_id']=='oa')).read_text(encoding='utf8')
 assert '机构超管能处理所有内部数据' not in t and '本机构全部预警' not in t
 assert '以项目确认的规则为准' in t
