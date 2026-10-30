"""Local product companion; intentionally not a formal review-workspace manifest.

Markdown owns the notes. The isolated renderer only reads the existing product DOM.
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

MARKER = '<!-- ADS local context notes companion -->'


def image_url(value: str, notes: Path) -> str:
    """Embed only project-local images, never fetch URLs or arbitrary local files."""
    parts = urlsplit(value)
    if parts.scheme or parts.netloc or parts.query or parts.fragment:
        raise ValueError('图示须为说明目录内的相对文件 / diagrams must be local relative files')
    path = (notes.parent / unquote(parts.path)).resolve()
    if not path.is_relative_to(notes.parent.resolve()) or not path.is_file():
        raise ValueError('图示缺失或越出说明目录 / diagram missing or outside notes directory: ' + value)
    types = {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
             '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp'}
    if path.suffix.lower() not in types:
        raise ValueError('不支持的图示格式 / unsupported diagram format: ' + path.suffix)
    return 'data:' + types[path.suffix.lower()] + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def inline(text: str) -> str:
    # Deliberately small Markdown subset; raw HTML is text, never executable markup.
    value = html.escape(text)
    value = re.sub(r'`([^`]+)`', r'<code>\1</code>', value)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', value)


def render_blocks(lines: list[str], notes: Path) -> str:
    result, paragraph, listing, code = [], [], [], None

    def flush():
        if paragraph:
            result.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()
        if listing:
            result.append('<ul>' + ''.join('<li>' + inline(item) + '</li>' for item in listing) + '</ul>')
            listing.clear()

    for line in lines:
        if line.startswith('```'):
            flush()
            if code is None:
                code = []
            else:
                result.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
                code = None
            continue
        if code is not None:
            code.append(line)
            continue
        image = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        heading = re.fullmatch(r'#{3,6}\s+(.+)', line)
        item = re.fullmatch(r'\s*[-*]\s+(.+)', line)
        if image:
            flush()
            src, alt = image_url(image[2], notes), html.escape(image[1], quote=True)
            result.append('<figure><button type="button" data-notes-zoom aria-label="' + alt + '"><img src="' + src + '" alt="' + alt + '"></button><figcaption>' + alt + '</figcaption></figure>')
        elif heading:
            flush()
            result.append('<h3>' + inline(heading[1]) + '</h3>')
        elif item:
            if paragraph:
                flush()
            listing.append(item[1])
        elif not line.strip():
            flush()
        else:
            if listing:
                flush()
            paragraph.append(line.strip())
    flush()
    if code is not None:
        raise ValueError('说明中有未关闭代码块 / unclosed fenced block')
    return '\n'.join(result)


def read_sections(notes: Path) -> list[dict]:
    """Each H2 has one CSS-context comment; H3 and lower stay in that section."""
    sections, current, fenced = [], None, False
    for line in notes.read_text(encoding='utf-8-sig').splitlines():
        if line.startswith('```'):
            fenced = not fenced
        heading = None if fenced else re.fullmatch(r'##\s+(.+)', line)
        mapping = None if fenced else re.fullmatch(r'\s*<!--\s*context:\s*(.+?)\s*-->\s*', line)
        if heading:
            current = {'title': heading[1], 'selector': '', 'lines': []}
            sections.append(current)
        elif mapping:
            if current is None or current['selector']:
                raise ValueError('每个二级标题后须且仅须一个 context 注释 / one context comment per H2')
            current['selector'] = mapping[1]
        elif current is not None:
            current['lines'].append(line)
        elif line.strip() and not line.startswith('# '):
            raise ValueError('说明正文应位于带 context 的二级标题下 / place notes under mapped H2 headings')
    if not sections or any(not item['selector'] for item in sections):
        raise ValueError('每个二级标题需要 <!-- context: CSS选择器 --> / each H2 needs a context selector')
    if len({item['selector'] for item in sections}) != len(sections):
        raise ValueError('context 选择器重复 / duplicate context selector')
    return [{'title': item['title'], 'selector': item['selector'],
             'html': render_blocks(item['lines'], notes)} for item in sections]


STYLE = r'''
*{box-sizing:border-box}html,body{height:100%;margin:0}body{font:15px/1.55 system-ui,sans-serif;color:#183147;background:#f5f7fa;display:grid;grid-template-rows:36px minmax(0,1fr)}
button{font:inherit;cursor:pointer;border:1px solid #bbcad5;border-radius:5px;background:white;color:#183147;padding:5px 12px}button:focus-visible{outline:3px solid #1774bc;outline-offset:2px}
#notes-toolbar{display:flex;justify-content:flex-end;align-items:center;border-bottom:1px solid #dce3e9;padding:2px 12px;gap:12px}#notes-toolbar a{color:#345879;font-size:12px}#notes-toggle{font-size:12px;padding:2px 10px}
#notes-shell{position:relative;display:grid;grid-template-columns:minmax(0,1fr);min-height:0}#notes-shell.is-open{grid-template-columns:minmax(0,1fr) minmax(300px,380px)}#notes-product{border:0;width:100%;height:100%;background:white}
#notes-panel{min-height:0;overflow:auto;border-left:1px solid #dce3e9;padding:20px;background:#f8fafc;overflow-wrap:anywhere}#notes-panel[hidden]{display:none}#notes-panel h2{font-size:20px;margin:0 0 14px}#notes-panel h3{font-size:16px;margin:22px 0 8px}#notes-panel p{margin:10px 0}#notes-panel ul{padding-left:22px}#notes-panel pre{white-space:pre-wrap;background:#edf1f5;padding:12px}#notes-panel code{font-size:13px}#notes-panel figure{margin:18px 0}#notes-panel figure button{width:100%;padding:8px;cursor:zoom-in}#notes-panel img{display:block;width:100%;max-height:180px;object-fit:contain}#notes-panel figcaption{font-size:12px;color:#566b7e;margin-top:4px}
#notes-diagram{max-width:94vw;width:1100px;max-height:90vh;border:1px solid #aabecf;border-radius:10px;padding:16px}#notes-diagram::backdrop{background:#162d4866}#notes-diagram header{display:flex;align-items:center;justify-content:space-between;gap:20px}#notes-diagram-body{overflow:auto;max-height:75vh;padding-top:12px}#notes-diagram-body img{display:block;max-width:none;min-width:100%;height:auto}#notes-status{font-size:13px;color:#657887}#notes-boundary{font-size:12px;color:#657887;border-top:1px solid #dce3e9;padding-top:14px}
@media(max-width:760px){#notes-shell.is-open{grid-template-columns:minmax(0,1fr)}#notes-shell.is-open #notes-product{visibility:hidden;pointer-events:none}#notes-panel{position:absolute;inset:0;border-left:0}#notes-diagram{width:94vw}}
'''

# Public, reusable renderer: mount reads the product window and owns only its host.
# It never dispatches business clicks, writes product attributes, or clones product UI.
RUNTIME = r'''
(() => {
  'use strict';
  const labels = {
    zh: {open:'查看当前说明', close:'返回产品', direct:'打开原产品', product:'产品页面', empty:'当前页面或浮层尚无对应说明', ambiguous:'当前上下文不唯一，请核对项目映射', inaccessible:'无法读取产品上下文。请通过本地同源 HTTP 打开。', title:'当前功能说明', zoom:'放大图示：', closeImage:'关闭图示', boundary:'项目附加说明；不代表正式 R0/R1 合同或验收已通过。'},
    en: {open:'Read current notes', close:'Return to product', direct:'Open original product', product:'Product page', empty:'No notes mapped to the current page or overlay', ambiguous:'The current context is ambiguous; check the project mapping', inaccessible:'Cannot read product context. Open through same-origin local HTTP.', title:'Current feature notes', zoom:'Enlarge diagram: ', closeImage:'Close diagram', boundary:'Project companion notes; no formal R0/R1 contract or acceptance claim.'}
  };
  function mount({frame, host, sections, language='zh'}) {
    const t=labels[language] || labels.zh;
    const shell=document.getElementById('notes-shell'), toggle=document.getElementById('notes-toggle');
    const dialog=document.getElementById('notes-diagram'), imageBody=document.getElementById('notes-diagram-body');
    let observer, cleanup=[], scheduled=false, currentKey='', explicit=null, scrolls=new Map();
    const visible=node=>{
      if(!node || !node.isConnected || !node.getClientRects().length)return false;
      for(let n=node;n && n.nodeType===1;n=n.parentElement){const s=n.ownerDocument.defaultView.getComputedStyle(n);if(n.hidden || s.display==='none' || s.visibility==='hidden' || s.visibility==='collapse' || s.opacity==='0')return false;}
      return true;
    };
    function choose(candidates) {
      const deepest=candidates.filter(n=>!candidates.some(other=>n!==other && n.contains(other)));
      if(deepest.length===1)return deepest[0];
      // CSS z-index alone cannot order separate stacking contexts or top layers.
      // Custom simultaneous overlays can use the product's explicit context event.
      return null;
    }
    function resolve(doc) {
      const matches=[];
      for(const section of sections){
        let nodes;
        try { nodes=[...doc.querySelectorAll(section.selector)].filter(visible); }
        catch { return {status:'ambiguous'}; }
        if(nodes.length>1)return {status:'ambiguous'};
        if(nodes.length===1)matches.push({node:nodes[0],section});
      }
      // Only real product roots are observed. Unknown overlays block parent notes.
      const overlays=[...doc.querySelectorAll('dialog[open],[role="dialog"],[role="alertdialog"],[aria-modal="true"],[popover]:popover-open')].filter(visible);
      const roots=[...doc.querySelectorAll('[data-ads-context]')].filter(visible);
      let target;
      if(explicit!==null){
        let chosen;
        try { chosen=[...doc.querySelectorAll(explicit)].filter(visible); } catch { return {status:'ambiguous'}; }
        if(chosen.length!==1)return {status:'empty'};
        target=chosen[0];
        if(overlays.length && !overlays.some(n=>n===target || n.contains(target)))return {status:'empty'};
      } else {
        const candidates=overlays.length?overlays:[...new Set([...roots,...matches.map(m=>m.node)])];
        if(!candidates.length)return {status:'empty'};
        target=choose(candidates);
        if(!target)return {status:'ambiguous'};
      }
      const mapping=matches.filter(m=>m.node===target);
      return mapping.length===1?{status:'mapped',section:mapping[0].section}:{status:mapping.length?'ambiguous':'empty'};
    }
    function render(state) {
      const key=JSON.stringify([state.status,state.section?.selector]);
      if(key===currentKey)return;
      if(dialog.open)dialog.close();
      if(currentKey)scrolls.set(currentKey,host.scrollTop);
      currentKey=key;
      host.dataset.notesContext=state.section?.selector || '';
      host.dataset.notesStatus=state.status;
      const heading=document.createElement('h2');heading.textContent=state.section?.title || t.title;
      const content=document.createElement('div');
      if(state.section)content.innerHTML=state.section.html;
      else {content.id='notes-status';content.setAttribute('role','status');content.textContent=t[state.status];}
      const boundary=document.createElement('p');boundary.id='notes-boundary';boundary.textContent=t.boundary;
      host.replaceChildren(heading,content,boundary);
      host.querySelectorAll('[data-notes-zoom]').forEach(button=>button.setAttribute('aria-label',t.zoom+button.querySelector('img').alt));
      host.scrollTop=scrolls.get(key)||0;
    }
    function refresh(){scheduled=false;try { if(!['http:','https:'].includes(location.protocol) || !['localhost','127.0.0.1','[::1]'].includes(location.hostname))throw new Error('local HTTP required');const doc=frame.contentDocument;if(!doc || !doc.documentElement)throw new Error('inaccessible');render(resolve(doc)); } catch {render({status:'inaccessible'});} }
    function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(refresh);}}
    function bind(){
      observer?.disconnect();cleanup.forEach(fn=>fn());cleanup=[];explicit=null;currentKey='';
      try {
        const win=frame.contentWindow,doc=frame.contentDocument;
        if(!doc || !doc.documentElement)throw new Error('inaccessible');
        observer=new MutationObserver(schedule);observer.observe(doc.documentElement,{subtree:true,childList:true,attributes:true});
        for(const name of ['resize','hashchange','popstate','transitionend','animationend','toggle','click','input']){
          win.addEventListener(name,schedule,true);cleanup.push(()=>win.removeEventListener(name,schedule,true));
        }
        // Optional product event for custom page/overlay implementations. Null resumes detection.
        const onContext=event=>{explicit=typeof event.detail?.selector==='string'?event.detail.selector:null;schedule();};
        win.addEventListener('ads:context',onContext);cleanup.push(()=>win.removeEventListener('ads:context',onContext));
      }catch { /* refresh renders an honest unavailable state. */ }
      refresh();
    }
    toggle.addEventListener('click',()=>{
      const open=host.hidden;host.hidden=!open;shell.classList.toggle('is-open',open);
      toggle.textContent=open?t.close:t.open;toggle.setAttribute('aria-expanded',String(open));schedule();
    });
    host.addEventListener('click',event=>{
      const button=event.target.closest('[data-notes-zoom]');if(!button)return;
      event.preventDefault();event.stopPropagation();
      imageBody.replaceChildren(button.querySelector('img').cloneNode(true));
      document.getElementById('notes-diagram-title').textContent=button.querySelector('img').alt;
      dialog.showModal();
    });
    document.getElementById('notes-diagram-close').addEventListener('click',()=>dialog.close());
    frame.addEventListener('load',bind);bind();
    return Object.freeze({refresh, getContext:()=>({selector:host.dataset.notesContext,status:host.dataset.notesStatus})});
  }
  window.ADSContextNotes=Object.freeze({mount});
})();
'''


def attach_notes(prototype: Path, notes: Path, output: Path | None = None, language: str = 'zh') -> dict:
    prototype, notes = prototype.resolve(), notes.resolve()
    output = (output or prototype.with_name(prototype.stem + '-review.html')).resolve()
    if language not in {'zh', 'en'}:
        raise ValueError('language must be zh or en')
    if not prototype.is_file() or prototype.suffix.lower() not in {'.html', '.htm'}:
        raise ValueError('prototype must be an existing local HTML file')
    if not notes.is_file() or not notes.is_relative_to(prototype.parent):
        raise ValueError('notes must be an existing file inside the product directory')
    if output.parent != prototype.parent or output in {prototype, notes} or output.suffix.lower() not in {'.html', '.htm'}:
        raise ValueError('output must be a separate HTML beside the original product')
    if output.exists() and MARKER not in output.read_text(encoding='utf-8')[:200]:
        raise ValueError('refusing to overwrite an existing non-companion file')
    product = prototype.read_text(encoding='utf-8-sig')
    if 'review-workspace-manifest' in product or 'data-review-workspace=' in product or MARKER in product:
        raise ValueError('product already has a review surface; update its existing renderer instead')
    sections = read_sections(notes)
    data = json.dumps({'sections': sections, 'language': language}, ensure_ascii=False).replace('<', '\\u003c')
    src = html.escape(quote(prototype.name), quote=True)
    title = '当前功能说明' if language == 'zh' else 'Current feature notes'
    direct = '打开原产品' if language == 'zh' else 'Open original product'
    opened = '查看当前说明' if language == 'zh' else 'Read current notes'
    close = '关闭图示' if language == 'zh' else 'Close diagram'
    rendered = f'''<!doctype html>
{MARKER}
<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{STYLE}</style></head>
<body><header id="notes-toolbar"><a href="{src}" target="_blank" rel="noopener">{direct}</a><button id="notes-toggle" type="button" aria-controls="notes-panel" aria-expanded="false">{opened}</button></header>
<main id="notes-shell"><iframe id="notes-product" src="{src}" title="{direct}"></iframe><aside id="notes-panel" aria-label="{title}" hidden></aside></main>
<dialog id="notes-diagram" aria-labelledby="notes-diagram-title"><header><strong id="notes-diagram-title"></strong><button id="notes-diagram-close" type="button">{close}</button></header><div id="notes-diagram-body"></div></dialog>
<script id="ads-context-notes-source" type="application/json">{data}</script><script>{RUNTIME}
const notesData=JSON.parse(document.getElementById('ads-context-notes-source').textContent);
window.adsNotes=ADSContextNotes.mount({{frame:document.getElementById('notes-product'),host:document.getElementById('notes-panel'),...notesData}});
</script></body></html>'''
    output.write_text(rendered, encoding='utf-8', newline='\n')
    return {'status': 'attached_notes_not_validated', 'output': str(output),
            'delivery': 'local_same_origin_http_companion_not_single_html',
            'required_files': [str(output), str(prototype)],
            'additional_dependencies': 'Keep all original product resources at their existing relative paths.',
            'editable_source': str(notes), 'contexts': [item['selector'] for item in sections],
            'source_sha256': hashlib.sha256(prototype.read_bytes()).hexdigest(),
            'notes_sha256': hashlib.sha256(notes.read_bytes()).hexdigest(),
            'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'not_proven': ['formal R0/R1 contract', 'business completeness', 'browser behavior', 'production acceptance']}
