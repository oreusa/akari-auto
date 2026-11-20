/* 新しい表紙（見本 /shin/cover2 → OK後に / と入れ替え）。
   11/19 23:16 owner「表紙ほぼおでかけじゃん」「地図も変」「全然お洒落でもAppleっぽくもない」。
   役目＝開いてすぐ、このサイトで分かること（おでかけ・家と土地・おかいもの・開店閉店）が同じ重さで見え、1タップで行ける。
   形＝apple.com の表紙：分野ごとに「見出し・1行・ボタン2つ・大きい絵」の面を縦に並べる。最後は分野ごとのリンクの一覧。
   こだわり＝面の絵は毎朝の本物の中身（開催中の写真・地価が上がった街・いちばん安い値段・次に開くお店）。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,TD=S_.TD,diff=S_.diff,md=S_.md,RM=S_.RM,D=S_.data;
function avg(b){try{var h=Uint8Array.from(atob(b),function(c){return c.charCodeAt(0)}),hd=h[0]|h[1]<<8|h[2]<<16,l=(hd&63)/63,p=((hd>>6)&63)/31.5-1,q=((hd>>12)&63)/31.5-1,bb=l-2/3*p,r=(3*l-bb+q)/2,g=r-q;
  var f=function(v){return Math.round(255*Math.max(0,Math.min(1,v)))};return "rgb("+f(r)+","+f(g)+","+f(bb)+")"}catch(e){return ""}}
function img(x){return x.im.indexOf("/")>=0?x.im:"/assets/ph/"+x.im}
function left(e){var n=diff(TD,e);return n<=0?"きょうまで":n<=7?"あと"+n+"日":md(e)+"まで"}
function yen(u){return (u>=100?Math.round(u).toLocaleString("ja-JP"):(Math.round(u*10)/10).toString())+"円"}
function btns(a,b){return '<p class="c3b"><a class="f" href="'+a[1]+'">'+esc(a[0])+'</a>'+(b?'<a href="'+b[1]+'">'+esc(b[0])+'</a>':'')+'</p>'}
function head(h,s){return '<h2>'+h+'</h2><p class="s">'+s+'</p>'}

var RN=(S_.reg&&S_.reg.n)||"関西",od=D.od,ie=D.ie,ka=D.kau,kai=D.kai,h="";
/* 1 おでかけ：開催中の写真が静かに切り替わる */
var ph=od.ph||[],SL=document.documentElement.classList.contains("iro");/* 見本 ?iro=1 の時だけ横にめくる形 */
h+='<section class="c3u">'+head(RN+'のおでかけ','いま開催中のイベントが<b>'+od.n+'</b>件。<br>毎朝、公式の発表から集めています。')+btns(['開催中を見る','/odekake'],['今週末','/odekake#we'])+
  (SL?(ph.length?'<div class="c3sl"><div class="c3tr" id="c3tr">'+ph.map(function(x,i){return '<a class="c3sd'+(i?'':' on')+'" href="'+(x.o?'/o/'+x.o:'/odekake')+'"><img src="'+img(x)+'" alt="" '+(i?'loading="lazy"':'fetchpriority="high"')+' decoding="async" style="background-color:'+avg(x.th)+'"><span class="c3sc"><b>'+esc(x.t)+'</b><small>'+esc(x.p)+'・'+left(x.e)+'</small></span></a>'}).join("")+
  '</div><div class="c3dt" id="c3dt">'+ph.map(function(_,i){return '<i'+(i?'':' class="on"')+'></i>'}).join("")+'</div></div>':''):(ph.length?'<a class="c3v c3ph" id="c3ph" href="'+(ph[0].o?'/o/'+ph[0].o:'/odekake')+'">'+ph.map(function(x,i){return '<img src="'+img(x)+'" alt="" '+(i?'loading="lazy"':'fetchpriority="high"')+' decoding="async" style="background-color:'+avg(x.th)+'"'+(i?'':' class="on"')+'>'}).join("")+
  '</a><p class="c3cap" id="c3cap">'+esc(ph[0].t)+'<span>'+esc(ph[0].p)+'・'+left(ph[0].e)+'</span></p>':''))+'</section>';
