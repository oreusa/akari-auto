"""「1個あたりで比べた」ページ（site/tanka.html）と data/tanka.json を作る。

11/1 オーナー「すごいって思わせてないと買われない」「数が多ければいいってもんじゃない」。
人が手でできない比べ方＝楽天の送料込みの商品を毎回100件以上取り、商品名から量（ml・本・kg・ロール・m）を読んで
「1Lあたり」「1kgあたり」「100mあたり」に直し、レビュー1,000件以上・★4.0以上の中で安い順に並べる。
量がはっきり読めない物（24本・48本を選ぶ物など）は比べない＝数字をまちがえない。
data/tanka.json は夜の回が投稿に使う（「楽天の水◯件を1Lあたりで比べたら1位は◯円」）。page.yml で毎回作る。
"""
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
import lib  # noqa: E402

JST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://usagi-life-notes.pages.dev"
PAGE = "tanka"
WEEK = "月火水木金土日"
PAGES = 4  # 1つの物で 30件×4ページ＝最大120件
TOP = 5

NUM = r"(\d+(?:\.\d+)?)"
MUST = {"soda": "炭酸", "tp": "トイレット", "rice": "米", "tea": "茶", "coffee": "コーヒー", "detergent": "洗剤", "softener": "柔軟剤",
        "shampoo": "シャンプー", "bodysoap": "ボディ", "dish": "食器", "tissue": "ティッシュ", "diaper": "おむつ", "wipes": "ふき",
        "trash": "袋", "battery": "単3", "mask": "マスク", "pasta": "パスタ", "protein": "プロテイン", "beans": "豆",
        "dogfood": "ドッグフード", "catfood": "キャットフード"}
NG = ("ふるさと", "定期", "お試し", "サンプル")
KIND = {"tea": "vol", "coffee": "vol", "detergent": "vol", "softener": "vol", "shampoo": "vol", "bodysoap": "vol", "dish": "vol",
        "tissue": "kumi", "diaper": "pcs", "wipes": "pcs", "trash": "pcs", "mask": "pcs", "battery": "hon",
        "pasta": "wt", "protein": "wt", "beans": "wt", "dogfood": "wt", "catfood": "wt"}
