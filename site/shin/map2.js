/* 11/20 owner「地図何とかならんかな？クオリティあげたい・大阪だけとか選べる方が使いやすい」→ おでかけの地図を作り直し（見本：?map2=1）。
   役目＝行きたい所が地図ですぐ見つかる・府県を1タップで選べる。
   こだわり＝写真のピン（近い所はまとまって数を出し、寄ると分かれる）・寄ると町の名前が出る本物の地図の細かさ・「この範囲の◯か所」が下のカードに並ぶ。
   形は /shin/map.json（tools/shin/mapgen.py が市町村の形から作る）を開いた時だけ読む。関東も同じファイル（形は site/shin/map.json）。 */
(function(){
"use strict";
var S_=window.SHIN,O=S_.od,$=S_.$,$$=S_.$$,el=S_.el,esc=S_.esc,RM=S_.RM,RG=S_.reg,PREF=RG.pref,S=O.S;
var miss=0,mseg=null,M=null,box=null,vb={x:0,y:0,w:200,h:250},W=1,H=1,ALL=null,L=[],CL=[],sel=null,me=null,inView=[],busy=0,moved=false,lastUser=0;
var WL={now:"開催中",we:"今週末",end:"まもなく終了",up:"これから",td:"きょうまで",new:"もうすぐ始まる"};
var SVGNS="http://www.w3.org/2000/svg";

function open(){
  if(!box)build();
  history.pushState({mp:1},"");box.classList.add("op");document.documentElement.classList.add("m2op");document.documentElement.style.overflow=document.body.style.overflow="hidden";S_.navCur("map");
  if(!M){$("#m2n").textContent="地図を読みこんでいます";fetch("/shin/map.json?v=1120a").then(function(r){return r.json()}).then(function(j){M=j;draw();refresh(true)}).catch(function(){$("#m2n").textContent="地図を読みこめませんでした"});}
  else refresh(true)}
function close(back){if(!box||!box.classList.contains("op"))return;box.classList.remove("op");document.documentElement.classList.remove("m2op");document.documentElement.style.overflow=document.body.style.overflow="";if(back!==false&&history.state&&history.state.mp)history.back();S_.navCur(S.w);/* 地図で選んだ府県・いつを一覧の URL にも（戻ったあと） */setTimeout(O.saveQ,60)}
addEventListener("popstate",function(){if(box&&box.classList.contains("op")&&!(history.state&&(history.state.mp||history.state.sh)))close(false)});
addEventListener("keydown",function(e){if(e.key==="Escape"&&box&&box.classList.contains("op")&&!document.querySelector(".sh.op"))close()});

function build(){
  box=el('<div class="m2" id="m2" role="dialog" aria-label="'+esc(RG.n)+'おでかけマップ">'+
   '<div class="m2h"><div class="m2t"><b>'+esc(RG.n)+'おでかけマップ</b><button class="m2x" aria-label="地図を閉じる"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>'+
   '<div class="seg fit" id="m2p"></div><div class="m2w" id="m2w"></div></div>'+
   '<div class="m2v" id="m2v"><svg id="m2s" preserveAspectRatio="none"><defs><linearGradient id="m2g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F6C66B"/><stop offset="1" stop-color="#F29E4C"/></linearGradient></defs><g id="m2b"></g></svg>'+
   '<div class="m2lb" id="m2lb"></div><div class="m2pn" id="m2pn"></div>'+
   '<div class="m2n"><span id="m2n"></span><button id="m2gx" hidden></button></div>'+
   '<div class="m2z"><button data-z="2" aria-label="寄る"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg></button><button data-z=".5" aria-label="引く"><svg viewBox="0 0 24 24"><path d="M5 12h14"/></svg></button><button data-z="me" aria-label="いまいる所"><svg viewBox="0 0 24 24"><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/><circle cx="12" cy="12" r="5.5"/><circle cx="12" cy="12" r="1.6" class="f"/></svg></button></div>'+
   '<p class="m2toast" id="m2toast"></p></div>'+
   '<div class="m2c" id="m2c"></div></div>');
  (document.getElementById("app")||document.body).appendChild(box);/* 下のバー（#app の中）より下に置く */
  $(".m2x",box).onclick=function(){close()};
  mseg=S_.seg($("#m2p"),[["",RG.n]].concat(PREF.map(function(p){return [p,p]})),S.p,function(v){S.p=v;O.changed();S_.navCur("map");refresh(true)});
  drawW();
  $("#m2w").addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;S.w=b.dataset.w;O.changed();S_.navCur("map");drawW();refresh(false)});
  $("#m2gx").onclick=function(){S.g="";O.changed();S_.navCur("map");refresh(false)};
  $(".m2z",box).addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;var z=b.dataset.z;if(z==="me"){locate();return}lastUser=1;zoomAt(+z,vb.x+vb.w/2,vb.y+vb.h/2,true)});
  /* 11/21 縦の指の動きで画面全体が動く（iPhone・Instagram）→ 地図の外の縦の動きは止める。横のカードは横だけ */
  var ty0=0,tx0=0;box.addEventListener("touchstart",function(e){var t=e.touches[0];tx0=t.clientX;ty0=t.clientY},{passive:true});
  box.addEventListener("touchmove",function(e){if(e.target.closest(".m2v"))return;var t=e.touches[0];if(e.touches.length>1||Math.abs(t.clientY-ty0)>Math.abs(t.clientX-tx0))e.preventDefault()},{passive:false});
  $("#m2c").addEventListener("scroll",function(){clearTimeout(box._t);box._t=setTimeout(function(){var c=$("#m2c"),f=c.querySelector(".mcd");if(!f)return;var w=f.offsetWidth+10,k=Math.max(0,Math.min(inView.length-1,Math.round(c.scrollLeft/w)));if(inView[k]&&inView[k]!==sel)select(inView[k],false)},90)},{passive:true});
  $("#m2c").addEventListener("click",function(e){var a=e.target.closest(".mcd");if(!a)return;e.preventDefault();var x=O.byi[a.dataset.i];if(x)O.openItem(x)});
  gestures();
  addEventListener("resize",function(){if(box.classList.contains("op")){size();place()}});
}
function drawW(){var c=O.counts();$("#m2w").innerHTML=[["now","開催中"],["we","今週末"],["end","まもなく終了"],["up","これから"]].map(function(w){return '<button data-w="'+w[0]+'" class="'+(S.w===w[0]?"on":"")+'">'+w[1]+'<small>'+c[w[0]]+'</small></button>'}).join("")}

