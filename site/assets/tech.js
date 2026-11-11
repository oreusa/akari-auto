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
  var RSEL="#wsec>.it,#wsec>.pr5,#wsec>.wh,.past>*,.tip,.fx>*,.wrap>.sns,.wrap>.ft,.lists>h2,.prom li,.wrap>p";
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

  /* ページの部品は後から作られる物がある（一覧・帯・下のバー）ので、何度呼んでも同じ結果になる形で見回す */
  var pend=0;function scan(){pend=0;bar();arm();carm();liveAll();clock();}
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
