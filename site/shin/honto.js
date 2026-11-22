/* 11/22「本当に安い？」（/nesage を作り替え）。中身は scripts/honto.py（楽天の日用品の値段を 11/1 から毎日記録した data/price-history.json）。
   v2（11/22 18:17 owner「よく分からないから月に任せる・本気で」）：切り替えのタブをやめ、開いた瞬間に答え（本当に安い品）が並ぶ形に。
   1行＝写真・品名・「11/1 3,990円 → 今 2,990円」・大きな −25%・小さな値段の線。押すと楽天（1行で押す物は1つ）。
   上から 本当に安い → 安く見えて11/1と同じくらい → いつもより高い → 変わらない（たたむ）。#b #c #d でその所へ。関西 links/shin/honto.js と同じ物。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,D=S_.data;
var R=D.rows||[],TT=D.tt||{},C=D.cnt||{};
function yen(n){return Math.round(n).toLocaleString("ja-JP")}
function md(s){return (+s.slice(5,7))+"/"+(+s.slice(8,10))}
function at(s){var m=/(\d+)-(\d+)-(\d+) (\d+):(\d+)/.exec(s||"");return m?(+m[2])+"月"+(+m[3])+"日 "+(+m[4])+":"+m[5]+" にしらべた値段":""}
function img(u){return u?'<span class="hti"><img src="'+esc(u)+'" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.parentNode.classList.add(\'no\');this.remove()"></span>':'<span class="hti no"></span>'}
/* 小さな値段の線（点線＝11/1の値段・点＝今） */
function spark(x){
  var W=64,H=24,h=x.h||[],lo=x.lo,hi=x.hi,n=h.length;if(!n)return "";
  if(hi===lo){lo*=.95;hi*=1.05}
  var X=function(i){return n>1?2+i*(W-6)/(n-1):W/2},Y=function(p){return 3+(hi-p)/(hi-lo)*(H-6)},d="",li=0;
  h.forEach(function(p,i){if(p==null)return;d+=(d?"L":"M")+X(i).toFixed(1)+" "+Y(p).toFixed(1);li=i});
  return '<svg class="hsp" viewBox="0 0 '+W+' '+H+'" aria-hidden="true"><line x1="0" x2="'+W+'" y1="'+Y(x.first).toFixed(1)+'" y2="'+Y(x.first).toFixed(1)+'" class="hsf"/><path d="'+d+'" class="hsl"/><circle cx="'+X(li).toFixed(1)+'" cy="'+Y(h[li]).toFixed(1)+'" r="2.6" class="hsd"/></svg>';
}
function row(x,k){
  var ref=x.ref||["",x.first],fact='<span class="hrf">'+esc(ref[0])+' '+yen(ref[1])+'円 <i>→</i> 今 <em>'+yen(x.now)+'円</em></span>',big;
  if(x.v==="a")big='<b>−'+Math.round((1-x.now/x.first)*100)+'<small>%</small></b>';
  else if(x.v==="c")big='<b>+'+Math.round((x.now/ref[1]-1)*100)+'<small>%</small></b>';
  else{var df=x.now-x.first;big='<b class="hrt">'+(df===0?"11/1と同じ":df>0?"11/1より<br>"+yen(df)+"円高い":"11/1より<br>"+yen(-df)+"円安いだけ")+'</b>'}
  return '<li><a class="hr v'+x.v+'" href="'+esc(x.url)+'" target="_blank" rel="sponsored noopener" data-k="本当に安い｜'+x.v+'｜'+(k+1)+'">'+img(x.img)+
    '<span class="hrm"><b>'+esc(x.n)+'</b>'+fact+'</span><span class="hrr">'+big+spark(x)+'</span></a></li>';
}
function sec(v,title,cap,L){
  if(!L.length)return "";
  return '<section class="hsec" id="'+v+'"><h2 class="hh v'+v+'"><span>'+title+'</span><small>'+L.length+'品</small></h2><p class="hcap">'+cap+'</p><ol class="hlist">'+L.map(row).join("")+'</ol></section>';
}
var A=R.filter(function(x){return x.v==="a"}),B=R.filter(function(x){return x.v==="b"}),Cc=R.filter(function(x){return x.v==="c"}),Dd=R.filter(function(x){return x.v==="d"});
var h='<section class="hero htop"><h1 class="h1t">'+esc(D.h1)+'</h1>'+
  '<p class="hans">楽天の日用品'+D.n+'品を'+md(D.since)+'から毎日記録してくらべると、<b>本当に安くなっているのは '+A.length+'品</b>でした。</p>'+
  '<p class="hmeta">'+(D.bf?'<span class="htbf">ブラックフライデー '+esc(D.bf)+'まで</span>':'')+'<span>'+at(D.at)+'</span></p></section>';
