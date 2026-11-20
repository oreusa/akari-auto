/* 新しいHP：関西おでかけ。役目＝行きたい所がすぐ見つかる。こだわり＝ストーリー・写真・扇のカード。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,el=S_.el,esc=S_.esc,TD=S_.TD,diff=S_.diff,md=S_.md,dd=S_.dd,RM=S_.RM,D=S_.data;
var dow=dd(TD).getUTCDay(),SAT=new Date(dd(TD).getTime()+((6-dow+7)%7)*864e5).toISOString().slice(0,10),SUN=new Date(dd(SAT).getTime()+864e5).toISOString().slice(0,10);
if(dow===0){SAT=TD;SUN=TD}
var G={art:["ART","#3B5BA5","#EEF1F8","アート・展示"],light:["LIGHT","#B7862A","#F8F2E6","光・イルミ"],koyo:["KOYO","#C0532B","#F9EEEA","紅葉"],flower:["FLOWER","#C2557A","#F9EDF2","花"],fes:["MATSURI","#B23A2E","#F8ECEB","まつり"],quest:["NAZOTOKI","#5B4B8A","#F0EEF6","謎とき"],play:["PLAY","#2E8B6E","#EAF4F0","あそぶ"],spot:["SPOT","#2F7D9A","#EAF3F6","スポット"],food:["FOOD","#C9702A","#FAF0E7","グルメ"],animal:["ANIMAL","#6F7F33","#F1F3E8","いきもの"],xmas:["XMAS","#2F7A4F","#EAF4EE","クリスマス"],hallo:["HALLOWEEN","#B45F1F","#FAEFE6","ハロウィン"],shop:["MARKET","#8A6A3F","#F5F0E8","マーケット"],hatsu:["HATSUMODE","#A23B3B","#F7ECEC","初詣"]};
var RG=S_.reg,PREF=RG.pref,PG=D.page||{};
/* 11/20 20:20 owner「いいと思う」→ 新しい地図と一覧をふだんの形に（?map2=0 でこの端末だけ前の形に戻せる） */
var M2=true;try{var _m=location.search.match(/[?&]map2=([01])/);if(_m)localStorage.setItem("tn_map2",_m[1]);M2=localStorage.getItem("tn_map2")!=="0"}catch(e){}
/* 見本：府県を選んだら覚える（おでかけの一覧だけ。府県のページ・イルミ・紅葉は覚えない） */
var PK="tn_odp_"+RG.n,REM=M2&&!PG.p&&!PG.st&&!PG.h1;
var IT=D.items.filter(function(x){return x.e>=TD}).map(function(x,i){x.i=i;x.st=x.s<=TD?"now":"up";x.left=diff(TD,x.e);x.g=G[x.k]||G.spot;return x});
var BYI={};IT.forEach(function(x){BYI[x.i]=x});
function avg(b){try{var h=Uint8Array.from(atob(b),function(c){return c.charCodeAt(0)}),hd=h[0]|h[1]<<8|h[2]<<16,l=(hd&63)/63,p=((hd>>6)&63)/31.5-1,q=((hd>>12)&63)/31.5-1,bb=l-2/3*p,r=(3*l-bb+q)/2,g=r-q;
  var f=function(v){return Math.round(255*Math.max(0,Math.min(1,v)))};return "rgb("+f(r)+","+f(g)+","+f(bb)+")"}catch(e){return ""}}
function img(x){return "/assets/ph/"+x.im}
function tile(x){return '<div class="tile" style="--gc:'+x.g[1]+';--gt:'+x.g[2]+'"><svg viewBox="0 0 24 24">'+(D.icons[x.k]||D.icons.spot||"")+'</svg><b>'+x.g[3]+'</b></div>'}
function lt(x){if(x.st==="up"){var n=diff(TD,x.s);return '<span class="lt">'+(n<=1?"あしたから":n+"日後から")+'</span>'}
  if(x.left===0)return '<span class="lt">きょうまで</span>';if(x.left<=7)return '<span class="lt">あと'+x.left+'日</span>';return '<span class="lt now">開催中</span>'}
function when(x){return x.st==="up"?md(x.s)+"から":md(x.e)+"まで"}
var Q=new URLSearchParams(location.search),S={p:Q.get("p")||PG.p||"",w:Q.get("w")||"now",g:Q.get("g")||"",n:24};
if(REM&&!Q.get("p")){try{var _rp=localStorage.getItem(PK);if(_rp&&PREF.indexOf(_rp)>=0)S.p=_rp}catch(e){}}
function saveQ(){var u=new URLSearchParams(location.search);["p","w","g"].forEach(function(k){if(S[k]&&!(k==="w"&&S[k]==="now"))u.set(k,S[k]);else u.delete(k)});
  history.replaceState(history.state,"",location.pathname+(u.toString()?"?"+u:""))}
