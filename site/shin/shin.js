/* 新しいHP（11/19）の共通の土台：空（昼の日差し・夜の星）・頭（ロゴ・昼夜）・下のバー・MENU・下から出る板・数え上がり。
   どのページも同じ物を読む。ページの中身は各ページの JS（odekake.js・ie.js …）が #main に作る。
   決まり：普通の役目＋こだわり1つ。動かすのは transform と opacity だけ。 */
(function(){
"use strict";
/* 11/20 19:20 見た目の見本 ?look=a|b|c（この端末で覚える・?look=0 で外す）→ look.css・look.js */
try{if(localStorage.getItem("tn_ty2")!=="0"&&!/[?&]ty=0/.test(location.search))document.documentElement.classList.add("lk-t1")}catch(e){}try{var _lk=location.search.match(/[?&]look=([abcdef0])/);if(_lk)localStorage.setItem("tn_lk2",_lk[1]);var _lv=localStorage.getItem("tn_lk2")||"f";if(_lv&&_lv!=="0"&&!document.getElementById("lkcss")){document.documentElement.classList.add("lk","lk-"+_lv);if(_lv==="d"||_lv==="e"||_lv==="f")document.documentElement.classList.add("lk-a","lk-d");if(_lv==="f")document.documentElement.classList.add("lk-e");var _l=document.createElement("link");_l.rel="stylesheet";_l.href="/shin/look.css?v=28";document.head.appendChild(_l);var _s=document.createElement("script");_s.src="/shin/look.js?v=28";_s.defer=true;document.head.appendChild(_s)}}catch(e){}
var H=document.documentElement,app=document.getElementById("app");
/* 11/20 owner「いいと思う」：分野ごとの色の線（iro）をふだんの見た目に。?iro=0 で外せる（この端末で覚える） */
try{var _q=location.search.match(/[?&]iro=([01])/);if(_q)localStorage.setItem("tn_iro",_q[1]);if(localStorage.getItem("tn_iro")!=="0"){var _p=location.pathname,_f=/^\/(shin\/cover\d?)?$|^\/index/.test(_p)?"top":/kaiten/.test(_p)?"kai":/okaimono|furusato|nesage|otoku|tanka|kaimawari|shin\/kau/.test(_p)?"kau":/fudosan|ikura|uru|ranking|machi|jikka|chika|akiya|kaitai|sagasu|moushikomi|gyosha|koe|shin\/ie/.test(_p)?"ie":"od";document.documentElement.classList.add("iro");document.documentElement.setAttribute("data-f",_f)}}catch(e){}
var CFG=JSON.parse(document.getElementById("cfg").textContent);
/* 11/20 owner「不動産・実家・空き家 ごっちゃになる・バラバラすぎる 整理して」：家と土地のページを3つの目的に分ける。
   上＝3つの目的の切りかえ（街の相場／売る・買う／実家・空き家）、下のバー＝今の目的のページだけ、MENU＝3つの見出しで全部。
   関西・関東とも同じ物（関東に無いページ＝まちランキング は出さない。相談は 11/10 から関東も同じ）。
   11/20 17:14 owner「月に任せる・他社と比べて勝つ」→ ふだんの見た目に（?seiri=0 でこの端末だけ前の形）。 */
function ieOrg(P,kt){
  var on=false;try{var q=location.search.match(/[?&]seiri=([01])/);if(q)localStorage.setItem("tn_seiri",q[1]);on=localStorage.getItem("tn_seiri")!=="0"}catch(e){}
  if(!on)return null;
  var p=P.replace(/\.html$/,"").replace(/\/index$/,"/");
  if(!/^\/(fudosan-list|machi\/|chika-|ranking|uru|ikura|sagasu|moushikomi|gyosha|fudosan$|jikka|kaitai|akiya|shindan)/.test(p))return null;
  var I={find:'<path d="M3 21h18M5 21V9l7-5 7 5v12"/><path d="M9.5 21v-6h5v6"/>',
   rank:'<path d="M5 20V11M12 20V5M19 20v-6"/>',pin:'<path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/>',star:'<path d="M12 4l2.4 5 5.4.6-4 3.7 1.1 5.3L12 16l-4.9 2.6 1.1-5.3-4-3.7 5.4-.6z"/>',
   sell:'<path d="M3 12l9-8 9 8"/><path d="M6 10v10h12V10"/><path d="M10 15h4"/>',
   tag:'<path d="M3.5 12.2V4.5a1 1 0 0 1 1-1h7.7l8.6 8.6a1.2 1.2 0 0 1 0 1.7l-7 7a1.2 1.2 0 0 1-1.7 0z"/><circle cx="8" cy="8" r="1.6"/>',
   key:'<circle cx="8" cy="15" r="4.2"/><path d="M11 12l8.5-8.5M16.5 6.5l2.5 2.5M14 9l2 2"/>',
   chat:'<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
   note:'<path d="M6 3.5h10l3 3V20.5H6z"/><path d="M9 10h7M9 13.5h7M9 17h4"/>',
   check:'<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8 12.5l2.7 2.7L16.5 9"/>',
   calc:'<rect x="5" y="3" width="14" height="18" rx="2.5"/><path d="M8 7.5h8M8.5 12h0M12 12h0M15.5 12h0M8.5 16h0M12 16h0M15.5 16h0"/>',
   gift:'<rect x="4" y="9" width="16" height="11" rx="1.5"/><path d="M3 9h18M12 9v11M12 9c-1.5-3-5-4-5-1.5S10 9 12 9zm0 0c1.5-3 5-4 5-1.5S14 9 12 9z"/>',
   box:'<path d="M3.5 8l8.5-4 8.5 4v9l-8.5 4-8.5-4z"/><path d="M3.5 8l8.5 4 8.5-4M12 12v9"/>',
   home:'<path d="M4 11l8-6 8 6v9H4z"/><path d="M9 20v-4.5h6V20"/><path d="M15.5 6.5V4h2v4"/>'};
  /* 17:27 owner「こんな項目いっぱいいるかな？一緒に出来るやつもある」→ 13を7つに（18:28 owner「片付けだけの反響あるかも」→ 片付けを名前に出し、片付けだけの見積りを足して8つ）。ページの中から行ける物（近くの街＝街をさがすのボタン・
     売る前に＝いくら？の中・診断と空き家の多い街＝実家・空き家の中・補助金ランキング＝解体の中）は並べない。まちランキング（駅・人口）は家と土地の並びから外す（ページの下のバーは同じ4つ）。 */
  var G=[{t:"街の相場",i:[["街の値段と地価","街をさがす","find","/fudosan-list"],["地価ランキング","地価","rank",kt?"/chika-kanto":"/chika-kansai"]]},
   {t:"売る・買う",i:[["いくらで売れる？","いくら？","tag","/ikura"],["家を買いたい","買いたい","key","/sagasu"],["無料の相談","相談する","chat","/moushikomi"]]},
   {t:"実家・空き家",i:[["実家・空き家","実家・空き家","note","/jikka/"],["片付け・解体の費用と補助金","解体","calc","/kaitai"],["片付け・遺品整理の無料見積り","片付け","box","/moushikomi?want=%E7%89%87%E4%BB%98%E3%81%91%E3%83%BB%E9%81%BA%E5%93%81%E6%95%B4%E7%90%86%E3%81%AE%E8%A6%8B%E7%A9%8D%E3%82%8A"]]}];
  var want="";try{want=new URLSearchParams(location.search).get("want")||""}catch(e){}
  var g=/^\/(jikka|kaitai|akiya|shindan)/.test(p)||(/^\/moushikomi/.test(p)&&/片付|解体|実家|空き家/.test(want))?2:/^\/(uru|ikura|sagasu|moushikomi|gyosha|fudosan$)/.test(p)?1:0;
  var cu=/^\/(jikka|shindan|akiya)/.test(p)?"/jikka/":/^\/machi\//.test(p)?"/fudosan-list":/^\/kaitai/.test(p)?"/kaitai":/^\/chika-/.test(p)?(kt?"/chika-kanto":"/chika-kansai"):/^\/uru/.test(p)?"/ikura":p;
  var svg=function(k){return '<svg viewBox="0 0 24 24">'+I[k]+'</svg>'};
  /* 11/20 17:25 owner「めっちゃ使いにくい」「何をするにもたどり着くには経由がいる」：上の切りかえと、目的ごとに変わる下のバーで
     行き先が2重・どこでも違う形だった → 上の切りかえは消す。下のバーはどの家と土地のページでも同じ4つ（よく使う行き先へ1回）。
     そのほかは入口（/fudosan-list）に全部並べる＋MENU。 */
  var ja=cu==="/jikka/"||cu==="/kaitai";
  var bi=[["街をさがす","find","/fudosan-list",cu==="/fudosan-list"],["いくら？","tag","/ikura",cu==="/ikura"],["実家・空き家","note","/jikka/",ja],["相談する","chat","/moushikomi",cu==="/moushikomi"&&!ja]];
  var nav=bi.map(function(x){return {t:x[0],ic:x[1],svg:svg(x[1]),href:x[2],cur:x[3]}});
  var menu=[];G.forEach(function(x){x.i.forEach(function(y){menu.push([y[0],y[3]].concat(y[3]===cu?[1]:[]))})});
  return {g:g,seg:"",nav:nav,menu:menu,G:G};
}
/* MENU の並び：["#","見出し"] は見出しの行（番号は数えない） */
function muList(items){var n=0;return items.map(function(m){if(m[1]==="#")return '<li class="mg">'+m[0]+'</li>';n++;return '<li><a href="'+m[1]+'"'+(m[2]?' class="here"':'')+' style="transition-delay:'+(60+n*30)+'ms"><small>'+(n<10?'0':'')+n+'</small>'+m[0]+'</a></li>'}).join("")}
var IEO=ieOrg(location.pathname,(CFG.reg&&CFG.reg.n==="関東")||/kanto|lifenote|life-note|usagi-life/.test(location.hostname));
if(IEO){var _fa=(CFG.nav||[]).filter(function(n){return n.a==="find"})[0];CFG.nav=IEO.nav.map(function(n){return _fa&&n.href==="/fudosan-list"&&n.cur?{t:n.t,svg:n.svg,a:"find",cur:1}:_fa&&n.href==="/fudosan-list?geo=1"?{t:n.t,svg:n.svg,a:"geo"}:n});CFG.menu.items=IEO.menu;window.TN_IEG=IEO.G;document.documentElement.classList.add("ieo")}
/* 11/19 関東も同じ土台で作る：地域の違い（名前・府県・色・地図・ロゴ）は CFG.reg。無ければ関西 */
var REG=CFG.reg||{n:"関西",brand:"TOWN NOTE",logo:"/assets/logo-s.png?v=2",logon:"/assets/logo-s-night.png",pref:["大阪","京都","兵庫","奈良","滋賀","和歌山"],pfs:"大阪・京都・兵庫・奈良・滋賀・和歌山",pc:{"大阪":"#D9775A","京都":"#9C7BB8","兵庫":"#4F86C6","奈良":"#5FA06A","滋賀":"#3FA3B5","和歌山":"#E09A3E"},fl:{"大阪":"#F7D9CC","京都":"#E6DBF1","兵庫":"#D6E4F5","奈良":"#D8ECD4","滋賀":"#D0EBEF","和歌山":"#F8E4C4"},lb:{"兵庫":[62,105],"京都":[122,78],"滋賀":[176,92],"大阪":[118,165],"奈良":[156,178],"和歌山":[118,215]},sl:{"大阪":"osaka","京都":"kyoto","兵庫":"hyogo","奈良":"nara","滋賀":"shiga","和歌山":"wakayama"},vb:"10 15 200 250"};
var RM=matchMedia("(prefers-reduced-motion:reduce)").matches;
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
function el(h){var t=document.createElement("template");t.innerHTML=h.trim();return t.content.firstChild}
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
var now=new Date(Date.now()+9*36e5),TD=now.toISOString().slice(0,10),seed=+TD.replace(/-/g,"");
var WD="日月火水木金土";
function dd(s){return new Date(s+"T00:00:00Z")}
function diff(a,b){return Math.round((dd(b)-dd(a))/864e5)}
function md(s){var d=dd(s);return (d.getUTCMonth()+1)+"/"+d.getUTCDate()+"（"+WD[d.getUTCDay()]+"）"}
var IC={sun:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/></svg>',
 moon:'<svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg>',
 now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',
 we:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',
 map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',
 inn:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>',
 find:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/></svg>',
 rank:'<svg viewBox="0 0 24 24"><path d="M5 20V11M12 20V5M19 20v-6"/></svg>',
 sell:'<svg viewBox="0 0 24 24"><path d="M3 12l9-8 9 8"/><path d="M6 10v10h12V10"/><path d="M10 15h4"/></svg>',
 buy:'<svg viewBox="0 0 24 24"><path d="M4 7h16l-1.5 11.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg>',
 yen:'<svg viewBox="0 0 24 24"><path d="M3.5 12.2V4.5a1 1 0 0 1 1-1h7.7l8.6 8.6a1.2 1.2 0 0 1 0 1.7l-7 7a1.2 1.2 0 0 1-1.7 0z"/><circle cx="8" cy="8" r="1.6"/></svg>',
 down:'<svg viewBox="0 0 24 24"><path d="M4 6l6 6 4-4 6 7"/><path d="M15 15h5v-5"/></svg>',
 star:'<svg viewBox="0 0 24 24"><path d="M12 4l2.4 5 5.4.6-4 3.7 1.1 5.3L12 16l-4.9 2.6 1.1-5.3-4-3.7 5.4-.6z"/></svg>',
 gift:'<svg viewBox="0 0 24 24"><rect x="4" y="9" width="16" height="11" rx="1.5"/><path d="M3 9h18M12 9v11M12 9c-1.5-3-5-4-5-1.5S10 9 12 9zm0 0c1.5-3 5-4 5-1.5S14 9 12 9z"/></svg>'};

/* ---- 骨組み ---- */
app.innerHTML='<div class="wrap"><header class="top"><a class="brand" href="/" aria-label="トップへ"><img id="logo" src="'+REG.logo+'" alt="'+REG.brand+'"><b>'+REG.brand+'</b></a>'+
 '<button class="tg" id="tg" role="switch" aria-checked="false" aria-label="夜の画面にする"><i class="kn"></i><span class="su"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path class="sp" d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/></svg></span><span class="mo"><svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg></span></button></header>'+(IEO?IEO.seg:'')+'</div>'+
 '<main id="main"></main>'+
 '<div class="wrap"><footer class="ft">'+(CFG.foot||"")+'<br><a href="/">'+REG.brand+' トップ</a>　<a href="/privacy">プライバシー</a></footer></div>'+
 '<nav class="nav" id="nav" aria-label="すぐ移動">'+CFG.nav.map(function(n,i){return n.href?'<a href="'+n.href+'"'+(n.cur?' class="cur"':'')+'>'+(n.svg||IC[n.ic])+'<span>'+n.t+'</span></a>':'<button data-a="'+n.a+'"'+(i===0||n.cur?' class="cur"':'')+'>'+(n.svg||IC[n.ic])+'<span>'+n.t+'</span></button>'}).join("")+'<button class="mn" id="mnb" aria-label="メニュー"><em></em><span>MENU</span></button></nav>'+
 '<div class="sh" id="sh" aria-hidden="true"><div class="bk"></div><div class="pn" role="dialog" aria-modal="true"><div class="grab"><i></i></div><button class="x" aria-label="閉じる">×</button><div id="shc"></div></div></div>'+
 '<div class="mu" id="mu"><div class="bk"></div><div class="pn"><div class="k">'+CFG.menu.k+'</div><ol>'+
 muList(CFG.menu.items)+
 '</ol><div class="rel">'+CFG.menu.rel.map(function(r){return '<a href="'+r[1]+'">'+r[0]+'</a>'}).join("")+'</div></div></div>';

/* 数え上がり（data-n。小数は data-d で桁、data-f で 1,234 の形） */
function fmt(v,b){var d=+(b.dataset.d||0),s=d?v.toFixed(d):String(Math.round(v));if(b.dataset.f)s=s.replace(/\B(?=(\d{3})+(?!\d))/g,",");return (b.dataset.pre||"")+s}
function countUp(b){var n=+b.dataset.n,t0=performance.now();if(RM||!isFinite(n)){b.textContent=fmt(n,b);return}
  (function f(t){var k=Math.min(1,(t-t0)/700),e=1-Math.pow(1-k,3);b.textContent=fmt(n*(.6+.4*e),b);if(k<1)requestAnimationFrame(f)})(t0)}
var cio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){cio.unobserve(e.target);countUp(e.target)}})},{rootMargin:"0px"});
/* 11/19 owner「動作悪い」：0円・0件が見えないように、最初から本当の数を出し、見えた時に6割から少しだけ上がる */
function counts(root){$$("[data-n]",root).forEach(function(b){b.textContent=fmt(+b.dataset.n,b);cio.observe(b)})}
/* 見えたら伸びる棒（data-w＝0〜1） */
var bio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){bio.unobserve(e.target);e.target.style.transform="scaleX("+e.target.dataset.w+")"}})});
function bars(root){$$("[data-w]",root).forEach(function(b){if(RM)b.style.transform="scaleX("+b.dataset.w+")";else bio.observe(b)})}

