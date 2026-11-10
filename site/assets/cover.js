/* 11/10 オーナーOK「ok 改善点がないなら実行」→ 表紙 v3「1つの地図で4つのノート」（見本 https://claude.ai/artifact/P5QnoLCpfwCSBDpvZABfrL）
   上の切り替え（おでかけ・街の地価・実家・おかいもの）で地図の数字と濃さが変わる／府県を押すと下から「◯◯のきょう」／前に押した府県を覚える。
   データは /assets/cover.json（tools/cover/make.py が毎日作る・3KB）。 */
(function(){
var COL={od:"#E39B3A",fu:"#4F7BA8",jk:"#5E9E6E",ok:"#C2727F"},L="od",svg=document.querySelector(".kmap"),C=null,NS=null;if(!svg)return;
/* 11/10 関東（LIFE NOTE）でも同じファイル：地図に東京があれば関東 */
var KT=!!svg.querySelector('.pf path[data-p="東京"]'),PREF=KT?["東京","神奈川","埼玉","千葉","茨城","栃木","群馬"]:["大阪","京都","兵庫","奈良","滋賀","和歌山"],HOME=PREF[0];
var d=new Date(),W="日月火水木金土",WX=KT?{"東京":"130000","神奈川":"140000","埼玉":"110000","千葉":"120000","茨城":"080000","栃木":"090000","群馬":"100000"}:{"大阪":"270000","京都":"260000","兵庫":"280000","奈良":"290000","滋賀":"250000","和歌山":"300000"};
var MY="";try{MY=localStorage.getItem("tn_pref")||""}catch(e){}
function sunset(){var rad=Math.PI/180,lat=KT?35.68:34.69,lng=KT?139.69:135.5,n=Math.floor((d-new Date(d.getFullYear(),0,0))/864e5),g=2*Math.PI/365*(n-1),eq=229.18*(.000075+.001868*Math.cos(g)-.032077*Math.sin(g)-.014615*Math.cos(2*g)-.040849*Math.sin(2*g)),de=.006918-.399912*Math.cos(g)+.070257*Math.sin(g)-.006758*Math.cos(2*g)+.000907*Math.sin(2*g)-.002697*Math.cos(3*g)+.00148*Math.sin(3*g),ha=Math.acos(Math.cos(90.833*rad)/(Math.cos(lat*rad)*Math.cos(de))-Math.tan(lat*rad)*Math.tan(de))/rad,m=720-4*(lng-ha)-eq+540;return Math.floor(m/60)+":"+("0"+Math.round(m%60)).slice(-2);}
var td=document.getElementById("today");
td.innerHTML="<div><b>"+(d.getMonth()+1)+"/"+d.getDate()+"（"+W[d.getDay()]+"）</b><span id='twx'></span></div><div>日の入り <b>"+sunset()+"</b><i>・</i><span id='tnow'>開催中 ―</span></div>";
/* 前に押した府県：日付の下に「大阪のきょう ›」 */
if(MY)td.insertAdjacentHTML("afterend",'<button class="mine" type="button">'+MY+'のきょう<span>›</span></button>');
fetch("/wx?a="+(WX[MY]||WX[HOME])).then(function(r){return r.json()}).then(function(j){if(!j.w)return;var mx=0;(j.pops||[]).slice(0,4).forEach(function(x){mx=Math.max(mx,+x.v||0)});document.getElementById("twx").innerHTML="<i>・</i>"+(WX[MY]?MY:HOME)+" "+j.w.split(" ")[0].replace(/時々.*|のち.*/,"")+" <b>"+mx+"%</b>";}).catch(function(){});
var hint=document.createElement("p");hint.className="lhint";document.querySelector(".mapsec").appendChild(hint);
var okp=document.createElement("div");okp.className="okp";okp.hidden=true;hint.after(okp);
var labels={};svg.querySelectorAll("g[transform] text.jp").forEach(function(t){var g=t.parentNode,c=document.createElementNS("http://www.w3.org/2000/svg","text");c.setAttribute("class","cnt");c.setAttribute("y","40");g.appendChild(c);labels[t.textContent]=c;});
function man(v){return v>=10000?(v/10000).toFixed(2).replace(/0$/,"")+"億":v.toLocaleString()+"万"}
function val(p){var x=C.p[p];return L==="od"?x.od:L==="fu"?x.avg:L==="jk"?(KT?x.kN:x.kAvg):0}
function paint(){if(!C)return;var mn=1e9,mx=-1e9;PREF.forEach(function(p){var v=val(p);mn=Math.min(mn,v);mx=Math.max(mx,v)});
 /* 11/10 オーナー「色が濃いほどはやめよう 大阪と東京が多いのは当たり前」→ 濃さで差をつけない。地図はいつもの色、数字だけ変わる */
 svg.querySelectorAll(".pf path").forEach(function(el){el.style.removeProperty("fill-opacity");el.style.removeProperty("fill");});
 svg.classList.toggle("dim",L==="ok");
 PREF.forEach(function(p){var c=labels[p],x=C.p[p];if(!c)return;c.setAttribute("fill",document.documentElement.classList.contains("night")?{od:"#FFD39A",fu:"#A9CBFF",jk:"#AEE0B5",ok:"#F2B6C3"}[L]:COL[L]);c.innerHTML=L==="od"?x.od+"<tspan>件</tspan>":L==="fu"?(x.avg>=0?"+":"")+x.avg.toFixed(1)+"<tspan>%</tspan>":L==="jk"?(KT?x.kN+"<tspan>街</tspan>":man(x.kAvg)):"";});
 var tot=PREF.reduce(function(a,p){return a+C.p[p].od},0);document.getElementById("tnow").innerHTML="開催中 <b>"+tot+"</b>";
 var R=KT?"都県":"府県";
 hint.style.setProperty("--c",COL[L]);hint.innerHTML=L==="od"?R+"ごとの、いま開催中のおでかけの数":L==="fu"?R+"ごとの、住宅地の値段の1年の動き（平均）":L==="jk"?(KT?R+"ごとの、実家ノートでまとめた街の数":"戸建が売れた平均の値段（近畿レインズ）"):"きょう、ふだんより安くなっている物";
 okp.hidden=L!=="ok";if(L==="ok"&&NS)okp.innerHTML=NS.downs.slice(0,3).map(function(x,i){return'<a href="/nesage"><span>0'+(i+1)+'</span><b>'+x.title+'</b><em>'+x.price.toLocaleString()+'円</em><u>−'+x.pct+'%</u></a>'}).join("")+'<a class="all" href="/okaimono">日用品の最安をくらべる →</a>';}
document.getElementById("lens").addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;L=b.getAttribute("data-l");this.querySelectorAll("button").forEach(function(x){x.classList.toggle("on",x===b)});paint();});
var sh=document.createElement("div");sh.id="tsheet";document.body.appendChild(sh);
var EN={"大阪":"OSAKA","京都":"KYOTO","兵庫":"HYOGO","奈良":"NARA","滋賀":"SHIGA","和歌山":"WAKAYAMA","東京":"TOKYO","神奈川":"KANAGAWA","埼玉":"SAITAMA","千葉":"CHIBA","茨城":"IBARAKI","栃木":"TOCHIGI","群馬":"GUNMA"};
function li(a){return'<ol>'+a.map(function(t,i){return'<li><span>0'+(i+1)+'</span>'+t+'</li>'}).join("")+'</ol>'}
window.__openSheet=function(p){if(!C)return;var x=C.p[p],l=L==="ok"?"od":L;sh.style.setProperty("--c",COL[l]);var h='<div class="hd"></div><button class="x" type="button" aria-label="閉じる">×</button><div class="en">'+EN[p]+'</div><h3>'+p+'のきょう</h3>';
 if(l==="od")h+='<div class="big"><div>開催中<b>'+x.od+'</b></div><div>入場無料<b>'+x.free+'</b></div></div>'+li(x.odL.map(function(o){return o.t}))+'<a class="go" href="/odekake?pref='+encodeURIComponent(p)+'">'+p+'のおでかけを見る<span>→</span></a>';
 else if(l==="fu")h+='<div class="big"><div>平均の上がり幅<b>'+(x.avg>=0?"+":"")+x.avg.toFixed(1)+'%</b></div><div>上がった街<b>'+x.upT+'<small>／'+x.tw+'</small></b></div></div>'+li(x.top.map(function(t){return t.n+'　+'+t.r.toFixed(1)+'%'}))+'<a class="go" href="/chika-'+(KT?"kanto":"kansai")+'">'+p+'の街の地価を見る<span>→</span></a>';
 else if(KT)h+='<div class="big"><div>実家ノートの街<b>'+x.kN+'<small>街</small></b></div><div>住宅地 1年<b>'+(x.avg>=0?"+":"")+x.avg.toFixed(1)+'%</b></div></div><p class="sn">相続した家を売る・片付ける・解体する前に、街ごとの地価と4つの順番をまとめています。</p><a class="go" href="/jikka/">'+p+'の実家ノートを見る<span>→</span></a>';
 else h+='<div class="big"><div>戸建が売れた平均<b>'+man(x.kAvg)+'</b></div><div>売れた数<b>'+x.kN.toLocaleString()+'<small>件</small></b></div></div><p class="sn">相続した家を売る・片付ける・解体する前に、街ごとの4つの順番をまとめています。</p><a class="go" href="/jikka/">'+p+'の実家ノートを見る<span>→</span></a>';
 sh.innerHTML=h;sh.classList.add("on");sh.querySelector(".x").onclick=function(){sh.classList.remove("on")};try{localStorage.setItem("tn_pref",p)}catch(e){}};