/* 11/20 owner「他社より確実に上」：どのカードにも♡。押した物は「♡ 残した」で見返せる（この端末にだけ残る） */
var HK="tn_hv",HV={};try{HV=JSON.parse(localStorage.getItem(HK)||"{}")}catch(e){}
function hvKey(x){return x.o||x.t}
/* 一言と同じ書き出しの「場所」は2回同じ文になるので、場所の行は地域にする */
function vnOf(x){var v=x.v||x.a||"";if(x.hk&&v.slice(0,5)===x.hk.slice(0,5))return x.a&&x.a!==v?x.a:"";return v}
function hvSave(){try{localStorage.setItem(HK,JSON.stringify(HV))}catch(e){}}
var HVI='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.7c0 5.6-7.5 10.2-7.5 10.2z"/></svg>';
function inW(x,w){if(w==="now")return x.st==="now";if(w==="end")return x.st==="now"&&x.left<=7;if(w==="td")return x.st==="now"&&x.left===0;if(w==="new")return x.st==="up"&&diff(TD,x.s)<=7;if(w==="we")return x.s<=SUN&&x.e>=SAT;return x.st==="up"}
function base(x){if(PG.free&&!x.f)return false;if(S.g==="_hv")return !!HV[hvKey(x)]&&(!S.p||x.p===S.p);if(S.p&&x.p!==S.p)return false;if(S.g&&x.k!==S.g)return false;return true}
function wCounts(){var c={now:0,we:0,end:0,up:0,td:0,new:0};IT.forEach(function(x){if(!base(x))return;for(var w in c)if(inW(x,w))c[w]++});return c}
function pick(){return IT.filter(function(x){return base(x)&&inW(x,S.w)}).sort(function(a,b){
  if(S.w==="up"||S.w==="new")return a.s<b.s?-1:a.s>b.s?1:0;if(S.w==="end"||S.w==="td")return a.e<b.e?-1:a.e>b.e?1:0;
  var pa=(a.im?0:3)-(a.ok||0),pb=(b.im?0:3)-(b.ok||0);if(pa!==pb)return pa-pb;if((b.pp||0)!==(a.pp||0))return (b.pp||0)-(a.pp||0);return a.e<b.e?-1:a.e>b.e?1:0})}
var nNow=IT.filter(function(x){return x.st==="now"}).length;
var nEnd=IT.filter(function(x){return x.st==="now"&&x.left<=7}).length,nTd=IT.filter(function(x){return x.st==="now"&&x.left===0}).length,
 nWe=IT.filter(function(x){return x.s<=SUN&&x.e>=SAT}).length,nNew=IT.filter(function(x){return x.st==="up"&&diff(TD,x.s)<=7}).length,DT=dd(TD),EN=["SUNDAY","MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"][DT.getUTCDay()];
var T1=nTd?["きょうまで",nTd,"td"]:["7日以内に始まる",nNew,"new"];
S_.main.innerHTML='<div class="wrap"><section class="hero"><h1 class="h1t">'+esc(PG.h1||RG.n+"のおでかけ・イベント")+'</h1><p class="h1p">'+esc(PG.sub||RG.pfs)+'</p>'+
 '<p class="dl">'+(DT.getUTCMonth()+1)+'月'+DT.getUTCDate()+'日（'+"日月火水木金土"[DT.getUTCDay()]+'）<span>いま開催中 <b data-n="'+nNow+'">0</b>件</span></p>'+
 '</section>'+
 '<div class="st" id="st"></div><div class="sec"><h2>今週末のおすすめ</h2><small id="fno"></small></div></div>'+
 '<div class="fan" id="fan"></div>'+
 '<div class="wrap">'+(M2?'':'<div class="tiles qk"><button data-w="'+T1[2]+'"><small>'+T1[0]+'</small><b data-n="'+T1[1]+'">0</b><i>→</i></button><button data-w="end"><small>7日以内に終わる</small><b data-n="'+nEnd+'">0</b><i>→</i></button><button data-w="we"><small>この週末に行ける</small><b data-n="'+nWe+'">0</b><i>→</i></button></div>')+'<div id="sent"></div><div class="bar'+(M2?' m2b':'')+'" id="bar"><div class="seg'+(M2?' fit':'')+'" id="seg"></div><div class="chips" id="chips"></div></div>'+
 (M2?'<div class="wt" id="wt" role="tablist"></div><div class="cnt m2cnt"><h3 id="ch"></h3><button class="tomap" id="tomap"><svg viewBox="0 0 24 24"><path d="M9 4.5 3.5 6.6v13l5.5-2.1 6 2.1 5.5-2.1v-13L15 6.6z"/><path d="M9 4.5v13M15 6.6v13"/></svg>地図で見る</button></div>':'<div class="cnt"><h3 id="ch"></h3><small id="cs"></small></div>')+'<div class="grid" id="grid"></div><div id="mr"></div></div>'+
 '<div class="sv" id="sv"><div class="bars"></div><div class="hd"><img data-logo src="/assets/logo-s.png?v=2" alt=""><span></span><button aria-label="閉じる">×</button></div><div class="fr"></div><div class="tx"></div><i class="tp l"></i><i class="tp r"></i></div>';
