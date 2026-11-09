/* 11/9 色（見本4）を全ページに */
(function(){try{if(document.getElementById("iro-css"))return;var l=document.createElement("link");l.id="iro-css";l.rel="stylesheet";l.href="/assets/iro.css?v=8";(document.head||document.documentElement).appendChild(l);}catch(e){}})();
/* 11/3 オーナー「下にスライドしたら、すぐ閉じちゃう」（アプリの中で開いたページが、下に引くとページごと閉じる）。
   ページが一番上にぴったり居ると、下に引く動きをアプリが「閉じる」に使う。指を置いた時・一番上に戻った時は 1px だけ下げておく（見た目は変わらない） */
(function(){
  try{if(!matchMedia("(pointer:coarse)").matches)return;}catch(e){return;}
  document.documentElement.style.overscrollBehaviorY="none";
  function nudge(){var d=document.documentElement;if(window.scrollY<1&&d.scrollHeight>innerHeight+2)window.scrollTo(0,1);}
  addEventListener("touchstart",nudge,{passive:true});
  addEventListener("scroll",function(){if(window.scrollY<1)requestAnimationFrame(nudge);},{passive:true});
  addEventListener("load",function(){setTimeout(nudge,50);});
})();
/* 10/31 オーナー「三本線を作って項目を選べるように…燈の方も」（月の links/assets/menu.js と同じ形）
   全ページ共通のメニュー（11/3 テスターの声「メニューが見にくい」→ 項目はゴシックの太字・英字の小見出しなし・説明を濃く）。右上の三本線 → 右から出る紙。昼と夜の切り替えもここ（night.js）。
   ページを足すときは L に1行足すだけ。/#shop・/#deal・/#trip はリストの欄ボタンを押す。押された数は /c の s=menu。 */
