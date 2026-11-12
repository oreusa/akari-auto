"""関東不動産リスト（11/7 オーナー「新しい燈の不動産hpは作りは全て月と同じだからね。ミスがないように」）。
月の関西不動産リスト（usagi-fudosan-media の tools/fudosan_list/towns.py と make.py）と同じ作り・同じ見た目で、地域と数字だけ関東にする。

元の数字: data/kanto_chika/*.csv（名前,R7,R8,平均価格。329の市区町村。令和7・8年地価公示の住宅地の対前年平均変動率）と sources.json（出典・のせていない町村）。
読み: data/kanto_chika/kana.json（Code for FUKUI localgovjp の citykana。月の kana.json と同じ作り方）。
地図: site/townnotes/kanto.json（月の kansai.json と同じ形）。
リストの型: scripts/fudosan_kanto_base.html（月の links/fudosan-list.html からカードだけ外した物。CSS・タブ・絞り込み・街で探す・地図・下のバーは月のまま）。
         見た目の CSS は site/assets/fv2.css（月の links/assets/v2.css と同じ物。燈の v2.css はおでかけリスト用で中身が違う）。

出力（site/ の中。page.yml で lifenote.py・spot_pages.py のあと、pwa.py の前に毎回作る）:
  /machi/<id>        街ごとのページ（tokyo-01 …）
  /chika-kanto       関東 地価ランキング（7都県のタブ）
  /assets/towns.json 街で探す・地図・くらべる・入口の検索用
  /fudosan-list      関東不動産リスト
  sitemap.xml に足す
使い方: python3 scripts/fudosan_kanto.py
"""
import html, json, math, os, re

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "site")
D = os.path.join(R, "data", "kanto_chika")
E = html.escape
BASE = os.environ.get("LIFE_BASE") or "https://usagi-life-notes.pages.dev"
# 月は検索に出すかを --live で分けていた。関東は 11/7 の頼みで最初から検索に出す（False にすると noindex の見本になる）
LIVE = True
TODAY = "2026年11月7日"
DATE = "2026-11-07"
# 共通の部品の番号（lifenote.py の VER と同じ物を使う）
VER = {"menu.js": 21, "v2sub.js": 10, "night.js": 15}
_m = re.search(r"VER = (\{[^}]*\})", open(os.path.join(R, "scripts", "lifenote.py"), encoding="utf-8").read())
if _m:
    VER.update(json.loads(_m.group(1)))

# 都県の色は燈の page.py・lifenote_top.py と同じ
PC = {"東京": "#4F86C6", "神奈川": "#3FA3B5", "埼玉": "#E09A3E", "千葉": "#D9775A", "茨城": "#5FA06A", "栃木": "#D2697E", "群馬": "#9C7BB8"}
EN = {"東京": "TOKYO", "神奈川": "KANAGAWA", "埼玉": "SAITAMA", "千葉": "CHIBA", "茨城": "IBARAKI", "栃木": "TOCHIGI", "群馬": "GUNMA"}
SRC = json.load(open(os.path.join(D, "sources.json"), encoding="utf-8"))
# (都県, csv, 英字, 色, 出典の名前, 出典URL, 都県の言い方, sources の行)
PREFS = [(s["p"], s["csv"], EN[s["p"]], PC[s["p"]], s["src"], s["url"], s["pfull"], s) for s in SRC]
PI = {p[0]: p for p in PREFS}
ORDER = [p[0] for p in PREFS]
# 政令市の区は、市の中だけを大きく描く（月の 大阪市・堺市・京都市・神戸市 と同じ）。東京23区は区部だけを描く
CITY_RE = r"^(横浜市|川崎市|相模原市|さいたま市|千葉市)"

K = json.load(open(os.path.join(S, "townnotes", "kanto.json"), encoding="utf-8"))


def full(pr):
    c = pr.get("c") or ""
    return pr["n"] if c.endswith("郡") or not c else c + pr["n"]


LAB = {(f["properties"]["p"], full(f["properties"])): f["geometry"]["coordinates"] for f in K["lab"]["features"]}
SHAPE = {}
for f in K["muni"]["features"]:
    SHAPE.setdefault((f["properties"]["p"], full(f["properties"])), []).append(f["geometry"])


def ku23(pf, n):
    return pf == "東京" and n.endswith("区")


def city_of(pf, n):
    m = re.match(CITY_RE, n)
    if m:
        return m.group(1)
    return "東京23区" if ku23(pf, n) else ""


# ---- 数字を読む
towns = []
for pf, fn, en, col, sname, surl, pfull, s in PREFS:
    rows = [l.strip().split(",") for l in open(os.path.join(D, fn + ".csv"), encoding="utf-8") if l.strip()]
    for i, r in enumerate(rows):
        name = r[0]
        r7 = float(r[1]) if r[1] != "" else None
        r8 = float(r[2])
        price = int(r[3]) if len(r) > 3 and r[3] else None
        ll = LAB.get((pf, name))
        assert ll and (pf, name) in SHAPE, ("地図に無い名前", pf, name)
        towns.append({"id": f"{fn}-{i + 1:02d}", "p": pf, "n": name, "r7": r7, "r8": r8, "price": price, "lon": ll[0], "lat": ll[1]})
assert len({t["n"] for t in towns}) == len(towns), "同じ名前の街が2つある"

# 都県ごとの順位（同じ数字は同じ順位）
for pf in PI:
    ts = sorted([t for t in towns if t["p"] == pf], key=lambda t: -t["r8"])
    prev, pr = None, 0
    for n, t in enumerate(ts, 1):
        if t["r8"] != prev:
            pr = n
        prev = t["r8"]
        t["rank"], t["of"] = pr, len(ts)
ts = sorted(towns, key=lambda t: -t["r8"])
prev, pr = None, 0
for n, t in enumerate(ts, 1):
    if t["r8"] != prev:
        pr = n
    prev = t["r8"]
    t["krank"] = pr


def pct(v):
    if v is None:
        return "―"
    return ("+" if v > 0 else "−" if v < 0 else "±") + f"{abs(v):.1f}%"


def short(n):
    """検索用の短い名前（横浜市西区→西区）"""
    return re.sub(CITY_RE, "", n)


def unit(pf):
    return "区市町村" if pf == "東京" else "市区町村" if any(re.match(CITY_RE, t["n"]) for t in towns if t["p"] == pf) else "市町村"


# ---- リストのカード（地価のタブ）：CSV の数字だけで作る。都県ごとに上がり幅の1〜3位。出典は都県の公式資料
def facts():
    out = []
    for pf, fn, en, col, sname, surl, pfull, s in PREFS:
        ts = sorted([t for t in towns if t["p"] == pf], key=lambda t: (-t["r8"], towns.index(t)))
        a, b, c = ts[0], ts[1], ts[2]
        tie = [t for t in ts if t["r8"] == a["r8"]]
        head = "1位 " + "・".join(t["n"] for t in tie[:3]) + pct(a["r8"])
        # 2位・3位（同じ数字の街はまとめて書く）
        grp = []
        for t in ts:
            if t["r8"] == a["r8"]:
                continue
            if grp and grp[-1][0]["r8"] == t["r8"]:
                grp[-1].append(t)
            elif len(grp) < 2 and (not grp or grp[-1][0]["rank"] + len(grp[-1]) <= 3):
                grp.append([t])
        m = "、".join(f"{g[0]['rank']}位は" + "・".join(x["n"] for x in g[:3]) + f"の{pct(g[0]['r8'])}" for g in grp) + "でした。"
        out.append({"pref": pf, "tab": "chika", "date": DATE, "src": f"{pfull} 令和8年地価公示", "url": surl,
                    "t": f"{head}　{pfull}{len(ts)}{unit(pf)}の住宅地", "m": m, "u": unit(pf)})
    return out


FACTS = facts()


def related(t):
    """月と同じ：この街の名前が出てくるカード"""
    s = short(t["n"])
    out = []
    for o in FACTS:
        if o["pref"] != t["p"]:
            continue
        if re.search(r"(^|[ 　・は])" + re.escape(t["n"]) + r"([+−±の]|$)", o["t"] + " " + o["m"]):
            out.append(o)
    return out[:4]


# ---- 都県の小さな地図（SVG、この街だけ色をつける）
def proj(lon, lat, b):
    x0, y0, x1, y1 = b
    k = math.cos(math.radians((y0 + y1) / 2))
    w = (x1 - x0) * k
    h = y1 - y0
    s = 300 / max(w, h)
    return ((lon - x0) * k * s, (y1 - lat) * s)


def rings(g):
    if g["type"] == "Polygon":
        return g["coordinates"]
    return [r for poly in g["coordinates"] for r in poly]


