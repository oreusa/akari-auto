// 投稿の表紙の絵・HPの新しい見た目（?look=f：上に琥珀・青緑・桃・空色・橙の光の帯、白に近い地にガラスのカード、夜は星空）に合わせた版。
// 11/20 owner「投稿の画像もね」（HPの光と動きの見た目に「極めて欲しい」）。今の card.js・photo.js と同じ spec で動く見本。
// 関東版（usagi tools/post_img/glass.js と同じ作り。直す時は両方）。使い方：node scripts/post_glass.js <spec.json>
//   spec＝[{name, night?, pill, en, head, big, unit, cap, rows:[[番号, 名前, 値]…], photo?:{im, cr, pos}}]
//   head は <br> と <em>…</em> だけ（em は光の色の字）。night:true で夜（21時の枠）＝紺の地に星と淡い光。
//   photo があると写真をガラスの枠に入れて、数字のカードを重ねる（クレジット「写真：cr」は必ず出す）。
//   出来上がり：OUT_DIR（無ければ site/card）/card-<name>.jpg。見出しや表がはみ出す時は作らない（× を出す）。
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const CFG=require('./post_card_config.js');const R=path.join(__dirname,'..');
const OUT=process.env.OUT_DIR||CFG.out;
const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
// 見出しは <br> ごとに1行（行の途中で折り返さない。入らなければ字を小さくするか、作らない）
const head=s=>esc(s).split('&lt;br&gt;').map(l=>`<span class="ln">${l.replace(/&lt;em&gt;/g,'<em>').replace(/&lt;\/em&gt;/g,'</em>')}</span>`).join('');
const logo='data:image/png;base64,'+fs.readFileSync(CFG.logo).toString('base64');
const img=p=>{const f=path.isAbsolute(p)?p:path.join(R,p);const e=path.extname(f).slice(1).replace('jpg','jpeg');return `data:image/${e};base64,`+fs.readFileSync(f).toString('base64')};
// 星（夜だけ）：毎回同じ並びになるよう名前から決める
const stars=(seed)=>{let s=0;for(const c of seed)s=(s*31+c.charCodeAt(0))>>>0;const r=()=>(s=(s*1103515245+12345)>>>0)/4294967296;let o='';
  for(let i=0;i<120;i++){const x=r()*1080,y=r()*1350,z=r()<.08?2.6:r()<.3?1.7:1.1,a=.25+r()*.7;o+=`<b style="left:${x.toFixed(0)}px;top:${y.toFixed(0)}px;width:${z}px;height:${z}px;opacity:${a.toFixed(2)}"></b>`}return o};
