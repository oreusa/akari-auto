"""11/10 オーナーOK「いつもの物」（見本 v2）→ /okaimono のはじめの画面。
?k= が無い時に出す：次のセールの帯・いつもの物（この端末に保存）・きょうお得な物・21種類の絵のボタン。
初めての人は「いつも買う物をえらぶ」→「◯つで始める」。種類を押すと今までの くらべる画面（?k=）へ。
しるし：値下がり中＝いちばん安い物の値段が、しらべた日の中で今いちばん安く、3%以上下がった（price-history）。
        お得＝しらべた物の平均より25%以上安い（L・kgが混ざる種類は単位がちがうので出さない）。
なくなる日：買った日（本人が入れる）＋いちばん安い物の量÷1か月に使う量（真ん中のボタンの量）。
okai_v4.py が読み込む（JS は v4 の JS の中で動く：C・st・MY・pick・months などを使う）。"""
import json

# 21種類の線の絵（24x24）
ICON = {
 "water": '<path d="M10 2.5h4v2.2l1.6 2.3V20a1 1 0 0 1-1 1H9.4a1 1 0 0 1-1-1V7l1.6-2.3z"/><path d="M8.4 11.5h7.2M8.4 16.5h7.2"/>',
 "soda": '<path d="M10 2.5h4v2.2l1.6 2.3V20a1 1 0 0 1-1 1H9.4a1 1 0 0 1-1-1V7l1.6-2.3z"/><circle cx="11" cy="16" r=".9"/><circle cx="13" cy="13" r=".7"/><circle cx="11.5" cy="10.5" r=".6"/>',
 "rice": '<path d="M4 11h16a8 8 0 0 1-16 0z"/><path d="M7 11c.5-2 2.5-3 5-3s4.5 1 5 3"/><path d="M9 21h6"/>',
 "tp": '<ellipse cx="9" cy="7.5" rx="5" ry="3"/><path d="M4 7.5v9c0 1.7 2.2 3 5 3s5-1.3 5-3v-9"/><path d="M14 16.5h6.5v-9H14"/><ellipse cx="9" cy="7.5" rx="1.4" ry=".8"/>',
 "tea": '<path d="M10 2.5h4v2.2l1.6 2.3V20a1 1 0 0 1-1 1H9.4a1 1 0 0 1-1-1V7l1.6-2.3z"/><path d="M12 17c-2-1-2.2-3.6 0-6 2.2 2.4 2 5 0 6z"/><path d="M12 17v-4"/>',
 "coffee": '<path d="M5 9h11v5a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5z"/><path d="M16 10.5h1.5a2 2 0 0 1 0 4H16"/><path d="M8.5 3.5c-.8 1 .8 2 0 3M12 3.5c-.8 1 .8 2 0 3"/><path d="M4 21h13"/>',
 "detergent": '<path d="M6.5 8h11l1 12.5H5.5z"/><path d="M9 8V4.5h6V8"/><path d="M12 11.5c-1.5 2-2 3-2 3.8a2 2 0 0 0 4 0c0-.8-.5-1.8-2-3.8z"/>',
 "softener": '<path d="M6.5 8h11l1 12.5H5.5z"/><path d="M9 8l1-3.5h4L15 8"/><path d="M9 15c1-1.2 2-1.2 3 0s2 1.2 3 0"/>',
 "shampoo": '<path d="M7.5 10h9v9.5a1.5 1.5 0 0 1-1.5 1.5H9a1.5 1.5 0 0 1-1.5-1.5z"/><path d="M10 10V7.5h4V10M12 7.5V5h4"/><path d="M10.5 14.5h3"/>',
 "bodysoap": '<path d="M7.5 10h9v9.5a1.5 1.5 0 0 1-1.5 1.5H9a1.5 1.5 0 0 1-1.5-1.5z"/><path d="M10 10V7.5h4V10M12 7.5V5h4"/><circle cx="11" cy="15" r="1.4"/><circle cx="13.6" cy="16.8" r=".9"/>',
 "dish": '<rect x="4" y="13" width="11" height="6" rx="1.5"/><path d="M4 16h11"/><path d="M18 4c-1.6 2.2-2.2 3.4-2.2 4.3a2.2 2.2 0 0 0 4.4 0c0-.9-.6-2.1-2.2-4.3z"/>',
 "tissue": '<path d="M3.5 11h17v8.5h-17z"/><path d="M9 11c0-3 1.5-5.2 3-6.3 1.5 1.1 3 3.3 3 6.3"/>',
 "diaper": '<path d="M3.5 7h17l-2 6.2c-1.1 3.8-4 5.8-6.5 5.8s-5.4-2-6.5-5.8z"/><path d="M3.5 7l4.5 3.2M20.5 7L16 10.2"/>',
 "wipes": '<rect x="3.5" y="7" width="17" height="11" rx="3"/><path d="M8.5 10h7v2.5h-7z"/>',
 "trash": '<path d="M6 9.5h12l-1 11H7z"/><path d="M8 9.5c0-2 1.5-3 4-3s4 1 4 3"/><path d="M10.5 6.5L9.5 4M13.5 6.5l1-2.5"/>',
 "battery": '<rect x="8" y="5" width="8" height="15.5" rx="1.5"/><path d="M10.5 3h3v2h-3z"/><path d="M12 10v4M10 12h4"/>',
 "mask": '<path d="M5.5 8.5h13v6a3 3 0 0 1-3 3h-7a3 3 0 0 1-3-3z"/><path d="M5.5 10H4a2 2 0 0 0 0 4h1.5M18.5 10H20a2 2 0 0 1 0 4h-1.5"/><path d="M8 11.5h8M8 14h8"/>',
 "pasta": '<path d="M4 12h16a8 8 0 0 1-16 0z"/><path d="M8 12c0-2 1-2 1-4s-1-2-1-4M11.5 12c0-2 1-2 1-4s-1-2-1-4M15 12c0-2 1-2 1-4"/>',
 "beans": '<ellipse cx="12" cy="12" rx="5.5" ry="7.5" transform="rotate(35 12 12)"/><path d="M8.2 16.5c3-2 1.5-6.5 7.6-9"/>',
 "dogfood": '<path d="M8.6 8.6l6.8 6.8"/><circle cx="6.6" cy="8.4" r="2"/><circle cx="8.4" cy="6.6" r="2"/><circle cx="15.6" cy="17.4" r="2"/><circle cx="17.4" cy="15.6" r="2"/>',
 "catfood": '<path d="M4.5 13.5a7.5 5 0 0 0 15 0z"/><path d="M8 13.5l1-5 2 1.8h2l2-1.8 1 5"/>',
}
ORDER = ["water", "soda", "rice", "tp", "tea", "coffee", "detergent", "softener", "shampoo", "bodysoap", "dish",
         "tissue", "diaper", "wipes", "trash", "battery", "mask", "pasta", "beans", "dogfood", "catfood"]

