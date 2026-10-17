"""External integrations. Tokens are request-scoped and never stored."""
import hashlib,json,re,time,uuid
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import quote

def request(url,headers,body=None,method=None):
    raw=json.dumps(body).encode() if body is not None and not isinstance(body,bytes) else body
    req=Request(url,data=raw,headers=headers,method=method)
    with urlopen(req,timeout=90) as r:
        result=r.read(70*1024*1024)
        return json.loads(result) if 'json' in r.headers.get('Content-Type','') and result else result

def notion(d,app):
    match=re.search(r'([0-9a-f]{32}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})(?:[?#/]|$)',d['page'],re.I)
    if not match: raise ValueError('Notion 페이지 URL 또는 ID가 필요합니다.')
    pid=str(uuid.UUID(match.group(1)))
    h={'Authorization':'Bearer '+d['token'],'Notion-Version':'2022-06-28','Content-Type':'application/json'}
    page=request('https://api.notion.com/v1/pages/'+pid,h)
    title='Notion note'
    for prop in page.get('properties',{}).values():
        if prop.get('type')=='title': title=''.join(x.get('plain_text','') for x in prop['title'])
    lines=[];count=0
    def blocks(block_id,depth=0):
        nonlocal count
        if depth>15: lines.append('[더 깊은 블록은 원문에서 확인]');return
        cursor=''
        while True:
            data=request('https://api.notion.com/v1/blocks/'+block_id+'/children?page_size=100'+('&start_cursor='+quote(cursor) if cursor else ''),h)
            for b in data['results']:
                count+=1
                if count>10000: raise ValueError('페이지 블록 수 제한 10,000개 초과')
                typ=b['type'];obj=b.get(typ,{})
                text=''.join(x.get('plain_text',x.get('text',{}).get('content','')) for x in obj.get('rich_text',[]))
                if typ.startswith('heading_'): text='#'*int(typ[-1])+' '+text
                if typ in ('bulleted_list_item','numbered_list_item','to_do'): text='- '+text
                if typ in ('bookmark','embed','link_preview'): text=obj.get('url','')
                if text: lines.append(text)
                if b.get('has_children'): blocks(b['id'],depth+1)
            if not data.get('has_more'): break
            cursor=data['next_cursor'];time.sleep(.35)
    blocks(pid)
    return app.upsert(dict(title=title,text='\n\n'.join(lines),notes='\n\n'.join(lines),url=page['url'],source='notion'),'notion:'+pid)

def cloud_sync(token,app):
    config=app.settings();base=config.get('supabase_url','').rstrip('/');key=config.get('supabase_key','')
    if not re.fullmatch(r'https://[a-z0-9-]+\.supabase\.co',base): raise ValueError('Supabase 프로젝트 URL을 설정해주세요.')
    h={'apikey':key,'Authorization':'Bearer '+token,'Content-Type':'application/json'}
    user=request(base+'/auth/v1/user',h)['id']
    # Local library belongs to one cloud account. Prevent accidental account mixing.
    with app.connect() as c:
        old=c.execute("SELECT value FROM settings WHERE key='cloud_owner'").fetchone()
        if old and json.loads(old['value'])!=user: raise ValueError('이 로컬 라이브러리는 다른 Google 계정에 연결되어 있습니다. 별도 data 폴더를 사용해주세요.')
        c.execute("INSERT OR IGNORE INTO settings VALUES('cloud_owner',?)",(json.dumps(user),))
    remote=[]
    for start in range(0,1000000,1000):
        rows=request(base+'/rest/v1/paperloom_records?select=*&order=id&limit=1000&offset='+str(start),h)
        remote+=rows
        if len(rows)<1000: break
    with app.LOCK:
        local={p['identity']:p for p in app.all_papers()}
        for r in remote:
            p=r['body']
            if r['kind']=='concept':
                with app.connect() as c:
                    old=c.execute('SELECT * FROM concepts WHERE name=?',(p['name'],)).fetchone()
                    if not old or p.get('updated',0)>old['updated']:
                        c.execute('INSERT INTO concepts(name,note,updated) VALUES(?,?,?) ON CONFLICT(name) DO UPDATE SET note=excluded.note,updated=excluded.updated',(p['name'],p['note'],p.get('updated',0)))
                continue
            if not re.fullmatch('[a-f0-9]{32}',p.get('id','')) or not p.get('identity'): raise ValueError('잘못된 클라우드 레코드')
            old=local.get(p['identity'])
            if old and old.get('updated',0)>=p.get('updated',0):
                if p.get('notes') and p.get('notes')!=old.get('notes'):
                    old['note_conflicts']=list(dict.fromkeys(old.get('note_conflicts',[])+[p['notes']]))
                    with app.connect() as c: c.execute('UPDATE papers SET body=? WHERE id=?',(json.dumps(old,ensure_ascii=False),old['id']))
                continue
            if old:
                p['id']=old['id']
                if old.get('notes') and old.get('notes')!=p.get('notes'):
                    p['note_conflicts']=list(dict.fromkeys(p.get('note_conflicts',[])+old.get('note_conflicts',[])+[old['notes']]))
            filename=p.get('pdf','')
            if filename:
                if not re.fullmatch(r'[a-f0-9]{64}\.pdf',filename): raise ValueError('잘못된 PDF 파일명')
                target=app.DATA/'pdfs'/filename
                if not target.exists():
                    data=request(base+'/storage/v1/object/authenticated/paperloom/'+user+'/'+filename,h)
                    if hashlib.sha256(data).hexdigest()+'.pdf'!=filename: raise ValueError('PDF 무결성 확인 실패')
                    target.write_bytes(data)
            p['analysis_state']='ready'
            with app.connect() as c:
                c.execute('INSERT INTO papers VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body',(p['id'],p['identity'],json.dumps(p,ensure_ascii=False)))
                for tag in p.get('tags',[]): c.execute('INSERT OR IGNORE INTO concepts(name) VALUES(?)',(tag,))
        papers=app.all_papers()
        with app.connect() as c: concepts=[dict(x) for x in c.execute('SELECT * FROM concepts')]
    remote_pdfs={r['body'].get('pdf') for r in remote if r['kind']=='paper'}
    for p in papers:
        if p.get('pdf') and p['pdf'] not in remote_pdfs:
            request(base+'/storage/v1/object/paperloom/'+user+'/'+p['pdf'],{**h,'Content-Type':'application/pdf','x-upsert':'true'},(app.DATA/'pdfs'/p['pdf']).read_bytes(),'POST')
    records=[{'id':hashlib.sha256(p['identity'].encode()).hexdigest(),'kind':'paper','body':p,'modified':p['updated']} for p in papers]
    records += [{'id':'concept:'+hashlib.sha256(c['name'].lower().encode()).hexdigest(),'kind':'concept','body':c,'modified':c.get('updated',0)} for c in concepts]
    for n in range(0,len(records),100): request(base+'/rest/v1/rpc/paperloom_put',h,{'records':records[n:n+100]})
    app.event(f'클라우드 동기화 완료: {len(papers)}개 자료')
    return {'count':len(papers)}