NEWPAGES = 2  # 足した物は 30件×2ページ（楽天APIを使いすぎない）  # 名前に必ずある言葉（検索で別の物が混ざるため）
# key, 見出し, 検索の言葉, ジャンル, 単位, 入れない言葉, 1単位のありえる値段の幅
CATS = [
    ("water", "水（ミネラルウォーター）", "水 天然水 ミネラルウォーター", "100316", "1L",
     ("炭酸", "茶", "サーバー", "定期", "コーヒー", "ジュース", "スポーツ", "ふるさと"), (15, 400)),
    ("soda", "炭酸水", "炭酸水 強炭酸", "100316", "1L",
     ("サーバー", "定期", "ジュース", "コーラ", "ふるさと", "茶"), (20, 500)),
    ("rice", "お米", "米 精米 kg", "100227", "1kg",
     ("ふるさと", "定期", "雑穀", "もち米", "玄米", "パック", "レトルト", "無洗米ではない"), (200, 2500)),
    ("tp", "トイレットペーパー", "トイレットペーパー ロール まとめ買い", "", "100m",
     ("ふるさと", "定期", "ホルダー", "ケース", "収納", "ラック"), (5, 200)),
] + [
    # 11/3 オーナー「もっと比べさせろ。項目もっとあるだろ。ここが運営資金」→ 毎日使う物を一気に足す。
    # 量の読み方は KIND（vol＝ml×本、wt＝g/kg×袋、pcs＝枚、hon＝本、kumi＝ティッシュの組×箱）。読めない物は比べない（数字をまちがえない）
    (k, t, q, "", u, NG + ng, rg) for k, t, q, u, ng, rg in [
        ("tea", "お茶（ペットボトル）", "お茶 ペットボトル 緑茶 ケース", "1L", ("紅茶", "ティーバッグ", "茶葉", "粉末", "パウダー"), (30, 500)),
        ("coffee", "コーヒー（ボトル）", "コーヒー ペットボトル 無糖 ケース", "1L", ("豆", "粉", "ドリップ", "インスタント", "カプセル"), (50, 800)),
        ("detergent", "洗濯洗剤（詰め替え）", "洗濯洗剤 詰め替え 超特大", "1L・1kg", ("粉", "シート", "ジェルボール", "柔軟剤"), (100, 3000)),
        ("softener", "柔軟剤（詰め替え）", "柔軟剤 詰め替え 超特大", "1L・1kg", ("洗剤", "シート"), (100, 3000)),
        ("shampoo", "シャンプー（詰め替え）", "シャンプー 詰め替え 大容量", "1L・1kg", ("トリートメントのみ", "サロン専売"), (200, 8000)),
        ("bodysoap", "ボディソープ（詰め替え）", "ボディソープ 詰め替え 大容量", "1L・1kg", ("固形", "石鹸 個"), (100, 5000)),
        ("dish", "食器用洗剤（詰め替え）", "食器用洗剤 詰め替え 大容量", "1L・1kg", ("食洗機", "タブレット", "粉"), (100, 3000)),
        ("tissue", "ティッシュ", "ティッシュペーパー 箱 まとめ買い", "100組", ("ウェット", "トイレット", "ケース", "カバー", "ポケット"), (2, 100)),
        ("diaper", "おむつ", "おむつ テープ パンツ ケース", "1枚", ("おしりふき", "大人", "ペット", "防水シート"), (10, 120)),
        ("wipes", "おしりふき・ウェットシート", "おしりふき ケース まとめ買い", "1枚", ("おむつ", "ケース単体", "フタ"), (0.3, 15)),
        ("trash", "ゴミ袋", "ゴミ袋 45L 枚", "1枚", ("ゴミ箱", "ホルダー", "スタンド"), (1, 60)),
        ("battery", "乾電池（単3）", "単3 乾電池 アルカリ 本", "1本", ("充電器", "単4", "ケース", "ホルダー", "充電池"), (15, 400)),
        ("mask", "マスク", "マスク 不織布 枚", "1枚", ("ケース", "ストラップ", "ホルダー", "シートマスク", "パック"), (1, 120)),
        ("pasta", "パスタ", "パスタ スパゲッティ kg", "1kg", ("ソース", "レトルト", "冷凍", "マシン"), (150, 3000)),
        ("protein", "プロテイン", "プロテイン ホエイ kg", "1kg", ("バー", "シェイカー", "ドリンク 本"), (1000, 15000)),
        ("beans", "コーヒー豆", "コーヒー豆 kg 焙煎", "1kg", ("ドリップバッグ", "インスタント", "ミル", "カプセル"), (800, 15000)),
        ("dogfood", "ドッグフード", "ドッグフード ドライ kg", "1kg", ("おやつ", "ウェット", "缶", "パウチ"), (100, 6000)),
        ("catfood", "キャットフード", "キャットフード ドライ kg", "1kg", ("おやつ", "ウェット", "缶", "パウチ", "ちゅ"), (100, 6000)),
    ]
]


def esc(s):
    return html.escape(str(s or ""), quote=True)


def short(name, n=46):
    name = " ".join(str(name).replace("【", " ").replace("】", " ").split())
    return name if len(name) <= n else name[:n] + "…"


def z2h(s):
    return str(s).translate(str.maketrans("０１２３４５６７８９．ｍｌＭＬｋｇＫＧｘＸ＊*", "0123456789.mlMLkgKG××××"))


def one(vals):
    """読めた数がちょうど1種類の時だけ使う（24本・48本のように選ぶ物は比べない）。"""
    s = sorted(set(vals))
    return s[0] if len(s) == 1 else None


