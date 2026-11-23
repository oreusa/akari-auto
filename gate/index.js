// 11/15 townnote.app の入口（Worker）。DNS の鍵が無いので、Worker のカスタムドメインで3つのアドレスを受けて、今の Pages へそのまま取り次ぐ。
// kansai.townnote.app → townnote.pages.dev（関西 TOWN NOTE）／kanto.townnote.app → lifenote-kanto.pages.dev（関東 LIFE NOTE）／townnote.app → 入口のページ
const VERIFY = ['google89ea47473ae57497.html']; // 汐が報告した確認ファイルの名前（関西・関東とも同じ名前）
const MAP = { 'kansai.townnote.app': 'townnote.pages.dev', 'kanto.townnote.app': 'lifenote-kanto.pages.dev' };
const TOP = `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TOWN NOTE｜関西・関東</title>
<meta name="description" content="関西の TOWN NOTE と、関東の LIFE NOTE。日付と地図でさがせる、おでかけと暮らしのノートです。">
<style>body{margin:0;background:#f7f2ea;color:#3a2a1e;font-family:"Hiragino Mincho ProN","Yu Mincho",serif;min-height:100vh;display:flex;align-items:center;justify-content:center}
main{width:min(92vw,520px);padding:32px 0;text-align:center}h1{font-size:34px;letter-spacing:.12em;margin:0 0 6px}p{margin:0 0 28px;color:#7a6250;font-size:15px}
a{display:block;text-decoration:none;color:inherit;background:#fff;border:1px solid #e3d6c3;border-radius:14px;padding:22px 20px;margin:14px 0;box-shadow:0 6px 18px rgba(80,50,20,.08)}
a b{display:block;font-size:24px;letter-spacing:.08em}a span{font-size:14px;color:#8a7260}</style></head>
<body><main><h1>TOWN NOTE</h1><p>見るエリアをえらんでください</p>
<a href="https://kansai.townnote.app/"><b>関西 TOWN NOTE</b><span>関西のおでかけ・暮らしのノート</span></a>
<a href="https://kanto.townnote.app/"><b>関東 LIFE NOTE</b><span>関東のおでかけ・暮らしのノート</span></a></main></body></html>`;
// 11/23 owner「もっとおしゃれに」→ 15:46「おけ」でふだんの入口に（?mihon=0 で前の形）。見本：HP と同じ（昼＝上だけ淡いオーロラ・夜＝澄んだ星空・すりガラスのカード・細い字）。?mihon=1 で見られる
const TOP2 = `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>TOWN NOTE（タウンノート）｜関西・関東のおでかけと暮らしのノート</title><link rel="canonical" href="https://townnote.app/">
<meta name="description" content="関西の TOWN NOTE と、関東の LIFE NOTE。日付と地図でさがせる、おでかけと暮らしのノートです。">
<meta property="og:title" content="TOWN NOTE（タウンノート）"><meta property="og:image" content="https://kansai.townnote.app/assets/ogp-top.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="https://kansai.townnote.app/assets/icon-192.png"><link rel="apple-touch-icon" href="https://kansai.townnote.app/assets/icon-180.png">
<meta name="theme-color" content="#F8F8FA">
<script>(function(){var n;try{n=localStorage.getItem("tn_gate")}catch(e){}var m=location.search.match(/[?&]yoru=([01])/);if(m)n=m[1]==="1"?"night":"day";if(!n){var h=new Date().getHours();n=(h>=18||h<6)?"night":"day"}if(n==="night")document.documentElement.classList.add("nt")})()</script>
<style>
:root{--bg:#F8F8FA;--ink:#111114;--sub:#6E6E76;--card:rgba(255,255,255,.58);--edge:rgba(255,255,255,.85);--line:rgba(17,17,20,.08);--sh:0 10px 30px rgba(20,24,40,.07)}
html.nt{--bg:#05070D;--ink:#F2F2F5;--sub:#9A9FAE;--card:rgba(255,255,255,.045);--edge:rgba(255,255,255,.13);--line:rgba(255,255,255,.08);--sh:none;color-scheme:dark}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Hiragino Kaku Gothic ProN","Noto Sans JP","Yu Gothic",sans-serif;-webkit-font-smoothing:antialiased;transition:background-color .5s}
.nt body{background:radial-gradient(90vw 60vh at 50% -12%,rgba(58,90,170,.22),transparent 70%),#05070D}
/* 昼：上だけ淡いオーロラの帯が流れて、下の白へ溶ける */
.au{position:fixed;inset:0 0 auto 0;height:62vh;overflow:hidden;pointer-events:none;z-index:0;-webkit-mask:linear-gradient(#000 35%,transparent);mask:linear-gradient(#000 35%,transparent)}
.au i{position:absolute;width:62vmax;height:62vmax;border-radius:50%;filter:blur(60px);opacity:.5;animation:fl 22s ease-in-out infinite alternate}
.au i:nth-child(1){background:#9FE3D3;left:-22vmax;top:-30vmax}
.au i:nth-child(2){background:#B9A8F2;left:18vw;top:-36vmax;animation-delay:-6s}
.au i:nth-child(3){background:#F7B6D2;right:-24vmax;top:-28vmax;animation-delay:-11s}
.au i:nth-child(4){background:#8FD0E8;left:30vw;top:-18vmax;opacity:.32;animation-delay:-16s}
@keyframes fl{to{transform:translate3d(6vmax,4vmax,0) scale(1.08)}}
.nt .au{display:none}
/* 夜：HP と同じ澄んだ星空 */
#sky{position:fixed;inset:0;pointer-events:none;z-index:0;display:none}.nt #sky{display:block}#sky canvas{width:100%;height:100%;display:block}
.tw{position:absolute;width:3px;height:3px;margin:-1.5px 0 0 -1.5px;border-radius:50%;background:#fff;box-shadow:0 0 6px 1px rgba(255,255,255,.55);opacity:.2;animation:tw 6s ease-in-out infinite}
@keyframes tw{50%{opacity:1}}
@media (prefers-reduced-motion:reduce){.au i,.tw{animation:none}}
main{position:relative;z-index:1;min-height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:max(64px,env(safe-area-inset-top)) 20px max(40px,env(safe-area-inset-bottom))}
.w{width:min(100%,440px)}
.lg{display:block;width:56px;height:56px;margin:0 auto 22px;border-radius:50%;background:#fff;box-shadow:0 6px 20px rgba(20,24,40,.08);padding:5px}
.nt .lg{box-shadow:0 0 28px rgba(255,255,255,.18)}
h1{margin:0;text-align:center;font-weight:200;font-size:34px;letter-spacing:.34em;text-indent:.34em;line-height:1.1}
.lead{margin:14px 0 40px;text-align:center;font-weight:300;font-size:14px;letter-spacing:.12em;color:var(--sub)}
a.c{position:relative;display:flex;align-items:center;gap:16px;text-decoration:none;color:inherit;padding:24px 22px;margin:0 0 14px;border-radius:22px;background:var(--card);border:1px solid var(--edge);box-shadow:var(--sh);-webkit-backdrop-filter:blur(18px) saturate(1.4);backdrop-filter:blur(18px) saturate(1.4);overflow:hidden;transition:transform .25s,border-color .25s}
a.c::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;opacity:0;transition:opacity .3s;background:radial-gradient(220px circle at var(--x,50%) var(--y,50%),rgba(255,255,255,.65),transparent 60%)}
.nt a.c::after{background:radial-gradient(220px circle at var(--x,50%) var(--y,50%),rgba(160,190,255,.16),transparent 60%)}
a.c:hover::after,a.c.on::after{opacity:1}a.c:active{transform:scale(.985)}
.c .t{flex:1;min-width:0}
.c small{display:block;font-size:10.5px;font-weight:500;letter-spacing:.28em;color:var(--sub);margin-bottom:8px}
.c small i{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:8px;vertical-align:1px}
.c b{display:block;font-weight:300;font-size:22px;letter-spacing:.1em}
.c span{display:block;margin-top:6px;font-size:13px;font-weight:300;color:var(--sub);letter-spacing:.04em}
.c svg{flex:none;opacity:.55}
.tg{position:fixed;z-index:2;top:max(16px,env(safe-area-inset-top));right:16px;display:flex;align-items:center;gap:6px;border:1px solid var(--line);background:var(--card);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);color:var(--sub);font:inherit;font-size:12px;letter-spacing:.1em;border-radius:999px;padding:7px 12px;cursor:pointer}
.tg svg{width:14px;height:14px}
.ft{margin-top:34px;text-align:center;font-size:11px;letter-spacing:.2em;color:var(--sub);font-weight:300}
</style></head><body>
<div class="au" aria-hidden="true"><i></i><i></i><i></i><i></i></div><div id="sky" aria-hidden="true"><canvas></canvas></div>
<button class="tg" type="button" aria-label="昼と夜を切り替える"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M13 9.5A5.5 5.5 0 0 1 6.5 3a5.5 5.5 0 1 0 6.5 6.5z"/></svg><span>夜</span></button>
<main><div class="w">
<img class="lg" src="https://kansai.townnote.app/assets/icon-192.png" alt="">
<h1>TOWN NOTE</h1>
<p class="lead">関西と関東の、おでかけと暮らしのノート</p>
<a class="c" href="https://kansai.townnote.app/"><div class="t"><small><i style="background:#F2A65A"></i>KANSAI</small><b>関西 TOWN NOTE</b><span>大阪・京都・兵庫・奈良・滋賀・和歌山</span></div><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M4 9h10M10 5l4 4-4 4"/></svg></a>
<a class="c" href="https://kanto.townnote.app/"><div class="t"><small><i style="background:#7FA7F0"></i>KANTO</small><b>関東 LIFE NOTE</b><span>東京・神奈川・埼玉・千葉・北関東</span></div><svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M4 9h10M10 5l4 4-4 4"/></svg></a>
<p class="ft">EVENTS ・ HOMES ・ NEW SHOPS</p>
</div></main>
<script>
(function(){var H=document.documentElement,b=document.querySelector(".tg"),sky=document.getElementById("sky"),cv=sky.querySelector("canvas"),tw=[];
function lab(){var n=H.classList.contains("nt");b.querySelector("span").textContent=n?"昼":"夜";b.querySelector("svg").innerHTML=n?'<circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1 1M11.6 11.6l1 1M3.4 12.6l1-1M11.6 4.4l1-1"/>':'<path d="M13 9.5A5.5 5.5 0 0 1 6.5 3a5.5 5.5 0 1 0 6.5 6.5z"/>';document.querySelector('meta[name="theme-color"]').content=n?"#05070D":"#F8F8FA"}
function draw(){if(!H.classList.contains("nt"))return;var w=innerWidth,h=innerHeight,dp=Math.min(2,devicePixelRatio||1);cv.width=w*dp;cv.height=h*dp;var c=cv.getContext("2d");c.scale(dp,dp);
var r=20251121;function rnd(){r=(r*16807)%2147483647;return r/2147483647}var n=Math.round(w*h/1800);
for(var i=0;i<n;i++){var x=rnd()*w,y=rnd()*h,k=rnd(),sz=k>.95?1.4:k>.75?.9:.55,a=k>.95?1:k>.75?.8:.5;c.fillStyle="rgba(255,255,255,"+a+")";c.beginPath();c.arc(x,y,sz,0,7);c.fill();
if(k>.96){var g=c.createRadialGradient(x,y,0,x,y,7);g.addColorStop(0,"rgba(255,255,255,.22)");g.addColorStop(1,"rgba(255,255,255,0)");c.fillStyle=g;c.fillRect(x-7,y-7,14,14)}}
tw.forEach(function(e){e.remove()});tw=[];if(!matchMedia("(prefers-reduced-motion:reduce)").matches)for(var j=0;j<7;j++){var e=document.createElement("i");e.className="tw";e.style.cssText="left:"+(rnd()*w).toFixed(0)+"px;top:"+(rnd()*h*.8).toFixed(0)+"px;animation-delay:-"+(rnd()*6).toFixed(1)+"s;animation-duration:"+(4+rnd()*4).toFixed(1)+"s";sky.appendChild(e);tw.push(e)}}
b.addEventListener("click",function(){H.classList.toggle("nt");try{localStorage.setItem("tn_gate",H.classList.contains("nt")?"night":"day")}catch(e){}lab();draw()});
var t;addEventListener("resize",function(){clearTimeout(t);t=setTimeout(draw,200)});lab();draw();
document.querySelectorAll("a.c").forEach(function(a){function mv(e){var p=e.touches?e.touches[0]:e,r=a.getBoundingClientRect();a.style.setProperty("--x",(p.clientX-r.left)+"px");a.style.setProperty("--y",(p.clientY-r.top)+"px")}
a.addEventListener("pointermove",mv);a.addEventListener("touchstart",function(e){mv(e);a.classList.add("on")},{passive:true});a.addEventListener("touchend",function(){a.classList.remove("on")})})})();
</script></body></html>
`;
export default {
  async fetch(req) {
    const u = new URL(req.url);
    // 11/15 Search Console の所有確認（HTMLファイル）。VERIFY に書いた名前だけ返す（どんな名前でも返すと Google が「ハッキングの恐れ」で確認を断る 11/15）
    const gv = u.pathname.match(/^\/(google[0-9a-f]{8,32}\.html)$/);
    if (gv && VERIFY.includes(gv[1])) return new Response('google-site-verification: ' + gv[1], { headers: { 'content-type': 'text/html; charset=utf-8' } });
    if (gv) return new Response('Not Found', { status: 404 }); // ほかの名前は必ず 404（Google が確かめに来る）
    const up = MAP[u.hostname];
    if (!up) {
      if (u.pathname === '/' || u.pathname === '/index.html') return new Response(u.searchParams.get('mihon') === '0' ? TOP : TOP2, { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': u.searchParams.get('mihon') === '0' ? 'no-store' : 'public, max-age=600' } });
      if (u.pathname === '/robots.txt') return new Response('User-agent: *\nAllow: /\n', { headers: { 'content-type': 'text/plain' } });
      // 11/23 夜の見回り：古い深いURL（townnote.app/odekake など）で来た人が入口に戻されていた → 同じページのある地域へ送る。
      // 関東の印（都県の名前・kanto）があれば関東、なければ関西に有るか確かめ、無くて関東に有れば関東。どちらにも無い時だけ入口。
      const pq = u.pathname + u.search;
      const KT = /(tokyo|kanagawa|saitama|chiba|ibaraki|tochigi|gunma|kanto|yokohama|kawasaki)/i;
      const order = KT.test(u.pathname) ? ['kanto', 'kansai'] : ['kansai', 'kanto'];
      for (const r of order) {
        try {
          const h = await fetch('https://' + MAP[r + '.townnote.app'] + u.pathname, { method: 'HEAD', redirect: 'follow' });
          if (h.status < 400) return Response.redirect('https://' + r + '.townnote.app' + pq, 301);
        } catch (e) {}
      }
      return Response.redirect('https://townnote.app/', 302);
    }
    const t = new URL(req.url); t.hostname = up; t.protocol = 'https:'; t.port = '';
    const h = new Headers(req.headers); h.set('x-tn-host', u.hostname);
    const r = await fetch(t.toString(), { method: req.method, headers: h, body: ['GET', 'HEAD'].includes(req.method) ? undefined : req.body, redirect: 'manual' });
    const out = new Response(r.body, r);
    const loc = out.headers.get('location');
    if (loc && loc.includes(up)) out.headers.set('location', loc.split(up).join(u.hostname));
    return out;
  }
};
