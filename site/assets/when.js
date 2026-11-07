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
  if(r==="sat")return dw(d)===6;if(r==="sun")return dw(d)===0;if(r==="we")return dw(d)===0||dw(d)===6||!!HOL[d];return r.split(",").indexOf(d)>=0;}
function inRange(o,dk){return D[dk].d.some(function(d){return d>=T&&openOn(o,d);});}
function isShort(o){if(!o.s||!o.e)return false;return (Date.parse(o.e)-Date.parse(o.s))/864e5<=14||(o.days&&o.days.indexOf(",")>0);}
function curPref(){var b=F.querySelector("button.on");if(!b)return "";var p=AK?(b.getAttribute("data-p")||""):b.textContent.trim();return p==="すべて"?"":p;}
/* 状態 */
var q=new URLSearchParams(location.search),st={d:q.get("d")||(q.get("v2t")?"all":"we"),f:{}};
if(DK.indexOf(st.d)<0&&st.d!=="all")st.d="we";(q.get("f")||"").split(",").forEach(function(k){if(FL[k])st.f[k]=1;});
function pass(o,dk,f,pf){if(pf&&o.pref!==pf)return false;if(dk!=="all"&&!inRange(o,dk))return false;
  for(var k in f){if(k==="fav"){if(!FAV[o.href])return false;}else if(!o[k])return false;}return true;}
