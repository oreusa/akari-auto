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
    """イルミと同じカードに、月と同じ「時間」「料金」の行と「今夜やっています」の札を足す（11/2 月の /koyo にそろえる）"""
    c = BASE_CARD(e, today).replace('<li class="it"', '<li class="it ky"', 1)
    if not e.get("start"):
        # 日程を公式で文字として確かめられていない所は、期間をのせない（月と同じ）
        c = re.sub(r'<span class="dt">.*?</span>', '<span class="dt">日程は公式でご確認ください</span>', c, count=1, flags=re.S)
        c = c.replace('<span class="st tba">発表前</span>', '<span class="st tba">日程は公式で</span>', 1)
    c = c.replace('</span><span class="dt">', '<span class="tn8" hidden>今夜やっています</span></span><span class="dt">', 1)
    rows = "".join(f'<span class="kv"><span>{k}</span>{esc(e[f])}</span>' for k, f in (("時間", "hours"), ("料金", "fee")) if e.get(f))
    return c.replace('<span class="ar">', rows + '<span class="ar">', 1)


# 月の tools/illumi/build.py と同じ形（イルミ⇔紅葉の切りかえ・時間と料金の行・今夜の札・今夜だけボタン）
KCSS = (".sw{display:flex;margin:20px 0 0;border:1px solid #D4D4D4;border-radius:99px;padding:3px;background:#fff}"
        ".sw a{flex:1;text-align:center;padding:9px 0;border-radius:99px;font-size:13.5px;font-weight:700;letter-spacing:.06em;color:#6B6058;text-decoration:none}"
        ".sw a[aria-current]{background:#2B2622;color:#fff}"
        ".cd .kv{display:flex;gap:10px;font-size:13px;line-height:1.6;color:#3A3A3A;margin-top:3px}"
        ".cd .kv span{flex:none;width:3.4em;font-size:11px;color:#8C7B6E;letter-spacing:.06em;padding-top:1px}"
        "html body .cw .cd .tn8{border-radius:99px;padding:4px 10px;font-size:11px;font-weight:700;line-height:1.2;background:#2B2622;color:#fff}"
        "html body .cw .cd .tn8[hidden]{display:none}"
        ".tnb{text-align:center;margin:12px 0 0}.tnb button{font-family:'Zen Kaku Gothic New';font-size:13px;font-weight:700;letter-spacing:.06em;color:#2B2622;"
        "background:#fff;border:1px solid #2B2622;border-radius:99px;padding:8px 18px;cursor:pointer}"
        ".tnb button[aria-pressed=true]{background:#2B2622;color:#fff}"
        ".kmore{display:block;text-align:right;font-size:12.5px;color:#2B2622;text-decoration:none;margin:4px 2px 0}"
        ".none8{text-align:center;font-size:13px;color:#7A6E66;margin:24px 0}")
KJS = ("<script>(function(){var t=new Date(Date.now()+9*36e5).toISOString().slice(0,10);"
       "document.querySelectorAll('.it.ky').forEach(function(li){var s=li.dataset.s,e=li.dataset.e;"
       "if(s&&s<=t&&(!e||e>=t)){li.classList.add('tonight');var x=li.querySelector('.tn8');if(x)x.hidden=false;}});"
       "var B=document.getElementById('tnb');if(!B)return;var N=false;"
       "B.onclick=function(){N=!N;B.setAttribute('aria-pressed',N);"
       "document.querySelectorAll('.it.ky').forEach(function(li){li.style.display=(!N||li.classList.contains('tonight'))?'':'none';});"
       "document.querySelectorAll('.ps').forEach(function(sec){var v=[].filter.call(sec.querySelectorAll('.it'),function(i){return i.style.display!='none';}).length;"
       "var c=sec.querySelector('.c');if(c)c.textContent=v+'件';sec.style.display=v?'':'none';});"
       "var z=document.getElementById('none8');if(z)z.hidden=!N||[].some.call(document.querySelectorAll('.ps'),function(x){return x.style.display!='none'&&!x.hidden;});"
       "try{navigator.sendBeacon('/c?f=koyo&s=koyo&k='+encodeURIComponent('今夜だけ'+(N?'':'解除')));}catch(e){}};})();</script>")


def sw(koyo, href="/illumination"):
    return (f'<nav class="sw" aria-label="見るもの"><a href="{href}"{"" if koyo else " aria-current=page"}>イルミネーション</a>'
            f'<a href="/koyo"{" aria-current=page" if koyo else ""}>紅葉ライトアップ</a></nav>')


