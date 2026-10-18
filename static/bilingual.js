'use strict';
const autoLabels={baseline:'기존 연구·baseline',claim:'본 논문 주장',reasoning:'논리·근거',experiment:'실험·결과'};
let bilingualTimer=null,bilingualValue=null,bilingualEnabled=true,autoEnabled=new Set(Object.keys(autoLabels));
async function startBilingual(pid,epoch){
 clearTimeout(bilingualTimer);bilingualValue=null;
 const controls=$('#bilingual-controls');if(!controls)return;
 controls.innerHTML=`<details id="reader-preferences"><summary class="reader-preferences-summary"><strong>번역·하이라이트</strong><span id="reader-settings-state">읽기 설정</span></summary><div class="reader-preferences-body"><div class="bilingual-options"><label><input id="bilingual-toggle" type="checkbox" checked> 영어 옆 한국어</label>${Object.entries(autoLabels).map(([k,v])=>`<label class="auto-label auto-${k}"><input data-auto-category="${k}" type="checkbox" checked>${v}</label>`).join('')}</div><p id="bilingual-status" role="status">문단별 번역·주장 분류를 준비합니다. Codex 사용량을 소비합니다.</p><button id="bilingual-retry" hidden>완료된 문단부터 이어서 처리</button><details><summary>자동 하이라이트 분류 근거 · AI 해석</summary><div id="auto-evidence"></div></details></div></details>`;
 bilingualEnabled=true;autoEnabled=new Set(Object.keys(autoLabels));
 $('#bilingual-toggle').onchange=e=>{bilingualEnabled=e.target.checked;$('#original-paper')?.classList.toggle('original-only',!bilingualEnabled)};
 $$('[data-auto-category]').forEach(b=>b.onchange=()=>{b.checked?autoEnabled.add(b.dataset.autoCategory):autoEnabled.delete(b.dataset.autoCategory);paintAuto()});
 const current=()=>paper?.id===pid&&renderEpoch===epoch&&!!$('#bilingual-controls');
 async function poll(){try{const v=await api('reader/auto/'+pid);if(!current())return;show(v);if(v.status==='running')bilingualTimer=setTimeout(poll,2500)}catch(e){if(current())$('#bilingual-status').textContent='번역 상태 확인 실패: '+e.message}}
 let positionRestored=false;
 function show(v){bilingualValue=v;applyBilingual();if(!positionRestored){positionRestored=true;requestAnimationFrame(()=>{if(current())$('#content').scrollTop=openPapers.find(p=>p.id===pid)?.scroll||0})}$('#bilingual-status').textContent=`AI 번역·분류 ${Object.keys(v.blocks).length}/${v.total} 문단 · ${({running:'처리 중',ready:'완료',error:'중단',idle:'대기'})[v.status]}${v.error?' · '+v.error:''} · 원문과 대조하세요`;$('#reader-settings-state').textContent=(v.status==='running'?'번역 중 ':v.status==='error'?'번역 중단 ':'번역 ')+Object.keys(v.blocks).length+'/'+v.total;$('#bilingual-retry').hidden=v.status!=='error'}
 $('#bilingual-retry').onclick=async()=>{try{const v=await api('reader/auto',{paper_id:pid,retry:true});if(current()){show(v);bilingualTimer=setTimeout(poll,2500)}}catch(e){if(current())$('#bilingual-status').textContent=e.message}};
 try{const modern=originalDoc?.sentence_alignment_version===1;const v=await api(modern?'reader/auto':'reader/auto/'+pid,modern?{paper_id:pid}:undefined);if(!current())return;show(v);if(v.status==='running')bilingualTimer=setTimeout(poll,2500)}catch(e){if(current())$('#bilingual-status').textContent='자동 번역 시작 실패: '+e.message}
}
function bilingualLocalRange(root,start,end){
 if(!Number.isInteger(start)||!Number.isInteger(end)||start<0||end<=start||end>root.textContent.length)return null;
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),range=document.createRange();let pos=0,node,started=false;
 while((node=walker.nextNode())){const next=pos+node.length;if(!started&&start<next){range.setStart(node,start-pos);started=true}if(started&&end<=next){range.setEnd(node,end-pos);return range}pos=next}return null;
}
function bilingualTranslation(target,text,formulas){
 target.replaceChildren();for(const part of String(text||'').split(/(⟦MATH_\d+⟧)/g)){const token=part.match(/^⟦MATH_(\d+)⟧$/);if(token&&formulas[+token[1]]){const clone=formulas[+token[1]].cloneNode(true);[clone,...clone.querySelectorAll('[id]')].forEach(n=>n.removeAttribute('id'));target.append(clone)}else target.append(document.createTextNode(part))}
}
function bilingualSourceRange(source,start,end){
 const range=readerRange(start,end);if(!range)return null;
 for(const node of source.querySelectorAll('math,a')){
  if(!range.intersectsNode(node))continue;const contents=bilingualLocalRange(node,0,node.textContent.length);if(!contents)continue;
  if(range.compareBoundaryPoints(Range.START_TO_START,contents)>0||range.compareBoundaryPoints(Range.END_TO_END,contents)<0)return null;
  if(node.contains(range.startContainer))range.setStartBefore(node);if(node.contains(range.endContainer))range.setEndAfter(node);
 }
 return range;
}
function bilingualSentencePairs(source,ko,block,output){
 source.querySelectorAll('[data-en-sentence]').forEach(n=>n.replaceWith(...n.childNodes));ko.replaceChildren();
 const sentences=Array.isArray(output?.sentences)?output.sentences:[],valid=[];
 let previousEnd=-1;for(const s of sentences){const range=bilingualSourceRange(source,s.start,s.end);if(!s.id||s.start<previousEnd||!range||range.toString()!==s.exact||!source.contains(range.startContainer)||!source.contains(range.endContainer))return false;previousEnd=s.end;valid.push(s)}
 if(!valid.length)return false;
 const formulas=[...source.querySelectorAll('math')];
 for(const s of [...valid].reverse()){const range=bilingualSourceRange(source,s.start,s.end),span=document.createElement('span');span.className='bilingual-sentence bilingual-en-sentence';span.dataset.enSentence=s.id;span.lang='en';span.tabIndex=0;span.append(range.extractContents());range.insertNode(span)}
 for(const s of valid){const span=document.createElement('div');span.className='bilingual-sentence bilingual-ko-sentence';span.lang='ko';Object.assign(span.dataset,{koSentence:s.id,sentenceId:s.id,blockId:block.id,enStart:String(s.start),enEnd:String(s.end),enExact:s.exact});span.tabIndex=0;bilingualTranslation(span,s.ko_template||s.ko,formulas);ko.append(span)}
 const pairs=valid.map(s=>[...source.querySelectorAll('[data-en-sentence]')].find(n=>n.dataset.enSentence===s.id)).map((en,i)=>[en,ko.children[i]]);
 for(const pair of pairs)for(const el of pair){el.onpointerenter=()=>pair.forEach(n=>n.classList.add('sentence-linked'));el.onpointerleave=()=>pair.forEach(n=>n.classList.remove('sentence-linked'));el.onfocus=()=>pair.forEach(n=>n.classList.add('sentence-linked'));el.onblur=()=>pair.forEach(n=>n.classList.remove('sentence-linked'))}
 ko._sentencePairs=pairs;return true;
}
function alignBilingualSentences(root){
 for(const ko of root.querySelectorAll('.bilingual-ko'))for(const pair of ko._sentencePairs||[]){pair.forEach(n=>n.style.minHeight='');if(getComputedStyle(ko.parentElement).gridTemplateColumns.split(' ').length<2)continue;const height=Math.max(...pair.map(n=>n.getBoundingClientRect().height));pair.forEach(n=>n.style.minHeight=height+'px')}
}
window.paintBilingualUserHighlights=function(annotations=[]){
 if(!window.CSS?.highlights)return;const root=$('#original-paper');if(!root)return;root.querySelectorAll('.sentence-has-source-note').forEach(n=>n.classList.remove('sentence-has-source-note'));
 for(const a of annotations){if(a.version!==originalDoc?.version)continue;const selection=a.translated_selection;for(const ko of root.querySelectorAll('[data-ko-sentence]')){if(selection&&ko.dataset.koSentence===selection.sentence_id&&ko.dataset.blockId===selection.block_id){const snapshot=a.translation_snapshot??selection.translation_snapshot;const r=typeof snapshot==='string'&&snapshot!==ko.textContent?null:bilingualLocalRange(ko,selection.start,selection.end);if(r&&r.toString()===selection.exact)CSS.highlights.get('reader-'+a.color)?.add(r)}else if(!selection&&a.start<Number(ko.dataset.enEnd)&&a.end>Number(ko.dataset.enStart)){ko.classList.add('sentence-has-source-note');ko.title='이 번역 문장의 영어 원문에 저장된 하이라이트가 있습니다.'}}}
};

