// プロフィール用ページの数え係（Cloudflare Pages Functions）。
// ・ページを開いた数：どの投稿から来たか（?f=x0715 など）ごとに1日ずつ数える
// ・ページの中で押されたリンク：/c?f=…&s=…&k=… を受けて数える（リンク先はそのまま。寄り道させない）
// 呼ばれるのは / と /c だけ（site/_routes.json）。画像などでは動かない。
// 数は KV（CLICKS）のキーのメタデータ n に入れる。scripts/pagestats.py が読んで data/page-stats.json にする。
const BOT = /bot|crawl|spider|slurp|preview|facebookexternalhit|embedly|whatsapp|discord|slack|telegram|curl|wget|python|headless/i;

function day() {
  return new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10); // 日本時間の日付
}

function clean(v, max) {
  return String(v || "").replace(/[|\r\n\t]/g, "").slice(0, max);
}

async function bump(env, key) {
  if (!env.CLICKS) return;
  // 無料枠（書き込み 1日1,000回・月と同じアカウント）を守る：数えた数が多い日は pagestats.py が「止め」を置く
  if (await env.CLICKS.get(`${day()}|stop`)) return;
  const got = await env.CLICKS.getWithMetadata(key);
  const n = ((got && got.metadata && got.metadata.n) || 0) + 1;
  await env.CLICKS.put(key, "", { metadata: { n }, expirationTtl: 60 * 60 * 24 * 180 });
}

export async function onRequest(ctx) {
  const { request, env } = ctx;
  const url = new URL(request.url);
  const ua = request.headers.get("user-agent") || "";
  if (url.pathname === "/c") {
    if (request.method === "POST" && !BOT.test(ua)) {
      const f = clean(url.searchParams.get("f"), 24) || "direct";
      const s = clean(url.searchParams.get("s"), 16) || "x";
      const k = clean(url.searchParams.get("k"), 40) || "x";
      ctx.waitUntil(bump(env, `${day()}|c|${f}|${s}|${k}`).catch(() => {}));
    }
    return new Response(null, { status: 204 });
  }
  const res = await ctx.next();
  if (request.method === "GET" && (url.pathname === "/" || url.pathname === "/index.html") && !BOT.test(ua)) {
    const f = clean(url.searchParams.get("f"), 24) || "direct";
    ctx.waitUntil(bump(env, `${day()}|v|${f}`).catch(() => {}));
  }
  return res;
}
