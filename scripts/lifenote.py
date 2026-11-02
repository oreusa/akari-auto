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
VER = {"menu.js": 7, "v2sub.js": 5, "v2.js": 3, "night.js": 4}


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
           '<a class="tnx" href="/okaimono" data-k="下の入口｜おかいものリスト"><small>PAGE 02</small><b>くらべたおかいものリスト<span>→</span></b><i>うさぎが数字で比べた物と、本当にお得な日</i></a>', o, count=1, flags=re.S)
o = meta(o, "関東おでかけリスト｜LIFE NOTE", "関東で、今日から・新しく・無料で行ける場所を、公式ページつきで毎日。地図・いまから行ける所・近くの宿も。", "/odekake")
wr("odekake.html", o)

# ---------- くらべたおかいものリスト ----------
k = src
for r in [r'<nav class="flt"', r'<p class="cnt"', r'<section class="blk" id="odekake"', r'<section class="blk arch" id="archive"',
          r'<a class="ilk"']:
    k = cut(k, r)
k = cut(k, r'<a class="co" data-en="LISTING"')
k = cut(k, r'<a class="tnx')
k = re.sub(r'<script src="/townnotes/map\.js[^"]*"[^>]*></script>', "", k)
k = re.sub(r'<script src="/assets/v2\.js[^"]*"></script>', "", k)
k = re.sub(r'<script src="/assets/top2\.js[^"]*"></script>', '<script src="/assets/v2sub.js?v=5" defer></script>', k)
k = re.sub(r'<h1 class="ttl">.*?</h1>', '<h1 class="ttl">くらべたおかいものリスト</h1>', k, count=1, flags=re.S)
k = re.sub(r'<p class="sub">.*?</p>', '<p class="sub">うさぎが3つ以上を数字で比べて選んだ物と、<br>本当にお得な日を、毎日のせています</p>', k, count=1, flags=re.S)
# いち押しは「おでかけ」の欄に入っていたので、買い物の最初の欄にする
k = re.sub(r'<button type="button" class="on" data-v="odekake">.*?</button>', "", k, count=1, flags=re.S)
k = k.replace('id="hot" data-v="odekake"', 'id="hot" data-v="pick"')
n_hot = 1 if 'id="hot"' in k else 0
k = re.sub(r'<nav class="cats" id="cats" aria-label="項目">',
           '<nav class="cats" id="cats" aria-label="項目">' + ('<button type="button" class="on" data-v="pick">いち押し<small>1</small></button>' if n_hot else ''), k, count=1)
first = "pick" if n_hot else (re.search(r'id="cats"[^>]*><button type="button" data-v="(\w+)"', k) or [None, "deal"])[1]
if not n_hot:
    k = k.replace(f'<button type="button" data-v="{first}">', f'<button type="button" class="on" data-v="{first}">', 1)
k = k.replace('e.hidden=e.dataset.v!=="odekake";', f'e.hidden=e.dataset.v!=="{first}";')
QK = ('<nav class="qk q4" aria-label="さがし方">'
      '<a href="/nesage" data-k="入口｜値下がり"><svg viewBox="0 0 24 24"><path d="M4 6l6 6 4-4 6 6"/><path d="M20 10v4h-4"/></svg><b>値下がり</b><small>本当に下がった物</small></a>'
      '<a href="/tanka" data-k="入口｜1個あたり"><svg viewBox="0 0 24 24"><path d="M12 4v16M6 8h12M6 8l-3 6h6zM18 8l-3 6h6z"/></svg><b>1個あたり</b><small>1Lあたり・1kgあたり</small></a>'
      '<a href="/furusato" data-k="入口｜ふるさと"><svg viewBox="0 0 24 24"><rect x="4" y="9" width="16" height="11" rx="1.5"/><path d="M12 9v11M4 13h16M12 9c-2-4-6-4-6-1.5S10 9 12 9zm0 0c2-4 6-4 6-1.5S14 9 12 9z"/></svg><b>ふるさと納税</b><small>1万円あたりの量</small></a>'
      '<a href="/kaimawari" data-k="入口｜買いまわり"><svg viewBox="0 0 24 24"><path d="M5 7h14l-1.5 9h-11z"/><circle cx="9" cy="19.5" r="1.2"/><circle cx="16" cy="19.5" r="1.2"/><path d="M8 7l1.5-3M16 7l-1.5-3"/></svg><b>買いまわり</b><small>1,000円ぽっきり</small></a>'
      '</nav>')
k = k.replace("</header>", "</header>" + QK, 1)
k = k.replace("</head>", "<style>html.top2 .qk.q4{grid-template-columns:repeat(2,1fr)}html.top2 .qk.q4 a{flex-direction:row;justify-content:flex-start;gap:10px;padding:12px 12px;text-align:left}"
              "html.top2 .qk.q4 a span{display:flex;flex-direction:column}html.top2 .qk.q4 small{text-align:left}"
              ".wrap>.sbox{margin-top:0}.head .ttl{font-size:26px;letter-spacing:.06em}</style></head>", 1)
k = re.sub(r'<p class="ft">.*?</p>', '<p class="ft">LIFE NOTE│リンクは広告（PR）です。買う前に、お店のページで最新の情報を確かめてください</p>'
           '<a class="tnx" href="/odekake" data-k="下の入口｜おでかけリスト"><small>PAGE 01</small><b>関東おでかけリスト<span>→</span></b><i>開催中・これからのおでかけを、公式ページつきで</i></a>', k, count=1, flags=re.S)
k = meta(k, "くらべたおかいものリスト｜LIFE NOTE", "うさぎが3つ以上を数字で比べて選んだ暮らしの物と、楽天のセール・ポイントアップの日。本当に値下がりした物、1個あたり、ふるさと納税も。広告（PR）を含みます。", "/okaimono")
# 4つの入口の中の文字は2行に（アイコンの右）
k = re.sub(r'(<nav class="qk q4".*?</nav>)', lambda m: re.sub(r"(<b>.*?</small>)", r"<span>\1</span>", m.group(1)), k, count=1, flags=re.S)
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
