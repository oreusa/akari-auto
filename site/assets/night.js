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
  var css="html.night{background:#fff;filter:invert(.92) hue-rotate(180deg)}"+
    "html.night img,html.night video,html.night picture,html.night svg image,html.night .nofilt,html.night .tnbtn .mm{filter:invert(1) hue-rotate(180deg)}"+
    "html.night .head img{background:#fff;border-radius:50%}"+
    /* 11/2 オーナー「夜もっと何とかならん」「夜のお洒落感」→ 真っ黒をやめて深い夜空の紺に。白い面も同じ紺になるよう、薄い青を全体に重ねる */
    "html.night body:after{content:'';position:fixed;inset:-50vh 0;background:#E9F0FF;mix-blend-mode:multiply;pointer-events:none;z-index:2147483646}"+
    /* 題名まわりの丸い飾りは、夜は星と月あかりに */
    "html.night .head{background:radial-gradient(1.2px 1.2px at 12% 18%,#000 98%,transparent),radial-gradient(1px 1px at 27% 42%,#000 98%,transparent),radial-gradient(1.4px 1.4px at 44% 9%,#000 98%,transparent),radial-gradient(1px 1px at 63% 31%,#000 98%,transparent),radial-gradient(1.2px 1.2px at 78% 14%,#000 98%,transparent),radial-gradient(1px 1px at 88% 46%,#000 98%,transparent),radial-gradient(1px 1px at 8% 58%,#000 98%,transparent),radial-gradient(1.3px 1.3px at 92% 72%,#000 98%,transparent),radial-gradient(1px 1px at 35% 70%,#000 98%,transparent),radial-gradient(circle at 82% 8%,rgba(40,70,140,.10) 0 90px,transparent 160px)!important}"+
    /* いまから行ける の地図：夜は暗い地図に */
    "html.night .rd svg{filter:brightness(.42) saturate(1.1) invert(1) hue-rotate(180deg)}"+
    "html.night .blob{display:none}"+
    /* MENU の四角は、夜はベージュにならないよう月あかりの銀に */
    "html.night #v2bar button.mn{background:#121826}"+
    "html.night .rd{border-color:#000}";
  var st=document.createElement("style");st.textContent=css;(document.head||d).appendChild(st);
  set(pick());
  window.usagiTheme={get:function(){return d.classList.contains("night")?"night":"day"},set:function(v){set(v,true)}};
})();
