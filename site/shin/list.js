/* 新しいHP：一覧の形（初詣・開店閉店・泊まり・いまから行ける・ランキング）。
   役目＝そのページの物が一目で並び、府県と種類で絞れて、押すと板で中身が全部分かる。
   こだわり＝おでかけと同じ写真の2列カード（写真の無い物は細い線の行）・いまから行けるは「いる場所から何分」で並ぶ。 */
(function(){
"use strict";
/* 11/22 見本 ?sd=1（会議の今週の重点）：まちランキングの1本を読んだ後に、相談の入口を1つ */
var SD=0;try{var _sd=location.search.match(/[?&]sd=([01])/);if(_sd)localStorage.setItem("tn_sd",_sd[1]);SD=localStorage.getItem("tn_sd")==="1"}catch(e){}
var S_=window.SHIN,$=S_.$,$$=S_.$$,el=S_.el,esc=S_.esc,TD=S_.TD,diff=S_.diff,md=S_.md,dd=S_.dd,RM=S_.RM,D=S_.data;
var RG=S_.reg,PREF=RG.pref,PG=D.page||{},K=PG.K||{},VIEW=PG.view||"grid";
var IT=D.items.filter(function(x){return !x.e||x.e>=TD}).map(function(x,i){x.i=i;x.st=x.s?(x.s<=TD?"now":"up"):"";x.left=x.e?diff(TD,x.e):null;x.g=K[x.k]||["",PG.c||"#6E6E73"];return x});
var BYI={};IT.forEach(function(x){BYI[x.i]=x});
function avg(b){try{var h=Uint8Array.from(atob(b),function(c){return c.charCodeAt(0)}),hd=h[0]|h[1]<<8|h[2]<<16,l=(hd&63)/63,p=((hd>>6)&63)/31.5-1,q=((hd>>12)&63)/31.5-1,bb=l-2/3*p,r=(3*l-bb+q)/2,g=r-q;
  var f=function(v){return Math.round(255*Math.max(0,Math.min(1,v)))};return "rgb("+f(r)+","+f(g)+","+f(bb)+")"}catch(e){return ""}}
function img(x){return x.im.indexOf("/")>=0?x.im:"/assets/ph/"+x.im}
function tile(x){return '<div class="tile" style="--gc:'+x.g[1]+';--gt:color-mix(in srgb,'+x.g[1]+' 9%,#fff)"><svg viewBox="0 0 24 24">'+(D.icons&&(D.icons[x.k]||D.icons._)||"")+'</svg><b>'+esc(x.g[0]||PG.h1)+'</b></div>'}
var FK="ls_fav_"+(PG.id||location.pathname),FAV={};try{FAV=JSON.parse(localStorage.getItem(FK)||"{}")}catch(e){}
function favSave(){try{localStorage.setItem(FK,JSON.stringify(FAV))}catch(e){}}

/* いまから行ける：出発する所と、そこから何分か（直線距離からの目安） */
var ORG=RG.org||[["梅田",34.7025,135.4959],["なんば",34.6666,135.5011],["京都駅",34.9858,135.7588],["三宮",34.6946,135.1955],["奈良駅",34.6809,135.8197],["大津駅",35.0031,135.8648],["和歌山駅",34.2325,135.1913]];
var Q=new URLSearchParams(location.search),S={p:Q.get("p")||PG.p||"",k:Q.get("k")||"",w:Q.get("w")||(PG.tabs?PG.tabs[0][0]:""),n:24,o:null,m:+(Q.get("m")||(PG.near?60:0))};
try{var so=JSON.parse(localStorage.getItem("ls_org")||"null");if(so&&so.length===3)S.o=so}catch(e){}
if(!S.o)S.o=ORG[0];
function km(a,b,c,d){var R=6371,x=(c-a)*Math.PI/180,y=(d-b)*Math.PI/180,h=Math.sin(x/2)*Math.sin(x/2)+Math.cos(a*Math.PI/180)*Math.cos(c*Math.PI/180)*Math.sin(y/2)*Math.sin(y/2);return 2*R*Math.asin(Math.sqrt(h))}
function mins(k){return Math.round((k*1.3/38*60+12)/5)*5}
function near(){IT.forEach(function(x){if(x.ll){x.km=km(S.o[1],S.o[2],x.ll[0],x.ll[1]);x.mn=mins(x.km)}else{x.km=null;x.mn=null}})}
function sunset(){var d=dd(TD),n=Math.round((d-Date.UTC(d.getUTCFullYear(),0,0))/864e5),la=S.o[1]*Math.PI/180,lo=S.o[2],
  de=23.44*Math.PI/180*Math.sin(2*Math.PI*(284+n)/365),ha=Math.acos((Math.sin(-0.833*Math.PI/180)-Math.sin(la)*Math.sin(de))/(Math.cos(la)*Math.cos(de)))*180/Math.PI,
  b=2*Math.PI*(n-81)/364,eot=9.87*Math.sin(2*b)-7.53*Math.cos(b)-1.5*Math.sin(b),t=12+ha/15-(lo-135)/15-eot/60;var h=Math.floor(t),m=Math.round((t-h)*60);if(m===60){h++;m=0}return h+":"+(m<10?"0":"")+m}

function pick(){var L=IT.filter(function(x){
  if(S.p&&x.p!==S.p)return false;if(S.k&&x.k!==S.k&&!(S.k==="_fav"&&FAV[x.id||x.t]))return false;
  if(S.w&&PG.tabs){var tb=PG.tabs.filter(function(t){return t[0]===S.w})[0];if(tb&&tb[2]&&x[tb[2]]!==tb[3])return false}
  if(PG.near){if(x.st==="up")return false;if(S.m&&(x.mn==null||x.mn>S.m))return false}
  return true});
  if(PG.near)L.sort(function(a,b){return (a.km==null?1e9:a.km)-(b.km==null?1e9:b.km)});
  return L}
function saveQ(){var u=new URLSearchParams(location.search);["p","k","w"].forEach(function(k){if(S[k])u.set(k,S[k]);else u.delete(k)});
  history.replaceState(history.state,"",location.pathname+(u.toString()?"?"+u:""))}

var DT=dd(TD);
S_.main.innerHTML='<div class="wrap"><section class="hero"><h1 class="h1t">'+esc(PG.h1)+'</h1><p class="h1p">'+esc(PG.sub||"")+'</p>'+
 '<p class="dl">'+(DT.getUTCMonth()+1)+'月'+DT.getUTCDate()+'日（'+"日月火水木金土"[DT.getUTCDay()]+'）'+(PG.dl?'<span>'+PG.dl+'</span>':"")+'</p></section>'+
 (PG.near?'<div class="nr"><div class="nrh"><small>出発する所</small><b id="org"></b><button id="geo2">'+S_.IC.map+'いまいる場所</button></div><div class="nro" id="orgs"></div>'+
   '<div class="nrt"><div><small>いま</small><b id="clk">--:--</b></div><div><small>日の入り</small><b id="sun">--:--</b></div><div><small>行ける所</small><b id="nn">0</b></div></div></div>':"")+
 (PG.tiles?'<div class="tiles qk">'+PG.tiles.map(function(t){return '<button data-'+t[2]+'="'+esc(t[3])+'"><small>'+esc(t[0])+'</small><b data-n="'+t[1]+'">0</b><i>→</i></button>'}).join("")+'</div>':"")+
 (PG.note?'<p class="lnote">'+PG.note+'</p>':"")+
 '<div id="sent"></div><div class="bar" id="bar">'+(PG.tabs?'<div class="seg" id="tab"></div>':"")+(PG.near?'<div class="seg" id="mseg"></div>':"")+(PG.seg===false?"":'<div class="seg" id="seg"></div>')+'<div class="chips" id="chips"></div></div>'+
 '<div class="cnt"><h3 id="ch"></h3><small id="cs"></small></div><div class="'+(VIEW==="list"?"lrs":"grid")+'" id="grid"></div><div id="mr"></div>'+
 (PG.also?'<nav class="also2" aria-label="あわせて見る"><small>あわせて見る</small>'+PG.also.map(function(a){return '<a href="'+a[1]+'">'+esc(a[0])+'<i>→</i></a>'}).join("")+'</nav>':"")+'</div>';
S_.counts(S_.main);

var setSeg=$("#seg")&&S_.seg($("#seg"),[["",RG.n]].concat(PREF.filter(function(p){return IT.some(function(x){return x.p===p})}).map(function(p){return [p,p]})),S.p,function(v){S.p=v;S.n=24;sync();go(true)});
if(PG.tabs)S_.seg($("#tab"),PG.tabs.map(function(t){return [t[0],t[1]]}),S.w,function(v){S.w=v;S.n=24;sync();go(true)});
if(PG.near){S_.seg($("#mseg"),[[30,"30分"],[60,"1時間"],[90,"1時間半"],[0,"すべて"]],String(S.m),function(v){S.m=+v;S.n=24;go(true)});
  var drawOrg=function(){$("#org").textContent=S.o[0];$("#orgs").innerHTML=ORG.map(function(o){return '<button class="chip'+(o[0]===S.o[0]?" on":"")+'" data-o="'+o[0]+'">'+o[0]+'</button>'}).join("");$("#sun").textContent=sunset()};
  var setOrg=function(o){S.o=o;try{localStorage.setItem("ls_org",JSON.stringify(o))}catch(e){}near();drawOrg();go(true)};
  $("#orgs").addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;setOrg(ORG.filter(function(o){return o[0]===b.dataset.o})[0])});
  $("#geo2").addEventListener("click",function(){var b=this;if(!navigator.geolocation)return;b.classList.add("wait");
    navigator.geolocation.getCurrentPosition(function(p){b.classList.remove("wait");setOrg(["いまいる場所",p.coords.latitude,p.coords.longitude])},function(){b.classList.remove("wait");b.textContent="場所が使えませんでした"},{timeout:9000,maximumAge:3e5})});
  var tick=function(){var t=new Date(Date.now()+9*36e5);$("#clk").textContent=t.getUTCHours()+":"+("0"+t.getUTCMinutes()).slice(-2)};tick();setInterval(tick,3e4);
  near();drawOrg()}
