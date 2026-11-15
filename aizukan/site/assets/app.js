/* AIタイプ図鑑 — 全ページ共通の動き（data.js の後に読む） */
(()=>{
'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const el=(t,a={},...k)=>{const e=document.createElement(t);for(const[n,v]of Object.entries(a)){if(v==null||v===false)continue;if(n==='class')e.className=v;else if(n==='text')e.textContent=v;else if(n==='html')e.innerHTML=v;else if(n.startsWith('on'))e.addEventListener(n.slice(2),v);else e.setAttribute(n,v)}for(const c of k.flat())if(c!=null&&c!==false)e.append(c.nodeType?c:document.createTextNode(String(c)));return e};
const store={get(k,d){try{const v=localStorage.getItem('aiz_'+k);return v?JSON.parse(v):d}catch{return d}},set(k,v){try{localStorage.setItem('aiz_'+k,JSON.stringify(v))}catch{}}};
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
const qt=x=>/^「/.test(x)?'“'+x+'”':'「'+x+'」';
const pad=n=>String(n).padStart(2,'0');
const IMG=(t,k)=>`/img/${pad(t+1)}_${k+1}.webp`;
const campOf=t=>Math.floor(t/3),paceOf=t=>t%3;
const fullName=(t,k)=>KI[k].n+TYPES[t].n;
const isRev=r=>Math.min(Math.abs(r.ma-50),Math.abs(r.mk-50))<8;
const starUrl=t=>`/hoshi/${pad(t+1)}/`;
const PAGE=document.body.dataset.page||'';

/* ===== 共通：星空・ヘッダー・小さな知らせ ===== */
(()=>{const cv=$('#sky');if(!cv)return;const g=cv.getContext('2d');let W,H,S=[];const fit=()=>{const d=Math.min(devicePixelRatio||1,2);W=cv.width=innerWidth*d;H=cv.height=innerHeight*d;S=Array.from({length:Math.min(500,Math.round(innerWidth*innerHeight/3200))},()=>({x:Math.random()*W,y:Math.random()*H,r:(Math.random()*1.05+.2)*d,p:Math.random()*6.3,s:.3+Math.random()*1.1,gold:Math.random()<.1}))};
  fit();addEventListener('resize',fit);
  const draw=t=>{g.clearRect(0,0,W,H);for(const s of S){const a=RM?.6:.3+.4*Math.sin(s.p+t/1000*s.s);g.globalAlpha=Math.max(.05,a);g.fillStyle=s.gold?'#E9C989':'#DDE3FF';g.beginPath();g.arc(s.x,s.y,s.r,0,6.3);g.fill()}if(!RM&&!document.hidden)requestAnimationFrame(draw)};
  requestAnimationFrame(draw);document.addEventListener('visibilitychange',()=>{if(!document.hidden&&!RM)requestAnimationFrame(draw)})})();
(()=>{const h=$('.hdr'),b=$('.menu-btn');if(!h||!b)return;b.addEventListener('click',()=>{const o=h.classList.toggle('open');b.setAttribute('aria-expanded',String(o))});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&h.classList.contains('open')){h.classList.remove('open');b.setAttribute('aria-expanded','false');b.focus()}})})();
function toast(msg){let t=$('#toast');if(!t){t=el('div',{id:'toast',class:'toast',role:'status'});document.body.append(t)}t.textContent=msg;t.classList.add('on');clearTimeout(toast.h);toast.h=setTimeout(()=>t.classList.remove('on'),2200)}
async function copy(text,okMsg='写しました'){try{await navigator.clipboard.writeText(text);toast(okMsg);return true}catch{return false}}

/* ===== カード ===== */
function card(t,k,{size='',rev=false,lazy=true}={}){
  return el('div',{class:`tcard c${campOf(t)}${size?' '+size:''}${rev?' rev':''}`},
    el('img',{src:IMG(t,k),alt:fullName(t,k)+'のカード',loading:lazy?'lazy':'eager',width:640,height:960}),
    el('span',{class:'num',text:ROMAN[t]}),el('span',{class:'nm'},el('small',{text:TYPES[t].star}),el('b',{text:fullName(t,k)})));
}
const back=()=>el('span',{class:'back','aria-hidden':'true'});

/* ===== 呪文 ===== */
const PROMPT=`あなたは、私がふだん使っているAIです。これまでの私とのやり取り（覚えている事・この会話までの様子）をもとに、私の「AIの使い方」と「主（あるじ）としての腕」を正直に評価してください。覚えていない事は、分かる範囲で推測して構いません。

大事な決まり
・遠慮もお世辞も要りません。褒めすぎは禁止です。
・「ふつうの使い手」を3とします。5は、はっきりそう言い切れる時だけにしてください。

【一】次の20の文に、1〜5で答えてください（1＝全く当てはまらない、3＝どちらとも言えない、5＝とても当てはまる）。
${QS.map((q,i)=>`${i+1}. ${q}`).join('\n')}

【二】次の15の文にも、同じく1〜5で答えてください。
${OQS.map((q,i)=>`${i+21}. ${q[0]}`).join('\n')}

【三】下の24の用途から、この人がよく使う順に3つ、番号で選んでください。
${USES.map((u,i)=>`${i+1} ${u}`).join('／')}

【四】下の16の「癖」から、この人に一番当てはまる物を2つ、強い順に番号で選んでください。
${KUSE.map((k,i)=>`${i+1} ${k.p}`).join('／')}

【五】下の12から、この人の頼み方のせいで、あなた（AI）がいつも間違えやすい所を1つ、番号で選んでください。
${MISS.map((m,i)=>`${i+1} ${m.n}`).join('／')}

最後に、次の形だけで答えてください（説明は要りません）。
【AIタイプ図鑑】
AI：（あなたの名前。例 ChatGPT）
記憶：（この人とのやり取りをどのくらい覚えているか。多い／少ない／ない）
答え：（【一】の20個の数字をカンマ区切りで）
主の採点：（【二】の15個の数字をカンマ区切りで）
用途：（【三】の3つの番号を多い順に）
癖：（【四】の2つの番号）
つまずき：（【五】の1つの番号）
口ぐせ：（この人がよく言う言葉。10文字以内）
ひとこと：（AIから見たこの人を、辛口に30文字以内で）
本音：（この人に、一度だけ言いたかった事。30文字以内）
場面：（【四】の癖が出た、実際の場面を1つ。40文字以内。人の名前や連絡先は書かない）`;

