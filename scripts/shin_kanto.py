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
sys.path.insert(0, os.path.join(R, "scripts", "shin"))
from ix import ix_html as IX, pre_html as PRE
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


# 11/20 関西のカードには「何が見られるか」の一言（hk）があり、関東には無かった → note（公式で確かめた文）から、
# 時刻・料金・休み・日付・場所だけの文を除いた、短い説明の1文を一言にする（関西の hk と同じ長さ 6〜26字）
_HTM = re.compile(r"\d{1,2}:\d\d|\d{1,2}時(?!間)|日没|終日")
_HBAD = re.compile(r"\d[\d,]*円|無料|休み|休館|休園|休室|予約|日時指定|先着|公式|変わ|中止|駐車|駅から|歩いて|必要|要ります|\d+/\d+|\d+月\d+日|※|^第\d+回$|\d+階$|中心$")
def hk_of(ds, t=""):
    for sg in [x.strip() for x in (ds or "").split("。") if x.strip()]:
        if "｜" in sg: sg = sg.split("｜", 1)[1].strip()
        if _HTM.search(sg) or _HBAD.search(sg) or not 6 <= len(sg) <= 26: continue
        if re.sub(r"\s", "", sg) in re.sub(r"\s", "", t) or (len(sg) <= 9 and sg[-3:] in t): continue
        return sg
    return ""


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
        _oid = hashlib.md5(re.sub(r"\s+", "", name).encode()).hexdigest()[:8]  # 11/20 イルミ・紅葉のカードからも1件ページへ（関西の fin と同じ）
        if "o" not in it and _oid in opages: it["o"] = _oid
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
        if x.get("note") and hk_of(x["note"], t): it["hk"] = hk_of(x["note"], t)
        if x.get("opennote"): it["h"] = x["opennote"]
        enrich(it, t, x.get("place", ""))
        oid = hashlib.md5(key.encode()).hexdigest()[:8]
        if oid in opages: it["o"] = oid
        if it.get("im"):  # 11/21 関西と同じ：写真の見た目の点（vb）・夜の写真（nt）・紅葉の色（wm）→ 丸の表紙・今週末の顔の並び（odekake.js TH）
            m = PHM(it["im"])
            if m and IS_NIGHT(m): it["nt"] = 1
            if m and m[1] >= .2: it["wm"] = 1
            b = PHB(it["im"])
            if b: it["vb"] = b
        out.append(it)
    print("shin_kanto items", len(out), "photos", sum("im" in i for i in out), "map", sum("xy" in i for i in out), "live", len(live))
    return out


REL = [["おでかけ", "/odekake"], ["家と土地", "/fudosan-list"], ["おかいもの", "/okaimono"], ["開店・閉店", "/kaiten"], ["トップへ", "/"]]
SEC = {"Odekake": "/odekake", "Home & Land": "/fudosan-list", "Shopping": "/okaimono", "New Shops": "/kaiten"}
# 11/20 owner「統一されてない・整理されてない」：MENU の項目と並び順は分野ごとにここ1か所だけ（関西 tools/shin/build.py の MENUS・skin.js と同じ形）
MENUS = {
    "Odekake": [["関東おでかけ", "/odekake"], ["イルミネーション", "/illumination"], ["紅葉", "/koyo"], ["いまから行ける", "/ima"], ["泊まり", "/tomari"], ["初詣", "/hatsumode"]],
    "Home & Land": [["家と土地の相場", "/fudosan-list"], ["地価ランキング", "/chika-kanto"], ["まちランキング", "/ranking"], ["家を売る前に", "/uru"], ["いくらで売れる？", "/ikura"], ["実家・空き家", "/jikka/"], ["解体の費用と補助金", "/kaitai"]],
    "Shopping": [["日用品の値段くらべ", "/okaimono"], ["本当に安い？", "/nesage"], ["お得な物", "/otoku"], ["ふるさと納税", "/furusato"]],
    "New Shops": [["関東の開店・閉店", "/kaiten"]],
}


