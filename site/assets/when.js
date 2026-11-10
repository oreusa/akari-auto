/* 11/6 オーナーOKの見本「押す所を減らした版・5か所直し」。月（関西おでかけリスト）と燈（関東おでかけリスト）で同じ物。
   ・最初に見えるのは日付の4つ（きょう・あした・この週末・来週末）だけ。はじめは「この週末」。
   ・無料・子どもと・雨でも（屋内）・☆保存した所 は「しぼりこむ」を押した時だけ出す。
   ・日にちの決まった催し（期間14日以内）を上に、長く開いている所（紅葉・イルミ・展覧会など）を下に。
   ・カードに「日曜（11/8）で終わります」「11/7（土）の1日だけ」などを1行。
   ・0件の時は、押すと広がるボタン（件数つき）を出す。条件はURLに残る（?d=we&f=kid）。
   子どもと・雨でもは、月と燈が公式ページを見て選んだ所だけ（下の K）。新しいおでかけを足したら K にも足す。 */
(function(){
if(window.__when)return;window.__when=1;
var AK=!!document.querySelector('nav.flt[data-v=odekake]');
var F=AK?document.querySelector('nav.flt[data-v=odekake]'):document.getElementById('flt');if(!F)return;
var SEL=AK?'#odekake .pane[data-t=now] .card.it,#odekake .pane[data-t=up] .card.it':'.paper .blk.b-now .it,.paper .blk.b-up .it';
if(!document.querySelector(SEL))return;
/* k=子どもと i=雨でも（屋内） */
var K={
/* 月（関西） */
"ハルカス300×名探偵コナン":"i","NHK日曜美術館50年展":"i","細田守の原点／展":"i","大英博物館日本美術コレクション百花繚乱":"i","名探偵コナン疾風の追走からの脱出":"i","ミュシャ芸術博覧会リターンズ":"i",
"特別展源氏物語王朝のかがやき":"i","没後100年クロード・モネ展":"i","特別展「寛永太平がはぐくむ美」":"i","やなせたかし展":"ik","水木しげる魂の漫画展":"i","トーベとムーミン展":"ik","ムーミン×神戸ポートタワー":"ik",
"仮面ライダー×自然のチカラ展":"ik","企画展平城遷都":"i","第78回正倉院展":"i","木下大サーカス橿原公演":"ik","飛鳥資料館秋期特別展":"i","百済寺と近江の仏教美術":"i","企画展くらひらく":"i","鈴木崇もののをかし":"i",
"豊臣兄弟！大和郡山大河ドラマ館":"i","北斎・広重づくし":"i","夜の海遊館":"ik","微わかる展2＋小さいすぎるよ展":"i","企画展「あっちもこっちもスズキさん」":"ik","虎屋所蔵品展「心なごむ動物たち」":"i",
"ジュエリーは、誰を夢みる":"i","びっくり構図展":"i","酒にのまれ展":"i","企画展「ふれる×れきはく」":"ik","斑鳩文化財センター秋季特別展「華麗なる王族」":"i","特別展「高照らすみやこ」":"i","没後25年上村松篁展":"i",
"丸木スマ展73歳からのアーティスト":"i","いい福展":"i",
"クラフトパーク秋の日曜体験":"k","怪々YOKAI祭2026":"k","淡路島秋のカーニバル2026":"k","みきUMAフェス2026":"k","PINGUmeetsアドベンチャーワールド":"k","アドベンチャーワールドLIGHTPARKS":"k","国城観光農園みかん狩り":"k",
"万博の森どんぐりフェス":"k","ナゾトキイベント「ぐわ兵衛とアソビ帝国」":"k","南大阪リアル謎解きゲームきくなーれのなぞとき大冒険":"k","おもしろ科学まつり和歌山大会":"k","50万本のコスモス":"k","ブルーメの丘秋の味覚バイキング":"k","ROKKO森の音ミュージアムハロウィンフェア":"k",
/* 燈（関東） */
"MAPPAEXPO15thAnniversary":"i","西塩子の回り舞台":"i","『牧場物語』×那須高原りんどう湖ファミリー牧場":"k",
"謎解き冒険ラリー不思議ハンターin幕張海浜公園":"k","第41回芝山はにわ祭":"k","ハワイアンフェス2026inサクラタウン":"k","メッツァの北欧クリスマス2026":"k",
"おでかけ子ザメサクラタウンさんぽ":"ik","没後150年藤枝太郎英義の刀剣美":"i","こども＋おとな＋秋の美術館":"ik","特別展「豊臣兄弟！」":"i","闇の魔術のハロウィーン":"ik","Re:ホラーにふれる展－映画美術の世界－":"i","鉄道広告展いろいろ、とりどり。":"i","糸が織りなす数学アートの世界":"i",
"現代によみがえる能装束―縫の精緻箔の輝き―":"i","ベストオブすみだ北斎美術館":"i","マリー・アントワネット・スタイル":"i","ミニチュアベーカリーの世界展2026":"i","月と星と―美術がつなぐとき":"i","2026秋の人気番組展":"i",
"MOMASコレクション第2期":"i","蜷川実花展はじまりの光":"i","ウルトラマルチバース地球防衛大作戦in横浜赤レンガ倉庫":"ik","北の丸大妖怪展百鬼騒乱":"ik","辻村寿三郎人形曼陀羅REVIVAL":"i","透明標本の世界―ガラスの中の骨格―":"ik",
"ちょこっとTARO太郎のかわいい":"i","ジオパーク巡回展地球時間の旅":"ik","映像ミュージアム企画展きかんしゃトーマスの世界展":"ik","THEHEADLINERS2026キュン発力の時代":"i","絵師も動物も、人気モノ勢揃い動物たちの浮世絵":"i",
"原作出版80周年きかんしゃトーマスの世界展":"ik","若冲がやってきた！":"i","ルーヴル美術館展ルネサンス":"i","歌川広重江戸のベストアングル":"i","国際美術展TOKYOATLAS":"i","マリメッコ展模様のちから":"i",
"横浜アンパンマンこどもミュージアムクリスマス":"ik","エリック・カールといのちの色―同じ世界で、ちがう色―":"ik","栃木県立美術館松本哲男展":"i","永遠なるガウディVRで辿るサグラダ・ファミリア":"i","シンシナティ美術館展":"i",
"古舘春一ハイキュー!!展挑戦者たち":"i","大チーバくん展さかざきちはるとチーバくんの20年":"ik","雨穴の変な世界展。":"i","草間彌生美術館パァーッと光が出て、キラキラッていろんなものが見えてくる。":"i","まるっとオビツ製作所":"i",
"こびとづかんこびと大発見":"ik","三島由紀夫のアオハル―中島飛行機からの出発―":"i","第96回企画展日本列島誕生のひみつ":"ik","プラネタリウム版チ。地球の運動について":"i","特別展「生きものたちの性」":"i","テート美術館ターナー展":"i",
"THEMOVEUMYOKOHAMAモネと浮世絵":"i","サンリオキャラクターズエキシビション":"ik","藤子・F・不二雄ミュージアムドラえも～ん！願いをかなえるひみつ道具展":"ik","東京都美術館開館100周年記念オルセー美術館所蔵いまを生きる歓び":"i",
"FlytotheMoon:月をめぐる5つの物語":"i","THEROBOTPARKODAIBA":"ik","マザー牧場アグロドーム30周年":"ik",
"ちばZOOフェスタ2026":"k","横浜・八景島シーパラダイス秋パラ！":"k","さがみはら星空探査隊":"k","秋の大ゆる運動会":"k","マザー牧場秋限定イベント":"k","湯河原温泉みかん狩り":"k","SLパレオエクスプレス2026":"k",
"ムーミン谷のクリスマス2026":"k","東武動物公園ウインターイルミネーション":"k","よみうりランドジュエルミネーション2026":"k","海・花そとあそび2026":"k","EzyRoller（軽井沢おもちゃ王国）":"k","MuchuPlanetユニクロパーク横浜ベイサイド":"k"};
var HOL={"2026-11-03":1,"2026-11-23":1,"2027-01-01":1,"2027-01-11":1,"2027-02-11":1,"2027-02-23":1,"2027-03-21":1,"2027-03-22":1};
var T=new Date(Date.now()+9*36e5).toISOString().slice(0,10),W="日月火水木金土";
function add(d,n){var x=new Date(d+"T00:00:00Z");x.setUTCDate(x.getUTCDate()+n);return x.toISOString().slice(0,10);}
function dw(d){return new Date(d+"T00:00:00Z").getUTCDay();}
function md(d){return (+d.slice(5,7))+"/"+(+d.slice(8));}
function mdw(d){return md(d)+"（"+W[dw(d)]+"）";}
var w0=dw(T),we,nwe;
if(w0===6)we=[T,add(T,1)];else if(w0===0)we=[T];else{var sa=add(T,6-w0);we=[sa,add(sa,1)];}
var ns=w0===0?add(T,6):add(we[0],7);nwe=[ns,add(ns,1)];
var D={today:{l:"きょう",d:[T]},tom:{l:"あした",d:[add(T,1)]},we:{l:"この週末",d:we},nwe:{l:"来週末",d:nwe}},DK=["today","tom","we","nwe"];
/* 11/10 決定版：1日ずつ選べる日付の帯（この週末・きょう・あした・2〜13日後・来週末） */
var DS=["we","today","tom"];for(var di=2;di<14;di++){var dd0=add(T,di);D["d"+dd0]={l:mdw(dd0),d:[dd0]};DS.push("d"+dd0);}DS.push("nwe");
var KN={KOYO:"紅葉",LIGHT:"イルミ",MATSURI:"祭り",FOOD:"食べもの",FLOWER:"花",ART:"アート",NAZOTOKI:"謎解き",PLAY:"あそび",ANIMAL:"動物",SPOT:"名所"},KO=["KOYO","LIGHT","MATSURI","FOOD","FLOWER","ART","NAZOTOKI","PLAY","ANIMAL","SPOT"];
function kindOf(o){if(!o.kd){var l=o.w&&o.w.querySelector(".lb");if(!l)return "";o.kd=l.textContent.trim();}return o.kd;}
var FL={free:"無料",kid:"子どもと",rain:"雨でも（屋内）",fav:"☆保存した所"},FK=["free","kid","rain","fav"];
function cardOf(w){return AK?w:w.querySelector("a.card")||w;}
function title(w){var t=w.querySelector(".t");return t?t.textContent.replace(/\s+/g,""):"";}
function link(w){var a=AK?w.querySelector("a.go"):w.querySelector("a.card");return a?a.getAttribute("href"):"";}
var FAV={};try{(JSON.parse(localStorage.getItem("tn_fav")||"[]")||[]).forEach(function(h){FAV[h]=1});}catch(e){}
function saveFav(){try{localStorage.setItem("tn_fav",JSON.stringify(Object.keys(FAV)));}catch(e){}}
var ALL=[].slice.call(document.querySelectorAll(SEL)).map(function(w){var a=cardOf(w),tg=K[title(w)]||"";
  return {w:w,s:a.getAttribute("data-s")||"",e:a.getAttribute("data-e")||"",days:a.getAttribute("data-days")||"",pref:w.getAttribute("data-pref")||a.getAttribute("data-pref")||"",
   free:AK?a.getAttribute("data-free")==="1":/無料/.test((a.getAttribute("data-tag")||"")+(a.getAttribute("data-note")||"")),kid:tg.indexOf("k")>=0,rain:tg.indexOf("i")>=0,href:link(w)};});
function openOn(o,d){if(o.s&&d<o.s)return false;if(o.e&&d>o.e)return false;var r=o.days;if(!r)return true;
  if(r.indexOf("wd:")===0)return (r.indexOf("h")>0&&!!HOL[d])||r.slice(3).indexOf(String(dw(d)))>=0;/* 11/9 夜「月曜休館の美術館が今日行けると出る」→ wd:開く曜日（0=日〜6=土）、h＝祝日も開く */if(r==="sat")return dw(d)===6;if(r==="sun")return dw(d)===0;if(r==="we")return dw(d)===0||dw(d)===6||!!HOL[d];return r.split(",").indexOf(d)>=0;}
function inRange(o,dk){return D[dk].d.some(function(d){return d>=T&&openOn(o,d);});}
function isShort(o){if(!o.s||!o.e)return false;return (Date.parse(o.e)-Date.parse(o.s))/864e5<=14||(o.days&&o.days.indexOf(",")>0);}
function curPref(){var b=F.querySelector("button.on");if(!b)return "";var p=AK?(b.getAttribute("data-p")||""):b.textContent.trim();return p==="すべて"?"":p;}
/* 状態 */
var q=new URLSearchParams(location.search),st={d:q.get("d")||(q.get("v2t")?"all":"we"),f:{}};
if(!D[st.d]&&st.d!=="all")st.d="we";st.k=q.get("k")||"";(q.get("f")||"").split(",").forEach(function(k){if(FL[k])st.f[k]=1;});
function pass(o,dk,f,pf){if(pf&&o.pref!==pf)return false;if(st.k&&dk!=="all"&&kindOf(o)!==st.k)return false;if(dk!=="all"&&!inRange(o,dk))return false;
  for(var k in f){if(k==="fav"){if(!FAV[o.href])return false;}else if(!o[k])return false;}return true;}
function count(dk,f,pf){var n=0;ALL.forEach(function(o){if(pass(o,dk,f,pf))n++;});return n;}
function nf(){return Object.keys(st.f).length;}
function syncUrl(){try{var u=new URLSearchParams(location.search);u.delete("v2t");if(st.d==="we")u.delete("d");else u.set("d",st.d);if(st.k)u.set("k",st.k);else u.delete("k");var fk=Object.keys(st.f);if(fk.length)u.set("f",fk.join(","));else u.delete("f");
  var s=u.toString();history.replaceState(null,"",location.pathname+(s?"?"+s:"")+location.hash);}catch(e){}}
/* 見た目 */
var css=document.createElement("style");css.textContent=
'.wn{margin:12px 0 6px;font-family:"Zen Kaku Gothic New",sans-serif;color:#2B2622}'+
'.wn .wl{font-size:11px;letter-spacing:.14em;color:#8C7B6E;margin:0 2px 6px;font-weight:700}'+
'.wn .wd{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}'+
'.wn button{font:700 13px "Zen Kaku Gothic New",sans-serif;border:1px solid #DADADA;background:#fff;border-radius:999px;padding:8px 10px;color:#2B2622;cursor:pointer;white-space:nowrap}'+
'.wn .wd button{padding:8px 0;text-align:center}.wn button small{font:500 11px Jost,sans-serif;color:#8C7B6E;margin-left:4px}'+
'.wn button.on{background:#2B2622;color:#fff;border-color:#2B2622}.wn button.on small{color:#ddd}.wn button.z{opacity:.45}'+
'.wn .wr{display:flex;align-items:center;gap:8px;margin-top:8px;flex-wrap:wrap}.wn .wsb{border-style:dashed}.wn .wsb.on{border-style:solid}'+
'.wn .wc{font-size:12.5px;line-height:1.5}.wn .wc b{font-size:14px}'+
'.wn .wsh{margin-top:10px;padding:12px;border:1px solid #DADADA;border-radius:14px;background:#fff;box-shadow:0 6px 18px rgba(0,0,0,.08)}'+
'.wn .wsh .wf{display:flex;flex-wrap:wrap;gap:6px}.wn .wsh .wb{display:flex;justify-content:space-between;align-items:center;margin-top:10px}'+
'.wn .wsh .wx{background:none;border:0;padding:6px 2px;text-decoration:underline;font-weight:500;font-size:12.5px}.wn .wsh .wok{background:#2B2622;color:#fff;border-color:#2B2622}'+
'.wn .wr .wcl{flex:0 0 auto;order:9;margin-left:auto;border:1px solid #D9D9DE;border-radius:999px;padding:4px 12px;font:700 12px "Zen Kaku Gothic New",sans-serif;color:#2B2622;background:#fff;cursor:pointer}'+
'.wn .wr .wx{background:none;border:0;padding:6px 2px;text-decoration:underline;font:500 12.5px "Zen Kaku Gothic New",sans-serif;color:#2B2622;cursor:pointer;flex:0 0 auto}'+
'.wn .wsh .wnt{margin:8px 2px 0;font-size:11px;color:#6E6E6E;line-height:1.6}'+
'.wsec{margin:0 0 8px}.wsec .wh{margin:18px 2px 8px;font:700 14px "Zen Kaku Gothic New",sans-serif;color:#2B2622}.wsec .wh b{font-size:15px}'+
'.wsec .wh span{display:block;font-weight:500;font-size:11.5px;color:#6E6E6E;margin-top:2px}'+
'.wsec .wsl .v2d,.wsec .wsl.v2d,.wsec .it.wsl .v2d{display:none!important}.wsec .it,.wsec .card.it{position:relative;display:block!important}.wsec .cdn{display:none!important}'+
'.wsec .wst{display:block;font:700 12px "Zen Kaku Gothic New",sans-serif;color:#1F7A4D;margin:4px 0 0}'+
'.wfav{position:absolute;right:12px;top:12px;width:30px;height:30px;border-radius:50%;border:1px solid #DADADA;background:#fff;font-size:14px;line-height:1;color:#2B2622;display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:2;padding:0}'+
'.wfav.on{background:#2B2622;color:#fff;border-color:#2B2622}'+
'.wsec .wmore{display:block;margin:4px auto 14px;background:none;border:0;border-bottom:1px solid #2B2622;padding:2px 2px 3px;font:13px "Zen Kaku Gothic New",sans-serif;color:#2B2622;cursor:pointer}'+
'.wz{margin:12px 0;padding:14px;border:1px dashed #CFCFCF;border-radius:12px;font:13px/1.7 "Zen Kaku Gothic New",sans-serif;color:#2B2622}'+
'.wz button{display:block;margin:8px 0 0;font:700 12.5px "Zen Kaku Gothic New",sans-serif;border:1px solid #2B2622;background:#fff;border-radius:999px;padding:6px 12px;color:#2B2622;cursor:pointer}'+
'.wn .wc b{white-space:nowrap}.wn .wr{flex-wrap:nowrap!important}.wn .wr .wc{flex:1 1 0;min-width:0;white-space:normal!important;overflow:visible!important;text-overflow:clip!important;line-height:1.35!important}.wn .wr .wsb{flex:0 0 auto}'+
'.wn .wd{display:flex!important;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;gap:6px;padding-bottom:2px}.wn .wd::-webkit-scrollbar{display:none}'+
'.wn .wd button{flex:0 0 auto;min-width:50px;padding:5px 8px!important;height:auto!important;line-height:1.15;text-align:center}.wn .wd button.wk2{min-width:78px}.wn .wd button small{display:block;margin:0;font-size:10px}'+
'.wn .wd button.sa{color:#3E6FA8}.wn .wd button.su{color:#C0584A}.wn .wd button.on{color:#fff}'+
'.wn .wkd{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;margin-top:8px;padding-bottom:2px}.wn .wkd::-webkit-scrollbar{display:none}'+
'.wn .wkd button{flex:0 0 auto;display:flex;align-items:center;gap:4px;padding:6px 11px}.wn .wkd button svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}'+
'.wn .wkd .wff{border-style:dashed}.wn .wkd .wff.on{border-style:solid}.wn .wks{flex:0 0 1px;background:#DADADA;margin:4px 2px}'+
'.pr5{margin:10px 0 16px;background:#fff;border:1px solid #E4E4E8;border-radius:14px;padding:12px 14px 6px}.pr5 .h{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}'+
'.pr5 .h b{font:700 15px "Zen Kaku Gothic New",sans-serif;color:#2B2622}.pr5 .h small{font-size:11px;color:#6E6E6E}'+
'.pr5 a{display:flex;align-items:center;gap:10px;padding:8px 0;border-top:1px solid #EFEFF2;text-decoration:none;color:#2B2622}.pr5 a:first-of-type{border-top:0}'+
'.pr5 .n{font:400 20px/1 Jost,sans-serif;width:18px;text-align:center;color:#C0584A}.pr5 .ti{flex:0 0 40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;background:color-mix(in srgb,var(--pc,#999) 14%,#fff)}'+
'.pr5 .ti svg{width:22px;height:22px;fill:none;stroke:var(--pc,#777);stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}.pr5 .tx{flex:1;min-width:0}'+
'.pr5 .tx b{display:block;font:700 13.5px "Zen Kaku Gothic New",sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.pr5 .tx span{font-size:11px;color:#6E6E6E}.pr5 .tx i{font-style:normal;font-weight:700;color:var(--pc,#777)}'+
'.wfw>.fold1{display:none}.wfw.fold>*:not(.fold1){display:none!important}.wfw.fold>.fold1{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 4px;font-size:13px;color:#55505A;cursor:pointer}.wfw.fold .fold1 b{color:#2B2622}.wfw.fold .fold1 em{font-style:normal;font-family:Jost,sans-serif;font-size:16px;color:#2B2622;margin-left:4px}.wfw.fold .fold1 span:last-child{border:1px solid #D9D9DE;border-radius:999px;padding:4px 12px;font-size:12px;font-weight:700;color:#2B2622;background:#fff}'+
'.tn-top .fold1{display:none}.tn-top.fold>*:not(.fold1){display:none!important}.tn-top.fold .fold1{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 14px;font-size:13px;color:#55505A;cursor:pointer}'+
'.tn-top.fold .fold1 b{color:#2B2622}.tn-top.fold .fold1 em{font-style:normal;font-family:Jost,sans-serif;font-size:16px;color:#2B2622;margin-left:4px}.tn-top.fold .fold1 span:last-child{border:1px solid #D9D9DE;border-radius:999px;padding:4px 12px;font-size:12px;font-weight:700;color:#2B2622;background:#fff}'+
'html.wmode .paper .blk.tb:not(:has(#wn)),html.wmode #none,html.wmode #odekake,html.wmode .v2tabs{display:none!important}'+
'html.wmode .paper .blk.tb:has(#wn){display:block!important}html.wmode .paper .blk.tb:has(#wn)>*:not(.tn-top):not(#wn):not(#wsec):not(.wk){display:none!important}html.wmode .paper .blk.tb:has(#wn)>.wk{display:none!important}';
document.head.appendChild(css);
var box=document.createElement("div");box.className="wn";box.id="wn";
var sec=document.createElement("div");sec.className="wsec";sec.id="wsec";
var anchor=AK?(F.nextElementSibling&&F.nextElementSibling.classList.contains("cnt")?F.nextElementSibling:F):(document.getElementById("none")||F);
anchor.parentNode.insertBefore(box,anchor.nextSibling);var top=box.closest('.tn-top');if(top)top.parentNode.insertBefore(sec,top.nextSibling);else box.parentNode.insertBefore(sec,box.nextSibling);
var sheetOpen=false,more={};
function btns(){var pf=curPref(),h='<div class="wl">いつ行く？</div><div class="wd">';
  DS.forEach(function(k){var n=count(k,st.f,pf),d0=D[k].d[0],w=dw(d0),c=(k.charAt(0)==="d"?(w===6?"sa":(w===0||HOL[d0])?"su":""):"")+(k==="we"||k==="nwe"?" wk2":"")+(st.d===k?" on":(n?"":" z")),sm=D[k].d.map(md).join("・");
   h+='<button type="button" data-d="'+k+'" class="'+c+'" aria-pressed="'+(st.d===k)+'">'+(k.charAt(0)==="d"?W[w]:D[k].l)+'<small>'+sm+'</small></button>';});
  h+='</div><div class="wkd"><button type="button" class="wff'+(st.f.free?' on':'')+'" data-f="free">無料</button><button type="button" class="wff'+(st.f.rain?' on':'')+'" data-f="rain">雨でもOK</button><button type="button" class="wff'+(st.f.kid?' on':'')+'" data-f="kid">子どもと</button><span class="wks"></span><button type="button" data-k=""'+(st.k?'':' class="on"')+'>すべての種類</button>';
  var kc={},ki={};ALL.forEach(function(o){var x=kindOf(o);if(!x)return;var k0=st.k;st.k="";if(pass(o,st.d,st.f,pf))kc[x]=1;st.k=k0;if(!ki[x]){var sv=o.w.querySelector(".ib svg");if(sv)ki[x]=sv.innerHTML;}});
  KO.forEach(function(x){if(!kc[x]&&st.k!==x)return;h+='<button type="button" data-k="'+x+'"'+(st.k===x?' class="on"':'')+'><svg viewBox="0 0 24 24">'+(ki[x]||"")+'</svg>'+KN[x]+'</button>';});
  h+='</div><div class="wr"><span class="wc"></span>'+(nf()||st.k?'<button type="button" class="wx">外す</button>':'')+'<button type="button" class="wcl">とじる ▴</button>'+'</div>';
  box.innerHTML=h;}
function stateLine(o,dk,short){var R=D[dk].d.filter(function(d){return d>=T;}),od=R.filter(function(d){return openOn(o,d);});
  if(o.s&&o.s===o.e)return mdw(o.s)+"の1日だけ";
  if(o.s&&o.e&&o.s>=R[0]&&o.e<=R[R.length-1]&&od.length>1)return od.map(function(d){return W[dw(d)];}).join("・")+"の"+od.length+"日だけ";
  if(!o.days&&o.e&&R.indexOf(o.e)>=0)return W[dw(o.e)]+"曜（"+md(o.e)+"）で終わります";
  if(od.length&&od.length<R.length)return od.map(mdw).join("・")+"だけ開催";
  if(o.e&&R.indexOf(o.e)>=0)return W[dw(o.e)]+"曜（"+md(o.e)+"）で終わります";
  if(o.s&&o.s>T&&R.indexOf(o.s)>=0)return mdw(o.s)+"から";
  if(short&&R.length>1)return "土・日とも開催";
  return "";}
function cl(o,dk,short){var c=o.w.cloneNode(true);c.removeAttribute("id");
  /* 11/7 夜のミス帳 #120 #121：写したカードに「宿・券を付けた」印が残り、券と近くの宿が出なかった → 印を外して付け直してもらう */
  c.removeAttribute("data-yk");[].forEach.call(c.querySelectorAll("[data-yk]"),function(e){e.removeAttribute("data-yk");});c.style.removeProperty("display");c.classList.remove("cap");
  var t=c.querySelector(".t"),s=dk==="all"?"":stateLine(o,dk,short);if(t&&s){var x=document.createElement("span");x.className="wst";x.textContent="● "+s;t.parentNode.insertBefore(x,t.nextSibling);c.classList.add("wsl");}else c.classList.add("wsl");
  if(o.href){var f=document.createElement("button");f.type="button";f.className="wfav"+(FAV[o.href]?" on":"");f.setAttribute("aria-label",(FAV[o.href]?"保存を外す":"行きたい所に保存"));f.textContent=FAV[o.href]?"★":"☆";f.dataset.h=o.href;c.appendChild(f);}
  return c;}
function group(list,key,head,sub,dk,short){if(!list.length)return;var h=document.createElement("div");h.className="wh";h.innerHTML=head+' <b>'+list.length+'件</b><span>'+sub+'</span>';sec.appendChild(h);
  list.forEach(function(o,i){if(i>=5&&!more[key])return;sec.appendChild(cl(o,dk,short));});
  if(list.length>5&&!more[key]){var m=document.createElement("button");m.type="button";m.className="wmore";m.dataset.k=key;m.textContent="もっと見る（あと"+(list.length-5)+"件）";sec.appendChild(m);}}
function byE(a,b){var x=a.e||"9999",y=b.e||"9999";return x<y?-1:x>y?1:0;}
function render(){setTimeout(function(){if(window.ykRun)window.ykRun();},0);var pf=curPref();btns();var wc=box.querySelector(".wc");
  var LM=st.d!=="all"||!!st.f.fav;document.documentElement.classList.toggle("wmode",LM);if(LM)[].forEach.call(document.querySelectorAll("#v2bar button[data-t]"),function(b){b.classList.remove("cur");});sec.innerHTML="";sec.hidden=!LM;favBar();
  if(!LM){wc.textContent="";syncUrl();return;}
  /* 11/9 下のバー「行きたい」：☆で残した所を、日付で選ばずに全部見せる */
  if(st.d==="all"){var LF=ALL.filter(function(o){return pass(o,"all",st.f,pf);}).sort(byE);wc.innerHTML="☆で残した所 <b>"+LF.length+"件</b>";
   if(!LF.length){var z0=document.createElement("div");z0.className="wz";z0.innerHTML="<b>まだ☆で残した所はありません。</b><br>カードの右上の☆を押すと、ここに集まります。<button type=\"button\" data-zd=\"we\">この週末のおでかけを見る</button>";sec.appendChild(z0);syncUrl();return;}
   group(LF,"f","☆で残した所","この端末に残っています。終わりが近い順","all",false);syncUrl();return;}
  var L=ALL.filter(function(o){return pass(o,st.d,st.f,pf);}),dd=D[st.d].d.filter(function(d){return d>=T;}).map(function(d,i,a){return i&&a[i-1].slice(5,7)===d.slice(5,7)?String(+d.slice(8)):md(d);}).join("・"),lab=st.d.charAt(0)==="d"?D[st.d].l:D[st.d].l+"（"+dd+"）";
  var fl=Object.keys(st.f).map(function(k){return FL[k];});if(st.k)fl.unshift(KN[st.k]);
  wc.innerHTML="<b>"+L.length+"件</b> 見つかりました";
  if(!L.length){var z=document.createElement("div");z.className="wz";var h='<b>この条件の所は、'+(pf?pf+"の":"")+lab+'にはありません。</b><br>押すと広がります：',any=0;
   DK.forEach(function(k){if(k===st.d)return;var n=count(k,st.f,pf);if(n){h+='<button type="button" data-zd="'+k+'">'+D[k].l+'にする（'+n+'件）</button>';any=1;}});
   Object.keys(st.f).forEach(function(k){var f2={};for(var x in st.f)if(x!==k)f2[x]=1;var n=count(st.d,f2,pf);if(n){h+='<button type="button" data-zf="'+k+'">「'+FL[k]+'」を外す（'+n+'件）</button>';any=1;}});
   if(pf){var n2=count(st.d,st.f,"");if(n2){h+='<button type="button" data-zp="1">府県を「すべて」にする（'+n2+'件）</button>';any=1;}}
   if(!any)h+='<button type="button" data-zd="all">日付で選ばずに見る</button>';
   z.innerHTML=h;sec.appendChild(z);syncUrl();return;}
  if(st.d==="we"&&!st.k&&!nf()&&L.length>5){var P5=L.slice().sort(function(a,b){return ((a.free?0:1)-(b.free?0:1))||byE(a,b);}),pk=[],UP={},UK={};
   P5.forEach(function(o){if(pk.length<5&&!UP[o.pref]&&!UK[kindOf(o)]){UP[o.pref]=UK[kindOf(o)]=1;pk.push(o);}});P5.forEach(function(o){if(pk.length<5&&pk.indexOf(o)<0&&!UP[o.pref]){UP[o.pref]=1;pk.push(o);}});P5.forEach(function(o){if(pk.length<5&&pk.indexOf(o)<0)pk.push(o);});
   var bx=document.createElement("div");bx.className="pr5";var hh='<div class="h"><b>今週末のおすすめ5</b><small>毎日更新</small></div>';
   pk.forEach(function(o,i){var sv=o.w.querySelector(".ib svg"),dd=o.w.querySelector(".dd"),pc=(o.w.getAttribute("style")||"").match(/--pc:\s*([^;]+)/);
    hh+='<a href="'+o.href+'" target="_blank" rel="noopener"'+(pc?' style="--pc:'+pc[1]+'"':'')+'><span class="n">'+(i+1)+'</span><span class="ti">'+(sv?sv.outerHTML:"")+'</span><span class="tx"><b>'+title(o.w)+'</b><span><i>'+(o.pref||"")+'</i>・'+(dd?dd.textContent.trim():mdw(o.e||T))+'</span></span></a>';});
   bx.innerHTML=hh;sec.appendChild(bx);}
  var S=L.filter(isShort).sort(byE),G=L.filter(function(o){return !isShort(o);}).sort(byE);
  group(S,"s","日にちの決まった催し",lab+"に開催。期間が短いので、先に見ておくと行きのがしません",st.d,true);
  group(G,"g","長く開いている所","紅葉・イルミ・展覧会など。"+(D[st.d].d.length>1?"どちらの日でも行けます":"この日も開いています"),st.d,false);
  syncUrl();if(window.__wfold)window.__wfold();}
box.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;
  if(b.dataset.k!==undefined){st.k=b.dataset.k;if(st.d==="all")st.d="we";more={};render();up();try{c("種類："+(KN[st.k]||"すべて"));}catch(x){}}
  else if(b.dataset.d){if(st.d==="all"&&st.f.fav)delete st.f.fav;st.d=st.d===b.dataset.d?"all":b.dataset.d;more={};render();up();try{c("日付："+D[b.dataset.d].l);}catch(x){}}
  else if(b.classList.contains("wsb")){sheetOpen=!sheetOpen;btns();render();}
  else if(b.dataset.f){if(st.f[b.dataset.f])delete st.f[b.dataset.f];else st.f[b.dataset.f]=1;if(st.d==="all")st.d="we";more={};render();if(b.classList.contains("wff"))up();try{c("しぼりこみ："+FL[b.dataset.f]);}catch(x){}}
  else if(b.classList.contains("wcl")){if(window.__wfoldNow)window.__wfoldNow();}
  else if(b.classList.contains("wx")){st.f={};st.k="";more={};render();}
  else if(b.classList.contains("wok")){sheetOpen=false;render();var y=sec.getBoundingClientRect().top+scrollY-90;scrollTo({top:Math.max(0,y),behavior:"smooth"});}});
