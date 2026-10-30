/* Run against the public CLI and local HTTP with a non-repair product.
   node test_context_notes_browser.cjs --output evidence --playwright <module-dir>
     [--python python] [--executable <chromium>]
   This is component evidence, not formal R0/R1 or business acceptance. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {spawnSync} = require('node:child_process');
const crypto = require('node:crypto');
const options = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, i, args) => i % 2 ? pairs : [...pairs, [value.slice(2), args[i+1]]], []));
if (!options.output) throw new Error('--output required');
const {chromium} = require(options.playwright || 'playwright');
const output = path.resolve(options.output);
fs.mkdirSync(output, {recursive: true});
const project = path.join(output, 'reservation-project');
fs.mkdirSync(project, {recursive: true});
const root = path.resolve(__dirname, '../..');
const productPath = path.join(project, 'reservations.html');
const checks = [], errors = [];
const product = `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Room reservations</title>
<style>body{font:16px/1.5 system-ui;margin:30px;color:#20384e}label{display:block;margin:15px 0}input,select,button{font:inherit;padding:7px}button{margin:4px}dialog{width:min(500px,80vw);border:1px solid #adc0d1;border-radius:8px}table{border-collapse:collapse;width:100%;max-width:850px}td,th{padding:12px;border-bottom:1px solid #ccd8e4;text-align:left}[hidden]{display:none!important}</style></head><body>
<nav><button id="active-view">Reservations</button><button id="archive-view">Archive</button></nav>
<main id="reservation-page" data-ads-context><h1>Room reservations</h1><form id="request-form"><label>Purpose <input id="purpose" value="Planning session"></label><label>Room <select id="room"><option>Lake</option><option>Forest</option></select></label><label><input id="video" type="checkbox"> Video call</label><button type="submit">Submit request</button></form><output id="result"></output>
<table><tr><th>Reservation</th><th>Room</th><th>Action</th></tr><tr><td>B-101</td><td>Lake</td><td><button id="detail-101" data-record="B-101">View details</button></td></tr><tr><td>B-202</td><td>Forest</td><td><button id="detail-202" data-record="B-202">View details</button></td></tr></table><button id="open-help">Booking help</button><button id="open-ambiguous">Show two custom overlays</button></main>
<main id="archive-page" data-ads-context hidden><h1>Archived reservations</h1><p>No archived reservations.</p></main>
<dialog id="reservation-detail"><h2>Reservation details</h2><p id="selected-record"></p><label>Private draft <input id="detail-draft"></label><button id="close-detail">Close details</button></dialog>
<dialog id="booking-help"><h2>Booking help</h2><p>Contact the room coordinator.</p><button id="close-help">Close help</button></dialog>
<div id="custom-one" role="dialog" hidden>Custom one <button id="close-ambiguous">Close both</button></div><div id="custom-two" role="dialog" hidden>Custom two</div>
<script>
const q=s=>document.querySelector(s);window.businessWrites=0;window.selected=null;
q('#request-form').onsubmit=e=>{e.preventDefault();window.businessWrites++;q('#result').textContent='Request submitted';};
document.querySelectorAll('[data-record]').forEach(button=>button.onclick=()=>{window.selected=button.dataset.record;q('#selected-record').textContent=window.selected;q('#reservation-detail').showModal();});
q('#close-detail').onclick=()=>q('#reservation-detail').close();q('#open-help').onclick=()=>q('#booking-help').showModal();q('#close-help').onclick=()=>q('#booking-help').close();
q('#archive-view').onclick=()=>{q('#reservation-page').hidden=true;q('#archive-page').hidden=false;};q('#active-view').onclick=()=>{q('#reservation-page').hidden=false;q('#archive-page').hidden=true;};
q('#open-ambiguous').onclick=()=>{q('#custom-one').hidden=false;q('#custom-two').hidden=false;};q('#close-ambiguous').onclick=()=>{q('#custom-one').hidden=true;q('#custom-two').hidden=true;};
window.snapshot=()=>({writes:window.businessWrites,selected:window.selected,purpose:q('#purpose').value,room:q('#room').value,video:q('#video').checked,privateDraft:q('#detail-draft').value,page:q('#reservation-page').hidden?'archive':'reservations',detail:q('#reservation-detail').open,help:q('#booking-help').open});
</script></body></html>`;
fs.writeFileSync(productPath, product);
fs.writeFileSync(path.join(project, 'flow.svg'), '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="240" viewBox="0 0 960 240"><rect width="960" height="240" fill="#edf5fd"/><g font-family="sans-serif" font-size="28" fill="#204f79"><rect x="50" y="60" width="300" height="110" rx="12" fill="white" stroke="#204f79"/><text x="95" y="125">Request room</text><path d="M350 115H570" stroke="#204f79" stroke-width="4"/><text x="450" y="95">→</text><rect x="580" y="60" width="320" height="110" rx="12" fill="white" stroke="#204f79"/><text x="620" y="125">Check capacity</text></g></svg>');
const copy = {
  en: {page:'Request a room', detail:'Read reservation details', text:'Fill in the purpose and room. A rejected request keeps the input. Capacity must be at most **8** people.', diagram:'Booking flow', detailText:'The details belong to the reservation opened from its actual list row. Closing returns to the existing list.'},
  zh: {page:'提交会议室预约', detail:'查看预约详情', text:'填写用途和会议室。提交被拒绝时保留输入；预约人数最多 **8** 人。', diagram:'预约处理流程', detailText:'详情对应从实际列表行打开的预约。关闭后回到原列表，不清空已有输入。'}
};
const hashes = {};
for (const lang of ['zh', 'en']) {
  const notes = copy[lang];
  const notePath = path.join(project, `notes-${lang}.md`);
  fs.writeFileSync(notePath, `# Room reservations\n\n## ${notes.page}\n<!-- context: #reservation-page -->\n${notes.text}\n\n![${notes.diagram}](flow.svg)\n\n## ${notes.detail}\n<!-- context: #reservation-detail -->\n${notes.detailText}\n\n## Custom product overlay\n<!-- context: #custom-one -->\nExplanation for the product's explicitly selected overlay.\n`);
  const target = path.join(project, `review-${lang}.html`);
  const cli = spawnSync(options.python || 'python', [path.join(root, 'scripts/build_review_workspace.py'), 'attach', '--prototype', productPath, '--notes', notePath, '--output', target, '--language', lang], {encoding:'utf8',env:{...process.env,PYTHONUTF8:'1',PYTHONDONTWRITEBYTECODE:'1'}});
  if (cli.status !== 0) throw new Error(cli.stdout + cli.stderr);
  const metadata = JSON.parse(cli.stdout);
  fs.writeFileSync(path.join(output, `cli-${lang}.json`), JSON.stringify(metadata,null,2));
  hashes[lang] = metadata.output_sha256;
}
const server = http.createServer((request, response) => {
  const name = decodeURIComponent(new URL(request.url, 'http://localhost').pathname).replace(/^\//, '');
  const filename = path.resolve(project, name);
  if (!filename.startsWith(project + path.sep) || !fs.existsSync(filename) || !fs.statSync(filename).isFile()) {response.writeHead(404);response.end();return;}
  response.setHeader('Content-Type', filename.endsWith('.html') ? 'text/html; charset=utf-8' : 'image/svg+xml');
  response.end(fs.readFileSync(filename));
});
function check(name, passed) { checks.push({name,passed:!!passed});if(!passed)throw new Error(name); }
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const base=`http://127.0.0.1:${server.address().port}`;
  const browser=await chromium.launch({headless:true,...(options.executable?{executablePath:options.executable}:{})});
  let failure;
  try {
    for(const lang of ['zh','en']) {
      const page=await browser.newPage({viewport:{width:1440,height:1000}});
      page.on('pageerror',error=>errors.push(String(error)));
      await page.goto(`${base}/review-${lang}.html`);
      const frame=page.frameLocator('#notes-product');
      await frame.locator('#purpose').fill(`Persistent draft ${lang}`);
      await frame.locator('#room').selectOption('Forest');
      await frame.locator('#video').check();
      const snapshot=()=>frame.locator('body').evaluate(()=>window.snapshot());
      const expected=JSON.stringify(await snapshot());
      check(`${lang}: default product mode`,await page.locator('#notes-panel').isHidden());
      await page.locator('#notes-toggle').click();
      await page.waitForFunction(()=>document.querySelector('#notes-panel').dataset.notesContext==='#reservation-page');
      check(`${lang}: correct project source visible`,await page.locator('#notes-panel h2').innerText()===copy[lang].page);
      check(`${lang}: shell controls localized`,await page.locator('#notes-toggle').innerText()===(lang==='zh'?'返回产品':'Return to product'));
      await page.locator('[data-notes-zoom]').click();
      check(`${lang}: enlarged real diagram`,await page.locator('#notes-diagram').isVisible()&&await page.locator('#notes-diagram-body img').getAttribute('src').then(src=>src.startsWith('data:image/svg+xml;base64,')));
      await page.screenshot({path:path.join(output,`diagram-${lang}.png`),fullPage:true});
      await page.locator('#notes-diagram-close').click();
      await page.locator('[data-notes-zoom]').click();
      await page.keyboard.press('Escape');
      check(`${lang}: close button and Escape recover`,!await page.locator('#notes-diagram').isVisible());
      check(`${lang}: notes preserve all business values`,JSON.stringify(await snapshot())===expected);
      await frame.locator('#detail-202').click();
      await page.waitForFunction(()=>document.querySelector('#notes-panel').dataset.notesContext==='#reservation-detail');
      check(`${lang}: real second record detail context`,await frame.locator('#selected-record').innerText()==='B-202'&&await page.locator('#notes-panel h2').innerText()===copy[lang].detail);
      check(`${lang}: parent note absent in details`,!await page.locator('[data-notes-zoom]').count());
      await frame.locator('#detail-draft').fill('Unsaved detail draft');
      const detail=JSON.stringify(await snapshot());
      await page.locator('#notes-toggle').click();await page.locator('#notes-toggle').click();
      check(`${lang}: toggling preserves modal and form`,JSON.stringify(await snapshot())===detail);
      const productBox=await page.locator('#notes-product').boundingBox(),panelBox=await page.locator('#notes-panel').boundingBox();
      check(`${lang}: desktop panel participates in layout`,Math.round(productBox.x+productBox.width)<=Math.round(panelBox.x));
      await page.screenshot({path:path.join(output,`detail-${lang}.png`),fullPage:true});
      await frame.locator('#close-detail').click();
      await page.waitForFunction(()=>document.querySelector('#notes-panel').dataset.notesContext==='#reservation-page');
      check(`${lang}: closing detail restores page note`,await frame.locator('#purpose').inputValue()===`Persistent draft ${lang}`);
      await frame.locator('#open-help').click();
      await page.waitForFunction(()=>document.querySelector('#notes-panel').dataset.notesStatus==='empty');
      check(`${lang}: unmapped dialog does not inherit page note`,await page.locator('#notes-panel').getAttribute('data-notes-context')==='');
      await frame.locator('#close-help').click();
      await frame.locator('#archive-view').click();
      await page.waitForFunction(()=>document.querySelector('#notes-panel').dataset.notesStatus==='empty');
      check(`${lang}: hidden mapped page cannot leak its notes`,await page.locator('#notes-panel').getAttribute('data-notes-context')==='');
      await frame.locator('#active-view').click();
      await frame.locator('#open-ambiguous').click();
      await page.waitForFunction(()=>document.querySelector('#notes-panel').dataset.notesStatus==='ambiguous');
      check(`${lang}: ambiguous overlays fail closed`,await page.locator('#notes-panel').getAttribute('data-notes-context')==='');
      // Public optional integration API; simulated product event, not a business-click claim.
      await frame.locator('body').evaluate(()=>window.dispatchEvent(new CustomEvent('ads:context',{detail:{selector:'#custom-one'}})));
      await page.waitForFunction(()=>document.querySelector('#notes-panel').dataset.notesContext==='#custom-one');
      check(`${lang}: product context event resolves custom overlay`,await page.locator('#notes-panel h2').innerText()==='Custom product overlay');
      await frame.locator('#close-ambiguous').click();
      await frame.locator('body').evaluate(()=>window.dispatchEvent(new CustomEvent('ads:context',{detail:{selector:null}})));
      await page.waitForFunction(()=>document.querySelector('#notes-panel').dataset.notesContext==='#reservation-page');
      const mobile=JSON.stringify(await snapshot());
      await page.setViewportSize({width:390,height:844});
      check(`${lang}: mobile notes hide the product surface`,!await page.locator('#notes-product').isVisible()&&await page.locator('#notes-panel').isVisible());
      await page.waitForFunction(()=>document.querySelector('#notes-panel').dataset.notesContext==='#reservation-page');
      check(`${lang}: mobile keeps correct contextual notes`,await page.locator('#notes-panel h2').innerText()===copy[lang].page);
      await page.screenshot({path:path.join(output,`mobile-${lang}.png`),fullPage:true});
      await page.locator('#notes-toggle').click();
      check(`${lang}: mobile return retains product state`,await page.locator('#notes-product').isVisible()&&JSON.stringify(await snapshot())===mobile);
      check(`${lang}: shell no horizontal overflow`,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      await frame.locator('#request-form button').click();
      check(`${lang}: actual business submit remains functional`,(await snapshot()).writes===1&&await frame.locator('#result').innerText()==='Request submitted');
      await page.close();
    }
    check('product source remains byte-identical',fs.readFileSync(productPath,'utf8')===product);
    check('no browser exceptions',errors.length===0);
  }catch(error){failure=error;}
  finally {
    fs.writeFileSync(path.join(output,'browser-results.json'),JSON.stringify({browser:browser.version(),source_sha256:crypto.createHash('sha256').update(product).digest('hex'),output_sha256:hashes,checks,browser_errors:errors,failure:failure?.message||null,not_proven:['formal R0/R1 workspace','real backend','business acceptance','all iframe-compatible products']},null,2));
    await browser.close();await new Promise(resolve=>server.close(resolve));
  }
  if(failure)throw failure;
  console.log(`PASS: ${checks.length} real HTTP browser checks`);
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