/* 形を描く（陸は府県ごと・市町村のさかいは髪の毛の細さ・府県のさかいは少し濃く・選んだ府県のふちだけ琥珀の線） */
function draw(){var g=$("#m2b"),h='<rect x="-400" y="-400" width="1200" height="1200" class="sea"/>';
  h+='<g class="nb">'+M.nb.map(function(d){return '<path d="'+d+'"/>'}).join("")+'</g>';
  h+='<g class="ld">'+Object.keys(M.land).map(function(p){return '<path data-p="'+p+'" d="'+M.land[p]+'"/>'}).join("")+'</g>';
  h+=M.lake.map(function(d){return '<path class="lk" d="'+d+'"/>'}).join("");
  h+='<path class="mb" d="'+M.mb+'"/><path class="pb" d="'+M.pb+'"/>'+Object.keys(M.ob).map(function(p){return '<path class="cs" d="'+M.ob[p]+'"/>'}).join("");
  h+='<path class="ol" id="m2ol" d=""/>';
  g.innerHTML=h;$$("#m2b path",box).forEach(function(p){p.setAttribute("vector-effect","non-scaling-stroke")});
  var lb='';PREF.forEach(function(p){var c=RG.lb[p];if(c)lb+='<span class="pl" data-x="'+c[0]+'" data-y="'+c[1]+'" data-p="'+p+'">'+esc(p)+'</span>'});
  M.lab.forEach(function(a){lb+='<span class="cl r'+a[4]+'" data-x="'+a[1]+'" data-y="'+a[2]+'" data-p="'+a[3]+'" data-r="'+a[4]+'">'+esc(a[0])+'</span>'});
  $("#m2lb").innerHTML=lb;
  /* 陸を押す＝その府県を選ぶ */
  $("#m2b").addEventListener("click",function(e){if(moved)return;var p=e.target.closest(".ld path");if(!p||p.dataset.p===S.p)return;S.p=p.dataset.p;mseg(S.p,true);O.changed();S_.navCur("map");refresh(true)});
}
function regionBox(){if(S.p&&M.bb[S.p])return M.bb[S.p];var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;PREF.forEach(function(p){var b=M.bb[p];if(!b)return;x0=Math.min(x0,b[0]);y0=Math.min(y0,b[1]);x1=Math.max(x1,b[0]+b[2]);y1=Math.max(y1,b[1]+b[3])});return [x0,y0,x1-x0,y1-y0]}