def pref_svg(pf, hi):
    city = city_of(pf, hi)
    keys = [k for k in SHAPE if k[0] == pf and (not city or city_of(pf, k[1]) == city)]
    xs, ys = [], []
    for k in keys:
        for g in SHAPE[k]:
            for r in rings(g):
                for x, y in r:
                    xs.append(x)
                    ys.append(y)
    b = (min(xs), min(ys), max(xs), max(ys))
    W, H = proj(b[2], b[1], b)
    col = PI[pf][3]
    ps = []
    for k in keys:
        d = ""
        for g in SHAPE[k]:
            for r in rings(g):
                pts = [proj(x, y, b) for x, y in r]
                d += "M" + "L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + "Z"
        on = k[1] == hi
        ps.append(f'<path d="{d}" fill="{col if on else "#F1F2F4"}" stroke="#fff" stroke-width="{0.8 if not on else 1.2}"/>')
    ps.sort(key=lambda s: col in s)
    pin_s = ""
    if (pf, hi) in LAB:
        cx, cy = proj(*LAB[(pf, hi)], b)
        # 11/4 月のオーナーが20案から選んだ「ネオン」のしずく（月と同じ）
        nl = "#" + "".join("%02x" % round(int(col[i:i + 2], 16) * .5 + 255 * .5) for i in (1, 3, 5))
        pin_s = (f'<g class="neo" transform="translate({cx:.0f},{cy:.0f}) scale(.8)" style="color:{col};--nl:{nl};filter:drop-shadow(0 1.5px 1.5px rgba(0,0,0,.2))"><ellipse class="nsh" cx="0" cy="1" rx="6" ry="2.2" fill="#2B2622" opacity=".2"/>'
                 f'<path class="nh" d="M0 0C-3-7-12-12-12-22a12 12 0 0 1 24 0C12-12 3-7 0 0Z" fill="none" stroke="{col}" stroke-width="6.8" stroke-opacity="0" stroke-linejoin="round"/>'
                 f'<path class="nb" d="M0 0C-3-7-12-12-12-22a12 12 0 0 1 24 0C12-12 3-7 0 0Z" fill="#fff" stroke="{col}" stroke-width="2.4" stroke-linejoin="round"/>'
                 f'<path class="ni" d="M-4.6 -21.2L0 -25.4L4.6 -21.2V-17.4H-4.6Z" fill="none" stroke="{col}" stroke-width="1.6" stroke-linejoin="round"/><path class="ni" d="M-1.3 -17.4V-20H1.3V-17.4" fill="none" stroke="{col}" stroke-width="1.3"/></g>')
    area = {}
    for k in keys:
        xs2 = [x for g in SHAPE[k] for r in rings(g) for x, _ in r]
        ys2 = [y for g in SHAPE[k] for r in rings(g) for _, y in r]
        area[k] = (max(xs2) - min(xs2)) * (max(ys2) - min(ys2))
    labs, grp = [], {}
    for k in keys:
        if k not in LAB:
            continue
        cty = city_of(pf, k[1])
        if cty and not city:  # 都県の地図では、政令市・23区は1つの名前に
            grp.setdefault(cty, []).append(proj(*LAB[k], b))
            continue
        nm = k[1][len(city):] if city and city != "東京23区" else k[1]
        x, y = proj(*LAB[k], b)
        labs.append((1e9 if k[1] == hi else area[k], x, y, nm, k[1] == hi))
    for cn, pts in grp.items():
        labs.append((1e8, sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts), cn, False))
    labs.sort(key=lambda l: -l[0])
    boxes, tx = [], []
    for _, x, y, nm, on in labs:
        fs = 15 if on else 10.5
        w, h = len(nm) * fs * 1.02, fs * 1.2
        for dx, dy in ([(0, 19), (0, -30), (w * .6 + 8, 0), (-w * .6 - 8, 0), (w * .6 + 8, -14), (-w * .6 - 8, -14)] if on else [(0, 0), (0, -h), (0, h)]):
            bx = (x + dx - w / 2, y + dy - h / 2, x + dx + w / 2, y + dy + h / 2)
            if bx[0] < -4 or bx[2] > W + 4 or bx[1] < -4 or bx[3] > H + 4:
                continue
            if any(bx[0] < o[2] and bx[2] > o[0] and bx[1] < o[3] and bx[3] > o[1] for o in boxes):
                continue
            boxes.append(bx)
            tx.append(f'<text x="{x + dx:.0f}" y="{y + dy:.0f}" font-size="{fs}" font-weight="{700 if on else 500}" fill="{"#2B2622" if on else "#5C5048"}">{E(nm)}</text>')
            break
        else:
            if on:
                cx2 = min(max(x, w / 2), W - w / 2)
                cy2 = min(max(y - 16, h / 2), H - h / 2)
                tx.append(f'<text x="{cx2:.0f}" y="{cy2:.0f}" font-size="{fs}" font-weight="700" fill="#2B2622">{E(nm)}</text>')
    ps.append('<g style="font-family:\'Zen Kaku Gothic New\',sans-serif;paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round;text-anchor:middle;dominant-baseline:central">' + "".join(tx) + '</g>')
    ps.append(pin_s)
    return f'<svg viewBox="-4 -4 {W + 8:.0f} {H + 8:.0f}" role="img" aria-label="{E(city or PI[pf][6])}の地図。{E(hi)}の場所">{"".join(ps)}</svg>'


def scope_name(t):
    return city_of(t["p"], t["n"]) or PI[t["p"]][6]


def near(t, n=6):
    def dist(a):
        return (a["lat"] - t["lat"]) ** 2 + ((a["lon"] - t["lon"]) * 0.82) ** 2
    return sorted([a for a in towns if a is not t], key=dist)[:n]


HEAD_CSS = """body{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New";color:#2B2622}
.wrap{max-width:440px;margin:0 auto;padding:0 16px 40px}
.head{text-align:center;margin:0 -16px;padding:30px 16px 22px;background:radial-gradient(circle at 14% 26%,rgba(242,214,194,.55) 0 74px,transparent 75px),radial-gradient(circle at 88% 16%,rgba(205,224,236,.6) 0 54px,transparent 55px),radial-gradient(circle at 80% 88%,rgba(214,228,205,.6) 0 48px,transparent 49px)}
.head img{width:60px;height:60px}
.en{font-family:Jost;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:10px}
h1{font-family:"Shippori Mincho",serif;font-weight:600;font-size:23px;line-height:1.5;letter-spacing:.1em;color:#231E1B;margin:14px 0 8px;font-feature-settings:"palt"}
h1 span{display:block;font-size:14px;letter-spacing:.2em;color:#6B6058;margin-top:4px}
.sub{font-size:13px;line-height:2;color:#6B6058;margin:0;text-wrap:balance}
.upd{font-size:11px;color:#8C7B6E;margin-top:8px}
h2{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.14em;margin:30px 0 8px;padding-left:10px;border-left:3px solid var(--pc,#4F86C6)}
.cap{font-size:11.5px;color:#8C7B6E;margin:0 0 10px;line-height:1.7}
.faq details{background:#fff;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);margin-bottom:8px;padding:12px 16px}
.faq summary{font-weight:700;font-size:14px;line-height:1.6;cursor:pointer}.faq p{font-size:13px;line-height:1.9;color:#5E544D;margin:8px 0 0}
.note{font-size:12px;line-height:1.9;color:#7A6E66;background:#F5F5F5;padding:14px 16px;margin-top:30px;word-break:break-all}.note a{color:#7A6E66}
.jmp{display:flex;justify-content:space-between;align-items:center;margin:12px 0 0;padding:13px 16px;border:1px solid #E3E3E3;border-radius:14px;text-decoration:none;color:#2B2622;font-weight:700;font-size:14px;background:#fff}.jmp i{font-style:normal;font-family:Jost;color:#9C8775}.itt{scroll-margin-top:12px}
.itt{margin:30px 0 6px;text-align:center}.itt .en2{font-family:Jost,sans-serif;font-size:11px;letter-spacing:.32em;color:#9C8775}.itt h2{margin:6px 0 14px;padding-left:0;border-left:0;font-size:20px}.itg{display:grid;grid-template-columns:1fr 1fr;gap:10px;text-align:left}.itc{display:flex;flex-direction:column;text-decoration:none;color:#2B2622;border:1px solid #E3E3E3;border-radius:18px;padding:16px 14px;background:#fff}.itc b{font-family:"Shippori Mincho",serif;font-size:17px;font-weight:700;letter-spacing:.06em}.itc span{font-size:12.5px;line-height:1.75;color:#6B6058;margin:8px 0 12px;flex:1}.itc i{font-style:normal;font-weight:700;font-size:13.5px;color:#B5735A}.itc.buy{cursor:default}.itc.buy span{margin-bottom:8px}.itc .yl{display:flex;justify-content:space-between;align-items:center;text-decoration:none;color:#2B2622;font-size:13.5px;font-weight:700;padding:9px 2px;border-top:1px solid #D9DCE1}.itc .yl i{color:#B5735A;font-size:13.5px}.itn{font-size:11.5px;color:#8C7B6E;text-align:left;margin:8px 2px 0}
.uru{display:block;text-decoration:none;color:#2B2622;border:1px solid #2B2622;padding:16px;margin-top:30px;text-align:center}
.uru .k{font-size:11px;letter-spacing:.2em;color:#8C7B6E}.uru .t{font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;letter-spacing:.08em;margin:6px 0 4px}.uru .m{font-size:12px;color:#6B6058;line-height:1.8}
.uru.buy{position:relative;margin-top:18px;padding:16px 14px 6px}.uru .bx{display:block;text-decoration:none;color:#2B2622;border-top:1px solid #E4E5E8;padding:12px 2px;text-align:left}.uru .k+.ad+.bx{margin-top:10px}.uru .bx b{display:block;font-family:"Shippori Mincho",serif;font-size:15px;font-weight:600}.uru .bx b:after{content:" →";color:#B5735A}.uru .bx span{display:block;font-size:11.5px;color:#6B6058;line-height:1.7;margin-top:3px}.uru .ad{position:absolute;top:6px;right:8px;font-size:10px;color:#8C7B6E}
.back{display:block;width:max-content;margin:28px auto 0;color:#2B2622;text-decoration:none;font-size:13px;letter-spacing:.1em;border-bottom:1px solid #2B2622;padding-bottom:2px}
.ft{text-align:center;font-size:10px;letter-spacing:.04em;color:#8C7B6E;margin-top:30px}"""

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">'
SCRIPTS = f'<script src="/assets/night.js?v={VER["night.js"]}"></script><script src="/assets/menu.js?v={VER["menu.js"]}" defer></script><script src="/assets/v2sub.js?v={VER["v2sub.js"]}" defer></script>'

# 燈の数え方（functions/_middleware.js）：/c?f=来た元&s=項目&k=名前。オーナーの端末（me=1 の印）は数えない。
# 開いた数は middleware が数えるので、ここでは押した数だけ（KV の書き込みの無料枠を守る）
CJS = ('var F="direct";try{F=sessionStorage.getItem("f")||"direct";}catch(e){}'
       'function s(k){try{navigator.sendBeacon("/c?f="+encodeURIComponent(F)+"&s=fudosan&k="+encodeURIComponent(String(k).slice(0,40)));}catch(e){}}')


def beacon(name):
    return ('<script>(function(){' + CJS +
            'document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a");if(!a)return;'
            f's({json.dumps(name + "｜", ensure_ascii=False)}+(a.getAttribute("data-k")||a.textContent.trim().slice(0,30)));}},true);}})();</script>')


