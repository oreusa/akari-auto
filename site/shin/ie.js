/* 新しいHP：家と土地。役目＝自分の街の家と土地がいくらか、すぐ分かる。こだわり＝数字が数え上がり、棒が伸びて比べられる。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,D=S_.data,RM=S_.RM;
var RG=S_.reg||{},RN=RG.n||"関西",PREF=RG.pref||["大阪","京都","兵庫","奈良","滋賀","和歌山"],PF=D.pfull||{"大阪":"大阪府","京都":"京都府","兵庫":"兵庫県","奈良":"奈良県","滋賀":"滋賀県","和歌山":"和歌山県"};
var PC=D.pc||{"大阪":"#D9775A","京都":"#9C7BB8","兵庫":"#4F86C6","奈良":"#5FA06A","滋賀":"#3FA3B5","和歌山":"#E09A3E"};
var TW=D.towns,PA=D.pa,BY={};TW.forEach(function(t,i){t.i=i;BY[t.id]=t});
/* toLocaleString は遅い（205の街で約60ms）→ 自前で3桁ごとに「,」 */function cm(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,",")}
function man(v){if(v==null)return "—";v=Math.round(v);return v>=10000?(Math.floor(v/10000)+"億"+(v%10000?cm(v%10000)+"万":"")):cm(v)+"万"}
function pct(v){return v==null?"—":(v>0?"+":"")+v.toFixed(1)+"%"}
function kana(s){return String(s||"").replace(/[ァ-ン]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-96)}).replace(/\s/g,"")}
function wavg(f){var n=0,s=0;TW.forEach(function(t){var a=t[f];if(a){n+=a[0];s+=a[0]*a[1]}});return n?s/n:0}
var avM=wavg("m"),avH=wavg("h"),nUp=TW.filter(function(t){return t.r8>0}).length;

var SORT={up:["地価の上がり順",function(t){return t.r8},function(t){return pct(t.r8)},"住宅地 1年"],
 m:["マンションが高い順",function(t){return t.m&&t.m[1]},function(t){return t.m?man(t.m[1])+"円":"—"},"中古マンション平均"],
 h:["一戸建てが安い順",function(t){return t.h&&-t.h[1]},function(t){return t.h?man(t.h[1])+"円":"—"},"中古一戸建て平均"],
 pop:["人が増えた順",function(t){return t.pop&&t.pop[1]},function(t){return t.pop?pct(t.pop[1]):"—"},"人口 5年"]};if(!avM)delete SORT.m;if(!avH)delete SORT.h;
var Q=new URLSearchParams(location.search),S={p:Q.get("p")||"",o:Q.get("o")||"up",n:30};

/* 11/20 owner「パッと見で使いにくい」→ 家と土地の入口を1枚に。
   17:25 owner「何をするにもたどり着くには経由がいる」→ 3枚の扉（押すと次の入口）をやめ、行き先を全部ここに並べる＝どこへも1回で着く。 */
var HUB=document.documentElement.classList.contains("ieo")&&window.TN_IEG;
/* 18:27 owner「本気で見やすいと思う？」→ 19:07 owner「月が決めていいよ」→ ふだんの形に（?ie2=0 でこの端末だけ前の形）：
   ①探す欄が主役 ②色の枠6つをやめ、下のバーに無い行き先だけを細い線の一覧に（同じ物を2回並べない） ③字は 16/13px ④府県の帯の下の並べかえの帯をやめ、件数の横の「並べ方」1つに */