/* 絞り込みが変わった：ピン・ふち・数を作り直す。fly=true なら選んだ府県へ寄る */
function refresh(fly){if(!M)return;size();drawW();ALL=O.pick().filter(function(x){return x.xy});
  $$(".ld path",box).forEach(function(p){p.classList.toggle("dim",!!S.p&&p.dataset.p!==S.p)});
  $("#m2ol").setAttribute("d",S.p&&M.ol[S.p]?M.ol[S.p]:"");$("#m2ol").setAttribute("stroke","url(#m2g)");
  $$(".pl",box).forEach(function(l){l.classList.toggle("on",l.dataset.p===S.p)});
  var gx=$("#m2gx");if(S.g){gx.hidden=false;gx.innerHTML=esc(O.gname(S.g))+'だけ<svg viewBox="0 0 24 24"><path d="M7 7l10 10M17 7L7 17"/></svg>'}else gx.hidden=true;
  sel=null;
  if(fly){var b=regionBox();lastUser=0;/* まわりに余白（左上の数の札・右の＋－ボタンにかからない） */fit(b[0]-b[2]*.03-1,b[1]-b[3]*.09-2,b[2]*1.17+2,b[3]*1.13+4,!box._shown||RM);box._shown=1}
  cluster();list(true)}

function size(){var v=$("#m2v");W=v.clientWidth||1;H=v.clientHeight||1}
function fit(x,y,w,h,inst){var r=W/H;if(w/h<r){var nw=h*r;x-=(nw-w)/2;w=nw}else{var nh=w/r;y-=(nh-h)/2;h=nh}
  /* 下のカードと上の数の帯にかからないように、少し下げる余白 */
  if(inst){vb={x:x,y:y,w:w,h:h};setVB();settle();return}
  var a={x:vb.x,y:vb.y,w:vb.w,h:vb.h},t0=performance.now();busy++;
  (function f(t){var k=Math.min(1,(t-t0)/560),e=1-Math.pow(1-k,3);vb={x:a.x+(x-a.x)*e,y:a.y+(y-a.y)*e,w:a.w+(w-a.w)*e,h:a.h+(h-a.h)*e};setVB();if(k<1)requestAnimationFrame(f);else{busy--;settle()}})(t0)}
function zoomAt(z,cx,cy,anim){var w=Math.max(9,Math.min(320,vb.w/z)),h=w*H/W;var x=cx-(cx-vb.x)*w/vb.w,y=cy-(cy-vb.y)*h/vb.h;if(anim)fit(x,y,w,h);else{vb={x:x,y:y,w:w,h:h};setVB()}}
function setVB(){$("#m2s").setAttribute("viewBox",vb.x+" "+vb.y+" "+vb.w+" "+vb.h);place()}
function sx(x){return (x-vb.x)/vb.w*W}function sy(y){return (y-vb.y)/vb.h*H}

/* 名前とピンを画面の場所に置く（動かしている間は置き直すだけ。止まったらまとめ直す） */
function ovw(){if(S.p||!M)return false;var b=fullBox();return vb.w>b[2]*.72}
var FB=null;function fullBox(){if(FB)return FB;var s=S.p;S.p="";FB=regionBox();S.p=s;return FB}
function place(){var k=vb.w,ov=CL.ov,P=ov?[]:CL.map(function(c){return [sx(c.ax),sy(c.ay),c.m.length>1?20:9]});
  $$("#m2lb span",box).forEach(function(l){var r=+l.dataset.r||0,show=ov?false:r===0?k>70:(r===1?k<130:r===2?k<62:k<30);if(r&&S.p&&l.dataset.p!==S.p&&k>40)show=false;
    if(!show){l.style.display="none";return}var X=sx(+l.dataset.x),Y=sy(+l.dataset.y);if(X<-60||X>W+60||Y<-20||Y>H+20){l.style.display="none";return}
    /* 点・数字の丸と重なる名前は出さない */var hw=l.textContent.length*(r===0?8:6)+4;for(var i=0;i<P.length;i++){if(Math.abs(P[i][0]-X)<hw+P[i][2]&&Math.abs(P[i][1]-Y)<P[i][2]+8){l.style.display="none";return}}
    l.style.display="";l.style.transform="translate("+X.toFixed(1)+"px,"+Y.toFixed(1)+"px) translate(-50%,-50%)"});
  CL.forEach(function(c){c.el.style.transform="translate("+sx(c.ax).toFixed(1)+"px,"+sy(c.ay).toFixed(1)+"px)"});
  if(me&&me.el)me.el.style.transform="translate("+sx(me.xy[0]).toFixed(1)+"px,"+sy(me.xy[1]).toFixed(1)+"px)"}