const HTML=x=>{const N=!!x.night,P=x.photo;return `<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Noto+Sans+JP:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>*{margin:0;box-sizing:border-box}
body{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:"Noto Sans JP",sans-serif;-webkit-font-smoothing:antialiased;
 background:${N?'#070A14':'#F8F8FA'};color:${N?'#F5F5F7':'#1D1D1F'}}
.hero{position:absolute;left:0;right:0;top:0;height:${P||!N?1350:860}px;overflow:hidden;${P||!N?'':'clip-path:polygon(0 0,100% 0,100% 80%,0 100%);'}background:${N?'#120E1C':'transparent'}}
.hero i{position:absolute;border-radius:50%;filter:blur(${N?90:110}px);opacity:${N?.42:.32}}
.hero i:nth-child(1){width:900px;height:900px;left:-300px;top:-380px;background:#FFB65C}
.hero i:nth-child(2){width:820px;height:820px;right:-360px;top:-220px;background:#2EC4B6}
.hero i:nth-child(3){width:700px;height:700px;left:220px;top:120px;background:#F6A6C8;${N?'':'opacity:.12'}}
.hero i:nth-child(4){width:600px;height:600px;right:-120px;top:330px;background:#6FB7F0;opacity:${N?.36:.14}}
.hero i:nth-child(5){width:700px;height:700px;left:-260px;top:380px;background:#FF8A5B;opacity:${N?.34:0}}
.hero::after{content:"";position:absolute;inset:0;background:${N?'linear-gradient(180deg,rgba(7,10,20,.35),rgba(7,10,20,.15) 50%,rgba(7,10,20,.85))':'linear-gradient(180deg,rgba(255,255,255,.18),rgba(255,255,255,0) 45%)'}}
.st{position:absolute;inset:0}.st b{position:absolute;border-radius:50%;background:#fff;box-shadow:0 0 6px rgba(255,255,255,.8)}
.top{position:absolute;left:72px;right:72px;top:68px;display:flex;align-items:center;gap:18px}
.top img{width:64px;height:64px;border-radius:50%;background:rgba(255,255,255,.75);padding:6px;object-fit:contain}
.top .br{font:600 22px Inter;letter-spacing:.22em;color:${N||P?'rgba(245,245,247,.85)':'rgba(29,29,31,.78)'}}
.top .pl{margin-left:auto;font:500 26px "Noto Sans JP";padding:12px 26px;border-radius:999px;background:${N?'rgba(255,255,255,.12)':'rgba(255,255,255,.55)'};
 border:1px solid ${N?'rgba(255,255,255,.18)':'rgba(255,255,255,.8)'};backdrop-filter:blur(14px);color:${N?'#F5F5F7':'#1D1D1F'}}
.en{position:absolute;left:72px;top:${P?190:196}px;font:500 24px Inter;letter-spacing:.32em;color:${N||P?'rgba(245,245,247,.7)':'rgba(29,29,31,.6)'}}
.hd{position:absolute;left:68px;right:68px;top:${P?236:246}px;font:800 ${x.hs||92}px/1.22 "Noto Sans JP";letter-spacing:-.01em;${P?'color:#fff;text-shadow:0 2px 24px rgba(0,0,0,.35)':''}}
.hd .ln{display:block;white-space:nowrap;overflow:hidden}
.hd em{font-style:normal;padding:0 .04em;background:linear-gradient(90deg,rgba(255,255,255,.0),rgba(255,255,255,.0)),linear-gradient(90deg,rgba(255,182,92,.55),rgba(46,196,182,.45));background-size:100% 100%,100% 24%;background-position:0 0,0 88%;background-repeat:no-repeat;-webkit-box-decoration-break:clone;box-decoration-break:clone}
${N||P?'.hd em{background-image:linear-gradient(90deg,rgba(255,182,92,.0),rgba(255,182,92,.0)),linear-gradient(90deg,#FF8A5B,#FFB65C 50%,#2EC4B6);opacity:1}':''}
.ph{position:absolute;left:0;right:0;top:0;height:1350px}.ph img{width:100%;height:100%;object-fit:cover;object-position:${P&&P.pos||'50% 50%'}}
.ph::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,12,20,.88),rgba(10,12,20,.55) 24%,rgba(10,12,20,.1) 42%,rgba(10,12,20,0) 55%,rgba(10,12,20,.55))}
.gl{position:absolute;left:56px;right:56px;bottom:${P?118:96}px;border-radius:44px;padding:44px 52px 40px;
 background:${N?'rgba(22,28,44,.62)':P?'rgba(255,255,255,.72)':'rgba(255,255,255,.82)'};border:1px solid ${N?'rgba(255,255,255,.12)':'rgba(255,255,255,.9)'};
 backdrop-filter:blur(26px) saturate(1.4);box-shadow:0 1px 2px rgba(0,0,0,.04),0 40px 80px -40px rgba(0,0,0,${N?.9:.35})}
.gl::before{content:"";position:absolute;inset:0;border-radius:inherit;padding:2px;background:linear-gradient(120deg,rgba(255,182,92,.9),rgba(246,166,200,.6) 35%,rgba(46,196,182,.85) 70%,rgba(111,183,240,.7));
 -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;opacity:${N||P?.85:.45}}
.big{font:300 168px/1 Inter;letter-spacing:-.04em;font-variant-numeric:tabular-nums;color:${N?'#F5F5F7':'#1D1D1F'}}
.big small{font:500 44px "Noto Sans JP";letter-spacing:0;margin-left:12px;color:${N?'rgba(245,245,247,.7)':'#5E5E5E'}}
.cap{margin-top:14px;font:500 30px/1.45 "Noto Sans JP";color:${N?'rgba(245,245,247,.78)':'#4A4A4F'}}
.rw{margin-top:28px;border-top:1px solid ${N?'rgba(255,255,255,.12)':'rgba(0,0,0,.08)'}}
.r{display:flex;align-items:baseline;gap:22px;padding:18px 0;border-bottom:1px solid ${N?'rgba(255,255,255,.08)':'rgba(0,0,0,.06)'};font:500 34px "Noto Sans JP"}
.r:last-child{border-bottom:0;padding-bottom:0}.r i{font:500 26px Inter;font-style:normal;width:46px;color:${N?'rgba(245,245,247,.5)':'#8A8A8E'}}
.r b{margin-left:auto;font:500 34px Inter;font-variant-numeric:tabular-nums}
.r.hi span,.r.hi b{color:${N?'#7FE3D8':'#0E8F84'}}
.cr{position:absolute;right:64px;bottom:58px;font:400 21px "Noto Sans JP";color:${P||N?'rgba(255,255,255,.75)':'rgba(29,29,31,.5)'}}
.ft{position:absolute;left:72px;bottom:56px;font:500 20px Inter;letter-spacing:.32em;color:${P||N?'rgba(255,255,255,.6)':'rgba(29,29,31,.42)'}}
</style><body>
${P?`<div class="ph"><img src="${img(P.im)}"></div>`:`<div class="hero"><i></i><i></i><i></i><i></i><i></i></div>${N?`<div class="st">${stars(x.name)}</div>`:''}`}
<div class="top"><img src="${logo}"><div class="br">${esc(CFG.name||"KANTO LIFE NOTE")}</div>${x.pill?`<div class="pl">${esc(x.pill)}</div>`:''}</div>
${x.en?`<div class="en">${esc(x.en)}</div>`:''}<div class="hd">${head(x.head)}</div>
<div class="gl">${x.big?`<div class="big">${esc(x.big)}${x.unit?`<small>${esc(x.unit)}</small>`:''}</div>`:''}${x.cap?`<div class="cap">${esc(x.cap)}</div>`:''}
${(x.rows||[]).length?`<div class="rw">${x.rows.slice(0,3).map(r=>`<div class="r${r[3]?' hi':''}"><i>${esc(r[0])}</i><span>${esc(r[1])}</span><b>${esc(r[2])}</b></div>`).join('')}</div>`:''}</div>
${P?`<div class="cr">写真：${esc(P.cr)}</div>`:''}<div class="ft">${esc(CFG.brand||"TOWN NOTE")}</div></body>`};
(async()=>{const specs=[].concat(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));fs.mkdirSync(OUT,{recursive:true});
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});let n=0;
 for(const x of specs){if(!/^[a-z0-9-]+$/.test(x.name||'')){console.log('× name：',x.name);continue}
  if(x.photo&&!x.photo.cr){console.log('× 写真のクレジットが無い：',x.name);continue}
  // 見出しがガラスのカードに重なる・横にはみ出す時は、字を小さくして（92→84→76→68）もう一度。それでも入らなければ作らない
  // （前の道具の hs 50〜66 は明朝の大きさなので、70 より小さい時はこの道具の大きさで始める）
  let bad=true;for(const hs of [x.hs&&x.hs>=70?x.hs:92,84,76,68]){
   await p.setContent(HTML(Object.assign({},x,{hs})),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
   bad=await p.evaluate(()=>{const h=document.querySelector('.hd').getBoundingClientRect(),g=document.querySelector('.gl').getBoundingClientRect();
    const wide=[...document.querySelectorAll('.hd .ln,.r span,.cap')].some(e=>e.scrollWidth>e.clientWidth+2);return h.bottom>g.top-24||g.top<300||wide});
   if(!bad)break}
  if(bad){console.log('× 見出しか表が入らない：',x.name);process.exitCode=1;continue}
  await p.screenshot({path:path.join(OUT,`card-${x.name}.jpg`),type:'jpeg',quality:90});n++
  if(!process.env.OUT_DIR||process.env.OUT_DIR===CFG.out){const f=path.join(OUT,'cards.json');let j={};try{j=JSON.parse(fs.readFileSync(f,'utf8'))}catch(e){}j.items=j.items||{};
   j.items[`card-${x.name}`]={url:CFG.base+`card-${x.name}.jpg?v=`+Date.now().toString(36),made:new Date(Date.now()+9*3600e3).toISOString().slice(0,10)};fs.writeFileSync(f,JSON.stringify(j,null,1))}}
 await b.close();console.log(`作った ${n} 枚`)})();
