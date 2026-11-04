"""1件ページ（/o/）の場所の地図。おでかけリストの TOWN NOTE 地図と同じ絵（府県のパステル色・白いふち・影・名物の絵・明朝の府県名）で、
その府県を大きく出し、会場の市区町村を濃く、会場にしずく形のピンを立てる。11/4 オーナー「僕らのオシャレな地図はどうした」。
燈版（11/4 月がコピー）：形は site/townnotes/kanto.json、色と名物の絵は scripts/region-kanto.js（月の tools/townnotes と同じ物）、
会場の場所は data/townnotes-geo.json（キーは「都県｜地図の検索語」）。会場の市区町村は、ピンが入っている形で決める。"""
import json, re, html, os

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = json.load(open(os.path.join(D, "site/townnotes/kanto.json"), encoding="utf-8"))
RJ = open(os.path.join(D, "scripts/region-kanto.js"), encoding="utf-8").read()
_g = os.path.join(D, "data/townnotes-geo.json")
GEO = json.load(open(_g, encoding="utf-8")) if os.path.exists(_g) else {}


def _obj(name):
    m = re.search(name + r":\{(.*?)\}", RJ)
    return dict(re.findall(r'"([^"]+)":"(#[0-9A-Fa-f]{6}|[A-Z]+)"', m.group(1)))


PC, FILL, DEEP, LIGHT, EN = _obj("pc"), _obj("fill"), _obj("deep"), _obj("light"), _obj("en")
LP = {k: (float(a), float(b)) for k, a, b in re.findall(r'"([^"]+)":\[([\d.]+),([\d.]+)\]', re.search(r"lp:\{(.*?)\}", RJ).group(1))}
ICON = {}
for p, x, y, n, s in re.findall(r'"([^"]+)":\{at:\[([\d.]+),([\d.]+)\],n:"([^"]*)",s:\'(.*?)\'\}', RJ):
    ICON[p] = (float(x), float(y), n, s)
PROJ = [float(x) for x in re.search(r"proj:\[([\d.,]+)\]", RJ).group(1).split(",")]


def P(lon, lat): return ((lon - PROJ[0]) * PROJ[1], (PROJ[2] - lat) * 100)


def rings(g):
    return g["coordinates"] if g["type"] == "Polygon" else [r for poly in g["coordinates"] for r in poly]


def mix(h, a):  # 府県の色を白に寄せる（a=白の割合）
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(x + (255 - x) * a) for x in (r, g, b))


def path(g, tol=0.0):
    out = []
    for r in rings(g):
        pts = []
        for c in r:  # 近すぎる点は省く（ページを軽く）
            q = P(*c)
            if not pts or abs(q[0] - pts[-1][0]) + abs(q[1] - pts[-1][1]) >= tol: pts.append(q)
        if len(pts) < 3: continue
        out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(out)


