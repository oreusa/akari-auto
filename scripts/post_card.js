// 投稿の表紙の絵（11/13 オーナー「せっかくHPもお洒落なのに宣伝写真これじゃなぁ」「TLに流れてきただけ」）。
// HPと同じ作り（淡い丸・明朝の見出し・字間の広い英字・小さいロゴ・細字の大きい数字・白い角丸の表）で、ひと目でうちと分かる1枚にする。
// 使い方：node scripts/post_card.js <spec.json>   spec＝[{name, en, head, big, unit, cap, rows:[[番号or"", 名前, 値], …]}]（1件でも配列）
//   head は <br> と <em>…</em> だけ使える（ほかの記号はそのまま文字になる）。big は数字や日付（例 "+757"・"11.19"）、unit は小さく付ける字（"人"・"木"）。
//   出来上がり：OUT_DIR/card-<name>.jpg と OUT_DIR/cards.json（url を投稿の image_url に使う）。
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const CFG=require('./post_card_config.js');
const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const head=s=>esc(s).replace(/&lt;br&gt;/g,'<br>').replace(/&lt;em&gt;/g,'<em>').replace(/&lt;\/em&gt;/g,'</em>');
const logo='data:image/png;base64,'+fs.readFileSync(CFG.logo).toString('base64');
const HTML=x=>`<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Jost:wght@200;300;400;500&family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500&display=swap" rel="stylesheet">
<style>*{margin:0;box-sizing:border-box}body{width:1080px;height:1350px;background:#F7F4EF;position:relative;overflow:hidden;font-family:"Zen Kaku Gothic New",sans-serif;color:#3A332E}
.c{position:absolute;border-radius:50%;filter:blur(2px)}.c1{width:520px;height:520px;left:-200px;top:-160px;background:#EFD6C3}.c2{width:440px;height:440px;right:-170px;top:60px;background:#D2DFEB}.c3{width:420px;height:420px;right:-60px;bottom:-200px;background:#D8E4D0}
.lg{position:absolute;left:0;right:0;top:78px;text-align:center}.lg img{width:118px;height:118px;object-fit:contain}
.en{position:absolute;left:0;right:0;top:222px;text-align:center;font:400 25px Jost;letter-spacing:.42em;color:#9C7E66}
.hd{position:absolute;left:60px;right:60px;top:300px;text-align:center;font:600 ${x.hs||74}px/1.62 "Shippori Mincho",serif;letter-spacing:.14em}.hd em{font-style:normal;color:#8A6248}
.ln{position:absolute;left:470px;width:140px;top:600px;border-top:1px solid #CDBFAF}
.big{position:absolute;left:0;right:0;top:640px;text-align:center;font:300 ${x.bs||200}px/1 Jost;letter-spacing:.02em}.big small{font:500 40px "Shippori Mincho",serif;letter-spacing:.14em;margin-left:12px;color:#6B5F55}
.cap{position:absolute;left:0;right:0;top:858px;text-align:center;font:400 27px "Zen Kaku Gothic New";letter-spacing:.16em;color:#8A7D72}
.cd{position:absolute;left:140px;right:140px;top:930px;background:rgba(255,255,255,.82);border-radius:28px;padding:34px 52px;box-shadow:0 0 0 1px #E8DFD3}
.r{display:flex;align-items:baseline;font:500 36px/1.9 "Zen Kaku Gothic New";letter-spacing:.08em}.r i{font:300 30px Jost;font-style:normal;color:#9C7E66;width:74px;letter-spacing:.1em}.r span{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.r b{font:400 36px Jost;letter-spacing:.04em;margin-left:16px;white-space:nowrap}
.ft{position:absolute;left:0;right:0;bottom:56px;text-align:center;font:500 24px Jost;letter-spacing:.5em;color:#B08A6E}</style>
<body><div class="c c1"></div><div class="c c2"></div><div class="c c3"></div><div class="lg"><img src="${logo}"></div><div class="en">${esc(x.en)}</div>
<div class="hd">${head(x.head)}</div><div class="ln"></div>${x.big?`<div class="big">${esc(x.big)}${x.unit?`<small>${esc(x.unit)}</small>`:''}</div>`:''}
${x.cap?`<div class="cap">${esc(x.cap)}</div>`:''}${(x.rows||[]).length?`<div class="cd">${x.rows.slice(0,3).map(r=>`<div class="r">${r[0]?`<i>${esc(r[0])}</i>`:''}<span>${esc(r[1])}</span><b>${esc(r[2])}</b></div>`).join('')}</div>`:''}
<div class="ft">${esc(CFG.brand)}</div></body>`;
(async()=>{const specs=[].concat(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));fs.mkdirSync(CFG.out,{recursive:true});
 const idxf=path.join(CFG.out,'cards.json');let idx={};try{idx=JSON.parse(fs.readFileSync(idxf,'utf8')).items||{}}catch(e){}
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});let n=0;
 for(const x of specs){if(!/^[a-z0-9-]+$/.test(x.name||'')){console.log('× name は英小文字・数字・- だけ：',x.name);process.exitCode=1;continue}
  await p.setContent(HTML(x),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
  // 見出しが3行を越える・はみ出す時は止める（読めない絵を出さない）
  const over=await p.evaluate(()=>{const h=document.querySelector('.hd');return h.getBoundingClientRect().bottom>590});
  if(over){console.log('× 見出しが長すぎる（3行まで・1行9字くらい）：',x.name);process.exitCode=1;continue}
  const f='card-'+x.name+'.jpg';await p.screenshot({path:path.join(CFG.out,f),type:'jpeg',quality:90});
  idx['card-'+x.name]={url:CFG.base+f+'?v='+Date.now().toString(36),made:new Date(Date.now()+9*3600e3).toISOString().slice(0,10)};n++}
 fs.writeFileSync(idxf,JSON.stringify({about:'投稿の表紙の絵（card.js が作る）。投稿の image_url に url を使う',items:idx},null,1));
 console.log('作った '+n+' 枚');await b.close()})();
