"""関東の紅葉ライトアップ2026（11/2 オーナー「燈のは紅葉作らないのか？」「見やすい使いやすいは絶対」）。

元は data/koyo.json（公式のお知らせで確かめた日程だけ）。イルミのページ（scripts/illumi.py）と同じ作り・同じ見た目で
  /koyo          … 紅葉ライトアップだけのページ（都県のタブ・地図・近くの宿・よくある質問）
  /illumination  … いちばん下に「紅葉ライトアップ」の段とタブを足す（同じカード）
を作る。page.yml で illumi.py のすぐ後に動かす（townnotes.py が同じカードの場所を調べ、近くの宿もつく）。
"""
import html, json, os, re
from datetime import date, datetime

import illumi
from illumi import JST, ROOT, PREFS, esc

PAGE = "koyo"
BASE_CARD = illumi.card


def card(e, today):
    """イルミと同じカード。夜の時間と料金を、場所の下に1行で足す"""
    c = BASE_CARD(e, today)
    if e.get("time"):
        c = c.replace('<span class="ar">', f'<span class="pl kt">{esc(e["time"])}</span><span class="ar">', 1)
    return c


def load(today):
    d = json.load(open(os.path.join(ROOT, "data", "koyo.json"), encoding="utf-8"))
    items = [e for e in d["items"] if not e.get("end") or date.fromisoformat(e["end"]) >= today]

    def key(e):
        if not e.get("start"):
            return (2, "")
        return (0, e["end"]) if date.fromisoformat(e["start"]) <= today else (1, e["start"])
    items.sort(key=key)
    return items


def page(items, today, now):
    illumi.card, keep = card, illumi.card
    try:
        h = illumi.render(items, today, now)
    finally:
        illumi.card = keep
    n = len(items)
    names = "・".join(e["name"] for e in items if e.get("start"))
    names = "・".join(names.split("・")[:3])
    title = "関東の紅葉ライトアップ2026｜東京・神奈川・埼玉・千葉・茨城・栃木・群馬の日程・時間・料金"
    desc = (f"関東（東京・神奈川・埼玉・千葉・茨城・栃木・群馬）の紅葉ライトアップ2026を{n}か所、都県ごとに日程・夜の時間・料金・無料かどうかで一覧に。"
            f"{names}など。近くの宿も。{now.year}年{now.month}月{now.day}日更新。")
    h = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", h, count=1, flags=re.S)
    h = re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*', lambda m: m.group(1) + esc(desc), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(title), h)
    h = h.replace(f"{illumi.SITE}/{illumi.PAGE}\"", f"{illumi.SITE}/{PAGE}\"")
    h = h.replace("KANTO ILLUMINATION", "KANTO AUTUMN LEAVES")
    h = h.replace("<h1>関東イルミネーション<small>2026 - 2027 日程一覧</small></h1>", "<h1>関東の紅葉ライトアップ<small>2026 日程一覧</small></h1>")
    h = re.sub(r'<p class="lead">.*?</p>',
               f'<p class="lead">東京・神奈川・埼玉・千葉・茨城・栃木・群馬の{n}か所を、<br>日程・夜の時間・料金でまとめました。</p>', h, count=1, flags=re.S)
    # 都県ごとのイルミのページへの欄は、紅葉では「イルミネーションも見る」1つに
    h = re.sub(r'<nav class="pn"[^>]*>.*?</nav>',
               '<nav class="pn" aria-label="ほかのページ"><p class="pnh">あわせて見る</p><a href="illumination">関東のイルミネーション</a>'
               '<a href="tomari">泊まりで行く所</a><a href="ima">今から行ける所</a></nav>', h, count=1, flags=re.S)
    h = h.replace("イルミネーション2026-2027", "紅葉ライトアップ2026").replace("のイルミネーション", "の紅葉ライトアップ")
    h = h.replace("で無料で見られるイルミネーションは？", "で無料で見られる紅葉ライトアップは？").replace("のイルミネーションはいつから始まる？", "の紅葉ライトアップはいつから始まる？")
    h = h.replace("2026 - 2027", "2026").replace('"name": "関東イルミネーション2026-2027"', '"name": "関東の紅葉ライトアップ2026"')
    h = h.replace("イルミネーション", "紅葉ライトアップ").replace("関東紅葉ライトアップ", "関東の紅葉ライトアップ")
    h = h.replace('<a href="illumination">関東の紅葉ライトアップ</a>', '<a href="illumination">関東のイルミネーション</a>')
    h = h.replace("illumi-pref", "koyo-pref")
    h = h.replace("</style>", ".pl.kt{margin-top:2px;color:#6B6058}</style>", 1)
    return h


# 都県の色（site/assets/v2sub.js の PC と同じ）。都県がまざる紅葉の段では、カードごとに色と都県名を付ける
PC = {"東京": "#4F86C6", "神奈川": "#3FA3B5", "埼玉": "#E09A3E", "千葉": "#D9775A", "茨城": "#5FA06A", "栃木": "#D2697E", "群馬": "#9C7BB8"}


def mixed(e, today):
    c = card(e, today)
    c = c.replace('<li class="it"', f'<li style="--pc:{PC.get(e["pref"], "#8C7B6E")}" class="it"', 1)
    return c.replace('<span class="pl">', f'<span class="pl">{esc(e["pref"])}・', 1)


def into_illumination(items, today):
    """イルミのページのいちばん下に「紅葉ライトアップ」の段（タブでも選べる）"""
    f = os.path.join(ROOT, "site", "illumination.html")
    if not os.path.exists(f) or not items:
        return
    h = open(f, encoding="utf-8").read()
    if 'data-p="紅葉"' in h:
        return
    sec = (f'<section class="ps" data-p="紅葉"><h2>紅葉ライトアップ<b class="c">{len(items)}件</b></h2>'
           f'<ul>{"".join(mixed(e, today) for e in items)}</ul>'
           '<a class="kmore" href="koyo">紅葉ライトアップを都県ごとに見る →</a></section>')
    h = h.replace('<p class="none" hidden>', sec + '<p class="none" hidden>', 1)
    h = re.sub(r'(<nav class="tabs"[^>]*>.*?)</nav>', lambda m: m.group(1) + '<button data-f="紅葉">紅葉</button></nav>', h, count=1, flags=re.S)
    h = h.replace("</style>", ".pl.kt{margin-top:2px;color:#6B6058}.kmore{display:block;text-align:right;font-size:12.5px;color:#6B6058;"
                  "margin:4px 2px 0;text-decoration:underline;text-underline-offset:3px}</style>", 1)
    open(f, "w", encoding="utf-8").write(h)


def main():
    now = datetime.now(JST)
    today = now.date()
    items = load(today)
    site = os.path.join(ROOT, "site")
    open(os.path.join(site, f"{PAGE}.html"), "w", encoding="utf-8").write(page(items, today, now))
    into_illumination(items, today)
    sm = os.path.join(site, "sitemap.xml")
    if os.path.exists(sm):
        x = open(sm, encoding="utf-8").read()
        if f"/{PAGE}<" not in x:
            x = x.replace("</urlset>", f"  <url><loc>{illumi.SITE}/{PAGE}</loc><lastmod>{now:%Y-%m-%d}</lastmod><changefreq>daily</changefreq></url>\n</urlset>", 1)
            open(sm, "w", encoding="utf-8").write(x)
    print(json.dumps({"koyo": len(items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
