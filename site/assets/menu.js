/* 10/31 オーナー「三本線を作って項目を選べるように…燈の方も」（月の links/assets/menu.js と同じ形）
   全ページ共通のメニュー。右上の三本線 → 右から出る紙。昼と夜の切り替えもここ（night.js）。
   ページを足すときは L に1行足すだけ。/#shop・/#deal・/#trip はリストの欄ボタンを押す。押された数は /c の s=menu。 */
(function(){
  var P=location.pathname.replace(/^\/townnotes\//,"/"),here=
    /^\/(index\.html)?$/.test(P)?"list":/^\/illumination/.test(P)?"illumi":/^\/tomari/.test(P)?"tomari":/^\/kaimawari/.test(P)?"kaimawari":/^\/furusato/.test(P)?"furusato":/^\/tanka/.test(P)?"tanka":"";
  var L=[
    ["LIST","list","/","関東おでかけリスト","開催中・これからのおでかけ"],
    ["MAP","map","/#map","地図で見る","関東の地図から、近くのおでかけを"],
    ["ILLUMINATION","illumi","/illumination","イルミネーション日程","2026-2027　都県ごとの日程と無料の所"],
    ["STAY","tomari","/tomari","泊まりで行くおでかけ","遠くのおでかけと、近くの宿"],
    ["-","SHOPPING"],
    ["KAIMAWARI","kaimawari","/kaimawari","買いまわりの1,000円ぽっきり","お買い物マラソン用・送料込み・レビュー1,000件以上"],
    ["FURUSATO","furusato","/furusato","ふるさと納税を比べた","寄付1万円あたりの量で・12/31まで"],
    ["PER UNIT","tanka","/tanka","1個あたりで比べた","楽天の水・お米などを1Lあたり・1kgあたりで"],
    ["SHOP","shop","/#shop","うさぎが比べた買い物","くらべて選んだ、暮らしの物"],
    ["DEAL","deal","/#deal","今だけのお得","ポイントアップ・セールの日"],
    ["HOTEL","trip","/#trip","宿と予約","口コミ1,000件以上・評価4.5以上の宿"]
  ];
  var css=
  "#umenu{position:fixed;top:12px;right:12px;z-index:9990;width:42px;height:42px;border-radius:50%;border:1px solid #DADADA;background:rgba(255,255,255,.94);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:0;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.07);-webkit-tap-highlight-color:transparent}"+
"#utheme{position:fixed;top:12px;right:62px;z-index:9990;width:76px;height:42px;border-radius:99px;border:1px solid #DADADA;background:rgba(255,255,255,.94);padding:0;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.07);-webkit-tap-highlight-color:transparent;transition:opacity .25s,transform .25s}"+
  "#utheme .kn{position:absolute;top:4px;left:4px;width:32px;height:32px;border-radius:50%;background:#2B2622;transition:transform .35s cubic-bezier(.3,.7,.2,1)}"+
  "#utheme[aria-checked=true] .kn{transform:translateX(34px)}"+
  "#utheme svg{position:absolute;top:11px;width:18px;height:18px;fill:none;stroke:#8C7B6E;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;transition:stroke .3s,transform .5s}"+
  "#utheme .su svg{left:11px}#utheme .mo svg{right:11px}#utheme:focus:not(:focus-visible){outline:none}"+
  "#utheme[aria-checked=false] .su svg{stroke:#fff;transform:rotate(90deg)}"+
  "#utheme[aria-checked=true] .mo svg{stroke:#fff;transform:rotate(-15deg)}"+
  "#utheme .sp{stroke-width:1.2}"+
  "#utheme.hide{opacity:0;transform:translateY(-8px);pointer-events:none}"+
  "html[style*=\"overflow: hidden\"] #utheme{display:none}"+
  "#umenu i{display:block;width:16px;height:1.5px;background:#3A3330;border-radius:1px}"+
  "#umenu:active{transform:scale(.94)}"+
  "html[style*=\"overflow: hidden\"] #umenu{display:none}"+
  "#umask{position:fixed;inset:0;z-index:9991;background:rgba(30,26,24,.32);opacity:0;pointer-events:none;transition:opacity .25s}"+
  "#umask.on{opacity:1;pointer-events:auto}"+
  "#upan{position:fixed;top:0;right:0;bottom:0;z-index:9992;width:min(86vw,360px);background:#fff;transform:translateX(102%);transition:transform .28s cubic-bezier(.2,.7,.2,1);display:flex;flex-direction:column;box-shadow:-8px 0 30px rgba(0,0,0,.08);font-family:'Zen Kaku Gothic New',sans-serif;color:#2B2622}"+
  "#upan.on{transform:none}"+
  "#upan .uh{display:flex;align-items:center;gap:10px;padding:16px 14px 14px 20px;border-bottom:1px solid #EDEDED}"+
  "#upan .uh img{width:34px;height:34px}"+
  "#upan .uh b{flex:1;font-family:Jost,sans-serif;font-weight:400;font-size:10.5px;letter-spacing:.32em;color:#8C7B6E}"+
  "#upan .ux{width:42px;height:42px;border:0;background:none;font-size:24px;line-height:1;color:#3A3330;cursor:pointer;border-radius:50%}"+
  "#upan .ux:active{background:#F3F3F3}"+
  "#upan nav{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:6px 0 10px}"+
  /* 11/1 月と同じ：ジャンルの見出しを薄い帯にして、日本語で（オーナー「メニュージャンルの区切りあると分かりやすい」） */
  "#upan .ug{display:flex;align-items:baseline;gap:10px;margin-top:14px;padding:9px 20px;background:#F1F2F4;border-top:1px solid #E4E5E8;border-bottom:1px solid #E4E5E8;font-family:'Zen Kaku Gothic New',sans-serif;font-size:12.5px;font-weight:700;letter-spacing:.12em;color:#3A3330}"+
  "#upan nav>.ug:first-child{margin-top:0;border-top:0}"+
  "#upan .ug small{font-family:Jost,sans-serif;font-weight:400;font-size:9px;letter-spacing:.3em;color:#9C8775}"+
  "#upan a.ui{display:block;position:relative;text-decoration:none;color:#2B2622;padding:13px 44px 13px 20px;border-top:1px solid #F1F1F1}"+
  "#upan a.ui:first-of-type{border-top:0}"+
  "#upan a.ui:active{background:#F7F7F7}"+
  "#upan a.ui small{display:block;font-family:Jost,sans-serif;font-size:9px;letter-spacing:.3em;color:#9C8775}"+
  "#upan a.ui span{display:block;font-family:'Shippori Mincho',serif;font-weight:600;font-size:16.5px;letter-spacing:.08em;margin-top:3px}"+
  "#upan a.ui em{display:block;font-style:normal;font-size:11.5px;color:#857A70;margin-top:3px;letter-spacing:.02em}"+
  "#upan a.ui:after{content:'\\2192';position:absolute;right:20px;top:50%;transform:translateY(-50%);font-family:Jost,sans-serif;color:#9C8775}"+
  "#upan a.ui.cur{background:#F7F7F7}"+
  "#upan a.ui.cur:before{content:'';position:absolute;left:0;top:12px;bottom:12px;width:3px;background:#2B2622}"+
  "#upan a.ui.cur:after{content:'いまのページ';font-family:'Zen Kaku Gothic New',sans-serif;font-size:10px;color:#8C7B6E}"+
  "#upan .ut{display:flex;align-items:center;justify-content:space-between;margin:8px 20px 0;padding:14px 0;border-top:1px solid #EDEDED;font-size:13.5px}"+
  "#upan .ut em{display:block;font-style:normal;font-size:11px;color:#8C7B6E;margin-top:2px}"+
  "#upan .sw{position:relative;width:50px;height:30px;border-radius:99px;border:0;background:#D9D9D9;cursor:pointer;flex:none;transition:background .2s}"+
  "#upan .sw:after{content:'';position:absolute;top:3px;left:3px;width:24px;height:24px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.2);transition:transform .2s}"+
  "#upan .sw[aria-checked=true]{background:#2B2622}"+
  "#upan .sw[aria-checked=true]:after{transform:translateX(20px)}"+
  "#upan .us{display:flex;gap:22px;justify-content:center;padding:14px 20px calc(18px + env(safe-area-inset-bottom));border-top:1px solid #EDEDED}"+
  "#upan .us a{font-family:Jost,sans-serif;font-size:13px;letter-spacing:.06em;color:#2B2622;text-decoration:none;border-bottom:1px solid #2B2622;padding:6px 0 2px}"+
  "html.umenu-open,html.umenu-open body{overflow:hidden}"+
  "@media (prefers-reduced-motion:reduce){#upan,#umask{transition:none}}";
  function ck(k){try{navigator.sendBeacon("/c?f=menu&s=menu&k="+encodeURIComponent(k.slice(0,40)));}catch(e){}}
  var SUN='<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.3M12 19.1v2.3M2.6 12h2.3M19.1 12h2.3M5.35 5.35l1.6 1.6M17.05 17.05l1.6 1.6M5.35 18.65l1.6-1.6M17.05 6.95l1.6-1.6"/></svg>',MOON='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.6 14.6A8 8 0 0 1 9.4 4.4a8 8 0 1 0 10.2 10.2z"/><path class="sp" d="M17.2 3.4v2.8M15.8 4.8h2.8"/></svg>',MK="";
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  function openView(v){var b=document.querySelector('button[data-v="'+v+'"]');if(!b)return;b.click();setTimeout(function(){var y=b.getBoundingClientRect().top+scrollY-10;scrollTo({top:y,behavior:"smooth"});},60);}
  function openMap(){var n=0;(function t(){var b=document.querySelector(".tnbtn");if(b){b.click();return;}if(++n<40)setTimeout(t,100);})();}
  var GJ={"KANTO ODEKAKE":"おでかけ","SHOPPING":"買い物"};
  function ug(k){return '<div class="ug">'+(GJ[k]||k)+(GJ[k]?'<small>'+k+'</small>':"")+'</div>';}
  function build(){
    var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
    var btn=document.createElement("button");btn.id="umenu";btn.type="button";btn.setAttribute("aria-label","メニューを開く");btn.setAttribute("aria-expanded","false");btn.setAttribute("aria-controls","upan");btn.innerHTML="<i></i><i></i><i></i>";
    var mask=document.createElement("div");mask.id="umask";
    var pan=document.createElement("div");pan.id="upan";pan.setAttribute("role","dialog");pan.setAttribute("aria-modal","true");pan.setAttribute("aria-label","メニュー");pan.setAttribute("aria-hidden","true");
    var h='<div class="uh"><img src="/logo-s.png" alt=""><b>USAGI LIFE NOTES</b><button class="ux" type="button" aria-label="メニューを閉じる">×</button></div><nav>'+ug("KANTO ODEKAKE");
    L.forEach(function(x){
      if(x[0]==="-"){h+=ug(x[1]);return;}
      var cur=x[1]===here,ext=/^https?:/.test(x[2]);
      h+='<a class="ui'+(cur?" cur":"")+'" data-k="'+x[1]+'" href="'+x[2]+'"'+(ext?' target="_blank" rel="noopener"':"")+(cur?' aria-current="page"':"")+'><small>'+x[0]+'</small><span>'+esc(x[3])+'</span><em>'+esc(x[4])+'</em></a>';
    });
    /* 10/31 オーナー「夜の見た目？なにこれ」→ 切り替えは右上の太陽と月のマークだけ（月と同じ） */
    h+='</nav>'+
      '<div class="us"><a href="https://www.instagram.com/ai_usagichan1/" target="_blank" rel="noopener">Instagram</a><a href="https://www.threads.com/@ai_usagichan1" target="_blank" rel="noopener">Threads</a><a href="https://x.com/ai_usagichan" target="_blank" rel="noopener">X</a></div>';
    pan.innerHTML=h;
    document.body.appendChild(btn);document.body.appendChild(mask);document.body.appendChild(pan);
    var last=null;
    function open(){last=document.activeElement;var nv=pan.querySelector("nav");if(nv)nv.scrollTop=0;document.documentElement.classList.add("umenu-open");mask.classList.add("on");pan.classList.add("on");pan.setAttribute("aria-hidden","false");btn.setAttribute("aria-expanded","true");setTimeout(function(){pan.querySelector(".ux").focus();},50);ck("メニュー｜開く");}
    function close(){document.documentElement.classList.remove("umenu-open");mask.classList.remove("on");pan.classList.remove("on");pan.setAttribute("aria-hidden","true");btn.setAttribute("aria-expanded","false");if(last&&last.focus)last.focus();}
    btn.addEventListener("click",open);mask.addEventListener("click",close);pan.querySelector(".ux").addEventListener("click",close);
    document.addEventListener("keydown",function(e){if(e.key==="Escape"&&pan.classList.contains("on"))close();});
    /* 右へなでて閉じる */
    var sx=null;pan.addEventListener("touchstart",function(e){sx=e.touches[0].clientX;},{passive:true});
    pan.addEventListener("touchend",function(e){if(sx!==null&&e.changedTouches[0].clientX-sx>70)close();sx=null;},{passive:true});
    /* 10/31 オーナー「太陽と月のマークにしようよ、オシャレなやつ」。三本線の隣。下へ読み進めたら隠す（しぼりこみの帯と重ねない）。メニューの中のスイッチと同じ動き */
    var tb=document.createElement("button");tb.id="utheme";tb.type="button";tb.setAttribute("role","switch");tb.setAttribute("aria-label","夜の見た目");
    tb.innerHTML='<span class="kn"></span><span class="su">'+SUN+'</span><span class="mo">'+MOON+'</span>';
    document.body.appendChild(tb);
    function syncTb(){var n=window.usagiTheme&&window.usagiTheme.get()==="night";tb.setAttribute("aria-checked",n?"true":"false");}
    syncTb();document.addEventListener("usagi-theme",syncTb);
    tb.addEventListener("click",function(){if(!window.usagiTheme)return;var v=window.usagiTheme.get()==="night"?"day":"night";window.usagiTheme.set(v);ck(MK+(v==="night"?"夜":"昼")+"（マーク）");});
    var tk=0;addEventListener("scroll",function(){if(tk)return;tk=1;requestAnimationFrame(function(){tk=0;tb.classList.toggle("hide",scrollY>120);});},{passive:true});
    pan.querySelectorAll("a.ui").forEach(function(a){a.addEventListener("click",function(e){
      var k=a.getAttribute("data-k");ck("メニュー｜"+a.querySelector("span").textContent);
      if(k===here&&k!=="map"){e.preventDefault();close();window.scrollTo({top:0,behavior:"smooth"});return;}
      if(k==="map"&&here==="list"){e.preventDefault();close();setTimeout(openMap,280);}
      if(/^(shop|deal|trip)$/.test(k)&&here==="list"){e.preventDefault();close();setTimeout(function(){openView(k);},280);}
    });});
    var hv=location.hash.slice(1);
    if(here==="list"&&/^(map|shop|deal|trip)$/.test(hv)){try{history.replaceState(null,"",location.pathname+location.search);}catch(e){}if(hv==="map")openMap();else setTimeout(function(){openView(hv);},300);}
  }
  if(document.body)build();else document.addEventListener("DOMContentLoaded",build);
})();
