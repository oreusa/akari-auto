/* 新しいHP：おかいもの。役目＝楽天・Yahoo!・Amazon を1つの画面で見比べる。こだわり＝いちばん安いお店が光る。
   値段は燈が毎日作る okai-shin.json。ページに入れた物をすぐ出し、新しい物が取れたら差し替える。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,RM=S_.RM,D=S_.data;
var SC={"楽天":"#BF0000","Yahoo!":"#6B3FD4","Amazon":"#E38800"};
var MYK="kau_my",MY=[];try{MY=JSON.parse(localStorage.getItem(MYK)||"[]")}catch(e){MY=[]}
function saveMy(){try{localStorage.setItem(MYK,JSON.stringify(MY))}catch(e){}}
function yen(v){return Math.round(v).toLocaleString()+"円"}
function per(c,o){if(c.unit!=="1L・1kg")return c.unit+"あたり";return o.ut||(/\d\s*(kg|g)(?![a-z])/i.test(o.a||"")?"1kgあたり":"1Lあたり")}
function icon(k){return '<svg viewBox="0 0 24 24">'+(D.ic[k]||"")+'</svg>'}
function amzUrl(c){return "https://www.amazon.co.jp/s?k="+encodeURIComponent(c.nm+(c.unit==="1L・1kg"?" 詰め替え":""))+"&tag="+D.amz}
function drop(o){var h=o.h;if(!h||h.length<5)return 0;var mx=Math.max.apply(null,h),mn=Math.min.apply(null,h);return o.p<=mn&&mx>=o.p*1.03?Math.round((1-o.p/mx)*100):0}
function bfOf(k){return (D.bf||[]).filter(function(b){return b.k===k})}
/* お店ごとのいちばん安い物 */
function shops(c){var b={};c.o.forEach(function(o){if(!b[o.w]||o.u<b[o.w].u)b[o.w]=o});return b}
function stat(){var win={"楽天":0,"Yahoo!":0},dr=0;D.cats.forEach(function(c){c.best=c.o[0];c.sh=shops(c);win[c.best.w]=(win[c.best.w]||0)+1;c.dr=0;c.o.forEach(function(o){var d=drop(o);if(d){dr++;c.dr=Math.max(c.dr,d)}})});return {win:win,dr:dr}}
var ST=stat(),BY={};D.cats.forEach(function(c){BY[c.k]=c});
function when(at){var m=/(\d{4})-(\d\d)-(\d\d) (\d\d:\d\d)/.exec(at||"");return m?(+m[2])+"月"+(+m[3])+"日 "+m[4]:""}
function kana(s){return String(s||"").replace(/[ァ-ン]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-96)}).replace(/\s/g,"")}
var SYN={"といれ":"tp","といぺ":"tp","てぃっしゅ":"tissue","はなかみ":"tissue","おむつ":"diaper","おしり":"wipes","みず":"water","すい":"water","たんさん":"soda","こめ":"rice","おこめ":"rice","ちゃ":"tea","おちゃ":"tea","こーひー":"coffee","まめ":"beans","せんざい":"detergent","せんたく":"detergent","じゅうなん":"softener","しゃんぷー":"shampoo","ぼでぃ":"bodysoap","しょっき":"dish","だいどころ":"dish","ごみ":"trash","ぶくろ":"trash","でんち":"battery","ますく":"mask","ぱすた":"pasta","すぱげ":"pasta","いぬ":"dogfood","どっぐ":"dogfood","ねこ":"catfood","きゃっと":"catfood"};

