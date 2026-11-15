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
export default {
  async fetch(req) {
    const u = new URL(req.url);
    // 11/15 Search Console の所有確認（HTMLファイル）。VERIFY に書いた名前だけ返す（どんな名前でも返すと Google が「ハッキングの恐れ」で確認を断る 11/15）
    const gv = u.pathname.match(/^\/(google[0-9a-f]{8,32}\.html)$/);
    if (gv && VERIFY.includes(gv[1])) return new Response('google-site-verification: ' + gv[1], { headers: { 'content-type': 'text/html; charset=utf-8' } });
    if (gv) return new Response('Not Found', { status: 404 }); // ほかの名前は必ず 404（Google が確かめに来る）
    const up = MAP[u.hostname];
    if (!up) {
      if (u.pathname === '/' || u.pathname === '/index.html') return new Response(TOP, { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'public, max-age=600' } });
      if (u.pathname === '/robots.txt') return new Response('User-agent: *\nAllow: /\n', { headers: { 'content-type': 'text/plain' } });
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