function kinds(){var c={};IT.forEach(function(x){if(!S.p||x.p===S.p)c[x.k]=(c[x.k]||0)+1});return Object.keys(K).filter(function(k){return c[k]})}
function drawChips(){var ks=kinds(),fv=PG.fav&&Object.keys(FAV).length;$("#chips").style.display=ks.length<2&&!fv?"none":"";
  $("#chips").innerHTML='<button class="chip'+(S.k?"":" on")+'" data-g="">すべて</button>'+(fv?'<button class="chip'+(S.k==="_fav"?" on":"")+'" data-g="_fav">'+S_.IC.star+'保存</button>':"")+
   ks.map(function(k){return '<button class="chip'+(S.k===k?" on":"")+'" data-g="'+k+'" style="--c:'+K[k][1]+'"><i></i>'+esc(K[k][0])+'</button>'}).join("")}
$("#chips").addEventListener("click",function(e){var b=e.target.closest(".chip");if(!b)return;S.k=b.dataset.g;S.n=24;sync();go(true)});
var qk=$(".tiles.qk");if(qk)qk.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;if(b.dataset.k!=null)S.k=b.dataset.k;if(b.dataset.w!=null){S.w=b.dataset.w;var t=$("#tab");if(t)$$("button",t).forEach(function(x){if(x.dataset.v===S.w)x.click()})}if(b.dataset.p!=null){S.p=b.dataset.p}
  S.n=24;sync();go(true);scrollTo({top:$("#sent").getBoundingClientRect().top+scrollY,behavior:"smooth"})});
