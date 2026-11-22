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
/* 11/21 owner まわりの声「色々ありすぎて何を触ったらいいか分からない」→ 見本 ?kn=1（?kn=0 で前）：
   入口は「おでかけ」「家と土地」の2つの大きな札だけ（30日で押された数の上の2つ）。ほかは小さな1行と、たためる「すべてのページ」へ。 */
var KN=0;try{var _k=location.search.match(/[?&]kn=([01])/);if(_k)localStorage.setItem("tn_kn2",_k[1]);KN=localStorage.getItem("tn_kn2")!=="0"}catch(e){}
if(KN){document.documentElement.classList.add("lk-kn");var tw0=(ie.tw||[])[0];
  h='<section class="kn"><h1 class="vh">'+esc(RN)+'のおでかけと家の値段｜'+esc((S_.reg&&S_.reg.brand)||"TOWN NOTE")+'</h1>'+
  '<a class="knc knod" href="/odekake" data-k="入口かんたん｜おでかけ">'+(ph.length?'<span class="knph" id="c3ph">'+ph.slice(0,5).map(function(x,i){return '<img src="'+img(x)+'" alt="" '+(i?'loading="lazy"':'fetchpriority="high"')+' decoding="async" style="background-color:'+avg(x.th)+'"'+(i?'':' class="on"')+'>'}).join("")+'</span>':'')+
   '<span class="knt"><small>おでかけ</small><b>いま開催中のイベント</b><em><i data-n="'+od.n+'">'+od.n+'</i>件・毎朝、公式の発表から</em></span><span class="knar" aria-hidden="true">→</span></a>'+
  '<a class="knc knie" href="/fudosan-list" data-k="入口かんたん｜家と土地"><span class="knt"><small>家と土地</small><b>街の相場と、売れる値段</b><em>'+esc(RN)+(ie.n||'')+'の街・実際に売れた値段と地価</em></span>'+
   (tw0?'<span class="knst"><b>+'+tw0.r+'<small>%</small></b><span>'+esc(tw0.n)+'<br>地価の上がり方 1位</span></span>':'')+'<span class="knar" aria-hidden="true">→</span></a>'+
  '<p class="kno"><span>ほかに</span><a href="/okaimono" data-k="入口かんたん｜おかいもの">日用品の値段くらべ</a><a href="/kaiten" data-k="入口かんたん｜開店閉店">開店・閉店ニュース</a></p>'+
  '<details class="knall"><summary>すべてのページ</summary><nav class="c3f" aria-label="すべてのページ">'+D.ft.map(function(g,i){return '<div class="c3g c3g'+i+'"><h3>'+esc(g[0])+'</h3>'+g[1].map(function(a){return '<a href="'+a[1]+'">'+esc(a[0])+'</a>'}).join("")+'</div>'}).join("")+
  '</nav></details><nav class="c3f knft" aria-label="SNS"><div class="c3g c3gs"><h3>'+esc((S_.reg&&S_.reg.brand)||"TOWN NOTE")+'</h3>'+D.sns.map(function(s){return '<a href="'+s[1]+'" target="_blank" rel="noopener">'+esc(s[0])+'</a>'}).join("")+'</div></nav></section>'}
/* 11/22 owner「使いやすくわかりやすい。でもお洒落にはしたい」→ 見本 ?ks=1（?ks=0 で前・kn の時だけ）：
   選ぶ物は同じ2つ＋ほかに2つのまま。おでかけは写真を大きく縦に（字は写真の上のすりガラス）、家と土地は上がった街3つを光の棒で、ほかには同じ形の小さな札2枚。 */