S_.main.innerHTML='<div class="wrap"><section class="hero"><h1 class="h1t">日用品の値段くらべ</h1><p class="h1p">楽天とYahoo!ショッピングの値段を1つの画面で（Amazonは押すと検索で開きます）</p>'+(document.documentElement.classList.contains("lk-kn")?'<p class="kno kno2"><span>ほかに</span><a href="/nesage">値下がりした物</a><a href="/furusato">ふるさと納税</a></p>':'')+
 '<div class="fnd"><label class="fin">'+S_.IC.find+'<input id="q" type="search" placeholder="品物で探す（例：ティッシュ、おむつ）" autocomplete="off" enterkeyhint="search"></label><div class="sug" id="sug"></div></div>'+
 '<div class="tiles" id="tl"></div><p class="upd"><i class="dot"></i><span id="at"></span></p></section>'+
 '<div id="bfx"></div><div id="myx"></div>'+
 '<div id="sent"></div><div class="bar" id="bar"><div class="seg" id="seg"></div></div>'+
 '<div class="cnt"><h3 id="ch"></h3><small>いちばん安い値段（送料込み）</small></div><div class="kg" id="kg"></div>'+
 '<p class="cr kcr">1L・1枚など同じ量あたりの値段で比べています。値段は調べた時のもので、お店で変わることがあります。お店へのリンクは広告（PR）です。</p></div>';

function head(){$("#tl").innerHTML=
  '<button data-a="w"><small>楽天の方が安い</small><b><span data-n="'+(ST.win["楽天"]||0)+'">0</span><u>/ '+D.cats.length+'種類</u></b></button>'+
  '<button data-a="w"><small>Yahoo!の方が安い</small><b><span data-n="'+(ST.win["Yahoo!"]||0)+'">0</span><u>/ '+D.cats.length+'種類</u></b></button>'+
  '<button data-a="drop"><small>値下がり中</small><b><span data-n="'+ST.dr+'">0</span><u>件</u></b><i>→</i></button>';
  $("#at").textContent=when(D.at)+" に調べた値段・"+D.cats.reduce(function(s,c){return s+c.o.length},0)+"件から";S_.counts($("#tl"))}
head();
$("#tl").addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;if(b.dataset.a==="drop")openDrop();else{var top=$("#sent").getBoundingClientRect().top+scrollY;scrollTo({top:top,behavior:"smooth"})}});

/* 探す */
var q=$("#q"),sug=$("#sug");
function hit(v){v=kana(v);if(!v)return [];var out=[];D.cats.forEach(function(c){if(kana(c.nm).indexOf(v)>=0)out.push(c)});
  Object.keys(SYN).forEach(function(s){if((s.indexOf(v)===0||v.indexOf(s)===0)&&BY[SYN[s]]&&out.indexOf(BY[SYN[s]])<0)out.push(BY[SYN[s]])});return out.slice(0,6)}
q.addEventListener("input",function(){var v=q.value.trim();if(!v){sug.classList.remove("op");return}var L=hit(v);
  sug.innerHTML=L.length?L.map(function(c){return '<button data-k="'+c.k+'"><b>'+esc(c.nm)+'</b><small>'+per(c,c.best)+'</small><span>'+yen(c.best.u)+'〜</span></button>'}).join(""):'<p>まだ調べていない品物です。下の21種類から選んでください</p>';sug.classList.add("op")});
sug.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;q.blur();sug.classList.remove("op");openKind(BY[b.dataset.k])});

/* ブラックフライデー（夜が確かめた行だけ・11/25 1:59 まで） */
function bfBox(){var L=D.bf||[],end=D.bfEnd&&new Date(D.bfEnd.replace(" ","T")+":00+09:00");if(!L.length||(end&&Date.now()>end)){$("#bfx").innerHTML="";return}
  $("#bfx").innerHTML='<section class="bfx"><div class="cnt"><h3>ブラックフライデーで安い物</h3><small>11/25（水）1:59まで</small></div><div class="bfs">'+L.slice(0,12).map(function(b){
    return '<a href="'+esc(b.url)+'" target="_blank" rel="noopener sponsored" style="--sc:'+(SC[b.w]||"#888")+'"><span class="sp">'+esc(b.w)+'</span><b>'+esc(b.n)+'</b><small>'+esc(b.q||"")+'</small><strong>'+esc(b.p)+'</strong>'+(b.cp?'<em>'+esc(b.cp)+'</em>':"")+'<i>'+when(b.at).replace(/^\d+月\d+日 /,"")+' に確かめた</i></a>'}).join("")+'</div></section>'}