(function(){
  /* 11/2 オーナー「燈のhpを LIFE NOTE…関東おでかけリスト・おかいものリスト 完全に分ける」→ / は入口、/odekake と /okaimono に分けた */
  var P=location.pathname.replace(/^\/townnotes\//,"/odekake").replace(/\.html$/,""),here=
    /^\/sagasu/.test(P)?"fbuy":/^\/fudosan-list/.test(P)?"flist":/^\/chika-/.test(P)?"chika":/^\/uru/.test(P)?"uru":/^\/(index)?$/.test(P)?"tn":/^\/odekake/.test(P)?"list":/^\/okaimono/.test(P)?"okai":/^\/otoku/.test(P)?"otoku":/^\/illumination/.test(P)?"illumi":/^\/koyo/.test(P)?"koyo":/^\/koe/.test(P)?"koe":/^\/tomari/.test(P)?"tomari":/^\/ima/.test(P)?"ima":/^\/kaimawari/.test(P)?"kaimawari":/^\/furusato/.test(P)?"furusato":/^\/tanka/.test(P)?"tanka":/^\/nesage/.test(P)?"nesage":"";
  var SH=/^(\/okaimono|\/nesage|\/tanka|\/furusato|\/kaimawari|\/otoku)/.test(P);
  /* 11/7 関東不動産リスト（月の関西不動産リストと同じ）：不動産のページは不動産だけのメニュー */
  var FU=/^\/(fudosan-list|uru|sagasu|chika-|machi\/)/.test(P);
  /* 11/6 夜「おかいものからリクエストへ行くと、下のバーがおでかけ側に変わって戻れない」→ どちらのリストから来たかを覚えて、リクエストのページもそちら側にする */
  try{if(SH)sessionStorage.setItem("usagi_side","okai");else if(here&&here!=="koe")sessionStorage.setItem("usagi_side","list");if(here==="koe"&&sessionStorage.getItem("usagi_side")==="okai")SH=true;}catch(e){}
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
    ["KANTO REAL ESTATE","flist","/fudosan-list","関東不動産リスト","地価・人口・新しい施設・制度を、公式の数字で"],
    ["OKAIMONO LIST","okai","/okaimono","くらべたおかいものリスト","1個あたりで比べた、いちばん安い物"],
    ["LIFE NOTE","tn","/","LIFE NOTE","関東のくらしのノート"]
  ];
  if(SH)L=[
    /* 11/6 /okaimono を「くらべる」1つに作り直した → メニューも下のバー（くらべる・買い時・セール・ふるさと）と同じ並びに */
    ["COMPARE","okai","/okaimono","くらべる","日用品21種類の最安とおすすめ"],
    ["PRICE DOWN","nesage","/nesage","買い時","ふだんより安い物"],
    ["SALE","kaimawari","/kaimawari","セール","買いまわりの1,000円ぽっきり"],
    ["FURUSATO","furusato","/furusato","ふるさと納税","寄付1万円あたりの量で・12/31まで"],
    ["DEALS","otoku","/otoku","お得まとめ・AIに聞く","セール・ふるさと・宿をまとめて"],
    ["-","CONTACT"],
    ["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],
    ["-","関連サイト"],
    ["KANTO ODEKAKE","list","/odekake","関東おでかけリスト","関東のイベント・新しいお店や施設"],
    ["KANTO REAL ESTATE","flist","/fudosan-list","関東不動産リスト","地価・人口・新しい施設・制度を、公式の数字で"],
    ["LIFE NOTE","tn","/","LIFE NOTE","関東のくらしのノート"]
  ];
  /* 11/9 オーナーOK（見本4）→ 11/9 12:54 オーナー「不動産だけメニューも色々ちがくない？」→ おでかけと同じ形（タイル6つ／ご相談・お問い合わせ／関連サイト）。関東はアフィリエイトだけなので申し込みは入れない */
  if(FU)L=[
    ["LIST","flist","/fudosan-list","関東不動産リスト","地価・人口・制度"],
    ["SEARCH","fq","/fudosan-list?fq=q","街の名前で探す","市区町村の名前で"],
    ["MAP","fmap","/fudosan-list?fq=map","地図で見る","上がった街を色で"],
    ["RANKING","chika","/chika-kanto","地価ランキング","関東329の市区町村"],
    ["SELL","uru","/uru.html","家を売りたい方へ","相場から順に"],
    ["BUY","fbuy","/sagasu","家を買いたい方へ","住む街の値段と物件"],
    ["-","CONTACT"],
    ["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],
    ["-","関連サイト"],
    ["KANTO ODEKAKE","list","/odekake","関東おでかけリスト","関東のイベント・新しいお店や施設"],
    ["OKAIMONO LIST","okai","/okaimono","くらべたおかいものリスト","1個あたりで比べた、いちばん安い物"],
    ["LIFE NOTE","tn","/","LIFE NOTE","関東のくらしのノート"]
  ];
  /* 入口は、3つのリストとご連絡だけ */
  if(here==="tn")L=[["-","LIFE NOTE"],
    ["KANTO ODEKAKE","list","/odekake","関東おでかけリスト","関東のイベント・新しいお店や施設"],
    ["KANTO REAL ESTATE","flist","/fudosan-list","関東不動産リスト","地価・人口・新しい施設・制度を、公式の数字で"],
    ["OKAIMONO LIST","okai","/okaimono","くらべたおかいものリスト","1個あたりで比べた、いちばん安い物"],
    ["-","CONTACT"],
    ["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],
    ["LISTING","listing","https://ig.me/m/ai_usagichan1","おでかけ掲載","新しいお店やイベントのご紹介"]];
  var css=
  "#upan .fml{padding:4px 4px 0}#upan .fmt small{display:block;font-family:Jost,sans-serif;font-size:11px;letter-spacing:.3em;color:#9C8775}#upan .fmt b{display:block;font-family:\"Shippori Mincho\",serif;font-size:22px;font-weight:600;letter-spacing:.12em;color:#2B2622;margin:2px 0 6px}#upan .fmg{font-size:12px;letter-spacing:.3em;color:#9C8775;margin:20px 0 0;padding-bottom:8px;border-bottom:1px solid #E6E6E6}#upan .fmr{display:block;text-decoration:none;color:#2B2622;padding:14px 6px;border-bottom:1px solid #EFEFEF}#upan .fmr small{display:block;font-family:Jost,sans-serif;font-size:10.5px;letter-spacing:.26em;color:#9C8775}#upan .fmr b{display:block;font-family:\"Shippori Mincho\",serif;font-size:17px;font-weight:700;letter-spacing:.06em;margin-top:3px}#upan .fmr.cur b:after{content:\"　いま\";font-family:sans-serif;font-size:11px;color:#B5735A;font-weight:400}"+
  "#upan .ufx{margin:22px 4px 6px;padding-top:16px;border-top:1px solid #E6E6E6;font-size:12px;color:#9C8775;text-align:center;line-height:2}#upan .ufx a{color:#857A70;text-decoration:none;margin:0 6px}"+
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
  "#upan nav{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:4px 16px 10px}"+
  /* 11/4 オーナーが見本Bを選んだ：おでかけの6つを絵つきのタイル2列に、ご相談・ほかは小さいボタン2列に。1画面に収める */
  "#upan .ug{margin:16px 4px 8px;font-size:11px;font-weight:700;letter-spacing:.18em;color:#8C7B6E}"+
  "#upan .ug small{display:none}"+
  "#upan .utg{display:grid;grid-template-columns:1fr 1fr;gap:10px}"+
  "#upan .usm{display:grid;grid-template-columns:1fr 1fr;gap:8px}"+
  "#upan a.ui{position:relative;text-decoration:none;color:#2B2622;-webkit-tap-highlight-color:transparent;transition:transform .12s}"+
  "#upan a.ui:active{transform:scale(.97)}"+
  "#upan a.ui small{display:none}"+
  "#upan a.tl{display:flex;flex-direction:column;gap:3px;padding:14px 12px 13px;border-radius:16px;background:linear-gradient(160deg,#F7F8FA,#EEF0F4);box-shadow:inset 0 0 0 1px #E6E8EC}"+
  "#upan a.tl i{display:block;width:26px;height:26px;margin-bottom:6px}"+
  "#upan a.tl span{font-weight:700;font-size:14px;letter-spacing:.04em;line-height:1.35}"+
  "#upan a.tl em{font-style:normal;font-size:10.5px;color:#7A6E66;line-height:1.4}"+
  "#upan a.sm{display:flex;align-items:center;gap:8px;padding:11px 10px;border-radius:12px;background:#F6F6F7;font-size:12px;font-weight:700;line-height:1.35}"+
  "#upan a.sm i{display:block;width:17px;height:17px;flex:none}"+
  /* 11/6 オーナー「関連サイトがもう少しだけ大きくてもいい」→ 関連サイトの2つだけ少し大きく */
  "#upan .urel a.sm{padding:15px 10px;font-size:13px;gap:8px;white-space:nowrap}#upan .urel a.sm i{width:20px;height:20px}"+
  "#upan a.sm em{display:none}"+
  "#upan a.ui svg{width:100%;height:100%;fill:none;stroke:#3A2F28;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}"+
  "#upan a.sm svg{stroke:#8C7B6E}"+
  "#upan a.ui.cur{box-shadow:inset 0 0 0 1.5px #3A2F28}"+
  "#upan a.ui u{position:absolute;right:10px;top:10px;text-decoration:none;font-size:10px;font-weight:700;letter-spacing:.08em;color:#fff;background:#3A2F28;border-radius:99px;padding:3px 8px}"+
  "#upan a.sm u{position:static;margin-left:auto;padding:2px 6px}"+
  /* 夜は見本と同じ紺と金（ページ全体の反転を先に打ち消した色） */
  "html.night #upan{background:#ebeeff}html.night #upan .uh{border-bottom-color:#dbe1ff}"+
  "html.night #upan a.tl{background:linear-gradient(160deg,#dbe1ff,#e6eaff);box-shadow:inset 0 0 0 1px #d4dbff}"+
  "html.night #upan a.sm{background:#e3e8ff}html.night #upan a.ui svg{stroke:#5f4000}html.night #upan a.sm svg{stroke:#646a82}"+
  "html.night #upan a.ui.cur{box-shadow:inset 0 0 0 1.5px #5f4000}html.night #upan a.ui u{background:#5f4000;color:#ebeeff}"+
  "html.night #upan .us{border-top-color:#dbe1ff}"+
  "#upan .ut{display:flex;align-items:center;justify-content:space-between;margin:8px 20px 0;padding:14px 0;border-top:1px solid #EDEDED;font-size:13.5px}"+
  "#upan .ut em{display:block;font-style:normal;font-size:11px;color:#8C7B6E;margin-top:2px}"+
  "#upan .sw{position:relative;width:50px;height:30px;border-radius:99px;border:0;background:#D9D9D9;cursor:pointer;flex:none;transition:background .2s}"+
  "#upan .sw:after{content:'';position:absolute;top:3px;left:3px;width:24px;height:24px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.2);transition:transform .2s}"+
  "#upan .sw[aria-checked=true]{background:#2B2622}"+
  "#upan .sw[aria-checked=true]:after{transform:translateX(20px)}"+
  "#upan .us{display:flex;gap:22px;justify-content:center;padding:14px 20px calc(18px + env(safe-area-inset-bottom));border-top:1px solid #EDEDED}"+
  "#upan .us a{font-family:Jost,sans-serif;font-size:13px;letter-spacing:.06em;color:#2B2622;text-decoration:none;border-bottom:1px solid #2B2622;padding:6px 0 2px}"+
  "#upan .ush{margin:4px 16px 2px;padding:8px 10px 8px 14px;border-radius:14px;background:linear-gradient(135deg,#FBEEE8,#EEF2FB);display:flex;flex-wrap:nowrap;align-items:center;gap:8px}"+
  "#upan .ush>svg{width:18px;height:18px;fill:none;stroke:#2B2622;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}"+
  "#upan .ush .ust{flex:1;min-width:0}#upan .ush .ust b{display:block;font-size:12.5px;white-space:nowrap;font-weight:700;letter-spacing:.08em;color:#2B2622}#upan .ush .ust small{display:none}"+
  "#upan .ush .ub{display:flex;gap:5px;flex:none}"+
  "#upan .ush button{flex:none;height:30px;padding:0 10px;border-radius:999px;border:1px solid #DDD;background:#fff;color:#2B2622;font:700 11.5px sans-serif;letter-spacing:.04em;cursor:pointer;white-space:nowrap;-webkit-tap-highlight-color:transparent}"+
  "#upan .ush button[data-s=share]{background:#2B2622;border-color:#2B2622;color:#fff}#upan .ush button[data-s=line]{background:#06C755;border-color:#06C755;color:#fff}"+
  "html.night #upan .ush{background:linear-gradient(135deg,#dbe1ff,#e6eaff);box-shadow:inset 0 0 0 1px #d4dbff}html.night #upan .ush button{background:#f4f6ff;border-color:#d4dbff}html.night #upan .ush button[data-s=share]{background:#2B2622;border-color:#2B2622}html.night #upan .ush button[data-s=line]{background:#06C755;border-color:#06C755}"+
  "html.umenu-open,html.umenu-open body{overflow:hidden}"+
  "@media (prefers-reduced-motion:reduce){#upan,#umask{transition:none}}";
  function ck(k){try{navigator.sendBeacon("/c?f=menu&s=menu&k="+encodeURIComponent(k.slice(0,40)));}catch(e){}}
  var SUN='<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.3M12 19.1v2.3M2.6 12h2.3M19.1 12h2.3M5.35 5.35l1.6 1.6M17.05 17.05l1.6 1.6M5.35 18.65l1.6-1.6M17.05 6.95l1.6-1.6"/></svg>',MOON='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.6 14.6A8 8 0 0 1 9.4 4.4a8 8 0 1 0 10.2 10.2z"/><path class="sp" d="M17.2 3.4v2.8M15.8 4.8h2.8"/></svg>',MK="";
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  function openView(v){var b=document.querySelector('button[data-v="'+v+'"]');if(!b)return;b.click();setTimeout(function(){var y=b.getBoundingClientRect().top+scrollY-10;scrollTo({top:y,behavior:"smooth"});},60);}
  function openMap(){var n=0;(function t(){var b=document.querySelector(".tnbtn");if(b){b.click();return;}if(++n<40)setTimeout(t,100);})();}
  var GJ={"KANTO ODEKAKE":"おでかけ","KANTO REAL ESTATE":"不動産","OKAIMONO LIST":"くらべた買い物","LIFE NOTE":"3つのリスト","CONTACT":"ご相談・お問い合わせ"};
  function ug(k){return '<div class="ug">'+(GJ[k]||k)+(GJ[k]?'<small>'+k+'</small>':"")+'</div>';}
  var IC={
    list:'<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 9h8M8 12.5h8M8 16h5"/>',
    map:'<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/>',
    ima:'<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    illumi:'<path d="M10 3C10.6 7.5 11.5 8.4 16 9C11.5 9.6 10.6 10.5 10 15C9.4 10.5 8.5 9.6 4 9C8.5 8.4 9.4 7.5 10 3Z"/><path d="M17.5 13.2c.3 2 .7 2.4 2.5 2.7c-1.8.3-2.2.7-2.5 2.7c-.3-2-.7-2.4-2.5-2.7c1.8-.3 2.2-.7 2.5-2.7Z"/>',
    koyo:'<path d="M12 3l1.6 3.8 3-1.6-.6 3.6 3.6-.4-2 3 2.6 1.6-4 1 .6 2.4-3-1.2-1.8 3-1.8-3-3 1.2.6-2.4-4-1 2.6-1.6-2-3 3.6.4-.6-3.6 3 1.6z"/><path d="M12 15.5V21"/>',
    tomari:'<path d="M3 18V8M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5"/><circle cx="7" cy="11" r="1.8"/>',
    koe:'<path d="M5 5h14v10H10l-4 4v-4H5z"/><path d="M9 9.5h6M9 12h4"/>',
    listing:'<path d="M4 9l2-4.5h12L20 9"/><path d="M4 9a2 2 0 0 0 4 0a2 2 0 0 0 4 0a2 2 0 0 0 4 0a2 2 0 0 0 4 0"/><path d="M5.5 11v9h13v-9"/><path d="M9.5 20v-5h5v5"/>',
    flist:'<path d="M4 20V9l5-3v14M9 20V4l8 4v12M4 20h16"/><path d="M12 10h2M12 13h2M12 16h2"/>',
    tn:'<path d="M6 3h10a2 2 0 0 1 2 2v16l-3-2-3 2-3-2-3 2V5"/><path d="M9 8h6M9 11h6"/>',
    fbuy:'<path d="M4 11l8-6 8 6v9H4z"/><circle cx="12" cy="14" r="2.5"/><path d="M13.8 15.8L16 18"/>',
    fq:'<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    fmap:'<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/>',
    chika:'<path d="M4 20V10M10 20V5M16 20v-7M22 20H2"/>',
    chikao:'<path d="M4 20V12M9 20V7M14 20v-5M19 20V9M2 20h20"/>',
    fnew:'<path d="M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6-5.3-3-5.3 3 1.2-6L3.4 9.3l6-.7z"/>',
    uru:'<path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/>',
    satei:'<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/>',
    okai:'<path d="M5 8h14l-1.2 11.2a2 2 0 0 1-2 1.8H8.2a2 2 0 0 1-2-1.8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    tanka:'<path d="M12 4v16M5 8h14M7 8l-3 6a3 3 0 0 0 6 0zM17 8l-3 6a3 3 0 0 0 6 0z"/>',
    furusato:'<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    nesage:'<path d="M4 6l6 6 4-4 6 6"/><path d="M20 10v4h-4"/>',
    kaimawari:'<path d="M20 12l-8 8-8-8V4h8z"/><circle cx="8" cy="8" r="1.5"/>',
    otoku:'<path d="M12 3v3M12 18v3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M3 12h3M18 12h3"/><circle cx="12" cy="12" r="3.5"/>',
    gyosha:'<path d="M3 12l4-4 4 3 3-3 7 6"/><path d="M7 15l3 3M11 14l3 3M14 13l2 2"/>'
  };
  var ST={okai:"くらべる",tanka:"1個あたり",furusato:"ふるさと納税",nesage:"買い時",kaimawari:"セール",otoku:"お得まとめ",list:"おでかけリスト",ima:"いま行ける",illumi:"イルミネーション",koyo:"紅葉ライトアップ",tomari:"泊まりで行く",flist:"不動産リスト",chika:"地価ランキング",chikao:"大阪市24区",
    uru:"家を売りたい方へ",satei:"売却・査定のご相談"};
  var SS={okai:"日用品の最安とおすすめ",tanka:"1Lあたり・1kgあたり",furusato:"寄付1万円あたりの量",nesage:"ふだんより安い物",kaimawari:"1,000円ぽっきり",otoku:"AIに聞く・宿",list:"開催中・これから",map:"近くをさがす",ima:"近い順・きょう開く所",illumi:"日程・無料の所",koyo:"夜の時間・料金",tomari:"遠くのおでかけと宿",
    flist:"地価・人口・制度",fq:"市区町村の名前で",fmap:"上がった街を色で",chika:"関東329の街",chikao:"24区の上がり幅",fnew:"最近足した数字"};
  function item(x,tile){var cur=x[1]===here,ext=/^https?:/.test(x[2]);
    return '<a class="ui '+(tile?"tl":"sm")+(cur?" cur":"")+'" data-k="'+x[1]+'" href="'+x[2]+'"'+(ext?' target="_blank" rel="noopener"':"")+(cur?' aria-current="page"':"")+'>'+(cur&&tile?'<u>いま</u>':'')+'<i><svg viewBox="0 0 24 24" aria-hidden="true">'+(IC[x[1]]||IC.list)+'</svg></i><span data-n="'+esc(x[3])+'">'+esc((!tile&&x[1]==="okai")?"おかいものリスト":(ST[x[1]]||x[3]))+'</span><em>'+esc(tile?(SS[x[1]]||x[4]):x[4])+'</em>'+(cur&&!tile?'<u>いま</u>':'')+'</a>';}
  function build(){
    var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
    var btn=document.createElement("button");btn.id="umenu";btn.type="button";btn.setAttribute("aria-label","メニューを開く");btn.setAttribute("aria-expanded","false");btn.setAttribute("aria-controls","upan");btn.innerHTML="<i></i><i></i><i></i>";
    var mask=document.createElement("div");mask.id="umask";
    var pan=document.createElement("div");pan.id="upan";pan.setAttribute("role","dialog");pan.setAttribute("aria-modal","true");pan.setAttribute("aria-label","メニュー");pan.setAttribute("aria-hidden","true");
    var h='<div class="uh"><a class="uhl" href="/" aria-label="LIFE NOTE の入口へ"><img src="'+(document.documentElement.classList.contains("night")?"/logo-s-night.png":"/logo-s.png")+'" alt=""><b>LIFE NOTE</b></a><button class="ux" type="button" aria-label="メニューを閉じる">×</button></div><nav>'+(here==="tn"?"":ug(FU?"KANTO REAL ESTATE":SH?"OKAIMONO LIST":"KANTO ODEKAKE"));
    /* 最初のまとまり＝タイル、あとのまとまり＝小さいボタン */
    var tiled=false,openG="",rel=false;
    L.forEach(function(x){
      if(x[0]==="-"){if(openG){h+='</div>';openG="";}h+=ug(x[1]);rel=x[1]==="関連サイト"||x[1]==="ほかのリスト";return;}
      if(!openG){openG=tiled?"usm":"utg";tiled=true;h+='<div class="'+openG+(rel?" urel":"")+'">';}
      h+=item(x,openG==="utg");
    });
    if(openG)h+='</div>';
    /* 10/31 オーナー「夜の見た目？なにこれ」→ 切り替えは右上の太陽と月のマークだけ（月と同じ） */
    /* 11/4 オーナー「hp共有を入れよう アプリにしたら誰かに送れない」「cだけで良いかも」→ 11/4「もう少し分かりやすくても良かった、さっきの感じで下の方でよい」→ C の箱をメニューの下に */
    h+='</nav>'+
      '<div class="ush"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15V3"/><path d="M7.5 7.5L12 3l4.5 4.5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg><div class="ust"><b>友だちに送る</b><small>このページを LINE などで送れます</small></div><div class="ub">'+(navigator.share?'<button type="button" data-s="share">送る</button>':'')+'<button type="button" class="nofilt" data-s="line">LINE</button><button type="button" data-s="copy">コピー</button></div></div>'+
      '<div class="us"><a href="https://www.instagram.com/ai_usagichan1/" target="_blank" rel="noopener">Instagram</a><a href="https://www.threads.com/@ai_usagichan1" target="_blank" rel="noopener">Threads</a><a href="https://x.com/ai_usagichan" target="_blank" rel="noopener">X</a></div>';
    pan.innerHTML=h;
    document.body.appendChild(btn);document.body.appendChild(mask);document.body.appendChild(pan);
    var last=null;
    function open(){last=document.activeElement;var nv=pan.querySelector("nav");if(nv)nv.scrollTop=0;document.documentElement.classList.add("umenu-open");mask.classList.add("on");pan.classList.add("on");pan.setAttribute("aria-hidden","false");btn.setAttribute("aria-expanded","true");setTimeout(function(){pan.querySelector(".ux").focus();},50);ck("メニュー｜開く");}
    function close(){document.documentElement.classList.remove("umenu-open");mask.classList.remove("on");pan.classList.remove("on");pan.setAttribute("aria-hidden","true");btn.setAttribute("aria-expanded","false");if(last&&last.focus)last.focus();}
    pan.querySelector(".ush").addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;var k=b.getAttribute("data-s"),u=location.origin+location.pathname,t=document.title;ck(MK+"送る（"+b.textContent+"）");
      if(k==="share"){navigator.share({title:t,url:u}).catch(function(){});return;}
      if(k==="line"){location.href="https://line.me/R/share?text="+encodeURIComponent(t+"\n"+u);return;}
      var done=function(){b.textContent="コピーしました";setTimeout(function(){b.textContent="コピー";},1800);};
      if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(u).then(done,function(){prompt("このURLをコピーしてください",u);});else prompt("このURLをコピーしてください",u);});
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
      var k=a.getAttribute("data-k");var sp=a.querySelector("span");ck("メニュー｜"+(sp.getAttribute("data-n")||sp.textContent));
      if(k===here&&k!=="map"){e.preventDefault();close();window.scrollTo({top:0,behavior:"smooth"});return;}
      if(k==="map"&&here==="list"){e.preventDefault();close();setTimeout(openMap,280);}
      if(/^(shop|deal|trip)$/.test(k)&&here==="otoku"){e.preventDefault();close();setTimeout(function(){openView(k);},280);}
    });});
    var hv=location.hash.slice(1);
    if((here==="list"&&hv==="map")||(here==="otoku"&&/^(shop|deal|trip|hot)$/.test(hv))){try{history.replaceState(null,"",location.pathname+location.search);}catch(e){}if(hv==="map")openMap();else setTimeout(function(){openView(hv==="hot"?"pick":hv);},300);}
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
    if(e.button>0||e.metaKey||e.ctrlKey||e.shiftKey)return;
    var a=e.target.closest&&e.target.closest('a[href*="google.com/maps"],a[href*="maps.google."]');if(!a)return;
    var v=get();e.preventDefault();
    if(v==="google"||v==="apple")go(a,v);else sheet(a);
  },true);
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

