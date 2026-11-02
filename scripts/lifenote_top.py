"""LIFE NOTE の入口ページ（site/index.html = /）を作る。scripts/lifenote.py が最後に呼ぶ。
11/2 オーナー「燈のhpを LIFE NOTE を作る…その他は完全に TOWN NOTE 仕様にする」
→ 月の TOWN NOTE 入口（usagi tools/townnotes_top/make.py）と同じ形：上に関東7都県の絵地図、まんなかに「あなたの街」、
  下に PAGE 01 関東おでかけリスト・PAGE 02 くらべたおかいものリスト。数は開いた時に2つのリストから読むので、手で直さなくても毎日合う。
"""
import html, json, math, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "site")
E = html.escape
BASE = os.environ.get("LIFE_BASE") or "https://lifenote.pages.dev"
K = json.load(open(os.path.join(S, "townnotes", "kanto.json"), encoding="utf-8"))
# 都県の色は page.py の PREF_COLOR と同じ。塗りはその薄い色
PC = {"東京": "#4F86C6", "神奈川": "#3FA3B5", "埼玉": "#E09A3E", "千葉": "#D9775A", "茨城": "#5FA06A", "栃木": "#D2697E", "群馬": "#9C7BB8"}
FILL = {"東京": "#D6E4F5", "神奈川": "#D0EBEF", "埼玉": "#F8E4C4", "千葉": "#F7D9CC", "茨城": "#D8ECD4", "栃木": "#F5D6DE", "群馬": "#E6DBF1"}
LP = {"東京": [139.40, 35.70], "神奈川": [139.30, 35.42], "埼玉": [139.30, 36.02], "千葉": [140.25, 35.45],
      "茨城": [140.30, 36.38], "栃木": [139.82, 36.68], "群馬": [138.98, 36.52]}
EN = {"東京": "TOKYO", "神奈川": "KANAGAWA", "埼玉": "SAITAMA", "千葉": "CHIBA", "茨城": "IBARAKI", "栃木": "TOCHIGI", "群馬": "GUNMA"}
# あなたの街：7都県どこも1つ以上
CHIPS = ["渋谷", "新宿", "池袋", "横浜", "鎌倉", "川越", "大宮", "舞浜", "千葉市", "水戸", "宇都宮", "高崎"]


def rings(g):
    return g["coordinates"] if g["type"] == "Polygon" else [r for p in g["coordinates"] for r in p]


xs = [x for f in K["pref"]["features"] for r in rings(f["geometry"]) for x, _ in r]
ys = [y for f in K["pref"]["features"] for r in rings(f["geometry"]) for _, y in r]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
k = math.cos(math.radians((y0 + y1) / 2))
SC = 600 / ((x1 - x0) * k)
W, H = 600, (y1 - y0) * SC


def P(lon, lat):
    return ((lon - x0) * k * SC, (y1 - lat) * SC)


paths = []
for f in K["pref"]["features"]:
    pf = f["properties"]["p"]
    d = "".join("M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in (P(*q) for q in r)) + "Z" for r in rings(f["geometry"]))
    paths.append(f'<path d="{d}" fill="{FILL[pf]}" data-p="{pf}"/>')
labels = []
for pf, (lo, la) in LP.items():
    x, y = P(lo, la)
    labels.append(f'<g transform="translate({x:.0f},{y:.0f})"><text class="jp" fill="{PC[pf]}">{pf}</text><text class="en" y="17">{EN[pf]}</text></g>')
SVG = (f'<svg class="kmap" viewBox="-10 -10 {W + 20:.0f} {H + 20:.0f}" role="img" aria-label="関東7都県の地図">'
       f'<g class="pf" stroke="#fff" stroke-width="2.4" stroke-linejoin="round">{"".join(paths)}</g>'
       f'<g class="lb">{"".join(labels)}</g></svg>')

desc = "関東のくらしで見つけたことを、ノートにまとめています。イベントや新しいお店・施設の「関東おでかけリスト」と、うさぎが数字で比べた物とお得な日の「くらべたおかいものリスト」。"
ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "LIFE NOTE", "url": f"{BASE}/", "description": desc}

page = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="google-site-verification" content="19Vt8Ili5pokwJHyAI3SwQ2UKI-eqeLVJSHS3PVUO54">
<title>LIFE NOTE（ライフノート）｜関東のおでかけと、くらべた楽天の買い物のノート</title>
<meta name="description" content="{E(desc)}"><link rel="canonical" href="{BASE}/">
<meta property="og:type" content="website"><meta property="og:url" content="{BASE}/"><meta property="og:title" content="LIFE NOTE"><meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{BASE}/og-v10.png"><meta name="twitter:card" content="summary"><meta name="theme-color" content="#FFFFFF">
<link rel="icon" href="/logo.png"><link rel="apple-touch-icon" href="/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="stylesheet" href="/assets/top.css?v=1"><script src="/assets/night.js?v=13"></script><script src="/assets/menu.js?v=13" defer></script><script src="/assets/v2sub.js?v=7" defer></script></head><body id="lifenote-top"><div class="wrap">
<header class="head"><img src="/logo-s.png" width="74" height="74" alt="LIFE NOTE のロゴ">
<h1>LIFE NOTE</h1><div class="kana">ライフノート</div>
<p class="sub">関東のくらしで見つけたことを、<br>公式の情報つきで、このノートに書きとめています。</p>
<div class="nofilt">{SVG}</div><div class="mapcap">都県を押すと、その都県の数が出ます</div><div class="pp" id="pp" hidden></div></header>

<section class="find"><h2><small>YOUR TOWN</small>あなたの街を探す</h2>
<p>街の名前を入れると、その街の<b>おでかけ</b>と<b>イルミネーション</b>が<br>まとめて出ます。</p>
<input class="fi" id="q" type="search" placeholder="例：横浜、川越、舞浜" enterkeyhint="search" aria-label="街の名前">
<div class="chips">{"".join(f'<button type="button">{c}</button>' for c in CHIPS)}</div>
<div class="res" id="res"></div></section>

<section class="lists"><h2>IN THIS NOTE　─　このノートの中身</h2>
<a class="ls" href="/odekake" data-k="入口｜関東おでかけリスト" style="--ac:#4F86C6;--bg:#EAF1FA;--c:#4F86C6"><div class="no"><small>PAGE</small>01</div><div class="en">KANTO ODEKAKE</div><h3>関東おでかけリスト</h3>
<p>イベント・新しいお店や施設を、公式ページつきで。<br>地図でも探せて、近くの宿も見られます。</p>
<div class="st"><div><span>開催中</span><b id="o1">―</b></div><div><span>これから</span><b id="o2">―</b></div><div><span>入場無料</span><b id="o3">―</b></div></div>
<div class="pv" id="opv"></div><div class="go">おでかけリストを開く<span>→</span></div></a>
<a class="ls" href="/okaimono" data-k="入口｜くらべたおかいものリスト" style="--ac:#C2703F;--bg:#FBEEE6;--c:#C2703F"><div class="no"><small>PAGE</small>02</div><div class="en">OKAIMONO LIST</div><h3>くらべたおかいものリスト</h3>
<p>3つ以上を数字で比べて選んだ、暮らしの物。<br>本当に値下がりした物と、お得な日も。</p>
<div class="st"><div><span>比べた物</span><b id="k1">―</b></div><div><span>今だけのお得</span><b id="k2">―</b></div><div><span>くらべ方</span><b>4<small style="font-size:12px">つ</small></b></div></div>
<div class="pv" id="kpv"></div><div class="go">おかいものリストを開く<span>→</span></div></a>
<p style="font-size:10.5px;color:#8C7B6E;text-align:center;margin:-6px 0 0">おかいものリストのリンクには広告（PR）があります</p></section>

<section class="prom"><h2>NOTE RULES　─　書きかたの約束</h2><ol><li><b>公式だけ</b>おでかけは<br>公式ページだけ</li><li><b>数字で比べる</b>買い物は<br>3つ以上を比べて</li><li><b>7都県</b>どの都県も<br>同じように</li></ol></section>