function sync(){drawChips();saveQ()}

function badge(x){if(x.bg)return '<span class="lt'+(x.bgc?" "+x.bgc:"")+'">'+esc(x.bg)+'</span>';
  if(x.st==="up"){var n=diff(TD,x.s);return '<span class="lt">'+(n<=1?"あしたから":n+"日後から")+'</span>'}
  if(x.left===0)return '<span class="lt">きょうまで</span>';if(x.left!=null&&x.left<=7)return '<span class="lt">あと'+x.left+'日</span>';if(x.st==="now")return '<span class="lt now">開催中</span>';return ""}
function when(x){if(x.d)return esc(x.d);if(!x.s)return "";return x.st==="up"?md(x.s)+"から":md(x.e)+"まで"}
function sub(x){return PG.near&&x.mn!=null?'<b class="mn">約'+x.mn+'分</b>・'+x.km.toFixed(x.km<10?1:0)+'km・'+esc(x.a||x.p):esc(x.a||x.p)}
var cache={};
function card(x){var key=x.i+(PG.near?"|"+S.o[0]:"");if(cache[key])return cache[key];var a;
  var hr=x.o?"/o/"+x.o:(x.u||"#");
  if(VIEW==="list")a=el('<a class="lr" href="'+esc(hr)+'" data-i="'+x.i+'" style="--gc:'+x.g[1]+'">'+(x.im?'<span class="lim" style="background-color:'+(x.th?avg(x.th):"var(--chip)")+'"><img alt="" loading="lazy" src="'+img(x)+'"></span>':"")+
   '<span class="lb2"><span class="lb">'+(x.g[0]?'<span class="g">'+esc(x.g[0])+'</span>':"")+'<span>'+esc(x.p)+'</span>'+badge(x)+'</span><b>'+esc(x.t)+'</b>'+(x.hk?'<small class="hk1">'+esc(x.hk)+'</small>':"")+
   '<small>'+[when(x),sub(x)].filter(Boolean).join("・")+'</small></span><i class="ch">›</i></a>');
  else a=el('<a class="cd" href="'+esc(hr)+'" data-i="'+x.i+'" style="--gc:'+x.g[1]+'"><div class="im" style="background-color:'+(x.th?avg(x.th):"var(--chip)")+'">'+(x.im?'<img alt="" loading="lazy" decoding="async" src="'+img(x)+'">':tile(x))+'</div>'+
   '<div class="lb">'+(x.g[0]?'<span class="g">'+esc(x.g[0])+'</span>':"")+'<span>'+esc(x.p)+'</span>'+badge(x)+'</div><h4>'+esc(x.t)+'</h4><div class="dt">'+(when(x)||"&nbsp;")+'</div><div class="vn">'+sub(x)+'</div></a>');
  var im=$("img",a);if(im){if(im.complete)im.classList.add("ld");else im.onload=function(){im.classList.add("ld")}}
  return cache[key]=a}