def inside(x, y, g):
    hit = False
    for r in rings(g):
        j = len(r) - 1
        for i in range(len(r)):
            xi, yi = r[i]; xj, yj = r[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi: hit = not hit
            j = i
    return hit


def where(title, city, pref):
    """会場の経度・緯度。燈は title に「地図の検索語」を渡す。"""
    g = GEO.get(f"{pref}｜{title}")
    if g and g[0]: return g[1], g[0], True
    for f in K["lab"]["features"]:
        pr = f["properties"]
        if pr.get("p") == pref and pr.get("n") and pr["n"] in city:
            return f["geometry"]["coordinates"][0], f["geometry"]["coordinates"][1], False
    return None


# 11/4 オーナーが選んだ「絵入りしずく」：ピンの頭に、カードと同じ絵（cardmark.js の絵と見分け方をそのまま読む）
_CM = None
def _cm():
    global _CM
    if _CM is None:
        try:
            js = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../site/assets/cardmark.js"), encoding="utf-8").read()
            a = js.index("var R="); rb = js[a:js.index("];", a) + 2]
            R = [(re.compile(p, re.I if fl else 0), k) for p, fl, k in re.findall(r"\[/(.*?)/(i?),'(\w+)'\]", rb)]
            b = js.index("var I={"); ib = js[b:js.index("};", b)]
            I = dict(re.findall(r"^(\w+):'(.*?)',?$", ib, re.M))
            _CM = (R, I)
        except Exception:
            _CM = ([], {})
    return _CM
def pin_icon(title, c):
    R, I = _cm()
    k = next((k for r, k in R if r.search(title or "")), "spot")
    svg = I.get(k) or I.get("spot", "")
    if not svg:
        return '<circle class="nd" cx="0" cy="-22" r="3.4" fill="' + c + '"/>'
    return ('<g class="ni" transform="translate(-6.6 -28.6) scale(.55)" fill="none" stroke="' + c +
            '" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">' + svg + '</g>')

def render(pref, title, city, label):
    if pref not in PC: return ""
    pf = [f for f in K["pref"]["features"] if f["properties"]["p"] == pref]
    xs, ys = [], []
    for f in pf:
        for r in rings(f["geometry"]):
            for c in r:
                x, y = P(*c); xs.append(x); ys.append(y)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = x1 - x0, y1 - y0
    # 横:縦 = 1:0.86（リストの地図と同じ）に合わせて、まわりに少し余白
    W = max(w, h / .86) * 1.16; H = W * .86
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    vx, vy = cx - W / 2, cy - H / 2
    sw = W / 340  # 画面の1pxぶん
    loc = where(title, city, pref)
    hit = None
    if loc:
        lx, ly = P(loc[0], loc[1])
    tw = re.sub(r"^(大阪府|京都府|兵庫県|奈良県|滋賀県|和歌山県)", "", city)
    tw = re.sub(r"ほか$", "", tw)
    out = [f'<svg viewBox="{vx:.1f} {vy:.1f} {W:.1f} {H:.1f}" role="img" aria-label="{html.escape(pref)}の地図。{html.escape(label)}の場所">',
           f'<rect x="{vx:.1f}" y="{vy:.1f}" width="{W:.1f}" height="{H:.1f}" fill="#EEF6F9"/>']
    # まわり（ほかの府県・関西の外）はうすく
    for f in K["nb"]["features"]:
        out.append(f'<path d="{path(f["geometry"], 2 * sw)}" fill="#F4F2EF" stroke="#fff" stroke-width="{1.2 * sw:.2f}"/>')
    for f in K["pref"]["features"]:
        q = f["properties"]["p"]
        if q == pref: continue
        out.append(f'<path d="{path(f["geometry"], 2 * sw)}" fill="{FILL[q]}" opacity=".45" stroke="#fff" stroke-width="{1.2 * sw:.2f}"/>')
    # その府県：影 → 市区町村（会場の所は濃く）→ 府県のふち
    shp = "".join(path(f["geometry"], .8 * sw) for f in pf)
    out.append(f'<path d="{shp}" fill="rgba(120,88,58,.18)" transform="translate({1.6 * sw:.2f} {2.6 * sw:.2f})"/>')
    for f in K["muni"]["features"]:
        pr = f["properties"]
        if pr["p"] != pref: continue
        on = bool(loc) and inside(loc[0], loc[1], f["geometry"])
        out.append(f'<path d="{path(f["geometry"], .8 * sw)}" fill="{mix(PC[pref], .45) if on else FILL[pref]}" stroke="#fff" stroke-width="{1.1 * sw:.2f}" stroke-linejoin="round"/>')
    out.append(f'<path d="{shp}" fill="none" stroke="#fff" stroke-width="{2.2 * sw:.2f}" stroke-linejoin="round"/>')
    # 名物の絵（その府県の物だけ）と府県名
    if pref in ICON:
        ix, iy, n, s = ICON[pref]; qx, qy = P(ix, iy); k = 34 / 40 * sw
        out.append(f'<g transform="translate({qx - 20 * k:.1f} {qy - 20 * k:.1f}) scale({k:.3f})" style="filter:drop-shadow(0 1.5px 0 rgba(255,255,255,.9)) drop-shadow(0 2px 2px rgba(80,60,40,.18))">'
                   f'<g fill="none" stroke="{PC[pref]}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">{s}</g><title>{html.escape(n)}</title></g>')
    if pref in LP:
        px_, py_ = P(*LP[pref])
        # 府県名は地図の左上に（会場のピンとぶつからないように）
        px_, py_ = vx + 14 * sw, vy + 22 * sw
        out.append(f'<text x="{px_:.1f}" y="{py_:.1f}" style="font-family:\'Shippori Mincho\',serif;font-weight:600;font-size:{17 * sw:.2f}px;letter-spacing:.16em" fill="#2B2622">{html.escape(pref)}</text>'
                   f'<text x="{px_:.1f}" y="{py_ + 15 * sw:.1f}" style="font-family:Jost,sans-serif;font-weight:400;font-size:{8.5 * sw:.2f}px;letter-spacing:.32em" fill="{PC[pref]}">{EN.get(pref, "")}</text>')
    if loc:
        k = sw
        out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{13 * k:.2f}" fill="{PC[pref]}" opacity=".18"/>'
                   f'<g class="neo" style="color:{PC[pref]};--nl:{_mx(PC[pref], "#ffffff", .5)}" transform="translate({lx:.1f} {ly:.1f}) scale({k:.3f})"><ellipse class="nsh" cx="0" cy="1" rx="6" ry="2.2" fill="#2B2622" opacity=".22"/>'
                   # 11/4 オーナーが20案から選んだ「ネオン」：線だけのしずく。昼は白地に色の線、夜は明るい線が光る
                   f'<path class="nb" d="M0 0C-3-7-12-12-12-22a12 12 0 0 1 24 0C12-12 3-7 0 0Z" fill="#fff" stroke="{PC[pref]}" stroke-width="2.4" stroke-linejoin="round"/>'
                   + pin_icon(title, PC[pref]) + '</g>')
        # 会場の名前の札（白い角丸・影）。右に入らなければ左へ
        t = label if len(label) <= 14 else label[:13] + "…"
        bw = (12 * len(t) + 22) * sw; bh = 26 * sw
        bx = lx + 16 * sw
        if bx + bw > vx + W - 6 * sw: bx = lx - 16 * sw - bw
        by = ly - 30 * sw - bh / 2
        if by < vy + 4 * sw or (bx < vx + 130 * sw and by < vy + 52 * sw): by = ly + 10 * sw  # 上の府県名とぶつかる時はピンの下へ
        out.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{bh / 2:.1f}" fill="#fff" style="filter:drop-shadow(0 1px 2px rgba(60,40,20,.12)) drop-shadow(0 3px 8px rgba(60,40,20,.12))"/>'
                   f'<text x="{bx + bw / 2:.1f}" y="{by + bh / 2:.1f}" text-anchor="middle" dominant-baseline="central" style="font-family:\'Zen Kaku Gothic New\',sans-serif;font-weight:700;font-size:{12 * sw:.2f}px;letter-spacing:.04em" fill="#3A2F28">{html.escape(t)}</text>')
    out.append("</svg>")
    return "".join(out)