/* 11/20 ページの下の一覧（HTML のまま・検索用にも）を、足（.ft）の上へ */
(function(){var ix=document.querySelector("body>.ix"),ft=app.querySelector(".ft");if(ix&&ft)ft.parentNode.insertBefore(ix,ft)})();
/* ---- 下から出る板 ---- */
/* 11/20 #app の中だと上の題の帯（#tb）が板より上に来て、MENU や板の上の方を押すと後ろが動いた → 板は body の直下へ */
["#sh","#mu"].forEach(function(q){var e=$(q);if(e)document.body.appendChild(e)});
var sh=$("#sh"),shc=$("#shc"),shOpen=false;
function sheet(html,from,after){var go2=function(){shc.innerHTML=html;$(".pn",sh).scrollTop=0;sh.classList.add("op");sh.setAttribute("aria-hidden","false");document.body.style.overflow="hidden";counts(shc);bars(shc);if(after)after(shc)};
  if(!shOpen)history.pushState({sh:1},"");shOpen=true;
  if(from&&document.startViewTransition&&!RM){from.style.viewTransitionName="ph";sh.classList.add("nov");
    var t=document.startViewTransition(function(){from.style.viewTransitionName="";go2();var p=$(".pim",shc);if(p)p.style.viewTransitionName="ph"});
    t.finished.then(function(){var p=$(".pim",shc);if(p)p.style.viewTransitionName="";sh.classList.remove("nov")})}
  else go2()}