S_.counts(S_.main);
if(!M2)$(".tiles").addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;S.w=b.dataset.w;S.n=24;sync();go(true);var top=$("#sent").getBoundingClientRect().top+scrollY;scrollTo({top:top,behavior:"smooth"})});

/* ストーリー（虹の輪のまま。見た印は前と同じ hx_seen に残す） */
var ST=(PG.st==="pref"?PREF.map(function(p){return [p,function(x){return x.p===p&&x.st==="now"}]}).concat([["無料",function(x){return x.f}],["これから",function(x){return x.st==="up"}]]):[["今週末",function(x){return x.s<=SUN&&x.e>=SAT}],["まもなく終了",function(x){return x.st==="now"&&x.left<=10}],["イルミ",function(x){return x.k==="light"}],["紅葉",function(x){return x.k==="koyo"}],["アート",function(x){return x.k==="art"}],["子どもと",function(x){return x.k==="play"||x.k==="animal"}],["無料",function(x){return x.f}],["近日開始",function(x){return x.st==="up"&&diff(TD,x.s)<=21}]])
 .map(function(s){var l=IT.filter(s[1]).sort(function(a,b){return ((a.im?0:3)-(a.ok||0))-((b.im?0:3)-(b.ok||0))}).slice(0,10);return {t:s[0],l:l}}).filter(function(s){return s.l.length>=2});
$("#st").innerHTML=ST.map(function(s,i){var c=s.l[0];return '<button data-s="'+i+'"><span class="rg">'+(c.im?'<img src="'+img(c)+'" alt="" loading="lazy">':'<span class="ph" style="display:block"></span>')+'</span><span>'+esc(s.t)+'</span></button>'}).join("");
var sv=$("#sv"),svS=null,svI=0,svA=null;
function svShow(){var s=ST[svS],x=s.l[svI];$(".hd span",sv).textContent=s.t+"　"+(svI+1)+"/"+s.l.length;
  $(".bars",sv).innerHTML=s.l.map(function(_,i){return '<i><b style="transform:scaleX('+(i<svI?1:0)+')"></b></i>'}).join("");
  $(".fr",sv).innerHTML=x.im?'<img src="'+img(x)+'" alt="">':tile(x);
  $(".tx",sv).innerHTML='<span class="tag" style="--gc:'+x.g[1]+'">'+x.g[3]+'</span><h3>'+esc(x.t)+'</h3><p>'+esc(x.hk||x.v||x.a)+'　'+when(x)+'</p><button data-i="'+x.i+'">くわしく見る</button>';
  try{var se=JSON.parse(localStorage.getItem("hx_seen")||"{}");se[x.t]=TD;localStorage.setItem("hx_seen",JSON.stringify(se))}catch(e){}
  if(svA)svA.cancel();var b=$$(".bars b",sv)[svI];svA=b.animate([{transform:"scaleX(0)"},{transform:"scaleX(1)"}],{duration:5200,fill:"forwards"});svA.onfinish=function(){svGo(1)}}
function svGo(d){var n=svI+d;if(n<0)n=0;if(n>=ST[svS].l.length){svClose();return}svI=n;svShow()}
function svOpen(i){svS=i;svI=0;sv.classList.add("op");document.body.style.overflow="hidden";svShow()}
function svClose(){if(svA)svA.cancel();sv.classList.remove("op");document.body.style.overflow=""}
$("#st").addEventListener("click",function(e){var b=e.target.closest("button");if(b)svOpen(+b.dataset.s)});
$(".tp.l",sv).onclick=function(){svGo(-1)};$(".tp.r",sv).onclick=function(){svGo(1)};$(".hd button",sv).onclick=svClose;
$(".tx",sv).addEventListener("click",function(e){var b=e.target.closest("button[data-i]");if(b){svClose();openItem(BYI[b.dataset.i])}});
var sy0=null;sv.addEventListener("touchstart",function(e){sy0=e.touches[0].clientY;if(svA)svA.pause()},{passive:true});
sv.addEventListener("touchend",function(e){var dy=e.changedTouches[0].clientY-(sy0||0);if(dy>90)svClose();else if(svA)svA.play()},{passive:true});

