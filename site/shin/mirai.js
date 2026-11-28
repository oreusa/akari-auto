/* 11/27 owner「おれが好きな近未来のオシャレ・本気で考えろ」→ 見本 ?mihon=3（この端末で覚える・?mihon=0 で外す）。
   普通の役目＋こだわり1つ（[[yakume-alpha-1119]]）。動かすのは transform と opacity だけ。関西・関東は同じファイル（akari site/shin/ に写す）。
   1 上の島：今いちばん大事な1件（締め切り）だけを iPhone の島の形で。押すと広がる。
   2 カードが開いて次のページになる：押した写真が次のページの一番上の写真へ伸びる（ブラウザの View Transitions。無い端末はふつうに開く）。
   3 押した瞬間に開く：指が触れたら次のページを先に読む（Speculation Rules の prefetch＝JS は動かさない＝数える仕組みは数えない）。 */
(function(){
"use strict";
if(window.__mirai)return;window.__mirai=1;
var D=document,H=D.documentElement;H.classList.add("mr");
var KANTO=/kanto|lifenote|life-note|usagi-life/.test(location.hostname)||/[?&]reg=kanto/.test(location.search);

/* ---------- 2 カードが開く動き ---------- */
/* @view-transition は shin.js・skin.js の読み込み口で先に入れる */
function big(img){var r=img.getBoundingClientRect();return r.width>=120&&r.height>=80}
D.addEventListener("click",function(e){
  var a=e.target.closest&&e.target.closest("a[href]");if(!a||a.target==="_blank"||a.host!==location.host||a.getAttribute("href").charAt(0)==="#")return;
  var im=a.querySelector("img");if(!im||!big(im))return;
  try{sessionStorage.setItem("mr_vt",im.currentSrc||im.src)}catch(x){}
  im.style.viewTransitionName="mrhero";
},true);
/* 戻ってきた時に名前が残ると次の動きがおかしくなる */
window.addEventListener("pageshow",function(){var x=D.querySelectorAll("img");for(var i=0;i<x.length;i++)if(x[i].style.viewTransitionName)x[i].style.viewTransitionName=""});
/* pagereveal（来たページの写真に名前を付ける）は shin.js・skin.js の読み込み口にある（ここでは間に合わない） */

/* ---------- 3 押した瞬間に開く ---------- */
try{
  if(HTMLScriptElement.supports&&HTMLScriptElement.supports("speculationrules")){
    var sr=D.createElement("script");sr.type="speculationrules";
    sr.textContent=JSON.stringify({prefetch:[{where:{and:[{href_matches:"/*"},{not:{selector_matches:"[target=_blank],[rel~=nofollow]"}}]},eagerness:"moderate"}]});
    D.head.appendChild(sr);
  }else{
    /* Safari：指が触れた所で先に取りに行く（同じアドレスは1回だけ） */
    var got={};D.addEventListener("touchstart",function(e){
      var a=e.target.closest&&e.target.closest("a[href]");if(!a||a.host!==location.host||a.target==="_blank")return;
      var u=a.href.split("#")[0];if(got[u]||u===location.href.split("#")[0])return;got[u]=1;
      try{fetch(u,{credentials:"same-origin",priority:"high"}).catch(function(){})}catch(x){}
    },{passive:true,capture:true});
  }
}catch(x){}

/* ---------- 1 上の島 ---------- */
/* 締め切りの正本は公式ページ（tools/fudosan_list/towns.py J_CITY・tools/kaitai/kanto_hojo.tsv）。見本なので今はここに手で。本番にする時は毎朝の機械で作る */
var ITEMS=KANTO?[
  {d:"2026-11-30",t:"平塚市の解体の補助",s:"建て替えで古い木造住宅を解体する時、解体費の1/3・上限36万円。受付は11月末までの予定です。",u:"/kaitai-hiratsuka",b:"くわしく見る"}
]:[
  {d:"2026-11-30",t:"西宮市の解体の補助",s:"耐震の足りない住宅の解体の補助。受付は11月30日まで（先着順）です。",u:"/kaitai-nishinomiya",b:"くわしく見る"},
  {d:"2026-11-30",t:"大東市の解体の補助",s:"古く危ない空き家の解体に、解体費の4/5・戸建は上限80万円。事前調査の受付は11月30日までです。",u:"/kaitai-daito",b:"くわしく見る"}
];
/* 11/27 owner「お出かけになんの関係あるの？」：島はそのページの分野の物だけ。家と土地のページ＝締め切り、おでかけのページ＝今から行ける、ほかのページは出さない */
var PATH=location.pathname.replace(/\.html$/,"").replace(/^\/shin/,"");
var IE=/^\/(kaitai|jikka|ie|chika|akiya|uru|sagasu|machi|moushikomi|koe|otoku|gyosha|souba)/.test(PATH),
    ODE=/^\/(odekake|tomari|koyo|illumination|hatsumode|christmas|toshikoshi|o\/)/.test(PATH);
var FALL={t:"いまから行けるおでかけ",s:"今日これから行けるおでかけを、近い順に出します。",u:"/ima",b:"近い順に見る",lab:"近い順"};
function jst(){var n=new Date(Date.now()+9*3600e3);return Date.UTC(n.getUTCFullYear(),n.getUTCMonth(),n.getUTCDate())}
function pick(){if(ODE)return FALL;if(!IE)return null;var t=jst(),best=null;
  for(var i=0;i<ITEMS.length;i++){var p=ITEMS[i].d.split("-"),dd=Math.round((Date.UTC(+p[0],p[1]-1,+p[2])-t)/864e5);
    if(dd<0)continue;if(!best||dd<best.n){best=ITEMS[i];best.n=dd}}
  if(best&&location.pathname.replace(/\.html$/,"").replace(/^\/shin/,"")===best.u)return null;
  return best||null}
function island(){
  if(D.getElementById("mrisl"))return;var it=pick();if(!it)return;
  var css=D.createElement("style");css.textContent=
  "#mrisl{position:fixed;left:50%;bottom:var(--mrb,calc(env(safe-area-inset-bottom,0px) + 96px));z-index:9000;transform:translateX(-50%);"+
  "max-width:min(84vw,340px);background:#000;color:#fff;border-radius:22px;border:1px solid rgba(255,255,255,.14);box-shadow:0 6px 24px rgba(0,0,0,.18);overflow:hidden;"+
  "font:500 13px/1.35 -apple-system,BlinkMacSystemFont,'Hiragino Sans','Noto Sans JP',sans-serif;letter-spacing:.01em;"+
  "transition:border-radius .38s cubic-bezier(.2,.8,.2,1);-webkit-tap-highlight-color:transparent}"+
  "#mrisl button.mrp{all:unset;display:flex;align-items:center;gap:8px;padding:8px 14px 8px 12px;cursor:pointer;min-height:20px;white-space:nowrap}"+
  "#mrisl .mrd{width:7px;height:7px;border-radius:50%;background:#30D158;flex:none;animation:mrb 2.4s ease-in-out infinite}"+
  "#mrisl .mrn{color:#FFD60A;font-weight:600}"+
  "#mrisl .mrx{display:grid;grid-template-rows:0fr;transition:grid-template-rows .38s cubic-bezier(.2,.8,.2,1)}"+
  "#mrisl .mrx>div{overflow:hidden;opacity:0;transform:translateY(-6px);transition:opacity .28s,transform .38s cubic-bezier(.2,.8,.2,1)}"+
  "#mrisl.op{border-radius:26px}#mrisl.op .mrx{grid-template-rows:1fr}#mrisl.op .mrx>div{opacity:1;transform:none}"+
  "#mrisl .mrx p{margin:0;padding:0 14px 8px;color:rgba(255,255,255,.78);font-weight:400;font-size:12.5px;line-height:1.5;white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}"+
  "#mrisl .mrx a{display:block;margin:0 10px 10px;padding:8px 0;text-align:center;border-radius:12px;background:#fff;color:#000;font-weight:600;text-decoration:none;font-size:13px}"+
  "#mrisl.hid{opacity:0;transform:translate(-50%,12px);pointer-events:none}#mrisl{transition:opacity .3s,transform .3s,border-radius .38s cubic-bezier(.2,.8,.2,1)}"+
  "@keyframes mrb{50%{opacity:.35}}@media (prefers-reduced-motion:reduce){#mrisl,#mrisl *{animation:none!important;transition:none!important}}";
  D.head.appendChild(css);
  var n=it.lab||(it.n===0?"きょうまで":"あと"+it.n+"日"),w=D.createElement("div");w.id="mrisl";w.setAttribute("role","region");w.setAttribute("aria-label","お知らせ");
  w.innerHTML='<button class="mrp" type="button" aria-expanded="false"><i class="mrd"'+(it.lab?' style="background:#64D2FF"':'')+'></i><span>'+it.t+'</span><span class="mrn">'+n+'</span></button>'+
    '<div class="mrx"><div><p>'+it.s+'</p><a href="'+it.u+'">'+it.b+'</a></div></div>';
  D.body.appendChild(w);
  /* 下のバーのすぐ上に浮かべる（バーの高さは端末で違うので測る） */
  function seat(){var e=D.elementFromPoint(innerWidth/2,innerHeight-24),f=null;while(e&&e!==D.body){if(getComputedStyle(e).position==="fixed")f=e;e=e.parentElement}
    if(f&&f!==w){var r=f.getBoundingClientRect();if(r.top>innerHeight*.6)w.style.setProperty("--mrb",(innerHeight-r.top+10)+"px")}}
  setTimeout(seat,300);addEventListener("resize",seat);
  var bt=w.querySelector(".mrp");
  /* 11/27 owner のスクショ：広げた島が一覧を隠した → 小さくし、6秒で自動で閉じる・下へ流しても閉じる */
  var ac=0;function shut(){w.classList.remove("op");bt.setAttribute("aria-expanded","false")}
  bt.addEventListener("click",function(){var o=w.classList.toggle("op");bt.setAttribute("aria-expanded",o?"true":"false");clearTimeout(ac);if(o)ac=setTimeout(shut,6000)});
  D.addEventListener("click",function(e){if(!w.contains(e.target)&&w.classList.contains("op")){w.classList.remove("op");bt.setAttribute("aria-expanded","false")}});
  /* 読んでいる間はじゃまをしない：下へ流す間は隠れて、止まったら戻る */
  var tm=0,ly=scrollY;addEventListener("scroll",function(){if(w.classList.contains("op")){if(Math.abs(scrollY-ly)>40){shut();ly=scrollY}return}var y=scrollY;if(y>ly+4&&y>80)w.classList.add("hid");ly=y;clearTimeout(tm);tm=setTimeout(function(){w.classList.remove("hid")},700)},{passive:true});
}
if(D.body)island();else D.addEventListener("DOMContentLoaded",island);
})();