function closeSheet(back){if(!shOpen)return;shOpen=false;sh.classList.remove("op");sh.setAttribute("aria-hidden","true");document.body.style.overflow="";if(back!==false&&history.state&&history.state.sh)history.back()}
addEventListener("popstate",function(){if(shOpen)closeSheet(false)});
$(".bk",sh).onclick=function(){closeSheet()};$(".x",sh).onclick=function(){closeSheet()};
shc.addEventListener("click",function(e){if(e.target.closest("[data-share]")){try{navigator.share({title:document.title,url:location.href})}catch(_){}}});
(function(){var pn=$(".pn",sh),y0=null,dy=0;pn.addEventListener("touchstart",function(e){if(pn.scrollTop<=0){y0=e.touches[0].clientY;dy=0}else y0=null},{passive:true});
 pn.addEventListener("touchmove",function(e){if(y0==null)return;dy=e.touches[0].clientY-y0;if(dy>0){pn.style.transition="none";pn.style.transform="translate3d(0,"+dy+"px,0)"}},{passive:true});
 pn.addEventListener("touchend",function(){if(y0==null)return;pn.style.transition="";pn.style.transform="";if(dy>110)closeSheet();y0=null},{passive:true})})();

/* ---- 下のバー ---- */
var nav=$("#nav"),ly=scrollY,navFn=null;
nav.addEventListener("pointerdown",function(e){var b=e.target.closest("a,button");if(!b)return;var r=b.getBoundingClientRect(),s=document.createElement("i");s.className="rp";s.style.left=(e.clientX-r.left)+"px";s.style.top=(e.clientY-r.top)+"px";b.appendChild(s);setTimeout(function(){s.remove()},650);
  b.classList.remove("tap");void b.offsetWidth;b.classList.add("tap")});