h+=sec("a","本当に安い","11/1からの記録で、いちばん安い値段になっている物です。押すと楽天のページが開きます。",A);
if(!A.length)h+='<p class="hem">いまは、11/1より本当に安くなっている物はありません。</p>';
h+=sec("b","安く見えて、11/1と同じくらい","途中で値段が上がって、そのあと下がった物です。割引に見えても、11/1とくらべると安くなっていません。",B);
h+=sec("c","いつもより高い","ふだんの値段（記録のまん中）より高くなっている物です。急がなければ、待つのも手です。",Cc);
if(Dd.length){var by={};Dd.forEach(function(x){(by[x.c]=by[x.c]||[]).push(x)});
  h+='<section class="hsec" id="d"><details class="hq"><summary><span>セール中も値段が変わらない物</span><small>'+Dd.length+'品</small></summary><p class="hcap">11/1から値段がほとんど変わっていない物です。</p>'+
    Object.keys(TT).filter(function(c){return by[c]}).map(function(c){return '<h3 class="hq3">'+esc(TT[c])+'</h3><ul class="hql">'+by[c].map(function(x){
      return '<li><a href="'+esc(x.url)+'" target="_blank" rel="sponsored noopener" data-k="本当に安い｜d｜'+esc(TT[c])+'"><b>'+esc(x.n)+'</b><span>'+yen(x.now)+'円</span></a></li>'}).join("")+'</ul>'}).join("")+'</details></section>'}
h+='<section class="fno htno"><h2>しらべ方</h2><p>楽天市場でよく買われている日用品を毎日2回しらべ、いちばん安い値段（送料込み）を1日1つ記録しています。値段はしらべた時のもので、お店で変わることがあります。</p>'+
  '<p>「本当に安い」＝記録の中でいちばん安く、はじめの日より3%以上安い物。「安く見えて11/1と同じくらい」＝途中で8%以上上がり、今もはじめの日より3%以上は安くない物。「いつもより高い」＝記録のまん中の値段より5%以上高い物。1日で半分や2倍になった物は、量やセットの数が変わった見え方のことがあるので入れていません。</p>'+
  '<p>リンクは楽天の広告（PR）です。</p>'+
  '<p class="htmore"><a href="/okaimono">日用品を1個あたりの値段でくらべる</a>'+(D.room?'<a href="'+esc(D.room)+'" target="_blank" rel="noopener" data-k="本当に安い｜ROOM">楽天ROOMでも紹介しています</a>':'')+'</p></section>';
