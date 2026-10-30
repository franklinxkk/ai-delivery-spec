"""Presentation-only transform of the worked starter; never migrates a product."""
import json,re

def contextual_values(values):
    doc=json.loads(values['review.json']);doc['workspace']['presentation_mode']='contextual'
    values['review.json']=json.dumps(doc,ensure_ascii=False,indent=2)+'\n'
    layout=values['layout.html']
    layout=re.sub(r'<nav\b[^>]*>(?:(?!</nav>).)*data-review-tab-target=(?:(?!</nav>).)*</nav>','',layout,flags=re.S)
    names={'overview':'整体与流程','function_flow':'当前功能说明','boundary_acceptance':'边界与验收'}
    for key,label in names.items():
        layout=layout.replace('<section data-review-tab="'+key+'">','<section data-review-tab="'+key+'"><h3>'+label+'</h3>')
    layout=layout.replace('<body>','<body class="ads-collapsed">',1)
    launcher='<button id="contextual-launcher" data-action="UIACT-REVIEW-TOGGLE" data-ads-act="expand">查看当前功能说明</button>'
    viewer='<dialog id="contextual-diagram-viewer" aria-label="业务流程放大图"><button data-action="UIACT-REVIEW-DIAGRAM-CLOSE">关闭图示</button><div id="contextual-diagram-body"></div></dialog>'
    layout=layout.replace('</body>',launcher+viewer+'</body>')
    layout=re.sub(r'(<figure\b[^>]*data-review-diagram="([^"]+)"[^>]*>)',lambda m:'<button class="contextual-diagram-open" data-action="UIACT-REVIEW-DIAGRAM" data-diagram="'+m[2]+'">放大流程图</button>'+m[1],layout)
    values['layout.html']=layout
    values['style.css']+='''
/* contextual: the product remains in place; instructions use the existing right surface. */
body:not(.ads-collapsed){grid-template-columns:minmax(0,1fr) var(--review-width)}
#contextual-launcher{position:fixed;right:18px;top:12px;z-index:110}
body:not(.ads-collapsed) #contextual-launcher,body.ads-collapsed .marker{display:none}
[data-review-workspace] h3{font-size:16px;margin:16px 0 10px}
[data-review-workspace] figure{max-height:180px;overflow:hidden;cursor:zoom-in}
.contextual-diagram-open{margin:8px 0;border:1px solid #bacbdc;border-radius:6px;padding:6px 12px;background:#f3f7fb;color:#204f79}
#contextual-diagram-viewer{width:min(1000px,90vw);max-height:85vh;border:1px solid #bacbdc;border-radius:10px;padding:24px}
#contextual-diagram-viewer::backdrop{background:#142a4555}
#contextual-diagram-viewer figure{max-height:none;font-size:18px}
'''
    runtime=values['runtime.js'].replace("all('[data-review-tab]').forEach(n=>n.hidden=n.dataset.reviewTab!==review.tab);","all('[data-review-tab]').forEach(n=>n.hidden=false);")
    runtime=re.sub(r"^\s*'UIACT-REVIEW-TAB':.*?\n",'',runtime,flags=re.M)
    addition='''
actionRegistry['UIACT-REVIEW-DIAGRAM']=node=>{const source=all('[data-review-diagram]').find(e=>e.dataset.reviewDiagram===node.dataset.diagram);if(!source)return;const copy=source.cloneNode(true);copy.removeAttribute('data-review-diagram');copy.querySelectorAll('[id]').forEach(e=>e.removeAttribute('id'));q('#contextual-diagram-body').replaceChildren(copy);q('#contextual-diagram-viewer').showModal()};
actionRegistry['UIACT-REVIEW-DIAGRAM-CLOSE']=()=>q('#contextual-diagram-viewer').close();
'''
    runtime=runtime.replace("document.addEventListener('click',event=>",addition+"\ndocument.addEventListener('click',event=>",1)
    runtime=re.sub(r'function resolveReviewTarget\(selector\)\{.*?\n', "function resolveReviewTarget(selector){const r=ADSReviewTargets.resolve({root:currentContextRoot(),selector});if(!r.el)fail('PROTO-REVIEW-TARGET-'+r.status.toUpperCase());return r.el}\n",runtime,count=1)
    values['runtime.js']=runtime
    return values