def amount(cat, name):
    """商品名から量を読む。読めなければ None。戻りは (単位の数, 量の説明)。"""
    t = z2h(name)
    if cat in ("water", "soda"):
        ml = [float(v) for v in re.findall(NUM + r"\s*(?:ml|mL|ML|ミリリットル)", t)]
        ml += [float(v) * 1000 for v in re.findall(NUM + r"\s*(?:L|ℓ|リットル)(?![a-zA-Z])", t)]
        n = [int(v) for v in re.findall(r"(\d+)\s*本", t)]
        a, b = one(ml), one(n)
        if not a or not b or a < 200 or a > 2500:
            return None
        return a * b / 1000, f"{a:g}ml×{b}本"
    if cat == "rice":
        kg = [float(v) for v in re.findall(NUM + r"\s*(?:kg|KG|Kg|キロ)", t)]
        a = one(kg)
        if not a or a < 1 or a > 30:
            return None
        return a, f"{a:g}kg"
    if cat == "tp":
        m = [float(v) for v in re.findall(NUM + r"\s*(?:m|M|メートル)(?![mlLa-zA-Z])", t)]
        r = [int(v) for v in re.findall(r"(\d+)\s*(?:ロール|R(?![a-zA-Z]))", t)]
        pk = re.findall(r"(\d+)\s*(?:ロール|R)\s*[x×]\s*(\d+)\s*(?:パック|袋|セット)", t)
        a, b = one(m), one(r)
        if pk and len(set(pk)) == 1 and a:  # 12ロール×4パック の形は掛ける
            b = int(pk[0][0]) * int(pk[0][1])
        if not a or not b or a < 10 or a > 300:
            return None
        return a * b / 100, f"{a:g}m×{b}ロール"
    k = KIND.get(cat)
    cnt = [int(v) for v in re.findall(r"[x×]\s*(\d+)\s*(?:本|個|袋|パック|セット|箱|ケース)?", t)] + \
          [int(v) for v in re.findall(r"(\d+)\s*(?:本|個|袋|パック|セット)(?:入|セット|組)?(?!\s*[x×]?\s*\d)", t)]
    c1 = one(cnt) if cnt else 1
    if not c1 or c1 > 200:
        return None
    if k == "vol":
        ml = [float(v) for v in re.findall(NUM + r"\s*(?:ml|mL|ML|ミリリットル)", t)]
        ml += [float(v) * 1000 for v in re.findall(NUM + r"\s*(?:L|ℓ|リットル)(?![a-zA-Z])", t)]
        if cat not in ("tea", "coffee"):  # 洗剤などの液体は g で売る物が多い（水に近い重さ）→ 1L・1kgあたりで同じに比べる
            ml += [float(v) for v in re.findall(NUM + r"\s*(?:g|グラム)(?![a-zA-Z])", t)]
            ml += [float(v) * 1000 for v in re.findall(NUM + r"\s*(?:kg|KG|Kg|キロ)", t)]
        a = one(ml)
        if not a or a < 100 or a > 6000:
            return None
        isg = bool(re.search(NUM + r"\s*(?:g|グラム|kg|KG|Kg|キロ)(?![a-zA-Z])", t)) and cat not in ("tea", "coffee") and not re.search(r"ml|mL|ML|L(?![a-zA-Z])", t)
        d = (f"{a / 1000:g}kg" if a >= 1000 else f"{a:g}g") if isg else (f"{a / 1000:g}L" if a >= 1000 else f"{a:g}ml")
        return a * c1 / 1000, d + (f"×{c1}" if c1 > 1 else "")
    if k == "wt":
        g = [float(v) for v in re.findall(NUM + r"\s*(?:g|グラム)(?![a-zA-Z])", t)]
        g += [float(v) * 1000 for v in re.findall(NUM + r"\s*(?:kg|KG|Kg|キロ)", t)]
        a = one(g)
        if not a or a < 100 or a > 30000:
            return None
        return a * c1 / 1000, (f"{a / 1000:g}kg" if a >= 1000 else f"{a:g}g") + (f"×{c1}" if c1 > 1 else "")
    if k in ("pcs", "hon"):
        w = "枚" if k == "pcs" else "本"
        n = [int(v) for v in re.findall(r"(\d+)\s*" + w, t)]
        pk = re.findall(r"(\d+)\s*" + w + r"\s*(?:入り?)?\s*[x×]\s*(\d+)", t)
        a = one(n)
        if pk and len(set(pk)) == 1:
            a = int(pk[0][0]) * int(pk[0][1])
        if not a or a < 2 or a > 5000:
            return None
        return a, f"{a}{w}"
    if k == "kumi":
        kumi = [int(v) for v in re.findall(r"(\d+)\s*組", t)]
        box = [int(v) for v in re.findall(r"(\d+)\s*(?:箱|個|パック)", t)]
        a, b = one(kumi), one(box)
        if not a or not b or a < 50 or a > 1000:
            return None
        return a * b / 100, f"{a}組×{b}箱"
    return None