sec.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;
  if(b.classList.contains("wfav")){e.preventDefault();e.stopPropagation();var h=b.dataset.h;if(FAV[h])delete FAV[h];else FAV[h]=1;saveFav();
   [].forEach.call(sec.querySelectorAll('.wfav'),function(x){if(x.dataset.h===h){x.classList.toggle("on",!!FAV[h]);x.textContent=FAV[h]?"★":"☆";x.setAttribute("aria-label",FAV[h]?"保存を外す":"行きたい所に保存");}});
   favBar();if(st.f.fav&&!FAV[h])render();else btns();return;}
  if(b.classList.contains("wmore")){more[b.dataset.k]=1;render();return;}
  if(b.dataset.zd){if(st.d==="all")delete st.f.fav;st.d=b.dataset.zd;render();}else if(b.dataset.zf){delete st.f[b.dataset.zf];render();}else if(b.dataset.zp){var a=F.querySelector("button");if(a)a.click();}});
F.addEventListener("click",function(e){var pb=e.target.closest&&e.target.closest("button");setTimeout(function(){more={};render();if(pb){try{localStorage.setItem("tn_pref"+(AK?"_k":""),pb.textContent.trim());}catch(x){}up();}},0);});
function up(){var tp=box.closest(".tn-top"),y=sec.getBoundingClientRect().top+scrollY-(tp?tp.offsetHeight:0)-8;if(scrollY>y+4)scrollTo({top:Math.max(0,y),behavior:"smooth"});}
/* 11/10 #101 #165：地図から ?pref= で来たら、その府県を先に当てる（保存した府県より先） */
var QP=q.get("pref")||"";if(QP){var qb=[].filter.call(F.querySelectorAll("button"),function(x){return x.textContent.trim()===QP||x.getAttribute("data-p")===QP;})[0];if(qb&&!qb.classList.contains("on"))setTimeout(function(){qb.click();},0);}
try{var sp=localStorage.getItem("tn_pref"+(AK?"_k":""));var on0=F.querySelector("button.on");if(sp&&sp!=="すべて"&&!QP&&!(on0&&on0!==F.querySelector("button")))[].forEach.call(F.querySelectorAll("button"),function(b){if(b.textContent.trim()===sp&&!b.classList.contains("on"))setTimeout(function(){b.click();},0);});}catch(e){}
window.addEventListener("load",function(){setTimeout(function(){if(!sheetOpen)render();},400);});
/* 11/10 オーナー「初めから出てるんじゃなくてスッキリ」：選ぶ欄は最初たたんで1行。押すと開く。開いた後も下に読むとまたたたむ */
(function(){var tp=box.closest(".tn-top");if(!tp){tp=document.createElement("div");tp.className="wfw";box.parentNode.insertBefore(tp,box);tp.appendChild(box);}var f1=document.createElement("div");f1.className="fold1";tp.appendChild(f1);var ly=scrollY,oy=0;
 function lab(){var pf=curPref()||(AK?"関東":"関西"),c0=box.querySelector(".wc b"),fl=Object.keys(st.f).map(function(k){return FL[k];});if(st.k)fl.unshift(KN[st.k]);
  f1.innerHTML='<span><b>'+pf+'・'+(st.d==="all"?"☆":D[st.d].l)+(fl.length?"・"+fl.join("・"):"")+'</b><em>'+(c0?c0.textContent:"")+'</em></span><span>えらぶ ▾</span>';}
 function fold(){lab();tp.classList.add("fold");}
 window.__wfoldNow=fold;window.__wfold=function(){if(tp.classList.contains("fold"))lab();};
 fold();
 addEventListener("scroll",function(){var y=scrollY;if(!tp.classList.contains("fold")&&y>oy+240&&y>ly+4)fold();ly=y;},{passive:true});
 f1.addEventListener("click",function(){tp.classList.remove("fold");oy=scrollY;});})();
