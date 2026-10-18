'use strict';
(function(){
 const toggle=document.getElementById('toggle-side'),menu=document.getElementById('secondary-views');
 function sync(){
  const visible=document.body.classList.contains('context-open');
  toggle.setAttribute('aria-expanded',String(visible));
  toggle.textContent=visible?'패널 닫기':'대화·노트';
  document.querySelectorAll('#tabs [data-tab]').forEach(button=>button.setAttribute('aria-selected',String(button.classList.contains('selected'))));
  const selected=menu.querySelector('button.selected');menu.querySelector('summary').textContent=selected?selected.textContent:'자료';
 }
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