def item_page(it):
    """楽天の商品ページURL（itemCode「店:番号」から。投稿の2つ目のリンクと expect に使う）。"""
    shop, _, no = str(it.get("itemCode") or "").partition(":")
    return f"https://item.rakuten.co.jp/{shop}/{no}/" if shop and no else ""


def fetch(cat):
    key, _, kw, gid, unit, ng, (lo, hi) = cat
    rows, seen, n_all, err = [], set(), 0, ""
    for page in range(1, (NEWPAGES if key in KIND else PAGES) + 1):
        q = {"keyword": kw, "postageFlag": 1, "availability": 1, "sort": "-reviewCount", "hits": 30, "page": page}
        if gid:
            q["genreId"] = gid
        items, err = lib._rakuten_search(q)
        time.sleep(1.1)  # 楽天APIは1秒に1回まで
        if not items:
            break
        for it in items:
            code = it.get("itemCode")
            if code in seen:
                continue
            seen.add(code)
            n_all += 1
            name = it.get("itemName") or ""
            if any(w in name for w in ng) or (MUST.get(key) and MUST[key] not in name):
                continue
            am = amount(key, name)
            price = int(it.get("itemPrice") or 0)
            if not am or not price:
                continue
            per = price / am[0]
            if not (lo <= per <= hi):  # 読みまちがいらしい物は入れない
                continue
            aff = it.get("affiliateUrl") or ""
            if not aff.startswith("https://hb.afl.rakuten.co.jp/"):
                continue
            rows.append({"name": short(name), "price": price, "per": round(per, 1), "amt": am[1],
                         "rc": int(it.get("reviewCount") or 0), "av": float(it.get("reviewAverage") or 0),
                         "shop": it.get("shopName") or "", "url": aff, "plain": item_page(it),
                         "img": lib._item_image(it)})
    ok = sorted([r for r in rows if r["rc"] >= 1000 and r["av"] >= 4.0], key=lambda r: r["per"])
    out, shops = [], set()
    for r in ok:  # 同じ店は1つ（並びが1店で埋まらないように）
        if r["shop"] in shops:
            continue
        shops.add(r["shop"])
        out.append(r)
    avg = round(sum(r["per"] for r in rows) / len(rows), 1) if rows else 0
    return {"key": key, "title": cat[1], "unit": unit, "seen": n_all, "read": len(rows), "ok": len(ok),
            "avg": avg, "top": out[:TOP]}, err


AMZ_WORDS = {"water": ("天然水", "ミネラルウォーター", "水 "), "soda": ("炭酸",), "rice": ("米",), "tp": ("トイレット",)}


def amazon_rows(key, unit_lo_hi):
    """凪がブラウザで確かめたAmazonの商品（7日以内・○・レビュー1,000件以上・★4.0以上）のうち、この物に当たる物。
    11/1 オーナー「Amazonも、使えよ」。Amazonは値段を隠すことが多いので、値段が読めた物だけ1Lあたりを出し、
    読めない物は「値段はAmazonのページで」として並べる（数字は作らない）。"""
    lo, hi = unit_lo_hi
    out = []
    for asin, it in lib.amazon_checked().items():
        name = str(it.get("name", ""))
        if not any(w in name for w in AMZ_WORDS.get(key, ())) or (key == "water" and "炭酸" in name):
            continue
        res = lib.amazon_link(asin, max_age_h=168)
        if not res.get("ok"):
            continue
        m = re.search(r"[￥¥]\s*([\d,]+)|([\d,]+)\s*円", str(it.get("price", "")))
        price = int((m.group(1) or m.group(2)).replace(",", "")) if m else 0
        am = amount(key, name + " " + str(it.get("specs", "")))
        per = round(price / am[0], 1) if price and am else 0
        if per and not (lo <= per <= hi):
            per = 0
        out.append({"name": short(name), "price": price, "per": per, "amt": am[1] if am else str(it.get("specs", ""))[:30],
                    "rc": int(it.get("reviews") or 0), "av": float(it.get("stars") or 0), "url": res["link"], "asin": asin})
    return sorted(out, key=lambda r: (r["per"] == 0, r["per"]))[:2]


