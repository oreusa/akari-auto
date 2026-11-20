/* 11/19 owner「他ページもぜんぶ変えれたら」→ 新しい土台で作り直していないページ（街・実家・解体・地価・売る・申し込み・おでかけ1件 …）に、
   新しい土台と同じ 頭（ロゴ・昼夜スイッチ）・大きい題が上の帯に収まる動き・下のバー＋MENU・本物の夜空 をかぶせる。
   読み込みは functions/_middleware.js が <head> に入れる（html.sk）。見た目は skin.css（build.py が shin.css から作る＋skin.tail.css）。 */
(function(){
"use strict";
if(window.__sk)return;window.__sk=1;
/* 11/20 owner「いいと思う」：分野ごとの色の線（iro）をふだんの見た目に。?iro=0 で外せる（この端末で覚える） */
try{var _q=location.search.match(/[?&]iro=([01])/);if(_q)localStorage.setItem("tn_iro",_q[1]);if(localStorage.getItem("tn_iro")!=="0"){var _p=location.pathname,_f=/^\/(shin\/cover\d?)?$|^\/index/.test(_p)?"top":/kaiten/.test(_p)?"kai":/okaimono|furusato|nesage|otoku|tanka|kaimawari|shin\/kau/.test(_p)?"kau":/fudosan|ikura|uru|ranking|machi|jikka|chika|akiya|kaitai|sagasu|moushikomi|gyosha|koe|shin\/ie/.test(_p)?"ie":"od";document.documentElement.classList.add("iro");document.documentElement.setAttribute("data-f",_f)}}catch(e){}
/* 11/19 owner「文字列おかしい」：日本語の見出し・文を意味の切れ目でだけ折り返す（BudouX） */
(function(){var s=document.createElement("script");s.src="/shin/bx.js?v=1";s.defer=true;document.head.appendChild(s)})();
var H=document.documentElement,P=location.pathname,RM=matchMedia("(prefers-reduced-motion:reduce)").matches;
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
var IC={now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',
 we:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',
 map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',
 inn:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>',
 find:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/></svg>',
 rank:'<svg viewBox="0 0 24 24"><path d="M5 20V11M12 20V5M19 20v-6"/></svg>',
 sell:'<svg viewBox="0 0 24 24"><path d="M3 12l9-8 9 8"/><path d="M6 10v10h12V10"/><path d="M10 15h4"/></svg>',
 yen:'<svg viewBox="0 0 24 24"><path d="M3.5 12.2V4.5a1 1 0 0 1 1-1h7.7l8.6 8.6a1.2 1.2 0 0 1 0 1.7l-7 7a1.2 1.2 0 0 1-1.7 0z"/><circle cx="8" cy="8" r="1.6"/></svg>',
 down:'<svg viewBox="0 0 24 24"><path d="M4 6l6 6 4-4 6 7"/><path d="M15 15h5v-5"/></svg>',
 buy:'<svg viewBox="0 0 24 24"><path d="M4 7h16l-1.5 11.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg>'};
/* ページの分野ごとの下のバーと MENU（11/19 owner「MENU はそのページの分野だけ」） */
var FUD={nav:[["街をさがす","find","/fudosan-list"],["ランキング","rank","/ranking"],["売りたい","sell","/uru"],["いくら？","yen","/ikura"]],
  k:"Home & Land",menu:[["家と土地の相場","/fudosan-list"],["地価ランキング","/chika-kansai"],["まちランキング","/ranking"],["家を売る前に","/uru"],["いくらで売れる？","/ikura"],["実家・空き家","/jikka/"],["解体の費用と補助金","/kaitai"]],
  rel:[["おでかけ","/odekake"],["おかいもの","/okaimono"],["開店・閉店","/kaiten"],["トップへ","/"]]};
var ODE={nav:[["開催中","now","/odekake"],["今週末","we","/odekake?w=we"],["いまから","map","/ima"],["泊まり","inn","/tomari"]],
  k:"Odekake",menu:[["関西おでかけ","/odekake"],["イルミネーション","/illumination"],["紅葉","/koyo"],["いまから行ける","/ima"],["泊まり","/tomari"],["初詣","/hatsumode"]],
  rel:[["家と土地","/fudosan-list"],["おかいもの","/okaimono"],["開店・閉店","/kaiten"],["トップへ","/"]]};
var KAI={nav:[["これから","now","/kaiten?w=soon"],["開いた","we","/kaiten?w=done"],["閉まる","down","/kaiten?w=close"],["おでかけ","map","/odekake"]],
  k:"New Shops",menu:[["関西の開店・閉店","/kaiten"],["関東の開店・閉店","https://kanto.townnote.app/kaiten"]],rel:[["おでかけ","/odekake"],["家と土地","/fudosan-list"],["おかいもの","/okaimono"],["トップへ","/"]]};
var TOP={nav:[["おでかけ","now","/odekake"],["家と土地","find","/fudosan-list"],["おかいもの","yen","/okaimono"],["開店閉店","buy","/kaiten"]],
  k:"Town Note",menu:[["トップ","/"],["関西のおでかけ","/odekake"],["家と土地の相場","/fudosan-list"],["日用品の値段くらべ","/okaimono"],["開店・閉店","/kaiten"]],rel:[]};
/* 関東（kanto.townnote.app）も同じ物を読む。関東にあるページだけを出す */
var KT=/kanto|lifenote|life-note|usagi-life/.test(location.hostname);
if(KT){FUD.nav[1]=["地価","rank","/chika-kanto"];FUD.menu=[["家と土地の相場","/fudosan-list"],["地価ランキング","/chika-kanto"],["家を売る前に","/uru"],["いくらで売れる？","/ikura"],["実家・空き家","/jikka/"],["解体の費用と補助金","/kaitai"]];
  ODE.nav=[["おでかけ","now","/odekake"],["いまから","map","/ima"],["紅葉","we","/koyo"],["開店閉店","buy","/kaiten"]];ODE.menu=[["関東おでかけ","/odekake"],["イルミネーション","/illumination"],["紅葉","/koyo"],["いまから行ける","/ima"]];
  KAI.menu=[["関東の開店・閉店","/kaiten"],["関西の開店・閉店","https://kansai.townnote.app/kaiten"]];}
var BR=KT?"LIFE NOTE":"TOWN NOTE",LG=KT?["/logo-s.png","/logo-s-night.png"]:["/assets/logo-s.png?v=2","/assets/logo-s-night.png"];
var OKA={nav:[["品物","find","/okaimono"],["値下がり","down","/nesage"],["お得","yen","/otoku"],["ふるさと納税","buy","/furusato"]],
  k:"Shopping",menu:[["日用品の値段くらべ","/okaimono"],["値下がりした物","/nesage"],["お得な物","/otoku"],["ふるさと納税","/furusato"]],rel:[["おでかけ","/odekake"],["家と土地","/fudosan-list"],["開店・閉店","/kaiten"],["トップへ","/"]]};
var C=/^\/(okaimono|nesage|otoku|furusato|kaimawari|tanka)/.test(P)?OKA:/^\/(o|odekake|illumination|koyo|ima|tomari|hatsumode)\b/.test(P)?ODE:/^\/kaiten/.test(P)?KAI:/^\/(machi|jikka|kaitai|chika|uru|ikura|moushikomi|gyosha|sagasu|shindan|akiya|fudosan|koe|ranking|townnotes)/.test(P)?FUD:TOP;
var here=function(u){return u.split("?")[0]===P.replace(/\.html$/,"")};
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
   home:'<path d="M4 11l8-6 8 6v9H4z"/><path d="M9 20v-4.5h6V20"/><path d="M15.5 6.5V4h2v4"/>'};
  var G=[{t:"街の相場",h:"街の相場をしらべる",u:"/fudosan-list",i:[["街の家と土地の相場","街の相場","find","/fudosan-list"],["いまいる場所の近くの街","近くの街","pin","/fudosan-list?geo=1"],["地価ランキング","地価","rank",kt?"/chika-kanto":"/chika-kansai"]].concat(kt?[]:[["まちランキング","まち","star","/ranking"]])},
   {t:"売る・買う",h:"売る・買う",u:"/uru",i:[["家を売る前に","売る前に","sell","/uru"],["いくらで売れる？","いくら？","tag","/ikura"],["家を買いたい","買いたい","key","/sagasu"],["売却・査定のご相談","相談する","chat","/moushikomi"]]},
   {t:"実家・空き家",h:"実家・空き家",u:"/jikka/",i:[["実家・空き家ノート","ノート","note","/jikka/"],["3問でわかる実家の診断","診断","check","/jikka/shindan/"],["解体・片付けの費用","解体の費用","calc","/kaitai"],["解体の補助金ランキング","補助金","gift","/kaitai-ranking"],["空き家が多い街ランキング","空き家の街","home","/akiya-ranking"]]}];
  var want="";try{want=new URLSearchParams(location.search).get("want")||""}catch(e){}
  var g=/^\/(jikka|kaitai|akiya|shindan)/.test(p)||(/^\/moushikomi/.test(p)&&/片付|解体|実家|空き家/.test(want))?2:/^\/(uru|ikura|sagasu|moushikomi|gyosha|fudosan$)/.test(p)?1:0;
  var cu=p==="/jikka/shindan/"||p==="/shindan"?"/jikka/shindan/":/^\/jikka\//.test(p)?"/jikka/":/^\/machi\//.test(p)?"/fudosan-list":/^\/kaitai-(?!ranking)./.test(p)?"/kaitai-ranking":/^\/chika-/.test(p)?(kt?"/chika-kanto":"/chika-kansai"):p;
  var svg=function(k){return '<svg viewBox="0 0 24 24">'+I[k]+'</svg>'};
  var seg='<nav class="topsg" aria-label="家と土地のページ"><div class="topsg-k">家と土地</div><div class="topsg-b">'+G.map(function(x,j){return '<a href="'+x.u+'"'+(j===g?' class="on" aria-current="true"':'')+'>'+x.t+'</a>'}).join("")+'</div></nav>';
  var bi=G[g].i.slice(0,4),ci=G[g].i.filter(function(x){return x[3]===cu})[0];if(ci&&bi.indexOf(ci)<0)bi[3]=ci;
  var nav=bi.map(function(x){return {t:x[1],ic:x[2],svg:svg(x[2]),href:x[3],cur:x[3]===cu}});
  var menu=[];G.forEach(function(x){menu.push([x.h,"#"]);x.i.forEach(function(y){menu.push([y[0],y[3]].concat(y[3]===cu?[1]:[]))})});
  return {g:g,seg:p==="/fudosan-list"?"":seg,nav:nav,menu:menu};
}
var IEO=C===FUD?ieOrg(P,KT):null;
if(IEO){C={nav:IEO.nav.map(function(x){return [x.t,x.ic,x.href,x.svg,x.cur]}),k:FUD.k,menu:IEO.menu.map(function(m){return m.length>2||m[1]==="#"?m:[m[0],m[1],0]}),rel:FUD.rel};H.classList.add("ieo")}

