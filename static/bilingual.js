'use strict';
const autoLabels={baseline:'기존 연구·baseline',claim:'본 논문 주장',reasoning:'논리·근거',experiment:'실험·결과'};
let bilingualTimer=null,bilingualValue=null,bilingualEnabled=true,autoEnabled=new Set(Object.keys(autoLabels));
async function startBilingual(pid,epoch){
 clearTimeout(bilingualTimer);bilingualValue=null;
 const controls=$('#bilingual-controls');if(!controls)return;
 controls.innerHTML=`<div class="bilingual-options"><label><input id="bilingual-toggle" type="checkbox" checked> 영어 옆 한국어</label>${Object.entries(autoLabels).map(([k,v])=>`<label class="auto-label auto-${k}"><input data-auto-category="${k}" type="checkbox" checked>${v}</label>`).join('')}</div><p id="bilingual-status" role="status">문단별 번역·주장 분류를 준비합니다. Codex 사용량을 소비합니다.</p><button id="bilingual-retry" hidden>완료된 문단부터 이어서 처리</button><details><summary>자동 하이라이트 분류 근거 · AI 해석</summary><div id="auto-evidence"></div></details>`;
 bilingualEnabled=true;autoEnabled=new Set(Object.keys(autoLabels));
 $('#bilingual-toggle').onchange=e=>{bilingualEnabled=e.target.checked;$('#original-paper')?.classList.toggle('original-only',!bilingualEnabled)};
 $$('[data-auto-category]').forEach(b=>b.onchange=()=>{b.checked?autoEnabled.add(b.dataset.autoCategory):autoEnabled.delete(b.dataset.autoCategory);paintAuto()});
 const current=()=>paper?.id===pid&&renderEpoch===epoch&&!!$('#bilingual-controls');
 async function poll(){try{const v=await api('reader/auto/'+pid);if(!current())return;show(v);if(v.status==='running')bilingualTimer=setTimeout(poll,2500)}catch(e){if(current())$('#bilingual-status').textContent='번역 상태 확인 실패: '+e.message}}
 function show(v){bilingualValue=v;applyBilingual();$('#bilingual-status').textContent=`AI 번역·분류 ${Object.keys(v.blocks).length}/${v.total} 문단 · ${({running:'처리 중',ready:'완료',error:'중단',idle:'대기'})[v.status]}${v.error?' · '+v.error:''} · 원문과 대조하세요`;$('#bilingual-retry').hidden=v.status!=='error'}
 $('#bilingual-retry').onclick=async()=>{try{const v=await api('reader/auto',{paper_id:pid,retry:true});if(current()){show(v);bilingualTimer=setTimeout(poll,2500)}}catch(e){if(current())$('#bilingual-status').textContent=e.message}};
 try{const v=await api('reader/auto',{paper_id:pid});if(!current())return;show(v);if(v.status==='running')bilingualTimer=setTimeout(poll,2500)}catch(e){if(current())$('#bilingual-status').textContent='자동 번역 시작 실패: '+e.message}
}
function applyBilingual(){
 const root=$('#original-paper');if(!root||!bilingualValue||bilingualValue.version!==originalDoc?.version)return;
 for(const block of originalDoc.blocks||[]){const source=root.querySelector(`[data-reader-block="${block.id}"]`);if(!source)continue;let row=source.parentElement;
 if(!row.classList.contains('bilingual-row')){row=document.createElement('div');row.className='bilingual-row';source.before(row);row.append(source);const ko=document.createElement('div');ko.className='bilingual-ko';ko.dataset.readerGenerated='true';ko.lang='ko';row.append(ko)}
 const output=bilingualValue.blocks[block.id];const ko=row.querySelector('.bilingual-ko');const text=output?.ko_template||output?.ko||'한국어 번역 대기 중…';if(ko.dataset.rendered!==text){ko.replaceChildren();const parts=text.split(/(⟦MATH_\d+⟧)/g);const formulas=source.querySelectorAll('math');for(const part of parts){const token=part.match(/^⟦MATH_(\d+)⟧$/);if(token&&formulas[+token[1]])ko.append(formulas[+token[1]].cloneNode(true));else ko.append(document.createTextNode(part))}ko.dataset.rendered=text}ko.classList.toggle('pending',!output);
 }
 paintHighlights();paintAuto();
 const evidence=$('#auto-evidence');const highlights=Object.values(bilingualValue.blocks).flatMap(b=>b.highlights);
 evidence.innerHTML=highlights.map((h,i)=>`<button data-auto-jump="${i}" class="auto-evidence-item"><b>${escape(autoLabels[h.category])}</b><q>${escape(h.exact)}</q><span>${escape(h.reason)} · ${escape(h.attribution)}</span></button>`).join('')||'<p>검증된 원문 인용과 분류 이유가 여기에 표시됩니다.</p>';
 evidence.onclick=e=>{const b=e.target.closest('[data-auto-jump]');if(!b)return;const h=highlights[+b.dataset.autoJump],r=readerRange(h.start,h.end);r?.startContainer.parentElement.scrollIntoView({block:'center'});if(r&&window.CSS?.highlights)CSS.highlights.set('reader-focus',new Highlight(r))};
}
function paintAuto(){if(!window.CSS?.highlights)return;for(const category of Object.keys(autoLabels)){const ranges=bilingualValue?.version===originalDoc?.version&&autoEnabled.has(category)?Object.values(bilingualValue.blocks).flatMap(b=>b.highlights).filter(h=>h.category===category).map(h=>readerRange(h.start,h.end)).filter(Boolean):[];const highlight=new Highlight(...ranges);if('priority' in highlight)highlight.priority=1;CSS.highlights.set('auto-'+category,highlight)}}