var stT=0;function settle(){clearTimeout(stT);stT=setTimeout(function(){if(busy)return;cluster();if(lastUser)list(false);lastUser=0},140)}

/* 近いピンをまとめる（画面で 38px 以内）。並びは一覧と同じ（写真あり・人気が先）なので、まとまりの顔はいちばん良い物 */
/* 11/20 owner「集合体恐怖症の人は見れないね」→ 写真の丸を並べない。1か所＝小さな点、まとまり＝数字だけの丸。写真は選んだ1か所だけ。 */
function cluster(){var R=46,out=[];
  /* 全体を見ている時は、府県ごとに「大阪 31」を1つだけ。押すとその府県へ */
  if(ovw()){var pn0=$("#m2pn");pn0.textContent="";var fr=document.createDocumentFragment(),cnt={};ALL.forEach(function(x){cnt[x.p]=(cnt[x.p]||0)+1});
    var L0=PREF.filter(function(p){return RG.lb[p]}).map(function(p,k){var b=document.createElement("button");b.className="pin pref"+(cnt[p]?"":" zero");b.setAttribute("aria-label",p+" "+(cnt[p]||0)+"か所");
      b.innerHTML='<span class="pc"><b>'+esc(p)+'</b><small>'+(cnt[p]||0)+'</small></span>';if(!RM&&!box._pinned)b.style.animationDelay=k*40+"ms";
      b.onclick=function(e){if(moved)return;e.stopPropagation();S.p=p;mseg(p,true);O.changed();S_.navCur("map");refresh(true)};fr.appendChild(b);
      return {ax:RG.lb[p][0],ay:RG.lb[p][1],m:[],el:b}});
    if(me){me.el=el('<i class="me" aria-hidden="true"></i>');fr.appendChild(me.el)}
    pn0.appendChild(fr);CL=L0;CL.ov=1;box._pinned=1;place();return}
  ALL.forEach(function(x){var X=sx(x.xy[0]),Y=sy(x.xy[1]);for(var i=0;i<out.length;i++){var c=out[i];if(Math.abs(c.X-X)<R&&Math.abs(c.Y-Y)<R){c.m.push(x);return}}out.push({X:X,Y:Y,ax:x.xy[0],ay:x.xy[1],m:[x]})});
  var pn=$("#m2pn");pn.textContent="";var frag=document.createDocumentFragment();
  out.forEach(function(c,k){var x=c.m[0],n=c.m.length;
    var b=document.createElement("button");b.className="pin"+(n>1?" grp":" one");
    b.setAttribute("aria-label",n>1?x.t+"ほか"+(n-1)+"か所":x.t);
    if(n>1){var d=Math.round(26+Math.min(14,Math.log(n)*5));b.style.setProperty("--d",d+"px");b.innerHTML='<span class="pc" style="width:'+d+'px;height:'+d+'px;margin:-'+d/2+'px 0 0 -'+d/2+'px">'+n+'</span>'}
    else b.innerHTML='<span class="pc"></span>';
    if(!RM&&!box._pinned)b.style.animationDelay=Math.min(k,30)*14+"ms";
    b.onclick=function(e){if(moved)return;e.stopPropagation();tapCluster(c)};c.el=b;frag.appendChild(b)});
  if(me){me.el=el('<i class="me" aria-hidden="true"></i>');frag.appendChild(me.el)}
  pn.appendChild(frag);CL=out;CL.ov=0;box._pinned=1;if(sel)mark(sel);place()}
/* 選んだ1か所だけ写真と名前を出す */
function mark(x){CL.forEach(function(c){var on=c.m.indexOf(x)>=0;c.el.classList.toggle("on",on);var f=c.el.querySelector(".pf2");if(f)f.remove();
  if(on){c.el.insertAdjacentHTML("beforeend",'<span class="pf2">'+(x.im?'<img src="'+O.img(x)+'" alt="">':'<span class="pi2"><svg viewBox="0 0 24 24">'+(O.icon(x.k)||"")+'</svg></span>')+'<b>'+esc(x.t)+'</b></span>');c.el.parentNode.appendChild(c.el)}})}
