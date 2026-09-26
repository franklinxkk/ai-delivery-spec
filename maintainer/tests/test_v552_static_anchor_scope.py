"""Initial markup and a replacement template do not prove simultaneous nodes."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from quality_gate import Gate


def duplicates(tmp_path, html):
    path=tmp_path/'app.html'
    path.write_text(html,encoding='utf-8')
    gate=Gate();gate.check_prototype(path,'L2')
    return {x.code for x in gate.findings if x.code in {'PROTO-DUPLICATE-REGION','PROTO-DUPLICATE-PAGE'}}


def test_replacement_template_is_not_a_second_static_region(tmp_path):
    html='''<main data-testid="page-VIEW-X"><section data-testid="region-REG-X">旧结果</section></main>
<script>const replacement='<section data-testid="region-REG-X">新结果</section>';document.querySelector('main').innerHTML=replacement;</script>'''
    assert not duplicates(tmp_path,html)
    assert 'PROTO-DUPLICATE-REGION' in duplicates(tmp_path,html.replace('</main>','<section data-testid="region-REG-X">另一个同时存在的结果</section></main>'))


def test_inert_template_and_comments_do_not_count_as_pages(tmp_path):
    html='''<main data-testid="page-VIEW-X"></main><template><main data-testid="page-VIEW-X"></main></template>
<!-- <main data-testid="page-VIEW-X"></main> -->'''
    assert not duplicates(tmp_path,html)
    assert 'PROTO-DUPLICATE-PAGE' in duplicates(tmp_path,html+'<main data-testid="page-VIEW-X"></main>')
