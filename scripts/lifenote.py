"""燈のHPを LIFE NOTE（ライフノート）の形にする（11/2 オーナー「燈のhpを LIFE NOTE を作る。関東おでかけリスト・おかいものリスト 完全に分ける。
おでかけの方はお泊まりは月のと同様につける。その他は完全に TOWN NOTE 仕様にする」）。

page.yml の最後（公開の前）に毎回動かす。それまでの係が作った site/index.html（おでかけと買い物が1枚に入った物）を3つに分ける。
  /          … LIFE NOTE の入口（scripts/lifenote_top.py が作る。関東の絵地図・あなたの街・2つのリスト）
  /odekake   … 関東おでかけリスト（おでかけ・地図・いまから行ける・イルミ・近くの宿・泊まり）
  /okaimono  … くらべたおかいものリスト（いち押し・今だけのお得・比べた買い物・宿と予約・値下がり・1個あたり・ふるさと・買いまわり）
ほかのページの「戻る」も、おでかけ側は /odekake、買い物側は /okaimono へ。名前は「LIFE NOTE」（1冊のノート。TOWN NOTE と同じ）。
"""
import os, re, subprocess, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "site")
# 11/2 オーナー「3はB」→ アドレスは lifenote.pages.dev。page.yml が Cloudflare で決まった本当のアドレスを LIFE_BASE に入れる
# 11/2 lifenote.pages.dev はほかの人の物だった。決まるまでは今のアドレス（違うアドレスを canonical に書くと検索に出なくなる）
BASE = os.environ.get("LIFE_BASE") or "https://usagi-life-notes.pages.dev"
OLD = "https://usagi-life-notes.pages.dev"
# 全ページ共通の部品は、直したら番号を上げる（古い物が手元に残らないように）
VER = {"menu.js": 45, "v2sub.js": 17, "v2.js": 12, "night.js": 18}  # 11/9 night 18（夜の灰色の丸）・menu 38（家を売る前に）・v2sub 15・v2 9（cardmark 12：紅葉の名所の絵）。上げ忘れると古い版が残る ／ 11/7 関東不動産リスト：menu.js（不動産のメニュー・メールの相談）・v2sub.js（不動産の下のバー）・night.js（街のページの夜）


def rd(n):
    return open(os.path.join(S, n), encoding="utf-8").read()


def wr(n, h):
    open(os.path.join(S, n), "w", encoding="utf-8").write(h)


def cut(h, start_re):
    """start_re で始まる要素を、入れ子を数えて閉じタグまで丸ごと消す（全部）。"""
    while True:
        m = re.search(start_re, h)
        if not m:
            return h
        tag = re.match(r"<(\w+)", m.group(0)).group(1)
        i, depth = m.end(), 1
        op, cl = re.compile(rf"<{tag}\b"), f"</{tag}>"
        while depth:
            j = h.find(cl, i)
            if j < 0:
                return h
            depth += len(op.findall(h, i, j)) - 1
            i = j + len(cl)
        h = h[:m.start()] + h[i:]


def brand(h):
    h = h.replace(OLD, BASE)
    for f, v in VER.items():
        h = re.sub(rf'(["/])assets/{re.escape(f)}\?v=\d+', rf"\g<1>assets/{f}?v={v}", h)
    h = h.replace("うさぎ│LIFE NOTES", "LIFE NOTE").replace("USAGI LIFE NOTES", "LIFE NOTE").replace("LIFE NOTES", "LIFE NOTE")
    return h


def meta(h, title, desc, path):
    h = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", h, count=1)
    h = re.sub(r'(<meta name="description" content=")[^"]*', rf"\g<1>{desc}", h, count=1)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', rf"\g<1>{title}", h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*', rf"\g<1>{desc}", h, count=1)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*', rf"\g<1>{BASE}{path}", h, count=1)
    h = re.sub(r'<link rel="canonical"[^>]*>', "", h)
    return h.replace("</title>", f'</title><link rel="canonical" href="{BASE}{path}">', 1)


src = rd("index.html")
if 'id="lifenote-top"' in src:
    print("もう入口になっている（2回目）。分けずに終わる")
    sys.exit(0)
src = brand(src)
# 右上の小さな英字「LIFE NOTE」を押すと入口へ（TOWN NOTE と同じ）
src = src.replace('<div class="en">LIFE NOTE</div>', '<a class="en" href="/" style="display:block;color:inherit;text-decoration:none">LIFE NOTE</a>', 1)

# ---------- 関東おでかけリスト ----------
o = src
for r in [r'<section class="sbox" id="sale"', r'<nav class="cats"', r'<section class="blk hotb" id="hot"',
          r'<section class="blk" id="deal"', r'<section class="blk" id="trip"', r'<section class="blk" id="shop"', r'<a class="tnx']:
    o = cut(o, r)
