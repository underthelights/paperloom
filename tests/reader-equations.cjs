const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict');

(async()=>{
 const staticRoot=path.resolve('static');
 const server=http.createServer((req,res)=>{
  const name=new URL(req.url,'http://localhost').pathname.slice(1)||'research.html';
  const file=path.resolve(staticRoot,name);
  if(!file.startsWith(staticRoot+path.sep)||!fs.existsSync(file)){res.writeHead(404);return res.end()}
  res.setHeader('Content-Type',name.endsWith('.js')?'application/javascript':name.endsWith('.css')?'text/css':name.endsWith('.json')?'application/json':'text/html');
  res.end(fs.readFileSync(file));
 }).listen(0,'127.0.0.1');
 await new Promise(resolve=>server.once('listening',resolve));
 let browser;
 try{
  browser=await chromium.launch({headless:true,channel:process.env.PLAYWRIGHT_CHANNEL||'chrome'});
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.route('**/api/**',route=>{
   const pathname=new URL(route.request().url()).pathname;
   return route.fulfill({json:pathname==='/api/research'?{papers:[],counts:{},jobs:[],notion:{}}:pathname==='/api/inbox'||pathname==='/api/concepts'?[]:{}});
  });
  await page.goto('http://127.0.0.1:'+server.address().port);
  await page.locator('#intake-form').waitFor();
  assert.equal(await page.evaluate(()=>typeof installEquationDerivations),'function');
  const payload=JSON.parse(fs.readFileSync('static/dreamzero-equations.json','utf8'));
  const equations=payload.equations;
  assert.ok(Array.isArray(equations)&&equations.length>0,'curated equations must exist');
  const equation=equations.find(eq=>eq.anchor&&eq.sections?.length);
  assert.ok(equation,'fixture needs a sourced equation with sections');
  const attack='<img src=x onerror="window.equationInjected=true">';
  equation.sections[0].text=attack+' literal explanation';
  equation.sections[0].title=attack+' literal title';
  await page.route('**/dreamzero-equations.json',route=>route.fulfill({json:payload}));
  const fixture={anchor:equation.anchor,alttext:equation.original_latex||equation.alttext||'x=y'};
  const before=await page.evaluate(({anchor,alttext})=>{
   paper={id:'equations-demo',arxiv:'2602.15922'};tab='html';renderEpoch++;
   originalDoc={version:'test',source:'https://arxiv.org/html/2602.15922v1'};
   document.querySelector('#content').innerHTML='<div id="original-paper"><article><p>Before 💡.</p><table class="ltx_equation" id="fixture-equation"><tbody><tr><td><math display="block"><mi>x</mi><mo>=</mo><mi>y</mi></math></td></tr></tbody></table><div class="ltx_equation"><math display="block"><mi>a</mi><mo>=</mo><mi>b</mi></math></div><p id="after-equations">Exact highlight after equations.</p></article></div><div id="reader-toolbar" hidden></div>';
   const root=document.querySelector('#original-paper');
   document.querySelector('#fixture-equation').id=anchor;
   root.querySelector('math').setAttribute('alttext',alttext);
   const text=root.textContent,exact=document.querySelector('#after-equations').textContent,start=text.indexOf(exact);
   return {html:root.innerHTML,text,exact,start,end:start+exact.length,range:readerRange(start,start+exact.length).toString()};
  },fixture);
  assert.equal(before.range,before.exact);
  await page.evaluate(()=>installEquationDerivations(document.querySelector('#original-paper'),paper.id,renderEpoch));
  const panels=page.locator('details.equation-derivation');
  assert.ok(await panels.count()>=2,'display and table equations need panels');
  assert.equal(await page.locator('details.equation-derivation:not([data-reader-generated])').count(),0);
  const restored=await page.evaluate(({start,end})=>{
   const root=document.querySelector('#original-paper'),clone=root.cloneNode(true);
   clone.querySelectorAll('[data-reader-generated]').forEach(node=>node.remove());
   const range=readerRange(start,end),selection=getSelection();selection.removeAllRanges();selection.addRange(range);captureReaderSelection();
   return {html:clone.innerHTML,text:clone.textContent,range:range.toString(),selection:readerSelection};
  },before);
  assert.equal(restored.text,before.text);
  assert.equal(restored.html,before.html,'original MathML and prose must remain unchanged');
  assert.equal(restored.range,before.exact);
  assert.equal(restored.selection.start,before.start);
  assert.equal(restored.selection.end,before.end);
  assert.equal(restored.selection.exact,before.exact);
  await panels.first().evaluate(node=>{node.open=true;node.querySelectorAll('details').forEach(child=>child.open=true)});
  assert.ok(await panels.first().locator('section,details').count()>0,'derivation must have structured sections');
  assert.match(await panels.first().textContent(),/literal explanation/);
  assert.equal(await panels.locator('img').count(),0,'curated strings must not become HTML');
  assert.equal(await page.evaluate(()=>!!window.equationInjected),false);
  const sizes=await page.locator('#original-paper math[display="block"]').evaluateAll(nodes=>nodes.filter(node=>!node.closest('[data-reader-generated]')).map(node=>parseFloat(getComputedStyle(node).fontSize)));
  assert.ok(sizes.length>=2&&sizes.every(size=>size>=22),JSON.stringify(sizes));
  const count=await panels.count();
  await page.evaluate(()=>installEquationDerivations(document.querySelector('#original-paper'),paper.id,renderEpoch));
  assert.equal(await panels.count(),count,'reinstall must be idempotent');
  await page.evaluate(async html=>{
   const root=document.querySelector('#original-paper');root.innerHTML=html;
   root.querySelector('math').setAttribute('alttext','different equation in a new source version');
   await installEquationDerivations(root,paper.id,renderEpoch);
  },before.html);
  assert.doesNotMatch(await page.locator('#original-paper').textContent(),/literal explanation|literal title/,'same anchor with different equation must not reuse curated derivation');
  await page.evaluate(async html=>{
   const root=document.querySelector('#original-paper');root.innerHTML=html;
   paper={id:'other-paper',arxiv:'2501.00103'};originalDoc={version:'test',source:'https://arxiv.org/html/2501.00103v1'};renderEpoch++;
   await installEquationDerivations(root,paper.id,renderEpoch);
  },before.html);
  assert.doesNotMatch(await page.locator('#original-paper').textContent(),/literal explanation|literal title/,'other papers must not receive DreamZero derivations');
  assert.deepEqual(errors,[]);
  console.log('PASS equation derivations: unchanged source, exact UTF-16 offsets, table math sizing, safe text, idempotence, paper isolation');
 }finally{await browser?.close();server.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
