const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict');
(async()=>{
 const root=path.resolve('static');
 const server=http.createServer((req,res)=>{
  const name=new URL(req.url,'http://localhost').pathname.slice(1)||'research.html',file=path.resolve(root,name);
  if(!file.startsWith(root+path.sep)||!fs.existsSync(file)){res.writeHead(404);return res.end()}
  res.setHeader('Content-Type',name.endsWith('.js')?'application/javascript':name.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file));
 }).listen(0,'127.0.0.1');await new Promise(resolve=>server.once('listening',resolve));
 let browser;
 try{
  browser=await chromium.launch({headless:true,channel:process.env.PLAYWRIGHT_CHANNEL||'chrome'});
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],requests=[];
  page.on('pageerror',error=>errors.push(error.message));
  const long='A long research title '.repeat(30);
  let items=[{id:'saved',title:long,input:'Original discovery',status:'ready',messages:[],organized:false,result:{concepts:['Control'],connections:[],papers:[],summary:'A verified source',collection:'Robotics'}}];
  const papers=[{id:'resume',title:long,arxiv:'2602.15922',status:'ready',updated:'2026-10-18',year:'2026'},{id:'legacy',title:'Hidden candidate',status:'candidate'}];
  await page.route('**/api/**',async route=>{
   const pathname=new URL(route.request().url()).pathname;let body={};
   if(pathname==='/api/research')body={papers,jobs:[],counts:{papers:1,candidates:1},notion:{}};
   else if(pathname==='/api/inbox'){
    if(route.request().method()==='POST'){
     const sent=route.request().postDataJSON();requests.push(sent);
     body={id:'new',title:sent.text,input:sent.text,messages:[{role:'user',content:sent.text}],status:'queued'};items=[body,...items];
    }else body=items;
   }else if(pathname==='/api/concepts')body=[];
   return route.fulfill({json:body});
  });
  await page.goto('http://127.0.0.1:'+server.address().port);await page.locator('#intake-form').waitFor();
  await page.addStyleTag({path:'static/inbox-studio.css'});
  assert.equal(await page.locator('.inbox-top h1').textContent(),'수집함');
  assert.equal(await page.locator('[data-resume-paper]').count(),1);
  assert.equal(await page.locator('#inbox-graph-disclosure').getAttribute('open'),null);
  assert.equal(await page.locator('#inbox-map [data-map-node]').count(),0,'closed graph must not run layout');
  assert.ok(await page.locator('.inbox-discoveries').evaluate(el=>el.compareDocumentPosition(document.querySelector('#inbox-graph-disclosure'))&Node.DOCUMENT_POSITION_FOLLOWING));
  await page.evaluate(()=>{window.graphCalls=0;const draw=drawInboxMap;drawInboxMap=()=>{window.graphCalls++;draw()}});
  await page.locator('#intake-text').fill('Draft must survive polling');
  items=[{...items[0],input:'Updated remote discovery'}];
  await page.evaluate(()=>loadInbox());
  assert.equal(await page.locator('#intake-text').inputValue(),'Draft must survive polling');
  assert.equal(await page.evaluate(()=>window.graphCalls),0);
  await page.locator('#inbox-graph-disclosure>summary').click();
  await page.waitForFunction(()=>window.graphCalls===1);
  await page.locator('#inbox-graph-disclosure>summary').click();
  await page.locator('#inbox-graph-disclosure>summary').click();
  await page.waitForTimeout(50);
  assert.equal(await page.evaluate(()=>window.graphCalls),1,'toggle must reuse mounted graph');
  await page.evaluate(()=>loadInbox(true));
  assert.equal(await page.locator('#inbox-graph-disclosure').evaluate(el=>el.open),true);
  assert.equal(await page.locator('#intake-text').inputValue(),'Draft must survive polling');
  for(const width of [1440,800]){
   await page.setViewportSize({width,height:1000});
   const overflow=await page.locator('.inbox-studio').evaluate(el=>el.scrollWidth>el.clientWidth+1);
   assert.equal(overflow,false,'long titles must not widen inbox at '+width);
  }
  await page.locator('#new-intake').click();
  assert.equal(await page.locator('#intake-text').inputValue(),'');
  await page.locator('#intake-text').fill('https://arxiv.org/abs/2602.15922');
  await page.locator('#intake-form button').click();
  await page.waitForFunction(()=>document.querySelector('#intake-form button').disabled);
  assert.deepEqual(requests,[{text:'https://arxiv.org/abs/2602.15922',id:null}]);
  assert.deepEqual(errors,[]);
  console.log('PASS inbox studio: capture route, recent papers, lazy graph, polling drafts/disclosure, long title bounds');
 }finally{await browser?.close();server.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
