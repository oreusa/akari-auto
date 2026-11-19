/* 新しいHP（11/19）の共通の土台：空（昼の日差し・夜の星）・頭（ロゴ・昼夜）・下のバー・MENU・下から出る板・数え上がり。
   どのページも同じ物を読む。ページの中身は各ページの JS（odekake.js・ie.js …）が #main に作る。
   決まり：普通の役目＋こだわり1つ。動かすのは transform と opacity だけ。 */
(function(){
"use strict";
var H=document.documentElement,app=document.getElementById("app");
var CFG=JSON.parse(document.getElementById("cfg").textContent);
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
 yen:'<svg viewBox="0 0 24 24"><path d="M6 4l6 8 6-8M12 12v8M8 13h8M8 16.5h8"/></svg>',
 down:'<svg viewBox="0 0 24 24"><path d="M4 6l6 6 4-4 6 7"/><path d="M15 15h5v-5"/></svg>',
 star:'<svg viewBox="0 0 24 24"><path d="M12 4l2.4 5 5.4.6-4 3.7 1.1 5.3L12 16l-4.9 2.6 1.1-5.3-4-3.7 5.4-.6z"/></svg>',
 gift:'<svg viewBox="0 0 24 24"><rect x="4" y="9" width="16" height="11" rx="1.5"/><path d="M3 9h18M12 9v11M12 9c-1.5-3-5-4-5-1.5S10 9 12 9zm0 0c1.5-3 5-4 5-1.5S14 9 12 9z"/></svg>'};

/* ---- 骨組み ---- */
app.innerHTML='<div class="wrap"><header class="top"><a class="brand" href="/" aria-label="トップへ"><img id="logo" src="'+REG.logo+'" alt="'+REG.brand+'"><b>'+REG.brand+'</b></a>'+
 '<button class="tg" id="tg" role="switch" aria-checked="false" aria-label="夜の画面にする"><i class="kn"></i><span class="su"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path class="sp" d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/></svg></span><span class="mo"><svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg></span></button></header></div>'+
 '<main id="main"></main>'+
 '<div class="wrap"><footer class="ft">'+(CFG.foot||"")+'<br><a href="/">'+REG.brand+' トップ</a>　<a href="/privacy">プライバシー</a></footer></div>'+
 '<nav class="nav" id="nav" aria-label="すぐ移動">'+CFG.nav.map(function(n,i){return n.href?'<a href="'+n.href+'"'+(n.cur?' class="cur"':'')+'>'+IC[n.ic]+'<span>'+n.t+'</span></a>':'<button data-a="'+n.a+'"'+(i===0?' class="cur"':'')+'>'+IC[n.ic]+'<span>'+n.t+'</span></button>'}).join("")+'<button class="mn" id="mnb" aria-label="メニュー"><em></em><span>MENU</span></button></nav>'+
 '<div class="sh" id="sh" aria-hidden="true"><div class="bk"></div><div class="pn" role="dialog" aria-modal="true"><div class="grab"><i></i></div><button class="x" aria-label="閉じる">×</button><div id="shc"></div></div></div>'+
 '<div class="mu" id="mu"><div class="bk"></div><div class="pn"><div class="k">'+CFG.menu.k+'</div><ol>'+
 CFG.menu.items.map(function(m,i){return '<li><a href="'+m[1]+'"'+(m[2]?' class="here"':'')+' style="transition-delay:'+(60+i*40)+'ms"><small>0'+(i+1)+'</small>'+m[0]+'</a></li>'}).join("")+
 '</ol><div class="rel">'+CFG.menu.rel.map(function(r){return '<a href="'+r[1]+'">'+r[0]+'</a>'}).join("")+'</div></div></div>';

/* 数え上がり（data-n。小数は data-d で桁、data-f で 1,234 の形） */
function fmt(v,b){var d=+(b.dataset.d||0),s=d?v.toFixed(d):String(Math.round(v));if(b.dataset.f)s=s.replace(/\B(?=(\d{3})+(?!\d))/g,",");return (b.dataset.pre||"")+s}
function countUp(b){var n=+b.dataset.n,t0=performance.now();if(RM||!isFinite(n)){b.textContent=fmt(n,b);return}
  (function f(t){var k=Math.min(1,(t-t0)/900),e=1-Math.pow(1-k,3);b.textContent=fmt(n*e,b);if(k<1)requestAnimationFrame(f)})(t0)}
var cio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){cio.unobserve(e.target);countUp(e.target)}})},{rootMargin:"0px 0px -10% 0px"});
function counts(root){$$("[data-n]",root).forEach(function(b){b.textContent=fmt(0,b);cio.observe(b)})}
/* 見えたら伸びる棒（data-w＝0〜1） */
var bio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){bio.unobserve(e.target);e.target.style.transform="scaleX("+e.target.dataset.w+")"}})});
function bars(root){$$("[data-w]",root).forEach(function(b){if(RM)b.style.transform="scaleX("+b.dataset.w+")";else bio.observe(b)})}

/* ---- 下から出る板 ---- */
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
nav.addEventListener("click",function(e){var b=e.target.closest("[data-a]");if(!b||!navFn)return;navFn(b.dataset.a)});
function navCur(a){$$("#nav [data-a]").forEach(function(b){b.classList.toggle("cur",b.dataset.a===a)})}
/* 11/19 下へ流す間だけ隠し、指を止めたら（0.8秒）すぐ戻す。押した後に勝手に動いた時もバーが消えたままにならない */
var nvT;addEventListener("scroll",function(){var y=scrollY;if(Math.abs(y-ly)>8){nav.classList.toggle("hide",y>ly&&y>300);ly=y}clearTimeout(nvT);nvT=setTimeout(function(){nav.classList.remove("hide")},800)},{passive:true});
var mu=$("#mu");$("#mnb").onclick=function(){mu.classList.add("op")};$(".bk",mu).onclick=function(){mu.classList.remove("op")};

/* ---- 府県の玉（選んだ所へ滑る・周りを光が回る） ---- */
function seg(box,list,cur,on){box.innerHTML='<i class="pill"></i>'+list.map(function(p){return '<button data-v="'+esc(p[0])+'">'+esc(p[1])+'</button>'}).join("");
  var pill=$(".pill",box);function mv(){var b=$("button.on",box);if(!b)return;pill.style.width=b.offsetWidth+"px";pill.style.transform="translateX("+(b.offsetLeft-4)+"px)";pill.style.left="4px"}
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
  ready:function(){apply(H.classList.contains("nt"));largeTitle()}};
/* 11/19 iPhone の設定アプリの形：大きい題は下へ流すと薄れて、上の細い帯に小さく収まる。帯を押すと一番上へ */
function largeTitle(){var h=$(".h1t");if(!h)return;var tb=document.createElement("button");tb.id="tb";tb.setAttribute("aria-label","一番上へ");tb.textContent=h.textContent;document.body.appendChild(tb);
  tb.onclick=function(){scrollTo({top:0,behavior:RM?"auto":"smooth"})};var q=0,on=false;
  function f(){q=0;var r=h.getBoundingClientRect(),p=Math.max(0,Math.min(1,(60-r.top)/70));if(!RM){h.style.opacity=(1-p*.9).toFixed(3);h.style.transform="translateY("+(p*-6).toFixed(1)+"px) scale("+(1-p*.04).toFixed(3)+")"}
    var o=r.bottom<46;if(o!==on){on=o;tb.classList.toggle("on",o);H.classList.toggle("tbon",o)}}
  addEventListener("scroll",function(){if(!q)q=requestAnimationFrame(f)},{passive:true});f()}
})();
