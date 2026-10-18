const {chromium}=require('playwright');
const assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.PLAYWRIGHT_CHANNEL||'chrome'});
 try{
  const page=await browser.newPage({viewport:{width:650,height:1000}}),requests=[];
  page.on('request',r=>requests.push(r.url()));
  await page.setContent('<main id="host"></main>');
  await page.addScriptTag({path:'static/walkthrough-lab.js'});await page.addStyleTag({path:'static/walkthrough-lab.css'});
  await page.evaluate(()=>{window.dispose=renderWalkthroughLab(document.querySelector('#host'),{arxiv:'2602.15922v1'},{input_shape:'<script>invalid</script>',output_shape:'B × T × D'})});
  assert.equal(await page.locator('.lab-assumptions script').count(),0);
  assert.match(await page.locator('.lab-assumptions').textContent(),/<script>invalid<\/script>/);
  await page.locator('[data-time]').fill('0.5');
  assert.equal(await page.locator('[data-current]').textContent(),'0.00');
  await page.locator('[data-coordinate="3"]').first().click();
  assert.equal(await page.locator('[data-current]').textContent(),'-0.50');
  await page.locator('[data-time]').focus();await page.keyboard.press('ArrowRight');
  assert.equal(await page.locator('[data-time]').inputValue(),'0.75');
  assert.equal(await page.locator('[data-current]').textContent(),'0.25');
  await page.locator('[data-mode="training"]').click();
  assert.equal(await page.locator('[data-time]').inputValue(),'0');
  await page.locator('[data-bias]').fill('0.5');
  assert.equal(await page.locator('[data-loss]').textContent(),'0.25');
  assert.equal(await page.locator('[data-gradient]').textContent(),'1.00');assert.match(await page.locator('.lab-time-convention').textContent(),/t=1−σ/);assert.match(await page.locator('.lab-mode-result').textContent(),/코드 방향 target vσ/);
  await page.locator('[data-mode="inference"]').click();
  await page.locator('[data-phase="4"]').click();
  for(const t of [.25,.5,.75,1]){await page.locator('[data-next]').click();assert.equal(Number(await page.locator('[data-time]').inputValue()),t)}
  assert.equal(await page.locator('[data-array="2"][data-coordinate="3"]').getAttribute('data-value'),'1');
  await page.locator('[data-phase="6"]').click();assert.equal(await page.locator('.lab-cache strong').textContent(),'새 observation KV · 교체');
  await page.locator('[data-reset]').click();assert.equal(await page.locator('.tensor-lab').getAttribute('data-phase'),'0');
  await page.locator('[data-play]').click();await page.waitForTimeout(760);assert.equal(await page.locator('.tensor-lab').getAttribute('data-phase'),'1');
  await page.evaluate(()=>dispose());await page.waitForTimeout(760);assert.equal(await page.locator('.tensor-lab').getAttribute('data-phase'),'1');
  await page.evaluate(()=>{window.dispose=renderWalkthroughLab(document.querySelector('#host'),{arxiv:'2602.15922'})});
  await page.locator('[data-play]').click();await page.evaluate(()=>{window.detached=document.querySelector('.tensor-lab');detached.remove()});
  await page.waitForTimeout(760);assert.equal(await page.evaluate(()=>detached.querySelector('[data-play]').textContent),'재생');
  await page.evaluate(()=>renderWalkthroughLab(document.querySelector('#host'),{arxiv:'9999.12345'}));assert.equal(await page.locator('.tensor-lab').count(),0);
  await page.evaluate(()=>renderWalkthroughLab(document.querySelector('#host'),{arxiv:'2602.15922'}));
  for(const width of [650,400]){await page.setViewportSize({width,height:1000});assert.equal(await page.locator('.tensor-lab').evaluate(el=>el.scrollWidth>el.clientWidth+1),false)}
  await page.evaluate(()=>{dispose();document.querySelector('#host').innerHTML='';window.dispose=renderWalkthroughLab(document.querySelector('#host'),{arxiv:'2602.15922'},{id:'loss',mode:'training',title:'실제 선택 단계',input_shape:'B × T',output_shape:'scalar',evidence:[{label:'선택한 코드',url:'https://example.com/code'}]})});
  assert.equal(await page.locator('.tensor-lab').getAttribute('data-phase'),'3');
  assert.equal(await page.locator('.tensor-lab').getAttribute('data-mode'),'training');
  assert.equal(await page.locator('.tensor-lab h3').textContent(),'실제 선택 단계');
  assert.match(await page.locator('.lab-context').textContent(),/B × T/);
  assert.equal(await page.locator('.lab-step-sources a').getAttribute('href'),'https://example.com/code');
  assert.equal(await page.locator('.lab-flow path').count(),6);
  await page.locator('[data-phase="5"]').click();await page.locator('[data-time]').fill('1');
  assert.equal(await page.locator('[data-observation="0"]').getAttribute('cx'),'50');
  assert.match(await page.locator('.lab-observation-caption').textContent(),/실행 후 새 관측/);
  await page.addStyleTag({content:':root{--panel:rgb(32,36,42);--ink:rgb(230,233,238);--accent:rgb(165,187,237);--accent-wash:rgb(43,53,73)}'});
  assert.deepEqual(await page.locator('.tensor-lab').evaluate(el=>({background:getComputedStyle(el).backgroundColor,color:getComputedStyle(el).color})),{background:'rgb(32, 36, 42)',color:'rgb(230, 233, 238)'});
  await page.locator('[data-play]').click();assert.equal(await page.locator('.lab-data-token').getAttribute('data-moving'),'true');
  await page.locator('[data-play]').click();assert.equal(await page.locator('.lab-data-token').getAttribute('data-moving'),'false');
  await page.evaluate(()=>{dispose();window.dispose=renderWalkthroughLab(document.querySelector('#host'),{arxiv:'2602.15922'},{id:'__proto__',operation:'constructor'})});
  assert.equal(await page.locator('.tensor-lab').getAttribute('data-phase'),'0','untrusted IDs must not resolve inherited object properties');
  assert.equal(requests.length,0,'lab must not fetch or run AI');
  console.log('walkthrough lab: interpolation, MSE, gradient, Euler, modes, keyboard, escaping, timer cleanup and no network passed');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