def amz_card(r, unit):
    pu = f'<span class="pu">{unit}あたり <b>{yen(r["per"])}円</b>（{r["price"]:,}円で計算・送料はページで）</span>' if r["per"] else \
        '<span class="pu">値段はAmazonのページで（Amazonはページを開かないと値段が出ない物があります）</span>'
    return (f'<li class="it"><a class="cd" href="{esc(r["url"])}" rel="sponsored noopener" target="_blank" data-k="amz:{esc(r["asin"])}">'
            f'<span class="rk az">A</span><span class="tx"><span class="nm">{esc(r["name"])}</span>{pu}'
            f'<span class="mt">{esc(r["amt"])}　★{r["av"]:.1f}　レビュー{r["rc"]:,}件</span>'
            f'<span class="go">Amazonで見る →</span></span></a></li>')


def yen(v):
    return f"{v:,.0f}" if v >= 100 else f"{v:,.1f}".rstrip("0").rstrip(".")


def card(r, i, unit, avg):
    img = f'<img src="{esc(r["img"])}" alt="" width="84" height="84" loading="lazy" onerror="this.remove()">' if r["img"] else ""
    diff = f'<span class="df">比べた全部の平均より {round((1 - r["per"] / avg) * 100)}% 安い</span>' if avg and r["per"] < avg * 0.95 else ""
    return (f'<li class="it"><a class="cd" href="{esc(r["url"])}" rel="sponsored noopener" target="_blank" data-k="{esc(r["name"][:30])}">'
            f'<span class="rk">{i}</span>{img}<span class="tx"><span class="nm">{esc(r["name"])}</span>'
            f'<span class="pu">{unit}あたり <b>{yen(r["per"])}円</b></span>{diff}'
            f'<span class="mt">{r["price"]:,}円（送料込み・{esc(r["amt"])}）　★{r["av"]:.2f}　レビュー{r["rc"]:,}件</span>'
            f'<span class="go">楽天で見る →</span></span></a></li>')


