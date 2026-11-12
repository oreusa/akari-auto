// 投稿に付ける画像を作る（11/12 オーナー「投稿は関西と関東は基本おなじ」「PR投稿はおかいもののHPの写真がある」「写真も効果ありならちょこちょこ入れる」）。
// 公開する前の site/ をスマホ幅で撮り、縦4:横5（1080×1350）の1枚にして site/postimg/<名前>.jpg に置く（HPと一緒に公開される。リポジトリには入れない）。
// 一覧は data/postimg.json（page.yml が保存する）。book.py は、投稿の中のHPのページと同じ行の url を、1本目の画像に付ける。
// 作りは月（関西）の tools/post_img/make.js と同じ。使い方：node scripts/post_img.js [名前の先頭で絞る]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');const http=require('http');const crypto=require('crypto');
const ROOT=path.join(__dirname,'..');const SITE=path.join(ROOT,'site');const OUT=path.join(SITE,'postimg');
const HOST=(process.env.LIFE_BASE||'https://lifenote-kanto.pages.dev').replace(/\/$/,'');const BASE=HOST+'/postimg/';
const only=process.argv[2]||'';
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.webp':'image/webp','.webmanifest':'application/json'};
const srv=http.createServer((q,s)=>{let u=decodeURIComponent(q.url.split('?')[0]);if(u.endsWith('/'))u+='index.html';let f=path.join(SITE,u);
 if(!fs.existsSync(f)||fs.statSync(f).isDirectory()){if(fs.existsSync(f+'.html'))f+='.html';else if(fs.existsSync(path.join(f,'index.html')))f=path.join(f,'index.html');else{s.writeHead(404);return s.end()}}
 s.writeHead(200,{'content-type':MIME[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(s)});
// 撮る物：おかいもの（種類ごと）・ふるさと納税・値下がり・おでかけ（都県ごと・紅葉・イルミ・初詣・1件ずつ）・解体の費用
function targets(){const T=[];const L=fs.readdirSync(SITE);
 const add=(re,label)=>{for(const f of L)if(re.test(f)){const c=f.slice(0,-5);T.push({name:c,page:'/'+c,label})}};
 add(/^okaimono(-[a-z0-9]+)?\.html$/,'くらべたおかいものリスト');add(/^furusato(-[a-z0-9]+)?\.html$/,'ふるさと納税を1万円あたりでくらべた');add(/^nesage\.html$/,'本当に値下がりした物');
 add(/^odekake(-[a-z]+)?\.html$/,'関東おでかけリスト');add(/^(koyo|illumination|illumi|hatsumode|tomari)\.html$/,'関東おでかけリスト');add(/^kaitai(-[a-z]+)?\.html$/,'解体・片付けの費用の目安');
 const O=path.join(SITE,'o');if(fs.existsSync(O))for(const f of fs.readdirSync(O))if(/^[0-9a-f]{8}\.html$/.test(f)){const c=f.slice(0,-5);T.push({name:'o-'+c,page:'/o/'+c,label:'関東おでかけリスト'})}
 return T.filter(t=>t.name.startsWith(only))}
const CARD=`<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500&family=Shippori+Mincho:wght@600&family=Zen+Kaku+Gothic+New:wght@500&display=swap" rel="stylesheet">
<style>*{margin:0;box-sizing:border-box}body{width:1080px;height:1350px;background:#F6F3EE;position:relative;overflow:hidden;font-family:"Zen Kaku Gothic New",sans-serif;color:#3A332E}
.fr{position:absolute;inset:26px;border:1px solid #CDBFAF}
.hd{position:absolute;left:70px;right:70px;top:62px;display:flex;justify-content:space-between;align-items:baseline}
.hd b{font:600 40px "Shippori Mincho",serif;letter-spacing:.06em}.hd b.s{font-size:31px}.hd i{font:500 22px Jost,sans-serif;letter-spacing:.3em;color:#B08A6E;font-style:normal;white-space:nowrap}
.ph{position:absolute;left:150px;top:150px;width:780px;height:1070px;border-radius:38px;overflow:hidden;background:#fff;box-shadow:0 24px 60px rgba(90,70,50,.18),0 0 0 1px #E4DACD}
.ph img{width:780px;display:block}.ph:after{content:"";position:absolute;left:0;right:0;bottom:0;height:150px;background:linear-gradient(rgba(255,255,255,0),#fff)}
.ft{position:absolute;left:0;right:0;bottom:58px;text-align:center;font-size:26px;letter-spacing:.1em;color:#6B5F55}</style>
<div class="fr"></div><div class="hd"><b id="lb"></b><i>LIFE NOTE</i></div><div class="ph"><img id="im"></div><div class="ft" id="ft"></div>`;
(async()=>{fs.mkdirSync(OUT,{recursive:true});const idx={};
 await new Promise(r=>srv.listen(0,r));const port=srv.address().port;const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,timezoneId:'Asia/Tokyo',colorScheme:'light'});const p=await ctx.newPage();
 const d=new Date(Date.now()+9*3600e3);const today=d.toISOString().slice(0,10);
 await p.clock.setFixedTime(new Date(today+'T03:00:00Z')); // 昼の見た目で撮る（夜は色が変わる）
 const c=await b.newPage({viewport:{width:1080,height:1350}});await c.setContent(CARD,{waitUntil:'networkidle'});await c.evaluate(()=>document.fonts.ready);
 await p.route('**/*',r=>{const u=r.request().url();(u.startsWith('http://127.0.0.1')||u.includes('fonts.g'))?r.continue():r.abort()}); // 数える合図・外の絵は呼ばない
 let made=0,fail=[];const T=targets();
 const t0=Date.now();const LIMIT=(+process.env.POSTIMG_SEC||420)*1000; // 時間の上限（おかいもの→おでかけの順に撮り、時間が来たら残りは次の回）
 for(const t of T){if(Date.now()-t0>LIMIT){fail.push('時間切れ '+t.name+' から先');break}
  try{await p.goto(`http://127.0.0.1:${port}${t.page}`,{waitUntil:'load',timeout:20000});await p.waitForTimeout(120);
   await p.evaluate(()=>{for(const e of document.querySelectorAll('*')){const s=getComputedStyle(e);if((s.position==='fixed'||s.position==='sticky')&&e.tagName!=='BODY')e.style.display='none'}});
   await p.addStyleTag({content:'*{opacity:1!important;transition:none!important;animation:none!important}.tk-v{transform:none!important}'});
   await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(80);
   // 撮る所：ページに data-shot があればそこ、無ければ h1 の少し上から
   const y=await p.evaluate(()=>{const e=document.querySelector('[data-shot]')||document.querySelector('h1');if(!e)return 0;return Math.max(0,e.getBoundingClientRect().top+scrollY-(e.hasAttribute('data-shot')?8:70))});
   const txt=await p.evaluate(()=>document.body.innerText.slice(0,3000));const h=crypto.createHash('sha1').update(txt).digest('hex').slice(0,10);
   const shot=await p.screenshot({clip:{x:0,y:y,width:390,height:560},fullPage:true,type:'png'});
   if(process.env.DBG)fs.writeFileSync(path.join(process.env.DBG,'shot-'+t.name+'.png'),shot);
   await c.evaluate(async([img,label,ft])=>{const l=document.getElementById('lb');l.textContent=label;l.className=label.length>14?'s':'';document.getElementById('ft').textContent=ft;const i=document.getElementById('im');i.src=img;await i.decode()},
     ['data:image/png;base64,'+shot.toString('base64'),t.label,'つづきは '+HOST.replace('https://','')+(t.page.startsWith('/o/')?'':t.page)]);
   await c.screenshot({path:path.join(OUT,t.name+'.jpg'),type:'jpeg',quality:86});
   idx[t.page]={url:BASE+t.name+'.jpg?v='+h,label:t.label};made++}catch(e){fail.push(t.name+' '+String(e).slice(0,80))}}
 const out={about:'投稿に付ける画像。投稿の中のHPのページ（/okaimono-tp 等）と同じ行の url を、1本目の画像に付ける。scripts/post_img.js が公開のたびに作る',updated:today,items:idx};
 fs.writeFileSync(path.join(OUT,'index.json'),JSON.stringify(out));
 if(!only&&made>=10)fs.writeFileSync(path.join(ROOT,'data','postimg.json'),JSON.stringify(out,null,1));
 console.log(`作った ${made}・失敗 ${fail.length}`);fail.forEach(f=>console.log(' ×',f));await b.close();srv.close()})();