/* 11/6 夜（読み上げ・キーボード）：どのページにも同じ手当て。見た目は変えない
   ・しぼりこみボタンに「押されている」を伝える（aria-pressed）
   ・本文に main の目印
   ・「地図」リンクに、どこの地図かを名前で
   ・名前のない検索欄に名前 */
(function(){
function pr(){var B=document.querySelectorAll("#flt button,.flt button,.tabs button,.sbk button,.mpc button,.dflt button");
 for(var i=0;i<B.length;i++){var b=B[i];if(b.getAttribute("role")==="tab")continue;var on=b.classList.contains("on");if(b.getAttribute("aria-pressed")!==String(on))b.setAttribute("aria-pressed",on);}}
function fix(){
 if(!document.querySelector("main,[role=main]")){var w=document.querySelector(".wrap")||document.querySelector(".paper");if(w)w.setAttribute("role","main");}
 var M=document.querySelectorAll("a.mp");for(var i=0;i<M.length;i++){var a=M[i];if(a.hasAttribute("aria-label"))continue;var box=a.closest(".it,.card,article,li")||a.parentElement,t=box&&box.querySelector(".t");
  var n=t?t.textContent.replace(/（\d+月\d+日まで）/,"").trim():"";if(n)a.setAttribute("aria-label",n.slice(0,40)+"の地図（Googleマップ）");}
 var S=document.querySelectorAll("input[type=search],input.fi,#q");for(var j=0;j<S.length;j++){var s=S[j];if(s.hasAttribute("aria-label")||s.labels&&s.labels.length)continue;s.setAttribute("aria-label",location.pathname.indexOf("fudosan")>=0?"市・区・町の名前で探す":/okaimono|nesage|kaimawari/.test(location.pathname)?"商品の名前で探す":s.placeholder?"検索（"+s.placeholder+"）":"街の名前やおでかけで探す");}
 pr();}
var tm;function later(){clearTimeout(tm);tm=setTimeout(fix,80)}
if(document.readyState!=="loading")fix();else document.addEventListener("DOMContentLoaded",fix);
addEventListener("load",fix);
/* 押したボタンが作り直されてフォーカスが消えた時（「人口・駅」など）は、同じ名前のボタンへ戻す */
document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("button"),tx=b&&b.textContent,cl=b&&b.parentElement&&b.parentElement.className;
 function back(){pr();if(!b||document.activeElement!==document.body)return;if(b.isConnected&&b.offsetParent){b.focus({preventScroll:true});return;}var c=document.querySelectorAll("button");for(var i=0;i<c.length;i++){if(c[i].textContent===tx&&c[i].parentElement&&c[i].parentElement.className===cl){c[i].focus({preventScroll:true});break;}}}
 setTimeout(back,0);setTimeout(back,120);},true);
try{new MutationObserver(later).observe(document.documentElement,{childList:true,subtree:true});}catch(e){}
})();

/* 11/7 関東不動産リスト：お家の売却・査定のご相談はメールで（月の menu.js と同じ。会社のHPは通さない）→ href="#ml" をメールに */
/* 11/9 オーナー「関東はアフェリエイトでいく。対応できないからだ」→ 関東はご相談を受けない。#ml が残っていても「家を売る前に」へ */
(function(){function ml(){document.querySelectorAll('a[href="#ml"]').forEach(function(a){a.href="/uru.html";});}if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",ml);else ml();document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest('a[href="#ml"]');if(a){ml();}},true);})();
