/* ふるさと納税（1万円でもらえる量）と、値下がりした物。11/19 owner「ふるさと押したら前のページ飛ぶ」「その他も本気でやり直せ」。
   前は燈（関東）の古いページをそのまま中に出していた → 新しい土台で作り直し。関西・関東で同じファイル（関東は akari site/shin/）。
   D.kind = "furu"（cats）か "nesage"（downs・ups）。中身は燈が毎日しらべる data/furusato.json・nesage.json。 */
(function(){
"use strict";
var S_=window.SHIN,$=S_.$,$$=S_.$$,esc=S_.esc,RM=S_.RM,D=S_.data;
function yen(n){return Math.round(n).toLocaleString("ja-JP")+"円"}
function img(u){return u?'<span class="fim"><img src="'+esc(u)+'" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.parentNode.classList.add(\'no\');this.remove()"></span>':'<span class="fim no"></span>'}
function star(r){return r.av?'<span class="fst">★'+(+r.av).toFixed(2)+'<small>（'+(r.rc||0).toLocaleString("ja-JP")+'件）</small></span>':''}
function at(s){var m=/(\d+)-(\d+)-(\d+) (\d+):(\d+)/.exec(s||"");return m?(+m[2])+"月"+(+m[3])+"日 "+(+m[4])+":"+m[5]+" に調べ直し":""}
var h="",tabs=[],cur="";
if(D.kind==="furu"){
  var C=D.cats.filter(function(c){return c.top&&c.top.length});cur=C.length?C[0].key:"";
  h+='<section class="hero"><h1 class="h1t">'+esc(D.h1)+'</h1><p class="h1p">'+esc(D.sub)+'</p><p class="fat">'+at(D.at)+'</p></section>';
  h+='<div class="fseg" id="fseg" role="tablist">'+C.map(function(c,i){return '<button type="button" role="tab" data-v="'+c.key+'" aria-selected="'+(i?"false":"true")+'">'+esc(c.title)+'</button>'}).join("")+'</div>';
  h+=C.map(function(c,i){var u=c.unit,t=c.top[0];
    return '<section class="fcat" id="c-'+c.key+'"'+(i?' hidden':'')+'><div class="flead"><p>寄付1万円で、いちばん多くもらえる'+esc(c.title)+'</p><b>'+t.per+'<small>'+esc(u)+'</small></b>'+
      '<span>くらべた'+c.read+'品の平均は '+c.avg+esc(u)+'。上の物は約'+(c.avg?Math.round(t.per/c.avg*10)/10:"-")+'倍です。</span></div>'+
      '<ol class="flist">'+c.top.map(function(r,k){return '<li><a href="'+esc(r.url||r.plain)+'" target="_blank" rel="sponsored noopener" data-k="ふるさと｜'+esc(c.title)+'｜'+(k+1)+'">'+
        '<i class="frk">'+(k+1)+'</i>'+img(r.img)+'<span class="ftx"><b>'+esc(r.name)+'</b><small>'+esc(r.shop)+'</small><em>寄付 '+yen(r.price)+'（'+esc(r.amt)+'）'+star(r)+'</em></span>'+
        '<span class="fv"><b>'+r.per+'<small>'+esc(u)+'</small></b><small>1万円あたり</small></span></a></li>'}).join("")+'</ol></section>'}).join("");
  h+='<section class="fno"><h2>くらべ方</h2><p>楽天ふるさと納税の返礼品を毎日しらべ直し、商品名から量を読んで「寄付1万円あたり」に直しました。定期便・選べる物など、量が1つに決まらない物は入れていません。レビュー30件以上・★4.0以上の物だけで、同じ町は1つだけ出しています。</p>'+
    '<p>寄付できるのは12月31日までです。上限額は、年収と家族の数で変わります。リンクは楽天の広告（PR）です。</p></section>';
}else{
  var dn=D.downs||[],up=D.ups||[];cur="down";
  h+='<section class="hero"><h1 class="h1t">'+esc(D.h1)+'</h1><p class="h1p">'+esc(D.sub)+'</p><p class="fat">'+at(D.at)+'</p></section>';
  h+='<div class="fseg" id="fseg" role="tablist"><button type="button" role="tab" data-v="down" aria-selected="true">値下がり '+dn.length+'</button><button type="button" role="tab" data-v="up" aria-selected="false">値上がり '+up.length+'</button></div>';
  var row=function(r,k,dir){return '<li><a href="'+esc(r.url||r.plain)+'" target="_blank" rel="sponsored noopener" data-k="値下がり｜'+esc(r.title)+'">'+
    img(r.img)+'<span class="ftx"><i class="fcg">'+esc(r.title)+'</i><b>'+esc(r.name)+'</b><small>'+esc(r.shop)+'</small><em>'+star(r)+'</em></span>'+
    '<span class="fv '+dir+'"><b>'+(dir==="dn"?"−":"+")+r.pct+'<small>%</small></b><small>'+yen(r.price)+'</small><s>ふだん '+yen(r.base)+'</s></span></a></li>'};
  h+='<section class="fcat" id="c-down"><ol class="flist">'+dn.map(function(r,k){return row(r,k,"dn")}).join("")+'</ol></section>';
  h+='<section class="fcat" id="c-up" hidden><p class="fcap">ふだんより高くなっている物です。急がない物は、待つのも手です。</p><ol class="flist">'+up.map(function(r,k){return row(r,k,"up")}).join("")+'</ol></section>';
  h+='<section class="fno"><h2>しらべ方</h2><p>楽天市場の日用品'+(D.tracked||"")+'品の値段を'+(D.since?(+D.since.slice(5,7))+"月"+(+D.since.slice(8,10))+"日から":"")+'毎日しらべ、「ふだん」（これまでの値段のまん中）より安い物を、下がった割合の順に並べています。値段は送料込みで、調べた時のものです。リンクは楽天の広告（PR）です。</p></section>';
}
S_.main.innerHTML='<div class="wrap furu">'+h+'</div>';
function show(v){cur=v;$$("#fseg button").forEach(function(b){b.setAttribute("aria-selected",b.dataset.v===v?"true":"false")});
  $$(".fcat").forEach(function(s){var on=s.id==="c-"+v;s.hidden=!on;if(on&&!RM)s.animate([{opacity:0,transform:"translateY(6px)"},{opacity:1,transform:"none"}],{duration:240,easing:"cubic-bezier(.2,.9,.25,1)"})});S_.navCur&&S_.navCur(v)}
$("#fseg").addEventListener("click",function(e){var b=e.target.closest("button");if(b)show(b.dataset.v)});
S_.onNav(function(a){show(a);scrollTo({top:0,behavior:RM?"auto":"smooth"})});
S_.ready();
})();