# 買い物の楽天ROOMは、おかいものリスト側だけ（完全に分ける）
o = cut(o, r'<a class="co" data-en="RAKUTEN ROOM"')
o = re.sub(r'<p class="sub">.*?</p>', '<p class="sub">関東の今日から・新しく・無料で行ける場所を、<br>公式ページつきで、毎日のせています</p>', o, count=1, flags=re.S)
o = re.sub(r'<p class="pr-note">.*?</p>',
           '<p class="pr-note">このページには楽天トラベルの広告（PR）があります（近くの宿）。<br>泊まる前に、楽天トラベルのページで最新の情報を確かめてください。<br><a href="/privacy">プライバシーポリシーと広告について</a></p>', o, count=1, flags=re.S)
o = re.sub(r'<p class="ft">.*?</p>', '<p class="ft">LIFE NOTE│過去のおでかけも、このページに残していきます</p>'
           '<a class="tnx" href="/okaimono" data-k="下の入口｜おかいものリスト"><small>関連サイト</small><b>くらべたおかいものリスト<span>→</span></b><i>1個あたりで比べた、いちばん安い物</i></a>', o, count=1, flags=re.S)
# 11/2 検索結果に日付が出るように、日付のあるおでかけを schema.org の Event に（見た目は変えない）
def events_ld(h):
    import json, urllib.parse
    ev = []
    for m in re.finditer(r'<div class="card it" data-pref="([^"]+)"[^>]*?data-e="(\d{4}-\d\d-\d\d)" data-s="(\d{4}-\d\d-\d\d)"[^>]*>(.*?)<svg class="arw"', h, re.S):
        pref, e, st, body = m.groups()
        a = re.search(r'<a class="go" href="([^"]+)"[^>]*>(.*?)</a>', body, re.S)
        if not a:
            continue
        name = re.sub(r"<[^>]+>", " ", a.group(2))
        name = re.sub(r"\s+", " ", name).strip()
        q = re.search(r'query=([^"&]+)', body)
        place = urllib.parse.unquote(q.group(1)).replace("+", " ").strip() if q else ""
        place = re.sub(r"\s*" + re.escape(pref) + r"$", "", place) or pref
        ev.append({"@type": "Event", "name": name, "startDate": st, "endDate": e,
                   "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "eventStatus": "https://schema.org/EventScheduled",
                   "location": {"@type": "Place", "name": place, "address": {"@type": "PostalAddress", "addressRegion": pref + ("都" if pref == "東京" else "県"), "addressCountry": "JP"}},
                   "url": a.group(1).replace("&amp;", "&")})
    if not ev:
        return h
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "関東おでかけリスト",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": x} for i, x in enumerate(ev[:60])]}
    tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>"
    return h.replace("</head>", tag + "</head>", 1)


o = events_ld(o)
import datetime as _dt  # 11/9 mybest に倣い題に年月（毎日2回作るので月が変われば変わる）
_n = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9)))
o = meta(o, f"関東のおでかけ 今週末・今日行けるイベント一覧【{_n.year}年{_n.month}月】｜関東おでかけリスト",
         "東京・神奈川・埼玉・千葉・茨城・栃木・群馬で、今週末や今日から行けるイベント、新しいお店・施設を公式ページつきで毎日更新。無料の場所、地図、近くの宿も。", "/odekake")
wr("odekake.html", o)

# ---------- くらべたおかいものリスト ----------
# 11/2 オーナー「買い物のほうはもっと真剣に工夫しろ」→ 月の不動産リストと同じく、おでかけリストの作り（件数・タブ・しぼりこみ・カード・下のボタン列）を使い、
# 中のカードだけ買い物にする（scripts/okaimono.py）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okaimono
k = okaimono.build(o, src)
k = meta(k, "楽天の日用品を1個あたりで比較｜いちばん安い物がすぐ分かる くらべたおかいものリスト",
         "楽天の水・お米・トイレットペーパーなど毎日の物を、送料込みの1個あたりの値段に直して比べています。ふるさと納税1万円あたり、いまが買い時の物、セールも毎日更新。広告（PR）を含みます。", "/okaimono")
wr("okaimono.html", k)

