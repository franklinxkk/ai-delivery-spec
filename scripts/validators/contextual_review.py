"""Contextual rendering contracts and hash-bound browser observations.

Never treat JSON content as visible UI. Absent observations remain unverified;
observed omissions are failures. The legacy tab projection keeps its own checks.
"""
from pathlib import Path
import hashlib,json,re
from collections import Counter

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def normalized(value): return re.sub(r'\s+', '', str(value or ''))
def canonical_manifest(value):
    # JSON.stringify uses 1 for 1.0; normalize integral JSON numbers before
    # hashing, preserving arrays and Unicode. The file-byte hash is also checked.
    if isinstance(value,float) and value.is_integer():return int(value)
    if isinstance(value,dict):return {k:canonical_manifest(v) for k,v in value.items()}
    if isinstance(value,list):return [canonical_manifest(v) for v in value]
    return value

def check_contextual(gate,path,raw,doc):
    def issue(code,message,ref='',severity='BLOCK'):
        gate.add(severity,'PROTO-CONTEXTUAL-'+code,path,message,str(ref),affected_consumers=('product','frontend','backend','qa'))
    contexts={c['context_ref']:c for c in doc.get('review_contexts',[])}
    points={p['ref']:p for p in doc.get('review_points',[])}
    semantics=doc.get('semantic_coverage_items',[])
    examples={e['example_ref']:e for e in doc.get('acceptance_examples',[])}
    diagrams={d['diagram_ref']:d for d in doc.get('diagram_contract',{}).get('diagrams',[])}
    presentation=doc.get('presentation',{})
    if doc.get('workspace',{}).get('review_level')!='R0':
        issue('REVIEW-LEVEL','contextual-v1 动态投影目前只支持 R0；R1 采用已实现记录/分享合同的静态 contextual 起点，不能跳过这些能力')
    views=presentation.get('contexts',[]); viewmap={c.get('context_ref'):c for c in views}
    if len(viewmap)!=len(views) or set(viewmap)!=set(contexts):
        issue('CONTEXT-BINDING','呈现上下文与声明分母不一致',sorted(set(viewmap)^set(contexts)))
    bound=[]
    for ref,c in viewmap.items():
        if not c.get('root_selector') or not c.get('task'):issue('CONTEXT-BINDING','上下文缺少产品根或任务说明',ref)
        refs=[p.get('ref') for p in c.get('point_views',[])]
        if refs!=contexts.get(ref,{}).get('review_point_refs',[]):issue('POINT-BINDING','呈现顺序与当前上下文声明不一致',ref)
        bound.extend(refs)
        for v in c.get('point_views',[]):
            if {'summary','title','selector','examples'} & v.keys():issue('DUPLICATE-TRUTH','呈现配置重复维护业务说明；应读取正式声明',v.get('ref'))
        for sec in c.get('source_sections',[]):
            if sec not in presentation.get('sections',{}):issue('SOURCE-SECTION','模块正文引用不存在',ref+'/'+sec)
        if c.get('diagram_ref') and c['diagram_ref'] not in diagrams:issue('DIAGRAM-BINDING','引用了未声明的业务图',ref)
    if Counter(bound)!=Counter(points.keys()):issue('POINT-BINDING','每个正式评审点须在一个上下文呈现一次')
    for s in semantics:
        if s.get('coverage_status')=='not_applicable':continue
        ps=[points.get(r) for r in s.get('review_point_refs',[])]
        if not ps or any(not p or p.get('owner_context_ref')!=s.get('owner_context_ref') for p in ps):
            issue('SEMANTIC-BINDING','语义覆盖没有绑定同一上下文的正式说明',s.get('coverage_id'))
    for ref,d in diagrams.items():
        resource=presentation.get('diagrams',{}).get(ref)
        if not resource or not resource.get('src') or not resource.get('title'):issue('DIAGRAM-BINDING','图声明没有可加载的呈现资源',ref)
    if set(presentation.get('diagrams',{}))!=set(diagrams):issue('DIAGRAM-BINDING','图资源与正式图声明不一致')
    for ref,p in points.items():
        if p.get('owner_context_ref') not in contexts:issue('POINT-BINDING','评审点归属上下文不存在',ref)
        if not p.get('summary') or not p.get('source_refs'):issue('POINT-CONTENT','缺少业务说明或来源',ref)
        if p.get('marker_required') and not p.get('target_selector'):issue('TARGET','需要标记的点缺少目标选择器',ref)
    if 'id="ads-review-data"' in raw:issue('DUPLICATE-TRUTH','仍存在独立的旧评审业务数据源')
    # The metadata declares assembly, not proof that JS consumed it.
    if not re.search(r'data-review-renderer=[\'\"]contextual-v1[\'\"]',raw):issue('RENDERER','未声明与本呈现合同对应的实际评审根')
    for c in contexts.values():
        p=c.get('product_location',{})
        if c.get('context_type')!='VIEW' and p.get('parent_view_ref') not in contexts:issue('LOCATION','浮层缺少有效的父页面',c['context_ref'])
    baseline=doc.get('baseline',{})
    for key,hashkey,normalize in [('requirement_ref','hash',True),('source_file','source_file_sha256',False)]:
        if not baseline.get(key):continue
        source=(Path(path).parent/baseline[key]).resolve()
        if not source.is_file():issue('SOURCE','绑定的来源文件不存在',baseline[key]);continue
        actual=hashlib.sha256(source.read_text(encoding='utf8').replace('\r\n','\n').replace('\r','\n').encode()).hexdigest() if normalize else digest(source)
        if actual!=baseline.get(hashkey):issue('SOURCE','实际来源与所绑定指纹不同',baseline[key])
    evidence_path=getattr(gate,'review_runtime_evidence',None)
    if not evidence_path:
        issue('RUNTIME-UNVERIFIED','动态呈现声明已检查；尚无当前文件的浏览器观察，不能判定内容可达或完成验收','--review-runtime-evidence',severity='GAP')
        return {p.get('target_ref') for p in points.values() if p.get('marker_required')}
    try:e=json.loads(Path(evidence_path).read_text(encoding='utf8'))
    except (OSError,ValueError) as ex:issue('EVIDENCE','浏览器证据无法读取',str(ex));return set()
    if e.get('schema_version')!=1 or e.get('prototype_sha256')!=digest(path):
        issue('EVIDENCE-DRIFT','浏览器证据不属于当前原型；修改后须重新采集',evidence_path);return set()
    manifest_raw=re.search(r'<script\b[^>]*id=[\'\"]review-workspace-manifest[\'\"][^>]*>(.*?)</script>',raw,re.S)
    manifest_text=(manifest_raw[1] if manifest_raw else '') if e.get('manifest_hash_format')=='embedded-json-bytes-v1' else json.dumps(canonical_manifest(doc),sort_keys=True,ensure_ascii=False,separators=(',',':'))
    if not manifest_text or e.get('manifest_sha256')!=hashlib.sha256(manifest_text.encode()).hexdigest():
        issue('EVIDENCE-DRIFT','浏览器证据的声明指纹不一致',evidence_path);return set()
    observations=e.get('observations',[])
    # Only current-file, current-manifest browser observations may resolve a
    # static dynamic-template false negative; declaration alone never does.
    gate.runtime_verified_actions={a.upper() for o in observations if o.get('capture_method') in {'browser_ui','fixture_then_browser_ui'} and o.get('panel_visible') and o.get('current_context')==o.get('context_ref') for a in o.get('visible_actions',[]) if isinstance(a,str)}
    observed={o.get('context_ref') for o in observations}
    missing=set(contexts)-observed
    if missing:issue('CONTEXT-UNVERIFIED','这些上下文没有实际浏览器观察',', '.join(sorted(missing)),severity='GAP')
    unexpected=observed-set(contexts)
    if unexpected:issue('UNDECLARED-CONTEXT','出现未声明的业务上下文',sorted(unexpected))
    seen_examples=set();seen_diagrams=set();seen_targets=set()
    for o in observations:
        ref=o.get('context_ref');c=contexts.get(ref)
        if not c:continue
        if o.get('capture_method') not in {'browser_ui','fixture_then_browser_ui'} or not o.get('trigger'):
            issue('EVIDENCE','缺少实际操作方式和入口记录',ref)
        if o.get('current_context')!=ref or o.get('detected_context')!=ref:issue('CONTEXT','业务上下文与说明不一致',ref)
        if not o.get('panel_visible') or not o.get('product_root_visible'):issue('VISIBILITY','当前说明或业务界面不可见',ref)
        if o.get('fingerprint_before')!=o.get('fingerprint_after') or not o.get('fingerprint_before'):issue('SIDE-EFFECT','评审展开前后业务指纹变化或未采集',ref)
        if o.get('runtime_errors'):issue('RUNTIME','浏览器或评审运行错误',ref)
        expected=c['review_point_refs'];cards=o.get('cards',[])
        if [p.get('ref') for p in cards]!=expected:issue('POINT-COVERAGE','实际卡片缺失、重复、错序或混入其他上下文',ref)
        for card in cards:
            p=points.get(card.get('ref'))
            if not p:continue
            if not card.get('visible') or normalized(p['summary']) not in normalized(card.get('text')):
                issue('POINT-CONTENT','展开后未看到对应业务说明',card.get('ref'))
            if p.get('implementation_detail',{}).get('required') and not card.get('implementation_visible'):
                issue('IMPLEMENTATION','关键操作缺少可展开阅读的同源模块实施与验收依据',p['ref'])
            target=card.get('target',{})
            if target.get('count',0)>1:issue('TARGET','定位匹配多个可见对象，不能任选一个',p['ref'])
            status=target.get('status'); condition=target.get('applicability') or {}
            refs=set(condition.get('source_refs') or [])
            known_refs=set(p.get('precondition_refs',[])) | set(p.get('source_refs',[]))
            observed_condition=(isinstance(condition.get('applies'),bool) and bool(condition.get('reason'))
                and bool(refs) and refs <= known_refs and isinstance(condition.get('observed'),dict) and bool(condition['observed']))
            if target.get('count')==1:
                seen_targets.add(p['ref'])
                if observed_condition and not condition['applies']:
                    issue('TARGET','条件观察为不适用，但目标仍显示；核对业务条件与实际界面',p['ref'])
            elif p.get('marker_required'):
                if status in {'missing','invalid_selector','missing_context','condition_conflict'} or (observed_condition and condition['applies']):
                    issue('TARGET','当前上下文定位失败；检查选择器、产品根及实际适用条件，不能用兜底说明代替',p['ref'])
                elif status=='not_applicable' and observed_condition and not condition['applies']:
                    pass  # A real condition observation explains this absence; it is not a visible-target pass.
                else:
                    issue('TARGET-CONDITION-UNVERIFIED','目标未出现，尚无绑定来源的适用条件观察；补当前状态及条件依据后重采集',p['ref'],severity='GAP')
        for example in o.get('examples',[]):
            declared=examples.get(example.get('ref'))
            if not declared or declared.get('owner_context_ref')!=ref:issue('EXAMPLE','出现未声明或跨上下文示例',example.get('ref'));continue
            seen_examples.add(example['ref'])
            if not example.get('visible') or any(normalized(declared[k]) not in normalized(example.get('text')) for k in ['precondition','action','expected_visible_result','expected_domain_result']):
                issue('EXAMPLE','示例展开后缺少前提、操作或结果',example['ref'])
        for diagram in o.get('diagrams',[]):
            if diagram.get('ref') not in diagrams:issue('DIAGRAM','存在未声明的图',diagram.get('ref'));continue
            seen_diagrams.add(diagram['ref'])
            if not diagram.get('thumbnail_visible') or not diagram.get('image_loaded') or not diagram.get('viewer_opened'):issue('DIAGRAM','图未加载或不能通过缩略图打开',diagram['ref'])
        if not o.get('return_preserves_context'):issue('RETURN','关闭图表后未恢复原说明上下文',ref)
    for ref in set(examples)-seen_examples:issue('EXAMPLE','声明的示例没有实际展开证据',ref)
    for ref in set(diagrams)-seen_diagrams:issue('DIAGRAM','声明的图没有实际打开证据',ref)
    for ref,p in points.items():
        if p.get('marker_required') and ref not in seen_targets:
            issue('TARGET-UNVERIFIED','条件目标尚无出现时的唯一定位证据',ref,severity='GAP')
    gate.metrics['contextual_runtime_observed_contexts']=len(observed&set(contexts))
    gate.metrics['contextual_runtime_observed_examples']=len(seen_examples)
    gate.metrics['contextual_runtime_observed_diagrams']=len(seen_diagrams)
    gate.metrics['contextual_runtime_scope']='browser projection and bindings; not business acceptance or backend integration'
    return {p.get('target_ref') for p in points.values() if p.get('marker_required')}

