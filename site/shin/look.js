/* 11/20 見た目の見本（look.css）：A は後ろの光のにじみ、どれも流すとふわっと出る */
(function(){var H=document.documentElement;try{var _p=location.search.match(/[?&]pal=([0-3])/);if(_p)localStorage.setItem("tn_pal",_p[1]);var _pv=localStorage.getItem("tn_pal");if(_pv&&_pv!=="0")H.classList.add("lk-p"+_pv)}catch(e){}if(!H.classList.contains("lk")||window.__lk)return;window.__lk=1;
function go(){if(H.classList.contains("lk-a")&&!document.querySelector(".lk-bg")){var b=document.createElement("div");b.className="lk-bg";b.setAttribute("aria-hidden","true");b.innerHTML="<i></i><i></i><i></i><i></i><i></i><b></b>";document.body.insertBefore(b,document.body.firstChild)}
 if(matchMedia("(prefers-reduced-motion:reduce)").matches||!("IntersectionObserver" in window))return;
 var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target)}})},{rootMargin:"0px 0px -6% 0px"});
 var seen=new WeakSet();function scan(){[].forEach.call(document.querySelectorAll(".mc,.go,.go2,.yh,.ls,.tb,.cmpt,.faq,.qr,.qr-h,.tiles,.rk li,.sec>h2,.dq"),function(el){if(seen.has(el))return;seen.add(el);var r=el.getBoundingClientRect();if(r.top<innerHeight*.92)return;el.classList.add("rv");io.observe(el)})}
 scan();new MutationObserver(function(){scan()}).observe(document.body,{childList:true,subtree:true})}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",function(){setTimeout(go,60)});else setTimeout(go,60)})();
/* 21:12 owner「僕のお洒落ってもうわかるんだよね？」→ お洒落＝色替えではなく、テクノロジーを感じる光と動き・触ると反応（バーの回る光と同じ考え）。色はほとんど無く少しだけ。
   F（lk-f）：①触ったカードのふちに指の所から光が走る ②数字が出る時に0から数え上がる ③題に光が横に流れる ④写真がゆっくり寄る・流すと奥行き */
(function(){var H=document.documentElement;if(!H.classList.contains("lk-f"))return;
var RM=matchMedia("(prefers-reduced-motion:reduce)").matches;
var CARD=".mc,.c3v,.qr a,.ls a,.fin,.go,.go2,.c3t,.cmpt,.tb,.yh a,.c3b a,.rk li,.c3kc,.vd,.faq details";
function glow(e){var c=e.target.closest&&e.target.closest(CARD);if(!c)return;var r=c.getBoundingClientRect();c.style.setProperty("--mx",(e.clientX-r.left)+"px");c.style.setProperty("--my",(e.clientY-r.top)+"px");c.classList.remove("lt");void c.offsetWidth;c.classList.add("lt");clearTimeout(c.__lt);c.__lt=setTimeout(function(){c.classList.remove("lt")},1500)}
document.addEventListener("pointerdown",glow,{passive:true});
if(RM)return;
function num(el){if(el.__n)return;var tn=null;for(var k=0;k<el.childNodes.length;k++){var x=el.childNodes[k];if(x.nodeType===3&&/\d/.test(x.nodeValue)){tn=x;break}}if(!tn)return;var t=tn.nodeValue,m=t.match(/^(\s*[+\-−]?)([\d,]+(?:\.\d+)?)(.*)$/);if(!m)return;el.__n=1;var dec=(m[2].split(".")[1]||"").length,v=parseFloat(m[2].replace(/,/g,"")),cm=m[2].indexOf(",")>=0,t0=performance.now(),D=700;
 function f(n){var s=n.toFixed(dec);if(cm){var p=s.split(".");p[0]=p[0].replace(/\B(?=(\d{3})+(?!\d))/g,",");s=p.join(".")}return m[1]+s+m[3]}
 (function st(now){var p=Math.min(1,(now-t0)/D),e=1-Math.pow(1-p,4);tn.nodeValue=f(v*e);if(p<1)requestAnimationFrame(st);else tn.nodeValue=t})(t0)}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;var el=e.target;io.unobserve(el);if(el.matches("h1,h2"))el.classList.add("shine");else num(el)})},{rootMargin:"0px 0px -8% 0px"});
var seen=new WeakSet();function scan(){[].forEach.call(document.querySelectorAll(".mc b,.c3n1 b,.c3n2 b,.c3ks b,.c3u h2,.m2h h1,.h1t,.sec>h2"),function(el){if(seen.has(el))return;seen.add(el);io.observe(el)})}
function start(){scan();new MutationObserver(scan).observe(document.body,{childList:true,subtree:true})}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start);else start();
var ims=[],tk=0;function par(){tk=0;var h=innerHeight;ims.forEach(function(im){var r=im.parentNode.getBoundingClientRect();if(r.bottom<0||r.top>h)return;var p=(r.top+r.height/2-h/2)/h;im.style.setProperty("--py",(p*-12).toFixed(1)+"px")})}
addEventListener("scroll",function(){if(!ims.length)ims=[].slice.call(document.querySelectorAll(".c3sd img,.c3t img,.c3kc .im img"));if(!tk)tk=requestAnimationFrame(par)},{passive:true})})();
/* 21:13 owner「めちゃくちゃ綺麗な画面になる提案、あれなんてゆうの？」→ グラスモーフィズム＋メッシュグラデーション（Stripe 型）。
   本物は「画面の一番上だけ、はっきりした色の光がゆっくり流れる帯・下は白」→ F に上の帯（.lk-hero）を足す */
(function(){var H=document.documentElement;if(!H.classList.contains("lk-f"))return;
function add(){if(document.querySelector(".lk-hero"))return;var d=document.createElement("div");d.className="lk-hero";d.setAttribute("aria-hidden","true");d.innerHTML="<i></i><i></i><i></i><i></i><i></i>";document.body.insertBefore(d,document.body.firstChild)}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",add);else add()})();
