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
BASE = os.environ.get("LIFE_BASE") or "https://lifenote.pages.dev"
OLD = "https://usagi-life-notes.pages.dev"
# 全ページ共通の部品は、直したら番号を上げる（古い物が手元に残らないように）
VER = {"menu.js": 8, "v2sub.js": 6, "v2.js": 4, "night.js": 5}


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
        h = re.sub(rf'/assets/{re.escape(f)}\?v=\d+', f"/assets/{f}?v={v}", h)
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
           '<p class="pr-note">このページには楽天トラベルの広告（PR）があります（近くの宿）。<br>泊まる前に、楽天トラベルのページで最新の情報を確かめてください。</p>', o, count=1, flags=re.S)
o = re.sub(r'<p class="ft">.*?</p>', '<p class="ft">LIFE NOTE│過去のおでかけも、このページに残していきます</p>'
           '<a class="tnx" href="/okaimono" data-k="下の入口｜おかいものリスト"><small>関連サイト</small><b>くらべたおかいものリスト<span>→</span></b><i>うさぎが数字で比べた物と、本当に安い物</i></a>', o, count=1, flags=re.S)
o = meta(o, "関東おでかけリスト｜LIFE NOTE", "関東で、今日から・新しく・無料で行ける場所を、公式ページつきで毎日。地図・いまから行ける所・近くの宿も。", "/odekake")
wr("odekake.html", o)

# ---------- くらべたおかいものリスト ----------
# 11/2 オーナー「買い物のほうはもっと真剣に工夫しろ」→ 月の不動産リストと同じく、おでかけリストの作り（件数・タブ・しぼりこみ・カード・下のボタン列）を使い、
# 中のカードだけ買い物にする（scripts/okaimono.py）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okaimono
k = okaimono.build(o, src)
k = meta(k, "くらべたおかいものリスト｜LIFE NOTE", "うさぎが3つ以上を数字で比べて選んだ暮らしの物。1個あたり・ふるさと納税1万円あたり・本当に値下がりした物・セールも。広告（PR）を含みます。", "/okaimono")
wr("okaimono.html", k)

# ---------- ほかのページの「戻る」とブランド ----------
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
    if h2 != h:
        wr(n, h2)
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
    add = "".join(f"<url><loc>{BASE}{p}</loc></url>" for p in ("/odekake", "/okaimono") if f"{BASE}{p}<" not in x)
    if add:
        open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", add + "</urlset>", 1))

# ---------- 入口 ----------
subprocess.run([sys.executable, os.path.join(R, "scripts", "lifenote_top.py")], check=True)
print("LIFE NOTE: / ・ /odekake", len(o), "・ /okaimono", len(k))
