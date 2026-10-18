'use strict';
(function(){
 const toggle=document.getElementById('toggle-side'),menu=document.getElementById('secondary-views');
 const rail=document.querySelector('.library'),bar=document.querySelector('.topbar'),search=rail.querySelector('.search'),field=document.getElementById('search');
 rail.setAttribute('aria-label','작업공간 탐색');
 rail.querySelector('.brand').setAttribute('aria-label','Paperloom');
 bar.querySelector('.breadcrumb').textContent='paperloom';
 bar.insertBefore(search,bar.lastElementChild);
 field.placeholder='논문·저자·개념 검색';field.oninput=null;
 field.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();openCatalog({q:field.value.trim()})}});
 const theme=document.getElementById('theme');rail.querySelector('footer').prepend(theme);
 if(!theme.querySelector('.rail-label')){const label=document.createElement('span');label.className='rail-label';label.textContent='테마';theme.append(label)}
 const work=document.createElement('span');work.id='workspace-jobs';work.setAttribute('role','status');bar.lastElementChild.prepend(work);
 function syncWork(){const active=state?.jobs?.filter(j=>['queued','running'].includes(j.status))||[];work.hidden=!active.length;work.textContent=active.length?'분석 '+active.length:''}
 window.addEventListener('paperloom-state-changed',syncWork);syncWork();

 function sync(){
  const visible=document.body.classList.contains('context-open');
  toggle.setAttribute('aria-expanded',String(visible));
  toggle.textContent=visible?'패널 닫기':'대화·노트';
  document.querySelectorAll('#tabs [data-tab]').forEach(button=>button.setAttribute('aria-selected',String(button.classList.contains('selected'))));
  const selected=menu.querySelector('button.selected');menu.querySelector('summary').textContent=selected?selected.textContent:'자료';
 }
 window.addEventListener('paperloom-state-changed',()=>{
  for(const element of document.querySelectorAll('[data-paper-status]')){
   const entry=state?.papers?.find(p=>p.id===element.dataset.paperStatus);if(!entry)continue;
   const status=paperDisplayStatus(entry);
   if(element.textContent!==status.label)element.textContent=status.label;
   if(element.classList.contains('paper-state'))element.dataset.status=status.tone;else element.dataset.state=status.tone;
  }
 });
 window.syncStudio=sync;
 toggle.setAttribute('aria-controls','research-context');
 toggle.onclick=()=>{const open=document.body.classList.toggle('context-open');document.body.classList.remove('no-side');localStorage.setItem('research.contextOpen',String(open));sync()};
 if(localStorage.getItem('research.contextOpen')==='true')document.body.classList.add('context-open');
 menu.querySelectorAll('[data-tab]').forEach(button=>button.addEventListener('click',()=>{menu.open=false;sync()}));
 document.querySelectorAll('#tabs>[data-tab]').forEach(button=>button.addEventListener('click',sync));
 document.addEventListener('keydown',event=>{if(event.key!=='Escape')return;const preferences=document.getElementById('reader-preferences');if(preferences?.open){preferences.open=false;preferences.querySelector('summary').focus()}else if(menu.open){menu.open=false;menu.querySelector('summary').focus()}});
 document.addEventListener('pointerdown',event=>{if(menu.open&&!menu.contains(event.target))menu.open=false;const preferences=document.getElementById('reader-preferences');if(preferences?.open&&!preferences.contains(event.target))preferences.open=false});
 window.addEventListener('paperloom-view-changed',()=>queueMicrotask(sync));
 new MutationObserver(sync).observe(document.body,{attributes:true,attributeFilter:['class']});
 sync();
})();