var V2=!!HUB;try{var _v=location.search.match(/[?&]ie2=([01])/);if(_v)localStorage.setItem("tn_ie2",_v[1]);V2=!!HUB&&localStorage.getItem("tn_ie2")!=="0"}catch(e){}
if(V2)document.documentElement.classList.add("ie2");
var QI={tag:'<path d="M3.5 12.2V4.5a1 1 0 0 1 1-1h7.7l8.6 8.6a1.2 1.2 0 0 1 0 1.7l-7 7a1.2 1.2 0 0 1-1.7 0z"/><circle cx="8" cy="8" r="1.6"/>',note:'<path d="M6 3.5h10l3 3V20.5H6z"/><path d="M9 10h7M9 13.5h7M9 17h4"/>',chat:'<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',rank:'<path d="M5 20V11M12 20V5M19 20v-6"/>',key:'<circle cx="8" cy="15" r="4.2"/><path d="M11 12l8.5-8.5M16.5 6.5l2.5 2.5M14 9l2 2"/>',box:'<path d="M3.5 8l8.5-4 8.5 4v9l-8.5 4-8.5-4z"/><path d="M3.5 8l8.5 4 8.5-4M12 12v9"/>',calc:'<rect x="5" y="3" width="14" height="18" rx="2.5"/><path d="M8 7.5h8M8.5 12h0M12 12h0M15.5 12h0M8.5 16h0M12 16h0M15.5 16h0"/>'};
var QD={"/chika-kansai":"上がった街・下がった街","/chika-kanto":"上がった街・下がった街","/ikura":"30秒で目安・売る順番も","/sagasu":"予算で住める街","/moushikomi":"売却・査定・解体","/jikka/":"相続・診断・空き家の街","/kaitai":"広さ別の費用の目安と、市の補助金","/moushikomi?want=%E7%89%87%E4%BB%98%E3%81%91%E3%83%BB%E9%81%BA%E5%93%81%E6%95%B4%E7%90%86%E3%81%AE%E8%A6%8B%E7%A9%8D%E3%82%8A":"家財の片付けだけでも大丈夫です"};
var BAR=/^\/(fudosan-list|ikura|jikka\/|moushikomi)$/;
/* 11/21 見本 ?kn=1：下のバーが4つの部屋になるので、家と土地の行き先は全部この入口に。3つの目的の見出しの下に並べる（1回で着く・枝分かれなし） */
var KN=document.documentElement.classList.contains("lk-kn");
if(V2&&KN)var DOOR='<h2 class="qr-h">何をしますか？</h2>'+window.TN_IEG.map(function(g){var L=g.i.filter(function(x){return x[3]!=="/fudosan-list"});return L.length?'<p class="qr-g">'+esc(g.t)+'</p><nav class="qr" aria-label="'+esc(g.t)+'">'+L.map(function(x){return '<a href="'+x[3]+'"><svg viewBox="0 0 24 24">'+(QI[x[2]]||QI.rank)+'</svg><span><b>'+esc(x[0])+'</b><small>'+esc(QD[x[3]]||"")+'</small></span><i>›</i></a>'}).join("")+'</nav>':''}).join("")+
 '<h2 class="dq dq2">街の値段と地価</h2>';
else if(V2)var DOOR='<h2 class="qr-h">ほかに調べる</h2><nav class="qr" aria-label="ほかに調べる">'+[].concat.apply([],window.TN_IEG.map(function(g){return g.i})).filter(function(x){return !BAR.test(x[3])}).map(function(x){return '<a href="'+x[3]+'"><svg viewBox="0 0 24 24">'+(QI[x[2]]||"")+'</svg><span><b>'+esc(x[0])+'</b><small>'+esc(QD[x[3]]||"")+'</small></span><i>›</i></a>'}).join("")+'</nav>'+
 '<h2 class="dq dq2">街の値段と地価</h2>';
else var DOOR=HUB?'<nav class="qk" aria-label="家と土地のページ">'+[].concat.apply([],window.TN_IEG.map(function(g){return g.i})).filter(function(x){return !/^\/fudosan-list|want=/.test(x[3])}).map(function(x){return '<a href="'+x[3]+'"><b>'+esc(x[0])+'</b><small>'+esc(QD[x[3]]||"")+'</small></a>'}).join("")+'</nav>'+
 '<h2 class="dq dq2">街の値段と地価</h2>':'';
S_.main.innerHTML='<div class="wrap"><section class="hero"><h1 class="h1t">'+esc(HUB?RN+'の家と土地':(D.h1||(RN+'の家と土地の相場')))+'</h1><p class="h1p">'+esc(V2?TW.length+'の街の、実際に売れた値段と地価':HUB?TW.length+'の街の値段と地価・家を売る買う・実家と空き家':(D.sub||(TW.length+'の街・実際に売れた値段と、地価の動き')))+'</p>'+
 '<div class="fnd"><label class="fin">'+S_.IC.find+'<input id="q" type="search" placeholder="街の名前で探す（例：'+esc(D.ph||'吹田、すいた')+'）" autocomplete="off" enterkeyhint="search"></label>'+
 '<div class="sug" id="sug"></div><button class="geo" id="geo">'+S_.IC.map+'<span>いまいる場所の街を見る</span></button></div>'+DOOR+
 '<div class="tiles">'+(avM?'<button data-o="m"><small>中古マンション <span style="white-space:nowrap">平均</span></small><b><span data-n="'+Math.round(avM)+'" data-f="1">0</span><u>万円</u></b><i>→</i></button>'+
 '<button data-o="h"><small>中古一戸建て <span style="white-space:nowrap">平均</span></small><b><span data-n="'+Math.round(avH)+'" data-f="1">0</span><u>万円</u></b><i>→</i></button>':'<button data-o="pop"><small>人が増えた街</small><b><span data-n="'+TW.filter(function(t){return t.pop&&t.pop[1]>0}).length+'">0</span><u>/ '+TW.length+'</u></b><i>→</i></button>')+
 '<button data-o="up"><small>地価が上がった街</small><b><span data-n="'+nUp+'">0</span><u>/ '+TW.length+'</u></b><i>→</i></button></div>'+
 '<p class="upd"><i class="dot"></i>'+esc(D.upd||'2026年の地価公示・2025年度に売れた家（レインズ）の数字')+'</p></section>'+
 '<div id="sent"></div><div class="bar" id="bar"><div class="seg" id="seg"></div><div class="chips" id="chips"></div></div>'+
 '<div class="cnt"><h3 id="ch"></h3><small id="cs"></small></div><ol class="rk" id="rk"></ol><div id="mr"></div></div>';
