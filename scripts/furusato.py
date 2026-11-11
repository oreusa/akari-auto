"""ふるさと納税「寄付1万円で、どれだけもらえるか」で比べたページ（site/furusato.html）と data/furusato.json を作る。

11/1 オーナー（月へ）「燈は売上を絶対作れ…月なりに方向転換してくれ」。
月の考え：11〜12月はふるさと納税のいちばんの時期（12/31 まで）。買う人が「どれが得か」を探している時に、
燈の「1個あたりで比べる」力がそのまま使える。1件の金額も大きい（1万円〜）。
楽天のふるさと納税の返礼品を毎回取り直し、商品名から量（kg・ロール・m・ml・本）を読んで「寄付1万円あたり」に直す。
量がひとつに決まらない物（選べる・定期便）は比べない＝数字をまちがえない。page.yml で毎回作る。
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
import lib  # noqa: E402
import tanka  # noqa: E402
from tanka import esc, short, item_page, z2h, one, NUM  # noqa: E402

JST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://usagi-life-notes.pages.dev"
PAGE = "furusato"
WEEK = "月火水木金土日"
PAGES = 6
TOP = 8
MIN_RC, MIN_AV = 30, 4.0  # 11/12 100件以上だとお米2件・水1件しか残らず、比べた事にならなかった → 30件以上・★4.0以上
NG_ALL = ("定期", "回お届け", "ヶ月", "か月", "カ月", "選べる", "えらべる", "お試し", "訳あり品の量", "頒布")
# key, 見出し, 検索の言葉, 単位, 名前に必ずある言葉, 入れない言葉, 寄付1万円あたりのありえる量の幅
CATS = [
    ("rice", "お米", "ふるさと納税 米 精米", "kg", "米", ("もち米", "玄米", "パック", "レトルト", "雑穀", "米粉", "米麹", "酒"), (2, 40)),
    ("tp", "トイレットペーパー", "ふるさと納税 トイレットペーパー", "m", "トイレット", ("ホルダー", "ケース", "ティッシュのみ"), (300, 15000)),
    ("water", "水", "ふるさと納税 水 天然水 ミネラルウォーター", "L", "水", ("炭酸", "茶", "サーバー", "コーヒー", "ジュース", "水産", "水揚", "水煮", "水炊"), (8, 400)),
]


def amount(key, name):
    """商品名から量を読む。読めなければ None。戻りは (量, 説明)。"""
    t = z2h(name)
    if key == "rice":
        pk = re.findall(NUM + r"\s*(?:kg|KG|Kg|キロ)\s*[x×]\s*(\d+)\s*(?:袋|個|セット|p|P)?", t)
        if pk and len(set(pk)) == 1:
            a, b = float(pk[0][0]), int(pk[0][1])
            return a * b, f"{a:g}kg×{b}"
        kg = [float(v) for v in re.findall(NUM + r"\s*(?:kg|KG|Kg|キロ)", t)]
        a = one(kg)
        if not a or a < 1 or a > 60:
            return None
        return a, f"{a:g}kg"
    if key == "tp":
        r = tanka.amount("tp", name)
        if not r:
            return None
        return r[0] * 100, r[1]  # tanka は100m単位
    if key == "water":
        r = tanka.amount("water", name)
        if not r:
            return None
        return r[0], r[1]
    return None


def fetch(cat):
    key, _, kw, unit, must, ng, (lo, hi) = cat
    rows, seen, n_all, err = [], set(), 0, ""
    for page in range(1, PAGES + 1):
        q = {"keyword": kw, "availability": 1, "sort": "-reviewCount", "hits": 30, "page": page}
        items, err = lib._rakuten_search(q)
        time.sleep(1.1)  # 楽天APIは1秒に1回まで
        if not items:
            break
        for it in items:
            code = it.get("itemCode")
            if code in seen:
                continue
            seen.add(code)
            name = it.get("itemName") or ""
            if "ふるさと納税" not in name and "ふるさと納税" not in (it.get("catchcopy") or ""):
                continue
            n_all += 1
            if must not in name or any(w in name for w in ng + NG_ALL):
                continue
            am = amount(key, name)
            price = int(it.get("itemPrice") or 0)
            if not am or price < 3000:
                continue
            per = am[0] / price * 10000
            if not (lo <= per <= hi):  # 読みまちがいらしい物は入れない
                continue
            aff = it.get("affiliateUrl") or ""
            if not aff.startswith("https://hb.afl.rakuten.co.jp/"):
                continue
            rows.append({"name": short(name, 52), "price": price, "per": round(per, 1), "amt": am[1],
                         "rc": int(it.get("reviewCount") or 0), "av": float(it.get("reviewAverage") or 0),
                         "shop": it.get("shopName") or "", "url": aff, "plain": item_page(it),
                         "img": lib._item_image(it)})
    ok = sorted([r for r in rows if r["rc"] >= MIN_RC and r["av"] >= MIN_AV], key=lambda r: -r["per"])
    out, shops = [], set()
    for r in ok:  # 同じ町は1つ
        if r["shop"] in shops:
            continue
        shops.add(r["shop"])
        out.append(r)
    avg = round(sum(r["per"] for r in rows) / len(rows), 1) if rows else 0
    return {"key": key, "title": cat[1], "unit": unit, "seen": n_all, "read": len(rows), "ok": len(ok),
            "avg": avg, "top": out[:TOP]}, err


def num(v):
    return f"{v:,.0f}" if v >= 100 else f"{v:,.1f}".rstrip("0").rstrip(".")


def card(r, i, unit, avg):
    img = f'<img src="{esc(r["img"])}" alt="" width="84" height="84" loading="lazy" onerror="this.remove()">' if r["img"] else ""
    diff = f'<span class="df">比べた全部の平均の {r["per"] / avg:.1f}倍</span>' if avg and r["per"] > avg * 1.1 else ""
    return (f'<li class="it"><a class="cd" href="{esc(r["url"])}" rel="sponsored noopener" target="_blank" data-k="{esc(r["name"][:30])}">'
            f'<span class="rk">{i}</span>{img}<span class="tx"><span class="nm">{esc(r["name"])}</span>'
            f'<span class="pu">寄付1万円あたり <b>{num(r["per"])}{unit}</b></span>{diff}'
            f'<span class="mt">寄付{r["price"]:,}円（{esc(r["amt"])}）　{esc(r["shop"][:16])}　★{r["av"]:.2f}　レビュー{r["rc"]:,}件</span>'
            f'<span class="go">楽天ふるさと納税で見る →</span></span></a></li>')


LEAD = '''<p class="lead">寄付額だけでは、どれがたくさんもらえるか分かりません。楽天のふるさと納税の返礼品を毎回取り直し、商品名の量（kg・ロール・m・ml・本）から「寄付1万円あたり」に直して比べました。量を選ぶ物・定期便のように量がひとつに決まらない物は、数字をまちがえないよう比べていません。</p>'''


def render(cats, now, one=None, allc=None):
    """one＝その物だけのページ（/furusato-<key>。11/12 検索から直に来られる入口。それまで /furusato は1度も押されていなかった）"""
    allc = allc or cats
    upd = f"{now.month}/{now.day}（{WEEK[now.weekday()]}）{now:%H:%M} 楽天で確かめた寄付額"
    seen = sum(c["seen"] for c in cats)
    tabs = "".join(f'<button type="button" data-f="{c["key"]}">{esc(c["title"])}</button>' for c in cats)
    secs = ""
    for c in cats:
        lis = "".join(card(r, i, c["unit"], c["avg"]) for i, r in enumerate(c["top"], 1))
        secs += (f'<section class="ps" data-p="{c["key"]}"><h2>{esc(c["title"])}</h2>'
                 f'<p class="how">楽天のふるさと納税の{c["seen"]}件を見て、量が読めた{c["read"]}件を「寄付1万円あたり」に直しました。'
                 f'レビュー{MIN_RC}件以上・評価{MIN_AV:.1f}以上は{c["ok"]}件。その中で多い順です（同じ町は1つ）。'
                 f'{"比べた全部の平均は1万円あたり" + num(c["avg"]) + c["unit"] + "。" if c["avg"] else ""}</p>'
                 f'<ul>{lis}</ul></section>')
    names = "・".join(c["title"] for c in cats)
    title = f"ふるさと納税 寄付1万円あたりで比べた{names}｜うさぎ│LIFE NOTES"
    path = PAGE
    if one:
        c0 = cats[0]; path = f"{PAGE}-{c0['key']}"
        title = f"ふるさと納税の{c0['title']}、寄付1万円で何{c0['unit']}？多い順（{now.month}月{now.day}日更新）｜くらべたおかいものリスト"
    more = "".join(f'<a href="/{PAGE}-{c["key"]}">ふるさと納税の{esc(c["title"])}</a>　' for c in allc if len(c["top"]) >= 3 and (not one or c["key"] != cats[0]["key"]))
    more += "".join(f'<a href="/okaimono-{c["key"]}">ふつうに買う時の{esc(c["title"])}の最安</a>　' for c in cats) if one else ""
    desc = f"楽天のふるさと納税の返礼品{seen}件を、寄付1万円あたりの量（kg・m・L）に直して比べました。レビュー{MIN_RC}件以上・評価{MIN_AV:.1f}以上の中で多い順。毎日更新。"
    css = open(os.path.join(ROOT, "scripts", "kaimawari.py"), encoding="utf-8").read()
    css = css[css.index("<style>") + 7:css.index("</style>")].replace("{{", "{").replace("}}", "}")
    left = (datetime(now.year, 12, 31, tzinfo=JST).date() - now.date()).days
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/{path}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/og-v10.png"><meta property="og:url" content="{SITE}/{path}"><meta name="twitter:card" content="summary">
<link rel="icon" href="/logo.png"><link rel="apple-touch-icon" href="/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Jost:wght@300;400&display=swap">
<style>{css}
.how{{font-size:12px;line-height:1.85;color:var(--sub);margin:0 0 12px}}
.rk{{flex:none;width:22px;font:600 18px/1 var(--min);color:var(--brown);padding-top:4px;text-align:center}}
.pu{{font-size:12.5px;color:var(--sub)}}.pu b{{font-size:19px;color:var(--red);letter-spacing:.02em}}
.df{{font-size:11.5px;color:var(--red)}}
.big{{background:#fff;border:1px solid var(--line);border-radius:4px;padding:14px;margin:18px 0 0;text-align:center;display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.big b{{display:block;font:600 28px/1.2 var(--min);color:var(--ink);letter-spacing:.04em}}.big span{{font-size:12px;color:var(--mute)}}
.note{{font-size:12px;line-height:1.85;color:var(--sub);background:#fff;border:1px solid var(--line);border-radius:4px;padding:12px 14px;margin:14px 0 0}}
</style><script src="/assets/night.js?v=14"></script><script src="/assets/menu.js?v=46" defer></script><link rel="stylesheet" href="/assets/sub.css?v=4"><script src="/assets/v2sub.js?v=11" defer></script></head>
<body><div class="wrap">
<header class="head"><img src="/logo-s.png" alt="うさぎ│LIFE NOTES のロゴ" width="64" height="64">
<p class="en">FURUSATO NOZEI</p>
<h1>{("ふるさと納税の" + esc(names) + "<small>寄付1万円で何" + cats[0]["unit"] + "もらえるか・多い順</small>") if one else ("寄付1万円あたりで比べた<small>楽天のふるさと納税（" + esc(names) + "）</small>")}</h1>
<p class="up">{esc(upd)}</p>
<div class="big"><div><b>{seen:,}件</b><span>比べた返礼品</span></div><div><b>あと{left}日</b><span>12/31の締め切りまで</span></div></div>
{"" if one else LEAD}
</header>
{"" if one else '<nav class="tabs" aria-label="物"><button type="button" data-f="" class="on">すべて</button>' + tabs + "</nav>"}
<main>{secs}
<p class="note">ふるさと納税は、自己負担2,000円をこえる分が税金から引かれます（控除の上限は収入や家族で変わります）。上限は総務省のふるさと納税ポータルサイトや楽天ふるさと納税のシミュレーションで確かめてから寄付してください。</p>
<p class="note">ほかの物：{more}</p>
</main>
<footer class="foot">
<p>寄付額・レビューは、このページを作った時に楽天で確かめた物です。量は商品名から読んでいるので、寄付する前にリンク先で内容量・届く時期を確かめてください。</p>
<p>このページのリンクは楽天アフィリエイトの広告（PR）です。</p>
<a class="back" href="/okaimono">くらべたおかいものリストを見る</a>
<p class="sign">うさぎ│LIFE NOTES</p>
</footer></div>
<script>
(function(){{
  var bs=document.querySelectorAll('.tabs button');
  bs.forEach(function(b){{b.addEventListener('click',function(){{var f=b.dataset.f;
    document.querySelectorAll('.ps').forEach(function(s){{s.hidden=!!f&&s.dataset.p!==f}});
    bs.forEach(function(x){{x.classList.toggle('on',x===b)}});}})}});
  document.querySelectorAll('.cd').forEach(function(a){{a.addEventListener('click',function(){{
    try{{navigator.sendBeacon("/c?f=furusato&s=furusato&k="+encodeURIComponent(a.dataset.k||''))}}catch(e){{}}}})}});
}})();
</script></body></html>
"""


