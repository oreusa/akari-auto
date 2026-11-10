"""11/10 夜 #150「高尾山のピンがずれ、宿の距離にもずれが移った」→ おでかけの場所（緯度・経度）が、書いてある市区町村・府県の形から外れていたら赤にする。
月（TOWN：links）と燈（LIFE：site）で同じファイル。ngcheck.py から呼ぶ（ネットは使わない）。
- 形は townnotes/kansai.json・kanto.json の muni（市区町村）と pref（府県）。形は少し粗いので、境目から 1.5km までは許す。
- TOWN：townnotes/geo.json（カード名→場所）と index.html のカードの data-map（「会場 市区町村」）。
- LIFE：data/townnotes-geo.json（「都県｜探す言葉」→場所）。探す言葉の最後の市区町村、無ければ都県で見る。
  宿の距離（data/kanto-yado.json の ll）が地図の場所と 0.5km 以上ちがう物は「！」で知らせる（楽天の回が落ちた時に公開まで止めないよう、赤にはしない）。
同じ市の中でのずれ（例：同じ八王子市の中で10km）は、形では見つけられない。"""
import json, math, os, re, html

TOL_KM = 1.5
PF = {"大阪": "大阪府", "京都": "京都府", "兵庫": "兵庫県", "奈良": "奈良県", "滋賀": "滋賀県", "和歌山": "和歌山県",
      "東京": "東京都", "神奈川": "神奈川県", "埼玉": "埼玉県", "千葉": "千葉県", "茨城": "茨城県", "栃木": "栃木県", "群馬": "群馬県"}


def _rings(g):
    if g["type"] == "Polygon":
        return [g["coordinates"]]
    if g["type"] == "MultiPolygon":
        return g["coordinates"]
    return []


def _inside(lon, lat, poly):
    def inr(r):
        c = False
        j = len(r) - 1
        for i in range(len(r)):
            xi, yi = r[i][0], r[i][1]
            xj, yj = r[j][0], r[j][1]
            if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi:
                c = not c
            j = i
        return c
    return inr(poly[0]) and not any(inr(h) for h in poly[1:])


def _km_to_edge(lon, lat, poly):
    kx = 111.32 * math.cos(math.radians(lat))
    best = 1e9
    for r in poly:
        for (x1, y1), (x2, y2) in zip(r, r[1:]):
            ax, ay = (x1 - lon) * kx, (y1 - lat) * 110.57
            bx, by = (x2 - lon) * kx, (y2 - lat) * 110.57
            dx, dy = bx - ax, by - ay
            t = max(0, min(1, -(ax * dx + ay * dy) / ((dx * dx + dy * dy) or 1e-12)))
            best = min(best, math.hypot(ax + t * dx, ay + t * dy))
    return best


def _near(lat, lon, feats):
    """その形の中、または境目から TOL_KM 以内なら True"""
    for f in feats:
        for poly in _rings(f["geometry"]):
            if _inside(lon, lat, poly) or _km_to_edge(lon, lat, poly) <= TOL_KM:
                return True
    return False


def _where(lat, lon, munis):
    for f in munis:
        for poly in _rings(f["geometry"]):
            if _inside(lon, lat, poly):
                return f["properties"]["n"]
    return "（どの市区町村にも入らない）"


def _city(s, names):
    """文字の中の市区町村名（形の名前にある物）を後ろから探す。政令市は区まで、無ければ市。"""
    s = re.sub(r"\s+", " ", s)
    best = None
    for n in names:
        i = s.rfind(n)
        if i >= 0 and (best is None or i + len(n) > best[0] or (i + len(n) == best[0] and len(n) > len(best[1]))):
            best = (i + len(n), n)
    return best[1] if best else None


def _km(a, b):
    kx = 111.32 * math.cos(math.radians(a[0]))
    return math.hypot((a[1] - b[1]) * kx, (a[0] - b[0]) * 110.57)


def check(root):
    bad = []
    shp = next((p for p in [os.path.join(root, "townnotes", "kansai.json"), os.path.join(root, "townnotes", "kanto.json")] if os.path.exists(p)), None)
    if not shp:
        return bad
    S = json.load(open(shp, encoding="utf-8"))
    munis = S["muni"]["features"]
    prefs = S["pref"]["features"]
    by_name = {}
    for f in munis:
        by_name.setdefault(f["properties"]["n"], []).append(f)
        # 政令市の区（大阪市北区）は「大阪市」でも引けるように
        m = re.match(r"(.+?市)(.+区)$", f["properties"]["n"])
        if m:
            by_name.setdefault(m.group(1), []).append(f)
    by_pref = {}
    for f in prefs:
        p = f["properties"].get("p") or f["properties"].get("n", "")
        by_pref.setdefault(p, []).append(f)
    names = sorted(by_name, key=len, reverse=True)
    items = []  # (表示名, pref, 文字, lat, lon)
    if shp.endswith("kansai.json"):
        G = json.load(open(os.path.join(root, "townnotes", "geo.json"), encoding="utf-8"))
        t = open(os.path.join(root, "index.html"), encoding="utf-8").read()
        for a in re.finditer(r'<a class="card"([^>]*)>.*?class="t">(.*?)</div>', t, re.S):
            at = dict(re.findall(r'(data-[\w-]+)="([^"]*)"', a.group(1)))
            nm = html.unescape(re.sub(r"<[^>]+>", "", a.group(2))).strip()
            g = G.get(nm)
            if g and g[0] is not None:
                items.append((nm, at.get("data-pref", ""), html.unescape(at.get("data-map", "")), g[0], g[1]))
    else:
        G = json.load(open(os.path.join(root, "..", "data", "townnotes-geo.json"), encoding="utf-8"))
        for k, g in G.items():
            if not g or g[0] is None or "｜" not in k:
                continue
            p, q = k.split("｜", 1)
            items.append((k, p, q, g[0], g[1]))
        # 宿の距離が、いまの地図の場所で計算されているか
        yf = os.path.join(root, "..", "data", "kanto-yado.json")
        of = os.path.join(root, "townnotes", "geo.json")
        if os.path.exists(yf) and os.path.exists(of):
            Y = json.load(open(yf, encoding="utf-8"))
            O = json.load(open(of, encoding="utf-8"))
            for nm, y in Y.items():
                o = O.get(re.sub(r"\s+", "", nm)) or O.get(nm)
                if o and o[0] is not None and y.get("ll") and _km(y["ll"], o) > 0.5:
                    print(f"！ 宿の距離が古い場所で計算されている（次の宿の回で直る。止めはしない）：{nm}（宿 {y['ll'][0]},{y['ll'][1]} ／ 地図 {o[0]},{o[1]}）")
    for nm, p, q, lat, lon in items:
        c = _city(q, names)
        if c:
            if not _near(lat, lon, by_name[c]):
                bad.append(f"場所が {c} の外：{nm}（{lat},{lon} は {_where(lat, lon, munis)}）")
        elif p in by_pref:
            if not _near(lat, lon, by_pref[p]):
                bad.append(f"場所が {PF.get(p, p)} の外：{nm}（{lat},{lon}）")
    return bad


if __name__ == "__main__":
    import sys
    b = check(sys.argv[1])
    for x in b:
        print("×", x)
    print(f"geocheck: {len(b)} 件" if b else "geocheck: なし")
