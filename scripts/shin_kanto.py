"""11/19 owner「全部！」「他ページもぜんぶ変えれたら教えて」→ 関東（LIFE NOTE）の表紙・おでかけ・都県のおでかけも、関西（TOWN NOTE）と同じ新しい土台で作る。
土台（site/shin/shin.css・shin.js・odekake.js・cover.js・list.js）は月の repo（usagi-fudosan-media links/shin）の写し。地域の違いは CFG.reg（名前・都県・色・地図・ロゴ）。
中身：data/page-spots.json（HPに載せるおでかけ）。公開の回（page.yml）では、リンクの確かめを通った物（site/odekake.html に載った物）だけにする。
写真：site/assets/mihon.json・phh.json。地図の場所：data/townnotes-geo.json。種類：site/assets/cardmark.js。
出す所：site/index.html・site/odekake.html・site/odekake-<都県>.html を新しい形に書き替える（前の物は site/kyu/ に残す）。
page.yml の最後の方（投稿の画像を撮った後・skin_bake の前）で動かす。python3 scripts/shin_kanto.py"""
import os, re, sys, json, html, hashlib, datetime, shutil

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "site")
SITE = "https://kanto.townnote.app"
TPL = open(os.path.join(R, "scripts", "shin", "page.tpl.html"), encoding="utf-8").read()
JST = datetime.timezone(datetime.timedelta(hours=9))
TD = datetime.datetime.now(JST).date().isoformat()
J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
ver = lambda f: hashlib.sha1(open(os.path.join(S, "shin", f), "rb").read()).hexdigest()[:8]
rd = lambda *p: json.load(open(os.path.join(R, *p), encoding="utf-8"))

PREF = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"]
FULL = {"東京": "東京都", "神奈川": "神奈川県", "埼玉": "埼玉県", "千葉": "千葉県", "茨城": "茨城県", "栃木": "栃木県", "群馬": "群馬県"}
SLUG = {"東京": "tokyo", "神奈川": "kanagawa", "埼玉": "saitama", "千葉": "chiba", "茨城": "ibaraki", "栃木": "tochigi", "群馬": "gunma"}
PC = {"東京": "#D9775A", "神奈川": "#4F86C6", "埼玉": "#E09A3E", "千葉": "#3FA3B5", "茨城": "#5FA06A", "栃木": "#9C7BB8", "群馬": "#C2557A"}
FL = {"東京": "#F7D9CC", "神奈川": "#D6E4F5", "埼玉": "#F8E4C4", "千葉": "#D0EBEF", "茨城": "#D8ECD4", "栃木": "#E6DBF1", "群馬": "#F6DCE6"}


# 地図：関西と同じ枠（viewBox 10 15 200 250）に関東が収まるように
def proj(lon, lat): return ((lon - 138.4) * 81 + 10, (37.15 - lat) * 100 + 27)
LBLL = {"群馬": (138.95, 36.62), "栃木": (139.75, 36.72), "茨城": (140.3, 36.3), "埼玉": (139.3, 36.02), "東京": (139.4, 35.72), "神奈川": (139.3, 35.43), "千葉": (140.2, 35.55)}
LB = {p: [round(proj(*v)[0], 1), round(proj(*v)[1], 1)] for p, v in LBLL.items()}
REG = {"n": "関東", "brand": "LIFE NOTE", "logo": "/logo-s.png", "logon": "/logo-s-night.png", "pref": PREF, "pfs": "東京・神奈川・埼玉・千葉・茨城・栃木・群馬",
       "pc": PC, "fl": FL, "lb": LB, "sl": SLUG, "vb": "10 15 200 250",
       "org": [["東京駅", 35.6812, 139.7671], ["新宿", 35.6896, 139.7006], ["渋谷", 35.658, 139.7016], ["横浜", 35.4658, 139.6223], ["大宮", 35.9064, 139.6238], ["千葉駅", 35.613, 140.1135], ["水戸駅", 36.3708, 140.4763], ["宇都宮駅", 36.559, 139.8985], ["高崎駅", 36.3228, 139.0127]]}