CSS = """
#okh{max-width:520px;margin:0 auto 10px;color:#1C1C1C}
#okh .en{font-family:Jost,sans-serif;letter-spacing:.18em;font-size:10px;color:#8A8A8E}
#okh .oh-st{display:flex;flex-wrap:wrap;align-items:center;gap:2px 10px;margin:8px 16px 0;padding:9px 12px;border-radius:12px;background:#F4F4F6;font-size:11.5px;color:#55555A}
#okh .oh-st .en{color:#1C1C1C}
#okh .oh-st a{margin-left:auto;color:#1C1C1C;text-decoration:none;font-weight:700}#okh .oh-st a b{color:#B3261E;margin-left:4px}
#okh .oh-h2{display:flex;align-items:baseline;gap:8px;margin:20px 16px 8px;font-family:"Shippori Mincho",serif;font-weight:600;font-size:17px;letter-spacing:.06em}
#okh .oh-h2 small{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11.5px;color:#8A8A8E;font-weight:500;letter-spacing:0}
#okh .oh-h2 a{margin-left:auto;font:700 13px "Zen Kaku Gothic New",sans-serif;color:#1C1C1C;text-decoration:none;border-bottom:1px solid #1C1C1C;letter-spacing:0}
#okh .oh-bd{display:flex;flex-direction:column;gap:8px;margin:0 16px}
#okh .oh-it{position:relative;display:flex;align-items:center;gap:12px;padding:10px 10px 10px 12px;border:1px solid #E6E6E8;border-radius:14px;background:#fff;overflow:hidden}
#okh .oh-it:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:#C9C9CE}
#okh .oh-it.buy:before{background:#1F7A4D}#okh .oh-it.deal:before{background:#2F5E9E}
#okh .oh-ph{position:relative;flex:none;width:68px;height:68px;padding:0;border:0;background:none;cursor:pointer}
#okh .oh-ph img{width:68px;height:68px;object-fit:cover;border-radius:10px;border:1px solid #F0F0F2;display:block}
#okh .oh-ph .oh-ic{position:absolute;right:-6px;bottom:-6px;width:26px;height:26px}
#okh .oh-ic{display:grid;place-items:center;border-radius:50%;border:1px solid #E6E6E8;background:#fff}
#okh .oh-ic svg,#okh .oh-tl svg{fill:none;stroke:#1C1C1C;stroke-width:1.3;stroke-linecap:round;stroke-linejoin:round}
#okh .oh-ph .oh-ic svg{width:16px;height:16px}
#okh .oh-b{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px;padding:0;border:0;background:none;text-align:left;font:inherit;color:inherit;cursor:pointer}
#okh .oh-t{display:flex;flex-wrap:wrap;align-items:center;gap:2px 6px}#okh .oh-t b{font-size:14.5px;white-space:nowrap}
#okh .oh-sg{flex:none;white-space:nowrap;font-style:normal;font-size:11px;font-weight:700;padding:2px 8px;border-radius:99px;background:#F0F0F2;color:#55555A}
#okh .buy .oh-sg{background:#E6F3EC;color:#1F7A4D}#okh .deal .oh-sg{background:#E8EEF7;color:#2F5E9E}
#okh .oh-pz{font-size:11.5px}#okh .oh-pz b{font:500 22px Jost,sans-serif;letter-spacing:-.01em}
#okh .oh-pz small{margin-left:6px;font-size:11px;color:#6A6A6E}
#okh .buy .oh-pz small{color:#1F7A4D;font-weight:700}#okh .deal .oh-pz small{color:#2F5E9E;font-weight:700}
#okh .oh-nm{font-size:10.5px;color:#8A8A8E;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#okh .oh-lf{margin-left:auto;font-size:11px;white-space:nowrap;color:#6A6A6E;padding:0;border:0;background:none;font-family:inherit;cursor:pointer}
#okh .oh-lf.low{color:#B3261E;font-weight:700}#okh .oh-lf.set{border-bottom:1px dashed #8A8A8E}
#okh .oh-go{flex:none;width:58px;padding:9px 0;border-radius:12px;background:#1C1C1C;color:#fff;font-size:11px;font-weight:700;line-height:1.35;text-align:center;text-decoration:none}
#okh .buy .oh-go{background:#1F7A4D}#okh .deal .oh-go{background:#2F5E9E}
#okh .oh-sum{margin:10px 16px 0;padding:14px;border-radius:16px;background:#F4F4F6;font-size:14px}
#okh .oh-sum small{display:block;font-size:11.5px;color:#6A6A6E;margin-top:2px}
#okh .oh-two{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
#okh .oh-two button{padding:10px 4px;border:1px solid #D6D6DA;border-radius:12px;background:#fff;font:700 12px "Zen Kaku Gothic New",sans-serif;color:#1C1C1C;white-space:nowrap;cursor:pointer}
#okh .oh-two button[disabled]{color:#9A9A9E}
#okh .oh-help{margin:8px 0 0;font-size:12px;line-height:1.7;color:#4A4A4E}
#okh .oh-tls{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:0 16px}
#okh .oh-tl{position:relative;display:flex;flex-direction:column;align-items:center;gap:4px;padding:11px 2px 8px;border:1px solid #E6E6E8;border-radius:14px;background:#fff;font:500 11px "Zen Kaku Gothic New",sans-serif;color:#1C1C1C;line-height:1.25;cursor:pointer}
#okh .oh-tl svg{width:24px;height:24px;stroke-width:1.2}
#okh .oh-tl[aria-pressed="true"]{border-color:#1C1C1C;box-shadow:inset 0 0 0 1px #1C1C1C}
#okh .oh-tl[aria-pressed="true"]:after{content:"✓";position:absolute;top:3px;right:6px;font-size:11px;font-weight:700}
#okh .oh-pk{margin:14px 16px 0;padding:18px 14px 14px;border:1px solid #E6E6E8;border-radius:18px;text-align:center}
#okh .oh-pk h2{margin:0;font-family:"Shippori Mincho",serif;font-weight:600;font-size:21px;line-height:1.5;letter-spacing:.08em}
#okh .oh-pk p{margin:8px 0 14px;font-size:12.5px;line-height:1.7;color:#4A4A4E}
#okh .oh-pk .oh-tls{margin:0}
#okh .oh-start{position:sticky;bottom:calc(84px + env(safe-area-inset-bottom));z-index:5;display:block;width:100%;margin:14px 0 0;padding:14px;border:0;border-radius:99px;background:#1C1C1C;color:#fff;font:700 14.5px "Zen Kaku Gothic New",sans-serif;letter-spacing:.06em;box-shadow:0 6px 18px rgba(0,0,0,.18);cursor:pointer}
#okh .oh-start[disabled]{background:#B8B8BC;box-shadow:none}
#okh .oh-note{margin:16px 16px 0;font-size:11.5px;line-height:1.7;color:#8A8A8E}
#okh .oh-date{position:absolute;opacity:0;width:1px;height:1px;pointer-events:none}
.v4 .ohb{display:inline-block;margin:10px 16px 0;font-size:13px;font-weight:700;color:#1C1C1C;text-decoration:none;border-bottom:1px solid #1C1C1C}
.v4 .ohv{margin:10px 16px 0;padding:10px 12px;border-radius:12px;background:#F4F4F6;font-size:12.5px;line-height:1.6}
.v4 .ohv.buy{background:#EEF6F1}.v4 .ohv.deal{background:#EEF2F9}
.v4 .ohv i{font-style:normal;font-size:11px;font-weight:700;padding:2px 8px;border-radius:99px;margin-right:6px;background:#fff}
.v4 .ohv.buy i{color:#1F7A4D}.v4 .ohv.deal i{color:#2F5E9E}
html.ok-home .v4 #v4h,html.ok-home .v4 .kat,html.ok-home .v4 #v4m,html.ok-home .v4 #v4my,html.ok-home .v4 .more{display:none!important}
html:not(.ok-home) #okh{display:none}
"""

