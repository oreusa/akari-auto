// 11/1 月：/ima（いまから行けるおでかけ）用。気象庁の府県の予報を読んで、降水確率と天気だけ返す（30分ためる）
// 例 /wx?a=130000（東京）。気象庁のデータは出典を書けば使える（政府標準利用規約）
const OK = new Set(["080000", "090000", "100000", "110000", "120000", "130000", "140000"]);
export async function onRequestGet({ request }) {
  const a = new URL(request.url).searchParams.get("a") || "";
  if (!OK.has(a)) return new Response("bad area", { status: 400 });
  try {
    const r = await fetch(`https://www.jma.go.jp/bosai/forecast/data/forecast/${a}.json`, { cf: { cacheTtl: 1800, cacheEverything: true } });
    if (!r.ok) throw new Error("jma " + r.status);
    const j = await r.json();
    const ts = j[0].timeSeries;
    const w = ts[0].areas[0], p = ts[1];
    const out = {
      area: w.area.name,
      w: (w.weathers && w.weathers[0] || "").replace(/　+/g, " ").split(" ").slice(0, 3).join(" "),
      pops: p.timeDefines.map((t, i) => ({ t, v: p.areas[0].pops[i] })),
      src: "気象庁",
    };
    return new Response(JSON.stringify(out), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=1800" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), { status: 502, headers: { "content-type": "application/json" } });
  }
}
