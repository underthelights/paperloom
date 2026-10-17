const { _electron: electron }=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
(async()=>{
 fs.mkdirSync('work',{recursive:true});
 require('node:child_process').execFileSync(path.resolve('.venv/bin/python'),['tests/pdf_fixture.py']);
 const profile=fs.mkdtempSync(path.resolve('work/editor-test-'));
 let client,origin;
 const errors=[];
 async function launch(){
  client=await electron.launch({executablePath:path.resolve('dist/mac-arm64/Paperloom.app/Contents/MacOS/Paperloom'),env:{...process.env,PAPERLOOM_PROFILE:profile}});
  const page=await client.firstWindow();page.on('pageerror',e=>errors.push(e.message));
  await page.locator('.paper-row').first().waitFor();origin=new URL(page.url()).origin;return page;
 }
 async function post(route,data){const r=await fetch(origin+'/api/'+route,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const v=await r.json();assert.equal(r.status,200,JSON.stringify(v));return v}
 try{
  let page=await launch();
  assert.equal(await page.locator('#library-count').innerText(),'903');
  assert.ok(await page.locator('#chat-form').evaluate(e=>e.getBoundingClientRect().bottom<=innerHeight));
  assert.equal(await page.evaluate(()=>typeof require),'undefined');
  await page.locator('[data-filter="all"]').click();
  assert.equal(await page.locator('.paper-row').count(),903);
  await page.locator('#paper-search').fill('diffusion');
  await page.waitForFunction(()=>document.querySelectorAll('.paper-row').length>0&&document.querySelectorAll('.paper-row').length<903);
  await page.locator('#paper-search').fill('');await page.locator('[data-filter="body"]').click();
  await page.waitForFunction(()=>document.querySelectorAll('.paper-row').length===109);
  const initialTitle=await page.locator('.document-title').innerText();
  await page.evaluate(()=>{const n=document.querySelector('#source-text');const walker=document.createTreeWalker(n,NodeFilter.SHOW_TEXT);let t;while(t=walker.nextNode()){if(t.textContent.trim().length>30){const r=document.createRange();r.setStart(t,0);r.setEnd(t,Math.min(90,t.textContent.length));const s=window.getSelection();s.removeAllRanges();s.addRange(r);break}}n.dispatchEvent(new MouseEvent('mouseup',{bubbles:true}));});
  await page.locator('#quote-chat').click();assert.ok(await page.locator('#quote-chip').isVisible());
  await page.locator('[data-side="notes"]').click();
  await page.locator('#review-note').fill('Editor persistence verification');await page.locator('#note-save').click();
  await page.waitForFunction(()=>document.querySelector('#note-status').textContent==='저장됨');
  const originalOrigin=origin;await client.close();client=null;await assert.rejects(fetch(origin+'/api/state'));
  page=await launch();assert.equal(origin,originalOrigin);assert.equal(await page.locator('.document-title').innerText(),initialTitle);
  await page.locator('[data-side="notes"]').click();assert.equal(await page.locator('#review-note').inputValue(),'Editor persistence verification');
  await page.locator('[data-side="chat"]').click();
  await page.screenshot({path:'work/editor-preview.png'});
  await page.locator('#import-open').click();await page.locator('#pdf-file').setInputFiles('work/test-reader.pdf');
  await page.waitForFunction(()=>document.querySelector('#pdf-pages').textContent==='1 / 2');
  await page.locator('.textLayer span').first().waitFor();
  assert.match(await page.locator('.textLayer').innerText(),/Selectable research text/);
  await page.locator('#pdf-next').click();await page.waitForFunction(()=>document.querySelector('#pdf-pages').textContent==='2 / 2');
  await page.locator('#pdf-prev').click();await page.waitForFunction(()=>document.querySelector('#pdf-pages').textContent==='1 / 2');
  await page.screenshot({path:'work/editor-pdf-preview.png'});
  if(process.env.PAPERLOOM_SKIP_LIVE_AI==='1'){assert.deepEqual(errors,[]);console.log('PASS: packaged editor layout, search, selection, notes/restart, PDF, stable origin and shutdown');return}
  const synthetic=await post('papers',{title:'Integration fixture — not a real paper',text:'Synthetic test material. The reported accuracy is 91 percent on ten toy samples. This is not a real experiment.',source:'test'});
  await page.evaluate(id=>localStorage.setItem('paperloom.active',id),synthetic.id);await page.reload();await page.locator('#context-title').filter({hasText:'Integration fixture'}).waitFor();
  await page.locator('#question').fill('자료에 제시된 정확도 숫자만 %와 함께 답하세요.');await page.locator('#send').click();
  await page.waitForFunction(()=>document.querySelectorAll('.message.assistant').length===1,{},{timeout:180000});
  assert.match(await page.locator('.message.assistant').innerText(),/91/);
  await page.locator('#question').fill('방금 답변의 근거가 되는 원문 문장 하나를 인용해줘.');await page.locator('#send').click();
  await page.waitForFunction(()=>document.querySelectorAll('.message.assistant').length===2,{},{timeout:180000});
  const result=await(await fetch(origin+'/api/state')).json();assert.equal(result.papers.find(p=>p.id===synthetic.id).chat.length,4);
  assert.deepEqual(errors,[]);
  console.log('PASS: Electron library/search, selected context, note persistence, isolated renderer, PDF text selection/page navigation, live Codex two-turn conversation, backend shutdown');
 }finally{if(client)await client.close();fs.rmSync(profile,{recursive:true,force:true})}
})().catch(e=>{console.error(e);process.exitCode=1});
