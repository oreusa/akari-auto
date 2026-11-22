/* 11/22「本当に安い？」（/nesage を作り替え）。オーナー「見やすくて使いやすいなら月に任せる。どう見たらいいか分からないにならないように」。
   中身は scripts/honto.py（楽天の日用品の値段を 11/1 から毎日記録した data/price-history.json）。
   1画面で押す物は1つ：上の4つの切り替え（今が安い・上げてから下げた・いつもより高い・変わらない）→ 1品ずつ「楽天で見る」だけ。
   どの品も「なぜそう言えるか」を1文で書く（うちの記録の事実だけ）。グラフは見なくても分かる飾り。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,RM=S_.RM,D=S_.data;
var R=D.rows||[],TT=D.tt||{},C=D.cnt||{};
function yen(n){return Math.round(n).toLocaleString("ja-JP")}
function md(s){return (+s.slice(5,7))+"/"+(+s.slice(8,10))}
function at(s){var m=/(\d+)-(\d+)-(\d+) (\d+):(\d+)/.exec(s||"");return m?(+m[2])+"月"+(+m[3])+"日 "+(+m[4])+":"+m[5]+" にしらべた値段":""}
function img(u){return u?'<span class="hti"><img src="'+esc(u)+'" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.parentNode.classList.add(\'no\');this.remove()"></span>':'<span class="hti no"></span>'}
var TAB=[["a","今が安い","11/1からの記録で、いちばん安い値段になっている物です。"],
  ["b","上げて下げた","途中で値段が上がり、そのあと下がった物です。割引に見えても、11/1とくらべると安くなっていません。"],
  ["c","高い","ふだんより高くなっている物です。急がない物は、待つのも手です。"],
  ["d","変わらない","11/1から値段がほとんど変わっていない物です。セールの間も、ふだんと同じ値段です。"]];
var BADGE={a:"記録でいちばん安い",b:"11/1とくらべると安くない",c:"いつもより高い"};
/* グラフ：11/1から今日までの値段（点線＝はじめの日の値段・点＝今） */
function graph(x){
  var W=320,H=78,T=18,B=8,h=x.h,lo=x.lo,hi=x.hi,n=h.length;
  if(hi===lo){lo=lo*.95;hi=hi*1.05}
  var pad=(hi-lo)*.12;lo-=pad;hi+=pad;
  var X=function(i){return n>1?4+i*(W-12)/(n-1):W/2},Y=function(p){return T+(hi-p)/(hi-lo)*(H-T-B)};
  var seg=[],cur="",li=-1,pk=-1;
  h.forEach(function(p,i){if(p==null){if(cur)seg.push(cur);cur="";return}cur+=(cur?"L":"M")+X(i).toFixed(1)+" "+Y(p).toFixed(1);li=i;if(pk<0||p>h[pk])pk=i});
  if(cur)seg.push(cur);
  var fy=Y(x.first).toFixed(1),s='<svg class="htgr" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" aria-hidden="true">';
  s+='<line x1="0" x2="'+W+'" y1="'+fy+'" y2="'+fy+'" class="htf"/>';
  s+=seg.map(function(d){return '<path d="'+d+'" class="htl"/>'}).join("");
  if(x.v==="b"&&pk>=0)s+='<circle cx="'+X(pk).toFixed(1)+'" cy="'+Y(h[pk]).toFixed(1)+'" r="3" class="htpk"/>';
  if(li>=0)s+='<circle cx="'+X(li).toFixed(1)+'" cy="'+Y(h[li]).toFixed(1)+'" r="4.2" class="htd"/>';
  s+='</svg>';
  var top='<span class="htf1">'+(x.d0.slice(5)==="11-01"?"11/1":md(x.d0))+'の値段 '+yen(x.first)+'円（点線）</span>';
  if(x.v==="b"&&pk>=0)top+='<span class="htf2">いちばん高い日 '+yen(h[pk])+'円</span>';
  return '<div class="htg"><div class="htgl">'+top+'</div>'+s+'<div class="htax"><span>'+md(x.d0)+'</span><span>今日</span></div></div>';
}
function card(x,k){
  return '<li class="htc v'+x.v+'"><div class="htt">'+img(x.img)+'<span class="httx"><i>'+esc(TT[x.c]||"")+'</i><b>'+esc(x.n)+'</b>'+(x.s?'<small>'+esc(x.s)+'</small>':'')+'</span></div>'+
    '<div class="htp"><span class="htn"><small>今</small>'+yen(x.now)+'<small>円</small></span><span class="htb">'+BADGE[x.v]+'</span></div>'+
    graph(x)+'<p class="htw">'+esc(x.why)+'</p>'+
    '<a class="htgo" href="'+esc(x.url)+'" target="_blank" rel="sponsored noopener" data-k="本当に安い｜'+x.v+'｜'+(k+1)+'">楽天で見る<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg></a></li>';
}
function quiet(list){
  var by={};list.forEach(function(x){(by[x.c]=by[x.c]||[]).push(x)});
  return Object.keys(TT).filter(function(c){return by[c]}).map(function(c){
    return '<details class="htq"><summary><b>'+esc(TT[c])+'</b><span>'+by[c].length+'品</span></summary><ul>'+by[c].map(function(x,k){
      return '<li><a href="'+esc(x.url)+'" target="_blank" rel="sponsored noopener" data-k="本当に安い｜d｜'+esc(TT[c])+'">'+img(x.img)+'<span class="httx"><b>'+esc(x.n)+'</b><small>'+esc(x.why)+'</small></span><span class="htqn">'+yen(x.now)+'<small>円</small></span></a></li>'}).join("")+'</ul></details>'}).join("");
}
var h='<section class="hero"><h1 class="h1t">'+esc(D.h1)+'</h1><p class="htlead">楽天の日用品'+D.n+'品の値段を、'+md(D.since)+'から毎日記録しています。セールの値段が本当に安いかを、記録でたしかめられます。</p>'+
  (D.bf?'<p class="htbf">ブラックフライデーは '+esc(D.bf)+' まで</p>':'')+'<p class="fat">'+at(D.at)+'</p></section>';