# ---------- ほかのページの「戻る」とブランド ----------
REL = {
    "illumination": [("/koyo", "紅葉ライトアップ"), ("/tomari", "会場の近くの宿"), ("/ima", "今から行ける所"), ("/illumination", "関東イルミ一覧")],
    "ima": [("/illumination", "イルミネーション"), ("/koyo", "紅葉ライトアップ"), ("/tomari", "泊まりで行く所")],
    "tomari": [("/illumination", "イルミネーション"), ("/koyo", "紅葉ライトアップ"), ("/ima", "今から行ける所")],
    "tanka": [("/furusato", "ふるさと納税1万円あたり"), ("/nesage", "値下がりした物")],
    "furusato": [("/okaimono", "1個あたりでくらべる（最安とおすすめ）"), ("/nesage", "値下がりした物")],
    "nesage": [("/okaimono", "1個あたりでくらべる（最安とおすすめ）"), ("/kaimawari", "買いまわり1,000円")],
    "kaimawari": [("/nesage", "値下がりした物"), ("/okaimono", "1個あたりでくらべる（最安とおすすめ）")],
}
SHOP = {"nesage.html", "furusato.html", "tanka.html", "kaimawari.html"}
for n in os.listdir(S):
    if not n.endswith(".html") or n in ("index.html", "odekake.html", "okaimono.html"):
        continue
    h = rd(n)
    h2 = brand(h)
    if n in SHOP:
        h2 = h2.replace('<a class="back" href="./">関東おでかけリストを見る</a>', '<a class="back" href="/okaimono">くらべたおかいものリストを見る</a>')
    else:
        h2 = re.sub(r'<a class="back" href="(?:\./|/)">関東おでかけリスト(を見る|へ戻る)</a>', r'<a class="back" href="/odekake">関東おでかけリスト\1</a>', h2)
    # 古い見本・試作の行き先（/ に送っていた物）はおでかけリストへ
    h2 = h2.replace('content="0;url=/"><link rel="canonical" href="/">', 'content="0;url=/odekake"><link rel="canonical" href="/odekake">').replace('location.replace("/")', 'location.replace("/odekake")')
    # 11/2 検索用：中身の近いページどうしをつなぐ（「戻る」の下に小さく1行。見た目は今の文字の色と大きさのまま）
    rel = REL.get("illumination" if n.startswith("illumination") else n[:-5])
    if rel and 'class="rel"' not in h2:
        row = "".join(f'<a href="{u}" style="color:inherit;white-space:nowrap;margin:0 8px">{t}</a>' for u, t in rel if u != "/" + n[:-5])
        h2 = re.sub(r'(<a class="back"[^>]*>[^<]*</a>)', r'\1' + f'<p class="rel" style="text-align:center;font-size:12px;line-height:2;color:#8C7B6E;margin:16px 0 0;padding:0;background:none;border:0">あわせて見る<br>{row}</p>', h2, count=1)
    if h2 != h:
        wr(n, h2)
# ---------- 検索用：1ページに1つ、探される言葉を題と説明に（11/2 オーナー OK「どのページもヒットさせたい」。見た目は変えない）
SEO = {
    "ima.html": ("今から行ける関東のおでかけ｜近い順・今日開いている所と天気", None, "/ima"),
    "tomari.html": ("泊まりで行く関東のおでかけ｜イベント会場の近くの宿｜LIFE NOTE", None, "/tomari"),
    # 買う直前の人が打つ言葉（11/2 オーナー OK「アフェリエイトの方も検索で出やすく」）
    "furusato.html": ("ふるさと納税 お米1万円で何kg？トイレットペーパー・水も寄付1万円あたりで比較｜LIFE NOTE", None, "/furusato"),
    "tanka.html": ("トイレットペーパー・水・お米 1個あたりいちばん安いのは？楽天を送料込みで比較｜LIFE NOTE", None, "/tanka"),
    "kaimawari.html": ("楽天お買い物マラソン 買いまわり1,000円ぽっきり おすすめ（送料込み・レビュー1,000件以上）｜LIFE NOTE", None, "/kaimawari"),
    "nesage.html": ("いまが買い時の日用品｜毎日の値段を記録して比較｜LIFE NOTE",
                    "楽天のよく買われる毎日の物の値段を毎日記録して、ふだんの値段より安くなった物だけを並べます。お買い物マラソン・ブラックフライデーの前に。", "/nesage"),
}
for n, (t, d, path) in SEO.items():
    f = os.path.join(S, n)
    if not os.path.exists(f):
        continue
    h = rd(n)
    if d is None:
        d = (re.search(r'<meta name="description" content="([^"]*)"', h) or [None, ""])[1]
    if 'property="og:title"' not in h:
        h = h.replace("</title>", '</title><meta property="og:title" content="">', 1)
    wr(n, meta(h, t, d, path))

tn = os.path.join(S, "townnotes", "index.html")
if os.path.exists(tn):
    t = open(tn, encoding="utf-8").read().replace('url=/"', 'url=/odekake"').replace('href="/"', 'href="/odekake"').replace('location.replace("/")', 'location.replace("/odekake")')
    open(tn, "w", encoding="utf-8").write(t)

# ---------- 検索用：sitemap に2つのリストを足す ----------
for n in ("sitemap.xml", "robots.txt"):
    f = os.path.join(S, n)
    if os.path.exists(f):
        t = open(f, encoding="utf-8").read()  # 先に読む（"w" で開くと中身が消える）
        open(f, "w", encoding="utf-8").write(t.replace(OLD, BASE))
sm = os.path.join(S, "sitemap.xml")
if os.path.exists(sm):
    x = open(sm, encoding="utf-8").read()
    add = "".join(f"<url><loc>{BASE}{p}</loc></url>" for p in ("/odekake", "/okaimono", "/nesage", "/privacy") if f"{BASE}{p}<" not in x)
    if add:
        open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", add + "</urlset>", 1))

# ---------- 入口 ----------
subprocess.run([sys.executable, os.path.join(R, "scripts", "lifenote_top.py")], check=True)
# 11/10 表紙 v3（1つの地図で4つのノート。月の TOWN NOTE と同じ）
subprocess.run([sys.executable, os.path.join(R, "scripts", "cover_kanto.py")])
print("LIFE NOTE: / ・ /odekake", len(o), "・ /okaimono", len(k))
