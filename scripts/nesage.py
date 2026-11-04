"""「本当に値下がりした物だけ」のページ（site/nesage.html）と、値段の記録（data/price-history.json・data/nesage.json）。

11/1 オーナー「みんなと同じことをしても出し抜けない」「計算尽くされた方法で」。
月の考え：楽天のセールでは「前に値上げしてから割引に見せる」ことが疑われていて、買う人はそこが不安。
人は何百もの商品の値段を毎日記録できないが、燈は楽天APIで毎回取れる。page.yml の回ごとに、
よく買われる毎日の物（レビューの多い順）の値段を記録し、記録した「ふだんの値段」より本当に下がった物だけを並べる。
記録が足りない物（2日分より少ない）は比べない＝数字をまちがえない。値段は送料込みの物だけ。
"""
import html
import json
import os
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
import lib  # noqa: E402

JST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://usagi-life-notes.pages.dev"
PAGE = "nesage"
WEEK = "月火水木金土日"
HIST = os.path.join(ROOT, "data", "price-history.json")
KEEP_DAYS = 45      # 値段の記録は45日分
DROP_ITEM = 21      # 21日見かけなかった商品は記録から外す
MIN_DAYS = 2        # ふだんの値段は、今日より前の2日分以上の記録があるときだけ出す
DROP = 0.05         # ふだんより5%以上安く、記録した中でいちばん安い＝本当に値下がり
UP = 0.10           # ふだんより10%以上高い＝いつもより高い
MIN_RC, MIN_AV = 300, 4.0

# key, 見出し, 検索の言葉, 入れない言葉
CATS = [
    ("water", "水", "水 天然水 2L 送料無料", ("炭酸", "サーバー", "定期", "ふるさと")),
    ("soda", "炭酸水", "炭酸水 強炭酸 500ml 送料無料", ("サーバー", "定期", "ふるさと")),
    ("rice", "お米", "米 10kg 精米", ("ふるさと", "定期", "もち米", "玄米")),
    ("tp", "トイレットペーパー", "トイレットペーパー まとめ買い", ("ふるさと", "定期", "ホルダー", "ケース")),
    ("tissue", "ティッシュ", "ティッシュペーパー まとめ買い", ("ふるさと", "定期", "ケース")),
    ("detergent", "洗濯洗剤", "洗濯洗剤 詰め替え 大容量", ("ふるさと", "定期")),
    ("softener", "柔軟剤", "柔軟剤 詰め替え 大容量", ("ふるさと", "定期")),
    ("dish", "食器用洗剤", "食器用洗剤 詰め替え 大容量", ("ふるさと", "定期")),
    ("diaper", "おむつ", "おむつ パンツ ケース", ("ふるさと", "定期")),
    ("wipes", "おしりふき", "おしりふき ケース", ("ふるさと", "定期")),
    ("coffee", "コーヒー", "コーヒー豆 ドリップ 送料無料", ("ふるさと", "定期", "メーカー", "マシン")),
    ("protein", "プロテイン", "プロテイン ホエイ 1kg", ("ふるさと", "定期", "シェイカー")),
    ("cat", "キャットフード", "キャットフード ドライ", ("ふるさと", "定期")),
    ("dog", "ドッグフード", "ドッグフード ドライ", ("ふるさと", "定期")),
    ("kairo", "カイロ", "カイロ 貼る 30個", ("ふるさと", "定期")),
    ("blanket", "電気毛布", "電気毛布", ("ふるさと", "定期", "カバー")),
    ("humid", "加湿器", "加湿器 スチーム", ("ふるさと", "定期", "フィルター")),
    ("battery", "モバイルバッテリー", "モバイルバッテリー 10000mAh", ("ふるさと", "定期", "ケース")),
]


def esc(s):
    return html.escape(str(s or ""), quote=True)


def short(name, n=46):
    name = " ".join(str(name).replace("【", " ").replace("】", " ").split())
    return name if len(name) <= n else name[:n] + "…"


def item_page(code):
    shop, _, no = str(code or "").partition(":")
    return f"https://item.rakuten.co.jp/{shop}/{no}/" if shop and no else ""


def fetch(cat):
    key, _, kw, ng = cat
    q = {"keyword": kw, "postageFlag": 1, "availability": 1, "sort": "-reviewCount", "hits": 30}
    items, err = lib._rakuten_search(q)
    time.sleep(1.1)  # 楽天APIは1秒に1回まで
    rows = []
    for it in items or []:
        name = it.get("itemName") or ""
        price = int(it.get("itemPrice") or 0)
        aff = it.get("affiliateUrl") or ""
        code = it.get("itemCode") or ""
        if not price or not code or any(w in name for w in ng) or not aff.startswith("https://hb.afl.rakuten.co.jp/"):
            continue
        rc, av = int(it.get("reviewCount") or 0), float(it.get("reviewAverage") or 0)
        if rc < MIN_RC or av < MIN_AV:
            continue
        rows.append({"code": code, "cat": key, "name": short(name), "price": price, "rc": rc, "av": av,
                     "shop": it.get("shopName") or "", "url": aff, "plain": item_page(code), "img": lib._item_image(it)})
    return rows, err


