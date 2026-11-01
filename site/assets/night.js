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
  var css="html.night{background:#fff;filter:invert(.95) hue-rotate(180deg)}"+
    "html.night img,html.night video,html.night picture,html.night svg image,html.night .nofilt,html.night .tnbtn .mm{filter:invert(1) hue-rotate(180deg)}"+
    "html.night .head img{background:#fff;border-radius:50%}"+
    /* 11/2 オーナー「夜もっと何とかならん」「夜のお洒落感」→ 真っ黒をやめて深い夜空の紺に。白い面も同じ紺になるよう、薄い青を全体に重ねる */
    "html.night body:after{content:'';position:fixed;inset:-50vh 0;background:#E9F0FF;mix-blend-mode:multiply;pointer-events:none;z-index:2147483646}"+
    /* 題名まわりの丸い飾りは、夜は星と月あかりに */
    "html.night .head{background:radial-gradient(1.2px 1.2px at 12% 18%,#000 98%,transparent),radial-gradient(1px 1px at 27% 42%,#000 98%,transparent),radial-gradient(1.4px 1.4px at 44% 9%,#000 98%,transparent),radial-gradient(1px 1px at 63% 31%,#000 98%,transparent),radial-gradient(1.2px 1.2px at 78% 14%,#000 98%,transparent),radial-gradient(1px 1px at 88% 46%,#000 98%,transparent),radial-gradient(1px 1px at 8% 58%,#000 98%,transparent),radial-gradient(1.3px 1.3px at 92% 72%,#000 98%,transparent),radial-gradient(1px 1px at 35% 70%,#000 98%,transparent)!important}"+
    /* いまから行ける の地図：夜は暗い地図に */
    "html.night .rd svg{filter:brightness(.42) saturate(1.1) invert(1) hue-rotate(180deg)}"+
    "html.night .blob{display:none}"+
    /* MENU の四角は、夜はベージュにならないよう月あかりの銀に */
    "html.night #v2bar button.mn{background:#121826}"+
    "html.night .rd{border-color:#000}"+
    /* 11/2 オーナー「夜空感がいい、夜景を見に行ってるかのような」→ 星がまたたき、入口の地図に街の灯り */
    ".nsky,.kmap .lt{display:none}html.night .nsky,html.night .kmap .lt{display:block}"+
    "html.night .head{position:relative;isolation:isolate}"+
    ".nsky{position:absolute;inset:0;z-index:-1;pointer-events:none;overflow:hidden}"+
    ".nsky i{position:absolute;left:0;top:0;width:1px;height:1px;border-radius:50%}"+
    ".nsky .s2{animation:tw 3.2s ease-in-out infinite}.nsky .s3{animation:tw 4.6s ease-in-out 1.4s infinite}"+
    ".kmap .lt{pointer-events:none;filter:drop-shadow(0 0 2px rgba(255,214,140,.9))}"+
    ".kmap .lt circle{fill:#FFE2A6}.kmap .lt .t{animation:tw 3.8s ease-in-out infinite}.kmap .lt .u{animation:tw 5.2s ease-in-out 1.7s infinite}"+
    "@keyframes tw{0%,100%{opacity:1}50%{opacity:.25}}"+
    "@media (prefers-reduced-motion:reduce){.nsky i,.kmap .lt circle{animation:none!important}}";
  var st=document.createElement("style");st.textContent=css;(document.head||d).appendChild(st);
  set(pick());
  /* 星と街の灯り：毎回同じ並びになるよう、決まった数から作る */
  function rnd(n){var x=n;return function(){x=(x*16807)%2147483647;return x/2147483647;};}
  function deco(){
    var r=rnd(7),hs=document.querySelectorAll(".head");
    for(var k=0;k<hs.length;k++){var h=hs[k];if(h.querySelector(".nsky"))continue;
      var w=Math.max(h.offsetWidth,320),ht=Math.max(h.offsetHeight,240),L=["","",""];
      for(var j=0;j<54;j++){var x=Math.round(r()*w),y=Math.round(r()*ht*.92),z=r(),sz=z<.12?2:z<.45?1.4:1,c=r()<.18?"#2A2410":"#000";
        L[j%3]+=(L[j%3]?",":"")+x+"px "+y+"px 0 "+(sz-1)/2+"px "+c;}
      var d2=document.createElement("div");d2.className="nsky";d2.setAttribute("aria-hidden","true");
      d2.innerHTML='<i style="box-shadow:'+L[0]+'"></i><i class="s2" style="box-shadow:'+L[1]+'"></i><i class="s3" style="box-shadow:'+L[2]+'"></i>';
      h.insertBefore(d2,h.firstChild);}
    var m=document.querySelector(".kmap");if(!m||m.querySelector(".lt"))return;
    var N={"大阪":90,"兵庫":70,"京都":55,"奈良":30,"滋賀":30,"和歌山":24},g=document.createElementNS("http://www.w3.org/2000/svg","g"),out="",r2=rnd(11);
    g.setAttribute("class","lt");
    [].forEach.call(m.querySelectorAll(".pf path"),function(pth){var n=N[pth.getAttribute("data-p")]||20,bb=pth.getBBox(),pt=m.createSVGPoint(),got=0,tries=0;
      while(got<n&&tries<n*40){tries++;pt.x=bb.x+r2()*bb.width;pt.y=bb.y+r2()*bb.height;
        if(!pth.isPointInFill||!pth.isPointInFill(pt))continue;got++;var q=r2();
        out+='<circle cx="'+pt.x.toFixed(1)+'" cy="'+pt.y.toFixed(1)+'" r="'+(q<.1?2.2:q<.4?1.5:1).toFixed(1)+'"'+(q>.8?' class="t"':q>.62?' class="u"':'')+' opacity="'+(.55+r2()*.45).toFixed(2)+'"/>';}});
    g.innerHTML=out;var lb=m.querySelector(".lb");m.insertBefore(g,lb);}
  function go(){if(d.classList.contains("night"))deco();}
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",go);else go();
  document.addEventListener("usagi-theme",function(){if(document.readyState!=="loading")go();});
  window.usagiTheme={get:function(){return d.classList.contains("night")?"night":"day"},set:function(v){set(v,true)}};
})();
