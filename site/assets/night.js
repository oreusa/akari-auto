/* 10/31 オーナー「夜と昼の切り替えにしたら？」「夜の方くらすぎない？」
   初めは昼。太陽と月のマーク（menu.js。三本線の隣とメニューの中）で夜に切り替えられ、選んだ方を覚える。
   色は全部のページで手で決めているので、ページ全体を反転して暗くし、写真・ロゴ・地図の色は元に戻す。
   ページの先頭で読むこと（あとで読むと一瞬白く光る）。 */
(function(){
  var K="usagi_theme",d=document.documentElement;
  /* 10/31 オーナー「初めは昼にしといて」→ 時間では変えない。太陽と月のマークで選んだ時だけ夜 */
  function pick(){try{var v=localStorage.getItem(K);if(v==="day"||v==="night")return v;}catch(e){}return "day";}
  function set(v,save){d.classList.toggle("night",v==="night");if(save)try{localStorage.setItem(K,v);}catch(e){}
    document.dispatchEvent(new CustomEvent("usagi-theme",{detail:v}));}
  var css="html.night{background:transparent;filter:invert(.95) hue-rotate(180deg)}"+
    /* 11/2 オーナー「画面周りに白くモヤ。見にくいから消して」→ iPhone の Safari は body の背景色で画面の上下をぼかす。
       夜も body が白のままだったので白いモヤが出ていた。body の色は夜の紺にして、見た目の白い面は後ろの1枚（反転して紺になる）で出す */
    "html.night body{background:#141A28!important}"+
    "html.night body:before{content:'';position:fixed;inset:-50vh 0;background:#fff;z-index:-1;pointer-events:none}"+
    /* 黒い影は反転すると白いモヤになるので、夜は影をなくす（下のボタン列・右上の丸） */
    "html.night #v2bar,html.night #utheme,html.night #umenu{box-shadow:none!important}"+
    "html.night img,html.night video,html.night picture,html.night svg image,html.night .nofilt,html.night .tnbtn .mm{filter:invert(1) hue-rotate(180deg)}"+
    /* 11/2 オーナー「中のデザインだけ光らせたら？」→ 夜は丸い台をなくし、ロゴの線だけを光らせる */
    "html.night .head img{background:none;border-radius:50%}"+
    /* 11/2 オーナー「夜もっと何とかならん」「夜のお洒落感」→ 真っ黒をやめて深い夜空の紺に。白い面も同じ紺になるよう、薄い青を全体に重ねる */
    "html.night body:after{content:'';position:fixed;inset:-50vh 0;background:#E9F0FF;mix-blend-mode:multiply;pointer-events:none;z-index:2147483646}"+
    /* 題名まわりの丸い飾りは、夜は星と月あかりに */
    "html.night .head{background:radial-gradient(1.2px 1.2px at 12% 18%,#000 98%,transparent),radial-gradient(1px 1px at 27% 42%,#000 98%,transparent),radial-gradient(1.4px 1.4px at 44% 9%,#000 98%,transparent),radial-gradient(1px 1px at 63% 31%,#000 98%,transparent),radial-gradient(1.2px 1.2px at 78% 14%,#000 98%,transparent),radial-gradient(1px 1px at 88% 46%,#000 98%,transparent),radial-gradient(1px 1px at 8% 58%,#000 98%,transparent),radial-gradient(1.3px 1.3px at 92% 72%,#000 98%,transparent),radial-gradient(1px 1px at 35% 70%,#000 98%,transparent)!important}"+
    /* いまから行ける の地図：夜は暗い地図に */
    "html.night .rd svg{filter:invert(1) hue-rotate(180deg)}"+
    /* 11/2 オーナー「他のページまだ白モヤ」→ いまから行ける の地図も入口と同じ夜の地図に（白っぽい灰色をやめる） */
    "html.night .rd svg>rect{fill:#141A28}"+
    /* 地図で見る（全画面の地図）：夜は暗すぎたので、少し明るく・色をはっきり */
    
    "html.night #mpL path{fill:#182139!important;fill-opacity:1;stroke:rgba(200,215,255,.16)}"+
    "html.night #mpL path[fill=none]{fill:none!important;stroke:rgba(235,215,166,.55)}"+
    "html.night .rd .mn{fill:#8F9AB3}"+
    "html.night .rd .rng{stroke:#C9D2E6;opacity:.5}"+
    "html.night .rd .rgl{fill:#E6EAF2;stroke:#141A28}"+
    "html.night .rd .pt{stroke:#141A28}"+
    "html.night #mpMe circle:first-child{fill:#fff;opacity:.15}html.night #mpMe circle+circle{fill:#F3F1EC;stroke:#141A28}html.night #mpMe rect{fill:#F3F1EC}html.night #mpMe text{fill:#141A28}"+
    /* 飾りの丸（入口の PAGE 01/02 の後ろ、燈のイルミの題名の後ろ）は夜は出さない */
    "html.night a.ls:before{display:none}"+
    "html.night header.head:before,html.night header.head:after{display:none}"+
    "html.night .blob{display:none}"+
    /* MENU の四角は、夜はベージュにならないよう月あかりの銀に */
    "html.night .rd{border-color:#000}"+
    /* 11/2 オーナー「夜空感がいい、夜景を見に行ってるかのような」→ 星がまたたき、入口の地図に街の灯り */
    ".nsky,.kmap .lt{display:none}html.night .nsky,html.night .kmap .lt{display:block}"+
    "html.night .head{position:relative;isolation:isolate}"+
    ".nsky{position:absolute;inset:0;z-index:-1;pointer-events:none;overflow:hidden}"+
    ".nsky i{position:absolute;left:0;top:0;width:1px;height:1px;border-radius:50%}"+
    ".nsky .s2{animation:tw 3.2s ease-in-out infinite}.nsky .s3{animation:tw 4.6s ease-in-out 1.4s infinite}.nsky .s4{animation:tw2 3.8s ease-in-out .6s infinite}"+
 /* 11/2 オーナー「月もうちょい明るく・星ももう少し綺麗に」→ 19:10「月すこーーーしだけ抑える／星は前の控えめな方がきれい／流れ星は色んな方向からたまーーーにの隠し要素」→ 月（ロゴの丸）をやわらかく光らせ、きらっと光る星と、ときどき流れ星。
    夜はページ全体を反転しているので、ここの色は「反転される前」の色（#000 が白、#3A2A00 があたたかい白に見える） */
  "html.night .head img[src*='logo-s-night']{filter:brightness(1.18) contrast(1.03) invert(1) hue-rotate(180deg) drop-shadow(0 0 9px rgba(58,42,0,.82)) drop-shadow(0 0 24px rgba(58,42,0,.42))}"+
  ".nsky .ss{position:absolute;left:0;top:0;width:80px;height:1.5px;border-radius:2px;background:linear-gradient(90deg,#000,transparent);transform-origin:0 50%;opacity:0}"+
    "@media (prefers-reduced-motion:reduce){.nsky .ss{display:none}}"+

    ".kmap .lt{pointer-events:none;filter:drop-shadow(0 0 2px rgba(255,214,140,.9))}"+
    ".kmap .lt circle{fill:#FFE2A6}.kmap .lt .t{animation:tw 3.8s ease-in-out infinite}.kmap .lt .u{animation:tw 5.2s ease-in-out 1.7s infinite}"+
    "@keyframes tw{0%,100%{opacity:1}50%{opacity:.25}}@keyframes tw2{0%,100%{opacity:1}45%,60%{opacity:0}}"+
    /* 11/2 19:18 オーナー「同じ色の文字が夜は綺麗に見えない」→ 夜は府県の色の文字をやめ、白っぽい文字に（選んだ府県は下線だけ府県の色） */
    "html.night .flt button[style*='--pc']:not(.on){color:#3A3632!important}"+
    "html.night .flt button.on{color:#14110E!important}html.night .mp{color:#3A3632!important}html.night .v2c span.p{color:#2B2622!important}"+
    /* 11/2 20:14 オーナー「夜、星と月以外オシャレに見えない」→ 夜のカード・ボタン・下の列も夜空に合わせる。
       色の塗りつぶし（府県の色の丸やタグ）をやめ、月あかりの金の細い線と銀の文字に。ここの色も「反転される前」の色 */
    "html.night .v2c span.on{background:transparent!important;box-shadow:inset 0 0 0 1px #372100;color:#372100!important}"+
    "html.night .v2c span.p{background:#D7E1FC!important;color:#04070F!important}"+
    "html.night .v2c span.f{background:transparent!important;box-shadow:inset 0 0 0 1px #30394B;color:#30394B!important}"+
    "html.night .paper .it .card .go{background:transparent!important;box-shadow:inset 0 0 0 1px #372100;color:#372100!important}"+
    "html.night #v2bar{background:#E1E9FE!important;box-shadow:inset 0 0 0 1px #C4D0EC!important}"+
    "html.night #v2bar button{color:#30394B}html.night #v2bar button.cur{color:#372100}html.night #v2bar button.cur span{border-bottom-color:#372100}"+
    "html.night #v2bar button.mn{background:transparent!important;color:#372100!important;box-shadow:inset 1px 0 0 #C4D0EC}html.night #v2bar button.mn i{background:#372100!important;box-shadow:0 -5px 0 #372100,0 5px 0 #372100!important}"+
    "html.night .st.on,html.night .st.now,html.night .tn8,html.night .card span.on{background:transparent!important;box-shadow:inset 0 0 0 1px #372100!important;border-color:transparent!important;color:#372100!important}"+
    "html.night .st.soon,html.night .st.pre,html.night .st.next{background:transparent!important;box-shadow:inset 0 0 0 1px #30394B!important;color:#30394B!important}"+
    "html.night .card .fr,html.night .it .fr{background:transparent!important;box-shadow:inset 0 0 0 1px #30394B!important;color:#30394B!important}"+
    "html.night .card div.go,html.night .it div.go,html.night .it span.ar,html.night .card.it:after{background:transparent!important;box-shadow:inset 0 0 0 1px #372100!important;color:#372100!important}"+
    /* 入口の地図で府県に data-p が無いもの（燈の関東）も、夜は紺の陸地＋府県の色の光る線に（色は昼の塗りの色を使う） */
    "html.night .kmap .pf path{fill:#182139!important;fill-opacity:1!important;filter:drop-shadow(0 0 2.5px var(--c,rgba(200,215,255,.6)))}html.night .kmap .pf path:not([data-p]){stroke:var(--c,#8FB6EA);stroke-width:1.6px}"+
    "@media (prefers-reduced-motion:reduce){.nsky i,.kmap .lt circle{animation:none!important}}";
  var st=document.createElement("style");st.textContent=css;(document.head||d).appendChild(st);
  set(pick());
  /* 入口の地図の府県の色を覚えておく（夜の光る線に使う） */
  function km(){[].forEach.call(document.querySelectorAll(".kmap .pf path"),function(x){var f=x.getAttribute("fill");if(f&&f.charAt(0)=="#")x.style.setProperty("--c",f)})}
  if(document.readyState!="loading")km();else document.addEventListener("DOMContentLoaded",km);
  /* 星と街の灯り：毎回同じ並びになるよう、決まった数から作る */
  function rnd(n){var x=n;return function(){x=(x*16807)%2147483647;return x/2147483647;};}
  /* 流れ星（隠し要素）：夜の見た目で、40〜120秒に1回だけ、毎回ちがう場所・向きから1本流れる */
  function shoot(d){var el=d.querySelector(".ss");if(!el||!el.animate)return;
    if(window.matchMedia&&matchMedia("(prefers-reduced-motion:reduce)").matches)return;
    function later(){setTimeout(go,40000+Math.random()*80000);}
    function go(){if(document.hidden||!document.documentElement.classList.contains("night")||!d.isConnected)return later();
      var W=d.offsetWidth||320,H=d.offsetHeight||240,x=W*(.1+Math.random()*.8),y=H*(.05+Math.random()*.4),
          dir=Math.random()<.5?-1:1,a=(15+Math.random()*35)*Math.PI/180,len=120+Math.random()*90,
          dx=Math.cos(a)*len*dir,dy=Math.sin(a)*len,rot=Math.atan2(dy,dx)*180/Math.PI+180,
          t0="translate("+x+"px,"+y+"px) rotate("+rot+"deg)",t1="translate("+(x+dx)+"px,"+(y+dy)+"px) rotate("+rot+"deg)";
      el.animate([{transform:t0,opacity:0},{transform:t0,opacity:1,offset:.08},{transform:t1,opacity:0}],{duration:800+Math.random()*500,easing:"ease-out"});
      later();}
    setTimeout(go,15000+Math.random()*45000);}
  function deco(){
    var r=rnd(7),hs=document.querySelectorAll(".head");
    for(var k=0;k<hs.length;k++){var h=hs[k];if(h.querySelector(".nsky"))continue;
      var w=Math.max(h.offsetWidth,320),ht=Math.max(h.offsetHeight,240),L=["","","",""];
      for(var j=0;j<66;j++){var x=Math.round(r()*w),y=Math.round(r()*ht*.92),z=r(),sz=z<.12?2:z<.45?1.4:1,c=r()<.18?"#2A2410":"#000";
        var g=j<54?j%3:3;L[g]+=(L[g]?",":"")+x+"px "+y+"px 0 "+(sz-1)/2+"px "+c;}
      var d2=document.createElement("div");d2.className="nsky";d2.setAttribute("aria-hidden","true");
      d2.innerHTML='<i style="box-shadow:'+L[0]+'"></i><i class="s2" style="box-shadow:'+L[1]+'"></i><i class="s3" style="box-shadow:'+L[2]+'"></i><i class="s4" style="box-shadow:'+L[3]+'"></i>';
      d2.innerHTML+='<em class="ss"></em>';shoot(d2);
      h.insertBefore(d2,h.firstChild);}
    var m=document.querySelector(".kmap");if(!m||m.querySelector(".lt"))return;
    var N={"東京":90,"神奈川":70,"埼玉":55,"千葉":50,"茨城":30,"栃木":26,"群馬":26},g=document.createElementNS("http://www.w3.org/2000/svg","g"),out="",r2=rnd(11);
    g.setAttribute("class","lt");
    [].forEach.call(m.querySelectorAll(".pf path"),function(pth){var n=N[pth.getAttribute("data-p")]||20,bb=pth.getBBox(),pt=m.createSVGPoint(),got=0,tries=0;
      while(got<n&&tries<n*40){tries++;pt.x=bb.x+r2()*bb.width;pt.y=bb.y+r2()*bb.height;
        if(!pth.isPointInFill||!pth.isPointInFill(pt))continue;got++;var q=r2();
        out+='<circle cx="'+pt.x.toFixed(1)+'" cy="'+pt.y.toFixed(1)+'" r="'+(q<.1?2.2:q<.4?1.5:1).toFixed(1)+'"'+(q>.8?' class="t"':q>.62?' class="u"':'')+' opacity="'+(.55+r2()*.45).toFixed(2)+'"/>';}});
    g.innerHTML=out;var lb=m.querySelector(".lb");m.insertBefore(g,lb);}
  /* 燈のロゴは白い台つきの絵なので、夜は台のない絵に替える */
  function logo(){var n=d.classList.contains("night"),im=document.querySelectorAll('.head img[src*="logo-s"],.uh img[src*="logo-s"]');
    for(var i=0;i<im.length;i++){var s0=im[i].getAttribute("src");im[i].setAttribute("src",n?s0.replace(/logo-s(-night)?\.png/,"logo-s-night.png"):s0.replace("logo-s-night.png","logo-s.png"));}}
  function go(){logo();if(d.classList.contains("night"))deco();}
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",go);else go();
  document.addEventListener("usagi-theme",function(){if(document.readyState!=="loading")go();});
  window.usagiTheme={get:function(){return d.classList.contains("night")?"night":"day"},set:function(v){set(v,true)}};
})();
