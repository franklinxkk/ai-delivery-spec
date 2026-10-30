/* Use from a project's real Playwright UI itinerary; this helper never navigates business pages. */
const fs=require('fs'),crypto=require('crypto');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const stable=x=>Array.isArray(x)?x.map(stable):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,stable(x[k])])):x;
async function captureReview(page,{context,trigger,fixture=false}){
 const fp=async()=>hash(await page.evaluate(()=>ADSReview.fingerprint()));
 const before=await fp();await page.locator('#ads-page-guide').click();
 const o={context_ref:context,trigger,capture_method:fixture?'fixture_then_browser_ui':'browser_ui',fingerprint_before:before,cards:[],examples:[],diagrams:[]};
 const refs=await page.locator('#ads-notes [data-review-point]').evaluateAll(es=>es.map(e=>e.dataset.reviewPoint));
 for(const ref of refs){
  const card=page.locator('#ads-notes [data-review-point="'+ref+'"]');
  if(!await card.evaluate(e=>e.open))await card.locator(':scope>summary').click();
  const impl=card.locator('[data-review-implementation]');
  if(await impl.count()&&!await impl.evaluate(e=>e.open))await impl.locator(':scope>summary').click();
  o.cards.push(await card.evaluate(e=>{const r=ADSReview.resolve(e.dataset.reviewPoint),impl=e.querySelector('[data-review-implementation]');return {ref:e.dataset.reviewPoint,text:e.innerText,visible:e.open&&!!e.getClientRects().length,implementation_visible:!!impl&&impl.open&&!!impl.getClientRects().length&&impl.innerText.length>15,condition_text:e.querySelector('.ads-conditional')?.innerText||'',target:{count:r.el?1:r.count||0,error:r.error||null,status:r.status||null,applicability:r.applicability||null}}}));
 }
 const examples=page.locator('#ads-notes details').filter({has:page.locator('summary').filter({hasText:'怎样验收'})});
 if(await examples.count()){
  if(!await examples.first().evaluate(e=>e.open))await examples.first().locator(':scope>summary').click();
  o.examples=await page.locator('[data-review-example]').evaluateAll(es=>es.map(e=>({ref:e.dataset.reviewExample,text:e.innerText,visible:!!e.getClientRects().length&&!e.closest('details:not([open])')})));
 }
 for(const button of await page.locator('#ads-notes [data-review-diagram]').all()){
  const ref=await button.getAttribute('data-review-diagram');await button.scrollIntoViewIfNeeded();const visible=await button.isVisible();await button.click();
  const viewer=page.locator('#ads-viewer');await viewer.waitFor({state:'visible'});
  o.diagrams.push({ref,thumbnail_visible:visible,viewer_opened:await viewer.evaluate(e=>e.open),image_loaded:await viewer.locator('img').evaluate(e=>e.complete&&e.naturalWidth>0)});
  await page.keyboard.press('Escape');
 }
 Object.assign(o,await page.evaluate(()=>({current_context:document.querySelector('#ads-review').dataset.reviewCurrentContext,detected_context:ADSReview.detect().key,panel_visible:document.body.classList.contains('ads-drawer-open'),product_root_visible:!!document.querySelector(ADSReview.context().root)?.getClientRects().length,runtime_errors:[...__ADS_REVIEW_GATE__.errors,...(__ADS_REVIEW_GATE__.targetErrors||[])].map(x=>x.message||x.error||x.name)})));
 o.return_preserves_context=o.current_context===context;o.fingerprint_after=await fp();
 o.visible_actions=await page.locator('#ads-product [data-action]:visible').evaluateAll(es=>[...new Set(es.map(e=>e.dataset.action))]);
 await page.locator('#ads-review [data-action="UIACT-REVIEW-CLOSE"]').first().click();
 return o;
}
function writeEvidence(htmlPath,observations,out){
 const bytes=fs.readFileSync(htmlPath),raw=bytes.toString('utf8'),manifestRaw=raw.match(/<script[^>]*id="review-workspace-manifest"[^>]*>([\s\S]*?)<\/script>/)[1];
 fs.writeFileSync(out,JSON.stringify({schema_version:1,prototype_sha256:hash(bytes),manifest_hash_format:'embedded-json-bytes-v1',manifest_sha256:hash(manifestRaw),captured_at:new Date().toISOString(),collector:'review_runtime_probe.cjs',claim_limit:'Observed browser projection; no backend, production or human acceptance claim.',observations},null,2));
}
module.exports={captureReview,writeEvidence};
