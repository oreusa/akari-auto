/* 11/19 owner「他ページもぜんぶ変えれたら」→ 新しい土台で作り直していないページ（街・実家・解体・地価・売る・申し込み・おでかけ1件 …）に、
   新しい土台と同じ 頭（ロゴ・昼夜スイッチ）・大きい題が上の帯に収まる動き・下のバー＋MENU・本物の夜空 をかぶせる。
   読み込みは functions/_middleware.js が <head> に入れる（html.sk）。見た目は skin.css（build.py が shin.css から作る＋skin.tail.css）。 */
(function(){
"use strict";
if(window.__sk)return;window.__sk=1;
/* 11/19 owner「文字列おかしい」：日本語の見出し・文を意味の切れ目でだけ折り返す（BudouX） */
(function(){var s=document.createElement("script");s.src="/shin/bx.js?v=1";s.defer=true;document.head.appendChild(s)})();
var H=document.documentElement,P=location.pathname,RM=matchMedia("(prefers-reduced-motion:reduce)").matches;
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
var IC={now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',
 we:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',
 map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',
 inn:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>',
 find:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/></svg>',
 rank:'<svg viewBox="0 0 24 24"><path d="M5 20V11M12 20V5M19 20v-6"/></svg>',
 sell:'<svg viewBox="0 0 24 24"><path d="M3 12l9-8 9 8"/><path d="M6 10v10h12V10"/><path d="M10 15h4"/></svg>',
 yen:'<svg viewBox="0 0 24 24"><path d="M6 4l6 8 6-8M12 12v8M8 13h8M8 16.5h8"/></svg>',
 down:'<svg viewBox="0 0 24 24"><path d="M4 6l6 6 4-4 6 7"/><path d="M15 15h5v-5"/></svg>',
 buy:'<svg viewBox="0 0 24 24"><path d="M4 7h16l-1.5 11.5a2 2 0 0 1-2 1.5H7.5a2 2 0 0 1-2-1.5z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg>'};
/* ページの分野ごとの下のバーと MENU（11/19 owner「MENU はそのページの分野だけ」） */
var FUD={nav:[["街をさがす","find","/fudosan-list"],["ランキング","rank","/ranking"],["売りたい","sell","/uru"],["いくら？","yen","/ikura"]],
  k:"Home & Land",menu:[["家と土地の相場","/fudosan-list"],["家を売る前に","/uru"],["いくらで売れる？","/ikura"],["実家・空き家","/jikka/"],["解体の費用と補助金","/kaitai"],["地価ランキング","/chika-kansai"],["まちランキング","/ranking"]],
  rel:[["おでかけ","/odekake"],["おかいもの","/okaimono"],["トップへ","/"]]};
var ODE={nav:[["開催中","now","/odekake"],["今週末","we","/odekake?w=we"],["いまから","map","/ima"],["泊まり","inn","/tomari"]],
  k:"Odekake",menu:[["関西おでかけ","/odekake"],["イルミネーション","/illumination"],["紅葉","/koyo"],["いまから行ける","/ima"],["泊まり","/tomari"],["初詣","/hatsumode"]],
  rel:[["家と土地","/fudosan-list"],["おかいもの","/okaimono"],["トップへ","/"]]};
var KAI={nav:[["これから","now","/kaiten?w=soon"],["開いた","we","/kaiten?w=done"],["閉まる","down","/kaiten?w=close"],["おでかけ","map","/odekake"]],
  k:"New Shops",menu:[["関西の開店・閉店","/kaiten"],["関東の開店・閉店","https://kanto.townnote.app/kaiten"]],rel:[["おでかけ","/odekake"],["家と土地","/fudosan-list"],["トップへ","/"]]};
var TOP={nav:[["おでかけ","now","/odekake"],["家と土地","find","/fudosan-list"],["おかいもの","yen","/okaimono"],["開店閉店","buy","/kaiten"]],
  k:"Town Note",menu:[["トップ","/"],["関西のおでかけ","/odekake"],["家と土地の相場","/fudosan-list"],["日用品の値段くらべ","/okaimono"],["開店・閉店","/kaiten"]],rel:[]};
/* 関東（kanto.townnote.app）も同じ物を読む。関東にあるページだけを出す */
var KT=/kanto|lifenote|life-note|usagi-life/.test(location.hostname);
if(KT){FUD.nav[1]=["地価","rank","/chika-kanto"];FUD.menu=[["家と土地の相場","/fudosan-list"],["家を売る前に","/uru"],["いくらで売れる？","/ikura"],["実家・空き家","/jikka/"],["解体の費用と補助金","/kaitai"],["地価ランキング","/chika-kanto"]];
  ODE.nav=[["おでかけ","now","/odekake"],["いまから","map","/ima"],["紅葉","we","/koyo"],["開店閉店","buy","/kaiten"]];ODE.menu=[["関東おでかけ","/odekake"],["いまから行ける","/ima"],["紅葉","/koyo"],["開店・閉店","/kaiten"]];
  KAI.menu=[["関東の開店・閉店","/kaiten"],["関西の開店・閉店","https://kansai.townnote.app/kaiten"]];}
var BR=KT?"LIFE NOTE":"TOWN NOTE",LG=KT?["/logo-s.png","/logo-s-night.png"]:["/assets/logo-s.png?v=2","/assets/logo-s-night.png"];
var OKA={nav:[["品物","find","/okaimono"],["値下がり","down","/nesage"],["お得","yen","/otoku"],["ふるさと納税","buy","/furusato"]],
  k:"Shopping",menu:[["日用品の値段くらべ","/okaimono"],["値下がりした物","/nesage"],["お得な物","/otoku"],["ふるさと納税","/furusato"]],rel:[["おでかけ","/odekake"],["家と土地","/fudosan-list"],["トップへ","/"]]};
var C=/^\/(okaimono|nesage|otoku|furusato|kaimawari|tanka)/.test(P)?OKA:/^\/(o|odekake|illumination|koyo|ima|tomari|hatsumode)\b/.test(P)?ODE:/^\/kaiten/.test(P)?KAI:/^\/(machi|jikka|kaitai|chika|uru|ikura|moushikomi|gyosha|sagasu|shindan|akiya|fudosan|koe|ranking|townnotes)/.test(P)?FUD:TOP;
var here=function(u){return u.split("?")[0]===P.replace(/\.html$/,"")};

function build(){
  if(H.classList.contains("night"))H.classList.add("nt");
  var n=H.classList.contains("nt");
  var top=document.createElement("div");top.className="skc";
  top.innerHTML='<div class="wrap"><header class="top"><a class="brand" href="/" aria-label="トップへ"><img id="logo" src="'+(n?LG[1]:LG[0])+'" alt="'+BR+'"><b>'+BR+'</b></a>'+
   '<button class="tg" id="tg" role="switch" aria-checked="'+n+'" aria-label="夜の画面にする"><i class="kn"></i><span class="su"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path class="sp" d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/></svg></span><span class="mo"><svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg></span></button></header></div>';
  document.body.insertBefore(top,document.body.firstChild);
  var sk=document.createElement("div");sk.className="skc";sk.id="sk";
  sk.innerHTML='<div id="sky" aria-hidden="true"><canvas id="stars"></canvas></div>'+
   '<nav class="nav" id="nav" aria-label="すぐ移動">'+C.nav.map(function(x){return '<a href="'+x[2]+'"'+(here(x[2])?' class="cur"':'')+'>'+IC[x[1]]+'<span>'+x[0]+'</span></a>'}).join("")+'<button class="mn" id="mnb" aria-label="メニュー"><em></em><span>MENU</span></button></nav>'+
   '<div class="mu" id="mu"><div class="bk"></div><div class="pn"><div class="k">'+C.k+'</div><ol>'+C.menu.map(function(m,i){return '<li><a href="'+m[1]+'"'+(here(m[1])?' class="here"':'')+' style="transition-delay:'+(60+i*40)+'ms"><small>0'+(i+1)+'</small>'+m[0]+'</a></li>'}).join("")+
   '</ol><div class="rel">'+C.rel.map(function(r){return '<a href="'+r[1]+'">'+r[0]+'</a>'}).join("")+'</div></div></div>';
  document.body.appendChild(sk);
  /* 下のバー：下へ流す間だけ隠れ、止めたら戻る */
  var nav=$("#nav"),ly=scrollY,nvT;
  addEventListener("scroll",function(){var y=scrollY;if(Math.abs(y-ly)>8){nav.classList.toggle("hide",y>ly&&y>300);ly=y}clearTimeout(nvT);nvT=setTimeout(function(){nav.classList.remove("hide")},800)},{passive:true});
  nav.addEventListener("pointerdown",function(e){var b=e.target.closest("a,button");if(!b)return;b.classList.remove("tap");void b.offsetWidth;b.classList.add("tap")});
  var mu=$("#mu");$("#mnb").onclick=function(){mu.classList.add("op")};$(".bk",mu).onclick=function(){mu.classList.remove("op")};
  /* 大きい題 → 上の細い帯 */
  var h=$(".head h1,.s3h h1,.wrap h1");if(h){var tb=document.createElement("button");tb.id="tb";tb.className="sk-tb";tb.setAttribute("aria-label","一番上へ");
    tb.textContent=(h.childNodes[0]&&h.childNodes[0].nodeType===3?h.childNodes[0].textContent:h.textContent).trim();sk.appendChild(tb);
    tb.onclick=function(){scrollTo({top:0,behavior:RM?"auto":"smooth"})};var q=0,on=false;
    var f=function(){q=0;var r=h.getBoundingClientRect(),o=r.bottom<46;if(o!==on){on=o;tb.classList.toggle("on",o);H.classList.toggle("tbon",o)}};
    addEventListener("scroll",function(){if(!q)q=requestAnimationFrame(f)},{passive:true});f()}
  /* 昼夜：今までの夜（night.js）と新しい夜空を一緒に切り替える */
  $("#tg").addEventListener("click",function(){var n=!H.classList.contains("nt");
    var go=function(){H.classList.toggle("nt",n);try{if(window.usagiTheme)usagiTheme.set(n?"night":"day");else{H.classList.toggle("night",n);localStorage.setItem("usagi_theme",n?"night":"day")}}catch(e){}
      $("#logo").src=n?LG[1]:LG[0];$("#tg").setAttribute("aria-checked",n?"true":"false");var m=$('meta[name="theme-color"]');if(m)m.content=n?"#0A0E18":"#FFFFFF";if(n){stars();shoot()}};
    if(!document.startViewTransition||RM){go();return}
    var kr=$("#tg .kn").getBoundingClientRect(),x=kr.left+kr.width/2+(n?34:-34),y=kr.top+kr.height/2,r=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y));H.classList.add("vtt");
    var t=document.startViewTransition(go);t.ready.then(function(){H.animate({clipPath:["circle(0px at "+x+"px "+y+"px)","circle("+r+"px at "+x+"px "+y+"px)"]},{duration:760,easing:"cubic-bezier(.4,0,.2,1)",pseudoElement:"::view-transition-new(root)"})});
    t.finished.then(function(){H.classList.remove("vtt")})});
  if(n){stars();shoot()}
  addEventListener("resize",function(){if(H.classList.contains("nt"))stars()});
}
/* 本物の空の決まりの夜空（shin.js と同じ・画面に貼り付く1枚） */
var SC=["255,255,255","255,255,255","255,255,255","235,242,255","210,225,255","255,246,228","255,232,200","255,214,170"],drawn="",seed=+new Date(Date.now()+9*36e5).toISOString().slice(0,10).replace(/-/g,"");
function stars(){var cv=$("#stars");if(!cv)return;var w=innerWidth,h=screen.height>innerHeight?Math.max(innerHeight,screen.height):innerHeight,dp=Math.min(2,devicePixelRatio||1);if(drawn===w+"x"+h)return;drawn=w+"x"+h;
  cv.width=w*dp;cv.height=h*dp;cv.style.height=h+"px";var c=cv.getContext("2d");c.scale(dp,dp);var r=seed,x,y,bb,rr,g,m;
  function rnd(){r=(r*16807)%2147483647;return r/2147483647}
  function band(y,x){return Math.exp(-Math.pow((x*.62-y+y*.5+w*.15)/(w*.32),2))}
  for(m=0;m<26;m++){x=rnd()*w;y=rnd()*h;bb=band(y,x);if(bb<.25)continue;rr=40+rnd()*110;g=c.createRadialGradient(x,y,0,x,y,rr);g.addColorStop(0,"rgba(190,200,235,"+(.035*bb).toFixed(3)+")");g.addColorStop(1,"rgba(190,200,235,0)");c.fillStyle=g;c.fillRect(x-rr,y-rr,rr*2,rr*2)}
  var n=Math.round(w*h/520);
  for(var i=0;i<n;i++){x=rnd()*w;y=rnd()*h;bb=band(y,x);if(rnd()>.35+bb*.65)continue;
    var mag=Math.pow(rnd(),3.2),sz=.22+mag*1.25,a=.18+mag*.8+rnd()*.12,col=SC[(rnd()*SC.length)|0];
    c.fillStyle="rgba("+col+","+Math.min(1,a).toFixed(3)+")";c.beginPath();c.arc(x,y,sz,0,7);c.fill();
    if(mag>.82){g=c.createRadialGradient(x,y,0,x,y,sz*6);g.addColorStop(0,"rgba("+col+",.28)");g.addColorStop(1,"rgba("+col+",0)");c.fillStyle=g;c.fillRect(x-sz*6,y-sz*6,sz*12,sz*12)}}
  $$("#sky .tw").forEach(function(e){e.parentNode.removeChild(e)});var sky=$("#sky");r=seed+7;
  for(i=0;i<Math.round(w*h/9000);i++){var e=document.createElement("i");e.className="tw";var big=rnd()>.8;
    e.style.cssText="left:"+(rnd()*w).toFixed(1)+"px;top:"+(rnd()*h).toFixed(1)+"px;--s:"+(big?2.4:1.5)+"px;--c:rgb("+SC[(rnd()*SC.length)|0]+");animation-duration:"+(2.5+rnd()*4).toFixed(2)+"s;animation-delay:-"+(rnd()*6).toFixed(2)+"s";sky.appendChild(e)}}
var shootT;function shoot(){clearTimeout(shootT);if(!H.classList.contains("nt")||RM)return;
  shootT=setTimeout(function(){var s=document.createElement("i"),big=Math.random()<.15,ang=18+Math.random()*34,len=big?220:110+Math.random()*90,dur=big?1.1:.5+Math.random()*.4;
    s.className="shoot"+(big?" big":"");s.style.cssText="left:"+(innerWidth*(.3+Math.random()*.75)).toFixed(0)+"px;top:"+(20+Math.random()*innerHeight*.45).toFixed(0)+"px;--a:"+ang.toFixed(1)+"deg;--l:"+len.toFixed(0)+"px;--d:"+(len*1.6).toFixed(0)+"px;animation-duration:"+dur.toFixed(2)+"s";
    $("#sky").appendChild(s);setTimeout(function(){if(s.parentNode)s.parentNode.removeChild(s)},dur*1000+200);shoot()},(6+Math.random()*16)*1e3)}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",build);else build();
})();
