"""The project-owned path must work without initializing the repair example."""
from pathlib import Path
import json
import os
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/build_review_workspace.py'


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True, encoding='utf-8',
                          env={**os.environ, 'PYTHONUTF8': '0', 'PYTHONIOENCODING': 'cp1252'})


def inputs(tmp_path, notes='## Book a room\n<!-- context: #booking -->\nUp to **8** people.\n'):
    product = tmp_path / 'booking.html'
    product.write_text('<!doctype html><main id="booking"><input value="keep"></main>', encoding='utf-8')
    source = tmp_path / 'notes.md'
    source.write_text(notes, encoding='utf-8')
    return product, source


@pytest.mark.parametrize('language', ['zh', 'en'])
def test_project_cli_preserves_original_and_reports_actual_delivery(tmp_path, language):
    product, notes = inputs(tmp_path)
    product = product.rename(tmp_path / '预约.html')
    original = product.read_bytes()
    result = run('attach', '--prototype', product, '--notes', notes, '--language', language)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    generated = Path(report['output'])
    assert report['status'] == 'attached_notes_not_validated'
    assert report['delivery'] == 'local_same_origin_http_companion_not_single_html'
    assert report['required_files'] == [str(generated), str(product)]
    assert product.read_bytes() == original
    html = generated.read_text(encoding='utf-8')
    assert 'review-workspace-manifest' not in html
    assert '维修' not in html and 'work order' not in html
    assert 'notes-panel" aria-label=' in html and ' hidden></aside>' in html
    # Rebuilding replaces only the generated companion.
    notes.write_text('## Changed notes\n<!-- context: #booking -->\nNew source.\n', encoding='utf-8')
    again = run('attach', '--prototype', product, '--notes', notes)
    assert again.returncode == 0
    assert product.read_bytes() == original
    assert 'Changed notes' in generated.read_text(encoding='utf-8')


@pytest.mark.parametrize('notes', [
    '## Booking\nNo selector.',
    '## A\n<!-- context: #booking -->\n## B\n<!-- context: #booking -->',
    '## A\n<!-- context: #booking -->\n![outside](../private.svg)',
    '## A\n<!-- context: #booking -->\n![remote](https://example.com/image.png)',
])
def test_invalid_sources_fail_without_output(tmp_path, notes):
    product, source = inputs(tmp_path, notes)
    result = run('attach', '--prototype', product, '--notes', source)
    assert result.returncode == 2
    assert not (tmp_path / 'booking-review.html').exists()


def test_source_text_is_nonexecutable_and_diagram_is_embedded(tmp_path):
    product, source = inputs(tmp_path, '## Booking\n<!-- context: #booking -->\n<script>bad()</script>\n\n![Diagram](flow.svg)')
    (tmp_path / 'flow.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>book</text></svg>', encoding='utf-8')
    result = run('attach', '--prototype', product, '--notes', source)
    assert result.returncode == 0, result.stdout
    html = (tmp_path / 'booking-review.html').read_text(encoding='utf-8')
    assert '<script>bad()' not in html
    assert 'image/svg+xml;base64,' in html


def test_output_and_notes_cannot_escape_or_replace_product(tmp_path):
    product, source = inputs(tmp_path)
    original = product.read_bytes()
    for target in [product, tmp_path.parent / 'escaped.html']:
        assert run('attach', '--prototype', product, '--notes', source, '--output', target).returncode == 2
    existing = tmp_path / 'booking-review.html'
    existing.write_text('existing user work', encoding='utf-8')
    assert run('attach', '--prototype', product, '--notes', source).returncode == 2
    assert existing.read_text(encoding='utf-8') == 'existing user work'
    assert product.read_bytes() == original


def test_existing_review_surface_is_not_duplicated(tmp_path):
    product, source = inputs(tmp_path)
    product.write_text('<aside data-review-workspace="existing"></aside>', encoding='utf-8')
    assert run('attach', '--prototype', product, '--notes', source).returncode == 2