var st=document.createElement("style");st.textContent=[
".hans{margin:12px 0 0;font-size:16px;line-height:1.7;color:var(--ink)}.hans b{font-weight:600;background:linear-gradient(transparent 62%,rgba(46,145,80,.22) 0)}",
"html.nt .hans b{background:linear-gradient(transparent 62%,rgba(120,210,150,.28) 0)}",
".hmeta{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:12px 0 0;font-size:12px;color:var(--mut)}",
".htbf{padding:4px 10px;border-radius:999px;border:1px solid #7FBF8E;font-weight:600;color:#2C7A45}html.nt .htbf{border-color:#3F7A52;color:#8FD3A4}",
".hsec{margin:30px 0 0}",
".hh{display:flex;align-items:baseline;gap:8px;margin:0;font:600 20px/1.35 var(--sans);letter-spacing:.01em}.hh small{font-size:13px;font-weight:500;color:var(--mut)}",
".hh span::before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;margin:0 8px 3px 0;vertical-align:middle}",
".hh.va span::before,.hr.va .hsd{background:#2E9150;fill:#2E9150}.hh.vb span::before,.hr.vb .hsd{background:#C08A1E;fill:#C08A1E}.hh.vc span::before,.hr.vc .hsd{background:#C2493A;fill:#C2493A}",
".hcap{margin:6px 0 0;font-size:13px;line-height:1.7;color:var(--sub)}",
".hlist{list-style:none;margin:8px 0 0;padding:0}.hlist li{border-bottom:1px solid var(--line)}",
".hr{display:grid;grid-template-columns:56px minmax(0,1fr) 72px;gap:12px;align-items:center;padding:12px 0;color:var(--ink);text-decoration:none;-webkit-tap-highlight-color:transparent}",
".hr:active{opacity:.6}",
".hti{display:block;width:56px;height:56px;border-radius:12px;overflow:hidden;background:#fff;border:1px solid var(--line)}.hti img{width:100%;height:100%;object-fit:contain}.hti.no{background:var(--chip)}",
".hrm{min-width:0;display:flex;flex-direction:column;gap:4px}",
".hrm b{font-weight:500;font-size:13.5px;line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}",
".hrf{font-size:12.5px;color:var(--sub);font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hrf i{font-style:normal;color:var(--mut);margin:0 1px}.hrf em{font-style:normal;font-weight:600;color:var(--ink)}",
".hrr{display:flex;flex-direction:column;align-items:flex-end;gap:4px;text-align:right}",
".hrr b{font:600 22px/1 var(--sans);letter-spacing:-.02em;font-variant-numeric:tabular-nums}.hrr b small{font-size:13px;margin-left:1px}",
".va .hrr b{color:#22703C}.vc .hrr b{color:#A33A2C}html.nt .va .hrr b{color:#8FD3A4}html.nt .vc .hrr b{color:#F0A499}",
".hrr b.hrt{font-size:12px;line-height:1.35;font-weight:600;color:#8A5A00;letter-spacing:0}html.nt .hrr b.hrt{color:#E8C27A}",
".hsp{display:block;width:64px;height:24px;overflow:visible}.hsl{fill:none;stroke:var(--ink);stroke-width:1.4;stroke-linejoin:round;stroke-linecap:round;opacity:.75}",
".hsf{stroke:var(--mut);stroke-width:1;stroke-dasharray:2 3}.hsd{stroke:var(--bg);stroke-width:1.2}",
".hem{margin:20px 0;color:var(--sub)}",
".hq{border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.hq summary{display:flex;align-items:center;gap:8px;min-height:56px;cursor:pointer;list-style:none;font:500 15px/1.4 var(--sans)}",
".hq summary::-webkit-details-marker{display:none}.hq summary small{color:var(--mut);font-size:13px}",
".hq summary::after{content:'';margin-left:auto;width:8px;height:8px;border-right:1.5px solid var(--mut);border-bottom:1.5px solid var(--mut);transform:rotate(45deg);transition:transform .2s}.hq[open] summary::after{transform:rotate(-135deg)}",
".hq3{margin:16px 0 4px;font-size:13px;font-weight:600;color:var(--sub)}.hql{list-style:none;margin:0;padding:0 0 4px}",
".hql a{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-top:1px solid var(--line);color:var(--ink);text-decoration:none;font-size:13px}",
".hql a b{font-weight:400;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hql a span{white-space:nowrap;font-variant-numeric:tabular-nums;color:var(--sub)}",
".htno{margin-top:40px}.htmore{display:flex;flex-direction:column;gap:10px;margin-top:16px}.htmore a{color:var(--ink);text-underline-offset:3px}"
].join("");document.head.appendChild(st);
S_.main.innerHTML='<div class="wrap furu honto">'+h+'</div>';
var hs=location.hash.slice(1);if(/^[bcd]$/.test(hs)){var t=$("#"+hs);if(t){if(hs==="d")$("details",t).open=true;setTimeout(function(){t.scrollIntoView({block:"start"})},80)}}
S_.ready();
})();
