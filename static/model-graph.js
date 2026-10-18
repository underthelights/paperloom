'use strict';
const modelRelationLabels={adopted:'실제 백본 채택',implementation:'별도 구현 구성',related:'관련 기술 비교'};
function modelGraphData(p){
 const report=p?.reports?.at(-1);return report?.model_graph?.nodes?.length?{...report.model_graph,review:report.review?.verdict==='pass'?'AI 검수 통과 · 원문 확인 가능':'AI 분석 · 검수 필요'}:null;
}
async function mountModelGraph(host,p=null,conceptName=''){
 if(!host)return;
 try{
  let g=modelGraphData(p);
  if(!g){
   const applicable=!p||String(p.arxiv||'').replace(/v\d+$/,'')==='2602.15922';
   if(!applicable){host.remove();return}
   const response=await fetch('/model-ecosystem.json');if(!response.ok)throw Error('모델 관계 자료를 읽을 수 없습니다.');g=await response.json();
   if(conceptName&&!g.nodes.some(n=>n.concept===conceptName)&&conceptName!=='Video Diffusion Models'){host.remove();return}
  }
  if(!host.isConnected)return;
  const nodes=g.nodes.slice(0,24),ids=new Set(nodes.map(n=>n.id)),edges=g.edges.filter(e=>ids.has(e.source)&&ids.has(e.target)&&modelRelationLabels[e.kind]);
  host.innerHTML=`<div class="model-graph-heading"><h2>모델·기술 관계</h2><span class="caption">${escape(g.checked||'분석 시점')} · 인용·유사도 점수와 별개 · ${escape(g.review||'출처 대조 자료')}</span></div><p class="caption">실선 화살표: 실제 채택 · 짧은 점선: 별도 구현 · 긴 점선: 기술 비교(채택 주장 아님)</p><div class="model-graph-layout"><div><svg class="model-graph-map" viewBox="0 0 740 ${Math.max(300,Math.ceil((nodes.length-1)/2)*120+80)}" aria-label="모델 채택과 관련 기술 관계 지도"></svg><div class="model-edge-list" aria-label="모델 관계 근거"></div></div><aside class="model-node-detail" aria-live="polite"></aside></div>`;
  const center=nodes.find(n=>n.id===g.center)||nodes[0];if(!center)return;
  const points=new Map([[center.id,{x:370,y:55}]]);let i=0;
  for(const n of nodes.filter(n=>n.id!==center.id)){points.set(n.id,{x:i%2?550:190,y:175+Math.floor(i/2)*120});i++}
  const svg=host.querySelector('svg'),detail=host.querySelector('aside');
  svg.innerHTML=edges.map(e=>{const a=points.get(e.source),b=points.get(e.target),dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy)||1,boundary=Math.min(86/Math.max(.001,Math.abs(dx/d)),25/Math.max(.001,Math.abs(dy/d)))+10,ex=b.x-dx/d*boundary,ey=b.y-dy/d*boundary,cx=(a.x+ex)/2+(e.kind==='implementation'?dy/d*30:0),cy=(a.y+ey)/2-(e.kind==='implementation'?dx/d*30:0);return `<g class="model-edge ${e.kind}"><path d="M${a.x} ${a.y} Q${cx} ${cy} ${ex} ${ey}"/><path class="arrowhead" d="M${ex-dx/d*10-dy/d*5} ${ey-dy/d*10+dx/d*5} L${ex} ${ey} L${ex-dx/d*10+dy/d*5} ${ey-dy/d*10-dx/d*5}" ${e.kind==='related'?'hidden':''}/><title>${escape(modelRelationLabels[e.kind]+': '+e.reason)}</title></g>`}).join('')+nodes.map(n=>{const a=points.get(n.id);return `<g class="model-node" data-model-node="${escape(n.id)}" role="button" tabindex="0" aria-label="${escape(n.label)}" transform="translate(${a.x} ${a.y})"><rect x="-86" y="-25" width="172" height="50" rx="8"/><text text-anchor="middle" y="5">${escape(n.label.slice(0,24))}</text></g>`}).join('');
  host.querySelector('.model-edge-list').innerHTML=edges.map((e,i)=>`<button data-model-edge="${i}"><strong>${escape(nodes.find(n=>n.id===e.source).label)} → ${escape(nodes.find(n=>n.id===e.target).label)}</strong><span>${escape(modelRelationLabels[e.kind])} · ${escape(e.version||'')}</span></button>`).join('');
  function evidence(e){return `<p><b>${escape(modelRelationLabels[e.kind])}</b> · ${escape(e.version||'')}</p><p>${escape(e.reason)}</p><p>${e.evidence.map(s=>link(s.url,s.label||'근거 원문')).join(' · ')}</p>`}
  async function showNode(n){
   const connected=edges.filter(e=>e.source===n.id||e.target===n.id);
   const aid=String(n.paper_url||'').match(/arxiv\.org\/(?:abs|html)\/(\d{4}\.\d{4,5})/)?.[1];
   const local=state?.papers.find(p=>aid&&String(p.arxiv||'').replace(/v\d+$/,'')===aid);
   host.querySelectorAll('[data-model-node]').forEach(el=>el.classList.toggle('selected',el.dataset.modelNode===n.id));
   detail.innerHTML=`<h3>${escape(n.label)}</h3><p class="caption">${escape(n.owner||'개발 주체 미확인')}</p><p>${escape(n.summary||'')}</p><div class="model-resource-links">${local?'<button data-model-paper>논문 읽기</button>':link(n.paper_url,'논문 ↗')} ${link(n.code_url,'코드 ↗')}<button data-model-note>개념 노트</button></div>${connected.map(evidence).join('<hr>')}`;
   if(local)detail.querySelector('[data-model-paper]').onclick=()=>select(local.id,'html');
   detail.querySelector('[data-model-note]').onclick=async()=>{try{const list=await api('concepts');let v=list.find(v=>v.name.toLowerCase()===String(n.concept||n.label).toLowerCase());if(!v)v=await api('concept/create',{name:n.concept||n.label,...(p?.id?{paper_id:p.id}:{})});await openNotebook(v.id)}catch(e){toast(e.message)}};
  }
  host.onclick=e=>{const node=e.target.closest('[data-model-node]'),edge=e.target.closest('[data-model-edge]');if(node)showNode(nodes.find(n=>n.id===node.dataset.modelNode));if(edge){const v=edges[+edge.dataset.modelEdge];detail.innerHTML=`<h3>관계 근거</h3>${evidence(v)}`}};
  svg.onkeydown=e=>{if((e.key==='Enter'||e.key===' ')&&e.target.closest('[data-model-node]')){e.preventDefault();e.target.closest('[data-model-node]').dispatchEvent(new MouseEvent('click',{bubbles:true}))}};
  showNode(nodes.find(n=>n.concept===conceptName)||center);
 }catch(e){if(host.isConnected)host.innerHTML=`<p class="notice">모델 관계 지도: ${escape(e.message)}</p>`}
}
