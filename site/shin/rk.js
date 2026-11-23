/* 新しいHP：地価ランキング（関西 /chika-kansai・/chika-osaka、関東 /chika-kanto・/chika-tokyo）。
   11/23 owner「hpと同じじゃないのあるんじゃない？全部やり変えて」→ 前のページに頭をかぶせていた物を、この土台で作り直した。
   D = {h1, sub, tabs:[{k,l}], groups:[{k,l}], rows:[{n,id,p,k,v:{tabk:[前年,今年]}}], avg:{tabk:[前年,今年]}, an, foot}
   ＋こだわり：「うちの街は何位？」で名前を入れると、その街の順位まで飛んで光る。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,RM=S_.RM,D=S_.data;
var T=D.tabs||[{k:"r",l:"住宅地"}],G=D.groups||[],R=D.rows,N0=30;
var st={t:0,g:G.length?G[0].k:"",all:0};var _h=location.hash.slice(1);G.forEach(function(g){if(g.h&&g.h===_h)st.g=g.k});
var kana=function(s){return (s||"").replace(/[ァ-ヶ]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-96)})};
function sg(v){return D.plain?v.toFixed(1):(v>0?"+":v<0?"−":"±")+Math.abs(v).toFixed(1)}
function hu(r){return r.u||(r.id?"/machi/"+r.id:"")}
function rows(tk,g){
  var a=R.filter(function(r){return r.v[tk]&&(!g||g==="all"||r.p===g)}).sort(function(x,y){return y.v[tk][1]-x.v[tk][1]||x.n.localeCompare(y.n,"ja")});
  var pv=null,pr=0;a=a.map(function(r,i){var v=r.v[tk][1];var k=v===pv?pr:i+1;pv=v;pr=k;return {r:r,k:k}});return a}
function gl(){var g=G.filter(function(x){return x.k===st.g})[0];return g?g.l:""}
function draw(){
  var tk=T[st.t].k,L=rows(tk,st.g),mx=Math.max.apply(null,L.map(function(x){return Math.abs(x.r.v[tk][1])}).concat([1]));
  var p3=L.slice(0,3).map(function(x){var v=x.r.v[tk];return '<a class="rkp'+x.k+'" href="'+(hu(x.r)||'#r-'+x.r.n)+'" data-k="地価｜上位｜'+esc(x.r.n)+'"><i>'+x.k+'位</i><b>'+esc(x.r.s||x.r.n)+'</b><span>'+sg(v[1])+'<small>%</small></span><em>'+esc(x.r.p&&G.length?x.r.p:'')+(v[0]!=null?(x.r.p&&G.length?'・':'')+'前年 '+sg(v[0])+'%':'')+'</em></a>'}).join("");
  var sh=st.all?L:L.slice(0,N0);
  var li=sh.map(function(x){var r=x.r,v=r.v[tk],up=v[0]==null?"":v[1]>v[0]?'<em class="u">前年より ↑</em>':v[1]<v[0]?'<em class="d">前年より ↓</em>':'<em>前年と同じ</em>';
    return '<li id="r-'+esc(r.id||r.n)+'"><span class="n">'+x.k+'</span>'+(hu(r)?'<a href="'+hu(r)+'" data-k="地価｜街｜'+esc(r.n)+'">':'<div>')+'<b>'+esc(r.n)+'</b><small>'+(G.length&&st.g==="all"?esc(r.p)+'・':'')+(v[0]!=null?'前年 '+sg(v[0])+'%':'')+(r.x?esc(r.x):'')+up+'</small>'+(hu(r)?'</a>':'</div>')+
      '<span class="v'+(v[1]<0?' m':'')+'">'+sg(v[1])+'<small>%</small></span><i class="b'+(v[1]<0?' m':'')+'" style="--w:'+Math.max(2,Math.round(Math.abs(v[1])/mx*100))+'%"></i></li>'}).join("");
  var av=D.avg&&D.avg[st.g==="all"||!st.g?"all":st.g];av=av&&av[tk];
  $("#rkb").innerHTML='<div class="rkp">'+p3+'</div>'+
    (av?'<p class="rka">'+esc((st.g&&st.g!=="all"?gl():D.an||"平均"))+'の平均 <b>'+sg(av[1])+'%</b>（前年 '+sg(av[0])+'%）</p>':'')+
    '<ol class="rkl">'+li+'</ol>'+(L.length>N0&&!st.all?'<button type="button" class="dbtn2 rkm" id="rkm">'+esc(gl()||"")+' '+L.length+'の街を全部見る</button>':'');
  var m=$("#rkm");if(m)m.addEventListener("click",function(){st.all=1;draw()});
}
var tabs=T.length>1?'<div class="rkt" role="tablist">'+T.map(function(t,i){return '<button type="button" role="tab" aria-selected="'+(i?"false":"true")+'" data-i="'+i+'">'+esc(t.l)+'</button>'}).join("")+'</div>':'';
var grp=G.length?'<div class="dchs rkg" id="rkg">'+G.map(function(g,i){return '<button type="button" data-g="'+g.k+'" aria-pressed="'+(g.k===st.g?"true":"false")+'">'+esc(g.l)+'</button>'}).join("")+'</div>':'';
S_.main.innerHTML='<div class="wrap dc rkx"><section class="hero"><h1 class="h1t">'+esc(D.h1)+'</h1>'+(D.sub?'<p class="h1p">'+D.sub+'</p>':'')+'</section>'+
  '<section class="rkf"><label for="rq">うちの街は何位？</label><input class="din" id="rq" type="search" placeholder="街の名前（例：'+esc(D.ex||R[0].n)+'）" autocomplete="off"><div id="rqo"></div></section>'+
  tabs+grp+'<div id="rkb" aria-live="polite"></div>'+(D.foot||"")+'</div>';
draw();
$$(".rkt button").forEach(function(b){b.addEventListener("click",function(){st.t=+b.dataset.i;st.all=0;$$(".rkt button").forEach(function(x){x.setAttribute("aria-selected",x===b?"true":"false")});draw()})});
$$("#rkg button").forEach(function(b){b.addEventListener("click",function(){st.g=b.dataset.g;st.all=0;$$("#rkg button").forEach(function(x){x.setAttribute("aria-pressed",x===b?"true":"false")});draw();
  if(!RM)$("#rkb").animate([{opacity:.3,transform:"translateY(6px)"},{opacity:1,transform:"none"}],{duration:260,easing:"cubic-bezier(.2,.9,.25,1)"})})});
/* うちの街は何位？ */
var q=$("#rq"),qo=$("#rqo");
q.addEventListener("input",function(){var s=kana(q.value.trim());if(!s){qo.innerHTML="";return}
  var tk=T[st.t].k,A=rows(tk,G.length?"all":""),n=A.length;
  var hit=A.filter(function(x){return (x.r.n+kana(x.r.k||"")).indexOf(s)>=0||kana(x.r.n).indexOf(s)>=0}).slice(0,5);
  qo.innerHTML=hit.length?hit.map(function(x){var v=x.r.v[tk];return '<button type="button" data-id="'+esc(x.r.id||x.r.n)+'"><b>'+esc(x.r.n)+'</b><span>'+esc(D.an||"")+n+'の街で <em>'+x.k+'位</em>・'+sg(v[1])+'%</span><i>→</i></button>'}).join(""):'<p class="dno2">見つかりませんでした。市区町村の名前で探してください。</p>'});
qo.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;
  if(G.length){st.g="all";$$("#rkg button").forEach(function(x){x.setAttribute("aria-pressed",x.dataset.g==="all"?"true":"false")})}
  try{var _r=R.filter(function(x){return (x.id||x.n)===b.dataset.id})[0];if(_r)dispatchEvent(new CustomEvent("tn-town",{detail:{n:_r.n,id:_r.id||""}}))}catch(_){}
  st.all=1;draw();var el=document.getElementById("r-"+b.dataset.id);if(!el)return;
  el.scrollIntoView({behavior:RM?"auto":"smooth",block:"center"});el.classList.add("hl");setTimeout(function(){el.classList.remove("hl")},2600);
  q.value="";qo.innerHTML="";try{S_.count&&S_.count("地価｜何位")}catch(_){}});
S_.ready();
})();