/* ===== 読み取りと判定 ===== */
function parse(raw){
  const s=String(raw||'').normalize('NFKC').replace(/[*_`#>|]/g,'');
  const line=k=>{const m=s.match(new RegExp(k+'\\s*[:：]\\s*(.*)'));return m?m[1].trim():''};
  if(!s.trim())return {error:'AIの答えを貼ってください。'};
  let ans=line('答え').match(/[1-5]/g)||[];
  if(ans.length<20){const rows=[...s.matchAll(/^\s*(\d{1,2})[.)．、\s]+.*?([1-5])\s*$/gm)].map(m=>[+m[1],m[2]]).filter(r=>r[0]>=1&&r[0]<=20);if(rows.length>=20){ans=[];rows.forEach(r=>ans[r[0]-1]=r[1])}}
  if(ans.length<20||ans.slice(0,20).some(v=>!v))return {error:'「答え：」の20個の数字が見つかりませんでした。AIの答えを【AIタイプ図鑑】の行から最後まで、まるごと貼ってください。'};
  const u=[...new Set((line('用途').match(/\d{1,2}/g)||[]).map(Number).filter(n=>n>=1&&n<=24))].slice(0,3);
  if(u.length<3)return {error:'「用途：」の番号が3つ見つかりませんでした。AIに「用途の番号を3つ」と頼んで、もう一度貼ってください。'};
  const q=v=>v.replace(/^[「『"“]+|[」』"”]+$/g,'');
  let o=line('主の採点').match(/[1-5]/g)||[];
  if(o.length<15){const rows=[...s.matchAll(/^\s*(\d{2})[.)．、\s]+.*?([1-5])\s*$/gm)].map(m=>[+m[1],m[2]]).filter(r=>r[0]>=21&&r[0]<=35);if(rows.length>=15){o=[];rows.forEach(r=>o[r[0]-21]=r[1])}}
  o=o.length>=15&&!o.slice(0,15).some(v=>!v)?o.slice(0,15).map(Number):null;
  const kz=[...new Set((line('癖').match(/\d{1,2}/g)||[]).map(Number).filter(n=>n>=1&&n<=KUSE.length))].slice(0,2).map(n=>n-1);
  const ms=(line('つまずき').match(/\d{1,2}/)||[])[0];
  const mem=line('記憶');
  return {a:ans.slice(0,20).map(Number),u,ai:line('AI').slice(0,20)||'あなたのAI',kuse:q(line('口ぐせ')).slice(0,20),hito:q(line('ひとこと')).slice(0,50),
    o,kz,ms:ms&&+ms>=1&&+ms<=MISS.length?+ms-1:-1,honne:q(line('本音')).slice(0,50),scene:q(line('場面')).slice(0,70),mem:/少/.test(mem)?1:/ない|無|覚えていない/.test(mem)?2:0};
}
function judge(x){
  const A=x.a,f=i=>A[i-1],r=i=>6-A[i-1],pct=v=>Math.round((v-1)/4*100);
  const ma=pct((f(1)+f(2)+r(3)+r(4)+f(5))/5),mk=pct((f(6)+f(7)+f(10)+r(8)+r(9))/5);
  const sp=[(f(11)+f(12))/2,(f(13)+f(14))/2,(f(15)+f(16))/2];let p=1;[1,2,0].forEach(i=>{if(sp[i]>sp[p])p=i});
  const camp=(ma>=50?0:2)+(mk>=50?0:1);
  const kv=[f(17),(f(11)+f(12))/2,f(18),f(19),f(20)];let k=0;[0,4,1,2,3].forEach(i=>{if(kv[i]>kv[k])k=i});
  return {t:camp*3+p,k,ma,mk,u:x.u,ai:x.ai,kuse:x.kuse||'',hito:x.hito||'',own:x.o?owner(x):null};
}
function rankOf(sc,v){let r=sc>=86?6:sc>=74?5:sc>=62?4:sc>=46?3:sc>=34?2:sc>=22?1:0;if(r===6&&Math.min(...v)<70)r=5;return r}
function ownFrom(lv,kz,ms,mem,self){
  const v=lv.map(l=>Math.round(l*100/12)),sc=Math.round(v.reduce((a,b)=>a+b,0)/5);
  const lo=v.indexOf(Math.min(...v)),hi=v.indexOf(Math.max(...v));
  return {lv,v,sc,rk:rankOf(sc,v),kz,ms:ms>=0?ms:MISS_OF_V[lo],lo,hi,mem,self};
}
function owner(x){
  const O=x.o,A=x.a,val=(q,d)=>{const n=q<=20?A[q-1]:O[q-21];return d?n:6-n};
  const lv=VIRT.map((_,i)=>OQS.map((q,j)=>[q,j]).filter(([q])=>q[1]===i).reduce((s,[q,j])=>s+(q[2]?6-O[j]:O[j]),0)-3);
  const v=lv.map(l=>Math.round(l*100/12)),lo=v.indexOf(Math.min(...v));
  let kz=(x.kz||[]).slice(0,2);
  if(kz.length<2){const cand=KUSE.map((k,i)=>[i,k.q?val(k.q,k.d):0]).filter(c=>!kz.includes(c[0])).sort((a,b)=>b[1]-a[1]);while(kz.length<2)kz.push(cand.shift()[0])}
  const o=ownFrom(lv,kz,x.ms>=0?x.ms:MISS_OF_V[lo],x.mem||0,x.ai==='自分');
  o.honne=x.honne||'';o.scene=x.scene||'';return o;
}

/* ===== 符号（URLに入れる） ===== */
const B=36;
function enc(r){let n=r.t;n=n*5+r.k;n=n*101+r.ma;n=n*101+r.mk;r.u.forEach(x=>n=n*24+(x-1));return 'AI-'+n.toString(B).toUpperCase()}
function dec(code){const m=(code||'').normalize('NFKC').toUpperCase().replace(/\s/g,'').match(/^(?:AI-?)?([0-9A-Z]{4,12})$/);if(!m)return null;let n=parseInt(m[1],B);if(!Number.isSafeInteger(n))return null;const u=[];for(let i=0;i<3;i++){u.unshift(n%24+1);n=Math.floor(n/24)}const mk=n%101;n=Math.floor(n/101);const ma=n%101;n=Math.floor(n/101);const k=n%5;n=Math.floor(n/5);if(n<0||n>11||ma>100||mk>100)return null;return {t:n,k,ma,mk,u}}
function encO(o){let n=0;o.lv.forEach(l=>n=n*13+l);n=n*256+o.kz[0]*16+o.kz[1];n=n*12+o.ms;n=n*3+(o.mem||0);n=n*2+(o.self?1:0);return n.toString(B).toUpperCase()}
function decO(s){if(!s||!/^[0-9A-Z]{1,8}$/i.test(s))return null;let n=parseInt(s,B);if(!Number.isSafeInteger(n))return null;const self=n%2===1;n=Math.floor(n/2);const mem=n%3;n=Math.floor(n/3);const ms=n%12;n=Math.floor(n/12);const kz=[Math.floor((n%256)/16),n%16];n=Math.floor(n/256);const lv=[];for(let i=0;i<5;i++){lv.unshift(n%13);n=Math.floor(n/13)}if(n!==0||kz[0]===kz[1])return null;return ownFrom(lv,kz,ms,mem,self)}
const resultUrl=r=>'/kekka/?c='+encodeURIComponent(enc(r))+(r.own?'&o='+encO(r.own):'');
const shareUrl=r=>location.origin+`/s/${pad(r.t+1)}-${r.k+1}/?c=`+encodeURIComponent(enc(r))+(r.own?'&o='+encO(r.own):'');

/* ===== 縁 ===== */
const diag=c=>3-c,flipAsk=c=>(c+2)%4;
function pals(t){const c=campOf(t),p=paceOf(t);return {best:diag(c)*3+p,learn:c*3+[2,0,1][p],clash:flipAsk(c)*3+[2,0,0][p]}}
function relation(a,b){
  const ca=campOf(a),cb=campOf(b),pa=paceOf(a),pb=paceOf(b),N=t=>TYPES[t].n;
  if(a===b)return ['双星','同じ星の下に生まれた二人。言葉にしなくても通じる。ただ、同じ場所で一緒につまずく。片方が「ほかの道は？」と言う役を引き受けると、二人は無敵になります。'];
  if(ca===cb)return ['師と弟子',`同じ宮に住み、歩く速さだけが違う二人。${N(pa===2?a:b)}の深さと、${N(pa===2?b:a)}の${PACE[pa===2?pb:pa]}を交換すると、互いの星がもう一段明るくなります。`];
  if(cb===diag(ca)&&pa===pb)return ['運命の対','頼み方も使い道も正反対で、歩く速さだけが同じ。欠けた所を、相手がそのまま持っている。六十枚の中でも、めったに出会えない組み合わせです。'];
  const s=new Set([pa,pb]);
  if((s.has(0)&&s.has(2))||(s.has(0)&&s.has(1)&&(ca<2)!==(cb<2)))return ['相剋','進む速さが合わず、ぶつかりやすい二人。けれど、ぶつかる所にこそ火花が散る。先に「今日はどこまで」を決めてから並んで歩くと、争いは力に変わります。'];
  if(pa===pb)return ['同じ歩幅',`歩く速さが同じ${PACE[pa]}の二人。見ている景色が違うので、話すほど互いの世界が広がります。`];
  return ['月と潮','近すぎず、遠すぎず。片方が満ちる時、もう片方が引く。困った夜に、違う角度の光をくれる相手です。'];
}

/* ===== 今日の託宣 ===== */
function today(){return new Date(Date.now()+9*3600e3).toISOString().slice(0,10)}
function hash(s){let h=2166136261;for(const ch of s){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0}
function oracle(r){const d=today(),h=hash(d+'|'+r.t+'|'+r.k);return {d,text:ORACLE[h%ORACLE.length],use:USES[(h>>>8)%24],num:(h>>>16)%9+1}}

/* ===== みんなの数（サーバー） ===== */
let STATS=null;const statsWait=[];
function onStats(fn){if(STATS)fn(STATS);else statsWait.push(fn)}
fetch('/api/stats',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(j=>{if(j&&typeof j.n==='number'){STATS=j;statsWait.splice(0).forEach(f=>{try{f(j)}catch{}});$$('[data-count]').forEach(e=>e.textContent=j.n.toLocaleString())}}).catch(()=>{});
const AI_NAME=a=>{const x=String(a||'').toLowerCase();return /chat ?gpt|gpt|openai/.test(x)?'ChatGPT':/claude/.test(x)?'Claude':/gemini|bard/.test(x)?'Gemini':/copilot/.test(x)?'Copilot':/perplexity/.test(x)?'Perplexity':/grok/.test(x)?'Grok':'その他'};
function sendHit(r){
  const d=today(),h=store.get('hit',{d:'',n:0});if(h.d===d&&h.n>=3)return;store.set('hit',{d,n:h.d===d?h.n+1:1});
  const body=JSON.stringify({t:r.t,k:r.k,rk:r.own&&!r.own.self?r.own.rk:-1,o:r.own&&!r.own.self?r.own.sc:-1,ai:r.own?.self?'自分':AI_NAME(r.ai)});
  try{fetch('/api/hit',{method:'POST',headers:{'content-type':'application/json'},body,keepalive:true}).catch(()=>{})}catch{}
}
function rankPct(sc){if(!STATS||!Array.isArray(STATS.hist))return null;const tot=STATS.hist.reduce((a,b)=>a+b,0);if(tot<20)return null;const above=STATS.hist.slice(sc+1).reduce((a,b)=>a+b,0);return Math.max(1,Math.ceil((above+1)/tot*100))}

/* ===== 出会ったカード ===== */
const metSet=()=>new Set(store.get('met',[]));
function meet(t,k){const s=metSet();s.add(t*5+k);store.set('met',[...s])}

/* ===== 部品 ===== */
function penta(v){
  const C=150,R=92,pt=(i,r)=>{const a=-Math.PI/2+i*2*Math.PI/5;return[(C+r*Math.cos(a)).toFixed(1),(C+r*Math.sin(a)).toFixed(1)]};
  const ring=f=>[0,1,2,3,4].map(i=>pt(i,R*f).join(',')).join(' ');
  const star=[0,2,4,1,3].map(i=>pt(i,R).join(',')).join(' ');
  const shape=v.map((x,i)=>pt(i,R*Math.max(.06,x/100)).join(',')).join(' ');
  const lab=VIRT.map((V,i)=>{const[x,y]=pt(i,R+30);return `<text x="${x}" y="${+y+2}" text-anchor="middle" font-size="18" fill="#F0DCAA" font-family="Shippori Mincho B1,serif" font-weight="700">${V.k}</text><text x="${x}" y="${+y+21}" text-anchor="middle" font-size="13" fill="#9C96B0" font-family="Cinzel,serif">${v[i]}</text>`}).join('');
  const d=el('div');d.innerHTML=`<svg class="penta" viewBox="0 0 300 300" role="img" aria-label="五つの徳 ${VIRT.map((V,i)=>V.n+' '+v[i]).join('、')}"><polygon points="${ring(1)}" fill="none" stroke="#8A6F3E" stroke-width="1"/><polygon points="${ring(.66)}" fill="none" stroke="#33344F" stroke-width="1"/><polygon points="${ring(.33)}" fill="none" stroke="#33344F" stroke-width="1"/><polygon points="${star}" fill="none" stroke="#8A6F3E77" stroke-width="1"/><polygon points="${shape}" fill="#D6B06833" stroke="#F0DCAA" stroke-width="2" stroke-linejoin="round"/>${v.map((x,i)=>{const[a,b]=pt(i,R*Math.max(.06,x/100));return `<circle cx="${a}" cy="${b}" r="3.5" fill="#F0DCAA"/>`}).join('')}${lab}</svg>`;
  return d.firstChild;
}
const seal=(rk,size='')=>el('div',{class:`seal${size?' '+size:''} r${rk}`,'aria-hidden':'true'},el('span',{class:'ring'}),el('b',{text:RANKS[rk].r}));
const fixBox=(label,text)=>el('div',{class:'fix'},el('div',{class:'fix-t'},el('small',{text:label}),el('p',{text:'「'+text+'」'})),el('button',{class:'btn dark sm',type:'button',onclick:()=>copy(text,'一文を写しました')},'写す'));
const block=(eyebrow,title,...kids)=>el('section',{class:'rblock'},el('header',{class:'rb-h'},el('span',{class:'eyebrow',text:eyebrow}),title?el('h2',{text:title}):null),...kids);
const pair=(a,b,la,lb)=>el('div',{class:'pair'},el('div',{},el('small',{text:la}),el('p',{text:a})),el('div',{},el('small',{text:lb}),el('p',{text:b})));

/* ===== カードを引く儀式 ===== */
function ritual(r,done){
  const T=TYPES[r.t],rev=isRev(r);
  const say=el('p',{class:'r-say',role:'status'},el('small',{text:'水鏡の案内人'}),el('span',{text:'あなたのAIの言葉を、たしかに受け取りました。'}));
  const fan=el('div',{class:'r-fan'});const ang=[-24,-12,0,12,24];
  const btns=ang.map((a,i)=>{const b=el('button',{type:'button','aria-label':`${i+1}枚目のカードを引く`,style:`transform:rotate(${a}deg) translateY(${Math.abs(a)/2.4}px);z-index:${5-Math.abs(i-2)}`},back());fan.append(b);return b});
  const tap=el('p',{class:'r-tap',text:'もう一度ふれると、結果へ進みます'});
  const skip=el('button',{class:'r-skip',type:'button'},'とばす');
  const ov=el('div',{class:'ritual',role:'dialog','aria-modal':'true','aria-label':'カードを引く'},el('div',{class:'r-in'},say,fan,tap),skip);
  document.body.append(ov);document.body.style.overflow='hidden';
  const txt=say.lastChild;const tm=[];
  tm.push(setTimeout(()=>{txt.textContent='五枚のカードを伏せました。'},RM?0:1300));
  tm.push(setTimeout(()=>{txt.textContent='あなたの指が選ぶ一枚が、あなたの星です。';tap.textContent='気になる一枚に、ふれてください';tap.classList.add('on')},RM?0:2600));
  let picked=false;
  btns.forEach((b,i)=>b.addEventListener('click',()=>{
    if(picked)return;picked=true;tm.forEach(clearTimeout);tap.classList.remove('on');tap.textContent='もう一度ふれると、結果へ進みます';
    btns.forEach((x,j)=>{if(j!==i)x.classList.add('gone')});
    b.style.transform='rotate(0deg) translateY(-24px) scale(1.06)';
    setTimeout(()=>{
      fan.replaceWith(el('div',{class:'r-big'},el('div',{class:'r-flip'},back(),el('div',{class:'r-front'},card(r.t,r.k,{rev,lazy:false})))));
      txt.textContent=rev?'……カードが、逆さに現れました。':`${HOUSES[campOf(r.t)].n}、${ROMAN[r.t]}。${T.star}。`;
      requestAnimationFrame(()=>requestAnimationFrame(()=>ov.querySelector('.r-flip').classList.add('open')));
      setTimeout(()=>{txt.textContent=`あなたは「${fullName(r.t,r.k)}」。`+(r.own?`主の位は「${RANKS[r.own.rk].n}」。`:'');tap.classList.add('on');ov.addEventListener('click',fin,{once:true})},RM?100:1700);
    },RM?50:650);
  }));
  skip.addEventListener('click',e=>{e.stopPropagation();fin()});
  let ended=false;function fin(){if(ended)return;ended=true;tm.forEach(clearTimeout);ov.remove();document.body.style.overflow='';done()}
  btns[2].focus();
}

/* ===== 結果を記録して結果ページへ ===== */
function commit(r){
  const pv=store.get('last',null);
  if(r.own&&pv?.own&&typeof pv.own.rk==='number')r.prev=pv.own.rk;
  r.code=enc(r);r.at=Date.now();
  store.set('last',r);
  const hist=store.get('hist',[]);hist.unshift({c:r.code,o:r.own?encO(r.own):'',t:r.t,k:r.k,rk:r.own?r.own.rk:-1,sc:r.own?r.own.sc:-1,ai:r.ai,hito:r.hito||'',honne:r.own?.honne||'',at:r.at});store.set('hist',hist.slice(0,20));
  meet(r.t,r.k);sendHit(r);
  location.href=resultUrl(r)+'&new=1';
}

/* ======================================================================
   ページごと
   ====================================================================== */
const PAGES={};

/* ----- 入口 ----- */
PAGES.home=()=>{
  const l=store.get('last',null),box=$('#again');
  if(box&&l&&typeof l.t==='number'){box.hidden=false;box.replaceChildren(el('a',{class:'again',href:resultUrl(l)},el('img',{src:IMG(l.t,l.k),alt:'',width:40,height:60}),el('span',{},el('small',{text:'前回のあなたのカード'}),el('b',{text:fullName(l.t,l.k)+(l.own?'　'+RANKS[l.own.rk].r+' '+RANKS[l.own.rk].n:'')})),el('em',{text:'結果を見る →'})))}
};

/* ----- 占う（呪文） ----- */
PAGES.uranai=()=>{
  const pre=$('#promptText');pre.textContent=PROMPT;
  $('#promptChars').textContent=PROMPT.length.toLocaleString();
  const step=n=>$$('.step').forEach((s,i)=>{s.classList.toggle('done',i<n);s.classList.toggle('now',i===n)});
  $('#copyPrompt').addEventListener('click',async()=>{
    if(await copy(PROMPT,'呪文を写しました')){$('#copyOk').hidden=false;step(1)}
    else{pre.closest('details').open=true;const rg=document.createRange();rg.selectNodeContents(pre);const s=getSelection();s.removeAllRanges();s.addRange(rg);$('#copyNg').hidden=false}
  });
  const ta=$('#answer'),err=$('#err');
  ta.addEventListener('input',()=>{if(ta.value.trim())step(2)});
  $('#judge').addEventListener('click',()=>{
    const x=parse(ta.value);
    if(x.error){err.hidden=false;err.textContent=x.error;ta.focus();return}
    err.hidden=true;const r=judge(x);r.hito=x.hito;r.kuse=x.kuse;
    ritual(r,()=>commit(r));
  });
};

/* ----- 自分で答える ----- */
PAGES.jibun=()=>{
  const ALLQ=[...QS,...OQS.map(q=>q[0])];
  const MYQS=ALLQ.map(q=>q.replace(/^この人は、/,'').replace(/^この人の/,'').replace(/^この人とのやり取りは/,'AIとのやり取りは').replace(/私の答え/g,'AIの答え').replace(/私に/g,'AIに').replace(/私を/g,'AIを'));
  const N=36,saved=store.get('jibun',null);
  const man=Array.isArray(saved?.m)&&saved.m.length===35?saved.m:Array(35).fill(0);let picks=Array.isArray(saved?.p)?saved.p:[];
  let qi=man.findIndex(v=>!v);if(qi<0)qi=35;
  const save=()=>store.set('jibun',{m:man,p:picks});
  const box=$('#qBox'),num=$('#qNum'),bar=$('#qBar'),bk=$('#qBack');
  const L=['ちがう','ややちがう','どちらとも','ややそう','そう'];
  function render(){
    num.textContent=`${Math.min(qi+1,N)} / ${N}`;bar.style.width=(qi/N*100)+'%';bar.parentNode.setAttribute('aria-valuenow',String(qi));
    bk.disabled=qi===0;
    if(qi<35){
      const part=qi<20?{e:'PART I',l:'あなたの使い方'}:{e:'PART II',l:'主としての腕　'+VIRT[OQS[qi-20][1]].n};
      box.replaceChildren(el('p',{class:'q-part'},el('span',{class:'eyebrow',text:part.e}),part.l),el('h2',{class:'q-t',id:'qt',text:MYQS[qi]}),
        el('div',{class:'scale',role:'radiogroup','aria-labelledby':'qt'},[1,2,3,4,5].map(v=>el('button',{type:'button',role:'radio','aria-checked':String(man[qi]===v),class:'s'+v,onclick:()=>{man[qi]=v;save();box.querySelectorAll('.scale button').forEach((b,j)=>b.setAttribute('aria-checked',String(j+1===v)));setTimeout(()=>{qi++;render()},RM?0:220)}},el('i'),el('span',{text:L[v-1]})))));
      box.querySelector('.scale button[aria-checked="true"]')?.focus({preventScroll:true});
    }else{
      const err=el('p',{class:'err',hidden:true,role:'alert'});
      const ub=el('div',{class:'uses'},USES.map((u,i)=>el('button',{type:'button',onclick:()=>{const n=i+1;picks=picks.includes(n)?picks.filter(x=>x!==n):picks.length<3?[...picks,n]:picks;save();mark()}},u)));
      const mark=()=>ub.querySelectorAll('button').forEach((b,j)=>{const k=picks.indexOf(j+1);b.setAttribute('aria-pressed',String(k>=0));if(k>=0)b.dataset.rank=ROMAN[k];else delete b.dataset.rank});
      box.replaceChildren(el('p',{class:'q-part'},el('span',{class:'eyebrow',text:'LAST'}),'最後の問い'),el('h2',{class:'q-t',text:'AIによく頼むことを、多い順に三つ選んでください'}),ub,err,
        el('div',{class:'q-go'},el('button',{class:'btn lg',type:'button',onclick:()=>{const miss=man.findIndex(v=>!v);if(miss>=0){qi=miss;render();return}if(picks.length<3){err.hidden=false;err.textContent='あと'+(3-picks.length)+'つ選んでください。';return}
          const r=judge({a:man.slice(0,20),o:man.slice(20),kz:[],ms:-1,u:picks,ai:'自分',kuse:'',hito:''});store.set('jibun',null);ritual(r,()=>commit(r))}},'カードを引く')));
      mark();
    }
  }
  bk.addEventListener('click',()=>{if(qi>0){qi--;render()}});
  render();
};

/* ----- 結果 ----- */
PAGES.kekka=()=>{
  const sp=new URLSearchParams(location.search),code=sp.get('c'),last=store.get('last',null);
  let base=dec(code),r=null,mine=false;
  if(!base&&last&&typeof last.t==='number'){base=last;mine=true}
  if(!base){$('#kekka').replaceChildren(el('div',{class:'empty'},el('h1',{text:'まだカードがありません'}),el('p',{class:'lead',text:'いつものAIに呪文を送ると、あなたのカードと主の位が出ます。'}),el('a',{class:'btn lg',href:'/uranai/'},'無料で占う')));return}
  if(!mine&&last&&last.code&&dec(last.code)&&enc(dec(last.code))===enc(base)){mine=true}
  if(mine&&last){r=Object.assign({},last)}
  else{r=Object.assign({},base,{ai:'',hito:(sp.get('h')||'').slice(0,50),kuse:''});const o=decO(sp.get('o'));if(o){o.honne='';o.scene='';r.own=o}}
  if(mine&&last&&!last.own&&sp.get('o')){const o=decO(sp.get('o'));if(o)r.own=Object.assign(o,{honne:'',scene:''})}
  const fresh=sp.get('new')==='1'&&mine;
  if(sp.get('new')){try{history.replaceState(null,'',location.pathname+'?'+[...sp].filter(([k])=>k!=='new').map(([k,v])=>k+'='+encodeURIComponent(v)).join('&')+location.hash)}catch{}}
  if(!mine)meet(r.t,r.k);
  const T=TYPES[r.t],c=campOf(r.t),p=paceOf(r.t),K=KI[r.k],H=HOUSES[c],[ali,leg]=CH[r.t*5+r.k],P=pals(r.t),rev=isRev(r),O=oracle(r),own=r.own,aiN=mine&&r.ai&&r.ai!=='自分'?r.ai:'あなたのAI';
  document.title=`${fullName(r.t,r.k)}〈${ali}〉｜AIタイプ図鑑`;
  const root=$('#kekka');root.className='kekka c'+c;
  const who=mine?null:el('p',{class:'shared-note'},'これは、ほかの人のカードです。',el('a',{href:'/uranai/'},'あなたも占う →'));

  /* 上：判決とカード（いちばん最初に「AIにどう言われたか」） */
  const F=FUN[r.t],rf=own?RANK_FUN[own.rk]:'';
  const vText=r.hito||F.roast[0],vBy=r.hito?(mine?aiN:'この人のAI')+'の判決':'この星の人へ、AIの本音';
  const hero=el('section',{class:'k-hero'},
    el('div',{class:'k-card'},card(r.t,r.k,{size:'lg',rev,lazy:false}),rev?el('p',{class:'revtag',text:'逆位置'}):null),
    el('blockquote',{class:'verdict k-verdict'},el('small',{text:vBy}),el('p',{text:qt(vText)}),mine&&r.kuse?el('span',{text:'あなたの口ぐせ「'+r.kuse+'」'}):null),
    el('div',{class:'k-info'},
      el('p',{class:'k-you',text:mine?'あなたは、':'この人は、'}),
      el('h1',{class:'k-name',text:fullName(r.t,r.k)}),
      el('p',{class:'k-alias',text:'〈 '+ali+' 〉'}),
      el('p',{class:'k-yet',text:F.yet+'。'}),
      el('div',{class:'chips'},el('span',{class:'chip'},el('i',{class:'dot'}),H.n),el('span',{class:'chip'},el('b',{text:ROMAN[r.t]}),T.star),el('span',{class:'chip',text:K.short+'の相'}),el('span',{class:'chip',text:PACE[p]+'の歩み'})),
      own?el('a',{class:'rank-banner',href:'#kurai'},seal(own.rk,'sm'),el('div',{},el('small',{text:'第二の札　主の位'}),el('b',{text:RANKS[own.rk].r+'　'+RANKS[own.rk].n}),el('span',{class:'rb-p',text:RANKS[own.rk].p}),el('span',{text:rf})),el('em',{text:'くわしく →'})):
        el('a',{class:'rank-banner none',href:'/uranai/'},el('div',{},el('small',{text:'第二の札　主の位'}),el('b',{text:'まだ開いていません'}),el('span',{text:'今の呪文で占うと、AIがあなたに位をつけます'})),el('em',{text:'占う →'})),
      el('div',{class:'k-acts'},
        el('button',{class:'btn',type:'button',onclick:()=>$('#sheet').scrollIntoView({behavior:RM?'auto':'smooth',block:'start'})},'診断書を見る・送る'),
        mine?el('a',{class:'btn ghost',href:'/kurabe/'},'ほかのAIと比べる'):el('a',{class:'btn ghost',href:'/uranai/'},'自分も占う'),
        el('a',{class:'btn ghost',href:'/nakama/'},'仲間と順位を作る'))));

  /* あるある：当たったらタップ */
  const ARU=[...T.aru,...F.aru.slice(0,3)],aKey='aru_'+enc(r),hits=new Set(mine?store.get(aKey,[]):[]);
  const aCount=el('p',{class:'aru-count'});
  const aruLine=()=>hits.size>=5?'ほぼ全部当たり。AIは、あなたをよく見ています。':hits.size>=3?'半分以上当たり。だいたい見抜かれています。':hits.size>=1?'少しだけ当たり。まだ隠している顔がありそうです。':'当てはまる物をタップしてください。';
  const paintA=()=>{aCount.replaceChildren(el('b',{text:hits.size+' / '+ARU.length}),'　'+aruLine())};
  const aruBox=el('section',{class:'k-aru'},el('header',{},el('span',{class:'eyebrow',text:'ARU ARU'}),el('h2',{text:(mine?'あなた':'この星の人')+'の「あるある」'}),el('p',{class:'note',text:'当たっていたらタップ。いくつ当たる？'})),
    el('div',{class:'aru-grid'},ARU.map((x,i)=>el('button',{type:'button',class:'aru-card','aria-pressed':String(hits.has(i)),onclick:e=>{hits.has(i)?hits.delete(i):hits.add(i);e.currentTarget.setAttribute('aria-pressed',String(hits.has(i)));if(mine)store.set(aKey,[...hits]);paintA()}},el('i',{'aria-hidden':'true'}),el('span',{text:x})))),aCount,
    el('button',{class:'xmini',type:'button',onclick:()=>xPost(`${fullName(r.t,r.k)}のあるある、${hits.size}/${ARU.length}当たった。\n${ARU.filter((x,i)=>hits.has(i)).slice(0,2).map(x=>'・'+x).join('\n')}\nあなたは何個当たる？\n#AIタイプ図鑑`)},el('b',{text:'X'}),'で当たった数を送る'));
  paintA();
  const secret=el('section',{class:'k-secret'},
    el('div',{class:'ks-a'},el('span',{class:'eyebrow',text:'SECRET'}),el('h2',{text:mine&&own&&own.honne?aiN+'の本音':'AIがこっそり思っていること'}),el('p',{class:'ks-q',text:qt(mine&&own&&own.honne?own.honne:F.roast[1])}),mine&&own&&own.scene?el('small',{text:'あの時のこと：'+own.scene}):el('small',{text:F.roast[2]}),
      el('button',{class:'xmini',type:'button',onclick:()=>xPost(`${mine&&own&&own.honne?'私のAI（'+aiN+'）':'AI'}の本音：\n${qt(mine&&own&&own.honne?own.honne:F.roast[1])}\n\n#AIタイプ図鑑`)},el('b',{text:'X'}),'でこの本音を送る')),
    el('div',{class:'ks-b'},el('span',{class:'eyebrow',text:'YOU SAY'}),el('h2',{text:'AIに言いがちな一言'}),el('ul',{class:'says'},F.say.map(x=>el('li',{text:'「'+x+'」'}))),el('small',{text:'当てはまったら、たぶんこの星です。'})));

  /* くわしい読み（たたむ） */
  const panel=(id,...kids)=>el('div',{class:'k-panel',id:'p-'+id},...kids);

  const pHoshi=panel('hoshi',
    block('ESSENCE','本質',el('p',{class:'prose',text:T.core})),
    rev?block('REVERSED','逆位置の読み',el('p',{class:'prose',text:T.rev}),el('p',{class:'note',text:'あなたの星は、二つの宮の境目に立っています。カードが逆さに出たのはそのためです。'})):null,
    block('IN THE EYES OF AI','AIから見たあなた',el('p',{class:'prose',text:T.ai})),
    block('TWO FACES','表と裏',pair(T.omote,T.ura,'表の顔','裏の顔')),
    block('HOUSE',H.n+'と'+K.n+'相',el('p',{class:'prose',text:H.lore}),el('p',{class:'prose',text:K.d})));

  let pKurai,fixSec=null;
  if(own){
    const R=RANKS[own.rk],pc=rankPct(own.sc);
    const up=r.prev!=null&&r.prev!==own.rk?el('p',{class:'rank-up'},r.prev<own.rk?'前回より位が上がりました　':'前回より位が下がりました　',el('b',{text:RANKS[r.prev].r+' → '+R.r})):null;
    const ladder=el('ol',{class:'ladder','aria-label':'七つの位'},RANKS.map((x,i)=>i).reverse().map(i=>el('li',{class:i===own.rk?'me':''},el('b',{text:RANKS[i].r}),el('span',{text:RANKS[i].n}),el('small',{text:RANKS[i].p}))));
    pKurai=panel('kurai',
      el('section',{class:'rank-hero'},
        el('div',{class:'rh-seal'},seal(own.rk,'lg')),
        el('div',{class:'rh-t'},el('span',{class:'eyebrow',text:'THE SECOND CARD'}),el('p',{class:'rh-k',text:'第二の札　主の位'}),el('h2',{class:'rh-n',text:R.n}),el('p',{class:'rh-p',text:R.p}),
          el('p',{class:'rh-sc',id:'rankPct'},...(pc?['占った人の中で ',el('b',{text:'上位 '+pc+'%'})]:['主の点 ',el('b',{text:own.sc}),' ／ 100'])),
          el('p',{class:'note',text:own.self?'あなた自身の答えから読んだ位です。AIに占わせると、もっと正直な位が出ます。':(mine?aiN+'が、主であるあなたにつけた位です。':'この人のAIが、この人につけた位です。')}),up),
        ladder),
      own.mem?el('p',{class:'memo',text:own.mem===2?'このAIは、やり取りを覚えていないと答えました。位は、今の会話から推し量った物です。いつもの会話で占うと、もっと当たります。':'このAIは、やり取りを少ししか覚えていないと答えました。位には、少し推し量りが入っています。'}):null,
      block('READING','位の読み',el('p',{class:'prose',text:R.d}),el('blockquote',{class:'whisper'},el('small',{text:(mine?aiN:'AI')+'の気持ち'}),el('p',{text:R.ai}))),
      block('FIVE VIRTUES','指示の五つの徳',el('div',{class:'virt-wrap'},el('div',{class:'penta-box'},penta(own.v)),
        el('div',{class:'virts'},VIRT.map((V,i)=>el('div',{class:'virt'+(i===own.hi?' hi':i===own.lo?' lo':'')},el('i',{text:V.k}),el('div',{},el('b',{text:V.n}),el('small',{text:V.d}),el('div',{class:'vbar'},el('span',{style:`width:${Math.max(4,own.v[i])}%`}))),el('em',{text:own.v[i]}))))),
        pair(VIRT[own.hi].hi,VIRT[own.lo].lo,'いちばん強い徳　'+VIRT[own.hi].n,'いちばん弱い徳　'+VIRT[own.lo].n)));
    fixSec=el('section',{class:'k-fix'},el('header',{class:'kf-h'},el('span',{class:'eyebrow',text:'HOW TO WIN YOUR AI'}),el('h2',{text:'AIともっと上手くやる'}),el('p',{class:'note',text:'あなたの癖と、AIがつまずく所。写して頼みの最初に置くだけで、AIの答えが変わります。'})),
      block('HABITS OF THE MASTER','主の癖',el('p',{class:'note',text:own.self?'あなたの答えから、強く出ている癖を二つ選びました。':(mine?aiN+'が選んだ、あなたの癖です。':'この人のAIが選んだ癖です。')}),
        el('div',{class:'kuse-list'},own.kz.map((k,i)=>{const X=KUSE[k];return el('article',{class:'kuse'},el('header',{},el('span',{class:'eyebrow',text:['FIRST','SECOND'][i]}),el('h3',{text:X.n}),el('small',{text:X.p})),el('p',{class:'kuse-ai',text:X.ai}),fixBox('この癖を消す一文',X.cure))}))),
      block('WHERE AI FALLS','AIがいつもミスる場所',el('div',{class:'miss'},el('b',{class:'miss-n',text:MISS[own.ms].n}),el('p',{class:'miss-s',text:'よくある形：'+MISS[own.ms].sign}),
        el('p',{class:'prose'},el('strong',{text:'それは、AIのせいだけではありません。'}),MISS[own.ms].why),fixBox('頼む時に足す一文',VIRT[MISS[own.ms].v].fix))),
      block('NEXT RANK','次の位への一歩',el('p',{class:'prose',text:own.rk<6?`いちばんの近道は「${VIRT[own.lo].n}」です。次の頼みから、この一文を最初に置いてください。何度か続けてからもう一度占うと、AIのつける位が変わります。`:'あなたはすでに最上の位にいます。この位を保つ鍵は、急ぐ日にも五つの徳を手放さないことです。'}),
        own.rk<6?fixBox('次の位へ',VIRT[own.lo].fix):null,
        own.rk<6?el('p',{class:'note',text:`次の位「${RANKS[own.rk+1].n}（${RANKS[own.rk+1].p}）」まで、あと ${Math.max(1,[22,34,46,62,74,86,101][own.rk]-own.sc)} 点。`}):null,
        el('a',{class:'more',href:'/kurai/'},'七つの位と、十六の癖をすべて見る →')));
    onStats(()=>{const pc=rankPct(own.sc),e=$('#rankPct');if(pc&&e)e.replaceChildren('占った人の中で ',el('b',{text:'上位 '+pc+'%'}))});
  }else{
    pKurai=panel('kurai',el('div',{class:'empty'},el('span',{class:'eyebrow',text:'THE SECOND CARD'}),el('h2',{text:'第二の札は、まだ伏せられています'}),el('p',{class:'lead',text:'今の呪文には、AIがあなたを「主」として採点する15の問いが入っています。もう一度占うと、七つの位のどれかと、あなたの癖、AIがいつもミスる場所が開きます。'}),el('a',{class:'btn',href:'/uranai/'},'今の呪文で占う')));
  }

  const pUn=panel('un',
    el('section',{class:'oracle'},el('span',{class:'eyebrow',text:'ORACLE OF TODAY'}),el('p',{class:'or-d',text:O.d.replace(/-/g,'.')+'　今日の託宣'}),el('p',{class:'or-t',text:O.text}),el('div',{class:'chips'},el('span',{class:'chip',text:'幸運の頼みごと「'+O.use+'」'}),el('span',{class:'chip'},'幸運の数 ',el('b',{text:O.num})))),
    block('FORTUNE','四つの運',el('div',{class:'lucks'},[['仕','仕事運',T.luck.work],['学','学び運',T.luck.learn],['創','創作運',T.luck.make],['心','心の運',T.luck.heart]].map(([i,n,x])=>el('div',{class:'luck'},el('i',{text:i}),el('div',{},el('b',{text:n}),el('p',{text:x})))))),
    block('KEY TO FORTUNE','開運の一手',el('p',{class:'prose',text:T.t}),fixBox('あなたに効く呪文（AIへの一言）',T.spell)));

  const myCode=enc(r);
  const pEn=panel('en',
    block('BONDS','縁のあるカード',el('div',{class:'pals'},[['運命の相手',P.best],['学べる相手',P.learn],['ぶつかる相手',P.clash]].map(([l,t])=>el('a',{class:'pal',href:starUrl(t)},el('small',{text:l}),card(t,0,{size:'sm'}),el('span',{text:TYPES[t].n+'｜'+TYPES[t].star}))))),
    block('SIGIL','星の符号',el('p',{class:'note',text:'この符号を友だちと交換すると、ふたりの縁が占えます。'}),
      el('div',{class:'sigil'},el('code',{text:myCode}),el('button',{class:'btn dark sm',type:'button',onclick:()=>copy(myCode,'符号を写しました')},'写す')),
      el('a',{class:'btn ghost',href:'/en/?a='+encodeURIComponent(myCode)},'この符号で縁を占う')));

  /* ===== 診断書：結果を一枚にまとめる（このまま画像にして送れる） ===== */
  const shareOn=()=>!!$('#shareH')?.checked;
  const sLink=()=>shareUrl(r)+(shareOn()&&r.hito?'&h='+encodeURIComponent(r.hito):'');
  const xPost=text=>open('https://x.com/intent/post?text='+encodeURIComponent(text)+'&url='+encodeURIComponent(sLink()),'_blank','noopener');
  const xText=()=>`${shareOn()&&r.hito?'私のAI（'+(r.ai||'AI')+'）の判決：\n「'+r.hito+'」\n\n':''}私は「${fullName(r.t,r.k)}」${rev?'（逆位置）':''}〈${ali}〉${own?'\n主の位：'+RANKS[own.rk].r+' '+RANKS[own.rk].n+'（'+own.sc+'点）\n'+starsOf(own.rk):''}${own?'\n能力値 '+VIRT.map((V,i)=>V.k+grade(own.v[i])).join(' '):''}${hits.size?'\nあるある '+hits.size+'/'+ARU.length+' 当たり':''}\nあなたのAIは、あなたを何だと思ってる？\n#AIタイプ図鑑`;
  const SH=sheetData(r,own,P);
  const sheet=el('section',{class:'sheet',id:'sheet','aria-labelledby':'sheetH'},
    el('header',{class:'sh-h'},el('span',{class:'eyebrow',text:'AI CARTE'}),el('h2',{id:'sheetH',text:mine?(aiN==='あなたのAI'?'AI':aiN)+'がつけた、あなたの診断書':'この人の診断書'}),el('p',{class:'note',text:'この一枚が、そのまま画像になります。'})),
    el('div',{class:'sh-paper'},
      el('div',{class:'sh-top'},el('div',{class:'sh-card'},card(r.t,r.k,{size:'sm',rev})),
        el('div',{class:'sh-id'},el('small',{text:SH.line}),el('b',{text:fullName(r.t,r.k)}),el('span',{text:'〈 '+ali+' 〉'}),el('em',{text:F.yet+'。'}))),
      own?el('div',{class:'sh-rank'},seal(own.rk,'sm'),el('div',{},el('small',{text:'主の位'}),el('b',{text:RANKS[own.rk].r+'　'+RANKS[own.rk].n}),el('span',{text:RANKS[own.rk].p+'・'+own.sc+'点'})),el('div',{class:'sh-komaru'},el('small',{text:'AIを困らせ度'}),el('b',{text:SH.komaru}))):
        el('a',{class:'sh-rank none',href:'/uranai/'},el('div',{},el('small',{text:'主の位'}),el('b',{text:'まだ開いていません'}),el('span',{text:'今の呪文で占うと、能力値と位が出ます'}))),
      own?el('div',{class:'sh-stats'},el('h3',{text:'主の能力値'}),el('ul',{},VIRT.map((V,i)=>el('li',{class:'g'+grade(own.v[i])},el('i',{text:V.k}),el('span',{text:SH.vn[i]}),el('div',{class:'sbar'},el('u',{style:`width:${Math.max(4,own.v[i])}%`})),el('b',{text:grade(own.v[i])}))))):null,
      el('div',{class:'sh-axes'},el('h3',{text:'AIとの付き合い方'}),
        el('div',{class:'ax'},el('div',{class:'lab'},el('span',{},'任せる ',el('b',{text:r.ma+'%'})),el('span',{},'一緒に ',el('b',{text:(100-r.ma)+'%'}))),el('div',{class:'bar'},el('i',{style:`left:${100-r.ma}%`}))),
        el('div',{class:'ax'},el('div',{class:'lab'},el('span',{},'作る ',el('b',{text:r.mk+'%'})),el('span',{},'知る・話す ',el('b',{text:(100-r.mk)+'%'}))),el('div',{class:'bar'},el('i',{style:`left:${100-r.mk}%`})))),
      el('div',{class:'sh-two'},el('div',{class:'good'},el('small',{text:'長所'}),el('p',{text:T.s})),el('div',{class:'bad'},el('small',{text:'短所'}),el('p',{text:T.w}))),
      el('dl',{class:'sh-list'},
        el('div',{},el('dt',{text:'よく頼む事'}),el('dd',{text:r.u.map((x,i)=>(i+1)+'. '+USES[x-1]).join('　')})),
        own?el('div',{},el('dt',{text:'主の癖'}),el('dd',{text:own.kz.map(k=>KUSE[k].n).join('・')})):null,
        own?el('div',{},el('dt',{text:'AIがミスる所'}),el('dd',{text:MISS[own.ms].n})):null,
        el('div',{},el('dt',{text:'相性◎'}),el('dd',{},el('a',{href:starUrl(P.best),text:TYPES[P.best].n}))),
        el('div',{},el('dt',{text:'相性×'}),el('dd',{},el('a',{href:starUrl(P.clash),text:TYPES[P.clash].n}))))),
    mine&&r.hito?el('label',{class:'opt'},el('input',{type:'checkbox',id:'shareH',checked:'checked'}),el('span',{},'AIの判決（ひとこと）も載せる',el('small',{text:'「本音」と「あの時のこと」は載せません'}))):null,
    el('div',{class:'sh-send'},
      el('button',{class:'btn lg',type:'button',onclick:()=>sendSheet(r,mine,aiN,xText,sLink)},'診断書を画像で送る'),
      el('div',{class:'share-btns'},
        el('button',{class:'sbtn x',type:'button',onclick:()=>xPost(xText())},el('b',{text:'X'}),'でポスト'),
        el('button',{class:'sbtn line',type:'button',onclick:()=>open('https://social-plugins.line.me/lineit/share?url='+encodeURIComponent(sLink()),'_blank','noopener')},el('b',{text:'LINE'}),'で送る'),
        el('button',{class:'sbtn',type:'button',onclick:()=>copy(sLink(),'リンクを写しました')},el('b',{text:'URL'}),'を写す')),
      el('div',{class:'shot',id:'shot'})));
  const again=el('div',{class:'again-row'},el('a',{class:'btn ghost',href:'/uranai/'},'もう一度占う'),el('a',{class:'btn ghost',href:'/kurabe/'},'AIくらべ'),el('a',{class:'btn ghost',href:'/nakama/'},'仲間と順位'));

  const deep=el('details',{class:'k-deep',id:'deep'},el('summary',{},el('span',{class:'eyebrow',text:'FULL READING'}),el('b',{text:'くわしい読みを開く'}),el('small',{text:'本質・表と裏・'+(own?'五つの徳・七つの位・':'')+'四つの運・縁'})),
    el('div',{class:'k-panels'},pHoshi,pKurai,pUn,pEn));
  root.replaceChildren(...[who,hero,sheet,aruBox,secret,fixSec,deep,again].filter(Boolean));
  root.querySelectorAll('.k-panel').forEach(p=>{const kids=[...p.children].filter(Boolean);p.replaceChildren(...kids)});
  root.querySelector('.rank-banner:not(.none)')?.addEventListener('click',e=>{e.preventDefault();$('#sheet').scrollIntoView({behavior:RM?'auto':'smooth',block:'start'})});
  if(/^#(kurai|un|en|hoshi)$/.test(location.hash)){deep.open=true;setTimeout(()=>$('#p-'+location.hash.slice(1))?.scrollIntoView({block:'start'}),80)}
  else if(/^#(share|sheet)$/.test(location.hash))setTimeout(()=>$('#sheet').scrollIntoView({block:'start'}),80);
  if(fresh&&own&&own.rk!==undefined){/* 位の段を見せたい人は上の帯から */}
};

/* ===== 診断書の中身と画像（1080×1350） ===== */
const grade=v=>v>=85?'S':v>=70?'A':v>=55?'B':v>=40?'C':v>=25?'D':'E';
const starsOf=rk=>'AIを困らせ度 '+RANK_FUN[rk].split('　')[0].replace('AIを困らせ度 ','');
function sheetData(r,own,P){
  const T=TYPES[r.t],H=HOUSES[campOf(r.t)],K=KI[r.k];
  return {line:`${H.n}・${ROMAN[r.t]} ${T.star}・${K.short}の相`,komaru:own?RANK_FUN[own.rk].split('　')[0].replace('AIを困らせ度 ',''):'',vn:['目的','材料','条件','確かめ','直し方']};
}
function wrapT(g,text,maxW){const out=[];let l='';for(const ch of String(text)){if(l&&g.measureText(l+ch).width>maxW){out.push(l);l=ch}else l+=ch}if(l)out.push(l);return out}
async function sheetCanvas(r,mine,aiN,withHito){
  const T=TYPES[r.t],[ali]=CH[r.t*5+r.k],rev=isRev(r),own=r.own,P=pals(r.t),SH=sheetData(r,own,P),F=FUN[r.t],C=HOUSES[campOf(r.t)].c;
  const W=1080,H=1350,cv=document.createElement('canvas');cv.width=W;cv.height=H;const g=cv.getContext('2d');
  try{await Promise.all([document.fonts.load('800 60px "Shippori Mincho B1"'),document.fonts.load('700 30px "Shippori Mincho B1"'),document.fonts.load('700 30px "Cinzel"'),document.fonts.load('500 26px "Zen Kaku Gothic New"'),document.fonts.load('700 26px "Zen Kaku Gothic New"')])}catch{}
  const im=new Image();im.src=IMG(r.t,r.k);try{await im.decode()}catch{}
  const MIN='"Shippori Mincho B1",serif',LAT='"Cinzel",serif',UI='"Zen Kaku Gothic New",sans-serif';
  const GOLD='#D6B068',GOLD2='#F0DCAA',TXT='#EEE8DA',SUB='#C9C2D6',MUTE='#9C96B0',LINE='#33344F';
  const bg=g.createRadialGradient(W/2,260,40,W/2,620,1150);bg.addColorStop(0,'#1B1840');bg.addColorStop(1,'#06060E');g.fillStyle=bg;g.fillRect(0,0,W,H);
  for(let i=0;i<110;i++){const x=(i*733)%W,y=(i*397)%H;g.globalAlpha=.18+(i%5)/14;g.fillStyle=i%7?'#DDE3FF':GOLD2;g.beginPath();g.arc(x,y,(i%3)*.6+.5,0,7);g.fill()}g.globalAlpha=1;
  g.strokeStyle=GOLD+'aa';g.lineWidth=2;g.strokeRect(28,28,W-56,H-56);g.strokeStyle=GOLD+'44';g.lineWidth=1;g.strokeRect(38,38,W-76,H-76);
  const txt=(s,x,y,font,color,align='left')=>{g.font=font;g.fillStyle=color;g.textAlign=align;g.fillText(s,x,y)};
  const fit=(s,maxW,size,weight,fam)=>{let z=size;g.font=`${weight} ${z}px ${fam}`;while(z>20&&g.measureText(s).width>maxW){z-=2;g.font=`${weight} ${z}px ${fam}`}return `${weight} ${z}px ${fam}`};
  const OY=40,who=mine?(aiN==='あなたのAI'?'AI':aiN):'この人のAI',hit=withHito&&r.hito;
  if(hit){txt(who+'がつけた、あなたの診断書',W/2,84,`700 22px ${MIN}`,GOLD,'center');const q='「'+r.hito+'」';txt(q,W/2,144,fit(q,W-150,34,800,MIN),GOLD2,'center');txt('― '+who+'の判決',W/2,182,`500 20px ${UI}`,MUTE,'center')}
  else{txt('AI CARTE',W/2,100,`700 26px ${LAT}`,GOLD,'center');txt(mine?who+'がつけた、あなたの診断書':'AIタイプ図鑑の診断書',W/2,146,`700 28px ${MIN}`,SUB,'center')}
  /* カード */
  const CX=74,CY=172+OY,CW=268,CHH=402;
  g.save();g.shadowColor=C;g.shadowBlur=40;g.fillStyle='#0A0A1A';g.fillRect(CX,CY,CW,CHH);g.restore();
  g.save();g.beginPath();g.rect(CX,CY,CW,CHH);g.clip();
  if(im.naturalWidth){if(rev){g.translate(CX+CW/2,CY+CHH/2);g.rotate(Math.PI);g.drawImage(im,-CW/2,-CHH/2,CW,CHH);g.setTransform(1,0,0,1,0,0)}else g.drawImage(im,CX,CY,CW,CHH)}
  const sh=g.createLinearGradient(0,CY,0,CY+CHH);sh.addColorStop(.65,'#06060E00');sh.addColorStop(1,'#06060Ee6');g.fillStyle=sh;g.fillRect(CX,CY,CW,CHH);g.restore();
  g.strokeStyle=GOLD2+'aa';g.lineWidth=2;g.strokeRect(CX+8,CY+8,CW-16,CHH-16);
  txt(ROMAN[r.t],CX+CW/2,CY+44,`700 24px ${LAT}`,GOLD2,'center');
  txt(T.star,CX+CW/2,CY+CHH-28,`700 22px ${MIN}`,GOLD,'center');
  if(rev)txt('逆位置',CX+CW/2,CY+CHH+34,`700 22px ${MIN}`,'#E7967A','center');
  /* 名前 */
  const RX=380,RW=W-RX-74;
  txt(SH.line,RX,200+OY,fit(SH.line,RW,24,500,UI),MUTE);
  txt(fullName(r.t,r.k),RX,280+OY,fit(fullName(r.t,r.k),RW,66,800,MIN),TXT);
  txt('〈 '+ali+' 〉',RX,332+OY,fit('〈 '+ali+' 〉',RW,30,700,MIN),GOLD2);
  g.font=`700 27px ${MIN}`;wrapT(g,F.yet+'。',RW).slice(0,2).forEach((l,i)=>txt(l,RX,392+OY+i*40,`700 27px ${MIN}`,SUB));
  /* 位 */
  const BY=470+OY;g.fillStyle='#11121F';g.strokeStyle=GOLD+'66';g.lineWidth=1.5;g.beginPath();g.roundRect(RX,BY,RW,104,16);g.fill();g.stroke();
  if(own){const R=RANKS[own.rk];txt('主の位',RX+24,BY+36,`500 20px ${UI}`,GOLD);txt(R.r+'　'+R.n,RX+24,BY+78,fit(R.r+'　'+R.n,RW*.55,34,800,MIN),TXT);
    txt(R.p+'・'+own.sc+'点',RX+RW-24,BY+36,`500 20px ${UI}`,MUTE,'right');txt('困らせ度 '+SH.komaru,RX+RW-24,BY+78,fit('困らせ度 '+SH.komaru,RW*.45,26,700,UI),'#E7967A','right')}
  else{txt('主の位',RX+24,BY+36,`500 20px ${UI}`,GOLD);txt('まだ開いていません',RX+24,BY+78,`700 30px ${MIN}`,MUTE)}
  /* 能力値（左） */
  let y=650+OY;const LX=74,LW=440;
  txt('主の能力値',LX,y,`700 26px ${MIN}`,GOLD2);y+=22;
  const GC={S:'#F0DCAA',A:'#D6B068',B:'#7FC3A0',C:'#6E9BE3',D:'#AE8AE6',E:'#E7967A'};
  if(own){VIRT.forEach((V,i)=>{const yy=y+30+i*62,gr=grade(own.v[i]);
    txt(V.k,LX+18,yy+10,`700 26px ${MIN}`,GOLD,'center');txt(SH.vn[i],LX+48,yy+10,`500 23px ${UI}`,SUB);
    g.fillStyle=LINE;g.beginPath();g.roundRect(LX+150,yy-4,220,12,6);g.fill();g.fillStyle=GC[gr];g.beginPath();g.roundRect(LX+150,yy-4,Math.max(10,220*own.v[i]/100),12,6);g.fill();
    txt(gr,LX+LW-6,yy+14,`700 40px ${LAT}`,GC[gr],'right')});y+=30+5*62}
  else{txt('今の呪文で占うと出ます',LX,y+40,`500 24px ${UI}`,MUTE);y+=80}
  /* 付き合い方・長所短所（右） */
  let y2=650+OY;const QX=560,QW=W-QX-74;
  txt('AIとの付き合い方',QX,y2,`700 26px ${MIN}`,GOLD2);y2+=46;
  [[`任せる ${r.ma}%`,`一緒に ${100-r.ma}%`,r.ma],[`作る ${r.mk}%`,`知る・話す ${100-r.mk}%`,r.mk]].forEach(([a,b,v])=>{txt(a,QX,y2,`500 21px ${UI}`,SUB);txt(b,QX+QW,y2,`500 21px ${UI}`,SUB,'right');
    const gr2=g.createLinearGradient(QX,0,QX+QW,0);gr2.addColorStop(0,'#8A6F3E');gr2.addColorStop(1,'#6E7FBF');g.fillStyle=gr2;g.beginPath();g.roundRect(QX,y2+14,QW,8,4);g.fill();
    g.fillStyle=GOLD2;g.beginPath();g.arc(QX+QW*(100-v)/100,y2+18,11,0,7);g.fill();y2+=66});
  y2+=6;
  [['長所',T.s,'#7FC3A0'],['短所',T.w,'#E7967A']].forEach(([l,v,cl])=>{txt(l,QX,y2,`700 21px ${UI}`,cl);g.font=`500 23px ${UI}`;const ls=wrapT(g,v,QW).slice(0,2);ls.forEach((x,i)=>txt(x,QX,y2+34+i*32,`500 23px ${UI}`,TXT));y2+=40+ls.length*32+8});
  /* 下の表 */
  y=Math.max(y,y2)+16;g.strokeStyle=LINE;g.lineWidth=1;g.beginPath();g.moveTo(74,y);g.lineTo(W-74,y);g.stroke();y+=44;
  const rows=[['よく頼む事',r.u.map((x,i)=>(i+1)+'. '+USES[x-1]).join('　')]];
  if(own){rows.push(['主の癖',own.kz.map(k=>KUSE[k].n).join('・')]);rows.push(['AIがミスる所',MISS[own.ms].n])}
  rows.push(['相性',`◎ ${TYPES[P.best].n}　× ${TYPES[P.clash].n}`]);
  rows.forEach(([k,v])=>{txt(k,74,y,`700 22px ${UI}`,GOLD);txt(v,250,y,fit(v,W-74-250,24,500,UI),TXT);y+=44});
  txt(location.host,74,H-50,`500 22px ${LAT}`,GOLD);txt('#AIタイプ図鑑',W-74,H-50,`700 24px ${MIN}`,GOLD,'right');
  if(!hit)txt('あなたのAIは、あなたを何だと思ってる？',W/2,H-50,`500 20px ${UI}`,MUTE,'center');
  return cv;
}
async function sendSheet(r,mine,aiN,xText,sLink){
  const box=$('#shot');box.replaceChildren(el('p',{class:'note',text:'画像を作っています…'}));
  const withH=!!$('#shareH')?.checked;
  const cv=await sheetCanvas(r,mine,aiN,withH);
  const blob=await new Promise(res=>cv.toBlob(res,'image/png'));const url=URL.createObjectURL(blob);
  const file=new File([blob],`AIタイプ図鑑_${fullName(r.t,r.k)}.png`,{type:'image/png'});
  const text=xText()+'\n'+sLink();
  const row=el('div',{class:'shot-btns'});
  if(navigator.canShare&&navigator.canShare({files:[file]}))row.append(el('button',{class:'btn',type:'button',onclick:()=>navigator.share({files:[file],text}).catch(()=>{})},'この画像を送る（X・LINE・インスタ）'));
  row.append(el('a',{class:'btn ghost',href:url,download:file.name},'画像を保存'),el('button',{class:'btn ghost',type:'button',onclick:()=>copy(text,'文とリンクを写しました')},'文を写す'));
  box.replaceChildren(el('img',{src:url,alt:fullName(r.t,r.k)+'の診断書の画像',width:1080,height:1350}),row,el('p',{class:'note',text:'Xに画像を付けるには、保存してからポストに貼ってください。スマホは画像の長押しでも保存できます。'}));
  box.scrollIntoView({behavior:RM?'auto':'smooth',block:'nearest'});
}

/* ----- 縁 ----- */
PAGES.en=()=>{
  const sp=new URLSearchParams(location.search),last=store.get('last',null);
  const A=$('#codeA'),Bx=$('#codeB'),err=$('#enErr'),out=$('#enOut');
  A.value=sp.get('a')||(last?.code||'');Bx.value=sp.get('b')||'';
  function run(scroll){
    const a=dec(A.value),b=dec(Bx.value);
    if(!a||!b){err.hidden=false;err.textContent=!a?'あなたの符号が読めません。結果ページの「縁」にある AI- から始まる符号を入れてください。':'相手の符号が読めません。AI- から始まる符号を入れてください。';return}
    err.hidden=true;meet(b.t,b.k);const [rl,tx]=relation(a.t,b.t);
    out.hidden=false;out.replaceChildren(
      el('div',{class:'en-faces'},el('a',{href:starUrl(a.t)},card(a.t,a.k)),el('span',{class:'en-x',text:'✦'}),el('a',{href:starUrl(b.t)},card(b.t,b.k))),
      el('p',{class:'note',style:'text-align:center',text:`${fullName(a.t,a.k)}　と　${fullName(b.t,b.k)}`}),
      el('span',{class:'eyebrow',text:'BOND'}),el('h2',{class:'en-rel',text:rl}),el('p',{class:'prose',text:tx}),
      el('div',{class:'en-share'},el('button',{class:'btn ghost',type:'button',onclick:()=>copy(location.origin+'/en/?a='+encodeURIComponent(enc(a))+'&b='+encodeURIComponent(enc(b)),'リンクを写しました')},'この縁のリンクを写す')));
    if(scroll)out.scrollIntoView({behavior:RM?'auto':'smooth',block:'nearest'});
  }
  $('#enGo').addEventListener('click',()=>run(true));
  if(A.value&&Bx.value)run(false);
  if(!last){$('#enMine').hidden=false}
};

/* ----- 図鑑 ----- */
PAGES.zukan=()=>{
  const met=metSet(),last=store.get('last',null),mine=last?last.t*5+last.k:-1;
  $('#metN').textContent=String(met.size);
  $('#metBar').style.width=(met.size/60*100)+'%';
  const g=$('#dex');let tab=-1;
  const tabs=$('#dexTabs');
  function render(){
    tabs.replaceChildren(...[['すべて',-1],...HOUSES.map((h,i)=>[h.n,i])].map(([n,i])=>el('button',{type:'button','aria-pressed':String(tab===i),class:i>=0?'c'+i:'',onclick:()=>{tab=i;render()}},i>=0?el('i',{class:'dot'}):null,n)));
    g.replaceChildren(...TYPES.map((_,t)=>t).filter(t=>tab<0||campOf(t)===tab).map(t=>{const got=[0,1,2,3,4].filter(k=>met.has(t*5+k)).length;
      return el('section',{class:'dex-row c'+campOf(t)},el('a',{class:'dex-h',href:starUrl(t)},el('span',{class:'r',text:ROMAN[t]}),el('b',{text:TYPES[t].n}),el('small',{text:TYPES[t].star}),el('em',{text:got+' / 5'})),
        el('div',{class:'dex-slots'},[0,1,2,3,4].map(k=>{const on=met.has(t*5+k);return el('a',{class:'slot'+(on?'':' lock')+(t*5+k===mine?' me':''),href:starUrl(t),'aria-label':on?fullName(t,k):'まだ出会っていないカード'},on?card(t,k,{size:'sm'}):back(),el('small',{text:on?KI[k].short:'？'}))})))}));
  }
  render();
  const hist=store.get('hist',[]),hb=$('#hist');
  if(hist.length){hb.hidden=false;$('#histList').replaceChildren(...hist.slice(0,8).map(h=>el('li',{},el('a',{href:'/kekka/?c='+encodeURIComponent(h.c)+(h.o?'&o='+h.o:'')},el('img',{src:IMG(h.t,h.k),alt:'',width:36,height:54,loading:'lazy'}),el('span',{},el('b',{text:fullName(h.t,h.k)}),el('small',{text:new Date(h.at).toLocaleDateString('ja-JP')+(h.rk>=0?'　'+RANKS[h.rk].r+' '+RANKS[h.rk].n:'')+(h.ai&&h.ai!=='自分'?'　'+h.ai:'')}))))))}
  onStats(S=>{
    const tot=S.n||0;$('#popNote').textContent=tot?`占った人 ${tot.toLocaleString()}人の、生まれた星`:'占った人が増えると表れます。';
    if(tot)$('#pop').replaceChildren(...TYPES.map((T,t)=>{const n=(S.t||[])[t]||0,pc=Math.round(n/tot*100);return el('div',{class:'poprow c'+campOf(t)},el('a',{href:starUrl(t),text:T.n}),el('div',{class:'bar'},el('i',{style:`width:${pc}%`})),el('span',{text:pc+'%'}))}));
    const rk=S.rk||[],rt=rk.reduce((a,b)=>a+b,0);
    if(rt>=10)$('#rkDist').replaceChildren(...RANKS.map((_,i)=>i).reverse().map(i=>el('div',{class:'poprow'},el('span',{text:RANKS[i].r+' '+RANKS[i].n}),el('div',{class:'bar'},el('i',{style:`width:${Math.round((rk[i]||0)/rt*100)}%`})),el('span',{text:Math.round((rk[i]||0)/rt*100)+'%'}))));
    const ok=Object.entries(S.ai||{}).filter(([n,a])=>n!=='その他'&&n!=='自分'&&a[1]>=5).map(([n,a])=>[n,Math.round(a[0]/a[1]),a[1]]).sort((a,b)=>a[1]-b[1]);
    if(ok.length>=2){$('#aiNote').textContent=`主につけた点の平均（低いほど辛口）。いまは ${ok[0][0]} がいちばん厳しく採点しています。`;$('#aiCmp').replaceChildren(...ok.map(([n,a,c])=>el('div',{class:'poprow'},el('span',{text:n}),el('div',{class:'bar'},el('i',{style:`width:${a}%`})),el('span',{text:a+'点'}))))}
  });
};


/* ----- AIくらべ ----- */
PAGES.kurabe=()=>{
  const hist=store.get('hist',[]).filter(h=>h&&typeof h.t==='number'&&h.ai&&h.ai!=='自分'&&h.ai!=='あなたのAI');
  const by=new Map();hist.forEach(h=>{const n=AI_NAME(h.ai)==='その他'?String(h.ai).slice(0,12):AI_NAME(h.ai);if(!by.has(n))by.set(n,Object.assign({},h,{nm:n,own:h.o?decO(h.o):null}))});
  const xs=[...by.values()].slice(0,4),box=$('#kbOut'),steps=$('#kbSteps');
  const done=new Set(xs.map(x=>x.nm));
  $('#kbAis').replaceChildren(...['ChatGPT','Claude','Gemini'].map(n=>el('li',{class:done.has(n)?'done':''},el('b',{text:n}),el('span',{text:done.has(n)?'占い済み':'まだ'}))));
  if(xs.length<2){steps.hidden=false;box.replaceChildren(el('div',{class:'empty'},el('span',{class:'eyebrow',text:xs.length?'ONE MORE AI':'NO RESULT YET'}),el('h2',{text:xs.length?'あと1つのAIで占うと、くらべられます':'まず1つ目のAIで占ってください'}),el('p',{class:'lead',text:xs.length?`いまは ${xs[0].nm} の結果だけです。同じ呪文を、別のAIに送ってください。`:'同じ呪文を ChatGPT・Claude・Gemini などに送ると、AIごとの見方の違いが並びます。'}),el('a',{class:'btn lg',href:'/uranai/'},xs.length?'別のAIで占う':'占う')));return}
  steps.hidden=true;
  const withO=xs.filter(x=>x.own),sorted=[...withO].sort((a,b)=>a.own.sc-b.own.sc);
  const harsh=sorted[0],sweet=sorted[sorted.length-1],split=harsh&&sweet&&harsh!==sweet&&harsh.own.sc!==sweet.own.sc;
  const sameCard=new Set(xs.map(x=>x.t)).size===1;
  const kzAll=withO.length>=2?withO.map(x=>x.own.kz):[];const common=kzAll.length?kzAll[0].filter(k=>kzAll.every(a=>a.includes(k))):[];
  const head=el('section',{class:'kb-verdict'},el('span',{class:'eyebrow',text:'THE VERDICT'}),
    split?el('h2',{},'あなたを一番ナメているのは ',el('em',{text:harsh.nm})):el('h2',{text:sameCard?'AIたちの意見は、ぴったりそろいました':'AIたちの意見は、割れました'}),
    split?el('p',{class:'lead',text:`${harsh.nm}はあなたに${harsh.own.sc}点、${sweet.nm}は${sweet.own.sc}点。同じあなたを見て、${sweet.own.sc-harsh.own.sc}点の差がつきました。`}):null,
    el('p',{class:'note',text:sameCard?`${xs.length}つのAIが、そろって「${TYPES[xs[0].t].n}」と答えました。かなり当たっています。`:`${xs.map(x=>x.nm+'は「'+TYPES[x.t].n+'」').join('、')}と見ています。`}));
  const cols=el('div',{class:'kb-cols',style:`--n:${xs.length}`},xs.map(x=>el('article',{class:'kb-col'+(split&&x===harsh?' harsh':split&&x===sweet?' sweet':'')},
    el('header',{},el('b',{text:x.nm}),split&&x===harsh?el('span',{class:'tag',text:'いちばん辛口'}):split&&x===sweet?el('span',{class:'tag',text:'いちばん甘口'}):null),
    el('a',{href:'/kekka/?c='+encodeURIComponent(x.c)+(x.o?'&o='+x.o:''),class:'kb-card'},card(x.t,x.k,{size:'sm'})),
    el('p',{class:'kb-name',text:fullName(x.t,x.k)}),
    x.own?el('div',{class:'kb-rank'},seal(x.own.rk,'sm'),el('div',{},el('b',{text:RANKS[x.own.rk].n}),el('small',{text:x.own.sc+'点・'+RANKS[x.own.rk].p}))):el('p',{class:'note',text:'主の位なし'}),
    x.hito?el('p',{class:'kb-hito',text:'「'+x.hito+'」'}):null,
    x.own?el('p',{class:'note',text:'癖：'+x.own.kz.map(k=>KUSE[k].n).join('・')}):null)));
  const agree=common.length?el('section',{class:'kb-agree'},el('span',{class:'eyebrow',text:'ALL AIS AGREE'}),el('h2',{text:'AIが口をそろえた、あなたの癖'}),...common.map(k=>el('div',{class:'kuse'},el('header',{},el('h3',{text:KUSE[k].n}),el('small',{text:KUSE[k].p})),el('p',{class:'kuse-ai',text:KUSE[k].ai}),fixBox('この癖を消す一文',KUSE[k].cure)))):null;
  const xt=`同じ呪文を${xs.length}つのAIに送ってみた。\n${xs.map(x=>`${x.nm}：${fullName(x.t,x.k)}${x.own?'／'+RANKS[x.own.rk].n+' '+x.own.sc+'点':''}`).join('\n')}${split?`\n私を一番ナメてたのは ${harsh.nm}`:''}\n#AIタイプ図鑑 #AIくらべ`;
  const share=el('div',{class:'kb-share'},el('button',{class:'btn',type:'button',onclick:()=>open('https://x.com/intent/post?text='+encodeURIComponent(xt)+'&url='+encodeURIComponent(location.origin+'/kurabe/'),'_blank','noopener')},'Xでポスト'),el('button',{class:'btn ghost',type:'button',onclick:()=>copy(xt,'文を写しました')},'文を写す'),el('a',{class:'btn ghost',href:'/uranai/'},'もう1つのAIで占う'));
  box.replaceChildren(...[head,cols,agree,share].filter(Boolean));
};

/* ----- 仲間と順位（サーバーを使わず、リンクの中に仲間を入れる） ----- */
PAGES.nakama=()=>{
  const sp=new URLSearchParams(location.search),last=store.get('last',null);
  const mem=sp.getAll('m').map(v=>{const [n,c,o]=String(v).split('*');const b=dec(c);if(!b||!n)return null;return {n:n.slice(0,10),c:enc(b),b,o:o&&decO(o)?o:'',own:o?decO(o):null}}).filter(Boolean).slice(0,20);
  const gname=(sp.get('g')||'').slice(0,20);
  const out=$('#nkOut'),form=$('#nkForm'),nameI=$('#nkName'),gI=$('#nkGroup'),err=$('#nkErr');
  nameI.value=store.get('nick','');
  if(gname)gI.value=gname;
  const mineIn=!!(last&&last.code&&mem.some(m=>m.c===last.code&&m.n===store.get('nick','')));
  const urlOf=list=>location.origin+'/nakama/?'+[gI.value.trim()?'g='+encodeURIComponent(gI.value.trim().slice(0,20)):null,...list.map(m=>'m='+encodeURIComponent(m.n+'*'+m.c+(m.o?'*'+m.o:'')))].filter(Boolean).join('&');
  $('#nkTitle').textContent=gname?`「${gname}」の主の順位`:mem.length?'仲間の主の順位':'仲間と順位を作る';
  if(!last){form.hidden=true;$('#nkNeed').hidden=false}
  else{
    $('#nkMe').replaceChildren(card(last.t,last.k,{size:'sm'}),el('div',{},el('small',{text:'あなたのカード'}),el('b',{text:fullName(last.t,last.k)}),el('span',{text:last.own?RANKS[last.own.rk].n+'・'+last.own.sc+'点':'主の位なし'})));
    $('#nkGo').textContent=mem.length?(mineIn?'名前を直してリンクを作り直す':'この順位に入る'):'グループを作る';
    $('#nkGo').addEventListener('click',()=>{
      const n=nameI.value.trim().replace(/[*&=?#]/g,'').slice(0,10);if(!n){err.hidden=false;err.textContent='呼び名を入れてください（10文字まで）。';nameI.focus();return}
      err.hidden=true;const prev=store.get('nick','');store.set('nick',n);
      const me={n,c:last.code,o:last.own?encO(last.own):''};
      location.href=urlOf([...mem.filter(m=>!(m.n===n||(m.n===prev&&m.c===last.code))),me]).replace(location.origin,'')+'&joined=1';
    });
  }
  if(!mem.length){out.hidden=true;return}
  out.hidden=false;
  const ranked=[...mem].sort((a,b)=>(b.own?b.own.sc:-1)-(a.own?a.own.sc:-1));
  const withO=ranked.filter(m=>m.own);
  const top=withO[0],bottom=withO.length>=2?withO[withO.length-1]:null;
  let bestPair=null;for(let i=0;i<mem.length;i++)for(let j=i+1;j<mem.length;j++){const[rl]=relation(mem[i].b.t,mem[j].b.t);if(rl==='運命の対'&&(!bestPair||bestPair[2]!=='運命の対'))bestPair=[mem[i],mem[j],rl];else if(rl==='双星'&&!bestPair)bestPair=[mem[i],mem[j],rl]}
  const awards=el('div',{class:'nk-awards'},
    top?el('div',{class:'aw gold'},el('small',{text:'最強の主'}),el('b',{text:top.n}),el('span',{text:RANKS[top.own.rk].n+'・'+top.own.sc+'点'})):null,
    bottom?el('div',{class:'aw warn'},el('small',{text:'AIを一番困らせている人'}),el('b',{text:bottom.n}),el('span',{text:RANKS[bottom.own.rk].n+'・'+bottom.own.sc+'点'})):null,
    bestPair?el('div',{class:'aw'},el('small',{text:bestPair[2]==='運命の対'?'運命の対':'双星（同じ星の二人）'}),el('b',{text:bestPair[0].n+' × '+bestPair[1].n}),el('span',{text:TYPES[bestPair[0].b.t].n+'と'+TYPES[bestPair[1].b.t].n})):null);
  const list=el('ol',{class:'nk-list'},ranked.map(m=>el('li',{class:(last&&m.c===last.code&&m.n===store.get('nick','')?'me':'')},
    el('span',{class:'nk-no',text:m.own?String(withO.indexOf(m)+1):'―'}),
    el('a',{class:'nk-card',href:'/kekka/?c='+encodeURIComponent(m.c)+(m.o?'&o='+m.o:'')},card(m.b.t,m.b.k,{size:'sm'})),
    el('div',{class:'nk-who'},el('b',{text:m.n}),el('span',{text:fullName(m.b.t,m.b.k)})),
    m.own?el('div',{class:'nk-rk'},seal(m.own.rk,'sm'),el('div',{},el('b',{text:RANKS[m.own.rk].n}),el('small',{text:m.own.sc+'点'}))):el('div',{class:'nk-rk'},el('small',{text:'位なし'})))));
  const link=urlOf(mem);
  const lt=`${gname?'「'+gname+'」の':''}AIの主の順位\n${withO.slice(0,5).map((m,i)=>`${i+1}位 ${m.n}（${RANKS[m.own.rk].n}）`).join('\n')}\nあなたも入って→`;
  const share=el('div',{class:'nk-share'},
    sp.get('joined')?el('p',{class:'ok',text:'入りました。このリンクを、グループに送り直してください。'}):el('p',{class:'note',text:'入ったら、新しいリンクをグループに送り直すと、全員の順位がそろいます。'}),
    el('div',{class:'share-btns three'},
      el('button',{class:'sbtn line',type:'button',onclick:()=>open('https://social-plugins.line.me/lineit/share?url='+encodeURIComponent(link),'_blank','noopener')},el('b',{text:'LINE'}),'で送る'),
      el('button',{class:'sbtn x',type:'button',onclick:()=>open('https://x.com/intent/post?text='+encodeURIComponent(lt)+'&url='+encodeURIComponent(link),'_blank','noopener')},el('b',{text:'X'}),'でポスト'),
      el('button',{class:'sbtn',type:'button',onclick:()=>copy(link,'リンクを写しました')},el('b',{text:'URL'}),'を写す')));
  out.replaceChildren(...[awards,list,share].filter(Boolean));
  if(sp.get('joined')){try{history.replaceState(null,'',link.replace(location.origin,''))}catch{}}
};

/* ----- 共有リンク（/s/NN-K/） ----- */
PAGES.share=()=>{const q=location.search;location.replace('/kekka/'+(q||''))};

/* ----- 星のページ：出会った印 ----- */
PAGES.hoshi=()=>{const t=+document.body.dataset.t,met=metSet();$$('.aspect').forEach((a,k)=>{if(met.has(t*5+k))a.classList.add('met')});
  const hits=new Set(store.get('aruS_'+t,[])),cnt=$('#aruN'),all=$$('.aru-card');
  const paint=()=>{if(cnt)cnt.textContent=hits.size+' / '+all.length};
  all.forEach((b,i)=>{b.setAttribute('aria-pressed',String(hits.has(i)));b.addEventListener('click',()=>{hits.has(i)?hits.delete(i):hits.add(i);b.setAttribute('aria-pressed',String(hits.has(i)));store.set('aruS_'+t,[...hits]);paint()})});paint()};

(PAGES[PAGE]||(()=>{}))();
})();
