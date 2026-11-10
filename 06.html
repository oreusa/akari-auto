/* 11/9 ほかのリスト（ページの下とメニューで同じ名前・同じタイル）。cur＝いま見ているリスト（出さない） */
window.TN_OL=(function(){var life=/usagi-life|lifenote|life-note/.test(location.host),p=location.pathname;
return {life:life,cur:/^\/(koe|privacy)/.test(p)?"":/fudosan|machi|uru|sagasu|chika|gyosha|moushikomi|jikka/.test(p)?"fu":/okaimono|otoku|tanka|nesage|furusato|kaimawari/.test(p)?"ok":"od",
I:{od:'<path d="M12 21s-6-5.6-6-10.5A6 6 0 0 1 18 10.5C18 15.4 12 21 12 21z"/><circle cx="12" cy="10.5" r="2.2"/>',
fu:'<path d="M4 11l8-6 8 6"/><path d="M6 10v9h12v-9"/><path d="M10 19v-5h4v5"/>',
ok:'<path d="M6 8h12l-1 12H7z"/><path d="M9 8a3 3 0 0 1 6 0"/>'},
L:[["od","ODEKAKE",life?"関東おでかけリスト":"関西おでかけリスト","週末どこ行く？を日付と地図で","/odekake","#E39B3A"],
["fu","REAL ESTATE",life?"関東不動産リスト":"関西不動産リスト","地価・人口・制度を公式の数字で","/fudosan-list","#4F7BA8"],
["ok","SHOPPING","おかいもの","比べた最安と、今だけのお得","/okaimono","#C2727F"]],
tiles:function(pre){var o=this,h="";o.L.forEach(function(x){if(x[0]===o.cur)return;h+='<a class="ot" style="--c:'+x[5]+'" href="'+x[4]+'" data-k="'+pre+x[2]+'"><svg viewBox="0 0 24 24" aria-hidden="true">'+o.I[x[0]]+'</svg><small>'+x[1]+'</small><b>'+x[2]+'</b><i>'+x[3]+'</i></a>';});return h;}};})();
/* 11/9 投稿から来た人を数える（URLの ?f=<投稿の印>。学習エンジンが「サイトに来た数」で投稿に点数を付ける。1回の訪問で1回だけ） */
(function(){try{var f=new URLSearchParams(location.search).get("f");if(!f||!/^[A-Za-z0-9_-]{1,32}$/.test(f))return;if(localStorage.getItem("usagi_owner")==="1")return;if(sessionStorage.getItem("tn_f")===f)return;sessionStorage.setItem("tn_f",f);var b=JSON.stringify({k:"来訪：SNS｜"+f});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}})();
/* 11/9 色（見本4）を全ページに */
(function(){try{if(document.getElementById("iro-css"))return;var l=document.createElement("link");l.id="iro-css";l.rel="stylesheet";l.href="/assets/iro.css?v=15";(document.head||document.documentElement).appendChild(l);}catch(e){}})();
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
/* 10/31 オーナー「三本線を作って項目を選べるように」「分かりやすく、使いやすく、細かいところまで」
   全ページ共通のメニュー（11/3 テスターの声「メニューが見にくい」→ 項目はゴシックの太字・英字の小見出しなし・説明を濃く）。右上の三本線 → 右から出る紙。昼と夜の切り替えもここ（night.js）。
   ページを足すときは L に1行足すだけ。押された数は /c に「メニュー｜名前」で数える。 */