/* 今週の顔（扇のように重なり、めくると立体で回る） */
var FAN=IT.filter(function(x){return x.im&&x.s<=SUN&&x.e>=TD}).sort(function(a,b){return (b.hr?1:0)-(a.hr?1:0)||(a.lo?1:0)-(b.lo?1:0)||(b.ok||0)-(a.ok||0)||(b.pp||0)-(a.pp||0)||(b.hk?1:0)-(a.hk?1:0)||((a.i*7919+S_.seed)%97)-((b.i*7919+S_.seed)%97)}).slice(0,8);
var fan=$("#fan");
fan.innerHTML='<i class="pad"></i>'+FAN.map(function(x){return '<a class="fc" href="#" data-i="'+x.i+'"><span class="in" style="background-color:'+avg(x.th)+'"><img src="'+img(x)+'" alt="" loading="lazy" decoding="async"><span class="cap"><small>'+x.g[3]+'・'+esc(x.p)+'</small><b>'+esc(x.t)+'</b><span>'+when(x)+'</span></span></span></a>'}).join("")+'<i class="pad"></i>';
var fcs=$$(".fc",fan),fq=0;
function fanTick(){fq=0;var k=Math.round(fan.scrollLeft/((fcs[0]&&fcs[0].offsetWidth+12)||1));$("#fno").textContent=Math.min(fcs.length,k+1)+" / "+fcs.length}
fan.addEventListener("scroll",function(){if(!fq)fq=requestAnimationFrame(fanTick)},{passive:true});
fanTick();addEventListener("resize",fanTick);
fan.addEventListener("click",function(e){var a=e.target.closest(".fc");if(!a)return;e.preventDefault();openItem(BYI[a.dataset.i],$(".in",a))});

/* 絞り込み */
var setSeg=S_.seg($("#seg"),[["",RG.n]].concat(PREF.map(function(p){return [p,p]})),S.p,function(v){S.p=v;S.n=24;sync();go(true)});
function kinds(){var c={};IT.forEach(function(x){if(!S.p||x.p===S.p)c[x.k]=(c[x.k]||0)+1});return Object.keys(G).filter(function(k){return c[k]})}
function drawChips(){if(S.g==="_hv"&&!Object.keys(HV).length){S.g="";saveQ()}var ks=kinds();$("#chips").style.display=ks.length<2&&!Object.keys(HV).length?"none":"";var nh=Object.keys(HV).length;$("#chips").innerHTML='<button class="chip'+(S.g?"":" on")+'" data-g="">すべて</button>'+(nh?'<button class="chip hvc'+(S.g==="_hv"?" on":"")+'" data-g="_hv">'+HVI+'残した '+nh+'</button>':"")+kinds().map(function(k){return '<button class="chip'+(S.g===k?" on":"")+'" data-g="'+k+'" style="--c:'+G[k][1]+'"><i></i>'+G[k][3]+'</button>'}).join("")}
$("#chips").addEventListener("click",function(e){var b=e.target.closest(".chip");if(!b)return;S.g=b.dataset.g;S.n=24;sync();go(true)});
function sync(){drawChips();S_.navCur(S.w);saveQ();if(REM)try{if(S.p)localStorage.setItem(PK,S.p);else localStorage.removeItem(PK)}catch(e){}}
var cache={};
function card(x){if(cache[x.i])return cache[x.i];
  var a=el('<a class="cd" href="'+(x.o?"/o/"+x.o:esc(x.u))+'" data-i="'+x.i+'" style="--gc:'+x.g[1]+'"><div class="im" style="background-color:'+(x.th?avg(x.th):x.g[2])+'">'+(x.im?'<img alt="" loading="lazy" decoding="async" src="'+img(x)+'">':tile(x))+'</div>'+
   '<span class="hv'+(HV[hvKey(x)]?" on":"")+'" role="button" tabindex="0" aria-label="♡で残す" aria-pressed="'+(HV[hvKey(x)]?"true":"false")+'">'+HVI+'</span><div class="lb"><span class="g">'+x.g[3]+'</span><span>'+esc(x.p)+'</span>'+lt(x)+'</div><h4>'+esc(x.t)+'</h4>'+(x.hk?'<p class="hk">'+esc(x.hk)+'</p>':'')+'<div class="dt">'+when(x)+'</div><div class="vn">'+esc(vnOf(x))+'</div></a>');
  var im=$("img",a);if(im){if(im.complete)im.classList.add("ld");else im.onload=function(){im.classList.add("ld")}}
  return cache[x.i]=a}
