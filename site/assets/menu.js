/* 10/31 オーナー「三本線を作って項目を選べるように…燈の方も」（月の links/assets/menu.js と同じ形）
   全ページ共通のメニュー。右上の三本線 → 右から出る紙。昼と夜の切り替えもここ（night.js）。
   ページを足すときは L に1行足すだけ。/#shop・/#deal・/#trip はリストの欄ボタンを押す。押された数は /c の s=menu。 */
(function(){
  /* 11/2 オーナー「燈のhpを LIFE NOTE…関東おでかけリスト・おかいものリスト 完全に分ける」→ / は入口、/odekake と /okaimono に分けた */
  var P=location.pathname.replace(/^\/townnotes\//,"/odekake").replace(/\.html$/,""),here=
    /^\/(index)?$/.test(P)?"tn":/^\/odekake/.test(P)?"list":/^\/okaimono/.test(P)?"okai":/^\/illumination/.test(P)?"illumi":/^\/koyo/.test(P)?"koyo":/^\/koe/.test(P)?"koe":/^\/tomari/.test(P)?"tomari":/^\/ima/.test(P)?"ima":/^\/kaimawari/.test(P)?"kaimawari":/^\/furusato/.test(P)?"furusato":/^\/tanka/.test(P)?"tanka":/^\/nesage/.test(P)?"nesage":"";
  var SH=/^(\/okaimono|\/nesage|\/tanka|\/furusato|\/kaimawari)/.test(P);
  /* 11/2 オーナー「もっとまとめろよ。TOWNNOTEこんなんじゃないだろ」→ 月と同じく、リストごとに自分の項目だけ＋関連サイト */
  var L=[
    ["LIST","list","/odekake","関東おでかけリスト","開催中・これからのおでかけ"],
    ["MAP","map","/odekake#map","地図で見る","関東の地図から、近くのおでかけを"],
    ["NOW","ima","/ima","いまから行けるおでかけ","いる場所から近い順に、きょう開いている所"],
    ["ILLUMINATION","illumi","/illumination","イルミネーション日程","2026-2027　都県ごとの日程と無料の所"],
    ["AUTUMN LEAVES","koyo","/koyo","紅葉ライトアップ日程","2026　夜の時間・料金・近くの宿"],
    ["STAY","tomari","/tomari","泊まりで行くおでかけ","遠くのおでかけと、近くの宿"],
    ["-","CONTACT"],
    ["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],
    ["LISTING","listing","https://ig.me/m/ai_usagichan1","おでかけ掲載","新しいお店やイベントのご紹介"],
    ["-","関連サイト"],
    ["OKAIMONO LIST","okai","/okaimono","くらべたおかいものリスト","うさぎが数字で比べた物と、本当に安い物"],
    ["LIFE NOTE","tn","/","LIFE NOTE","関東のくらしのノート"]
  ];
  if(SH)L=[
    ["LIST","okai","/okaimono","くらべたおかいものリスト","3つ以上を数字で比べて選んだ物"],
    ["PER UNIT","tanka","/tanka","1個あたりで比べた","水・お米などを1Lあたり・1kgあたりで"],
    ["FURUSATO","furusato","/furusato","ふるさと納税を比べた","寄付1万円あたりの量で・12/31まで"],
    ["PRICE DOWN","nesage","/nesage","本当に値下がりした物","毎日の値段を記録して、下がった物だけ"],
    ["SALE","kaimawari","/kaimawari","買いまわりの1,000円ぽっきり","送料込み・レビュー1,000件以上"],
    ["-","CONTACT"],
    ["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],
    ["-","関連サイト"],
    ["KANTO ODEKAKE","list","/odekake","関東おでかけリスト","関東のイベント・新しいお店や施設"],
    ["LIFE NOTE","tn","/","LIFE NOTE","関東のくらしのノート"]
  ];
  /* 入口は、2つのリストとご連絡だけ */
  if(here==="tn")L=[["-","LIFE NOTE"],
    ["KANTO ODEKAKE","list","/odekake","関東おでかけリスト","関東のイベント・新しいお店や施設"],
    ["OKAIMONO LIST","okai","/okaimono","くらべたおかいものリスト","うさぎが数字で比べた物と、本当に安い物"],
    ["-","CONTACT"],
    ["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],
    ["LISTING","listing","https://ig.me/m/ai_usagichan1","おでかけ掲載","新しいお店やイベントのご紹介"]];
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
  "#upan .uh .uhl{flex:1;display:flex;align-items:center;gap:10px;text-decoration:none;-webkit-tap-highlight-color:transparent}"+
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
  var GJ={"KANTO ODEKAKE":"おでかけ","OKAIMONO LIST":"くらべた買い物","LIFE NOTE":"2つのリスト","CONTACT":"ご相談・お問い合わせ"};
  function ug(k){return '<div class="ug">'+(GJ[k]||k)+(GJ[k]?'<small>'+k+'</small>':"")+'</div>';}
  function build(){
    var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
    var btn=document.createElement("button");btn.id="umenu";btn.type="button";btn.setAttribute("aria-label","メニューを開く");btn.setAttribute("aria-expanded","false");btn.setAttribute("aria-controls","upan");btn.innerHTML="<i></i><i></i><i></i>";
    var mask=document.createElement("div");mask.id="umask";
    var pan=document.createElement("div");pan.id="upan";pan.setAttribute("role","dialog");pan.setAttribute("aria-modal","true");pan.setAttribute("aria-label","メニュー");pan.setAttribute("aria-hidden","true");
    var h='<div class="uh"><a class="uhl" href="/" aria-label="LIFE NOTE の入口へ"><img src="'+(document.documentElement.classList.contains("night")?"/logo-s-night.png":"/logo-s.png")+'" alt=""><b>LIFE NOTE</b></a><button class="ux" type="button" aria-label="メニューを閉じる">×</button></div><nav>'+(here==="tn"?"":ug(SH?"OKAIMONO LIST":"KANTO ODEKAKE"));
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
      if(/^(shop|deal|trip)$/.test(k)&&here==="okai"){e.preventDefault();close();setTimeout(function(){openView(k);},280);}
    });});
    var hv=location.hash.slice(1);
    if((here==="list"&&hv==="map")||(here==="okai"&&/^(shop|deal|trip|hot)$/.test(hv))){try{history.replaceState(null,"",location.pathname+location.search);}catch(e){}if(hv==="map")openMap();else setTimeout(function(){openView(hv==="hot"?"pick":hv);},300);}
  }
  if(document.body)build();else document.addEventListener("DOMContentLoaded",build);
})();

