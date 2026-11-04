/* 11/4 オーナー「日付とマークもっとオシャレに」→ 見本3の右「右！反映いこ 漏れダメよ！」。
   おでかけのカード（リスト・府県ページ・イルミ・紅葉・泊まり・いまから）の左に、種類の絵のタイル（下に FOOD などの英字）と
   日付の札（11.8 SUN）、その下に「あと4日」（7日以内は府県の色）を出す。月（TOWN NOTE）と燈（LIFE NOTE）で同じ物。
   v2.js / v2sub.js から読み込む。不動産のカード（data-cat）は対象外。 */
(function(){
if(window.__cardmark)return;window.__cardmark=1;
var I={
fes:'<path d="M9.5 3.5h5v2h-5zM9.5 18.5h5v2h-5z"/><ellipse cx="12" cy="12" rx="6.2" ry="6.6"/><path d="M6.2 9.6h11.6M5.8 12h12.4M6.2 14.4h11.6"/>',
koyo:'<path d="M12 3l1.6 3.8 3-1.6-.6 3.6 3.6-.4-2 3 2.6 1.6-4 1 .6 2.4-3-1.2-1.8 3-1.8-3-3 1.2.6-2.4-4-1 2.6-1.6-2-3 3.6.4-.6-3.6 3 1.6z"/><path d="M12 15.5V21"/>',
light:'<path d="M10 3C10.6 7.5 11.5 8.4 16 9C11.5 9.6 10.6 10.5 10 15C9.4 10.5 8.5 9.6 4 9C8.5 8.4 9.4 7.5 10 3Z"/><path d="M17.5 13.2c.3 2 .7 2.4 2.5 2.7c-1.8.3-2.2.7-2.5 2.7c-.3-2-.7-2.4-2.5-2.7c1.8-.3 2.2-.7 2.5-2.7Z"/><circle cx="6.5" cy="18.5" r="1"/>',
art:'<rect x="3.5" y="4.5" width="17" height="14" rx="1"/><rect x="6.5" y="7.5" width="11" height="8"/><path d="M6.5 15.5l3.3-3.3 2.4 2.2 2-1.8 3.3 2.9"/><circle cx="14.6" cy="9.8" r=".9"/>',
food:'<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10"/><path d="M17 21V3c-2 1.5-3 4-3 7h3"/>',
flower:'<path d="M12.00 8.00Q13.30 5.70 12.00 3.40Q10.70 5.70 12.00 8.00Z"/><path d="M12.00 8.00Q14.40 6.90 14.70 4.28Q12.30 5.38 12.00 8.00Z"/><path d="M12.00 8.00Q14.59 8.53 16.37 6.58Q13.79 6.05 12.00 8.00Z"/><path d="M12.00 8.00Q13.79 9.95 16.37 9.42Q14.59 7.47 12.00 8.00Z"/><path d="M12.00 8.00Q12.30 10.62 14.70 11.72Q14.40 9.10 12.00 8.00Z"/><path d="M12.00 8.00Q10.70 10.30 12.00 12.60Q13.30 10.30 12.00 8.00Z"/><path d="M12.00 8.00Q9.60 9.10 9.30 11.72Q11.70 10.62 12.00 8.00Z"/><path d="M12.00 8.00Q9.41 7.47 7.63 9.42Q10.21 9.95 12.00 8.00Z"/><path d="M12.00 8.00Q10.21 6.05 7.63 6.58Q9.41 8.53 12.00 8.00Z"/><path d="M12.00 8.00Q11.70 5.38 9.30 4.28Q9.60 6.90 12.00 8.00Z"/><circle cx="12" cy="8" r="1.6"/><path d="M12 9.6V21"/><path d="M12 17c-1.6-2.2-4-2.4-5.2-1.4 1.3 1.7 3.6 2.1 5.2 1.4zM12 15.5c1.6-2.2 4-2.4 5.2-1.4-1.3 1.7-3.6 2.1-5.2 1.4z"/>',
hallo:'<path d="M12 6c-5 0-8 3-8 7s3 7 8 7 8-3 8-7-3-7-8-7z"/><path d="M12 6V3.5"/><path d="M9 12l1.5 1.5M15 12l-1.5 1.5M9 16.5c2 1 4 1 6 0"/>',
xmas:'<path d="M12 5.5l3 4h-1.6l3.6 4.5h-2l3.5 4.5h-13L9 14H7l3.6-4.5H9z"/><path d="M12 18.5V21"/><path d="M12 1.8l.7 1.5 1.6.2-1.2 1.1.3 1.6-1.4-.8-1.4.8.3-1.6-1.2-1.1 1.6-.2z"/>',
quest:'<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/><path d="M8.6 8.9a2 2 0 1 1 2.8 1.8c-.7.3-.9.8-.9 1.4"/><circle cx="10.5" cy="14" r=".5"/>',
animal:'<path d="M12 12.5c-2.8 0-5 2.4-5 4.6 0 1.6 1.3 2.4 2.6 2.4 1 0 1.6-.5 2.4-.5s1.4.5 2.4.5c1.3 0 2.6-.8 2.6-2.4 0-2.2-2.2-4.6-5-4.6z"/><ellipse cx="6" cy="10.5" rx="1.7" ry="2.1"/><ellipse cx="18" cy="10.5" rx="1.7" ry="2.1"/><ellipse cx="9.3" cy="6.3" rx="1.7" ry="2.2"/><ellipse cx="14.7" cy="6.3" rx="1.7" ry="2.2"/>',
play:'<circle cx="12" cy="10" r="6.5"/><path d="M12 3.5v13M5.5 10h13M7.4 5.4l9.2 9.2M16.6 5.4l-9.2 9.2"/><circle cx="12" cy="3.5" r="1.2"/><circle cx="18.5" cy="10" r="1.2"/><circle cx="5.5" cy="10" r="1.2"/><circle cx="12" cy="16.5" r="1.2"/><path d="M8.5 21l3.5-5 3.5 5"/>',
shop:'<path d="M4 9l2-4.5h12L20 9"/><path d="M4 9a2 2 0 0 0 4 0a2 2 0 0 0 4 0a2 2 0 0 0 4 0a2 2 0 0 0 4 0"/><path d="M5.5 11v9h13v-9"/><path d="M9.5 20v-5h5v5"/>',
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
'.cmt{position:relative;width:100%;height:100%;border-radius:15px;display:grid;place-items:center;overflow:hidden;color:var(--pc,#8a8f98);background:linear-gradient(150deg,color-mix(in srgb,var(--pc,#8a8f98) 7%,#fff),color-mix(in srgb,var(--pc,#8a8f98) 24%,#fff));box-shadow:inset 0 1px 0 rgba(255,255,255,.9),0 6px 12px -8px color-mix(in srgb,var(--pc,#8a8f98) 70%,transparent)}'+
'.cmt::before{content:"";position:absolute;width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.55);left:-8px;top:-10px}'+
'.cmt svg{position:relative;width:27px;height:27px;fill:color-mix(in srgb,var(--pc,#8a8f98) 22%,#fff);stroke:currentColor;stroke-width:1.4;stroke-linecap:round;stroke-linejoin:round}'+
'html.night .cmt{filter:invert(1) hue-rotate(180deg);--pl:color-mix(in srgb,var(--pc,#8a8f98) 52%,#fff);color:var(--pl);background:radial-gradient(120% 90% at 50% 115%,color-mix(in srgb,var(--pc,#8a8f98) 55%,transparent),transparent 62%),linear-gradient(160deg,#28324D,#151C2E);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--pl) 30%,transparent),inset 0 1px 0 rgba(255,255,255,.22)}'+
'html.night .cmt::before{width:7px;height:7px;border-radius:0;left:6px;top:6px;background:#FFF6D8;clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%)}'+
'html.night .cmt svg{fill:color-mix(in srgb,var(--pc,#8a8f98) 28%,transparent);filter:drop-shadow(0 0 3px color-mix(in srgb,var(--pl) 85%,transparent))}'+
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
'html.night .cmb .ib::after{clip-path:none!important;filter:drop-shadow(0 0 2px #FFE7A0)!important;width:auto!important;height:auto!important;inset:0!important;left:0!important;top:0!important;border-radius:inherit!important;background-color:transparent!important;background-image:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 10 10\'%3E%3Cpath d=\'M5 0L6.1 3.9 10 5 6.1 6.1 5 10 3.9 6.1 0 5 3.9 3.9Z\' fill=\'%23FFF6D8\'/%3E%3C/svg%3E"),url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 10 10\'%3E%3Cpath d=\'M5 0L6.1 3.9 10 5 6.1 6.1 5 10 3.9 6.1 0 5 3.9 3.9Z\' fill=\'%23FFF6D8\'/%3E%3C/svg%3E"),url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 10 10\'%3E%3Ccircle cx=\'5\' cy=\'5\' r=\'5\' fill=\'%23FFF6D8\'/%3E%3C/svg%3E"),url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 10 10\'%3E%3Ccircle cx=\'5\' cy=\'5\' r=\'5\' fill=\'%23FFF6D8\'/%3E%3C/svg%3E"),url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 20 20\'%3E%3Cpath d=\'M13 2a8 8 0 1 0 5 13A7 7 0 0 1 13 2Z\' fill=\'%23FFE9A8\'/%3E%3C/svg%3E")!important;background-repeat:no-repeat!important;background-size:10px 10px,6px 6px,2.5px 2.5px,2px 2px,13px 13px!important;background-position:6px 7px,18px 4px,57px 30px,9px 32px,48px 5px!important}html.night .cmb .ib::after{animation:cmtw2 3.2s ease-in-out infinite!important}@keyframes cmtw2{0%,100%{opacity:1}50%{opacity:.55}}'+
'@keyframes cmtw{0%,100%{opacity:.95;transform:scale(1)}50%{opacity:.35;transform:scale(.6)}}'+
'html.night .cmb .ib svg{fill:color-mix(in srgb,var(--pc,#8a8f98) 28%,transparent);filter:drop-shadow(0 0 3px color-mix(in srgb,var(--pl) 85%,transparent))}'+
'html.night .cmb .lb{color:var(--pl);opacity:.95}'+
'html.night .cmb .dd{background:linear-gradient(180deg,#2C3652,#1B2338);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--pl) 38%,transparent),inset 0 1px 0 rgba(255,255,255,.14),0 4px 10px -3px rgba(0,0,0,.5)}'+
'html.night .cmb .dd b{color:#F4F1EA}html.night .cmb .dd small{color:var(--pl)}'+
'html.night .cmb .cd{color:var(--pl)}'+
'html.night .cmb .cd.hot{background:linear-gradient(180deg,var(--pl),var(--pc,#8a8f98));color:#141A28;box-shadow:0 0 10px -2px var(--pc,#8a8f98)}'+
'@media (prefers-reduced-motion:reduce){html.night .cmb .ib::after{animation:none!important}}';
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

function kindT(t){t=t||'';for(var i=0;i<R.length;i++)if(R[i][0].test(t))return R[i][1];if(/illumination/.test(location.pathname))return 'light';if(/koyo/.test(location.pathname))return 'koyo';return 'spot';}
/* 11/4 オーナー「地図下選択のロゴも変わるよね？」→ 地図の下のカードの絵も、カードと同じ絵と形にする（map.js から呼ぶ） */
window.cmIcon=function(t){return I[kindT(t)]};
window.cmTile=function(t,pc){var k=kindT(t);return '<div class="cmt" style="--pc:'+(pc||'#8a8f98')+'"><svg viewBox="0 0 24 24">'+I[k]+'</svg></div>';};
try{document.dispatchEvent(new CustomEvent('cm-ready'))}catch(e){}
window.addEventListener('load',go);
try{new MutationObserver(later).observe(document.documentElement,{childList:true,subtree:true});}catch(e){}
})();