/* 2 家と土地：地価がいちばん上がった街 */
var tw=ie.tw||[];
h+='<section class="c3u g">'+head('家と土地の値段',RN+(ie.n||'')+'の街の、実際に売れた値段と<br>住宅地の地価の動き。')+btns(['街をさがす','/fudosan-list'],['いくらで売れる？','/ikura'])+
  (tw.length?'<div class="c3v c3st"><p class="c3lb">住宅地の地価が、1年でいちばん上がった街</p><a class="c3n1" href="/machi/'+tw[0].id+'"><b>+'+tw[0].r+'<small>%</small></b><span>'+esc(tw[0].n)+'</span></a>'+
  '<div class="c3n2">'+tw.slice(1).map(function(t){return '<a href="/machi/'+t.id+'"><b>+'+t.r+'<small>%</small></b><span>'+esc(t.n)+'</span></a>'}).join("")+'</div></div>':'')+'</section>';
/* 3 おかいもの：いちばん安い値段 */
var ks=ka.ks||[];
h+='<section class="c3u k">'+head('日用品の値段くらべ','楽天・Yahoo!ショッピング・Amazon を、<br>1つの画面で。'+ka.n+'種類を毎朝しらべ直し。')+btns(['いちばん安いお店を見る','/okaimono'])+
  (ks.length?'<div class="c3v c3ks">'+ks.map(function(k){return '<a href="/okaimono"><svg viewBox="0 0 24 24" aria-hidden="true">'+k.ic+'</svg><span>'+esc(k.nm)+'</span><b>'+yen(k.u)+'</b><small>'+esc(k.unit)+'あたり</small></a>'}).join("")+'</div><p class="c3cap">いま、いちばん安いお店の値段</p>':'')+'</section>';
/* 4 開店・閉店：次に開くお店 */
var x=kai.x;
h+='<section class="c3u">'+head('開店・閉店ニュース',RN+'で、これから開くお店が<b>'+kai.n+'</b>件。<br>新しいお店と、閉まるお店。')+btns(['これから開くお店','/kaiten'],['閉まるお店','/kaiten#w=close'])+
  (x?'<a class="c3v c3kc" href="'+(x.sp||'/kaiten')+'"><span class="im"><img src="'+img(x)+'" alt="" loading="lazy" decoding="async"></span><small>'+esc(x.big?x.d.replace(/(開店|閉店|期間限定)$/,"")+"・"+x.big:x.d)+'</small><b>'+esc(x.t)+'</b><em>'+esc(x.a||x.p)+'</em></a>':'')+'</section>';
/* 5 季節：写真の面を2つ */
function tile(t,s,u,p){return '<a class="c3t" href="'+u+'">'+(p?'<img src="'+img(p)+'" alt="" loading="lazy" decoding="async" style="background-color:'+avg(p.th)+'">':'')+'<span><b>'+t+'</b><small>'+s+'</small><i>見る</i></span></a>'}
h+='<div class="c3tg"><a class="c3t c3il" href="/illumination"><div class="c3bk" aria-hidden="true">'+Array.apply(null,Array(42)).map(function(_,i){var r=function(k){return ((i+1)*k*9301+49297)%233280/233280};return '<em style="--x:'+(r(7)*100).toFixed(1)+'%;--y:'+(30+r(13)*68).toFixed(1)+'%;--s:'+(i%7?6+r(17)*16:34+r(19)*30).toFixed(0)+'px;--d:'+(r(23)*5).toFixed(1)+'s;--h:'+(i%9?36+r(29)*12:i%2?205:340).toFixed(0)+';--o:'+(i%7?.9:.45)+'"></em>'}).join("")+'</div><span><b>イルミネーション</b><small>'+RN+'の光のイベント</small><i>見る</i></span></a>'+tile('紅葉','見ごろの名所','/koyo',D.ko)+'</div>';
/* 6 すべてのページ（apple.com の一番下の一覧の形） */
h+='<nav class="c3f" aria-label="すべてのページ">'+D.ft.map(function(g,i){return '<div class="c3g c3g'+i+'"><h3>'+esc(g[0])+'</h3>'+g[1].map(function(a){return '<a href="'+a[1]+'">'+esc(a[0])+'</a>'}).join("")+'</div>'}).join("")+
  '<div class="c3g c3gs"><h3>'+esc((S_.reg&&S_.reg.brand)||"TOWN NOTE")+'</h3>'+D.sns.map(function(s){return '<a href="'+s[1]+'" target="_blank" rel="noopener">'+esc(s[0])+'</a>'}).join("")+'</div></nav>';
