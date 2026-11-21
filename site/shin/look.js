/* 11/20 見た目の見本（look.css）：A は後ろの光のにじみ、どれも流すとふわっと出る */
(function(){var H=document.documentElement;try{var _p=location.search.match(/[?&]pal=([0-3])/);if(_p)localStorage.setItem("tn_pal",_p[1]);var _pv=localStorage.getItem("tn_pal");if(_pv&&_pv!=="0")H.classList.add("lk-p"+_pv)}catch(e){}try{var _e=location.search.match(/[?&]edge=([0-3])/);if(_e)localStorage.setItem("tn_edge",_e[1]);var _ev=localStorage.getItem("tn_edge")||"1";if(_ev&&_ev!=="0")H.classList.add("lk-e"+_ev)}catch(e){}try{var _t=location.search.match(/[?&]ty=([01])/);if(_t)localStorage.setItem("tn_ty2",_t[1]);var _tv=localStorage.getItem("tn_ty2")||"1";if(_tv!=="1")H.classList.remove("lk-t1");if(_tv==="1"){H.classList.add("lk-t1");var _K=/kanto|lifenote/.test(location.hostname)?"KANTO":"KANSAI",_P=location.pathname.replace(/^\/shin/,"").replace(/\.html$/,""),_EN={"/odekake":"ODEKAKE — ","/illumination":"ILLUMINATION — ","/koyo":"AUTUMN LEAVES — ","/ima":"RIGHT NOW — ","/tomari":"STAY — ","/hatsumode":"NEW YEAR — ","/kaiten":"OPEN & CLOSE — ","/okaimono":"SHOPPING","/kau":"SHOPPING","/fudosan-list":"REAL ESTATE — ","/ie":"REAL ESTATE — "}[_P.replace(/-(osaka|kyoto|hyogo|nara|shiga|wakayama|tokyo|kanagawa|saitama|chiba|ibaraki|tochigi|gunma)$/,"")];if(_EN!==undefined){var _w=function(){var h=document.querySelector(".h1t");if(h){h.setAttribute("data-en",_EN.indexOf("—")>0?_EN+_K:_EN);/* 題は1行に収まるなら1行（「・」で折れて残るのを防ぐ）。13字まで・28px まで縮める */var tx=h.textContent.replace(/[\u200b]/g,"");if(tx.length<=14){var fit=function(){h.style.whiteSpace="nowrap";h.style.removeProperty("font-size");var pr=h.parentElement,cs=getComputedStyle(pr),av=pr.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight)-2,rg=document.createRange();rg.selectNodeContents(h);var tw=rg.getBoundingClientRect().width,fs=parseFloat(getComputedStyle(h).fontSize);/* 11/21 iPhone で右が切れた：h1 自身の幅は字に合わせて伸びるので、親の幅と字の本当の幅でくらべる */if(tw>av){var n=Math.floor(fs*av/tw*10)/10;if(n>=24)h.style.setProperty("font-size",n+"px","important");else h.style.whiteSpace=""}};fit();addEventListener("resize",fit);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fit)}}else setTimeout(_w,60)};_w()}}}catch(e){}try{var _h=location.search.match(/[?&]hue=([0-5])/);if(_h)localStorage.setItem("tn_hue",_h[1]);var _hv=localStorage.getItem("tn_hue")||"4";if(_hv&&_hv!=="0")H.classList.add("lk-h"+_hv)}catch(e){}if(!H.classList.contains("lk")||window.__lk)return;window.__lk=1;
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
var seen=new WeakSet();function scan(){[].forEach.call(document.querySelectorAll(".mc b,.c3n1 b,.c3n2 b,.c3ks b"),function(el){if(seen.has(el))return;seen.add(el);io.observe(el)})}
function start(){scan();new MutationObserver(scan).observe(document.body,{childList:true,subtree:true})}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start);else start();
var ims=[],tk=0;function par(){tk=0;var h=innerHeight;ims.forEach(function(im){var r=im.parentNode.getBoundingClientRect();if(r.bottom<0||r.top>h)return;var p=(r.top+r.height/2-h/2)/h;im.style.setProperty("--py",(p*-12).toFixed(1)+"px")})}
addEventListener("scroll",function(){if(!ims.length)ims=[].slice.call(document.querySelectorAll(".c3sd img,.c3t img,.c3kc .im img"));if(!tk)tk=requestAnimationFrame(par)},{passive:true})})();
/* 21:13 owner「めちゃくちゃ綺麗な画面になる提案、あれなんてゆうの？」→ グラスモーフィズム＋メッシュグラデーション（Stripe 型）。
   本物は「画面の一番上だけ、はっきりした色の光がゆっくり流れる帯・下は白」→ F に上の帯（.lk-hero）を足す */
