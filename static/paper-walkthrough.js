/* Evidence-linked reading aid; this renderer does not execute paper models. */
(function(){
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const text=v=>Array.isArray(v)?v.join(' × '):typeof v==='object'?'확인 불가':String(v??'확인 불가');
 const href=v=>{try{const u=new URL(v);return u.protocol==='https:'&&!u.username&&!u.password?u.href:''}catch{return ''}};
 window.renderPaperWalkthrough=function(paper,report){
  const host=document.querySelector('#content');if(!host)return;
  const data=report?.walkthrough,steps=Array.isArray(data?.steps)?data.steps.filter(x=>x&&typeof x==='object').slice(0,100):[];
  if(!steps.length){host.innerHTML='<div class="walk-empty"><h2>연산 해설</h2><p>이 논문에는 근거가 연결된 단계별 해설이 아직 없습니다. 코드와 설정을 확인한 분석 결과가 필요합니다.</p></div>';return}
  let index=0;
  const labels={source:'출처 기반 · 실행 검증 아님',illustrative:'설명용 예시',unknown:'확인 불가'},modes={training:'학습',inference:'추론',shared:'학습·추론 공통'};
  host.innerHTML=`<section class="paper-walkthrough"><header class="walk-heading"><div><h2>${esc(data.title||paper?.title||'연산 해설')}</h2><p>${esc(data.scope||'코드와 논문을 읽는 단계별 해설입니다.')}</p></div><span class="walk-counter" aria-live="polite"></span></header><progress class="walk-progress" max="${steps.length}" value="1" aria-label="해설 읽기 진행"></progress><div class="walk-layout"><details class="walk-toc" open><summary>단계 목차</summary><nav aria-label="연산 단계">${steps.map((s,i)=>`<button type="button" data-walk-step="${i}"><span>${String(i+1).padStart(2,'0')}</span>${esc(s.title||'단계 '+(i+1))}</button>`).join('')}</nav></details><article class="walk-explanation" tabindex="-1"></article><aside class="walk-visual" aria-label="연산 시각화"></aside></div><footer class="walk-controls"><button type="button" class="walk-prev">← 이전</button><span>모델 실행 결과가 아닌 출처 기반 해설</span><button type="button" class="walk-next">다음 →</button></footer></section>`;
  const root=host.querySelector('.paper-walkthrough');
  function draw(focus=false){
   const s=steps[index],status=labels[s.verification]||labels.unknown,mode=modes[s.mode]||'적용 모드 확인 필요';
   root.querySelector('.walk-counter').textContent=`${index+1} / ${steps.length}`;root.querySelector('progress').value=index+1;
   root.querySelectorAll('[data-walk-step]').forEach((b,i)=>{b.classList.toggle('active',i===index);if(i===index)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current')});
   const evidence=(Array.isArray(s.evidence)?s.evidence:[]).filter(e=>e&&href(e.url));
   const article=root.querySelector('.walk-explanation');article.innerHTML=`<div class="walk-badges"><span>${esc(mode)}</span><span class="walk-verification">${esc(status)}</span></div><h3>${esc(s.title||'단계 '+(index+1))}</h3><p class="walk-prose">${esc(s.explanation||'설명 확인 불가')}</p>${s.equation?`<h4>관계식</h4><pre class="walk-equation">${esc(text(s.equation))}</pre>`:''}<h4>확인 근거</h4>${evidence.length?`<ul class="walk-evidence">${evidence.map(e=>`<li><a href="${esc(href(e.url))}" target="_blank" rel="noopener noreferrer">${esc(e.label||e.url)} ↗</a></li>`).join('')}</ul>`:'<p>연결된 원문·코드 근거가 없습니다.</p>'}`;
   const concepts=Array.isArray(s.concepts)?s.concepts.filter(n=>typeof n==='string'&&n.trim()).slice(0,12):[];
   if(concepts.length&&typeof api==='function'&&typeof openNotebook==='function'){
    const section=document.createElement('div');section.className='walk-concepts';section.innerHTML='<h4>연결 개념</h4>'+concepts.map((n,i)=>`<button type="button" data-walk-concept="${i}">${esc(n)} ↗</button>`).join('');article.append(section);
    section.querySelectorAll('button').forEach(b=>b.onclick=async()=>{b.disabled=true;try{const name=concepts[Number(b.dataset.walkConcept)],list=await api('concepts');let v=list.find(c=>String(c.name).toLowerCase()===name.toLowerCase());if(!v)v=await api('concept/create',{name,...(paper?.id?{paper_id:paper.id}:{})});if(root.isConnected)await openNotebook(v.id)}catch(e){if(typeof toast==='function')toast(e.message);else{const error=document.createElement('p');error.textContent=e.message;section.append(error)}}finally{b.disabled=false}});
   }
   const visual=root.querySelector('.walk-visual');visual.innerHTML=`<div class="walk-diagram"><div class="walk-tensor"><span>입력 shape</span><code>${esc(text(s.input_shape))}</code></div><span class="walk-arrow" aria-hidden="true">↓</span><div class="walk-operation">${esc(s.operation||'연산 확인 필요')}</div><span class="walk-arrow" aria-hidden="true">↓</span><div class="walk-tensor"><span>출력 shape</span><code>${esc(text(s.output_shape))}</code></div><p class="walk-visual-note">${esc(status)}. 차원 기호와 설정은 왼쪽 근거를 확인하세요.</p></div>`;
   if(['permute','patchify'].includes(s.operation)){
    const demo=document.createElement('section');demo.className='walk-matrix-demo';
    const transpose=s.operation==='permute',values=transpose?[1,2,3,4,5,6]:Array.from({length:16},(_,i)=>i+1);
    const order=transpose?[1,4,2,5,3,6]:[1,2,5,6,3,4,7,8,9,10,13,14,11,12,15,16];
    const group=n=>transpose?Math.floor((n-1)/3):Math.floor(Math.floor((n-1)/4)/2)*2+Math.floor(((n-1)%4)/2);
    const cell=n=>`<button type="button" data-toy-cell="${n}" class="walk-cell walk-group-${group(n)}" aria-label="예시 값 ${n}의 위치 확인">${n}</button>`;
    demo.innerHTML=`<h4>${transpose?'축 교환: 위치가 어떻게 바뀌는가':'패치: 이웃 픽셀을 하나의 벡터로 묶기'}</h4><p>논문과 독립적인 작은 교육용 배열입니다. 실제 DreamZero 입력·가중치·출력이 아닙니다.</p><div class="walk-matrix-pair"><div><h5>${transpose?'입력 2 × 3':'입력 4 × 4'}</h5><div class="walk-grid" style="--walk-columns:${transpose?3:4}" data-toy-side="input">${values.map(cell).join('')}</div></div><span aria-hidden="true">→</span><div><h5>${transpose?'출력 3 × 2':'4개 패치 × 4개 값'}</h5><div class="walk-grid" style="--walk-columns:${transpose?2:4}" data-toy-side="output">${order.map(cell).join('')}</div></div></div><p class="walk-toy-detail" aria-live="polite">숫자를 누르면 같은 값의 입력·출력 위치를 확인합니다.</p><p>${transpose?'y[j,i] = x[i,j]. 값은 그대로이고 축과 위치만 바뀝니다. 위 논문의 고차원 permute를 이 2차원 예시와 혼동하지 마세요.':'각 색은 하나의 2 × 2 패치입니다. 행 우선 순서로 4개 값을 나열했습니다. 실제 Conv3d patch embedding에는 학습된 투영이 추가되며 이 예시에는 포함되지 않습니다.'}</p>`;
    visual.append(demo);demo.querySelectorAll('[data-toy-cell]').forEach(b=>b.onclick=()=>{const n=Number(b.dataset.toyCell),i=values.indexOf(n),o=order.indexOf(n);demo.querySelectorAll('[data-toy-cell]').forEach(c=>{const selected=Number(c.dataset.toyCell)===n;c.classList.toggle('selected',selected);c.setAttribute('aria-pressed',String(selected))});demo.querySelector('.walk-toy-detail').textContent=transpose?`값 ${n}: x[${Math.floor(i/3)},${i%3}] → y[${Math.floor(o/2)},${o%2}] (0부터 센 인덱스)`:`값 ${n}: x[${Math.floor(i/4)},${i%4}] → 패치 ${Math.floor(o/4)}, 벡터 위치 ${o%4} (0부터 센 인덱스)`});
   }
   if(s.operation==='attention'){
    const demo=document.createElement('div');demo.className='walk-attention';demo.innerHTML='<h4>Softmax 직접 보기</h4><p>논문과 독립적인 숫자 예시입니다. 실제 모델의 가중치·출력이 아닙니다.</p><label>첫 attention logit <input class="walk-logit" type="range" min="-4" max="4" step="0.1" value="1"><output class="walk-logit-value">1.0</output></label><p><code>pᵢ = exp(zᵢ − max(z)) / Σⱼ exp(zⱼ − max(z))</code></p><div class="walk-bars" aria-live="polite"></div>';
    visual.append(demo);const update=()=>{const z=[Number(demo.querySelector('input').value),0,-1],max=Math.max(...z),exp=z.map(v=>Math.exp(v-max)),total=exp.reduce((a,b)=>a+b,0);demo.querySelector('output').textContent=z[0].toFixed(1);demo.querySelector('.walk-bars').innerHTML=z.map((v,i)=>`<div><span>z${i+1} = ${v.toFixed(1)}</span><meter min="0" max="1" value="${exp[i]/total}" aria-label="토큰 ${i+1} attention 확률"></meter><strong>${(exp[i]/total*100).toFixed(1)}%</strong></div>`).join('')};demo.querySelector('input').oninput=update;update();
   }
   root.querySelector('.walk-prev').disabled=index===0;root.querySelector('.walk-next').disabled=index===steps.length-1;if(focus)article.focus({preventScroll:true});
  }
  root.querySelectorAll('[data-walk-step]').forEach(b=>b.onclick=()=>{index=Number(b.dataset.walkStep);draw(true)});
  root.querySelector('.walk-prev').onclick=()=>{if(index>0){index--;draw(true)}};root.querySelector('.walk-next').onclick=()=>{if(index<steps.length-1){index++;draw(true)}};draw();
 };
})();
