"""11/22「本当に安い？」のページ（/nesage を作り替え）の中身。
オーナー（11/22）「見やすくて使いやすいなら月に任せる。どう見たらいいか分からないにならないように。使う人・見る人のことを考えて」。
data/price-history.json（楽天の日用品・11/1 から毎日の値段。nesage.py が毎回記録）から、1品ずつ
  今が安い／上げてから下げた／いつもより高い／変わらない
を決め、その理由を「うちの記録の事実」だけの1文にする（お店を悪く言わない）。描くのは site/shin/honto.js。
shin_kanto.py の furu() から呼ぶ：build() → dict（ページの data）。"""
import json
import os
import re
import statistics
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JST = timezone(timedelta(hours=9))
AFF = os.environ.get("RAKUTEN_AFFILIATE_ID") or "58b50f43.00cd84ff.58b50f44.4872e82d"
MIN_DAYS = 7          # 7日分より少ない物は決めない（数字をまちがえない）
LOW = 0.97            # 3%以上安い＝安い
PEAK = 1.08           # 途中で8%以上上がった＝上げた
HIGH = 1.05           # ふだんより5%以上高い＝高い
TITLE = {"water": "水", "soda": "炭酸水", "rice": "お米", "tp": "トイレットペーパー", "tissue": "ティッシュ", "detergent": "洗濯洗剤",
         "softener": "柔軟剤", "dish": "食器用洗剤", "diaper": "おむつ", "wipes": "おしりふき", "coffee": "コーヒー", "protein": "プロテイン",
         "cat": "キャットフード", "dog": "ドッグフード", "kairo": "カイロ", "blanket": "電気毛布", "humid": "加湿器", "battery": "モバイルバッテリー"}
ORDER = list(TITLE)


def md(d):
    return f"{int(d[5:7])}/{int(d[8:10])}"


def yen(n):
    return f"{int(round(n)):,}円"


def short(n, k=40):
    n = re.sub(r"【[^】]*】|\[[^\]]*\]|［[^］]*］|《[^》]*》|『[^』]*』|「[^」]*」|（[^）]*）|＼[^／]*／|＼[^ ]*|期間限定[^ ]*まで|[0-9０-９]+[%％]\s*OFF|★|☆|◆|■|●|！|!", " ", n or "")
    n = re.sub(r"\s+", " ", n).strip()
    return n if len(n) <= k else n[:k].rstrip() + "…"


def link(h):
    if h.get("a"):
        return h["a"]
    u = h.get("u") or ""
    return f"https://hb.afl.rakuten.co.jp/hgc/{AFF}/?pc={quote(u, safe='')}&m={quote(u, safe='')}" if u else ""


def judge(ds, ps):
    """ds＝日付、ps＝値段（同じ長さ・古い順）。(種類, 1文, 並べる数)"""
    first, now, d0 = ps[0], ps[-1], ds[0]
    prior = ps[:-1]
    med, low, peak = statistics.median(prior), min(prior), max(prior)
    since = "11/1" if d0.endswith("-11-01") else md(d0)
    start = "11/1" if d0.endswith("-11-01") else f"記録をはじめた{md(d0)}"
    # 今の値段になった日（同じ値段が続いている最初の日）
    k = len(ps) - 1
    while k > 0 and ps[k - 1] == now:
        k -= 1
    from_d = md(ds[k])
    pi = ps.index(peak)
    if peak >= first * PEAK and pi > 0 and now < peak and now >= first * LOW:
        diff = now - first
        tail = "と同じ値段です。" if diff == 0 else (f"より{yen(diff)}高い値段です。" if diff > 0 else f"とくらべて{yen(-diff)}しか安くありません。")
        return "b", f"{md(ds[pi])}に{yen(peak)}へ上がり、{from_d}から{yen(now)}に。{since}の{yen(first)}{tail}", (peak - now) / peak, [md(ds[pi]), peak]
    if now <= low and now <= med * LOW and now < first:
        pct = round((1 - now / first) * 100)
        return "a", f"{start}は{yen(first)}。{from_d}から{yen(now)}になり、{since}からの記録でいちばん安い値段です。{since}より{yen(first - now)}（{pct}%）安い。", 1 - now / first, [since, first]
    if now >= med * HIGH:
        pct = round((now / med - 1) * 100)
        return "c", f"ふだん（記録のまん中）は{yen(med)}。{from_d}から{yen(now)}で、{pct}%高い値段です。急がない物は、待つのも手です。", now / med - 1, ["ふだん", round(med)]
    if len(set(ps)) == 1:
        return "d", f"{since}から{len(ps)}日、ずっと{yen(now)}です。", 0, None
    return "d", f"{since}から大きくは変わっていません（{yen(min(ps))}〜{yen(max(ps))}）。", 0, None


