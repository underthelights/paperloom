const {_electron:electron}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
(async()=>{
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),'paperloom-close-tab-'));let app;
 try{
  const bundle=path.resolve(process.env.PAPERLOOM_TEST_APP||'dist/mac-arm64/Paperloom.app');
  app=await electron.launch({executablePath:path.join(bundle,'Contents/MacOS/Paperloom'),env:{...process.env,PAPERLOOM_PROFILE:profile}});
  const page=await app.firstWindow(),errors=[];page.setDefaultTimeout(10000);page.on('pageerror',e=>errors.push(e.message));await page.waitForLoadState('domcontentloaded');await page.locator('#intake-form').waitFor();await page.waitForFunction(()=>typeof closePaperTab==='function');
  const menu=await app.evaluate(({Menu})=>{const item=Menu.getApplicationMenu().getMenuItemById('close-paper-tab');return item?{id:item.id,accelerator:item.accelerator}:null});assert.equal(menu?.id,'close-paper-tab');assert.ok(/(?:CmdOrCtrl|CommandOrControl)\+W/i.test(menu.accelerator));
  const records=[1,2].map(n=>({id:'tab-fixture-'+n,title:'Tab fixture '+n,status:'ready',authors:[],year:'2026',url:'',arxiv:'2602.0000'+n,source:'arXiv',notes:'',chat:[],reports:[],references:[]}));
  await page.route('**/api/research/paper/tab-fixture-*',r=>r.fulfill({json:records.find(p=>r.request().url().endsWith(p.id))}));
  await page.route('**/api/reader/**',r=>r.fulfill({json:{status:'ready',blocks:{},total:0}}));
  const pressClose=()=>app.evaluate(({BrowserWindow})=>{const w=BrowserWindow.getAllWindows()[0];w.focus();w.webContents.focus();const modifiers=[process.platform==='darwin'?'meta':'control'];w.webContents.sendInputEvent({type:'keyDown',keyCode:'W',modifiers});w.webContents.sendInputEvent({type:'keyUp',keyCode:'W',modifiers})});
  const windows=()=>app.evaluate(({BrowserWindow})=>BrowserWindow.getAllWindows().filter(w=>!w.isDestroyed()).length);
  const openBoth=async()=>{await page.evaluate(async records=>{openPapers=[];activeId=null;paper=null;state.papers=records;await select(records[0].id,'brief');await select(records[1].id,'brief')},records);assert.equal(await page.locator('[data-paper-tab]').count(),2)};
  console.log('CHECK textarea shortcut');await openBoth();await page.locator('#question').focus();assert.equal(await page.evaluate(()=>document.activeElement.id),'question');await pressClose();await page.waitForFunction(()=>openPapers.length===1);assert.equal(await windows(),1);assert.equal(await page.locator('[data-paper-tab]').getAttribute('data-paper-tab'),records[0].id);assert.equal(await page.evaluate(()=>activeId),records[0].id);
  console.log('CHECK native menu last tab');await app.evaluate(({Menu,BrowserWindow})=>{const item=Menu.getApplicationMenu().getMenuItemById('close-paper-tab');item.click(item,BrowserWindow.getAllWindows()[0],{})});await page.locator('#catalog-form').waitFor();assert.equal(await page.locator('[data-paper-tab]').count(),0);assert.equal(await windows(),1);
  console.log('CHECK no-tab shortcut');await pressClose();assert.equal(await windows(),1);assert.equal(await page.locator('[data-paper-tab]').count(),0);
  console.log('CHECK consecutive shortcuts');await openBoth();await pressClose();await page.waitForFunction(()=>openPapers.length===1&&!closingPaperTab);assert.equal(await windows(),1);await pressClose();await page.waitForFunction(()=>openPapers.length===0&&!closingPaperTab);assert.equal(await windows(),1);await page.locator('#catalog-form').waitFor();assert.deepEqual(errors,[]);console.log('PASS packaged Cmd+W with textarea focus, native menu, last-tab catalog, no-tab no-op, repeated accelerator, window retained; isolated profile');
 }finally{if(app)await app.close();fs.rmSync(profile,{recursive:true,force:true})}
})().catch(e=>{console.error(e);process.exitCode=1});