/* 下のバーの「開催中」「これから」は、日付で選ばない一覧（タブ）にもどす */
document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("#v2bar button[data-t]");if(b&&st.d!=="all"){st.d="all";render();}},true);
/* 11/9 オーナーOK（見本⑤）：下のバーの「開催中」「これから」→「さがす」「行きたい（☆の数）」 */
var IS='<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg>',IF='<svg viewBox="0 0 24 24"><path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8L3.5 9.7l5.9-.9z"/></svg>';
function favBar(){var b=document.querySelector('#v2bar [data-a="fav"]');if(!b)return;var n=Object.keys(FAV).length,i=b.querySelector("b");if(!i){i=document.createElement("b");i.className="fvn";b.appendChild(i);}i.textContent=n;i.hidden=!n;b.classList.toggle("cur",!!st.f.fav&&st.d==="all");}
function fixBar(){var bar=document.getElementById("v2bar");if(!bar)return false;if(bar.querySelector('[data-a="find"]'))return true;
  var t=bar.querySelectorAll("button[data-t]");if(t.length<2)return true;
  var f1=document.createElement("button");f1.type="button";f1.dataset.a="find";f1.innerHTML=IS+"<span>さがす</span>";
  var f2=document.createElement("button");f2.type="button";f2.dataset.a="fav";f2.innerHTML=IF+"<span>行きたい</span>";
  t[0].parentNode.replaceChild(f1,t[0]);t[1].parentNode.replaceChild(f2,t[1]);
  var cs=document.createElement("style");cs.textContent='#v2bar [data-a=fav]{position:relative}#v2bar .fvn{position:absolute;top:4px;left:56%;font:500 9.5px Jost,sans-serif;background:#B0705A;color:#fff;border-radius:999px;padding:1px 5px;line-height:1.3}';document.head.appendChild(cs);
  bar.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;
   if(b.dataset.a==="find"){e.stopImmediatePropagation();if(st.f.fav&&st.d==="all"){delete st.f.fav;st.d="we";render();}var y=F.getBoundingClientRect().top+scrollY-12;scrollTo({top:Math.max(0,y),behavior:"smooth"});try{c("下のバー：さがす");}catch(x){}}
   else if(b.dataset.a==="fav"){e.stopImmediatePropagation();st.f={fav:1};st.d="all";sheetOpen=false;more={};render();var tp=box.closest(".tn-top"),y2=sec.getBoundingClientRect().top+scrollY-(tp?tp.offsetHeight:0)-8;scrollTo({top:Math.max(0,y2),behavior:"smooth"});try{c("下のバー：行きたい");}catch(x){}}},true);
  favBar();return true;}
if(!fixBar()){var tries=0,iv=setInterval(function(){if(fixBar()||++tries>40)clearInterval(iv);},150);}
render();
})();