def build(now=None):
    now = now or datetime.now(JST)
    h = json.load(open(os.path.join(R, "data", "price-history.json"), encoding="utf-8"))
    codes = h.get("codes", {})
    days = sorted({d for v in codes.values() for d in v.get("p", {})})
    if not days:
        return None
    last = days[-1]
    fresh = (date.fromisoformat(last) - timedelta(days=2)).isoformat()
    # 写真・リンクの足し（記録に写真がまだ無い物は、前の nesage.json の行から）
    extra, at = {}, now.strftime("%Y-%m-%d %H:%M")
    try:
        n = json.load(open(os.path.join(R, "data", "nesage.json"), encoding="utf-8"))
        at = n.get("at") or at  # 値段を最後にしらべた時
        for r in (n.get("downs") or []) + (n.get("ups") or []):
            extra[r.get("plain")] = r
    except Exception:
        pass
    span = [d.isoformat() for d in (date.fromisoformat(days[0]) + timedelta(days=i) for i in range((date.fromisoformat(last) - date.fromisoformat(days[0])).days + 1))]
    out, seen = [], set()
    for code, v in codes.items():
        p = v.get("p") or {}
        ds = sorted(p)
        if len(ds) < MIN_DAYS or v.get("last", "") < fresh or ds[-1] < fresh:
            continue
        ps = [p[d] for d in ds]
        # 1日で半分・2倍のような動きは、量や種類（セット数）が変わった見え方のことが多い → まちがえないよう載せない
        if any(b >= a * 1.8 or b <= a * 0.55 for a, b in zip(ps, ps[1:])):
            continue
        kind, why, score, ref = judge(ds, ps)
        x = extra.get(v.get("u")) or {}
        it = {"id": code, "n": short(v.get("n")), "c": v.get("c", ""), "v": kind, "why": why, "now": ps[-1], "first": ps[0],
              "lo": min(ps), "hi": max(ps), "sc": round(score, 4), "ref": ref, "url": link(v) or x.get("url", ""),
              "img": v.get("i") or x.get("img", ""), "s": v.get("s") or x.get("shop", ""),
              "h": [p.get(d) for d in span if d >= ds[0]], "d0": ds[0]}
        key = (it["n"][:16], it["now"], it["first"], it["c"])  # 同じ商品が別の番号で2つある時は1つだけ
        if not it["url"] or key in seen:
            continue
        seen.add(key)
        if kind == "d":  # 変わらない物はグラフを出さないので軽く
            for k_ in ("h", "lo", "hi", "sc", "first"):
                it.pop(k_, None)
        out.append(it)
    rank = {k: i for i, k in enumerate(ORDER)}
    out.sort(key=lambda x: ("abcd".index(x["v"]), -x["sc"] if x["v"] != "d" else rank.get(x["c"], 99), x["now"]))
    cnt = {k: sum(1 for x in out if x["v"] == k) for k in "abcd"}
    try:
        import bf_okaimono
        bf = bf_okaimono.START <= now <= bf_okaimono.END
        bfe = bf_okaimono.END
    except Exception:
        bf, bfe = False, None
    return {"kind": "honto", "h1": "本当に安い？", "at": at, "since": days[0], "last": last, "n": len(out),
            "cnt": cnt, "rows": out, "tt": {k: TITLE[k] for k in ORDER}, "room": "https://room.rakuten.co.jp/ai_usagichan/items",
            "bf": (f"{bfe.month}月{bfe.day}日 {bfe.hour}:{bfe.minute:02d}" if bf and bfe else "")}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(R, "scripts"))
    d = build()
    print(d["n"], d["cnt"])
    for x in d["rows"]:
        if x["v"] != "d":
            print(x["v"], x["n"][:24], "|", x["why"])