bfBox();

/* いつもの物（この端末だけに覚える） */
function myBox(){var L=MY.map(function(k){return BY[k]}).filter(Boolean);
  $("#myx").innerHTML=L.length?'<section class="myx"><div class="cnt"><h3>いつもの物</h3><small>この端末に保存</small></div><div class="kg">'+L.map(card).join("")+'</div></section>':"";
  if(L.length)S_.counts($("#myx"))}
myBox();

/* 種類のカード：いちばん安い値段と、お店ごとの棒 */
function card(c){var b=c.best,sh=c.sh,mx=0;Object.keys(sh).forEach(function(w){mx=Math.max(mx,sh[w].u)});
  return '<button class="kc" data-k="'+c.k+'"><span class="ki">'+icon(c.k)+'</span>'+(c.dr?'<span class="dr">値下がり</span>':"")+'<b class="knm">'+esc(c.nm)+'</b>'+
   '<span class="kp"><small>'+per(c,b)+'</small><strong><span data-n="'+Math.round(b.u)+'" data-f="1">0</span>円</strong></span>'+
   '<span class="ks">'+["楽天","Yahoo!"].map(function(w){var o=sh[w];return o?'<span class="'+(w===b.w?"win":"")+'"><em>'+w+'</em><i><i data-w="'+(o.u/mx).toFixed(3)+'"></i></i><b>'+Math.round(o.u).toLocaleString("ja-JP")+'円</b></span>':'<span class="no"><em>'+w+'</em><i></i><b>なし</b></span>'}).join("")+'</span></button>'}
var G=[["","すべて"]].concat(D.groups.map(function(g){return [g[0],g[0]]})),cur="";
S_.seg($("#seg"),G,cur,function(v){cur=v;grid(true)});
function grid(anim){var ks=cur?D.groups.filter(function(g){return g[0]===cur})[0][1]:D.cats.map(function(c){return c.k});
  var L=ks.map(function(k){return BY[k]}).filter(Boolean);$("#ch").innerHTML=esc(cur||"すべて")+" <b>"+L.length+"</b>種類";
  $("#kg").innerHTML=L.map(card).join("");S_.counts($("#kg"));S_.bars($("#kg"));
  if(anim&&!RM)$$("#kg .kc").forEach(function(x,i){x.animate([{opacity:0,transform:"translateY(10px)"},{opacity:1,transform:"none"}],{duration:360,delay:i*30,easing:"cubic-bezier(.2,.9,.25,1)",fill:"backwards"})});
  if(anim){var top=$("#sent").getBoundingClientRect().top+scrollY;if(scrollY>top)scrollTo({top:top,behavior:"smooth"})}}
grid(false);S_.bars($("#myx"));
document.addEventListener("click",function(e){var b=e.target.closest(".kc");if(b)openKind(BY[b.dataset.k])});
new IntersectionObserver(function(e){$("#bar").classList.toggle("stuck",!e[0].isIntersecting)}).observe($("#sent"));

/* 値段の線（30日） */
function spark(h){if(!h||h.length<3)return "";var mx=Math.max.apply(null,h),mn=Math.min.apply(null,h),r=mx-mn||1,W=100,H=28;
  var pts=h.map(function(v,i){return (i/(h.length-1)*W).toFixed(1)+","+(H-2-(v-mn)/r*(H-4)).toFixed(1)}).join(" ");
  return '<svg class="spk" viewBox="0 0 100 28" preserveAspectRatio="none"><polyline points="'+pts+'"/></svg>'}