# 11/20 関西（usagi tools/shin/build.py の FIT）と同じ：写真ごとに 明るさ・赤や橙・緑・幅 を量り、ページに合う写真を先に
# （イルミは夜の写真、紅葉は赤や黄の写真。幅900未満は「今週末のおすすめ」の後ろへ）。量った数は data/photo_m.json に残す
_PMF = os.path.join(R, "data", "photo_m.json")
try: _PM = json.load(open(_PMF, encoding="utf-8"))
except Exception: _PM = {}
# 11/20 暗い昼の写真（木陰の寺など）を「夜の写真」と取り違えていた → 暗い所の割合・上の方（空）の暗さ・青空の割合も量る
def NIGHT(px):
    lum = [0.299*r + 0.587*g + 0.114*b for r, g, b in px]; top = lum[:64*12]
    return [round(sum(v < 35 for v in lum)/len(lum), 2), round(sum(v < 40 for v in top)/len(top), 2),
            round(sum(1 for r, g, b in px[:64*12] if b > r + 15 and b > 110)/len(top), 2)]
def IS_NIGHT(m):
    return (m[4] >= .5 or (m[5] >= .35 and m[6] < .2)) if len(m) > 6 else m[0] < 75
def PHM(f):
    if f in _PM and len(_PM[f]) > 6: return _PM[f]
    try:
        import colorsys
        from PIL import Image
        im0 = Image.open(os.path.join(S, "assets", "ph", f)); w0 = im0.size[0]
        im = im0.convert("RGB").resize((64, 48)); px = list(im.getdata())
        lum = sum(0.299*r + 0.587*g + 0.114*b for r, g, b in px) / len(px); w = gr = 0
        for r, g, b in px:
            h, sa, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            if sa > .35 and v > .25 and (h < .11 or h > .95): w += 1
            if sa > .25 and v > .2 and .17 < h < .45: gr += 1
        _PM[f] = [round(lum), round(w/len(px), 2), round(gr/len(px), 2), w0]
        _PM[f] += NIGHT(px)
        json.dump(_PM, open(_PMF, "w", encoding="utf-8"))
        return _PM[f]
    except Exception:
        return _PM.get(f)
