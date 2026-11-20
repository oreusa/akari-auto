"""11/20 owner「地図何とかならんかな？クオリティあげたい・大阪だけとか選べる方が使いやすい」→ おでかけの地図（新しい形）の形のファイルを作る。
市町村の形（townnotes/kansai.json・kanto.json の muni）から、府県の陸・府県のさかい・市町村のさかい・まわりの県・湖・町の名前を作る。
地図を開いた時だけ読む（ページを重くしない）。地形は変わらないので、作り直すのは形のファイルを変えた時だけ。
  関西: python3 tools/shin/mapgen.py kansai links/townnotes/kansai.json links/shin/map.json
  関東: python3 tools/shin/mapgen.py kanto  <akari>/site/townnotes/kanto.json <akari>/site/shin/map.json
湖（琵琶湖）は Natural Earth 10m lakes（パブリックドメイン）から写した点。"""
import json, sys, collections

REG, SRC, OUT = sys.argv[1:4]
if REG == "kansai":
    PJ = [134, 82.2, 0, 36, 100, 0]
    BIG = ["大阪市", "京都市", "神戸市", "奈良市", "大津市", "和歌山市", "堺市", "姫路市"]
else:
    PJ = [138.4, 81, 10, 37.15, 100, 27]
    BIG = ["横浜市", "川崎市", "さいたま市", "千葉市", "水戸市", "宇都宮市", "前橋市", "高崎市", "八王子市", "新宿区", "船橋市", "つくば市"]

# build.py・shin_kanto.py の proj と同じ（おでかけの xy と合わせる）。地図の画面でも「いまいる所」に使う
proj = lambda lon, lat: ((lon - PJ[0]) * PJ[1] + PJ[2], (PJ[3] - lat) * PJ[4] + PJ[5])

# 琵琶湖（Natural Earth 10m lakes "Biwa Ko"）
BIWA = [[136.221,35.385],[136.2489,35.3768],[136.2787,35.3647],[136.2766,35.3368],[136.2528,35.2841],[136.2398,35.2708],[136.1633,35.2258],[136.105,35.2055],[136.0779,35.1905],[136.0603,35.1646],[136.0785,35.1587],[136.0738,35.1493],[136.0564,35.1404],[136.0364,35.1366],[136.0185,35.1354],[135.9999,35.1319],[135.9831,35.1254],[135.9708,35.116],[135.9646,35.1233],[135.9572,35.1036],[135.9531,35.0783],[135.9452,35.0568],[135.9266,35.0477],[135.9193,35.0389],[135.9193,34.9953],[135.9095,34.9788],[135.8984,34.98],[135.8848,34.9903],[135.8733,35.0059],[135.8683,35.0236],[135.8736,35.0389],[135.9216,35.1051],[135.9281,35.1192],[135.9322,35.1713],[135.9369,35.1863],[135.9572,35.219],[136.0164,35.2667],[136.0261,35.2773],[136.0341,35.2923],[136.0679,35.3076],[136.0744,35.3215],[136.0429,35.3865],[136.0432,35.3977],[136.0514,35.4109],[136.0585,35.4365],[136.0709,35.4542],[136.095,35.4442],[136.1135,35.4766],[136.1224,35.4866],[136.1265,35.4716],[136.1283,35.4557],[136.1347,35.4433],[136.1527,35.438],[136.1574,35.4454],[136.1603,35.4625],[136.1633,35.4995],[136.1777,35.4951],[136.1898,35.4869],[136.1968,35.4748],[136.1974,35.4586],[136.1974,35.466],[136.1989,35.4351],[136.2054,35.4062],[136.221,35.385]]

k = json.load(open(SRC, encoding="utf-8"))
P = lambda c: tuple(round(v, 1) for v in proj(c[0], c[1]))
fmt = lambda pts: "M" + "L".join(f"{x:g} {y:g}" for x, y in pts)

def rings(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        for ring in poly:
            s = []
            for c in ring:
                p = P(c)
                if not s or s[-1] != p: s.append(p)
            if len(s) >= 4: yield s

land = collections.defaultdict(list)
segs = collections.defaultdict(list)
for f in k["muni"]["features"]:
    pf = f["properties"]["p"]
    for s in rings(f["geometry"]):
        land[pf].append(fmt(s) + "Z")
        for a, b in zip(s, s[1:]):
            if a != b: segs[frozenset((a, b))].append(pf)

def chain(edges):
    """線のかけらをつないで、なるべく長い線にする（ファイルを小さく）"""
    adj = collections.defaultdict(list)
    for e in edges:
        a, b = tuple(e)
        adj[a].append(b); adj[b].append(a)
    used, out = set(), []
    def walk(a):
        line = [a]
        while True:
            nx = [b for b in adj[line[-1]] if frozenset((line[-1], b)) not in used]
            if not nx: return line
            used.add(frozenset((line[-1], nx[0]))); line.append(nx[0])
    starts = [p for p in adj if len(adj[p]) != 2] + list(adj)
    for p in starts:
        while any(frozenset((p, b)) not in used for b in adj[p]):
            l = walk(p)
            if len(l) > 1: out.append(fmt(l))
    return "".join(out)

mb = [e for e, v in segs.items() if len(v) >= 2 and len(set(v)) == 1]
pb = [e for e, v in segs.items() if len(set(v)) >= 2]
# 府県の外まわり（海岸とまわりの県とのさかい）＝その府県だけの線
ob = collections.defaultdict(list)
for e, v in segs.items():
    if len(v) == 1: ob[v[0]].append(e)

bb = {}
for pf, ps in land.items():
    xs, ys = [], []
    for f in k["muni"]["features"]:
        if f["properties"]["p"] != pf: continue
        for s in rings(f["geometry"]):
            xs += [p[0] for p in s]; ys += [p[1] for p in s]
    bb[pf] = [round(min(xs), 1), round(min(ys), 1), round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)]

nb = []
for f in k["nb"]["features"]:
    nb.append("".join(fmt(s) + "Z" for s in rings(f["geometry"])))

lab = []
for f in k["lab"]["features"]:
    pr = f["properties"]; n = pr["n"]
    r = 1 if n in BIG else 2 if n.endswith("市") or n.endswith("区") else 3
    x, y = P(f["geometry"]["coordinates"])
    lab.append([n, x, y, pr["p"], r])

out = {"pj": PJ, "land": {p: "".join(v) for p, v in land.items()}, "mb": chain(mb), "pb": chain(pb),
       "ob": {p: chain(v) for p, v in ob.items()},
       "ol": {p: chain(ob[p] + [e for e, v in segs.items() if len(set(v)) >= 2 and p in v]) for p in land}, "nb": nb, "bb": bb, "lab": lab,
       "lake": [fmt([P(c) for c in BIWA]) + "Z"] if REG == "kansai" else []}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(OUT, len(json.dumps(out, ensure_ascii=False)) // 1024, "KB", {p: len(v) for p, v in land.items()})
