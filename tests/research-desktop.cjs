const {_electron:electron}=require('playwright');
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
(async()=>{
 const profile=fs.mkdtempSync(path.resolve('work/research-ui-'));let client,origin;const errors=[];
 async function launch(){client=await electron.launch({executablePath:path.resolve('dist/mac-arm64/Paperloom.app/Contents/MacOS/Paperloom'),env:{...process.env,PAPERLOOM_PROFILE:profile}});const page=await client.firstWindow();page.on('pageerror',e=>errors.push(e.message));await page.locator('#intake-form').waitFor();await page.locator('.paper-row').first().click();await page.locator('.tldr').waitFor();origin=new URL(page.url()).origin;return page}
 async function post(route,data){const response=await fetch(origin+route,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});assert.equal(response.status,200);return response.json()}
 try{
  let page=await launch();assert.equal(await page.evaluate(()=>typeof require),'undefined');
  assert.equal(await page.locator('#candidate-count').innerText(),'873');assert.equal(await page.locator('#paper-count').innerText(),'1');
  await page.locator('[data-filter="candidate"]').click();assert.equal(await page.locator('.paper-row').count(),873);await page.locator('#search').fill('diffusion');assert.ok(await page.locator('.paper-row').count()>0);assert.ok(await page.locator('.paper-row').count()<873);await page.locator('#search').fill('');await page.locator('[data-filter="papers"]').click();
  await page.evaluate(()=>{localStorage.setItem('research.theme','light')});await page.reload();await page.locator('#intake-form').waitFor();await page.locator('.paper-row').first().click();await page.locator('.tldr').waitFor();assert.equal(await page.locator('html').getAttribute('data-theme'),'light');
  assert.equal(await page.locator('.overview-figure img').evaluate(i=>i.complete&&i.naturalWidth>0),true);
  assert.ok(await page.locator('.katex').count()>10);assert.equal(await page.locator('.katex-error').count(),0);
  assert.ok(await page.locator('#chat-form').evaluate(e=>e.getBoundingClientRect().bottom<=innerHeight));
  await page.screenshot({path:'work/research-light.png'});await page.locator('#theme').click();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');await page.screenshot({path:'work/research-dark.png'});
  await page.locator('[data-tab="graph"]').click();assert.ok(await page.locator('.node').count()>70);assert.ok(await page.locator('.context-edge').count()>0);await page.locator('[data-node="0"] circle').click();assert.match(await page.locator('#graph-detail').innerText(),/참고문헌/);await page.locator('#graph-plus').click();await page.screenshot({path:'work/research-graph.png'});
  await page.locator('[data-tab="labs"]').click();assert.match(await page.locator('#content').innerText(),/UNC|North Carolina/);await page.locator('[data-tab="code"]').click();assert.match(await page.locator('#content').innerText(),/확인 불가/);
  await page.locator('[data-tab="pdf"]').click();await page.waitForFunction(()=>document.querySelector('#pdf-pages')?.textContent.includes('/'),{},{timeout:30000});assert.match(await page.locator('#pdf-pages').innerText(),/^1 \/ /);await page.locator('#pdf-next').click();await page.waitForFunction(()=>document.querySelector('#pdf-pages')?.textContent.startsWith('2 /'));
  await page.evaluate(()=>{const node=[...document.querySelectorAll('.textLayer span')].find(n=>n.textContent.trim().length>20)?.firstChild;const range=document.createRange();range.selectNodeContents(node);const selection=getSelection();selection.removeAllRanges();selection.addRange(range);document.querySelector('#content').dispatchEvent(new MouseEvent('mouseup',{bubbles:true}))});await page.locator('#ask-selection').click();assert.ok(await page.locator('#quote-chip').isVisible());
  await page.locator('[data-side="notes"]').click();await page.locator('#notes').fill('Isolated profile persistence test.');await page.waitForFunction(()=>document.querySelector('#note-status').textContent==='저장됨');
  const oldOrigin=origin;await client.close();client=null;await assert.rejects(fetch(origin+'/api/research'));page=await launch();assert.equal(origin,oldOrigin);assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');await page.locator('[data-side="notes"]').click();assert.equal(await page.locator('#notes').inputValue(),'Isolated profile persistence test.');
  const initialized=await post('/mcp',{jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2025-03-26',capabilities:{},clientInfo:{name:'test',version:'1'}}});assert.equal(initialized.result.serverInfo.name,'paperloom-research');
  const listing=await post('/mcp',{jsonrpc:'2.0',id:2,method:'tools/list'});assert.ok(listing.result.tools.some(t=>t.name==='import_notion_metadata'));
  const denied=await fetch(origin+'/api/research/note',{method:'POST',headers:{'Content-Type':'application/json','Origin':'https://untrusted.example'},body:'{}'});assert.equal(denied.status,403);
  if(process.env.PAPERLOOM_LIVE_AI==='1'){
   await page.locator('[data-side="chat"]').click();await page.locator('#question').fill('이 논문의 공식 구현 저장소를 확인했나요? 현재 브리프에 근거해 한 문장으로 답하세요.');await page.locator('#send').click();await page.waitForFunction(()=>document.querySelectorAll('.message.assistant').length>0,{},{timeout:180000});assert.match(await page.locator('.message.assistant').innerText(),/확인|공식|구현/);
  }
  assert.deepEqual(errors,[]);console.log('PASS: packaged research brief, figures, math, themes/restart, metadata-only candidates, graph, PDF selection, notes, MCP, origin protection'+(process.env.PAPERLOOM_LIVE_AI==='1'?', live Codex conversation':''));
 }finally{if(client)await client.close();fs.rmSync(profile,{recursive:true,force:true})}
})().catch(e=>{console.error(e);process.exitCode=1});
