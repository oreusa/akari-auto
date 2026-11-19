"""11/19 owner「全部！」「他ページもぜんぶ変えれたら教えて」→ 関東（LIFE NOTE）の表紙・おでかけ・都県のおでかけも、関西（TOWN NOTE）と同じ新しい土台で作る。
土台（site/shin/shin.css・shin.js・odekake.js・cover.js・list.js）は月の repo（usagi-fudosan-media links/shin）の写し。地域の違いは CFG.reg（名前・都県・色・地図・ロゴ）。
中身：data/page-spots.json（HPに載せるおでかけ）。公開の回（page.yml）では、リンクの確かめを通った物（site/odekake.html に載った物）だけにする。
写真：site/assets/mihon.json・phh.json。地図の場所：data/townnotes-geo.json。種類：site/assets/cardmark.js。
出す所：site/index.html・site/odekake.html・site/odekake-<都県>.html を新しい形に書き替える（前の物は site/kyu/ に残す）。
page.yml の最後の方（投稿の画像を撮った後・skin_bake の前）で動かす。python3 scripts/shin_kanto.py"""
import os, re, json, html, hashlib, datetime, shutil

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
       "pc": PC, "fl": FL, "lb": LB, "sl": SLUG, "vb": "10 15 200 250"}


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
    write("index.html", "/", "LIFE NOTE（ライフノート）｜関東のおでかけと、家と土地の値段", c,
          {"h1": "関東のおでかけと、家と土地", "sub": "東京・神奈川・埼玉・千葉・茨城・栃木・群馬を、公式の発表と数字で", "pc": pc, "top": top, "go": [g for g in go], "more": more, "map": MAP,
           "sns": [["インスタ", "https://www.instagram.com/usagichan_ai_si/"], ["Threads", "https://www.threads.com/@usagichan_ai_si"], ["X", "https://x.com/ai_usagichan"]]},
          "cover", "関東のくらしで見つけたことを、ノートにまとめています。開催中のおでかけ・イベント、街の家と土地の値段、日用品の値段くらべ、開店・閉店を、公式の発表と数字で。")


if __name__ == "__main__":
    main()