function count(dk,f,pf){var n=0;ALL.forEach(function(o){if(pass(o,dk,f,pf))n++;});return n;}
function nf(){return Object.keys(st.f).length;}
function syncUrl(){try{var u=new URLSearchParams(location.search);u.delete("v2t");if(st.d==="we")u.delete("d");else u.set("d",st.d);var fk=Object.keys(st.f);if(fk.length)u.set("f",fk.join(","));else u.delete("f");
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
'html.wmode .paper .blk.tb:not(:has(#wn)),html.wmode #none,html.wmode #odekake,html.wmode .v2tabs{display:none!important}'+
'html.wmode .paper .blk.tb:has(#wn){display:block!important}html.wmode .paper .blk.tb:has(#wn)>*:not(.tn-top):not(#wn):not(#wsec):not(.wk){display:none!important}html.wmode .paper .blk.tb:has(#wn)>.wk{display:none!important}';
document.head.appendChild(css);
var box=document.createElement("div");box.className="wn";box.id="wn";
var sec=document.createElement("div");sec.className="wsec";sec.id="wsec";
var anchor=AK?(F.nextElementSibling&&F.nextElementSibling.classList.contains("cnt")?F.nextElementSibling:F):(document.getElementById("none")||F);
anchor.parentNode.insertBefore(box,anchor.nextSibling);var top=box.closest('.tn-top');if(top)top.parentNode.insertBefore(sec,top.nextSibling);else box.parentNode.insertBefore(sec,box.nextSibling);
var sheetOpen=false,more={};
function btns(){var pf=curPref(),h='<div class="wl">いつ行く？</div><div class="wd">';
  DK.forEach(function(k){var n=count(k,st.f,pf);h+='<button type="button" data-d="'+k+'"'+(st.d===k?' class="on"':(n?'':' class="z"'))+' aria-pressed="'+(st.d===k)+'">'+D[k].l+'<small>'+n+'</small></button>';});
  h+='</div><div class="wr"><button type="button" class="wsb'+(nf()||sheetOpen?' on':'')+'" aria-expanded="'+sheetOpen+'">＋ しぼりこむ'+(nf()?'（'+nf()+'）':'')+'</button><span class="wc"></span></div>';
  h+='<div class="wsh"'+(sheetOpen?'':' hidden')+'><div class="wl">しぼりこむ（いくつでも）</div><div class="wf">';
  FK.forEach(function(k){var f2={};for(var x in st.f)f2[x]=1;f2[k]=1;var n=count(st.d,f2,pf);if(k==="fav"&&!Object.keys(FAV).length&&!st.f.fav)return;
   h+='<button type="button" data-f="'+k+'"'+(st.f[k]?' class="on"':'')+' aria-pressed="'+!!st.f[k]+'">'+FL[k]+'<small>'+n+'</small></button>';});
  h+='</div><p class="wnt">「子どもと」「雨でも（屋内）」は、公式ページを見て選んだ所です。☆はこの端末だけに残ります。</p><div class="wb"><button type="button" class="wx">外す</button><button type="button" class="wok">この条件で見る（'+count(st.d,st.f,pf)+'件）</button></div></div>';
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
  var t=c.querySelector(".t"),s=stateLine(o,dk,short);if(t&&s){var x=document.createElement("span");x.className="wst";x.textContent="● "+s;t.parentNode.insertBefore(x,t.nextSibling);c.classList.add("wsl");}
  if(o.href){var f=document.createElement("button");f.type="button";f.className="wfav"+(FAV[o.href]?" on":"");f.setAttribute("aria-label",(FAV[o.href]?"保存を外す":"行きたい所に保存"));f.textContent=FAV[o.href]?"★":"☆";f.dataset.h=o.href;c.appendChild(f);}
  return c;}
function group(list,key,head,sub,dk,short){if(!list.length)return;var h=document.createElement("div");h.className="wh";h.innerHTML=head+' <b>'+list.length+'件</b><span>'+sub+'</span>';sec.appendChild(h);
  list.forEach(function(o,i){if(i>=5&&!more[key])return;sec.appendChild(cl(o,dk,short));});
  if(list.length>5&&!more[key]){var m=document.createElement("button");m.type="button";m.className="wmore";m.dataset.k=key;m.textContent="もっと見る（あと"+(list.length-5)+"件）";sec.appendChild(m);}}
function byE(a,b){var x=a.e||"9999",y=b.e||"9999";return x<y?-1:x>y?1:0;}
function render(){setTimeout(function(){if(window.ykRun)window.ykRun();},0);var pf=curPref();btns();var wc=box.querySelector(".wc");
  document.documentElement.classList.toggle("wmode",st.d!=="all");if(st.d!=="all")[].forEach.call(document.querySelectorAll("#v2bar button[data-t]"),function(b){b.classList.remove("cur");});sec.innerHTML="";sec.hidden=st.d==="all";
  if(st.d==="all"){wc.textContent="";syncUrl();return;}
  var L=ALL.filter(function(o){return pass(o,st.d,st.f,pf);}),dd=D[st.d].d.filter(function(d){return d>=T;}).map(function(d,i,a){return i&&a[i-1].slice(5,7)===d.slice(5,7)?String(+d.slice(8)):md(d);}).join("・"),lab=D[st.d].l+"（"+dd+"）";
  var fl=Object.keys(st.f).map(function(k){return FL[k];});
  wc.innerHTML=(pf?pf+"で":"")+lab+"に行ける所"+(fl.length?"（"+fl.join("・")+"）":"")+" <b>"+L.length+"件</b>";
  if(!L.length){var z=document.createElement("div");z.className="wz";var h='<b>この条件の所は、'+(pf?pf+"の":"")+lab+'にはありません。</b><br>押すと広がります：',any=0;
   DK.forEach(function(k){if(k===st.d)return;var n=count(k,st.f,pf);if(n){h+='<button type="button" data-zd="'+k+'">'+D[k].l+'にする（'+n+'件）</button>';any=1;}});
   Object.keys(st.f).forEach(function(k){var f2={};for(var x in st.f)if(x!==k)f2[x]=1;var n=count(st.d,f2,pf);if(n){h+='<button type="button" data-zf="'+k+'">「'+FL[k]+'」を外す（'+n+'件）</button>';any=1;}});
   if(pf){var n2=count(st.d,st.f,"");if(n2){h+='<button type="button" data-zp="1">府県を「すべて」にする（'+n2+'件）</button>';any=1;}}
   if(!any)h+='<button type="button" data-zd="all">日付で選ばずに見る</button>';
   z.innerHTML=h;sec.appendChild(z);syncUrl();return;}
  var S=L.filter(isShort).sort(byE),G=L.filter(function(o){return !isShort(o);}).sort(byE);
  group(S,"s","日にちの決まった催し",lab+"に開催。期間が短いので、先に見ておくと行きのがしません",st.d,true);
  group(G,"g","長く開いている所","紅葉・イルミ・展覧会など。"+(D[st.d].d.length>1?"どちらの日でも行けます":"この日も開いています"),st.d,false);
  syncUrl();}
box.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;
  if(b.dataset.d){st.d=st.d===b.dataset.d?"all":b.dataset.d;more={};render();try{c("日付："+D[b.dataset.d].l);}catch(x){}}
  else if(b.classList.contains("wsb")){sheetOpen=!sheetOpen;btns();render();}
  else if(b.dataset.f){if(st.f[b.dataset.f])delete st.f[b.dataset.f];else st.f[b.dataset.f]=1;if(st.d==="all")st.d="we";more={};render();try{c("しぼりこみ："+FL[b.dataset.f]);}catch(x){}}
  else if(b.classList.contains("wx")){st.f={};more={};render();}
  else if(b.classList.contains("wok")){sheetOpen=false;render();var y=sec.getBoundingClientRect().top+scrollY-90;scrollTo({top:Math.max(0,y),behavior:"smooth"});}});
sec.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;
  if(b.classList.contains("wfav")){e.preventDefault();e.stopPropagation();var h=b.dataset.h;if(FAV[h])delete FAV[h];else FAV[h]=1;saveFav();
   [].forEach.call(sec.querySelectorAll('.wfav'),function(x){if(x.dataset.h===h){x.classList.toggle("on",!!FAV[h]);x.textContent=FAV[h]?"★":"☆";x.setAttribute("aria-label",FAV[h]?"保存を外す":"行きたい所に保存");}});
   if(st.f.fav&&!FAV[h])render();else btns();return;}
  if(b.classList.contains("wmore")){more[b.dataset.k]=1;render();return;}
  if(b.dataset.zd){st.d=b.dataset.zd;render();}else if(b.dataset.zf){delete st.f[b.dataset.zf];render();}else if(b.dataset.zp){var a=F.querySelector("button");if(a)a.click();}});
F.addEventListener("click",function(){setTimeout(function(){more={};render();},0);});
/* 下のバーの「開催中」「これから」は、日付で選ばない一覧（タブ）にもどす */
document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("#v2bar button[data-t]");if(b&&st.d!=="all"){st.d="all";render();}},true);
render();
})();
