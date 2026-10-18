"""Render trusted Manim diagrams from a selected, source-bound tensor trace."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit, unquote
import knowledge
import research as R

VERSION = 1
GATE = knowledge.VIDEO_GATE
ACTIVE = set()


def identifier(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',value):
        raise ValueError('잘못된 논문·연산 식별자')
    return value


def text(value,limit=6000):
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]','',value)[:limit] if isinstance(value,str) else ''


def select_spec(pid,mode,step_id,row_index=-1):
    identifier(pid);identifier(step_id)
    if mode not in ('training','inference'):raise ValueError('학습 또는 추론 모드를 선택하세요.')
    if not isinstance(row_index,int) or isinstance(row_index,bool) or row_index < -1:raise ValueError('잘못된 세부 연산 번호')
    paper=R.get(pid);reports=paper.get('reports',[]);report=reports[-1] if reports else {}
    trace=report.get('walkthrough')
    if not isinstance(trace,dict):
        raise ValueError('저장된 코드·설정 기반 텐서 추적이 없습니다. 먼저 논문을 분석하세요.')
    step=next((s for s in trace.get('steps',[]) if s.get('id')==step_id),None)
    if not step or step.get('mode') not in (mode,'shared'):raise ValueError('현재 모드에 없는 연산입니다.')
    rows=step.get('shape_trace',[])
    if row_index>=len(rows):raise ValueError('세부 연산 번호가 범위를 벗어났습니다.')
    fields=('id','title','operation','input_shape','output_shape','equation','explanation','mode','verification')
    clean={k:text(step.get(k)) for k in fields}
    clean['shape_trace']=[{k:text(r.get(k)) for k in ('title','operation','input_shape','output_shape','equation','assumptions','basis')} for r in rows if isinstance(r,dict)]
    clean['mechanics']=[{k:text(r.get(k)) for k in ('title','explanation','input_shape','output_shape','equation','assumptions','basis')} for r in step.get('mechanics',[]) if isinstance(r,dict)]
    profile=trace.get('execution_profile') or {}
    selected={k:text(profile.get(k)) for k in ('repository','commit','config','mode','scope')}
    selected['dimensions']=[{k:text(d.get(k)) for k in ('symbol','value','meaning')} for d in profile.get('dimensions',[]) if isinstance(d,dict)]
    selected['unknowns']=[text(v) for v in profile.get('unknowns',[]) if isinstance(v,str)]
    scene=R.ROOT/'tensor_scenes.py'
    result={'version':VERSION,'paper_id':pid,'report_id':text(report.get('id')),'source_digest':hashlib.sha256(json.dumps(trace,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            'scene_digest':hashlib.sha256(scene.read_bytes()).hexdigest(),'mode':mode,'profile':selected,'step':clean}
    if row_index>=0:result['row_index']=row_index
    return result


def key(spec):
    # The full source digest already covers these nonvisual explanation fields.
    visual={**spec,'step':{k:v for k,v in spec['step'].items() if k!='mechanics'},
            'profile':{k:v for k,v in spec['profile'].items() if k!='unknowns'}}
    return hashlib.sha256(json.dumps(visual,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def prune(pid,preserve):
    with R.LOCK:_prune(pid,preserve)


def _prune(pid,preserve):
    parent=directory(pid,preserve).parent
    folders=sorted((p for p in parent.iterdir() if re.fullmatch(r'[a-f0-9]{64}',p.name) and p.is_dir() and not p.is_symlink()),key=lambda p:p.stat().st_mtime,reverse=True)
    for folder in folders[128:]:
        if folder.name==preserve or folder.name in ACTIVE:continue
        try:
            try:owner=int((folder/'render.lock').read_text())
            except (OSError,ValueError):owner=0
            if _alive(owner):continue
            status=json.loads((folder/'status.json').read_text())
            if not isinstance(status,dict):continue
            if status.get('status') in ('queued','running') and _alive(status.get('owner_pid')):continue
            shutil.rmtree(folder)
        except (OSError,ValueError):pass


def directory(pid,digest):
    identifier(pid)
    if not re.fullmatch(r'[a-f0-9]{64}',digest):raise ValueError('잘못된 영상 키')
    root=R.DATA/'tensor-motion';path=root/pid/digest
    if not root.resolve().is_relative_to(R.DATA.resolve()) or not path.resolve().is_relative_to(root.resolve()):raise ValueError('잘못된 영상 경로')
    return path


def _write(folder,value):
    tmp=folder/'status.writing';tmp.write_text(json.dumps(value,ensure_ascii=False));os.replace(tmp,folder/'status.json')


def _alive(pid):
    if not isinstance(pid,int) or pid<=0:return False
    try:os.kill(pid,0);return True
    except (OSError,OverflowError):return False


def get_status(pid,mode,step_id,row_index=-1):
    return _status(select_spec(pid,mode,step_id,row_index),row_index)


def _status(spec,row_index=-1):
    pid=spec['paper_id'];mode=spec['mode'];step_id=spec['step']['id'];digest=key(spec);folder=directory(pid,digest)
    try:value=json.loads((folder/'status.json').read_text())
    except (FileNotFoundError,json.JSONDecodeError):value={'status':'missing','progress':0,'stage':'영상 생성 전'}
    if value['status'] in ('queued','running') and not _alive(value.get('owner_pid')):
        value={'status':'error','progress':0,'stage':'중단','error':'이전 렌더링이 중단되었습니다. 다시 생성하세요.'}
    if value['status']=='ready' and not (folder/'video.mp4').is_file():
        value={'status':'error','progress':0,'stage':'파일 없음','error':'완료 영상 파일을 찾지 못했습니다.'}
    if value['status']=='running':
        try:
            progress=json.loads((folder/'progress.json').read_text());value.update(progress=max(5,min(90,int(progress['progress']))),stage=text(progress.get('stage'),200))
        except (OSError,ValueError,KeyError):pass
    public={k:value[k] for k in ('status','progress','stage','error') if k in value}
    public.update(key=digest,mode=mode,step_id=step_id,row_index=row_index)
    if public['status']=='ready':
        public.update(url=f'/api/research/motion/video/{pid}/{digest}',download_url=f'/api/research/motion/video/{pid}/{digest}?download=1')
    return public


def start(data):
    pid=data.get('paper_id');mode=data.get('mode');step_id=data.get('step_id');row=data.get('row_index',-1)
    with R.LOCK:
        spec=select_spec(pid,mode,step_id,row);digest=key(spec);folder=directory(pid,digest)
        current=_status(spec,row)
        if current['status'] in ('ready','queued','running'):return current
        python=knowledge.runtime();folder.mkdir(parents=True,exist_ok=True)
        lock=folder/'render.lock'
        try:fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        except FileExistsError:
            try:owner=int(lock.read_text())
            except (ValueError,OSError):owner=0
            if _alive(owner):return {**current,'status':'queued','progress':0,'stage':'렌더링 대기'}
            lock.unlink(missing_ok=True);fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as stream:stream.write(str(os.getpid()))
        _write(folder,{'status':'queued','progress':0,'stage':'렌더링 대기','owner_pid':os.getpid()})
        ACTIVE.add(digest)
        try:threading.Thread(target=_render,args=(folder,spec,python),daemon=True).start()
        except Exception:
            ACTIVE.discard(digest);lock.unlink(missing_ok=True)
            _write(folder,{'status':'error','progress':0,'stage':'실패','error':'렌더링 작업을 시작하지 못했습니다.'})
            raise
    return _status(spec,row)


def _render(folder,spec,python):
    digest=key(spec)
    try:
        with GATE:
            _write(folder,{'status':'running','progress':5,'stage':'Manim 장면 렌더링','owner_pid':os.getpid()})
            (folder/'scene.json').write_text(json.dumps(spec,ensure_ascii=False))
            env={**os.environ,'PAPERLOOM_TENSOR_SPEC':str(folder/'scene.json'),'PAPERLOOM_TENSOR_PROGRESS':str(folder/'progress.json')}
            command=[python,'-m','manim','-ql','--disable_caching','--media_dir',str(folder/'media'),str(R.ROOT/'tensor_scenes.py'),'TensorTraceScene']
            with (folder/'render.log').open('w') as log:
                subprocess.run(command,env=env,stdout=log,stderr=log,timeout=240,check=True,shell=False,cwd=str(folder))
            source=next((folder/'media/videos').rglob('TensorTraceScene.mp4'))
            if source.stat().st_size<1000:raise ValueError('완성 영상이 비어 있습니다.')
            shutil.copy2(source,folder/'video.writing');os.replace(folder/'video.writing',folder/'video.mp4')
            _write(folder,{'status':'ready','progress':100,'stage':'완료','owner_pid':os.getpid()})
            try:prune(spec['paper_id'],digest)
            except OSError:pass
    except Exception as exc:
        _write(folder,{'status':'error','progress':0,'stage':'실패','error':'Manim 렌더링 실패: '+str(exc)[:300]})
    finally:
        (folder/'render.lock').unlink(missing_ok=True)
        shutil.rmtree(folder/'media',ignore_errors=True)
        ACTIVE.discard(digest)


def video_file(pid,digest):
    folder=directory(pid,digest);path=folder/'video.mp4'
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(folder.resolve()):raise ValueError('생성된 영상이 없습니다.')
    status=json.loads((folder/'status.json').read_text())
    if status.get('status')!='ready':raise ValueError('완료된 영상이 아닙니다.')
    return path


def code_excerpt(pid,url):
    """Read only code anchors already attached to this paper's current trace."""
    paper=R.get(identifier(pid));reports=paper.get('reports',[]);report=reports[-1] if reports else {};trace=report.get('walkthrough') or {}
    allowed={e.get('url') for s in trace.get('steps',[]) for e in s.get('evidence',[]) if isinstance(e,dict)}
    for s in trace.get('steps',[]):
        for row in s.get('mechanics',[])+s.get('shape_trace',[]):allowed.update(e.get('url') for e in row.get('evidence',[]) if isinstance(e,dict))
    if url not in allowed:raise ValueError('선택 분석에 포함되지 않은 코드 근거입니다.')
    profile=trace.get('execution_profile',{});prefix=profile.get('repository','').rstrip('/')+'/blob/'+profile.get('commit','')+'/'
    if not url.startswith(prefix):raise ValueError('고정 커밋의 코드 근거가 아닙니다.')
    parsed=urlsplit(url);relative=unquote(parsed.path.split('/blob/'+profile['commit']+'/',1)[-1]);match=re.fullmatch(r'L(\d+)(?:-L(\d+))?',parsed.fragment)
    if not match:raise ValueError('코드 행 범위가 없습니다.')
    source_run=report.get('tensor_audit',{}).get('source_code_run') or paper.get('last_run')
    identifier(source_run);run_root=R.DATA/'runs'/source_run;root=run_root/'code';file=root/relative
    if not root.resolve().is_relative_to(run_root.resolve()) or not run_root.resolve().is_relative_to(R.DATA.resolve()):raise ValueError('잘못된 코드 저장소 경로')
    root=root.resolve()
    if file.is_symlink() or not file.resolve().is_relative_to(root) or not file.is_file() or file.stat().st_size>1024*1024:raise ValueError('로컬에 확인된 코드가 없습니다.')
    commit=profile.get('commit','')
    if not re.fullmatch(r'[0-9a-f]{40}',commit):raise ValueError('고정 코드 커밋이 없습니다.')
    blob=commit+':'+relative
    try:
        size=int(subprocess.check_output(['git','-C',str(root),'cat-file','-s',blob],timeout=10))
        if size>1024*1024:raise ValueError('코드 파일 크기 제한 초과')
        raw=subprocess.check_output(['git','-C',str(root),'show','--no-ext-diff','--no-textconv',blob],timeout=10)
    except subprocess.SubprocessError as exc:raise ValueError('고정 커밋의 코드 파일을 읽지 못했습니다.') from exc
    lines=raw.decode('utf-8','replace').splitlines();start,end=int(match[1]),int(match[2] or match[1])
    if not 1<=start<=end<=len(lines):raise ValueError('잘못된 코드 행 범위')
    end=min(end,start+399)
    return {'url':url,'path':relative,'start':start,'end':end,'code':'\n'.join(lines[start-1:end]),'truncated':int(match[2] or match[1])>end}