var grid=$("#grid"),first=true;
function hvTap(e){var h=e.target.closest&&e.target.closest(".hv");if(!h)return;e.preventDefault();e.stopPropagation();
  var c=h.closest(".cd"),x=IT.filter(function(y){return String(y.i)===c.dataset.i})[0];if(!x)return;var k=hvKey(x);
  if(HV[k])delete HV[k];else{HV[k]=1;try{navigator.sendBeacon("/c",JSON.stringify({k:"♡："+x.t.slice(0,60)}))}catch(er){}}
  hvSave();h.classList.toggle("on",!!HV[k]);h.setAttribute("aria-pressed",HV[k]?"true":"false");
  if(!RM)h.animate([{transform:"scale(1)"},{transform:"scale(1.35)"},{transform:"scale(1)"}],{duration:360,easing:"cubic-bezier(.3,1.6,.5,1)"});
  var was=S.g;drawChips();if(was==="_hv")go(true)}
grid.addEventListener("click",hvTap,true);grid.addEventListener("keydown",function(e){if((e.key==="Enter"||e.key===" ")&&e.target.classList&&e.target.classList.contains("hv"))hvTap(e)},true);
function go(anim){var L=pick(),show=L.slice(0,S.n),pr=S.p||RG.n,wl={now:"開催中",we:"今週末",up:"これから",end:"7日以内に終わる",td:"きょうまで",new:"7日以内に始まる"}[S.w];
  if(M2){var wc=wCounts();$("#wt").innerHTML=[["now","開催中"],["we","今週末"],["end","まもなく終了"],["up","これから"]].map(function(w){return '<button role="tab" data-w="'+w[0]+'" aria-selected="'+(S.w===w[0])+'"'+(S.w===w[0]?' class="on"':'')+'>'+w[1]+'<small>'+wc[w[0]]+'</small></button>'}).join("");
    $("#ch").innerHTML=esc(pr)+(S.g==="_hv"?"・♡で残した":S.g&&G[S.g]?"・"+G[S.g][3]:"")+(S.w==="td"||S.w==="new"?"・"+wl:"")+" <b data-n='"+L.length+"'>"+L.length+"</b>件"+(S.w==="we"?'<small>'+md(SAT)+"・"+md(SUN).replace(/（.）/,"")+'</small>':"")}
  else{$("#ch").innerHTML=esc(pr)+"・"+(S.g==="_hv"?"♡で残した":wl)+" <b data-n='"+L.length+"'>"+L.length+"</b>件";$("#cs").textContent=S.g==="_hv"?"この端末にだけ残っています":S.g&&G[S.g]?G[S.g][3]:(S.w==="we"?md(SAT)+"・"+md(SUN).replace(/（.）/,""):"")}
  if(anim&&!first)S_.countUp($("#ch b"));
  var old={};if(anim&&!RM)$$(".cd",grid).forEach(function(c){old[c.dataset.i]=c.getBoundingClientRect()});
  var frag=document.createDocumentFragment();show.forEach(function(x){frag.appendChild(card(x))});grid.replaceChildren(frag);
  if(!L.length)grid.innerHTML='<div class="none" style="grid-column:1/-1">この条件のおでかけは、いまはありません</div>';
  $("#mr").innerHTML=L.length>S.n?'<button class="more">もっと見る（残り'+(L.length-S.n)+'件）</button>':"";
  if(anim&&!RM)$$(".cd",grid).forEach(function(c,k){var o=old[c.dataset.i],n=c.getBoundingClientRect();
    if(o){var dx=o.left-n.left,dy=o.top-n.top;if(dx||dy)c.animate([{transform:"translate("+dx+"px,"+dy+"px)"},{transform:"none"}],{duration:480,easing:"cubic-bezier(.2,.9,.25,1)"})}
    else if(n.top<innerHeight+40)c.animate([{opacity:0,transform:"translateY(14px) scale(.98)"},{opacity:1,transform:"none"}],{duration:420,delay:Math.min(k,8)*35,easing:"cubic-bezier(.2,.9,.25,1)",fill:"backwards"})});
  if(anim){var top=$("#sent").getBoundingClientRect().top+scrollY;if(scrollY>top)scrollTo({top:top,behavior:"smooth"})}
  first=false}
$("#mr").addEventListener("click",function(e){if(e.target.closest(".more")){S.n+=24;go(false)}});
sync();go(false);
new IntersectionObserver(function(e){$("#bar").classList.toggle("stuck",!e[0].isIntersecting)}).observe($("#sent"));
function lit(e){var c=e.target.closest&&e.target.closest(".cd");if(!c)return;var r=$(".im",c).getBoundingClientRect();c.style.setProperty("--x",(e.clientX-r.left)+"px");c.style.setProperty("--y",(e.clientY-r.top)+"px");c.classList.add("lit");clearTimeout(c._t);c._t=setTimeout(function(){c.classList.remove("lit")},700)}
grid.addEventListener("pointermove",function(e){if(e.pointerType==="mouse")lit(e)});