def _mx(a, b, w):  # a を w、b を 1-w で混ぜる
    x = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; y = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join("%02x" % round(x[k] * w + y[k] * (1 - w)) for k in range(3))


def night_css():
    """11/4 夜は地図だけ反転を打ち消し、夜の地図（月あかり）と同じ紺の色で描く"""
    c = [
         'html.night .tmap svg{filter:invert(1) hue-rotate(180deg)}',
         'html.night .tmap svg>rect:first-of-type{fill:#141A30}',
         'html.night .tmap path[fill="#F4F2EF"]{fill:#1F2744}',
         'html.night .tmap path[opacity=".45"]{fill:#2A3358}',
         'html.night .tmap text[fill="#2B2622"]{fill:#fff}',
         'html.night .tmap rect[rx]{fill:#2A3358}html.night .tmap text[fill="#3A2F28"]{fill:#fff}',
         'html.night .tmap .neo{filter:drop-shadow(0 0 1.5px currentColor) drop-shadow(0 0 4px currentColor)}html.night .tmap .neo .nb{fill:#1A2140;stroke:var(--nl)}html.night .tmap .neo .ni{stroke:var(--nl)}html.night .tmap .neo .nd{fill:var(--nl)}html.night .tmap .neo .nsh{display:none}']
    for p, pc in PC.items():
        if p in FILL:
            c.append('html.night .tmap path[fill="%s"]:not([opacity]){fill:%s}' % (FILL[p], _mx(pc, "#2B3459", .25)))
        c.append('html.night .tmap path[fill="%s"]{fill:%s}' % (mix(pc, .45), _mx(pc, "#4A558A", .55)))
    return "".join(c)