def head(title, desc, url, ld=None):
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><meta name="description" content="{E(desc)}">'
            + ('' if LIVE else '<meta name="robots" content="noindex">') + (f'<link rel="canonical" href="{url}">' if LIVE else '')
            + f'<meta property="og:type" content="article"><meta property="og:url" content="{url}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">'
            f'<meta property="og:image" content="{BASE}/og-v10.png"><meta name="twitter:card" content="summary">'
            f'<link rel="icon" href="/logo.png">{FONTS}'
            + (f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ''))


def src_note(s):
    """出典の文：令和8年の表・令和7年の表・平均価格の表（ある物だけ）"""
    out = f'{E(s["src"])}（価格時点 2026年1月1日）<br><a href="{E(s["url"])}" data-k="出典">{E(s["url"])}</a>'
    if s.get("url_r7"):
        out += f'<br>令和7年の数字：<a href="{E(s["url_r7"])}" data-k="出典（令和7年）">{E(s["url_r7"])}</a>'
    if s.get("url_price"):
        out += f'<br>平均価格：<a href="{E(s["url_price"])}" data-k="出典（平均価格）">{E(s["url_price"])}</a>'
    return out


URU = ('<a class="uru" href="/uru.html" data-k="お家を売る前に大事なこと"><div class="k">お家を売る・持ち続ける前に</div><div class="t">お家を売る前に大事なこと</div>'
       '<div class="m">売るか、持ち続けるか。<br>迷ったときに読むページです。</div></a>')

# 家を探す方へ（バリューコマース Yahoo!不動産 流通領域・LIFE NOTE sid 3786665 で提携済み）
from urllib.parse import quote as _q
YAHOO_RE = "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=3786665&pid=892742457&vc_url=" + _q("https://realestate.yahoo.co.jp/", safe="")


# 11/8 オーナー（月のスレッド）「アフェリエイト通った全部」→ タウンライフ不動産購入・住まいサーフィン（LIFE NOTE sid 3786665 の自由テキスト）
TOWNLIFE_RE = "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=3786665&pid=892742462"
SUMAI_RE = "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=3786665&pid=892742456"
# 11/9 夜の試験：タウンライフ・住まいサーフィンは「無効の広告」ページに進む（ミス帳#134・#135）→ 使えると確かめるまで出さない（月）
VC_EXTRA_ON = False

# 11/9 オーナー「動線悪すぎ、Yahoo飛んでまた地名から調べるんだろ？」→ 街ごとの売り出し中の一覧へ直接（全国地方公共団体コード：jis_kanto.json、geolonia/japanese-addresses から作成）
JIS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "jis_kanto.json"), encoding="utf-8"))
YKIND = [("中古マンション", "used/mansion"), ("中古の一戸建て", "used/house"), ("土地", "land")]


def yahoo_town(p, n, path):
    c = JIS.get(p + "|" + n)
    u = f"https://realestate.yahoo.co.jp/{path}/search/03/{c[:2]}/{c}/" if c else "https://realestate.yahoo.co.jp/"
    return YAHOO_RE.split("&vc_url=")[0] + "&vc_url=" + _q(u, safe="")


def buy_card(p, n):
    rows = "".join(f'<a class="yl" href="{E(yahoo_town(p, n, path))}" rel="nofollow sponsored" target="_blank" data-k="家を探す｜Yahoo!不動産｜{k}｜{E(n)}">{k}<i>→</i></a>' for k, path in YKIND)
    return f'<div class="itc buy"><b>買いたい</b><span>{E(n)}でいま売り出し中の家（Yahoo!不動産）</span>{rows}</div>'


# 11/9 オーナーOK（月の見本3と同じ）：街ページは「売りたい・買いたい」の2つだけ（売る前に・Yahoo!の箱はここにまとめた）
def itt_box(n, p="", tid=""):
    return (f'<section class="itt" id="itt"><div class="en2">IN THIS TOWN</div><h2>{E(n)}で</h2><div class="itg">'
            f'<a class="itc" href="/uru.html" data-k="この街で｜売りたい｜{E(n)}"><b>売りたい</b><span>いくらで売れそうか、相場から順に（無料）</span><i>手順を見る →</i></a>'
            f'' + buy_card(p, n) + f''
            f'</div>'
            # 11/12 台帳：関東は7日で1195回見られて申し込みを開いた人0。街ページ329枚に申し込みへの道が1つも無かった → 街の名前入りで、申し込みの2つ目の画面（場所入り）へ直接
            + (f'<a class="itg2 itq" href="/moushikomi?lite=1&amp;machi={tid}&amp;want={_q("査定してほしい")}" data-k="この街で｜いくらで売れるか聞く｜{E(n)}">{E(short(n))}の家、いくらで売れるか無料で聞く <i>→</i></a>'
               f'<p class="itn" style="text-align:center;margin-top:6px">無料・売るか決めていなくても大丈夫です。メールかお電話、ご希望の方でお返事します。</p>'
               f'<a class="itg2" href="/moushikomi?machi={tid}&amp;want={_q("相続した家のこと")}" data-k="この街で｜困りごとの相談｜{E(n)}">相続した家・古い家・再建築不可などのご相談 <i>→</i></a>'
               f'<a class="itg2" href="/kaitai" data-k="この街で｜解体・片付けの費用｜{E(n)}">解体・片付けの費用を、30秒で目安を出す <i>→</i></a>' if tid else '')
            + f'<p class="itn">「買いたい」の3つは広告です（Yahoo!不動産のこの街の一覧が開きます）。</p></section>')


def buy_box(n):
    return (f'<div class="uru buy"><div class="k">この街で家を探している方へ</div><div class="ad">広告</div>' +
            f'<a class="bx" href="{E(TOWNLIFE_RE)}" rel="nofollow sponsored" target="_blank" data-k="家を探す｜タウンライフ｜{E(n)}"><b>希望を1回送って、物件を提案してもらう</b><span>タウンライフ不動産。予算や駅を送ると、何社かから物件のご提案が届きます（無料）</span></a>' * VC_EXTRA_ON +
            f'<a class="bx" href="{E(YAHOO_RE)}" rel="nofollow sponsored" target="_blank" data-k="家を探す｜Yahoo!不動産｜{E(n)}"><b>自分で物件を探す</b><span>Yahoo!不動産。中古マンション・一戸建て・新築を、駅や広さで</span></a>' +
            f'<a class="bx" href="{E(SUMAI_RE)}" rel="nofollow sponsored" target="_blank" data-k="家を探す｜住まいサーフィン｜{E(n)}"><b>新築マンションが割高か調べる</b><span>住まいサーフィン。値段が割高か割安かを、無料の会員登録で</span></a>' * VC_EXTRA_ON + '</div>')


# ================= 街ごとのページ
TOWN_CSS = """.itg2.itq{background:#3A332E;color:#fff;border:0;border-radius:12px;padding:15px 16px;font-size:15px;font-weight:700;margin-top:12px}.itg2.itq i{color:#fff}
.itg2{display:flex;justify-content:space-between;margin:10px 0 0;padding:11px 14px;border-top:1px solid #E6E6E6;border-bottom:1px solid #E6E6E6;text-decoration:none;color:#5E544D;font-size:13px;text-align:left}.itg2 i{font-style:normal;font-family:Jost;color:#9C8775}
.big{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:20px 0 0}
.big div{background:#F5F5F5;padding:12px 14px}.big b{display:block;font-family:Jost;font-size:24px;font-weight:500;color:var(--pc)}.big span{font-size:11px;color:#7A6E66;letter-spacing:.04em}
.big .w{grid-column:1/3}.big .w b{font-size:15px;font-family:"Zen Kaku Gothic New";font-weight:700;color:#2B2622;line-height:1.7}
.mp{margin:14px 0 0;padding:14px;background:#fff;border:1px solid #ECECEC}.mp svg{display:block;width:100%;height:auto;max-height:280px}
.mp p{font-size:11px;color:#8C7B6E;margin:8px 0 0;text-align:center}
.nb{list-style:none;margin:0;padding:0}.nb li{border-bottom:1px solid #ECECEC}
.nb a{display:flex;justify-content:space-between;align-items:center;padding:12px 2px;text-decoration:none;color:#2B2622;font-weight:700;font-size:14px}
.nb a b{font-family:Jost;font-weight:500;font-size:15px}.nb a small{font-size:11px;color:#8C7B6E;font-weight:500;margin-left:6px}
.fc{display:block;text-decoration:none;color:#2B2622;background:#fff;border-left:3px solid var(--pc);box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.05);padding:12px 14px;margin-bottom:10px}
.fc small{display:block;font-size:11px;color:#8C7B6E}.fc b{display:block;font-size:14.5px;line-height:1.6;margin:3px 0}.fc span{font-size:12.5px;color:#5E544D;line-height:1.7}
.rq{display:block;width:100%;margin:10px 0 0;padding:13px;border:0;border-radius:12px;background:#3A2F28;color:#fff;font-family:"Zen Kaku Gothic New",sans-serif;font-size:13.5px;font-weight:700;cursor:pointer}.rq:disabled{background:#8C7B6E}"""


