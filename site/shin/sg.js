/* 新しいHP：家を買いたい（/sagasu「その予算で、どの街に住める？」）。関西・関東で同じファイル。
   11/23 owner「全部やり変えて」→ 前のページ（頭をかぶせただけ）を、この土台で作り直した。数字と計算の元は前のページのまま（tools/fudosan_list/kau.py が毎朝作る）。
   D = {h1, sub, rows:[{id,p,n,c,m,h,w,l,la,r,o}], ord, col, bud, unit, units, kinds:[[k,y,l]], note, foot} */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,RM=S_.RM,D=S_.data;
var R=D.rows,TD=new Date(Date.now()+9*3600e3).toISOString().slice(0,10);
R.forEach(function(t){t.o=(t.o||[]).filter(function(x){return x[1]>=TD})});
var st={k:D.kinds[0][0],y:D.kinds[0][1],b:3000,p:"",s:"up",n:30};
function man(v){return v>=10000?Math.floor(v/10000)+"億"+(v%10000?(v%10000).toLocaleString()+"万":"")+"円":v.toLocaleString()+"万円"}
function yu(t){var u=t.c?"https://realestate.yahoo.co.jp/"+st.y+"/search/"+(D.yr||"06")+"/"+t.c.slice(0,2)+"/"+t.c+"/":"https://realestate.yahoo.co.jp/";return D.aff+encodeURIComponent(u)}
S_.main.innerHTML='<div class="wrap dc rkx sgx"><section class="hero"><h1 class="h1t">'+esc(D.h1)+'</h1><p class="h1p">'+D.sub+'</p></section>'+
 '<section class="sgq"><p class="dq"><i>1</i>買いたい家</p><div class="rkt" id="kd">'+D.kinds.map(function(k,i){return '<button type="button" aria-selected="'+(i?"false":"true")+'" data-k="'+k[0]+'" data-y="'+k[1]+'">'+esc(k[2])+'</button>'}).join("")+'</div>'+
 '<p class="dq"><i>2</i>予算は？</p><div class="dchs sgb" id="bc"></div></section>'+
 '<div class="sgr" aria-live="polite"><span>この予算で届く街</span><b id="res">0</b><small>/ '+R.length+'</small></div>'+
 '<div class="dchs rkg" id="pf"></div>'+
 '<div class="sgs"><div class="rkt" id="so"><button type="button" aria-selected="true" data-s="up">値上がり順</button><button type="button" aria-selected="false" data-s="cheap">安い順</button><button type="button" aria-selected="false" data-s="od">おでかけ多い順</button></div>'+
 '<p class="sgh"><span>押すと、その街で売り出し中の家（広告）</span><span id="unit">'+esc(D.units[st.k]||D.unit)+'</span></p></div>'+
 '<ol class="rkl sgl" id="tl"></ol><p class="dnote">'+D.note+'</p>'+(D.foot||"")+'</div>';
var bc=$("#bc"),tl=$("#tl"),rs=$("#res"),last=0;
function cnt(to){if(RM||!rs.animate){rs.textContent=to;last=to;return}var a=last,t0=performance.now();last=to;(function f(t){var k=Math.min(1,(t-t0)/420);rs.textContent=Math.round(a+(to-a)*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(f)})(t0)}
function draw(){
 bc.innerHTML=D.bud.map(function(v){return '<button type="button" data-b="'+v+'" aria-pressed="'+(v===st.b)+'">'+v.toLocaleString()+'<small>万円まで</small></button>'}).join("");
 var A=R.filter(function(t){return t[st.k]!=null&&t[st.k]<=st.b}),c={};A.forEach(function(t){c[t.p]=(c[t.p]||0)+1});
 cnt(A.length);
 $("#pf").innerHTML='<button type="button" data-p="" aria-pressed="'+(!st.p)+'">ぜんぶ '+A.length+'</button>'+D.ord.map(function(p){return '<button type="button" data-p="'+p+'" aria-pressed="'+(st.p===p)+'">'+p+' '+(c[p]||0)+'</button>'}).join("");
 var L=A.filter(function(t){return !st.p||t.p===st.p});
 L.sort(st.s==="up"?function(a,b){return b.r-a.r}:st.s==="cheap"?function(a,b){return a[st.k]-b[st.k]}:function(a,b){return b.o.length-a.o.length||b.r-a.r});
 tl.innerHTML=L.length?L.slice(0,st.n).map(function(t,i){return '<li><span class="n">'+(i+1)+'</span><a href="'+esc(yu(t))+'" rel="nofollow sponsored noopener" target="_blank" data-k="家を探す｜Yahoo!不動産｜'+esc(t.n)+'"><b>'+esc(t.n)+'</b><small>'+esc(t.p)+(st.k==="l"&&t.la?'・平均'+t.la+'㎡':'')+'<em class="'+(t.r>0?"u":t.r<0?"d":"")+'">地価 '+(t.r>0?"+":"")+t.r.toFixed(1)+'%</em></small>'+
   (t.o.length?'<small class="sgo">いま：'+esc(t.o[0][0])+(t.o.length>1?' ほか'+(t.o.length-1):'')+'</small>':'')+'</a><span class="v">'+man(t[st.k])+'</span></li>'}).join("")+
   (L.length>st.n?'<li class="sgm"><button type="button" class="dbtn2" id="kmore">あと'+(L.length-st.n)+'の街を見る</button></li>':''):'<li class="sge">この予算では、まだ届く街がありません。予算を少し上げてみてください。</li>';
 S_.counts&&S_.counts(tl)}
function seg(el,fn){el.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;$$("button",el).forEach(function(x){x.setAttribute("aria-selected",x===b?"true":"false")});fn(b);st.n=30;draw()})}
seg($("#kd"),function(b){st.k=b.dataset.k;st.y=b.dataset.y;$("#unit").textContent=D.units[st.k]||D.unit});
seg($("#so"),function(b){st.s=b.dataset.s});
bc.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;st.b=+b.dataset.b;st.n=30;draw()});
$("#pf").addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;st.p=b.dataset.p;st.n=30;draw()});
tl.addEventListener("click",function(e){if(e.target.id==="kmore"){st.n+=60;draw()}});
draw();try{var _o=bc.querySelector('[aria-pressed=true]');bc.scrollLeft=_o.offsetLeft-bc.clientWidth/2+_o.offsetWidth/2}catch(_){}S_.ready();
})();