h+='<div class="htseg" id="htseg" role="tablist">'+TAB.map(function(t,i){return '<button type="button" role="tab" data-v="'+t[0]+'" aria-selected="'+(i?"false":"true")+'"><b>'+t[1]+'</b><small>'+(C[t[0]]||0)+'品</small></button>'}).join("")+'</div>';
h+=TAB.map(function(t,i){var L=R.filter(function(x){return x.v===t[0]});
  return '<section class="htcat" id="h-'+t[0]+'"'+(i?' hidden':'')+'><p class="htcap">'+t[2]+'</p>'+
    (L.length?(t[0]==="d"?quiet(L):'<ol class="htl0">'+L.map(card).join("")+'</ol>'):'<p class="htem">いまは、ありません。</p>')+'</section>'}).join("");
h+='<section class="fno htno"><h2>しらべ方</h2><p>楽天市場でよく買われている日用品（水・お米・トイレットペーパー・洗剤・おむつ・電気毛布など）を、毎日2回しらべて、いちばん安い値段を1日1つ記録しています。値段は送料込みで、しらべた時のものです（お店で変わることがあります）。</p>'+
  '<p>「今が安い」は、記録した中でいちばん安く、はじめの日より3%以上安い物。「上げてから下げた」は、途中で8%以上上がり、今の値段がはじめの日とくらべて3%も安くない物。「いつもより高い」は、記録のまん中の値段より5%以上高い物です。1日で半分や2倍になった物は、量やセットの数が変わった見え方のことがあるので入れていません。</p>'+
  '<p>リンクは楽天の広告（PR）です。</p>'+
  '<p class="htmore"><a href="/okaimono">日用品を1個あたりの値段でくらべる</a>'+(D.room?'<a href="'+esc(D.room)+'" target="_blank" rel="noopener" data-k="本当に安い｜ROOM">楽天ROOMでも紹介しています</a>':'')+'</p></section>';