def town_page(t):
    pf, fn, en, col, sname, surl, pfull, s = PI[t["p"]]
    n = t["n"]
    up = t["r8"] > 0
    word = "上がりました" if t["r8"] > 0 else "下がりました" if t["r8"] < 0 else "変わりませんでした"
    trend = ""
    if t["r7"] is not None:
        d = round(t["r8"] - t["r7"], 1)
        # 月の文に足した所：前の年と上がり・下がりが入れかわった街（例 前橋市 −0.1%→+0.1%）は「上がり幅が大きく」と書かない
        trend = "前の年の下がりから、上がりに変わりました" if up and t["r7"] < 0 else "前の年の横ばいから、上がりに変わりました" if up and t["r7"] == 0 else \
            "前の年の下がりから、横ばいに変わりました" if t["r8"] == 0 and t["r7"] < 0 else "前の年の上がりから、横ばいに変わりました" if t["r8"] == 0 and t["r7"] > 0 else \
            "前の年の上がりから、下がりに変わりました" if t["r8"] < 0 and t["r7"] > 0 else "前の年の横ばいから、下がりに変わりました" if t["r8"] < 0 and t["r7"] == 0 else \
            "前の年より上がり幅が大きくなりました" if d > 0 and up else "前の年より上がり幅が小さくなりました" if d < 0 and up else \
            "前の年より下がり幅が小さくなりました" if d > 0 and t["r8"] < 0 else "前の年より下がり幅が大きくなりました" if d < 0 and t["r8"] < 0 else \
            "前の年と同じ動きでした" if d == 0 else ""
    # 11/9 収益化：売る・買う人が「◯◯区 土地 相場」「◯◯市 家 売る」で探すので、題にその言葉を入れる（数字は地価公示のまま）
    title = f"{n}の地価・土地相場 2026｜住宅地は{pct(t['r8'])}｜家を売る前・買う前に"
    desc = (f"{pfull}{n}の住宅地の地価は、令和8年地価公示（2026年1月1日時点）で前の年から{pct(t['r8'])}。"
            f"{pfull}の{t['of']}の市区町村で{t['rank']}位です。" + (f"前の年は{pct(t['r7'])}。" if t['r7'] is not None else "") + "家を売る前・買う前に、公式の数字で街の値段の動きを見られます。")
    rel = related(t)
    nb = near(t)
    faq = [(f"{n}の住宅地の地価は上がっていますか？",
            f"令和8年地価公示（2026年1月1日時点）で、{n}の住宅地は前の年から平均{pct(t['r8'])}で、{word}。" + (f"前の年（令和7年）は{pct(t['r7'])}でした。" if t["r7"] is not None else "")),
           (f"{n}は{pfull}で何位ですか？",
            f"住宅地の上がり幅で、{pfull}の{t['of']}の市区町村のうち{t['rank']}位です（このページで比べた市区町村の中での順位）。"),
           ("この数字で、わが家の値段がわかりますか？",
            "わかりません。街の中の調査地点の平均の動きで、1軒ずつの値段ではありません。家の値段は、場所・広さ・築年数などで大きく変わります。")]
    url = f"{BASE}/machi/{t['id']}"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Dataset", "name": f"{n}の住宅地の地価の変動率（令和8年地価公示）", "description": desc, "isBasedOn": surl,
         "temporalCoverage": "2026-01-01", "spatialCoverage": f"{pfull}{n}"},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "関東不動産リスト", "item": f"{BASE}/fudosan-list"},
            {"@type": "ListItem", "position": 2, "name": "関東 地価ランキング", "item": f"{BASE}/chika-kanto"},
            {"@type": "ListItem", "position": 3, "name": f"{n}の地価", "item": url}]}]}
    big = (f'<div class="big"><div><span>住宅地 1年の動き</span><b style="color:{col if t["r8"] > 0 else "#6B6058"}">{pct(t["r8"])}</b></div>'
           f'<div><span>{pfull}での順位</span><b style="color:#2B2622">{t["rank"]}<small style="font-size:13px">位／{t["of"]}</small></b></div>'
           + (f'<div><span>前の年（令和7年）</span><b style="color:#6B6058">{pct(t["r7"])}</b></div>' if t["r7"] is not None else '')
           + (f'<div><span>住宅地の平均価格（1㎡）</span><b style="color:#6B6058">{t["price"] / 10000:.2f}万円</b></div>' if t["price"] else '')
           + (f'<div class="w"><b>{E(trend)}。</b></div>' if trend else '') + '</div>'
           + '<a class="jmp" href="#itt" data-k="街ページ｜売りたい・買いたいへ">この街で 売りたい・買いたい（売り出し中の家）<i>↓</i></a>')
    rel_h = ""
    if rel:
        # data-cat があると cardmark.js が日付の絵を付けない（地価の数字はおでかけではないので）
        rel_h = '<h2>この街で調べた数字</h2>' + "".join(
            f'<a class="fc" href="{E(o["url"])}" data-cat="chika" data-k="関連｜{E(o["t"][:20])}"><small>{E(o["src"])}</small><b>{E(o["t"].replace("｜", "　"))}</b><span>{E(o["m"])}</span></a>' for o in rel)
    nb_h = '<h2>近くの街</h2><ul class="nb">' + "".join(
        f'<li><a href="/machi/{a["id"]}" data-k="近くの街｜{E(a["n"])}">{E(a["n"])}<small>{E(a["p"])}</small><b style="color:{PI[a["p"]][3]}">{pct(a["r8"])}</b></a></li>' for a in nb) + '</ul>'
    sc = scope_name(t)
    body = f'''<style>{HEAD_CSS}{TOWN_CSS}</style>{SCRIPTS}</head><body style="--pc:{col}"><div class="wrap">
<div class="head"><img src="/logo-s.png" width="60" height="60" alt="LIFE NOTE のロゴ"><div class="en">{en} ─ LAND PRICE</div>
<h1>{E(n)}の地価<span>2026 住宅地の1年の動き</span></h1>
<p class="sub">国の地価公示の数字で、<br>{E(pfull)}{E(n)}の住宅地の動きを見ます。</p>
<div class="upd">2026年1月1日時点の数字（{TODAY} 作成）</div></div>
{big}
<div class="mp nofilt">{pref_svg(t["p"], n)}<p>{E(sc)}の中の{E(short(n) if sc != pfull else n)}</p></div>
{itt_box(n, t["p"], t["id"])}
{rel_h}
{nb_h}
<a class="back" href="/chika-kanto#{fn}" data-k="{E(pfull)}のランキング" style="margin-top:18px">{E(pfull)}の街をランキングで見る</a>
<h2>この街をもっと調べてほしい</h2><p class="cap">駅ごとの地価や人口など、もっと細かく知りたい方はボタンを押してください。押された街から順に調べて、このリストに足します。</p>
<button class="rq" type="button" data-n="{E(n)}">{E(n)}をもっと調べてほしい</button>
<section class="faq"><h2>よくある質問</h2>
{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)}
</section>
<p class="note">出典：{src_note(s)}<br>数字は街の中の調査地点の平均の変動率で、1軒ずつの値段ではありません。</p>
<a class="back" href="/fudosan-list" data-k="関東不動産リストへ">関東不動産リストを見る</a>
<div class="ft">LIFE NOTE</div></div>
<script>(function(){{{CJS}var b=document.querySelector(".rq");if(!b)return;b.onclick=function(){{s("調べてほしい："+b.dataset.n);b.disabled=true;b.textContent="受け付けました。調べて、このリストに足します";}};}})();</script>
{beacon("街｜" + n)}</body></html>'''
    return head(title, desc, url, ld) + body


os.makedirs(os.path.join(S, "machi"), exist_ok=True)
for f in os.listdir(os.path.join(S, "machi")):
    if f.endswith(".html"):
        os.remove(os.path.join(S, "machi", f))
for t in towns:
    open(os.path.join(S, "machi", t["id"] + ".html"), "w", encoding="utf-8").write(town_page(t))