# 11/21 写真の見た目の点（関西 tools/photo/best.py visual_im と同じ物差し・テーマなし）。data/photo_b.json にためる
_PBF = os.path.join(R, "data", "photo_b.json")
try: _PB = json.load(open(_PBF, encoding="utf-8"))
except Exception: _PB = {}
def PHB(f):
    if f in _PB: return _PB[f]
    try:
        from PIL import Image, ImageFilter, ImageStat
        im = Image.open(os.path.join(S, "assets", "ph", f)).convert("RGB"); im.thumbnail((240, 240))
        hsv = im.convert("HSV"); px = list(hsv.getdata()); n = len(px) or 1
        L = im.convert("L"); lm = ImageStat.Stat(L).mean[0]
        sat = sum(p[1] for p in px) / n / 255
        edge = ImageStat.Stat(L.filter(ImageFilter.FIND_EDGES)).mean[0]
        sc = max(-10, min(14, (sat - .22) * 60)) + max(-12, min(10, (edge - 9) * 1.2))
        if lm < 60: sc -= 14
        elif lm > 205: sc -= 10
        top = px[:n // 3]
        if top and sum(1 for p in top if p[1] < 30 and p[2] > 170) / len(top) > .55: sc -= 10
        _PB[f] = round(sc, 1)
        json.dump(_PB, open(_PBF, "w", encoding="utf-8"))
    except Exception:
        _PB[f] = 0
    return _PB[f]
# 11/20 人気順（関西の POP と同じ考え）：この30日に新しいページのカードが押された数。data/page-stats.json の click["card"]「ページ|題」
def _pop():
    try:
        d = json.load(open(os.path.join(R, "data", "page-stats.json"), encoding="utf-8"))["days"]
    except Exception:
        return {}
    cut = (datetime.date.fromisoformat(TD) - datetime.timedelta(days=30)).isoformat(); out = {}
    for day, v in d.items():
        if day < cut: continue
        for item, n in (v.get("click", {}).get("card") or {}).items():
            t = item.split("|", 1)[-1]
            out[t] = out.get(t, 0) + n
    return out
POPS = _pop()
def FIT(items, kind):
    for it in items:
        m = PHM(it["im"]) if it.get("im") else None
        if not m: continue
        lum, warm, green = m[:3]
        if len(m) > 3 and m[3] < 900: it["lo"] = 1
        if kind == "illumination": it["ok"] = 2 if IS_NIGHT(m) else -1
        elif kind == "koyo": it["ok"] = 2 if warm >= .2 else (-1 if green >= .3 and warm < .1 else 0)
        if not it.get("ok"): it.pop("ok", None)
        b = PHB(it["im"])
        if b: it["vb"] = b

def write(fname, url, title, cfg, data, js, desc):
    cfg["reg"] = REG
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        FIT(data["items"], "illumination" if fname.startswith("illumination") else "koyo" if fname.startswith("koyo") else "")
        for it in data["items"]:
            n = POPS.get(re.sub(r"\s+", " ", it.get("t", "")).strip()[:40])
            if n: it["pp"] = n
    # 11/20 表紙の MENU は分野の入口そのものなので、下の重なるボタンは出さない（関西と同じ）
    m = cfg["menu"]
    if m.get("k") in MENUS:
        cur = next((x[1] for x in m["items"] if len(x) > 2 and x[2]), None)
        m["items"] = [[t, u] + ([1] if u == cur else []) for t, u in MENUS[m["k"]]]
    # MENU の下のボタンは「ほかの分野＋トップへ」をどのページでも同じ順で（自分の分野は出さない）
    m["rel"] = [] if url == "/" else [r for r in REL if r[1] != SEC.get(m.get("k"), url)]
    head = (f'<meta name="description" content="{html.escape(desc)}">' +
            f'<link rel="canonical" href="{SITE}{url}"><meta property="og:title" content="{html.escape(title.split("｜")[0])}">'
            f'<meta property="og:image" content="{SITE}/og-v10.png"><meta property="og:url" content="{SITE}{url}">')
    page = (TPL.replace("__TITLE__", html.escape(title)).replace("__HEAD__", head).replace("__CFG__", J(cfg)).replace("__DATA__", J(data))
            .replace("__CV__", ver("shin.css")).replace("__JV__", ver("shin.js")).replace("__PAGE__", js).replace("__PV__", ver(js + ".js")))
    # 11/20 検索の機械にも中身とリンクが見えるように、ページの下の「一覧」を HTML のまま（scripts/shin/ix.py・関西と同じ）
    page = page.replace('<div id="app"></div>', '<div id="app">' + PRE(data) + '</div>' + IX(fname[:-5], data, S), 1)
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
        # 11/21 夜の気づき（反響7日0件）：STEP2 で外の AI査定が大きなボタン・自分たちの相談は小さな「こちら」だけだった
        # → 人の売却相談を目立つボタンに、外の AI査定は「（広告）」と書いた2つめのボタンに（/ikura と同じ出し方）。行き先はそのまま
        ad = re.search(r'<a class="dbtn" (href="https://px\.a8\.net[^"]*")[^>]*>.*?</a>(<img [^>]*a8\.net[^>]*>)?', sc, re.S)
        hito = re.search(r'<p[^>]*>人に聞きたい方は <a href="([^"]+)"[^>]*>.*?</a></p>', sc, re.S)
        if ad and hito:
            sc = sc.replace(hito.group(0), "")
            sc = sc.replace(ad.group(0), f'<a class="dbtn" href="{hito.group(1)}" data-k="売る前に｜申し込む">人に無料で売却相談（名字だけでOK）<small>約1分・売るか決めていなくても大丈夫</small></a>'
                            f'<a class="dbtn2" {ad.group(1)} rel="nofollow sponsored noopener" target="_blank" data-k="売る前に｜AI査定">AIでざっくり値段を見る（無料）<small style="display:block;font-weight:400;font-size:12px;opacity:.7;margin-top:2px">ざっくりAI査定＋（広告）・電話ラッシュなし</small></a>' + (ad.group(2) or ""))
            sc = sc.replace("「いくらで売れそうか」を、無料のAI査定で見られます。", "「いくらで売れそうか」を、無料で人に聞けます。").replace("無料で人に聞けます。売るか決めていなくても大丈夫です。", "無料で人に聞けます。")
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


HOME_NAV = [{"t": "街をさがす", "ic": "find", "href": "/fudosan-list"}, {"t": "ランキング", "ic": "rank", "href": "/ranking"},
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
    # 11/23 owner「全部やり変えて」：地価ランキング（関東・東京23区）を新しい土台で（scripts/shin_chika.py＝月の tools/shin/chika.py の写し・site/shin/rk.js）
    try:
        sys.path.insert(0, os.path.join(R, "scripts")); import shin_chika
        for u in shin_chika.build_kanto(write, S, R, home_cfg):
            sm = os.path.join(S, "sitemap.xml")
            if os.path.exists(sm) and f"{SITE}{u}<" not in open(sm, encoding="utf-8").read():
                x = open(sm, encoding="utf-8").read().replace("</urlset>", f"<url><loc>{SITE}{u}</loc></url></urlset>"); open(sm, "w", encoding="utf-8").write(x)
    except Exception as e:
        print("shin_kanto: 地価ランキングは前のまま", repr(e))
    # 11/23 前のページを新しい土台で作り直す（scripts/shin_yari.py＝月の tools/shin/yari.py の写し。関西と同じ）
    import shin_yari as Y
    REL0 = [["家と土地の相場", "/fudosan-list", "街ごとの売れた値段"], ["地価ランキング", "/chika-kanto", "住宅地の1年の動き"], ["まちランキング", "/ranking", "人口の順位も"], ["実家・空き家", "/jikka/", "売る・片付ける前に"]]
    for fname, title, desc, fn, js in [
        ("sagasu.html", "その予算で、どの街に住める？｜関東329の街を地価公示から｜LIFE NOTE", "関東329の市区町村を、中古マンション・一戸建て・新築・土地の値段の目安（地価公示から）で、予算から選べます。",
         lambda: Y.sagasu(os.path.join(S, "sagasu.html"), REL0), "sg")]:
        try:
            d = fn()
            if d: write(fname, "/" + fname[:-5], title, home_cfg("/" + fname[:-5]), d, js, desc)
        except Exception as e:
            print("shin_kanto: 前のまま", fname, repr(e))
    # 実家・空き家ノート（入口と街ごと）
    try:
        jd = os.path.join(S, "jikka"); os.makedirs(os.path.join(S, "kyu", "jikka"), exist_ok=True)
        ti, de = Y.meta(os.path.join(jd, "index.html"))
        d = Y.jikka_index(os.path.join(jd, "index.html"), "川口市")
        if d: write("jikka/index.html", "/jikka/", ti, home_cfg("/jikka/"), d, "doc", de)
        n = 0
        for f in sorted(os.listdir(jd)):
            if not re.match(r"^[a-z]+-\d+\.html$", f): continue
            ti, de = Y.meta(os.path.join(jd, f))
            d = Y.jikka_town(os.path.join(jd, f), "LIFE NOTE")
            if d: write("jikka/" + f, "/jikka/" + f[:-5], ti, dict(home_cfg("/jikka/"), sell=Y.sell_cfg(1, Y.town_of(d), f[:-5])), d, "doc", de); n += 1
        print("jikka: 新しい形", n)
        sp = os.path.join(jd, "shindan", "index.html")
        if os.path.exists(sp):
            os.makedirs(os.path.join(S, "kyu", "jikka", "shindan"), exist_ok=True)
            ti, de = Y.meta(sp); d = Y.shindan(sp)
            if d: write("jikka/shindan/index.html", "/jikka/shindan/", ti, home_cfg("/jikka/"), d, "doc", de)
    except Exception as e:
        print("shin_kanto: 実家ノートは前のまま", repr(e))
    # 解体（入口・補助金ランキング・市ごと）と空き家の割合ランキング
    try:
        n = 0
        for f in sorted(os.listdir(S)):
            if not re.match(r"^kaitai(-[a-z]+)?\.html$", f): continue
            ti, de = Y.meta(os.path.join(S, f)); d = Y.kaitai(os.path.join(S, f))
            if d: write(f, "/" + f[:-5], ti, home_cfg("/kaitai"), d, "doc", de); n += 1
        print("kaitai: 新しい形", n)
        ti, de = Y.meta(os.path.join(S, "akiya-ranking.html"))
        d = Y.akiya(os.path.join(S, "akiya-ranking.html"), "関東", "川口市", [["実家・空き家ノート", "/jikka/", "街ごとの数字と順番"], ["解体の補助金", "/kaitai-ranking", "市ごとの上限"], ["地価ランキング", "/chika-kanto", "住宅地の1年の動き"], ["まちランキング", "/ranking", "人口の順位も"]])
        if d: write("akiya-ranking.html", "/akiya-ranking", ti, home_cfg("/akiya-ranking"), d, "rk", de)
    except Exception as e:
        print("shin_kanto: 解体・空き家は前のまま", repr(e))
    # 申し込み・リクエストと感想（入力と送る仕組みは前のまま）
    try:  # お得まとめ（関西と同じ入口）
        c = Y.kau_cfg("/otoku", "", "商品・宿へのリンクは広告（PR）です。"); c.pop("desc", None)
        write("otoku.html", "/otoku", "お得まとめ｜セール・値下がり・ふるさと納税・宿の入口｜LIFE NOTE", c, Y.otoku(), "doc", "セール・値下がりした物・ふるさと納税・宿。お得の入口をひとつにまとめました。")
    except Exception as e:
        print("shin_kanto: お得まとめは前のまま", repr(e))
    for f in ("moushikomi.html", "koe.html"):
        try:
            ti, de = Y.meta(os.path.join(S, f)); d = Y.form(os.path.join(S, f))
            if d: write(f, "/" + f[:-5], ti, home_cfg("/" + f[:-5]), d, "doc", de)
        except Exception as e:
            print("shin_kanto: 前のまま", f, repr(e))
    # 11/23 おでかけ1件のページ（/o/*）も新しい土台で（関西と同じ・shin_yari.spot）。前のページは site/kyu/o/ に残る
    try:
        od = os.path.join(S, "o"); os.makedirs(os.path.join(S, "kyu", "o"), exist_ok=True); n = 0
        oc = {"nav": [{"t": "開催中", "ic": "now", "href": "/odekake"}], "menu": {"k": "Odekake", "items": [["関東おでかけ", "/odekake", 1]]},
              "foot": "日程や料金は変わることがあります。出かける前に公式ページで確かめてください。<br>券・宿のリンクの一部は広告です。"}
        import copy as _cp
        for f in sorted(os.listdir(od)):
            if not re.match(r"^[0-9a-f]+\.html$", f): continue
            p_ = os.path.join(od, f); d = Y.spot(p_)
            if not d: continue
            ti, de = Y.meta(p_)
            write("o/" + f, "/o/" + f[:-5], ti, _cp.deepcopy(oc), d, "doc", de)
            Y.keep_head(p_, p_); n += 1
        print("o: 新しい形", n)
    except Exception as e:
        print("shin_kanto: おでかけ1件は前のまま", repr(e))
    # 11/23 開店・閉店の1店のページ（/kaiten/<日付>-<id>）も新しい土台で（関西と同じ・shin_yari.shop）
    try:
        kd = os.path.join(S, "kaiten"); os.makedirs(os.path.join(S, "kyu", "kaiten"), exist_ok=True); n = 0
        kc = {"nav": [{"t": "開店閉店", "ic": "now", "href": "/kaiten"}], "menu": {"k": "New Shops", "items": [["関東の開店・閉店", "/kaiten", 1]]},
              "foot": "日付・場所は各社の公式の発表をもとにしています。出かける前に公式の発表をご確認ください。"}
        import copy as _cp
        for f in sorted(os.listdir(kd)):
            if not re.match(r"^\d{8}-[0-9a-f]+\.html$", f): continue
            p_ = os.path.join(kd, f); d = Y.shop(p_)
            if not d: continue
            ti, de = Y.meta(p_)
            write("kaiten/" + f, "/kaiten/" + f[:-5], ti, _cp.deepcopy(kc), d, "doc", de)
            Y.keep_head(p_, p_); n += 1
        print("kaiten 1店: 新しい形", n)
    except Exception as e:
        print("shin_kanto: 開店閉店の1店は前のまま", repr(e))
    # 11/23 買いまわり 1,000円ぽっきり（kaimawari.py が作った前のページ → 新しい土台。前のページは site/kyu/kaimawari.html＝関西も読む）
    try:
        kp = os.path.join(S, "kaimawari.html")
        if os.path.exists(kp):
            kt = Y.old(kp); d = Y.kaimawari(kt)
            if d:
                de = "楽天の買いまわり用に、1,000〜1,199円・送料込み・レビュー1,000件以上・評価4.0以上の物だけを、ジャンルごとに集めました。ポイントの計算つき。"
                c = Y.kau_cfg("/kaimawari", "", "商品へのリンクは楽天アフィリエイトの広告（PR）です。"); c.pop("desc", None)
                write("kaimawari.html", "/kaimawari", "買いまわり 1,000円ぽっきり（送料込み）まとめ｜LIFE NOTE", c, d, "doc", de)
                Y.keep_head(None, kp, only_ld=True, text=kt)
                print("kaimawari: 新しい形")
    except Exception as e:
        print("shin_kanto: 買いまわりは前のまま", repr(e))


def main():
    IT = items()
    if len(IT) < 10:
        print("shin_kanto: おでかけが少ないので書き替えない", len(IT)); return
    base = {"nav": [{"t": "開催中", "ic": "now", "a": "now"}, {"t": "今週末", "ic": "we", "a": "we"}, {"t": "地図", "ic": "map", "a": "map"}, {"t": "泊まり", "ic": "inn", "href": "/tomari"}],
            "menu": {"k": "Odekake", "items": [["関東おでかけ", "/odekake"], ["イルミネーション", "/illumination"], ["紅葉", "/koyo"], ["いまから行ける", "/ima"], ["泊まり", "/tomari"], ["初詣", "/hatsumode"]]},
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
        import shin_kanto_lists as SL
        c = cfg("/ima"); c["nav"] = SL.ODE_NAV("/ima")
        write("ima.html", "/ima", "いまから行ける関東のおでかけ｜近い順・きょう開いている所｜LIFE NOTE", c,
              {"items": im, "icons": ICONS, "page": {"h1": "いまから行けるおでかけ", "sub": "きょう開いている所を、近い順に", "near": 1, "K": KINDS(im), "cnt": "か所", "seg": False,
                                                     "none": "この時間で行ける所は見つかりませんでした。「1時間半」「すべて」でもう少し遠くまで探せます。", "also": [a for a in SL.ALSO if a[1] != "/ima"],
                                                     "note": "かかる時間は直線距離から出した目安です（電車と歩きを合わせたおおよその時間）。本当の行き方は「行き方」から Google マップで。開いている時間は出かける前に公式で確かめてください。"}},
              "list", f"いる場所といまの時刻から、きょう開いている関東のおでかけ{len(im)}か所を近い順に並べます。30分・1時間・1時間半で行ける所がすぐ分かります。")

    # ---------- 11/23 関西と同じ：紅葉の都県・初詣・泊まり・まちランキング（scripts/shin_kanto_lists.py） ----------
    try:
        sys.path.insert(0, os.path.join(R, "scripts"))
        import shin_kanto_lists as SL
        SL.build(write, cfg, IT, il, ky, ICONS, KINDS, R, S, TD, PREF, FULL, SLUG)
    except Exception as e:
        print("shin_kanto: 初詣・泊まり・まちランキングは前のまま", repr(e))

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
            # 11/23 夜の見回り：日がまだ発表されていない店（fuzzy＝「2027年3月」）が日付の欄で 3/1 になっていた → 「3月予定（日は未発表）」と書く。期間限定の終わりも「〜12/13」の形に
            if x.get("fuzzy"):
                fz = x["fuzzy"]; it["d"] = re.sub(r"^\d{4}年", "", fz) + "予定（日は未発表）・" + lab; it["big"] = ""
                it["rows"] = [r for r in [["日", fz + "予定（日はまだ発表されていません）"], ["場所", x.get("pl") or x["p"]], ["時間", x.get("tm") or ""]] if r[1]]
            elif x.get("end"):
                _e = datetime.date.fromisoformat(x["end"]); it["rows"][0][1] = it["rows"][0][1].replace("〜" + x["end"], f"〜{_e.month}月{_e.day}日")
            if v: it.update({"im": v["img"], "cr": v["cr"], "cu": v.get("page", "")})
            kt.append(it)
        kt.reverse()
        if kt:
            cn = {k: sum(1 for x in kt if x["w"] == k) for k in ("soon", "done", "close")}
            c = cfg("/kaiten")
            c["nav"] = [{"t": "これから", "ic": "now", "a": "w=soon"}, {"t": "開いた", "ic": "we", "a": "w=done"}, {"t": "閉まる", "ic": "down", "a": "w=close"}, {"t": "保存", "ic": "star", "a": "fav"}]
            c["menu"] = {"k": "New Shops", "items": [["関東の開店・閉店", "/kaiten", 1]]}
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
                 "menu": {"k": "Shopping", "items": [["日用品の値段くらべ", "/okaimono", 1], ["ふるさと納税", "/furusato"], ["本当に安い？", "/nesage"], ["今までのおかいものの画面", "/kyu/okaimono"]]},
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
    ph = [x for x in sorted(now, key=lambda x: ((1 if (x.get("k") == "light" and not x.get("nt")) or (x.get("k") == "koyo" and not x.get("wm")) else 0), -(x.get("vb") or 0)//6, x["e"])) if x.get("im")]
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
    more = [["関東のイルミネーション", "/illumination"], ["関東の紅葉", "/koyo"], ["いまから行けるおでかけ", "/ima"], ["泊まりで行くおでかけ", "/tomari"],
            ["関東の初詣", "/hatsumode"], ["関東まちランキング", "/ranking"], ["実家・空き家", "/jikka/"], ["ふるさと納税", "/furusato"]]
    c = copy.deepcopy(base)
    c["nav"] = [{"t": "おでかけ", "ic": "now", "href": "/odekake"}, {"t": "家と土地", "ic": "find", "href": "/fudosan-list"}, {"t": "おかいもの", "ic": "yen", "href": "/okaimono"}, {"t": "地図", "ic": "map", "a": "map"}]
    c["menu"] = {"k": "Life Note", "items": [["トップ", "/", 1], ["おでかけ", "/odekake"], ["家と土地", "/fudosan-list"], ["おかいもの", "/okaimono"], ["開店・閉店", "/kaiten"]]}
    c["foot"] = "おでかけの券・宿と、おかいもののリンクには広告（PR）があります。"
    # 11/19 23:16 owner「表紙ほぼおでかけ」「Appleっぽくもない」→ 関西と同じ apple.com の形（cover2.js）。地図は表紙に置かない
    RK = {"koyo": 0, "flower": 1, "spot": 2, "animal": 3, "play": 4}
    def pick_ph(f, n):
        r, u = [], set()
        for x in sorted(now, key=lambda x: (RK.get(x.get("k"), 9), (1 if (x.get("k") == "light" and not x.get("nt")) or (x.get("k") == "koyo" and not x.get("wm")) else 0), -(x.get("vb") or 0)//6, x["e"])):
            if x.get("im") and f(x) and x["im"] not in u: r.append({k: x[k] for k in ("t", "p", "e", "im", "th", "o") if k in x}); u.add(x["im"])
            if len(r) >= n: break
        return r
    tw = []
    try:
        # 11/23 地価ランキングを新しい土台にしたので、上の3つは kyu/ に残した前のページから読む（表紙の「地価が1年で上がった街」が空だった）
        _cp = os.path.join(S, "kyu", "chika-kanto.html")
        ck = open(_cp if os.path.exists(_cp) else os.path.join(S, "chika-kanto.html"), encoding="utf-8").read()
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
    c["menu"] = {"k": "Life Note", "items": [["トップ", "/", 1], ["おでかけ", "/odekake"], ["家と土地", "/fudosan-list"], ["おかいもの", "/okaimono"], ["開店・閉店", "/kaiten"]]}
    write("index.html", "/", "LIFE NOTE（ライフノート）｜関東のおでかけと、家と土地の値段", c,
          {"od": {"n": len(now), "ph": hero}, "ie": {"n": towns, "tw": tw}, "kau": {"n": nkau, "ks": ks},
           "kai": {"n": sum(1 for x in ktl if x["w"] == "soon"), "x": ka}, "ko": ko,
           "ft": [["おでかけ", [["関東のおでかけ", "/odekake"], ["イルミネーション", "/illumination"], ["紅葉", "/koyo"], ["いまから行ける", "/ima"], ["泊まりで行く", "/tomari"], ["初詣", "/hatsumode"]]],
                  ["家と土地", [["家と土地の相場", "/fudosan-list"], ["地価ランキング", "/chika-kanto"], ["まちランキング", "/ranking"], ["家を売る前に", "/uru"], ["いくらで売れる？", "/ikura"], ["家を買いたい", "/sagasu"], ["実家・空き家ノート", "/jikka/"], ["3問でわかる実家の診断", "/jikka/shindan/"], ["解体・片付けの費用", "/kaitai"], ["解体の補助金", "/kaitai-ranking"], ["空き家が多い街", "/akiya-ranking"]]],
                  ["おかいもの", [["日用品の値段くらべ", "/okaimono"], ["値下がりした物", "/nesage"], ["ふるさと納税", "/furusato"], ["開店・閉店ニュース", "/kaiten"]]],
                  ["このサイト", [["相談・申し込み", "/moushikomi"], ["リクエスト・感想", "/koe"], ["プライバシーポリシー", "/privacy"]]]],
           "sns": [["Instagram", "https://www.instagram.com/usagichan_ai_si/"], ["Threads", "https://www.threads.com/@usagichan_ai_si"], ["X", "https://x.com/ai_usagichan"]]},
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
        c = {"nav": [{"t": "街をさがす", "ic": "find", "a": "find"}, {"t": "地価", "ic": "rank", "href": "/chika-kanto"}, {"t": "売りたい", "ic": "sell", "href": "/uru"}, {"t": "いくら？", "ic": "yen", "href": "/ikura"}],
             "menu": {"k": "Home & Land", "items": [["家と土地の相場", "/fudosan-list", 1], ["家を売る前に", "/uru"], ["いくらで売れる？", "/ikura"], ["実家・空き家", "/jikka/"], ["解体の費用と補助金", "/kaitai"], ["地価ランキング", "/chika-kanto"]]},
             "foot": "地価：国土交通省・各都県「令和8年地価公示」。人口・空き家：総務省統計局（国勢調査・住宅・土地統計調査）。<br>どれも街の平均で、1軒ずつの値段ではありません。「買いたい」のリンクは広告です（Yahoo!不動産）。"}
        import shin_yari as _Y; c["sell"] = _Y.sell_cfg(1)
        write("fudosan-list.html", "/fudosan-list", f"関東の家と土地の相場｜{len(out)}の街の地価と人口｜LIFE NOTE", c,
              {"towns": out, "pa": PA, "map": MAP, "pfull": PF, "pc": PC, "h1": "関東の家と土地の相場", "sub": f"{len(out)}の街の、地価の動きと人口・空き家",
               "upd": "2026年の地価公示・国勢調査（2025年）の数字", "ph": "横浜、よこはま"}, "ie",
              f"関東{len(out)}の市区町村の、住宅地の地価の動き（令和8年地価公示）と人口・空き家の割合を、街ごとにまとめました。都県の平均とも比べられます。")
    except Exception as e:
        print("shin_kanto: 家と土地は前のまま", repr(e))


def furu():
    """ふるさと納税・値下がりした物（関西と同じ furu.js）。11/19 owner「ふるさと押したら前のページ飛ぶ」"""
    NAVR = lambda first: first + [{"t": "おかいもの", "ic": "yen", "href": "/okaimono"}]
    MENU = lambda cur: {"k": "Shopping", "items": [[a, u] + ([1] if u == cur else []) for a, u in [["日用品の値段くらべ", "/okaimono"], ["ふるさと納税", "/furusato"], ["本当に安い？", "/nesage"], ["開店・閉店", "/kaiten"]]]}
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
    # 11/22「本当に安い？」：/nesage を作り替え（scripts/honto.py・site/shin/honto.js）。オーナー「見やすくて使いやすいなら任せる」
    try:
        import honto
        hd = honto.build()
        if hd and hd["n"] >= 30:
            json.dump(hd, open(os.path.join(R, "data", "honto.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))  # 関西 TOWN NOTE も同じ物を読む
            write("nesage.html", "/nesage", "本当に安い？｜セールの値段を11月1日からの記録でたしかめる（楽天の日用品）｜LIFE NOTE",
                  {"nav": [], "menu": MENU("/nesage"), "foot": FOOT}, hd, "honto",
                  f"楽天市場の日用品{hd['n']}品の値段を11月1日から毎日記録。ブラックフライデーなどセールの値段が本当に安いか、"
                  f"今が安い{hd['cnt']['a']}品・上げてから下げた{hd['cnt']['b']}品・いつもより高い{hd['cnt']['c']}品を、値段の動きのグラフでたしかめられます。")
    except Exception as e:
        print("shin_kanto: 本当に安い？は前のまま", repr(e))


if __name__ == "__main__":
    main()
