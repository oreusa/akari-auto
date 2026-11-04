/* 10/31 オーナー「燈のも見して」：月の見本（usagi links/assets/v2.js）と同じ形を燈のカードに合わせたもの。見本ページだけで読む */
(function(){
var T=new Date(Date.now()+9*36e5).toISOString().slice(0,10),WD=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
function fd(s){var d=new Date(s+"T00:00:00Z");return (d.getUTCMonth()+1)+"."+String(d.getUTCDate()).padStart(2,"0")+" "+WD[d.getUTCDay()];}
function deco(){document.querySelectorAll("#odekake .card.it").forEach(function(c){
  if(c.querySelector(".v2c"))return;var d=c.querySelector(".d");if(!d)return;
  var pref=c.dataset.pref||"",s=c.dataset.s,e=c.dataset.e,free=c.dataset.free==="1";
  var st=s&&s>T?"これから":(e?"開催中":"");
  var h='';if(pref)h+='<span class="p" data-p="'+pref+'">'+pref+'</span>';if(st)h+='<span'+(st==="開催中"?' class="on"':'')+'>'+st+'</span>';if(free)h+='<span class="f">無料</span>';
  var cx=document.createElement("div");cx.className="v2c";cx.innerHTML=h;
  var w=d.querySelector(".when");
  var dt=document.createElement("div");dt.className="v2d";
  dt.textContent=s&&s>T?fd(s)+(e&&e!==s?" — "+fd(e):""):(e?fd(e)+" まで":(w?w.textContent:""));
  c.insertBefore(dt,c.firstChild);c.insertBefore(cx,dt);
});}
deco();
document.addEventListener("click",function(ev){var p=ev.target.closest&&ev.target.closest(".v2c span.p");if(!p)return;ev.preventDefault();ev.stopPropagation();
  var b=[].find.call(document.querySelectorAll(".flt[data-v=odekake] button"),function(x){return x.dataset.p===p.dataset.p});if(b){b.click();var f=b.parentNode;scrollTo({top:f.getBoundingClientRect().top+scrollY-70,behavior:"smooth"});}},true);
/* 近くの宿：カードの中、地図の右へ */
function mvYk(){document.querySelectorAll(".yk").forEach(function(y){var c=y.previousElementSibling;if(c&&c.classList.contains("it")&&!c.contains(y)){var r=c.querySelector(".mpr")||c;r.appendChild(y);}});}
mvYk();new MutationObserver(function(){mvYk();deco();}).observe(document.getElementById("odekake")||document.body,{childList:true,subtree:true});
/* 11/1 月と同じ並び：件数→「イベント｜新しいお店・施設」→4つのタブ→都県→地図で見る→カード */
(function(){var ot=document.querySelector("#odekake .otab"),fl=document.querySelector('.wrap>nav.flt[data-v="odekake"]'),cn=document.querySelector('.wrap>p.cnt[data-v="odekake"]');
  if(!ot||!fl)return;var w=document.createElement("div");w.className="v2tabs";w.setAttribute("data-v","odekake");
  w.innerHTML='<div class="tgrp"><span>'+(ot.dataset.g1||"イベント")+'</span><span>'+(ot.dataset.g2||"新しいお店・施設")+'</span></div>';w.appendChild(ot);
  fl.parentNode.insertBefore(w,fl);if(cn)fl.parentNode.insertBefore(cn,w);})();
var tabs=document.querySelector(".v2tabs .otab")||document.querySelector("#odekake .otab");
var I={now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>',up:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',inn:'<svg viewBox="0 0 24 24"><path d="M4 11l8-6 8 6v9H4z"/><path d="M10 20v-5h4v5"/></svg>'};
var bar=document.createElement("nav");bar.id="v2bar";bar.setAttribute("aria-label","すぐ移動");
/* 11/2 くらべたおかいものリスト：下のボタン列は買い物の4つのタブ＋MENU */
var OK=document.body.dataset.bar==="okai";
I.pick='<svg viewBox="0 0 24 24"><path d="M5 7h14l-1.5 9h-11z"/><circle cx="9" cy="19.5" r="1.2"/><circle cx="16" cy="19.5" r="1.2"/></svg>';
I.unit='<svg viewBox="0 0 24 24"><path d="M12 4v16M6 8h12M6 8l-3 6h6zM18 8l-3 6h6z"/></svg>';
I.down='<svg viewBox="0 0 24 24"><path d="M4 6l6 6 4-4 6 6"/><path d="M20 10v4h-4"/></svg>';
I.sale='<svg viewBox="0 0 24 24"><path d="M3 12l9-9h7v7l-9 9z"/><circle cx="15" cy="9" r="1.4"/></svg>';
if(OK){var tb=tabs?[].slice.call(tabs.querySelectorAll("button")):[];
  bar.innerHTML=tb.map(function(b,i){var t=b.dataset.t,l=b.childNodes[1]?b.childNodes[1].textContent:"";return '<button data-t="'+t+'"'+(b.classList.contains("on")?' class="cur"':'')+'>'+(I[t]||"")+'<span>'+l+'</span></button>';}).join("")+'<button class="mn" data-a="menu"><i></i>MENU</button>';}
else bar.innerHTML='<button data-t="now" class="cur">'+I.now+'<span>開催中</span></button><button data-t="up">'+I.up+'<span>これから</span></button><button data-a="map">'+I.map+'<span>地図</span></button><button data-a="inn">'+I.inn+'<span>泊まり</span></button><button class="mn" data-a="menu"><i></i>MENU</button>';
document.body.appendChild(bar);
function syncBar(){var on=tabs&&tabs.querySelector("button.on");bar.querySelectorAll("button[data-t]").forEach(function(b){b.classList.toggle("cur",!!on&&b.dataset.t===on.dataset.t)});}
bar.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;
  if(b.dataset.t){var cat=document.querySelector('#cats button[data-v=odekake]');if(cat&&!cat.classList.contains("on"))cat.click();
    var t=tabs&&tabs.querySelector('button[data-t="'+b.dataset.t+'"]');if(t)t.click();syncBar();var o=document.getElementById("odekake");if(o)scrollTo({top:o.getBoundingClientRect().top+scrollY-10,behavior:"smooth"});}
  else if(b.dataset.a==="map"){var m=document.querySelector(".tnbtn");if(m)m.click();}
  else if(b.dataset.a==="inn")location.href="/tomari";
  else{var u=document.getElementById("umenu");if(u)u.click();}});
bar.classList.add("on");document.documentElement.classList.add("v2bar-on");
if(tabs)tabs.addEventListener("click",function(){setTimeout(syncBar,30)});
/* 11/2 ほかのページの下のボタン（/odekake?v2t=0・1・map）から来たら、そのタブ・地図を開く */
(function(){var q=null;try{q=new URLSearchParams(location.search).get("v2t");}catch(e){}if(q===null)return;
  try{var u=new URLSearchParams(location.search);u.delete("v2t");history.replaceState(null,"",location.pathname+(u.toString()?"?"+u:"")+location.hash);}catch(e){}
  setTimeout(function(){if(q==="map"){var n=0;(function t(){var m=document.querySelector(".tnbtn");if(m){m.click();return;}if(++n<40)setTimeout(t,100);})();return;}
    var b=bar.querySelector('button[data-t="'+(q==="1"?"up":"now")+'"]');if(b)b.click();},120);})();
})();

/* 11/4 カードの日付と絵（cardmark.js。月と同じ）を読み込む */
(function(){if(document.querySelector('script[src*="cardmark.js"]'))return;var s=document.createElement("script");s.src="/assets/cardmark.js?v=3";s.defer=true;document.head.appendChild(s);})();
