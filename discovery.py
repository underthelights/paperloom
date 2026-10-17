"""External citation neighborhoods with auditable similarity scores (OpenAlex)."""
import json,math,re,uuid,os
from urllib.parse import urlencode
import research as R
FIELDS='id,doi,title,publication_year,authorships,cited_by_count,referenced_works,related_works,primary_location,best_oa_location,abstract_inverted_index'

def request(path,**params):
    if os.environ.get('OPENALEX_API_KEY'):params['api_key']=os.environ['OPENALEX_API_KEY']
    return json.loads(R.fetch('https://api.openalex.org/'+path+'?'+urlencode(params)))

def wid(value):
    value=str(value).rsplit('/',1)[-1]
    if not re.fullmatch(r'W\d+',value):raise ValueError('올바른 OpenAlex 논문 ID가 필요합니다.')
    return value

def node(work):
    inverted=work.get('abstract_inverted_index') or {};words={i:w for w,indices in inverted.items() for i in indices}
    abstract=' '.join(words[i] for i in sorted(words))[:12000]
    locations=[work.get('best_oa_location') or {},work.get('primary_location') or {}];url=next((v.get('landing_page_url') for v in locations if v.get('landing_page_url')),None) or work.get('doi') or work['id']
    arxiv=next((R.arxiv_id(v.get(k,'')) for v in locations for k in ('landing_page_url','pdf_url') if R.arxiv_id(v.get(k,''))),None)
    return {'id':wid(work['id']),'title':work.get('title') or '제목 미제공','year':work.get('publication_year'),'authors':[a.get('author',{}).get('display_name','') for a in work.get('authorships',[])][:15],
            'citations':work.get('cited_by_count',0),'doi':work.get('doi'),'url':url,'arxiv':arxiv,'abstract':abstract,'references':[wid(x) for x in work.get('referenced_works',[])],'related':[wid(x) for x in work.get('related_works',[])],'source':work['id']}

def search(query):
    query=str(query).strip()[:500]
    if not query:raise ValueError('논문 제목, DOI 또는 arXiv 링크를 입력하세요.')
    if re.fullmatch(r'(https://openalex.org/)?W\d+',query):return [node(request('works/'+wid(query))) ]
    if R.arxiv_id(query):query=R.metadata(R.arxiv_id(query))['title']
    if query.startswith(('10.','https://doi.org/')):return [node(request('works/https://doi.org/'+query.removeprefix('https://doi.org/')))]
    return [node(w) for w in request('works',search=query,per_page=8,select=FIELDS).get('results',[])]

def cache_path(seed):
    path=R.DATA/'discovery';path.mkdir(parents=True,exist_ok=True);return path/(wid(seed)+'.json')

def assemble(seed,works,citing,notices):
    unique={w['id']:w for w in [seed]+works+citing};nodes=list(unique.values());ids=set(unique);refs={w['id']:set(w['references']) for w in nodes};incoming={i:{w['id'] for w in nodes if i in refs[w['id']]} for i in ids};edges=[]
    for n in nodes:
        n['role']='seed' if n['id']==seed['id'] else 'prior' if n['id'] in refs[seed['id']] else 'derivative' if seed['id'] in refs[n['id']] else 'related'
    for i,a in enumerate(nodes):
        for b in nodes[i+1:]:
            x,y=a['id'],b['id'];shared=refs[x]&refs[y];cociters=incoming[x]&incoming[y]
            bc=len(shared)/math.sqrt(len(refs[x])*len(refs[y])) if refs[x] and refs[y] else 0
            cc=len(cociters)/math.sqrt(len(incoming[x])*len(incoming[y])) if incoming[x] and incoming[y] else 0
            directions=([{'from':x,'to':y}] if y in refs[x] else [])+([{'from':y,'to':x}] if x in refs[y] else [])
            if shared or cociters or directions:edges.append({'source':x,'target':y,'coupling':round(bc,4),'cocitation':round(cc,4),'score':round((bc+cc)/2,4),'shared_references':sorted(shared),'sample_cociters':sorted(cociters),'citations':directions,'citation_basis':'original-bibliography-title-match' if (a.get('reference_origin') or b.get('reference_origin')) else 'openalex'})
    return {'seed':seed['id'],'nodes':nodes,'edges':edges,'retrieved':R.now(),'notices':notices,'coverage':{'nodes':len(nodes),'seed_reference_total':len(seed['references']),'seed_citation_total':seed['citations'],'incoming_sample':len(citing),'reference_limit':25,'incoming_limit':25,'related_limit':12},'method':'Similarity = (bibliographic coupling cosine + co-citation cosine within this retrieved sample) / 2. Citation arrows are separate observed links. OpenAlex related works are candidates, not verified citations.'}