var KS=0;try{var _s=location.search.match(/[?&]ks=([01])/);if(_s)localStorage.setItem("tn_ks2",_s[1]);KS=localStorage.getItem("tn_ks2")!=="0"}catch(e){}
if(KN&&KS){document.documentElement.classList.add("lk-ks");
  var EN=RN==="関東"?"KANTO":"KANSAI",dw=["SUN","MON","TUE","WED","THU","FRI","SAT"][new Date(TD+"T00:00:00Z").getUTCDay()],mx=Math.max.apply(null,tw.slice(0,3).map(function(t){return t.r}).concat([1])),kx=kai.x||{};
  h='<section class="kn ks"><p class="ksd">'+dw+' '+(+TD.slice(5,7))+'.'+(+TD.slice(8,10))+'<span class="ksl"></span>'+EN+'</p><h1 class="vh">'+esc(RN)+'のおでかけと家の値段｜'+esc((S_.reg&&S_.reg.brand)||"TOWN NOTE")+'</h1>'+
  '<a class="knc ksod" href="/odekake" data-k="入口かんたん｜おでかけ">'+(ph.length?'<span class="knph" id="c3ph">'+ph.slice(0,5).map(function(x,i){return '<img src="'+img(x)+'" alt="" '+(i?'loading="lazy"':'fetchpriority="high"')+' decoding="async" style="background-color:'+avg(x.th)+'"'+(i?'':' class="on"')+'>'}).join("")+'</span>'+
    '<span class="kscap" id="c3cap">'+esc(ph[0].t)+'<span>'+esc(ph[0].p)+'・'+left(ph[0].e)+'</span></span>':'')+
   '<span class="ksgl"><small>ODEKAKE<span class="ksj">おでかけ</span></small><b>いま開催中のイベント</b><em><span class="kscnt" data-n="'+od.n+'">'+od.n+'</span>件・毎朝、公式の発表から</em><span class="knar" aria-hidden="true">→</span></span></a>'+
  '<a class="knc ksie" href="/fudosan-list" data-k="入口かんたん｜家と土地"><span class="knt"><small>HOME &amp; LAND<span class="ksj">家と土地</span></small><b>街の相場と、売れる値段</b><em>'+esc(RN)+(ie.n||'')+'の街・実際に売れた値段と地価</em></span>'+
   (tw.length?'<span class="ksbr"><small>地価が1年で上がった街</small>'+tw.slice(0,3).map(function(t,i){return '<span class="ksr"><span class="ksn">'+(i+1)+'</span><span class="ksm2">'+esc(t.n)+'</span><span class="ksu"><span class="kss" style="--w:'+Math.round(t.r/mx*100)+'%"></span></span><b>+'+t.r+'<small>%</small></b></span>'}).join("")+'</span>':'')+'<span class="knar" aria-hidden="true">→</span></a>'+
  '<div class="ksm"><a class="knc" href="/okaimono" data-k="入口かんたん｜おかいもの"><small>SHOPPING</small><b>日用品の<br>値段くらべ</b><em>'+(ka.n||"")+'種類・3つの店から</em></a>'+
   '<a class="knc" href="/kaiten" data-k="入口かんたん｜開店閉店"><small>NEW SHOPS</small><b>開店・閉店<br>ニュース</b><em>'+(kai.n?kai.n+'件・':'')+esc(kx.big||"毎日更新")+'</em></a></div>'+
  '<details class="knall"><summary>すべてのページ</summary><nav class="c3f" aria-label="すべてのページ">'+D.ft.map(function(g,i){return '<div class="c3g c3g'+i+'"><h3>'+esc(g[0])+'</h3>'+g[1].map(function(a){return '<a href="'+a[1]+'">'+esc(a[0])+'</a>'}).join("")+'</div>'}).join("")+
  '</nav></details><nav class="c3f knft" aria-label="SNS"><div class="c3g c3gs"><h3>'+esc((S_.reg&&S_.reg.brand)||"TOWN NOTE")+'</h3>'+D.sns.map(function(s){return '<a href="'+s[1]+'" target="_blank" rel="noopener">'+esc(s[0])+'</a>'}).join("")+'</div></nav></section>'}
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
  var go=function(){ims[i].classList.remove("on");i=(i+1)%ims.length;ims[i].classList.add("on");var p=ph[i];if(!KN)box.href=p.o?"/o/"+p.o:"/odekake";
    if(cap)cap.innerHTML=esc(p.t)+'<span>'+esc(p.p)+'・'+left(p.e)+'</span>'};
  new IntersectionObserver(function(es){if(es[0].isIntersecting){if(!tm)tm=setInterval(go,4200)}else{clearInterval(tm);tm=null}}).observe(box)}
/* 面の文字がふわっと出る（見えない時は最初から出しておく） */
if(!RM&&"IntersectionObserver" in window){var us=$$(".c3u,.c3t");us.forEach(function(u,k){if(k)u.classList.add("c3in")});
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.remove("c3in");io.unobserve(e.target)}})},{rootMargin:"0px 0px -12% 0px"});us.forEach(function(u){io.observe(u)})}
if(KN&&KS){var cn=$(".kscnt");if(cn&&!RM){var N=+cn.dataset.n,t0=0;cn.textContent="0";requestAnimationFrame(function st(t){if(!t0)t0=t;var k=Math.min(1,(t-t0)/900);cn.textContent=Math.round(N*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(st)})}
  setTimeout(function(){var b=$(".ksbr");if(b)b.classList.add("on")},RM?0:250)}
S_.ready();
})();
