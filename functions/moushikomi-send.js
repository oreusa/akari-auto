// 11/9 オーナー「申し込みページ作れないの？ hpで送信、俺にメールが届く」
// TOWN NOTE・LIFE NOTE の /moushikomi から送られた売却・査定のお申し込みを、KV（CLICKS）に控えとして置く（キー mos|日時|乱数、60日で消える）。
// メールはページが FormSubmit へ送る。ここはメールが届かなかった時の控え。個人の情報なので、リポジトリ（公開）には書き出さない。
const BOT = /bot|crawl|spider|slurp|preview|headless|curl|wget|python/i;
const ORIGINS = ["https://townnote.pages.dev", "https://usagi-life-notes.pages.dev"];
const MAX_DAY = 30;
function day() { return new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10); }
function clean(v, max) { return String(v || "").replace(/[\u0000-\u0009\u000B-\u001F\u007F]/g, "").trim().slice(0, max); }
function res(C, ok, msg) {
  return new Response(JSON.stringify({ ok, msg }), { status: ok ? 200 : 400, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...C } });
}
export async function onRequestPost({ request, env }) {
  const o = request.headers.get("origin") || "";
  const C = ORIGINS.includes(o) ? { "access-control-allow-origin": o, vary: "origin" } : {};
  if (!ORIGINS.includes(o) || BOT.test(request.headers.get("user-agent") || "")) return res(C, false, "送れませんでした");
  let b;
  try { b = await request.json(); } catch (e) { return res(C, false, "送れませんでした"); }
  if (b.hp) return res(C, true, "ok");
  const d = {
    site: b.site === "LIFE NOTE" ? "LIFE NOTE" : "TOWN NOTE",
    name: clean(b.name, 40), email: clean(b.email, 80), tel: clean(b.tel, 20), place: clean(b.place, 60),
    kind: clean(b.kind, 10), want: clean(b.want, 20), text: clean(b.text, 2400), page: clean(b.page, 60),
  };
  if (!d.name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(d.email) || !d.place) return res(C, false, "入力を確かめてください");
  if (!env.CLICKS) return res(C, false, "いまは送れません");
  const cnt = `${day()}|mos-n`;
  const got = await env.CLICKS.getWithMetadata(cnt);
  const n = (got && got.metadata && got.metadata.n) || 0;
  if (n >= MAX_DAY) return res(C, false, "今日はたくさん届いたため、明日またお送りください");
  await env.CLICKS.put(cnt, "", { metadata: { n: n + 1 }, expirationTtl: 60 * 60 * 24 * 3 });
  d.at = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 16).replace("T", " ");
  await env.CLICKS.put(`mos|${d.at}|${Math.random().toString(36).slice(2, 8)}`, JSON.stringify(d), { expirationTtl: 60 * 60 * 24 * 60 });
  return res(C, true, "ok");
}
export async function onRequestOptions({ request }) {
  const o = request.headers.get("origin") || "";
  if (!ORIGINS.includes(o)) return new Response(null, { status: 403 });
  return new Response(null, { status: 204, headers: { "access-control-allow-origin": o, "access-control-allow-methods": "POST", "access-control-allow-headers": "content-type", "access-control-max-age": "86400", vary: "origin" } });
}