/* 1件の板 */
function openItem(x,from){if(!x)return;var tot=Math.max(1,diff(x.s,x.e)),gone=Math.max(0,Math.min(tot,diff(x.s,TD))),pc=x.st==="now"?gone/tot:0,mq=encodeURIComponent((x.v||"")+" "+(x.a||x.p));
  S_.sheet('<div class="pim" style="background-color:'+(x.th?avg(x.th):x.g[2])+'">'+(x.im?'<img src="'+img(x)+'" alt="">':tile(x))+'</div><div class="bd" style="--gc:'+x.g[1]+'">'+
   '<div class="lb"><span class="g">'+x.g[3]+'</span><span>'+esc(x.p)+'・'+esc(x.a)+'</span></div><h2>'+esc(x.t)+'</h2>'+(x.hk?'<p class="hk">'+esc(x.hk)+'</p>':"")+
   '<div class="per"><div class="row"><span>'+md(x.s)+'</span><span>'+md(x.e)+'</span></div><div class="tr"><i data-w="'+pc.toFixed(3)+'" style="background:'+x.g[1]+'"></i>'+(x.st==="now"?'<b style="left:'+(pc*100)+'%;border-color:'+x.g[1]+'"></b>':"")+'</div>'+
   '<div class="big">'+(x.pk?(x.st==="up"?"見頃の時期まで あと"+diff(TD,x.s)+"日":"いまが見頃の時期です"):x.st==="up"?"あと"+diff(TD,x.s)+"日で始まります":x.left===0?"きょうまで":"終わりまで あと"+x.left+"日")+'</div></div>'+
   '<dl class="kv">'+(x.v?'<dt>会場</dt><dd>'+esc(x.v)+'</dd>':"")+'<dt>場所</dt><dd>'+esc(x.a||x.p)+'</dd>'+(x.h?'<dt>時間</dt><dd>'+esc(x.h)+'</dd>':"")+(x.fe?'<dt>料金</dt><dd>'+esc(x.fe)+'</dd>':x.f?'<dt>料金</dt><dd>無料</dd>':"")+(x.pk?'<dt>見頃</dt><dd>'+esc(x.pk)+'</dd>':"")+'</dl>'+
   (x.ds?'<p class="ds">'+esc(x.ds)+'</p>':"")+
   '<div class="acts"><a class="pr" href="'+esc(x.u)+'" target="_blank" rel="noopener">公式サイトで確かめる</a><a href="https://www.google.com/maps/search/?api=1&query='+mq+'" target="_blank" rel="noopener">地図で開く</a>'+(x.o?'<a href="/o/'+x.o+'">くわしいページ</a>':'<button data-share="1">送る</button>')+'</div>'+
   (x.cr?'<p class="cr">写真：'+(x.cu?'<a href="'+esc(x.cu)+'" target="_blank" rel="noopener">'+esc(x.cr)+'</a>':esc(x.cr))+'</p>':"")+'</div>',from)}
grid.addEventListener("click",function(e){var a=e.target.closest(".cd");if(!a||e.metaKey||e.ctrlKey)return;e.preventDefault();openItem(BYI[a.dataset.i],$(".im",a))});

/* ---- 地図（府県の色の地図はそのまま・まわりを作り直し）。いまの絞り込みと同じ物が出る ---- */
var PC=RG.pc,FL=RG.fl;
var LB=RG.lb;
var mp=null,vb={x:10,y:15,w:200,h:250},mpL=[],mpSel=-1,moved=false;
function mapOpen(){if(!mp){mp=el('<div class="mp" id="mp"><div class="mph"><b>'+RG.n+'おでかけマップ</b><small id="mpn"></small><button class="mpx" aria-label="閉じる">×</button></div>'+
  '<svg id="mps" viewBox="'+RG.vb+'" preserveAspectRatio="xMidYMid meet"><g id="mpg"><g class="nb">'+D.map.nb.map(function(d){return '<path d="'+d+'"/>'}).join("")+'</g>'+
  Object.keys(D.map.pref).map(function(p){return '<path class="pf" data-p="'+p+'" d="'+D.map.pref[p]+'" style="--f:'+FL[p]+';--c:'+PC[p]+'"/>'}).join("")+
  Object.keys(LB).map(function(p){return '<text class="pl" x="'+LB[p][0]+'" y="'+LB[p][1]+'" style="fill:'+PC[p]+'">'+p+'</text>'}).join("")+'<g id="mpp"></g></g></svg>'+
  '<div class="mpz"><button data-z="1.6">＋</button><button data-z="0.625">－</button><button data-z="0">全体</button></div><div class="mpc" id="mpc"></div></div>');document.getElementById("app").appendChild(mp);
  $(".mpx",mp).onclick=function(){mapClose()};mapGest();
  $(".mpz",mp).addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;var z=+b.dataset.z;if(!z)fit(10,15,200,250);else zoom(z,vb.x+vb.w/2,vb.y+vb.h/2,true)});
  $("#mps").addEventListener("click",function(e){if(moved)return;var c=e.target.closest(".pin");if(c){selPin(+c.dataset.k,true);return}var f=e.target.closest(".pf");if(f){var bb=f.getBBox();fit(bb.x-6,bb.y-6,bb.width+12,bb.height+12)}});
  $("#mpc").addEventListener("scroll",function(){clearTimeout(mp._t);mp._t=setTimeout(function(){var c=$("#mpc"),w=c.firstChild?c.firstChild.offsetWidth+10:1,k=Math.round(c.scrollLeft/w);if(k!==mpSel)selPin(k,false)},90)},{passive:true});
  $("#mpc").addEventListener("click",function(e){var a=e.target.closest(".mcd");if(a){e.preventDefault();openItem(BYI[a.dataset.i])}})}
  history.pushState({mp:1},"");mp.classList.add("op");document.body.style.overflow="hidden";drawPins();
  if(S.p){var f=$('.pf[data-p="'+S.p+'"]',mp),bb=f.getBBox();fit(bb.x-6,bb.y-6,bb.width+12,bb.height+12,true)}else fit(10,15,200,250,true)}
