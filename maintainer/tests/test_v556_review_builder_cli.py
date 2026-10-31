"""Exercise the documented command, not just the callable init function."""
from pathlib import Path
import json, subprocess, sys
import pytest
ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'scripts/build_review_workspace.py'

def run(*args):
    return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')

@pytest.mark.parametrize('level',['R0','R1'])
@pytest.mark.parametrize('mode',['tabs','contextual'])
def test_documented_init_build_cli(tmp_path,level,mode):
    project=tmp_path/'review'
    initialized=run('init','--review-level',level,'--presentation-mode',mode,'--output',project)
    assert initialized.returncode==0,initialized.stderr+initialized.stdout
    assert json.loads(initialized.stdout)['status']=='example_initialized_not_project_accepted'
    built=run('build','--project',project)
    assert built.returncode==0,built.stderr+built.stdout
    html=(project/'prototype.html').read_text(encoding='utf-8')
    assert ('data-review-tab-target=' not in html) if mode=='contextual' else ('data-review-tab-target=' in html)
    metadata=json.loads((project/'review.json').read_text(encoding='utf-8'))
    assert metadata['workspace'].get('presentation_mode','tabs')==mode
    assert (project/'requirement.md').is_file()

def test_omitted_mode_keeps_compatible_default(tmp_path):
    result=run('init','--output',tmp_path/'review')
    assert result.returncode==0,result.stderr+result.stdout
    assert 'Traceback' not in result.stderr

def test_invalid_mode_is_explicit_argument_error(tmp_path):
    result=run('init','--output',tmp_path/'review','--presentation-mode','unknown')
    assert result.returncode==2 and 'invalid choice' in result.stderr
    assert not (tmp_path/'review').exists()