var grid=$("#grid"),first=true;
function go(anim){var L=pick(),show=L.slice(0,S.n),pr=S.p||RG.n;
  var tl=PG.tabs&&S.w?PG.tabs.filter(function(t){return t[0]===S.w})[0][1].replace(/\s\d+$/,""):(PG.near?(S.m?(S.m<60?S.m+"分":S.m/60+"時間").replace(".5時間","時間半")+"で行ける":"きょう開いている"):(PG.unit||"ぜんぶ"));
  $("#ch").innerHTML=esc(pr)+"・"+esc(tl)+" <b>"+L.length+"</b>"+(PG.cnt||"件");$("#cs").textContent=S.k==="_fav"?"保存した物":S.k&&K[S.k]?K[S.k][0]:(PG.near?S.o[0]+"から近い順":"");
  if(PG.near)$("#nn").textContent=L.length;
  if(anim&&!first)S_.countUp($("#ch b"));
  var frag=document.createDocumentFragment();show.forEach(function(x){frag.appendChild(card(x))});grid.replaceChildren(frag);
  if(!L.length)grid.innerHTML='<div class="none" style="grid-column:1/-1">'+esc(PG.none||"この条件の物は、いまはありません")+'</div>';
  $("#mr").innerHTML=L.length>S.n?'<button class="more">もっと見る（残り'+(L.length-S.n)+(PG.cnt||"件")+'）</button>':"";
  if(anim&&!RM)$$(".cd,.lr",grid).forEach(function(c,k){var n=c.getBoundingClientRect();if(n.top<innerHeight+40)c.animate([{opacity:0,transform:"translateY(12px)"},{opacity:1,transform:"none"}],{duration:380,delay:Math.min(k,8)*30,easing:"cubic-bezier(.2,.9,.25,1)",fill:"backwards"})});
  if(anim){var top=$("#sent").getBoundingClientRect().top+scrollY;if(scrollY>top)scrollTo({top:top,behavior:"smooth"})}
  first=false}