function mapClose(back){if(!mp||!mp.classList.contains("op"))return;mp.classList.remove("op");document.body.style.overflow="";if(back!==false&&history.state&&history.state.mp)history.back();S_.navCur(S.w)}
addEventListener("popstate",function(){if(mp&&mp.classList.contains("op")&&!(history.state&&(history.state.mp||history.state.sh)))mapClose(false)});
function drawPins(){mpL=pick().filter(function(x){return x.xy});$("#mpn").textContent=(S.p||RG.n)+"・"+{now:"開催中",we:"今週末",up:"これから",end:"まもなく終わる",td:"きょうまで",new:"もうすぐ始まる"}[S.w]+" "+mpL.length+"か所";
  $$(".pf",mp).forEach(function(f){f.classList.toggle("dim",!!S.p&&f.dataset.p!==S.p)});
  $("#mpp").innerHTML=mpL.map(function(x,k){return '<g class="pin" data-k="'+k+'" transform="translate('+x.xy[0]+' '+x.xy[1]+')"><g class="pi" style="animation-delay:'+Math.min(k,40)*18+'ms"><circle class="ring" r="4.2" style="stroke:'+x.g[1]+'"/><circle class="dt2" r="2.1" style="fill:'+x.g[1]+'"/></g></g>'}).join("");
  $("#mpc").innerHTML=mpL.map(function(x){return '<a class="mcd" href="#" data-i="'+x.i+'" style="--gc:'+x.g[1]+'"><span class="mim" style="background-color:'+(x.th?avg(x.th):x.g[2])+'">'+(x.im?'<img src="'+img(x)+'" alt="" loading="lazy">':tile(x))+'</span><span class="mtx"><span class="lb"><span class="g">'+x.g[3]+'</span><span>'+esc(x.p)+'</span>'+lt(x)+'</span><b>'+esc(x.t)+'</b><small>'+when(x)+'・'+esc(x.v||x.a)+'</small></span></a>'}).join("");
  mpSel=-1;if(mpL.length)selPin(0,false,true);pinScale()}
function selPin(k,fromPin,quiet){mpSel=k;$$(".pin",mp).forEach(function(p){p.classList.toggle("on",+p.dataset.k===k)});var on=$('.pin[data-k="'+k+'"]',mp);if(on)on.parentNode.appendChild(on);
  if(fromPin){var c=$("#mpc"),a=c.children[k];if(a)c.scrollTo({left:a.offsetLeft-(c.clientWidth-a.offsetWidth)/2,behavior:"smooth"})}
  var x=mpL[k];if(!quiet&&x){var cx=x.xy[0],cy=x.xy[1];if(cx<vb.x+vb.w*.15||cx>vb.x+vb.w*.85||cy<vb.y+vb.h*.15||cy>vb.y+vb.h*.7)fit(cx-vb.w/2,cy-vb.h*.42,vb.w,vb.h)}}