def render(cats, now):
    upd = f"{now.month}/{now.day}（{WEEK[now.weekday()]}）{now:%H:%M} 楽天で確かめた値段"
    seen = sum(c["seen"] for c in cats)
    tabs = "".join(f'<button type="button" data-f="{c["key"]}">{esc(c["title"].split("（")[0])}</button>' for c in cats)
    secs = ""
    for c in cats:
        lis = "".join(card(r, i, c["unit"], c["avg"]) for i, r in enumerate(c["top"], 1))
        secs += (f'<section class="ps" data-p="{c["key"]}"><h2>{esc(c["title"])}</h2>'
                 f'<p class="how">楽天の送料込みの{c["seen"]}件を見て、量が読めた{c["read"]}件を{c["unit"]}あたりに直しました。'
                 f'レビュー1,000件以上・評価4.0以上は{c["ok"]}件。その中で安い順です（同じお店は1つ）。'
                 f'{"比べた全部の平均は" + c["unit"] + "あたり" + yen(c["avg"]) + "円。" if c["avg"] else ""}</p>'
                 f'<ul>{lis}</ul>'
                 + (f'<h3 class="az3">Amazonでは（Amazonのページを開いて確かめた物）</h3><ul>{"".join(amz_card(r, c["unit"]) for r in c["amz"])}</ul>'
                    if c.get("amz") else "") + '</section>')
    names = "・".join(c["title"].split("（")[0] for c in cats)
    amz = any(c.get("amz") for c in cats)
    title = f"1個あたりで比べた 楽天{'とAmazon' if amz else ''}の{names}｜うさぎ│LIFE NOTES"
    desc = f"楽天の送料込みの商品{seen}件を、1Lあたり・1kgあたり・100mあたりに直して比べました。レビュー1,000件以上・評価4.0以上の中で安い順。"
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
.how{{font-size:12px;line-height:1.85;color:var(--sub);margin:0 0 12px}}
.rk{{flex:none;width:22px;font:600 18px/1 var(--min);color:var(--brown);padding-top:4px;text-align:center}}
.pu{{font-size:12.5px;color:var(--sub)}}.pu b{{font-size:19px;color:var(--red);letter-spacing:.02em}}
.df{{font-size:11.5px;color:var(--red)}}
.az{{font:700 13px/22px var(--en);color:#fff;background:#2B2622;border-radius:50%;width:22px;height:22px;padding:0;margin-top:2px}}
.az3{{font:600 13px/1.5 var(--go);color:var(--sub);margin:16px 0 8px}}
.big{{background:#fff;border:1px solid var(--line);border-radius:4px;padding:14px;margin:18px 0 0;text-align:center}}
.big b{{display:block;font:600 30px/1.2 var(--min);color:var(--ink);letter-spacing:.04em}}.big span{{font-size:12px;color:var(--mute)}}
</style><script src="/assets/night.js?v=14"></script><script src="/assets/menu.js?v=6" defer></script><link rel="stylesheet" href="/assets/sub.css?v=4"><script src="/assets/v2sub.js?v=3" defer></script></head>
<body><div class="wrap">
<header class="head"><img src="logo-s.png" alt="うさぎ│LIFE NOTES のロゴ" width="64" height="64">
<p class="en">PER UNIT</p>
<h1>1個あたりで比べた<small>楽天{"とAmazon" if amz else ""}の、毎日なくなる物</small></h1>
<p class="up">{esc(upd)}</p>
<div class="big"><b>{seen:,}件</b><span>今回、楽天で見て比べた商品の数</span></div>
<p class="lead">値段だけでは、どれが本当に安いか分かりません。燈が楽天の送料込みの商品を毎回取り直し、商品名の量（ml・本・kg・ロール・m）から1Lあたり・1kgあたり・100mあたりに直して比べました。24本・48本を選ぶ物のように量がひとつに決まらない物は、数字をまちがえないよう比べていません。</p>
</header>
<nav class="tabs" aria-label="物"><button type="button" data-f="" class="on">すべて</button>{tabs}</nav>
<main>{secs}</main>
<footer class="foot">
<p>値段・送料・レビューは、このページを作った時に楽天で確かめた物です。量は商品名から読んでいるので、買う前にリンク先で内容量を確かめてください。</p>
<p>このページのリンクは楽天アフィリエイト・Amazonアソシエイトの広告（PR）です。Amazonのアソシエイトとして、うさぎ│LIFE NOTES は適格販売により収入を得ています。</p>
<a class="back" href="./">関東おでかけリストを見る</a>
<p class="sign">うさぎ│LIFE NOTES</p>
</footer></div>
<script>
(function(){{
  var bs=document.querySelectorAll('.tabs button');
  bs.forEach(function(b){{b.addEventListener('click',function(){{var f=b.dataset.f;
    document.querySelectorAll('.ps').forEach(function(s){{s.hidden=!!f&&s.dataset.p!==f}});
    bs.forEach(function(x){{x.classList.toggle('on',x===b)}});}})}});
  document.querySelectorAll('.cd').forEach(function(a){{a.addEventListener('click',function(){{
    try{{navigator.sendBeacon("/c?f=tanka&s=tanka&k="+encodeURIComponent(a.dataset.k||''))}}catch(e){{}}}})}});
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
            try:
                r["amz"] = amazon_rows(c[0], c[6])
            except Exception as e:  # Amazonが読めなくても楽天の比べは出す
                errs.append(f"{c[0]} amazon: {str(e)[:60]}")
            cats.append(r)
    print(json.dumps({"tanka": [(c["key"], c["seen"], c["read"], c["ok"], len(c["top"])) for c in cats], "errs": errs},
                     ensure_ascii=False))
    if len(cats) < 2:  # 少なすぎる時は前のページを残す
        return
    site = os.path.join(ROOT, "site")
    os.makedirs(site, exist_ok=True)
    open(os.path.join(site, f"{PAGE}.html"), "w", encoding="utf-8").write(render(cats, now))
    slim = [{k: c[k] for k in ("key", "title", "unit", "seen", "read", "ok", "avg")} |
            {"top": [{k: r[k] for k in ("name", "price", "per", "amt", "rc", "av", "shop", "plain")} for r in c["top"]],
             "amazon": [{k: r[k] for k in ("asin", "name", "price", "per", "amt", "rc", "av")} for r in c.get("amz", [])]}
            for c in cats]
    lib.save_json(os.path.join(ROOT, "data", "tanka.json"), {"at": now.strftime("%Y-%m-%d %H:%M"), "cats": slim})


if __name__ == "__main__":
    main()