nav.addEventListener("click",function(e){var c=e.target.closest("a.cur");if(c&&c.pathname===location.pathname){e.preventDefault();scrollTo({top:0,behavior:RM?"auto":"smooth"});return}var b=e.target.closest("[data-a]");if(!b||!navFn)return;navFn(b.dataset.a)});
function navCur(a){$$("#nav [data-a]").forEach(function(b){b.classList.toggle("cur",b.dataset.a===a)})}
/* 11/19 下へ流す間だけ隠し、指を止めたら（0.8秒）すぐ戻す。押した後に勝手に動いた時もバーが消えたままにならない */
var nvT;addEventListener("scroll",function(){var y=scrollY;if(Math.abs(y-ly)>8){nav.classList.toggle("hide",y>ly&&y>300);ly=y}clearTimeout(nvT);nvT=setTimeout(function(){nav.classList.remove("hide")},800)},{passive:true});
/* 11/20 子のページ（1件・府県・ランキングなど）は親の行に印 */(function(){if(document.querySelector(".mu li a.here"))return;var P0=location.pathname.replace(/\.html$/,""),b=null,bl=0;Array.prototype.forEach.call(document.querySelectorAll(".mu li a"),function(a){var u=a.getAttribute("href");if(!u||u.charAt(0)!=="/"||u==="/")return;var v=u.replace(/\/$/,"");if(P0.indexOf(v)===0&&v.length>bl){b=a;bl=v.length}});if(!b&&/^\/o\//.test(P0))b=document.querySelector('.mu li a[href="/odekake"]');if(b)b.classList.add("here")})();/* 11/20 owner「メニューを触ろうとすると後ろが反応する」：開いている間は後ろのページを動かさない */var mu=$("#mu"),mo=function(o){mu.classList.toggle("op",o);document.documentElement.style.overflow=document.body.style.overflow=o?"hidden":""};$("#mnb").onclick=function(){mo(true)};$(".bk",mu).onclick=function(){mo(false)};mu.addEventListener("touchmove",function(e){var p=$(".pn",mu);if(!p.contains(e.target)||p.scrollHeight<=p.clientHeight+1)e.preventDefault()},{passive:false});mu.addEventListener("wheel",function(e){var p=$(".pn",mu);if(!p.contains(e.target)||p.scrollHeight<=p.clientHeight+1)e.preventDefault()},{passive:false});addEventListener("keydown",function(e){if(e.key==="Escape"&&mu.classList.contains("op"))mo(false)});addEventListener("pageshow",function(){mo(false)});

/* ---- 府県の玉（選んだ所へ滑る・周りを光が回る） ---- */
function seg(box,list,cur,on){box.innerHTML='<i class="pill"></i>'+list.map(function(p){return '<button data-v="'+esc(p[0])+'">'+esc(p[1])+'</button>'}).join("");
  var pill=$(".pill",box);function mv(){var b=$("button.on",box);if(!b)return;pill.style.width=b.offsetWidth+"px";pill.style.transform="translateX("+(b.offsetLeft-4)+"px)";pill.style.left="4px"}
  /* 11/21 隠れている間に測ると幅0の玉になる（帯を1段にした時）→ 見えた時に測り直す */try{new ResizeObserver(function(){if(box.offsetWidth)mv()}).observe(box)}catch(e){}
  function set(v,user){$$("button",box).forEach(function(b){b.classList.toggle("on",b.dataset.v===v)});mv();var b=$("button.on",box);if(b&&user&&box.scrollWidth>box.clientWidth)box.scrollTo({left:b.offsetLeft-box.clientWidth/2+b.offsetWidth/2,behavior:"smooth"})}
  box.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;set(b.dataset.v,true);on(b.dataset.v)});
  set(cur);requestAnimationFrame(mv);addEventListener("resize",mv);if(document.fonts)document.fonts.ready.then(mv);return set}

/* ---- 昼と夜 ---- */
var cv=document.getElementById("stars"),drawn=0;
/* 11/19 owner「もっとリアルな小さな星の夜空と流れ星」→ 本物の空の決まりで描く：
   ・暗い星ほど数が多い（等級が1つ下がると約3倍）。ほとんどは髪の毛より細い点
   ・星の色は温度で違う（青白・白・薄い黄・橙）
   ・斜めに天の川（とても淡い光の帯＋細かい星の集まり＋暗い筋）
   ・明るい星だけ、空気のゆらぎで静かにまたたく（CSS の opacity だけ・軽い）
   ・流れ星は一瞬（0.5〜0.9秒）。頭が光って尾が細い。向きと長さは毎回ちがう。たまに明るい火球 */
var SC=["255,255,255","255,255,255","255,255,255","235,242,255","210,225,255","255,246,228","255,232,200","255,214,170"];
function stars(){var w=innerWidth,h=Math.min(document.body.scrollHeight,innerHeight*8),dp=Math.min(2,devicePixelRatio||1);if(drawn===w+"x"+h)return;drawn=w+"x"+h;
  cv.width=w*dp;cv.height=h*dp;cv.style.height=h+"px";var c=cv.getContext("2d");c.scale(dp,dp);var r=seed,x,y,bb,rr,g,m;
  function rnd(){r=(r*16807)%2147483647;return r/2147483647}
  function band(y,x){return Math.exp(-Math.pow((x*.62-y+y*.5+w*.15)/(w*.32),2))}
  for(var y0=0;y0<h;y0+=innerHeight){
    for(m=0;m<26;m++){x=rnd()*w;y=y0+rnd()*innerHeight;bb=band(y-y0,x);if(bb<.25)continue;
      rr=40+rnd()*110;g=c.createRadialGradient(x,y,0,x,y,rr);g.addColorStop(0,"rgba(190,200,235,"+(.035*bb).toFixed(3)+")");g.addColorStop(1,"rgba(190,200,235,0)");c.fillStyle=g;c.fillRect(x-rr,y-rr,rr*2,rr*2)}
    for(m=0;m<10;m++){x=rnd()*w;y=y0+rnd()*innerHeight;bb=band(y-y0,x);if(bb<.5)continue;
      rr=18+rnd()*40;g=c.createRadialGradient(x,y,0,x,y,rr);g.addColorStop(0,"rgba(5,8,16,.18)");g.addColorStop(1,"rgba(5,8,16,0)");c.fillStyle=g;c.fillRect(x-rr,y-rr,rr*2,rr*2)}}
  var n=Math.round(w*h/520);
  for(var i=0;i<n;i++){x=rnd()*w;y=rnd()*h;bb=band(y%innerHeight,x);if(rnd()>.35+bb*.65)continue;
    var mag=Math.pow(rnd(),3.2),sz=.22+mag*1.25,a=.18+mag*.8+rnd()*.12,col=SC[(rnd()*SC.length)|0];
    c.fillStyle="rgba("+col+","+Math.min(1,a).toFixed(3)+")";c.beginPath();c.arc(x,y,sz,0,7);c.fill();
    if(mag>.82){g=c.createRadialGradient(x,y,0,x,y,sz*6);g.addColorStop(0,"rgba("+col+",.28)");g.addColorStop(1,"rgba("+col+",0)");c.fillStyle=g;c.fillRect(x-sz*6,y-sz*6,sz*12,sz*12)}}
  twinkle(w,h)}
function twinkle(w,h){$$("#sky .tw").forEach(function(e){e.parentNode.removeChild(e)});var r=seed+7,sky=$("#sky"),hh=Math.min(h,innerHeight*3);function rnd(){r=(r*16807)%2147483647;return r/2147483647}
  var n=Math.round(w*hh/9000);for(var i=0;i<n;i++){var e=document.createElement("i");e.className="tw";var big=rnd()>.8;
    e.style.cssText="left:"+(rnd()*w).toFixed(1)+"px;top:"+(rnd()*hh).toFixed(1)+"px;--s:"+(big?2.4:1.5)+"px;--c:rgb("+SC[(rnd()*SC.length)|0]+");animation-duration:"+(2.5+rnd()*4).toFixed(2)+"s;animation-delay:-"+(rnd()*6).toFixed(2)+"s";sky.appendChild(e)}}
var shootT;function shoot(){clearTimeout(shootT);if(!H.classList.contains("nt")||RM)return;
  shootT=setTimeout(function(){var s=document.createElement("i"),big=Math.random()<.15,ang=18+Math.random()*34,len=big?220:110+Math.random()*90,dur=big?1.1:.5+Math.random()*.4;
    s.className="shoot"+(big?" big":"");s.style.cssText="left:"+(innerWidth*(.3+Math.random()*.75)).toFixed(0)+"px;top:"+(scrollY+20+Math.random()*innerHeight*.45).toFixed(0)+"px;--a:"+ang.toFixed(1)+"deg;--l:"+len.toFixed(0)+"px;--d:"+(len*1.6).toFixed(0)+"px;animation-duration:"+dur.toFixed(2)+"s";
    $("#sky").appendChild(s);setTimeout(function(){if(s.parentNode)s.parentNode.removeChild(s)},dur*1000+200);shoot()},(6+Math.random()*16)*1e3)}
function apply(n){H.classList.toggle("nt",n);try{localStorage.setItem("usagi_theme",n?"night":"day")}catch(e){}
  var src=n?REG.logon:REG.logo;$$("img[data-logo],#logo").forEach(function(i){i.src=src});
  $("#tg").setAttribute("aria-checked",n?"true":"false");var m=$('meta[name="theme-color"]');if(m)m.content=n?"#0A0E18":"#FFFFFF";
  if(n){stars();shoot()}}
$("#tg").addEventListener("click",function(e){var n=!H.classList.contains("nt");
  if(!document.startViewTransition||RM){apply(n);return}
  var kr=$("#tg .kn").getBoundingClientRect(),x=kr.left+kr.width/2+(n?34:-34),y=kr.top+kr.height/2,r=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y));H.classList.add("vtt");
  var t=document.startViewTransition(function(){apply(n)});
  t.ready.then(function(){H.animate({clipPath:["circle(0px at "+x+"px "+y+"px)","circle("+r+"px at "+x+"px "+y+"px)"]},{duration:760,easing:"cubic-bezier(.4,0,.2,1)",pseudoElement:"::view-transition-new(root)"})});
  t.finished.then(function(){H.classList.remove("vtt")})});