def main():
    now = datetime.now(JST)
    cats, errs = [], []
    for c in CATS:
        try:
            r, err = fetch(c)
        except Exception as e:  # 楽天につながらない時は、その物を出さない
            r, err = None, str(e)[:80]
        if err:
            errs.append(f"{c[0]}: {err[:80]}")
        if r and r["top"]:
            cats.append(r)
    print(json.dumps({"furusato": [(c["key"], c["seen"], c["read"], c["ok"], len(c["top"])) for c in cats], "errs": errs},
                     ensure_ascii=False))
    if not cats:  # 1つも無い時は前のページを残す
        return
    site = os.path.join(ROOT, "site")
    os.makedirs(site, exist_ok=True)
    open(os.path.join(site, f"{PAGE}.html"), "w", encoding="utf-8").write(render(cats, now))
    made = []
    for c in cats:  # 物ごとのページ（3件以上ある物だけ。薄いページは作らない）
        if len(c["top"]) >= 3:
            open(os.path.join(site, f"{PAGE}-{c['key']}.html"), "w", encoding="utf-8").write(render([c], now, one=True, allc=cats))
            made.append(c["key"])
    sm = os.path.join(site, "sitemap.xml")
    if os.path.exists(sm):
        x = open(sm, encoding="utf-8").read()
        add = "".join(f"<url><loc>{SITE}/{PAGE}-{k}</loc></url>" for k in made if f"/{PAGE}-{k}<" not in x)
        if add:
            open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", add + "</urlset>", 1))
    slim = [{k: c[k] for k in ("key", "title", "unit", "seen", "read", "ok", "avg")} | {"page": c["key"] in made} |
            {"top": [{k: r[k] for k in ("name", "price", "per", "amt", "rc", "av", "shop", "plain")} for r in c["top"]]}
            for c in cats]
    lib.save_json(os.path.join(ROOT, "data", "furusato.json"), {"at": now.strftime("%Y-%m-%d %H:%M"), "cats": slim})


if __name__ == "__main__":
    main()
