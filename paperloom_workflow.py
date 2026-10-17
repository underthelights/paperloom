"""Persistent intake-to-library orchestration; paper IDs own all reader artifacts."""
import json,re,threading,time
import research as R
import intake,reader,discovery
ACTIVE=set()

def init():
    with R.db() as c:c.execute('CREATE TABLE IF NOT EXISTS library_links(inbox_id TEXT NOT NULL,paper_id TEXT NOT NULL,collection TEXT NOT NULL,concepts TEXT NOT NULL,PRIMARY KEY(inbox_id,paper_id))')
    for item in intake.state():
        if item.get('pipeline',{}).get('status')=='running':
            update(item['id'],status='interrupted',stage='재시작 필요',error='앱 종료로 연결 작업이 중단되었습니다. 이어서 처리할 수 있습니다.')

def update(iid,**values):
    with R.LOCK:
        item=intake.get(iid);item.setdefault('pipeline',{}).update(values);intake.save(item)

def bind(iid,pid):
    with R.LOCK:
        item=intake.get(iid);result=item.get('result') or {};collection=result.get('collection','미분류');concepts=result.get('concepts',[])
        with R.db() as c:c.execute('INSERT OR REPLACE INTO library_links VALUES(?,?,?,?)',(iid,pid,collection,json.dumps(concepts,ensure_ascii=False)))
        p=R.get(pid);p['category']=collection;R.save(p)
        import knowledge
        for name in concepts:
            if isinstance(name,str) and name.strip():knowledge.create(name[:120],pid)

def reclassify(iid):
    with R.db() as c:ids=[r[0] for r in c.execute('SELECT paper_id FROM library_links WHERE inbox_id=?',(iid,))]
    for pid in ids:bind(iid,pid)

def evidence_papers(item):
    text='\n'.join(m['content'] for m in item['messages'] if m['role']=='user');materials=item.get('materials',[])
    direct=[]
    for value in re.findall(r'https?://[^\s<>\]\)]+',text)+[text.strip()]:
        aid=R.arxiv_id(value.rstrip('.,;'))
        if aid:direct.append({'url':'https://arxiv.org/abs/'+aid,'basis':'user-link'})
    if not direct:
        for material in materials:
            for url in material.get('paper_links',[]):
                if R.arxiv_id(url):direct.append({'url':url,'basis':'source-link','source':material['url']})
    if not direct:
        for row in item.get('pipeline',{}).get('items',[]):
            if row.get('paper_id'):
                p=R.get(row['paper_id'])
                if p.get('arxiv'):direct.append({'url':'https://arxiv.org/abs/'+p['arxiv'],'basis':'existing-library-link'})
    # Model-suggested papers require an exact title mention in supplied evidence.
    evidence=R.norm(text+' '+' '.join(m.get('text','') for m in materials))
    for candidate in (item.get('result') or {}).get('papers',[]):
        if len(candidate.get('title',''))>=15 and R.norm(candidate['title']) in evidence:
            direct.append({**candidate,'basis':'explicit-title'})
    unique={}
    for candidate in direct:
        aid=R.arxiv_id(candidate['url']);key=re.sub(r'v\d+$','',aid)
        unique.setdefault(key,candidate)
    return list(unique.values())

def start(iid,retry=False):
    with R.LOCK:
        if iid in ACTIVE:return intake.get(iid)
        item=intake.get(iid)
        if not item.get('result'):raise ValueError('분류 결과가 먼저 필요합니다.')
        papers=evidence_papers(item)
        if not papers:
            update(iid,status='needs_paper',stage='논문 원문 연결 필요',items=[],error='확인 가능한 arXiv 링크나 본문에 명시된 정확한 논문 제목을 입력하세요. 추정한 논문은 자동 추가하지 않습니다.');return intake.get(iid)
        previous=item.get('pipeline',{})
        if previous.get('status')=='done' and not retry:
            old={x.get('url') for x in previous.get('items',[])}
            if {x['url'] for x in papers}.issubset(old):reclassify(iid);return intake.get(iid)
        ACTIVE.add(iid);update(iid,status='running',stage='원문 확인',error='',items=previous.get('items',[]),deferred=max(0,len(papers)-3))
    threading.Thread(target=run,args=(iid,papers[:3]),daemon=True).start();return intake.get(iid)

def graph_for(p):
    if p.get('openalex'):seed=p['openalex']
    else:
        candidates=discovery.search(p['title']);exact=[w for w in candidates if R.norm(w['title'])==R.norm(p['title'])]
        if len(exact)!=1:return {'status':'needs_match','error':'외부 색인에 일치하는 논문이 없거나 여러 판본이 있습니다. 연결 논문 탭에서 선택하세요.'}
        seed=exact[0]['id']
    g=discovery.graph(seed)
    # A previous empty graph may predate collection of the original bibliography.
    if len(g['nodes'])==1 and p.get('references'):g=discovery.graph(seed,True)
    with R.LOCK:
        latest=R.get(p['id']);latest['openalex']=seed;R.save(latest)
    return {'status':'ready' if len(g['nodes'])>1 else 'empty','id':seed,'nodes':len(g['nodes']),'edges':len(g['edges']),'error':'' if len(g['nodes'])>1 else '외부 인용 정보와 원문에서 확인 가능한 연결이 없습니다.'}