S_.main.innerHTML='<div class="c3">'+h+'</div>';

/* 11/20 owner「ここスライドでも良かった・お洒落に」：写真は指で横にめくる。5秒ごとに次へ（触っている間・動きを減らす設定の人は止める） */
var tr=$("#c3tr");
if(tr){var sds=$$(".c3sd",tr),dts=$$("#c3dt i"),cur=0,tm=null,hold=0;
  var mark=function(){var c=tr.scrollLeft+tr.clientWidth/2,best=0,bd=1e9;sds.forEach(function(e,k){var d=Math.abs(e.offsetLeft+e.offsetWidth/2-c);if(d<bd){bd=d;best=k}});cur=best;sds.forEach(function(e,k){e.classList.toggle("on",k===cur)});dts.forEach(function(e,k){e.classList.toggle("on",k===cur)})};
  var go=function(k){var e=sds[k];if(e)tr.scrollTo({left:e.offsetLeft-(tr.clientWidth-e.offsetWidth)/2,behavior:RM?"auto":"smooth"})};
  var rf=0;tr.addEventListener("scroll",function(){if(!rf)rf=requestAnimationFrame(function(){rf=0;mark()})},{passive:true});
  tr.addEventListener("touchstart",function(){hold=1},{passive:true});tr.addEventListener("touchend",function(){setTimeout(function(){hold=0},2500)},{passive:true});
  dts.forEach(function(d,k){d.addEventListener("click",function(){go(k)})});
  if(!RM&&sds.length>1)new IntersectionObserver(function(es){if(es[0].isIntersecting){if(!tm)tm=setInterval(function(){if(!hold&&!document.hidden)go(cur+1<sds.length?cur+1:0)},5000)}else{clearInterval(tm);tm=null}}).observe(tr)}
/* 写真が静かに切り替わる（動きを減らす設定の人は切り替えない） */
var box=$("#c3ph");
if(box&&ph.length>1&&!RM){var ims=$$("img",box),cap=$("#c3cap"),i=0,tm=null;
  var go=function(){ims[i].classList.remove("on");i=(i+1)%ims.length;ims[i].classList.add("on");var p=ph[i];box.href=p.o?"/o/"+p.o:"/odekake";
    cap.innerHTML=esc(p.t)+'<span>'+esc(p.p)+'・'+left(p.e)+'</span>'};
  new IntersectionObserver(function(es){if(es[0].isIntersecting){if(!tm)tm=setInterval(go,4200)}else{clearInterval(tm);tm=null}}).observe(box)}
/* 面の文字がふわっと出る（見えない時は最初から出しておく） */
if(!RM&&"IntersectionObserver" in window){var us=$$(".c3u,.c3t");us.forEach(function(u,k){if(k)u.classList.add("c3in")});
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.remove("c3in");io.unobserve(e.target)}})},{rootMargin:"0px 0px -12% 0px"});us.forEach(function(u){io.observe(u)})}
S_.ready();
})();