/* 11/27 夜の点検「シングルとダブルが一緒・厚みで選べない」→ トイレットペーパーは1つずつに厚みの札（名前に無い物は「厚みの表示なし」） */
function thick(c,o){if(c.k!=="tp")return "";var n=o.n||"",t=/ダブル/.test(n)?"ダブル":/シングル/.test(n)?"シングル":"厚みの表示なし";return '<span class="sp" style="background:var(--ink);color:var(--bg)">'+t+'</span>'}
function row(c,o,i){var d=drop(o);
  return '<a class="of" href="'+esc(o.url)+'" target="_blank" rel="noopener sponsored" style="--sc:'+SC[o.w]+'"><span class="oi">'+(o.img?'<img src="'+esc(o.img)+'" alt="" loading="lazy">':icon(c.k))+'</span>'+
   '<span class="ot"><span class="sp">'+o.w+'</span>'+thick(c,o)+'<b>'+esc(o.n)+'</b><small>'+esc(o.a)+(o.rc?'・★'+o.av+'（'+o.rc+'件）':"")+'</small>'+(d?'<em class="dr">30日でいちばん安い・'+d+'%下がった</em>':"")+'</span>'+
   '<span class="oprc"><strong>'+yen(o.p)+'</strong><small>'+per(c,o)+' '+yen(o.u)+'</small></span></a>'}
function openKind(c){if(!c)return;var sh=c.sh,b=c.best,mx=0,bf=bfOf(c.k),amz=bf.filter(function(x){return x.w==="Amazon"})[0];
  Object.keys(sh).forEach(function(w){mx=Math.max(mx,sh[w].u)});var on=MY.indexOf(c.k)>=0,d=drop(b);
  var cmp=["楽天","Yahoo!"].map(function(w){var o=sh[w];if(!o)return '<div class="srow no"><span class="sn">'+w+'</span><span class="ssv">今回は見つかりませんでした</span></div>';
     return '<div class="srow'+(w===b.w?" win":"")+'" style="--sc:'+SC[w]+'"><span class="sn">'+w+'</span><i class="sb"><i data-w="'+(o.u/mx).toFixed(3)+'"></i></i><span class="ssv"><b>'+yen(o.u)+'</b>'+(w===b.w?'<em>いちばん安い</em>':'<em>+'+yen(o.u-b.u)+'</em>')+'</span></div>'}).join("")+
   '<a class="srow amz" style="--sc:'+SC.Amazon+'" href="'+esc(amz?amz.url:amzUrl(c))+'" target="_blank" rel="noopener sponsored"><span class="sn">Amazon</span><span class="ssv">'+(amz?'<b>'+esc(amz.p)+'</b><em>ブラックフライデー・'+esc(amz.n)+'</em>':'<b class="lk">値段を見る ›</b><em>Amazonは値段を自動で調べられないため、検索が開きます</em>')+'</span></a>';
  S_.sheet('<div class="bd kw"><div class="lb"><span class="g">'+per(c,b)+'で比べています</span><span>'+c.o.length+'件から</span></div>'+
   '<h2><span class="ki">'+icon(c.k)+'</span>'+esc(c.nm)+'</h2>'+
   '<section class="pc"><h3>お店ごとのいちばん安い値段<small>'+per(c,b)+'・送料込み</small></h3><div class="cmpS">'+cmp+'</div></section>'+
   '<section class="best" style="--sc:'+SC[b.w]+'"><div class="bt"><span class="sp">'+b.w+'</span><span class="cr2">いちばん安い</span></div>'+
   '<div class="bb">'+(b.img?'<img src="'+esc(b.img)+'" alt="">':'')+'<div><b>'+esc(b.n)+'</b><small>'+esc(b.a)+'・'+esc(b.s||"")+'</small>'+(b.rc?'<small>★'+b.av+'（'+b.rc+'件のレビュー）</small>':"")+'</div></div>'+
   '<div class="bp"><div><small>値段（送料込み）</small><strong><span data-n="'+b.p+'" data-f="1">0</span>円</strong></div><div><small>'+per(c,b)+'</small><strong>'+yen(b.u)+'</strong></div></div>'+
   (b.h?'<div class="hs"><small>この30日の値段'+(d?'・<b class="up">いまがいちばん安い（'+d+'%下がった）</b>':'')+'</small>'+spark(b.h)+'</div>':"")+
   '<a class="go" href="'+esc(b.url)+'" target="_blank" rel="noopener sponsored">'+b.w+'で見る</a></section>'+
   (bf.length?'<section class="pc"><h3>ブラックフライデー<small>11/25 1:59まで</small></h3>'+bf.map(function(x){return '<a class="of" href="'+esc(x.url)+'" target="_blank" rel="noopener sponsored" style="--sc:'+(SC[x.w]||"#888")+'"><span class="ot"><span class="sp">'+x.w+'</span><b>'+esc(x.n)+'</b><small>'+esc(x.q||"")+(x.cp?'・'+esc(x.cp):"")+'</small></span><span class="oprc"><strong>'+esc(x.p)+'</strong></span></a>'}).join("")+'</section>':"")+
   '<section class="pc"><h3>安い順にぜんぶ<small>'+per(c,b)+'が安い順</small></h3><div class="ofs">'+c.o.map(function(o,i){return row(c,o,i)}).join("")+'</div></section>'+
   '<div class="acts"><button class="pr" id="myb">'+(on?"★ いつもの物から外す":"☆ いつもの物にする")+'</button></div>'+
   '<p class="cr">'+when(D.at)+' に調べた値段です。お店で変わることがあります。同じ量あたりの値段は、送料込みの値段を量で割っています。お店へのリンクは広告（PR）です。</p></div>',null,function(box){
    $("#myb",box).onclick=function(){var i=MY.indexOf(c.k);if(i>=0)MY.splice(i,1);else MY.unshift(c.k);saveMy();myBox();S_.bars($("#myx"));this.textContent=MY.indexOf(c.k)>=0?"★ いつもの物から外す":"☆ いつもの物にする"}})}