def path(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poly in polys:
        for ring in poly:
            s, last = [], None
            for c in ring:
                x, y = proj(c[0], c[1]); p = (round(x, 1), round(y, 1))
                if p != last: s.append(p); last = p
            if len(s) >= 4: out.append("M" + "L".join(f"{x:g} {y:g}" for x, y in s) + "Z")
    return "".join(out)


kj = rd("site", "townnotes", "kanto.json")
MAP = {"pref": {f["properties"]["p"]: path(f["geometry"]) for f in kj["pref"]["features"]}, "nb": [path(f["geometry"]) for f in kj["nb"]["features"]]}

# 種類（関西と同じ cardmark.js の決まり）
cm = open(os.path.join(S, "assets", "cardmark.js"), encoding="utf-8").read()
ICONS = dict(re.findall(r"^(\w+):'(<[^']+)',?$", cm[cm.find("var I={"):cm.find("};", cm.find("var I={"))], re.M))
RULES = re.findall(r"\[/(.+?)/(i?),'(\w+)'\]", cm[cm.find("var R=["):cm.find("var PCM")])
def kind(*txt):
    for t in txt:
        for pat, fl, k in RULES:
            if re.search(pat.replace("\\/", "/"), t or "", re.I if fl else 0): return k
    return "spot"


# 種類の名前と色（関西 tools/shin/lists.py の cfg_kinds と同じ）
KG = {"art": ["アート・展示", "#3B5BA5"], "light": ["光・イルミ", "#B7862A"], "koyo": ["紅葉", "#C0532B"], "flower": ["花", "#C2557A"], "fes": ["まつり", "#B23A2E"],
      "quest": ["謎とき", "#5B4B8A"], "play": ["あそぶ", "#2E8B6E"], "spot": ["スポット", "#2F7D9A"], "food": ["グルメ", "#C9702A"], "animal": ["いきもの", "#6F7F33"],
      "xmas": ["クリスマス", "#2F7A4F"], "hallo": ["ハロウィン", "#B45F1F"], "shop": ["マーケット", "#8A6A3F"]}
KINDS = lambda its: {k: v for k, v in KG.items() if any(x.get("k") == k for x in its)}
norm = lambda s: re.sub(r"[\s　・／/「」『』]", "", s or "")


def items():
    sp = rd("data", "page-spots.json")["items"]
    mh = rd("site", "assets", "mihon.json") if os.path.exists(os.path.join(S, "assets", "mihon.json")) else {}
    phh = rd("site", "assets", "phh.json") if os.path.exists(os.path.join(S, "assets", "phh.json")) else {}
    geo = rd("data", "townnotes-geo.json")
    byn = {norm(v.get("n")): v for v in mh.values()}
    byu = {}
    for v in mh.values(): byu.setdefault(v.get("u"), v)
    # 公開の回はリンクの確かめを通った物だけ（site/odekake.html に載った公式リンク）
    live = set()
    op = os.path.join(S, "odekake.html")
    if os.path.exists(op):
        src = open(op, encoding="utf-8").read()
        if "/shin/shin.css" not in src:
            live = {html.unescape(u) for u in re.findall(r'<a class="go" href="([^"]+)"', src)}
    opages = {f[:-5] for f in os.listdir(os.path.join(S, "o"))} if os.path.isdir(os.path.join(S, "o")) else set()
    def enrich(it, name, pl):
        v = byn.get(norm(name)) or byu.get(it.get("u")) or {}
        for k in ("im", "cr", "cu", "hk"):
            if v.get(k) and k not in it: it[k] = v[k]
        if v.get("vn") and not it.get("v"): it["v"] = v["vn"]
        if it.get("im") in phh: it["th"] = phh[it["im"]]
        g = None
        if pl:
            g = geo.get(f"{it['p']}｜{pl} {it['p']}") or next((gv for gk, gv in geo.items() if gk.startswith(f"{it['p']}｜{pl}")), None)
        if g and g[0] is not None:
            X, Y = proj(g[1], g[0]); it["xy"] = [round(X, 2), round(Y, 2)]
        return it
    global ENRICH; ENRICH = enrich
    out, seen = [], set()
    for x in sp:
        p, t, u = x.get("pref"), (x.get("title") or "").strip(), x.get("url", "")
        e, s = (x.get("ends") or "")[:10], (x.get("start") or "")[:10]
        if p not in FULL or not t or not e or e < TD: continue
        if s and (datetime.date.fromisoformat(s) - datetime.date.fromisoformat(TD)).days > 14: continue
        if len(live) >= 5 and u not in live: continue
        key = re.sub(r"\s+", "", t)
        if key in seen: continue
        seen.add(key)
        it = {"t": t, "u": u, "p": p, "s": s or TD, "e": e, "a": x.get("place", ""), "v": x.get("place", ""), "k": kind(t, x.get("note", ""))}
        if x.get("free"): it["f"] = 1
        if x.get("note"): it["ds"] = x["note"]
        if x.get("opennote"): it["h"] = x["opennote"]
        enrich(it, t, x.get("place", ""))
        oid = hashlib.md5(key.encode()).hexdigest()[:8]
        if oid in opages: it["o"] = oid
        out.append(it)
    print("shin_kanto items", len(out), "photos", sum("im" in i for i in out), "map", sum("xy" in i for i in out), "live", len(live))
    return out


REL = [["おでかけ", "/odekake"], ["家と土地", "/fudosan-list"], ["おかいもの", "/okaimono"], ["トップへ", "/"]]


def write(fname, url, title, cfg, data, js, desc):
    cfg["reg"] = REG
    cfg["menu"]["rel"] = [r for r in REL if r[1] != url]
    head = (f'<meta name="description" content="{html.escape(desc)}">' +
            f'<link rel="canonical" href="{SITE}{url}"><meta property="og:title" content="{html.escape(title.split("｜")[0])}">'
            f'<meta property="og:image" content="{SITE}/og-v10.png"><meta property="og:url" content="{SITE}{url}">')
    page = (TPL.replace("__TITLE__", html.escape(title)).replace("__HEAD__", head).replace("__CFG__", J(cfg)).replace("__DATA__", J(data))
            .replace("__CV__", ver("shin.css")).replace("__JV__", ver("shin.js")).replace("__PAGE__", js).replace("__PV__", ver(js + ".js")))
    dst = os.path.join(S, fname)
    if os.path.exists(dst):
        old = open(dst, encoding="utf-8").read()
        if "/shin/shin.css" not in old:
            os.makedirs(os.path.join(S, "kyu"), exist_ok=True)
            open(os.path.join(S, "kyu", fname), "w", encoding="utf-8").write(old)
    open(dst, "w", encoding="utf-8").write(page)
    print(fname, len(page) // 1024, "KB")


# ---------- 読む・入れるページ（売る前に・いくら？）11/19 23時 owner「その他も本気でやり直せ」：頭のかぶせをやめ、中身を新しい部品（doc.js の .dc）に書き直す ----------
def acc(rows):
    return "".join(f'<details><summary>{q}</summary><div class="ddd">{a}</div></details>' for q, a in rows)


def old_doc(fname):
    """前のページ（site/kyu/ に残した物があればそれ）から 題・説明・中身・計算の script を取り出して、新しい部品の名前に直す"""
    src = os.path.join(S, "kyu", fname) if os.path.exists(os.path.join(S, "kyu", fname)) else os.path.join(S, fname)
    t = open(src, encoding="utf-8").read()
    if "/shin/shin.css" in t: return None
    b = t[t.index("<body"):]
    js = "\n".join(m.group(1) for m in re.finditer(r"<script>(.*?)</script>", b, re.S))
    b = re.sub(r"<script.*?</script>", "", b, flags=re.S)
    h1 = re.sub(r"<span>.*?</span>", "", re.search(r"<h1>(.*?)</h1>", b, re.S).group(1)).strip()
    sub = (re.search(r'<p class="(?:s3l|sub)">(.*?)</p>', b, re.S) or [None, ""])[1].replace("<br>", "")
    return t, b, h1, sub, js


def doc_uru():
    r = old_doc("uru.html")
    if not r: return None
    t, b, h1, sub, js = r
    secs = re.findall(r'<section class="s3">(.*?)</section>', b, re.S)
    out = []
    for i, sc in enumerate(secs):
        sc = re.sub(r'<div class="sn">STEP 0?(\d+)</div>', r'<span class="dno">\1</span>', sc)
        if "<details" in sc:
            det = re.findall(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", sc, re.S)
            know = [d for d in det if not re.sub("<[^>]+>", "", d[0]).strip().endswith("？")]
            faq = [d for d in det if re.sub("<[^>]+>", "", d[0]).strip().endswith("？")]
            hd = sc[:sc.index('<div class="acc">')] if '<div class="acc">' in sc else sc[:sc.index("<details")]
            out.append('<section class="dsec">' + hd + acc(know) + "</section>")
            if faq: out.append('<section class="dsec"><h2>よくある質問</h2>' + acc(faq) + "</section>")
            continue
        sc = sc.replace('<input id="tq"', '<input class="din" id="tq"').replace('class="b1"', 'class="dbtn"')
        sc = re.sub(r'<p style="margin:14px 0 0"><a href="/ikura"([^>]*) style="[^"]*">(.*?)→</a></p>', r'<a class="dbtn2" href="/ikura"\1>\2</a>', sc)
        out.append('<section class="dsec">' + sc + "</section>")
    pr = '<p class="dnote">このページのリンクの一部は広告（PR）です。</p>' if "広告（PR）" in b else ""
    rel = ('<section class="dsec"><h2>あわせて見る</h2><div class="drel"><a href="/fudosan-list">家と土地の相場<small>関東の街ごとの値段</small></a><a href="/jikka/">実家・空き家<small>売る・片付ける前に</small></a>'
           '<a href="/ikura">いくらで売れる？<small>30秒で目安</small></a><a href="/chika-kanto">地価ランキング<small>住宅地の1年の動き</small></a></div></section>')
    return {"h1": h1, "sub": re.sub(r"<[^>]+>", "", sub), "html": "".join(out) + pr + rel, "js": js}


def doc_ikura():
    r = old_doc("ikura.html")
    if not r: return None
    t, b, h1, sub, js = r
    card = re.search(r'<div class="card">(.*?)</div>\s*<div class="res"', b, re.S).group(1)
    res = b[b.index('<div class="res"'):b.index('<p class="note">')]
    note = re.search(r'<p class="note">(.*?)</p>', b, re.S).group(1)
    card = re.sub(r'<p class="q">0?(\d+)<b( id="al")?>(.*?)</b></p>', r'<p class="dq"><i>\1</i><b\2 style="font-weight:600">\3</b></p>', card)
    card = card.replace('class="step"', 'class="dstep"').replace('class="chips"', 'class="dchs"').replace('<select id="ci"', '<select class="din" id="ci"')
    card = card.replace('class="row"', 'class="drow"').replace('<input id="ar"', '<input class="din" id="ar"').replace('class="hint"', 'class="dhint"')
    res = (res.replace('class="res"', 'class="dres"').replace('class="lb"', 'class="dlb"').replace('class="big"', 'class="dbig"').replace('class="go"', 'class="dbtn"')
           .replace('class="sm"', 'class="dhint"'))
    body = ('<section class="dsec">' + card + res + "</section>" + f'<p class="dnote">{note}</p><p class="dnote">このページのリンクの一部は広告（PR）です。</p>'
            '<section class="dsec"><h2>あわせて見る</h2><div class="drel"><a href="/uru">家を売る前に<small>3つの順で迷わない</small></a><a href="/fudosan-list">家と土地の相場<small>関東の街ごとの値段</small></a></div></section>')
    return {"h1": h1, "sub": re.sub(r"<[^>]+>", "", sub).replace("。", "。", 1), "html": body, "js": js}


HOME_NAV = [{"t": "街をさがす", "ic": "find", "href": "/fudosan-list"}, {"t": "ランキング", "ic": "rank", "href": "/chika-kanto"},
            {"t": "売りたい", "ic": "sell", "href": "/uru"}, {"t": "いくら？", "ic": "yen", "href": "/ikura"}]
HOME_MENU = [["家と土地の相場", "/fudosan-list"], ["地価ランキング", "/chika-kanto"], ["家を売る前に", "/uru"], ["いくらで売れる？", "/ikura"], ["実家・空き家", "/jikka/"], ["予算で街さがし", "/sagasu"], ["空き家の割合ランキング", "/akiya-ranking"]]


def home_cfg(cur):
    return {"nav": [dict(n, cur=1) if n["href"] == cur else n for n in HOME_NAV], "menu": {"k": "Home & Land", "items": [[t, u] + ([1] if u == cur else []) for t, u in HOME_MENU]},
            "foot": "数字はどれも国・都県などの公式の発表です。街の平均で、1軒ずつの値段ではありません。<br>このページのリンクの一部は広告（PR）です。"}


def docs():
    for fname, url, title, fn, desc in [
        ("uru.html", "/uru", "家を売る前に｜相場を見る・値段を聞く・大事なこと（関東）｜LIFE NOTE", doc_uru,
         "関東で家を売る前に、街の相場を見る・無料で値段を見る・知っておく大事なことを、3つの順でまとめました。"),
        ("ikura.html", "/ikura", "お家はいくらで売れる？｜関東の市区町村の地価公示から30秒で目安｜LIFE NOTE", doc_ikura,
         "関東の市区町村で、国の地価公示から、マンション・一戸建て・土地の売れそうな値段の目安を30秒で出します。無料・名前も要りません。")]:
        try:
            d = fn()
            if d: write(fname, url, title, home_cfg(url), d, "doc", desc)
        except Exception as e:
            print("shin_kanto: 前のまま", fname, repr(e))


def main():
    IT = items()
    if len(IT) < 10:
        print("shin_kanto: おでかけが少ないので書き替えない", len(IT)); return
    base = {"nav": [{"t": "開催中", "ic": "now", "a": "now"}, {"t": "今週末", "ic": "we", "a": "we"}, {"t": "地図", "ic": "map", "a": "map"}, {"t": "紅葉", "ic": "star", "href": "/koyo"}],
            "menu": {"k": "Odekake", "items": [["関東おでかけ", "/odekake"], ["イルミネーション", "/illumination"], ["紅葉", "/koyo"], ["いまから行ける", "/ima"], ["開店・閉店", "/kaiten"]]},
            "foot": "情報は各公式サイトで確かめてから出かけてください。写真の撮影者は各ページに書いています（ウィキメディア・コモンズ ほか）。<br>券・宿のリンクの一部は広告です。"}
    import copy
    def cfg(cur):
        c = copy.deepcopy(base)
        c["menu"]["items"] = [[t, u] + ([1] if u == cur else []) for t, u in c["menu"]["items"]]
        return c
    data = {"items": IT, "icons": ICONS, "map": MAP}
    ym = f"{TD[:4]}年{int(TD[5:7])}月"
    write("odekake.html", "/odekake", f"関東おでかけリスト【{ym}】｜開催中・今週末のイベント（東京・神奈川・埼玉・千葉・茨城・栃木・群馬）｜LIFE NOTE",
          cfg("/odekake"), data, "odekake",
          "東京・神奈川・埼玉・千葉・茨城・栃木・群馬のおでかけ・イベントを、開催中・今週末・まもなく終了に分けて、公式ページつきでまとめています。写真と地図で探せて、毎日更新しています。")
    for p in PREF:
        n = sum(1 for i in IT if i["p"] == p)
        if not n: continue
        d = dict(data); d["page"] = {"h1": f"{p}のおでかけ・イベント", "sub": f"{FULL[p]}・{n}件", "p": p}
        write(f"odekake-{SLUG[p]}.html", f"/odekake-{SLUG[p]}", f"{p}のおでかけ・イベント（{FULL[p]}）｜開催中・今週末｜LIFE NOTE", cfg("/odekake"), d, "odekake",
              f"{FULL[p]}のおでかけ・イベントを、開催中・今週末・まもなく終了に分けて、公式ページつきでまとめています。写真と地図で探せて、毎日更新しています。")
    # ---------- イルミネーション・紅葉（関西と同じ形） ----------
    il, ky = [], []
    for x in rd("data", "illumi.json")["items"]:
        e, s_ = (x.get("end") or "2027-03-31")[:10], (x.get("start") or "")[:10]
        if x.get("pref") not in FULL or not s_ or e < TD: continue
        it = {"t": x["name"], "u": x.get("url", ""), "p": x["pref"], "s": s_, "e": e, "a": x.get("city", ""), "v": x.get("venue", ""), "k": "light"}
        if x.get("free"): it["f"] = 1
        if x.get("hours"): it["h"] = x["hours"]
        if x.get("fee"): it["fe"] = x["fee"]
        il.append(ENRICH(it, x["name"], x.get("venue", "")))
    for x in rd("data", "koyo.json")["items"]:
        e, s_ = (x.get("end") or x.get("start") or "")[:10], (x.get("start") or "")[:10]
        if x.get("pref") not in FULL or not s_ or e < TD: continue
        it = {"t": x["name"], "u": x.get("url", ""), "p": x["pref"], "s": s_, "e": e, "a": x.get("city", ""), "v": x.get("venue", ""), "k": "koyo"}
        if x.get("hours"): it["h"] = x["hours"]
        if x.get("fee"): it["fe"] = x["fee"]
        if x.get("free") or (x.get("fee") or "").startswith("無料"): it["f"] = 1
        ky.append(ENRICH(it, x["name"], x.get("venue", "")))
    def prange(t):
        mm = re.findall(r"(\d+)月(上旬|初旬|中旬|下旬|末)", t or "")
        if not mm: return None
        today = datetime.date.fromisoformat(TD)
        def d(mo, k, end):
            mo = int(mo); y = today.year if mo >= 6 or today.month < 6 else today.year + 1
            a, b = {"上旬": (1, 10), "初旬": (1, 10), "中旬": (11, 20), "下旬": (21, 0), "末": (21, 0)}[k]
            if end and b == 0: return datetime.date(y + mo // 12, mo % 12 + 1, 1) - datetime.timedelta(days=1)
            return datetime.date(y, mo, b if end else a)
        return d(*mm[0], False), d(*mm[-1], True)
    for x in rd("data", "meisho.json")["items"]:
        r = prange(x.get("peak"))
        if x.get("pref") not in FULL or not r or r[1].isoformat() < TD: continue
        it = {"t": x["name"], "u": x.get("url", ""), "p": x["pref"], "s": r[0].isoformat(), "e": r[1].isoformat(), "a": x.get("city", ""), "v": "", "k": "koyo", "pk": x.get("peak", "")}
        if x.get("fee"): it["fe"] = x["fee"]
        if (x.get("fee") or "").startswith("無料"): it["f"] = 1
        if x.get("note"): it["hk"] = x["note"]
        ky.append(ENRICH(it, x["name"], x.get("city", "")))
    print("illumination", len(il), "koyo", len(ky))
    if il:
        write("illumination.html", "/illumination", "関東イルミネーション2026-2027｜開催中・無料・今週末（東京・神奈川・埼玉・千葉・茨城・栃木・群馬）｜LIFE NOTE", cfg("/illumination"),
              dict(data, items=il, page={"h1": "関東のイルミネーション", "sub": f"2026-2027・{len(il)}か所", "st": "pref"}), "odekake",
              f"関東のイルミネーション{len(il)}か所を、開催中・これから・無料に分けて、公式ページつきでまとめています。地図と写真で探せて、毎日更新しています。")
        write("illumination-muryo.html", "/illumination-muryo", "関東の無料イルミネーション2026-2027｜LIFE NOTE", cfg("/illumination"),
              dict(data, items=il, page={"h1": "関東の無料イルミネーション", "sub": f"2026-2027・{sum(1 for i in il if i.get('f'))}か所", "st": "pref", "free": 1}), "odekake",
              "関東の無料で見られるイルミネーションを、開催中・これからに分けてまとめています。")
        for p in PREF:
            ni = sum(1 for i in il if i["p"] == p)
            if not ni: continue
            write(f"illumination-{SLUG[p]}.html", f"/illumination-{SLUG[p]}", f"{p}のイルミネーション2026-2027（{FULL[p]}）｜LIFE NOTE", cfg("/illumination"),
                  dict(data, items=il, page={"h1": f"{p}のイルミネーション", "sub": f"2026-2027・{ni}か所", "p": p, "st": "pref"}), "odekake",
                  f"{FULL[p]}のイルミネーション{ni}か所を、開催中・これから・無料に分けてまとめています。")
    if ky:
        write("koyo.html", "/koyo", "関東の紅葉2026｜見頃とライトアップ（東京・神奈川・埼玉・千葉・茨城・栃木・群馬）｜LIFE NOTE", cfg("/koyo"),
              dict(data, items=ky, page={"h1": "関東の紅葉", "sub": f"見頃とライトアップ・{len(ky)}か所", "st": "pref"}), "odekake",
              f"関東の紅葉の名所と夜のライトアップ{len(ky)}か所を、見頃の時期・料金・時間つきでまとめています。地図と写真で探せて、毎日更新しています。")

    # ---------- いまから行ける（関西 /ima と同じ形：いる場所から近い順・きょう開いている所） ----------
    im, seen = [], set()
    for src in (IT, il, ky):
        for x in src:
            if not x.get("xy") or x["s"] > TD or x["e"] < TD: continue
            k = re.sub(r"\s+", "", x["t"])
            if k in seen: continue
            seen.add(k)
            it = dict(x); it["ll"] = [round(37.15 - (x["xy"][1] - 27) / 100, 4), round((x["xy"][0] - 10) / 81 + 138.4, 4)]
            im.append(it)
    if len(im) >= 10:
        c = cfg("/ima"); c["nav"] = [{"t": "近い順", "ic": "map", "a": "top", "cur": 1}, {"t": "おでかけ", "ic": "now", "href": "/odekake"}, {"t": "イルミ", "ic": "we", "href": "/illumination"}, {"t": "保存", "ic": "star", "a": "fav"}]
        write("ima.html", "/ima", "いまから行ける関東のおでかけ｜近い順・きょう開いている所｜LIFE NOTE", c,
              {"items": im, "icons": ICONS, "page": {"h1": "いまから行けるおでかけ", "sub": "きょう開いている所を、近い順に", "near": 1, "K": KINDS(im), "cnt": "か所", "seg": False,
                                                     "none": "この時間で行ける所は見つかりませんでした。「1時間半」「すべて」でもう少し遠くまで探せます。",
                                                     "note": "かかる時間は直線距離から出した目安です（電車と歩きを合わせたおおよその時間）。本当の行き方は「行き方」から Google マップで。開いている時間は出かける前に公式で確かめてください。"}},
              "list", f"いる場所といまの時刻から、きょう開いている関東のおでかけ{len(im)}か所を近い順に並べます。30分・1時間・1時間半で行ける所がすぐ分かります。")

    # ---------- 開店・閉店（scripts/kaiten.py の決まりをそのまま使う：ジャンル・初出店・場所の写真） ----------
    try:
        sys.path.insert(0, os.path.join(R, "scripts"))
        import kaiten as K
        GC = {"カフェ": "#8A5A3B", "パン・スイーツ": "#C2557A", "ごはん": "#C0532B", "スーパー・コンビニ": "#2E8B6E", "ドラッグ・薬": "#2F7D9A", "服・雑貨": "#5B4B8A",
              "美容・からだ": "#B7862A", "遊び・体験": "#3B5BA5", "車・家電": "#4F6681", "施設": "#6F8C68", "その他": "#6E6E73"}
        kt = []
        for x in sorted([x for x in rd("data", "kaiten.json")["items"] if K.bucket(x)], key=lambda x: x["d"]):
            b = K.bucket(x); g, _ = K.genre(x); h = K.hatsu(x); v = K.vphoto(x); d = datetime.date.fromisoformat(x["d"])
            lab = {"open": "開店", "pop": "期間限定", "close": "閉店"}[x["k"]]
            wd = "月火水木金土日"[d.weekday()]
            it = {"t": x["n"], "p": x["p"], "a": x.get("pl") or "", "k": g, "w": b, "u": x["u"], "ub": "公式の発表を見る", "id": K.slug(x),
                  "d": f"{d.month}/{d.day}（{wd}）{lab}", "hk": x.get("pt", ""),
                  "bg": (h or lab) if b != "close" else "閉店", "bgc": "off" if b == "close" else ("pop" if not h else ""),
                  "rows": [r for r in [["日", f"{d.month}月{d.day}日（{wd}）{lab}" + (f"〜{x['end']}" if x.get("end") else "")], ["場所", x.get("pl") or x["p"]], ["時間", x.get("tm") or ""]] if r[1]],
                  "mq": (x.get("pl") or "") + " " + x["n"], "big": ("あと" + str((d - datetime.date.fromisoformat(TD)).days) + "日で" + lab if x["d"] > TD else ("きょう" + lab if x["d"] == TD else ""))}
            if os.path.exists(os.path.join(S, "kaiten", it["id"] + ".html")): it["sp"] = "/kaiten/" + it["id"]
            if v: it.update({"im": v["img"], "cr": v["cr"], "cu": v.get("page", "")})
            kt.append(it)
        kt.reverse()
        if kt:
            cn = {k: sum(1 for x in kt if x["w"] == k) for k in ("soon", "done", "close")}
            c = cfg("/kaiten")
            c["nav"] = [{"t": "これから", "ic": "now", "a": "w=soon"}, {"t": "開いた", "ic": "we", "a": "w=done"}, {"t": "閉まる", "ic": "down", "a": "w=close"}, {"t": "保存", "ic": "star", "a": "fav"}]
            c["menu"] = {"k": "New Shops", "items": [["関東の開店・閉店", "/kaiten", 1], ["関西の開店・閉店", "https://kansai.townnote.app/kaiten"]]}
            c["foot"] = "各社の公式の発表（プレスリリース・お店のお知らせ）から集めています。写真はお店の入る建物・場所の写真で、撮影者を各ページに書いています（ウィキメディア・コモンズ ほか）。"
            write("kaiten.html", "/kaiten", "関東の開店・閉店ニュース｜新しいお店・閉まるお店を公式の発表で｜LIFE NOTE", c,
                  {"items": kt, "icons": ICONS, "page": {"h1": "関東の開店・閉店", "sub": "新しいお店・閉まるお店を、公式の発表で", "view": "list", "fav": 1, "id": "kaiten",
                                                         "K": {g: [g, GC[g]] for g in GC if any(x["k"] == g for x in kt)},
                                                         "dl": f"毎日更新・<b>{len(kt)}</b>件", "tabs": [["soon", f"これから {cn['soon']}", "w", "soon"], ["done", f"開いた {cn['done']}", "w", "done"], ["close", f"閉まる {cn['close']}", "w", "close"]]}},
                  "list", f"東京・神奈川・埼玉・千葉など関東の新しいお店・閉まるお店を、各社の公式の発表から毎日集めています。これから{cn['soon']}件・開いた{cn['done']}件・閉まる{cn['close']}件。")
    except Exception as e:
        print("shin_kanto: 開店・閉店は前のまま", repr(e))

    # ---------- おかいもの（関西 /shin/kau と同じ形・値段は site/okai-shin.json） ----------
    try:
        d = json.load(open(os.path.join(S, "okai-shin.json"), encoding="utf-8"))
        if len(d.get("cats", [])) >= 10:
            from okai_home import ICON
            GROUPS = [("赤ちゃん", ["diaper", "wipes"]), ("紙・日用品", ["tp", "tissue", "trash", "mask", "battery"]),
                      ("洗濯・お風呂", ["detergent", "softener", "shampoo", "bodysoap", "dish"]),
                      ("飲み物・食べ物", ["water", "tea", "soda", "coffee", "beans", "rice", "pasta"]), ("ペット", ["dogfood", "catfood"])]
            have = {c_["k"] for c_ in d["cats"]}
            d["ic"] = {k: v for k, v in ICON.items() if k in have}
            d["groups"] = [[g, [k for k in ks if k in have]] for g, ks in GROUPS]
            d["live"] = "/okai-shin.json"
            c = {"nav": [{"t": "品物", "ic": "find", "a": "find"}, {"t": "値下がり", "ic": "down", "a": "drop"}, {"t": "いつもの物", "ic": "star", "a": "my"}, {"t": "ふるさと納税", "ic": "gift", "href": "/furusato"}],
                 "menu": {"k": "Shopping", "items": [["日用品の値段くらべ", "/okaimono", 1], ["ふるさと納税", "/furusato"], ["値下がりした物の一覧", "/nesage"], ["今までのおかいものの画面", "/kyu/okaimono"]]},
                 "foot": "値段：楽天市場・Yahoo!ショッピングで調べた送料込みの値段（調べた時のもの。お店で変わることがあります）。Amazonは値段を自動で調べられないため、押すとAmazonの検索が開きます。<br>このページのお店へのリンクは広告（PR）です。"}
            write("okaimono.html", "/okaimono", "日用品の値段くらべ（楽天・Yahoo!・Amazon）｜LIFE NOTE", c, d, "kau",
                  f"ティッシュ・トイレットペーパー・おむつ・洗剤・水・お米など{len(d['cats'])}種類を、楽天とYahoo!ショッピングの送料込みの値段で、1Lあたり・1枚あたりに直して比べています。Amazonも同じ画面から見られます。広告（PR）を含みます。")
    except Exception as e:
        print("shin_kanto: おかいものは前のまま", repr(e))

    docs()
    furu()
    ie_kanto()
    # ---------- 表紙 ----------
    now = [x for x in IT if x["s"] <= TD <= x["e"]]
    pc = {p: sum(1 for x in now if x["p"] == p) for p in PREF}
    ph = [x for x in sorted(now, key=lambda x: x["e"]) if x.get("im")]
    top, used = [], set()
    while len(top) < 8 and ph:
        for p in PREF:
            c_ = next((x for x in ph if x["p"] == p and x["t"] not in used), None)
            if c_ and len(top) < 8: top.append({k: c_[k] for k in ("t", "p", "e", "im", "th", "o") if k in c_}); used.add(c_["t"])
        if all(x["t"] in used for x in ph): break
    towns = len([f for f in os.listdir(os.path.join(S, "machi")) if f.endswith(".html")]) if os.path.isdir(os.path.join(S, "machi")) else 0
    kaiten = 0
    try:
        kaiten = len(re.findall(r'class="kc', open(os.path.join(S, "kaiten.html"), encoding="utf-8").read()))
    except Exception:
        pass
    go = [{"t": "関東のおでかけ・イベント", "s": "開催中・今週末・まもなく終わる", "n": str(len(now)), "nu": "開催中", "u": "/odekake", "ic": "now"},
          {"t": "家と土地の相場", "s": f"{towns}の街の地価の動き" if towns else "街の地価の動き", "n": str(towns or ""), "nu": "街", "u": "/fudosan-list", "ic": "find"},
          {"t": "日用品の値段くらべ", "s": "楽天・Yahoo!を1つの画面で", "n": "", "nu": "", "u": "/okaimono", "ic": "yen"},
          {"t": "開店・閉店", "s": "新しいお店・閉まるお店", "n": "", "nu": "", "u": "/kaiten", "ic": "buy"}]
    more = [["関東のイルミネーション", "/illumination"], ["関東の紅葉", "/koyo"], ["いまから行けるおでかけ", "/ima"], ["地価ランキング", "/chika-kanto"], ["空き家の割合ランキング", "/akiya-ranking"],
            ["予算で街さがし", "/sagasu"], ["家を売る前に", "/uru"], ["ふるさと納税", "/furusato"], ["値下がりした日用品", "/nesage"]]
    c = copy.deepcopy(base)
    c["nav"] = [{"t": "おでかけ", "ic": "now", "href": "/odekake"}, {"t": "家と土地", "ic": "find", "href": "/fudosan-list"}, {"t": "おかいもの", "ic": "yen", "href": "/okaimono"}, {"t": "地図", "ic": "map", "a": "map"}]
    c["menu"] = {"k": "Life Note", "items": [["トップ", "/", 1], ["関東のおでかけ", "/odekake"], ["家と土地の相場", "/fudosan-list"], ["日用品の値段くらべ", "/okaimono"], ["開店・閉店", "/kaiten"], ["紅葉・イルミ", "/koyo"]]}
    c["foot"] = "おでかけの券・宿と、おかいもののリンクには広告（PR）があります。"
    # 11/19 23:16 owner「表紙ほぼおでかけ」「Appleっぽくもない」→ 関西と同じ apple.com の形（cover2.js）。地図は表紙に置かない
    RK = {"koyo": 0, "flower": 1, "spot": 2, "animal": 3, "play": 4}
    def pick_ph(f, n):
        r, u = [], set()
        for x in sorted(now, key=lambda x: (RK.get(x.get("k"), 9), x["e"])):
            if x.get("im") and f(x) and x["im"] not in u: r.append({k: x[k] for k in ("t", "p", "e", "im", "th", "o") if k in x}); u.add(x["im"])
            if len(r) >= n: break
        return r
    tw = []
    try:
        ck = open(os.path.join(S, "chika-kanto.html"), encoding="utf-8").read()
        for m in re.finditer(r'<a href="/machi/([\w-]+)"[^>]*><span class="no">\d+</span><span class="nm">([^<]+)<small>[^<]*</small></span>.*?<span class="v"[^>]*>\+?(-?[\d.]+)%', ck):
            tw.append({"n": m.group(2), "r": float(m.group(3)), "id": m.group(1)})
            if len(tw) >= 3: break
    except Exception:
        pass
    ks = []
    try:
        od_ = json.load(open(os.path.join(S, "okai-shin.json"), encoding="utf-8")); from okai_home import ICON
        KS = {c_["k"]: c_ for c_ in od_["cats"]}
        ks = [{"k": k, "nm": KS[k]["nm"], "unit": KS[k]["unit"], "u": KS[k]["o"][0]["u"], "ic": ICON.get(k, "")} for k in ("rice", "water", "tissue") if k in KS and KS[k].get("o")]
        nkau = len(od_["cats"])
    except Exception:
        nkau = 0
    ktl = locals().get("kt") or []
    ka = next(({k: x[k] for k in ("t", "a", "d", "im", "big", "sp", "p") if k in x} for x in reversed(ktl) if x["w"] == "soon" and x.get("im")), None)
    hero = pick_ph(lambda x: True, 5)
    ko = (pick_ph(lambda x: x.get("k") == "koyo" and x.get("im") not in {q["im"] for q in hero}, 1) or pick_ph(lambda x: x.get("k") == "koyo", 1) or [None])[0]
    c["nav"] = [{"t": "おでかけ", "ic": "now", "href": "/odekake"}, {"t": "家と土地", "ic": "find", "href": "/fudosan-list"}, {"t": "おかいもの", "ic": "yen", "href": "/okaimono"}, {"t": "開店閉店", "ic": "buy", "href": "/kaiten"}]
    c["menu"] = {"k": "Life Note", "items": [["トップ", "/", 1], ["関東のおでかけ", "/odekake"], ["家と土地の相場", "/fudosan-list"], ["日用品の値段くらべ", "/okaimono"], ["開店・閉店", "/kaiten"], ["ふるさと納税", "/furusato"]]}
    write("index.html", "/", "LIFE NOTE（ライフノート）｜関東のおでかけと、家と土地の値段", c,
          {"od": {"n": len(now), "ph": hero}, "ie": {"n": towns, "tw": tw}, "kau": {"n": nkau, "ks": ks},
           "kai": {"n": sum(1 for x in ktl if x["w"] == "soon"), "x": ka}, "ko": ko,
           "ft": [["おでかけ", [["関東のおでかけ", "/odekake"], ["イルミネーション", "/illumination"], ["紅葉", "/koyo"], ["いまから行ける", "/ima"]]],
                  ["家と土地", [["家と土地の相場", "/fudosan-list"], ["地価ランキング", "/chika-kanto"], ["空き家の割合ランキング", "/akiya-ranking"], ["予算で街さがし", "/sagasu"], ["いくらで売れる？", "/ikura"], ["家を売る前に", "/uru"], ["実家・空き家", "/jikka/"], ["解体の費用", "/kaitai"], ["解体の補助金", "/kaitai-ranking"]]],
                  ["おかいもの", [["日用品の値段くらべ", "/okaimono"], ["開店・閉店ニュース", "/kaiten"], ["ふるさと納税", "/furusato"], ["値下がりした物", "/nesage"]]],
                  ["このサイト", [["相談・申し込み", "/moushikomi"], ["リクエスト・感想", "/koe"], ["プライバシーポリシー", "/privacy"]]]],
           "sns": [["インスタ", "https://www.instagram.com/usagichan_ai_si/"], ["Threads", "https://www.threads.com/@usagichan_ai_si"], ["X", "https://x.com/ai_usagichan"]]},
          "cover2", "関東のくらしで見つけたことを、ノートにまとめています。開催中のおでかけ・イベント、街の家と土地の値段、日用品の値段くらべ、開店・閉店を、公式の発表と数字で。")


def ie_kanto():
    """家と土地の相場（関西 /shin/ie と同じ ie.js）。11/19 owner「その他も本気でやり直せ」→ 前の関東不動産リスト（古い形）をやめる。
    数字：site/assets/towns.json（地価公示・順位・位置）＋ scripts/toukei_kanto.json（国勢調査・住宅土地統計）。関東は売れた値段（レインズ）がまだ無い。"""
    try:
        towns = json.load(open(os.path.join(S, "assets", "towns.json"), encoding="utf-8"))
        tk = json.load(open(os.path.join(R, "scripts", "toukei_kanto.json"), encoding="utf-8"))
        jis = json.load(open(os.path.join(R, "scripts", "jis_kanto.json"), encoding="utf-8"))
        PF = {"東京": "東京都", "神奈川": "神奈川県", "埼玉": "埼玉県", "千葉": "千葉県", "茨城": "茨城県", "栃木": "栃木県", "群馬": "群馬県"}
        PJ = {"東京": "13000", "神奈川": "14000", "埼玉": "11000", "千葉": "12000", "茨城": "08000", "栃木": "09000", "群馬": "10000"}
        PA = {}
        for p_ in PF:
            s_ = tk.get(PJ[p_], {})
            PA[p_] = {"m": None, "h": None, "t": None, "pop": round((s_["p25"] / s_["p20"] - 1) * 100, 1) if s_.get("p20") else None,
                      "ak": round(s_["a23"] / s_["j23"] * 100, 1) if s_.get("j23") else None}
        out = []
        for t_ in towns:
            x = {k: t_.get(k) for k in ("id", "p", "n", "s", "k", "r7", "r8", "rk", "of")}
            s_ = tk.get(jis.get(t_["p"] + "|" + t_["n"]) or "", {})
            if s_.get("p20"): x["pop"] = [s_["p25"], round((s_["p25"] / s_["p20"] - 1) * 100, 1)]
            if s_.get("o25"): x["o"] = s_["o25"]
            if s_.get("j23"): x["ak"] = round(s_["a23"] / s_["j23"] * 100, 1)
            if t_.get("la"):
                X, Y = proj(t_["lo"], t_["la"]); x["xy"] = [round(X, 2), round(Y, 2)]
            pg = os.path.join(S, "machi", t_["id"] + ".html")
            if os.path.exists(pg):
                h_ = open(pg, encoding="utf-8").read()
                buy = [html.unescape(u) for u in re.findall(r'<a [^>]*href="(https://ck\.jp\.ap\.valuecommerce[^"]+)"', h_)]
                if buy: x["buy"] = buy[:3]
                kt_ = re.search(r'href="(/kaitai-[a-z]+)"', h_)
                if kt_: x["kt"] = kt_.group(1)
            out.append(x)
        if len(out) < 100:
            return
        c = {"nav": [{"t": "街をさがす", "ic": "find", "a": "find"}, {"t": "ランキング", "ic": "rank", "a": "rank"}, {"t": "売りたい", "ic": "sell", "href": "/uru"}, {"t": "いくら？", "ic": "yen", "href": "/ikura"}],
             "menu": {"k": "Home & Land", "items": [["家と土地の相場", "/fudosan-list", 1], ["家を売る前に", "/uru"], ["いくらで売れる？", "/ikura"], ["実家・空き家", "/jikka/"], ["解体の費用と補助金", "/kaitai"], ["地価ランキング", "/chika-kanto"]]},
             "foot": "地価：国土交通省・各都県「令和8年地価公示」。人口・空き家：総務省統計局（国勢調査・住宅・土地統計調査）。<br>どれも街の平均で、1軒ずつの値段ではありません。「買いたい」のリンクは広告です（Yahoo!不動産）。"}
        write("fudosan-list.html", "/fudosan-list", f"関東の家と土地の相場｜{len(out)}の街の地価と人口｜LIFE NOTE", c,
              {"towns": out, "pa": PA, "map": MAP, "pfull": PF, "pc": PC, "h1": "関東の家と土地の相場", "sub": f"{len(out)}の街の、地価の動きと人口・空き家",
               "upd": "2026年の地価公示・国勢調査（2025年）の数字", "ph": "横浜、よこはま"}, "ie",
              f"関東{len(out)}の市区町村の、住宅地の地価の動き（令和8年地価公示）と人口・空き家の割合を、街ごとにまとめました。都県の平均とも比べられます。")
    except Exception as e:
        print("shin_kanto: 家と土地は前のまま", repr(e))


def furu():
    """ふるさと納税・値下がりした物（関西と同じ furu.js）。11/19 owner「ふるさと押したら前のページ飛ぶ」"""
    NAVR = lambda first: first + [{"t": "おかいもの", "ic": "yen", "href": "/okaimono"}]
    MENU = lambda cur: {"k": "Shopping", "items": [[a, u] + ([1] if u == cur else []) for a, u in [["日用品の値段くらべ", "/okaimono"], ["ふるさと納税", "/furusato"], ["値下がりした物", "/nesage"], ["開店・閉店", "/kaiten"]]]}
    FOOT = "値段は楽天市場で調べた時のものです（お店で変わることがあります）。このページの商品へのリンクは広告（PR）です。"
    try:
        f = json.load(open(os.path.join(R, "data", "furusato.json"), encoding="utf-8"))
        cats = [c_ for c_ in f["cats"] if c_.get("top")]
        if cats:
            IC = {"rice": "gift", "tp": "find", "water": "star"}
            write("furusato.html", "/furusato", "ふるさと納税 寄付1万円でもらえる量くらべ（お米・トイレットペーパー・水）｜LIFE NOTE",
                  {"nav": NAVR([{"t": c_["title"] if len(c_["title"]) <= 5 else "トイレ", "ic": IC.get(c_["key"], "gift"), "a": c_["key"]} for c_ in cats][:3]), "menu": MENU("/furusato"), "foot": FOOT},
                  {"kind": "furu", "h1": "ふるさと納税 1万円でもらえる量", "sub": "楽天ふるさと納税の返礼品を、寄付1万円あたりの量でくらべました。", "at": f["at"], "cats": cats}, "furu",
                  "ふるさと納税の返礼品（お米・トイレットペーパー・水）を、寄付1万円でもらえる量でくらべました。楽天ふるさと納税を毎日しらべ直しています。")
    except Exception as e:
        print("shin_kanto: ふるさと納税は前のまま", repr(e))
    try:
        n = json.load(open(os.path.join(R, "data", "nesage.json"), encoding="utf-8"))
        if n.get("downs"):
            write("nesage.html", "/nesage", "値下がりした日用品｜ふだんより安い物（楽天市場を毎日しらべ）｜LIFE NOTE",
                  {"nav": NAVR([{"t": "値下がり", "ic": "down", "a": "down"}, {"t": "値上がり", "ic": "rank", "a": "up"}, {"t": "ふるさと", "ic": "gift", "href": "/furusato"}]), "menu": MENU("/nesage"), "foot": FOOT},
                  {"kind": "nesage", "h1": "値下がりした物", "sub": f"楽天市場の日用品{n.get('tracked', '')}品の値段を毎日しらべ、ふだんより安くなっている物を並べています。",
                   "at": n["at"], "since": n.get("since"), "tracked": n.get("tracked"), "downs": n["downs"], "ups": n.get("ups", [])}, "furu",
                  f"楽天市場の日用品{n.get('tracked', '')}品の値段を毎日しらべ、ふだんより安くなっている物を並べています。")
    except Exception as e:
        print("shin_kanto: 値下がりは前のまま", repr(e))


if __name__ == "__main__":
    main()