S_.counts(S_.main);

/* 探す（ひらがなでも） */
var q=$("#q"),sug=$("#sug");
q.addEventListener("input",function(){var v=kana(q.value.trim());if(!v){sug.innerHTML="";sug.classList.remove("op");return}
  var L=TW.filter(function(t){return kana(t.n).indexOf(v)>=0||kana(t.k).indexOf(v)>=0}).slice(0,8);
  sug.innerHTML=L.length?L.map(function(t){return '<button data-id="'+t.id+'"><b>'+esc(t.n)+'</b><small>'+t.p+'</small><span>'+pct(t.r8)+'</span></button>'}).join(""):'<p>見つかりません。市や区の名前で探してください</p>';sug.classList.add("op")});
[].forEach.call(document.querySelectorAll(".door [data-door]"),function(a){a.addEventListener("click",function(e){e.preventDefault();var top=$("#sent").getBoundingClientRect().top+scrollY-60;scrollTo({top:top,behavior:"smooth"})})});
if(Q.get("q")){q.value=Q.get("q");q.dispatchEvent(new Event("input"))}
sug.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;q.blur();sug.classList.remove("op");openTown(BY[b.dataset.id])});
$("#geo").addEventListener("click",function(){var b=this;if(!navigator.geolocation)return;b.classList.add("ld");$("span",b).textContent="場所を調べています…";
  navigator.geolocation.getCurrentPosition(function(p){var K=RN==="関東",x=K?(p.coords.longitude-138.4)*81+10:(p.coords.longitude-134)*82.2,y=K?(37.15-p.coords.latitude)*100+27:(36-p.coords.latitude)*100,best=null,bd=1e9;
    TW.forEach(function(t){if(!t.xy)return;var d=Math.hypot(t.xy[0]-x,t.xy[1]-y);if(d<bd){bd=d;best=t}});b.classList.remove("ld");$("span",b).textContent="いまいる場所の街を見る";
    if(best&&bd<40)openTown(best);else $("span",b).textContent=RN+"の外のようです"},function(){b.classList.remove("ld");$("span",b).textContent="場所が使えませんでした"},{timeout:8000,maximumAge:6e5})});
$(".tiles").addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;S.o=b.dataset.o;S.n=30;sync();go(true);var top=$("#sent").getBoundingClientRect().top+scrollY;scrollTo({top:top,behavior:"smooth"})});

/* 並べる */
S_.seg($("#seg"),[["",RN]].concat(PREF.map(function(p){return [p,p]})),S.p,function(v){S.p=v;S.n=30;sync();go(true)});
if(V2){var _c=$(".cnt");_c.insertAdjacentHTML("beforeend",'<label class="osel"><span>並べ方</span><select id="osel" aria-label="並べ方">'+Object.keys(SORT).map(function(k){return '<option value="'+k+'">'+SORT[k][0]+'</option>'}).join("")+'</select></label>');
  $("#osel").addEventListener("change",function(){S.o=this.value;S.n=30;sync();go(true)})}
function sync(){if(V2&&$("#osel"))$("#osel").value=S.o;$("#chips").innerHTML=Object.keys(SORT).map(function(k){return '<button class="chip'+(S.o===k?" on":"")+'" data-o="'+k+'">'+SORT[k][0]+'</button>'}).join("");
  var u=new URLSearchParams(location.search);S.p?u.set("p",S.p):u.delete("p");S.o!=="up"?u.set("o",S.o):u.delete("o");history.replaceState(history.state,"",location.pathname+(u.toString()?"?"+u:""))}