function tapCluster(c){if(c.m.length===1){var x=c.m[0];if(sel===x){O.openItem(x);return}select(x,true);return}
  var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;c.m.forEach(function(x){x0=Math.min(x0,x.xy[0]);y0=Math.min(y0,x.xy[1]);x1=Math.max(x1,x.xy[0]);y1=Math.max(y1,x.xy[1])});
  var w=Math.max(x1-x0,0),h=Math.max(y1-y0,0);
  if(w<.35&&h<.35||vb.w<=9.5){/* 同じ場所に何か所も（同じ会場など）＝寄らずに下のカードに並べる */inView=c.m.slice();drawCards();select(c.m[0],true);return}
  /* 11/20 本番で見て：2か所の丸を押すと寄りすぎて、右上の＋－に写真がかかった→ 少なくとも 約8km 四方は見せる */lastUser=1;var pw=Math.max(w*.5,4),ph=Math.max(h*.5,4);fit(x0-pw,y0-ph,w+pw*2,h+ph*2)}

/* 下のカード：いま地図に見えている所だけ（引いた時は全部） */
function list(all){var m=.02;inView=ALL.filter(function(x){if(all)return true;var X=sx(x.xy[0]),Y=sy(x.xy[1]);return X>=-W*m&&X<=W*(1+m)&&Y>=-H*m&&Y<=H*(1+m)});
  if(me)inView.sort(function(a,b){return dist(a)-dist(b)});miss=all?O.pick().length-ALL.length:0;drawCards();
  var n=inView.length,pr=S.p||RG.n;$("#m2n").innerHTML=(all?esc(pr)+"・"+WL[S.w]:"この範囲・"+WL[S.w])+" <b>"+n+"</b>か所";
  if(n&&inView.indexOf(sel)<0)select(inView[0],false,true)}
function dist(x){if(!me)return 0;return Math.hypot(x.xy[0]-me.xy[0],x.xy[1]-me.xy[1])*1.113}
function km(x){var d=dist(x);return d<1?Math.round(d*10)/10+"km":Math.round(d)+"km"}
function drawCards(){var c=$("#m2c");c.scrollLeft=0;
  if(!inView.length){c.innerHTML='<p class="m2e">'+(ALL.length?"この範囲にはありません。引くか、ほかの府県を選んでください":"この条件のおでかけは、いまはありません")+'</p>';return}
  c.innerHTML=inView.slice(0,60).map(function(x){return '<a class="mcd" href="'+(x.o?"/o/"+x.o:esc(x.u))+'" data-i="'+x.i+'" style="--gc:'+x.g[1]+'"><span class="mim" style="background-color:'+(x.th?O.avg(x.th):x.g[2])+'">'+(x.im?'<img src="'+O.img(x)+'" alt="" loading="lazy">':O.tile(x))+'</span><span class="mtx"><span class="lb"><span class="g">'+x.g[3]+'</span><span>'+esc(x.p)+'</span>'+O.lt(x)+'</span><b>'+esc(x.t)+'</b><small>'+O.when(x)+(me?'・ここから'+km(x):'・'+esc(x.v||x.a||""))+'</small></span></a>'}).join("")+(inView.length>60?'<p class="m2e">ほか '+(inView.length-60)+'か所。寄ると分かれます</p>':"")+(miss>0?'<p class="m2e">ほか '+miss+'件は地図に場所が出ていません（一覧で見られます）</p>':"")}
function select(x,fromPin,quiet){sel=x;var k=inView.indexOf(x);
  mark(x);
  if(me&&me.el)me.el.parentNode.appendChild(me.el);
  if(fromPin&&k>=0){var c=$("#m2c"),a=c.children[k];if(a)c.scrollTo({left:a.offsetLeft-(c.clientWidth-a.offsetWidth)/2,behavior:RM?"auto":"smooth"})}
  if(!quiet){var X=sx(x.xy[0]),Y=sy(x.xy[1]);if(X<W*.1||X>W*.9||Y<H*.12||Y>H*.88)fit(x.xy[0]-vb.w/2,x.xy[1]-vb.h/2,vb.w,vb.h)}}