/* 11/20 owner「他社とも比べて勝つ」：ほかの相場サイト（GMO・東急リバブル・ダイヤモンド・トチノカチ・三菱地所）は
   ①件数が少なくても平均だけを大きく出す ②近くの街と並べて比べられない ③自分の家の目安へすぐ行けない。
   → 街のページ（値段と地価）に「近くの街とくらべる」（近い6つ・切りかえ・件数・少ない時の印）と「うちの家はいくら？」を足す（見本 ?seiri=1） */
function cmpTowns(M,id,k){var me=M.t[id];if(!me||!me[3]||!me[3][8])return;var xy=me[3][8];
  var esc=function(x){return String(x).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})};
  var man=function(v){v=Math.round(v);return v>=10000?Math.floor(v/10000)+"億"+(v%10000?(v%10000).toLocaleString()+"万":""):v.toLocaleString()+"万"};
  var pc=function(v){return (v>0?"+":"")+v.toFixed(1)+"%"};
  var L=Object.keys(M.t).filter(function(i){var v=M.t[i][3];return v&&v[8]}).map(function(i){var v=M.t[i][3];return {id:i,n:M.t[i][0],v:v,d:i===id?-1:Math.hypot(v[8][0]-xy[0],v[8][1]-xy[1])}}).sort(function(a,b){return a.d-b.d}).slice(0,6);
  var hasM=L.some(function(x){return x.v[4]&&x.v[4][0]});
  var K=[["地価の動き",function(v){return v[1]},pc,"住宅地の地価・1年"]];
  var enough=function(f){return L.filter(function(x){return f(x.v)!=null}).length>=3};
  if(hasM)K.push(["マンション",function(v){return v[4]&&v[4][0]?v[4][1]:null},function(x){return man(x)+"円"},"中古マンションが売れた平均・2025年度",4],["一戸建て",function(v){return v[5]&&v[5][0]?v[5][1]:null},function(x){return man(x)+"円"},"中古一戸建てが売れた平均・2025年度",5]);
  else K.push(["人口の動き",function(v){return v[6]},pc,"人口・5年"],["空き家",function(v){return v[7]},function(x){return x.toFixed(1)+"%"},"空き家の割合・2023年"]);
  K=K.filter(function(q){return enough(q[1])});if(!K.length)return;
  var sec=document.createElement("section");sec.className="cmpt";sec.setAttribute("aria-label","近くの街とくらべる");
  var draw=function(j){var q=K[j],vals=L.map(function(x){return q[1](x.v)}),mx=Math.max.apply(null,vals.filter(function(x){return x!=null}).map(Math.abs).concat([0.0001]));
    sec.innerHTML='<h2 class="cmpt-h">近くの街とくらべる</h2><div class="cmpt-k" role="tablist">'+K.map(function(x,i){return '<button role="tab" aria-selected="'+(i===j)+'"'+(i===j?' class="on"':'')+' data-j="'+i+'">'+x[0]+'</button>'}).join("")+'</div>'+
     '<p class="cmpt-s">'+q[3]+(q[4]?'。（ ）は売れた件数。10件より少ない街は目安だけです':'')+'</p><ol class="cmpt-l">'+L.map(function(x,i){var val=vals[i],c=q[4]&&x.v[q[4]]?x.v[q[4]][0]:null,w=val==null?0:Math.max(.04,Math.abs(val)/mx);
      return '<li'+(x.id===id?' class="me"':'')+'><a href="/machi/'+x.id+'"><span class="n">'+esc(x.n)+(x.id===id?'<em>この街</em>':'')+'</span><b>'+(val==null?'—':q[2](val))+(c!=null?'<small>（'+c+'件）</small>':'')+(c!=null&&c<10?'<u>少ない</u>':'')+'</b><i class="bar"><i style="width:'+(w*100).toFixed(1)+'%"'+(val<0?' class="neg"':'')+'></i></i></a></li>'}).join("")+'</ol>'+
     '<a class="cmpt-go" href="/ikura?machi='+id+'"><b>この街で、うちの家はいくら？</b><small>種類と広さから30秒で目安・名前は要りません</small><i>›</i></a>';
    [].forEach.call(sec.querySelectorAll(".cmpt-k button"),function(b){b.onclick=function(){draw(+b.dataset.j)}})};
  draw(0);
  var at=document.getElementById("itt")||document.querySelector(".faq");if(at)at.parentNode.insertBefore(sec,at);else return;
  /* 件数が少ない平均に印（ほかのサイトは件数を出さないか、少なくても平均だけ大きく出す） */
  [].forEach.call(document.querySelectorAll(".sold .vs"),function(e){var m=e.textContent.match(/^(\d+)件の平均/);if(m&&+m[1]<10&&!e.querySelector("u"))e.insertAdjacentHTML("beforeend",'<u class="cmpt-few">件数が少ないので目安だけ</u>')});
}
function build(){
  if(H.classList.contains("night"))H.classList.add("nt");
  var n=H.classList.contains("nt");
  var top=document.createElement("div");top.className="skc";
  top.innerHTML='<div class="wrap"><header class="top"><a class="brand" href="/" aria-label="トップへ"><img id="logo" src="'+(n?LG[1]:LG[0])+'" alt="'+BR+'"><b>'+BR+'</b></a>'+
   '<button class="tg" id="tg" role="switch" aria-checked="'+n+'" aria-label="夜の画面にする"><i class="kn"></i><span class="su"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path class="sp" d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/></svg></span><span class="mo"><svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg></span></button></header>'+(IEO?IEO.seg:'')+'</div>';
  document.body.insertBefore(top,document.body.firstChild);
  /* 11/20 owner「同じ街の相場・実家・解体を1つにまとめる」：街のページ（/machi/・/jikka/・/kaitai-市）の上は、その街の3つのタブ（値段と地価／実家・空き家／解体・片付け）。表は /shin/machi.json（tools/shin/machimap.py） */
  if(IEO)(function(){var tm=P.match(/^\/(machi|jikka)\/([a-z]+-\d+)/),km=P.match(/^\/kaitai-(?!ranking)([a-z]+)/);if(!tm&&!km)return;
    var o0=top.querySelector(".topsg"),show=function(){if(o0)o0.style.visibility=""};if(o0)o0.style.visibility="hidden";setTimeout(show,1500);
    var last="";try{last=sessionStorage.getItem("tn_machi")||"";if(tm)sessionStorage.setItem("tn_machi",tm[2])}catch(e){}
    fetch("/shin/machi.json").then(function(r){return r.json()}).then(function(M){var id,nm,k,cur;
      if(tm){id=tm[2];var t=M.t[id];if(!t)return show();nm=t[0];k=t[2];cur=tm[1]==="machi"?0:1}
      else{k=km[1];var c=M.k[k];if(!c)return show();cur=2;id=c[1].indexOf(last)>=0?last:(c[1].length===1?c[1][0]:"");nm=id?M.t[id][0]:c[0]}
      var t2=id?M.t[id]:null,u=[id?"/machi/"+id:"/fudosan-list?q="+encodeURIComponent(nm),t2&&t2[1]?"/jikka/"+id:"/jikka/",k?"/kaitai-"+k:"/kaitai"];
      var L=["値段と地価","実家・空き家",k?"解体の補助金":"解体・片付け"];
      var h='<nav class="topsg toptw" aria-label="'+nm+'のページ"><div class="topsg-k">'+nm+'</div><div class="topsg-b">'+L.map(function(x,i){return '<a href="'+u[i]+'"'+(i===cur?' class="on" aria-current="page"':'')+'>'+x+'</a>'}).join("")+'</div></nav>';
      var o=top.querySelector(".topsg");if(o)o.outerHTML=h;if(tm&&tm[1]==="machi")cmpTowns(M,id,k)}).catch(show)})();
  var sk=document.createElement("div");sk.className="skc";sk.id="sk";
  sk.innerHTML='<div id="sky" aria-hidden="true"><canvas id="stars"></canvas></div>'+
   '<nav class="nav" id="nav" aria-label="すぐ移動">'+C.nav.map(function(x){return '<a href="'+x[2]+'"'+((x.length>4?x[4]:here(x[2]))?' class="cur"':'')+'>'+(x[3]||IC[x[1]])+'<span>'+x[0]+'</span></a>'}).join("")+'<button class="mn" id="mnb" aria-label="メニュー"><em></em><span>MENU</span></button></nav>'+
   '<div class="mu" id="mu"><div class="bk"></div><div class="pn"><div class="k">'+C.k+'</div><ol>'+(function(){var k=0;return C.menu.map(function(m){if(m[1]==="#")return '<li class="mg">'+m[0]+'</li>';k++;return '<li><a href="'+m[1]+'"'+((m.length>2?m[2]:here(m[1]))?' class="here"':'')+' style="transition-delay:'+(60+k*30)+'ms"><small>'+(k<10?'0':'')+k+'</small>'+m[0]+'</a></li>'}).join("")})()+
   '</ol><div class="rel">'+C.rel.map(function(r){return '<a href="'+r[1]+'">'+r[0]+'</a>'}).join("")+'</div></div></div>';
  document.body.appendChild(sk);
  /* 下のバー：下へ流す間だけ隠れ、止めたら戻る */
  var nav=$("#nav"),ly=scrollY,nvT;
  addEventListener("scroll",function(){var y=scrollY;if(Math.abs(y-ly)>8){nav.classList.toggle("hide",y>ly&&y>300);ly=y}clearTimeout(nvT);nvT=setTimeout(function(){nav.classList.remove("hide")},800)},{passive:true});
  nav.addEventListener("click",function(e){var c=e.target.closest("a.cur");if(c&&c.pathname===location.pathname){e.preventDefault();scrollTo({top:0,behavior:RM?"auto":"smooth"})}});
  nav.addEventListener("pointerdown",function(e){var b=e.target.closest("a,button");if(!b)return;b.classList.remove("tap");void b.offsetWidth;b.classList.add("tap")});
  /* 11/20 子のページ（1件・府県・ランキングなど）は親の行に印 */(function(){if(document.querySelector(".mu li a.here"))return;var P0=location.pathname.replace(/\.html$/,""),b=null,bl=0;Array.prototype.forEach.call(document.querySelectorAll(".mu li a"),function(a){var u=a.getAttribute("href");if(!u||u.charAt(0)!=="/"||u==="/")return;var v=u.replace(/\/$/,"");if(P0.indexOf(v)===0&&v.length>bl){b=a;bl=v.length}});if(!b&&/^\/o\//.test(P0))b=document.querySelector('.mu li a[href="/odekake"]');if(b)b.classList.add("here")})();/* 11/20 owner「メニューを触ろうとすると後ろが反応する」：開いている間は後ろのページを動かさない */var mu=$("#mu"),mo=function(o){mu.classList.toggle("op",o);document.documentElement.style.overflow=document.body.style.overflow=o?"hidden":""};$("#mnb").onclick=function(){mo(true)};$(".bk",mu).onclick=function(){mo(false)};mu.addEventListener("touchmove",function(e){var p=$(".pn",mu);if(!p.contains(e.target)||p.scrollHeight<=p.clientHeight+1)e.preventDefault()},{passive:false});mu.addEventListener("wheel",function(e){var p=$(".pn",mu);if(!p.contains(e.target)||p.scrollHeight<=p.clientHeight+1)e.preventDefault()},{passive:false});addEventListener("keydown",function(e){if(e.key==="Escape"&&mu.classList.contains("op"))mo(false)});addEventListener("pageshow",function(){mo(false)});
  /* 大きい題 → 上の細い帯 */
  var h=$(".head h1,.s3h h1,.wrap h1");if(h){var tb=document.createElement("button");tb.id="tb";tb.className="sk-tb";tb.setAttribute("aria-label","一番上へ");
    tb.textContent=(h.childNodes[0]&&h.childNodes[0].nodeType===3?h.childNodes[0].textContent:h.textContent).trim();sk.appendChild(tb);
    tb.onclick=function(){scrollTo({top:0,behavior:RM?"auto":"smooth"})};var q=0,on=false;
    var f=function(){q=0;var r=h.getBoundingClientRect(),o=r.bottom<46;if(o!==on){on=o;tb.classList.toggle("on",o);H.classList.toggle("tbon",o)}};
    addEventListener("scroll",function(){if(!q)q=requestAnimationFrame(f)},{passive:true});f()}
  /* 昼夜：今までの夜（night.js）と新しい夜空を一緒に切り替える */
  $("#tg").addEventListener("click",function(){var n=!H.classList.contains("nt");
    var go=function(){H.classList.toggle("nt",n);try{if(window.usagiTheme)usagiTheme.set(n?"night":"day");else{H.classList.toggle("night",n);localStorage.setItem("usagi_theme",n?"night":"day")}}catch(e){}
      $("#logo").src=n?LG[1]:LG[0];$("#tg").setAttribute("aria-checked",n?"true":"false");var m=$('meta[name="theme-color"]');if(m)m.content=n?"#0A0E18":"#FFFFFF";if(n){stars();shoot()}};
    if(!document.startViewTransition||RM){go();return}
    var kr=$("#tg .kn").getBoundingClientRect(),x=kr.left+kr.width/2+(n?34:-34),y=kr.top+kr.height/2,r=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y));H.classList.add("vtt");
    var t=document.startViewTransition(go);t.ready.then(function(){H.animate({clipPath:["circle(0px at "+x+"px "+y+"px)","circle("+r+"px at "+x+"px "+y+"px)"]},{duration:760,easing:"cubic-bezier(.4,0,.2,1)",pseudoElement:"::view-transition-new(root)"})});
    t.finished.then(function(){H.classList.remove("vtt")})});
  if(n){stars();shoot()}
  addEventListener("resize",function(){if(H.classList.contains("nt"))stars()});
}
/* 本物の空の決まりの夜空（shin.js と同じ・画面に貼り付く1枚） */
var SC=["255,255,255","255,255,255","255,255,255","235,242,255","210,225,255","255,246,228","255,232,200","255,214,170"],drawn="",seed=+new Date(Date.now()+9*36e5).toISOString().slice(0,10).replace(/-/g,"");
function stars(){var cv=$("#stars");if(!cv)return;var w=innerWidth,h=screen.height>innerHeight?Math.max(innerHeight,screen.height):innerHeight,dp=Math.min(2,devicePixelRatio||1);if(drawn===w+"x"+h)return;drawn=w+"x"+h;
  cv.width=w*dp;cv.height=h*dp;cv.style.height=h+"px";var c=cv.getContext("2d");c.scale(dp,dp);var r=seed,x,y,bb,rr,g,m;
  function rnd(){r=(r*16807)%2147483647;return r/2147483647}
  function band(y,x){return Math.exp(-Math.pow((x*.62-y+y*.5+w*.15)/(w*.32),2))}
  for(m=0;m<26;m++){x=rnd()*w;y=rnd()*h;bb=band(y,x);if(bb<.25)continue;rr=40+rnd()*110;g=c.createRadialGradient(x,y,0,x,y,rr);g.addColorStop(0,"rgba(190,200,235,"+(.035*bb).toFixed(3)+")");g.addColorStop(1,"rgba(190,200,235,0)");c.fillStyle=g;c.fillRect(x-rr,y-rr,rr*2,rr*2)}
  var n=Math.round(w*h/520);
  for(var i=0;i<n;i++){x=rnd()*w;y=rnd()*h;bb=band(y,x);if(rnd()>.35+bb*.65)continue;
    var mag=Math.pow(rnd(),3.2),sz=.22+mag*1.25,a=.18+mag*.8+rnd()*.12,col=SC[(rnd()*SC.length)|0];
    c.fillStyle="rgba("+col+","+Math.min(1,a).toFixed(3)+")";c.beginPath();c.arc(x,y,sz,0,7);c.fill();
    if(mag>.82){g=c.createRadialGradient(x,y,0,x,y,sz*6);g.addColorStop(0,"rgba("+col+",.28)");g.addColorStop(1,"rgba("+col+",0)");c.fillStyle=g;c.fillRect(x-sz*6,y-sz*6,sz*12,sz*12)}}
  $$("#sky .tw").forEach(function(e){e.parentNode.removeChild(e)});var sky=$("#sky");r=seed+7;
  for(i=0;i<Math.round(w*h/9000);i++){var e=document.createElement("i");e.className="tw";var big=rnd()>.8;
    e.style.cssText="left:"+(rnd()*w).toFixed(1)+"px;top:"+(rnd()*h).toFixed(1)+"px;--s:"+(big?2.4:1.5)+"px;--c:rgb("+SC[(rnd()*SC.length)|0]+");animation-duration:"+(2.5+rnd()*4).toFixed(2)+"s;animation-delay:-"+(rnd()*6).toFixed(2)+"s";sky.appendChild(e)}}
var shootT;function shoot(){clearTimeout(shootT);if(!H.classList.contains("nt")||RM)return;
  shootT=setTimeout(function(){var s=document.createElement("i"),big=Math.random()<.15,ang=18+Math.random()*34,len=big?220:110+Math.random()*90,dur=big?1.1:.5+Math.random()*.4;
    s.className="shoot"+(big?" big":"");s.style.cssText="left:"+(innerWidth*(.3+Math.random()*.75)).toFixed(0)+"px;top:"+(20+Math.random()*innerHeight*.45).toFixed(0)+"px;--a:"+ang.toFixed(1)+"deg;--l:"+len.toFixed(0)+"px;--d:"+(len*1.6).toFixed(0)+"px;animation-duration:"+dur.toFixed(2)+"s";
    $("#sky").appendChild(s);setTimeout(function(){if(s.parentNode)s.parentNode.removeChild(s)},dur*1000+200);shoot()},(6+Math.random()*16)*1e3)}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",build);else build();
})();
