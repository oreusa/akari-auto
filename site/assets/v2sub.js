/* 11/1 オーナー「HP内全部ちゃんとやれ」→ 燈の中のページにも、トップと同じ下のボタン列（右端に MENU）を出す（月の v2sub.js と同じ形）。
   開催中・これから・地図は /odekake へ移動して開く（v2.js が ?v2t= を読む）。タブと見出しに都県の色を付ける。 */
(function(){
var PC={"東京":"#4F86C6","神奈川":"#3FA3B5","埼玉":"#E09A3E","千葉":"#D9775A","茨城":"#5FA06A","栃木":"#D2697E","群馬":"#9C7BB8"};
var st=document.createElement("style");st.textContent=":root{--ink:#1C1C1C;--acc:#3A2F28}#v2bar{position:fixed;left:10px;right:10px;bottom:calc(10px + env(safe-area-inset-bottom));z-index:9980;display:flex;align-items:stretch;background:rgba(255,255,255,.97);border-radius:16px;box-shadow:0 6px 24px rgba(0,0,0,.14);overflow:hidden;max-width:460px;margin:0 auto}#v2bar a,#v2bar button{flex:1;text-decoration:none;border:0;background:none;padding:10px 2px 9px;font-family:\"Zen Kaku Gothic New\",sans-serif;font-size:11px;font-weight:700;color:var(--ink);letter-spacing:.02em;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;-webkit-tap-highlight-color:transparent;transition:opacity .15s}#v2bar a:active,#v2bar button:active{opacity:.55}#v2bar svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}#v2bar a.cur{color:var(--acc)}#v2bar a.cur span{border-bottom:2px solid var(--acc)}#v2bar button.mn{flex:0 0 72px;background:var(--acc);color:#fff;font-family:Jost,sans-serif;letter-spacing:.14em;font-size:10.5px;justify-content:center;gap:7px}#v2bar button.mn i{display:block;width:18px;height:1.5px;background:#fff;box-shadow:0 -5px 0 #fff,0 5px 0 #fff;margin:5px 0 3px}html.v2bar-on #umenu{display:none!important}html[style*=\"overflow: hidden\"] #v2bar{display:none}html.v2bar-on #utheme{right:12px}";document.head.appendChild(st);
var I={now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',up:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',inn:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>'};
function go(){
var inn=/\/tomari/.test(location.pathname),P=location.pathname.replace(/\.html$/,"");
/* 11/2 LIFE NOTE：買い物のページ（くらべたおかいものリストとその仲間）は、買い物の下のボタン列。おでかけ側は /odekake へ */
var SH=[["/okaimono","いち押し",'<svg viewBox="0 0 24 24"><path d="M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.4 6.7 19.4l1.2-6L3.4 9.3l6-.7z"/></svg>'],
 ["/nesage","値下がり",'<svg viewBox="0 0 24 24"><path d="M4 6l6 6 4-4 6 6"/><path d="M20 10v4h-4"/></svg>'],
 ["/tanka","1個あたり",'<svg viewBox="0 0 24 24"><path d="M12 4v16M6 8h12M6 8l-3 6h6zM18 8l-3 6h6z"/></svg>'],
 ["/furusato","ふるさと",'<svg viewBox="0 0 24 24"><rect x="4" y="9" width="16" height="11" rx="1.5"/><path d="M12 9v11M4 13h16"/></svg>']];
var shop=/^\/(okaimono|nesage|tanka|furusato|kaimawari)/.test(P);
var bar=document.createElement("nav");bar.id="v2bar";bar.setAttribute("aria-label","すぐ移動");
/* LIFE NOTE の入口ページ：2つのリストといまから行ける（月の TOWN NOTE 入口と同じ形） */
var top=P===""||P==="/"||P==="/index";
bar.innerHTML=top?'<a href="/odekake">'+I.map+'<span>おでかけ</span></a><a href="/okaimono"><svg viewBox="0 0 24 24"><path d="M5 8h14l-1 12H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg><span>おかいもの</span></a><a href="/ima">'+I.now+'<span>いま行ける</span></a><button class="mn" type="button"><i></i>MENU</button>':(shop?SH.map(function(x){return '<a href="'+x[0]+'"'+(P.indexOf(x[0])===0?' class="cur"':'')+'>'+x[2]+'<span>'+x[1]+'</span></a>';}).join(""):
 '<a href="/odekake?v2t=0">'+I.now+'<span>開催中</span></a><a href="/odekake?v2t=1">'+I.up+'<span>これから</span></a><a href="/odekake?v2t=map">'+I.map+'<span>地図</span></a><a href="/tomari"'+(inn?' class="cur"':'')+'>'+I.inn+'<span>泊まり</span></a>')+'<button class="mn" type="button"><i></i>MENU</button>';
bar.querySelector(".mn").onclick=function(){var m=document.getElementById("umenu");if(m)m.click();};
document.body.appendChild(bar);document.documentElement.classList.add("v2bar-on");
function col(el,t){for(var k in PC){if(t.indexOf(k)===0){el.style.setProperty("--pc",PC[k]);return;}}}
document.querySelectorAll(".tabs button").forEach(function(b){col(b,b.textContent.trim());});
document.querySelectorAll(".ps").forEach(function(s){var h=s.querySelector("h2");if(h)col(s,h.textContent.trim());});document.querySelectorAll(".ps h2").forEach(function(h){col(h,h.textContent.trim());});
document.querySelectorAll(".pn a").forEach(function(a){col(a,a.textContent.trim());});
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",go);else go();
})();