const bilingualSnapshots=new WeakMap();
function applyBilingual(){
 const root=$('#original-paper');if(!root||!bilingualValue||bilingualValue.version!==originalDoc?.version)return;
 const signature=JSON.stringify(bilingualValue.blocks);const previous=bilingualSnapshots.get(root);if(previous?.signature===signature)return;
 const sources=new Map([...root.querySelectorAll('[data-reader-block]')].map(n=>[n.dataset.readerBlock,n]));
 for(const block of originalDoc.blocks||[]){const source=sources.get(block.id);if(!source)continue;let row=source.parentElement;
 if(!row.classList.contains('bilingual-row')){row=document.createElement('div');row.className='bilingual-row';source.before(row);row.append(source);const ko=document.createElement('div');ko.className='bilingual-ko';ko.dataset.readerGenerated='true';ko.lang='ko';row.append(ko)}
 const output=bilingualValue.blocks[block.id],ko=row.querySelector('.bilingual-ko');const text=output?.ko_template||output?.ko||'한국어 번역 대기 중…';
 const paired=bilingualSentencePairs(source,ko,block,output);row.classList.toggle('sentence-aligned',paired);ko.dataset.translationUnit=paired?'sentence':'paragraph';
 if(!paired){const label=document.createElement('small');label.className='bilingual-unit-label';label.dataset.readerGenerated='true';label.textContent=output?'문단 번역':'번역 대기';const body=document.createElement('div');bilingualTranslation(body,text,[...source.querySelectorAll('math')]);ko.append(label,body);ko._sentencePairs=[];window.formatReadingStructure?.(body)}ko.classList.toggle('pending',!output);

 }
 paintHighlights();paintAuto();
 previous?.observer?.disconnect();let width=-1;const observer=new ResizeObserver(()=>{if(!root.isConnected){observer.disconnect();return}const next=root.clientWidth;if(next===width)return;width=next;requestAnimationFrame(()=>alignBilingualSentences(root))});observer.observe(root);requestAnimationFrame(()=>alignBilingualSentences(root));
 bilingualSnapshots.set(root,{signature,observer});
 const evidence=$('#auto-evidence');const highlights=Object.values(bilingualValue.blocks).flatMap(b=>bilingualBlockHighlights(b));
 if(!evidence)return;
 evidence.innerHTML=highlights.map((h,i)=>`<button data-auto-jump="${i}" class="auto-evidence-item"><b>${escape(autoLabels[h.category])}</b><q>${escape(h.exact)}</q><span>${escape(h.reason)} · ${escape(h.attribution)}</span></button>`).join('')||'<p>검증된 원문 인용과 분류 이유가 여기에 표시됩니다.</p>';
 evidence.onclick=e=>{const b=e.target.closest('[data-auto-jump]');if(!b)return;const h=highlights[+b.dataset.autoJump],r=readerRange(h.start,h.end);r?.startContainer.parentElement.scrollIntoView({block:'center'});if(r&&window.CSS?.highlights)CSS.highlights.set('reader-focus',new Highlight(r))};
}
function bilingualBlockHighlights(block){const seen=new Set();return [...(block.highlights||[]),...(block.sentences||[]).flatMap(s=>s.highlights||[])].filter(h=>{const key=JSON.stringify([h.start,h.end,h.exact,h.category]);if(seen.has(key))return false;seen.add(key);return true})}
function paintAuto(){if(!window.CSS?.highlights)return;const resolve=readerRangeResolver(),groups=Object.fromEntries(Object.keys(autoLabels).map(k=>[k,[]]));if(bilingualValue?.version===originalDoc?.version){for(const block of Object.values(bilingualValue.blocks)){for(const h of bilingualBlockHighlights(block)){if(!autoEnabled.has(h.category)||!groups[h.category])continue;const range=resolve(h.start,h.end);if(range&&range.toString()===h.exact)groups[h.category].push(range)}}}for(const block of Object.values(bilingualValue?.version===originalDoc?.version?bilingualValue.blocks:{}))for(const sentence of block.sentences||[]){const ko=[...document.querySelectorAll('[data-ko-sentence]')].find(n=>n.dataset.koSentence===sentence.id);if(!ko)continue;for(const h of sentence.highlights||[]){if(!autoEnabled.has(h.category)||!groups[h.category])continue;const r=bilingualLocalRange(ko,h.ko_start,h.ko_end);if(r&&r.toString()===h.ko_exact)groups[h.category].push(r)}}for(const [category,ranges] of Object.entries(groups)){const highlight=new Highlight(...ranges);if('priority' in highlight)highlight.priority=1;CSS.highlights.set('auto-'+category,highlight)}}
