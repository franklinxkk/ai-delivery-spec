"""Context-event wiring recognizes legal bindings, not comments or other scopes."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validators.gate_prototype_checks import _has_context_event_listener
from test_review_workspace_contracts import html_gate, manifest, review_html


EVENT = "product-context-change"


@pytest.mark.parametrize("source", [
    "window.addEventListener('product-context-change', resolveCurrentContext);",
    'window.addEventListener("product-context-change", () => resolveCurrentContext());',
    "const contextEvent='product-context-change';window.addEventListener(contextEvent, resolveCurrentContext);",
    "const clock='fixed', view='VIEW-X', contextEvent='product-context-change';window.addEventListener(contextEvent, () => resolveCurrentContext());",
    "let view='VIEW-X',\n contextEvent = `product-context-change`; window.addEventListener(contextEvent, resolveCurrentContext);",
    "var view='VIEW-X', contextEvent='product-context-change'; window.addEventListener(contextEvent, resolveCurrentContext);",
    "let contextEvent; contextEvent='product-context-change'; window.addEventListener(contextEvent, resolveCurrentContext);",
    "const contextEvent='product-context-change'; function register(){window.addEventListener(contextEvent, resolveCurrentContext);}",
])
def test_context_listener_accepts_literal_and_multi_declarator_binding(source):
    assert _has_context_event_listener(source, EVENT)


@pytest.mark.parametrize("source", [
    "// window.addEventListener('product-context-change', resolveCurrentContext);",
    "/* const e='product-context-change'; window.addEventListener(e, resolveCurrentContext); */",
    '''const example = "window.addEventListener('product-context-change', resolveCurrentContext);";''',
    "const contextEvent='different-event';window.addEventListener(contextEvent, resolveCurrentContext);",
    "// contextEvent='product-context-change';\nwindow.addEventListener(contextEvent, resolveCurrentContext);",
    "function other(){const contextEvent='product-context-change';}window.addEventListener(contextEvent, resolveCurrentContext);",
    "{const contextEvent='product-context-change';}window.addEventListener(contextEvent, resolveCurrentContext);",
    "let contextEvent='product-context-change';contextEvent='different';window.addEventListener(contextEvent, resolveCurrentContext);",
    "const contextEvent='product-context-change';function register(){const contextEvent='different';window.addEventListener(contextEvent, resolveCurrentContext);}",
    "const contextEvent='product-context-change'+'-other';window.addEventListener(contextEvent, resolveCurrentContext);",
    "const contextEvent='product-context-change';window.addEventListener(contextEvent+'-other', resolveCurrentContext);",
    "const contextEvent='product-context-change';window.dispatchEvent(new Event(contextEvent));",
])
def test_context_listener_does_not_accept_non_code_wrong_event_or_other_scope(source):
    assert not _has_context_event_listener(source, EVENT)


def codes(tmp_path, raw):
    return {item.code for item in html_gate(tmp_path / 'review.html', raw).findings}


def comma_bound_review():
    return review_html(manifest('1' * 64)).replace(
        'const productContextEvent="product-context-change";',
        "const clock='fixed', view='VIEW-X', productContextEvent='product-context-change';",
    )


def test_actual_gate_accepts_comma_binding_without_weakening_missing_listener(tmp_path):
    raw = comma_bound_review()
    assert 'PROTO-REVIEW-OVERLAY-DETECTION' not in codes(tmp_path, raw)
    listener = 'window.addEventListener(productContextEvent,resolveCurrentContext);'
    # An observer or a comment containing the original call is not a listener.
    assert 'PROTO-REVIEW-OVERLAY-DETECTION' in codes(tmp_path, raw.replace(listener, '/* ' + listener + ' */'))
    assert 'PROTO-REVIEW-OVERLAY-DETECTION' in codes(tmp_path, raw.replace('PROTO-REVIEW-OVERLAY-UNDECLARED', 'unrelated'))


def test_undeclared_product_overlay_remains_blocked(tmp_path):
    raw = comma_bound_review().replace('</main>', '<section role="dialog">Unmapped business dialog</section></main>', 1)
    assert 'PROTO-REVIEW-OVERLAY-UNCOVERED' in codes(tmp_path, raw)


def test_ambiguous_declared_topmost_remains_blocked(tmp_path):
    document = manifest('1' * 64)
    document['review_contexts'].append({
        'context_ref': 'MODAL-CONFLICT', 'context_type': 'MODAL', 'title': 'Conflicting overlay',
        'detection': copy.deepcopy(document['review_contexts'][1]['detection']),
        'product_location': copy.deepcopy(document['review_contexts'][1]['product_location']),
        'surface_types': ['form'], 'secondary_context_refs': [], 'review_point_refs': [],
    })
    assert 'PROTO-REVIEW-OVERLAY-DETECTION' in codes(tmp_path, review_html(document))


def test_no_declared_event_cannot_borrow_any_listener(tmp_path):
    document = manifest('1' * 64)
    document['context_contract']['product_context_event'] = 'different-context-event'
    assert 'PROTO-REVIEW-OVERLAY-DETECTION' in codes(tmp_path, review_html(document))