(function(){
  var P=location.pathname.replace(/^\/townnotes\//,"/"),FU=/^\/(fudosan|uru|moushikomi|gyosha|sagasu|chika-|machi\/|jikka)/.test(P),here=
    /^\/sagasu/.test(P)?"fbuy":/^\/fudosan-list/.test(P)?"flist":/^\/chika-kansai/.test(P)?"chika":/^\/chika-osaka/.test(P)?"chikao":/^\/(odekake|index\.html)$/.test(P)?"list":/^\/illumination/.test(P)?"illumi":/^\/koyo/.test(P)?"koyo":/^\/koe/.test(P)?"koe":/^\/tomari/.test(P)?"tomari":/^\/ima/.test(P)?"ima":/^\/(town-notes)?$/.test(P)?"tn":/^\/uru/.test(P)?"uru":/^\/gyosha/.test(P)?"gyosha":/^\/jikka/.test(P)?"jikka":/^\/moushikomi/.test(P)?"satei":/^\/(fudosan|gyosha)/.test(P)?"fudosan":"";
  var L=[
    ["LIST","list","/odekake","関西おでかけリスト","開催中・これからのおでかけ"],
    ["MAP","map","/odekake#map","地図で見る","関西の地図から、近くのおでかけを"],
    ["NOW","ima","/ima","いまから行けるおでかけ","いる場所から近い順に、きょう開いている所"],
    ["ILLUMINATION","illumi","/illumination.html","イルミネーション日程","2026-2027　府県ごとの日程と無料の所"],
    ["AUTUMN LEAVES","koyo","/koyo","紅葉ライトアップ日程","2026　夜の時間・料金・近くの宿"],
    ["STAY","tomari","/tomari.html","泊まりで行くおでかけ","遠くのおでかけと、近くの宿"],
    ["-","CONTACT"],
    /* 11/1 オーナー「おでかけ側にご相談いらねぇだろ」→ 不動産のご相談は不動産リスト側だけ */
    ["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],
    ["LISTING","listing","https://ig.me/m/fudousan_ai_si","おでかけ掲載","新しいお店やイベントのご紹介"]
  ];
  /* 11/1 オーナー「完全に分ける。メニューもそうだ」→ 関西不動産リストのページは不動産だけのメニュー */
  /* 11/7 オーナー「違うページ飛ぶし使いにくい」→ くらべたおかいものリストも TOWN NOTE の中で開く（functions/okaimono.js）。下のバーと同じ並び */
  var SHP=/^\/(okaimono|nesage|tanka|furusato|kaimawari|otoku)/.test(P);
  if(SHP)L=[
    ["-","OKAIMONO LIST"],
    ["COMPARE","okai","/okaimono","くらべる","日用品21種類の最安とおすすめ"],
    ["PRICE DOWN","nesage","/nesage","買い時","ふだんより安い物"],
    ["SALE","kaimawari","/kaimawari","セール","買いまわりの1,000円ぽっきり"],
    ["FURUSATO","furusato","/furusato","ふるさと納税","寄付1万円あたりの量で・12/31まで"],
    ["DEALS","otoku","/otoku","お得まとめ・AIに聞く","セール・ふるさと・宿をまとめて"],
    ["-","CONTACT"],
    ["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],
    ["-","関連サイト"],
    ["KANSAI ODEKAKE","list","/odekake","関西おでかけリスト","関西のイベント・新しいお店や施設"],
    ["KANSAI REAL ESTATE","flist","/fudosan-list","関西不動産リスト","地価・人口・新しい施設・制度を、公式の数字で"],
    ["TOWN NOTE","tn","/","TOWN NOTE","関西の街のノート"]
  ];
  /* 11/9 オーナーOK（見本4）→ 11/9 12:54 オーナー「不動産だけメニューも色々ちがくない？」→ おでかけと同じ形（タイル6つ／ご相談・お問い合わせ／関連サイト） */
  /* 11/9 オーナー「これ売る前と業者のやつどこ？」→ 不動産メニューに「家を売る前に」 */
  if(FU)L=[
    ["LIST","flist","/fudosan-list","関西不動産リスト","地価・人口・制度"],
    ["SELL","uru","/uru","家を売る前に","相場・売り出し価格・大事なこと"],
    ["BUY","fbuy","/sagasu","家を買いたい方へ","住む街の値段と物件"],
    ["JIKKA NOTE","jikka","/jikka/","実家・空き家ノート","相続した家を売る・片付ける・解体する前に"],
    ["FOR PROFESSIONALS","gyosha","/gyosha","業者さま・士業の先生方へ","動かしにくい不動産のご相談"],
    ["-","CONTACT"],
    ["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],
    ["APPLY","satei","/moushikomi","売却のお申し込み","無料・約1分"],
    ["-","関連サイト"],
    ["KANSAI ODEKAKE","list","/odekake","関西おでかけリスト","関西のイベント・新しいお店や施設"],
    ["OKAIMONO LIST","okai","/okaimono","くらべたおかいものリスト","日用品を1個あたりでくらべて最安へ"],
    ["TOWN NOTE","tn","/","TOWN NOTE","関西の街のノート"]
  ];
  else if(!SHP)L=L.concat([["-","関連サイト"],["KANSAI REAL ESTATE","flist","/fudosan-list","関西不動産リスト","地価・人口・新しい施設・制度を、公式の数字で"],["OKAIMONO LIST","okai","/okaimono","くらべたおかいものリスト","日用品を1個あたりでくらべて最安へ"],["TOWN NOTE","tn","/","TOWN NOTE","関西の街のノート"]]);
  /* 11/9 オーナー「ちゃんと統一できてる？メニューは？」→ 関連サイトをページの下と同じ「ほかのリスト」タイルに（いまのリストは出さない・入口へは上の名前から）。おでかけは下のバーと同じ物（地図・泊まり）を外す */
  (function(){var o=[],sk=false;L.forEach(function(x){if(x[0]==="-"){sk=x[1]==="関連サイト";if(sk)return;}else if(sk)return;if(x[1]==="map"||x[1]==="tomari")return;o.push(x);});o.push(["-","ほかのリスト"]);L=o;})();
  /* TOWN NOTE の入口ページは、3つのリストとご相談だけ（11/7 夜のミス帳 #98） */
  // 11/4 オーナー「売る前にと売却は不動産だけ」「1番最初だし」→ 入口のメニューからは外す（不動産のページには残す）
  if(/^\/(town-notes)?$/.test(P))L=[["-","TOWN NOTE"],["KANSAI ODEKAKE","list","/odekake","関西おでかけリスト","関西のイベント・新しいお店や施設"],["KANSAI REAL ESTATE","flist","/fudosan-list","関西不動産リスト","地価・人口・新しい施設・制度を、公式の数字で"],["OKAIMONO LIST","okai","/okaimono","くらべたおかいものリスト","日用品を1個あたりでくらべて最安へ"],["-","CONTACT"],["REQUEST","koe","/koe","リクエスト・感想","増やしてほしい・これがほしい・使ってみた感想"],["LISTING","listing","https://ig.me/m/fudousan_ai_si","おでかけ掲載","新しいお店やイベントのご紹介"]];
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
  function ck(k){try{if(localStorage.getItem("usagi_owner")==="1")return;}catch(e){}try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}
  var SUN='<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.3M12 19.1v2.3M2.6 12h2.3M19.1 12h2.3M5.35 5.35l1.6 1.6M17.05 17.05l1.6 1.6M5.35 18.65l1.6-1.6M17.05 6.95l1.6-1.6"/></svg>',MOON='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19.6 14.6A8 8 0 0 1 9.4 4.4a8 8 0 1 0 10.2 10.2z"/><path class="sp" d="M17.2 3.4v2.8M15.8 4.8h2.8"/></svg>',MK="メニュー｜";
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  var GJ={"KANSAI ODEKAKE":"おでかけ","OKAIMONO LIST":"くらべたおかいもの","KANSAI REAL ESTATE":"不動産","TOWN NOTE":"3つのリスト","CONTACT":"ご相談・お問い合わせ"};
  function ug(k){return '<div class="ug">'+esc(GJ[k]||k)+(GJ[k]?'<small>'+k+'</small>':"")+'</div>';}
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
    gyosha:'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M3 13h18"/>',
    gyosha:'<path d="M3 12l4-4 4 3 3-3 7 6"/><path d="M7 15l3 3M11 14l3 3M14 13l2 2"/>',
    okai:'<path d="M5 8h14l-1.2 12H6.2z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    jikka:'<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M9 20v-4a3 3 0 0 1 6 0v4"/>'
  };
  var ST={list:"おでかけリスト",ima:"いま行ける",illumi:"イルミネーション",koyo:"紅葉ライトアップ",tomari:"泊まりで行く",flist:"不動産リスト",chika:"地価ランキング",chikao:"大阪市24区",
    uru:"家を売りたい方へ",satei:"売却のお申し込み",gyosha:"業者さま・士業の先生方へ",okai:"おかいものリスト",jikka:"実家・空き家ノート"};
  var SS={list:"開催中・これから",map:"近くをさがす",ima:"近い順・きょう開く所",illumi:"日程・無料の所",koyo:"夜の時間・料金",tomari:"遠くのおでかけと宿",
    flist:"地価・人口・制度",fq:"市区町村の名前で",fmap:"上がった街を色で",chika:"関西205の街",chikao:"24区の上がり幅",fnew:"最近足した数字",okai:"1個あたりで最安"};
  function item(x,tile){var cur=x[1]===here,ext=/^https?:/.test(x[2]);
    return '<a class="ui '+(tile?"tl":"sm")+(cur?" cur":"")+'" data-k="'+x[1]+'" href="'+x[2]+'"'+(ext?' target="_blank" rel="noopener"':"")+(cur?' aria-current="page"':"")+'>'+(cur&&tile?'<u>いま</u>':'')+'<i><svg viewBox="0 0 24 24" aria-hidden="true">'+(IC[x[1]]||IC.list)+'</svg></i><span data-n="'+esc(x[3])+'">'+esc(ST[x[1]]||x[3])+'</span><em>'+esc(tile?(SS[x[1]]||x[4]):x[4])+'</em>'+(cur&&!tile?'<u>いま</u>':'')+'</a>';}
  function openMap(){var n=0;(function t(){var b=document.querySelector(".tnbtn");if(b){b.click();return;}if(++n<40)setTimeout(t,100);})();}
  function build(){
    var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
    var btn=document.createElement("button");btn.id="umenu";btn.type="button";btn.setAttribute("aria-label","メニューを開く");btn.setAttribute("aria-expanded","false");btn.setAttribute("aria-controls","upan");btn.innerHTML="<i></i><i></i><i></i>";
    var mask=document.createElement("div");mask.id="umask";
    var pan=document.createElement("div");pan.id="upan";pan.setAttribute("role","dialog");pan.setAttribute("aria-modal","true");pan.setAttribute("aria-label","メニュー");pan.setAttribute("aria-hidden","true");
    var h='<div class="uh"><a class="uhl" href="/" aria-label="TOWN NOTEの入口へ"><img src="'+(document.documentElement.classList.contains("night")?"/assets/logo-s-night.png?v=5":"/assets/logo-s.png?v=2")+'" alt=""><b>TOWN NOTE</b></a><button class="ux" type="button" aria-label="メニューを閉じる">×</button></div><nav>'+(/^\/(town-notes)?$/.test(P)||SHP?"":ug(FU?"KANSAI REAL ESTATE":"KANSAI ODEKAKE"));
    /* 最初のまとまり＝タイル、あとのまとまり＝小さいボタン */
    var tiled=false,openG="",rel=false;
    L.forEach(function(x){
      if(x[0]==="-"){if(openG){h+='</div>';openG="";}h+=ug(x[1]);rel=x[1]==="関連サイト"||x[1]==="ほかのリスト";if(x[1]==="ほかのリスト")h+='<div class="fx mfx"><div class="og">'+window.TN_OL.tiles("メニュー｜")+'</div></div>';return;}
      if(!openG){openG=tiled?"usm":"utg";tiled=true;h+='<div class="'+openG+(rel?" urel":"")+'">';}
      h+=item(x,openG==="utg");
    });
    if(openG)h+='</div>';
    /* 10/31 オーナー「夜の見た目？なにこれ」→ 切り替えは右上の太陽と月のマークだけにした */
    /* 11/4 オーナー「hp共有を入れよう アプリにしたら誰かに送れない」「cだけで良いかも」→ 11/4「もう少し分かりやすくても良かった、さっきの感じで下の方でよい」→ C の箱をメニューの下に */
    h+='</nav>'+
      '<div class="ush"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15V3"/><path d="M7.5 7.5L12 3l4.5 4.5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg><div class="ust"><b>友だちに送る</b><small>このページを LINE などで送れます</small></div><div class="ub">'+(navigator.share?'<button type="button" data-s="share">送る</button>':'')+'<button type="button" class="nofilt" data-s="line">LINE</button><button type="button" data-s="copy">コピー</button></div></div>'+
      '<div class="us"><a href="https://www.instagram.com/fudousan_ai_si/" target="_blank" rel="noopener">Instagram</a><a href="https://www.threads.com/@fudousan_ai_si" target="_blank" rel="noopener">Threads</a><a href="https://x.com/fudosan_ai_si" target="_blank" rel="noopener">X</a></div>';
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
    });});
    if(here==="list"&&location.hash==="#map"){try{history.replaceState(null,"",location.pathname+location.search);}catch(e){}openMap();}
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
/* 11/9 オーナー「申し込みページ作れないの？ hpで送信、俺にメールが届く」→ href="#ml" はお申し込みページ /moushikomi へ（メールソフトは開かない） */
(function(){function ml(){document.querySelectorAll('a[href="#ml"]').forEach(function(a){a.href="/moushikomi";});}if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",ml);else ml();document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest('a[href="#ml"]');if(a){ml();}},true);})();
/* 11/9 不動産：見た街を覚えておき、お申し込みページの「お家の場所」に先に入れる（入力を1つ減らす） */
(function(){try{var m=location.pathname.match(/^\/(?:townnotes\/)?machi\/([a-z]+-\d+)/);if(m)sessionStorage.setItem("tn_machi",m[1]);}catch(e){}})();

/* 11/9 オーナー「関連サイトも他もだけど、差別化して ここもわかりやすいように」→ ページの下を全リストで同じ順・同じ形に：
   ①そのページでやること（そのまま）②お店・主催者の方へ（小さな1行）③ほかのリスト（小さなタイル・今のリストは出さない）④FOLLOW ⑤注意書き */
(function(){
function run(){
if(document.querySelector(".fx:not(.mfx)"))return;
var O=window.TN_OL,sns=document.querySelector(".sns"),ft=document.querySelector(".ft")||document.querySelector("footer .sign");
if(/^\/(town-notes)?$/.test(location.pathname)&&!sns)return;
if(!sns&&!ft){var mm=document.querySelector("main");if(!mm)return;mm.insertAdjacentHTML("beforeend",'<div class="ft"></div>');ft=mm.lastElementChild;}
var h='<div class="fx">';
document.querySelectorAll(".sns a.co, .cos a.co").forEach(function(a){
 var en=a.getAttribute("data-en")||"";var t=(a.childNodes[0]&&a.childNodes[0].nodeValue||a.textContent).trim();
 var lab=en==="LISTING"?"お店・主催者の方へ：おでかけ掲載のご相談":t+"を見る";
 h+='<a class="fl" href="'+a.getAttribute("href")+'" rel="noopener" data-k="下｜'+lab+'">'+lab+' <span>→</span></a>';});
/* 11/9 オーナー「ちゃんと統一できてる？」→ FOLLOW の無いページ（イルミ・紅葉・泊まり・街ページなど）にも同じ下を出す */
if(!sns&&O.cur==="od")h+='<a class="fl" href="https://ig.me/m/fudousan_ai_si" rel="noopener" data-k="下｜おでかけ掲載のご相談">お店・主催者の方へ：おでかけ掲載のご相談 <span>→</span></a>';
h+='<div class="oh">ほかのリスト</div><div class="og">'+O.tiles("下の入口｜")+'</div></div>';
document.querySelectorAll(".cos, .sns a.co").forEach(function(e){e.remove();});
document.querySelectorAll("a.tnx").forEach(function(e){e.remove();});
if(!sns){ft.insertAdjacentHTML("beforebegin",h+'<div class="sns fsn"><h2>FOLLOW</h2><a href="https://www.instagram.com/fudousan_ai_si/" target="_blank" rel="noopener">Instagram<span>@fudousan_ai_si</span></a><a href="https://www.threads.com/@fudousan_ai_si" target="_blank" rel="noopener">Threads<span>@fudousan_ai_si</span></a><a href="https://x.com/fudosan_ai_si" target="_blank" rel="noopener">X<span>@fudosan_ai_si</span></a></div>');sns=document.querySelector(".fsn");}
else sns.insertAdjacentHTML("beforebegin",h);
var after=sns;if(ft&&sns.parentNode){sns.parentNode.insertBefore(ft,sns.nextSibling);after=ft;}
document.querySelectorAll(".pr-note").forEach(function(n){after.parentNode.insertBefore(n,after.nextSibling);after=n;});
}
if(document.readyState!=="loading")run();else document.addEventListener("DOMContentLoaded",run);
})();

/* 11/9 オーナー「メニュー見にくい」「差別化されたUIUX」「新しいHPを増やしても邪魔にならないように」→ 見本「ノートの見出し」OK（うんうん）
   左に見出しタブ（リストごとに1本）、右にそのノートの目次。HPを足すときは NB に1つ足すだけ（タブが1本増える。メニューは長くならない）。
   11/9 オーナー「インスタ・スレッズ・Xはロゴの方が可愛い 主張少なく」「送るも主張少なく」→ 下は細い線のマークだけ。閉じる×は右下（親指の届く所） */
(function(){
var O=window.TN_OL||{life:false},LF=O.life,P=location.pathname.replace(/^\/townnotes\//,"/").replace(/\.html$/,"");
var A={site:LF?"関東":"関西",ig:LF?"usagichan_ai_si":"fudousan_ai_si",x:LF?"ai_usagichan":"fudosan_ai_si"};
var NB=[
 {k:"od",t:"おでかけ",en:"ODEKAKE",c:"#E39B3A",lead:"週末どこ行く？を、日付と地図で。",rows:[
  ["/odekake","おでかけリスト","開催中",/^\/(odekake|index)?$/],["/ima","いま行ける","近い順・きょう開く所",/^\/ima/],
  ["/illumination","イルミネーション","日程・無料の所",/^\/illumination/],["/koyo","紅葉ライトアップ","夜の時間・料金",/^\/koyo/],
  ["/tomari","泊まりで行く","遠くのおでかけと宿",/^\/tomari/]],
  sub:[["/koe","リクエスト・感想"],["https://ig.me/m/"+A.ig,"おでかけ掲載"]]},
 {k:"fu",t:"不動産",en:"REAL ESTATE",c:"#4F7BA8",lead:A.site+"の街の値段を、公式の数字で。",rows:[
  ["/fudosan-list","不動産リスト","地価・制度",/^\/fudosan-list/],["/uru","家を売りたい","相場と大事なこと",/^\/uru/],
  ["/sagasu","家を買いたい","住む街をさがす",/^\/sagasu/],[LF?"/chika-kanto":"/chika-kansai","地価ランキング",LF?"関東の街":"関西205の街",/^\/chika-/]]
  .concat(LF?[]:[["/gyosha","業者・士業の方","窓口",/^\/gyosha/]]),
  /* 11/10 オーナー「関東も問い合わせ…関西と同じで俺に問い合わせでいい」 */sub:[["/moushikomi","売却のお申し込み"],["/koe","リクエスト・感想"]]},
 {k:"jk",t:"実家",en:"JIKKA NOTE",c:"#5E9E6E",lead:"実家・空き家、何から始める？",nw:1,rows:[
  ["/jikka/","実家・空き家ノート","4ステップ",/^\/jikka/],["/moushikomi","売却・片付け・解体","ご相談",/^$/]],
  sub:[["/koe","リクエスト・感想"]],only:!LF},
 {k:"ok",t:"おかいもの",en:"SHOPPING",c:"#C2727F",lead:"比べた最安と、今だけのお得。",rows:[
  ["/okaimono","くらべる","日用品の最安とおすすめ",/^\/okaimono/],["/nesage","買い時","ふだんより安い物",/^\/nesage/],
  ["/kaimawari","セール","1,000円ぽっきり",/^\/kaimawari/],["/furusato","ふるさと納税","寄付1万円あたりの量",/^\/furusato/],
  ["/otoku","お得まとめ","セール・ふるさと・宿",/^\/otoku/]],sub:[["/koe","リクエスト・感想"]]}
].filter(function(n){return n.only!==false;});
function side(){if(/^\/jikka/.test(P))return "jk";if(/^\/(fudosan|uru|moushikomi|gyosha|sagasu|chika-|machi\/)/.test(P))return "fu";if(/^\/(okaimono|otoku|tanka|nesage|furusato|kaimawari)/.test(P))return "ok";
 if(/^\/koe/.test(P)){try{var s=sessionStorage.getItem("tn_side");if(s)return s;}catch(e){}}return "od";}
var HERE=side();try{if(!/^\/koe/.test(P))sessionStorage.setItem("tn_side",HERE);}catch(e){}
/* 前回のつづき：ほかのページを見ていたら、目次の上に1行（この端末だけ） */
var LAST=null;try{LAST=JSON.parse(localStorage.getItem("tn_last")||"null");var tt=(document.title||"").split(/[｜|]/)[0].replace(/【[^】]*】/g,"").trim().slice(0,20);
 /* 11/10 夜 #164：括弧が無く、名前の無いページでも保存して「前回のつづき」が /undefined に飛んでいた */
 var U=location.pathname.replace(/\.html$/,"");if(tt&&!/^\/(koe|moushikomi|privacy)/.test(P)){localStorage.setItem("tn_last",JSON.stringify({u:U,t:tt}));}if(LAST&&(!LAST.u||!LAST.t||String(LAST.u).indexOf("undefined")>=0||LAST.u.replace(/\.html$/,"")===U))LAST=null;}catch(e){}
function ck(k){try{if(localStorage.getItem("usagi_owner")==="1")return;}catch(e){}try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
var css="#upan .nbk{flex:1;display:flex;min-height:0}"+
"#upan .nbt{width:54px;flex:none;display:flex;flex-direction:column;gap:6px;padding:14px 0 0 8px}"+
"#upan .nbt button{position:relative;flex:0 1 96px;min-height:64px;border:0;border-left:3px solid var(--c);border-radius:10px 0 0 10px;background:#F4F4F6;writing-mode:vertical-rl;font:700 12.5px 'Zen Kaku Gothic New',sans-serif;letter-spacing:.26em;color:#8a8079;cursor:pointer;padding:0;-webkit-tap-highlight-color:transparent}"+
"#upan .nbt button.on{background:#fff;color:#231E1B;box-shadow:-4px 0 12px -6px rgba(0,0,0,.2);z-index:2}"+
"#upan .nbt button.nw{border-left-style:dashed}#upan .nbt button i{position:absolute;top:7px;left:0;right:0;writing-mode:horizontal-tb;font:500 8px Jost,sans-serif;letter-spacing:.08em;color:var(--c);font-style:normal;text-align:center}#upan .nbt button.nw{padding-top:14px}"+
"#upan nav{position:relative;border-left:1px solid #E7E8EB;padding:20px 16px 96px 18px!important}"+
"#upan nav:before{content:'';position:absolute;left:-1px;top:0;bottom:0;width:3px;background:var(--c)}"+
"#upan .nen{font:300 9.5px Jost,sans-serif;letter-spacing:.34em;color:var(--c)}"+
"#upan .nh{font-family:'Shippori Mincho',serif;font-weight:600;font-size:21px;letter-spacing:.12em;color:#231E1B;margin:5px 0 3px}"+
"#upan .nl{font-size:11.5px;color:#7d756f;margin:0 0 14px}"+
"#upan .nlast{display:flex;align-items:center;gap:6px;margin:0 0 14px;padding:9px 11px;border-radius:10px;background:#F6F6F8;text-decoration:none;color:#3c3532;font-size:12px}#upan .nlast small{font-size:10.5px;color:#8a8079;flex:none}#upan .nlast b{font-weight:500;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}#upan .nlast span{color:#aaa}"+
"#upan a.nr{display:flex!important;align-items:center;gap:9px;padding:14px 2px!important;margin:0!important;height:auto!important;min-height:0;line-height:1.4;border-bottom:1px solid #EBECEF;text-decoration:none;color:#231E1B;-webkit-tap-highlight-color:transparent}#upan a.nr:first-of-type{border-top:1px solid #EBECEF}#upan a.nr:active{background:#F6F6F8}"+
"#upan a.nr .no{font:300 13px Jost,sans-serif;color:var(--c);width:19px;flex:none}"+
"#upan a.nr b{font-size:14.5px;font-weight:500;white-space:nowrap}"+
"#upan a.nr .ld{flex:1;min-width:6px;height:0;border-bottom:1px dotted #cfd3d9;align-self:center;margin-top:4px}"+
"#upan a.nr em{font-style:normal;font-size:10.5px;color:#7d756f;white-space:nowrap;flex:0 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis}"+
"#upan a.nr u{text-decoration:none;font:500 8.5px Jost,sans-serif;letter-spacing:.14em;color:#fff;background:var(--c);border-radius:3px;padding:1px 5px;margin-left:6px;vertical-align:2px}"+
"#upan .nsub{margin-top:16px;font-size:12px;line-height:2.2}#upan .nsub a{color:#3c3532;text-decoration:none;border-bottom:1px solid #E3E5E9;margin-right:14px;white-space:nowrap}"+
"#upan #umaprow{justify-content:flex-start!important;margin:14px 0 0!important}"+
"#upan .ush,#upan .us{display:none!important}"+
"#upan .nft{display:flex;align-items:center;gap:4px;padding:8px 84px calc(10px + env(safe-area-inset-bottom)) 14px;border-top:1px solid #EDEDED}"+
"#upan .nft small{white-space:nowrap;font-size:10.5px;color:#8a8079;margin:0 2px 0 4px;letter-spacing:.06em}#upan .nft .sp{flex:0 0 14px}"+
"#upan .nft a,#upan .nft button{width:40px;height:40px;display:grid;place-items:center;border:0;background:none;color:#5b524d;cursor:pointer;border-radius:50%;-webkit-tap-highlight-color:transparent;position:relative}"+
"#upan .nft a:active,#upan .nft button:active{background:#F1F1F3}#upan .nft svg{width:19px;height:19px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}"+
"#upan .nft button.ok:after{content:'コピーしました';position:absolute;bottom:42px;left:50%;transform:translateX(-50%);white-space:nowrap;font-size:10.5px;background:#231E1B;color:#fff;border-radius:6px;padding:3px 7px}"+
"#upan .uh .ux{position:absolute;right:16px;bottom:calc(14px + env(safe-area-inset-bottom));z-index:3;width:54px;height:54px;border-radius:50%;background:#fff;border:1px solid #DADDE2;box-shadow:0 4px 16px rgba(0,0,0,.10);font:300 26px Jost,sans-serif;color:#231E1B}"+
"html.night #upan .nbt button{background:#dde3ff;color:#6b6f86}html.night #upan .nbt button.on{background:#ebeeff;color:#231E1B}html.night #upan nav{border-left-color:#d4dbff}"+
"html.night #upan .nlast{background:#e1e6ff}html.night #upan a.nr,html.night #upan a.nr:first-of-type{border-color:#d9dfff}html.night #upan .nft{border-top-color:#d9dfff}html.night #upan .uh .ux{background:#ebeeff;border-color:#cfd6ff}";
var IG='<svg viewBox="0 0 24 24"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".6" fill="currentColor"/></svg>',
TH='<svg viewBox="0 0 24 24"><path d="M16.6 11.3c-.4-2.6-2.1-3.9-4.5-3.9-2.6 0-4.4 1.9-4.4 4.6 0 2.9 1.9 4.9 4.6 4.9 2.3 0 3.6-1.3 3.6-2.9 0-1.7-1.4-2.6-3.3-2.6-1.7 0-2.6.8-2.6 1.8 0 .9.8 1.5 1.8 1.5 2.2 0 3.3-1.9 3-5.6"/><path d="M19.5 8.2C18.4 5.1 15.7 3.5 12.2 3.5 7 3.5 3.8 7 3.8 12s3.2 8.5 8.4 8.5c3.4 0 5.9-1.5 7-4.1"/></svg>',
XL='<svg viewBox="0 0 24 24"><path d="M4 4l16 16M20 4L4 20" stroke-width="1.4"/></svg>',
SH='<svg viewBox="0 0 24 24"><path d="M12 15V3"/><path d="M7.5 7.5L12 3l4.5 4.5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg>',
LN='<svg viewBox="0 0 24 24"><path d="M12 4C7 4 3.5 7.1 3.5 10.9c0 3.4 2.8 6.2 6.7 6.8l-.4 2.6c-.1.5.4.8.8.5l3.9-3.2c4.3-.6 6-3.5 6-6.7C20.5 7.1 17 4 12 4z"/></svg>',
CP='<svg viewBox="0 0 24 24"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/></svg>';
function run(){
 var pan=document.getElementById("upan"),nav=pan&&pan.querySelector("nav");if(!nav||pan.querySelector(".nbk"))return;
 var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
 var bk=document.createElement("div");bk.className="nbk";var tb=document.createElement("div");tb.className="nbt";tb.setAttribute("role","tablist");tb.setAttribute("aria-label","ノート");
 nav.parentNode.insertBefore(bk,nav);bk.appendChild(tb);bk.appendChild(nav);
 var cur=HERE;
 function draw(){var n=NB.filter(function(x){return x.k===cur;})[0]||NB[0];
  tb.innerHTML=NB.map(function(x){return '<button type="button" role="tab" aria-selected="'+(x.k===n.k)+'" class="'+(x.k===n.k?"on":"")+(x.nw?" nw":"")+'" style="--c:'+x.c+'" data-t="'+x.k+'">'+(x.nw?"<i>NEW</i>":"")+esc(x.t)+'</button>';}).join("");
  nav.style.setProperty("--c",n.c);
  var h='<div class="nen">'+n.en+'</div><div class="nh">'+esc(n.t)+'ノート</div><div class="nl">'+esc(n.lead)+'</div>';
  if(LAST&&n.k===HERE)h+='<a class="nlast" href="'+esc(LAST.u)+'" data-n="つづき"><small>前回のつづき</small><b>'+esc(LAST.t)+'</b><span>→</span></a>';
  n.rows.forEach(function(r,i){var on=r[3].test(P);h+='<a class="nr" href="'+r[0]+'" data-n="'+esc(r[1])+'"'+(on?' aria-current="page"':'')+'><span class="no">0'+(i+1)+'</span><b>'+esc(r[1])+(on?'<u>NOW</u>':'')+'</b><span class="ld"></span><em>'+esc(r[2])+'</em></a>';});
  if(n.sub.length)h+='<div class="nsub">'+n.sub.map(function(s){var ex=/^https?:/.test(s[0]);return '<a href="'+s[0]+'" data-n="'+esc(s[1])+'"'+(ex?' target="_blank" rel="noopener"':'')+'>'+esc(s[1])+'</a>';}).join("")+'</div>';
  var mr=document.getElementById("umaprow");nav.innerHTML=h;if(mr&&n.k==="od")nav.appendChild(mr);nav.scrollTop=0;}
 draw();
 tb.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;cur=b.getAttribute("data-t");draw();ck("メニュー｜タブ "+b.textContent.replace("NEW",""));});
 nav.addEventListener("click",function(e){var a=e.target.closest("a");if(!a)return;ck("メニュー｜"+(a.getAttribute("data-n")||a.textContent));
  if(a.getAttribute("aria-current")==="page"){e.preventDefault();pan.querySelector(".ux").click();window.scrollTo({top:0,behavior:"smooth"});}});
 /* 地図アプリの切り替えは、おでかけのノートの下に（あとから足される） */
 var mt=0;(function w(){var mr=document.getElementById("umaprow");if(mr){if(cur!=="od")mr.remove();return;}if(++mt<60)setTimeout(w,100);})();
 /* 開くたびに、いま見ているノートから */
 try{new MutationObserver(function(){if(pan.classList.contains("on")&&cur!==HERE){cur=HERE;draw();}}).observe(pan,{attributes:true,attributeFilter:["class"]});}catch(e){}
 /* 下：送る（線のマーク）とSNS（ロゴ） */
 var ft=document.createElement("div");ft.className="nft";
 ft.innerHTML='<small>送る</small>'+(navigator.share?'<button type="button" data-s="share" aria-label="このページを送る">'+SH+'</button>':'')+'<button type="button" data-s="line" aria-label="LINEで送る">'+LN+'</button><button type="button" data-s="copy" aria-label="URLをコピー">'+CP+'</button><span class="sp"></span>'+
  '<a href="https://www.instagram.com/'+A.ig+'/" target="_blank" rel="noopener" aria-label="Instagram">'+IG+'</a><a href="https://www.threads.com/@'+A.ig+'" target="_blank" rel="noopener" aria-label="Threads">'+TH+'</a><a href="https://x.com/'+A.x+'" target="_blank" rel="noopener" aria-label="X">'+XL+'</a>';
 pan.appendChild(ft);
 ft.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;var k=b.getAttribute("data-s"),u=location.origin+location.pathname,t=document.title;ck("メニュー｜送る（"+k+"）");
  if(k==="share"){navigator.share({title:t,url:u}).catch(function(){});return;}
  if(k==="line"){location.href="https://line.me/R/share?text="+encodeURIComponent(t+"\n"+u);return;}
  var done=function(){b.classList.add("ok");setTimeout(function(){b.classList.remove("ok");},1800);};
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(u).then(done,function(){prompt("このURLをコピーしてください",u);});else prompt("このURLをコピーしてください",u);});
}
var n=0;(function t(){run();if(!document.querySelector("#upan .nbk")&&++n<50)setTimeout(t,100);})();
})();

/* 11/10 オーナー「見やすさと操作性と技術で勝負」→ 押す前にページを先に取っておく（押したらすぐ開く）。
   ページの中身を先に「動かす」のではなく「取っておく」だけ（数える仕組みに影響しない）。Chrome は指を近づけた時、iPhone は触れた瞬間に。 */
(function(){try{
 if(HTMLScriptElement.supports&&HTMLScriptElement.supports("speculationrules")){var s=document.createElement("script");s.type="speculationrules";
  s.textContent=JSON.stringify({prefetch:[{where:{and:[{href_matches:"/*"},{not:{href_matches:"/c*"}},{not:{href_matches:"/moushikomi*"}}]},eagerness:"moderate"}]});document.head.appendChild(s);return;}
 var done={};function pf(e){var a=e.target.closest&&e.target.closest("a[href]");if(!a||a.origin!==location.origin||a.target==="_blank")return;var u=a.pathname+a.search;if(done[u]||u===location.pathname||/^\/(c|moushikomi)/.test(u))return;done[u]=1;var l=document.createElement("link");l.rel="prefetch";l.href=u;document.head.appendChild(l);}
 document.addEventListener("touchstart",pf,{passive:true,capture:true});document.addEventListener("mouseover",pf,{passive:true,capture:true});
}catch(e){}})();

/* 11/10 オーナー・夜 #170「メニューを閉じてすぐ別の項目を押すと、閉じかけのメニューと暗い背景が次の画面に一瞬残る」→ ページを移る時と、戻ってきた時は、メニューを動きなしで閉じきる */
(function(){try{
var ss=document.createElement("style");ss.textContent="html.umenu-go #umask,html.umenu-go #upan{transition:none!important}";document.head.appendChild(ss);
function shut(){var d=document.documentElement;d.classList.add("umenu-go");d.classList.remove("umenu-open");var m=document.getElementById("umask"),p=document.getElementById("upan");if(m)m.classList.remove("on");if(p){p.classList.remove("on");p.setAttribute("aria-hidden","true");}}
function back(){document.documentElement.classList.remove("umenu-go");}
document.addEventListener("click",function(e){if(e.defaultPrevented)return;var a=e.target.closest&&e.target.closest("a[href]");if(!a||a.target==="_blank"||a.origin!==location.origin)return;if(a.pathname===location.pathname&&a.search===location.search)return;shut();},false);
addEventListener("pagehide",shut);
addEventListener("pageshow",function(e){shut();requestAnimationFrame(function(){requestAnimationFrame(back)});});
}catch(e){}})();