$("#mr").addEventListener("click",function(e){if(e.target.closest(".more")){S.n+=24;go(false)}});
sync();go(false);
new IntersectionObserver(function(e){$("#bar").classList.toggle("stuck",!e[0].isIntersecting)}).observe($("#sent"));

/* 1件の板 */
function openItem(x,from){if(!x)return;var mq=encodeURIComponent(x.mq||((x.v||x.t)+" "+(x.a||x.p))),big="";
  if(x.big)big=x.big;else if(x.s&&x.e){big=x.st==="up"?"あと"+diff(TD,x.s)+"日で始まります":x.left===0?"きょうまで":"終わりまで あと"+x.left+"日"}
  var tot=x.s&&x.e?Math.max(1,diff(x.s,x.e)):0,pc=tot&&x.st==="now"?Math.max(0,Math.min(tot,diff(x.s,TD)))/tot:0;
  S_.sheet((x.im?'<div class="pim" style="background-color:'+(x.th?avg(x.th):"var(--chip)")+'"><img src="'+img(x)+'" alt=""></div>':'<div class="pim0"></div>')+'<div class="bd" style="--gc:'+x.g[1]+'">'+
   '<div class="lb">'+(x.g[0]?'<span class="g">'+esc(x.g[0])+'</span>':"")+'<span>'+esc(x.p)+(x.a?'・'+esc(x.a):"")+'</span></div><h2>'+esc(x.t)+'</h2>'+(x.hk?'<p class="hk">'+esc(x.hk)+'</p>':"")+
   (x.s&&x.e?'<div class="per"><div class="row"><span>'+md(x.s)+'</span><span>'+md(x.e)+'</span></div><div class="tr"><i data-w="'+pc.toFixed(3)+'" style="background:'+x.g[1]+'"></i>'+(x.st==="now"?'<b style="left:'+(pc*100)+'%;border-color:'+x.g[1]+'"></b>':"")+'</div><div class="big">'+esc(big)+'</div></div>':big?'<div class="per"><div class="big">'+esc(big)+'</div></div>':"")+
   (PG.near&&x.mn!=null?'<div class="nrb"><b>約'+x.mn+'分</b><span>'+esc(S.o[0])+'から '+x.km.toFixed(1)+'km（直線距離からの目安）</span></div>':"")+
   (x.rows&&x.rows.length?'<dl class="kv">'+x.rows.map(function(r){return '<dt>'+esc(r[0])+'</dt><dd>'+esc(r[1])+'</dd>'}).join("")+'</dl>':"")+
   (x.ds?'<p class="ds">'+esc(x.ds)+'</p>':"")+(x.body?'<div class="bdy">'+esc(x.body)+'</div>':"")+
   (x.links&&x.links.length?'<div class="lks"><h3>'+esc(x.lh||"近くの宿")+'</h3>'+x.links.map(function(l){return '<a href="'+esc(l[1])+'" target="_blank" rel="noopener sponsored"><span><b>'+esc(l[0])+'</b><small>'+esc(l[2]||"")+'</small></span>'+(l[3]?'<em>'+esc(l[3])+'</em>':"")+'<i>›</i></a>'}).join("")+(x.lnote?'<p class="cr">'+esc(x.lnote)+'</p>':"")+'</div>':"")+(SD&&/^\/ranking/.test(location.pathname)?(function(){var m=x.links&&x.links[0]&&/\/machi\/([\w-]+)/.exec(x.links[0][1]),nm=m?x.links[0][0]:"";return '<a class="sdc" href="/moushikomi?lite=1'+(m?'&machi='+m[1]:'')+'&want='+encodeURIComponent("査定してほしい")+'" data-k="相談へ｜まちランキング">'+'<small>'+(nm?esc(nm)+'などで、':'')+'家を売る・住み替えるなら</small><b>今の家がいくらか、無料で相談</b><em>名字だけ・約1分・売るか決めていなくても大丈夫</em><i aria-hidden="true">→</i></a>'})():"")+
   '<div class="acts">'+(x.u?'<a class="pr" href="'+esc(x.u)+'" target="_blank" rel="noopener">'+esc(x.ub||"公式で確かめる")+'</a>':"")+(x.nomap?"":'<a href="https://www.google.com/maps/'+(PG.near&&x.ll?'dir/?api=1&origin='+S.o[1]+','+S.o[2]+'&destination='+x.ll[0]+','+x.ll[1]+'&travelmode=transit':'search/?api=1&query='+mq)+'" target="_blank" rel="noopener">'+(PG.near?"行き方":"地図で開く")+'</a>')+
   (x.o?'<a href="/o/'+x.o+'">くわしいページ</a>':x.sp?'<a href="'+esc(x.sp)+'">くわしいページ</a>':'<button data-share="1">送る</button>')+(PG.fav?'<button class="fv'+(FAV[x.id||x.t]?" on":"")+'" data-fav="1">'+S_.IC.star+'<span>'+(FAV[x.id||x.t]?"保存した":"保存")+'</span></button>':"")+'</div>'+
   (x.cr?'<p class="cr">写真：'+(x.cu?'<a href="'+esc(x.cu)+'" target="_blank" rel="noopener">'+esc(x.cr)+'</a>':esc(x.cr))+'</p>':"")+(x.src?'<p class="cr">出どころ：<a href="'+esc(x.src)+'" target="_blank" rel="noopener">公式の発表</a></p>':"")+'</div>',from,function(box){
     var f=$("[data-fav]",box);if(f)f.onclick=function(){var k=x.id||x.t;if(FAV[k])delete FAV[k];else FAV[k]=1;favSave();f.classList.toggle("on",!!FAV[k]);$("span",f).textContent=FAV[k]?"保存した":"保存";drawChips()}})}