/* 下へなでて閉じる */
var sy=null;sh.addEventListener("touchstart",function(e){sy=e.touches[0].clientY},{passive:true});sh.addEventListener("touchend",function(e){if(sy!==null&&e.changedTouches[0].clientY-sy>60)sh.classList.remove("on");sy=null},{passive:true});
svg.querySelectorAll(".pf path").forEach(function(el){el.addEventListener("click",function(){window.__openSheet(el.getAttribute("data-p"))})});
document.addEventListener("click",function(e){if(e.target.closest(".mine"))window.__openSheet(MY)});
var ls=document.querySelector(".lists");ls.insertAdjacentHTML("beforebegin",'<div class="kicker">TODAY\'S NOTE　─　きょうのノート</div>');var cards=ls.querySelectorAll("a.ls");var dt=document.createElement("div");dt.className="dots";dt.innerHTML=Array.prototype.map.call(cards,function(_,i){return"<i"+(i?"":" class=on")+"></i>"}).join("");ls.after(dt);
ls.addEventListener("scroll",function(){var i=Math.round(ls.scrollLeft/(cards[0].offsetWidth+12));dt.querySelectorAll("i").forEach(function(x,j){x.classList.toggle("on",j===i)})},{passive:true});
fetch("/assets/cover.json").then(function(r){return r.json()}).then(function(j){C=j;paint()});
fetch("https://raw.githubusercontent.com/oreusa/akari-auto/main/data/nesage.json").then(function(r){return r.json()}).then(function(j){NS=j;paint()}).catch(function(){});
document.addEventListener("usagi-theme",paint);
})();