def dress(h, koyo, href="/illumination"):
    """切りかえボタン・CSS・今夜の札の JS を付ける（紅葉もイルミも同じ）"""
    if 'class="sw"' not in h:
        h = h.replace("</header>", "</header>" + sw(koyo, href), 1)
    if ".sw{" not in h:
        h = h.replace("</style>", KCSS + "</style>", 1)
    if "querySelectorAll('.it.ky')" not in h:
        h = h.replace("</body>", KJS + "</body>", 1)
    return h


def load(today):
    d = json.load(open(os.path.join(ROOT, "data", "koyo.json"), encoding="utf-8"))
    # 11/2 終わる日が無いのに始まる日だけある物でページ作りが止まった → 日程未発表として扱う
    for e in d["items"]:
        if e.get("start") and not e.get("end"):
            e["start"] = None
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
    h = h.replace("発表前", "日程は公式で")
    h = re.sub(r'<details><summary>日程が「日程は公式で」の所はどうなりますか？</summary><p>.*?</p></details>',
               '<details><summary>日程が「日程は公式で」の所はどうなりますか？</summary><p>2026年の日程を、公式ページでまだ確かめられていない所です。分かりしだい書き足します。お出かけ前にリンク先でご確認ください。</p></details>', h, flags=re.S)
    h = re.sub(r'<p>日程は各公式のお知らせで確かめた物です。.*?</p>',
               '<p>日程・時間・料金は、各公式ページで確かめてのせています。名前を押すと公式のページ、「地図」を押すと場所が開きます。「今夜やっています」は、今日が期間の中の所です。紅葉の色づきは年によってずれるので、お出かけ前にリンク先でご確認ください。</p>', h, count=1, flags=re.S)
    h = re.sub(r'(<nav class="tabs"[^>]*>.*?</nav>)', r'\1<div class="tnb"><button id="tnb" aria-pressed="false">今夜やっている所だけ</button></div>', h, count=1, flags=re.S)
    h = h.replace('<p class="none" hidden>', '<p class="none8" id="none8" hidden>今夜やっている所は、ありません。ボタンをもう一度押すと全部出ます。</p><p class="none" hidden>', 1)
    return dress(h, True)


# 都県の色（site/assets/v2sub.js の PC と同じ）。都県がまざる紅葉の段では、カードごとに色と都県名を付ける
PC = {"東京": "#4F86C6", "神奈川": "#3FA3B5", "埼玉": "#E09A3E", "千葉": "#D9775A", "茨城": "#5FA06A", "栃木": "#D2697E", "群馬": "#9C7BB8"}


def mixed(e, today):
    c = card(e, today)
    c = c.replace('<li class="it ky"', f'<li style="--pc:{PC.get(e["pref"], "#8C7B6E")}" class="it ky"', 1)
    return c.replace('<span class="pl">', f'<span class="pl">{esc(e["pref"])}・', 1)


def into_illumination(items, today):
    """イルミのページにも紅葉の段（月と同じ）。関東ぜんぶのページは下に「紅葉」の段とタブ、都県のページはその都県の紅葉"""
    for p, full in [(None, "関東")] + list(PREFS):
        slug = illumi.PAGE + (f"-{illumi.YADO[p]}" if p else "")
        f = os.path.join(ROOT, "site", slug + ".html")
        if not os.path.exists(f):
            continue
        h = open(f, encoding="utf-8").read()
        rows = [e for e in items if not p or e["pref"] == p]
        if rows and 'data-p="紅葉"' not in h:
            name = "紅葉ライトアップ" if not p else f"{full}の紅葉ライトアップ"
            sec = (f'<section class="ps" data-p="紅葉"><h2>{name}<b class="c">{len(rows)}件</b></h2>'
                   f'<ul>{"".join((mixed if not p else card)(e, today) for e in rows)}</ul>'
                   '<a class="kmore" href="/koyo">関東ぜんぶの紅葉ライトアップを見る →</a></section>')
            h = h.replace('<p class="none" hidden>', sec + '<p class="none" hidden>', 1)
            if not p:
                h = re.sub(r'(<nav class="tabs"[^>]*>.*?)</nav>', lambda m: m.group(1) + '<button data-f="紅葉">紅葉</button></nav>', h, count=1, flags=re.S)
        open(f, "w", encoding="utf-8").write(dress(h, False, "/" + slug))


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