JS = r"""
/* ===== 11/10 いつもの物（はじめの画面） okai_home.py ===== */
var ICON=__ICON__,ORDER=__ORDER__,SALE=__SALE__,okh=document.getElementById("okh");
function ic(k){return '<svg viewBox="0 0 24 24" aria-hidden="true">'+(ICON[k]||"")+'</svg>';}
function oneUnit(c){var L=c.o.slice(),UT={};L.forEach(function(o){if(o.ut)UT[o.ut]=(UT[o.ut]||0)+1;});var u=Object.keys(UT).sort(function(a,b){return UT[b]-UT[a];})[0];
 if(u)L=L.filter(function(o){return o.ut===u;});return L.sort(function(a,b){return a.u-b.u;});}
function cheap(c){return oneUnit(c)[0];}
function md(d){return (+d.slice(5,7))+"/"+(+d.slice(8,10));}
/* しるし：値下がり中（しらべた日の中で今がいちばん安く、3%以上下がった）・お得（しらべた物の平均より25%以上安い） */
function sig(c){var o=cheap(c);if(!o)return null;var r={o:o,cls:"",lab:"",sub:""};
 if(o.h){var ds=Object.keys(o.h).sort();if(ds.length>=4){var vs=ds.map(function(d){return o.h[d];}),now=vs[vs.length-1],mn=Math.min.apply(null,vs),hi=Math.max.apply(null,vs);
  if(now<=mn&&hi>=now*1.03){var i=vs.length-1;while(i>0&&vs[i-1]===now)i--;r.cls="buy";r.lab="値下がり中";r.sub=md(ds[i])+"に"+Math.round((1-now/hi)*100)+"%下がった";return r;}}}
 if(c.avg&&c.unit!=="1L・1kg"&&o.u<=c.avg*0.75){r.cls="deal";r.lab="お得";r.sub="平均より"+Math.round((1-o.u/c.avg)*100)+"%安い";return r;}
 r.sub="平均なみ";return r;}
function ohut(c,o){return (c.unit==="1L・1kg"?(o.ut||"1L"):c.unit).replace("あたり","");}
function today(){var d=new Date(Date.now()+9*36e5);return d.toISOString().slice(0,10);}
function daysLeft(c,k){var m=MY[k];if(!m||!m.b||!c.use)return null;var o=cheap(c);if(!o)return null;var q=c.use[1][1],r=months(c,o,q);if(!r)return null;
 var used=(new Date(today())-new Date(m.b))/864e5;return Math.round(r.m*30.4-used);}
function row(k,mine){var c=C[k],s=sig(c);if(!s)return "";var o=s.o,lf="";
 if(mine){var dl=daysLeft(c,k);lf=dl==null?'<button type="button" class="oh-lf set" data-buy="'+k+'">買った日を入れる</button>':'<button type="button" class="oh-lf'+(dl<=7?" low":"")+'" data-buy="'+k+'">'+(dl<=0?"そろそろなくなる頃":"あと"+dl+"日")+'</button>';}
 return '<article class="oh-it '+s.cls+'"><button type="button" class="oh-ph" data-go="'+k+'" aria-label="'+esc(c.nm)+'をくらべる">'+(o.img?'<img src="'+esc(o.img)+'" alt="" loading="lazy" referrerpolicy="no-referrer">':'')+'<span class="oh-ic">'+ic(k)+'</span></button>'+
  '<div class="oh-b" data-go="'+k+'" role="link" tabindex="0"><span class="oh-t"><b>'+esc(c.nm)+'</b>'+(s.lab?'<i class="oh-sg">'+s.lab+'</i>':'')+lf+'</span>'+
  '<span class="oh-pz"><b>'+yen(o.u)+'</b>円/'+esc(ohut(c,o))+'<small>'+esc(s.sub)+'</small></span><span class="oh-nm">'+esc(o.n)+'　総額'+o.p.toLocaleString()+'円</span></div>'+
  '<a class="oh-go" href="'+esc(o.url)+'" rel="sponsored noopener" target="_blank" data-k="oh:'+esc(o.n.slice(0,20))+'">'+esc(o.w)+'<br>で見る</a></article>';}
function strip(){var h='<div class="oh-st"><span class="en">'+esc(upd())+'</span><span>楽天・Yahoo!の送料込み '+D.cats.reduce(function(a,c){return a+c.seen;},0).toLocaleString()+'件</span>';
 if(SALE){var now=Date.now(),st0=new Date(SALE.start+":00+09:00"),en=new Date(SALE.end+":00+09:00"),on=now>=st0;
  var dd=Math.ceil(((on?en:st0)-now)/864e5);h+='<a href="/kaimawari">'+esc(SALE.name)+(on?' 開催中<b>あと'+dd+'日</b>':' '+md(SALE.start)+'〜'+(SALE.tbd?'（予定）':'')+'<b>あと'+dd+'日</b>')+'</a>';}
 return h+'</div>';}
var pend={};
function deals(skip,n){return ORDER.filter(function(k){return C[k]&&skip.indexOf(k)<0;}).map(function(k){return [k,sig(C[k])];}).filter(function(x){return x[1]&&x[1].cls;})
 .sort(function(a,b){return (a[1].cls==="buy"?0:1)-(b[1].cls==="buy"?0:1)||a[1].o.u/(C[a[0]].avg||a[1].o.u)-b[1].o.u/(C[b[0]].avg||b[1].o.u);}).slice(0,n).map(function(x){return x[0];});}
function tiles(sel){return '<div class="oh-tls">'+ORDER.filter(function(k){return C[k];}).map(function(k){return '<button type="button" class="oh-tl" data-tl="'+k+'" aria-pressed="'+(!!sel[k])+'">'+ic(k)+'<span>'+esc(C[k].nm)+'</span></button>';}).join("")+'</div>';}
var deferred=null;window.addEventListener("beforeinstallprompt",function(e){e.preventDefault();deferred=e;});
function home(){document.documentElement.classList.add("ok-home");var ks=ORDER.filter(function(k){return MY[k]&&C[k];}),h=strip();
 if(!ks.length){var n=Object.keys(pend).length;
  h+='<section class="oh-pk"><h2>いつも買う物を、<br>えらんでください</h2><p>えらんだ物だけ、いちばん安い1個あたりと買い時を、毎日2回しらべてお見せします。登録はいりません（この端末だけに残ります）。</p>'+tiles(pend)+
   '<button type="button" class="oh-start" id="ohs"'+(n?'':' disabled')+'>'+(n?n+'つで始める':'えらぶと始められます')+'</button></section>'+
   '<h2 class="oh-h2"><span class="en">TODAY</span>きょうお得な物<small>値下がり中・平均より安い順</small></h2><section class="oh-bd">'+deals([],4).map(function(k){return row(k,false);}).join("")+'</section>';}
 else{var tot=0,shops={},bl=[];ks.forEach(function(k){var o=cheap(C[k]);if(o){tot+=o.p;shops[o.s]=1;}if(MY[k].b)bl.push(k);});
  h+='<h2 class="oh-h2"><span class="en">MY LIST</span>いつもの物<small>'+ks.length+'つ</small><a href="#ohadd">＋足す・外す</a></h2><section class="oh-bd">'+ks.map(function(k){return row(k,true);}).join("")+'</section>'+
   '<div class="oh-sum"><b>'+ks.length+'つまとめて</b> いちばん安い物で 合計 '+tot.toLocaleString()+'円・'+Object.keys(shops).length+'店<small>送料込みの総額です。お店ごとに届きます。'+(bl.length?'':'「買った日を入れる」を押すと、なくなる日をカレンダーに入れられます。')+'</small>'+
   '<div class="oh-two"><button type="button" id="ohcal"'+(bl.length?'':' disabled')+'>'+'なくなる日をカレンダーに'+'</button><button type="button" id="ohapp">ホーム画面に置く</button></div><p class="oh-help" id="ohhelp" hidden></p></div>';
  var dl=deals(ks,3);if(dl.length)h+='<h2 class="oh-h2"><span class="en">TODAY</span>ほかにもお得な物<small>値下がり中・平均より安い順</small></h2><section class="oh-bd">'+dl.map(function(k){return row(k,false);}).join("")+'</section>';
  h+='<h2 class="oh-h2" id="ohadd"><span class="en">ADD</span>ほかの物を足す<small>タップで足す・外す</small></h2>'+tiles(MY);}
 h+='<p class="oh-note">送料込みの値段 ÷ 量で、1個あたりをくらべています（'+esc(upd())+' 更新・1日2回）。「値下がり中」は11/1からの値段の動き、「お得」は同じ種類でしらべた物（送料込み）の平均とくらべています。なくなる日は、いちばん安い物の量と、1か月に使う量の目安から出しています。</p><input type="date" class="oh-date" id="ohd" aria-label="買った日">';
 okh.innerHTML=h;hbind();}
function hbind(){
 okh.querySelectorAll("[data-go]").forEach(function(b){b.onkeydown=function(e){if(e.key==="Enter")b.click();};b.onclick=function(e){if(e.target.closest("[data-buy]"))return;track("home:"+b.dataset.go);pick(b.dataset.go,true);window.scrollTo(0,0);};});
 okh.querySelectorAll("[data-tl]").forEach(function(b){b.onclick=function(){var k=b.dataset.tl,first=!ORDER.some(function(x){return MY[x]&&C[x];});
  if(first){if(pend[k])delete pend[k];else pend[k]=1;}else{if(MY[k])delete MY[k];else MY[k]={u:cheap(C[k]).u,d:AT};mysave();track("いつもの物:"+k);}
  var y=window.scrollY;home();window.scrollTo(0,y);};});
 var s=document.getElementById("ohs");if(s)s.onclick=function(){Object.keys(pend).forEach(function(k){MY[k]={u:cheap(C[k]).u,d:AT};});pend={};mysave();track("はじめる");home();window.scrollTo(0,0);};
 var di=document.getElementById("ohd"),cur="";
 okh.querySelectorAll("[data-buy]").forEach(function(b){b.onclick=function(e){e.stopPropagation();cur=b.dataset.buy;di.value=MY[cur].b||today();di.max=today();
  try{if(di.showPicker){di.showPicker();return;}}catch(e){}var v=prompt("買った日（例 "+today()+"）",di.value);if(v&&/^\d{4}-\d\d-\d\d$/.test(v)){MY[cur].b=v;mysave();home();}};});
 if(di)di.onchange=function(){if(cur&&MY[cur]&&/^\d{4}-\d\d-\d\d$/.test(di.value)){MY[cur].b=di.value;mysave();track("買った日:"+cur);var y=window.scrollY;home();window.scrollTo(0,y);}};
 var cal=document.getElementById("ohcal");if(cal)cal.onclick=function(){var ev=[];ORDER.forEach(function(k){if(!MY[k]||!C[k])return;var dl=daysLeft(C[k],k);if(dl==null)return;
   var d=new Date(Date.now()+9*36e5+Math.max(1,dl-3)*864e5).toISOString().slice(0,10).replace(/-/g,"");
   ev.push("BEGIN:VEVENT\r\nUID:okaimono-"+k+"-"+d+"@lifenote\r\nDTSTAMP:"+new Date().toISOString().replace(/[-:]/g,"").slice(0,15)+"Z\r\nDTSTART;VALUE=DATE:"+d+"\r\nSUMMARY:"+C[k].nm+"がそろそろなくなります\r\nDESCRIPTION:いちばん安い1個あたりを見る "+location.origin+"/okaimono?k="+k+"\r\nEND:VEVENT");});
  if(!ev.length)return;var t="BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//LIFE NOTE//okaimono//JA\r\n"+ev.join("\r\n")+"\r\nEND:VCALENDAR\r\n";
  var a=document.createElement("a");a.href=URL.createObjectURL(new Blob([t],{type:"text/calendar"}));a.download="okaimono.ics";document.body.appendChild(a);a.click();a.remove();track("カレンダー");};
 var ap=document.getElementById("ohapp"),hp=document.getElementById("ohhelp");if(ap)ap.onclick=function(){track("ホーム画面");
  if(deferred){deferred.prompt();deferred=null;return;}
  hp.hidden=false;hp.innerHTML=/iphone|ipad/i.test(navigator.userAgent)?'iPhone：下の <b>共有ボタン</b>（四角に上向きの矢印）→ <b>ホーム画面に追加</b>。次からアプリのように開けます。':'Android：右上の <b>︙</b> → <b>ホーム画面に追加</b>。次からアプリのように開けます。';};
}
function view(){if(st.k){document.documentElement.classList.remove("ok-home");render();}else home();}
"""


def js(sale):
    return (JS.replace("__ICON__", json.dumps(ICON, ensure_ascii=False))
              .replace("__ORDER__", json.dumps(ORDER))
              .replace("__SALE__", json.dumps(sale, ensure_ascii=False)))


def next_sale(path, now):
    """data/sales.json から、いま開催中か次のセール（終わった物は出さない）。note があるうちは日程が（予定）"""
    try:
        ss = json.load(open(path, encoding="utf-8")).get("sales", [])
    except Exception:
        return None
    t = now.strftime("%Y-%m-%dT%H:%M")
    up = sorted((s for s in ss if s.get("end", "") > t), key=lambda s: s["start"])
    if not up:
        return None
    s = up[0]
    return {"name": s["name"], "start": s["start"], "end": s["end"], "tbd": bool(s.get("note"))}