$("#chips").addEventListener("click",function(e){var b=e.target.closest(".chip");if(!b)return;S.o=b.dataset.o;S.n=30;sync();go(true)});
function go(anim){var f=SORT[S.o],L=TW.filter(function(t){return (!S.p||t.p===S.p)&&f[1](t)!=null}).sort(function(a,b){return f[1](b)-f[1](a)});
  var vals=L.map(f[1]),mx=Math.max.apply(null,vals.map(Math.abs).concat([1e-9]));
  $("#ch").innerHTML=esc(S.p||RN)+(V2?"":"・"+f[0])+" <b data-n='"+L.length+"'>"+L.length+"</b>の街";$("#cs").textContent=f[3];
  $("#rk").innerHTML=L.slice(0,S.n).map(function(t,i){var v=f[1](t),w=Math.abs(v)/mx;
    return '<li><button data-id="'+t.id+'" style="--pc:'+PC[t.p]+'"><em>'+(i+1)+'</em><span class="tn"><b>'+esc(t.n)+'</b><small>'+t.p+(t.m?'・マンション '+man(t.m[1]):'')+(t.h?'・一戸建て '+man(t.h[1]):'')+'</small><i class="br'+(v<0?" neg":"")+'"><i data-w="'+w.toFixed(3)+'"></i></i></span><strong class="'+(S.o==="up"||S.o==="pop"?(v>=0?"up":"dn"):"")+'">'+f[2](t)+'</strong></button></li>'}).join("");
  $("#mr").innerHTML=L.length>S.n?'<button class="more">もっと見る（残り'+(L.length-S.n)+'の街）</button>':"";
  S_.bars($("#rk"));if(anim)S_.countUp($("#ch b"));
  if(anim&&!RM)$$("#rk li").forEach(function(li,k){if(k<12)li.animate([{opacity:0,transform:"translateY(10px)"},{opacity:1,transform:"none"}],{duration:380,delay:k*28,easing:"cubic-bezier(.2,.9,.25,1)",fill:"backwards"})});
  if(anim){var top=$("#sent").getBoundingClientRect().top+scrollY;if(scrollY>top)scrollTo({top:top,behavior:"smooth"})}}
$("#mr").addEventListener("click",function(e){if(e.target.closest(".more")){S.n+=30;go(false)}});
$("#rk").addEventListener("click",function(e){var b=e.target.closest("button[data-id]");if(b)openTown(BY[b.dataset.id])});
sync();go(false);
new IntersectionObserver(function(e){$("#bar").classList.toggle("stuck",!e[0].isIntersecting)}).observe($("#sent"));

/* 1つの街（4つの数をセットで：平均・件数・広さ・築年） */
function cmp(v,a,lab){if(v==null||!a)return "";var mx=Math.max(v,a),d=Math.round(v-a);
  return '<div class="cmp"><div><span>この街</span><i><i data-w="'+(v/mx).toFixed(3)+'" style="background:var(--pc)"></i></i><b>'+man(v)+'</b></div><div><span>'+lab+'</span><i><i data-w="'+(a/mx).toFixed(3)+'"></i></i><b>'+man(a)+'</b></div>'+
   '<p>'+lab+'より'+(d===0?"同じくらい":man(Math.abs(d))+"円"+(d>0?"高い":"安い"))+'</p></div>'}
