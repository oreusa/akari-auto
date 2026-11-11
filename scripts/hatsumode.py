"""関東の初詣ページ（site/hatsumode.html）を作る。11/11 月（関西 /hatsumode と同じ中身の形。オーナー 11/9 OK の形を関東へ）。
形は関東の紅葉ページ（site/koyo.html、scripts/koyo.py が先に作る）を借りて、中身だけ入れ替える。
データは data/hatsumode.tsv（各寺社の公式ページで確かめた事だけ。2027年の案内が出たら書き換えて「2027年」にする）。
使い方: python3 scripts/hatsumode.py   （page.yml で koyo.py のあとに動かす。失敗してもHPは出す）"""
import html, json, os, re, sys, urllib.parse
from datetime import datetime, timezone, timedelta

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SITE = os.path.join(ROOT, "site")
BASE = "https://lifenote-kanto.pages.dev/"
PREFS = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"]
E = html.escape
fu = lambda p: p + ("都" if p == "東京" else "県")


def main():
    now = datetime.now(timezone(timedelta(hours=9)))
    s = open(os.path.join(SITE, "koyo.html"), encoding="utf-8").read()
    if not os.path.exists(os.path.join(ROOT, "data", "hatsumode.tsv")):
        print("hatsumode: data/hatsumode.tsv がまだ無いので作らない"); return
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(ROOT, "data", "hatsumode.tsv"), encoding="utf-8") if l.strip() and not l.startswith("#")]
    rows = [r for r in rows if len(r) == 7]
    secs = ""; places = []
    for p in PREFS:
        rs = [r for r in rows if r[0] == p]
        if not rs:
            continue
        cs = ""
        for _, n, city, tm, tr, yr, url in rs:
            tag = '<span class="st now">2027年の案内</span>' if yr == "2027年" else f'<span class="st tba">{"昨年" if yr == "昨年" else "例年"}の案内</span>'
            kv = f'<span class="kv"><span>時間</span>{E(tm)}</span>' + (f'<span class="kv"><span>交通</span>{E(tr)}</span>' if tr not in ("", "—") else "")
            gm = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(f"{n} {fu(p)}{city}")
            cs += (f'<li class="it" data-p="{p}"><div class="cw"><a class="cd" href="{E(url)}" target="_blank" rel="noopener" data-k="初詣｜{E(n)}">'
                   f'<span class="bd">{tag}</span><span class="nm">{E(n)}</span><span class="pl">{E(city)}</span>{kv}<span class="ar">→</span></a>'
                   f'<a class="mp" href="{E(gm)}" target="_blank" rel="noopener">地図</a></div></li>')
            places.append((p, n, city, tm, yr, url))
        secs += f'<section class="ps" data-p="{p}"><h2>{fu(p)}の初詣<b class="c">{len(rs)}か所</b></h2><ul>{cs}</ul></section>'
    N = len(places)
    if N < 5:
        print("hatsumode: データが5か所より少ないので作らない", N); return
    n27 = sum(1 for x in places if x[4] == "2027年")
    names = "・".join(x[1] for x in places[:4])
    title = f"関東の初詣2027｜大晦日・三が日の時間と交通規制（{N}か所）"
    desc = (f"関東（東京・神奈川・埼玉・千葉・茨城・栃木・群馬）の初詣{N}か所の、大晦日と三が日の参拝時間・交通規制・駐車場を、"
            f"各寺社の公式ページからまとめました。{names}など。{now.year}年{now.month}月{now.day}日更新。")
    qa = []
    yo = [x for x in places if re.search(r"夜通し|24時間|終夜|終日", x[3])]
    if yo:
        qa.append(("大晦日の夜中にお参りできる関東の寺社は？", "、".join(f"{x[1]}（{x[3].split('。')[0]}）" for x in yo) + "です。各寺社の公式ページの案内です。"))
    qa.append(("2027年の時間はもう決まっていますか？", (f"{n27}か所は2027年の案内が出ています。" if n27 else "") + "ほかは昨年・例年の案内です。新しい案内が出たら書き換えます。お出かけ前に公式ページをご確認ください。"))
    faq = '<section class="faq"><h2>よくある質問</h2>' + "".join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in qa) + "</section>"
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "関東の初詣2027", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {"@type": "Place", "name": x[1], "address": fu(x[0]) + x[2], "url": x[5]}} for i, x in enumerate(places)]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "関東おでかけリスト", "item": BASE + "odekake"}, {"@type": "ListItem", "position": 2, "name": "関東の初詣2027", "item": BASE + "hatsumode"}]}]
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', "", s, flags=re.S)
    s = s.replace("</head>", "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld) + "</head>", 1)
    s = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", s, count=1)
    for k in ('name="description"', 'property="og:description"'):
        s = re.sub(rf'(<meta {k} content=")[^"]*', lambda m: m.group(1) + E(desc), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(title), s, count=1)
    s = re.sub(r'(<meta property="article:modified_time" content=")[^"]*', lambda m: m.group(1) + now.strftime("%Y-%m-%dT%H:%M:00+09:00"), s, count=1)
    s = re.sub(r'(<link rel="canonical" href="[^"]*?/)koyo"', r'\1hatsumode"', s, count=1)
    s = re.sub(r'(<meta property="og:url" content="[^"]*?/)koyo"', r'\1hatsumode"', s, count=1)
    s = re.sub(r'<p class="en">[^<]*</p>', '<p class="en">KANTO HATSUMODE</p>', s, count=1)
    s = re.sub(r"<h1>.*?</h1>", "<h1>関東の初詣<small>2027 大晦日・三が日の時間と交通規制</small></h1>", s, count=1, flags=re.S)
    s = re.sub(r'<p class="lead">.*?</p>', f'<p class="lead">東京・神奈川・埼玉・千葉・茨城・栃木・群馬の{N}か所の、<br>大晦日と三が日の時間・交通規制をまとめました。</p>', s, count=1, flags=re.S)
    s = re.sub(r'<p class="up">.*?</p>', f'<p class="up">{now.year}年{now.month}月{now.day}日 更新</p>', s, count=1, flags=re.S)
    s = re.sub(r'<nav class="sw".*?</nav>', "", s, count=1, flags=re.S)
    s = re.sub(r'<div class="tnb">.*?</div>', "", s, count=1, flags=re.S)
    have = {x[0] for x in places}
    for p in PREFS:
        if p not in have:
            s = s.replace(f'<button data-f="{p}">{p}</button>', "", 1)
    a = s.index("<main>") + len("<main>"); b = s.index('<section class="faq">'); e = s.index("</section>", b) + len("</section>")
    s = s[:a] + secs + '<p class="none" hidden>この都県の初詣は、まだのせていません。</p>' + faq + s[e:]
    f0 = s.index('<footer class="foot">'); f1 = s.index('<nav class="pn"', f0); f2 = s.index("</nav>", f1) + len("</nav>")
    s = (s[:f0] + '<footer class="foot">\n<p>時間・交通規制・駐車場は、各寺社の公式ページの案内をのせています。2027年の案内が出ていない所は、昨年・例年の内容です。'
         '名前を押すと公式のページ、「地図」を押すと場所が開きます。お出かけ前にリンク先でご確認ください。</p>\n'
         '<nav class="pn" aria-label="ほかのページ"><p class="pnh">あわせて見る</p><a href="illumination">関東のイルミネーション</a><a href="tomari">泊まりで行く所</a><a href="ima">今から行ける所</a></nav>' + s[f2:])
    s = s.replace("紅葉ライトアップ", "初詣").replace("koyo-pref", "hatsu-pref")
    for bad in ("今夜やって", "AUTUMN", "紅葉", "近くの宿"):
        if bad in s[s.index("<body"):]:
            print("hatsumode: 紅葉ページの言葉が残っている →", bad, "（作らない）"); return
    open(os.path.join(SITE, "hatsumode.html"), "w", encoding="utf-8").write(s)
    print("hatsumode", N, "places")


if __name__ == "__main__":
    main()
