/* 11/11 オーナー「hpを一掃テクノロジーっぽく。スラスラ動作、浮かび上がるような今どきの」
   tech.css と組。night.js が html に tk（動き）／tk2（動き＋デザイン）を付けた時だけ読まれる。
   ページの中身・配置には触らない。失敗しても何も起きないように、全部 try の中。
   月（TOWN）で直したら、燈（LIFE）の site/assets/ にそのまま写す。 */
(function(){
  "use strict";
  var d=document,h=d.documentElement;
  if(!h.classList.contains("tk")||window.__tk)return;window.__tk=1;
  var RM=false;try{RM=matchMedia("(prefers-reduced-motion:reduce)").matches;}catch(e){}
  /* iPhone は、何か1つ touchstart を聞いていないと「押している間」の見た目が出ない */
  try{d.addEventListener("touchstart",function(){},{passive:true});}catch(e){}
  if(RM)return;
  var SD=false;try{SD=CSS.supports("animation-timeline:view()");}catch(e){}
  h.classList.add(SD?"tk-sd":"tk-io");
  var IO="IntersectionObserver" in window,MO="MutationObserver" in window;

  /* ④ 上の細い線：どこまで読んだか */
  function bar(){try{if(d.getElementById("tkbar")||!d.body)return;var b=d.createElement("div");b.id="tkbar";b.setAttribute("aria-hidden","true");d.body.appendChild(b);
    if(!SD){var tick=0,upd=function(){tick=0;var m=h.scrollHeight-innerHeight;b.style.transform="scaleX("+(m>0?Math.min(1,Math.max(0,scrollY/m)):0)+")";};
      addEventListener("scroll",function(){if(!tick)tick=requestAnimationFrame(upd);},{passive:true});upd();}
  }catch(e){}}

  /* ⑤ 古い端末むけ：見えた時に1回だけ浮かび上がる（新しい端末は CSS だけで動く） */
  var RSEL="#wsec>.it,#wsec>.pr5,#wsec>.wh,.past>*,.tip,.fx>*,.wrap>.sns,.wrap>.ft,.lists>h2,.prom li,.wrap>p,.tk-v";
  var io=null;
  if(!SD&&IO){try{io=new IntersectionObserver(function(es){var n=0;es.forEach(function(en){if(!en.isIntersecting)return;var el=en.target;io.unobserve(el);
    el.style.setProperty("--tkd",Math.min(n++,5)*60+"ms");el.classList.add("tk-on");
    setTimeout(function(){el.classList.remove("tk-r","tk-on");el.style.removeProperty("--tkd");},1500);});},{rootMargin:"0px 0px -70px 0px",threshold:.05});}catch(e){io=null;}}
  function arm(){if(!io)return;try{var q=d.querySelectorAll(RSEL);for(var i=0;i<q.length;i++){var el=q[i];if(el.__tk)continue;el.__tk=1;
    var r=el.getBoundingClientRect();if(r.top<innerHeight-70)continue; /* もう見えている物・通りすぎた物は隠さない（ちらつかせない） */
    el.classList.add("tk-r");io.observe(el);}}catch(e){}}

  /* ⑨ 数字が数え上がる。最後は必ず元の文字に戻す。
     途中でページ側が数字を書きかえたら、すぐ手を放す（数字をまちがえない）。 */
  function numNode(el){for(var n=el.firstChild;n;n=n.nextSibling){if(n.nodeType===3&&/\d/.test(n.nodeValue))return n;}return null;}
  function parse(s){var m=/^(\D*?)(\d{1,3}(?:,\d{3})+|\d+)(\D*)$/.exec(s);if(!m)return null;return{pre:m[1],v:parseInt(m[2].replace(/,/g,""),10),post:m[3],comma:m[2].indexOf(",")>=0};}
  function fmt(p,v){var s=String(v);if(p.comma)s=s.replace(/\B(?=(\d{3})+$)/g,",");return p.pre+s+p.post;}
  function run(el,from,ms){try{var tn=numNode(el);if(!tn||el.__tkw)return;var fin=tn.nodeValue,p=parse(fin);if(!p||p.v===from||p.v>99999)return;
    var t0=0,last=fmt(p,from);el.__tkw=1;tn.nodeValue=last;
    var end=function(){el.__tkw=0;var n=numNode(el);el.__tkl=n?n.nodeValue:"";};
    var step=function(t){if(!t0)t0=t;if(!tn.parentNode||tn.nodeValue!==last){end();return;} /* ページ側が書きかえた → やめる */
      var k=Math.min(1,(t-t0)/ms),e=1-Math.pow(1-k,4);
      if(k>=1){tn.nodeValue=fin;end();return;}
      last=fmt(p,Math.round(from+(p.v-from)*e));tn.nodeValue=last;requestAnimationFrame(step);};
    requestAnimationFrame(step);}catch(e){try{el.__tkw=0;}catch(_){}}}
  /* 見えた時に 0 から1回（開いた時にもう見えている数字は動かさない） */
  var co=null;if(IO){try{co=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;co.unobserve(en.target);run(en.target,0,900);});},{threshold:.6});}catch(e){co=null;}}
  function carm(){if(!co)return;try{var q=d.querySelectorAll(".ls .st b,#wsec>.wh b");for(var i=0;i<q.length;i++){if(q[i].__tkc)continue;q[i].__tkc=1;var r=q[i].getBoundingClientRect();
    if(r.top<innerHeight&&r.bottom>0&&r.left<innerWidth&&r.right>0)continue;co.observe(q[i]);}}catch(e){}}
  /* 切り替えで数字が変わった時：前の数 → 新しい数（地図の件数・しぼりこみの件数・開催中） */
  function live(el){try{if(!MO||!el||el.__tkm)return;el.__tkm=1;var tn=numNode(el);el.__tkl=tn?tn.nodeValue:"";
    new MutationObserver(function(){if(el.__tkw)return;var n=numNode(el),now=n?n.nodeValue:"";if(now===el.__tkl)return;
      var a=parse(el.__tkl||""),b=parse(now);el.__tkl=now;if(a&&b&&a.pre===b.pre&&a.post===b.post)run(el,a.v,520);
    }).observe(el,{childList:true,characterData:true,subtree:true});}catch(e){}}
  function liveAll(){try{var q=d.querySelectorAll(".kmap .lb text.cnt,.fold1 em,.wc b,#tnow b");for(var i=0;i<q.length;i++)live(q[i]);}catch(e){}}

  /* tk2：表紙の「きょう」の行に、1秒ずつ進む時計 */
  var ck=null;
  function clock(){try{if(!h.classList.contains("tk2")||ck||!d.getElementById("today"))return;ck=d.createElement("span");ck.className="tkclk";ck.setAttribute("aria-hidden","true");
    var lab=d.createElement("i");lab.textContent="JST";ck.appendChild(lab);var ctx=d.createTextNode("");ck.appendChild(ctx);
    var two=function(n){return(n<10?"0":"")+n;},tk=function(){try{var td=d.querySelector("#today>div");if(!td)return;if(ck.parentNode!==td)td.appendChild(ck); /* ページ側が行を書き直しても、付け直す */
      var t=new Date(Date.now()+9*3600e3);ctx.nodeValue=two(t.getUTCHours())+":"+two(t.getUTCMinutes())+":"+two(t.getUTCSeconds());}catch(e){}};
    tk();setInterval(tk,1000);}catch(e){}}

  /* tk2：表紙の切り替えの白い札が、押した所へすべる */
  function pill(){try{if(!h.classList.contains("tk2"))return;var L=d.getElementById("lens");if(!L)return;
    var set=function(){try{var on=L.querySelector("button.on");if(!on||!on.offsetWidth){if(L.classList.contains("tkp"))L.classList.remove("tkp");return;}
      L.style.setProperty("--lx",on.offsetLeft+"px");L.style.setProperty("--lw",on.offsetWidth+"px");
      var c=getComputedStyle(on).getPropertyValue("--c");if(c)L.style.setProperty("--lc",c.trim());if(!L.classList.contains("tkp"))L.classList.add("tkp");}catch(e){}}; /* 同じ札を付け直すと、見張りが自分を呼び続けて固まる。必ず「まだ無い時だけ」 */
    set();if(L.__tkp)return;L.__tkp=1;
    if(MO)new MutationObserver(set).observe(L,{attributes:true,attributeFilter:["class"],subtree:true,childList:true});
    addEventListener("resize",set,{passive:true});try{if(d.fonts&&d.fonts.ready)d.fonts.ready.then(set);}catch(e){}
  }catch(e){}}
  /* tk2：地図の府県ごとに、細い輪が静かに広がる */
  function pings(){try{if(!h.classList.contains("tk2"))return;var gs=d.querySelectorAll(".kmap .lb>g");for(var i=0;i<gs.length;i++){var g=gs[i];if(g.__tkp||g.querySelector(".tkping"))continue;g.__tkp=1;
    var jp=g.querySelector("text.jp"),c=d.createElementNS("http://www.w3.org/2000/svg","circle");c.setAttribute("class","tkping");c.setAttribute("cx","0");c.setAttribute("cy","12");c.setAttribute("r","46");
    c.setAttribute("stroke",(jp&&jp.getAttribute("fill"))||"#8C7B6E");c.style.animationDelay=(i*0.6)+"s";g.insertBefore(c,g.firstChild);}}catch(e){}}

  /* ⑩ どのページでも：同じ形で3つ以上ならんだカード・行（一覧の中身）を自動で見つけて、浮かび上がらせる。
     ページごとに名前を書かなくてよい（新しいページを足しても、そのまま効く）。
     さわらない物：上に張りつく帯・下のバー・メニュー・地図・表・横に流れる帯・小さな札・中に張りつく部品を持つ物。 */
  var SKIP="#wsec,#upan,#umask,#tsheet,#v2bar,#utheme,#totop,#tkbar,nav,table,svg,form,.tn-top,.lens,.qk,.lists,.kmap,.leaflet-container,.tk-v,[hidden]";
  var TAGS={DIV:1,A:1,LI:1,ARTICLE:1,SECTION:1,DETAILS:1,DL:1};
  var abudget=6000;
  function okPos(el){try{var cs=getComputedStyle(el);if(cs.position!=="static"&&cs.position!=="relative")return false;if(cs.display==="none"||cs.display==="inline"||cs.display==="contents")return false;
    if(cs.transform!=="none"||cs.animationName!=="none")return false;return true;}catch(e){return false;}}
  function cleanInside(el){var q=el.getElementsByTagName("*");if(q.length>70)return false;for(var i=0;i<q.length;i++){if(--abudget<0)return false;var p=getComputedStyle(q[i]).position;if(p==="fixed"||p==="sticky")return false;}return true;}
  function xscroll(el){for(var p=el.parentNode,n=0;p&&p!==d.body&&n<6;p=p.parentNode,n++){try{var o=getComputedStyle(p).overflowX;if((o==="auto"||o==="scroll")&&p.scrollWidth>p.clientWidth+4)return true;}catch(e){}}return false;}
  function auto(){try{var root=d.querySelector(".wrap")||d.querySelector("main")||d.body;if(!root||abudget<0)return;var W=Math.min(root.clientWidth||innerWidth,innerWidth);
    var all=root.getElementsByTagName("*"),groups=new Map(),n=Math.min(all.length,5000);
    for(var i=0;i<n;i++){var el=all[i];if(el.__tka||!TAGS[el.tagName])continue;var par=el.parentNode;if(!par)continue;
      var key=el.tagName+"."+(el.classList[0]||""),m=groups.get(par);if(!m){m={};groups.set(par,m);}(m[key]||(m[key]=[])).push(el);}
    groups.forEach(function(m,par){for(var k in m){var g=m[k];if(g.length<3)continue;if(par.closest&&par.closest(SKIP))continue;if(xscroll(g[0]))continue;
      for(var j=0;j<g.length;j++){var el=g[j];el.__tka=1;if(el.closest(".tk-v")||el.matches(SKIP))continue;
        var w=el.offsetWidth,ht=el.offsetHeight;if(ht<44||ht>900||w<W*.4)continue;if(!okPos(el)||!cleanInside(el))continue;
        el.classList.add("tk-v");}}});
  }catch(e){}}
  /* tk2：下から出る「◯◯のきょう」。数字が数え上がり、地図は押した府県だけがはっきり残る */
  function sheet(){try{if(!h.classList.contains("tk2"))return;var sh=d.getElementById("tsheet"),mp=d.querySelector(".kmap");if(!sh||!mp)return;
    var q=sh.querySelectorAll(".big b");for(var i=0;i<q.length;i++){if(q[i].__tks)continue;q[i].__tks=1;run(q[i],0,700);}
    var sync=function(){try{var on=sh.classList.contains("on"),t=sh.querySelector("h3"),name=on&&t?t.textContent.replace(/の.*$/,""):"";
      var ps=mp.querySelectorAll(".pf path"),hit=false,i;for(i=0;i<ps.length;i++){var y=!!name&&ps[i].getAttribute("data-p")===name;if(y)hit=true;if(ps[i].classList.contains("tk-sel")!==y)ps[i].classList.toggle("tk-sel",y);}
      var gs=mp.querySelectorAll(".lb>g");for(i=0;i<gs.length;i++){var jp=gs[i].querySelector("text.jp"),z=!!name&&!!jp&&jp.textContent===name;if(gs[i].classList.contains("tk-sel")!==z)gs[i].classList.toggle("tk-sel",z);}
      if(mp.classList.contains("tk-has")!==hit)mp.classList.toggle("tk-has",hit);}catch(e){}};
    sync();if(sh.__tkb)return;sh.__tkb=1;if(MO)new MutationObserver(sync).observe(sh,{attributes:true,attributeFilter:["class"],childList:true});
  }catch(e){}}

  /* 題の文字に光を通すのは、文字が濃い色のページだけ（白い字の題には使わない） */
  function h1s(){try{if(!h.classList.contains("tk2"))return;var e=d.querySelector(".head h1");if(!e||e.__tkh)return;e.__tkh=1;var c=getComputedStyle(e).color.match(/\d+/g);
    if(c&&+c[0]<70&&+c[1]<70&&+c[2]<70&&!e.querySelector("*"))e.classList.add("tk-h1");}catch(e){}}

  /* ページの部品は後から作られる物がある（一覧・帯・下のバー）ので、何度呼んでも同じ結果になる形で見回す */
  var pend=0;function scan(){pend=0;bar();arm();carm();liveAll();clock();pill();pings();auto();h1s();arm();sheet();}
  function later(){if(!pend)pend=setTimeout(scan,60);}
  function start(){scan();try{if(MO&&d.body)new MutationObserver(later).observe(d.body,{childList:true,subtree:true});}catch(e){}}
  if(d.readyState==="loading")d.addEventListener("DOMContentLoaded",start);else start();

  /* 昼と夜：押した所から丸く広がる */
  try{if(d.startViewTransition){var busy=false;d.addEventListener("click",function(ev){var b=ev.target&&ev.target.closest&&ev.target.closest("#utheme");if(!b||busy)return;
    ev.preventDefault();ev.stopImmediatePropagation();busy=true;
    var r=b.getBoundingClientRect();h.style.setProperty("--tkx",(r.left+r.width/2)+"px");h.style.setProperty("--tky",(r.top+r.height/2)+"px");h.classList.add("tk-th");
    var done=function(){h.classList.remove("tk-th");busy=false;};
    /* 下の b.click() は busy の間なので、この関数を素通りして元の切り替えに届く */
    try{d.startViewTransition(function(){b.click();}).finished.then(done,done);}catch(e){b.click();done();}
  },true);}}catch(e){}
})();