(function(){var H=document.documentElement;if(!H.classList.contains("lk-f"))return;
function add(){if(document.querySelector(".lk-hero"))return;var d=document.createElement("div");d.className="lk-hero";d.setAttribute("aria-hidden","true");d.innerHTML="<i></i><i></i><i></i><i></i><i></i>";document.body.insertBefore(d,document.body.firstChild);/* 11/22 owner「動作見直して」：上の光の帯が見えていない間は動きを止めて、下に流す時を軽く */try{new IntersectionObserver(function(es){document.documentElement.classList.toggle("lk-off",!es[0].isIntersecting)}).observe(d)}catch(e){}}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",add);else add()})();
/* 11/21 6:06 owner「夜の星ってもっとシンプルでとても綺麗なのないの？」→ 見本 ?sky=1 澄んだ星空（白い星だけ・大きさは3つ・明るい星が数個ゆっくりまたたく）
   ?sky=2 ごく少ない星（星を数十だけ・またたかない・流れ星だけ残す）。?sky=0 で今の形。星は画面に貼り付き、流しても動かない */
(function(){var H=document.documentElement;var v="0";try{var m=location.search.match(/[?&]sky=([0-2])/);if(m)localStorage.setItem("tn_sky",m[1]);v=localStorage.getItem("tn_sky")||"1"}catch(e){}
if(v==="0")return;H.classList.add("lk-s"+v);
var cv,tw=[];function draw(){if(!cv){cv=document.createElement("canvas");cv.className="lk-sky";cv.setAttribute("aria-hidden","true");var host=document.getElementById("sky")||document.body;host.appendChild(cv)}
 var w=innerWidth,h=innerHeight,dp=Math.min(2,devicePixelRatio||1);cv.width=w*dp;cv.height=h*dp;var c=cv.getContext("2d");c.scale(dp,dp);
 var r=20251121;function rnd(){r=(r*16807)%2147483647;return r/2147483647}
 var n=v==="1"?Math.round(w*h/1800):18;
 for(var i=0;i<n;i++){var x=rnd()*w,y=rnd()*h,k=rnd(),sz,a;
  if(v==="1"){sz=k>.95?1.4:k>.75?.9:.55;a=k>.95?1:k>.75?.8:.5}else{sz=1.1+k*.6;a=.95}
  c.fillStyle="rgba(255,255,255,"+a+")";c.beginPath();c.arc(x,y,sz,0,7);c.fill();
  if(v==="1"&&k>.96){var g=c.createRadialGradient(x,y,0,x,y,7);g.addColorStop(0,"rgba(255,255,255,.22)");g.addColorStop(1,"rgba(255,255,255,0)");c.fillStyle=g;c.fillRect(x-7,y-7,14,14)}}
 tw.forEach(function(e){e.remove()});tw=[];if(v==="1"&&!matchMedia("(prefers-reduced-motion:reduce)").matches){for(var j=0;j<7;j++){var e=document.createElement("i");e.className="lk-tw";e.style.cssText="left:"+(rnd()*w).toFixed(0)+"px;top:"+(rnd()*h*.8).toFixed(0)+"px;animation-delay:-"+(rnd()*6).toFixed(1)+"s;animation-duration:"+(4+rnd()*4).toFixed(1)+"s";cv.parentNode.appendChild(e);tw.push(e)}}}
var t;function go(){draw();addEventListener("resize",function(){clearTimeout(t);t=setTimeout(draw,200)})}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",go);else go()})();
/* 11/21 上に貼り付く選ぶ帯を1段に：流している間は府県を「大阪 ▾」の1つの札にまとめ、開店閉店の「これから・開いた・閉まる」は下のバーと同じなので隠す */
(function(){function go(){var b=document.getElementById("bar"),s=document.getElementById("seg"),c=document.getElementById("chips");if(!b||!s||!c||b.querySelector(".lk-pf"))return;if(c.querySelectorAll("button").length<3||!c.offsetHeight)return;
var pf=document.createElement("button");pf.type="button";pf.className="chip lk-pf";pf.setAttribute("aria-label","地域を選ぶ");c.insertBefore(pf,c.firstChild);
function lab(){var o=s.querySelector(".on");pf.innerHTML="<span>"+(o?o.textContent:"地域")+"</span><svg width='10' height='10' viewBox='0 0 10 10' aria-hidden='true'><path d='M2 3.5l3 3 3-3' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round'/></svg>"}
lab();b.classList.add("lk-1r");new MutationObserver(function(){if(pf.parentNode!==c||c.firstChild!==pf){c.insertBefore(pf,c.firstChild);lab()}}).observe(c,{childList:true});
pf.addEventListener("click",function(e){e.stopPropagation();b.classList.toggle("lk-pfo")});
s.addEventListener("click",function(){setTimeout(function(){lab();b.classList.remove("lk-pfo")},0)});
new MutationObserver(function(){if(!b.classList.contains("stuck")&&b.classList.contains("lk-pfo"))b.classList.remove("lk-pfo")}).observe(b,{attributes:true,attributeFilter:["class"]})}
if(document.readyState==="complete")setTimeout(go,300);else addEventListener("load",function(){setTimeout(go,300)})})();
