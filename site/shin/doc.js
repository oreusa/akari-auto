/* 新しいHP：読む・入れるページ（売る前に・いくら？・実家 など）。11/19 owner「その他も本気でやり直せ」。
   前のページに頭をかぶせるのをやめ、中身をこの土台の部品（.dc）で書き直した。
   D = {h1, sub, html, js?, towns?}。html は tools/shin/docs.py が作る。js は前のページの計算（いくら？など）をそのまま動かす。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,RM=S_.RM,D=S_.data;
S_.main.innerHTML='<div class="wrap dc"><section class="hero"><h1 class="h1t">'+esc(D.h1)+'</h1>'+(D.sub?'<p class="h1p">'+D.sub+'</p>':'')+'</section>'+D.html+'</div>';
/* 開く・閉じる（高さをなめらかに） */
$$(".dc details").forEach(function(d){var s=d.querySelector("summary");s.addEventListener("click",function(e){if(RM)return;e.preventDefault();var b=d.querySelector(".ddd");
  if(!b){d.open=!d.open;return}
  if(d.open){var h=b.scrollHeight;b.animate([{height:h+"px",opacity:1},{height:"0px",opacity:0}],{duration:220,easing:"cubic-bezier(.2,.9,.25,1)"}).onfinish=function(){d.open=false};d.classList.remove("op")}
  else{d.open=true;d.classList.add("op");var h2=b.scrollHeight;b.animate([{height:"0px",opacity:0},{height:h2+"px",opacity:1}],{duration:260,easing:"cubic-bezier(.2,.9,.25,1)"})}})});
/* 街の名前で探す（assets/towns.json → /machi/） */
var tq=$("#tq");if(tq){var TW=null,box=$("#tqo");
  var load=function(){if(TW)return Promise.resolve(TW);return fetch(D.towns||"/assets/towns.json").then(function(r){return r.json()}).then(function(j){TW=j.towns||j;return TW})};
  var kana=function(s){return s.replace(/[ァ-ヶ]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-96)})};
  tq.addEventListener("focus",load);
  tq.addEventListener("input",function(){var q=kana(tq.value.trim());if(!q){box.innerHTML="";return}
    load().then(function(T){var L=T.filter(function(t){return (t.n+(t.k||"")).indexOf(q)>=0||kana(t.n).indexOf(q)>=0}).slice(0,6);
      box.innerHTML=L.length?L.map(function(t){return '<a href="/machi/'+t.id+'"><b>'+esc(t.n)+'</b><small>'+esc(t.p)+(t.r8!=null?'・住宅地の地価 '+(t.r8>0?"+":"")+t.r8+'%':'')+'</small><i>→</i></a>'}).join(""):'<p class="dno2">見つかりませんでした。市の名前（例：寝屋川市）で探してください。</p>'})})}
/* 前のページの計算（いくら？など） */
if(D.js){try{(new Function(D.js))()}catch(e){}}
/* 選んだ印が動く（chips の aria-pressed） */
$$(".dc .dchs").forEach(function(g){g.addEventListener("click",function(e){var b=e.target.closest("button");if(b&&!RM)b.animate([{transform:"scale(.96)"},{transform:"none"}],{duration:180})})});
S_.ready();
})();