# ================= 検索・地図用のデータ（読みは kana.json）
KANA = json.load(open(os.path.join(D, "kana.json"), encoding="utf-8"))
json.dump([{"id": t["id"], "p": t["p"], "n": t["n"], "s": short(t["n"]), "r7": t["r7"], "r8": t["r8"], "rk": t["rank"], "of": t["of"],
            "la": round(t["lat"], 4), "lo": round(t["lon"], 4), "k": KANA.get(t["n"], "").replace(" ", "")} for t in towns],
          open(os.path.join(S, "assets", "towns.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

# ================= 関東ランキング
RK_CSS = """.sum{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:20px 0 0}
.sum div{background:#F5F5F5;padding:12px 14px}.sum b{display:block;font-family:Jost;font-size:20px;font-weight:500;color:#4F86C6}.sum span{font-size:11px;color:#7A6E66;letter-spacing:.04em}.sum em{font-style:normal;display:block;font-size:13px;font-weight:700;color:#2B2622}
.flt{display:flex;flex-wrap:nowrap;justify-content:center;gap:0 13px;margin:24px 0 8px;padding:10px 0;border-top:1px solid #D4D4D4;border-bottom:1px solid #D4D4D4;overflow-x:auto}
.flt button{flex:none;border:none;background:none;padding:4px 0;font-family:"Zen Kaku Gothic New";font-size:14px;font-weight:700;letter-spacing:.04em;color:var(--pc,#8C7B6E);border-bottom:1px solid transparent;cursor:pointer;opacity:.85}
.flt button.on{opacity:1;border-bottom-color:currentColor}
ol{list-style:none;margin:0;padding:0}
.r a{display:grid;grid-template-columns:30px 1fr auto;align-items:center;column-gap:10px;row-gap:5px;padding:11px 2px;border-bottom:1px solid #ECECEC;text-decoration:none;color:#2B2622}
.no{font-family:Jost;font-size:14px;color:#9C9187;text-align:center;grid-row:1/3}
.top .no{color:#fff;background:var(--c);border-radius:50%;width:24px;height:24px;line-height:24px;font-size:13px;justify-self:center}
.nm{grid-column:2;grid-row:1;font-weight:700;font-size:14px;letter-spacing:.04em}.nm small{font-size:11px;color:#8C7B6E;font-weight:500;margin-left:6px}
.bar{grid-column:2/4;grid-row:2;height:6px;background:#F1F2F4;position:relative}.bar i{position:absolute;top:0;bottom:0;background:var(--c);opacity:.55}.top .bar i{opacity:1}.bar .z{position:absolute;top:-3px;bottom:-3px;width:1px;background:#B9B9B9}
.v{grid-column:3;grid-row:1;font-family:Jost;font-weight:500;font-size:16px;text-align:right}
.pane{display:none}.pane.on{display:block}
.ilk{display:block;width:max-content;max-width:100%;margin:14px auto 0;color:#2B2622;text-decoration:none;font-family:"Shippori Mincho",serif;font-weight:600;font-size:14px;letter-spacing:.08em;border-bottom:1px solid #2B2622;padding-bottom:3px}"""


def rk_list(ts, show_pref):
    mn = min(t["r8"] for t in ts)
    zero = (-min(mn, 0)) / (max(t["r8"] for t in ts) - min(mn, 0) or 1) * 100
    span = (max(t["r8"] for t in ts) - min(mn, 0)) or 1
    out, prev, pr = [], None, 0
    for i, t in enumerate(sorted(ts, key=lambda t: -t["r8"]), 1):
        if t["r8"] != prev:
            pr = i
        prev = t["r8"]
        c = PI[t["p"]][3]
        w = abs(t["r8"]) / span * 100
        left = zero if t["r8"] >= 0 else zero - w
        out.append(f'<li class="r{" top" if pr <= 3 else ""}" style="--c:{c}"><a href="/machi/{t["id"]}" data-k="ランキング｜{E(t["n"])}">'
                   f'<span class="no">{pr}</span><span class="nm">{E(t["n"])}' + (f'<small>{t["p"]}</small>' if show_pref else '') + '</span>'
                   f'<span class="bar"><b class="z" style="left:{zero:.1f}%"></b><i style="left:{left:.1f}%;width:{w:.1f}%"></i></span>'
                   f'<span class="v" style="color:{c if t["r8"] > 0 else "#7A6E66"}">{pct(t["r8"])}</span></a></li>')
    return "\n".join(out)


top = sorted(towns, key=lambda t: -t["r8"])[0]
ups = sum(1 for t in towns if t["r8"] > 0)
NAMES = "・".join(ORDER)
desc = (f"関東7都県（{NAMES}）の{len(towns)}の市区町村の住宅地の地価を、令和8年地価公示の数字で上がり幅の順に並べました。"
        f"1位は{top['n']}（{pct(top['r8'])}）。都県ごとにも見られます。")
panes = [("all", "関東", "関東ぜんぶ", towns, True)] + [(p[1], p[0], p[6], [t for t in towns if t["p"] == p[0]], False) for p in PREFS]
srcs = "<br>".join(src_note(p[7]) for p in PREFS)
nones = "、".join(f"{p[6]}の{p[7]['none'].split('。')[0]}" for p in PREFS if p[7].get("none"))
gm = len([t for t in towns if t["p"] == "群馬"])
faq = [("関東で住宅地の地価がいちばん上がった街は？",
        f"令和8年地価公示（2026年1月1日時点）で比べると、{top['n']}（{top['p']}）の{pct(top['r8'])}がいちばん大きい上がり幅でした。"),
       ("上がった街はいくつありますか？",
        f"このページで比べた{len(towns)}の市区町村のうち、住宅地の平均が上がったのは{ups}、変わらなかったのは{sum(1 for t in towns if t['r8'] == 0)}、下がったのは{sum(1 for t in towns if t['r8'] < 0)}でした。"),
       ("のっていない町や村があるのはなぜ？",
        "住宅地の調査地点がない町や村、都県の資料に住宅地の平均が出ていない町や村はのせていません。"
        + nones + f"です。群馬県は、地価公示の住宅地の地点がある{gm}の市町村だけです。"
        "東京都の島の町村は、このページの地図に入れていないため、のせていません。")]
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "Dataset", "name": "関東の市区町村 住宅地の地価ランキング（令和8年地価公示）", "description": desc, "temporalCoverage": "2026-01-01", "spatialCoverage": "関東"},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]}
rk = head(f"関東 地価ランキング2026｜{len(towns)}の市区町村の住宅地（令和8年地価公示）", desc, f"{BASE}/chika-kanto", ld) + f'''<style>{HEAD_CSS}{RK_CSS}</style>{SCRIPTS}</head><body><div class="wrap">
<div class="head"><img src="/logo-s.png" width="60" height="60" alt="LIFE NOTE のロゴ"><div class="en">KANTO ─ LAND PRICE</div>
<h1>関東 地価ランキング<span>2026 住宅地の1年の動き</span></h1>
<p class="sub">7都県・{len(towns)}の市区町村を、<br>国の地価公示の数字で並べました。</p>
<div class="upd">2026年1月1日時点の数字（{TODAY} 作成）</div></div>
<div class="sum"><div><span>関東の1位</span><em>{E(top["n"])}</em><b>{pct(top["r8"])}</b></div><div><span>上がった街</span><em>{len(towns)}の街のうち</em><b>{ups}</b></div></div>
<nav class="flt">''' + "".join(f'<button data-p="{k}" style="--pc:{PI[pf][3] if pf in PI else "#2B2622"}"{" class=\"on\"" if k == "all" else ""}>{"すべて" if k == "all" else pf}</button>' for k, pf, _, _, _ in panes) + '</nav>' + \
    "".join(f'<section class="pane{" on" if k == "all" else ""}" id="{k}"><h2 style="--pc:{PI[pf][3] if pf in PI else "#4F86C6"}">{E(nm)}の住宅地</h2><p class="cap">上がり幅の順です（値段の順ではありません）。押すと、その街のページが開きます。</p><ol>{rk_list(ts, sp)}</ol></section>'
            for k, pf, nm, ts, sp in panes) + f'''
<section class="faq"><h2>よくある質問</h2>
{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)}
</section>
{URU}
<p class="note">出典（価格時点 2026年1月1日）<br>{srcs}<br>数字は街の中の調査地点の平均の変動率で、1軒ずつの値段ではありません。</p>
<a class="back" href="/moushikomi?lite=1&amp;want=%E6%9F%BB%E5%AE%9A%E3%81%97%E3%81%A6%E3%81%BB%E3%81%97%E3%81%84" data-k="地価ランキング｜いくらで売れるか聞く" style="display:block;background:#3A332E;color:#fff;border:0;border-radius:12px;padding:15px 16px;margin:18px 0 14px;text-align:center;text-decoration:none;font-weight:700;font-size:15px">お家がいくらで売れるか、無料で聞く</a><a class="back" href="/fudosan-list" data-k="関東不動産リストへ">関東不動産リストを見る</a>
<div class="ft">LIFE NOTE</div></div>
<script>(function(){{function go(k){{var b=document.querySelector('.flt button[data-p="'+k+'"]');if(!b)return;document.querySelectorAll(".flt button,.pane").forEach(function(x){{x.classList.remove("on")}});b.classList.add("on");document.getElementById(k).classList.add("on");}}
document.querySelectorAll(".flt button").forEach(function(b){{b.onclick=function(){{go(b.dataset.p);history.replaceState(null,"","#"+b.dataset.p);}}}});if(location.hash)go(location.hash.slice(1));}})();</script>
{beacon("地価ランキング関東")}</body></html>'''
open(os.path.join(S, "chika-kanto.html"), "w", encoding="utf-8").write(rk)


# ================= 関東不動産リスト（月の fudosan-list と同じ型に、関東の中身を入れる）
h = open(os.path.join(R, "scripts", "fudosan_kanto_base.html"), encoding="utf-8").read()


def rep(old, new, count=1):
    """月の型の言葉を入れかえる。型が変わって見つからない時は止める（間違ったページを出さない）"""
    global h
    assert old in h, ("型に見つからない", old[:80])
    h = h.replace(old, new) if count == 0 else h.replace(old, new, count)


def resub(pat, new, flags=0):
    global h
    h2 = re.sub(pat, lambda m: new, h, count=1, flags=flags)
    assert h2 != h, ("型に見つからない", pat[:80])
    h = h2


URL = f"{BASE}/fudosan-list"
LDESC = "東京・神奈川・埼玉・千葉・茨城・栃木・群馬の地価、人口、駅の乗る人、新しい施設、住まいの制度を、公式の資料つきでまとめました。"
KJS = json.dumps(PC, ensure_ascii=False)
PJS = json.dumps(ORDER, ensure_ascii=False)
# ---- head
rep('<meta name="google-site-verification" content="VdNVMVF15cEGulZ_syxp2iotl_CHYHhzys9rJ4hjkOk">', '')  # 月のサイトの印は外す（燈の印 19Vt8… は残す）
resub(r'<meta name="description"[^>]*><meta name="robots" content="noindex">', f'<meta name="description" content="{LDESC}">' + ('' if LIVE else '<meta name="robots" content="noindex">'))
rep('content="https://townnote.pages.dev/fudosan-list"><link rel="canonical" href="https://townnote.pages.dev/fudosan-list">',
    f'content="{URL}">' + (f'<link rel="canonical" href="{URL}">' if LIVE else ''))
rep('<meta property="og:title" content="関西不動産リスト">', '<meta property="og:title" content="関東不動産リスト">')
resub(r'<meta property="og:description"[^>]*>', f'<meta property="og:description" content="{LDESC}">')
rep('<meta property="og:image" content="https://townnote.pages.dev/assets/ogp.png"><meta property="og:image:width" content="600"><meta property="og:image:height" content="600">',
    f'<meta property="og:image" content="{BASE}/og-v10.png">')
rep('<meta name="twitter:image" content="https://townnote.pages.dev/assets/ogp.png">', f'<meta name="twitter:image" content="{BASE}/og-v10.png">')
# アイコン・ホーム画面は燈の物（manifest と sw.js は pwa.py が足す）
rep('<link rel="icon" href="assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">',
    '<link rel="icon" href="/logo.png">')
rep('<title>関西不動産リスト｜地価・人口・新しい施設・制度を公式の数字で</title>', '<title>関東不動産リスト｜地価・人口・新しい施設・制度を公式の数字で</title>')
rep('<script src="assets/night.js?v=24"></script><script src="assets/menu.js?v=46" defer></script>',
    f'<script src="/assets/night.js?v={VER["night.js"]}"></script><script src="/assets/menu.js?v={VER["menu.js"]}" defer></script>')
