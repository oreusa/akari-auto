/* 関東不動産リストの「2つの街をくらべる」（月の links/assets/kurabe.js と同じ物。11/7 関東用に都県の名前・数え方だけ替えた）。
   街の行（.tw）の横に「＋くらべる」。2つ選ぶと、上に3行の表（上がり幅・去年より上がり方が・都県で何位）。
   上がり方の強い方に色。残り（1年前の数字・都県と関東の平均）は「もっと見る」。数字は towns.json（令和8年地価公示・住宅地）だけ。
   選んだ街はURLに残る（?vs=tokyo-03,kanagawa-03）。 */
(function(){
if(window.__kurabe)return;window.__kurabe=1;
var FQ=document.getElementById("fq");if(!FQ)return;
var PF={"東京":"東京都","神奈川":"神奈川県","埼玉":"埼玉県","千葉":"千葉県","茨城":"茨城県","栃木":"栃木県","群馬":"群馬県"};
var TW=[],BY={},sel=[];
function pct(v){return v==null?"—":(v>0?"+":v<0?"−":"±")+Math.abs(v).toFixed(1)+"%";}
function esc(s){return String(s).replace(/[&<>"]/g,function(x){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[x]});}
function avg(L){var a=L.filter(function(t){return t.r8!=null});return a.length?a.reduce(function(s,t){return s+t.r8},0)/a.length:null;}
var css=document.createElement("style");css.textContent=
'#fq .kbw{display:flex;align-items:center;gap:8px}#fq .kbw>.tw{flex:1;min-width:0}'+
'#fq .kbb{flex:none;border:1.5px solid #2B2622;background:#fff;border-radius:999px;padding:6px 11px;font:700 12.5px "Zen Kaku Gothic New",sans-serif;color:#2B2622;cursor:pointer;white-space:nowrap}'+
'#fq .kbb.on{background:#2B2622;color:#fff}'+
'.kbc{margin:14px 0;border:1.5px solid #2B2622;border-radius:16px;padding:14px 14px 12px;background:#fff;font-family:"Zen Kaku Gothic New",sans-serif;color:#2B2622}'+
'.kbc h3{margin:0 0 2px;font-size:15px;line-height:1.5}.kbc .s{font-size:11.5px;color:#6E6E6E}'+
'.kbc table{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px}.kbc th,.kbc td{padding:8px 4px;border-top:1px solid #ECECEC;text-align:right;vertical-align:middle}'+
'.kbc th{text-align:left;font-weight:500;color:#555;font-size:12px}.kbc thead th,.kbc thead td{font-weight:700;font-size:14px;border-top:0}'+
'.kbc td b{font-family:Jost,sans-serif;font-size:17px;font-weight:500}.kbc td.w{white-space:nowrap;font-size:12.5px}'+
'.kbc .hi{background:#F6E7E1;border-radius:6px;padding:1px 5px}.kbc .na{display:block;color:#8C7B6E;font-size:11px}'+
'.kbc .mo{width:100%;margin-top:6px;border:0;border-top:1px solid #ECECEC;background:none;padding:10px 0 2px;font:700 12.5px "Zen Kaku Gothic New",sans-serif;color:#8C7B6E;cursor:pointer}'+
'.kbc .ch{width:100%;margin-top:10px;border:1px solid #DADADA;background:#fff;border-radius:999px;padding:9px;font:700 12.5px "Zen Kaku Gothic New",sans-serif;color:#2B2622;cursor:pointer}'+
'.kbc .nt{font-size:11px;color:#6E6E6E;margin:8px 0 0;line-height:1.6}'+
'.kbbar{position:fixed;left:12px;right:12px;bottom:calc(92px + env(safe-area-inset-bottom,0px));background:#2B2622;color:#fff;border-radius:12px;padding:10px 12px;font:700 12.5px/1.6 "Zen Kaku Gothic New",sans-serif;z-index:60;display:flex;gap:10px;align-items:center;max-width:440px;margin:0 auto}'+
'.kbbar[hidden],.kbc[hidden]{display:none!important}.kbbar span{flex:1}.kbbar button{flex:none;background:none;border:1px solid #fff;color:#fff;border-radius:999px;padding:3px 10px;font:700 12px "Zen Kaku Gothic New",sans-serif;cursor:pointer}';
document.head.appendChild(css);
var card=document.createElement("div");card.className="kbc";card.hidden=true;
/* 「街で探す」「地図」を開くたびに #fq の中は作り直されるので、そのたびに見出しのすぐ下へ入れ直す */
function place(){if(sel.length<2||FQ.contains(card))return;var fh=FQ.querySelector(".fh");if(fh)fh.parentNode.insertBefore(card,fh.nextSibling);}
var bar=document.createElement("div");bar.className="kbbar";bar.hidden=true;document.body.appendChild(bar);
var moreOpen=false;
function word(t){if(t.r7==null||t.r8==null)return {w:"—",v:null};var d=t.r8-t.r7;return {w:d>=0.5?"強まった":d>0?"少し強まった":d===0?"同じ":d>-0.5?"少し弱まった":"弱まった",v:d};}
function syncUrl(){try{var u=new URLSearchParams(location.search);if(sel.length)u.set("vs",sel.join(","));else u.delete("vs");var s=u.toString();history.replaceState(null,"",location.pathname+(s?"?"+s:"")+location.hash);}catch(e){}}
function marks(){[].forEach.call(FQ.querySelectorAll(".kbb"),function(b){var on=sel.indexOf(b.dataset.id)>=0;var tx=on?"えらんだ":"＋ くらべる";if(b.textContent!==tx)b.textContent=tx;if(b.classList.contains("on")!==on)b.classList.toggle("on",on);if(b.getAttribute("aria-pressed")!==String(on))b.setAttribute("aria-pressed",on);});}
function draw(){marks();syncUrl();
  if(sel.length===1){var a=BY[sel[0]];bar.hidden=false;bar.innerHTML='<span>'+esc(a.n)+'をえらびました。もう1つの街の「＋くらべる」を押してください</span><button type="button">やめる</button>';}else bar.hidden=true;
  if(sel.length<2){card.hidden=true;return;}
  var a=BY[sel[0]],b=BY[sel[1]],wa=word(a),wb=word(b),same=a.p===b.p;
  function hi(x,y,big){return x!=null&&y!=null&&(big?x>y:x<y);}
  var r1a=hi(a.r8,b.r8,1),r1b=hi(b.r8,a.r8,1),r2a=hi(wa.v,wb.v,1),r2b=hi(wb.v,wa.v,1),r3a=same&&hi(a.rk,b.rk,0),r3b=same&&hi(b.rk,a.rk,0);
  function rk(t,h){return '<span'+(h?' class="hi"':'')+'>'+t.rk+'位</span>'+(same?'':'<span class="na">'+PF[t.p]+' '+t.of+'の中</span>');}
  var h='<h3>'+esc(a.n)+'と'+esc(b.n)+'をくらべる</h3><div class="s">令和8年地価公示（2026年1月1日時点）・住宅地の平均</div><table><thead><tr><th></th><td>'+esc(a.s||a.n)+'</td><td>'+esc(b.s||b.n)+'</td></tr></thead><tbody>'+
   '<tr><th>住宅地の上がり幅</th><td><b'+(r1a?' class="hi"':'')+'>'+pct(a.r8)+'</b></td><td><b'+(r1b?' class="hi"':'')+'>'+pct(b.r8)+'</b></td></tr>'+
   '<tr><th>去年より上がり方が</th><td class="w"><span'+(r2a?' class="hi"':'')+'>'+wa.w+'</span></td><td class="w"><span'+(r2b?' class="hi"':'')+'>'+wb.w+'</span></td></tr>'+
   '<tr><th style="white-space:nowrap">'+(same?PF[a.p]+a.of+'市区町村で':'都県の中で')+'</th><td>'+rk(a,r3a)+'</td><td>'+rk(b,r3b)+'</td></tr>';
  if(moreOpen){var pa=avg(TW.filter(function(t){return t.p===a.p})),pb=avg(TW.filter(function(t){return t.p===b.p})),ka=avg(TW);
   h+='<tr><th>1年前（令和7年）</th><td>'+pct(a.r7)+'</td><td>'+pct(b.r7)+'</td></tr>'+
    (same?'<tr><th>'+PF[a.p]+'の平均<span class="na">計算</span></th><td colspan="2" style="text-align:center">'+pct(pa)+'</td></tr>':'<tr><th>都県の平均<span class="na">計算</span></th><td>'+pct(pa)+'</td><td>'+pct(pb)+'</td></tr>')+
    '<tr><th>関東'+TW.length+'市区町村の平均<span class="na">計算</span></th><td colspan="2" style="text-align:center">'+pct(ka)+'</td></tr>';}
  h+='</tbody></table>'+(moreOpen?'':'<button type="button" class="mo">もっと見る（1年前・都県と関東の平均）</button>')+
   '<button type="button" class="ch">街を替える</button><p class="nt">色の付いた方が、上がり方の強い方です。街の中の調査地点の平均の動きで、1軒ずつの値段ではありません。住みやすさや値上がりを約束する物でもありません。</p>';
  card.innerHTML=h;card.hidden=false;if(!FQ.querySelector(".fh")&&window.FQ)window.FQ.open("q");place();}
function addBtns(){place();[].forEach.call(FQ.querySelectorAll("a.tw"),function(a){if(a.parentNode.classList.contains("kbw"))return;var m=(a.getAttribute("href")||"").match(/\/machi\/([\w-]+)/);if(!m||!BY[m[1]])return;
  var w=document.createElement("div");w.className="kbw";a.parentNode.insertBefore(w,a);w.appendChild(a);var b=document.createElement("button");b.type="button";b.className="kbb";b.dataset.id=m[1];w.appendChild(b);});marks();}
FQ.addEventListener("click",function(e){var b=e.target.closest("button");if(!b)return;
  if(b.classList.contains("kbb")){e.preventDefault();var id=b.dataset.id,i=sel.indexOf(id);if(i>=0)sel.splice(i,1);else{if(sel.length>=2)sel=[sel[0]];sel.push(id);}moreOpen=false;draw();
   try{var F0="direct";try{F0=sessionStorage.getItem("f")||"direct";}catch(y){}navigator.sendBeacon("/c?f="+encodeURIComponent(F0)+"&s=fudosan&k="+encodeURIComponent(("くらべる｜"+BY[id].n).slice(0,40)));}catch(x){}
   if(sel.length===2)scrollTo({top:Math.max(0,card.getBoundingClientRect().top+scrollY-70),behavior:"smooth"});}
  else if(b.classList.contains("mo")){moreOpen=true;draw();}
  else if(b.classList.contains("ch")){sel=[sel[0]];draw();var q=FQ.querySelector("input");if(q){scrollTo({top:Math.max(0,q.getBoundingClientRect().top+scrollY-90),behavior:"smooth"});}}});
bar.addEventListener("click",function(e){if(e.target.closest("button")){sel=[];draw();}});
fetch("/assets/towns.json").then(function(r){return r.json()}).then(function(d){TW=d;d.forEach(function(t){BY[t.id]=t});
  var v=(new URLSearchParams(location.search).get("vs")||"").split(",").filter(function(x){return BY[x]}).slice(0,2);sel=v;
  addBtns();new MutationObserver(addBtns).observe(FQ,{childList:true,subtree:true});draw();}).catch(function(){});
})();
