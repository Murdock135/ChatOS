// Fictional browser fixture: no private workspace, source account or model calls.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require(process.env.CHATOS_PLAYWRIGHT_PATH || 'playwright-core');
const root = path.resolve(__dirname, '../frontend/dist');
const output = path.resolve(__dirname, '../docs/design/evidence/v4');
fs.mkdirSync(output, {recursive:true});
const topics = ['Garden planning', 'Interface design', 'Research methods', 'Travel journals', 'Music practice', 'Cooking notes'];
const documents = topics.flatMap((topic,g)=>Array.from({length:18},(_,i)=>({
  source:i%2?'codex':'chatgpt', id:`fiction-${g}-${i}`, title:`${topic}: ${i<9?'Early ideas':'Weekly review'} ${i+1}`,
  group:`topic-${g}`, x:Math.cos(g*Math.PI/3)*8+(i%6)*.5, y:Math.sin(g*Math.PI/3)*8+Math.floor(i/6)*.6,
  date:'2026-11-09', capture:'available_visible_messages', membership_strength:.5+i/36,
  excerpt:`Fictional ${topic.toLowerCase()} conversation about ${i<9?'early ideas and options':'weekly review and practice'}.`, projects:[],messages:2,models:['Sample model'],updated_at:'2026-11-09T15:00:00Z'
})));
const map={groups:Object.fromEntries(topics.map((t,i)=>[`topic-${i}`,t])),documents,checked_at:'2026-11-10T14:00:00Z',method:'Fictional map fixture',limits:'Predetermined coordinates for interface verification only.',search:{query:'',mode:'keyword',note:'Fictional data'},generation:'fixture',input_fingerprint:'fixture',freshness_note:'Fixture only'};
let mapUnavailable=false, failSmart=false;
const errors=[];
const requests=[];
const server=http.createServer((req,res)=>{
 const pathname=new URL(req.url,'http://localhost').pathname;
 const file=path.join(root, pathname==='/'?'index.html':pathname);
 if(!file.startsWith(root)||!fs.existsSync(file)){res.writeHead(404);res.end();return;}
 const ext=path.extname(file);res.setHeader('Content-Type',({'.html':'text/html','.css':'text/css','.js':'text/javascript','.woff2':'font/woff2','.svg':'image/svg+xml'})[ext]||'application/octet-stream');
 res.end(fs.readFileSync(file));
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({...(process.env.CHATOS_CHROME_PATH ? {executablePath:process.env.CHATOS_CHROME_PATH} : {channel:'chrome'}),headless:true});
 try {
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1,colorScheme:'dark'});
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/api/**',async route=>{
  const u=new URL(route.request().url()); requests.push(u.pathname+u.search);
  let data={},status=200;
  if(u.pathname==='/api/overview')data={workspace:'/fictional/workspace',projects:[],chats:documents.length,archived:0,status:{}};
  else if(u.pathname==='/api/chats'){
   if(failSmart&&u.searchParams.get('mode')==='hybrid'){status=400;data={error:'Fixture model unavailable'};}
   else {const q=(u.searchParams.get('q')||'').toLowerCase(),source=u.searchParams.get('source');const items=documents.filter(d=>(!q||d.title.toLowerCase().includes(q))&&(!source||d.source===source));const off=Number(u.searchParams.get('offset')||0),limit=Number(u.searchParams.get('limit')||50);data={items:items.slice(off,off+limit),total:items.length};}
  }
  else if(u.pathname==='/api/map'){data=mapUnavailable?{groups:{},documents:[],limits:'No local embeddings configured.',method:'Unavailable',search:{}}:map;}
  else if(u.pathname==='/api/home')data={directives:[],sources:[],conversations:documents.length,workspace:'/fictional/workspace',gmail:null};
  else if(u.pathname==='/api/chat'){const d=documents.find(d=>d.id===u.searchParams.get('id'));data={record:{...d,messages:[{id:'m1',role:'user',text:'How should I revisit these ideas?'},{id:'m2',role:'assistant',text:d.excerpt}]},annotation:{title:'',note:'',archived:false}};}
  else if(u.pathname==='/api/search-models')data={settings:{embedding:{model_id:'fixture/embed'},reranker:{model_id:'fixture/rank'}},downloaded:{},runtime_ready:false};
  else if(u.pathname==='/api/setup')data={supported:false,detail:'Fictional setup'};
  await route.fulfill({status,contentType:'application/json',body:JSON.stringify(data)});
 });
 await page.goto(`http://127.0.0.1:${server.address().port}`);
 await page.locator('#chat-list .chat-card').first().waitFor();
 await page.waitForTimeout(850);
 assert.equal(await page.locator('#view-explore').getAttribute('data-mode'),'search');
 assert.equal(await page.locator('#view-map').isVisible(),true);
 const initial=await page.locator('#view-chats').boundingBox();
 const stage=await page.locator('.explorer-stage').boundingBox();
 assert.ok(initial.width<=650 && initial.x>=stage.x+16 && initial.x+initial.width<=stage.x+stage.width-16,'Initial search panel must be bounded inside stage');
 await page.screenshot({path:path.join(output,'desktop-search.png'),fullPage:false,animations:'disabled'});
 await page.locator('#search').fill('Garden');await page.waitForTimeout(650);
 assert.match(await page.locator('#result-count').innerText(),/18 conversations/);
 await page.locator('#explore-toggle').click();await page.waitForTimeout(950);
 assert.equal(await page.locator('#search').inputValue(),'Garden');
 assert.equal(await page.locator('#view-explore').getAttribute('data-mode'),'map');
 const adjacent=await page.locator('#view-chats').boundingBox();
 assert.ok(adjacent.width<=400 && adjacent.x>=stage.x && adjacent.x+adjacent.width<stage.x+stage.width/2,'Map mode must leave most of the canvas visible');
 await page.screenshot({path:path.join(output,'desktop-map.png'),fullPage:false,animations:'disabled'});
 await page.locator('.map-discovery > summary').click();
 await page.locator('#map-legend .topic-chip').nth(1).click();
 await page.waitForTimeout(1150);
 assert.equal(await page.locator('#map-level').innerText(),'Subtopics');
 await page.locator('#map-legend .subtopic-chip').first().click();
 await page.waitForTimeout(1150);
 assert.equal(await page.locator('#map-level').innerText(),'Conversations');
 await page.locator('.map-discovery > summary').click();
 const point=await page.evaluate(()=>mapPositions.find(p=>p.x>420 && p.x<1100 && p.y>100 && p.y<500));
 assert.ok(point,'A conversation point is visible');
 const canvasBox=await page.locator('#map-canvas').boundingBox();
 await page.mouse.click(canvasBox.x+point.x,canvasBox.y+point.y);
 assert.equal(await page.locator('.map-result-panel').getAttribute('open'),'');
 assert.match(await page.locator('#map-selected-count').textContent(),/1 selected/);
 await page.screenshot({path:path.join(output,'desktop-conversations.png'),fullPage:false,animations:'disabled'});
 await page.locator('.map-result-panel > summary').click();
 await page.locator('#map-back').click();await page.waitForTimeout(1150);
 assert.equal(await page.locator('#map-level').innerText(),'Subtopics');
 await page.locator('#map-back').click();await page.waitForTimeout(1150);
 assert.equal(await page.locator('#map-level').innerText(),'Topics');
 await page.locator('#chat-list .chat-card').first().click();
 await page.locator('#reader').waitFor({state:'visible'});
 await page.keyboard.press('Escape');
 assert.equal(await page.locator('#reader').isVisible(),false);
 assert.equal(await page.locator('#view-explore').getAttribute('data-mode'),'map');
 const widths=[1180,900,768,560,390];const measurements=[];
 for(const width of widths){
  await page.setViewportSize({width,height:900});await page.waitForTimeout(800);
  for(const mode of ['map','search']){
   if(await page.locator('#view-explore').getAttribute('data-mode')!==mode)await page.locator('#explore-toggle').click();
   await page.waitForTimeout(800);
   const m=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,search:document.querySelector('#view-chats').getBoundingClientRect().toJSON(),canvas:document.querySelector('#map-canvas').getBoundingClientRect().toJSON(),map:document.querySelector('#view-map').getBoundingClientRect().toJSON(),layout:document.querySelector('#view-chats .library-layout').getBoundingClientRect().toJSON(),table:document.querySelector('#view-chats .conversation-table').getBoundingClientRect().toJSON(),controls:document.querySelector('.map-controls').getBoundingClientRect().toJSON()}));
   measurements.push({mode,...m});assert.ok(m.scroll<=width,`Overflow at ${width} ${mode}: ${m.scroll}`);
   assert.ok(m.search.width>240,`Unreadable search at ${width}`);
   assert.ok(m.layout.width>=m.search.width-4,`Narrow layout at ${width}`);
   assert.ok(m.table.width>=m.search.width-40,`Narrow table at ${width}`);
   assert.ok(m.controls.width<=64,`Oversized map controls at ${width}`);
   if(width<=760)assert.ok(mode==='search'?m.search.y<m.map.y:m.map.y<m.search.y,`Incorrect mobile ordering at ${width} ${mode}`);
   if(width===390)await page.screenshot({path:path.join(output,`phone-${mode}.png`),fullPage:false,animations:"disabled"});
  }
 }
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({reducedMotion:'reduce'});
 await page.locator('#search').fill('');await page.waitForTimeout(650);
 mapUnavailable=true;await page.reload();await page.locator('#chat-list .chat-card').first().waitFor();
 assert.equal(await page.locator('#search').isVisible(),true);
 failSmart=true;await page.locator('[data-search-mode="hybrid"]').first().click();
 await page.locator('#search-error').waitFor({state:'visible'});
 assert.match(await page.locator('#search-error-message').innerText(),/Fixture model unavailable/);
 await page.locator('[data-search-mode="keyword"]').first().click();
 await page.locator('#search-error').waitFor({state:'hidden'});
 await page.waitForFunction(()=>document.getElementById('result-count').textContent.includes('108 conversations'));
 assert.match(await page.locator('#result-count').innerText(),/108 conversations/);
 await page.screenshot({path:path.join(output,'desktop-empty-map.png'),fullPage:false,animations:"disabled"});
 mapUnavailable=false;await page.reload();await page.locator('#chat-list .chat-card').first().waitFor();
 await page.waitForFunction(()=>document.getElementById('map-summary').textContent.includes('108 conversations'));
 await page.locator('#theme-toggle').click();
 assert.equal(await page.locator('html').getAttribute('data-theme'),'light');
 await page.screenshot({path:path.join(output,'desktop-light-search.png'),fullPage:false,animations:'disabled'});
 await page.locator('#explore-toggle').click();await page.waitForTimeout(1100);
 await page.screenshot({path:path.join(output,'desktop-light-map.png'),fullPage:false,animations:'disabled'});
 await page.reload();await page.locator('#chat-list .chat-card').first().waitFor();
 assert.equal(await page.locator('html').getAttribute('data-theme'),'light');
 await page.setViewportSize({width:390,height:900});await page.waitForTimeout(900);
 await page.screenshot({path:path.join(output,'phone-light-search.png'),fullPage:false,animations:'disabled'});
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(output,'browser-checks.json'),JSON.stringify({status:'passed',fixture:'fictional conversations and predetermined coordinates',measurements,errors,requests:requests.length},null,2)+'\n');
 console.log(JSON.stringify({status:'passed',responsiveStates:measurements.length,errors,output}));
 } finally {await browser.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