rep('<link rel="stylesheet" href="assets/v2.css?v=7">', '<link rel="stylesheet" href="/assets/fv2.css?v=7">')
rep('<script src="assets/v2sub.js?v=11" defer></script>', f'<script src="/assets/v2sub.js?v={VER["v2sub.js"]}" defer></script>')
rep('<script src="/assets/kurabe.js?v=2" defer></script>', '<script src="/assets/kurabe.js?v=2" defer></script>')
# ---- 見出し
rep('<img src="assets/logo-s.png?v=2" width="60" height="60" alt="ロゴ"><div class="en">TOWN NOTE</div>',
    '<img src="/logo-s.png" width="60" height="60" alt="LIFE NOTE のロゴ"><a class="en" href="/" style="display:block;text-decoration:none">LIFE NOTE</a>')
rep('<h1>関西不動産リスト</h1><p class="sub">関西の街を調査して見つけた数字を、<br>公式の資料つきで紹介しています</p>',
    '<h1>関東不動産リスト</h1><p class="sub">関東の街を調査して見つけた数字を、<br>公式の資料つきで紹介しています</p>')
resub(r'<a class="ilk" href="chika-kansai">関西 \d+の街 地価ランキング 2026<span>→</span></a>',
      '')  # 11/9 見本1：ランキングは「03 街の値段を見る」に