function openDrop(){var L=[];D.cats.forEach(function(c){c.o.forEach(function(o){var d=drop(o);if(d)L.push([c,o,d])})});L.sort(function(a,b){return b[2]-a[2]});
  S_.sheet('<div class="bd kw"><div class="lb"><span class="g">楽天で毎日調べている値段から</span></div><h2>30日でいちばん安い物</h2>'+
   '<p class="lead2">この30日に調べた中で、いまの値段がいちばん安く、3%以上下がった物です。</p><div class="ofs">'+
   (L.length?L.map(function(x){return row(x[0],x[1])}).join(""):'<p class="cr">いまはありません。</p>')+'</div><p class="cr">'+when(D.at)+' に調べた値段です。お店へのリンクは広告（PR）です。</p></div>')}

S_.onNav(function(a){if(a==="find"){S_.navCur("find");scrollTo({top:0,behavior:"smooth"});setTimeout(function(){q.focus()},350)}
  else if(a==="drop"){openDrop()}
  else if(a==="my"){S_.navCur("my");var t=$("#myx");if(t.innerHTML){scrollTo({top:t.getBoundingClientRect().top+scrollY-10,behavior:"smooth"})}
    else S_.sheet('<div class="bd kw"><h2>いつもの物</h2><p class="lead2">品物を開いて「☆ いつもの物にする」を押すと、ページの上に並びます。いつも買う物の値段を、開いてすぐ見比べられます。保存はこの端末だけです。</p></div>')}});

/* 新しい値段を取りに行く（ページに入れた物より新しければ差し替える） */
if(D.live&&window.fetch)fetch(D.live,{cache:"no-cache"}).then(function(r){return r.ok?r.json():null}).then(function(n){
  if(!n||!n.cats||n.made<=D.made)return;["at","made","cats","bf","bfEnd"].forEach(function(k){D[k]=n[k]});BY={};D.cats.forEach(function(c){BY[c.k]=c});ST=stat();head();bfBox();myBox();grid(false);S_.bars($("#myx"))}).catch(function(){});
/* 今までの /okaimono?k=water などから来た人は、その品物をすぐ開く */
var K0=new URLSearchParams(location.search).get("k");if(K0&&BY[K0])setTimeout(function(){openKind(BY[K0])},300);
S_.ready();
})();