/* 11/2 オーナー「地図、AppleマップとGoogle、Google使ってない人も多いから選べるように」
   ページの中の Googleマップ のリンクを押したとき、最初の1回だけ「Googleマップ／Appleマップ」を選んでもらい、次からはその地図で開く。
   選んだ物はこの端末に覚える（usagi_mapapp）。メニューの下の「地図アプリ」でいつでも変えられる。 */
(function(){
  var KEY="usagi_mapapp";
  function get(){try{return localStorage.getItem(KEY)||"";}catch(e){return "";}}
  function set(v){try{localStorage.setItem(KEY,v);}catch(e){}document.dispatchEvent(new Event("usagi-mapapp"));}
  function apple(u){
    try{var x=new URL(u),q=x.searchParams;
      if(/\/maps\/dir/.test(x.pathname)){var f={transit:"r",walking:"w",driving:"d"}[q.get("travelmode")||""]||"";
        var o="https://maps.apple.com/?daddr="+encodeURIComponent(q.get("destination")||"");if(q.get("origin"))o+="&saddr="+encodeURIComponent(q.get("origin"));return o+(f?"&dirflg="+f:"");}
      var s=q.get("query")||q.get("q");if(!s){var m=x.pathname.match(/\/maps\/(?:search|place)\/([^\/]+)/);if(m)s=decodeURIComponent(m[1].replace(/\+/g," "));}
      return s?"https://maps.apple.com/?q="+encodeURIComponent(s):u;
    }catch(e){return u;}}
  function go(a,app){var u=a.href;if(app==="apple")u=apple(u);
    if(a.target==="_blank")window.open(u,"_blank","noopener");else location.href=u;}
  var css="#umap-m{position:fixed;inset:0;background:rgba(20,22,28,.38);z-index:2147483000;opacity:0;transition:opacity .2s}#umap-m.on{opacity:1}"+
    "#umap-s{position:fixed;left:0;right:0;bottom:0;z-index:2147483001;background:#fff;border-radius:18px 18px 0 0;padding:18px 18px calc(18px + env(safe-area-inset-bottom));box-shadow:0 -6px 24px rgba(0,0,0,.12);transform:translateY(100%);transition:transform .25s ease;max-width:560px;margin:0 auto;font-family:\"Zen Kaku Gothic New\",sans-serif;color:#333}"+
    "#umap-s.on{transform:none}#umap-s h3{margin:0 0 4px;font-size:16px;font-weight:600;text-align:center}#umap-s p{margin:0 0 14px;font-size:12px;color:#777;text-align:center}"+
    "#umap-s .b{display:flex;gap:10px}#umap-s button{flex:1;padding:14px 8px;border:1px solid #E2E4E8;border-radius:12px;background:#fff;font-family:inherit;font-weight:700;font-size:15px;color:#333;cursor:pointer}"+
    "#umap-s button:active{background:#F1F2F4}#umap-s .x{display:block;margin:12px auto 0;flex:none;border:0;padding:6px 14px;font-size:13px;color:#777;background:none}"+
    "html.night #umap-s{box-shadow:none}";
  function sheet(a){
    if(!document.getElementById("umap-css")){var st=document.createElement("style");st.id="umap-css";st.textContent=css;document.head.appendChild(st);}
    var m=document.createElement("div");m.id="umap-m";var s=document.createElement("div");s.id="umap-s";s.setAttribute("role","dialog");s.setAttribute("aria-modal","true");s.setAttribute("aria-label","地図アプリを選ぶ");
    s.innerHTML='<h3>どの地図で開きますか？</h3><p>次からは選んだ地図で開きます（メニューの下で変えられます）</p><div class="b"><button type="button" data-a="google">Googleマップ</button><button type="button" data-a="apple">Appleマップ</button></div><button type="button" class="x">やめる</button>';
    document.body.appendChild(m);document.body.appendChild(s);
    requestAnimationFrame(function(){m.classList.add("on");s.classList.add("on");});
    function close(){m.classList.remove("on");s.classList.remove("on");setTimeout(function(){m.remove();s.remove();},260);}
    m.addEventListener("click",close);s.querySelector(".x").addEventListener("click",close);
    s.querySelectorAll("[data-a]").forEach(function(b){b.addEventListener("click",function(){var v=b.getAttribute("data-a");set(v);close();go(a,v);});});
    var f=s.querySelector("[data-a]");if(f)f.focus();
  }
  document.addEventListener("click",function(e){
    if(e.defaultPrevented||e.button>0||e.metaKey||e.ctrlKey||e.shiftKey)return;
    var a=e.target.closest&&e.target.closest('a[href*="google.com/maps"],a[href*="maps.google."]');if(!a)return;
    var v=get();e.preventDefault();
    if(v==="google"||v==="apple")go(a,v);else sheet(a);
  });
  /* メニューの下の切り替え（メニューができてから足す） */
  function row(){var nv=document.querySelector("#upan nav");if(!nv||document.getElementById("umaprow"))return;
    var st=document.createElement("style");st.textContent="#umaprow{display:flex;align-items:center;justify-content:center;gap:8px;margin:18px 0 22px;font-family:\"Zen Kaku Gothic New\",sans-serif;font-size:12px;color:#777}#umaprow button{border:1px solid #E2E4E8;background:#fff;border-radius:999px;padding:5px 12px;font:inherit;font-size:12px;color:#555;cursor:pointer}#umaprow button.on{border-color:#555;color:#222;font-weight:600}";document.head.appendChild(st);
    var d=document.createElement("div");d.id="umaprow";d.innerHTML='<span>地図アプリ</span><button type="button" data-a="google">Google</button><button type="button" data-a="apple">Apple</button>';
    nv.appendChild(d);
    function sync(){var v=get();d.querySelectorAll("button").forEach(function(b){var on=b.getAttribute("data-a")===v;b.classList.toggle("on",on);b.setAttribute("aria-pressed",on?"true":"false");});}
    d.querySelectorAll("button").forEach(function(b){b.addEventListener("click",function(){set(b.getAttribute("data-a"));});});
    document.addEventListener("usagi-mapapp",sync);sync();}
  var n=0;(function t(){row();if(!document.getElementById("umaprow")&&++n<50)setTimeout(t,100);})();
})();