def load_hist():
    try:
        return json.load(open(HIST, encoding="utf-8"))
    except (OSError, ValueError):
        return {"since": "", "codes": {}}


def judge(h, today, price):
    """今日の値段を、今日より前の記録（14日分）と比べる。戻り：(ふだんの値段, いちばん安かった値段, 記録の日数)"""
    past = sorted((d, p) for d, p in h["p"].items() if d < today)[-14:]
    if len(past) < MIN_DAYS:
        return None, None, len(past)
    ps = [p for _, p in past]
    return statistics.median(ps), min(ps), len(past)


def card(r, kind):
    img = f'<img src="{esc(r["img"])}" alt="" width="84" height="84" loading="lazy" onerror="this.remove()">' if r["img"] else ""
    if kind == "down":
        tag = f'<span class="pu">ふだん {r["base"]:,.0f}円 → 今 <b>{r["price"]:,}円</b></span><span class="df">{r["pct"]}% 安い・{r["days"]}日分の記録でいちばん安い</span>'
    else:
        tag = f'<span class="pu">ふだん {r["base"]:,.0f}円 → 今 <b class="hi">{r["price"]:,}円</b></span><span class="df up">{r["pct"]}% 高い。急がなくてよさそう</span>'
    return (f'<li class="it"><a class="cd" href="{esc(r["url"])}" rel="sponsored noopener" target="_blank" data-k="{esc(kind + ":" + r["name"][:28])}">'
            f'{img}<span class="tx"><span class="ct">{esc(r["title"])}</span><span class="nm">{esc(r["name"])}</span>{tag}'
            f'<span class="mt">送料込み　★{r["av"]:.2f}　レビュー{r["rc"]:,}件</span>'
            f'<span class="go">楽天で見る →</span></span></a></li>')