def run(iid,candidates):
    rows=[]
    try:
        for candidate in candidates:
            row={**candidate,'source_status':'running','analysis_status':'pending','graph_status':'pending'};rows.append(row);update(iid,items=rows,stage='원문 확인')
            try:
                if candidate['basis']=='explicit-title':
                    metadata=R.metadata(R.arxiv_id(candidate['url']))
                    if R.norm(metadata['title'])!=R.norm(candidate['title']):raise ValueError('제안된 논문 제목과 arXiv 원문 제목이 일치하지 않습니다.')
                p=R.add(candidate['url'])
                row.update(paper_id=p['id'],title=p['title'],source_status='metadata_only');bind(iid,p['id']);update(iid,items=rows,stage='원문 수집·분석')
                if p.get('reports'):
                    row['analysis_status']='ready'
                else:
                    with R.LOCK:active=next((j for j in R.JOBS.values() if j['paper_id']==p['id'] and j['status'] in ('queued','running')),None)
                    job=R.snapshot(active['id']) if active else R.start(p['id']);row.update(analysis_job=job['id'],analysis_status='running');update(iid,items=rows)
                    while True:
                        job=R.snapshot(job['id'])
                        if job['status'] not in ('queued','running'):break
                        if row['source_status']!='ready' and R.get(p['id']).get('last_run'):
                            row['source_status']='ready';update(iid,items=rows)
                        time.sleep(2)
                    if job['status']!='done':raise ValueError(job.get('error') or '분석이 중지되었습니다.')
                    row['analysis_status']='ready'
                p=R.get(p['id']);row['review_status']=p.get('status');row['source_status']='ready' if p.get('last_run') else 'metadata_only'
                try:reader.document(p['id']);row['reader_status']='html'
                except Exception:row['reader_status']='pdf' if p.get('last_run') else 'unavailable'
                update(iid,items=rows,stage='관련 논문 그래프 연결')
                try:
                    graph=graph_for(p);row.update(graph_status=graph['status'],graph_id=graph.get('id'),graph_nodes=graph.get('nodes',0),graph_error=graph.get('error',''))
                except Exception as error:row.update(graph_status='error',graph_error=str(error)[:500])
                bind(iid,p['id']);update(iid,items=rows)
            except Exception as error:
                row.update(error=str(error)[:800]);row['analysis_status']='error';update(iid,items=rows)
        complete=all(r['analysis_status']=='ready' and r['graph_status']=='ready' for r in rows)
        update(iid,status='done' if complete else 'partial',stage='라이브러리에 연결됨' if complete else '확인·재시도가 필요한 항목 있음',items=rows)
    except Exception as error:update(iid,status='error',error=str(error)[:800])
    finally:
        with R.LOCK:ACTIVE.discard(iid)

def paper_summary(pid):
    p=R.get(pid)
    with R.db() as c:links=[dict(r) for r in c.execute('SELECT * FROM library_links WHERE paper_id=?',(pid,))]
    for link in links:
        item=intake.get(link['inbox_id']);link.update(concepts=json.loads(link['concepts']),title=item['title'],input=item['input'])
    annotations=reader.annotations(pid)
    return {'paper_id':pid,'links':links,'highlights':len(annotations),'annotation_notes':sum(bool(a.get('note')) for a in annotations),'has_note':bool(p.get('notes')),'explanations':sum(bool(a.get('answer')) for a in annotations)}

def inbox():
    items=intake.state()
    for item in items:
        for row in item.get('pipeline',{}).get('items',[]):
            if row.get('paper_id'):
                row['library']=paper_summary(row['paper_id'])
                jid=row.get('analysis_job')
                if jid in R.JOBS:row['analysis_stage']=R.JOBS[jid].get('stage')
    return items


def link_graph(pid,seed):
    graph=discovery.graph(seed);center=next(n for n in graph['nodes'] if n['id']==graph['seed']);p=R.get(pid)
    if R.norm(center['title'])!=R.norm(p['title']):raise ValueError('다른 논문의 그래프는 이 논문에 연결할 수 없습니다.')
    with R.LOCK:
        p=R.get(pid);p['openalex']=graph['seed'];R.save(p)
        with R.db() as c:ids=[r[0] for r in c.execute('SELECT inbox_id FROM library_links WHERE paper_id=?',(pid,))]
        for iid in ids:
            item=intake.get(iid);pipeline=item.get('pipeline',{})
            for row in pipeline.get('items',[]):
                if row.get('paper_id')==pid:row.update(graph_id=graph['seed'],graph_status='ready' if len(graph['nodes'])>1 else 'empty',graph_nodes=len(graph['nodes']),graph_error='')
            if pipeline.get('items') and all(r.get('analysis_status')=='ready' and r.get('graph_status')=='ready' for r in pipeline['items']):pipeline.update(status='done',stage='라이브러리에 연결됨')
            intake.save(item)
    return {'paper_id':pid,'graph_id':graph['seed']}
