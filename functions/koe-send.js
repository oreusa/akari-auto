// 11/2 オーナー「メニューに 増やしてほしい・これがほしい・レビュー をつけたい／俺らしか触ってないからテスターが必要」
// /koe のページから送られた声を KV（CLICKS）に1件ずつ置く。キー koe|日時|乱数、値は JSON。
// scripts/koe.py が毎回の page.yml で読んで data/koe.json に移し、KV から消す。公開はオーナーがOKした物だけ（data/koe_public.json）。
// いたずら対策：本文は 5〜400 字、ボット・隠し欄に字があるものは捨てる、1日 40 件まで（KV 書き込みの無料枠を守る）。
const BOT = /bot|crawl|spider|slurp|preview|headless|curl|wget|python/i;
const KINDS = { more: "増やしてほしい", want: "これがほしい", review: "使ってみた感想" };
const MAX_DAY = 40;

function day() {
  return new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
}
function clean(v, max) {
  return String(v || "").replace(/[\u0000-\u0009\u000B-\u001F\u007F]/g, "").trim().slice(0, max);
}
function res(ok, msg) {
  return new Response(JSON.stringify({ ok, msg }), {
    status: ok ? 200 : 400,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

export async function onRequestPost({ request, env }) {
  const ua = request.headers.get("user-agent") || "";
  if (BOT.test(ua)) return res(false, "送れませんでした");
  let b;
  try { b = await request.json(); } catch (e) { return res(false, "送れませんでした"); }
  if (b.hp) return res(true, "ok"); // 隠し欄に字がある＝機械。受けたふりだけする
  const kind = KINDS[b.kind] ? b.kind : "";
  const text = clean(b.text, 400);
  if (!kind) return res(false, "種類を選んでください");
  if (text.length < 5) return res(false, "5文字以上で書いてください");
  const star = kind === "review" ? Math.max(0, Math.min(5, parseInt(b.star, 10) || 0)) : 0;
  const name = clean(b.name, 20);
  const page = clean(b.page, 40);
  if (!env.CLICKS) return res(false, "いまは送れません。時間をおいてお試しください");
  const cnt = `${day()}|koe-n`;
  const got = await env.CLICKS.getWithMetadata(cnt);
  const n = (got && got.metadata && got.metadata.n) || 0;
  if (n >= MAX_DAY) return res(false, "今日はたくさん届いたため、明日またお送りください");
  await env.CLICKS.put(cnt, "", { metadata: { n: n + 1 }, expirationTtl: 60 * 60 * 24 * 3 });
  const at = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 16).replace("T", " ");
  const key = `koe|${at}|${Math.random().toString(36).slice(2, 8)}`;
  await env.CLICKS.put(key, JSON.stringify({ at, kind: KINDS[kind], star, text, name, page }), { expirationTtl: 60 * 60 * 24 * 60 });
  return res(true, "ok");
}

export async function onRequest() {
  return new Response(null, { status: 405 });
}