def render(downs, ups, n_items, n_days, since, now):
    upd = f"{now.month}/{now.day}（{WEEK[now.weekday()]}）{now:%H:%M} 楽天で確かめた値段"
    s = datetime.strptime(since, "%Y-%m-%d") if since else now
    since_t = f"{s.month}/{s.day}"
    if downs:
        main = f'<ul>{"".join(card(r, "down") for r in downs)}</ul>'
    elif n_days < MIN_DAYS:
        main = (f'<p class="none">{since_t}から値段の記録を始めました。今日より前の記録が{MIN_DAYS}日分たまると、'
                f'ここに「本当に下がった物」が出ます。</p>')
    else:
        main = '<p class="none">今は、記録した中で本当に値下がりしている物はありません。値段が下がったら、ここに出ます。</p>'
    up_sec = (f'<h2 class="h2">いつもより高い物（急がなくてよさそう）</h2><ul>{"".join(card(r, "up") for r in ups)}</ul>'
              if ups else "")
    title = "楽天で本当に値下がりした物だけ｜燈が毎日値段を記録｜うさぎ│LIFE NOTES"
    desc = (f"燈が楽天のよく買われる毎日の物{n_items}件の値段を{since_t}から毎日記録し、ふだんの値段より本当に下がった物だけを並べます。"
            "お買い物マラソン・ブラックフライデーの前に。")
    css = open(os.path.join(ROOT, "scripts", "kaimawari.py"), encoding="utf-8").read()
    css = css[css.index("<style>") + 7:css.index("</style>")].replace("{{", "{").replace("}}", "}")
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/{PAGE}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/og-v10.png"><meta property="og:url" content="{SITE}/{PAGE}"><meta name="twitter:card" content="summary">
<link rel="icon" href="logo.png"><link rel="apple-touch-icon" href="logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Jost:wght@300;400&display=swap">
<style>{css}
.ct{{font-size:11px;color:var(--mute);letter-spacing:.04em}}
.pu{{font-size:12.5px;color:var(--sub)}}.pu b{{font-size:19px;color:var(--red);letter-spacing:.02em}}.pu b.hi{{color:var(--ink)}}
.df{{font-size:11.5px;color:var(--red)}}.df.up{{color:var(--mute)}}
.none{{background:#fff;border:1px solid var(--line);border-radius:4px;padding:16px;font-size:13px;line-height:1.9;color:var(--sub)}}
.h2{{font:600 15px/1.5 var(--go);margin:26px 0 10px}}
.big{{background:#fff;border:1px solid var(--line);border-radius:4px;padding:14px;margin:18px 0 0;text-align:center}}
.big b{{display:block;font:600 30px/1.2 var(--min);color:var(--ink);letter-spacing:.04em}}.big span{{font-size:12px;color:var(--mute)}}
</style><script src="/assets/night.js?v=14"></script><script src="/assets/menu.js?v=18" defer></script><link rel="stylesheet" href="/assets/sub.css?v=4"><script src="/assets/v2sub.js?v=3" defer></script></head>
<body><div class="wrap">
<header class="head"><img src="logo-s.png" alt="うさぎ│LIFE NOTES のロゴ" width="64" height="64">
<p class="en">REAL PRICE DROP</p>
<h1>本当に値下がりした物だけ<small>楽天のよく買われる毎日の物を、燈が毎日記録</small></h1>
<p class="up">{esc(upd)}</p>
<div class="big"><b>{n_items:,}件</b><span>{since_t}から値段を記録している商品の数（{n_days}日分）</span></div>
<p class="lead">セールの「〇%OFF」は、前の値段がいつの値段か分かりません。燈は、よく買われている水・お米・洗剤・おむつなどの値段を毎日楽天で記録し、記録した「ふだんの値段」（今日より前の14日分の真ん中）より5%以上安く、記録した中でいちばん安い物だけをここに出します。記録が{MIN_DAYS}日分より少ない物は比べていません。</p>
</header>
<main><h2 class="h2">今、本当に下がっている物</h2>{main}{up_sec}</main>
<footer class="foot">
<p>値段は送料込みの物だけで、このページを作った時に楽天で確かめた物です。ポイントやクーポンは入れていません。買う前にリンク先で値段を確かめてください。</p>
<p>このページのリンクは楽天アフィリエイトの広告（PR）です。</p>
<a class="back" href="./">関東おでかけリストを見る</a>
<p class="sign">うさぎ│LIFE NOTES</p>
</footer></div>
<script>
document.querySelectorAll('.cd').forEach(function(a){{a.addEventListener('click',function(){{
  try{{navigator.sendBeacon("/c?f=nesage&s=nesage&k="+encodeURIComponent(a.dataset.k||''))}}catch(e){{}}}})}});
</script></body></html>
"""


def main():
    now = datetime.now(JST)
    today = now.strftime("%Y-%m-%d")
    hist = load_hist()
    codes = hist.setdefault("codes", {})
    if not hist.get("since"):
        hist["since"] = today
    rows, errs = [], []
    for c in CATS:
        try:
            r, err = fetch(c)
        except Exception as e:  # 楽天につながらない物は、その回は飛ばす
            r, err = [], str(e)[:80]
        if err:
            errs.append(f"{c[0]}: {err[:80]}")
        rows += r
    if len(rows) < 30:  # 少なすぎる時は記録もページも前のまま
        print(json.dumps({"nesage": "少なすぎるので前のまま", "rows": len(rows), "errs": errs}, ensure_ascii=False))
        return
    titles = {c[0]: c[1] for c in CATS}
    downs, ups, seen = [], [], set()
    for r in rows:
        if r["code"] in seen:
            continue
        seen.add(r["code"])
        h = codes.setdefault(r["code"], {"p": {}})
        h.update({"n": r["name"], "c": r["cat"], "u": r["plain"], "last": today})
        base, low, days = judge(h, today, r["price"])
        h["p"][today] = min(r["price"], h["p"].get(today, r["price"]))  # 同じ日は安い方を残す
        if base is None:
            continue
        r = dict(r, title=titles.get(r["cat"], ""), base=base, days=days)
        if r["price"] <= low and r["price"] <= base * (1 - DROP):
            downs.append(dict(r, pct=round((1 - r["price"] / base) * 100)))
        elif r["price"] >= base * (1 + UP):
            ups.append(dict(r, pct=round((r["price"] / base - 1) * 100)))
    # 古い記録を消す
    old = (now - timedelta(days=KEEP_DAYS)).strftime("%Y-%m-%d")
    gone = (now - timedelta(days=DROP_ITEM)).strftime("%Y-%m-%d")
    for code in list(codes):
        h = codes[code]
        h["p"] = {d: p for d, p in h["p"].items() if d >= old}
        if h.get("last", "") < gone or not h["p"]:
            del codes[code]
    n_days = len({d for h in codes.values() for d in h["p"] if d < today})
    downs.sort(key=lambda r: -r["pct"])
    ups.sort(key=lambda r: -r["pct"])
    downs, ups = downs[:30], ups[:8]
    lib.save_json(HIST, hist)
    site = os.path.join(ROOT, "site")
    os.makedirs(site, exist_ok=True)
    open(os.path.join(site, f"{PAGE}.html"), "w", encoding="utf-8").write(render(downs, ups, len(codes), n_days, hist["since"], now))
    slim = lambda r: {k: r[k] for k in ("title", "name", "price", "base", "pct", "days", "rc", "av", "shop", "plain")}
    lib.save_json(os.path.join(ROOT, "data", "nesage.json"),
                  {"at": now.strftime("%Y-%m-%d %H:%M"), "since": hist["since"], "tracked": len(codes), "days": n_days,
                   "downs": [slim(r) for r in downs[:10]], "ups": [slim(r) for r in ups[:5]]})
    print(json.dumps({"nesage": {"rows": len(rows), "tracked": len(codes), "days": n_days, "downs": len(downs), "ups": len(ups)},
                      "errs": errs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
