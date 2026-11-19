// 関東版（燈）。関西 tools/post_img/photo.js と同じ作り。
// 投稿の写真の表紙（11/19 オーナー「投稿に使う写真も劇的に変えれる」）。HPの激変版（?mihon=2）と同じ写真・同じ作り。
// HP の写真 site/assets/ph/<im>（mihon.json の im・cr）を上に大きく、下に暗い帯と明朝の見出し、大きい日付。写真の人の名前と許可は必ず右上に出す。
// 使い方：node tools/post_img/photo.js <spec.json>   spec＝[{name, im, cr, pos?, zoom?, pill, head, big?, unit?, cap?}]
//   im は site/assets/ph のファイル名か、site/card/ph/<file>（投稿用に集めた写真・credits.json に cr）、cr はクレジットそのまま（mihon.json の cr）。pos は写真の見せる所（CSS object-position。例 "50% 40%"）。
//   pill は左上の札（例 "京都　11/21（土）から"）。head は <br> と <em> だけ。
//   出来上がり：post_card.js と同じ site/card/card-<name>.jpg と cards.json。
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const CFG=require('./post_card_config.js');const PH=path.join(__dirname,'../site/assets/ph');
const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const head=s=>esc(s).replace(/&lt;br&gt;/g,'<br>').replace(/&lt;em&gt;/g,'<em>').replace(/&lt;\/em&gt;/g,'</em>');
const logo='data:image/png;base64,'+fs.readFileSync(CFG.logo).toString('base64');
const R=path.join(__dirname,'..');const fp=f=>f.includes('/')?path.join(R,f):path.join(PH,f);
const img=f=>'data:image/'+(/\.webp$/.test(f)?'webp':'jpeg')+';base64,'+fs.readFileSync(fp(f)).toString('base64');
const HTML=x=>`<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Jost:wght@200;300;400;500&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>*{margin:0;box-sizing:border-box}body{width:1080px;height:1350px;background:#16120F;position:relative;overflow:hidden;font-family:"Zen Kaku Gothic New",sans-serif;color:#fff}
.ph{position:absolute;left:0;top:0;width:1080px;height:1010px;object-fit:cover;object-position:${x.pos||'50% 50%'};transform:scale(${x.zoom||1});transform-origin:${x.pos||'50% 50%'};filter:saturate(1.06) contrast(1.04)}
.sh{position:absolute;left:0;right:0;top:0;height:1350px;background:linear-gradient(180deg,rgba(22,18,15,.35) 0,rgba(22,18,15,0) 170px,rgba(22,18,15,0) 520px,rgba(22,18,15,.72) 820px,#16120F 1010px)}
.vg{position:absolute;inset:0;box-shadow:inset 0 0 220px rgba(0,0,0,.28)}
.lg{position:absolute;left:52px;top:46px;display:flex;align-items:center;gap:16px}.lg i{width:82px;height:82px;border-radius:50%;background:rgba(255,253,249,.94);display:flex;align-items:center;justify-content:center}.lg img{width:66px;height:66px;object-fit:contain;mix-blend-mode:multiply}
.lg b{font:500 23px Jost;letter-spacing:.42em;text-shadow:0 1px 8px rgba(0,0,0,.45)}
.cr{position:absolute;right:44px;top:56px;max-width:520px;text-align:right;font:400 19px "Zen Kaku Gothic New";letter-spacing:.04em;color:rgba(255,255,255,.88);text-shadow:0 1px 6px rgba(0,0,0,.6)}
.bt{position:absolute;left:64px;right:64px;bottom:96px}
.pl{display:inline-flex;align-items:center;gap:14px;background:rgba(255,253,249,.95);color:#3A332E;border-radius:999px;padding:12px 30px 12px 26px;font:700 29px "Zen Kaku Gothic New";letter-spacing:.06em}.pl:before{content:"";width:13px;height:13px;border-radius:50%;background:#C2643E}
.hd{margin-top:30px;font:700 ${x.hs||72}px/1.42 "Shippori Mincho",serif;letter-spacing:.06em;text-shadow:0 2px 18px rgba(0,0,0,.35)}.hd em{font-style:normal;color:#F3C9A4}
.rw{margin-top:30px;display:flex;align-items:baseline;gap:26px;border-top:1px solid rgba(255,255,255,.22);padding-top:26px}
.big{flex:none;white-space:nowrap;font:300 ${x.bs||118}px/1 Jost;letter-spacing:.01em}.big small{font:500 34px "Shippori Mincho",serif;margin-left:10px;color:rgba(255,255,255,.8)}
.cap{flex:1;font:400 27px/1.5 "Zen Kaku Gothic New";letter-spacing:.08em;color:rgba(255,255,255,.82)}
.ft{position:absolute;left:64px;right:64px;bottom:40px;display:flex;justify-content:space-between;font:500 20px Jost;letter-spacing:.42em;color:rgba(255,255,255,.5)}</style>
<body><img class="ph" src="${img(x.im)}"><div class="sh"></div><div class="vg"></div>
<div class="lg"><i><img src="${logo}"></i><b>${esc(CFG.brand)}</b></div><div class="cr">写真：${esc(x.cr)}</div>
<div class="bt">${x.pill?`<div class="pl">${esc(x.pill)}</div>`:''}<div class="hd">${head(x.head)}</div>
${x.big||x.cap?`<div class="rw">${x.big?`<div class="big">${esc(x.big)}${x.unit?`<small>${esc(x.unit)}</small>`:''}</div>`:''}${x.cap?`<div class="cap">${head(x.cap)}</div>`:''}</div>`:''}</div>
<div class="ft"><span>KANTO TOWN NOTE</span><span>${esc(x.en||'')}</span></div></body>`;
(async()=>{const specs=[].concat(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));const out=process.env.OUT_DIR||CFG.out;fs.mkdirSync(out,{recursive:true});
 const idxf=path.join(out,'cards.json');let idx={};try{idx=JSON.parse(fs.readFileSync(idxf,'utf8')).items||{}}catch(e){}
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});let n=0;
 for(const x of specs){if(!/^[a-z0-9-]+$/.test(x.name||'')){console.log('× name：',x.name);process.exitCode=1;continue}
  if(!x.im||!fs.existsSync(fp(x.im))){console.log('× 写真が無い：',x.name,x.im);process.exitCode=1;continue}
  if(!x.cr){console.log('× クレジットが無い（写真は出さない）：',x.name);process.exitCode=1;continue}
  await p.setContent(HTML(x),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
  // 見出しが写真の真ん中まで上がる（4行以上）時は止める
  const over=await p.evaluate(()=>document.querySelector('.bt').getBoundingClientRect().top<640);
  if(over){console.log('× 見出しが長すぎる：',x.name);process.exitCode=1;continue}
  const f='card-'+x.name+'.jpg';await p.screenshot({path:path.join(out,f),type:'jpeg',quality:90});
  idx['card-'+x.name]={url:CFG.base+f+'?v='+Date.now().toString(36),made:new Date(Date.now()+9*3600e3).toISOString().slice(0,10),photo:x.im,cr:x.cr};n++}
 fs.writeFileSync(idxf,JSON.stringify({about:'投稿の表紙の絵（card.js・photo.js が作る）。投稿の image_url に url を使う',items:idx},null,1));
 console.log('作った '+n+' 枚');await b.close()})();
