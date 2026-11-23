/* 11/24 まちランキングの見本（?mihon=1 紙面 ／ ?mihon=2 索引）。本番は変えない。
   同じ形のカードが45本ならぶ形をやめて、中身（公式の数字の1位と値）を前に出す。
   オーロラ・夜空・下のバー・ロゴ・売る入口・絞り込みはそのまま。押すと今と同じ「順位の全部」が開く（元の行を押す）。 */
(function(){
var M=(location.search.match(/[?&]mihon=([12])/)||[])[1];if(!M)return;
var D;try{D=JSON.parse(document.getElementById("d").textContent)}catch(e){return}
var IT=D.items||[],grid=document.getElementById("grid");if(!grid)return;
document.documentElement.classList.add("rkm","rkm"+M);
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
var RX=/(\d+)位\s*([^0-9+＋\-−\s・][^\s]*?(?:（[^）]*）)?)\s*([+＋\-−]?[\d,.]+)\s*(%|％|万円\/㎡|万円|円\/㎡|万人|人)/;
function rows(x){if(x._r)return x._r;var out=[],seen={};x.body.split("\n").forEach(function(l){var m=RX.exec(l);if(m&&!seen[m[1]]&&out.length<10){seen[m[1]]=1;out.push({no:+m[1],n:m[2],v:m[3].replace("＋","+").replace("−","-"),u:m[4].replace("％","%")})}});
  out.sort(function(a,b){return a.no-b.no});return x._r=out}
function lead(x){var l=(x.body.split("\n").filter(function(s){return s.trim()})[0]||"").trim();return l.length>60?"":l}
function num(v){return parseFloat(String(v).replace(/,/g,""))}
var KN={eki:"駅",ie:"家と土地",hito:"人口",hoka:"そのほか"};
function meta(x){return (x.d||"").replace(/・/g," ")}
var box=document.createElement("div");box.id="rkm";box.className="rkm-"+M;grid.parentNode.insertBefore(box,grid);
function open(i){var a=grid.querySelector('[data-i="'+i+'"]');if(a)a.click()}
box.addEventListener("click",function(e){var a=e.target.closest("[data-oi]");if(!a)return;e.preventDefault();open(a.getAttribute("data-oi"))});

function bars(r,max){return '<ol class="rb">'+r.slice(0,5).map(function(o){var w=max?Math.max(4,Math.round(Math.abs(num(o.v))/max*100)):0;
  return '<li><span class="rn">'+o.no+'</span><span class="rt">'+esc(o.n)+'</span><b class="rv">'+esc(o.v)+'<small>'+esc(o.u)+'</small></b><i class="rl" style="--w:'+w+'%"></i></li>'}).join("")+'</ol>'}

function paper(L){var h="";L.forEach(function(p,k){var x=p.x,r=rows(x),t=r[0];
  if(k===0&&t){var max=Math.max.apply(null,r.slice(0,5).map(function(o){return Math.abs(num(o.v))}));
    h+='<article class="pl0"><a href="#" data-oi="'+p.i+'"><p class="pm">'+esc(KN[x.k]||"")+'　'+esc(meta(x))+'</p><h3>'+esc(x.t)+'</h3>'+
       '<p class="rkbig"><span>1位 '+esc(t.n)+'</span><b>'+esc(t.v)+'<small>'+esc(t.u)+'</small></b></p>'+(lead(x)?'<p class="rkld">'+esc(lead(x))+'</p>':"")+bars(r,max)+'<span class="rkmore">順位の全部と出どころ</span></a></article>';return}
  h+='<article class="pl1"><a href="#" data-oi="'+p.i+'"><p class="pm">'+esc(KN[x.k]||"")+'　'+esc(meta(x))+'</p><h3>'+esc(x.t)+'</h3>'+
     (t?'<p class="rkone"><span>1位 '+esc(t.n)+'</span><b>'+esc(t.v)+'<small>'+esc(t.u)+'</small></b></p>':(lead(x)?'<p class="rkld">'+esc(lead(x))+'</p>':""))+'</a></article>'});
  return h}

function index(L){var h='<div class="ixh"><span>No.</span><span>ランキング</span><span>1位</span></div>',last="";
  L.forEach(function(p){var x=p.x,r=rows(x),t=r[0],dd=(x.d||"").split("・").pop();
    if(dd!==last){h+='<p class="ixd">'+esc(dd)+'</p>';last=dd}
    h+='<a class="ixr" href="#" data-oi="'+p.i+'"><span class="ixn">'+esc(((x.d||"").match(/No\.(\d+)/)||[])[1]||"")+'</span><span class="ixt">'+esc(x.t)+'<small>'+esc(KN[x.k]||"")+'・'+esc(x.p)+'</small></span>'+
       (t?'<span class="ixv"><small>'+esc(t.n)+'</small><b>'+esc(t.v)+'</b><i>'+esc(t.u)+'</i></span>':'<span class="ixv ixe">ひらく</span>')+'</a>'});
  return h}

function draw(){var L=[].map.call(grid.querySelectorAll("[data-i]"),function(a){var i=a.getAttribute("data-i");return{i:i,x:IT[+i]||IT.filter(function(z){return String(z.i)===i})[0]}}).filter(function(p){return p.x});
  box.innerHTML=M==="1"?paper(L):index(L)}
new MutationObserver(draw).observe(grid,{childList:true});draw();
})();