rep("この府県の分は、これから増やしていきます", "この都県の分は、これから増やしていきます")
# 11/7 月の不動産リストと同じ形：何ができるかの1行・街の検索・横浜市西区の例（scripts/fudosan_kanto_head.html）
resub(r'<div class="head">.*?<p class="sub">.*?</p>\s*</div>', open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fudosan_kanto_head.html"), encoding="utf-8").read(), re.S)


# ---- カード（地価のタブだけ。ほかのタブは、これから）
def lk(u):
    pdf = u.lower().split("?")[0].endswith(".pdf")
    return f'<div class="lk">{"公式資料（PDF）が開きます" if pdf else "公式資料が開きます"}</div>'


def card(o):
    return (f'<a class="card" data-pref="{o["pref"]}" data-cat="{o["tab"]}" data-date="{o["date"]}" href="{E(o["url"])}">'
            f'<div class="bd"><div class="d">{E(o["src"])}</div><div class="t">{E(o["t"])}</div>'
            f'<div class="m">{E(o["m"])}</div>' + (f'<div class="spc">数字：住宅地の変動率（{o["u"]}ごとの平均）・1月1日時点</div>' if o.get("u") else "") + f'{lk(o["url"])}</div><div class="go">→</div></a>')


# ---- 11/7 人口・駅／新しい施設／制度のカード：data/kanto_facts.json（公式の資料で月か燈が確かめた物だけ。1件＝pref・tab(jinko|dekiru|seido)・date・src・t・m・url）
try:
    KF = json.load(open(os.path.join(R, "data", "kanto_facts.json"), encoding="utf-8"))
except Exception:
    KF = []
WAIT = '<div class="tip" style="margin:6px 0 14px">関東の数字は、都県・市区町村の公式の資料で確かめてから、ここに載せていきます（準備中）。</div>'
for cls, en, jp, tab in (("b-up", "PEOPLE", "人口と駅の数字", "jinko"), ("b-new", "NEW", "これからできる・最近できた施設（再開発・駅・お店）", "dekiru"), ("b-done", "MONEY", "住まいの制度とお金", "seido")):
    cs = [o for o in KF if o.get("tab") == tab and o.get("url", "").startswith("http")]
    rep(f'<div class="blk {cls}"><div class="wk hd2"><span class="en2">{en}</span><span class="jp2">{jp}</span></div></div>',
        f'<div class="blk {cls}"><div class="wk hd2"><span class="en2">{en}</span><span class="jp2">{jp}</span></div>' + ("\n".join(card(o) for o in cs) if cs else WAIT) + '</div>')


rep('<div class="blk b-now"><div class="wk hd2"><span class="en2">LAND PRICE</span><span class="jp2">地価・相場の数字</span></div></div>',
    '<div class="blk b-now"><div class="wk hd2"><span class="en2">LAND PRICE</span><span class="jp2">地価・相場の数字</span></div>' + "\n".join(card(o) for o in FACTS) + '</div>')
# ---- 下の箱：フォローは燈の分。相談は「売る前に」「売却・査定のご相談（メール）」の2つ（業者さまページは燈に無いので入れない。会社名・会社HPは出さない）
rep('<a href="https://www.instagram.com/fudousan_ai_si/">Instagram<span>@fudousan_ai_si</span></a>', '<a href="https://www.instagram.com/usagichan_ai_si/">Instagram<span>@usagichan_ai_si</span></a>')
rep('<a href="https://www.threads.com/@fudousan_ai_si">Threads<span>@fudousan_ai_si</span></a>', '<a href="https://www.threads.com/@usagichan_ai_si">Threads<span>@usagichan_ai_si</span></a>')
rep('<a href="https://x.com/fudosan_ai_si">X<span>@fudosan_ai_si</span></a>', '<a href="https://x.com/ai_usagichan">X<span>@ai_usagichan</span></a>')
rep('<a class="co" data-en="BEFORE YOU SELL" href="uru.html">', '<a class="co" data-en="BEFORE YOU SELL" href="/uru.html">')
rep('\n<a class="co" data-en="FOR AGENTS" href="gyosha.html">業者さまへ<span>物件のご紹介・ご相談はこちら</span></a>', '')
# 11/9 オーナー「関東はアフェリエイトでいく。対応できないからだ」→ 売却・査定のご相談の箱は外す
resub(r'\n<a class="co" data-en="FOR OWNERS" href="#ml">.*?</a>', '', re.S)
rep('お家を売る前に大事なこと<span>ご相談の前に、ぜひご覧ください</span>', '家を売る前に<span>相場を見る・大事なことを知る</span>')
rep('<div class="ft">ぴょんと街しらべ│調べた数字は、このページに残していきます<br><small style="font-size:10px;color:#A0A0A0">「前売り券」「近くの宿」のリンクは広告です（アソビュー・楽天トラベル）</small></div>',
    '<div class="ft">LIFE NOTE│調べた数字は、このページに残していきます</div>')
rep('<a class="tnx" href="/odekake" data-k="下の入口｜関西おでかけリスト"><small>関連サイト</small><b>関西おでかけリスト<span>→</span></b><i>関西のイベント・新しいお店や施設を、公式ページつきで</i></a>',
    '<a class="tnx" href="/odekake" data-k="下の入口｜関東おでかけリスト"><small>関連サイト</small><b>関東おでかけリスト<span>→</span></b><i>関東のイベント・新しいお店や施設を、公式ページつきで</i></a>')
# ---- 数え方は燈の形（/c?f=&s=&k=）。開いた数は middleware が数えるので、表示の分は送らない
OLD_C = 'function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}'
NEW_C = ('var FF="direct";try{FF=sessionStorage.getItem("f")||"direct";}catch(e){}'
         'function c(k){if(O)return;try{navigator.sendBeacon("/c?f="+encodeURIComponent(FF)+"&s=fudosan&k="+encodeURIComponent(String(k).slice(0,40)));}catch(e){}}')
assert h.count(OLD_C) == 2, h.count(OLD_C)
rep(OLD_C, NEW_C, 0)
rep('c("表示：不動産リスト"+(document.referrer&&!/usagi-odekake|townnote.pages/.test(document.referrer)?"（外から）":""));', '')
# ---- 都県
OLD_PC = '{"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A"}'
assert h.count(OLD_PC) == 2
rep(OLD_PC, KJS.replace(" ", ""), 0)
rep('var P=["大阪","京都","兵庫","奈良","滋賀","和歌山"],F=', f'var P={PJS.replace(" ", "")},F=')
rep('PS=["大阪","京都","兵庫","奈良","滋賀","和歌山"];', f'PS={PJS.replace(" ", "")};')
resub(r"<span>関西の街<b>\d+</b></span>", f"<span>関東の街<b>{len(towns)}</b></span>")
rep('府県を「すべて」にもどす', '都県を「すべて」にもどす')
# ---- 街で探す・地図
resub(r'var PL=\[[^\]]*\];', "var PL=" + json.dumps(["港区", "世田谷区", "武蔵野市", "横浜市西区", "川崎市中原区", "藤沢市", "さいたま市浦和区", "川口市",
                                                 "千葉市中央区", "流山市", "つくば市", "宇都宮市", "高崎市", "前橋市"], ensure_ascii=False) + ";")
rep('（関西 "+(TW?TW.length:"")+" の街）', '（関東 "+(TW?TW.length:"")+" の街）')
rep('fetch("/townnotes/kansai.json")', 'fetch("/townnotes/kanto.json")')
LP = {"東京": [139.40, 35.70], "神奈川": [139.30, 35.42], "埼玉": [139.30, 36.02], "千葉": [140.25, 35.45],
      "茨城": [140.30, 36.38], "栃木": [139.82, 36.68], "群馬": [138.98, 36.52]}  # lifenote_top.py と同じ
CITY = {"神奈川": ["横浜市", "川崎市", "相模原市"], "埼玉": ["さいたま市"], "千葉": ["千葉市"]}
KU = {c: sum(1 for t in towns if t["n"].startswith(c)) for v in CITY.values() for c in v}
resub(r'var LP=\{[^}]*\},CITY=\{[^}]*\};KU=\{[^}]*\};',
      "var LP=" + json.dumps(LP, ensure_ascii=False, separators=(",", ":")) + ",CITY=" + json.dumps(CITY, ensure_ascii=False, separators=(",", ":"))
      + ";KU=" + json.dumps(KU, ensure_ascii=False, separators=(",", ":")) + ";")
rep('var m=n.match(/^(大阪市|堺市|京都市|神戸市)/);', 'var m=n.match(/' + CITY_RE + '/);')
rep('aria-label="関西の地価の地図"', 'aria-label="関東の地価の地図"')
rep('"府県を選ぶと、市・区・町の名前と数字が出ます。"', '"都県を選ぶと、市・区・町の名前と数字が出ます。"')
rep("'は、府県の資料に住宅地の平均がありません。", "'は、都県の資料に住宅地の平均がありません。")
rep('placeholder="例：吹田、西宮、草津"', 'placeholder="例：港区、横浜、川越"')
rep('c("地図：府県 "+p);', 'c("地図：都県 "+p);')
# 11/9 20:30 オーナー「何個も同じやつ」「下のやつ見にくくない？」→ TOWN と同じ形：売る人向けの1ブロック → 関連サイト → FOLLOW と注意書き。箱の枠はやめて細い線と余白
_m = re.search(r'<div class="sns"><h2>FOLLOW</h2>(.*?)<div class="cos">.*?</div>\s*</div>\s*(<div class="ft">.*?</div>)(<a class="tnx".*?</a>)', h, flags=re.S)
assert _m, "下の欄が見つからない"
_SELL = ('<section class="sell2"><small>BEFORE YOU SELL</small><h2>家を売る前に</h2>'
         '<p>相場と、売る前に知っておく大事なことを、順番に見られます。迷ったらご相談ください。</p>'
         '<div class="b1"><a href="/uru.html" data-k="下｜売る前に読む">売る前に読む<span>相場・大事なこと</span></a></div>'
         '<div class="b1" style="margin-top:10px"><a href="/moushikomi?lite=1&amp;want=%E6%9F%BB%E5%AE%9A%E3%81%97%E3%81%A6%E3%81%BB%E3%81%97%E3%81%84" data-k="下｜無料で聞く">いくらで売れるか、無料で聞く<span>売るか決めていなくても大丈夫・約1分</span></a></div></section>')
h = h[:_m.start()] + _SELL + _m.group(3) + '<div class="sns"><h2>FOLLOW</h2>' + _m.group(1) + '</div>' + _m.group(2) + h[_m.end():]
h = h.replace("</style>", ".sell2{margin:40px 0 0;padding:26px 4px 0;border-top:1px solid #D6D9DE;text-align:center}.sell2 small{font-family:Jost,sans-serif;font-size:10px;letter-spacing:.32em;color:#9C8775}.sell2 h2{font-family:'Shippori Mincho',serif;font-weight:600;font-size:20px;letter-spacing:.1em;margin:6px 0 0;color:#2B2622}.sell2 p{font-size:12.5px;color:#6B6058;line-height:1.8;margin:8px 0 0}.sell2 .b1{margin:16px 0 0}.sell2 .b1 a{display:flex;flex-direction:column;justify-content:center;min-height:56px;text-decoration:none;font-weight:700;font-size:15px;color:#fff;background:#2B2622;border-radius:10px}.sell2 .b1 a span{font-weight:400;font-size:11px;color:#D9D2CC;margin-top:2px}.sell2+.tnx{margin-top:34px;border:0!important;border-top:1px solid #D6D9DE!important;border-radius:0!important;box-shadow:none!important}\n</style>", 1)
for bad in ("関西", "府県", "大阪", "townnote.pages", "fudousan_ai", "fudosan_ai", "kansai", "TOWN NOTE", "ぴょん", "gyosha", "JSON.stringify({k"):
    left = [m.start() for m in re.finditer(re.escape(bad), h)]
    # CSS・スクリプトの中の月のメモ（/* … */）に残る言葉は見た目に出ないので、見える所だけ確かめる
    vis = re.sub(r"/\*.*?\*/", "", re.sub(r"<!--.*?-->", "", h, flags=re.S), flags=re.S)
    assert bad not in vis, ("関西の言葉が残っている", bad, vis[vis.find(bad) - 80:vis.find(bad) + 80])
open(os.path.join(S, "fudosan-list.html"), "w", encoding="utf-8").write(h)

# ================= 実家・空き家ノート（11/9 オーナー「つくれ」・月の関西版と同じ形）
# 関東はアフィリエイトだけ（オーナー11/9）：相談・申し込みの言葉は使わない。売るは Yahoo!不動産の売却査定（VC）。片付け・解体は台帳に登録した広告ができてから足す
# 11/10 オーナー「Yahooは資料請求が目的だろ？するかな売りたい人が」→ 売る人に Yahoo は出さない（A8 の査定が承認されたらそれを入れる）。実家ノートとの行き来も外す（完全別）
J_SELL = YAHOO_RE.split("&vc_url=")[0] + "&vc_url=" + _q("https://realestate.yahoo.co.jp/sell/", safe="")
J_SRC = [
    ("相続登記を確かめる", "2024年4月1日から、相続で家や土地を受け取ったと知った日から3年以内の相続登記が義務になりました。2024年3月より前の相続も対象で、期限は「2027年3月31日」か「受け取ったと知った日から3年」の、どちらか遅い方です。",
     "法務省「相続登記の申請義務化」", "https://www.moj.go.jp/MINJI/souzokutouki-gimuka/index.html"),
    ("家財を片付ける", "遠方の実家なら、片付け・遺品整理の見積りを先に取ると、売る時期を決めやすくなります。見積りは作業の中身と追加料金を確かめてから頼みましょう。",
     "国民生活センター「遺品整理を頼むときは、事業者選びは慎重に」", "https://www.kokusen.go.jp/mimamori/mj_mailmag/mj-shinsen525.html"),
    ("売るか、解体するか", "古い家は「そのまま売る」「更地にして売る」で値段も費用も変わります。手入れが足りず市区町村から「管理不全空家」として勧告を受けると、土地の固定資産税の軽減（住宅用地特例）が外れます。",
     "国土交通省「空家等対策の推進に関する特別措置法の一部を改正する法律」概要", "https://www.mlit.go.jp/jutakukentiku/house/content/001621960.pdf"),
    ("税金の特例を確かめる", "相続した空き家（1981年5月31日以前に建てた家など）は、「相続から3年目の年の12月31日まで」かつ「2027年12月31日まで」に売ると、売ったもうけから最高3,000万円を差し引けます（相続人が3人以上なら1人2,000万円まで・条件あり）。くわしくは税務署・税理士へ。",
     "国税庁 タックスアンサー No.3306", "https://www.nta.go.jp/taxes/shiraberu/taxanswer/joto/3306.htm"),
]
J_CSS = """.jn{display:grid;grid-template-columns:1fr 1fr;gap:10px}.jn>div{background:#F4F4F6;border-radius:12px;padding:12px 14px}
.jn b{display:block;font-family:Jost,"Zen Kaku Gothic New";font-weight:400;font-size:24px;color:#2B2622;line-height:1.3}.jn b small{font-size:12px}.jn span{display:block;font-size:11.5px;color:#7A6E66;margin-top:2px;line-height:1.6}
.src{font-size:11px;color:#8C7B6E;line-height:1.7;margin:8px 0 0}.src a{color:#8C7B6E}
.mk3{font-family:Jost,sans-serif;font-size:10.5px;letter-spacing:.3em;color:#9C8775;margin:30px 0 0}.jh{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.1em;margin:4px 0 12px;padding:0;border:0}
.st{display:flex;gap:12px;align-items:flex-start;padding:12px 0;border-top:1px solid #ECECEC}.st:last-of-type{border-bottom:1px solid #ECECEC}.st i{font-style:normal;font-family:Jost,sans-serif;font-weight:300;font-size:20px;color:var(--pc);width:26px;flex:none;line-height:1.3}
.st b{display:block;font-size:14.5px}.st p{margin:3px 0 0;font-size:13px;line-height:1.8;color:#4E453F}.st a{display:inline-block;font-size:11px;color:#8C7B6E;margin-top:4px}
.jb{display:block;text-align:center;border-radius:12px;padding:14px 12px;font-size:14.5px;font-weight:700;margin-top:10px;text-decoration:none;color:#2B2622;border:1px solid #2B2622;background:#fff}.jb small{display:block;font-size:11px;font-weight:500;color:#857A70;margin-top:2px}.jb.b1{background:#2B2622;color:#fff;border-color:#2B2622}.jb.b1 small{color:#D9D2CC}
.jp{font-size:11.5px;color:#8C7B6E;text-align:center;margin:8px 0 0;line-height:1.7}
.jl{display:flex;justify-content:space-between;margin:14px 0 0;padding:12px 4px;border-top:1px solid #E6E6E6;border-bottom:1px solid #E6E6E6;text-decoration:none;color:#5E544D;font-size:13px}.jl i{font-style:normal;font-family:Jost;color:#9C8775}
.flt{display:flex;flex-wrap:nowrap;justify-content:center;gap:0 13px;margin:24px 0 8px;padding:10px 0;border-top:1px solid #D4D4D4;border-bottom:1px solid #D4D4D4;overflow-x:auto}
.flt button{flex:none;border:none;background:none;padding:4px 0;font-family:"Zen Kaku Gothic New";font-size:14px;font-weight:700;letter-spacing:.04em;color:var(--pc,#8C7B6E);border-bottom:1px solid transparent;cursor:pointer;opacity:.85}
.flt button.on{opacity:1;border-bottom-color:currentColor}.pane{display:none}.pane.on{display:block}
.jli{list-style:none;margin:0;padding:0}.jli li{border-bottom:1px solid #ECECEC}.jli a{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:12px 2px;text-decoration:none;color:#2B2622;font-weight:700;font-size:14px}
.jli a small{font-size:11.5px;color:#7A6E66;font-weight:500;text-align:right}"""


def jikka_page(t):
    pf, fn, en, col, sname, surl, pfull, s = PI[t["p"]]
    n = t["n"]
    title = f"{n}の実家・空き家｜売る・片付け・解体の前に（地価と順番）"
    desc = (f"{pfull}{n}で親の家を相続した・空き家のままの方へ。住宅地の地価は令和8年地価公示で前の年から{pct(t['r8'])}。"
            "相続登記の義務、片付け、売るか解体するか、3,000万円の特別控除まで、公式の出典つきで順番に。")
    url = f"{BASE}/jikka/{t['id']}"
    ld = {"@context": "https://schema.org", "@graph": [{"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "LIFE NOTE", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": "実家・空き家ノート", "item": f"{BASE}/jikka/"},
        {"@type": "ListItem", "position": 3, "name": f"{n}の実家・空き家", "item": url}]}]}
    steps = "".join(f'<div class="st"><i>{i:02d}</i><div><b>{E(h)}</b><p>{E(p)}</p><a href="{E(u)}" target="_blank" rel="noopener" data-k="実家｜出典｜{i:02d}">出典：{E(sn)}</a></div></div>'
                    for i, (h, p, sn, u) in enumerate(J_SRC, 1))
    pr = f'<div><b>{t["price"] / 10000:.1f}<small>万円</small></b><span>住宅地の平均価格（1㎡）</span></div>' if t["price"] else f'<div><b>{t["rank"]}<small>位／{t["of"]}</small></b><span>{E(pfull)}での順位（上がり幅）</span></div>'
    body = f'''<style>{HEAD_CSS}{J_CSS}</style>{SCRIPTS}</head><body style="--pc:{col}"><div class="wrap">
<div class="head"><img src="/logo-s.png" width="60" height="60" alt="LIFE NOTE のロゴ"><div class="en">{en} ─ JIKKA NOTE</div>
<h1>{E(n)}の実家・空き家ノート<span>売る・片付ける・解体する前に</span></h1>
<p class="sub">親の家を相続した・空き家のままになっている。<br>この街で決めるための数字と順番です。</p>
<div class="upd">2026年11月 更新</div></div>
<p class="mk3">LAND PRICE 2026</p><h2 class="jh">この街の土地の値段</h2>
<div class="jn"><div><b>{pct(t["r8"])}</b><span>住宅地 1年の動き</span></div>{pr}</div>
<p class="src">出典：令和8年地価公示（2026年1月1日時点）。{E(pfull)}{t["of"]}市区町村で{t["rank"]}位。</p>
<a href="/jikka/shindan/?machi={t["id"]}" data-k="実家｜3問診断へ" style="display:block;margin:22px 0 0;padding:14px 16px;border:1.5px solid #2F7D5B;border-radius:14px;text-decoration:none;color:#231E1B;font-weight:700;font-size:15px;text-align:left">うちの場合は？ 3問でわかる診断へ →<small style="display:block;font-weight:500;font-size:12px;color:#6B6058;margin-top:2px">約30秒・無料・お名前は要りません</small></a>
<p class="mk3" id="steps">STEPS</p><h2 class="jh">迷ったら、この順で</h2>
{steps}
<p class="mk3">NEXT</p><h2 class="jh">次にできること</h2>
<a class="jb b1" href="/moushikomi?machi={t["id"]}&amp;want={_q("相続した家のこと")}" data-k="実家｜売却の相談｜{E(n)}">この家の売却を相談する<small>無料・約1分</small></a>
<a class="jb" href="/moushikomi?lite=1&amp;machi={t["id"]}&amp;want={_q("片付け・遺品整理の見積り")}" data-k="実家｜片付けの見積り｜{E(n)}">片付け・遺品整理の見積りを頼む<small>無料・約1分</small></a>
<a class="jb" href="/moushikomi?lite=1&amp;machi={t["id"]}&amp;want={_q("解体の見積り")}" data-k="実家｜解体の見積り｜{E(n)}">解体費用の見積りを頼む<small>無料・約1分</small></a>
<p class="jp">どれも同じお申し込みページです。内容を見て、メールでご連絡します。</p>
<a class="jl" href="/kaitai" data-k="実家｜費用の目安">先に、解体・片付けの費用の目安を見る <i>→</i></a>
<a class="jl" href="/jikka/#{fn}" data-k="実家｜一覧">ほかの街の実家・空き家ノート <i>→</i></a>
<div class="ft">LIFE NOTE</div></div>
{beacon("実家｜" + n)}</body></html>'''
    return head(title, desc, url, ld) + body


