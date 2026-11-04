/* 11/4 オーナー「日付とマークもっとオシャレに」→ 見本3の右「右！反映いこ 漏れダメよ！」。
   おでかけのカード（リスト・府県ページ・イルミ・紅葉・泊まり・いまから）の左に、種類の絵のタイル（下に FOOD などの英字）と
   日付の札（11.8 SUN）、その下に「あと4日」（7日以内は府県の色）を出す。月（TOWN NOTE）と燈（LIFE NOTE）で同じ物。
   v2.js / v2sub.js から読み込む。不動産のカード（data-cat）は対象外。 */
(function(){
if(window.__cardmark)return;window.__cardmark=1;
var I={
fes:'<path d="M4 20V9l8-5 8 5v11"/><path d="M9 20v-6h6v6"/><circle cx="12" cy="9.5" r="1.3"/>',
koyo:'<path d="M12 21v-6"/><path d="M12 15c-5 0-8-4-8-8 3 0 5 1 6 3 0-3 1-5 2-7 1 2 2 4 2 7 1-2 3-3 6-3 0 4-3 8-8 8z"/>',
light:'<path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/><circle cx="12" cy="12" r="3.2"/>',
art:'<rect x="4" y="5" width="16" height="13" rx="1.5"/><path d="M4 15l4.5-4 3.5 3 3-2.5L20 15"/><circle cx="15.5" cy="9" r="1.3"/>',
food:'<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10"/><path d="M17 21V3c-2 1.5-3 4-3 7h3"/>',
flower:'<circle cx="12" cy="10" r="2"/><path d="M12 8c0-3 3-4 3-1 3 0 2 3 0 3 2 2-1 4-3 2-2 2-5 0-3-2-2 0-3-3 0-3 0-3 3-2 3 1z"/><path d="M12 13v8M12 18c-2-2-4-2-5-1"/>',
hallo:'<path d="M12 6c-5 0-8 3-8 7s3 7 8 7 8-3 8-7-3-7-8-7z"/><path d="M12 6V3.5"/><path d="M9 12l1.5 1.5M15 12l-1.5 1.5M9 16.5c2 1 4 1 6 0"/>',
xmas:'<path d="M12 3l3 4.5h-1.6L17 12h-2l3.5 5h-13L9 12H7l3.6-4.5H9z"/><path d="M12 17v4"/>',
quest:'<circle cx="10.5" cy="10.5" r="5.5"/><path d="M14.5 14.5L20 20"/><path d="M9 9.2a1.6 1.6 0 1 1 2.2 1.5c-.6.3-.7.6-.7 1.1"/>',
animal:'<ellipse cx="12" cy="15.5" rx="4" ry="3.3"/><circle cx="6.5" cy="10.5" r="1.7"/><circle cx="17.5" cy="10.5" r="1.7"/><circle cx="9.5" cy="6.5" r="1.7"/><circle cx="14.5" cy="6.5" r="1.7"/>',
play:'<circle cx="12" cy="10" r="6"/><path d="M12 4v12M6 10h12M7.8 5.8l8.4 8.4M16.2 5.8l-8.4 8.4"/><path d="M9 21l3-5 3 5"/>',
shop:'<path d="M5 8h14l-1 12H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
spot:'<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/>'};
var LB={fes:'MATSURI',koyo:'KOYO',light:'LIGHT',art:'ART',food:'FOOD',flower:'FLOWER',hallo:'HALLOWEEN',xmas:'XMAS',quest:'NAZOTOKI',animal:'ANIMAL',play:'PLAY',shop:'MARKET',spot:'SPOT'};
var R=[[/ENLIGHTENMENT|Superblue|イマーシブ|ミュージアム|美術館|博物館/i,'art'],[/ハロウィ[ンー]|HALLOWEEN|ゾンビ|仮装/i,'hallo'],[/クリスマス|CHRISTMAS|Xmas|サンタ|ツリー/i,'xmas'],[/紅葉|もみじ|錦秋|イチョウ|銀杏/,'koyo'],
[/謎|なぞ|脱出|スタンプラリー|リサーチ|探査|めぐり|回遊/,'quest'],
[/イルミ|ILLUMI|ライト|LIGHT|灯|光|ナイト|NIGHT|夜|ルミナ|NAKED|チームラボ|teamLab|ホタル|ランタ[ー]?ン|プロジェクション|瑠璃絵|Twilight|花火|あかり|ヒカリ|Sparkl|SPARKLE|Neon|ルミ|SNOW|snow|WINTER|Winter|青の洞窟|宝石|Crystal|MIRAGE|雲海|KITTE|LuCe/i,'light'],
[/いきもの|生き物|動物|水族館|ニフレル|アニタッチ|アドベンチャーワールド|ペンギン|PINGU|牧場|ふれあい|シーパラ|水族/i,'animal'],
[/展|美術|博物|ミュージアム|アート|ギャラリー|芸術|博覧会|北斎|文化財|文化館|映画|ミュシャ|ジュエリー|Superblue|イマーシブ|ENLIGHTENMENT|大河ドラマ館|コレクション|浮世絵|モネ|広重|若冲|能装束|人形|標本|ガウディ|アントワネット|エリック・カール|三島由紀夫|MOMAS|太郎|物語|HEADLINERS|アンソロジー/i,'art'],
[/グルメ|食|ラーメン|麺|肉|MEAT|やきいも|焼|酒|ビール|BEER|カレー|マルシェ|パン|スイーツ|COFFEE|コーヒー|味覚|バイキング|キッチンカー|収穫|みかん|ぶどう|いちご|りんご|珈琲|ワイン|鍋|ふるまい|ラー1/i,'food'],
[/花|コスモス|菊|バラ|ばら|ダリア|植物|緑化|フラワー|ガーデン|森/,'flower'],
[/おもちゃ|アスレチック|サーカス|遊園|ランド|ドライブ|ライド|サイクル|ペダル|体験|ツアー|ウォーキング|キャラクター|コナン|ムーミン|USJ|ユニバーサル|パーク|PARK|運動会|ワークショップ|こびと|ウルトラ|ROBOT|SLパレオ|鉄道|プラネタリウム|オビツ/i,'play'],
[/祭|まつり|フェス|Festa|Festival|FES|カーニバル|パレード/i,'fes'],
[/マーケット|セール|フリマ|蚤の市|昼市|朝市|マルシェ/,'shop']];
var PCM={"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A","東京":"#4F86C6","群馬":"#9C7BB8","栃木":"#D2697E","千葉":"#D9775A","埼玉":"#E09A3E","神奈川":"#3FA3B5","茨城":"#5FA06A"};
var MO=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'],WE=['SUN','MON','TUE','WED','THU','FRI','SAT'];
var T0=new Date(Date.now()+9*36e5).toISOString().slice(0,10),TY=+T0.slice(0,4),TM=+T0.slice(5,7);
function days(a,b){return Math.round((new Date(b+'T00:00:00Z')-new Date(a+'T00:00:00Z'))/864e5)}
function iso(m,d){var y=TY;if(m<TM-3)y++;else if(m>TM+8)y--;return y+'-'+('0'+m).slice(-2)+'-'+('0'+d).slice(-2)}
function fromText(x){ /* 「11/21（土）まで」「10/1（木）〜1/31（日）」「11/14（土）〜」など */
  if(!x||/発表前|未発表|昨年|公式/.test(x))return{};var m=x.match(/(\d{1,2})(?:[\/.]|月)(\d{1,2})/g)||[];
  var p=m.map(function(v){var q=v.split(/[\/.]|月/);return iso(+q[0],+q[1])});
  if(p.length>=2)return{s:p[0],e:p[1]};if(p.length==1){if(/まで/.test(x))return{e:p[0]};if(/〜\s*$|から/.test(x))return{s:p[0]};return{s:p[0],e:p[0]};}return{};}
var css=
'html body .cm.cm.cm.cm.cm{position:relative;padding-left:98px!important;min-height:150px;box-sizing:border-box}'+
'html body a.card.cm.cmh .v2d,html body a.card.cm.cmh>.d,html body a.card.cm.cmh .bd>.d,html body .cm.cmh .when,html body .cm.cmh .v2d,html body a.cd.cm.cmh>.dt,html body a.fc.cm.cmh>span{display:none!important}'+'html body .paper .it.cmp>a.mp,html body .cmp.cmp>a.mp{left:98px!important}html body .cmp.cmp>.rt{padding-left:98px}html body .paper .it.cmp>.yk,html body .cmp.cmp>.yk{left:160px!important}'+
'.cmb{position:absolute;left:15px;top:15px;width:68px;text-align:center;line-height:1;pointer-events:none}'+
'.cmb .ib{position:relative;width:66px;height:66px;margin:0 auto;border-radius:22px;background:linear-gradient(150deg,color-mix(in srgb,var(--pc,#8a8f98) 7%,#fff) 0%,color-mix(in srgb,var(--pc,#8a8f98) 24%,#fff) 100%);box-shadow:inset 0 1px 0 rgba(255,255,255,.9),0 8px 16px -10px color-mix(in srgb,var(--pc,#8a8f98) 70%,transparent);display:grid;place-items:center;color:var(--pc,#8a8f98);overflow:hidden}'+
'.cmb .ib::before{content:"";position:absolute;width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.55);left:-10px;top:-14px}'+
'.cmb .ib::after{content:"";position:absolute;width:5px;height:5px;border-radius:50%;background:#fff;right:12px;top:11px;opacity:.9}'+
'.cmb .ib svg{position:relative;width:34px;height:34px;margin-top:-8px;fill:color-mix(in srgb,var(--pc,#8a8f98) 22%,#fff);stroke:currentColor;stroke-width:1.35;stroke-linecap:round;stroke-linejoin:round;animation:cmfl 3.6s ease-in-out infinite}'+
'@keyframes cmfl{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}'+
'@media (prefers-reduced-motion:reduce){.cmb .ib svg{animation:none}}'+
'.cmb .lb{position:absolute;bottom:6px;left:0;right:0;font-family:Jost,sans-serif;font-weight:600;font-size:6.5px;letter-spacing:.22em;color:var(--pc,#8a8f98);opacity:.85;padding-left:.22em}'+
'.cmb .dd{position:relative;margin:-12px auto 0;display:inline-flex;align-items:baseline;gap:4px;background:#fff;border-radius:999px;padding:5px 10px;box-shadow:0 0 0 1px color-mix(in srgb,var(--pc,#8a8f98) 16%,#fff),0 3px 8px -2px rgba(60,40,20,.14);white-space:nowrap}'+
'.cmb .dd b{font-family:Jost,sans-serif;font-weight:500;font-size:13px;color:#2B2622;letter-spacing:.02em}'+
'.cmb .dd small{font-family:Jost,sans-serif;font-size:8px;font-weight:500;letter-spacing:.14em;color:var(--pc,#8a8f98)}'+
'.cmb .dd.tx b{font-family:"Zen Kaku Gothic New",sans-serif;font-size:10px;font-weight:700;letter-spacing:.04em}'+
'.cmb .cd{display:inline-block;margin-top:5px;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:9.5px;color:var(--pc,#8a8f98);letter-spacing:.06em;white-space:nowrap}'+
'.cmb .cd.hot{background:var(--pc,#8a8f98);color:#fff;border-radius:999px;padding:3px 7px 2px}'+
/* 11/4 オーナー「夜可愛くない 反転だけしたよう」「左上は太陽か？」→ 夜は反転を打ち消して、夜専用の色で描く。
   夜空の紺のタイルに府県の色がにじむツヤ、絵は光る線、左上の丸は小さくまたたく星に */
'html.night .cmb{filter:invert(1) hue-rotate(180deg);--pl:color-mix(in srgb,var(--pc,#8a8f98) 52%,#fff)}'+
'html.night .cmb .ib{background:radial-gradient(120% 90% at 50% 115%,color-mix(in srgb,var(--pc,#8a8f98) 55%,transparent) 0%,transparent 62%),linear-gradient(160deg,#28324D 0%,#151C2E 100%);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--pl) 30%,transparent),inset 0 1px 0 rgba(255,255,255,.22),0 0 18px -4px color-mix(in srgb,var(--pc,#8a8f98) 75%,transparent);color:var(--pl)}'+
'html.night .cmb .ib::before{width:auto;height:auto;inset:0;border-radius:inherit;background:linear-gradient(180deg,rgba(255,255,255,.16) 0%,rgba(255,255,255,.04) 42%,transparent 43%)}'+
'html.night .cmb .ib::after{width:9px;height:9px;border-radius:0;left:9px;top:8px;right:auto;background:#FFF6D8;clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%);filter:drop-shadow(0 0 2px #FFE7A0);animation:cmtw 2.8s ease-in-out infinite}'+
'@keyframes cmtw{0%,100%{opacity:.95;transform:scale(1)}50%{opacity:.35;transform:scale(.6)}}'+
'html.night .cmb .ib svg{fill:color-mix(in srgb,var(--pc,#8a8f98) 28%,transparent);filter:drop-shadow(0 0 3px color-mix(in srgb,var(--pl) 85%,transparent))}'+
'html.night .cmb .lb{color:var(--pl);opacity:.95}'+
'html.night .cmb .dd{background:linear-gradient(180deg,#2C3652,#1B2338);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--pl) 38%,transparent),inset 0 1px 0 rgba(255,255,255,.14),0 4px 10px -3px rgba(0,0,0,.5)}'+
'html.night .cmb .dd b{color:#F4F1EA}html.night .cmb .dd small{color:var(--pl)}'+
'html.night .cmb .cd{color:var(--pl)}'+
'html.night .cmb .cd.hot{background:linear-gradient(180deg,var(--pl),var(--pc,#8a8f98));color:#141A28;box-shadow:0 0 10px -2px var(--pc,#8a8f98)}'+
'@media (prefers-reduced-motion:reduce){html.night .cmb .ib::after{animation:none}}';
var st=document.createElement('style');st.textContent=css;(document.head||document.documentElement).appendChild(st);
function kind(a,ad){var t=(a.querySelector(ad.t)||{}).textContent||'';var m=(a.querySelector('.m,.pl,small')||{}).textContent||'';
  for(var i=0;i<R.length;i++)if(R[i][0].test(t))return R[i][1];
  for(i=0;i<R.length;i++)if(R[i][0].test(m))return R[i][1];
  var b=document.body&&document.body.getAttribute('data-kind')||'';if(/紅葉/.test(b))return 'koyo';if(/イルミ/.test(b)||/illumination/.test(location.pathname))return 'light';
  return 'spot';}
/* カードの形ごとの読み方：card=カード, t=名前, d=日付の行, box=データ(data-s/e)のある所 */
var AD=[
 {q:'a.card',t:'.t',d:'.v2d,.d'},                       /* 月の全ページ・燈のいまから */
 {q:'div.card.it',t:'.t',d:'.when'},                    /* 燈のおでかけリスト */
 {q:'li.it>.cw>a.cd',t:'.nm',d:'.dt',box:'li.it'},      /* 燈のイルミ・紅葉 */
 {q:'a.fc',t:'b',d:'span'}];                            /* 1件ページの「ほかのおでかけ」・燈の都県ページ */
function one(a,ad){
  if(a.dataset.cm||a.dataset.cat||a.classList.contains('kc')||!a.querySelector(ad.t))return;a.dataset.cm=1;
  var bx=ad.box?a.closest(ad.box):a;
  if(!bx.hasAttribute('data-s')&&!bx.hasAttribute('data-e')){var up=a.parentElement&&a.parentElement.closest('[data-s],[data-e]');if(up&&up.querySelectorAll(ad.q).length===1)bx=up;}
  var s=bx.dataset.s||'',e=bx.dataset.e||'',o=bx.dataset.open||'';
  if(!bx.hasAttribute('data-s')&&!bx.hasAttribute('data-e')){var dt=a.querySelector(ad.d);var r=fromText(dt&&dt.textContent);s=r.s||'';e=r.e||'';}
  if(!getComputedStyle(a).getPropertyValue('--pc').trim()){var up2=a.closest('[data-pref],[data-p]')||{dataset:{}};var pr=a.dataset.pref||bx.dataset.p||up2.dataset.pref||up2.dataset.p||'';
    if(!PCM[pr]){var tx=a.textContent;for(var q in PCM)if(tx.indexOf(q)>=0){pr=q;break}}
    if(PCM[pr])a.style.setProperty('--pc',PCM[pr]);}
  if(!getComputedStyle(a).getPropertyValue('--pc').trim()){var bc=getComputedStyle(a).borderLeftColor;if(bc&&!/rgba\(0, 0, 0, 0\)/.test(bc))a.style.setProperty('--pc',bc);}
  var d,w,n=-1;
  if(o){d=o;w='オープン'}else if(s&&s>T0){d=s;w='から'}else if(e){d=e;w='まで'}else if(s){d=s;w='から'}
  var k=kind(a,ad),pill='',cd='';
  if(d){var y=new Date(d+'T00:00:00Z');pill='<div class="dd"><b>'+(y.getUTCMonth()+1)+'.'+y.getUTCDate()+'</b><small>'+WE[y.getUTCDay()]+'</small></div>';
    if(w==='まで'){n=days(T0,d);cd=n<=0?'<span class="cd hot">今日まで</span>':n<=7?'<span class="cd hot">あと'+n+'日</span>':'<span class="cd">あと'+n+'日</span>';}
    else if(w==='から'&&e===s){n=days(T0,d);cd=n<=7?'<span class="cd hot">'+n+'日後</span>':'<span class="cd">'+n+'日後</span>';}
    else if(w==='から'){n=days(T0,d);cd=n<=0?'<span class="cd">から開催中</span>':n<=7?'<span class="cd hot">'+n+'日後から</span>':'<span class="cd">'+n+'日後から</span>';}
    else cd='<span class="cd">'+w+'</span>';}
  var c=document.createElement('div');c.className='cmb';c.setAttribute('aria-hidden','true');
  c.innerHTML='<div class="ib"><svg viewBox="0 0 24 24">'+I[k]+'</svg><span class="lb">'+LB[k]+'</span></div>'+pill+cd;
  a.insertBefore(c,a.firstChild);a.classList.add('cm');
  /* 日付の行は「まで」の時だけ隠す（札と同じ内容）。期間・開く日・発表前などは残す */
  var dl=a.querySelector(ad.d);var dx=dl?dl.textContent:'';
  if(w==='まで'&&!/開く日|〜\s*\d|発表前|公式/.test(dx))a.classList.add('cmh');}
function go(){for(var j=0;j<AD.length;j++){var L=document.querySelectorAll(AD[j].q);for(var i=0;i<L.length;i++)one(L[i],AD[j]);}var i;
  /* 「地図」の小さなリンクがカードの左下にある形（リスト）は、絵のタイルと重ならないよう右へ */
  var M=document.querySelectorAll('a.card.cm~a.mp,a.card.cm~.rt,a.cd.cm~a.mp');for(i=0;i<M.length;i++)M[i].parentElement.classList.add('cmp');}
var tm;function later(){clearTimeout(tm);tm=setTimeout(go,60)}
if(document.readyState!=='loading')go();else document.addEventListener('DOMContentLoaded',go);
window.addEventListener('load',go);
try{new MutationObserver(later).observe(document.documentElement,{childList:true,subtree:true});}catch(e){}
})();