addEventListener("load",function(){drawn=0;if(H.classList.contains("nt"))stars()});

window.SHIN={reg:REG,$:$,$$:$$,el:el,esc:esc,TD:TD,seed:seed,diff:diff,md:md,dd:dd,IC:IC,RM:RM,countUp:countUp,counts:counts,bars:bars,sheet:sheet,closeSheet:closeSheet,seg:seg,
  onNav:function(f){navFn=f},navCur:navCur,main:$("#main"),data:JSON.parse((document.getElementById("d")||{textContent:"{}"}).textContent),
  ready:function(){apply(H.classList.contains("nt"));largeTitle();
  /* 11/19 表紙のボタン（/odekake#we・/kaiten#w=close）：# の後ろを下のバーのボタンと同じ動きにする */
  var hs=decodeURIComponent(location.hash.slice(1));if(hs&&navFn&&$('#nav [data-a="'+hs+'"]'))setTimeout(function(){navFn(hs);navCur(hs)},60)}};
/* 11/19 iPhone の設定アプリの形：大きい題は下へ流すと薄れて、上の細い帯に小さく収まる。帯を押すと一番上へ */
function largeTitle(){var h=$(".h1t");if(!h)return;var tb=document.createElement("button");tb.id="tb";tb.setAttribute("aria-label","一番上へ");tb.textContent=h.textContent;document.body.appendChild(tb);
  tb.onclick=function(){scrollTo({top:0,behavior:RM?"auto":"smooth"})};var q=0,on=false;
  function f(){q=0;var r=h.getBoundingClientRect(),p=Math.max(0,Math.min(1,(60-r.top)/70));/* 11/21 owner「下に行くと動くからたまに変になってる」→ 細い字の見本（lk-t1）では題を薄くしたり縮めたりせず、そのまま上へ流す */if(!RM&&!document.documentElement.classList.contains("lk-t1")){h.style.opacity=(1-p*.9).toFixed(3);h.style.transform="translateY("+(p*-6).toFixed(1)+"px) scale("+(1-p*.04).toFixed(3)+")"}
    var o=r.bottom<46;if(o!==on){on=o;tb.classList.toggle("on",o);H.classList.toggle("tbon",o)}}
  addEventListener("scroll",function(){if(!q)q=requestAnimationFrame(f)},{passive:true});f()}
})();
/* 11/20 数える：新しいページ（shin）には数える仕組みが無く、11/19夜の入れ替えから表示・クリックが数えられていなかった。前と同じ名前で /c へ送る（オーナーの端末は数えない） */
(function(){var O=false;try{O=localStorage.getItem("usagi_owner")==="1"}catch(e){}
  /* 関東（燈のサイト）の /c は書き込みに1日の上限がある → 表示は送らず（_middleware.js が数える）、カードを押した数だけを「操作」の枠（f=card・1日100まで）で送る。人気順に使う */
  var K=/kanto|lifenote/.test(location.hostname);
  var P=location.pathname.replace(/^\/shin(?=\/)/,"").replace(/\.html$/,"").replace(/\/$/,"")||"/",
      N={"/":"TOWN NOTE 入口","/odekake":"おでかけリスト","/illumination":"イルミネーション","/koyo":"紅葉ライトアップ","/ima":"いまから行ける","/tomari":"泊まり","/hatsumode":"初詣","/fudosan-list":"不動産リスト","/okaimono":"おかいもの","/kaiten":"開店・閉店","/ikura":"いくら","/uru":"売る前・買う前に","/jikka":"実家ノート","/furusato":"ふるさと納税","/nesage":"値下がり","/otoku":"お得"}[P]||(/^\/o\//.test(P)?"1件ページ":(document.title.split("｜")[0]||P).slice(0,30));
  function s(k){if(O)return;if(K){var m=/^クリック：([^｜]*)｜(.*)$/.exec(k);if(!m)return;var u="/c?f=card&s="+encodeURIComponent(m[1].slice(0,16))+"&k="+encodeURIComponent(m[2].slice(0,40));try{if(!(navigator.sendBeacon&&navigator.sendBeacon(u,"")))fetch(u,{method:"POST",keepalive:true})}catch(e){}return}try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true})}catch(e){}}
  window.SHIN_COUNT=s;
  /* 11/21 来た元・来訪：前のページ（assets/menu.js）だけが送っていて、shin に入れ替えた 11/19夜から「来た元」が 73→9 に落ちた。同じ名前・同じ分け方で1回の訪問に1度だけ送る（関東は _middleware.js が ?f= を数える・/c の上限があるので送らない） */
  if(!K&&!O&&!navigator.webdriver)try{
    var f=new URLSearchParams(location.search).get("f");
    if(f&&/^[A-Za-z0-9_-]{1,32}$/.test(f)&&sessionStorage.getItem("tn_f")!==f){sessionStorage.setItem("tn_f",f);s("来訪：SNS｜"+f)}
    if(!sessionStorage.getItem("tn_src")){sessionStorage.setItem("tn_src","1");var rr=document.referrer,hh="";try{hh=rr?new URL(rr).hostname:""}catch(e){}
      if(hh!==location.hostname)s("来た元："+(!hh?"直接・アプリ":/google\./.test(hh)?"Google":/yahoo\./.test(hh)?"Yahoo":/bing\.|duckduckgo|copilot/.test(hh)?"Bing":/chatgpt|openai|perplexity|claude\.ai|gemini/.test(hh)?"AI":/threads\./.test(hh)?"Threads":/(^|\.)t\.co$|twitter\.|(^|\.)x\.com$/.test(hh)?"X":/instagram\./.test(hh)?"インスタ":/rakuten\./.test(hh)?"楽天":/pages\.dev$|townnote\.app$/.test(hh)?"もう片方のHP":"ほか（"+hh.slice(0,24)+"）"))}
  }catch(e){}
  if(P==="/ikura")return;
  var r=document.referrer,out=r&&!/townnote|usagi-odekake|pages\.dev/.test(r);
  s("表示："+N+(out?"（外から）":""));
  document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a,button[data-k]");if(!a||e.target.closest(".hv"))return;
    var h=a.querySelector("h4,.t,b"),t=a.getAttribute("data-k")||(h?h.textContent:a.textContent)||"";t=t.replace(/[\u200b\u00ad]/g,"").replace(/\s+/g," ").trim().slice(0,60);if(t)s("クリック："+N+"｜"+t)},true)})();