grid.addEventListener("click",function(e){var a=e.target.closest(".cd,.lr");if(!a||e.metaKey||e.ctrlKey)return;e.preventDefault();openItem(BYI[a.dataset.i],$(".im,.lim",a))});
var k0=Q.get("i");if(k0){var x0=IT.filter(function(x){return x.id===k0})[0];if(x0)setTimeout(function(){openItem(x0)},300)}
S_.onNav(function(a){if(a==="top")scrollTo({top:0,behavior:"smooth"});else if(a==="list")scrollTo({top:$("#sent").getBoundingClientRect().top+scrollY,behavior:"smooth"});else if(a==="geo"){var g=$("#geo2");if(g)g.click()}else if(a.indexOf("w=")===0){var b=$('#tab button[data-v="'+a.slice(2)+'"]');if(b)b.click();S_.navCur(a)}else if(a==="fav"){S.k="_fav";S.w="";S.n=24;sync();go(true);S_.navCur(a);scrollTo({top:$("#sent").getBoundingClientRect().top+scrollY,behavior:"smooth"})}});
/* 11/22 見本 kn：開店閉店の絞り込みが3段→「種類」はたたんで、件数の横の「種類で絞る」で開く */
/* 11/22 kn：いまから行けるの長い説明は1行にたたむ */
if(document.documentElement.classList.contains("lk-kn")){var _ln=$(".lnote");if(_ln&&_ln.textContent.length>60){var _d=document.createElement("details");_d.className="lnd";_d.innerHTML='<summary>かかる時間・開いている時間は目安です</summary>';var _p=document.createElement("p");_p.innerHTML=_ln.innerHTML;_d.appendChild(_p);_ln.replaceWith(_d)}}
if((PG.tabs||PG.near)&&document.documentElement.classList.contains("lk-kn")&&$("#chips")){var _bar=$("#bar"),_cs=$("#cs");if(!S.k)_bar.classList.add("kf");
  if(_cs){var kb=document.createElement("button");kb.type="button";kb.className="kfb";kb.textContent="種類で絞る";_cs.parentNode.insertBefore(kb,_cs);
    kb.addEventListener("click",function(){_bar.classList.toggle("kf");kb.classList.toggle("on",!_bar.classList.contains("kf"))});kb.classList.toggle("on",!_bar.classList.contains("kf"))}}
if(PG.tabs)S_.navCur("w="+S.w);S_.ready();
})();