def original_references(center):
    paper=next((p for p in R.all_records() if p.get('references') and R.norm(p['title'])==R.norm(center['title'])),None)
    if not paper:return [],[]
    refs=paper['references'];ranked=sorted(enumerate(refs),key=lambda pair:(not any(k in pair[1]['title'].lower() for k in ('robot','action','policy','diffusion')),pair[0]))[:12]
    works=[];matches=[]
    for _,ref in ranked:
        try:
            candidates=[w for w in search(ref['title']) if R.norm(w['title'])==R.norm(ref['title'])]
            if not candidates:continue
            dated=[w for w in candidates if w['year'] and str(w['year']) in ref.get('citation','')]
            chosen=(dated or candidates)[0]
            if chosen['id'] not in {w['id'] for w in works}:works.append(chosen)
            matches.append({'id':chosen['id'],'title':ref['title'],'source':ref.get('source',paper.get('url','')),'match':'title-and-year' if dated else 'title-only-version-unverified'})
        except Exception:continue
    center['references']=[w['id'] for w in works];center['reference_origin']='original-bibliography';center['reference_matches']=matches;center['original_reference_total']=len(refs)
    notice='외부 색인에 중심 논문의 참고문헌이 없어 원문 참고문헌 '+str(len(refs))+'개 중 로봇·행동·정책·확산 관련 제목을 우선한 12개를 대조했습니다. '+str(len(works))+'개 제목이 일치했습니다. 제목만 일치한 항목은 판본이 확인되지 않았으며, 중심 논문의 직접 인용은 원문 참고문헌에 근거합니다.'
    return works,[notice]

def graph(seed,refresh=False):
    seed=wid(seed);path=cache_path(seed)
    if path.exists() and not refresh:return json.loads(path.read_text())
    center=node(request('works/'+seed));notices=[];works=[];citing=[]
    if not center['references']:
        works,notices=original_references(center)
    selected=list(dict.fromkeys(center['references'][:25]+center['related'][:12]));selected=[x for x in selected if x!=seed]
    if selected:
        try:works.extend([node(w) for w in request('works',filter='openalex_id:'+'|'.join(selected),per_page=50,select=FIELDS).get('results',[])])
        except Exception as error:notices.append('참고문헌·관련 논문 조회 실패: '+str(error))
    try:citing=[node(w) for w in request('works',filter='cites:'+seed,sort='cited_by_count:desc',per_page=25,select=FIELDS).get('results',[])]
    except Exception as error:notices.append('후속 인용 논문 조회 실패: '+str(error))
    result=assemble(center,works,citing,notices);tmp=path.with_suffix('.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False));tmp.replace(path);return result

def import_work(seed,target):
    data=graph(seed);work=next((w for w in data['nodes'] if w['id']==wid(target)),None)
    if not work:raise ValueError('현재 그래프에서 논문을 찾을 수 없습니다.')
    if work['arxiv']:return R.add(work['arxiv'])
    with R.LOCK:
        for p in R.all_records():
            if p.get('openalex')==work['id'] or (work['doi'] and p.get('doi')==work['doi']):return p
        p={'id':uuid.uuid4().hex,'identity':'openalex:'+work['id'],'openalex':work['id'],'doi':work['doi'],'title':work['title'],'authors':work['authors'],'year':work['year'],'url':work['url'],'abstract':work['abstract'],'status':'ready','source':'OpenAlex','captured':R.now(),'notes':'','chat':[],'reports':[],'references':[]}
        return R.save(p)