<nav class="cos"><a href="https://ig.me/m/ai_usagichan1" data-k="入口｜おでかけ掲載"><small>LISTING</small><b>おでかけ掲載</b><span>新しいお店や、毎年のイベントのご紹介</span></a><a href="https://room.rakuten.co.jp/ai_usagichan/items" data-k="入口｜楽天ROOM"><small>RAKUTEN ROOM</small><b>楽天ROOM</b><span>うさぎが比べて選んだ物を、まとめて置いています</span></a></nav>
<div class="sns"><h2>FOLLOW</h2><a href="https://www.instagram.com/ai_usagichan1/">Instagram</a><a href="https://www.threads.com/@ai_usagichan1">Threads</a><a href="https://x.com/ai_usagichan">X</a></div>
<a href="/privacy" style="display:block;text-align:center;font-size:11px;color:#8C7B6E;margin:18px 0 0">プライバシーポリシーと広告について</a><div class="ft">LIFE NOTE（ライフノート）</div></div>
<script>(function(){{
var PC={json.dumps(PC, ensure_ascii=False)},EN={json.dumps(EN, ensure_ascii=False)};var SLUG={{"東京":"tokyo","神奈川":"kanagawa","埼玉":"saitama","千葉":"chiba","茨城":"ibaraki","栃木":"tochigi","群馬":"gunma"}};
/* どの投稿から来たか（?f=）は、リストに移っても数えられるように覚えておく（リストと同じ sessionStorage の f） */
var F="";try{{F=new URLSearchParams(location.search).get("f")||"";if(F)sessionStorage.setItem("f",F);else F=sessionStorage.getItem("f")||"";}}catch(e){{}}
function c(k){{try{{navigator.sendBeacon("/c?f="+encodeURIComponent(F||"direct")+"&s=top&k="+encodeURIComponent(String(k).slice(0,40)));}}catch(e){{}}}}
/* 前の1枚のページへのリンク（/#shop・/#map など）は、分けた先へ送る */
var hv=location.hash.slice(1),qv=new URLSearchParams(location.search).get("v2t");
if(/^(shop|deal|trip|hot)$/.test(hv)){{location.replace("/okaimono"+location.search+"#"+hv);return;}}
if(/^(map|odekake|archive)$/.test(hv)||qv!==null){{location.replace("/odekake"+location.search+(hv?"#"+hv:""));return;}}
function esc(s){{return String(s).replace(/[&<>"]/g,function(x){{return{{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[x]}})}}
var today=new Date(Date.now()+9*36e5).toISOString().slice(0,10),pcs=Object.keys(PC);
function prefOf(t){{for(var i=0;i<pcs.length;i++)if(t.indexOf(pcs[i])>=0)return pcs[i];return "";}}
var OD=[],IL=[];
var pO=fetch("/odekake",{{headers:{{"x-ima":"1"}}}}).then(function(r){{return r.text()}}).then(function(t){{var d=new DOMParser().parseFromString(t,"text/html");
 d.querySelectorAll("#odekake .card.it").forEach(function(a){{var e=a.getAttribute("data-e")||"",s=a.getAttribute("data-s")||"",tt=a.querySelector(".t"),w=a.querySelector(".when"),g=a.querySelector("a.go"),mp=a.querySelector("a.mp");if(e&&e<today)return;if(!tt)return;
  var q="";try{{q=decodeURIComponent((mp&&mp.getAttribute("href")||"").split("query=")[1]||"");}}catch(x){{}}
  OD.push({{t:tt.textContent.trim().replace(/\\s+/g," "),m:q,w:w?w.textContent.trim():"",p:a.getAttribute("data-pref")||"",h:g?g.getAttribute("href"):"/odekake",f:a.getAttribute("data-free")==="1",now:!(s&&s>today),up:!!(s&&s>today)}});}});
 var n1=OD.filter(function(x){{return x.now}}).length,n2=OD.filter(function(x){{return x.up}}).length,n3=OD.filter(function(x){{return x.f}}).length,u='<small style="font-size:12px">件</small>';
 document.getElementById("o1").innerHTML=n1+u;document.getElementById("o2").innerHTML=n2+u;document.getElementById("o3").innerHTML=n3+u;
 /* 3件は都県がかぶらないように */
 var seen={{}},pv=OD.filter(function(x){{if(!x.now||seen[x.p])return false;seen[x.p]=1;return true}}).slice(0,3);
 document.getElementById("opv").innerHTML=pv.map(function(x){{return '<div><i style="color:'+(PC[x.p]||"#8C7B6E")+'">'+esc(x.p)+'</i>'+esc(x.t)+'</div>'}}).join("");}}).catch(function(){{}});
var pI=fetch("/illumination").then(function(r){{return r.text()}}).then(function(t){{var d=new DOMParser().parseFromString(t,"text/html");
 d.querySelectorAll(".card").forEach(function(a){{var e=a.getAttribute("data-e")||"";if(e&&e<today)return;var tt=a.querySelector(".t,h3,.nm");if(!tt)return;var tx=a.textContent.replace(/\\s+/g," ");
  IL.push({{t:tt.textContent.trim(),x:tx,p:prefOf(tx)}});}});}}).catch(function(){{}});
fetch("/okaimono",{{headers:{{"x-ima":"1"}}}}).then(function(r){{return r.text()}}).then(function(t){{var d=new DOMParser().parseFromString(t,"text/html"),u='<small style="font-size:12px">件</small>';
 var sh=d.querySelectorAll("#shop article.card").length,dl=d.querySelectorAll("#deal .card").length;
 document.getElementById("k1").innerHTML=sh+u;document.getElementById("k2").innerHTML=dl+u;
 var rows=[],h=d.querySelector("#hot .nm,#hot h3");if(h)rows.push(["いち押し",h.textContent.trim()]);
 d.querySelectorAll("#shop article.card").forEach(function(a){{if(rows.length>=3)return;var n=a.querySelector(".nm,h3");if(n)rows.push(["比べた",n.textContent.trim()]);}});
 document.getElementById("kpv").innerHTML=rows.map(function(r){{return '<div><i style="color:#C2703F">'+r[0]+'</i>'+esc(r[1].slice(0,40))+'</div>'}}).join("");}}).catch(function(){{}});
/* 地図：都県を押すと、その都県のおでかけの数 */
var svg=document.querySelector(".kmap"),pp=document.getElementById("pp");
svg.querySelectorAll(".pf path").forEach(function(el){{el.addEventListener("click",function(){{var p=el.getAttribute("data-p");Promise.all([pO,pI]).then(function(){{
 svg.classList.add("sel");svg.querySelectorAll(".pf path").forEach(function(x){{x.classList.toggle("on",x.getAttribute("data-p")===p)}});
 var od=OD.filter(function(x){{return x.p===p}}),nw=od.filter(function(x){{return x.now}}),fr=od.filter(function(x){{return x.f}}),il=IL.filter(function(x){{return x.p===p}});
 pp.style.setProperty("--pc",PC[p]);pp.hidden=false;var u='<small style="font-size:12px">件</small>';
 pp.innerHTML='<h3>'+p+'<small>'+EN[p]+'</small></h3><div class="g"><a href="/odekake?pref='+encodeURIComponent(p)+'" data-k="入口の地図｜おでかけ｜'+p+'"><span>おでかけ（開催中）</span><b>'+nw.length+u+'</b><em>'+(nw[0]?esc(nw[0].t):"これから足します")+'</em></a>'+
  '<a href="/illumination-'+SLUG[p]+'" data-k="入口の地図｜イルミ｜'+p+'"><span>イルミネーション</span><b>'+il.length+u+'</b><em>'+(il[0]?esc(il[0].t):(fr[0]?"無料 "+esc(fr[0].t):"これから足します"))+'</em></a></div>';
 c("入口の地図："+p);}});}});}});
/* あなたの街：おでかけとイルミをまとめて */
var q=document.getElementById("q"),res=document.getElementById("res"),tq;
function find(v){{v=v.replace(/\\s/g,"");if(!v){{res.innerHTML="";return;}}var vv=v.replace(/(市|区|町|村|駅)$/,"");
 var od=OD.filter(function(x){{return (x.t+x.m).replace(/\\s/g,"").indexOf(vv)>=0}}).slice(0,6);
 var il=IL.filter(function(x){{return x.x.replace(/\\s/g,"").indexOf(vv)>=0}}).slice(0,4);
 var h="";if(od.length)h+='<div class="sec">ODEKAKE　おでかけ</div>'+od.map(function(x){{return '<a href="'+esc(x.h)+'" rel="noopener" style="--pc:'+(PC[x.p]||"#8C7B6E")+'" data-k="入口の検索｜おでかけ｜'+esc(x.t.slice(0,20))+'"><i>'+esc(x.p)+'</i><b>'+esc(x.t)+'<small>'+esc(x.w)+(x.now?"・開催中":x.up?"・これから":"")+'</small></b><em style="color:#9C8775">→</em></a>'}}).join("");
 if(il.length)h+='<div class="sec">ILLUMINATION　イルミネーション</div>'+il.map(function(x){{return '<a href="'+(SLUG[x.p]?"/illumination-"+SLUG[x.p]:"/illumination")+'" style="--pc:'+(PC[x.p]||"#8C7B6E")+'" data-k="入口の検索｜イルミ｜'+esc(x.t.slice(0,20))+'"><i>'+esc(x.p||"関東")+'</i><b>'+esc(x.t)+'</b><em style="color:#9C8775">→</em></a>'}}).join("");
 res.innerHTML=h||'<div class="none">「'+esc(v)+'」はまだありません。調べて、リストに足していきます。</div>';}}
q.oninput=function(){{Promise.all([pO,pI]).then(function(){{find(q.value)}});clearTimeout(tq);tq=setTimeout(function(){{if(q.value.trim())c("入口で探す："+q.value.trim())}},1500);}};
document.querySelectorAll(".chips button").forEach(function(b){{b.onclick=function(){{q.value=b.textContent;Promise.all([pO,pI]).then(function(){{find(b.textContent)}});c("入口で探す："+b.textContent);}}}});
document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest("a");if(!a)return;c("入口｜"+(a.getAttribute("data-k")||a.textContent.trim().slice(0,30)));}},true);
/* リストへ移る時も ?f= を付けたまま */
if(location.search)document.querySelectorAll('a.ls,.pp a').forEach(function(a){{a.href=a.getAttribute("href")+location.search;}});
}})();</script></body></html>'''
open(os.path.join(S, "index.html"), "w", encoding="utf-8").write(page)
print("LIFE NOTE 入口", len(page))
