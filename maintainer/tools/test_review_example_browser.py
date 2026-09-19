"""Offline browser checks for the shipped review example; Playwright is optional.

Run: python maintainer/tools/test_review_example_browser.py --output <evidence-dir>
Pass --executable for a locally installed Chromium. This is not production proof.
"""
from pathlib import Path
import argparse
import hashlib
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--executable')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source = ROOT/'examples/medium-review-handoff/review-prototype.html'
    checks, errors = [], []

    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
        if not value:
            raise AssertionError(name)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=args.executable)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(source.as_uri())
        click = lambda action: page.locator('[data-action="'+action+'"]').first.click()
        snapshot = lambda: page.evaluate('window.__demo.snapshot()')
        fingerprint = lambda: page.evaluate('window.__demo.fingerprint()')
        try:
            check('loaded product mode', page.locator('#order-name').inner_text() == '001 · 水泵异响')
            before_box = page.locator('.order-card').bounding_box()
            click('UIACT-REVIEW-TOGGLE')
            check('review panel opens', page.locator('[data-review-workspace]').is_visible())
            # Fixed container width: markers must not become additional grid cells.
            check('business grid contains exactly two cells', page.locator('.order-card > div').count() == 2)
            before = fingerprint()
            click('UIACT-REVIEW-SELECT')
            check('marker and card select together', page.locator('[data-review-ref][aria-current=true]').count() == 1 and page.locator('[data-review-point][aria-current=true]').count() == 1)
            check('selected target is visible', page.locator('[data-review-target-selected=true]').is_visible())
            page.locator('[data-review-point]:visible summary').click()
            for role in ['frontend','backend','qa']:
                check(role+' detail readable', page.locator('[data-review-point]:visible [data-review-role-detail='+role+']').is_visible())
            check('reading details preserves business', fingerprint() == before)
            page.locator('#reviewer').fill('教学复核')
            page.locator('#comment').fill('已核对指派权限和原子结果')
            click('UIACT-REVIEW-RECORD')
            check('review record persisted', page.locator('[data-review-progress]').get_attribute('data-review-progress-resolved') == '1')
            check('review record does not approve business', fingerprint() == before)
            click('UIACT-REVIEW-EXPORT')
            exported = page.locator('#review-json').input_value()
            bad = json.loads(exported);bad[0]['baseline_ref'] = '0'*64
            page.locator('#review-json').fill(json.dumps(bad))
            click('UIACT-REVIEW-IMPORT')
            check('wrong baseline import rejected', '未导入' in page.locator('#review-message').inner_text())
            page.locator('#review-json').fill(exported);click('UIACT-REVIEW-IMPORT')
            check('same baseline import works', '已导入' in page.locator('#review-message').inner_text())
            page.locator('[data-review-workspace]').evaluate('(node)=>node.scrollTop=0')
            page.screenshot(path=str(args.output/'desktop-review.png'), full_page=True)
            click('ACT-X-SUBMIT')
            check('assignment writes one audit', snapshot()['orders'][0]['status']=='assigned' and len(snapshot()['audit'])==1)
            db = snapshot()
            duplicate = page.evaluate("window.__demo.request('assign',{version:2})")
            check('duplicate assignment has no side effect', not duplicate['ok'] and snapshot()==db)
            page.locator('#actor').select_option('lin')
            previous_tab=page.locator('[data-review-workspace]').get_attribute('data-review-active-tab')
            page.locator('#open-detail').click()
            check('drawer context and breadcrumb sync', page.locator('[data-review-workspace]').get_attribute('data-review-current-context') == 'DRAWER-X' and '工单详情' in page.locator('#breadcrumb').inner_text())
            page.locator('[data-review-ref="RVP-DRAWER-CONFIRM"]').click()
            page.locator('#close-detail').click()
            check('closing overlay restores parent selection', page.locator('[data-review-ref="RVP-VIEW-SUBMIT"]').get_attribute('aria-current')=='true')
            check('closing overlay restores parent tab', page.locator('[data-review-workspace]').get_attribute('data-review-active-tab')==previous_tab)
            page.locator('#open-detail').click()
            page.locator('#completion-note').fill('   ');click('ACT-X-CONFIRM')
            check('blank completion rejected without writes', '请填写' in page.locator('#feedback').inner_text() and snapshot()==db)
            page.locator('#completion-note').fill('字'*101);click('ACT-X-CONFIRM')
            check('overlong completion rejected without writes', '不能超过' in page.locator('#feedback').inner_text() and snapshot()==db)
            page.locator('#completion-note').fill('更换轴承，试运行正常')
            page.locator('#simulate-conflict').click();conflicted=snapshot();click('ACT-X-CONFIRM')
            check('stale version rejected and input preserved', '请刷新' in page.locator('#feedback').inner_text() and snapshot()==conflicted and page.locator('#completion-note').input_value()=='更换轴承，试运行正常')
            page.locator('#refresh-order').click();click('ACT-X-CONFIRM')
            check('refresh recovers into one completion', not page.locator('#drawer').is_visible() and snapshot()['orders'][0]['status']=='closed' and len(snapshot()['audit'])==2)
            saved=snapshot();page.reload()
            check('business data persists on refresh', snapshot()==saved)
            check('review data persists separately', page.locator('[data-review-progress]').get_attribute('data-review-progress-resolved')=='1')
            page.locator('#reset').click()
            initial=snapshot()
            rejected=page.evaluate("window.__demo.request('assign',{actor:'lin'})")
            check('service rejects wrong assigning actor', not rejected['ok'] and snapshot()==initial)
            rejected=page.evaluate("window.__demo.request('complete',{id:'002',actor:'lin',version:1,note:'正常完工'})")
            check('service rejects another assignee', not rejected['ok'] and snapshot()==initial)
            # Exercise repeated review updates to detect recursion and drift.
            click('UIACT-REVIEW-TOGGLE');before=fingerprint()
            for _ in range(12):
                page.locator('[data-review-tab-target=boundary_acceptance]').click()
                page.locator('[data-review-tab-target=overview]').click()
            check('repeated updates converge without mutation', fingerprint()==before and not errors)
            page.locator('input[aria-label="评审说明宽度"]').fill('520')
            check('resizing preserves business', fingerprint()==before)
            click('UIACT-REVIEW-SELECT');share=page.evaluate('window.__demo.shareLocator()')
            old_page=page
            page=old_page.context.new_page()
            page.set_viewport_size({'width':1440,'height':1000})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(share)
            old_page.close()
            check('share hydrates point and context', page.locator('[data-review-point][aria-current=true]').count()==1)
            page.set_viewport_size({'width':390,'height':844})
            click('UIACT-REVIEW-TOGGLE') # first toggle is product expand
            check('compact review replaces product surface', page.locator('[data-review-workspace]').is_visible() and not page.locator('#product').is_visible())
            page.locator('[data-review-point]:visible').click()
            check('compact card can resolve product target', page.locator('[data-review-point][aria-current=true]').count()==1)
            page.screenshot(path=str(args.output/'mobile-review.png'),full_page=True)
            click('UIACT-REVIEW-COMPACT')
            check('compact mode returns to product', page.locator('#product').is_visible())
            check('mobile has no horizontal overflow', page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
            check('runtime recorded no invariant violation', not page.evaluate('window.__ADS_REVIEW_GATE__.violations'))
            check('no browser exceptions', not errors)
            probe=page.context.new_page()
            probe.goto(source.as_uri())
            result=probe.evaluate("()=>{try{window.__demo.resolveReviewTarget('[data-action=ACT-NOT-HERE]');return ''}catch(e){return e.message}}")
            check('missing review target rejects honestly', result=='PROTO-REVIEW-TARGET-UNRESOLVED')
            result=probe.evaluate("()=>{const n=document.querySelector('[data-action=ACT-X-SUBMIT]');n.parentElement.append(n.cloneNode(true));try{window.__demo.resolveReviewTarget('[data-action=ACT-X-SUBMIT]');return ''}catch(e){return e.message}}")
            check('duplicate review target is blocking', result=='PROTO-REVIEW-TARGET-AMBIGUOUS')
            probe.close()
        finally:
            (args.output/'browser-results.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':checks,'browser_errors':errors,'browser_version':browser.version,'not_proven':['real backend','authentication','database transaction','customer acceptance']},ensure_ascii=False,indent=2),encoding='utf-8')
            browser.close()
    print(f'PASS: {len(checks)} browser checks')


if __name__ == '__main__':
    main()
