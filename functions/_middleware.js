// プロフィール用ページの数え係（Cloudflare Pages Functions）。
// 数えるのは、ページの中でアフィリエイトのリンク（PR）が押された回数だけ（10/24 オーナー「あくまでアフィリエイトだけ」）。
// /c?f=…&s=…&k=… を受けて、どの投稿から来た人が（f）、どの項目の（s）、どの物を（k）押したかを数える。リンク先はそのまま。
// 開いた数（10/24 オーナー「HPも見られてるか足す」）は、1日の合計1つだけを数え、1日500で止める（押した数300・操作100と合わせてもKVの書き込み1日1,000回の無料枠に収まる）。
// 呼ばれるのは / と /odekake と /okaimono と /fudosan-list と /c と /wx（site/_routes.json）。/wx は functions/wx.js。/ima と入口が /odekake を読むときは x-ima を付けるので開いた数に入れない。
// 数は KV（CLICKS）のキーのメタデータ n に入れる。scripts/pagestats.py が読んで data/page-stats.json にする。
const BOT = /bot|crawl|spider|slurp|preview|facebookexternalhit|externalagent|buffer|embedly|whatsapp|discord|slack|telegram|curl|wget|python|headless/i;

function day() {
  return new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10); // 日本時間の日付
}

function clean(v, max) {
  return String(v || "").replace(/[|\r\n\t]/g, "").slice(0, max);
}

// 11/10 おかいものの探す・条件・種類と、メニューの開け閉め（お金にならない操作）は別の枠。
// 11/9 はこの2つが308のうち245で、買うボタン・宿の押された数を数える枠（300）を食べて止めた。
const UI = new Set(["okaimono", "menu"]);

async function bump(env, key, ui) {
  if (!env.CLICKS) return;
  // 無料枠（書き込み 1日1,000回・月と同じアカウント）を守る：数えた数が多い日は pagestats.py が「止め」を置く
  if (await env.CLICKS.get(`${day()}|${ui ? "stopui" : "stop"}`)) return;
  const got = await env.CLICKS.getWithMetadata(key);
  const n = ((got && got.metadata && got.metadata.n) || 0) + 1;
  await env.CLICKS.put(key, "", { metadata: { n }, expirationTtl: 60 * 60 * 24 * 180 });
}

const VIEW_MAX = 500;

// 11/11 投稿から来た人（?f=x0715・t0715 など、予約係が付ける印）は、合計とは別に「日付|v|印」でも数える（どの枠の投稿がHPに人を連れて来たかを見るため）。
const POST_SRC = /^[xt]\d{4}$/;

async function view(env, f) {
  if (!env.CLICKS) return;
  const key = `${day()}|v|all`;
  const got = await env.CLICKS.getWithMetadata(key);
  const n = (got && got.metadata && got.metadata.n) || 0;
  if (n >= VIEW_MAX) return;
  await env.CLICKS.put(key, "", { metadata: { n: n + 1 }, expirationTtl: 60 * 60 * 24 * 180 });
  if (f && POST_SRC.test(f)) {
    const k2 = `${day()}|v|${f}`;
    const g2 = await env.CLICKS.getWithMetadata(k2);
    const n2 = ((g2 && g2.metadata && g2.metadata.n) || 0) + 1;
    await env.CLICKS.put(k2, "", { metadata: { n: n2 }, expirationTtl: 60 * 60 * 24 * 180 });
  }
}

export async function onRequest(ctx) {
  const { request, env } = ctx;
  const url = new URL(request.url);
  const ua = request.headers.get("user-agent") || "";
  // オーナーの分は数えない（10/25 オーナー「ホームページと楽天クリックは俺らじゃないのか？」）。
  // /?me=on を1回開くと、その端末に印（クッキー me=1、1年）が付き、以後その端末の開いた数・押した数は数えない。/?me=off で外す。
  const me = url.searchParams.get("me");
  if (url.pathname === "/" && (me === "on" || me === "off")) {
    const cookie = me === "on" ? "me=1; Max-Age=31536000; Path=/; Secure; SameSite=Lax" : "me=; Max-Age=0; Path=/; Secure; SameSite=Lax";
    const body = me === "on" ? "この端末はオーナーの印を付けました。これからはHPの数に入りません。" : "この端末の印を外しました。";
    return new Response(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><p style="font:16px sans-serif;padding:24px">${body}</p><p style="font:16px sans-serif;padding:0 24px"><a href="/">HPを開く</a></p>`,
      { headers: { "content-type": "text/html; charset=utf-8", "set-cookie": cookie, "cache-control": "no-store" } });
  }
  if (/(?:^|;\s*)me=1(?:;|$)/.test(request.headers.get("cookie") || "")) {
    return url.pathname === "/c" ? new Response(null, { status: 204 }) : ctx.next();
  }
  // 11/2 LIFE NOTE：入口 / と、2つのリスト /odekake・/okaimono。リストは外から直に来た時だけ数える（入口から移った人を2回数えない）
  const ref = request.headers.get("referer") || "";
  const own = /^https:\/\/(lifenote[^/]*|life-note|usagi-life-notes)\.pages\.dev\//.test(ref);
  const lp = url.pathname.replace(/\.html$/, "");
  // 11/7 関東不動産リスト /fudosan-list も、2つのリストと同じく外から直に来た時だけ数える
  // 11/11 投稿からのリンクを、その催しのページ・都県のページへ直に付けるようにした → 投稿の印（?f=x0715 等）つきで外から来た時は、どのページでも数える
  const fq = url.searchParams.get("f") || "";
  const isView = lp === "/" || ((lp === "/odekake" || lp === "/okaimono" || lp === "/fudosan-list") && !own) || (/^[xt]\d{4}$/.test(fq) && !own && !/\.[a-z0-9]+$/i.test(lp));
  if (isView && request.method === "GET" && !BOT.test(ua) && !request.headers.get("purpose") && !request.headers.get("sec-purpose") && !request.headers.get("x-ima")) {
    ctx.waitUntil(view(env, url.searchParams.get("f") || "").catch(() => {}));
  }
  if (url.pathname === "/c") {
    if (request.method === "POST" && !BOT.test(ua)) {
      const f = clean(url.searchParams.get("f"), 24) || "direct";
      let s = clean(url.searchParams.get("s"), 16);
      let k = clean(url.searchParams.get("k"), 40);
      // 11/11 月と同じ形の合図（本文が {"k":"申し込み｜送信"} だけ）は、これまで全部「x|x」に入って中身が分からなかった → 本文の k を読み、項目 hp で数える
      if (!s && !k) {
        try { const j = JSON.parse(await request.clone().text()); if (j && j.k) { s = "hp"; k = clean(j.k, 40); } } catch (e) {}
      }
      s = s || "x"; k = k || "x";
      ctx.waitUntil(bump(env, `${day()}|c|${f}|${s}|${k}`, UI.has(f)).catch(() => {}));
    }
    return new Response(null, { status: 204 });
  }
  return ctx.next();
}
