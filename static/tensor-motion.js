/* Source-shaped animation controls; rendering is explicitly requested. */
(function(){
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const shape=v=>Array.isArray(v)?v.join(' × '):String(v??'확인 불가');
 const localURL=v=>typeof v==='string'&&/^\/api\/research\/motion\//.test(v)&&!v.includes('\\')?v:'';
 window.mountTensorMotion=function(host,paper,walkthrough,options={}){
  if(!host)return{select(){},dispose(){}};const steps=Array.isArray(walkthrough?.steps)?walkthrough.steps.filter(s=>s&&typeof s.id==='string'):[];
  let mode=options.mode==='inference'?'inference':'training',selected=0,rowIndex=-1,epoch=0,timer=null,disposed=false;
  const current=token=>!disposed&&host.isConnected&&epoch===token;
  const visible=()=>steps.filter(s=>s.mode===mode||s.mode==='shared');
  const stop=()=>{if(timer)clearTimeout(timer);timer=null;host.querySelector('video')?.pause()};
  function draw(){
   stop();const token=++epoch,list=visible();selected=Math.max(0,Math.min(selected,list.length-1));const step=list[selected];
   host.innerHTML=`<section class="tensor-motion"><header><h3>연산 영상</h3><div class="tensor-motion-modes"><button type="button" data-motion-mode="training" aria-pressed="${mode==='training'}">학습</button><button type="button" data-motion-mode="inference" aria-pressed="${mode==='inference'}">추론</button></div></header><nav class="tensor-motion-timeline" aria-label="영상 연산 단계">${list.map((s,i)=>`<button type="button" data-motion-step="${i}" aria-current="${i===selected?'step':'false'}">${i+1}. ${esc(s.title||s.id)}</button>`).join('')}</nav>${step?`<nav class="tensor-motion-rows" aria-label="세부 텐서 연산"><button type="button" data-motion-row="-1" aria-pressed="${rowIndex===-1}">단계 전체</button>${(step.shape_trace||[]).map((r,i)=>`<button type="button" data-motion-row="${i}" aria-pressed="${rowIndex===i}">${i+1}. ${esc(r.title||r.operation||'연산')}</button>`).join('')}</nav><div class="tensor-motion-source"><span>${esc(step.operation||'연산')}</span><code>${esc(shape(step.input_shape))}</code><b aria-hidden="true">→</b><code>${esc(shape(step.output_shape))}</code></div><div class="tensor-motion-media"></div><div class="tensor-motion-state" role="status">저장된 영상 확인 중…</div><progress class="tensor-motion-progress" max="100" value="0" aria-label="영상 생성 진행" hidden></progress><div class="tensor-motion-actions"><button type="button" data-motion-prev ${selected===0?'disabled':''}>이전</button><button type="button" data-motion-play disabled>재생</button><button type="button" data-motion-next ${selected===list.length-1?'disabled':''}>다음</button><button type="button" data-motion-generate>이 연산 영상 생성</button><a class="tensor-motion-download" hidden download>내보내기</a></div><div class="tensor-motion-evidence"><button type="button" data-motion-panel="code">코드</button><button type="button" data-motion-panel="equation">수식</button><button type="button" data-motion-panel="derivation">유도 과정</button></div><p class="tensor-motion-notice">코드·설정에 기록된 shape의 구조를 시각화합니다. 모델 실행값이나 실험 재현 영상이 아닙니다.</p>`:'<p class="tensor-motion-empty">이 모드에 해당하는 연산 단계가 없습니다.</p>'}</section>`;
   if(step){
    const rows=host.querySelector('.tensor-motion-rows'),source=host.querySelector('.tensor-motion-source');
    const detail=document.createElement('details');detail.className='tensor-motion-shapes';const summary=document.createElement('summary');summary.textContent='입력 → 출력 shape · 코드 설정 기준';source.before(detail);detail.append(summary,source);
    ['.tensor-motion-media','.tensor-motion-state','.tensor-motion-progress','.tensor-motion-actions'].forEach(selector=>rows.before(host.querySelector(selector)));
   }
   host.querySelectorAll('[data-motion-mode]').forEach(b=>b.onclick=()=>{const prior=visible()[selected]?.id;mode=b.dataset.motionMode;selected=Math.max(0,visible().findIndex(s=>s.id===prior));rowIndex=-1;draw();if(visible()[selected])options.onStep?.(visible()[selected].id,rowIndex,'code')});
   host.querySelectorAll('[data-motion-step]').forEach(b=>b.onclick=()=>{selected=Number(b.dataset.motionStep);rowIndex=-1;draw();options.onStep?.(visible()[selected].id,rowIndex,'code')});
   if(!step)return;
   host.querySelectorAll('[data-motion-row]').forEach(b=>b.onclick=()=>{rowIndex=Number(b.dataset.motionRow);draw();options.onStep?.(step.id,rowIndex,'code')});
   const chosen=rowIndex>=0?step.shape_trace?.[rowIndex]:null;if(chosen){const box=host.querySelector('.tensor-motion-source');box.innerHTML=`<span>${esc(chosen.operation||chosen.title||'연산')}</span><code>${esc(shape(chosen.input_shape))}</code><b aria-hidden="true">→</b><code>${esc(shape(chosen.output_shape))}</code>`}
   host.querySelector('[data-motion-prev]').onclick=()=>{selected--;rowIndex=-1;draw();options.onStep?.(visible()[selected].id,rowIndex,'code')};host.querySelector('[data-motion-next]').onclick=()=>{selected++;rowIndex=-1;draw();options.onStep?.(visible()[selected].id,rowIndex,'code')};
   host.querySelectorAll('[data-motion-panel]').forEach(b=>b.onclick=()=>options.onStep?.(step.id,rowIndex,b.dataset.motionPanel));
   let responseSequence=0,autoAttempted=false;const get=()=>api('research/motion/'+encodeURIComponent(paper.id)+'?'+new URLSearchParams({mode,step:step.id,row_index:rowIndex}));
   function show(result){
    if(!current(token))return;const status=host.querySelector('.tensor-motion-state'),generate=host.querySelector('[data-motion-generate]'),progress=host.querySelector('progress'),media=host.querySelector('.tensor-motion-media'),play=host.querySelector('[data-motion-play]');
    const pending=['queued','running'].includes(result.status);generate.disabled=pending;progress.hidden=!pending;progress.value=Math.max(0,Math.min(100,Number(result.progress)||0));status.textContent=pending?`${result.stage||'영상 생성 중'} · ${Math.round(progress.value)}%`:result.status==='error'?'생성 실패: '+(result.error||'오류 내용 미제공'):result.status==='ready'?'저장된 연산 영상':'아직 생성한 영상이 없습니다.';
    if(result.status==='ready'){
     const src=localURL(result.url);if(!src){status.textContent='영상 주소를 확인할 수 없습니다.';return}
     let video=media.querySelector('video');if(!video){video=document.createElement('video');video.controls=true;video.muted=true;video.playsInline=true;video.autoplay=true;video.preload='metadata';media.append(video);video.onplay=()=>play.textContent='일시정지';video.onpause=()=>play.textContent='재생'}
     if(video.getAttribute('src')!==src)video.src=src;play.disabled=false;play.onclick=()=>{if(video.paused)video.play().catch(()=>{status.textContent='재생 버튼을 눌러 영상을 시작하세요.'});else video.pause()};video.play().catch(()=>{});
     const download=host.querySelector('.tensor-motion-download'),url=localURL(result.download_url);download.hidden=!url;if(url)download.href=url;
    }
    if(pending)timer=setTimeout(poll,1200);if(result.status==='missing'&&options.autoGenerate&&!autoAttempted){autoAttempted=true;queueMicrotask(()=>{if(current(token))host.querySelector('[data-motion-generate]')?.click()})}
   }
   async function poll(){if(!current(token))return;const sequence=++responseSequence;try{const result=await get();if(sequence===responseSequence)show(result)}catch(e){if(current(token)&&sequence===responseSequence)show({status:'error',error:e.message})}}
   host.querySelector('[data-motion-generate]').onclick=async()=>{const button=host.querySelector('[data-motion-generate]');button.disabled=true;const sequence=++responseSequence;if(timer)clearTimeout(timer);timer=null;try{const result=await api('research/motion',{paper_id:paper.id,mode,step_id:step.id,row_index:rowIndex});if(current(token)&&sequence===responseSequence){show(result);if(!['queued','running','ready','error'].includes(result.status))await poll()}}catch(e){if(current(token))show({status:'error',error:e.message})}};
   poll();
  }
  draw();return{select(stepId,index=-1,notify=false){if(disposed)return;const step=steps.find(s=>s.id===stepId);if(!step)return;if(step.mode!=='shared'&&['training','inference'].includes(step.mode))mode=step.mode;selected=visible().findIndex(s=>s.id===stepId);if(selected<0)return;rowIndex=Number.isInteger(index)&&index>=0&&index<(step.shape_trace||[]).length?index:-1;draw();if(notify)options.onStep?.(step.id,rowIndex,'code')},dispose(){disposed=true;epoch++;stop()}};
 };
})();