function setVB(){$("#mps").setAttribute("viewBox",vb.x+" "+vb.y+" "+vb.w+" "+vb.h);pinScale()}
function pinScale(){var s=Math.max(.35,Math.min(1.2,vb.w/200));$$(".pi",mp).forEach(function(p){p.setAttribute("transform","scale("+s+")")});$$(".pl",mp).forEach(function(t){t.style.fontSize=(9*s)+"px"})}
function fit(x,y,w,h,inst){var sv=$("#mps"),r=sv.clientWidth/Math.max(1,sv.clientHeight);if(w/h<r){var nw=h*r;x-=(nw-w)/2;w=nw}else{var nh=w/r;y-=(nh-h)/2;h=nh}
  if(inst||RM){vb={x:x,y:y,w:w,h:h};setVB();return}var a={x:vb.x,y:vb.y,w:vb.w,h:vb.h},t0=performance.now();
  (function f(t){var k=Math.min(1,(t-t0)/520),e=1-Math.pow(1-k,3);vb={x:a.x+(x-a.x)*e,y:a.y+(y-a.y)*e,w:a.w+(w-a.w)*e,h:a.h+(h-a.h)*e};setVB();if(k<1)requestAnimationFrame(f)})(t0)}
function zoom(z,cx,cy,anim){var w=Math.max(18,Math.min(260,vb.w/z)),h=vb.h*w/vb.w;var x=cx-(cx-vb.x)*w/vb.w,y=cy-(cy-vb.y)*h/vb.h;if(anim)fit(x,y,w,h);else{vb={x:x,y:y,w:w,h:h};setVB()}}
function mapGest(){var sv=$("#mps"),pts={},st=null;
  function scl(){var r=sv.getBoundingClientRect();return Math.max(vb.w/r.width,vb.h/r.height)}
  function toSvg(cx,cy){var r=sv.getBoundingClientRect(),s=scl(),ox=(r.width*s-vb.w)/2,oy=(r.height*s-vb.h)/2;return [vb.x-ox+(cx-r.left)*s,vb.y-oy+(cy-r.top)*s]}
  function snap(){st={vb:{x:vb.x,y:vb.y,w:vb.w,h:vb.h},pts:JSON.parse(JSON.stringify(pts))}}
  sv.addEventListener("pointerdown",function(e){pts[e.pointerId]=[e.clientX,e.clientY];if(Object.keys(pts).length===1)moved=false;snap()});
  sv.addEventListener("pointermove",function(e){if(!pts[e.pointerId]||!st)return;pts[e.pointerId]=[e.clientX,e.clientY];var ids=Object.keys(pts);
    if(ids.length===1){var p0=st.pts[ids[0]];if(!p0)return;var dx=e.clientX-p0[0],dy=e.clientY-p0[1];if(Math.abs(dx)+Math.abs(dy)>6)moved=true;if(!moved)return;var s=scl();vb={x:st.vb.x-dx*s,y:st.vb.y-dy*s,w:st.vb.w,h:st.vb.h};setVB()}
    else{var a0=st.pts[ids[0]],b0=st.pts[ids[1]],a1=pts[ids[0]],b1=pts[ids[1]];if(!a0||!b0)return;moved=true;var d0=Math.hypot(a0[0]-b0[0],a0[1]-b0[1]),d1=Math.hypot(a1[0]-b1[0],a1[1]-b1[1]);
      vb={x:st.vb.x,y:st.vb.y,w:st.vb.w,h:st.vb.h};var c=toSvg((a0[0]+b0[0])/2,(a0[1]+b0[1])/2);zoom(d1/Math.max(1,d0),c[0],c[1],false)}});
  function up(e){delete pts[e.pointerId];snap()}
  sv.addEventListener("pointerup",up);sv.addEventListener("pointercancel",up);sv.addEventListener("pointerleave",up);
  sv.addEventListener("wheel",function(e){e.preventDefault();var c=toSvg(e.clientX,e.clientY);zoom(e.deltaY<0?1.15:1/1.15,c[0],c[1],false)},{passive:false})}

/* 見本：新しい地図（map2.js を開く時だけ読む） */
var O=S_.od={S:S,saveQ:saveQ,byi:BYI,openItem:openItem,pick:pick,counts:wCounts,img:img,avg:avg,tile:tile,lt:lt,when:when,icon:function(k){return D.icons[k]||D.icons.spot||""},gname:function(k){return k==="_hv"?"♡で残した物":G[k]?G[k][3]:""},
  changed:function(){S.n=24;setSeg(S.p);sync();go(false)}};
function map2(){if(O.mapOpen){O.mapOpen();return}var s=document.createElement("script");s.src="/shin/map2.js?v=1120d";s.onload=function(){O.mapOpen()};document.head.appendChild(s)}
if(M2)$("#wt").addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;S.w=b.dataset.w;S.n=24;sync();go(true)});
if(M2)$("#tomap").onclick=map2;
S_.onNav(function(a){if(a==="map"){S_.navCur("map");if(M2)map2();else mapOpen();return}if(M2&&O.mapClose)O.mapClose();else mapClose();S.w=a;S.n=24;sync();go(true);var top=$("#sent").getBoundingClientRect().top+scrollY;scrollTo({top:top,behavior:"smooth"})});
S_.navCur(S.w);S_.ready();
})();