function openTown(t){if(!t)return;try{dispatchEvent(new CustomEvent("tn-town",{detail:{n:t.n,id:t.id||""}}))}catch(e){}var pa=PA[t.p]||{},trend=t.r7==null||t.r8==null?"":t.r8>t.r7?"前の年より上がり幅が大きくなりました。":t.r8<t.r7?"前の年より上がり幅が小さくなりました。":"前の年と同じくらいです。";
  var nm=esc(t.n),moushi="/moushikomi?lite=1&machi="+t.id+"&want="+encodeURIComponent("査定してほしい");
  S_.sheet('<div class="bd tw" style="--pc:'+PC[t.p]+'"><div class="lb"><span class="g" style="color:'+PC[t.p]+'">'+PF[t.p]+'</span>'+(t.rk?'<span>地価の上がり幅 '+t.rk+'位／'+t.of+'</span>':"")+'</div>'+
   '<h2>'+esc(t.n)+'</h2><div class="hero2"><div><small>住宅地の地価 1年の動き</small><b class="'+(t.r8>=0?"up":"dn")+'"><span data-n="'+(t.r8||0)+'" data-d="1" data-pre="'+(t.r8>0?"+":"")+'">0</span>%</b></div><p>'+(t.r7!=null?"前の年は"+pct(t.r7)+"。":"")+trend+'</p></div>'+
   (t.m?'<section class="pc"><h3>中古マンション<small>2025年度に売れた '+t.m[0]+'件の平均</small></h3><div class="big"><span data-n="'+Math.round(t.m[1])+'" data-f="1">0</span><u>万円</u></div><ul class="four"><li><small>件数</small>'+t.m[0]+'件</li><li><small>広さ</small>'+Math.round(t.m[2])+'㎡</li><li><small>築年数</small>'+Math.round(t.m[3])+'年</li><li><small>1㎡あたり</small>'+t.m[4].toFixed(1)+'万円</li></ul>'+cmp(t.m[1],pa.m,PF[t.p]+"の平均")+'</section>':"")+
   (t.h?'<section class="pc"><h3>中古の一戸建て<small>2025年度に売れた '+t.h[0]+'件の平均</small></h3><div class="big"><span data-n="'+Math.round(t.h[1])+'" data-f="1">0</span><u>万円</u></div><ul class="four"><li><small>件数</small>'+t.h[0]+'件</li><li><small>土地</small>'+Math.round(t.h[2])+'㎡</li><li><small>建物</small>'+Math.round(t.h[3])+'㎡</li><li><small>築年数</small>'+Math.round(t.h[4])+'年</li></ul>'+cmp(t.h[1],pa.h,PF[t.p]+"の平均")+'</section>':"")+
   (t.t?'<section class="pc"><h3>土地<small>2025年度に売れた '+t.t[0]+'件の平均</small></h3><div class="big"><span data-n="'+t.t[1]+'" data-d="1">0</span><u>万円／㎡</u></div><ul class="four"><li><small>件数</small>'+t.t[0]+'件</li><li><small>平均の広さ</small>'+Math.round(t.t[3])+'㎡</li><li><small>平均の値段</small>'+man(t.t[2])+'円</li><li><small>府県の平均</small>'+(pa.t?pa.t.toFixed(1)+'万円／㎡':"—")+'</li></ul></section>':"")+
   ((t.pop||t.ak)?'<section class="pc"><h3>くらしの数字<small>国勢調査・住宅土地統計調査</small></h3><ul class="three">'+
     (t.pop?'<li><small>人口（2025年）</small><b>'+t.pop[0].toLocaleString()+'人</b><span class="'+(t.pop[1]>=0?"up":"dn")+'">5年で'+pct(t.pop[1])+'</span></li>':"")+
     (t.o!=null?'<li><small>65歳以上</small><b>'+t.o+'%</b></li>':"")+(t.ak!=null?'<li><small>空き家の割合</small><b>'+t.ak+'%</b><span>'+PF[t.p]+' '+(pa.ak||"—")+'%</span></li>':"")+'</ul></section>':"")+
   '<div class="acts"><a class="pr" href="'+moushi+'">'+nm+'の家、いくらで売れるか無料で聞く</a>'+
   (t.buy?'<div class="buy"><small>'+nm+'でいま売り出し中（広告・Yahoo!不動産）</small><div>'+["マンション","一戸建て","土地"].map(function(l,i){return t.buy[i]?'<a href="'+esc(t.buy[i])+'" target="_blank" rel="noopener sponsored">'+l+'</a>':""}).join("")+'</div></div>':"")+
   '<a href="/machi/'+t.id+'">'+nm+'のくわしいページ</a>'+(t.kt?'<a href="'+t.kt+'">解体の補助金</a>':'<a href="/ikura?machi='+t.id+'">売れた値段から目安</a>')+'</div>'+
   '<p class="cr">どれも街の平均で、1軒ずつの値段ではありません。広さ・築年数・駅からの近さで大きく変わります。</p></div>')}

S_.onNav(function(a){if(a==="geo"){scrollTo({top:0,behavior:"smooth"});$("#geo").click();return}if(a==="find"){scrollTo({top:0,behavior:"smooth"});setTimeout(function(){q.focus()},350);S_.navCur("find")}
  else{S_.navCur("rank");var top=$("#sent").getBoundingClientRect().top+scrollY;scrollTo({top:top,behavior:"smooth"})}});
S_.ready();
/* 11/20 関東の街の位置は関東の地図の形（scripts/shin_kanto.py proj）で比べる。前は関西の形で比べて「関東の外のようです」になっていた。
   下のバーの「近くの街」（ほかのページから ?geo=1 で来た時も） */
if(Q.get("geo")==="1")setTimeout(function(){var g=$("#geo");if(g)g.click()},400);
})();