os.makedirs(os.path.join(S, "jikka"), exist_ok=True)
for f in os.listdir(os.path.join(S, "jikka")):
    if f.endswith(".html"):
        os.remove(os.path.join(S, "jikka", f))
for t in towns:
    open(os.path.join(S, "jikka", t["id"] + ".html"), "w", encoding="utf-8").write(jikka_page(t))
_jp = [(fn, pf, [t for t in towns if t["p"] == pf]) for pf, fn, *_ in PREFS]
_jl = head(f"関東の実家・空き家ノート｜{len(towns)}の街の地価と、売る・片付け・解体の順番",
           f"関東{len(ORDER)}都県・{len(towns)}の市区町村ごとに、相続した実家・空き家を「売る・片付ける・解体する」前に見る数字と順番。相続登記の義務、3,000万円の特別控除を公式の出典つきで。",
           f"{BASE}/jikka/") + f'''<style>{HEAD_CSS}{J_CSS}</style>{SCRIPTS}</head><body><div class="wrap">
<div class="head"><img src="/logo-s.png" width="60" height="60" alt="LIFE NOTE のロゴ"><div class="en">KANTO ─ JIKKA NOTE</div>
<h1>実家・空き家ノート<span>関東 {len(towns)}の街</span></h1>
<p class="sub">親の家を相続した・空き家のままの方へ。<br>街を選ぶと、土地の値段と順番が見られます。</p>
<div class="upd">2026年11月 更新</div></div>
<style>.jq{{margin:24px 0 6px;padding:14px 16px 16px;background:#F5F4F2;border:1px solid #ECEAE6;border-radius:16px;text-align:center}}.jq b{{display:block;font-size:13px;letter-spacing:.08em;color:#2B2622;margin-bottom:10px}}.jq input{{width:100%;box-sizing:border-box;font:500 16px "Zen Kaku Gothic New",sans-serif;padding:12px 16px;border:1.5px solid #CFC6BC;border-radius:12px;background:#fff;color:#2B2622;-webkit-appearance:none;appearance:none}}.jq input:focus{{outline:none;border-color:#8C7B6E}}#jres{{display:none}}#jres.on{{display:block}}#jres p{{font-size:13px;color:#7A6E66;margin:14px 2px}}html.jq-on .flt,html.jq-on .pane{{display:none!important}}</style><a href="/jikka/shindan/" data-k="実家｜一覧｜3問診断へ" style="display:block;margin:22px 0 0;padding:14px 16px;border:1.5px solid #2F7D5B;border-radius:14px;text-decoration:none;color:#231E1B;font-weight:700;font-size:15px;text-align:left">何から始める？ 3問でわかる診断へ →<small style="display:block;font-weight:500;font-size:12px;color:#6B6058;margin-top:2px">約30秒・無料・お名前は要りません</small></a><div class="jq"><b>街の名前で探す</b><input id="jqi" type="search" placeholder="例：横浜市西区・川越市・柏市" enterkeyhint="search" autocomplete="off"></div><div id="jres"></div><nav class="flt">''' + "".join(f'<button data-p="{k}" style="--pc:{PI[pf][3]}"{" class=\"on\"" if i == 0 else ""}>{pf}</button>' for i, (k, pf, _) in enumerate(_jp)) + '</nav>' + \
    "".join(f'<section class="pane{" on" if i == 0 else ""}" id="{k}"><ul class="jli">' + "".join(f'<li><a href="/jikka/{t["id"]}" data-k="実家一覧｜{E(t["n"])}">{E(t["n"])}<small>住宅地 {pct(t["r8"])}</small></a></li>' for t in ts) + '</ul></section>' for i, (k, pf, ts) in enumerate(_jp)) + f'''
<p class="note">古い家を解体する時の補助金は、<a href="/kaitai-ranking" data-k="実家｜一覧｜解体の補助金ランキング">市ごとの解体の補助金ランキング</a>で見られます。</p>
<div class="ft">LIFE NOTE</div></div>
<script>(function(){{function go(k){{var b=document.querySelector('.flt button[data-p="'+k+'"]');if(!b)return;document.querySelectorAll(".flt button,.pane").forEach(function(x){{x.classList.remove("on")}});b.classList.add("on");document.getElementById(k).classList.add("on");}}
document.querySelectorAll(".flt button").forEach(function(b){{b.onclick=function(){{go(b.dataset.p);history.replaceState(null,"","#"+b.dataset.p);}}}});if(location.hash)go(location.hash.slice(1));}})();</script>
<script>(function(){{var i=document.getElementById("jqi"),r=document.getElementById("jres"),all=[].slice.call(document.querySelectorAll(".pane .jli li")),tq;function n(s){{return s.replace(/\\s/g,"").replace(/[市区町村]$/,"")}}i.oninput=function(){{var q=n(i.value);r.innerHTML="";document.documentElement.classList.toggle("jq-on",!!q);r.classList.toggle("on",!!q);if(!q)return;var u=document.createElement("ul");u.className="jli";all.forEach(function(li){{if(li.querySelector("a").firstChild.textContent.replace(/\\s/g,"").indexOf(q)>=0)u.appendChild(li.cloneNode(true))}});if(u.children.length)r.appendChild(u);else r.innerHTML="<p>「"+i.value.trim()+"」は見つかりませんでした。府県から選んでください。</p>";clearTimeout(tq);tq=setTimeout(function(){{try{{var b=JSON.stringify({{k:"実家一覧｜検索："+i.value.trim()}});navigator.sendBeacon&&navigator.sendBeacon("/c",b)}}catch(e){{}}}},1500);}};}})();</script>
{beacon("実家一覧")}</body></html>'''
open(os.path.join(S, "jikka", "index.html"), "w", encoding="utf-8").write(_jl)

# ================= sitemap（あれば足す）
sm = os.path.join(S, "sitemap.xml")
if LIVE and os.path.exists(sm):
    x = open(sm, encoding="utf-8").read()
    add = "".join(f"<url><loc>{BASE}{p}</loc></url>" for p in ["/fudosan-list", "/chika-kanto", "/sagasu", "/jikka/", "/kaitai"] + ["/" + f[:-5] for f in sorted(os.listdir(os.path.join(os.path.dirname(sm)))) if f.startswith("kaitai-") and f.endswith(".html")] + [f"/machi/{t['id']}" for t in towns] + [f"/jikka/{t['id']}" for t in towns] if f"{BASE}{p}<" not in x)
    if add:
        open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", add + "</urlset>", 1))
print("関東不動産リスト:", len(towns), "街のページ ・ /chika-kanto ・ /fudosan-list", len(FACTS), "件", "live" if LIVE else "noindex",
      "・関連カードのある街", sum(1 for t in towns if related(t)))