def check_document_sections(gate,path,prd,doc):
    """Validate human-PRD provenance without pretending local UI IDs are PRD IDs.

    This deliberately does not certify structured machine handoff. R0 only.
    Each copied module body must equal its actual Markdown section, and each
    point's declared source must include its actual displayed source section.
    """
    def issue(code,message,ref=''):
        gate.add('BLOCK','PROTO-CONTEXTUAL-'+code,path,message,ref)
    if doc.get('workspace',{}).get('review_level')!='R0' or doc.get('machine_handoff',{}).get('status')=='ready':
        issue('SOURCE-MODE','文档章节追溯仅适用于未签署 R0；正式机器交接不能省略编号合同')
    parts=re.split(r'(?m)^## \[(REQ-[A-Z0-9-]+)\] (.+)\n',prd)
    sections={parts[i]:{'title':parts[i+1], 'body':parts[i+2]} for i in range(1,len(parts)-2,3)}
    p=doc.get('presentation',{})
    for key,value in p.get('sections',{}).items():
        ref='REQ-'+key.replace('.','-');actual=sections.get(ref)
        lines=[]
        for block in value.get('blocks',[]):
            if 'rows' in block:lines.extend(' | '.join(row) for row in block['rows'])
            else:lines.append(block.get('text',''))
        if not actual or normalized(actual['title'])!=normalized(value.get('title')) or normalized(actual['body'])!=normalized('\n'.join(lines)):
            issue('SOURCE-CONTENT','呈现模块正文与本次权威 PRD 文本投影不一致',ref)
    bindings={v['ref']:v for c in p.get('contexts',[]) for v in c.get('point_views',[])}
    for point in doc.get('review_points',[]):
        sources=set(point.get('source_refs',[]));view=bindings.get(point['ref'],{});source='REQ-'+str(view.get('source','')).replace('.','-')
        if not sources or sources-set(sections) or source not in sources:
            issue('SOURCE-REF','评审点须引用真实章节，且与展开的同源正文相符',point['ref'])
    for item in doc.get('semantic_coverage_items',[]):
        if not item.get('source_refs') or set(item['source_refs'])-set(sections):
            issue('SOURCE-REF','语义项来源章节不存在',item.get('coverage_id',''))
    gate.metrics['handoff_scope']='human PRD section provenance; structured ID handoff not claimed'
    gate.add('INFO','PROTO-CONTEXTUAL-DOCUMENT-SOURCE',path,'本次按真实文档章节追溯；UI/评审本地编号不是 PRD 编号，不声明结构化机器交接通过','document_sections')
