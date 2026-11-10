/* 11/1 オーナー「HP内全部ちゃんとやれ」→ 燈の中のページにも、トップと同じ下のボタン列（右端に MENU）を出す（月の v2sub.js と同じ形）。
   開催中・これから・地図は /odekake へ移動して開く（v2.js が ?v2t= を読む）。タブと見出しに都県の色を付ける。 */
(function(){
var PC={"東京":"#4F86C6","神奈川":"#3FA3B5","埼玉":"#E09A3E","千葉":"#D9775A","茨城":"#5FA06A","栃木":"#D2697E","群馬":"#9C7BB8"};
var st=document.createElement("style");st.textContent=":root{--ink:#1C1C1C;--acc:#3A2F28}#v2bar{position:fixed;left:10px;right:10px;bottom:calc(10px + env(safe-area-inset-bottom));z-index:9980;display:flex;align-items:stretch;background:rgba(255,255,255,.97);border-radius:16px;box-shadow:0 6px 24px rgba(0,0,0,.14);overflow:hidden;max-width:460px;margin:0 auto}#v2bar a,#v2bar button{flex:1;text-decoration:none;border:0;background:none;padding:10px 2px 9px;font-family:\"Zen Kaku Gothic New\",sans-serif;font-size:11px;font-weight:700;color:var(--ink);letter-spacing:.02em;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;-webkit-tap-highlight-color:transparent;transition:opacity .15s}#v2bar a:active,#v2bar button:active{opacity:.55}#v2bar svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}#v2bar a.cur{color:var(--acc)}#v2bar a.cur span{border-bottom:2px solid var(--acc)}#v2bar button.mn{flex:0 0 72px;background:var(--acc);color:#fff;font-family:Jost,sans-serif;letter-spacing:.14em;font-size:10.5px;justify-content:center;gap:7px}#v2bar button.mn i{display:block;width:18px;height:1.5px;background:#fff;box-shadow:0 -5px 0 #fff,0 5px 0 #fff;margin:5px 0 3px}html.v2bar-on #umenu{display:none!important}html[style*=\"overflow: hidden\"] #v2bar{display:none}html.v2bar-on #utheme{right:12px}";document.head.appendChild(st);
var I={ai:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5M9 9.5h4M11 7.5v4"/></svg>',now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',up:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',inn:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>'};
function goF(){
/* 11/7 関東不動産リスト（月の v2sub.js の goF と同じ）：不動産のページの下のバー。街で探す・地図・ランキング・売る前に（新着は MENU） */
var F={q:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg>',rk:'<svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V5M16 20v-7M22 20H2"/></svg>',mp:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',ur:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>'};
var here=/\/fudosan-list/.test(location.pathname),rk=/\/chika-/.test(location.pathname);
var ps=document.createElement("style");ps.textContent="body{padding-bottom:84px}";document.head.appendChild(ps);
var bar=document.createElement("nav");bar.id="v2bar";bar.setAttribute("aria-label","すぐ移動");
bar.innerHTML='<a data-m="q">'+F.q+'<span>街で探す</span></a><a data-m="map">'+F.mp+'<span>地図</span></a><a data-h="/chika-kanto"'+(rk?' class="cur"':'')+'>'+F.rk+'<span>ランキング</span></a><a data-h="/uru.html">'+F.ur+'<span>売る前に</span></a><button class="mn" type="button"><i></i>MENU</button>';
bar.querySelectorAll("a").forEach(function(a){a.setAttribute("data-k","下のバー｜"+a.textContent);
 if(a.dataset.h){a.href=a.dataset.h;return;}
 if(here&&window.FQ){a.href="#";a.onclick=function(e){e.preventDefault();window.FQ.open(a.dataset.m);};}
 else a.href="/fudosan-list?fq="+a.dataset.m;});
bar.querySelector(".mn").onclick=function(){var m=document.getElementById("umenu");if(m)m.click();};
document.body.appendChild(bar);bar.classList.add("on");document.documentElement.classList.add("v2bar-on");
window.V2BAR=bar;
}
function goJ(){
/* 11/10 オーナー「実家のやつは不動産リストと完全別に…そのページしか触らない人も多い」→ 実家ノートだけの下のバー（不動産の項目は出さない）。
   街をさがす（実家ノートの一覧）・この順で（街のページの4つの順番）・相談する（11/10 オーナー「関東も関西と同じで俺に問い合わせ」→ LIFE も）・MENU */
var J={q:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg>',st:'<svg viewBox="0 0 24 24"><path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1.2"/><circle cx="4.5" cy="12" r="1.2"/><circle cx="4.5" cy="18" r="1.2"/></svg>',ml:'<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>'};
var life=/life|kanto/.test(location.hostname),idx=/^\/jikka\/?(index(\.html)?)?$/.test(location.pathname),m=location.pathname.match(/^\/jikka\/([a-z]+-\d+)/);
var ps=document.createElement("style");ps.textContent="body{padding-bottom:84px}";document.head.appendChild(ps);
var bar=document.createElement("nav");bar.id="v2bar";bar.setAttribute("aria-label","すぐ移動");
bar.innerHTML='<a data-h="/jikka/"'+(idx?' class="cur"':'')+'>'+J.q+'<span>街をさがす</span></a>'+(idx?'':'<a data-h="#steps">'+J.st+'<span>この順で</span></a>')+('<a data-h="/moushikomi'+(m?'?machi='+m[1]+'&want='+encodeURIComponent("相続した家のこと"):'?want='+encodeURIComponent("相続した家のこと"))+'">'+J.ml+'<span>相談する</span></a>')+'<button class="mn" type="button"><i></i>MENU</button>';
bar.querySelectorAll("a").forEach(function(a){a.href=a.dataset.h;a.setAttribute("data-k","下のバー｜実家｜"+a.textContent);});
bar.querySelector(".mn").onclick=function(){var m=document.getElementById("umenu");if(m)m.click();};
document.body.appendChild(bar);bar.classList.add("on");document.documentElement.classList.add("v2bar-on");
}
function go(){
if(/^\/jikka/.test(location.pathname))return goJ();
if(/^\/(fudosan-list|uru|moushikomi|sagasu|chika-|machi\/)/.test(location.pathname))return goF();
var inn=/\/tomari/.test(location.pathname),P=location.pathname.replace(/\.html$/,"");
/* 11/2 LIFE NOTE：買い物のページ（くらべたおかいものリストとその仲間）は、買い物の下のボタン列。おでかけ側は /odekake へ */
/* 11/2 くらべたおかいものリストのタブ4つ（くらべた物・1個あたり・値下がり・セール）へ。いまのページの仲間に下線 */
/* 11/5 オーナー「AIで調べる項目、バーにいれたり、もっと見やすく使いやすく」→ 左に「AIに聞く」、ふるさと納税も1押しで */
/* 11/6 オーナーOK「見本4」→ /okaimono はくらべる1つに。下のバーは くらべる・買い時・セール・ふるさと（前のページは /otoku） */
var SH=[["cmp","くらべる",'<svg viewBox="0 0 24 24"><path d="M12 4v16M6 8h12M6 8l-3 6h6zM18 8l-3 6h6z"/></svg>',/^\/(okaimono|tanka)$/,"/okaimono"],
 ["down","買い時",'<svg viewBox="0 0 24 24"><path d="M4 6l7 7 4-4 5 5"/><path d="M20 10v4h-4"/></svg>',/^\/nesage/,"/nesage"],
 ["sale","セール",'<svg viewBox="0 0 24 24"><path d="M3 12l9-9h7v7l-9 9z"/><circle cx="15" cy="9" r="1.4"/></svg>',/^\/kaimawari/,"/kaimawari"],
 ["furu","ふるさと",'<svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>',/^\/furusato/,"/furusato"]];
var shop=/^\/(okaimono|nesage|tanka|furusato|kaimawari|otoku)/.test(P);
var bar=document.createElement("nav");bar.id="v2bar";bar.setAttribute("aria-label","すぐ移動");
/* LIFE NOTE の入口ページ：2つのリストといまから行ける（月の TOWN NOTE 入口と同じ形） */
var top=P===""||P==="/"||P==="/index";
bar.innerHTML=top?'<a href="/odekake">'+I.map+'<span>おでかけ</span></a><a href="/fudosan-list"><svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V5M16 20v-7M22 20H2"/></svg><span>不動産</span></a><a href="/okaimono"><svg viewBox="0 0 24 24"><path d="M5 8h14l-1 12H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg><span>おかいもの</span></a><a href="/otoku#kq">'+I.ai+'<span>AIに聞く</span></a><a href="/ima">'+I.now+'<span>いま行ける</span></a><button class="mn" type="button"><i></i>MENU</button>':(shop?SH.map(function(x){return '<a href="'+(x[4]||'/okaimono?t='+x[0])+'"'+(x[3].test(P)?' class="cur"':'')+'>'+x[2]+'<span>'+x[1]+'</span></a>';}).join(""):
 /* 11/9 TOWN と同じ5つに（入口の街さがしは11/8になくなったので「街で探す」を外す） */'<a href="/odekake">'+'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></svg>'+'<span>さがす</span></a><a href="/odekake?d=all&f=fav" style="position:relative">'+'<svg viewBox="0 0 24 24"><path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8L3.5 9.7l5.9-.9z"/></svg>'+'<span>行きたい</span>'+(function(){var n=0;try{n=(JSON.parse(localStorage.getItem("tn_fav")||"[]")||[]).length;}catch(e){}return n?'<b style="position:absolute;top:4px;left:56%;font:500 9.5px Jost,sans-serif;background:#B0705A;color:#fff;border-radius:999px;padding:1px 5px;line-height:1.3">'+n+'</b>':'';})()+'</a><a href="/odekake?v2t=map">'+I.map+'<span>地図</span></a><a href="/tomari"'+(inn?' class="cur"':'')+'>'+I.inn+'<span>泊まり</span></a>')+'<button class="mn" type="button"><i></i>MENU</button>';
/* 11/7 入口に「不動産」を足して5つになったので、文字が2行に折れないよう少し小さく */
if(top){bar.classList.add("b6");var s6=document.createElement("style");s6.textContent="#v2bar.b6 a{font-size:10px;letter-spacing:0;white-space:nowrap}";document.head.appendChild(s6);}
bar.querySelector(".mn").onclick=function(){var m=document.getElementById("umenu");if(m)m.click();};
document.body.appendChild(bar);
function fo(){var h=location.hash;if(h==="#kq"){var k=document.getElementById("kq");if(k){k.scrollIntoView({block:"center"});try{k.focus({preventScroll:true});}catch(e){}}}
 if(h==="#town"){var t=document.getElementById("town");if(t){t.scrollIntoView({block:"start"});var q=t.querySelector("input");if(q)try{q.focus({preventScroll:true});}catch(e){}}}}
addEventListener("hashchange",fo);setTimeout(fo,60);document.documentElement.classList.add("v2bar-on");
function col(el,t){for(var k in PC){if(t.indexOf(k)===0){el.style.setProperty("--pc",PC[k]);return;}}}
document.querySelectorAll(".tabs button").forEach(function(b){col(b,b.textContent.trim());});
document.querySelectorAll(".ps").forEach(function(s){var h=s.querySelector("h2");if(h)col(s,h.textContent.trim());});document.querySelectorAll(".ps h2").forEach(function(h){col(h,h.textContent.trim());});
document.querySelectorAll(".pn a").forEach(function(a){col(a,a.textContent.trim());});
}
/* 11/2 オーナー「イルミ、紅葉、地図動かない」→ そのページに自分の地図（イルミ・紅葉・泊まり）があるときは、下のバーの「地図」でそのページの地図を開く（おでかけリストへ飛ばない） */
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest('#v2bar a[href*="v2t=map"]');if(!a)return;
  var t=document.querySelector(".tnbtn");if(!t)return;e.preventDefault();var tn=document.querySelector(".tn");if(tn&&tn.classList.contains("fs"))return;t.click();},true);
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",go);else go();
})();

/* 11/4 カードの日付と絵（cardmark.js。月と同じ）を読み込む */
(function(){if(document.querySelector('script[src*="cardmark.js"]'))return;var s=document.createElement("script");s.src="/assets/cardmark.js?v=14";s.defer=true;document.head.appendChild(s);})();