/* いまいる所（スマホの位置。使うのはこの画面の中だけ・どこにも送らない） */
function locate(){var t=$("#m2toast");if(!navigator.geolocation){toast("この端末では位置が使えません");return}toast("いまいる所を探しています");
  navigator.geolocation.getCurrentPosition(function(p){var j=M.pj,xy=[(p.coords.longitude-j[0])*j[1]+j[2],(j[3]-p.coords.latitude)*j[4]+j[5]],b=regionBox(),all=M.bb;
    var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;Object.keys(all).forEach(function(k){var q=all[k];x0=Math.min(x0,q[0]);y0=Math.min(y0,q[1]);x1=Math.max(x1,q[0]+q[2]);y1=Math.max(y1,q[1]+q[3])});
    if(xy[0]<x0-15||xy[0]>x1+15||xy[1]<y0-15||xy[1]>y1+15){toast("いまは"+RG.n+"の外にいるようです");return}
    me={xy:xy};if(S.p){S.p="";mseg("",true);O.changed();S_.navCur("map");ALL=O.pick().filter(function(x){return x.xy});$$(".ld path",box).forEach(function(p){p.classList.remove("dim")});$("#m2ol").setAttribute("d","")}
    toast("近い順に並べました");lastUser=1;fit(xy[0]-11,xy[1]-11,22,22)},function(){toast("位置が使えませんでした（設定で許可すると近い順に並びます）")},{enableHighAccuracy:false,timeout:9000,maximumAge:300000})}
function toast(s){var t=$("#m2toast");t.textContent=s;t.classList.add("on");clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove("on")},2600)}

/* 指で動かす・2本指で寄る・ダブルタップで寄る・ホイール */
function gestures(){var v=$("#m2v"),pts={},st=null,tap0=0;
  function toSvg(cx,cy){var r=v.getBoundingClientRect();return [vb.x+(cx-r.left)/W*vb.w,vb.y+(cy-r.top)/H*vb.h]}
  function snap(){st={vb:{x:vb.x,y:vb.y,w:vb.w,h:vb.h},pts:JSON.parse(JSON.stringify(pts))}}
  v.addEventListener("pointerdown",function(e){if(e.target.closest(".m2z,.m2n"))return;pts[e.pointerId]=[e.clientX,e.clientY];if(Object.keys(pts).length===1)moved=false;snap()});
  v.addEventListener("pointermove",function(e){if(!pts[e.pointerId]||!st)return;pts[e.pointerId]=[e.clientX,e.clientY];var ids=Object.keys(pts);
    if(ids.length===1){var p0=st.pts[ids[0]];if(!p0)return;var dx=e.clientX-p0[0],dy=e.clientY-p0[1];if(Math.abs(dx)+Math.abs(dy)>7)moved=true;if(!moved)return;vb={x:st.vb.x-dx/W*vb.w,y:st.vb.y-dy/H*vb.h,w:vb.w,h:vb.h};setVB()}
    else{var a0=st.pts[ids[0]],b0=st.pts[ids[1]],a1=pts[ids[0]],b1=pts[ids[1]];if(!a0||!b0)return;moved=true;var d0=Math.hypot(a0[0]-b0[0],a0[1]-b0[1]),d1=Math.hypot(a1[0]-b1[0],a1[1]-b1[1]);
      vb={x:st.vb.x,y:st.vb.y,w:st.vb.w,h:st.vb.h};var c=toSvg((a0[0]+b0[0])/2,(a0[1]+b0[1])/2);zoomAt(d1/Math.max(1,d0),c[0],c[1],false);
      var m0=[(a0[0]+b0[0])/2,(a0[1]+b0[1])/2],m1=[(a1[0]+b1[0])/2,(a1[1]+b1[1])/2];vb.x-=(m1[0]-m0[0])/W*vb.w;vb.y-=(m1[1]-m0[1])/H*vb.h;setVB()}});
  function up(e){if(!pts[e.pointerId])return;delete pts[e.pointerId];snap();if(!Object.keys(pts).length&&moved){lastUser=1;settle()}
    if(e.type==="pointerup"&&!moved&&!e.target.closest(".pin")){var t=performance.now();if(t-tap0<300){var c=toSvg(e.clientX,e.clientY);lastUser=1;zoomAt(2,c[0],c[1],true);tap0=0}else tap0=t}}
  v.addEventListener("pointerup",up);v.addEventListener("pointercancel",up);v.addEventListener("pointerleave",up);
  v.addEventListener("wheel",function(e){e.preventDefault();var c=toSvg(e.clientX,e.clientY);zoomAt(e.deltaY<0?1.18:1/1.18,c[0],c[1],false);lastUser=1;settle()},{passive:false})}

O.mapOpen=open;O.mapClose=close;
})();
