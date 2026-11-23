/* 11/24 まちランキングの見本（?mihon=1 紙面 ／ ?mihon=2 索引）。本番は変えない。
   同じ形のカードが45本ならぶ形をやめて、中身（公式の数字の1位と値）を前に出す。
   オーロラ・夜空・下のバー・ロゴ・売る入口・絞り込みはそのまま。押すと今と同じ「順位の全部」が開く（元の行を押す）。
   11/24 オーナー「もう少し分かりやすく、見やすく」→ 1画面目を詰める・題は「何の順位か」・数字に「何の数か」・
   No.と日付をやめて新しい物だけ NEW・薄い小さな字をやめる。 */
(function(){
var M=(location.search.match(/[?&]mihon=(\d)/)||[])[1]||"1";if(M==="0")return;
var D;try{D=JSON.parse(document.getElementById("d").textContent)}catch(e){document.documentElement.classList.remove("rkm");return}
var IT=D.items||[],grid=document.getElementById("grid");if(!grid)return;
var H=document.documentElement;H.classList.add("rkm","rkm"+M);
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
var RX=/(\d+)位\s*は?\s*([^0-9+＋\-−\s・：の、は][^\s：]*?(?:（[^）]*）)?)の?[\s：]*([+＋\-−]?[\d,.]+)\s*(%|％|万円\/㎡|万円|円\/㎡|万人|人)/;
function rows(x){if(x._r)return x._r;var out=[],seen={};x.body.split("\n").forEach(function(l){var m=RX.exec(l);if(m&&!seen[m[1]]&&out.length<10){seen[m[1]]=1;out.push({no:+m[1],n:m[2],v:m[3].replace("＋","+").replace("−","-"),u:m[4].replace("％","%")})}});
  if(!out.length){var m=RX.exec(x.t);if(m)out.push({no:+m[1],n:m[2],v:m[3].replace("＋","+").replace("−","-"),u:m[4].replace("％","%")})}
  out.sort(function(a,b){return a.no-b.no});return x._r=out}
function lead(x){var l=(x.body.split("\n").filter(function(s){return s.trim()})[0]||"").trim();return l.length>60?"":l}
function num(v){return parseFloat(String(v).replace(/,/g,""))}

/* 何の数か（単位の意味）。本文の言葉から決める */
function what(x,t){var b=x.t+" "+x.body,u=t?t.u:"";
  if(u==="人"){if(/観光|入込/.test(b))return "1年に来た人";if(/乗車人員/.test(b))return "1日に乗る人（降りる人は入れない）";if(/乗降/.test(b))return "1日に乗り降りする人";return "1日に駅を使う人"}
  if(u==="万人")return "1年に来た人";
  if(/㎡/.test(u))return (/商業地/.test(x.t)?"商業地":"住宅地")+"1㎡の値段";
  if(u==="万円")return /中古|売れ/.test(b)?"実際に売れた家の値段（平均）":"値段";
  if(u==="%"){var m=x.t.match(/([^\s　、]+?)の割合/);if(m)return m[1]+"の人の割合";
    if(/人口/.test(x.t))return "人口の増え方（5年前から）";
    return (/商業地/.test(x.t)?"商業地":"住宅地")+"の値段の上がり幅（1年）"}
  return ""}
/* 何の順位か（題の「どこの・何の」の所）と、驚きの一言（題の残り） */
var BAD=/位|差|抜|上回|迫|入れ替|入れかわ|？|\?|いくら/;
function subj(x,t){var ps=x.t.split(/、|　|｜/).map(function(s){return s.trim()}).filter(Boolean),S="",k=-1;
  ps.forEach(function(p,i){var q=p.replace(/^(.+?)に実家があるなら$/,"$1");if(k<0&&!BAD.test(q)&&!/[\d,]+(人|%|％)$/.test(q)){S=q;k=i}});
  if(k<0){var m=x.body.match(/(?:^|[\s。、！])((?!上位)[^\s。、！の]{1,8}\d+(?:区|市町村|市町|市|駅))/);if(m&&/上位|表/.test(m[1]))m=null;S=m?m[1]:(x.k==="eki"?(x.p||"関西"):(x.p||""))}
  S=S.replace(/で$/,"");
  if(t&&(t.u==="%"||/㎡/.test(t.u)))S=S.replace(/[・の\s]*(住宅地|商業地)(の基準地価|の平均)?$/,"")||S;
  if(/人口/.test(x.t))S=S.replace(/の人口$/,"")||S;
  if(t&&t.u==="人"&&x.k==="eki"&&!/駅/.test(S))S+="の駅";
  var hk=ps.filter(function(p,i){return i!==k}).join("　");
  return {s:S,h:hk}}
function plain(h,t){return !h||(t&&h.indexOf(t.n.replace(/（.*/,""))>=0)}
function md(x){var m=(x.d||"").match(/(\d{1,2})\/(\d{1,2})\s*$/);return m?(+m[1])*100+(+m[2]):0}
var NEW=IT.reduce(function(a,x){return Math.max(a,md(x))},0),NN=IT.filter(function(x){return NEW&&md(x)===NEW}).length;
function isNew(x){return NEW>0&&NN*2<IT.length&&md(x)===NEW}
function info(x){var r=rows(x),t=r[0],s=subj(x,t);return {r:r,t:t,s:s.s,h:plain(s.h,t)?(lead(x)||s.h):s.h,ld:lead(x),w:what(x,t),nw:isNew(x)}}
var nb='<span class="rknew">NEW</span>';

var box=document.createElement("div");box.id="rkm";box.className="rkc";grid.parentNode.insertBefore(box,grid);
function open(i){var a=grid.querySelector('[data-i="'+i+'"]');if(a)a.click()}
box.addEventListener("click",function(e){var a=e.target.closest("[data-oi]");if(!a)return;e.preventDefault();open(a.getAttribute("data-oi"))});

/* 11/24 オーナー「区切り分かりやすく？文字ばかりだから工夫は必要」→ AとBを1つに：1本ずつ白い札・左上に分野の絵と色・
   どの札にも上位3つの横の棒（字を読まなくても分かる）・題は1行で太く・何の数かは小さな札・驚きの一言は一番下に1行。一番新しい1本だけ大きな数字 */
var KIND={eki:["駅","#3B5BA5",'<rect x="6" y="3" width="12" height="13" rx="3"/><path d="M6 10h12M9.5 19.5L8 21.5M14.5 19.5l1.5 2"/><circle cx="9.5" cy="13" r=".9"/><circle cx="14.5" cy="13" r=".9"/>'],
  ie:["家と土地","#C0532B",'<path d="M4 11l8-7 8 7"/><path d="M6 9.5V20h12V9.5"/><path d="M10 20v-5h4v5"/>'],
  hito:["人口","#2E8B6E",'<circle cx="12" cy="7.5" r="3.5"/><path d="M5 20.5c.8-4 3.6-6.5 7-6.5s6.2 2.5 7 6.5"/>'],
  hoka:["そのほか","#6E6E73",'<circle cx="7" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="17" cy="12" r="1.6"/>']};
function top3(r,big){var t=r.slice(big?1:0,3),max=Math.max.apply(null,r.slice(0,3).map(function(o){return Math.abs(num(o.v))}))||1;
  return '<ol class="r3">'+t.map(function(o){var w=Math.max(6,Math.round(Math.abs(num(o.v))/max*100));
    return '<li><span class="rn">'+o.no+'</span><span class="rt">'+esc(o.n)+'</span><b class="rv">'+esc(o.v)+'<small>'+esc(o.u)+'</small></b><i class="rl"><i style="width:'+w+'%"></i></i></li>'}).join("")+'</ol>'}
function card(p,big){var x=p.x,f=info(x),t=f.t,K=KIND[x.k]||KIND.hoka,hk=big?(f.ld||f.h):f.h;
  return '<article class="rc'+(big?' rc0':'')+'" style="--kc:'+K[1]+'"><a href="#" data-oi="'+p.i+'">'+
    '<p class="rck"><svg viewBox="0 0 24 24" aria-hidden="true">'+K[2]+'</svg><span>'+esc(K[0])+'</span>'+(f.nw?nb:"")+'</p>'+
    '<h3>'+esc(f.s)+'</h3>'+(f.w?'<p class="rcw"><span>'+esc(f.w)+'</span></p>':"")+
    (big&&t?'<p class="rkbig"><span>1位　'+esc(t.n)+'</span><b>'+esc(t.v)+'<small>'+esc(t.u)+'</small></b></p>':"")+
    (f.r.length>(big?1:0)?top3(f.r,big&&!!t):"")+(hk?'<p class="rch">'+esc(hk)+'</p>':"")+'</a></article>'}
function cards(L){return L.map(function(p,k){return card(p,p.x===IT[0]&&!!info(p.x).t)}).join("")}

function draw(){var L=[].map.call(grid.querySelectorAll("[data-i]"),function(a){var i=a.getAttribute("data-i");return{i:i,x:IT[+i]||IT.filter(function(z){return String(z.i)===i})[0]}}).filter(function(p){return p.x});
  box.innerHTML=cards(L);
  var hk=document.querySelector('#chips .chip[data-g="hoka"]');if(hk&&/そのほか/.test(hk.textContent))[].forEach.call(hk.childNodes,function(n){if(n.nodeType===3)n.textContent=n.textContent.replace("そのほか","ほか")})}
new MutationObserver(draw).observe(grid,{childList:true});draw();

/* 1画面目を詰める：説明は1行・府県は「関西 ▾」1つ（押すと府県が開く） */
var ln=document.querySelector("#main .lnote");if(ln)ln.textContent="公式の数字です。押すと順位の全部と出どころ。";
document.addEventListener("click",function(e){var bar=document.getElementById("bar");if(!bar||!e.target.closest)return;
  if(e.target.closest("#bar .lk-pf")){bar.classList.toggle("rkpfo");return}
  if(e.target.closest("#seg button"))setTimeout(function(){bar.classList.remove("rkpfo")},0)},true);
})();