var st=document.createElement("style");st.textContent=[
".htlead{margin:10px 0 0;font-size:14px;line-height:1.75;color:var(--sub)}",
".htbf{display:inline-block;margin:12px 0 0;padding:5px 12px;border-radius:999px;border:1px solid #7FBF8E;font-size:12.5px;font-weight:600;color:#2C7A45}",
"html.nt .htbf{border-color:#3F7A52;color:#8FD3A4}",
".htseg{position:sticky;top:calc(48px + env(safe-area-inset-top,0px));box-shadow:0 -8px 0 var(--bg);z-index:5;display:grid;grid-template-columns:repeat(4,1fr);gap:2px;margin:18px 0 0;padding:4px;border-radius:16px;background:var(--chip)}",
".htseg button{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;min-height:52px;padding:6px 2px;border:0;border-radius:12px;background:none;color:var(--sub);font:500 12.5px/1.2 var(--sans);cursor:pointer;-webkit-tap-highlight-color:transparent}",
".htseg button b{font-weight:600;letter-spacing:-.01em}.htseg button small{font-size:11.5px;font-variant-numeric:tabular-nums}",
".htseg button[aria-selected=true]{background:var(--on);color:var(--ont)}",
".htcat{min-height:calc(100vh - 120px)}",
".htcap{margin:14px 2px 4px;font-size:13.5px;line-height:1.7;color:var(--sub)}",
".htl0{list-style:none;margin:0;padding:0}",
".htc{margin:12px 0 0;padding:16px;border:1px solid var(--line);border-radius:20px;background:var(--card)}",
".htt{display:grid;grid-template-columns:56px 1fr;gap:12px;align-items:center}",
".hti{display:block;width:56px;height:56px;border-radius:12px;overflow:hidden;background:#fff;border:1px solid var(--line)}.hti img{width:100%;height:100%;object-fit:contain}.hti.no{background:var(--chip)}",
".httx{min-width:0;display:flex;flex-direction:column;gap:2px}.httx i{font-style:normal;font-size:11.5px;color:var(--mut)}",
".httx b{font-weight:500;font-size:14px;line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.httx small{font-size:11.5px;color:var(--mut);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}",
".htp{display:flex;align-items:baseline;justify-content:space-between;gap:8px;flex-wrap:wrap;margin:14px 0 0}",
".htn{font:600 28px/1 var(--sans);letter-spacing:-.02em;font-variant-numeric:tabular-nums}.htn small{font-size:13px;font-weight:500;margin:0 2px}.htn small:first-child{color:var(--sub);margin:0 6px 0 0}",
".htb{padding:4px 10px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}",
".va .htb{background:#E7F5EA;color:#22703C}.vb .htb{background:#FBF0DC;color:#8A5A00}.vc .htb{background:#F8E4E1;color:#A33A2C}",
"html.nt .va .htb{background:#173222;color:#8FD3A4}html.nt .vb .htb{background:#33280F;color:#E8C27A}html.nt .vc .htb{background:#3A1D1A;color:#F0A499}",
".htg{margin:12px 0 0}.htgl{display:flex;justify-content:space-between;gap:8px;font-size:11px;color:var(--mut)}",
".htgr{display:block;width:100%;height:78px;overflow:visible}",
".htl{fill:none;stroke:var(--ink);stroke-width:1.7;stroke-linejoin:round;stroke-linecap:round;vector-effect:non-scaling-stroke}",
".htf{stroke:var(--mut);stroke-width:1;stroke-dasharray:3 4;vector-effect:non-scaling-stroke}",
".htd{stroke:var(--card);stroke-width:2;vector-effect:non-scaling-stroke}.va .htd{fill:#2E9150}.vb .htd{fill:#C08A1E}.vc .htd{fill:#C2493A}",
".htpk{fill:var(--card);stroke:var(--ink);stroke-width:1.4;vector-effect:non-scaling-stroke}",
".htax{display:flex;justify-content:space-between;font-size:11px;color:var(--mut);font-variant-numeric:tabular-nums}",
".htw{margin:12px 0 0;font-size:14px;line-height:1.75;color:var(--ink)}",
".htgo{display:flex;align-items:center;justify-content:center;gap:4px;margin:14px 0 0;min-height:46px;border-radius:999px;background:var(--on);color:var(--ont);font:600 15px/1 var(--sans);text-decoration:none}",
".htgo svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2}",
".htq{border-bottom:1px solid var(--line)}.htq summary{display:flex;justify-content:space-between;align-items:center;min-height:52px;padding:0 2px;cursor:pointer;list-style:none;font-size:15px}",
".htq summary::-webkit-details-marker{display:none}.htq summary b{font-weight:500}.htq summary span{color:var(--mut);font-size:13px}",
".htq summary span::after{content:'';display:inline-block;width:7px;height:7px;margin:0 4px 2px 10px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(45deg);transition:transform .2s}",
".htq[open] summary span::after{transform:rotate(-135deg);margin-bottom:-2px}",
".htq ul{list-style:none;margin:0 0 8px;padding:0}.htq li a{display:grid;grid-template-columns:44px 1fr auto;gap:10px;align-items:center;padding:10px 0;color:var(--ink);text-decoration:none;border-top:1px solid var(--line)}",
".htq .hti{width:44px;height:44px;border-radius:10px}.htqn{font:600 16px/1 var(--sans);font-variant-numeric:tabular-nums;white-space:nowrap}.htqn small{font-size:11px;font-weight:500;margin-left:1px}",
".htem{margin:24px 0;text-align:center;color:var(--sub)}",
".htno{margin-top:36px}.htmore{display:flex;flex-direction:column;gap:10px;margin-top:16px}.htmore a{color:var(--ink);text-underline-offset:3px}"
].join("");document.head.appendChild(st);
S_.main.innerHTML='<div class="wrap furu honto">'+h+'</div>';
function show(v,scroll){if(!$("#h-"+v))return;$$("#htseg button").forEach(function(b){b.setAttribute("aria-selected",b.dataset.v===v?"true":"false")});
  $$(".htcat").forEach(function(s){var on=s.id==="h-"+v;s.hidden=!on;if(on&&!RM)s.animate([{opacity:0},{opacity:1}],{duration:200,easing:"ease-out"})});
  try{history.replaceState(null,"",v==="a"?location.pathname+location.search:"#"+v)}catch(e){}
  if(scroll){var g=$("#htseg"),y=$("#h-"+v).getBoundingClientRect().top+scrollY-g.offsetHeight-56;if(scrollY>y)scrollTo({top:y,behavior:"auto"})}}
$("#htseg").addEventListener("click",function(e){var b=e.target.closest("button");if(b)show(b.dataset.v,1)});
var hs=location.hash.slice(1);if(/^[bcd]$/.test(hs))show(hs);
S_.ready();
})();
